import ast
import importlib
import sys
import threading
import time
import types
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from request_llms.codex_cli.config import CodexSettings
from request_llms.codex_cli.scheduler import CodexScheduler
from request_llms.codex_cli.types import CodexError, CodexResult

from .conftest import make_request


REPO = Path(__file__).resolve().parents[2]


def _source(relative_path):
    return (REPO / relative_path).read_text(encoding="utf-8")


_MISSING = object()


@contextmanager
def _isolated_sys_modules(module_roots):
    def matches(name):
        return any(name == root or name.startswith(root + ".") for root in module_roots)

    original_modules = {
        name: module
        for name, module in sys.modules.items()
        if matches(name)
    }
    for root in module_roots:
        original_modules.setdefault(root, _MISSING)
    original_attributes = {}
    for name in original_modules:
        parent_name, separator, child_name = name.rpartition(".")
        if not separator:
            continue
        parent = sys.modules.get(parent_name)
        if parent is not None:
            original_attributes[(parent_name, child_name)] = getattr(
                parent, child_name, _MISSING
            )
    try:
        yield
    finally:
        for name in list(sys.modules):
            if matches(name) and name not in original_modules:
                sys.modules.pop(name, None)
        for name, original in original_modules.items():
            if original is _MISSING:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = original
        for (parent_name, child_name), original in original_attributes.items():
            parent = sys.modules.get(parent_name)
            if parent is None:
                continue
            if original is _MISSING:
                if hasattr(parent, child_name):
                    delattr(parent, child_name)
            else:
                setattr(parent, child_name, original)


def test_codex_model_registration_and_display_name_are_static():
    source = _source("request_llms/bridge_all.py")
    tree = ast.parse(source)
    assert "codex-cli" in _source("config.py")
    assert "Codex CLI（本机登录）" in source
    assert "codex_cli_noui" in source
    assert "codex_cli_ui" in source
    assert any(
        isinstance(node, ast.FunctionDef) and node.name == "predict_no_ui_long_connection"
        for node in tree.body
    )


def test_toolbar_choices_remain_plain_model_ids():
    from themes.gui_toolbar import _model_dropdown_choices

    choices = _model_dropdown_choices(["gpt-3.5-turbo", "codex-cli"])
    assert choices == ["gpt-3.5-turbo", "codex-cli"]
    assert all(type(choice) is str for choice in choices)

    source = _source("themes/gui_toolbar.py")
    assert "gr.Dropdown(_model_dropdown_choices(AVAIL_LLM_MODELS)" in source
    assert "gr.Markdown" in source
    assert "Codex CLI（本机登录）" in source
    init_source = _source("themes/init.js")
    assert "Array.isArray(choice)" not in init_source
    assert "model_sel.props.choices.includes(cached_model)" in init_source


def test_codex_ui_discloses_best_effort_isolation_boundary():
    source = _source("themes/gui_toolbar.py")
    docs = _source("docs/codex-cli.md")
    for content in (source, docs):
        assert "最佳努力隔离" in content
        assert "不能保证" in content
        assert "副作用" in content


def test_public_bridge_rejects_codex_attachment_without_scope_error(monkeypatch):
    import request_llms.bridge_all as bridge_all

    monkeypatch.setattr(bridge_all, "contain_uploaded_files", lambda inputs: True)
    monkeypatch.setattr(
        bridge_all,
        "update_ui",
        lambda **kwargs: iter([kwargs["msg"]]),
    )
    chatbot = []
    events = list(
        bridge_all.predict(
            "uploaded input",
            {"llm_model": "codex-cli"},
            {},
            chatbot,
            [],
            "",
            True,
            None,
        )
    )
    assert events == ["unsupported_input"]
    assert chatbot[-1][1] == "[Local Message] Codex CLI 仅支持纯文本输入，不支持附件。"


def test_codex_to_api_switch_keeps_cookie_api_key(monkeypatch):
    import toolbox

    api_key = "sk-test-key-preserved"
    values = {
        "API_KEY": api_key,
        "LLM_MODEL": "codex-cli",
        "AZURE_API_KEY": "",
        "AZURE_CFG_ARRAY": {},
        "NUM_CUSTOM_BASIC_BTN": 0,
        "EMBEDDING_MODEL": "text-embedding-3-small",
    }

    def fake_get_conf(*names):
        if len(names) == 1:
            return values[names[0]]
        return tuple(values[name] for name in names)

    monkeypatch.setattr(toolbox, "get_conf", fake_get_conf)
    cookies = toolbox.load_chat_cookies()
    assert cookies["llm_model"] == "codex-cli"
    assert cookies["api_key"] == api_key

    cookies["llm_model"] = "gpt-3.5-turbo"
    assert cookies["api_key"] == api_key


def test_default_model_unchanged():
    config_source = _source("config.py")
    assert 'LLM_MODEL = "gpt-3.5-turbo-16k"' in config_source


def test_api_backend_still_requires_api_key_and_keeps_retry_path():
    source = _source("request_llms/bridge_chatgpt.py")
    assert "if not is_any_api_key(llm_kwargs['api_key'])" in source
    assert "MAX_RETRY" in source
    assert "requests.exceptions.ReadTimeout" in source


def test_crazy_utils_codex_failure_is_not_resubmitted():
    calls = []

    toolbox = types.ModuleType("toolbox")
    toolbox.update_ui = lambda **kwargs: iter(())
    toolbox.get_conf = lambda *args: 1
    toolbox.trimmed_format_exc = lambda: "must not be formatted"
    toolbox.get_max_token = lambda kwargs: 1000
    toolbox.Singleton = lambda decorated: decorated
    visual = types.ModuleType("shared_utils.char_visual_effect")
    visual.scrolling_visual_effect = lambda text, limit: text
    bridge_all = types.ModuleType("request_llms.bridge_all")
    bridge_all.model_info = {"codex-cli": {"can_multi_thread": True}}

    def fail_once(*args, **kwargs):
        calls.append(1)
        raise CodexError("tool_activity_blocked", "Codex CLI 请求被策略拒绝。")

    bridge_all.predict_no_ui_long_connection = fail_once
    module_roots = [
        "toolbox",
        "shared_utils.char_visual_effect",
        "request_llms.bridge_all",
        "crazy_functions.crazy_utils",
    ]
    before = {name: sys.modules.get(name, _MISSING) for name in module_roots}
    with _isolated_sys_modules(module_roots):
        sys.modules["toolbox"] = toolbox
        sys.modules["shared_utils.char_visual_effect"] = visual
        sys.modules["request_llms.bridge_all"] = bridge_all
        sys.modules.pop("crazy_functions.crazy_utils", None)
        module = importlib.import_module("crazy_functions.crazy_utils")

        chatbot = []
        generator = module.request_gpt_model_in_new_thread_with_ui_alive(
            "input",
            "shown",
            {"llm_model": "codex-cli"},
            chatbot,
            [],
            "",
            refresh_interval=0,
            retry_times_at_unknown_error=2,
        )
        with pytest.raises(StopIteration) as stopped:
            while True:
                next(generator)
        assert stopped.value.value == "Codex CLI 请求被策略拒绝。"
        assert len(calls) == 1
    for name, original in before.items():
        assert sys.modules.get(name, _MISSING) is original


def test_source_comment_codex_failure_is_not_resubmitted():
    toolbox = types.ModuleType("toolbox")
    toolbox.CatchException = lambda function: function
    toolbox.update_ui = lambda **kwargs: iter(())
    bridge_all = types.ModuleType("request_llms.bridge_all")
    bridge_all.predict_no_ui_long_connection = lambda *args, **kwargs: None
    crazy_utils = types.ModuleType("crazy_functions.crazy_utils")
    crazy_utils.request_gpt_model_in_new_thread_with_ui_alive = lambda *args, **kwargs: None
    module_roots = [
        "toolbox",
        "request_llms.bridge_all",
        "crazy_functions.crazy_utils",
        "crazy_functions.agent_fns.python_comment_agent",
    ]
    before = {name: sys.modules.get(name, _MISSING) for name in module_roots}
    with _isolated_sys_modules(module_roots):
        sys.modules["toolbox"] = toolbox
        sys.modules["request_llms.bridge_all"] = bridge_all
        sys.modules["crazy_functions.crazy_utils"] = crazy_utils
        sys.modules.pop("crazy_functions.agent_fns.python_comment_agent", None)
        module = importlib.import_module("crazy_functions.agent_fns.python_comment_agent")

        instance = module.PythonCodeComment.__new__(module.PythonCodeComment)
        instance.path = "sample.py"
        instance.file_basename = "sample.py"
        instance.full_context = ["pass\n"]
        instance.observe_window_update = lambda value: None
        calls = []

        batch_calls = []

        def get_next_batch():
            if not batch_calls:
                batch_calls.append(1)
                return "pass\n", 0, 1
            raise StopIteration

        instance.get_next_batch = get_next_batch

        def fail_tag(*args, **kwargs):
            calls.append(1)
            raise CodexError("request_timeout", "Codex CLI 请求超时。")

        instance.tag_code = fail_tag
        with pytest.raises(CodexError) as caught:
            instance.begin_comment_source_code()
        assert caught.value.code == "request_timeout"
        assert len(calls) == 1
    for name, original in before.items():
        assert sys.modules.get(name, _MISSING) is original


def test_plugin_parallel_calls_share_single_slot():
    active = 0
    peak = 0
    lock = threading.Lock()

    def runner(request, settings, on_text):
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
        time.sleep(0.01)
        on_text(request.prompt)
        with lock:
            active -= 1
        return CodexResult(request.prompt)

    settings = CodexSettings(
        cli_path="/tmp/fake-codex",
        cli_model="",
        queue_capacity=32,
        min_start_interval=0.0,
        queue_timeout=5.0,
        request_timeout=5.0,
        max_input_bytes=1000,
        max_output_bytes=1000,
    )
    scheduler = CodexScheduler(settings, runner, time.monotonic)
    try:
        with ThreadPoolExecutor(max_workers=12) as executor:
            submissions = [
                scheduler.submit(make_request(str(index)), lambda text: None)
                for index in range(12)
            ]
            results = list(
                executor.map(lambda submission: submission.future.result(timeout=3), submissions)
            )
        assert [result.text for result in results] == [str(index) for index in range(12)]
        assert peak == 1
    finally:
        scheduler.close()


def test_api_backend_retains_existing_retry_behavior():
    source = _source("request_llms/bridge_chatgpt.py")
    assert "retry += 1" in source
    assert "if retry > MAX_RETRY" in source


def test_multi_model_failure_cancels_workers_and_stops_watchdog(monkeypatch):
    import request_llms.bridge_all as bridge_all

    worker_started = threading.Event()
    worker_cancelled = threading.Event()
    test_cleanup = threading.Event()
    worker_lock = threading.Lock()
    worker_index = [0]

    def codex_worker(inputs, llm_kwargs, history, sys_prompt, observe, silence):
        with worker_lock:
            index = worker_index[0]
            worker_index[0] += 1
        if index == 0:
            assert worker_started.wait(1)
            raise CodexError("tool_activity_blocked", "Codex CLI 请求被策略拒绝。")
        worker_started.set()
        token = llm_kwargs.get("cancel_token")
        while (
            (token is None or not token.is_cancelled())
            and not test_cleanup.is_set()
        ):
            time.sleep(0.01)
        if token is not None and token.is_cancelled():
            worker_cancelled.set()
        raise CodexError("cancelled", "Codex CLI 请求已取消。")

    monkeypatch.setattr(
        bridge_all,
        "model_info",
        {
            "codex-cli": {"fn_without_ui": codex_worker},
        },
    )

    created_threads = []
    real_thread = threading.Thread

    def tracked_thread(*args, **kwargs):
        thread = real_thread(*args, **kwargs)
        target = kwargs.get("target")
        created_threads.append((thread, target, args, kwargs))
        return thread

    monkeypatch.setattr(threading, "Thread", tracked_thread)
    observe_window = ["", time.time(), "running"]
    result = {}

    def call():
        try:
            result["value"] = bridge_all.predict_no_ui_long_connection(
                "input",
                {"llm_model": "codex-cli&codex-cli"},
                [],
                "",
                observe_window,
                True,
            )
        except BaseException as error:
            result["error"] = error

    call_thread = real_thread(target=call)
    call_thread.start()
    try:
        assert worker_started.wait(1)
        call_thread.join(2)
        assert not call_thread.is_alive()
        assert worker_cancelled.is_set()
        watchdog_threads = [
            thread
            for thread, target, args, kwargs in created_threads
            if getattr(target, "__name__", "") == "mutex_manager"
        ]
        assert watchdog_threads
        assert all(not thread.is_alive() for thread in watchdog_threads)
        assert isinstance(result.get("error"), CodexError)
    finally:
        test_cleanup.set()
        for thread, target, args, kwargs in created_threads:
            if getattr(target, "__name__", "") == "mutex_manager":
                thread_args = kwargs.get("args", ())
                if thread_args:
                    thread_args[0][-1] = False
                thread.join(1)
        call_thread.join(1)


def test_multi_model_route_preserves_external_cancel_token(monkeypatch):
    import request_llms.bridge_all as bridge_all

    def codex_worker(inputs, llm_kwargs, history, sys_prompt, observe, silence):
        assert llm_kwargs["cancel_token"] is external_token
        return "ok"

    monkeypatch.setattr(
        bridge_all,
        "model_info",
        {
            "codex-cli": {"fn_without_ui": codex_worker},
        },
    )
    external_token = __import__(
        "request_llms.codex_cli.types", fromlist=["CancelToken"]
    ).CancelToken()
    result = bridge_all.predict_no_ui_long_connection(
        "input",
        {"llm_model": "codex-cli&codex-cli", "cancel_token": external_token},
        [],
        "",
        ["", time.time(), "running"],
        True,
    )
    assert "ok" in result


def test_plugin_cancel_removes_queued_work():
    entered = threading.Event()
    release = threading.Event()
    started = []

    def runner(request, settings, on_text):
        started.append(request.prompt)
        entered.set()
        release.wait(2)
        return CodexResult(request.prompt)

    settings = CodexSettings(
        cli_path="/tmp/fake-codex",
        cli_model="",
        queue_capacity=2,
        min_start_interval=0.0,
        queue_timeout=5.0,
        request_timeout=5.0,
        max_input_bytes=1000,
        max_output_bytes=1000,
    )
    scheduler = CodexScheduler(settings, runner, time.monotonic)
    try:
        first = scheduler.submit(make_request("first"), lambda text: None)
        assert entered.wait(1)
        second = scheduler.submit(make_request("second"), lambda text: None)
        second.cancel.cancel()
        with pytest.raises(CodexError) as caught:
            second.future.result(timeout=1)
        assert caught.value.code == "cancelled"
        release.set()
        assert first.future.result(timeout=2).text == "first"
        assert started == ["first"]
    finally:
        release.set()
        scheduler.close()

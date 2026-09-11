#!/usr/bin/env python3
"""Deterministic test-only stand-in for ``codex exec``.

This file intentionally has no production import path.  Scenarios are selected
through environment variables so tests can exercise process lifecycle behavior
without making a model request.
"""

import json
import os
import signal
import subprocess
import sys
import time


def _help():
    print(
        """Run Codex non-interactively
Usage: codex exec [OPTIONS] [PROMPT]
If '-' is used, instructions are read from stdin.
--json --ephemeral --skip-git-repo-check --ignore-user-config --ignore-rules
--sandbox <read-only|workspace-write|danger-full-access>
-C <DIR> -m <MODEL>"""
    )


def _record_formal_start():
    path = os.environ.get("FAKE_CODEX_FORMAL_START_COUNT_PATH")
    if not path:
        return
    try:
        with open(path, "r", encoding="utf-8") as handle:
            count = int(handle.read())
    except (OSError, ValueError):
        count = 0
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(str(count + 1))


def _metadata(prompt):
    path = os.environ.get("FAKE_CODEX_METADATA_PATH")
    if not path:
        return
    value = {
        "pid": os.getpid(),
        "cwd": os.getcwd(),
        "cwd_entries": sorted(os.listdir(os.getcwd())),
        "prompt": prompt,
        "openai_api_key": os.environ.get("OPENAI_API_KEY"),
        "api_key": os.environ.get("API_KEY"),
        "other_api_key": os.environ.get("OTHER_API_KEY"),
    }
    child_pid = os.environ.get("FAKE_CODEX_CHILD_PID")
    if child_pid:
        value["child_pid"] = int(child_pid)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False)


def _event(value):
    sys.stdout.write(json.dumps(value, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _success(text):
    _event({"type": "thread.started", "thread_id": "fake-thread"})
    _event({"type": "turn.started"})
    _event({
        "type": "item.completed",
        "item": {"id": "item-0", "type": "agent_message", "text": text},
    })
    _event({
        "type": "turn.completed",
        "usage": {
            "input_tokens": 1,
            "cached_input_tokens": 0,
            "output_tokens": 1,
            "reasoning_output_tokens": 0,
        },
    })


def main():
    if "--version" in sys.argv:
        print("codex-cli 0.153.4-fake")
        return 0
    if "--help" in sys.argv or len(sys.argv) < 2:
        probe_metadata_path = os.environ.get("FAKE_CODEX_PROBE_METADATA_PATH")
        if probe_metadata_path:
            with open(probe_metadata_path, "w", encoding="utf-8") as handle:
                json.dump({"pid": os.getpid()}, handle)
        delay = float(os.environ.get("FAKE_CODEX_PROBE_DELAY", "0"))
        if delay:
            time.sleep(delay)
        _help()
        return 0

    _record_formal_start()
    scenario = os.environ.get("FAKE_CODEX_SCENARIO", "success")
    if scenario == "no_stdin":
        # Deliberately leave stdin unread.  The runtime test sends more than
        # a pipe can buffer so a synchronous writer would block forever.
        _metadata("")
        delay = float(os.environ.get("FAKE_CODEX_DELAY", "60"))
        time.sleep(delay)
        return 0

    prompt = sys.stdin.read()
    _metadata(prompt)
    text = os.environ.get("FAKE_CODEX_TEXT", "fake response")

    if scenario == "stderr_flood":
        sys.stderr.write("stderr-noise-" * 65536)
        sys.stderr.flush()
        _success(text)
        return 0
    if scenario == "sensitive":
        sys.stderr.write(os.environ.get("FAKE_SECRET", "secret") + "\n")
        sys.stderr.flush()
        _success("safe response")
        return 0
    if scenario == "corrupt":
        sys.stdout.write("{not-json}\n")
        sys.stdout.flush()
        return 0
    if scenario == "action":
        _event({"type": "thread.started", "thread_id": "fake-thread"})
        _event({"type": "turn.started"})
        _event({
            "type": "item.started",
            "item": {
                "id": "item-action",
                "type": "command_execution",
                "command": "echo unsafe",
                "aggregated_output": "",
                "exit_code": None,
                "status": "in_progress",
            },
        })
        time.sleep(60)
        return 0
    if scenario == "output_limit":
        _event({"type": "thread.started", "thread_id": "fake-thread"})
        _event({"type": "turn.started"})
        for index in range(100):
            _event({
                "type": "item.completed",
                "item": {
                    "id": "item-%d" % index,
                    "type": "agent_message",
                    "text": "x" * 1024,
                },
            })
        return 0
    if scenario == "nonzero":
        _success(text)
        return 7
    if scenario in {"delay", "ignore_terminate", "spawn_child"}:
        if scenario in {"ignore_terminate", "spawn_child"}:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            child = subprocess.Popen(["/bin/sh", "-c", "sleep 60"])
            os.environ["FAKE_CODEX_CHILD_PID"] = str(child.pid)
            _metadata(prompt)
        delay = float(os.environ.get("FAKE_CODEX_DELAY", "60"))
        time.sleep(delay)
        _success(text)
        return 0

    _success(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

# 实现带二级菜单的插件

## 一、如何写带有二级菜单的插件

1. 声明一个 `Class`，继承父类 `GptAcademicPluginTemplate`

    ```python
    from crazy_functions.plugin_template.plugin_class_template import GptAcademicPluginTemplate
    from crazy_functions.plugin_template.plugin_class_template import ArgProperty

    class Demo_Wrap(GptAcademicPluginTemplate):
        def __init__(self): ...
    ```

2. 声明二级菜单中需要的变量，覆盖父类的`define_arg_selection_menu`函数。

    ```python
    class Demo_Wrap(GptAcademicPluginTemplate):
        ...

        def define_arg_selection_menu(self):
            """
            定义插件的二级选项菜单

            第一个参数，名称`main_input`，参数`type`声明这是一个文本框，文本框上方显示`title`，文本框内部显示`description`，`default_value`为默认值；
            第二个参数，名称`advanced_arg`，参数`type`声明这是一个文本框，文本框上方显示`title`，文本框内部显示`description`，`default_value`为默认值；
            第三个参数，名称`allow_cache`，参数`type`声明这是一个下拉菜单，下拉菜单上方显示`title`+`description`，下拉菜单的选项为`options`，`default_value`为下拉菜单默认值；
            """
            gui_definition = {
                "main_input":
                    ArgProperty(title="ArxivID", description="输入Arxiv的ID或者网址", default_value="", type="string").model_dump_json(),
                "advanced_arg":
                    ArgProperty(title="额外的翻译提示词",
                                description=r"如果有必要, 请在此处给出自定义翻译命令",
                                default_value="", type="string").model_dump_json(),
                "allow_cache":
                    ArgProperty(title="是否允许从缓存中调取结果", options=["允许缓存", "从头执行"], default_value="允许缓存", description="无", type="dropdown").model_dump_json(),
            }
            return gui_definition
        ...
    ```


    > [!IMPORTANT]
    >
    > ArgProperty 中每个条目对应一个参数，`type == "string"`时，使用文本块，`type == dropdown`时，使用下拉菜单。
    >
    > 注意：`main_input` 和 `advanced_arg`是两个特殊的参数。`main_input`会自动与界面右上角的`输入区`进行同步，而`advanced_arg`会自动与界面右下角的`高级参数输入区`同步。除此之外，参数名称可以任意选取。其他细节详见`crazy_functions/plugin_template/plugin_class_template.py`。




3. 编写插件程序，覆盖父类的`execute`函数。

    例如：

    ```python
    class Demo_Wrap(GptAcademicPluginTemplate):
        ...
        ...

        def execute(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
            """
            执行插件

            plugin_kwargs字典中会包含用户的选择，与上述 `define_arg_selection_menu` 一一对应
            """
            allow_cache = plugin_kwargs["allow_cache"]
            advanced_arg = plugin_kwargs["advanced_arg"]

            if allow_cache == "从头执行": plugin_kwargs["advanced_arg"] = "--no-cache " + plugin_kwargs["advanced_arg"]
            yield from Latex翻译中文并重新编译PDF(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)

    ```



4. 注册插件

    将以下条目插入`crazy_functional.py`即可。注意，与旧插件不同的是，`Function`键值应该为None，而`Class`键值为上述插件的类名称（`Demo_Wrap`）。
    ```
        "新插件": {
            "Group": "学术",
            "Color": "stop",
            "AsButton": True,
            "Info": "插件说明",
            "Function": None,
            "Class": Demo_Wrap,
        },
    ```

5. 已经结束了，启动程序测试吧~！



## 二、背后的原理（需要JavaScript的前置知识）


### (I) 首先介绍三个Gradio官方没有的重要前端函数

主javascript程序`common.js`中有三个Gradio官方没有的重要API

1. `get_data_from_gradio_component`
    这个函数可以获取任意gradio组件的当前值，例如textbox中的字符，dropdown中的当前选项，chatbot当前的对话等等。调用方法举例：
    ```javascript
    // 获取当前的对话
    let chatbot = await get_data_from_gradio_component('gpt-chatbot');
    ```

2. `get_gradio_component`
    有时候我们不仅需要gradio组件的当前值，还需要它的label值、是否隐藏、下拉菜单其他可选选项等等，而通过这个函数可以直接获取这个组件的句柄。举例：
    ```javascript
    // 获取下拉菜单组件的句柄
    var model_sel = await get_gradio_component("elem_model_sel");
    // 获取它的所有属性，包括其所有可选选项
    console.log(model_sel.props)
    ```


3. `push_data_to_gradio_component`
    这个函数可以将数据推回gradio组件，例如textbox中的字符，dropdown中的当前选项等等。调用方法举例：

    ```javascript
    // 修改一个按钮上面的文本
    push_data_to_gradio_component("btnName", "gradio_element_id", "string");

    // 隐藏一个组件
    push_data_to_gradio_component({ visible: false, __type__: 'update' }, "plugin_arg_menu", "obj");

    // 修改组件label
    push_data_to_gradio_component({ label: '新label的值', __type__: 'update' }, "gpt-chatbot", "obj")

    // 第一个参数是value，
    //     - 可以是字符串（调整textbox的文本，按钮的文本）；
    //     - 还可以是 { visible: false, __type__: 'update' }  这样的字典（调整visible, label, choices）
    // 第二个参数是elem_id
    // 第三个参数是"string" 或者 "obj"
    ```


### (II) 从点击插件到执行插件的逻辑过程

简述：程序启动时把每个插件的二级菜单编码为BASE64，存储在用户的浏览器前端，用户调用对应功能时，会按照插件的BASE64编码，将平时隐藏的菜单（有选择性地）显示出来。

1. 启动阶段（主函数 `main.py` 中），遍历每个插件，生成二级菜单的BASE64编码，存入变量`register_advanced_plugin_init_code_arr`。
    ```python
    def get_js_code_for_generating_menu(self, btnName):
        define_arg_selection = self.define_arg_selection_menu()
        DEFINE_ARG_INPUT_INTERFACE = json.dumps(define_arg_selection)
        return base64.b64encode(DEFINE_ARG_INPUT_INTERFACE.encode('utf-8')).decode('utf-8')
    ```


2. 用户加载阶段（主javascript程序`common.js`中），浏览器加载`register_advanced_plugin_init_code_arr`，存入本地的字典`advanced_plugin_init_code_lib`：

    ```javascript
    advanced_plugin_init_code_lib = {}
    function register_advanced_plugin_init_code(key, code){
        advanced_plugin_init_code_lib[key] = code;
    }
    ```

3. 用户点击插件按钮（主函数 `main.py` 中）时，仅执行以下javascript代码，唤醒隐藏的二级菜单（生成菜单的代码在`common.js`中的`generate_menu`函数上）：


    ```javascript
    // 生成高级插件的选择菜单
    function run_advanced_plugin_launch_code(key){
        generate_menu(advanced_plugin_init_code_lib[key], key);
    }
    function on_flex_button_click(key){
        run_advanced_plugin_launch_code(key);
    }
    ```

    ```python
    click_handle = plugins[k]["Button"].click(None, inputs=[], outputs=None, _js=f"""()=>run_advanced_plugin_launch_code("{k}")""")
    ```

4. 当用户点击二级菜单的执行键时，通过javascript脚本模拟点击一个隐藏按钮，触发后续程序（`common.js`中的`execute_current_pop_up_plugin`，会把二级菜单中的参数缓存到`invisible_current_pop_up_plugin_arg_final`，然后模拟点击`invisible_callback_btn_for_plugin_exe`按钮）。隐藏按钮的定义在（主函数 `main.py` ），该隐藏按钮会最终触发`route_switchy_bt_with_arg`函数（定义于`themes/gui_advanced_plugin_class.py`）：

    ```python
    click_handle_ng = new_plugin_callback.click(route_switchy_bt_with_arg, [
            gr.State(["new_plugin_callback", "usr_confirmed_arg"] + input_combo_order),
            new_plugin_callback, usr_confirmed_arg, *input_combo
        ], output_combo)
    ```

5. 最后，`route_switchy_bt_with_arg`中，会搜集所有用户参数，统一集中到`plugin_kwargs`参数中，并执行对应插件的`execute`函数。
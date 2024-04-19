# encoding: utf-8
# @Time   : 2024/3/17
# @Author : Spike
# @Descr   :

from common.toolbox import update_ui, CatchException
from common import gr_converter_html
from crazy_functions.reader_fns.crazy_box import json_args_return
from crazy_functions.Reader_自定义插件流程 import Reader_多阶段生成回答
from crazy_functions.reader_fns.project_feishu import _get_story, ProjectFeishu


@CatchException
def Project_获取项目数据(user_input, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    if llm_kwargs['project_config'].get('project_user_key'):
        filter_time, unscheduled, un_issue = json_args_return(plugin_kwargs, ['筛选时间范围',
                                                                    '筛选未排期需求', '筛选用例详情'], None)
        un_issue = un_issue or llm_kwargs.get('关联缺陷')
        user_input = user_input if not user_input else f"获取前后{filter_time}天的需求列表" + f"\n{user_input}"

        project_status = gr_converter_html.get_fold_panel()
        user_key = llm_kwargs["project_config"].get("project_user_key")
        header = llm_kwargs["project_config"].get("project_header")
        gpt_result = project_status(f'正在努力爬取`{user_key[:5]}***{user_key[-5:]}`用户数据...')
        chatbot.append([user_input, gpt_result])
        yield from update_ui(chatbot, history)

        story_list = ProjectFeishu('', header=header, user_key=user_key
                                   ).get_home_story_list(filter_time, unscheduled, un_issue)
        project_content = ''
        for api_name, story in story_list:
            chatbot[-1][1] = project_status(f'当前正在爬取`{api_name}`项目', project_content)
            yield from update_ui(chatbot, history)
            project_content = "\n\n".join([_get_story(i) for i in story])
            chatbot[-1][1] = project_status(f'`{api_name}`项目爬取完成', project_content)
            yield from update_ui(chatbot, history)

        story_list_content = [user_input, project_content]
        plugin_kwargs['embedding_content'] = story_list_content
        chatbot[-1][1] = project_status(f'所有数据爬取完成！', project_content, 'Done')
        yield from update_ui(chatbot, history)
        yield from Reader_多阶段生成回答(user_input, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt,
                                         web_port)
        return
    chatbot.append(
        [user_input, '没有配置user-key，无法获取需求详情，请在右下角设置-个人中心-中配置`Feishu Project user-key`'])
    yield from update_ui(chatbot, history)

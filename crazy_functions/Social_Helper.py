import pickle, os, random
from toolbox import CatchException, update_ui, get_conf, get_log_folder, update_ui_lastest_msg
from crazy_functions.crazy_utils import input_clipping
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from crazy_functions.json_fns.pydantic_io import GptJsonIO, JsonStringError
from request_llms.bridge_all import predict_no_ui_long_connection
from pydantic import BaseModel, Field
from loguru import logger


SOCIAL_NETWOK_WORKER_REGISTER = {}

class SocialNetwork():
    def __init__(self):
        self.people = []

class SaveAndLoad():
    def __init__(self, user_name, llm_kwargs, auto_load_checkpoint=True, checkpoint_dir=None) -> None:
        self.user_name = user_name
        self.checkpoint_dir = checkpoint_dir
        if auto_load_checkpoint:
            self.social_network = self.load_from_checkpoint(checkpoint_dir)
        else:
            self.social_network = SocialNetwork()

    def does_checkpoint_exist(self, checkpoint_dir=None):
        import os, glob
        if checkpoint_dir is None: checkpoint_dir = self.checkpoint_dir
        if not os.path.exists(checkpoint_dir): return False
        if len(glob.glob(os.path.join(checkpoint_dir, "social_network.pkl"))) == 0: return False
        return True

    def save_to_checkpoint(self, checkpoint_dir=None):
        if checkpoint_dir is None: checkpoint_dir = self.checkpoint_dir
        with open(os.path.join(checkpoint_dir, 'social_network.pkl'), "wb+") as f:
            pickle.dump(self.social_network, f)
        return

    def load_from_checkpoint(self, checkpoint_dir=None):
        if checkpoint_dir is None: checkpoint_dir = self.checkpoint_dir
        if self.does_checkpoint_exist(checkpoint_dir=checkpoint_dir):
            with open(os.path.join(checkpoint_dir, 'social_network.pkl'), "rb") as f:
                social_network = pickle.load(f)
                return social_network
        else:
            return SocialNetwork()


class Friend(BaseModel):
    friend_name: str = Field(description="name of a friend")
    friend_description: str = Field(description="description of a friend (everything about this friend)")
    friend_relationship: str = Field(description="The relationship with a friend (e.g. friend, family, colleague)")


def structure_output(txt, prompt, err_msg, run_gpt_fn, pydantic_cls):
    gpt_json_io = GptJsonIO(pydantic_cls)
    analyze_res = run_gpt_fn(
        txt, 
        sys_prompt=prompt + gpt_json_io.format_instructions
    )
    try:
        friend:Friend = gpt_json_io.generate_output_auto_repair(analyze_res, run_gpt_fn)
    except JsonStringError as e:
        return None, err_msg

    err_msg = ""
    return friend, err_msg
            

class SocialNetworkWorker(SaveAndLoad):
    def run(self, txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
        run_gpt_fn = lambda inputs, sys_prompt: predict_no_ui_long_connection(inputs=inputs, llm_kwargs=llm_kwargs, history=[], sys_prompt=sys_prompt, observe_window=[])
        # adding friend: 🧑‍🤝‍🧑
        if txt.startswith("add-friend"):
            friend, err_msg = structure_output(
                txt=txt,
                prompt="根据提示, 解析一个联系人的身份信息\n\n",
                err_msg=f"不能理解该联系人",
                run_gpt_fn=run_gpt_fn,
                pydantic_cls=Friend
            )
            if friend:
                self.add_friend(friend)
            else:
                yield from update_ui_lastest_msg(lastmsg=err_msg, chatbot=chatbot, history=history, delay=0)

        # learn friend info: 🧑‍🤝‍🧑
        if txt.startswith("give-advice"):
            # randomly select a friend
            if len(self.social_network.people) == 0:
                yield from update_ui_lastest_msg(lastmsg="没有联系人", chatbot=chatbot, history=history, delay=0)
                return
            else:
                # randomly select a friend
                friend = random.choice(self.social_network.people)
                yield from update_ui_lastest_msg(lastmsg=f"给你一个建议: {friend.friend_description}", chatbot=chatbot, history=history, delay=0)

    def add_friend(self, friend):
        # check whether the friend is already in the social network
        for f in self.social_network.people:
            if f.friend_name == friend.friend_name:
                f.friend_description = friend.friend_description
                f.friend_relationship = friend.friend_relationship
                logger.info(f"Repeated friend, update info: {friend}")
                return
        logger.info(f"Add a new friend: {friend}")
        self.social_network.people.append(friend)
        return


@CatchException
def I人助手(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):

    # 1. we retrieve worker from global context
    user_name = chatbot.get_user()
    checkpoint_dir=get_log_folder(user_name, plugin_name='experimental_rag')
    if user_name in SOCIAL_NETWOK_WORKER_REGISTER:
        social_network_worker = SOCIAL_NETWOK_WORKER_REGISTER[user_name]
    else:
        social_network_worker = SOCIAL_NETWOK_WORKER_REGISTER[user_name] = SocialNetworkWorker(
            user_name, 
            llm_kwargs, 
            checkpoint_dir=checkpoint_dir, 
            auto_load_checkpoint=True
        )

    # 2. save
    yield from social_network_worker.run(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request)
    social_network_worker.save_to_checkpoint(checkpoint_dir)
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


from toolbox import CatchException, update_ui, get_conf, get_log_folder, update_ui_lastest_msg
from crazy_functions.crazy_utils import input_clipping
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
import pickle, os

SOCIAL_NETWOK_WORKER_REGISTER = {}

class SocialNetwork():
    def __init__(self):
        self.people = []

class SocialNetworkWorker():
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


@CatchException
def I人助手(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request, num_day=5):

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
    social_network_worker.social_network.people.append("张三")
    social_network_worker.save_to_checkpoint(checkpoint_dir)
    chatbot.append(["good", "work"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


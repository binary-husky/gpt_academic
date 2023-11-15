from pydantic import BaseModel, Field
from typing import List
from comm_tools.toolbox import update_ui_lastest_msg, disable_auto_promotion
from request_llms.bridge_all import predict_no_ui_long_connection
from crazy_functions.json_fns.pydantic_io import GptJsonIO, JsonStringError
import time
import pickle

def have_any_recent_upload_files(chatbot):
    _5min = 5 * 60
    if not chatbot: return False    # chatbot is None
    most_recent_uploaded = chatbot._cookies.get("most_recent_uploaded", None)
    if not most_recent_uploaded: return False   # most_recent_uploaded is None
    if time.time() - most_recent_uploaded["time"] < _5min: return True # most_recent_uploaded is new
    else: return False  # most_recent_uploaded is too old

class GptAcademicState():
    def __init__(self):
        self.reset()

    def reset(self):
        pass

    def lock_plugin(self, chatbot):
        chatbot._cookies['plugin_state'] = pickle.dumps(self)

    def unlock_plugin(self, chatbot):
        self.reset()
        chatbot._cookies['plugin_state'] = pickle.dumps(self)

    def set_state(self, chatbot, key, value):
        setattr(self, key, value)
        chatbot._cookies['plugin_state'] = pickle.dumps(self)

    def get_state(chatbot, cls=None):
        state = chatbot._cookies.get('plugin_state', None)
        if state is not None:   state = pickle.loads(state)
        elif cls is not None:   state = cls()
        else:                   state = GptAcademicState()
        state.chatbot = chatbot
        return state

class GatherMaterials():
    def __init__(self, materials) -> None:
        materials = ['image', 'prompt']
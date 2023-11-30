from toolbox import CatchException, update_ui, get_conf, select_api_key, get_log_folder
from crazy_functions.multi_stage.multi_stage_utils import GptAcademicState
from crazy_functions.crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
import random

class 小游戏(GptAcademicState):
    def __init__(self):
        self.need_game_reset = True
        self.llm_kwargs = None
        super().__init__()
    
    def lock_plugin(self, chatbot):
        chatbot._cookies['lock_plugin'] = 'crazy_functions.互动小游戏->谁是卧底'
        self.dump_state(chatbot)

    def unlock_plugin(self, chatbot):
        self.reset()
        chatbot._cookies['lock_plugin'] = None
        self.dump_state(chatbot)

    def set_state(self, chatbot, key, value):
        return super().set_state(chatbot, key, value)

    def init_game(self, chatbot):
        chatbot.get_cookies()['lock_plugin'] = ''

    def clean_up_game(self, chatbot):
        chatbot.get_cookies()['lock_plugin'] = None

    def init_player(self):
        pass

    def step(self, prompt, chatbot):
        pass

    def continue_game(self, prompt, chatbot):
        if self.need_game_reset:
            self.need_game_reset = False
            yield from self.init_game(chatbot)
        yield from self.step(prompt, chatbot)
        self.dump_state(chatbot)
        yield update_ui(chatbot=chatbot, history=[])

class 小游戏_谁是卧底_玩家():
    def __init__(self, game_handle, card, llm_model, name) -> None:
        self.game_handle = game_handle
        self.card = card
        self.name = name
        self.is_out = False
        self.llm_model = llm_model
        self.is_human = llm_model == 'human'
        self.what_player_has_spoken = []

    def speek(self, content=None):
        if content is None:
            assert not self.is_human
            speak_what = yield from
        else:
            self.what_player_has_spoken.append(content)

    def agi_speek(self):
        inputs = f'please say something about {self.card}'
        res = yield from request_gpt_model_in_new_thread_with_ui_alive(
            inputs = inputs,
            inputs_show_user=inputs,
            llm_kwargs=self.game_handle.llm_kwargs,
            chatbot=chatbot,
            history=history,
            sys_prompt=sys_prompt
        )
        pass

    def vote(self, content=None):
        if content is None:
            assert not self.is_human
            self.vote_who = yield from
        else:
            try:
                self.vote_who = int(content)
            except:
                self.vote_who = None

    def agi_vote(self):
        pass

class 小游戏_谁是卧底(小游戏):
    def __init__(self):
        self.game_phase = '发言' # 投票
        super().__init__()

    def init_game(self, chatbot):
        self.n_players = 3
        self.n_ai_players = self.n_players - 1
        card = "橙子"
        undercover_card = "橘子"
        llm_model = self.llm_kwargs['llm_model']
        self.players = [
            小游戏_谁是卧底(self, card, llm_model, str(i)) for i in range(self.n_players)
        ]

        undercover = random.randint(0, self.n_players-1)
        human = 0

        self.players[undercover].card = undercover_card
        self.players[human].llm_model = 'human'
        super().init_game(chatbot)

    def who_is_out(self):
        votes = {}
        for player in self.players:
            if player.is_out: continue
            if player.vote is None: continue
            if player.vote not in votes: votes[player.vote] = 0
            votes[player.vote] += 1
        max_votes = max(votes.values())
        players_with_max_votes = [player for player, vote_count in votes.items() if vote_count == max_votes]
        for player in players_with_max_votes:
            print('淘汰了', player.name)
            player.is_out = True
        return players_with_max_votes

    def step(self, prompt, chatbot):

        if self.game_phase == '发言':
            for player in self.players:
                if player.is_out: continue
                if player.is_human:
                    player.speek(prompt)
                else:
                    player.speek()
            self.game_phase = '投票'

        elif self.game_phase == '投票':
            for player in self.players:
                if player.is_out: continue
                if player.is_human:
                    player.vote(prompt)
                else:
                    player.vote()
            self.who_is_out()
            if len([player for player in self.players if not player.is_out]) <= 2:
                if sum([player for player in self.players if player.is_undercover]) == 1:
                    print('卧底获胜')
                else:
                    print('平民获胜')
                self.need_game_reset = True
            self.game_phase = '发言'

        else:
            raise RuntimeError
        

@CatchException
def 谁是卧底(prompt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port):
    # 尚未完成
    history = []    # 清空历史
    state = 小游戏_谁是卧底.get_state(chatbot, 小游戏_谁是卧底)
    state.llm_kwargs = llm_kwargs
    yield from state.continue_game(prompt, chatbot)

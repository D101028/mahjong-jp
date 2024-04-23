"""
    Class main process works
"""

from lang import tc as lang
from ext import support

from player import Player
from pai import *
from action import Performer

from typing import Union
import random

class GameCore:
    def __init__(self, gametype:str = lang.yonin_ton_ikkyoku):
        self.gametype = gametype
        
        self.player_num = support.gametype_player_num_dict[gametype]
        self.players = [Player(ID = n) for n in range(self.player_num)]
        self.gameround: GameRound

    def process(self):
        self.gameround = GameRound(gametype = self.gametype, 
                                   chanfon = support.fonwei_tuple[0], 
                                   rnd = 1, 
                                   benchan = 0)
        while True:
            is_next_round = self.gameround.run() # return a bool (whether next round)
            if not is_next_round:
                break
            else:
                self.gameround.next_round()

    def run(self):
        self.process()

class GameRound:
    """一局遊戲(ex 東一局、東二局)"""
    def __init__(self, gametype:str, chanfon:str, rnd:int, riichiboo:int, benchan:int, players:list[Player]):
        self.gametype = gametype # lang.yonin_ton_ikkyoku, lang.yonin_ton, lang.yonin_nan, lang.sannin_ton_ikkyoku, lang.sannin_ton, lang.sannin_nan
        self.chanfon = chanfon # lang.ton, lang.nan, lang.shaa, lang.pei, support.fonwei_tuple[i]
        self.round = rnd # 東一局:  1, 東二: 2, ..., 南一: 5, ...
        self.riichiboo = riichiboo
        self.benchan = benchan
        self.players = players # {lang.ton: Player, lang.nan: Player, ...}
        self.player_pos_in_action = 0 # 0:ton, 1:nan, 2:shaa, 3:pei
        self.yama = Yama(gametype)
        # self.junme = 0 # plus 1 if 東家摸牌 or 任一人吃、碰、槓、拔北

        self.performer = Performer()

    def run(self):
        if self.gametype == lang.yonin_ton_ikkyoku:
            self.run_yonin_ton_ikkyoku()
        return True
    
    def run_yonin_ton_ikkyoku(self):
        if self.gametype != lang.yonin_ton_ikkyoku:
            raise RuntimeError("Error")
        
        if self.chanfon == support.fonwei_tuple[0] and self.round == 1 and self.benchan == 0:
            # init players' data            
            # set players' positions and tensuu
            pos_list = support.fonwei_tuple[0:4]
            random.shuffle(pos_list)
            count = 0
            for player in self.players:
                player.menfon = pos_list[count]
                player.tensuu = support.gametype_tensuu_init_dict[self.gametype]
                count += 1
            # sort the position
            self.players.sort(key = lambda player: support.chanfon_pos_dict[player.menfon])

        self.yama.deal(self.players)

        self.performer.draw_all()
        
        while True: # run all junme
            if len(self.yama.dora_pointers) >= 5:
                # 四槓散了
                pass 

            self.performer.refresh_river()

            # the player in this round
            player = self.players[self.player_pos_in_action]

            self.yama.draw(player)

            player_round = PlayerRound(player = player, 
                                       yama = self.yama, 
                                       chanfon = self.chanfon)

            player_round.run()

            self.player_pos_in_action = (self.player_pos_in_action + 1) % 4

    def next_round(self):
        # clear and change players' data
        return 
    
class PlayerRound:
    """玩家摸牌、打牌一次"""
    def __init__(self, gametype: str, player: Player, yama: Yama, chanfon: str, is_ankan_rinshan: bool = False) -> None:
        self.gametype = gametype
        self.player = player
        self.yama = yama
        self.chanfon = chanfon
        self.is_ankan_rinshan = is_ankan_rinshan

    def run(self):
        if self.gametype in (lang.yonin_ton_ikkyoku):
            self.run_yonin()

    def run_yonin(self):
        # 玩家摸牌
        pai = self.yama.draw(self.player) # including adding player_junme

        # 自摸判定
        if is_agari(self.player.tehai.pai_list + [pai]):
            param = Param(self.player.is_riichi, 
                          self.player.riichi_junme, 
                          self.player.player_junme, 
                          True, False, False, 
                          self.yama.get_available_pai_num(), 
                          self.player.menfon, 
                          self.chanfon, 
                          self.is_ankan_rinshan)
            agari_result = AgariResult(self.player.tehai, agari_pai=pai, param=param)

        # 暗槓處理

        # 玩家打牌

        # 榮和判斷

        # 鳴牌處理

        # 四槓流局判斷

        # 荒牌流局判斷
    
    def run_sanin(self):
        # 玩家摸牌
        self.yama.draw(self.player)

        # 自摸判定

        # 暗槓(拔北)處理

        # 玩家打牌

        # 榮和判斷

        # 鳴牌處理

        # 四槓流局判斷

        # 荒牌流局判斷
        
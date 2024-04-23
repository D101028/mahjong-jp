"""
    Class main process works
"""

from lang import tc as lang
from ext import support

from player import Player
from pai import Yama
from gameaction import Performer

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
    def __init__(self, gametype:str, chanfon:str, rnd:str, benchan:int, players:list[Player]):
        self.gametype = gametype
        self.chanfon = chanfon
        self.round = rnd
        self.benchan = benchan
        self.players = players
        self.player_pos_in_action = 0 # 0:ton, 1:nan, 2:shaa, 3:pei
        self.yama = Yama(gametype)
        self.junme = 0 # plus 1 if 東家摸牌 or 任一人吃、碰、槓、拔北

        self.performer = Performer()

    def run(self):
        if self.gametype == lang.yonin_ton_ikkyoku:
            self.run_yonin_ton_ikkyoku()
        return True
    
    def run_yonin_ton_ikkyoku(self):
        if self.gametype != lang.yonin_ton_ikkyoku:
            print("Error 1")
            exit()
        
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

            # tsumo
            

            self.player_pos_in_action = (self.player_pos_in_action + 1) % 4

    def next_round(self):
        # clear and change players' data
        return 
    

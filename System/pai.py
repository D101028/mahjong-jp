"""
    Pai, Furo, Yama, Tehai class
"""

from ext.index import *
from lang import tc as lang

from player import Player

import random

class Pai:
    def __init__(self, name: str):
        self.name = name
        self.number = int(name[0]) if name[0] != "0" else 5
        self.type = name[1]
        self.is_akadora = (name[0] == "0")

def create_pai(name: str):
    return Pai(name)

def create_pai_list(name_list: list[str]):
    return [create_pai(name) for name in name_list]

class Yama:
    def __init__(self, gametype: str):
        self.gametype = gametype 

        self.pai_list: list[Pai]
        self.dora_pointers: list[Pai] = []

        if gametype == lang.yonin_ton_ikkyoku:
            pai_list_temp = PAI_INDEX_WITH_AKADORA.copy()
            random.shuffle(pai_list_temp)
            self.pai_list = create_pai_list(pai_list_temp)

    def deal(self, players: list[Player]):
        for player in players:
            # deal pais
            player.tehai = Tehai(self.pai_list[0:13])
            del self.pai_list[0:13]
        # open dora pointer
        self.dora_pointers.append(self.pai_list[0])
        del self.pai_list[0]
    
    def get_available_pai_num(self):
        if self.gametype == lang.yonin_ton_ikkyoku:
            return len(self.pai_list) + len(self.dora_pointers) - 14 # wanpai cannot be drawn


class Furo:
    def __init__(self):
        self.type: str
        self.pai_list: list[Pai]
        self.rotate: int | None
        self.be_minpai_player_id: int

class Tehai:
    def __init__(self, pai_list: list[Pai]):
        self.pai_list: pai_list
        self.furo: Furo
    
    def sort(self):
        return 


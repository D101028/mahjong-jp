"""
    Toppest class of game process
"""
from lang import tc as lang

from gamecore import GameCore
from player import Player

class Game:
    def __init__(self, gametype:str = lang.yonin_ton_ikkyoku):
        # create a mahjong game
        self.gametype = gametype
        self.gamecore = GameCore(gametype)
    
    def run(self):
        self.gamecore.run()

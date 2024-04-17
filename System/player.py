"""
    Player class
"""

from pai import Pai, Furo, Tehai

class Player:
    def __init__(self, ID: int):
        self.ID = ID # 0,1,2,(3)
        self.tehai: Tehai 
        self.tensuu: int 
        self.menfon: str

"""
    Player class
    including calculate is_agari
    HansuuResult class
"""
from typing import Union
from ext import support
from ext.support import Yaku
from lang import tc as lang

import pai
from pai import Pai, Furo, Tehai, TehaiComb, Param, HansuuResult

class Player:
    def __init__(self, ID: int):
        self.ID = ID # 0,1,2,(3)
        self.tehai: Tehai 
        self.tensuu: int 
        self.menfon: str # lang.ton, lang.nan, lang.shaa, lang.pei

        self.tsumo_pai: Union[Pai, None] = None
        self.ron_temp_pai: Pai | None = None

        self.is_riichi: bool = False
        self.riichi_junme: Union[bool, None] = None

    def is_menchin(self):
        return all([furo.type == lang.ankan for furo in self.tehai.furo_list])

    def is_agari(self):
        # 檢查胡牌型
        
        if self.tsumo_pai is None and self.ron_temp_pai is None:
            return False
        furo_pai = []
        for furo in self.tehai.furo_list:
            furo_pai += furo.to_agari_cal()
        all_pai = self.tehai.pai_list + furo_pai + ([self.tsumo_pai] if not self.tsumo_pai is None else [self.ron_temp_pai])
        all_pai.sort(key = lambda p: p.usual_name)

        return pai.is_agari(all_pai)




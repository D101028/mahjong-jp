"""
    Class main process works
"""

import random
from typing import Union

from lang import tc as lang
from ext import support
from player import Player, River
from pai import *
from action import *


class GameCore:
    def __init__(self, gametype:str = lang.yonin_ton_ikkyoku):
        self.gametype = gametype
        self.performer = Performer()
        
        self.player_num = support.gametype_player_num_dict[gametype]
        self.players = [Player(ID = n) for n in range(self.player_num)]
        self.gameround: GameRound

    def process(self):
        self.gameround = GameRound(gametype = self.gametype, 
                                   performer = self.performer, 
                                   chanfon = support.fonwei_tuple[0], 
                                   rnd = 1, 
                                   riichiboo = 0, 
                                   benchan = 0, 
                                   players = self.players)
        
        gameresult = self.gameround.run() # 遞迴跑完所有局數，回傳遊戲結果
        for p in self.players:
            print(p.ID, ":", p.tensuu)

    def run(self):
        # init players' data            
        # set players' positions and tensuu
        pos_list = list(support.fonwei_tuple[0:4])
        random.shuffle(pos_list)
        count = 0
        for player in self.players:
            player.menfon = pos_list[count]
            player.tensuu = support.gametype_tensuu_init_dict[self.gametype]
            count += 1
        self.players.sort(key=lambda p: support.fonwei_tuple.index(p.menfon))
        self.process()

class GameRound:
    """一局遊戲(ex 東一局、東二局)，run 以遞迴"""
    def __init__(self, gametype:str, performer: Performer, chanfon:str, rnd:int, riichiboo:int, benchan:int, players:list[Player]):
        self.gametype = gametype # lang.yonin_ton_ikkyoku, lang.yonin_ton, lang.yonin_nan, lang.sannin_ton_ikkyoku, lang.sannin_ton, lang.sannin_nan
        self.performer = performer
        self.chanfon = chanfon # lang.ton, lang.nan, lang.shaa, lang.pei, support.fonwei_tuple[i]
        self.round = rnd # 東一局:  1, 東二: 2, ..., 南一: 1, ...
        self.riichiboo = riichiboo # 供托立直棒數
        self.benchan = benchan # 本場數
        self.players = players
        self.yama = Yama(gametype)

        self.next_round_num: int

        print(self.chanfon + str(self.round) + "局 " + str(self.benchan) + "本場 " + "供托：" + str(self.riichiboo))

    def run(self):
        if self.gametype == lang.yonin_ton_ikkyoku:
            return self.run_yonin_ton_ikkyoku()
    
    def run_yonin_ton_ikkyoku(self):
        self.yama.deal(self.players)

        print("draw table")
        
        print("refresh river")


        ################################ cheat #############################################
        # self.players[0].tehai.pai_list = create_pai_list("111222055777s1z")
        # self.players[1].tehai.pai_list = create_pai_list("23456789s123456z")
        # self.players[2].tehai.pai_list = create_pai_list("1257s12345678p1z")
        # self.players[3].tehai.pai_list = create_pai_list("19s19m19p1234567z")
        ################################ cheat #############################################


        player_round = PlayerRoundYonin(gameround = self, 
                                        player = self.players[0], 
                                        player_pos = 0)

        status = player_round.run() # 遞迴跑完所有巡數，回傳結束狀態(自摸、榮和、和了連莊、流局連莊、荒牌流局、四槓散了、四風連打、九種九牌)
        
        return self.next(status)

    def get_players_rank(self) -> list[Player]:
        pass 

    def next(self, status: str):
        if self.gametype == lang.yonin_ton_ikkyoku:
            if status == lang.status_agari:
                return # 遊戲結果
            elif status == lang.status_agari_renchan:
                if (support.chanfon_pos_dict[self.chanfon]+1)*self.round >= 1 and all(self.players[0].tensuu > p.tensuu for p in self.players[1:]):
                    # 打超過東一局 且 莊家點數最大
                    if support.is_last_oya_infinitely_renchan and GetPlayerInput().boolean: # 獲得莊家是否連莊
                        return self.run_this()
                    return # 遊戲結果
                return self.run_this()
            elif status == lang.status_huanpai_ryukyoku: # 莊家 no ten 流局
                if (support.chanfon_pos_dict[self.chanfon]+1)*self.round >= 1 and max([p.tensuu for p in self.players]) >= support.gametype_tensuu_over_dict[self.gametype]:
                    # 打超過東一局 且 有人超過最低點
                    return # 遊戲結果
                return self.run_next(True)
            elif status in (lang.status_kyuushukyuuhai_ryukyoku, lang.status_ryukyoku_renchan,lang.status_suuhonrenda, lang.status_suukansanra, lang.status_suuchariichi, lang.status_sanchahoo):
                return self.run_this()
        elif self.gametype == lang.yonin_ton:
            pass 
    
    def run_this(self):
        self.clear_players_data()
        next_round = GameRound(self.gametype, self.performer, self.chanfon, self.round, self.riichiboo, self.benchan+1, self.players)
        return next_round.run()

    def run_next(self, is_ryukyoku):
        benchan = self.benchan + 1 if is_ryukyoku else 0
        self.clear_players_data()
        self.switch_fonwei()
        next_round = GameRound(self.gametype, self.performer, self.chanfon, self.next_round_num, self.riichiboo, benchan, self.players)
        return next_round.run()

    def clear_players_data(self):
        for p in self.players:
            p.tehai = Tehai([])
            p.river = River()
            p.tsumo_pai = None
            p.ron_temp_pai = None
            p.is_riichi = False
            p.riichi_junme = None
            p.player_junme = 0
            p.datsu_furiten_pais.clear()
            p.riichi_furiten_pais.clear()
            p.doujin_furiten_pais.clear()

    def switch_fonwei(self):
        # 輪換門風，必要時輪換場風、變更局數(儲存在self.next_round_num)
        for player in self.players:
            player.menfon = support.fonwei_tuple[(support.fonwei_tuple.index(player.menfon) + 1) % 4]
        if self.round == 4:
            self.next_round_num = 1
            self.chanfon = support.fonwei_tuple[support.fonwei_tuple.index(player.menfon) + 1]
        self.players.sort(key=lambda p: support.fonwei_tuple.index(p.menfon))

class PlayerRoundYonin:
    """玩家摸牌、打牌一次，run 以遞迴"""
    def __init__(self, 
                 gameround: GameRound, 
                 player: Player, 
                 player_pos: int, 
                 kan_type: Union[str, None] = None, 
                 is_chii_pon: bool = False) -> None:
        self.gameround = gameround
        self.player = player
        self.player_pos = player_pos
        self.kan_type = kan_type # lang.minkan, lang.ankan, lang.kakan
        self.is_chii_pon = is_chii_pon

        self.is_to_draw_rinshan = self.kan_type in (lang.minkan, lang.kakan, lang.ankan)

    def run(self):
        if not self.is_chii_pon:
            player_available_actions: list[str] = []
            # 玩家摸牌
            pai = self.player_draw()

            # 暗槓翻寶牌
            if self.kan_type == lang.ankan:
                self.open_dora()

            # 九種九牌判定
            if self.player.player_junme == 1:
                kyuuhai_count = 0
                for p in self.player.tehai.pai_list:
                    if p in yaochuu_list:
                        kyuuhai_count += 1
                if kyuuhai_count >= 9:
                    player_available_actions.append(lang.action_kyuushukyuuhai_ryukyoku)

            # 自摸判定
            if is_agari(self.player.tehai.pai_list + [pai]):
                param = Param(self.player.is_riichi, 
                            self.player.riichi_junme, 
                            self.player.player_junme, 
                            True, False, False, 
                            self.gameround.yama.get_available_pai_num(), 
                            self.player.menfon, 
                            self.gameround.chanfon, 
                            self.is_to_draw_rinshan, 
                            self.gameround.yama.dora_pointers, 
                            self.gameround.yama.uradora_pointers)
                agari_result_list = get_agari_result_list(self.player.tehai, pai, param)
                if agari_result_list: # agari
                    player_available_actions.append(lang.action_tsumo)
            # 立直判定
            pai_list = [pai] + self.player.tehai.pai_list
            riichi_pai_pos_list = []
            if self.player.is_menchin() and not self.player.is_riichi and self.gameround.yama.get_available_pai_num() >= 4:
                for i in range(len(pai_list)):
                    pai_list_copy = pai_list[:i] + pai_list[i+1:]
                    if get_tenpai_list(pai_list_copy):
                        riichi_pai_pos_list.append(i)
            if riichi_pai_pos_list:
                player_available_actions.append(lang.action_riichi)

            # 加、暗槓判斷(吃碰完不能槓)
            if self.gameround.yama.get_available_pai_num() != 0:
                # 加槓
                for f in self.player.tehai.furo_list:
                    if f.type == lang.koutsu and f.pai_tuple[0] in pai_list:
                        player_available_actions.append(lang.action_kakan)
                        break
                # 暗槓
                if self.player.is_riichi:
                    for p in pai_list:
                        if pai_list.count(p) < 4:
                            continue
                        for tc in self.player.tehai.tehai_comb_list:
                            if any(p in m.pai_list for m in tc.mentsu_list):
                                # 立直後禁止暗槓槓牌為任一聽牌組合中能組出順子
                                break
                        else:
                            player_available_actions.append(lang.action_ankan)
                            break
                else:
                    for p in pai_list:
                        if pai_list.count(p) < 4:
                            continue
                        player_available_actions.append(lang.action_ankan)
                        break

            # 行為處理
            action_dict = { 
                lang.action_kakan: self.kakan, 
                lang.action_ankan: self.ankan
            }
            print(player_available_actions)
            player_action = GetPlayerAction(player_available_actions) if player_available_actions else []
            for i in range(len(player_available_actions)):
                action = player_available_actions[i]
                if player_action.bool_list[i]:
                    if action == lang.action_tsumo:
                        self.tsumo(agari_result_list)
                        if self.player.menfon == support.fonwei_tuple[0]:
                            return lang.status_agari_renchan
                        return lang.status_agari
                    elif action == lang.action_kyuushukyuuhai_ryukyoku:
                        self.kyuushukyuuhai_ryukyoku()
                        return lang.status_kyuushukyuuhai_ryukyoku
                    elif action == lang.action_riichi:
                        datsu_pai = self.riichi(riichi_pai_pos_list)
                    else:
                        return action_dict[action]() # 加暗槓遞迴

            # 玩家打牌
            if self.player.is_riichi:
                if self.player.riichi_junme == self.player.player_junme: # 剛立直已打過牌
                    pass 
                else:
                    datsu_pai = self.datsuhai(0)
            else:
                datsu_pai = self.datsuhai(GetPlayerDatsuhai().number)
        else:
            # 玩家打牌
            n = GetPlayerDatsuhai().number
            datsu_pai = self.player.tehai.pai_list[n - 1]
            del self.player.tehai.pai_list[n - 1]
            print(f"打出：{datsu_pai}")
            self.player.river.pai_list.append(datsu_pai)
            self.player.datsu_furiten_pais.append(datsu_pai)
            
        # 榮和判斷
        status = self.check_ron(datsu_pai)
        if status is not None:
            return status
        
        # 若剛立直，在這裡放供托
        if self.player.riichi_junme == self.player.player_junme:
            self.gameround.riichiboo += 1
            self.player.tensuu -= 1000

        # 明槓、加槓翻寶牌
        if self.kan_type in (lang.minkan, lang.kakan):
            self.open_dora()

        # 四風連打判定
        if all(p.player_junme == 1 for p in self.gameround.players):
            list_temp = [Pai(s) for s in (support.lang_yakuhai_painame_dict[lang.yakuhai_ton],support.lang_yakuhai_painame_dict[lang.yakuhai_nan],support.lang_yakuhai_painame_dict[lang.yakuhai_shaa],support.lang_yakuhai_painame_dict[lang.yakuhai_pei])]
            first_pai_list = [p.river.pai_list[0] for p in self.gameround.players]
            for p in list_temp:
                if first_pai_list.count(p) == 4:
                    self.suuhonrenda()
                    return lang.status_suuhonrenda

        # 四槓散了
        if len(self.gameround.yama.dora_pointers) >= 5:
            kantsu_num_list = [[f.type for f in p.tehai.furo_list].count(lang.ankan) + [f.type for f in p.tehai.furo_list].count(lang.minkan) + [f.type for f in p.tehai.furo_list].count(lang.kakan) for p in self.gameround.players]
            if (any([n == 4 for n in kantsu_num_list]) and any([n == 1 for n in kantsu_num_list])) or all([n <= 3 for n in kantsu_num_list]):
                self.suukansanra()
                return lang.status_suukansanra
        # 四家立直
        for p in self.gameround.players:
            if not p.is_riichi:
                break
        else:
            self.suuchariichi()
            return lang.status_suuchariichi

        # 同巡振聽
        for i in range(3):
            p = self.gameround.players[(self.player_pos + 1)%4]
            p.doujin_furiten_pais.append(datsu_pai)

        # 鳴牌判斷
        action_dict = {
            lang.action_pon: self.pon, 
            lang.action_minkan: self.minkan, 
            lang.action_chii: self.chii
        }
        # 碰
        is_able_to_pon_players_list: list[Player] = []
        is_able_to_kan_players_list: list[Player] = []
        is_able_to_chii_players_list: list[Player] = []
        for pl in [self.gameround.players[(self.player_pos + 1 + i) % 4] for i in range(3)]:
            if pl.is_riichi:
                continue
            if pl.tehai.is_able_to_pon(datsu_pai):
                is_able_to_pon_players_list.append(pl)
        # 槓
        for pl in [self.gameround.players[(self.player_pos + 1 + i) % 4] for i in range(3)]:
            if pl.is_riichi:
                continue
            if pl.tehai.is_able_to_kan(datsu_pai):
                is_able_to_kan_players_list.append(pl)
        # 吃
        if self.gameround.players[(self.player_pos + 1) % 4].tehai.is_able_to_chii(datsu_pai) and not self.gameround.players[(self.player_pos + 1) % 4].is_riichi:
            is_able_to_chii_players_list.append(self.gameround.players[(self.player_pos + 1) % 4])
        # 鳴牌行為處理
        l = [(pl, lang.action_pon) for pl in is_able_to_pon_players_list] + [(pl, lang.action_minkan) for pl in is_able_to_kan_players_list] + [(pl, lang.action_chii) for pl in is_able_to_chii_players_list]
        # bool_list = GetPlayersMinpaiAction(l).bool_list
        bool_list = [bool(int(input("Player " + str(t[0].ID) + " you can " + t[1] + " >>>"))) for t in l]
        for i in range(len(l)):
            if bool_list[i]: # 優先順位：碰、明槓 > 吃
                return action_dict[l[i][1]](l[i][0])

        # 荒牌流局 or next player round
        if self.gameround.yama.get_available_pai_num() == 0:
            return lang.status_huanpai_ryukyoku
        else:
            return self.next()

####### 通常處理 #######  
    def player_draw(self):
        """摸牌，包含嶺上"""
        pai = self.gameround.yama.draw(self.player) # including adding player_junme
        self.gameround.performer.refresh_tehai(self.player)
        print(f"refresh {self.player.ID} tehai")
        print(self.player.tehai.__str__())
        print(pai)
        return pai

    def open_dora(self):
        self.gameround.yama.dora_pointers.append(self.gameround.yama.pai_list[0])
        del self.gameround.yama.pai_list[0]
        self.gameround.yama.uradora_pointers.append(self.gameround.yama.pai_list[0])
        del self.gameround.yama.pai_list[0]
        print("dora pointers: " + str([p.__str__() for p in self.gameround.yama.dora_pointers]))

    def riichi(self, riichi_pai_pos_list: list[int]) -> Pai:
        """宣告立直，還未放供托，return datsuhai"""
        print("riichi!")
        pai = self.datsuhai(riichi_pai_pos_list[int(GetPlayerInput().input(str(riichi_pai_pos_list)+">>>"))])
        self.player.riichi_furiten_pais.append(pai)

        self.player.is_riichi = True
        self.player.riichi_junme = self.player.player_junme
        return pai
    
    def datsuhai(self, number: int) -> Pai:
        if number == 0:
            pai = self.player.tsumo_pai
            self.player.tsumo_pai = None
            print(f"打出：{pai}")
            self.player.river.pai_list.append(pai)
            return pai
        pai = self.player.tehai.pai_list[number - 1]
        del self.player.tehai.pai_list[number - 1]
        print(f"打出：{pai}")
        self.player.river.pai_list.append(pai)
        self.player.tehai.pai_list.append(self.player.tsumo_pai)
        self.player.tehai.sort()
        self.player.tsumo_pai = None
        self.player.datsu_furiten_pais.append(pai)
        self.player.doujin_furiten_pais.clear()
        return pai

    def check_ron(self, datsu_pai: Pai):
        player_list: list[Player] = []
        agari_result_list_list: list[list[AgariResult]] = []
        for i in range(3):
            pl = self.gameround.players[(self.player_pos + 1 + i) % 4]
            if is_agari(pl.tehai.pai_list + [datsu_pai]) and not self.player.is_furiten():
                param = Param(pl.is_riichi, 
                            pl.riichi_junme, 
                            pl.player_junme, 
                            False, True, False, 
                            self.gameround.yama.get_available_pai_num(), 
                            pl.menfon, 
                            self.gameround.chanfon, 
                            self.is_to_draw_rinshan, 
                            self.gameround.yama.dora_pointers, 
                            self.gameround.yama.uradora_pointers)
                agari_result_list = get_agari_result_list(pl.tehai, datsu_pai, param)
                if agari_result_list:
                    player_list.append(pl)
                    agari_result_list_list.append(agari_result_list)
        # bool_list = GetPlayersRonAction(player_list).bool_list
        bool_list = [bool(int(input(f"player {p.ID} you can ron! >>>"))) for p in player_list]
        ron_players:list[Player] = []
        ron_result_list:list[AgariResult] = []
        for i in range(len(bool_list)):
            if bool_list[i]:
                ron_players.append(player_list[i])
                ron_result_list.append(max(agari_result_list_list[i], key=lambda a: a.tensuu[0]))
        if ron_players:
            if len(ron_players) == 3:
                self.sanchahoo()
                return lang.status_sanchahoo
            self.ron(ron_players, ron_result_list)
            if any(p.menfon == support.fonwei_tuple[0] for p in ron_players):
                return lang.status_agari_renchan
            return lang.status_agari

####### 結束此局 #######  
    def kyuushukyuuhai_ryukyoku(self):
        print("九種九牌")

    def suuhonrenda(self):
        print("四風連打")

    def sanchahoo(self):
        print("三家和")

    def suukansanra(self):
        print("四槓散了")

    def suuchariichi(self):
        print("四家立直")

    def tsumo(self, agari_result_list: list[AgariResult]):
        print("tsumo!")
        agari_result = max(agari_result_list, key=lambda a: a.tensuu[0])
        print(agari_result)
        player_list = self.gameround.players.copy()
        player_list.remove(self.player)
        if self.player.menfon == support.fonwei_tuple[0]:
            self.player.tensuu += 3*agari_result.tensuu[0]
            for player in player_list:
                player.tensuu -= agari_result.tensuu[0]
        else:
            self.player.tensuu += agari_result.tensuu[0] + agari_result.tensuu[1]*2
            for player in player_list:
                if player.menfon == support.fonwei_tuple[0]:
                    player.tensuu -= agari_result.tensuu[0]
                else:
                    player.tensuu -= agari_result.tensuu[1]
        self.player.tensuu += self.gameround.riichiboo * 1000
        self.gameround.riichiboo = 0
        for p in player_list:
            p.tensuu -= self.gameround.benchan*100
            self.player.tensuu += self.gameround.benchan*100

    def ron(self, ron_players: list[Player], agari_result_list: list[AgariResult]):
        # 可能有兩家要和
        sorted_players = sorted(ron_players, key=lambda p: (support.fonwei_tuple.index(p.menfon) - support.fonwei_tuple.index(self.player.menfon))%4)
        list_temp = [p.tensuu for p in ron_players]
        for i in range(len(ron_players)):
            player = ron_players[i]
            agari_result = agari_result_list[i]
            tensuu = agari_result.tensuu[0] + self.gameround.benchan*100
            self.player.tensuu -= tensuu
            player.tensuu += tensuu
        # 供托處理(順位：下、對、上)
        player = sorted_players[0]
        player.tensuu += self.gameround.riichiboo*1000
        self.gameround.riichiboo = 0
        for i in range(len(ron_players)):
            p = ron_players[i]
            print(f"{p.ID}: ron!, {p.tensuu - list_temp[i]}")
            print(agari_result_list[i])

####### 直接遞迴之方法 #######                                                                                                                                                   哈
    def next(self):
        """下個遞迴"""
        next_player_pos = (self.player_pos + 1)%4
        next_player = self.gameround.players[next_player_pos]
        next_player_round = PlayerRoundYonin(self.gameround, next_player, next_player_pos)
        return next_player_round.run()

    def kakan(self):
        # add players' junme
        for p in self.gameround.players:
            p.player_junme += 1
        pai_list_copy = self.player.tehai.pai_list.copy() + [self.player.tsumo_pai]
        available_pais:list[tuple[Pai, Furo, int]] = []
        pos = 0
        for f in self.player.tehai.furo_list:
            if f.type != lang.koutsu:
                continue
            fp = f.pai_tuple[0]
            for p in pai_list_copy:
                if p != fp:
                    continue
                available_pais.append((p, f, pos))
            pos += 1
        else:
            del pos
        for p, f, pos in available_pais:
            if bool(int(input(f"Player {self.player.ID} you can kakan {p.name} >>>"))):
                print("kakan!")
                # 副露處理
                furo = Furo(type=lang.minkan, 
                            pai_tuple=tuple([p] + list(f.pai_tuple)), 
                            minpai_pai=f.minpai_pai, 
                            be_minpai_player_id=f.be_minpai_player_id)
                self.player.tehai.furo_list[pos] = furo
                # print(self.player.tehai.furo_list[0])
                self.player.tsumo_pai = None
                pai_list_copy.remove(p)
                self.player.tehai.pai_list = pai_list_copy
                self.player.tehai.sort()
                # [print(p0) for p0 in self.player.tehai.pai_list]

                # 搶槓處理
                player_list: list[Player] = []
                agari_result_list_list: list[list[AgariResult]] = []
                for i in range(3):
                    pl = self.gameround.players[(self.player_pos + 1 + i) % 4]
                    if is_agari(pl.tehai.pai_list + [p]):
                        param = Param(pl.is_riichi, 
                                    pl.riichi_junme, 
                                    pl.player_junme, 
                                    False, True, True, 
                                    self.gameround.yama.get_available_pai_num(), 
                                    pl.menfon, 
                                    self.gameround.chanfon, 
                                    self.is_to_draw_rinshan, 
                                    self.gameround.yama.dora_pointers, 
                                    self.gameround.yama.uradora_pointers)
                        agari_result_list = get_agari_result_list(pl.tehai, p, param)
                        if agari_result_list:
                            player_list.append(pl)
                            agari_result_list_list.append(agari_result_list)
                # bool_list = GetPlayersRonAction(player_list).bool_list
                bool_list = [bool(int(input(f"player {p.ID} you can ron! >>>"))) for p in player_list]
                ron_players:list[Player] = []
                ron_result_list:list[AgariResult] = []
                for i in range(len(bool_list)):
                    if bool_list[i]:
                        ron_players.append(player_list[i])
                        ron_result_list.append(max(agari_result_list_list[i], key=lambda a: a.tensuu[0]))
                if ron_players:
                    if len(ron_players) == 3:
                        self.sanchahoo()
                        return lang.status_sanchahoo
                    self.ron(ron_players, ron_result_list)
                    if any(p.menfon == support.fonwei_tuple[0] for p in ron_players):
                        return lang.status_agari_renchan
                    return lang.status_agari

                # 遞迴
                next_player_round = PlayerRoundYonin(self.gameround, self.player, self.player_pos, lang.kakan)
                return next_player_round.run()

    def ankan(self):
        # add players' junme
        for p in self.gameround.players:
            p.player_junme += 1
        pai_list_copy = self.player.tehai.pai_list + [self.player.tsumo_pai]
        def loop(pai_list: list[Pai]) -> list[list[Pai]]:
            if len(pai_list) == 0:
                return []
            p = pai_list[0]
            number = pai_list.count(p)
            if number < 4:
                [pai_list.remove(p) for i in range(number)]
                return loop(pai_list)
            else:
                l = []
                for p0 in pai_list.copy():
                    if p0 != p:
                        continue
                    l.append(p0)
                    pai_list.remove(p0)
                return [l] + loop(pai_list)
        available_kan = loop(pai_list_copy.copy())
 
        for kan in available_kan:
            if bool(int(input(f"Player {self.player.ID} you can ankan:" + kan[0].__str__() + " >>>"))):
                p = kan[0]
                print("ankan!")
                # 副露處理
                furo = Furo(type=lang.ankan, 
                            pai_tuple=tuple(kan), 
                            minpai_pai=None, 
                            be_minpai_player_id=None)
                self.player.tehai.furo_list.append(furo)
                self.player.tsumo_pai = None
                pai_list_copy.remove(p)
                pai_list_copy.remove(p)
                pai_list_copy.remove(p)
                pai_list_copy.remove(p)
                self.player.tehai.pai_list = pai_list_copy
                self.player.tehai.sort()

                # 搶槓處理(國士)
                player_list: list[Player] = []
                agari_result_list_list: list[list[AgariResult]] = []
                for i in range(3):
                    pl = self.gameround.players[(self.player_pos + 1 + i) % 4]
                    if is_agari(pl.tehai.pai_list + [p]):
                        param = Param(pl.is_riichi, 
                                      pl.riichi_junme, 
                                      pl.player_junme, 
                                      False, True, True, 
                                      self.gameround.yama.get_available_pai_num(), 
                                      pl.menfon, 
                                      self.gameround.chanfon, 
                                      self.is_to_draw_rinshan, 
                                      self.gameround.yama.dora_pointers, 
                                      self.gameround.yama.uradora_pointers)
                        agari_result_list = get_agari_result_list(pl.tehai, p, param)
                        list_temp: list[AgariResult] = []
                        for agari_result in agari_result_list:
                            if agari_result.tehai_comb.tenpai_type not in (lang.kokushimusoutanmenmachi, lang.kokushimusoujuusanmenmachi):
                                continue
                            list_temp.append(agari_result)
                        if list_temp:
                            player_list.append(pl)
                            agari_result_list_list.append(list_temp)
                # bool_list = GetPlayersRonAction(player_list).bool_list
                bool_list = [bool(int(input(f"player {p.ID} you can ron! >>>"))) for p in player_list]
                ron_players:list[Player] = []
                ron_result_list:list[AgariResult] = []
                for i in range(len(bool_list)):
                    if bool_list[i]:
                        ron_players.append(player_list[i])
                        ron_result_list.append(max(agari_result_list_list[i], key=lambda a: a.tensuu[0]))
                if ron_players:
                    if len(ron_players) == 3:
                        self.sanchahoo()
                        return lang.status_sanchahoo
                    self.ron(ron_players, ron_result_list)
                    if any(p.menfon == support.fonwei_tuple[0] for p in ron_players):
                        return lang.status_agari_renchan
                    return lang.status_agari

                # 遞迴
                next_player_round = PlayerRoundYonin(self.gameround, self.player, self.player_pos, lang.ankan)
                return next_player_round.run()

    def chii(self, chii_player: Player):
        # add players' junme
        for p in self.gameround.players:
            p.player_junme += 1
        pai = self.player.river.pai_list[-1]
        pppai = pai.previous().previous()
        ppai = pai.previous()
        npai = pai.next()
        nnpai = pai.next().next()
        bool1 = pppai in chii_player.tehai.pai_list
        bool2 = ppai in chii_player.tehai.pai_list
        bool3 = npai in chii_player.tehai.pai_list
        bool4 = nnpai in chii_player.tehai.pai_list
        comb: list[tuple[Pai, Pai]] = []
        if bool1 and bool2:
            if pppai.number == 5:
                p0 = Pai("0" + pppai.type)
                if chii_player.tehai.pai_list.count(pppai) > 1:
                    if any(p0.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((p0, ppai))
                    if any(pppai.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((pppai, ppai))
                else:
                    if any(p0.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((p0, ppai))
                    else:
                        comb.append((pppai, ppai))
            elif ppai.number == 5:
                p0 = Pai("0" + ppai.type)
                if chii_player.tehai.pai_list.count(ppai) > 1:
                    if any(p0.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((pppai, p0))
                    if any(ppai.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((pppai, ppai))
                else:
                    if any(p0.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((pppai, p0))
                    else:
                        comb.append((pppai, ppai))
            else:
                comb.append((pppai, ppai))
        if bool2 and bool3:
            if ppai.number == 5:
                p0 = Pai("0" + ppai.type)
                if chii_player.tehai.pai_list.count(ppai) > 1:
                    if any(p0.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((p0, npai))
                    if any(ppai.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((ppai, npai))
                else:
                    if any(p0.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((p0, npai))
                    else:
                        comb.append((ppai, npai))
            elif npai.number == 5:
                p0 = Pai("0" + npai.type)
                if chii_player.tehai.pai_list.count(npai) > 1:
                    if any(p0.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((ppai, p0))
                    if any(npai.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((ppai, npai))
                else:
                    if any(p0.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((ppai, p0))
                    else:
                        comb.append((ppai, npai))
            else:
                comb.append((ppai, npai))
        if bool3 and bool4:
            if npai.number == 5:
                p0 = Pai("0" + npai.type)
                if chii_player.tehai.pai_list.count(ppai) > 1:
                    if any(p0.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((p0, nnpai))
                    if any(npai.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((npai, nnpai))
                else:
                    if any(p0.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((p0, nnpai))
                    else:
                        comb.append((npai, nnpai))
            elif nnpai.number == 5:
                p0 = Pai("0" + nnpai.type)
                if chii_player.tehai.pai_list.count(nnpai) > 1:
                    if any(p0.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((npai, p0))
                    if any(nnpai.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((npai, nnpai))
                else:
                    if any(p0.equal(p) for p in chii_player.tehai.pai_list):
                        comb.append((npai, p0))
                    else:
                        comb.append((npai, nnpai))
            else:
                comb.append((npai, nnpai))
        s = ""
        for i in comb:
            s += "(" + " ".join([p.__str__() for p in i]) + ")"
        choice = int(input(f"Player {chii_player.ID} choose one: {s} >>>"))

        furo = Furo(lang.shuntsu, tuple([pai] + list(comb[choice])), pai, self.player.ID)
        chii_player.tehai.furo_list.append(furo)
        Pai.strict_remove(chii_player.tehai.pai_list, comb[choice][0])
        Pai.strict_remove(chii_player.tehai.pai_list, comb[choice][1])
        del self.player.river.pai_list[-1]
        print("chii!")
        print(chii_player.tehai)

        next_player_round = PlayerRoundYonin(self.gameround, chii_player, support.fonwei_tuple.index(chii_player.menfon), None, True)
        return next_player_round.run()

    def pon(self, pon_player: Player):
        # add players' junme
        for p in self.gameround.players:
            p.player_junme += 1
        pai = self.player.river.pai_list[-1]
        comb: list[tuple[Pai, Pai]] = []
        if pai.number == 5 and pai.type != support.lang_paitype_dict[lang.zuu]:
            p5 = Pai("5"+pai.type)
            p0 = Pai("0"+pai.type)
            p5num = 0
            p0num = 0
            for p in pon_player.tehai.pai_list:
                if p.equal(p5):
                    p5num += 1
                elif p.equal(p0):
                    p0num += 1
            if p5num >= 1 and p0num >= 1:
                comb.append((p0, p5))
            if p5num >= 2:
                comb.append((p5, p5.copy()))
            if p0num >= 2:
                comb.append((p0, p0.copy()))
        else:
            comb.append((pai, pai.copy()))
        s = ""
        for c in comb:
            s += "(" + " ".join([p.__str__() for p in c]) + ")"
        choice = int(input(f"Player {pon_player.ID} choose one: {s} >>>"))

        furo = Furo(lang.koutsu, tuple([pai] + list(comb[choice])), pai, self.player.ID)
        pon_player.tehai.furo_list.append(furo)
        Pai.strict_remove(pon_player.tehai.pai_list, comb[choice][0])
        Pai.strict_remove(pon_player.tehai.pai_list, comb[choice][1])
        del self.player.river.pai_list[-1]
        print("pon!")
        print(pon_player.tehai)
        
        next_player_round = PlayerRoundYonin(self.gameround, pon_player, support.fonwei_tuple.index(pon_player.menfon), None, True)
        return next_player_round.run()

    def minkan(self, minkan_player: Player):
        # add players' junme
        for p in self.gameround.players:
            p.player_junme += 1
        print("kan!")
        pai = self.player.river.pai_list[-1]
        del self.player.river.pai_list[-1]
        l: list[Pai] = [pai]
        for p in minkan_player.tehai.pai_list.copy():
            if p == pai:
                l.append(p)
                minkan_player.tehai.pai_list.remove(p)
        furo = Furo(lang.minkan, tuple(l), pai, self.player.ID)
        minkan_player.tehai.furo_list.append(furo)

        next_player_round = PlayerRoundYonin(self.gameround, minkan_player, support.fonwei_tuple.index(minkan_player.menfon), lang.minkan)
        return next_player_round.run()

    
class PlayerRoundSanin:
    def __init__(self) -> None:
        pass
    def run_sanin(self):
        pass 
    
    def tsumo(self):
        pass 
        
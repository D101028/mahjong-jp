from game import *
import discord
from discord.ext import commands
import asyncio

async def create_process(bot:commands.Bot, ctx:commands.Context):
    process = GameProcess(bot = bot, ctx = ctx)
    await process._init()


class GameProcess():
    def __init__(self, bot:commands.Bot, ctx:commands.Context):
        self.ctx = ctx
        self.bot = bot
        self.is_listening = True
    async def _init(self):
        self.game = Game()
        await self.send_message("rinshan:", self.game.rinshan)
        self.is_finished = False

        is_to_draw = True # 是否摸牌
        is_ankan_out = False # 紀錄上一次是否為暗槓
        count = 0
        while len(self.game.yama) > 14 or (len(self.game.yama)==14 and not is_to_draw):
            if self.is_finished:
                return
            is_other_action = False # 是否有人鳴牌
            is_chi_pon_inner = False 
            is_minkan = False 
            is_kakan = False 
            is_ankan = False
            if self.game.playing == "N": # 自身扮演
                if not is_to_draw:
                    pass 
                else:
                    self.game.draw()
                player = self.game.players["N"]
                # global a
                # if a == "4z": # 超級作弊
                #     player.tehai[-1] = "3z"
                #     a = "3z"
                # elif a == "3z":
                #     player.tehai[-1] = "2z"
                #     a = "2z"
                # elif a == "2z":
                #     player.tehai[-1] = "1z"
                #     a = "1z"
                # elif a == "1z":
                #     player.tehai[-1] = "5z"
                #     a = "5z"
                # if self.game.junme == 1: # 作弊一下
                #     player.tehai = ["5z","4z","1z","1z","1z","2z","2z","2z","3z","3z","3z","4z","4z","4z"]
                #     a = "4z"
                # if self.game.junme == 1:
                #     player.tehai = ["1m","2m","3m","4m","5m","6m","7m","8m","9m","1s","2s","3s","7s","8s"]
                await self.send_message(player.tehai, player.furo)
                if not player.is_riichi:
                    await self.send_message("  1     2     3     4     5     6     7     8     9     10    11    12    13    14")
                
                # 自摸
                is_agari = (self.game.hansuu(player, "tsumo") != 0)
                if is_agari:
                    await self.send_message("you can tsumo!", end="")
                    if "tsumo" in await self.get_input(">>>"):
                        await self.send_message("tsumo nia!!")
                        hansuu, yaku_list, pai_combin, fusuu = self.game.hansuu(player=player, agari_type="tsumo", is_output_fusuu=True)
                        tensuu = self.game.tensuu(hansuu, fusuu, False)
                        await self.send_message(yaku_list)
                        await self.send_message(hansuu, "飜", fusuu, "符")
                        await self.send_message(tensuu)
                        self.is_finished = True
                if self.is_finished:
                    break 

                furo_koutsu = [] # ex.["2m", "1z"]
                for h in player.furo:
                    if mentsu_judge(h)[0] == "koutsu":
                        furo_koutsu.append(h[0][0]+h[0][1])
                
                # 槓
                if is_to_draw: # 吃、碰完不能加槓
                    # 加槓
                    for h in furo_koutsu:
                        if h in player.tehai: # 測試用
                            await self.send_message("you can kakan", h, end=" ")
                            userinput = await self.get_input(">>>")
                            if userinput == "kakan" or userinput == "kan":
                                await self.send_message("kan nia!")
                                self.game.kakan(h)
                                is_kakan = True
                                is_other_action = True
                                await self.chyankan_check(h)
                    # 暗槓
                    ankan_able_pai = []
                    tehai_temp = player.tehai.copy()
                    for h in player.tehai:
                        if tehai_temp.count(h) == 4:
                            ankan_able_pai.append(h)
                            tehai_temp.remove(h)
                            tehai_temp.remove(h)
                            tehai_temp.remove(h)
                            tehai_temp.remove(h)
                    for pai in ankan_able_pai: # 測試用
                        await self.send_message("you can ankan", pai, end=" ")
                        userinput = await self.get_input(">>>")
                        if userinput == "ankan" or userinput == "kan":
                            await self.send_message("kan nia!")
                            self.game.ankan(pai)
                            is_ankan = True 
                            is_other_action = True 
                            await self.kokushi_chyankan_check(pai)

                if player.is_riichi: # 立直摸切
                    time.sleep(3)
                    cutting = self.game.cut(0)
                    player.is_ippatsu_junme = False
                    is_tenpai, tenpais = self.game.check_tenpai(player=player)
                    for tenpai in tenpais: # 振聽確認
                        if tenpai in player.furiten_pai: # 捨牌、立直振聽
                            player.furiten = True
                        else:
                            player.furiten = False
                        if tenpai in player.doujun_furiten_pai: # 同巡振聽
                            player.doujun_furiten = True
                        else:
                            player.doujun_furiten = False
                    if is_tenpai:
                        if player.furiten or player.doujun_furiten:
                            await self.send_message("Tenpai!", str(tenpais), "furiten")
                        else:
                            await self.send_message("Tenpai!", str(tenpais))
                    is_chi_pon_inner, is_minkan = await self.check(cutting)
                    is_other_action = is_chi_pon_inner or is_minkan
                elif not is_kakan and not is_ankan: # 槓完直接進下一迴圈(同理摸嶺上牌)
                    userinput = await self.get_input("切牌>>>")
                    userinput = userinput.split(" ")
                    if "riichi" in userinput: # 立直
                        riichiable, agari_pai = self.game.check_riichi(player = player, cut_num = int(userinput[0])-1)
                        if riichiable:
                            player.is_riichi = True
                            player.riichi_junme = self.game.junme
                            player.is_tenpai = True
                            player.tenpais = agari_pai.copy()
                            player.is_ippatsu_junme = True
                            await self.send_message("riichi nia!!")
                        else:
                            await self.send_message("相公 (指)(怒)")

                    cutting = self.game.cut(int(userinput[0]))
                    is_tenpai, tenpais = self.game.check_tenpai(player=player)
                    for tenpai in tenpais: # 振聽確認
                        if tenpai in player.furiten_pai: # 捨牌、立直振聽
                            player.furiten = True
                        else:
                            player.furiten = False
                        if tenpai in player.doujun_furiten_pai: # 同巡振聽
                            player.doujun_furiten = True
                        else:
                            player.doujun_furiten = False
                    if is_tenpai:
                        if player.furiten or player.doujun_furiten:
                            await self.send_message("Tenpai!", str(tenpais), "furiten")
                        else:
                            await self.send_message("Tenpai!", str(tenpais))

                    is_chi_pon_inner, is_minkan = await self.check(cutting)
                    is_other_action = is_chi_pon_inner or is_minkan

                    if self.game.rinshankaihou_able: # 明槓&加槓翻寶牌指示牌、結束嶺上開花巡
                        if is_ankan_out: # 暗槓不翻
                            pass 
                        else: # 明加槓翻寶牌指示牌
                            self.game.rinshan.append(self.game.yama[0])
                            del self.game.yama[0]
                            await self.send_message("rinshan:",self.game.rinshan)
                        self.game.rinshankaihou_able = False


            else: # 電腦出牌(自動摸切)
                if not is_to_draw:
                    pass 
                else:
                    self.game.draw()
                cutting = self.game.cut(0)
                await self.send_message(self.game.playing, ":", cutting)
                is_chi_pon_inner, is_minkan = await self.check(cutting)
                is_other_action = is_chi_pon_inner or is_minkan

            if is_other_action: # 有人鳴牌
                count = MENFON_INDEX.index(self.game.playing)
            else:
                self.game.playing = MENFON_INDEX[(count+1)%4]
                count += 1
            
            if is_chi_pon_inner: # 下一位不摸牌
                is_to_draw = False
            else:
                is_to_draw = True
            
            if is_ankan:
                is_ankan_out = True
            else:
                is_ankan_out = False

        # 流局滿貫 # 不計寶牌
        if not self.is_finished:
            for m in MENFON_INDEX: # 荒牌流局
                await self.send_message(m + ": ")
                if self.game.players[m].is_tenpai:
                    await self.send_message("Tenpai:", player.tenpais)
                else:
                    await self.send_message("No ten")
    
    async def send_message(self, *values, end = None):
        string = "```\n"
        for value in values:
            string += str(value) + " "
        string += "\n```"
        await self.ctx.send(string)

    async def get_input(self, *values):
        msg = await self.bot.wait_for("message")
        content = msg.content
        if content[:3] == "```":
            content = await self.get_input()
        return content

    async def kokushi_chyankan_check(self, kan_pai:str):
        """國士無雙搶暗槓"""
        _list = ["1m","9m","1p","9p","1s","9s","1z","2z","3z","4z","5z","6z","7z"]
        if kan_pai in _list:
            playing_player = self.game.players[self.game.playing]
            for menfon, player in self.game.players.items():
                if menfon == playing_player.menfon:
                    continue 
                tehai = player.tehai.copy()
                if len(tehai) == 13: # 無副露
                    list0 = _list.copy()
                    list0.remove(kan_pai)
                    for i in list0: # 擁有除kan_pai之外所有么九牌
                        if not i in tehai:
                            return 
                    for i in tehai: # 手牌都是么九牌
                        if not i in _list:
                            return 
                    # 國士搶槓成功
                    if player.menfon == "N": # 測試用
                        await self.send_message("you can ron !")
                        userinput = await self.get_input(">>>")
                        if userinput == "ron":
                            await self.send_message("ron nia!")
                            hansuu, yaku_list, pai_combin, fusuu = self.game.hansuu(player, "ron", kan_pai, is_output_yaku=True, is_chyankan=True,is_output_fusuu=True)
                            tensuu = self.game.tensuu(hansuu, fusuu, False)
                            await self.send_message(yaku_list)
                            await self.send_message(hansuu, "飜", fusuu, "符")
                            await self.send_message(tensuu)
                            self.is_finished = True
                        else:
                            if player.is_riichi: # 立直振聽
                                player.furiten_pai.append(kan_pai)
                                player.furiten = True
        return 

    async def chyankan_check(self, kan_pai:str): # 未 debug
        """搶明、加槓"""
        playing_player = self.game.players[self.game.playing]
        for menfon, player in self.game.players.items():
            if menfon == playing_player.menfon:
                continue 
            tehai = player.tehai.copy()
            for i in player.furo:
                for j in i:
                    tehai.append(j[0]+j[1])
            tehai.append(kan_pai)
            if self.game.is_agari(tehai):
                if player.menfon == "N": # 測試用
                    await self.send_message("you can ron !")
                    userinput = await self.get_input(">>>")
                    if userinput == "ron":
                        await self.send_message("ron nia!")
                        hansuu, yaku_list, pai_combin, fusuu = self.game.hansuu(player, "ron", kan_pai, is_output_yaku=True, is_chyankan=True, is_output_fusuu=True)
                        tensuu = self.game.tensuu(hansuu, fusuu, False)
                        await self.send_message(yaku_list)
                        await self.send_message(hansuu, "飜", fusuu, "符")
                        await self.send_message(tensuu)
                        self.is_finished = True
                    else:
                        if player.is_riichi: # 立直振聽
                            player.furiten_pai.append(kan_pai)
                            player.furiten = True

    async def check(self, c:str) -> bool:
        is_chi_pon = False
        is_minkan = False
        playing_player = self.game.players[self.game.playing]
        # 榮和
        players = await self.ron_able(c)
        if len(players) != 0:
            for player in players:
                if player.menfon == "N": # 測試用
                    await self.send_message("you can ron !")
                    userinput = await self.get_input(">>>")
                    if userinput == "ron":
                        await self.send_message("ron nia!")
                        hansuu, yaku_list, pai_combin, fusuu = self.game.hansuu(player, "ron", c, is_output_fusuu=True)
                        tensuu = self.game.tensuu(hansuu, fusuu, False)
                        await self.send_message(yaku_list)
                        await self.send_message(hansuu, "飜", fusuu, "符")
                        await self.send_message(tensuu)
                        self.is_finished = True
                    else:
                        if player.is_riichi: # 立直振聽
                            player.furiten_pai.append(c)
                            player.furiten = True

        # 同巡振聽
        for p in MENFON_INDEX:
            if p == self.game.playing:
                continue
            player = self.game.players[p]
            tehai = player.tehai.copy()
            tehai.append(c)
            if self.game.is_agari(tehai):
                player.doujun_furiten_pai = self.game.check_tenpai(player = player, overright=False)[1]
                player.doujun_furiten = True

        # 碰
        players = await self.pon_able(c)
        if len(players) != 0:
            for player in players:
                if player.is_riichi:
                    continue
                if player.menfon == "N": # 測試用
                    await self.send_message("you can pon")
                    userinput = await self.get_input(">>>")
                    if userinput == "pon":
                        self.game.pon(pon_player = player, pon_ed_player = playing_player)
                        await self.send_message("pon nia!")
                        is_chi_pon = True
        
        # 明槓
        players = await self.kan_able(c)
        if len(players) != 0:
            for player in players:
                if player.is_riichi:
                    continue
                if player.menfon == "N": # 測試用
                    await self.send_message("you can kan")
                    userinput = await self.get_input(">>>")
                    if userinput == "kan":
                        self.game.minkan(kan_player = player, kan_ed_player = playing_player)
                        await self.send_message("kan nia!")
                        await self.chyankan_check(c)
                        is_minkan = True
        
        # 吃
        players = await self.chi_able(c)
        if len(players) != 0:
            next_player = self.game.players[p_next(self.game.playing)]
            if next_player in players:
                if next_player.menfon == "N": # 測試用
                    await self.send_message("you can chi")
                    userinput = await self.get_input(">>>")
                    if userinput == "chi":
                        chi_ed_player = playing_player
                        chi_player = next_player

                        chi_pai = chi_ed_player.river[-1]
                        could_furo = []
                        minus1 = card_minus(chi_pai)
                        minus2 = card_minus(minus1)
                        plus1 = card_plus(chi_pai)
                        plus2 = card_plus(plus1)
                        if plus1 in chi_player.tehai and plus2 in chi_player.tehai:
                            could_furo.append([chi_pai, plus1, plus2])
                        if minus1 in chi_player.tehai and plus1 in chi_player.tehai:
                            could_furo.append([minus1, chi_pai, plus1])
                        if minus2 in chi_player.tehai and minus1 in chi_player.tehai:
                            could_furo.append([minus2, minus1, chi_pai])
                        chi_num = 0
                        if chi_player.menfon == "N": # 測試用
                            if len(could_furo) > 1:
                                count = 0
                                for i in could_furo:
                                    count += 1
                                    await self.send_message(count, ":", i)
                                userinput = int(await self.get_input(">>>"))
                                chi_num = userinput - 1

                        self.game.chi(chi_player = next_player, chi_ed_player = playing_player, could_furo = could_furo, chi_num = chi_num)
                        await self.send_message("chi nia!")
                        is_chi_pon = True
        
        return is_chi_pon, is_minkan
    
    async def ron_able(self, c:str) -> list[Player]:
        players = []
        for p in MENFON_INDEX:
            if p == self.game.playing:
                continue
            player = self.game.players[p]
            if player.furiten or player.doujun_furiten: # 振聽
                continue
            if self.game.hansuu(player = player, agari_type = "ron", ron_hai = c) != 0:
                players.append(player)
        return players
    
    async def pon_able(self, c:str) -> list[Player]:
        players = []
        for p in MENFON_INDEX:
            player = self.game.players[p]
            if p == self.game.playing or player.is_riichi:
                continue
            if player.tehai.count(c) >= 2:
                players.append(player)
        return players
    
    async def kan_able(self, c:str) -> list[Player]:
        # 明槓
        players = []
        for p in MENFON_INDEX:
            player = self.game.players[p]
            if p == self.game.playing or player.is_riichi:
                continue
            if player.tehai.count(c) >= 3:
                players.append(player)
        return players
    
    async def chi_able(self, c:str) -> list[Player]:
        players = []
        if c[1] == "z":
            return []
        for p in MENFON_INDEX:
            player = self.game.players[p]
            if p == self.game.playing or player.is_riichi:
                continue
            tehai = player.tehai.copy()
            # 赤寶處理
            count = 0
            for h in tehai:
                if h == "0m":
                    tehai[count] = "5m"
                elif h == "0p":
                    tehai[count] = "5p"
                elif h == "0s":
                    tehai[count] = "5s"
                count += 1
            
            num = int(c[0])
            s = c[1]
            boolean1 = f"{num+1}{s}" in tehai and f"{num+2}{s}" in tehai
            boolean2 = f"{num-1}{s}" in tehai and f"{num+1}{s}" in tehai 
            boolean3 = f"{num-2}{s}" in tehai and f"{num+-1}{s}" in tehai 
            if boolean1 or boolean2 or boolean3:
                players.append(player)
        return players


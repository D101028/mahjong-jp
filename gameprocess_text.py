from gamecore import *
import discord
from discord.ext import commands
import asyncio
from ext.support import get_emoji, INDEX

async def create_process(bot:commands.Bot, ctx:commands.Context):
    process = GameProcess(bot = bot, ctx = ctx)
    await process._init()

a="4z"
class GameProcess():
    def __init__(self, bot:commands.Bot, ctx:commands.Context):
        self.ctx = ctx
        self.bot = bot
        self.is_listening = True
        self.emoji_list = ctx.guild.emojis
        self.text_emoji_dict = {}
        # 字牌表符確認
        for e in self.emoji_list:
            if e.name in INDEX[3]:
                self.text_emoji_dict[e.name] = e
        # 數牌表符確認
        for e in self.emoji_list:
            if e.name in INDEX[4]:
                self.text_emoji_dict[e.name] = e

    async def _init(self):
        self.river_message = await self.ctx.send("River Message")
        self.tehai_message = await self.ctx.send("Tehai Message")
        self.tempai_message_text = ""

        self.game = Game()

        # 測試用作弊
        # self.game.players["N"].tehai = ["3m","4m","4m","5m","5m","6m","6m","7m","1z","1z","1z","2z","2z"]
        
        await self.refresh_tehai()
        await self.refresh_river()
        # await self.send_message()

        self.is_finished = False

        is_to_draw = True # 是否摸牌
        is_ankan_out = False # 紀錄上一次是否為暗槓
        count = 0
        while len(self.game.yama) > 14 or (len(self.game.yama)==14 and not is_to_draw):
            if self.is_finished:
                return
            # await self.refresh_tehai()
            await self.refresh_river()
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
                # if self.game.junme == 3:
                    # player.tehai = ["0m","5m","5m","1s","2s","3s","4s","5s","6s","7s","8s","9s","1z","5m"]
                    # player.tehai[-1] = "0m"
                await self.refresh_tehai()
                # await self.send_message(player.tehai, player.furo)
                # if not player.is_riichi:
                #     await self.send_message("  1     2     3     4     5     6     7     8     9     10    11    12    13    14")
                
                # 自摸
                is_agari = (self.game.hansuu(player, "tsumo") != 0) and is_to_draw
                if is_agari:
                    await self.send_message("you can tsumo!", end="")
                    if "tsumo" in await self.get_input(">>>"):
                        await self.send_message("tsumo nia!!")
                        if player.is_riichi:
                            await self.send_message(await self.pai_list_emoji_tran(self.game.uradora_pointer), is_code_mode=False)
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
                        h = akadorasuu_tran(h)[0]
                        furo_koutsu.append(h[0][0]+h[0][1])
                
                # 槓
                if is_to_draw: # 吃、碰完不能加槓
                    # 加槓
                    tehai_no_aka = akadorasuu_tran(player.tehai.copy())[0]
                    for h in furo_koutsu:
                        if h in tehai_no_aka: # 測試用
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
                    tehai_temp = akadorasuu_tran(player.tehai.copy())[0]
                    for h in tehai_no_aka:
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
                    await self.refresh_tehai()
                    await self.refresh_river()
                    player.is_ippatsu_junme = False
                    is_tenpai, tenpais = self.game.check_tenpai(player=player)
                    # 振聽確認
                    player.furiten = False
                    player.doujun_furiten = False
                    for tenpai in tenpais: 
                        if tenpai in player.furiten_pai: # 捨牌、立直振聽
                            player.furiten = True
                            break
                    for tenpai in tenpais:
                        if tenpai in player.doujun_furiten_pai: # 同巡振聽
                            player.doujun_furiten = True
                            break
                    msg = ""
                    if is_tenpai:
                        if player.furiten or player.doujun_furiten:
                            msg = "Tenpai!"+" "+str(tenpais)+" "+"furiten"
                        else:
                            msg = "Tenpai!"+" "+str(tenpais)
                    if self.tempai_message_text != msg:
                        self.tempai_message_text = msg
                        await self.refresh_tehai()

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
                    await self.refresh_tehai()
                    await self.refresh_river()
                    is_tenpai, tenpais = self.game.check_tenpai(player=player)
                    # 振聽確認
                    player.furiten = False
                    player.doujun_furiten = False
                    for tenpai in tenpais: 
                        if tenpai in player.furiten_pai: # 捨牌、立直振聽
                            player.furiten = True
                            break
                    for tenpai in tenpais:
                        if tenpai in player.doujun_furiten_pai: # 同巡振聽
                            player.doujun_furiten = True
                            break
                    msg = ""
                    if is_tenpai:
                        if player.furiten or player.doujun_furiten:
                            msg = "Tenpai!"+" "+str(tenpais)+" "+"furiten"
                        else:
                            msg = "Tenpai!"+" "+str(tenpais)
                    if self.tempai_message_text != msg:
                        self.tempai_message_text = msg
                        await self.refresh_tehai()

                    is_chi_pon_inner, is_minkan = await self.check(cutting)
                    is_other_action = is_chi_pon_inner or is_minkan

                    if self.game.rinshankaihou_able: # 明槓&加槓翻寶牌指示牌、結束嶺上開花巡
                        if is_ankan_out: # 暗槓不翻
                            pass 
                        else: # 明加槓翻寶牌指示牌
                            self.game.rinshan.append(self.game.yama[0])
                            del self.game.yama[0]
                            # await self.send_message("rinshan:",self.game.rinshan)
                        self.game.rinshankaihou_able = False
                # print(player.is_menchin(), player.tehai, player.furo)

            else: # 電腦出牌(自動摸切)
                if not is_to_draw:
                    pass 
                else:
                    self.game.draw()

                # 測試用作弊
                # if self.game.playing == "W" and self.game.junme == 1:
                #     player = self.game.players[self.game.playing]
                #     player.tehai[-1] = "0m"
                # elif self.game.playing == "E" and self.game.junme == 3:
                #     player = self.game.players[self.game.playing]
                #     player.tehai[-1] = "2z"

                cutting = self.game.cut(0)
                # await self.refresh_tehai()
                await self.refresh_river()
                # await self.send_message(self.game.playing, ":", cutting)
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
    
    async def send_message(self, *values, end = None, is_code_mode:bool = True) -> discord.Message:
        string = "```\n" if is_code_mode else ""
        for value in values:
            string += str(value) + " "
        string += "\n```" if is_code_mode else ""
        msg = await self.ctx.send(string)
        return msg

    async def get_input(self, *values, is_delete_message = True):
        msg = await self.bot.wait_for("message")
        content = msg.content
        if content[:3] == "```":
            content = await self.get_input()
        if is_delete_message:
            await msg.delete()
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
                                player.furiten_pai.append(akadora_str_tran(kan_pai))
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
                            player.furiten_pai.append(akadora_str_tran(kan_pai))
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
                        if player.is_riichi:
                            await self.send_message(await self.pai_list_emoji_tran(self.game.uradora_pointer), is_code_mode = False)
                        hansuu, yaku_list, pai_combin, fusuu = self.game.hansuu(player, "ron", c, is_output_fusuu=True)
                        tensuu = self.game.tensuu(hansuu, fusuu, False)
                        await self.send_message(yaku_list)
                        await self.send_message(hansuu, "飜", fusuu, "符")
                        await self.send_message(tensuu)
                        self.is_finished = True
                        return is_chi_pon, is_minkan
                    else:
                        if player.is_riichi: # 立直振聽
                            player.furiten_pai.append(akadora_str_tran(c))
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
                    msg = await self.send_message("you can pon")
                    userinput = await self.get_input(">>>")
                    await msg.delete()
                    if userinput == "pon":
                        pon_player = player 
                        pon_ed_player = playing_player
                        pon_pai = pon_ed_player.river[-1]

                        is_able_choose_akadora = False
                        if pon_pai in ("5m","5p","5s"):
                            if "0" + pon_pai[-1] in pon_player.tehai and player.tehai.count("5"+pon_pai[-1])>=2:
                                is_able_choose_akadora = True
                        
                        if is_able_choose_akadora:
                            pai_type = pon_pai[-1]
                            msg01 = await self.send_message(f"1. ['5{pai_type}', '5{pai_type}', '5{pai_type}']\n2. ['0{pai_type}', '5{pai_type}', '5{pai_type}']")
                            num = await self.get_input()
                            await msg01.delete()
                            if num == "2": # 含赤寶
                                self.game.pon(pon_player = pon_player, pon_ed_player = pon_ed_player, is_contain_akadora=True)
                            else:
                                self.game.pon(pon_player = pon_player, pon_ed_player = pon_ed_player)
                        else:
                            self.game.pon(pon_player = pon_player, pon_ed_player = pon_ed_player)
                        await self.send_message("pon nia!")
                        is_chi_pon = True
        
        # 明槓
        players = await self.kan_able(c)
        if len(players) != 0:
            for player in players:
                if player.is_riichi:
                    continue
                if player.menfon == "N": # 測試用
                    msg = await self.send_message("you can kan")
                    userinput = await self.get_input(">>>")
                    await msg.delete()
                    if userinput == "kan":
                        self.game.minkan(kan_player = player, kan_ed_player = playing_player)
                        await self.send_message("kan nia!")
                        is_minkan = True
        
        # 吃
        players = await self.chi_able(c)
        if len(players) != 0:
            next_player = self.game.players[p_next(self.game.playing)]
            if next_player in players:
                if next_player.menfon == "N": # 測試用
                    msg = await self.send_message("you can chi")
                    userinput = await self.get_input(">>>")
                    await msg.delete()
                    if userinput == "chi":
                        chi_ed_player = playing_player
                        chi_player = next_player

                        akadora_nashi_tehai = akadorasuu_tran(chi_player.tehai.copy())[0]
                        chi_pai = chi_ed_player.river[-1]
                        could_furo = []
                        minus1 = card_minus(chi_pai)
                        minus2 = card_minus(minus1)
                        plus1 = card_plus(chi_pai)
                        plus2 = card_plus(plus1)
                        if plus1 in akadora_nashi_tehai and plus2 in akadora_nashi_tehai:
                            if plus1 in ("5m","5p","5s"):
                                if "0"+plus1[1] in chi_player.tehai: # 手上有可組合紅寶
                                    if plus1 in chi_player.tehai: # 手上也有非紅寶
                                        could_furo.append([chi_pai, plus1, plus2])
                                        could_furo.append([chi_pai, "0"+plus1[1], plus2])
                                    else: # 手上沒有非紅寶
                                        could_furo.append([chi_pai, "0"+plus1[1], plus2])
                                else: # 手上沒有可組合紅寶
                                    could_furo.append([chi_pai, plus1, plus2])
                            elif plus2 in ("5m","5p","5s"):
                                if "0"+plus2[1] in chi_player.tehai:
                                    if plus2 in chi_player.tehai:
                                        could_furo.append([chi_pai, plus1, plus2])
                                        could_furo.append([chi_pai, plus1, "0"+plus2[1]])
                                    else:
                                        could_furo.append([chi_pai, plus1, "0"+plus2[1]])
                                else:
                                    could_furo.append([chi_pai, plus1, plus2])
                            else:
                                could_furo.append([chi_pai, plus1, plus2])

                        if minus1 in akadora_nashi_tehai and plus1 in akadora_nashi_tehai:
                            if minus1 in ("5m","5p","5s"):
                                if "0"+minus1[1] in chi_player.tehai: # 手上有可組合紅寶
                                    if minus1 in chi_player.tehai: # 手上也有非紅寶
                                        could_furo.append([minus1, chi_pai, plus1])
                                        could_furo.append(["0"+minus1[1], chi_pai, plus1])
                                    else: # 手上沒有非紅寶
                                        could_furo.append(["0"+minus1[1], chi_pai, plus1])
                                else: # 手上沒有可組合紅寶
                                    could_furo.append([minus1, chi_pai, plus1])
                            elif plus1 in ("5m","5p","5s"):
                                if "0"+plus1[1] in chi_player.tehai: # 手上有可組合紅寶
                                    if plus1 in chi_player.tehai: # 手上也有非紅寶
                                        could_furo.append([minus1, chi_pai, plus1])
                                        could_furo.append([minus1, chi_pai, "0"+plus1[1]])
                                    else: # 手上沒有非紅寶
                                        could_furo.append([minus1, chi_pai, "0"+plus1[1]])
                                else: # 手上沒有可組合紅寶
                                    could_furo.append([minus1, chi_pai, plus1])
                            else:
                                could_furo.append([minus1, chi_pai, plus1])
                        
                        if minus2 in akadora_nashi_tehai and minus1 in akadora_nashi_tehai:
                            if minus2 in ("5m","5p","5s"):
                                if "0"+minus2[1] in chi_player.tehai: # 手上有可組合紅寶
                                    if minus2 in chi_player.tehai: # 手上也有非紅寶
                                        could_furo.append([minus2, minus1, chi_pai])
                                        could_furo.append(["0"+minus2[1], minus1, chi_pai])
                                    else: # 手上沒有非紅寶
                                        could_furo.append(["0"+minus2[1], minus1, chi_pai])
                                else: # 手上沒有可組合紅寶
                                    could_furo.append([minus2, minus1, chi_pai])
                            elif minus1 in ("5m","5p","5s"):
                                if "0"+minus1[1] in chi_player.tehai: # 手上有可組合紅寶
                                    if minus1 in chi_player.tehai: # 手上也有非紅寶
                                        could_furo.append([minus2, minus1, chi_pai])
                                        could_furo.append([minus2, "0"+minus1[1], chi_pai])
                                    else: # 手上沒有非紅寶
                                        could_furo.append([minus2, "0"+minus1[1], chi_pai])
                                else: # 手上沒有可組合紅寶
                                    could_furo.append([minus2, minus1, chi_pai])
                            else:
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
        if c[0] == "0":
            c = "5" + c[-1]
        players = []
        for p in MENFON_INDEX:
            player = self.game.players[p]
            if p == self.game.playing or player.is_riichi:
                continue
            tehai = akadorasuu_tran(player.tehai.copy())[0]
            if tehai.count(c) >= 2:
                players.append(player)
        return players
    
    async def kan_able(self, c:str) -> list[Player]:
        # 明槓
        if c[0] == "0":
            c = "5" + c[-1]
        players = []
        for p in MENFON_INDEX:
            player = self.game.players[p]
            if p == self.game.playing or player.is_riichi:
                continue
            tehai = akadorasuu_tran(player.tehai.copy())[0]
            if tehai.count(c) >= 3:
                players.append(player)
        return players
    
    async def chi_able(self, c:str) -> list[Player]:
        if c[0] == "0":
            c = "5" + c[-1]
        players = []
        if c[1] == "z":
            return []
        for p in MENFON_INDEX:
            player = self.game.players[p]
            if p == self.game.playing or player.is_riichi:
                continue
            tehai = akadorasuu_tran(player.tehai.copy())[0]
            
            num = int(c[0])
            s = c[1]
            boolean1 = f"{num+1}{s}" in tehai and f"{num+2}{s}" in tehai
            boolean2 = f"{num-1}{s}" in tehai and f"{num+1}{s}" in tehai 
            boolean3 = f"{num-2}{s}" in tehai and f"{num+-1}{s}" in tehai 
            if boolean1 or boolean2 or boolean3:
                players.append(player)
        return players

    async def refresh_river(self):
        playing_msg = {
            "E":"", "S":"", "W":"", "N":""
        }
        playing_msg[self.game.playing] = " \**"
        river_msg = "------------------------\n"
        # river_msg = "```"
        river_msg += "寶牌指示：" + await self.pai_list_emoji_tran(self.game.rinshan) + "\n\n"
        river_msg += "東" + playing_msg["E"] + "\n" + await self.river_tran(self.game.players["E"].river)
        river_msg += "南" + playing_msg["S"] + "\n" + await self.river_tran(self.game.players["S"].river)
        river_msg += "西" + playing_msg["W"] + "\n" + await self.river_tran(self.game.players["W"].river)
        river_msg += "北" + playing_msg["N"] + "\n" + await self.river_tran(self.game.players["N"].river)

        river_msg += "\n------------------------"
        await self.river_message.edit(content=river_msg)

    async def refresh_tehai(self):
        player = self.game.players["N"]
        tehai_message = ""
        tehai_message += await self.tehai_tran(player=player) + "```1  2  3  4  5  6  7  8  9  10 11 12 13 14```"
        tehai_message += "\n" + self.tempai_message_text
        await self.tehai_message.edit(content=tehai_message)

    # async def show_river(self):
    #     rinshan_message = "rinshan:" + " " + str(self.game.rinshan)
    #     river_msg = "```{}```".format(rinshan_message+"\n\n東\n\n\n\n\n南\n\n\n\n\n西\n\n\n\n\n北\n\n\n\n.")
    #     await self.river_message.edit(content = river_msg)

    async def river_tran(self, river_list:list[str], is_emoji:bool = True) -> str:
        count = 0
        line_num = 1
        string = ""
        for t in river_list:
            count += 1
            if is_emoji:
                emoji = self.text_emoji_dict[t]
                string += f"{emoji} "
            else:
                string += t + " "
            if count == 6:
                string += "\n"
                line_num += 1
                count = 0
        string += " \n"*(5-line_num)
        return string

    async def tehai_tran(self, player:Player, is_emoji:bool = True) -> str:
        tehai = player.tehai.copy()
        furo = player.furo.copy()
        string = ""
        for t in tehai:
            if is_emoji:
                emoji = self.text_emoji_dict[t]
                string += f"{emoji} "
        string += "\n"
        for t in furo:
            m_type, pos =  mentsu_judge(t)
            if m_type == "ankan": # 暗槓
                for count in range(4):
                    emoji = self.text_emoji_dict[t[count%3]]
                    string += f"{emoji}"
                string += "."
            elif m_type == "kakan":
                for count in range(3):
                    emoji = self.text_emoji_dict[t[count][0] + t[count][1]]
                    string += f"{emoji}"
                    if count == pos:
                        string += "\***"
                string += "."
            elif m_type == "minkan":
                for count in range(3):
                    emoji = self.text_emoji_dict[t[count][0] + t[count][1]]
                    string += f"{emoji}"
                    if count == pos:
                        string += "\**"
                string += "."
            elif m_type == "koutsu":
                for count in range(3):
                    emoji = self.text_emoji_dict[t[count][0] + t[count][1]]
                    string += f"{emoji}"
                    if count == pos:
                        string += "\*"
                string += "."
            else:
                for count in range(3):
                    emoji = self.text_emoji_dict[t[count][0] + t[count][1]]
                    string += f"{emoji}"
                    if count == pos:
                        string += "\*"
                string += "."
        return string 

    async def pai_list_emoji_tran(self, pai_list:list[str]) -> str:
        string = ""
        for p in pai_list:
            emoji = self.text_emoji_dict[p]
            string += f"{emoji} "
        return string 


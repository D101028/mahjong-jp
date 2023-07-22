import time
import random
from code_index import INDEX
index = INDEX[2].copy()
MENFON_INDEX = ["E","S","W","N"]
import support 
import tc
s = tc
# def shuffle():
#     # 洗牌
#     return 
yama = index.copy()
random.shuffle(yama)

def deal(player = 4, yama = yama):
    # 發牌
    output = []
    for i in range(player):
        output.append(yama[0:13])
        del yama[0:13]
    output.append(yama)
    return output

def sort(userinput: list, index = ["m","p","s","z"]):
    # 理牌
    clubs = [[],[],[],[]]
    for i in userinput:
        if i[1] == "m":
            clubs[0].append(i)
        elif i[1] == "p":
            clubs[1].append(i)
        elif i[1] == "s":
            clubs[2].append(i)
        elif i[1] == "z":
            clubs[3].append(i)
    for i in clubs:
        i.sort()
    return clubs[0] + clubs[1] + clubs[2] + clubs[3]

def card_plus(userinput:str, z_contained = False, mod = False):
    contained = "mpsz" if z_contained else "mps"
    if not userinput[1] in contained:
        return
    if userinput[0] == "0":
        userinput = "5" + userinput[1:]
    if mod:
        if userinput[1] == "z":
            output = str(((int(userinput[0])+1)-1) % 7 + 1) + userinput[1:]
        else:
            output = str(((int(userinput[0])+1)-1) % 9 + 1) + userinput[1:]
    else:
        output = str((int(userinput[0])+1)) + userinput[1:]
    return output

def p_next(p:str):
    return MENFON_INDEX[(MENFON_INDEX.index(p) + 1) % 4]

def akadorasuu_tran(tehai:list)->tuple[list,int]:
    tehai = tehai.copy()
    count = 0
    dora = 0
    for h in tehai:
        if "0m" in h:
            tehai[count] = "5"+h[1:]
            dora += 1
        elif "0p" in h:
            tehai[count] = "5"+h[1:]
            dora += 1
        elif "0s" in h:
            tehai[count] = "5"+h[1:]
            dora += 1
        count += 1
    return tehai, dora
    

class Player():
    def __init__(self, menfon:str, tehai:list, ):
        """menfon: 風\ntehai: 手牌 -> ["1m", "2m", ...]"""
        self.menfon = menfon
        self.river = []
        self.tehai = self.sort(tehai)
        self.furo = [] # [["1m*", "2m", "3m"], ["1z", "1z", "1z*"]]
            # chi: [1m*, 2m, 3m] (上 對 下)
            # pon: [1m, 1m, 1m*]
            # minkan: [1z, 1z**, 1z]
            # ankan: [1z, 1z, 1z]
            # kakan: [1z, 1z***, 1z]
        self.is_tenpai = False
        self.tenpais = []
        self.is_riichi = False 
        self.riichi_junme = None
        self.is_ippatsu_junme = False
        self.furiten_pai = []
        self.furiten = False
    
    def sort(self, userinput: list, index = ["m","p","s","z"]):
        # 理牌
        clubs = [[],[],[],[]]
        for i in userinput:
            if i[1] == index[0]:
                clubs[0].append(i)
            elif i[1] == index[1]:
                clubs[1].append(i)
            elif i[1] == index[2]:
                clubs[2].append(i)
            elif i[1] == index[3]:
                clubs[3].append(i)
        for i in clubs:
            i.sort()
        return clubs[0] + clubs[1] + clubs[2] + clubs[3]


class Game():
    def __init__(self):
        yama = [] + INDEX[2]
        random.shuffle(yama)
        self.yama = yama # 牌山序列
        self.playing = "E" # 打出玩家
        d = self.deal()
        self.players_status = {
            # [河面, 手牌, 副露]
            # chi: [1m*, 2m, 3m] (上 對 下)
            # pon: [1m, 1m, 1m*]
            # minkan: [1z, 1z**, 1z]
            # ankan: [1z, 1z, 1z]
            # kakan: [1z, 1z***, 1z]

            "E": [[], self.sort(d[0]), []],
            "S": [[], self.sort(d[1]), []],
            "W": [[], self.sort(d[2]), []],
            "N": [[], self.sort(d[3]), []],
        }
        self.players = {
            "E": Player(menfon = "E", tehai = self.sort(d[1])),
            "S": Player(menfon = "S", tehai = self.sort(d[1])),
            "W": Player(menfon = "W", tehai = self.sort(d[1])),
            "N": Player(menfon = "N", tehai = self.sort(d[1])),
        }
        self.chanfon = "E"
        self.junme = 0 # 巡數
        self.rinshan = [self.yama[0]]
        del self.yama[0]

        # self.draw()

    def deal(self, player = 4):
        # 發牌
        """-> [player1, player2, player3, player4]"""
        output = []
        for i in range(player):
            output.append(self.yama[0:13])
            del self.yama[0:13]
        return output
    def sort(self, userinput: list, index = ["m","p","s","z"]):
        # 理牌
        clubs = [[],[],[],[]]
        for i in userinput:
            if i[1] == index[0]:
                clubs[0].append(i)
            elif i[1] == index[1]:
                clubs[1].append(i)
            elif i[1] == index[2]:
                clubs[2].append(i)
            elif i[1] == index[3]:
                clubs[3].append(i)
        for i in clubs:
            i.sort()
        return clubs[0] + clubs[1] + clubs[2] + clubs[3]
    def draw(self):
        # 摸牌
        drawed = self.yama[0]
        del self.yama[0]
        self.players[self.playing].tehai.append(drawed)
        if self.playing == "E":
            self.junme += 1
    def cut(self, num = 0) -> str:
        # 切牌
        """output cutting"""
        player = self.players[self.playing]
        num = int(num)
        cutting = ""
        cutting = player.tehai[num-1]
        del player.tehai[num-1]
        player.tehai = self.sort(player.tehai)
        player.river.append(cutting)
        player.furiten_pai.append(cutting)
        return cutting


    def chi(self):
        # 吃牌處理
        for m, p in self.players.items():
            if m != self.playing and p.is_ippatsu_junme:
                p.is_ippatsu_junme = False
        self.junme += 1
        return 
    def pon(self, pon_player:Player, pon_ed_player:Player):
        # 碰牌處理
        for m, p in self.players.items():
            if m != self.playing and p.is_ippatsu_junme:
                p.is_ippatsu_junme = False
        self.junme += 1
        self.playing = pon_player.menfon

        pon_pai = pon_ed_player.river[-1]
        del pon_ed_player.river[-1]
        furo = [pon_pai, pon_pai, pon_pai]
        if pon_ed_player.menfon == p_next(pon_player.menfon):
            furo[2]+="*"
        elif pon_ed_player.menfon == p_next(p_next((pon_player.menfon))):
            furo[1]+="*"
        elif pon_ed_player.menfon == p_next(p_next(p_next((pon_player.menfon)))):
            furo[0]+="*"
        pon_player.furo.append(furo)
        del pon_player.tehai[pon_player.tehai.index(pon_pai)]
        del pon_player.tehai[pon_player.tehai.index(pon_pai)]

    def kan(self):
        # 槓牌處理
        # 明槓
        for m, p in self.players.items():
            if m != self.playing and p.is_ippatsu_junme:
                p.is_ippatsu_junme = False
        self.junme += 1
        # 暗槓、加槓
        return 
    def ron(self):
        # 榮和處理
        return 
    def tsumo(self):
        # 自摸處理
        return 
    # def pei(self):
    #     # 拔北處理
    #     return 

    def is_agari(self, tehai:list = None) -> bool:
        if tehai is None:
            tehai = self.players[self.playing].tehai.copy()
        # 確認張數
        if not len(tehai) in (2,5,8,11,14):
            return False
        # 紅寶處理
        tehai = akadorasuu_tran(tehai=tehai)[0]

        tehai = self.sort(tehai)

        # 檢查是否有對子
        double=[]
        for x in tehai:
            if tehai.count(x) >= 2:
                double.append(x)
        if len(double)==0:
            return False
        # 是否為七對子(四張相同牌不算兩對子)
        if len(double)==14:
            return True
        
        # 是否為國士無雙
        gokushi = True
        for i in ["1m", "9m", "1p", "9p", "1s", "9s", "1z", "2z", "3z", "4z", "5z", "6z", "7z"]:
            if not i in tehai:
                gokushi = False
                break
        if gokushi:
            return True
        
        # 正常和牌型檢驗
        a1=tehai.copy()
        a2=[]
        for x in double:
            a1.remove(x)
            a1.remove(x)
            a2.append((x,x))
            for i in range(int(len(a1)/3)):
                if a1.count(a1[0])==3:
                    a2.append((a1[0],)*3)
                    a1=a1[3:]
                elif a1[0][1] !="z" and a1[0] in a1 and card_plus(a1[0]) in a1 and card_plus(card_plus(a1[0])) in a1:
                    a2.append((a1[0],card_plus(a1[0]),card_plus(card_plus(a1[0]))))
                    a1.remove(card_plus(card_plus(a1[0])))
                    a1.remove(card_plus(a1[0]))
                    a1.remove(a1[0])

                else:
                    a1=tehai.copy()
                    a2=[]
                    # 重製
                    break
            else:
                #print('和牌成功,结果：',a2)
                return True

        else:
            return False

    def hansuu(self, player:Player = None, agari_type:str = "tsumo", ron_hai:str = None, output_yaku = False) -> int or tuple[int,list[list]]:
        # 飜數計算
        yaku = []
        tehai = player.tehai.copy()
        if len(player.tehai) in (1,4,7,10,13): # 榮和
            if ron_hai is None:
                print(player.tehai, ron_hai)
                print("Error 01")
                exit()
                return 0
            tehai.append(ron_hai)
        elif not len(player.tehai) in (2,5,8,11,14): # 相公
            return 0

        # 是否為和牌型 (不輸入副露)
        if not self.is_agari(tehai):
            return 0

        # 紅寶處理
        tehai, akadorasuu = akadorasuu_tran(tehai=tehai)
        # 手牌格式轉換 (輸入副露)
        normal_tehai = tehai
        input_tehai = "".join(tehai)
        for i in player.furo:
            i, a = akadorasuu_tran(i)
            akadorasuu += a
            for h in i:
                input_tehai += h[0] + h[1]
                normal_tehai.append(h[0] + h[1])
        agari_hai = normal_tehai[-1]

        han = 0
        if player is None:
            player = self.players["E"]

        # 立直 or 雙立直
        if player.is_riichi and len(player.furo)==0:
            if player.riichi_junme == 1:
                han += 2
                yaku.append([2,s.dabururiichi])
            else:
                han += 1
                yaku.append([1,s.riichi])

        # 一發
        if player.is_ippatsu_junme and len(player.furo)==0:
            han += 1
            yaku.append([1,s.ippatsu])
        
        # 門前清自摸和
        if agari_type == "tsumo" and len(player.furo) == 0:
            han += 1
            yaku.append([1,s.tsumo])

        # 加槓
        # 海底撈月
        # 河底摸魚
        # 嶺上開花

        # support.py 計算之役
        result = support.main(tehai=input_tehai, has_koyaku=False)
        hansuu_yaku_list = result[2]
        pai_combin_list = result[3]
        pos = -1
        del_pos_list = []
        for h in hansuu_yaku_list:
            pos += 1
            pai_combin = pai_combin_list[pos]
            pai_combin.replace(s.yakuhai_ton*3, "111z")
            pai_combin.replace(s.yakuhai_nan*3, "222z")
            pai_combin.replace(s.yakuhai_shaa*3, "333z")
            pai_combin.replace(s.yakuhai_pei*3, "444z")
            pai_combin.replace(s.yakuhai_haku*3, "555z")
            pai_combin.replace(s.yakuhai_hatsu*3, "666z")
            pai_combin.replace(s.yakuhai_chun*3, "777z")
            pai_combin.replace(s.yakuhai_ton*2, "11z")
            pai_combin.replace(s.yakuhai_nan*2, "22z")
            pai_combin.replace(s.yakuhai_shaa*2, "33z")
            pai_combin.replace(s.yakuhai_pei*2, "44z")
            pai_combin.replace(s.yakuhai_haku*2, "55z")
            pai_combin.replace(s.yakuhai_hatsu*2, "66z")
            pai_combin.replace(s.yakuhai_chun*2, "77z")

            splitted_pai_combin = pai_combin.split(" ")
            toitsu = splitted_pai_combin[0]
            mentsu_s = splitted_pai_combin[1:]

            # 國士無雙特判
            if [26, s.kokushimusoujuusanmen] in h or [13, s.kokushimusou] in h:
                if not normal_tehai[-1] in normal_tehai[:-1]:
                    # 一般國士
                    if not [13, s.kokushimusou] in h:
                        h.remove([26, s.kokushimusoujuusanmen])
                        h.append([13, s.kokushimusou])
                else: # 十三面
                    if [13, s.kokushimusou] in h:
                        h.remove([13, s.kokushimusou])
                        h.append([26, s.kokushimusoujuusanmen])

            # 和牌分割不合副露
            def is_mentsu_equal(mentsu1:str, mentsu2:list):
                """123m == [1m*,2m,3m]\n 111z != [1m,1m,1m]"""
                # print(mentsu1,mentsu2)
                if mentsu1[3] == mentsu2[0][1]:
                    num1 = mentsu1[:3]
                    num2 = ""
                    for i in mentsu2:
                        num2 += i[0]
                    num2_list = list(num2)
                    num2_list.sort()
                    num2 = "".join(num2_list)
                    if num1 != num2:
                        return False
                    return True
                return False
            is_correct_furo = True
            if len(splitted_pai_combin) == 5:
                for furo in player.furo.copy():
                    contained = False
                    for i in mentsu_s:
                        if is_mentsu_equal(i, furo):
                            contained = True
                    if not contained:
                        is_correct_furo = False
                        break
            elif len(player.furo) != 0: # 七對子、國士無雙有副露
                is_correct_furo = False
            if not is_correct_furo:
                del_pos_list.append(pos)
                continue

            # 場風、自風特判
            if [1,s.yakuhai_ton+s.question_mark] in h:
                if self.chanfon != "E":
                    h.remove([1,s.yakuhai_ton+s.question_mark])
                else:
                    h.remove([1,s.yakuhai_ton+s.question_mark])
                    h.append([1,s.yakuhai_ton+"(場風)"])
                if player.menfon == "E":
                    h.append([1,s.yakuhai_ton])
            if [1,s.yakuhai_nan+s.question_mark] in h:
                if self.chanfon != "S":
                    h.remove([1,s.yakuhai_nan+s.question_mark])
                else:
                    h.remove([1,s.yakuhai_nan+s.question_mark])
                    h.append([1,s.yakuhai_nan+"(場風)"])
                if player.menfon == "S":
                    h.append([1,s.yakuhai_nan])
            if [1,s.yakuhai_shaa+s.question_mark] in h:
                if self.chanfon != "W":
                    h.remove([1,s.yakuhai_shaa+s.question_mark])
                else:
                    h.remove([1,s.yakuhai_shaa+s.question_mark])
                    h.append([1,s.yakuhai_shaa+"(場風)"])
                if player.menfon == "W":
                    h.append([1,s.yakuhai_ton])
            if [1,s.yakuhai_pei+s.question_mark] in h:
                if self.chanfon != "N":
                    h.remove([1,s.yakuhai_pei+s.question_mark])
                else:
                    h.remove([1,s.yakuhai_pei+s.question_mark])
                    h.append([1,s.yakuhai_pei+"(場風)"])
                if player.menfon == "N":
                    h.append([1,s.yakuhai_pei])
            


            # 門清特判:
            #     一盃口
            #     二盃口
            #     九蓮寶燈/純正
            if len(player.furo) != 0:
                if [1,s.iipeekoo] in h:
                    h.remove([1,s.iipeekoo])
                if [3,s.ryanpeekoo] in h:
                    h.remove([3,s.ryanpeekoo])
                if [1,s.iipeekoo+s.question_mark] in h:
                    h.remove([1,s.iipeekoo+s.question_mark])
                if [3,s.ryanpeekoo+s.question_mark] in h:
                    h.remove([3,s.ryanpeekoo+s.question_mark])
                if [26,s.junseichuurenpouton] in h: # 九蓮
                    h.remove([26,s.junseichuurenpouton])
                if [13,s.chuurenpouton] in h: # 九蓮
                    h.remove([13,s.chuurenpouton])
            # 九蓮特判
            if [13,s.chuurenpouton] in h:
                t = normal_tehai[:-1]
                t.sort()
                nums = ""
                for i in t:
                    nums += i[0]
                if nums == "1112345678999": # 九面聽
                    h.remove([13,s.chuurenpouton])
                    h.append([26,s.junseichuurenpouton])
            elif [26,s.junseichuurenpouton] in h:
                t = normal_tehai[:-1]
                t.sort()
                nums = ""
                for i in t:
                    nums += i[0]
                if nums != "1112345678999": # 非九面聽
                    h.remove([26,s.junseichuurenpouton])
                    h.append([13,s.chuurenpouton])


            # 降翻特判:
            #     三色同順
            #     一氣通貫
            #     混全
            #     混一色
            #     純全
            #     清一色
            #     一色三節
            if len(player.furo) != 0:
                for i in ([3,s.sanshokudoujun], [2,s.ikkitsuukan], [2,s.honchantaiyaochuu], [3,s.honiisoo], [3,s.junchantaiyaochuu], [3,s.junchantaiyaochuu], [6,s.chiniisoo], [3,s.isshokusanjun]):
                    if i in h:
                        h[h.index(i)][0] -= 1

            # 另計:
            #     平和
            if len(player.furo) == 0 and len(mentsu_s) == 4:
                junsuu = 0
                rianmen = False
                for mentsu in mentsu_s:
                    if mentsu[0] in (s.yakuhai_ton,s.yakuhai_nan,s.yakuhai_shaa,s.yakuhai_pei):
                        continue
                    if mentsu[0] == mentsu[1]:
                        continue
                    else:
                        junsuu += 1
                        if agari_hai in (mentsu[0]+mentsu[3], mentsu[2]+mentsu[3]):
                            rianmen = True
                if junsuu == 4 and rianmen:
                    h.append([1, s.pinfu])

            #     寶牌
            dora_list = [card_plus(i, True, True) for i in self.rinshan]
            if akadorasuu != 0:
                h.append([akadorasuu, s.akadorasuu])
            dorasuu = 0
            for d in dora_list:
                dorasuu += normal_tehai.count(d)
            if dorasuu != 0:
                h.append([dorasuu, s.dora])
            #     四槓子
            kan = 0
            for i in player.furo:
                for j in i:
                    if "**" in j:
                        kan += 1
            if kan == 4:
                h.append([13, s.suukantsu])
            #     對對和/三暗刻/四暗刻/單騎
            if [13, s.suuankoo] in h or [26, s.suuankootanki] in h:
                ankan = 0
                for i in player.furo:
                    for j in i:
                        if "***" in j:
                            ankan += 1
                pon_furo = len(player.furo) - ankan
                if pon_furo == 1:
                    if [13, s.suuankoo] in h:
                        h.remove([13, s.suuankoo])
                        h.append([2, s.toitoihoo])
                        h.append([2, s.sanankoo])
                    else:
                        h.remove([26, s.suuankootanki])
                        h.append([2, s.toitoihoo])
                        h.append([2, s.sanankoo])
                elif pon_furo >= 2:
                    if [13, s.suuankoo] in h:
                        h.remove([13, s.suuankoo])
                        h.append([2, s.toitoihoo])
                    else:
                        h.remove([26, s.suuankootanki])
                        h.append([2, s.toitoihoo])
                else:
                    if [13, s.suuankoo] in h:
                        if normal_tehai.count(agari_hai) == 2:
                            h.remove([13, s.suuankoo])
                            h.append([26, s.suuankootanki])
                    else:
                        if normal_tehai.count(agari_hai) != 2:
                            h.remove([26, s.suuankootanki])
                            h.append([13, s.suuankoo])
            #     天地和/人和
            if self.junme == 1:
                if player.menfon == "E":
                    h.append([13, s.tenhou])
                else:
                    h.append([13, s.chiihou])
                    
        # 刪除不合之組合
        del_pos_list.sort()
        del_pos_list.reverse()
        for p in del_pos_list:
            del hansuu_yaku_list[p]

        # 合併、取最大飜數
        maximum = 0
        max_set = hansuu_yaku_list[0]
        for h in hansuu_yaku_list:
            count = 0
            for i in h:
                count += i[0]
            if count > maximum:
                maximum = count
                max_set = h
        han += maximum
        if output_yaku:
            yaku = yaku + max_set
            
            # sort
            # sorted_yaku = yaku.copy()
            # count = 0
            # for s in yaku:
            #     if s[0] == 13:
            #         del sorted_yaku[count]
            #         sorted_yaku.pop(s)

            #     count += 1

            return han, yaku
        else:
            return han
    
    def fusuu(self):
        # 符數計算
        return 
    
    def tensuu(self):
        # 點數計算
        return 
    
    def check_tenpai(self, player:Player = None, overright = True) -> tuple[bool, list[str]]:
        if player is None:
            player = self.players[self.playing]
        is_tenpai = False
        agari_pai = []
        tehai = player.tehai.copy()
        for h in INDEX[0]:
            if self.is_agari(tehai=tehai+[h]):
                is_tenpai = True
                if h[0] == "0":
                    if not "5"+h[1] in agari_pai:
                        agari_pai.append("5"+h[1])
        if is_tenpai and overright:
            player.is_tenpai = True 
            player.tenpais = agari_pai.copy()
            return player.is_tenpai, player.tenpais
        else:
            return True, agari_pai.copy()
    
    def check_riichi(self, player:Player, cut_num:int) -> tuple[bool, list[str] or None]:
        if len(player.furo) != 0:
            return False, None
        if len(player.tehai) != 14:
            print(player.tehai)
            print("Error 02")
            exit()
        tehai = player.tehai.copy()
        del tehai[cut_num]
        riichiable = False
        agari_pai = []
        for h in INDEX[0]:
            if self.is_agari(tehai=tehai+[h]):
                riichiable = True 
                agari_pai.append(h)
        return riichiable, agari_pai

class GameProcess():
    def __init__(self):
        self.game = Game()
        print("rinshan:", self.game.rinshan)

        is_chii_pon_kan = False
        count = 0
        while len(self.game.yama) > 14:
            is_other_action = False # 是否有人鳴牌
            if self.game.playing == "N": # 自身扮演
                if is_chii_pon_kan:
                    pass 
                else:
                    self.game.draw()
                player = self.game.players["N"]
                if self.game.junme == 1: # 作弊一下
                    player.tehai = ["1m","4m","1m","2m","3m","1m","5z","6m","7m","9m","9m","9m","9m","8m"]
                print(player.tehai, player.furo)
                print("  1     2     3     4     5     6     7     8     9     10    11    12    13    14")
                
                is_agari = (self.game.hansuu(player, "tsumo") != 0)
                if is_agari:
                    print("you can tsumo!", end="")
                    if "tsumo" in input(">>>"):
                        print("You Win!!")
                        print(self.game.hansuu(player=player, agari_type="tsumo", output_yaku=True))
                        exit()

                if player.is_riichi: # 立直摸切
                    time.sleep(3)
                    cutting = self.game.cut(0)
                    player.is_ippatsu_junme = False
                    is_tenpai, tenpais = self.game.check_tenpai(player=player)
                    for tenpai in tenpais: # 振聽
                        if tenpai in player.furiten_pai:
                            player.furiten = True
                    if is_tenpai:
                        if player.furiten:
                            print("Tenpai!", str(tenpais), "furiten")
                        else:
                            print("Tenpai!", str(tenpais))
                    is_other_action = self.check(cutting)
                else:

                    userinput = input(">>>").split(" ")
                    
                    if "riichi" in userinput: # 立直
                        riichiable, agari_pai = self.game.check_riichi(player = player, cut_num = int(userinput[0])-1)
                        if riichiable:
                            player.is_riichi = True
                            player.riichi_junme = self.game.junme
                            player.is_tenpai = True
                            player.tenpais = agari_pai.copy()
                            player.is_ippatsu_junme = True
                            print("riichi nia!!")
                        else:
                            print("相公 (指)(怒)")

                    cutting = self.game.cut(int(userinput[0]))
                    is_tenpai, tenpais = self.game.check_tenpai(player=player)
                    if is_tenpai:
                        print("Tenpai!", str(tenpais))
                    is_other_action = self.check(cutting)

            else: # 電腦出牌(自動摸切)
                if is_chii_pon_kan:
                    pass 
                else:
                    self.game.draw()
                cutting = self.game.cut(0)
                print(self.game.playing, ":", cutting)
                is_other_action = self.check(cutting)

            if is_other_action: # 有人鳴牌
                count = MENFON_INDEX.index(self.game.playing)
                is_chii_pon_kan = True
            else:
                self.game.playing = MENFON_INDEX[(count+1)%4]
                is_chii_pon_kan = False
                count += 1
        for m in MENFON_INDEX:
            print(m, end=": ")
            if self.game.players[m].is_tenpai:
                print("Tenpai:", player.tenpais)
            else:
                print("No ten")
    
    def check(self, c:str) -> bool:
        is_action = False
        # 榮和
        players = self.ron_able(c)
        if len(players) != 0:
            for player in players:
                if player.menfon == "N": # 測試用
                    print("you can ron !")
                    userinput = input(">>>")
                    if userinput == "ron":
                        print("YOU WIN!")
                        print(self.game.hansuu(player, "ron", c, output_yaku=True))
                        exit()
                    else:
                        player.furiten_pai.append(c)
                        player.furiten = True

        # 碰
        players = self.pon_able(c)
        if len(players) != 0:
            for player in players:
                if player.menfon == "N" and not player.is_riichi: # 測試用
                    print("you can pon")
                    userinput = input(">>>")
                    if userinput == "pon":
                        self.game.pon(pon_player = player, pon_ed_player = self.game.players[self.game.playing])
                        print("pon nia!")
                        is_action = True
        else:
            pass

        # 槓
        players = self.kan_able(c)
        if len(players) != 0:
            pass
        else:
            pass

        # 吃
        players = self.chi_able(c)
        if len(players) != 0:
            pass
        else:
            pass

        return is_action
    
    def ron_able(self, c:str) -> list[Player]:
        players = []
        for p in MENFON_INDEX:
            if p == self.game.playing:
                continue
            player = self.game.players[p]
            if player.furiten: # 振聽
                continue
            if self.game.hansuu(player = player, agari_type = "ron", ron_hai = c) != 0:
                players.append(player)
        return players
    
    def pon_able(self, c:str) -> list[Player]:
        players = []
        for p in MENFON_INDEX:
            if p == self.game.playing:
                continue
            player = self.game.players[p]
            if player.tehai.count(c) >= 2:
                players.append(player)
        return players
    
    def kan_able(self, c:str) -> list[Player]:
        players = []
        for p in MENFON_INDEX:
            if p == self.game.playing:
                continue
            player = self.game.players[p]
            if player.tehai.count(c) >= 3:
                players.append(player)
        return players
    
    def chi_able(self, c:str) -> list[Player]:
        players = []
        if c[1] == "z":
            return []
        for p in MENFON_INDEX:
            if p == self.game.playing:
                continue
            player = self.game.players[p]
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




if __name__=="__main__":
    GameProcess()
    # tehai = ["1z", "1z", "1z", "4z", "4z", "5m", "6m", "7m", "1s", "1s", "1s", "2s", "3s", "1s"]
    # print(Game.is_agari(self = None, tehai = tehai))
    # g = Game()
    # p = g.players["N"]
    # p.tehai = ["1m","2m","3m","2m","3m","4m","7m","8m","9m","5m"]
    # p.furo = [["7m*","8m","9m"]]
    # p.tehai = ["1m","2m","3m","4m","4m","5m","6m","6m","9m","9m"]
    # p.furo = [["1m*","2m","3m"]]
    # p.tehai = ["1m","1m","1p","9p","1s","9s","1z","2z","3z","4z","5z","6z","7z"]
    # p.tehai = ["1m","1m","1m","2m","3m","4m","5m","6m","7m","9m","9m","9m","9m"]
    # p.furo = [['3m', '3m', '3m*']]
    # p.is_riichi = False 
    # print(g.hansuu(p, "ron", "8m", output_yaku=True))
    # tehai = ['6m', '7m', '4p', '5p', '6p', '2z', '2z', '6z', '6z', '6z']
    # print(g.check_tenpai(p))
    # print(g.is_agari(p.tehai))
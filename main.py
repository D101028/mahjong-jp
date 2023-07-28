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

def card_minus(userinput:str, z_contained = False, mod = False):
    contained = "mpsz" if z_contained else "mps"
    if not userinput[1] in contained:
        return
    if userinput[0] == "0":
        userinput = "5" + userinput[1:]
    if mod:
        if userinput[1] == "z":
            output = str(((int(userinput[0])-1)+1) % 7 - 1) + userinput[1:]
        else:
            output = str(((int(userinput[0])-1)+1) % 9 - 1) + userinput[1:]
    else:
        output = str((int(userinput[0])-1)) + userinput[1:]
    return output

def p_next(p:str):
    return MENFON_INDEX[(MENFON_INDEX.index(p) + 1) % 4]

def akadorasuu_tran(tehai:list[str])->tuple[list,int]:
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

def mentsu_judge(mentsu:list[str]) -> tuple[str, int or None]:
    """output: ('juntsu', None) ('koutsu', pos) ('minkan', pos) ('ankan', pos)"""
    if mentsu[0][0] != mentsu[1][0]:
        # 順子
        return 'juntsu', None
    pos = 0
    for i in mentsu:
        if len(i) != 2:
            if i[2:] == "*":
                return 'koutsu', pos 
            if i[2:] == "**":
                return 'minkan', pos 
            if i[2:] == "***":
                return 'kakan', pos 
        pos += 1
    return 'ankan', None

def pai_combin_tran(pai_combin:str):
    """ '1z1z1z' -> '111z' '2z2z 3z3z3z 123s' -> '22z 333z 123z'"""
    _list = pai_combin.split(" ")
    newlist = []
    for i in _list:
        if len(i) == 6:
            newlist.append(i[0]*3 + i[1])
        elif len(i) == 4 and not i[1] in ('1','2','3','4','5','6','7','8','9'):
            newlist.append(i[0]*2 + i[1])
        else:
            newlist.append(i)
    return " ".join(newlist)

def is_mentsu_equal(mentsu1:str, mentsu2:list):
    """123m == [1m*,2m,3m]\n 111z != [1m,1m,1m]\n 1z1z1z == [1z,1z,1z]"""
    # print(mentsu1,mentsu2)
    if len(mentsu1) == 6:
        mentsu1 = mentsu1[0]+mentsu1[2]+mentsu1[4]+mentsu1[5]
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

def round_up(num:int, n:int = 2):
    if num % 10**n == 0:
        return num 
    else:
        return (num//10**n+1)*10**n

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
        # 捨牌、立直振聽
        self.furiten_pai = []
        self.furiten = False
        # 同巡振聽
        self.doujun_furiten_pai = []
        self.doujun_furiten = False
    
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

    def is_menchin(self):
        for i in self.furo:
            for j in i:
                if len(i) != 2:
                    return False 
        return True

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
        
        # 嶺上開花巡
        self.rinshankaihou_able = False
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
        if cutting[0] == "0":
            player.furiten_pai.append("5"+cutting[1:])
        else:
            player.furiten_pai.append(cutting)

        # 解除同巡振聽
        player.doujun_furiten_pai = []
        player.doujun_furiten = False

        return cutting


    def chi(self, chi_player:Player, chi_ed_player:Player):
        # 吃牌處理
        for m, p in self.players.items():# 斷一發
            if m != self.playing and p.is_ippatsu_junme:
                p.is_ippatsu_junme = False
        self.junme += 1
        self.playing = chi_player.menfon

        chi_pai = chi_ed_player.river[-1]
        del chi_ed_player.river[-1]
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
                    print(count, ":", i)
                userinput = int(input(">>>"))
                chi_num = userinput - 1
        furo = []
        furo.append(chi_pai+"*")
        for i in could_furo[chi_num]:
            if i != chi_pai:
                furo.append(i)
                del chi_player.tehai[chi_player.tehai.index(i)]
        chi_player.furo.append(furo)

    def pon(self, pon_player:Player, pon_ed_player:Player):
        # 碰牌處理
        for m, p in self.players.items():# 斷一發
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

    def minkan(self, kan_player:Player, kan_ed_player:Player):
        # 明槓處理
        for m, p in self.players.items():# 斷一發
            if m != self.playing and p.is_ippatsu_junme:
                p.is_ippatsu_junme = False
        self.junme += 1
        self.playing = kan_player.menfon

        kan_pai = kan_ed_player.river[-1]
        del kan_ed_player.river[-1]
        furo = [kan_pai, kan_pai, kan_pai]
        if kan_ed_player.menfon == p_next(kan_player.menfon):
            furo[2]+="**"
        elif kan_ed_player.menfon == p_next(p_next(kan_player.menfon)):
            furo[1]+="**"
        elif kan_ed_player.menfon == p_next(p_next(p_next(kan_player.menfon))):
            furo[0]+="**"
        kan_player.furo.append(furo)
        del kan_player.tehai[kan_player.tehai.index(kan_pai)]
        del kan_player.tehai[kan_player.tehai.index(kan_pai)]
        del kan_player.tehai[kan_player.tehai.index(kan_pai)]

        # 嶺上開花巡
        self.rinshankaihou_able = True

    def kakan(self, h:str):
        # 加槓
        player = self.players[self.playing]

        for m, p in self.players.items():# 斷一發
            if m != self.playing and p.is_ippatsu_junme:
                p.is_ippatsu_junme = False
        self.junme += 1
        self.playing = player.menfon

        del player.tehai[player.tehai.index(h)]
        count = 0
        for i in player.furo:
            _type, pos = mentsu_judge(i)
            if _type == "koutsu":
                if i[0][0]+i[0][1] == h:
                    player.furo[count][pos] = h+"***"
                    break
            count += 1

        # 嶺上開花巡
        self.rinshankaihou_able = True

    def ankan(self, pai:str):
        # 暗槓
        player = self.players[self.playing]
        self.junme += 1
        self.playing = player.menfon 
        player.tehai.remove(pai)
        player.tehai.remove(pai)
        player.tehai.remove(pai)
        player.tehai.remove(pai)
        player.furo.append([pai, pai, pai])


        # 翻寶牌指示牌
        self.rinshan.append(self.yama[0])
        del self.yama[0]
        print("rinshan:",self.rinshan)

        # 嶺上開花巡
        self.rinshankaihou_able = True

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
            if tehai.count(x) >= 2 and not x in double:
                double.append(x)
        if len(double)==0:
            return False
        # 是否為七對子(四張相同牌不算兩對子)
        if len(double)==7:
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

    def hansuu(self, player:Player = None, 
               agari_type:str = "tsumo", 
               ron_hai:str = None, 
               is_chyankan = False, 
               is_output_yaku = False, 
               is_output_pai_combin = False, 
               is_output_fusuu = False) -> int or tuple[int,list[list]] or tuple[int,list[list],str] or tuple[int,list[list],str,int]:
        """飜數計算 >>>`is_output_yaku` `is_output_pai_combin` `is_output_fusuu` 為向上必須"""
        if is_output_fusuu:
            is_output_yaku, is_output_pai_combin = True, True
        elif is_output_pai_combin:
            is_output_yaku = True
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

        # 是否門清
        is_menchin = player.is_menchin()
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
        agari_hai = player.tehai[-1]

        han = 0
        if player is None:
            player = self.players["E"]

        # 立直 or 雙立直
        if player.is_riichi and is_menchin:
            if player.riichi_junme == 1:
                han += 2
                yaku.append([2,s.dabururiichi])
            else:
                han += 1
                yaku.append([1,s.riichi])

        # 一發
        if player.is_ippatsu_junme and is_menchin:
            han += 1
            yaku.append([1,s.ippatsu])
        
        # 門前清自摸和
        if agari_type == "tsumo" and is_menchin:
            han += 1
            yaku.append([1,s.tsumo])

        # 搶槓(明、加槓)
        if is_chyankan:
            han += 1
            yaku.append([1,s.chyankan])

        # 海底撈月、河底摸魚
        if len(self.yama) == 0:
            han += 1
            if agari_type == "tsumo":
                yaku.append([1,s.haiteiraoyue])
            else:
                yaku.append([1,s.houteiraoyui])
        # 嶺上開花
        if agari_type == "tsumo" and self.rinshankaihou_able:
            han += 1
            yaku.append([1,s.rinshankaihou])

        # support.py 計算之役
        result = support.main(tehai=input_tehai, has_koyaku=False)
        hansuu_yaku_list = result[2]
        pai_combin_list = result[3]
        temp = []
        for pai_combin_ in pai_combin_list: # 調整格式
            temp.append(pai_combin_tran(pai_combin_))
        pai_combin_list = temp
        pos = -1
        del_pos_list = []
        for h in hansuu_yaku_list:
            pos += 1
            pai_combin = pai_combin_list[pos]

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
            elif not is_menchin: # 七對子、國士無雙有副露
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
            if not is_menchin:
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
            if not is_menchin:
                for i in ([3,s.sanshokudoujun], [2,s.ikkitsuukan], [2,s.honchantaiyaochuu], [3,s.honiisoo], [3,s.junchantaiyaochuu], [3,s.junchantaiyaochuu], [6,s.chiniisoo], [3,s.isshokusanjun]):
                    if i in h:
                        h[h.index(i)][0] -= 1

            # 另計:
            #     平和
            if is_menchin and len(mentsu_s) == 4:
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

            #     四槓子
            kan = 0
            for i in player.furo:
                _type = mentsu_judge(i)[0]
                if _type in ('minkan', 'ankan', 'kakan'):
                    kan += 1
            if kan == 4:
                h.append([13, s.suukantsu])
            #     對對和/三暗刻/四暗刻/單騎
            if [13, s.suuankoo] in h or [26, s.suuankootanki] in h:
                ankan = 0
                for i in player.furo:
                    not_ankan = False
                    for j in i:
                        if len(j) != 2:
                            not_ankan = True
                            break 
                    if not not_ankan:
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
            if [2, s.sanankoo] in h and agari_type == "ron": # 三暗刻特判
                m_temp  = mentsu_s.copy()
                furo_temp = player.furo.copy()
                del_num = []
                count = 0
                for mentsu in mentsu_s:
                    for f in furo_temp:
                        if is_mentsu_equal(mentsu, f):
                            del_num.append(count)
                            furo_temp.remove(f)
                    count += 1
                    del_num.reverse()
                for i in del_num:
                    del m_temp[i]
                for mentsu in m_temp:
                    if agari_hai == mentsu[0]+mentsu[-1]:
                        h.remove([2, s.sanankoo])

            #     天地和/人和
            if self.junme == 1:
                if player.menfon == "E":
                    h.append([13, s.tenhou])
                else:
                    h.append([13, s.chiihou])
                    
            #     寶牌 # 不是役
            if len(yaku) + len(h) != 0:
                dora_list = [card_plus(i, True, True) for i in self.rinshan]
                if akadorasuu != 0:
                    h.append([akadorasuu, s.akadorasuu])
                dorasuu = 0
                for d in dora_list:
                    dorasuu += normal_tehai.count(d)
                if dorasuu != 0:
                    h.append([dorasuu, s.dora])
            
            #     裡寶牌
                if player.is_riichi:
                    uradorasuu = 0
                    uradora_pointer = []
                    for i in self.rinshan:
                        uradora_pointer.append(self.yama[-1])
                        del self.yama[-1]
                    uradora = [card_plus(i, True, True) for i in uradora_pointer]
                    for i in uradora:
                        if i in normal_tehai:
                            uradorasuu += 1
                    if uradorasuu != 0:
                        h.append([uradorasuu, s.uradora])

        # 刪除不合之組合
        del_pos_list.sort()
        del_pos_list.reverse()
        for p in del_pos_list:
            del hansuu_yaku_list[p]
        for p in del_pos_list:
            del pai_combin_list[p]

        # 合併、役滿特判
        final_yaku_list = []
        for i in hansuu_yaku_list:
            yaku_temp = yaku + i
            is_yakuman = False
            yakuman = []
            for y in yaku_temp:
                if y[0] >= 13 and y[1] != s.dora:
                    yakuman.append(y)
                    is_yakuman = True
            if not is_yakuman:
                final_yaku_list.append(yaku_temp)
            else:
                final_yaku_list.append(yakuman)
        # 取最大飜數
        maximum = 0
        max_set = final_yaku_list[0]
        pos = 0
        max_pos = 0
        for h in final_yaku_list:
            count = 0
            for i in h:
                count += i[0]
            if count > maximum:
                maximum = count
                max_set = h
                max_pos = pos
            pos += 1
        han = maximum

        output_yaku = max_set
        output_pai_combin = pai_combin_tran(pai_combin_list[max_pos])
        if is_output_yaku:
            if is_output_pai_combin:
                if is_output_fusuu:
                    is_pinfu = [1,s.pinfu] in output_yaku
                    output_fusuu = self.fusuu(player, agari_type, agari_hai, output_yaku, output_pai_combin.split(" "), is_pinfu)
                    return han, output_yaku, output_pai_combin, output_fusuu
                return han, output_yaku, output_pai_combin
            else:
                return han, output_yaku
        else:
            return han
    
    def fusuu(self, 
              player:Player, 
              agari_type:str = "tsumo", 
              agari_hai:str = None, 
              han_combin:list[list[int,str]] = None, 
              pai_combin:list[str] = None, 
              is_pinfu:bool = None
              ) -> int:
        """符數計算"""
        # 特判
        if [2, s.chiitoitsu] in han_combin or [13, s.kokushimusou] in han_combin or [26, s.kokushimusoujuusanmen]in han_combin:
            return 25
        if is_pinfu:
            if agari_type == "tsumo":
                return 30
            else:
                return 20
        # 底符
        fu = 20
        # 門前加符
        if agari_type == "ron" and player.is_menchin():
            fu += 10
        # 自摸
        if agari_type == "tsumo":
            fu += 2

        # 面子
        toitsu = pai_combin[0]
        furo = player.furo.copy()
        tehai_temp = [] # 非副露之手牌
        for i in pai_combin[1:]:
            is_furo = False
            for f in furo:
                if is_mentsu_equal(i, f): # 副露 + 暗槓
                    furo.remove(f)
                    mentsu_type = mentsu_judge(f)[0]
                    if mentsu_type == "juntsu":
                        pass 
                    elif mentsu_type == "koutsu": # 明刻
                        if i[0] in ("1", "9") or i[-1] == "z": # 么九
                            fu += 4
                        else: 
                            fu += 2
                    elif mentsu_type == "minkan":
                        if i[0] in ("1", "9") or i[-1] == "z":
                            fu += 16
                        else:
                            fu += 8
                    elif mentsu_type == "ankan":
                        if i[0] in ("1", "9") or i[-1] == "z":
                            fu += 32
                        else:
                            fu += 16
                    is_furo = True
                    break 
            # 非副露
            if not is_furo and i[0]==i[1]: # 暗刻
                if i[0] in ("1", "9") or i[-1] == "z":
                    fu += 8
                else:
                    fu += 4
            tehai_temp.append(i)
        # 雀頭
        pai = toitsu[0]+toitsu[-1]
        if pai in ("5z","6z","7z"): # 三元牌
            fu += 2
        dict_temp = {"E":"1z","S":"2z","W":"3z","N":"4z"}
        if pai == dict_temp[player.menfon]:
            fu += 2
        if pai == dict_temp[self.chanfon]:
            fu += 2
        # 聽牌型
        tanki = agari_hai == pai
        kanchan = False
        bienchan = False
        if len(tehai_temp) != 0:
            for i in tehai_temp:
                if i[0:3] in ("123", "789"):
                    if agari_hai in ("3"+i[-1], "7"+i[-1]):
                        bienchan = True
                if i[0:3] in ("123","234","345","456","567","678","789"):
                    if agari_hai[-1] == i[-1]:
                        if agari_hai[0] == i[1]:
                            kanchan = True
                if bienchan and kanchan:
                    break
        if tanki: # 單騎聽
            fu += 2
        elif bienchan: # 邊張聽
            fu += 2
        elif kanchan: # 崁張聽
            fu += 2
        fu = round_up(fu, 1)
        return fu
    
    def tensuu(self, hansuu:int, fusuu:int, is_banker:bool = False):
        """output: [all, [閒家, 莊家]] or [all, [閒家]]"""
        # 點數計算
        # 青天井規則
        # basic = fusuu*2**(hansuu+2)
        # if is_banker:
        #     return [round_up(basic*2*3,2), [round_up(basic*2)]]
        # else:
        #     return [round_up(basic*4,2), [round_up(basic, 2), round_up(basic*2)]]
        
        # 一般規則
        if hansuu>=5 or (hansuu==4 and fusuu>=40) or (hansuu==3 and fusuu>=70):
            if hansuu in (3,4,5):
                if is_banker:
                    return [12000,[4000]]
                else:
                    return [8000,[2000,4000]]
            elif hansuu in (6,7):
                if is_banker:
                    return [18000,[6000]]
                else:
                    return [12000,[3000,6000]]
            elif hansuu in (8,9,10):
                if is_banker:
                    return [24000,[8000]]
                else:
                    return [16000,[4000,8000]]
            elif hansuu in (11,12):
                if is_banker:
                    return [36000,[12000]]
                else:
                    return [24000,[6000,12000]]
            else:
                if is_banker:
                    return [48000,[16000]]
                else:
                    return [32000,[8000,16000]]
        else:
            basic = fusuu*2**(hansuu+2)
            if is_banker:
                return [round_up(basic*2*3,2), [round_up(basic*2)]]
            else:
                return [round_up(basic*4,2), [round_up(basic, 2), round_up(basic*2)]]

    
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
                else:
                    agari_pai.append(h)
        if is_tenpai and overright:
            player.is_tenpai = True 
            player.tenpais = agari_pai.copy()
            return player.is_tenpai, player.tenpais
        else:
            if overright:
                player.is_tenpai = is_tenpai
                player.tenpais = agari_pai.copy()
            return is_tenpai, agari_pai.copy()
    
    def check_riichi(self, player:Player, cut_num:int) -> tuple[bool, list[str] or None]:
        if not player.is_menchin():
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
a = ""
class GameProcess():
    def __init__(self):
        self.game = Game()
        print("rinshan:", self.game.rinshan)

        is_to_draw = True # 是否摸牌
        is_ankan_out = False # 紀錄上一次是否為暗槓
        count = 0
        while len(self.game.yama) > 14:
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
                global a
                if a == "4z": # 超級作弊
                    player.tehai[-1] = "3z"
                    a = "3z"
                elif a == "3z":
                    player.tehai[-1] = "2z"
                    a = "2z"
                elif a == "2z":
                    player.tehai[-1] = "1z"
                    a = "1z"
                elif a == "1z":
                    player.tehai[-1] = "5z"
                    a = "5z"
                if self.game.junme == 1: # 作弊一下
                    player.tehai = ["5z","4z","1z","1z","1z","2z","2z","2z","3z","3z","3z","4z","4z","4z"]
                    a = "4z"
                print(player.tehai, player.furo)
                print("  1     2     3     4     5     6     7     8     9     10    11    12    13    14")
                
                # 自摸
                is_agari = (self.game.hansuu(player, "tsumo") != 0)
                if is_agari:
                    print("you can tsumo!", end="")
                    if "tsumo" in input(">>>"):
                        print("You Win!!")
                        hansuu, yaku_list, pai_combin, fusuu = self.game.hansuu(player=player, agari_type="tsumo", is_output_fusuu=True)
                        tensuu = self.game.tensuu(hansuu, fusuu, False)
                        print(yaku_list)
                        print(hansuu, "飜", fusuu, "符")
                        print(tensuu)
                        exit()

                furo_koutsu = [] # ex.["2m", "1z"]
                for h in player.furo:
                    if mentsu_judge(h)[0] == "koutsu":
                        furo_koutsu.append(h[0][0]+h[0][1])
                
                # 槓
                if is_to_draw: # 吃、碰完不能加槓
                    # 加槓
                    for h in furo_koutsu:
                        if h in player.tehai: # 測試用
                            print("you can kakan", h, end=" ")
                            userinput = input(">>>")
                            if userinput == "kakan" or userinput == "kan":
                                print("kan nia!")
                                self.game.kakan(h)
                                is_kakan = True
                                is_other_action = True
                                self.chyankan_check(h)
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
                        print("you can ankan", pai, end=" ")
                        userinput = input(">>>")
                        if userinput == "ankan" or userinput == "kan":
                            print("kan nia!")
                            self.game.ankan(pai)
                            is_ankan = True 
                            is_other_action = True 
                            self.kokushi_chyankan_check(pai)

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
                            print("Tenpai!", str(tenpais), "furiten")
                        else:
                            print("Tenpai!", str(tenpais))
                    is_chi_pon_inner, is_minkan = self.check(cutting)
                    is_other_action = is_chi_pon_inner or is_minkan
                elif not is_kakan and not is_ankan: # 槓完直接進下一迴圈(同理摸嶺上牌)
                    userinput = input("切牌>>>").split(" ")
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
                            print("Tenpai!", str(tenpais), "furiten")
                        else:
                            print("Tenpai!", str(tenpais))

                    is_chi_pon_inner, is_minkan = self.check(cutting)
                    is_other_action = is_chi_pon_inner or is_minkan

                    if self.game.rinshankaihou_able: # 明槓&加槓翻寶牌指示牌、結束嶺上開花巡
                        if is_ankan_out: # 暗槓不翻
                            pass 
                        else: # 明加槓翻寶牌指示牌
                            self.game.rinshan.append(self.game.yama[0])
                            del self.game.yama[0]
                            print("rinshan:",self.game.rinshan)
                        self.game.rinshankaihou_able = False


            else: # 電腦出牌(自動摸切)
                if not is_to_draw:
                    pass 
                else:
                    self.game.draw()
                cutting = self.game.cut(0)
                print(self.game.playing, ":", cutting)
                is_chi_pon_inner, is_minkan = self.check(cutting)
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

        for m in MENFON_INDEX: # 荒牌流局
            print(m, end=": ")
            if self.game.players[m].is_tenpai:
                print("Tenpai:", player.tenpais)
            else:
                print("No ten")
    
    def kokushi_chyankan_check(self, kan_pai:str):
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
                        print("you can ron !")
                        userinput = input(">>>")
                        if userinput == "ron":
                            print("YOU WIN!")
                            hansuu, yaku_list, pai_combin, fusuu = self.game.hansuu(player, "ron", kan_pai, is_output_yaku=True, is_chyankan=True,is_output_fusuu=True)
                            tensuu = self.game.tensuu(hansuu, fusuu, False)
                            print(yaku_list)
                            print(hansuu, "飜", fusuu, "符")
                            print(tensuu)
                            exit()
                        else:
                            if player.is_riichi: # 立直振聽
                                player.furiten_pai.append(kan_pai)
                                player.furiten = True
        return 

    def chyankan_check(self, kan_pai:str): # 未 debug
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
                    print("you can ron !")
                    userinput = input(">>>")
                    if userinput == "ron":
                        print("YOU WIN!")
                        hansuu, yaku_list, pai_combin, fusuu = self.game.hansuu(player, "ron", kan_pai, is_output_yaku=True, is_chyankan=True, is_output_fusuu=True)
                        tensuu = self.game.tensuu(hansuu, fusuu, False)
                        print(yaku_list)
                        print(hansuu, "飜", fusuu, "符")
                        print(tensuu)
                        exit()
                    else:
                        if player.is_riichi: # 立直振聽
                            player.furiten_pai.append(kan_pai)
                            player.furiten = True

    def check(self, c:str) -> bool:
        is_chi_pon = False
        is_minkan = False
        playing_player = self.game.players[self.game.playing]
        # 榮和
        players = self.ron_able(c)
        if len(players) != 0:
            for player in players:
                if player.menfon == "N": # 測試用
                    print("you can ron !")
                    userinput = input(">>>")
                    if userinput == "ron":
                        print("YOU WIN!")
                        hansuu, yaku_list, pai_combin, fusuu = self.game.hansuu(player, "ron", c, is_output_fusuu=True)
                        tensuu = self.game.tensuu(hansuu, fusuu, False)
                        print(yaku_list)
                        print(hansuu, "飜", fusuu, "符")
                        print(tensuu)
                        exit()
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
        players = self.pon_able(c)
        if len(players) != 0:
            for player in players:
                if player.is_riichi:
                    continue
                if player.menfon == "N": # 測試用
                    print("you can pon")
                    userinput = input(">>>")
                    if userinput == "pon":
                        self.game.pon(pon_player = player, pon_ed_player = playing_player)
                        print("pon nia!")
                        is_chi_pon = True
        
        # 明槓
        players = self.kan_able(c)
        if len(players) != 0:
            for player in players:
                if player.is_riichi:
                    continue
                if player.menfon == "N": # 測試用
                    print("you can kan")
                    userinput = input(">>>")
                    if userinput == "kan":
                        self.game.minkan(kan_player = player, kan_ed_player = playing_player)
                        print("kan nia!")
                        self.chyankan_check(c)
                        is_minkan = True
        
        # 吃
        players = self.chi_able(c)
        if len(players) != 0:
            next_player = self.game.players[p_next(self.game.playing)]
            if next_player in players:
                if next_player.menfon == "N": # 測試用
                    print("you can chi")
                    userinput = input(">>>")
                    if userinput == "chi":
                        self.game.chi(chi_player = next_player, chi_ed_player = playing_player)
                        print("chi nia!")
                        is_chi_pon = True
        
        return is_chi_pon, is_minkan
    
    def ron_able(self, c:str) -> list[Player]:
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
    
    def pon_able(self, c:str) -> list[Player]:
        players = []
        for p in MENFON_INDEX:
            player = self.game.players[p]
            if p == self.game.playing or player.is_riichi:
                continue
            if player.tehai.count(c) >= 2:
                players.append(player)
        return players
    
    def kan_able(self, c:str) -> list[Player]:
        # 明槓
        players = []
        for p in MENFON_INDEX:
            player = self.game.players[p]
            if p == self.game.playing or player.is_riichi:
                continue
            if player.tehai.count(c) >= 3:
                players.append(player)
        return players
    
    def chi_able(self, c:str) -> list[Player]:
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




if __name__=="__main__":
    GameProcess()
    print(Game.tensuu(None, 1, 30, False))
    # tehai = ["1z", "1z", "1z", "4z", "4z", "5m", "6m", "7m", "1s", "1s", "1s", "2s", "3s", "1s"]
    # print(Game.is_agari(self = None, tehai = tehai))
    # g = Game()
    # print(g.rinshan)
    # p = g.players["N"]
    # p.tehai = ["1m","2m","3m","2m","3m","4m","7m","7m","7m","1s","2s","3s","5s"]

    # p.furo = [["7m*","8m","9m"]]
    # p.tehai = ["1m","2m","3m","4m","4m","5m","6m","6m","9m","9m"]
    # p.furo = [["1m*","2m","3m"]]
    # p.tehai = ["1m","1m","1p","9p","1s","9s","1z","2z","3z","4z","5z","6z","7z"]
    # p.tehai = ["1m","1m","1m","2m","3m","4m","5m","6m","7m","9m","9m","9m","9m"]
    # p.furo = [['3m', '3m', '3m*']]
    # p.is_riichi = False 
    # print(g.hansuu(p, "ron", "5s", is_output_yaku=True))
    # tehai = ['6m', '7m', '4p', '5p', '6p', '2z', '2z', '6z', '6z', '6z']
    # print(g.check_tenpai(p))
    # print(g.is_agari(p.tehai))
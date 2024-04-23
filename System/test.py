# from player import Player
from pai import *
from ext import support

# create_pai_list

# str_list = ["1m","8m","6m","1m","1m","8m","6m","5m","2z","2z","2z","4z","4z"]
# hoora_list = ["1m","1m","1m","1m","2m","3m","4m","5m","6m","7m","8m","9m","9m","9m"]
# hoora_list = ["2m","2m","2m","2m","3m","3m","3m","3m","4m","4m","4m","4m","5m","5m"]
# str_list = ["2m","2m","2m","2m","3m","3m","3m","3m","4m","4m","4m","4m","5m"]
# hoora_list = ["1m","9m","1p","9p","1s","9s","1z","2z","3z","4z","5z","6z","7z","7z"]
# hoora_list = ["1m","1m","2m","2m","3m","3m","4m","4m","5m","5m","6m","6m","7m","7m"]
# pai_list1 = [Pai(p) for p in hoora_list]
# [print(a) for a in get_agari_comb_list(pai_list1)]
# str_list = ["1m","9m","1p","9p","1s","9s","2z","2z","3z","4z","5z","6z","7z"]
# str_list = ["1m","1m","1m","1m","2m","2m","2m","2m","3m","3m","3m","3m","4m"]
# str_list = ["1m","1m","1m","1m","3m","3m","4m","4m","5m","5m","6m","6m","7m"]
# pai_list = [Pai(p) for p in str_list]

# tehai = Tehai(pai_list)
# tehai.get_tehai_comb_list()
# [print(tehai_comb) for tehai_comb in tehai.tehai_comb_list]

# s = "11122233399s11z"
# s = "1112223334449s"
s = "2345566778s"
f1 = "234s"
# f2 = "1111s"
# f3 = "1111m"
# f4 = "1111z"
pai_list = create_pai_list(s)
f_pai_list1 = create_pai_list(f1)
# f_pai_list2 = create_pai_list(f2)
# f_pai_list3 = create_pai_list(f3)
# f_pai_list4 = create_pai_list(f4)
param = Param(
    is_riichi=False, 
    riichi_junme=None, 
    agari_junme=10, 
    is_tsumo=True, 
    is_ron=False, 
    is_chyankan=False, 
    available_pai_num=30, 
    menfon=lang.nan, 
    chanfon=lang.ton, 
    is_rinshanpai_agari=False, 
    dora_pointers=[Pai("5s")]
)

tehai = Tehai(pai_list)
furo1 = Furo(lang.shuntsu, tuple(f_pai_list1), 2)
# furo2 = Furo(lang.minkan, tuple(f_pai_list2), 2)
# furo3 = Furo(lang.minkan, tuple(f_pai_list3), 2)
# furo4 = Furo(lang.minkan, tuple(f_pai_list4), 2)

tehai.furo_list.append(furo1)
# tehai.furo_list.append(furo2)
# tehai.furo_list.append(furo3)
# tehai.furo_list.append(furo4)
# comb_list = tehai.get_tehai_comb_list()
# for c in comb_list:
#     print(c)
#     yaku_list = get_yaku_list(c, param)
#     for yaku in yaku_list:
#         print(yaku, end=" ")
#     print(f"紅寶牌數：{len(c.akadora_list)}")
#     [print(p, end = " ") for p in c.all_pais()]
#     print("\n")

l = get_agari_result_list(tehai, agari_pai=Pai("5s"), param=param)
[print(r) for r in l]

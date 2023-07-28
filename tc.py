# -*- coding: utf-8 -*-
#!/usr/bin/python3
#python 3.7.2 3.7.3

"""
由胡祥友于2019年2月20日翻译
由胡祥友于2019年6月6日翻译
"""
title="麻將計算器"

ask_input_tehai="輸入手牌"
help="輸入手牌：m=萬，p=筒，s=索，z=字。1~7z=東、南、西、北、白、發、中\n輸入test查看示例\n詳細內容請查看README.md"
language_switched="語言已切換至中文"
has_0="手牌含有0，按5處理"
has_0m="手牌含有0m，按5m處理"
has_0p="手牌含有0p，按5p處理"
has_0s="手牌含有0s，按5s處理"
has_invalid_input="手牌含有無效輸入"
low_speed="手牌過多，確定繼續嗎？（直接按回車繼續）"

yakuman_level_list=('','役滿','兩倍役滿','三倍役滿','四倍役滿','五倍役滿','六倍役滿','七倍役滿')
kazoeyakuman='累計役滿'
tehai="手牌"
more_than_4="{}多於4張"
more_than_14="{}張手牌，多於14張"
less_than_13="{}張手牌，少於13張（可能有副露）"
taapai_or_shaopai="{}張手牌，大相公或小相公"
dora='寶牌'
akadora='紅寶牌'
uradora='裡寶牌'

riichi='立直'
ippatsu="一發"
dabururiichi='雙立直'
tsumo='自摸'
tenhou='天和'
chiihou='地和'
chyankan='搶槓'
haiteiraoyue='海底撈月'
houteiraoyui='河底撈魚'

kokushimusoujuusanmen='國士無雙十三面'
kokushimusou='國士無雙'
chiitoitsu='七對子'
tanyaochuu='斷幺九'
yakuhai_ton='東'
yakuhai_nan='南'
yakuhai_shaa='西'
yakuhai_pei='北'
yakuhai_haku='白'
yakuhai_hatsu='發'
yakuhai_chun='中'
pinfu='平和'
iipeekoo='一盃口'
rinshankaihou='嶺上開花'
sanshokudoujun='三色同順'
ikkitsuukan='一氣通貫'
honchantaiyaochuu='混全帶幺九'
toitoihoo='對對和'
sanankoo='三暗刻'
honroutou='混老頭'
sanshokudookoo='三色同刻'
shousangen='小三元'
honiisoo='混一色'
junchantaiyaochuu='純全帶幺九'
ryanpeekoo='二盃口'
chiniisoo='清一色'
suuankootanki='四暗刻單騎'
suuankoo='四暗刻'
daisangen='大三元'
tsuuiisoo='字一色'
shousuushii='小四喜'
ryuuiisoo='綠一色'
chinroutou='清老頭'
junseichuurenpouton='純正九蓮寶燈'
chuurenpouton='九蓮寶燈'
daisuushii='大四喜'
sankantsu='三槓子'
suukantsu='四槓子'
beginning_of_the_cosmos='天地創世'

hoora="和了"
fuu="符"
han="番"
ten="點"
not_hoora="沒有和了"
da="打"
karaten="空聽"
tenpai="聽牌"
nooten="沒有聽牌"
furiten="振聽"

colon="："
ideographic_comma="、"
question_mark="？"
time_spent="計算耗時{}秒"

has_koyaku="已開啟古役"
not_has_koyaku="已關閉古役"
koyaku="古役"
uumensai="五門齊"
sanrenkoo="三連刻"
isshokusanjun="一色三同順"
daisharin="大車輪"
daichikurin="大竹林"
daisuurin="大數邻"
daichisei="大七星"

ok="確定"
clear="清空"
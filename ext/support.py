import discord 
from discord.ext import commands

INDEX = [
    ["1m","2m","3m","4m","5m","6m","7m","8m","9m",
     "1p","2p","3p","4p","5p","6p","7p","8p","9p",
     "1s","2s","3s","4s","5s","6s","7s","8s","9s",
     "1z","2z","3z","4z","5z","6z","7z",
     "0m","0p","0s"],
    # {
    #     "萬":"m", "索":"s", "筒":"p",
    #     "東南西北白發中":"1234567z",
    #     "赤萬所筒":"0mps"
    # }, 
    # 有赤寶
    ["1m","2m","3m","4m","0m","6m","7m","8m","9m","1m","2m","3m","4m","5m","6m","7m","8m","9m","1m","2m","3m","4m","5m","6m","7m","8m","9m","1m","2m","3m","4m","5m","6m","7m","8m","9m",
     "1p","2p","3p","4p","0p","6p","7p","8p","9p","1p","2p","3p","4p","5p","6p","7p","8p","9p","1p","2p","3p","4p","5p","6p","7p","8p","9p","1p","2p","3p","4p","5p","6p","7p","8p","9p",
     "1s","2s","3s","4s","0s","6s","7s","8s","9s","1s","2s","3s","4s","5s","6s","7s","8s","9s","1s","2s","3s","4s","5s","6s","7s","8s","9s","1s","2s","3s","4s","5s","6s","7s","8s","9s",
     "1z","2z","3z","4z","5z","6z","7z","1z","2z","3z","4z","5z","6z","7z","1z","2z","3z","4z","5z","6z","7z","1z","2z","3z","4z","5z","6z","7z",
     ],
    # 無赤寶
    ["1m","2m","3m","4m","5m","6m","7m","8m","9m","1m","2m","3m","4m","5m","6m","7m","8m","9m","1m","2m","3m","4m","5m","6m","7m","8m","9m","1m","2m","3m","4m","5m","6m","7m","8m","9m",
     "1p","2p","3p","4p","5p","6p","7p","8p","9p","1p","2p","3p","4p","5p","6p","7p","8p","9p","1p","2p","3p","4p","5p","6p","7p","8p","9p","1p","2p","3p","4p","5p","6p","7p","8p","9p",
     "1s","2s","3s","4s","5s","6s","7s","8s","9s","1s","2s","3s","4s","5s","6s","7s","8s","9s","1s","2s","3s","4s","5s","6s","7s","8s","9s","1s","2s","3s","4s","5s","6s","7s","8s","9s",
     "1z","2z","3z","4z","5z","6z","7z","1z","2z","3z","4z","5z","6z","7z","1z","2z","3z","4z","5z","6z","7z","1z","2z","3z","4z","5z","6z","7z",
     ], 
    # 字牌
    ["1z", "2z", "3z", "4z", "5z", "6z", "7z"], 
    # 數牌
    ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", 
     "1s", "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s", 
     "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", 
     "0m", "0s", "0p"]
]
DESCRIPTION_DEMO = """
### 麻將測試 0.1

還在測試版本。
點擊 Join 開始遊戲。

## 遊戲簡介
規則同日麻，測試版時期為單人座北風。
吃碰槓牌及立直牌以 \* 代替旋轉90度，
\* 表吃、碰；\** 表大明槓；\***表加槓；皆無則表暗槓。

! 榮和平和計30符
! 不計流局滿貫
! 四張相同牌可算作雙碰聽
! 不計食替
! 不計四風連打
! 不計九種九牌
"""
DESCRIPTION = """
### 好玩的麻將（暫） 1.0

點擊 Join 加入遊戲。

## 遊戲說明
一般規則同日麻，東一局無連莊。點擊 Join 將隨機分配玩家的門風，Add robot 可加入自動摸切機器人，待四家到齊即開始遊戲。

吃碰槓牌及立直牌以 `*` 代替旋轉90度，
`*` 表吃、碰；`**` 表大明槓；`***`表加槓；皆無則表暗槓。

! 榮和平和計30符
! 不計流局滿貫
! 四張相同牌可算作雙碰聽
! 不計食替
! 不計四風連打
! 不計九種九牌
! 不計兩家、三家和(以風位順序優先)
! 不計四家立直流局

* 請勿同時多人點擊 Join 及 Add robot 按鈕
"""
game_illustration_embed = discord.Embed(
    description = DESCRIPTION
)

def get_emoji(ctx:commands.Context, name):
    for emoji in ctx.guild.emojis:
        if emoji.name == name:
            return emoji
    return ""
"""
    Classes connecting to the UI terminal
"""

class Performer:
    def __init__(self):
        pass 
    def draw_all(self):
        pass 
    def refresh_river(self):
        pass 
    def refresh_tehai(self, player):
        pass 
    def print(self, msg: str):
        print(msg)

class GetPlayerAction: # 自摸、加暗槓
    def __init__(self, action_list: list[str]):
        self.bool_list: list[bool]
        
        self.bool_list = list(map(bool, map(int, input(f"{str(action_list)}>>>").split())))

class GetPlayerDatsuhai: # 打牌
    def __init__(self):
        self.number: int # 0 for 摸打, 1~13 for 手牌左到右

        self.number = int(input("datsuhai number>>>"))

class GetPlayersRonAction:
    def __init__(self, players: list) -> None:
        self.bool_list: list[bool]
        self.bool_list =  [False]*len(players)

class GetPlayerInput:
    def __init__(self) -> None:
        self.boolean: bool
    
    def input(self, msg = ""):
        return input(msg)

class GetPlayersMinpaiAction: # 吃、碰、明槓
    def __init__(self, actions: list[tuple]) -> None: # tuple[player, action_type]
        self.bool_list: list[bool]

        self.bool_list = [False]*len(actions)

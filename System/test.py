from pai import get_tenpai_list, create_pai_list

s = "1112223334555m"
pai_list = create_pai_list(s)

print(" ".join(map(lambda i: i.__str__(), get_tenpai_list(pai_list))))

del_pos_list = [1,2,5]
hansuu_yaku_list = [0,1,2,3,4,5,6,7]
del_pos_list.sort()
del_pos_list.reverse()
length = len(del_pos_list)
for i in del_pos_list:
    del hansuu_yaku_list[i]
print(hansuu_yaku_list)
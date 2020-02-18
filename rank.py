from collections import defaultdict
import json
from math import floor

num_val = defaultdict(int)

for num in range(1,15):
    if num == 10:
        char = 'T'
    elif num == 11:
        char = 'J'
    elif num == 12:
        char = 'Q'
    elif num == 13:
        char = 'K'
    elif num == 14:
        char = 'A'
    else:
        char = str(num)
    
    num_val[char] = num

with open('data.json') as json_file:
    count_dict = json.load(json_file)

hands_list = []

for hands in count_dict:
    hands_list.append([hands, count_dict[hands]['%'], 0])

for i in hands_list:
    factor = 1 + num_val[i[0][0]] / 100
    i[2] = round(min(1, i[1] * factor) * 100, 2)

hands_list.sort(key=lambda x: -x[2])


with open('rank_pairs.txt', 'w') as rank_pair, open('rank.txt', 'w') as rank:
    for hands in hands_list:
        data = str(hands[0]) + ' ' + str(hands[1]) + ' ' + str(hands[2]) + '\n'
        if hands[0][0] == hands[0][1]:
            rank_pair.write(data)
        else:
            rank.write(data)


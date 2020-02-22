from collections import defaultdict
import json
from math import floor

num_val = defaultdict(int)

with open('data_2.json') as json_file:
    count_dict = json.load(json_file)

hands_list = []

for hands in count_dict:
    hands_list.append([hands, count_dict[hands]['%']])

hands_list.sort(key=lambda x: -x[1])


with open('rank_pairs.txt', 'w') as rank_pair, open('rank.txt', 'w') as rank:
    for hands in hands_list:
        data = str(hands[0]) + ' ' + str(hands[1]) + '\n'
        if hands[0][0] == hands[0][1]:
            rank_pair.write(data)
        else:
            rank.write(data)


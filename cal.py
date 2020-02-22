from collections import defaultdict
import random
import json
import os.path

class Poker:
    def __init__(self, val, suit, num):
        self.value = val
        self.suit = suit
        self.num_value = num

class Player:
    def __init__(self):
        self.card_1 = None
        self.card_2 = None

class Stack:
    def __init__(self):
        self.cards = self.initiate_stack()
    
    def initiate_stack(self):

        stack = []
        val_dict = {2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'T', 11:'J', 12:'Q', 13:'K', 14:'A'}
        for n in range(2,15):
            for s in ('h','c','s','d'):
                card = Poker(val_dict[n], s, n)
                stack.append(card)
        return stack
    
    def shuffle(self):
        random.shuffle(self.cards)

class Table:
    def __init__(self, num_player):
        self.seats = [Player() for _ in range(num_player)]
        self.board = []
        self.stack = Stack()
        self.num_player = num_player
        
    def clean(self):

        # clean hands
        for player in self.seats:
            self.stack.cards.append(player.card_1)
            player.card_1 = None 
            self.stack.cards.append(player.card_2)
            player.card_2 = None

        # clean board
        for _ in range(len(self.board)):
            self.stack.cards.append(self.board.pop())
        
        self.stack.shuffle()

class Result:
    def __init__(self, is_sd, is_dsd, is_fd, cards, hands, res, sd, fd):
        self.is_sd = is_sd
        self.is_dsd = is_dsd
        self.is_fd = is_fd
        self.cards = cards
        self.hands = hands 
        self.ranked_res = res
        self.showed_res = res+sd+fd
        self.score = 0
    
    def print(self):
        for c in self.cards:
            print(c.value, c.suit, ' ', end='')
        print('  ', self.ranked_res, end = '                ')
        for h in self.hands:
            print(h.value, h.suit, ' ', end='')
        print('    ', self.score)

class Judger:

    def __init__(self):
        self.all_res = []
        self.board = None
        self.valid_fd = True
        self.score_map = {
            'FS': 16,
            'FOK': 15,
            'FH': 14,
            'FL': 13,
            'STR': 12,
            'FD/DSD': 11,
            'SET': 10,
            'TP': 9,
            'FD/SD': 8,
            'P': 7,
            'FD': 6,
            'DSD': 5,
            'SD': 2,
            'NA': 0
        }
    
    def is_real_fd(self):

        f = set()
        suit = None
        suit_count = 0

        for c in self.board:
            if c.suit in f:
                suit = c.suit
            else:
                f.add(c.suit)
        
        if len(f) == 3:
            return False
        
        for res in self.all_res:
            for c in res.cards:
                if c.suit == suit:
                    suit_count += 1
                if suit_count > 5:
                    return False 
        
        return True
        
    
    def score_allocate(self):

        self.valid_fd = self.is_real_fd()
        code = 'NA'

        for idv_res in self.all_res:

            # fd
            if idv_res.is_fd and self.valid_fd:
                if idv_res.is_sd:
                    code = 'FD/SD'
                elif idv_res.is_dsd:
                    code = 'FD/DSD'
                else:
                    code = idv_res.ranked_res if idv_res.ranked_res != 'NA' else 'FD'
            elif idv_res.is_sd: # not fd but sd
                code = idv_res.ranked_res if idv_res.ranked_res != 'NA' else 'SD'
            elif idv_res.is_dsd: # only dsd
                code = idv_res.ranked_res if idv_res.ranked_res != 'NA' else 'DSD'
            else: # not fd, sd, dsd
                code = idv_res.ranked_res
            
            idv_res.score = self.score_map[code]
            idv_res.ranked_res = code
    
    def make_sum(self, cards):
        s = 0
        for c in cards:
            s += c.num_value
        return s
    
    def find_max(self, cards):
        m = -1
        for c in cards:
            if c.num_value > m:
                m = c.num_value
        return m
    
    def find_top_pair(self, cards):
        cur_p = -1
        s = set()
        for c in cards:
            if c.num_value in s and c.num_value > cur_p:
                cur_p = c.num_value
            else:
                s.add(c.num_value)
        return cur_p
    
    def find_second_pair(self, cards, top_pair):
        cur_p = -1
        s = set()
        for c in cards:
            if c.num_value in s and c.num_value > cur_p:
                cur_p = c.num_value
            elif c.num_value != top_pair:
                s.add(c.num_value)
        return cur_p

    def sum_comparitor(self, candidates):

        winners = []
        max_val = -1
        
        for c in candidates:
            s = self.make_sum(c.hands)
            if s > max_val:
                max_val = s 
                winners = [c]
            elif s == max_val:
                winners.append(c)

        return winners
    
    def max_comparitor(self, candidates):

        winners = []
        max_val = -1

        for c in candidates:
            m = self.find_max(c.hands)
            # print('cur_max', max_val, 'find max', m)
            if m > max_val:
                winners = [c]
                max_val = m
            elif m == max_val:
                winners.append(c)
        return winners
    
    def two_pair_comparitor(self, candidates):

        cur_p = -1
        winners = []

        for c in candidates:
            c_p = self.find_top_pair(c.cards)
            if c_p > cur_p:
                cur_p = c_p
                winners = [c]
            elif c_p == cur_p:
                winners.append(c)
        
        if len(winners) > 1: # same top pair
            cur_s_p = -1
            for w in winners:
                csp = self.find_second_pair(w.cards, cur_p)
                if csp > cur_s_p:
                    cur_s_p = csp 
                    winners = [w]
                elif csp == cur_s_p:
                    winners.append(w)
            
            if len(winners) > 1: # same second pair
                
                max_val = -1
                tmp_w = []

                for w in winners:
                    cm = self.find_max(w.hands)
                    if cm > max_val:
                        max_val = cm 
                        tmp_w = [w]
                    elif cm == max_val:
                        tmp_w.append(w)

                winners = tmp_w
        
        return winners

    
    def pair_comparitor(self, candidates):

        cur_p = -1
        winners = []

        for c in candidates:
            c_p = self.find_top_pair(c.cards)
            if c_p > cur_p:
                cur_p = c_p
                winners = [c]
            elif c_p == cur_p:
                winners.append(c)
        
        if len(winners) > 1:
            # print(len(winners),'players have the same pair')
            winners = self.max_comparitor(winners)
            if len(winners) > 1:
                # print(len(winners), 'players have the same high card')
                m = -1
                win = []
                for w in winners:
                    tmp = w.hands[0].num_value + w.hands[1].num_value
                    if tmp > m:
                        m = tmp
                        win = [w]
                    elif tmp == m:
                        win.append(w)
                winners = win

        return winners

    def find_winner(self):

        self.score_allocate()

        self.all_res.sort(key=lambda x: x.score)

        top = self.all_res[-1].score
        candidates = []

        for r in self.all_res:
            if r.score == top:
                candidates.append(r)
        
        # print('# of candidates:', len(candidates))
        if len(candidates) == 1:
            return candidates

        if top in (6,8,11,15): # FDs + FOK
            # print('FD, FK')
            return [self.all_res[-1]]
        elif top in (7,9): # P or TP
            # print('P/TP')
            return self.pair_comparitor(candidates)
        elif top == 14: # FH
            # print('FH')
            return self.sum_comparitor(candidates)
        else: 
            # print('Others')
            return self.max_comparitor(candidates)
            
def distribute_cards(cur_table):
    cur_table.stack.shuffle()

    for player in cur_table.seats:
        player.card_1 = cur_table.stack.cards.pop()
    
    for player in cur_table.seats:
        player.card_2 = cur_table.stack.cards.pop()

    for _ in range(3):
        cur_table.board.append(cur_table.stack.cards.pop())

    # for p in cur_table.seats:
    #     print(p.card_1.value, p.card_1.suit, p.card_2.value, p.card_2.suit)
    
    # for card in cur_table.board:
    #     print(card.value, card.suit)

def is_straight(sum_diff):
    return sum_diff == 4

def is_straight_draw(cards, sum_diff, length):
    if length == 4:
        return sum_diff == 4
    elif length == 5:
        first_two_diff = cards[1].num_value - cards[0].num_value
        last_two_diff = cards[-1].num_value - cards[-2].num_value
        return sum_diff - first_two_diff == 4 or sum_diff - last_two_diff == 4 
    else:
        return False

def is_double_straight_draw(cards, sum_diff, length):
    if length == 4:
        return sum_diff == 3
    elif length == 5:
        first_two_diff = cards[1].num_value - cards[0].num_value
        last_two_diff = cards[-1].num_value - cards[-2].num_value
        return sum_diff - first_two_diff == 3 or sum_diff - last_two_diff == 3
    else:
        return False

def is_flush_draw(count_suit):
    for key in count_suit:
        if count_suit[key] == 4:
            return True 
    return False

def raw_count(cards, hands):
    cards.sort(key=lambda x: x.num_value)
    count_val = defaultdict(int)
    count_suit = defaultdict(int)
    sum_diff = 0
    is_sd = False
    is_fd = False
    is_dsd = False

    res = "NA"
    sd = ""
    fd = ""

    for i in range(len(cards)):
        count_val[cards[i].num_value] += 1
        count_suit[cards[i].suit] += 1
        if i < len(cards)-1:
            sum_diff += cards[i+1].num_value - cards[i].num_value
    
    if len(count_val) == 2:
        res = "FH"
    elif len(count_val) == 3:
        for key in count_val:
            if count_val[key] == 3:
                res = "SET"
            elif count_val[key] == 2:
                res = "TP"
    elif len(count_val) == 4: # Pairs

        # draw place holder
        res = "P"
    elif is_straight(sum_diff):
        if len(count_suit) == 1:
            res = "FS"
        else:
            res = "STR"
    elif is_straight_draw(cards, sum_diff, len(count_val)):
        sd = " w/ Straight Draw"
        is_sd = True
    elif is_double_straight_draw(cards, sum_diff, len(count_val)):
        sd = " w/ Double Straight Draw"
        is_dsd = True
    elif len(count_suit) == 1:
        res = "FL"

    if is_flush_draw(count_suit):
        fd = " w/ Flush Draw"
        is_fd = True
    
    # print(hands[0].value, hands[1].value)

    return Result(is_sd, is_dsd, is_fd, cards, hands, res, sd, fd)

def define_type(hands):
    tp = str(hands[0].value) + str(hands[1].value)
    if tp[0] != tp[1]:
        if hands[0].suit == hands[1].suit:
            tp += 's'
        else:
            tp += 'o'
    return tp

if __name__ == '__main__':

    cur_table = Table(7)

    if not os.path.isfile('data_2.json'):
        count_dict = defaultdict(lambda: defaultdict(int))
    else:
        with open('data_2.json') as json_file:
            count_dict = json.load(json_file)

    # test_cards = [
    #     Poker('T','h',10),
    #     Poker('J','h',11),
    #     Poker('Q','h',12),
    # ]

    # test_hands = [
    #     Poker('9','h',9),
    #     Poker('K','s',13)
    # ]

    # print(raw_count(test_cards+test_hands, test_hands))

    for _ in range(4000000):

        # print()

        distribute_cards(cur_table)
        judger = Judger()

        for player in cur_table.seats:

            card_suit = "s"
            hands = [player.card_1, player.card_2]
            hands.sort(key=lambda x: -x.num_value)

            typ = define_type(hands)
            if typ not in count_dict:
                count_dict[typ] = {'Total': 1, 'Hits': 0, '%': 0}
            else:
                count_dict[typ]['Total'] += 1

            res = raw_count(hands+cur_table.board, hands)
            judger.all_res.append(res)
            judger.board = cur_table.board

        winners = judger.find_winner()

        # test_set = set(['FH', 'STR', 'FL', 'FS'])

        # for res in judger.all_res:
        #     # if res.ranked_res in test_set:
        #     res.print()
        
        for res in winners:
            # print('Winners are: ', end=' ')
            # res.print()
            typ = define_type(res.hands)


            count_dict[typ]['Hits'] += 1
            count_dict[typ]['%'] = round(count_dict[typ]['Hits'] / count_dict[typ]['Total'], 4)

        cur_table.clean()
    
    with open('data_2.json', 'w') as outfile:
        json.dump(count_dict, outfile)

    # print(len(count_dict))
    print("Done!")

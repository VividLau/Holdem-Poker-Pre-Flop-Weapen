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

def print_cards(cards, res, hands):
    for c in cards:
        print(c.value, c.suit, ' ', end='')
    print(res, end = ' ')
    for h in hands:
        print(h.value, h.suit, ' ', end='')
    print()

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

    res = "Nothing"
    sd = ""
    fd = ""

    for i in range(len(cards)):
        count_val[cards[i].num_value] += 1
        count_suit[cards[i].suit] += 1
        if i < len(cards)-1:
            sum_diff += cards[i+1].num_value - cards[i].num_value
    
    if len(count_val) == 2:
        res = "Four of kinds / Full house"
    elif len(count_val) == 3:
        for key in count_val:
            if count_val[key] == 3:
                res = "Set"
            elif count_val[key] == 2:
                res = "Two Pairs"
    elif len(count_val) == 4: # Pairs

        # draw place holder
        res = "Pairs"
    elif is_straight(sum_diff):
        if len(count_suit) == 1:
            res = "Flush Straight"
        else:
            res = "Straight"
    elif is_straight_draw(cards, sum_diff, len(count_val)):
        sd = " w/ Straight Draw"
    elif is_double_straight_draw(cards, sum_diff, len(count_val)):
        sd = " w/ Double Straight Draw"
    elif len(count_suit) == 1:
        res = "Flush"


    if is_flush_draw(count_suit):
        fd = " w/ Flush Draw"
    

    # print(hands[0].value, hands[1].value)

    return [res+sd+fd, cards]

if __name__ == '__main__':

    cur_table = Table(6)

    # if not os.path.isfile('data.json'):
    #     count_dict = defaultdict(lambda: defaultdict(int))
    # else:
    #     with open('data.json') as json_file:
    #         count_dict = json.load(json_file)

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

    for _ in range(500):
        distribute_cards(cur_table)
        for player in cur_table.seats:

            card_suit = "s"
            hands = [player.card_1, player.card_2]
            hands.sort(key=lambda x: -x.num_value)

            res, cards = raw_count(hands+cur_table.board, hands)

            if res == "Set": print_cards(cards, res, hands)
            # print_cards(cards, res, hands)

            # if hands[0].suit != hands[1].suit:
            #     card_suit = "o"
            
            # cur_type = hands[0].value+hands[1].value+card_suit
            # count_dict[cur_type]['Total'] += 1

            # if res != "Nothing":
            #     count_dict[cur_type]['Hit'] += 1

            # count_dict[cur_type]['%'] = round(count_dict[cur_type]['Hit'] / count_dict[cur_type]['Total'], 4)

        cur_table.clean()
    
    # with open('data.json', 'w') as outfile:
    #     json.dump(count_dict, outfile)

    # print(len(count_dict))
    print("Done!")

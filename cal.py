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

def print_cards(cards, res):
    for c in cards:
        print(c.value, c.suit, ' ', end='')
    print(res)

def is_straight(cards):
    for i in range(1, len(cards)):
        if cards[i].num_value - cards[i-1].num_value != 1:
            return False 
    return True

def is_straight_draw(cards):
    if cards[0].num_value == 14 or cards[-1].num_value == 14:
        return False
    for i in range(1, 4):
        if cards[i].num_value - cards[i-1].num_value != 1:
            return False
    if cards[1].num_value - cards[0].num_value != 1 and cards[-1].num_value - cards[-2].num_value != -1:
        return False 
    
    return True
    
def raw_count(cards, hands):
    cards.sort(key=lambda x: x.num_value)
    count_val = defaultdict(int)
    count_suit = defaultdict(int)

    res = "Nothing"

    for c in cards:
        count_val[c.num_value] += 1
        count_suit[c.suit] += 1
    
    if len(count_val) == 2:
        res = "Four of kinds / Full house"
    elif len(count_val) == 3:
        for key in count_val:
            if count_val[key] == 3:
                res = "Set"
            elif count_val[key] == 2:
                res = "Two Pairs"
    elif len(count_val) == 4:
        for key in count_val:
            if count_val[key] == 2 and cards[-1].num_value == key and (key - hands[1].num_value <= 2 or hands[1].num_value >= 10):
                res = "Top Pair, High Kicker"
    elif is_straight(cards):
        res = "Straight"
    elif is_straight_draw(cards):
        res = "Straight Draw"
    elif len(count_suit) == 1:
        res = "Flush"
    elif len(count_suit) == 2:
        for key in count_suit:
            if count_suit[key] == 4:
                res = "Flush Draw"
    else:
        pass

    # print(hands[0].value, hands[1].value)
    # print_cards(cards, res)

    return res

if __name__ == '__main__':

    cur_table = Table(6)

    if not os.path.isfile('data.json'):
        count_dict = defaultdict(lambda: defaultdict(int))
    else:
        with open('data.json') as json_file:
            count_dict = json.load(json_file)

    for _ in range(5000000):
        distribute_cards(cur_table)
        for player in cur_table.seats:

            card_suit = "s"
            hands = [player.card_1, player.card_2]
            hands.sort(key=lambda x: -x.num_value)

            res = raw_count(hands+cur_table.board, hands)
            if hands[0].suit != hands[1].suit:
                card_suit = "o"
            
            cur_type = hands[0].value+hands[1].value+card_suit
            count_dict[cur_type]['Total'] += 1

            if res != "Nothing":
                count_dict[cur_type]['Hit'] += 1

            count_dict[cur_type]['%'] = round(count_dict[cur_type]['Hit'] / count_dict[cur_type]['Total'], 4)

        cur_table.clean()
    
    with open('data.json', 'w') as outfile:
        json.dump(count_dict, outfile)

    # print(len(count_dict))
    print("Done!")

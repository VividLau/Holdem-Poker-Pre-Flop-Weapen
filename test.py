import random
from collections import defaultdict

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
    def __init__(self, n1, s1, n2, s2):
        self.n1 = n1
        self.s1 = s1 
        self.n2 = n2 
        self.s2 = s2
        self.cards = self.initiate_stack()
    
    def initiate_stack(self):

        stack = []
        val_dict = {2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'T', 11:'J', 12:'Q', 13:'K', 14:'A'}
        for n in range(2,15):
            for s in ('h','c','s','d'):
                if (self.n1 == n and self.s1 == s) or (self.n2 == n and self.s2 == s):
                    continue
                card = Poker(val_dict[n], s, n)
                stack.append(card)
        print(len(stack))
        return stack
    
    def shuffle(self):
        random.shuffle(self.cards)

class Table:
    def __init__(self, num_player, n1, s1, n2, s2):
        self.seats = [Player() for _ in range(num_player)]
        self.board = []
        self.stack = Stack(n1, s1, n2, s2)
        self.num_player = num_player
        
    def clean(self):

        # clean hands
        for player in self.seats:
            if player.card_1.value != '2' and player.card_1.suit != 's':
                self.stack.cards.append(player.card_1)
                player.card_1 = None 
                self.stack.cards.append(player.card_2)
                player.card_2 = None

        # clean board
        for _ in range(len(self.board)):
            self.stack.cards.append(self.board.pop())

def distribute_cards(cur_table):
    cur_table.stack.shuffle()

    for player in cur_table.seats:
        if player.card_1 == None:
            player.card_1 = cur_table.stack.cards.pop()
    
    for player in cur_table.seats:
        if player.card_2 == None:
            player.card_2 = cur_table.stack.cards.pop()

    for _ in range(3):
        cur_table.board.append(cur_table.stack.cards.pop())

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
            if count_val[key] == 2 and cards[-1].num_value == key and key - hands[1].num_value <= 2:
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

    if hands[0].value == '2' and hands[0].value == '2':
        # print(hands[0].value, hands[1].value)
        print_cards(cards, res)

    return res

if __name__ == '__main__':

    cur_table = Table(6, 2, 's', 2, 'd')
    hit = 0
    for _ in range(10000):
        cur_table.seats[0].card_1 = Poker('2','s',2)
        cur_table.seats[0].card_2 = Poker('2','d',2)
        distribute_cards(cur_table)
        for player in cur_table.seats:
            hands = [player.card_1, player.card_2]
            hands.sort(key=lambda x: -x.num_value)
            res = raw_count(hands+cur_table.board, hands)

            if hands[0] == cur_table.seats[0].card_1 and res != "Nothing":
                hit += 1

        cur_table.clean()
    
    print(hit)

# -*- encoding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class PokerCard(object):

    SUITS = ['Heart', 'Spade', 'Diamond', 'Club']
    RANK_SYMBOLS = ['Small-A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def __init__(self, suit, rank):
        """
        Standard French playing card except jokers.
        Ace has the highest rank, which is 14
        """
        if suit not in self.SUITS:
            raise Exception("Given suit %s is not supported in this kind of playing card." % suit)
        if rank < 1 or rank > 14:
            # consider Ace can be 1 or 14
            raise Exception("Given rank %d is not supported in this kind of playing card." % rank)

        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return "%s %s" % (self.suit, self.rank_symbol())

    def __cmp__(self, other):
        return cmp(self.rank, other.rank)

    def rank_symbol(self):
        return self.RANK_SYMBOLS[self.rank - 1]


class CardDeckController(object):

    def __init__(self):
        """
        A standard card deck contains 54 playing cards. 4 suits by 13 ranks and 2 jokers.
        In this case, we don't consider jokers.
        """
        self._card_pool = []
        self.draw_deck = []

    def add_card_deck(self, batch=1):
        for i in range(batch):
            new_card_deck = []
            for rank in range(2, 15):
                for suit in ['Heart', 'Spade', 'Diamond', 'Club']:
                    new_card_deck.append(PokerCard(suit, rank))
            self._card_pool.extend(new_card_deck)

    def size(self):
        return len(self._card_pool)

    def remain_size(self):
        return len(self.draw_deck)

    def shuffle(self):
        import random
        random.shuffle(self.draw_deck)

    def initialize(self):
        self.draw_deck = self._card_pool[:]
        self.shuffle()

    def deal(self):
        if len(self.draw_deck) < 1:
            raise Exception("The draw deck is empty for now.")
        return self.draw_deck.pop(0)

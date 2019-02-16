# -*- encoding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from card_models import CardDeckController


class User(object):

    def __init__(self, name, money):
        self.name = name
        self.money = money

    def __repr__(self):
        return self.name


class Player(object):

    def __init__(self, username, money):
        self.username = username
        self.money = money
        self.host = False

        self.game = None
        self.game_pos = None
        self.first_hole = None
        self.second_hole = None
        self.cur_bet = 0
        self.best_hand_value = None
        self.status = 'init'  # 'init', 'in game', 'all in', 'out game'

    def info(self):
        d = {}
        d['name'] = self.print_name()
        d['money'] = self.money
        d['host'] = self.host
        d['game_pos'] = self.game_pos
        d['first_hole'] = str(self.first_hole)
        d['second_hole'] = str(self.second_hole)
        d['cur_bet'] = self.cur_bet
        d['best_hand_value'] = str(self.best_hand_value)
        d['status'] = self.status
        return d

    def print_name(self):
        return "Player%d-%s" % (self.game_pos, self.username)

    def print_holes(self):
        return "  <%s>  <%s>  " % (self.first_hole, self.second_hole)

    def update_best_hand_value(self):
        from hand_value import HandValue
        holes = [self.first_hole, self.second_hole]
        community_cards = self.game.community_cards
        self.best_hand_value = HandValue(holes + community_cards)

    def clear(self):
        self.first_hole = None
        self.second_hole = None
        self.cur_bet = 0
        self.best_hand_value = None
        self.status = 'in game'

    def bet(self, amount):
        amount = int(amount)
        if amount > self.money:
            print "------", type(amount)
            print "------", amount
            print "------", type(self.money)
            print "------", self.money
            raise Exception("Don't have enough money")
        self.money -= amount
        self.game.pot += amount
        self.cur_bet += amount

    def bet_to(self, amount):
        self.bet(amount - self.cur_bet)

    def check(self):
        pass

    def call(self):
        self.bet_to(self.game.highest_bet)

    def raise_bet(self, amount):
        self.bet(amount)
        self.game.highest_bet = self.cur_bet

    def allin(self):
        self.status = 'all in'
        self.bet(self.money)

    def fold(self):
        self.status = 'out game'


class Game(object):

    def __init__(self):
        self.pot = 0
        self.community_cards = []
        self.highest_bet = 0
        self.players = []
        self.pos_button = 0
        self.pos_small_blind = 1
        self.pos_big_blind = 2
        self.active_player_pos = -1
        self.status = 'init'  # 'init', 'new game', 'pre flop', 'flop', 'turn', 'river', 'showdown'
        self.log = ['Welcome to Texas Hold\'em Poker Game v1.0-alpha']
        self.action_num = 0

        self.card_deck_controller = CardDeckController()
        self.card_deck_controller.add_card_deck()

    def info(self):
        d = {}
        d['pot'] = self.pot
        d['community_cards'] = map(str, self.community_cards)
        d['highest_bet'] = self.highest_bet
        d['players'] = [x.info() for x in self.players]
        d['pos_button'] = self.pos_button
        d['pos_small_blind'] = self.pos_small_blind
        d['pos_big_blind'] = self.pos_big_blind
        d['active_player_pos'] = self.active_player_pos
        d['status'] = self.status
        d['log'] = self.log
        return d

    def add_player(self, player):
        self.players.append(player)
        player.game_pos = len(self.players)
        player.game = self

    def print_community_cards(self):
        if len(self.community_cards) == 0:
            return " "
        s = ">  <".join(map(str, self.community_cards))
        return "  <%s>  " % s

    def new_game(self):
        self.pot = 0
        self.community_cards = []
        self.card_deck_controller.initialize()
        for player in self.players:
            player.clear()

        self.pos_button = (self.pos_button + 1) % len(self.players)
        self.pos_small_blind = (self.pos_small_blind + 1) % len(self.players)
        self.pos_big_blind = (self.pos_big_blind + 1) % len(self.players)
        self.status = 'new game'

    def deal(self):
        n = len(self.players)

        # round-1
        for i in range(self.pos_button, self.pos_button + n):
            j = i % n
            if self.players[j].first_hole is not None or self.players[j].second_hole is not None:
                raise Exception("Didn't clear players' holes")
            self.players[j].first_hole = self.card_deck_controller.deal()

        # round-2
        for i in range(self.pos_button, self.pos_button + n):
            j = i % n
            self.players[j].second_hole = self.card_deck_controller.deal()

    def pre_flop(self):
        self.status = 'pre flop'

    def flop(self):
        self.community_cards.append(self.card_deck_controller.deal())
        self.community_cards.append(self.card_deck_controller.deal())
        self.community_cards.append(self.card_deck_controller.deal())
        for player in self.players:
            player.update_best_hand_value()
        self.status = 'flop'

    def turn(self):
        self.community_cards.append(self.card_deck_controller.deal())
        for player in self.players:
            player.update_best_hand_value()
        self.status = 'turn'

    def river(self):
        self.community_cards.append(self.card_deck_controller.deal())
        for player in self.players:
            player.update_best_hand_value()
        self.status = 'river'

    def showdown(self):
        alive_players = filter(lambda x: x.status == 'in game' or x.status == 'all in', self.players)
        win_hand_value = max([x.best_hand_value for x in alive_players])
        winners = []
        for player in self.players:
            if player.status == 'in game' or player.status == 'all in':
                if player.best_hand_value == win_hand_value:
                    winners.append(player)
        self.status = 'showdown'
        return winners

    def checkout(self, winners):
        num_winners = len(winners)
        prize = self.pot / num_winners
        for winner in winners:
            winner.money += prize
        self.pot = 0

        return prize

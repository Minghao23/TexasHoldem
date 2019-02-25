# -*- encoding:utf-8 -*-
from card_models import CardDeckController

import sys

reload(sys)
sys.setdefaultencoding('utf-8')


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
        self.pos = None
        self.first_hole = None
        self.second_hole = None
        self.cur_bet = 0
        self.best_hand_value = None
        self.status = 'init'  # 'init', 'in game', 'all in', 'out game'， 'offline'

    def info(self):
        d = {}
        d['name'] = self.print_name()
        d['money'] = self.money
        d['host'] = self.host
        d['pos'] = self.pos
        d['first_hole'] = str(self.first_hole)
        d['second_hole'] = str(self.second_hole)
        d['cur_bet'] = self.cur_bet
        d['best_hand_value'] = str(self.best_hand_value)
        d['status'] = self.status
        return d

    def print_name(self):
        return "Player%d-%s" % (self.pos + 1, self.username)

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
        if amount < self.game.blind_money:
            raise Exception("Must bet more than blind money %d" % self.game.blind_money)
        if amount > self.money:
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
        self.game.alive_players_indices.remove(self.pos)
        self.status = 'out game'


class Game(object):

    def __init__(self, blind_money=2, num_players=8, bet_limit=50):
        self.blind_money = blind_money
        self.num_players = num_players
        self.bet_limit = bet_limit  # don't consider upper limitation for now

        self.pot = 0
        self.community_cards = []
        self.highest_bet = 0
        self.players = [None for _ in range(num_players)]
        self.pos_button = -1
        self.pos_small_blind = -1
        self.pos_big_blind = -1
        self.active_player_pos = -1
        self.status = 'init'  # 'init', 'new game', 'pre flop', 'flop', 'turn', 'river', 'showdown'
        self.log = ['Welcome to Texas Hold\'em Poker Game v1.0-alpha']
        self.next_stage_flag = False
        self.alive_players_indices = []

        self.card_deck_controller = CardDeckController()
        self.card_deck_controller.add_card_deck()

    def info(self):
        d = {}
        d['pot'] = self.pot
        d['community_cards'] = map(str, self.community_cards)
        d['highest_bet'] = self.highest_bet
        d['players'] = [x.info() if x is not None else x for x in self.players]
        d['pos_button'] = self.pos_button
        d['pos_small_blind'] = self.pos_small_blind
        d['pos_big_blind'] = self.pos_big_blind
        d['active_player_pos'] = self.active_player_pos
        d['status'] = self.status
        d['log'] = self.log
        return d

    def add_player(self, player):

        # find a vacant position
        new_pos = 0
        while self.players[new_pos] is not None:
            new_pos += 1

        if new_pos >= self.num_players:
            raise Exception("Can't add players any more")

        player.game = self
        player.pos = new_pos
        self.players[new_pos] = player

        return player.pos

    def print_community_cards(self):
        if len(self.community_cards) == 0:
            return " "
        s = ">  <".join(map(str, self.community_cards))
        return "  <%s>  " % s

    def remove_offline_players(self):
        for i in range(len(self.players)):
            if self.players[i] is not None and self.players[i].status == 'offline':
                self.players[i] = None
                self.alive_players_indices.remove(i)

    def find_next_active_pos(self, pos):
        next_pos = (pos + 1) % self.num_players
        while self.players[next_pos] is None or self.players[next_pos].status != 'in game':
            next_pos = (next_pos + 1) % self.num_players
        return next_pos

    def new_game(self):
        self.pot = 0
        self.community_cards = []
        self.highest_bet = 0
        self.card_deck_controller.initialize()

        # initialize players
        self.alive_players_indices = []
        self.remove_offline_players()
        for player in self.players:
            if player is not None:
                player.clear()
                self.alive_players_indices.append(player.pos)

        self.pos_button = self.find_next_active_pos(self.pos_button)
        self.pos_small_blind = self.find_next_active_pos(self.pos_button)
        self.pos_big_blind = self.find_next_active_pos(self.pos_small_blind)
        self.active_player_pos = -1
        self.next_stage_flag = False
        self.status = 'new game'

    def deal(self):
        # round-1
        for i in range(self.pos_button, self.pos_button + self.num_players):
            player = self.players[i % self.num_players]
            if player is not None:
                if player.first_hole is not None or player.second_hole is not None:
                    raise Exception("Didn't clear players' holes")
                player.first_hole = self.card_deck_controller.deal()

        # round-2
        for i in range(self.pos_button, self.pos_button + self.num_players):
            player = self.players[i % self.num_players]
            if player is not None:
                player.first_hole = self.card_deck_controller.deal()

    def pre_flop(self):
        self.status = 'pre flop'

    def flop(self):
        self.community_cards.append(self.card_deck_controller.deal())
        self.community_cards.append(self.card_deck_controller.deal())
        self.community_cards.append(self.card_deck_controller.deal())
        for pos in self.alive_players_indices:
            self.players[pos].update_best_hand_value()
        self.status = 'flop'

    def turn(self):
        self.community_cards.append(self.card_deck_controller.deal())
        for pos in self.alive_players_indices:
            self.players[pos].update_best_hand_value()
        self.status = 'turn'

    def river(self):
        self.community_cards.append(self.card_deck_controller.deal())
        for pos in self.alive_players_indices:
            self.players[pos].update_best_hand_value()
        self.status = 'river'

    def showdown(self):
        win_hand_value = max([self.players[pos].best_hand_value for pos in self.alive_players_indices])
        winners = []
        for pos in self.alive_players_indices:
            if self.players[pos].best_hand_value == win_hand_value:
                winners.append(self.players[pos])
        self.status = 'showdown'
        return winners

    def checkout(self, winners):
        # TODO solve all in players, add side pot
        num_winners = len(winners)
        prize = self.pot / num_winners
        for winner in winners:
            winner.money += prize

        return prize

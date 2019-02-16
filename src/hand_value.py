# -*- encoding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from card_models import PokerCard


class HandValue(object):

    HAND_VALUES = ['Royal Flush',
                   'Straight Flush',
                   'Four of a Kind',
                   'Full House',
                   'Flush',
                   'Straight',
                   'Three of a Kind',
                   'Two Pairs',
                   'Pair',
                   'High Card']

    def __init__(self, cards):
        if len(cards) < 5:
            raise Exception("HandValue must depend on more than 5 cards")
        self.name, self.cards = find_best_hand_value(cards)

    def __repr__(self):
        s = ">  <".join(map(str, self.cards))
        return "%s  <%s>  " % (self.name, s)

    def __cmp__(self, other):
        if self.HAND_VALUES.index(self.name) < self.HAND_VALUES.index(other.name):
            return 1
        elif self.HAND_VALUES.index(self.name) > self.HAND_VALUES.index(other.name):
            return -1
        else:
            if self.name == 'Royal Flush':
                return 0
            elif self.name == 'Straight Flush':
                # avoid comparing the Straight started with Ace
                return cmp(self.cards[4], other.cards[4])
            elif self.name == 'Four of a Kind':
                return cmp(self.cards[0], other.cards[0])
            elif self.name == 'Full House':
                return cmp(self.cards[0], other.cards[0])
            elif self.name == 'Flush':
                return cmp_high_card(self.cards, other.cards)
            elif self.name == 'Straight':
                return cmp(self.cards[4], other.cards[4])
            elif self.name == 'Three of a Kind':
                return cmp(self.cards[0], other.cards[0])
            elif self.name == 'Two Pairs':
                if cmp(self.cards[0], other.cards[0]) != 0:
                    return cmp(self.cards[0], other.cards[0])
                elif cmp(self.cards[2], other.cards[2]) != 0:
                    return cmp(self.cards[2], other.cards[2])
                else:
                    return cmp(self.cards[4], other.cards[4])
            elif self.name == 'Pair':
                if cmp(self.cards[0], other.cards[0]) != 0:
                    return cmp(self.cards[0], other.cards[0])
                else:
                    return cmp_high_card(self.cards, other.cards)
            elif self.name == 'High Card':
                return cmp_high_card(self.cards, other.cards)
            else:
                raise Exception("Can't compare")


def find_best_hand_value(cards):
    n = len(cards)
    if n < 5:
        raise Exception("Number of cards must not less than 5")
    result_hand_values = {}  # store all possible hand value and corresponding cards

    # find high card
    sorted_cards = sorted(cards, reverse=True)
    result_hand_values['High Card'] = sorted_cards[:5]

    # find all straight
    straight_results = find_straights(sorted_cards)
    if len(straight_results) != 0:
        result_hand_values['Straight'] = straight_results[0]
        for straight_result in straight_results:
            cur_suit = straight_result[0].suit
            if straight_result[1].suit == cur_suit and \
                    straight_result[2].suit == cur_suit and \
                    straight_result[3].suit == cur_suit and \
                    straight_result[4].suit == cur_suit:
                result_hand_values['Straight Flush'] = straight_result
                if straight_result[0].rank == 10:
                    result_hand_values['Royal Flush'] = straight_result

    # find all flushes
    flush_results = find_flushes(sorted_cards)
    if flush_results is not None:
        result_hand_values['Flush'] = flush_results[0]

    # find 4 of a kind
    fours_result = find_n_of_a_kind(sorted_cards, n=4)
    if fours_result is not None:
        result_hand_values['Four of a Kind'] = fours_result

    # find 3 of a kind
    threes_result = find_n_of_a_kind(sorted_cards, n=3)
    if threes_result is not None:
        result_hand_values['Three of a Kind'] = threes_result

    # find pair
    pair_result = find_n_of_a_kind(sorted_cards, n=2)
    if pair_result is not None:
        result_hand_values['Pair'] = pair_result

    # find full house
    full_house_result = find_full_house(sorted_cards)
    if full_house_result is not None:
        result_hand_values['Full House'] = full_house_result

    # find two pairs
    two_pairs_result = find_two_pairs(sorted_cards)
    if two_pairs_result is not None:
        result_hand_values['Two Pairs'] = two_pairs_result

    # return the best one
    for hand_value in HandValue.HAND_VALUES:
        if hand_value in result_hand_values:
            return hand_value, result_hand_values[hand_value]


def find_straights(ori_sorted_cards):
    straight_results = []
    memo = []

    def dfs_helper(list, straight_results, memo, pos):
        if len(memo) == 5:
            straight_results.append(memo[:])
            return
        if pos >= len(list):
            return

        cur_rank = memo[-1].rank
        i = pos + 1
        while i < len(list) and list[i].rank != cur_rank - 1:
            i += 1
        if i == len(list):
            return
        while i < len(list) and list[i].rank == cur_rank - 1:
            memo.append(list[i])
            dfs_helper(list, straight_results, memo, i)
            memo.pop(-1)
            i += 1

    # 1. Dummy rank 1 for Ace
    sorted_cards = ori_sorted_cards[:]
    for card in ori_sorted_cards:
        if card.rank == 14:
            sorted_cards.append(PokerCard(card.suit, 1))
    # 2. Search all straights by DFS
    for index in range(len(sorted_cards) - 5 + 1):
        memo.append(sorted_cards[index])
        dfs_helper(sorted_cards, straight_results, memo, index)
        memo.pop(-1)
    # 3. Sort by ascending order
    for straight_result in straight_results:
        straight_result.sort()
    # 4. Change Ace back
    for straight_result in straight_results:
        if straight_result[0].rank == 1:
            straight_result[0].rank = 14

    return straight_results


def find_flushes(cards):
    sorted_cards = sorted(cards, reverse=True)
    heart_group = filter(lambda x: x.suit == 'Heart', sorted_cards)
    diamond_group = filter(lambda x: x.suit == 'Diamond', sorted_cards)
    spade_group = filter(lambda x: x.suit == 'Spade', sorted_cards)
    club_group = filter(lambda x: x.suit == 'Club', sorted_cards)

    result_flush = []
    for group in [heart_group, diamond_group, spade_group, club_group]:
        if len(group) >= 5:
            result_flush.append(group[:5])

    return compare_high_cards(result_flush)


def compare_high_cards(high_cards):
    """
    Parameter must be descending ordered 5-card groups
    return the best 1 or more high cards
    """
    result = None
    if len(high_cards) == 0:
        return result
    for i in range(len(high_cards)):
        if len(high_cards[i]) != 5:
            raise Exception("Must be 5-card group")
        high_cards[i] = sorted(high_cards[i], reverse=True)

    result = high_cards[:]
    for j in range(5):
        temp_ranks = [x[j].rank for x in result]
        max_rank = max(temp_ranks)
        result = filter(lambda x: x[j].rank == max_rank, result)

    return result


def find_n_of_a_kind(sorted_cards, n):
    if n < 2:
        raise Exception("N must greater than 2")
    result = []
    start = 0
    end = 1
    while end < len(sorted_cards):
        if sorted_cards[end] == sorted_cards[start]:
            end += 1
        else:
            start = end
            end = start + 1
        if end - start == n:
            result.extend(sorted_cards[start: end])
            break
    if len(result) == 0:
        return None
    remain = sorted_cards[: start] + sorted_cards[end:]
    result.extend(remain[:5 - n])
    return result


def find_two_pairs(sorted_cards):
    result = []
    # 1. find largest 2 of a kind
    start = 0
    end = 1
    while end < len(sorted_cards):
        if sorted_cards[end] == sorted_cards[start]:
            end += 1
        else:
            start = end
            end = start + 1
        if end - start == 2:
            result.extend(sorted_cards[start: end])
            break
    if len(result) != 2:
        return None

    # 2. find another largest 2 of a kind from remaining part
    remain = sorted_cards[: start] + sorted_cards[end:]
    start = 0
    end = 1
    while end < len(remain):
        if remain[end] == remain[start]:
            end += 1
        else:
            start = end
            end = start + 1
        if end - start == 2:
            result.extend(remain[start: end])
            break
    if len(result) != 4:
        return None

    # 3. complement with the largest card in the rest
    remain = remain[: start] + remain[end:]
    result.append(remain[0])
    return result


def find_full_house(sorted_cards):
    result = []
    # 1. find largest 3 of a kind
    start = 0
    end = 1
    while end < len(sorted_cards):
        if sorted_cards[end] == sorted_cards[start]:
            end += 1
        else:
            start = end
            end = start + 1
        if end - start == 3:
            result.extend(sorted_cards[start: end])
            break
    if len(result) != 3:
        return None

    # 2. find largest 2 of a kind from remaining part
    remain = sorted_cards[: start] + sorted_cards[end:]
    start = 0
    end = 1
    while end < len(remain):
        if remain[end] == remain[start]:
            end += 1
        else:
            start = end
            end = start + 1
        if end - start == 2:
            result.extend(remain[start: end])
            break
    if len(result) != 5:
        return None

    return result


def cmp_high_card(a, b):
    """
    a and b must be of the same size
    :param a: list of cards
    :param b: list of cards
    :return: cmp
    """
    assert len(a) == len(b)
    _a = sorted(a, reverse=True)
    _b = sorted(b, reverse=True)
    for i in range(len(a)):
        if cmp(_a[i], _b[i]) == 0:
            continue
        else:
            return cmp(_a[i], _b[i])
    return 0

# a = [PokerCard('Diamond', 8),
#      PokerCard('Diamond', 9),
#      PokerCard('Heart', 9),
#      PokerCard('Diamond', 10),
#      PokerCard('Heart', 10),
#      PokerCard('Spade', 10),
#      PokerCard('Club', 10),
#      PokerCard('Diamond', 12),
#      PokerCard('Heart', 12),
#      PokerCard('Diamond', 13),
#      PokerCard('Heart', 13),
#      PokerCard('Diamond', 14),
#      PokerCard('Heart', 14),
#      PokerCard('Club', 14),
#      PokerCard('Spade', 14),
#      PokerCard('Heart', 2),
#      PokerCard('Heart', 3),
#      PokerCard('Heart', 4),
#      PokerCard('Heart', 5)
#      ]
# b1 = [PokerCard('Heart', 14),
#       PokerCard('Heart', 2),
#       PokerCard('Heart', 3),
#       PokerCard('Heart', 4),
#       PokerCard('Heart', 14)]
#
# b2 = [PokerCard('Club', 6),
#       PokerCard('Club', 6),
#       PokerCard('Club', 2),
#       PokerCard('Club', 5),
#       PokerCard('Club', 4)]
# # print find_best_hand_value(a)
# # find_flushes(a)
# # print compare_high_cards([b1, b2])
# # a.sort(reverse=True)
# # print a
# # print find_n_of_a_kind(a, 4)
#
# h3 = PokerCard('Heart', 13)
# s12 = PokerCard('Heart', 14)
# h4 = PokerCard('Heart', 12)
# c7 = PokerCard('Heart', 11)
# s14 = PokerCard('Spade', 7)
# d6 = PokerCard('Club', 7)
# d10 = PokerCard('Heart', 10)
#
# a = [h3, s12, h4, c7, s14, d6, d10]
# print HandValue(a)


# a1 = PokerCard('Heart', 6)
# a2 = PokerCard('Diamond', 7)
# a3 = PokerCard('Heart', 6)
# a4 = PokerCard('Diamond', 2)
# a5 = PokerCard('Heart', 12)
#
# b5 = PokerCard('Spade', 2)
# b1 = PokerCard('Club', 5)
# b2 = PokerCard('Club', 7)
# b3 = PokerCard('Spade', 6)
# b4 = PokerCard('Spade', 12)
#
# hv1 = HandValue([a1, a2, a3, a4, a5])
# hv2 = HandValue([b1, b2, b3, b4, b5])
#
# print hv1
# print hv2
# print ">?", hv1 > hv2
# print "=?", hv1 == hv2
#
# print type(max([hv1, hv2]))

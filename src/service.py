# -*- encoding:utf-8 -*-
from texas_game import Player, Game
import loggers

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# Rules
blind_money = 2
max_players = 8
bet_limit = 50

game = Game()
logger = loggers.get_logger()


def game_info():
    return game.info()


def add_player(name, money=100):
    player = Player(name, money)
    game.add_player(player)
    if len(game.players) == 1:
        player.host = True
        game.log.append("%s 成为了房主" % player.print_name())
    game.log.append("%s 加入了游戏" % player.print_name())


def start_game():
    if len(game.players) < 2:
        logger.error("人数不足2，无法开始")
        raise Exception("Error")
    game.new_game()
    game.log.append("<<<<<<<<<<<<<<<<<<<< Game Start >>>>>>>>>>>>>>>>>>>>")
    game.log.append("游戏开始")

    logger.info("大小盲自动下注")
    if blind_money / 2 > game.players[game.pos_small_blind].money or blind_money > game.players[game.pos_big_blind].money:
        logger.error("大小盲没钱了！游戏崩溃！")
        raise Exception("Error")
    game.players[game.pos_small_blind].bet(blind_money / 2)
    game.players[game.pos_big_blind].bet(blind_money)
    game.log.append("（自动）小盲 %s 下注金额 %d" % (game.players[game.pos_small_blind].print_name(), blind_money / 2))
    game.log.append("（自动）大盲 %s 下注金额 %d" % (game.players[game.pos_big_blind].print_name(), blind_money))
    game.highest_bet = blind_money

    logger.info("发底牌")
    game.log.append("开始发底牌")
    game.deal()

    logger.info("--- Pre Flop ---")
    game.log.append("----------- Pre-Flop Round -----------")
    game.pre_flop()
    game.log.append("开始翻牌前（第一轮）下注，从大盲下一位开始行动")
    game.action_num = 1

    game.active_player_pos = (game.pos_big_blind + 1) % len(game.players)
    game.log.append("请玩家 %s 开始行动" % game.players[game.active_player_pos].print_name())


def player_action(action, amount=0):
    player_pos = game.active_player_pos
    player = game.players[player_pos]

    if player.status != 'in game':
        logger.error("玩家无法活动！")
        raise Exception("Error")

    if action == 'check':
        player.check()
        game.log.append("玩家 %s 选择了 Check(让牌)" % player.print_name())
    elif action == 'call':
        player.call()
        game.log.append("玩家 %s 选择了 Call(跟注)" % player.print_name())
    elif action == 'raise':
        player.raise_bet(amount)
        game.log.append("玩家 %s 选择了 Raise(加注)，加注金额 %d" % (player.print_name(), amount))
    elif action == 'fold':
        player.fold()
        game.log.append("玩家 %s 选择了 Fold(弃牌)" % player.print_name())

    # 如果场上只有一个玩家in game，直接判胜
    in_game_num = 0
    for player in game.players:
        if player.status == 'in game' or 'all in':
            in_game_num += 1
    if in_game_num == 1:
        winners = game.players
        game.log.append("场上只剩一位玩家，游戏结束")
        game.log.append("赢得胜利的玩家是：%s" % winners[0].print_name())
        game.log.append("赢得胜利的牌型是：%s" % winners[0].best_hand_value)
        game.log.append("赢取的金额为：%d" % game.pot)
        game.checkout(winners)
        game.status = 'showdown'
        game.log.append("恭喜！")
        return

    # find halting criteria
    next_player_pos = (player_pos + 1) % len(game.players)
    if game.status == 'pre flop':
        min_poll_count = len(game.players) - 1
    else:
        min_poll_count = len(game.players)
    while True:
        player = game.players[next_player_pos]
        game.action_num += 1
        if game.action_num > min_poll_count and game.players[next_player_pos].cur_bet == game.highest_bet:
            next_step()
            return
        if player.status != 'in game':
            game.log.append("跳过玩家 %s" % player.print_name())
            next_player_pos = (next_player_pos + 1) % len(game.players)
        else:
            break
    game.log.append("请玩家 %s 开始行动" % player.print_name())
    game.active_player_pos = next_player_pos


def next_step():
    if game.status == 'pre flop':
        game.log.append("结束翻牌前（第一轮）下注")
        game.log.append("开始发前三张公共牌")
        game.flop()
        game.log.append("----------- Flop Round -----------")
        game.log.append("开始翻牌圈（第二轮）下注，从小盲开始行动")
        game.action_num = 1
        game.active_player_pos = game.pos_small_blind
        game.log.append("请玩家 %s 开始行动" % game.players[game.active_player_pos].print_name())
    elif game.status == 'flop':
        game.log.append("结束翻牌圈（第二轮）下注")
        game.log.append("开始发第四张公共牌")
        game.turn()
        game.log.append("----------- Turn Round -----------")
        game.log.append("开始转牌圈（第三轮）下注，从小盲开始行动")
        game.action_num = 1
        game.active_player_pos = game.pos_small_blind
        game.log.append("请玩家 %s 开始行动" % game.players[game.active_player_pos].print_name())
    elif game.status == 'turn':
        game.log.append("结束转牌圈（第三轮）下注")
        game.log.append("开始发第五张公共牌")
        game.river()
        game.log.append("----------- River Round -----------")
        game.log.append("开始河牌圈（第四轮）下注，从小盲开始行动")
        game.action_num = 1
        game.active_player_pos = game.pos_small_blind
        game.log.append("请玩家 %s 开始行动" % game.players[game.active_player_pos].print_name())
    elif game.status == 'river':
        game.log.append("结束河牌圈（第四轮）下注")
        game.log.append("----------- Showdown -----------")
        game.log.append("所有轮次结束，开始判定胜利玩家")
        winners = game.showdown()
        game.log.append("赢得胜利的玩家是：")
        game.log.append("  ".join([x.print_name() for x in winners]))
        game.log.append("赢得胜利的牌型是：")
        for winner in winners:
            game.log.append(str(winner.best_hand_value))
        prize = game.checkout(winners)
        game.log.append("赢取的金额为：%d" % prize)
        game.checkout(winners)
        game.log.append("恭喜！")
        game.log.append("房主请开始游戏")
# -*- encoding:utf-8 -*-
from texas_game import Player, Game
import loggers

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# Rules
init_money = 100
max_players = 8
min_players = 3
offline_pending_times = 10  # sec

game = Game()
logger = loggers.get_logger()

offline_timer = {}


def game_info():
    return game.info()


def heartbeat(pos):
    if pos not in offline_timer:
        raise Exception("No such player alive")
    offline_timer[pos].reset(offline_pending_times)


def offline(pos):
    player = game.players[pos]
    logger.info("玩家 %s 离线" % player.print_name())
    game.log.append("玩家 %s 离线" % player.print_name())
    offline_timer[pos].cancel()
    offline_timer.pop(pos)
    player.status = 'offline'
    game.remove_offline_players()

    # change host
    if player.host:
        player.host = False
        for player in game.players:
            if player is not None:
                player.host = True
                game.log.append("%s 成为了房主" % player.print_name())

    # 如果场上只有一个玩家in game，直接判胜
    if len(game.alive_players_indices) == 1:
        winners = game.players
        game.log.append("----------- Showdown -----------")
        game.log.append("场上只剩一位玩家，游戏结束")
        game.log.append("赢得胜利的玩家是：%s" % winners[0].print_name())
        game.log.append("赢得胜利的牌型是：%s" % winners[0].best_hand_value)
        game.log.append("赢取的金额为：%d" % game.pot)
        game.checkout(winners)
        game.status = 'showdown'
        game.log.append("恭喜！")
        return

    # change active player
    if player.pos == game.active_player_pos:
        next_pos = game.find_next_active_pos(player.pos)
        game.active_player_pos = next_pos
        game.log.append("请玩家 %s 开始行动" % game.players[next_pos].print_name())


def add_player(name, money=init_money):
    if game.status not in ['showdown', 'init']:
        raise Exception("Cannot join when game is running")
    if len(game.players) >= max_players:
        raise Exception("Only support %d players" % max_players)
    player = Player(name, money)
    pos = game.add_player(player)

    # add timer
    from timer import TimerReset
    offline_timer[pos] = TimerReset(offline_pending_times, offline, [pos, ])
    offline_timer[pos].start()
    game.log.append("%s 加入了游戏" % player.print_name())

    # assign the first host
    if len(filter(lambda x: x is not None, game.players)) == 1:
        player.host = True
        game.log.append("%s 成为了房主" % player.print_name())
    return pos, player.host


def start_game(pos):
    if len(game.players) < min_players:
        logger.error("人数不足%d，无法开始" % min_players)
        raise Exception("Number of players must be greater than %d" % min_players)
    if not game.players[pos].host:
        raise Exception("Only host can start game")

    game.new_game()
    game.log.append("<<<<<<<<<<<< Game Start >>>>>>>>>>>>")
    game.log.append("游戏开始")

    # big blind and small blind bet
    if game.blind_money / 2 > game.players[game.pos_small_blind].money or \
            game.blind_money > game.players[game.pos_big_blind].money:
        logger.error("大小盲没钱了！游戏崩溃！")
        raise Exception("Big blind or small blind has no enough money")
    game.players[game.pos_small_blind].bet(game.blind_money / 2)
    game.players[game.pos_big_blind].bet(game.blind_money)
    game.log.append("（自动）小盲 %s 下注金额 %d" % (game.players[game.pos_small_blind].print_name(), game.blind_money / 2))
    game.log.append("（自动）大盲 %s 下注金额 %d" % (game.players[game.pos_big_blind].print_name(), game.blind_money))
    game.highest_bet = game.blind_money

    game.log.append("开始发底牌")
    game.deal()

    game.log.append("----------- Pre-Flop Round -----------")
    game.pre_flop()
    game.log.append("开始翻牌前（第一轮）下注，从大盲下一位开始行动")

    game.active_player_pos = game.find_next_active_pos(game.pos_big_blind)
    game.log.append("请玩家 %s 开始行动" % game.players[game.active_player_pos].print_name())


def player_action(player_pos, action, amount=0):
    if player_pos != game.active_player_pos:
        raise Exception("Not a correct player. Action doesn't permitted")

    player = game.players[player_pos]

    if player is None or player.status != 'in game':
        logger.error("玩家无法活动！")
        raise Exception("Error")

    if action == 'check':
        if player.cur_bet != game.highest_bet:
            raise Exception("Check condition was not satisfied")
        player.check()
        game.log.append("玩家 %s 选择了 Check(让牌)" % player.print_name())
    elif action == 'call':
        if player.cur_bet > game.highest_bet:
            raise Exception("Call condition was not satisfied")
        player.call()
        game.log.append("玩家 %s 选择了 Call(跟注)" % player.print_name())
    elif action == 'raise':
        amount = int(amount)
        if player.cur_bet + amount <= game.highest_bet or amount > player.money:
            raise Exception("Raise condition was not satisfied")
        player.raise_bet(amount)
        game.log.append("玩家 %s 选择了 Raise(加注)，加注金额 %d" % (player.print_name(), amount))
    elif action == 'fold':
        player.fold()
        game.log.append("玩家 %s 选择了 Fold(弃牌)" % player.print_name())

    # 如果场上只有一个玩家in game，直接判胜
    if len(game.alive_players_indices) == 1:
        winners = game.players
        game.log.append("----------- Showdown -----------")
        game.log.append("场上只剩一位玩家，游戏结束")
        game.log.append("赢得胜利的玩家是：%s" % winners[0].print_name())
        game.log.append("赢得胜利的牌型是：%s" % winners[0].best_hand_value)
        game.log.append("赢取的金额为：%d" % game.pot)
        game.checkout(winners)
        game.status = 'showdown'
        game.log.append("恭喜！")
        return

    # find halting criteria
    if game.status == 'pre flop':
        end_pos = game.pos_big_blind
    else:
        end_pos = game.pos_small_blind

    next_pos = (player.pos + 1) % game.num_players
    while True:
        if next_pos == end_pos:
            game.next_stage_flag = True
        if game.players[next_pos] is not None:
            if game.next_stage_flag and game.players[next_pos].cur_bet == game.highest_bet:
                next_step()
                return
            if game.players[next_pos].status != 'in game':
                game.log.append("跳过玩家 %s" % game.players[next_pos].print_name())
            else:
                break
        next_pos = (next_pos + 1) % game.num_players

    game.log.append("请玩家 %s 开始行动" % game.players[next_pos].print_name())
    game.active_player_pos = next_pos


def next_step():
    if game.status == 'pre flop':
        game.log.append("结束翻牌前（第一轮）下注")
        game.log.append("开始发前三张公共牌")
        game.flop()
        game.log.append("----------- Flop Round -----------")
        game.log.append("开始翻牌圈（第二轮）下注，从小盲开始行动")
        game.active_player_pos = game.pos_small_blind
        game.next_stage_flag = False
        game.log.append("请玩家 %s 开始行动" % game.players[game.active_player_pos].print_name())
    elif game.status == 'flop':
        game.log.append("结束翻牌圈（第二轮）下注")
        game.log.append("开始发第四张公共牌")
        game.turn()
        game.log.append("----------- Turn Round -----------")
        game.log.append("开始转牌圈（第三轮）下注，从小盲开始行动")
        game.active_player_pos = game.pos_small_blind
        game.next_stage_flag = False
        game.log.append("请玩家 %s 开始行动" % game.players[game.active_player_pos].print_name())
    elif game.status == 'turn':
        game.log.append("结束转牌圈（第三轮）下注")
        game.log.append("开始发第五张公共牌")
        game.river()
        game.log.append("----------- River Round -----------")
        game.log.append("开始河牌圈（第四轮）下注，从小盲开始行动")
        game.active_player_pos = game.pos_small_blind
        game.next_stage_flag = False
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
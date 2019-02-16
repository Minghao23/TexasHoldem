# coding=utf-8
from texas_game import Player, Game

# Rules
blind_money = 2
max_players = 8
bet_limit = 50

game = Game()
player1 = Player("hmh", 100)
player2 = Player("qk", 100)
player3 = Player("lvc", 100)
player4 = Player("zzc", 100)

print ">>> 欢迎来到德州扑克 v1.0-alpha"

print ">>> 请各位玩家加入游戏"
###
game.add_player(player1)
game.add_player(player2)
game.add_player(player3)
game.add_player(player4)
num_players = len(game.players)
print ">>> 已加入游戏的玩家有："
for player in game.players:
    print "%s  " % player.print_name(),
print " "

print "----------- New Game -----------"
game.new_game()
print ">>> 开始新游戏：[庄家]%s  [小盲]%s  [大盲]%s" % (
    game.players[game.pos_button].print_name(),
    game.players[game.pos_small_blind].print_name(),
    game.players[game.pos_big_blind].print_name())

print ">>> 大小盲请下注（自动）"
if blind_money / 2 > game.players[game.pos_small_blind].money or blind_money > game.players[game.pos_big_blind].money:
    print "大小盲没钱了！游戏崩溃！"
    exit()
game.players[game.pos_small_blind].bet(blind_money/2)
game.players[game.pos_big_blind].bet(blind_money)
game.highest_bet = blind_money

print ">>> 开始发底牌"
game.deal()

print "----------- Pre-Flop Round -----------"
print ">>> 开始翻牌前下注，从大盲下一位开始行动"
start_i = game.pos_big_blind  # pre-flop 大盲自动下注
i = start_i + 1  # 从大盲后一位开始
while True:
    #TODO 如果场上只有一个玩家in game，直接判胜
    player = game.players[i % num_players]
    if player.status != 'in game':
        print ">>> 跳过玩家[%s]"
        continue
    if i >= start_i + num_players and player.cur_bet == game.highest_bet:
        print ">>> 结束翻牌前下注"
        break
    print ">>> 请玩家[%s]开始行动：1-让牌  2-加注  3-弃牌" % player.print_name()
    print "您的底牌：%s" % player.print_holes()
    print "当前公牌：%s" % game.print_community_cards()
    print "您的当前总下注金额为：%d" % player.cur_bet
    print "场上最高的下注金额为：%d" % game.highest_bet

    # 需要判断是否符合行动条件
    player.call()
    i += 1

print ">>> 开始发前三张公共牌"
game.flop()
print ">>> 当前公共牌为：%s" % game.print_community_cards()

print "----------- Flop Round -----------"
print ">>> 开始翻牌圈下注，从小盲开始行动"
start_i = game.pos_small_blind  # 小盲位开始
i = start_i  # 从大盲后一位开始
while True:
    # TODO 如果场上只有一个玩家in game，直接判胜
    player = game.players[i % num_players]
    if player.status != 'in game':
        print ">>> 跳过玩家[%s]"
        continue
    if i >= start_i + num_players and player.cur_bet == game.highest_bet:
        print ">>> 结束翻牌圈下注"
        break
    print ">>> 请玩家[%s]开始行动：1-让牌  2-加注  3-弃牌" % player.print_name()
    print "您的底牌：%s" % player.print_holes()
    print "当前公牌：%s" % game.print_community_cards()
    print "当前您的最大牌型为：%s" % player.best_hand_value
    print "您的当前总下注金额为：%d" % player.cur_bet
    print "场上最高的下注金额为：%d" % game.highest_bet

    # 需要判断是否符合行动条件
    player.call()
    i += 1

print ">>> 开始发第四张公共牌"
game.turn()
print ">>> 当前公共牌为：%s" % game.print_community_cards()

print "----------- Turn Round -----------"
print ">>> 开始转牌圈下注，从小盲开始行动"
start_i = game.pos_small_blind  # 小盲位开始
i = start_i  # 从大盲后一位开始
while True:
    # TODO 如果场上只有一个玩家in game，直接判胜
    player = game.players[i % num_players]
    if player.status != 'in game':
        print ">>> 跳过玩家[%s]"
        continue
    if i >= start_i + num_players and player.cur_bet == game.highest_bet:
        print ">>> 结束转牌圈下注"
        break
    print ">>> 请玩家[%s]开始行动：1-让牌  2-加注  3-弃牌" % player.print_name()
    print "您的底牌：%s" % player.print_holes()
    print "当前公牌：%s" % game.print_community_cards()
    print "当前您的最大牌型为：%s" % player.best_hand_value
    print "您的当前总下注金额为：%d" % player.cur_bet
    print "场上最高的下注金额为：%d" % game.highest_bet

    # 需要判断是否符合行动条件
    player.call()
    i += 1

print ">>> 开始发第五张公共牌"
game.turn()
print ">>> 当前公共牌为：%s" % game.print_community_cards()

print "----------- River Round -----------"
print ">>> 开始河牌圈下注，从小盲开始行动"
start_i = game.pos_small_blind  # 小盲位开始
i = start_i  # 从大盲后一位开始
while True:
    # TODO 如果场上只有一个玩家in game，直接判胜
    player = game.players[i % num_players]
    if player.status != 'in game':
        print ">>> 跳过玩家[%s]"
        continue
    if i >= start_i + num_players and player.cur_bet == game.highest_bet:
        print ">>> 结束河牌圈下注"
        break
    print ">>> 请玩家[%s]开始行动：1-让牌  2-加注  3-弃牌" % player.print_name()
    print "您的底牌：%s" % player.print_holes()
    print "当前公牌：%s" % game.print_community_cards()
    print "当前您的最大牌型为：%s" % player.best_hand_value
    print "您的当前总下注金额为：%d" % player.cur_bet
    print "场上最高的下注金额为：%d" % game.highest_bet

    # 需要判断是否符合行动条件
    player.call()
    i += 1

print "----------- Showdown -----------"
print ">>> 游戏结束，赢得胜利的玩家是："
winners = game.showdown()
print "  ".join([x.print_name() for x in winners])
print ">>> 赢得胜利的牌型为："
for winner in winners:
    print winner.best_hand_value
prize = game.checkout(winners)
print "赢取的金额为：%d" % prize
print "恭喜！"
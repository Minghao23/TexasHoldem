# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse
from src import service
import json


def index(request):
    return HttpResponse("Hello, this is Texas Hold'em Game, developed by Minghao23.")


def game_info_response():
    response_json = json.dumps(service.game_info())
    return HttpResponse(response_json, content_type="application/json")


def join_game(request):
    if request.method == 'GET':
        name = request.GET.get('name', '张三')
        service.add_player(name)
        return game_info_response()


def start_game(request):
    if request.method == 'GET':
        service.start_game()
        return game_info_response()


def check(request):
    if request.method == 'GET':
        service.player_action('check')
        return game_info_response()


def call(request):
    if request.method == 'GET':
        service.player_action('call')
        return game_info_response()


def raise_bet(request):
    if request.method == 'GET':
        amount = request.GET.get('amount')
        service.player_action('raise', int(amount))
        return game_info_response()


def fold(request):
    if request.method == 'GET':
        service.player_action('fold')
        return game_info_response()


def info(request):
    if request.method == 'GET':
        return game_info_response()
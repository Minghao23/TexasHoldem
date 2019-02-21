# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse
from src import service
import json


def index(request):
#     return render(request, 'texas/index.html')
    return HttpResponse("Hello, this is Texas Hold'em Game, developed by Minghao23.")

def join(request, **kwargs):
    return render(request, 'texas/join.html')

def game(request, **kwargs):
    page_data = {"position": request.GET.get("pos", "")}
    return render(request, 'texas/game.html',{"page_data": json.dumps(page_data)})

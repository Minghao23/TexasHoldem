# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse
from src import service
import json


def index(request):
    return render(request, 'texas/index.html')

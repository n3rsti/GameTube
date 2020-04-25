from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
import requests
from .forms import TrackerSearchForm
from riotwatcher import LolWatcher, ApiError

file = open("key.txt", "r")
key = file.read()
watcher = LolWatcher(key)


def get_server(server):
    switch = {
        "EUNE": "EUN1",
        "EUW": "EUW1"
    }
    return switch.get(server.upper(), "EUW")


def search_view(request):
    if request.method == "POST":
        form = TrackerSearchForm(request.POST)
        if form.is_valid():
            player = form.cleaned_data.get('username')
            server = form.cleaned_data.get('server').lower()
            return redirect('player_detail', server, player)
    else:
        form = TrackerSearchForm()
    context = {
        "title": "Search",
        "form": form
    }
    return render(request, 'index.html', context)


def player_view(request, username, server):
    server = get_server(server)
    data = None
    try:
        data = watcher.summoner.by_name(server, username)
        matches = watcher.match.matchlist_by_account(server, data['accountId'])
        ranked_stats = watcher.league.by_summoner(server, data['id'])[0]
    except ApiError as err:
        if err.response.status_code == 429:
            print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
            print('this retry-after is handled by default by the RiotWatcher library')
            print('future requests wait until the retry-after time passes')
        elif err.response.status_code == 404:
            print('Summoner with that name not found.')
        else:
            raise
        return redirect("tracker_search")
   
    context = {
        "json": data,
        "icon": data['profileIconId'],
        "name": data['name'],
        "level": data['summonerLevel'],
        "ranked": ranked_stats,
        "rank": f"{ranked_stats['tier']} {ranked_stats['rank']}",
        "winrate": f"{int(ranked_stats['wins'] * 100 / (ranked_stats['wins'] + ranked_stats['losses']))}%",
        "matches": matches['matches'],
        "title": data['name']
    }
    return render(request, 'player.html', context)

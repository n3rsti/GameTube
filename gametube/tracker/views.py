from django.shortcuts import render, redirect
import requests
from .models import LolVersion, Champion
from .forms import TrackerSearchForm
from riotwatcher import LolWatcher, ApiError
from django.shortcuts import get_object_or_404
import json


file = open("key.txt", "r")
key = file.read()
watcher = LolWatcher(key)
def get_server(server):
    switch = {
        "EUNE": "EUN1",
        "EUW": "EUW1"
    }
    return switch.get(server.upper(), "EUW")

def get_queue(queue):
    switch = {
        "RANKED_SOLO_5x5": "Solo / Duo",
        "RANKED_FLEX_SR": "Flex 5:5"
    }
    return switch.get(queue, "EUW")

db_version = LolVersion.objects.all().first()
champions = requests.get(f'http://ddragon.leagueoflegends.com/cdn/{db_version.patch}/data/en_US/champion.json').json()

def update_champions():
    for champion in champions['data']:
        try:
            champion = Champion.objects.get(champion_id = champions['data'][champion]['key'])
        except Champion.DoesNotExist:
            champion_id=champions['data'][champion]['id']
            champion = Champion(name = champions['data'][champion]['id'], champion_id=champion_id)
            champion.save()


version = requests.get('https://ddragon.leagueoflegends.com/api/versions.json').json()[0]
if not str(db_version.patch) == str(version):
    db_version.patch = version
    db_version.save()
    update_champions()


            




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
    except:
        return redirect("tracker_search")
   
    acc_id = data['id']
    
    mastery = watcher.champion_mastery.by_summoner(server, acc_id)
    highest_mastery = mastery[0]['championId']
    highest_mastery_champ = Champion.objects.get(champion_id = highest_mastery).name
    
    queue = []
    tier = []
    rank = []
    lp = []
    wins = []
    losses = []
    winrate = []

    for ranked in watcher.league.by_summoner(server, data['id']):
        queue.append(get_queue(ranked['queueType']))
        tier.append(ranked['tier'])
        rank.append(ranked['rank'])
        lp.append(ranked['leaguePoints'])
        wins.append(ranked['wins'])
        losses.append(ranked['losses'])
        winrate.append(int(ranked['wins'] * 100 / (ranked['wins'] + ranked['losses'])))
    context = {
        "json": data,
        "icon": data['profileIconId'],
        "name": data['name'],
        "level": data['summonerLevel'],
        "tier": ranked_stats['tier'],
        "rank": ranked_stats['rank'],
        "winrate": f"{int(ranked_stats['wins'] * 100 / (ranked_stats['wins'] + ranked_stats['losses']))}%",
        "matches": matches['matches'],
        "title": data['name'],
        "highest_champ": highest_mastery_champ,
        "rankeds": zip(reversed(queue), reversed(tier), reversed(rank), reversed(lp), reversed(wins), reversed(losses), reversed(winrate)),
        "queue": queue,
    }
    return render(request, 'player.html', context)

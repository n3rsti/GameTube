from django.shortcuts import render, redirect
import requests
from .models import LolVersion, Champion
from .forms import TrackerSearchForm
from django.shortcuts import get_object_or_404
import json


file = open("key.txt", "r")
key = file.read()
def get_server(server):
    switch = {
        "EUNE": "EUN1",
        "EUW": "EUW1",
        "BR": "BR1",
        "JP": "JP1",
        "KR": "KR",
        "LAN": "LA1",
        "LAS": "LA2",
        "NA": "NA1",
        "OC": "OC1",
        "TR": "TR1",
        "RU": "RU"
    }
    return switch.get(server.upper(), "EUW")

def get_queue(queue):
    switch = {
        "RANKED_SOLO_5x5": "Solo / Duo",
        "RANKED_FLEX_SR": "Flex 5:5"
    }
    return switch.get(queue, "EUW")

def get_rank(rank):
    switch = {
        "I": 1,
        "II": 2,
        "III": 3,
        "IV": 4
    }
    return switch.get(rank, 1)



def update_champions():
    for champion in champions['data']:
        try:
            champion = Champion.objects.get(champion_id = champions['data'][champion]['key'])
        except Champion.DoesNotExist:
            champion_id=champions['data'][champion]['id']
            champion = Champion(name = champions['data'][champion]['id'], champion_id=champion_id)
            champion.save()


def update_patch():
    version = requests.get('https://ddragon.leagueoflegends.com/api/versions.json').json()[0]
    if not str(db_version.patch) == str(version):
        db_version.patch = version
        db_version.save()
        update_champions()


db_version = LolVersion.objects.all().first()
champions = requests.get(f'http://ddragon.leagueoflegends.com/cdn/{db_version.patch}/data/en_US/champion.json').json()




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
        data = requests.get(f'https://{server}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{username}?api_key={key}').json()
        matches = requests.get(f'https://{server}.api.riotgames.com/lol/match/v4/matchlists/by-account/{data["accountId"]}?api_key={key}').json()
        ranked_stats = requests.get(f'https://{server}.api.riotgames.com/lol/league/v4/entries/by-summoner/{data["id"]}?api_key={key}').json()
        solo_stats = ranked_stats[0]
    except:
        return redirect("tracker_search")
   
    acc_id = data['id']
    
    mastery = requests.get(f'https://{server}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{data["id"]}?api_key={key}').json()
    highest_mastery = mastery[0]['championId']
    highest_mastery_champ = Champion.objects.get(champion_id = highest_mastery).name
    
    matchlist = requests.get(f'https://{server}.api.riotgames.com/lol/match/v4/matchlists/by-account/{data["accountId"]}?api_key={key}').json()
    
    queue = []
    tier = []
    rank = []
    lp = []
    wins = []
    losses = []
    winrate = []
    rank_int = []

    players = []
    match_wins = []

    for match in matchlist['matches'][:5]:
        match_api = requests.get(f'https://{server}.api.riotgames.com/lol/match/v4/matches/{match["gameId"]}?api_key={key}').json()
        for player in match_api['participantIdentities']:
            players.append([player['player']['summonerName'], player['player']['profileIcon'], player['participantId']])
            if player['player']['summonerName'] == data['name']:
                player_index = int(player['participantId']) - 1
                match_wins.append(match_api['participants'][player_index]['stats']['win'])

    for ranked in ranked_stats:
        queue.append(get_queue(ranked['queueType']))
        tier.append(ranked['tier'])
        rank.append(ranked['rank'])
        lp.append(ranked['leaguePoints'])
        wins.append(ranked['wins'])
        losses.append(ranked['losses'])
        winrate.append(int(ranked['wins'] * 100 / (ranked['wins'] + ranked['losses'])))
        rank_int.append(get_rank(ranked['rank']))
    context = {
        "json": data,
        "icon": data['profileIconId'],
        "name": data['name'],
        "level": data['summonerLevel'],
        "tier": solo_stats['tier'],
        "rank": solo_stats['rank'],
        "winrate": f"{int(solo_stats['wins'] * 100 / (solo_stats['wins'] + solo_stats['losses']))}%",
        "matches": zip(matches['matches'][:5], match_wins),
        "title": data['name'],
        "highest_champ": highest_mastery_champ,
        "rankeds": zip(queue, tier, rank, lp, wins, losses, winrate, rank_int),
        "queue": reversed(queue),
        "patch": db_version.patch,
    }
    return render(request, 'player.html', context)

import requests
from collections import Counter

api_key = 'RGAPI-444178e4-b47c-408c-b7a3-0092fccb073e'

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://developer.riotgames.com",
        "X-Riot-Token": api_key
        }


def get_my_info(nickname):

    #닉네임으로 유저계정정보 불러오기
    url = f'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{nickname}'
    response = requests.request("GET", url, headers=headers)
    user = response.json()

    try:
        #반환할 데이터 폼 구성하기
        user_info = {
        'name':user['name'], 
        'level':user['summonerLevel'], 
        'profile_icon':user['profileIconId'], 
        'account_id':user['accountId'],
        'puuid':user['puuid'],
        'player_id':user['id'],
        'rank':False, 
        'now_playing':False
        }
        #아이디 확인, 오류 발생 시엔 Exception으로 넘어간다.
        id = user['id']
        #불러온 JSON 파일에서 계정ID를 이용하여 랭크 정보 불러오기
        #언랭일 경우도 계산해야됨 ***중요***
        url = f'https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{id}'
        response = requests.request("GET", url, headers=headers)
        rank = response.json()
        if rank:
            for i in rank:
                if i['queueType'] == 'RANKED_SOLO_5x5':
                    user_info['rank'] = {
                        'tier':i['tier'],
                        'rank':i['rank'], 
                        'point':i['leaguePoints'], 
                        'wins':i['wins'], 
                        'losses':i['losses'],
                        'win_rate':'{:.2f}'.format(i['wins'] / (i['losses']+i['wins']) * 100)
                        }

        #게임중인지 아닌지 확인하여 게임중이면 게임정보 불러오기
        url = f'https://kr.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{id}'
        response = requests.request("GET", url, headers=headers)
        playing = response.json()
        try:
            if not playing['gameQueueConfigId'] == 420:
                user_info['now_playing'] = False
            else:
                user_info['now_playing'] = playing['participants']
                for a in user_info['now_playing']:
                    if user_info['name'] == a['summonerName']:
                        user_info['team_id'] = a['teamId']
                        user_info['champ'] = a['championId']   
        except:
            # user_info['now_playing'] = False
            return False
        

        return user_info
    except:
        #플레이어 정보가 없으므로 False 반환 나중에 flask 코딩할 때 if not get_my_info 등으로 가능
        return False


#get my info에서 result를 삽입 물론 now playing이 True 인 경우에만
def get_oppo_info(oppo):
    if oppo['now_playing']:
        for i in oppo['now_playing']:
            if not i['teamId'] == oppo['team_id']:
                oppo = get_my_info(i['summonerName'])

    return oppo

#상대방 룬, 스펠 정보 추출 (룬[머시깆시기], 스펠1, 스펠2) 형태
def rune_info(oppo):
    if oppo['now_playing']:
        for i in oppo['now_playing']:
            if i['summonerName'] != oppo['name']:
                return i['perks'], i['spell1Id'], i['spell2Id']


#상대가 현재 게임중인 챔피언의 매치리스트, kda, 승, 패 불러오기
def champ_history(oppo):
    #플레이어의 챔피언 정보를 저장할 포맷 설정
    oppo_champ_info = {
        'champ':0,
        'lv':0,
        'point':0,


        'all_kills':0,
        'kills':0, 
        'deaths':0, 
        'assists':0, 


        'match':0,
        'wins':0, 
        'losses':0,

        'sight':0,

        'damage':0,

        'minion':0,

        'items':[]
        }
    #만약 함수에 인자로 주어질 상대방 프로필에 챔피언 아이디가 있다면 실행
    if oppo.get('champ'):
        #매치 리스트 생성
        url = 'https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/{}?champion={}&queue=420&season=13'.format(oppo['account_id'], oppo['champ'])
        response = requests.request("GET", url, headers=headers)
        user = response.json()
        match_list = [a['gameId'] for a in user['matches']]

        #플레이어의 챔피언 숙련도 저장
        url = 'https://kr.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{}/by-champion/{}'.format(oppo['player_id'], oppo['champ'])
        response = requests.request("GET", url, headers=headers)
        champ_info = response.json()
        oppo_champ_info['champ'] = champ_info['championId']
        oppo_champ_info['lv'] = champ_info['championLevel']
        oppo_champ_info['point'] = champ_info['championPoints']

        #최대 호출을 넘길 수 있으니 보험으로 try, exception
        try:
            #매치리스트 길이만큼 실행
            for match in match_list:
                url = f'https://kr.api.riotgames.com/lol/match/v4/matches/{match}'
                response = requests.request("GET", url, headers=headers)
                match_info = response.json()
                #매치에서 게임에 참여한 플레이어 탐색
                for parts in match_info['participants']:
                    #탐색하던 플레이어가 상대방이면 상대방의 정보 저장
                    if parts['championId'] == oppo['champ']:
                        oppo_champ_info['kills'] += parts['stats']['kills']
                        oppo_champ_info['deaths'] += parts['stats']['deaths']
                        oppo_champ_info['assists'] += parts['stats']['assists']
                        oppo_champ_info['sight'] += parts['stats']['wardsPlaced']
                        oppo_champ_info['sight'] += parts['stats']['wardsKilled']
                        oppo_champ_info['damage'] += parts['stats']['totalDamageDealt']
                        oppo_champ_info['minion'] += parts['stats']['totalMinionsKilled']
                    

                        #여기서 아이템 예외처리하는것도 좋을듯 (  if parts['stats'][f'item{i}'] == '무언가' 그럼 append 하지 않는걸로  )
                        for i in range(7):
                            if parts['stats'][f'item{i}'] in [0, 1001, 2003, 2033, 2031, 2055, 3364, 3363, 3340]:
                                pass
                            else:
                                oppo_champ_info['items'].append(parts['stats'][f'item{i}'])
    

                        if parts['stats']['win'] == True:
                            oppo_champ_info['wins'] += 1
                        else:
                            oppo_champ_info['losses'] += 1
                    if parts['teamId'] != oppo['team_id']:
                        oppo_champ_info['all_kills'] += parts['stats']['deaths']
        except:
            pass
    
    #전체 판수도 계산
    oppo_champ_info['match'] = oppo_champ_info['wins'] + oppo_champ_info['losses']

    #아이템 목록 JSON
    url = 'https://ddragon.leagueoflegends.com/cdn/11.13.1/data/ko_KR/item.json'
    item_json = requests.get(url).json()
    #아이템 중 가장 빈도가 높았던 6개를 다시 정리
    champ_item = []
    items = Counter(oppo_champ_info['items']).most_common(6)
    for item in items:
        try:
            ib = item_json['data'][str(item[0])]['name']
            per_match = item[1] / oppo_champ_info['match'] * 100
            
            champ_item.append([item[0], ib, round(per_match, 2)])
        except:
            pass

    oppo_champ_info['items'] = champ_item

    
    #데이터 반환
    return oppo_champ_info



def radar_data(oppo_champ_info):
    cs = oppo_champ_info['minion'] / oppo_champ_info['match']
    offensive = (oppo_champ_info['kills']+oppo_champ_info['deaths']+oppo_champ_info['assists']) / oppo_champ_info['match']
    sight_point = oppo_champ_info['sight'] / oppo_champ_info['match']
    battle_join = oppo_champ_info['all_kills'] / (oppo_champ_info['kills']+oppo_champ_info['assists'])
    carry = oppo_champ_info['all_kills'] / oppo_champ_info['kills']

    result = [round(cs/10, 1), round(offensive, 1), round(sight_point, 1), round(battle_join, 1)*2, round(carry, 1)*2]
    return result

def get_champ_name(champ_id):
    url = 'https://ddragon.leagueoflegends.com/cdn/11.13.1/data/ko_KR/champion.json'
    js = requests.get(url).json()
    for j in js['data']:
        if js['data'][j]['key'] == str(champ_id['champ']):
            return [js['data'][j]['id'], js['data'][j]['name']]

def get_spell_name(rune):
    url = 'http://ddragon.leagueoflegends.com/cdn/11.13.1/data/en_US/summoner.json'
    js = requests.get(url).json()
    spell = []
    for s in js['data']:
        if js['data'][s]['key'] == str(rune[-2]):
            spell.append(js['data'][s]['name'])
        elif js['data'][s]['key'] == str(rune[-1]):
            spell.append(js['data'][s]['name'])

    for s in range(len(spell)):
        if spell[s] == 'Ignite':
            spell[s] = 'Dot'
    return spell

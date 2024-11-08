import requests
import json 
import shutil
import os
import random
import time
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from pathlib import Path
from pydub import AudioSegment

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip, deflate, br',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
}

def song_types_openings(song):
    if song["songType"].split(" ")[0] == "Opening":
        return True
    else:
        return False
def song_types_endings(song):
    if song["songType"].split(" ")[0] == "Ending":
        return True
    else:
        return False
def song_types_inserts(song):
    if song["songType"].split(" ")[0] == "Insert":
        return True
    else:
        return False
        
def get_reduct_type(type):
    if type == "Opening":
        return "OP"
    if type == "Ending":
        return "ED"
    if type == "Insert":
        return "INS"

def gen():
    with open('./data.json') as file:
        settings = json.load(file)
        
    def debug_log(mess):
        if settings['log']:
            print(mess)

    debug_log('настроечки подгружены, дебаг лог включооон')

    # settings = {
    #     "gen_type": "mal_user",
    #     "malName": "AmqPsih",
    #     "lists": {
    #         "ptw": False,
    #         "watching": True,
    #         "completed": True,
    #         "onhold": False,
    #         "dropped": False,
    #     },

    #     "rounds": 3,
    #     "themes": 6,
    #     "questions": 6,
    #     # "rounds": 1,
    #     # "themes": 2,
    #     # "questions": 2,

    #     "animeTypes": {
    #         "tv": True,
    #         "movie": True,
    #         "ova": True,
    #         "ona": True,
    #         "special": False
    #     },

    #     "openings": {
    #         "include": True,
    #         "count": 80,
    #     },
    #     "endings": {
    #         "include": True,
    #         "count": 28,
    #     },
    #     "inserts": {
    #         "include": False,
    #         "count": 10,
    #     },
        
    #     "difficulty": {
    #         "min": 50,
    #         "max": 100,
    #     }
    # }

    offset = 0
    animes_ids = []
    
    debug_log('начинаем пиздить анимки с майанимелиста')

    while True:
        res = requests.get('https://myanimelist.net/animelist/{0}/load.json?offset={1}&status=7'.format(settings["malName"], offset))

        response = json.loads(res.text)

        if not len(response) > 0:
            break

        for i in range(len(response)):
            if response[i]["status"] == 1:
                if not settings['lists']['watching']:
                    continue
            elif response[i]["status"] == 2:
                if not settings['lists']['completed']:
                    continue
            elif response[i]["status"] == 3:
                if not settings['lists']['onhold']:
                    continue
            elif response[i]["status"] == 4:
                if not settings['lists']['dropped']:
                    continue
            elif response[i]["status"] == 6:
                if not settings['lists']['ptw']:
                    continue

            animes_ids.append(response[i]["anime_id"])
            
            debug_log('готова проходка: {0} / анимок: {1}'.format(str(offset), str(len(animes_ids))))

        offset += 300
    
    debug_log('анимки подгружены')
    
    songs = []

    debug_log('получаем сонги')

    for i in range(0, len(animes_ids), 300):
        send_data = {
            "malIds": animes_ids[i:i+300],
        }

        res = requests.post('https://anisongdb.com/api/malIDs_request', json=send_data)

        response = json.loads(res.text)
        
        for res_song in range(len(response)):
            if response[i]["songDifficulty"] == None:
                debug_log('сонг: {0} - нет сложности, скип'.format(str(response[i]['annSongId'])))
                continue

            if response[i]["audio"] == None:
                debug_log('сонг: {0} - нет аудио, скип'.format(str(response[i]['annSongId'])))
                continue

            if not (response[i]["songDifficulty"] >= settings["difficulty"]["min"] and response[i]["songDifficulty"] <= settings["difficulty"]["max"]):
                debug_log('сонг: {0} - не подходит по сложности, скип'.format(str(response[i]['annSongId'])))
                continue

            if response[res_song]["songType"].split(" ")[0] == "Opening" and not settings["openings"]["include"]:
                debug_log('сонг: {0} - опенинги не включены в список, скип'.format(str(response[res_song]['annSongId'])))
                continue
                
            if response[res_song]["songType"].split(" ")[0] == "Ending" and not settings["endings"]["include"]:
                debug_log('сонг: {0} - эндинги не включены в список, скип'.format(str(response[res_song]['annSongId'])))
                continue
            
            if response[res_song]["songType"].split(" ")[0] == "Insert" and not settings["inserts"]["include"]:
                debug_log('сонг: {0} - инсерты не включены в список, скип'.format(str(response[res_song]['annSongId'])))
                continue

            match response[res_song]["animeType"]:
                case "TV":
                    if not settings["animeTypes"]["tv"]:
                        debug_log('сонг: {0} - тв не включен в список, скип'.format(str(response[res_song]['annSongId'])))
                        continue
                case "Movie":
                    if not settings["animeTypes"]["movie"]:
                        debug_log('сонг: {0} - фильмы не включены в список, скип'.format(str(response[res_song]['annSongId'])))
                        continue
                case "OVA":
                    if not settings["animeTypes"]["ova"]:
                        debug_log('сонг: {0} - ова не включен в список, скип'.format(str(response[res_song]['annSongId'])))
                        continue
                case "ONA":
                    if not settings["animeTypes"]["ona"]:
                        debug_log('сонг: {0} - она не включен в список, скип'.format(str(response[res_song]['annSongId'])))
                        continue
                case "Special":
                    if not settings["animeTypes"]["special"]:
                        debug_log('сонг: {0} - спешл не включен в список, скип'.format(str(response[res_song]['annSongId'])))
                        continue
                case _:
                    continue
            
            songs.append(response[res_song])
            
        debug_log('готова проходка: {0} / сонгов: {1}'.format(str(i), str(len(songs))))

    debug_log('сонги подгружены')

    debug_log('шаффлим ссонги')
    for j in range(10):
        random.shuffle(songs)
    debug_log('зашафлено.')

    new_songs = []
    franchises = []
    loc_fr = []
        
    debug_log('отбираем только годные опенинги')

    for i in range(len(songs) - 1):
        debug_log('смотрим: {0} / всего сонгов: {1}'.format(str(songs[i]['annSongId']), str(len(new_songs))))

        if len(new_songs) > settings['rounds'] * settings['themes'] * settings['questions']:
            debug_log('сонг: {0} - стал последним в списке'.format(str(songs[i]['annSongId'])))
            break

        # if songs[i]["songDifficulty"] == None:
        #     debug_log('сонг: {0} - нет сложности, скип'.format(str(songs[i]['annSongId'])))
        #     continue

        # if songs[i]["audio"] == None:
        #     debug_log('сонг: {0} - нет аудио, скип'.format(str(songs[i]['annSongId'])))
        #     continue

        # if not (songs[i]["songDifficulty"] >= settings["difficulty"]["min"] and songs[i]["songDifficulty"] <= settings["difficulty"]["max"]):
        #     debug_log('сонг: {0} - не подходит по сложности, скип'.format(str(songs[i]['annSongId'])))
        #     continue
        
        # if songs[i]["songType"].split(" ")[0] == "Opening" and not settings["openings"]["include"]:
        #     debug_log('сонг: {0} - опенинги не включены в список, скип'.format(str(songs[i]['annSongId'])))
        #     continue
            
        # if songs[i]["songType"].split(" ")[0] == "Ending" and not settings["endings"]["include"]:
        #     debug_log('сонг: {0} - эндинги не включены в список, скип'.format(str(songs[i]['annSongId'])))
        #     continue
        
        # if songs[i]["songType"].split(" ")[0] == "Insert" and not settings["inserts"]["include"]:
        #     debug_log('сонг: {0} - инсерты не включены в список, скип'.format(str(songs[i]['annSongId'])))
        #     continue
            
        if len(new_songs) > 0:
            match songs[i]["songType"].split(" ")[0]:
                case "Opening":
                    song_types_openings_len = len(list(filter(song_types_openings, new_songs)))
                    if not song_types_openings_len <= settings["openings"]["count"]:
                        debug_log('сонг: {0} - перебор по опенингам, скип'.format(str(songs[i]['annSongId'])))
                        continue
                case "Ending":
                    song_types_endings_len = len(list(filter(song_types_endings, new_songs)))
                    if not song_types_endings_len <= settings["endings"]["count"]:
                        debug_log('сонг: {0} - перебор по эндингам, скип'.format(str(songs[i]['annSongId'])))
                        continue
                case "Insert":
                    song_types_inserts_len = len(list(filter(song_types_inserts, new_songs)))
                    if not song_types_inserts_len <= settings["inserts"]["count"]:
                        debug_log('сонг: {0} - перебор по инсертам, скип'.format(str(songs[i]['annSongId'])))
                        continue
                case _:
                    continue

        #     match songs[i]["animeType"]:
        #         case "TV":
        #             if not settings["animeTypes"]["tv"]:
        #                 debug_log('сонг: {0} - тв не включен в список, скип'.format(str(songs[i]['annSongId'])))
        #                 continue
        #         case "Movie":
        #             if not settings["animeTypes"]["movie"]:
        #                 debug_log('сонг: {0} - фильмы не включены в список, скип'.format(str(songs[i]['annSongId'])))
        #                 continue
        #         case "OVA":
        #             if not settings["animeTypes"]["ova"]:
        #                 debug_log('сонг: {0} - ова не включен в список, скип'.format(str(songs[i]['annSongId'])))
        #                 continue
        #         case "ONA":
        #             if not settings["animeTypes"]["ona"]:
        #                 debug_log('сонг: {0} - она не включен в список, скип'.format(str(songs[i]['annSongId'])))
        #                 continue
        #         case "Special":
        #             if not settings["animeTypes"]["special"]:
        #                 debug_log('сонг: {0} - спешл не включен в список, скип'.format(str(songs[i]['annSongId'])))
        #                 continue
        #         case _:
        #             continue
            
        s_song_has = False
        for s_song in range(len(new_songs)):
            if songs[i]["annId"] == new_songs[s_song]["annId"]:
                s_song_has = True
                break
            if songs[i]["annSongId"] == new_songs[s_song]["annSongId"]:
                s_song_has = True
                break
        if songs[i]["annId"] in loc_fr:
            debug_log('сонг: {0} - аниме франшиза уже есть, скип'.format(str(songs[i]['annSongId'])))
            continue
        if s_song_has:
            debug_log('сонг: {0} - сонг уже есть, скип'.format(str(songs[i]['annSongId'])))
            continue

        query = f'''
        {{
                animes(ids: "{songs[i]['linked_ids']['myanimelist']}") {{
                    id
                    malId
                    name
                    russian
                    franchise
                }}
            }}
        '''
        
        response = requests.post('https://shikimori.one/api/graphql',
            json={"query": query},
            headers=headers
        )
        response.raise_for_status()
        res = json.loads(response.content)
        shiki_anime = res['data']['animes'][0]
        if shiki_anime['franchise'] in franchises:
            debug_log('сонг: {0} - франшиза уже есть, скип'.format(str(songs[i]['annSongId'])))
            continue

        franchises.append(shiki_anime['franchise'])
        loc_fr.append(songs[i]['annId'])
        songs[i]['russian'] = shiki_anime['russian']
        new_songs.append(songs[i])
        
        debug_log('отобран: {0}'.format(str(songs[i]['annSongId'])))
        time.sleep(0.3)

    debug_log('сонги отобраны, ништяк')

    debug_log('собираем пак епта')

    openings_count = 0
    endings_count = 0
    inserts_count = 0

    curr_char = 0
    f_name = random.random()
    os.makedirs("./out")
    os.makedirs("./out/Audio")
    os.makedirs("./build_{0}_{1}".format(settings['malName'], f_name))
    
    z = ZipFile('./build_{0}_{1}/sigame.siq'.format(settings['malName'], f_name), "w")
    folder = "./out"
    
    root = ET.Element('package')
    root.set("name", "SiGame Anime Pack")
    root.set("version", "5")
    root.set("id", "69831e55-f450-4fdf-8200-ee18d9d8d413")
    root.set("xmlns", "https://github.com/VladimirKhil/SI/blob/master/assets/siq_5.xsd")

    tags = ET.Element("tags")
    tag = ET.Element("tag")
    tag.text = "Аниме"
    tags.append(tag)
    root.append(tags)
    
    info = ET.Element("info")
    authors = ET.Element("authors")
    author = ET.Element("author")
    author.text = "Kao Generator"
    info.append(authors)
    authors.append(author)
    root.append(info)
    
    rounds = ET.Element("rounds")
    
    tempRounds = 0
    while tempRounds < settings['rounds']:
        if curr_char > len(new_songs) - 1: 
            break

        round = ET.Element("round")
        round.set("name", "round {}".format(tempRounds + 1))
        
        themes = ET.Element("themes")
        
        tempThemes = 0
        while tempThemes < settings['themes']:
            if curr_char > len(new_songs) - 1: 
                break

            theme = ET.Element("theme")

            theme.set("name", "JUST SONGS")
            
            questions = ET.Element("questions")

            tempQuestions = 0
            while tempQuestions < settings['questions']:
                if curr_char > len(new_songs) - 1: 
                    break
                
                out_file = Path("./out/Audio/sw_{}".format(new_songs[curr_char]["audio"])).expanduser()
                response = requests.request("GET", "https://naedist.animemusicquiz.com/{}".format(new_songs[curr_char]["audio"]))
                response.raise_for_status()
                # if response.status_code == 200:
                with open(out_file, "wb") as fout:
                    fout.write(response.content)
                    
                song = AudioSegment.from_mp3("./out/Audio/sw_{}".format(new_songs[curr_char]["audio"]))
                start = random.randrange(0, int(new_songs[curr_char]["songLength"] * 1000) - 21000)
                end = start + 20000
                cut_song = song[start:end] 
                cut_song.export("./out/Audio/{}".format(new_songs[curr_char]["audio"]), format="mp3", bitrate="128k")
                os.remove("./out/Audio/sw_{}".format(new_songs[curr_char]["audio"]))

                question = ET.Element("question")
                question.set("price", "1")
                
                params = ET.Element("params")
                param = ET.Element("param")
                param.set("name", "question")
                param.set("type", "content")
                
                item1 = ET.Element("item")
                item1.set("waitForFinish", "False")
                item1.text = "Guess Anime by " + get_reduct_type(new_songs[curr_char]["songType"].split(" ")[0])
                param.append(item1)
                
                item2 = ET.Element("item")
                item2.set("type", "audio")
                item2.set("isRef", "True")
                item2.set("placement", "background")
                item2.text = new_songs[curr_char]["audio"]
                param.append(item2)
                
                params.append(param)
                
                right = ET.Element("right")
                answer = ET.Element("answer")
                # answer.text = shiki_anime['russian'] + " - " + data[curr_char]["animeJPName"] + " (" + data[curr_char]["animeCategory"] + ") - (" + data[curr_char]["songType"] + ") - (" + str(int(data[curr_char]["songDifficulty"])) + ") - (" + data[curr_char]["songArtist"] + " - " + data[curr_char]["songName"] + ")"
                answer.text = new_songs[curr_char]['russian'] + " - " + new_songs[curr_char]["animeJPName"] + " (" + new_songs[curr_char]["animeCategory"] + ") - (" + new_songs[curr_char]["songType"] + ") - (" + str(int(new_songs[curr_char]["songDifficulty"])) + ") - (" + new_songs[curr_char]["songArtist"] + " - " + new_songs[curr_char]["songName"] + ")"
                right.append(answer)
                
                question.append(params)
                question.append(right)
                
                questions.append(question)

                # franchises.append(shiki_anime['franchise'])

                match new_songs[curr_char]["songType"].split(" ")[0]:
                    case "Opening":
                        openings_count += 1
                    case "Ending":
                        endings_count += 1
                    case "Insert":
                        inserts_count += 1
                    case _:
                        continue

                tempQuestions += 1

                curr_char += 1
            theme.append(questions)
            
            themes.append(theme)
            
            tempThemes += 1
            
        round.append(themes)
        
        rounds.append(round)

        tempRounds += 1
    
    root.append(rounds)
    
    tree = ET.ElementTree(root)
    tree.write('./out/content.xml', encoding="utf-8", xml_declaration=True)
    
    shutil.copy2('./example/example.siq', './build_{0}_{1}/sigame.siq'.format(settings['malName'], f_name))
    
    for folder_name, subfolders, filenames in os.walk(folder):
        for filename in filenames:
            file_path = os.path.join(folder_name, filename)
            z.write(file_path, arcname=os.path.relpath(file_path, folder))
    
    z.close()
    
    shutil.rmtree('./out')
    
    debug_log('все, в пизду, идите играйте')

gen()
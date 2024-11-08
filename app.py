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

# with open('./data.json') as file:
#     settings = json.load(file)

# print(settings)

settings = {
    "gen_type": "mal_user",
    "malName": "AmqPsih",
    "lists": {
        "ptw": False,
        "watching": True,
        "completed": True,
        "onhold": False,
        "dropped": False,
    },

    "rounds": 3,
    "themes": 6,
    "questions": 6,
    # "rounds": 1,
    # "themes": 2,
    # "questions": 2,

    "animeTypes": {
        "tv": True,
        "movie": True,
        "ova": True,
        "ona": True,
        "special": False
    },

    "openings": {
        "include": True,
        "count": 80,
    },
    "endings": {
        "include": True,
        "count": 28,
    },
    "inserts": {
        "include": False,
        "count": 10,
    },
    
    "difficulty": {
        "min": 50,
        "max": 100,
    }
}

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip, deflate, br',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
}

def get_reduct_type(type):
    if type == "Opening":
        return "OP"
    if type == "Ending":
        return "ED"
    if type == "Insert":
        return "INS"

def fetch_mal_list():
    offset = 0
    animes = []
    
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

            animes.append(response[i]["anime_id"])

        offset += 300

    return animes

not_found_list = [
    'r9qhim.mp3',
    'os28yw.mp3',
    'f2r9or.mp3',
    'mnc0no.mp3',
    'oshfc6.mp3'
]

def get_songs_from_anisong(data):
    songs = []

    for i in range(0, len(data), 300):
        send_data = {
            "malIds": data[i:i+300],
        }

        res = requests.post('https://anisongdb.com/api/malIDs_request', json=send_data)

        response = json.loads(res.text)
        
        for res_song in range(len(response)):
            if response[res_song]['audio'] in not_found_list:
                print(response[res_song])
                continue
            songs.append(response[res_song])

        time.sleep(1)

    return songs

def shuffle_songs(data):
    new_data = data

    for j in range(10):
        random.shuffle(new_data)
    
    return new_data

def get_songs(data):
    new_songs = []
    franchises = []

    # def song_types_openings(song):
    #     if song["songType"].split(" ")[0] == "Opening":
    #         return True
    #     else:
    #         return False
    # def song_types_endings(song):
    #     if song["songType"].split(" ")[0] == "Ending":
    #         return True
    #     else:
    #         return False
    # def song_types_inserts(song):
    #     if song["songType"].split(" ")[0] == "Insert":
    #         return True
    #     else:
    #         return False
        
    for i in range(len(data)):
        if data[i]["songDifficulty"] == None:
            continue

        if data[i]["audio"] == None:
            continue

        if not (data[i]["songDifficulty"] >= settings["difficulty"]["min"] and data[i]["songDifficulty"] <= settings["difficulty"]["max"]):
            continue
        
        if data[i]["songType"].split(" ")[0] == "Opening" and not settings["openings"]["include"]:
            continue
            
        if data[i]["songType"].split(" ")[0] == "Ending" and not settings["endings"]["include"]:
            continue
        
        if data[i]["songType"].split(" ")[0] == "Insert" and not settings["inserts"]["include"]:
            continue
            
        if len(new_songs) > 0:
            match data[i]["songType"].split(" ")[0]:
                case "Opening":
                    song_types_openings_len = len(list(filter(song_types_openings, new_songs)))
                    if not song_types_openings_len <= settings["openings"]["count"]:
                        continue
                case "Ending":
                    song_types_endings_len = len(list(filter(song_types_endings, new_songs)))
                    if not song_types_endings_len <= settings["endings"]["count"]:
                        continue
                case "Insert":
                    song_types_inserts_len = len(list(filter(song_types_inserts, new_songs)))
                    if not song_types_inserts_len <= settings["inserts"]["count"]:
                        continue
                case _:
                    continue
            match data[i]["animeType"]:
                case "TV":
                    if not settings["animeTypes"]["tv"]:
                        continue
                case "Movie":
                    if not settings["animeTypes"]["movie"]:
                        continue
                case "OVA":
                    if not settings["animeTypes"]["ova"]:
                        continue
                case "ONA":
                    if not settings["animeTypes"]["ona"]:
                        continue
                case "Special":
                    if not settings["animeTypes"]["special"]:
                        continue
                case _:
                    continue
            
        s_song_has = False
        for s_song in range(len(new_songs)):
            if data[i]["annId"] == new_songs[s_song]["annId"]:
                s_song_has = True
            if data[i]["annSongId"] == new_songs[s_song]["annSongId"]:
                s_song_has = True
        if s_song_has:
            continue

        query = f'''
        {{
                animes(ids: "{data[i]['linked_ids']['myanimelist']}") {{
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
            continue

        franchises.append(shiki_anime['franchise'])
        data[i]['russian'] = shiki_anime['russian']
        new_songs.append(data[i])
        # time.sleep(0.3)

    return new_songs


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

def generate_random_pack(data):
    print(len(data))

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
        if curr_char > len(data) - 1: 
            break

        round = ET.Element("round")
        round.set("name", "round {}".format(tempRounds + 1))
        
        themes = ET.Element("themes")
        
        tempThemes = 0
        while tempThemes < settings['themes']:
            if curr_char > len(data) - 1: 
                break

            theme = ET.Element("theme")

            theme.set("name", "JUST SONGS")
            
            questions = ET.Element("questions")

            tempQuestions = 0
            while tempQuestions < settings['questions']:
                if curr_char > len(data) - 1: 
                    break

                # song_type_count_overkill = False
                # match data[curr_char]["songType"].split(" ")[0]:
                #     case "Opening":
                #         if not openings_count <= settings["openings"]["count"]:
                #             song_type_count_overkill = True
                #     case "Ending":
                #         if not endings_count <= settings["endings"]["count"]:
                #             song_type_count_overkill = True
                #     case "Insert":
                #         if not inserts_count <= settings["inserts"]["count"]:
                #             song_type_count_overkill = True
                #     case _:
                #         continue

                # query = f'''
                # {{
                #         animes(ids: "{data[curr_char]['linked_ids']['myanimelist']}") {{
                #             id
                #             malId
                #             name
                #             russian
                #             franchise
                #         }}
                #     }}
                # '''
                # response = requests.post('https://shikimori.one/api/graphql',
                #     json={"query": query},
                #     headers=headers
                # )
                # res = json.loads(response.content)

                # shiki_anime = res['data']['animes'][0]

                # if not shiki_anime['franchise'] in franchises and not song_type_count_overkill:

                question = ET.Element("question")
                question.set("price", "1")
                
                params = ET.Element("params")
                param = ET.Element("param")
                param.set("name", "question")
                param.set("type", "content")
                
                item1 = ET.Element("item")
                item1.set("waitForFinish", "False")
                item1.text = "Guess Anime by " + get_reduct_type(data[curr_char]["songType"].split(" ")[0])
                param.append(item1)
                
                item2 = ET.Element("item")
                item2.set("type", "audio")
                item2.set("isRef", "True")
                item2.set("placement", "background")
                item2.text = data[curr_char]["audio"]
                param.append(item2)
                
                params.append(param)
                
                right = ET.Element("right")
                answer = ET.Element("answer")
                # answer.text = shiki_anime['russian'] + " - " + data[curr_char]["animeJPName"] + " (" + data[curr_char]["animeCategory"] + ") - (" + data[curr_char]["songType"] + ") - (" + str(int(data[curr_char]["songDifficulty"])) + ") - (" + data[curr_char]["songArtist"] + " - " + data[curr_char]["songName"] + ")"
                answer.text = data[curr_char]['russian'] + " - " + data[curr_char]["animeJPName"] + " (" + data[curr_char]["animeCategory"] + ") - (" + data[curr_char]["songType"] + ") - (" + str(int(data[curr_char]["songDifficulty"])) + ") - (" + data[curr_char]["songArtist"] + " - " + data[curr_char]["songName"] + ")"
                right.append(answer)
                
                question.append(params)
                question.append(right)
                
                questions.append(question)
                
                out_file = Path("./out/Audio/sw_{}".format(data[curr_char]["audio"])).expanduser()
                response = requests.request("GET", "https://naedist.animemusicquiz.com/{}".format(data[curr_char]["audio"]))
                response.raise_for_status()
                print(response.raise_for_status())
                # if response.status_code == 200:
                with open(out_file, "wb") as fout:
                    fout.write(response.content)
                    
                song = AudioSegment.from_mp3("./out/Audio/sw_{}".format(data[curr_char]["audio"]))
                start = random.randrange(0, int(data[curr_char]["songLength"] * 1000) - 21000)
                end = start + 20000
                cut_song = song[start:end] 
                cut_song.export("./out/Audio/{}".format(data[curr_char]["audio"]), format="mp3", bitrate="128k")
                os.remove("./out/Audio/sw_{}".format(data[curr_char]["audio"]))

                # franchises.append(shiki_anime['franchise'])

                match data[curr_char]["songType"].split(" ")[0]:
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

def get_random_songs():
    max_songs = settings["rounds"] * settings["themes"] * settings["questions"]
    songs = []

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

    while(len(songs) < max_songs):
        res = requests.post('https://anisongdb.com/api/get_50_random_songs')

        response = json.loads(res.text)
        
        for res_song in range(len(response)):
            if response[res_song]["songDifficulty"] == None:
                continue

            if not (response[res_song]["songDifficulty"] >= settings["difficulty"]["min"] and response[res_song]["songDifficulty"] <= settings["difficulty"]["max"]):
                continue
            
            if response[res_song]["songType"].split(" ")[0] == "Opening" and not settings["openings"]["include"]:
                continue
                
            if response[res_song]["songType"].split(" ")[0] == "Ending" and not settings["endings"]["include"]:
                continue
            
            if response[res_song]["songType"].split(" ")[0] == "Insert" and not settings["inserts"]["include"]:
                continue
                
            if len(songs) > 0:
                if not len(list(filter(song_types_openings, songs))) <= settings["openings"]["count"]:
                    continue
                if not len(list(filter(song_types_endings, songs))) <= settings["endings"]["count"]:
                    continue
                if not len(list(filter(song_types_inserts, songs))) <= settings["inserts"]["count"]:
                    continue

            if response[res_song]["audio"] == None:
                continue
                
            for s_song in range(len(songs)):
                if response[res_song]["annId"] == songs[s_song]["annId"]:
                    continue

            songs.append(response[res_song])

            time.sleep(1)
    
    return songs

def gen_by_mal():
    mal_res = fetch_mal_list()
    songs_mal_res = get_songs_from_anisong(mal_res)
    songs_shuffled_res = shuffle_songs(songs_mal_res)
    songs_res = get_songs(songs_shuffled_res)
    generate_random_pack(songs_res)

def gen_by_random():
    generate_random_pack(get_random_songs())

def main():
    if settings["gen_type"] == 'anisong_random':
        gen_by_random()
    if settings["gen_type"] == 'mal_user':
        gen_by_mal()

main()
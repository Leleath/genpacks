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
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

with open('./popular_animes/popular_animes.txt') as file:
    popular_animes = file.read().split('\n')

del popular_animes[0]
del popular_animes[-1]

for i in range(500):
    random.shuffle(popular_animes)

# 

with open('./data.json') as file:
    sett = json.load(file)
    
def debug_log(mess):
    if sett['log']:
        print(mess)

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

def gen(settings):
    print('Настройки подгружены')
    debug_log('Лог включен')
    
    debug_log('Получаем сонги')
    
    songs = []

    for i in range(0, 3000, 300):
        send_data = {
            "malIds": popular_animes[i:i+300],
        }

        res = requests.post('https://anisongdb.com/api/malIDs_request', json=send_data)

        response = json.loads(res.text)
        
        for res_song in range(len(response)):
            if response[res_song]["songDifficulty"] == None:
                debug_log('Сонг: {0} - Нет сложности, пропускаем'.format(str(response[res_song]['annSongId'])))
                continue

            if response[res_song]["audio"] == None:
                debug_log('Сонг: {0} - Нет аудио, пропускаем'.format(str(response[res_song]['annSongId'])))
                continue

            if response[res_song]["isDub"]:
                if settings['dub']:
                    debug_log('Сонг: {0} - Дубляж не включен, пропускаем'.format(str(response[res_song]['annSongId'])))
                    continue

            if response[res_song]["isRebroadcast"]:
                if settings['rebroadcast']:
                    debug_log('Сонг: {0} - Реброадкаст не включен, пропускаем'.format(str(response[res_song]['annSongId'])))
                    continue

            if not (response[res_song]["songDifficulty"] >= settings["difficulty"]["min"] and response[res_song]["songDifficulty"] <= settings["difficulty"]["max"]):
                debug_log('Сонг: {0} - Не подходит по сложности, пропускаем'.format(str(response[res_song]['annSongId'])))
                continue

            if response[res_song]["songType"].split(" ")[0] == "Opening" and not settings["openings"]["include"]:
                debug_log('Сонг: {0} - Опенинги не включены в список, пропускаем'.format(str(response[res_song]['annSongId'])))
                continue
                
            if response[res_song]["songType"].split(" ")[0] == "Ending" and not settings["endings"]["include"]:
                debug_log('Сонг: {0} - Эндинги не включены в список, пропускаем'.format(str(response[res_song]['annSongId'])))
                continue
            
            if response[res_song]["songType"].split(" ")[0] == "Insert" and not settings["inserts"]["include"]:
                debug_log('Сонг: {0} - Инсерты не включены в список, пропускаем'.format(str(response[res_song]['annSongId'])))
                continue

            match response[res_song]["animeType"]:
                case "TV":
                    if not settings["animeTypes"]["tv"]:
                        debug_log('Сонг: {0} - TV не включены в список, пропускаем'.format(str(response[res_song]['annSongId'])))
                        continue
                case "Movie":
                    if not settings["animeTypes"]["movie"]:
                        debug_log('Сонг: {0} - Фильмы не включены в список, пропускаем'.format(str(response[res_song]['annSongId'])))
                        continue
                case "OVA":
                    if not settings["animeTypes"]["ova"]:
                        debug_log('Сонг: {0} - OVA не включены в список, пропускаем'.format(str(response[res_song]['annSongId'])))
                        continue
                case "ONA":
                    if not settings["animeTypes"]["ona"]:
                        debug_log('Сонг: {0} - ONA не включены в список, пропускаем'.format(str(response[res_song]['annSongId'])))
                        continue
                case "Special":
                    if not settings["animeTypes"]["special"]:
                        debug_log('Сонг: {0} - Спешлы не включены в список, пропускаем'.format(str(response[res_song]['annSongId'])))
                        continue
                case _:
                    continue
            
            songs.append(response[res_song])
            
        debug_log('Цикл: {0} / Всего сонгов: {1}'.format(str(i), str(len(songs))))
        
        time.sleep(0.3)

    debug_log('Сонги подгружены')

    debug_log('Шафлим сонги')
    for j in range(500):
        random.shuffle(songs)
    debug_log('Шафл завершен.')
        
    debug_log('Отбираем сонги')

    new_songs = []
    franchises = []
    loc_fr = []

    for i in range(len(songs) - 1):
        debug_log('Смотрим: {0} / Всего сонгов: {1}'.format(str(songs[i]['annSongId']), str(len(new_songs))))

        if len(new_songs) > (settings['rounds'] * settings['themes'] * settings['questions']):
            debug_log('Сонг: {0} - Стал последним в списке, пропускаем'.format(str(songs[i]['annSongId'])))
            break

        if len(new_songs) > 0:
            match songs[i]["songType"].split(" ")[0]:
                case "Opening":
                    song_types_openings_len = len(list(filter(song_types_openings, new_songs)))
                    if not song_types_openings_len <= settings["openings"]["count"]:
                        debug_log('Сонг: {0} - Перебор по опенингам, пропускаем'.format(str(songs[i]['annSongId'])))
                        continue
                case "Ending":
                    song_types_endings_len = len(list(filter(song_types_endings, new_songs)))
                    if not song_types_endings_len <= settings["endings"]["count"]:
                        debug_log('Сонг: {0} - Перебор по эндингам, пропускаем'.format(str(songs[i]['annSongId'])))
                        continue
                case "Insert":
                    song_types_inserts_len = len(list(filter(song_types_inserts, new_songs)))
                    if not song_types_inserts_len <= settings["inserts"]["count"]:
                        debug_log('Сонг: {0} - Перебор по инсертам, пропускаем'.format(str(songs[i]['annSongId'])))
                        continue
                case _:
                    continue

        s_song_has = False
        for s_song in range(len(new_songs)):
            if songs[i]["annId"] == new_songs[s_song]["annId"]:
                s_song_has = True
                break
            if songs[i]["annSongId"] == new_songs[s_song]["annSongId"]:
                s_song_has = True
                break
        if s_song_has:
            debug_log('Сонг: {0} - Сонг уже есть, пропускаем'.format(str(songs[i]['annSongId'])))
            continue

        if songs[i]["annId"] in loc_fr:
            debug_log('Сонг: {0} - Аниме франшиза уже есть, пропускаем'.format(str(songs[i]['annSongId'])))
            continue

        query = f'''
        {{
                animes(ids: "{songs[i]['linked_ids']['myanimelist']}") {{
                    id
                    malId
                    name
                    russian
                    franchise
                    
                    screenshots {{ id originalUrl x166Url x332Url }}
                }}
            }}
        '''
        
        response = requests.post('https://shikimori.one/api/graphql',
            json={"query": query},
            headers=headers
        )
        res = json.loads(response.content)
        shiki_anime = res['data']['animes'][0]
        if shiki_anime['franchise'] in franchises:
            debug_log('Сонг: {0} - Франшиза уже есть, пропускаем'.format(str(songs[i]['annSongId'])))
            continue

        franchises.append(shiki_anime['franchise'])
        loc_fr.append(songs[i]['annId'])
        songs[i]['russian'] = shiki_anime['russian']
        
        if settings['images']:
            if len(shiki_anime['screenshots']) > 4:
                rand_images = []
                while not len(rand_images) == 4:
                    rand_image_range = random.randrange(len(shiki_anime['screenshots']))

                    new_img = {
                        "index": rand_image_range,
                        "src": shiki_anime['screenshots'][rand_image_range]['originalUrl']
                    }

                    if not (new_img in rand_images):
                        rand_images.append(new_img)

                songs[i]['rand_images'] = rand_images
            else:
                debug_log('Сонг: {0} - У тайтла нет скришотов, пропускаем'.format(str(songs[i]['annSongId'])))
                continue

        new_songs.append(songs[i])
        
        debug_log('Отобран: {0}'.format(str(songs[i]['annSongId'])))

        time.sleep(0.3)

    debug_log('Сонги отобраны')

    debug_log('Собираем пак')

    openings_count = 0
    endings_count = 0
    inserts_count = 0

    curr_char = 0
    f_name = random.random()
    os.makedirs("./temp")
    os.makedirs("./temp/Audio")
    os.makedirs("./temp/Images")
    os.makedirs("./builds/build_{0}_{1}".format(settings['malName'], f_name))
    
    z = ZipFile('./builds/build_{0}_{1}/sigame.siq'.format(settings['malName'], f_name), "w")
    folder = "./temp"
    
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
                if settings['images']:
                    item2.set("duration", "00:00:13")
                else:
                    item2.set("duration", "00:00:15")
                item2.text = new_songs[curr_char]["audio"]
                param.append(item2)
                
                if settings['images']:
                    item3 = ET.Element("item")
                    item3.set("type", "image")
                    item3.set("isRef", "True")
                    item3.set("duration", "00:00:02")
                    item3.text = str(new_songs[curr_char]["annId"]) + ".jpg"
                    param.append(item3)
                
                params.append(param)
                
                right = ET.Element("right")
                answer = ET.Element("answer")
                answer.text = new_songs[curr_char]['russian'] + " - " + new_songs[curr_char]["animeJPName"] + " (" + new_songs[curr_char]["animeCategory"] + ") - (" + new_songs[curr_char]["songType"] + ") - (" + str(int(new_songs[curr_char]["songDifficulty"])) + ") - (" + new_songs[curr_char]["songArtist"] + " - " + new_songs[curr_char]["songName"] + ")"
                right.append(answer)
                
                question.append(params)
                question.append(right)
                
                questions.append(question)

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

                debug_log('Добавлено в пак: {0}'.format(str(new_songs[curr_char]['annSongId'])))
                
                curr_char += 1
            theme.append(questions)
            
            themes.append(theme)
            
            tempThemes += 1
            
        round.append(themes)
        
        rounds.append(round)

        tempRounds += 1
    
    root.append(rounds)

    def download_song(song_s):
        debug_log('Скачиваем сонг: {0}'.format(str(song_s['annSongId'])))

        out_file = Path("./temp/Audio/sw_{}".format(song_s["audio"])).expanduser()
        response = requests.request("GET", "https://naedist.animemusicquiz.com/{}".format(song_s["audio"]))
        with open(out_file, "wb") as fout:
            fout.write(response.content)
            
        song = AudioSegment.from_mp3("./temp/Audio/sw_{}".format(song_s["audio"]))
        start = random.randrange(0, int(song_s["songLength"] * 1000) - ((settings["cut_audio"] * 1000) + 1))
        end = start + (settings["cut_audio"] * 1000)
        cut_song = song[start:end] 
        cut_song.export("./temp/Audio/{}".format(song_s["audio"]), format="mp3", bitrate="128k")
        os.remove("./temp/Audio/sw_{}".format(song_s["audio"]))
        
        debug_log('Сонг скачан: {0}'.format(str(song_s['annSongId'])))

        if settings['images']:
            debug_log('Скачиваем скриншоты: {0}'.format(str(song_s['annSongId'])))

            img_srcs = []

            for img_index in range(len(song_s["rand_images"])):
                new_src = "./temp/Images/{0}_{1}".format(str(img_index), str(song_s["annId"]) + ".jpg")

                out_file = Path(new_src).expanduser()
                response = requests.request("GET", song_s["rand_images"][img_index]['src'])
                with open(out_file, "wb") as fout:
                    fout.write(response.content)

                img_srcs.append(new_src)

            img1 = Image.open(img_srcs[0])
            img2 = Image.open(img_srcs[1])
            img3 = Image.open(img_srcs[2])
            img4 = Image.open(img_srcs[3])

            dst = Image.new('RGB', (img1.width * 2, img1.height * 2))

            dst.paste(img1, (0, 0))
            dst.paste(img2, (img1.width, 0))
            dst.paste(img3, (0, img1.height))
            dst.paste(img4, (img1.width, img1.height))

            newsize = (1920, 1080)
            dst.resize(newsize)
            
            dst.save("./temp/Images/{}".format(str(song_s["annId"]) + ".jpg"))

            for img in img_srcs:
                os.remove(img)

            debug_log('Скриншоты собраны: {0}'.format(str(song_s['annSongId'])))

    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(download_song, new_songs)

    tree = ET.ElementTree(root)
    tree.write('./temp/content.xml', encoding="utf-8", xml_declaration=True)
    
    shutil.copy2('./example/example.siq', './builds/build_{0}_{1}/sigame.siq'.format(settings['malName'], f_name))
    
    debug_log('Сохраняем пак')
    
    for folder_name, subfolders, filenames in os.walk(folder):
        for filename in filenames:
            file_path = os.path.join(folder_name, filename)
            z.write(file_path, arcname=os.path.relpath(file_path, folder))
    
    z.close()
    
    shutil.rmtree('./temp')
    
    debug_log('Пак собран, можно играть')

    return True

gen(sett)
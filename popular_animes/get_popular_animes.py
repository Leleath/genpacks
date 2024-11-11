import requests
import json
import time

page = 1
animes_count = 0

while True:
    res = requests.get('https://api.jikan.moe/v4/anime?order_by=popularity&page={0}'.format(page))

    response = json.loads(res.text)
    res_data = response['data']

    if not len(res_data) > 0:
        break

    f = open("./popular_animes/popular_animes.txt", "a")
    for i in range(len(res_data)):
        f.write(str(res_data[i]['mal_id']) + "\n")
        
        animes_count += 1
    f.close()
        
    print('Страница: {0} / Всего аниме: {1}'.format(str(page), str(animes_count)))

    page += 1

    time.sleep(1)
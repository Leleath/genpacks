import requests
import json
import time

page = 1
animes_count = 0

f = open("./popular_animes/all_animes.txt", "a")

count = 0
while True:
    f.write(str(count) + "\n")

    if count > 60000:
        break

    count += 1

f.close()
## Anime Songs Pack Generator

Перед скачиванием поставьте на комп ffmpeg и добавьте папку bin в переменные среды Path.

*idk*

Переименуйте файл data_example.json в data.json !

Дополнительные библиотеки:  
```
requests
shutil
zipfile
pydub
concurrent.futures
PIL
```

```python
{
    "log": True, # Вести лог в консоль

    "malName": "Username", # Имя пользователя MAL

    # Включить в генерацию отдельные списки
    "lists": {
        "ptw": False, # "Буду смотреть"
        "watching": True, # "Cмотрю"
        "completed": True, # "Просмотрено"
        "onhold": False, # "Отложено"
        "dropped": False  # "Брошено"
    },

    "rounds": 3, # Количество раундов
    "themes": 6, # Количество тем
    "questions": 6,  # Количество вопросов
    # Слишком много не делайте. Долгая генерация + большой вес пака

    # Включить в генерацию отдельные типы аниме
    "animeTypes": {
        "tv": True, # "Сериал"
        "movie": True, # "Фильм"
        "ova": True, # "OVA"
        "ona": True, # "ONA"
        "special": False # "Спешл"
    },

    # Включить в генерацию отдельные типы сонгов
    # "Опенинги"
    "openings": {
        "include": True, # Опенинги
        "count": 108 # Количество опенингов во всем паке
    },

    # "Эндинги"
    "endings": {
        "include": False, # Эндинги
        "count": 28 # Количество во всем паке
    }, 
    
    # "Инсерты"
    "inserts": {
        "include": False, # Инсерты
        "count": 10 # Количество во всем паке
    },
    
    # Настройка сложности сонгов
    "difficulty": {
        "min": 0, # Минимальная сложность
        "max": 60 # Максимальная сложность
    },
    # Сложность по AMQ

    # Генерировать картинки после сонгов
    "images": True,

    # Время на угадывание (в секундах)
    "cut_audio": 20
}
```
# akniga_downloader
Загружает файлы аудиокниг с сайта [akniga](https://akniga.org).
Скрипт может использоваться самостоятельно, но предназначен для работы с телеграм ботом [tg-combine](https://github.com/fabrikant/tg-combine)

# Требования
1. Операционная система **Linux** тестировалось на ubuntu 24.04. На **Windows** должно работать, но не тестировалось.
1. [python3](https://www.python.org/) и venv. Чем новее, тем лучше. Тестировалось на 3.12.
1. Установленный [ffmpeg](https://www.ffmpeg.org/)

# Установка
Скачиваем любым способом исходный код. Например:  
```bash
git clone https://github.com/fabrikant/akniga_downloader.git
```
Переходим в каталог с исходным кодом и выполняем команду  
**Linux:**
```bash
./install.sh
```
**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
deactivate
```
Также необходимо открыть файл install.sh и скачать по ссылкам дополнительные модули (после команды wget).

# Использование на Linux и Windows
**Linux**

Выполнить скрипт **download-book.sh** с соответствующими параметрами
При запуске будет автоматически активировано виртуальное окружение, вызван скрипт python, а по окончанию работы деактивировано виртуальное окружение. Пример:
```bash
./download-book.sh --help
```

>**ВАЖНО!!!**
>
>**Для получения справки по доступным ключам, скрипт можно вызвать с параметром -h или --help.**

**Windows**

Перед запуском скрипта необходимо активировать виртуальное окружение командой:
```
venv\Scripts\activate
```
Далее скрипт вызывается командой аналогичной Linux, но вместо файла *sh* запускается соответствующий python файл. Например:
```
python3 download_book.py --help
```

# Использование
1. Загрузка книги:

    ```bash
    ./download-book.sh --output {/tmp/audiobooks} --url {https://akniga.org/vellington-devid-izolirovannyy-agent}
    ``` 
    >*Значения в фигурных скобках нужно заменить на свои.*

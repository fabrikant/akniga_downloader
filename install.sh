#! /bin/bash
DIR=$(dirname $0)
cd $DIR

#Загрузка общих для всех качалок модулей
rm -rf opf.py tg_sender.py common_arguments.py
wget https://raw.githubusercontent.com/fabrikant/litres_audiobooks_downloader/main/opf.py
wget https://raw.githubusercontent.com/fabrikant/litres_audiobooks_downloader/main/tg_sender.py
wget https://raw.githubusercontent.com/fabrikant/litres_audiobooks_downloader/main/common_arguments.py

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
deactivate

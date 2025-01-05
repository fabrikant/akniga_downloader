#! /bin/bash
DIR=$(dirname $0)
cd $DIR
./download_external_modules.sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
deactivate

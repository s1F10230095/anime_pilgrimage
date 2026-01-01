#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# ★ --clear を削除しました
python manage.py collectstatic --no-input

python manage.py migrate
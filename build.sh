#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# --clear を追加して、古いキャッシュを削除してから集め直します
python manage.py collectstatic --no-input --clear

python manage.py migrate
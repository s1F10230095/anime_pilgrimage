# 1. Python 3.10の軽量版をベースにする（Renderと同じバージョン）
FROM python:3.10-slim

# 2. Pythonがバッファ（一時保存）せず直接ログを出力するように設定
ENV PYTHONUNBUFFERED=1
# .pycファイルを作らないようにする
ENV PYTHONDONTWRITEBYTECODE=1

# 3. 必要なOSのライブラリをインストール
# (PostgreSQL接続用ライブラリ「libpq-dev」とコンパイル用「gcc」を入れる)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. 作業ディレクトリを作成
WORKDIR /app

# 5. ライブラリのリストをコピーしてインストール
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# 6. プロジェクトの全ファイルをコンテナ内にコピー
COPY . /app/

# 7. コンテナ起動時に実行するコマンド
# (Renderと同じgunicornを使って起動。ポート8000で待ち受け)
CMD ["gunicorn", "anime_pilgrimage.wsgi:application", "--bind", "0.0.0.0:8000"]
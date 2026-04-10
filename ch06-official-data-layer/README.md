# 第 6 章 Official data layer を使う！ - サポートページ

第 6 章で用いたコマンドは以下です。

### Data layer 側のセットアップ

```bash
# リポジトリのクローン
git clone https://github.com/Chainlit/chainlit-datalayer.git
cd chainlit-datalayer
# 環境設定
uv venv --python 3.13.4
uv pip install asyncpg boto3
source .venv/bin/activate
cp .env.example .env
# データベースの起動
docker compose up -d
npx prisma@6.19.0 migrate deploy
npx prisma@6.19.0 studio
```

### Demo app 側のセットアップ

```bash
# 環境設定
cd demo_app
uv venv --python 3.13.4
uv pip install asyncpg boto3 chainlit==2.9.6
source .venv/bin/activate
cp .env.template .env
chainlit create-secret
# デモアプリの起動
chainlit run app.py
```

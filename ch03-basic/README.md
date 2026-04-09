# 第3章 サポートページ — 基本機能確認用アプリ

本リポジトリは、書籍第3章のサンプルコードです。
Chainlit の基本機能を概観するための、ルールベースで応答するシンプルなアプリを実装しています。

## セットアップ

### 前提条件

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- [docker](http://docker.com/)

### インストール

```bash
uv sync
```

### 環境変数の設定

`.env` を作成し、Chainlit用のシークレットキーを設定してください。

```bash
# .env ファイルの作成
cp .env.example .env

# chainlit用のシークレットを生成.
# 以下の実行結果中のガイドに従い，.env の CHAINLIT_AUTH_SECRET を設定してください．
uv run chainlit create-secret
```

> **注意**: `.env` は Git にコミットしないでください。

### 実行方法

```bash
# データベースを作成・起動
docker compose -f sandbox/postgres/docker-compose.yaml up -d

# アプリケーションを起動
uv run chainlit run --watch --host localhost --port 8000 main.py

# データベースを停止
docker compose -f sandbox/postgres/docker-compose.yaml stop
```

- アプリケーションの起動後、ブラウザで [http://localhost:8000](http://localhost:8000) にアクセスしてください。
  - ログインページでは、以下を入力してください：
    - ユーザー名： `guest@example.com`
    - パスワード： `（任意の文字列）`
- データベースの状態を確認したい場合は、ブラウザで [http://localhost:8080](http://localhost:8080) にアクセスしてください。
  - ログインページでは、以下を入力してください：
    - データベース種類： `PostgreSQL`
    - サーバー: `db`
    - ユーザー名： `app`
    - パスワード： `example`
    - データベース： `app_db`
- アプリケーションの停止は、Ctrl+Cで行ってください。

# 第10章 サポートページ — ChainlitのUIを癖に染める

本リポジトリは、書籍第10章のサンプルコードです。
カスタムCSSやカスタムJavaScriptを活用し、ChainlitのUIをSF風にカスタマイズします。

## Appendixサイト

書籍版はモノクロ印刷のため、カラーやアニメーションの補足資料をAppendixサイトに掲載しています。

- [Appendixサイト](https://seahawk-tiger.github.io/chainlit-ui-appendix/)

---

## セットアップ

### 前提条件

- uv
- Python 3.13.4 (uvで管理)
- chainlit 2.9.6 (uvで管理)

### インストール

```bash
uv sync
```

### 環境変数の設定

`.env.example` をコピーして `.env` を作成します。

```bash
cp .env.example .env
```

認証用シークレットを生成します。

```bash
uv run chainlit create-secret
```

表示された値を `.env` に設定します。

```env
CHAINLIT_AUTH_SECRET=生成された値
LOGIN_USERNAME=任意のユーザー名
LOGIN_PASSWORD=任意のパスワード
```

> **注意**: `.env` は Git にコミットしないでください。

## 実行方法

```bash
uv run chainlit run app.py
```

起動後、ブラウザで http://localhost:8000 にアクセスしてください。
`.env` に設定したユーザー名・パスワードでログインします。

## デモ機能

ログイン後、以下のメッセージを入力してください。

```
demo
```

以下の要素が表示されます。

- 画像（assets/dummy_image.png）
- Dataframe（assets/dummy_table.csv）
- Plotly グラフ（assets/dummy_plot.csv）

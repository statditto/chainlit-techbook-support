# 第9章 物理パズルゲーム サポートページ

第9章のサポートページです。

Chainlit の **send_window_message** を活用して作る、LLM生成ステージを遊べる物理パズルゲームです。

## 概要

LLMが生成したステージJSONを受け取り、ブラウザ上で物理演算とドラッグ操作で遊べるゲームを実装します。

## セットアップ

### 必要なもの

- [uv](https://docs.astral.sh/uv/)
- OpenAI APIキー

### インストール

```bash
uv sync
```

### 環境変数

`.env.example` をコピーして `.env` を作成し、APIキーを設定してください。

```bash
cp .env.example .env
# .env を編集して OPENAI_API_KEY を設定
```

### 起動

```bash
uv run chainlit run app.py
```

ブラウザで http://localhost:8000 が開きます。

## ライセンス

MIT

## 正誤表

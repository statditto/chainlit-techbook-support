# # 第8章 絵しりとり サポートページ

第1章のサポートページです。

Chainlit の **CustomElement** を活用して作る、AI と遊べる絵しりとり Web アプリです。

## 概要

キャンバスに絵を描いて送ると、AI が絵を当てて、しりとりの次の絵を返してくれます。
これを数ラウンド繰り返し、最後に答え合わせ！

## セットアップ

### 必要なもの

- [uv](https://docs.astral.sh/uv/)
- [Google AI Studio](https://aistudio.google.com/) の API キー

### インストール

```bash
uv sync
```

### 環境変数

`.env.example` をコピーして `.env` を作成し、API キーを設定してください。

```bash
cp .env.example .env
# .env を編集して GEMINI_API_KEY を設定
```

### 起動

```bash
uv run chainlit run app.py -w
```

ブラウザで http://localhost:8000 が開きます。

## ライセンス

MIT

## 正誤表
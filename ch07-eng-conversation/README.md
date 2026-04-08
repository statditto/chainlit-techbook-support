# 第7章 サポートページ — 英会話パートナー（音声対応チャットUI）

本リポジトリは、書籍第7章のサンプルコードです。Chainlit の音声入出力機能を活用し、英会話練習ができるチャットアプリを構築します。

## 主な機能

- トピック選択式の英会話練習
- テキスト入力・音声入力の両対応（Whisper による文字起こし）
- AIパートナーの応答を音声で自動再生（OpenAI TTS）
- 会話終了後に英語のレビュー・フィードバックを生成

## セットアップ

### 前提条件

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- OpenAI API キー

### インストール

```bash
uv sync
```

### 環境変数の設定

`.env` を作成し、OpenAI API キーを設定してください。

```bash
cp .env.example .env
```

```
OPENAI_API_KEY=your_openai_api_key_here
```

> **注意**: `.env` は Git にコミットしないでください。

## 実行方法

```bash
chainlit run app.py -w
```

起動後、ブラウザで http://localhost:8000 にアクセスしてください。

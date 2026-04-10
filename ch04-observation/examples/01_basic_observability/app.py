"""
実装例1: シンプルなLLM呼び出しの観察

Chainlitの基本機能を使って、LLM呼び出しを観察可能にする最もシンプルな例です。

主な学習ポイント:
1. @cl.on_message デコレータでメッセージハンドラを定義
2. cl.Step で処理を構造化し、観察可能にする
3. step.input / step.output で入出力を記録
4. step.metadata でトークン数などのメタデータを記録
"""

import os
import json
from openai import AsyncOpenAI
import chainlit as cl
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# OpenAI クライアントの初期化
# base_url を指定することで、社内proxy経由でのアクセスが可能
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL") or None,  # 空文字列の場合はNoneにしてデフォルトを使用
)


@cl.on_message
async def main(message: cl.Message):
    """
    ユーザーからのメッセージを受け取り、LLMに送信して応答を返す。

    cl.Step を使うことで、LLM呼び出しの詳細を観察可能にします：
    - どのような入力を送ったか (step.input)
    - どのような出力を受け取ったか (step.output)
    - トークン数やモデル名などのメタデータ (step.metadata)
    """

    # Stepを作成して、LLM呼び出しを観察可能にする
    # type="llm" を指定することで、Chainlit UIでLLM呼び出しとして表示される
    async with cl.Step(name="LLM呼び出し", type="llm", show_input=True) as step:
        # ステップの入力を記録
        # これにより、LLMに何を送ったかが後から確認できる
        step.input = message.content

        # OpenAI APIを呼び出し
        response = await client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "あなたは親切なアシスタントです。"},
                {"role": "user", "content": message.content}
            ],
        )

        # 応答のテキストを取得
        response_text = response.choices[0].message.content

        # ステップの出力を記録
        # これにより、LLMから何を受け取ったかが確認できる
        step.output = response_text

        # メタデータを記録
        # トークン数、モデル名、完了理由などを記録することで、
        # パフォーマンスやコストの分析が可能になる
        metadata = {
            "model": response.model,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "finish_reason": response.choices[0].finish_reason,
        }
        step.metadata = metadata
        metadata_json = json.dumps(metadata, ensure_ascii=False, indent=2)

        # メタデータをStepの出力にも含める（UIで確実に表示されるように）
        step.output = "\n".join([
            response_text,
            "",
            "---",
            "**Metadata:**",
            "```json",
            metadata_json,
            "```",
        ])


    # ユーザーに応答を表示
    await cl.Message(content=response_text).send()


@cl.on_chat_start
async def on_chat_start():
    """
    チャットセッション開始時に実行される関数。
    ウェルカムメッセージを表示して、ユーザーに使い方を案内します。
    """
    await cl.Message(
        content="こんにちは！LLM観察UIへようこそ。\n\n"
        "このアプリでは、LLMへの各呼び出しがステップとして記録され、"
        "入力・出力・トークン数などの詳細を確認できます。\n\n"
        "何か質問してみてください！"
    ).send()

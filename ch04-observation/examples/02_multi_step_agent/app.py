"""
実装例2: Multi-Step Agentの観察

Function Calling（Tool Calling）を使うAgentで、複数のツールを呼び出す様子を
階層的なStepで観察します。

主な学習ポイント:
1. 階層的なStepの構造（Stepの中にStepをネスト）
2. ツール呼び出しの観察（type="tool"）
3. Agent全体の実行フローの可視化
4. エラーハンドリングの観察
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from openai import AsyncOpenAI
import chainlit as cl
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL") or None,
)


# ===== ツール定義 =====
# 実際のAPIを呼ぶ代わりに、ダミーデータを返すツールを定義します

async def get_weather(location: str) -> str:
    """指定された場所の天気情報を取得する（ダミー実装）"""
    # 実際の実装では、Weather APIを呼び出す
    weathers = {
        "東京": "晴れ、気温25度",
        "大阪": "曇り、気温23度",
        "札幌": "雨、気温18度",
    }
    return weathers.get(location, f"{location}の天気情報は見つかりませんでした")



async def add(a: float, b: float) -> str:
    """2つの数値を加算する"""
    result = a + b
    return f"{a} + {b} = {result}"


# OpenAI Function Calling用のツール定義
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "指定された場所の現在の天気情報を取得します",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "天気を知りたい場所（例: 東京、大阪）",
                    }
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "2つの数値を加算して結果を返します。数値計算を行う場合、必ずこのツールを使います",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "1つ目の数値",
                    },
                    "b": {
                        "type": "number",
                        "description": "2つ目の数値",
                    },
                },
                "required": ["a", "b"],
            },
        },
    },
]

# ツール関数のマッピング
TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "add": add,
}


async def execute_tool_call(tool_call, parent_step: cl.Step) -> str:
    """
    ツール呼び出しを実行し、結果を返す。
    各ツール呼び出しを個別のStepとして記録します。
    """
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)

    # 各ツール呼び出しを個別のStepとして記録
    # type="tool" を指定することで、ツールアイコンとともに表示される
    async with cl.Step(
        name=f"ツール: {function_name}",
        type="tool",
        parent_id=parent_step.id,  # 親ステップを指定して階層構造を作る
    ) as tool_step:
        # ツール呼び出しの引数を記録
        # ツール関数を実行
        function_to_call = TOOL_FUNCTIONS[function_name]
        t0 = time.perf_counter()
        result = await function_to_call(**function_args)
        latency_ms = round((time.perf_counter() - t0) * 1000)

        # メタデータを記録
        tool_step.metadata = {
            "function_name": function_name,
            "arguments": function_args,
            "executed_at": datetime.now().isoformat(),
            "latency_ms": latency_ms,
        }

        # 実行結果とメタデータをUIに表示
        metadata_json = json.dumps(tool_step.metadata, ensure_ascii=False, indent=2)
        tool_step.output = (
            result
            + "\n\n---\n**Metadata:**\n```json\n"
            + metadata_json
            + "\n```"
        )

        return result


async def run_agent(user_message: str, conversation_history: List[Dict[str, Any]]):
    """
    Agentを実行し、必要に応じてツールを呼び出す。
    全体の実行フローをStepで記録します。
    """

    # Agent全体の実行をStepとして記録
    async with cl.Step(name="Agent実行", type="run") as agent_step:
        # 会話履歴を準備
        messages = conversation_history + [
            {"role": "user", "content": user_message}
        ]

        # 最大5回までツール呼び出しを繰り返す（無限ループ防止）
        max_iterations = 5
        for iteration in range(max_iterations):
            # LLM呼び出しをStepとして記録
            async with cl.Step(
                name=f"LLM呼び出し #{iteration + 1}",
                type="llm",
                parent_id=agent_step.id,
            ) as llm_step:
                # OpenAI APIを呼び出し
                t0 = time.perf_counter()
                response = await client.chat.completions.create(
                    model="gpt-5.2",
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                )
                latency_ms = round((time.perf_counter() - t0) * 1000)

                response_message = response.choices[0].message

                # メタデータを記録
                llm_step.metadata = {
                    "model": response.model,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                    "finish_reason": response.choices[0].finish_reason,
                    "tool_calls": len(response_message.tool_calls or []),
                    "latency_ms": latency_ms,
                }

                # LLMの応答とメタデータをUIに表示
                base_output = response_message.content or "(ツール呼び出しを選択)"
                metadata_json = json.dumps(llm_step.metadata, ensure_ascii=False, indent=2)
                llm_step.output = (
                    base_output
                    + "\n\n---\n**Metadata:**\n```json\n"
                    + metadata_json
                    + "\n```"
                )

            # メッセージ履歴に追加
            messages.append(response_message)

            # ツール呼び出しがない場合は終了
            if not response_message.tool_calls:
                agent_step.output = response_message.content
                return response_message.content, messages

            # ツール呼び出しを実行
            for tool_call in response_message.tool_calls:
                result = await execute_tool_call(tool_call, llm_step)

                # ツール実行結果をメッセージ履歴に追加
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": result,
                    }
                )

        # 最大反復回数に達した場合
        agent_step.output = "最大反復回数に達しました"
        return "申し訳ありませんが、処理に時間がかかりすぎています。", messages


@cl.on_chat_start
async def on_chat_start():
    """チャットセッション開始時に会話履歴を初期化"""
    cl.user_session.set(
        "conversation_history",
        [
            {
                "role": "system",
                "content": "あなたは親切なアシスタントです。ユーザーの質問に答えるために、必要に応じてツールを使用してください。",
            }
        ],
    )

    await cl.Message(
        content="こんにちは！Multi-Step Agent観察UIへようこそ。\n\n"
        "このAgentは以下のツールを使用できます:\n"
        "- 天気情報の取得\n"
        "- 四則演算\n"
        "\n"
        "各ツール呼び出しがステップとして記録され、"
        "Agentの思考プロセスを観察できます。\n\n"
        "\n"
        "試してみてください:\n"
        "- 「東京の天気を教えて」\n"
        "- 「3 + 14 は？」\n"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """ユーザーからのメッセージを処理"""

    # 会話履歴を取得
    conversation_history = cl.user_session.get("conversation_history")

    # Agentを実行
    response_text, updated_history = await run_agent(
        message.content, conversation_history
    )

    # 会話履歴を更新
    cl.user_session.set("conversation_history", updated_history)

    # 応答を表示
    await cl.Message(content=response_text).send()

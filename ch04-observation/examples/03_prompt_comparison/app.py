"""
実装例3: プロンプトエンジニアリングのための観察

複数のプロンプトバリエーションを試して比較することで、
最適なプロンプトを見つけるプロセスを支援します。

主な学習ポイント:
1. 複数のプロンプトバリエーションの並列実行と比較
2. cl.Text による構造化データの表示
3. パフォーマンス計測（レイテンシ、トークン数）
4. プロンプトテンプレートの管理
"""

import os
import time
from typing import List, Dict, Any
from openai import AsyncOpenAI
import chainlit as cl
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL") or None,
)


# プロンプトバリエーション定義
PROMPT_VARIANTS = {
    "シンプル": """以下のテキストを要約してください：

{text}""",
    "詳細指示": """以下のテキストを、以下の要件に従って要約してください：

要件:
- 3文以内で要約する
- 重要なポイントを箇条書きで含める
- 客観的な表現を使う

テキスト:
{text}""",
    "Few-shot": """以下の例を参考に、テキストを要約してください。

例1:
テキスト: 「人工知能は近年急速に発展しており、様々な分野で活用されています。特に自然言語処理の分野では、GPTなどの大規模言語モデルが登場し、人間のような文章生成が可能になりました。」
要約: AI技術、特に自然言語処理分野で大規模言語モデルが発展し、人間レベルの文章生成が実現。

では、以下のテキストを要約してください：
{text}""",
    "Chain-of-Thought": """以下のテキストを要約してください。まず、重要なポイントを洗い出してから、それらを統合して要約を作成してください。

テキスト:
{text}

ステップ1: 重要なポイントを列挙
ステップ2: ポイントを統合して要約を作成""",
}


async def run_prompt_variant(
    variant_name: str,
    prompt_template: str,
    text: str,
    model: str = "gpt-5.2",
) -> Dict[str, Any]:
    """
    単一のプロンプトバリエーションを実行し、結果を返す。
    実行時間とトークン数も計測します。
    """

    async with cl.Step(
        name=f"プロンプト: {variant_name}",
        type="llm",
    ) as step:
        # プロンプトを生成
        prompt = prompt_template.format(text=text)
        step.input = prompt

        # 実行時間を計測
        start_time = time.time()

        # LLM呼び出し
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )

        end_time = time.time()
        latency = end_time - start_time

        # 結果を取得
        result = response.choices[0].message.content
        step.output = result

        # メタデータを記録
        step.metadata = {
            "variant": variant_name,
            "model": response.model,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "latency_seconds": round(latency, 2),
            "tokens_per_second": round(
                response.usage.completion_tokens / latency, 2
            ),
        }

        return {
            "variant": variant_name,
            "result": result,
            "metadata": step.metadata,
        }


async def compare_prompts(text: str, model: str = "gpt-5.2"):
    """
    複数のプロンプトバリエーションを実行し、結果を比較します。
    """

    async with cl.Step(name="プロンプト比較実験", type="run") as experiment_step:
        experiment_step.input = f"対象テキスト（{len(text)}文字）"

        # 各プロンプトバリエーションを実行
        results = []
        for variant_name, prompt_template in PROMPT_VARIANTS.items():
            result = await run_prompt_variant(
                variant_name, prompt_template, text, model
            )
            results.append(result)

        # 比較結果をまとめる
        comparison = "## プロンプト比較結果\n\n"

        for result in results:
            comparison += f"### {result['variant']}\n"
            comparison += f"**出力:**\n{result['result']}\n\n"
            comparison += f"**パフォーマンス:**\n"
            comparison += f"- トークン数: {result['metadata']['total_tokens']} "
            comparison += f"(prompt: {result['metadata']['prompt_tokens']}, "
            comparison += f"completion: {result['metadata']['completion_tokens']})\n"
            comparison += f"- レイテンシ: {result['metadata']['latency_seconds']}秒\n"
            comparison += f"- 生成速度: {result['metadata']['tokens_per_second']} tokens/sec\n\n"
            comparison += "---\n\n"

        experiment_step.output = comparison

        return results, comparison


@cl.on_chat_start
async def on_chat_start():
    """チャットセッション開始時の初期化"""
    await cl.Message(
        content="## プロンプトエンジニアリング観察UI\n\n"
        "このツールは、複数のプロンプトバリエーションを並列実行し、"
        "結果を比較することで、最適なプロンプトを見つけるプロセスを支援します。\n\n"
        "**使い方:**\n"
        "1. 要約したいテキストを入力してください\n"
        "2. システムが4つの異なるプロンプト戦略で要約を生成します\n"
        "3. 各バリエーションの結果とパフォーマンスを比較できます\n\n"
        "**比較されるプロンプト戦略:**\n"
        "- **シンプル**: 最小限の指示\n"
        "- **詳細指示**: 具体的な要件を含む\n"
        "- **Few-shot**: 例示を含む\n"
        "- **Chain-of-Thought**: 段階的な思考を促す\n\n"
        "試しに、長めのテキスト（ニュース記事やブログ記事など）を貼り付けてみてください！"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """ユーザーからのメッセージを処理"""

    text = message.content

    # テキストが短すぎる場合は警告
    if len(text) < 100:
        await cl.Message(
            content="⚠️ テキストが短すぎます。少なくとも100文字以上のテキストを入力してください。\n\n"
            "プロンプト比較の効果を確認するには、ある程度長いテキストが必要です。"
        ).send()
        return

    # プロンプト比較を実行
    results, comparison = await compare_prompts(text)

    # 結果を表示
    await cl.Message(content=comparison).send()

    # パフォーマンス比較グラフ用のデータを生成
    # （実際にはChartJSなどで可視化できますが、ここではテキストで表現）
    perf_comparison = "\n## パフォーマンス比較\n\n"
    perf_comparison += "| プロンプト | トークン数 | レイテンシ (秒) | 生成速度 (tokens/sec) |\n"
    perf_comparison += "|-----------|-----------|----------------|---------------------|\n"

    for result in results:
        meta = result['metadata']
        perf_comparison += f"| {result['variant']} | {meta['total_tokens']} | "
        perf_comparison += f"{meta['latency_seconds']} | {meta['tokens_per_second']} |\n"

    # 最も効率的なバリエーションを特定
    best_latency = min(results, key=lambda r: r['metadata']['latency_seconds'])
    best_tokens = min(results, key=lambda r: r['metadata']['total_tokens'])

    perf_comparison += f"\n**最速:** {best_latency['variant']} ({best_latency['metadata']['latency_seconds']}秒)\n"
    perf_comparison += f"**最少トークン:** {best_tokens['variant']} ({best_tokens['metadata']['total_tokens']} tokens)\n"

    await cl.Message(content=perf_comparison).send()

    # 推奨事項を提示
    recommendation = "\n## 💡 推奨事項\n\n"

    # 品質とパフォーマンスのトレードオフを分析
    if best_latency['variant'] == best_tokens['variant']:
        recommendation += f"✅ **{best_latency['variant']}** が最も効率的です（速度とトークン数の両方で優位）。\n\n"
    else:
        recommendation += f"⚖️ トレードオフが存在します：\n"
        recommendation += f"- 速度優先: **{best_latency['variant']}**\n"
        recommendation += f"- コスト優先: **{best_tokens['variant']}**\n\n"

    recommendation += "結果の品質を確認し、ユースケースに最適なバリエーションを選択してください。\n"
    recommendation += "\n**考慮すべき点:**\n"
    recommendation += "- 出力の品質（正確さ、完全性、読みやすさ）\n"
    recommendation += "- レイテンシ（ユーザー体験への影響）\n"
    recommendation += "- トークン数（APIコスト）\n"

    await cl.Message(content=recommendation).send()


# ===== プロンプトテンプレート管理機能 =====

@cl.action_callback("show_prompt_template")
async def show_prompt_template(action: cl.Action):
    """
    プロンプトテンプレートを表示するアクションハンドラ。
    （この機能はオプション）
    """
    variant_name = action.value

    if variant_name in PROMPT_VARIANTS:
        template = PROMPT_VARIANTS[variant_name]

        # Textエレメントで表示
        await cl.Message(
            content=f"## プロンプトテンプレート: {variant_name}\n\n```\n{template}\n```"
        ).send()

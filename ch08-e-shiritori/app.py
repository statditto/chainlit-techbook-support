import base64
import os

import chainlit as cl
from dotenv import load_dotenv
from google.genai import errors as genai_errors

from gemini import identify_drawing, generate_image, pick_next_word

load_dotenv()

MAX_ROUNDS = int(os.getenv("MAX_ROUNDS", "5"))


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #

def _canvas(hint: str, round_num: int) -> cl.CustomElement:
    return cl.CustomElement(
        name="DrawCanvas",
        props={"hint": hint, "round": round_num, "maxRounds": MAX_ROUNDS},
    )


def _summary(history: list) -> str:
    lines = []
    for i, h in enumerate(history):
        lines.append(f"**ラウンド {i+1}**\n")
        lines.append(f"- あなた：**{h['user']}**")
        if h["ai"]:
            lines.append(f"- AI：**{h['ai']}**")
        lines.append("")  # 空行で区切り
    chain = []
    for h in history:
        chain.append(h["user"])
        if h["ai"]:
            chain.append(h["ai"])
    lines.append(f"**しりとり：** {' → '.join(chain)}")
    return "\n".join(lines)


async def _finish(history: list):
    await cl.Message(
        content=(
            "## 🎉 ゲーム終了！\n\n"
            "### 🔍 答え合わせ\n"
            f"{_summary(history)}\n\n"
            "また遊ぶ場合はページをリロードしてね！"
        ),
    ).send()


# ------------------------------------------------------------------ #
# Chainlit handlers
# ------------------------------------------------------------------ #

@cl.on_chat_start
async def start():
    cl.user_session.set("round", 0)
    cl.user_session.set("last_char", None)
    cl.user_session.set("history", [])

    await cl.Message(
        content=(
            "# 🎨 絵しりとり\n\n"
            f"全 **{MAX_ROUNDS}ラウンド** のしりとりです。\n\n"
            "1. 絵を描いて「送る」\n"
            "2. AIが絵を見て考える（思考過程が見えるよ👀）\n"
            "3. AIがしりとりの次の絵を返すので、続きを描こう！\n"
            "4. 答え合わせはゲーム終了後！\n\n"
            "まずは好きな絵を描いてね！"
        ),
        elements=[_canvas("好きな絵を描いてね！", 1)],
    ).send()


@cl.action_callback("submit_drawing")
async def on_submit(action: cl.Action):
    round_num: int = cl.user_session.get("round")
    last_char: str | None = cl.user_session.get("last_char")
    history: list = cl.user_session.get("history")

    # デコード
    img_data: str = action.payload.get("image", "")
    if "," in img_data:
        img_data = img_data.split(",", 1)[1]
    img_bytes = base64.b64decode(img_data)

    # --- Step 1: 絵を判定 ---
    try:
        async with cl.Step(name="🤔 判定中...") as step:
            thinking, user_word = await identify_drawing(img_bytes, last_char)
            step.output = thinking or "（考え中...）"
    except genai_errors.ClientError as e:
        await cl.Message(content=f"⚠️ APIエラー：{e}").send()
        return

    if not user_word:
        await cl.Message(content="認識できませんでした😅 もう一度描いてみてね！").send()
        return

    round_num += 1
    cl.user_session.set("round", round_num)

    if round_num > MAX_ROUNDS:
        history.append({"user": user_word, "ai": None})
        cl.user_session.set("history", history)
        await _finish(history)
        return

    # --- Step 2: しりとりの次の単語 ---
    try:
        next_char = user_word[-1]
        async with cl.Step(name="🎨 しりとりの次を考え中...") as step:
            thinking2, ai_word = await pick_next_word(next_char)
            step.output = thinking2 or "（考え中...）"

        if not ai_word:
            ai_word = "たこ"

        ai_img_bytes = await generate_image(ai_word)
    except genai_errors.ClientError as e:
        await cl.Message(content=f"⚠️ APIエラー：{e}").send()
        return

    history.append({"user": user_word, "ai": ai_word})
    cl.user_session.set("history", history)
    cl.user_session.set("last_char", ai_word[-1])

    # --- AIの絵を表示 ---
    ai_img = cl.Image(content=ai_img_bytes, mime="image/png", name="ai_drawing", display="inline")

    if round_num >= MAX_ROUNDS:
        await cl.Message(content="🤖 AIの絵", elements=[ai_img]).send()
        await _finish(history)
        return

    await cl.Message(content="🤖 AIの絵", elements=[ai_img]).send()

    # 次のキャンバス
    await cl.Message(
        content="続きの絵を描いてね！",
        elements=[_canvas("しりとりで続く絵を描こう！", round_num + 1)],
    ).send()

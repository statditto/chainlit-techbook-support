import json
import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

VISION_MODEL = os.getenv("VISION_MODEL", "gemini-flash-lite-latest")
WORD_MODEL = os.getenv("WORD_MODEL", "gemini-flash-lite-latest")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gemini-2.0-flash-exp-image-generation")

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

_KANA_RE = re.compile(r"[^\u3040-\u309F\u30A0-\u30FF]")

# 構造化出力スキーマ
_SHIRITORI_SCHEMA = {
    "type": "object",
    "properties": {
        "thinking": {
            "type": "string",
            "description": "5歳の幼稚園児風の短い思考過程（2〜3行）",
        },
        "answer": {
            "type": "string",
            "description": "ひらがなの単語（「ん」で終わらないこと）",
        },
    },
    "required": ["thinking", "answer"],
}


def _parse(text: str) -> tuple[str, str]:
    """構造化JSON応答から (thinking, word) を抽出する。"""
    data = json.loads(text)
    thinking = data.get("thinking", "")
    word = _KANA_RE.sub("", data.get("answer", ""))
    return thinking, word


async def identify_drawing(image_bytes: bytes, last_char: str | None) -> tuple[str, str]:
    """絵を識別。(thinking, word) を返す。"""
    constraint = ""
    if last_char:
        constraint = (
            f"だいじなヒント：しりとりのつづきだから「{last_char}」からはじまることばのはずだよ！"
            f"「{last_char}」からはじまることばだとおもってかんがえてね。\n"
        )

    prompt = (
        "この絵が何を描いているか当ててください。\n"
        + constraint
        + "\n【絶対ルール】「ん」で終わる単語は禁止。別の候補を考え直すこと。\n"
        "5歳の幼稚園児のように2〜3行だけ短く考えてください。"
    )

    resp = client.models.generate_content(
        model=VISION_MODEL,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_SHIRITORI_SCHEMA,
        ),
    )
    return _parse(resp.text)


async def pick_next_word(start_char: str) -> tuple[str, str]:
    """しりとりの次の単語を選ぶ。(thinking, word) を返す。"""
    resp = client.models.generate_content(
        model=WORD_MODEL,
        contents=(
            f"しりとりゲームです。「{start_char}」から始まる日本語の名詞を1つ選んでください。\n\n"
            "【絶対ルール】「ん」で終わる単語は禁止。選ぶ前に末尾を確認すること。\n"
            "5歳の幼稚園児のように2〜3行だけ短く考えてください。"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_SHIRITORI_SCHEMA,
        ),
    )
    return _parse(resp.text)


async def generate_image(japanese_word: str) -> bytes:
    """
    日本語の単語を英訳し、Gemini 2.5 Flash Image で画像を生成する。
    """

    tr = client.models.generate_content(
        model=WORD_MODEL,
        contents=f"Return ONLY the English noun for '{japanese_word}'. No explanation.",
    )
    prompt_en = tr.text.strip()

    # 幼稚園児風の味のあるタッチをプロンプトで指定
    resp = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=(
            f"A simple, cute, childlike crayon drawing of '{prompt_en}'. "
            "Kindergarten art style, hand-drawn, white background.Only the drawing, no text."
        ),
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"]
        ),
    )

    try:
        return resp.candidates[0].content.parts[0].inline_data.data
    except (IndexError, AttributeError):
        raise ValueError(f"画像生成に失敗しました: {japanese_word}")
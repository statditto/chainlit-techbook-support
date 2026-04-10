import os
import random
import uuid
import asyncio
import json
from dotenv import load_dotenv
from openai import OpenAI
import jsonschema

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-5.2"

# ==== Stage JSON Schema ====
STAGE_SCHEMA = {
    "type": "object",
    "required": ["version", "stage_id", "seed", "canvas", "physics", "rules", "bodies", "constraints", "ui"],
    "properties": {
        "version": {"type": "string"},
        "stage_id": {"type": "string"},
        "seed": {"type": "integer"},
        "difficulty": {"type": "string"},
        "canvas": {
            "type": "object",
            "required": ["width", "height"],
            "properties": {
                "width": {"type": "integer"},
                "height": {"type": "integer"},
            },
        },
        "physics": {
            "type": "object",
            "required": ["gravityY", "gravityX", "timeStepMs"],
            "properties": {
                "gravityY": {"type": "number"},
                "gravityX": {"type": "number"},
                "timeStepMs": {"type": "number"},
            },
        },
        "rules": {
            "type": "object",
            "required": ["win"],
            "properties": {
                "win": {"type": "object"},
            },
        },
        "bodies": {"type": "array", "minItems": 2},
        "constraints": {"type": "array"},
        "ui": {
            "type": "object",
            "required": ["allowDrag", "dragWhitelistTags"],
            "properties": {
                "allowDrag": {"type": "boolean"},
                "dragWhitelistTags": {"type": "array"},
            },
        },
    },
}

STAGE_GENERATION_SYSTEM = """あなたは物理パズルゲームのステージを生成する優秀なゲームデザイナーです。
ユーザーの要件に従い、Matter.jsで動作する有効なステージJSONを生成してください。
ステージは必ず解けるものでなければなりません。
出力はJSON形式のステージデータのみで、余計な説明やテキストを含めないでください。

## ゲームメカニクス（重要）
- ボール（ball）は重力で自由落下する。プレイヤーはボールを操作できない。
- 板（ramp, platform）はプレイヤーがドラッグして位置を変えられる。
- 障害物（obstacle）は動かせない。
- プレイヤーは板を配置して、ボールの落下経路を変え、ゴール（goal）まで導く。
- ゴール（goal）は固定センサーでボールが入ればクリア。ゴールは床か障害物の上に配置する必要がある。
- ステージは必ず解けるものでなければならない。

## キャンバス
- 幅800px、高さ600px

## 必須ボディ
1. label="ball": ボール（isStatic=false, isSensor=false, color="#60a5fa"）。上部左右どちらかに配置。
2. label="goal": ゴール（isStatic=true, isSensor=true, color="#34d399"）。
    * ゴールは必ず矩形（rectangle）で生成すること。円（circle/r）は使わない。
    * 床の上に接地させること。床のy=595なので、ゴールのy = 590 - (h/2) とする。
    * ゴールの周囲を板で囲まないこと。ゴールの位置が開始地点に近すぎないこと。
3. label="wall": 境界壁4本（isStatic=true, isSensor=false, color="#374151"）。
    - 床: x=400, y=595, w=800, h=10
    - 天井: x=400, y=5, w=800, h=10
    - 左壁: x=5, y=300, w=10, h=600
    - 右壁: x=795, y=300, w=10, h=600
4. label="ramp": 移動可能な板2〜6本（labelは必ず "ramp" にすること。"platform"は使わない）
    - 難易度に応じてランダムな個数を配置。ユーザーの要望に応じて個数や角度を調整。
    - 適度に傾けて配置。（angle: ±0.1〜0.6程度）
    - 長さ: w=120〜150、h=12〜16
    - 色: 必ず color="#fb923c"（オレンジ）にすること。他の色は使わない。

## 難易度ガイドライン（板の枚数と障害物の数で決定）
- easy: 移動可能な板4~5枚(傾きは全てゴール方向)、障害物0個、ゴール大（w=80, h=60）
- normal: 移動可能な板3~4枚(傾きがゴール方向でない場合あり)、障害物（label="obstacle"）1~2個、ゴール中（w=60, h=50）
- hard: 移動可能な板1~2枚(傾きは自由)、障害物3~5個、ゴール小（w=40, h=40）
* 障害物はボールの経路を邪魔する固定ブロック。label="obstacle"でdragWhitelistTagsには含めないこと。
* 障害物の色は必ず color="#9ca3af"（ライトグレー）にすること。
* 重要：障害物を水平（angle=0）に配置してボールの通路を完全に塘がないこと。障害物は必ず傾けて配置するか、隙間を空けてボールが通過できるようにすること。
* 障害物の幅はキャンバス幅の半分以下（w ≤ 400）にすること。ボールが板を使って迂回できる余地を必ず残すこと。

## 物理パラメータ（通常の場合）
- ボール：friction: 0.01, frictionStatic: 0.02, frictionAir: 0.001, restitution: 0.3, density: 0.005
- 板：friction: 0.01, frictionStatic: 0.02, frictionAir: 0, restitution: 0.1, density: 0.001
- 障害物：friction: 0.01, frictionStatic: 0.02, restitution: 0.1
- 壁：friction: 0.01, restitution: 0.1
- gravityY: 通常=1.0、月面=0.166、重力強め＝2.0、逆重力＝-1.0
- gravityX: 通常=0.0

## JSONテンプレート
{
    "version": "1.0",
    "stage_id": "uuid",
    "seed": ランダムな整数,
    "difficulty": "easy" | "normal" | "hard",
    "canvas": {"width": 800, "height": 600},
    "physics": {"gravityY": 1.0, "gravityX": 0.0, "timeStepMs": 16.67},
    "rules": {
        "win": {"type": "enter_goal", "targetLabel": "ball", "goalId": "goal-1", "dwellMs": 500}
    },
    "bodies": [ ... ],
    "constraints": [ ... ],
    "ui": {"allowDrag": true, "dragWhitelistTags": ["ramps"]}
}
            
##  パズルデザインの注意点
- ボールは上部から落下し、板や障害物を経由してゴールに到達する必要がある。
- 板はバラバラに配置して、プレイヤーが並べ直す余地を残す。
- ゴールは下部の床の上に接地させること（y = 590 - h/2）。上方は解放すること。
- テーマ（宇宙、水中など）はカラーパレットで表現。
- ステージは板を正しく配置すれば必ずクリアできるように設計すること。絶対に解けないステージは生成しないこと。
- ゴールには必ず "id": "goal-1" を付与すること。
"""

def validate_stage(stage: dict) -> bool:
    try:
        jsonschema.validate(stage, STAGE_SCHEMA)
        labels = [b.get("label") for b in stage.get("bodies", [])]
        if "ball" not in labels or "goal" not in labels:
            return False
        goal_id = stage["rules"]["win"]["goalId"]
        ids = [b.get("id") for b in stage.get("bodies", [])]
        if goal_id not in ids:
            return False
        return True
    except jsonschema.ValidationError:
        return False
    
async def generate_stage(requirements: str, current_stage: dict = None) -> dict:
    context = ""
    if current_stage:
        context = f"\n\n現在のステージの情報\n ```json\n{json.dumps(current_stage, indent=2)}\n```\n\nこのステージを{requirements}の要件に合わせて調整してください。"

    usr_msg = f"以下の要件でステージを生成してください：\n{requirements}\n{context}"

    for attempt in range(3):
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=MODEL,
                messages = [
                    {"role": "system", "content": STAGE_GENERATION_SYSTEM},
                    {"role": "user", "content": usr_msg},
                ]
            )
            
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```json"):
                raw = raw.split("```json")[1].split("```")[0].strip()
            stage = json.loads(raw)
            stage["stage_id"] = str(uuid.uuid4())
            stage["seed"] = random.randint(0, 999999)

            if validate_stage(stage):
                return stage
            
        except Exception as e:
            print(f"Attempt {attempt+1}: Failed to generate valid stage - {e}")
    raise ValueError("有効なステージの生成に失敗しました。")

import chainlit as cl
from llm import generate_stage


@cl.on_chat_start
async def on_chat_start() -> None:
    cl.user_session.set("current_stage", None)
    await cl.Message(
        content=(
            "パズルシミュレーターへようこそ！\n"
            "板を並べてゴールを目指しましょう！\n"
            "**例：** `簡単なパズルを作って` / `難しいパズルを作って` / `重力を強くして`"
        ),
    ).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    current_stage = cl.user_session.get("current_stage")
    action = "調整" if current_stage else "生成"

    async with cl.Step(f"ステージ{action}中...", type="tool", show_input=False):
        stage = await generate_stage(message.content.strip(), current_stage)
        cl.user_session.set("current_stage", stage)

    print(stage)
    diff = stage.get("difficulty", "normal")
    label = {"easy": "優しい", "normal": "普通", "hard": "難しい"}.get(diff, diff)

    await cl.Message(
        content=f"ステージ{action}完了！ 難易度: {label}"
    ).send()
    await cl.send_window_message({"type": "stage_updated", "stage": stage})
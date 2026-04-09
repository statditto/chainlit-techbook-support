import os
import chainlit as cl
from dotenv import load_dotenv
from typing import Optional
import asyncio # スピナー発生のためにラグを作為的に発生する用

# 特定のメッセージが送信されたら用意された返答する用
from response_message import get_response


load_dotenv()

USERNAME = os.getenv("LOGIN_USERNAME")
PASSWORD = os.getenv("LOGIN_PASSWORD")

@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.User]:
    # .envに書かれたuser_nameとpasswordが一致したらログイン成功
    if username == USERNAME and password == PASSWORD:
        return cl.User(
            identifier="admin",
            metadata={"role": "admin", "provider": "hardcoded"},
        )
    return None

@cl.on_message
async def main(message: cl.Message):
    await asyncio.sleep(2) # スピナー発生時間
    # response_message.py内に記載したmessageが送信されたら用意された返答をする
    response = await get_response(message.content)

    if response is not None:
        await response.send()
        return

    # 登録してないメッセージが届いたらおうむ返しする。
    await cl.Message(content=f"echo: {message.content}").send()
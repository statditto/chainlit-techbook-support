from __future__ import annotations

from pathlib import Path
from typing import Optional

import chainlit as cl
import pandas as pd
import plotly.express as px

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

DUMMY_IMAGE_PATH = ASSETS_DIR / "dummy_image.png"
DUMMY_TABLE_CSV_PATH = ASSETS_DIR / "dummy_table.csv"
DUMMY_PLOT_CSV_PATH = ASSETS_DIR / "dummy_plot.csv"


async def get_response(user_text: str) -> Optional[cl.Message]:
    """
    反応するキーワードと返すメッセージを対応づける
    """
    text = (user_text or "").strip().lower()

    # Trigger words for the UI demo
    if text in {"demo", "ui", "elements"}:
        return build_ui_demo_message()

    return None


def build_ui_demo_message() -> cl.Message:
    """
    返答するメッセージを定義する(demo用)
    """
    # Dataframe element
    df_table = pd.read_csv(DUMMY_TABLE_CSV_PATH)

    # Plotly element
    df_plot = pd.read_csv(DUMMY_PLOT_CSV_PATH)
    fig = px.bar(
        df_plot,
        x="column1",
        y="column2",
        title="Dummy Plot",
    )

    elements: list[cl.Element] = [
        cl.Image(
            name="dummy_image",
            path=str(DUMMY_IMAGE_PATH),
            display="inline",
        ),
        cl.Dataframe(
            name="dummy_table",
            data=df_table,
        ),
        cl.Plotly(
            name="dummy_plot",
            figure=fig,
        ),
    ]

    return cl.Message(
        content="echo: demo",
        elements=elements,
    )

import os
from pathlib import Path
import re
import openai
import pandas as pd

from settings import FEED_EXPORT_PATH


class AskAI:
    AI = openai

    def get_feed_export(self, path: Path) -> Path:
        return sorted(
            list(f for f in path.iterdir() if not f.name.startswith("/~$")),
            key=lambda x: re.search(r"\d{4}-\d{2}-\d{2}--\d{2}-\d{2}-\d{2}", x.name)[0],
        )[-1]

    def summarize(self):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "anwser like mafia pate"},
                {"role": "user", "content": "How did Kurt Cobain die?"},
            ],
        )
        response = completion.choices[0].message.content
        print(f"ChatGPT: {response}")

    def do(self) -> None:
        openai.api_key = os.getenv("OPENAI_SECRET_KEY")

        df = pd.read_excel(self.get_feed_export(FEED_EXPORT_PATH))
        print(df)
        self.summarize()


if __name__ == "__main__":
    AskAI().do()

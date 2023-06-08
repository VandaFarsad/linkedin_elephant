import logging
import os
from pathlib import Path
import re
import openai
import pandas as pd

from settings import FEED_EXPORT_PATH

logger = logging.getLogger("AskAIJob")


class AskAIJob:
    AI = openai
    N_BEST_FEEDS = 12  # number of the most commented feeds to parse

    def get_feed_export(self, path: Path) -> Path:
        return sorted(
            list(f for f in path.iterdir() if not f.name.startswith("~$")),
            key=lambda x: re.search(r"\d{4}-\d{2}-\d{2}--\d{2}-\d{2}-\d{2}", x.name)[0],
        )[-1]

    def summarize(self, df: pd.DataFrame) -> str:
        df = df.sort_values(["Kommentare"], ascending=False).head(self.N_BEST_FEEDS)
        records = df[["Autor", "URL", "Inhalt"]].to_dict("records")
        data_string = "\n\n\n".join(
            [f"""Feed. Author: {r['Autor']}. URL: {r['URL']}. Content: "{r['Inhalt']}" """ for r in records]
        )
        print(data_string)
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Answer as concisely as possible.",
                },
                {
                    "role": "user",
                    "content": f"summarize each linkedin post in one sentence and link the person who wrote it: {data_string}",  # noqa
                },
            ],
        )
        return completion.choices[0].message.content

    def do(self) -> None:
        logger.info("Starting CollectFeedJob")
        openai.api_key = os.getenv("OPENAI_SECRET_KEY")

        feed_export = self.get_feed_export(FEED_EXPORT_PATH)
        logger.info(f"Verarbeite Feed Export Datei {feed_export}")
        df = pd.read_excel(feed_export)
        response_summarize = self.summarize(df)
        print(f"ChatGPT: {response_summarize}")

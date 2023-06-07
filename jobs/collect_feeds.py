import datetime
import logging
import os
import re
from typing import Any

import pandas as pd
from linkedin_api import Linkedin

from settings import FEED_EXPORT_PATH


logger = logging.getLogger("CollectFeedsJob")


class CollectFeedsJob:
    def is_older_than_1_day(self, feed: dict[str, str]) -> bool:
        """True is feed is older than a day. Otherwise False."""
        if not (old := feed.get("old")):
            return False
        age = old.split()[0]
        if (match := re.search(r"\b(\d+)([a-z])\b", age)) and match.group(2) in ("h", "m"):
            # if (match := re.search(r"\b(\d+)([a-z])\b", age)) and match.group(2) in ("h", "m", "d"):
            return False
        return True

    def get_yesterdays_feeds(self, api: Linkedin) -> list[dict[str, Any]]:
        offset_hundert = 0
        yesterdays_feed = []
        run = True
        while run:
            run = False
            for feed in api.get_feed_posts(offset=100 * offset_hundert):
                if self.is_older_than_1_day(feed):
                    # run = False
                    continue
                else:
                    run = True
                yesterdays_feed.append(feed)
                logger.info(
                    f'Feed: {100 * offset_hundert}-{100 * (offset_hundert+ 1)}. {feed.get("author_name", "")}. {feed.get("old", "")}'  # noqa
                )
            offset_hundert += 1
        return yesterdays_feed

    def parse_comment(self, comment: dict[str, Any]) -> str:
        return ".".join([c.get("value", "") for c in comment.get("values", [])])

    def get_datetime(self, old: str) -> datetime.datetime | None:
        age = old.split()[0]
        if matches := re.search(r"\b(\d+)([a-z])\b", age):
            match matches.group(2):
                case "m":
                    return datetime.datetime.now() - datetime.timedelta(minutes=int(matches.group(1)))
                case "h":
                    return datetime.datetime.now() - datetime.timedelta(hours=int(matches.group(1)))
                case "d":
                    return datetime.datetime.now() - datetime.timedelta(days=int(matches.group(1)))
        return None

    def count_post_comments(self, api: Linkedin, post_urn: str) -> int:
        """
        get_post_comments: Get post comments

        :param post_urn: Post URN
        :type post_urn: str
        :param comment_count: Number of comments to fetch
        :type comment_count: int, optional
        :return: List of post comments
        :rtype: list
        """
        counter = 0
        while True:
            url_params = {
                "count": 100,
                "start": 0,
                "q": "comments",
                "sortOrder": "RELEVANCE",
            }
            url = "/feed/comments"
            url_params["updateId"] = "activity:" + post_urn
            res = api._fetch(url, params=url_params)
            data = res.json()
            if data and "status" in data and data["status"] != 200:
                logger.info("request failed: {}".format(data["status"]))
                return counter
            n_comments = data.get("metadata", {}).get("updatedCommentCount", 0)
            counter += n_comments
            if n_comments < 100:
                return counter

    def do(self) -> None:
        logger.info("Starting CollectFeedJob")

        api = Linkedin(os.getenv("EMAIL"), os.getenv("PASSWORD"))

        contents: list[dict[str, Any]] = []
        for feed in self.get_yesterdays_feeds(api):
            if match := re.search(r"(\d+)$", feed["url"]):
                urn = match.group(1)
                content = {
                    "Datum": self.get_datetime(feed["old"]),
                    "Autor": feed["author_name"],
                    "Inhalt": feed["content"],
                    "Kommentare": self.count_post_comments(api, urn),
                    "URL": feed["url"],
                }
                contents.append(content)
                logger.info(
                    f'{content["Datum"]} {content["Autor"]}. Kommentare: {content["Kommentare"]}. URL: {feed["url"]}'
                )

        df_pivot: pd.DataFrame = pd.pivot_table(
            pd.DataFrame(contents),
            index=["Inhalt"],
            aggfunc={"Kommentare": "nunique", "Datum": "min", "Autor": "min", "URL": "min"},
        )
        df_pivot = (
            df_pivot.reset_index()
            .sort_values(["Autor", "Inhalt"])
            .sort_values(["Kommentare"], ascending=False)[["Datum", "Autor", "Kommentare", "URL", "Inhalt"]]
        )
        df_pivot["URL"] = df_pivot["URL"].apply(lambda x: f'=HYPERLINK("{x}", "Link")')

        FEED_EXPORT_PATH.mkdir(exist_ok=True)
        df_pivot.to_excel(
            FEED_EXPORT_PATH / f"LinkedIn_Feeds_{datetime.datetime.now().strftime('%Y-%m-%d--%H-%M-%S')}.xlsx",
            index=False,
        )

import logging

from helpers import read_env_file
from jobs.collect_feeds import CollectFeedsJob

logger = logging.getLogger("GetFeedJob")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


if __name__ == "__main__":
    read_env_file()

    CollectFeedsJob().do()

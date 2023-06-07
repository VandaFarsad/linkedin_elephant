import logging

from helpers import read_env_file
from jobs.collect_feeds import CollectFeedsJob
from settings import LOGS_PATH


LOGS_PATH.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)

stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOGS_PATH / "logs.log")
file_handler.setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[stdout_handler, file_handler],
)


if __name__ == "__main__":
    read_env_file()

    CollectFeedsJob().do()

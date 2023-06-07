import os


def get_env_data_as_dict(path: str) -> dict[str, str]:
    """
    For loading the .env -file (for docker) into the virtual environment
    """
    with open(path, "r") as f:
        return dict(
            tuple(line.replace("", "").split("=", maxsplit=1))  # type: ignore
            for line in f.read().replace('"', "").replace("'", "").split("\n")
            if line.strip() and not line.startswith("#")
        )


def read_env_file(path: str = ".env") -> None:
    vars_dict = get_env_data_as_dict(path)
    os.environ.update(vars_dict)

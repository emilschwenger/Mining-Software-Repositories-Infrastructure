import json
from datetime import datetime


def get_current_timestamp():
    """
    Returns the current timestamp in the local timezone format.
    """
    return float(datetime.now().timestamp())


def dict_search(dictionary: dict, keys: [], default):
    """
    This method takes in a list of keys searches the dictionary by traversing the keys from keys:[]
    If a single key does not exist or the last keys value is None this method returns default.
    """
    value = dictionary
    for key_index, key in enumerate(keys):
        if key_index < len(keys) and not isinstance(value, dict):
            return default
        value = value.get(key, None)
        if value is None:
            return default
    return value


def check_number_float(value):
    """
    Check if value is float else return -1.0
    """
    try:
        return float(value)
    except Exception as e:
        return -1.0


def check_number_int(value):
    """
    Check if value is int else return -1
    """
    try:
        return int(value)
    except Exception as e:
        return -1


def check_datetime(value):
    """
    Check if value is a datetime in format %Y-%m-%dT%H:%M:%SZ else return default time
    """
    try:
        datetime_value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        return value
    except Exception as e:
        return "0001-01-01T01:01:01Z"


def check_string(value):
    """
    Check if value is a string else return '-'
    """
    try:
        return str(value)
    except Exception as e:
        return "-"


def check_boolean(value):
    """
    Return a boolean if value is empty or none else return the boolean
    """
    try:
        return bool(value)
    except Exception as e:
        return False


def null_if_none(value):
    """
    Return an empty string is value is empty or none else return the string
    """
    if value is None:
        return ""
    else:
        return value


def read_repo_list():
    """
    Read repository list at MSRInfrastructure/repository_list.txt
    Expected format: every line a new PUBLIC GitHub repository url
    """
    with open("./repository_list.txt", "r+") as f:
        repo_list = f.readlines()
    return [repo.strip() for repo in repo_list]


def extract_repo_url_owner_and_name(url: str):
    """
    Extracts repository owner and username from a github repository url
    e.g., https://github.com/x/y return (x, y)
    """
    if url is None:
        return None
    url_split = url.split("/")
    if len(url_split) < 5:
        return None
    return url_split[3], url_split[4]

def read_config():
    """
    Read tool configuration file and return it as a dictionary
    Expected format: JSON
    """
    with open("./config.json", "r+") as f:
        config_file = json.loads(f.read())
        if config_file is None:
            raise Exception("Configuration file is empty or does not exist")
    return config_file

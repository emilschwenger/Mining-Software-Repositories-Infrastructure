import json
import threading
import time
from typing import Dict, Union, Tuple
from datetime import datetime
from src.Utility.Utility import read_config
from src.DataAcquisition.GitHubAPIService.GitHubAPIType import GITHUB_API_TYPE
from src.Utility.Logger import MSRLogger


class TokenManager:
    """
    TokenManager orchestrates GitHub tokens in a thread save way. All RepositoryCollector instances use the same
    TokenManager to acquire and return token. If a token expires as it is overused, the TokenManger automatically holds
    the token back until it reset.
    """

    def __init__(self):
        # Initiate logger
        self.logger = MSRLogger.get_logger(self.__class__.__name__)
        # Retrieve tokens from config file
        config = read_config()
        tokens = config.get("github_tokens", None)
        if tokens is None:
            self.logger.exception("Configuration file corruption, please define .tokens.")
        # Initialize token storage
        self.tokens: Dict[GITHUB_API_TYPE, Dict[str, list]] = {
            GITHUB_API_TYPE.GRAPH_QL_API: {
                "available": [(token, datetime.min) for token in tokens],
                "in_use": []
            },
            GITHUB_API_TYPE.REST_API: {
                "available": [(token, datetime.min) for token in tokens],
                "in_use": []
            }
        }
        # Initialize locks
        self.acquire_token_lock = {
            GITHUB_API_TYPE.GRAPH_QL_API: threading.Lock(),
            GITHUB_API_TYPE.REST_API: threading.Lock()
        }
        self.modify_tokens_lock = threading.Lock()
        # Terminates the program if no token is set
        self.token_list_empty = True if len(tokens) <= 0 else False
        if self.token_list_empty:
            self.logger.exception("Please add at least one token 1 tokens")

    def get_token(self, api_type: GITHUB_API_TYPE) -> str:
        """
        Acquire a GitHub token for a specific API_TYPE
        """
        self.logger.info(f"Trying to acquire token for api {api_type.value}")
        while self.acquire_token_lock.get(api_type):
            while (token := self._get_available_token(api_type)) is None:
                if token is None:
                    self.logger.info(f"Waiting 10 seconds before retrying to acquire token of type {api_type.value}")
                    time.sleep(10)
            else:
                self.logger.info(f"Successfully acquired new token: {token[0]} of type {api_type.value}")
                return token[0]

    def _get_available_token(self, api_type: GITHUB_API_TYPE) -> Union[Tuple[str, datetime], None]:
        with self.modify_tokens_lock:
            final_token = None
            for token in self.tokens.get(api_type).get("available"):
                if token[1] < datetime.utcnow():
                    final_token = token
                    break
            if final_token is None:
                return None
            else:
                self.tokens.get(api_type).get("available").remove(final_token)
                self.tokens.get(api_type).get("in_use").append(final_token[0])
                return final_token

    def return_token(self, return_token: str, api_type: GITHUB_API_TYPE, reuse_time: Union[datetime, str] = None):
        """
        Return a GitHub token for a specific API_TYPE with an alternative reuse time if it is used up
        """
        self.logger.info(f"Returning token: {return_token}")
        # Convert str to datetime if necessary
        if isinstance(reuse_time, str):
            reuse_time = datetime.strptime(reuse_time, "%Y-%m-%dT%H:%M:%SZ")
        # Remove the token from in_use list and add it to available
        with self.modify_tokens_lock:
            if return_token not in self.tokens.get(api_type).get("in_use"):
                self.logger.exception("Invalid token return, token does not exist")
            self.tokens.get(api_type).get("in_use").remove(return_token)
            if reuse_time is None:
                self.tokens.get(api_type).get("available").append((return_token, datetime.utcnow()))
                self.logger.info(f"Successfully returned token with immediate reuse time {datetime.utcnow()}")
            else:
                self.tokens.get(api_type).get("available").append((return_token, reuse_time))
                self.logger.info(f"Successfully returned token with reuse time {reuse_time}")

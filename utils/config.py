import os
from functools import cached_property
from pathlib import Path
from typing import Dict
from mw_vault import Vault
import yaml

import logging
from retell import Retell


logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Custom exception for configuration errors"""
    pass



class Config:
    """
    Configuration class
    """

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self.__load_config()

    def __load_config(self) -> Dict:
        """
        Load the configuration file
        """
        with open(self.config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        return config

    def __getitem__(self, key):
        return self.config[key]

    def __contains__(self, key):
        return key in self.config

    @cached_property
    def vault(self) -> Vault:
        """
        Vault object
        """
        return Vault(auto_renew_token=True)

    def set_aws_creds(self) -> Dict:
        """
        Set AWS credentials in env variables
        """
        if "aws" in self.config:
            aws_config = self.config["aws"]
            aws_creds = self.vault.get_secret(aws_config["vault_path"])

            os.environ["AWS_ACCESS_KEY_ID"] = aws_creds["AWS_ACCESS_KEY_ID"]
            os.environ["AWS_SESSION_TOKEN"] = aws_creds["AWS_SESSION_TOKEN"]
            os.environ["AWS_SECRET_ACCESS_KEY"] = aws_creds["AWS_SECRET_ACCESS_KEY"]
        else:
            raise KeyError("AWS configuration not found in config file")

    def get_retell_client(self) -> Retell:
        """
        Returns the Retell client from the config.
        """
        if "retell" not in self.config:
            raise ConfigError("No section 'retell' in config file")

        retell_config = self.config["retell"]

        if "vault_path" not in retell_config:
            raise ConfigError("No 'vault_path' in 'retell' section of config file")

        retell_creds = self.vault.get_secret(retell_config["vault_path"])

        if "api_key" not in retell_creds:
            raise ConfigError("Missing 'api_key' in Retell credentials")

        retell_client = Retell(
            api_key=retell_creds["api_key"],
        )

        return retell_client
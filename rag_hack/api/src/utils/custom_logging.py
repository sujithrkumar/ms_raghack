"""
Custom logging configuration for the project.
@author: Sujith R Kumar (sujith.kumar@course5i.com)
"""
import os
from pathlib import Path
import yaml
import logging.config
import logging
import coloredlogs


def setup_logging(config_path='configs/logging.yaml', logging_level=logging.INFO, env_key='LOG_CFG'):
    """
    Sets up logging using the logging configuration file.
    :param logging_level:
    :type logging_level:
    :param config_path: path of the configuration file. Defaults to logging.yaml
    :type config_path: string (file path)
    :param default_level:
    :type default_level:
    :param env_key: env_key where logging path can be set. Defaults to LOG_CFG.
    If this key has a value then the config_path will be overriden by this value.
    :type env_key:
    :return:
    :rtype:
    """
    value = os.getenv(env_key, None)
    if value:
        config_path = value
    config_path = Path(config_path)
    if config_path.exists():
        with config_path.open(mode="r+") as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
                coloredlogs.install()
                return logging
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=logging_level)
                coloredlogs.install(level=logging_level)
                return logging
    else:
        logging.basicConfig(level=logging_level)
        coloredlogs.install(level=logging_level)
        print('Failed to load configuration file. Using default configs')
        return logging

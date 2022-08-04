import logging
import os.path
from os import PathLike
from typing import Iterable, Optional, Union

import yaml

logger = logging.getLogger(__name__)


class Config:
    _singleton = None
    default_files = [
        os.path.join(os.path.dirname(__file__), "default.cfg.yaml"),
        os.path.expanduser("~/astrolive.cfg.yaml"),
        "./astrolive.cfg.yaml",
    ]

    def __init__(self) -> None:
        self.data = {}

    @classmethod
    def global_config(cls) -> dict:
        """Returns the global configuration data.

        Args:
            Configuration class

        Returns:
            Dict of the global configuration data
        """

        return cls.global_instance().data

    @classmethod
    def global_instance(cls) -> "Config":
        """Returns the global configuration singleton object.

        Args:
            Configuration class

        Returns:
            Config object
        """

        if cls._singleton is None:
            cls.global_instance_from_files()
        return cls._singleton

    @classmethod
    def global_instance_from_files(
        cls, source: Optional[Iterable[Union[str, PathLike]]] = None
    ) -> None:
        """Sets the global configuration singleton object.

        Args:
            Path string

        Returns:
            Config object
        """

        cls._singleton = cls.instance_from_files(source=source)

    @classmethod
    def instance_from_files(cls, source: Optional[Iterable[str]] = None) -> "Config":
        """Creates global configuration singleton object.

        Args:
            Source

        Returns:
            Config object
        """

        cfg = cls()
        cfg.read_config(source=source)
        return cfg

    def read_config(self, source: Optional[Iterable[str]] = None) -> None:
        """Reads and parses the yaml configuration.

        Args:
            Source

        Returns:
            Config object
        """

        if not source:
            source = self.default_files
        config = {}
        for src in source:
            try:
                with open(src) as fd:
                    logger.info("Loading configuration from: %s", src)
                    y = yaml.safe_load(fd)
                    config.update(y)
            except IOError:
                logger.info("Non existing config file: %s", src)
        # expand includes
        for k in config.keys():
            self.expand_includes(config, k)
        self.data = config

    @classmethod
    def expand_includes(cls, d: dir, key: str) -> None:
        """Recursively dives into the configuration for includes.

        Args:
            Config object
            Dictionary
            Key

        Returns:
            Config object
        """

        try:
            incs = d[key].pop("include")
        except KeyError:
            return
        if isinstance(incs, str):
            incs = [incs]
        for i in incs:
            cls.expand_includes(d, i)
            d[key].update(d[i])

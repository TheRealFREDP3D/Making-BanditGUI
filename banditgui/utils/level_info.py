#!/usr/bin/env python3
"""
Level Information Module

This module provides access to the level information for the Bandit wargame.
It reads the JSON data files created by the get_data.py script and implements
caching for better performance.
"""

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from banditgui.config.logging import get_logger
from banditgui.exceptions import LevelInfoError

# Set up logging
logger = get_logger('utils.level_info')


class LevelInfo:
    """
    Class for accessing level information for the Bandit wargame.

    This class provides methods to access general information, level-specific
    information, and available levels. It implements caching for better performance.
    """

    # Constants
    DATA_DIR = Path(__file__).parent.parent / "data"
    GENERAL_INFO_FILE = DATA_DIR / "general_info.json"
    LEVELS_INFO_FILE = DATA_DIR / "levels_info.json"
    ALL_DATA_FILE = DATA_DIR / "all_data.json"

    def __init__(self):
        """Initialize the LevelInfo class."""
        # Cache for data
        self._general_info_cache = None
        self._levels_info_cache = None
        self._all_data_cache = None

        logger.debug("LevelInfo initialized")

    def _load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Dict[str, Any]: The loaded JSON data

        Raises:
            LevelInfoError: If the file cannot be loaded
        """
        try:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                return {}

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Loaded JSON file: {file_path}")
                return data
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in {file_path}: {str(e)}"
            logger.error(error_msg)
            raise LevelInfoError(error_msg)
        except Exception as e:
            error_msg = f"Error loading {file_path}: {str(e)}"
            logger.error(error_msg)
            raise LevelInfoError(error_msg)

    @lru_cache(maxsize=1)
    def _get_all_data(self) -> Dict[str, Any]:
        """
        Get all data from the all_data.json file.

        Returns:
            Dict[str, Any]: All data
        """
        if self._all_data_cache is None:
            try:
                self._all_data_cache = self._load_json_file(self.ALL_DATA_FILE)
            except LevelInfoError:
                logger.warning("Failed to load all_data.json, using empty data")
                self._all_data_cache = {}

        return self._all_data_cache

    @lru_cache(maxsize=1)
    def _get_levels_data(self) -> List[Dict[str, Any]]:
        """
        Get levels data from the levels_info.json file or all_data.json.

        Returns:
            List[Dict[str, Any]]: Levels data
        """
        if self._levels_info_cache is None:
            try:
                # Try to load from levels_info.json first
                if os.path.exists(self.LEVELS_INFO_FILE):
                    self._levels_info_cache = self._load_json_file(self.LEVELS_INFO_FILE)
                # If that fails, try all_data.json
                elif os.path.exists(self.ALL_DATA_FILE):
                    all_data = self._get_all_data()
                    self._levels_info_cache = all_data.get("levels_info", [])
                else:
                    logger.warning("No level data files found")
                    self._levels_info_cache = []
            except LevelInfoError:
                logger.warning("Failed to load levels data, using empty data")
                self._levels_info_cache = []

        return self._levels_info_cache

    def get_general_info(self) -> Dict[str, str]:
        """
        Get the general information about the Bandit wargame.

        Returns:
            Dict[str, str]: General information
        """
        try:
            if self._general_info_cache is None:
                # Try to load from general_info.json first
                if os.path.exists(self.GENERAL_INFO_FILE):
                    self._general_info_cache = self._load_json_file(self.GENERAL_INFO_FILE)
                # If that fails, try all_data.json
                elif os.path.exists(self.ALL_DATA_FILE):
                    all_data = self._get_all_data()
                    self._general_info_cache = all_data.get("general_info", {})
                else:
                    logger.warning("No general info files found")
                    self._general_info_cache = {
                        "general": "General information not available. Run get_data.py to fetch it."
                    }

            return self._general_info_cache
        except Exception as e:
            error_msg = f"Error getting general information: {str(e)}"
            logger.error(error_msg)
            return {"general": error_msg}

    def get_available_levels(self) -> List[int]:
        """
        Get a list of available level numbers.

        Returns:
            List[int]: Available level numbers
        """
        try:
            levels_data = self._get_levels_data()

            if levels_data:
                return [level_data["level"] for level_data in levels_data]
            else:
                # Default to levels 0-34 if no data is available
                logger.info("No levels data available, using default range 0-34")
                return list(range(0, 35))
        except Exception as e:
            error_msg = f"Error getting available levels: {str(e)}"
            logger.error(error_msg)
            # Return a minimal set of levels in case of error
            return [0, 1]

    def get_level_info(self, level: int) -> Optional[Dict[str, str]]:
        """
        Get information for a specific level.

        Args:
            level: The level number

        Returns:
            Optional[Dict[str, str]]: Level information or None if not found
        """
        try:
            levels_data = self._get_levels_data()

            for level_data in levels_data:
                if level_data["level"] == level:
                    logger.debug(f"Found information for level {level}")
                    return level_data

            # If we get here, the level was not found
            logger.warning(f"Level {level} not found")
            return None
        except Exception as e:
            error_msg = f"Error getting level {level} information: {str(e)}"
            logger.error(error_msg)
            return None

    def get_all_levels_info(self) -> List[Dict[str, str]]:
        """
        Get information for all levels.

        Returns:
            List[Dict[str, str]]: Information for all levels
        """
        try:
            return self._get_levels_data()
        except Exception as e:
            error_msg = f"Error getting all levels information: {str(e)}"
            logger.error(error_msg)
            return []

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._general_info_cache = None
        self._levels_info_cache = None
        self._all_data_cache = None
        # Also clear the lru_cache
        self._get_all_data.cache_clear()
        self._get_levels_data.cache_clear()
        logger.debug("Cache cleared")


# Create a singleton instance
level_info = LevelInfo()

# Provide module-level functions that use the singleton
def get_general_info() -> Dict[str, str]:
    """
    Get the general information about the Bandit wargame.

    Returns:
        Dict[str, str]: General information
    """
    return level_info.get_general_info()


def get_available_levels() -> List[int]:
    """
    Get a list of available level numbers.

    Returns:
        List[int]: Available level numbers
    """
    return level_info.get_available_levels()


def get_level_info(level: int) -> Optional[Dict[str, str]]:
    """
    Get information for a specific level.

    Args:
        level: The level number

    Returns:
        Optional[Dict[str, str]]: Level information or None if not found
    """
    return level_info.get_level_info(level)


def get_all_levels_info() -> List[Dict[str, str]]:
    """
    Get information for all levels.

    Returns:
        List[Dict[str, str]]: Information for all levels
    """
    return level_info.get_all_levels_info()


def clear_cache() -> None:
    """Clear all cached data."""
    level_info.clear_cache()


if __name__ == "__main__":
    # Simple test code
    print("General Info:", get_general_info())
    print("Available Levels:", get_available_levels())
    print("Level 0 Info:", get_level_info(0))

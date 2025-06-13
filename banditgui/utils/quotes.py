"""
Quotes utility for BanditGUI.

This module provides functionality for loading and using geek pop culture quotes.
"""

import json
import os
import random
from typing import Dict, List, Optional

from banditgui.config.logging import get_logger

logger = get_logger('utils.quotes')


class QuoteManager:
    """
    Manager for geek pop culture quotes.
    """

    def __init__(self):
        """Initialize the quote manager."""
        self.quotes = []
        self.load_quotes()
        logger.debug(f"QuoteManager initialized with {len(self.quotes)} quotes")

    def load_quotes(self) -> None:
        """Load quotes from the JSON file."""
        try:
            # Get the path to the quotes file
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            quotes_file = os.path.join(current_dir, 'data', 'geek_quotes.json')

            # Load the quotes
            with open(quotes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.quotes = data.get('quotes', [])

            logger.info(f"Loaded {len(self.quotes)} quotes from {quotes_file}")
        except Exception as e:
            logger.error(f"Error loading quotes: {e}")
            # Provide some default quotes in case the file can't be loaded
            self.quotes = [
                {"text": "Have you tried turning it off and on again?", "source": "The IT Crowd", "character": "Roy"},
                {"text": "I'm giving her all she's got, Captain!", "source": "Star Trek", "character": "Scotty"},
                {"text": "These aren't the droids you're looking for.", "source": "Star Wars", "character": "Obi-Wan Kenobi"},
                {"text": "Live long and prosper.", "source": "Star Trek", "character": "Spock"},
                {"text": "The cake is a lie.", "source": "Portal", "character": "Game"}
            ]
            logger.warning(f"Using {len(self.quotes)} default quotes")

    def get_random_quote(self) -> Dict:
        """
        Get a random quote.

        Returns:
            Dict: A random quote with text, source, and character
        """
        if not self.quotes:
            return {"text": "No quotes available", "source": "System", "character": "Error"}

        return random.choice(self.quotes)

    def get_formatted_quote(self, quote: Optional[Dict] = None) -> str:
        """
        Get a formatted quote string.

        Args:
            quote: Optional specific quote to format (if None, gets a random one)

        Returns:
            str: A formatted quote string like '"Quote text"'
        """
        if quote is None:
            quote = self.get_random_quote()

        return f'"{quote["text"]}"'

    def get_quotes_by_source(self, source: str) -> List[Dict]:
        """
        Get quotes from a specific source.

        Args:
            source: The source to filter by (case-insensitive partial match)

        Returns:
            List[Dict]: List of quotes from the specified source
        """
        source = source.lower()
        return [q for q in self.quotes if source in q.get('source', '').lower()]

    def get_quotes_by_character(self, character: str) -> List[Dict]:
        """
        Get quotes from a specific character.

        Args:
            character: The character to filter by (case-insensitive partial match)

        Returns:
            List[Dict]: List of quotes from the specified character
        """
        character = character.lower()
        return [q for q in self.quotes if character in q.get('character', '').lower()]


# Create a singleton instance
quote_manager = QuoteManager()


def get_random_quote() -> Dict:
    """
    Get a random quote.

    Returns:
        Dict: A random quote with text, source, and character
    """
    return quote_manager.get_random_quote()


def get_formatted_quote() -> str:
    """
    Get a formatted random quote string.

    Returns:
        str: A formatted quote string like '"Quote text"'
    """
    return quote_manager.get_formatted_quote()


def get_terminal_welcome_quotes(count: int = 1) -> List[str]:
    """
    Get a list of formatted quotes for terminal welcome message.

    Args:
        count: Number of quotes to return

    Returns:
        List[str]: List of formatted quote strings
    """
    if not quote_manager.quotes:
        return []

    # Ensure we don't request more quotes than available
    num_to_sample = min(count, len(quote_manager.quotes))

    # Select quotes randomly without replacement
    sampled_quotes = random.sample(quote_manager.quotes, num_to_sample)

    # Format the selected quotes
    return [quote_manager.get_formatted_quote(q) for q in sampled_quotes]

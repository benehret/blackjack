"""
Card and Deck classes for the blackjack game.
"""

import os
import random
from typing import List
import pygame

from constants import CARD_WIDTH, CARD_HEIGHT, SUITS, VALUES, FACE_CARDS


class Card:
    """Represents a playing card."""
    
    def __init__(self, suit: str, value: str, image_path: str):
        self.suit = suit
        self.value = value
        self.image = self._load_image(image_path)

    def _load_image(self, image_path: str) -> pygame.Surface:
        """Load and scale the card image."""
        image = pygame.image.load(image_path)
        return pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))

    def get_numeric_value(self) -> int:
        """Get the numeric value of the card for blackjack scoring."""
        if self.value in FACE_CARDS:
            return 10
        elif self.value == 'ace':
            return 11
        else:
            return int(self.value)

    def __str__(self) -> str:
        return f"{self.value.title()} of {self.suit.title()}"

    def __repr__(self) -> str:
        return f"Card('{self.suit}', '{self.value}')"


class Deck:
    """Represents a deck of playing cards."""
    
    def __init__(self):
        self.cards = []
        self._create_deck()
        self.shuffle()

    def _create_deck(self) -> None:
        """Create a full deck of 52 cards."""
        for suit in SUITS:
            for value in VALUES:
                image_path = self._get_image_path(suit, value)
                self.cards.append(Card(suit, value, image_path))

    def _get_image_path(self, suit: str, value: str) -> str:
        """Get the image path for a card."""
        if value in FACE_CARDS:
            return os.path.join('cards', f'{value}_of_{suit}2.png')
        else:
            return os.path.join('cards', f'{value}_of_{suit}.png')

    def shuffle(self) -> None:
        """Shuffle the deck."""
        random.shuffle(self.cards)

    def draw(self) -> Card:
        """Draw a card from the deck."""
        if not self.cards:
            raise ValueError("Cannot draw from empty deck")
        return self.cards.pop()

    def cards_remaining(self) -> int:
        """Get the number of cards remaining in the deck."""
        return len(self.cards)

    def is_low(self, threshold: int = 20) -> bool:
        """Check if the deck is running low on cards."""
        return len(self.cards) < threshold
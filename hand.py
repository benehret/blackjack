"""
Hand class for managing cards and game state.
"""

from typing import List
from card import Card


class Hand:
    """Represents a hand of cards in blackjack."""
    
    def __init__(self, cards: List[Card] = None, bet: int = 0):
        self.cards = cards if cards else []
        self.bet = bet
        self.doubled = False
        self.finished = False
        self.busted = False
        self.blackjack = False

    def add_card(self, card: Card) -> None:
        """Add a card to the hand."""
        self.cards.append(card)

    def calculate_score(self) -> int:
        """Calculate the best possible score for the hand."""
        score = 0
        aces = 0
        
        # Count non-ace cards first
        for card in self.cards:
            if card.value == 'ace':
                aces += 1
            else:
                score += card.get_numeric_value()
        
        # Add aces, using 11 when possible, 1 otherwise
        for _ in range(aces):
            if score + 11 <= 21:
                score += 11
            else:
                score += 1
                
        return score

    def is_bust(self) -> bool:
        """Check if the hand is busted (over 21)."""
        return self.calculate_score() > 21

    def is_blackjack(self) -> bool:
        """Check if the hand is a natural blackjack."""
        return len(self.cards) == 2 and self.calculate_score() == 21

    def can_split(self) -> bool:
        """Check if the hand can be split."""
        if len(self.cards) != 2:
            return False
        return self.cards[0].get_numeric_value() == self.cards[1].get_numeric_value()

    def can_double_down(self, available_money: int) -> bool:
        """Check if the hand can be doubled down."""
        return (len(self.cards) == 2 and 
                not self.doubled and 
                not self.finished and 
                self.bet <= available_money)

    def double_down(self) -> int:
        """Double the bet and mark as doubled. Returns the additional bet amount."""
        if not self.can_double_down(self.bet):
            raise ValueError("Cannot double down on this hand")
        
        additional_bet = self.bet
        self.bet *= 2
        self.doubled = True
        return additional_bet

    def split(self) -> 'Hand':
        """Split the hand and return the new hand with the second card."""
        if not self.can_split():
            raise ValueError("Cannot split this hand")
        
        # Remove the second card and create new hand
        second_card = self.cards.pop()
        new_hand = Hand([second_card], self.bet)
        
        return new_hand

    def get_status_string(self) -> str:
        """Get a string representation of the hand's status."""
        if self.busted:
            return "BUST"
        elif self.blackjack:
            return "BLACKJACK"
        elif self.finished:
            return "STAND"
        elif self.doubled:
            return "DOUBLED"
        else:
            return ""

    def __str__(self) -> str:
        cards_str = ', '.join(str(card) for card in self.cards)
        return f"Hand: [{cards_str}] Score: {self.calculate_score()} Bet: ${self.bet}"

    def __len__(self) -> int:
        return len(self.cards)
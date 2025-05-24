"""
Main game logic for the blackjack game.
"""

import time
from typing import List, Optional
from enum import Enum

from card import Card, Deck
from hand import Hand
from constants import STARTING_BANKROLL, DEALER_PLAY_DELAY, MAX_SPLIT_HANDS, DECK_RESHUFFLE_THRESHOLD


class GameState(Enum):
    """Enumeration of possible game states."""
    BETTING = "betting"
    PLAYING = "playing"
    DEALER_TURN = "dealer_turn"
    ROUND_COMPLETE = "round_complete"
    GAME_OVER = "game_over"


class BlackjackGame:
    """Main game logic for blackjack."""
    
    def __init__(self):
        self.deck = Deck()
        self.player_hands: List[Hand] = []
        self.dealer_hand = Hand()
        self.current_hand_index = 0
        
        # Game state
        self.state = GameState.BETTING
        self.message = ""
        
        # Dealer timing
        self.last_dealer_action_time = 0
        self.dealer_card_revealed = False
        
        # Betting system
        self.bankroll = STARTING_BANKROLL
        self.current_bet = 0
        self.split_count = 0

    def place_bet(self, amount: int) -> bool:
        """Place a bet. Returns True if successful."""
        if self.state != GameState.BETTING or amount > self.bankroll:
            return False
        
        self.current_bet += amount
        self.bankroll -= amount
        return True

    def can_deal(self) -> bool:
        """Check if cards can be dealt."""
        return self.state == GameState.BETTING and self.current_bet > 0

    def deal_initial_cards(self) -> None:
        """Deal the initial cards to start a round."""
        if not self.can_deal():
            return
        
        # Create initial player hand
        player_hand = Hand(bet=self.current_bet)
        player_hand.add_card(self.deck.draw())
        player_hand.add_card(self.deck.draw())
        self.player_hands = [player_hand]
        
        # Deal dealer cards
        self.dealer_hand = Hand()
        self.dealer_hand.add_card(self.deck.draw())
        self.dealer_hand.add_card(self.deck.draw())
        
        # Reset state
        self.current_hand_index = 0
        self.state = GameState.PLAYING
        self.message = ""
        self.dealer_card_revealed = False
        self.split_count = 0
        
        # Check for blackjack
        if player_hand.is_blackjack():
            self._handle_player_blackjack()

    def _handle_player_blackjack(self) -> None:
        """Handle when player gets blackjack on initial deal."""
        player_hand = self.player_hands[0]
        self.dealer_card_revealed = True
        
        if self.dealer_hand.is_blackjack():
            self.message = "Push! Both have blackjack!"
            self.bankroll += self.current_bet  # Return bet
        else:
            self.message = "Blackjack! You win!"
            self.bankroll += int(self.current_bet * 2.5)  # 3:2 payout
        
        player_hand.blackjack = True
        self.state = GameState.ROUND_COMPLETE

    def get_current_hand(self) -> Optional[Hand]:
        """Get the currently active hand."""
        if self.current_hand_index < len(self.player_hands):
            return self.player_hands[self.current_hand_index]
        return None

    def can_hit(self) -> bool:
        """Check if player can hit."""
        if self.state != GameState.PLAYING:
            return False
        
        current_hand = self.get_current_hand()
        return current_hand is not None and not current_hand.finished

    def can_stand(self) -> bool:
        """Check if player can stand."""
        return self.can_hit()

    def can_double_down(self) -> bool:
        """Check if player can double down."""
        if self.state != GameState.PLAYING:
            return False
        
        current_hand = self.get_current_hand()
        return (current_hand is not None and 
                current_hand.can_double_down(self.bankroll))

    def can_split(self) -> bool:
        """Check if player can split."""
        if self.state != GameState.PLAYING or self.split_count >= MAX_SPLIT_HANDS - 1:
            return False
        
        current_hand = self.get_current_hand()
        return (current_hand is not None and 
                current_hand.can_split() and 
                current_hand.bet <= self.bankroll)

    def hit(self) -> None:
        """Player hits (takes another card)."""
        if not self.can_hit():
            return
        
        current_hand = self.get_current_hand()
        current_hand.add_card(self.deck.draw())
        
        if current_hand.is_bust():
            current_hand.busted = True
            current_hand.finished = True
            self._next_hand()
        elif current_hand.calculate_score() == 21:  # Add this line
            current_hand.finished = True            # Add this line
            self._next_hand()                       # Add this line
        elif current_hand.doubled:
            # After doubling, you get one card and hand is finished
            current_hand.finished = True
            self._next_hand()

    def stand(self) -> None:
        """Player stands (finishes current hand)."""
        if not self.can_stand():
            return
        
        current_hand = self.get_current_hand()
        current_hand.finished = True
        self._next_hand()

    def double_down(self) -> None:
        """Player doubles down."""
        if not self.can_double_down():
            return
        
        current_hand = self.get_current_hand()
        additional_bet = current_hand.double_down()
        self.bankroll -= additional_bet
        self.hit()  # Get one card and finish hand

    def split_hand(self) -> None:
        """Split the current hand."""
        if not self.can_split():
            return
        
        current_hand = self.get_current_hand()
        
        # Create new hand with the split card
        new_hand = current_hand.split()
        
        # Add new cards to both hands
        current_hand.add_card(self.deck.draw())
        new_hand.add_card(self.deck.draw())
        
        # Insert new hand after current hand
        self.player_hands.insert(self.current_hand_index + 1, new_hand)
        
        # Deduct additional bet
        self.bankroll -= current_hand.bet
        self.split_count += 1

    def _next_hand(self) -> None:
        """Move to the next hand or start dealer's turn."""
        self.current_hand_index += 1
        if self.current_hand_index >= len(self.player_hands):
            # All hands finished, dealer's turn
            self.state = GameState.DEALER_TURN
            self.last_dealer_action_time = time.time()

    def update_dealer(self) -> None:
        """Update dealer's turn (called each frame)."""
        if self.state != GameState.DEALER_TURN:
            return
        
        current_time = time.time()
        
        if not self.dealer_card_revealed:
            if current_time - self.last_dealer_action_time >= DEALER_PLAY_DELAY:
                self.dealer_card_revealed = True
                self.last_dealer_action_time = current_time
        else:
            dealer_score = self.dealer_hand.calculate_score()
            if dealer_score < 17:
                if current_time - self.last_dealer_action_time >= DEALER_PLAY_DELAY:
                    self.dealer_hand.add_card(self.deck.draw())
                    self.last_dealer_action_time = current_time
            else:
                self._end_round()

    def _end_round(self) -> None:
        """End the round and calculate results."""
        dealer_score = self.dealer_hand.calculate_score()
        dealer_busted = self.dealer_hand.is_bust()
        
        total_winnings = 0
        results = []
        
        for i, hand in enumerate(self.player_hands):
            player_score = hand.calculate_score()
            hand_result, winnings = self._calculate_hand_result(hand, dealer_score, dealer_busted)
            
            total_winnings += winnings
            results.append(f"Hand {i+1}: {hand_result}")
        
        self.bankroll += total_winnings
        
        # Create message
        if len(self.player_hands) == 1:
            self.message = results[0].replace("Hand 1: ", "")
        else:
            self.message = " | ".join(results)
        
        self.state = GameState.ROUND_COMPLETE

    def _calculate_hand_result(self, hand: Hand, dealer_score: int, dealer_busted: bool) -> tuple[str, int]:
        """Calculate the result and winnings for a single hand."""
        player_score = hand.calculate_score()
        
        if hand.busted:
            return "Bust", 0
        elif hand.blackjack and not self.dealer_hand.is_blackjack():
            return "Blackjack!", int(hand.bet * 2.5)  # 3:2 payout
        elif dealer_busted:
            return "Win (Dealer Bust)", hand.bet * 2
        elif dealer_score > player_score:
            return "Lose", 0
        elif dealer_score < player_score:
            return "Win", hand.bet * 2
        else:
            return "Push", hand.bet  # Return bet

    def new_round(self) -> None:
        """Start a new round."""
        if self.deck.is_low(DECK_RESHUFFLE_THRESHOLD):
            self.deck = Deck()
        
        self.player_hands = []
        self.dealer_hand = Hand()
        self.current_hand_index = 0
        self.current_bet = 0
        self.state = GameState.BETTING
        self.message = ""
        self.dealer_card_revealed = False
        self.split_count = 0

    def is_game_over(self) -> bool:
        """Check if the game is over (no money left)."""
        return self.bankroll == 0 and self.current_bet == 0 and self.state == GameState.BETTING

    def get_game_state(self) -> GameState:
        """Get the current game state."""
        if self.is_game_over():
            return GameState.GAME_OVER
        return self.state

    # Properties for UI access
    @property
    def is_betting_phase(self) -> bool:
        return self.state == GameState.BETTING

    @property
    def is_playing_phase(self) -> bool:
        return self.state == GameState.PLAYING

    @property
    def is_dealer_turn(self) -> bool:
        return self.state == GameState.DEALER_TURN

    @property
    def is_round_complete(self) -> bool:
        return self.state == GameState.ROUND_COMPLETE

    @property
    def hide_dealer_card(self) -> bool:
        """Whether to hide the dealer's first card."""
        return not self.dealer_card_revealed
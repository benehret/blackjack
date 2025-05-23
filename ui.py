"""
User interface components for the blackjack game.
"""

from typing import Tuple, List
import pygame

from constants import (
    BUTTON_WIDTH, BUTTON_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT,
    CARD_WIDTH, CARD_HEIGHT, WHITE, BLACK, GRAY, BLUE, GOLD, RED, GREEN
)
from hand import Hand


class Button:
    """Represents a clickable button."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, color: Tuple[int, int, int]):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 32)
        self.enabled = True

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button on the given surface."""
        color = self.color if self.enabled else GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if the button was clicked at the given position."""
        return self.rect.collidepoint(pos) and self.enabled

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the button."""
        self.enabled = enabled


class GameUI:
    """Manages the game's user interface."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Create buttons
        self._create_buttons()

    def _create_buttons(self) -> None:
        """Create all game buttons."""
        # Game action buttons
        self.hit_button = Button(50, WINDOW_HEIGHT - 100, 120, BUTTON_HEIGHT, "Hit", WHITE)
        self.stand_button = Button(180, WINDOW_HEIGHT - 100, 120, BUTTON_HEIGHT, "Stand", WHITE)
        self.double_button = Button(310, WINDOW_HEIGHT - 100, 120, BUTTON_HEIGHT, "Double", BLUE)
        self.split_button = Button(440, WINDOW_HEIGHT - 100, 120, BUTTON_HEIGHT, "Split", BLUE)
        
        # Control buttons
        self.play_again_button = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 50, 
                                      BUTTON_WIDTH, BUTTON_HEIGHT, "Play Again", WHITE)
        
        # Betting buttons
        bet_button_y = WINDOW_HEIGHT - 200
        self.bet_5_button = Button(WINDOW_WIDTH//2 - 320, bet_button_y, 120, BUTTON_HEIGHT, "Bet $5", GOLD)
        self.bet_10_button = Button(WINDOW_WIDTH//2 - 180, bet_button_y, 120, BUTTON_HEIGHT, "Bet $10", GOLD)
        self.bet_25_button = Button(WINDOW_WIDTH//2 - 40, bet_button_y, 120, BUTTON_HEIGHT, "Bet $25", GOLD)
        self.bet_50_button = Button(WINDOW_WIDTH//2 + 100, bet_button_y, 120, BUTTON_HEIGHT, "Bet $50", GOLD)
        self.bet_100_button = Button(WINDOW_WIDTH//2 + 240, bet_button_y, 120, BUTTON_HEIGHT, "Bet $100", GOLD)
        
        self.deal_button = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT - 130, 
                                BUTTON_WIDTH, BUTTON_HEIGHT, "Deal Cards", WHITE)

    def draw_background(self) -> None:
        """Draw the game background."""
        self.screen.fill(GREEN)

    def draw_bankroll_info(self, bankroll: int, current_bet: int) -> None:
        """Draw bankroll and bet information."""
        bankroll_text = self.font.render(f"Bankroll: ${bankroll}", True, WHITE)
        bet_text = self.font.render(f"Current Bet: ${current_bet}", True, WHITE)
        self.screen.blit(bankroll_text, (WINDOW_WIDTH - 200, 20))
        self.screen.blit(bet_text, (WINDOW_WIDTH - 200, 60))

    def draw_betting_instructions(self) -> None:
        """Draw betting phase instructions."""
        instruction_text = self.font.render("Place your bet and click Deal Cards!", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH//2, 300))
        self.screen.blit(instruction_text, instruction_rect)

    def draw_dealer_cards(self, dealer_hand: Hand, hide_first_card: bool) -> None:
        """Draw the dealer's cards."""
        for i, card in enumerate(dealer_hand.cards):
            x_pos = 50 + i * (CARD_WIDTH + 10)
            y_pos = 50
            
            if i == 0 and hide_first_card:
                # Draw card back for dealer's hidden card
                pygame.draw.rect(self.screen, RED, (x_pos, y_pos, CARD_WIDTH, CARD_HEIGHT))
                # Add some pattern to make it look like a card back
                pygame.draw.rect(self.screen, WHITE, (x_pos + 10, y_pos + 10, CARD_WIDTH - 20, CARD_HEIGHT - 20), 2)
            else:
                self.screen.blit(card.image, (x_pos, y_pos))

    def draw_player_hands(self, player_hands: List[Hand], current_hand_index: int, 
                         dealer_revealing: bool) -> None:
        """Draw all player hands."""
        num_hands = len(player_hands)
        
        if num_hands == 1:
            self._draw_single_hand(player_hands[0], current_hand_index, dealer_revealing)
        else:
            self._draw_multiple_hands(player_hands, current_hand_index, dealer_revealing)

    def _draw_single_hand(self, hand: Hand, current_hand_index: int, dealer_revealing: bool) -> None:
        """Draw a single player hand."""
        x_pos = 50
        y_pos = WINDOW_HEIGHT - 320
        
        # Highlight current hand
        if not hand.finished and not dealer_revealing:
            pygame.draw.rect(self.screen, BLUE, 
                           (x_pos - 10, y_pos - 10, 
                            len(hand.cards) * (CARD_WIDTH + 10) + 20, CARD_HEIGHT + 40), 3)
        
        # Draw cards
        for i, card in enumerate(hand.cards):
            self.screen.blit(card.image, (x_pos + i * (CARD_WIDTH + 10), y_pos))
        
        # Draw hand info
        self._draw_hand_info(hand, x_pos, y_pos, single_hand=True)

    def _draw_multiple_hands(self, player_hands: List[Hand], current_hand_index: int, 
                           dealer_revealing: bool) -> None:
        """Draw multiple player hands."""
        num_hands = len(player_hands)
        total_width = WINDOW_WIDTH - 100
        hand_width = total_width // num_hands
        
        for hand_idx, hand in enumerate(player_hands):
            x_pos = 50 + hand_idx * hand_width
            y_pos = WINDOW_HEIGHT - 320
            
            # Highlight current hand
            if (hand_idx == current_hand_index and not hand.finished and not dealer_revealing):
                pygame.draw.rect(self.screen, BLUE, 
                               (x_pos - 10, y_pos - 10, 
                                min(len(hand.cards) * (CARD_WIDTH + 10) + 20, hand_width), 
                                CARD_HEIGHT + 60), 3)
            
            # Draw cards with appropriate spacing
            card_spacing = min(CARD_WIDTH + 10, (hand_width - 20) // max(len(hand.cards), 1))
            for i, card in enumerate(hand.cards):
                card_x = x_pos + i * card_spacing
                if card_x + CARD_WIDTH <= x_pos + hand_width - 20:
                    self.screen.blit(card.image, (card_x, y_pos))
            
            # Draw hand info
            self._draw_hand_info(hand, x_pos, y_pos, single_hand=False, hand_index=hand_idx)

    def _draw_hand_info(self, hand: Hand, x_pos: int, y_pos: int, 
                       single_hand: bool = True, hand_index: int = 0) -> None:
        """Draw information about a hand."""
        hand_score = hand.calculate_score()
        status = hand.get_status_string()
        status_text = f" ({status})" if status else ""
        
        if single_hand:
            hand_text = self.small_font.render(f"Score: {hand_score}{status_text} | Bet: ${hand.bet}", 
                                             True, WHITE)
            self.screen.blit(hand_text, (x_pos, y_pos + CARD_HEIGHT + 5))
        else:
            # Shorter text for multiple hands
            short_status = self._get_short_status(status)
            hand_text = self.small_font.render(f"H{hand_index + 1}: {hand_score}{short_status}", 
                                             True, WHITE)
            bet_text = self.small_font.render(f"${hand.bet}", True, WHITE)
            self.screen.blit(hand_text, (x_pos, y_pos + CARD_HEIGHT + 5))
            self.screen.blit(bet_text, (x_pos, y_pos + CARD_HEIGHT + 25))

    def _get_short_status(self, status: str) -> str:
        """Get abbreviated status for multiple hands display."""
        status_map = {
            "BUST": " (BUST)",
            "BLACKJACK": " (BJ)",
            "STAND": " (STAND)",
            "DOUBLED": " (2X)"
        }
        return status_map.get(status, "")

    def draw_dealer_info(self, dealer_hand: Hand, card_revealed: bool) -> None:
        """Draw dealer score information."""
        dealer_score = dealer_hand.calculate_score() if card_revealed else "?"
        dealer_text = self.font.render(f"Dealer: {dealer_score}", True, WHITE)
        self.screen.blit(dealer_text, (50, 20))

    def draw_current_hand_indicator(self, current_hand_index: int) -> None:
        """Draw indicator for which hand is currently being played."""
        current_hand_text = self.small_font.render(f"Playing Hand {current_hand_index + 1}", True, WHITE)
        self.screen.blit(current_hand_text, (WINDOW_WIDTH - 200, 100))

    def draw_message(self, message: str) -> None:
        """Draw game messages."""
        if not message:
            return
            
        # Handle long messages by splitting them
        if len(message) > 40:
            parts = message.split(" | ")
            for i, part in enumerate(parts):
                message_text = self.small_font.render(part, True, WHITE)
                message_rect = message_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50 + i * 25))
                self.screen.blit(message_text, message_rect)
        else:
            message_text = self.font.render(message, True, WHITE)
            message_rect = message_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
            self.screen.blit(message_text, message_rect)

    def draw_game_over(self) -> None:
        """Draw game over message."""
        game_over_text = self.font.render("Game Over! No money left!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        self.screen.blit(game_over_text, game_over_rect)

    def draw_betting_buttons(self) -> None:
        """Draw all betting-related buttons."""
        self.bet_5_button.draw(self.screen)
        self.bet_10_button.draw(self.screen)
        self.bet_25_button.draw(self.screen)
        self.bet_50_button.draw(self.screen)
        self.bet_100_button.draw(self.screen)

    def draw_action_buttons(self) -> None:
        """Draw all game action buttons."""
        self.hit_button.draw(self.screen)
        self.stand_button.draw(self.screen)
        self.double_button.draw(self.screen)
        self.split_button.draw(self.screen)

    def update_betting_buttons(self, bankroll: int) -> None:
        """Update the enabled state of betting buttons based on bankroll."""
        self.bet_5_button.set_enabled(bankroll >= 5)
        self.bet_10_button.set_enabled(bankroll >= 10)
        self.bet_25_button.set_enabled(bankroll >= 25)
        self.bet_50_button.set_enabled(bankroll >= 50)
        self.bet_100_button.set_enabled(bankroll >= 100)
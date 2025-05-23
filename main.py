"""
Main entry point for the blackjack game.
"""

import pygame
import sys
from typing import Tuple

from constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from game import BlackjackGame, GameState
from ui import GameUI


class BlackjackApp:
    """Main application class that handles the game loop and events."""
    
    def __init__(self):
        pygame.init()
        
        # Set up display
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Blackjack")
        self.clock = pygame.time.Clock()
        
        # Initialize game components
        self.game = BlackjackGame()
        self.ui = GameUI(self.screen)
        
        self.running = True

    def handle_events(self) -> None:
        """Handle all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(pygame.mouse.get_pos())

    def _handle_mouse_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Handle mouse click events based on current game state."""
        if self.game.is_betting_phase:
            self._handle_betting_clicks(mouse_pos)
        elif self.game.is_playing_phase:
            self._handle_action_clicks(mouse_pos)
        elif self.game.is_round_complete:
            self._handle_round_complete_clicks(mouse_pos)

    def _handle_betting_clicks(self, mouse_pos: Tuple[int, int]) -> None:
        """Handle clicks during betting phase."""
        ui = self.ui
        
        if ui.bet_5_button.is_clicked(mouse_pos):
            self.game.place_bet(5)
        elif ui.bet_10_button.is_clicked(mouse_pos):
            self.game.place_bet(10)
        elif ui.bet_25_button.is_clicked(mouse_pos):
            self.game.place_bet(25)
        elif ui.bet_50_button.is_clicked(mouse_pos):
            self.game.place_bet(50)
        elif ui.bet_100_button.is_clicked(mouse_pos):
            self.game.place_bet(100)
        elif ui.deal_button.is_clicked(mouse_pos) and self.game.can_deal():
            self.game.deal_initial_cards()

    def _handle_action_clicks(self, mouse_pos: Tuple[int, int]) -> None:
        """Handle clicks during playing phase."""
        ui = self.ui
        
        if ui.hit_button.is_clicked(mouse_pos):
            self.game.hit()
        elif ui.stand_button.is_clicked(mouse_pos):
            self.game.stand()
        elif ui.double_button.is_clicked(mouse_pos):
            self.game.double_down()
        elif ui.split_button.is_clicked(mouse_pos):
            self.game.split_hand()

    def _handle_round_complete_clicks(self, mouse_pos: Tuple[int, int]) -> None:
        """Handle clicks when round is complete."""
        ui = self.ui
        
        if ui.play_again_button.is_clicked(mouse_pos):
            self.game.new_round()

    def update(self) -> None:
        """Update game state."""
        self.game.update_dealer()
        self._update_ui()

    def _update_ui(self) -> None:
        """Update UI component states."""
        # Update betting buttons
        self.ui.update_betting_buttons(self.game.bankroll)
        
        # Update action buttons
        self._update_action_buttons()

    def _update_action_buttons(self) -> None:
        """Update action button states based on game state."""
        ui = self.ui
        
        ui.hit_button.set_enabled(self.game.can_hit())
        ui.stand_button.set_enabled(self.game.can_stand())
        ui.double_button.set_enabled(self.game.can_double_down())
        ui.split_button.set_enabled(self.game.can_split())

    def render(self) -> None:
        """Render the game."""
        ui = self.ui
        game = self.game
        
        # Draw background
        ui.draw_background()
        
        # Draw bankroll info
        ui.draw_bankroll_info(game.bankroll, game.current_bet)
        
        # Draw based on game state
        if game.get_game_state() == GameState.GAME_OVER:
            ui.draw_game_over()
        elif game.is_betting_phase:
            self._render_betting_phase()
        else:
            self._render_playing_phase()
        
        # Draw message
        ui.draw_message(game.message)
        
        # Update display
        pygame.display.flip()

    def _render_betting_phase(self) -> None:
        """Render the betting phase."""
        ui = self.ui
        
        if self.game.current_bet == 0:
            ui.draw_betting_instructions()
        
        # Draw betting buttons
        ui.draw_betting_buttons()
        
        if self.game.current_bet > 0:
            ui.deal_button.draw(ui.screen)

    def _render_playing_phase(self) -> None:
        """Render the playing phase."""
        ui = self.ui
        game = self.game
        
        # Draw dealer cards
        ui.draw_dealer_cards(game.dealer_hand, game.hide_dealer_card)
        
        # Draw dealer info
        ui.draw_dealer_info(game.dealer_hand, game.dealer_card_revealed)
        
        # Draw player hands
        ui.draw_player_hands(game.player_hands, game.current_hand_index, game.is_dealer_turn)
        
        # Show current hand indicator for multiple hands
        if len(game.player_hands) > 1 and not game.is_dealer_turn:
            ui.draw_current_hand_indicator(game.current_hand_index)
        
        # Draw appropriate buttons
        if game.is_playing_phase:
            ui.draw_action_buttons()
        elif game.is_round_complete:
            ui.play_again_button.draw(ui.screen)

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


def main():
    """Main entry point."""
    try:
        app = BlackjackApp()
        app.run()
    except Exception as e:
        print(f"Error running game: {e}")
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()
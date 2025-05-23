import pygame
import random
import os
from typing import List, Tuple
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
CARD_WIDTH = 100
CARD_HEIGHT = 145
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
FPS = 60
DEALER_PLAY_DELAY = 1.0  # Seconds between dealer actions

# Colors
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GOLD = (255, 215, 0)
GRAY = (128, 128, 128)
BLUE = (100, 150, 255)

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Blackjack")
clock = pygame.time.Clock()

class Card:
    def __init__(self, suit: str, value: str, image_path: str):
        self.suit = suit
        self.value = value
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))

    def get_value(self) -> int:
        if self.value in ['jack', 'queen', 'king']:
            return 10
        elif self.value == 'ace':
            return 11
        else:
            return int(self.value)

class Hand:
    def __init__(self, cards: List[Card] = None, bet: int = 0):
        self.cards = cards if cards else []
        self.bet = bet
        self.doubled = False
        self.finished = False
        self.busted = False
        self.blackjack = False

    def add_card(self, card: Card):
        self.cards.append(card)

    def calculate_score(self) -> int:
        score = 0
        aces = 0
        
        for card in self.cards:
            if card.value == 'ace':
                aces += 1
            else:
                score += card.get_value()
        
        for _ in range(aces):
            if score + 11 <= 21:
                score += 11
            else:
                score += 1
                
        return score

    def is_bust(self) -> bool:
        return self.calculate_score() > 21

    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.calculate_score() == 21

    def can_split(self) -> bool:
        return len(self.cards) == 2 and self.cards[0].get_value() == self.cards[1].get_value()

class Deck:
    def __init__(self):
        self.cards = []
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        values = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']
        
        for suit in suits:
            for value in values:
                image_path = os.path.join('cards', f'{value}_of_{suit}.png')
                if value in ['jack', 'queen', 'king']:
                    image_path = os.path.join('cards', f'{value}_of_{suit}2.png')
                self.cards.append(Card(suit, value, image_path))
        
        random.shuffle(self.cards)

    def draw(self) -> Card:
        return self.cards.pop()

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int]):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 32)
        self.enabled = True

    def draw(self, surface: pygame.Surface):
        color = self.color if self.enabled else GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos) and self.enabled

    def set_enabled(self, enabled: bool):
        self.enabled = enabled

class Game:
    def __init__(self):
        self.deck = Deck()
        self.player_hands = []
        self.dealer_hand = Hand()
        self.current_hand_index = 0
        self.game_over = False
        self.message = ""
        self.dealer_revealing = False
        self.last_dealer_action_time = 0
        self.dealer_card_revealed = False
        self.dealer_done = False
        
        # Betting system
        self.bankroll = 1000  # Starting money
        self.current_bet = 0
        self.betting_phase = True
        self.round_complete = False
        self.split_count = 0
        
        # Create buttons
        self.hit_button = Button(50, WINDOW_HEIGHT - 100, 120, BUTTON_HEIGHT, "Hit", WHITE)
        self.stand_button = Button(180, WINDOW_HEIGHT - 100, 120, BUTTON_HEIGHT, "Stand", WHITE)
        self.double_button = Button(310, WINDOW_HEIGHT - 100, 120, BUTTON_HEIGHT, "Double", BLUE)
        self.split_button = Button(440, WINDOW_HEIGHT - 100, 120, BUTTON_HEIGHT, "Split", BLUE)
        self.play_again_button = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 50, 
                                      BUTTON_WIDTH, BUTTON_HEIGHT, "Play Again", WHITE)
        
        # Betting buttons
        self.bet_5_button = Button(WINDOW_WIDTH//2 - 320, WINDOW_HEIGHT - 200, 
                                 120, BUTTON_HEIGHT, "Bet $5", GOLD)
        self.bet_10_button = Button(WINDOW_WIDTH//2 - 180, WINDOW_HEIGHT - 200, 
                                  120, BUTTON_HEIGHT, "Bet $10", GOLD)
        self.bet_25_button = Button(WINDOW_WIDTH//2 - 40, WINDOW_HEIGHT - 200, 
                                  120, BUTTON_HEIGHT, "Bet $25", GOLD)
        self.bet_50_button = Button(WINDOW_WIDTH//2 + 100, WINDOW_HEIGHT - 200, 
                                  120, BUTTON_HEIGHT, "Bet $50", GOLD)
        self.bet_100_button = Button(WINDOW_WIDTH//2 + 240, WINDOW_HEIGHT - 200, 
                                   120, BUTTON_HEIGHT, "Bet $100", GOLD)
        self.deal_button = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT - 130, 
                                BUTTON_WIDTH, BUTTON_HEIGHT, "Deal Cards", WHITE)

    def place_bet(self, amount: int):
        if self.betting_phase and amount <= self.bankroll:
            self.current_bet += amount
            self.bankroll -= amount
            self.update_betting_buttons()

    def update_betting_buttons(self):
        self.bet_5_button.set_enabled(self.bankroll >= 5)
        self.bet_10_button.set_enabled(self.bankroll >= 10)
        self.bet_25_button.set_enabled(self.bankroll >= 25)
        self.bet_50_button.set_enabled(self.bankroll >= 50)
        self.bet_100_button.set_enabled(self.bankroll >= 100)

    def deal_initial_cards(self):
        if self.current_bet > 0:
            # Create initial hand
            player_hand = Hand(bet=self.current_bet)
            player_hand.add_card(self.deck.draw())
            player_hand.add_card(self.deck.draw())
            self.player_hands = [player_hand]
            
            # Deal dealer cards
            self.dealer_hand = Hand()
            self.dealer_hand.add_card(self.deck.draw())
            self.dealer_hand.add_card(self.deck.draw())
            
            self.current_hand_index = 0
            self.game_over = False
            self.message = ""
            self.dealer_revealing = False
            self.last_dealer_action_time = 0
            self.dealer_card_revealed = False
            self.dealer_done = False
            self.betting_phase = False
            self.round_complete = False
            self.split_count = 0
            
            # Check for blackjack
            if player_hand.is_blackjack():
                self.dealer_card_revealed = True
                if self.dealer_hand.is_blackjack():
                    self.message = "Push! Both have blackjack!"
                    self.bankroll += self.current_bet  # Return bet
                else:
                    self.message = "Blackjack! You win!"
                    self.bankroll += int(self.current_bet * 2.5)  # 3:2 payout
                self.game_over = True
                self.dealer_done = True
                self.round_complete = True
                player_hand.blackjack = True

    def get_current_hand(self) -> Hand:
        if self.current_hand_index < len(self.player_hands):
            return self.player_hands[self.current_hand_index]
        return None

    def can_double_down(self) -> bool:
        current_hand = self.get_current_hand()
        if not current_hand or current_hand.doubled:
            return False
        return (len(current_hand.cards) == 2 and 
                current_hand.bet <= self.bankroll and
                not current_hand.finished)

    def can_split(self) -> bool:
        current_hand = self.get_current_hand()
        if not current_hand or self.split_count >= 3:  # Max 4 hands
            return False
        return (current_hand.can_split() and 
                current_hand.bet <= self.bankroll and
                not current_hand.finished)

    def hit(self):
        if not self.game_over and not self.dealer_revealing and not self.betting_phase:
            current_hand = self.get_current_hand()
            if current_hand and not current_hand.finished:
                current_hand.add_card(self.deck.draw())
                
                if current_hand.is_bust():
                    current_hand.busted = True
                    current_hand.finished = True
                    self.next_hand()
                elif current_hand.doubled:
                    # After doubling, you get one card and hand is finished
                    current_hand.finished = True
                    self.next_hand()

    def stand(self):
        if not self.game_over and not self.dealer_revealing and not self.betting_phase:
            current_hand = self.get_current_hand()
            if current_hand and not current_hand.finished:
                current_hand.finished = True
                self.next_hand()

    def double_down(self):
        if self.can_double_down():
            current_hand = self.get_current_hand()
            self.bankroll -= current_hand.bet
            current_hand.bet *= 2
            current_hand.doubled = True
            self.hit()  # Get one card and finish hand

    def split_hand(self):
        if self.can_split():
            current_hand = self.get_current_hand()
            
            # Create new hand with second card
            new_hand = Hand(bet=current_hand.bet)
            new_hand.add_card(current_hand.cards.pop())
            
            # Add a card to each hand
            current_hand.add_card(self.deck.draw())
            new_hand.add_card(self.deck.draw())
            
            # Insert new hand after current hand
            self.player_hands.insert(self.current_hand_index + 1, new_hand)
            
            # Deduct additional bet
            self.bankroll -= current_hand.bet
            self.split_count += 1

    def next_hand(self):
        self.current_hand_index += 1
        if self.current_hand_index >= len(self.player_hands):
            # All hands finished, dealer's turn
            self.dealer_revealing = True
            self.last_dealer_action_time = time.time()

    def update_dealer(self):
        current_time = time.time()
        
        if self.dealer_revealing and not self.dealer_done:
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
                    self.end_game()

    def end_game(self):
        if not self.dealer_done:
            dealer_score = self.dealer_hand.calculate_score()
            dealer_busted = self.dealer_hand.is_bust()
            
            total_winnings = 0
            results = []
            
            for i, hand in enumerate(self.player_hands):
                player_score = hand.calculate_score()
                hand_result = ""
                winnings = 0
                
                if hand.busted:
                    hand_result = "Bust"
                    # No winnings, bet already lost
                elif hand.blackjack and not self.dealer_hand.is_blackjack():
                    hand_result = "Blackjack!"
                    winnings = int(hand.bet * 2.5)  # 3:2 payout
                elif dealer_busted:
                    hand_result = "Win (Dealer Bust)"
                    winnings = hand.bet * 2
                elif dealer_score > player_score:
                    hand_result = "Lose"
                    # No winnings
                elif dealer_score < player_score:
                    hand_result = "Win"
                    winnings = hand.bet * 2
                else:
                    hand_result = "Push"
                    winnings = hand.bet  # Return bet
                
                total_winnings += winnings
                results.append(f"Hand {i+1}: {hand_result}")
            
            self.bankroll += total_winnings
            
            # Create message
            if len(self.player_hands) == 1:
                self.message = results[0].replace("Hand 1: ", "")
            else:
                self.message = " | ".join(results)
            
            self.game_over = True
            self.dealer_done = True
            self.round_complete = True

    def new_round(self):
        if len(self.deck.cards) < 20:  # Reshuffle when deck is low
            self.deck = Deck()
        
        self.player_hands = []
        self.dealer_hand = Hand()
        self.current_hand_index = 0
        self.current_bet = 0
        self.betting_phase = True
        self.game_over = False
        self.message = ""
        self.dealer_revealing = False
        self.dealer_card_revealed = False
        self.dealer_done = False
        self.round_complete = False
        self.split_count = 0
        self.update_betting_buttons()

    def update_action_buttons(self):
        current_hand = self.get_current_hand()
        playing = not self.game_over and not self.dealer_revealing and not self.betting_phase
        
        if playing and current_hand and not current_hand.finished:
            self.hit_button.set_enabled(True)
            self.stand_button.set_enabled(True)
            self.double_button.set_enabled(self.can_double_down())
            self.split_button.set_enabled(self.can_split())
        else:
            self.hit_button.set_enabled(False)
            self.stand_button.set_enabled(False)
            self.double_button.set_enabled(False)
            self.split_button.set_enabled(False)

    def draw_game(self):
        # Draw background
        screen.fill(GREEN)
        
        # Draw bankroll and current bet
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        bankroll_text = font.render(f"Bankroll: ${self.bankroll}", True, WHITE)
        bet_text = font.render(f"Current Bet: ${self.current_bet}", True, WHITE)
        screen.blit(bankroll_text, (WINDOW_WIDTH - 200, 20))
        screen.blit(bet_text, (WINDOW_WIDTH - 200, 60))
        
        if self.betting_phase and self.current_bet == 0:
            # Show betting instructions
            instruction_text = font.render("Place your bet and click Deal Cards!", True, WHITE)
            instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH//2, 300))
            screen.blit(instruction_text, instruction_rect)
        elif not self.betting_phase:
            # Draw dealer's cards
            for i, card in enumerate(self.dealer_hand.cards):
                if i == 0 and not self.dealer_card_revealed:
                    # Draw card back for dealer's hidden card
                    pygame.draw.rect(screen, RED, (50 + i * (CARD_WIDTH + 10), 50, CARD_WIDTH, CARD_HEIGHT))
                else:
                    screen.blit(card.image, (50 + i * (CARD_WIDTH + 10), 50))

            # Draw player's hands with proper spacing
            num_hands = len(self.player_hands)
            
            if num_hands == 1:
                # Single hand - center it
                hand = self.player_hands[0]
                x_pos = 50
                y_pos = WINDOW_HEIGHT - 320
                
                # Highlight current hand
                if not hand.finished and not self.dealer_revealing:
                    pygame.draw.rect(screen, BLUE, (x_pos - 10, y_pos - 10, 
                                   len(hand.cards) * (CARD_WIDTH + 10) + 20, CARD_HEIGHT + 40), 3)
                
                # Draw cards
                for i, card in enumerate(hand.cards):
                    screen.blit(card.image, (x_pos + i * (CARD_WIDTH + 10), y_pos))
                
                # Draw hand info
                hand_score = hand.calculate_score()
                status = ""
                if hand.busted:
                    status = " (BUST)"
                elif hand.blackjack:
                    status = " (BLACKJACK)"
                elif hand.finished:
                    status = " (STAND)"
                elif hand.doubled:
                    status = " (DOUBLED)"
                
                hand_text = small_font.render(f"Score: {hand_score}{status} | Bet: ${hand.bet}", True, WHITE)
                screen.blit(hand_text, (x_pos, y_pos + CARD_HEIGHT + 5))
            
            else:
                # Multiple hands - arrange horizontally
                total_width = WINDOW_WIDTH - 100  # Leave margins
                hand_width = total_width // num_hands
                
                for hand_idx, hand in enumerate(self.player_hands):
                    x_pos = 50 + hand_idx * hand_width
                    y_pos = WINDOW_HEIGHT - 320
                    
                    # Highlight current hand
                    if hand_idx == self.current_hand_index and not hand.finished and not self.dealer_revealing:
                        pygame.draw.rect(screen, BLUE, (x_pos - 10, y_pos - 10, 
                                       min(len(hand.cards) * (CARD_WIDTH + 10) + 20, hand_width), 
                                       CARD_HEIGHT + 60), 3)
                    
                    # Draw cards (limit spacing if too many hands)
                    card_spacing = min(CARD_WIDTH + 10, (hand_width - 20) // max(len(hand.cards), 1))
                    for i, card in enumerate(hand.cards):
                        card_x = x_pos + i * card_spacing
                        # Ensure cards don't go beyond hand boundary
                        if card_x + CARD_WIDTH <= x_pos + hand_width - 20:
                            screen.blit(card.image, (card_x, y_pos))
                    
                    # Draw hand info
                    hand_score = hand.calculate_score()
                    status = ""
                    if hand.busted:
                        status = " (BUST)"
                    elif hand.blackjack:
                        status = " (BJ)"
                    elif hand.finished:
                        status = " (STAND)"
                    elif hand.doubled:
                        status = " (2X)"
                    
                    # Use shorter text for multiple hands
                    hand_text = small_font.render(f"H{hand_idx + 1}: {hand_score}{status}", True, WHITE)
                    bet_text = small_font.render(f"${hand.bet}", True, WHITE)
                    screen.blit(hand_text, (x_pos, y_pos + CARD_HEIGHT + 5))
                    screen.blit(bet_text, (x_pos, y_pos + CARD_HEIGHT + 25))

            # Draw dealer score
            dealer_score = self.dealer_hand.calculate_score() if self.dealer_card_revealed else "?"
            dealer_text = font.render(f"Dealer: {dealer_score}", True, WHITE)
            screen.blit(dealer_text, (50, 20))

            # Show current hand indicator
            if not self.dealer_revealing and self.current_hand_index < len(self.player_hands):
                current_hand_text = small_font.render(f"Playing Hand {self.current_hand_index + 1}", True, WHITE)
                screen.blit(current_hand_text, (WINDOW_WIDTH - 200, 100))

        # Draw message
        if self.message:
            # Handle long messages
            if len(self.message) > 40:
                words = self.message.split(" | ")
                for i, word in enumerate(words):
                    message_text = small_font.render(word, True, WHITE)
                    message_rect = message_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50 + i * 25))
                    screen.blit(message_text, message_rect)
            else:
                message_text = font.render(self.message, True, WHITE)
                message_rect = message_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
                screen.blit(message_text, message_rect)

        # Update and draw buttons based on game state
        if self.betting_phase:
            # Draw betting buttons
            self.bet_5_button.draw(screen)
            self.bet_10_button.draw(screen)
            self.bet_25_button.draw(screen)
            self.bet_50_button.draw(screen)
            self.bet_100_button.draw(screen)
            
            if self.current_bet > 0:
                self.deal_button.draw(screen)
        elif not self.game_over and not self.dealer_revealing:
            # Update and draw game action buttons
            self.update_action_buttons()
            self.hit_button.draw(screen)
            self.stand_button.draw(screen)
            self.double_button.draw(screen)
            self.split_button.draw(screen)
        elif self.round_complete:
            # Draw play again button
            self.play_again_button.draw(screen)
            
        # Check for game over (no money left)
        if self.bankroll == 0 and self.current_bet == 0 and self.betting_phase:
            game_over_text = font.render("Game Over! No money left!", True, RED)
            game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(game_over_text, game_over_rect)

        pygame.display.flip()

def main():
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if game.betting_phase:
                    # Handle betting buttons
                    if game.bet_5_button.is_clicked(mouse_pos):
                        game.place_bet(5)
                    elif game.bet_10_button.is_clicked(mouse_pos):
                        game.place_bet(10)
                    elif game.bet_25_button.is_clicked(mouse_pos):
                        game.place_bet(25)
                    elif game.bet_50_button.is_clicked(mouse_pos):
                        game.place_bet(50)
                    elif game.bet_100_button.is_clicked(mouse_pos):
                        game.place_bet(100)
                    elif game.deal_button.is_clicked(mouse_pos) and game.current_bet > 0:
                        game.deal_initial_cards()
                elif not game.game_over and not game.dealer_revealing:
                    # Handle game action buttons
                    if game.hit_button.is_clicked(mouse_pos):
                        game.hit()
                    elif game.stand_button.is_clicked(mouse_pos):
                        game.stand()
                    elif game.double_button.is_clicked(mouse_pos):
                        game.double_down()
                    elif game.split_button.is_clicked(mouse_pos):
                        game.split_hand()
                elif game.round_complete:
                    # Handle play again button
                    if game.play_again_button.is_clicked(mouse_pos):
                        game.new_round()

        game.update_dealer()
        game.draw_game()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
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
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = []
        self.dealer_hand = []
        self.game_over = False
        self.message = ""
        self.dealer_revealing = False
        self.last_dealer_action_time = 0
        self.dealer_card_revealed = False
        self.dealer_done = False
        
        # Create buttons
        self.hit_button = Button(WINDOW_WIDTH//2 - 220, WINDOW_HEIGHT - 100, 
                               BUTTON_WIDTH, BUTTON_HEIGHT, "Hit", WHITE)
        self.stand_button = Button(WINDOW_WIDTH//2 + 20, WINDOW_HEIGHT - 100, 
                                 BUTTON_WIDTH, BUTTON_HEIGHT, "Stand", WHITE)
        self.play_again_button = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2, 
                                      BUTTON_WIDTH, BUTTON_HEIGHT, "Play Again", WHITE)
        
        self.deal_initial_cards()

    def deal_initial_cards(self):
        self.player_hand = [self.deck.draw(), self.deck.draw()]
        self.dealer_hand = [self.deck.draw(), self.deck.draw()]
        self.game_over = False
        self.message = ""
        self.dealer_revealing = False
        self.last_dealer_action_time = 0
        self.dealer_card_revealed = False
        self.dealer_done = False

    def calculate_score(self, hand: List[Card]) -> int:
        score = 0
        aces = 0
        
        for card in hand:
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

    def hit(self):
        if not self.game_over and not self.dealer_revealing:
            self.player_hand.append(self.deck.draw())
            if self.calculate_score(self.player_hand) > 21:
                self.game_over = True
                self.message = "Bust! Dealer wins!"
                self.dealer_card_revealed = True
                self.dealer_done = True

    def stand(self):
        if not self.game_over and not self.dealer_revealing:
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
                dealer_score = self.calculate_score(self.dealer_hand)
                if dealer_score < 17:
                    if current_time - self.last_dealer_action_time >= DEALER_PLAY_DELAY:
                        self.dealer_hand.append(self.deck.draw())
                        self.last_dealer_action_time = current_time
                else:
                    self.end_game()

    def end_game(self):
        if not self.dealer_done:
            player_score = self.calculate_score(self.player_hand)
            dealer_score = self.calculate_score(self.dealer_hand)
            
            if dealer_score > 21:
                self.message = "Dealer busts! You win!"
            elif dealer_score > player_score:
                self.message = "Dealer wins!"
            elif dealer_score < player_score:
                self.message = "You win!"
            else:
                self.message = "Push!"
            
            self.game_over = True
            self.dealer_done = True

    def draw_game(self):
        # Draw background
        screen.fill(GREEN)
        
        # Draw dealer's cards
        for i, card in enumerate(self.dealer_hand):
            if i == 0 and not self.dealer_card_revealed:
                # Draw card back for dealer's hidden card
                pygame.draw.rect(screen, RED, (50 + i * (CARD_WIDTH + 10), 50, CARD_WIDTH, CARD_HEIGHT))
            else:
                screen.blit(card.image, (50 + i * (CARD_WIDTH + 10), 50))

        # Draw player's cards
        for i, card in enumerate(self.player_hand):
            screen.blit(card.image, (50 + i * (CARD_WIDTH + 10), WINDOW_HEIGHT - 250))

        # Draw scores
        font = pygame.font.Font(None, 36)
        player_score = self.calculate_score(self.player_hand)
        dealer_score = self.calculate_score(self.dealer_hand) if self.dealer_card_revealed else "?"
        
        dealer_text = font.render(f"Dealer: {dealer_score}", True, WHITE)
        player_text = font.render(f"Player: {player_score}", True, WHITE)
        screen.blit(dealer_text, (50, 20))
        screen.blit(player_text, (50, WINDOW_HEIGHT - 280))

        # Draw message
        if self.message:
            message_text = font.render(self.message, True, WHITE)
            message_rect = message_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
            screen.blit(message_text, message_rect)

        # Draw buttons
        if not self.game_over and not self.dealer_revealing:
            self.hit_button.draw(screen)
            self.stand_button.draw(screen)
        elif self.game_over:
            self.play_again_button.draw(screen)

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
                
                if not game.game_over and not game.dealer_revealing:
                    if game.hit_button.is_clicked(mouse_pos):
                        game.hit()
                    elif game.stand_button.is_clicked(mouse_pos):
                        game.stand()
                elif game.game_over:
                    if game.play_again_button.is_clicked(mouse_pos):
                        game = Game()

        game.update_dealer()
        game.draw_game()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main() 
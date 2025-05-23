"""
Game constants and configuration settings.
"""

# Window settings
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60

# Card settings
CARD_WIDTH = 100
CARD_HEIGHT = 145

# Button settings
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50

# Game settings
DEALER_PLAY_DELAY = 1.0  # Seconds between dealer actions
STARTING_BANKROLL = 1000
MAX_SPLIT_HANDS = 4
DECK_RESHUFFLE_THRESHOLD = 20

# Colors (RGB tuples)
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GOLD = (255, 215, 0)
GRAY = (128, 128, 128)
BLUE = (100, 150, 255)

# Card suits and values
SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
VALUES = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']
FACE_CARDS = ['jack', 'queen', 'king']
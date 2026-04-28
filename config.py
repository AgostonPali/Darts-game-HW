# config.py
import math

# Képernyő beállítások
WIDTH, HEIGHT = 800, 800
FPS = 60

# Modern Színpaletta
DARK_BG = (26, 26, 46)       # Sötétkék/lila modern háttér
BOARD_BG = (22, 33, 62)      # A tábla mögötti fal színe
WHITE = (240, 240, 245)
BLACK = (15, 15, 20)
RED = (233, 69, 96)          # Modern, élénkebb piros
GREEN = (42, 157, 143)       # Pasztellesebb, modern zöld
BEIGE = (241, 250, 238)
GRAY = (140, 140, 150)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)

# Céltábla méretei
BOARD_CENTER = (WIDTH // 2, HEIGHT // 2 - 80) # Kicsit feljebb toljuk a UI miatt
PIXELS_PER_METER = 800  
R_BULL_INNER = int(0.00635 * PIXELS_PER_METER)
R_BULL_OUTER = int(0.0159 * PIXELS_PER_METER)
R_TRIPLE_INNER = int(0.099 * PIXELS_PER_METER)
R_TRIPLE_OUTER = int(0.107 * PIXELS_PER_METER)
R_DOUBLE_INNER = int(0.162 * PIXELS_PER_METER)
R_DOUBLE_OUTER = int(0.170 * PIXELS_PER_METER)
R_BOARD = int(0.226 * PIXELS_PER_METER)

# Darts szektorok
SECTORS = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
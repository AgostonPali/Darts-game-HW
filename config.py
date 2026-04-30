# config.py
import math

# Belső logikai felbontás (A fullscreen ehhez képest skálázódik)
WIDTH, HEIGHT = 800, 800
FPS = 60

# Modern Színpaletta
DARK_BG = (26, 26, 46)       
BOARD_BG = (22, 33, 62)      
WHITE = (240, 240, 245)
BLACK = (15, 15, 20)
RED = (233, 69, 96)          
GREEN = (42, 157, 143)       
BEIGE = (241, 250, 238)
GRAY = (140, 140, 150)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)

# Céltábla méretei és nagyítása
PIXELS_PER_METER = 1000  # A korábbi 800 helyett, így a tábla láthatóan nagyobb lett
BOARD_CENTER = (WIDTH // 2, HEIGHT // 2 - 60)

R_BULL_INNER = int(0.00635 * PIXELS_PER_METER)
R_BULL_OUTER = int(0.0159 * PIXELS_PER_METER)
R_TRIPLE_INNER = int(0.099 * PIXELS_PER_METER)
R_TRIPLE_OUTER = int(0.107 * PIXELS_PER_METER)
R_DOUBLE_INNER = int(0.162 * PIXELS_PER_METER)
R_DOUBLE_OUTER = int(0.170 * PIXELS_PER_METER)
R_BOARD = int(0.226 * PIXELS_PER_METER)

# Darts szektorok
SECTORS = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
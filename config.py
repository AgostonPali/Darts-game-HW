# config.py
import math

WIDTH, HEIGHT = 800, 800
FPS = 60

DARK_BG_CENTER = (40, 45, 65)
DARK_BG_EDGE = (10, 10, 15)
BOARD_BG = (22, 33, 62, 180) 
WHITE = (240, 240, 245)
BLACK = (15, 15, 20)
SHADOW = (0, 0, 0, 60) 
RED = (220, 40, 60)          
GREEN = (30, 140, 100)       
BEIGE = (245, 240, 210)
GRAY = (140, 140, 150)
GOLD = (255, 215, 0)
SILVER = (210, 210, 220)
WIRE_COLOR = (180, 180, 190)

BOARD_CENTER = (WIDTH // 2, HEIGHT // 2 - 40)
SECTORS = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]

class BoardConfig:
    DISTANCE = 2.37
    PIXELS_PER_METER = 1150
    R_BULL_INNER = 0
    R_BULL_OUTER = 0
    R_TRIPLE_INNER = 0
    R_TRIPLE_OUTER = 0
    R_DOUBLE_INNER = 0
    R_DOUBLE_OUTER = 0
    R_BOARD = 0

    @classmethod
    def set_distance(cls, meters):
        cls.DISTANCE = meters
        cls.PIXELS_PER_METER = int(1150 * (2.37 / meters))
        cls.R_BULL_INNER = int(0.00635 * cls.PIXELS_PER_METER)
        cls.R_BULL_OUTER = int(0.0159 * cls.PIXELS_PER_METER)
        cls.R_TRIPLE_INNER = int(0.099 * cls.PIXELS_PER_METER)
        cls.R_TRIPLE_OUTER = int(0.107 * cls.PIXELS_PER_METER)
        cls.R_DOUBLE_INNER = int(0.162 * cls.PIXELS_PER_METER)
        cls.R_DOUBLE_OUTER = int(0.170 * cls.PIXELS_PER_METER)
        cls.R_BOARD = int(0.190 * cls.PIXELS_PER_METER)

# Inicializálás standard távolsággal
BoardConfig.set_distance(2.37)
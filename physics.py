# physics.py
from config import *

def calculate_impact(aim_x, power_percent):
    """
    A célzott X koordináta megmarad.
    Az Y koordinátát a dobás erőssége (power_percent: 0.0 - 1.0) határozza meg.
    Tökéletes erősség (pl. 0.75) esetén pont a tábla magasságába (Y közepére) megy.
    """
    ideal_power = 0.75
    
    # Mennyivel tért el a tökéletes erőtől?
    power_diff = ideal_power - power_percent
    
    # 10% eltérés az erőben = 120 pixel eltérés függőlegesen
    # Ha gyengébb (power_diff pozitív), a nyíl lefelé esik (+Y irány a képernyőn)
    # Ha erősebb (power_diff negatív), a nyíl feljebb megy (-Y irány)
    hit_y = BOARD_CENTER[1] + (power_diff * 1200)
    
    return int(aim_x), int(hit_y)
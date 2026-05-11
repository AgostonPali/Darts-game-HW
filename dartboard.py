# dartboard.py
import pygame
import math
from config import *

def draw_board(surface, font):
    bc = BoardConfig
    shadow_surf = pygame.Surface((bc.R_BOARD*2 + 40, bc.R_BOARD*2 + 40), pygame.SRCALPHA)
    pygame.draw.circle(shadow_surf, SHADOW, (bc.R_BOARD + 20, bc.R_BOARD + 20), bc.R_BOARD + 10)
    surface.blit(shadow_surf, (BOARD_CENTER[0] - bc.R_BOARD - 15, BOARD_CENTER[1] - bc.R_BOARD - 5))

    pygame.draw.circle(surface, BLACK, BOARD_CENTER, bc.R_BOARD)
    
    angle_step = 360 / 20
    for i, sector in enumerate(SECTORS):
        start_angle = math.radians(90 - (i * angle_step) + (angle_step / 2))
        end_angle = math.radians(90 - ((i+1) * angle_step) + (angle_step / 2))
        
        color1 = BLACK if i % 2 == 0 else BEIGE
        color2 = RED if i % 2 == 0 else GREEN
        
        draw_pie_slice(surface, BOARD_CENTER, bc.R_DOUBLE_INNER, start_angle, end_angle, color1)
        draw_pie_slice(surface, BOARD_CENTER, bc.R_DOUBLE_OUTER, start_angle, end_angle, color2, bc.R_DOUBLE_INNER)
        draw_pie_slice(surface, BOARD_CENTER, bc.R_TRIPLE_INNER, start_angle, end_angle, color1)
        draw_pie_slice(surface, BOARD_CENTER, bc.R_TRIPLE_OUTER, start_angle, end_angle, color2, bc.R_TRIPLE_INNER)
        
        text_angle = math.radians(90 - (i * angle_step))
        text_r = bc.R_BOARD - max(5, int(11 * (2.37 / bc.DISTANCE))) 
        tx = BOARD_CENTER[0] + text_r * math.cos(text_angle)
        ty = BOARD_CENTER[1] - text_r * math.sin(text_angle)
        
        scaled_font = pygame.font.SysFont("Segoe UI, Arial", max(10, int(22 * (2.37 / bc.DISTANCE))), bold=True)
        text_surf = scaled_font.render(str(sector), True, WHITE)
        text_rect = text_surf.get_rect(center=(tx, ty))
        surface.blit(text_surf, text_rect)

        line_angle = start_angle
        lx1 = BOARD_CENTER[0] + bc.R_BULL_OUTER * math.cos(line_angle)
        ly1 = BOARD_CENTER[1] - bc.R_BULL_OUTER * math.sin(line_angle)
        lx2 = BOARD_CENTER[0] + bc.R_DOUBLE_OUTER * math.cos(line_angle)
        ly2 = BOARD_CENTER[1] - bc.R_DOUBLE_OUTER * math.sin(line_angle)
        pygame.draw.line(surface, WIRE_COLOR, (lx1, ly1), (lx2, ly2), 2)

    pygame.draw.circle(surface, WIRE_COLOR, BOARD_CENTER, bc.R_DOUBLE_OUTER, 2)
    pygame.draw.circle(surface, WIRE_COLOR, BOARD_CENTER, bc.R_DOUBLE_INNER, 2)
    pygame.draw.circle(surface, WIRE_COLOR, BOARD_CENTER, bc.R_TRIPLE_OUTER, 2)
    pygame.draw.circle(surface, WIRE_COLOR, BOARD_CENTER, bc.R_TRIPLE_INNER, 2)
    
    pygame.draw.circle(surface, GREEN, BOARD_CENTER, bc.R_BULL_OUTER)
    pygame.draw.circle(surface, WIRE_COLOR, BOARD_CENTER, bc.R_BULL_OUTER, 2)
    pygame.draw.circle(surface, RED, BOARD_CENTER, bc.R_BULL_INNER)
    pygame.draw.circle(surface, WIRE_COLOR, BOARD_CENTER, bc.R_BULL_INNER, 2)

def draw_pie_slice(surface, center, radius, start_angle, end_angle, color, inner_radius=0):
    points = [center] if inner_radius == 0 else []
    steps = 15 
    for i in range(steps + 1):
        angle = start_angle + (end_angle - start_angle) * i / steps
        x = center[0] + radius * math.cos(angle)
        y = center[1] - radius * math.sin(angle)
        points.append((x, y))
        
    if inner_radius > 0:
        for i in range(steps, -1, -1):
            angle = start_angle + (end_angle - start_angle) * i / steps
            x = center[0] + inner_radius * math.cos(angle)
            y = center[1] - inner_radius * math.sin(angle)
            points.append((x, y))
            
    if len(points) > 2:
        pygame.draw.polygon(surface, color, points)

def get_score(x, y):
    bc = BoardConfig
    dx = x - BOARD_CENTER[0]
    dy = BOARD_CENTER[1] - y 
    dist = math.sqrt(dx**2 + dy**2)
    
    if dist <= bc.R_BULL_INNER: return 50
    if dist <= bc.R_BULL_OUTER: return 25
    
    # A külső dupla dróton túli terület szigorúan 0 pontot ér
    if dist > bc.R_DOUBLE_OUTER: return 0
    
    angle_deg = math.degrees(math.atan2(dy, dx))
    adjusted_angle = (90 - angle_deg) % 360
    sector_idx = int(((adjusted_angle + 9) % 360) // 18)
    base_score = SECTORS[sector_idx]
    
    if bc.R_TRIPLE_INNER < dist <= bc.R_TRIPLE_OUTER: return base_score * 3
    if bc.R_DOUBLE_INNER < dist <= bc.R_DOUBLE_OUTER: return base_score * 2
    return base_score
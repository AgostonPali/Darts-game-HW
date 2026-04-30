# main.py
import pygame
import sys
import random
import math
from config import *
import dartboard

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
virtual_surface = pygame.Surface((WIDTH, HEIGHT)) 
pygame.display.set_caption("Darts Simulator Pro")
clock = pygame.time.Clock()
is_fullscreen = False

font = pygame.font.SysFont("Segoe UI, Arial", 22, bold=True)
small_font = pygame.font.SysFont("Segoe UI, Arial", 16, bold=True)
title_font = pygame.font.SysFont("Segoe UI, Arial", 56, bold=True)
score_font = pygame.font.SysFont("Segoe UI, Arial", 42, bold=True)

class GameState:
    MENU = 0
    PLAYING = 1
    WAITING_FOR_NEXT_TURN = 2
    GAMEOVER = 3

state = GameState.MENU
player_score = 301
pc_score = 301
player_start_score = 301
pc_start_score = 301
current_turn = "PLAYER" 
darts_thrown = 0
darts_on_board = [] 
turn_scores = [] 

action_phase = "AIM_X" 
aim_x_val = BOARD_CENTER[0]
aim_x_dir = 1
aim_y_val = BOARD_CENTER[1]
aim_y_dir = 1
flying_dart = None 
timer = 0 

def get_scaled_mouse_pos():
    mx, my = pygame.mouse.get_pos()
    sw, sh = screen.get_size()
    scale = min(sw / WIDTH, sh / HEIGHT)
    new_w = int(WIDTH * scale)
    new_h = int(HEIGHT * scale)
    offset_x = (sw - new_w) // 2
    offset_y = (sh - new_h) // 2
    
    virtual_x = (mx - offset_x) / scale
    virtual_y = (my - offset_y) / scale
    return (virtual_x, virtual_y)

def reset_turn_data():
    global darts_thrown, darts_on_board, action_phase, aim_x_val, aim_y_val, turn_scores
    darts_thrown = 0
    darts_on_board.clear()
    turn_scores.clear()
    action_phase = "AIM_X"
    aim_x_val = BOARD_CENTER[0]
    aim_y_val = BOARD_CENTER[1]

def start_flight(is_pc=False):
    global action_phase, flying_dart
    action_phase = "FLYING"
    
    start_pos = (WIDTH//2, HEIGHT)
    target_pos = (aim_x_val, aim_y_val)
    flight_angle = math.degrees(math.atan2(target_pos[1] - start_pos[1], target_pos[0] - start_pos[0])) + 90
    
    flying_dart = {
        "pos": start_pos,
        "target": target_pos,
        "progress": 0.0,
        "is_pc": is_pc
    }

def draw_modern_dart(surface, x, y, angle_deg, scale):
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    
    def transform(px, py):
        rx = px * cos_a - py * sin_a
        ry = px * sin_a + py * cos_a
        return (x + rx * scale, y + ry * scale)

    pygame.draw.polygon(surface, SILVER, [transform(0,0), transform(4, 12), transform(-4, 12)])
    pygame.draw.polygon(surface, (200, 160, 50), [transform(4, 12), transform(5, 40), transform(-5, 40), transform(-4, 12)])
    pygame.draw.line(surface, (30, 30, 30), transform(0, 40), transform(0, 75), max(1, int(4*scale)))
    f_pts = [transform(0, 70), transform(15, 95), transform(15, 105), transform(0, 95), 
             transform(-15, 105), transform(-15, 95)]
    pygame.draw.polygon(surface, RED, f_pts)

def draw_ui(surface):
    pygame.draw.rect(surface, BOARD_BG, (10, 10, 220, 120), border_radius=12)
    pygame.draw.rect(surface, BOARD_BG, (WIDTH - 230, 10, 220, 120), border_radius=12)
    
    surface.blit(font.render("PLAYER", True, GRAY), (25, 15))
    surface.blit(score_font.render(str(player_score), True, WHITE), (25, 35))
    
    pc_lbl = font.render("COMPUTER", True, GRAY)
    surface.blit(pc_lbl, (WIDTH - 25 - pc_lbl.get_width(), 15))
    pc_scr = score_font.render(str(pc_score), True, WHITE)
    surface.blit(pc_scr, (WIDTH - 25 - pc_scr.get_width(), 35))
    
    score_str = " + ".join([str(s) for s in turn_scores])
    score_surf = small_font.render(score_str, True, GOLD)
    if current_turn == "PLAYER":
        surface.blit(score_surf, (25, 90))
    else:
        surface.blit(score_surf, (WIDTH - 25 - score_surf.get_width(), 90))

    turn_text = font.render("PLAYER'S TURN" if current_turn == "PLAYER" else "COMPUTER'S TURN", 
                            True, RED if current_turn == "PLAYER" else GREEN)
    surface.blit(turn_text, (WIDTH//2 - turn_text.get_width()//2, 20))
    
    for i in range(3 - darts_thrown):
        draw_modern_dart(surface, 40 + i*35, HEIGHT - 70, 0, 0.6)

def main():
    global state, aim_x_val, aim_x_dir, aim_y_val, aim_y_dir, action_phase
    global darts_thrown, player_score, pc_score, flying_dart, current_turn, timer, turn_scores, is_fullscreen, screen
    global player_start_score, pc_start_score

    btn_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT//2, 240, 60)
    restart_btn_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 20, 240, 60)

    while True:
        virtual_surface.fill(DARK_BG)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

            if state == GameState.MENU and event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = get_scaled_mouse_pos()
                if btn_rect.collidepoint((mx, my)) or is_fullscreen:
                    state = GameState.PLAYING
                    player_score = 301
                    pc_score = 301
                    player_start_score = 301
                    pc_start_score = 301
                    current_turn = "PLAYER"
                    reset_turn_data()
                    
            elif state == GameState.GAMEOVER and event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = get_scaled_mouse_pos()
                if restart_btn_rect.collidepoint((mx, my)):
                    state = GameState.PLAYING
                    player_score = 301
                    pc_score = 301
                    player_start_score = 301
                    pc_start_score = 301
                    current_turn = "PLAYER"
                    reset_turn_data()

            elif state == GameState.PLAYING and current_turn == "PLAYER":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if action_phase == "AIM_X":
                        action_phase = "AIM_Y"
                        aim_y_val = BOARD_CENTER[1] + R_BOARD 
                        aim_y_dir = -1
                    elif action_phase == "AIM_Y":
                        start_flight(is_pc=False)

        if state == GameState.MENU:
            title = title_font.render("DARTS PRO 301", True, WHITE)
            virtual_surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            
            pygame.draw.rect(virtual_surface, RED, btn_rect, border_radius=30)
            btn_txt = font.render("START GAME", True, WHITE)
            virtual_surface.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width()//2, btn_rect.centery - btn_txt.get_height()//2))
            
            help_txt = small_font.render("Press F11 for Fullscreen", True, GRAY)
            virtual_surface.blit(help_txt, (WIDTH//2 - help_txt.get_width()//2, HEIGHT - 50))
            
        elif state == GameState.PLAYING or state == GameState.WAITING_FOR_NEXT_TURN:
            dartboard.draw_board(virtual_surface, font)
            
            for x, y, _ in darts_on_board:
                draw_modern_dart(virtual_surface, x, y, 0, 0.4)
            draw_ui(virtual_surface)

            if state == GameState.PLAYING:
                if current_turn == "PLAYER":
                    if action_phase == "AIM_X":
                        dist = abs(aim_x_val - BOARD_CENTER[0])
                        speed_mult = 1.0 + (1.0 - min(1.0, dist / 200.0)) * 1.2
                        aim_x_val += (3.5 * speed_mult) * aim_x_dir
                        if aim_x_val > BOARD_CENTER[0] + 200 or aim_x_val < BOARD_CENTER[0] - 200:
                            aim_x_dir *= -1
                    
                    elif action_phase == "AIM_Y":
                        dist_y = abs(aim_y_val - BOARD_CENTER[1])
                        speed_mult_y = 1.0 + (1.0 - min(1.0, dist_y / float(R_BOARD))) * 1.2
                        aim_y_val += (3.5 * (R_BOARD / 200.0) * speed_mult_y) * aim_y_dir
                        
                        if aim_y_val > BOARD_CENTER[1] + R_BOARD + 10 or aim_y_val < BOARD_CENTER[1] - R_BOARD - 10:
                            aim_y_dir *= -1
                    
                    if action_phase in ["AIM_X", "AIM_Y"]:
                        s_x = WIDTH//2 - 200
                        pygame.draw.rect(virtual_surface, BLACK, (s_x, HEIGHT-100, 400, 10), border_radius=5)
                        pygame.draw.circle(virtual_surface, GOLD if action_phase=="AIM_X" else GRAY, 
                                           (int(max(s_x, min(aim_x_val, s_x+400))), HEIGHT-95), 10)
                        
                        if action_phase == "AIM_Y":
                            pygame.draw.circle(virtual_surface, GOLD, (int(aim_x_val), int(aim_y_val)), 6, 2)

                            p_width = 16
                            p_height = R_BOARD * 2 + 20
                            p_x = WIDTH - 60
                            p_y = BOARD_CENTER[1] - R_BOARD - 10
                            
                            pygame.draw.rect(virtual_surface, BLACK, (p_x, p_y, p_width, p_height), border_radius=8)
                            
                            pygame.draw.line(virtual_surface, GREEN, (p_x - 10, BOARD_CENTER[1]), (p_x + p_width + 10, BOARD_CENTER[1]), 3)
                            virtual_surface.blit(small_font.render("BULL", True, GREEN), (p_x + p_width + 12, BOARD_CENTER[1] - 8))
                            
                            t20_y = BOARD_CENTER[1] - (R_TRIPLE_INNER + R_TRIPLE_OUTER) / 2
                            pygame.draw.line(virtual_surface, GOLD, (p_x - 10, t20_y), (p_x + p_width + 10, t20_y), 3)
                            virtual_surface.blit(small_font.render("T20", True, GOLD), (p_x + p_width + 12, t20_y - 8))
                            
                            pygame.draw.circle(virtual_surface, RED, (p_x + p_width//2, int(aim_y_val)), 8)
                
                elif current_turn == "COMPUTER" and action_phase != "FLYING":
                    timer += 1
                    if timer > 60:
                        aim_x_val = BOARD_CENTER[0] + random.randint(-35, 35)
                        aim_y_val = BOARD_CENTER[1] - (R_TRIPLE_INNER + R_TRIPLE_OUTER)/2 + random.randint(-35, 35)
                        start_flight(is_pc=True)
                        timer = 0

                if action_phase == "FLYING":
                    fd = flying_dart
                    fd["progress"] += 0.035
                    t = fd["progress"]
                    
                    distance_from_bottom = HEIGHT - fd["target"][1]
                    arc = distance_from_bottom * 0.4
                    
                    curr_x = fd["pos"][0] + (fd["target"][0] - fd["pos"][0]) * t
                    curr_y = fd["pos"][1] + (fd["target"][1] - fd["pos"][1]) * t - arc * math.sin(math.pi * t)
                    
                    dt = 0.01
                    next_y = fd["pos"][1] + (fd["target"][1] - fd["pos"][1]) * (t+dt) - arc * math.sin(math.pi * (t+dt))
                    next_x = fd["pos"][0] + (fd["target"][0] - fd["pos"][0]) * (t+dt)
                    angle = math.degrees(math.atan2(next_y - curr_y, next_x - curr_x)) + 90
                    
                    draw_modern_dart(virtual_surface, curr_x, curr_y, angle, 1.5 - t)

                    if t >= 1.0:
                        score = dartboard.get_score(fd["target"][0], fd["target"][1])
                        turn_scores.append(score)
                        darts_on_board.append((fd["target"][0], fd["target"][1], fd["is_pc"]))
                        darts_thrown += 1

                        # Túldobás (Bust) logika alkalmazása
                        if fd["is_pc"]: 
                            if pc_score - score < 0:
                                pc_score = pc_start_score
                                darts_thrown = 3
                            else:
                                pc_score -= score
                        else: 
                            if player_score - score < 0:
                                player_score = player_start_score
                                darts_thrown = 3
                            else:
                                player_score -= score
                        
                        if player_score == 0 or pc_score == 0: 
                            state = GameState.GAMEOVER
                        elif darts_thrown >= 3:
                            state = GameState.WAITING_FOR_NEXT_TURN
                            timer = 0
                        else:
                            action_phase = "AIM_X"
            
            if state == GameState.WAITING_FOR_NEXT_TURN:
                timer += 1
                if timer > 90:
                    current_turn = "COMPUTER" if current_turn == "PLAYER" else "PLAYER"
                    reset_turn_data()
                    player_start_score = player_score
                    pc_start_score = pc_score
                    state = GameState.PLAYING
                    timer = 0

        elif state == GameState.GAMEOVER:
            msg = "PLAYER WINS!" if player_score == 0 else "COMPUTER WINS!"
            txt = title_font.render(msg, True, GREEN)
            virtual_surface.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 60))
            
            pygame.draw.rect(virtual_surface, RED, restart_btn_rect, border_radius=30)
            btn_txt = font.render("NEW GAME", True, WHITE)
            virtual_surface.blit(btn_txt, (restart_btn_rect.centerx - btn_txt.get_width()//2, restart_btn_rect.centery - btn_txt.get_height()//2))

        sw, sh = screen.get_size()
        scale = min(sw / WIDTH, sh / HEIGHT)
        new_w = int(WIDTH * scale)
        new_h = int(HEIGHT * scale)
        
        scaled_surface = pygame.transform.smoothscale(virtual_surface, (new_w, new_h))
        
        offset_x = (sw - new_w) // 2
        offset_y = (sh - new_h) // 2
        
        screen.fill(BLACK) 
        screen.blit(scaled_surface, (offset_x, offset_y))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
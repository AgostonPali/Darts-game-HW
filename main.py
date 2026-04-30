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
pygame.display.set_caption("Darts Game - 301 Edition")
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
player_score = pc_score = player_start_score = pc_start_score = 301
current_turn = "PLAYER" 
darts_thrown = 0
darts_on_board = [] 
turn_scores = [] 
particles = [] # Becsapódási effektek tárolója

action_phase = "AIM_X" 
aim_x_val = BOARD_CENTER[0]
aim_x_dir = aim_y_dir = 1
aim_y_val = BOARD_CENTER[1]
flying_dart = None 
timer = 0 

# Előre renderelt háttér és UI rétegek
bg_surface = pygame.Surface((WIDTH, HEIGHT))
for y in range(HEIGHT):
    for x in range(WIDTH):
        dist = math.sqrt((x - WIDTH/2)**2 + (y - HEIGHT/2)**2)
        ratio = min(1.0, dist / (WIDTH * 0.7))
        r = int(DARK_BG_CENTER[0] * (1 - ratio) + DARK_BG_EDGE[0] * ratio)
        g = int(DARK_BG_CENTER[1] * (1 - ratio) + DARK_BG_EDGE[1] * ratio)
        b = int(DARK_BG_CENTER[2] * (1 - ratio) + DARK_BG_EDGE[2] * ratio)
        bg_surface.set_at((x, y), (r, g, b))

ui_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
pygame.draw.rect(ui_surface, BOARD_BG, (10, 10, 220, 120), border_radius=12)
pygame.draw.rect(ui_surface, BOARD_BG, (WIDTH - 230, 10, 220, 120), border_radius=12)

def get_scaled_mouse_pos():
    mx, my = pygame.mouse.get_pos()
    sw, sh = screen.get_size()
    scale = min(sw / WIDTH, sh / HEIGHT)
    return ((mx - (sw - int(WIDTH * scale)) // 2) / scale, (my - (sh - int(HEIGHT * scale)) // 2) / scale)

def reset_turn_data():
    global darts_thrown, darts_on_board, action_phase, aim_x_val, aim_y_val, turn_scores
    darts_thrown = 0
    darts_on_board.clear()
    turn_scores.clear()
    action_phase = "AIM_X"
    aim_x_val, aim_y_val = BOARD_CENTER[0], BOARD_CENTER[1]

def start_flight(is_pc=False):
    global action_phase, flying_dart
    action_phase = "FLYING"
    start_pos = (WIDTH//2, HEIGHT + 100)
    target_pos = (aim_x_val, aim_y_val)
    flight_angle = math.degrees(math.atan2(target_pos[1] - start_pos[1], target_pos[0] - start_pos[0])) + 90
    flying_dart = {"pos": start_pos, "target": target_pos, "progress": 0.0, "is_pc": is_pc}

def spawn_particles(x, y):
    for _ in range(15):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 4)
        particles.append([x, y, math.cos(angle)*speed, math.sin(angle)*speed, 255])

def update_and_draw_particles(surface):
    for p in reversed(particles):
        p[0] += p[2]
        p[1] += p[3]
        p[4] -= 10 # Fade out sebesség
        if p[4] <= 0:
            particles.remove(p)
        else:
            pygame.draw.circle(surface, (255, 200, 100, p[4]), (int(p[0]), int(p[1])), 2)

def draw_modern_dart(surface, x, y, angle_deg, scale):
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    
    def transform(px, py):
        rx = px * cos_a - py * sin_a
        ry = px * sin_a + py * cos_a
        return (x + rx * scale, y + ry * scale)

    # Árnyék (csak repülés közben látható igazán az eltolás miatt)
    shadow_pts = [transform(0, 50), transform(10, 100), transform(-10, 100)]
    pygame.draw.polygon(surface, SHADOW, shadow_pts)

    pygame.draw.polygon(surface, SILVER, [transform(0,0), transform(4, 12), transform(-4, 12)])
    
    # Henger test fémes csillogással
    barrel_pts = [transform(4, 12), transform(5, 40), transform(-5, 40), transform(-4, 12)]
    pygame.draw.polygon(surface, (210, 170, 40), barrel_pts)
    pygame.draw.polygon(surface, (255, 240, 180), [transform(1, 15), transform(2, 38), transform(0, 38), transform(-1, 15)]) # Highlight
    
    pygame.draw.line(surface, (30, 30, 30), transform(0, 40), transform(0, 75), max(1, int(4*scale)))
    
    f_pts = [transform(0, 70), transform(15, 95), transform(15, 105), transform(0, 95), 
             transform(-15, 105), transform(-15, 95)]
    pygame.draw.polygon(surface, RED, f_pts)
    pygame.draw.polygon(surface, (150, 20, 20), [transform(0, 70), transform(15, 95), transform(0, 95)]) # Toll árnyékolás

def draw_ui(surface):
    surface.blit(ui_surface, (0, 0))
    surface.blit(font.render("PLAYER", True, GRAY), (25, 15))
    surface.blit(score_font.render(str(player_score), True, WHITE), (25, 35))
    
    pc_lbl = font.render("COMPUTER", True, GRAY)
    surface.blit(pc_lbl, (WIDTH - 25 - pc_lbl.get_width(), 15))
    pc_scr = score_font.render(str(pc_score), True, WHITE)
    surface.blit(pc_scr, (WIDTH - 25 - pc_scr.get_width(), 35))
    
    score_surf = small_font.render(" + ".join([str(s) for s in turn_scores]), True, GOLD)
    surface.blit(score_surf, (25 if current_turn == "PLAYER" else WIDTH - 25 - score_surf.get_width(), 90))

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
        virtual_surface.blit(bg_surface, (0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                is_fullscreen = not is_fullscreen
                screen = pygame.display.set_mode((0, 0) if is_fullscreen else (WIDTH, HEIGHT), pygame.FULLSCREEN if is_fullscreen else pygame.RESIZABLE)

            if state == GameState.MENU and event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(get_scaled_mouse_pos()) or is_fullscreen:
                    state, player_score, pc_score, player_start_score, pc_start_score, current_turn = GameState.PLAYING, 301, 301, 301, 301, "PLAYER"
                    reset_turn_data()
                    
            elif state == GameState.GAMEOVER and event.type == pygame.MOUSEBUTTONDOWN:
                if restart_btn_rect.collidepoint(get_scaled_mouse_pos()):
                    state, player_score, pc_score, player_start_score, pc_start_score, current_turn = GameState.PLAYING, 301, 301, 301, 301, "PLAYER"
                    reset_turn_data()

            elif state == GameState.PLAYING and current_turn == "PLAYER" and event.type == pygame.MOUSEBUTTONDOWN:
                if action_phase == "AIM_X":
                    action_phase, aim_y_val, aim_y_dir = "AIM_Y", BOARD_CENTER[1] + R_BOARD, -1
                elif action_phase == "AIM_Y":
                    start_flight(is_pc=False)

        if state == GameState.MENU:
            title = title_font.render("DARTS GAME 301", True, WHITE)
            virtual_surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            pygame.draw.rect(virtual_surface, RED, btn_rect, border_radius=30)
            btn_txt = font.render("START GAME", True, WHITE)
            virtual_surface.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width()//2, btn_rect.centery - btn_txt.get_height()//2))
            
        elif state in (GameState.PLAYING, GameState.WAITING_FOR_NEXT_TURN):
            dartboard.draw_board(virtual_surface, font)
            
            for x, y, _ in darts_on_board:
                draw_modern_dart(virtual_surface, x, y, 0, 0.4)
            
            update_and_draw_particles(virtual_surface)
            draw_ui(virtual_surface)

            if state == GameState.PLAYING:
                if current_turn == "PLAYER":
                    if action_phase == "AIM_X":
                        dist = abs(aim_x_val - BOARD_CENTER[0])
                        aim_x_val += (3.5 * (1.0 + (1.0 - min(1.0, dist / 200.0)) * 1.2)) * aim_x_dir
                        if aim_x_val > BOARD_CENTER[0] + 200 or aim_x_val < BOARD_CENTER[0] - 200: aim_x_dir *= -1
                    elif action_phase == "AIM_Y":
                        dist_y = abs(aim_y_val - BOARD_CENTER[1])
                        aim_y_val += (3.5 * (R_BOARD / 200.0) * (1.0 + (1.0 - min(1.0, dist_y / float(R_BOARD))) * 1.2)) * aim_y_dir
                        if aim_y_val > BOARD_CENTER[1] + R_BOARD + 10 or aim_y_val < BOARD_CENTER[1] - R_BOARD - 10: aim_y_dir *= -1
                    
                    if action_phase in ("AIM_X", "AIM_Y"):
                        s_x = WIDTH//2 - 200
                        pygame.draw.rect(virtual_surface, BLACK, (s_x, HEIGHT-100, 400, 10), border_radius=5)
                        pygame.draw.circle(virtual_surface, GOLD if action_phase=="AIM_X" else GRAY, (int(max(s_x, min(aim_x_val, s_x+400))), HEIGHT-95), 10)
                        
                        if action_phase == "AIM_Y":
                            pygame.draw.circle(virtual_surface, GOLD, (int(aim_x_val), int(aim_y_val)), 6, 2)
                            p_w, p_h, p_x, p_y = 16, R_BOARD * 2 + 20, WIDTH - 60, BOARD_CENTER[1] - R_BOARD - 10
                            pygame.draw.rect(virtual_surface, BLACK, (p_x, p_y, p_w, p_h), border_radius=8)
                            pygame.draw.line(virtual_surface, GREEN, (p_x - 10, BOARD_CENTER[1]), (p_x + p_w + 10, BOARD_CENTER[1]), 3)
                            pygame.draw.line(virtual_surface, GOLD, (p_x - 10, BOARD_CENTER[1] - (R_TRIPLE_INNER + R_TRIPLE_OUTER) / 2), (p_x + p_w + 10, BOARD_CENTER[1] - (R_TRIPLE_INNER + R_TRIPLE_OUTER) / 2), 3)
                            pygame.draw.circle(virtual_surface, RED, (p_x + p_w//2, int(aim_y_val)), 8)
                
                elif current_turn == "COMPUTER" and action_phase != "FLYING":
                    timer += 1
                    if timer > 60:
                        aim_x_val, aim_y_val = BOARD_CENTER[0] + random.randint(-35, 35), BOARD_CENTER[1] - (R_TRIPLE_INNER + R_TRIPLE_OUTER)/2 + random.randint(-35, 35)
                        start_flight(is_pc=True)
                        timer = 0

                if action_phase == "FLYING":
                    fd = flying_dart
                    fd["progress"] += 0.035
                    t = fd["progress"]
                    
                    arc = (HEIGHT - fd["target"][1]) * 0.4
                    curr_x = fd["pos"][0] + (fd["target"][0] - fd["pos"][0]) * t
                    curr_y = fd["pos"][1] + (fd["target"][1] - fd["pos"][1]) * t - arc * math.sin(math.pi * t)
                    
                    # Dinamikus árnyék a táblán
                    shadow_y = fd["target"][1] + (1-t)*100
                    pygame.draw.ellipse(virtual_surface, SHADOW, (curr_x - 10*t, shadow_y, 20*t, 10*t))

                    dt = 0.01
                    next_y = fd["pos"][1] + (fd["target"][1] - fd["pos"][1]) * (t+dt) - arc * math.sin(math.pi * (t+dt))
                    next_x = fd["pos"][0] + (fd["target"][0] - fd["pos"][0]) * (t+dt)
                    angle = math.degrees(math.atan2(next_y - curr_y, next_x - curr_x)) + 90
                    
                    draw_modern_dart(virtual_surface, curr_x, curr_y, angle, 1.5 - t)

                    if t >= 1.0:
                        spawn_particles(fd["target"][0], fd["target"][1])
                        score = dartboard.get_score(fd["target"][0], fd["target"][1])
                        turn_scores.append(score)
                        darts_on_board.append((fd["target"][0], fd["target"][1], fd["is_pc"]))
                        darts_thrown += 1

                        if fd["is_pc"]: 
                            pc_score = pc_start_score if pc_score - score < 0 else pc_score - score
                            if pc_score == pc_start_score: darts_thrown = 3
                        else: 
                            player_score = player_start_score if player_score - score < 0 else player_score - score
                            if player_score == player_start_score: darts_thrown = 3
                        
                        if player_score == 0 or pc_score == 0: state = GameState.GAMEOVER
                        elif darts_thrown >= 3: state, timer = GameState.WAITING_FOR_NEXT_TURN, 0
                        else: action_phase = "AIM_X"
            
            if state == GameState.WAITING_FOR_NEXT_TURN:
                timer += 1
                if timer > 90:
                    current_turn = "COMPUTER" if current_turn == "PLAYER" else "PLAYER"
                    reset_turn_data()
                    player_start_score, pc_start_score = player_score, pc_score
                    state, timer = GameState.PLAYING, 0

        elif state == GameState.GAMEOVER:
            txt = title_font.render("PLAYER WINS!" if player_score == 0 else "COMPUTER WINS!", True, GREEN)
            virtual_surface.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 60))
            pygame.draw.rect(virtual_surface, RED, restart_btn_rect, border_radius=30)
            btn_txt = font.render("NEW GAME", True, WHITE)
            virtual_surface.blit(btn_txt, (restart_btn_rect.centerx - btn_txt.get_width()//2, restart_btn_rect.centery - btn_txt.get_height()//2))

        sw, sh = screen.get_size()
        scale = min(sw / WIDTH, sh / HEIGHT)
        new_w, new_h = int(WIDTH * scale), int(HEIGHT * scale)
        screen.fill(BLACK) 
        screen.blit(pygame.transform.smoothscale(virtual_surface, (new_w, new_h)), ((sw - new_w) // 2, (sh - new_h) // 2))
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
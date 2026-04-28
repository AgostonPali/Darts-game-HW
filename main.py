# main.py
import pygame
import sys
import random
import math
from config import *
import dartboard
import physics

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Darts Simulator Pro")
clock = pygame.time.Clock()

# Fontok
font = pygame.font.SysFont("Segoe UI, Arial", 22, bold=True)
small_font = pygame.font.SysFont("Segoe UI, Arial", 16, bold=True)
title_font = pygame.font.SysFont("Segoe UI, Arial", 56, bold=True)
score_font = pygame.font.SysFont("Segoe UI, Arial", 42, bold=True)

class GameState:
    MENU = 0
    PLAYING = 1
    WAITING_FOR_NEXT_TURN = 2
    GAMEOVER = 3

# Állapotok és globális változók
state = GameState.MENU
player_score = 301
pc_score = 301
current_turn = "PLAYER" 
darts_thrown = 0
darts_on_board = [] 
turn_scores = [] # Az aktuális 3 dobás értéke

action_phase = "AIM_X" 
aim_x_val = BOARD_CENTER[0]
aim_x_dir = 1
power_level = 0.0
power_dir = 1
flying_dart = None 
timer = 0 # Általános időzítő szünetekhez

def reset_turn_data():
    global darts_thrown, darts_on_board, action_phase, aim_x_val, turn_scores
    darts_thrown = 0
    darts_on_board.clear()
    turn_scores.clear()
    action_phase = "AIM_X"
    aim_x_val = BOARD_CENTER[0]

def start_flight(is_pc=False):
    global action_phase, flying_dart
    action_phase = "FLYING"
    hit_pos = physics.calculate_impact(aim_x_val, power_level)
    
    flying_dart = {
        "pos": (WIDTH//2, HEIGHT),
        "target": hit_pos,
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

    # Hegy
    pygame.draw.polygon(surface, SILVER, [transform(0,0), transform(4, 12), transform(-4, 12)])
    # Test
    pygame.draw.polygon(surface, (200, 160, 50), [transform(4, 12), transform(5, 40), transform(-5, 40), transform(-4, 12)])
    # Szár
    pygame.draw.line(surface, (30, 30, 30), transform(0, 40), transform(0, 75), max(1, int(4*scale)))
    # Toll
    f_pts = [transform(0, 70), transform(15, 95), transform(15, 105), transform(0, 95), 
             transform(-15, 105), transform(-15, 95)]
    pygame.draw.polygon(surface, RED, f_pts)

def draw_ui():
    # Panelek
    pygame.draw.rect(screen, BOARD_BG, (10, 10, 220, 120), border_radius=12)
    pygame.draw.rect(screen, BOARD_BG, (WIDTH - 230, 10, 220, 120), border_radius=12)
    
    # Játékos info
    screen.blit(font.render("PLAYER", True, GRAY), (25, 15))
    screen.blit(score_font.render(str(player_score), True, WHITE), (25, 35))
    
    # Gép info
    pc_lbl = font.render("COMPUTER", True, GRAY)
    screen.blit(pc_lbl, (WIDTH - 25 - pc_lbl.get_width(), 15))
    pc_scr = score_font.render(str(pc_score), True, WHITE)
    screen.blit(pc_scr, (WIDTH - 25 - pc_scr.get_width(), 35))
    
    # Aktuális kör részeredményei
    score_str = " + ".join([str(s) for s in turn_scores])
    score_surf = small_font.render(score_str, True, GOLD)
    if current_turn == "PLAYER":
        screen.blit(score_surf, (25, 90))
    else:
        screen.blit(score_surf, (WIDTH - 25 - score_surf.get_width(), 90))

    # Turn display
    turn_text = font.render("PLAYER'S TURN" if current_turn == "PLAYER" else "COMPUTER'S TURN", 
                            True, RED if current_turn == "PLAYER" else GREEN)
    screen.blit(turn_text, (WIDTH//2 - turn_text.get_width()//2, 20))
    
    # Készleten lévő nyilak (ikonok)
    for i in range(3 - darts_thrown):
        draw_modern_dart(screen, 40 + i*35, HEIGHT - 70, 0, 0.6)

def main():
    global state, aim_x_val, aim_x_dir, action_phase, power_level, power_dir
    global darts_thrown, player_score, pc_score, flying_dart, current_turn, timer, turn_scores

    while True:
        screen.fill(DARK_BG)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if state == GameState.MENU and event.type == pygame.MOUSEBUTTONDOWN:
                state = GameState.PLAYING
                reset_turn_data()
            elif state == GameState.PLAYING and current_turn == "PLAYER":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if action_phase == "AIM_X":
                        action_phase = "POWER"
                        power_level = 0.0
                    elif action_phase == "POWER":
                        start_flight(is_pc=False)

        if state == GameState.MENU:
            title = title_font.render("DARTS PRO 301", True, WHITE)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            btn_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT//2, 240, 60)
            pygame.draw.rect(screen, RED, btn_rect, border_radius=30)
            btn_txt = font.render("START GAME", True, WHITE)
            screen.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width()//2, btn_rect.centery - btn_txt.get_height()//2))
            
        elif state == GameState.PLAYING or state == GameState.WAITING_FOR_NEXT_TURN:
            dartboard.draw_board(screen, font)
            for x, y, _ in darts_on_board:
                draw_modern_dart(screen, x, y, 0, 0.4)
            draw_ui()

            if state == GameState.PLAYING:
                if current_turn == "PLAYER":
                    if action_phase == "AIM_X":
                        dist = abs(aim_x_val - BOARD_CENTER[0])
                        speed_mult = 1.0 + (1.0 - min(1.0, dist / 200.0)) * 1.2
                        aim_x_val += (3.5 * speed_mult) * aim_x_dir
                        if aim_x_val > BOARD_CENTER[0] + 200 or aim_x_val < BOARD_CENTER[0] - 200:
                            aim_x_dir *= -1
                    elif action_phase == "POWER":
                        power_level += 0.015 * power_dir
                        if power_level >= 1.0 or power_level <= 0.0: power_dir *= -1
                    
                    if action_phase in ["AIM_X", "POWER"]:
                        # UI Sliders & Target Point
                        s_x = WIDTH//2 - 200
                        pygame.draw.rect(screen, BLACK, (s_x, HEIGHT-100, 400, 10), border_radius=5)
                        pygame.draw.circle(screen, GOLD if action_phase=="AIM_X" else GRAY, 
                                           (int(max(s_x, min(aim_x_val, s_x+400))), HEIGHT-95), 10)
                        if action_phase == "POWER":
                            px, py = physics.calculate_impact(aim_x_val, power_level)
                            pygame.draw.circle(screen, GOLD, (px, py), 6, 2)
                
                elif current_turn == "COMPUTER" and action_phase != "FLYING":
                    timer += 1
                    if timer > 60: # Gép gondolkodási ideje dobások között
                        aim_x_val = BOARD_CENTER[0] + random.randint(-40, 40)
                        power_level = 0.75 + random.uniform(-0.1, 0.08)
                        start_flight(is_pc=True)
                        timer = 0

                if action_phase == "FLYING":
                    fd = flying_dart
                    # Sebesség: 0.015-ről 0.035-re növelve a dinamizmusért
                    fd["progress"] += 0.035
                    t = fd["progress"]
                    
                    # Pozíció számítás ívvel
                    arc = 250 * (0.5 + power_level/2)
                    curr_x = fd["pos"][0] + (fd["target"][0] - fd["pos"][0]) * t
                    curr_y = fd["pos"][1] + (fd["target"][1] - fd["pos"][1]) * t - arc * math.sin(math.pi * t)
                    
                    # Érintő alapú dőlésszög (felfelé állásból lefelé billenés)
                    # Közelítő derivált a dőléshez
                    dt = 0.01
                    next_y = fd["pos"][1] + (fd["target"][1] - fd["pos"][1]) * (t+dt) - arc * math.sin(math.pi * (t+dt))
                    next_x = fd["pos"][0] + (fd["target"][0] - fd["pos"][0]) * (t+dt)
                    angle = math.degrees(math.atan2(next_y - curr_y, next_x - curr_x)) + 90
                    
                    draw_modern_dart(screen, curr_x, curr_y, angle, 1.5 - t)

                    if t >= 1.0:
                        score = dartboard.get_score(fd["target"][0], fd["target"][1])
                        turn_scores.append(score)
                        darts_on_board.append((fd["target"][0], fd["target"][1], fd["is_pc"]))
                        
                        if fd["is_pc"]: pc_score = max(0, pc_score - score)
                        else: player_score = max(0, player_score - score)
                        
                        darts_thrown += 1
                        if player_score == 0 or pc_score == 0: state = GameState.GAMEOVER
                        elif darts_thrown >= 3:
                            state = GameState.WAITING_FOR_NEXT_TURN
                            timer = 0
                        else:
                            action_phase = "AIM_X"
            
            # Forduló utáni várakozás
            if state == GameState.WAITING_FOR_NEXT_TURN:
                timer += 1
                if timer > 90: # Kb. 1.5 másodperc szünet
                    current_turn = "COMPUTER" if current_turn == "PLAYER" else "PLAYER"
                    reset_turn_data()
                    state = GameState.PLAYING
                    timer = 0

        elif state == GameState.GAMEOVER:
            msg = "PLAYER WINS!" if player_score == 0 else "COMPUTER WINS!"
            txt = title_font.render(msg, True, GREEN)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
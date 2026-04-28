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
pygame.display.set_caption("Darts Szimulátor")
clock = pygame.time.Clock()

# Modern fontok (ha nincs a rendszeren, visszavált alapra)
font = pygame.font.SysFont("Segoe UI, Arial", 22, bold=True)
title_font = pygame.font.SysFont("Segoe UI, Arial", 56, bold=True)
score_font = pygame.font.SysFont("Segoe UI, Arial", 36, bold=True)

class GameState:
    MENU = 0
    PLAYING = 1
    GAMEOVER = 2

# Állapotok
state = GameState.MENU
player_score = 501
pc_score = 501
current_turn = "PLAYER" 
darts_thrown = 0
darts_on_board = [] # (x, y, is_pc)

# Új célzási változók
action_phase = "AIM_X" # "AIM_X", "POWER", "FLYING", "WAIT"
aim_x_val = BOARD_CENTER[0]
aim_x_dir = 1
power_level = 0.0
power_dir = 1
flying_dart = None 
pc_timer = 0

def reset_turn():
    global darts_thrown, darts_on_board, action_phase, aim_x_val
    darts_thrown = 0
    darts_on_board.clear()
    action_phase = "AIM_X"
    aim_x_val = BOARD_CENTER[0]

def start_flight(is_pc=False):
    global action_phase, flying_dart
    action_phase = "FLYING"
    hit_pos = physics.calculate_impact(aim_x_val, power_level)
    
    start_pos = (WIDTH//2, HEIGHT)
    # Szög a nyíl irányához (hogy a tábla felé mutasson repülés közben)
    flight_angle = math.degrees(math.atan2(hit_pos[1] - start_pos[1], hit_pos[0] - start_pos[0])) + 90
    
    flying_dart = {
        "pos": start_pos, 
        "target": hit_pos, 
        "progress": 0.0, 
        "angle": flight_angle,
        "is_pc": is_pc
    }

def draw_modern_dart(surface, x, y, angle_deg, scale):
    """Kidolgozottabb nyíl megjelenítése forgatva és skálázva."""
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    
    def transform(px, py):
        # Elforgatás és eltolás a megadott (x,y) koordinátára
        rx = px * cos_a - py * sin_a
        ry = px * sin_a + py * cos_a
        return (x + rx * scale, y + ry * scale)

    # 1. Hegy (ezüst)
    pygame.draw.polygon(surface, SILVER, [transform(0,0), transform(5, 15), transform(-5, 15)])
    
    # 2. Test / Barrel (arany/réz recézve)
    barrel_points = [transform(4, 15), transform(6, 45), transform(-6, 45), transform(-4, 15)]
    pygame.draw.polygon(surface, (200, 160, 50), barrel_points)
    # Recézés (grips) a testen
    for i in range(20, 45, 4):
        pygame.draw.line(surface, BLACK, transform(-5, i), transform(5, i), max(1, int(1*scale)))
        
    # 3. Szár (fekete)
    pygame.draw.polygon(surface, (30, 30, 30), [transform(4, 45), transform(3, 80), transform(-3, 80), transform(-4, 45)])
    
    # 4. Toll (piros modern forma)
    flight_points = [
        transform(2, 70), transform(20, 95), transform(20, 110), transform(2, 100),
        transform(-2, 100), transform(-20, 110), transform(-20, 95), transform(-2, 70)
    ]
    pygame.draw.polygon(surface, RED, flight_points)
    pygame.draw.polygon(surface, BLACK, flight_points, 1)

def draw_ui():
    # Játékos panelek árnyékolt háttérrel
    pygame.draw.rect(screen, BOARD_BG, (10, 10, 200, 80), border_radius=10)
    pygame.draw.rect(screen, BOARD_BG, (WIDTH - 210, 10, 200, 80), border_radius=10)
    
    screen.blit(font.render("JÁTÉKOS", True, GRAY), (20, 15))
    screen.blit(score_font.render(str(player_score), True, WHITE), (20, 40))
    
    pc_lbl = font.render("GÉP", True, GRAY)
    screen.blit(pc_lbl, (WIDTH - 20 - pc_lbl.get_width(), 15))
    pc_scr = score_font.render(str(pc_score), True, WHITE)
    screen.blit(pc_scr, (WIDTH - 20 - pc_scr.get_width(), 40))
    
    turn_text = font.render("TE JÖSSZ" if current_turn == "PLAYER" else "GÉP JÖN", True, RED if current_turn=="PLAYER" else GREEN)
    screen.blit(turn_text, (WIDTH//2 - turn_text.get_width()//2, 30))
    
    # Nyilak a képernyő alján
    for i in range(3 - darts_thrown):
        draw_modern_dart(screen, 60 + i*50, HEIGHT - 100, 0, 0.8)

def process_pc_turn():
    global pc_timer, action_phase, aim_x_val, power_level
    
    pc_timer -= 1
    if pc_timer <= 0:
        if action_phase == "AIM_X":
            aim_x_val = BOARD_CENTER[0] + random.randint(-20, 20)
            action_phase = "POWER"
            pc_timer = 30
        elif action_phase == "POWER":
            # Gép megpróbálja eltalálni az ideális 0.75-ös erőt
            power_level = 0.75 + random.uniform(-0.06, 0.04) 
            start_flight(is_pc=True)

def draw_sliders():
    # --- Vízszintes Célkereszt (AIM_X fázisban mozog) ---
    slider_width = 400
    slider_y = HEIGHT - 120
    slider_x_start = WIDTH//2 - slider_width//2
    
    # Háttér sáv
    pygame.draw.rect(screen, BLACK, (slider_x_start, slider_y, slider_width, 10), border_radius=5)
    pygame.draw.rect(screen, GRAY, (slider_x_start, slider_y, slider_width, 10), 1, border_radius=5)
    
    # Közép jelölő
    pygame.draw.line(screen, WHITE, (WIDTH//2, slider_y - 5), (WIDTH//2, slider_y + 15), 2)
    
    # Mozgó kurzor
    cursor_x = max(slider_x_start, min(aim_x_val, slider_x_start + slider_width))
    color_x = GOLD if action_phase == "AIM_X" else GRAY
    pygame.draw.circle(screen, color_x, (int(cursor_x), slider_y + 5), 10)
    
    # Ha lerögzítettük az X-et, felrajzolunk egy halvány vonalat a táblára
    if action_phase != "AIM_X":
        pygame.draw.line(screen, (255, 215, 0, 100), (aim_x_val, 0), (aim_x_val, HEIGHT), 1)

    # --- Függőleges Erősség Skála (POWER fázisban mozog) ---
    p_width, p_height = 20, 300
    p_x = WIDTH - 60
    p_y = HEIGHT//2 - p_height//2
    
    pygame.draw.rect(screen, BLACK, (p_x, p_y, p_width, p_height), border_radius=10)
    
    # Optimális erőszint jelölő vonal (kb. 0.75)
    ideal_y = p_y + p_height - int(0.75 * p_height)
    pygame.draw.line(screen, GREEN, (p_x - 10, ideal_y), (p_x + p_width + 10, ideal_y), 3)
    
    # Aktuális erőszint
    fill_h = int(power_level * p_height)
    color_p = RED if action_phase == "POWER" else GRAY
    pygame.draw.rect(screen, color_p, (p_x, p_y + p_height - fill_h, p_width, fill_h), border_radius=10)

def main():
    global state, aim_x_val, aim_x_dir, action_phase, power_level, power_dir
    global darts_thrown, player_score, pc_score, flying_dart, current_turn, pc_timer

    while True:
        screen.fill(DARK_BG)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if state == GameState.MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    state = GameState.PLAYING
                    reset_turn()
                    
            elif state == GameState.PLAYING and current_turn == "PLAYER":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if action_phase == "AIM_X":
                        action_phase = "POWER"
                        power_level = 0.0
                    elif action_phase == "POWER":
                        start_flight(is_pc=False)

        if state == GameState.MENU:
            # Modern menü árnyékos címmel
            shadow = title_font.render("DARTS PRO", True, BLACK)
            title = title_font.render("DARTS PRO", True, WHITE)
            screen.blit(shadow, (WIDTH//2 - shadow.get_width()//2 + 3, HEIGHT//3 + 3))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            
            # Gomb
            btn_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2, 300, 60)
            pygame.draw.rect(screen, RED, btn_rect, border_radius=30)
            btn_txt = font.render("JÁTÉK INDÍTÁSA", True, WHITE)
            screen.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width()//2, btn_rect.centery - btn_txt.get_height()//2))
            
        elif state == GameState.PLAYING:
            dartboard.draw_board(screen, font)
            
            # Bedobott nyilak
            for x, y, is_pc in darts_on_board:
                draw_modern_dart(screen, x, y, 0, 0.4)
            
            draw_ui()
            
            if current_turn == "PLAYER":
                if action_phase == "AIM_X":
                    # Nem lineáris sebesség számítása: középen gyorsabb
                    dist_from_center = abs(aim_x_val - BOARD_CENTER[0])
                    # Szorzó: szélén 1x, középen 3x sebesség
                    speed_mult = 1.0 + (1.0 - min(1.0, dist_from_center / 200.0)) * 2.0
                    
                    aim_x_val += (4 * speed_mult) * aim_x_dir
                    
                    if aim_x_val > BOARD_CENTER[0] + 200 or aim_x_val < BOARD_CENTER[0] - 200:
                        aim_x_dir *= -1
                        
                elif action_phase == "POWER":
                    # Kicsit lassított erősség csúszka
                    power_level += 0.015 * power_dir
                    if power_level >= 1.0:
                        power_level = 1.0
                        power_dir = -1
                    elif power_level <= 0.0:
                        power_level = 0.0
                        power_dir = 1
            
            elif current_turn == "PC" and action_phase != "FLYING":
                process_pc_turn()
            
            # Skálák rajzolása az UI fölé
            if action_phase in ["AIM_X", "POWER"]:
                draw_sliders()
            
            if action_phase == "FLYING":
                fd = flying_dart
                fd["progress"] += 0.05
                
                # Z-tengely mélység szimulációja skálázással (nyíl kisebb lesz ahogy távolodik)
                current_scale = 1.5 - fd["progress"]
                
                cx = int(fd["pos"][0] + (fd["target"][0] - fd["pos"][0]) * fd["progress"])
                cy = int(fd["pos"][1] + (fd["target"][1] - fd["pos"][1]) * fd["progress"])
                
                draw_modern_dart(screen, cx, cy, fd["angle"], max(0.4, current_scale))
                
                if fd["progress"] >= 1.0:
                    darts_on_board.append((fd["target"][0], fd["target"][1], fd["is_pc"]))
                    score = dartboard.get_score(fd["target"][0], fd["target"][1])
                    
                    if fd["is_pc"]:
                        pc_score = max(0, pc_score - score)
                    else:
                        player_score = max(0, player_score - score)
                        
                    darts_thrown += 1
                    
                    if player_score == 0 or pc_score == 0:
                        state = GameState.GAMEOVER
                    elif darts_thrown >= 3:
                        current_turn = "PC" if current_turn == "PLAYER" else "PLAYER"
                        pc_timer = 40
                        reset_turn()
                    else:
                        action_phase = "AIM_X"
                        pc_timer = 40
                
        elif state == GameState.GAMEOVER:
            winner = "JÁTÉKOS" if player_score == 0 else "GÉP"
            pygame.draw.rect(screen, BOARD_BG, (WIDTH//2 - 200, HEIGHT//2 - 60, 400, 120), border_radius=20)
            end_text = title_font.render(f"{winner} NYERT!", True, GREEN)
            screen.blit(end_text, (WIDTH//2 - end_text.get_width()//2, HEIGHT//2 - end_text.get_height()//2))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
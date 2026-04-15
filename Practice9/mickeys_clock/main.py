"""
main.py — Mickey Mouse Clock  (v4 — real images)
=================================================
• Clock face   : images/clock_square.png
• Mickey body  : images/mickey_alpha.png  (centred on clock)
• Rotating hand: images/hand_cropped.png  (wrist at Mickey's right
                  shoulder, rotates clockwise by seconds)

0 sec  → 12 o'clock (hand points UP)
15 sec → 3 o'clock
30 sec → 6 o'clock
45 sec → 9 o'clock

Run:
    pip install pygame pillow
    python main.py
"""

import pygame
import sys
import os
import math
from clock import get_current_time, get_second_angle, format_time

# ═══════════════════════════════════════════════
#  WINDOW
# ═══════════════════════════════════════════════
WIN_W   = 660
WIN_H   = 800
CLOCK_S = 620           # clock face square on screen
CLOCK_X = (WIN_W - CLOCK_S) // 2
CLOCK_Y = 8
CX      = WIN_W // 2
CY      = CLOCK_Y + CLOCK_S // 2

FPS     = 30
TITLE   = "Mickey's Clock"

C_BG       = (250, 245, 235)
C_BLACK    = ( 20,  20,  20)
C_WHITE    = (255, 255, 255)
C_RED      = (210,  30,  30)
C_BLUE     = ( 50, 110, 230)
C_GRAY     = (110, 110, 120)
C_DARK     = ( 55,  55,  65)
C_TIMER_BG = (235, 212, 138)
C_TIMER_BD = ( 80,  75,  60)

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")


# ═══════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════
def load(name, size=None, alpha=True):
    img = pygame.image.load(os.path.join(IMG_DIR, name))
    img = img.convert_alpha() if alpha else img.convert()
    if size:
        img = pygame.transform.smoothscale(img, size)
    return img


def draw_hand_at(surf, hand, angle_cw, pivot):
    """
    Rotate hand CW by angle_cw°, keeping its wrist (bottom-centre)
    pinned to pivot on surf.
    angle_cw = 0  → points UP (12 o'clock)
    """
    hw, hh   = hand.get_size()
    diag     = int(math.hypot(hw, hh)) + 8
    canvas_s = diag * 2
    canvas   = pygame.Surface((canvas_s, canvas_s), pygame.SRCALPHA)

    # paste so wrist (bottom-centre) = canvas centre
    canvas.blit(hand, (diag - hw // 2, diag - hh))

    rotated      = pygame.transform.rotate(canvas, -angle_cw)   # CW rotation
    rot_w, rot_h = rotated.get_size()
    surf.blit(rotated, (pivot[0] - rot_w // 2,
                        pivot[1] - rot_h // 2))


def draw_timer(surf, seconds, minutes, hours, f_big, f_med, f_sm):
    py   = CLOCK_Y + CLOCK_S + 4
    ph   = WIN_H - py - 6
    rect = pygame.Rect(8, py, WIN_W - 16, ph)
    pygame.draw.rect(surf, C_TIMER_BG, rect, border_radius=18)
    pygame.draw.rect(surf, C_TIMER_BD, rect, 2, border_radius=18)

    pcx = WIN_W // 2
    pcy = py + ph // 2
    acx = pcx - 140    # arc centre x

    # background ring
    arc_r, thick = 34, 8
    for deg in range(360):
        a = math.radians(deg - 90)
        x1 = int(acx + (arc_r - thick//2)*math.cos(a))
        y1 = int(pcy + (arc_r - thick//2)*math.sin(a))
        x2 = int(acx + (arc_r + thick//2)*math.cos(a))
        y2 = int(pcy + (arc_r + thick//2)*math.sin(a))
        pygame.draw.line(surf, (190,165,90), (x1,y1), (x2,y2), 2)

    # filled arc
    col = C_RED if seconds >= 50 else C_BLUE
    for deg in range(int(seconds/60*360)):
        a = math.radians(deg - 90)
        x1 = int(acx + (arc_r - thick//2)*math.cos(a))
        y1 = int(pcy + (arc_r - thick//2)*math.sin(a))
        x2 = int(acx + (arc_r + thick//2)*math.cos(a))
        y2 = int(pcy + (arc_r + thick//2)*math.sin(a))
        pygame.draw.line(surf, col, (x1,y1), (x2,y2), 2)

    surf.blit(f_big.render(f"{seconds:02d}", True, C_DARK),
              f_big.render(f"{seconds:02d}", True, C_DARK).get_rect(center=(acx, pcy-4)))
    surf.blit(f_sm.render("сек", True, C_GRAY),
              f_sm.render("сек", True, C_GRAY).get_rect(center=(acx, pcy+17)))

    ts   = f_med.render(format_time(hours, minutes, seconds), True, C_DARK)
    tr   = ts.get_rect(center=(pcx+50, pcy))
    pill = tr.inflate(22, 12)
    pygame.draw.rect(surf, C_WHITE, pill, border_radius=9)
    pygame.draw.rect(surf, C_TIMER_BD, pill, 1, border_radius=9)
    surf.blit(ts, tr)
    surf.blit(f_sm.render("Текущее время", True, C_GRAY),
              f_sm.render("Текущее время", True, C_GRAY).get_rect(center=(pcx+50, pcy-24)))


# ═══════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption(TITLE)
    clk   = pygame.time.Clock()

    f_big = pygame.font.SysFont("Arial Black", 20, bold=True)
    f_med = pygame.font.SysFont("Courier New",  28, bold=True)
    f_sm  = pygame.font.SysFont("Arial", 13)

    # ── Images ──────────────────────────────────
    clock_face = load("clock_square.png", size=(CLOCK_S, CLOCK_S), alpha=False)

    # Mickey — 52% of clock width, keep aspect 1168:880
    mw = int(CLOCK_S * 0.52)
    mh = int(mw * 880 / 1168)
    mickey = load("mickey_alpha.png", size=(mw, mh))

    # Hand — height 42% of clock size, keep aspect 185:330
    hand_h = int(CLOCK_S * 0.42)
    hand_w = int(hand_h * 185 / 330)
    hand   = load("hand_cropped.png", size=(hand_w, hand_h))

    # Mickey position (centre of clock, slightly below)
    mx = CX - mw // 2
    my = CY - mh // 2 + int(CLOCK_S * 0.04)

    # Right shoulder = roughly (68% x, 30% y) in the Mickey image
    shoulder = (mx + int(mw * 0.68),
                my + int(mh * 0.30))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if (event.type == pygame.KEYDOWN and
                    event.key == pygame.K_ESCAPE):
                running = False

        hours, minutes, seconds = get_current_time()
        angle = get_second_angle(seconds)   # 0° = 12 o'clock, CW

        screen.fill(C_BG)

        # 1. Clock face
        screen.blit(clock_face, (CLOCK_X, CLOCK_Y))

        # 2. Mickey (centred)
        screen.blit(mickey, (mx, my))

        # 3. Rotating hand — wrist at right shoulder
        draw_hand_at(screen, hand, angle, pivot=shoulder)

        # 4. Shoulder cap (covers the seam)
        pygame.draw.circle(screen, C_BLACK, shoulder, 8)
        pygame.draw.circle(screen, (70, 70, 80), shoulder, 4)

        # 5. Timer panel
        draw_timer(screen, seconds, minutes, hours, f_big, f_med, f_sm)

        pygame.display.flip()
        clk.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
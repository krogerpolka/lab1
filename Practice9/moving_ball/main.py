"""
main.py - Moving Ball Game
Control a red ball with arrow keys. Ball cannot leave the screen.

Controls:
  ↑ ↓ ← →  – Move ball (20 px per press)
  R         – Reset ball to centre
  ESC / Q   – Quit
"""

import pygame
import sys
from ball import Ball

# ── Window settings ──────────────────────────────────────────────
WIDTH, HEIGHT = 800, 600
FPS           = 60
TITLE         = "Moving Ball Game"

# ── Colours ──────────────────────────────────────────────────────
WHITE       = (255, 255, 255)
BLACK       = (  0,   0,   0)
LIGHT_BLUE  = (210, 230, 255)
DARK_BLUE   = ( 30,  60, 120)
GRAY        = (180, 180, 190)
DARK_GRAY   = ( 60,  60,  70)
ACCENT      = ( 60, 120, 220)


def draw_grid(surface, cell=40):
    """Draw a subtle background grid."""
    for x in range(0, WIDTH, cell):
        pygame.draw.line(surface, (225, 235, 250), (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, cell):
        pygame.draw.line(surface, (225, 235, 250), (0, y), (WIDTH, y), 1)


def draw_boundary(surface):
    """Draw the play-area border."""
    pygame.draw.rect(surface, ACCENT, (0, 0, WIDTH, HEIGHT), 4)


def draw_hud(surface, ball: Ball, font_info, font_small):
    """Draw position info and controls at the bottom."""
    # Info bar background
    bar_rect = (0, HEIGHT - 45, WIDTH, 45)
    pygame.draw.rect(surface, DARK_GRAY, bar_rect)

    # Position
    bx, by = ball.get_position()
    pos_txt = font_info.render(f"Position: ({bx}, {by})", True, WHITE)
    surface.blit(pos_txt, (12, HEIGHT - 35))

    # Controls hint
    hints = "[↑↓←→] Move    [R] Reset    [ESC/Q] Quit"
    hint_s = font_small.render(hints, True, GRAY)
    surface.blit(hint_s, (WIDTH - hint_s.get_width() - 12, HEIGHT - 30))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # Fonts
    font_title = pygame.font.SysFont("Arial", 30, bold=True)
    font_info  = pygame.font.SysFont("Consolas", 18)
    font_small = pygame.font.SysFont("Arial", 15)

    # Create ball in the centre
    ball = Ball(WIDTH, HEIGHT - 45)   # account for HUD strip

    # Track the last direction for a small trail effect
    trail = []   # list of (x, y) for ghost trail

    running = True
    while running:
        # ── Events ───────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False

                elif event.key == pygame.K_r:
                    # Reset ball to centre
                    ball = Ball(WIDTH, HEIGHT - 45)
                    trail.clear()

                # Arrow-key movement
                old_pos = ball.get_position()

                if event.key == pygame.K_UP:
                    ball.move_up()
                elif event.key == pygame.K_DOWN:
                    ball.move_down()
                elif event.key == pygame.K_LEFT:
                    ball.move_left()
                elif event.key == pygame.K_RIGHT:
                    ball.move_right()

                # Store trail point if ball actually moved
                new_pos = ball.get_position()
                if new_pos != old_pos:
                    trail.append(old_pos)
                    if len(trail) > 8:   # keep last 8 ghost positions
                        trail.pop(0)

        # ── Draw ─────────────────────────────────────────────
        screen.fill(LIGHT_BLUE)
        draw_grid(screen)
        draw_boundary(screen)

        # Draw ghost trail (fading circles)
        for i, (tx, ty) in enumerate(trail):
            alpha   = int(60 * (i + 1) / len(trail))
            r_size  = Ball.RADIUS - 4
            ghost_s = pygame.Surface((r_size * 2, r_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(ghost_s, (220, 30, 30, alpha),
                               (r_size, r_size), r_size)
            screen.blit(ghost_s, (tx - r_size, ty - r_size))

        # Draw ball
        ball.draw(screen)

        # Title
        t = font_title.render("Moving Ball Game", True, DARK_BLUE)
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 12))

        # HUD
        draw_hud(screen, ball, font_info, font_small)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
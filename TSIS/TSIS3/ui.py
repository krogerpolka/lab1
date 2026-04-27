"""
ui.py  —  TSIS 3
All non-gameplay screens: Main Menu, Settings, Leaderboard, Username entry.
Built entirely with pygame — no external UI libraries.
"""

import pygame   # Graphics, input, and timing
import sys      # sys.exit() for clean shutdown

# Import shared visual resources defined in racer.py
from racer import (
    screen, clock, font_large, font_medium, font_small, font_tiny,
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    WHITE, BLACK, GRAY, RED, YELLOW, GREEN, BLUE, CYAN, ORANGE,
    SILVER, GOLD, BRONZE, LIME, PURPLE, DARK,
    CAR_COLOR_MAP,
)
from persistence import load_leaderboard, load_settings, save_settings  # Data I/O


# ── Color palette for UI screens ─────────────────────────────────────────────
BG       = ( 8,  8, 18)       # Deep dark-blue background for all menu screens
ACCENT   = (255, 200,  0)     # Golden yellow — used for titles and hovered buttons
DIM      = ( 60,  60,  80)    # Muted button background when not hovered
HIGHLIGHT= (255, 255, 255)    # Pure white — hovered button border


# ══════════════════════════════════════════════════════════════════════════════
# SHARED HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _fill_bg(surface):
    """
    Fill the screen with the dark background and draw subtle vertical road lines
    in the centre for a racing atmosphere on all menu screens.
    """
    surface.fill(BG)
    # Two thin vertical stripes near the centre, repeated vertically as dashes
    for x in range(SCREEN_WIDTH // 2 - 60, SCREEN_WIDTH // 2 + 61, 120):
        for y in range(0, SCREEN_HEIGHT, 80):
            pygame.draw.rect(surface, ( 25, 25, 40), (x - 2, y, 4, 40))   # 4 px wide, 40 px tall dash


def _draw_centered(font, text, color, y, surface=None):
    """Render text centred horizontally at pixel row 'y'."""
    if surface is None:
        surface = screen
    surf = font.render(text, True, color)
    surface.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))


def _button(label, x, y, w, h, hovered, font=font_medium):
    """
    Draw a rectangular button and return its Rect for click detection.
    - When hovered: gold fill with white border (text black for contrast)
    - When not hovered: dim fill with grey border (text white)
    """
    color  = ACCENT   if hovered else DIM      # Background fill color
    border = HIGHLIGHT if hovered else GRAY    # Border color
    pygame.draw.rect(screen, color,  (x, y, w, h), border_radius=8)   # Filled rectangle
    pygame.draw.rect(screen, border, (x, y, w, h), 2, border_radius=8) # 2 px border
    lbl = font.render(label, True, BLACK if hovered else WHITE)         # Label text
    screen.blit(lbl, (x + w // 2 - lbl.get_width() // 2,
                       y + h // 2 - lbl.get_height() // 2))            # Centre label in button
    return pygame.Rect(x, y, w, h)   # Return Rect so the caller can test mouse clicks


# ══════════════════════════════════════════════════════════════════════════════
# USERNAME ENTRY  —  shown once at launch so the player can set their name
# ══════════════════════════════════════════════════════════════════════════════

def username_screen(default_name: str = "") -> str:
    """
    Full-screen text input for the player's name.
    - Pre-fills with 'default_name' (the previously saved username).
    - Returns the entered string when ENTER is pressed.
    - ESC cancels and returns the default name (or "Player").
    - Max 16 characters.
    """
    name = list(default_name)   # Work with a mutable list of characters
    cursor_visible = True        # Blinking cursor state
    cursor_timer   = 0           # Timestamp of the last cursor blink toggle

    while True:
        clock.tick(FPS)
        now = pygame.time.get_ticks()

        # Toggle cursor visibility every 500 ms for a blinking effect
        if now - cursor_timer > 500:
            cursor_visible = not cursor_visible
            cursor_timer   = now

        _fill_bg(screen)
        _draw_centered(font_large,  "ENTER YOUR NAME", ACCENT, 140)
        _draw_centered(font_small,  "Press ENTER to continue", GRAY, 210)

        # Draw the text input box
        box_w, box_h = 320, 50
        bx = SCREEN_WIDTH // 2 - box_w // 2
        by = 270
        pygame.draw.rect(screen, DIM,   (bx, by, box_w, box_h), border_radius=8)     # Background
        pygame.draw.rect(screen, ACCENT,(bx, by, box_w, box_h), 2, border_radius=8)  # Gold border

        # Show typed name + blinking cursor character
        display = "".join(name) + ("|" if cursor_visible else " ")
        txt = font_medium.render(display, True, WHITE)
        screen.blit(txt, (bx + 12, by + box_h // 2 - txt.get_height() // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    return "".join(name).strip()   # Confirm: return trimmed string
                elif event.key == pygame.K_BACKSPACE:
                    if name:
                        name.pop()                 # Delete the last typed character
                elif event.key == pygame.K_ESCAPE:
                    return default_name or "Player"   # Cancel: keep old name
                elif len(name) < 16 and event.unicode.isprintable():
                    name.append(event.unicode)     # Append printable character (letters, digits, etc.)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN MENU  —  the first screen after username entry
# ══════════════════════════════════════════════════════════════════════════════

def main_menu() -> str:
    """
    Show four buttons: PLAY, LEADERBOARD, SETTINGS, QUIT.
    Supports both mouse clicks and keyboard arrow keys + ENTER.
    Returns the lowercase action string for the chosen option.
    """
    items   = [("PLAY",        "play"),
               ("LEADERBOARD", "leaderboard"),
               ("SETTINGS",    "settings"),
               ("QUIT",        "quit")]
    selected = 0              # Keyboard cursor (highlighted button index)
    btn_w, btn_h = 260, 50
    bx = SCREEN_WIDTH // 2 - btn_w // 2   # Centre buttons horizontally

    while True:
        clock.tick(FPS)
        mouse = pygame.mouse.get_pos()   # Current mouse position

        _fill_bg(screen)

        # Title and subtitle
        _draw_centered(font_large, "RACER", ACCENT, 70)
        _draw_centered(font_small, "TSIS 3  —  Advanced Edition", SILVER, 120)

        # Draw each button; a button is highlighted if hovered by mouse OR selected by keyboard
        btns = []
        for i, (label, _) in enumerate(items):
            y       = 190 + i * 65   # Stack buttons 65 px apart
            hovered = pygame.Rect(bx, y, btn_w, btn_h).collidepoint(mouse)
            btns.append(_button(label, bx, y, btn_w, btn_h, hovered or selected == i))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(items)    # Move keyboard cursor up (wraps)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(items)    # Move keyboard cursor down (wraps)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return items[selected][1]                  # Confirm keyboard selection
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:   # Left mouse click
                for i, rect in enumerate(btns):
                    if rect.collidepoint(event.pos):
                        return items[i][1]   # Return action for the clicked button


# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS SCREEN  —  change sound, car colour, difficulty
# ══════════════════════════════════════════════════════════════════════════════

def settings_screen() -> dict:
    """
    Interactive settings screen.
    Clicking a value button cycles it to the next option.
    Returns the updated settings dict when the player clicks BACK or presses ESC.
    """
    cfg = load_settings()   # Load current values from disk

    color_options = list(CAR_COLOR_MAP.keys())       # ["blue", "red", "green", "purple", "orange"]
    diff_options  = ["easy", "normal", "hard"]

    def next_option(lst, current):
        """Return the next value in 'lst' after 'current', wrapping around."""
        idx = lst.index(current) if current in lst else 0
        return lst[(idx + 1) % len(lst)]

    BTN_W, BTN_H = 220, 44
    BX = SCREEN_WIDTH // 2 - BTN_W // 2

    while True:
        clock.tick(FPS)
        mouse = pygame.mouse.get_pos()

        _fill_bg(screen)
        _draw_centered(font_large,  "SETTINGS", ACCENT, 50)

        # Each row: (display label, dict key, current value string)
        rows = [
            ("Sound",      "sound",      str(cfg["sound"])),          # True / False
            ("Car Color",  "car_color",  cfg["car_color"]),           # blue / red / …
            ("Difficulty", "difficulty", cfg["difficulty"]),          # easy / normal / hard
        ]

        rects = {}   # Maps setting key → button Rect (for click detection)
        for i, (label, key, value) in enumerate(rows):
            y = 150 + i * 80   # Separate rows by 80 px

            # Row label above the button
            lbl_s = font_small.render(label, True, SILVER)
            screen.blit(lbl_s, (BX, y - 20))

            # Clickable value button
            hovered = pygame.Rect(BX, y, BTN_W, BTN_H).collidepoint(mouse)
            rects[key] = _button(value.upper(), BX, y, BTN_W, BTN_H, hovered)

            # Colour swatch next to the car color button so the player can preview the colour
            if key == "car_color":
                c = CAR_COLOR_MAP.get(cfg["car_color"], BLUE)
                pygame.draw.rect(screen, c, (BX + BTN_W + 16, y + 4, 36, 36), border_radius=6)

        # BACK button returns the player to the main menu
        back_y   = 450
        back_h   = pygame.Rect(BX, back_y, BTN_W, BTN_H).collidepoint(mouse)
        back_btn = _button("BACK", BX, back_y, BTN_W, BTN_H, back_h)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_settings(cfg)   # Save before leaving
                return cfg
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_btn.collidepoint(event.pos):
                    save_settings(cfg)   # Persist changes to settings.json
                    return cfg
                for key, rect in rects.items():
                    if rect.collidepoint(event.pos):
                        # Cycle to the next value for the clicked setting
                        if key == "sound":
                            cfg["sound"] = not cfg["sound"]   # Toggle True ↔ False
                        elif key == "car_color":
                            cfg["car_color"] = next_option(color_options, cfg["car_color"])
                        elif key == "difficulty":
                            cfg["difficulty"] = next_option(diff_options, cfg["difficulty"])


# ══════════════════════════════════════════════════════════════════════════════
# LEADERBOARD SCREEN  —  shows top-10 saved scores
# ══════════════════════════════════════════════════════════════════════════════

def leaderboard_screen():
    """
    Display the top-10 entries from leaderboard.json in a table.
    Columns: rank, name, score, distance (m), coins.
    Top 3 entries are coloured gold / silver / bronze.
    """
    entries = load_leaderboard()   # Read current top scores from disk
    BTN_W, BTN_H = 180, 44
    bx = SCREEN_WIDTH // 2 - BTN_W // 2

    while True:
        clock.tick(FPS)
        mouse = pygame.mouse.get_pos()

        _fill_bg(screen)
        _draw_centered(font_large, "TOP 10", ACCENT, 30)   # Screen title

        # Column header row
        _draw_h_row(65, "#", "NAME", "SCORE", "DIST", "COINS", SILVER)

        # Data rows — one per leaderboard entry
        rank_colors = [GOLD, SILVER, BRONZE]   # Special colors for ranks 1, 2, 3
        for i, e in enumerate(entries[:10]):
            y   = 95 + i * 47   # 47 px per row
            col = rank_colors[i] if i < 3 else WHITE   # Gold/Silver/Bronze for top 3, white for rest
            _draw_h_row(y, str(i + 1),
                        e.get("name", "?")[:10],           # Truncate long names to 10 chars
                        str(e.get("score", 0)),
                        str(e.get("distance", 0)) + "m",   # Show distance with 'm' unit
                        str(e.get("coins", 0)),
                        col)

        if not entries:
            _draw_centered(font_medium, "No entries yet!", GRAY, 250)   # Empty leaderboard message

        # BACK button
        hov  = pygame.Rect(bx, 565, BTN_W, BTN_H).collidepoint(mouse)
        back = _button("BACK", bx, 565, BTN_W, BTN_H, hov)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_m):
                return   # ESC or M closes the leaderboard
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    return


def _draw_h_row(y, rank, name, score, dist, coins, color):
    """
    Draw one row of the leaderboard table at vertical position 'y'.
    Each column is placed at a fixed X coordinate; text is rendered in 'color'.
    Columns: rank (#), name, score, distance, coins.
    """
    cols = [50, 100, 230, 330, 415]   # Fixed X positions for each column
    vals = [rank, name, score, dist, coins]
    for x, v in zip(cols, vals):      # zip pairs each X with the matching value
        s = font_small.render(str(v), True, color)
        screen.blit(s, (x, y))
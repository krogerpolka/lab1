"""
racer.py  —  TSIS 3
All game objects, constants, and helper draw functions.
"""

import pygame   # Main game library: handles graphics, input, sound, timing
import random   # Used to randomize lanes, speeds, coin types, obstacle kinds
import sys      # sys.exit() — cleanly terminates the program

# ──────────────────────────────────────────────
# Initialize pygame
# ──────────────────────────────────────────────
pygame.init()   # Must be called before using ANY pygame feature

# ──────────────────────────────────────────────
# Screen / timing constants
# ──────────────────────────────────────────────
SCREEN_WIDTH  = 480   # Window width in pixels
SCREEN_HEIGHT = 680   # Window height in pixels
FPS           = 60    # Target frames per second — controls game speed

# ──────────────────────────────────────────────
# Color constants  (R, G, B tuples)
# ──────────────────────────────────────────────
WHITE   = (255, 255, 255)  # Used for road lines, text, outlines
BLACK   = (  0,   0,   0)  # Used for coin labels and dark backgrounds
GRAY    = (100, 100, 100)  # Road surface color
DARK    = ( 30,  30,  30)  # Very dark shade for backgrounds
RED     = (220,  30,  30)  # Tail-lights, damage color, game-over text
YELLOW  = (255, 215,   0)  # Enemy tail-lights, coin score display
GREEN   = ( 30, 200,  30)  # HP bar when full
BLUE    = ( 30, 100, 220)  # Default player car color
CYAN    = (  0, 220, 220)  # Shield visual and nitro flash
ORANGE  = (255, 140,   0)  # Nitro power-up and flame effect
SILVER  = (192, 192, 192)  # Silver coin, HUD labels
GOLD    = (255, 215,   0)  # Gold coin, #1 leaderboard rank
BRONZE  = (205, 127,  50)  # Bronze coin, #3 leaderboard rank
PURPLE  = (160,  32, 240)  # Purple car option
LIME    = (160, 240,  50)  # Distance display, HP bar (low)
PINK    = (255,  80, 180)  # Pink enemy car color

# Maps setting string → actual RGB color used when drawing the player car
CAR_COLOR_MAP = {
    "blue":   (30,  100, 220),
    "red":    (220,  30,  30),
    "green":  ( 30, 180,  30),
    "purple": (160,  32, 240),
    "orange": (255, 140,   0),
}

# ──────────────────────────────────────────────
# Road layout constants
# ──────────────────────────────────────────────
ROAD_LEFT  = 80    # X pixel where the road starts (left edge)
ROAD_RIGHT = 400   # X pixel where the road ends (right edge)
LANE_COUNT = 3     # Number of driving lanes

def lane_x(lane: int, car_width: int) -> int:
    """
    Converts a lane index (0, 1, 2) into a pixel X coordinate.
    Centers the car within the lane.
    """
    lane_width = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT  # Width of one lane in pixels
    return ROAD_LEFT + lane * lane_width + (lane_width - car_width) // 2

# ──────────────────────────────────────────────
# Gameplay tuning constants
# ──────────────────────────────────────────────
COINS_PER_SPEED_UP  = 5        # Every 5 coins collected → enemy speed increases by 1
DISTANCE_PER_FRAME  = 1        # How many virtual metres the player travels per frame
POWERUP_TIMEOUT     = 8_000    # Milliseconds before an uncollected power-up disappears
NITRO_DURATION      = 4_000    # Milliseconds the nitro boost lasts
NITRO_SPEED_BONUS   = 4        # Extra pixels/frame added to PLAYER movement during nitro
NITRO_SCROLL_BONUS  = 5        # Extra pixels/frame added to ALL objects scrolling (road speed)

# Difficulty presets: (enemy_spawn_ms, coin_spawn_ms, obstacle_spawn_ms, base_enemy_speed)
# Lower spawn_ms = objects appear more frequently = harder
DIFFICULTY_PRESETS = {
    "easy":   (2000, 1800, 3500, 3),  # Slow spawn, low starting speed
    "normal": (1500, 2000, 2500, 4),  # Balanced
    "hard":   (1000, 2200, 1600, 6),  # Fast spawn, high starting speed
}

# ──────────────────────────────────────────────
# Coin type definitions
# ──────────────────────────────────────────────
# Each type has: display label, score value, color, outline color, size, spawn weight
COIN_TYPES = [
    {"label": "B", "value": 1, "color": BRONZE, "outline": (139, 90,  43), "radius": 10, "weight": 60},  # Bronze — most common
    {"label": "S", "value": 3, "color": SILVER, "outline": (120, 120, 120), "radius": 12, "weight": 30},  # Silver — medium
    {"label": "G", "value": 5, "color": GOLD,   "outline": (180, 140,  0), "radius": 14, "weight": 10},  # Gold — rarest, most valuable
]

# Build a weighted pool: e.g. 60 bronze entries, 30 silver, 10 gold
# random.choice(COIN_POOL) automatically picks according to these weights
COIN_POOL = []
for _ct in COIN_TYPES:
    COIN_POOL.extend([_ct] * _ct["weight"])   # Repeat each type by its weight

# ──────────────────────────────────────────────
# Window, clock, fonts
# ──────────────────────────────────────────────
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Create the game window
pygame.display.set_caption("Racer  —  TSIS 3")                   # Title bar text
clock  = pygame.time.Clock()                                      # Used to cap FPS with clock.tick(FPS)

# Different font sizes for different UI purposes
font_large  = pygame.font.SysFont("Consolas", 38, bold=True)  # Titles (GAME OVER, menu)
font_medium = pygame.font.SysFont("Consolas", 24, bold=True)  # Score, buttons, labels
font_small  = pygame.font.SysFont("Consolas", 15)             # HUD info, leaderboard rows
font_tiny   = pygame.font.SysFont("Consolas", 12)             # Small labels on obstacles/coins



# PlayerCar  —  the car the user controls

class PlayerCar:
    WIDTH  = 50    # Car rectangle width in pixels
    HEIGHT = 80    # Car rectangle height in pixels
    SPEED  = 5     # Base movement speed in pixels per frame
    MAX_HP = 3     # Starting hit points

    def __init__(self, color=BLUE):
        self.base_color = color   # Color chosen in settings
        # Place the car centered horizontally, near the bottom of the screen
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2 - self.WIDTH // 2,
            SCREEN_HEIGHT - self.HEIGHT - 20,
            self.WIDTH, self.HEIGHT,
        )
        self.hp = self.MAX_HP        # Current health points

        # ── Power-up state flags ──
        self.shield_active = False   # True while shield power-up is active
        self.nitro_active  = False   # True while nitro boost is active
        self.nitro_end_ms  = 0       # Timestamp (ms) when nitro expires
        self.invincible_flash = 0    # Counts down frames of brief invincibility after a hit

    def move(self, keys, nitro_bonus=0):
        """Read arrow-key input and move the car; confined to road boundaries."""
        spd = self.SPEED + (NITRO_SPEED_BONUS if self.nitro_active else 0)  # Boost speed if nitro is on
        if keys[pygame.K_LEFT]  and self.rect.left   > ROAD_LEFT:     self.rect.x -= spd  # Move left
        if keys[pygame.K_RIGHT] and self.rect.right  < ROAD_RIGHT:    self.rect.x += spd  # Move right
        if keys[pygame.K_UP]    and self.rect.top    > 0:             self.rect.y -= spd  # Move up
        if keys[pygame.K_DOWN]  and self.rect.bottom < SCREEN_HEIGHT: self.rect.y += spd  # Move down

    def update(self, now_ms):
        """Called every frame to tick down time-limited effects."""
        if self.nitro_active and now_ms >= self.nitro_end_ms:
            self.nitro_active = False   # Nitro timer expired → deactivate
        if self.invincible_flash > 0:
            self.invincible_flash -= 1  # Count down 1 frame of invincibility

    def activate_nitro(self, now_ms):
        """Turn on nitro; records when it should expire."""
        self.nitro_active = True
        self.nitro_end_ms = now_ms + NITRO_DURATION  # Expiry = now + 4 seconds

    def activate_shield(self):
        """Turn on the shield; it absorbs the next collision."""
        self.shield_active = True

    def repair(self):
        """Restore HP to maximum (used by the repair power-up)."""
        self.hp = self.MAX_HP

    def take_damage(self, amount=1):
        """
        Apply 'amount' damage to the player.
        Returns True if the player dies (hp reaches 0).
        Invincibility frames and shield both block damage.
        """
        if self.invincible_flash > 0:
            return False                    # Still in post-hit invincibility window — no damage
        if self.shield_active:
            self.shield_active = False      # Shield absorbs the hit and breaks
            self.invincible_flash = 90      # Grant ~1.5 s of invincibility after shield break
            return False
        self.hp = max(0, self.hp - amount)
        self.invincible_flash = 90          # Brief invincibility so player isn't combo-killed
        return self.hp <= 0                 # True = player is dead

    # Kept for backward compatibility with enemy collision code
    def hit_by_obstacle(self):
        return self.take_damage(1)

    def draw(self, surface):
        """Render the car body, windshield, tail-lights, shield ring, and nitro flame."""
        color = self.base_color

        # Flash CYAN during nitro (alternates every 100 ms)
        if self.nitro_active and (pygame.time.get_ticks() // 100) % 2 == 0:
            color = CYAN

        # Flash WHITE during invincibility (alternates every 5 frames)
        if self.invincible_flash > 0 and (self.invincible_flash // 5) % 2 == 0:
            color = WHITE

        pygame.draw.rect(surface, color, self.rect, border_radius=8)   # Car body

        # Windshield (light blue rectangle near the top of the car)
        pygame.draw.rect(surface, (180, 220, 255),
                         (self.rect.x + 8, self.rect.y + 10, 34, 20), border_radius=4)

        # Left tail-light (red rectangle at the back of the car)
        pygame.draw.rect(surface, RED,
                         (self.rect.x + 5, self.rect.bottom - 12, 12, 8), border_radius=2)
        # Right tail-light
        pygame.draw.rect(surface, RED,
                         (self.rect.right - 17, self.rect.bottom - 12, 12, 8), border_radius=2)

        # Shield ring — drawn as a circle outline around the car
        if self.shield_active:
            pygame.draw.circle(surface, CYAN,
                                self.rect.center,
                                max(self.rect.width, self.rect.height) // 2 + 8, 3)

        # Nitro flame — two overlapping ellipses below the car (orange outer, yellow inner)
        if self.nitro_active:
            flame_rect = pygame.Rect(self.rect.x + 10, self.rect.bottom, 30, 18)
            pygame.draw.ellipse(surface, ORANGE, flame_rect)
            inner = pygame.Rect(self.rect.x + 16, self.rect.bottom + 2, 18, 10)
            pygame.draw.ellipse(surface, YELLOW, inner)



# EnemyCar  —  AI traffic cars that scroll down

class EnemyCar:
    WIDTH  = 50
    HEIGHT = 80
    COLORS = [RED, GREEN, ORANGE, PURPLE, PINK]   # Possible enemy car colors (random)

    def __init__(self, base_speed, player_rect=None):
        self.color = random.choice(self.COLORS)            # Pick a random color
        lane = self._safe_lane(player_rect)                # Choose a lane that avoids the player
        x    = lane_x(lane, self.WIDTH)                    # Convert lane index to pixel X
        # Spawn just above the visible screen (negative Y), with random extra offset
        self.rect  = pygame.Rect(x, -self.HEIGHT - random.randint(0, 60), self.WIDTH, self.HEIGHT)
        # Random speed variation ±1–2 pixels around base speed
        self.speed = max(2, base_speed + random.randint(-1, 2))

    def _safe_lane(self, player_rect):
        """
        Pick a random lane, trying not to spawn directly on the player's lane.
        Tries up to 6 times; if it can't avoid the player lane it just uses whatever it has.
        """
        lane = random.randint(0, LANE_COUNT - 1)
        if player_rect:
            # Determine which lane the player is currently in
            pl = (player_rect.centerx - ROAD_LEFT) // ((ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT)
            pl = max(0, min(LANE_COUNT - 1, pl))   # Clamp to valid range
            for _ in range(6):
                if lane != pl:
                    break
                lane = random.randint(0, LANE_COUNT - 1)  # Try a different lane
        return lane

    def update(self, extra=0):
        """Move the car downward every frame; 'extra' is the nitro scroll bonus."""
        self.rect.y += self.speed + extra

    def is_off_screen(self):
        """True when the car has scrolled below the bottom of the window."""
        return self.rect.top > SCREEN_HEIGHT

    def draw(self, surface):
        """Draw enemy car body, windshield, and yellow head-lights."""
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)   # Body
        # Windshield (greenish-white)
        pygame.draw.rect(surface, (200, 230, 200),
                         (self.rect.x + 8, self.rect.y + 10, 34, 20), border_radius=4)
        # Head-lights (yellow, at the bottom because car moves toward player)
        pygame.draw.rect(surface, YELLOW,
                         (self.rect.x + 5, self.rect.bottom - 12, 12, 8), border_radius=2)
        pygame.draw.rect(surface, YELLOW,
                         (self.rect.right - 17, self.rect.bottom - 12, 12, 8), border_radius=2)



# Coin  —  collectible items that fall down the road

class Coin:
    FALL_SPEED = 4   # Pixels per frame the coin moves downward

    def __init__(self):
        self.kind   = random.choice(COIN_POOL)   # Pick weighted random type (B/S/G)
        self.radius = self.kind["radius"]         # Display size depends on type
        self.value  = self.kind["value"]          # Score points: 1, 3, or 5
        x = random.randint(ROAD_LEFT + self.radius, ROAD_RIGHT - self.radius)  # Random X on road
        self.center = [x, -self.radius]           # Start above the screen
        # Rect is used for collision detection; kept in sync with center
        self.rect   = pygame.Rect(x - self.radius, -self.radius * 2,
                                   self.radius * 2, self.radius * 2)

    def update(self, extra=0):
        """Move coin down; 'extra' comes from nitro scroll bonus."""
        self.center[1] += self.FALL_SPEED + extra
        self.rect.center = (int(self.center[0]), int(self.center[1]))  # Sync rect with center

    def is_off_screen(self):
        return self.center[1] > SCREEN_HEIGHT + self.radius   # Below visible area

    def draw(self, surface):
        """Draw filled circle with outline and letter label (B / S / G)."""
        cx, cy = int(self.center[0]), int(self.center[1])
        pygame.draw.circle(surface, self.kind["color"],   (cx, cy), self.radius)        # Fill
        pygame.draw.circle(surface, self.kind["outline"], (cx, cy), self.radius, 2)     # Outline
        lbl = font_small.render(self.kind["label"], True, BLACK)
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))     # Centered label



# PowerUp  —  falling items that grant special abilities

# Visual definition for each power-up type
POWERUP_DEFS = {
    "nitro":  {"label": "N", "color": ORANGE, "outline": (200, 90,  0),  "radius": 14},  # Speed boost
    "shield": {"label": "S", "color": CYAN,   "outline": (  0, 160, 160),"radius": 14},  # Absorbs 1 hit
    "repair": {"label": "R", "color": LIME,   "outline": ( 80, 180,  0), "radius": 14},  # Restores full HP
}

class PowerUp:
    FALL_SPEED = 3   # Falls slower than coins so the player has time to react

    def __init__(self, kind: str, spawn_ms: int):
        self.kind      = kind        # "nitro", "shield", or "repair"
        self.spawn_ms  = spawn_ms    # Time of creation (used to check expiry)
        d = POWERUP_DEFS[kind]
        self.radius  = d["radius"]
        self.color   = d["color"]
        self.outline = d["outline"]
        self.label   = d["label"]
        x = random.randint(ROAD_LEFT + self.radius, ROAD_RIGHT - self.radius)
        self.center = [x, -self.radius]           # Start above the screen
        self.rect   = pygame.Rect(x - self.radius, -self.radius * 2,
                                   self.radius * 2, self.radius * 2)

    def update(self, extra=0):
        """Move power-up downward each frame."""
        self.center[1] += self.FALL_SPEED + extra
        self.rect.center = (int(self.center[0]), int(self.center[1]))

    def is_off_screen(self):
        return self.center[1] > SCREEN_HEIGHT + self.radius

    def is_expired(self, now_ms):
        """Returns True if the power-up has been on screen longer than POWERUP_TIMEOUT (8 s)."""
        return now_ms - self.spawn_ms > POWERUP_TIMEOUT

    def draw(self, surface, now_ms):
        """
        Draw the power-up circle.
        Blinks (skips drawing every other 200 ms) during the last 2 seconds before expiry.
        """
        cx, cy = int(self.center[0]), int(self.center[1])
        age = now_ms - self.spawn_ms
        # Blink warning: alternate visibility every 200 ms when close to expiry
        if age > POWERUP_TIMEOUT - 2000 and (now_ms // 200) % 2 == 0:
            return   # Skip draw on this frame = blinking effect
        pygame.draw.circle(surface, self.outline, (cx, cy), self.radius + 4, 2)  # Glow ring
        pygame.draw.circle(surface, self.color,   (cx, cy), self.radius)          # Filled body
        lbl = font_medium.render(self.label, True, BLACK)
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))



# Obstacle  —  road hazards that damage the player

OBSTACLE_TYPES = [
    {"kind": "hole",    "color": (30,  20,  10),  "w": 44, "h": 32, "damage": 1, "deadly": False},   # Pothole — 1 damage
    {"kind": "oil",     "color": (20,  20,  60),  "w": 50, "h": 22, "damage": 1, "deadly": False},   # Oil slick — 1 damage
    {"kind": "barrier", "color": (255, 200,  0),  "w": 60, "h": 18, "damage": 2, "deadly": False},   # Road barrier — 2 damage
]

class Obstacle:
    FALL_SPEED = 5   # Base downward speed (overridden by constructor)

    def __init__(self, base_speed, player_rect=None):
        self.kind_def = random.choice(OBSTACLE_TYPES)   # Randomly pick hole / oil / barrier
        w, h = self.kind_def["w"], self.kind_def["h"]
        lane = random.randint(0, LANE_COUNT - 1)
        # Try to avoid spawning directly on the player's current lane
        if player_rect:
            pl = (player_rect.centerx - ROAD_LEFT) // ((ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT)
            for _ in range(5):
                if lane != pl:
                    break
                lane = random.randint(0, LANE_COUNT - 1)
        lw   = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT
        x    = ROAD_LEFT + lane * lw + (lw - w) // 2   # Center obstacle in its lane
        # Spawn above screen with random extra gap so obstacles don't all appear at once
        self.rect  = pygame.Rect(x, -h - random.randint(0, 80), w, h)
        self.speed = max(2, base_speed + random.randint(0, 2))   # Slightly randomised speed

    def update(self, extra=0):
        """Scroll the obstacle downward."""
        self.rect.y += self.speed + extra

    def is_off_screen(self):
        return self.rect.top > SCREEN_HEIGHT

    def draw(self, surface):
        """Draw the correct visual for each obstacle type."""
        k    = self.kind_def["kind"]
        color = self.kind_def["color"]
        if k == "hole":
            # Dark ellipse to represent a pit in the road
            pygame.draw.ellipse(surface, color, self.rect)
            pygame.draw.ellipse(surface, (80, 60, 30), self.rect, 3)   # Brown rim
            lbl = font_tiny.render("HOLE", True, (160, 120, 60))
            surface.blit(lbl, (self.rect.centerx - lbl.get_width() // 2,
                                self.rect.centery - lbl.get_height() // 2))
        elif k == "oil":
            # Dark blue ellipse with a lighter inner shimmer
            pygame.draw.ellipse(surface, color, self.rect)
            shine = pygame.Rect(self.rect.x + 6, self.rect.y + 4, self.rect.w // 3, self.rect.h // 3)
            pygame.draw.ellipse(surface, (60, 60, 140), shine)    # Highlight shimmer
            pygame.draw.ellipse(surface, (0, 0, 100), self.rect, 2)
            lbl = font_tiny.render("OIL", True, (100, 100, 220))
            surface.blit(lbl, (self.rect.centerx - lbl.get_width() // 2,
                                self.rect.centery - lbl.get_height() // 2))
        else:  # barrier
            pygame.draw.rect(surface, color, self.rect, border_radius=4)    # Yellow body
            pygame.draw.rect(surface, RED, self.rect, 2, border_radius=4)   # Red outline
            lbl = font_tiny.render("STOP", True, RED)
            surface.blit(lbl, (self.rect.centerx - lbl.get_width() // 2,
                                self.rect.centery - lbl.get_height() // 2))



# NitroStrip  —  road strip that auto-activates nitro on contact

class NitroStrip:
    """
    A glowing 'N' circle that falls down the road.
    When the player drives over it, nitro is activated automatically.
    """
    RADIUS = 18   # Visual/collision radius in pixels
    SCROLL = 4    # Falls slightly slower than enemies for better visibility

    def __init__(self):
        lane = random.randint(0, LANE_COUNT - 1)
        lw   = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT
        cx   = ROAD_LEFT + lane * lw + lw // 2   # Center X of chosen lane
        self.center    = [cx, -self.RADIUS]       # Start above screen
        self.rect      = pygame.Rect(cx - self.RADIUS, -self.RADIUS * 2,
                                      self.RADIUS * 2, self.RADIUS * 2)
        self.triggered = False   # Prevents double-activation if collision check runs twice

    def update(self, extra=0):
        """Move the strip downward and keep rect in sync with center."""
        self.center[1] += self.SCROLL + extra
        self.rect.center = (int(self.center[0]), int(self.center[1]))

    def is_off_screen(self):
        return self.center[1] > SCREEN_HEIGHT + self.RADIUS

    def draw(self, surface):
        """Draw an animated orange/yellow glowing circle with an 'N' label."""
        cx, cy = int(self.center[0]), int(self.center[1])
        t = pygame.time.get_ticks()
        # Alternate between orange and deeper orange every 120 ms for pulsing animation
        outer_c = (255, 200, 0) if (t // 120) % 2 == 0 else (255, 120, 0)
        inner_c = (255, 240, 80)
        pygame.draw.circle(surface, outer_c, (cx, cy), self.RADIUS + 4, 3)  # Outer glow ring
        pygame.draw.circle(surface, outer_c, (cx, cy), self.RADIUS)          # Main fill
        pygame.draw.circle(surface, inner_c, (cx, cy), self.RADIUS - 5)      # Inner highlight
        lbl = font_medium.render("N", True, BLACK)
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))



# draw_road  —  renders the scrolling road background

def draw_road(surface, offset):
    """
    Draw the full road scene each frame.
    'offset' is the current scroll position (0–79 px), which shifts dashed lane lines
    downward to create the illusion the car is moving forward.
    """
    surface.fill((34, 120, 34))   # Green grass on both sides of the road

    # Grey road surface between ROAD_LEFT and ROAD_RIGHT
    pygame.draw.rect(surface, GRAY, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, SCREEN_HEIGHT))

    # Solid white left and right road edges
    pygame.draw.rect(surface, WHITE, (ROAD_LEFT,      0, 6, SCREEN_HEIGHT))
    pygame.draw.rect(surface, WHITE, (ROAD_RIGHT - 6, 0, 6, SCREEN_HEIGHT))

    # Dashed centre lane dividers; offset makes them scroll to simulate movement
    lane_width = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT
    for i in range(1, LANE_COUNT):
        lx = ROAD_LEFT + lane_width * i   # X position of this lane divider
        for y in range(-80 + offset % 80, SCREEN_HEIGHT, 80):
            pygame.draw.rect(surface, WHITE, (lx - 2, y, 4, 40))   # 40 px dash, 40 px gap



# draw_hud  —  renders the Heads-Up Display

def draw_hud(surface, score, coin_count, enemy_speed, coins_to_boost,
             distance, powerup_info=None, hp=3, max_hp=3):
    """
    Draw all on-screen game info:
    - Semi-transparent top bar: score, coins, speed, distance, boost countdown
    - Active power-up banner (name + seconds remaining)
    - HP bar at the bottom-left
    - Legend for coin values at the bottom-right
    """
    # Semi-transparent black bar using SRCALPHA surface (alpha=160)
    bar = pygame.Surface((SCREEN_WIDTH, 56), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 160))       # RGBA — 160/255 opacity
    surface.blit(bar, (0, 0))

    surface.blit(font_medium.render(f"Score: {score}", True, WHITE), (8, 6))           # Top-left: score
    coin_lbl = font_medium.render(f"C:{coin_count}", True, YELLOW)
    surface.blit(coin_lbl, (SCREEN_WIDTH - coin_lbl.get_width() - 8, 6))              # Top-right: coin total
    surface.blit(font_small.render(f"Boost in: {coins_to_boost}c", True, SILVER), (8, 34))  # Coins until next speed boost
    dist_lbl = font_small.render(f"{distance} m", True, LIME)
    surface.blit(dist_lbl, (SCREEN_WIDTH // 2 - dist_lbl.get_width() // 2, 34))       # Centre: distance
    spd = font_small.render(f"Spd:{enemy_speed}", True, SILVER)
    surface.blit(spd, (SCREEN_WIDTH - spd.get_width() - 8, 34))                       # Right: speed level

    # Show active power-up name and time remaining (in seconds)
    if powerup_info:
        name, ms_left = powerup_info
        secs = max(0, ms_left // 1000)   # Convert milliseconds to seconds
        colors = {"nitro": ORANGE, "shield": CYAN, "repair": LIME}
        c = colors.get(name, WHITE)
        pu_lbl = font_small.render(f"[{name.upper()} {secs}s]", True, c)
        surface.blit(pu_lbl, (SCREEN_WIDTH // 2 - pu_lbl.get_width() // 2, 6))

    # HP bar: filled rectangle whose width is proportional to current HP
    hp_bar_x, hp_bar_y = 8, SCREEN_HEIGHT - 36
    bar_w, bar_h = 120, 14
    pygame.draw.rect(surface, (60, 10, 10), (hp_bar_x, hp_bar_y, bar_w, bar_h), border_radius=4)  # Dark red background
    fill = int(bar_w * max(0, hp) / max_hp)   # How many pixels to fill based on HP ratio
    hp_color = GREEN if hp >= max_hp else (YELLOW if hp == 2 else RED)   # Color changes with HP level
    if fill > 0:
        pygame.draw.rect(surface, hp_color, (hp_bar_x, hp_bar_y, fill, bar_h), border_radius=4)
    pygame.draw.rect(surface, WHITE, (hp_bar_x, hp_bar_y, bar_w, bar_h), 1, border_radius=4)   # White outline
    hp_lbl = font_tiny.render(f"HP {hp}/{max_hp}", True, WHITE)
    surface.blit(hp_lbl, (hp_bar_x + bar_w + 6, hp_bar_y))   # "HP 2/3" text next to bar

    # Bottom-right legend explaining coin values
    leg = font_tiny.render("B=1  S=3  G=5 pts", True, SILVER)
    surface.blit(leg, (SCREEN_WIDTH - leg.get_width() - 8, SCREEN_HEIGHT - 18))



# game_over_screen  —  shown when the player dies

def game_over_screen(score, coin_count, distance):
    """
    Display final stats and wait for input.
    Returns: "retry" (R key), "menu" (M key), or exits (ESC).
    """
    while True:
        screen.fill((10, 10, 20))   # Very dark background
        _draw_centered(font_large,  "GAME OVER",             RED,    180)
        _draw_centered(font_medium, f"Score    : {score}",   WHITE,  255)
        _draw_centered(font_medium, f"Distance : {distance} m", LIME, 290)
        _draw_centered(font_medium, f"Coins    : {coin_count}", YELLOW, 325)
        _draw_centered(font_small,  "R — Retry    M — Main Menu    ESC — Quit", GRAY, 400)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:      return "retry"   # Restart immediately
                if event.key == pygame.K_m:      return "menu"    # Go to main menu
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()


def _draw_centered(font, text, color, y):
    """Helper: render text centred horizontally on the screen at a given Y position."""
    surf = font.render(text, True, color)
    screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))
"""
main.py  —  TSIS 3: Racer Game — Advanced Driving, Leaderboard & Power-Ups
Run:  python main.py
"""

import shutil, os

# Delete the bytecode cache so Python always reloads the latest source files
if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")

import pygame   # Core game library
import random   # Used for random coin/obstacle spawning probability
import sys      # sys.exit() for clean shutdown

# Import game objects, drawing helpers, and constants from racer module
from racer import (
    PlayerCar, EnemyCar, Coin, PowerUp, Obstacle, NitroStrip,
    draw_road, draw_hud, game_over_screen,
    screen, clock,
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    COINS_PER_SPEED_UP, DIFFICULTY_PRESETS, POWERUP_TIMEOUT,
    NITRO_DURATION, DISTANCE_PER_FRAME, NITRO_SCROLL_BONUS,
    CAR_COLOR_MAP, BLUE,
)
from persistence import load_settings, add_leaderboard_entry  # File I/O for settings & scores
from ui import main_menu, settings_screen, leaderboard_screen, username_screen  # Screen UIs
from sounds import SoundManager   # Manages all audio effects


def play(settings: dict):
    """
    Main gameplay loop.
    Receives the current settings dict and runs the game until the player crashes.
    Returns "retry" or "menu" based on what the player chose on the game-over screen.
    """
    # ── Load settings ──────────────────────────────────────
    diff   = settings.get("difficulty", "normal")
    # Unpack the 4 values for the chosen difficulty
    e_ms, c_ms, o_ms, base_spd = DIFFICULTY_PRESETS[diff]
    # e_ms = enemy spawn interval (ms), c_ms = coin spawn interval, o_ms = obstacle spawn interval

    car_color = CAR_COLOR_MAP.get(settings.get("car_color", "blue"), BLUE)  # Player car color
    username  = settings.get("username", "Player") or "Player"               # Name for leaderboard

    # ── Sound ──────────────────────────────────────────────
    sfx = SoundManager(enabled=settings.get("sound", False))  # Create audio manager (on/off)
    sfx.start_engine()   # Start looping engine sound

    # ── Game objects ───────────────────────────────────────
    player   = PlayerCar(color=car_color)  # The user-controlled car
    enemies  = []     # Active enemy cars on screen
    coins    = []     # Active coins on screen
    powerups = []     # Active power-ups on screen
    obstacles= []     # Active obstacles on screen
    strips   = []     # Active nitro strips on screen

    # ── State variables ────────────────────────────────────
    score        = 0    # Player's current score
    coin_count   = 0    # Total coins collected this run
    distance     = 0    # Virtual metres travelled
    road_offset  = 0    # Scroll offset (0–79 px) for animated lane dashes
    enemy_speed  = base_spd   # Current enemy scroll speed (increases over time)

    # ── Custom pygame timer events ──────────────────────────
    # Each event fires at a set interval to spawn a new object
    ENEMY_EV    = pygame.USEREVENT + 1   # Triggers enemy car spawn
    COIN_EV     = pygame.USEREVENT + 2   # Triggers coin spawn
    OBSTACLE_EV = pygame.USEREVENT + 3   # Triggers obstacle spawn
    STRIP_EV    = pygame.USEREVENT + 4   # Triggers nitro strip spawn
    POWERUP_EV  = pygame.USEREVENT + 5   # Triggers power-up spawn

    pygame.time.set_timer(ENEMY_EV,    e_ms)   # Set how often each event fires (ms)
    pygame.time.set_timer(COIN_EV,     c_ms)
    pygame.time.set_timer(OBSTACLE_EV, o_ms)
    pygame.time.set_timer(STRIP_EV,    5000)   # Nitro strips every 5 seconds
    pygame.time.set_timer(POWERUP_EV,  7000)   # Power-up every 7 seconds

    last_scale_dist = 0   # Tracks the last distance at which difficulty was scaled up

    def scale_difficulty():
        """Increase enemy speed and spawn rate every 500 metres."""
        nonlocal enemy_speed, e_ms, o_ms
        enemy_speed = min(enemy_speed + 1, 16)         # Cap speed at 16
        e_ms  = max(600,  int(e_ms  * 0.92))           # Reduce enemy spawn interval by 8% (min 600 ms)
        o_ms  = max(800,  int(o_ms  * 0.92))           # Reduce obstacle spawn interval by 8% (min 800 ms)
        pygame.time.set_timer(ENEMY_EV,    e_ms)       # Apply updated spawn intervals
        pygame.time.set_timer(OBSTACLE_EV, o_ms)
        sfx.set_engine_pitch(enemy_speed)              # Adjust engine sound volume with speed

    active_pu = None    # Name of currently active power-up (None = none active)
    pu_end_ms = 0       # Timestamp when current power-up expires

    # ══════════════════════════════════════════
    # MAIN GAME LOOP
    # ══════════════════════════════════════════
    while True:
        clock.tick(FPS)                       # Limit loop to 60 iterations per second
        now = pygame.time.get_ticks()         # Current time in milliseconds (from pygame start)

        # ── Event handling ─────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sfx.stop_all(); pygame.quit(); sys.exit()   # Close window → exit cleanly

            # Spawn objects based on timer events
            if event.type == ENEMY_EV:
                enemies.append(EnemyCar(enemy_speed, player.rect))   # New enemy in a random lane

            if event.type == COIN_EV:
                if random.random() < 0.7:   # 70% chance: skip some coin spawns for variety
                    coins.append(Coin())

            if event.type == OBSTACLE_EV:
                if random.random() < 0.65:  # 65% chance
                    obstacles.append(Obstacle(enemy_speed, player.rect))

            if event.type == STRIP_EV:
                if random.random() < 0.4:   # 40% chance: nitro strips are rare
                    strips.append(NitroStrip())

            if event.type == POWERUP_EV:
                if len(powerups) == 0:      # Only spawn if no power-up is already on screen
                    kind = random.choice(["nitro", "shield", "repair"])
                    powerups.append(PowerUp(kind, now))

        # ── Distance & difficulty scaling ──────
        distance += DISTANCE_PER_FRAME   # Accumulate virtual metres every frame
        if distance - last_scale_dist >= 500:   # Every 500 m → increase difficulty
            last_scale_dist = distance
            scale_difficulty()

        # ── Player input & state update ─────────
        keys = pygame.key.get_pressed()   # Read current keyboard state
        player.move(keys)                 # Apply arrow-key movement
        player.update(now)                # Tick nitro/invincibility timers

        # Extra scroll speed applied to all objects when nitro is active
        nitro_extra = NITRO_SCROLL_BONUS if player.nitro_active else 0

        # ── Scroll all on-screen objects ────────
        for e in enemies[:]:          # Iterate a copy so we can safely remove items
            e.update(nitro_extra)
            if e.is_off_screen():
                enemies.remove(e); score += 1   # +1 point for each enemy successfully dodged

        for c in coins[:]:
            c.update(nitro_extra)
            if c.is_off_screen(): coins.remove(c)   # Remove missed coins

        for o in obstacles[:]:
            o.update(nitro_extra)
            if o.is_off_screen(): obstacles.remove(o)

        for s in strips[:]:
            s.update(nitro_extra)
            if s.is_off_screen(): strips.remove(s)

        for p in powerups[:]:
            p.update(nitro_extra)
            # Remove if scrolled off screen OR expired after 8 seconds
            if p.is_off_screen() or p.is_expired(now):
                powerups.remove(p)

        # ── Nitro strip collision ───────────────
        for s in strips[:]:
            if not s.triggered and player.rect.colliderect(s.rect):
                s.triggered = True                       # Prevent duplicate activation
                player.activate_nitro(now)
                active_pu = "nitro"; pu_end_ms = now + NITRO_DURATION
                strips.remove(s)
                sfx.play("nitro")

        # ── Power-up collection ─────────────────
        for p in powerups[:]:
            if player.rect.colliderect(p.rect):   # Player touched the power-up
                powerups.remove(p)
                if p.kind == "nitro":
                    player.activate_nitro(now)
                    active_pu = "nitro"; pu_end_ms = now + NITRO_DURATION
                    sfx.play("nitro")
                elif p.kind == "shield":
                    player.activate_shield()
                    active_pu = "shield"; pu_end_ms = now + 999_999  # Shield lasts until hit
                    sfx.play("shield")
                elif p.kind == "repair":
                    player.repair()                              # Restore full HP
                    active_pu = "repair"; pu_end_ms = now + 800  # Brief banner display only
                    sfx.play("powerup")
                score += 10   # Bonus points for picking up any power-up

        # Clear active_pu display when the effect ends
        if active_pu == "nitro"  and not player.nitro_active:  active_pu = None
        if active_pu == "shield" and not player.shield_active: active_pu = None
        if active_pu == "repair" and now > pu_end_ms:          active_pu = None

        # ── Coin collection ─────────────────────
        for c in coins[:]:
            if player.rect.colliderect(c.rect):
                coins.remove(c)
                score      += c.value    # Add coin value to score
                coin_count += c.value    # Track total coins for leaderboard
                sfx.play("gold_coin" if c.value == 5 else "coin")   # Different sound for gold coins
                # Check if this coin pushed us over the next speed-up threshold
                if coin_count // COINS_PER_SPEED_UP > (coin_count - c.value) // COINS_PER_SPEED_UP:
                    enemy_speed = min(enemy_speed + 1, 16)
                    sfx.set_engine_pitch(enemy_speed)

        # ── Obstacle collision ──────────────────
        for o in obstacles[:]:
            if player.rect.colliderect(o.rect):
                dmg  = o.kind_def.get("damage", 1)   # 1 for hole/oil, 2 for barrier
                died = player.take_damage(dmg)        # Returns True if HP hits 0
                obstacles.remove(o)                   # Remove obstacle after collision
                if died:
                    sfx.play("crash"); sfx.stop_engine()
                    _draw_final_frame(player, enemies, coins, powerups, obstacles, strips,
                                      road_offset, score, coin_count, enemy_speed,
                                      _coins_to_boost(coin_count), distance,
                                      _pu_info(active_pu, pu_end_ms, now))
                    result = game_over_screen(score, coin_count, distance)
                    add_leaderboard_entry(username, score, distance, coin_count)  # Save to leaderboard
                    return result   # "retry" or "menu"
                else:
                    sfx.play("obstacle_hit")   # Survived hit — play lighter sound

        # ── Enemy collision ─────────────────────
        for e in enemies[:]:
            if player.rect.colliderect(e.rect):
                if player.shield_active:
                    # Shield absorbs the enemy hit — remove the enemy and break the shield
                    player.shield_active = False
                    player.invincible_flash = 90
                    enemies.remove(e)
                    sfx.play("shield")
                    break
                # No shield → instant death (enemies are more dangerous than obstacles)
                sfx.play("crash"); sfx.stop_engine()
                _draw_final_frame(player, enemies, coins, powerups, obstacles, strips,
                                  road_offset, score, coin_count, enemy_speed,
                                  _coins_to_boost(coin_count), distance,
                                  _pu_info(active_pu, pu_end_ms, now))
                result = game_over_screen(score, coin_count, distance)
                add_leaderboard_entry(username, score, distance, coin_count)
                return result

        # ── Scroll road background ──────────────
        # Advance offset by current speed; wrap at 80 px to loop the dashed lines
        road_offset = (road_offset + enemy_speed + nitro_extra) % 80

        # ── Draw everything ─────────────────────
        draw_road(screen, road_offset)             # Road + grass background
        for s in strips:    s.draw(screen)         # Nitro strips
        for o in obstacles: o.draw(screen)         # Road hazards
        for e in enemies:   e.draw(screen)         # Enemy cars
        for c in coins:     c.draw(screen)         # Coins
        for p in powerups:  p.draw(screen, now)    # Power-ups (need 'now' for blink logic)
        player.draw(screen)                        # Player car on top
        draw_hud(screen, score, coin_count, enemy_speed,
                 _coins_to_boost(coin_count), distance,
                 _pu_info(active_pu, pu_end_ms, now),
                 player.hp, player.MAX_HP)         # HUD overlay
        pygame.display.flip()                      # Push the rendered frame to the screen


# ── Helper: how many coins until the next speed boost ──
def _coins_to_boost(coin_count):
    """Returns remaining coins needed to trigger the next speed increase."""
    return COINS_PER_SPEED_UP - (coin_count % COINS_PER_SPEED_UP)

# ── Helper: package active power-up info for draw_hud ──
def _pu_info(active_pu, pu_end_ms, now):
    """Returns (name, ms_remaining) tuple or None if no power-up is active."""
    if active_pu is None: return None
    return (active_pu, max(0, pu_end_ms - now))

# ── Helper: draw one last frame before showing the game-over screen ──
def _draw_final_frame(player, enemies, coins, powerups, obstacles, strips,
                      road_offset, score, coin_count, enemy_speed,
                      coins_to_boost, distance, pu_info):
    """
    Renders the final game state (car in its crash position) so the
    game-over screen doesn't suddenly appear on a blank background.
    """
    draw_road(screen, road_offset)
    for s in strips:    s.draw(screen)
    for o in obstacles: o.draw(screen)
    for e in enemies:   e.draw(screen)
    for c in coins:     c.draw(screen)
    for p in powerups:  p.draw(screen, pygame.time.get_ticks())
    player.draw(screen)
    draw_hud(screen, score, coin_count, enemy_speed, coins_to_boost, distance, pu_info,
             player.hp, player.MAX_HP)
    pygame.display.flip()


def run():
    """
    Entry point: loads settings, shows the username screen once, then enters
    the main menu loop where the player can play, view the leaderboard, change
    settings, or quit.
    """
    settings = load_settings()              # Read saved settings from settings.json
    from persistence import save_settings

    # Ask for username every launch (pre-fills with the last saved name)
    settings["username"] = username_screen(settings.get("username", ""))
    save_settings(settings)   # Persist the (potentially updated) username

    # ── Main menu loop ──────────────────────
    while True:
        choice = main_menu()               # Show menu; returns the chosen option string

        if choice == "play":
            result = play(settings)        # Run the game; result is "retry" or "menu"
            if result == "retry":
                continue                  # Skip back to the top of the loop → play again

        elif choice == "leaderboard":
            leaderboard_screen()          # Show top-10 scores

        elif choice == "settings":
            settings = settings_screen()  # Let player change car/difficulty/sound
            if not settings.get("username"):
                # If username was cleared in settings, prompt again
                settings["username"] = username_screen()
                save_settings(settings)

        elif choice == "quit":
            pygame.quit(); sys.exit()     # Close window and terminate process


if __name__ == "__main__":
    run()   # Only runs if this file is executed directly (not imported)
"""
ball.py - Ball class for the Moving Ball Game
Encapsulates ball state, movement, and boundary checking.
"""

import pygame


class Ball:
    """
    A circular ball that moves in 4 directions and stays within
    the screen boundaries.

    Attributes:
        x, y    – current centre position
        radius  – ball radius (25 px → diameter 50 px)
        color   – RGB colour tuple
        speed   – pixels moved per key press
    """

    RADIUS = 25          # 50×50 ball → radius 25
    COLOR  = (220, 30, 30)   # red
    SPEED  = 20          # pixels per key press

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_w = screen_width
        self.screen_h = screen_height

        # Start in the centre of the screen
        self.x = screen_width  // 2
        self.y = screen_height // 2

    # ── Movement ──────────────────────────────────────────────────

    def move_up(self):
        """Move up by SPEED pixels; ignore if ball would leave screen."""
        new_y = self.y - self.SPEED
        if new_y - self.RADIUS >= 0:
            self.y = new_y

    def move_down(self):
        new_y = self.y + self.SPEED
        if new_y + self.RADIUS <= self.screen_h:
            self.y = new_y

    def move_left(self):
        new_x = self.x - self.SPEED
        if new_x - self.RADIUS >= 0:
            self.x = new_x

    def move_right(self):
        new_x = self.x + self.SPEED
        if new_x + self.RADIUS <= self.screen_w:
            self.x = new_x

    # ── Drawing ───────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        """Draw the ball (with a simple 3-D shading effect)."""
        # Shadow
        shadow_color = (180, 180, 180)
        pygame.draw.circle(surface, shadow_color,
                           (self.x + 4, self.y + 4), self.RADIUS)

        # Main body
        pygame.draw.circle(surface, self.COLOR,
                           (self.x, self.y), self.RADIUS)

        # Outline
        pygame.draw.circle(surface, (140, 0, 0),
                           (self.x, self.y), self.RADIUS, 2)

        # Highlight (small white dot, upper-left)
        highlight_x = self.x - self.RADIUS // 3
        highlight_y = self.y - self.RADIUS // 3
        pygame.draw.circle(surface, (255, 180, 180),
                           (highlight_x, highlight_y), self.RADIUS // 5)

    # ── Info ──────────────────────────────────────────────────────

    def get_position(self) -> tuple:
        return (self.x, self.y)
import pygame          # main library for creating the window, drawing, and handling input
import sys             # used to exit the program cleanly with sys.exit()
import math            # used for sqrt() and hypot() when drawing triangles and circles
from collections import deque   # deque = double-ended queue, used as BFS queue in flood-fill

# ──────────────────────────────────────────────
# Initialize pygame and its font module
# ──────────────────────────────────────────────
pygame.init()   # must be called before anything else in pygame

# ──────────────────────────────────────────────
# Screen layout constants
# ──────────────────────────────────────────────
SCREEN_W  = 900    # total window width in pixels
SCREEN_H  = 680    # total window height in pixels
TOOLBAR_H = 100    # how many pixels tall the top toolbar strip is

# ──────────────────────────────────────────────
# UI color constants (RGB tuples)
# ──────────────────────────────────────────────
BG_CANVAS   = (255, 255, 255)   # white — the drawing area background
BG_TOOLBAR  = ( 40,  40,  50)   # dark grey-blue — toolbar background
HIGHLIGHT   = ( 80, 140, 220)   # bright blue — shown on the active/selected button
BORDER_CLR  = (100, 100, 110)   # grey — border lines around buttons and swatches
TEXT_COLOR  = (220, 220, 220)   # light grey — text on buttons and labels

# ──────────────────────────────────────────────
# 18-colour palette (list of RGB tuples)
# Displayed as clickable swatches in the toolbar
# ──────────────────────────────────────────────
PALETTE = [
    (  0,   0,   0), (255, 255, 255), (128, 128, 128), (192, 192, 192),  # black, white, greys
    (255,   0,   0), (128,   0,   0), (255, 128,   0), (128,  64,   0),  # reds and oranges
    (255, 255,   0), (128, 128,   0), (  0, 255,   0), (  0, 128,   0),  # yellows and greens
    (  0, 255, 255), (  0, 128, 128), (  0,   0, 255), (  0,   0, 128),  # cyans and blues
    (255,   0, 255), (128,   0, 128),                                     # magentas/purples
]

# ──────────────────────────────────────────────
# Tool ID constants (strings used as identifiers)
# Compared against cur_tool in the event loop to decide what to draw
# ──────────────────────────────────────────────
TOOL_PEN      = "pen"        # freehand pencil — draws as you drag the mouse
TOOL_RECT     = "rect"       # rectangle outline — drag to define bounding box
TOOL_SQUARE   = "square"     # square — like rect but forces equal width and height
TOOL_CIRCLE   = "circle"     # circle — drag distance becomes the radius
TOOL_ERASER   = "eraser"     # eraser — paints white (background color) over drawn pixels
TOOL_RTRI     = "right_tri"  # right-angle triangle — corner at start point
TOOL_ETRI     = "equil_tri"  # equilateral triangle — all sides equal length
TOOL_RHOMBUS  = "rhombus"    # rhombus / diamond — vertices at midpoints of bounding box
TOOL_LINE     = "line"       # straight line with live preview while dragging
TOOL_FILL     = "fill"       # flood-fill — fills a region with the current color on click
TOOL_TEXT     = "text"       # text tool — click to place, type, press Enter to stamp

# ──────────────────────────────────────────────
# Brush size presets
# Three named levels selectable via toolbar buttons or keyboard keys 1/2/3
# ──────────────────────────────────────────────
SIZE_SMALL  = 2    # thin brush — keyboard shortcut: 1
SIZE_MEDIUM = 5    # medium brush — keyboard shortcut: 2
SIZE_LARGE  = 10   # thick brush — keyboard shortcut: 3
SIZE_LEVELS = [SIZE_SMALL, SIZE_MEDIUM, SIZE_LARGE]   # list used when building size buttons

# ──────────────────────────────────────────────
# Window, clock, fonts, and drawing canvas
# ──────────────────────────────────────────────
screen    = pygame.display.set_mode((SCREEN_W, SCREEN_H))   # create the OS window
pygame.display.set_caption("Paint — TSIS 2")                # window title bar text
clock     = pygame.time.Clock()                              # used to cap frame rate at 60 FPS
font      = pygame.font.SysFont("Arial", 13, bold=True)     # small bold font for toolbar labels
text_font = pygame.font.SysFont("Arial", 20)                # larger font for user-typed text on canvas

# canvas is a separate Surface (off-screen image) — drawings accumulate here between frames
# height = screen height minus toolbar so the canvas only occupies the drawing area
canvas = pygame.Surface((SCREEN_W, SCREEN_H - TOOLBAR_H))
canvas.fill(BG_CANVAS)   # start with a blank white canvas

# ──────────────────────────────────────────────
# Toolbar fixed-position Rects
# pygame.Rect(x, y, width, height) — defines a clickable/drawable area
# ──────────────────────────────────────────────
plus_rect  = pygame.Rect(385, 52, 28, 22)            # "+" button — increases brush size by 1
minus_rect = pygame.Rect(418, 52, 28, 22)            # "−" button — decreases brush size by 1
clear_rect = pygame.Rect(SCREEN_W - 80, 15, 70, 34)  # red "Clear" button — wipes the canvas

# S / M / L size preset buttons (each highlights when that size is active)
size_s_rect = pygame.Rect(385, 28, 28, 22)   # Small preset button  (2 px)
size_m_rect = pygame.Rect(418, 28, 28, 22)   # Medium preset button (5 px)
size_l_rect = pygame.Rect(451, 28, 28, 22)   # Large preset button  (10 px)


# ══════════════════════════════════════════════
# CLASS: ToolButton
# Each instance is one clickable button in the toolbar.
# ══════════════════════════════════════════════
class ToolButton:
    """A clickable button in the toolbar that activates a drawing tool."""

    def __init__(self, x, y, w, h, label, tool_id):
        self.rect    = pygame.Rect(x, y, w, h)   # bounding box for click detection and drawing
        self.label   = label     # string shown on the button face (e.g. "✏ Pen")
        self.tool_id = tool_id   # matches one of the TOOL_* constants above

    def draw(self, surface, active_tool):
        """Draw the button — blue if it is the active tool, dark grey otherwise."""
        color = HIGHLIGHT if self.tool_id == active_tool else BG_TOOLBAR   # pick fill color
        pygame.draw.rect(surface, color,      self.rect, border_radius=6)      # filled background
        pygame.draw.rect(surface, BORDER_CLR, self.rect, 1, border_radius=6)   # 1 px border
        lbl = font.render(self.label, True, TEXT_COLOR)   # render label text to a Surface
        # Center the text inside the button by offsetting by half its size
        surface.blit(lbl, (self.rect.centerx - lbl.get_width()  // 2,
                           self.rect.centery - lbl.get_height() // 2))

    def is_clicked(self, pos):
        """Return True if the mouse position (x, y) falls inside this button's rect."""
        return self.rect.collidepoint(pos)   # collidepoint checks if pos is inside the rect


# ══════════════════════════════════════════════
# FUNCTION: draw_toolbar
# Called every frame to redraw the entire toolbar area.
# ══════════════════════════════════════════════
def draw_toolbar(surface, tool_buttons, cur_tool, cur_color, cur_size, palette_rects):
    """
    Render all toolbar UI elements onto `surface`:
      - dark background strip
      - tool buttons (3 rows)
      - current colour preview square
      - brush size label + S/M/L buttons + +/- buttons
      - 18-colour palette swatches
      - red Clear button
      - Ctrl+S hint text
    """
    # Draw the dark background rectangle covering the entire toolbar area
    pygame.draw.rect(surface, BG_TOOLBAR, (0, 0, SCREEN_W, TOOLBAR_H))

    # Draw all tool buttons (each button checks internally whether to highlight itself)
    for btn in tool_buttons:
        btn.draw(surface, cur_tool)   # pass cur_tool so the active button knows to highlight

    # ── Current colour preview square ──────────────────────────────────────
    color_rect = pygame.Rect(330, 10, 44, 80)                            # position and size of preview box
    pygame.draw.rect(surface, cur_color,  color_rect, border_radius=4)  # filled with active colour
    pygame.draw.rect(surface, TEXT_COLOR, color_rect, 2, border_radius=4)  # white border around it

    # ── Brush size label and controls ──────────────────────────────────────
    surface.blit(font.render(f"Size:{cur_size}", True, TEXT_COLOR), (385, 10))   # e.g. "Size:5"

    # S / M / L buttons — highlight the one that matches the current size
    for rect, label, size_val in [
        (size_s_rect, "S", SIZE_SMALL),
        (size_m_rect, "M", SIZE_MEDIUM),
        (size_l_rect, "L", SIZE_LARGE),
    ]:
        btn_color = HIGHLIGHT if cur_size == size_val else BORDER_CLR   # blue if active, grey otherwise
        pygame.draw.rect(surface, btn_color, rect, border_radius=4)     # draw button background
        lbl = font.render(label, True, TEXT_COLOR)                      # render "S", "M", or "L"
        surface.blit(lbl, (rect.centerx - lbl.get_width() // 2,         # center text in button
                           rect.centery - lbl.get_height() // 2))

    # Fine ±1 adjustment buttons
    pygame.draw.rect(surface, BORDER_CLR, plus_rect,  border_radius=4)   # draw "+" button background
    pygame.draw.rect(surface, BORDER_CLR, minus_rect, border_radius=4)   # draw "−" button background
    surface.blit(font.render("+", True, TEXT_COLOR),
                 (plus_rect.centerx  - 4, plus_rect.centery  - 8))    # "+" label centered in button
    surface.blit(font.render("-", True, TEXT_COLOR),
                 (minus_rect.centerx - 4, minus_rect.centery - 8))    # "−" label centered in button

    # ── Colour palette swatches ────────────────────────────────────────────
    # 18 colours in a 9×2 grid; each swatch rect was pre-calculated in main()
    for idx, rect in enumerate(palette_rects):
        pygame.draw.rect(surface, PALETTE[idx], rect, border_radius=3)    # filled with that colour
        pygame.draw.rect(surface, BORDER_CLR,   rect, 1, border_radius=3) # thin grey border

    # ── Clear button ───────────────────────────────────────────────────────
    pygame.draw.rect(surface, (180, 40, 40), clear_rect, border_radius=6)   # red background
    surface.blit(font.render("Clear", True, TEXT_COLOR),
                 (clear_rect.centerx - 18, clear_rect.centery - 8))   # "Clear" label centered

    # ── Keyboard shortcut hint ─────────────────────────────────────────────
    surface.blit(font.render("Ctrl+S: Save PNG", True, (160, 160, 170)),
                 (SCREEN_W - 150, 60))   # dimmed hint text in bottom-right corner of toolbar


# ══════════════════════════════════════════════
# FUNCTION: to_canvas
# Translates screen coordinates → canvas-local coordinates.
# The canvas Surface starts at y = TOOLBAR_H on screen, so we subtract that offset.
# ══════════════════════════════════════════════
def to_canvas(x, y):
    """Convert a screen (x, y) position to the coordinate system of the canvas Surface."""
    return x, y - TOOLBAR_H   # x stays the same; y is shifted up by toolbar height


# ══════════════════════════════════════════════
# SHAPE DRAWING HELPERS
# Each function draws one shape onto `surface`.
# They work on both the real canvas and the temporary preview copy.
# `size` = line thickness in pixels.
# ══════════════════════════════════════════════

def draw_square(surface, color, start, end, size):
    """
    Draw a square starting at `start`.
    Side = min(|dx|, |dy|) so width always equals height.
    Drag direction is preserved so the square follows the cursor quadrant.
    """
    dx   = end[0] - start[0]           # horizontal distance dragged
    dy   = end[1] - start[1]           # vertical distance dragged
    side = min(abs(dx), abs(dy))        # use the shorter dimension as side length
    sx   = side if dx >= 0 else -side   # keep sign (direction) of horizontal drag
    sy   = side if dy >= 0 else -side   # keep sign (direction) of vertical drag
    rx   = min(start[0], start[0] + sx)  # top-left x of the square
    ry   = min(start[1], start[1] + sy)  # top-left y of the square
    pygame.draw.rect(surface, color, (rx, ry, side, side), size)   # draw square outline


def draw_right_triangle(surface, color, start, end, size):
    """
    Draw a right-angle triangle.
    A = start (right-angle corner), B = (end.x, start.y), C = (start.x, end.y).
    The right angle is always at the starting click point.
    """
    A = start                   # right-angle corner — where you clicked
    B = (end[0], start[1])      # horizontal corner — same y as A, x moved to end
    C = (start[0], end[1])      # vertical corner   — same x as A, y moved to end
    pygame.draw.polygon(surface, color, [A, B, C], size)   # draw triangle from 3 points


def draw_equilateral_triangle(surface, color, start, end, size):
    """
    Draw an equilateral triangle (all sides equal).
    Base goes from start to (end.x, start.y).
    Apex height = base * sqrt(3) / 2 — exact formula for equilateral triangle.
    Dragging up places apex above the base; dragging down places it below.
    """
    base_x1 = start[0]                  # left end of the base
    base_x2 = end[0]                    # right end of the base
    base_y  = start[1]                  # y-coordinate of the base (horizontal line)
    base    = abs(base_x2 - base_x1)   # length of the base in pixels

    if base == 0:
        return   # nothing to draw if the user didn't drag horizontally

    height = int(base * math.sqrt(3) / 2)   # exact height of an equilateral triangle

    # Apex goes up if dragged upward, down if dragged downward
    apex_y = base_y - height if end[1] <= start[1] else base_y + height
    apex_x = (base_x1 + base_x2) // 2   # apex is horizontally centred over the base

    A = (base_x1, base_y)   # left base corner
    B = (base_x2, base_y)   # right base corner
    C = (apex_x,  apex_y)   # apex (top or bottom)
    pygame.draw.polygon(surface, color, [A, B, C], size)   # draw the triangle


def draw_rhombus(surface, color, start, end, size):
    """
    Draw a rhombus (diamond) fitted inside the drag bounding box.
    Each vertex sits at the midpoint of one side of the bounding box.
    """
    cx = (start[0] + end[0]) // 2   # centre x of the bounding box
    cy = (start[1] + end[1]) // 2   # centre y of the bounding box

    top    = (cx,       start[1])   # midpoint of top edge
    right  = (end[0],   cy)         # midpoint of right edge
    bottom = (cx,       end[1])     # midpoint of bottom edge
    left   = (start[0], cy)         # midpoint of left edge

    pygame.draw.polygon(surface, color, [top, right, bottom, left], size)   # draw diamond


# ══════════════════════════════════════════════
# TOOL: Straight Line
# ══════════════════════════════════════════════

def draw_line(surface, color, start, end, size):
    """
    Draw a straight line from `start` to `end` with the given thickness.
    Used for the live preview (on a canvas copy) and the final committed stroke.
    max(1, size) ensures the line is at least 1 px wide.
    """
    pygame.draw.line(surface, color, start, end, max(1, size))


# ══════════════════════════════════════════════
# TOOL: Flood Fill (BFS algorithm)
# ══════════════════════════════════════════════

def flood_fill(surface, start_pos, fill_color):
    """
    Fill all connected pixels of the same color starting at `start_pos`.

    Algorithm — Breadth-First Search (BFS):
      1. Read the color of the clicked pixel → target_color.
      2. If it already equals fill_color, stop (nothing to do).
      3. Add the start pixel to a queue.
      4. While the queue is not empty:
           - Pop a pixel.
           - If its color still matches target_color, paint it fill_color.
           - Add its 4 neighbors (up/down/left/right) to the queue if not yet visited.
      5. When queue is empty, the entire connected region has been filled.

    surface.lock() / unlock() gives faster direct pixel access via get_at / set_at.
    """
    sx, sy = int(start_pos[0]), int(start_pos[1])   # start pixel coordinates (integer)
    w, h   = surface.get_size()                      # canvas width and height in pixels

    # Ignore clicks outside the canvas boundaries
    if sx < 0 or sy < 0 or sx >= w or sy >= h:
        return

    # get_at() returns RGBA; [:3] keeps only RGB to avoid alpha comparison issues
    target_color = surface.get_at((sx, sy))[:3]              # the color we want to replace
    fill_rgb     = fill_color[:3] if len(fill_color) > 3 else fill_color  # new color (RGB)

    if target_color == fill_rgb:   # already the correct color — nothing to do
        return

    surface.lock()   # lock the surface for faster pixel-level read/write operations

    queue   = deque()        # BFS queue — holds (x, y) pixel coordinates to process
    visited = set()          # set of already-queued pixels to avoid processing them twice
    queue.append((sx, sy))   # seed the queue with the starting pixel
    visited.add((sx, sy))    # mark the start pixel as visited immediately

    while queue:
        x, y = queue.popleft()   # take the next pixel from the front of the queue

        # Double-check color — a neighbor may have changed it already
        if surface.get_at((x, y))[:3] != target_color:
            continue

        surface.set_at((x, y), fill_rgb)   # paint this pixel with the fill color

        # Enqueue the 4 cardinal neighbors if they are in-bounds and not yet visited
        for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                if surface.get_at((nx, ny))[:3] == target_color:   # same color as original
                    visited.add((nx, ny))    # mark visited before adding to avoid duplicates
                    queue.append((nx, ny))   # schedule this neighbor for painting

    surface.unlock()   # release the surface lock — always required after surface.lock()


# ══════════════════════════════════════════════
# FEATURE: Save Canvas (Ctrl+S)
# ══════════════════════════════════════════════

def save_canvas(surface):
    """
    Save the canvas as a PNG file with a timestamp in the filename.
    The file is saved in the current working directory (same folder as the script).
    Returns the filename so the caller can display a confirmation banner.

    Example filename: canvas_2024-05-14_153022.png
    """
    from datetime import datetime   # datetime for generating a unique timestamp

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")   # e.g. "2024-05-14_153022"
    filename  = f"canvas_{timestamp}.png"                     # unique filename — never overwrites old saves
    pygame.image.save(surface, filename)                      # write Surface pixels to PNG in current folder
    print(f"[Save] Canvas saved as '{filename}'")             # confirmation printed to the terminal
    return filename   # return the filename so tools.py can show it in the on-screen banner
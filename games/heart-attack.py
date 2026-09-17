import pygame
import random
import math
import sys


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

WIDTH = 1000
HEIGHT = 700

FPS = 60

MIN_HEART_SIZE = 12
MAX_HEART_SIZE = 70

# How much a heart shrinks per click
SHRINK_AMOUNT = 10

# Hearts appear between these intervals
MIN_SPAWN_TIME = 1.0
MAX_SPAWN_TIME = 5.0

# Heart speed range
MIN_SPEED = 35
MAX_SPEED = 95

# Distance required between hearts when spawning
# The game will try to maximize distance regardless.
SPAWN_MARGIN = 10


# ------------------------------------------------------------
# Colors
# ------------------------------------------------------------

BACKGROUND = (20, 20, 35)
WHITE = (245, 245, 245)
GRAY = (150, 150, 160)
RED = (230, 60, 80)
PINK = (255, 100, 160)
PURPLE = (190, 80, 230)
ORANGE = (255, 140, 60)
YELLOW = (255, 210, 60)
CYAN = (60, 210, 230)
GREEN = (70, 210, 130)

HEART_COLORS = [
    RED,
    PINK,
    PURPLE,
    ORANGE,
    YELLOW,
    CYAN,
    GREEN,
]


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def distance(x1, y1, x2, y2):
    """Return distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def draw_heart(surface, x, y, size, color):
    """
    Draw a heart centered at x,y.

    The heart is constructed from:
      - two circles for the upper lobes
      - a polygon for the lower point
    """

    # Overall dimensions
    width = size * 2
    height = size * 2

    # Circle radius
    radius = size * 0.55

    # Centers of the two upper lobes
    left_x = x - size * 0.5
    right_x = x + size * 0.5
    top_y = y - size * 0.25

    pygame.draw.circle(
        surface,
        color,
        (int(left_x), int(top_y)),
        int(radius)
    )

    pygame.draw.circle(
        surface,
        color,
        (int(right_x), int(top_y)),
        int(radius)
    )

    # Bottom point
    points = [
        (x - size * 0.95, y - size * 0.05),
        (x + size * 0.95, y - size * 0.05),
        (x, y + size * 1.05),
    ]

    pygame.draw.polygon(surface, color, points)


def heart_radius(size):
    """
    Approximate collision/click radius of a heart.
    """
    return size * 0.95


# ------------------------------------------------------------
# Heart class
# ------------------------------------------------------------

class Heart:
    def __init__(self, x, y, size):

        self.x = x
        self.y = y

        self.size = size

        self.color = random.choice(HEART_COLORS)

        # Random movement angle
        angle = random.uniform(0, math.pi * 2)

        # Random speed
        speed = random.uniform(MIN_SPEED, MAX_SPEED)

        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    def update(self, dt):

        self.x += self.dx * dt
        self.y += self.dy * dt

        radius = heart_radius(self.size)

        # Bounce off left/right edges
        if self.x - radius <= 0:
            self.x = radius
            self.dx = abs(self.dx)

        elif self.x + radius >= WIDTH:
            self.x = WIDTH - radius
            self.dx = -abs(self.dx)

        # Bounce off top/bottom edges
        if self.y - radius <= 0:
            self.y = radius
            self.dy = abs(self.dy)

        elif self.y + radius >= HEIGHT:
            self.y = HEIGHT - radius
            self.dy = -abs(self.dy)

    # --------------------------------------------------------
    # Draw
    # --------------------------------------------------------

    def draw(self, surface):

        draw_heart(
            surface,
            self.x,
            self.y,
            self.size,
            self.color
        )

    # --------------------------------------------------------
    # Mouse hit detection
    # --------------------------------------------------------

    def contains_point(self, px, py):

        # First use a circular bounding area
        r = heart_radius(self.size)

        return distance(
            self.x,
            self.y,
            px,
            py
        ) <= r

    # --------------------------------------------------------
    # Shrink
    # --------------------------------------------------------

    def shrink(self):

        self.size -= SHRINK_AMOUNT

        return self.size <= MIN_HEART_SIZE

    # --------------------------------------------------------
    # Collision
    # --------------------------------------------------------

    def collides_with(self, other):

        r1 = heart_radius(self.size)
        r2 = heart_radius(other.size)

        d = distance(
            self.x,
            self.y,
            other.x,
            other.y
        )

        return d < r1 + r2


# ------------------------------------------------------------
# Find the best location for a new heart
# ------------------------------------------------------------

def find_best_spawn_location(hearts, size):

    radius = heart_radius(size)

    # If there are no hearts, choose a random position
    if not hearts:

        x = random.uniform(
            radius,
            WIDTH - radius
        )

        y = random.uniform(
            radius,
            HEIGHT - radius
        )

        return x, y

    # We don't just pick one random location.
    #
    # Instead, generate many candidate positions and choose
    # the one whose closest existing heart is farthest away.

    candidates = 150

    best_x = None
    best_y = None
    best_distance = -1

    for _ in range(candidates):

        x = random.uniform(
            radius + SPAWN_MARGIN,
            WIDTH - radius - SPAWN_MARGIN
        )

        y = random.uniform(
            radius + SPAWN_MARGIN,
            HEIGHT - radius - SPAWN_MARGIN
        )

        closest_distance = float("inf")

        for heart in hearts:

            d = distance(
                x,
                y,
                heart.x,
                heart.y
            )

            # Account for the sizes of both hearts
            d -= radius
            d -= heart_radius(heart.size)

            closest_distance = min(
                closest_distance,
                d
            )

        if closest_distance > best_distance:

            best_distance = closest_distance

            best_x = x
            best_y = y

    return best_x, best_y


# ------------------------------------------------------------
# Create a new heart
# ------------------------------------------------------------

def create_heart(hearts):

    size = random.uniform(
        MIN_HEART_SIZE + 15,
        MAX_HEART_SIZE
    )

    x, y = find_best_spawn_location(
        hearts,
        size
    )

    return Heart(
        x,
        y,
        size
    )


# ------------------------------------------------------------
# Draw text
# ------------------------------------------------------------

def draw_text(surface, text, font, x, y, color=WHITE):

    image = font.render(
        text,
        True,
        color
    )

    surface.blit(
        image,
        (x, y)
    )


# ------------------------------------------------------------
# Game
# ------------------------------------------------------------

def main():

    pygame.init()

    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT)
    )

    pygame.display.set_caption(
        "Heart Rush"
    )

    clock = pygame.time.Clock()

    # Fonts
    score_font = pygame.font.SysFont(
        "arial",
        32,
        bold=True
    )

    info_font = pygame.font.SysFont(
        "arial",
        20
    )

    game_over_font = pygame.font.SysFont(
        "arial",
        64,
        bold=True
    )

    restart_font = pygame.font.SysFont(
        "arial",
        28
    )

    # --------------------------------------------------------
    # Game state
    # --------------------------------------------------------

    hearts = []

    score = 0

    game_over = False

    # Time until next heart appears
    spawn_timer = random.uniform(
        MIN_SPAWN_TIME,
        MAX_SPAWN_TIME
    )

    # --------------------------------------------------------
    # Main loop
    # --------------------------------------------------------

    running = True

    while running:

        dt = clock.tick(FPS) / 1000.0

        # Limit very large time steps
        dt = min(dt, 0.05)

        # ----------------------------------------------------
        # Events
        # ----------------------------------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            # ------------------------------------------------
            # Mouse click
            # ------------------------------------------------

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1 and not game_over:

                    mouse_x, mouse_y = event.pos

                    # Check hearts from largest to smallest.
                    #
                    # This makes the larger heart easier to
                    # select if two hearts overlap visually.

                    clicked_heart = None

                    for heart in sorted(
                        hearts,
                        key=lambda h: h.size,
                        reverse=True
                    ):

                        if heart.contains_point(
                            mouse_x,
                            mouse_y
                        ):

                            clicked_heart = heart
                            break

                    if clicked_heart is not None:

                        score += 1

                        should_remove = clicked_heart.shrink()

                        if should_remove:

                            hearts.remove(
                                clicked_heart
                            )

            # ------------------------------------------------
            # Restart
            # ------------------------------------------------

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:

                    if game_over:

                        hearts.clear()

                        score = 0

                        game_over = False

                        spawn_timer = random.uniform(
                            MIN_SPAWN_TIME,
                            MAX_SPAWN_TIME
                        )

                elif event.key == pygame.K_ESCAPE:

                    running = False

        # ----------------------------------------------------
        # Game update
        # ----------------------------------------------------

        if not game_over:

            # ------------------------------------------------
            # Spawn timer
            # ------------------------------------------------

            spawn_timer -= dt

            if spawn_timer <= 0:

                hearts.append(
                    create_heart(hearts)
                )

                spawn_timer = random.uniform(
                    MIN_SPAWN_TIME,
                    MAX_SPAWN_TIME
                )

            # ------------------------------------------------
            # Update hearts
            # ------------------------------------------------

            for heart in hearts:

                heart.update(dt)

            # ------------------------------------------------
            # Check heart collisions
            # ------------------------------------------------

            collision_found = False

            for i in range(len(hearts)):

                for j in range(i + 1, len(hearts)):

                    if hearts[i].collides_with(
                        hearts[j]
                    ):

                        collision_found = True
                        break

                if collision_found:
                    break

            if collision_found:

                game_over = True

        # ----------------------------------------------------
        # Draw
        # ----------------------------------------------------

        screen.fill(BACKGROUND)

        # Draw hearts
        for heart in hearts:

            heart.draw(screen)

        # ----------------------------------------------------
        # HUD
        # ----------------------------------------------------

        draw_text(
            screen,
            f"Score: {score}",
            score_font,
            20,
            15
        )

        draw_text(
            screen,
            f"Hearts: {len(hearts)}",
            info_font,
            22,
            55,
            GRAY
        )

        if not game_over:

            draw_text(
                screen,
                "Click the hearts before they collide!",
                info_font,
                20,
                HEIGHT - 35,
                GRAY
            )

        # ----------------------------------------------------
        # Game over screen
        # ----------------------------------------------------

        if game_over:

            # Dark transparent overlay
            overlay = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 160)
            )

            screen.blit(
                overlay,
                (0, 0)
            )

            # Game over
            text = game_over_font.render(
                "GAME OVER",
                True,
                WHITE
            )

            text_rect = text.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 - 60)
            )

            screen.blit(
                text,
                text_rect
            )

            # Score
            score_text = restart_font.render(
                f"Final Score: {score}",
                True,
                WHITE
            )

            score_rect = score_text.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 + 10)
            )

            screen.blit(
                score_text,
                score_rect
            )

            # Restart
            restart_text = restart_font.render(
                "Press R to restart   |   ESC to quit",
                True,
                GRAY
            )

            restart_rect = restart_text.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 + 60)
            )

            screen.blit(
                restart_text,
                restart_rect
            )

        pygame.display.flip()

    pygame.quit()
    sys.exit()


# ------------------------------------------------------------
# Start game
# ------------------------------------------------------------

if __name__ == "__main__":
    main()

import pygame
import random
import math
import sys


# ============================================================
# CONFIGURATION
# ============================================================

WIDTH = 1000
HEIGHT = 700
FPS = 60

MIN_HEART_SIZE = 14
MAX_HEART_SIZE = 65

# How much a heart shrinks when it hits another heart
SHRINK_AMOUNT = 8

# Hearts appear randomly within this range
MIN_SPAWN_TIME = 1.0
MAX_SPAWN_TIME = 5.0

# Slower heart movement
MIN_SPEED = 35
MAX_SPEED = 95

# Minimum length of a wall
MIN_WALL_LENGTH = 10

# How long after a collision before the same pair can
# register another collision
COLLISION_COOLDOWN = 0.20


# ============================================================
# COLORS
# ============================================================

BACKGROUND = (18, 18, 32)
WHITE = (245, 245, 245)
GRAY = (150, 150, 165)
LIGHT_GRAY = (200, 200, 210)

WALL_COLOR = (100, 180, 255)
WALL_GLOW = (50, 110, 180)

RED = (235, 60, 80)
PINK = (255, 100, 165)
PURPLE = (190, 80, 235)
ORANGE = (255, 145, 60)
YELLOW = (255, 215, 65)
CYAN = (60, 215, 235)
GREEN = (70, 215, 130)

HEART_COLORS = [
    RED,
    PINK,
    PURPLE,
    ORANGE,
    YELLOW,
    CYAN,
    GREEN,
]


# ============================================================
# MATH HELPERS
# ============================================================

def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def closest_point_on_segment(px, py, x1, y1, x2, y2):
    """
    Find the point on line segment (x1,y1)-(x2,y2)
    that is closest to point (px,py).
    """

    dx = x2 - x1
    dy = y2 - y1

    length_squared = dx * dx + dy * dy

    if length_squared == 0:
        return x1, y1

    t = (
        (px - x1) * dx +
        (py - y1) * dy
    ) / length_squared

    t = max(0, min(1, t))

    return (
        x1 + t * dx,
        y1 + t * dy
    )


def reflect_velocity(vx, vy, nx, ny):
    """
    Reflect velocity vector across a surface whose
    normal is (nx, ny).
    """

    dot = vx * nx + vy * ny

    vx -= 2 * dot * nx
    vy -= 2 * dot * ny

    return vx, vy


# ============================================================
# HEART DRAWING
# ============================================================

def draw_heart(surface, x, y, size, color):
    """
    Draw a heart centered at x,y.
    """

    radius = size * 0.55

    left_x = x - size * 0.48
    right_x = x + size * 0.48

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

    points = [
        (
            int(x - size * 0.95),
            int(y - size * 0.02)
        ),
        (
            int(x + size * 0.95),
            int(y - size * 0.02)
        ),
        (
            int(x),
            int(y + size * 1.05)
        ),
    ]

    pygame.draw.polygon(
        surface,
        color,
        points
    )


def heart_radius(size):
    """
    Approximate the heart's collision radius.
    """
    return size * 0.90


# ============================================================
# HEART CLASS
# ============================================================

class Heart:

    def __init__(self, x, y, size):

        self.x = x
        self.y = y

        self.size = size

        self.color = random.choice(
            HEART_COLORS
        )

        # Random direction
        angle = random.uniform(
            0,
            math.pi * 2
        )

        speed = random.uniform(
            MIN_SPEED,
            MAX_SPEED
        )

        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

        # Prevent the heart from immediately colliding
        # with the same heart over and over.
        self.collision_timers = {}

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    def update(self, dt):

        self.x += self.dx * dt
        self.y += self.dy * dt

        # Reduce collision timers
        expired = []

        for other_id in self.collision_timers:

            self.collision_timers[other_id] -= dt

            if self.collision_timers[other_id] <= 0:
                expired.append(other_id)

        for other_id in expired:
            del self.collision_timers[other_id]

        self.bounce_off_screen()

    # --------------------------------------------------------
    # Screen edges
    # --------------------------------------------------------

    def bounce_off_screen(self):

        radius = heart_radius(
            self.size
        )

        # Left
        if self.x - radius < 0:

            self.x = radius

            if self.dx < 0:
                self.dx = -self.dx

        # Right
        elif self.x + radius > WIDTH:

            self.x = WIDTH - radius

            if self.dx > 0:
                self.dx = -self.dx

        # Top
        if self.y - radius < 0:

            self.y = radius

            if self.dy < 0:
                self.dy = -self.dy

        # Bottom
        elif self.y + radius > HEIGHT:

            self.y = HEIGHT - radius

            if self.dy > 0:
                self.dy = -self.dy

    # --------------------------------------------------------
    # Wall collision
    # --------------------------------------------------------

    def bounce_off_wall(self, wall):

        x1, y1, x2, y2 = wall

        closest_x, closest_y = closest_point_on_segment(
            self.x,
            self.y,
            x1,
            y1,
            x2,
            y2
        )

        dx = self.x - closest_x
        dy = self.y - closest_y

        dist = math.hypot(dx, dy)

        radius = heart_radius(
            self.size
        )

        if dist < radius:

            # If the center is exactly on the wall,
            # create a normal perpendicular to the wall.
            if dist < 0.0001:

                wall_dx = x2 - x1
                wall_dy = y2 - y1

                wall_length = math.hypot(
                    wall_dx,
                    wall_dy
                )

                if wall_length == 0:
                    return

                nx = -wall_dy / wall_length
                ny = wall_dx / wall_length

            else:

                nx = dx / dist
                ny = dy / dist

            # Only bounce if moving toward the wall
            velocity_toward_wall = (
                self.dx * nx +
                self.dy * ny
            )

            if velocity_toward_wall < 0:

                self.dx, self.dy = reflect_velocity(
                    self.dx,
                    self.dy,
                    nx,
                    ny
                )

            # Push the heart away from the wall
            overlap = radius - dist + 1

            self.x += nx * overlap
            self.y += ny * overlap

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


# ============================================================
# WALL DRAWING
# ============================================================

def draw_wall(surface, wall):

    x1, y1, x2, y2 = wall

    # Outer glow
    pygame.draw.line(
        surface,
        WALL_GLOW,
        (int(x1), int(y1)),
        (int(x2), int(y2)),
        8
    )

    # Main wall
    pygame.draw.line(
        surface,
        WALL_COLOR,
        (int(x1), int(y1)),
        (int(x2), int(y2)),
        3
    )

    # End caps
    pygame.draw.circle(
        surface,
        WHITE,
        (int(x1), int(y1)),
        4
    )

    pygame.draw.circle(
        surface,
        WHITE,
        (int(x2), int(y2)),
        4
    )


# ============================================================
# FIND BEST HEART SPAWN LOCATION
# ============================================================

def find_best_spawn_location(
    hearts,
    size
):

    radius = heart_radius(size)

    # No hearts yet
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

    # Try many candidate locations and choose the one
    # that is farthest from the nearest existing heart.

    best_x = None
    best_y = None
    best_distance = -float("inf")

    for _ in range(150):

        x = random.uniform(
            radius + 10,
            WIDTH - radius - 10
        )

        y = random.uniform(
            radius + 10,
            HEIGHT - radius - 10
        )

        closest = float("inf")

        for heart in hearts:

            d = distance(
                x,
                y,
                heart.x,
                heart.y
            )

            d -= radius
            d -= heart_radius(
                heart.size
            )

            closest = min(
                closest,
                d
            )

        if closest > best_distance:

            best_distance = closest

            best_x = x
            best_y = y

    return best_x, best_y


# ============================================================
# CREATE HEART
# ============================================================

def create_heart(hearts):

    size = random.uniform(
        MIN_HEART_SIZE + 10,
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


# ============================================================
# HEART-HEART COLLISION
# ============================================================

def handle_heart_collision(
    heart1,
    heart2
):
    """
    Make two hearts bounce apart and shrink.

    Returns True if this was a new collision.
    """

    id1 = id(heart1)
    id2 = id(heart2)

    # Don't repeatedly count the same collision
    # while the hearts are still touching.
    if id2 in heart1.collision_timers:
        return False

    # Vector from heart1 to heart2
    dx = heart2.x - heart1.x
    dy = heart2.y - heart1.y

    dist = math.hypot(dx, dy)

    if dist == 0:

        angle = random.uniform(
            0,
            math.pi * 2
        )

        nx = math.cos(angle)
        ny = math.sin(angle)

        dist = 0.001

    else:

        nx = dx / dist
        ny = dy / dist

    # Relative velocity
    relative_velocity = (
        (heart2.dx - heart1.dx) * nx +
        (heart2.dy - heart1.dy) * ny
    )

    # If they are moving toward one another,
    # perform an elastic-style collision.
    if relative_velocity < 0:

        # Project velocities onto collision normal
        v1 = heart1.dx * nx + heart1.dy * ny
        v2 = heart2.dx * nx + heart2.dy * ny

        # Equal-mass elastic collision:
        # swap the normal components.
        heart1.dx += (v2 - v1) * nx
        heart1.dy += (v2 - v1) * ny

        heart2.dx += (v1 - v2) * nx
        heart2.dy += (v1 - v2) * ny

    # Push them apart so they don't remain overlapping
    combined_radius = (
        heart_radius(heart1.size) +
        heart_radius(heart2.size)
    )

    overlap = combined_radius - dist

    if overlap > 0:

        push = overlap / 2 + 1

        heart1.x -= nx * push
        heart1.y -= ny * push

        heart2.x += nx * push
        heart2.y += ny * push

    # Shrink both hearts
    heart1.size -= SHRINK_AMOUNT
    heart2.size -= SHRINK_AMOUNT

    # Set collision cooldown
    heart1.collision_timers[id2] = COLLISION_COOLDOWN
    heart2.collision_timers[id1] = COLLISION_COOLDOWN

    return True


# ============================================================
# TEXT
# ============================================================

def draw_text(
    surface,
    text,
    font,
    x,
    y,
    color=WHITE
):

    image = font.render(
        text,
        True,
        color
    )

    surface.blit(
        image,
        (x, y)
    )


# ============================================================
# MAIN GAME
# ============================================================

def main():

    pygame.init()

    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT)
    )

    pygame.display.set_caption(
        "Heart Bounce"
    )

    clock = pygame.time.Clock()

    # --------------------------------------------------------
    # Fonts
    # --------------------------------------------------------

    score_font = pygame.font.SysFont(
        "arial",
        30,
        bold=True
    )

    rate_font = pygame.font.SysFont(
        "arial",
        38,
        bold=True
    )

    info_font = pygame.font.SysFont(
        "arial",
        19
    )

    small_font = pygame.font.SysFont(
        "arial",
        17
    )

    # --------------------------------------------------------
    # Game state
    # --------------------------------------------------------

    hearts = []

    walls = []

    score = 0

    start_time = pygame.time.get_ticks()

    spawn_timer = random.uniform(
        MIN_SPAWN_TIME,
        MAX_SPAWN_TIME
    )

    # Mouse drawing state
    drawing_wall = False

    wall_start = None
    wall_current = None

    running = True

    while running:

        dt = clock.tick(FPS) / 1000.0

        dt = min(
            dt,
            0.05
        )

        # ====================================================
        # EVENTS
        # ====================================================

        for event in pygame.event.get():

            # ------------------------------------------------
            # Quit
            # ------------------------------------------------

            if event.type == pygame.QUIT:

                running = False

            # ------------------------------------------------
            # Left mouse button
            # ------------------------------------------------

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    drawing_wall = True

                    wall_start = event.pos

                    wall_current = event.pos

                # Right-click clears all walls
                elif event.button == 3:

                    walls.clear()

            # ------------------------------------------------
            # Mouse movement
            # ------------------------------------------------

            elif event.type == pygame.MOUSEMOTION:

                if drawing_wall:

                    wall_current = event.pos

            # ------------------------------------------------
            # Mouse button released
            # ------------------------------------------------

            elif event.type == pygame.MOUSEBUTTONUP:

                if event.button == 1 and drawing_wall:

                    drawing_wall = False

                    end = event.pos

                    x1, y1 = wall_start
                    x2, y2 = end

                    length = distance(
                        x1,
                        y1,
                        x2,
                        y2
                    )

                    if length >= MIN_WALL_LENGTH:

                        walls.append(
                            (
                                x1,
                                y1,
                                x2,
                                y2
                            )
                        )

                    wall_start = None
                    wall_current = None

            # ------------------------------------------------
            # Keyboard
            # ------------------------------------------------

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    running = False

                elif event.key == pygame.K_r:

                    # Restart
                    hearts.clear()

                    walls.clear()

                    score = 0

                    start_time = pygame.time.get_ticks()

                    spawn_timer = random.uniform(
                        MIN_SPAWN_TIME,
                        MAX_SPAWN_TIME
                    )

        # ====================================================
        # SPAWN HEARTS
        # ====================================================

        spawn_timer -= dt

        if spawn_timer <= 0:

            hearts.append(
                create_heart(hearts)
            )

            spawn_timer = random.uniform(
                MIN_SPAWN_TIME,
                MAX_SPAWN_TIME
            )

        # ====================================================
        # UPDATE HEARTS
        # ====================================================

        for heart in hearts:

            heart.update(dt)

            # Bounce off every wall
            for wall in walls:

                heart.bounce_off_wall(
                    wall
                )

        # ====================================================
        # HEART-HEART COLLISIONS
        # ====================================================

        hearts_to_remove = []

        for i in range(len(hearts)):

            for j in range(i + 1, len(hearts)):

                heart1 = hearts[i]
                heart2 = hearts[j]

                r1 = heart_radius(
                    heart1.size
                )

                r2 = heart_radius(
                    heart2.size
                )

                d = distance(
                    heart1.x,
                    heart1.y,
                    heart2.x,
                    heart2.y
                )

                if d < r1 + r2:

                    collision = handle_heart_collision(
                        heart1,
                        heart2
                    )

                    if collision:

                        # Each heart that gets hit counts.
                        score += 2

                        # Remove hearts that have become tiny.
                        if heart1.size <= MIN_HEART_SIZE:
                            hearts_to_remove.append(
                                heart1
                            )

                        if heart2.size <= MIN_HEART_SIZE:
                            hearts_to_remove.append(
                                heart2
                            )

        # Remove dead hearts
        for heart in hearts_to_remove:

            if heart in hearts:

                hearts.remove(
                    heart
                )

        # ====================================================
        # HEART-HITS PER MINUTE
        # ====================================================

        elapsed_seconds = (
            pygame.time.get_ticks()
            - start_time
        ) / 1000.0

        if elapsed_seconds > 0:

            hits_per_minute = (
                score /
                elapsed_seconds *
                60
            )

        else:

            hits_per_minute = 0

        # ====================================================
        # DRAW
        # ====================================================

        screen.fill(
            BACKGROUND
        )

        # ----------------------------------------------------
        # Draw walls
        # ----------------------------------------------------

        for wall in walls:

            draw_wall(
                screen,
                wall
            )

        # ----------------------------------------------------
        # Draw wall currently being created
        # ----------------------------------------------------

        if (
            drawing_wall
            and wall_start is not None
            and wall_current is not None
        ):

            pygame.draw.line(
                screen,
                LIGHT_GRAY,
                wall_start,
                wall_current,
                3
            )

            pygame.draw.circle(
                screen,
                WHITE,
                wall_start,
                4
            )

            pygame.draw.circle(
                screen,
                WHITE,
                wall_current,
                4
            )

        # ----------------------------------------------------
        # Draw hearts
        # ----------------------------------------------------

        for heart in hearts:

            heart.draw(
                screen
            )

        # ====================================================
        # HUD
        # ====================================================

        draw_text(
            screen,
            f"Heart Hits: {score}",
            score_font,
            20,
            15
        )

        # Make hits/minute the prominent statistic
        draw_text(
            screen,
            f"{hits_per_minute:.1f} HITS / MINUTE",
            rate_font,
            20,
            55
        )

        draw_text(
            screen,
            f"Hearts: {len(hearts)}",
            info_font,
            22,
            105,
            GRAY
        )

        # Instructions
        draw_text(
            screen,
            "Drag the mouse to build walls",
            small_font,
            20,
            HEIGHT - 65,
            GRAY
        )

        draw_text(
            screen,
            "Right-click: clear walls    R: restart    ESC: quit",
            small_font,
            20,
            HEIGHT - 38,
            GRAY
        )

        pygame.display.flip()

    # ========================================================
    # SHUTDOWN
    # ========================================================

    pygame.quit()

    sys.exit()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()


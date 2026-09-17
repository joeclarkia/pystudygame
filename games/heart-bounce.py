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

# Exactly one heart every 4 seconds
SPAWN_INTERVAL = 4.0

# Never allow more than this many hearts
MAX_HEARTS = 10

# Slower heart movement
MIN_SPEED = 35
MAX_SPEED = 95

# Minimum distance the mouse must move before a new
# free-form wall segment is added
MIN_WALL_POINT_DISTANCE = 5

# Minimum wall length before it is kept
MIN_WALL_LENGTH = 10

# Width of the clickable area around a wall
WALL_CLICK_DISTANCE = 10

# Prevent the same two hearts from registering
# repeated collisions while still touching
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
    return math.hypot(
        x2 - x1,
        y2 - y1
    )


def closest_point_on_segment(
    px,
    py,
    x1,
    y1,
    x2,
    y2
):
    """
    Find the point on line segment (x1,y1)-(x2,y2)
    closest to point (px,py).
    """

    dx = x2 - x1
    dy = y2 - y1

    length_squared = (
        dx * dx +
        dy * dy
    )

    if length_squared == 0:
        return x1, y1

    t = (
        (px - x1) * dx +
        (py - y1) * dy
    ) / length_squared

    t = max(
        0,
        min(1, t)
    )

    return (
        x1 + t * dx,
        y1 + t * dy
    )


def reflect_velocity(
    vx,
    vy,
    nx,
    ny
):
    """
    Reflect velocity across a surface whose
    normal vector is nx,ny.
    """

    dot = (
        vx * nx +
        vy * ny
    )

    vx -= 2 * dot * nx
    vy -= 2 * dot * ny

    return vx, vy


# ============================================================
# HEART DRAWING
# ============================================================

def draw_heart(
    surface,
    x,
    y,
    size,
    color
):
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
        (
            int(left_x),
            int(top_y)
        ),
        int(radius)
    )

    pygame.draw.circle(
        surface,
        color,
        (
            int(right_x),
            int(top_y)
        ),
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
    return size * 0.90


# ============================================================
# HEART CLASS
# ============================================================

class Heart:

    def __init__(
        self,
        x,
        y,
        size
    ):

        self.x = x
        self.y = y

        self.size = size

        self.color = random.choice(
            HEART_COLORS
        )

        angle = random.uniform(
            0,
            math.pi * 2
        )

        speed = random.uniform(
            MIN_SPEED,
            MAX_SPEED
        )

        self.dx = (
            math.cos(angle) *
            speed
        )

        self.dy = (
            math.sin(angle) *
            speed
        )

        # Dictionary of other-heart IDs and their
        # collision cooldowns.
        self.collision_timers = {}

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    def update(self, dt):

        self.x += self.dx * dt
        self.y += self.dy * dt

        # Update collision cooldowns
        expired = []

        for other_id in self.collision_timers:

            self.collision_timers[
                other_id
            ] -= dt

            if (
                self.collision_timers[
                    other_id
                ] <= 0
            ):
                expired.append(
                    other_id
                )

        for other_id in expired:

            del self.collision_timers[
                other_id
            ]

        self.bounce_off_screen()

    # --------------------------------------------------------
    # Screen edge bouncing
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

    def bounce_off_wall(
        self,
        wall_segment
    ):
        """
        Bounce off one segment of a free-form wall.
        """

        x1, y1, x2, y2 = wall_segment

        closest_x, closest_y = (
            closest_point_on_segment(
                self.x,
                self.y,
                x1,
                y1,
                x2,
                y2
            )
        )

        dx = self.x - closest_x
        dy = self.y - closest_y

        dist = math.hypot(
            dx,
            dy
        )

        radius = heart_radius(
            self.size
        )

        if dist < radius:

            # If the center is exactly on the wall,
            # use a perpendicular wall normal.
            if dist < 0.0001:

                wall_dx = x2 - x1
                wall_dy = y2 - y1

                wall_length = math.hypot(
                    wall_dx,
                    wall_dy
                )

                if wall_length == 0:
                    return

                nx = (
                    -wall_dy /
                    wall_length
                )

                ny = (
                    wall_dx /
                    wall_length
                )

            else:

                nx = dx / dist
                ny = dy / dist

            # Only bounce when moving toward wall
            velocity_toward_wall = (
                self.dx * nx +
                self.dy * ny
            )

            if velocity_toward_wall < 0:

                self.dx, self.dy = (
                    reflect_velocity(
                        self.dx,
                        self.dy,
                        nx,
                        ny
                    )
                )

            # Push the heart away from the wall
            overlap = (
                radius -
                dist +
                1
            )

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
# WALL CLASS
# ============================================================

class Wall:

    def __init__(self):

        # List of (x,y) points making up the free-form path
        self.points = []

    # --------------------------------------------------------
    # Add point
    # --------------------------------------------------------

    def add_point(
        self,
        x,
        y
    ):

        if not self.points:

            self.points.append(
                (x, y)
            )

            return

        last_x, last_y = (
            self.points[-1]
        )

        if distance(
            last_x,
            last_y,
            x,
            y
        ) >= MIN_WALL_POINT_DISTANCE:

            self.points.append(
                (x, y)
            )

    # --------------------------------------------------------
    # Get line segments
    # --------------------------------------------------------

    def segments(self):

        result = []

        for i in range(
            len(self.points) - 1
        ):

            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]

            result.append(
                (
                    x1,
                    y1,
                    x2,
                    y2
                )
            )

        return result

    # --------------------------------------------------------
    # Draw
    # --------------------------------------------------------

    def draw(
        self,
        surface
    ):

        if len(self.points) < 2:
            return

        # Glow
        pygame.draw.lines(
            surface,
            WALL_GLOW,
            False,
            self.points,
            9
        )

        # Main wall
        pygame.draw.lines(
            surface,
            WALL_COLOR,
            False,
            self.points,
            4
        )

        # Draw small bright points at the ends
        pygame.draw.circle(
            surface,
            WHITE,
            (
                int(self.points[0][0]),
                int(self.points[0][1])
            ),
            4
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (
                int(self.points[-1][0]),
                int(self.points[-1][1])
            ),
            4
        )

    # --------------------------------------------------------
    # Is mouse near wall?
    # --------------------------------------------------------

    def contains_point(
        self,
        px,
        py
    ):
        """
        Returns True if the mouse is close enough
        to any segment of the wall to delete it.
        """

        for (
            x1,
            y1,
            x2,
            y2
        ) in self.segments():

            closest_x, closest_y = (
                closest_point_on_segment(
                    px,
                    py,
                    x1,
                    y1,
                    x2,
                    y2
                )
            )

            if distance(
                px,
                py,
                closest_x,
                closest_y
            ) <= WALL_CLICK_DISTANCE:

                return True

        return False


# ============================================================
# FIND BEST HEART SPAWN LOCATION
# ============================================================

def find_best_spawn_location(
    hearts,
    size
):

    radius = heart_radius(
        size
    )

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

    best_x = None
    best_y = None

    best_distance = (
        -float("inf")
    )

    # Test many candidate locations
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

    return (
        best_x,
        best_y
    )


# ============================================================
# CREATE HEART
# ============================================================

def create_heart(
    hearts
):

    size = random.uniform(
        MIN_HEART_SIZE + 10,
        MAX_HEART_SIZE
    )

    x, y = (
        find_best_spawn_location(
            hearts,
            size
        )
    )

    return Heart(
        x,
        y,
        size
    )


# ============================================================
# HEART COLLISION
# ============================================================

def handle_heart_collision(
    heart1,
    heart2
):
    """
    Bounce two hearts apart and shrink both.
    Returns True if this is a new collision.
    """

    id1 = id(heart1)
    id2 = id(heart2)

    # Collision already registered recently
    if id2 in heart1.collision_timers:

        return False

    dx = heart2.x - heart1.x
    dy = heart2.y - heart1.y

    dist = math.hypot(
        dx,
        dy
    )

    if dist < 0.0001:

        angle = random.uniform(
            0,
            math.pi * 2
        )

        nx = math.cos(angle)
        ny = math.sin(angle)

        dist = 0.0001

    else:

        nx = dx / dist
        ny = dy / dist

    # Relative velocity along collision normal
    relative_velocity = (
        (heart2.dx - heart1.dx) * nx +
        (heart2.dy - heart1.dy) * ny
    )

    if relative_velocity < 0:

        v1 = (
            heart1.dx * nx +
            heart1.dy * ny
        )

        v2 = (
            heart2.dx * nx +
            heart2.dy * ny
        )

        # Equal-mass elastic collision
        heart1.dx += (
            v2 - v1
        ) * nx

        heart1.dy += (
            v2 - v1
        ) * ny

        heart2.dx += (
            v1 - v2
        ) * nx

        heart2.dy += (
            v1 - v2
        ) * ny

    # Push hearts apart
    combined_radius = (
        heart_radius(
            heart1.size
        ) +
        heart_radius(
            heart2.size
        )
    )

    overlap = (
        combined_radius -
        dist
    )

    if overlap > 0:

        push = (
            overlap / 2 +
            1
        )

        heart1.x -= (
            nx * push
        )

        heart1.y -= (
            ny * push
        )

        heart2.x += (
            nx * push
        )

        heart2.y += (
            ny * push
        )

    # Shrink both
    heart1.size -= SHRINK_AMOUNT
    heart2.size -= SHRINK_AMOUNT

    # Cooldown
    heart1.collision_timers[
        id2
    ] = COLLISION_COOLDOWN

    heart2.collision_timers[
        id1
    ] = COLLISION_COOLDOWN

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
# MAIN
# ============================================================

def main():

    pygame.init()

    screen = pygame.display.set_mode(
        (
            WIDTH,
            HEIGHT
        )
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

    start_time = (
        pygame.time.get_ticks()
    )

    # First heart appears after 4 seconds
    spawn_timer = SPAWN_INTERVAL

    # Free-form wall currently being drawn
    drawing_wall = False

    current_wall = None

    running = True

    # ========================================================
    # GAME LOOP
    # ========================================================

    while running:

        dt = (
            clock.tick(FPS) /
            1000.0
        )

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
            # Mouse button down
            # ------------------------------------------------

            elif (
                event.type ==
                pygame.MOUSEBUTTONDOWN
            ):

                # --------------------------------------------
                # LEFT CLICK
                # --------------------------------------------

                if event.button == 1:

                    mouse_x, mouse_y = (
                        event.pos
                    )

                    # First see whether the user clicked
                    # an existing wall.
                    #
                    # If so, delete that wall rather than
                    # starting a new one.

                    wall_to_delete = None

                    # Search backwards so newer walls
                    # are selected first.
                    for wall in reversed(
                        walls
                    ):

                        if wall.contains_point(
                            mouse_x,
                            mouse_y
                        ):

                            wall_to_delete = wall
                            break

                    if wall_to_delete is not None:

                        walls.remove(
                            wall_to_delete
                        )

                    else:

                        # Start drawing a new free-form wall
                        drawing_wall = True

                        current_wall = Wall()

                        current_wall.add_point(
                            mouse_x,
                            mouse_y
                        )

                # --------------------------------------------
                # RIGHT CLICK
                # --------------------------------------------

                elif event.button == 3:

                    # Clear every wall
                    walls.clear()

            # ------------------------------------------------
            # Mouse movement
            # ------------------------------------------------

            elif (
                event.type ==
                pygame.MOUSEMOTION
            ):

                if (
                    drawing_wall
                    and current_wall is not None
                ):

                    mouse_x, mouse_y = (
                        event.pos
                    )

                    current_wall.add_point(
                        mouse_x,
                        mouse_y
                    )

            # ------------------------------------------------
            # Mouse button released
            # ------------------------------------------------

            elif (
                event.type ==
                pygame.MOUSEBUTTONUP
            ):

                if (
                    event.button == 1
                    and drawing_wall
                ):

                    drawing_wall = False

                    if (
                        current_wall is not None
                        and len(
                            current_wall.points
                        ) >= 2
                    ):

                        # Calculate total wall length
                        total_length = 0

                        for (
                            x1,
                            y1,
                            x2,
                            y2
                        ) in current_wall.segments():

                            total_length += distance(
                                x1,
                                y1,
                                x2,
                                y2
                            )

                        if (
                            total_length >=
                            MIN_WALL_LENGTH
                        ):

                            walls.append(
                                current_wall
                            )

                    current_wall = None

            # ------------------------------------------------
            # Keyboard
            # ------------------------------------------------

            elif (
                event.type ==
                pygame.KEYDOWN
            ):

                # ESC quits
                if event.key == pygame.K_ESCAPE:

                    running = False

                # R restarts
                elif event.key == pygame.K_r:

                    hearts.clear()

                    walls.clear()

                    score = 0

                    start_time = (
                        pygame.time.get_ticks()
                    )

                    spawn_timer = (
                        SPAWN_INTERVAL
                    )

        # ====================================================
        # SPAWN HEART
        # ====================================================

        spawn_timer -= dt

        if (
            spawn_timer <= 0
            and len(hearts) < MAX_HEARTS
        ):

            hearts.append(
                create_heart(
                    hearts
                )
            )

            # Exactly four seconds until the
            # next scheduled spawn.
            spawn_timer += (
                SPAWN_INTERVAL
            )

        elif spawn_timer <= 0:

            # We hit the 10-heart limit.
            #
            # Keep checking every frame until a heart
            # disappears, but do NOT add extra hearts
            # for the skipped spawn.
            spawn_timer = 0

        # ====================================================
        # UPDATE HEARTS
        # ====================================================

        for heart in hearts:

            heart.update(dt)

            # Bounce off every segment of every wall
            for wall in walls:

                for segment in wall.segments():

                    heart.bounce_off_wall(
                        segment
                    )

        # ====================================================
        # HEART COLLISIONS
        # ====================================================

        hearts_to_remove = []

        for i in range(
            len(hearts)
        ):

            for j in range(
                i + 1,
                len(hearts)
            ):

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

                    collision = (
                        handle_heart_collision(
                            heart1,
                            heart2
                        )
                    )

                    if collision:

                        # Each heart hit counts as one.
                        # Therefore one collision = 2 hits.
                        score += 2

                        if (
                            heart1.size <=
                            MIN_HEART_SIZE
                        ):

                            hearts_to_remove.append(
                                heart1
                            )

                        if (
                            heart2.size <=
                            MIN_HEART_SIZE
                        ):

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
        # HEART HITS PER MINUTE
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
        # Draw completed walls
        # ----------------------------------------------------

        for wall in walls:

            wall.draw(
                screen
            )

        # ----------------------------------------------------
        # Draw wall currently being created
        # ----------------------------------------------------

        if (
            drawing_wall
            and current_wall is not None
        ):

            if len(
                current_wall.points
            ) >= 2:

                pygame.draw.lines(
                    screen,
                    LIGHT_GRAY,
                    False,
                    current_wall.points,
                    4
                )

            # Start point
            if current_wall.points:

                x, y = (
                    current_wall.points[0]
                )

                pygame.draw.circle(
                    screen,
                    WHITE,
                    (
                        int(x),
                        int(y)
                    ),
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

        draw_text(
            screen,
            f"{hits_per_minute:.1f} HITS / MINUTE",
            rate_font,
            20,
            55
        )

        draw_text(
            screen,
            f"Hearts: {len(hearts)} / {MAX_HEARTS}",
            info_font,
            22,
            105,
            GRAY
        )

        # ----------------------------------------------------
        # Instructions
        # ----------------------------------------------------

        draw_text(
            screen,
            "Left-drag: draw a wall",
            small_font,
            20,
            HEIGHT - 88,
            GRAY
        )

        draw_text(
            screen,
            "Click wall: delete it    Right-click: clear all walls",
            small_font,
            20,
            HEIGHT - 62,
            GRAY
        )

        draw_text(
            screen,
            "R: restart    ESC: quit",
            small_font,
            20,
            HEIGHT - 36,
            GRAY
        )

        pygame.display.flip()

    # ========================================================
    # SHUTDOWN
    # ========================================================

    pygame.quit()

    sys.exit()


# ============================================================
# START GAME
# ============================================================

if __name__ == "__main__":
    main()


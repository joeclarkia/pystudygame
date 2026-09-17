import pygame
import math
import random
import sys

# ============================================================
# ASHER-stroids
# A Pygame space-car demolition game
# ============================================================

pygame.init()

WIDTH = 1000
HEIGHT = 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ASHER-stroids")
clock = pygame.time.Clock()

# ------------------------------------------------------------
# Colors
# ------------------------------------------------------------

BLACK = (5, 5, 12)
WHITE = (240, 240, 240)
GRAY = (130, 130, 140)
DARK_GRAY = (35, 35, 40)

YELLOW = (255, 220, 60)
RED = (240, 60, 60)
BLUE = (60, 150, 255)
GREEN = (70, 210, 100)
ORANGE = (255, 150, 40)
PURPLE = (180, 80, 220)
CYAN = (60, 220, 220)

CAR_COLORS = [
    RED,
    BLUE,
    GREEN,
    ORANGE,
    PURPLE,
    CYAN,
    WHITE
]

# ------------------------------------------------------------
# Fonts
# ------------------------------------------------------------

font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 64, bold=True)
small_font = pygame.font.SysFont("arial", 18)

# ------------------------------------------------------------
# Stars
# ------------------------------------------------------------

stars = []

for _ in range(180):
    stars.append([
        random.randrange(WIDTH),
        random.randrange(HEIGHT - 105),
        random.choice([1, 1, 1, 2])
    ])


# ============================================================
# Utility functions
# ============================================================

def wrap_position(x, y, margin=0):
    play_height = HEIGHT - 105

    if x < -margin:
        x = WIDTH + margin
    elif x > WIDTH + margin:
        x = -margin

    if y < -margin:
        y = play_height + margin
    elif y > play_height + margin:
        y = -margin

    return x, y


def distance(x1, y1, x2, y2):
    return math.hypot(
        x1 - x2,
        y1 - y2
    )


# ============================================================
# Player Ship
# ============================================================

class Ship:

    def __init__(self):
        self.reset()

    def reset(self):

        self.x = WIDTH / 2
        self.y = (HEIGHT - 105) / 2

        self.angle = -90

        self.velocity_x = 0
        self.velocity_y = 0

        self.radius = 16

        self.thrusting = False

    def rotate(self, amount):
        self.angle += amount

    def thrust(self):

        radians = math.radians(
            self.angle
        )

        self.velocity_x += (
            math.cos(radians) * 0.18
        )

        self.velocity_y += (
            math.sin(radians) * 0.18
        )

        speed = math.hypot(
            self.velocity_x,
            self.velocity_y
        )

        if speed > 7:

            self.velocity_x = (
                self.velocity_x / speed * 7
            )

            self.velocity_y = (
                self.velocity_y / speed * 7
            )

        self.thrusting = True

    def update(self):

        self.x += self.velocity_x
        self.y += self.velocity_y

        self.velocity_x *= 0.995
        self.velocity_y *= 0.995

        self.x, self.y = wrap_position(
            self.x,
            self.y,
            self.radius
        )

    def shoot(self):

        radians = math.radians(
            self.angle
        )

        nose_x = (
            self.x +
            math.cos(radians) * 20
        )

        nose_y = (
            self.y +
            math.sin(radians) * 20
        )

        return Bullet(
            nose_x,
            nose_y,
            math.cos(radians) * 10
            + self.velocity_x,
            math.sin(radians) * 10
            + self.velocity_y
        )

    def draw(self, surface):

        radians = math.radians(
            self.angle
        )

        # Nose
        nose = (
            self.x +
            math.cos(radians) * 22,

            self.y +
            math.sin(radians) * 22
        )

        # Left rear point
        left = (
            self.x +
            math.cos(radians + 2.5) * 17,

            self.y +
            math.sin(radians + 2.5) * 17
        )

        # Right rear point
        right = (
            self.x +
            math.cos(radians - 2.5) * 17,

            self.y +
            math.sin(radians - 2.5) * 17
        )

        pygame.draw.polygon(
            surface,
            WHITE,
            [nose, left, right],
            2
        )

        # Engine flame
        if self.thrusting:

            flame_x = (
                self.x +
                math.cos(
                    radians + math.pi
                ) * 18
            )

            flame_y = (
                self.y +
                math.sin(
                    radians + math.pi
                ) * 18
            )

            flame_left = (
                self.x +
                math.cos(
                    radians + 2.7
                ) * 9,

                self.y +
                math.sin(
                    radians + 2.7
                ) * 9
            )

            flame_right = (
                self.x +
                math.cos(
                    radians - 2.7
                ) * 9,

                self.y +
                math.sin(
                    radians - 2.7
                ) * 9
            )

            pygame.draw.polygon(
                surface,
                YELLOW,
                [
                    (flame_x, flame_y),
                    flame_left,
                    flame_right
                ]
            )

        self.thrusting = False


# ============================================================
# Bullet
# ============================================================

class Bullet:

    def __init__(
        self,
        x,
        y,
        velocity_x,
        velocity_y
    ):

        self.x = x
        self.y = y

        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

        self.life = 60
        self.radius = 3

    def update(self):

        self.x += self.velocity_x
        self.y += self.velocity_y

        self.life -= 1

        self.x, self.y = wrap_position(
            self.x,
            self.y
        )

    def draw(self, surface):

        pygame.draw.circle(
            surface,
            YELLOW,
            (
                int(self.x),
                int(self.y)
            ),
            self.radius
        )


# ============================================================
# Car Part
#
# IMPORTANT:
# Car parts have NO collision detection.
# They simply fly through the player's ship.
# ============================================================

class CarPart:

    def __init__(
        self,
        x,
        y,
        part_type,
        color
    ):

        self.x = x
        self.y = y

        self.part_type = part_type
        self.color = color

        angle = random.uniform(
            0,
            math.pi * 2
        )

        speed = random.uniform(
            2,
            7
        )

        self.velocity_x = (
            math.cos(angle) * speed
        )

        self.velocity_y = (
            math.sin(angle) * speed
        )

        self.rotation = random.uniform(
            -12,
            12
        )

        self.rotation_angle = random.uniform(
            0,
            360
        )

        self.life = random.randint(
            45,
            100
        )

        self.size = random.randint(
            5,
            10
        )

    def update(self):

        self.x += self.velocity_x
        self.y += self.velocity_y

        self.velocity_x *= 0.97
        self.velocity_y *= 0.97

        self.rotation_angle += (
            self.rotation
        )

        self.life -= 1

    def draw_rotated_polygon(
        self,
        surface,
        points,
        color
    ):

        angle = math.radians(
            self.rotation_angle
        )

        rotated = []

        for px, py in points:

            rx = (
                px * math.cos(angle)
                -
                py * math.sin(angle)
            )

            ry = (
                px * math.sin(angle)
                +
                py * math.cos(angle)
            )

            rotated.append(
                (
                    int(self.x + rx),
                    int(self.y + ry)
                )
            )

        pygame.draw.polygon(
            surface,
            color,
            rotated
        )

    def draw(self, surface):

        if self.life <= 0:
            return

        # ----------------------------------------------------
        # Wheel
        # ----------------------------------------------------

        if self.part_type == "wheel":

            pygame.draw.circle(
                surface,
                (25, 25, 25),
                (
                    int(self.x),
                    int(self.y)
                ),
                self.size
            )

            pygame.draw.circle(
                surface,
                GRAY,
                (
                    int(self.x),
                    int(self.y)
                ),
                max(
                    2,
                    self.size // 3
                )
            )

        # ----------------------------------------------------
        # Door
        # ----------------------------------------------------

        elif self.part_type == "door":

            points = [
                (-8, -12),
                (8, -12),
                (9, 12),
                (-9, 12)
            ]

            self.draw_rotated_polygon(
                surface,
                points,
                self.color
            )

            pygame.draw.line(
                surface,
                WHITE,
                (
                    int(self.x - 5),
                    int(self.y)
                ),
                (
                    int(self.x + 5),
                    int(self.y)
                ),
                1
            )

        # ----------------------------------------------------
        # Bumper
        # ----------------------------------------------------

        elif self.part_type == "bumper":

            points = [
                (-14, -4),
                (14, -4),
                (14, 4),
                (-14, 4)
            ]

            self.draw_rotated_polygon(
                surface,
                points,
                GRAY
            )

        # ----------------------------------------------------
        # Hood / trunk
        # ----------------------------------------------------

        elif self.part_type == "hood":

            points = [
                (-12, -8),
                (12, -8),
                (10, 8),
                (-10, 8)
            ]

            self.draw_rotated_polygon(
                surface,
                points,
                self.color
            )

        # ----------------------------------------------------
        # Window
        # ----------------------------------------------------

        elif self.part_type == "window":

            points = [
                (-9, -6),
                (9, -6),
                (7, 6),
                (-7, 6)
            ]

            self.draw_rotated_polygon(
                surface,
                points,
                (70, 140, 180)
            )

        # ----------------------------------------------------
        # Random piece of wreckage
        # ----------------------------------------------------

        else:

            s = self.size

            points = [
                (-s, -s),
                (s, -s),
                (s, s),
                (-s, s)
            ]

            self.draw_rotated_polygon(
                surface,
                points,
                self.color
            )


# ============================================================
# Explosion Particle
# ============================================================

class ExplosionParticle:

    def __init__(
        self,
        x,
        y
    ):

        self.x = x
        self.y = y

        angle = random.uniform(
            0,
            math.pi * 2
        )

        speed = random.uniform(
            1,
            6
        )

        self.velocity_x = (
            math.cos(angle) * speed
        )

        self.velocity_y = (
            math.sin(angle) * speed
        )

        self.life = random.randint(
            20,
            50
        )

        self.size = random.randint(
            2,
            5
        )

        self.color = random.choice([
            YELLOW,
            ORANGE,
            RED,
            WHITE
        ])

    def update(self):

        self.x += self.velocity_x
        self.y += self.velocity_y

        self.velocity_x *= 0.96
        self.velocity_y *= 0.96

        self.life -= 1

    def draw(self, surface):

        if self.life > 0:

            pygame.draw.circle(
                surface,
                self.color,
                (
                    int(self.x),
                    int(self.y)
                ),
                self.size
            )


# ============================================================
# Car
# ============================================================

class Car:

    def __init__(
        self,
        x,
        y,
        size=3
    ):

        self.x = x
        self.y = y

        self.size = size

        # ----------------------------------------------------
        # Car sizes
        # ----------------------------------------------------

        if size == 3:

            self.width = 68
            self.height = 36
            self.radius = 34

            self.speed = random.uniform(
                1.0,
                2.0
            )

            self.points = 20

        elif size == 2:

            self.width = 48
            self.height = 28
            self.radius = 24

            self.speed = random.uniform(
                1.5,
                2.7
            )

            self.points = 50

        else:

            self.width = 32
            self.height = 20
            self.radius = 16

            self.speed = random.uniform(
                2.0,
                3.5
            )

            self.points = 100

        # ----------------------------------------------------
        # Color
        # ----------------------------------------------------

        self.color = random.choice(
            CAR_COLORS
        )

        # ----------------------------------------------------
        # Movement
        # ----------------------------------------------------

        direction = random.uniform(
            0,
            math.pi * 2
        )

        self.velocity_x = (
            math.cos(direction)
            * self.speed
        )

        self.velocity_y = (
            math.sin(direction)
            * self.speed
        )

        self.rotation = random.uniform(
            -2.5,
            2.5
        )

        self.rotation_angle = random.uniform(
            0,
            360
        )

    def update(self):

        self.x += self.velocity_x
        self.y += self.velocity_y

        self.rotation_angle += (
            self.rotation
        )

        self.x, self.y = wrap_position(
            self.x,
            self.y,
            self.radius
        )

    def draw_rotated_polygon(
        self,
        surface,
        points,
        color,
        width=0
    ):

        angle = math.radians(
            self.rotation_angle
        )

        rotated = []

        for px, py in points:

            rx = (
                px * math.cos(angle)
                -
                py * math.sin(angle)
            )

            ry = (
                px * math.sin(angle)
                +
                py * math.cos(angle)
            )

            rotated.append(
                (
                    int(self.x + rx),
                    int(self.y + ry)
                )
            )

        pygame.draw.polygon(
            surface,
            color,
            rotated,
            width
        )

    def draw(self, surface):

        w = self.width
        h = self.height

        # ----------------------------------------------------
        # Main body
        # ----------------------------------------------------

        body = [
            (-w / 2, -h / 2),
            (w / 2, -h / 2),
            (w / 2, h / 2),
            (-w / 2, h / 2)
        ]

        self.draw_rotated_polygon(
            surface,
            body,
            self.color
        )

        # Body outline
        self.draw_rotated_polygon(
            surface,
            body,
            WHITE,
            2
        )

        # ----------------------------------------------------
        # Roof
        # ----------------------------------------------------

        roof = [
            (-w * 0.22, -h * 0.48),
            (w * 0.20, -h * 0.48),
            (w * 0.32, h * 0.02),
            (-w * 0.30, h * 0.02)
        ]

        self.draw_rotated_polygon(
            surface,
            roof,
            self.color
        )

        # ----------------------------------------------------
        # Windows
        # ----------------------------------------------------

        window1 = [
            (-w * 0.20, -h * 0.40),
            (-w * 0.02, -h * 0.40),
            (-w * 0.06, -h * 0.04),
            (-w * 0.25, -h * 0.04)
        ]

        window2 = [
            (w * 0.02, -h * 0.40),
            (w * 0.18, -h * 0.40),
            (w * 0.27, -h * 0.04),
            (w * 0.06, -h * 0.04)
        ]

        self.draw_rotated_polygon(
            surface,
            window1,
            (50, 90, 120)
        )

        self.draw_rotated_polygon(
            surface,
            window2,
            (50, 90, 120)
        )

        # ----------------------------------------------------
        # Wheels
        # ----------------------------------------------------

        wheel_positions = [
            (-w * 0.32, -h * 0.55),
            (w * 0.32, -h * 0.55),
            (-w * 0.32, h * 0.55),
            (w * 0.32, h * 0.55)
        ]

        angle = math.radians(
            self.rotation_angle
        )

        for wx, wy in wheel_positions:

            rx = (
                wx * math.cos(angle)
                -
                wy * math.sin(angle)
            )

            ry = (
                wx * math.sin(angle)
                +
                wy * math.cos(angle)
            )

            pygame.draw.circle(
                surface,
                (20, 20, 20),
                (
                    int(self.x + rx),
                    int(self.y + ry)
                ),
                max(
                    4,
                    int(h * 0.25)
                )
            )

        # ----------------------------------------------------
        # Headlights
        # ----------------------------------------------------

        self.draw_rotated_polygon(
            surface,
            [
                (w * 0.38, -h * 0.32),
                (w * 0.48, -h * 0.25),
                (w * 0.48, -h * 0.05),
                (w * 0.38, -h * 0.08)
            ],
            YELLOW
        )

        # ----------------------------------------------------
        # Taillight
        # ----------------------------------------------------

        self.draw_rotated_polygon(
            surface,
            [
                (-w * 0.48, h * 0.05),
                (-w * 0.38, h * 0.05),
                (-w * 0.38, h * 0.30),
                (-w * 0.48, h * 0.25)
            ],
            RED
        )

    # --------------------------------------------------------
    # Create flying pieces when destroyed
    # --------------------------------------------------------

    def explode(self):

        parts = []

        # Four wheels
        for _ in range(4):

            parts.append(
                CarPart(
                    self.x,
                    self.y,
                    "wheel",
                    self.color
                )
            )

        # Two doors
        for _ in range(2):

            parts.append(
                CarPart(
                    self.x,
                    self.y,
                    "door",
                    self.color
                )
            )

        # Hood
        parts.append(
            CarPart(
                self.x,
                self.y,
                "hood",
                self.color
            )
        )

        # Trunk
        parts.append(
            CarPart(
                self.x,
                self.y,
                "hood",
                self.color
            )
        )

        # Windows
        for _ in range(2):

            parts.append(
                CarPart(
                    self.x,
                    self.y,
                    "window",
                    self.color
                )
            )

        # Bumpers
        for _ in range(2):

            parts.append(
                CarPart(
                    self.x,
                    self.y,
                    "bumper",
                    GRAY
                )
            )

        # Random chunks
        chunk_count = (
            5
            if self.size == 1
            else 8
        )

        for _ in range(chunk_count):

            parts.append(
                CarPart(
                    self.x,
                    self.y,
                    "chunk",
                    self.color
                )
            )

        return parts


# ============================================================
# Create initial car field
# ============================================================

def create_car_field(number):

    cars = []

    play_height = HEIGHT - 105

    for _ in range(number):

        while True:

            x = random.randint(
                0,
                WIDTH
            )

            y = random.randint(
                0,
                play_height
            )

            # Keep cars away from starting position
            if distance(
                x,
                y,
                WIDTH / 2,
                play_height / 2
            ) > 180:

                break

        cars.append(
            Car(
                x,
                y,
                3
            )
        )

    return cars


# ============================================================
# Game State
# ============================================================

ship = Ship()

cars = create_car_field(7)

bullets = []

car_parts = []

explosion_particles = []

score = 0

lives = 3

shoot_cooldown = 0

game_over = False


# ============================================================
# Main Game Loop
# ============================================================

running = True

while running:

    clock.tick(FPS)

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            # Fire
            if event.key == pygame.K_SPACE:

                if (
                    not game_over
                    and shoot_cooldown <= 0
                ):

                    bullets.append(
                        ship.shoot()
                    )

                    shoot_cooldown = 10

            # Restart
            if event.key == pygame.K_r:

                if game_over:

                    ship.reset()

                    cars = create_car_field(
                        7
                    )

                    bullets.clear()

                    car_parts.clear()

                    explosion_particles.clear()

                    score = 0
                    lives = 3

                    game_over = False

    # ========================================================
    # CONTROLS
    # ========================================================

    keys = pygame.key.get_pressed()

    if not game_over:

        if (
            keys[pygame.K_LEFT]
            or keys[pygame.K_a]
        ):

            ship.rotate(-5)

        if (
            keys[pygame.K_RIGHT]
            or keys[pygame.K_d]
        ):

            ship.rotate(5)

        if (
            keys[pygame.K_UP]
            or keys[pygame.K_w]
        ):

            ship.thrust()

        # Hold space to fire
        if keys[pygame.K_SPACE]:

            if shoot_cooldown <= 0:

                bullets.append(
                    ship.shoot()
                )

                shoot_cooldown = 10

    if shoot_cooldown > 0:
        shoot_cooldown -= 1

    # ========================================================
    # UPDATE OBJECTS
    # ========================================================

    if not game_over:

        ship.update()

        for bullet in bullets:
            bullet.update()

        bullets = [
            bullet
            for bullet in bullets
            if bullet.life > 0
        ]

        for car in cars:
            car.update()

    # --------------------------------------------------------
    # Car parts continue flying
    #
    # NOTE: There is deliberately NO collision check here.
    # --------------------------------------------------------

    for part in car_parts:
        part.update()

    car_parts = [
        part
        for part in car_parts
        if part.life > 0
    ]

    # --------------------------------------------------------
    # Explosion particles
    # --------------------------------------------------------

    for particle in explosion_particles:
        particle.update()

    explosion_particles = [
        particle
        for particle in explosion_particles
        if particle.life > 0
    ]

    # ========================================================
    # BULLET / CAR COLLISIONS
    # ========================================================

    if not game_over:

        cars_to_remove = []

        bullets_to_remove = []

        for bullet in bullets:

            for car in cars:

                if car in cars_to_remove:
                    continue

                if distance(
                    bullet.x,
                    bullet.y,
                    car.x,
                    car.y
                ) < car.radius:

                    bullets_to_remove.append(
                        bullet
                    )

                    cars_to_remove.append(
                        car
                    )

                    score += car.points

                    # ----------------------------------------
                    # Explode the car!
                    # ----------------------------------------

                    car_parts.extend(
                        car.explode()
                    )

                    # Explosion sparks
                    for _ in range(30):

                        explosion_particles.append(
                            ExplosionParticle(
                                car.x,
                                car.y
                            )
                        )

                    # ----------------------------------------
                    # Split large cars
                    # ----------------------------------------

                    if car.size > 1:

                        for _ in range(2):

                            new_car = Car(
                                car.x,
                                car.y,
                                car.size - 1
                            )

                            new_car.velocity_x *= 1.3
                            new_car.velocity_y *= 1.3

                            cars.append(
                                new_car
                            )

                    break

        bullets = [
            bullet
            for bullet in bullets
            if bullet not in bullets_to_remove
        ]

        cars = [
            car
            for car in cars
            if car not in cars_to_remove
        ]

    # ========================================================
    # SHIP / CAR COLLISION
    #
    # ONLY INTACT CARS CAN HURT THE SHIP.
    # Flying doors, wheels, windows, bumpers, etc.
    # are completely harmless.
    # ========================================================

    if not game_over:

        for car in cars:

            if distance(
                ship.x,
                ship.y,
                car.x,
                car.y
            ) < (
                car.radius +
                ship.radius
            ):

                lives -= 1

                # Ship explosion
                for _ in range(35):

                    explosion_particles.append(
                        ExplosionParticle(
                            ship.x,
                            ship.y
                        )
                    )

                if lives <= 0:

                    game_over = True

                else:

                    ship.reset()

                break

    # ========================================================
    # NEW WAVE
    # ========================================================

    if (
        not game_over
        and len(cars) == 0
    ):

        number = min(
            14,
            5 + score // 500
        )

        cars = create_car_field(
            number
        )

    # ========================================================
    # DRAW
    # ========================================================

    screen.fill(BLACK)

    # --------------------------------------------------------
    # Stars
    # --------------------------------------------------------

    for x, y, size in stars:

        pygame.draw.circle(
            screen,
            WHITE,
            (x, y),
            size
        )

    # --------------------------------------------------------
    # Cars
    # --------------------------------------------------------

    for car in cars:
        car.draw(screen)

    # --------------------------------------------------------
    # Bullets
    # --------------------------------------------------------

    for bullet in bullets:
        bullet.draw(screen)

    # --------------------------------------------------------
    # Flying car parts
    # --------------------------------------------------------

    for part in car_parts:
        part.draw(screen)

    # --------------------------------------------------------
    # Explosion particles
    # --------------------------------------------------------

    for particle in explosion_particles:
        particle.draw(screen)

    # --------------------------------------------------------
    # Player ship
    # --------------------------------------------------------

    if not game_over:
        ship.draw(screen)

    # ========================================================
    # HORIZON
    # ========================================================

    horizon_y = HEIGHT - 95

    pygame.draw.line(
        screen,
        (80, 80, 100),
        (0, horizon_y),
        (WIDTH, horizon_y),
        2
    )

    title = big_font.render(
        "ASHER-stroids",
        True,
        WHITE
    )

    title_rect = title.get_rect(
        center=(
            WIDTH // 2,
            HEIGHT - 48
        )
    )

    screen.blit(
        title,
        title_rect
    )

    # ========================================================
    # HUD
    # ========================================================

    score_text = font.render(
        f"SCORE: {score}",
        True,
        WHITE
    )

    lives_text = font.render(
        f"LIVES: {lives}",
        True,
        WHITE
    )

    screen.blit(
        score_text,
        (20, 15)
    )

    screen.blit(
        lives_text,
        (WIDTH - 120, 15)
    )

    controls = small_font.render(
        "ARROWS / WASD = steer & thrust    SPACE = fire",
        True,
        GRAY
    )

    screen.blit(
        controls,
        (20, HEIGHT - 118)
    )

    # ========================================================
    # GAME OVER
    # ========================================================

    if game_over:

        game_over_text = big_font.render(
            "GAME OVER",
            True,
            RED
        )

        rect = game_over_text.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 - 30
            )
        )

        screen.blit(
            game_over_text,
            rect
        )

        restart = font.render(
            "Press R to restart",
            True,
            WHITE
        )

        restart_rect = restart.get_rect(
            center=(
                WIDTH // 2,
                HEIGHT // 2 + 40
            )
        )

        screen.blit(
            restart,
            restart_rect
        )

    pygame.display.flip()


# ============================================================
# Shutdown
# ============================================================

pygame.quit()
sys.exit()


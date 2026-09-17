import pygame
import math
import random
import sys

# ------------------------------------------------------------
# ASHER-stroids
# A classic Asteroids-style game made with Pygame
# ------------------------------------------------------------

pygame.init()

WIDTH = 1000
HEIGHT = 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ASHER-stroids")
clock = pygame.time.Clock()

# Colors
BLACK = (5, 5, 12)
WHITE = (240, 240, 240)
GRAY = (130, 130, 140)
YELLOW = (255, 220, 70)
RED = (255, 80, 80)
BLUE = (80, 180, 255)

# Fonts
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


# ------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------

def wrap_position(x, y, margin=0):
    """Wrap an object around the screen edges."""
    if x < -margin:
        x = WIDTH + margin
    elif x > WIDTH + margin:
        x = -margin

    if y < -margin:
        y = HEIGHT - 105 + margin
    elif y > HEIGHT - 105 + margin:
        y = -margin

    return x, y


def distance(x1, y1, x2, y2):
    return math.hypot(x1 - x2, y1 - y2)


# ------------------------------------------------------------
# Ship
# ------------------------------------------------------------

class Ship:
    def __init__(self):
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        self.angle = -90
        self.velocity_x = 0
        self.velocity_y = 0
        self.radius = 16
        self.thrusting = False

    def reset(self):
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        self.angle = -90
        self.velocity_x = 0
        self.velocity_y = 0

    def rotate(self, amount):
        self.angle += amount

    def thrust(self):
        radians = math.radians(self.angle)

        self.velocity_x += math.cos(radians) * 0.18
        self.velocity_y += math.sin(radians) * 0.18

        # Limit maximum speed
        speed = math.hypot(self.velocity_x, self.velocity_y)

        if speed > 7:
            self.velocity_x = self.velocity_x / speed * 7
            self.velocity_y = self.velocity_y / speed * 7

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
        radians = math.radians(self.angle)

        nose_x = self.x + math.cos(radians) * 20
        nose_y = self.y + math.sin(radians) * 20

        return Bullet(
            nose_x,
            nose_y,
            math.cos(radians) * 10 + self.velocity_x,
            math.sin(radians) * 10 + self.velocity_y
        )

    def draw(self, surface):
        radians = math.radians(self.angle)

        # Main nose
        nose = (
            self.x + math.cos(radians) * 22,
            self.y + math.sin(radians) * 22
        )

        # Rear points
        left = (
            self.x + math.cos(radians + 2.5) * 17,
            self.y + math.sin(radians + 2.5) * 17
        )

        right = (
            self.x + math.cos(radians - 2.5) * 17,
            self.y + math.sin(radians - 2.5) * 17
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
                self.x + math.cos(radians + math.pi) * 18
            )
            flame_y = (
                self.y + math.sin(radians + math.pi) * 18
            )

            flame_left = (
                self.x + math.cos(radians + 2.7) * 9,
                self.y + math.sin(radians + 2.7) * 9
            )

            flame_right = (
                self.x + math.cos(radians - 2.7) * 9,
                self.y + math.sin(radians - 2.7) * 9
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


# ------------------------------------------------------------
# Bullet
# ------------------------------------------------------------

class Bullet:
    def __init__(self, x, y, velocity_x, velocity_y):
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

        self.x, self.y = wrap_position(self.x, self.y)

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            YELLOW,
            (int(self.x), int(self.y)),
            self.radius
        )


# ------------------------------------------------------------
# Asteroid
# ------------------------------------------------------------

class Asteroid:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

        if size == 3:
            self.radius = 42
            self.speed = random.uniform(1.0, 2.0)
            self.points = 20
        elif size == 2:
            self.radius = 25
            self.speed = random.uniform(1.5, 2.7)
            self.points = 50
        else:
            self.radius = 14
            self.speed = random.uniform(2.0, 3.5)
            self.points = 100

        angle = random.uniform(0, math.pi * 2)

        self.velocity_x = math.cos(angle) * self.speed
        self.velocity_y = math.sin(angle) * self.speed

        # Random irregular asteroid shape
        self.shape = []

        num_points = random.randint(9, 13)

        for i in range(num_points):
            angle = (math.pi * 2 / num_points) * i

            radius = self.radius * random.uniform(
                0.75,
                1.25
            )

            self.shape.append((
                math.cos(angle) * radius,
                math.sin(angle) * radius
            ))

        self.rotation = random.uniform(-2, 2)
        self.rotation_angle = 0

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        self.rotation_angle += self.rotation

        self.x, self.y = wrap_position(
            self.x,
            self.y,
            self.radius
        )

    def draw(self, surface):
        points = []

        rotation = math.radians(self.rotation_angle)

        for px, py in self.shape:

            rotated_x = (
                px * math.cos(rotation)
                - py * math.sin(rotation)
            )

            rotated_y = (
                px * math.sin(rotation)
                + py * math.cos(rotation)
            )

            points.append((
                self.x + rotated_x,
                self.y + rotated_y
            ))

        pygame.draw.polygon(
            surface,
            GRAY,
            points,
            2
        )


# ------------------------------------------------------------
# Create asteroids
# ------------------------------------------------------------

def create_asteroid_field(number):
    asteroids = []

    for _ in range(number):

        # Don't initially spawn right on top of the player
        while True:
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT - 120)

            if distance(
                x,
                y,
                WIDTH / 2,
                HEIGHT / 2
            ) > 180:
                break

        asteroids.append(
            Asteroid(x, y, 3)
        )

    return asteroids


# ------------------------------------------------------------
# Explosion particles
# ------------------------------------------------------------

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 5)

        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed

        self.life = random.randint(20, 45)

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
                YELLOW,
                (int(self.x), int(self.y)),
                max(1, self.life // 10)
            )


# ------------------------------------------------------------
# Game variables
# ------------------------------------------------------------

ship = Ship()
bullets = []
asteroids = create_asteroid_field(7)
particles = []

score = 0
lives = 3

shoot_cooldown = 0

game_over = False

# ------------------------------------------------------------
# Main game loop
# ------------------------------------------------------------

running = True

while running:

    clock.tick(FPS)

    # --------------------------------------------------------
    # Events
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:
                if not game_over and shoot_cooldown <= 0:
                    bullets.append(ship.shoot())
                    shoot_cooldown = 10

            if event.key == pygame.K_r:
                if game_over:
                    ship.reset()
                    asteroids = create_asteroid_field(7)
                    bullets.clear()
                    particles.clear()

                    score = 0
                    lives = 3

                    game_over = False

    keys = pygame.key.get_pressed()

    # --------------------------------------------------------
    # Controls
    # --------------------------------------------------------

    if not game_over:

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            ship.rotate(-5)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            ship.rotate(5)

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            ship.thrust()

        # Hold space to fire repeatedly
        if keys[pygame.K_SPACE]:

            if shoot_cooldown <= 0:
                bullets.append(ship.shoot())
                shoot_cooldown = 10

    if shoot_cooldown > 0:
        shoot_cooldown -= 1

    # --------------------------------------------------------
    # Update objects
    # --------------------------------------------------------

    if not game_over:

        ship.update()

        for bullet in bullets:
            bullet.update()

        bullets = [
            bullet for bullet in bullets
            if bullet.life > 0
        ]

        for asteroid in asteroids:
            asteroid.update()

        for particle in particles:
            particle.update()

        particles = [
            particle for particle in particles
            if particle.life > 0
        ]

    # --------------------------------------------------------
    # Bullet / asteroid collisions
    # --------------------------------------------------------

    if not game_over:

        bullets_to_remove = []
        asteroids_to_remove = []

        for bullet in bullets:

            for asteroid in asteroids:

                if asteroid in asteroids_to_remove:
                    continue

                if distance(
                    bullet.x,
                    bullet.y,
                    asteroid.x,
                    asteroid.y
                ) < asteroid.radius:

                    bullets_to_remove.append(bullet)
                    asteroids_to_remove.append(asteroid)

                    score += asteroid.points

                    # Explosion
                    for _ in range(10):
                        particles.append(
                            Particle(
                                asteroid.x,
                                asteroid.y
                            )
                        )

                    # Split large asteroid into smaller ones
                    if asteroid.size > 1:

                        for _ in range(2):

                            new_asteroid = Asteroid(
                                asteroid.x,
                                asteroid.y,
                                asteroid.size - 1
                            )

                            # Give fragments a little more speed
                            new_asteroid.velocity_x *= 1.25
                            new_asteroid.velocity_y *= 1.25

                            asteroids.append(
                                new_asteroid
                            )

                    break

        bullets = [
            bullet for bullet in bullets
            if bullet not in bullets_to_remove
        ]

        asteroids = [
            asteroid for asteroid in asteroids
            if asteroid not in asteroids_to_remove
        ]

    # --------------------------------------------------------
    # Ship / asteroid collisions
    # --------------------------------------------------------

    if not game_over:

        for asteroid in asteroids:

            if distance(
                ship.x,
                ship.y,
                asteroid.x,
                asteroid.y
            ) < asteroid.radius + ship.radius:

                lives -= 1

                for _ in range(25):
                    particles.append(
                        Particle(
                            ship.x,
                            ship.y
                        )
                    )

                if lives <= 0:
                    game_over = True
                else:
                    ship.reset()

                break

    # --------------------------------------------------------
    # New wave
    # --------------------------------------------------------

    if not game_over and len(asteroids) == 0:

        # Start a slightly larger wave
        number = min(14, 5 + score // 500)

        asteroids = create_asteroid_field(number)

    # --------------------------------------------------------
    # Draw
    # --------------------------------------------------------

    screen.fill(BLACK)

    # Stars
    for x, y, size in stars:
        pygame.draw.circle(
            screen,
            WHITE,
            (x, y),
            size
        )

    # Asteroids
    for asteroid in asteroids:
        asteroid.draw(screen)

    # Bullets
    for bullet in bullets:
        bullet.draw(screen)

    # Particles
    for particle in particles:
        particle.draw(screen)

    # Ship
    if not game_over:
        ship.draw(screen)

    # --------------------------------------------------------
    # Horizon / ASHER-stroids
    # --------------------------------------------------------

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
        center=(WIDTH // 2, HEIGHT - 48)
    )

    screen.blit(title, title_rect)

    # --------------------------------------------------------
    # HUD
    # --------------------------------------------------------

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

    screen.blit(score_text, (20, 15))
    screen.blit(lives_text, (WIDTH - 120, 15))

    controls = small_font.render(
        "ARROWS / WASD = steer & thrust    SPACE = fire",
        True,
        GRAY
    )

    screen.blit(
        controls,
        (20, HEIGHT - 118)
    )

    # --------------------------------------------------------
    # Game over
    # --------------------------------------------------------

    if game_over:

        game_over_text = big_font.render(
            "GAME OVER",
            True,
            RED
        )

        rect = game_over_text.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 - 30)
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
            center=(WIDTH // 2, HEIGHT // 2 + 40)
        )

        screen.blit(
            restart,
            restart_rect
        )

    pygame.display.flip()


pygame.quit()
sys.exit()

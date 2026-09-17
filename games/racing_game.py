import pygame
import random
import math

# ============================================================
# Configuration
# ============================================================

WIDTH = 1000
HEIGHT = 700
FPS = 60

ROAD_WIDTH = 540
ROAD_CENTER = WIDTH // 2

CAR_WIDTH = 42
CAR_HEIGHT = 72

MAX_SPEED = 11.0
ACCELERATION = 0.18
BRAKING = 0.30
FRICTION = 0.06
STEERING_SPEED = 5.0

# Easier difficulty
NUM_AI_CARS = 5
NUM_OBSTACLES = 4

# Colors
GRASS = (45, 140, 55)
ROAD = (65, 65, 65)
ROAD_EDGE = (235, 235, 235)
LANE_MARKING = (245, 245, 180)

RED = (220, 40, 40)
BLUE = (40, 100, 220)
YELLOW = (240, 210, 40)
GREEN = (40, 190, 90)
PURPLE = (170, 60, 190)
ORANGE = (240, 130, 30)
CYAN = (30, 190, 210)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (150, 150, 150)


# ============================================================
# Utility
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


# ============================================================
# Curved Track
# ============================================================

def track_center(y, road_offset):
    """
    Returns the X coordinate of the center of the road at
    a particular screen Y position.

    Several sine waves are combined to make the track curve
    naturally rather than simply zig-zagging.
    """

    world_y = y + road_offset

    curve1 = math.sin(world_y / 240.0) * 120
    curve2 = math.sin(world_y / 470.0) * 80
    curve3 = math.sin(world_y / 1000.0) * 100

    return ROAD_CENTER + curve1 + curve2 + curve3


def road_bounds(y, road_offset):
    center = track_center(y, road_offset)

    left = center - ROAD_WIDTH / 2
    right = center + ROAD_WIDTH / 2

    return left, right


# ============================================================
# Car
# ============================================================

class Car:

    def __init__(
        self,
        x,
        y,
        color,
        is_player=False,
        style="sports"
    ):

        self.x = x
        self.y = y

        self.color = color
        self.is_player = is_player
        self.style = style

        self.width = CAR_WIDTH
        self.height = CAR_HEIGHT

        self.speed = 0

        self.ai_speed = random.uniform(5.5, 8.3)
        self.ai_lane = random.randint(0, 2)

        self.crashed = False

    def rect(self):
        return pygame.Rect(
            int(self.x - self.width / 2),
            int(self.y - self.height / 2),
            self.width,
            self.height
        )

    # --------------------------------------------------------
    # Player control
    # --------------------------------------------------------

    def update_player(self, keys, road_offset):

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed += ACCELERATION

        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed -= BRAKING

        else:
            if self.speed > 0:
                self.speed -= FRICTION
            elif self.speed < 0:
                self.speed += FRICTION

        self.speed = clamp(
            self.speed,
            -3,
            MAX_SPEED
        )

        steering = (
            STEERING_SPEED *
            max(abs(self.speed) / MAX_SPEED, 0.3)
        )

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= steering

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += steering

        # Current road boundaries
        left, right = road_bounds(
            self.y,
            road_offset
        )

        self.x = clamp(
            self.x,
            left + self.width / 2 + 5,
            right - self.width / 2 - 5
        )

    # --------------------------------------------------------
    # AI control
    # --------------------------------------------------------

    def update_ai(
        self,
        player_speed,
        obstacles,
        road_offset
    ):

        if self.speed < self.ai_speed:
            self.speed += 0.08

        elif self.speed > self.ai_speed:
            self.speed -= 0.05

        self.speed = clamp(
            self.speed,
            0,
            MAX_SPEED * 0.9
        )

        left, right = road_bounds(
            self.y,
            road_offset
        )

        lane_width = ROAD_WIDTH / 3

        target_x = (
            left +
            lane_width * self.ai_lane +
            lane_width / 2
        )

        # Look for obstacles ahead.
        # AI will change lanes if it sees one.
        for obstacle in obstacles:

            if (
                abs(obstacle.x - self.x) < 55
                and obstacle.y < self.y
                and self.y - obstacle.y < 200
            ):

                possible_lanes = [0, 1, 2]
                random.shuffle(possible_lanes)

                for lane in possible_lanes:

                    candidate_x = (
                        left +
                        lane_width * lane +
                        lane_width / 2
                    )

                    if abs(candidate_x - obstacle.x) > 80:
                        self.ai_lane = lane
                        target_x = candidate_x
                        break

        # Move toward desired lane
        difference = target_x - self.x

        self.x += clamp(
            difference * 0.08,
            -2.5,
            2.5
        )

        # Follow the road vertically
        self.y += player_speed - self.speed

    # --------------------------------------------------------
    # Drawing
    # --------------------------------------------------------

    def draw(self, screen):

        rect = self.rect()

        # Shadow
        shadow = rect.copy()
        shadow.x += 5
        shadow.y += 5

        pygame.draw.rect(
            screen,
            (30, 30, 30),
            shadow,
            border_radius=8
        )

        # ----------------------------------------------------
        # Different vehicle styles
        # ----------------------------------------------------

        if self.style == "sports":

            pygame.draw.rect(
                screen,
                self.color,
                rect,
                border_radius=10
            )

            # Center stripe
            pygame.draw.rect(
                screen,
                WHITE,
                (
                    rect.centerx - 3,
                    rect.top + 3,
                    6,
                    rect.height - 6
                )
            )

            # Windows
            pygame.draw.rect(
                screen,
                (55, 120, 160),
                (
                    rect.x + 7,
                    rect.y + 12,
                    rect.width - 14,
                    20
                ),
                border_radius=5
            )

        elif self.style == "muscle":

            pygame.draw.rect(
                screen,
                self.color,
                rect,
                border_radius=4
            )

            # Black racing stripe
            pygame.draw.rect(
                screen,
                BLACK,
                (
                    rect.centerx - 5,
                    rect.top,
                    10,
                    rect.height
                )
            )

            pygame.draw.rect(
                screen,
                (45, 100, 130),
                (
                    rect.x + 6,
                    rect.y + 12,
                    rect.width - 12,
                    18
                )
            )

            # Hood scoop
            pygame.draw.rect(
                screen,
                GRAY,
                (
                    rect.centerx - 7,
                    rect.y + 3,
                    14,
                    12
                ),
                border_radius=3
            )

        elif self.style == "formula":

            # Pointed nose
            pygame.draw.polygon(
                screen,
                self.color,
                [
                    (rect.centerx, rect.top - 8),
                    (rect.right, rect.top + 25),
                    (rect.right - 5, rect.bottom),
                    (rect.left + 5, rect.bottom),
                    (rect.left, rect.top + 25)
                ]
            )

            # Cockpit
            pygame.draw.ellipse(
                screen,
                BLACK,
                (
                    rect.x + 10,
                    rect.y + 15,
                    rect.width - 20,
                    25
                )
            )

            pygame.draw.ellipse(
                screen,
                (70, 130, 170),
                (
                    rect.x + 14,
                    rect.y + 18,
                    rect.width - 28,
                    17
                )
            )

            # Rear wing
            pygame.draw.rect(
                screen,
                BLACK,
                (
                    rect.x - 5,
                    rect.bottom - 12,
                    rect.width + 10,
                    7
                )
            )

        elif self.style == "pickup":

            pygame.draw.rect(
                screen,
                self.color,
                rect,
                border_radius=5
            )

            # Cab
            pygame.draw.rect(
                screen,
                (50, 100, 130),
                (
                    rect.x + 5,
                    rect.y + 8,
                    rect.width - 10,
                    25
                ),
                border_radius=4
            )

            # Truck bed
            pygame.draw.rect(
                screen,
                self.color,
                (
                    rect.x + 5,
                    rect.y + 37,
                    rect.width - 10,
                    25
                )
            )

        else:

            # Generic vehicle
            pygame.draw.rect(
                screen,
                self.color,
                rect,
                border_radius=7
            )

            pygame.draw.rect(
                screen,
                (70, 140, 175),
                (
                    rect.x + 7,
                    rect.y + 10,
                    rect.width - 14,
                    20
                ),
                border_radius=4
            )

        # ----------------------------------------------------
        # Wheels
        # ----------------------------------------------------

        wheel_width = 8
        wheel_height = 18

        wheel_positions = [
            (
                rect.left - 4,
                rect.top + 13
            ),
            (
                rect.right - 4,
                rect.top + 13
            ),
            (
                rect.left - 4,
                rect.bottom - 31
            ),
            (
                rect.right - 4,
                rect.bottom - 31
            )
        ]

        for x, y in wheel_positions:

            pygame.draw.rect(
                screen,
                BLACK,
                (
                    x,
                    y,
                    wheel_width,
                    wheel_height
                ),
                border_radius=3
            )

        # Player arrow
        if self.is_player:

            pygame.draw.polygon(
                screen,
                WHITE,
                [
                    (rect.centerx, rect.top - 18),
                    (rect.centerx - 8, rect.top - 5),
                    (rect.centerx + 8, rect.top - 5)
                ]
            )


# ============================================================
# Moving obstacle
# ============================================================

class Obstacle:

    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.width = 45
        self.height = 45

        self.speed = random.uniform(
            1.5,
            4.0
        )

        self.direction = random.choice(
            [-1, 1]
        )

    def rect(self):

        return pygame.Rect(
            int(self.x - self.width / 2),
            int(self.y - self.height / 2),
            self.width,
            self.height
        )

    def update(self, player_speed):

        self.y += player_speed - self.speed

        # Obstacles move slightly side-to-side
        self.x += self.direction * 0.5

    def draw(self, screen):

        rect = self.rect()

        pygame.draw.rect(
            screen,
            (40, 40, 40),
            (
                rect.x + 4,
                rect.y + 4,
                rect.width,
                rect.height
            )
        )

        pygame.draw.rect(
            screen,
            ORANGE,
            rect,
            border_radius=4
        )

        # Warning stripes
        pygame.draw.line(
            screen,
            WHITE,
            rect.topleft,
            rect.bottomright,
            5
        )

        pygame.draw.line(
            screen,
            WHITE,
            rect.topright,
            rect.bottomleft,
            5
        )


# ============================================================
# Racing Game
# ============================================================

class RacingGame:

    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(
            "Curvy Road Racing"
        )

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(
            "arial",
            24
        )

        self.big_font = pygame.font.SysFont(
            "arial",
            60,
            bold=True
        )

        self.reset()

    # --------------------------------------------------------
    # Reset game
    # --------------------------------------------------------

    def reset(self):

        self.road_offset = 0

        # Player starts in center of road
        player_x = track_center(
            HEIGHT - 130,
            self.road_offset
        )

        self.player = Car(
            player_x,
            HEIGHT - 130,
            RED,
            is_player=True,
            style="sports"
        )

        # AI cars
        colors = [
            BLUE,
            YELLOW,
            GREEN,
            PURPLE,
            CYAN
        ]

        styles = [
            "muscle",
            "formula",
            "pickup",
            "sports",
            "muscle"
        ]

        self.ai_cars = []

        for i in range(NUM_AI_CARS):

            y = (
                HEIGHT
                - 350
                - i * 120
            )

            lane = i % 3

            left, right = road_bounds(
                y,
                self.road_offset
            )

            lane_width = ROAD_WIDTH / 3

            x = (
                left
                + lane_width * lane
                + lane_width / 2
            )

            car = Car(
                x,
                y,
                colors[i],
                style=styles[i]
            )

            car.ai_lane = lane

            self.ai_cars.append(car)

        # Obstacles
        self.obstacles = []

        for i in range(NUM_OBSTACLES):

            y = random.randint(
                -1500,
                -200
            )

            x = track_center(
                y,
                self.road_offset
            )

            lane = random.randint(0, 2)

            lane_width = ROAD_WIDTH / 3

            x += (
                (lane - 1)
                * lane_width
                + lane_width / 2
            )

            self.obstacles.append(
                Obstacle(x, y)
            )

        self.distance_traveled = 0

        self.position = 1

        self.game_over = False

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    def update(self):

        if self.game_over:
            return

        keys = pygame.key.get_pressed()

        # Player
        self.player.update_player(
            keys,
            self.road_offset
        )

        # Move the world
        self.road_offset += self.player.speed

        # Keep number manageable
        self.road_offset %= 100000

        self.distance_traveled += max(
            0,
            self.player.speed
        )

        # AI
        for car in self.ai_cars:

            car.update_ai(
                self.player.speed,
                self.obstacles,
                self.road_offset
            )

            # Keep AI on road
            left, right = road_bounds(
                car.y,
                self.road_offset
            )

            car.x = clamp(
                car.x,
                left + car.width / 2,
                right - car.width / 2
            )

        # Obstacles
        for obstacle in self.obstacles:

            obstacle.update(
                self.player.speed
            )

        # Recycle obstacles
        for obstacle in self.obstacles:

            if obstacle.y > HEIGHT + 100:

                obstacle.y = random.randint(
                    -1200,
                    -300
                )

                center = track_center(
                    obstacle.y,
                    self.road_offset
                )

                lane = random.randint(
                    0,
                    2
                )

                lane_width = ROAD_WIDTH / 3

                obstacle.x = (
                    center
                    + (lane - 1) * lane_width
                    + lane_width / 2
                )

        # ----------------------------------------------------
        # Collision detection
        # ----------------------------------------------------

        player_rect = self.player.rect()

        for obstacle in self.obstacles:

            if player_rect.colliderect(
                obstacle.rect()
            ):

                self.player.crashed = True
                self.player.speed = 0
                self.game_over = True

        for car in self.ai_cars:

            if player_rect.colliderect(
                car.rect()
            ):

                self.player.crashed = True
                self.player.speed = 0
                self.game_over = True

        # ----------------------------------------------------
        # Position
        # ----------------------------------------------------

        cars_ahead = 0

        for car in self.ai_cars:

            if car.y < self.player.y:
                cars_ahead += 1

        self.position = cars_ahead + 1

    # ========================================================
    # Drawing
    # ========================================================

    def draw_background(self):

        # Grass
        self.screen.fill(GRASS)

        # Draw road using horizontal slices.
        # This makes the road curve smoothly.
        slice_height = 10

        for y in range(
            0,
            HEIGHT,
            slice_height
        ):

            left, right = road_bounds(
                y,
                self.road_offset
            )

            # Road
            pygame.draw.rect(
                self.screen,
                ROAD,
                (
                    int(left),
                    y,
                    int(right - left) + 2,
                    slice_height + 1
                )
            )

            # Road edges
            pygame.draw.rect(
                self.screen,
                ROAD_EDGE,
                (
                    int(left),
                    y,
                    7,
                    slice_height + 1
                )
            )

            pygame.draw.rect(
                self.screen,
                ROAD_EDGE,
                (
                    int(right - 7),
                    y,
                    7,
                    slice_height + 1
                )
            )

        # Lane markings
        lane_width = ROAD_WIDTH / 3

        dash_length = 45
        gap = 35

        y = -dash_length + (
            self.road_offset % (dash_length + gap)
        )

        while y < HEIGHT:

            center = track_center(
                y,
                self.road_offset
            )

            # Draw two lane lines
            for lane in [1, 2]:

                x = (
                    center
                    - ROAD_WIDTH / 2
                    + lane * lane_width
                )

                pygame.draw.rect(
                    self.screen,
                    LANE_MARKING,
                    (
                        int(x - 3),
                        int(y),
                        6,
                        dash_length
                    )
                )

            y += dash_length + gap

    # --------------------------------------------------------
    # HUD
    # --------------------------------------------------------

    def draw_hud(self):

        speed = int(
            self.player.speed * 12
        )

        speed_text = self.font.render(
            f"Speed: {speed} mph",
            True,
            WHITE
        )

        self.screen.blit(
            speed_text,
            (20, 20)
        )

        position_text = self.font.render(
            f"Position: "
            f"{self.position}/{NUM_AI_CARS + 1}",
            True,
            WHITE
        )

        self.screen.blit(
            position_text,
            (20, 55)
        )

        distance_text = self.font.render(
            f"Distance: "
            f"{int(self.distance_traveled)}",
            True,
            WHITE
        )

        self.screen.blit(
            distance_text,
            (20, 90)
        )

        controls = self.font.render(
            "Arrow Keys / WASD: Drive",
            True,
            WHITE
        )

        self.screen.blit(
            controls,
            (20, HEIGHT - 40)
        )

    # --------------------------------------------------------
    # Game over screen
    # --------------------------------------------------------

    def draw_game_over(self):

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 170)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        title = "CRASH!"

        title_surface = self.big_font.render(
            title,
            True,
            WHITE
        )

        title_rect = title_surface.get_rect(
            center=(
                WIDTH / 2,
                HEIGHT / 2 - 50
            )
        )

        self.screen.blit(
            title_surface,
            title_rect
        )

        position_surface = self.font.render(
            f"You were in position "
            f"{self.position}",
            True,
            WHITE
        )

        position_rect = position_surface.get_rect(
            center=(
                WIDTH / 2,
                HEIGHT / 2 + 20
            )
        )

        self.screen.blit(
            position_surface,
            position_rect
        )

        restart_surface = self.font.render(
            "Press SPACE to restart",
            True,
            WHITE
        )

        restart_rect = restart_surface.get_rect(
            center=(
                WIDTH / 2,
                HEIGHT / 2 + 70
            )
        )

        self.screen.blit(
            restart_surface,
            restart_rect
        )

    # --------------------------------------------------------
    # Draw everything
    # --------------------------------------------------------

    def draw(self):

        self.draw_background()

        # Obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # AI cars
        for car in self.ai_cars:
            car.draw(self.screen)

        # Player
        self.player.draw(self.screen)

        self.draw_hud()

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    # ========================================================
    # Main loop
    # ========================================================

    def run(self):

        running = True

        while running:

            self.clock.tick(FPS)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if (
                        event.key == pygame.K_SPACE
                        and self.game_over
                    ):
                        self.reset()

            self.update()
            self.draw()

        pygame.quit()


# ============================================================
# Start
# ============================================================

if __name__ == "__main__":

    game = RacingGame()
    game.run()


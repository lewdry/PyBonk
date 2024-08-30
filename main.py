import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Load the collision sound
collision_sound = pygame.mixer.Sound("beep.wav")

# Screen dimensions
WIDTH, HEIGHT = 970, 580
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyBonk")

# Ball class
class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.radius = random.randint(10, 30)
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(self.radius, HEIGHT - self.radius)
        self.dx = random.choice([-1, 1]) * random.uniform(1, 2)  # Adjust speed
        self.dy = random.choice([-1, 1]) * random.uniform(1, 2)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.grabbed = False

    def move(self):
        if not self.grabbed:
            self.x += self.dx
            self.y += self.dy

            # Bounce off the walls
            if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
                self.dx = -self.dx
            if self.y - self.radius <= 0 or self.y + self.radius >= HEIGHT:
                self.dy = -self.dy

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def check_collision(self, other):
        distance = math.hypot(self.x - other.x, self.y - other.y)
        return distance < self.radius + other.radius

    def resolve_collision(self, other):
        if self.check_collision(other):
            collision_sound.play()
            self.dx, other.dx = other.dx, self.dx
            self.dy, other.dy = other.dy, self.dy

    def check_grabbed(self, mouse_pos):
        distance = math.hypot(self.x - mouse_pos[0], self.y - mouse_pos[1])
        return distance < self.radius

# Create a list of balls
balls = [Ball() for _ in range(3)]

# Function to reset all balls
def reset_game():
    for ball in balls:
        ball.reset()

# Main loop
running = True
clock = pygame.time.Clock()

grabbed_ball = None
mouse_start_pos = None
last_click_time = 0

while running:
    screen.fill((255, 255, 255))  # Clear screen with white background

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            current_time = time.time()
            if current_time - last_click_time < 0.3:  # Detect double-click (0.3 seconds)
                reset_game()
            last_click_time = current_time

            mouse_pos = pygame.mouse.get_pos()
            for ball in balls:
                if ball.check_grabbed(mouse_pos):
                    grabbed_ball = ball
                    ball.grabbed = True
                    mouse_start_pos = mouse_pos
                    break
        elif event.type == pygame.MOUSEBUTTONUP:
            if grabbed_ball:
                mouse_pos = pygame.mouse.get_pos()
                grabbed_ball.dx = (mouse_pos[0] - mouse_start_pos[0]) / 10
                grabbed_ball.dy = (mouse_pos[1] - mouse_start_pos[1]) / 10
                grabbed_ball.grabbed = False
                grabbed_ball = None
        elif event.type == pygame.MOUSEMOTION:
            if grabbed_ball:
                grabbed_ball.x, grabbed_ball.y = pygame.mouse.get_pos()

    # Move and draw balls
    for i, ball in enumerate(balls):
        ball.move()
        ball.draw(screen)
        for other_ball in balls[i+1:]:
            ball.resolve_collision(other_ball)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

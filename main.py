import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Load the collision sound
collision_sound = pygame.mixer.Sound("beep.wav")
collision_sound.set_volume(0.2)  # Set volume to 20% of the maximum volume

# Screen dimensions
WIDTH, HEIGHT = 965, 580
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyBonk")

# Font for displaying text
font = pygame.font.Font(None, 30)


# Ball class
class Ball:

    def __init__(self):
        self.reset()

    def reset(self):
        self.radius = random.randint(10, 30)
        self.mass = math.pi * self.radius**2  # Mass proportional to area (radius^2)
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(self.radius, HEIGHT - self.radius)
        self.dx = random.choice([-1, 1]) * random.uniform(1, 2)  # Adjust speed
        self.dy = random.choice([-1, 1]) * random.uniform(1, 2)
        self.color = (random.randint(0, 255), random.randint(0, 255),
                      random.randint(0, 255))
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
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)),
                           self.radius)

    def check_collision(self, other):
        distance = math.hypot(self.x - other.x, self.y - other.y)
        return distance < self.radius + other.radius

    def resolve_collision(self, other):
        if self.check_collision(other):
            collision_sound.play()

            # Calculate the collision normal vector
            normal_x = other.x - self.x
            normal_y = other.y - self.y
            normal_length = math.hypot(normal_x, normal_y)
            normal_x /= normal_length
            normal_y /= normal_length

            # Calculate the relative velocity
            rel_vel_x = other.dx - self.dx
            rel_vel_y = other.dy - self.dy

            # Calculate the velocity along the normal
            vel_along_normal = rel_vel_x * normal_x + rel_vel_y * normal_y

            # Prevent balls from sticking together (if they are already separating, don't resolve the collision)
            if vel_along_normal > 0:
                return

            # Calculate the restitution (elasticity)
            restitution = 1  # Elastic collision

            # Calculate the impulse scalar
            impulse = -(1 + restitution) * vel_along_normal
            impulse /= 1 / self.mass + 1 / other.mass

            # Apply the impulse to the balls' velocities
            impulse_x = impulse * normal_x
            impulse_y = impulse * normal_y

            self.dx -= impulse_x / self.mass
            self.dy -= impulse_y / self.mass
            other.dx += impulse_x / other.mass
            other.dy += impulse_y / other.mass

    def check_grabbed(self, mouse_pos):
        distance = math.hypot(self.x - mouse_pos[0], self.y - mouse_pos[1])
        return distance < self.radius


# Create a list of balls
balls = [Ball() for _ in range(1)]


# Function to reset all balls and the collision counter
def reset_game():
    global collision_count
    for ball in balls:
        ball.reset()
    collision_count = 0


# Initialize collision count
collision_count = 0

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
        for other_ball in balls[i + 1:]:
            if ball.check_collision(other_ball):
                ball.resolve_collision(other_ball)
                collision_count += 1

    # Display the collision counter
    counter_text = font.render(f"Collisions: {collision_count}", True,
                               (0, 0, 0))
    screen.blit(counter_text, (WIDTH - counter_text.get_width() - 10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

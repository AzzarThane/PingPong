from pygame import *
from random import randint, choice
import math

# Initialize mixer and font
mixer.init()
font.init()

# Load sounds
bounce_sfx = mixer.Sound("bounce.wav")
explosion = mixer.Sound("explosion.wav")

# Images
img_ball = "Ball.png"
img_racket = "Racket.png"

# Taunt messages
taunts = [
    "Ты играешь как сонная черепаха!",
    "Моя бабушка играет лучше!",
    "Это всё? Серьёзно?",
    "Попробуй не проиграть в этот раз!",
    "Даже не близко...",
    "Ты вообще пытаешься?",
    "Грустное зрелище...",
    "Может, тебе в шашки?",
    "Я плачу от твоей игры!",
    "Позор! Позор! Позор!"
]

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__()
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update_r(self):
        keys = key.get_pressed()
        if keys[K_UP] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[K_DOWN] and self.rect.y < win_height - self.rect.height:
            self.rect.y += self.speed
    
    def update_l(self):
        keys = key.get_pressed()
        if keys[K_w] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[K_s] and self.rect.y < win_height - self.rect.height:
            self.rect.y += self.speed

class Ball(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, speed_x, speed_y):
        super().__init__(player_image, player_x, player_y, size_x, size_y, 0)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.last_collision = 0
    
    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Bounce off top and bottom
        if self.rect.y <= 0 or self.rect.y >= win_height - self.rect.height:
            self.speed_y *= -1
            bounce_sfx.play()
        
        # Paddle collision with cooldown
        current_time = time.get_ticks()
        if (sprite.collide_rect(self, racket1) or sprite.collide_rect(self, racket2)) and current_time - self.last_collision > 500:
            self.speed_x *= -1
            bounce_sfx.play()
            self.last_collision = current_time

class Arrow(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y):
        super().__init__(player_image, player_x, player_y, size_x, size_y, 0)
        self.original_image = self.image
        self.angle = 0
        self.rotating = True
        self.rotation_speed = randint(30, 100)
        self.current_speed = self.rotation_speed
        self.slowdown_start_time = 0
        self.slowdown_duration = randint(1500, 2500)  # Random slowdown
    
    def update(self):
        if self.rotating:
            if self.slowdown_start_time > 0:
                elapsed = time.get_ticks() - self.slowdown_start_time
                if elapsed < self.slowdown_duration:
                    progress = elapsed / self.slowdown_duration
                    self.current_speed = self.rotation_speed * (1 - progress)
                else:
                    self.current_speed = 0
                    self.rotating = False
            self.angle = (self.angle + self.current_speed) % 360
            self.image = transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=(win_width//2, win_height//2))
    
    def start_slowdown(self):
        self.slowdown_start_time = time.get_ticks()
    
    def get_angle(self):
        return self.angle % 360

# Game setup
win_width, win_height = 700, 500
display.set_caption("Ping Pong")
window = display.set_mode((win_width, win_height))
BG_COLOR = (0, 200, 255)
TEXT_COLOR = (255, 255, 255)
game_font = font.Font(None, 36)

# Initial sprites
racket1 = Player(img_racket, 30, 200, 15, 150, 10)
racket2 = Player(img_racket, win_width-80, 200, 15, 150, 10)
ball = Ball(img_ball, win_width//2, win_height//2, 50, 50, 0, 0)
arrow = Arrow("arrow.png", win_width//2, win_height//2, 100, 50)

# Game variables
score_left = 0
score_right = 0
difficulty_level = 1

def draw_text(message, y_offset=0):
    text = game_font.render(message, True, TEXT_COLOR)
    text_rect = text.get_rect(center=(win_width//2, win_height//2 + y_offset))
    window.blit(text, text_rect)

def countdown():
    for i in range(3, 0, -1):
        window.fill(BG_COLOR)
        draw_text(f"{i}...")
        display.update()
        time.delay(1000)

def start_round():
    global difficulty_level
    arrow.rotating = True
    arrow.rotation_speed = randint(30, 100)
    arrow.slowdown_duration = randint(1500, 2500)
    arrow.current_speed = arrow.rotation_speed
    arrow.slowdown_start_time = time.get_ticks()
    arrow.angle = 0
    
    # Arrow rotation phase
    running = True
    while running:
        for e in event.get():
            if e.type == QUIT:
                return False
        
        window.fill(BG_COLOR)
        racket1.reset()
        racket2.reset()
        arrow.update()
        arrow.reset()
        
        # Display difficulty
        draw_text(f"Level: {difficulty_level}", -60)
        display.update()
        
        if not arrow.rotating:
            running = False
        time.delay(16)
    
    # Calculate ball direction
    final_angle = arrow.get_angle()
    speed = 6 + (difficulty_level - 1) * 2  # Increase speed with difficulty
    angle_rad = math.radians(final_angle)
    ball.speed_x = speed * math.cos(angle_rad)
    ball.speed_y = speed * math.sin(angle_rad)
    
    # Reset ball position
    ball.rect.center = (win_width//2, win_height//2)
    return True

def show_taunt():
    draw_text(choice(taunts))
    display.update()
    time.delay(2000)

# Main game loop
Run = True
countdown()
start_round()

while Run:
    for e in event.get():
        if e.type == QUIT:
            Run = False
    
    # Update sprites
    racket1.update_l()
    racket2.update_r()
    ball.update()
    
    # Check for goal
    if ball.rect.x < -50 or ball.rect.x > win_width + 50:
        # Update scores
        if ball.rect.x < 0:
            score_right += 1
        else:
            score_left += 1
        
        # Update difficulty
        total_points = score_left + score_right
        difficulty_level = 1 + (total_points // 3)
        
        # Adjust paddle size
        new_height = 150 - (difficulty_level - 1) * 20
        new_height = max(50, new_height)
        for racket in [racket1, racket2]:
            racket.image = transform.scale(image.load(img_racket), (15, new_height))
            racket.rect = racket.image.get_rect(center=racket.rect.center)
            racket.rect.y = max(5, min(racket.rect.y, win_height - new_height - 5))
        
        # Reset game
        explosion.play()
        window.fill(BG_COLOR)
        show_taunt()
        ball.rect.center = (win_width//2, win_height//2)
        ball.speed_x = ball.speed_y = 0
        countdown()
        start_round()
    
    # Drawing
    window.fill(BG_COLOR)
    # Display scores
    score_text = game_font.render(f"{score_left} - {score_right}", True, TEXT_COLOR)
    window.blit(score_text, (win_width//2 - score_text.get_width()//2, 10))
    # Display difficulty
    level_text = game_font.render(f"Level: {difficulty_level}", True, TEXT_COLOR)
    window.blit(level_text, (10, 10))
    
    racket1.reset()
    racket2.reset()
    ball.reset()
    display.update()
    time.delay(16)

quit()
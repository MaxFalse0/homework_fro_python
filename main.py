import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Смешная пушка")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

try:
    banana_img = pygame.image.load("banana.png")
    banana_img = pygame.transform.scale(banana_img, (20, 20))
    apple_img = pygame.image.load("apple.png")
    apple_img = pygame.transform.scale(apple_img, (20, 20))
    pear_img = pygame.image.load("pear.png")
    pear_img = pygame.transform.scale(pear_img, (20, 20))
    cleaner_img = pygame.image.load("cleaner.png")
    cleaner_img = pygame.transform.scale(cleaner_img, (50, 50))
    fly_img = pygame.image.load("fly.png")
    fly_img = pygame.transform.scale(fly_img, (30, 30))
except pygame.error as e:
    print(f"Ошибка при загрузке изображения: {e}")

font = pygame.font.Font(None, 50)


class Projectile:
    def __init__(self, x, y, angle, type="banana"):
        self.x = x
        self.y = y
        self.angle = math.radians(angle)
        self.type = type
        self.speed = 30 if type == "banana" else 40 if type == "apple" else 20
        self.vx = self.speed * math.cos(self.angle)
        self.vy = -self.speed * math.sin(self.angle)
        self.gravity = 0.4 if type != "pear" else 0.6
        self.bounces = 3 if type != "apple" else 1
        self.image = banana_img if type == "banana" else apple_img if type == "apple" else pear_img

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity

        if self.x <= 0 or self.x >= WIDTH - 20:
            self.vx = -self.vx
            self.bounces -= 1
        if self.y <= 0:
            self.vy = -self.vy
            self.bounces -= 1

        if self.bounces < 0 or self.y > HEIGHT:
            return False
        return True

    def draw(self):
        screen.blit(self.image, (int(self.x), int(self.y)))


class Cannon:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT - 50
        self.angle = 45
        self.angle_speed = 2
        self.projectile_type = "banana"  # Тип снаряда по умолчанию

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.angle = min(90, self.angle + self.angle_speed)
        if keys[pygame.K_RIGHT]:
            self.angle = max(0, self.angle - self.angle_speed)
        if keys[pygame.K_1]:
            self.projectile_type = "banana"
        if keys[pygame.K_2]:
            self.projectile_type = "apple"
        if keys[pygame.K_3]:
            self.projectile_type = "pear"

    def draw(self):
        pygame.draw.rect(screen, BLACK, (self.x - 20, self.y - 10, 40, 20))
        pygame.draw.line(screen, BLACK, (self.x, self.y),
                         (self.x + 50 * math.cos(math.radians(self.angle)),
                          self.y - 50 * math.sin(math.radians(self.angle))), 5)


class Letter:
    def __init__(self, letter, index, total):
        self.letter = letter
        self.x = 50 + (WIDTH - 100) // (total - 1) * index
        self.y = 50
        self.size = 40

    def draw(self):
        text = font.render(self.letter, True, BLACK)
        screen.blit(text, (self.x, self.y))


class Cleaner:
    def __init__(self, is_fast=False):
        self.x = WIDTH
        self.y = HEIGHT - 100
        self.speed = 8 if is_fast else 3  # Быстрая или мощная
        self.active = False
        self.target_letter = None
        self.target_x = 0
        self.progress = 0
        self.is_fast = is_fast

    def start(self, text):
        if text:
            self.active = True
            self.target_letter = random.choice(text)
            self.x = WIDTH
            self.progress = 0
            self.target_x = 50 + text.index(self.target_letter) * 30

    def update(self, text):
        if self.active:
            if self.x > self.target_x:
                self.x -= self.speed
            else:
                self.progress += 1
                if self.progress > 30:
                    if self.target_letter in text:
                        if self.is_fast:
                            text = text.replace(self.target_letter, "", 1)
                        else:
                            text = text.replace(self.target_letter, "", min(3, text.count(self.target_letter)))
                    self.active = False
                    self.x = WIDTH
        return text

    def draw(self):
        if self.active:
            screen.blit(cleaner_img, (int(self.x), int(self.y)))


class Fly:
    def __init__(self):
        self.x = random.randint(200, WIDTH - 50)
        self.y = random.randint(100, HEIGHT - 100)
        self.speed_x = random.choice([-2, 2])
        self.speed_y = random.choice([-2, 2])

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x < 200 or self.x > WIDTH - 50:
            self.speed_x = -self.speed_x
        if self.y < 100 or self.y > HEIGHT - 100:
            self.speed_y = -self.speed_y

    def draw(self):
        screen.blit(fly_img, (int(self.x), int(self.y)))


cannon = Cannon()
projectiles = []
letters = [Letter(chr(65 + i), i, 26) for i in range(26)]
text_typed = ""
cleaners = []
flies = [Fly() for _ in range(3)]  # 3 мухи
timer = random.randint(5, 60) * 60  # Таймер в кадрах (60 fps)

running = True
clock = pygame.time.Clock()

while running:
    screen.fill(WHITE)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                projectiles.append(Projectile(cannon.x, cannon.y, cannon.angle, cannon.projectile_type))
            elif event.key == pygame.K_BACKSPACE:
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    new_cleaner = Cleaner(is_fast=True)  # Быстрая уборщица
                else:
                    new_cleaner = Cleaner(is_fast=False)  # Мощная уборщица
                new_cleaner.start(text_typed)
                cleaners.append(new_cleaner)

    cannon.update(keys)

    for projectile in projectiles[:]:
        if not projectile.update():
            projectiles.remove(projectile)
            continue

        proj_rect = pygame.Rect(projectile.x, projectile.y, 20, 20)
        for fly in flies:
            fly_rect = pygame.Rect(fly.x, fly.y, 30, 30)
            if proj_rect.colliderect(fly_rect):
                if projectile in projectiles:
                    projectiles.remove(projectile)
                break
        else:
            for letter in letters:
                letter_rect = pygame.Rect(letter.x - 10, letter.y - 10, letter.size + 20, letter.size + 20)
                if proj_rect.colliderect(letter_rect):
                    text_typed += letter.letter * (2 if projectile.type == "pear" else 1)
                    if projectile in projectiles:
                        projectiles.remove(projectile)
                    break

    for cleaner in cleaners[:]:
        text_typed = cleaner.update(text_typed)
        if not cleaner.active:
            cleaners.remove(cleaner)

    for fly in flies:
        fly.update()

    timer -= 1
    if timer <= 0:
        text_typed = ""
        timer = random.randint(5, 60) * 60

    cannon.draw()
    for letter in letters:
        letter.draw()
    for projectile in projectiles:
        projectile.draw()
    for cleaner in cleaners:
        cleaner.draw()
    for fly in flies:
        fly.draw()

    text_surface = font.render(text_typed, True, BLACK)
    screen.blit(text_surface, (50, HEIGHT - 100))
    timer_surface = font.render(f"Timer: {timer // 60}", True, BLACK)
    screen.blit(timer_surface, (WIDTH - 150, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

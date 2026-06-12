import pygame as pg
import random

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

BLACK = (0, 0, 0)
WHITE = (200, 220, 180)
GREEN = (50, 200, 50)
DARK_GREEN = (0, 60, 0)
RED = (200, 40, 40)
YELLOW = (220, 220, 0)
BLUE = (40, 100, 200)
ORANGE = (200, 120, 40)
GRAY = (60, 60, 60)


class Menu:
    def __init__(self, options, title=""):
        self.options = options
        self.selected = 0
        self.title = title
        self.font = pg.font.SysFont('Arial', 28)
        self.big_font = pg.font.SysFont('Arial', 48)

    def draw(self, screen):
        screen.fill(BLACK)
        if self.title:
            t = self.big_font.render(self.title, True, GREEN)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 150))
        for i, opt in enumerate(self.options):
            color = YELLOW if i == self.selected else WHITE
            prefix = "> " if i == self.selected else "  "
            text = self.font.render(f"{prefix}{opt}", True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2 + 10, 300 + i * 60))
        instr = self.font.render("Usa arriba/abajo para navegar, ENTER para seleccionar", True, GRAY)
        screen.blit(instr, (SCREEN_WIDTH // 2 - instr.get_width() // 2, 550))


class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.3, 1.2)

    def update(self):
        self.x -= self.speed
        if self.x < 0:
            self.x = SCREEN_WIDTH
            self.y = random.randint(0, SCREEN_HEIGHT)

    def draw(self, surface):
        pg.draw.circle(surface, GRAY, (int(self.x), int(self.y)), 1)


class Player(pg.sprite.Sprite):
    def __init__(self, x, y, w, h, color):
        super().__init__()
        self.image = pg.Surface((w, h), pg.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = 0
        self.vy = 0

    def wrap(self):
        if self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH
        if self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
        if self.rect.bottom < 0:
            self.rect.top = SCREEN_HEIGHT
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.bottom = 0

    def clamp(self):
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH


class Projectile(pg.sprite.Sprite):
    def __init__(self, x, y, vx, vy, w, h, color):
        super().__init__()
        self.image = pg.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = vx
        self.vy = vy

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

    def off_screen(self):
        return (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
                self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT)


class Enemy(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.vx = 0
        self.vy = 0

    def wrap(self, margin=80):
        if self.rect.right < -margin:
            self.rect.left = SCREEN_WIDTH + margin
        if self.rect.left > SCREEN_WIDTH + margin:
            self.rect.right = -margin
        if self.rect.bottom < -margin:
            self.rect.top = SCREEN_HEIGHT + margin
        if self.rect.top > SCREEN_HEIGHT + margin:
            self.rect.bottom = -margin

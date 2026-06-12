import pygame as pg
import os
import math
import random
from bricksteorid import *

# Brandhorst Beaumont C.I: 28.387.689
# Kleberson Lopez C.I: 29.982.554
# Jefferson Irausquin C.I: 26.067.444

os.environ['SDL_VIDEO_WINDOW_POS'] = 'x,y'

pg.init()

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Arteroids & Brick Blaster")
clock = pg.time.Clock()

font = pg.font.SysFont('Arial', 28)
big_font = pg.font.SysFont('Arial', 48)

class Ship(Player):
    def __init__(self):
        super().__init__(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 30, 30, GREEN)
        self.image = pg.Surface((30, 30), pg.SRCALPHA)
        tip = (30, 15)
        top = (2, 0)
        bottom = (2, 30)
        pg.draw.polygon(self.image, GREEN, [tip, top, bottom])
        pg.draw.polygon(self.image, DARK_GREEN, [tip, top, bottom], 2)
        self.original = self.image.copy()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.angle = 0
        self.cooldown = 0

    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.angle += 5
        if keys[pg.K_RIGHT]:
            self.angle -= 5
        if keys[pg.K_UP]:
            rad = math.radians(self.angle)
            self.vx += math.cos(rad) * 0.25
            self.vy -= math.sin(rad) * 0.25
        self.vx *= 0.99
        self.vy *= 0.99
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.wrap()
        self.image = pg.transform.rotate(self.original, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        if self.cooldown > 0:
            self.cooldown -= 1

    def shoot(self):
        if self.cooldown == 0:
            self.cooldown = 15
            rad = math.radians(self.angle)
            return Bullet(self.rect.centerx, self.rect.centery, rad)
        return None

class Bullet(Projectile):
    def __init__(self, x, y, angle):
        vx = math.cos(angle) * 10
        vy = -math.sin(angle) * 10
        super().__init__(x, y, vx, vy, 8, 4, YELLOW)

    def update(self):
        super().update()
        if self.off_screen():
            self.kill()

class Asteroid(Enemy):
    def __init__(self):
        super().__init__()
        size = random.randint(30, 60)
        self.image = pg.Surface((size, size), pg.SRCALPHA)
        points = []
        for i in range(8):
            a = math.radians(i * 45 + random.randint(-15, 15))
            r = size // 2 + random.randint(-5, 5)
            points.append((size // 2 + r * math.cos(a), size // 2 + r * math.sin(a)))
        pg.draw.polygon(self.image, GRAY, points)
        pg.draw.polygon(self.image, WHITE, points, 2)
        self.rect = self.image.get_rect()
        side = random.randint(0, 3)
        if side == 0:
            self.rect.x = -size
            self.rect.y = random.randint(0, SCREEN_HEIGHT)
        elif side == 1:
            self.rect.x = SCREEN_WIDTH + size
            self.rect.y = random.randint(0, SCREEN_HEIGHT)
        elif side == 2:
            self.rect.x = random.randint(0, SCREEN_WIDTH)
            self.rect.y = -size
        else:
            self.rect.x = random.randint(0, SCREEN_WIDTH)
            self.rect.y = SCREEN_HEIGHT + size
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 3)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.rotation_speed = random.uniform(-3, 3)
        self.angle = 0

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.angle += self.rotation_speed
        self.wrap()

class Arteroids:
    def __init__(self):
        self.ship = Ship()
        self.all_sprites = pg.sprite.Group(self.ship)
        self.asteroids = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.stars = [Star() for _ in range(60)]
        self.score = 0
        self.lives = 3
        self.state = "playing"
        self.spawn_timer = 0
        self.difficulty = 2000

    def run(self):
        game = True
        while game:
            dt = clock.tick(FPS)
            self.spawn_timer += dt
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return "quit"
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return "menu"
                    if event.key == pg.K_r and self.state == "game_over":
                        return "restart"
                    if event.key == pg.K_SPACE and self.state == "playing":
                        bullet = self.ship.shoot()
                        if bullet:
                            self.all_sprites.add(bullet)
                            self.bullets.add(bullet)
            if self.state == "playing":
                self.all_sprites.update()
                if self.spawn_timer >= self.difficulty:
                    self.spawn_timer = 0
                    self.difficulty = max(500, self.difficulty - 50)
                    ast = Asteroid()
                    self.all_sprites.add(ast)
                    self.asteroids.add(ast)
                hits = pg.sprite.groupcollide(self.bullets, self.asteroids, True, True)
                for _, asts in hits.items():
                    self.score += 100 * len(asts)
                hits = pg.sprite.spritecollide(self.ship, self.asteroids, True)
                if hits:
                    self.lives -= len(hits)
                    if self.lives <= 0:
                        self.state = "game_over"
            for star in self.stars:
                star.update()
            screen.fill(BLACK)
            for star in self.stars:
                star.draw(screen)
            self.all_sprites.draw(screen)
            score_surf = font.render(f"Score: {self.score}", True, GREEN)
            screen.blit(score_surf, (10, 10))
            lives_surf = font.render(f"Vidas: {self.lives}", True, GREEN)
            screen.blit(lives_surf, (SCREEN_WIDTH - lives_surf.get_width() - 10, 10))
            if self.state == "game_over":
                overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(180)
                overlay.fill(BLACK)
                screen.blit(overlay, (0, 0))
                go = big_font.render("GAME OVER", True, RED)
                sf = font.render(f"Puntaje: {self.score}", True, WHITE)
                rl = font.render("Presiona R para reiniciar o ESC para menu", True, WHITE)
                screen.blit(go, (SCREEN_WIDTH // 2 - go.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
                screen.blit(sf, (SCREEN_WIDTH // 2 - sf.get_width() // 2, SCREEN_HEIGHT // 2))
                screen.blit(rl, (SCREEN_WIDTH // 2 - rl.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            pg.display.flip()
        return "quit"

class Paddle(Player):
    def __init__(self):
        super().__init__(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30, 120, 14, GREEN)
        self.rect.midbottom = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)

    def update(self):
        mouse_x, _ = pg.mouse.get_pos()
        self.rect.centerx = mouse_x
        self.clamp()

class Ball(Projectile):
    def __init__(self):
        super().__init__(0, 0, 0, 0, 16, 16, WHITE)
        self.image = pg.Surface((16, 16), pg.SRCALPHA)
        pg.draw.circle(self.image, WHITE, (8, 8), 7)
        self.rect = self.image.get_rect()
        self.launched = False

    def reset(self):
        self.launched = False
        self.vx = 0
        self.vy = 0

    def launch(self):
        self.launched = True
        angle = random.uniform(-0.4, 0.4)
        speed = 6
        self.vx = speed * math.sin(angle)
        self.vy = -speed * math.cos(angle)

    def update(self):
        if not self.launched:
            return
        super().update()
        if self.rect.left <= 0:
            self.rect.left = 0
            self.vx = -self.vx
        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.vx = -self.vx
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy = -self.vy

class Brick(Enemy):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pg.Surface((100, 24))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class BrickBlaster:
    def __init__(self):
        self.paddle = Paddle()
        self.ball = Ball()
        self.all_sprites = pg.sprite.Group(self.paddle, self.ball)
        self.bricks = pg.sprite.Group()
        self.score = 0
        self.lives = 3
        self.state = "playing"
        self._create_bricks()
        self.all_sprites.add(self.bricks)

    def _create_bricks(self):
        rows = 5
        cols = 10
        gap = 6
        brick_w = 100
        brick_h = 24
        total_w = cols * brick_w + (cols - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        row_colors = [RED, ORANGE, YELLOW, GREEN, BLUE]
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (brick_w + gap)
                y = 50 + row * (brick_h + gap)
                self.bricks.add(Brick(x, y, row_colors[row]))

    def run(self):
        game = True
        while game:
            clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return "quit"
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return "menu"
                    if event.key == pg.K_r and self.state in ("game_over", "win"):
                        return "restart"
                    if event.key == pg.K_SPACE and not self.ball.launched and self.state == "playing":
                        self.ball.launch()
                if event.type == pg.MOUSEBUTTONDOWN:
                    if not self.ball.launched and self.state == "playing":
                        self.ball.launch()
            if not self.ball.launched and self.state == "playing":
                self.ball.rect.midbottom = (self.paddle.rect.centerx, self.paddle.rect.top - 2)
            if self.state == "playing":
                self.all_sprites.update()
                if self.ball.launched and self.ball.rect.colliderect(self.paddle.rect) and self.ball.vy > 0:
                    hit_pos = (self.ball.rect.centerx - self.paddle.rect.centerx) / 60
                    angle = hit_pos * math.radians(60)
                    speed = math.sqrt(self.ball.vx ** 2 + self.ball.vy ** 2)
                    self.ball.vx = speed * math.sin(angle)
                    self.ball.vy = -speed * math.cos(angle)
                    self.ball.rect.bottom = self.paddle.rect.top
                hits = pg.sprite.spritecollide(self.ball, self.bricks, False)
                if hits:
                    brick = hits[0]
                    dx = (self.ball.rect.centerx - brick.rect.centerx) / brick.rect.width
                    dy = (self.ball.rect.centery - brick.rect.centery) / brick.rect.height
                    if abs(dx) > abs(dy):
                        self.ball.vx = -self.ball.vx
                    else:
                        self.ball.vy = -self.ball.vy
                    brick.kill()
                    self.score += 10
                    if len(self.bricks) == 0:
                        self.state = "win"
                if self.ball.launched and self.ball.rect.top > SCREEN_HEIGHT:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = "game_over"
                    else:
                        self.ball.reset()
            screen.fill(BLACK)
            self.all_sprites.draw(screen)
            score_surf = font.render(f"Score: {self.score}", True, GREEN)
            screen.blit(score_surf, (10, 10))
            lives_surf = font.render(f"Vidas: {self.lives}", True, GREEN)
            screen.blit(lives_surf, (SCREEN_WIDTH - lives_surf.get_width() - 10, 10))
            if not self.ball.launched and self.state == "playing":
                instr = font.render("Click o ESPACIO para lanzar", True, GREEN)
                screen.blit(instr, (SCREEN_WIDTH // 2 - instr.get_width() // 2, SCREEN_HEIGHT // 2 + 80))
            if self.state in ("game_over", "win"):
                overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(180)
                overlay.fill(BLACK)
                screen.blit(overlay, (0, 0))
                if self.state == "game_over":
                    msg = big_font.render("GAME OVER", True, RED)
                else:
                    msg = big_font.render("VICTORIA!", True, YELLOW)
                sf = font.render(f"Puntaje: {self.score}", True, WHITE)
                rl = font.render("Presiona R para reiniciar o ESC para menu", True, WHITE)
                screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
                screen.blit(sf, (SCREEN_WIDTH // 2 - sf.get_width() // 2, SCREEN_HEIGHT // 2))
                screen.blit(rl, (SCREEN_WIDTH // 2 - rl.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            pg.display.flip()
        return "quit"

if __name__ == "__main__":
    menu = Menu(["1. Arteroids (Asteroids)", "2. Brick Blaster", "3. Salir"], "ARTEROIDS & BRICK BLASTER")
    running = True
    while running:
        menu_active = True
        while menu_active:
            clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    menu_active = False
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        menu.selected = (menu.selected - 1) % len(menu.options)
                    if event.key == pg.K_DOWN:
                        menu.selected = (menu.selected + 1) % len(menu.options)
                    if event.key == pg.K_RETURN:
                        if menu.selected == 0:
                            result = Arteroids().run()
                            if result == "quit":
                                menu_active = False
                                running = False
                        elif menu.selected == 1:
                            result = BrickBlaster().run()
                            if result == "quit":
                                menu_active = False
                                running = False
                        elif menu.selected == 2:
                            menu_active = False
                            running = False
            menu.draw(screen)
            pg.display.flip()
    pg.quit()

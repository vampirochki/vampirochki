import pygame
from pygame import *
from random import randint

pygame.init()

info = display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
window = display.set_mode((WIDTH, HEIGHT, FULLSCREEN))
display.set_caption("Космічний захисник")

clock = time.Clock()
FPS = 60

try:
    background = transform.scale(image.load("galaxy.jpg"), (WIDTH, HEIGHT))
except:
    background = Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        color = int(255 * (1 - y / HEIGHT) * 0.3)
        draw.line(background, (0, 0, color), (0, y), (WIDTH, y))

font.init()
font1 = font.SysFont("Arial", 36)
font_large = font.SysFont("Arial", 48)
font_medium = font.SysFont("Arial", 24)
score = 0
lost = 3

game_state = "playing"

class GameSprite(sprite.Sprite):
    def __init__(self, image_path, x, y, speed, width, height):
        super().__init__()
        try:
            self.image = transform.scale(image.load(image_path), (width, height))
        except:
            self.image = Surface((width, height))
            if "rocket" in image_path:
                self.image.fill((0, 255, 0))
            elif "steroid" in image_path:
                self.image.fill((139, 69, 19))
            elif "bullet" in image_path:
                self.image.fill((255, 255, 0))
        
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
 
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, image_path, x, y, speed, width, height):
        super().__init__(image_path, x, y, speed, width, height)
        self.last_shot = 0
        self.shoot_delay = 150
        self.invulnerable_time = 0
    
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < WIDTH - self.rect.width - 5:
            self.rect.x += self.speed
        if keys[K_UP] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[K_DOWN] and self.rect.y < HEIGHT - self.rect.height - 5:
            self.rect.y += self.speed
        
        if keys[K_SPACE]:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot > self.shoot_delay:
                self.fire()
                self.last_shot = current_time

    def fire(self):
        bullet = Bullet("bullet.png", self.rect.centerx - 7, self.rect.top, -8, 15, 20)
        bullets.add(bullet)

class Asteroid(GameSprite):
    def __init__(self, image_path, x, y, speed, width, height):
        super().__init__(image_path, x, y, speed, width, height)
        self.rotation = 0
        self.rotation_speed = randint(-5, 5)
        self.size = randint(30, 60)
        self.image = Surface((self.size, self.size))
        self.image.fill((139, 69, 19))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
 
    def update(self):
        global lost
        self.rect.y += self.speed
        self.rect.x += randint(-1, 1)
        self.rotation += self.rotation_speed
        
        if self.rect.y > HEIGHT:
            self.rect.y = -randint(80, 120)
            self.rect.x = randint(50, WIDTH - 80)
            lost += 1

class Boss(GameSprite):
    def __init__(self, image_path, x, y, speed, width, height):
        super().__init__(image_path, x, y, speed, width, height)
        self.max_health = 200
        self.health = self.max_health
        self.direction = 1  
        self.last_shot = 0
        self.shoot_delay = 800  
        self.act = 1  
        self.act_change_health = 100 
        
        self.image = Surface((width, height))
        self.image.fill((200, 0, 0))  
        
    def update(self):
        self.rect.x += self.speed * self.direction

        if self.rect.x <= 0 or self.rect.x >= WIDTH - self.rect.width:
            self.direction *= -1
            self.rect.y += 20  
        
        if self.rect.y > HEIGHT // 3:
            self.rect.y = HEIGHT // 3
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.fire()
            self.last_shot = current_time
        
        if self.health <= self.act_change_health and self.act == 1:
            self.act = 2
            self.speed += 2  
            self.shoot_delay = 500 
            self.image.fill((255, 100, 100))
    
    def fire(self):
        if self.act == 1:

            boss_bullet = BossBullet("boss_bullet.png", 
                                   self.rect.centerx - 15, 
                                   self.rect.bottom, 
                                   6, 30, 30, 0)
            boss_bullets.add(boss_bullet)
        else:
            angles = [-30, 0, 30]
            for angle in angles:
                boss_bullet = BossBullet("boss_bullet.png", 
                                       self.rect.centerx - 15, 
                                       self.rect.bottom, 
                                       6, 30, 30, angle)
                boss_bullets.add(boss_bullet)
    
    def take_damage(self, damage=10):
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True
        return False
    
    def draw_health_bar(self, surface):
        bar_width = 200
        bar_height = 10
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = 20

        pygame.draw.rect(surface, (100, 100, 100), 
                        (bar_x, bar_y, bar_width, bar_height))

        health_ratio = max(0, self.health / self.max_health)
        health_width = int(bar_width * health_ratio)
        
        if self.act == 1:
            health_color = (255, 0, 0)
        else:
            health_color = (255, 100, 0)  
            
        pygame.draw.rect(surface, health_color, 
                        (bar_x, bar_y, health_width, bar_height))
        
        pygame.draw.rect(surface, (255, 255, 255), 
                        (bar_x, bar_y, bar_width, bar_height), 2)
        
        health_text = font_medium.render(f"БОС: {self.health}/{self.max_health} HP", 
                                       True, (255, 255, 255))
        surface.blit(health_text, (bar_x, bar_y - 25))
        
        act_text = font_medium.render(f"АКТ {self.act}", True, (255, 255, 0))
        surface.blit(act_text, (bar_x + bar_width - 80, bar_y - 25))

class BossBullet(GameSprite):
    def __init__(self, image_path, x, y, speed, width, height, angle=0):
        super().__init__(image_path, x, y, speed, width, height)
        self.image = Surface((width, height))
        self.image.fill((255, 100, 0))
        self.angle = angle
        
    def update(self):
        if self.angle == 0:

            self.rect.y += self.speed
        else:

            import math
            self.rect.x += self.speed * math.sin(math.radians(self.angle))
            self.rect.y += self.speed * math.cos(math.radians(self.angle))
        
        if self.rect.y > HEIGHT or self.rect.x < 0 or self.rect.x > WIDTH:
            self.kill()

class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()

player = Player("rocket.png", x=WIDTH//2, y=HEIGHT=100, speed=6, width=50, height=50)

asteroids = sprite.Group()
bullets = sprite.Group()
boss_bullets = sprite.Group()
boss_group = sprite.Group()

for _ in range(8):
    asteroid = Asteroid("asteroid.png", x=randint(50, WIDTH - 80), y=randint(-150, -50), 
                       speed=randint(2, 6), width=50, height=50)
    asteroids.add(asteroid)

game = True
boss_spawned = False
boss_defeated = False
lose_reason = ""

while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        elif e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                game = False
            elif e.key == K_r and (game_state == "game_over"):
                score = 0
                lives = 3
                game_state = "playing"
                asteroids.empty()
                bullets.empty()
                for _ in range(8):
                    asteroid = Asteroid("asteroid.png", randint(50, WIDTH - 80), 
                                       randint(-150, -50), randint(2, 6), 50, 50)
                    asteroids.add(asteroid)
                player.rect.x = WIDTH//2
                player.rect.y = HEIGHT-100
                player.last_shot = 0
                player.invulnerable_time = 0

    window.blit(background, (0, 0))

    if game_state == "playing":
        player.update()
        
        if player.invulnerable_time > 0 and player.invulnerable_time % 10 < 5:
            pass
        else:
            player.reset()

        asteroids.update()
        asteroids.draw(window)

        bullets.update()
        bullets.draw(window)

        collisions = sprite.groupcollide(asteroids, bullets, True, True)
        for _ in collisions:
            score += 10
            new_asteroid = Asteroid("asteroid.png", randint(50, WIDTH - 80), 
                                   randint(-150, -50), randint(2, 6), 50, 50)
            asteroids.add(new_asteroid)

        player_hit = sprite.spritecollide(player, asteroids, False)
        if player_hit:
            if player.take_damage():
                lives -= 1
                if lives <= 0:
                    game_state = "game_over"

        if score > 0 and score % 200 == 0:
            extra_asteroid = Asteroid("asteroid.png", randint(50, WIDTH - 80), 
                                     randint(-150, -50), randint(3, 7), 50, 50)
            asteroids.add(extra_asteroid)

        text_score = font1.render("Бали: " + str(score), True, (255, 255, 255))
        text_lives = font1.render("Життя: " + str(lives), True, (255, 255, 255))
        text_controls = font.SysFont("Arial", 20).render("WASD/Стрілки - рух, Пробіл - стрільба, ESC - вихід", True, (200, 200, 200))
        
        window.blit(text_score, (10, 20))
        window.blit(text_lives, (10, 60))
        window.blit(text_controls, (10, HEIGHT - 30))

    elif game_state == "game_over":
        game_over_text = font_large.render("ГРА ЗАКІНЧЕНА!", True, (255, 0, 0))
        final_score = font1.render("Фінальний рахунок: " + str(score), True, (255, 255, 255))
        restart_text = font1.render("Натисніть R для перезапуску", True, (255, 255, 255))
        
        game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 75))
        score_rect = final_score.get_rect(center=(WIDTH//2, HEIGHT//2 - 25))
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 75))
        
        window.blit(game_over_text, game_over_rect)
        window.blit(final_score, score_rect)
        window.blit(restart_text, restart_rect)

    display.update()
    clock.tick(FPS)

pygame.quit()

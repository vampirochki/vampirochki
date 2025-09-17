import pygame
from pygame import *
from random import randint

pygame.init()

WIDTH, HEIGHT = 700, 500
window = display.set_mode((WIDTH, HEIGHT))
display.set_caption("Космічний шутер")

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
lost = 0

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
            elif "ufo" in image_path:
                self.image.fill((255, 0, 0))
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
        self.shoot_delay = 200
    
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < WIDTH - self.rect.width - 5:
            self.rect.x += self.speed
        
        if keys[K_SPACE]:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot > self.shoot_delay:
                self.fire()
                self.last_shot = current_time

    def fire(self):
        bullet = Bullet("bullet.png", self.rect.centerx - 7, self.rect.top, -7, 15, 20)
        bullets.add(bullet)

class Enemy(GameSprite):
    def update(self):
        global lost
        self.rect.y += self.speed
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

player = Player("rocket.png", x=300, y=400, speed=5, width=65, height=65)

enemies = sprite.Group()
bullets = sprite.Group()
boss_bullets = sprite.Group()
boss_group = sprite.Group()

for _ in range(5):
    enemy = Enemy("ufo.png", x=randint(50, WIDTH - 80), y=randint(-150, -50), 
                 speed=randint(2, 5) * 0.7, width=65, height=65)
    enemies.add(enemy)

game = True
boss_spawned = False
boss_defeated = False
lose_reason = ""

while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        elif e.type == KEYDOWN:
            if e.key == K_r and (game_state == "win" or game_state == "lose"):
                score = 0
                lost = 0
                game_state = "playing"
                boss_spawned = False
                boss_defeated = False
                lose_reason = ""
                enemies.empty()
                bullets.empty()
                boss_bullets.empty()
                boss_group.empty()
                for _ in range(5):
                    enemy = Enemy("ufo.png", randint(50, WIDTH - 80), 
                                randint(-150, -50), randint(2, 5) * 0.7, 65, 65)
                    enemies.add(enemy)
                player.rect.x = 300
                player.rect.y = 400
                player.last_shot = 0

    window.blit(background, (0, 0))

    if game_state == "playing":
        player.update()
        player.reset()

        if score >= 40 and not boss_spawned and not boss_defeated:
            enemies.empty()
            boss = Boss("ufo.png", WIDTH // 2 - 75, 50, 3, 150, 100)
            boss_group.add(boss)
            boss_spawned = True

        if not boss_spawned:
            enemies.update()
            enemies.draw(window)

        bullets.update()
        bullets.draw(window)
        
        boss_bullets.update()
        boss_bullets.draw(window)
        
        boss_group.update()
        boss_group.draw(window)

        if not boss_spawned:
            collisions = sprite.groupcollide(enemies, bullets, True, True)
            for _ in collisions:
                score += 1

                if score < 40:
                    new_enemy = Enemy("ufo.png", randint(50, WIDTH - 80), 
                                    randint(-150, -50), randint(2, 5) * 0.7, 65, 65)
                    enemies.add(new_enemy)

        boss_collisions = sprite.groupcollide(boss_group, bullets, False, True)
        for boss, bullet_list in boss_collisions.items():
            for _ in bullet_list:
                if boss.take_damage():
                    score += 50
                    boss_defeated = True
                    boss_spawned = False

        if not boss_spawned:
            player_hit = sprite.spritecollide(player, enemies, False)
            if player_hit:
                lose_reason = "Зіткнення з ворогом"
                game_state = "lose"

        boss_player_hit = sprite.spritecollide(player, boss_group, False)
        if boss_player_hit:
            lose_reason = "Зіткнення з босом"
            game_state = "lose"

        boss_bullet_hit = sprite.spritecollide(player, boss_bullets, False)
        if boss_bullet_hit:
            lose_reason = "Влучання кулі боса"
            game_state = "lose"

        if boss_defeated:
            game_state = "win"

        elif lost >= 30:
            lose_reason = f"Пропущено {lost} ворогів (ліміт: 30)"
            game_state = "lose"

        for boss in boss_group:
            boss.draw_health_bar(window)

        text_score = font1.render("Збито: " + str(score), True, (255, 255, 255))
        text_lost = font1.render("Пропущено: " + str(lost), True, (255, 0, 0))
        text_controls = font.SysFont("Arial", 20).render("Керування: Стрілки - рух, Пробіл - стрільба", True, (200, 200, 200))
        window.blit(text_score, (10, 20))
        window.blit(text_lost, (10, 60))
        window.blit(text_controls, (10, HEIGHT - 30))
        
        if score < 40:
            progress_text = font_medium.render(f"До боса: {40 - score} ворогів", True, (255, 255, 0))
            window.blit(progress_text, (WIDTH // 2 - 80, HEIGHT - 60))
        elif boss_spawned and not boss_defeated:
            boss_warning = font_medium.render("УВАГА! З'ЯВИВСЯ БОС!", True, (255, 255, 0))
            window.blit(boss_warning, (WIDTH // 2 - 120, HEIGHT - 60))

    elif game_state == "win":
        win_text = font_large.render("ПЕРЕМОГА!", True, (0, 255, 0))
        final_score = font1.render("Фінальний рахунок: " + str(score), True, (255, 255, 255))
        boss_text = font1.render("Бос переможений!", True, (255, 255, 0))
        restart_text = font1.render("Натисніть R для перезапуску", True, (255, 255, 255))
        
        win_rect = win_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 75))
        score_rect = final_score.get_rect(center=(WIDTH//2, HEIGHT//2 - 25))
        boss_rect = boss_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 25))
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 75))
        
        window.blit(win_text, win_rect)
        window.blit(final_score, score_rect)
        window.blit(boss_text, boss_rect)
        window.blit(restart_text, restart_rect)

    elif game_state == "lose":
        lose_text = font_large.render("ПРОГРАШ!", True, (255, 0, 0))
        final_score = font1.render("Фінальний рахунок: " + str(score), True, (255, 255, 255))
        reason_text = font1.render("Причина: " + lose_reason, True, (255, 255, 0))
        restart_text = font1.render("Натисніть R для перезапуску", True, (255, 255, 255))
        
        lose_rect = lose_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 75))
        score_rect = final_score.get_rect(center=(WIDTH//2, HEIGHT//2 - 25))
        reason_rect = reason_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 25))
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 75))
        
        window.blit(lose_text, lose_rect)
        window.blit(final_score, score_rect)
        window.blit(reason_text, reason_rect)
        window.blit(restart_text, restart_rect)

    display.update()
    clock.tick(FPS)

pygame.quit()
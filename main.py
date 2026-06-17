import pygame
import random
import json
import os
from enum import Enum
from dataclasses import dataclass
from typing import List

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Game states
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    LEVEL_COMPLETE = 4
    PAUSED = 5

# Power-up types
class PowerUpType(Enum):
    SHIELD = 1
    RAPID_FIRE = 2
    TRIPLE_SHOT = 3
    HEALING = 4

@dataclass
class PowerUp:
    x: float
    y: float
    type: PowerUpType
    width: int = 20
    height: int = 20
    speed: float = 3
    
    def draw(self, screen):
        colors = {
            PowerUpType.SHIELD: CYAN,
            PowerUpType.RAPID_FIRE: YELLOW,
            PowerUpType.TRIPLE_SHOT: GREEN,
            PowerUpType.HEALING: RED
        }
        pygame.draw.rect(screen, colors[self.type], (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2)
    
    def update(self):
        self.y += self.speed
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

@dataclass
class Bullet:
    x: float
    y: float
    speed: float = 7
    width: int = 5
    height: int = 15
    
    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
    
    def update(self):
        self.y -= self.speed
    
    def is_off_screen(self):
        return self.y < 0

@dataclass
class Enemy:
    x: float
    y: float
    width: int = 40
    height: int = 40
    speed: float = 2
    health: int = 1
    shoot_timer: int = 0
    
    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        pygame.draw.polygon(screen, YELLOW, [
            (self.x + self.width/2, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x, self.y + self.height)
        ])
    
    def update(self):
        self.y += self.speed
        self.shoot_timer += 1
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

@dataclass
class EnemyBullet:
    x: float
    y: float
    speed: float = 4
    width: int = 4
    height: int = 12
    
    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
    
    def update(self):
        self.y += self.speed
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 50
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.shield = 0
        self.max_shield = 100
        self.rapid_fire = 0
        self.triple_shot = 0
        self.shoot_delay = 0
        
    def draw(self, screen):
        # Main body
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        # Cockpit
        pygame.draw.circle(screen, CYAN, (int(self.x + self.width/2), int(self.y + 10)), 5)
        # Shield
        if self.shield > 0:
            pygame.draw.circle(screen, CYAN, (int(self.x + self.width/2), int(self.y + self.height/2)), 
                             int(self.width), 2)
    
    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
        
        # Update power-ups
        if self.rapid_fire > 0:
            self.rapid_fire -= 1
        if self.triple_shot > 0:
            self.triple_shot -= 1
        if self.shoot_delay > 0:
            self.shoot_delay -= 1
    
    def shoot(self):
        bullets = []
        if self.shoot_delay <= 0:
            if self.triple_shot > 0:
                bullets.append(Bullet(self.x + self.width/2 - 10, self.y))
                bullets.append(Bullet(self.x + self.width/2, self.y))
                bullets.append(Bullet(self.x + self.width/2 + 10, self.y))
            else:
                bullets.append(Bullet(self.x + self.width/2 - 2.5, self.y))
            
            self.shoot_delay = 5 if self.rapid_fire > 0 else 15
        
        return bullets
    
    def take_damage(self, damage):
        if self.shield > 0:
            self.shield -= damage
        else:
            self.health -= damage
        self.health = max(0, self.health)
    
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
    
    def get_shield(self, amount):
        self.shield = min(self.max_shield, self.shield + amount)
    
    def is_alive(self):
        return self.health > 0

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Shooter - Advanced")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        self.state = GameState.MENU
        self.reset_game()
        self.load_high_score()
        
    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 80)
        self.bullets: List[Bullet] = []
        self.enemies: List[Enemy] = []
        self.enemy_bullets: List[EnemyBullet] = []
        self.power_ups: List[PowerUp] = []
        self.score = 0
        self.level = 1
        self.enemy_spawn_rate = max(30 - self.level * 5, 10)
        self.spawn_timer = 0
        self.enemy_speed = 1 + self.level * 0.5
        
    def load_high_score(self):
        if os.path.exists("highscore.json"):
            try:
                with open("highscore.json", "r") as f:
                    data = json.load(f)
                    self.high_score = data.get("high_score", 0)
            except:
                self.high_score = 0
        else:
            self.high_score = 0
    
    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            with open("highscore.json", "w") as f:
                json.dump({"high_score": self.high_score}, f)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.PLAYING
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                        self.state = GameState.MENU
                elif self.state == GameState.LEVEL_COMPLETE:
                    if event.key == pygame.K_SPACE:
                        self.level += 1
                        self.reset_game()
                        self.state = GameState.PLAYING
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
        return True
    
    def update(self):
        if self.state != GameState.PLAYING:
            return
        
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        
        # Shooting
        if keys[pygame.K_SPACE]:
            self.bullets.extend(self.player.shoot())
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
        
        # Spawn enemies
        self.spawn_timer += 1
        if self.spawn_timer > self.enemy_spawn_rate:
            enemy = Enemy(
                random.randint(0, SCREEN_WIDTH - 40),
                -50,
                speed=self.enemy_speed,
                health=1 + self.level // 2
            )
            self.enemies.append(enemy)
            self.spawn_timer = 0
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            
            # Enemy shooting
            if enemy.shoot_timer > 60:
                self.enemy_bullets.append(EnemyBullet(
                    enemy.x + enemy.width/2,
                    enemy.y + enemy.height
                ))
                enemy.shoot_timer = 0
            
            if enemy.is_off_screen():
                self.enemies.remove(enemy)
        
        # Update enemy bullets
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.enemy_bullets.remove(bullet)
        
        # Update power-ups
        for power_up in self.power_ups[:]:
            power_up.update()
            if power_up.is_off_screen():
                self.power_ups.remove(power_up)
        
        # Collision detection: bullets vs enemies
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if self.check_collision(bullet, enemy):
                    self.bullets.remove(bullet)
                    enemy.health -= 1
                    self.score += 10
                    
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += 90
                        # Drop power-ups
                        if random.random() < 0.3:
                            power_type = random.choice(list(PowerUpType))
                            self.power_ups.append(PowerUp(enemy.x, enemy.y, power_type))
                    break
        
        # Collision detection: player vs enemy bullets
        for bullet in self.enemy_bullets[:]:
            if self.check_collision(bullet, self.player):
                self.enemy_bullets.remove(bullet)
                self.player.take_damage(10)
                if not self.player.is_alive():
                    self.state = GameState.GAME_OVER
                    self.save_high_score()
        
        # Collision detection: player vs enemies
        for enemy in self.enemies[:]:
            if self.check_collision(self.player, enemy):
                self.player.take_damage(20)
                self.enemies.remove(enemy)
                if not self.player.is_alive():
                    self.state = GameState.GAME_OVER
                    self.save_high_score()
        
        # Collision detection: player vs power-ups
        for power_up in self.power_ups[:]:
            if self.check_collision(power_up, self.player):
                self.apply_power_up(power_up.type)
                self.power_ups.remove(power_up)
                self.score += 50
        
        # Level complete check
        if len(self.enemies) == 0 and self.spawn_timer > 120:
            self.state = GameState.LEVEL_COMPLETE
    
    def apply_power_up(self, power_type):
        if power_type == PowerUpType.SHIELD:
            self.player.get_shield(50)
        elif power_type == PowerUpType.RAPID_FIRE:
            self.player.rapid_fire = 300
        elif power_type == PowerUpType.TRIPLE_SHOT:
            self.player.triple_shot = 300
        elif power_type == PowerUpType.HEALING:
            self.player.heal(30)
    
    def check_collision(self, obj1, obj2):
        return (obj1.x < obj2.x + obj2.width and
                obj1.x + obj1.width > obj2.x and
                obj1.y < obj2.y + obj2.height and
                obj1.y + obj1.height > obj2.y)
    
    def draw(self):
        self.screen.fill(BLACK)
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.LEVEL_COMPLETE:
            self.draw_level_complete()
        elif self.state == GameState.PAUSED:
            self.draw_paused()
        
        pygame.display.flip()
    
    def draw_menu(self):
        title = self.font_large.render("SPACE SHOOTER", True, CYAN)
        start = self.font_medium.render("Press SPACE to Start", True, WHITE)
        high = self.font_small.render(f"High Score: {self.high_score}", True, YELLOW)
        
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        self.screen.blit(start, (SCREEN_WIDTH//2 - start.get_width()//2, 300))
        self.screen.blit(high, (SCREEN_WIDTH//2 - high.get_width()//2, 450))
    
    def draw_game(self):
        # Draw game objects
        self.player.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)
        for power_up in self.power_ups:
            power_up.draw(self.screen)
        
        # Draw HUD
        score_text = self.font_small.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font_small.render(f"Level: {self.level}", True, WHITE)
        health_text = self.font_small.render(f"Health: {self.player.health}/{self.player.max_health}", True, GREEN)
        shield_text = self.font_small.render(f"Shield: {self.player.shield}/{self.player.max_shield}", True, CYAN)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 40))
        self.screen.blit(health_text, (10, 70))
        self.screen.blit(shield_text, (10, 100))
        
        # Draw health bar
        pygame.draw.rect(self.screen, RED, (SCREEN_WIDTH - 210, 10, 200, 20))
        pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - 210, 10, 200 * self.player.health / self.player.max_health, 20))
    
    def draw_game_over(self):
        game_over = self.font_large.render("GAME OVER", True, RED)
        score = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        high = self.font_medium.render(f"High Score: {self.high_score}", True, YELLOW)
        restart = self.font_small.render("Press SPACE to return to menu", True, WHITE)
        
        self.screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, 100))
        self.screen.blit(score, (SCREEN_WIDTH//2 - score.get_width()//2, 250))
        self.screen.blit(high, (SCREEN_WIDTH//2 - high.get_width()//2, 320))
        self.screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 450))
    
    def draw_level_complete(self):
        complete = self.font_large.render("LEVEL COMPLETE!", True, GREEN)
        score = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        next_level = self.font_medium.render(f"Level {self.level + 1}", True, CYAN)
        cont = self.font_small.render("Press SPACE to continue", True, WHITE)
        
        self.screen.blit(complete, (SCREEN_WIDTH//2 - complete.get_width()//2, 100))
        self.screen.blit(score, (SCREEN_WIDTH//2 - score.get_width()//2, 200))
        self.screen.blit(next_level, (SCREEN_WIDTH//2 - next_level.get_width()//2, 280))
        self.screen.blit(cont, (SCREEN_WIDTH//2 - cont.get_width()//2, 450))
    
    def draw_paused(self):
        self.draw_game()
        paused = self.font_large.render("PAUSED", True, YELLOW)
        resume = self.font_small.render("Press ESC to resume", True, WHITE)
        self.screen.blit(paused, (SCREEN_WIDTH//2 - paused.get_width()//2, SCREEN_HEIGHT//2 - 100))
        self.screen.blit(resume, (SCREEN_WIDTH//2 - resume.get_width()//2, SCREEN_HEIGHT//2 + 100))
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
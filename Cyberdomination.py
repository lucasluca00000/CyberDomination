import pygame
import sys
import random
import math
from enum import Enum

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
PURPLE = (138, 43, 226)
RED = (255, 0, 0)
NEON_PINK = (255, 16, 240)
NEON_BLUE = (0, 242, 255)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cyber Domination")
clock = pygame.time.Clock()


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, speed=8):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (5, 5), 5)
        pygame.draw.circle(self.image, RED, (5, 5), 3)
        self.rect = self.image.get_rect(center=(x, y))

        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx ** 2 + dy ** 2)
        if dist > 0:
            self.vel_x = (dx / dist) * speed
            self.vel_y = (dy / dist) * speed
        else:
            self.vel_x = speed
            self.vel_y = 0

        self.damage = 10

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
                self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 40
        self.height = 60
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.run_speed = 8
        self.jump_power = -15
        self.gravity = 0.8
        self.on_ground = False

        self.is_running = False
        self.facing_right = True
        self.is_attacking = False
        self.is_hurt = False
        self.health = 100
        self.max_health = 100

        self.current_animation = "idle"
        self.animation_timer = 0
        self.animation_frame = 0
        self.hurt_timer = 0
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.attack_cooldown = 0
        self.attack_range = 60

        self.sprites = self.load_sprites()

    def load_sprites(self):
        sprites = {'idle': [], 'walk': [], 'run': [], 'attack': [], 'hurt': []}
        try:
            for i in range(1, 3):
                img = pygame.image.load(f'personnqges/idle_{i}.png.png').convert_alpha()
                sprites['idle'].append(pygame.transform.scale(img, (self.width, self.height)))
            for i in range(1, 5):
                img = pygame.image.load(f'personnqges/walk_{i}.png.png').convert_alpha()
                sprites['walk'].append(pygame.transform.scale(img, (self.width, self.height)))
            for i in range(1, 5):
                img = pygame.image.load(f'personnqges/run_{i}.png.png').convert_alpha()
                sprites['run'].append(pygame.transform.scale(img, (self.width, self.height)))
            for i in range(1, 5):
                img = pygame.image.load(f'personnqges/attack_{i}.png.png').convert_alpha()
                sprites['attack'].append(pygame.transform.scale(img, (self.width, self.height)))
            for i in range(1, 4):
                img = pygame.image.load(f'personnqges/hurt_{i}.png.png').convert_alpha()
                sprites['hurt'].append(pygame.transform.scale(img, (self.width, self.height)))
            print("Sprites du personnage chargés avec succès")
        except pygame.error as e:
            print(f"Erreur: {e} - Utilisation des sprites par défaut")
            return None
        return sprites

    def take_damage(self, damage):
        if not self.invulnerable:
            self.health -= damage
            self.is_hurt = True
            self.hurt_timer = 0
            self.animation_frame = 0
            self.invulnerable = True
            self.invulnerable_timer = 0
            if self.health <= 0:
                self.health = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if (keys[pygame.K_a] or keys[pygame.K_RCTRL]) and self.attack_cooldown <= 0:
            if not self.is_attacking and not self.is_hurt:
                self.is_attacking = True
                self.animation_frame = 0
                self.attack_cooldown = 30

        if not self.is_attacking and not self.is_hurt:
            self.vel_x = 0
            self.is_running = keys[pygame.K_LSHIFT]

            if keys[pygame.K_LEFT] or keys[pygame.K_q]:
                self.vel_x = -self.run_speed if self.is_running else -self.speed
                self.facing_right = False
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vel_x = self.run_speed if self.is_running else self.speed
                self.facing_right = True

            if (keys[pygame.K_SPACE] or keys[pygame.K_z] or keys[pygame.K_UP]) and self.on_ground:
                self.vel_y = self.jump_power
                self.on_ground = False

    def apply_gravity(self):
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

    def update_animation(self):
        self.animation_timer += 1

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.invulnerable:
            self.invulnerable_timer += 1
            if self.invulnerable_timer > 60:
                self.invulnerable = False
                self.invulnerable_timer = 0

        if self.is_hurt:
            self.hurt_timer += 1
            if self.animation_timer > 8:
                self.animation_frame += 1
                self.animation_timer = 0
                if self.animation_frame >= 3:
                    self.is_hurt = False
                    self.animation_frame = 0
                    self.hurt_timer = 0
            return

        if self.is_attacking:
            if self.animation_timer > 5:
                self.animation_frame += 1
                self.animation_timer = 0
                if self.animation_frame >= 4:
                    self.is_attacking = False
                    self.animation_frame = 0
            return

        if not self.on_ground:
            self.current_animation = "jump"
        elif self.vel_x != 0:
            if self.is_running:
                self.current_animation = "run"
                if self.animation_timer > 4:
                    self.animation_frame = (self.animation_frame + 1) % 4
                    self.animation_timer = 0
            else:
                self.current_animation = "walk"
                if self.animation_timer > 6:
                    self.animation_frame = (self.animation_frame + 1) % 4
                    self.animation_timer = 0
        else:
            self.current_animation = "idle"
            if self.animation_timer > 10:
                self.animation_frame = (self.animation_frame + 1) % 2
                self.animation_timer = 0

    def draw_sprite(self):
        self.image.fill((0, 0, 0, 0))

        if self.invulnerable and self.invulnerable_timer % 10 < 5:
            return

        if self.sprites:
            sprite_to_draw = None

            if self.is_hurt and self.sprites['hurt']:
                frame = min(self.animation_frame, len(self.sprites['hurt']) - 1)
                sprite_to_draw = self.sprites['hurt'][frame]
            elif self.is_attacking and self.sprites['attack']:
                frame = min(self.animation_frame, len(self.sprites['attack']) - 1)
                sprite_to_draw = self.sprites['attack'][frame]
            elif not self.on_ground:
                if self.sprites['idle']:
                    sprite_to_draw = self.sprites['idle'][0]
            elif self.vel_x != 0:
                if self.is_running and self.sprites['run']:
                    frame = self.animation_frame % len(self.sprites['run'])
                    sprite_to_draw = self.sprites['run'][frame]
                elif self.sprites['walk']:
                    frame = self.animation_frame % len(self.sprites['walk'])
                    sprite_to_draw = self.sprites['walk'][frame]
            else:
                if self.sprites['idle']:
                    frame = self.animation_frame % len(self.sprites['idle'])
                    sprite_to_draw = self.sprites['idle'][frame]

            if sprite_to_draw:
                if not self.facing_right:
                    sprite_to_draw = pygame.transform.flip(sprite_to_draw, True, False)
                self.image.blit(sprite_to_draw, (0, 0))
                return

        if self.is_hurt:
            color = RED
        elif self.is_attacking:
            color = NEON_PINK
        else:
            color = CYAN

        body_rect = pygame.Rect(10, 15, 20, 30)
        pygame.draw.rect(self.image, color, body_rect)
        pygame.draw.circle(self.image, color, (20, 10), 7)

        if self.is_attacking:
            arm_x = 35 if self.facing_right else 5
            pygame.draw.line(self.image, NEON_PINK, (20, 25), (arm_x, 25), 4)
            if self.facing_right:
                pygame.draw.circle(self.image, (255, 255, 0, 150), (arm_x + 5, 25), 8, 2)
            else:
                pygame.draw.circle(self.image, (255, 255, 0, 150), (arm_x - 5, 25), 8, 2)
        else:
            offset = int(math.sin(self.animation_frame) * 3)
            pygame.draw.line(self.image, color, (15, 25), (12, 35 + offset), 3)
            pygame.draw.line(self.image, color, (25, 25), (28, 35 - offset), 3)

        if self.current_animation in ["walk", "run"]:
            leg_offset = int(math.sin(self.animation_frame * 0.8) * 5)
            pygame.draw.line(self.image, color, (15, 45), (12, 58 + leg_offset), 4)
            pygame.draw.line(self.image, color, (25, 45), (28, 58 - leg_offset), 4)
        else:
            pygame.draw.line(self.image, color, (15, 45), (15, 58), 4)
            pygame.draw.line(self.image, color, (25, 45), (25, 58), 4)

        if self.is_running and self.vel_x != 0:
            for i in range(3):
                alpha = 80 - i * 25
                trail_x = -8 if self.facing_right else 8
                pygame.draw.circle(self.image, (*color[:3], alpha), (20 + trail_x * i, 30), 5)

    def check_attack_collision(self, enemies):
        if self.is_attacking and self.animation_frame == 2:
            attack_rect = pygame.Rect(
                self.rect.centerx + (self.attack_range if self.facing_right else -self.attack_range),
                self.rect.centery - 20, 20, 40
            )

            for enemy in enemies:
                if attack_rect.colliderect(enemy.rect):
                    enemy.take_damage(25)

    def update(self, platforms, enemies, projectiles):
        self.handle_input()
        self.apply_gravity()
        self.update_animation()
        self.check_attack_collision(enemies)

        if not self.is_attacking and not self.is_hurt:
            self.rect.x += self.vel_x
        elif self.is_hurt:
            knockback = -3 if self.facing_right else 3
            self.rect.x += knockback

        self.check_collision_x(platforms)

        self.rect.y += self.vel_y
        self.on_ground = False
        self.check_collision_y(platforms)

        for projectile in projectiles:
            if self.rect.colliderect(projectile.rect):
                self.take_damage(projectile.damage)
                projectile.kill()

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0

        if self.rect.top > SCREEN_HEIGHT:
            self.take_damage(20)
            self.rect.y = 100
            self.vel_y = 0

        self.draw_sprite()

    def check_collision_x(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_x > 0:
                    self.rect.right = p.rect.left
                elif self.vel_x < 0:
                    self.rect.left = p.rect.right

    def check_collision_y(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = p.rect.bottom
                    self.vel_y = 0


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, ptype="normal"):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.rect = self.image.get_rect(x=x, y=y)

        if ptype == "normal":
            self.image.fill((45, 30, 70))
            pygame.draw.rect(self.image, NEON_BLUE, (0, 0, w, h), 2)
            for i in range(0, w, 15):
                pygame.draw.line(self.image, (65, 45, 95), (i, 0), (i, h), 1)
        else:
            self.image.fill((35, 50, 80))
            pygame.draw.rect(self.image, CYAN, (0, 0, w, h), 2)
            for i in range(0, w, 20):
                if i % 40 == 0:
                    pygame.draw.rect(self.image, CYAN, (i + 2, 3, 16, h - 6))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 40
        self.height = 60
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(x=x, y=y)

        self.health = 50
        self.max_health = 50
        self.vel_x = 2
        self.direction = 1

        self.last_shot_time = 0
        self.shoot_delay = 10000  # 10 secondes
        self.detection_range = 400

        self.animation_frame = 0
        self.animation_timer = 0

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()

    def can_see_player(self, player):
        return abs(self.rect.centerx - player.rect.centerx) < self.detection_range

    def shoot(self, player, projectiles):
        current_time = pygame.time.get_ticks()
        if self.can_see_player(player):
            if current_time - self.last_shot_time >= self.shoot_delay:
                projectile = Projectile(
                    self.rect.centerx,
                    self.rect.centery,
                    player.rect.centerx,
                    player.rect.centery,
                    speed=6
                )
                projectiles.add(projectile)
                self.last_shot_time = current_time

    def update(self, platforms, player, projectiles):
            # Tir
            self.shoot(player, projectiles)

            # Animation
            self.animation_timer += 1
            if self.animation_timer > 10:
                self.animation_frame = (self.animation_frame + 1) % 4
                self.animation_timer = 0

            # Déplacement
            self.rect.x += self.vel_x * self.direction

            if self.rect.left < 50 or self.rect.right > SCREEN_WIDTH - 50:
                self.direction *= -1

            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.direction > 0:
                        self.rect.right = platform.rect.left
                        self.direction = -1
                    else:
                        self.rect.left = platform.rect.right
                        self.direction = 1

            self.draw_sprite()

    def draw_sprite(self):
        self.image.fill((0, 0, 0, 0))

        color = (200, 50, 50)
        pygame.draw.rect(self.image, color, (12, 20, 16, 25))
        pygame.draw.rect(self.image, (150, 30, 30), (14, 10, 12, 12))

        eye_y = 14 + int(math.sin(self.animation_frame) * 2)
        pygame.draw.circle(self.image, RED, (18, eye_y), 2)
        pygame.draw.circle(self.image, RED, (22, eye_y), 2)

        weapon_x = 30 if self.direction > 0 else 10
        pygame.draw.rect(self.image, (100, 100, 100), (weapon_x - 8, 28, 12, 4))

        leg_offset = int(math.sin(self.animation_frame * 0.5) * 3)
        pygame.draw.line(self.image, color, (17, 45), (15, 58 + leg_offset), 3)
        pygame.draw.line(self.image, color, (23, 45), (25, 58 - leg_offset), 3)

        if self.health < self.max_health:
            health_ratio = self.health / self.max_health
            pygame.draw.rect(self.image, RED, (5, 2, 30, 3))
            pygame.draw.rect(self.image, (0, 255, 0), (5, 2, int(30 * health_ratio), 3))


class Menu:
    def __init__(self):
        self.options = ["NOUVELLE PARTIE", "QUITTER"]
        self.selected = 0
        self.title_font = pygame.font.Font(None, 100)
        self.option_font = pygame.font.Font(None, 50)

    def draw(self, screen):
        for i in range(SCREEN_HEIGHT):
            c = int(30 + (i / SCREEN_HEIGHT) * 60)
            pygame.draw.line(screen, (c, c // 2, min(int(c * 1.8), 255)), (0, i), (SCREEN_WIDTH, i))

        offset = (pygame.time.get_ticks() // 20) % 50
        for x in range(-offset, SCREEN_WIDTH, 50):
            pygame.draw.line(screen, (60, 40, 100), (x, 0), (x, SCREEN_HEIGHT), 1)

        title = "CYBER DOMINATION"
        title_surf = self.title_font.render(title, True, NEON_BLUE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_surf, title_rect)

        subtitle = "[ HACK THE SYSTEM ]"
        sub_surf = pygame.font.Font(None, 30).render(subtitle, True, CYAN)
        screen.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 220)))

        y_start = 400
        for i, opt in enumerate(self.options):
            color = NEON_PINK if i == self.selected else WHITE
            opt_surf = self.option_font.render(opt, True, color)
            opt_rect = opt_surf.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 80))
            screen.blit(opt_surf, opt_rect)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_z]:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.selected
        return None


class Game:
    def __init__(self):
        self.state = GameState.MENU
        self.menu = Menu()
        self.player = None
        self.platforms = []
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.backgrounds = self.load_backgrounds()

    def load_backgrounds(self):
        try:
            bg = pygame.image.load("image (1).png").convert()
            bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            return bg
        except pygame.error as e:
            print(f"Erreur background : {e}")
            return None

    def init_game(self):
        self.player = Player(100, 400)
        self.platforms = self.create_level()
        self.enemies.empty()
        self.projectiles.empty()

        self.enemies.add(Enemy(400, 500))
        self.enemies.add(Enemy(700, 300))
        self.enemies.add(Enemy(1000, 450))

    def create_level(self):
        p = []
        p.append(Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
        p.append(Platform(200, 550, 200, 30, "tech"))
        p.append(Platform(500, 450, 200, 30))
        p.append(Platform(800, 350, 180, 30, "tech"))
        p.append(Platform(300, 300, 150, 30))
        p.append(Platform(600, 200, 180, 30, "tech"))
        p.append(Platform(1000, 500, 200, 30))
        p.append(Platform(100, 400, 150, 30, "tech"))
        return p

    def draw_background(self):
        if self.backgrounds:
            screen.blit(self.backgrounds, (0, 0))
        else:
            screen.fill((20, 20, 40))

    def draw_hud(self):
        pygame.draw.rect(screen, (20, 10, 40), (0, 0, SCREEN_WIDTH, 50))
        pygame.draw.line(screen, NEON_BLUE, (0, 50), (SCREEN_WIDTH, 50), 2)

        font = pygame.font.Font(None, 30)
        hp_text = font.render(f"HP: {self.player.health}/{self.player.max_health}", True, CYAN)
        screen.blit(hp_text, (20, 15))

        pygame.draw.rect(screen, (30, 20, 50), (150, 15, 250, 20))
        hp_w = int((self.player.health / self.player.max_health) * 250)
        pygame.draw.rect(screen, CYAN, (150, 15, hp_w, 20))
        pygame.draw.rect(screen, NEON_BLUE, (150, 15, 250, 20), 2)

        state = self.player.current_animation.upper()
        state_surf = font.render(state, True, NEON_PINK)
        screen.blit(state_surf, (SCREEN_WIDTH - 200, 15))

        enemies_text = font.render(f"ENNEMIS: {len(self.enemies)}", True, YELLOW)
        screen.blit(enemies_text, (SCREEN_WIDTH // 2 - 70, 15))

    def draw_instructions(self):
        font = pygame.font.Font(None, 22)
        instructions = ["Q/D : Déplacer | SHIFT : Courir", "ESPACE : Sauter | A : Attaquer", "ESC : Menu"]

        y = SCREEN_HEIGHT - 85
        for inst in instructions:
            surf = font.render(inst, True, WHITE)
            bg = pygame.Surface((surf.get_width() + 10, surf.get_height() + 5), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 150))
            screen.blit(bg, (5, y - 2))
            screen.blit(surf, (10, y))
            y += 25

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.state == GameState.MENU:
                    choice = self.menu.handle_input(event)
                    if choice == 0:
                        self.init_game()
                        self.state = GameState.PLAYING
                    elif choice == 1:
                        running = False

                elif self.state == GameState.PLAYING:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.state = GameState.MENU

            if self.state == GameState.MENU:
                self.menu.draw(screen)

            elif self.state == GameState.PLAYING:
                if self.player.health <= 0:
                    self.state = GameState.GAME_OVER

                self.player.update(self.platforms, self.enemies, self.projectiles)

                for enemy in self.enemies:
                    enemy.update(self.platforms, self.player, self.projectiles)

                self.projectiles.update()

                self.draw_background()

                for platform in self.platforms:
                    screen.blit(platform.image, platform.rect)

                for projectile in self.projectiles:
                    screen.blit(projectile.image, projectile.rect)

                for enemy in self.enemies:
                    screen.blit(enemy.image, enemy.rect)

                screen.blit(self.player.image, self.player.rect)

                self.draw_hud()
                self.draw_instructions()

            elif self.state == GameState.GAME_OVER:
                screen.fill(BLACK)

                font = pygame.font.Font(None, 100)
                text = font.render("GAME OVER", True, RED)
                screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))

                restart_font = pygame.font.Font(None, 40)
                restart_text = restart_font.render(
                    "Appuyez sur ENTREE pour recommencer",
                    True,
                    WHITE
                )
                screen.blit(
                    restart_text,
                    restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
                )

                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    self.init_game()
                    self.state = GameState.PLAYING

            pygame.display.update()
            clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()

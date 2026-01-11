<<<<<<< HEAD
import pygame
import sys
import os
from enum import Enum

# Initialisation de Pygame
pygame.init()

# Constantes
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
PURPLE = (138, 43, 226)
RED = (255, 0, 0)
DARK_PURPLE = (50, 20, 80)
NEON_PINK = (255, 16, 240)
NEON_BLUE = (0, 242, 255)

# Configuration de la fenêtre
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cyber Domination")
clock = pygame.time.Clock()


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4


class Animation:
    def __init__(self, frames, frame_duration=100):
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = now

    def get_current_frame(self):
        return self.frames[self.current_frame]

    def reset(self):
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Pour l'instant, on utilise des rectangles colorés
        # Quand tu auras les sprites IDLE et HURT, on les ajoutera
        self.width = 40
        self.height = 60
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Physique
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.run_speed = 8
        self.jump_power = -15
        self.gravity = 0.8
        self.on_ground = False

        # États
        self.is_running = False
        self.facing_right = True
        self.is_attacking = False
        self.health = 100
        self.max_health = 100

        # Animations (temporaires avec rectangles colorés)
        self.current_animation = "idle"
        self.animation_timer = 0
        self.animation_frame = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Attaque
        if keys[pygame.K_a] or keys[pygame.K_RCTRL]:
            if not self.is_attacking:
                self.is_attacking = True
                self.animation_frame = 0

        if not self.is_attacking:
            # Déplacement horizontal
            self.vel_x = 0
            self.is_running = keys[pygame.K_LSHIFT]

            if keys[pygame.K_LEFT] or keys[pygame.K_q]:
                self.vel_x = -self.run_speed if self.is_running else -self.speed
                self.facing_right = False
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vel_x = self.run_speed if self.is_running else self.speed
                self.facing_right = True

            # Saut
            if (keys[pygame.K_SPACE] or keys[pygame.K_z] or keys[pygame.K_UP]) and self.on_ground:
                self.vel_y = self.jump_power
                self.on_ground = False

    def apply_gravity(self):
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

    def update_animation(self):
        self.animation_timer += 1

        if self.is_attacking:
            if self.animation_timer > 5:
                self.animation_frame += 1
                self.animation_timer = 0
                if self.animation_frame >= 4:  # 4 frames d'attaque
                    self.is_attacking = False
                    self.animation_frame = 0

        # Déterminer l'animation actuelle
        if self.is_attacking:
            self.current_animation = "attack"
        elif not self.on_ground:
            self.current_animation = "jump"
        elif self.vel_x != 0:
            if self.is_running:
                self.current_animation = "run"
            else:
                self.current_animation = "walk"
        else:
            self.current_animation = "idle"

    def draw_placeholder(self):
        # Dessiner un personnage temporaire stylisé
        self.image.fill((0, 0, 0, 0))

        # Corps
        color = CYAN if not self.is_attacking else NEON_PINK
        pygame.draw.rect(self.image, color, (10, 10, 20, 35))

        # Tête
        pygame.draw.circle(self.image, color, (20, 8), 8)

        # Bras (change selon l'animation)
        if self.is_attacking:
            arm_x = 30 if self.facing_right else 10
            pygame.draw.line(self.image, NEON_PINK, (20, 20), (arm_x, 25), 3)
        else:
            pygame.draw.line(self.image, color, (15, 20), (10, 30), 3)
            pygame.draw.line(self.image, color, (25, 20), (30, 30), 3)

        # Jambes
        pygame.draw.line(self.image, color, (15, 45), (12, 58), 3)
        pygame.draw.line(self.image, color, (25, 45), (28, 58), 3)

        # Effet de mouvement
        if self.is_running:
            for i in range(3):
                alpha = 100 - i * 30
                trail_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                trail_surf.fill((0, 255, 255, alpha))
                offset = -10 if self.facing_right else 10
                self.image.blit(trail_surf, (i * offset, 0))

    def update(self, platforms):
        self.handle_input()
        self.apply_gravity()
        self.update_animation()

        # Déplacement horizontal
        if not self.is_attacking:
            self.rect.x += self.vel_x
        self.check_collision_x(platforms)

        # Déplacement vertical
        self.rect.y += self.vel_y
        self.on_ground = False
        self.check_collision_y(platforms)

        # Limites de l'écran
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0

        # Dessiner le personnage
        self.draw_placeholder()

    def check_collision_x(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right

    def check_collision_y(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type="normal"):
        super().__init__()
        self.width = width
        self.height = height
        self.platform_type = platform_type
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Style cyberpunk
        if platform_type == "normal":
            self.image.fill((60, 40, 90))
            pygame.draw.rect(self.image, NEON_BLUE, (0, 0, width, height), 2)
            # Lignes décoratives
            for i in range(0, width, 20):
                pygame.draw.line(self.image, (80, 60, 120), (i, 0), (i, height), 1)
        elif platform_type == "tech":
            self.image.fill((40, 60, 90))
            pygame.draw.rect(self.image, CYAN, (0, 0, width, height), 2)
            # Motif tech
            for i in range(0, width, 10):
                if i % 20 == 0:
                    pygame.draw.rect(self.image, CYAN, (i, 2, 8, height - 4))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.health = 50
        self.vel_x = 2
        self.direction = 1

        # Effet neon
        pygame.draw.rect(self.image, NEON_PINK, self.rect, 2)

    def update(self, platforms):
        self.rect.x += self.vel_x * self.direction

        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1


class Menu:
    def __init__(self):
        self.options = ["NOUVELLE PARTIE", "OPTIONS", "QUITTER"]
        self.selected = 0
        self.title_font = pygame.font.Font(None, 100)
        self.option_font = pygame.font.Font(None, 50)
        self.glitch_offset = 0
        self.glitch_timer = 0

    def draw(self, screen):
        # Fond dégradé cyberpunk animé
        for i in range(SCREEN_HEIGHT):
            color_value = int(30 + (i / SCREEN_HEIGHT) * 60)
            r = color_value
            g = color_value // 2
            b = color_value * 1.8
            if b > 255:
                b = 255
            pygame.draw.line(screen, (r, g, int(b)), (0, i), (SCREEN_WIDTH, i))

        # Grille animée
        offset = (pygame.time.get_ticks() // 20) % 50
        for x in range(-offset, SCREEN_WIDTH, 50):
            pygame.draw.line(screen, (60, 40, 100), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(-offset, SCREEN_HEIGHT, 50):
            pygame.draw.line(screen, (60, 40, 100), (0, y), (SCREEN_WIDTH, y), 1)

        # Titre avec effet glitch
        self.glitch_timer += 1
        if self.glitch_timer > 10:
            self.glitch_offset = pygame.time.get_ticks() % 3 - 1
            self.glitch_timer = 0

        title = "CYBER DOMINATION"
        title_surface = self.title_font.render(title, True, NEON_BLUE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))

        # Effet glitch
        glitch_surface = self.title_font.render(title, True, NEON_PINK)
        screen.blit(glitch_surface, (title_rect.x + self.glitch_offset * 3, title_rect.y))
        screen.blit(title_surface, title_rect)

        # Sous-titre
        subtitle_font = pygame.font.Font(None, 30)
        subtitle = "[ HACK THE SYSTEM ]"
        subtitle_surface = subtitle_font.render(subtitle, True, CYAN)
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 220))
        screen.blit(subtitle_surface, subtitle_rect)

        # Options du menu
        y_start = 350
        for i, option in enumerate(self.options):
            color = NEON_PINK if i == self.selected else WHITE

            # Indicateur de sélection
            if i == self.selected:
                indicator = ">>>"
                indicator_surface = self.option_font.render(indicator, True, NEON_PINK)
                screen.blit(indicator_surface, (SCREEN_WIDTH // 2 - 200, y_start + i * 80))

            option_surface = self.option_font.render(option, True, color)
            option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 80))
            screen.blit(option_surface, option_rect)

            # Effet de scan pour l'option sélectionnée
            if i == self.selected:
                scan_y = (pygame.time.get_ticks() // 10) % 60
                pygame.draw.line(screen, (NEON_PINK[0], NEON_PINK[1], NEON_PINK[2], 100),
                                 (option_rect.left, option_rect.top + scan_y),
                                 (option_rect.right, option_rect.top + scan_y), 2)

        # Instructions
        instruction_font = pygame.font.Font(None, 25)
        instructions = "Utilisez les FLECHES ou Z/Q/S/D pour naviguer | ENTREE pour sélectionner"
        instruction_surface = instruction_font.render(instructions, True, CYAN)
        instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(instruction_surface, instruction_rect)

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
        self.background_offset = 0

    def init_game(self):
        self.player = Player(100, 500)
        self.platforms = self.create_level()
        self.enemies.empty()

        # Ajouter des ennemis
        enemy1 = Enemy(400, 300)
        enemy2 = Enemy(800, 500)
        self.enemies.add(enemy1, enemy2)

    def create_level(self):
        platforms = []

        # Sol principal
        platforms.append(Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50, "normal"))

        # Plateformes - style cyberpunk
        platforms.append(Platform(200, 550, 200, 30, "tech"))
        platforms.append(Platform(500, 450, 200, 30, "normal"))
        platforms.append(Platform(800, 350, 200, 30, "tech"))
        platforms.append(Platform(300, 300, 150, 30, "normal"))
        platforms.append(Platform(600, 200, 180, 30, "tech"))
        platforms.append(Platform(1000, 500, 200, 30, "normal"))
        platforms.append(Platform(100, 400, 150, 30, "tech"))

        # Murs
        platforms.append(Platform(450, 350, 30, 100, "normal"))
        platforms.append(Platform(950, 250, 30, 100, "tech"))

        return platforms

    def draw_game_background(self):
        # Fond dégradé cyberpunk animé avec parallax
        self.background_offset = (self.background_offset + 0.5) % SCREEN_WIDTH

        for i in range(SCREEN_HEIGHT):
            ratio = i / SCREEN_HEIGHT
            r = int(30 + ratio * 40)
            g = int(20 + ratio * 30)
            b = int(60 + ratio * 80)
            pygame.draw.line(screen, (r, g, b), (0, i), (SCREEN_WIDTH, i))

        # Grille cyber animée
        grid_offset = int(self.background_offset) % 100
        for x in range(-grid_offset, SCREEN_WIDTH + 100, 100):
            pygame.draw.line(screen, (50, 40, 80), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 100):
            pygame.draw.line(screen, (50, 40, 80), (0, y), (SCREEN_WIDTH, y), 1)

        # Éléments de décor cyberpunk (lignes néon)
        neon_y = (pygame.time.get_ticks() // 50) % SCREEN_HEIGHT
        pygame.draw.line(screen, (NEON_BLUE[0], NEON_BLUE[1], NEON_BLUE[2], 50),
                         (0, neon_y), (SCREEN_WIDTH, neon_y), 3)

    def draw_hud(self):
        # Barre HUD
        hud_height = 50
        hud_surface = pygame.Surface((SCREEN_WIDTH, hud_height), pygame.SRCALPHA)
        hud_surface.fill((20, 10, 40, 200))
        screen.blit(hud_surface, (0, 0))

        # Bordure néon
        pygame.draw.line(screen, NEON_BLUE, (0, hud_height), (SCREEN_WIDTH, hud_height), 2)

        # Texte vie
        font = pygame.font.Font(None, 30)
        health_text = font.render(f"HP: {self.player.health}/{self.player.max_health}", True, CYAN)
        screen.blit(health_text, (20, 15))

        # Barre de vie graphique avec effet néon
        bar_width = 250
        bar_height = 20
        bar_x = 150
        bar_y = 15

        pygame.draw.rect(screen, (30, 20, 50), (bar_x, bar_y, bar_width, bar_height))
        health_width = int((self.player.health / self.player.max_health) * bar_width)

        # Gradient de vie
        for i in range(health_width):
            ratio = i / bar_width
            r = int(0 + ratio * 255)
            g = int(255 - ratio * 255)
            b = 255
            pygame.draw.line(screen, (r, g, b), (bar_x + i, bar_y), (bar_x + i, bar_y + bar_height))

        pygame.draw.rect(screen, NEON_BLUE, (bar_x, bar_y, bar_width, bar_height), 2)

        # État du joueur
        state_text = self.player.current_animation.upper()
        state_render = font.render(state_text, True, NEON_PINK)
        screen.blit(state_render, (SCREEN_WIDTH - 200, 15))

        # FPS counter
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, CYAN)
        screen.blit(fps_text, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 40))

    def draw_instructions(self):
        font_small = pygame.font.Font(None, 22)
        instructions = [
            "Q/D ou FLECHES : Déplacer",
            "SHIFT : Courir",
            "ESPACE : Sauter",
            "A : Attaquer",
            "ESC : Menu",
        ]

        y_offset = SCREEN_HEIGHT - 140
        for instruction in instructions:
            # Fond semi-transparent
            text_surface = font_small.render(instruction, True, WHITE)
            bg_surface = pygame.Surface((text_surface.get_width() + 10, text_surface.get_height() + 5), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 150))
            screen.blit(bg_surface, (5, y_offset - 2))
            screen.blit(text_surface, (10, y_offset))
            y_offset += 25

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.state == GameState.MENU:
                    choice = self.menu.handle_input(event)
                    if choice == 0:  # Nouvelle partie
                        self.init_game()
                        self.state = GameState.PLAYING
                    elif choice == 1:  # Options
                        pass  # À implémenter
                    elif choice == 2:  # Quitter
                        running = False

                elif self.state == GameState.PLAYING:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.state = GameState.MENU

            # Mise à jour et dessin selon l'état
            if self.state == GameState.MENU:
                self.menu.draw(screen)

            elif self.state == GameState.PLAYING:
                # Mise à jour
                self.player.update(self.platforms)
                self.enemies.update(self.platforms)

                # Dessin
                self.draw_game_background()

                # Dessiner les plateformes
                for platform in self.platforms:
                    screen.blit(platform.image, platform.rect)

                # Dessiner les ennemis
                for enemy in self.enemies:
                    screen.blit(enemy.image, enemy.rect)

                # Dessiner le joueur
                screen.blit(self.player.image, self.player.rect)

                # HUD
                self.draw_hud()
                self.draw_instructions()

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()


# Lancer le jeu
if __name__ == "__main__":
    game = Game()
=======
import pygame
import sys
import os
from enum import Enum

# Initialisation de Pygame
pygame.init()

# Constantes
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
PURPLE = (138, 43, 226)
RED = (255, 0, 0)
DARK_PURPLE = (50, 20, 80)
NEON_PINK = (255, 16, 240)
NEON_BLUE = (0, 242, 255)

# Configuration de la fenêtre
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cyber Domination")
clock = pygame.time.Clock()


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4


class Animation:
    def __init__(self, frames, frame_duration=100):
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = now

    def get_current_frame(self):
        return self.frames[self.current_frame]

    def reset(self):
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Pour l'instant, on utilise des rectangles colorés
        # Quand tu auras les sprites IDLE et HURT, on les ajoutera
        self.width = 40
        self.height = 60
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Physique
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.run_speed = 8
        self.jump_power = -15
        self.gravity = 0.8
        self.on_ground = False

        # États
        self.is_running = False
        self.facing_right = True
        self.is_attacking = False
        self.health = 100
        self.max_health = 100

        # Animations (temporaires avec rectangles colorés)
        self.current_animation = "idle"
        self.animation_timer = 0
        self.animation_frame = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Attaque
        if keys[pygame.K_a] or keys[pygame.K_RCTRL]:
            if not self.is_attacking:
                self.is_attacking = True
                self.animation_frame = 0

        if not self.is_attacking:
            # Déplacement horizontal
            self.vel_x = 0
            self.is_running = keys[pygame.K_LSHIFT]

            if keys[pygame.K_LEFT] or keys[pygame.K_q]:
                self.vel_x = -self.run_speed if self.is_running else -self.speed
                self.facing_right = False
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vel_x = self.run_speed if self.is_running else self.speed
                self.facing_right = True

            # Saut
            if (keys[pygame.K_SPACE] or keys[pygame.K_z] or keys[pygame.K_UP]) and self.on_ground:
                self.vel_y = self.jump_power
                self.on_ground = False

    def apply_gravity(self):
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

    def update_animation(self):
        self.animation_timer += 1

        if self.is_attacking:
            if self.animation_timer > 5:
                self.animation_frame += 1
                self.animation_timer = 0
                if self.animation_frame >= 4:  # 4 frames d'attaque
                    self.is_attacking = False
                    self.animation_frame = 0

        # Déterminer l'animation actuelle
        if self.is_attacking:
            self.current_animation = "attack"
        elif not self.on_ground:
            self.current_animation = "jump"
        elif self.vel_x != 0:
            if self.is_running:
                self.current_animation = "run"
            else:
                self.current_animation = "walk"
        else:
            self.current_animation = "idle"

    def draw_placeholder(self):
        # Dessiner un personnage temporaire stylisé
        self.image.fill((0, 0, 0, 0))

        # Corps
        color = CYAN if not self.is_attacking else NEON_PINK
        pygame.draw.rect(self.image, color, (10, 10, 20, 35))

        # Tête
        pygame.draw.circle(self.image, color, (20, 8), 8)

        # Bras (change selon l'animation)
        if self.is_attacking:
            arm_x = 30 if self.facing_right else 10
            pygame.draw.line(self.image, NEON_PINK, (20, 20), (arm_x, 25), 3)
        else:
            pygame.draw.line(self.image, color, (15, 20), (10, 30), 3)
            pygame.draw.line(self.image, color, (25, 20), (30, 30), 3)

        # Jambes
        pygame.draw.line(self.image, color, (15, 45), (12, 58), 3)
        pygame.draw.line(self.image, color, (25, 45), (28, 58), 3)

        # Effet de mouvement
        if self.is_running:
            for i in range(3):
                alpha = 100 - i * 30
                trail_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                trail_surf.fill((0, 255, 255, alpha))
                offset = -10 if self.facing_right else 10
                self.image.blit(trail_surf, (i * offset, 0))

    def update(self, platforms):
        self.handle_input()
        self.apply_gravity()
        self.update_animation()

        # Déplacement horizontal
        if not self.is_attacking:
            self.rect.x += self.vel_x
        self.check_collision_x(platforms)

        # Déplacement vertical
        self.rect.y += self.vel_y
        self.on_ground = False
        self.check_collision_y(platforms)

        # Limites de l'écran
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0

        # Dessiner le personnage
        self.draw_placeholder()

    def check_collision_x(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right

    def check_collision_y(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type="normal"):
        super().__init__()
        self.width = width
        self.height = height
        self.platform_type = platform_type
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Style cyberpunk
        if platform_type == "normal":
            self.image.fill((60, 40, 90))
            pygame.draw.rect(self.image, NEON_BLUE, (0, 0, width, height), 2)
            # Lignes décoratives
            for i in range(0, width, 20):
                pygame.draw.line(self.image, (80, 60, 120), (i, 0), (i, height), 1)
        elif platform_type == "tech":
            self.image.fill((40, 60, 90))
            pygame.draw.rect(self.image, CYAN, (0, 0, width, height), 2)
            # Motif tech
            for i in range(0, width, 10):
                if i % 20 == 0:
                    pygame.draw.rect(self.image, CYAN, (i, 2, 8, height - 4))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.health = 50
        self.vel_x = 2
        self.direction = 1

        # Effet neon
        pygame.draw.rect(self.image, NEON_PINK, self.rect, 2)

    def update(self, platforms):
        self.rect.x += self.vel_x * self.direction

        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1


class Menu:
    def __init__(self):
        self.options = ["NOUVELLE PARTIE", "OPTIONS", "QUITTER"]
        self.selected = 0
        self.title_font = pygame.font.Font(None, 100)
        self.option_font = pygame.font.Font(None, 50)
        self.glitch_offset = 0
        self.glitch_timer = 0

    def draw(self, screen):
        # Fond dégradé cyberpunk animé
        for i in range(SCREEN_HEIGHT):
            color_value = int(30 + (i / SCREEN_HEIGHT) * 60)
            r = color_value
            g = color_value // 2
            b = color_value * 1.8
            if b > 255:
                b = 255
            pygame.draw.line(screen, (r, g, int(b)), (0, i), (SCREEN_WIDTH, i))

        # Grille animée
        offset = (pygame.time.get_ticks() // 20) % 50
        for x in range(-offset, SCREEN_WIDTH, 50):
            pygame.draw.line(screen, (60, 40, 100), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(-offset, SCREEN_HEIGHT, 50):
            pygame.draw.line(screen, (60, 40, 100), (0, y), (SCREEN_WIDTH, y), 1)

        # Titre avec effet glitch
        self.glitch_timer += 1
        if self.glitch_timer > 10:
            self.glitch_offset = pygame.time.get_ticks() % 3 - 1
            self.glitch_timer = 0

        title = "CYBER DOMINATION"
        title_surface = self.title_font.render(title, True, NEON_BLUE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))

        # Effet glitch
        glitch_surface = self.title_font.render(title, True, NEON_PINK)
        screen.blit(glitch_surface, (title_rect.x + self.glitch_offset * 3, title_rect.y))
        screen.blit(title_surface, title_rect)

        # Sous-titre
        subtitle_font = pygame.font.Font(None, 30)
        subtitle = "[ HACK THE SYSTEM ]"
        subtitle_surface = subtitle_font.render(subtitle, True, CYAN)
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 220))
        screen.blit(subtitle_surface, subtitle_rect)

        # Options du menu
        y_start = 350
        for i, option in enumerate(self.options):
            color = NEON_PINK if i == self.selected else WHITE

            # Indicateur de sélection
            if i == self.selected:
                indicator = ">>>"
                indicator_surface = self.option_font.render(indicator, True, NEON_PINK)
                screen.blit(indicator_surface, (SCREEN_WIDTH // 2 - 200, y_start + i * 80))

            option_surface = self.option_font.render(option, True, color)
            option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 80))
            screen.blit(option_surface, option_rect)

            # Effet de scan pour l'option sélectionnée
            if i == self.selected:
                scan_y = (pygame.time.get_ticks() // 10) % 60
                pygame.draw.line(screen, (NEON_PINK[0], NEON_PINK[1], NEON_PINK[2], 100),
                                 (option_rect.left, option_rect.top + scan_y),
                                 (option_rect.right, option_rect.top + scan_y), 2)

        # Instructions
        instruction_font = pygame.font.Font(None, 25)
        instructions = "Utilisez les FLECHES ou Z/Q/S/D pour naviguer | ENTREE pour sélectionner"
        instruction_surface = instruction_font.render(instructions, True, CYAN)
        instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(instruction_surface, instruction_rect)

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
        self.background_offset = 0

    def init_game(self):
        self.player = Player(100, 500)
        self.platforms = self.create_level()
        self.enemies.empty()

        # Ajouter des ennemis
        enemy1 = Enemy(400, 300)
        enemy2 = Enemy(800, 500)
        self.enemies.add(enemy1, enemy2)

    def create_level(self):
        platforms = []

        # Sol principal
        platforms.append(Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50, "normal"))

        # Plateformes - style cyberpunk
        platforms.append(Platform(200, 550, 200, 30, "tech"))
        platforms.append(Platform(500, 450, 200, 30, "normal"))
        platforms.append(Platform(800, 350, 200, 30, "tech"))
        platforms.append(Platform(300, 300, 150, 30, "normal"))
        platforms.append(Platform(600, 200, 180, 30, "tech"))
        platforms.append(Platform(1000, 500, 200, 30, "normal"))
        platforms.append(Platform(100, 400, 150, 30, "tech"))

        # Murs
        platforms.append(Platform(450, 350, 30, 100, "normal"))
        platforms.append(Platform(950, 250, 30, 100, "tech"))

        return platforms

    def draw_game_background(self):
        # Fond dégradé cyberpunk animé avec parallax
        self.background_offset = (self.background_offset + 0.5) % SCREEN_WIDTH

        for i in range(SCREEN_HEIGHT):
            ratio = i / SCREEN_HEIGHT
            r = int(30 + ratio * 40)
            g = int(20 + ratio * 30)
            b = int(60 + ratio * 80)
            pygame.draw.line(screen, (r, g, b), (0, i), (SCREEN_WIDTH, i))

        # Grille cyber animée
        grid_offset = int(self.background_offset) % 100
        for x in range(-grid_offset, SCREEN_WIDTH + 100, 100):
            pygame.draw.line(screen, (50, 40, 80), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 100):
            pygame.draw.line(screen, (50, 40, 80), (0, y), (SCREEN_WIDTH, y), 1)

        # Éléments de décor cyberpunk (lignes néon)
        neon_y = (pygame.time.get_ticks() // 50) % SCREEN_HEIGHT
        pygame.draw.line(screen, (NEON_BLUE[0], NEON_BLUE[1], NEON_BLUE[2], 50),
                         (0, neon_y), (SCREEN_WIDTH, neon_y), 3)

    def draw_hud(self):
        # Barre HUD
        hud_height = 50
        hud_surface = pygame.Surface((SCREEN_WIDTH, hud_height), pygame.SRCALPHA)
        hud_surface.fill((20, 10, 40, 200))
        screen.blit(hud_surface, (0, 0))

        # Bordure néon
        pygame.draw.line(screen, NEON_BLUE, (0, hud_height), (SCREEN_WIDTH, hud_height), 2)

        # Texte vie
        font = pygame.font.Font(None, 30)
        health_text = font.render(f"HP: {self.player.health}/{self.player.max_health}", True, CYAN)
        screen.blit(health_text, (20, 15))

        # Barre de vie graphique avec effet néon
        bar_width = 250
        bar_height = 20
        bar_x = 150
        bar_y = 15

        pygame.draw.rect(screen, (30, 20, 50), (bar_x, bar_y, bar_width, bar_height))
        health_width = int((self.player.health / self.player.max_health) * bar_width)

        # Gradient de vie
        for i in range(health_width):
            ratio = i / bar_width
            r = int(0 + ratio * 255)
            g = int(255 - ratio * 255)
            b = 255
            pygame.draw.line(screen, (r, g, b), (bar_x + i, bar_y), (bar_x + i, bar_y + bar_height))

        pygame.draw.rect(screen, NEON_BLUE, (bar_x, bar_y, bar_width, bar_height), 2)

        # État du joueur
        state_text = self.player.current_animation.upper()
        state_render = font.render(state_text, True, NEON_PINK)
        screen.blit(state_render, (SCREEN_WIDTH - 200, 15))

        # FPS counter
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, CYAN)
        screen.blit(fps_text, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 40))

    def draw_instructions(self):
        font_small = pygame.font.Font(None, 22)
        instructions = [
            "Q/D ou FLECHES : Déplacer",
            "SHIFT : Courir",
            "ESPACE : Sauter",
            "A : Attaquer",
            "ESC : Menu",
        ]

        y_offset = SCREEN_HEIGHT - 140
        for instruction in instructions:
            # Fond semi-transparent
            text_surface = font_small.render(instruction, True, WHITE)
            bg_surface = pygame.Surface((text_surface.get_width() + 10, text_surface.get_height() + 5), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 150))
            screen.blit(bg_surface, (5, y_offset - 2))
            screen.blit(text_surface, (10, y_offset))
            y_offset += 25

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.state == GameState.MENU:
                    choice = self.menu.handle_input(event)
                    if choice == 0:  # Nouvelle partie
                        self.init_game()
                        self.state = GameState.PLAYING
                    elif choice == 1:  # Options
                        pass  # À implémenter
                    elif choice == 2:  # Quitter
                        running = False

                elif self.state == GameState.PLAYING:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.state = GameState.MENU

            # Mise à jour et dessin selon l'état
            if self.state == GameState.MENU:
                self.menu.draw(screen)

            elif self.state == GameState.PLAYING:
                # Mise à jour
                self.player.update(self.platforms)
                self.enemies.update(self.platforms)

                # Dessin
                self.draw_game_background()

                # Dessiner les plateformes
                for platform in self.platforms:
                    screen.blit(platform.image, platform.rect)

                # Dessiner les ennemis
                for enemy in self.enemies:
                    screen.blit(enemy.image, enemy.rect)

                # Dessiner le joueur
                screen.blit(self.player.image, self.player.rect)

                # HUD
                self.draw_hud()
                self.draw_instructions()

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()


# Lancer le jeu
if __name__ == "__main__":
    game = Game()
>>>>>>> f0f359a (Initial commit)
    game.run()
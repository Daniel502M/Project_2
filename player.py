import pygame
import math
from settings import PLAYER_SPEED, MAP_WIDTH, MAP_HEIGHT


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.original_image = pygame.image.load('assets/player.png').convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)

        self.speed = PLAYER_SPEED
        self.health = 100
        self.alive = True
        self.ammo = 20
        self.shooting = False
        self.shoot_cooldown = 250
        self.last_shot = pygame.time.get_ticks()
        self.reload_font = pygame.font.Font(None, 30)
        self.health_font = pygame.font.Font(None, 32)

        self.coins = 0

        self.hitbox_width = int(self.rect.width * 0.35)
        self.hitbox_height = int(self.rect.height * 0.55)
        self.hitbox = pygame.Rect(0, 0, self.hitbox_width, self.hitbox_height)
        self.update_hitbox()

        self.health_images = {
            0: pygame.image.load('assets/Hp_player/0_hp.png').convert_alpha(),
            10: pygame.image.load('assets/Hp_player/10_hp.png').convert_alpha(),
            20: pygame.image.load('assets/Hp_player/20_hp.png').convert_alpha(),
            30: pygame.image.load('assets/Hp_player/30_hp.png').convert_alpha(),
            40: pygame.image.load('assets/Hp_player/40_hp.png').convert_alpha(),
            50: pygame.image.load('assets/Hp_player/50_hp.png').convert_alpha(),
            60: pygame.image.load('assets/Hp_player/60_hp.png').convert_alpha(),
            70: pygame.image.load('assets/Hp_player/70_hp.png').convert_alpha(),
            80: pygame.image.load('assets/Hp_player/80_hp.png').convert_alpha(),
            90: pygame.image.load('assets/Hp_player/90_hp.png').convert_alpha(),
            100: pygame.image.load('assets/Hp_player/100_hp.png').convert_alpha()
        }

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
        print(f"Игрок получил урон! Текущее здоровье: {self.health}")
        if self.health == 0:
            self.die()

    def die(self):
        self.alive = False
        print("Player has died!")

    def update(self, keys, mouse_pos, bullets_group, obstacles, shoot_sound=None):
        dx, dy = self.handle_movement(keys)
        self.rotate(mouse_pos)
        self.handle_shooting(mouse_pos, bullets_group, shoot_sound)
        self.move_and_collide(dx, dy, obstacles)
        self.update_hitbox()

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def draw_hitbox(self, screen, offset):
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox.move(-offset), 2)

    def draw_health(self, screen):
        # Сортируем ключи словаря с изображениями по убыванию, чтобы сначала проверять наибольшие значения здоровья
        sorted_healths = sorted(self.health_images.keys(), reverse=True)

        for hp in sorted_healths:
            if self.health >= hp:
                screen.blit(self.health_images[hp], (10, 40))
                break
        else:
            # Если здоровье меньше минимального доступного значения, отображаем изображение для 0 HP
            screen.blit(self.health_images[0], (10, 10))

    def handle_movement(self, keys):
        dx = dy = 0
        if keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_s]: dy += self.speed
        if keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_d]: dx += self.speed
        return dx, dy

    def rotate(self, mouse_pos):
        rel_x = mouse_pos[0] - self.rect.centerx
        rel_y = mouse_pos[1] - self.rect.centery
        angle = math.degrees(-math.atan2(rel_y, rel_x)) + 282
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def handle_shooting(self, mouse_pos, bullets_group, shoot_sound=None):
        now = pygame.time.get_ticks()
        if self.shooting and now - self.last_shot > self.shoot_cooldown and self.ammo > 0:
            from bullet import Bullet  # импорт внутри, чтобы избежать цикличности
            bullet = Bullet(self.rect.center, mouse_pos)
            bullets_group.add(bullet)
            self.ammo -= 1
            self.last_shot = now
            if shoot_sound:
                shoot_sound.play()

    def draw_reload_indicator(self, screen):
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.shoot_cooldown:
            text = self.reload_font.render("Reloading...", True, (255, 0, 0))
            screen.blit(text, (10, 70))

    def move_and_collide(self, dx, dy, obstacles):
        slide_speed = self.speed * 0.3  # скорость скольжения (≤ 30% от обычной)
        original_x = self.hitbox.x
        original_y = self.hitbox.y

        # Двигаемся по X
        self.hitbox.x += dx
        collided_x = None
        for obstacle in obstacles:
            if self.hitbox.colliderect(obstacle):
                collided_x = obstacle
                if dx > 0:
                    self.hitbox.right = obstacle.left
                elif dx < 0:
                    self.hitbox.left = obstacle.right

        # Двигаемся по Y
        self.hitbox.y += dy
        collided_y = None
        for obstacle in obstacles:
            if self.hitbox.colliderect(obstacle):
                collided_y = obstacle
                if dy > 0:
                    self.hitbox.bottom = obstacle.top
                elif dy < 0:
                    self.hitbox.top = obstacle.bottom

        # Скользим по Y если заблокирован X
        if collided_x and not collided_y and abs(dy) > 0:
            self.hitbox.x = original_x
            self.hitbox.y += math.copysign(slide_speed, dy)
            for obstacle in obstacles:
                if self.hitbox.colliderect(obstacle):
                    self.hitbox.y -= math.copysign(slide_speed, dy)
                    break

        # Скользим по X если заблокирован Y
        if collided_y and not collided_x and abs(dx) > 0:
            self.hitbox.y = original_y
            self.hitbox.x += math.copysign(slide_speed, dx)
            for obstacle in obstacles:
                if self.hitbox.colliderect(obstacle):
                    self.hitbox.x -= math.copysign(slide_speed, dx)
                    break

        # Ограничения карты
        self.hitbox.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))
        self.rect.center = self.hitbox.center

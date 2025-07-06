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
        self.armor = 0  # ← броня
        self.max_health = 100
        self.armor = 0  # Новое: броня
        self.alive = True
        self.ammo = 20
        self.shooting = False
        self.shoot_cooldown = 250
        self.last_shot = pygame.time.get_ticks()
        self.reload_font = pygame.font.Font(None, 30)
        self.health_font = pygame.font.Font(None, 32)

        self.coins = 50

        self.hitbox_width = int(self.rect.width * 0.35)
        self.hitbox_height = int(self.rect.height * 0.55)
        self.hitbox = pygame.Rect(0, 0, self.hitbox_width, self.hitbox_height)
        self.update_hitbox()

        self.health_images = {
            i: pygame.image.load(f'assets/Hp_player/{i}_hp.png').convert_alpha()
            for i in range(0, 101, 10)
        }

        self.armor_images = {
            i: pygame.image.load(f'assets/Armor_player/{i}_armor.png').convert_alpha()
            for i in range(10, 101, 10)
        }

    def take_damage(self, amount):
        # Сначала броня
        if self.armor > 0:
            absorbed = min(self.armor, amount)
            self.armor -= absorbed
            amount -= absorbed
            print(f"Броня поглотила {absorbed} урона. Осталось брони: {self.armor}")

        # Остаток урона по здоровью
        if amount > 0:
            self.health -= amount
            print(f"Игрок получил {amount} урона! Здоровье: {self.health}")
            if self.health <= 0:
                self.health = 0
                self.die()

    def heal(self, amount):
        old_hp = self.health
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
        print(f"Здоровье восстановлено с {old_hp} до {self.health}")

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

    def draw_status_bars(self, screen):
        # Отображение плашки здоровья
        sorted_healths = sorted(self.health_images.keys(), reverse=True)
        for hp in sorted_healths:
            if self.health >= hp:
                screen.blit(self.health_images[hp], (10, 40))  # Здоровье на (10, 40)
                break
        else:
            screen.blit(self.health_images[0], (10, 40))

        # Отображение плашки брони — если броня есть
        if self.armor > 0:
            sorted_armors = sorted(self.armor_images.keys(), reverse=True)
            for ar in sorted_armors:
                if self.armor >= ar:
                    screen.blit(self.armor_images[ar], (10, 78))  # Броня чуть ниже
                    break

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
            from bullet import Bullet
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
        slide_speed = self.speed * 0.3
        original_x = self.hitbox.x
        original_y = self.hitbox.y

        self.hitbox.x += dx
        collided_x = None
        for obstacle in obstacles:
            if self.hitbox.colliderect(obstacle):
                collided_x = obstacle
                if dx > 0:
                    self.hitbox.right = obstacle.left
                elif dx < 0:
                    self.hitbox.left = obstacle.right

        self.hitbox.y += dy
        collided_y = None
        for obstacle in obstacles:
            if self.hitbox.colliderect(obstacle):
                collided_y = obstacle
                if dy > 0:
                    self.hitbox.bottom = obstacle.top
                elif dy < 0:
                    self.hitbox.top = obstacle.bottom

        if collided_x and not collided_y and abs(dy) > 0:
            self.hitbox.x = original_x
            self.hitbox.y += math.copysign(slide_speed, dy)
            for obstacle in obstacles:
                if self.hitbox.colliderect(obstacle):
                    self.hitbox.y -= math.copysign(slide_speed, dy)
                    break

        if collided_y and not collided_x and abs(dx) > 0:
            self.hitbox.y = original_y
            self.hitbox.x += math.copysign(slide_speed, dx)
            for obstacle in obstacles:
                if self.hitbox.colliderect(obstacle):
                    self.hitbox.x -= math.copysign(slide_speed, dx)
                    break

        self.hitbox.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))
        self.rect.center = self.hitbox.center

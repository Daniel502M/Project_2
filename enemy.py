import pygame
import math
import random
from settings import ENEMY_SPEED, MAP_WIDTH, MAP_HEIGHT

PATROL_RADIUS = 200
CHASE_RADIUS = 250
VISION_RANGE = 250


class Enemy(pygame.sprite.Sprite):
    def __init__(self, player_rect, screen_width, screen_height, all_obstacles):
        super().__init__()
        self.speed = ENEMY_SPEED
        self.health = 25
        self.alive = True
        self.state = "patrolling"
        self.current_frame = 0
        self.angle = 0
        self.animation_speed = 0.1
        self.attack_damage_applied = False

        self.move_frames = [pygame.image.load(f"assets/Animation/Zombie_Brown_Animation_{i+1}.png").convert_alpha() for i in range(7)]
        self.attack_frames = [pygame.image.load(f"assets/Attack_Animation/Zombie_Brown_Attack_Animation_{i+1}.png").convert_alpha() for i in range(4)]
        self.death_frames = [pygame.image.load(f"assets/Zombie_Kill/Zombie_Brown_Kill_{i+1}.png").convert_alpha() for i in range(2)]

        self.original_image = self.move_frames[0]
        self.image = self.original_image

        spawn_pos = random_spawn_position(player_rect, screen_width, screen_height, all_obstacles)
        self.rect = self.image.get_rect(center=spawn_pos)
        self.hitbox_width = int(self.rect.width * 0.3)
        self.hitbox_height = int(self.rect.height * 0.5)
        self.hitbox = pygame.Rect(0, 0, self.hitbox_width, self.hitbox_height)
        self.update_hitbox()

        self.coin_group = None  # Это установим позже из main.py

        self.patrol_origin = self.rect.center
        self.patrol_points = self.generate_patrol_points()
        self.patrol_index = 0
        self.vision_lost_timer = 0

    def generate_patrol_points(self):
        points = []
        for _ in range(3):
            offset = pygame.Vector2(random.randint(-PATROL_RADIUS, PATROL_RADIUS),
                                    random.randint(-PATROL_RADIUS, PATROL_RADIUS))
            point = (self.patrol_origin[0] + offset.x, self.patrol_origin[1] + offset.y)
            points.append(point)
        return points

    def update(self, player, obstacles):
        if not self.alive:
            self.animate_death()
            return

        if self.state != "attacking":
            self.detect_player(player, obstacles)

        if self.state == "attacking":
            self.animate_attack(player)
        elif self.state == "chasing":
            self.chase_player(player, obstacles)
        elif self.state == "patrolling":
            self.patrol(obstacles)
        elif self.state == "idle":
            self.animate_idle(player)

        self.rotate_towards(self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def detect_player(self, player, obstacles):
        dist = pygame.Vector2(player.rect.center).distance_to(self.rect.center)
        if dist <= VISION_RANGE:
            line_clear = not any(ob.clipline(self.hitbox.center, player.rect.center) for ob in obstacles)
            if line_clear:
                self.state = "chasing"
                self.vision_lost_timer = 0
                return

        if self.state == "chasing":
            self.vision_lost_timer += 1
            if self.vision_lost_timer > 120:
                self.state = "patrolling"
                self.vision_lost_timer = 0

    def chase_player(self, player, obstacles):
        if self.hitbox.colliderect(player.hitbox):
            self.state = "attacking"
            return

        self.move_towards(player.rect.center, obstacles)
        self.animate_movement(player)

    def patrol(self, obstacles):
        target = self.patrol_points[self.patrol_index]
        if pygame.Vector2(self.rect.center).distance_to(target) < 10:
            self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)
        else:
            self.move_towards(target, obstacles)
            self.animate_movement_simple()

    def move_towards(self, target_pos, obstacles):
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        dx = dx / dist * self.speed
        dy = dy / dist * self.speed

        # Движение по X
        self.rect.x += dx
        self.update_hitbox()
        for ob in obstacles:
            if self.hitbox.colliderect(ob):
                overlap = self.hitbox.right - ob.left if dx > 0 else ob.right - self.hitbox.left
                if overlap > ob.width * 0.3:
                    self.rect.x -= dx
                    self.update_hitbox()
                break

        # Движение по Y
        self.rect.y += dy
        self.update_hitbox()
        for ob in obstacles:
            if self.hitbox.colliderect(ob):
                overlap = self.hitbox.bottom - ob.top if dy > 0 else ob.bottom - self.hitbox.top
                if overlap > ob.height * 0.3:
                    self.rect.y -= dy
                    self.update_hitbox()
                break

        self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))
        self.update_hitbox()

        direction = pygame.Vector2(target_pos) - pygame.Vector2(self.rect.center)
        self.angle = math.degrees(-math.atan2(direction.y, direction.x)) + 90

    def animate_attack(self, player):
        self.current_frame += self.animation_speed
        index = int(self.current_frame)
        if index < len(self.attack_frames):
            self.original_image = self.attack_frames[index]
            self.rotate_towards_player(player)
            if index == 2 and not self.attack_damage_applied:
                self.attack_damage_applied = True
                player.take_damage(5)
        else:
            self.current_frame = 0
            self.attack_damage_applied = False
            self.state = "chasing"

    def animate_movement(self, player):
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.move_frames):
            self.current_frame = 0
        self.original_image = self.move_frames[int(self.current_frame)]
        self.rotate_towards_player(player)

    def animate_movement_simple(self):
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.move_frames):
            self.current_frame = 0
        self.original_image = self.move_frames[int(self.current_frame)]

    def animate_idle(self, player):
        self.original_image = self.move_frames[0]
        self.rotate_towards_player(player)

    def animate_death(self):
        self.current_frame += self.animation_speed
        index = int(self.current_frame)
        if index < len(self.death_frames):
            self.original_image = self.death_frames[index]
        else:
            self.kill()

    def rotate_towards(self, angle):
        self.angle = angle
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def rotate_towards_player(self, player):
        direction = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        self.angle = math.degrees(-math.atan2(direction.y, direction.x)) + 90
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def take_damage(self, amount):
        if self.alive:
            self.health -= amount
            if self.health <= 0:
                self.alive = False
                self.state = "dead"
                self.current_frame = 0

                if self.coin_group:  # Выпадение монет
                    from coin import Coin
                    for _ in range(random.randint(0, 5)):
                        offset = pygame.Vector2(random.randint(-15, 15), random.randint(-15, 15))
                        self.coin_group.add(Coin(self.rect.center + offset))

    def update_hitbox(self):
        self.hitbox.center = self.rect.center


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, pos, target, speed=300):
        super().__init__()
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 100, 100), (4, 4), 4)
        self.rect = self.image.get_rect(center=pos)
        direction = pygame.Vector2(target) - pygame.Vector2(pos)
        if direction.length() == 0:
            direction = pygame.Vector2(1, 0)
        self.velocity = direction.normalize() * speed
        self.spawn_time = pygame.time.get_ticks()

    def update(self, dt, bullet_blocking, player):
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt

        if pygame.sprite.collide_rect(self, player):
            player.take_damage(10)
            self.kill()
            return

        for ob in bullet_blocking:
            if ob.colliderect(self.rect):
                self.kill()
                return

        if pygame.time.get_ticks() - self.spawn_time > 3000:
            self.kill()


class RangedEnemy(Enemy):
    def __init__(self, player_rect, screen_width, screen_height, all_obstacles):
        super().__init__(player_rect, screen_width, screen_height, all_obstacles)
        self.last_shot = 0
        self.shot_cooldown = 1500

    def update(self, player, obstacles, bullets_group, shoot_sound=None):
        super().update(player, obstacles)

        if self.alive and self.state == "chasing":
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shot_cooldown:
                self.last_shot = now
                bullet = EnemyBullet(self.rect.center, player.rect.center)
                bullets_group.add(bullet)
                if shoot_sound:
                    shoot_sound.play()


def random_spawn_position(player_rect, screen_width, screen_height, all_obstacles):
    max_attempts = 100
    for _ in range(max_attempts):
        x = random.randint(0, MAP_WIDTH)
        y = random.randint(0, MAP_HEIGHT)
        spawn_rect = pygame.Rect(x - 20, y - 20, 40, 40)

        visible_area = pygame.Rect(
            player_rect.centerx - screen_width // 2,
            player_rect.centery - screen_height // 2,
            screen_width,
            screen_height
        )

        if visible_area.colliderect(spawn_rect):
            continue

        if any(spawn_rect.colliderect(ob) for ob in all_obstacles):
            continue

        return x, y

    return random.choice([
        (random.randint(0, MAP_WIDTH), -60),
        (random.randint(0, MAP_WIDTH), MAP_HEIGHT + 60),
        (-60, random.randint(0, MAP_HEIGHT)),
        (MAP_WIDTH + 60, random.randint(0, MAP_HEIGHT))
    ])

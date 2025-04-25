import pygame
import math
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Square Shooter")
clock = pygame.time.Clock()

# Загружаем и поворачиваем изображение игрока на заданный угол
player_image_original = pygame.image.load("player.png").convert_alpha()
player_image_original = pygame.transform.scale(player_image_original, (80, 80))

MAP_WIDTH = 3000
MAP_HEIGHT = 3000

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (0, 200, 0)

player_size = 40
player_pos = [1000, 1000]
player_speed = 5

bullet_radius = 5
bullet_speed = 10
bullets = []

camera_offset = [0, 0]

# Фон
tile_size = 100
tile_surface = pygame.Surface((tile_size, tile_size))
tile_surface.fill((30, 30, 30))
pygame.draw.rect(tile_surface, (50, 50, 50), (0, 0, tile_size, tile_size), 2)

# Враги
enemies = []
enemy_radius = 20
enemy_speed = 2
enemy_spawn_timer = 0
enemy_spawn_delay = 2000  # миллисекунды

font = pygame.font.SysFont(None, 36)

# Стрельба
can_shoot = True
shoot_delay = 200  # мс
last_shot_time = 0

# Патроны
max_ammo = 20
total_ammo = 60  # запасные патроны
ammo_pickups = []
pickup_radius = 10
pickup_amount = 5
current_ammo = max_ammo
reload_delay = 1000  # мс
reloading = False
reload_start_time = 0

pygame.mouse.set_visible(False)

player_hp = 5
enemy_damage_delay = 1000  # мс
last_damage_times = {}  # по enemy_id: время последнего удара

initial_rotation_angle = 290  # например, 290 градусов
player_image_original = pygame.transform.rotate(player_image_original, initial_rotation_angle)


def spawn_ammo(pos):
    ammo_pickups.append({'pos': pos, 'amount': pickup_amount})


def draw_background(camera_offset):
    for x in range(-tile_size, 3000, tile_size):
        for y in range(-tile_size, 3000, tile_size):
            screen.blit(tile_surface, (x - camera_offset[0], y - camera_offset[1]))


def draw_crosshair(pos):
    pygame.draw.line(screen, WHITE, (pos[0] - 10, pos[1]), (pos[0] + 10, pos[1]), 2)
    pygame.draw.line(screen, WHITE, (pos[0], pos[1] - 10), (pos[0], pos[1] + 10), 2)


def shoot_bullet(start_pos, target_pos):
    dx = target_pos[0] - start_pos[0]
    dy = target_pos[1] - start_pos[1]
    angle = math.atan2(dy, dx)
    vx = math.cos(angle) * bullet_speed
    vy = math.sin(angle) * bullet_speed
    bullets.append({'pos': list(start_pos), 'vel': (vx, vy)})


def spawn_enemy():
    margin = 100
    for _ in range(10):  # Попытка найти подходящее место
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(camera_offset[0] - margin, camera_offset[0] + WIDTH + margin)
            y = camera_offset[1] - margin
        elif side == 'bottom':
            x = random.randint(camera_offset[0] - margin, camera_offset[0] + WIDTH + margin)
            y = camera_offset[1] + HEIGHT + margin
        elif side == 'left':
            x = camera_offset[0] - margin
            y = random.randint(camera_offset[1] - margin, camera_offset[1] + HEIGHT + margin)
        else:
            x = camera_offset[0] + WIDTH + margin
            y = random.randint(camera_offset[1] - margin, camera_offset[1] + HEIGHT + margin)

        if 0 <= x <= MAP_WIDTH and 0 <= y <= MAP_HEIGHT:
            enemies.append({'pos': [x, y]})
            break  # Успешный спавн — выйти


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


running = True


def draw_ammo_counter():
    # Патроны: Заряженные / Запас
    ammo_text = font.render(f"Ammo: {current_ammo} / {total_ammo}", True, WHITE)
    screen.blit(ammo_text, (20, 100))

    # HP
    hp_color = RED if player_hp <= 2 else WHITE
    hp_text = font.render(f"HP: {player_hp}", True, hp_color)
    screen.blit(hp_text, (20, 60))


# Внутри основного цикла:
while running:
    dt = clock.tick(60)
    current_time = pygame.time.get_ticks()
    mouse_pos = pygame.mouse.get_pos()
    world_mouse_pos = [mouse_pos[0] + camera_offset[0], mouse_pos[1] + camera_offset[1]]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Стрельба при зажатой кнопке
    if pygame.mouse.get_pressed()[0] and can_shoot and current_ammo > 0 and not reloading:
        shoot_bullet(player_pos[:], world_mouse_pos)
        can_shoot = False
        last_shot_time = current_time
        current_ammo -= 1

    # Задержка между выстрелами
    if not can_shoot and current_time - last_shot_time >= shoot_delay:
        can_shoot = True

    # Автоматическая перезарядка (если патроны закончились)
    if current_ammo == 0 and not reloading:
        reloading = True
        reload_start_time = current_time

    if reloading and current_time - reload_start_time >= reload_delay:
        refill = min(max_ammo, total_ammo)
        current_ammo = refill
        total_ammo -= refill
        reloading = False

    # Управление игроком
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and player_pos[1] - player_speed >= 0:
        player_pos[1] -= player_speed
    if keys[pygame.K_s] and player_pos[1] + player_speed <= MAP_HEIGHT - player_size:
        player_pos[1] += player_speed
    if keys[pygame.K_a] and player_pos[0] - player_speed >= 0:
        player_pos[0] -= player_speed
    if keys[pygame.K_d] and player_pos[0] + player_speed <= MAP_WIDTH - player_size:
        player_pos[0] += player_speed

    # Камера
    camera_offset[0] = player_pos[0] - WIDTH // 2
    camera_offset[1] = player_pos[1] - HEIGHT // 2

    for pickup in ammo_pickups[:]:
        if distance(player_pos, pickup['pos']) < player_size // 2 + pickup_radius:
            total_ammo += pickup['amount']
            ammo_pickups.remove(pickup)

    # Отрисовка
    screen.fill(BLACK)
    draw_background(camera_offset)

    for pickup in ammo_pickups:
        screen_x = int(pickup['pos'][0] - camera_offset[0])
        screen_y = int(pickup['pos'][1] - camera_offset[1])
        pygame.draw.circle(screen, (100, 100, 255), (screen_x, screen_y), pickup_radius)

    # Игрок — вращение за курсором
    dx = world_mouse_pos[0] - player_pos[0]
    dy = world_mouse_pos[1] - player_pos[1]
    angle_deg = math.degrees(math.atan2(-dy, dx))
    rotated_surf = pygame.transform.rotate(player_image_original, angle_deg)
    rect = rotated_surf.get_rect(center=(player_pos[0] - camera_offset[0], player_pos[1] - camera_offset[1]))
    screen.blit(rotated_surf, rect)

    # Пули, враги и столкновения — как раньше
    for bullet in bullets[:]:
        bullet['pos'][0] += bullet['vel'][0]
        bullet['pos'][1] += bullet['vel'][1]
        screen_pos = (int(bullet['pos'][0] - camera_offset[0]), int(bullet['pos'][1] - camera_offset[1]))
        pygame.draw.circle(screen, WHITE, screen_pos, bullet_radius)

        for enemy in enemies[:]:
            if distance(bullet['pos'], enemy['pos']) < bullet_radius + enemy_radius:
                spawn_ammo(enemy['pos'])  # <-- Вот это добавим
                bullets.remove(bullet)
                enemies.remove(enemy)
                break

    # Проверка урона от врагов
    for i, enemy in enumerate(enemies):
        dist = distance(player_pos, enemy['pos'])
        if dist < player_size // 2 + enemy_radius:
            last_time = last_damage_times.get(i, 0)
            if current_time - last_time >= enemy_damage_delay:
                player_hp -= 1
                last_damage_times[i] = current_time
                if player_hp <= 0:
                    print("GAME OVER")
                    running = False

    for enemy in enemies:
        dx = player_pos[0] - enemy['pos'][0]
        dy = player_pos[1] - enemy['pos'][1]
        angle = math.atan2(dy, dx)
        new_x = enemy['pos'][0] + math.cos(angle) * enemy_speed
        new_y = enemy['pos'][1] + math.sin(angle) * enemy_speed

        # Ограничения по границам карты
        if 0 <= new_x <= MAP_WIDTH and 0 <= new_y <= MAP_HEIGHT:
            enemy['pos'][0] = new_x
            enemy['pos'][1] = new_y

        pygame.draw.circle(screen, GREEN,
                           (int(enemy['pos'][0] - camera_offset[0]), int(enemy['pos'][1] - camera_offset[1])),
                           enemy_radius)

    # Спавн врагов
    enemy_spawn_timer += dt
    if enemy_spawn_timer >= enemy_spawn_delay:
        spawn_enemy()
        enemy_spawn_timer = 0

    # Прицел
    draw_crosshair(mouse_pos)

    # Отображение патронов
    draw_ammo_counter()

    pygame.display.flip()

pygame.quit()
sys.exit()


# TODO:
# давай реализуем следующее:
# HUD-элементы:
# Индикатор перезарядки (например, полоса или надпись "Reloading...").
# Таймер выживания или счётчик убийств.
# Мини-карта (хотя бы схематичная точка игрока и врагов).
# Отображение текущего количества врагов на карте.
# только распиши подробно куда и что добавляем

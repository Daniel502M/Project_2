import pygame
import sys
import random

from settings import WIDTH, HEIGHT, FPS
from player import Player
from enemy import Enemy
from bullet import Bullet
from pickup import AmmoPickup
from map_loader import TileMap


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

tile_map = TileMap("Maps/Cart_Game.tmx")
obstacles = tile_map.get_collision_rects()

# Прицел
crosshair_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.circle(crosshair_surface, (255, 0, 0), (20, 20), 15, 2)

# Игрок и группы
player = Player((WIDTH // 2, HEIGHT // 2))
player_group = pygame.sprite.GroupSingle(player)
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
pickups = pygame.sprite.Group()

# Счётчики
kills = 0
start_time = pygame.time.get_ticks()

# Спавн врагов
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 2000)

font = pygame.font.SysFont(None, 30)

# Игровой цикл
while True:
    dt = clock.tick(FPS)
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    enemies.update(player, obstacles)

    # События
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == SPAWN_EVENT:
            enemies.add(Enemy(player.rect.center))
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                player.shooting = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                player.shooting = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                # Создать нового врага рядом с игроком (например, сверху)
                new_enemy = Enemy((player.rect.centerx, player.rect.centery - 100))

    # Камера
    offset = pygame.Vector2(player.rect.center) - pygame.Vector2(WIDTH // 2, HEIGHT // 2)

    # Учитываем смещение камеры для мыши
    mouse_world_pos = (mouse_pos[0] + offset.x, mouse_pos[1] + offset.y)

    # Обновления
    player.update(keys, mouse_world_pos, bullets, obstacles)
    bullets.update(obstacles)
    enemies.update(player, obstacles)
    pickups.update()

    # Столкновения
    for bullet in bullets:
        hit_list = pygame.sprite.spritecollide(bullet, enemies, False)
        for enemy in hit_list:
            line_blocked = any(obs.clipline(bullet.rect.center, enemy.rect.center) for obs in obstacles)
            if line_blocked:
                continue  # Не наносим урон — между пулей и врагом стена

            enemy.health -= 25
            bullet.kill()
            if enemy.health <= 0:
                pickups.add(AmmoPickup(enemy.rect.center))
                enemy.kill()
                kills += 1

    for enemy in enemies:
        if player.hitbox.colliderect(enemy.hitbox):
            # Проверяем, нет ли стены между игроком и врагом
            blocked = False
            for obs in obstacles:
                if obs.clipline(player.hitbox.center, enemy.hitbox.center):
                    blocked = True
                    break
            if not blocked:
                player.health -= 1
                break  # Урон только от одного врага за кадр

    pickup_hits = pygame.sprite.spritecollide(player, pickups, True)
    for pickup in pickup_hits:
        player.ammo += 5

    # Отрисовка
    screen.fill((30, 30, 30))

    # Рисуем карту со смещением камеры
    tile_map.draw(screen, offset)

    for rect in obstacles:
        pygame.draw.rect(screen, (0, 0, 255), rect.move(-offset), 2)  # Красные рамки

    # Рисуем все объекты со сдвигом offset
    for pickup in pickups:
        screen.blit(pickup.image, pickup.rect.topleft - offset)

    for bullet in bullets:
        screen.blit(bullet.image, bullet.rect.topleft - offset)

    for enemy in enemies:
        screen.blit(enemy.image, enemy.rect.topleft - offset)
        pygame.draw.rect(screen, (255, 0, 0), enemy.hitbox.move(-offset), 2)

    screen.blit(player.image, player.rect.topleft - offset)
    player.draw_hitbox(screen, offset)

    # Прицел
    screen.blit(crosshair_surface, (mouse_pos[0] - 20, mouse_pos[1] - 20))

    # HUD
    ammo_text = font.render(f"Ammo: {player.ammo}", True, (255, 255, 255))
    health_text = font.render(f"Health: {player.health}", True, (255, 0, 0))
    time_text = font.render(f"Survived: {(pygame.time.get_ticks() - start_time) // 1000}s", True, (255, 255, 255))
    kills_text = font.render(f"Kills: {kills}", True, (255, 255, 255))
    enemies_text = font.render(f"Enemies: {len(enemies)}", True, (255, 255, 255))

    screen.blit(ammo_text, (10, 10))
    screen.blit(health_text, (10, 40))
    screen.blit(time_text, (10, 70))
    screen.blit(kills_text, (10, 100))
    screen.blit(enemies_text, (10, 130))

    # Мини-карта
    mini_map_rect = pygame.Rect(WIDTH - 110, 10, 100, 100)
    pygame.draw.rect(screen, (50, 50, 50), mini_map_rect, border_radius=4)
    pygame.draw.rect(screen, (255, 255, 255), mini_map_rect, 2, border_radius=4)

    # Размер мини-карты и её масштаб относительно области вокруг игрока
    MINI_MAP_SCALE = 0.1  # Чем меньше, тем больше область охвата на миникарте
    MAP_VIEW_SIZE = 1000  # Отображаемая область игрового мира на миникарте

    center_x, center_y = player.rect.center

    # Рисуем игрока в центре миникарты
    pygame.draw.circle(screen, (0, 255, 0), (mini_map_rect.centerx, mini_map_rect.centery), 3)

    # Рисуем врагов
    for enemy in enemies:
        dx = enemy.rect.centerx - center_x
        dy = enemy.rect.centery - center_y

        # Масштабирование
        map_x = mini_map_rect.centerx + int(dx * MINI_MAP_SCALE)
        map_y = mini_map_rect.centery + int(dy * MINI_MAP_SCALE)

        # Ограничение отрисовки врагов только в пределах миникарты
        if mini_map_rect.collidepoint(map_x, map_y):
            pygame.draw.circle(screen, (255, 0, 0), (map_x, map_y), 2)

    pygame.display.update()

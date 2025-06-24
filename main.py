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
pygame.mixer.init()

# # 🎵 Загрузка и запуск фоновой музыки
# pygame.mixer.music.load("Zombie_Games_Sound.mp3")
# pygame.mixer.music.set_volume(0.3)
# pygame.mixer.music.play(-1)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

door_open_time = {}  # {door_id: время_открытия}

# Загружаем карту и препятствия
tile_map = TileMap("Maps/Laboratory_Cart/Laboratory_Cart..tmx")
static_obstacles, door_obstacles = tile_map.get_collision_rects()
object_obstacles, _ = tile_map.get_object_collision_rects()

# Загружаем спрайт-лист дверей (Sprite_for_Card_Game.png)
door_spritesheet = pygame.image.load("Maps/Laboratory_Cart/Sprite_for_Cart_Game.png").convert_alpha()

# Координаты фрагментов (размер каждой 64×64 — уточни)
SPRITE_SIZE = 64
door_gids = {
    15: ("top", 0, 0),     # gid 15 — верхняя дверь
    20: ("bottom", 64, 0), # gid 20 — нижняя дверь
    12: ("right", 128, 0), # gid 12 — правая
    13: ("left", 192, 0),  # gid 13 — левая
}

# Подготовка изображений открытых дверей
door_open_images = {}
for gid, (name, sx, sy) in door_gids.items():
    clip = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
    clip.blit(door_spritesheet, (0, 0), pygame.Rect(sx, sy, SPRITE_SIZE, SPRITE_SIZE))
    door_open_images[gid] = clip

open_door_sprites = {}  # door_id → изображение

# Объединяем препятствия
static_obstacles += object_obstacles
opened_doors = set()
crosshair_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.circle(crosshair_surface, (255, 0, 0), (20, 20), 15, 2)

map_pixel_width = tile_map.tmx_data.width * tile_map.tmx_data.tilewidth
map_pixel_height = tile_map.tmx_data.height * tile_map.tmx_data.tileheight
player = Player((map_pixel_width // 2, map_pixel_height - 100))

player_group = pygame.sprite.GroupSingle(player)
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
pickups = pygame.sprite.Group()

kills = 0
start_time = pygame.time.get_ticks()

SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 2000)
font = pygame.font.SysFont(None, 30)

while True:
    dt = clock.tick(FPS) / 1000
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == SPAWN_EVENT:
            if len(enemies) < 50:
                enemies.add(Enemy(player.rect, WIDTH, HEIGHT))
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            player.shooting = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            player.shooting = False

    offset = pygame.Vector2(player.rect.center) - pygame.Vector2(WIDTH // 2, HEIGHT // 2)
    mouse_world = (mouse_pos[0] + offset.x, mouse_pos[1] + offset.y)

    # Управление дверями
    for door in door_obstacles:
        did = door["id"]
        gid = door["gid"]
        if did in opened_doors:
            if pygame.time.get_ticks() - door_open_time[did] > 3000:
                opened_doors.remove(did)
                del door_open_time[did]
                del open_door_sprites[did]
            continue

        dist = pygame.Vector2(player.rect.center) - pygame.Vector2(door["rect"].center)
        if dist.length() < 50:
            opened_doors.add(did)
            door_open_time[did] = pygame.time.get_ticks()
            if gid in door_open_images:
                open_door_sprites[did] = door_open_images[gid]

    # Коллизии
    active_obstacles = static_obstacles + [
        door["rect"] for door in door_obstacles if door["id"] not in opened_doors
    ]
    bullet_blocking = static_obstacles + object_obstacles + [
        door["rect"] for door in door_obstacles if door["id"] not in opened_doors
    ]

    player.update(keys, mouse_world, bullets, active_obstacles)
    bullets.update(bullet_blocking)
    enemies.update(player, active_obstacles)
    pickups.update()

    # Пули и враги
    for bullet in bullets:
        for enemy in pygame.sprite.spritecollide(bullet, enemies, False):
            blocked = any(obs.clipline(bullet.rect.center, enemy.rect.center) for obs in bullet_blocking)
            if blocked:
                continue
            enemy.health -= 25
            bullet.kill()
            if enemy.health <= 0:
                pickups.add(AmmoPickup(enemy.rect.center))
                enemy.kill()
                kills += 1

    # Урон игроку
    for enemy in enemies:
        if player.hitbox.colliderect(enemy.hitbox):
            blocked = any(obs.clipline(player.hitbox.center, enemy.hitbox.center) for obs in active_obstacles)
            if not blocked:
                player.take_damage(1)
                break

    # Подбор
    for pickup in pygame.sprite.spritecollide(player, pickups, True):
        player.ammo += 5

    # Отображение
    screen.fill((30, 30, 30))
    tile_map.draw(screen, offset,
                  skip_door_ids={f"{d['pos'][0]}_{d['pos'][1]}" for d in door_obstacles if d['id'] in opened_doors})

    # Отрисовка дверей
    for door in door_obstacles:
        pos = door["rect"].topleft
        sp = (pos[0] - offset.x, pos[1] - offset.y)
        if door["id"] in opened_doors:
            # Используем open_gid
            img = tile_map.get_closed_door_image({"gid": door["open_gid"]})
            if img:
                screen.blit(img, sp)
        else:
            closed = tile_map.get_closed_door_image(door)
            if closed:
                screen.blit(closed, sp)

    # Коллизии
    for rect in active_obstacles:
        pygame.draw.rect(screen, (0, 0, 255), rect.move(-offset), 2)

    # Остальные объекты
    for group in (pickups, bullets, enemies):
        for spr in group:
            screen.blit(spr.image, spr.rect.topleft - offset)

    screen.blit(player.image, player.rect.topleft - offset)
    screen.blit(crosshair_surface, (mouse_pos[0] -20, mouse_pos[1] -20))

    # HUD
    ammo_text = font.render(f"Ammo: {player.ammo}", True, (255,255,255))
    health_text = font.render(f"Health: {player.health}", True, (255,0,0))
    time_text = font.render(f"Survived: {(pygame.time.get_ticks() - start_time)//1000}s",
                             True, (255,255,255))
    kills_text = font.render(f"Kills: {kills}", True, (255,255,255))
    enemies_text = font.render(f"Enemies: {len(enemies)}", True, (255,255,255))

    screen.blit(ammo_text, (10, 10))
    screen.blit(health_text, (10, 40))
    screen.blit(time_text, (10, 70))
    screen.blit(kills_text, (10, 100))
    screen.blit(enemies_text, (10, 130))

    # Мини-карта
    mini = pygame.Rect(WIDTH - 110, 10, 100, 100)
    pygame.draw.rect(screen, (50, 50, 50), mini, border_radius=4)
    pygame.draw.rect(screen, (255, 255, 255), mini, 2, border_radius=4)
    cx, cy = player.rect.center
    pygame.draw.circle(screen, (0, 255, 0), (mini.centerx, mini.centery), 3)
    for e in enemies:
        dx = e.rect.centerx - cx
        dy = e.rect.centery - cy
        mx = mini.centerx + int(dx * 0.1)
        my = mini.centery + int(dy * 0.1)
        if mini.collidepoint(mx, my):
            pygame.draw.circle(screen, (255,0,0),(mx, my),2)

    if not player.alive:
        go = pygame.font.SysFont(None,72)
        text = go.render("GAME OVER",True,(255,0,0))
        screen.blit(text,(WIDTH//2 -150, HEIGHT//2 -36))
        pygame.display.flip()
        pygame.time.delay(3000)
        pygame.quit()
        sys.exit()

    pygame.display.update()

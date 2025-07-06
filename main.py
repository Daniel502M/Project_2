import pygame
import sys
import random
from settings import WIDTH, HEIGHT, FPS
from player import Player
from enemy import Enemy, RangedEnemy
from bullet import Bullet
from pickup import AmmoPickup
from coin import Coin
from shop import Shop
from map_loader import TileMap
from menu import show_menu

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("assets/sounds/Zombie_Games_Sound.mp3")
pygame.mixer.music.set_volume(0.3)

player_shoot_sound = pygame.mixer.Sound("assets/sounds/player_shoot.mp3")
enemy_shoot_sound = pygame.mixer.Sound("assets/sounds/enemy_shoot.mp3")
enemy_death_sound = pygame.mixer.Sound("assets/sounds/enemy_death.mp3")
enemy_death_sound.set_volume(0.2)
player_shoot_sound.set_volume(0.3)
enemy_shoot_sound.set_volume(0.2)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

if not show_menu():
    pygame.quit()
    sys.exit()

# Старт музыки только после меню
pygame.mixer.music.play(-1)
pygame.mouse.set_visible(False)  # Скрываем курсор после меню

door_open_time = {}
tile_map = TileMap("Maps/Laboratory_Cart/Laboratory_Cart.tmx")
static_obstacles, door_obstacles = tile_map.get_collision_rects()
object_obstacles, _ = tile_map.get_object_collision_rects()

door_spritesheet = pygame.image.load("Maps/Laboratory_Cart/Sprite_for_Cart_Game.png").convert_alpha()
SPRITE_SIZE = 64
door_gids = {
    15: ("top", 0, 0),
    20: ("bottom", 64, 0),
    12: ("right", 128, 0),
    13: ("left", 192, 0),
}

door_open_images = {}
for gid, (name, sx, sy) in door_gids.items():
    clip = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
    clip.blit(door_spritesheet, (0, 0), pygame.Rect(sx, sy, SPRITE_SIZE, SPRITE_SIZE))
    door_open_images[gid] = clip

open_door_sprites = {}
static_obstacles += object_obstacles
opened_doors = set()
crosshair_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.circle(crosshair_surface, (255, 0, 0), (20, 20), 15, 2)

map_pixel_width = tile_map.tmx_data.width * tile_map.tmx_data.tilewidth
map_pixel_height = tile_map.tmx_data.height * tile_map.tmx_data.tileheight
player = Player((map_pixel_width // 2, map_pixel_height - 100))

player_group = pygame.sprite.GroupSingle(player)
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
pickups = pygame.sprite.Group()
coins = pygame.sprite.Group()

kills = 0
start_time = pygame.time.get_ticks()

SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 2000)
font = pygame.font.SysFont(None, 30)

shop = Shop()
shop_open = False
game_paused = False

while True:
    dt = clock.tick(FPS) / 1000
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if shop_open:
                    shop_open = False
                    pygame.mouse.set_visible(False)
                else:
                    game_paused = True
                    pygame.mouse.set_visible(True)
            elif event.key == pygame.K_t and not game_paused:
                shop_open = not shop_open
                pygame.mouse.set_visible(shop_open)

        if shop_open:
            result = shop.handle_event(event, player)
            if result == 'close':
                shop_open = False
                pygame.mouse.set_visible(False)

        elif not game_paused:
            if event.type == SPAWN_EVENT and len(enemies) < 50:
                enemies.add(
                    RangedEnemy(player.rect, WIDTH, HEIGHT, static_obstacles)
                    if random.random() < 0.2
                    else Enemy(player.rect, WIDTH, HEIGHT, static_obstacles)
                )
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                player.shooting = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                player.shooting = False

    if game_paused:
        pygame.mixer.music.pause()
        play = show_menu()
        if play:
            game_paused = False
            pygame.mouse.set_visible(False)
            pygame.mixer.music.unpause()
        else:
            pygame.quit()
            sys.exit()
        continue

    if shop_open:
        shop.draw(screen, player)
        pygame.display.flip()
        continue

    offset = pygame.Vector2(player.rect.center) - pygame.Vector2(WIDTH // 2, HEIGHT // 2)
    mouse_world = (mouse_pos[0] + offset.x, mouse_pos[1] + offset.y)

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

    active_obstacles = static_obstacles + [
        door["rect"] for door in door_obstacles if door["id"] not in opened_doors
    ]
    bullet_blocking = static_obstacles + object_obstacles + [
        door["rect"] for door in door_obstacles if door["id"] not in opened_doors
    ]

    player.update(keys, mouse_world, bullets, active_obstacles, shoot_sound=player_shoot_sound)
    bullets.update(dt, bullet_blocking, enemies)
    pickups.update()
    enemy_bullets.update(dt, bullet_blocking, player)

    for enemy in enemies:
        if isinstance(enemy, RangedEnemy):
            enemy.update(player, active_obstacles, enemy_bullets, shoot_sound=enemy_shoot_sound)
        else:
            enemy.update(player, active_obstacles)

    for bullet in bullets:
        for enemy in pygame.sprite.spritecollide(bullet, enemies, False):
            blocked = any(obs.clipline(bullet.rect.center, enemy.rect.center) for obs in bullet_blocking)
            if blocked:
                continue
            enemy.health -= 25
            bullet.kill()
            if enemy.health <= 0:
                for _ in range(random.randint(0, 5)):
                    coins.add(Coin(enemy.rect.center))
                enemy_death_sound.play()
                enemy.kill()
                kills += 1

    for coin in pygame.sprite.spritecollide(player, coins, True):
        player.coins += 1

    for enemy in enemies:
        if player.hitbox.colliderect(enemy.hitbox):
            blocked = any(obs.clipline(player.hitbox.center, enemy.hitbox.center) for obs in active_obstacles)
            if not blocked:
                player.take_damage(1)
                break

    for pickup in pygame.sprite.spritecollide(player, pickups, True):
        player.ammo += 5

    screen.fill((30, 30, 30))
    tile_map.draw(screen, offset,
                  skip_door_ids={f"{d['pos'][0]}_{d['pos'][1]}" for d in door_obstacles if d['id'] in opened_doors})

    for door in door_obstacles:
        pos = door["rect"].topleft
        sp = (pos[0] - offset.x, pos[1] - offset.y)
        if door["id"] in opened_doors:
            img = tile_map.get_closed_door_image({"gid": door["open_gid"]})
            if img:
                screen.blit(img, sp)
        else:
            closed = tile_map.get_closed_door_image(door)
            if closed:
                screen.blit(closed, sp)

    for rect in active_obstacles:
        pygame.draw.rect(screen, (0, 0, 255), rect.move(-offset), 2)

    for group in (pickups, coins, bullets, enemy_bullets, enemies):
        for spr in group:
            screen.blit(spr.image, spr.rect.topleft - offset)

    screen.blit(player.image, player.rect.topleft - offset)
    player.draw_health(screen)
    player.draw_armor(screen)
    screen.blit(crosshair_surface, (mouse_pos[0] - 20, mouse_pos[1] - 20))

    ammo_text = font.render(f"Ammo: {player.ammo}", True, (255, 255, 255))
    armor_text = font.render(f"Armor: {player.armor}", True, (0, 200, 255))
    time_text = font.render(f"Survived: {(pygame.time.get_ticks() - start_time) // 1000}s", True, (255, 255, 255))
    kills_text = font.render(f"Kills: {kills}", True, (255, 255, 255))
    enemies_text = font.render(f"Enemies: {len(enemies)}", True, (255, 255, 255))

    coin_icon = pygame.image.load("assets/coin.png").convert_alpha()
    screen.blit(coin_icon, (10, 222))
    coins_text = font.render(f"x {player.coins}", True, (255, 255, 0))
    screen.blit(coins_text, (40, 220))

    screen.blit(ammo_text, (10, 10))
    screen.blit(armor_text, (10, 70))
    screen.blit(time_text, (10, 130))
    screen.blit(kills_text, (10, 160))
    screen.blit(enemies_text, (10, 190))

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
            pygame.draw.circle(screen, (255, 0, 0), (mx, my), 2)

    if not player.alive:
        go = pygame.font.SysFont(None, 72)
        text = go.render("GAME OVER", True, (255, 0, 0))
        screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 - 36))
        pygame.display.flip()
        pygame.time.delay(3000)
        game_paused = True
        pygame.mouse.set_visible(True)

    pygame.display.update()

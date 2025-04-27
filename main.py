import pygame
import sys
import random

from settings import WIDTH, HEIGHT, FPS
from player import Player
from enemy import Enemy
from bullet import Bullet
from pickup import AmmoPickup

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)  # Скрыть стандартный курсор
start_time = pygame.time.get_ticks()
kills = 0

# Создание прицела автоматически
crosshair_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.circle(crosshair_surface, (255, 0, 0), (20, 20), 15, 2)
pygame.draw.line(crosshair_surface, (255, 0, 0), (20, 0), (20, 40), 2)
pygame.draw.line(crosshair_surface, (255, 0, 0), (0, 20), (40, 20), 2)

# Спрайт-группы
player = Player((WIDTH // 2, HEIGHT // 2))
player_group = pygame.sprite.GroupSingle(player)
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
pickups = pygame.sprite.Group()

SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 2000)  # Каждые две секунды спавн врагов

# Главный цикл игры
while True:
    dt = clock.tick(FPS)
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    # События
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == SPAWN_EVENT:
            enemies.add(Enemy(player.rect.center))
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and player.shoot():
                bullets.add(Bullet(player.rect.center, mouse_pos))

    # Обновление
    player_group.update(keys, mouse_pos)
    player.draw_reload_indicator(screen)

    bullets.update()
    enemies.update(player.rect)

    # Столкновения пуль и врагов
    for bullet in bullets:
        hit_list = pygame.sprite.spritecollide(bullet, enemies, False)
        for enemy in hit_list:
            enemy.health -= 25
            bullet.kill()
            if enemy.health <= 0:
                pickups.add(AmmoPickup(enemy.rect.center))
                enemy.kill()
                kills += 1

    # Столкновения игрока и врагов
    if pygame.sprite.spritecollide(player, enemies, False):
        player.health -= 1
        if player.health <= 0:
            print("Game Over")
            pygame.quit()
            sys.exit()

    # Подбор патронов
    pickup_hits = pygame.sprite.spritecollide(player, pickups, True)
    for pickup in pickup_hits:
        player.ammo += 5

    # Рендер
    screen.fill((30, 30, 30))
    player_group.draw(screen)
    bullets.draw(screen)
    enemies.draw(screen)
    pickups.draw(screen)
    screen.blit(crosshair_surface, (mouse_pos[0] - crosshair_surface.get_width() // 2,
                                    mouse_pos[1] - crosshair_surface.get_height() // 2))

    # Отображение информации
    font = pygame.font.SysFont(None, 30)
    ammo_text = font.render(f"Ammo: {player.ammo}", True, (255, 255, 255))
    health_text = font.render(f"Health: {player.health}", True, (255, 0, 0))
    screen.blit(ammo_text, (10, 10))
    screen.blit(health_text, (10, 40))

    # Таймер
    current_time = (pygame.time.get_ticks() - start_time) // 1000
    font = pygame.font.Font(None, 30)
    time_text = font.render(f"Survived: {current_time}s", True, (255, 255, 255))
    screen.blit(time_text, (10, 70))

    # Отображение количества врагов
    enemies_text = font.render(f"Enemies: {len(enemies)}", True, (255, 255, 255))
    screen.blit(enemies_text, (10, 130))

    # Счётчик убийств
    kills_text = font.render(f"Kills: {kills}", True, (255, 255, 255))
    screen.blit(kills_text, (10, 100))

    # Мини-карта
    mini_map_rect = pygame.Rect(WIDTH - 110, 10, 100, 100)
    pygame.draw.rect(screen, (50, 50, 50), mini_map_rect)

    # Игрок на мини-карте
    player_pos_on_map = (mini_map_rect.x + player.rect.centerx * 100 // WIDTH,
                         mini_map_rect.y + player.rect.centery * 100 // HEIGHT)
    pygame.draw.circle(screen, (0, 255, 0), player_pos_on_map, 3)

    # Враги на мини-карте
    for enemy in enemies:
        enemy_pos_on_map = (mini_map_rect.x + enemy.rect.centerx * 100 // WIDTH,
                            mini_map_rect.y + enemy.rect.centery * 100 // HEIGHT)
        pygame.draw.circle(screen, (255, 0, 0), enemy_pos_on_map, 2)

    camera_offset = pygame.math.Vector2(player.rect.centerx - WIDTH // 2,
                                        player.rect.centery - HEIGHT // 2)

    pygame.display.update()

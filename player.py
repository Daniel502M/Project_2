import pygame
from animations import load_animations
from astar import astar
from animations import load_attack_animation


class Player:
    def __init__(self, x, y, width, height, map_width, map_height):
        self.x = x  # координата X персонажа на карте (левый верхний угол хитбокса).
        self.y = y  # координата Y персонажа на карте.
        self.width = width  # ширина хитбокса персонажа.
        self.height = height  # высота хитбокса персонажа.
        self.map_width = map_width  # ширина карты (граница, за которую нельзя выйти).
        self.map_height = map_height  # высота карты.
        self.speed = 3  # Скорость передвижения
        self.attack_animation_speed = 4  # Количество кадров в секунду для анимации атаки
        self.animation_count = 0
        self.direction = "down"  # Начальное направление
        self.last_direction = "down"  # Запоминаем последнее направление
        self.is_moving = False
        self.target_x = x  # желаемая координата X, куда должен переместиться персонаж.
        self.target_y = y  # желаемая координата Y, куда должен переместиться персонаж.
        self.move_directions = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
            "up_left": (-1, -1),
            "up_right": (1, -1),
            "down_left": (-1, 1),
            "down_right": (1, 1)
        }
        # Добавляем hitbox
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.is_attacking = False  # Добавляем атрибут is_attacking
        animations = load_animations() # Загружаем анимации
        self.animations = {
            "up_left": animations["upper_left"],
            "up_right": animations["upper_right"],
            "down_left": animations["lower_left"],
            "down_right": animations["lower_right"],
            "up": animations["up"],
            "down": animations["down"],
            "left": animations["left"],
            "right": animations["right"]
        }
        self.attack_animation = {  # <-- Перенесли сюда!
            "up": load_attack_animation("up"),
            "down": load_attack_animation("down"),
            "left": load_attack_animation("left"),
            "right": load_attack_animation("right")
        }
        self.attack_animation_count = 0
        self.path = []
        self.target_index = 0
        self.attack_animation_index = 0  # Индекс текущего кадра атаки

    def handle_input(self):
        try:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0  # Изменения координат

            if keys[pygame.K_w]:
                dy -= 1
                self.last_direction = "up"
            if keys[pygame.K_s]:
                dy += 1
                self.last_direction = "down"
            if keys[pygame.K_a]:
                dx -= 1
                self.last_direction = "left"
            if keys[pygame.K_d]:
                dx += 1
                self.last_direction = "right"

            # Обновляем анимацию
            if self.is_moving:
                self.animation_count = (self.animation_count + 1) % 24
        except Exception as e:
            print(f"Ошибка при обработке ввода: {e}")

    def get_direction(self, dx, dy):
        try:
            if dx == 0 and dy < 0:
                self.last_direction = "up"
                return "up"
            elif dx == 0 and dy > 0:
                self.last_direction = "down"
                return "down"
            elif dx < 0 and dy == 0:
                self.last_direction = "left"
                return "left"
            elif dx > 0 and dy == 0:
                self.last_direction = "right"
                return "right"
            elif dx < 0 and dy < 0:
                self.last_direction = "up_left"
                return "up_left"
            elif dx > 0 > dy:
                self.last_direction = "up_right"
                return "up_right"
            elif dx < 0 < dy:
                self.last_direction = "down_left"
                return "down_left"
            elif dx > 0 and dy > 0:
                self.last_direction = "down_right"
                return "down_right"
        except Exception as e:
            print(f"Ошибка при определении направления: {e}")
            return None

    def move(self):
        try:
            if not self.is_moving or self.is_attacking:  # Не двигаться во время атаки
                return
        except Exception as e:
            print(f"Произошла ошибка при перемещении персонажа: {e}")

    def handle_mouse_click(self, event, camera, obstacle_map):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            target_x = mouse_x + camera.offset_x - self.width // 2
            target_y = mouse_y + camera.offset_y - self.height

            start = (self.x // 16, self.y // 16)
            goal = (target_x // 16, target_y // 16)
            path = astar(start, goal, obstacle_map)

            if path:
                self.path = path
                self.target_index = 0
                self.is_moving = True

    def draw(self, display, camera):
        try:
            if self.is_moving:
                self.animation_count = (self.animation_count + 1) % 24
                current_frame = self.animations[self.direction][self.animation_count // 4]
            else:
                current_frame = self.animations[self.last_direction][0]

            screen_x = self.x - camera.offset_x
            screen_y = self.y - camera.offset_y

            display.blit(pygame.transform.scale(current_frame, (48, 63)), (screen_x, screen_y))

            # Рисуем хитбокс игрока красным
            pygame.draw.rect(display, (255, 0, 0), (screen_x + 18, screen_y + 44, self.width - 20, self.height - 36), 1)
        except Exception as e:
            print(f"Произошла ошибка при отриске: {e}")
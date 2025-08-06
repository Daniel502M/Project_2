import pygame
import pytmx
from map_config import map_configs


class TileMap:
    def __init__(self, filename):
        self.filename = filename
        self.tmx_data = pytmx.load_pygame(filename, pixelalpha=True)
        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight
        self.width = self.tmx_data.width * self.tile_width
        self.height = self.tmx_data.height * self.tile_height

        self.config = map_configs.get(filename)
        if self.config is None:
            raise ValueError(f"[❌] Нет конфигурации карты для {filename}")

    def draw(self, surface, offset=pygame.Vector2(0, 0), skip_door_ids=None, show_tile_ids=False, allowed_gids=None):
        """Отрисовывает карту. Если указан skip_door_ids — не рисует двери с этими id.
        При show_tile_ids=True отображает ID каждого тайла поверх него (для отладки).
        Если указан allowed_gids — отображаются только указанные GID."""
        if skip_door_ids is None:
            skip_door_ids = set()

        door_gids = self.config.get("door_gids", {}).keys()
        font = pygame.font.Font(None, 32) if show_tile_ids else None

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid == 0:
                        continue

                    # Пропускаем только указанные двери
                    door_id = f"{x}_{y}"
                    if gid in door_gids:
                        if door_id in skip_door_ids:
                            continue

                    # Основная отрисовка всех объектов
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        pos_x = x * self.tile_width - offset.x
                        pos_y = y * self.tile_height - offset.y
                        surface.blit(tile, (pos_x, pos_y))

                    # Отображение ID тайлов при необходимости
                    if show_tile_ids and font:
                        if allowed_gids is None or gid in allowed_gids:
                            text = font.render(str(gid), True, (255, 0, 0))
                            surface.blit(text, (pos_x + 10, pos_y + 10))

    def get_collision_rects(self, layer_name="Стены"):
        walls = []
        doors = []

        # 🚫 GID, через которые можно проходить (не будут добавляться в коллизии)
        non_collidable_gids = {109, 110, 111, 112, 113, 114, 115, 116}

        door_gids = self.config.get("door_gids", {}).keys()
        processed_doors = set()

        layer = self.tmx_data.get_layer_by_name(layer_name)
        open_gids = self.config.get("open_gids", {})
        wall_hitboxes = self.config.get("wall_hitboxes", {})

        for x, y, gid in layer:
            if gid == 0 or gid in non_collidable_gids:
                continue

            tile_x = x * self.tile_width
            tile_y = y * self.tile_height
            w, h = self.tile_width, self.tile_height

            # Обработка только дверей
            if gid in door_gids:
                door_id = f"{x}_{y}"
                if door_id in processed_doors:
                    continue
                processed_doors.add(door_id)

                # Создание хитбокса для двери
                door_type = self.config["door_gids"][gid][0]
                if door_type == "top":
                    rect = pygame.Rect(tile_x, tile_y, w, 13)
                elif door_type == "bottom":
                    rect = pygame.Rect(tile_x, tile_y + h - 13, w, 13)
                elif door_type == "right":
                    rect = pygame.Rect(tile_x + w - 13, tile_y, 13, h)
                elif door_type == "left":
                    rect = pygame.Rect(tile_x, tile_y, 13, h)

                doors.append({
                    "id": door_id,
                    "rect": rect,
                    "pos": (x, y),
                    "gid": gid,
                    "open_gid": open_gids.get(gid, gid),
                    "is_open": False
                })
                continue

            # Обработка стен и других объектов
            if gid in wall_hitboxes:
                for ox, oy, ww, hh in wall_hitboxes[gid]:
                    walls.append(pygame.Rect(
                        tile_x + ox,
                        tile_y + oy,
                        ww,
                        hh
                    ))
            else:
                walls.append(pygame.Rect(tile_x, tile_y, w, h))

        return walls, doors

    def get_closed_door_image(self, door):
        """Возвращает изображение закрытой двери по GID."""
        return self.tmx_data.get_tile_image_by_gid(door["gid"])

    def get_object_collision_rects(self, layer_name="Объекты"):
        """Возвращает коллизии объектов и прямоугольники, блокирующие пули."""
        object_rects = []
        bullet_blocking_rects = []

        non_collidable_gids = {109, 110, 111, 112, 113, 114, 115, 116}
        bullet_passable_gids = self.config.get("bullet_passable_gids", set())
        gid_hitboxes = self.config.get("gid_hitboxes", {})

        try:
            layer = self.tmx_data.get_layer_by_name(layer_name)
        except Exception as e:
            print(f"[❌] Ошибка: слой '{layer_name}' не найден — {e}")
            return [], []

        if not isinstance(layer, pytmx.TiledTileLayer):
            print(f"[❌] Слой '{layer_name}' не является тайловым слоем!")
            return [], []

        for x, y, gid in layer:
            if gid == 0 or gid in non_collidable_gids:
                continue

            tile_x = x * self.tile_width
            tile_y = y * self.tile_height

            if gid in gid_hitboxes:
                w, h, ox, oy = gid_hitboxes[gid]
                rect = pygame.Rect(tile_x + ox, tile_y + self.tile_height - h + oy, w, h)
            else:
                rect = pygame.Rect(tile_x, tile_y, self.tile_width, self.tile_height)

            object_rects.append(rect)
            if gid not in bullet_passable_gids:
                bullet_blocking_rects.append(rect)

        return object_rects, bullet_blocking_rects

    def print_unique_gids(self):
        unique_gids = set()

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for _, _, gid in layer:
                    if gid != 0:
                        unique_gids.add(gid)

        print("[📦] Уникальные GID на карте:")
        for gid in sorted(unique_gids):
            print(f"GID: {gid}")

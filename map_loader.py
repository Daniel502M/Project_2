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

        self.object_offsets = self.config.get("object_offsets", {})  # смещения по координатам
        self.gid_offsets = self.config.get("gid_offsets", {})        # смещения по GID

    def draw(self, surface, offset=pygame.Vector2(0, 0), skip_door_ids=None, show_tile_ids=False, allowed_gids=None):
        if skip_door_ids is None:
            skip_door_ids = set()

        door_gids = self.config.get("door_gids", {}).keys()
        font = pygame.font.Font(None, 32) if show_tile_ids else None

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid == 0:
                        continue

                    door_id = f"{x}_{y}"
                    if gid in door_gids and door_id in skip_door_ids:
                        continue

                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        # Смещение по координатам и GID
                        ox1, oy1 = self.object_offsets.get((x, y), (0, 0))
                        ox2, oy2 = self.gid_offsets.get(gid, (0, 0))
                        pos_x = x * self.tile_width + ox1 + ox2 - offset.x
                        pos_y = y * self.tile_height + oy1 + oy2 - offset.y
                        surface.blit(tile, (pos_x, pos_y))

                        if show_tile_ids and font:
                            if allowed_gids is None or gid in allowed_gids:
                                text = font.render(str(gid), True, (255, 0, 0))
                                surface.blit(text, (pos_x + 10, pos_y + 10))

    def get_collision_rects(self, layer_name="Стены"):
        walls = []
        doors = []

        ignored_gids = self.config.get("ignored_collision_gids", set())
        door_gids = self.config.get("door_gids", {}).keys()
        processed_doors = set()

        layer = self.tmx_data.get_layer_by_name(layer_name)
        open_gids = self.config.get("open_gids", {})
        wall_hitboxes = self.config.get("wall_hitboxes", {})

        for x, y, gid in layer:
            if gid == 0 or gid in ignored_gids:
                continue

            ox1, oy1 = self.object_offsets.get((x, y), (0, 0))
            ox2, oy2 = self.gid_offsets.get(gid, (0, 0))
            tile_x = x * self.tile_width + ox1 + ox2
            tile_y = y * self.tile_height + oy1 + oy2
            w, h = self.tile_width, self.tile_height

            if gid in door_gids:
                door_id = f"{x}_{y}"
                if door_id in processed_doors:
                    continue
                processed_doors.add(door_id)

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

            if gid in wall_hitboxes:
                for ox, oy, ww, hh in wall_hitboxes[gid]:
                    walls.append(pygame.Rect(tile_x + ox, tile_y + oy, ww, hh))
            else:
                walls.append(pygame.Rect(tile_x, tile_y, w, h))

        return walls, doors

    def get_closed_door_image(self, door):
        return self.tmx_data.get_tile_image_by_gid(door["gid"])

    def get_object_collision_rects(self, layer_name="Объекты"):
        object_rects = []
        bullet_blocking_rects = []

        ignored_gids = self.config.get("ignored_collision_gids", set())
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
            if gid == 0 or gid in ignored_gids:
                continue

            ox1, oy1 = self.object_offsets.get((x, y), (0, 0))
            ox2, oy2 = self.gid_offsets.get(gid, (0, 0))
            tile_x = x * self.tile_width + ox1 + ox2
            tile_y = y * self.tile_height + oy1 + oy2

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

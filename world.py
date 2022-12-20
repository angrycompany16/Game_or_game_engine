import pygame
import Assets.LDtk.LdtkJson as LdtkJson
import json
import level
import player
import utils
import game_manager
import renderer

PIXEL_SCALE_FACTOR = 4

# Contains player and everything that is done throughout the whole game
class World():
    def __init__(self, path, game_surf, camera) -> None:
        with open(path, "r") as read_file:
            self.world = LdtkJson.ldtk_json_from_dict(json.load(read_file))

        self.levels = []
        self.game_surf = game_surf
        self.cam_scroll = pygame.Vector2(0)

        # Camera settings
        self.dead_zone_x = camera["dead_zone_x"]
        self.dead_zone_y = camera["dead_zone_y"]
        self.cam_smooth = camera["smooth_factor"]
        self.cam_size = camera["size"]

        self.setup_game()

    def setup_game(self):
        for level_instance in self.world.levels:
            self.levels.append(level.Level(
                level_instance.layer_instances, 
                game_manager.convert_ldtk_path(level_instance.get_field("Tileset_img")), 
                level_instance.px_wid, 
                level_instance.px_hei,
                level_instance.get_field("shadow_color"), 
                _fps=level_instance.get_field("FPS")
            ))
        
        self.current_level = self.levels[3]

        
        spawn_pos = self.current_level.get_spawn_pos()

        self.player = player.Player(game_manager.player_character, pygame.Vector2(spawn_pos), game_manager.player_anim, self.game_surf)
        self.player.enemies = self.current_level.enemies
        game_manager.shadow_color = self.current_level.shadow_color

    def update(self):
        self.game_surf.fill((0, 0, 0), pygame.Rect((0, 0), self.game_surf.get_size()))
        
        self.player.update_player(self.current_level.tile_rects, self.current_level.ramps)
        
        exited, player_exit_data = self.player.check_exits(self.current_level.exits)

        if exited:
            self.switch_level(player_exit_data)

        self.current_level.update_lvl(renderer.layers)

        self.player.draw(renderer.layers["playerspace"])

        renderer.add_drop_shadow("UI", (1, 1), [31, 14, 28])

        self.game_surf = renderer.render_all()

        self.control_camera()
        # Magic 

    def switch_level(self, player_exit_data):
        self.current_level = self.levels[player_exit_data[1]]
        spawn_pos = pygame.Vector2(self.current_level.find_entrace(player_exit_data[2])[0])
        spawn_pos.y += 7
        self.player.position = spawn_pos
        self.player.rect.topleft = spawn_pos
        
        self.cam_scroll = pygame.Vector2(
            (spawn_pos.x - self.cam_size[0] / 2, spawn_pos.y - self.cam_size[1] / 2))

        self.player.enemies = self.current_level.enemies
        self.player.shadow_color = self.current_level.shadow_color

    def control_camera(self):
        player_pos = pygame.Vector2(self.player.rect.x - 232, self.player.rect.y - 119)

        # Set camera x scroll (uses dead zone and smoothness)
        if player_pos.x - self.cam_scroll.x > self.dead_zone_x:
            self.cam_scroll.x += (player_pos.x - self.cam_scroll.x - self.dead_zone_x) * self.cam_smooth
        elif player_pos.x - self.cam_scroll.x < -self.dead_zone_x:
            self.cam_scroll.x += (player_pos.x - self.cam_scroll.x + self.dead_zone_x) * self.cam_smooth

        # Set camera y scroll (uses dead zone and smoothness)
        if player_pos.y - self.cam_scroll.y > self.dead_zone_y:
            self.cam_scroll.y += (player_pos.y - self.cam_scroll.y - self.dead_zone_y) * self.cam_smooth
        elif player_pos.y - self.cam_scroll.y < -self.dead_zone_y:
            self.cam_scroll.y += (player_pos.y - self.cam_scroll.y + self.dead_zone_y) * self.cam_smooth
        
        self.cam_scroll.x = utils.clamp(self.cam_scroll.x, 0, self.current_level.width - self.game_surf.get_width())
        self.cam_scroll.y = utils.clamp(self.cam_scroll.y, 0, self.current_level.height - self.game_surf.get_height())

        game_manager.cam_scroll = self.cam_scroll

    def set_level(self, id):
        pass

    def transform(self):
        size = self.game_surf.get_size()

        scaled_surf = pygame.transform.scale(self.game_surf, (size[0] * PIXEL_SCALE_FACTOR, size[1] * PIXEL_SCALE_FACTOR))

        return scaled_surf, scaled_surf.get_rect()

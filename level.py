
from ast import literal_eval
import pygame
import game_manager
import animations
import particle_system
import combat_system
import renderer

# TODO - lights with additive blending sprites
# TODO - UI elements
# TODO - parallax outside of pixel perfect rendering

# Contains level-specific stuff
class Level:
    def __init__(self, layer_instances, tileset, width, height, shadow_color, _fps=12) -> None:
        self.layer_instances = layer_instances
        self.tiles = []
        self.tile_rects = []
        self.ramps = []
        self.background_images = []
        self.exits = []
        self.entrances = []
        self.lvl_particle_systems = []

        self.enemies = [
            # combat_system.Enemy(
            #     pygame.Rect(0, 0, 20, 20), combat_system.PatrolMovementController(pygame.Vector2(200, 100), pygame.Vector2(20, 0), pygame.Vector2(20, 0)), combat_system.Damageable(4, 1), combat_system.EnemySpriteRenderer(global_stuff.enemy_test, renderer.layers["UI"])
            # )
        ]

        self.tileset = pygame.image.load(tileset)
        self.anim = animations.Animator([
            animations.AnimationClip(self.tileset, 256, 256, fps=_fps)
        ])
        self.shadow_color = shadow_color
        self.tile_size = 0
        self.cam_scroll = pygame.Vector2(0, 0)
        self.width = width
        self.height = height if height != 272 else 270

        self.animations = []

        # TODO - rewrite with more list comprehensions
        # Parse all the LDtk layers...
        for layer in self.layer_instances:
            if layer.identifier == "Playerspace":
                self.tile_size = (layer.grid_size, layer.grid_size)
                if layer.type == "IntGrid":
                    self.tiles = layer.auto_layer_tiles
                elif layer.type == "Tiles":
                    self.tiles = layer.grid_tiles
                    if game_manager.DEV_MODE:
                        self.tile_rects = [pygame.Rect(tile.px, (layer.grid_size, layer.grid_size)) for tile in layer.grid_tiles]

            elif layer.identifier == "Colliders":
                if not game_manager.DEV_MODE:
                    self.tile_rects = [pygame.Rect(collider.px, (collider.width, collider.height)) for collider in layer.entity_instances]

            elif layer.identifier == "Ramps":
                for collider in layer.entity_instances:
                    ramp = (
                        pygame.Rect(collider.px, (collider.width, collider.height)),
                        collider.get_field("Ramp_direction")
                    )

                    self.ramps.append(ramp)
            elif layer.identifier == "Images":
                for entity in layer.entity_instances:
                    # Creates the correct path to the image file
                    path = game_manager.convert_ldtk_path(entity.get_field("Path"))

                    self.background_images.append([
                        pygame.image.load(path).convert_alpha(), 
                        entity.get_field("Layer").lower(), 
                        entity.get_field("ParallaxValue")
                    ])
            elif layer.identifier == "Exits":
                for exit in layer.entity_instances:
                    self.exits.append((pygame.Rect(exit.px, (exit.width, exit.height)), exit.get_field("Level_ID"), exit.get_field("Entrance_ID")))
            elif layer.identifier == "Entrances":
                for entrance in layer.entity_instances:
                    self.entrances.append((entrance.px, entrance.get_field("ID")))
            elif layer.identifier == "Particle_systems":
                for particle_sys in layer.entity_instances:
                    self.lvl_particle_systems.append(game_manager.level_particle_systems[particle_sys.get_field("name")])

    def update_lvl(self, renderer_layers):
        self.tileset = self.anim.update()
        self.cam_scroll = game_manager.cam_scroll

        for layer in self.layer_instances:
            for render_layer in renderer_layers:
                if layer.identifier.lower() == render_layer.lower():
                    for tile in layer.grid_tiles:
                        renderer_layers[render_layer].blit(self.tileset, tile.px - self.cam_scroll, pygame.Rect(tile.src, self.tile_size))

        for enemy in self.enemies:
            enemy.update()

        for image in self.background_images:
            renderer_layers[image[1]].blit(image[0], -self.cam_scroll * image[2])

        for particle_sys in self.lvl_particle_systems:
            particle_sys.update()
        
    def get_spawn_pos(self):
        for layer in self.layer_instances:
            if layer.identifier == "Entrances":
                self.spawn_pos = [entity.px for entity in layer.entity_instances if entity.get_field("ID") == 0]
                return self.spawn_pos[0]

    def find_entrace(self, ID):
        for entrance in self.entrances:
            if entrance[1] == ID:
                return entrance
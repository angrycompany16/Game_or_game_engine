from copy import copy
import pygame

GAME_WIDTH, GAME_HEIGHT = 480, 270

layers = {
    "background3": pygame.Surface((GAME_WIDTH, GAME_HEIGHT), flags=pygame.SRCALPHA), 
    "background2": pygame.Surface((GAME_WIDTH, GAME_HEIGHT), flags=pygame.SRCALPHA), 
    "background1": pygame.Surface((GAME_WIDTH, GAME_HEIGHT), flags=pygame.SRCALPHA), 
    "midground": pygame.Surface((GAME_WIDTH, GAME_HEIGHT), flags=pygame.SRCALPHA), 
    "playerspace": pygame.Surface((GAME_WIDTH, GAME_HEIGHT), flags=pygame.SRCALPHA), 
    "foreground": pygame.Surface((GAME_WIDTH, GAME_HEIGHT), flags=pygame.SRCALPHA),
    "UI": pygame.Surface((GAME_WIDTH, GAME_HEIGHT), flags=pygame.SRCALPHA)
}

filters = {}

def add_drop_shadow(layer, shift, shadow_color):
    if type(layer) == str:
        layer_ = copy(layers[layer])
        shadow_mask = pygame.mask.from_surface(layers[layer])
        surface_converted = shadow_mask.to_surface()
        surface_converted.set_colorkey((0, 0, 0))

        surface_converted = surface_converted.convert_alpha()

        surface_converted.fill((255 - shadow_color[0], 255 - shadow_color[1], 255 - shadow_color[2], 0), special_flags=pygame.BLEND_RGBA_SUB)

        layers[layer].blit(surface_converted, shift)
        layers[layer].blit(layer_, (0, 0))
    elif type(layer) == pygame.Surface:
        layer_ = copy(layer)
        shadow_mask = pygame.mask.from_surface(layer)
        surface_converted = shadow_mask.to_surface()
        surface_converted.set_colorkey((0, 0, 0))

        surface_converted = surface_converted.convert_alpha()

        surface_converted.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_SUB)
        surface_converted.fill((shadow_color[0], shadow_color[1], shadow_color[2], 0), special_flags=pygame.BLEND_RGBA_ADD)

        layer.blit(surface_converted, shift)
        layer.blit(layer_, (0, 0))

def render_all() -> pygame.Surface:
    temporary_surf = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), flags=pygame.SRCALPHA)

    for layer in layers.values():
        temporary_surf.blit(layer.convert_alpha(), (0, 0))
        layer.fill(pygame.Color(0, 0, 0, 0))

    for filter in filters.values():
        temporary_surf.blit(filter[0].convert_alpha(), (0, 0), special_flags=filter[1])


    return temporary_surf
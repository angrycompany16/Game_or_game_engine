from Assets.LDtk.LdtkJson import LayerDefinition
import game_manager
import pygame

class Damageable():
    def __init__(self, max_health, attack_damage) -> None:
        self.max_health = max_health
        self.health = max_health
        self.events = []
        self.attack_damage = attack_damage

    def take_damage(self, damage):
        self.health -= damage
        self.events.append(("DAMAGE_TAKEN", damage))

        if self.health <= 0:
            self.die()

    def die(self):
        self.events.append(["DEATH"])

    def deal_damage(self, target):
        target.take_damage(self.attack_damage)

    def get_events(self):
        events_copy = []
        for event in self.events:
            events_copy.append(event)
            self.events.pop(0)

        return events_copy

"""
    What varies from enemy to enemy?
     - Hitbox
     - Sprite / animations
     - THe way it moves
     - How much damage it deals / how much HP it has
     - The loot it drops
"""

class Enemy():
    def __init__(self, rect, movement_controller, damageable, enemy_renderer) -> None:
        self.rect = rect
        self.movement_controller = movement_controller
        self.damageable = damageable
        self.enemy_renderer = enemy_renderer

    def update(self):
        self.rect.topleft = self.movement_controller.update()
        self.enemy_renderer.render(self.rect)

class PatrolMovementController():
    def __init__(self, start_pos: pygame.Vector2, move_speed: pygame.Vector2, turn_point: pygame.Vector2) -> None:
        self.position = start_pos
        self.move_speed = move_speed
        self.turn_point = turn_point

    # Apply movement
    def update(self):
        self.position += self.move_speed * game_manager.dt
        return self.position

class EnemySpriteRenderer():
    def __init__(self, image, layer) -> None:
        self.image = image
        self.layer = layer
        self.cam_scroll = pygame.Vector2(0, 0)

    def render(self, rect):
        self.cam_scroll = game_manager.cam_scroll
        self.layer.blit(self.image, (rect.left - self.cam_scroll.x, rect.top - self.cam_scroll.y))
import math
import pygame

class vfx():
    def __init__(self) -> None:
        pass

class PlayerAttackVfx(vfx):
    def __init__(self) -> None:
        super().__init__()
        self.radius = 10
        self.triangle_angle = 30 * math.pi / 180
        self.triangle_size = 14
        self.surf = pygame.Surface((100, 100)).convert_alpha()
        self.center = (self.surf.get_width() / 2, self.surf.get_height() / 2)

    def update(self, angle):
        self.surf.fill(pygame.Color(0, 0, 0, 0))
        pygame.draw.circle(self.surf, pygame.Color(255, 255, 255), self.center, self.radius)

        triangle_points = (
            (self.radius * math.cos(angle - self.triangle_angle) + self.center[0], self.radius * math.sin(angle - self.triangle_angle) + self.center[1]),
            (self.radius * math.cos(angle + self.triangle_angle) + self.center[0], self.radius * math.sin(angle + self.triangle_angle) + self.center[1]),
            ((self.radius + self.triangle_size) * math.cos(angle) + self.center[0], (self.radius + self.triangle_size) * math.sin(angle) + self.center[1]),
        )
        pygame.draw.polygon(self.surf, pygame.Color(255, 255, 255), triangle_points)



from math import floor
import pygame
import random
import utils
import game_manager
import perlin_noise

# What we want:
# - Add noise
# - Movement damping (make particles stop after some time)
# - Add special velocity, acceleration and rotation
# - Basic collision physics
# - Add transparency to particle color (should be easy?)

# - Choose sprite or polygon (maybe?)
class ParticleSystem():
    def __init__(self, self_pos=pygame.Vector2(0, 0 ), start_pos=pygame.Vector2(0, 0), start_vel=pygame.Vector2(5, 5), acceleration=pygame.Vector2(0, 10), image=None, spawn_rate=1, lifetime=1, start_scale=1, start_rotation=1, start_color=pygame.Color(255, 255, 255), end_color=pygame.Color(255, 255, 255), scale_time_factor=0, rotation_time_factor=0, noise_factor=1, noise_scale=1, rendering_layer=None, direction=pygame.Vector2(1, 1), activate_on_start=False) -> None:
        self.self_pos = self_pos
        self.direction = direction
        self.particles = []
        self.emitting = activate_on_start
        
        self.start_pos = start_pos
        self.start_vel = start_vel
        self.acceleration = acceleration
        self.image = image
        self.spawn_rate = spawn_rate
        self.lifetime = lifetime
        self.rendering_layer = rendering_layer
        self.noise_factor = noise_factor
        self.noise_scale = noise_scale

        self.start_scale = start_scale
        self.scale_time_factor = scale_time_factor
        self.start_rotation = start_rotation
        self.rotation_time_factor = rotation_time_factor
        self.start_color = start_color
        self.end_color = end_color

        self.noise_map = perlin_noise.PerlinNoise(random.randint(1, 1000))

        self.t = 0

    def update(self):
        if self.emitting:
            dt = game_manager.dt
            self.t += dt

            particles_to_spawn = floor(self.t / (1 / self.spawn_rate))
            if self.t > 1 / self.spawn_rate:
                for i in range(particles_to_spawn):
                    new_particle = Particle(
                        self.start_pos.val + self.self_pos, 
                        pygame.Vector2(self.start_vel.val.x * self.direction.x, self.start_vel.val.y * self.direction.y), 
                        pygame.Vector2(self.acceleration.val.x * self.direction.x, self.acceleration.val.y * self.direction.y), 
                        self.image,
                        self.lifetime.val,
                        self.start_scale.val,
                        self.start_rotation.val,
                        self.start_color.val,
                        self.end_color.val,
                        self.scale_time_factor.val,
                        self.rotation_time_factor.val,
                        self.rendering_layer,
                        self.noise_factor,
                        self.noise_scale,
                        self.noise_map,
                    )
                    self.particles.append(new_particle)

                self.t = 0

        for index, particle in sorted(enumerate(self.particles), reverse=True):
            will_die = particle.update()
            if will_die:
                self.particles.pop(index)
            else:
                particle.draw()

    def burst(self, count):
        for _ in range(count):
            new_particle = Particle(
                self.start_pos.val + self.self_pos, 
                pygame.Vector2(self.start_vel.val.x * self.direction.x, self.start_vel.val.y * self.direction.y), 
                pygame.Vector2(self.acceleration.val.x * self.direction.x, self.acceleration.val.y * self.direction.y), 
                self.image,
                self.lifetime.val,
                self.start_scale.val,
                self.start_rotation.val,
                self.start_color.val,
                self.end_color.val,
                self.scale_time_factor.val,
                self.rotation_time_factor.val,
                self.rendering_layer,
                self.noise_factor,
                self.noise_scale,
                self.noise_map,
            )
            self.particles.append(new_particle)

class Particle():
    def __init__(self, start_pos, start_vel, acceleration, image, lifetime, start_scale, start_rotation, start_color, end_color, scale_time_factor, rotation_time_factor, rendering_layer, noise_factor, noise_scale, noise_map) -> None:
        self.position = start_pos
        self.velocity = start_vel
        self.acceleration = acceleration
        self.image = image.convert_alpha()
        self.image_colored = image.convert_alpha()
        self.rect = image.get_rect(center = start_pos)
        self.lifetime = lifetime
        self.rendering_layer = rendering_layer

        self.start_scale = start_scale
        self.scale = start_scale
        self.scale_time_factor = scale_time_factor

        self.start_rotation = start_rotation
        self.rotation = start_rotation
        self.rotation_time_factor = rotation_time_factor

        self.start_color = start_color
        self.color = start_color
        self.end_color = end_color

        self.noise_factor = noise_factor
        self.noise_scale = noise_scale

        self.noise_map = noise_map

        self.time = 0
        self.cam_scroll = 0

    def update(self) -> bool:
        dt = game_manager.dt
        self.cam_scroll = game_manager.cam_scroll

        self.rotation += dt * self.rotation_time_factor
        self.scale += dt * self.scale_time_factor

        self.color = utils.lerp_1(self.start_color, self.end_color, self.time / self.lifetime)

        if self.scale < 0:
            return True

        self.time += dt
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
        self.velocity += pygame.Vector2([random.random() - 0.5, random.random() - 0.5]) *  self.noise_factor
# self.noise_map((self.position * self.noise_scale).xy)
        self.rect.topleft = self.position

        self.image_colored = self.image.copy().convert_alpha()

        colored_surf = pygame.Surface(self.image.get_size())
        colored_surf.fill(pygame.Color(self.color))
        self.image_colored.blit(colored_surf, pygame.Rect((0, 0), self.image.get_size()), special_flags=pygame.BLEND_RGBA_MULT)
        
        return self.time > self.lifetime

    def draw(self):
        # rotated_surf, rotated_rect = utils.rotozoom_centered(self.image, self.rotation, self.scale, self.rect.center)
        size = (self.image.get_width() * self.scale, self.image.get_height() * self.scale)

        scaled_surf, scaled_rect = utils.scale_centered(self.image_colored, size, (self.rect.center[0] - self.cam_scroll.x, self.rect.center[1] - self.cam_scroll.y))
        rotated_surf, rotated_rect = utils.rotate_centered(scaled_surf, self.rotation, scaled_rect.center)
        
        self.rendering_layer.blit(rotated_surf, rotated_rect)

class ParticleSystemField():
    def __init__(self, min, max=None) -> None:
        self.min = min
        self.max = max

    def get_val(self):
        if not max: return self.min
        if type(self.min) != type(self.max): raise Exception(f"Type '{type(min)}' of min is not equal to type '{type(max)}' of max")

        if type(self.min) == pygame.Vector2:
            return pygame.Vector2(
                utils.lerp_2(self.min.x, self.max.x, random.random()),
                utils.lerp_2(self.min.y, self.max.y, random.random())
            )
        else:
            return utils.lerp_2(self.min, self.max, random.random())




    def set_val(self, val):
        self.min = val[0]
        self.max = val[1]

    def del_val(self):
        del self._val

    val = property(get_val, set_val, del_val)

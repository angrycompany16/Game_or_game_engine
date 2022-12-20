import utils
import math
import pygame
import game_manager
import renderer
import vfx
import combat_system
import copy
import animations

#region constants
PLAYER_IDLE = "PLAYER_IDLE"
PLAYER_RUN = "PLAYER_RUN"
PLAYER_JUMP = "PLAYER_JUMP"
PLAYER_FALL = "PLAYER_FALL"
PLAYER_SHOOT = "PLAYER_SHOOT"
PLAYER_SHOOT_DOWN = "PLAYER_SHOOT_DOWN"
PLAYER_ATTACK = "PLAYER_ATTACK"
PLAYER_ATTACK_UP = "PLAYER_ATTACK_UP"
GRAVITY_Y = 600
B_W_PALETTE = [(x, x, x) for x in range(256)]
SPRITE_WIDTH, SPRITE_HEIGHT = 12, 25
#endregion

#region colors
# -------- PALETTE COLORS --------
#         [140, 143, 174]
#          [88, 69, 99]
#          [62, 33, 55]
#          [154, 99, 72]
#         [215, 155, 125]
#         [245, 237, 186]
#          [192, 199, 65]
#          [100, 125, 52]
#          [228, 148, 58]
#          [157, 48, 59]
#         [210, 100, 113]
#         [112, 55, 127]
#         [126, 196, 193]
#         [52, 133, 157]
#          [23, 67, 75]
#          [31, 14, 28]
#endregion

class Player:
    def __init__(self, image, pos, animator, game_surf, gravity=pygame.Vector2(0, GRAVITY_Y), velocity=pygame.Vector2(0))  -> None:
        self.game_surf = game_surf
        
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.acceleration = gravity
        self.velocity = velocity
        self.position = pos
        self.facing_right = True
        # For changing the size of the player sprite
        self.blit_offset = pygame.Vector2(0)

        # Jumping variables
        self.is_grounded = False
        self.was_grounded = False
        self.jump_velocity = -300
        self.cancel_jump_vel = 50

        # Percentage of speed that is removed when turning or stopping
        self.move_speed = 135
        self.stop_damping_gr = 0.14
        self.turn_damping_gr = 0.92
        self.stop_damping_air = 0.06
        self.turn_damping_air = 0.94

        # Coyote time and jump buffer
        self.coyote_time = 0.1
        self.coyote_time_counter = 0
        self.jump_buffer = 0.1
        self.jump_buffer_counter = 0

        # Animations
        self.animator = animator

        # Particles
        self.foot_particles = game_manager.foot_particles
        self.jump_particles = game_manager.jump_particles
        self.arc_particles = game_manager.arc_particles
        self.land_particles = game_manager.land_particles
        self.damage_particles = game_manager.damage_particles

        self.particle_systems = [
            self.foot_particles,
            self.jump_particles,
            self.arc_particles,
            self.land_particles,
            self.damage_particles
        ]

        self.cam_scroll = pygame.Vector2(0)

        # Attacking - melee
        self.attacking = False
        self.attack_duration = 0.18
        self.attack_time = 0
        self.attack_up_dir = 0

        # Attacking - ranged
        self.bullets = []
        self.bullet_explosions = []
        self.bullet_speed = 300
        self.shooting = False
        self.fire_rate = 4.8
        self.time_since_fire = 0
        self.bullets_in_mag = 5

        # Damage stats
        self.damageable = combat_system.Damageable(5, 1)

        # Combat
        self.enemies = []

    def update_player(self, collision_rects, collision_ramps):
        # Update physics
        dt = game_manager.dt * game_manager.global_timescale

        self.cam_scroll = game_manager.cam_scroll

        self.get_movement()
        self.process_physics(collision_rects, collision_ramps, dt)

        if self.facing_right and self.velocity.x < 0 or not self.facing_right and self.velocity.x > 0:
            self.flip()

        self.process_animations()
        self.process_particles()
        self.process_sprite()
        self.process_combat(collision_rects)

        self.was_grounded = self.is_grounded

    def process_physics(self, collision_rects, collision_ramps, dt):
        # Update physics
        self.velocity += self.acceleration * dt

        dx = self.velocity.x * dt
        dy = self.velocity.y * dt

        # Create collision rects
        dx_rect = pygame.Rect(self.rect.x + (math.ceil(dx) if dx > 0 else math.floor(dx)), self.rect.y, self.rect.width, self.rect.height)
        dy_rect = pygame.Rect(self.rect.x, self.rect.y + (math.ceil(dy) if dy > 0 else math.floor(dy)), self.rect.width, self.rect.height)

        self.is_grounded = False

        # Check and resolve collisions (tiles)
        for tile in collision_rects:
            if tile.colliderect(dx_rect):
                dx = 0
                self.velocity.x = 0

            if tile.colliderect(dy_rect):
                if self.velocity.y < 0:
                    dy = 0
                    self.velocity.y = self.cancel_jump_vel
                    break
                elif self.velocity.y > 0:
                    dy = tile.top - self.position.y - self.rect.height
                    self.velocity.y = 0
                    self.is_grounded = True
                    break
        
        # Check and resolve collisions (ramps)
        for ramp in collision_ramps:
            if ramp[0].colliderect(dx_rect):
                if ramp[1] == "Topleft":
                    rel_x = dx_rect.topleft[0] - ramp[0].topleft[0]
                    if dx_rect.topright[1] < ramp[0].top + ramp[0].height - rel_x:
                        dx = 0
                        self.velocity.x = 0
                elif ramp[1] == "Topright":
                    rel_x = dx_rect.topright[0] - ramp[0].topleft[0]
                    if dx_rect.topright[1] < ramp[0].top + rel_x:
                        dx = 0
                        self.velocity.x = 0
                elif ramp[1] == "Bottomleft":
                    pass
                elif ramp[1] == "Bottomright":
                    pass

            if ramp[0].colliderect(dy_rect):
                if self.velocity.y < 0:

                    if ramp[1] == "Topleft":
                        rel_x = dx_rect.topleft[0] - ramp[0].topleft[0]
                        if dx_rect.topright[1] < ramp[0].top + ramp[0].height - rel_x:
                            dy = 0
                            self.velocity.y = self.cancel_jump_vel
                    elif ramp[1] == "Topright":
                        rel_x = dx_rect.topright[0] - ramp[0].topleft[0]
                        if dx_rect.topright[1] < ramp[0].top + rel_x:
                            dy = 0
                            self.velocity.y = self.cancel_jump_vel

                elif self.velocity.y > 0:
                    if ramp[1] == "Bottomleft":
                        pass
                    elif ramp[1] == "Bottomright":
                        pass

        # Update position
        self.position += pygame.Vector2(dx, dy)

        self.rect.topleft = self.position.xy

        # Jump buffer and coyote time
        if self.is_grounded:
            self.coyote_time_counter = self.coyote_time
        else:
            self.coyote_time_counter -= dt

        self.jump_buffer_counter -= dt

        if self.jump_buffer_counter > 0 and self.is_grounded:
            self.velocity.y = self.jump_velocity

    def process_animations(self):
        if self.shooting:
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                self.animator.set_state(PLAYER_SHOOT_DOWN)
            else:
                self.animator.set_state(PLAYER_SHOOT)
        elif self.attacking:
            if self.attack_up_dir == 1:
                self.animator.set_state(PLAYER_ATTACK_UP)
            elif self.attack_up_dir == -1:
                pass
                # attack down
            else:
                self.animator.set_state(PLAYER_ATTACK)
        elif self.velocity.y < 0:
            self.animator.set_state(PLAYER_JUMP)
        elif self.velocity.y > 0:
            self.animator.set_state(PLAYER_FALL)
        else:
            if abs(self.velocity.x) > 60:
                self.animator.set_state(PLAYER_RUN) 
            else:
                self.animator.set_state(PLAYER_IDLE) 

    def process_particles(self):
        if abs(self.velocity.x) < 20 or not self.is_grounded:
            self.foot_particles.emitting = False
        else:
            if self.facing_right:
                self.foot_particles.direction.x = 1
            else:
                self.foot_particles.direction.x = -1

            self.foot_particles.emitting = True

        # Playing particle systems when landing and jumping
        if self.was_grounded and not self.is_grounded:
            self.arc_particles.emitting = True
            self.jump_particles.burst(20)
        elif not self.was_grounded and self.is_grounded:
            self.land_particles.burst(40)

        # Stop arc particle system
        if self.velocity.y > -250 and self.arc_particles.emitting:
            self.arc_particles.emitting = False

        for particle_system in self.particle_systems:
            if particle_system:
                particle_system.self_pos = self.rect.midbottom
                particle_system.update()

    def process_sprite(self):
        self.image = self.animator.update()
        self.blit_offset = pygame.Vector2(0)

    def process_combat(self, collisions_environment):
        if self.shooting:
            self.time_since_fire += game_manager.dt
            if self.time_since_fire > 1 / self.fire_rate:
                self.shoot()
                self.time_since_fire = 0

        if self.attacking:
            self.attack_time += game_manager.dt
            if self.attack_time > self.attack_duration:
                self.stop_attack()
                self.attack_time = 0

        for bullet in self.bullets:
            bullet.update(collisions_environment)
            if bullet.time > bullet.lifetime:
                self.bullet_explosions.append(BulletExplosion(
                    animations.Animator((animations.AnimationClip(
                        game_manager.bullet_explode_sheet, 12, 12, looping=False, fps=40),
                    )),
                    0.1,
                    bullet.rect.center
                ))
                self.bullets.remove(bullet)
                continue

            bullet.draw()

        for explosion in self.bullet_explosions:
            explosion.update()
            if explosion.time > explosion.lifetime:
                self.bullet_explosions.remove(explosion)
                continue

            explosion.draw()

        for enemy in self.enemies:
            if enemy.rect.colliderect(self.rect):
                self.damageable.take_damage(enemy.damageable.attack_damage)

        for event in self.damageable.get_events():
            if event[0] == "DAMAGE_TAKEN":
                self.damage_particles.burst(40)
                print("Player took damage")

            if event[0] == "DEATH":
                print("The player has died")

    def get_movement(self):
        # Set velocity based on key input
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            if self.is_grounded:
                self.velocity.x += (-self.move_speed - self.velocity.x) * (1 - self.turn_damping_gr)
            else:
                self.velocity.x += (-self.move_speed - self.velocity.x) * (1 - self.turn_damping_air)
        elif pygame.key.get_pressed()[pygame.K_RIGHT]:
            if self.is_grounded:
                self.velocity.x += (self.move_speed - self.velocity.x) * (1 - self.turn_damping_gr)
            else:
                self.velocity.x += (self.move_speed - self.velocity.x) * (1 - self.turn_damping_air)
        else:
            if self.is_grounded:
                self.velocity.x *= (1 - self.stop_damping_gr)
            else:
                self.velocity.x *= (1 - self.stop_damping_air)

    def jump(self):
        self.jump_buffer_counter = self.jump_buffer

        if self.coyote_time_counter > 0:
            self.velocity.y = self.jump_velocity

    def cancel_jump(self):
        fall_vel = self.cancel_jump_vel * (self.jump_velocity - self.velocity.y + 225) / self.jump_velocity

        if self.is_grounded:
            return
        elif self.velocity.y > fall_vel:
            return
        
        self.velocity.y = fall_vel

    def attack(self, up_dir):
        self.attacking = True
        self.attack_up_dir = up_dir
        # self.velocity.x += 100 if self.facing_right else -100

    def stop_attack(self):
        self.attack_time = 0
        self.attacking = False

    def shoot(self):
        # if self.bullets_in_mag == 0: return

        direction = pygame.Vector2(0, 0)
        image = None
        direction.x = 1 if self.facing_right else -1
        image = game_manager.bullet_r_sprite if self.facing_right else game_manager.bullet_l_sprite

        if pygame.key.get_pressed()[pygame.K_UP]:
            direction = pygame.Vector2(0, -1)
            image = game_manager.bullet_u_sprite
        elif pygame.key.get_pressed()[pygame.K_DOWN] and not self.is_grounded:
            image = game_manager.bullet_d_sprite
            direction = pygame.Vector2(0, 1)

        self.bullets.append(Bullet(
            image,
            pygame.Vector2(self.rect.center) + pygame.Vector2(0, -7),
            direction.normalize() * self.bullet_speed,
            0.3
        ))
        self.bullets_in_mag -= 1

    def flip(self):
        self.facing_right = not self.facing_right

    def draw(self, surf):
        # pygame.draw.rect(surf, pygame.Color(255, 0, 0), pygame.Rect(self.rect.x - self.cam_scroll.x, self.rect.y - self.cam_scroll.y, self.rect.width, self.rect.height), width=1)
        dim = self.image.get_size()

        sprite_surf = pygame.Surface((dim[0], dim[1]), pygame.SRCALPHA)
        sprite_surf.fill((0, 0, 0, 0))
        if self.facing_right:
            sprite_surf.blit(self.image.convert_alpha(), (0, 0))
        else:
            sprite_surf.blit(pygame.transform.flip(self.image.convert_alpha(), True, False), (0, 0))

        # renderer.add_drop_shadow(sprite_surf, (-1, 1), game_manager.shadow_color)

        surf.blit(sprite_surf.convert_alpha(), (
            self.rect.x - dim[0] / 2 + self.rect.width / 2 - self.cam_scroll.x - self.blit_offset.x,
            self.rect.y - dim[1] / 2 + self.rect.height / 2 - self.cam_scroll.y - self.blit_offset.y
        ))

    def check_exits(self, exits):
        for exit in exits:
            if exit[0].colliderect(self.rect):
                # print(exits)
                return True, exit
        return False, None

#region old attack system
    # INIT METHOD
    # # Attacking properties
    # self.attack_timescale = 0.1
    # self.attack_smooth = 0.1
    # self.max_range = 50
    # self.attack_force_x = 1500
    # self.attack_force_y = self.attack_force_x / 1.7778
    # self.attack_duration = .015
    # self.attack_damping = 0.92
    # self.attack_end_speed = 250
    # self.attack_vfx = vfx.PlayerAttackVfx()

    # # Attacking variables
    # self.local_timescale = 1
    # self.attack_end_point = pygame.Vector2(0)
    # self.attack_start_point = pygame.Vector2(0)
    # self.attack_dir = pygame.Vector2(0)
    # self.preparing_attack = False
    # self.attacking = False
    # self.attack_time = 0

    # # Attack UI
    # self.attack_circle_radius = 7
    # self.attack_circle_thickness = 3

    # # Slow down time until it's low
    # def attack_start(self, mouse_pos):
    #     self.attack_start_point = pygame.Vector2(mouse_pos)
    #     self.acceleration.y = 0
    #     self.preparing_attack = True

    # # Target the attack in mouse direction
    # def attack_target(self, mouse_pos):
    #     self.attack_end_point = pygame.Vector2(mouse_pos)
    #     attack_angle = 0
    #     if self.attack_start_point != self.attack_end_point:
    #         self.attack_dir = (self.attack_end_point - self.attack_start_point).normalize()
    #         attack_angle = -self.attack_dir.angle_to(pygame.Vector2(1, 0)) * math.pi / 180
    #     else:
    #         attack_angle = math.atan2(0, 1)
    #         self.attack_dir = pygame.Vector2(0)

    #     self.attack_vfx.update(attack_angle)

    #     self.attack_dir.x *= self.attack_force_x
    #     self.attack_dir.y *= self.attack_force_y

    # # Increase time back to normal again
    # def attack_end(self):
    #     self.preparing_attack = False
    #     self.velocity.y = 0
    #     self.attacking = True
    #     self.velocity = self.attack_dir

    # # Logic of the attack itself
    # def process_attack(self):
    #     # Forces the velocity to be equal to the attack dir without issues
    #     self.velocity = pygame.Vector2(self.attack_dir.x, self.attack_dir.y)

    # def draw_attack_UI(self):
    #     pygame.draw.circle(renderer.layers["UI"], pygame.Color(255, 255, 255), self.attack_start_point, self.attack_circle_radius, self.attack_circle_thickness)
    #     pygame.draw.circle(renderer.layers["UI"], pygame.Color(255, 255, 255), self.attack_end_point, self.attack_circle_radius, self.attack_circle_thickness)

    #     if self.attack_dir != pygame.Vector2(0):
    #         start_point_line = self.attack_start_point + self.attack_dir.normalize() * self.attack_circle_radius
    #         end_point_line = self.attack_end_point - self.attack_dir.normalize() * self.attack_circle_radius
    #         pygame.draw.line(renderer.layers["UI"], pygame.Color(255, 255, 255), start_point_line, end_point_line, 1)
#endregion

class Bullet():
    def __init__(self, image, start_pos, vel, lifetime) -> None:
        self.image = image
        self.rect = self.image.get_rect()
        self.pos = start_pos
        self.vel = vel
        self.lifetime = lifetime

        self.time = 0

    def update(self, collision_tiles):
        self.time += game_manager.dt
        self.pos += self.vel * game_manager.dt
        self.rect.center = self.pos

        for tile in collision_tiles:
            if self.rect.colliderect(tile):
                self.time = self.lifetime + 1

    def draw(self):
        dim = self.image.get_size()

        sprite_surf = pygame.Surface((dim[0], dim[1]), pygame.SRCALPHA)
        sprite_surf.fill((0, 0, 0, 0))
        sprite_surf.blit(self.image.convert_alpha(), (0, 0))

        renderer.add_drop_shadow(sprite_surf, (-1, 1), game_manager.shadow_color)

        renderer.layers["foreground"].blit(sprite_surf.convert_alpha(), (
            self.rect.x - game_manager.cam_scroll.x,
            self.rect.y - game_manager.cam_scroll.y
        ))

class BulletExplosion():
    def __init__(self, animator, lifetime, pos) -> None:
        self.animator = animator
        self.lifetime = lifetime
        self.time = 0
        self.image = self.animator.update()
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.image = self.animator.update()

        if self.animator.current_clip.finished == True:
            self.time = self.lifetime + 1

    def draw(self):
        dim = self.image.get_size()

        sprite_surf = pygame.Surface((dim[0], dim[1]), pygame.SRCALPHA)
        sprite_surf.fill((0, 0, 0, 0))
        sprite_surf.blit(self.image.convert_alpha(), (0, 0))

        renderer.layers["foreground"].blit(sprite_surf.convert_alpha(), (
            self.rect.x - game_manager.cam_scroll.x,
            self.rect.y - game_manager.cam_scroll.y
        ))
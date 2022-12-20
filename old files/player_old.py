from math import ceil, floor
import utils
import pygame
import enum

class Player:
    def __init__(self, image, pos, gravity, velocity=pygame.Vector2(0))  -> None:
        self.image = image
        self.rect = self.image.get_rect()
        self.acceleration = gravity
        self.velocity = velocity
        self.position = pos
        self.facingRight = True
        self.move_damping = pygame.Vector2(0.3, 1)
        self.move_dir = pygame.Vector2(1, 0)
        self.gravity_dir = GravityDirection.down
        self.rotation = 0
        self.previous_rotation = 0
        self.desired_rotation = 0
        self.dt = 0
        # Rotate animation variable
        self.t = 0
        self.is_rotating = False

    def update_player(self, collision_rects):
        # Update physics
        self.get_movement()
        self.velocity += self.acceleration * self.dt

        dx = self.velocity.x * self.dt
        dy = self.velocity.y * self.dt

        # Create collision rects
        dx_rect = pygame.Rect(self.rect.x + (ceil(dx) if dx > 0 else floor(dx)), self.rect.y, self.image.get_width(), self.image.get_height())
        dy_rect = pygame.Rect(self.rect.x, self.rect.y + (ceil(dy) if dy > 0 else floor(dy)), self.image.get_width(), self.image.get_height())
        
        # Check and resolve collisions
        for tile in collision_rects:
            if tile.colliderect(dx_rect):
                dx = 0
                self.velocity.x = 0

            if tile.colliderect(dy_rect):
                if self.velocity.y < 0:
                    dy = tile.bottom - self.rect.top
                    self.velocity.y = 0
                elif self.velocity.y > 0:
                    dy = tile.top - self.rect.bottom
                    self.velocity.y = 0

        # Update position
        self.position += pygame.Vector2(dx, dy)
        self.rect.topleft = self.position.xy

        if self.is_rotating:
            self.rotation = self.rotate_anim(0.7, self.previous_rotation, self.desired_rotation)

        # Sprite flipping logic
        if self.gravity_dir == GravityDirection.right:
            if self.facingRight and self.velocity.y > 0 or not self.facingRight and self.velocity.y < 0:
                self.flip()
        elif self.gravity_dir == GravityDirection.left:
            if self.facingRight and self.velocity.y < 0 or not self.facingRight and self.velocity.y > 0:
                self.flip()
        elif self.gravity_dir == GravityDirection.up:
            if self.facingRight and self.velocity.x > 0 or not self.facingRight and self.velocity.x < 0:
                self.flip()
        elif self.gravity_dir == GravityDirection.down:
            if self.facingRight and self.velocity.x < 0 or not self.facingRight and self.velocity.x > 0:
                self.flip()

    def get_movement(self):
        # Set velocity based on key input
        if pygame.key.get_pressed()[pygame.K_a]:
            if self.gravity_dir == GravityDirection.right or self.gravity_dir == GravityDirection.left:
                self.velocity.y = self.move_dir.y * -50
            elif self.gravity_dir == GravityDirection.up or self.gravity_dir == GravityDirection.down:
                self.velocity.x = self.move_dir.x * -50
        elif pygame.key.get_pressed()[pygame.K_d]:
            if self.gravity_dir == GravityDirection.right or self.gravity_dir == GravityDirection.left:
                self.velocity.y = self.move_dir.y * 50
            elif self.gravity_dir == GravityDirection.up or self.gravity_dir == GravityDirection.down:
                self.velocity.x = self.move_dir.x * 50
        else:
            self.velocity.x *= self.move_damping.x
            self.velocity.y *= self.move_damping.y

    def control_gravity(self, key_pressed):
        if self.is_rotating:
            return

        self.previous_rotation = self.rotation

        if key_pressed == pygame.K_RIGHT:
            self.desired_rotation -= 90
        elif key_pressed == pygame.K_LEFT:
            self.desired_rotation += 90

        if self.desired_rotation < 0:
            self.desired_rotation = 270
            self.previous_rotation = 360
        elif self.desired_rotation > 270:
            self.desired_rotation = 0
            self.previous_rotation = -90

        if self.desired_rotation == 0:
            self.acceleration = pygame.Vector2(0, 50)
            self.velocity.y = 10
            self.move_damping = pygame.Vector2(0.9, 1)
            self.move_dir = pygame.Vector2(1, 0)

            self.gravity_dir = GravityDirection.down
        elif self.desired_rotation == 90:
            self.acceleration = pygame.Vector2(-50, 0)
            self.velocity.x = -10
            self.move_damping = pygame.Vector2(1, 0.9)
            self.move_dir = pygame.Vector2(0, 1)

            self.gravity_dir = GravityDirection.left
        elif self.desired_rotation == 180:
            self.acceleration = pygame.Vector2(0, -50)
            self.velocity.y = -10
            self.move_damping = pygame.Vector2(0.9, 1)
            self.move_dir = pygame.Vector2(-1, 0)

            self.gravity_dir = GravityDirection.up
        elif self.desired_rotation == 270:
            self.acceleration = pygame.Vector2(50, 0)
            self.velocity.x = 10
            self.move_damping = pygame.Vector2(1, 0.9)
            self.move_dir = pygame.Vector2(0, -1)

            self.gravity_dir = GravityDirection.right

        self.is_rotating = True

    def rotate_anim(self, duration, start_rot, end_rot) -> float:
        while self.t < duration:
            rotation = utils.lerp_2(start_rot, end_rot, utils.circle(self.t / duration))
            self.t += self.dt
            return rotation

        self.t = 0
        self.is_rotating = False
        return end_rot


    def flip(self):
        self.facingRight = not self.facingRight
        self.image = pygame.transform.flip(self.image, True, False)

    def draw(self, surf):
        transformed_surf = utils.rotate_centered(self.image, -self.rotation, self.rect.center)
        surf.blit(transformed_surf[0], transformed_surf[1])

class GravityDirection(enum.Enum):
    down = 1
    up = 2
    left = 3
    right = 4
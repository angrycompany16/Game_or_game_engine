import pygame
import world
import game_manager

SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
GAME_WIDTH, GAME_HEIGHT = 480, 270
TILE_SIZE = 16

pygame.display.init()
pygame.font.init()
pygame.display.set_caption("The game!")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.FULLSCREEN)
font = pygame.font.SysFont("Arial", 18)

world_cam = {
    "dead_zone_x": 30,
    "dead_zone_y": 15,
    "smooth_factor": 0.05,
    "size": (GAME_WIDTH, GAME_HEIGHT)
}

clock = pygame.time.Clock()

# Initializes the world, player, etc
world_main = world.World("Assets/LDtk/world.ldtk", pygame.Surface((GAME_WIDTH, GAME_HEIGHT), flags=pygame.SRCALPHA), world_cam)

def main():
    running = True

    while running:
        pygame.display.update()
        screen.fill(pygame.Color(255, 0, 0))

        tick_time = clock.tick() / 1000

        game_manager.dt = tick_time * game_manager.global_timescale
        game_manager.abs_dt = tick_time

        world_main.update()
        transformed_surf, transformed_rect = world_main.transform()
        screen.blit(transformed_surf, transformed_rect)

        fps = str(int(clock.get_fps()))
        fps_text = font.render(fps, 1, pygame.Color("coral"))

        screen.blit(fps_text, (10, 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    world_main.player.jump()
                if event.key == pygame.K_a and not world_main.player.attacking:
                    world_main.player.shooting = True
                    world_main.player.shoot()
                if event.key == pygame.K_s and not world_main.player.shooting:
                    up_attacking = int(pygame.key.get_pressed()[pygame.K_UP])
                    down_attacking = int(pygame.key.get_pressed()[pygame.K_DOWN])
                    world_main.player.attack(up_attacking - down_attacking)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    world_main.player.cancel_jump()
                if event.key == pygame.K_a:
                    world_main.player.shooting = False
                    world_main.player.time_since_fire = 0

    pygame.display.quit()

if __name__ == "__main__":
    main()
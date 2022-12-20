import pygame 
import particle_system
import animations
import renderer

# Boilerplate for converting images
GAME_WIDTH, GAME_HEIGHT = 480, 270
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080

pygame.display.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

global_timescale = 1
dt = 0
# dt_abs = 0
cam_scroll = pygame.Vector2(0)
shadow_color = 0

DEV_MODE = True

# Spritesheets
def load_spritesheet(sheet, width, height):
    # Get the amount of frames/images in spritesheet
    sheet_width_units = round(sheet.get_width() / width)
    sheet_height_units = round(sheet.get_height() / height)

    frames = []

    # Create surface for each frame and add it to the list
    for i in range(0, sheet_height_units):
        for j in range(0, sheet_width_units):
            new_surf = pygame.Surface((width, height), flags=pygame.SRCALPHA)
            new_surf.blit(sheet, pygame.Rect(0, 0, 0, 0), pygame.Rect(width * j, height * i, width, height))
            frames.append(new_surf)

    return frames

def convert_ldtk_path(path):
    return "Assets" + path[2:]

# Enemy sprite sheets
enemy_test = pygame.image.load("Assets/Images/Test_imgs/enemy-test.png").convert_alpha()

# Player
player_character = pygame.image.load("Assets/Images/Character_sprites/character_sprite.png").convert_alpha()
player_idle_sheet = pygame.image.load("Assets/Images/Character_sprites/character_idle_sheet.png").convert_alpha()
player_run_sheet = pygame.image.load("Assets/Images/Character_sprites/character_run_sheet.png").convert_alpha()
player_jump_sheet = pygame.image.load("Assets/Images/Character_sprites/character_jump_sheet.png").convert_alpha()
player_fall_sheet = pygame.image.load("Assets/Images/Character_sprites/character_fall_sheet.png").convert_alpha()
player_shoot_sheet = pygame.image.load("Assets/Images/Character_sprites/character_shoot.png").convert_alpha()
player_shoot_down_sheet = pygame.image.load("Assets/Images/Character_sprites/character_shoot_down-Sheet.png").convert_alpha()
player_attack_sheet = pygame.image.load("Assets/Images/Character_sprites/player_attack-Sheet.png").convert_alpha()
player_attack_up_sheet = pygame.image.load("Assets/Images/Character_sprites/player_attack_up-Sheet.png").convert_alpha()

bullet_r_sprite = pygame.image.load("Assets/Images/Character_sprites/Bullet/bullet-right.png").convert_alpha()
bullet_l_sprite = pygame.image.load("Assets/Images/Character_sprites/Bullet/bullet-left.png").convert_alpha()
bullet_d_sprite = pygame.image.load("Assets/Images/Character_sprites/Bullet/bullet-down.png").convert_alpha()
bullet_u_sprite = pygame.image.load("Assets/Images/Character_sprites/Bullet/bullet-up.png").convert_alpha()
bullet_explode_sheet = pygame.image.load("Assets/Images/Character_sprites/Bullet/bullet-explode-Sheet.png").convert_alpha()

particle_round = pygame.image.load("Assets/Images/Particles/particle_test.png").convert_alpha()
particle_square = pygame.image.load("Assets/Images/Particles/particle_square.png").convert_alpha()
particle_checkered = pygame.image.load("Assets/Images/Particles/particle_checkered.png").convert_alpha()
particle_leaf = pygame.image.load("Assets/Images/test_imgs/leaf_particle_test.png").convert_alpha()
particle_leaf2 = pygame.image.load("Assets/Images/test_imgs/leaf_particle_2.png").convert_alpha()

player_anim = animations.Animator((
    animations.AnimationClip(player_idle_sheet, 12, 25, name="PLAYER_IDLE"),
    animations.AnimationClip(player_run_sheet, 12, 25, name="PLAYER_RUN"),
    animations.AnimationClip(player_jump_sheet, 12, 25, name="PLAYER_JUMP", looping=False),
    animations.AnimationClip(player_fall_sheet, 12, 25, name="PLAYER_FALL"),
    animations.AnimationClip(player_shoot_sheet, 17, 28, name="PLAYER_SHOOT", fps=24),
    animations.AnimationClip(player_shoot_down_sheet, 17, 29, name="PLAYER_SHOOT_DOWN"),
    animations.AnimationClip(player_attack_sheet, 70, 24, name="PLAYER_ATTACK", fps=17),
    animations.AnimationClip(player_attack_up_sheet, 76, 63, name="PLAYER_ATTACK_UP", fps=17)
))

#region PARTICLE SYSTEMS

# Player particle systems
foot_particles = particle_system.ParticleSystem(
    self_pos=pygame.Vector2(0, 0), 
    start_pos=particle_system.ParticleSystemField(pygame.Vector2(-5, -1), pygame.Vector2(5, -1)), 
    start_vel=particle_system.ParticleSystemField(pygame.Vector2(-25, -10), pygame.Vector2(-10, -20)), 
    acceleration=particle_system.ParticleSystemField(pygame.Vector2(0, 10), pygame.Vector2(0, 20)), 
    image=particle_checkered, 
    spawn_rate=40,
    lifetime=particle_system.ParticleSystemField(0.1, 0.3),
    start_scale=particle_system.ParticleSystemField(1, 4),
    start_rotation=particle_system.ParticleSystemField(0, 90),
    start_color=particle_system.ParticleSystemField(pygame.Vector3(255, 255, 255), pygame.Vector3(255, 255, 255)),
    end_color=particle_system.ParticleSystemField(pygame.Vector3(255, 255, 255), pygame.Vector3(255, 255, 255)),
    scale_time_factor=particle_system.ParticleSystemField(-6, -10),
    rotation_time_factor=particle_system.ParticleSystemField(0, 0),
    rendering_layer=renderer.layers["foreground"]
)
arc_particles = particle_system.ParticleSystem(
    self_pos=pygame.Vector2(0, 0), 
    start_pos=particle_system.ParticleSystemField(pygame.Vector2(2, 0), pygame.Vector2(-2, 0)), 
    start_vel=particle_system.ParticleSystemField(pygame.Vector2(-10, -10), pygame.Vector2(-5, -20)), 
    acceleration=particle_system.ParticleSystemField(pygame.Vector2(0, 10), pygame.Vector2(0, 20)), 
    image=particle_checkered, 
    spawn_rate=40,
    lifetime=particle_system.ParticleSystemField(0.15, 0.3),
    start_scale=particle_system.ParticleSystemField(2, 3),
    start_rotation=particle_system.ParticleSystemField(0, 90),
    start_color=particle_system.ParticleSystemField(pygame.Vector3(255, 255, 255), pygame.Vector3(255, 255, 255)),
    end_color=particle_system.ParticleSystemField(pygame.Vector3(255, 255, 255), pygame.Vector3(255, 255, 255)),
    scale_time_factor=particle_system.ParticleSystemField(-6, -10),
    rotation_time_factor=particle_system.ParticleSystemField(0, 0),
    rendering_layer=renderer.layers["foreground"]
)
jump_particles = particle_system.ParticleSystem(
    self_pos=pygame.Vector2(0, 0), 
    start_pos=particle_system.ParticleSystemField(pygame.Vector2(-5, -1), pygame.Vector2(5, -1)), 
    start_vel=particle_system.ParticleSystemField(pygame.Vector2(10, -10), pygame.Vector2(-10, -20)), 
    acceleration=particle_system.ParticleSystemField(pygame.Vector2(0, -30), pygame.Vector2(0, -50)), 
    image=particle_checkered, 
    spawn_rate=40,
    lifetime=particle_system.ParticleSystemField(0.2, 0.4),
    start_scale=particle_system.ParticleSystemField(1, 3),
    start_rotation=particle_system.ParticleSystemField(0, 90),
    start_color=particle_system.ParticleSystemField(pygame.Vector3(255, 255, 255), pygame.Vector3(255, 255, 255)),
    end_color=particle_system.ParticleSystemField(pygame.Vector3(255, 255, 255), pygame.Vector3(255, 255, 255)),
    scale_time_factor=particle_system.ParticleSystemField(-6, -10),
    rotation_time_factor=particle_system.ParticleSystemField(0, 0),
    direction=pygame.Vector2(1, 1),
    rendering_layer=renderer.layers["foreground"]
)
land_particles = particle_system.ParticleSystem(
    self_pos=pygame.Vector2(0, 0), 
    start_pos=particle_system.ParticleSystemField(pygame.Vector2(-8, 0), pygame.Vector2(8, 0)), 
    start_vel=particle_system.ParticleSystemField(pygame.Vector2(50, -10), pygame.Vector2(-50, -15)), 
    acceleration=particle_system.ParticleSystemField(pygame.Vector2(0, 70), pygame.Vector2(0, 100)), 
    image=particle_checkered, 
    spawn_rate=40,
    lifetime=particle_system.ParticleSystemField(0.2, 0.4),
    start_scale=particle_system.ParticleSystemField(1, 3),
    start_rotation=particle_system.ParticleSystemField(0, 90),
    start_color=particle_system.ParticleSystemField(pygame.Vector3(255, 255, 255), pygame.Vector3(255, 255, 255)),
    end_color=particle_system.ParticleSystemField(pygame.Vector3(255, 255, 255), pygame.Vector3(255, 255, 255)),
    scale_time_factor=particle_system.ParticleSystemField(-6, -10),
    rotation_time_factor=particle_system.ParticleSystemField(0, 0),
    rendering_layer=renderer.layers["foreground"]
)
damage_particles = particle_system.ParticleSystem(
    self_pos=pygame.Vector2(100, 100), 
    start_pos=particle_system.ParticleSystemField(pygame.Vector2(-2, -2), pygame.Vector2(2, 2)), 
    start_vel=particle_system.ParticleSystemField(pygame.Vector2(-150, -150), pygame.Vector2(150, 150)), 
    acceleration=particle_system.ParticleSystemField(pygame.Vector2(0, 0), pygame.Vector2(0, 0)), 
    image=particle_checkered, 
    spawn_rate=0,
    lifetime=particle_system.ParticleSystemField(0.05, 0.3),
    start_scale=particle_system.ParticleSystemField(1, 3),
    start_rotation=particle_system.ParticleSystemField(0, 90),
    start_color=particle_system.ParticleSystemField(pygame.Vector3(157, 48, 59), pygame.Vector3(157, 48, 59)),
    end_color=particle_system.ParticleSystemField(pygame.Vector3(157, 48, 59), pygame.Vector3(157, 48, 59)),
    scale_time_factor=particle_system.ParticleSystemField(-2, -5),
    rotation_time_factor=particle_system.ParticleSystemField(0, 0),
    rendering_layer=renderer.layers["foreground"]
)

# Test level particle systems here!
level_2_system_bg2 = particle_system.ParticleSystem(
    self_pos=pygame.Vector2(0, 0), 
    start_pos=particle_system.ParticleSystemField(pygame.Vector2(-200, -100), pygame.Vector2(736, 416)), 
    start_vel=particle_system.ParticleSystemField(pygame.Vector2(10, 5), pygame.Vector2(20, 10)), 
    acceleration=particle_system.ParticleSystemField(pygame.Vector2(0, 0), pygame.Vector2(0, 0)), 
    image=particle_leaf, 
    spawn_rate=7,
    lifetime=particle_system.ParticleSystemField(10, 20),
    start_scale=particle_system.ParticleSystemField(1.0, 2.0),
    start_rotation=particle_system.ParticleSystemField(0, 90),
    start_color=particle_system.ParticleSystemField(pygame.Vector3(255, 255, 255), pygame.Vector3(255, 255, 255)),
    end_color=particle_system.ParticleSystemField(pygame.Vector3(255, 255, 255), pygame.Vector3(255, 255, 255)),
    scale_time_factor=particle_system.ParticleSystemField(-0.1, -0.15),
    rotation_time_factor=particle_system.ParticleSystemField(0, 10),
    noise_factor=0.3,
    rendering_layer=renderer.layers["background2"],
    direction=pygame.Vector2(1, 1),
    activate_on_start=True
)
level_2_system_bg1 = particle_system.ParticleSystem(
    self_pos=pygame.Vector2(0, 0), 
    start_pos=particle_system.ParticleSystemField(pygame.Vector2(-200, -100), pygame.Vector2(736, 416)), 
    start_vel=particle_system.ParticleSystemField(pygame.Vector2(20, 10), pygame.Vector2(40, 20)), 
    acceleration=particle_system.ParticleSystemField(pygame.Vector2(0, 0), pygame.Vector2(0, 0)), 
    image=particle_leaf2, 
    spawn_rate=10,
    lifetime=particle_system.ParticleSystemField(7.5, 15.0),
    start_scale=particle_system.ParticleSystemField(1.0, 2.0),
    start_rotation=particle_system.ParticleSystemField(0, 90),
    start_color=particle_system.ParticleSystemField(pygame.Vector3(255, 255, 255), pygame.Vector3(255, 255, 255)),
    end_color=particle_system.ParticleSystemField(pygame.Vector3(255, 255, 255), pygame.Vector3(255, 255, 255)),
    scale_time_factor=particle_system.ParticleSystemField(-0.1, -0.15),
    rotation_time_factor=particle_system.ParticleSystemField(10, 45),
    noise_factor=2,
    rendering_layer=renderer.layers["background1"],
    direction=pygame.Vector2(1, 1),
    activate_on_start=True
)
level_1_system_bg2 = particle_system.ParticleSystem(
    self_pos=pygame.Vector2(0, 0), 
    start_pos=particle_system.ParticleSystemField(pygame.Vector2(-200, -100), pygame.Vector2(736, 416)), 
    start_vel=particle_system.ParticleSystemField(pygame.Vector2(10, 5), pygame.Vector2(20, 10)), 
    acceleration=particle_system.ParticleSystemField(pygame.Vector2(0, 0), pygame.Vector2(0, 0)), 
    image=particle_square, 
    spawn_rate=10,
    lifetime=particle_system.ParticleSystemField(10, 20),
    start_scale=particle_system.ParticleSystemField(2.0, 1.0),
    start_rotation=particle_system.ParticleSystemField(0, 0),
    start_color=particle_system.ParticleSystemField(pygame.Vector3(52, 133, 157), pygame.Vector3(52, 133, 157)),
    end_color=particle_system.ParticleSystemField(pygame.Vector3(52, 133, 157), pygame.Vector3(52, 133, 157)),
    scale_time_factor=particle_system.ParticleSystemField(-0.05, -0.1),
    rotation_time_factor=particle_system.ParticleSystemField(0, 0),
    noise_factor=1,
    rendering_layer=renderer.layers["background2"],
    direction=pygame.Vector2(1, 1),
    activate_on_start=True
)
level_1_system_bg1 = particle_system.ParticleSystem(
    self_pos=pygame.Vector2(0, 0), 
    start_pos=particle_system.ParticleSystemField(pygame.Vector2(-200, -100), pygame.Vector2(736, 416)), 
    start_vel=particle_system.ParticleSystemField(pygame.Vector2(20, 10), pygame.Vector2(40, 20)), 
    acceleration=particle_system.ParticleSystemField(pygame.Vector2(0, 0), pygame.Vector2(0, 0)), 
    image=particle_square, 
    spawn_rate=10,
    lifetime=particle_system.ParticleSystemField(7.5, 15.0),
    start_scale=particle_system.ParticleSystemField(2.0, 3.0),
    start_rotation=particle_system.ParticleSystemField(0, 0),
    start_color=particle_system.ParticleSystemField(pygame.Vector3(23, 67, 75), pygame.Vector3(23, 67, 75)),
    end_color=particle_system.ParticleSystemField(pygame.Vector3(23, 67, 75), pygame.Vector3(23, 67, 75)),
    scale_time_factor=particle_system.ParticleSystemField(-0.1, -0.15),
    rotation_time_factor=particle_system.ParticleSystemField(0, 0),
    noise_factor=2,
    rendering_layer=renderer.layers["background1"],
    direction=pygame.Vector2(1, 1),
    activate_on_start=True
)

#endregion

level_particle_systems = {
    "3 - bg2": level_2_system_bg2, 
    "3 - bg1": level_2_system_bg1, 
    "2 - bg2": level_1_system_bg2, 
    "2 - bg1": level_1_system_bg1 
}
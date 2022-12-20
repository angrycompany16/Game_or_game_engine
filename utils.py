import pygame
import math

def lerp_1(start, end, t) -> float:
    return start + t * (end - start)

def lerp_2(start, end, t) -> float:
    return (1 - t) * start + t * end

def rotate_centered(image, angle, center):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = center)

    return rotated_image, new_rect

def scale_centered(image, new_size, center):
    scaled_image = pygame.transform.scale(image, new_size)
    new_rect = scaled_image.get_rect(center = center)

    return scaled_image, new_rect

def rotozoom_centered(image, angle, scale, center):
    transformed_surf = pygame.transform.rotozoom(image, angle, scale)
    transformed_rect = transformed_surf.get_rect(center = center)

    return transformed_surf, transformed_rect

def circle(t) -> float:
    return math.sqrt(1 - (t - 1) ** 2)

def clamp(val, min, max):
    if min <= val and val <= max:
        return val
    elif min > val:
        return min
    elif max < val:
        return max
    else:
        return None
        
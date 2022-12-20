import pygame
import game_manager
import typing

class AnimationClip:
    def __init__(self, spritesheet: pygame.image, frame_width: int, frame_height: int, name="Main", fps=12, looping=True, locked=False) -> None:
        self.spritesheet = spritesheet
        self.name = name
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.fps = fps
        self.looping = looping
        self.locked = locked
        self.current_time = 0
        self.current_frame = 0
        self.finished = False

        self.images = game_manager.load_spritesheet(self.spritesheet, self.frame_width, self.frame_height)

    # Update which part of the spritesheet is being rendered and return it as a surface
    def update(self) -> pygame.Surface:
        self.current_time += game_manager.dt

        if self.current_time >= 1 / self.fps:
            self.current_frame += 1
            self.current_time = 0

            if self.current_frame > len(self.images) - 1:
                if self.looping:
                    self.current_frame = 0
                else:
                    self.finished = True
                    self.current_frame -= 1

        return self.images[self.current_frame]

class Animator:
    def __init__(self, animation_clips: typing.List[AnimationClip]) -> None:
        self.animation_clips = animation_clips
        self.current_clip = animation_clips[0]

    def set_state(self, anim_name: str) -> None:
        if anim_name == self.current_clip.name: return
        if self.get_clip_with_name(anim_name).locked == True: return
        
        self.current_clip = self.get_clip_with_name(anim_name)
        self.current_clip.current_frame = 0

    def get_clip_with_name(self, anim_name: str) -> AnimationClip:
        for anim in self.animation_clips:
            if anim.name == anim_name:
                return anim
            
        return None

    def update(self) -> pygame.Surface:
        current_frame = self.current_clip.update()
        return current_frame
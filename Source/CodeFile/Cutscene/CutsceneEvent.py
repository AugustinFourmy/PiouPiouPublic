import pygame
import pathlib
import enum


class CutsceneElementType(enum.Enum):
    SPRITE = 0
    NON_RENDER_TEXT = 1
    FUNC = 2
    SFX = 3
    MUSIC_WITH_INTRO = 4
    MUSIC = 5
    ANIMATED_SPRITE = 6


class Event:
    def __init__(self, start_frame: int, end_frame: int, element):
        self.element = element
        self.end_frame = end_frame
        self.start_frame = start_frame
        self.duration = self.end_frame - self.start_frame
        if self.duration == 0:
            self.duration = 1

    def update(self):
        print("No Update in this event")


class PlayEvent(Event):
    def __init__(self, frame: int, element, speed: int):
        Event.__init__(self, frame, frame, element)
        self.speed = speed

    def update(self):
        self.element.sprite.play(speed=self.speed)


class MoveToEvent(Event):
    def __init__(self, start_frame: int, end_frame: int, element, final_pos: tuple[float, float]):
        Event.__init__(self, start_frame, end_frame, element)
        x = final_pos[0] - self.element.pos[0]
        y = final_pos[1] - self.element.pos[1]
        self.velocity = (x / self.duration, y / self.duration)

    def update(self):
        self.element.pos[0] += self.velocity[0]
        self.element.pos[1] += self.velocity[1]


class FadeEvent(Event):
    def __init__(self, start_frame: int, end_frame: int, element, final_opacity: int):
        Event.__init__(self, start_frame, end_frame, element)
        self.final_opacity = final_opacity
        self.first_time = True
        self.fade_speed = 0.0

    def update(self):
        if self.first_time:
            self.fade_speed = (self.final_opacity - self.element.opacity) / self.duration
            self.first_time = False
        self.element.opacity += self.fade_speed
class FlipEvent(Event):
    def __init__(self, frame, element, h, v):
        Event.__init__(self, frame, frame, element)
        self.h = h
        self.v = v
        
    def update(self):
        self.element.draw_sprite = pygame.transform.flip(self.element.rotated_sprite, self.h, self.v).convert_alpha()
            
        


class RotateEvent(Event):
    def __init__(self, start_frame: int, end_frame: int, element, final_angle):
        Event.__init__(self, start_frame, end_frame, element)
        self.rotation_speed = (final_angle - self.element.angle) / self.duration

    def update(self):
        self.element.angle += self.rotation_speed
        self.element.rotated_sprite = pygame.transform.rotate(self.element.sprite, self.element.angle).convert_alpha()
        self.element.draw_sprite = pygame.transform.rotate(self.element.scaled_sprite, self.element.angle).convert_alpha()


class ScaleEvent(Event):
    def __init__(self, start_frame: int, end_frame: int, element, final_scale):
        Event.__init__(self, start_frame, end_frame, element)
        self.scale_speed = ((final_scale[0] - self.element.scale[0]) / self.duration, (final_scale[1] - self.element.scale[1])/self.duration)

    def update(self):
        self.element.scale = (self.element.scale[0] + self.scale_speed[0], self.element.scale[1] + self.scale_speed[1])
        if self.element.type == CutsceneElementType.ANIMATED_SPRITE:
            self.element.sprite.scale(self.element.scale)
        else:
            self.element.scaled_sprite = pygame.transform.scale(self.element.sprite, self.element.scale).convert_alpha()
            self.element.draw_sprite = pygame.transform.scale(self.element.rotated_sprite, self.element.scale).convert_alpha()


# Non-render comment_text event

class LetterByLetterEvent(Event):
    def __init__(self, start_frame: int, end_frame: int, element, starting_letter_id: int, ending_leter_id: int, taille: int, color='#ffffff'):
        assert element.type == CutsceneElementType.NON_RENDER_TEXT, 'Invalid Element type for this event'
        assert starting_letter_id < ending_leter_id,  'Invalid letter id'
        Event.__init__(self, start_frame, end_frame, element)
        self.show_speed = (ending_leter_id - starting_letter_id)/self.duration
        self.font = pygame.font.Font(pathlib.Path(self.element.font_path), taille)
        self.color = color
        self.start_id = starting_letter_id
        self.place = self.start_id

    def update(self):
        self.place += self.show_speed
        self.element.draw_sprite = self.font.render(self.element.text[self.start_id:int(self.place)], True, self.color)


class RenderText(Event):
    def __init__(self, frame: int, element, taille: int, color='#ffffff'):
        assert element.type == CutsceneElementType.NON_RENDER_TEXT, 'Invalid Element type for this event'
        Event.__init__(self, frame, frame, element)
        self.font = pygame.font.Font(pathlib.Path(self.element.font_path), taille)
        self.color = color

    def update(self):
        self.element.draw_sprite = self.font.render(self.element.text, True, self.color)


class HideEvent(Event):
    def __init__(self, frame: int, element):
        Event.__init__(self, frame, frame, element)

    def update(self):
        self.element.drawing = False


class ShowEvent(Event):
    def __init__(self, frame: int, element):
        Event.__init__(self, frame, frame, element)

    def update(self):
        self.element.drawing = True


# Function

class RunFuncEvent(Event):
    def __init__(self, frame: int, element):
        Event.__init__(self, frame, frame, element)

    def update(self):
        self.element.function()


class RunFuncMultipleTimeEvent(Event):
    def __init__(self, start_frame: int, end_frame: int, element):
        Event.__init__(self, start_frame, end_frame, element)

    def update(self):
        self.element.function()



# SFX


class PlaySfxEvent(Event):
    def __init__(self, frame: int, element):
        Event.__init__(self, frame, frame, element)

    def update(self):
        self.element.sfx.play()


# Music

class PlayMusicEvent(Event):
    def __init__(self, frame: int, element, looping: bool):
        self.looping = looping
        Event.__init__(self, frame, frame, element)

    def update(self):
        pygame.mixer.music.load(self.element.main_loop)
        if self.looping:
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.play()


class PlayMusicWithIntroEvent(Event):
    def __init__(self, frame: int, element, looping: bool):
        self.looping = looping
        Event.__init__(self, frame, frame, element)

    def update(self):
        pygame.mixer.music.load(self.element.music_intro)
        pygame.mixer.music.play()
        if self.looping:
            pygame.mixer.music.queue(self.element.main_loop, loops=-1)
        else:
            pygame.mixer.music.play()


class MusicStopEvent(Event):
    def __init__(self, frame: int, element):
        Event.__init__(self, frame, frame, element)

    def update(self):
        pygame.mixer.music.stop()


class MusicStopFadeOutEvent(Event):
    def __init__(self, frame: int, element, duration: int):
        Event.__init__(self, frame, frame, element)
        self.fade_out_duration = duration

    def update(self):
        pygame.mixer.music.fadeout(self.fade_out_duration)


class MusicUnloadEvent(Event):
    def __init__(self, frame: int, element):
        Event.__init__(self, frame, frame, element)

    def update(self):
        pygame.mixer.music.unload()

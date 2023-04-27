import pygame
import Source.CodeFile.Cutscene.CutsceneEvent as Events
from Source.CodeFile.Animation.teste_animation import animated_sprite


def load_sprite_element(element_dict):
    return CutsceneElement(Events.CutsceneElementType.SPRITE, pos_initial=tuple(element_dict["position_initial"]),
                           sprite_path=element_dict["sprite_path"],
                           initial_visibility=element_dict["visible"])


def load_animated_sprite(element_dict):
    return CutsceneElement(Events.CutsceneElementType.ANIMATED_SPRITE,
                           pos_initial=tuple(element_dict["position_initial"]),
                           sprite_path=element_dict["sprite_path"],
                           initial_visibility=element_dict["visible"],
                           sprite_sheet_direction=element_dict["is_vertical"],
                           sprite_sheet_height_limit=element_dict["mono_sprite_size"][1],
                           sprite_sheet_width_limit=element_dict["mono_sprite_size"][0]
                           )


def load_text_element(element_dict):
    return CutsceneElement(Events.CutsceneElementType.NON_RENDER_TEXT,
                           pos_initial=tuple(element_dict["position_initial"]), text=element_dict["text"],
                           font_path=element_dict["font_path"])


def load_function_element(element_dict):
    if len(element_dict['arguments_list']) == 0:
        return CutsceneElement(Events.CutsceneElementType.FUNC, function=eval(element_dict["func_name"]))
    arg_def = [arg[2] for arg in element_dict["arguments_list"]]
    return CutsceneElement(Events.CutsceneElementType.FUNC, function=lambda: eval(element_dict["func_name"])(*arg_def))


def load_sfx_element(element_dict):
    return CutsceneElement(Events.CutsceneElementType.SFX, sfx_path=element_dict["sfx_path"])


def load_music_with_intro_element(element_dict):
    return CutsceneElement(Events.CutsceneElementType.MUSIC_WITH_INTRO, music_path=element_dict["main_music_path"],
                           intro_music_path=element_dict["intro_music_path"])


def load_music_element(element_dict):
    return CutsceneElement(Events.CutsceneElementType.MUSIC, music_path=element_dict["music_path"])


load_element_func = {
    "Sprite": load_sprite_element,
    "Sprite Animé": load_animated_sprite,
    "Texte": load_text_element,
    "Fonction": load_function_element,
    "SFX": load_sfx_element,
    "Musique avec intro unique": load_music_with_intro_element,
    "Musique sans intro unique": load_music_element
}

def load_move_to_event(event_dict, element):
    return Events.MoveToEvent(event_dict['start_frame'], event_dict['end_frame'], element, tuple(event_dict['destination']))

def load_fade_event(event_dict, element):
    return Events.FadeEvent(event_dict['start_frame'], event_dict['end_frame'], element, event_dict['opacity'])


def load_rotate_event(event_dict, element):
    return Events.RotateEvent(event_dict['start_frame'], event_dict['end_frame'], element, event_dict['angle'])


def load_scale_event(event_dict, element):
    return Events.ScaleEvent(event_dict['start_frame'], event_dict['end_frame'], element, tuple(event_dict['new_size']))


def load_letter_by_letter_event(event_dict, element):
    return Events.LetterByLetterEvent(event_dict['start_frame'], event_dict['end_frame'], element, event_dict['first_letter_id'], event_dict['end_letter_id'], event_dict['font_size'])


def load_run_multiple_time_event(event_dict, element):
    return Events.RunFuncMultipleTimeEvent(event_dict['start_frame'], event_dict['end_frame'], element)


def load_show_event(event_dict, element):
    return Events.ShowEvent(event_dict['frame'], element)


def load_hide_event(event_dict, element):
    return Events.HideEvent(event_dict['frame'], element)


def load_rerder_event(event_dict, element):
    return Events.RenderText(event_dict['frame'], element, event_dict['font_size'])


def load_run_event(event_dict, element):
    return Events.RunFuncEvent(event_dict['frame'], element)


def load_play_sfx_event(event_dict, element):
    return Events.PlaySfxEvent(event_dict['frame'], element)


def load_play_intro_plus_music_event(event_dict, element):
    return Events.PlayMusicWithIntroEvent(event_dict['frame'], element, event_dict["looping"])


def load_music_stop_event(event_dict, element):
    return Events.MusicStopEvent(event_dict['frame'], element)


def load_music_fade_out_event(event_dict, element):
    return  Events.MusicStopFadeOutEvent(event_dict['frame'], element, event_dict['fade_duration'])


def load_play_music_event(event_dict, element):
    return Events.PlayMusicEvent(event_dict['frame'], element, event_dict["looping"])


def load_unload_music_event(event_dict, element):
    return Events.MusicUnloadEvent(event_dict['frame'], element)


def load_play_event(event_dict, element):
    return Events.PlayEvent(event_dict['frame'], element, event_dict['speed'])

def load_flip_event(event_dict, element):
    return Events.FlipEvent(event_dict['frame'], element, event_dict['h'], event_dict['v'])


load_event_func = {
    "Se déplacer vers": load_move_to_event,
    "Changer l'opacité": load_fade_event,
    "Pivoter":load_rotate_event,
    "Changer la taille": load_scale_event,
    "Afficher lettre par lettre": load_letter_by_letter_event,
    "Run à la suite": load_run_multiple_time_event,
    "Montrer": load_show_event,
    "Cacher": load_hide_event,
    "Convertir en image": load_rerder_event,
    "Run": load_run_event,
    "Jouer (Sfx)": load_play_sfx_event,
    "Jouer (Intro + Musique)": load_play_intro_plus_music_event,
    "Stop": load_music_stop_event,
    "Stop en fondu": load_music_fade_out_event,
    "Jouer (Musique)": load_play_music_event,
    "Unload": load_unload_music_event,
    "Play": load_play_event,
    "Flip": load_flip_event
}


class CutsceneElement:
    def __init__(self,
                 element_type: Events.CutsceneElementType,
                 pos_initial: tuple[float, float] = (0, 0),
                 sprite_path: str = None,
                 text: str = None,
                 font_path: str = None,
                 initial_visibility=None,
                 function=None,
                 music_path=None,
                 intro_music_path=None,
                 sfx_path=None,
                 sprite_sheet_direction: bool = False,
                 sprite_sheet_width_limit: int = -1,
                 sprite_sheet_height_limit: int = -1
                 ):
        self.type = element_type
        self.pos = list(pos_initial)
        self.drawing = True
        self.opacity = 255
        if self.type in (Events.CutsceneElementType.SPRITE, Events.CutsceneElementType.NON_RENDER_TEXT, Events.CutsceneElementType.ANIMATED_SPRITE):
            self.angle = 0
            if self.type in (Events.CutsceneElementType.SPRITE, Events.CutsceneElementType.ANIMATED_SPRITE):
                assert sprite_path is not None, "Sprite Missing"
                assert initial_visibility is not None, "Visibility no specified"
                self.drawing = initial_visibility
                if self.type == Events.CutsceneElementType.ANIMATED_SPRITE:
                    self.sprite = animated_sprite(sprite_path, sprite_sheet_direction,
                                                  width=sprite_sheet_width_limit, height=sprite_sheet_height_limit)

                else:
                    self.sprite = pygame.image.load(sprite_path).convert_alpha()
                    self.scaled_sprite = self.sprite
                    self.rotated_sprite = self.sprite
                    self.draw_sprite = self.sprite
                self.scale = self.sprite.get_size()
            else:
                assert text is not None and font_path is not None, f"{'Text' if text is None and not font_path is None else 'Font' if font_path is None and not text is None else 'Text and font'} missing"
                self.text = text
                self.font_path = font_path
        elif self.type == Events.CutsceneElementType.FUNC:
            self.function = function
        elif self.type == Events.CutsceneElementType.SFX:
            assert sfx_path is not None, "Element lacking"
            self.sfx = pygame.mixer.Sound(sfx_path)
        elif self.type == Events.CutsceneElementType.MUSIC_WITH_INTRO:
            assert music_path is not None and intro_music_path is not None, "Element lacking"
            self.music_intro = intro_music_path
            self.main_loop = music_path
        elif self.type == Events.CutsceneElementType.MUSIC:
            assert music_path is not None, "Element lacking"
            self.main_loop = music_path

        if self.type == Events.CutsceneElementType.SPRITE:
            self.draw_sprite = self.sprite
        else:
            self.draw_sprite = None

        self.event_list = []
        self.playing_events = []

    def update(self, current_frame):
        for event in self.event_list:
            if event.start_frame == current_frame:
                self.playing_events.append(event)
        # Update

        for event in self.playing_events:
            event.update()

        backup = []

        for i in range(len(self.playing_events)):
            if self.playing_events[i].end_frame == current_frame:
                backup.append(i)

        backup.sort(reverse=True)

        for elt in backup:
            self.playing_events.pop(elt)

    def add_event(self, event: Events.Event):
        self.event_list.append(event)

    def add_event_from_list(self, *event_list: Events.Event):
        for event in event_list:
            self.event_list.append(event)

    def draw(self, screen_buffer: pygame.Surface):
            if self.type == Events.CutsceneElementType.ANIMATED_SPRITE:
                if self.drawing and not self.opacity == 0:
                    self.sprite.set_alpha(self.opacity)
                self.sprite.draw(screen_buffer, self.pos)
            elif self.draw_sprite is not None:
                if self.drawing and not self.opacity == 0:
                    screen_buffer.blit(self.draw_sprite, self.pos)
                self.draw_sprite.set_alpha(self.opacity)


class Cutscene:
    def __init__(self, duration: int = 0, element_list: list[CutsceneElement] = None):
        self.playing = False
        self.progress = 0
        self.duration = duration
        if element_list is None:
            self.__element = []
        else:
            self.__element = element_list

    def load_from_json_dict(self, json_dict: dict):
        self.__element = []
        self.progress = 0
        self.duration = json_dict['duration']
        for element in json_dict["element"].values():
            cutscene_element = load_element_func[element['type']](element)
            for event in element['event_dict'].values():
                cutscene_element.add_event(load_event_func[event['type']](event, cutscene_element))
            self.__element.append(cutscene_element)

    def play(self):
        if not self.playing:
            self.playing = True
        for element in self.__element:
            element.update(self.progress)
        if self.duration == self.progress:
            self.playing = False
        self.progress += 1

    def draw(self, screen_buffer):
        for element in self.__element:
            element.draw(screen_buffer)

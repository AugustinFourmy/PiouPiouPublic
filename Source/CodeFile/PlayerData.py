class PlayerDeath:
    def __init__(self, moment: int, cause: str) -> None:
        """Mort du joueur,
        l'argument moment désigne la phase du jeu dans lequels le joueur est mort :
            De 1 à 5, cela désigne les vagues 1 à 5
            6 désigne durant l'affrontement avec l'anguille
        l'argument cause désigne l'attaque qui à tuer le joueur
        """
        self.__moment = moment
        self.__cause = cause

    def __str__(self):
        return f"Mort à la vague {self.__moment} par {self.__cause}"

    def get_moment(self) -> int:
        return self.__moment

    def get_cause(self) -> str:
        return self.__cause


class PlayerData:
    def __init__(self):
        self.__death_list = []
        self.__unlocked_achievement = []
        self.__already_killed_ovni = False
        self.__first_time_overdrive_fragment = True
        self.__current_wave = 1
        self.__current_win_count = 0

    def __str__(self):
        death_list_str = ""
        for i in range(self.get_death_count()):
            death_list_str += "\n\t" + str(self.__death_list[i])
        death_list_str += "\n"

        return f"Partie ou le joueur est mort {self.get_death_count()} fois : {death_list_str} en ayant gagné " \
               f"{self.__current_win_count} fois en ayant été jusqu'à la vague {self.__current_wave}"

    def set_unlocked_list(self, unlock_list: list[bool]):
        self.__unlocked_achievement = unlock_list

    def get_unlock_list(self):
        return self.__unlocked_achievement
    
    def get_current_wave(self) -> int:
        return self.__current_wave

    def get_win_count(self) -> int:
        return self.__current_win_count

    def get_death_count(self) -> int:
        return len(self.__death_list)
    
    def has_already_killed_ovni(self):
        return self.__already_killed_ovni
    
    def killed_ovni(self):
        self.__already_killed_ovni = True

    def get_death(self, identifiant: int) -> PlayerDeath:
        return self.__death_list[identifiant]

    def set_current_wave(self, val: int):
        self.__current_wave = val

    def add_death(self, death):
        self.__death_list.append(death)

    def add_win(self):
        self.__current_win_count += 1

    def set_first_time_of(self, value: bool):
        self.__first_time_overdrive_fragment = value
    
    def get_first_time_overdrive_fragment(self):
        return self.__first_time_overdrive_fragment
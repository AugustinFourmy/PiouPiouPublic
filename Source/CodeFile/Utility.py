import pickle
import os

class Timer:
    def __init__(self, duration, looping=False):
        self.__duration = duration
        self.__time_left = duration
        self.__looping = looping
    
    def tick(self, nb = 1):
        if self.__time_left - nb > -1:
            self.__time_left -= nb
        if self.__time_left <= 0:
            if self.__looping:
                self.__time_left = self.__duration 
            return True
        return False
    
    def cancelTick(self, nb_Tick = 1):
        self.__time_left += nb_Tick
    
    def getTimeLeft(self):
        return self.__time_left
    
    def getDuration(self):
        return self.__duration
    
    def getLooping(self):
        return self.__looping
    
    def setLooping(self, value: bool):
        self.__looping = value
    

    def setDuration(self, value: int):
        self.__duration = value
    
    def restart(self):
        self.__time_left = self.__duration

class SaveLoadHandler:
    def __init__(self, save_path):
        self.save_path = save_path

    def save(self, data):
        save_file = open(self.save_path, "wb")
        pickle.dump(data, save_file)
        save_file.close()

    def has_a_save(self) -> bool:
        return os.path.exists(self.save_path)

    def load(self):
        if self.has_a_save():
            save_file = open(self.save_path, "rb")
            data = pickle.load(save_file)
            save_file.close()
            return data
        return None

def text_sepparator(txt: str, max_line_len: int, max_line_number: int) -> list:
        word_list = txt.split()
        current_line = ""
        line_list = []
        for i in range(len(word_list)):
            if len(current_line) + len(word_list[i]) + 1 <= max_line_len:
                current_line += " " + word_list[i]
            elif len(line_list) < max_line_number:
                line_list.append(current_line)
                current_line = " " + word_list[i]
                i -= 1
        if current_line != "" and len(line_list) < max_line_number:
            line_list.append(current_line)
        return line_list
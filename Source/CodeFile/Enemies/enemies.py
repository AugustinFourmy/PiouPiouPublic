import pygame
from Source.CodeFile.Enemies.Attack import Attack as att

class TirAttaque(att):
    def __init__(self, sprite, bullet_num, speed_x, speed_y):
        att.__init__(self, sprite)
        self.__bullet_num = bullet_num
        self.__speed_x = speed_x
        self.__speed_y = speed_y
    
    def new(self, enemy):
        if self.__bullet_num == 5:
            # Paterne de l'enemi rouge
            self.bullet_list.append((pygame.rect.Rect(enemy.x + 50, enemy.y + 5, 10, (233 / 53) * 10), (self.__speed_x, self.__speed_y)))  # Diagonal droite
            self.bullet_list.append((pygame.rect.Rect(enemy.x + 50, enemy.y + 5, 10, (233 / 53) * 10), (-self.__speed_x, self.__speed_y)))  # Diagonal gauche
            self.bullet_list.append((pygame.rect.Rect(enemy.x + 50, enemy.y + 5, 10, (233 / 53) * 10), (2 * self.__speed_x, self.__speed_y)))  # Diagonale lointaine droite
            self.bullet_list.append((pygame.rect.Rect(enemy.x + 50, enemy.y + 5, 10, (233 / 53) * 10), (-2 * self.__speed_x, self.__speed_y)))  # Diagonale lointaine gauche
            self.bullet_list.append((pygame.rect.Rect(enemy.x + 50, enemy.y + 5, 10, (233 / 53) * 10), (0, self.__speed_y)))  # Tire droit
        elif self.__bullet_num == 3:
            # Paterne de l'ennemi jaune
            self.bullet_list.append((pygame.rect.Rect(enemy.x + 50, enemy.y + 5, 10, (233 / 53) * 10), (self.__speed_x, self.__speed_y)))  # Diagonal droite
            self.bullet_list.append((pygame.rect.Rect(enemy.x + 50, enemy.y + 5, 10, (233 / 53) * 10), (-self.__speed_x, self.__speed_y)))  # Diagonal gauche
            self.bullet_list.append((pygame.rect.Rect(enemy.x + 50, enemy.y + 5, 10, (233 / 53) * 10), (0, self.__speed_y)))  # Tire droit
        else:
            self.bullet_list.append((pygame.rect.Rect(enemy.x + 50, enemy.y + 5, 10, (233 / 53) * 10), (self.__speed_x, self.__speed_y)))
            
    def update(self, player):
        off_screens = []  

        for i in range(len(self.bullet_list)):
            self.bullet_list[i][0].x += self.bullet_list[i][1][0]  # On ajoute la velocite horizontal a la coordone x du rectangle de la balle
            self.bullet_list[i][0].y += self.bullet_list[i][1][1]  # On ajoute la velocite vertical a la coordone y du rectangle de la balle
            if 800 < self.bullet_list[i][0].y or self.bullet_list[i][0].y < -20 or 660 < self.bullet_list[i][0].x or self.bullet_list[i][0].x < -20:
                # Si la balle est en dehors des bornes de l'ecran on l'ajoute a la liste qui servira a la supprimer
                off_screens.append(i)

        off_screens.sort(reverse=True) 
        for elt in off_screens:# Pour tous les elements de la liste de disparition
            self.bullet_list.pop(elt)
        
        backup = []  # liste qui va stocker les balles ennemis qui vont disparaitre

        for i in range(len(self.bullet_list)):  # Parcours toutes les balles ennemis
            if self.bullet_list[i][0].colliderect(player.colision_rect):  # Si la balle touche alors que le joueur n'est pas invinsible
                player.take_damage(1, 60, f"AttBasic{self.__bullet_num}")
                backup.append(i)  # On ajoute l'indice de la balle qui a toucher le joueur a la liste de disparition (backup)

        backup.sort(reverse=True)  # On inverse tri les valeur dans l'ordre decroissant pour faire disparaitre celle avec la valeur la plus haute d'abord (sinon il y a une erreur pop index out of range)

        for elt in backup:  # Pour tous les elements de la liste de disparition
            self.bullet_list.pop(elt)  # On supprime la balles d'indice elt
    
    def clean(self):
        self.bullet_list = []



class Enemy:
    def __init__(self, hp: int, colonne: int, color: str, rect_pos: tuple[int, int], rect_size: tuple[int, int], shoot_delais):
        self.colonne = colonne
        self.max_hp = hp
        self.hp = hp
        self.x = colonne * 106
        self.y = 5
        self.is_invincible = False
        self.invincibility_timer = 0
        self.color = color
        self.base_timer = shoot_delais
        self.timer = self.base_timer
        self.collision_rect = pygame.rect.Rect(rect_pos[0], rect_pos[1], rect_size[0], rect_size[1])
        
    def move(self):
        self.y += 1
        self.collision_rect.y = self.y

    def take_damage(self, invincibility_timer: int) -> bool:
        self.hp -= 1
        self.is_invincible = True
        self.invincibility_timer = invincibility_timer
        return self.hp == 0

    def invincibility_decrease(self):
        self.invincibility_timer -= 1
        if self.invincibility_timer == 0:
            self.is_invincible = False
        

class Alien(Enemy):
    def __init__(self, max_hp: int, colonne: int, shoot_delais: int, hard_y: int=6) -> None:
        color = '#00EA4E' if max_hp == 10 else '#FFFF00' if max_hp == 20 else '#800D0D'
        Enemy.__init__(self, max_hp, colonne, color, (colonne * 106 + 1, hard_y), (102, 53), shoot_delais)
        self.actual_sprite = 0 if max_hp == 10 else 1 if max_hp == 20 else 2
        self.base_sprite = self.actual_sprite

    def __str__(self):
        return f"Alien avec {self.hp} pv"



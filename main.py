import pyxel

WIDTH = 256
HEIGHT = 256
HAUT, BAS, GAUCHE, DROITE = 0, 1, 2, 3



class Sprite:
    def __init__(self, x, y, u, v, w, h, colkey=pyxel.COLOR_PURPLE):
        self.x, self.y = x, y
        self.u, self.v = u, v
        self.w, self.h = w, h
        self.colkey = colkey
    
    def collision(self, sprite):
        x11, x12, y11, y12 = self.x, self.x + self.w, self.y, self.y + self.h
        x21, x22, y21, y22 = sprite.x, sprite.x + sprite.w, sprite.y, sprite.y + sprite.h
        return (x11 < x22 and x12 > x21 and y11 < y22 and y12 > y21)
    
    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.u, self.v, self.w, self.h, self.colkey)


class Personnage(Sprite):
    def __init__(self, x, y, u, v, w, h, vitesse_max=1, vitesse=0.2, colkey=pyxel.COLOR_PURPLE):
        super().__init__(x, y, u, v, w, h, colkey)
        self.vitesse_max = vitesse_max
        self.gravity = 0.3
        self.vitesse = vitesse
        self.dx, self.dy = 0, 0
    
    def deplacer(self, direction):
        if direction == GAUCHE and -self.vitesse_max<self.dx :
            self.dx -= self.vitesse
        elif direction == DROITE and self.dx<self.vitesse_max :
            self.dx += self.vitesse
    
    def update(self) :
        if self.dx > 0:
            self.dx -= self.vitesse
        elif self.dx < 0:
            self.dx += self.vitesse
        
        if ... :
            self.y -= self.gravity


class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Plataforma!", fps=60)
        pyxel.load("2.pyxres")
        
        self.sprite = Sprite(20, 20, 0, 16, 16, 16)
        
        pyxel.run(self._update, self._draw)
    
    def _update(self):
        pass
    
    def _draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        self.sprite.draw()


App()

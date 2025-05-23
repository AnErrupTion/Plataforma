import pyxel

WIDTH = 256
HEIGHT = 256
HAUT, BAS, GAUCHE, DROITE = 0, 1, 2, 3


class Sprite:
    def __init__(self, x, y, u, v, colkey=pyxel.COLOR_PURPLE):
        self.x, self.y = x, y
        self.u, self.v = u, v
        self.w, self.h = 16, 16
        self.colkey = colkey

    def collision(self, sprite):
        x11, x12, y11, y12 = self.x, self.x + self.w, self.y, self.y + self.h
        x21, x22, y21, y22 = (
            sprite.x,
            sprite.x + sprite.w,
            sprite.y,
            sprite.y + sprite.h,
        )
        return x11 < x22 and x12 > x21 and y11 < y22 and y12 > y21

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.u, self.v, self.w, self.h, self.colkey)


class Personnage(Sprite):
    def __init__(self, x, y, u, v, vitesse_max, vitesse):
        super().__init__(x, y, u, v)
        self.vitesse_max = vitesse_max
        self.gravity = 0.3
        self.vitesse = vitesse
        self.dx, self.dy = 0, 0

    def deplacer(self, direction):
        if direction == GAUCHE and -self.vitesse_max < self.dx:
            if self.w > 0:
                self.w = -self.w
            self.dx -= self.vitesse
        elif direction == DROITE and self.dx < self.vitesse_max:
            if self.w < 0:
                self.w = -self.w
            self.dx += self.vitesse

    def update(self):
        if self.dx > 0:
            self.dx -= self.vitesse - 0.1
        elif self.dx < 0:
            self.dx += self.vitesse - 0.1

        # if ...:
        #     self.y -= self.gravity

        self.x += round(self.dx)
        self.y += round(self.dy)


class Collectible(Sprite):
    def __init__(self, x, y, u, v):
        super().__init__(x, y, u, v)

    def ramasser(self, joueur, niveau):
        print("Collectible ramassé !")
        niveau.collectibles.remove(self)


class Piece(Collectible):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 48)

    def ramasser(self, joueur, niveau):
        joueur.score += 1
        return super().ramasser(joueur, niveau)


class Plateforme(Sprite):
    def __init__(self, x, y, u, v, colkey=pyxel.COLOR_PURPLE):
        super().__init__(x, y, u, v, colkey)

    def est_en_collision(self, joueur):
        return self.joueur.collision(self)


class Joueur(Personnage):
    def __init__(self, x, y):
        super().__init__(x, y, 0, 16, 2, 0.4)

    def update(self):
        super().update()

        if pyxel.btn(pyxel.KEY_LEFT):
            self.deplacer(GAUCHE)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.deplacer(DROITE)


class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Plataforma!", fps=60)
        pyxel.load("2.pyxres")

        self.joueur = Joueur(64, 64)

        pyxel.run(self._update, self._draw)

    def _update(self):
        self.joueur.update()

    def _draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        self.joueur.draw()


App()

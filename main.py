import pyxel

WIDTH = 256
HEIGHT = 256
HAUT, BAS, GAUCHE, DROITE = 0, 1, 2, 3
TILE_COLLISION = [(i, j) for i in range(0, 5) for j in range(12, 14)]

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
    def __init__(self, x, y, u, v, level, vitesse_max, vitesse):
        super().__init__(x, y, u, v)
        self.vitesse_max = vitesse_max
        self.gravity = 2
        self.vitesse = vitesse
        self.dx, self.dy = 0, 0
        self.level = level
        self.saute = False
        self.saut_timer = 0
        self.is_grounded = False

    def sauter(self):
        if self.is_grounded:
            self.saute = True
            self.saut_timer = 0
    
    def saut_update(self):
        if self.saute and (self.saut_timer > 32 or not self.peut_deplacer(HAUT)):
            self.saute = False
            self.saut_timer = 0
        if self.saute:
            self.dy = -self.gravity
            self.saut_timer += 1

    def peut_deplacer(self, direction) :
        if direction == BAS :
            if self.level.tilemap.pget(self.x//8, (self.y+self.h)//8) in TILE_COLLISION or self.level.tilemap.pget((self.x+self.w-1)//8, (self.y+self.h)//8) in TILE_COLLISION:
                return False
        elif direction == HAUT :
            if self.level.tilemap.pget(self.x//8, self.y//8) in TILE_COLLISION or self.level.tilemap.pget((self.x+self.w-1)//8, self.y//8) in TILE_COLLISION :
                return False
        elif direction == GAUCHE :
            if self.level.tilemap.pget(self.x//8, self.y//8) in TILE_COLLISION or self.level.tilemap.pget(self.x//8, (self.y+self.h-1)//8) in TILE_COLLISION:
                return False
        elif direction == DROITE :
            if self.level.tilemap.pget((self.x+self.w)//8, self.y//8) in TILE_COLLISION or self.level.tilemap.pget((self.x+self.w)//8, (self.y+self.h-1)//8) in TILE_COLLISION:
                return False
        return True

    def deplacer(self, direction):
        if direction == GAUCHE and -self.vitesse_max < self.dx and self.peut_deplacer(GAUCHE):
            if self.w > 0:
                self.w = -self.w
            self.dx = round(self.dx-self.vitesse, 1)
        elif direction == DROITE and self.dx < self.vitesse_max and self.peut_deplacer(DROITE):
            if self.w < 0:
                self.w = -self.w
            self.dx = round(self.dx+self.vitesse, 1)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        
        if self.dx > 0:
            self.dx = round(self.dx-0.2, 1)
        elif self.dx < 0:
            self.dx = round(self.dx+0.2, 1)

        if self.peut_deplacer(BAS):
            self.is_grounded = False
            self.dy = self.gravity
        
        if not self.peut_deplacer(HAUT) or not self.peut_deplacer(BAS):
            self.is_grounded = True
            self.dy = 0
        
        self.saut_update()



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
    def __init__(self, x, y, level):
        super().__init__(x, y, 0, 16, level, 2, 0.4)

    def update(self):
        super().update()

        if pyxel.btn(pyxel.KEY_LEFT):
            self.deplacer(GAUCHE)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.deplacer(DROITE)
        if pyxel.btnp(pyxel.KEY_UP):
            self.sauter()


class Niveau:
    def __init__(self, tilemap, collectibles, plateformes):
        self.tilemap = pyxel.tilemap(tilemap)
        self.collectibles = collectibles
        self.plateformes = plateformes
        self.tilemap.load(0, 0, "2.pyxres", 0)

    def draw(self):
        pyxel.bltm(0, 0, self.tilemap, 0, 0, 64 * 8, 32 * 8)


class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Plataforma!", fps=60)
        pyxel.load("2.pyxres")

        self.niveau = Niveau(0, [], [])
        self.joueur = Joueur(64, 64, self.niveau)

        pyxel.run(self._update, self._draw)

    def _update(self):
        self.joueur.update()

    def _draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)
        self.niveau.draw()
        self.joueur.draw()


App()

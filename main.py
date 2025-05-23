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
        x11, x12, y11, y12 = self.x, self.x + abs(self.w), self.y, self.y + abs(self.h)
        x21, x22, y21, y22 = (
            sprite.x,
            sprite.x + abs(sprite.w),
            sprite.y,
            sprite.y + abs(sprite.h),
        )
        return x11 < x22 and x12 > x21 and y11 < y22 and y12 > y21

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.u, self.v, self.w, self.h, self.colkey)


class Personnage(Sprite):
    def __init__(self, x, y, u, v, level, nb_frames, vitesse_max, vitesse):
        super().__init__(x, y, u, v)
        self.vitesse_max = vitesse_max
        self.gravity = 2
        self.vitesse = vitesse
        self.dx, self.dy = 0, 0
        self.level = level
        self.saute = False
        self.saut_timer = 0
        self.is_grounded = False
        self.uorig = u
        self.umax = nb_frames * 16

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

    def peut_deplacer(self, direction):
        if direction == BAS:
            if (
                self.level.tilemap.pget(self.x // 8, (self.y + self.h) // 8)
                in TILE_COLLISION
                or self.level.tilemap.pget(
                    (self.x + self.w - 1) // 8, (self.y + self.h) // 8
                )
                in TILE_COLLISION
            ):
                return False
        elif direction == HAUT:
            if (
                self.level.tilemap.pget(self.x // 8, self.y // 8) in TILE_COLLISION
                or self.level.tilemap.pget((self.x + self.w - 1) // 8, self.y // 8)
                in TILE_COLLISION
            ):
                return False
        elif direction == GAUCHE:
            if (
                self.level.tilemap.pget(self.x // 8, self.y // 8) in TILE_COLLISION
                or self.level.tilemap.pget(self.x // 8, (self.y + self.h - 1) // 8)
                in TILE_COLLISION
            ):
                return False
        elif direction == DROITE:
            if (
                self.level.tilemap.pget((self.x + self.w) // 8, self.y // 8)
                in TILE_COLLISION
                or self.level.tilemap.pget(
                    (self.x + self.w) // 8, (self.y + self.h - 1) // 8
                )
                in TILE_COLLISION
            ):
                return False
        return True

    def deplacer(self, direction):
        if pyxel.frame_count % 10 == 0:
            self.u = (self.u + 16) % self.umax

        if (
            direction == GAUCHE
            and -self.vitesse_max < self.dx
            and self.peut_deplacer(GAUCHE)
        ):
            if self.w > 0:
                self.w = -self.w
            self.dx = round(self.dx - self.vitesse, 1)
        elif (
            direction == DROITE
            and self.dx < self.vitesse_max
            and self.peut_deplacer(DROITE)
        ):
            if self.w < 0:
                self.w = -self.w
            self.dx = round(self.dx + self.vitesse, 1)

    def update(self, joueur, niveau):
        if 0 <= self.x + self.dx <= WIDTH - abs(self.w):
            self.x += self.dx
        if 0 <= self.y + self.dy <= HEIGHT - abs(self.h):
            self.y += self.dy

        if self.dx > 0:
            self.dx = round(self.dx - 0.2, 1)
        elif self.dx < 0:
            self.dx = round(self.dx + 0.2, 1)

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

    def update(self, joueur, niveau):
        if joueur.collision(self):
            self._ramasser(joueur, niveau)
            niveau.objets.remove(self)

    def _ramasser(self, joueur, niveau):
        pass


class Piece(Collectible):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 48)

    def _ramasser(self, joueur, niveau):
        print("Pièce ramassée !")
        joueur.score += 1


class Interactible(Sprite):
    def __init__(self, x, y, u, v, touche):
        self.touche = touche
        self.interagis = False
        super().__init__(x, y, u, v)

    def update(self, joueur, niveau):
        if pyxel.btnp(self.touche) and not self.interagis:
            self._interaction()
            self.interagis = True

    def _interaction(self):
        pass


class Coffre(Interactible):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 32, pyxel.KEY_E)

    def _interaction(self):
        print("Interagis avec un coffre !")
        return super()._interaction()


class Joueur(Personnage):
    def __init__(self, x, y, level, vie):
        self.vie = vie
        self.score = 0
        super().__init__(x, y, 0, 16, level, 4, 2, 0.4)

    def update(self, joueur, niveau):
        super().update(joueur, niveau)

        appuye = False
        if pyxel.btn(pyxel.KEY_LEFT):
            self.deplacer(GAUCHE)
            appuye = True
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.deplacer(DROITE)
            appuye = True
        if pyxel.btnp(pyxel.KEY_UP):
            self.sauter()
            appuye = True

        if not appuye:
            self.u = self.uorig


class Monstre(Personnage):
    def __init__(self, x, y, u, v, level, nb_frames, vitesse_max, vitesse, degats):
        self.degats = degats
        super().__init__(x, y, u, v, level, nb_frames, vitesse_max, vitesse)


class Projectile(Sprite):
    def __init__(self, x, y, u, v, direction, vitesse, degats):
        self.direction = direction
        self.vitesse = vitesse
        self.degats = degats
        super().__init__(x, y, u, v)
        self.w = direction * self.w

    def update(self, joueur, niveau):
        self.x += self.direction * self.vitesse

        if self.collision(joueur):
            joueur.vie -= self.degats
            niveau.objets.remove(self)


class Squelette(Monstre):
    def __init__(self, x, y, level):
        super().__init__(x, y, 64, 16, level, 4, 1.5, 0.3, 1)
        self.wabs = abs(self.w)

    def update(self, joueur, niveau):
        if pyxel.frame_count % 60 == 0 and abs(joueur.x - self.x) < 120:
            direction = -1 if joueur.x < self.x else 1
            self.w = direction * self.wabs

            projectile = Projectile(self.x, self.y, 0, 80, direction, 2, self.degats)
            niveau.objets.append(projectile)

        return super().update(joueur, niveau)


class Coeur(Sprite):
    def __init__(self, camx, camy, num):
        super().__init__(camx + 5 + num * 10, camy + 5, 112, 48)


class Niveau:
    def __init__(self, w, h, tilemap, objets):
        self.w, self.h = w, h
        self.tilemap = pyxel.tilemaps[tilemap]
        self.objets = objets
        self.tilemap.load(0, 0, "2.pyxres", 0)

    def draw(self):
        pyxel.bltm(0, 0, self.tilemap, 0, 0, self.w * 8, self.h * 8)

        for objet in self.objets:
            objet.draw()

    def update(self, joueur):
        for objet in self.objets:
            objet.update(joueur, self)


class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Plataforma!", fps=60)
        pyxel.load("2.pyxres")

        self.niveau = Niveau(64, 32, 0, [])
        self.niveau.objets.append(Squelette(160, 40, self.niveau))

        self.joueur = Joueur(8, 64, self.niveau, 3)
        self.coeur = Sprite(10, 10, 112, 48)

        pyxel.run(self._update, self._draw)

    def _update(self):
        self.niveau.update(self.joueur)
        self.joueur.update(self.joueur, self.niveau)

    def _draw(self):
        camx, camy = self.joueur.x - 20, self.joueur.y - 60

        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        pyxel.camera(camx, camy)

        self.niveau.draw()
        self.joueur.draw()

        for num in range(self.joueur.vie):
            coeur = Coeur(camx, camy, num)
            coeur.draw()


App()

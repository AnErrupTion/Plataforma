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
    def __init__(self, x, y, u, v, level, nb_frames, vitesse_max, vitesse, vie):
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
        self.ucur = 0
        self.umax = nb_frames * 16
        self.vie = vie

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
                    (self.x + abs(self.w) - 1) // 8, (self.y + self.h) // 8
                )
                in TILE_COLLISION
            ):
                return False
        elif direction == HAUT:
            if (
                self.level.tilemap.pget(self.x // 8, self.y // 8) in TILE_COLLISION
                or self.level.tilemap.pget((self.x + abs(self.w) - 1) // 8, self.y // 8)
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
                self.level.tilemap.pget((self.x + abs(self.w)) // 8, self.y // 8)
                in TILE_COLLISION
                or self.level.tilemap.pget(
                    (self.x + abs(self.w)) // 8, (self.y + self.h - 1) // 8
                )
                in TILE_COLLISION
            ):
                return False
        return True

    def deplacer(self, direction):
        if pyxel.frame_count % 10 == 0:
            self.u = self.uorig + self.ucur % self.umax
            self.ucur += 16

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

    def verifie_position(self):
        if self.peut_deplacer(BAS):
            self.is_grounded = False
            self.dy = self.gravity

        if not self.peut_deplacer(HAUT) or not self.peut_deplacer(BAS):
            self.is_grounded = True
            self.dy = 0

        if self.dx > 0 and not self.peut_deplacer(DROITE):
            self.dx = 0
        elif self.dx < 0 and not self.peut_deplacer(GAUCHE):
            self.dx = 0

    def update(self, joueur, niveau):
        self.x += self.dx
        self.y += self.dy

        if self.dx > 0:
            self.dx = round(self.dx - 0.2, 1)
        elif self.dx < 0:
            self.dx = round(self.dx + 0.2, 1)

        self.verifie_position()

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
        joueur.score += 1


class Diamant(Collectible):
    def __init__(self, x, y):
        super().__init__(x, y, 128, 32)

    def _ramasser(self, joueur, niveau):
        joueur.score += 10


class Interactible(Sprite):
    def __init__(self, x, y, u, v, touche):
        self.touche = touche
        self.interagis = False
        super().__init__(x, y, u, v)

    def update(self, joueur, niveau):
        if pyxel.btnp(self.touche) and not self.interagis:
            self._interaction(niveau)
            self.interagis = True

    def _interaction(self, niveau):
        pass


class Coffre(Interactible):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 32, pyxel.KEY_E)
        self.est_ouvert = False

    def _interaction(self, niveau):
        if not self.est_ouvert:
            self.u += 16
        niveau.objets.append(Diamant(self.x, self.y - 24))
        return super()._interaction(niveau)


class Joueur(Personnage):
    def __init__(self, x, y, level):
        self.score = 0
        super().__init__(x, y, 0, 16, level, 4, 2, 0.4, 3)
        self.epee = Epee(self)

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
        if pyxel.btnp(pyxel.KEY_R):
            pyxel.play(0, 4)
            for objet in niveau.objets:
                if isinstance(objet, Monstre) and self.collision(objet):
                    objet.vie -= 1

        if not appuye:
            self.u = self.uorig

    def draw(self):
        super().draw()
        self.epee.draw()


class Monstre(Personnage):
    def __init__(self, x, y, u, v, level, nb_frames, vitesse_max, vitesse, vie, degats):
        self.degats = degats
        super().__init__(x, y, u, v, level, nb_frames, vitesse_max, vitesse, vie)

    def update(self, joueur, niveau):
        super().update(joueur, niveau)

        if self.vie <= 0:
            niveau.objets.remove(self)


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


class Arbalete(Sprite):
    def __init__(self, personnage):
        self.personnage = personnage
        super().__init__(personnage.x + 8, personnage.y, 80, 64)
        self.wabs = abs(self.w)
        direction = 1 if self.personnage.x < self.x else -1
        self.w = direction * self.wabs
        self.uorig = self.u
        self.ucur = 0
        self.umax = 3 * 16
        self.animer = False

    def draw(self):
        if self.animer:
            if pyxel.frame_count % 30 == 0:
                self.u = self.uorig + self.ucur % self.umax
                self.ucur += 16
        else:
            self.u = self.uorig

        self.y = self.personnage.y

        self.x = self.personnage.x + 8
        direction = 1 if self.personnage.x < self.x else -1
        self.w = direction * self.wabs
        return super().draw()


class Epee(Sprite):
    def __init__(self, personnage):
        self.personnage = personnage
        super().__init__(personnage.x + 10, personnage.y, 0, 64)
        self.wabs = abs(self.w)
        direction = 1 if self.personnage.x < self.x else -1
        self.w = direction * self.wabs

    def draw(self):
        self.y = self.personnage.y
        self.x = self.personnage.x + 10
        direction = 1 if self.personnage.x < self.x else -1
        self.w = direction * self.wabs
        return super().draw()


class Squelette(Monstre):
    def __init__(self, x, y, level):
        super().__init__(x, y, 64, 16, level, 4, 1.5, 0.3, 2, 1)
        self.wabs = abs(self.w)
        self.arbalete = Arbalete(self)

    def update(self, joueur, niveau):
        self.arbalete.animer = abs(joueur.x - self.x) < 120
        if pyxel.frame_count % 120 == 0 and self.arbalete.animer:
            direction = -1 if joueur.x < self.x else 1
            self.w = direction * self.wabs

            pyxel.play(0, 3)
            projectile = Projectile(self.x, self.y, 128, 64, direction, 2, self.degats)
            niveau.objets.append(projectile)

        return super().update(joueur, niveau)

    def draw(self):
        super().draw()
        self.arbalete.draw()


class Coeur(Sprite):
    def __init__(self, camx, camy, num):
        super().__init__(camx + num * 10, camy, 112, 48)


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
        pyxel.playm(0, loop=True)

        self.etat = 2

        pyxel.run(self._update, self._draw)

    def _reset(self):
        self.etat = 0
        self.niveau = Niveau(
            64, 32, 0, [Piece(64, 64), Piece(240, 55), Coffre(59 * 8, 0)]
        )
        self.niveau.objets.append(Squelette(20 * 8, 5 * 8, self.niveau))
        self.niveau.objets.append(Squelette(49 * 8, 2 * 8, self.niveau))

        self.joueur = Joueur(8, 64, self.niveau)
        self.coeur = Sprite(10, 10, 112, 48)

    def _update(self):
        if self.etat == 0:
            if self.joueur.vie <= 0 or self.joueur.y >= HEIGHT - 20:
                pyxel.camera(0, 0)
                self.etat = 1
                return

            if self.joueur.score >= 12:
                pyxel.camera(0, 0)
                self.etat = 3
                return

            self.niveau.update(self.joueur)
            self.joueur.update(self.joueur, self.niveau)
        elif self.etat >= 1:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self._reset()

    def _draw(self):
        if self.etat == 0:
            camx, camy = self.joueur.x - 60, self.joueur.y - 60

            pyxel.cls(pyxel.COLOR_NAVY)
            pyxel.camera(camx, camy)

            self.niveau.draw()
            self.joueur.draw()

            for num in range(self.joueur.vie):
                coeur = Coeur(camx, camy, num)
                coeur.draw()

            piece = Piece(camx, camy + 15)
            piece.draw()

            pyxel.text(
                camx + 16,
                camy + 20,
                str(self.joueur.score),
                pyxel.COLOR_WHITE,
            )
        elif self.etat == 1:
            pyxel.cls(pyxel.COLOR_RED)

            texte = "Vous etes mort ! Appuyez sur Espace pour recommencer."
            pyxel.text(
                WIDTH // 2 - (pyxel.FONT_WIDTH * len(texte)) // 2,
                (HEIGHT // 2 - pyxel.FONT_HEIGHT // 2) - 20,
                texte,
                pyxel.COLOR_WHITE,
            )
        elif self.etat == 2:
            pyxel.cls(pyxel.COLOR_NAVY)

            texte = "Plataforma!"
            pyxel.text(
                WIDTH // 2 - (pyxel.FONT_WIDTH * len(texte)) // 2,
                (HEIGHT // 2 - pyxel.FONT_HEIGHT // 2) - 40,
                texte,
                pyxel.COLOR_WHITE,
            )

            texte = "Appuyez sur Espace pour commencer."
            pyxel.text(
                WIDTH // 2 - (pyxel.FONT_WIDTH * len(texte)) // 2,
                HEIGHT // 2 - pyxel.FONT_HEIGHT // 2,
                texte,
                pyxel.COLOR_WHITE,
            )
        elif self.etat == 3:
            pyxel.cls(pyxel.COLOR_GREEN)

            texte = "Vous avez gagne ! Appuyez sur Espace pour recommencer."
            pyxel.text(
                WIDTH // 2 - (pyxel.FONT_WIDTH * len(texte)) // 2,
                (HEIGHT // 2 - pyxel.FONT_HEIGHT // 2) - 20,
                texte,
                pyxel.COLOR_WHITE,
            )


App()

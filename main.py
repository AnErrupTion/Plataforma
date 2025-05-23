import pyxel

WIDTH = 256
HEIGHT = 256


class Sprite:
    def __init__(self, x, y, u, v, w, h, colkey=pyxel.COLOR_PURPLE):
        self.x, self.y = x, y
        self.u, self.v = u, v
        self.w, self.h = w, h
        self.colkey = colkey

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.u, self.v, self.w, self.h, self.colkey)


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

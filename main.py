import pyxel

class Sprite:
    def __init__(self, x, y, u, v, w, h, colkey=2):
        self.x, self.y = x, y
        self.u, self.v = u, v
        self.w, self.h = w, h
        self.colkey = colkey
    
    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.u, self.v, self.w, self.h, self.colkey)

class App:
    def __init__(self):
        pyxel.init(256, 256, title="Plataforma!", fps=60)
        pyxel.run(self._update, self._draw)

    def _update(self):
        pass

    def _draw(self):
        pass


App()

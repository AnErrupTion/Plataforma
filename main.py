import pyxel


class App:
    def __init__(self):
        pyxel.init(256, 256, title="Plataforma!", fps=60)
        pyxel.run(self._update, self._draw)

    def _update(self):
        pass

    def _draw(self):
        pass


App()

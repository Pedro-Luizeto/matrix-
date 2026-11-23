import random
import time
import tkinter.font as tkfont

from config import (
    BG_COLOR, FONT_FAMILY, FONT_SIZE, PALETTES,
    TRAIL_MAX, TRAIL_MIN,
)

GLYPHS = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "アイウエオカキクケコサシスセソタチツテト"
    "ナニヌネノハヒフヘホマミムメモヤユヨラリルレロ"
    "ワヲンЖФЯШЩДЛП"
)


class DigitalRain:
    """Mantém os objetos do Canvas e atualiza apenas o que precisa mudar."""

    def __init__(self, canvas):
        self.canvas = canvas
        self.width = 1
        self.height = 1
        self.speed_factor = 1.0
        self.density = 1.0
        self.palette_name = "Classic"
        self.paused = False

        self.columns = []
        self.last_frame = time.perf_counter()
        self.fps = 0.0
        self._fps_frames = 0
        self._fps_started = self.last_frame

        self.font = tkfont.Font(
            family=FONT_FAMILY, size=FONT_SIZE, weight="bold"
        )
        self.char_width = max(9, self.font.measure("M"))
        self.line_height = FONT_SIZE + 3

        self.canvas.configure(background=BG_COLOR, highlightthickness=0)
        self.canvas.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        width = max(1, event.width)
        height = max(1, event.height)
        if width != self.width or height != self.height:
            self.width, self.height = width, height
            self.rebuild()

    def _make_stream(self, x, initial=False):
        length = random.randint(TRAIL_MIN, TRAIL_MAX)
        stream = {
            "x": x,
            "y": random.uniform(-self.height, self.height) if initial
                 else random.uniform(-self.height, 0),
            "speed": random.uniform(85, 245),
            "length": length,
            "glyphs": [random.choice(GLYPHS) for _ in range(length)],
            "items": [],
            "change_clock": random.uniform(0.025, 0.09),
        }

        palette = PALETTES[self.palette_name]
        for index in range(length):
            color_index = min(
                len(palette) - 1,
                int(index * len(palette) / max(1, length))
            )
            color = palette[color_index]

            # Um halo discreto atrás da cabeça dá sensação de brilho.
            glow = None
            if index == 0:
                glow = self.canvas.create_text(
                    x + 1, -100, text=stream["glyphs"][index],
                    fill="#007D25", font=(FONT_FAMILY, FONT_SIZE + 3, "bold"),
                    tags=("rain",),
                )

            item = self.canvas.create_text(
                x, -100, text=stream["glyphs"][index],
                fill=color, font=(FONT_FAMILY, FONT_SIZE, "bold"),
                tags=("rain",),
            )
            stream["items"].append((item, glow))

        return stream

    def rebuild(self):
        """Reconstrói as colunas apenas quando tamanho/densidade mudam."""
        self.canvas.delete("rain")
        self.columns.clear()

        spacing = max(8, int(self.char_width / self.density))
        count = max(1, self.width // spacing + 1)

        for index in range(count):
            x = index * spacing + spacing // 2
            self.columns.append(self._make_stream(x, initial=True))

    def set_speed(self, value):
        self.speed_factor = max(0.2, min(3.0, float(value)))

    def set_density(self, value):
        value = max(0.5, min(2.0, float(value)))
        if abs(value - self.density) >= 0.04:
            self.density = value
            self.rebuild()

    def set_palette(self, name):
        if name in PALETTES and name != self.palette_name:
            self.palette_name = name
            self.rebuild()

    def reset(self):
        for stream in self.columns:
            stream["y"] = random.uniform(-self.height, 0)
            stream["speed"] = random.uniform(85, 245)
            stream["glyphs"] = [
                random.choice(GLYPHS) for _ in range(stream["glyphs"])
            ]
            for index, (item, glow) in enumerate(stream["items"]):
                self.canvas.itemconfigure(item, text=stream["glyphs"][index])
                if glow:
                    self.canvas.itemconfigure(glow, text=stream["glyphs"][index])

    def toggle_pause(self):
        self.paused = not self.paused
        self.last_frame = time.perf_counter()

    def update(self):
        """Avança a simulação usando delta time, sem recriar itens por quadro."""
        now = time.perf_counter()
        delta = min(now - self.last_frame, 0.05)
        self.last_frame = now

        if not self.paused:
            for stream in self.columns:
                stream["y"] += stream["speed"] * self.speed_factor * delta
                stream["change_clock"] -= delta

                if stream["change_clock"] <= 0:
                    # Troca poucos símbolos por vez, evitando trabalho excessivo.
                    for _ in range(random.randint(1, 3)):
                        index = random.randrange(stream["length"])
                        stream["glyphs"][index] = random.choice(GLYPHS)
                        item, glow = stream["items"][index]
                        self.canvas.itemconfigure(
                            item, text=stream["glyphs"][index]
                        )
                        if glow:
                            self.canvas.itemconfigure(
                                glow, text=stream["glyphs"][index]
                            )
                    stream["change_clock"] = random.uniform(0.025, 0.09)

                for index, (item, glow) in enumerate(stream["items"]):
                    y = stream["y"] - index * self.line_height
                    if y < -self.line_height or y > self.height + self.line_height:
                        self.canvas.coords(item, stream["x"], -100)
                        if glow:
                            self.canvas.coords(glow, stream["x"] + 1, -100)
                        continue

                    self.canvas.coords(item, stream["x"], y)
                    if glow:
                        self.canvas.coords(glow, stream["x"] + 1, y)

                if stream["y"] - stream["length"] * self.line_height > self.height:
                    # Reaproveita os mesmos itens quando a coluna termina.
                    stream["y"] = random.uniform(-self.height * 0.6, -20)
                    stream["speed"] = random.uniform(85, 245)
                    stream["change_clock"] = random.uniform(0.025, 0.09)

        self._update_fps(now)
        return self.fps

    def _update_fps(self, now):
        self._fps_frames += 1
        elapsed = now - self._fps_started
        if elapsed >= 0.5:
            self.fps = self._fps_frames / elapsed
            self._fps_frames = 0
            self._fps_started = now

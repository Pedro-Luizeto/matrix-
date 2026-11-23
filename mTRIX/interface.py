import time
import tkinter as tk
from tkinter import ttk, messagebox

from animation import DigitalRain
from config import BG_COLOR, NEON_GREEN, FRAME_INTERVAL_MS


class MatrixTerminal:
    def __init__(self, root):
        self.root = root
        self.root.title("MATRIX TERMINAL")
        self.root.geometry("1100x700")
        self.root.minsize(720, 480)
        self.root.configure(bg=BG_COLOR)
        self.fullscreen = False
        self.running = True
        self.started_at = time.time()
        self._after_id = None

        self.canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.rain = DigitalRain(self.canvas)

        self._build_overlay()
        self.root.bind("<Escape>", self._escape_fullscreen)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self._show_boot_screen()
        self._schedule_frame()

    def _build_overlay(self):
        self.topbar = tk.Frame(self.root, bg="#061109", padx=16, pady=9)
        self.topbar.place(relx=0.018, rely=0.025, relwidth=0.964)

        tk.Label(
            self.topbar, text="▌ MATRIX TERMINAL  //  DIGITAL RAIN",
            bg="#061109", fg=NEON_GREEN,
            font=("Consolas", 15, "bold"),
        ).pack(side="left")

        self.status_label = tk.Label(
            self.topbar, text="● SYSTEM ONLINE",
            bg="#061109", fg="#56FF8A", font=("Consolas", 9, "bold"),
        )
        self.status_label.pack(side="right", padx=(12, 0))

        self.stats_label = tk.Label(
            self.topbar, text="FPS: --  |  LOCAL TIME: --:--:--",
            bg="#061109", fg="#7DBF91", font=("Consolas", 9),
        )
        self.stats_label.pack(side="right")

        self.controls = tk.Frame(self.root, bg="#061109", padx=12, pady=9)
        self.controls.place(relx=0.018, rely=0.91, relwidth=0.964)

        self.pause_button = self._button(self.controls, "Ⅱ PAUSAR", self.toggle_pause)
        self.pause_button.pack(side="left", padx=3)

        self._button(self.controls, "↻ REINICIAR", self.reset_animation).pack(side="left", padx=3)
        self._button(self.controls, "⛶ TELA CHEIA", self.toggle_fullscreen).pack(side="left", padx=3)

        self._button(self.controls, "SAIR  ×", self.close).pack(side="right", padx=3)

        tk.Label(self.controls, text="VELOCIDADE", bg="#061109", fg="#79C98D",
                 font=("Consolas", 8, "bold")).pack(side="left", padx=(18, 3))
        self.speed_scale = tk.Scale(
            self.controls, from_=0.3, to=2.5, resolution=0.1,
            orient="horizontal", length=105, showvalue=False,
            bg="#061109", fg=NEON_GREEN, troughcolor="#12351C",
            highlightthickness=0, command=self.rain.set_speed,
        )
        self.speed_scale.set(1.0)
        self.speed_scale.pack(side="left")

        tk.Label(self.controls, text="DENSIDADE", bg="#061109", fg="#79C98D",
                 font=("Consolas", 8, "bold")).pack(side="left", padx=(10, 3))
        self.density_scale = tk.Scale(
            self.controls, from_=0.6, to=1.8, resolution=0.1,
            orient="horizontal", length=95, showvalue=False,
            bg="#061109", fg=NEON_GREEN, troughcolor="#12351C",
            highlightthickness=0, command=self.rain.set_density,
        )
        self.density_scale.set(1.0)
        self.density_scale.pack(side="left")

        tk.Label(self.controls, text="COR", bg="#061109", fg="#79C98D",
                 font=("Consolas", 8, "bold")).pack(side="left", padx=(10, 3))
        self.palette_box = ttk.Combobox(
            self.controls, values=("Classic", "Emerald", "Toxic"),
            state="readonly", width=9, font=("Consolas", 8),
        )
        self.palette_box.set("Classic")
        self.palette_box.bind("<<ComboboxSelected>>",
                              lambda event: self.rain.set_palette(self.palette_box.get()))
        self.palette_box.pack(side="left")

    def _button(self, parent, text, command):
        return tk.Button(
            parent, text=text, command=command,
            bg="#0B2412", fg=NEON_GREEN, activebackground="#164522",
            activeforeground="#FFFFFF", relief="flat", bd=0,
            padx=10, pady=6, cursor="hand2", font=("Consolas", 8, "bold"),
        )

    def _show_boot_screen(self):
        self.boot_title = self.canvas.create_text(
            0, 0, text="INITIALIZING MATRIX",
            fill=NEON_GREEN, font=("Consolas", 18, "bold"), tags=("boot",),
        )
        self.boot_subtitle = self.canvas.create_text(
            0, 0, text="Carregando módulos do sistema...",
            fill="#4DAF68", font=("Consolas", 10), tags=("boot",),
        )
        self.boot_progress = self.canvas.create_text(
            0, 0, text="[                    ] 0%",
            fill="#00C832", font=("Consolas", 10), tags=("boot",),
        )
        self._boot_step = 0
        self._boot_tick()

    def _boot_tick(self):
        if not self.running:
            return
        self._boot_step += 1
        progress = min(100, self._boot_step * 10)
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        self.canvas.coords(self.boot_title, width / 2, height / 2 - 35)
        self.canvas.coords(self.boot_subtitle, width / 2, height / 2 + 2)
        filled = progress // 5
        bar = "[" + "█" * filled + " " * (20 - filled) + f"] {progress}%"
        self.canvas.itemconfigure(self.boot_progress, text=bar)
        self.canvas.coords(self.boot_progress, width / 2, height / 2 + 30)
        if self._boot_step >= 10:
            self.canvas.delete("boot")
        else:
            self.root.after(110, self._boot_tick)

    def _schedule_frame(self):
        if self.running:
            self._after_id = self.root.after(FRAME_INTERVAL_MS, self._frame)

    def _frame(self):
        if not self.running:
            return
        fps = self.rain.update()
        clock = time.strftime("%H:%M:%S")
        self.stats_label.configure(text=f"FPS: {fps:04.1f}  |  LOCAL TIME: {clock}")
        self.status_label.configure(
            text="Ⅱ SYSTEM PAUSED" if self.rain.paused else "● SYSTEM ONLINE",
            fg="#F4D35E" if self.rain.paused else "#56FF8A",
        )
        self._schedule_frame()

    def toggle_pause(self):
        self.rain.toggle_pause()
        self.pause_button.configure(text="▶ CONTINUAR" if self.rain.paused else "Ⅱ PAUSAR")

    def reset_animation(self):
        self.rain.reset()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        return "break"

    def _escape_fullscreen(self, event=None):
        if self.fullscreen:
            self.fullscreen = False
            self.root.attributes("-fullscreen", False)
        return "break"

    def close(self):
        if not self.running:
            return
        self.running = False
        if self._after_id is not None:
            try:
                self.root.after_cancel(self._after_id)
            except tk.TclError:
                pass
        self.root.destroy()

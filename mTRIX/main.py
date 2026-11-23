import tkinter as tk
from tkinter import messagebox

from interface import MatrixTerminal


def main():
    root = tk.Tk()
    try:
        MatrixTerminal(root)
        root.mainloop()
    except tk.TclError as error:
        messagebox.showerror(
            "Matrix Terminal",
            f"Não foi possível iniciar a interface gráfica:\n{error}",
        )


if __name__ == "__main__":
    main()

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np


def wczytaj_dane_z_pliku(plik):
    zbiory_punktow = []
    aktualny_zbior = []

    with open(plik, 'r') as f:
        for linia in f:
            linia = linia.strip()
            if not linia:
                if aktualny_zbior:
                    zbiory_punktow.append(aktualny_zbior)
                    aktualny_zbior = []
            else:
                dx, dy, dz = map(float, linia.split(','))
                aktualny_zbior.append((dx, dy, dz))
        
        if aktualny_zbior:
            zbiory_punktow.append(aktualny_zbior)

    return zbiory_punktow


def przekszt(zbiory_punktow, ex, ey, ez, theta_x, theta_y, theta_z, zoom):
    wynik = []

    tx = np.radians(theta_x)
    ty = np.radians(theta_y)
    tz = np.radians(theta_z)

    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(tx), np.sin(tx)],
        [0, -np.sin(tx), np.cos(tx)]
    ])

    Ry = np.array([
        [np.cos(ty), 0, -np.sin(ty)],
        [0, 1, 0],
        [np.sin(ty), 0, np.cos(ty)]
    ])

    Rz = np.array([
        [np.cos(tz), np.sin(tz), 0],
        [-np.sin(tz), np.cos(tz), 0],
        [0, 0, 1]
    ])

    S = np.array([
        [zoom, 0, 0],
        [0, zoom, 0],
        [0, 0, 1]
    ])

    R = Rx @ Ry @ Rz

    C = np.array([ex, ey, ez])

    z_clip = 0.01

    for zbior in zbiory_punktow:
        transformed = []

        for dx, dy, dz in zbior:
            a = np.array([dx, dy, dz])
            d = a + C
            d_rot = S @ (R @ d)
            transformed.append(d_rot)  # 3D punkt po transformacji

        indeksy = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]

        proste = []

        for i1, i2 in indeksy:
            if i1 >= len(transformed) or i2 >= len(transformed):
                continue

            p1 = transformed[i1]
            p2 = transformed[i2]
            z1, z2 = p1[2], p2[2]

            if z1 <= 0 and z2 <= 0:
                continue

            if z1 <= z_clip or z2 <= z_clip:
                t = (z_clip - z1) / (z2 - z1)
                clip_point = p1 + t * (p2 - p1)

                if z1 < z_clip:
                    p1 = clip_point
                else:
                    p2 = clip_point

            x1, y1 = p1[0] / abs(p1[2]), p1[1] / abs(p1[2])
            x2, y2 = p2[0] / abs(p2[2]), p2[1] / abs(p2[2])
            proste.append(((x1, y1), (x2, y2)))
        wynik.append(proste)
    return wynik


class Aplikacja:
    def __init__(self, master, original_data):
        self.master = master
        self.master.title("Wyświetlacz")
        self.original_data = original_data
        self.ey = 0
        self.ex = 0
        self.ez = 0
        self.theta_x = 0
        self.theta_y = 0
        self.theta_z = 0
        self.zoom = 1

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack()

        # Przycisk do zmiany widoku
        frame = tk.Frame(master)
        frame.pack()

        tk.Button(frame, text="↑", command=self.up).grid(row=0, column=1)
        tk.Button(frame, text="↓", command=self.down).grid(row=2, column=1)
        tk.Button(frame, text="←", command=self.left).grid(row=1, column=0)
        tk.Button(frame, text="→", command=self.right).grid(row=1, column=2)
        tk.Button(frame, text="⇑", command=self.front).grid(row=0, column=6)
        tk.Button(frame, text="⇓", command=self.back).grid(row=2, column=6)
        tk.Button(frame, text="rx+", command=self.rxup).grid(row=0, column=7)
        tk.Button(frame, text="rx-", command=self.rxdown).grid(row=2, column=7)
        tk.Button(frame, text="ry+", command=self.ryup).grid(row=0, column=8)
        tk.Button(frame, text="ry-", command=self.rydown).grid(row=2, column=8)
        tk.Button(frame, text="rz+", command=self.rzup).grid(row=0, column=9)
        tk.Button(frame, text="rz-", command=self.rzdown).grid(row=2, column=9)
        tk.Button(frame, text="zoom+", command=self.zoomup).grid(row=0, column=9)
        tk.Button(frame, text="zoom-", command=self.zoomdown).grid(row=2, column=9)
        

        self.odswiez_dane()
        self.rysuj()

    def odswiez_dane(self):
        self.dane = przekszt(self.original_data, self.ex, self.ey, self.ez, self.theta_x, self.theta_y, self.theta_z, self.zoom)

    def rysuj(self):
        self.ax.clear()

        for bryla in self.dane:
            for x1, x2 in bryla:
                self.ax.plot([x1[0], x2[0]], [x1[1], x2[1]], color='blue')

        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(-5, 5)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.canvas.draw()

    def up(self):
        self.ey -= 1
        self.odswiez_dane()
        self.rysuj()

    def down(self):
        self.ey += 1
        self.odswiez_dane()
        self.rysuj()

    def left(self):
        self.ex += 1
        self.odswiez_dane()
        self.rysuj()

    def right(self):
        self.ex -= 1
        self.odswiez_dane()
        self.rysuj()

    def front(self):
        self.ez -= 1
        self.odswiez_dane()
        self.rysuj()

    def back(self):
        self.ez += 1
        self.odswiez_dane()
        self.rysuj()

    def rxup(self):
        self.theta_x+=15
        self.odswiez_dane()
        self.rysuj()

    def rxdown(self):
        self.theta_x-=15
        self.odswiez_dane()
        self.rysuj()

    def ryup(self):
        self.theta_y+=15
        self.odswiez_dane()
        self.rysuj()

    def rydown(self):
        self.theta_y-=15
        self.odswiez_dane()
        self.rysuj()

    def rzup(self):
        self.theta_z+=15
        self.odswiez_dane()
        self.rysuj()

    def rzdown(self):
        self.theta_z-=15
        self.odswiez_dane()
        self.rysuj()

    def zoomup(self):
        if(self.zoom+0.25!=10):
            self.zoom+=0.25
        self.odswiez_dane()
        self.rysuj()

    def zoomdown(self):
        if(self.zoom-0.25!=0):
            self.zoom-=0.25
        self.odswiez_dane()
        self.rysuj()



if __name__ == "__main__":
    original_data = wczytaj_dane_z_pliku("bloki.txt")
    root = tk.Tk()
    app = Aplikacja(root, original_data)
    root.mainloop()

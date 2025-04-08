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


def przekszt(zbiory_punktow, ex, ey, ez, theta_x, theta_y, theta_z):
    wynik = []

    # Konwersja kątów do radianów
    tx = np.radians(theta_x)
    ty = np.radians(theta_y)
    tz = np.radians(theta_z)

    # Macierze rotacji
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

    # Macierz transformacji kamery (kolejność rotacji: ZYX)
    R = Rx @ Ry @ Rz

    # Pozycja kamery
    C = np.array([ex, ey, ez])

    for zbior in zbiory_punktow:
        aktualny_zbior = []
        for dx, dy, dz in zbior:
            #print(str(dx)+" "+str(dy)+" "+str(dz))
            a = np.array([dx, dy, dz])
            d = a + C  # wektor względem kamery
            d_rot = R @ d  # obrót kamery

            

            if d_rot[2] <= 0:
                continue
            d_rot[2] = abs(d_rot[2])


            x = d_rot[0] / d_rot[2]
            y = d_rot[1] / d_rot[2]
            #print(str(x)+" "+str(y))
            aktualny_zbior.append((x, y))

        # Tworzymy linie
        proste = []
        if len(aktualny_zbior) >= 8:
            proste.extend([
                (aktualny_zbior[0], aktualny_zbior[1]),
                (aktualny_zbior[1], aktualny_zbior[2]),
                (aktualny_zbior[2], aktualny_zbior[3]),
                (aktualny_zbior[3], aktualny_zbior[0]),
                (aktualny_zbior[4], aktualny_zbior[5]),
                (aktualny_zbior[5], aktualny_zbior[6]),
                (aktualny_zbior[6], aktualny_zbior[7]),
                (aktualny_zbior[7], aktualny_zbior[4]),
                (aktualny_zbior[0], aktualny_zbior[4]),
                (aktualny_zbior[1], aktualny_zbior[5]),
                (aktualny_zbior[2], aktualny_zbior[6]),
                (aktualny_zbior[3], aktualny_zbior[7]),
            ])
        wynik.append(proste)

    return wynik


class Aplikacja:
    def __init__(self, master, original_data):
        self.master = master
        self.master.title("Wyświetlacz")
        self.original_data = original_data
        self.ey = 1
        self.ex = 1
        self.ez = 1
        self.theta_x = 0
        self.theta_y = 0
        self.theta_z = 0
        self.indeks = 0

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
        

        self.odswiez_dane()
        self.rysuj()

    def odswiez_dane(self):
        self.dane = przekszt(self.original_data, self.ex, self.ey, self.ez, self.theta_x, self.theta_y, self.theta_z)

    def rysuj(self):
        self.ax.clear()
        proste = self.dane[self.indeks]

        for x1, x2 in proste:
            self.ax.plot([x1[0], x2[0]], [x1[1], x2[1]], color='blue')

        self.ax.set_xlim(-5, 5)  # Ustaw zakres osi X
        self.ax.set_ylim(-5, 5)

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



if __name__ == "__main__":
    original_data = wczytaj_dane_z_pliku("bloki.txt")
    root = tk.Tk()
    app = Aplikacja(root, original_data)
    root.mainloop()

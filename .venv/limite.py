import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sympy import symbols, limit, lambdify, oo, sympify, sqrt, Piecewise, zoo, nan, simplify

x = symbols('x')

EXPRESION_DEFAULT = "x / (x - 3)"


class CalculadoraEstudiante(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analizador de Funciones")
        self.geometry("700x850")

        self.zoom_actual = 10
        self.zoom_min = 2
        self.zoom_max = 100

        self.expresion_sympy = None

        self._crear_interfaz()
        self._cargar_expresion()

    def _crear_interfaz(self):
        panel = tk.Frame(self, pady=10)
        panel.pack(fill="x")

        tk.Label(panel, text="f(x) =", font=("Arial", 12, "bold")).pack()

        self.entrada_fx = tk.Entry(panel, font=("Arial", 13), width=30, justify="center")
        self.entrada_fx.insert(0, EXPRESION_DEFAULT)
        self.entrada_fx.pack(pady=4)

        tk.Button(panel, text="CARGAR FUNCIÓN", command=self._cargar_expresion,
                  bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=3)

        tk.Label(panel, text="Punto a analizar (a):", font=("Arial", 11)).pack()

        self.entrada_a = tk.Entry(panel, font=("Arial", 14), width=10, justify="center")
        self.entrada_a.insert(0, "3")
        self.entrada_a.pack(pady=4)

        tk.Button(panel, text="ANALIZAR", command=self.analizar,
                  bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(pady=3)

        frame_zoom = tk.Frame(self)
        frame_zoom.pack(pady=5)

        tk.Button(frame_zoom, text="Zoom +", command=self.zoom_in,
                  bg="#616161", fg="white").pack(side="left", padx=5)

        tk.Button(frame_zoom, text="Zoom -", command=self.zoom_out,
                  bg="#616161", fg="white").pack(side="left", padx=5)

        self.lbl_resultado = tk.Label(self, text="Carga una función y presiona ANALIZAR",
                                      font=("Arial", 10, "italic"), wraplength=650)
        self.lbl_resultado.pack(pady=5)

        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.widget_canvas = self.canvas.get_tk_widget()
        self.widget_canvas.pack(fill="both", expand=True)

    def _parsear_expresion(self, texto):
        texto = texto.replace("^", "**")
        local_dict = {"x": x, "sqrt": sqrt}
        return sympify(texto, locals=local_dict)

    def _cargar_expresion(self):
        try:
            texto = self.entrada_fx.get().strip()
            self.expresion_sympy = self._parsear_expresion(texto)
            self.lbl_resultado.config(
                text=f"Función cargada: f(x) = {self.expresion_sympy}",
                fg="#2E7D32"
            )
            self.graficar_inicial()
        except Exception as e:
            messagebox.showerror("Error al parsear", f"No se pudo interpretar la función:\n{e}")

    def graficar_inicial(self):
        if self.expresion_sympy is None:
            return

        self.ax.clear()

        try:
            f_num = lambdify(x, self.expresion_sympy, modules=["numpy"])

            asintotas = []
            try:
                denom = self.expresion_sympy.as_numer_denom()[1]
                raices = np.roots([float(c) for c in denom.as_poly().all_coeffs()])
                asintotas = sorted([float(r.real) for r in raices if np.isreal(r)])
            except Exception:
                pass

            puntos = [-100] + asintotas + [100]

            for i in range(len(puntos) - 1):
                a, b = puntos[i], puntos[i + 1]
                eps = 1e-3

                x_datos = np.linspace(a + eps, b - eps, 800)

                with np.errstate(divide='ignore', invalid='ignore'):
                    y_datos = f_num(x_datos)
                    y_datos = np.where(np.abs(y_datos) > 100, np.nan, y_datos)

                self.ax.plot(x_datos, y_datos, color="#1A237E", lw=2,
                             label="f(x)" if i == 0 else "")
        except Exception:
            pass

        try:
            for r in asintotas:
                self.ax.axvline(r, color='red', linestyle='--', alpha=0.7)
        except Exception:
            pass


        try:
            simplificada = simplify(self.expresion_sympy)
            f_simplificada = lambdify(x, simplificada, modules=["numpy"])

            for r in asintotas:
                original = self.expresion_sympy.subs(x, r)
                if original.has(zoo) or original.has(nan):
                    y_hueco = f_simplificada(r)
                    self.ax.plot(r, y_hueco, 'o',
                                 markerfacecolor='white',
                                 markeredgecolor='blue',
                                 markersize=6)
        except Exception:
            pass


        try:
            h_lim_pos = limit(self.expresion_sympy, x, oo)
            if h_lim_pos.is_finite:
                self.ax.axhline(float(h_lim_pos), color='red', linestyle='--',
                                alpha=0.7, label=f"A. Horiz +∞ (y={h_lim_pos})")
        except Exception:
            pass

        try:
            h_lim_neg = limit(self.expresion_sympy, x, -oo)
            if h_lim_neg.is_finite:
                self.ax.axhline(float(h_lim_neg), color='orange', linestyle='--',
                                alpha=0.7, label=f"A. Horiz -∞ (y={h_lim_neg})")
        except Exception:
            pass

        self.ax.axhline(0, color='black', lw=1)
        self.ax.axvline(0, color='black', lw=1)
        self.ax.grid(True, linestyle=':', alpha=0.6)
        self.ax.set_title(f"f(x) = {self.expresion_sympy}", fontsize=10)

        self.zoom_actual = 10
        self.actualizar_limites()

        self.ax.legend(fontsize=8)
        self.canvas.draw()

    def zoom_in(self):
        if self.zoom_actual > self.zoom_min:
            self.zoom_actual *= 0.8
            self.actualizar_limites()

    def zoom_out(self):
        if self.zoom_actual < self.zoom_max:
            self.zoom_actual *= 1.25
            self.actualizar_limites()

    def actualizar_limites(self):
        self.ax.set_xlim(-self.zoom_actual, self.zoom_actual)
        self.ax.set_ylim(-self.zoom_actual, self.zoom_actual)
        self.canvas.draw()

    def _es_infinito(self, val):
        return (not val.is_finite) or (val == zoo) or (val == nan)

    def _limite_existe(self, val):
        try:
            return val.is_finite and val.is_real
        except Exception:
            return False

    def analizar(self):
        if self.expresion_sympy is None:
            messagebox.showwarning("Aviso", "Primero carga una función.")
            return

        try:
            a_val = float(self.entrada_a.get())

            lim_izq = limit(self.expresion_sympy, x, a_val, dir='-')
            lim_der = limit(self.expresion_sympy, x, a_val, dir='+')

            try:
                sustitucion = self.expresion_sympy.subs(x, a_val)
                if self._es_infinito(sustitucion):
                    sustitucion = None
            except Exception:
                sustitucion = None

            izq_inf = self._es_infinito(lim_izq)
            der_inf = self._es_infinito(lim_der)
            izq_existe = self._limite_existe(lim_izq)
            der_existe = self._limite_existe(lim_der)

            if izq_inf or der_inf:
                res = f"⚠️  ASÍNTOTA VERTICAL en x = {a_val}\n" \
                      f"   Lím izq = {lim_izq}  |  Lím der = {lim_der}"
                color = "#B71C1C"

            elif not izq_existe or not der_existe:
                res = f"❌  DISCONTINUIDAD ESENCIAL en x = {a_val}\n" \
                      f"   El límite no existe en ninguna dirección"
                color = "#6A1B9A"

            elif lim_izq != lim_der:
                res = f"↕️  DISCONTINUIDAD DE SALTO en x = {a_val}\n" \
                      f"   Lím izq = {lim_izq}  |  Lím der = {lim_der}"
                color = "#E65100"

            elif sustitucion is None:
                res = f"○  DISCONTINUIDAD EVITABLE en x = {a_val}\n" \
                      f"   Límite = {lim_izq}  |  f({a_val}) no definida"
                color = "#F57F17"

            elif sustitucion != lim_izq:
                res = f"○  DISCONTINUIDAD EVITABLE en x = {a_val}\n" \
                      f"   Límite = {lim_izq}  |  f({a_val}) = {sustitucion}"
                color = "#F57F17"

            else:
                res = f"✅  FUNCIÓN CONTINUA en x = {a_val}\n" \
                      f"   f({a_val}) = Límite = {lim_izq}"
                color = "#1B5E20"

            self.lbl_resultado.config(text=res, fg=color, font=("Arial", 10, "bold"))
            self.actualizar_limites()

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    CalculadoraEstudiante().mainloop()
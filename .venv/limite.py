import tkinter as tk
from tkinter import messagebox
from sympy import symbols, simplify, limit


x = symbols('x')


expr = (1)/(x - 2)


def calcular_f(x_val):
    try:
        numerador = (x_val**2 + 5 * x_val + 4)
        denominador = (x_val**2 + 3 * x_val - 4)

        if denominador == 0:
            return "indefinido"
        return numerador / denominador
    except:
        return "Error"



def analizar_limite(a):
    try:
        lim_izq = limit(expr, x, a, dir='-')
        lim_der = limit(expr, x, a, dir='+')

        if lim_izq == lim_der:
            if lim_izq.is_finite:
                # Revisar si hay hueco
                if expr.subs(x, a) == float('inf') or expr.subs(x, a) == float('-inf'):
                    return f"HUECO → Límite: {lim_izq}"
                return f"LÍMITE EXISTE: {lim_izq}"
            else:
                return "ASÍNTOTA VERTICAL (∞)"
        else:
            return "DISCONTINUIDAD DE SALTO"

    except:
        return "NO SE PUEDE DETERMINAR"


def ejecutar_estudio():
    try:
        a = float(entry_a.get())
    except ValueError:
        messagebox.showerror("Error", "Ingresa un número válido.")
        return

    txt_resultado.delete('1.0', tk.END)

    txt_resultado.insert(tk.END, f"{'IZQUIERDA':<15} | {'X=' + str(a):^12} | {'DERECHA':<15}\n")
    txt_resultado.insert(tk.END, "-" * 48 + "\n")

    pasos = [0.1, 0.01, 0.001, 0.0001]

    for h in pasos:
        izq = calcular_f(round(a - h, 6))
        der = calcular_f(round(a + h, 6))

        txt_izq = f"{izq:.4f}" if isinstance(izq, (float, int)) else str(izq)
        txt_der = f"{der:.4f}" if isinstance(der, (float, int)) else str(der)

        txt_resultado.insert(tk.END, f"{txt_izq:<15} | {'--->':^12} | {txt_der:<15}\n")

    # 🔥 Resultado simbólico real
    resultado = analizar_limite(a)
    lbl_conclusion.config(text=resultado)


# --- Interfaz ---
ventana = tk.Tk()
ventana.title("Calculadora de Límites PRO")
ventana.geometry("500x520")

tk.Label(ventana, text="Estudiar límite cuando x tiende a:", font=("Arial", 10, "bold")).pack(pady=10)

entry_a = tk.Entry(ventana, font=("Arial", 14), justify='center')
entry_a.pack(pady=5)

btn_calcular = tk.Button(
    ventana,
    text="ANALIZAR TENDENCIA",
    command=ejecutar_estudio,
    bg="#1976D2",
    fg="white",
    font=("Arial", 10, "bold"),
    padx=20
)
btn_calcular.pack(pady=15)

txt_resultado = tk.Text(
    ventana,
    height=10,
    width=55,
    font=("Courier New", 10),
    bg="#F5F5F5",
    padx=10,
    pady=10
)
txt_resultado.pack(pady=10)

lbl_conclusion = tk.Label(
    ventana,
    text="Ingresa un valor para comenzar",
    font=("Arial", 12, "bold")
)
lbl_conclusion.pack(pady=20)

ventana.mainloop()
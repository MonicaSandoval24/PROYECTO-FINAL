from datetime import date, timedelta

import customtkinter as ctk

from models.reportes import (ingresos_por_dia, ingresos_por_mes,
                             productos_mas_vendidos, resumen_ventas)
from views.graficos import crear_grafico, dibujar_ingresos, dibujar_mas_vendidos

PERIODOS = {
    "Últimos 7 días": ("dia", 7),
    "Últimos 30 días": ("dia", 30),
    "Últimos 6 meses": ("mes", 6),
    "Último año": ("mes", 12),
}


def fecha_inicio(tipo, cantidad):
    hoy = date.today()
    if tipo == "dia":
        return (hoy - timedelta(days=cantidad - 1)).isoformat()
    anio, mes = hoy.year, hoy.month - (cantidad - 1)
    while mes <= 0:
        mes += 12
        anio -= 1
    return f"{anio:04d}-{mes:02d}-01"


class DashboardWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Dashboard de ventas")
        self.geometry("1100x720")
        self.minsize(950, 640)
        self.configure(fg_color="#F1F5F9")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.crear_interfaz()
        self.actualizar()
        self.after(100, self.lift)
        self.after(150, self.focus_force)

    def crear_interfaz(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 6))

        titulos = ctk.CTkFrame(header, fg_color="transparent")
        titulos.pack(side="left")
        ctk.CTkLabel(titulos, text="Dashboard de ventas",
                     font=("Arial", 24, "bold"), text_color="#0F172A").pack(anchor="w")
        ctk.CTkLabel(titulos, text="Resumen del comportamiento de tu negocio.",
                     font=("Arial", 13), text_color="#64748B").pack(anchor="w")

        ctk.CTkButton(header, text="Actualizar", width=105,
                      command=self.actualizar).pack(side="right", padx=4)
        self.periodo_var = ctk.StringVar(value="Últimos 30 días")
        ctk.CTkOptionMenu(header, values=list(PERIODOS),
                          variable=self.periodo_var, width=170,
                          command=lambda valor: self.actualizar()).pack(
                              side="right", padx=4)

        tarjetas = ctk.CTkFrame(self, fg_color="transparent")
        tarjetas.grid(row=1, column=0, sticky="ew", padx=22, pady=8)
        tarjetas.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.ingresos_label = self.crear_tarjeta(tarjetas, 0, "Ingresos", "#16A34A")
        self.ventas_label = self.crear_tarjeta(tarjetas, 1, "Ventas realizadas", "#0F172A")
        self.unidades_label = self.crear_tarjeta(tarjetas, 2, "Unidades vendidas", "#0F172A")
        self.promedio_label = self.crear_tarjeta(tarjetas, 3, "Ticket promedio", "#2563EB")

        graficos = ctk.CTkFrame(self, fg_color="transparent")
        graficos.grid(row=2, column=0, sticky="nsew", padx=22, pady=(8, 20))
        graficos.grid_columnconfigure((0, 1), weight=1)
        graficos.grid_rowconfigure(0, weight=1)

        self.top = self.crear_panel(graficos, 0, "Productos más vendidos")
        self.ingresos = self.crear_panel(graficos, 1, "Ingresos por período")

    def crear_tarjeta(self, parent, columna, titulo, color):
        tarjeta = ctk.CTkFrame(parent, fg_color="white", corner_radius=12)
        tarjeta.grid(row=0, column=columna, sticky="ew", padx=6, pady=4)
        ctk.CTkLabel(tarjeta, text=titulo, font=("Arial", 11),
                     text_color="#64748B").pack(anchor="w", padx=15, pady=(12, 2))
        valor = ctk.CTkLabel(tarjeta, text="0", font=("Arial", 24, "bold"),
                             text_color=color)
        valor.pack(anchor="w", padx=15, pady=(0, 12))
        return valor

    def crear_panel(self, parent, columna, titulo):
        panel = ctk.CTkFrame(parent, fg_color="white", corner_radius=12)
        panel.grid(row=0, column=columna, sticky="nsew", padx=6, pady=4)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(panel, text=titulo, font=("Arial", 16, "bold"),
                     text_color="#0F172A").grid(
                         row=0, column=0, sticky="w", padx=16, pady=(12, 4))

        figura, eje, canvas = crear_grafico(panel)
        canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew",
                                    padx=10, pady=(0, 12))
        return figura, eje, canvas

    def actualizar(self):
        tipo, cantidad = PERIODOS[self.periodo_var.get()]
        desde = fecha_inicio(tipo, cantidad)

        resumen = resumen_ventas(desde)
        self.ingresos_label.configure(text=f"${resumen['ingresos']:,.2f}")
        self.ventas_label.configure(text=str(resumen["ventas"]))
        self.unidades_label.configure(text=str(resumen["unidades"]))
        self.promedio_label.configure(text=f"${resumen['promedio']:,.2f}")

        dibujar_mas_vendidos(*self.top, productos_mas_vendidos(desde))

        if tipo == "dia":
            etiquetas, valores = ingresos_por_dia(cantidad)
        else:
            etiquetas, valores = ingresos_por_mes(cantidad)
        dibujar_ingresos(*self.ingresos, etiquetas, valores, tipo == "mes")

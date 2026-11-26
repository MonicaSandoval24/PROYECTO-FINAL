import customtkinter as ctk

from models.productos import listar_productos

SIN_PRODUCTOS = "Sin productos registrados"


def opciones_productos():
    return {f"{p[1]} - {p[2]}": p for p in listar_productos()}


def crear_tabla(parent, titulos, row):
    encabezado = ctk.CTkFrame(parent, fg_color="#E2E8F0", corner_radius=6)
    encabezado.grid(row=row, column=0, sticky="ew", padx=16)
    encabezado.grid_columnconfigure(tuple(range(len(titulos))), weight=1)
    for col, titulo in enumerate(titulos):
        ctk.CTkLabel(encabezado, text=titulo, font=("Arial", 11, "bold"),
                     text_color="#334155").grid(
                         row=0, column=col, padx=5, pady=8, sticky="ew")

    cuerpo = ctk.CTkScrollableFrame(parent, fg_color="white", corner_radius=0)
    cuerpo.grid(row=row + 1, column=0, sticky="nsew", padx=16, pady=(0, 12))
    cuerpo.grid_columnconfigure(0, weight=1)
    return cuerpo


def agregar_fila(cuerpo, numero, valores, fondo="#F8FAFC"):
    fila = ctk.CTkFrame(cuerpo, fg_color=fondo, corner_radius=6)
    fila.grid(row=numero, column=0, sticky="ew", pady=3)
    fila.grid_columnconfigure(tuple(range(len(valores))), weight=1)
    for col, valor in enumerate(valores):
        ctk.CTkLabel(fila, text=valor, font=("Arial", 11),
                     text_color="#334155").grid(
                         row=0, column=col, padx=4, pady=7, sticky="ew")
    return fila


def limpiar(cuerpo):
    for widget in cuerpo.winfo_children():
        widget.destroy()


def mensaje_vacio(cuerpo, texto):
    ctk.CTkLabel(cuerpo, text=texto, text_color="#64748B").grid(
        row=0, column=0, pady=20)

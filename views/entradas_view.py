import customtkinter as ctk
from tkinter import messagebox

from models.entradas import obtener_entradas, registrar_entrada
from views.comun import (SIN_PRODUCTOS, agregar_fila, crear_tabla, limpiar,
                         mensaje_vacio, opciones_productos)


class EntradasWindow(ctk.CTkToplevel):
    def __init__(self, master, al_cambiar=None):
        super().__init__(master)
        self.title("Entradas de mercadería")
        self.geometry("860x640")
        self.minsize(760, 560)
        self.configure(fg_color="#F1F5F9")
        self.al_cambiar = al_cambiar
        self.productos = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.crear_interfaz()
        self.recargar_productos()
        self.cargar_historial()
        self.after(100, self.lift)
        self.after(150, self.focus_force)

    def crear_interfaz(self):
        ctk.CTkLabel(self, text="Entrada de mercadería",
                     font=("Arial", 24, "bold"), text_color="#0F172A").grid(
                         row=0, column=0, sticky="w", padx=28, pady=(20, 6))

        form = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        form.grid(row=1, column=0, sticky="ew", padx=28, pady=8)
        form.grid_columnconfigure((0, 1), weight=1)

        self.etiqueta(form, "Producto", 0, 0)
        self.etiqueta(form, "Cantidad recibida", 0, 1)

        self.producto_var = ctk.StringVar(value=SIN_PRODUCTOS)
        self.producto_menu = ctk.CTkOptionMenu(
            form, variable=self.producto_var, values=[SIN_PRODUCTOS],
            command=lambda valor: self.mostrar_info(), dynamic_resizing=False
        )
        self.producto_menu.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 6))

        self.cantidad_entry = ctk.CTkEntry(form, placeholder_text="Cantidad")
        self.cantidad_entry.grid(row=1, column=1, sticky="ew", padx=12, pady=(0, 6))

        self.etiqueta(form, "Proveedor (opcional)", 2, 0)
        self.etiqueta(form, "Nota (opcional)", 2, 1)

        self.proveedor_entry = ctk.CTkEntry(form, placeholder_text="Proveedor")
        self.proveedor_entry.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 6))

        self.nota_entry = ctk.CTkEntry(form, placeholder_text="Nota")
        self.nota_entry.grid(row=3, column=1, sticky="ew", padx=12, pady=(0, 6))

        ctk.CTkButton(form, text="Registrar entrada", width=150,
                      command=self.registrar,
                      fg_color="#16A34A", hover_color="#15803D").grid(
                          row=3, column=2, padx=(4, 14), pady=(0, 6))

        self.info_label = ctk.CTkLabel(form, text="", font=("Arial", 11),
                                       text_color="#64748B")
        self.info_label.grid(row=4, column=0, columnspan=3, sticky="w",
                             padx=14, pady=(0, 12))

        historial = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        historial.grid(row=2, column=0, sticky="nsew", padx=28, pady=(8, 20))
        historial.grid_columnconfigure(0, weight=1)
        historial.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(historial, text="Historial de entradas",
                     font=("Arial", 17, "bold"), text_color="#0F172A").grid(
                         row=0, column=0, sticky="w", padx=16, pady=(12, 8))
        self.historial_body = crear_tabla(
            historial, ["Fecha", "Código", "Producto", "Cantidad", "Proveedor"], 1
        )

    def etiqueta(self, parent, texto, row, column):
        ctk.CTkLabel(parent, text=texto, font=("Arial", 11),
                     text_color="#475569").grid(
                         row=row, column=column, sticky="w", padx=14, pady=(10, 2))

    def recargar_productos(self):
        seleccionado = self.producto_var.get()
        self.productos = opciones_productos()

        if self.productos:
            nombres = list(self.productos)
            self.producto_menu.configure(values=nombres, state="normal")
            self.producto_var.set(seleccionado if seleccionado in self.productos
                                  else nombres[0])
        else:
            self.producto_menu.configure(values=[SIN_PRODUCTOS], state="disabled")
            self.producto_var.set(SIN_PRODUCTOS)

        self.mostrar_info()

    def producto_actual(self):
        return self.productos.get(self.producto_var.get())

    def mostrar_info(self):
        producto = self.producto_actual()
        if producto is None:
            self.info_label.configure(
                text="Registra productos en el inventario primero.")
            return
        _, _, _, _, stock, minimo = producto
        self.info_label.configure(
            text=f"Stock actual: {stock}     Stock mínimo: {minimo}")

    def registrar(self):
        producto = self.producto_actual()
        if producto is None:
            messagebox.showwarning("Sin productos",
                                   "Primero registra productos en el inventario.",
                                   parent=self)
            return

        try:
            cantidad = int(self.cantidad_entry.get().strip())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Cantidad inválida",
                "La cantidad debe ser un número entero mayor que cero.",
                parent=self
            )
            return

        try:
            nuevo_stock = registrar_entrada(
                producto[0], cantidad,
                self.proveedor_entry.get().strip(),
                self.nota_entry.get().strip()
            )
        except ValueError as error:
            messagebox.showerror("No se pudo registrar la entrada", str(error),
                                 parent=self)
            self.recargar_productos()
            return

        for entry in (self.cantidad_entry, self.proveedor_entry, self.nota_entry):
            entry.delete(0, "end")

        self.recargar_productos()
        self.cargar_historial()
        if self.al_cambiar:
            self.al_cambiar()

        messagebox.showinfo(
            "Entrada registrada",
            f"Se agregaron {cantidad} unidades a {producto[2]}.\n"
            f"Stock actual: {nuevo_stock}.",
            parent=self
        )

    def cargar_historial(self):
        limpiar(self.historial_body)
        entradas = obtener_entradas()
        for numero, (fecha, codigo, nombre, cantidad, proveedor) in enumerate(entradas, start=1):
            agregar_fila(self.historial_body, numero, [
                fecha, codigo, nombre, str(cantidad), proveedor or "-"
            ])
        if not entradas:
            mensaje_vacio(self.historial_body, "Todavía no hay entradas registradas.")

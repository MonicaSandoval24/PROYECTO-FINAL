import customtkinter as ctk
from tkinter import messagebox

from models.ventas import StockInsuficiente, obtener_ventas, registrar_venta
from views.comun import (SIN_PRODUCTOS, agregar_fila, crear_tabla, limpiar,
                         mensaje_vacio, opciones_productos)


class VentasWindow(ctk.CTkToplevel):
    def __init__(self, master, al_cambiar=None):
        super().__init__(master)
        self.title("Registro de ventas")
        self.geometry("860x720")
        self.minsize(760, 620)
        self.configure(fg_color="#F1F5F9")
        self.al_cambiar = al_cambiar
        self.productos = {}
        self.por_id = {}
        self.carrito = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.crear_interfaz()
        self.recargar_productos()
        self.cargar_historial()
        self.after(100, self.lift)
        self.after(150, self.focus_force)

    def crear_interfaz(self):
        ctk.CTkLabel(self, text="Nueva venta", font=("Arial", 24, "bold"),
                     text_color="#0F172A").grid(
                         row=0, column=0, sticky="w", padx=28, pady=(20, 6))

        form = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        form.grid(row=1, column=0, sticky="ew", padx=28, pady=8)
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="Producto", font=("Arial", 11),
                     text_color="#475569").grid(
                         row=0, column=0, sticky="w", padx=14, pady=(12, 2))
        ctk.CTkLabel(form, text="Cantidad", font=("Arial", 11),
                     text_color="#475569").grid(
                         row=0, column=1, sticky="w", padx=14, pady=(12, 2))

        self.producto_var = ctk.StringVar(value=SIN_PRODUCTOS)
        self.producto_menu = ctk.CTkOptionMenu(
            form, variable=self.producto_var, values=[SIN_PRODUCTOS],
            command=lambda valor: self.mostrar_info(), dynamic_resizing=False
        )
        self.producto_menu.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 6))

        self.cantidad_entry = ctk.CTkEntry(form, width=100, placeholder_text="1")
        self.cantidad_entry.grid(row=1, column=1, padx=12, pady=(0, 6))
        self.cantidad_entry.bind("<Return>", lambda event: self.agregar_al_carrito())

        ctk.CTkButton(form, text="Agregar", width=110,
                      command=self.agregar_al_carrito,
                      fg_color="#2563EB", hover_color="#1D4ED8").grid(
                          row=1, column=2, padx=(4, 14), pady=(0, 6))

        self.info_label = ctk.CTkLabel(form, text="", font=("Arial", 11),
                                       text_color="#64748B")
        self.info_label.grid(row=2, column=0, columnspan=3, sticky="w",
                             padx=14, pady=(0, 12))

        carrito = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        carrito.grid(row=2, column=0, sticky="nsew", padx=28, pady=8)
        carrito.grid_columnconfigure(0, weight=1)
        carrito.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(carrito, text="Carrito", font=("Arial", 17, "bold"),
                     text_color="#0F172A").grid(
                         row=0, column=0, sticky="w", padx=16, pady=(12, 8))
        self.carrito_body = crear_tabla(
            carrito, ["Producto", "Cantidad", "Precio", "Subtotal", ""], 1
        )

        pie = ctk.CTkFrame(carrito, fg_color="transparent")
        pie.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 12))
        self.total_label = ctk.CTkLabel(pie, text="Total: $0.00",
                                        font=("Arial", 18, "bold"),
                                        text_color="#0F172A")
        self.total_label.pack(side="left")
        ctk.CTkButton(pie, text="Confirmar venta",
                      command=self.confirmar_venta,
                      fg_color="#16A34A", hover_color="#15803D").pack(
                          side="right", padx=4)
        ctk.CTkButton(pie, text="Vaciar", width=90,
                      command=self.vaciar_carrito,
                      fg_color="#64748B", hover_color="#475569").pack(
                          side="right", padx=4)

        historial = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        historial.grid(row=3, column=0, sticky="nsew", padx=28, pady=(8, 20))
        historial.grid_columnconfigure(0, weight=1)
        historial.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(historial, text="Últimas ventas", font=("Arial", 17, "bold"),
                     text_color="#0F172A").grid(
                         row=0, column=0, sticky="w", padx=16, pady=(12, 8))
        self.historial_body = crear_tabla(
            historial, ["N.º", "Fecha", "Artículos", "Total"], 1
        )

    def recargar_productos(self):
        seleccionado = self.producto_var.get()
        self.productos = opciones_productos()
        self.por_id = {p[0]: p for p in self.productos.values()}
        self.carrito = {pid: cant for pid, cant in self.carrito.items()
                        if pid in self.por_id}

        if self.productos:
            nombres = list(self.productos)
            self.producto_menu.configure(values=nombres, state="normal")
            self.producto_var.set(seleccionado if seleccionado in self.productos
                                  else nombres[0])
        else:
            self.producto_menu.configure(values=[SIN_PRODUCTOS], state="disabled")
            self.producto_var.set(SIN_PRODUCTOS)

        self.mostrar_info()
        self.mostrar_carrito()

    def producto_actual(self):
        return self.productos.get(self.producto_var.get())

    def mostrar_info(self):
        producto = self.producto_actual()
        if producto is None:
            self.info_label.configure(
                text="Registra productos en el inventario para poder vender.")
            return
        producto_id, _, _, precio, stock, _ = producto
        disponible = stock - self.carrito.get(producto_id, 0)
        self.info_label.configure(
            text=f"Precio: ${precio:.2f}     Disponible: {disponible}")

    def agregar_al_carrito(self):
        producto = self.producto_actual()
        if producto is None:
            return

        try:
            cantidad = int(self.cantidad_entry.get().strip() or "1")
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Cantidad inválida",
                "La cantidad debe ser un número entero mayor que cero.",
                parent=self
            )
            return

        producto_id, _, nombre, _, stock, _ = producto
        pedido = self.carrito.get(producto_id, 0) + cantidad
        if pedido > stock:
            messagebox.showwarning(
                "Stock insuficiente",
                f"Solo hay {stock} unidades de {nombre}.",
                parent=self
            )
            return

        self.carrito[producto_id] = pedido
        self.cantidad_entry.delete(0, "end")
        self.mostrar_carrito()
        self.mostrar_info()

    def mostrar_carrito(self):
        limpiar(self.carrito_body)
        total = 0

        for numero, (producto_id, cantidad) in enumerate(self.carrito.items(), start=1):
            _, _, nombre, precio, _, _ = self.por_id[producto_id]
            subtotal = precio * cantidad
            total += subtotal
            fila = agregar_fila(self.carrito_body, numero, [
                nombre, str(cantidad), f"${precio:.2f}", f"${subtotal:.2f}"
            ])
            fila.grid_columnconfigure(4, weight=1)
            ctk.CTkButton(fila, text="Quitar", width=70, height=26,
                          fg_color="#DC2626", hover_color="#B91C1C",
                          command=lambda p=producto_id: self.quitar(p)).grid(
                              row=0, column=4, padx=4, pady=4)

        if not self.carrito:
            mensaje_vacio(self.carrito_body, "El carrito está vacío.")

        self.total_label.configure(text=f"Total: ${total:.2f}")

    def quitar(self, producto_id):
        self.carrito.pop(producto_id, None)
        self.mostrar_carrito()
        self.mostrar_info()

    def vaciar_carrito(self):
        self.carrito = {}
        self.mostrar_carrito()
        self.mostrar_info()

    def confirmar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacío",
                                   "Agrega al menos un producto.", parent=self)
            return

        try:
            venta_id, total, stock_bajo = registrar_venta(list(self.carrito.items()))
        except (StockInsuficiente, ValueError) as error:
            messagebox.showerror("No se pudo registrar la venta", str(error),
                                 parent=self)
            self.recargar_productos()
            return

        self.carrito = {}
        self.recargar_productos()
        self.cargar_historial()
        if self.al_cambiar:
            self.al_cambiar()

        messagebox.showinfo("Venta registrada",
                            f"Venta N.º {venta_id} registrada por ${total:.2f}.",
                            parent=self)

        if stock_bajo:
            detalle = "\n".join(
                f"• {nombre}: quedan {stock} (mínimo {minimo})"
                for nombre, stock, minimo in stock_bajo
            )
            messagebox.showwarning(
                "Stock bajo",
                f"Estos productos necesitan reabastecimiento:\n\n{detalle}",
                parent=self
            )

    def cargar_historial(self):
        limpiar(self.historial_body)
        ventas = obtener_ventas()
        for numero, (venta_id, fecha, articulos, total) in enumerate(ventas, start=1):
            agregar_fila(self.historial_body, numero, [
                str(venta_id), fecha, str(articulos), f"${total:.2f}"
            ])
        if not ventas:
            mensaje_vacio(self.historial_body, "Todavía no hay ventas registradas.")

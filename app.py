import sqlite3
import customtkinter as ctk
from tkinter import messagebox

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "smartstock.db")

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class SmartStockApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SmartStock & Sales Analytics")
        self.geometry("1120x720")
        self.minsize(950, 620)
        self.selected_product_id = None

        self.create_database()
        self.create_interface()
        self.load_products()

    # ---------------- BASE DE DATOS ----------------
    def connect_db(self):
        return sqlite3.connect(DB_NAME)

    def create_database(self):
        with self.connect_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT NOT NULL UNIQUE,
                    nombre TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    precio REAL NOT NULL,
                    stock INTEGER NOT NULL,
                    stock_minimo INTEGER NOT NULL
                )
            """)

    # ---------------- INTERFAZ ----------------
    def create_interface(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Menú lateral
        sidebar = ctk.CTkFrame(self, width=215, corner_radius=0,
                               fg_color="#172554")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar, text="SmartStock", font=("Arial", 25, "bold"),
            text_color="white"
        ).pack(pady=(35, 3))
        ctk.CTkLabel(
            sidebar, text="& Sales Analytics", font=("Arial", 13),
            text_color="#BFDBFE"
        ).pack(pady=(0, 35))

        ctk.CTkLabel(
            sidebar, text="GESTIÓN COMERCIAL", font=("Arial", 11, "bold"),
            text_color="#93C5FD"
        ).pack(anchor="w", padx=20, pady=(5, 12))

        ctk.CTkLabel(
            sidebar, text="📦  Inventario", font=("Arial", 15, "bold"),
            text_color="white", anchor="w"
        ).pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            sidebar, text="Prototipo inicial\nMódulo de productos",
            font=("Arial", 12), text_color="#BFDBFE",
            justify="left"
        ).pack(side="bottom", anchor="w", padx=20, pady=25)

        # Área principal
        main = ctk.CTkFrame(self, fg_color="#F1F5F9", corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(3, weight=1)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 12))
        ctk.CTkLabel(
            header, text="Panel de inventario",
            font=("Arial", 26, "bold"), text_color="#0F172A"
        ).pack(anchor="w")
        ctk.CTkLabel(
            header, text="Registra y controla los productos de tu negocio.",
            font=("Arial", 13), text_color="#64748B"
        ).pack(anchor="w", pady=(4, 0))

        # Tarjetas de resumen
        summary = ctk.CTkFrame(main, fg_color="transparent")
        summary.grid(row=1, column=0, sticky="ew", padx=22, pady=8)
        for col in range(3):
            summary.grid_columnconfigure(col, weight=1)

        self.total_value = ctk.CTkLabel(summary, text="0",
                                        font=("Arial", 25, "bold"),
                                        text_color="#0F172A")
        self.low_value = ctk.CTkLabel(summary, text="0",
                                      font=("Arial", 25, "bold"),
                                      text_color="#DC2626")
        self.units_value = ctk.CTkLabel(summary, text="0",
                                        font=("Arial", 25, "bold"),
                                        text_color="#0F172A")

        self.create_stat_card(summary, 0, "Productos registrados", self.total_value)
        self.create_stat_card(summary, 1, "Productos con stock bajo", self.low_value)
        self.create_stat_card(summary, 2, "Unidades disponibles", self.units_value)

        # Formulario
        form = ctk.CTkFrame(main, fg_color="white", corner_radius=12)
        form.grid(row=2, column=0, sticky="ew", padx=28, pady=10)
        form.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(form, text="Datos del producto",
                     font=("Arial", 17, "bold"),
                     text_color="#0F172A").grid(
                         row=0, column=0, columnspan=4,
                         sticky="w", padx=18, pady=(15, 8))

        self.codigo_entry = self.add_field(form, "Código", 1, 0)
        self.nombre_entry = self.add_field(form, "Nombre", 1, 1)
        self.categoria_entry = self.add_field(form, "Categoría", 1, 2)
        self.precio_entry = self.add_field(form, "Precio ($)", 1, 3)
        self.stock_entry = self.add_field(form, "Stock actual", 3, 0)
        self.minimo_entry = self.add_field(form, "Stock mínimo", 3, 1)

        buttons = ctk.CTkFrame(form, fg_color="transparent")
        buttons.grid(row=3, column=2, columnspan=2, sticky="ew",
                     padx=12, pady=(22, 12))
        ctk.CTkButton(buttons, text="Guardar producto",
                      command=self.save_product,
                      fg_color="#2563EB", hover_color="#1D4ED8").pack(
                          side="left", padx=4, expand=True, fill="x")
        ctk.CTkButton(buttons, text="Limpiar",
                      command=self.clear_form,
                      fg_color="#64748B", hover_color="#475569").pack(
                          side="left", padx=4, expand=True, fill="x")

        # Inventario / tabla
        inventory = ctk.CTkFrame(main, fg_color="white", corner_radius=12)
        inventory.grid(row=3, column=0, sticky="nsew", padx=28, pady=(5, 24))
        inventory.grid_columnconfigure(0, weight=1)
        inventory.grid_rowconfigure(2, weight=1)

        top = ctk.CTkFrame(inventory, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        ctk.CTkLabel(top, text="Inventario de productos",
                     font=("Arial", 17, "bold"),
                     text_color="#0F172A").pack(side="left")

        self.search_entry = ctk.CTkEntry(
            top, placeholder_text="Buscar por código o nombre...",
            width=240
        )
        self.search_entry.pack(side="right", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda event: self.load_products())

        filter_row = ctk.CTkFrame(inventory, fg_color="transparent")
        filter_row.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))
        self.filter_value = ctk.StringVar(value="Todos")
        ctk.CTkOptionMenu(
            filter_row, values=["Todos", "Stock bajo", "Stock normal"],
            variable=self.filter_value, command=lambda value: self.load_products(),
            width=150
        ).pack(side="left")
        ctk.CTkButton(
            filter_row, text="Actualizar", width=105,
            command=self.load_products
        ).pack(side="right", padx=4)
        ctk.CTkButton(
            filter_row, text="Eliminar seleccionado", width=165,
            fg_color="#DC2626", hover_color="#B91C1C",
            command=self.delete_product
        ).pack(side="right", padx=4)

        # Encabezados
        headings = ctk.CTkFrame(inventory, fg_color="#E2E8F0", corner_radius=6)
        headings.grid(row=2, column=0, sticky="new", padx=16, pady=(0, 0))
        headings.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        for col, title in enumerate(["Código", "Producto", "Categoría",
                                     "Precio", "Stock", "Estado"]):
            ctk.CTkLabel(headings, text=title, font=("Arial", 11, "bold"),
                         text_color="#334155").grid(
                             row=0, column=col, padx=5, pady=9, sticky="ew")

        self.rows_frame = ctk.CTkScrollableFrame(
            inventory, fg_color="white", corner_radius=0
        )
        self.rows_frame.grid(row=3, column=0, sticky="nsew", padx=16, pady=(0, 12))
        self.rows_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        ctk.CTkLabel(
            inventory, text="Selecciona una fila para modificar o eliminar un producto.",
            font=("Arial", 11), text_color="#64748B"
        ).grid(row=4, column=0, sticky="w", padx=18, pady=(0, 10))

    def create_stat_card(self, parent, column, title, value_label):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12)
        card.grid(row=0, column=column, sticky="ew", padx=6, pady=4)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text=title, font=("Arial", 11),
            text_color="#64748B"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 2))

        value_label.grid(
            row=1, column=0, sticky="w", padx=15, pady=(0, 12)
        )

    def add_field(self, parent, label, row, column):
        ctk.CTkLabel(parent, text=label, font=("Arial", 11),
                     text_color="#475569").grid(
                         row=row, column=column, sticky="w",
                         padx=14, pady=(5, 2))
        entry = ctk.CTkEntry(parent, height=32, placeholder_text=label)
        entry.grid(row=row + 1, column=column, sticky="ew",
                   padx=12, pady=(0, 8))
        return entry

    # ---------------- OPERACIONES ----------------
    def save_product(self):
        codigo = self.codigo_entry.get().strip()
        nombre = self.nombre_entry.get().strip()
        categoria = self.categoria_entry.get().strip()

        try:
            precio = float(self.precio_entry.get())
            stock = int(self.stock_entry.get())
            minimo = int(self.minimo_entry.get())
            if precio < 0 or stock < 0 or minimo < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Datos inválidos",
                "Precio, stock y stock mínimo deben ser números válidos y no negativos."
            )
            return

        if not codigo or not nombre or not categoria:
            messagebox.showwarning(
                "Campos incompletos",
                "Completa el código, nombre y categoría del producto."
            )
            return

        try:
            with self.connect_db() as conn:
                if self.selected_product_id is None:
                    conn.execute("""
                        INSERT INTO productos
                        (codigo, nombre, categoria, precio, stock, stock_minimo)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (codigo, nombre, categoria, precio, stock, minimo))
                    message = "Producto registrado correctamente."
                else:
                    conn.execute("""
                        UPDATE productos
                        SET codigo=?, nombre=?, categoria=?, precio=?,
                            stock=?, stock_minimo=?
                        WHERE id=?
                    """, (codigo, nombre, categoria, precio, stock, minimo,
                          self.selected_product_id))
                    message = "Producto actualizado correctamente."

            messagebox.showinfo("SmartStock", message)
            self.clear_form()
            self.load_products()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Código duplicado",
                "Ya existe un producto con ese código. Utiliza uno diferente."
            )

    def load_products(self):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        search = self.search_entry.get().strip() if hasattr(self, "search_entry") else ""
        filter_status = self.filter_value.get() if hasattr(self, "filter_value") else "Todos"

        with self.connect_db() as conn:
            products = conn.execute("""
                SELECT id, codigo, nombre, categoria, precio, stock, stock_minimo
                FROM productos
                WHERE codigo LIKE ? OR nombre LIKE ?
                ORDER BY nombre
            """, (f"%{search}%", f"%{search}%")).fetchall()

            all_products = conn.execute(
                "SELECT stock, stock_minimo FROM productos"
            ).fetchall()

        total = len(all_products)
        low = sum(1 for stock, minimum in all_products if stock <= minimum)
        units = sum(stock for stock, minimum in all_products)

        self.total_value.configure(text=str(total))
        self.low_value.configure(text=str(low))
        self.units_value.configure(text=str(units))

        visible_count = 0
        for product in products:
            product_id, codigo, nombre, categoria, precio, stock, minimo = product
            is_low = stock <= minimo

            if filter_status == "Stock bajo" and not is_low:
                continue
            if filter_status == "Stock normal" and is_low:
                continue

            visible_count += 1
            row = ctk.CTkFrame(
                self.rows_frame,
                fg_color="#FEF2F2" if is_low else "#F8FAFC",
                corner_radius=6
            )
            row.grid(row=visible_count, column=0, sticky="ew", pady=3)
            row.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

            values = [codigo, nombre, categoria, f"${precio:.2f}", str(stock),
                      "Stock bajo" if is_low else "Normal"]
            for col, value in enumerate(values):
                color = "#DC2626" if col == 5 and is_low else "#334155"
                label = ctk.CTkLabel(
                    row, text=value, font=("Arial", 11),
                    text_color=color, anchor="center"
                )
                label.grid(row=0, column=col, padx=4, pady=9, sticky="ew")
                label.bind("<Button-1>", lambda event, p=product: self.select_product(p))

            row.bind("<Button-1>", lambda event, p=product: self.select_product(p))

        if visible_count == 0:
            ctk.CTkLabel(
                self.rows_frame, text="No hay productos para mostrar.",
                text_color="#64748B"
            ).grid(row=0, column=0, pady=25)

    def select_product(self, product):
        (self.selected_product_id, codigo, nombre, categoria,
         precio, stock, minimo) = product
        entries = [
            (self.codigo_entry, codigo),
            (self.nombre_entry, nombre),
            (self.categoria_entry, categoria),
            (self.precio_entry, str(precio)),
            (self.stock_entry, str(stock)),
            (self.minimo_entry, str(minimo))
        ]
        for entry, value in entries:
            entry.delete(0, "end")
            entry.insert(0, value)

    def delete_product(self):
        if self.selected_product_id is None:
            messagebox.showwarning(
                "Selecciona un producto",
                "Primero selecciona una fila del inventario."
            )
            return

        if messagebox.askyesno(
            "Confirmar eliminación",
            "¿Seguro que deseas eliminar este producto?"
        ):
            with self.connect_db() as conn:
                conn.execute(
                    "DELETE FROM productos WHERE id=?",
                    (self.selected_product_id,)
                )
            self.clear_form()
            self.load_products()
            messagebox.showinfo("SmartStock", "Producto eliminado.")

    def clear_form(self):
        self.selected_product_id = None
        for entry in [
            self.codigo_entry, self.nombre_entry, self.categoria_entry,
            self.precio_entry, self.stock_entry, self.minimo_entry
        ]:
            entry.delete(0, "end")


if __name__ == "__main__":
    app = SmartStockApp()
    app.mainloop()

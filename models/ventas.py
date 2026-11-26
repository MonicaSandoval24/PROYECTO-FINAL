from datetime import datetime

from database import conexion


class StockInsuficiente(Exception):
    pass


def registrar_venta(items):
    cantidades = {}
    for producto_id, cantidad in items:
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        cantidades[producto_id] = cantidades.get(producto_id, 0) + cantidad

    if not cantidades:
        raise ValueError("La venta no tiene productos.")

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with conexion() as conn:
        lineas = []
        total = 0
        for producto_id, cantidad in cantidades.items():
            fila = conn.execute(
                "SELECT nombre, precio, stock FROM productos WHERE id = ?",
                (producto_id,)
            ).fetchone()
            if fila is None:
                raise ValueError("Uno de los productos ya no existe.")
            nombre, precio, stock = fila
            if cantidad > stock:
                raise StockInsuficiente(
                    f"Stock insuficiente para {nombre}. Disponible: {stock}."
                )
            lineas.append((producto_id, cantidad, precio))
            total += precio * cantidad

        total = round(total, 2)
        cursor = conn.execute(
            "INSERT INTO ventas (fecha, total) VALUES (?, ?)", (fecha, total)
        )
        venta_id = cursor.lastrowid

        for producto_id, cantidad, precio in lineas:
            conn.execute("""
                INSERT INTO detalle_venta
                (venta_id, producto_id, cantidad, precio_unitario)
                VALUES (?, ?, ?, ?)
            """, (venta_id, producto_id, cantidad, precio))
            conn.execute(
                "UPDATE productos SET stock = stock - ? WHERE id = ?",
                (cantidad, producto_id)
            )

        marcadores = ", ".join("?" for _ in cantidades)
        stock_bajo = conn.execute(f"""
            SELECT nombre, stock, stock_minimo
            FROM productos
            WHERE id IN ({marcadores}) AND stock <= stock_minimo
        """, list(cantidades)).fetchall()

    return venta_id, total, stock_bajo


def obtener_ventas(limite=50):
    with conexion() as conn:
        return conn.execute("""
            SELECT v.id, v.fecha, COALESCE(SUM(d.cantidad), 0), v.total
            FROM ventas v
            LEFT JOIN detalle_venta d ON d.venta_id = v.id
            GROUP BY v.id
            ORDER BY v.id DESC
            LIMIT ?
        """, (limite,)).fetchall()

from datetime import datetime

from database import conexion


def registrar_entrada(producto_id, cantidad, proveedor="", nota=""):
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with conexion() as conn:
        existe = conn.execute(
            "SELECT 1 FROM productos WHERE id = ?", (producto_id,)
        ).fetchone()
        if existe is None:
            raise ValueError("El producto ya no existe.")

        conn.execute("""
            INSERT INTO entradas (fecha, producto_id, cantidad, proveedor, nota)
            VALUES (?, ?, ?, ?, ?)
        """, (fecha, producto_id, cantidad, proveedor or None, nota or None))
        conn.execute(
            "UPDATE productos SET stock = stock + ? WHERE id = ?",
            (cantidad, producto_id)
        )
        nuevo_stock = conn.execute(
            "SELECT stock FROM productos WHERE id = ?", (producto_id,)
        ).fetchone()[0]

    return nuevo_stock


def obtener_entradas(limite=50):
    with conexion() as conn:
        return conn.execute("""
            SELECT e.fecha, p.codigo, p.nombre, e.cantidad,
                   COALESCE(e.proveedor, '')
            FROM entradas e
            JOIN productos p ON p.id = e.producto_id
            ORDER BY e.id DESC
            LIMIT ?
        """, (limite,)).fetchall()

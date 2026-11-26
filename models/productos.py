from database import conexion


def listar_productos():
    with conexion() as conn:
        return conn.execute("""
            SELECT id, codigo, nombre, precio, stock, stock_minimo
            FROM productos
            ORDER BY nombre
        """).fetchall()

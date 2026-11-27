from datetime import date, timedelta

from database import conexion


def resumen_ventas(desde):
    with conexion() as conn:
        num_ventas, ingresos = conn.execute("""
            SELECT COUNT(*), COALESCE(SUM(total), 0)
            FROM ventas
            WHERE date(fecha) >= ?
        """, (desde,)).fetchone()
        unidades = conn.execute("""
            SELECT COALESCE(SUM(d.cantidad), 0)
            FROM detalle_venta d
            JOIN ventas v ON v.id = d.venta_id
            WHERE date(v.fecha) >= ?
        """, (desde,)).fetchone()[0]

    promedio = ingresos / num_ventas if num_ventas else 0
    return {
        "ventas": num_ventas,
        "ingresos": ingresos,
        "unidades": unidades,
        "promedio": promedio,
    }


def productos_mas_vendidos(desde, limite=5):
    with conexion() as conn:
        return conn.execute("""
            SELECT p.nombre, SUM(d.cantidad) AS unidades,
                   SUM(d.cantidad * d.precio_unitario) AS ingresos
            FROM detalle_venta d
            JOIN ventas v ON v.id = d.venta_id
            JOIN productos p ON p.id = d.producto_id
            WHERE date(v.fecha) >= ?
            GROUP BY d.producto_id
            ORDER BY unidades DESC
            LIMIT ?
        """, (desde, limite)).fetchall()


def ingresos_por_dia(dias):
    inicio = date.today() - timedelta(days=dias - 1)
    with conexion() as conn:
        filas = conn.execute("""
            SELECT date(fecha), SUM(total)
            FROM ventas
            WHERE date(fecha) >= ?
            GROUP BY date(fecha)
        """, (inicio.isoformat(),)).fetchall()

    totales = dict(filas)
    etiquetas = []
    valores = []
    for i in range(dias):
        dia = inicio + timedelta(days=i)
        etiquetas.append(dia.strftime("%d/%m"))
        valores.append(totales.get(dia.isoformat(), 0))
    return etiquetas, valores


def ingresos_por_mes(meses):
    hoy = date.today()
    lista = []
    anio, mes = hoy.year, hoy.month
    for _ in range(meses):
        lista.append((anio, mes))
        mes -= 1
        if mes == 0:
            anio, mes = anio - 1, 12
    lista.reverse()

    inicio = f"{lista[0][0]:04d}-{lista[0][1]:02d}-01"
    with conexion() as conn:
        filas = conn.execute("""
            SELECT strftime('%Y-%m', fecha), SUM(total)
            FROM ventas
            WHERE date(fecha) >= ?
            GROUP BY strftime('%Y-%m', fecha)
        """, (inicio,)).fetchall()

    totales = dict(filas)
    nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
               "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    etiquetas = [f"{nombres[m - 1]} {str(a)[2:]}" for a, m in lista]
    valores = [totales.get(f"{a:04d}-{m:02d}", 0) for a, m in lista]
    return etiquetas, valores

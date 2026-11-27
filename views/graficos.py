from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

AZUL = "#2563EB"
VERDE = "#16A34A"
TEXTO = "#334155"
SUAVE = "#94A3B8"
LINEA = "#E2E8F0"


def crear_grafico(parent):
    figura = Figure(figsize=(5, 3.4), dpi=100, facecolor="white")
    eje = figura.add_subplot(111)
    canvas = FigureCanvasTkAgg(figura, master=parent)
    return figura, eje, canvas


def preparar_eje(eje):
    eje.clear()
    eje.set_facecolor("white")
    for lado in ("top", "right", "left"):
        eje.spines[lado].set_visible(False)
    eje.spines["bottom"].set_color(LINEA)
    eje.tick_params(colors=TEXTO, labelsize=8, length=0)


def sin_datos(eje, texto):
    eje.text(0.5, 0.5, texto, ha="center", va="center",
             color=SUAVE, fontsize=10, transform=eje.transAxes)
    eje.set_xticks([])
    eje.set_yticks([])
    eje.spines["bottom"].set_visible(False)


def dibujar_mas_vendidos(figura, eje, canvas, datos):
    preparar_eje(eje)

    if not datos:
        sin_datos(eje, "Sin ventas en este período")
    else:
        nombres = [fila[0] for fila in reversed(datos)]
        unidades = [fila[1] for fila in reversed(datos)]
        barras = eje.barh(nombres, unidades, color=AZUL, height=0.55)
        eje.bar_label(barras, padding=4, color=TEXTO, fontsize=8)
        eje.xaxis.set_visible(False)
        eje.spines["bottom"].set_visible(False)
        eje.set_xlim(0, max(unidades) * 1.18)

    figura.tight_layout()
    canvas.draw()


def dibujar_ingresos(figura, eje, canvas, etiquetas, valores, por_mes):
    preparar_eje(eje)

    if not any(valores):
        sin_datos(eje, "Sin ingresos en este período")
    else:
        posiciones = range(len(valores))
        if por_mes:
            eje.bar(posiciones, valores, color=VERDE, width=0.6)
        else:
            eje.plot(posiciones, valores, color=VERDE, linewidth=2,
                     marker="o", markersize=3)
            eje.fill_between(posiciones, valores, color=VERDE, alpha=0.12)

        paso = max(1, len(etiquetas) // 8)
        eje.set_xticks(list(posiciones)[::paso])
        eje.set_xticklabels(etiquetas[::paso])
        eje.yaxis.set_major_formatter(lambda valor, _: f"${valor:,.0f}")
        eje.grid(axis="y", color=LINEA, linewidth=0.8)
        eje.set_axisbelow(True)
        eje.set_ylim(bottom=0)

    figura.tight_layout()
    canvas.draw()

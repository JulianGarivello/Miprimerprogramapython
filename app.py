import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import unicodedata
import re
from datetime import datetime
from io import BytesIO

# ─────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard · Muestras 2026",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────
# ESTILOS PERSONALIZADOS
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Mono', monospace;
    }

    h1, h2, h3 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 800 !important;
    }

    .block-container { padding-top: 2rem; padding-bottom: 2rem; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #13161e;
        border: 1px solid #252836;
        border-radius: 12px;
        padding: 16px 20px !important;
    }

    [data-testid="metric-container"] label {
        font-size: 0.65rem !important;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #6b7280 !important;
    }

    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: 'Syne', sans-serif !important;
        font-size: 2.4rem !important;
        font-weight: 800 !important;
    }

    div[data-testid="stHorizontalBlock"] { gap: 1rem; }

    .section-title {
        font-family: 'Syne', sans-serif;
        font-size: 0.65rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #e8c547;
        margin: 2rem 0 1rem 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #252836;
    }

    .stDataFrame { border-radius: 12px; overflow: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────
def normalizar(s: str) -> str:
    """Quita tildes, espacios y guiones bajos, convierte a mayúsculas."""
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[\s_]+", "", s).upper()


def buscar_col(columnas, fragmento: str):
    for col in columnas:
        if fragmento in normalizar(col):
            return col
    return None


# ─────────────────────────────────────────────────────────────────
# CARGA Y PROCESAMIENTO
# ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def cargar_datos(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_excel(BytesIO(file_bytes), sheet_name="2026")
    df.columns = df.columns.str.strip().str.upper()
    return df


def procesar(df: pd.DataFrame) -> dict:
    cols = df.columns

    COL_DISEÑADOR  = buscar_col(cols, "DISENADOR")
    COL_TECNOLOGIA = buscar_col(cols, "TECNOLOG")
    COL_MAQUINA    = buscar_col(cols, "MAQUINA")
    COL_ESTADO     = buscar_col(cols, "ESTADOMUESTRA")
    COL_F_INGRESO  = buscar_col(cols, "FECHAINGRESO")
    COL_F_TRABAJO  = buscar_col(cols, "FECHATRABAJO")
    COL_F_ENTREGA  = buscar_col(cols, "FECHAENTREGA")
    COL_F_MUESTRA  = buscar_col(cols, "ENTREGAMUESTRA")

    missing = [name for name, col in [
        ("DISEÑADOR", COL_DISEÑADOR), ("TECNOLOGÍA", COL_TECNOLOGIA),
        ("MÁQUINA", COL_MAQUINA), ("ESTADO MUESTRA", COL_ESTADO),
        ("FECHA INGRESO", COL_F_INGRESO), ("FECHA TRABAJO", COL_F_TRABAJO),
        ("FECHA ENTREGA", COL_F_ENTREGA), ("ENTREGA MUESTRA", COL_F_MUESTRA),
    ] if col is None]

    if missing:
        st.error(f"❌ No se encontraron las columnas: {', '.join(missing)}")
        st.stop()

    # Limpiar
    for col in [COL_F_INGRESO, COL_F_TRABAJO, COL_F_ENTREGA, COL_F_MUESTRA]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in [COL_TECNOLOGIA, COL_MAQUINA, COL_DISEÑADOR, COL_ESTADO]:
        df[col] = df[col].astype(str).str.upper().str.strip()

    # Filtrar filas sin diseñador
    df = df[~df[COL_DISEÑADOR].isin(["", "NAN", "NULL", "NAT"])]

    muestras = {
        "DIGITAL":      {"ATEXCO": 0, "REGGIANI": 0, "MIMAKI": 0},
        "CONVENCIONAL": {"ROTATIVA": 0, "PLANA": 0},
    }
    lead_time   = {"DIGITAL": [], "CONVENCIONAL": []}
    cumplimiento = {}
    pendientes   = {}

    for _, fila in df.iterrows():
        diseñador  = fila[COL_DISEÑADOR]
        tecnologia = fila[COL_TECNOLOGIA]
        maquina    = fila[COL_MAQUINA]
        estado     = fila[COL_ESTADO]

        f_ingreso = fila[COL_F_INGRESO]
        f_trabajo = fila[COL_F_TRABAJO]
        f_entrega = fila[COL_F_ENTREGA]
        f_muestra = fila[COL_F_MUESTRA]

        es_digital      = tecnologia.startswith("DIGIT")
        es_convencional = tecnologia.startswith("CONVENC")

        # Pendientes
        pendientes.setdefault(diseñador, 0)
        if pd.isna(f_entrega):
            pendientes[diseñador] += 1

        # Muestras en proceso
        if estado == "EN PROCESO":
            if es_digital:
                if   maquina == "ATEXCO":   muestras["DIGITAL"]["ATEXCO"]   += 1
                elif maquina == "REGGIANI": muestras["DIGITAL"]["REGGIANI"] += 1
                elif maquina == "MIMAKI":   muestras["DIGITAL"]["MIMAKI"]   += 1
            elif es_convencional:
                if   maquina == "ROTATIVA": muestras["CONVENCIONAL"]["ROTATIVA"] += 1
                elif maquina == "PLANA":    muestras["CONVENCIONAL"]["PLANA"]    += 1

        # Lead time
        if not pd.isna(f_ingreso) and not pd.isna(f_muestra):
            dias = (f_muestra - f_ingreso).days
            if   es_digital:      lead_time["DIGITAL"].append(dias)
            elif es_convencional: lead_time["CONVENCIONAL"].append(dias)

        # Cumplimiento
        cumplimiento.setdefault(diseñador, {"CUMPLIDAS": 0, "INCUMPLIDAS": 0})
        if not pd.isna(f_trabajo) and not pd.isna(f_entrega):
            if f_entrega <= f_trabajo:
                cumplimiento[diseñador]["CUMPLIDAS"]   += 1
            else:
                cumplimiento[diseñador]["INCUMPLIDAS"] += 1

    def prom(lst):
        return sum(lst) / len(lst) if lst else 0.0

    return {
        "muestras":    muestras,
        "lead_time":   {
            "digital":      {"avg": prom(lead_time["DIGITAL"]),      "n": len(lead_time["DIGITAL"])},
            "convencional": {"avg": prom(lead_time["CONVENCIONAL"]), "n": len(lead_time["CONVENCIONAL"])},
        },
        "pendientes":   pendientes,
        "cumplimiento": cumplimiento,
        "total_filas":  len(df),
    }


# ─────────────────────────────────────────────────────────────────
# COLORES
# ─────────────────────────────────────────────────────────────────
COLORS = {
    "ATEXCO":   "#34d399",
    "REGGIANI": "#a78bfa",
    "MIMAKI":   "#fbbf24",
    "ROTATIVA": "#f87171",
    "PLANA":    "#60a5fa",
    "DIGITAL":  "#4fc3f7",
    "CONV":     "#f06292",
}

PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono", color="#9ca3af", size=12),
        margin=dict(l=16, r=16, t=32, b=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    )
)


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────
def main():
    # ── Header ──
    st.markdown("""
        <h1 style='font-family:Syne,sans-serif;font-weight:800;letter-spacing:-0.03em;margin-bottom:0'>
            MUESTRAS <span style='color:#e8c547'>2026</span>
        </h1>
        <p style='font-size:0.75rem;color:#6b7280;letter-spacing:0.12em;text-transform:uppercase;margin-top:4px'>
            Dashboard · Análisis de Estampación
        </p>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Upload ──
    uploaded = st.file_uploader(
        "Carga la base de datos actualizada",
        type=["xlsx", "xls"],
        help="Debe contener una hoja llamada '2026'",
    )

    if not uploaded:
        st.info("📂 Sube el archivo Excel para visualizar el dashboard.")
        return

    with st.spinner("Procesando datos…"):
        df_raw = cargar_datos(uploaded.read())
        data   = procesar(df_raw)

    m   = data["muestras"]
    lt  = data["lead_time"]
    pen = data["pendientes"]
    cum = data["cumplimiento"]

    total_d = sum(m["DIGITAL"].values())
    total_c = sum(m["CONVENCIONAL"].values())
    total_g = total_d + total_c

    st.caption(f"✅ Archivo: **{uploaded.name}** · {data['total_filas']:,} filas procesadas")

    # ────────────────────────────────────────────────────────────
    # SECCIÓN 1 · MUESTRAS EN PROCESO
    # ────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Muestras en proceso</div>", unsafe_allow_html=True)

    # KPI row
    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
    c1.metric("🔢 Total", total_g)
    c2.metric("💠 Digital", total_d)
    c3.metric("Atexco",   m["DIGITAL"]["ATEXCO"])
    c4.metric("Reggiani", m["DIGITAL"]["REGGIANI"])
    c5.metric("Mimaki",   m["DIGITAL"]["MIMAKI"])
    c6.metric("🔶 Convencional", total_c)
    c7.metric("Rotativa", m["CONVENCIONAL"]["ROTATIVA"])
    c8.metric("Plana",    m["CONVENCIONAL"]["PLANA"])

    st.write("")

    col_left, col_right, col_bar = st.columns([1, 1, 2])

    # Doughnut Digital
    with col_left:
        fig_d = go.Figure(go.Pie(
            labels=["Atexco", "Reggiani", "Mimaki"],
            values=[m["DIGITAL"]["ATEXCO"], m["DIGITAL"]["REGGIANI"], m["DIGITAL"]["MIMAKI"]],
            hole=0.65,
            marker_colors=[COLORS["ATEXCO"], COLORS["REGGIANI"], COLORS["MIMAKI"]],
            textinfo="label+percent",
            textfont=dict(size=11),
        ))
        fig_d.update_layout(
            title="Tecnología Digital",
            **PLOTLY_TEMPLATE["layout"],
            height=300,
            showlegend=False,
        )
        st.plotly_chart(fig_d, use_container_width=True)

    # Doughnut Convencional
    with col_right:
        fig_c = go.Figure(go.Pie(
            labels=["Rotativa", "Plana"],
            values=[m["CONVENCIONAL"]["ROTATIVA"], m["CONVENCIONAL"]["PLANA"]],
            hole=0.65,
            marker_colors=[COLORS["ROTATIVA"], COLORS["PLANA"]],
            textinfo="label+percent",
            textfont=dict(size=11),
        ))
        fig_c.update_layout(
            title="Tecnología Convencional",
            **PLOTLY_TEMPLATE["layout"],
            height=300,
            showlegend=False,
        )
        st.plotly_chart(fig_c, use_container_width=True)

    # Bar comparativa
    with col_bar:
        labels = ["Atexco", "Reggiani", "Mimaki", "Rotativa", "Plana"]
        values = [
            m["DIGITAL"]["ATEXCO"], m["DIGITAL"]["REGGIANI"], m["DIGITAL"]["MIMAKI"],
            m["CONVENCIONAL"]["ROTATIVA"], m["CONVENCIONAL"]["PLANA"],
        ]
        colors = [COLORS[k] for k in ["ATEXCO", "REGGIANI", "MIMAKI", "ROTATIVA", "PLANA"]]

        fig_b = go.Figure(go.Bar(
            x=labels, y=values,
            marker_color=colors,
            text=values, textposition="outside",
        ))
        fig_b.update_layout(
            title="Comparativa General",
            **PLOTLY_TEMPLATE["layout"],
            height=300,
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="#252836"),
        )
        st.plotly_chart(fig_b, use_container_width=True)

    # ────────────────────────────────────────────────────────────
    # SECCIÓN 2 · LEAD TIME
    # ────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Lead time promedio del proceso</div>", unsafe_allow_html=True)

    lt_col1, lt_col2 = st.columns(2)

    with lt_col1:
        st.metric(
            label=f"💠 Lead Time Digital  ·  n={lt['digital']['n']} muestras",
            value=f"{lt['digital']['avg']:.1f} días",
            help="Promedio de días entre fecha de ingreso y fecha de entrega de muestra (tecnología digital)",
        )

    with lt_col2:
        st.metric(
            label=f"🔶 Lead Time Convencional  ·  n={lt['convencional']['n']} muestras",
            value=f"{lt['convencional']['avg']:.1f} días",
            help="Promedio de días entre fecha de ingreso y fecha de entrega de muestra (tecnología convencional)",
        )

    # ────────────────────────────────────────────────────────────
    # SECCIÓN 3 · PENDIENTES POR DISEÑADOR
    # ────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Pendientes por diseñador</div>", unsafe_allow_html=True)

    df_pen = (
        pd.DataFrame(
            [(d, c) for d, c in pen.items() if c > 0],
            columns=["Diseñador", "Pendientes"],
        )
        .sort_values("Pendientes", ascending=False)
        .reset_index(drop=True)
    )
    df_pen.index += 1

    if df_pen.empty:
        st.success("✅ Sin pendientes registrados.")
    else:
        pen_col1, pen_col2 = st.columns([1, 2])

        with pen_col1:
            st.dataframe(
                df_pen,
                use_container_width=True,
                height=min(400, 40 + len(df_pen) * 35),
            )

        with pen_col2:
            fig_pen = px.bar(
                df_pen,
                x="Pendientes", y="Diseñador",
                orientation="h",
                color="Pendientes",
                color_continuous_scale=["#252836", "#e8c547"],
                text="Pendientes",
            )
            fig_pen.update_traces(textposition="outside")
            fig_pen.update_layout(
                **PLOTLY_TEMPLATE["layout"],
                height=max(300, len(df_pen) * 32 + 60),
                showlegend=False,
                coloraxis_showscale=False,
                yaxis=dict(autorange="reversed"),
                xaxis=dict(gridcolor="#252836"),
            )
            st.plotly_chart(fig_pen, use_container_width=True)

    # ────────────────────────────────────────────────────────────
    # SECCIÓN 4 · CUMPLIMIENTO POR DISEÑADOR
    # ────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Cumplimiento por diseñador</div>", unsafe_allow_html=True)
    st.caption("⚠️ Se excluye a **Julián Garivello**")

    EXCLUIR_NORM = normalizar("Julián Garivello")

    rows_cum = []
    for dis, d in cum.items():
        if EXCLUIR_NORM in normalizar(dis):
            continue
        total = d["CUMPLIDAS"] + d["INCUMPLIDAS"]
        pct   = d["CUMPLIDAS"] / total * 100 if total > 0 else 0.0
        rows_cum.append({
            "Diseñador":    dis,
            "Cumplidas":    d["CUMPLIDAS"],
            "Incumplidas":  d["INCUMPLIDAS"],
            "Total":        total,
            "%":            round(pct, 1),
        })

    df_cum = (
        pd.DataFrame(rows_cum)
        .sort_values("%", ascending=False)
        .reset_index(drop=True)
    )
    df_cum.index += 1

    if df_cum.empty:
        st.info("Sin datos de cumplimiento.")
    else:
        cum_col1, cum_col2 = st.columns([1, 2])

        with cum_col1:
            st.dataframe(
                df_cum,
                use_container_width=True,
                height=min(500, 40 + len(df_cum) * 35),
                column_config={
                    "%": st.column_config.ProgressColumn(
                        "Cumplimiento %",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    ),
                },
            )

        with cum_col2:
            fig_cum = go.Figure()
            fig_cum.add_trace(go.Bar(
                name="Cumplidas",
                y=df_cum["Diseñador"],
                x=df_cum["Cumplidas"],
                orientation="h",
                marker_color=COLORS["ATEXCO"],
                text=df_cum["Cumplidas"],
                textposition="inside",
            ))
            fig_cum.add_trace(go.Bar(
                name="Incumplidas",
                y=df_cum["Diseñador"],
                x=df_cum["Incumplidas"],
                orientation="h",
                marker_color=COLORS["ROTATIVA"],
                text=df_cum["Incumplidas"],
                textposition="inside",
            ))
            _cum_layout = {**PLOTLY_TEMPLATE["layout"]}
            _cum_layout["barmode"] = "stack"
            _cum_layout["height"] = max(350, len(df_cum) * 32 + 80)
            _cum_layout["yaxis"] = dict(autorange="reversed")
            _cum_layout["xaxis"] = dict(gridcolor="#252836")
            _cum_layout["legend"] = dict(orientation="h", y=1.05, bgcolor="rgba(0,0,0,0)", font=dict(size=11))
            fig_cum.update_layout(**_cum_layout)
            st.plotly_chart(fig_cum, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()

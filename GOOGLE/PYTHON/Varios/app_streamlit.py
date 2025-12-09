import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Configuración básica de la página
st.set_page_config(page_title="Demo Streamlit completa", layout="wide")
sns.set_style("darkgrid")

st.title("📊 Demo completa de Streamlit")
st.write(
    "Ejemplo rápido de lo que puede hacer Streamlit: "
    "sidebar interactiva, tablas, estadísticas, gráficos y layouts."
)

# ───────────────────────── SIDEBAR ─────────────────────────
st.sidebar.header("Opciones")

demo = st.sidebar.radio(
    "Elige demo:",
    ["Pingüinos (dataset real)", "Datos aleatorios"],
)

mostrar_datos = st.sidebar.checkbox("Mostrar tabla de datos", value=True)

# ───────────────────────── DEMO 1: PINGÜINOS ─────────────────────────
if demo == "Pingüinos (dataset real)":
    st.subheader("🐧 Dataset de pingüinos (Seaborn)")

    df = sns.load_dataset("penguins").dropna()

    # Controles interactivos
    especies = ["Todas"] + sorted(df["species"].unique().tolist())
    especie_sel = st.sidebar.selectbox("Especie", especies)

    columnas_numericas = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    x_feat = st.sidebar.selectbox("Eje X", columnas_numericas, index=0)
    y_feat = st.sidebar.selectbox("Eje Y", columnas_numericas, index=3)

    # Filtro por especie
    if especie_sel != "Todas":
        df_plot = df[df["species"] == especie_sel]
    else:
        df_plot = df

    # Layout en columnas
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Estadísticas básicas")
        st.write(df_plot[columnas_numericas].describe())

    with col2:
        st.markdown("### Gráfico de dispersión (Seaborn + Matplotlib)")
        fig, ax = plt.subplots()
        sns.scatterplot(
            data=df_plot,
            x=x_feat,
            y=y_feat,
            hue="species",
            style="sex",
            ax=ax,
        )
        ax.set_title(f"{y_feat} vs {x_feat}")
        st.pyplot(fig)

    if mostrar_datos:
        st.markdown("### Datos filtrados")
        st.dataframe(df_plot)

    # Correlaciones
    st.markdown("### Mapa de correlación")
    corr = df[columnas_numericas].corr()
    fig_corr, ax_corr = plt.subplots()
    sns.heatmap(corr, annot=True, cmap="viridis", ax=ax_corr)
    st.pyplot(fig_corr)

# ───────────────────────── DEMO 2: DATOS ALEATORIOS ─────────────────────────
else:
    st.subheader("🎲 Datos aleatorios (simulación)")

    n_puntos = st.sidebar.slider("Número de puntos", min_value=10, max_value=500, value=100, step=10)
    ruido = st.sidebar.slider("Nivel de ruido", min_value=0.0, max_value=2.0, value=0.5, step=0.1)

    x = np.linspace(0, 10, n_puntos)
    y = np.sin(x) + np.random.normal(scale=ruido, size=n_puntos)

    df_rand = pd.DataFrame({"x": x, "y": y})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Línea interactiva (Streamlit nativo)")
        st.line_chart(df_rand, x="x", y="y")

    with col2:
        st.markdown("### Histograma (Matplotlib)")
        fig_hist, ax_hist = plt.subplots()
        ax_hist.hist(y, bins=20)
        ax_hist.set_title("Distribución de valores de y")
        st.pyplot(fig_hist)

    if mostrar_datos:
        st.markdown("### Datos generados")
        st.dataframe(df_rand)

st.markdown("---")
st.caption("Demo hecha para que trastees con sliders, selects y gráficos sin tocar HTML.")

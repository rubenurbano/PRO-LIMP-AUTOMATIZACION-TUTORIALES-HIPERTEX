# app_streamlit_sheets.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Streamlit + Google Sheets", layout="wide")

st.title("📈 Demo Streamlit con datos de Google Sheets")

st.write(
    "Esta app carga datos desde una hoja de Google Sheets publicada como CSV "
    "y muestra una tabla y un gráfico simple."
)

st.sidebar.header("Configuración")

# 👉 Pega aquí tu URL de Google Sheets publicada como CSV
default_url = "https://docs.google.com/spreadsheets/d/TU_ID/export?format=csv"

gsheet_url = st.sidebar.text_input(
    "URL de la hoja Google Sheets (CSV):",
    value=default_url,
    help="Usa la URL que obtienes al publicar la hoja como CSV."
)

cargar = st.sidebar.button("Cargar datos")

if cargar:
    if not gsheet_url or "http" not in gsheet_url:
        st.error("Por favor, introduce una URL válida de Google Sheets publicada como CSV.")
    else:
        try:
            st.write("Leyendo datos desde Google Sheets...")
            df = pd.read_csv(gsheet_url)

            st.subheader("✅ Datos cargados")
            st.dataframe(df)

            # Intentamos detectar columnas numéricas automáticamente
            numeric_cols = df.select_dtypes(include="number").columns.tolist()

            if len(numeric_cols) >= 2:
                st.subheader("📊 Gráfico de líneas interactivo")

                x_col = st.selectbox("Columna eje X:", numeric_cols, index=0)
                y_col = st.selectbox("Columna eje Y:", numeric_cols, index=1)

                fig, ax = plt.subplots()
                ax.plot(df[x_col], df[y_col], marker="o")
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f"{y_col} en función de {x_col}")
                st.pyplot(fig)
            else:
                st.warning(
                    "No se encontraron al menos 2 columnas numéricas para graficar. "
                    "Asegúrate de que tu hoja tenga números (no texto) en algunas columnas."
                )

        except Exception as e:
            st.error(f"Error leyendo la hoja: {e}")

else:
    st.info("Introduce la URL de tu Google Sheets publicada como CSV y pulsa 'Cargar datos'.")

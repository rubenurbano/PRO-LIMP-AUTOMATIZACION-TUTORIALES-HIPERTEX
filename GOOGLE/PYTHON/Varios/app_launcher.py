import streamlit as st
import subprocess
import sys
import os
import platform
import tempfile
import uuid

st.set_page_config(page_title="🔧 Lanzador de Scripts Locales", layout="centered")
st.title("🔧 Lanzador de Scripts (.ps1, .bat, .py, .sh)")

st.write(
    "Selecciona un archivo local y ejecútalo desde esta interfaz. "
    "Funciona solo en entorno local por seguridad."
)

file_path = st.file_uploader(
    "Elige un script:",
    type=["ps1", "bat", "py", "sh"],
    help="Formatos permitidos: .ps1, .bat, .py, .sh"
)

if file_path:
    # Carpeta temporal del sistema (NO la carpeta de tus scripts)
    temp_dir = tempfile.gettempdir()
    unique_name = f"launcher_{uuid.uuid4().hex}_{file_path.name}"
    temp_path = os.path.join(temp_dir, unique_name)

    # Guardamos solo una COPIA en temp
    with open(temp_path, "wb") as f:
        f.write(file_path.read())

    st.success(f"Archivo cargado (copia temporal): {file_path.name}")

    if st.button("🚀 Ejecutar script seleccionado"):
        st.write("Ejecutando, espera un momento...")

        ext = os.path.splitext(temp_path)[1].lower()
        system = platform.system().lower()

        try:
            if ext == ".ps1":
                cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", temp_path]
            elif ext == ".bat":
                cmd = [temp_path]
            elif ext == ".py":
                cmd = [sys.executable, temp_path]
            elif ext == ".sh":
                if "windows" in system:
                    cmd = ["bash", temp_path]  # Requiere Git Bash o WSL
                else:
                    cmd = ["bash", temp_path]
            else:
                st.error("Tipo de archivo no soportado.")
                st.stop()

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            st.subheader("📄 Salida del script:")
            st.code(result.stdout or "(sin salida)")

            if result.stderr:
                st.subheader("⚠️ Errores:")
                st.code(result.stderr)

            st.success("✅ Ejecución finalizada.")

        except Exception as e:
            st.error(f"Error al ejecutar el script: {e}")

        # Ahora sí, BORRAMOS SOLO LA COPIA TEMPORAL
        try:
            os.remove(temp_path)
        except OSError:
            pass

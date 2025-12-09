import streamlit as st

st.title("Mi primera aplicación Streamlit")

st.write("¡Hola, Streamlit!")

# Un slider de ejemplo
valor = st.slider("Selecciona un valor", 0, 100, 25)
st.write(f"El valor seleccionado es: {valor}")

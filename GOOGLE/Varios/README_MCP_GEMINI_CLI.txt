# README_MCP_GEMINI_CLI.txt
# ----------------------------------------------------------
# Referencia oficial – Integración de MCP en Gemini CLI
# Autor: Rubén Urbano
# Carpeta: HIPERTEX
# Fecha: 08/11/2025
# ----------------------------------------------------------

## 1. Situación actual (confirmada)
El entorno `Gemini CLI` ya incluye **soporte nativo para MCP** (Model Context Protocol).
Esto se comprueba porque al ejecutar dentro del CLI el comando:

    /mcp

muestra los subcomandos disponibles:

    list      → Lista los servidores MCP configurados
    desc      → Describe los servidores MCP y sus herramientas
    schema    → Muestra los esquemas de las herramientas
    auth      → Autenticación (para MCPs con OAuth)
    refresh   → Reinicia los MCPs activos

Cuando se ejecuta:

    /mcp list

el resultado actual es:

    No MCP servers configured.
    Please view MCP documentation in your browser:
    https://goo.gle/gemini-cli-docs-mcp

Esto confirma que **la función MCP está activada**, pero **no hay servidores registrados aún**.

---

## 2. Qué comandos funcionan hoy
✅ `/mcp` → Muestra el menú MCP y ayuda contextual.  
✅ `/mcp list` → Lista los MCP configurados (vacío si no hay ninguno).  
✅ `/mcp desc`, `/mcp schema`, `/mcp refresh` → Comandos activos pero dependientes de MCPs registrados.  

Actualmente Gemini CLI **no permite añadir MCPs locales directamente** (la opción `/mcp add` aún no está disponible en esta build).

---

## 3. Qué esperar en la próxima actualización
🔜 Google está desplegando progresivamente el soporte completo para:

/mcp add <nombre> --command "python" --args "mcp_server.py"


Ese comando permitirá registrar **servidores MCP locales** que se ejecutan por STDIO o WebSocket (como `ServidorMCP_Ruben`).

Una vez disponible:
1. Gemini CLI lanzará el proceso (`python mcp_server.py`).
2. Detectará automáticamente las herramientas (`get_time`, `hola`, etc.).
3. Podrá ejecutarlas directamente desde el entorno Gemini o usarlas dentro de flujos de trabajo IA.

---

## 4. Estado actual de Rubén Urbano
✅ FastMCP instalado correctamente (v2.13.0.2).  
✅ Servidor MCP funcional (`mcp_server.py`) en modo STDIO.  
✅ Gemini CLI reconoce el módulo MCP y los comandos de gestión.  
🚧 Falta que Google habilite el registro manual (`/mcp add` o `/mcp connect`).  

---

## 5. Próximos pasos sugeridos
1. Mantener actualizado `Gemini CLI`:

gemini update

2. Revisar periódicamente la documentación oficial:
https://goo.gle/gemini-cli-docs-mcp
3. Preparar el archivo `mcp_server.py` como imagen Docker (para futura ejecución remota).
4. Esperar la activación del registro MCP local para vincular el servidor Rubén-MCP.

---

# Conclusión
El entorno `HIPERTEX` está completamente preparado para la integración MCP.
Una vez activado el registro local, el servidor `ServidorMCP_Ruben` podrá conectarse directamente a Gemini CLI y compartir herramientas con el modelo de IA sin intermediarios.

# Rubén Urbano – HIPERTEX – 2025



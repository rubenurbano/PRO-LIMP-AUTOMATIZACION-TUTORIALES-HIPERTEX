import yt_dlp

# Carpeta donde se guardarán los vídeos
OUTPUT_TEMPLATE = r"C:\Users\rubenurbano\videosyt\%(title)s.%(ext)s"


def progress_hook(d):
    status = d.get("status")

    if status == "downloading":
        percent = d.get("_percent_str", "").strip()
        speed = d.get("_speed_str", "").strip()
        eta = d.get("_eta_str", "").strip()
        print(f"\rDescargando... {percent}  |  Velocidad: {speed}  |  ETA: {eta}   ", end="", flush=True)

    elif status == "finished":
        print("\n✅ Descarga completada. Procesando archivo...")


def main():
    url = input("Pega la URL de YouTube: ").strip()

    if not url:
        print("No se ingresó ninguna URL. Saliendo.")
        return

    ydl_opts = {
        "outtmpl": OUTPUT_TEMPLATE,
        "format": "bestvideo+bestaudio/best",  # mejor calidad disponible
        "progress_hooks": [progress_hook],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("✅ Vídeo guardado en tu carpeta de Videos.")
    except Exception as e:
        print("\n❌ Ocurrió un error durante la descarga:")
        print(repr(e))


if __name__ == "__main__":
    main()

from pytube import YouTube

url = "https://www.youtube.com/watch?v=LYAbV6RLLXE"

try:
    yt = YouTube(url)
    print("Título:", yt.title)
    print("Views:", yt.views)
except Exception as e:
    print("ERROR TYPE:", type(e))
    print("ERROR REPR:", repr(e))

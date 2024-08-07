from pytube import YouTube, Playlist
from youtube_search import YoutubeSearch
import os
from pydub import AudioSegment


url = 'https://www.youtube.com/watch?v=AEoci8pjC7Y&ab_channel=CentralRecord'

yt = YouTube(url)
stream = yt.streams.filter(only_audio=True).first()
output_path = stream.download()
_, file = os.path.split(output_path)
file = file[:-4]

print(file)


# Cargar el archivo de audio
audio = AudioSegment.from_file("temp/speech.mp3")
audio = audio + 10
audio.export("temp/speech.mp3", format="mp3")

# Guardar el archivo con el volumen aumentado
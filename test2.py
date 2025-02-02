import os
import asyncio
from youtube_search import YoutubeSearch

from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress

query = 'hola'

results = YoutubeSearch(query, max_results=5).to_dict()

videos = [YouTube("https://www.youtube.com" + result['url_suffix']) for result in results]

searches = ''
n = 1
for video in videos:
    searches += f'{n}. 🎶 **{video.author}** - {video.title}\n'
    print(searches)
    n += 1

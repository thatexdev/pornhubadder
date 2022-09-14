from pyrogram.types import ReplyKeyboardRemove
from pyrogram import Client, filters
from youtube_dl import YoutubeDL
import os
import wget
from pyromod.helpers import ikb, array_chunk
import subprocess

apiID = 3910389
apiHash = '86f861352f0ab76a251866059a6adbd6'
botToken = '5751159360:AAHbgHXe8Gy9KY6jX1821GwwZd_NGsDY3B0'
allowedUsers = [5680166111]
app = Client('bot', api_id=apiID, api_hash=apiHash, bot_token=botToken)
lastURL = {}


@app.on_message(filters.regex(r'^\/start$') & filters.user(allowedUsers))
async def startBot(c, m):
    lastURL[m.from_user.id] = ''
    await m.reply('To start downloading, send a link from the Porn Hub site, e.g :\nhttps://www.pornhub.com/view_video.php?viewkey=ph5ef8d4462fb64',
                  quote=True,
                  reply_markup=ReplyKeyboardRemove(),
                  disable_web_page_preview=True
                  )


@app.on_message(filters.regex(r'^(https|http):\/\/www.pornhub.com\/view_video.php\?viewkey=(.*)$') & filters.user(allowedUsers))
async def extractVideo(c, m):
    with YoutubeDL() as ydl:
        videoInformation = ydl.extract_info(m.text, download=False)
        videoTitle = videoInformation.get('title', None)
        videoDuration = videoInformation.get('duration', None)
        videoLikes = videoInformation.get('like_count', None)
        videoDislikes = videoInformation.get('dislike_count', None)
        videoComments = videoInformation.get('comment_count', None)
        downloadKeyboards = []
        for i in videoInformation.get('formats', None):
            if i['format_id'].endswith('1'):
                downloadKeyboards.append((i['height'], f'dl:{i["format_id"]}'))
        await m.reply_photo(
            videoInformation.get('thumbnail', None),
            quote=True,
            caption=f'🎥**{videoTitle}**\n-\n👍 {videoLikes}\n👎 {videoDislikes}\n💌 {videoComments}\n⏱ {videoDuration} s\n\nChoose the quality you want to download :',
            reply_markup=ikb(array_chunk(downloadKeyboards, 2))
        )
        lastURL[m.from_user.id] = m.text


@app.on_callback_query(filters.user(allowedUsers))
async def downloadVideo(c, m):
    await m.message.delete()
    sentMessage = await c.send_message(m.from_user.id, 'Downloading, please wait ...')
    lastVideo = lastURL[m.from_user.id]
    formatID = m.data.split(':')[1]
    with YoutubeDL() as ydl:
        videoInformation = ydl.extract_info(lastVideo, download=False)
        videoTitle = videoInformation.get('title', None)
        videoID = videoInformation.get('id', None)
        videoDuration = videoInformation.get('duration', None)
        videoThumbnail = videoInformation.get('thumbnail', None)
        for i in videoInformation.get('formats', None):
            if i['format_id'] == formatID:
                formatData = i
        subprocess.check_output(
            f'youtube-dl -f {formatID} {lastVideo}', shell=True)
    await sentMessage.edit('Uploading, please wait ...')
    downloadedPhoto = wget.download(videoThumbnail)
    await sentMessage.reply_video(f'{videoTitle}-{videoID}.mp4', quote=True, duration=videoDuration, width=formatData['width'], height=formatData['height'], supports_streaming=True, thumb=downloadedPhoto)
    os.remove(f'{videoTitle}-{videoID}.mp4')
    os.remove(downloadedPhoto)
    await sentMessage.edit('Done !')


app.run()

import yt_dlp

class MailDownloader():
    def __init__(self, logger, preferred_codec='wav', download_video=False):
        self. ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': preferred_codec,
            'preferredquality': '320',
            }],
        }
        self.ydl_video = {
            'format': 'best',
        }
        self.download_video = download_video
        self.logger = logger
        self.exceptions = {'Video': [], 'WAV': []}


    def download_all_uris(self, urls):
        self.logger.info("2. Downloading URLs")
        for i in range(len(urls)):
            try:
                self.download(link=urls[i])
            except Exception as e:
                self.logger.error("Encountered exception: ", e, "for file: ", urls[i])
        self.logger.info("2. Finished downloading")

    def download(self, link):
    # Download audio
        self.logger.info(f"Downloading {link}")
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([link])
        except Exception as e:
            self.logger.error(f"Exception while downloading WAV for {link}", exc_info=e)
            self.logger.error(e)
            self.exceptions['WAV'].append(link)

        # Download Video
        if self.download_video == True:
            try:
                with yt_dlp.YoutubeDL(self.ydl_video) as ydl:
                    ydl.download([link])
            except Exception as e:
                self.logger.error(f"Exception while downloading Video for {link}", exc_info=e)
                self.logger.error(e)
                self.exceptions['Video'].append(link)
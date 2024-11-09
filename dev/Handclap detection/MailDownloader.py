import yt_dlp
#from multiprocessing import Pool

exceptions = {'Video': [], 'WAV': []}

def download_all_uris(urls, logger, download_video=False):
    logger.info("2. Downloading URLs")
    #for parallelism. note - no args:
        # with Pool() as pool:
        #     try:
        #         pool.map(urls, download)
        #     except Exception as e:
        #         logger.error("Encountered exception: ", e, "for file: ", urls)
    for _, url in enumerate(urls):
        try:
            download(link=url, logger=logger, preferred_codec='wav', download_video=download_video)
        except KeyboardInterrupt:
            logger.info("Keyboard Interrupt")
            exit(1)
        except Exception as e:
            logger.error("Encountered exception: ", e, "for file: ", url)
    logger.info("2. Finished downloading")

def download(link, logger, preferred_codec='wav', download_video=False):
# Download audio
    ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': preferred_codec,
        'preferredquality': '320',
        }],
    }

    logger.info(f"Downloading {link}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
    except Exception as e:
        logger.error(f"Exception while downloading WAV for {link}", exc_info=e)
        logger.error(e)
        exceptions['WAV'].append(link)

    # Download Video
    if download_video is True:
        ydl_video = {
            'format': 'best',
        }
        try:
            with yt_dlp.YoutubeDL(ydl_video) as ydl:
                ydl.download([link])
        except Exception as e:
            logger.error(f"Exception while downloading Video for {link}", exc_info=e)
            logger.error(e)
            exceptions['Video'].append(link)

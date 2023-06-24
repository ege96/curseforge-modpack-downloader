from cfdownloader import ModpackDownloader

API_KEY = "CURSEFORGE_API_KEY"

downloader = ModpackDownloader(API_KEY)
downloader.download_modpack("PATH_TO_MODPACK_ZIP_FILE")

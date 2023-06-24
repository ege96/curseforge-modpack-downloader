import os

from dotenv import load_dotenv

from cfdownloader import ModpackDownloader

load_dotenv()
API_KEY = os.getenv("CURSEFORGE_API")

downloader = ModpackDownloader(API_KEY)
downloader.download_modpack()

from os import listdir, path

from .file_reader import ModpackFile
from .mod_downloader import HttpSession


def _search_for_modpack():
    possible_modpacks = []

    idx = 1

    for file in listdir():
        if file.endswith(".zip"):
            possible_modpacks.append(file)
            print(f"{idx}: {file}")
            idx += 1

    if len(possible_modpacks) == 0:
        print("No modpacks found, enter the path to the modpack zip file.")

        while True:
            file_path = input("File path: ")

            if path.isfile(file_path):
                ext = path.splitext(file_path)[-1].lower()
                if ext == ".zip":
                    return file_path

            print("Please enter a valid path to a zip file.")

    while True:
        try:
            choice = int(input("Which modpack would you like to download? "))
            if choice in range(1, len(possible_modpacks) + 1):
                return possible_modpacks[choice - 1]
            print(f"Please enter a number between 1 and {len(possible_modpacks)}.")

        except ValueError:
            print("Please enter a number.")


class ModpackDownloader:
    def __init__(self, api_key: str):
        if api_key is None:
            raise ValueError("API key cannot be None.")

        self.api_key = api_key

    def download_modpack(self, file_path: str = None, output_dir: str = "downloaded_modpacks") -> None:
        """Downloads a modpack from curseforge.

        Args:
            file_path (str): The path to the zip file.
            output_dir (str, optional): The directory to download the mods to. Defaults to "downloaded_modpacks".

        """
        if file_path is None:
            file_path = _search_for_modpack()

        modpack = ModpackFile(file_path, output_dir)
        modpack.unzip_and_extract()

        project_ids, file_ids = modpack.get_project_file_ids()
        print(f"Detected {len(project_ids)} mods.")

        with HttpSession(self.api_key) as session:
            mod_data = session.get_mod_data(project_ids, file_ids)
            session.download_mods(mod_data, modpack.output_dir)
            # session.alternate_download_data(modpack.manifest_data, modpack.output_dir)

        input("Press enter to exit.")

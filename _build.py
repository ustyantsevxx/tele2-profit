import os
import shutil
import zipfile

from _version import __version__


def remove_dir_if_exists(path):
    if os.path.isdir(path):
        shutil.rmtree(path)


def remove_file_if_exists(path):
    if os.path.isfile(path):
        os.remove(path)


def build_zip():
    os.system('pyinstaller --onefile --paths venv main.py')
    with zipfile.ZipFile(f'tele2-profit@{__version__}.zip', 'w',
                         zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write('dist/main.exe', 'main.exe')


if __name__ == '__main__':
    remove_file_if_exists(f'tele2-profit@{__version__}.zip')
    build_zip()
    remove_dir_if_exists('dist')
    remove_dir_if_exists('build')
    remove_dir_if_exists('__pycache__')
    remove_file_if_exists('main.spec')

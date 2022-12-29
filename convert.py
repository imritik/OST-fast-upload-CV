from docx2pdf import convert
import time
import sys
import os
import subprocess
import re


class Convert:
    def __init__(self, filename):
        self.toPdf(filename)
        self.convert_to('output', f'input\{filename}', timeout=15)

    def convert_to(self, folder, source, timeout=None):
        args = [self.libreoffice_exec(), '--headless', '--convert-to',
                'pdf', '--outdir', folder, source]

        process = subprocess.run(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        filename = re.search('-> (.*?) using filter', process.stdout.decode())

        return filename.group(1)

    def libreoffice_exec(self):
        if sys.platform == 'darwin':
            return '/Applications/LibreOffice.app/Contents/MacOS/soffice'
        return 'libreoffice'

    def toPdf(self, filename):

        ext = filename.split('.')[-1]

        if ext == 'docx':
            try:
                convert('input/', 'output/')
            except Exception as e:
                print(e)
        else:
            print("Format not supported.")


if __name__ == '__main__':
    now = time.time()
    Convert('sample.doc')

    end = time.time()

    print(end - now)
# -*- coding: utf-8 -*-
import magic

from samples.filetypes.filetype import FileTypeDetector


class MagicFileTypeDetector(FileTypeDetector):

    name = 'python-magic'

    def __init__(self):
        super(MagicFileTypeDetector, self).__init__()

    def from_file_pointer(self, fp):
        self.fp = fp
        content = self.fp.read()
        self.fp.seek(0)
        return self.from_file_content(content)

    def from_file_content(self, content):
        return (magic.from_buffer(content), self.name)

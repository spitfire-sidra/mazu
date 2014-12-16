# -*- coding: utf-8 -*-


class FileTypeDetector(object):

    """
    Parent class for file type detectors.
    """

    name = 'FileTypeDetector'

    def __init__(self):
        self.fp = None
        self.content = None

    def from_file_pointer(self, fp):
        """
        Identify the contents of file's pointer.
        This method must return a tuple('file type', 'name of detector').
        """
        pass

    def from_file_content(self, content):
        """
        Identify the contents of file.
        This method must return a tuple('file type', 'name of detector').
        """
        pass

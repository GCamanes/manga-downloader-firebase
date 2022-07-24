import glob
import os

from constants import ConstantsHandler

Constants = ConstantsHandler()


class ChapterFirebaseModel:
    def __init__(self):
        self.key = ''
        self.number = ''
        self.pages = []

    @classmethod
    def fromDict(cls, dictInput):
        obj = cls()  # cls.__new__(cls) does not call __init__ (if needed)

        try:
            obj.key = dictInput.get(Constants.MANGA_DOC_KEY) or ''
            obj.number = dictInput.get(Constants.CHAPTER_DOC_NUMBER) or ''
            obj.pages = dictInput.get(Constants.CHAPTER_DOC_PAGES) or []

            return obj
        except:
            return None

    @classmethod
    def fromPath(cls, path):
        obj = cls()  # cls.__new__(cls) does not call __init__ (if needed)

        if os.path.isdir(path):
            obj.key = path.split('/')[-1]
            obj.number = path.split('chap_')[-1]
            elementsInPath = glob.glob(path + '/*')
            for file in elementsInPath:
                if os.path.isfile(file):
                    obj.pages.append(file.split(Constants.MANGA_DL_PATH+'/')[-1])

            return obj

        else:
            return None

    def toString(self):
        return 'Chapter: {} ({})\npages: {}'.format(
            self.key,
            self.number,
            len(self.pages),
        )

    def toDict(self):
        return {
            Constants.MANGA_DOC_KEY: self.key,
            Constants.CHAPTER_DOC_NUMBER: self.number,
            Constants.CHAPTER_DOC_PAGES: sorted(self.pages),
        }

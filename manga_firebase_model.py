import os
import json

from constants import ConstantsHandler

Constants = ConstantsHandler()


class MangaFirebaseModel:
    def __init__(self):
        self.authors = []
        self.key = ''
        self.title = ''
        self.status = Constants.WRONG_LINK_CHECKING
        self.coverLink = None
        self.lastRelease = ''
        self.chapterKeys = []

    @classmethod
    def fromDict(cls, dictInput):
        obj = cls()  # cls.__new__(cls) does not call __init__ (if needed)
        # super(MangaInfoModel, obj).__init__() # Call any polymorphic base class initializers

        obj.key = dictInput.get(Constants.MANGA_DOC_KEY) or ''
        obj.title = dictInput.get(Constants.MANGA_DOC_TITLE) or ''
        obj.authors = dictInput.get(Constants.MANGA_DOC_AUTHORS) or []
        obj.status = dictInput.get(Constants.MANGA_DOC_STATUS) or ''
        obj.coverLink = dictInput.get(Constants.MANGA_DOC_COVER) or ''
        obj.lastRelease = dictInput.get(Constants.MANGA_DOC_LAST_RELEASE) or ''
        obj.chapterKeys = dictInput.get(Constants.MANGA_DOC_CHAPTER_KEYS) or []

        return obj

    def toString(self):
        return 'Title: {} ({})\nAuthors: {}\nStatus: {}'.format(self.title, self.key, self.authors,
                                                                self.status)

    def toDict(self):
        return {
            Constants.MANGA_DOC_KEY: self.key,
            Constants.MANGA_DOC_TITLE: self.title,
            Constants.MANGA_DOC_AUTHORS: self.authors,
            Constants.MANGA_DOC_STATUS: self.status,
            Constants.MANGA_DOC_COVER: self.coverLink,
            Constants.MANGA_DOC_LAST_RELEASE: self.lastRelease,
            Constants.MANGA_DOC_CHAPTER_KEYS: self.chapterKeys,
        }

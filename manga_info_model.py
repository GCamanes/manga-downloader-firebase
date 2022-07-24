import os
import subprocess
import json

from constants import ConstantsHandler
from function_helper import FunctionHelper

Constants = ConstantsHandler()
FunctionHelper = FunctionHelper()


class MangaInfoModel:
    def __init__(self):
        self.authors = []
        self.link = ''
        self.keyRaw = ''
        self.key = ''
        self.title = ''
        self.status = Constants.WRONG_LINK_CHECKING
        self.lastChapter = ''
        self.firstChapter = ''
        self.coverLink = ''
        self.lastRelease = ''
        self.allChapters = []

    @classmethod
    def fromHtmlContent(cls, link, htmlContent):
        obj = cls()

        obj.link = link
        obj.keyRaw = link[1:]
        obj.key = obj.keyRaw.replace('_', '-').lower()

        nextLineMangaCover = False
        nextLineMangaInfo = False
        mangaInfoLines = 0

        chaptersLink = []

        for line in htmlContent:
            if nextLineMangaCover:
                nextLineMangaCover = False
                try:
                    obj.coverLink = line.split('<img src="')[-1].split('"')[0]
                except:
                    pass
            elif '<div class="manga_series_image">' in line:
                nextLineMangaCover = True
            elif nextLineMangaInfo:
                if mangaInfoLines == 0:
                    obj.title = line.split('<h5>')[-1].split('</h5>')[0]
                elif mangaInfoLines == 2:
                    obj.status = line.split('<div>')[-1].split('</div>')[0]
                elif mangaInfoLines == 4:
                    obj.authors.append(line.split('<div>')[-1].split('</div>')[0])
                if mangaInfoLines > 4:
                    nextLineMangaInfo = False
                mangaInfoLines += 1
            elif '<div class="manga_series_data">' in line:
                nextLineMangaInfo = True
            elif '<td><a href="/' in line and obj.keyRaw in line:
                chapterLink = line.split('href="')[-1].split('"')[0]
                chaptersLink.append(chapterLink)

        obj.allChapters = chaptersLink
        obj.firstChapter = chaptersLink[0]
        obj.lastChapter = chaptersLink[-1]
        obj.lastRelease = chaptersLink[-1]

        return obj

    @classmethod
    def fromJson(cls, mangaKey):
        obj = cls()  # cls.__new__(cls) does not call __init__ (if needed)
        # super(MangaInfoModel, obj).__init__() # Call any polymorphic base class initializers

        filePath = '{}/{}/{}.json'.format(Constants.MANGA_DL_PATH, mangaKey, mangaKey)

        try:
            with open(filePath, "r") as fp:
                jsonObject = json.load(fp)
                obj.authors = jsonObject['authors']
                obj.link = jsonObject['link']
                obj.keyRaw = jsonObject['keyRaw']
                obj.key = jsonObject['key']
                obj.title = jsonObject['title']
                obj.coverLink = jsonObject['coverLink']
                obj.status = jsonObject['status']
                obj.lastChapter = jsonObject['lastChapter']
                obj.firstChapter = jsonObject['firstChapter']
                obj.lastRelease = jsonObject['lastRelease']
                obj.allChapters = jsonObject['allChapters']

        except:
            pass

        return obj

    def checking(self):
        return self.key != '' and self.status != Constants.WRONG_LINK_CHECKING

    def toString(self):
        return 'Title: {} ({})\nAuthors: {}\nStatus: {}\nCover: {}' \
               '\nFirst chapter : {}\nLast chapter: {}'.format(self.title, self.link,
                                                               ', '.join(self.authors),
                                                               self.status, self.coverLink,
                                                               self.firstChapter, self.lastRelease)

    def toDict(self):
        return {
            "title": self.title,
            "link": self.link,
            "coverLink": self.coverLink,
            "keyRaw": self.keyRaw,
            "key": self.key,
            "authors": self.authors,
            "status": self.status,
            "firstChapter": self.firstChapter,
            "lastChapter": self.lastChapter,
            "lastRelease": self.lastRelease,
            "allChapters": self.allChapters,
        }

    def toDictForFirebase(self, chapterKeys):
        return {
            Constants.MANGA_DOC_TITLE: self.title,
            Constants.MANGA_DOC_KEY: self.key,
            Constants.MANGA_DOC_AUTHORS: self.authors,
            Constants.MANGA_DOC_STATUS: self.status,
            Constants.MANGA_DOC_COVER: self.coverLink,
            Constants.MANGA_DOC_LAST_RELEASE: self.lastRelease,
            Constants.MANGA_DOC_CHAPTER_KEYS: chapterKeys,
        }

    # Function to build manga dl path
    def buildMangaPath(self):
        return '{}/{}/'.format(Constants.MANGA_DL_PATH, self.key)

    # Function to create manga dl directory
    def createMangaDirectory(self):
        if not os.path.exists(Constants.MANGA_DL_PATH):
            os.makedirs(Constants.MANGA_DL_PATH)
        mangaPath = self.buildMangaPath()
        if not os.path.exists(mangaPath):
            os.makedirs(mangaPath)
            # Save cover file
            fileNamePath = '{}{}'.format(
                self.buildMangaPath(), self.coverLink.split('/')[-1].replace('_', '-'))
            # Download img file
            subprocess.run(
                ['curl', '-o', fileNamePath, self.coverLink],
                capture_output=True,
                text=True,
            )
            # Rename file with real extension
            self.coverLink = FunctionHelper.renameFileExtension(fileNamePath) \
                .split(Constants.MANGA_DL_PATH + '/')[-1]
        else:
            oldMangaInfo = MangaInfoModel.fromJson(self.key)
            self.coverLink = oldMangaInfo.coverLink
            self.authors = oldMangaInfo.authors

    def saveMangaInfoToJson(self):
        with open('{}/{}.json'.format(self.buildMangaPath(), self.key), "w") as outfile:
            json.dump(self.toDict(), outfile, indent=4)

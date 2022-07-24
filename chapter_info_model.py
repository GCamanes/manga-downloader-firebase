import os
import subprocess
from constants import ConstantsHandler
from function_helper import FunctionHelper

Constants = ConstantsHandler()
FunctionHelper = FunctionHelper()


class ChapterInfoModel:
    def __init__(self, mangaInfo, link, htmlContent):
        self.link = link
        self.mangaInfo = mangaInfo
        self.number = FunctionHelper.getChapterNumber(link.split('_')[-1])
        self.pagesLink = []

        for line in htmlContent:
            if 'src="https://images.mangafreak.net/mangas/' in line:
                newPageLink = line.split('src="')[-1].split('"')[0]
                self.pagesLink.append(newPageLink)

    def toString(self):
        return 'Chapter n°: {}\nLink: {}\nPages: {}'.format(
            self.number,
            self.link,
            len(self.pagesLink),
        )

    # Function to build chapter dl path
    def buildChapterPath(self):
        return '{}/{}/{}_chap_{}'.format(Constants.MANGA_DL_PATH, self.mangaInfo.key,
                                         self.mangaInfo.key, self.number)

    # Function to create chapter dl directory
    def createChapterDirectory(self):
        chapterPath = self.buildChapterPath()
        if not os.path.exists(chapterPath):
            os.makedirs(chapterPath)
            return True
        return False

    # Function to download pages
    def downloadChapterPages(self):
        needToDownload = self.createChapterDirectory()
        if needToDownload:
            for (pageLink, index) in zip(self.pagesLink, range(1, len(self.pagesLink) + 1)):
                pageNumber = FunctionHelper.getPageName(str(index))
                extension = pageLink.split('.')[-1]
                pageFileName = '{}_chap_{}_page_{}.{}'.format(
                    self.mangaInfo.key,
                    self.number,
                    pageNumber,
                    extension
                )
                pageFilePath = '{}/{}'.format(self.buildChapterPath(), pageFileName)
                # Download img file
                subprocess.run(
                    ['curl', '-o', pageFilePath, pageLink],
                    capture_output=True,
                    text=True,
                )
                # Rename file with real extension
                FunctionHelper.renameFileExtension(pageFilePath) \
                    .split(Constants.MANGA_DL_PATH + '/')[-1]

        return needToDownload

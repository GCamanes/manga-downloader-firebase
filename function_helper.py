import os
import subprocess
import glob
import re

from constants import ConstantsHandler

Constants = ConstantsHandler()


class FunctionHelper:
    # Function to apply function on a list
    @staticmethod
    def mapEasy(listIn, fun):
        listOut = listIn.copy()
        for i in range(len(listIn)):
            listOut[i] = fun(listIn[i])
        return listOut

    # Function to compute percentage
    @staticmethod
    def computePercentage(value, divisor):
        return round(value * 1.0 / divisor * 100, 2)

    # Function to get key of a chapter
    @staticmethod
    def getChapterKey(key, number):
        return '{}_{}'.format(key, number)

    # Function to get the number of a chapter with 4 digits
    @staticmethod
    def getChapterNumber(chap):
        if len(chap.split(".")[0]) == 1:
            return "000" + chap
        elif len(chap.split(".")[0]) == 2:
            return "00" + chap
        elif len(chap.split(".")[0]) == 3:
            return "0" + chap
        else:
            return chap

    # Function to get the string page number (3 digits)
    @staticmethod
    def getPageName(page):
        strPage = str(page)
        if len(strPage) == 1:
            strPage = "00" + strPage
        elif len(strPage) == 2:
            strPage = "0" + strPage
        return strPage

    # Function to build manga info url
    @staticmethod
    def buildMangaInfoUrl(link):
        return "{}Manga{}".format(Constants.WEBSITE, link)

    # Function to build chapter info url
    @staticmethod
    def buildChapterInfoUrl(link):
        return "{}{}".format(Constants.WEBSITE[:-1], link)

    # Function to rename file with real extension
    @staticmethod
    def renameFileExtension(filePath):
        # Get real extension
        output = subprocess.check_output(['file', '--mime-type', filePath])
        realFileExtension = str(output).split('/')[-1].split("\\")[0]
        # Rename file
        fileNamePathWithoutExtension = os.path.splitext(filePath)[0]
        newFilePath = '{}.{}'.format(fileNamePathWithoutExtension, realFileExtension)
        renameCommandLine = 'mv {} {}'.format(filePath, newFilePath)
        os.system(renameCommandLine)
        return newFilePath

    # Function to fixe chapter page file names
    @staticmethod
    def fixeChapterPageNames(chapterPath):
        if os.path.isdir(chapterPath):
            baseFileName = chapterPath.split('/')[-1]
            filesInPath = glob.glob(chapterPath + '/*')
            for file in filesInPath:
                if os.path.isfile(file):
                    page = file.split('page_')[-1]
                    newFilePath = '{}/{}_page_{}'.format(chapterPath, baseFileName, page)
                    commandLine = 'mv "{}" "{}"'.format(file, newFilePath)
                    os.system(commandLine)

    @staticmethod
    def checkMissingChapter(mangaPath):
        print('Checking {}'.format(mangaPath))
        elementsInPath = glob.glob(mangaPath + '/*')
        previous = None
        for fileOrDir in sorted(elementsInPath):
            if os.path.isdir(fileOrDir):
                searchForNumber = re.findall(r"([\d.]*\d+)", fileOrDir)
                if len(searchForNumber) == 1:
                    number = float(searchForNumber[0])
                    if previous is not None:
                        previousInt = int(previous)
                        possiblePreviousChapters = [previousInt + round(x * 0.1, 1) for x in
                                                    range(1, 11)]
                        if number not in possiblePreviousChapters:
                            print('=> missing chapter(s) between {} to {}'.format(previous, number))

                    previous = number
                else:
                    print(fileOrDir)

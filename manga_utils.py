import os

from constants import ConstantsHandler
from function_helper import FunctionHelper

from manga_info_model import MangaInfoModel
from chapter_info_model import ChapterInfoModel

Constants = ConstantsHandler()
FunctionHelper = FunctionHelper()


class MangaManager:
    def __init__(self):
        self.website = Constants.WEBSITE

    # Function to get all info on a manga
    @staticmethod
    def getMangaInfo(link):
        # build search url
        url = FunctionHelper.buildMangaInfoUrl(link)
        # build command line
        # output = subprocess.check_output(
        #    "curl -s '{}'".format(url), shell=True, text=True)
        # content = output.split('\n')

        # Get html content
        filePath = '{}_{}.txt'.format(Constants.MANGA_INFO_PATH, link[1:])
        tmpFilePath = '{}_{}_tmp.txt'.format(Constants.MANGA_INFO_PATH, link[1:])
        os.system("curl -s '{}' > {}".format(url, filePath))
        # Remove non ascii characters
        os.system("bash ./remove_non_ascii.sh {} {}".format(filePath, tmpFilePath))
        # read the file
        f = open(filePath, 'r')
        content = f.readlines()
        f.close()
        # delete temporary file
        os.system('rm {}'.format(filePath))

        return MangaInfoModel.fromHtmlContent(link, content)

    # Function to get all info on a chapter
    @staticmethod
    def getChapterInfo(mangaInfo, link):
        # build search url
        url = FunctionHelper.buildChapterInfoUrl(link)

        # Get html content
        filePath = '{}_{}.txt'.format(Constants.CHAPTER_INFO_PATH, link[1:])
        tmpFilePath = '{}_{}_tmp.txt'.format(Constants.CHAPTER_INFO_PATH, link[1:])
        os.system("curl -s '{}' > {}".format(url, filePath))
        # Remove non ascii characters
        os.system("bash ./remove_non_ascii.sh {} {}".format(filePath, tmpFilePath))
        # read the file
        f = open(filePath, 'r')
        content = f.readlines()
        f.close()
        # delete temporary file
        os.system('rm {}'.format(filePath))

        return ChapterInfoModel(mangaInfo, link, content)

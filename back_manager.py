# -----------------------------------------------------------------------------------
# SETUP
# -----------------------------------------------------------------------------------
# python3 -m pip install firebase-admin
# python3 -m pip install google-cloud-firestore
# python3 -m pip install google-cloud-storage

# download private key from firebase project
# then name it ServiceAccountKey.json
# then place it in project root path

# IMPORT
import os
import json
import sys
import glob
import argparse
import firebase_admin
from firebase_admin import credentials, firestore, storage
from uuid import uuid4

from manga_utils import MangaManager
from manga_info_model import MangaInfoModel
from manga_firebase_model import MangaFirebaseModel
from chapter_firebase_model import ChapterFirebaseModel

from constants import ConstantsHandler
from function_helper import FunctionHelper

Constants = ConstantsHandler()
FunctionHelper = FunctionHelper()


# -----------------------------------------------------------------------------------
# DATA MANAGER
# -----------------------------------------------------------------------------------

class DataManager:
    def __init__(self):
        self.mangaManager = MangaManager()
        # Cloud Firestore certificate
        self.cred = credentials.Certificate(Constants.SERVICE_ACCOUNT_KEY_PATH)
        self.app = firebase_admin.initialize_app(
            self.cred,
            {'storageBucket': self.getStorageUrl()},
        )
        # Get firestore client to interact with distant database
        self.store = firestore.client()

    # Function to get storage URL
    @staticmethod
    def getStorageUrl():
        storageUrl = None
        try:
            with open(Constants.SERVICE_ACCOUNT_KEY_PATH, "r") as fp:
                jsonObject = json.load(fp)
                storageUrl = '{}.appspot.com'.format(jsonObject['project_id'])
        except:
            pass
        return storageUrl

    # Function to download a manga
    def downloadManga(self, link):
        print("\nDOWNLOADING {}...".format(link))

        mangaInfo = self.mangaManager.getMangaInfo(link)

        if mangaInfo.checking():
            # Create directory if needed
            mangaInfo.createMangaDirectory()
            # Save info to json
            mangaInfo.saveMangaInfoToJson()
            # Download chapters
            self.downloadMangaChapters(mangaInfo)
        else:
            print('\n/!\\ No result on link {}'.format(link))

    # Function to update downloaded manga
    def updateDownloadManga(self, link):
        print("\nUPDATING DOWNLOAD {}...".format(link))

        mangaInfo = self.mangaManager.getMangaInfo(link)

        if mangaInfo.checking():
            # Create directory if needed
            mangaInfo.createMangaDirectory()
            # Save info to json
            mangaInfo.saveMangaInfoToJson()
            # Download chapters
            self.updateDownloadMangaChapters(mangaInfo)

        else:
            print('\n/!\\ No result on link {}'.format(link))

    # Function to download chapters
    def downloadMangaChapters(self, mangaInfo):
        for chapterLink in mangaInfo.allChapters:
            try:
                chapterInfo = self.mangaManager.getChapterInfo(mangaInfo, chapterLink)
                downloaded = chapterInfo.downloadChapterPages()
                if downloaded:
                    print('CHAPTER {} downloaded !'.format(chapterInfo.link))
                else:
                    break
            except:
                print('ERROR while downloading {}'.format(chapterLink))

    # Function to update downloaded chapters
    def updateDownloadMangaChapters(self, mangaInfo):
        for chapterLink in mangaInfo.allChapters.__reversed__():
            try:
                chapterInfo = self.mangaManager.getChapterInfo(mangaInfo, chapterLink)
                downloaded = chapterInfo.downloadChapterPages()
                if downloaded:
                    print('CHAPTER {} downloaded !'.format(chapterInfo.link))
                else:
                    break
            except:
                print('ERROR while downloading {}'.format(chapterLink))

    # Function to update downloaded chapters of all manga
    def updateDownloadAllManga(self):
        print("UPDATING DOWNLOAD ALL MANGA...")
        elementsInPath = glob.glob(Constants.MANGA_DL_PATH + '/*')
        for fileOrDir in sorted(elementsInPath):
            if os.path.isdir(fileOrDir):
                mangaKey = fileOrDir.split('/')[-1]
                mangaInfo = MangaInfoModel.fromJson(mangaKey)
                if mangaInfo.checking():
                    self.updateDownloadManga(mangaInfo.link)

    def updateMangaOnFirebase(self, mangaKey, chapterKeys):
        mangaInfo = MangaInfoModel.fromJson(mangaKey)
        self.store.collection(Constants.MANGAS_COLLECTION).document(mangaInfo.key).set(
            mangaInfo.toDictForFirebase(chapterKeys))

    def updateChapterOnFirebase(self, mangaKey, chapterToUpload):
        self.store.collection(Constants.MANGAS_COLLECTION).document(mangaKey) \
            .collection(Constants.CHAPTERS_COLLECTION).document(chapterToUpload.key) \
            .set(chapterToUpload.toDict())

    def getMangaInfoOnFirebase(self, mangaKey):
        mangaFound = None
        mangasOnFirebase = self.store.collection(Constants.MANGAS_COLLECTION).get()
        for manga in mangasOnFirebase:
            mangaFirebase = MangaFirebaseModel.fromDict(
                self.store.collection(Constants.MANGAS_COLLECTION).document(
                    manga.id).get().to_dict()
            )
            if mangaFirebase.key == mangaKey:
                mangaFound = mangaFirebase
        return mangaFound

    def getLastChapterOnFirebase(self, mangaKey):
        lastChapter = None
        mangasOnFirebase = self.store.collection(Constants.MANGAS_COLLECTION).document(
            mangaKey).collection(Constants.CHAPTERS_COLLECTION).get()
        if len(mangasOnFirebase) > 0:
            lastChapter = ChapterFirebaseModel.fromDict(
                self.store.collection(Constants.MANGAS_COLLECTION).document(mangaKey)
                    .collection(Constants.CHAPTERS_COLLECTION).document(mangasOnFirebase[-1].id)
                    .get().to_dict()
            )

        return lastChapter

    @staticmethod
    def uploadFileToStorage(myBucket, filePath):
        # Create blob
        blob = myBucket.blob(filePath)
        # Create new token
        new_token = uuid4()
        # Create new dictionary with the metadata
        metadata = {"firebaseStorageDownloadTokens": new_token}
        # Set metadata to blob
        blob.metadata = metadata
        # Upload
        blob.upload_from_filename('{}/{}'.format(Constants.MANGA_DL_PATH, filePath))

    def uploadMangaToFirebase(self, mangaKey):
        print('UPLOADING : {} ...'.format(mangaKey))
        pathToUpload = '{}/{}'.format(Constants.MANGA_DL_PATH, mangaKey)
        # Create bucket
        bucket = firebase_admin.storage.bucket()

        if os.path.isdir(pathToUpload):
            mangaFoundOnFirebase = self.getMangaInfoOnFirebase(mangaKey)
            if mangaFoundOnFirebase is None:
                coverPath = MangaInfoModel.fromJson(mangaKey).coverLink
                # Upload
                self.uploadFileToStorage(bucket, coverPath)
            self.updateMangaOnFirebase(
                mangaKey,
                [path.split('/')[-1] for path in sorted(glob.glob(pathToUpload + '/*')) if
                 os.path.isdir(path)],
            )

            lastChapter = self.getLastChapterOnFirebase(mangaKey)

            elementsInPath = glob.glob(pathToUpload + '/*')
            for fileOrDir in sorted(elementsInPath):
                if os.path.isdir(fileOrDir):
                    chapterToUpload = ChapterFirebaseModel.fromPath(fileOrDir)
                    if lastChapter is None or lastChapter.key < chapterToUpload.key:
                        print('UPLOADING {} to firebase'.format(chapterToUpload.key))
                        self.updateChapterOnFirebase(mangaKey, chapterToUpload)
                        for (page, index) in zip(chapterToUpload.pages,
                                                 range(1, len(chapterToUpload.pages) + 1)):
                            self.uploadFileToStorage(bucket, page)
                            print('=> {} : {} %'.format(
                                chapterToUpload.key,
                                FunctionHelper.computePercentage(index,
                                                                 len(chapterToUpload.pages)),
                            ))

        else:
            print('/!\\ ERROR : path {} not fount'.format(pathToUpload))

    def uploadAllMangaToFirebase(self):
        try:
            mangasCollection = self.store.collection(Constants.MANGAS_COLLECTION).get()
            for manga in mangasCollection:
                mangaFirebase = MangaFirebaseModel.fromDict(
                    self.store.collection(Constants.MANGAS_COLLECTION).document(manga.id)
                        .get().to_dict())
                self.uploadMangaToFirebase(mangaFirebase.key)
        except Exception as error:
            print('\n/!\\ ERROR in uploading manga :', str(error))
            sys.exit()

    def showMangasOnFirestore(self):
        try:
            mangasCollection = self.store.collection(Constants.MANGAS_COLLECTION).get()
            for (manga, index) in zip(mangasCollection, range(1, len(mangasCollection) + 1)):
                mangaFirebase = MangaFirebaseModel.fromDict(
                    self.store.collection(Constants.MANGAS_COLLECTION).document(manga.id)
                        .get().to_dict())
                print('{} : {}'.format(index, mangaFirebase.title))
        except Exception as error:
            print('\n/!\\ ERROR in show manga list :', str(error))
            sys.exit()

    def deleteManga(self, mangaKey):
        try:
            mangaFoundOnFirebase = self.getMangaInfoOnFirebase(mangaKey)
            if mangaFoundOnFirebase is not None:
                chaptersCollection = self.store.collection(Constants.MANGAS_COLLECTION) \
                    .document(mangaKey) \
                    .collection(Constants.CHAPTERS_COLLECTION).get()

                for chapDoc in chaptersCollection:
                    self.store.collection(Constants.MANGAS_COLLECTION).document(mangaKey) \
                        .collection(Constants.CHAPTERS_COLLECTION).document(chapDoc.id).delete()
                self.store.collection(Constants.MANGAS_COLLECTION).document(mangaKey).delete()
                print('SUCCESS {} deleted from firestore'.format(mangaKey))
            else:
                print('/!\\ ERROR DELETING MANGA {} not in manga list'.format(mangaKey))
        except Exception as error:
            print('/!\\ ERROR DELETING MANGA {} : {}'.format(mangaKey, str(error)))
            sys.exit()


# -----------------------------------------------------------------------------------
# MAIN FUNCTION
# -----------------------------------------------------------------------------------

def main():
    # Init DataManager
    dataManager = DataManager()

    # Definition of argument option
    parser = argparse.ArgumentParser(prog="mangaReaderFirebase.py")
    parser.add_argument('-l', '--list',
                        help='show list of mangas in firestore',
                        action="store_true")
    parser.add_argument('-d', '--delete', nargs=1,
                        help='delete a manga from firestore (use "mangaKey")',
                        action='store', type=str)
    parser.add_argument('--dlmanga', nargs=1,
                        help='download manga (use "/mangaLink")',
                        action='store', type=str)
    parser.add_argument('--udlmanga', nargs=1,
                        help='update downloaded manga (use "/mangaLink")',
                        action='store', type=str)
    parser.add_argument('--udlall',
                        help='update downloaded all manga in manga path',
                        action="store_true")
    parser.add_argument('--upload', nargs=1,
                        help='upload downloaded manga to firebase storage (use "mangaKey")',
                        action='store', type=str)
    parser.add_argument('--uploadall',
                        help='upload all downloaded manga to firebase storage',
                        action='store_true')
    parser.add_argument('-f', '--fixe', nargs=1,
                        help='fixe file page names in path',
                        action='store', type=str)
    parser.add_argument('-c', '--check', nargs=1,
                        help='check missing chapter',
                        action='store', type=str)

    # Parsing of command line argument
    args = parser.parse_args(sys.argv[1:])

    if args.list:
        dataManager.showMangasOnFirestore()
        sys.exit()

    elif args.dlmanga is not None:
        dataManager.downloadManga(args.dlmanga[0])
        sys.exit()

    elif args.udlmanga is not None:
        dataManager.updateDownloadManga(args.udlmanga[0])
        sys.exit()

    elif args.udlall:
        dataManager.updateDownloadAllManga()
        sys.exit()

    elif args.upload is not None:
        dataManager.uploadMangaToFirebase(args.upload[0])
        sys.exit()

    elif args.uploadall:
        dataManager.uploadAllMangaToFirebase()
        sys.exit()

    elif args.fixe is not None:
        FunctionHelper.fixeChapterPageNames(args.fixe[0])
        sys.exit()

    elif args.delete is not None:
        dataManager.deleteManga(args.delete[0])
        sys.exit()

    elif args.check is not None:
        FunctionHelper.checkMissingChapter(args.check[0])
        sys.exit()


if __name__ == "__main__":
    main()

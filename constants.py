# -----------------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------------

def constant(f):
    def fset(self, value):
        raise TypeError

    def fget(self):
        return f(self)

    return property(fget, fset)


class ConstantsHandler(object):
    # FILES
    @constant
    def PATH(self):
        return '.'

    # DOWNLOAD
    @constant
    def MANGA_DL_PATH(self):
        return './manga-dl'

    @constant
    def MANGA_SEARCH_PATH(self):
        return '{}/search.txt'.format(self.PATH)

    @constant
    def MANGA_INFO_PATH(self):
        return '{}/mangaInfo'.format(self.PATH)

    @constant
    def MANGA_CHAPTERS_PATH(self):
        return '{}/mangaChapterslist.txt'.format(self.PATH)

    @constant
    def CHAPTER_INFO_PATH(self):
        return '{}/chapterInfo'.format(self.PATH)

    @constant
    def MANGA_CHAPTER_PAGE_PATH(self):
        return '{}/mangaChapterPage.txt'.format(self.PATH)

    # FIREBASE
    @constant
    def SERVICE_ACCOUNT_KEY_PATH(self):
        return '{}/ServiceAccountKey.json'.format(self.PATH)

    # MANGA WEBSITE
    @constant
    def HTTPS(self):
        return 'https:'

    @constant
    def WEBSITE(self):
        return 'https://w12.mangafreak.net/'

    @constant
    def WRONG_LINK_CHECKING(self):
        return 'WRONG_LINK'

    @constant
    def DISABLED(self):
        return 'disabled'

    # COLLECTION NAMES (CLOUD FIRESTORE)
    @constant
    def MANGAS_COLLECTION(self):
        return u'mangas'

    @constant
    def CHAPTERS_COLLECTION(self):
        return u'chapters'

    @constant
    def MANGA_DOC_TITLE(self):
        return u'title'

    @constant
    def MANGA_DOC_AUTHORS(self):
        return u'authors'

    @constant
    def MANGA_DOC_KEY(self):
        return u'key'

    @constant
    def MANGA_DOC_STATUS(self):
        return u'status'

    @constant
    def MANGA_DOC_COVER(self):
        return u'coverLink'

    @constant
    def MANGA_DOC_LAST_RELEASE(self):
        return u'lastRelease'

    @constant
    def MANGA_DOC_CHAPTER_KEYS(self):
        return u'chapterKeys'

    @constant
    def CHAPTER_DOC_NUMBER(self):
        return u'number'

    @constant
    def CHAPTER_DOC_PAGES(self):
        return u'pages'

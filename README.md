# Manga-downloader-firebase
Python script to download manga and upload them to firebase

## Some terminal commands

All action are listed in ```back_manager.py```.
You can:
- list manga uploaded to firebase
- remove a manga from firebase
- download one manga from the source website (starting from the first chapter)
- download one manga starting from the last released chapter
- download all missing chapters from previously downloaded manga
- upload one manga to firebase
- upload all manga previously upload to firebase
- fix file names from a chapter folder
- check for missing chapter

## Syncing download with an external drive

```rsync -aEv --delete "Desktop/fangapp/manga-downloader-firebase/manga-dl" "/Volumes/DD-MyPassport"```
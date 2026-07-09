from peewee import *
import os
db=SqliteDatabase('downloaded.db')
class DM(Model):
    id=CharField()
    path=CharField()
    manga_name=CharField()
    image=BlobField()
    lang_list=JSONField()
    translated_path=CharField()
    translated=BooleanField()
    class Meta:
        database=db
db.connect()
db.create_tables([DM])

def scan():
    mangas=DM.select()
    for manga in mangas:
        print(manga.id, manga.path, manga.manga_name, manga.lang_list)
        if not os.path.exists(manga.path):
            manga.delete_instance()


def add_downloaded(id, path, manga_name, image, lang_l):
    DM.create(id=id, path=path, manga_name=manga_name, image=image, lang_list=lang_l, translated_path="", translated=False)

def change_translated_status(id, translated_path, translated):
    manga=DM.get(id=id)
    if translated:
        manga.translated=True
        manga.translated_path=translated_path
        manga.save()
    else:
        manga.translated=False
        manga.translated_path=""
        manga.save()

def delete_downloaded(manga_name):
    manga=DM.get(manga_name=manga_name)
    manga.delete_instance()

def get_by_id(id):
    try:
        manga=DM.get(id=id)
        return True
    except:
        return False
def get_manga_downloaded():
    mangas=DM.select()
    manga_list=[]
    for manga in mangas:
        manga_list.append((manga.id, manga.path, manga.manga_name, manga.image, manga.lang_list, manga.translated_path, manga.translated))
    return manga_list
    
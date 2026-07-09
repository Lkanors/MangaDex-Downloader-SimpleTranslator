import requests
from PIL import Image
import io
import arcade
import os
import pathlib
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import pathvalidate
import db_manager as db
import time
base_url_mangadex = "https://api.mangadex.org"
name=-1
def mangadex(title):
    r = requests.get(
    f"{base_url_mangadex}/manga",
    params={"title": title,
            "limit": 50},
    )
    return r.json()["data"]

def get_titles(title):
    data=mangadex(title)
    # print(data)
    mangas=[list(manga["attributes"]["title"].values())[0] for i, manga in enumerate(data)]
    ids=[i["id"] for i in data]
    print(f"Cписок названий: ", mangas)
    return [ids, mangas]

def get_images(manga_id):
    global name
    name+=1
    url = f"https://api.mangadex.org/manga/{manga_id}?includes[]=cover_art"

    data = requests.get(url).json()
    cover = next(
        rel for rel in data["data"]["relationships"]
        if rel["type"] == "cover_art"
    )
    filename = cover["attributes"]["fileName"]
    cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{filename}"

    img = requests.get(cover_url)
    img=img.content
    return img

def pil_convert(img, w, h):
    bs=io.BytesIO(img)
    p_image=Image.open(bs)
    p_image.thumbnail((w,h), Image.Resampling.LANCZOS)
    p_image=p_image.convert('RGBA')
    texture=arcade.Texture(p_image, name=f"tex_{name}")
    sprite=arcade.Sprite()
    sprite.texture=texture
    return sprite

def get_manga_full(title):
    data=get_titles(title)
    # images=[get_images(i) for i in data[0]]
    return (data[1], data[0])

def get_all_chapters(manga_id):
    chapters = []
    offset = 0

    while True:
        r = requests.get(
            f"{base_url_mangadex}/manga/{manga_id}/feed",
            params={
                "limit": 500,
                "offset": offset,
                "order[chapter]": "asc"
            },
            timeout=30
        )

        r.raise_for_status()
        data = r.json()

        chapters.extend(data["data"])

        offset += data["limit"]
        if offset >= data["total"]:
            break

    return chapters


def show_languages(manga_id):
    chapters=get_all_chapters(manga_id)
    counter = Counter()

    for ch in chapters:
        lang = ch["attributes"]["translatedLanguage"]
        counter[lang] += 1

    # print("\nДоступные языки:\n")
    lang_sorted=[]
    exist_chapters=[]
    for chapter in chapters:
        if chapter["attributes"]["translatedLanguage"]=='en' and\
        chapter["attributes"].get("chapter") not in exist_chapters:
            exist_chapters.append(chapter["attributes"].get("chapter"))
            lang_sorted.append((lang, chapter))
    for lang, count in sorted(counter.items())[::-1]:
        print(lang)
        if lang!="ar":
            for chapter in chapters:
                if chapter["attributes"]["translatedLanguage"]==lang and\
                chapter["attributes"].get("chapter") not in exist_chapters:
                    exist_chapters.append(chapter["attributes"].get("chapter"))
                    lang_sorted.append((lang, chapter))
    return lang_sorted
    #     if size==0: return (len(counter), lang, chapters)
    #     size-=1


def get_page_urls(chapter_id):
    r = requests.get(f"{base_url_mangadex}/at-home/server/{chapter_id}", timeout=30)
    r.raise_for_status()

    data = r.json()

    base = data["baseUrl"]
    chapter = data["chapter"]
    print(chapter["data"])
    return [
        f"{base}/data/{chapter['hash']}/{page}"
        for page in chapter["data"]
    ]


def download_image(url, path):
    r = requests.get(url, timeout=60)
    r.raise_for_status()

    with open(path, "wb") as f:
        f.write(r.content)

def get_path(manga_name):
    return os.path.join(pathlib.Path.cwd(), manga_name)

def download_chapter(manga_id, manga_name, data):
    list_languages=[]
    chapters=show_languages(manga_id)
    count_ch=0
    os.makedirs(manga_name, exist_ok=True)
    for root, folders, files in os.walk(manga_name):
        folders_e=folders
        break
    n_max=0
    for i in folders:
        n_max+=1
    # for folder in folders:
    #     n_max=max(float(folder.split(' - ')[-1]), int(float(n_max)//1))
    #     print(f'-------------\n{n_max}\n-------------')
    # print(f'n_max {n_max}')
    # n_max=int(float(n_max)//1)
    if n_max>=2:
        chapters=chapters[n_max-2:]
    for lang, chapter in chapters:
        count_ch+=1
        attrs = chapter["attributes"]
        number = attrs.get("chapter") or "unknown"
        folder=f"{manga_name} - {number}"
        # folder = f"Chapter {number}"
        # if title:
        #     folder += f" - {title}"
        folder=pathvalidate.sanitize_filepath(folder)
        chapter_folder=os.path.join(manga_name, folder)
        os.makedirs(pathvalidate.sanitize_filepath(chapter_folder), exist_ok=True)
        list_languages.append((lang, pathvalidate.sanitize_filepath(os.path.join(os.getcwd(),chapter_folder))))
        urls = get_page_urls(chapter["id"])
        print(f"Скачивается {folder}")

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = []
            for i, url in enumerate(urls, 1):
                ext = os.path.splitext(url)[1]
                # path=os.path.join(manga_name, folder)
                path = os.path.join(chapter_folder, f"Ch. {number} - {i:03}{ext}")
                data[0]=f"Ch {number} - {i} image - {count_ch}/{len(chapter)}"
                path=pathvalidate.sanitize_filepath(path)
                if os.path.isfile(path):
                    print(f"{path} - exists. Skipping...")
                    continue
                futures.append(pool.submit(download_image, url, path))
    try:
        db.add_downloaded(manga_id,pathvalidate.sanitize_filepath(os.path.join(os.getcwd(),manga_name)),manga_name, get_images(manga_id),list_languages)
    except Exception as e:
        print(e)
        with open('images/no_img.png', 'rb') as file:
            db.add_downloaded(manga_id,pathvalidate.sanitize_filepath(os.path.join(os.getcwd(),manga_name)),manga_name, file.read(),list_languages)
    print('full_downloaded')

import arcade
import time
import pyglet
import md_downloader as md
from pyglet.shapes import RoundedRectangle
from arcade_add import InputText, ButtonMenu, Button, SelectList, buttons_state
from unification import Unify
import db_manager as db
import threading
WIDTH=1280
HEIGHT=720

RATE=pyglet.display.get_display().get_default_screen().get_mode().rate
print(RATE)
class TranslatePage:
    def __init__(self,space,color):
        self.space=space
        self.color=color
        self.manga_list=SelectList()
        self.spritel=arcade.SpriteList()
        self.update_image=False
        self.model_list=("translategemma:latest",)
        self.translation_status_bool=False
        self.target_lang_input=InputText()
        self.target_lang_input.input=""
        self.target_lang_input.shorted=""

    def create_downloaded_list(self,x,y,wd,hg):
        self.x=x
        self.y=y
        self.wd=wd
        self.hg=hg
        self.manga_ids=[]
        self.m_l=[]
        self.lang_ch_list=[]
        self.images=[]
        self.manga_path=[]
        self.translated=[]
        self.downloaded=db.get_manga_downloaded()
        for i in self.downloaded:
            self.manga_ids.append(i[0])
            self.translated.append(i[6])
            self.manga_path.append(i[1])
            self.m_l.append(i[2])
            self.lang_ch_list.append(i[4])
            self.images.append(i[3])
        print(self.lang_ch_list)
        self.manga_list.set_items(self.m_l)
        self.manga_list.pre_draw(self.x+self.space//2,40,self.wd,self.hg)
        self.translate_button=Button(150,50, 'Translate manga')
    def create_translator(self, source_lang, chapter_path, target_lang, context):
        # self.target_lang=target_lang
        self.translator=Unify(source_lang, target_lang, context,
                            self.model_list[0], self.manga_path[self.manga_list.selected],
                            chapter_path, self.manga_ids[self.manga_list.selected])

    def draw(self, x,y,wd,hg):
        
        self.x=x
        self.y=y
        self.wd=wd
        self.hg=hg
        # print(self.space)
        self.manga_list.draw(self.x+self.space//2,self.y,self.wd,self.hg)
        
        if len(self.m_l)>0 and not self.translated[self.manga_list.selected] and not self.translation_status_bool:
            arcade.draw_text("Target language", self.x-350, 30, font_size=16)
            self.target_lang_input.draw(self.x, 40, 400, 40)
            self.translate_button.draw(self.x+self.space//2,40)
        if self.update_image:
            self.spritel.clear()
            self.spritel.append(self.image_draw)
            self.image_draw.center_x=self.x-self.space//2
            self.image_draw.center_y=y
            self.update_image=False
        self.spritel.draw()
        
    def update(self):
        try:
            self.translate_button.reset_visible()
            if not self.translation_status.is_alive():
                self.translation_status_bool=False
                self.translated[self.manga_list.selected]=True
        except:
            pass

    def check_all_buttons(self,x,y):
        try:
            translate_b_status=self.translate_button.check_click(x,y)
            if translate_b_status:
                self.translation_status_bool=True
                self.translation_status=threading.Thread(target=self.translation, daemon=True)
                self.translation_status.start()
        except AttributeError:
            pass
    def translation(self):
        target_lang = self.target_lang_input.input.strip() or "ru"
        for i in self.lang_ch_list[self.manga_list.selected]:
            lang=i[0]
            path=i[1]
            self.create_translator(lang, path, target_lang, 'context')
            self.translator.start_translation()
    def hover(self,x,y):
        try:
            self.translate_button.hover(x,y)
        except AttributeError:
            pass
    def check(self,x,y):
        self.status_check=self.manga_list.check_click(x,y)
        if self.status_check is not None:
            def get_image():
                try:
                    self.image_draw=md.pil_convert(self.images[self.manga_list.selected], self.wd,self.hg)
                    self.update_image=True
                except Exception as e:
                    print(e)
            get_image()
    

        

class MangaList:
    def __init__(self, space, color):
        self.space=space
        self.color=color
        self.downloading_status=False
        self.draw_texts=[]
        self.list=SelectList()
        self.manga=[]
        self.status_check=None
        self.spritel=arcade.SpriteList()
        self.image_draw=None
        self.image_state=False
        self.update_image=False
        self.data=[""]
        self.language_chapters_list=[]
    def mangadex(self, title):
        self.download_button=Button(150, 50,"Download chapters")
        self.manga=md.get_manga_full(title)
        print(self.manga[1])
        self.list.set_items(self.manga[0])
        self.list.pre_draw(self.x+self.space//2,self.y,self.wd,self.hg)
        

    def draw(self, x,y, wd, hg):
        self.x=x
        self.y=y
        self.wd=wd
        self.hg=hg
        if len(self.manga)>0 and not self.downloading_status and not db.get_by_id(self.manga[1][self.list.selected]):
            self.download_button.draw(self.x+300, 40)
        self.spritel.draw()
        try:
            if self.downloading_status:
                arcade.draw_text(f"Manga downloading... ({self.data[0]})",self.x-self.space//2-self.wd//2,60, font_size=16)
        except AttributeError:
            pass
        try:
            if self.image_state.is_alive():
                arcade.draw_text("Image loading...",self.x-self.space//2-self.wd//2,30, font_size=16)
        except AttributeError:
            pass
        if self.update_image==True:
            self.spritel.clear()
            self.spritel.append(self.image_draw)
            self.image_draw.center_x=self.x-self.space//2
            self.image_draw.center_y=y
            self.update_image=False
        self.list.draw(self.x+self.space//2,self.y,self.wd,self.hg)
    def hover(self,x,y):
        try:
            self.download_button.hover(x,y)
        except AttributeError:
            pass
    def get_manga_downloaded(self, id):
        return db.get_by_id(id)
    def update(self):
        try:
            if self.downloading_process.is_alive():
                self.downloading_status=True
            else:
                self.downloading_status=False
        except:
            pass
        self.download_button.reset_visible()
    def check_download_button(self,x,y):
        try:
            if self.download_button.check_click(x,y) and not self.get_manga_downloaded(self.manga[1][self.list.selected]):
                print(f'Downloading {self.manga[0][self.list.selected]}')
                self.downloading_process=threading.Thread(target=md.download_chapter, args=(self.manga[1][self.list.selected], self.manga[0][self.list.selected][:50], self.data))
                self.downloading_process.start()
        except Exception as e:
            print(e)
            return False
    def check(self,x,y):
        self.status_check=self.list.check_click(x,y)
        if self.status_check is not None:
            def get_image():
                try:
                    self.image_draw=md.pil_convert(md.get_images(self.manga[1][self.status_check]), self.wd,self.hg)
                    self.update_image=True
                except Exception as e:
                    with open('images/no_img.jpg', 'rb') as file:
                        self.image_draw=md.pil_convert(file.read(), self.wd,self.hg)
                    print(e)
            print(1)
            # if not self.image_state:
            #     print(1)
            self.image_state=threading.Thread(target=get_image, daemon=True)
            self.image_state.start()

        return self.status_check

    def scroll(self, wheel_delta):
        return self.list.scroll(wheel_delta)

    def start_scrollbar_drag(self, x, y):
        return self.list.start_scrollbar_drag(x, y)

    def drag_scrollbar(self, y):
        return self.list.drag_scrollbar(y)

    def stop_scrollbar_drag(self):
        self.list.stop_scrollbar_drag()


        
class Interface(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, "Manga translator", False, True, draw_rate=1/RATE, update_rate=1/RATE,)
        self.current_state=None
        self.background_color=(18,19,20)
        self.mangadex=ButtonMenu(text='MangaDex')
        self.translate_menu=ButtonMenu(text='Translate')
        self.manga_list=MangaList(600, (25,26,27))
        self.translate=TranslatePage(600, (25,26,27))
        self.input_text=InputText()
        db.scan()
    
    def draw_md(self):
        self.manga_list.draw(self.wd//2+60, self.hg//2+25, self.wd//2.5, self.hg-150)
        self.manga_list.space=100+self.wd//2.5
        self.input_text.draw(self.wd//2+60, 40, 400, 40)
        self.draw_texts()
    
    def draw_translate(self):
        self.translate.space=100+self.wd//2.5
        self.translate.draw(self.wd//2+60, self.hg//2+25, self.wd//2.5, self.hg-150)

    def draw_blocks(self):
        self.wd, self.hg = self.get_size()
        arcade.draw_rect_filled(arcade.XYWH(60, self.hg//2, 120, self.hg), (25,26,27))
        self.mangadex.draw(60, self.hg-30)
        self.translate_menu.draw(60, self.hg-90)
        if self.current_state=="md":
            self.draw_md()
        if self.current_state=="translate":
            self.draw_translate()


    def draw_texts(self):
        arcade.draw_text("Enter title",self.wd//2+60-300, 30, font_size=16)

    def on_draw(self):
        self.clear()
        self.draw_blocks()

    def on_close(self):
        arcade.exit()
        super().on_close()
    def on_update(self, delta_time):
        try:
            if self.current_state=="translate":
                self.translate.update()
            if self.current_state=="md":
                self.manga_list.update()
        except AttributeError:
            pass
    
    def on_resize(self, width, height):
        self.on_draw()
        self.mangadex.resize()
        self.translate_menu.resize()
        try:
            self.manga_list.download_button.resize()
        except:
            pass
        try:
            self.translate.translate_button.resize()
        except:
            pass
        if self.current_state=="md":
            if len(self.manga_list.spritel)>0:
                self.manga_list.image_draw.center_x=self.manga_list.x-self.manga_list.space//2
                self.manga_list.image_draw.center_y=self.manga_list.y
        if self.current_state=="translate":
            if len(self.translate.spritel)>0:
                self.translate.image_draw.center_x=self.translate.x-self.translate.space//2
                self.translate.image_draw.center_y=self.translate.y

    def on_mouse_motion(self, x, y, buttonMenu, modifiers):
        self.mouse_x=x
        self.mouse_y=y
        if self.current_state=="md":
            self.manga_list.hover(x,y)
        self.mangadex.hover(x,y)
        self.translate_menu.hover(x,y)
        try:
            self.translate.hover(x,y)
        except AttributeError:
            pass
    
    def on_mouse_release(self, x, y, buttonMenu, modifiers):
        if self.current_state=="md":
            was_dragging = self.manga_list.list.scrollbar_dragging
            self.manga_list.stop_scrollbar_drag()
            if was_dragging:
                return
            self.manga_list.check(x,y)
            self.manga_list.check_download_button(x,y)
        if self.mangadex.check_click(x,y): self.current_state="md"
        if self.translate_menu.check_click(x,y): 

            self.current_state="translate"
            self.translate.create_downloaded_list(self.wd//2+60, self.hg//2+25, self.wd//2.5, self.hg-150)
            db.scan()
        if self.current_state=="translate":
            self.translate.check(x,y)
            self.translate.check_all_buttons(x,y)

        

    def on_mouse_press(self, x, y, buttonMenu, modifiers):
        if self.current_state=="md":
            self.manga_list.start_scrollbar_drag(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttonMenus, modifiers):
        if self.current_state=="md":
            self.manga_list.drag_scrollbar(y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.current_state=="md":
            self.manga_list.scroll(scroll_y)
    def on_text(self, text):
        if self.current_state=="md":
            self.input_text.add_symb(text)
        if self.current_state=="translate":
            self.translate.target_lang_input.add_symb(text)

    def on_key_press(self, key, modifiers):
        if self.current_state=="md":
            if key==arcade.key.BACKSPACE:
                self.input_text.remove_symb()
            if key==arcade.key.ENTER:
                if buttons_state[self.mangadex.number]:
                    if self.input_text.input!='': self.manga_list.mangadex(self.input_text.input)
        if self.current_state=="translate":
            if key==arcade.key.BACKSPACE:
                self.translate.target_lang_input.remove_symb()

window = Interface()
arcade.run()
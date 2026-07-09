import arcade
from pyglet.shapes import RoundedRectangle
buttons_state=[]


class ButtonMenu:
    def __init__(self, x=60, y=720-30, w=100, h=40, text="Кнопка", font="Arial"):
        buttons_state.append(False)
        self.number=len(buttons_state)-1
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.color = (246,108,0)
        self.hover_color = tuple(i-40 if i-40>0 else i for i in self.color)
        self.pressed = False
        self.font=font
        self.clicked=False
        self.temp=-1
        self.visible=False
        
    def center_coords_translator(self, x,y,w,h):
        nx=x-w//2
        ny=y-h//2
        return (nx,ny,w,h)
    def color_clicked(self):
        if self.temp!=buttons_state[self.number] or self.temp==-1:
            if buttons_state[self.number]:
                self.temp=buttons_state[self.number]
                self.rect.x=self.x
                self.rect.y=self.y
                self.rect.width=self.w
                self.rect.h=self.h
                self.rect.color=self.hover_color
                self.rect=RoundedRectangle(
                *self.center_coords_translator(self.x, self.y, self.w, self.h),
                color=self.hover_color,
                radius=10)
            else:
                self.temp=buttons_state[self.number]
                self.rect=RoundedRectangle(
                *self.center_coords_translator(self.x, self.y, self.w, self.h),
                color=self.color,
                radius=10)

    def draw(self,x=60,y=720-30):
        self.visible=True
        self.x=x
        self.y=y
        self.color_clicked()
        try:
            self.rect.draw()
        except AttributeError:
            self.rect=RoundedRectangle(
        *self.center_coords_translator(self.x, self.y, self.w, self.h),
        color=self.color,
        radius=10)
        arcade.draw_text(
            self.text, 
            self.x, 
            self.y, 
            arcade.color.BLACK, 
            font_name=self.font,
            font_size=12, 
            anchor_x="center", 
            anchor_y="center"
        )
    def reset_visible(self):
        self.visible=False
    def resize(self):
        self.rect=RoundedRectangle(
            *self.center_coords_translator(self.x, self.y, self.w, self.h),
            color=self.color,
            radius=10
            )
        
    def hover(self, x, y):
        left = self.x - self.w / 2
        right = self.x + self.w / 2
        bottom = self.y - self.h / 2
        top = self.y + self.h / 2
        if left <= x <= right and bottom <= y <= top or self.clicked:
            self.rect=RoundedRectangle(
            *self.center_coords_translator(self.x, self.y, self.w, self.h),
            color=self.hover_color,
            radius=10
            )
        else:
            self.rect=RoundedRectangle(
            *self.center_coords_translator(self.x, self.y, self.w, self.h),
            color=self.color,
            radius=10
            )

    def check_click(self, x: float, y: float) -> bool:
        global buttons_state
        if self.visible:
            left = self.x - self.w / 2
            right = self.x + self.w / 2
            bottom = self.y - self.h / 2
            top = self.y + self.h / 2
            if not buttons_state[self.number]:
                if left <= x <= right and bottom <= y <= top:
                    if any(buttons_state):
                        for i in range(len(buttons_state)):
                            if i!=self.number: buttons_state[i]=False
                    buttons_state[self.number]=True
                    self.clicked=True
                    return self.clicked
                buttons_state[self.number]=False
            self.clicked=False
            return self.clicked
        return False
    
class Button(ButtonMenu):
    def __init__(self, w=100, h=40, text="Кнопка", font="Arial"):
        self.w = w
        self.h = h
        self.text = text
        self.color = (246,108,0)
        self.hover_color = tuple(i-40 if i-40>0 else i for i in self.color)
        self.pressed = False
        self.font=font
        self.clicked=False
        self.temp=False
        # self.rect=RoundedRectangle(
        # *self.center_coords_translator(self.x, self.y, self.w, self.h),
        # color=self.color,
        # radius=10)
    def color_clicked(self):
        pass

    def check_click(self, x: float, y: float) -> bool:
        if self.visible:
            left = self.x - self.w / 2
            right = self.x + self.w / 2
            bottom = self.y - self.h / 2
            top = self.y + self.h / 2
            if left <= x <= right and bottom <= y <= top:
                self.clicked=True
                return self.clicked
            self.clicked=False
            return self.clicked
        return False
    
class InputText:
    def __init__(self, color=(25,26,27)):
        self.color=color
        self.input=""
        self.shorted=self.input
        self.max_input_fl=False
        self.shorted=""
        pass
    def draw(self,x,y,w,h):
        self.w=w-20
        arcade.draw_rect_filled(arcade.XYWH(x,y,w,h), self.color)
        arcade.draw_text(self.shorted,x-w//2+10,y-h//6,arcade.color.WHITE, font_size=16, width=w-20)
    def update_shorted(self):
        left = 0
        right = len(self.input)
        while left < right:
            mid = (left + right) // 2
            text = arcade.Text(self.input[mid:], 0, 0, font_size=16)
            if text.content_width > self.w:
                left = mid + 1
            else:
                right = mid
        self.shorted = self.input[left:]
    def add_symb(self, letter):
        self.input+=letter
        self.update_shorted()
    def remove_symb(self):
        self.input=self.input[:-1]
        self.update_shorted()


import arcade

import arcade

class SelectList:
    def __init__(self, items=None, color=(25,26,27), selected_color=(246,108,0), text_color=arcade.color.WHITE):
        self.color = color
        self.selected_color = selected_color
        self.text_color = text_color
        self.items = items or []
        self.selected = 0 if self.items else -1
        
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.row_height = 32
        self.scroll_offset = 0.0
        self.visible_count = 0
        self.scrollbar_width = 10
        
        self.scrollbar_dragging = False
        self.scrollbar_drag_offset = 0
        
        # Кэши и сигнатуры
        self.text_cache = []
        self.visible_rects = {}  # Словарь {index: rect} для видимых строк
        self._layout_signature = None
        self._text_cache_signature = None
        self._width_cache = {}
        
        # --- Оптимизации отрисовки ---
        # Один объект для быстрого измерения ширины текста
        self._measure_text = arcade.Text("", 0, 0, font_size=16, color=self.text_color)
        # Пул объектов текста для отрисовки (создаются по мере необходимости)
        self._text_pool = []
        self._active_text_objects = []

    def set_items(self, items):
        self.items = list(items)
        self.selected = 0 if self.items else -1
        self.scroll_offset = 0.0
        self.text_cache = []
        self.visible_rects = {}
        self._layout_signature = None
        self._text_cache_signature = None

    def _measure_width(self, text):
        if not text: return 0
        width = self._width_cache.get(text)
        if width is None:
            self._measure_text.value = text
            width = self._measure_text.content_width
            self._width_cache[text] = width
        return width

    def get_selected(self):
        if 0 <= self.selected < len(self.items):
            return self.items[self.selected]
        return None

    def _max_scroll(self):
        return max(0, len(self.items) - self.visible_count)

    def _has_scroll(self):
        return self._max_scroll() > 0

    def _track_top(self):
        return self.y + self.h // 2 - 8

    def _track_bottom(self):
        return self.y - self.h // 2 + 8

    def _thumb_rect(self):
        if not self._has_scroll():
            return None

        track_top = self._track_top()
        track_bottom = self._track_bottom()
        track_h = max(1, track_top - track_bottom)
        ratio = self.visible_count / len(self.items)
        thumb_h = max(18, int(track_h * ratio))
        max_scroll = self._max_scroll()
        travel = max(1, track_h - thumb_h)
        progress = self.scroll_offset / max_scroll if max_scroll else 0
        thumb_top = track_top - int(travel * progress)
        thumb_bottom = thumb_top - thumb_h
        thumb_y = (thumb_top + thumb_bottom) / 2
        thumb_x = self.x + self.w / 2 - self.scrollbar_width / 2 - 6
        return arcade.XYWH(thumb_x, thumb_y, self.scrollbar_width, thumb_h)

    def _fit_text(self, text, max_width):
        if max_width <= 0:
            return ""

        if self._measure_width(text) <= max_width:
            return text

        ellipsis = "..."
        ellipsis_width = self._measure_width(ellipsis)
        if ellipsis_width >= max_width:
            return ellipsis

        left = 0
        right = len(text)
        while left < right:
            mid = (left + right + 1) // 2
            if self._measure_width(text[:mid]) + ellipsis_width <= max_width:
                left = mid
            else:
                right = mid - 1

        return text[:left] + ellipsis

    def _rebuild_text_cache(self, max_width):
        cache_signature = (tuple(map(str, self.items)), max_width, self.text_color)
        if cache_signature == self._text_cache_signature and len(self.text_cache) == len(self.items):
            return

        self.text_cache = [self._fit_text(str(item), max_width) for item in self.items]
        self._text_cache_signature = cache_signature

    def _update_view(self):
        """Легкое обновление позиций. Вызывается при скролле и клике."""
        self.visible_rects = {}
        self._active_text_objects = []
        
        if not self.items:
            return

        has_scroll = self._has_scroll()
        scrollbar_shift = (self.scrollbar_width + 10) if has_scroll else 0
        top = self.y + self.h / 2 - self.row_height / 2 - 8
        left = self.x - self.w // 2 + 12
        
        scroll_start = max(0, min(int(self.scroll_offset), self._max_scroll()))
        scroll_fraction = self.scroll_offset - scroll_start
        visible_end = min(len(self.items), scroll_start + self.visible_count + 1)

        # Убеждаемся, что пул текстовых объектов достаточно велик
        while len(self._text_pool) < (visible_end - scroll_start):
            self._text_pool.append(arcade.Text("", 0, 0, font_size=16, color=self.text_color, anchor_y="center"))

        pool_idx = 0
        for draw_index, item_index in enumerate(range(scroll_start, visible_end)):
            row_y = top - (draw_index * self.row_height) - (scroll_fraction * self.row_height)
            row_w = self.w - 8 - scrollbar_shift
            rect = arcade.XYWH(self.x - scrollbar_shift / 2 if has_scroll else self.x, row_y, row_w, self.row_height - 4)
            
            # Сохраняем ВСЕ видимые прямоугольники
            self.visible_rects[item_index] = rect

            # Берем текст из кэша и обновляем объект из пула
            text_str = self.text_cache[item_index] if item_index < len(self.text_cache) else str(self.items[item_index])
            text_obj = self._text_pool[pool_idx]
            text_obj.value = text_str
            text_obj.position = (left, row_y)
            self._active_text_objects.append(text_obj)
            pool_idx += 1

    def pre_draw(self, x, y, w, h):
        signature = (x, y, w, h)
        if signature == self._layout_signature:
            return

        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.row_height = 32 if not self.items else max(24, min(40, h // max(1, len(self.items))))
        content_h = max(1, h - 16)
        self.visible_count = max(1, int(content_h // self.row_height))
        self.scroll_offset = max(0.0, min(self.scroll_offset, float(self._max_scroll())))

        max_width = w - 24 - (self.scrollbar_width + 10 if self._has_scroll() else 0)
        self._rebuild_text_cache(max_width)
        self._update_view()
        self._layout_signature = signature

    def draw(self, x=None, y=None, w=None, h=None):
        if x is not None:
            self.pre_draw(x, y, w, h)

        # 1. Рисуем ОДИН фон вместо N прямоугольников
        arcade.draw_rect_filled(arcade.XYWH(self.x, self.y, self.w, self.h), self.color)

        # 2. Рисуем ОДИН прямоугольник для выбранной строки (если она видна)
        if self.selected in self.visible_rects:
            arcade.draw_rect_filled(self.visible_rects[self.selected], self.selected_color)

        # 3. Рисуем скроллбар (трек и ползунок)
        if self._has_scroll():
            track_x = self.x + self.w / 2 - self.scrollbar_width / 2 - 6
            track_y = (self._track_top() + self._track_bottom()) / 2
            track_h = self._track_top() - self._track_bottom()
            arcade.draw_rect_filled(arcade.XYWH(track_x, track_y, self.scrollbar_width, track_h), (50, 52, 54))
            
            thumb = self._thumb_rect()
            if thumb:
                arcade.draw_rect_filled(thumb, (190, 192, 194))

        # 4. Рисуем текст из пула
        for text_obj in self._active_text_objects:
            text_obj.draw()

    def rectangles_change(self):
        self.scroll_offset = max(0.0, min(self.scroll_offset, float(self._max_scroll())))
        self._update_view()

    def contains(self, x, y):
        left = self.x - self.w / 2
        right = self.x + self.w / 2
        top = self.y + self.h / 2
        bottom = self.y - self.h / 2
        return left <= x <= right and bottom <= y <= top

    def scroll(self, delta):
        if not self._has_scroll() or delta == 0:
            return False
        prev = self.scroll_offset
        self.scroll_offset = max(0.0, min(self.scroll_offset - float(delta), float(self._max_scroll())))
        if prev != self.scroll_offset:
            self._update_view()
            return True
        return False

    def start_scrollbar_drag(self, x, y):
        if not self._has_scroll():
            return False
        thumb = self._thumb_rect()
        if thumb is None:
            return False
        left = thumb.center_x - thumb.width / 2
        right = thumb.center_x + thumb.width / 2
        bottom = thumb.center_y - thumb.height / 2
        top = thumb.center_y + thumb.height / 2
        if left <= x <= right and bottom <= y <= top:
            self.scrollbar_dragging = True
            self.scrollbar_drag_offset = top - y
            return True
        return False

    def drag_scrollbar(self, y):
        if not self.scrollbar_dragging or not self._has_scroll():
            return False

        track_top = self._track_top()
        track_bottom = self._track_bottom()
        thumb = self._thumb_rect()
        thumb_h = thumb.height
        travel = max(1, (track_top - track_bottom) - thumb_h)
        new_top = max(track_bottom + thumb_h, min(track_top, y + self.scrollbar_drag_offset))
        progress = (track_top - new_top) / travel
        new_offset = max(0.0, min(progress * self._max_scroll(), float(self._max_scroll())))
        if new_offset != self.scroll_offset:
            self.scroll_offset = new_offset
            self._update_view()
            return True
        return False

    def stop_scrollbar_drag(self):
        self.scrollbar_dragging = False
        self.scrollbar_drag_offset = 0

    def check_click(self, x, y):
        if not self.items:
            return None

        # Перебираем ВСЕ видимые прямоугольники
        for index, rect in self.visible_rects.items():
            left = rect.center_x - rect.width / 2
            right = rect.center_x + rect.width / 2
            bottom = rect.center_y - rect.height / 2
            top = rect.center_y + rect.height / 2

            if left <= x <= right and bottom <= y <= top:
                self.selected = index
                self._update_view() 
                return index

        return None
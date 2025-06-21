import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk, ImageSequence
import threading
import time
import pynput.mouse
from pynput.keyboard import Listener as KeyboardListener, Key
import os
import sys
from tkinter import messagebox

# Настройка стиля
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class InteractiveSplashScreen:
    def __init__(self, on_click_callback):
        self.splash = tk.Toplevel()
        self.splash.overrideredirect(True)
        self.splash.attributes('-topmost', True)
        self.splash.geometry("400x300+500+300")
        self.splash.configure(bg="#2b2b2b")
        self.on_click = on_click_callback
        self.running = True
        
        # Загрузка гифки
        gif_path = self.resource_path("loading.gif")
        try:
            self.gif = Image.open(gif_path)
            self.frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(self.gif)]
            
            self.label = tk.Label(self.splash, bg="#2b2b2b", cursor="hand2")
            self.label.pack(expand=True)
            self.label.bind("<Button-1>", self.handle_click)
            
            # Текст "Нажмите для продолжения"
            self.click_text = tk.Label(
                self.splash, 
                text="Нажмите для продолжения", 
                bg="#2b2b2b", 
                fg="white",
                font=("Arial", 12)
            )
            self.click_text.pack(side="bottom", pady=20)
            
            self.current_frame = 0
            self.animate()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить гифку: {str(e)}")
            self.splash.destroy()
            sys.exit(1)
        
    def handle_click(self, event):
        self.running = False
        self.splash.destroy()
        self.on_click()
        
    def animate(self):
        if self.running:
            if self.current_frame < len(self.frames):
                self.label.configure(image=self.frames[self.current_frame])
                self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.splash.after(50, self.animate)
    
    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        path = os.path.join(base_path, relative_path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Файл не найден: {path}")
        return path

class GraveAutoClicker(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Скрываем главное окно сначала
        
        # Инициализация переменных
        self.clicking = False
        self.click_thread = None
        self.keyboard_listener = None
        self.splash = None
        
        # Показываем интерактивный splash screen
        self.show_splash_screen()
        
        # Настройки
        self.cps = 10
        self.button = "left"
        self.hotkey = "F6"
        self.bind_mode = False
        self.mouse = pynput.mouse.Controller()
        
        # Обработка закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def show_splash_screen(self):
        self.splash = InteractiveSplashScreen(self.show_main_window)
    
    def show_main_window(self):
        # Настройка окна
        self.title("GraveAutoClicker")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Создание интерфейса
        self.create_widgets()
        
        # Слушатель клавиатуры
        self.keyboard_listener = KeyboardListener(on_press=self.on_key_press)
        self.keyboard_listener.start()
        
        # Показываем главное окно с анимацией
        self.deiconify()
        self.animate_window()
    
    def create_widgets(self):
        # Главный фрейм
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Заголовок с анимацией
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="GraveAutoClicker",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#4CC9F0"
        )
        self.title_label.pack(pady=(20, 10))
        
        # Анимированный статус
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Статус: Остановлен",
            font=ctk.CTkFont(size=12),
            text_color="#F72585"
        )
        self.status_label.pack(pady=5)
        
        # Настройки кликера
        self.settings_frame = ctk.CTkFrame(self.main_frame, corner_radius=8)
        self.settings_frame.pack(pady=10, padx=20, fill="x")
        
        # Выбор кнопки
        ctk.CTkLabel(self.settings_frame, text="Кнопка:").pack(pady=(10, 0))
        self.button_combo = ctk.CTkComboBox(
            self.settings_frame,
            values=["Левая", "Правая", "Колесо"],
            button_color="#4361EE",
            dropdown_hover_color="#3A0CA3"
        )
        self.button_combo.pack(pady=5, padx=20, fill="x")
        self.button_combo.set("Левая")
        
        # Кликов в секунду (до 150)
        ctk.CTkLabel(self.settings_frame, text="Кликов/сек (1-150):").pack(pady=(10, 0))
        self.cps_slider = ctk.CTkSlider(
            self.settings_frame,
            from_=1,
            to=150,
            number_of_steps=149,
            button_color="#4361EE",
            button_hover_color="#3A0CA3"
        )
        self.cps_slider.set(10)
        self.cps_slider.pack(pady=5, padx=20, fill="x")
        
        self.cps_value = ctk.CTkLabel(self.settings_frame, text="10")
        self.cps_value.pack()
        
        # Горячая клавиша
        ctk.CTkLabel(self.settings_frame, text="Горячая клавиша:").pack(pady=(10, 0))
        self.hotkey_entry = ctk.CTkEntry(
            self.settings_frame,
            placeholder_text="F6",
            justify="center"
        )
        self.hotkey_entry.pack(pady=5, padx=20, fill="x")
        self.hotkey_entry.insert(0, "F6")
        
        self.bind_button = ctk.CTkButton(
            self.settings_frame,
            text="Изменить",
            command=self.toggle_bind_mode,
            fg_color="#4361EE",
            hover_color="#3A0CA3"
        )
        self.bind_button.pack(pady=(0, 10), padx=20, fill="x")
        
        # Кнопки управления
        self.buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.buttons_frame.pack(pady=20)
        
        self.start_button = ctk.CTkButton(
            self.buttons_frame,
            text="Старт",
            command=self.start_clicker,
            fg_color="#4CC9F0",
            hover_color="#4895EF",
            width=120,
            height=40,
            corner_radius=8
        )
        self.start_button.pack(side='left', padx=10)
        
        self.stop_button = ctk.CTkButton(
            self.buttons_frame,
            text="Стоп",
            command=self.stop_clicker,
            fg_color="#F72585",
            hover_color="#B5179E",
            width=120,
            height=40,
            corner_radius=8,
            state="disabled"
        )
        self.stop_button.pack(side='left', padx=10)
        
        # Привязка событий
        self.cps_slider.bind("<Motion>", self.update_cps_display)
    
    def animate_window(self):
        self.alpha = 0
        self.fade_in()
    
    def fade_in(self):
        if self.alpha < 1:
            self.alpha += 0.05
            self.attributes("-alpha", self.alpha)
            self.after(20, self.fade_in)
    
    def start_clicker(self):
        if not self.clicking:
            self.clicking = True
            self.status_label.configure(text="Статус: Работает", text_color="#4CC9F0")
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            
            self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
            self.click_thread.start()
            
            self.animate_button(self.start_button, "#4CC9F0")
    
    def stop_clicker(self):
        if self.clicking:
            self.clicking = False
            self.status_label.configure(text="Статус: Остановлен", text_color="#F72585")
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            
            if self.click_thread:
                self.click_thread.join(timeout=0.1)
            
            self.animate_button(self.stop_button, "#F72585")
    
    def click_loop(self):
        button_map = {
            "Левая": pynput.mouse.Button.left,
            "Правая": pynput.mouse.Button.right,
            "Колесо": pynput.mouse.Button.middle
        }
        
        selected_button = self.button_combo.get()
        cps = self.cps_slider.get()
        delay = 1.0 / cps if cps > 0 else 0
        
        while self.clicking and selected_button in button_map:
            try:
                self.mouse.click(button_map[selected_button])
                if delay > 0:
                    time.sleep(delay)
            except Exception as e:
                print(f"Ошибка клика: {e}")
                self.stop_clicker()
                break
    
    def toggle_bind_mode(self):
        self.bind_mode = not self.bind_mode
        if self.bind_mode:
            self.bind_button.configure(text="Нажмите клавишу...")
            self.hotkey_entry.delete(0, tk.END)
            self.hotkey_entry.insert(0, "...")
        else:
            self.bind_button.configure(text="Изменить")
    
    def on_key_press(self, key):
        if self.bind_mode:
            try:
                key_name = key.char.upper()
            except AttributeError:
                key_name = key.name.upper()
            
            self.hotkey = key_name
            self.hotkey_entry.delete(0, tk.END)
            self.hotkey_entry.insert(0, key_name)
            self.toggle_bind_mode()
        elif hasattr(key, 'name') and key.name.upper() == self.hotkey:
            if not self.clicking:
                self.start_clicker()
            else:
                self.stop_clicker()
    
    def update_cps_display(self, event):
        self.cps_value.configure(text=str(int(self.cps_slider.get())))
    
    def animate_button(self, button, color):
        original_color = button.cget("fg_color")
        steps = 10
        
        def animate_step(step):
            if step <= steps:
                r = int(original_color[1:3], 16)
                g = int(original_color[3:5], 16)
                b = int(original_color[5:7], 16)
                
                new_r = r + (int(color[1:3], 16) - r) * step / steps
                new_g = g + (int(color[3:5], 16) - g) * step / steps
                new_b = b + (int(color[5:7], 16) - b) * step / steps
                
                hex_color = f"#{int(new_r):02x}{int(new_g):02x}{int(new_b):02x}"
                button.configure(fg_color=hex_color)
                self.after(30, lambda: animate_step(step + 1))
        
        animate_step(1)
    
    def on_close(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите закрыть приложение?"):
            # Останавливаем кликер
            self.clicking = False
            
            # Останавливаем поток кликера
            if self.click_thread:
                self.click_thread.join(timeout=0.5)
            
            # Останавливаем слушатель клавиатуры
            if self.keyboard_listener:
                self.keyboard_listener.stop()
            
            # Закрываем splash screen, если он еще открыт
            if hasattr(self, 'splash') and self.splash:
                self.splash.running = False
                try:
                    self.splash.splash.destroy()
                except:
                    pass
            
            # Закрываем приложение
            self.destroy()
            self.quit()

if __name__ == "__main__":
    app = GraveAutoClicker()
    app.mainloop()
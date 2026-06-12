import cv2
import mediapipe as mp
import numpy as np
from pynput.mouse import Button, Controller
import tkinter as tk
from PIL import Image, ImageTk
import time
import ctypes

# Windows DPI Ayarı
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


class MouseKontrol:
    def __init__(self, root):
        self.root = root
        self.root.title("El İle Mouse Kontrol Sistemi")
        self.root.attributes("-topmost", True)

        # İlk Başlangıç Boyutları (Kontrol Paneli)
        self.panel_w, self.panel_h = 400, 500
        # Çalışma Modu Boyutları (Sadece Kamera)
        self.cam_w, self.cam_h = 800, 600

        self.root.geometry(f"{self.panel_w}x{self.panel_h}+100+100")

        self.bg_color = "#1D1D1F"
        self.accent_color = "#0071E3"
        self.text_color = "#F5F5F7"
        self.video_bg = "#000000"
        self.danger_color = "#FF3B30"
        self.secondary_text = "#86868B"

        self.root.configure(bg=self.bg_color)
        self.mouse = Controller()

        self.p_locX, self.p_locY = 0, 0
        self.running = False
        self.cap = None

        self.is_dragging = False
        self.click_pressed = False
        self.last_click_time = 0
        self.fist_start_time = 0
        self.scroll_accumulator = 0
        self.last_action_time = 0

        # HIZ VE AKICILIK AYARLARI
        self.base_smooth = 0.10
        self.precision_smooth = 0.02
        self.click_limit = 28
        self.scroll_limit = 35
        self.scroll_sensitivity = 0.15
        self.double_click_gap = 0.30
        self.action_cooldown = 0.25
        self.fist_threshold = 0.45

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )

        self.setup_ui()

        # "q" tuşuna basınca durdurma özelliği
        self.root.bind('q', lambda e: self.toggle_system() if self.running else None)

    def setup_ui(self):
        # Tüm UI bileşenlerini bir ana frame içinde topluyoruz
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill="both", expand=True)

        self.title_label = tk.Label(self.main_frame, text="El İle Mouse Kontrol Sistemi", bg=self.bg_color,
                                    fg=self.text_color, font=("Segoe UI", 14, "bold"))
        self.title_label.pack(pady=20)

        self.start_btn = tk.Button(
            self.main_frame, text="SİSTEMİ BAŞLAT", command=self.toggle_system,
            bg=self.accent_color, fg="white", font=("Segoe UI", 10, "bold"), width=20, height=2,
            relief="flat", cursor="hand2"
        )
        self.start_btn.pack(pady=10)

        # Video label başlangıçta panel içinde
        self.video_label = tk.Label(self.root, bg=self.video_bg, highlightthickness=0)
        self.video_label.pack(pady=10)

        self.info_label = tk.Label(self.main_frame, text="Durdurmak için 'q' tuşuna basın",
                                   bg=self.bg_color, fg=self.secondary_text, font=("Segoe UI", 9))
        self.info_label.pack(side="bottom", pady=10)

    def toggle_system(self):
        if not self.running:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.cap.isOpened(): return


            self.running = True
            self.main_frame.pack_forget()  # Yazıları ve butonu gizle
            self.root.geometry(f"{self.cam_w}x{self.cam_h}+0+0")  # Sol üste git ve büyüt
            self.video_label.pack(fill="both", expand=True, pady=0)  # Videoyu tam ekran yap

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.update_loop()
        else:
            #MOD DEĞİŞİMİ: PANELE GERİ DÖN
            self.running = False
            if self.cap: self.cap.release()
            self.video_label.pack_forget()
            self.video_label.config(image="")

            self.root.geometry(f"{self.panel_w}x{self.panel_h}+100+100")  # Eski konuma dön
            self.main_frame.pack(fill="both", expand=True)  # UI'ı geri getir
            self.video_label.pack(pady=10)  # Video alanını yerine koy
            self.reset_all_actions()

    def reset_all_actions(self):
        if self.is_dragging: self.mouse.release(Button.left)
        self.is_dragging = False
        self.click_pressed = False

    def handle_fist_release(self, now):
        self.mouse.release(Button.left)
        if (now - self.fist_start_time) < self.fist_threshold:
            self.mouse.click(Button.right, 1)
        self.is_dragging = False
        self.last_action_time = now

    def update_loop(self):
        if self.running and self.cap:
            success, img = self.cap.read()
            if success:
                img = cv2.flip(img, 1)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = self.hands.process(img_rgb)
                now = time.time()

                if results.multi_hand_landmarks:
                    for hand_lms in results.multi_hand_landmarks:
                        lms = hand_lms.landmark
                        thumb, index, middle, palm = lms[4], lms[8], lms[12], lms[9]

                        d_click = np.hypot((thumb.x - middle.x) * 640, (thumb.y - middle.y) * 480)
                        d_scroll = np.hypot((thumb.x - index.x) * 640, (thumb.y - index.y) * 480)
                        is_fist = index.y > lms[6].y and middle.y > lms[10].y

                        current_smooth = self.precision_smooth if d_click < (
                                    self.click_limit + 15) else self.base_smooth
                        if is_fist: current_smooth = 0.14

                        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
                        target_x = np.interp(palm.x * 640, (120, 520), (0, sw))
                        target_y = np.interp(palm.y * 480, (100, 380), (0, sh))

                        curr_x = self.p_locX + (target_x - self.p_locX) * current_smooth
                        curr_y = self.p_locY + (target_y - self.p_locY) * current_smooth

                        self.mouse.position = (int(curr_x), int(curr_y))
                        diff_y = self.p_locY - curr_y
                        self.p_locX, self.p_locY = curr_x, curr_y

                        if now - self.last_action_time > self.action_cooldown:
                            if is_fist:
                                if not self.is_dragging:
                                    self.mouse.press(Button.left)
                                    self.is_dragging, self.fist_start_time = True, now
                            elif d_click < self.click_limit:
                                if not self.click_pressed:
                                    if (now - self.last_click_time) < self.double_click_gap:
                                        self.mouse.click(Button.left, 2)
                                        self.last_action_time = now
                                    else:
                                        self.mouse.click(Button.left, 1)
                                        self.last_click_time = now
                                    self.click_pressed = True
                            elif d_scroll < self.scroll_limit:
                                self.scroll_accumulator += diff_y * self.scroll_sensitivity
                                scroll_val = int(self.scroll_accumulator)
                                if scroll_val != 0:
                                    self.mouse.scroll(0, scroll_val)
                                    self.scroll_accumulator -= scroll_val
                            else:
                                if self.is_dragging: self.handle_fist_release(now)
                                self.click_pressed = False

                        mp.solutions.drawing_utils.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
                else:
                    self.reset_all_actions()


                img_resized = cv2.resize(img, (self.cam_w, self.cam_h))
                img_tk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)))
                self.video_label.imgtk = img_tk
                self.video_label.configure(image=img_tk)

            self.root.after(15, self.update_loop)


if __name__ == "__main__":
    root = tk.Tk()
    app = MouseKontrol(root)
    root.mainloop()
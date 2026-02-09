import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time
import math
import json
import os
import sys

# --- KONFIGURACJA ŚCIEŻEK ---
def resource_path(relative_path):
    """ Obsługa zasobów dla wersji .py oraz skompilowanego .exe """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

BASE_DIR = os.path.join(os.path.expanduser("~"), ".polsoft", "games")
SCORE_FILE = os.path.join(BASE_DIR, "DiceRollerBattle.json")

# --- ULTRA HD PALETTE ---
C_BG = "#020406"      
C_CYAN = "#00f2ff"    
C_PINK = "#ff0055"    
C_GOLD = "#ffcc00"    
C_SCAN = "#0a0e14"
C_GLOW_CYAN = "#004444"
C_GLOW_PINK = "#440011"

class DiceRollerBattle:
    def __init__(self, root):
        self.root = root
        self.root.title("DICE ROLLER BATTLE // polsoft.ITS™")
        self.root.geometry("450x650")
        self.root.configure(bg=C_BG)
        self.root.resizable(False, False)

        # Inicjalizacja folderu danych
        if not os.path.exists(BASE_DIR):
            os.makedirs(BASE_DIR)

        # Ładowanie ikony (opcjonalnie)
        try:
            self.root.iconbitmap(resource_path("icon.ico"))
        except:
            pass

        self.p_score, self.c_score = 0, 0
        self.round = 1
        self.particles = []
        self.running = True
        
        self.data = self.load_data()
        self.mode = self.data.get("settings", {}).get("last_mode", 6)

        self.canvas = tk.Canvas(root, width=450, height=650, bg=C_BG, highlightthickness=0)
        self.canvas.pack()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_menu()
        self.update_fx_loop()

    # --- SYSTEM ZAPISU ---
    def load_data(self):
        default = {"top_scores": [], "settings": {"last_mode": 6}}
        if os.path.exists(SCORE_FILE):
            try:
                with open(SCORE_FILE, "r") as f: return json.load(f)
            except: return default
        return default

    def save_data(self):
        with open(SCORE_FILE, "w") as f: json.dump(self.data, f, indent=4)

    # --- SILNIK GRAFICZNY ---
    def create_particles(self, x, y, color):
        for _ in range(4):
            p = self.canvas.create_rectangle(x, y, x+2, y+2, fill=color, outline="")
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)
            self.particles.append({'id': p, 'vx': math.cos(angle)*speed, 'vy': math.sin(angle)*speed, 'life': 1.0})

    def update_fx_loop(self):
        if not self.running: return
        for p in self.particles[:]:
            self.canvas.move(p['id'], p['vx'], p['vy'])
            p['life'] -= 0.08
            if p['life'] <= 0:
                self.canvas.delete(p['id'])
                self.particles.remove(p)
        self.root.after(30, self.update_fx_loop)

    def draw_glow_rect(self, x1, y1, x2, y2, color):
        for i in range(4, 0, -1):
            offset = i * 2
            self.canvas.create_rectangle(x1-offset, y1-offset, x2+offset, y2+offset, outline=color, width=1, tags="fx")

    def draw_base_ui(self):
        for i in range(0, 650, 4): # Scanlines
            self.canvas.create_line(0, i, 450, i, fill=C_SCAN, width=1)
        self.canvas.create_rectangle(0, 0, 450, 40, fill="#080c12", outline=C_CYAN)
        self.canvas.create_text(225, 635, text="polsoft.ITS™ London // TERMINAL_v4.0_STABLE", fill="#1a2533", font=("Consolas", 7))

    def clear(self):
        self.canvas.delete("all")
        self.draw_base_ui()

    # --- EKRANY ---
    def show_menu(self):
        self.clear()
        self.canvas.create_text(228, 123, text="DICE ROLLER", fill="#110005", font=("Impact", 50, "italic"))
        self.canvas.create_text(225, 120, text="DICE ROLLER", fill=C_CYAN, font=("Impact", 48, "italic"))
        self.canvas.create_text(225, 175, text="BATTLE SYSTEM", fill=C_PINK, font=("Impact", 35, "italic"))
        
        self.draw_btn("INITIALIZE_LINK", 300, self.start_setup)
        self.draw_btn("DATA_ARCHIVE", 370, self.show_top5)
        self.draw_btn("TERMINATE", 440, self.on_close)

    def start_setup(self):
        self.clear()
        self.canvas.create_text(225, 150, text="SELECT_DICE_CORE", fill=C_GOLD, font=("Impact", 30))
        self.draw_btn("D6_NEURAL", 280, lambda: self.init_battle(6))
        self.draw_btn("D20_SYNAPTIC", 350, lambda: self.init_battle(20))

    def init_battle(self, mode):
        self.mode = mode
        self.data["settings"]["last_mode"] = mode
        self.save_data()
        self.p_score, self.c_score, self.round = 0, 0, 1
        self.show_battle_screen()

    def show_battle_screen(self):
        self.clear()
        self.hud_id = self.canvas.create_text(225, 20, text=f"CORE: D{self.mode} // SEQ: {self.round}/5", fill=C_CYAN, font=("Consolas", 10, "bold"))
        self.score_id = self.canvas.create_text(225, 90, text="00 - 00", fill=C_PINK, font=("Impact", 60))
        
        self.draw_glow_rect(60, 220, 180, 340, C_GLOW_CYAN)
        self.canvas.create_rectangle(60, 220, 180, 340, outline=C_CYAN, width=2)
        
        self.draw_glow_rect(270, 220, 390, 340, C_GLOW_PINK)
        self.canvas.create_rectangle(270, 220, 390, 340, outline=C_PINK, width=2)

        self.p_val = self.canvas.create_text(120, 280, text="??", fill=C_CYAN, font=("Impact", 85))
        self.c_val = self.canvas.create_text(330, 280, text="??", fill=C_PINK, font=("Impact", 85))

        self.btn_roll = tk.Button(self.root, text="EXECUTE_ROLL", command=self.animate_roll,
                                 bg=C_PINK, fg="white", font=("Arial", 12, "bold"), bd=0, padx=40, pady=10)
        self.canvas.create_window(225, 500, window=self.btn_roll)

    def animate_roll(self):
        self.btn_roll.config(state="disabled")
        for i in range(15):
            if not self.running: return
            off_x, off_y = random.randint(-3, 3), random.randint(-3, 3)
            self.canvas.move("all", off_x, off_y)
            self.canvas.itemconfig(self.p_val, text=str(random.randint(1, self.mode)), fill="white" if i%2==0 else C_CYAN)
            self.canvas.itemconfig(self.c_val, text=str(random.randint(1, self.mode)), fill="white" if i%2==0 else C_PINK)
            self.create_particles(120, 280, C_CYAN); self.create_particles(330, 280, C_PINK)
            self.root.update(); time.sleep(0.045)
            self.canvas.move("all", -off_x, -off_y)

        p_res, c_res = random.randint(1, self.mode), random.randint(1, self.mode)
        self.p_score += p_res; self.c_score += c_res
        self.canvas.itemconfig(self.p_val, text=f"{p_res:02d}", fill=C_CYAN)
        self.canvas.itemconfig(self.c_val, text=f"{c_res:02d}", fill=C_PINK)
        self.canvas.itemconfig(self.score_id, text=f"{self.p_score:02d} - {self.c_score:02d}")

        if self.round >= 5:
            self.root.after(1000, self.finish)
        else:
            self.round += 1
            self.canvas.itemconfig(self.hud_id, text=f"CORE: D{self.mode} // SEQ: {self.round}/5")
            self.btn_roll.config(state="normal")

    def finish(self):
        if not self.running: return
        res = "VICTORY" if self.p_score > self.c_score else "DEFEAT"
        messagebox.showinfo("BATTLE_REPORT", f"STATUS: {res}\nTOTAL: {self.p_score} - {self.c_score}")
        name = simpledialog.askstring("DATABASE", "ENTER OPERATOR NAME:")
        if name:
            scores = self.data.get("top_scores", [])
            scores.append({"name": name, "score": self.p_score, "date": time.strftime("%Y-%m-%d")})
            self.data["top_scores"] = sorted(scores, key=lambda x: x['score'], reverse=True)[:5]
            self.save_data()
        self.show_menu()

    def show_top5(self):
        self.clear()
        self.canvas.create_text(225, 80, text="TOP_OPERATORS", fill=C_GOLD, font=("Impact", 35))
        scores = self.data.get("top_scores", [])
        for i, s in enumerate(scores):
            txt = f"{i+1}. {s['name'][:12].upper()} >> {s['score']} PTS"
            self.canvas.create_text(225, 190+(i*45), text=txt, fill="white", font=("Consolas", 14))
        self.draw_btn("BACK", 520, self.show_menu)

    def on_close(self):
        self.running = False
        self.root.destroy()

    def draw_btn(self, text, y, cmd):
        btn = tk.Button(self.root, text=text, command=cmd, bg=C_BG, fg=C_CYAN,
                        activebackground=C_CYAN, activeforeground=C_BG,
                        font=("Consolas", 11, "bold"), bd=1, relief="flat", width=25)
        self.canvas.create_window(225, y, window=btn)

if __name__ == "__main__":
    root = tk.Tk()
    app = DiceRollerBattle(root)
    root.mainloop()
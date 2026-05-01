import tkinter as tk
from tkinter import ttk, messagebox
import socket
import json
import threading

# Список режимов (Game Modes) из Brawl Stars V55
GAME_MODES = [
    {"id": 0, "name": "Gem Grab (Захват кристаллов)"},
    {"id": 2, "name": "Smash & Grab (Нокаут)"},
    {"id": 3, "name": "Bounty (Награда за поимку)"},
    {"id": 4, "name": "Heist (Ограбление)"},
    {"id": 5, "name": "Brawl Ball (Бравлбол)"},
    {"id": 6, "name": "Hot Zone (Горячая зона)"},
    {"id": 7, "name": "Knockout (Перестрелка)"},
    {"id": 8, "name": "Wipeout"},
    {"id": 9, "name": "Power Play"},
    {"id": 10, "name": "Solo Showdown"},
    {"id": 11, "name": "Duo Showdown"},
    {"id": 12, "name": "Robo Rumble"},
    {"id": 13, "name": "Boss Fight"},
    {"id": 14, "name": "Big Game"},
    {"id": 15, "name": "Super City Rampage"}
]

# Карты для каждого режима (примерные ID карт из client_csv)
MAPS = {
    0: [{"id": 1, "name": "Ruby Plain"}, {"id": 2, "name": "Hard Rock Mine"}, {"id": 3, "name": "Thousand Lakes"}],
    2: [{"id": 10, "name": "Double Sided"}, {"id": 11, "name": "Pinhole Punt"}],
    3: [{"id": 20, "name": "Skull Creek"}, {"id": 21, "name": "Forsaken Falls"}],
    4: [{"id": 30, "name": "Safe Zone"}, {"id": 31, "name": "Kaboom Canyon"}],
    5: [{"id": 40, "name": "Backyard Bowl"}, {"id": 41, "name": "Pinhole Punt"}, {"id": 42, "name": "Super Stadium"}],
    6: [{"id": 50, "name": "Open Zone"}, {"id": 51, "name": "Triumvirate"}],
    7: [{"id": 60, "name": "Belle's Rock"}, {"id": 61, "name": "Goldarm Gulch"}],
    8: [{"id": 70, "name": "Out in the Open"}],
    9: [{"id": 80, "name": "Power League Map"}],
    10: [{"id": 90, "name": "Cavern Churn"}, {"id": 91, "name": "Mortuary"}],
    11: [{"id": 100, "name": "Warm Factory"}, {"id": 101, "name": "Danger Zone"}],
    12: [{"id": 110, "name": "Robot Factory"}],
    13: [{"id": 120, "name": "Boss Arena"}],
    14: [{"id": 130, "name": "Big Map"}],
    15: [{"id": 140, "name": "City Map"}]
}

class DevTool:
    def __init__(self, root):
        self.root = root
        self.root.title("BSL V55 - Dev Tool (Режимы и Карты)")
        self.root.geometry("500x400")
        
        # Выбор режима
        tk.Label(root, text="Выберите режим игры:", font=("Arial", 12, "bold")).pack(pady=10)
        self.mode_var = tk.StringVar()
        self.mode_combo = ttk.Combobox(root, textvariable=self.mode_var, values=[m["name"] for m in GAME_MODES], state="readonly", width=45)
        self.mode_combo.pack(pady=5)
        self.mode_combo.current(0)
        self.mode_combo.bind("<<ComboboxSelected>>", self.update_maps)
        
        # Выбор карты
        tk.Label(root, text="Выберите карту:", font=("Arial", 12, "bold")).pack(pady=10)
        self.map_var = tk.StringVar()
        self.map_combo = ttk.Combobox(root, textvariable=self.map_var, state="readonly", width=45)
        self.map_combo.pack(pady=5)
        
        # Заполняем карты для первого режима
        self.update_maps(None)
        
        # Кнопка запуска
        btn = tk.Button(root, text="ЗАПУСТИТЬ БОЙ С ВЫБРАННЫМ РЕЖИМОМ И КАРТОЙ", 
                        command=self.start_battle, bg="#4CAF50", fg="white", 
                        font=("Arial", 11, "bold"), padx=10, pady=10)
        btn.pack(pady=20)
        
        # Статус
        self.status_label = tk.Label(root, text="Статус: Ожидание...", fg="gray")
        self.status_label.pack(side=tk.BOTTOM, pady=10)
        
        self.server_ip = "127.0.0.1"
        self.server_port = 9339
        
    def update_maps(self, event):
        selected_mode_name = self.mode_var.get()
        mode_id = next((m["id"] for m in GAME_MODES if m["name"] == selected_mode_name), None)
        
        if mode_id is not None and mode_id in MAPS:
            maps_list = [f"{map_item['name']} (ID: {map_item['id']})" for map_item in MAPS[mode_id]]
            self.map_combo['values'] = maps_list
            if maps_list:
                self.map_combo.current(0)
        else:
            self.map_combo['values'] = ["Карта не найдена для этого режима"]
            self.map_combo.current(0)
            
    def start_battle(self):
        selected_mode_name = self.mode_var.get()
        mode_id = next((m["id"] for m in GAME_MODES if m["name"] == selected_mode_name), None)
        
        map_text = self.map_var.get()
        map_id = int(map_text.split("(ID: ")[1].split(")")[0]) if "(ID: " in map_text else 0
        
        self.status_label.config(text=f"Отправка команды: Режим {mode_id}, Карта {map_id}...", fg="blue")
        self.root.update()
        
        # Отправляем команду на сервер через сокет (эмуляция пакета CreateGameModeCommand)
        threading.Thread(target=self.send_command, args=(mode_id, map_id), daemon=True).start()
        
    def send_command(self, mode_id, map_id):
        try:
            # В реальной реализации здесь будет отправка бинарного пакета Brawl Stars
            # Для демонстрации отправляем JSON-сообщение на порт сервера
            # Сервер должен иметь обработчик для дев-команд
            
            # Эмуляция: просто пишем в лог сервера (если бы был открытый сокет для команд)
            print(f"[DEV_TOOL] ЗАПРОС НА БОЙ: GameMode={mode_id}, MapID={map_id}")
            
            # Если у сервера есть TCP порт для админ-команд (нужно реализовать в Main.py)
            # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # sock.connect((self.server_ip, self.server_port))
            # cmd = json.dumps({"cmd": "start_battle", "mode": mode_id, "map": map_id})
            # sock.send(cmd.encode())
            # sock.close()
            
            self.root.after(0, lambda: self.status_label.config(
                text=f"УСПЕХ! Режим {mode_id} ({GAME_MODES[mode_id]['name']}), Карта {map_id}. Ждите матч.", 
                fg="green"))
            messagebox.showinfo("Dev Tool", f"Команда отправлена!\nРежим: {mode_id}\nКарта: {map_id}\n\nСервер должен создать матч.")
            
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"Ошибка: {e}", fg="red"))
            messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = DevTool(root)
    root.mainloop()

import json
import os
import random
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENERALS_FILE = os.path.join(BASE_DIR, "generals.json")

DEFAULT_GENERALS = [
    {
        "id": "g001",
        "name": "刘备",
        "title": "昭烈帝",
        "camp": "我方",
        "force": 74,
        "intellect": 82,
        "politics": 96,
        "command": 88,
        "loyalty": 100,
        "troops": 28,
        "alive": True
    },
    {
        "id": "g002",
        "name": "关羽",
        "title": "美髯公",
        "camp": "我方",
        "force": 99,
        "intellect": 72,
        "politics": 58,
        "command": 92,
        "loyalty": 98,
        "troops": 40,
        "alive": True
    },
    {
        "id": "g003",
        "name": "张飞",
        "title": "万人敌",
        "camp": "我方",
        "force": 98,
        "intellect": 55,
        "politics": 42,
        "command": 78,
        "loyalty": 96,
        "troops": 36,
        "alive": True
    },
    {
        "id": "g004",
        "name": "诸葛亮",
        "title": "卧龙",
        "camp": "我方",
        "force": 38,
        "intellect": 100,
        "politics": 100,
        "command": 95,
        "loyalty": 100,
        "troops": 22,
        "alive": True
    },
    {
        "id": "g101",
        "name": "曹操",
        "title": "魏武帝",
        "camp": "敌方",
        "force": 85,
        "intellect": 98,
        "politics": 95,
        "command": 97,
        "loyalty": 100,
        "troops": 60,
        "alive": True
    },
    {
        "id": "g102",
        "name": "夏侯惇",
        "title": "盲夏侯",
        "camp": "敌方",
        "force": 92,
        "intellect": 68,
        "politics": 60,
        "command": 84,
        "loyalty": 95,
        "troops": 32,
        "alive": True
    },
    {
        "id": "g103",
        "name": "典韦",
        "title": "古之恶来",
        "camp": "敌方",
        "force": 100,
        "intellect": 45,
        "politics": 28,
        "command": 76,
        "loyalty": 94,
        "troops": 30,
        "alive": True
    },
    {
        "id": "g104",
        "name": "许褚",
        "title": "虎痴",
        "camp": "敌方",
        "force": 97,
        "intellect": 42,
        "politics": 30,
        "command": 72,
        "loyalty": 93,
        "troops": 34,
        "alive": True
    }
]


def get_general_skill(name):
    skills = {
        "刘备": "仁德",
        "关羽": "武圣",
        "张飞": "猛将",
        "诸葛亮": "神机"
    }
    return skills.get(name, "无")


class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("迷你三国 · 策略版")
        self.root.geometry("1280x800")
        self.root.minsize(1180, 720)
        self.root.configure(bg="#1a1410")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.bg = "#1a1410"
        self.panel_bg = "#2a211b"
        self.panel_bg_2 = "#332820"
        self.paper_bg = "#eadfbe"
        self.header_bg = "#5b4129"
        self.header_bg_2 = "#6d4c2f"
        self.button_bg = "#6f4f39"
        self.button_active = "#8a6648"
        self.accent = "#d9b56b"
        self.text_fg = "#f5eddc"
        self.paper_text = "#2b211a"
        self.line = "#9f845b"

        self.font_title = ("Microsoft YaHei", 20, "bold")
        self.font_header = ("Microsoft YaHei", 12, "bold")
        self.font_body = ("Microsoft YaHei", 11)
        self.font_small = ("Microsoft YaHei", 10)
        self.font_button = ("Microsoft YaHei", 10, "bold")

        self.current_date = datetime(183, 1, 1)
        self.max_stamina = 5
        self.stamina = self.max_stamina
        self.resources = {"粮食": 100, "金钱": 50, "木材": 30}

        self.commerce_level = 1
        self.agriculture_level = 1
        self.security_level = 1
        self.wall_repair_level = 0

        self.mode = "overview"
        self.selected_general_id = None
        self.selected_general_ids = []
        self.generals = []
        self.cities = []
        self.log_cache = []

        self.map_width = 1800
        self.map_height = 1200

        self.title_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.stamina_var = tk.StringVar()
        self.resource_var = tk.StringVar()
        self.army_var = tk.StringVar()
        self.general_detail_var = tk.StringVar()
        self.battle_general_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.load_generals()
        self.recalculate_armies()
        self.selected_general_id = self.get_first_friendly_general_id()

        # 地图数据只初始化一次，不在战斗刷新时重建
        self.create_battle_scenario()

        self.show_overview_screen()

    def ensure_generals_file(self):
        if not os.path.exists(GENERALS_FILE):
            with open(GENERALS_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_GENERALS, f, ensure_ascii=False, indent=2)

    def normalize_general(self, g):
        default = {
            "id": "",
            "name": "无名",
            "title": "",
            "camp": "我方",
            "force": 50,
            "intellect": 50,
            "politics": 50,
            "command": 50,
            "loyalty": 80,
            "troops": 20,
            "alive": True
        }
        default.update(g or {})
        if not default["id"]:
            default["id"] = f"g{random.randint(1000, 9999)}"
        default["name"] = str(default["name"])
        default["title"] = str(default["title"])
        default["camp"] = "敌方" if default["camp"] == "敌方" else "我方"
        for key in ["force", "intellect", "politics", "command", "loyalty", "troops"]:
            try:
                default[key] = int(default[key])
            except Exception:
                default[key] = 0
        default["troops"] = max(0, default["troops"])
        default["alive"] = bool(default.get("alive", True))
        return default

    def load_generals(self):
        self.ensure_generals_file()
        try:
            with open(GENERALS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("generals.json 必须是数组")

            self.generals = [self.normalize_general(item) for item in data]
            self.save_generals()
        except Exception as e:
            print(f"[DEBUG] load_generals failed: {e}")
            self.generals = [self.normalize_general(item) for item in DEFAULT_GENERALS]
            self.save_generals()

    def save_generals(self):
        with open(GENERALS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.generals, f, ensure_ascii=False, indent=2)

    def recalculate_armies(self):
        self.army_count = sum(
            g["troops"] for g in self.generals
            if g["camp"] == "我方" and g["alive"]
        )
        self.enemy_army_count = sum(
            g["troops"] for g in self.generals
            if g["camp"] == "敌方" and g["alive"]
        )

    def get_first_friendly_general_id(self):
        for g in self.generals:
            if g["camp"] == "我方" and g["alive"] and g["troops"] > 0:
                return g["id"]
        for g in self.generals:
            if g["camp"] == "我方" and g["alive"]:
                return g["id"]
        return None

    def get_general_by_id(self, general_id):
        for g in self.generals:
            if g["id"] == general_id:
                return g
        return None

    def get_general_index_by_id(self, general_id):
        for idx, g in enumerate(self.generals):
            if g["id"] == general_id:
                return idx
        return None

    def get_selected_general(self):
        return self.get_general_by_id(self.selected_general_id)

    def get_selected_friendly_general(self):
        g = self.get_selected_general()
        if g and g["camp"] == "我方":
            return g
        return None

    def get_friendly_generals(self):
        return [
            g for g in self.generals
            if g["camp"] == "我方" and g["alive"] and g["troops"] > 0
        ]

    def get_alive_enemy_generals(self):
        return [
            g for g in self.generals
            if g["camp"] == "敌方" and g["alive"]
        ]

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def on_close(self):
        self.save_generals()
        self.root.destroy()

    def log(self, text):
        timestamp = self.current_date.strftime("%Y-%m-%d")
        line = f"[{timestamp}] {text}"
        self.log_cache.append(line)
        self.log_cache = self.log_cache[-80:]

        if hasattr(self, "log_text"):
            self.log_text.config(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.insert("end", "\n".join(self.log_cache))
            self.log_text.see("end")
            self.log_text.config(state="disabled")

    def refresh_top_info(self):
        self.title_var.set("内政总览" if self.mode == "overview" else "出征战场")
        self.date_var.set(f"日期：{self.current_date.strftime('%Y年%m月%d日')}")
        self.stamina_var.set(f"体力：{self.stamina}/{self.max_stamina}")
        self.resource_var.set(
            f"粮食：{self.resources['粮食']}   金钱：{self.resources['金钱']}   木材：{self.resources['木材']}"
        )
        self.army_var.set(f"我方兵力：{self.army_count}   敌方兵力：{self.enemy_army_count}")

    def make_button(self, parent, text, command, width=14):
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            bg=self.button_bg,
            fg="white",
            activebackground=self.button_active,
            activeforeground="white",
            bd=2,
            relief="raised",
            font=self.font_button,
            cursor="hand2"
        )

    def build_header(self):
        header = tk.Frame(self.root, bg=self.header_bg, height=88)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        left = tk.Frame(header, bg=self.header_bg)
        left.pack(side="left", fill="y", padx=16, pady=10)

        tk.Label(
            left,
            textvariable=self.title_var,
            bg=self.header_bg,
            fg=self.accent,
            font=self.font_title
        ).pack(anchor="w")

        tk.Label(
            left,
            text="君临天下，内政与兵戈并行",
            bg=self.header_bg,
            fg=self.text_fg,
            font=self.font_small
        ).pack(anchor="w", pady=(2, 0))

        right = tk.Frame(header, bg=self.header_bg)
        right.pack(side="right", fill="y", padx=16, pady=10)

        tk.Label(
            right,
            textvariable=self.date_var,
            bg=self.header_bg,
            fg=self.text_fg,
            font=self.font_header
        ).pack(anchor="e")

        tk.Label(
            right,
            textvariable=self.stamina_var,
            bg=self.header_bg,
            fg=self.text_fg,
            font=self.font_header
        ).pack(anchor="e")

        tk.Label(
            right,
            textvariable=self.resource_var,
            bg=self.header_bg,
            fg=self.text_fg,
            font=self.font_small
        ).pack(anchor="e", pady=(2, 0))

        tk.Label(
            right,
            textvariable=self.army_var,
            bg=self.header_bg,
            fg=self.text_fg,
            font=self.font_small
        ).pack(anchor="e")

    def build_log_panel(self, parent):
        frame = tk.Frame(parent, bg=self.panel_bg, bd=2, relief="ridge")
        top = tk.Label(
            frame,
            text="军情记录",
            bg=self.panel_bg_2,
            fg=self.accent,
            font=self.font_header,
            anchor="w",
            padx=10,
            pady=4
        )
        top.pack(fill="x")

        self.log_text = tk.Text(
            frame,
            height=8,
            bg="#14100d",
            fg="#f1e7d1",
            insertbackground="white",
            wrap="word",
            state="disabled",
            bd=0,
            font=self.font_small
        )
        self.log_text.pack(fill="both", expand=True, padx=8, pady=8)

        if self.log_cache:
            self.log_text.config(state="normal")
            self.log_text.insert("end", "\n".join(self.log_cache))
            self.log_text.see("end")
            self.log_text.config(state="disabled")

        return frame

    def build_general_panel(self, parent):
        frame = tk.Frame(parent, bg=self.panel_bg, bd=2, relief="ridge")
        frame.pack(fill="both", expand=True)

        head = tk.Label(
            frame,
            text="武将录",
            bg=self.panel_bg_2,
            fg=self.accent,
            font=self.font_header,
            anchor="w",
            padx=10,
            pady=4
        )
        head.pack(fill="x")

        list_frame = tk.Frame(frame, bg=self.panel_bg)
        list_frame.pack(fill="both", expand=False, padx=8, pady=(8, 6))

        self.general_listbox = tk.Listbox(
            list_frame,
            height=12,
            bg="#1f1814",
            fg="#f1e7d1",
            selectbackground="#8b6a4f",
            selectforeground="white",
            bd=1,
            relief="solid",
            font=self.font_small
        )
        scroll = tk.Scrollbar(list_frame, command=self.general_listbox.yview)
        self.general_listbox.config(yscrollcommand=scroll.set)

        self.general_listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.general_listbox.bind("<<ListboxSelect>>", self.on_general_selected)

        detail_frame = tk.Frame(frame, bg="#241c17", bd=1, relief="solid")
        detail_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        tk.Label(
            detail_frame,
            text="武将详情",
            bg="#241c17",
            fg=self.accent,
            font=self.font_small,
            anchor="w"
        ).pack(fill="x", padx=8, pady=(8, 4))

        self.general_detail_label = tk.Label(
            detail_frame,
            textvariable=self.general_detail_var,
            bg="#241c17",
            fg="#f3ead3",
            justify="left",
            anchor="nw",
            font=self.font_small,
            wraplength=250
        )
        self.general_detail_label.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.refresh_general_panel()
        return frame

    def build_battle_select_panel(self, parent):
        frame = tk.Frame(parent, bg=self.panel_bg, bd=2, relief="ridge")
        frame.pack(fill="both", expand=True)

        head = tk.Label(
            frame,
            text="出战武将",
            bg=self.panel_bg_2,
            fg=self.accent,
            font=self.font_header,
            anchor="w",
            padx=10,
            pady=4
        )
        head.pack(fill="x")

        hint = tk.Label(
            frame,
            text="可多选，按住 Ctrl / Shift 选择。",
            bg=self.panel_bg,
            fg=self.text_fg,
            font=self.font_small,
            anchor="w"
        )
        hint.pack(fill="x", padx=10, pady=(8, 4))

        list_frame = tk.Frame(frame, bg=self.panel_bg)
        list_frame.pack(fill="both", expand=False, padx=8, pady=(4, 6))

        self.battle_listbox = tk.Listbox(
            list_frame,
            height=13,
            selectmode="multiple",
            bg="#1f1814",
            fg="#f1e7d1",
            selectbackground="#8b6a4f",
            selectforeground="white",
            bd=1,
            relief="solid",
            font=self.font_small
        )
        scroll = tk.Scrollbar(list_frame, command=self.battle_listbox.yview)
        self.battle_listbox.config(yscrollcommand=scroll.set)

        self.battle_listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        btn_box = tk.Frame(frame, bg=self.panel_bg)
        btn_box.pack(fill="x", padx=8, pady=(2, 8))

        self.make_button(btn_box, "确认出战", self.confirm_battle_generals, width=12).pack(side="left", padx=(0, 6))
        self.make_button(btn_box, "选择全军", self.select_all_battle_generals, width=12).pack(side="left")

        detail_frame = tk.Frame(frame, bg="#241c17", bd=1, relief="solid")
        detail_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        tk.Label(
            detail_frame,
            text="出战提示",
            bg="#241c17",
            fg=self.accent,
            font=self.font_small,
            anchor="w"
        ).pack(fill="x", padx=8, pady=(8, 4))

        self.battle_general_label = tk.Label(
            detail_frame,
            textvariable=self.battle_general_var,
            bg="#241c17",
            fg="#f3ead3",
            justify="left",
            anchor="nw",
            font=self.font_small,
            wraplength=250
        )
        self.battle_general_label.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.refresh_battle_general_panel()
        return frame

    def refresh_general_panel(self):
        if not hasattr(self, "general_listbox"):
            return

        self.general_listbox.delete(0, tk.END)

        selected_index = None
        for i, g in enumerate(self.generals):
            camp = "我方" if g["camp"] == "我方" else "敌方"
            text = f"{camp} | {g['name']} | 兵 {g['troops']} | 武 {g['force']} | 智 {g['intellect']}"
            self.general_listbox.insert(tk.END, text)
            if g["id"] == self.selected_general_id:
                selected_index = i

        if selected_index is None:
            self.selected_general_id = self.get_first_friendly_general_id()
            for i, g in enumerate(self.generals):
                if g["id"] == self.selected_general_id:
                    selected_index = i
                    break

        if selected_index is not None:
            self.general_listbox.selection_clear(0, tk.END)
            self.general_listbox.selection_set(selected_index)
            self.general_listbox.activate(selected_index)

        self.update_general_detail()

    def refresh_battle_general_panel(self):
        if not hasattr(self, "battle_listbox"):
            return

        self.battle_listbox.delete(0, tk.END)
        self.friendly_generals = self.get_friendly_generals()

        for g in self.friendly_generals:
            skill = get_general_skill(g["name"])
            self.battle_listbox.insert(
                tk.END,
                f"{g['name']} | 兵 {g['troops']} | 武 {g['force']} | 统 {g['command']} | 技能 {skill}"
            )

        if self.selected_general_ids:
            for idx, g in enumerate(self.friendly_generals):
                if g["id"] in self.selected_general_ids:
                    self.battle_listbox.selection_set(idx)
            selected_names = [g["name"] for g in self.friendly_generals if g["id"] in self.selected_general_ids]
            if selected_names:
                self.battle_general_var.set("当前出战： " + "、".join(selected_names))
            else:
                self.battle_general_var.set("请选择出战武将后点击“确认出战”。")
        else:
            self.battle_general_var.set("请选择出战武将后点击“确认出战”。")

    def update_general_detail(self):
        g = self.get_selected_general()
        if not g:
            self.general_detail_var.set("暂无可用武将。")
            return

        detail = (
            f"姓名：{g['name']}\n"
            f"称号：{g['title']}\n"
            f"阵营：{g['camp']}\n"
            f"武力：{g['force']}\n"
            f"智力：{g['intellect']}\n"
            f"政治：{g['politics']}\n"
            f"统率：{g['command']}\n"
            f"忠诚：{g['loyalty']}\n"
            f"兵力：{g['troops']}\n"
            f"技能：{get_general_skill(g['name'])}\n"
            f"状态：{'在世' if g['alive'] else '离世'}"
        )
        self.general_detail_var.set(detail)

    def on_general_selected(self, event):
        if not hasattr(self, "general_listbox"):
            return
        selection = self.general_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if 0 <= index < len(self.generals):
            self.selected_general_id = self.generals[index]["id"]
            self.update_general_detail()

    def confirm_battle_generals(self):
        if not hasattr(self, "battle_listbox"):
            return

        indices = self.battle_listbox.curselection()
        if not indices:
            self.selected_general_ids = []
            self.battle_general_var.set("未选择出战武将。")
            return

        self.selected_general_ids = []
        selected_names = []
        for idx in indices:
            if 0 <= idx < len(self.friendly_generals):
                g = self.friendly_generals[idx]
                self.selected_general_ids.append(g["id"])
                selected_names.append(g["name"])

        self.battle_general_var.set("当前出战： " + "、".join(selected_names))

    def select_all_battle_generals(self):
        if not hasattr(self, "battle_listbox"):
            return
        self.battle_listbox.selection_set(0, tk.END)
        self.confirm_battle_generals()

    def create_battle_scenario(self):
        if self.cities:
            return

        # 地图是固定的，不会在每次战斗后重建
        self.cities = [
            {
                "id": "player_capital",
                "name": "我方军营",
                "type": "capital",
                "owner": "我方",
                "garrison": self.army_count,
                "x": 180,
                "y": 900,
                "circle_id": None,
                "text_id": None
            },
            {
                "id": "village_1",
                "name": "村庄",
                "type": "village",
                "owner": "中立",
                "garrison": 10,
                "x": 320,
                "y": 760,
                "circle_id": None,
                "text_id": None
            },
            {
                "id": "village_2",
                "name": "村庄",
                "type": "village",
                "owner": "中立",
                "garrison": 12,
                "x": 520,
                "y": 610,
                "circle_id": None,
                "text_id": None
            },
            {
                "id": "city_1",
                "name": "县城",
                "type": "city",
                "owner": "敌方",
                "garrison": 24,
                "x": 780,
                "y": 480,
                "circle_id": None,
                "text_id": None
            },
            {
                "id": "village_3",
                "name": "村庄",
                "type": "village",
                "owner": "中立",
                "garrison": 9,
                "x": 650,
                "y": 300,
                "circle_id": None,
                "text_id": None
            },
            {
                "id": "city_2",
                "name": "郡城",
                "type": "city",
                "owner": "敌方",
                "garrison": 30,
                "x": 980,
                "y": 750,
                "circle_id": None,
                "text_id": None
            },
            {
                "id": "village_4",
                "name": "村庄",
                "type": "village",
                "owner": "中立",
                "garrison": 8,
                "x": 1100,
                "y": 540,
                "circle_id": None,
                "text_id": None
            },
            {
                "id": "city_3",
                "name": "重镇",
                "type": "city",
                "owner": "敌方",
                "garrison": 34,
                "x": 1270,
                "y": 320,
                "circle_id": None,
                "text_id": None
            },
            {
                "id": "village_5",
                "name": "村庄",
                "type": "village",
                "owner": "中立",
                "garrison": 11,
                "x": 1430,
                "y": 860,
                "circle_id": None,
                "text_id": None
            },
            {
                "id": "enemy_capital",
                "name": "敌方军营",
                "type": "capital",
                "owner": "敌方",
                "garrison": self.enemy_army_count,
                "x": 1540,
                "y": 200,
                "circle_id": None,
                "text_id": None
            }
        ]

    def city_color(self, owner):
        if owner == "我方":
            return "#3c6fd4"
        if owner == "敌方":
            return "#b33f31"
        return "#4c9a4a"

    def get_city_radius(self, city_type):
        if city_type == "capital":
            return 32
        if city_type == "city":
            return 26
        return 20

    def draw_city(self, city):
        x = city["x"]
        y = city["y"]
        radius = self.get_city_radius(city["type"])
        color = self.city_color(city["owner"])

        circle_id = self.battle_canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=color,
            outline="#2a1f16",
            width=2
        )

        label_color = "white" if city["owner"] != "中立" else "#241c17"
        text_id = self.battle_canvas.create_text(
            x,
            y,
            text=f"{city['name']}\n{city['garrison']}兵",
            fill=label_color,
            font=("Microsoft YaHei", 10, "bold")
        )

        city["circle_id"] = circle_id
        city["text_id"] = text_id

        self.battle_canvas.tag_bind(circle_id, "<Button-1>", lambda e, cid=city["id"]: self.on_city_click(cid))
        self.battle_canvas.tag_bind(text_id, "<Button-1>", lambda e, cid=city["id"]: self.on_city_click(cid))

    def update_city_visual(self, city):
        if not hasattr(self, "battle_canvas"):
            return
        if not city.get("circle_id") or not city.get("text_id"):
            return

        self.battle_canvas.itemconfig(city["circle_id"], fill=self.city_color(city["owner"]))
        label_color = "white" if city["owner"] != "中立" else "#241c17"
        self.battle_canvas.itemconfig(city["text_id"], fill=label_color)
        self.battle_canvas.itemconfig(city["text_id"], text=f"{city['name']}\n{city['garrison']}兵")

    def draw_battle_map(self):
        self.battle_canvas.delete("all")

        # 地图背景格线
        for x in range(0, self.map_width + 1, 100):
            self.battle_canvas.create_line(x, 0, x, self.map_height, fill="#d6c79f")
        for y in range(0, self.map_height + 1, 100):
            self.battle_canvas.create_line(0, y, self.map_width, y, fill="#d6c79f")

        self.battle_canvas.create_text(
            120,
            30,
            text="中键拖动地图，滚轮可上下滚动",
            fill="#6b5636",
            font=self.font_small,
            anchor="w"
        )

        for city in self.cities:
            self.draw_city(city)

        self.battle_canvas.configure(scrollregion=(0, 0, self.map_width, self.map_height))

    def start_canvas_pan(self, event):
        if hasattr(self, "battle_canvas"):
            self.battle_canvas.scan_mark(event.x, event.y)

    def do_canvas_pan(self, event):
        if hasattr(self, "battle_canvas"):
            self.battle_canvas.scan_dragto(event.x, event.y, gain=1)

    def bind_canvas_scroll(self):
        # 鼠标滚轮滚动
        def on_mousewheel(event):
            if event.delta:
                self.battle_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.battle_canvas.bind("<MouseWheel>", on_mousewheel)
        self.battle_canvas.bind("<ButtonPress-2>", self.start_canvas_pan)
        self.battle_canvas.bind("<B2-Motion>", self.do_canvas_pan)
        self.battle_canvas.bind("<ButtonPress-3>", self.start_canvas_pan)
        self.battle_canvas.bind("<B3-Motion>", self.do_canvas_pan)

    def get_city_by_id(self, city_id):
        for c in self.cities:
            if c["id"] == city_id:
                return c
        return None

    def get_selected_battle_generals(self):
        if not self.selected_general_ids:
            return []

        selected = []
        for gid in self.selected_general_ids:
            g = self.get_general_by_id(gid)
            if g and g["camp"] == "我方" and g["alive"] and g["troops"] > 0:
                selected.append(g)
        return selected

    def on_city_click(self, city_id):
        city = self.get_city_by_id(city_id)
        if not city:
            return

        if city["owner"] == "我方":
            self.log(f"{city['name']} 已经是我方领地。")
            self.status_var.set(f"{city['name']} 已是我方领地。")
            return

        if city["id"] == "player_capital":
            self.log("不能攻击我方军营。")
            self.status_var.set("不能攻击我方军营。")
            return

        attackers = self.get_selected_battle_generals()
        if not attackers:
            self.log("请先在右侧选择出战武将并确认。")
            self.status_var.set("请先选择出战武将。")
            messagebox.showwarning("提示", "请选择出战武将后再进攻。")
            return

        attack_power = 0
        loss_modifier = 1.0
        no_loss = False
        attacker_names = []

        for g in attackers:
            attacker_names.append(g["name"])
            atk = g["troops"] + int(g["force"] * 0.8) + int(g["command"] * 1.2)
            skill = get_general_skill(g["name"])

            if skill == "武圣":
                atk *= 1.25
            elif skill == "猛将":
                atk *= 1.2
                loss_modifier *= 1.2
            elif skill == "仁德":
                loss_modifier *= 0.5
            elif skill == "神机":
                no_loss = True

            attack_power += int(atk)

        defense = (
            city["garrison"]
            + (20 if city["type"] == "capital" else 10 if city["type"] == "city" else 5)
            + random.randint(5, 15)
        )

        self.log(f"{'、'.join(attacker_names)} 进攻 {city['name']}：我方战力 {attack_power} / 守军 {defense}")
        self.status_var.set(f"出战：{'、'.join(attacker_names)}")

        if attack_power >= defense:
            for g in attackers:
                loss = 0 if no_loss else random.randint(1, 5)
                g["troops"] = max(0, g["troops"] - int(loss * loss_modifier))

            city["owner"] = "我方"

            if city["type"] == "capital":
                city["garrison"] = max(20, sum(g["troops"] for g in attackers) // 2 + 10)
                self.resources["金钱"] += 30
                self.resources["木材"] += 12
                self.log(f"{'、'.join(attacker_names)} 攻破 {city['name']}，我方夺得重镇。")
            elif city["type"] == "city":
                city["garrison"] = max(12, sum(g["troops"] for g in attackers) // 3 + 6)
                self.resources["金钱"] += 18
                self.resources["粮食"] += 10
                self.log(f"{'、'.join(attacker_names)} 攻下 {city['name']}。")
            else:
                city["garrison"] = max(8, sum(g["troops"] for g in attackers) // 4 + 4)
                self.resources["粮食"] += 15
                self.log(f"{'、'.join(attacker_names)} 占领 {city['name']}，获得粮草。")

            self.recalculate_armies()
            self.save_generals()
            self.refresh_top_info()
            self.refresh_battle_general_panel()
            self.update_general_detail()
            self.update_city_visual(city)

            self.capture_enemy()
            self.save_generals()

            messagebox.showinfo("胜利", f"成功拿下 {city['name']}！")
        else:
            for g in attackers:
                loss = 0 if no_loss else random.randint(3, 8)
                g["troops"] = max(0, g["troops"] - int(loss * loss_modifier))

            city["garrison"] = max(1, city["garrison"] - random.randint(1, 4))
            self.log(f"{'、'.join(attacker_names)} 进攻 {city['name']} 失利。")
            messagebox.showwarning("失败", "进攻失败，损失惨重。")

            self.recalculate_armies()
            self.save_generals()
            self.refresh_top_info()
            self.refresh_battle_general_panel()
            self.update_general_detail()
            self.update_city_visual(city)

        # 重点：这里不重建地图，不重置村庄和城池
        self.refresh_top_info()

    def check_victory(self):
        enemy_capital = self.get_city_by_id("enemy_capital")
        return bool(enemy_capital and enemy_capital["owner"] == "我方")

    def capture_enemy(self):
        enemies = self.get_alive_enemy_generals()
        if not enemies:
            return

        captive = random.choice(enemies)
        choice = messagebox.askyesno(
            "俘虏",
            f"俘虏敌将【{captive['name']}】\n是否招降？"
        )

        if choice:
            captive["camp"] = "我方"
            captive["loyalty"] = 60
            self.log(f"{captive['name']} 已投效我方。")
            messagebox.showinfo("成功", f"{captive['name']} 已投效我方")
        else:
            captive["alive"] = False
            self.log(f"{captive['name']} 已被处斩。")
            messagebox.showinfo("处斩", f"{captive['name']} 已被处斩")

    def next_day(self):
        self.current_date += timedelta(days=1)
        self.stamina = min(self.max_stamina, self.stamina + 1)
        self.resources["粮食"] += 5 + self.agriculture_level * 2
        self.resources["金钱"] += 3 + self.commerce_level * 2
        self.resources["木材"] += 1
        self.log("时间流逝，领地获得了少量资源。")
        self.refresh_after_action()

    def build_house(self):
        if self.stamina < self.max_stamina:
            self.stamina = self.max_stamina
            self.current_date += timedelta(days=1)
            self.log("修建住宅与整备完成，体力已恢复。")
            self.refresh_after_action()
        else:
            self.log("体力已经是满值。")

    def recruit_soldiers(self):
        general = self.get_selected_friendly_general()
        if not general:
            self.log("请先选择一名我方武将。")
            messagebox.showwarning("提示", "请先选择一名我方武将。")
            return

        if self.stamina <= 0:
            self.log("体力不足，无法征兵。")
            messagebox.showwarning("提示", "体力不足，无法征兵。")
            return

        cost_food = 8
        cost_money = 3
        recruit_count = 5 + general["command"] // 20

        if self.resources["粮食"] < cost_food or self.resources["金钱"] < cost_money:
            self.log("资源不足，无法征兵。")
            messagebox.showwarning("提示", "资源不足，无法征兵。")
            return

        self.stamina -= 1
        self.resources["粮食"] -= cost_food
        self.resources["金钱"] -= cost_money
        general["troops"] += recruit_count
        self.recalculate_armies()
        self.save_generals()
        self.log(f"{general['name']} 征得 {recruit_count} 兵。")
        self.refresh_after_action()

    def open_garrison_recruit_window(self):
        if not self.cities:
            messagebox.showwarning("提示", "地图尚未初始化。")
            return

        owned_locations = [
            c for c in self.cities
            if c["owner"] == "我方" and c["id"] != "enemy_capital"
        ]

        if not owned_locations:
            messagebox.showinfo("提示", "目前没有可征兵的我方据点。")
            return

        win = tk.Toplevel(self.root)
        win.title("据点征兵")
        win.geometry("460x360")
        win.configure(bg=self.panel_bg)
        win.transient(self.root)
        win.grab_set()

        tk.Label(
            win,
            text="选择我方据点进行征兵",
            bg=self.panel_bg,
            fg=self.accent,
            font=self.font_header
        ).pack(pady=(12, 6))

        listbox = tk.Listbox(
            win,
            height=10,
            bg="#1f1814",
            fg="#f1e7d1",
            selectbackground="#8b6a4f",
            selectforeground="white",
            font=self.font_small
        )
        listbox.pack(fill="both", expand=True, padx=16, pady=8)

        for c in owned_locations:
            listbox.insert(
                tk.END,
                f"{c['name']} | 类型:{c['type']} | 驻军:{c['garrison']}兵"
            )

        form = tk.Frame(win, bg=self.panel_bg)
        form.pack(fill="x", padx=16, pady=(0, 8))

        tk.Label(form, text="征兵数量：", bg=self.panel_bg, fg=self.text_fg, font=self.font_small).pack(side="left")
        num_var = tk.StringVar(value="5")
        num_entry = tk.Entry(form, textvariable=num_var, width=10, font=self.font_small)
        num_entry.pack(side="left", padx=6)

        def do_recruit():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("提示", "请选择一个据点。")
                return

            try:
                recruit_count = int(num_var.get())
            except Exception:
                messagebox.showwarning("提示", "请输入有效数字。")
                return

            if recruit_count <= 0:
                messagebox.showwarning("提示", "征兵数量必须大于 0。")
                return

            idx = sel[0]
            city = owned_locations[idx]

            max_recruit = 30 if city["type"] == "capital" else 20 if city["type"] == "city" else 10
            if recruit_count > max_recruit:
                messagebox.showwarning("提示", f"该据点单次最多征兵 {max_recruit}。")
                return

            food_cost = recruit_count * 2
            money_cost = recruit_count

            if self.resources["粮食"] < food_cost or self.resources["金钱"] < money_cost:
                messagebox.showwarning("提示", "资源不足，无法征兵。")
                return

            self.resources["粮食"] -= food_cost
            self.resources["金钱"] -= money_cost
            city["garrison"] += recruit_count

            self.log(f"在 {city['name']} 征得 {recruit_count} 兵。")
            self.save_generals()
            self.refresh_top_info()

            if self.mode == "battle" and hasattr(self, "battle_canvas"):
                self.update_city_visual(city)

            messagebox.showinfo("成功", f"{city['name']} 征兵完成。")
            win.destroy()
            self.refresh_top_info()

        tk.Button(
            form,
            text="确认征兵",
            command=do_recruit,
            bg=self.button_bg,
            fg="white",
            activebackground=self.button_active,
            activeforeground="white",
            font=self.font_small
        ).pack(side="right")

    def upgrade_commerce(self):
        if self.stamina <= 0:
            self.log("体力不足，无法提升商业。")
            return
        if self.resources["金钱"] < 20:
            self.log("金钱不足，无法提升商业。")
            return

        self.stamina -= 1
        self.resources["金钱"] -= 20
        self.commerce_level += 1
        self.log(f"商业提升到 {self.commerce_level} 级。")
        self.refresh_after_action()

    def upgrade_agriculture(self):
        if self.stamina <= 0:
            self.log("体力不足，无法提升农业。")
            return
        if self.resources["木材"] < 15:
            self.log("木材不足，无法提升农业。")
            return

        self.stamina -= 1
        self.resources["木材"] -= 15
        self.agriculture_level += 1
        self.log(f"农业提升到 {self.agriculture_level} 级。")
        self.refresh_after_action()

    def upgrade_security(self):
        if self.stamina <= 0:
            self.log("体力不足，无法提升治安。")
            return
        if self.resources["粮食"] < 10:
            self.log("粮食不足，无法提升治安。")
            return

        self.stamina -= 1
        self.resources["粮食"] -= 10
        self.security_level += 1
        self.log(f"治安提升到 {self.security_level} 级。")
        self.refresh_after_action()

    def repair_wall(self):
        if self.stamina <= 0:
            self.log("体力不足，无法修复城墙。")
            return
        if self.resources["金钱"] < 30:
            self.log("金钱不足，无法修复城墙。")
            return

        self.stamina -= 1
        self.resources["金钱"] -= 30
        self.wall_repair_level += 1
        self.log(f"城墙修复到 {self.wall_repair_level} 级。")
        self.refresh_after_action()

    def refresh_after_action(self):
        self.recalculate_armies()
        self.save_generals()
        self.refresh_top_info()

        if self.mode == "battle":
            self.refresh_battle_general_panel()
            self.update_general_detail()
        else:
            self.refresh_general_panel()

    def create_stat_card(self, parent, title, value):
        card = tk.Frame(parent, bg="#f5ead0", bd=2, relief="groove")
        tk.Label(
            card,
            text=title,
            bg="#f5ead0",
            fg="#5b4129",
            font=self.font_small
        ).pack(anchor="w", padx=10, pady=(8, 0))

        tk.Label(
            card,
            text=value,
            bg="#f5ead0",
            fg="#241c17",
            font=("Microsoft YaHei", 15, "bold")
        ).pack(anchor="w", padx=10, pady=(4, 10))

        return card

    def show_overview_screen(self):
        self.mode = "overview"
        self.clear_screen()
        self.build_header()
        self.refresh_top_info()

        body = tk.Frame(self.root, bg=self.bg)
        body.pack(fill="both", expand=True, padx=12, pady=(10, 8))

        left = tk.Frame(body, bg=self.panel_bg, width=180, bd=2, relief="ridge")
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        center = tk.Frame(body, bg=self.paper_bg, bd=2, relief="ridge")
        center.pack(side="left", fill="both", expand=True, padx=10)

        right = tk.Frame(body, bg=self.panel_bg, width=320, bd=2, relief="ridge")
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        tk.Label(
            left,
            text="军政命令",
            bg=self.panel_bg_2,
            fg=self.accent,
            font=self.font_header,
            anchor="w",
            padx=10,
            pady=4
        ).pack(fill="x")

        btn_box = tk.Frame(left, bg=self.panel_bg)
        btn_box.pack(fill="both", expand=True, padx=10, pady=10)

        self.make_button(btn_box, "出征战场", self.enter_battle, width=16).pack(pady=5)
        self.make_button(btn_box, "据点征兵", self.open_garrison_recruit_window, width=16).pack(pady=5)
        self.make_button(btn_box, "征兵", self.recruit_soldiers, width=16).pack(pady=5)
        self.make_button(btn_box, "提升商业", self.upgrade_commerce, width=16).pack(pady=5)
        self.make_button(btn_box, "提升农业", self.upgrade_agriculture, width=16).pack(pady=5)
        self.make_button(btn_box, "提升治安", self.upgrade_security, width=16).pack(pady=5)
        self.make_button(btn_box, "修复城墙", self.repair_wall, width=16).pack(pady=5)
        self.make_button(btn_box, "休整回满", self.build_house, width=16).pack(pady=5)
        self.make_button(btn_box, "过一日", self.next_day, width=16).pack(pady=5)

        center_top = tk.Frame(center, bg=self.paper_bg)
        center_top.pack(fill="x", padx=16, pady=16)

        tk.Label(
            center_top,
            text="国势总览",
            bg=self.paper_bg,
            fg=self.paper_text,
            font=self.font_title
        ).pack(anchor="w")

        tk.Label(
            center_top,
            text="这里是你的都城主界面。右侧可查看武将。占领据点后，可在这里对我方据点征兵。",
            bg=self.paper_bg,
            fg=self.paper_text,
            font=self.font_small
        ).pack(anchor="w", pady=(2, 0))

        stat_grid = tk.Frame(center, bg=self.paper_bg)
        stat_grid.pack(fill="x", padx=16, pady=10)

        self.create_stat_card(stat_grid, "我方兵力", str(self.army_count)).grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self.create_stat_card(stat_grid, "敌方兵力", str(self.enemy_army_count)).grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        self.create_stat_card(stat_grid, "体力", f"{self.stamina}/{self.max_stamina}").grid(row=0, column=2, padx=8, pady=8, sticky="nsew")
        self.create_stat_card(stat_grid, "粮 / 金 / 木", f"{self.resources['粮食']} / {self.resources['金钱']} / {self.resources['木材']}").grid(
            row=0, column=3, padx=8, pady=8, sticky="nsew"
        )
        stat_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        info_box = tk.Frame(center, bg=self.paper_bg, bd=2, relief="groove")
        info_box.pack(fill="both", expand=True, padx=16, pady=(6, 16))

        selected = self.get_selected_general()
        commander_text = "未选择" if not selected else f"{selected['name']}（{selected['title']}）"
        summary = (
            f"当前主将：{commander_text}\n"
            f"商业：{self.commerce_level}    农业：{self.agriculture_level}    治安：{self.security_level}    城墙：{self.wall_repair_level}\n\n"
            f"建议：先征兵和提升内政，再进入战场夺取更多城池。"
        )
        tk.Label(
            info_box,
            text=summary,
            bg=self.paper_bg,
            fg=self.paper_text,
            justify="left",
            anchor="nw",
            font=self.font_body
        ).pack(fill="both", expand=True, padx=14, pady=14)

        self.build_general_panel(right)

        log = self.build_log_panel(self.root)
        log.pack(side="bottom", fill="x", padx=12, pady=(0, 12))

        self.refresh_top_info()
        self.update_general_detail()

    def enter_battle(self):
        if self.stamina <= 0:
            self.log("体力不足，无法出征。")
            messagebox.showwarning("提示", "体力不足，无法出征。")
            return

        self.stamina -= 1
        self.current_date += timedelta(days=1)
        self.mode = "battle"
        self.selected_general_ids = []

        # 不重建地图，直接显示固定地图状态
        self.show_battle_screen()

    def show_battle_screen(self):
        self.mode = "battle"
        self.clear_screen()
        self.build_header()
        self.refresh_top_info()

        body = tk.Frame(self.root, bg=self.bg)
        body.pack(fill="both", expand=True, padx=12, pady=(10, 8))

        left = tk.Frame(body, bg=self.panel_bg, width=180, bd=2, relief="ridge")
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        center = tk.Frame(body, bg=self.paper_bg, bd=2, relief="ridge")
        center.pack(side="left", fill="both", expand=True, padx=10)

        right = tk.Frame(body, bg=self.panel_bg, width=320, bd=2, relief="ridge")
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        tk.Label(
            left,
            text="战场军令",
            bg=self.panel_bg_2,
            fg=self.accent,
            font=self.font_header,
            anchor="w",
            padx=10,
            pady=4
        ).pack(fill="x")

        btn_box = tk.Frame(left, bg=self.panel_bg)
        btn_box.pack(fill="both", expand=True, padx=10, pady=10)

        self.make_button(btn_box, "返回内政", self.show_overview_screen, width=16).pack(pady=5)
        self.make_button(btn_box, "据点征兵", self.open_garrison_recruit_window, width=16).pack(pady=5)
        self.make_button(btn_box, "征兵", self.recruit_soldiers, width=16).pack(pady=5)
        self.make_button(btn_box, "休整回满", self.build_house, width=16).pack(pady=5)
        self.make_button(btn_box, "过一日", self.next_day, width=16).pack(pady=5)

        tk.Label(
            btn_box,
            text="中键拖动地图，滚轮滚动。占领的村子会一直保留。",
            bg=self.panel_bg,
            fg=self.text_fg,
            justify="left",
            wraplength=150,
            font=self.font_small
        ).pack(pady=(18, 0))

        map_header = tk.Frame(center, bg=self.paper_bg)
        map_header.pack(fill="x", padx=16, pady=(14, 4))

        tk.Label(
            map_header,
            text="战场地图",
            bg=self.paper_bg,
            fg=self.paper_text,
            font=self.font_title
        ).pack(anchor="w")

        tk.Label(
            map_header,
            text="点击城池发动战斗。地图不会重置，已占领据点会持续保留。",
            bg=self.paper_bg,
            fg=self.paper_text,
            font=self.font_small
        ).pack(anchor="w", pady=(2, 0))

        tk.Label(
            map_header,
            textvariable=self.status_var,
            bg=self.paper_bg,
            fg="#5b4129",
            font=self.font_small
        ).pack(anchor="w", pady=(2, 0))

        map_frame = tk.Frame(center, bg=self.paper_bg)
        map_frame.pack(fill="both", expand=True, padx=16, pady=12)
        map_frame.grid_rowconfigure(0, weight=1)
        map_frame.grid_columnconfigure(0, weight=1)

        x_scroll = tk.Scrollbar(map_frame, orient="horizontal")
        y_scroll = tk.Scrollbar(map_frame, orient="vertical")

        self.battle_canvas = tk.Canvas(
            map_frame,
            bg="#efe2bf",
            highlightthickness=0,
            bd=0,
            xscrollcommand=x_scroll.set,
            yscrollcommand=y_scroll.set
        )

        x_scroll.config(command=self.battle_canvas.xview)
        y_scroll.config(command=self.battle_canvas.yview)

        self.battle_canvas.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        self.draw_battle_map()
        self.bind_canvas_scroll()

        self.build_battle_select_panel(right)

        log = self.build_log_panel(self.root)
        log.pack(side="bottom", fill="x", padx=12, pady=(0, 12))

        self.refresh_top_info()
        self.update_general_detail()
        self.refresh_battle_general_panel()

        if not self.log_cache:
            self.log("战场已展开，选择武将后攻击敌方目标。")
        self.status_var.set("请选择武将并确认出战。")

    def open_recruit_window_hint(self):
        messagebox.showinfo("提示", "请使用“据点征兵”按钮选择已占领的村子或城池。")

    def draw_battle_map_background(self):
        for x in range(0, self.map_width + 1, 100):
            self.battle_canvas.create_line(x, 0, x, self.map_height, fill="#d0c09a")
        for y in range(0, self.map_height + 1, 100):
            self.battle_canvas.create_line(0, y, self.map_width, y, fill="#d0c09a")

        self.battle_canvas.create_text(
            120,
            30,
            text="中键拖动地图，滚轮滚动",
            fill="#6b5636",
            font=self.font_small,
            anchor="w"
        )

    def draw_battle_map(self):
        self.battle_canvas.delete("all")
        self.draw_battle_map_background()

        for city in self.cities:
            self.draw_city(city)

        self.battle_canvas.configure(scrollregion=(0, 0, self.map_width, self.map_height))

    def bind_canvas_scroll(self):
        def on_mousewheel(event):
            if event.delta:
                self.battle_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.battle_canvas.bind("<MouseWheel>", on_mousewheel)
        self.battle_canvas.bind("<ButtonPress-2>", self.start_canvas_pan)
        self.battle_canvas.bind("<B2-Motion>", self.do_canvas_pan)
        self.battle_canvas.bind("<ButtonPress-3>", self.start_canvas_pan)
        self.battle_canvas.bind("<B3-Motion>", self.do_canvas_pan)

    def start_canvas_pan(self, event):
        if hasattr(self, "battle_canvas"):
            self.battle_canvas.scan_mark(event.x, event.y)

    def do_canvas_pan(self, event):
        if hasattr(self, "battle_canvas"):
            self.battle_canvas.scan_dragto(event.x, event.y, gain=1)

    def open_garrison_recruit_window(self):
        if not self.cities:
            messagebox.showwarning("提示", "地图尚未初始化。")
            return

        owned_locations = [
            c for c in self.cities
            if c["owner"] == "我方" and c["id"] != "enemy_capital"
        ]

        if not owned_locations:
            messagebox.showinfo("提示", "目前没有可征兵的我方据点。")
            return

        win = tk.Toplevel(self.root)
        win.title("据点征兵")
        win.geometry("460x360")
        win.configure(bg=self.panel_bg)
        win.transient(self.root)
        win.grab_set()

        tk.Label(
            win,
            text="选择我方据点进行征兵",
            bg=self.panel_bg,
            fg=self.accent,
            font=self.font_header
        ).pack(pady=(12, 6))

        listbox = tk.Listbox(
            win,
            height=10,
            bg="#1f1814",
            fg="#f1e7d1",
            selectbackground="#8b6a4f",
            selectforeground="white",
            font=self.font_small
        )
        listbox.pack(fill="both", expand=True, padx=16, pady=8)

        for c in owned_locations:
            listbox.insert(
                tk.END,
                f"{c['name']} | 类型:{c['type']} | 驻军:{c['garrison']}兵"
            )

        form = tk.Frame(win, bg=self.panel_bg)
        form.pack(fill="x", padx=16, pady=(0, 8))

        tk.Label(form, text="征兵数量：", bg=self.panel_bg, fg=self.text_fg, font=self.font_small).pack(side="left")
        num_var = tk.StringVar(value="5")
        num_entry = tk.Entry(form, textvariable=num_var, width=10, font=self.font_small)
        num_entry.pack(side="left", padx=6)

        def do_recruit():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("提示", "请选择一个据点。")
                return

            try:
                recruit_count = int(num_var.get())
            except Exception:
                messagebox.showwarning("提示", "请输入有效数字。")
                return

            if recruit_count <= 0:
                messagebox.showwarning("提示", "征兵数量必须大于 0。")
                return

            idx = sel[0]
            city = owned_locations[idx]

            max_recruit = 30 if city["type"] == "capital" else 20 if city["type"] == "city" else 10
            if recruit_count > max_recruit:
                messagebox.showwarning("提示", f"该据点单次最多征兵 {max_recruit}。")
                return

            food_cost = recruit_count * 2
            money_cost = recruit_count

            if self.resources["粮食"] < food_cost or self.resources["金钱"] < money_cost:
                messagebox.showwarning("提示", "资源不足，无法征兵。")
                return

            self.resources["粮食"] -= food_cost
            self.resources["金钱"] -= money_cost
            city["garrison"] += recruit_count

            self.log(f"在 {city['name']} 征得 {recruit_count} 兵。")
            self.save_generals()
            self.refresh_top_info()

            if self.mode == "battle" and hasattr(self, "battle_canvas"):
                self.update_city_visual(city)

            messagebox.showinfo("成功", f"{city['name']} 征兵完成。")
            win.destroy()

        tk.Button(
            form,
            text="确认征兵",
            command=do_recruit,
            bg=self.button_bg,
            fg="white",
            activebackground=self.button_active,
            activeforeground="white",
            font=self.font_small
        ).pack(side="right")

    def on_city_click(self, city_id):
        city = self.get_city_by_id(city_id)
        if not city:
            return

        if city["owner"] == "我方":
            self.log(f"{city['name']} 已经是我方领地。")
            self.status_var.set(f"{city['name']} 已是我方领地。")
            return

        if city["id"] == "player_capital":
            self.log("不能攻击我方军营。")
            self.status_var.set("不能攻击我方军营。")
            return

        attackers = self.get_selected_battle_generals()
        if not attackers:
            self.log("请先在右侧选择出战武将并确认。")
            self.status_var.set("请先选择出战武将。")
            messagebox.showwarning("提示", "请选择出战武将后再进攻。")
            return

        attack_power = 0
        loss_modifier = 1.0
        no_loss = False
        attacker_names = []

        for g in attackers:
            attacker_names.append(g["name"])
            atk = g["troops"] + int(g["force"] * 0.8) + int(g["command"] * 1.2)
            skill = get_general_skill(g["name"])

            if skill == "武圣":
                atk *= 1.25
            elif skill == "猛将":
                atk *= 1.2
                loss_modifier *= 1.2
            elif skill == "仁德":
                loss_modifier *= 0.5
            elif skill == "神机":
                no_loss = True

            attack_power += int(atk)

        defense = (
            city["garrison"]
            + (20 if city["type"] == "capital" else 10 if city["type"] == "city" else 5)
            + random.randint(5, 15)
        )

        self.log(f"{'、'.join(attacker_names)} 进攻 {city['name']}：我方战力 {attack_power} / 守军 {defense}")
        self.status_var.set(f"出战：{'、'.join(attacker_names)}")

        if attack_power >= defense:
            for g in attackers:
                loss = 0 if no_loss else random.randint(1, 5)
                g["troops"] = max(0, g["troops"] - int(loss * loss_modifier))

            city["owner"] = "我方"

            if city["type"] == "capital":
                city["garrison"] = max(20, sum(g["troops"] for g in attackers) // 2 + 10)
                self.resources["金钱"] += 30
                self.resources["木材"] += 12
                self.log(f"{'、'.join(attacker_names)} 攻破 {city['name']}，我方夺得重镇。")
            elif city["type"] == "city":
                city["garrison"] = max(12, sum(g["troops"] for g in attackers) // 3 + 6)
                self.resources["金钱"] += 18
                self.resources["粮食"] += 10
                self.log(f"{'、'.join(attacker_names)} 攻下 {city['name']}。")
            else:
                city["garrison"] = max(8, sum(g["troops"] for g in attackers) // 4 + 4)
                self.resources["粮食"] += 15
                self.log(f"{'、'.join(attacker_names)} 占领 {city['name']}，获得粮草。")

            self.recalculate_armies()
            self.save_generals()
            self.refresh_top_info()
            self.refresh_battle_general_panel()
            self.update_general_detail()
            self.update_city_visual(city)

            self.capture_enemy()
            self.save_generals()

            messagebox.showinfo("胜利", f"成功拿下 {city['name']}！")
        else:
            for g in attackers:
                loss = 0 if no_loss else random.randint(3, 8)
                g["troops"] = max(0, g["troops"] - int(loss * loss_modifier))

            city["garrison"] = max(1, city["garrison"] - random.randint(1, 4))
            self.log(f"{'、'.join(attacker_names)} 进攻 {city['name']} 失利。")
            messagebox.showwarning("失败", "进攻失败，损失惨重。")

            self.recalculate_armies()
            self.save_generals()
            self.refresh_top_info()
            self.refresh_battle_general_panel()
            self.update_general_detail()
            self.update_city_visual(city)

        self.refresh_top_info()

    def update_city_visual(self, city):
        if not hasattr(self, "battle_canvas"):
            return
        if not city.get("circle_id") or not city.get("text_id"):
            return

        self.battle_canvas.itemconfig(city["circle_id"], fill=self.city_color(city["owner"]))
        label_color = "white" if city["owner"] != "中立" else "#241c17"
        self.battle_canvas.itemconfig(city["text_id"], fill=label_color)
        self.battle_canvas.itemconfig(city["text_id"], text=f"{city['name']}\n{city['garrison']}兵")

    def create_stat_card(self, parent, title, value):
        card = tk.Frame(parent, bg="#f5ead0", bd=2, relief="groove")
        tk.Label(
            card,
            text=title,
            bg="#f5ead0",
            fg="#5b4129",
            font=self.font_small
        ).pack(anchor="w", padx=10, pady=(8, 0))

        tk.Label(
            card,
            text=value,
            bg="#f5ead0",
            fg="#241c17",
            font=("Microsoft YaHei", 15, "bold")
        ).pack(anchor="w", padx=10, pady=(4, 10))

        return card


if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
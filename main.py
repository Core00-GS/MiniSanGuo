import json
import os
import random
import tkinter as tk
import tkinter.font as tkfont
from datetime import datetime, timedelta
from tkinter import messagebox, ttk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENERALS_FILE = os.path.join(BASE_DIR, "generals.json")

DEFAULT_GENERALS = [
    {"id":"g001","name":"刘备","title":"昭烈帝","camp":"我方","force":74,"intellect":82,"politics":96,"command":88,"loyalty":100,"troops":46,"alive":True,"morale":100,"exp":0,"level":1},
    {"id":"g002","name":"关羽","title":"美髯公","camp":"我方","force":99,"intellect":72,"politics":58,"command":92,"loyalty":98,"troops":38,"alive":True,"morale":100,"exp":0,"level":1},
    {"id":"g003","name":"张飞","title":"万人敌","camp":"我方","force":98,"intellect":55,"politics":42,"command":78,"loyalty":96,"troops":32,"alive":True,"morale":100,"exp":0,"level":1},
    {"id":"g004","name":"诸葛亮","title":"卧龙","camp":"我方","force":38,"intellect":100,"politics":100,"command":95,"loyalty":100,"troops":22,"alive":True,"morale":100,"exp":0,"level":1},
    {"id":"g005","name":"赵云","title":"常胜将军","camp":"我方","force":97,"intellect":80,"politics":70,"command":94,"loyalty":100,"troops":32,"alive":True,"morale":100,"exp":0,"level":1},
    {"id":"g101","name":"曹操","title":"魏武帝","camp":"敌方","force":85,"intellect":98,"politics":95,"command":97,"loyalty":100,"troops":60,"alive":True,"morale":100,"exp":0,"level":3},
    {"id":"g102","name":"夏侯惇","title":"盲夏侯","camp":"敌方","force":92,"intellect":68,"politics":60,"command":84,"loyalty":95,"troops":32,"alive":True,"morale":100,"exp":0,"level":2},
    {"id":"g103","name":"典韦","title":"古之恶来","camp":"敌方","force":100,"intellect":45,"politics":28,"command":76,"loyalty":94,"troops":30,"alive":True,"morale":100,"exp":0,"level":2},
    {"id":"g104","name":"许褚","title":"虎痴","camp":"敌方","force":97,"intellect":42,"politics":30,"command":72,"loyalty":93,"troops":34,"alive":True,"morale":100,"exp":0,"level":2},
    {"id":"g105","name":"郭嘉","title":"鬼才","camp":"敌方","force":35,"intellect":100,"politics":88,"command":70,"loyalty":90,"troops":18,"alive":True,"morale":100,"exp":0,"level":2},
]

# ─── 武将技能定义 ──────────────────────────────────────────────
SKILLS = {
    "刘备":  {"name":"仁德",  "desc":"我方伤亡减半，民心+",  "color":"#4fc3f7"},
    "关羽":  {"name":"武圣",  "desc":"攻击力×1.25，必杀率高", "color":"#ef9a9a"},
    "张飞":  {"name":"猛将",  "desc":"攻击力×1.2，但损兵较多","color":"#ce93d8"},
    "诸葛亮":{"name":"神机",  "desc":"我方零损耗，智谋决胜",  "color":"#80cbc4"},
    "赵云":  {"name":"龙胆",  "desc":"攻守兼备，兵力不低于1", "color":"#a5d6a7"},
    "曹操":  {"name":"奸雄",  "desc":"随机夺敌将领忠心",      "color":"#ffcc02"},
    "夏侯惇":{"name":"铁壁",  "desc":"守城加成+30%",          "color":"#bcaaa4"},
    "典韦":  {"name":"怒甲",  "desc":"攻击+15，但只能单将出击","color":"#ff8a65"},
    "许褚":  {"name":"虎威",  "desc":"正面对决增幅×1.15",     "color":"#b0bec5"},
    "郭嘉":  {"name":"遗计",  "desc":"败退时敌军额外损兵",    "color":"#ffe082"},
}

# ─── 随机事件表 ──────────────────────────────────────────────
RANDOM_EVENTS = [
    {"text":"境内发现金矿，金钱+20","effect":{"金钱":20}},
    {"text":"秋收丰年，粮食+30","effect":{"粮食":30}},
    {"text":"山间伐木，木材+20","effect":{"木材":20}},
    {"text":"瘟疫蔓延，粮食-15","effect":{"粮食":-15}},
    {"text":"流民涌入，可征兵数+10","effect":{"bonus_troops":10}},
    {"text":"大旱之年，粮食-20","effect":{"粮食":-20}},
    {"text":"商队途经，金钱+15","effect":{"金钱":15}},
    {"text":"山贼作乱，金钱-10","effect":{"金钱":-10}},
]

DIPLOMACY_OPTIONS = ["结盟","停战","宣战","索要粮草","要求称臣"]


def get_skill(name):
    return SKILLS.get(name, {"name":"无","desc":"无特殊技能","color":"#888888"})


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("群雄逐鹿 · 三国策略")
        self.root.geometry("1440x860")
        self.root.minsize(1200, 720)
        self.root.configure(bg="#0d0b08")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # ── 调色板（深色水墨 + 金朱点缀） ───────────────────────
        self.C = {
            "bg":        "#0d0b08",
            "panel":     "#15120e",
            "panel2":    "#1e1912",
            "panel3":    "#261f17",
            "border":    "#3d3020",
            "border2":   "#5c4a2f",
            "gold":      "#c9a84c",
            "gold2":     "#f0d080",
            "red":       "#c0392b",
            "blue":      "#2471a3",
            "green":     "#1e8449",
            "gray":      "#7f8c8d",
            "text":      "#e8dcc8",
            "text2":     "#a89070",
            "text3":     "#6b5a40",
            "map_bg":    "#2b2318",
            "map_line":  "#3a2e1e",
            "friendly":  "#1a5276",
            "enemy":     "#7b241c",
            "neutral":   "#1e6a2e",
            "btn":       "#2c2418",
            "btn_h":     "#3d3020",
            "btn_gold":  "#5a3e10",
            "btn_goldh": "#7a5518",
            "accent":    "#c9a84c",
        }

        # ── 字体 ──────────────────────────────────────────────
        self.F = {
            "title":  ("STKaiti",   22, "bold"),
            "head":   ("STKaiti",   14, "bold"),
            "body":   ("Microsoft YaHei", 11),
            "small":  ("Microsoft YaHei", 10),
            "tiny":   ("Microsoft YaHei",  9),
            "mono":   ("Consolas",  10),
            "num":    ("STKaiti",   18, "bold"),
        }

        # ── 游戏状态 ──────────────────────────────────────────
        self.current_date   = datetime(184, 1, 1)
        self.turn           = 1
        self.max_stamina    = 6
        self.stamina        = self.max_stamina
        self.resources      = {"粮食":120,"金钱":60,"木材":40,"民心":80}
        self.commerce_lv    = 1
        self.agriculture_lv = 1
        self.security_lv    = 1
        self.wall_lv        = 0
        self.tech_lv        = 1
        self.spy_count      = 0
        self.diplomacy      = {}
        self.achievement    = []
        self.season         = "春"
        self.weather        = "晴"
        self.battle_count   = 0
        self.victory_count  = 0

        self.mode               = "overview"
        self.selected_general_id = None
        self.selected_general_ids = []
        self.generals              = []
        self.cities                = []
        self.log_cache             = []
        self.army_count            = 0
        self.enemy_army_count      = 0

        self.map_width  = 1900
        self.map_height = 1200

        # StringVar
        self.date_var          = tk.StringVar()
        self.stamina_var       = tk.StringVar()
        self.resource_var      = tk.StringVar()
        self.army_var          = tk.StringVar()
        self.general_detail_var= tk.StringVar()
        self.battle_general_var= tk.StringVar()
        self.status_var        = tk.StringVar()
        self.season_var        = tk.StringVar()
        self.weather_var       = tk.StringVar()
        self.morale_var        = tk.StringVar()

        self.load_generals()
        self.recalculate_armies()
        self.selected_general_id = self.get_first_friendly_id()
        self.create_battle_scenario()
        self.show_overview()

    # ═══════════════════════════════════════════════════════
    #  数据 I/O
    # ═══════════════════════════════════════════════════════
    def ensure_file(self):
        if not os.path.exists(GENERALS_FILE):
            with open(GENERALS_FILE,"w",encoding="utf-8") as f:
                json.dump(DEFAULT_GENERALS,f,ensure_ascii=False,indent=2)

    def normalize(self,g):
        d = {"id":"","name":"无名","title":"","camp":"我方","force":50,"intellect":50,
             "politics":50,"command":50,"loyalty":80,"troops":20,"alive":True,
             "morale":100,"exp":0,"level":1}
        d.update(g or {})
        if not d["id"]: d["id"] = f"g{random.randint(1000,9999)}"
        d["camp"] = "敌方" if d["camp"] == "敌方" else "我方"
        for k in ["force","intellect","politics","command","loyalty","troops","morale","exp","level"]:
            try:
                d[k] = int(d[k])
            except:
                d[k] = 0
        d["troops"] = max(0, d["troops"])
        d["morale"] = clamp(d.get("morale",100),0,100)
        d["alive"]  = bool(d.get("alive",True))
        return d

    def load_generals(self):
        self.ensure_file()
        try:
            with open(GENERALS_FILE,"r",encoding="utf-8") as f:
                data = json.load(f)
            self.generals = [self.normalize(x) for x in data]
        except:
            self.generals = [self.normalize(x) for x in DEFAULT_GENERALS]
        self.save_generals()

    def save_generals(self):
        with open(GENERALS_FILE,"w",encoding="utf-8") as f:
            json.dump(self.generals,f,ensure_ascii=False,indent=2)

    # ═══════════════════════════════════════════════════════
    #  查询辅助
    # ═══════════════════════════════════════════════════════
    def recalculate_armies(self):
        self.army_count       = sum(g["troops"] for g in self.generals if g["camp"]=="我方" and g["alive"])
        self.enemy_army_count = sum(g["troops"] for g in self.generals if g["camp"]=="敌方" and g["alive"])

    def get_first_friendly_id(self):
        for g in self.generals:
            if g["camp"]=="我方" and g["alive"] and g["troops"]>0:
                return g["id"]
        return None

    def get_by_id(self,gid):
        for g in self.generals:
            if g["id"] == gid:
                return g
        return None

    def get_selected(self):
        return self.get_by_id(self.selected_general_id)

    def get_friendly(self):
        return [g for g in self.generals if g["camp"]=="我方" and g["alive"] and g["troops"]>0]

    def get_enemies_alive(self):
        return [g for g in self.generals if g["camp"]=="敌方" and g["alive"]]

    def get_city(self,cid):
        for c in self.cities:
            if c["id"] == cid:
                return c
        return None

    def get_selected_attackers(self):
        return [g for gid in self.selected_general_ids
                for g in [self.get_by_id(gid)]
                if g and g["camp"]=="我方" and g["alive"] and g["troops"]>0]

    def city_color(self,owner):
        return {"我方":self.C["friendly"],"敌方":self.C["enemy"]}.get(owner,self.C["neutral"])

    def city_radius(self,t):
        return {"capital":34,"city":26,"village":18}.get(t,18)

    def season_from_date(self):
        m = self.current_date.month
        return ["冬","春","春","夏","夏","夏","秋","秋","秋","冬","冬","冬"][m-1]

    def random_weather(self):
        return random.choice(["晴","阴","雨","大雾","风雪"])

    def get_morale_avg(self):
        fl = self.get_friendly()
        if not fl:
            return 0
        return int(sum(g["morale"] for g in fl)/len(fl))

    # ═══════════════════════════════════════════════════════
    #  地图初始化
    # ═══════════════════════════════════════════════════════
    def create_battle_scenario(self):
        if self.cities:
            return
        self.cities = [
            {"id":"player_capital","name":"汉中","type":"capital","owner":"我方","garrison":self.army_count,"x":160,"y":880,"circle_id":None,"text_id":None},
            {"id":"v1","name":"沔水村","type":"village","owner":"中立","garrison":10,"x":310,"y":760,"circle_id":None,"text_id":None},
            {"id":"v2","name":"褒斜道","type":"village","owner":"中立","garrison":12,"x":500,"y":620,"circle_id":None,"text_id":None},
            {"id":"c1","name":"武都","type":"city","owner":"敌方","garrison":26,"x":760,"y":490,"circle_id":None,"text_id":None},
            {"id":"v3","name":"阳平关","type":"village","owner":"中立","garrison":10,"x":640,"y":310,"circle_id":None,"text_id":None},
            {"id":"c2","name":"南郑","type":"city","owner":"敌方","garrison":32,"x":970,"y":740,"circle_id":None,"text_id":None},
            {"id":"v4","name":"成固镇","type":"village","owner":"中立","garrison":9,"x":1100,"y":540,"circle_id":None,"text_id":None},
            {"id":"c3","name":"洛阳","type":"city","owner":"敌方","garrison":36,"x":1270,"y":330,"circle_id":None,"text_id":None},
            {"id":"v5","name":"颍川村","type":"village","owner":"中立","garrison":11,"x":1430,"y":850,"circle_id":None,"text_id":None},
            {"id":"enemy_capital","name":"许都","type":"capital","owner":"敌方","garrison":self.enemy_army_count,"x":1560,"y":190,"circle_id":None,"text_id":None},
        ]

    # ═══════════════════════════════════════════════════════
    #  通用 UI 零件
    # ═══════════════════════════════════════════════════════
    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def on_close(self):
        self.save_generals()
        self.root.destroy()

    def log(self,text):
        ts = self.current_date.strftime("%Y年%m月%d日")
        ln = f"◆ [{ts}] {text}"
        self.log_cache.append(ln)
        self.log_cache = self.log_cache[-100:]
        if hasattr(self, "log_text"):
            self.log_text.config(state="normal")
            self.log_text.delete("1.0","end")
            self.log_text.insert("end","\n".join(self.log_cache))
            self.log_text.see("end")
            self.log_text.config(state="disabled")

    def btn(self, parent, text, cmd, w=14, style="normal"):
        colors = {
            "normal": (self.C["btn"],    self.C["btn_h"],    self.C["text"]),
            "gold":   (self.C["btn_gold"],self.C["btn_goldh"],self.C["gold"]),
            "danger": ("#3b1212",        "#5a1a1a",           "#e88"),
        }
        bg, abg, fg = colors.get(style, colors["normal"])
        b = tk.Button(parent, text=text, command=cmd, width=w,
                      bg=bg, fg=fg, activebackground=abg, activeforeground=fg,
                      bd=1, relief="flat", font=self.F["body"], cursor="hand2",
                      highlightthickness=1, highlightbackground=self.C["border2"])
        b.bind("<Enter>", lambda e: b.config(bg=abg))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def separator(self, parent, color=None):
        c = color or self.C["border"]
        tk.Frame(parent, bg=c, height=1).pack(fill="x", padx=8, pady=4)

    def label(self, parent, text, size="body", color=None, **kw):
        fg = color or self.C["text"]
        return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=fg,
                        font=self.F.get(size, self.F["body"]), **kw)

    # ─── 顶部横幅 ─────────────────────────────────────────
    def build_header(self):
        hdr = tk.Frame(self.root, bg=self.C["panel2"], height=70)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        lf = tk.Frame(hdr, bg=self.C["panel2"])
        lf.pack(side="left", fill="y", padx=18, pady=8)
        tk.Label(lf, text="群雄逐鹿", bg=self.C["panel2"], fg=self.C["gold"],
                 font=self.F["title"]).pack(anchor="w")
        tk.Label(lf, text="天下三分  逐鹿中原", bg=self.C["panel2"], fg=self.C["text3"],
                 font=self.F["tiny"]).pack(anchor="w")

        mf = tk.Frame(hdr, bg=self.C["panel2"])
        mf.pack(side="left", fill="y", expand=True, padx=10, pady=6)

        res_icons = [("🌾","粮食","粮食"),("💰","金钱","金钱"),("🪵","木材","木材"),("❤","民心","民心")]
        for icon, label_txt, key in res_icons:
            rf = tk.Frame(mf, bg=self.C["panel3"], bd=0)
            rf.pack(side="left", padx=5, pady=2)
            tk.Label(rf, text=f"{icon} {label_txt}", bg=self.C["panel3"], fg=self.C["text2"],
                     font=self.F["tiny"], padx=6).pack(anchor="w")
            val_lbl = tk.Label(rf, text=str(self.resources[key]),
                               bg=self.C["panel3"], fg=self.C["gold2"],
                               font=self.F["num"], padx=6)
            val_lbl.pack()
            setattr(self, f"res_lbl_{key}", val_lbl)

        rf = tk.Frame(hdr, bg=self.C["panel2"])
        rf.pack(side="right", fill="y", padx=18, pady=8)

        self.date_lbl = tk.Label(rf, textvariable=self.date_var,
                                 bg=self.C["panel2"], fg=self.C["gold"], font=self.F["head"])
        self.date_lbl.pack(anchor="e")

        info_row = tk.Frame(rf, bg=self.C["panel2"])
        info_row.pack(anchor="e")
        tk.Label(info_row, textvariable=self.stamina_var,
                 bg=self.C["panel2"], fg=self.C["text"], font=self.F["small"]).pack(side="left", padx=6)
        tk.Label(info_row, textvariable=self.season_var,
                 bg=self.C["panel2"], fg=self.C["text2"], font=self.F["small"]).pack(side="left", padx=6)
        tk.Label(info_row, textvariable=self.weather_var,
                 bg=self.C["panel2"], fg=self.C["text2"], font=self.F["small"]).pack(side="left")

        army_row = tk.Frame(rf, bg=self.C["panel2"])
        army_row.pack(anchor="e")
        tk.Label(army_row, textvariable=self.army_var,
                 bg=self.C["panel2"], fg=self.C["text2"], font=self.F["tiny"]).pack()

        self.refresh_header()

    def refresh_header(self):
        date_text = self.current_date.strftime("%Y年 %m月 %d日")
        self.date_var.set(f"◆ {date_text}")
        self.stamina_var.set(f"体力 {'■'*self.stamina}{'□'*(self.max_stamina-self.stamina)} {self.stamina}/{self.max_stamina}")
        self.season_var.set(f"【{self.season_from_date()}】")
        self.weather_var.set(f"天气:{self.weather}")
        self.army_var.set(f"我方 ▲{self.army_count}   敌方 ▼{self.enemy_army_count}   胜:{self.victory_count}")

    # ─── 日志面板 ─────────────────────────────────────────
    def build_log(self, parent):
        frm = tk.Frame(parent, bg=self.C["panel"], bd=1, relief="solid")
        tk.Label(frm, text="军情战报", bg=self.C["panel2"], fg=self.C["gold"],
                 font=self.F["head"], anchor="w", padx=10, pady=3).pack(fill="x")
        self.log_text = tk.Text(frm, height=6, bg="#090806", fg="#c9b890",
                                wrap="word", state="disabled", bd=0,
                                font=self.F["mono"], insertbackground="white")
        self.log_text.pack(fill="both", expand=True, padx=6, pady=6)
        if self.log_cache:
            self.log_text.config(state="normal")
            self.log_text.insert("end","\n".join(self.log_cache))
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        return frm

    # ─── 武将面板 ─────────────────────────────────────────
    def build_general_panel(self, parent, battle=False):
        frm = tk.Frame(parent, bg=self.C["panel"])
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="将帅录", bg=self.C["panel2"], fg=self.C["gold"],
                 font=self.F["head"], anchor="w", padx=10, pady=3).pack(fill="x")

        if battle:
            tk.Label(frm, text="Ctrl/Shift 多选 → 确认出战",
                     bg=self.C["panel"], fg=self.C["text2"], font=self.F["tiny"],
                     anchor="w", padx=8).pack(fill="x")

        lf = tk.Frame(frm, bg=self.C["panel"])
        lf.pack(fill="both", expand=False, padx=6, pady=4)
        mode = "multiple" if battle else "browse"
        lb = tk.Listbox(lf, height=11, selectmode=mode,
                        bg="#0a0806", fg=self.C["text"],
                        selectbackground=self.C["border2"], selectforeground=self.C["gold"],
                        bd=0, font=self.F["small"], activestyle="none")
        sc = tk.Scrollbar(lf, command=lb.yview, bg=self.C["panel"])
        lb.config(yscrollcommand=sc.set)
        lb.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")

        if battle:
            self.battle_lb = lb
        else:
            self.general_lb = lb
            lb.bind("<<ListboxSelect>>", self.on_general_select)

        if battle:
            bb = tk.Frame(frm, bg=self.C["panel"])
            bb.pack(fill="x", padx=6, pady=2)
            self.btn(bb, "确认出战", self.confirm_attackers, w=10, style="gold").pack(side="left", padx=2)
            self.btn(bb, "全军出战", self.select_all, w=10).pack(side="left", padx=2)

        df = tk.Frame(frm, bg=self.C["panel3"], bd=1, relief="solid")
        df.pack(fill="both", expand=True, padx=6, pady=(2,6))
        tk.Label(df, text="武将详情", bg=self.C["panel3"], fg=self.C["gold"],
                 font=self.F["tiny"], anchor="w", padx=8, pady=4).pack(fill="x")
        detail_key = "battle_general_var" if battle else "general_detail_var"
        tk.Label(df, textvariable=getattr(self, detail_key),
                 bg=self.C["panel3"], fg=self.C["text"],
                 justify="left", anchor="nw", font=self.F["tiny"],
                 wraplength=260).pack(fill="both", expand=True, padx=8, pady=(0,8))

        self.populate_general_list(battle)
        return frm

    def populate_general_list(self, battle=False):
        lb = getattr(self, "battle_lb", None) if battle else getattr(self, "general_lb", None)
        if not lb:
            return
        lb.delete(0, "end")

        if battle:
            self.friendly_generals = self.get_friendly()
            for g in self.friendly_generals:
                sk = get_skill(g["name"])["name"]
                bar = "█" * (g["morale"] // 20)
                lb.insert("end", f"{g['name']} {g['title'][:2]}  兵:{g['troops']}  技:{sk}  气:{bar}")
            self.update_battle_detail()
        else:
            sel_idx = None
            for i, g in enumerate(self.generals):
                tag = "◆" if g["camp"] == "我方" else "◇"
                status = "✦" if g["alive"] else "✕"
                lb.insert("end", f"{tag}{status} {g['name']} Lv{g['level']}  兵:{g['troops']}  武:{g['force']} 智:{g['intellect']}")
                if g["id"] == self.selected_general_id:
                    sel_idx = i
            if sel_idx is not None:
                lb.selection_clear(0, "end")
                lb.selection_set(sel_idx)
                lb.activate(sel_idx)
            self.update_general_detail()

    def update_general_detail(self):
        g = self.get_selected()
        if not g:
            self.general_detail_var.set("暂无武将。")
            return
        sk = get_skill(g["name"])
        self.general_detail_var.set(
            f"姓名：{g['name']}  {g['title']}\n"
            f"阵营：{g['camp']}  等级：Lv{g['level']}\n"
            f"武力：{g['force']}  智力：{g['intellect']}\n"
            f"政治：{g['politics']}  统率：{g['command']}\n"
            f"忠诚：{g['loyalty']}  士气：{g['morale']}\n"
            f"兵力：{g['troops']}  经验：{g['exp']}\n"
            f"技能：【{sk['name']}】{sk['desc']}\n"
            f"状态：{'在世' if g['alive'] else '已故'}"
        )

    def update_battle_detail(self):
        if not self.selected_general_ids:
            self.battle_general_var.set("请选择出战武将，确认后点击地图城池攻击。")
            return
        names = [g["name"] for gid in self.selected_general_ids for g in [self.get_by_id(gid)] if g]
        total_troops = sum(g["troops"] for gid in self.selected_general_ids for g in [self.get_by_id(gid)] if g)
        self.battle_general_var.set(f"出战：{'、'.join(names)}\n总兵力：{total_troops}\n点击地图城池发动进攻")

    def on_general_select(self, e):
        lb = getattr(self, "general_lb", None)
        if not lb:
            return
        sel = lb.curselection()
        if not sel:
            return
        idx = sel[0]
        if 0 <= idx < len(self.generals):
            self.selected_general_id = self.generals[idx]["id"]
            self.update_general_detail()

    def confirm_attackers(self):
        lb = getattr(self, "battle_lb", None)
        if not lb:
            return
        idxs = lb.curselection()
        if not idxs:
            self.selected_general_ids = []
            self.update_battle_detail()
            return
        self.selected_general_ids = [self.friendly_generals[i]["id"] for i in idxs if 0 <= i < len(self.friendly_generals)]
        self.update_battle_detail()

    def select_all(self):
        lb = getattr(self, "battle_lb", None)
        if not lb:
            return
        lb.selection_set(0, "end")
        self.confirm_attackers()

    # ═══════════════════════════════════════════════════════
    #  总览界面
    # ═══════════════════════════════════════════════════════
    def show_overview(self):
        self.mode = "overview"
        self.clear()
        self.build_header()

        body = tk.Frame(self.root, bg=self.C["bg"])
        body.pack(fill="both", expand=True, padx=10, pady=(6,0))

        lf = tk.Frame(body, bg=self.C["panel"], width=170, bd=1, relief="solid")
        lf.pack(side="left", fill="y")
        lf.pack_propagate(False)
        tk.Label(lf, text="军政令", bg=self.C["panel2"], fg=self.C["gold"],
                 font=self.F["head"], anchor="w", padx=10, pady=4).pack(fill="x")
        bcnt = tk.Frame(lf, bg=self.C["panel"])
        bcnt.pack(fill="both", expand=True, padx=8, pady=8)

        cmds = [
            ("⚔ 出征战场",  self.enter_battle,           "gold"),
            ("兵 征兵",      self.recruit_soldiers,        "normal"),
            ("城 据点征兵",  self.open_garrison_recruit,   "normal"),
            ("商 发展商业",  self.upgrade_commerce,        "normal"),
            ("农 发展农业",  self.upgrade_agriculture,     "normal"),
            ("治 提升治安",  self.upgrade_security,        "normal"),
            ("城 修筑城墙",  self.repair_wall,             "normal"),
            ("技 科技研发",  self.upgrade_tech,            "normal"),
            ("谍 派遣间谍",  self.send_spy,                "normal"),
            ("交 外交谈判",  self.open_diplomacy,          "normal"),
            ("★ 武将升级",  self.open_general_upgrade,    "normal"),
            ("休 休整回满",  self.rest,                    "normal"),
            ("日 结束本日",  self.next_day,                "normal"),
        ]
        for txt, cmd, style in cmds:
            self.btn(bcnt, txt, cmd, w=17, style=style).pack(pady=3, fill="x")

        cf = tk.Frame(body, bg=self.C["panel3"], bd=1, relief="solid")
        cf.pack(side="left", fill="both", expand=True, padx=8)

        title_row = tk.Frame(cf, bg=self.C["panel2"])
        title_row.pack(fill="x")
        tk.Label(title_row, text="◈ 内政总览", bg=self.C["panel2"],
                 fg=self.C["gold"], font=self.F["title"], padx=14, pady=6).pack(side="left")
        tk.Label(title_row, text=f"第 {self.turn} 回合", bg=self.C["panel2"],
                 fg=self.C["text2"], font=self.F["head"], padx=8).pack(side="right")

        cards = tk.Frame(cf, bg=self.C["panel3"])
        cards.pack(fill="x", padx=14, pady=10)

        card_data = [
            ("我方兵力", str(self.army_count), "#4fc3f7"),
            ("敌方兵力", str(self.enemy_army_count), "#ef5350"),
            ("体力", f"{self.stamina}/{self.max_stamina}", "#ffb74d"),
            ("平均士气", f"{self.get_morale_avg()}%", "#81c784"),
            ("科技等级", f"Lv{self.tech_lv}", "#ce93d8"),
            ("间谍", str(self.spy_count), "#80cbc4"),
        ]

        for i, (title, val, color) in enumerate(card_data):
            card = tk.Frame(cards, bg=self.C["panel2"], bd=1, relief="solid")
            card.grid(row=0, column=i, padx=5, pady=4, sticky="nsew")
            tk.Label(
                card,
                text=title,
                bg=self.C["panel2"],
                fg=self.C["text2"],
                font=self.F["tiny"],
                padx=10
            ).pack(anchor="w", pady=(6, 0))
            tk.Label(
                card,
                text=str(val),
                bg=self.C["panel2"],
                fg=color,
                font=("Arial", 14),
                padx=10
            ).pack(anchor="w", pady=(2, 8))

        for i in range(6):
            cards.grid_columnconfigure(i, weight=1)

        gov_frm = tk.Frame(cf, bg=self.C["panel3"])
        gov_frm.pack(fill="x", padx=14, pady=2)
        gov_items = [
            ("🏗 商业",   self.commerce_lv),
            ("🌾 农业",   self.agriculture_lv),
            ("⚖ 治安",   self.security_lv),
            ("🏯 城墙",   self.wall_lv),
            ("🔬 科技",   self.tech_lv),
        ]
        for label, lv in gov_items:
            gf = tk.Frame(gov_frm, bg=self.C["panel2"], bd=1, relief="solid")
            gf.pack(side="left", padx=4, pady=4)
            tk.Label(gf, text=label, bg=self.C["panel2"], fg=self.C["text2"],
                     font=self.F["tiny"], padx=8, pady=2).pack()
            bar = tk.Frame(gf, bg=self.C["panel2"])
            bar.pack(padx=8, pady=(0,6))
            for i in range(5):
                clr = self.C["gold"] if i < lv else self.C["border"]
                tk.Frame(bar, bg=clr, width=12, height=6).pack(side="left", padx=1)

        self.separator(cf, self.C["border"])

        advice_frm = tk.Frame(cf, bg=self.C["panel3"])
        advice_frm.pack(fill="both", expand=True, padx=14, pady=6)
        tk.Label(advice_frm, text="◈ 战略参谋", bg=self.C["panel3"],
                 fg=self.C["gold"], font=self.F["head"], anchor="w").pack(anchor="w")

        sg = self.get_selected()
        cmd_name = f"{sg['name']}（{sg['title']}）" if sg else "未选将领"
        friendly_cities = len([c for c in self.cities if c["owner"] == "我方"])
        enemy_cities    = len([c for c in self.cities if c["owner"] == "敌方"])

        advice = (
            f"主将：{cmd_name}\n"
            f"我方占领据点：{friendly_cities}  敌方据点：{enemy_cities}\n"
            f"胜利条件：攻占敌方军营（许都）\n\n"
            f"参谋建议：\n"
            f"  ▸ 体力充足时应积极出征，体力不足可休整回满。\n"
            f"  ▸ 提升科技可解锁强力加成效果。\n"
            f"  ▸ 间谍可在攻城前削弱敌方守军。\n"
            f"  ▸ 武将升级可大幅提升战斗力。\n"
            f"  ▸ 外交谈判可暂时稳住中立势力。\n"
        )
        tk.Label(advice_frm, text=advice, bg=self.C["panel3"], fg=self.C["text"],
                 justify="left", anchor="nw", font=self.F["small"],
                 wraplength=500).pack(fill="both", expand=True, pady=6)

        if self.achievement:
            ach_lbl = "  ".join(f"【{a}】" for a in self.achievement[-3:])
            tk.Label(advice_frm, text=f"★ 成就：{ach_lbl}", bg=self.C["panel3"],
                     fg=self.C["gold2"], font=self.F["tiny"]).pack(anchor="w")

        rf = tk.Frame(body, bg=self.C["panel"], width=310, bd=1, relief="solid")
        rf.pack(side="right", fill="y")
        rf.pack_propagate(False)
        self.build_general_panel(rf, battle=False)

        self.build_log(self.root).pack(side="bottom", fill="x", padx=10, pady=(4,8))

    # ═══════════════════════════════════════════════════════
    #  战场界面
    # ═══════════════════════════════════════════════════════
    def show_battle(self):
        self.mode = "battle"
        self.clear()
        self.build_header()

        body = tk.Frame(self.root, bg=self.C["bg"])
        body.pack(fill="both", expand=True, padx=10, pady=(6,0))

        lf = tk.Frame(body, bg=self.C["panel"], width=170, bd=1, relief="solid")
        lf.pack(side="left", fill="y")
        lf.pack_propagate(False)
        tk.Label(lf, text="战场令", bg=self.C["panel2"], fg=self.C["gold"],
                 font=self.F["head"], anchor="w", padx=10, pady=4).pack(fill="x")
        bf = tk.Frame(lf, bg=self.C["panel"])
        bf.pack(fill="both", expand=True, padx=8, pady=8)
        self.btn(bf, "◀ 返回内政", self.show_overview, w=17, style="gold").pack(pady=3, fill="x")
        self.btn(bf, "城 据点征兵", self.open_garrison_recruit, w=17).pack(pady=3, fill="x")
        self.btn(bf, "兵 征兵", self.recruit_soldiers, w=17).pack(pady=3, fill="x")
        self.btn(bf, "谍 释放间谍", self.use_spy, w=17).pack(pady=3, fill="x")
        self.btn(bf, "休 休整回满", self.rest, w=17).pack(pady=3, fill="x")
        self.btn(bf, "日 结束本日", self.next_day, w=17).pack(pady=3, fill="x")

        tk.Label(lf, text="◈ 操作提示\n中键/右键拖动地图\n鼠标滚轮上下滚动\n点击城池发起进攻\n占领的城池永久保留",
                 bg=self.C["panel"], fg=self.C["text3"], font=self.F["tiny"],
                 justify="left", wraplength=150, padx=10).pack(pady=10, anchor="w")

        cf = tk.Frame(body, bg=self.C["map_bg"], bd=1, relief="solid")
        cf.pack(side="left", fill="both", expand=True, padx=8)

        map_hdr = tk.Frame(cf, bg=self.C["panel2"])
        map_hdr.pack(fill="x")
        tk.Label(map_hdr, text="◈ 天下形势", bg=self.C["panel2"],
                 fg=self.C["gold"], font=self.F["title"], padx=14, pady=5).pack(side="left")
        tk.Label(map_hdr, textvariable=self.status_var, bg=self.C["panel2"],
                 fg=self.C["text2"], font=self.F["small"], padx=10).pack(side="right")

        legend = tk.Frame(cf, bg=self.C["panel3"])
        legend.pack(fill="x", padx=10, pady=4)
        for txt, color in [("● 我方", self.C["friendly"]), ("● 敌方", self.C["enemy"]), ("● 中立", self.C["neutral"] )]:
            tk.Label(legend, text=txt, bg=self.C["panel3"], fg=color,
                     font=self.F["tiny"], padx=8).pack(side="left")
        tk.Label(legend, text="大圆=军营  中圆=城池  小圆=村庄",
                 bg=self.C["panel3"], fg=self.C["text3"], font=self.F["tiny"], padx=12).pack(side="left")

        map_container = tk.Frame(cf, bg=self.C["map_bg"])
        map_container.pack(fill="both", expand=True, padx=8, pady=6)
        map_container.grid_rowconfigure(0, weight=1)
        map_container.grid_columnconfigure(0, weight=1)

        xsc = tk.Scrollbar(map_container, orient="horizontal", bg=self.C["panel"])
        ysc = tk.Scrollbar(map_container, orient="vertical", bg=self.C["panel"])

        self.canvas = tk.Canvas(map_container, bg=self.C["map_bg"],
                                highlightthickness=0, bd=0,
                                xscrollcommand=xsc.set, yscrollcommand=ysc.set)
        xsc.config(command=self.canvas.xview)
        ysc.config(command=self.canvas.yview)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        ysc.grid(row=0, column=1, sticky="ns")
        xsc.grid(row=1, column=0, sticky="ew")

        self.draw_map()
        self.bind_map_scroll()

        rf = tk.Frame(body, bg=self.C["panel"], width=310, bd=1, relief="solid")
        rf.pack(side="right", fill="y")
        rf.pack_propagate(False)
        self.build_general_panel(rf, battle=True)

        self.build_log(self.root).pack(side="bottom", fill="x", padx=10, pady=(4,8))
        self.refresh_header()
        self.status_var.set("请在右侧选择出战武将，然后点击城池发起进攻")

    # ─── 地图绘制 ─────────────────────────────────────────
    def draw_map(self):
        self.canvas.delete("all")
        for x in range(0, self.map_width+1, 80):
            self.canvas.create_line(x, 0, x, self.map_height, fill=self.C["map_line"], width=1)
        for y in range(0, self.map_height+1, 80):
            self.canvas.create_line(0, y, self.map_width, y, fill=self.C["map_line"], width=1)

        terrains = [(400,150,"山岭"),(800,200,"平原"),(1200,600,"河流"),(550,900,"密林")]
        for x, y, t in terrains:
            self.canvas.create_text(x, y, text=t, fill=self.C["text3"], font=self.F["tiny"], tags="terrain")

        pairs = [("player_capital","v1"),("v1","v2"),("v2","c1"),("c1","v3"),
                 ("c1","c2"),("v3","c3"),("c2","v4"),("v4","c3"),
                 ("c3","enemy_capital"),("c2","v5"),("v5","enemy_capital")]
        for a, b in pairs:
            ca = self.get_city(a)
            cb = self.get_city(b)
            if ca and cb:
                self.canvas.create_line(ca["x"], ca["y"], cb["x"], cb["y"],
                                        fill=self.C["border2"], width=2, dash=(6,4))

        for c in self.cities:
            self.draw_city(c)
        self.canvas.configure(scrollregion=(0,0,self.map_width,self.map_height))

    def draw_city(self, city):
        x, y = city["x"], city["y"]
        r = self.city_radius(city["type"])
        col = self.city_color(city["owner"])
        oc = self.C["gold"] if city["owner"] == "我方" else self.C["border2"]

        cid = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=col, outline=oc, width=2)
        if city["type"] == "capital":
            self.canvas.create_oval(x-r//2, y-r//2, x+r//2, y+r//2,
                                    fill="", outline=self.C["gold"], width=1)
        txt = f"{city['name']}\n⚑{city['garrison']}"
        tid = self.canvas.create_text(x, y, text=txt, fill="white",
                                      font=("Microsoft YaHei", 9, "bold"))
        city["circle_id"] = cid
        city["text_id"] = tid

        for cobj in [cid, tid]:
            self.canvas.tag_bind(cobj, "<Button-1>", lambda e, cid2=city["id"]: self.on_city_click(cid2))
            self.canvas.tag_bind(cobj, "<Enter>", lambda e, c=col: self.canvas.config(cursor="hand2"))
            self.canvas.tag_bind(cobj, "<Leave>", lambda e: self.canvas.config(cursor=""))

    def update_city_visual(self, city):
        if not hasattr(self, "canvas"):
            return
        if not city.get("circle_id"):
            return
        col = self.city_color(city["owner"])
        oc = self.C["gold"] if city["owner"] == "我方" else self.C["border2"]
        self.canvas.itemconfig(city["circle_id"], fill=col, outline=oc)
        self.canvas.itemconfig(city["text_id"], text=f"{city['name']}\n⚑{city['garrison']}")

    def bind_map_scroll(self):
        def scroll(e):
            if e.delta:
                self.canvas.yview_scroll(int(-e.delta/120), "units")
        self.canvas.bind("<MouseWheel>", scroll)
        self.canvas.bind("<ButtonPress-2>", lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B2-Motion>", lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))
        self.canvas.bind("<ButtonPress-3>", lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B3-Motion>", lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))

    # ═══════════════════════════════════════════════════════
    #  战斗逻辑（增强版）
    # ═══════════════════════════════════════════════════════
    def on_city_click(self, cid):
        city = self.get_city(cid)
        if not city:
            return

        if city["owner"] == "我方":
            self.log(f"「{city['name']}」已是我方领地。")
            return
        if cid == "player_capital":
            self.log("不可攻击我方军营。")
            return

        attackers = self.get_selected_attackers()
        if not attackers:
            self.status_var.set("请先选择出战武将！")
            messagebox.showwarning("提示", "请先在右侧选择出战武将，然后再点击城池。")
            return

        self.resolve_battle(city, attackers)

    def resolve_battle(self, city, attackers):
        attack_power = 0
        loss_mod = 1.0
        no_loss = False
        force_single = False
        atk_names = []

        for g in attackers:
            atk_names.append(g["name"])
            atk = g["troops"] + int(g["force"] * 0.8) + int(g["command"] * 1.2)
            morale_bonus = (g["morale"] / 100) * 0.2
            atk *= (1 + morale_bonus)
            sk = get_skill(g["name"])["name"]

            if sk == "武圣":
                atk *= 1.25
            elif sk == "猛将":
                atk *= 1.2
                loss_mod *= 1.2
            elif sk == "仁德":
                loss_mod *= 0.5
            elif sk == "神机":
                no_loss = True
            elif sk == "龙胆":
                atk *= 1.1
            elif sk == "怒甲":
                atk += 15
                force_single = True
            elif sk == "虎威":
                atk *= 1.15

            attack_power += int(atk)

        if self.weather == "大雾":
            attack_power = int(attack_power * 0.85)
        if self.weather == "风雪":
            attack_power = int(attack_power * 0.9)

        attack_power = int(attack_power * (1 + self.tech_lv * 0.03))

        defense = (
            city["garrison"]
            + (25 if city["type"] == "capital" else 12 if city["type"] == "city" else 6)
            + random.randint(5, 15)
        )

        if self.spy_count > 0:
            defense = int(defense * 0.85)
            self.spy_count -= 1
            self.log("间谍行动：敌方守备削弱15%。")

        self.battle_count += 1
        self.log(f"{'、'.join(atk_names)} 攻打【{city['name']}】| 我方:{attack_power} / 敌守:{defense}")

        if attack_power >= defense:
            self._on_victory(city, attackers, no_loss, loss_mod, atk_names)
        else:
            self._on_defeat(city, attackers, no_loss, loss_mod, atk_names)

        self.recalculate_armies()
        self.save_generals()
        self.refresh_header()
        self.populate_general_list(battle=True)
        self.update_general_detail()
        self.update_city_visual(city)
        self.refresh_header()

    def _on_victory(self, city, attackers, no_loss, loss_mod, names):
        self.victory_count += 1
        for g in attackers:
            loss = 0 if no_loss else random.randint(1, 4)
            g["troops"] = max(0, g["troops"] - int(loss * loss_mod))
            g["exp"] += 20
            self._check_level_up(g)
            g["morale"] = clamp(g["morale"] + 10, 0, 100)

        city["owner"] = "我方"
        if city["type"] == "capital":
            city["garrison"] = max(20, sum(g["troops"] for g in attackers)//2 + 10)
            self.resources["金钱"] += 35
            self.resources["木材"] += 15
            self.resources["民心"] = clamp(self.resources["民心"] + 15, 0, 100)
            self.log(f"大胜！{'、'.join(names)} 攻克【{city['name']}】，天下震动！")
            self._check_achievement("攻克军营")
        elif city["type"] == "city":
            city["garrison"] = max(12, sum(g["troops"] for g in attackers)//3 + 6)
            self.resources["金钱"] += 20
            self.resources["粮食"] += 12
            self.resources["民心"] = clamp(self.resources["民心"] + 8, 0, 100)
            self.log(f"胜！{'、'.join(names)} 夺取【{city['name']}】。")
        else:
            city["garrison"] = max(8, sum(g["troops"] for g in attackers)//4 + 4)
            self.resources["粮食"] += 18
            self.resources["民心"] = clamp(self.resources["民心"] + 5, 0, 100)
            self.log(f"{'、'.join(names)} 占领【{city['name']}】，获得粮草。")

        self.try_capture_enemy()
        self.save_generals()

        if self.check_victory():
            self._game_over(True)
            return
        messagebox.showinfo("胜利 ⚔", f"成功拿下【{city['name']}】！\n武将经验+20，士气提升。")

    def _on_defeat(self, city, attackers, no_loss, loss_mod, names):
        for g in attackers:
            loss = 0 if no_loss else random.randint(3, 9)
            g["troops"] = max(0, g["troops"] - int(loss * loss_mod))
            g["exp"] += 8
            g["morale"] = clamp(g["morale"] - 15, 0, 100)
            if get_skill(g["name"])["name"] == "遗计":
                city["garrison"] = max(1, city["garrison"] - random.randint(3, 8))
                self.log("【遗计】发动！敌方守军损兵。")

        city["garrison"] = max(1, city["garrison"] - random.randint(1, 3))
        self.resources["民心"] = clamp(self.resources["民心"] - 5, 0, 100)
        self.log(f"败！{'、'.join(names)} 进攻【{city['name']}】失利，士气受损。")
        messagebox.showwarning("失败 ✕", "进攻失败，损失惨重，士气下降。")

    def _check_level_up(self, g):
        threshold = g["level"] * 50
        if g["exp"] >= threshold:
            g["level"] += 1
            g["exp"] -= threshold
            g["force"] = min(100, g["force"] + 2)
            g["intellect"] = min(100, g["intellect"] + 2)
            g["command"] = min(100, g["command"] + 2)
            self.log(f"【{g['name']}】晋升 Lv{g['level']}！各项属性成长。")

    def _check_achievement(self, key):
        if key not in self.achievement:
            self.achievement.append(key)
            self.log(f"🏆 解锁成就：【{key}】")

    def try_capture_enemy(self):
        enemies = self.get_enemies_alive()
        if not enemies:
            return
        captive = random.choice(enemies)
        choice = messagebox.askyesno("俘获敌将",
            f"俘虏：【{captive['name']}】{captive['title']}\n"
            f"武:{captive['force']} 智:{captive['intellect']} 统:{captive['command']}\n\n"
            f"是否招降？（否则处斩）")
        if choice:
            captive["camp"] = "我方"
            captive["loyalty"] = 60
            captive["morale"] = 70
            self.log(f"【{captive['name']}】归降，已加入我方阵营！")
            self._check_achievement("招降敌将")
            messagebox.showinfo("招降成功", f"【{captive['name']}】已归降！")
        else:
            captive["alive"] = False
            self.log(f"【{captive['name']}】已被处斩。")

    def check_victory(self):
        ec = self.get_city("enemy_capital")
        return bool(ec and ec["owner"] == "我方")

    def _game_over(self, win):
        if win:
            msg = f"🎉 天下一统！\n历时 {self.turn} 回合，共取得 {self.victory_count} 场胜利。\n成就：{', '.join(self.achievement) or '无'}"
            messagebox.showinfo("天下一统", msg)
        else:
            messagebox.showwarning("游戏结束", "我方已无力抵抗，天下归于敌手。")
        self.root.destroy()

    # ═══════════════════════════════════════════════════════
    #  内政命令
    # ═══════════════════════════════════════════════════════
    def need_stamina(self, cost=1):
        if self.stamina < cost:
            self.log("体力不足。")
            messagebox.showwarning("体力不足", "体力不足，请先休整。")
            return False
        return True

    def spend_stamina(self, cost=1):
        self.stamina -= cost

    def recruit_soldiers(self):
        g = self.get_by_id(self.selected_general_id)
        if not g or g["camp"] != "我方" or not g["alive"]:
            messagebox.showwarning("提示", "请先选择一名我方武将。")
            return
        if not self.need_stamina():
            return
        cost_f, cost_m = 8, 3
        if self.resources["粮食"] < cost_f or self.resources["金钱"] < cost_m:
            self.log("资源不足。")
            messagebox.showwarning("提示", "资源不足，无法征兵。")
            return
        count = 5 + g["command"] // 20 + self.agriculture_lv
        self.spend_stamina()
        self.resources["粮食"] -= cost_f
        self.resources["金钱"] -= cost_m
        g["troops"] += count
        self.recalculate_armies()
        self.save_generals()
        self.log(f"{g['name']} 征得 {count} 兵。")
        self.refresh_after_action()

    def upgrade_commerce(self):
        if not self.need_stamina():
            return
        if self.resources["金钱"] < 20:
            messagebox.showwarning("提示", "金钱不足（需20）。")
            return
        self.spend_stamina()
        self.resources["金钱"] -= 20
        self.commerce_lv += 1
        self.log(f"商业升至 {self.commerce_lv} 级，金钱收入提升。")
        self.refresh_after_action()

    def upgrade_agriculture(self):
        if not self.need_stamina():
            return
        if self.resources["木材"] < 15:
            messagebox.showwarning("提示", "木材不足（需15）。")
            return
        self.spend_stamina()
        self.resources["木材"] -= 15
        self.agriculture_lv += 1
        self.log(f"农业升至 {self.agriculture_lv} 级，粮食产量提升。")
        self.refresh_after_action()

    def upgrade_security(self):
        if not self.need_stamina():
            return
        if self.resources["粮食"] < 10:
            messagebox.showwarning("提示", "粮食不足（需10）。")
            return
        self.spend_stamina()
        self.resources["粮食"] -= 10
        self.security_lv += 1
        self.log(f"治安升至 {self.security_lv} 级，民心+5。")
        self.resources["民心"] = clamp(self.resources["民心"] + 5, 0, 100)
        self.refresh_after_action()

    def repair_wall(self):
        if not self.need_stamina():
            return
        if self.resources["金钱"] < 30:
            messagebox.showwarning("提示", "金钱不足（需30）。")
            return
        self.spend_stamina()
        self.resources["金钱"] -= 30
        self.wall_lv += 1
        self.log(f"城墙修缮至 {self.wall_lv} 级。")
        self.refresh_after_action()

    def upgrade_tech(self):
        if not self.need_stamina():
            return
        cost_m = 30
        cost_f = 20
        if self.resources["金钱"] < cost_m or self.resources["粮食"] < cost_f:
            messagebox.showwarning("提示", f"需金钱{cost_m}、粮食{cost_f}。")
            return
        self.spend_stamina()
        self.resources["金钱"] -= cost_m
        self.resources["粮食"] -= cost_f
        self.tech_lv += 1
        self.log(f"科技突破！技术等级提升至 Lv{self.tech_lv}，攻击力+3%。")
        self.refresh_after_action()

    def send_spy(self):
        if not self.need_stamina():
            return
        if self.resources["金钱"] < 15:
            messagebox.showwarning("提示", "需金钱15以派遣间谍。")
            return
        if random.random() < 0.7:
            self.spend_stamina()
            self.resources["金钱"] -= 15
            self.spy_count += 1
            self.log(f"间谍成功潜入！当前间谍数：{self.spy_count}（下次攻城削弱敌守备15%）。")
        else:
            self.log("间谍行动失败，金钱损失。")
            self.resources["金钱"] -= 10
        self.refresh_after_action()

    def use_spy(self):
        if self.spy_count <= 0:
            messagebox.showinfo("提示", "当前没有可用间谍，请在内政界面派遣。")
            return
        target = [c for c in self.cities if c["owner"] == "敌方"]
        if not target:
            messagebox.showinfo("提示", "当前无敌方据点可渗透。")
            return
        city = random.choice(target)
        city["garrison"] = max(1, int(city["garrison"] * 0.8))
        self.spy_count -= 1
        self.log(f"间谍渗透【{city['name']}】，守军削减20%，现有{city['garrison']}兵。")
        self.update_city_visual(city)
        messagebox.showinfo("间谍行动", f"成功渗透【{city['name']}】！守军减少20%。\n剩余间谍：{self.spy_count}")
        self.refresh_header()

    def open_diplomacy(self):
        win = tk.Toplevel(self.root)
        win.title("外交谈判")
        win.geometry("420x340")
        win.configure(bg=self.C["panel"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="◈ 外交谈判", bg=self.C["panel2"], fg=self.C["gold"],
                 font=self.F["head"], pady=8).pack(fill="x")
        tk.Label(win, text="选择外交动作（消耗金钱50或粮食30）",
                 bg=self.C["panel"], fg=self.C["text2"], font=self.F["small"],
                 pady=4).pack()

        for opt in DIPLOMACY_OPTIONS:
            def action(o=opt):
                cost_type = "金钱" if o in ["结盟", "索要粮草"] else "粮食"
                cost = 50 if cost_type == "金钱" else 30
                if self.resources[cost_type] < cost:
                    messagebox.showwarning("资源不足", f"需{cost_type}{cost}。")
                    return
                self.resources[cost_type] -= cost
                result = random.choice(["成功", "失败", "拒绝"])
                bonus = ""
                if result == "成功":
                    if o == "索要粮草":
                        self.resources["粮食"] += 40
                        bonus = "获粮食40。"
                    elif o == "结盟":
                        bonus = "结盟成功，暂时提升民心。"
                        self.resources["民心"] = clamp(self.resources["民心"] + 10, 0, 100)
                self.log(f"外交【{o}】→ {result}。{bonus}")
                self.refresh_header()
                messagebox.showinfo("外交结果", f"【{o}】结果：{result}\n{bonus}")
                win.destroy()
            self.btn(win, opt, action, w=18).pack(pady=4)

        tk.Button(win, text="取消", command=win.destroy,
                  bg=self.C["btn"], fg=self.C["text2"], font=self.F["small"]).pack(pady=8)

    def open_general_upgrade(self):
        win = tk.Toplevel(self.root)
        win.title("武将强化")
        win.geometry("480x400")
        win.configure(bg=self.C["panel"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="◈ 武将强化", bg=self.C["panel2"], fg=self.C["gold"],
                 font=self.F["head"], pady=8).pack(fill="x")
        tk.Label(win, text="每次强化消耗金钱30，随机提升一名我方武将属性",
                 bg=self.C["panel"], fg=self.C["text2"], font=self.F["small"], pady=4).pack()

        lb = tk.Listbox(win, height=8, bg="#0a0806", fg=self.C["text"],
                        selectbackground=self.C["border2"], font=self.F["small"])
        lb.pack(fill="both", expand=True, padx=16, pady=8)
        friendlies = [g for g in self.generals if g["camp"] == "我方" and g["alive"]]
        for g in friendlies:
            lb.insert("end", f"{g['name']} Lv{g['level']}  武:{g['force']} 智:{g['intellect']} 统:{g['command']}")

        def do_upgrade():
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning("提示", "请选择武将。")
                return
            if self.resources["金钱"] < 30:
                messagebox.showwarning("提示", "金钱不足（需30）。")
                return
            g = friendlies[sel[0]]
            self.resources["金钱"] -= 30
            stat = random.choice(["force", "intellect", "command", "politics"])
            g[stat] = min(100, g[stat] + random.randint(2, 5))
            stat_cn = {"force":"武力","intellect":"智力","command":"统率","politics":"政治"}[stat]
            self.log(f"【{g['name']}】{stat_cn}强化 → 现为 {g[stat]}。")
            self.save_generals()
            self.refresh_header()
            messagebox.showinfo("强化成功", f"【{g['name']}】{stat_cn} 提升！")
            win.destroy()

        self.btn(win, "确认强化", do_upgrade, w=14, style="gold").pack(pady=4)
        tk.Button(win, text="取消", command=win.destroy,
                  bg=self.C["btn"], fg=self.C["text2"], font=self.F["small"]).pack(pady=2)

    def open_garrison_recruit(self):
        owned = [c for c in self.cities if c["owner"] == "我方" and c["id"] != "enemy_capital"]
        if not owned:
            messagebox.showinfo("提示", "暂无可征兵的我方据点。")
            return

        win = tk.Toplevel(self.root)
        win.title("据点征兵")
        win.geometry("460x360")
        win.configure(bg=self.C["panel"])
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="◈ 据点征兵", bg=self.C["panel2"], fg=self.C["gold"],
                 font=self.F["head"], pady=8).pack(fill="x")
        lb = tk.Listbox(win, height=8, bg="#0a0806", fg=self.C["text"],
                        selectbackground=self.C["border2"], font=self.F["small"])
        lb.pack(fill="both", expand=True, padx=16, pady=8)
        for c in owned:
            lb.insert("end", f"{c['name']}  类型:{c['type']}  驻军:{c['garrison']}")

        row = tk.Frame(win, bg=self.C["panel"])
        row.pack(fill="x", padx=16, pady=4)
        tk.Label(row, text="数量：", bg=self.C["panel"], fg=self.C["text"], font=self.F["small"]).pack(side="left")
        num_v = tk.StringVar(value="5")
        tk.Entry(row, textvariable=num_v, width=8, font=self.F["small"]).pack(side="left", padx=6)

        def do():
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning("提示", "请选择据点。")
                return
            try:
                n = int(num_v.get())
            except:
                messagebox.showwarning("提示", "请输入有效数字。")
                return
            city = owned[sel[0]]
            mx = 30 if city["type"] == "capital" else 20 if city["type"] == "city" else 10
            if n <= 0 or n > mx:
                messagebox.showwarning("提示", f"数量范围：1~{mx}")
                return
            fc, mc = n * 2, n
            if self.resources["粮食"] < fc or self.resources["金钱"] < mc:
                messagebox.showwarning("提示", "资源不足。")
                return
            self.resources["粮食"] -= fc
            self.resources["金钱"] -= mc
            city["garrison"] += n
            self.log(f"在【{city['name']}】征兵{n}，驻军增至{city['garrison']}。")
            self.save_generals()
            self.refresh_header()
            if self.mode == "battle" and hasattr(self, "canvas"):
                self.update_city_visual(city)
            messagebox.showinfo("成功", f"【{city['name']}】征兵完成。")
            win.destroy()

        self.btn(win, "确认征兵", do, w=14, style="gold").pack(pady=6)

    def rest(self):
        self.stamina = self.max_stamina
        self.current_date += timedelta(days=1)
        self.resources["粮食"] -= max(0, self.army_count // 10)
        self.log("全军休整，体力恢复满值。（消耗粮草）")
        self.refresh_after_action()

    def next_day(self):
        self.current_date += timedelta(days=1)
        self.turn += 1
        self.stamina = min(self.max_stamina, self.stamina + 2)
        self.resources["粮食"] += 6 + self.agriculture_lv * 2
        self.resources["金钱"] += 4 + self.commerce_lv * 2
        self.resources["木材"] += 2
        self.resources["民心"] = clamp(self.resources["民心"] + self.security_lv - 1, 0, 100)
        self.resources["粮食"] = max(0, self.resources["粮食"] - self.army_count // 15)

        if random.random() < 0.30:
            ev = random.choice(RANDOM_EVENTS)
            for k, v in ev["effect"].items():
                if k == "bonus_troops":
                    friendly = self.get_friendly()
                    if friendly:
                        g = random.choice(friendly)
                        g["troops"] += v
                        self.log(f"事件：{ev['text']} → {g['name']}获{v}兵。")
                else:
                    self.resources[k] = max(0, self.resources.get(k, 0) + v)
                    self.log(f"随机事件：{ev['text']}")

        if random.random() < 0.15:
            self._enemy_counterattack()

        self.weather = self.random_weather()
        self.save_generals()
        self.log(f"第 {self.turn} 日，天气：{self.weather}。")
        self.refresh_after_action()

    def _enemy_counterattack(self):
        my_cities = [c for c in self.cities if c["owner"] == "我方" and c["type"] != "capital"]
        if not my_cities:
            return
        target = random.choice(my_cities)
        atk = random.randint(10, 25)
        if atk > target["garrison"]:
            target["owner"] = "敌方"
            target["garrison"] = max(5, atk // 2)
            self.log(f"⚠ 敌军反攻！【{target['name']}】失守，敌方夺回据点！")
            if hasattr(self, "canvas"):
                self.update_city_visual(target)
            messagebox.showwarning("警报！", f"敌军反攻，我方【{target['name']}】失守！")
        else:
            target["garrison"] = max(1, target["garrison"] - atk // 3)
            self.log(f"敌军骚扰【{target['name']}】，守军抵御成功。")

    def enter_battle(self):
        if not self.need_stamina():
            return
        self.spend_stamina()
        self.current_date += timedelta(days=1)
        self.selected_general_ids = []
        self.show_battle()

    def refresh_after_action(self):
        self.recalculate_armies()
        self.save_generals()
        self.refresh_header()
        if self.mode == "battle":
            self.populate_general_list(battle=True)
        else:
            self.populate_general_list(battle=False)
            self.show_overview()


if __name__ == "__main__":
    root = tk.Tk()
    Game(root)
    root.mainloop()

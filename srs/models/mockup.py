"""Мокапы GUI в виде InterconnectionView SysML v2.

Части окна (part) рисуются прямоугольниками с заголовком «part» name : Type,
листовые части — элементами интерфейса своего типа из пакета GuiLib с подписью
name : Type, значения атрибутов (:>>) — содержимым элементов.
"""
import re

from PIL import Image, ImageDraw, ImageFont

S = 2
INK, MUTED, LINE, FILL = (24, 24, 24), (110, 110, 110), (70, 70, 70), (255, 255, 255)
SOFT, ACCENT, HL = (232, 236, 243), (212, 222, 238), (255, 241, 196)


def _font(size, style=""):
    name = {"": "segoeui.ttf", "b": "segoeuib.ttf", "i": "segoeuii.ttf"}[style]
    return ImageFont.truetype("C:/Windows/Fonts/" + name, size * S)


F_KW, F_HEAD, F_TEXT, F_SMALL, F_LBL, F_BIG = (_font(10, "i"), _font(12, "b"), _font(12), _font(11),
                                               _font(10, "i"), _font(17, "b"))
F_BOLD = _font(12, "b")


# ------------------------------------------------------------------ разбор --

class Part:
    def __init__(self, name, typ, parent=None):
        self.name, self.typ, self.parent = name, typ, parent
        self.attrs, self.children = {}, []

    def a(self, key, default=None):
        return self.attrs.get(key, default)


TOKEN = re.compile(r'"[^"]*"|:>>|[(){};:,=]|[^\s(){};:,="]+')


def parse(text, root_name):
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    toks = TOKEN.findall(text)
    i = 0

    def value():
        nonlocal i
        t = toks[i]
        if t == "(":
            i += 1
            out = []
            while toks[i] != ")":
                if toks[i] != ",":
                    out.append(value())
                else:
                    i += 1
            i += 1
            return out
        i += 1
        if t.startswith('"'):
            return t[1:-1]
        if t in ("true", "false"):
            return t == "true"
        return int(t) if t.isdigit() else t

    def part(parent):
        nonlocal i
        # part NAME : TYPE
        name, typ = toks[i + 1], toks[i + 3]
        p = Part(name, typ, parent)
        i += 4
        if toks[i] == ";":
            i += 1
            return p
        i += 1  # {
        while toks[i] != "}":
            t = toks[i]
            if t == "part":
                p.children.append(part(p))
            elif t == ":>>":
                key = toks[i + 1]
                i += 3
                v = value()
                p.attrs[key] = v if isinstance(v, list) or key not in ("weights", "highlight") else [v]
                i += 1  # ;
            else:
                while toks[i] != ";":
                    i += 1
                i += 1
        i += 1
        return p

    while i < len(toks):
        if toks[i] == "part" and toks[i + 1] == root_name and toks[i + 2] == ":":
            return part(None)
        i += 1
    raise SystemExit(f"часть {root_name} не найдена")


# --------------------------------------------------------------- рисование --

class Mock:
    def __init__(self):
        self.img = None
        self.d = ImageDraw.Draw(Image.new("RGB", (10, 10)))

    def tw(self, s, f):
        b = self.d.textbbox((0, 0), s, font=f)
        return (b[2] - b[0]) / S

    def rect(self, x, y, w, h, r=0, fill=FILL, outline=LINE, width=1):
        xy = [x * S, y * S, (x + w) * S, (y + h) * S]
        if r:
            self.d.rounded_rectangle(xy, r * S, fill=fill, outline=outline, width=width * S)
        else:
            self.d.rectangle(xy, fill=fill, outline=outline, width=width * S)

    def text(self, x, y, s, f=F_TEXT, fill=INK, anchor="la"):
        self.d.text((x * S, y * S), s, font=f, fill=fill, anchor=anchor)

    def line(self, pts, fill=LINE, width=1):
        self.d.line([(a * S, b * S) for a, b in pts], fill=fill, width=width * S)

    def wrap(self, s, w, f):
        out, cur = [], ""
        for word in s.split():
            t = (cur + " " + word).strip()
            if self.tw(t, f) <= w or not cur:
                cur = t
            else:
                out.append(cur)
                cur = word
        return out + ([cur] if cur else [])

    # ------------------------------------------------------------ размеры
    PAD, HEAD = 10, 40

    def boxed(self, p):
        """Часть рисуется рамкой «part», если это окно, контейнер или прямой потомок окна."""
        return p.parent is None or p.children or p.parent.typ == "Window"

    def leaf_h(self, p, w):
        t = p.typ
        if t == "Button" or t in ("ComboBox", "TextField"):
            return 30
        if t == "Label":
            return 28 if p.a("big") else 20
        if t == "Indicator":
            return 20
        if t == "Scale":
            return 22
        if t == "CheckBox":
            return 22
        if t == "Toggle":
            return 40
        if t == "Table":
            return 26 + 24 * len(p.a("rows", []))
        if t == "Note":
            return 17 * len(p.a("lines", []))
        if t == "Menu":
            return 28 * len(p.a("items", [])) + 4
        if t == "Notification":
            return 30 + 17 * len(self.wrap(p.a("text", ""), w - 60, F_TEXT)) + 10
        if t == "StatusBar":
            return 20
        if t == "TabBar":
            return 30
        return 24

    def leaf_w(self, p):
        t = p.typ
        if t == "Button":
            return self.tw(p.a("text", ""), F_TEXT) + 40
        if t == "Label":
            return self.tw(p.a("text", ""), F_BIG if p.a("big") else F_TEXT) + 4
        if t == "Indicator":
            return self.tw(p.a("text", ""), F_BOLD) + 24
        if t == "Scale":
            return 420
        if t == "Menu":
            return 210
        return None

    def h(self, p, w):
        if self.boxed(p):
            inner = w - 2 * self.PAD
            hh = self.HEAD + (20 if p.typ == "Window" else 0)
            if p.children:
                hh += self.content_h(p, inner)
            else:
                hh += self.leaf_h(p, inner) + 4
            return hh + self.PAD
        return 16 + self.leaf_h(p, w)

    def content_h(self, p, w):
        kids = p.children
        if p.a("layout") == "row":
            ws = self.row_widths(p, w)
            return max(self.h(k, kw) for k, kw in zip(kids, ws))
        return sum(self.h(k, self.col_w(p, k, w)) for k in kids) + 8 * (len(kids) - 1)

    def row_widths(self, p, w):
        kids = p.children
        weights = p.a("weights") or [1] * len(kids)
        gap = 10
        free = w - gap * (len(kids) - 1)
        return [free * k / sum(weights) for k in weights]

    def col_w(self, p, k, w):
        if p.a("layout") == "center" and not self.boxed(k):
            lw = self.leaf_w(k)
            return min(w, max(lw or w, self.tw(f"{k.name} : {k.typ}", F_LBL) + 4))
        return w

    # ------------------------------------------------------------ отрисовка
    def draw(self, p, x, y, w):
        hh = self.h(p, w)
        if self.boxed(p):
            top = p.parent is None
            self.rect(x, y, w, hh, r=0 if top else 8, width=2 if top else 1)
            self.text(x + w / 2, y + 5, "«part»", F_KW, MUTED, "ma")
            self.text(x + w / 2, y + 19, f"{p.name} : {p.typ}", F_HEAD, INK, "ma")
            cy = y + self.HEAD
            if p.typ == "Window":
                self.text(x + self.PAD, cy, f'caption = "{p.a("caption", "")}"', F_SMALL, MUTED)
                cy += 20
            inner = w - 2 * self.PAD
            if p.children:
                self.draw_content(p, x + self.PAD, cy, inner)
            else:
                self.widget(p, x + self.PAD, cy, inner)
        else:
            self.text(x, y, f"{p.name} : {p.typ}", F_LBL, MUTED)
            self.widget(p, x, y + 16, w)
        return hh

    def draw_content(self, p, x, y, w):
        kids = p.children
        if p.a("layout") == "row":
            cx = x
            for k, kw in zip(kids, self.row_widths(p, w)):
                self.draw(k, cx, y, kw)
                cx += kw + 10
            return
        for k in kids:
            kw = self.col_w(p, k, w)
            kx = x + (w - kw) / 2 if p.a("layout") == "center" else x
            y += self.draw(k, kx, y, kw) + 8

    def widget(self, p, x, y, w):
        t, a = p.typ, p.a
        if t == "Button":
            bw = w if p.parent.a("layout") == "row" else min(w, self.leaf_w(p))
            self.rect(x, y, bw, 30, r=6, fill=ACCENT if a("primary") else SOFT)
            self.text(x + bw / 2, y + 15, a("text", ""), F_BOLD if a("primary") else F_TEXT, INK, "mm")
        elif t == "Label":
            self.text(x, y + 2, a("text", ""), F_BIG if a("big") else F_TEXT)
        elif t == "Indicator":
            self.d.ellipse([(x + 2) * S, (y + 6) * S, (x + 12) * S, (y + 16) * S], fill=(46, 139, 87))
            self.text(x + 20, y + 11, a("text", ""), F_BOLD, INK, "lm")
        elif t == "Scale":
            n = 60
            for i in range(n + 1):
                tx = x + i * w / n
                hgt = 12 if i % 5 == 0 else 7
                col = (197, 33, 43) if i / n * 100 > a("progress", 0) else LINE
                self.line([(tx, y + 18 - hgt), (tx, y + 18)], col)
        elif t in ("ComboBox", "TextField"):
            self.rect(x, y, w, 30, r=4)
            txt = a("value") if t == "ComboBox" else a("placeholder", "")
            self.text(x + 10, y + 15, txt, F_TEXT, INK if t == "ComboBox" else MUTED, "lm")
            if t == "ComboBox":
                ax, ay = x + w - 16, y + 13
                self.d.polygon([(ax * S, ay * S), ((ax + 8) * S, ay * S), ((ax + 4) * S, (ay + 5) * S)], fill=INK)
        elif t == "CheckBox":
            self.rect(x, y + 3, 15, 15, r=2)
            if a("checked"):
                self.line([(x + 3, y + 10), (x + 7, y + 15), (x + 13, y + 5)], INK, 2)
            self.text(x + 22, y + 11, a("text", ""), F_TEXT, INK, "lm")
        elif t == "Toggle":
            self.text(x, y + 2, a("text", ""), F_TEXT)
            self.text(x, y + 21, a("hint", ""), F_SMALL, MUTED)
            sx = x + w - 46
            on = a("on")
            self.rect(sx, y + 8, 40, 22, r=11, fill=(60, 60, 60) if on else SOFT)
            cx = sx + (29 if on else 11)
            self.d.ellipse([(cx - 7) * S, (y + 12) * S, (cx + 7) * S, (y + 26) * S], fill=FILL)
        elif t == "Table":
            cols, rows = a("columns", []), a("rows", [])
            ws = a("widths") or [1] * len(cols)
            cw = [w * k / sum(ws) for k in ws]
            hl = set(a("highlight", []))
            self.rect(x, y, w, 26 + 24 * len(rows))
            self.rect(x, y, w, 26, fill=SOFT)
            for r_i, row in enumerate(rows, 1):
                ry = y + 2 + r_i * 24
                if r_i in hl:
                    self.rect(x + 1, ry, w - 2, 24, fill=HL, outline=HL)
                self.line([(x, ry), (x + w, ry)], (200, 200, 200))
            cx = x
            for c_i, col in enumerate(cols):
                if c_i:
                    self.line([(cx, y), (cx, y + 26 + 24 * len(rows))], (200, 200, 200))
                self.text(cx + 6, y + 13, col, F_BOLD, INK, "lm")
                for r_i, row in enumerate(rows, 1):
                    cell = row.split("|")[c_i]
                    ry = y + 2 + r_i * 24 + 12
                    if cell in ("[ ]", "[x]"):
                        bx = cx + cw[c_i] / 2 - 7
                        self.rect(bx, ry - 7, 14, 14, r=2)
                        if cell == "[x]":
                            self.line([(bx + 3, ry), (bx + 6, ry + 4), (bx + 11, ry - 4)], INK, 2)
                    else:
                        self.text(cx + 6, ry, cell, F_SMALL, INK, "lm")
                cx += cw[c_i]
        elif t == "Note":
            for i, s in enumerate(a("lines", [])):
                self.text(x, y + 1 + i * 17, s, F_SMALL, MUTED)
        elif t == "Menu":
            items = a("items", [])
            mw = min(w, self.leaf_w(p))
            self.rect(x, y, mw, 28 * len(items) + 4, r=4)
            for i, s in enumerate(items):
                self.text(x + 14, y + 16 + i * 28, s, F_TEXT, INK, "lm")
                if i:
                    self.line([(x + 6, y + 2 + i * 28), (x + mw - 6, y + 2 + i * 28)], (210, 210, 210))
        elif t == "Notification":
            hgt = self.leaf_h(p, w)
            self.rect(x, y, w, hgt, r=8, fill=(248, 248, 248))
            self.rect(x + 10, y + 10, 32, 32, r=6, fill=(197, 33, 43), outline=(197, 33, 43))
            self.text(x + 26, y + 26, "M", F_BOLD, FILL, "mm")
            self.text(x + 52, y + 8, a("title", ""), F_BOLD)
            for i, s in enumerate(self.wrap(a("text", ""), w - 60, F_TEXT)):
                self.text(x + 52, y + 28 + i * 17, s)
        elif t == "StatusBar":
            self.text(x, y + 2, a("text", ""), F_SMALL, INK)
        elif t == "TabBar":
            cx = x
            for i, s in enumerate(a("tabs", []), 1):
                tw_ = max(120, self.tw(s, F_TEXT) + 40)
                self.rect(cx, y, tw_, 30, r=4, fill=ACCENT if i == a("selected") else SOFT)
                self.text(cx + tw_ / 2, y + 15, s, F_TEXT, INK, "mm")
                cx += tw_ + 8

    def render(self, root, out_path, title, width=900):
        hgt = self.h(root, width)
        tab = f"view '{title}' [InterconnectionView]"
        W, H = width + 40, hgt + 64
        self.img = Image.new("RGB", (int(W * S), int(H * S)), FILL)
        self.d = ImageDraw.Draw(self.img)
        tw_ = self.tw(tab, F_HEAD) + 24
        self.rect(4, 4, W - 8, H - 8)
        self.d.polygon([(4 * S, 4 * S), ((4 + tw_ + 12) * S, 4 * S), ((4 + tw_) * S, 28 * S), (4 * S, 28 * S)],
                       outline=LINE, fill=FILL, width=S)
        self.text(14, 16, tab, F_HEAD, INK, "lm")
        self.draw(root, 20, 44, width)
        self.img.resize((int(W), int(H)), Image.LANCZOS).save(out_path, optimize=True)
        print("  ->", out_path)


def render(text, root_name, out_path, title):
    Mock().render(parse(text, root_name), out_path, title)

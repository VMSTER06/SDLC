"""Визуализация моделей SysML v2 (текстовая нотация) в PNG.

Скрипт разбирает подмножество SysML v2, которое используется в моделях
каталога srs/models, и рисует диаграммы в графической нотации SysML v2:
- interconnection — части и соединения (контекст, мокапы GUI, карта окон);
- usecase        — варианты использования с субъектом и акторами;
- requirement    — дерево требований (бизнес-цели);
- state          — диаграмма состояний;
- action         — диаграмма действий.

Каждая строка views.txt: <имя файла PNG> <вид> <файл .sysml> <короткое имя элемента>
[параметры]. Параметр row=<a,b> раскладывает дочерние части элемента a в строку,
pos=<имя:столбец:строка;...> задаёт размещение состояний.

Запуск: python render.py (из каталога srs/models), результат — ../images/*.png.
"""
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

S = 2  # рисуем с двойным разрешением и уменьшаем для сглаживания
HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "images"
FONT_DIR = Path("C:/Windows/Fonts")
INK, MUTED, FILL, HEAD, LINE = (24, 24, 24), (90, 90, 90), (255, 255, 255), (238, 241, 246), (60, 60, 60)


def font(size, bold=False, italic=False):
    name = "segoeuib.ttf" if bold else ("segoeuii.ttf" if italic else "segoeui.ttf")
    path = FONT_DIR / name
    if not path.exists():
        path = FONT_DIR / ("arialbd.ttf" if bold else "arial.ttf")
    return ImageFont.truetype(str(path), size * S)


F_KW, F_NAME, F_TEXT, F_SMALL = font(11, italic=True), font(13, bold=True), font(12), font(11)


# ---------------------------------------------------------------- разбор ----

class El:
    def __init__(self, kind, short=None, name=None, typ=None, parent=None):
        self.kind, self.short, self.name, self.typ, self.parent = kind, short, name, typ, parent
        self.children, self.attrs, self.connects, self.transitions, self.flow = [], {}, [], [], []
        self.doc = ""
        self.actors = []

    def find(self, short):
        if self.short == short:
            return self
        for c in self.children:
            r = c.find(short)
            if r:
                return r
        return None

    def child(self, short):
        return next((c for c in self.children if c.short == short), None)

    def resolve(self, path):
        cur = self
        for part in path.split("."):
            cur = cur.child(part) if cur else None
        return cur

    def label(self):
        return self.name or self.short or ""


DECL = re.compile(
    r"^(?P<kind>part def|part|use case def|requirement|state def|state|action def|action|item def|connection def)"
    r"\s*(?:<(?P<short>[^>]+)>)?\s*(?:'(?P<name>[^']*)')?\s*(?::\s*'(?P<typ>[^']*)')?\s*(?P<rest>.*)$")


def parse(text):
    # многострочный doc сворачивается в одну строку с маркером перевода строки
    text = re.sub(r"/\*(.*?)\*/", lambda m: "/*" + m.group(1).replace("\n", " ~~ ") + "*/", text, flags=re.S)
    root = El("root")
    stack = [root]
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        cur = stack[-1]
        if line.startswith("doc"):
            m = re.search(r"/\*(.*)\*/", line)
            if m:
                body = m.group(1).replace(" ~~ ", "\n")
                cur.doc = " ".join(s.strip(" *") for s in body.split("\n")).strip()
            continue
        if line == "}":
            stack.pop()
            continue
        if line.startswith("package"):
            el = El("package", name=line.split()[1], parent=cur)
            cur.children.append(el)
            stack.append(el)
            continue
        if line.startswith(("private import", "entry", "first start", "subject", "end part")):
            continue
        m = re.match(r"actor '([^']*)'", line)
        if m:
            cur.actors.append(m.group(1))
            continue
        m = re.match(r"attribute redefines '([^']*)'\s*=\s*\((.*)\);", line)
        if m:
            cur.attrs[m.group(1)] = re.findall(r'"([^"]*)"', m.group(2))
            continue
        if line.startswith("attribute"):
            continue
        m = re.match(r"(?:connection\s*(?:'(?P<lab>[^']*)')?\s*(?::\s*'(?P<typ>[^']*)')?\s*)?connect\s+(?P<a>[\w.]+)\s+to\s+(?P<b>[\w.]+);", line)
        if m:
            cur.connects.append((m.group("a"), m.group("b"), m.group("lab"), m.group("typ")))
            continue
        m = re.match(r"transition first (\w+) accept : '([^']*)' then (\w+);", line)
        if m:
            cur.transitions.append(m.groups())
            continue
        m = re.match(r"then action <(\w+)> '([^']*)';", line)
        if m:
            cur.flow.append(("action", m.group(1), m.group(2)))
            continue
        m = re.match(r"action <(\w+)> '([^']*)';", line)
        if m and cur.kind == "action def":
            cur.flow.append(("label", m.group(1), m.group(2)))
            continue
        if line.startswith("then decide"):
            cur.flow.append(("decide",))
            continue
        m = re.match(r"if '([^']*)'(?: and '([^']*)')? then (\w+);", line)
        if m:
            cur.flow.append(("if", m.group(1), m.group(3)))
            continue
        m = re.match(r"else (\w+);", line)
        if m:
            cur.flow.append(("else", m.group(1)))
            continue
        if line.startswith("then done"):
            cur.flow.append(("done",))
            continue
        m = DECL.match(line)
        if m:
            el = El(m.group("kind"), m.group("short"), m.group("name"), m.group("typ"), cur)
            cur.children.append(el)
            rest = m.group("rest")
            if rest.startswith("{") and not rest.endswith("}"):
                stack.append(el)
            continue
    return root


# --------------------------------------------------------------- рисование --

class Canvas:
    def __init__(self, w, h):
        self.img = Image.new("RGB", (w * S, h * S), FILL)
        self.d = ImageDraw.Draw(self.img)

    def box(self, x, y, w, h, r=0, fill=FILL, outline=INK, width=1, dash=False):
        xy = [x * S, y * S, (x + w) * S, (y + h) * S]
        if dash:
            self.d.rectangle(xy, fill=fill)
            for i in range(int(x), int(x + w), 10):
                self.line([(i, y), (min(i + 5, x + w), y)])
                self.line([(i, y + h), (min(i + 5, x + w), y + h)])
            for j in range(int(y), int(y + h), 10):
                self.line([(x, j), (x, min(j + 5, y + h))])
                self.line([(x + w, j), (x + w, min(j + 5, y + h))])
        elif r:
            self.d.rounded_rectangle(xy, r * S, fill=fill, outline=outline, width=width * S)
        else:
            self.d.rectangle(xy, fill=fill, outline=outline, width=width * S)

    def line(self, pts, fill=LINE, width=1):
        self.d.line([(px * S, py * S) for px, py in pts], fill=fill, width=width * S)

    def arrow(self, pts, fill=LINE, open_=True):
        self.line(pts, fill)
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        import math
        a = math.atan2(y2 - y1, x2 - x1)
        L = 10
        p1 = (x2 - L * math.cos(a - 0.45), y2 - L * math.sin(a - 0.45))
        p2 = (x2 - L * math.cos(a + 0.45), y2 - L * math.sin(a + 0.45))
        if open_:
            self.line([p1, (x2, y2), p2], fill)
        else:
            self.d.polygon([(p1[0] * S, p1[1] * S), (x2 * S, y2 * S), (p2[0] * S, p2[1] * S)], fill=fill)

    def text(self, x, y, s, f=F_TEXT, fill=INK, anchor="la"):
        self.d.text((x * S, y * S), s, font=f, fill=fill, anchor=anchor)

    def size(self, s, f=F_TEXT):
        b = self.d.textbbox((0, 0), s, font=f)
        return (b[2] - b[0]) / S, (b[3] - b[1]) / S

    def save(self, name):
        OUT.mkdir(exist_ok=True)
        w, h = self.img.size
        self.img.resize((w // S, h // S), Image.LANCZOS).save(OUT / name, optimize=True)
        print("  ->", OUT / name)


_probe = Canvas(10, 10)


def tw(s, f=F_TEXT):
    return _probe.size(s, f)[0]


def wrap(s, width, f=F_TEXT):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(t, f) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def header(c, x, y, w, kw, name, typ=None):
    c.text(x + w / 2, y + 6, "«" + kw + "»", F_KW, MUTED, "ma")
    yy = y + 22
    title = name + (" : " + typ if typ else "")
    for ln in wrap(title, w - 16, F_NAME):
        c.text(x + w / 2, yy, ln, F_NAME, INK, "ma")
        yy += 18
    return yy + 2


def header_h(w, name, typ=None):
    return 24 + 18 * len(wrap(name + (" : " + typ if typ else ""), w - 16, F_NAME)) + 4


def border_point(r, toward):
    x, y, w, h = r
    cx, cy = x + w / 2, y + h / 2
    tx, ty = toward
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    sx = (w / 2) / abs(dx) if dx else 1e9
    sy = (h / 2) / abs(dy) if dy else 1e9
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s


def edge_label(c, p1, p2, s, f=F_SMALL):
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    w, h = c.size(s, f)
    c.box(mx - w / 2 - 3, my - h / 2 - 4, w + 6, h + 8, outline=FILL)
    c.text(mx, my, s, f, MUTED, "mm")


# ------------------------------------------------------------ interconnection

def chips(c, x, y, w, values, table=False):
    """Значения атрибута: кнопки/пункты — «плашки», столбцы таблицы — ячейки."""
    if table:
        cw = w / len(values)
        c.box(x, y, w, 26, fill=HEAD, outline=LINE)
        for i, v in enumerate(values):
            if i:
                c.line([(x + i * cw, y), (x + i * cw, y + 26)])
            c.text(x + i * cw + cw / 2, y + 13, v if tw(v, F_SMALL) < cw - 4 else v.split(",")[0], F_SMALL, INK, "mm")
        for k in range(3):
            c.box(x, y + 26 + k * 22, w, 22, outline=(180, 180, 180))
        return 26 + 66 + 6
    cx, cy, rowh = x, y, 26
    for v in values:
        vw = tw(v, F_SMALL) + 20
        if cx + vw > x + w and cx > x:
            cx, cy = x, cy + rowh + 4
        c.box(cx, cy, vw, rowh, r=12, fill=HEAD, outline=LINE)
        c.text(cx + vw / 2, cy + rowh / 2, v, F_SMALL, INK, "mm")
        cx += vw + 6
    return cy - y + rowh + 6


def chips_h(w, values, table=False):
    if table:
        return 26 + 66 + 6
    cx, rows = 0, 1
    for v in values:
        vw = tw(v, F_SMALL) + 20
        if cx + vw > w and cx > 0:
            cx, rows = 0, rows + 1
        cx += vw + 6
    return rows * 30 + 6


class Layout:
    def __init__(self, rows):
        self.rows = rows  # множество элементов, дети которых идут в строку
        self.rects = {}

    def measure(self, el, w):
        pad = 10
        h = header_h(w, el.label(), el.typ)
        for name, vals in el.attrs.items():
            h += chips_h(w - 2 * pad, vals, name == "столбцы")
        kids = [k for k in el.children if k.kind == "part"]
        if kids:
            if el in self.rows:
                cw = (w - pad * (len(kids) + 1)) / len(kids)
                h += max(self.measure(k, cw) for k in kids) + pad
            else:
                for k in kids:
                    h += self.measure(k, w - 2 * pad) + pad
        return max(h, 46)

    def draw(self, c, el, x, y, w, top=False):
        pad = 10
        h = self.measure(el, w)
        c.box(x, y, w, h, r=0 if top else 6, width=2 if top else 1)
        yy = header(c, x, y, w, "part", el.label(), el.typ)
        for name, vals in el.attrs.items():
            yy += chips(c, x + pad, yy, w - 2 * pad, vals, name == "столбцы")
        kids = [k for k in el.children if k.kind == "part"]
        if el in self.rows and kids:
            cw = (w - pad * (len(kids) + 1)) / len(kids)
            for i, k in enumerate(kids):
                self.draw(c, k, x + pad + i * (cw + pad), yy, cw)
        else:
            for k in kids:
                self.draw(c, k, x + pad, yy, w - 2 * pad)
                yy += self.measure(k, w - 2 * pad) + pad
        self.rects[el] = (x, y, w, h)
        return h


def connections(c, el, lay):
    for a, b, lab, typ in el.connects:
        ea, eb = el.resolve(a), el.resolve(b)
        if not ea or not eb or ea not in lay.rects or eb not in lay.rects:
            continue
        ra, rb = lay.rects[ea], lay.rects[eb]
        ca = (ra[0] + ra[2] / 2, ra[1] + ra[3] / 2)
        cb = (rb[0] + rb[2] / 2, rb[1] + rb[3] / 2)
        # соединение рисуется по правому краю, чтобы не закрывать содержимое
        if abs(ca[0] - cb[0]) < 40 and typ:
            xr = max(ra[0] + ra[2], rb[0] + rb[2]) + 14
            y1, y2 = ca[1], cb[1]
            c.line([(ra[0] + ra[2], y1), (xr, y1), (xr, y2), (rb[0] + rb[2], y2)], width=1)
            s = ": " + typ
            c.d.text(((xr + 4) * S, (y1 + y2) / 2 * S), s, font=F_SMALL, fill=MUTED, anchor="lm")
        elif not typ and not lab:
            p1, p2 = border_point(ra, cb), border_point(rb, ca)
            c.line([p1, p2], fill=(150, 150, 150))
        else:
            p1, p2 = border_point(ra, cb), border_point(rb, ca)
            c.line([p1, p2])
            edge_label(c, p1, p2, lab or (": " + typ))
    for k in el.children:
        connections(c, k, lay)


def typed_margin(el):
    m = 0
    for a, b, lab, typ in el.connects:
        if typ:
            m = max(m, tw(": " + typ, F_SMALL) + 30)
    for k in el.children:
        m = max(m, typed_margin(k))
    return m


def render_mockup(el, out, rows=(), width=760):
    lay = Layout({el.resolve(r) if r != el.short else el for r in rows} - {None})
    margin = typed_margin(el)
    h = lay.measure(el, width)
    c = Canvas(int(width + 40 + margin), int(h + 40))
    lay.draw(c, el, 20, 20, width, top=True)
    connections(c, el, lay)
    c.save(out)


def render_context(el, out):
    kids = [k for k in el.children if k.kind == "part"]
    degree = {k: 0 for k in kids}
    for a, b, _, _ in el.connects:
        for n in (a, b):
            k = el.child(n)
            if k:
                degree[k] += 1
    hub = max(kids, key=lambda k: degree[k])
    others = [k for k in kids if k is not hub]
    left = [k for k in others if any(el.child(a) is k for a, b, _, _ in el.connects if el.child(b) is hub)]
    right = [k for k in others if k not in left]
    bw, bh, gap = 230, 74, 26
    n = max(len(left), len(right), 1)
    H = n * bh + (n - 1) * gap + 140
    W = 3 * bw + 2 * 230 + 40
    c = Canvas(W, H)
    c.box(10, 10, W - 20, H - 20, width=2)
    header(c, 10, 10, W - 20, "part", el.label())
    rects = {}

    def column(items, x):
        total = len(items) * bh + (len(items) - 1) * gap
        y0 = 70 + (H - 90 - total) / 2
        for i, k in enumerate(items):
            rects[k] = (x, y0 + i * (bh + gap), bw, bh)

    column(left, 30)
    column(right, W - 30 - bw)
    rects[hub] = (W / 2 - bw / 2, 70 + (H - 90 - 120) / 2, bw, 120)
    for k, (x, y, w, h) in rects.items():
        c.box(x, y, w, h, r=6, width=2 if k is hub else 1)
        header(c, x, y, w, "part", k.label(), k.typ)
    for a, b, lab, _ in el.connects:
        ra, rb = rects[el.child(a)], rects[el.child(b)]
        ca = (ra[0] + ra[2] / 2, ra[1] + ra[3] / 2)
        cb = (rb[0] + rb[2] / 2, rb[1] + rb[3] / 2)
        p1, p2 = border_point(ra, cb), border_point(rb, ca)
        c.line([p1, p2])
        if lab:
            edge_label(c, p1, p2, lab)
    c.save(out)


def render_navigation(el, out):
    kids = [k for k in el.children if k.kind == "part"]
    pos = {"w0": (0, 1), "w1": (1, 1), "w2": (2, 0), "w3": (3, 0), "w4": (2, 2)}
    bw, bh, gx, gy = 200, 70, 70, 50
    W = 4 * bw + 3 * gx + 80
    H = 3 * bh + 2 * gy + 120
    c = Canvas(W, H)
    c.box(10, 10, W - 20, H - 20, width=2)
    header(c, 10, 10, W - 20, "part", el.label())
    rects = {}
    for k in kids:
        col, row = pos.get(k.short, (0, 0))
        rects[k] = (40 + col * (bw + gx), 70 + row * (bh + gy), bw, bh)
        c.box(*rects[k], r=6)
        header(c, *rects[k][:3], "part", k.label())
    seen = set()
    for a, b, _, _ in el.connects:
        ra, rb = rects[el.child(a)], rects[el.child(b)]
        ca = (ra[0] + ra[2] / 2, ra[1] + ra[3] / 2)
        cb = (rb[0] + rb[2] / 2, rb[1] + rb[3] / 2)
        off = 8 if (b, a) in seen else (-8 if any(x == b and y == a for x, y, _, _ in el.connects) else 0)
        seen.add((a, b))
        import math
        ang = math.atan2(cb[1] - ca[1], cb[0] - ca[0]) + math.pi / 2
        ox, oy = off * math.cos(ang), off * math.sin(ang)
        p1 = border_point(ra, (cb[0] + ox, cb[1] + oy))
        p2 = border_point(rb, (ca[0] + ox, ca[1] + oy))
        c.arrow([(p1[0] + ox, p1[1] + oy), (p2[0] + ox, p2[1] + oy)])
    c.save(out)


# ----------------------------------------------------------------- use case

def render_usecases(pkg, out):
    ucs = [k for k in pkg.children if k.kind == "use case def"]
    actors = []
    for u in ucs:
        for a in u.actors:
            if a not in actors:
                actors.append(a)
    ew, eh, gap = 380, 56, 18
    H = len(ucs) * (eh + gap) + 150
    W = 980
    c = Canvas(W, H)
    sx, sy, sw, sh = 260, 20, ew + 80, H - 40
    c.box(sx, sy, sw, sh, width=2)
    header(c, sx, sy, sw, "subject", "ПО Murik DNS")
    centers = {}
    for i, u in enumerate(ucs):
        x, y = sx + 40, sy + 70 + i * (eh + gap)
        c.d.ellipse([x * S, y * S, (x + ew) * S, (y + eh) * S], outline=INK, width=S, fill=FILL)
        lines = wrap(u.label(), ew - 50, F_TEXT)
        for j, ln in enumerate(lines):
            c.text(x + ew / 2, y + eh / 2 + (j - (len(lines) - 1) / 2) * 16, ln, F_TEXT, INK, "mm")
        centers[u] = (x, y + eh / 2, x + ew, y + eh / 2)
    apos = {}
    for i, a in enumerate(actors):
        side = 0 if i == 0 else 1
        users = [u for u in ucs if a in u.actors]
        ay = sum(centers[u][1] for u in users) / len(users)
        ax = 120 if side == 0 else W - 120
        apos[a] = (ax, ay, side)
        d = c.d
        d.ellipse([(ax - 12) * S, (ay - 46) * S, (ax + 12) * S, (ay - 22) * S], outline=INK, width=S)
        c.line([(ax, ay - 22), (ax, ay + 10)], INK)
        c.line([(ax - 20, ay - 10), (ax + 20, ay - 10)], INK)
        c.line([(ax, ay + 10), (ax - 16, ay + 34)], INK)
        c.line([(ax, ay + 10), (ax + 16, ay + 34)], INK)
        c.text(ax, ay - 74, "«actor»", F_KW, MUTED, "ma")
        for j, ln in enumerate(wrap(a, 200, F_NAME)):
            c.text(ax, ay + 40 + j * 17, ln, F_NAME, INK, "ma")
    for u in ucs:
        for a in u.actors:
            ax, ay, side = apos[a]
            x1, y, x2, _ = centers[u]
            c.line([(ax + (24 if side == 0 else -24), ay - 4), (x1 if side == 0 else x2, y)])
    c.save(out)


# -------------------------------------------------------------- requirement

def render_requirements(el, out):
    kids = [k for k in el.children if k.kind == "requirement"]
    bw, gap = 250, 20
    cols = len(kids)
    W = cols * bw + (cols + 1) * gap
    bodies = [wrap(k.doc, bw - 20, F_TEXT) for k in kids]
    bh = max(header_h(bw, k.label()) + 26 + 17 * len(b) for k, b in zip(kids, bodies)) + 10
    H = 100 + 70 + bh + 30
    c = Canvas(W, H)
    tw_ = 360
    tx, ty = W / 2 - tw_ / 2, 20
    c.box(tx, ty, tw_, 70, width=2)
    header(c, tx, ty, tw_, "requirement", el.label())
    # знак вложенности (круг с крестом) у родителя
    cx, cy = W / 2, ty + 70 + 8
    c.d.ellipse([(cx - 8) * S, (cy - 8) * S, (cx + 8) * S, (cy + 8) * S], outline=INK, width=S, fill=FILL)
    c.line([(cx - 8, cy), (cx + 8, cy)], INK)
    c.line([(cx, cy - 8), (cx, cy + 8)], INK)
    by = 170
    c.line([(cx, cy + 8), (cx, by - 30)])
    c.line([(gap + bw / 2, by - 30), (W - gap - bw / 2, by - 30)])
    for i, (k, body) in enumerate(zip(kids, bodies)):
        x = gap + i * (bw + gap)
        c.line([(x + bw / 2, by - 30), (x + bw / 2, by)])
        c.box(x, by, bw, bh)
        yy = header(c, x, by, bw, "requirement", k.label())
        c.line([(x, yy), (x + bw, yy)])
        c.text(x + 10, yy + 5, "doc", F_KW, MUTED)
        for j, ln in enumerate(body):
            c.text(x + 10, yy + 24 + j * 17, ln, F_TEXT)
    c.save(out)


# ------------------------------------------------------------------- state

def render_states(sm, out, pos):
    states = [k for k in sm.children if k.kind == "state"]
    bw, bh, gx, gy = 190, 64, 150, 90
    cols = max(p[0] for p in pos.values()) + 1
    rows = max(p[1] for p in pos.values()) + 1
    W = cols * bw + (cols - 1) * gx + 160
    H = rows * bh + (rows - 1) * gy + 130
    c = Canvas(W, H)
    c.box(10, 10, W - 20, H - 20, r=10, width=2)
    header(c, 10, 10, W - 20, "state def", sm.label())
    rects = {}
    for s in states:
        col, row = pos[s.short]
        rects[s.short] = (90 + col * (bw + gx), 80 + row * (bh + gy), bw, bh)
        c.box(*rects[s.short], r=16)
        c.text(rects[s.short][0] + bw / 2, rects[s.short][1] + bh / 2, s.label(), F_NAME, INK, "mm")
    # начальное псевдосостояние
    r0 = rects[sm.transitions[0][0]] if False else rects[states[0].short]
    ix, iy = r0[0] - 50, r0[1] + bh / 2
    c.d.ellipse([(ix - 8) * S, (iy - 8) * S, (ix + 8) * S, (iy + 8) * S], fill=INK)
    c.arrow([(ix + 8, iy), (r0[0], iy)], INK, open_=False)
    pairs = {}
    for a, trig, b in sm.transitions:
        pairs.setdefault(frozenset((a, b)), []).append((a, trig, b))
    import math
    for key, items in pairs.items():
        for idx, (a, trig, b) in enumerate(items):
            ra, rb = rects[a], rects[b]
            ca = (ra[0] + bw / 2, ra[1] + bh / 2)
            cb = (rb[0] + bw / 2, rb[1] + bh / 2)
            off = 0 if len(items) == 1 else (14 if idx == 0 else -14)
            if len(items) > 1 and a > b:
                off = -off
            ang = math.atan2(cb[1] - ca[1], cb[0] - ca[0]) + math.pi / 2
            ox, oy = off * math.cos(ang), off * math.sin(ang)
            p1 = border_point(ra, (cb[0] + ox, cb[1] + oy))
            p2 = border_point(rb, (ca[0] + ox, ca[1] + oy))
            p1, p2 = (p1[0] + ox, p1[1] + oy), (p2[0] + ox, p2[1] + oy)
            c.arrow([p1, p2], INK, open_=False)
            lab = "accept " + trig
            lines = wrap(lab, 150, F_SMALL)
            mx = p1[0] + (p2[0] - p1[0]) * 0.5 + ox * 1.6
            my = p1[1] + (p2[1] - p1[1]) * 0.5 + oy * 1.6
            hgt = len(lines) * 15
            wmax = max(tw(l, F_SMALL) for l in lines)
            c.box(mx - wmax / 2 - 3, my - hgt / 2 - 2, wmax + 6, hgt + 4, outline=FILL)
            for j, ln in enumerate(lines):
                c.text(mx, my - hgt / 2 + j * 15 + 7, ln, F_SMALL, MUTED, "mm")
    c.save(out)


# ------------------------------------------------------------------ action

def render_action(ad, out):
    bw = 520
    steps, labels, branch = [], {}, None
    for item in ad.flow:
        if item[0] == "label":
            labels[item[1]] = item[2]
    seq, cur = [], None
    flow = ad.flow
    i = 0
    main = []
    while i < len(flow) and flow[i][0] != "decide":
        if flow[i][0] == "action":
            main.append(flow[i][2])
        i += 1
    guard = next(f for f in flow if f[0] == "if")
    els = next(f for f in flow if f[0] == "else")
    # ветви: после метки идут then action ... then done
    branches = {}
    curb = None
    for f in flow:
        if f[0] == "label":
            curb = f[1]
            branches[curb] = [f[2]]
        elif f[0] == "action" and curb:
            branches[curb].append(f[2])
        elif f[0] == "done":
            curb = None
    yes, no = branches[guard[2]], branches[els[1]]

    def bh(s, w=bw):
        return 18 * len(wrap(s, w - 30)) + 24

    W = bw + 360
    H = 80 + sum(bh(s) + 34 for s in main) + 90 + sum(bh(s) + 34 for s in yes) + 80
    c = Canvas(int(W), int(H))
    c.box(10, 10, W - 20, H - 20, r=10, width=2)
    header(c, 10, 10, W - 20, "action def", ad.label())
    x0, y = 40, 70
    cx = x0 + bw / 2
    c.d.ellipse([(cx - 9) * S, (y) * S, (cx + 9) * S, (y + 18) * S], fill=INK)
    y += 18

    def node(x, y, w, s):
        h = bh(s, w)
        c.box(x, y, w, h, r=12)
        lines = wrap(s, w - 30)
        for j, ln in enumerate(lines):
            c.text(x + w / 2, y + 12 + j * 18 + 9, ln, F_TEXT, INK, "mm")
        return h

    for s in main:
        c.arrow([(cx, y), (cx, y + 30)])
        y += 30
        y += node(x0, y, bw, s)
    c.arrow([(cx, y), (cx, y + 26)])
    y += 26
    d = 22
    c.d.polygon([(cx * S, y * S), ((cx + d) * S, (y + d) * S), (cx * S, (y + 2 * d) * S), ((cx - d) * S, (y + d) * S)],
                outline=INK, fill=FILL, width=S)
    dy = y + d
    y += 2 * d
    c.text(cx + 8, y + 4, "[" + guard[1] + "]", F_SMALL, MUTED)
    nx, nw = x0 + bw + 40, W - (x0 + bw + 40) - 30
    c.line([(cx + d, dy), (nx + nw / 2, dy)])
    c.text(cx + d + 8, dy - 18, "[else]", F_SMALL, MUTED)
    c.arrow([(nx + nw / 2, dy), (nx + nw / 2, dy + 40)])
    nh = node(nx, dy + 40, nw, no[0])
    ny_end = dy + 40 + nh
    for s in yes:
        c.arrow([(cx, y), (cx, y + 30)])
        y += 30
        y += node(x0, y, bw, s)
    c.arrow([(cx, y), (cx, y + 30)])
    y += 30
    for r, f in ((11, None), (6, INK)):
        c.d.ellipse([(cx - r) * S, (y + 11 - r) * S, (cx + r) * S, (y + 11 + r) * S], outline=INK, width=S, fill=f)
    c.line([(nx + nw / 2, ny_end), (nx + nw / 2, y + 11)])
    c.arrow([(nx + nw / 2, y + 11), (cx + 12, y + 11)])
    c.save(out)


# -------------------------------------------------------------------- main

def main():
    files = {}
    for line in (HERE / "views.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out, view, src, short, *opts = line.split()
        opts = dict(o.split("=", 1) for o in opts)
        if src not in files:
            files[src] = parse((HERE / src).read_text(encoding="utf-8"))
        root = files[src]
        el = root.find(short) if short != "-" else root.children[0]
        if el is None:
            sys.exit(f"{src}: элемент <{short}> не найден")
        print(out, view, src, short)
        if view == "interconnection":
            render_mockup(el, out, opts.get("row", "").split(",") if "row" in opts else ())
        elif view == "context":
            render_context(el, out)
        elif view == "navigation":
            render_navigation(el, out)
        elif view == "usecase":
            render_usecases(el, out)
        elif view == "requirement":
            render_requirements(el, out)
        elif view == "state":
            pos = {k: tuple(map(int, v.split(":"))) for k, v in
                   (p.split(":", 1) for p in opts["pos"].split(";"))}
            render_states(el, out, pos)
        elif view == "action":
            render_action(el, out)


if __name__ == "__main__":
    main()

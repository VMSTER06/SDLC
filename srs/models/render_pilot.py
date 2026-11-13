"""Проверка моделей и визуализация эталонной реализацией SysML v2 Pilot Implementation.

Ядро jupyter-sysml-kernel (релиз 2026-09.1) запускается без Jupyter через jupyter_client:
все файлы *.sysml загружаются в одно ядро (ошибки разбора выводятся), затем для строк
pilot-views.txt выполняется команда %viz, а полученный SVG сохраняется в PNG.

Переменные окружения:
  SYSML_PILOT — каталог распакованного ядра (содержит jupyter-sysml-kernel-*-all.jar и sysml.library);
  JAVA21      — путь к java.exe версии 21 и выше (по умолчанию java из PATH).
Зависимости Python: jupyter_client, cairosvg.

Запуск: python render_pilot.py (из каталога srs/models).
"""
import json
import os
import sys
import tempfile
from pathlib import Path

import cairosvg
from jupyter_client import KernelManager

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "images"


def start_kernel():
    pilot = Path(os.environ["SYSML_PILOT"])
    spec_root = Path(tempfile.mkdtemp())
    spec = spec_root / "kernels" / "sysml"
    spec.mkdir(parents=True)
    (spec / "kernel.json").write_text(json.dumps({
        "argv": [os.environ.get("JAVA21", "java"), "-Xmx2g", "-cp", str(pilot / "*"),
                 "org.omg.sysml.jupyter.kernel.ISysML", "{connection_file}"],
        "display_name": "SysML", "language": "sysml",
        "env": {"ISYSML_LIBRARY_PATH": str(pilot / "sysml.library")}}), encoding="utf-8")
    os.environ["JUPYTER_PATH"] = str(spec_root)
    km = KernelManager(kernel_name="sysml")
    km.start_kernel()
    kc = km.client()
    kc.start_channels()
    kc.wait_for_ready(timeout=180)
    return km, kc


def execute(kc, code):
    msg_id = kc.execute(code)
    result = []
    while True:
        m = kc.get_iopub_msg(timeout=300)
        if m["parent_header"].get("msg_id") != msg_id:
            continue
        t, c = m["msg_type"], m["content"]
        if t in ("execute_result", "display_data"):
            result.append(c["data"])
        elif t == "stream":
            result.append({"text/plain": c["text"]})
        elif t == "error":
            result.append({"error": c.get("evalue", "")})
        elif t == "status" and c["execution_state"] == "idle":
            return result


def main():
    km, kc = start_kernel()
    errors = 0
    try:
        for f in sorted(HERE.glob("*.sysml")):
            res = execute(kc, f.read_text(encoding="utf-8"))
            text = " ".join(r.get("text/plain", "") for r in res)
            bad = [r["error"] for r in res if "error" in r] or (["ERROR"] if "ERROR" in text else [])
            errors += bool(bad)
            print(f"{f.name}: {'ошибки: ' + str(bad) if bad else 'OK – ' + text.strip()}")
        for line in (HERE / "pilot-views.txt").read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            png, width, command = line.split(maxsplit=2)
            svg = next((r["image/svg+xml"] for r in execute(kc, command) if "image/svg+xml" in r), None)
            if svg is None:
                print(f"{png}: %viz не вернул изображение")
                errors += 1
                continue
            cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(OUT / png),
                             output_width=int(width), background_color="white")
            print(f"{png}: {command}")
    finally:
        kc.stop_channels()
        km.shutdown_kernel(now=True)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()

"""UltraRAG 仓的门禁适配器（GHA 那条腿，卡 E156）。

跟 fw / dsh 那两份的差别只有三处，都是实测出来的：
  1. pip install -q faiss-cpu：上游把它放在 optional extra retriever 里，而 workflow 的
     pip install -e . 不带 extra ⇒ 不装的话 tests/servers/retriever 里那条会用
     importorskip 跳过。「配不上就跳过」不算读数，所以要显式装。
  2. 子进程带 -X utf8 且 PYTHONUTF8=1：tests/servers/evaluation/test_normalize_text.py
     用默认编码 read_text()，非 UTF-8 locale 上会 UnicodeDecodeError。
  3. 本仓的 conftest 是**新建**的（源仓没有 conftest.py），所以垫片由构建器写进树根。

文件名钉死在 tests/test_windows_autostart_e2e.py：镜像仓的 workflow 是冻结的模板，
最后一步写死 python -m pytest -q tests/test_windows_autostart_e2e.py。
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
READING = os.path.join(ROOT, ".pipe", "gha_reading.json")
BEGIN = "=== GHA-GATE-READING-BEGIN ==="
END = "=== GHA-GATE-READING-END ==="
GUARD = "GHA_GATE_ADAPTER"

#: 上游是 optional extra，不装就 importorskip —— 跳过不算读数。
EXTRAS = ("faiss-cpu",)

WORDS = (("passed", "passed"), ("failed", "failed"), ("error", "errors"),
         ("skipped", "skipped"), ("xfailed", "xfailed"), ("xpassed", "xpassed"))


def _parse(text):
    out = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0,
           "xfailed": 0, "xpassed": 0, "red": []}
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("FAILED ") or s.startswith("ERROR "):
            parts = s.split()
            if len(parts) > 1:
                out["red"].append(parts[1])
    tail = [ln for ln in text.splitlines()
            if " in " in ln and ("passed" in ln or "failed" in ln or "error" in ln)]
    if not tail:
        return out
    head = tail[-1].rsplit(" in ", 1)[0]
    for part in head.split(","):
        part = part.strip()
        for word, key in WORDS:
            if part.endswith(word):
                digits = part[:-len(word)].strip()
                if digits.isdigit():
                    out[key] = int(digits)
                break
    return out


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def test_ultrarag_suite_on_github_actions():
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return
    if os.environ.get(GUARD):
        return
    env = dict(os.environ)
    env[GUARD] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env.pop("PYTEST_ADDOPTS", None)

    extras_rc = 0
    extras_out = ""
    if EXTRAS:
        ex = subprocess.run([sys.executable, "-X", "utf8", "-m", "pip", "install", "-q"]
                            + list(EXTRAS),
                            cwd=ROOT, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", env=env)
        extras_rc = ex.returncode
        extras_out = ((ex.stdout or "") + (ex.stderr or ""))[-3000:]
        print("----- extras install (tail) -----", flush=True)
        print(extras_out, flush=True)

    argv = [sys.executable, "-X", "utf8", "-m", "pytest", "-q", "-o", "addopts=",
            "-p", "no:cacheprovider", "--ignore", os.path.abspath(__file__), "tests"]
    # ★ env 必须显式传进去：runner 上默认 codepage 是 cp1252，子进程不继承这里的
    # PYTHONIOENCODING 就会在打印中文时 UnicodeEncodeError（实测：framework 6 条 CLI 用例全红）。
    proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=env)
    merged = (proc.stdout or "") + chr(10) + (proc.stderr or "")
    reading = {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "at": _now(),
        "python": ".".join(str(x) for x in sys.version_info[:3]),
        "cwd": ROOT,
        "suite": "tests",
        "extras": list(EXTRAS),
        "extras_rc": extras_rc,
    }
    reading.update(_parse(merged))
    # ok 只由 rc / failed / errors 决定：extras 装不上但测试仍然全绿时它是真的绿。
    if reading["failed"] or reading["errors"]:
        reading["ok"] = False

    print("----- UltraRAG suite output (tail) -----", flush=True)
    print(merged[-6000:], flush=True)
    os.makedirs(os.path.dirname(READING), exist_ok=True)
    with open(READING, "w", encoding="utf-8", newline=chr(10)) as fh:
        fh.write(json.dumps(reading, ensure_ascii=False, indent=2) + chr(10))
    print("[reading-hook] wrote " + READING, flush=True)
    blob = json.dumps(reading, ensure_ascii=False, sort_keys=True)
    print(BEGIN, flush=True)
    print(blob, flush=True)
    print(END, flush=True)
    assert reading["ok"], "UltraRAG 测试没全绿：" + merged[-2000:]

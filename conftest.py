# GHA-READING-HOOK
# 由 scripts/cloud/gha/build_snapshot.py 追加到快照的 conftest.py 末尾（卡 E156）。
# 为什么需要它：适配器把读数写进 .pipe/gha_reading.json，但 pytest 只在**失败**时打
# Captured stdout —— 全绿那趟作业日志里一条 GHA-GATE 都不会有。这个钩子在 capture 之外
# 原样重打三行，于是「绿了」也有读数可查。


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    import json
    import os

    root = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(root, ".pipe", "gha_reading.json")
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as fh:
        blob = fh.read().strip()
    if not blob.startswith("{"):
        return
    try:
        data = json.loads(blob)
    except ValueError:
        return
    if not data.get("ok"):
        # 失败那趟适配器自己已经通过 captured stdout 打过一块；再打一遍只会让日志含糊
        return
    for line in ("=== GHA-GATE-READING-BEGIN ===", blob, "=== GHA-GATE-READING-END ==="):
        terminalreporter.write_line(line)

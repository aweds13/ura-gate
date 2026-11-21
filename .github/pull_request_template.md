# 合入清单（Pull Request）

> 这不是形式主义：本项目**审计不通过就不提交**（用户 2026-09-18 拍板）。
> 下面的每一条都有对应的**机器检查**，跑一遍 `python -X utf8 scripts/run_gates.py` 就有答案。

## 一句话说明

<!-- 这次改了什么、为什么改（用户视角的一句话）。 -->

## 任务卡与追溯

- [ ] 提交带 `Task:` trailer（与 `docs/traceability.toml` 的编号一致）
- [ ] 提交带 `Refs:`（涉及的 SR / OP / GAP）与 `Ledger:`（台账状态变更）
- [ ] 台账里对应条目的 `status` 已更新（`done` 要有**能跑通的证据断言**）
- [ ] 文档与代码**同一个提交**：`docs/traceability.toml` + `docs/changelog.md` + CHECKPOINT（`复盘/长任务执行协议.md` 或 `复盘/交接-重构进度.md`）

## 门禁（十一项全绿）

- [ ] `python -X utf8 scripts/run_gates.py` 通过（pytest / 验收 / ruff / mypy / check_layers / 自测 /
      DOM 探针 / audit / 台账↔规格标题对账 / LF-1 真机 / 前端自检）
- [ ] `gates/last.json` **已随提交入库**（审计按它核对 `Gates:` trailer 的真伪）
- [ ] 新增/改了路由 → 台账里被引用（或写进 `meta.acknowledged_routes`）
- [ ] 新条目的编号合法（`docs/CODING_GUIDELINES.md` §9.1：`SR-Fx.y` 只给规格条目；拆卡加 `a/b` 后缀；
      自造卡用 `T-*`/`STEP-*`/`OP-*`；标题以规格原词开头）
- [ ] 声称与证据的差欠**逐条**写进 `[exceptions]` 并写明理由（修一条删一条，不许静默豁免）

## 口径与边界

- [ ] 没有新增"规格说有、代码没有"的假实现（做不到就**改规格 + 写依据**，或标 `partial`/`deferred` + `gaps`）
- [ ] 没有违反约定层红线（`docs/specification/conventions.md`；含**不折算时间**、温和不施压、本地优先）
- [ ] 新增字段/迁移**幂等**、老库安全（缺列/缺表不失败）
- [ ] 用户写的正文不进日志（SR-NF16 隐私最小化）

## 界面（若涉及前端）

- [ ] 零构建、零第三方依赖（单文件 `src/web/index.html` + `app.css`）
- [ ] 交互走 `data-action`（或 `data-enter` / `data-change`）+ `ACTIONS` 注册表，**没有内联事件**
- [ ] 颜色只住 `app.css` 的令牌区（HTML/JS 里不写死颜色）；
      尺寸走**尺度令牌**（`--sp-*` / `--r-*` / `--fs-*`，R5 起护栏强制，发丝级 1~3px 除外）
- [ ] 空态走 `emptyState()`、危险动作走 `confirmAsk()`（**不许原生 `confirm`**）
- [ ] DOM 探针跑过（12 视图 + 详情面板 + 完成明细展开 + 复习卡编辑态 + 硬考核 + 白名单勿扰）

## 用户可见变化

<!-- 用户会看到什么不一样？需不需要他在真机上确认（涉及系统集成/通知/文件打开时**必须**让他确认）。 -->

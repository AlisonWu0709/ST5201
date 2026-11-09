# 阶段1及1.5进度记录

日期：2026-11-09。当前分支 `part-c2-c3-part-d`，HEAD `995c669`。**正式 Part C/D 尚未执行**。本次没有 commit、push、PR、main修改或正式数值结论。

## 阶段1.6更新

已完成未跟踪文件A/B/C分类和精确.gitignore，保留但排除smoke/demo/benchmark、缓存、临时日志和机器审计快照。正式results与formal目录未整体忽略。待提交路径、完整逐文件分类和当前数量见 `reports/STAGE_1_6_ACCEPTANCE.md`。

最新验收：compileall通过；pytest 39项通过（5.08秒）；A/B1 14项与B2/B3 9个设置通过；git diff --check通过。三个已跟踪验证摘要连续两轮重跑逐字节不变，保留现有环境版本与浮点诊断更新。未更改组员源码，未暂存或提交。

正式运行命令改为仓库外 `../ST5201-formal-results/formal/part_c_run01` 与 `part_d_run01`，以确保clean基线提交后运行产物不改变仓库dirty状态，严格provenance恢复规则不变。阶段1.5记录的仓库内formal路径仅为当时设计，后续以README和阶段1.6验收记录为准。正式实验仍未执行。

## 已完成

阶段1：阅读教师PDF、审查并迁入旧模块/tests/reports；接通正式A/B方法；建立统一C/D驱动、重复层面指标、seed-once、dataset_id、基本checkpoint及PNG/PDF导出，25项测试通过。

阶段1.5：补齐 schema/version、UUID run_id、config_hash、完整配置、Git commit/dirty、关键源码 SHA256 和环境版本；恢复逐项严格比对，不兼容立即拒绝。新增正式 CLI 与显式单目录 postprocess；smoke/demo/benchmark/formal 隔离。旧 smoke 不删除；旧无指纹 checkpoint 不再接受恢复。修复阶段1中文文档编码损坏。

适配器 spy 测试确认 estimate_circle、oracle_projection、plugin_projection、oracle_bayes、plugin_bayes、manifold_fitting 均实际调用。C六方法、D四方法，输出有限(m,2)，MF fallback rate/counts 可保存。

## 测试与记录

| 命令 | 结果 | 进程墙钟耗时 |
|---|---|---|
| python part_b/validation_projection.py | 14项通过 | 0.262478秒 |
| python part_b/validation.py | 9个设置通过 | 0.504913秒 |
| python -m pytest -q | 39项通过，pytest计时5.15秒 | 6.022462秒 |

日志见 `reports/validation_stage_1_5/`。测试新增源码/配置/seed/schema/方法/Git/环境不匹配拒绝、旧checkpoint拒绝、实际A/B调用验证、正式目录保护及smoke不得进入正式汇总。

新版 C smoke 12行、D smoke 16行均通过并成功 `--resume`。两者的 `--test-only` 汇总及 PNG/PDF/代表图导出通过。全部是SMOKE_TEST_ONLY，无正式结果。验证脚本按已有行为刷新共享numerical_checks摘要，源码未修改。

## 性能探测（仅计时，不作方法效果比较）

单一 C 设置：n=100、sigma=.15、m=100、1次重复、seed=5201，六种方法共享数据。未运行第二个设置或正式50次循环。

| 方法 | 实测时间（毫秒，约） |
|---|---:|
| raw | 0.031 |
| oracle_projection | 0.114 |
| fitted_projection | 0.160 |
| oracle_posterior_mean | 2.670 |
| plugin_posterior_mean | 1.407 |
| mf | 5.356 |

另在同一批输出上计时 C/D 几何指标内核，未生成 D 新数据。计时与外推文件位于 `artifacts/benchmark/stage_1_5/`，标记 BENCHMARK_ONLY。

假设 MF 对 n×m 线性、固定 K 的 Bayes 对 m 线性、几何指标对 grid×m 线性，正式两部分各450个setting-repetitions。外推计算主体 C=142.554秒、D=258.895秒；粗略规划区间 C=71–428秒、D=129–777秒（非置信区间）。不含完整checkpoint写盘、启动及后处理；单设置、不同噪声/形状、更大工作集和系统负载均限制估算可靠性。这不是正式实验结果。

## 文件与旧目录验收

本阶段开始的完整文件哈希/时间戳快照见 `reports/STAGE_1_5_BASELINE.json`；结束时的全部文件盘点、未跟踪清单、变化分类、缓存/临时文件检查及旧目录前后比较见 `reports/STAGE_1_5_INVENTORY.json`。

旧目录34个文件的 SHA256、大小、mtime 本阶段前后全部一致，最新修改时间仍为11月3日16:30:18（UTC+8）。没有阶段1之前的独立快照，不能声称拥有更早逐字节审计证据。共享组员源码无git差异。

阶段1.5新增/生成45个交付文件，修改6个已有文件；当前未跟踪清单共73个文件（含阶段1遗留）。完整逐文件路径见上述盘点文件。`git diff --stat`只包含三个已有验证摘要：3 files changed, 20 insertions(+), 20 deletions(-)，不含未跟踪目录。

member_c_work 有测试执行生成且被Git忽略的 __pycache__；未发现复制的 .venv 或临时文件。顶层原有 .venv 不属于新整合内容。当前缓存不在未跟踪交付文件清单中。

## 下一阶段

已具备显式启动正式实验的代码条件，本次停止于准备完成。正式 C9×50、D3×3×50及后处理的准确首次运行/恢复/汇总命令见 README 的“下一阶段正式命令”；所有正式输出选择新 `artifacts/formal/<run>/` 目录。

启动后不得改源码、Git状态或环境；严格指纹校验会拒绝不兼容恢复。单run仅允许一个写入进程。正式实验完成后补充K=1024及椭圆细网格复核、完整性和MCSE检查，然后才开始证据分析、正式图表及最终报告。

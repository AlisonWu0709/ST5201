# 阶段1.6：Git整理与正式实验前验收

本阶段未运行正式Part C/D，未git add、commit、push或创建PR。HEAD保持995c669，分支保持part-c2-c3-part-d。源码运行逻辑无旧目录绝对路径依赖，正式运行仅从当前共享仓库导入方法。

## 验证结果

- `python -m compileall -q member_c_work part_a part_b part_c mf_weighted.py`：通过，0.095秒。
- `python -m pytest -q`：39项通过，pytest计时5.08秒，进程墙钟5.869秒。
- `python part_b/validation_projection.py`：14项检查通过，0.270秒。
- `python part_b/validation.py`：9个设置通过，0.369秒。
- `git diff --check`：通过。
- 两个实验入口与postprocess的`--help`已核对；README的参数和CLI一致。现有测试覆盖恢复、源码指纹、环境/Git状态和配置变化拒绝，以及输出类型隔离。

## 三个已跟踪验证摘要逐项解释

1. `results/numerical_checks/a_b1_validation_summary.txt`：只更新Python/NumPy版本，从旧记录3.12.14/2.5.4变为当前3.13.9/2.3.5。版本是有效复现信息，保留；检查结果和其余数据不变。
2. `results/numerical_checks/validation_summary.csv`：只更新最后一列K=512与K=1024最大差异的浮点数，量级约10⁻¹⁵。所有MF半径、查询数和fallback计数均不变，仍为修正MF公式。保留原始数值诊断，不修改组员算法或人为把诊断归零。
3. `results/numerical_checks/validation_summary.txt`：同一K网格差异的格式化文本随CSV更新；MF总fallback仍为7/1080，其余一致。

没有时间戳、随机路径或临时文件名。相同环境连续两轮重跑后，三个文件与阶段1.5结束时的内容逐字节一致，生成逻辑无需调整。机器版本与微小浮点差异是有说明的验证证据，不作方法效果比较。临时进程日志另行忽略。

## 分类与忽略规则

A为必须提交的源码、测试、持久文档及方法草稿；B仅为明确标记的输入schema样例；C为本地生成物、缓存、日志或带机器路径/时间戳的迁移审计。以下完整清单同时覆盖原73个未跟踪文件及本阶段新增验收记录。

`.gitignore`精确排除Python/pytest缓存、三个测试产物目录、旧SMOKE_TEST_ONLY文件、阶段1.5机器审计快照、validation进程日志、原子写临时文件和指定测试临时目录。未忽略整个results或formal目录。正式summary、CSV、manifest及图仍可按需提交。无需空目录占位；运行时自行mkdir。

`results/INPUT_SCHEMA.csv`属于B：仅列头的输入schema样例，不是正式结果，也不是固定数值fixture；本项目无额外固定fixture需要提交。

## 待提交建议（仅列命令，未执行）

在审阅本清单后，可使用以下精确路径集合；目录member_c_work内C类已由.gitignore排除：

```powershell
git add -- .gitignore member_c_work results/numerical_checks/a_b1_validation_summary.txt results/numerical_checks/validation_summary.csv results/numerical_checks/validation_summary.txt
```

建议commit message：`Integrate Part C/D framework with provenance and preflight validation`

创建clean基线后，从共享仓库根目录运行下列命令。正式输出选择仓库同级目录，避免运行中新文件令Git dirty状态变化而阻断严格恢复。输出目录无需预建。

```powershell
python -m member_c_work.part_c_experiment --formal --output-dir ../ST5201-formal-results/formal/part_c_run01
python -m member_c_work.part_d_experiment --formal --output-dir ../ST5201-formal-results/formal/part_d_run01
```

中断后保持相同源码、Git提交/dirty状态和环境，使用：

```powershell
python -m member_c_work.part_c_experiment --formal --resume --output-dir ../ST5201-formal-results/formal/part_c_run01
python -m member_c_work.part_d_experiment --formal --resume --output-dir ../ST5201-formal-results/formal/part_d_run01
```

完成后汇总与绘图：

```powershell
python -m member_c_work.postprocess --run-dir ../ST5201-formal-results/formal/part_c_run01
python -m member_c_work.postprocess --run-dir ../ST5201-formal-results/formal/part_d_run01
```

预计各自生成manifest.json、checkpoint.json、representative.npz、repetitions.csv、analysis/summary.csv、PNG/PDF；C另有analysis/parameter_summary.csv。正式C为9×50、2700行，D为3×3×50、1800行。所有恢复与后处理完成前保持仓库不变，再将正式摘要选择性复制至共享仓库results/formal/审阅提交。

已具备创建clean基线commit的条件；本次只整理与验收，正式实验尚未执行。

## Complete classification (repository-relative paths)

A: 26 files; B: 1 file; C: 75 existing ignored files under member_c_work.
Total proposed add set: 31 files (27 new plus 4 tracked modifications).
C includes 52 generated outputs/logs/audits and 23 bytecode/cache files. Original 73 untracked files are all classified.
Repository-root caches and the pre-existing .venv are outside this member_c_work count.

### A - required source, tests and durable documentation

- `member_c_work/INTEGRATION_CHECKLIST.md`
- `member_c_work/PROGRESS_REPORT.md`
- `member_c_work/README.md`
- `member_c_work/__init__.py`
- `member_c_work/benchmark.py`
- `member_c_work/data_generation.py`
- `member_c_work/demo_plots.py`
- `member_c_work/experiment.py`
- `member_c_work/method_adapters.py`
- `member_c_work/metrics_circle.py`
- `member_c_work/metrics_ellipse.py`
- `member_c_work/part_c_experiment.py`
- `member_c_work/part_d_experiment.py`
- `member_c_work/postprocess.py`
- `member_c_work/provenance.py`
- `member_c_work/reports/PART_C_METHODS_DRAFT.md`
- `member_c_work/reports/PART_D_DRAFT.md`
- `member_c_work/reports/STAGE_1_6_ACCEPTANCE.md`
- `member_c_work/requirements.txt`
- `member_c_work/result_integration.py`
- `member_c_work/statistics.py`
- `member_c_work/tests/test_experiments.py`
- `member_c_work/tests/test_integration.py`
- `member_c_work/tests/test_metrics.py`
- `member_c_work/tests/test_run_safety.py`
- `member_c_work/visualization.py`

### B - optional, clearly labelled schema sample

- `member_c_work/results/INPUT_SCHEMA.csv` (header-only schema; not experimental data)

### C - do not commit; retained locally and ignored

- `member_c_work/__pycache__/__init__.cpython-313.pyc`
- `member_c_work/__pycache__/benchmark.cpython-313.pyc`
- `member_c_work/__pycache__/data_generation.cpython-313.pyc`
- `member_c_work/__pycache__/demo_plots.cpython-313.pyc`
- `member_c_work/__pycache__/experiment.cpython-313.pyc`
- `member_c_work/__pycache__/method_adapters.cpython-313.pyc`
- `member_c_work/__pycache__/metrics_circle.cpython-313.pyc`
- `member_c_work/__pycache__/metrics_ellipse.cpython-313.pyc`
- `member_c_work/__pycache__/part_c_experiment.cpython-313.pyc`
- `member_c_work/__pycache__/part_d_experiment.cpython-313.pyc`
- `member_c_work/__pycache__/postprocess.cpython-313.pyc`
- `member_c_work/__pycache__/provenance.cpython-313.pyc`
- `member_c_work/__pycache__/result_integration.cpython-313.pyc`
- `member_c_work/__pycache__/statistics.cpython-313.pyc`
- `member_c_work/__pycache__/visualization.cpython-313.pyc`
- `member_c_work/artifacts/benchmark/stage_1_5/BENCHMARK_ONLY_estimates.json`
- `member_c_work/artifacts/benchmark/stage_1_5/BENCHMARK_ONLY_timings.csv`
- `member_c_work/artifacts/benchmark/stage_1_5/manifest.json`
- `member_c_work/artifacts/demo/SMOKE_TEST_ONLY_circle_plots.png`
- `member_c_work/artifacts/demo/SMOKE_TEST_ONLY_ellipse_plot.pdf`
- `member_c_work/artifacts/smoke/stage_1_5_part_c/SMOKE_TEST_ONLY_repetitions.csv`
- `member_c_work/artifacts/smoke/stage_1_5_part_c/analysis/SMOKE_TEST_ONLY_clean_test_coverage_error.pdf`
- `member_c_work/artifacts/smoke/stage_1_5_part_c/analysis/SMOKE_TEST_ONLY_clean_test_coverage_error.png`
- `member_c_work/artifacts/smoke/stage_1_5_part_c/analysis/SMOKE_TEST_ONLY_coverage_error.pdf`
- `member_c_work/artifacts/smoke/stage_1_5_part_c/analysis/SMOKE_TEST_ONLY_coverage_error.png`
- `member_c_work/artifacts/smoke/stage_1_5_part_c/analysis/SMOKE_TEST_ONLY_denoising_mse.pdf`
- `member_c_work/artifacts/smoke/stage_1_5_part_c/analysis/SMOKE_TEST_ONLY_denoising_mse.png`
- `member_c_work/artifacts/smoke/stage_1_5_part_c/analysis/SMOKE_TEST_ONLY_parameter_summary.csv`
- `member_c_work/artifacts/smoke/stage_1_5_part_c/analysis/SMOKE_TEST_ONLY_radial_error.pdf`
- `member_c_work/artifacts/smoke/stage_1_5_part_c/analysis/SMOKE_TEST_ONLY_radial_error.png`
- `member_c_work/artifacts/smoke/stage_1_5_part_c/analysis/SMOKE_TEST_ONLY_representative.pdf`
- `member_c_work/artifacts/smoke/stage_1_5_part_c/analysis/SMOKE_TEST_ONLY_representative.png`
- `member_c_work/artifacts/smoke/stage_1_5_part_c/analysis/SMOKE_TEST_ONLY_summary.csv`
- `member_c_work/artifacts/smoke/stage_1_5_part_c/checkpoint.json`
- `member_c_work/artifacts/smoke/stage_1_5_part_c/manifest.json`
- `member_c_work/artifacts/smoke/stage_1_5_part_c/representative.npz`
- `member_c_work/artifacts/smoke/stage_1_5_part_d/SMOKE_TEST_ONLY_repetitions.csv`
- `member_c_work/artifacts/smoke/stage_1_5_part_d/analysis/SMOKE_TEST_ONLY_denoising_mse.pdf`
- `member_c_work/artifacts/smoke/stage_1_5_part_d/analysis/SMOKE_TEST_ONLY_denoising_mse.png`
- `member_c_work/artifacts/smoke/stage_1_5_part_d/analysis/SMOKE_TEST_ONLY_ellipse_to_output.pdf`
- `member_c_work/artifacts/smoke/stage_1_5_part_d/analysis/SMOKE_TEST_ONLY_ellipse_to_output.png`
- `member_c_work/artifacts/smoke/stage_1_5_part_d/analysis/SMOKE_TEST_ONLY_output_to_ellipse.pdf`
- `member_c_work/artifacts/smoke/stage_1_5_part_d/analysis/SMOKE_TEST_ONLY_output_to_ellipse.png`
- `member_c_work/artifacts/smoke/stage_1_5_part_d/analysis/SMOKE_TEST_ONLY_representative.pdf`
- `member_c_work/artifacts/smoke/stage_1_5_part_d/analysis/SMOKE_TEST_ONLY_representative.png`
- `member_c_work/artifacts/smoke/stage_1_5_part_d/analysis/SMOKE_TEST_ONLY_summary.csv`
- `member_c_work/artifacts/smoke/stage_1_5_part_d/checkpoint.json`
- `member_c_work/artifacts/smoke/stage_1_5_part_d/manifest.json`
- `member_c_work/artifacts/smoke/stage_1_5_part_d/representative.npz`
- `member_c_work/figures/SMOKE_TEST_ONLY_circle_plots.png`
- `member_c_work/figures/SMOKE_TEST_ONLY_ellipse_plot.pdf`
- `member_c_work/reports/STAGE_1_5_BASELINE.json`
- `member_c_work/reports/STAGE_1_5_FILES.md`
- `member_c_work/reports/STAGE_1_5_INVENTORY.json`
- `member_c_work/reports/validation_stage_1_5/pytest.txt`
- `member_c_work/reports/validation_stage_1_5/timings.json`
- `member_c_work/reports/validation_stage_1_5/validation.txt`
- `member_c_work/reports/validation_stage_1_5/validation_projection.txt`
- `member_c_work/reports/validation_stage_1_6/0_output.txt`
- `member_c_work/reports/validation_stage_1_6/1_output.txt`
- `member_c_work/reports/validation_stage_1_6/2_output.txt`
- `member_c_work/reports/validation_stage_1_6/3_output.txt`
- `member_c_work/reports/validation_stage_1_6/timings.json`
- `member_c_work/results/SMOKE_TEST_ONLY_part_c.csv`
- `member_c_work/results/SMOKE_TEST_ONLY_part_c.csv.checkpoint.json`
- `member_c_work/results/SMOKE_TEST_ONLY_part_d.csv`
- `member_c_work/results/SMOKE_TEST_ONLY_part_d.csv.checkpoint.json`
- `member_c_work/tests/__pycache__/test_experiments.cpython-313-pytest-8.4.2.pyc`
- `member_c_work/tests/__pycache__/test_experiments.cpython-313.pyc`
- `member_c_work/tests/__pycache__/test_integration.cpython-313-pytest-8.4.2.pyc`
- `member_c_work/tests/__pycache__/test_integration.cpython-313.pyc`
- `member_c_work/tests/__pycache__/test_metrics.cpython-313-pytest-8.4.2.pyc`
- `member_c_work/tests/__pycache__/test_metrics.cpython-313.pyc`
- `member_c_work/tests/__pycache__/test_run_safety.cpython-313-pytest-8.4.2.pyc`
- `member_c_work/tests/__pycache__/test_run_safety.cpython-313.pyc`

### Tracked files to include

- `.gitignore`
- `results/numerical_checks/a_b1_validation_summary.txt`
- `results/numerical_checks/validation_summary.csv`
- `results/numerical_checks/validation_summary.txt`

All ten synthetic git-check-ignore probes passed without creating formal files. The old 34-file directory still matches the earlier hash/mtime snapshot. Staging area is empty.

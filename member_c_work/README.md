# Member C：阶段1、1.5与1.6整合验收

阶段1完成了旧目录安全整合、正式 A/B 接口连接、统一 C/D 驱动、指标、统计、绘图和小规模验证。阶段1.5补齐源码指纹、严格恢复检查、结果目录隔离、正式运行入口、正式汇总入口及性能探测。正式 Part C 和 Part D **尚未执行**。所有 smoke、demo、benchmark 数据均不能用于报告结论或方法排名。

旧目录 `E:/nus classes/st5201/Project/member_c_work` 只读；共享 `part_a/`、`part_b/`、`part_c/`、`mf_weighted.py` 未修改，MF 修正提交 995c669 保持原样。阶段1的部分中文文档曾因 PowerShell 编码而损坏，阶段1.5已以 UTF-8 重写。

## 模块与实际接口

- `data_generation.py`：uniform-angle 圆/椭圆；训练和测试独立。
- `metrics_circle.py`：radial、coverage、clean-test coverage；正式 L=720。
- `metrics_ellipse.py`：双向网格 squared distance、denoising MSE；正式 grid=4096。
- `statistics.py`、`result_integration.py`：重复层面均值、sample SD、MCSE、配对和完整性校验。
- `method_adapters.py`：统一 `(train_noisy, test_noisy, sigma) -> (output, diagnostics)`，输出有限 `(m,2)`。
- `experiment.py`、`part_c_experiment.py`、`part_d_experiment.py`：配置、共享样本、seed-once、dataset_id、checkpoint。
- `provenance.py`：源码 SHA256、配置 SHA256、Git/环境指纹。
- `postprocess.py`、`visualization.py`：显式指定单一 run 目录，验证后生成汇总 CSV、PNG/PDF、首个数据集的等比例散点图。
- `benchmark.py`：单个设置单次重复的计时与粗略耗时外推。

Part C 方法：`raw`, `oracle_projection`, `fitted_projection`, `oracle_posterior_mean`, `plugin_posterior_mean`, `mf`。

Part D 方法：`raw`, `fitted_projection`, `plugin_posterior_mean`, `mf`。

实际调用 `part_a.circle_estimator.estimate_circle`、`part_b.projection.oracle_projection/plugin_projection`、`part_b.bayes_estimator.oracle_bayes/plugin_bayes`、`part_b.manifold_fitting.manifold_fitting`。测试以 spy 验证六个入口均被调用。Bayes K=512；MF k=3 和修正 B3 radii，diagnostics 保存 fallback rate 及各项计数。拟合方法不接收 clean points 或真实几何参数。参数误差只写在两种 fitted-circle 行，汇总时去重，不归于 MF。

## 验证与小型运行

从仓库根目录运行；依赖见 `requirements.txt`。

```powershell
python part_b/validation_projection.py
python part_b/validation.py
python -m pytest -q
python -m member_c_work.part_c_experiment --smoke --output-dir member_c_work/artifacts/smoke/my_c_test
python -m member_c_work.part_d_experiment --smoke --output-dir member_c_work/artifacts/smoke/my_d_test
python -m member_c_work.demo_plots
python -m member_c_work.benchmark --output-dir member_c_work/artifacts/benchmark/my_probe
```

smoke 为 n=30、m=12、sigma=.15、2次重复、grid=64；C一个 setting，D两个 b。已有目录需加 `--resume`，或选择新目录。相同源码、配置和环境才能恢复。benchmark 固定 n=100、m=100、sigma=.15、1次重复，包含六种方法，不进行正式实验。

最新阶段1.6验证：compileall通过（0.095秒），A/B1 14项通过（进程0.270秒），B2/B3 9个设置通过（0.369秒），pytest **39项通过，5.08秒**（进程5.869秒）。环境为 Python 3.13.9、NumPy 2.3.5、pandas 2.3.3、Matplotlib 3.10.6、pytest 8.4.2。本地临时日志位于被忽略的 `reports/validation_stage_1_6/`，可提交验收记录见 `reports/STAGE_1_6_ACCEPTANCE.md`。

## checkpoint 安全与目录隔离

每个 run 目录保存 `manifest.json`、`checkpoint.json`、repetition-level CSV 和 `representative.npz`。manifest/checkpoint 记录：schema/version、完整配置及固定模型设置、seed、方法列表、唯一 UUID run_id、config_hash、Git commit、dirty 状态、Python/NumPy/pandas 版本及源码哈希。源码包含指定 A/B/MF 文件、C1 参数指标及 `member_c_work` 顶层所有 Python 模块。

恢复前逐项严格比较；源码、配置、版本、commit 或 dirty 状态不一致即拒绝，并列出差异。manifest 和 checkpoint 必须一致。旧版无指纹 checkpoint 拒绝恢复，保留文件供追溯。调整源码后应使用新的 run 目录；commit、dirty 状态变化同样要求新 run，避免混合结果。

只初始化一次 seed=5201；续跑重放 RNG 生成已完成样本并校验 dataset_id，跳过已完成方法。每次完整重复后原子替换 checkpoint。CSV 行记录 run_id/config_hash；若写 CSV 前中断可恢复重建。checkpoint 不支持多个进程同时写，运行期间请保持源码不变。

- `artifacts/smoke/<run>/`：文件名与行内含 `SMOKE_TEST_ONLY`。
- `artifacts/demo/`：独立绘图示例，不能进入正式汇总。
- `artifacts/benchmark/<run>/`：仅计时，标记 `BENCHMARK_ONLY`。
- `../ST5201-formal-results/formal/<run>/`：正式运行推荐输出到共享仓库外，避免新输出改变Git dirty状态而阻断严格恢复。CLI同样支持仓库内formal目录，但clean基线提交后请使用本页仓库外命令。
- 阶段1遗留 `results/SMOKE_TEST_ONLY*` 和 `figures/SMOKE_TEST_ONLY*` 原样保留。正式脚本不会扫描这些目录。

CLI 必须选择 `--smoke` 或 `--formal`，且显式给出对应目录。formal 目录不得包含 smoke/demo/benchmark 路径。非空目录必须显式 `--resume`，新实验须用新目录。正式汇总不读取默认路径、不做跨目录 glob，并拒绝非 FORMAL manifest/CSV。

阶段1.6已通过精确.gitignore排除测试产物、机器审计快照、临时日志和缓存；`results/`、formal目录及其正式CSV/图表没有被整体忽略。阶段1.5日志/完整机器盘点属于本地证据，不随源码提交；可提交验收与逐文件分类见 `reports/STAGE_1_6_ACCEPTANCE.md`。

## 下一阶段正式命令（本次未执行）

Part C 默认 c=(0,0)、R=1、n={100,500,2000}、sigma={.05,.15,.30}、50次重复、m=500、L=720、seed=5201，共2700行。

Part D 默认 b={1,.9,.75}、n={100,500,2000}、sigma=.15、50次重复、m=500、grid=4096、seed=5201，共1800行。D 的具体 sigma、50次及网格4096为小组预设；PDF要求改变 b/n、固定噪声和使用密椭圆网格。

先由用户创建clean基线commit；之后从共享仓库根目录首次正式运行（本阶段未执行）：

```powershell
python -m member_c_work.part_c_experiment --formal --output-dir ../ST5201-formal-results/formal/part_c_run01
python -m member_c_work.part_d_experiment --formal --output-dir ../ST5201-formal-results/formal/part_d_run01
```

中断后恢复（不要改源码、配置、环境或Git状态）：

```powershell
python -m member_c_work.part_c_experiment --formal --resume --output-dir ../ST5201-formal-results/formal/part_c_run01
python -m member_c_work.part_d_experiment --formal --resume --output-dir ../ST5201-formal-results/formal/part_d_run01
```

完成后生成汇总与图：

```powershell
python -m member_c_work.postprocess --run-dir ../ST5201-formal-results/formal/part_c_run01
python -m member_c_work.postprocess --run-dir ../ST5201-formal-results/formal/part_d_run01
```

输出位于仓库同级 `ST5201-formal-results/formal/part_c_run01/` 和 `part_d_run01/`，包括各自 `repetitions.csv` 及 `analysis/summary.csv`、参数汇总（C）和 PNG/PDF。正式实验及汇总全部完成后，可将选定数值摘要、manifest和图表复制到共享仓库 `results/formal/`，再单独审阅提交；该目录不被忽略。恢复/汇总期间不要修改仓库。代表图固定使用首个数据集，不按结果选择。MCSE按重复计算，clean-test coverage 仅为空间间距参考，不能视作严格下界。阶段1.5只用 `--test-only` 验证了 smoke 汇总/绘图入口。

单设置计时外推：C计算主体约143秒，D约259秒；粗略规划范围分别71–428秒、129–777秒。范围不是置信区间，未计完整 checkpoint I/O、启动和绘图；更大样本的缓存、噪声及几何变化会影响耗时。正式执行后才可获得真实总耗时。

正式结果完成后仍需 K=1024 代表性复核、椭圆网格敏感性、重复完整性及 MCSE 审核，再开始正式结果解释。AI辅助用于整合、测试与文档，组员应复核并在最终提交中披露。

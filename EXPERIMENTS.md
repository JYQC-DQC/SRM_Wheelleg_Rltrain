# 实验记录

## 2026-11-10 训练评审修复

仅修改本仓库。修复质量设备、场景生命周期、事件奖励、窗口课程、固定评测延迟、永久外力、
力矩/电压缩放、隧道指令/过滤接触、训练启动记录及 transition_states 输出命名。

实际执行 `D:/Anaconda3/envs/mjlab/python.exe runs/run_cpu_tests.py tests/test_review_fixes.py tests/test_training.py -s`，
沿用已安装 pytest 的本地启动脚本，不运行 Isaac；输出：

```text
dt=0.01: result_total=8.000000, guidance_total=1.208500
dt=0.02: result_total=8.000000, guidance_total=1.183000
28 passed in 1.89s
```

`ruff check wheelleg isaac tools tests/test_review_fixes.py`：`All checks passed!`

`ruff format --check wheelleg isaac tools tests/test_review_fixes.py`：`28 files already formatted`

未运行全量测试、Isaac/GPU 仿真、PPO 冒烟、视频或实车。新增 API 的缓存来源均为 Isaac Lab v2.3.2，
保存在 runs/api_reference；本次新增 contact_sensor_cfg.py、contact_sensor_data.py、contact_sensor.py、
wrench_composer.py、physics_materials_cfg.py。GPU mass_ratio、过滤接触方向及场景克隆/外力仍需目标镜像动态验证。

本仓库现有 .gitignore 将 tests/ 和 runs/ 留在本地；本次没有改变这一约定。

尚未进行 GPU 训练或实车测试。

| 日期 | 配置与提交 | 机器人版本 | 验证类型 | 结果与产物路径 |
|---|---|---|---|---|
| 2026-11-08 | feat/ppo-foundation 首批代码 | 无云台配置，标定待填 | CPU 单元测试 | 12 passed；无 GPU/实车测试 |
| 2026-11-10 | 多策略实现中间版本 | 无云台，真实参数继续留空 | CPU 数值检查 | 31 passed in 1.55s；用户随后要求暂停完整测试，此结果不覆盖后续改动 |

2026-11-10：新增七阶段训练入口，指南同步到 v2.1；尚无 Isaac/GPU 训练、sim2sim、实车或 ONNX 实测产物。
目标版本 rsl_rl/ONNX Runtime 仅下载到忽略目录 runs/test_deps 作准备，未修改本机环境安装版本；未进行 PPO 训练。

# SRM 轮腿 PPO

首批实现：配置加载、35 维观测参考实现、C 接口头生成、35→256→128→64→6 的 PyTorch Actor、CPU 测试。尚未接入 Isaac Lab，不能开始正式训练。

当前先训练真实无云台底盘，后续装云台再更新质量/质心/惯量并评测、续训。保留闭链和气弹簧。
物理和 PD 500 Hz，推理 100 Hz。M3508 减速比 15.76:1；弹簧标称 450 N、行程 75 mm。
全部电机、扫频、弹簧和延迟辨识必须完成；不以随机化代替辨识。跳过隧道并在后方地面落地是必须任务。

## 本机 CPU 开发

推荐 Python 3.11。激活自己的环境后，在仓库根目录执行：

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check .
python -m tools.check_config --robot config/robot.yaml --policy config/policies/p1/policy_meta.yaml
python -m tools.gen_c_config --robot config/robot.yaml --policy config/policies/p1/policy_meta.yaml --output export/gen_config.h --interface-only
```

配置检查列出的 MISSING 是尚待 CAD/实测的数据，不是建议填默认值。`--require-ready` 在未齐全时返回非零。
目标云环境为用户提供的 Isaac Sim 5.1 / Isaac Lab 2.3.2 / Ubuntu 24.04 / CUDA 12.8 镜像；不在本机基础环境强装 Isaac。

## 两个仓库

- 本仓库：模型、PPO、sim2sim、导出。
- `D:/Code-RM/github`，分支 `wheelleg_RL`：现有 H723 框架内实现部署、采集、扫频及电机/弹簧辨识分析。
- 当前逻辑关节顺序和单位见 [接口合同](docs/INTERFACE.md)。
- 先完成参数合同和 FW0，再按完整辨识门槛推进。尚未导出的 CAD/标零结果不从其他机器人抄来。
- 老指南是设计参考，最新用户约定和本 README 优先；特别是分支、两个仓库分工及无云台阶段。

训练权重/视频/轨迹存 `runs/`，不进 Git；有效发布物和配置另行按版本保存。


## 本轮验证（2026-11-08）

- Python 数值测试：12 passed（本机既有 mjlab Python 3.12 环境）；Ruff 检查和格式通过。
- Actor 为 50,758 参数，FP32 权重 203,032 字节；这是参数存储量，不是 CubeAI 总 RAM 或运行时间。
- 只验证网络形状、状态恢复和反向传播；未接入 PPO 优化器、Isaac 环境或训练。
- 当前 Anaconda base 的 PyTorch/NumPy 组合导入时会 abort，未修改该环境。无 Torch 的 CPU 配置测试可用 `python -m pytest tests/test_contract.py -q` 单独运行。
- 本机 mjlab 的 CUDA 13 / Torch 环境仅用于 CPU 数值检查，不代表目标 Isaac Lab 2.3.2 镜像已验证。
- 后续到云端严格记录镜像自带 Python/Torch/Isaac 版本，不在已有镜像上无条件升级 torch。

下一批：固件默认失能与同步控制、遥测记录；机械侧导出实际闭链 CAD 及质量惯量。
缺少几何/标定/辨识数据时不能声明正式训练就绪。

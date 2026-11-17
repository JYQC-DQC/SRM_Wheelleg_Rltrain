# SHU-Train｜上大无云台轮腿底盘

P1 通行先练平地，再练被动落地与预设起身，最后混合地形；不另训旧 recovery。P2 练原地自转，P3 练按键跳跃。三套策略各有自己的速度估计器。这里记录训练合同，不代表已完成 Isaac/GPU 训练或实车验证。

- [训练顺序、检查命令与校准交接](docs/TRAINING.md)
- [策略输入、历史帧与动作合同](docs/INTERFACE.md)
- [上大训练方案：奖励、课程与待定项](docs/上大轮腿训练方案/README.md)
- [扫频与辨识指南](docs/SWEEP_IDENT.md)

本仓负责训练与策略导出；固件部署和辨识在 `D:/Code-RM/github` 的 `wheelleg_RL` 分支进行。缺少本车 CAD、USD 或实测参数时保留 `null`，不借用参考车数据启动正式训练。方案里的历史实现固定在[参考车快照 1a56b67](https://github.com/JYQC-DQC/SRM_Wheelleg_Rltrain/tree/1a56b67067accd185bc5e7c41175dc0795e3d8fb)，不是本分支的训练入口。

纯数值及训练接口回归：`python -m pytest -q`；静态检查：`python -m ruff check .` 和 `python -m ruff format --check .`。安装目标训练与导出依赖后可覆盖 PPO 更新和 ONNX 对拍；这些检查不代替 Isaac 动力学或实车验收。

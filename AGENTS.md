# SRM_Wheelleg_Rltrain

先读 docs/CODING_GUIDE.md 与 README.md。用户最新约定优先于历史指南。

- 本仓库负责 PPO 训练、模型、MuJoCo sim2sim、观测合同和固件参数导出。
- 部署、扫频、电机/气弹簧辨识及分析在 D:/Code-RM/github 的 wheelleg_RL 分支进行；这里导入结果。
- 当前阶段是真实无云台底盘。几何、质量、零点、ID 和辨识量缺失时写 null，不照搬开源机器人。
- 500 Hz 物理/PD，100 Hz 策略；完整辨识不可省略，不能以加宽随机化代替。
- 跳隧道是必须项：完整越过，在后方地面落地，不奖励顶面落地。
- 固件不在本仓库新建工程；不修改参考开源项目。
- 验证：python -m pytest -q；python -m ruff check .；python -m ruff format --check .
- 不编造 GPU 训练、实机测试或推理性能。

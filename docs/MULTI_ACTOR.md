# 多 Actor 调度与专项训练

本架构遵循 AGENTS.md 的冻结基础 Actor 约定。当前已接通 Landing/Jump 训练、Isaac 评测、MuJoCo 跳跃回放及分别导出 ONNX 的路径。

## Actor 与固定输入合同

`wheelleg/multi_actor.py` 的 ActorBank 通过名称和显式整数 ID 选择 Actor，可注册三个、四个或更多 Actor。`config/reference/scut_actor_bundle.yaml` 是本机 Landing 5800 / Jump 3400 的配置示例，路径指向已有下载文件。云端需填写云端对应的检查点与参数路径。

mode 始终使用 docs/INTERFACE.md 的固定七维定义。当前自动调度器以 jump 标志选择 Jump，其他阶段选择冻结 Landing。第三、第四种专项可注册到 ActorBank 并通过显式 ID 调用；对应的任务触发、安全退出及训练环境仍需逐项实现和验证，不能占用 mode 槽表达新的含义。

所有 Actor 共用关节顺序、零点、传感器缩放、动作缩放、PD、限幅、控制频率和上一帧实际原始动作。加载时核对这些合同，冻结模型记录 SHA-256，文件变更时拒绝加载。当前仅支持单帧 obs_v2、前馈策略。

## 控制权与交接

1. 等待及助跑由冻结 Landing 执行。
2. 跳跃请求在选择动作前进入活动状态，首个蹬地动作由 Jump 执行。
3. Jump 完成腾空、收腿、触地与连续 0.8 秒落稳。
4. 切回 Landing 观察 2 秒，之后结束本次回合。整段观察要求双轮接触、roll/pitch 小于 0.25 rad、竖直速度小于 0.3 m/s、roll/pitch 角速度小于 1 rad/s、前进速度误差小于 0.5 m/s、偏航角速度误差小于 0.5 rad/s。任一时刻不满足即记录交接失败。阈值与时长在 bundle 的 handoff 节点明确配置。
5. 课程成功延迟到交接完成；交接失败增加一次 -4 成本。Jump 失败或物理终止走失败回合重置，避免在失控腾空时将控制权交给地面 Actor。

现有跳跃阶段奖励保留，落稳相关即时奖励仍在落稳时计算；交接成本通过后续价值回报影响之前的 Jump 动作。交接成功还要求本次跳跃已满足目标高度、起跳速度和适用的航向验收。

## 专项 PPO

Jump 的 surrogate、熵、KL、优势归一化只使用 Jump 实际执行的步骤。冻结 Actor 的动作不作为 Jump 的策略学习样本。空专项批次显式清除 Actor/std 梯度，避免 Adam 动量改变参数。

critic 是组合控制器的辅助价值网络，学习包括冻结 Landing 阶段在内的完整回报，因此交接失败能沿 GAE 回传。critic 新增两个特权量，分别为交接剩余时间和累计失败标志；Actor 仍为 35 维。该模式目前支持单 GPU，禁用 RND、对称增广和循环/历史网络。原奖励参数、回合混合比例与课程等级不因启用 bundle 自动调整。

## 启动和保存

在 Isaac 环境、仓库根目录设置 PYTHONPATH 后，向原训练命令增加 `--actor-bundle <manifest.yaml>`。`--initialize-from` 可以选择 Jump 的初始化检查点；省略时使用 bundle 中专项 Actor 的检查点。原 Landing 始终独立加载并冻结。

训练将全部模型与参数复制到新 run 的 `params/actors/`，保存可搬迁的 `params/actor_bundle.yaml`。checkpoint 合同记录冻结 Actor 校验值、调度和交接配置。旧单 Actor checkpoint 仅能通过 `--initialize-from` 迁移 Actor，不能恢复旧 critic/优化器。多 Actor run 的 `--resume` 自动发现其 bundle，恢复时核查合同。

## 评测、回放与导出

- Isaac 标准评测入口自动发现 checkpoint 的 `params/actor_bundle.yaml`，课程成功按完成交接统计。
- `tools.play_jump` 自动发现 bundle，也可传 `--actor-bundle`，在同一机器人状态及动作延迟链中切换 Actor。交接观察期间拒绝重复按键，失败后需要重置。
- `tools.export_policy` 自动发现多 Actor run，分别导出每个 Actor，逐个执行 ONNX 数值对照，并输出 `deployment_bundle.yaml`。部署侧加载具名 ONNX，按显式状态选择模型，保持实际上一帧原始动作连续。仓库仅生成部署包，未修改固件工程。

这是结构与接口实现；小规模测试不代表跳跃能力或实机交接性能验收。

## 本次专项训练配方

`config/reference/scut_p3_multi_actor.yaml` 保留现有跳跃奖励，取消不跳跃回合，原地跳与行进跳各占 50%。两组独立课程均在当前等级积累 500 个有效事件、成功率达到 60% 后升档。独立平地组的升档门槛在 MultiActorEnv 中关闭，仍保留跳跃方向验收和交接后观察验收。基础 Landing 不参与优化；这不代表交接质量已通过长训练验证。

## 续训升至 L2 与失败诊断

`--resume <多 Actor checkpoint> --restart-jump-level 2` 恢复 Actor、critic、优化器及迭代数，再将两组课程设为 L2（9.25 cm），清空旧课程窗口、成功率缓存和引导衰减时钟，并重置物理回合。`--iterations` 是额外迭代数；本次沿用原训练 10000 轮的总目标。60% 升档门槛、500 次事件窗口和原奖励不变。

落稳事件无论跳高、速度或航向是否合格，均延迟到交接观察结束后只计一次。未落稳的失败即时计一次。每个事件由去重标志保护，回合重置后才允许下一事件计数。

`JumpOutcome/stationary/*` 与 `JumpOutcome/moving/*` 分别记录最终事件数、成功数、未落稳事件失败，以及高度、起跳速度、航向和交接稳定性失败的计数与比例。四项验收原因只对已完成落稳、走完交接观察的事件评估，允许同一事件同时不合格，不能将原因计数相加当作失败事件总数；比例分母为该组所有最终事件。未落稳的失败单列为 event_failures。

`MultiActor/handoff_success_rate` 保留原完整验收口径；新增 `handoff_stability_success_rate` 仅统计交接观察本身。`Handoff/<组>/<原因>_failures` 进一步区分倾角、竖直速度、横滚/俯仰角速度、前进速度、偏航角速度、双轮接触缺失、物理终止和时间截断。观察期一次接触缺失仍然算失败。2026-11-21 用户仅授权将交接竖直速度上限由 0.2 放宽至 0.3 m/s，其他验收条件不变。

训练和 MuJoCo 回放均支持 --handoff-vertical-speed 0.3。从旧 0.2 门槛检查点续训时，必须显式传此参数；仅允许迁移合同中的这个字段，冻结模型哈希、mode、critic 特征、观察时长等任何其他差异仍拒绝恢复。迁移保留网络、优化器、迭代数、课程等级和引导状态，清空旧验收门槛下的统计窗口；原 checkpoint 和 params 快照不覆盖。注意落稳阶段 stable_vz_m_s: 0.20 仍保持原值，本次调整只针对交回 Landing 后的观察。

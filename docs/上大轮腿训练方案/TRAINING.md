# SHU-Train 训练与交接

| 策略 | 顺序与交接条件 |
|---|---|
| P1 通行 | **平地 → 被动落地（含预设起身）→ 混合地形**。平地指令范围全开才进落地；继续训练同一 Actor 和 encoder，不重开驾驶课程。落地按空生／预设起身／普通出生 40%／40%／20% 采样，只升掉高。负责人自行做 sim2sim 并指定混训 checkpoint，不按参考车成绩代选。 |
| P1 混训 | 保留 30% 平地；含粗糙面、井字、坡和单／双级台阶。自由操控与指定路线分开；路线按实际有效过线结算，三级上、下分别由同方向单／双级先修解锁。预设起身已并入落地，不增加独立 recovery 阶段。 |
| P2 自转 | 平地原地高速自转，平移指令为零；仿真上限不是实车放行值。 |
| P3 跳跃 | **先在无障碍平面练按键跳，再练越隧道横梁**。一次按键触发一次跳跃，不用测距替代操作手按键。整车越过横梁、首触落在后方地面且随后落稳才算成功；落梁顶再滑下不算。 |

具体奖惩和未定阈值见[方案索引](README.md)。跨阶段初始化须匹配[网络合同](INTERFACE.md)，不能拿旧单帧 Actor、五输出估计器或旧优化器状态充当新策略。

P3 的指令与模拟按键分布、各阶段时间、落稳阈值、碰撞包络与裕量、引导权重继续留待确认；配置中以 `null` 标记。

## PPO 学习率

三套策略共用 PPO 自适应学习率：初始 `1e-4`，下限 `1e-5`，上限 `1e-3`。目标 KL 为 `0.01`。每个小批次检查一次：`0 < KL < 0.005` 时乘 `1.2`，`KL > 0.02` 时除以 `1.2`，其余情况不调整。只调 PPO 优化器，速度 Encoder 的独立 Adam 固定为 `1e-3`。同阶段续训恢复已有学习率，超出新边界则先收回边界；跨阶段只迁移网络，从初始学习率开始。

## 不启动仿真的检查

在仓库根目录、已安装项目依赖的环境执行。训练入口的 `--check-only` 列出该 task 的缺项，不启动仿真；正式启动仍须通过阶段就绪检查。下面 `tools.check_config --require-ready` 单独检查机器人与策略的公共合同，不能代替阶段就绪检查。

```powershell
python -m isaac.scripts.train --task p1-flat --check-only
python -m tools.check_config --robot config/robot.yaml --policy config/policies/p1/policy_meta.yaml --require-ready
```

## P3：训练输入与手动 rollout

P3 的默认模板是 `config/policies/p3/policy_meta.yaml`。检查两阶段的缺参：

```powershell
python -m isaac.scripts.train --task p3-jump --check-only
python -m isaac.scripts.train --task p3-tunnel --check-only
```

正式 P3 入口读取所选阶段的 `press_time_range_s`（秒）、`no_press_probability`、`moving_probability`。三者未定为 `null`；确认后填写才有训练输入。每个非空回合最多模拟一次按键上升沿，按回合时间触发，不读取梁距。移动与不移动使用各自的前速目标；没有外力辅助跳跃。

手动 rollout 使用显式的 checkpoint、`--vx-m-s`，并选择 `--press-time-s` 加 `--jump-height-m`，或 `--no-press`。两种 P3 地形都不支持按障碍距离触发。该路径读取 `training.evaluation` 的 `duration_s`、`episodes_per_case`、`seed`、`height_m` 和两项延迟，不使用训练按键分布。外部调用时，先 `obs = env.unwrapped.set_jump_button(button_down, target_height_m=...)`，再使用返回的观测计算动作；下一拍记得释放。本流程只做操作者指定的 rollout，不做自动选模或验收。

隧道模板保留梁底 `0.25 m`、梁顶 `0.27 m`、沿 x 长 `0.35 m`、前沿距入口 `1.35 m` 和车道净宽 `0.8 m`；这些值不能替代梁外宽或整车碰撞包络。其余待确认参数保持 `null`。

## P1 正式训练入口（只在就绪后使用）

下面路径是占位符，不代表仓库已附带训练权重：

```powershell
python -m isaac.scripts.train --task p1-flat --run-name shu-flat
python -m isaac.scripts.train --task p1-landing --run-name shu-landing --initialize-from "<flat 六桶满档检查点>"
python -m isaac.scripts.train --task p1-stairs --run-name shu-mixed --initialize-from "<负责人在 sim2sim 后指定的 landing 检查点>"
```

所有阶段固定使用[统一接口 v4](INTERFACE.md)，不接旧版检查点。P1 起身和落地仍由环境状态机发奖、计时和交回驾驶，不由网络提交成功标志。P2 当前不训练横移；未来启用已有 `vy_cmd` 需要训练对应指令和课程，不扩网络。

跨阶段 `--initialize-from` 只迁移推理网络；同阶段 `--resume` 才恢复 PPO、速度监督优化器和该阶段课程状态。环境以实际出生时钟结算，不从随机偏移的回合时钟截短落地样本。`--check-only` 列出的数量是待填配置字段数（不是独立测量项目数）；按具体阶段补齐对应项，未给出的 CAD、出生关节／弹簧映射或任务参数都不能透过正式入口。

## 到模和实测后交什么

1. CAD/USD：闭链几何、刚体／关节映射、无云台质量／质心／惯量、轮径、出生姿态和净空。对照本车核实腿长摆角、连杆干涉、气弹簧行程和各掉高带。
2. 固件侧：交付六通道 ID、方向、零点与限位、IMU 安装、驱动力矩包络、延迟及弹簧辨识报告；按[扫频与辨识指南](../SWEEP_IDENT.md)回填机器人与策略配置。接触刚体名单、阈值和释放参数也要按本车确认。
3. 未知参数保留 `null`。不得用参考车参数或扩大随机化替代辨识。配置就绪后才进入目标 Isaac Sim 5.1 / Isaac Lab 2.3.2 / rsl-rl-lib 3.1.2 环境验证；CPU 测试与源码核对不是 GPU 验收。

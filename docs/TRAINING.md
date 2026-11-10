# 多策略训练代码（2026-11-10）

对齐推进指南 v2.1。当前为无云台底盘；真实 USD、机械参数、标定和辨识量仍待填。
本次交付是代码实现，未进行 Isaac 环境运行、GPU 冒烟训练、sim2sim 或实车验收。

## 任务与续训关系

| 任务 | 策略 | 内容 | 建议 Actor 初始化来源 |
|---|---|---|---|
| `p1-flat` | P1 | 平地速度/转向/腿高；指令片段及指令范围课程 | 从头训练 |
| `p1-landing` | P1 | 混入空中出生、airborne 状态、落地约束 | p1-flat |
| `p1-stairs` | P1 | 单/双台阶、坡道、凸起；30% 平地；地形等级课程 | p1-landing |
| `p1-recovery` | P1 | 接管状态库、低姿态起身、高度参考、零力矩窗口；保留粗糙地形 | p1-stairs |
| `p2-spin` | P2 | 双档转速、旋转平移、独立 PD 参数 | p1-flat |
| `p3-jump` | P3 | 0/1/2 次事件、接触驱动相位、五档跳高、引导项退火 | p1-landing |
| `p3-tunnel` | P3 | 横梁/护栏、横梁高度课程、后方地面落地 | p3-jump |

以上是 3 个策略、7 个训练阶段，P1 的各阶段通常依次续训成为同一策略。
Actor 均为 35→256→128→64→6；critic 为 81 维，台阶/起身阶段加入 77 点扫描后为 158 维。
跨阶段用 `--initialize-from` 严格加载 Actor，不裁切/补零网络输入；critic 和优化器重新初始化。
相同任务用 `--resume` 恢复 Actor、critic、优化器、迭代和课程状态。

## 配置与缺参

- `config/robot.yaml`：真实资产映射、几何依赖、执行器、弹簧、延迟与随机化。
- `config/policies/p1/policy_meta.yaml`、`p2/...`、`p3/...`：每个策略的 PD、动作缩放、指令、奖励、阶段、评测。
- 普通 `null` 表示未知；唯一明确例外是 **`action_clip: null`，表示按 v2.1 不裁剪原始动作**。
- 禁用状态库时 `transition_reset.probability: 0.0`，其路径可以为 null；启用后必须提供真实 rollout 库。
- `baseline_evaluation_passed: false` 是未通过，不是默认假定通过；第二阶段推扰还需填写 `phase2_start_iteration`。
- CPU 检查不启动 Isaac，不要求 Torch：

```powershell
python -m isaac.scripts.train --task p1-flat --check-only
python -m isaac.scripts.train --task p2-spin --check-only
python -m isaac.scripts.train --task p3-tunnel --check-only
```

缺参将列出完整配置路径。未选阶段的缺参不会阻塞当前任务；训练不要求先填评测指令。
P3 的最高目标不得超过 `feasible_height_m`。`joint_lower/upper_rad` 是机械限位，腿目标进一步内收 0.05 rad；
轮关节仍连续转动，不在 PhysX 设置轮位置限位。`hip_pivot_positions_b_m` 是左右虚拟腿的真实基座点，不能照抄参考机器人。
USD 中的完整被动关节初态必须由闭链模型提供。

## 云端运行

使用 Isaac Sim 5.1 / Isaac Lab 2.3.2，rsl-rl-lib **3.1.2**（已核对该版本官方 setup.py 和接口源码）。
不升级镜像的 Torch。安装本项目和其训练入口：

```bash
python -m pip install -e '.[train]'
python -m isaac.scripts.train --task p1-flat --run-name p1_smoke --num-envs 512 --iterations 200 --headless
python -m isaac.scripts.train --task p2-spin --run-name p2_first --initialize-from runs/p1_flat/model_5000.pt --headless
python -m isaac.scripts.train --task p3-jump --run-name p3_first --initialize-from runs/p1_landing/model_5000.pt --headless
python -m isaac.scripts.train --task p3-tunnel --run-name p3_tunnel --initialize-from runs/p3_first/model_5000.pt --headless
python -m isaac.scripts.train --task p1-flat --run-name p1_continue --resume runs/p1_flat/model_5000.pt --headless
```

命令中的运行名和 checkpoint 是使用示例，当前未生成这些训练产物。输出目录不得覆盖现有 run。
配置快照和运行元数据写入 `runs/<run>/params/`；checkpoint 和 TensorBoard 日志写入该 run。
所有正式启动都先执行缺参检查；没有用 SCUT 参数或虚假数据替代真实底盘。

## v2.1 已同步内容

1. 原始动作不裁剪；上一动作观测保留原始值。只裁剪转换后的腿位置/轮速度目标，输出单点执行力矩包络。
2. 每回合独立采样四髋零点误差 ±0.01 rad，只影响 Actor 传感输入；不改真实关节角或 PD 反馈。
3. IMU roll/pitch 各 ±1°，同一个固定旋转作用于陀螺和重力；critic 使用真实状态。
4. 各刚体惯量独立 ×0.9–1.1，在质量随机化之后执行，避免后者重新计算惯量覆盖它。
5. 第一阶段推扰 0.25 m/s；第二阶段按配置在 3000 轮升到 1.25 m/s（指南允许范围内的起点）。
6. 第二阶段增加 0.1 s 撞击，100→300 N，8–15 s 间隔，侧向为主；必须先记录基线评测通过。
7. `no_fork` 是二值项，平方项为 `(5*max(abs(dx)-0.05,0))²`；`leg_symmetry` 默认 0，配置拒绝同时开启。

P2 当前采用固定世界航向作为“虚拟云台”参考。模式位 33/34 表示参考航向相对机体 yaw 的 sin/cos；
没有模拟不存在的实体云台。后续装云台时必须增加其真实惯量与 yaw 控制，并同步部署合同。

## 评测、录像与导出

```bash
python -m isaac.scripts.evaluate --task p1-flat --robot runs/p1_flat/params/robot.yaml --policy runs/p1_flat/params/policy_meta.yaml --checkpoint runs/p1_flat/model_5000.pt --output runs/p1_flat/eval --video --headless
python -m pip install -e '.[export]'
python -m tools.export_policy --checkpoint runs/p1_flat/model_5000.pt --robot runs/p1_flat/params/robot.yaml --policy runs/p1_flat/params/policy_meta.yaml --rollout runs/p1_flat/eval/rollout.npz --output runs/p1_flat/export
```

- P1 固定 16 条指令；P2 双向旋转/平移组合；P3 包含不跳基线和五档跳高；具体指令等待本车能力确定。
- 评测关闭域随机化和噪声，固定种子；传感/动作延迟分别使用 policy 的 `evaluation.observation_delay_steps` / `action_delay_steps`（单位 2 ms，必填，不默认 0）。失败之后的自动重置不计入成功或误差。
- 输出 `evaluation.json/md`、`rollout.npz`，可选录像；末尾有效状态输出 `transition_states.npz`。R 的接管库仍由 `handover_states_npz` 指定，两者用途不同。
- 评测旧阶段时重新选择旧 `--task`，用新 checkpoint 回归旧任务，不能仅看新技能回报。
- 导出只接受至少 100 帧真实 rollout 观测；ONNX 输入固定 `[1,35]`，输出 `[1,6]`，与 PyTorch 最大误差须 `<1e-5`。
- 导出包含 ONNX、golden.npz/h、参数头、机器人和策略快照、manifest；未生成 CubeAI C 网络，不声明固件可用。

跳隧道要求轮底越过后沿、所有刚体原点越过后沿、在后方地面稳定保持 1 s。
碰横梁/护栏或顶面会使该次事件失败；不会通过“先落顶面，再驶下去”获得成功。
`collision_body_names` 必须覆盖 USD 全部刚体。每个刚体一个 ContactSensor，通过 `filter_prim_paths_expr`
分别过滤横梁、左护栏和右护栏，使用 `force_matrix_w` 判定真实接触；删除包围球区域猜测。
横梁施加给机器人向上的接触法向力用于顶面惩罚，需在真实资产上验证方向和过滤结果。
跳高输入来自本回合横梁上表面高度加 `clearance_margin_m`，不独立随机；只采样 `tunnel.vx_range_m_s` 的正向速度，vy/wz=0。
隧道仅按位置窗口触发，不再要求 age >= next_trigger；普通跳跃仍保留时间触发条件。
每回合先采样跳跃次数，再放置横梁；次数为 0 时使用 `tunnel.no_jump_beam_pose`（环境局部 xyz + wxyz）把横梁移至地面下，保留正常直行指令。跳跃次数消耗完不在回合中途移动横梁。
测得的 `feasible_height_m` 必须覆盖最大课程横梁高度、制造扰动和余量；隧道评测同样只用直行越障。
刚体原点通过不等价于精确碰撞网格全部通过，完整几何净空仍需模型验收，不能以 CPU 检查替代。

## 训练评审修复（2026-11-10）

- 质量比例分子、分母都转到仿真设备。场景配置不含地形；`_setup_scene` 显式创建地形，克隆一次，仅 CPU 调用碰撞过滤。
- 地面 static/dynamic friction 都为 1.0，friction/restitution combine mode 都为 multiply，参数来自 `robot.training.ground_material`。
- 持续奖励乘 dt 并按 `reward_clip` 限幅；一次性 `termination`、`jump_apex`、`jump_landing`、`jump_impact`、`jump_asymmetric_landing`、`tunnel_crossing` 不乘 dt，也不受持续项限幅，权重为每次事件总量。termination=-4.0，其余权重不变；空中原有终止倍率保留。
- 指令课程按完成回合窗口统计，`command_curriculum.min_completed_episodes` 必填，当前为 4096，校验不得小于 `training.num_envs`；一个窗口至多升级一次，然后清空计数。均值分母用实际采样步数，不用随机初始化后的回合时钟。窗口状态写入 checkpoint。
- 外力用 `permanent_wrench_composer`，每个物理步维护持续时间；`robot.training.randomization.external_wrench_duration_s=10.0`，校验不得小于 `push_interval_s` 上限。来源 SCUT `wheelbipe25_v3/env_cfg.py:161-170` 的 interval 事件：两次采样之间外力持续作用，新采样覆盖旧外力。侧向撞击仍用 `training.disturbance.collision_duration_s=0.1`；最后不足一物理步按占空比保冲量。
- 外力来源：SCUT `source/agent_tasks/agent_tasks/manager/mdp/isaaclab/events.py:438-488`；新接口已核对本地 `runs/api_reference/events.py:1038-1043` 和 `wrench_composer.py:221`。
- output_scale 在 DC 包络裁剪之后生效；执行器透传上限覆盖最大输出比例，避免二次裁掉随机化。电压仅缩放空载转速；髋力矩上限只按回合进度下降 0–10%。
- 训练使用 `init_at_random_ep_len=True`；`params/run.json` 包含 `workspace_dirty`。

必要 CPU 回归：`python -m pytest tests/test_review_fixes.py -q -s`。包括一次完整跳跃的事件奖励总量大于引导奖励总量、步长独立性、窗口课程、包络后缩放、必填配置和隧道指令。
本次未启动 Isaac、GPU PPO、视频评测或实车；场景、PhysX 过滤接触、永久外力、GPU 设备修复仅经过源码核对与静态检查。

后续按用户要求直接调整：课程窗口 4096、持续外力 10 s、P3 `jump_impact=-0.0001`、隧道位置触发和零跳跃回合隐藏横梁。这批调整未运行测试或静态检查。

## 当前边界

- 已写训练、课程、评测和导出逻辑；真实 CAD→USD/MJCF 资产生成、五连杆 CAD 数值标定、
  MuJoCo 双引擎验收及手写恢复控制器 R 不在本次训练代码中伪造。起身任务读取 R 的真实接管状态库。
- 按回报重置采样和历史估计器按指南后置；当前使用均匀高度 bin 和成功率课程。
- 尚未在目标 Isaac/GPU 上运行，训练收敛与 sim2real 未验证。
- 用户要求先完成代码、暂停完整测试；最后只做静态检查及配置加载。先前中间版本的一轮 CPU 检查为 31 passed，
  该结果不覆盖其后的所有代码变动。

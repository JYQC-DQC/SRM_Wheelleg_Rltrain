# 多策略训练代码（2026-11-10）

2026-11-14 revision 7：stairs删除世界+x进展/卡住项，宽核高度权重2→1；仅井字和粗糙地形加入站立/直行/自转/组合。生效规则与停留风险见 [STAIRS_FREE_COMMANDS_20261114.md](STAIRS_FREE_COMMANDS_20261114.md)。本地改动未在Isaac/GPU运行，未更新云端。

2026-11-14 revision 6：中性出界、取消中心走廊、扩大井字/坡面/粗糙覆盖及受限随机出生，以 [STAIRS_BOUNDARIES_20261114.md](STAIRS_BOUNDARIES_20261114.md) 为准。纯出界不扣终止分、不进成功率分子分母、不升降课程；物理失败优先。此版本尚未在Isaac/GPU运行。

## 2026-11-14 stairs生效逻辑修订

### revision 5：高度覆盖与地形分区约束

stairs平地仍占30%，高度均匀采样从配置下限到`spring_extension_height_m-step_height_margin_m`，
当前SCUT参考为0.20–0.43885688 m，覆盖与上台阶辅助相同的最高可用站姿；0.44885688 m是机械几何极限，保留0.01 m余量。
这里指root参考高度，不是髋轴到轮心的腿长。生成资产后运行时按实际弹簧高度重算，不固定依赖模板上限。
后续新flat训练也必须覆盖这一最高可用高度，不能继续将0.35 m当作最终训练上限；
启动前须同步核对该任务的动作限位、被动关节限位和sim2sim映射，否则高指令不可达。
本轮只修改stairs高度采样，独立flat旧配置暂保留；SCUT参考被动限位授权仍仅限stairs，SRM须按自身CAD确定。

奖励分区按地形kind，详见STAIRS_REVISION_20261114.md：flat强约束，up/down/mixed保留台阶弱约束，
grid/slope/rough分别使用中等约束；缓坡允许静态俯仰但保持较强角速度约束。
导轮支撑引起的跟踪/高度/腿加速度豁免，以及导轮单独接触减罚，仅适用于up/down/mixed。
其他地形仍把实际导轮承重视为支撑，不能误判成腾空而获得空中豁免。
真实飞行和下落触地缓冲仍保留原事件规则；台阶弱约束按整个台阶地块生效，并非新增边缘距离状态机。
revision=5，Actor和critic维度不变，旧stairs checkpoint用`--initialize-from`，不能直接`--resume`。
本轮未运行测试、Isaac/GPU或sim2sim；本地改动不会自动更新正在运行的云端训练。

以下为revision 4历史说明，冲突处以上述revision 5为准。

当前以 [STAIRS_REVISION_20261114.md](STAIRS_REVISION_20261114.md) 为准，下面11月13日段落为历史记录。
平地30%恢复站立/直行/纯转向/组合，角速度死区独立0.02；辅助上限取气弹簧最大伸长站姿高度减0.01m。
参考模型硬上限约0.4389m；revision 4按最近台阶高度+[0.19,0.27]m和常规指令构造区间并随机采样一次，
不再对矮台阶固定伸到最长。评测取区间中点；检测持续时续持、消失后0.3s结束，导轮支撑取消辅助。SRM高度待CAD确认。
仅SCUT参考stairs仿真按授权扩展左右front2/rear2被动限位至弹簧极限对应角；SRM及原USD不改。
当前双轮必须仍在末级边缘之后并恢复支撑；课程跟踪不再重复乘高度门控。
速度按地形类型×高度行分别统计，256回合窗口≥60%升速、<30%降速；单纯超时不降地形。
删除额外0.6s导轮豁免，所有原终止接触使用已有0.4s累计机制。按用户指示baseline=true，
stairs启用阶段2调度：phase2_start_iteration=4000，前4000轮弱扰动，之后3000轮渐增，起点前不施加碰撞。
该标记是用户授权，不代表本轮新产生评测通过报告；P1共用计划也影响阶段2的recovery，flat/landing仍为阶段1。
Actor不变，critic373维、course revision=4，旧stairs只能--initialize-from。仅静态/配置和几何核算，未运行训练。

## 2026-11-13 stairs 评审修复

当前实现以 [STAIRS_TRAINING.md](STAIRS_TRAINING.md) 为准：安全平台出生；独立上、下、上下混合台阶；
10% 小范围随机井字障碍；按地形分配直行/倒车速度，取消 flat 随机转向片段；
真实越障并停稳+跟踪回报判晋升，失败降级，按类型调整速度。
stairs 不再随机空中出生，不再给旧 +20/+10 空中奖励；只对下台阶事件收 `stair_impact`。
扫描和路线状态使 stairs critic 变为368维，Actor仍35维/obs_version=2；旧stairs用 `--initialize-from`，不能 `--resume`。
基线门槛仍false、phase2起点仍null，当前不允许启动强扰动训练；不会为能启动而代填通过。
这批只做静态检查和配置加载，未运行测试、Isaac/GPU、sim2sim或实车。

## 2026-11-11 动作反馈与数值安全修复

修复在共用代码路径生效，SRM 和华南虎参考配置共用，不以 `reference_preset` 分流。

- `training.observation_clip` 必填，原始物理分量先限幅、再缩放、最后 nan_to_num。
  上一帧动作输入限到 ±100，原始输出仍不裁剪，单独记录诊断最大值。
  指令/角速度/重力/关节角/力矩/轮心速度/kp/kd/延迟为 ±100，关节速度 ±200；
  腿高指令 [0,1]，机身高度和质量比例 ±10。来源 SCUT V14/cfg_utils.py:75-124。
- `training.numerical_safety` 必填。原始关节速度/机身线速度/机身角速度非有限，
  或绝对值超过 500/100/200，即终止该环境并将本步每项奖励及总奖励置零。
- `training.critic_torque_scale` 必填，两份 robot 配置为 0.05（SCUT V14/cfg_utils.py:133）。
  Actor 35 维、critic 81/158 维不变，obs_version 保持 2。
- **critic 输入分布已改变：旧 checkpoint 禁止 `--resume`，只能 `--initialize-from` 提取 Actor。**
  新 checkpoint 保存限幅/critic 缩放合同，恢复时在加载权重和优化器前比较合同；不匹配直接报错。
  发生过动作指数增长的 Actor，即便可提取也未证明稳定，应先运行反馈诊断再决定是否继续使用。
- `p1-flat` 和 `p2-spin` 不运行腾空状态机，airborne 恒假，倾角阈值固定 `tilt_rad`，
  机身接触/终止倍率固定 1。其他任务的腾空逻辑和奖励权重不变。
- `asset.initial_root_position_m[2]` 必须根据初始关节姿态下轮底触地的机身高度确定，
  若配置离地余量，则为该触地高度加 `training.spawn_clearance_m`（0.01 m）。SRM 同样适用，当前仍为 null。
  华南虎准备工具从 USD 零位姿的 base_link 和左右轮刚体世界坐标计算
  `base_z-wheel_z+wheel_radius_m`；两轮相差 >1 mm 或任一触地高度偏离 0.185 m >1 cm 就报错，
  验证触地高度后再加余量（0.185 来源 supermimic_wheelbipe/tools/mujoco_check.py:58）。
- 第一次完整 reset 的 `sim.forward` 后检查轮底离地高度，超过 `spawn_clearance_max_m=0.03` 或非有限即报错，
  信息包含实测值。其他任务有意的空中出生、恢复库和状态库样本不当作默认出生姿态验收。
- 每轮 TensorBoard 写 `Safety/raw_action_abs_max` 和 `Safety/numerical_terminations`，
  后者为这一轮发生数值安全终止的环境次数（同一槽位重置后再次失败会再次计数）。

反馈诊断（本次只新增工具，不执行）：

```bash
python -m tools.check_action_feedback --checkpoint runs/<run>/model_655.pt --robot config/robot.yaml --policy config/policies/p1/policy_meta.yaml --observations runs/<run>/eval/rollout.npz
```

`observation[N,35]` 为有限的固定初始观测，每行一条反馈轨迹；只把 Actor 输出接回上一动作槽位，
其余分量固定。限幅开/关各迭代 400 步，输出超过 1e6 的环境数、非有限环境数和原始动作最大绝对值。
本次不运行 CPU 测试、反馈诊断、USD 准备工具、Isaac/GPU 训练，也不推送。

对齐推进指南 v2.2（2026-11-12 的修改见 docs/SCUT_LATEST.md 末尾和 docs/LESSONS.md）。当前为无云台底盘；真实 USD、机械参数、标定和辨识量仍待填。
本次交付是代码实现，未进行 Isaac 环境运行、GPU 冒烟训练、sim2sim 或实车验收。

## 任务与续训关系

2026-11-12 landing训练补充：仅 `p1-landing` 的宽核高度奖励显式覆盖为1.5；
新增仅训练启用的空中出生首次落地事件诊断，不改变奖励之外的终止/课程/观测，不修改评测分支。
事件生命周期、互斥结果、配置阈值及TensorBoard分母见 [LANDING_TRAINING.md](LANDING_TRAINING.md)。
旧启动配置需同步 `stages.landing.landing_diagnostics` 和reward_overrides；模板修改不影响已启动训练。

| 任务 | 策略 | 内容 | 建议 Actor 初始化来源 |
|---|---|---|---|
| `p1-flat` | P1 | 平地速度/转向/腿高；指令片段及指令范围课程 | 从头训练 |
| `p1-landing` | P1 | 混入空中出生、airborne 状态、落地约束 | p1-flat |
| `p1-stairs` | P1 | 单/双上、下、混合台阶，井字障碍；30%平地；分地形速度与真实越障课程 | p1-landing |
| `p1-recovery` | P1 | 随机倒地出生、低姿态起身、高度参考、零力矩窗口；保留粗糙地形 | p1-stairs |
| `p2-spin` | P2 | 双档转速、旋转平移；50% 平地、30% 小起伏、20% 缓坡混训 | p1-flat |
| `p3-jump` | P3 | 0/1/2 次事件、接触驱动相位、五档跳高、引导项退火 | p1-landing |
| `p3-tunnel` | P3 | 横梁/护栏、横梁高度课程、后方地面落地 | p3-jump |

以上是 3 个策略、7 个训练阶段，P1 的各阶段通常依次续训成为同一策略。
Actor 均为 35→256→128→64→6；flat critic为81维，landing为90维，recovery/P2为158维，stairs为373维（11月14日revision 4）。
跨阶段用 `--initialize-from` 严格加载 Actor，不裁切/补零网络输入；critic 和优化器重新初始化。
相同任务用 `--resume` 恢复 Actor、critic、优化器、迭代和课程状态。

## 配置与缺参

2026-11-13 速度课程门槛调整：两套 P1 模板的 `command_curriculum.success_fraction`
和 landing 的 `command_curriculum_landing_gate.success_rate` 从 0.8 改为 0.75。
4096 回合窗口、至少 256 个最高出生高度档落地事件、每窗口至多升 0.05 均不变；
高度课程 `air_height_curriculum.success_rate` 保持 0.8。配置只在启动时读取，运行中的任务不会热更新。
75% 是速度课程升级资格，不代表干净落地成功率或最终验收标准。

### 2026-11-13：P1 静止与高速俯仰

- P1 的 `stand_still` 权重从 -1 改为 -2（SCUT 已发布 flat_and_rotation 配置
  `pretrained/26_infantry/flat_and_rotation/2026-07-29_23-20-03/params/env.yaml:1706`）。
  公式仍是零平移指令下的航向系水平速度绝对值之和；死区仍为 0.1。
  单轴溜车 0.05 m/s 时从 -0.05/s 变为 -0.10/s，不是位置保持或回到原地的奖励。
- 俯仰惩罚保留 `(a*exp(-vx²/b)+c)² * gravity_x² * ground_mask` 的原形式，
  之后仍乘原权重和 dt。删除上一版硬下限，改为连续衰减；`vx` 是实测航向系前向速度。
  必填参数为 `training.reward_parameters.pitch_velocity_amplitude/sigma/offset`，分别对应 a/b/c，
  都必须为有限正数，b 的单位为 (m/s)²。P1 从原来的 2/3/2 改成 1/4/3：
  零速系数仍为 16，同一倾角下 ±2 m/s 保留 70.9%，±3 m/s 保留 60.3%，高速极限为 56.25%。
  比例针对平方后的惩罚项，不是倾角阈值，也不是总奖励。
- SRM 与 SCUT P1 模板同步，P1 四阶段都继承这两项调整。stairs/recovery 的俯仰权重仍覆盖为 -2，
  flat/landing 仍为 -3；landing 腾空时俯仰负罚关闭，腾空/缓冲期站定惩罚关闭的逻辑保留。
  P2/P3 的 a/b/c 填 2/3/2，保留它们的惩罚曲线及 stand_still=-1。
- 腿速度惩罚与 SCUT 同阶段相同，保持不变；加速度惩罚和落地引导按下节回调。
  不调整腿角、动作平滑、指令分布或落地事件总额；观测维度和 obs_version 不变。
  旧 policy 快照缺少新系数会在加载时报错；华南虎需重新运行 `tools.prepare_scut`，已启动训练不会自动更新。
  奖励变化后建议用 `--initialize-from` 继承 Actor，再训练 critic；本项没有改变 checkpoint 的观测合同。
- 本批仅做静态检查与公式数值核算，不运行 pytest、Isaac/GPU 训练或 sim2sim；抑制溜车和高速倾斜的效果待验证。

### 腿速度与加速度对照（2026-11-13）

本轮为减轻快速缓冲/制动的代价，把 P1 加速度权重统一降低 10 倍：flat -2e-5→-2e-6，
landing/stairs/recovery -4e-6→-4e-7。仍保留 flat 与后续阶段的 5:1 比例；这是设计初值，不是验证后的最优值。
P1 腾空期间此项为 0，p1-landing 空中出生首次落地的缓冲期也为 0；普通地面出生不新增缓冲窗口。
掩码覆盖状态转换前后，避免在缓冲结束的同一步补罚刚发生的缓冲动作。
landing 首次过程按事件自身的 flight/cushion 判断，不叠加旧 airborne 的 0.3 s 接触退出延时：
缓冲结束边界步仍屏蔽，下一策略步在地面即恢复。之后再次腾空，只有 airborne 成立且当前仍满足
双轮无接触、轮底离地和机身高度条件时才屏蔽；不会重开首次缓冲。其他 P1 阶段保持原 airborne 门控。
所有屏蔽步仍更新上一帧关节速度，恢复惩罚时只比较相邻策略步，不累计整个腾空/缓冲期的速度变化。
P2/P3 不增加或改变加速度项，也不改现有状态机、腿速度与动作平滑项。

仅 p1-landing：空中轮速对准权重 8→6；伸腿引导权重 4→3，最大惩罚及未饱和段斜率均降低 25%。
轮速对准的是航向系实际水平地速，不是 vx 指令；首次任意刚体接触后关闭，不要求缓冲中继续追预转轮速。
其意图是减少触地瞬间的轮地相对速度，稳定落地不等于立即把水平速度变为零；
当前仍用机身速度近似两轮轮心速度，摆腿/机身转动影响尚未计入。
伸腿引导原本只罚不奖，继续只罚不奖；SCUT 目标腿长仍为 0.28 m、归一化缺口仍为 0.1 m，
SRM 目标腿长仍为 null。只在首次触地前生效，接触后不约束伸缩，成功/失败/进展等事件总额不变。
两套 P1 模板同步，需重新生成训练配置后启动；已有 checkpoint 和正在运行的 viewer 不会因此改变。

比较的是实际主动腿关节角速度/角加速度，不是虚拟腿摆角，也不是动作的一阶/二阶差分。
以下权重均在单项裁剪前，连续奖励均乘策略 dt；相同物理轨迹下应比较每秒累计代价。

| 配置 | 物理 / 策略步长 | 腿速度平方和权重 | 腿加速度平方和权重 |
|---|---|---|---|
| 本项目 P1 flat | 2 / 10 ms | -0.005 | -2e-6，速度按 10 ms 差分 |
| 本项目 P1 landing | 2 / 10 ms | -0.001 | -4e-7，速度按 10 ms 差分；腾空/首次缓冲屏蔽 |
| SCUT V14 flat | 5 / 20 ms | -0.005 | -5e-7，使用 robot.data.joint_acc |
| SCUT V14 Flat-v1 landing | 5 / 20 ms | -0.001 | -1e-7，使用 robot.data.joint_acc |
| 复旦 plane 当前默认配置 | 5 / 10 ms | -5e-5，四腿关节 | -2.5e-7，含轮子在内的六关节 |
| 复旦 jump 当前默认配置 | 5 / 10 ms | 未启用 | 未启用（配置已注释） |

本项目加速度为 `(qdot_t-qdot_previous)/0.01`，复旦同样除以策略步长 0.01，
复旦的 qdot 先由 5 ms 关节位置差分得到；观测缩放 0.05/0.0025 不作用于这些奖励。
SCUT 的原始腿速度和加速度奖励都没有观测缩放，奖励乘 0.02。
对于相同且低频平滑的关节运动，dt 积分抵消每秒步数，不应再把权重按 50/100 Hz 成倍放大；
差分已除以时间，也不能把所有加速度代价统一按步长平方补偿。

因此本项目 flat/landing 的速度项分别等于 SCUT 对应阶段，flat 是复旦 plane 的 100 倍；
在惩罚启用且等效平滑关节加速度下，flat/landing 的加速度项分别约为 SCUT 对应阶段的 4 倍（此前 40 倍），
flat 对复旦 plane 的腿关节贡献约为 8 倍（此前 80 倍）。不能把这个倍数解释成落地冲击或整条轨迹的必然倍数：
不同采样/差分窗口会滤掉不同频段；复旦还有轮加速度贡献。
本项目单项裁剪为 ±2.5/步，复旦 plane 为 ±1×dt/步（即 ±1/s），SCUT 上述奖励汇总没有同样的单项裁剪。

量级例子（计算，不是仿真）：四个腿关节各以 0.1 rad 幅值、2 Hz 正弦运动，
本项目 flat 速度与加速度项平均约扣 0.0158/s、0.00100/s，landing 启用惩罚时约扣 0.00316/s、0.000199/s。
较大系数不等于低频摆动一定受强约束；加速度平方项也可能过度压制快速制动，本轮减小并按阶段屏蔽，效果待训练。
原始动作二阶差分不除 dt，不能与物理关节加速度混为一谈；它的步长缩放规律也不同。

来源：SCUT `wheelbipe25_v3/env.py:3506-3515,4002-4005`，
`wheelbipe_V14/env_cfg.py:871-872,1085-1086,1665-1666`；
复旦 `plane/wheel_legged_gym/envs/base/legged_robot.py:134-144,168,325-330,1270-1275,1752-1760`，
同目录 `legged_robot_config.py:123,197-198,207,249`，
`jump/wheel_legged_gym/envs/base/legged_robot_config.py:184-210`（具体机器人配置未覆盖这些项）。
待确认：本地 `runs/api_reference` 没有 `ArticulationData.joint_acc` 定义，在线源码读取未成功，
因此 SCUT 的实际加速度更新/缓存窗口尚不能确认；冲击及高频抖动需用相同轨迹实测，不宣称已精确等效。

### 配置来源与缺参

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

### 2026-11-12：P2 同任务混合地形

`p2-spin` 从第一轮混合平地50%、随机起伏30%、缓坡20%，不新增 `p2-rough`，不单独续训 rough。
布局借鉴 SCUT `RM_ROTATION_TERRAINS_CFG_99`，简化为三类，比例为本项目设计选择。
起伏使用 SCUT 0–3 cm、5 mm 噪声步长、0.2 m 下采样；坡角 ±0.1 rad（约±5.7°），坡地出生点放在坡面。
每块9×9 m，8行10列，按行生成不同几何难度，初始环境随机取所有行；这不是训练升级课程。
不使用 P1 按位移升降级、台阶信号、抬腿指令、进度/卡住奖励，P2 腾空状态仍禁用。
扫描仅用于局部地面高度和 critic；Actor输入、模式位、动作与 obs_version=2 不变。
旧 P2 critic 为81维，新版158维，因此用 `--initialize-from` 提取 Actor，禁止用旧 P2 `--resume`。
重跑 `tools.prepare_scut` 生成 `policy_p2.yaml` 后启动；SRM P2 同步地形设计参数，真实资产/PD缺参仍留空。
P2 评测也使用混合地形，JSON按出生地块给出 `spawn_terrain_groups`；移动时可能跨地块，不能当成全程地形标签。
历史估计器及华南虎/复旦算法对比见 [FLAT_EVALUATION.md](FLAT_EVALUATION.md)。
本批未运行测试、Isaac/GPU训练或评测，比例和范围尚无收敛证据。

### 2026-11-12：地形边界与射线兜底

`p1-stairs`、`p1-recovery`、`p2-spin` 使用有限地块网格（stairs为8行20列、8m方块，recovery为8行10列8m，P2为8行10列9m），以世界原点为中心；
此前网格外没有任何地面，也没有出界判定，机器人可能驶出边缘下落，直到约 10 s 后触发 100 m/s 数值保护。
`p1-flat`/`p1-landing` 使用无限平面，不受影响。现在的处理：

- 地形配置新增 `border_width_m`（默认 5 m）：IsaacLab 在网格外加一圈顶面与地面齐平的平地。
- 新增 `boundary_margin_m`（默认 0.5 m，同 SCUT V14）：机身离开“网格减去余量”的范围即按 **timeout** 重置，
  不给终止惩罚，PPO 在边缘正常自举价值（SCUT `wheelbipe_V14/env.py:540-564`）。
  出界占比写入 `Episode_Termination/out_of_bounds`。
- `p1-stairs`/`p1-recovery` 的地形等级课程忽略出界回合，等级保持不变，避免把走到网格边缘当成通过地块。
- 高度扫描射线未命中（非有限值）时：地面高度取命中射线的中位数，全部未命中时沿用上一有效值；
  critic 扫描用该地面高度填补；台阶检测不计未命中射线。2026-11-13起stairs改用轮下局部邻域地面参考，见专页。

新增配置字段为必填，旧 run 快照需用新的 policy YAML；字段本身不改变 Actor 或 critic 维度。
出界比例、价值估计和课程速度的变化尚未在 GPU 训练中验证。

### 2026-11-12：历史估计器（已实现，默认关闭，未训练）

按指南 §7.2 实现：最近 `frames` 帧 Actor 观测（与部署一致，含延迟、噪声和限幅）→ 128 → 64 → 5，
输出机体系线速度 3 维和左右轮接触 2 维（Sigmoid 概率）。估计值 `detach` 后接在 35 维观测之后，Actor 输入为 40。
仿真真值只作监督标签：速度 MSE、接触 BCE，独立 Adam，在每次 PPO 更新之后用同一批 rollout 训练，
PPO 梯度不进入估计器（`isaac/wheelleg_tasks/history_policy.py`）。重置后的第一帧填满整段历史。

- 默认 `history_estimator.frames: 0`、`obs_version: 2`，训练、评测、导出与之前完全相同；
  缺少该块的旧 run 快照按关闭处理。
- 开启：policy YAML 设 `obs_version: 3`、`history_estimator.frames: 5`；训练参数在 `training.history_estimator`。
  两者必须同时修改，否则加载即报错。
- 从现有单帧模型开始：用 `--initialize-from`。35 输入的 Actor 会在新增 5 列补零，开始时动作与原模型完全一致；
  估计器从头训练。不能 `--resume`（观测合同和 obs_version 都不同）。
- 评测脚本把历史一并传给模型，`rollout.npz` 额外保存 `history`；导出生成双输入 ONNX。
- 规模：估计器 31,109 参数，Actor 52,038 参数，合计 83,147。
- 已做 CPU 检查：配置约束、缓冲区语义、补零迁移等价、rsl_rl 3.1.2 下 PPO 与估计器联合更新、
  双输入 ONNX 与 PyTorch 一致。**没有 GPU 训练、没有收益证据，不部署。**

## 评测、录像与导出

stairs键鼠MuJoCo试驾入口为`python -m tools.play_stairs`，地图取该run配置，
有单/双上下台阶、井字小凸起、坡/起伏及难度选择。见 [MUJOCO_STAIRS.md](MUJOCO_STAIRS.md)。
沿用现有sim2sim的简化机器人，缺少独立导轮，不能代替导轮支撑动作验收或正式Isaac评测。

### 2026-11-12：flat 选模评测

`p1-flat` 默认使用精细评测；其他任务保持原评测，`--suite legacy` 可复现旧 flat 16 用例。
新协议、指标解释、选模步骤及 SCUT 方法对照见 [FLAT_EVALUATION.md](FLAT_EVALUATION.md)。
支持一次比较多个 `--checkpoint`，共同使用同一份机器人/策略合同和评测条件。
旧 run 快照缺少 `evaluation.flat_suite` 时，用 `--evaluation-policy` 从新的 policy YAML
**只读取 training.evaluation**；不会替换原 run 的控制增益、动作尺度、训练奖励或指令上限。
速度/转速/高度门槛与训练指令课程一致（`command_curriculum`），名义用例的延迟取训练范围中值；
其余门槛是工程验收目标，不是已经通过验证的机器人能力。

```bash
python -m isaac.scripts.evaluate --task p1-flat \
  --robot runs/<run>/params/robot.yaml --policy runs/<run>/params/policy_meta.yaml \
  --evaluation-policy config/reference/scut_p1.yaml \
  --checkpoint runs/<run>/model_5000.pt runs/<run>/model_6000.pt \
  --output runs/<run>/flat_selection --headless
```

本次没有运行 pytest、Isaac/GPU 评测或训练；只进行源码检查、格式整理与静态检查。


```bash
python -m isaac.scripts.evaluate --task p1-flat --suite legacy --robot runs/p1_flat/params/robot.yaml --policy runs/p1_flat/params/policy_meta.yaml --checkpoint runs/p1_flat/model_5000.pt --output runs/p1_flat/eval --video --headless
python -m pip install -e '.[export]'
python -m tools.export_policy --checkpoint runs/p1_flat/model_5000.pt --robot runs/p1_flat/params/robot.yaml --policy runs/p1_flat/params/policy_meta.yaml --rollout runs/p1_flat/eval/rollout.npz --output runs/p1_flat/export
```

- P1 legacy 固定 16 条指令；flat 精细协议见上文；P2 双向旋转/平移组合；P3 包含不跳基线和五档跳高。
- 评测关闭域随机化和噪声，固定种子；传感/动作延迟分别使用 policy 的 `evaluation.observation_delay_steps` / `action_delay_steps`（单位 2 ms，必填，不默认 0）。失败之后的自动重置不计入成功或误差。
- 输出 `evaluation.json/md`、`rollout.npz`，可选录像；末尾有效状态输出 `transition_states.npz`。起身任务不再使用接管状态库（2026-11-12）。
- 评测旧阶段时重新选择旧 `--task`，用新 checkpoint 回归旧任务，不能仅看新技能回报。
- 导出只接受至少 100 帧真实 rollout 观测；ONNX 输入 `[1,35]`（obs_version 3 另加 `obs_history[1,frames×35]`），
  输出 `[1,6]`，与 PyTorch 最大误差须 `<1e-5`。
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
  MuJoCo 双引擎验收及手写恢复控制器 R 不在本次训练代码中伪造。起身任务从随机倒地姿态出生，不读取接管状态库。
- 按回报重置采样按指南后置；当前使用均匀高度 bin 和成功率课程。历史估计器已实现但默认关闭，未训练。
- 尚未在目标 Isaac/GPU 上运行，训练收敛与 sim2real 未验证。
- 用户要求先完成代码、暂停完整测试；最后只做静态检查及配置加载。先前中间版本的一轮 CPU 检查为 31 passed，
  该结果不覆盖其后的所有代码变动。

# 最新框架运行 SCUT 华南虎参考模型

2026-11-12 landing 空中出生高度课程（只跑了 CPU 测试，未在 Isaac 中运行）：出生高度偏移上限从 0.2 m 起，
按最新一档的首次恢复成功率（每 1024 个事件一个窗口，≥ 0.8）逐级放到 0.28/0.35/0.42 m。评测和 stairs/recovery 不变。
课程状态存进 checkpoint，旧 landing checkpoint 只能 `--initialize-from`。需重新运行 `tools.prepare_scut`。
同时给 landing 的指令课程加落地门槛：同一窗口内速度通过率 ≥ 0.8 且落地首次恢复率 ≥ 0.8（至少 256 个事件）才升级，
避免速度升得太快变相让落地变难；flat 等阶段不变。landing 空中出生概率 0.3→0.4（stairs/recovery 仍 0.3）。
详见 `LANDING_REWARD_DESIGN.md`「空中出生高度课程」「指令课程的落地门槛」。

2026-11-12 平地“上下起伏换前向速度”的限制（只跑了 CPU 测试，未在 Isaac 中运行）：

- 速度口径：跟踪误差、课程和评测的前向速度改为航向系（只含 yaw）世界水平速度。原来的机体系 vx·cos(俯仰)（同 SCUT）
  在机身俯仰时把竖直速度漏进前向速度，起伏与俯仰同相就能“赚”到速度奖励。stand_still 和 roll/pitch 惩罚里的速度也改用航向系。
- 竖直速度：`vertical_velocity` 改为 (世界系 vz − 高度参考变化率)²。变化率取斜率限制后的高度指令，recovery 起身段取平滑起身曲线的导数，
  stairs 的台阶抬高是阶跃不计速率。P1 权重 -0.5→-4。
- 姿态：`angular_xy` -0.05→-0.2（复旦 ang_vel_xy），`pitch_penalty` -2→-3；roll 不加强（高速转向要侧倾）。
- 新增 `leg_joint_acc` -2e-5：髋关节加速度按 100 Hz 策略步差分，不是 SCUT 的物理步 joint_acc，权重不照搬 -5e-7。
  它在约 2.5 Hz 与 leg_joint_vel 相等，主要压高频腿部抖动；本车 2 cm 起伏只对应约 0.07 rad 髋角，低频起伏主要靠竖直速度项。
- 估算（高度正弦起伏）：2 cm/2 Hz 每秒合计约扣 0.35（原约 0.2），3 cm/3 Hz 约 1.1（原约 0.45）。
- 阶段：flat/landing 用新权重；stairs/recovery 用 reward_overrides 保留旧的 pitch/竖直速度/角速度权重；
  landing/stairs/recovery 的 leg_joint_acc 按平滑项惯例取 ×0.2。P2/P3 权重未改，但共用的速度口径和竖直速度定义已变。
- 未改：stairs/P3 的 air_wheel_alignment 仍用机体系 vx。
- 观测和 critic 合同不变，可 `--resume`；奖励尺度变了，续训初期 critic 会重新适应。需重新运行 `tools.prepare_scut`。
- 校准：看 `Episode_Reward/leg_joint_acc`，若早期超过约 -0.3/s，说明主要在罚探索噪声，应减小权重。

2026-11-12 landing奖励第二版（只跑了 CPU 测试，未在 Isaac 中运行）：成功/失败改为发生时立即结算；
首次触地后加一次性缓冲期；腾空时保留姿态正奖励，加只罚不奖的轮心居中和轮速对准（目标为真实地速）；
80% 空中出生速度跟随指令、指令冻结到落地窗口结束；critic 加 9 维事件状态（landing state_space 90）。
旧 landing checkpoint 只能 `--initialize-from`。详见 `LANDING_REWARD_DESIGN.md`。

2026-11-12 landing训练更新：参考与通用P1的landing阶段宽核权重覆盖为1.5；
新增首次空中出生落地诊断和 `Landing/*` TensorBoard日志，必须重新生成或同步实际训练配置。
（该条写的“不修改落地奖励项”已被后续提交和上一条取代。）详见 `LANDING_TRAINING.md`，本批未运行Isaac/GPU。

## 2026-11-12 当前补充：P2同任务混合地形与flat选模（未GPU验证）

`p2-spin`直接混训50%平地、30%随机小起伏、20%缓坡，不新增 `p2-rough` 或单独rough训练。
参考SCUT `terrains.py:672-699` 的旋转地形组合，采用其 `RANDOM_UNIFORM_FOR_RM` 噪声参数；
比例和±0.1rad坡角为本项目设计值，不包含原版全部小台阶/阶梯坡。坡面出生，固定混合全部难度行，
不使用P1距离课程。Actor仍35维，P2 critic增加扫描后158维，旧P2用 `--initialize-from`，不要 `--resume`。
重新运行 `tools.prepare_scut` 生成 `policy_p2.yaml`。P2评测也走混合地形，按出生地块报告分组指标。
flat精细选模、多检查点、轨迹输出和历史估计器/复旦对照见 `docs/FLAT_EVALUATION.md`。
旧章节是历史修改记录，涉及“P2尚无配置”“P2只有平地”的描述不代表当前状态。
本次没有运行pytest、Isaac/GPU或实车，不推送。

分支 codex/scut-latest-adaptation 基于 54e467c。仅使用最新 P1/P2/P3 框架，当前适配并验证 P1-flat；
没有合入旧 srm_scut_env、旧 PPO 适配器、教师权重或旧训练 checkpoint。

## 资产和参数边界

使用 SCUT Wheelbipe_V14_2_CFG 的完整 USD（包含云台），保留质量惯量、闭链、被动/导向关节、云台 actuator。
六个主动电机和两气弹簧由最新版500 Hz控制路径施力，策略100 Hz。
SCUT参考资产是理想PD模型，使用源码的髋40 Nm、轮5 Nm、髋60/2及轮0/0.2；
不把速度限幅谎称为空载转速，不填写未知的DC堵转/空载辨识量；该参考模式不会调用DC包络。
弹簧采用参考V14的400–600 N线性设定和50 N s/m阻尼；不是SRM实测结果。

prepare_scut 在目标 Isaac 环境中用 USD 读取刚体列表、髋轴锚点及弹簧行程，记录 USD/资产源码 SHA-256。
虚拟腿基座取同侧前后髋轴在base坐标系的中点。USD的主动髋轴无有限角度止挡，因此模板里的±1.5 rad
只是本次仿真目标范围（再内收0.05 rad），不会写成PhysX机械限位。
指令范围、升降速度、课程阈值、腾空分类阈值和默认摩擦0均为显式的初始设计选择，需独立评测调整。
参考资产中保留的被动关节armature/damping和云台控制来自源资产，不宣称无云台SRM已验收。

仅 variant=reference_simulation_only 且 reference_preset=scut_v14_2 可使用这条参考路径；
SRM config/robot.yaml及P1/P2/P3默认文件未填写或修改，原实测门禁仍生效。参考配置禁止用于实车部署。

## 云端准备（新目录，镜像自带环境）

使用 Isaac Sim5.1 / Isaac Lab2.3.2 / RSL-RL3.1.2。不要source旧项目的activate_cloud.sh或.cloud-deps。
项目需保留Git元数据，训练入口会记录实际提交及dirty状态；资产引用原参考目录，不改开源仓库。
设Python为镜像/workspace/isaaclab/_isaac_sim/python.sh，并将项目根目录加入PYTHONPATH。

```bash
cd /root/gpufree-data/wheelleg/scut_latest_framework
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
/workspace/isaaclab/_isaac_sim/python.sh -m tools.prepare_scut \
  --reference-package /root/gpufree-data/wheelleg/srm_scut_cloud/reference/agent_world \
  --output runs/scut_reference --headless
/workspace/isaaclab/_isaac_sim/python.sh -m isaac.scripts.train \
  --task p1-flat --robot runs/scut_reference/robot.yaml --policy runs/scut_reference/policy_meta.yaml --check-only
/workspace/isaaclab/_isaac_sim/python.sh -m isaac.scripts.train \
  --task p1-flat --robot runs/scut_reference/robot.yaml --policy runs/scut_reference/policy_meta.yaml \
  --run-name scut_latest_smoke512 --num-envs 512 --iterations 200 --headless
```

生成目录和run-name不可覆盖已有目录，重复执行需换新名称。上述是从零训练，不携带旧权重。
要开UI，去掉--headless，并使用有显示权限的远程桌面终端；当前图形扩展缓存未在新框架验收。

## 新框架内续训

只使用新框架生成的checkpoint：

```bash
/workspace/isaaclab/_isaac_sim/python.sh -m isaac.scripts.train \
  --task p1-flat --robot runs/scut_latest_smoke512/params/robot.yaml \
  --policy runs/scut_latest_smoke512/params/policy_meta.yaml \
  --resume runs/scut_latest_smoke512/model_199.pt \
  --run-name scut_latest_continue --num-envs 2048 --iterations 2000 --headless
```

先评测冒烟结果，再决定是否正式运行。P1-flat的成功不代表落地、台阶、起身、旋转、跳隧道已经可用；
其余阶段仍受各自配置、状态库和模型验收门禁限制。

## 本次启动修复

PD增益显式float32，允许合法YAML整数增益参与浮点随机化。
DelayBuffer采样使用其公开time_lags.dtype，兼容目标镜像int32缓冲区。
异常在Kit关闭前打印，避免只看到进程退出0却没有检查点而误判成功。

测试位于本地tests/test_scut_latest.py，遵守当前仓库“测试仅保留本地”的约定，不强制加入Git。

## 验证记录与尚未完成项

本地执行：`python -m pytest -q` → 4 passed；`python -m ruff check .` → All checks passed!；
`python -m ruff format --check .` → 28 files already formatted。
当前分支仅有4项本地适配回归；这不代表重写框架全部数值行为已充分测试。
单环境2轮实际GPU PPO已运行并生成model_0.pt/model_1.pt。
初次512环境运行发现PhysX逐次摩擦setter中间状态错误，已改为先清零dynamic、再写static、最后写dynamic；
修复后的 `scut_latest_smoke512_v2` 最后确认运行至142/200轮，该时日志未见Python异常和PhysX error。
随后SSH连接在认证后被服务器关闭，尚未核实200轮完成及最终checkpoint，不宣称完整冒烟通过。
本地最后补齐的16组评测命令与文档尚未同步云端；不要把云端旧评测快照当作本地最终配置。
下一步：恢复SSH访问后同步最终源码/配置，在新run中验证完整512×200冒烟和独立评测。
未启动2048环境正式训练；旧模型未迁移，SCUT开源仓库未修改。

## 同步小修版本 644775e（2026-11-10）

适配分支已合入最新版课程窗口、持续外力和隧道触发修复；华南虎独立P1配置同步
command_curriculum.min_completed_episodes=4096，参考机器人模板同步external_wrench_duration_s=10.0。
保留华南虎USD检查、理想PD参考路径和运行时dtype/摩擦setter顺序适配，不恢复旧版训练逻辑或权重。
之前142/200轮的云端记录仅对应旧适配版本，不能作为本次修订的验证证据。
按用户要求，本轮未运行测试、Ruff、格式检查、配置预检或GPU训练；未上传覆盖云端运行目录。
已生成的runs/scut_reference配置不会自动更新。运行本次版本时，重新用prepare_scut生成一个新的
输出目录（例如runs/scut_reference_644775e），再用该目录的robot.yaml和policy_meta.yaml启动新的run。
不要复用含100回合课程窗口或0.01秒外力持续时间的旧生成配置。
# 2026-11-11 共用数值安全更新

共用观测已修复上一动作反馈：物理分量先限幅再缩放、最后清理非有限值，critic 力矩缩放为 0.05。
必须重新使用 `tools.prepare_scut` 生成配置；旧 runs 中的 robot.yaml 不会自动更新。
旧 checkpoint 的 critic 分布不兼容，禁止 `--resume`，只能 `--initialize-from` 提取 Actor。

模板出生高度不再硬填 0.38 m，而留 null 给准备工具计算。工具从 USD 零位姿读取 base_link、
左右轮刚体世界坐标，验证触地高度接近 0.185 m、左右差不超过 1 mm，再加 0.01 m 余量。
首次重置后还检查实际轮底离地高度不超过 0.03 m。计算不符合条件就报错，不自动回退旧高度。

这批修改未运行测试、USD 准备、反馈诊断或 Isaac/GPU 训练；高度检查是否通过尚无实测结果。


# 2026-11-11 平地起立修复（分支 fix/flat-standup，未测试）

现象：`model_1000` 把腿折到最短、轮子悬空，用导轮和后大腿撑地不动，回报仍接近满分。本次修改：

- 接触：`asset.undesired_contact_body_names` 扩为机身、腿连杆、云台、导轮（只罚，二值项）；
  新增 `asset.termination_contact_body_names`（机身、云台、导轮）。倾倒/触地须连续
  `training.termination.duration_s=0.4` 才终止，数值异常仍立即终止。来源 SCUT V14/env.py:118-139。
- 出生：`p1-flat` 训练回合用 `training.leg_reset` 的闭链逆解随机两条腿的腿长/摆角，机身 roll/pitch ±0.15 rad、
  yaw 随机，出生高度按较低的轮底离地 `spawn_clearance_m` 计算；前 `settle_s=1.0` 不按倾倒/触地终止。
  评测仍用默认零位姿出生。弹簧连杆关节仍写默认值，闭链由 PhysX 收敛，需实测复位后的关节速度尖峰。
- 指令：最终范围 vx ±2.7 m/s、wz ±2π rad/s、冲刺 ±3.0 m/s；课程仍从 25% 起。死区 0.1 内的指令按 0 跟踪。
- 课程：允许误差 = 0.1 + 0.25 × 回合平均指令幅值，另要求回合平均高度误差 < 0.03 m；原地不动或趴地不能升级。
- 奖励：`stand_still` 改为速度绝对值；新增 `leg_joint_vel`、`wheel_vel`、`action_smoothness_leg/wheel`。
  `value_loss_coef` 改为 4.0（SCUT V14 实际值）。

必须重新运行 `tools.prepare_scut` 生成配置：它把接触名单正则展开成 USD 实际刚体名，未匹配的正则
（例如 USD 没有 `*_guide_link`）打印为 `UNMATCHED_CONTACT_PATTERNS` 并写入 `reference_manifest.json`。
奖励项和课程状态已变，旧 checkpoint 不要 `--resume`，从零训练。
本次未运行测试、Ruff、`prepare_scut` 或 Isaac/GPU 训练；本地 tests/ 里依赖 `contact_base`、二维 `command_error_sum`、
旧 `stand_still`/`undesired_contact` 数值的用例需要同步更新。

## 2026-11-11 第二轮调整（standup_4096_2000 停在 281 轮后）

第一轮从第 40 轮起 `height_error` 停在 -0.57（机身约 0.18 m，腿折叠），回合跑满但约 30% 时间有非轮触地。调整：
新增宽核 `track_height_wide`（σ=0.025，权重 1）；高度指令上限 0.3→0.4 m（未验证腿长可达）；
`height_error` -1→-1.5；`lin_vel_error` -1→-20；腿连杆加入终止名单。未冒烟，直接 4096×2000 从零训练。

## 2026-11-11 第三轮调整（只改代码，未部署、未测试）

- 课程起步 `initial_fraction` 0.25→0.4；高度指令上限 0.40→0.35 m。
- `p1-flat` 加高度门控：高度误差 5 cm 内 `track_lin_vel`/`track_ang_vel` 全给，10 cm 外为 0（SCUT linear_band）。
- `lin_vel_error` -20→-16（即 e²：差 1 m/s 每秒扣 1）；`height_error` -1.5→-2（误差 10 cm 每秒扣 2）。
- 腿位置目标限幅恢复 SCUT 的 ±3.14 rad（余量 0）；出生摆角改为 SCUT 的 [-90°, 135°]，机身从 0.38 m 落下；
  不含 predefined_reset_ground 倒地出生，不随机关节初速度。
- TensorBoard 新增 `Curriculum/command_fraction`。
需重新运行 `tools.prepare_scut`（模板已变）。

## 2026-11-11 第四轮调整（覆盖第三轮中的出生范围和两项权重；只改代码，未部署、未测试）

standup2_4096_2000 到第 301 轮仍停在机身约 0.18 m（`track_height_wide` 0.55、`height_error` -2.5），
约 40% 的时间有非轮触地但不终止，回合总回报约 -2.7。据此：

- 出生摆角恢复 ±0.6 rad（不用 SCUT 的 [-90°, 135°]），`min_root_height_m` 0.25。本地 MuJoCo 网格纯运动学检查：
  全部边角组合下出生时机身最低点离地 >= 0.05 m、腿连杆 >= 0.028 m；导轮只在 USD 里，未检查。
- 课程高度门槛 0.03→0.05 m。
- 权重：`track_height_wide` 1→2，`height_error` -2→-1，`lin_vel_error` -16→-8，`undesired_contact` -2→-4；
  高度门控同时作用于速度/转速的跟踪奖励和误差惩罚（与 SCUT 一致）。
- 上一轮站起来的激励估算已有约 5/s 仍未站起，权重不一定是瓶颈；部署前建议先回放 standup2 的 checkpoint 看实际姿态。

- 终止计数改为慢慢回落：新增 `training.termination.release_s=2.0`（满计数回落到 0 的时间），对所有任务生效。

## 2026-11-12 P1 后续阶段适配（只改代码，未部署、未在 Isaac 中运行）

- 随机腿姿出生、起立窗口对所有任务的训练回合生效；高度门控对 P1 全部阶段生效（腾空时置 1）。评测仍从零位出生。
- 空中出生照 SCUT V14/env_cfg.py:1488-1521：随机 roll ±0.1 / pitch ±0.2 rad、vy ±0.5 m/s、角速度、
  腿长 0.15-0.35 m、摆角 ±45°。腾空时关闭 `pitch_penalty` 和 `height_error`（SCUT airborne reward_scales）。
  `air_rewards.wheel_center_sigma` 取 SCUT 的 0.02。
- `p1-recovery` 不再使用接管状态库（删除 `handover_states_npz`）：按 SCUT predefined_reset_ground 的参数，
  腿接近水平、机身水平地从 0.25 m 落下后起身；占比仍由 `recovery_probability` 决定。
- 地形尺寸取自 RMUC 2027 规则手册 V1.0.0：图 4-27 中央高地外侧平台高 200 mm、宽 800 mm，路面 300 mm；
  图 4-37 起伏路段凸起高 70 mm、间距 240 mm。台阶高 0.02-0.24 m（200 mm × 1.2）、踏面 0.8 m；凸起 0.01-0.07 m。
  尺寸是从图上读的，图中 350/360 mm 两个标注的含义未确认。
- 新增 `randomization.body_materials`：机身（0.01-0.1）和导轮（0.1-0.7）摩擦随机化，SCUT V14/env_cfg.py:136-159。
- SRM 配置新增的几何量留 null。P2、P3 仍没有华南虎版策略配置。

## 2026-11-12 P2 参考配置、起伏/波浪地形、落地阶段平滑惩罚（只改代码，未部署、未在 Isaac 中运行）

- 新增 `config/reference/scut_p2.yaml`，`tools.prepare_scut` 同时输出 `policy_p2.yaml` 并检查 `p2-spin` 可启动。
  取值来源和与 SRM P2 配置的差别写在该文件开头。新增奖励项 `spin_heading_error`（SCUT 的方向误差平方项）。
  P3 没有华南虎版配置。
- 台阶/起身阶段的地形增加随机起伏和波浪两种高度场地块（各 5%，参数照 SCUT terrains.py:102-115），地形列数 10→20。
  （波浪地形在下一条记录里去掉了。）
- P1 各阶段新增 `reward_overrides`：landing/stairs/recovery 按 SCUT V14/env_cfg.py:1662-1668 把
  `action_rate`、`action_smoothness_leg/wheel`、`leg_joint_vel`、`wheel_vel` 降到约 1/5；flat 为空。
- 未做：SCUT 空中出生后 3 s 的指令限幅（vx ±2.5、wz ±0.5π）。

## 2026-11-12 指南 v2.2 对应的修改（已提交，未部署、未在 Isaac 中运行）

- 恢复系数：地面取 1.0（乘法合成），轮子 0–0.2、机身 0–0.2、导轮 0–0.1 随机。范围是设计选择，待实测。
- 去掉波浪地形（SCUT 没有启用）；随机起伏地面占 10%，地形列数回到 10。
- 落地及之后阶段的平滑惩罚按本项目平地权重 ×0.2，不照抄 SCUT 的数值（两边策略频率不同）。
- 空中出生后 3 s 指令限幅：vx ±2.5 m/s、wz ±0.5π rad/s（SCUT V14/env_cfg.py:1510-1516）。
- P2 参考配置按平地经验调整奖励（高度门控、宽核高度奖励、触地 −4、转速平方惩罚 −0.1、方向误差 −0.02），理由写在
  `config/reference/scut_p2.yaml` 开头；P2 的高度门控参数在 SRM 的 P2 配置里也成为必填。
- 指南升到 v2.2，新增 `docs/LESSONS.md`。
- **启动 `p1-stairs` / `p1-recovery` 前要改两项**（`training.disturbance`）：`baseline_evaluation_passed: true`、
  `phase2_start_iteration: 0`。不改的话训练会拒绝启动并列出这两项。

## 2026-11-12 课程停在 0.85 后的调整（只改代码，未部署、未在 Isaac 中运行）

现象：`standup3` 续训到约 1900 轮已站稳（高度误差约 1.3 cm），课程从第 1411 轮起停在 0.85。推算是“直行加转向”
的外侧轮转速接近 60 rad/s 的目标上限，没有力矩留给平衡（见 docs/LESSONS.md §2.7）。

- 转向指令上限 2π→5 rad/s。
- 轮速目标上限 `wheel_speed_limit_rad_s` 60→100（SCUT 配置里的 max_wheel_vel；它的代码再乘 1.5 得 150，这里没有乘）。
- `scut_p1.yaml` 的 `save_interval` 500→200。
- 新增 `commands.combined_wz_limit_rad_s=3.0`：“直行加转向”片段的转向在课程比例超过 0.6 后等比例缩到 ±3 rad/s 以内，
  对 P1 全部阶段生效；纯转向、纯直行、冲刺不变。（先前按外侧轮 55 rad/s 裁剪的方案已去掉。）
- 新增 `training.height_wide_anneal`：`p1-flat` 的宽核高度奖励从 2 线性退到 0.5（默认第 2000 轮起、500 轮内）。
  用 `--resume` 续训时把 `start_iteration` 设成不小于续训起点的轮数。落地等后续阶段仍用 2，没有改。
- TensorBoard 新增 `Curriculum/pass_rate`、`pass_velocity`、`pass_yaw_rate`、`pass_height`、`pass_survived`。
- 需要重新运行 `tools.prepare_scut`（模板和生成内容都变了）。观测合同没变，可以从 `standup3` 的检查点 `--resume`。

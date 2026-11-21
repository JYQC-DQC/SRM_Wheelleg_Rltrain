# 策略与固件接口（冻结：obs_version 4）

训练入口、阶段交接与学习率见[训练与交接](TRAINING.md)。

P1/P2/P3 同形同义，各有独立权重。控制/物理 500 Hz，策略 100 Hz。未经负责人确认不得再增通道或复用槽位传递其他信息。

| 基础帧下标（从 0 起） | 内容及实车来源 |
|---|---|
| 0–3 | `vx_cmd, vy_cmd, wz_cmd, height_cmd`：主控最终下发指令，非实测速度或高度。当前 P1/P2/P3 所有训练均为 `vy_cmd=0`，保留给未来平移小陀螺；当前不训练平移。 |
| 4–9 | 机体角速度 xyz（rad/s）、姿态解算得到的机体系单位重力；x 前 y 左 z 上，直立重力 `[0,0,-1]`。不是归一化加速度计。 |
| 10–13 | 四腿相对默认关节角（rad）：左前、左后、右前、右后，无轮角占位。 |
| 14–19 | 六路关节端速度（rad/s），按左前、左后、左轮、右前、右后、右轮。 |
| 20–25 | 同顺序上一策略拍的六个原始动作，首次置零。不是电机目标或实际力矩。 |

- **ONNX 两个外部输入**：`obs[27] = 基础帧26 + jump_request_m`；`obs_history[130]` 只存五帧基础帧，旧→新，末帧等于 `obs[:26]`。真正复位/切策略以首帧填满；同一 P1 首触、接稳或交回驾驶不清历史。
- **Encoder** `130→128→64→3`，输出机体系估计线速度 m/s。**Actor** 顺序为 `[基础帧26, 估速3, jump_request_m]`，`30→128→64→32→6`，隐藏层 ELU。跳跃请求是 Actor 第 30 维（下标 29），不是 ONNX 的第 30 个外部读数。每套 39,721 参数，三套 FP32 权重共 476,652 B，不含激活和运行库。
- **跳跃请求**单位 m，不乘站高缩放。P1/P2 恒为 0；P3 无请求为 0，请求为正的目标跳高。主控在按键上升沿锁存高度，按策略时钟保持 `event_duration_s + landing_stable_s`（该训练阶段的配置常数）；窗口内不重触发，超时清零，长按不自动重复。清零不读取轮接触、是否接稳或跳跃得分。reset 清请求，操作手一直按住不产生新边沿。
- **训练裁判不进网络**：起跳、首触、起身、落稳、失败及课程用仿真接触/运动学判断，不读 Actor 输出作为事件标签。射线保留给地形测量和 critic，不给 Actor 台阶位，也不替主控抬高站高指令。训练指令调度仍可按已定出生/恢复流程限令、交回驾驶；实车要复现同样的指令行为，需要对应的主控调度，网络不提供“已接稳”判定。
- **动作与校准**：四腿位置残差、两轮速度目标；物理观测先限幅再缩放。`action_clip: null` 不取消执行端目标限幅。方向、零点、默认角及 IMU 安装等仍须校准。`shu_train.tools.gen_c_config --interface-only` 不能用于实车放行；实测日志需逐拍对齐两路输入与六路输出。
- **迁移边界**：v3 的 35/175 检查点、ONNX、golden 向量及固件头不兼容，不应补零硬接。按 v4 重新训练、导出；v4 内仍按既定顺序跨阶段迁移。

## 跳跃 Actor 三方核对（2026-11-19）

| 本地版本 | 可执行模型或训练配置 | 起跳意图如何到达控制器 |
|---|---|---|
| 华南虎 26 国赛车 | 7 月 29 日轻量 flat 配置为单帧 35 → 128 → 64 → 32 → 6。7 月 30 日轻量 rough_rotation_stair 的 ONNX 同形。7 月 19 日 rough_dash 发布图为单帧 35 → 256 → 128 → 64 → 6。 | 七个模式槽为 normal、stair、slope、recover、jump、height_target、state_time。轻量 flat 和该 rough_dash 的冻结配置均关闭 jump_takeoff 状态机与 permission。公开目录和作者说明把 rough_dash 归为飞坡/落地，本次未找到可单独核实的主动跳专用权重。 |
| 复旦非腿熊 Jump | 部署示例 Jump、Stable、Upstairs、Spin 的 ONNX 同形。历史 125 → 128 → 64 → 3，当前 25 加估速 3 → 128 → 64 → 32 → 6。Jump 当前帧包含角速度、重力投影、前速/转速/站高指令、四腿角、六路速度和上一动作。 | 固件在准备状态检查左侧 TOF，启用时须有效且距离小于 0.9 m，离线有旁路。触发后选 Jump 480 ms，执行期给锁存前速减 0.1 m/s、零偏航、0.10 m 站高。计时相位属于主控。 |
| 上大 P3 v4 | 外部 obs 27、history 130。历史 5×26 → 128 → 64 → 3。当前基础 26、估速 3、目标跳高 1 → 128 → 64 → 32 → 6。 | 操作手上升沿锁存正值 `jump_request_m`，无请求为零。P3 能在同一网络内等待、助跑和起跳。接触、腾空和越梁结果归环境判分。 |

复旦与上大的六路动作交错排列，四腿位置残差与两轮速度目标；华南虎所核模型按前四腿、后两轮拆分。复旦 Jump 的第三个指令是站高，固件示例中的 0.10 m 是执行期站高设定值。上大的目标跳高另占一维，保留 `vy_cmd` 使基础帧比复旦多一维。

依据：[华南虎发布说明](../../../wheeled-legged_RL/pretrained/26_infantry/readme.md)、[轻量 flat 冻结环境](../../../wheeled-legged_RL/pretrained/26_infantry/flat_and_rotation/2026-07-29_23-20-03/params/env.yaml)、[复旦 Jump 训练](../../../fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py)、[复旦部署示例图](../../../XYEGA_RM2026_WheelLeg_Infatry_RLdeploy/pseudocode/example/onnx/jump/jump_pos0.2_0.4_p6.0_d0.5_0.2.onnx)、[底盘切换与组帧](../../../XYEGA_RM2026_WheelLeg_Infatry_RLdeploy/source_code/User/Application/chassis/chassis.cpp)、[上大推理图](../../shu_train/wheelleg/actor.py)。

### 三家按 Actor 首层下标复核（2026-11-21，零基下标）

- **上大**：0/1/2/3 = vx指令/vy预留/wz指令/站高；4–6 机体角速度 xyz；7–9 机体单位重力 xyz；10–13 左前/左后/右前/右后相对默认关节角；14–19 六路关节速度，20–25 上拍六路原始动作，六路均为左前/左后/左轮/右前/右后/右轮；26–28 为历史估出的机体系 vx/vy/vz（m/s），29 是跳高请求（m），P1 恒零。当前帧通道缩放依次为指令 1、站高 5、角速 0.5、重力 1、角度 1、关节速度 0.1、上一动作 1；估速和请求不再乘站高/关节速度系数。输入不含实测站高、接触、TOF、模式或相位时间。输出中 0/1/3/4 映射四腿位置残差，2/5 映射左右轮速度目标。见[组帧](../../shu_train/wheelleg/observation.py)、[网络拼接](../../shu_train/wheelleg/actor.py)、[配置](../../shu_train/config/policies/p1/policy_meta.yaml)。
- **华南虎**（上述轻量 flat/mixed）：0–3 运动三指令+站高；4–6 角速度，7–9 投影重力；10–13 四腿相对角，14–15 屏蔽的两轮角槽（非有效轮角测量）；16–19 腿速、20–21 轮速、22–27 近一拍动作（腿四、轮二）；28–34 依次 normal/stair/slope/recover/jump/height_target/state_time。单帧 35，无历史估速。快照未开相应状态机，不能仅看最后七槽就认定模型收到台阶/跳跃阶段。四腿内部用运行时关节索引，不凭 YAML 正则倒推确切电机顺序。见[组帧](../../../wheeled-legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py#L3198)、[模式赋值](../../../wheeled-legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py#L1769)。
- **复旦非腿熊**（plane/Upstairs/Jump）：0–2 角速度，3–5 投影重力，6–8 vx指令/wz指令/目标站高，9–12 四腿相对角，13–18 六路速度，19–24 上拍动作，25–27 历史估速。六路是 lf0/lf1/左轮/rf0/rf1/右轮；复旦虚拟腿 DOF 不等于上大主动关节原始角。外部输入 25 和 125，首层输入为当前帧在前、估速在后（复旦的估速监督按其配置缩放）。Jump 的站高槽不是跳跃请求；未见相位时间进入这 28 维。见[Upstairs 组帧](../../../fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py#L338)、[Jump 拼接](../../../fudan_rl_wheel_leg/jump/wheel_legged_gym/rsl_rl/modules/actor_critic_sequence.py#L181)、[复旦部署 DOF 顺序](../../../fudan_rl_wheel_leg/mujoco/python_tools/onnx_mj_binglian.py#L30)。接口同形不证明不同日期快照是同一权重。

# 初版接口合同

## 2026-11-11 数值合同补充（obs_version 仍为 2）

Actor 仍为 35 维，顺序和缩放不变；固件必须与 Python 共用以下处理顺序：
先构造原始物理分量（关节角减默认角、轮位置置 0），按 `robot.training.observation_clip` 限幅，
再乘各分量缩放，最后将残留 NaN/Inf 置 0。正负 Inf 先由限幅变为对应边界；NaN 最后置 0。
尤其上一帧动作输入限在 [-100,100]，但策略原始输出缓存和电机目标映射仍保持独立，
这不是开启 `action_clip`。不得把未限幅的历史动作直接反馈到网络。
`gen_config.h` 导出 `WL_OBS_CLIP_<分量>_MIN/MAX`，部署侧不能手抄限幅表。
训练 critic 使用相同的先限幅再缩放流程，力矩缩放为 0.05；不改变 actor/critic 维度。

固定软件逻辑顺序：left_front, left_rear, left_wheel, right_front, right_rear, right_wheel。
这不是推断出来的 USD 顺序或 CAN ID；资产加载和驱动适配必须显式映射到该顺序。

- 500 Hz 控制/仿真，每 5 步调用 100 Hz 策略。
- obs_v2：command(3), height(1), angular_velocity(3), gravity(3), q_relative(6), qd(6), previous_action(6), mode(7)。
- 坐标：机体 x 前、y 左、z 上，角速度 rad/s，重力为单位重力向量在机体系的投影；直立为 [0,0,-1]。
- q 单位 rad、qd 单位 rad/s；轮位置观测固定为 0；腿位置减 q_default。
- 前一动作是上次策略原始输出（裁剪前），首次进入策略置 0；它不是最终电机力矩。
- P1 mode 为 [normal, stair, 0, recover, 0, 0, 0]。
- P2 无云台阶段：mode=[0,1,平移速度,sin(参考系平移方向),cos(参考系平移方向),sin(参考yaw−底盘yaw),cos(参考yaw−底盘yaw)]；command xy=0，wz 是旋转指令。参考 yaw 固定在世界系，后续实体云台需单独同步。
- P3 mode=[0,0,0,0,jump,目标跳高×5,phase]；接触事件控制实际阶段，相位仅作为观测。
- 动作：4 个真实主动关节的位置残差 + 2 个轮速度目标，按上述交错顺序；不是串联等效关节力矩。
- 动作缩放、PD、限幅、零点须与固件一致；默认关节角、方向及限位目前未知。
- v2.1：action_clip=null 表示原始输出不裁剪；q_ref 只在实测髋限位内收 0.05 rad 后裁剪，轮速按独立上限裁剪。C 头使用 WL_ACTION_CLIP_ENABLED=0，不能将 null 当作缺参或零上限。
- 训练 sensor 延迟在 2 ms 物理步采样，命令、模式和上一原始动作不随传感延迟一起倒退。
- Actor 35 维保持 obs_v2；新增 critic 信息不进入固件输入。
- 2026-11-12：P2 混合地形训练增加77点特权扫描，critic从81变158维；部署Actor合同不变。
  旧P2检查点只能提取Actor初始化，不能恢复旧critic/优化器。
- 2026-11-12：obs_version 3 为可选历史合同（默认不启用，未训练、未部署）。ONNX 输入 `obs[1,35]` 与
  `obs_history[1,frames×35]`，历史按时间从旧到新排列，每帧就是当拍的 35 维 Actor 观测；
  每次策略切换或重置后用第一帧填满整段历史。`WL_HISTORY_FRAMES` 为 0 表示 obs_version 2 单输入。
  速度/接触估计器在 ONNX 内部，固件不需要也不得提供仿真真值。

`gen_c_config.py --interface-only` 仅导出 ABI、时序及已确认的减速比，明确标记 `WL_DEPLOYMENT_CONFIG_READY=0`。
去掉该选项会在缺少参数时拒绝导出；它不生成或伪造神经网络代码。

辨识/遥测工具归队内仓库，辨识报告和拟合参数审核后导入本仓库。
仅改质量/质心可重新评测再续训；修改通道语义/缩放需更新合同和部署包版本。

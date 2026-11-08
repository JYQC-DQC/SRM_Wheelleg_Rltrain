# 初版接口合同

固定软件逻辑顺序：left_front, left_rear, left_wheel, right_front, right_rear, right_wheel。
这不是推断出来的 USD 顺序或 CAN ID；资产加载和驱动适配必须显式映射到该顺序。

- 500 Hz 控制/仿真，每 5 步调用 100 Hz 策略。
- obs_v2：command(3), height(1), angular_velocity(3), gravity(3), q_relative(6), qd(6), previous_action(6), mode(7)。
- 坐标：机体 x 前、y 左、z 上，角速度 rad/s，重力为单位重力向量在机体系的投影；直立为 [0,0,-1]。
- q 单位 rad、qd 单位 rad/s；轮位置观测固定为 0；腿位置减 q_default。
- 前一动作是上次策略原始输出（裁剪前），首次进入策略置 0；它不是最终电机力矩。
- P1 mode 为 [normal, stair, 0, recover, 0, 0, 0]。
- 动作：4 个真实主动关节的位置残差 + 2 个轮速度目标，按上述交错顺序；不是串联等效关节力矩。
- 动作缩放、PD、限幅、零点须与固件一致；默认关节角、方向及限位目前未知。

`gen_c_config.py --interface-only` 仅导出 ABI、时序及已确认的减速比，明确标记 `WL_DEPLOYMENT_CONFIG_READY=0`。
去掉该选项会在缺少参数时拒绝导出；它不生成或伪造神经网络代码。

辨识/遥测工具归队内仓库，辨识报告和拟合参数审核后导入本仓库。
仅改质量/质心可重新评测再续训；修改通道语义/缩放需更新合同和部署包版本。

# stairs revision 9：有条件恢复+x进展与stuck

本轮仅修改stairs共用代码、两份P1模板及文档。保留之前尚未提交的平地课程/free放宽改动，不修改云端训练。

## 生效条件

只对command_mode=traverse：up/down/mixed台阶及slope。flat motion和grid/rough free完全不应用世界+x约束，哪怕free此刻刚好直行也不启用。

每步同时满足以下条件才启用：

- 已过tracking_warmup_s=1s，尚未通过/到达终点，没有出界/物理终止。
- 实际追踪的非死区vx命令绝对值>stand_deadzone=0.1m/s。
- cos(yaw)×sign(vx_command)≥0.8660254，即指令运动方向距世界+x不超过30°。
- |wz_command|≤0.3rad/s。大heading纠偏暂停，不为了+x惩罚正常回正。
- 非真实飞行、非导轮支撑收腿、非落地缓冲；这些沿用现有状态，不增加新豁免计时器。

yaw约pi、vx<0的倒车实际仍沿+x，因此正常计分。站立、原地转向、自由组合、反向离开路线不产生这两项。无法以当前条件保证所有策略漏洞消除，须观察route_active_seconds与route_stuck_ratio；偏航到门控外仍由现有转速跟踪/路线完成约束负责，不能把门控外当作任务成功。

## 奖励与检测

- progress_weight=+1/米，使用机身root的世界x位移，不用可摆动的轮位置计算前进。
- 每步位移限制在±max(vx_command×cos(yaw),0)×dt，防止单靠超指令速度多刷进展；正负位移都计，原地往返不是只收正奖励。
- 位移已经含时间积分，不再乘dt。进入生效区的第一步只初始化位置，避免把reset/豁免期间位移计为进展。
- 连续有效窗口1s，机身净+x位移不足0.05m判stuck；判定后按-1/秒连续扣分。恢复净进展达到0.05m可提前清除判定，否则下一窗口重新判断。
- 退出条件时窗口时间、净位移、stuck立即清零；再次启用必须重新积满窗口。
- stuck仅检测和奖励惩罚，不新增硬终止，不更改纯出界的中性处理。
- 日志恢复Episode_Reward/progress与stuck；分地形新增route_active_seconds及route_stuck_ratio（分母为有效路段时间，不是整个回合）。

工程阈值是本项目恢复/设计值，不称SCUT原配。progress/stuck各恢复历史+1/-1量级；低速评分与奖励分别调整。

## 截图指出的评分问题

旧路线课程exp(-ev²/0.5)，0.25m/s命令完全静止评分约0.882，高于晋级门槛0.6；0.4m/s静止也约0.726。几何越过条件仍可挡住永久原地停住，但评分无法准确反映低速跟踪，且会削弱降级与速度窗口的辨别能力。

只对traverse的线速度课程改为：

    tolerance = min(sqrt(tracking_sigma), 0.15 + 0.35*abs(tracked_vx_command))
    score = exp(-(linear_error/tolerance)^2)

0.25m/s完全静止约0.330；0.4m/s完全静止约0.149；准确跟踪仍为1。保留原tracking_promote=0.6、tracking_demote=0.4和yaw评分。高速容差不超过旧sqrt(0.5)，不因此变得比旧评分更松。

这是课程统计修正，不更改track_lin_vel/lin_vel_error的奖励公式、不移除高度门控。训练运动激励由恢复的progress/stuck承担。flat的新误差判据、grid/rough已放宽的free评分保持不变。

## 合同与验证

为使critic能看到stuck相关记忆，新增窗口有效时间、净位移、stuck三个特征：course FEATURES 21→24；当前stairs critic 375→378。Actor仍35维、obs_version=2。stair_course_revision=9，旧checkpoint只能initialize-from继承Actor，不能resume恢复旧critic。

参数集中在stages.stairs.course，必填校验；通用与SCUT参考模板一致。没有新Isaac API调用。

只做静态/配置和数值算式检查，沿用用户不做测试的约定，未运行pytest、Isaac/GPU或MuJoCo。不能声称恢复后通过率已改善。未提交、推送、上传或重启训练。

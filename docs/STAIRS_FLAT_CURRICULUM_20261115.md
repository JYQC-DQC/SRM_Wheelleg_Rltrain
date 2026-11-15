# stairs 平地课程与 SCUT 粗糙地形判据核对

2026-11-15追加：已按用户要求放宽grid/rough专用跟踪门槛；最新数值和左右转高度差审查见 [STAIRS_FREE_THRESHOLDS_20261115.md](STAIRS_FREE_THRESHOLDS_20261115.md)。优先于下文旧门槛及“未修改门槛”的历史说明；尚未更新云端。

2026-11-15，revision 8。仅修改 stairs 的平地混训课程；井字/粗糙地形评分与奖励本次不改。

## 平地独立课程

仍使用同一 Actor、30% 平地比例及原站立/直行/自转/组合概率。课程由平地有效完成回合独立驱动，
不再把平地地形行号当作能力等级；台阶和其他地形课程不受影响。

| 级别（日志从0开始） | vx上限 m/s | wz上限 rad/s | 参考高度范围 m |
|---|---:|---:|---|
| 0 | ±0.54 | ±1.00 | 0.20–0.3075 |
| 1 | ±0.54 | ±1.00 | 0.20–0.3672 |
| 2 | ±0.945 | ±1.75 | 0.20–0.3672 |
| 3 | ±0.945 | ±1.75 | 0.20–0.4389 |
| 4 | ±1.35 | ±2.50 | 0.20–0.4389 |
| 5 | ±1.89 | ±3.50 | 0.20–0.4389 |
| 6 | ±2.295 | ±4.25 | 0.20–0.4389 |
| 7 | ±2.70 | ±5.00 | 0.20–0.4389 |

表中是 SCUT 参考包络；组合运动仍受原 combined_wz_limit_rad_s 限制，小转向分支也随级别缩放。
高度上限按机器人实际 spring_extension_height_m 减 step_height_margin_m 动态计算，SRM 缺参不代填。
三级先覆盖最高高度，再继续扩大运动范围；这些是本项目设计值，不是抄自 SCUT 的课程。

- 每窗口至少4096个同级有效平地完成回合，配置校验不得小于 training.num_envs。
- 成功率≥60%升一级、<20%降一级，其余保持；每个关闭窗口最多变一级，不重用多余回合。
- 纯出界不入分母；提前物理失败入失败分母。回合开始时锁定级别，旧级别回合不参与新级别窗口。
- 成功仍要求达到最短回合时间、结束时恢复支撑/姿态且无终止。
- 有效采样段平均绝对误差：vx≤0.15+0.25×平均|vx指令| m/s；
  wz≤0.25+0.25×平均|wz指令| rad/s；高度≤0.06m。不用宽核评分把完全不动当作掌握平地。
- 保存并恢复级别、窗口完成数/成功数、上窗口成功率；日志新增 command_level、window_pass_rate、
  window_completed、vx_fraction、wz_fraction、height_fraction、height_max_m。
- 随机评测使用最高课程包络；手动 sim2sim 仍使用检查点自己的配置及操作者指令。

Actor35、critic375维不变，obs_version仍为2；course合同升为8。旧revision7只能用
--initialize-from继承Actor，不可--resume；新合同检查点可以恢复上述课程状态。
本地修改不会影响正在运行的云端 revision7，也不会改变已下载的第600轮模型。

## 井字/粗糙：我们是否更严格

核对本机 wheeled-legged_RL 仓库的 V14→V13→25_v3 继承链，以及以下发布快照：

- rough_rotation_stair/2026-07-30_09-16-27/params/env.yaml:2202，curriculum:null；
  :3050–3058，rough_height_offset_curriculum_cfg.enabled:false；:1470，max_init_terrain_level:null。
- rough_dash/2026-07-19_19-15-07/params/env.yaml:2422，curriculum:null；
  :2884起，rough_height_offset_curriculum_cfg.enabled:false。
- V14/env.py:259–272：可选高度课程按训练轮数/interval计算级别，并不是通过率课程；
  :274起先检查enabled。25_v3/env.py的curriculum_manager仅在配置非空时创建，
  :5133–5135仅在manager存在时reset。
- V14/env.py:541–572：区域出界加入timeout；rotation快照:2759–2762启用边界且use_inner_terrain_area:false。

因此，generator.curriculum:true表示按难度行生成地形，不能解释为启用了我们的成功率升级规则。
上述发布路径没有与我们相同的“井字/粗糙通过验收→升级”门槛；不能把它们描述为更低的某个成功率阈值。

我们额外要求：实际地形内累计有效时间≥3s，结束时两轮仍在surface区域、恢复双轮支撑、非期望
接触不超限、姿态/角速度/高度满足恢复条件，且vx和wz各自整段平均评分都≥0.6。
评分为exp(-(error/(0.1+0.25*abs(command)))²；奖励仍用原宽核。
例如vx=0.25m/s时，瞬时评分0.6对应误差约0.116m/s；wz=0时对应约0.0715rad/s。
这是瞬时等值，不是回合平均绝对误差的硬门槛。单位分别是m/s和rad/s，不能混作同一种容差。

结论：我们的自由地形晋级限制确实更严格，而且评分和优化奖励不一致。
当前运行0–746轮井字0/2984、粗糙0/899有效回合成功，说明门槛需要诊断；但不能仅据0成功断定
哪一条件存在代码bug。建议后续拆出线速度、转速、地形内时间和结束恢复条件的通过比例，再调整评分。
不能直接照搬“无课程”，也不建议仅把总成功率门槛下调来掩盖跟踪不足。

## 验证边界

本次只做语法、配置加载和静态检查，不运行pytest或Isaac/GPU训练。
最新已保存revision7 model_600及原始params已下载并启动MuJoCo地形操作窗口；
MODEL_READY: tiles=88, obs=(35,), delays=5/4。这不验证新课程。
现有MuJoCo资产缺少16个独立导轮刚体，不能据此验收导轮支撑行为。

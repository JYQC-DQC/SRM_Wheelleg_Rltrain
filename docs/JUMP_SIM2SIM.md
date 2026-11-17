# P3 手动跳跃 sim2sim

按 `codex/scut-latest-adaptation` 的 `aaa5e20` 接入 P3；复用训练的 `JumpEvent` 和唯一的
35 维观测布局。物理/PD/气弹簧为 500 Hz，Actor 为 100 Hz，传感器及动作延迟来自下载快照。

## 启动

Windows 双击 `sim2sim/play_jump_latest.cmd`，或在仓库根目录执行：

```powershell
D:/Anaconda/envs/Mujoco/python.exe -m tools.play_jump
```

默认加载 `sim2sim/checkpoints/jump_latest/` 中编号最大的 `model_*.pt` 及该目录下的
`params/robot.yaml`、`params/policy_meta.yaml`、`params/run.json`。不要混用其他训练的配置。
`--run` 可指定另一个已下载的 P3 平地跳跃训练目录，`--checkpoint` 可固定某个文件。
模型/检查点是本机资源，不进 Git；源模型默认 `runs/scut_experience/scene.xml`，可用 `--source` 指定。

```powershell
# 出生到20cm隧道，目标跳高25cm、前进1m/s、自身偏航角速度0rad/s
D:/Anaconda/envs/Mujoco/python.exe -m tools.play_jump --site 4 --height 0.25 --vx 1.0 --wz 0
# 无窗口CPU运行；启动时模拟一次空格按键
D:/Anaconda/envs/Mujoco/python.exe -m tools.play_jump --headless 3
```

默认同时打开模型窗口和中文控制面板。面板可输入精确数值并点“应用设定”；跳跃高度输入单位为 cm，
命令行高度单位为 m。`--no-panel` 只打开模型窗口。生成的场地、出生点与启动来源记录在
`runs/jump_viewer/arena.xml` 和 `last_launch.json`。

## 指令

| 按键 | 功能 |
|---|---|
| Space 空格 | 请求一次跳跃；事件进行中再次按下不会重启计时 |
| W / S | 前后速度累加 / 递减，每次 0.25 m/s，允许范围 −2.5 至 +2.5 m/s |
| A / D | 自身偏航角速度累加 / 递减，每次 0.5 rad/s，范围 −3 至 +3 rad/s |
| Q / E | 下一次跳跃目标高度减 / 增 1 cm，范围 4–40 cm |
| C | 速度及偏航指令归零，继续执行策略稳定控制 |
| X 或 Esc | 锁存紧急停机：六路主动电机输出立即归零，继续模拟重力、接触和被动气弹簧 |
| R | 回到当前场地出生点，并清空速度、延迟、上一动作、跳跃状态及急停锁存 |
| P | 暂停 / 继续 |
| Z | 1× / 0.5× / 0.25× 慢放 |
| F1–F12 | 快速出生到对应场地，同时完整复位 |

模型窗口直接处理 GLFW 按键，空格不会触发 MuJoCo 默认的暂停操作。
面板空格也只触发跳跃，不会顺带点击焦点按钮。输入框内可编辑数字，X/Esc 始终可急停。
速度为累加指令，松键不会自动停车；C 是受控停车，X/Esc 是切断主动输出，R 重新出生。
鼠标左键拖动旋转，右键拖动平移，滚轮缩放。

跳跃高度是**相对按键触发时机身根节点的目标高度增量**，不是机身离地高度，也不是轮底越障净空。
一旦触发，本次事件锁存目标；面板及 Q/E 修改的是下一次目标。相位及起跳/触地/落稳计时复用快照的
`stages.jump`，不施加额外弹射力，也不按设定高度移动机器人。

## 场地

| 快捷键 | 场地 |
|---|---|
| F1 | 平地 |
| F2 / F3 / F4 / F5 / F6 | 10 / 15 / 20 / 25 / 30 cm 隧道 |
| F7 / F8 / F9 / F10 / F11 | 10 / 15 / 20 / 25 / 30 cm 单级台阶 |
| F12 | 每级 20 cm 的二级台阶，总高 40 cm，第一级有效台面长 80 cm |

隧道沿前进方向长 **35 cm**，顶板和两侧壁厚均为 **2 cm**，前后开口、板下中空；高度以外顶面计。
例如 20 cm 档净空高 18 cm。下方保留场地地面，没有实心填充。

未指定的尺寸采用可修改的仿真场地设置：隧道外宽 80 cm（内部净宽 76 cm），单级台面长 120 cm、宽
160 cm，二级台阶宽 160 cm、第二级台面长 80 cm。二级台面边缘依次为 x=0、0.8、1.6 m，表面高度
依次为 0.2、0.4 m。出生点在入口前 2.5 m，朝向 +X；所有场地同时存在，可以手动驾驶过去。

这些场地尺寸与操作范围在 `config/policies/p3/policy_meta.yaml` 的 `sim2sim` 节配置；
机器人质量、闭链、关节、PD、缩放、限幅仍严格读取训练快照。

## 验证边界

交付时下载的来源为云端 `p3_flat_aaa5e20_from_model_800_inheritstd_4096_5200_save200/model_600.pt`。
这是新训练的第600轮检查点；本轮初始 Actor 继承上一训练第800轮，不是已完成5200轮。
`download.json` 记录远端目录和 SHA-256；后续下载更高编号文件后启动器会自动选用。

当前训练只包含原地与正向跳跃，倒车和非零偏航是操作员测试指令，不代表训练已经覆盖这些能力。
平地和台阶的 HUD jump 成功表示跳跃事件的高度/起跳速度/落稳判定，不代表台阶路线已完成。
隧道场地另外复用 `TunnelTraversal` 和 `tunnel_landing`：从入口前方腾空完整越过横梁、
保持在通道内，并在后方地面稳定落地才显示 cleared；顶面落地、穿过孔洞和绕行均不计成功。
这些是仿真诊断，不能代替实车验收。

沿用既有 SCUT 参考 MJCF，缺少16个独立导轮刚体，缺项在启动记录中明确列出。
场地碰撞、闭链和气弹簧可运行，不表示已消除 PhysX 与 MuJoCo 的接触差异；参考模型结果不等同于
真实无云台 SRM 底盘结果。没有进行实机验证。

## 本次检查结果（2026-11-17）

新增回放专项测试及既有隧道判定测试：`9 passed in 4.07s`。涵盖训练观测/Actor 数值对齐、
隧道中空与场地尺寸、空格目标锁存、急停持续零输出、所有出生点复位、数值冒烟及顶面落地拒绝。
新增脚本与测试的 Ruff 检查、格式检查通过。

全仓 `pytest`：`2 failed, 54 passed in 7.21s`。两项失败位于
`test_jump_safety.py::test_success_air_bonus_is_bounded_one_shot_and_has_no_landing_dwell` 和
`test_scut_latest.py::test_reference_only_exempts_unused_dc_fields`；本次未修改其被测训练代码。
全仓 Ruff 报10个已有超长行（旧 `sim2sim/play.py` 与 `sim2sim/sim2sim.py`），
格式检查提示旧 `build_model.py`、`play.py`、`sim2sim.py` 三文件需要格式化；未整体重排旧文件。

已离屏渲染并检查场地。桌面已检测到 MuJoCo 和控制面板窗口，但桌面控制授权超时，
实际窗口按键交互未完成验证；按键分派与空格触发已通过程序测试。

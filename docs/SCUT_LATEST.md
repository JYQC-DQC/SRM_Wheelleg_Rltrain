# 最新框架运行 SCUT 华南虎参考模型

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


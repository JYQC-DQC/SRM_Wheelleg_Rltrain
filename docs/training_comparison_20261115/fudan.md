# 附录C：复旦50组当前及历史配置

[返回总览](README.md)

两组当前入口+48组历史快照。AST静态求值常量、算术及类继承；未执行第三方模块。未解析表达式数为0。名称不代表质量排名。

| ID | 配置 | mesh | vx初值 | wz初值 | h初值 | 历史帧/latent |
|---|---|---|---|---|---|---|
| F01 | plane/current | plane | [-2.0, 2.0] | [-2, 2] | [0.1, 0.2] | [5, 3] |
| F02 | plane/wheel_legged\25_20_1.0_0.2_angz+ | plane | [-2.0, 2.0] | [-7, 7] | [0.1, 0.3] | [5, 3] |
| F03 | plane/wheel_legged\25_20_1.0_0.2_angz++ | plane | [-2.0, 2.0] | [-10, 10] | [0.1, 0.3] | [5, 3] |
| F04 | plane/wheel_legged\25_20_1.0_0.2_angz+++ | plane | [-2.0, 2.0] | [-13, 13] | [0.1, 0.3] | [5, 3] |
| F05 | plane/wheel_legged\25_20_1.0_0.2_angz+++_zengjiajiangli | plane | [0, 0] | [-13, 13] | [0.1, 0.3] | [5, 3] |
| F06 | plane/wheel_legged\25_20_1.0_0.2_angz+++继续训练但是调小范围了 | plane | [-2.0, 2.0] | [-2, 2] | [0.1, 0.2] | [5, 3] |
| F07 | plane/wheel_legged\25_20_1.0_0.2_orientation+ | plane | [-2, 2] | [-2, 2] | [0.1, 0.3] | [5, 3] |
| F08 | plane/wheel_legged\25_20_1.0_0.2_orientation+_suiji | trimesh | [-2.0, 2.0] | [-4.0, 4.0] | [0.09, 0.33] | [5, 3] |
| F09 | plane/wheel_legged\25_20_1.0_0.2_orientation+_suiji继续训练了很久 | trimesh | [-2.1, 2.1] | [-5.0, 5.0] | [0.09, 0.33] | [5, 3] |
| F10 | plane/wheel_legged\25_40_5.0_0.2 | plane | [-2, 2] | [-4, 4] | [0.1, 0.3] | [5, 3] |
| F11 | plane/wheel_legged\25_40_5.0_0.2_recover | plane | [-2, 2] | [-4, 4] | [0.1, 0.3] | [5, 3] |
| F12 | plane/wheel_legged\6010.2 | plane | [-2.0, 2.0] | [-2.0, 2.0] | [0.14, 0.3] | [5, 3] |
| F13 | plane/wheel_legged\6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0 | trimesh | [-2.0, 2.0] | [-2.0, 2.0] | [0.14, 0.3] | [5, 3] |
| F14 | plane/wheel_legged\6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚 | trimesh | [-2.0, 2.0] | [-2.0, 2.0] | [0.14, 0.3] | [5, 3] |
| F15 | plane/wheel_legged\6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0 | trimesh | [-2.0, 2.0] | [-2.0, 2.0] | [0.14, 0.3] | [5, 3] |
| F16 | plane/wheel_legged\6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚 | trimesh | [-2.0, 2.0] | [-2.0, 2.0] | [0.14, 0.3] | [5, 3] |
| F17 | plane/wheel_legged\history10latent16_pd201.00.2terrian | trimesh | [-2.1, 2.1] | [-5.0, 5.0] | [0.09, 0.33] | [10, 16] |
| F18 | plane/wheel_legged\history10latent16_pd602.00.2terrian | trimesh | [-2.0, 2.0] | [-4.0, 4.0] | [0.09, 0.33] | [10, 16] |
| F19 | plane/wheel_legged\linx_scales=3.0pd=101.00.2_randization=normal | plane | [-2.0, 2.0] | [-2, 2] | [0.09, 0.35] | [5, 3] |
| F20 | plane/wheel_legged\linx_scales=3.0pd=201.00.2_randization=normal | plane | [-2.0, 2.0] | [-2, 2] | [0.09, 0.35] | [5, 3] |
| F21 | plane/wheel_legged\linx_scales=3.0pd=51.50.25_randization=normal_new | plane | [-2.0, 2.0] | [-2, 2] | [0.09, 0.35] | [5, 3] |
| F22 | plane/wheel_legged\linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing | trimesh | [-2.0, 2.0] | [-2.0, 2.0] | [0.09, 0.35] | [5, 3] |
| F23 | plane/wheel_legged\linx_scales=3.0pd=61.00.2_randization=normal | plane | [-2.0, 2.0] | [-2, 2] | [0.09, 0.35] | [5, 3] |
| F24 | plane/wheel_legged\linx_scales=4.0pd=101.00.2_randization=normal | plane | [-2.0, 2.0] | [-2, 2] | [0.09, 0.2] | [5, 3] |
| F25 | plane/wheel_legged\linx_scales=5.0pd=151.00.2_randization=hard | plane | [-2.0, 2.0] | [-2, 2] | [0.09, 0.35] | [5, 3] |
| F26 | plane/wheel_legged\linx_scales=5.0pd=151.00.2_randization=mid | plane | [-2.0, 2.0] | [-2, 2] | [0.09, 0.35] | [5, 3] |
| F27 | plane/wheel_legged\linx_scales=5.0pd=151.00.2_randization=normal | plane | [-2.0, 2.0] | [-2, 2] | [0.09, 0.35] | [5, 3] |
| F28 | plane/wheel_legged\recover_from_lied_on_ground | plane | [-2.0, 2.0] | [-2, 2] | [0.1, 0.2] | [5, 3] |
| F29 | plane/wheel_legged\recover_from_lied_on_ground_yuntai | plane | [-2.0, 2.0] | [-2, 2] | [0.07, 0.12] | [5, 3] |
| F30 | plane/wheel_legged\recover_from_lied_on_ground_yuntai_height_jiajiajia | plane | [-2.0, 2.0] | [-2, 2] | [0.1, 0.2] | [5, 3] |
| F31 | plane/wheel_legged\recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia | plane | [-2.0, 2.0] | [-2, 2] | [0.1, 0.3] | [5, 3] |
| F32 | plane/wheel_legged\recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia | plane | [-2.0, 2.0] | [-6, 6] | [0.1, 0.2] | [5, 3] |
| F33 | plane/wheel_legged\recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia | plane | [-2.0, 2.0] | [-11, 11] | [0.1, 0.2] | [5, 3] |
| F34 | plane/wheel_legged\recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia | plane | [-2.0, 2.0] | [-15, 15] | [0.1, 0.2] | [5, 3] |
| F35 | plane/wheel_legged\recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia | plane | [-2.0, 2.0] | [-18, 18] | [0.1, 0.2] | [5, 3] |
| F36 | plane/wheel_legged\上台阶1 | plane | [-2.0, 2.0] | [-2.0, 2.0] | [0.1, 0.33] | [5, 3] |
| F37 | plane/wheel_legged\上台阶2 | trimesh | [-2.0, 2.0] | [-2.0, 2.0] | [0.23, 0.33] | [5, 3] |
| F38 | plane/wheel_legged\上台阶3 | trimesh | [-2.3, 2.3] | [-2.0, 2.0] | [0.23, 0.33] | [5, 3] |
| F39 | plane/wheel_legged\上台阶3_angz+ | trimesh | [-2.3, 2.3] | [-5.0, 5.0] | [0.17, 0.33] | [5, 3] |
| F40 | plane/wheel_legged\上台阶3_angz+添加随机地形，进一步训练v1 | trimesh | [-2.0, 2.0] | [-4.0, 4.0] | [0.09, 0.33] | [5, 3] |
| F41 | plane/wheel_legged\上台阶3_angz+添加随机地形，进一步训练v2 | trimesh | [-2.0, 2.0] | [-4.0, 4.0] | [0.09, 0.33] | [5, 3] |
| F42 | plane/wheel_legged\上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够 | trimesh | [-2.0, 2.0] | [-4.0, 4.0] | [0.09, 0.33] | [5, 3] |
| F43 | plane/wheel_legged\腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover | trimesh | [-2.0, 2.0] | [-2.0, 2.0] | [0.13, 0.35] | [5, 3] |
| F44 | plane/wheel_legged\腿熊第一版本recover | plane | [-2.0, 2.0] | [-2.0, 2.0] | [0.11, 0.31] | [5, 3] |
| F45 | plane/wheel_legged\腿熊第三版本加入随机地形继续训练很久recover | trimesh | [-2.0, 2.0] | [-2.0, 2.0] | [0.11, 0.31] | [5, 3] |
| F46 | plane/wheel_legged\腿熊第二版本加入随机地形recover | trimesh | [-2.0, 2.0] | [-2.0, 2.0] | [0.11, 0.31] | [5, 3] |
| F47 | plane/wheel_legged\腿熊第五版本 | trimesh | [-2.0, 2.0] | [-2.0, 2.0] | [0.13, 0.35] | [5, 3] |
| F48 | plane/wheel_legged\腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover | trimesh | [-2.0, 2.0] | [-2.0, 2.0] | [0.13, 0.35] | [5, 3] |
| F49 | jump/current | plane | [-2.1, 2.1] | [-2, 2] | [0.12, 0.15] | [5, 3] |
| F50 | jump/wheel_legged\p60.50.2目前测试下来最好的 | plane | [-2.1, 2.1] | [-2, 2] | [0.12, 0.15] | [5, 3] |



## F01 plane/current

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/wheel_legged/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1843>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1848>) |
| tracking_ang_vel_enhance | 1.0 | [_reward_tracking_ang_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1853>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1731>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1892>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1719>) |
| ang_vel_xy | -0.2 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1723>) |
| orientation | -100.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1744>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1762>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.1, 0.2] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 20.0 |
| control.stiffness.f1 | 20.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.tracking_ang_vel_enhance | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.2 |
| rewards.scales.orientation | -100.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 8192 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | {WHEEL_LEGGED_GYM_ROOT_DIR}/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.6, 1.4] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.6, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-1.0, 2.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.9, 1.1] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.02, 0.02, 0.02] |
| domain_rand.push_robots | false |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.95, 1.05] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.95, 1.05] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.95, 1.05] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.03, 0.03] |
| domain_rand.randomize_action_delay | false |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F02 plane/wheel_legged\25_20_1.0_0.2_angz+

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1843>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1848>) |
| tracking_ang_vel_enhance | 1.0 | [_reward_tracking_ang_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1853>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1731>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1892>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1719>) |
| ang_vel_xy | -0.07 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1723>) |
| orientation | -18.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1744>) |
| action_rate | -0.1 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1762>) |
| action_smooth | -0.1 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-7, 7] |
| commands.ranges.height | [0.1, 0.3] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 20.0 |
| control.stiffness.f1 | 20.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.tracking_ang_vel_enhance | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.07 |
| rewards.scales.orientation | -18.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.1 |
| rewards.scales.action_smooth | -0.1 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["rf", "lf", "base"] |
| asset.terminate_after_contacts_on | ["rf", "lf", "base"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F03 plane/wheel_legged\25_20_1.0_0.2_angz++

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1843>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1848>) |
| tracking_ang_vel_enhance | 1.0 | [_reward_tracking_ang_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1853>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1731>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1892>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1719>) |
| ang_vel_xy | -0.07 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1723>) |
| orientation | -18.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1744>) |
| action_rate | -0.1 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1762>) |
| action_smooth | -0.1 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-10, 10] |
| commands.ranges.height | [0.1, 0.3] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 20.0 |
| control.stiffness.f1 | 20.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.tracking_ang_vel_enhance | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.07 |
| rewards.scales.orientation | -18.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.1 |
| rewards.scales.action_smooth | -0.1 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["rf", "lf", "base"] |
| asset.terminate_after_contacts_on | ["rf", "lf", "base"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F04 plane/wheel_legged\25_20_1.0_0.2_angz+++

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1843>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1848>) |
| tracking_ang_vel_enhance | 1.0 | [_reward_tracking_ang_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1853>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1731>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1892>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1719>) |
| ang_vel_xy | -0.07 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1723>) |
| orientation | -18.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1744>) |
| action_rate | -0.1 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1762>) |
| action_smooth | -0.1 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-13, 13] |
| commands.ranges.height | [0.1, 0.3] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 20.0 |
| control.stiffness.f1 | 20.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.tracking_ang_vel_enhance | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.07 |
| rewards.scales.orientation | -18.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.1 |
| rewards.scales.action_smooth | -0.1 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["rf", "lf", "base"] |
| asset.terminate_after_contacts_on | ["rf", "lf", "base"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F05 plane/wheel_legged\25_20_1.0_0.2_angz+++_zengjiajiangli

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1878>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1883>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1888>) |
| tracking_ang_vel_enhance | 1.0 | [_reward_tracking_ang_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1893>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1771>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1932>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1759>) |
| ang_vel_xy | -0.07 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1763>) |
| orientation | -18.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1767>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1792>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1798>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1784>) |
| action_rate | -0.1 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1802>) |
| action_smooth | -0.1 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1806>) |
| wheel_vel_abs_match | 0.5 | [_reward_wheel_vel_abs_match](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1951>) |
| wheel_torque_abs_match | 0.5 | [_reward_wheel_torque_abs_match](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1959>) |
| wheel_torque_smooth | 0.5 | [_reward_wheel_torque_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1969>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1824>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1841>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | false |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [0, 0] |
| commands.ranges.ang_vel_yaw | [-13, 13] |
| commands.ranges.height | [0.1, 0.3] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 20.0 |
| control.stiffness.f1 | 20.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.tracking_ang_vel_enhance | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.07 |
| rewards.scales.orientation | -18.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.1 |
| rewards.scales.action_smooth | -0.1 |
| rewards.scales.wheel_vel_abs_match | 0.5 |
| rewards.scales.wheel_torque_abs_match | 0.5 |
| rewards.scales.wheel_torque_smooth | 0.5 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |
| rewards.wheel_vel_abs_match_sigma | 0.05 |
| rewards.wheel_torque_abs_match_sigma | 0.05 |
| rewards.wheel_torque_smooth_sigma | 0.1 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["rf", "lf", "base"] |
| asset.terminate_after_contacts_on | ["rf", "lf", "base"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F06 plane/wheel_legged\25_20_1.0_0.2_angz+++继续训练但是调小范围了

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1843>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1848>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1731>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1892>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1719>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1723>) |
| orientation | -15.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1752>) |
| dof_acc | -3e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1758>) |
| torques | -0.001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1744>) |
| action_rate | -0.3 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1762>) |
| action_smooth | -0.3 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.1, 0.2] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 20.0 |
| control.stiffness.f1 | 20.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -15.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -3e-07 |
| rewards.scales.torques | -0.001 |
| rewards.scales.action_rate | -0.3 |
| rewards.scales.action_smooth | -0.3 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["rf", "lf", "base"] |
| asset.terminate_after_contacts_on | ["rf", "lf", "base"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F07 plane/wheel_legged\25_20_1.0_0.2_orientation+

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1878>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1883>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1888>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1771>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1932>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1759>) |
| ang_vel_xy | -0.07 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1763>) |
| orientation | -18.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1767>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1792>) |
| dof_acc | -2.7e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1798>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1784>) |
| action_rate | -0.16 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1802>) |
| action_smooth | -0.15 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1806>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1824>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1841>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2, 2] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.1, 0.3] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 20.0 |
| control.stiffness.f1 | 20.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.07 |
| rewards.scales.orientation | -18.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.7e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.16 |
| rewards.scales.action_smooth | -0.15 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["rf", "lf", "base"] |
| asset.terminate_after_contacts_on | ["rf", "lf", "base"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F08 plane/wheel_legged\25_20_1.0_0.2_orientation+_suiji

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1925>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1930>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1935>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1818>) |
| base_height_enhance | 1.0 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1827>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1979>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1806>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1810>) |
| orientation | -20.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1814>) |
| dof_vel | -2e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1839>) |
| dof_acc | -1e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1845>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1831>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1849>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1853>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1871>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1888>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 6.0 |
| commands.advanced_max_ang_vel_curriculum | 6.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-4.0, 4.0] |
| commands.ranges.height | [0.09, 0.33] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.3, 0.2, 0.0, 0.3, 0.2, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 20.0 |
| control.stiffness.f1 | 20.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.base_height_enhance | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -20.0 |
| rewards.scales.dof_vel | -2e-05 |
| rewards.scales.dof_acc | -1e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F09 plane/wheel_legged\25_20_1.0_0.2_orientation+_suiji继续训练了很久

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1925>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1930>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1935>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1818>) |
| base_height_enhance | 1.0 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1827>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1979>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1806>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1810>) |
| orientation | -20.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1814>) |
| dof_vel | -2e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1839>) |
| dof_acc | -1e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1845>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1831>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1849>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1853>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1871>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1888>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 6.0 |
| commands.advanced_max_ang_vel_curriculum | 6.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.1, 2.1] |
| commands.ranges.ang_vel_yaw | [-5.0, 5.0] |
| commands.ranges.height | [0.09, 0.33] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.3, 0.2, 0.0, 0.3, 0.2, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 20.0 |
| control.stiffness.f1 | 20.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.base_height_enhance | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -20.0 |
| rewards.scales.dof_vel | -2e-05 |
| rewards.scales.dof_acc | -1e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F10 plane/wheel_legged\25_40_5.0_0.2

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1878>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1883>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1888>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1771>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1932>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1759>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1763>) |
| orientation | -15.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1767>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1792>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1798>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1784>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1802>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1806>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1824>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1841>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2, 2] |
| commands.ranges.ang_vel_yaw | [-4, 4] |
| commands.ranges.height | [0.1, 0.3] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 40.0 |
| control.stiffness.f1 | 40.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 5.0 |
| control.damping.f1 | 5.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -15.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["rf", "lf", "base"] |
| asset.terminate_after_contacts_on | ["rf", "lf", "base"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F11 plane/wheel_legged\25_40_5.0_0.2_recover

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1878>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1883>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1888>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1771>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1932>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1759>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1763>) |
| orientation | -15.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1767>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1792>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1798>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1784>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1802>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1806>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1824>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1841>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2, 2] |
| commands.ranges.ang_vel_yaw | [-4, 4] |
| commands.ranges.height | [0.1, 0.3] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 40.0 |
| control.stiffness.f1 | 40.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 5.0 |
| control.damping.f1 | 5.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -15.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.23 |
| init_state.default_joint_angles.lf1_Joint | -0.65 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.23 |
| init_state.default_joint_angles.rf1_Joint | 0.65 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F12 plane/wheel_legged\6010.2

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2016>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2021>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2026>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1909>) |
| nominal_state | -0.1 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2081>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1897>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1901>) |
| orientation | -10.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1905>) |
| dof_vel | -1e-06 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1930>) |
| dof_acc | -1e-08 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1936>) |
| torques | -1e-05 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1922>) |
| action_rate | -0.003 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1940>) |
| action_smooth | -0.003 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1944>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1962>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1979>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 4.0 |
| commands.advanced_max_ang_vel_curriculum | 4.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 10.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2.0, 2.0] |
| commands.ranges.height | [0.14, 0.3] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.5, 0.2, 0.1, 0.1, 0.1, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 60.0 |
| control.stiffness.f1 | 60.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -0.1 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -10.0 |
| rewards.scales.dof_vel | -1e-06 |
| rewards.scales.dof_acc | -1e-08 |
| rewards.scales.torques | -1e-05 |
| rewards.scales.action_rate | -0.003 |
| rewards.scales.action_smooth | -0.003 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.wheel_contact_force_threshold | 1.0 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.13] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.35 |
| init_state.default_joint_angles.lf1_Joint | -0.55 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.35 |
| init_state.default_joint_angles.rf1_Joint | 0.55 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | wheel |
| asset.wheel_names | ["l_wheel", "r_wheel"] |
| asset.offset | 0.0 |
| asset.l1 | 0.21 |
| asset.l2 | 0.25 |
| asset.penalize_contacts_on | ["base", "lf", "rf"] |
| asset.terminate_after_contacts_on | ["base", "lf", "rf"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.lift_robots | false |
| domain_rand.lift_interval_s | 7 |
| domain_rand.lift_height | 0.7 |
| domain_rand.downward_impulse_robots | true |
| domain_rand.downward_impulse_interval_s | 7 |
| domain_rand.downward_impulse_vel_range | [2.4, 2.8] |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F13 plane/wheel_legged\6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2016>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2021>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2026>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1909>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2081>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1897>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1901>) |
| orientation | -10.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1905>) |
| dof_vel | -1e-06 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1930>) |
| dof_acc | -1e-08 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1936>) |
| torques | -1e-05 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1922>) |
| action_rate | -0.003 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1940>) |
| action_smooth | -0.003 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1944>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1962>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1979>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 4.0 |
| commands.advanced_max_ang_vel_curriculum | 4.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 10.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2.0, 2.0] |
| commands.ranges.height | [0.14, 0.3] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.0, 0.3, 0.3, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 60.0 |
| control.stiffness.f1 | 60.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -10.0 |
| rewards.scales.dof_vel | -1e-06 |
| rewards.scales.dof_acc | -1e-08 |
| rewards.scales.torques | -1e-05 |
| rewards.scales.action_rate | -0.003 |
| rewards.scales.action_smooth | -0.003 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.wheel_contact_force_threshold | 1.0 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.13] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.35 |
| init_state.default_joint_angles.lf1_Joint | -0.55 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.35 |
| init_state.default_joint_angles.rf1_Joint | 0.55 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | wheel |
| asset.wheel_names | ["l_wheel", "r_wheel"] |
| asset.offset | 0.0 |
| asset.l1 | 0.21 |
| asset.l2 | 0.25 |
| asset.penalize_contacts_on | ["base", "lf", "rf"] |
| asset.terminate_after_contacts_on | ["base", "lf", "rf"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.lift_robots | false |
| domain_rand.lift_interval_s | 7 |
| domain_rand.lift_height | 0.7 |
| domain_rand.downward_impulse_robots | true |
| domain_rand.downward_impulse_interval_s | 7 |
| domain_rand.downward_impulse_vel_range | [2.4, 2.8] |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F14 plane/wheel_legged\6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2030>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2035>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2040>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1912>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2095>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1900>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1904>) |
| orientation | -10.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1908>) |
| dof_vel | -3e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1933>) |
| dof_acc | -5e-08 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1939>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1925>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1943>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1947>) |
| power | -0.0001 | [_reward_power](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1929>) |
| leg_action_l2 | -0.01 | [_reward_leg_action_l2](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1965>) |
| torque_rate | -0.001 | [_reward_torque_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1971>) |
| dof_vel_limits | -0.05 | [_reward_dof_vel_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2008>) |
| torque_limits | -0.1 | [_reward_torque_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2019>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1975>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1992>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 4.0 |
| commands.advanced_max_ang_vel_curriculum | 4.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 10.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2.0, 2.0] |
| commands.ranges.height | [0.14, 0.3] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.0, 0.3, 0.3, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 60.0 |
| control.stiffness.f1 | 60.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -10.0 |
| rewards.scales.dof_vel | -3e-05 |
| rewards.scales.dof_acc | -5e-08 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.power | -0.0001 |
| rewards.scales.leg_action_l2 | -0.01 |
| rewards.scales.torque_rate | -0.001 |
| rewards.scales.dof_vel_limits | -0.05 |
| rewards.scales.torque_limits | -0.1 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.wheel_contact_force_threshold | 1.0 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 0.9 |
| rewards.soft_torque_limit | 0.9 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.13] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.35 |
| init_state.default_joint_angles.lf1_Joint | -0.55 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.35 |
| init_state.default_joint_angles.rf1_Joint | 0.55 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | wheel |
| asset.wheel_names | ["l_wheel", "r_wheel"] |
| asset.offset | 0.0 |
| asset.l1 | 0.21 |
| asset.l2 | 0.25 |
| asset.penalize_contacts_on | ["base", "lf", "rf"] |
| asset.terminate_after_contacts_on | ["base", "lf", "rf"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.lift_robots | false |
| domain_rand.lift_interval_s | 7 |
| domain_rand.lift_height | 0.7 |
| domain_rand.downward_impulse_robots | true |
| domain_rand.downward_impulse_interval_s | 7 |
| domain_rand.downward_impulse_vel_range | [2.4, 2.8] |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F15 plane/wheel_legged\6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2016>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2021>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2026>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1909>) |
| nominal_state | -0.1 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2081>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1897>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1901>) |
| orientation | -10.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1905>) |
| dof_vel | -1e-06 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1930>) |
| dof_acc | -1e-08 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1936>) |
| torques | -1e-05 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1922>) |
| action_rate | -0.003 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1940>) |
| action_smooth | -0.003 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1944>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1962>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1979>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 4.0 |
| commands.advanced_max_ang_vel_curriculum | 4.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 10.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2.0, 2.0] |
| commands.ranges.height | [0.14, 0.3] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.5, 0.2, 0.1, 0.1, 0.1, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 60.0 |
| control.stiffness.f1 | 60.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -0.1 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -10.0 |
| rewards.scales.dof_vel | -1e-06 |
| rewards.scales.dof_acc | -1e-08 |
| rewards.scales.torques | -1e-05 |
| rewards.scales.action_rate | -0.003 |
| rewards.scales.action_smooth | -0.003 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.wheel_contact_force_threshold | 1.0 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.13] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.35 |
| init_state.default_joint_angles.lf1_Joint | -0.55 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.35 |
| init_state.default_joint_angles.rf1_Joint | 0.55 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | wheel |
| asset.wheel_names | ["l_wheel", "r_wheel"] |
| asset.offset | 0.0 |
| asset.l1 | 0.21 |
| asset.l2 | 0.25 |
| asset.penalize_contacts_on | ["base", "lf", "rf"] |
| asset.terminate_after_contacts_on | ["base", "lf", "rf"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.lift_robots | false |
| domain_rand.lift_interval_s | 7 |
| domain_rand.lift_height | 0.7 |
| domain_rand.downward_impulse_robots | true |
| domain_rand.downward_impulse_interval_s | 7 |
| domain_rand.downward_impulse_vel_range | [2.4, 2.8] |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F16 plane/wheel_legged\6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2017>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2022>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2027>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1914>) |
| nominal_state | -0.1 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2082>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1902>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1906>) |
| orientation | -20.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1910>) |
| dof_vel | -1e-06 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1935>) |
| dof_acc | -5e-08 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1941>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1927>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1945>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1949>) |
| wheel_torques | -10.0 | [_reward_wheel_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2011>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1967>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1984>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 4.0 |
| commands.advanced_max_ang_vel_curriculum | 4.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 10.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2.0, 2.0] |
| commands.ranges.height | [0.14, 0.3] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.5, 0.2, 0.1, 0.1, 0.1, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 60.0 |
| control.stiffness.f1 | 60.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -0.1 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -20.0 |
| rewards.scales.dof_vel | -1e-06 |
| rewards.scales.dof_acc | -5e-08 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.wheel_torques | -10.0 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.wheel_contact_force_threshold | 1.0 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.13] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.35 |
| init_state.default_joint_angles.lf1_Joint | -0.55 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.35 |
| init_state.default_joint_angles.rf1_Joint | 0.55 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | wheel |
| asset.wheel_names | ["l_wheel", "r_wheel"] |
| asset.offset | 0.0 |
| asset.l1 | 0.21 |
| asset.l2 | 0.25 |
| asset.penalize_contacts_on | ["base", "lf", "rf"] |
| asset.terminate_after_contacts_on | ["base", "lf", "rf"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.lift_robots | false |
| domain_rand.lift_interval_s | 7 |
| domain_rand.lift_height | 0.7 |
| domain_rand.downward_impulse_robots | true |
| domain_rand.downward_impulse_interval_s | 7 |
| domain_rand.downward_impulse_vel_range | [2.4, 2.8] |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F17 plane/wheel_legged\history10latent16_pd201.00.2terrian

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1925>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1930>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1935>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1818>) |
| base_height_enhance | 1.0 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1827>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1979>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1806>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1810>) |
| orientation | -20.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1814>) |
| dof_vel | -2e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1839>) |
| dof_acc | -1e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1845>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1831>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1849>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1853>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1871>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1888>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 6.0 |
| commands.advanced_max_ang_vel_curriculum | 6.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.1, 2.1] |
| commands.ranges.ang_vel_yaw | [-5.0, 5.0] |
| commands.ranges.height | [0.09, 0.33] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.3, 0.2, 0.0, 0.3, 0.2, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 20.0 |
| control.stiffness.f1 | 20.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.base_height_enhance | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -20.0 |
| rewards.scales.dof_vel | -2e-05 |
| rewards.scales.dof_acc | -1e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 10 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 250 |
| policy.latent_dim | 16 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F18 plane/wheel_legged\history10latent16_pd602.00.2terrian

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1925>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1930>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1935>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1818>) |
| base_height_enhance | 1.0 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1827>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1979>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1806>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1810>) |
| orientation | -20.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1814>) |
| dof_vel | -2e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1839>) |
| dof_acc | -1e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1845>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1831>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1849>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1853>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1871>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1888>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 6.0 |
| commands.advanced_max_ang_vel_curriculum | 6.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-4.0, 4.0] |
| commands.ranges.height | [0.09, 0.33] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.3, 0.2, 0.0, 0.3, 0.2, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 60.0 |
| control.stiffness.f1 | 60.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 2.0 |
| control.damping.f1 | 2.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.base_height_enhance | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -20.0 |
| rewards.scales.dof_vel | -2e-05 |
| rewards.scales.dof_acc | -1e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 10 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["base"] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 250 |
| policy.latent_dim | 16 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F19 plane/wheel_legged\linx_scales=3.0pd=101.00.2_randization=normal

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1963>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1968>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1973>) |
| base_height | 2.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1856>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:2017>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1844>) |
| ang_vel_xy | -0.07 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1848>) |
| orientation | -18.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1852>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1877>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1883>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1869>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1887>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1891>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1909>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.09, 0.35] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 10.0 |
| control.stiffness.f1 | 10.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 2.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.07 |
| rewards.scales.orientation | -18.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["rf", "lf", "base"] |
| asset.terminate_after_contacts_on | ["rf", "lf", "base"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| domain_rand.randomize_leg_kp | false |
| domain_rand.leg_kp_range | [0.95, 1.05] |
| domain_rand.randomize_leg_kd | false |
| domain_rand.leg_kd_range | [0.95, 1.05] |
| domain_rand.randomize_leg_motor_torque | false |
| domain_rand.leg_motor_torque_range | [0.95, 1.05] |
| domain_rand.randomize_leg_joint_offset | false |
| domain_rand.leg_joint_offset_range | [-0.03, 0.03] |
| domain_rand.randomize_wheel_motor_torque | false |
| domain_rand.wheel_motor_torque_range | [0.95, 1.05] |
| domain_rand.randomize_wheel_action_delay | false |
| domain_rand.wheel_delay_ms_range | [0, 4] |
| domain_rand.randomize_wheel_action_deadzone | false |
| domain_rand.wheel_action_deadzone_range | [0.0, 0.03] |
| domain_rand.randomize_wheel_radius_scale | false |
| domain_rand.wheel_radius_scale_range | [0.98, 1.02] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F20 plane/wheel_legged\linx_scales=3.0pd=201.00.2_randization=normal

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1963>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1968>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1973>) |
| base_height | 2.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1856>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:2017>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1844>) |
| ang_vel_xy | -0.07 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1848>) |
| orientation | -18.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1852>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1877>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1883>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1869>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1887>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1891>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1909>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.09, 0.35] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 20.0 |
| control.stiffness.f1 | 20.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 2.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.07 |
| rewards.scales.orientation | -18.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["rf", "lf", "base"] |
| asset.terminate_after_contacts_on | ["rf", "lf", "base"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| domain_rand.randomize_leg_kp | false |
| domain_rand.leg_kp_range | [0.95, 1.05] |
| domain_rand.randomize_leg_kd | false |
| domain_rand.leg_kd_range | [0.95, 1.05] |
| domain_rand.randomize_leg_motor_torque | false |
| domain_rand.leg_motor_torque_range | [0.95, 1.05] |
| domain_rand.randomize_leg_joint_offset | false |
| domain_rand.leg_joint_offset_range | [-0.03, 0.03] |
| domain_rand.randomize_wheel_motor_torque | false |
| domain_rand.wheel_motor_torque_range | [0.95, 1.05] |
| domain_rand.randomize_wheel_action_delay | false |
| domain_rand.wheel_delay_ms_range | [0, 4] |
| domain_rand.randomize_wheel_action_deadzone | false |
| domain_rand.wheel_action_deadzone_range | [0.0, 0.03] |
| domain_rand.randomize_wheel_radius_scale | false |
| domain_rand.wheel_radius_scale_range | [0.98, 1.02] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F21 plane/wheel_legged\linx_scales=3.0pd=51.50.25_randization=normal_new

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1963>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1968>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1973>) |
| base_height | 1.5 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1856>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:2017>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1844>) |
| ang_vel_xy | -0.07 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1848>) |
| orientation | -18.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1852>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1877>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1883>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1869>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1887>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1891>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1909>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.09, 0.35] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 5.0 |
| control.stiffness.f1 | 5.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.5 |
| control.damping.f1 | 1.5 |
| control.damping.wheel | 0.25 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.5 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.07 |
| rewards.scales.orientation | -18.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["rf", "lf", "base"] |
| asset.terminate_after_contacts_on | ["rf", "lf", "base"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| domain_rand.randomize_leg_kp | false |
| domain_rand.leg_kp_range | [0.95, 1.05] |
| domain_rand.randomize_leg_kd | false |
| domain_rand.leg_kd_range | [0.95, 1.05] |
| domain_rand.randomize_leg_motor_torque | false |
| domain_rand.leg_motor_torque_range | [0.95, 1.05] |
| domain_rand.randomize_leg_joint_offset | false |
| domain_rand.leg_joint_offset_range | [-0.03, 0.03] |
| domain_rand.randomize_wheel_motor_torque | false |
| domain_rand.wheel_motor_torque_range | [0.95, 1.05] |
| domain_rand.randomize_wheel_action_delay | false |
| domain_rand.wheel_delay_ms_range | [0, 4] |
| domain_rand.randomize_wheel_action_deadzone | false |
| domain_rand.wheel_action_deadzone_range | [0.0, 0.03] |
| domain_rand.randomize_wheel_radius_scale | false |
| domain_rand.wheel_radius_scale_range | [0.98, 1.02] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F22 plane/wheel_legged\linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 2.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1963>) |
| tracking_lin_vel_enhance | 2.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1968>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1973>) |
| base_height | 1.5 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1856>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:2017>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1844>) |
| ang_vel_xy | -0.07 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1848>) |
| orientation | -18.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1852>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1877>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1883>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1869>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1887>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1891>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1909>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2.0, 2.0] |
| commands.ranges.height | [0.09, 0.35] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.3, 0.3, 0.0, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 5.0 |
| control.stiffness.f1 | 5.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.5 |
| control.damping.f1 | 1.5 |
| control.damping.wheel | 0.25 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 2.0 |
| rewards.scales.tracking_lin_vel_enhance | 2.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.5 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.07 |
| rewards.scales.orientation | -18.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["rf", "lf", "base"] |
| asset.terminate_after_contacts_on | ["rf", "lf", "base"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| domain_rand.randomize_leg_kp | false |
| domain_rand.leg_kp_range | [0.95, 1.05] |
| domain_rand.randomize_leg_kd | false |
| domain_rand.leg_kd_range | [0.95, 1.05] |
| domain_rand.randomize_leg_motor_torque | false |
| domain_rand.leg_motor_torque_range | [0.95, 1.05] |
| domain_rand.randomize_leg_joint_offset | false |
| domain_rand.leg_joint_offset_range | [-0.03, 0.03] |
| domain_rand.randomize_wheel_motor_torque | false |
| domain_rand.wheel_motor_torque_range | [0.95, 1.05] |
| domain_rand.randomize_wheel_action_delay | false |
| domain_rand.wheel_delay_ms_range | [0, 4] |
| domain_rand.randomize_wheel_action_deadzone | false |
| domain_rand.wheel_action_deadzone_range | [0.0, 0.03] |
| domain_rand.randomize_wheel_radius_scale | false |
| domain_rand.wheel_radius_scale_range | [0.98, 1.02] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F23 plane/wheel_legged\linx_scales=3.0pd=61.00.2_randization=normal

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1963>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1968>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1973>) |
| base_height | 2.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1856>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:2017>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1844>) |
| ang_vel_xy | -0.07 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1848>) |
| orientation | -18.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1852>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1877>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1883>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1869>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1887>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1891>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1909>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.09, 0.35] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 6.0 |
| control.stiffness.f1 | 6.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 2.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.07 |
| rewards.scales.orientation | -18.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["rf", "lf", "base"] |
| asset.terminate_after_contacts_on | ["rf", "lf", "base"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| domain_rand.randomize_leg_kp | false |
| domain_rand.leg_kp_range | [0.95, 1.05] |
| domain_rand.randomize_leg_kd | false |
| domain_rand.leg_kd_range | [0.95, 1.05] |
| domain_rand.randomize_leg_motor_torque | false |
| domain_rand.leg_motor_torque_range | [0.95, 1.05] |
| domain_rand.randomize_leg_joint_offset | false |
| domain_rand.leg_joint_offset_range | [-0.03, 0.03] |
| domain_rand.randomize_wheel_motor_torque | false |
| domain_rand.wheel_motor_torque_range | [0.95, 1.05] |
| domain_rand.randomize_wheel_action_delay | false |
| domain_rand.wheel_delay_ms_range | [0, 4] |
| domain_rand.randomize_wheel_action_deadzone | false |
| domain_rand.wheel_action_deadzone_range | [0.0, 0.03] |
| domain_rand.randomize_wheel_radius_scale | false |
| domain_rand.wheel_radius_scale_range | [0.98, 1.02] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F24 plane/wheel_legged\linx_scales=4.0pd=101.00.2_randization=normal

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1843>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1848>) |
| base_height | 2.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1731>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1892>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1719>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1723>) |
| orientation | -10.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1744>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1762>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1784>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.09, 0.2] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 10.0 |
| control.stiffness.f1 | 10.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 2.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -10.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["rf", "lf", "base"] |
| asset.terminate_after_contacts_on | ["rf", "lf", "base"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 4.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F25 plane/wheel_legged\linx_scales=5.0pd=151.00.2_randization=hard

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1963>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1968>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1973>) |
| base_height | 2.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1856>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:2017>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1844>) |
| ang_vel_xy | -0.07 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1848>) |
| orientation | -18.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1852>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1877>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1883>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1869>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1887>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1891>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1909>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.09, 0.35] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 15.0 |
| control.stiffness.f1 | 15.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 2.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.07 |
| rewards.scales.orientation | -18.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["rf", "lf", "base"] |
| asset.terminate_after_contacts_on | ["rf", "lf", "base"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.05, 2.5] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-3.0, 4.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.7, 1.3] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.07, 0.07, 0.06] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 4 |
| domain_rand.max_push_vel_xy | 3.2 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.85, 1.15] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.85, 1.15] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.85, 1.15] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.07, 0.07] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 14] |
| domain_rand.randomize_leg_kp | true |
| domain_rand.leg_kp_range | [0.85, 1.15] |
| domain_rand.randomize_leg_kd | true |
| domain_rand.leg_kd_range | [0.85, 1.15] |
| domain_rand.randomize_leg_motor_torque | true |
| domain_rand.leg_motor_torque_range | [0.85, 1.15] |
| domain_rand.randomize_leg_joint_offset | true |
| domain_rand.leg_joint_offset_range | [-0.07, 0.07] |
| domain_rand.randomize_wheel_motor_torque | true |
| domain_rand.wheel_motor_torque_range | [0.85, 1.15] |
| domain_rand.randomize_wheel_action_delay | true |
| domain_rand.wheel_delay_ms_range | [0, 10] |
| domain_rand.randomize_wheel_action_deadzone | true |
| domain_rand.wheel_action_deadzone_range | [0.0, 0.08] |
| domain_rand.randomize_wheel_radius_scale | true |
| domain_rand.wheel_radius_scale_range | [0.93, 1.07] |
| normalization.obs_scales.lin_vel | 5.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F26 plane/wheel_legged\linx_scales=5.0pd=151.00.2_randization=mid

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1963>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1968>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1973>) |
| base_height | 2.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1856>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:2017>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1844>) |
| ang_vel_xy | -0.07 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1848>) |
| orientation | -18.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1852>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1877>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1883>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1869>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1887>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1891>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1909>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.09, 0.35] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 15.0 |
| control.stiffness.f1 | 15.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 2.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.07 |
| rewards.scales.orientation | -18.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["rf", "lf", "base"] |
| asset.terminate_after_contacts_on | ["rf", "lf", "base"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| domain_rand.randomize_leg_kp | true |
| domain_rand.leg_kp_range | [0.95, 1.05] |
| domain_rand.randomize_leg_kd | true |
| domain_rand.leg_kd_range | [0.95, 1.05] |
| domain_rand.randomize_leg_motor_torque | true |
| domain_rand.leg_motor_torque_range | [0.95, 1.05] |
| domain_rand.randomize_leg_joint_offset | true |
| domain_rand.leg_joint_offset_range | [-0.03, 0.03] |
| domain_rand.randomize_wheel_motor_torque | true |
| domain_rand.wheel_motor_torque_range | [0.95, 1.05] |
| domain_rand.randomize_wheel_action_delay | true |
| domain_rand.wheel_delay_ms_range | [0, 4] |
| domain_rand.randomize_wheel_action_deadzone | true |
| domain_rand.wheel_action_deadzone_range | [0.0, 0.03] |
| domain_rand.randomize_wheel_radius_scale | true |
| domain_rand.wheel_radius_scale_range | [0.98, 1.02] |
| normalization.obs_scales.lin_vel | 5.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F27 plane/wheel_legged\linx_scales=5.0pd=151.00.2_randization=normal

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1843>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1848>) |
| base_height | 2.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1731>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1892>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1719>) |
| ang_vel_xy | -0.07 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1723>) |
| orientation | -18.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1744>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1762>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1784>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.09, 0.35] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 15.0 |
| control.stiffness.f1 | 15.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 2.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.07 |
| rewards.scales.orientation | -18.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["rf", "lf", "base"] |
| asset.terminate_after_contacts_on | ["rf", "lf", "base"] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 5.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F28 plane/wheel_legged\recover_from_lied_on_ground

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1843>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1848>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1731>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1892>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1719>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1723>) |
| orientation | -10.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1744>) |
| action_rate | -0.1 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1762>) |
| action_smooth | -0.1 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.1, 0.2] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 10.0 |
| control.stiffness.f1 | 10.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -10.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.1 |
| rewards.scales.action_smooth | -0.1 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 8192 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.23 |
| init_state.default_joint_angles.lf1_Joint | -0.65 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.23 |
| init_state.default_joint_angles.rf1_Joint | 0.65 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V1/urdf/infantry_V1.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F29 plane/wheel_legged\recover_from_lied_on_ground_yuntai

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1843>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1848>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1731>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1892>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1719>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1723>) |
| orientation | -10.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1744>) |
| action_rate | -0.1 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1762>) |
| action_smooth | -0.1 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.07, 0.12] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 10.0 |
| control.stiffness.f1 | 10.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -10.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.1 |
| rewards.scales.action_smooth | -0.1 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 8192 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.23 |
| init_state.default_joint_angles.lf1_Joint | -0.65 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.23 |
| init_state.default_joint_angles.rf1_Joint | 0.65 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F30 plane/wheel_legged\recover_from_lied_on_ground_yuntai_height_jiajiajia

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1843>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1848>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1731>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1892>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1719>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1723>) |
| orientation | -10.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1744>) |
| action_rate | -0.1 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1762>) |
| action_smooth | -0.1 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.1, 0.2] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 10.0 |
| control.stiffness.f1 | 10.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -10.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.1 |
| rewards.scales.action_smooth | -0.1 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 8192 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.23 |
| init_state.default_joint_angles.lf1_Joint | -0.65 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.23 |
| init_state.default_joint_angles.rf1_Joint | 0.65 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F31 plane/wheel_legged\recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1843>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1848>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1731>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1892>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1719>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1723>) |
| orientation | -10.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1744>) |
| action_rate | -0.1 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1762>) |
| action_smooth | -0.1 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.1, 0.3] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 10.0 |
| control.stiffness.f1 | 10.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -10.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.1 |
| rewards.scales.action_smooth | -0.1 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 8192 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.23 |
| init_state.default_joint_angles.lf1_Joint | -0.65 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.23 |
| init_state.default_joint_angles.rf1_Joint | 0.65 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F32 plane/wheel_legged\recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1843>) |
| tracking_ang_vel | 1.1 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1848>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1731>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1892>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1719>) |
| ang_vel_xy | -0.15 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1723>) |
| orientation | -30.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1744>) |
| action_rate | -0.05 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1762>) |
| action_smooth | -0.05 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-6, 6] |
| commands.ranges.height | [0.1, 0.2] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 10.0 |
| control.stiffness.f1 | 10.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.1 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.15 |
| rewards.scales.orientation | -30.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.05 |
| rewards.scales.action_smooth | -0.05 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 8192 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.23 |
| init_state.default_joint_angles.lf1_Joint | -0.65 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.23 |
| init_state.default_joint_angles.rf1_Joint | 0.65 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F33 plane/wheel_legged\recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.1 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1843>) |
| tracking_ang_vel | 1.1 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1848>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1731>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1892>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1719>) |
| ang_vel_xy | -0.2 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1723>) |
| orientation | -30.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1744>) |
| action_rate | -0.05 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1762>) |
| action_smooth | -0.05 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-11, 11] |
| commands.ranges.height | [0.1, 0.2] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 10.0 |
| control.stiffness.f1 | 10.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.1 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.1 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.2 |
| rewards.scales.orientation | -30.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.05 |
| rewards.scales.action_smooth | -0.05 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 8192 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.23 |
| init_state.default_joint_angles.lf1_Joint | -0.65 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.23 |
| init_state.default_joint_angles.rf1_Joint | 0.65 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F34 plane/wheel_legged\recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1843>) |
| tracking_ang_vel | 3.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1848>) |
| tracking_ang_vel_enhance | 3.0 | [_reward_tracking_ang_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1853>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1731>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1892>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1719>) |
| ang_vel_xy | -0.2 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1723>) |
| orientation | -30.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1744>) |
| action_rate | -0.05 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1762>) |
| action_smooth | -0.05 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-15, 15] |
| commands.ranges.height | [0.1, 0.2] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 10.0 |
| control.stiffness.f1 | 10.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 3.0 |
| rewards.scales.tracking_ang_vel_enhance | 3.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.2 |
| rewards.scales.orientation | -30.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.05 |
| rewards.scales.action_smooth | -0.05 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 8192 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.23 |
| init_state.default_joint_angles.lf1_Joint | -0.65 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.23 |
| init_state.default_joint_angles.rf1_Joint | 0.65 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F35 plane/wheel_legged\recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1843>) |
| tracking_ang_vel | 4.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1848>) |
| tracking_ang_vel_enhance | 4.0 | [_reward_tracking_ang_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1853>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1731>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1892>) |
| lin_vel_z | -1.0 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1719>) |
| ang_vel_xy | -0.2 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1723>) |
| orientation | -30.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1744>) |
| action_rate | -0.05 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1762>) |
| action_smooth | -0.05 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-18, 18] |
| commands.ranges.height | [0.1, 0.2] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 10.0 |
| control.stiffness.f1 | 10.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 4.0 |
| rewards.scales.tracking_ang_vel_enhance | 4.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -1.0 |
| rewards.scales.ang_vel_xy | -0.2 |
| rewards.scales.orientation | -30.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.05 |
| rewards.scales.action_smooth | -0.05 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 8192 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.23 |
| init_state.default_joint_angles.lf1_Joint | -0.65 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.23 |
| init_state.default_joint_angles.rf1_Joint | 0.65 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F36 plane/wheel_legged\上台阶1

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1843>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1848>) |
| base_height | 2.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1731>) |
| base_height_enhance | 1.5 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1740>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1892>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1719>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1723>) |
| orientation | -10.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1744>) |
| action_rate | -0.05 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1762>) |
| action_smooth | -0.05 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | false |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2.0, 2.0] |
| commands.ranges.height | [0.1, 0.33] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 15.0 |
| control.stiffness.f1 | 15.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 2.0 |
| rewards.scales.base_height_enhance | 1.5 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -10.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.05 |
| rewards.scales.action_smooth | -0.05 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 8192 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.23 |
| init_state.default_joint_angles.lf1_Joint | -0.65 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.23 |
| init_state.default_joint_angles.rf1_Joint | 0.65 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F37 plane/wheel_legged\上台阶2

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1843>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1848>) |
| base_height | 2.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1731>) |
| base_height_enhance | 1.5 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1740>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1892>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1719>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1723>) |
| orientation | -10.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1744>) |
| action_rate | -0.05 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1762>) |
| action_smooth | -0.05 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | false |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2.0, 2.0] |
| commands.ranges.height | [0.23, 0.33] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.0, 0.0, 0.0, 0.5, 0.5, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 15.0 |
| control.stiffness.f1 | 15.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 2.0 |
| rewards.scales.base_height_enhance | 1.5 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -10.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.05 |
| rewards.scales.action_smooth | -0.05 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 8192 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.23 |
| init_state.default_joint_angles.lf1_Joint | -0.65 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.23 |
| init_state.default_joint_angles.rf1_Joint | 0.65 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 2.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F38 plane/wheel_legged\上台阶3

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.5 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.5 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1843>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1848>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1731>) |
| base_height_enhance | 1.0 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1740>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1892>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1719>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1723>) |
| orientation | -10.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1744>) |
| action_rate | -0.05 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1762>) |
| action_smooth | -0.05 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | false |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.3, 2.3] |
| commands.ranges.ang_vel_yaw | [-2.0, 2.0] |
| commands.ranges.height | [0.23, 0.33] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.0, 0.0, 0.0, 0.5, 0.5, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 15.0 |
| control.stiffness.f1 | 15.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.5 |
| rewards.scales.tracking_lin_vel_enhance | 1.5 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.base_height_enhance | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -10.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.05 |
| rewards.scales.action_smooth | -0.05 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 8192 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.23 |
| init_state.default_joint_angles.lf1_Joint | -0.65 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.23 |
| init_state.default_joint_angles.rf1_Joint | 0.65 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F39 plane/wheel_legged\上台阶3_angz+

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.5 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1838>) |
| tracking_lin_vel_enhance | 1.5 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1843>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1848>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1731>) |
| base_height_enhance | 1.0 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1740>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1892>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1719>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1723>) |
| orientation | -10.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1727>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1752>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1758>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1744>) |
| action_rate | -0.05 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1762>) |
| action_smooth | -0.05 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1766>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1784>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1801>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | false |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.3, 2.3] |
| commands.ranges.ang_vel_yaw | [-5.0, 5.0] |
| commands.ranges.height | [0.17, 0.33] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.0, 0.0, 0.0, 0.5, 0.5, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 15.0 |
| control.stiffness.f1 | 15.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.5 |
| rewards.scales.tracking_lin_vel_enhance | 1.5 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.base_height_enhance | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -10.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.05 |
| rewards.scales.action_smooth | -0.05 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 8192 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.23 |
| init_state.default_joint_angles.lf1_Joint | -0.65 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.23 |
| init_state.default_joint_angles.rf1_Joint | 0.65 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F40 plane/wheel_legged\上台阶3_angz+添加随机地形，进一步训练v1

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1925>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1930>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1935>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1818>) |
| base_height_enhance | 1.0 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1827>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1979>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1806>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1810>) |
| orientation | -20.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1814>) |
| dof_vel | -2e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1839>) |
| dof_acc | -1e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1845>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1831>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1849>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1853>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1871>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1888>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 6.0 |
| commands.advanced_max_ang_vel_curriculum | 6.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-4.0, 4.0] |
| commands.ranges.height | [0.09, 0.33] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.3, 0.2, 0.0, 0.3, 0.2, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 15.0 |
| control.stiffness.f1 | 15.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.base_height_enhance | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -20.0 |
| rewards.scales.dof_vel | -2e-05 |
| rewards.scales.dof_acc | -1e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 8192 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.23 |
| init_state.default_joint_angles.lf1_Joint | -0.65 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.23 |
| init_state.default_joint_angles.rf1_Joint | 0.65 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F41 plane/wheel_legged\上台阶3_angz+添加随机地形，进一步训练v2

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1925>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1930>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1935>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1818>) |
| base_height_enhance | 1.0 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1827>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1979>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1806>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1810>) |
| orientation | -20.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1814>) |
| dof_vel | -2e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1839>) |
| dof_acc | -1e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1845>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1831>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1849>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1853>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1871>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1888>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 6.0 |
| commands.advanced_max_ang_vel_curriculum | 6.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 5.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-4.0, 4.0] |
| commands.ranges.height | [0.09, 0.33] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.3, 0.2, 0.0, 0.3, 0.2, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 15.0 |
| control.stiffness.f1 | 15.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.base_height_enhance | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -20.0 |
| rewards.scales.dof_vel | -2e-05 |
| rewards.scales.dof_acc | -1e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 8192 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.23 |
| init_state.default_joint_angles.lf1_Joint | -0.65 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.23 |
| init_state.default_joint_angles.rf1_Joint | 0.65 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F42 plane/wheel_legged\上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1925>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1930>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1935>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1818>) |
| base_height_enhance | 1.0 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1827>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1979>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1806>) |
| ang_vel_xy | -0.07 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1810>) |
| orientation | -20.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1814>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1839>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1845>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1831>) |
| action_rate | -0.05 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1849>) |
| action_smooth | -0.05 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1853>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1871>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1888>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.8 |
| commands.advanced_max_curriculum | 2.8 |
| commands.basic_max_ang_vel_curriculum | 6.0 |
| commands.advanced_max_ang_vel_curriculum | 6.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 10.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-4.0, 4.0] |
| commands.ranges.height | [0.09, 0.33] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.3, 0.2, 0.0, 0.3, 0.2, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 15.0 |
| control.stiffness.f1 | 15.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.base_height_enhance | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.07 |
| rewards.scales.orientation | -20.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.05 |
| rewards.scales.action_smooth | -0.05 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 8192 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.1] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.23 |
| init_state.default_joint_angles.lf1_Joint | -0.65 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.23 |
| init_state.default_joint_angles.rf1_Joint | 0.65 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F43 plane/wheel_legged\腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2016>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2021>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2026>) |
| wheel_air_theta0 | 1.0 | [_reward_wheel_air_theta0](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2042>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1909>) |
| base_height_enhance | 1.0 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1918>) |
| nominal_state | -2.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2081>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1897>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1901>) |
| orientation | -15.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1905>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1930>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1936>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1922>) |
| action_rate | -0.1 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1940>) |
| action_smooth | -0.1 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1944>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1962>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1979>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 4.0 |
| commands.advanced_max_ang_vel_curriculum | 4.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 10.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2.0, 2.0] |
| commands.ranges.height | [0.13, 0.35] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.5, 0.2, 0.1, 0.1, 0.1, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 15.0 |
| control.stiffness.f1 | 15.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.wheel_air_theta0 | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.base_height_enhance | 1.0 |
| rewards.scales.nominal_state | -2.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -15.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.1 |
| rewards.scales.action_smooth | -0.1 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.wheel_contact_force_threshold | 1.0 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.13] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.35 |
| init_state.default_joint_angles.lf1_Joint | -0.55 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.35 |
| init_state.default_joint_angles.rf1_Joint | 0.55 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/hero_2_V1/urdf/hero_2_V1.urdf |
| asset.name | WheelLegged |
| asset.foot_name | wheel |
| asset.wheel_names | ["l_wheel", "r_wheel"] |
| asset.offset | 0.0 |
| asset.l1 | 0.21 |
| asset.l2 | 0.25 |
| asset.penalize_contacts_on | ["base", "lf", "rf"] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.lift_robots | false |
| domain_rand.lift_interval_s | 7 |
| domain_rand.lift_height | 0.7 |
| domain_rand.downward_impulse_robots | true |
| domain_rand.downward_impulse_interval_s | 7 |
| domain_rand.downward_impulse_vel_range | [2.4, 2.8] |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F44 plane/wheel_legged\腿熊第一版本recover

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1925>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1930>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1935>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1818>) |
| base_height_enhance | 1.0 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1827>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1979>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1806>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1810>) |
| orientation | -20.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1814>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1839>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1845>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1831>) |
| action_rate | -0.1 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1849>) |
| action_smooth | -0.1 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1853>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1871>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1888>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 4.5 |
| commands.advanced_max_ang_vel_curriculum | 4.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 10.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2.0, 2.0] |
| commands.ranges.height | [0.11, 0.31] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.3, 0.2, 0.0, 0.3, 0.2, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 15.0 |
| control.stiffness.f1 | 15.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.base_height_enhance | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -20.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.1 |
| rewards.scales.action_smooth | -0.1 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.13] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.35 |
| init_state.default_joint_angles.lf1_Joint | -0.55 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.35 |
| init_state.default_joint_angles.rf1_Joint | 0.55 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/hero_2_V1/urdf/hero_2_V1.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.21 |
| asset.l2 | 0.25 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F45 plane/wheel_legged\腿熊第三版本加入随机地形继续训练很久recover

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1925>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1930>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1935>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1818>) |
| base_height_enhance | 1.0 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1827>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1979>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1806>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1810>) |
| orientation | -20.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1814>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1839>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1845>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1831>) |
| action_rate | -0.1 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1849>) |
| action_smooth | -0.1 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1853>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1871>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1888>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 4.0 |
| commands.advanced_max_ang_vel_curriculum | 4.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 10.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2.0, 2.0] |
| commands.ranges.height | [0.11, 0.31] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.3, 0.2, 0.0, 0.3, 0.2, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 15.0 |
| control.stiffness.f1 | 15.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.base_height_enhance | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -20.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.1 |
| rewards.scales.action_smooth | -0.1 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.13] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.35 |
| init_state.default_joint_angles.lf1_Joint | -0.55 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.35 |
| init_state.default_joint_angles.rf1_Joint | 0.55 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/hero_2_V1/urdf/hero_2_V1.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.21 |
| asset.l2 | 0.25 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F46 plane/wheel_legged\腿熊第二版本加入随机地形recover

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1925>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1930>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1935>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1818>) |
| base_height_enhance | 1.0 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1827>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1979>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1806>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1810>) |
| orientation | -20.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1814>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1839>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1845>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1831>) |
| action_rate | -0.1 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1849>) |
| action_smooth | -0.1 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1853>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1871>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1888>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 4.0 |
| commands.advanced_max_ang_vel_curriculum | 4.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 10.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2.0, 2.0] |
| commands.ranges.height | [0.11, 0.31] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.3, 0.2, 0.0, 0.3, 0.2, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 15.0 |
| control.stiffness.f1 | 15.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.base_height_enhance | 1.0 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -20.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.1 |
| rewards.scales.action_smooth | -0.1 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.13] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.35 |
| init_state.default_joint_angles.lf1_Joint | -0.55 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.35 |
| init_state.default_joint_angles.rf1_Joint | 0.55 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/hero_2_V1/urdf/hero_2_V1.urdf |
| asset.name | WheelLegged |
| asset.foot_name | None |
| asset.offset | 0.0 |
| asset.l1 | 0.21 |
| asset.l2 | 0.25 |
| asset.penalize_contacts_on | [] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F47 plane/wheel_legged\腿熊第五版本

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2016>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2021>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2026>) |
| wheel_air_theta0 | 0.05 | [_reward_wheel_air_theta0](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2042>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1909>) |
| base_height_enhance | 1.0 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1918>) |
| nominal_state | -2.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2081>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1897>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1901>) |
| orientation | -15.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1905>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1930>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1936>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1922>) |
| action_rate | -0.01 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1940>) |
| action_smooth | -0.01 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1944>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1962>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1979>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 4.0 |
| commands.advanced_max_ang_vel_curriculum | 4.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 10.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2.0, 2.0] |
| commands.ranges.height | [0.13, 0.35] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.5, 0.2, 0.1, 0.1, 0.1, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 15.0 |
| control.stiffness.f1 | 15.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.wheel_air_theta0 | 0.05 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.base_height_enhance | 1.0 |
| rewards.scales.nominal_state | -2.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -15.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.01 |
| rewards.scales.action_smooth | -0.01 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.wheel_contact_force_threshold | 1.0 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.13] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.35 |
| init_state.default_joint_angles.lf1_Joint | -0.55 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.35 |
| init_state.default_joint_angles.rf1_Joint | 0.55 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/hero_2_V1/urdf/hero_2_V1.urdf |
| asset.name | WheelLegged |
| asset.foot_name | wheel |
| asset.wheel_names | ["l_wheel", "r_wheel"] |
| asset.offset | 0.0 |
| asset.l1 | 0.21 |
| asset.l2 | 0.25 |
| asset.penalize_contacts_on | ["base", "lf", "rf"] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.lift_robots | false |
| domain_rand.lift_interval_s | 7 |
| domain_rand.lift_height | 0.7 |
| domain_rand.downward_impulse_robots | true |
| domain_rand.downward_impulse_interval_s | 7 |
| domain_rand.downward_impulse_vel_range | [2.4, 2.8] |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F48 plane/wheel_legged\腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2016>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2021>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2026>) |
| wheel_air_theta0 | 1.0 | [_reward_wheel_air_theta0](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2042>) |
| base_height | 1.0 | [_reward_base_height](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1909>) |
| base_height_enhance | 1.0 | [_reward_base_height_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1918>) |
| nominal_state | -4.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2081>) |
| lin_vel_z | -0.1 | [_reward_lin_vel_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1897>) |
| ang_vel_xy | -0.05 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1901>) |
| orientation | -20.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1905>) |
| dof_vel | -5e-05 | [_reward_dof_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1930>) |
| dof_acc | -2.5e-07 | [_reward_dof_acc](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1936>) |
| torques | -0.0001 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1922>) |
| action_rate | -0.1 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1940>) |
| action_smooth | -0.1 | [_reward_action_smooth](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1944>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1962>) |
| dof_pos_limits | -1.0 | [_reward_dof_pos_limits](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1979>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | true |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 2.5 |
| commands.basic_max_ang_vel_curriculum | 4.0 |
| commands.advanced_max_ang_vel_curriculum | 4.0 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 10.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.0, 2.0] |
| commands.ranges.ang_vel_yaw | [-2.0, 2.0] |
| commands.ranges.height | [0.13, 0.35] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | trimesh |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.5, 0.2, 0.1, 0.1, 0.1, 0.0] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 15.0 |
| control.stiffness.f1 | 15.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 1.0 |
| control.damping.f1 | 1.0 |
| control.damping.wheel | 0.1 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.wheel_air_theta0 | 1.0 |
| rewards.scales.base_height | 1.0 |
| rewards.scales.base_height_enhance | 1.0 |
| rewards.scales.nominal_state | -4.0 |
| rewards.scales.lin_vel_z | -0.1 |
| rewards.scales.ang_vel_xy | -0.05 |
| rewards.scales.orientation | -20.0 |
| rewards.scales.dof_vel | -5e-05 |
| rewards.scales.dof_acc | -2.5e-07 |
| rewards.scales.torques | -0.0001 |
| rewards.scales.action_rate | -0.1 |
| rewards.scales.action_smooth | -0.1 |
| rewards.scales.collision | -1.0 |
| rewards.scales.dof_pos_limits | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 1 |
| rewards.tracking_sigma | 0.25 |
| rewards.wheel_contact_force_threshold | 1.0 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.13] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | -0.35 |
| init_state.default_joint_angles.lf1_Joint | -0.55 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | 0.35 |
| init_state.default_joint_angles.rf1_Joint | 0.55 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /root/gpufree-data/final_version/plane/resources/robots/hero_2_V1/urdf/hero_2_V1.urdf |
| asset.name | WheelLegged |
| asset.foot_name | wheel |
| asset.wheel_names | ["l_wheel", "r_wheel"] |
| asset.offset | 0.0 |
| asset.l1 | 0.21 |
| asset.l2 | 0.25 |
| asset.penalize_contacts_on | ["base", "lf", "rf"] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.0, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 7 |
| domain_rand.max_push_vel_xy | 2.0 |
| domain_rand.lift_robots | false |
| domain_rand.lift_interval_s | 7 |
| domain_rand.lift_height | 0.7 |
| domain_rand.downward_impulse_robots | true |
| domain_rand.downward_impulse_interval_s | 7 |
| domain_rand.downward_impulse_vel_range | [2.4, 2.8] |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 10] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [50, 100, 2] |
| viewer.lookat | [60, 100, 1] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 1.0 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F49 jump/current

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/wheel_legged/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1897>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1906>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1911>) |
| flight | 0.15 | [_reward_flight](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1791>) |
| encourage_jump | 1.0 | [_reward_encourage_jump](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1729>) |
| base_height_flight | 6.0 | [_reward_base_height_flight](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1770>) |
| leg_tuck | 1.7 | [_reward_leg_tuck](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1764>) |
| takeoff_extend | 0.5 | [_reward_takeoff_extend](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1776>) |
| line_z | 6.0 | [_reward_line_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1759>) |
| pen_theta_no0 | -2.0 | [_reward_pen_theta_no0](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1957>) |
| action_rate | -0.04 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1821>) |
| torques | -5e-05 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1803>) |
| orientation | -25.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1799>) |
| ang_vel_xy | -0.1 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1796>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1949>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1843>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | false |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 20.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.1, 2.1] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.12, 0.15] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 6.0 |
| control.stiffness.f1 | 6.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 0.5 |
| control.damping.f1 | 0.5 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.flight | 0.15 |
| rewards.scales.encourage_jump | 1.0 |
| rewards.scales.base_height_flight | 6.0 |
| rewards.scales.leg_tuck | 1.7 |
| rewards.scales.takeoff_extend | 0.5 |
| rewards.scales.line_z | 6.0 |
| rewards.scales.pen_theta_no0 | -2.0 |
| rewards.scales.action_rate | -0.04 |
| rewards.scales.torques | -5e-05 |
| rewards.scales.orientation | -25.0 |
| rewards.scales.ang_vel_xy | -0.1 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.collision | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 2.5 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | {WHEEL_LEGGED_GYM_ROOT_DIR}/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | wheel |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["lf", "rf", "base"] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.5, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 3.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 5 |
| domain_rand.max_push_vel_xy | 1.5 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | false |
| domain_rand.delay_ms_range | [0, 5] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。


## F50 jump/wheel_legged\p60.50.2目前测试下来最好的

[base配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot_config.py>) · [覆盖配置](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/wheel_legged_config.py>) · [环境实现](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py>)

| 奖励项 | 权重 | 实际定义位置 |
|---|---|---|
| tracking_lin_vel | 1.0 | [_reward_tracking_lin_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1897>) |
| tracking_lin_vel_enhance | 1.0 | [_reward_tracking_lin_vel_enhance](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1906>) |
| tracking_ang_vel | 1.0 | [_reward_tracking_ang_vel](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1911>) |
| flight | 0.15 | [_reward_flight](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1791>) |
| encourage_jump | 1.0 | [_reward_encourage_jump](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1729>) |
| base_height_flight | 6.0 | [_reward_base_height_flight](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1770>) |
| leg_tuck | 1.7 | [_reward_leg_tuck](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1764>) |
| takeoff_extend | 0.5 | [_reward_takeoff_extend](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1776>) |
| line_z | 6.0 | [_reward_line_z](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1759>) |
| pen_theta_no0 | -2.0 | [_reward_pen_theta_no0](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1957>) |
| action_rate | -0.04 | [_reward_action_rate](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1821>) |
| torques | -5e-05 | [_reward_torques](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1803>) |
| orientation | -25.0 | [_reward_orientation](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1799>) |
| ang_vel_xy | -0.1 | [_reward_ang_vel_xy](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1796>) |
| nominal_state | -1.0 | [_reward_nominal_state](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1949>) |
| collision | -1.0 | [_reward_collision](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1843>) |



| 字段 | 原值 |
|---|---|
| commands.curriculum | false |
| commands.basic_max_curriculum | 2.5 |
| commands.advanced_max_curriculum | 1.5 |
| commands.curriculum_threshold | 0.7 |
| commands.num_commands | 3 |
| commands.resampling_time | 20.0 |
| commands.heading_command | false |
| commands.ranges.lin_vel_x | [-2.1, 2.1] |
| commands.ranges.ang_vel_yaw | [-2, 2] |
| commands.ranges.height | [0.12, 0.15] |
| commands.ranges.heading | [-3.14, 3.14] |
| terrain.mesh_type | plane |
| terrain.horizontal_scale | 0.1 |
| terrain.vertical_scale | 0.005 |
| terrain.border_size | 25 |
| terrain.curriculum | true |
| terrain.static_friction | 0.5 |
| terrain.dynamic_friction | 0.5 |
| terrain.restitution | 0.5 |
| terrain.measure_heights | true |
| terrain.measured_points_x | [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5] |
| terrain.measured_points_y | [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3] |
| terrain.selected | false |
| terrain.terrain_kwargs | null（未配置/待填） |
| terrain.max_init_terrain_level | 5 |
| terrain.terrain_length | 8.0 |
| terrain.terrain_width | 8.0 |
| terrain.num_rows | 10 |
| terrain.num_cols | 20 |
| terrain.terrain_proportions | [0.2, 0.2, 0.2, 0.1, 0.2, 0.1] |
| terrain.slope_treshold | 0.75 |
| control.control_type | P |
| control.stiffness.f0 | 6.0 |
| control.stiffness.f1 | 6.0 |
| control.stiffness.wheel | 0.0 |
| control.damping.f0 | 0.5 |
| control.damping.f1 | 0.5 |
| control.damping.wheel | 0.2 |
| control.action_scale | 0.5 |
| control.decimation | 2 |
| control.pos_action_scale | 0.5 |
| control.vel_action_scale | 10.0 |
| rewards.scales.tracking_lin_vel | 1.0 |
| rewards.scales.tracking_lin_vel_enhance | 1.0 |
| rewards.scales.tracking_ang_vel | 1.0 |
| rewards.scales.flight | 0.15 |
| rewards.scales.encourage_jump | 1.0 |
| rewards.scales.base_height_flight | 6.0 |
| rewards.scales.leg_tuck | 1.7 |
| rewards.scales.takeoff_extend | 0.5 |
| rewards.scales.line_z | 6.0 |
| rewards.scales.pen_theta_no0 | -2.0 |
| rewards.scales.action_rate | -0.04 |
| rewards.scales.torques | -5e-05 |
| rewards.scales.orientation | -25.0 |
| rewards.scales.ang_vel_xy | -0.1 |
| rewards.scales.nominal_state | -1.0 |
| rewards.scales.collision | -1.0 |
| rewards.only_positive_rewards | false |
| rewards.clip_single_reward | 2.5 |
| rewards.tracking_sigma | 0.25 |
| rewards.soft_dof_pos_limit | 0.97 |
| rewards.soft_dof_vel_limit | 1.0 |
| rewards.soft_torque_limit | 1.0 |
| rewards.base_height_target | 0.18 |
| rewards.max_contact_force | 100.0 |



<details markdown="1"><summary>其他合并配置：观测/初始化/接触名单/随机化/物理</summary>


| 字段 | 原值 |
|---|---|
| env.num_envs | 4096 |
| env.num_observations | 25 |
| env.num_privileged_obs | 141 |
| env.obs_history_length | 5 |
| env.obs_history_dec | 1 |
| env.num_actions | 6 |
| env.env_spacing | 3.0 |
| env.send_timeouts | true |
| env.episode_length_s | 20 |
| env.dof_vel_use_pos_diff | true |
| env.fail_to_terminal_time_s | 1 |
| init_state.pos | [0.0, 0.0, 0.2] |
| init_state.rot | [0.0, 0.0, 0.0, 1.0] |
| init_state.lin_vel | [0.0, 0.0, 0.0] |
| init_state.ang_vel | [0.0, 0.0, 0.0] |
| init_state.default_joint_angles.lf0_Joint | 0.2 |
| init_state.default_joint_angles.lf1_Joint | 0.4 |
| init_state.default_joint_angles.l_wheel_Joint | 0.0 |
| init_state.default_joint_angles.rf0_Joint | -0.2 |
| init_state.default_joint_angles.rf1_Joint | -0.4 |
| init_state.default_joint_angles.r_wheel_Joint | 0.0 |
| asset.dof_armature.hip | 0.0 |
| asset.dof_armature.thigh | 0.0 |
| asset.dof_armature.calf | 0.0 |
| asset.dof_armature.wheel | 0.0 |
| asset.file | /data/RL/RL/jump/wheel_leg/Wheel-Legged-Gym-master/resources/robots/infantry_V4/urdf/infantry_V4_increase.urdf |
| asset.name | WheelLegged |
| asset.foot_name | wheel |
| asset.offset | 0.0 |
| asset.l1 | 0.175 |
| asset.l2 | 0.208 |
| asset.penalize_contacts_on | ["lf", "rf", "base"] |
| asset.terminate_after_contacts_on | [] |
| asset.disable_gravity | false |
| asset.collapse_fixed_joints | true |
| asset.fix_base_link | false |
| asset.default_dof_drive_mode | 3 |
| asset.self_collisions | 1 |
| asset.replace_cylinder_with_capsule | true |
| asset.flip_visual_attachments | false |
| asset.density | 0.001 |
| asset.angular_damping | 0.0 |
| asset.linear_damping | 0.0 |
| asset.max_angular_velocity | 1000.0 |
| asset.max_linear_velocity | 1000.0 |
| asset.armature | 0.0 |
| asset.thickness | 0.01 |
| domain_rand.randomize_friction | true |
| domain_rand.friction_range | [0.1, 2.0] |
| domain_rand.randomize_restitution | true |
| domain_rand.restitution_range | [0.5, 1.0] |
| domain_rand.randomize_base_mass | true |
| domain_rand.added_mass_range | [-2.0, 23.0] |
| domain_rand.randomize_inertia | true |
| domain_rand.randomize_inertia_range | [0.8, 1.2] |
| domain_rand.randomize_base_com | true |
| domain_rand.rand_com_vec | [0.05, 0.05, 0.05] |
| domain_rand.push_robots | true |
| domain_rand.push_interval_s | 5 |
| domain_rand.max_push_vel_xy | 1.5 |
| domain_rand.randomize_Kp | true |
| domain_rand.randomize_Kp_range | [0.9, 1.1] |
| domain_rand.randomize_Kd | true |
| domain_rand.randomize_Kd_range | [0.9, 1.1] |
| domain_rand.randomize_motor_torque | true |
| domain_rand.randomize_motor_torque_range | [0.9, 1.1] |
| domain_rand.randomize_default_dof_pos | true |
| domain_rand.randomize_default_dof_pos_range | [-0.05, 0.05] |
| domain_rand.randomize_action_delay | true |
| domain_rand.delay_ms_range | [0, 5] |
| normalization.obs_scales.lin_vel | 3.0 |
| normalization.obs_scales.ang_vel | 0.25 |
| normalization.obs_scales.dof_pos | 1.0 |
| normalization.obs_scales.dof_vel | 0.05 |
| normalization.obs_scales.dof_acc | 0.0025 |
| normalization.obs_scales.height_measurements | 5.0 |
| normalization.obs_scales.torque | 0.05 |
| normalization.clip_observations | 100.0 |
| normalization.clip_actions | 100.0 |
| noise.add_noise | true |
| noise.noise_level | 1.0 |
| noise.noise_scales.dof_pos | 0.02 |
| noise.noise_scales.dof_vel | 1.5 |
| noise.noise_scales.lin_vel | 0.1 |
| noise.noise_scales.ang_vel | 0.2 |
| noise.noise_scales.gravity | 0.05 |
| noise.noise_scales.height_measurements | 0.1 |
| viewer.ref_env | 0 |
| viewer.pos | [0, -2, 1] |
| viewer.lookat | [0, 0, 0] |
| sim.dt | 0.005 |
| sim.substeps | 1 |
| sim.gravity | [0.0, 0.0, -9.81] |
| sim.up_axis | 1 |
| sim.physx.num_threads | 10 |
| sim.physx.solver_type | 1 |
| sim.physx.num_position_iterations | 4 |
| sim.physx.num_velocity_iterations | 0 |
| sim.physx.contact_offset | 0.01 |
| sim.physx.rest_offset | 0.0 |
| sim.physx.bounce_threshold_velocity | 0.5 |
| sim.physx.max_depenetration_velocity | 1.0 |
| sim.physx.max_gpu_contact_pairs | 8388608 |
| sim.physx.default_buffer_size_multiplier | 5 |
| sim.physx.contact_collection | 2 |


</details>


<details markdown="1"><summary>完整PPO及历史估计器</summary>


| 字段 | 原值 |
|---|---|
| seed | 1 |
| runner_class_name | OnPolicyRunner |
| policy.init_noise_std | 0.5 |
| policy.actor_hidden_dims | [128, 64, 32] |
| policy.critic_hidden_dims | [256, 128, 64] |
| policy.activation | elu |
| policy.num_encoder_obs | 125 |
| policy.latent_dim | 3 |
| policy.encoder_hidden_dims | [128, 64] |
| algorithm.value_loss_coef | 1.0 |
| algorithm.use_clipped_value_loss | true |
| algorithm.clip_param | 0.2 |
| algorithm.entropy_coef | 0.01 |
| algorithm.num_learning_epochs | 5 |
| algorithm.num_mini_batches | 4 |
| algorithm.learning_rate | 0.001 |
| algorithm.schedule | adaptive |
| algorithm.gamma | 0.99 |
| algorithm.lam | 0.95 |
| algorithm.desired_kl | 0.005 |
| algorithm.max_grad_norm | 1.0 |
| algorithm.extra_learning_rate | 0.001 |
| runner.policy_class_name | ActorCriticSequence |
| runner.algorithm_class_name | PPO |
| runner.num_steps_per_env | 48 |
| runner.max_iterations | 50000 |
| runner.save_interval | 100 |
| runner.experiment_name | wheel_legged |
| runner.run_name |  |
| runner.resume | false |
| runner.load_run | -1 |
| runner.checkpoint | -1 |
| runner.resume_path | null（未配置/待填） |


</details>

地形实现：[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/utils/terrain.py>)。历史目录未保存同目录terrain.py，不保证历史网格与现有生成器相同。

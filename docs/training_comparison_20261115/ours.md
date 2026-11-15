# 附录A：我们的全部阶段和有效权重

[返回总览](README.md)

base→stage覆盖后的正常状态权重；mask、事件追加和地形分区另外列出。null不代填，0表示关闭。

## config\policies\p1\policy_meta.yaml

[配置来源](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/config/policies/p1/policy_meta.yaml>)

| 字段 | 原值 |
|---|---|
| name | p1_locomotion |
| obs_version | 2 |
| hidden_dims | [256, 128, 64] |
| activation | elu |
| observation_scales.command | [1.0, 1.0, 1.0] |
| observation_scales.height | 5.0 |
| observation_scales.angular_velocity | 0.5 |
| observation_scales.gravity | 1.0 |
| observation_scales.joint_position | 1.0 |
| observation_scales.joint_velocity | 0.1 |
| action_scales | [0.5, 0.5, 10.0, 0.5, 0.5, 10.0] |
| action_clip | null（未配置/待填） |
| kp | [null, null, null, null, null, null] |
| kd | [null, null, null, null, null, null] |
| torque_limit_nm | [null, null, null, null, null, null] |
| history_estimator.frames | 0 |
| history_estimator.hidden_dims | [128, 64] |
| policy_family | p1 |
| mode_semantics | ["normal", "stair", "zero", "recover", "zero", "zero", "zero"] |
| guide_version | 2.2 |



<details markdown="1"><summary>完整training：命令/奖励参数/PPO/课程/评测/扰动</summary>


| 字段 | 原值 |
|---|---|
| seed | 42 |
| num_envs | 4096 |
| rollout_steps | 48 |
| max_iterations | 20000 |
| save_interval | 500 |
| episode_length_s | 20.0 |
| init_noise_std | 1.0 |
| reward_clip | 2.5 |
| history_estimator.learning_rate | 0.001 |
| history_estimator.velocity_loss_coef | 1.0 |
| history_estimator.contact_loss_coef | 1.0 |
| ppo.value_loss_coef | 2.0 |
| ppo.use_clipped_value_loss | true |
| ppo.clip_param | 0.2 |
| ppo.entropy_coef | 0.005 |
| ppo.num_learning_epochs | 5 |
| ppo.num_mini_batches | 4 |
| ppo.learning_rate | 0.0001 |
| ppo.schedule | adaptive |
| ppo.gamma | 0.995 |
| ppo.lam | 0.95 |
| ppo.desired_kl | 0.01 |
| ppo.max_grad_norm | 1.0 |
| commands.segment_duration_s | [3.0, 15.0] |
| commands.height_duration_s | [2.0, 6.0] |
| commands.vx_range_m_s | null（未配置/待填） |
| commands.wz_range_rad_s | null（未配置/待填） |
| commands.height_range_m | null（未配置/待填） |
| commands.linear_slew_m_s2 | 2.0 |
| commands.angular_slew_rad_s2 | 10.0 |
| commands.height_slew_m_s | null（未配置/待填） |
| commands.segment_probabilities | [0.1, 0.25, 0.15, 0.25, 0.1, 0.15] |
| commands.dash_range_m_s | null（未配置/待填） |
| commands.combined_wz_limit_rad_s | null（未配置/待填） |
| reward_parameters.linear_sigma | 0.5 |
| reward_parameters.angular_sigma | 0.25 |
| reward_parameters.height_sigma | 0.001 |
| reward_parameters.height_wide_sigma | 0.025 |
| reward_parameters.height_gate_full_error_m | 0.05 |
| reward_parameters.height_gate_zero_error_m | 0.1 |
| reward_parameters.roll_sigma | 0.01 |
| reward_parameters.pitch_sigma | 0.02 |
| reward_parameters.pitch_velocity_amplitude | 1.0 |
| reward_parameters.pitch_velocity_sigma | 4.0 |
| reward_parameters.pitch_velocity_offset | 3.0 |
| reward_parameters.fork_deadzone_m | 0.05 |
| reward_parameters.stand_deadzone | 0.1 |
| reward_parameters.contact_force_n | 3.0 |
| reward_parameters.spin_velocity_sigma | 0.25 |
| reward_parameters.spin_heading_sigma | 0.025 |
| reward_parameters.air_wheel_torque_sigma | 1.5 |
| reward_parameters.fork_square_scale | 5.0 |
| reward_parameters.leg_length_symmetry_scale | 10.0 |
| rewards.track_lin_vel | 1.0 |
| rewards.lin_vel_error | -1.0 |
| rewards.track_ang_vel | 1.0 |
| rewards.ang_vel_error | -1.0 |
| rewards.track_height | 1.0 |
| rewards.track_height_wide | 1.0 |
| rewards.height_error | -1.0 |
| rewards.flat_roll | 1.0 |
| rewards.flat_pitch | 1.0 |
| rewards.roll_penalty | -2.0 |
| rewards.pitch_penalty | -3.0 |
| rewards.vertical_velocity | -4.0 |
| rewards.angular_xy | -0.2 |
| rewards.no_fork | -1.0 |
| rewards.no_fork_square | -1.0 |
| rewards.undesired_contact | -2.0 |
| rewards.stand_still | -2.0 |
| rewards.joint_torque | -0.0001 |
| rewards.wheel_power | -0.0001 |
| rewards.action_rate | -0.01 |
| rewards.leg_joint_vel | -0.005 |
| rewards.leg_joint_acc | -2e-06 |
| rewards.wheel_vel | -1e-05 |
| rewards.action_smoothness_leg | -0.05 |
| rewards.action_smoothness_wheel | -0.01 |
| rewards.termination | -4.0 |
| rewards.leg_symmetry | 0.0 |
| evaluation.flat_suite.height_samples | 3 |
| evaluation.flat_suite.speed_fractions | [0.25, 0.5, 1.0] |
| evaluation.flat_suite.combined_fractions | [0.5, 1.0] |
| evaluation.flat_suite.seeds | [123, 456] |
| evaluation.flat_suite.startup_s | 2.0 |
| evaluation.flat_suite.hold_s | 20.0 |
| evaluation.flat_suite.stand_window_s | 10.0 |
| evaluation.flat_suite.transition_settling_s | 2.0 |
| evaluation.flat_suite.stable_hold_s | 0.5 |
| evaluation.flat_suite.recovery_deadline_s | 3.0 |
| evaluation.flat_suite.push_after_s | 4.0 |
| evaluation.flat_suite.push_velocity_m_s | 0.25 |
| evaluation.flat_suite.delay_command_fraction | 0.5 |
| evaluation.flat_suite.delay_pairs_steps | [[3, 3], [8, 5]] |
| evaluation.flat_suite.trace_stride | 5 |
| evaluation.flat_suite.acceptance.stand_drift_m | 0.2 |
| evaluation.flat_suite.acceptance.tilt_p95_rad | 0.17453292519943295 |
| evaluation.flat_suite.acceptance.contact_fraction | 0.01 |
| evaluation.observation_delay_steps | null（未配置/待填） |
| evaluation.action_delay_steps | null（未配置/待填） |
| evaluation.duration_s | 10.0 |
| evaluation.settling_s | 1.0 |
| evaluation.episodes_per_case | 16 |
| evaluation.seed | 123 |
| evaluation.height_m | null（未配置/待填） |
| evaluation.vx_values_m_s | null（未配置/待填） |
| evaluation.wz_values_rad_s | null（未配置/待填） |
| evaluation.combined_commands | null（未配置/待填） |
| disturbance.baseline_evaluation_passed | true |
| disturbance.ramp_iterations | 3000 |
| disturbance.final_push_velocity_m_s | 1.25 |
| disturbance.collision_interval_s | [8.0, 15.0] |
| disturbance.collision_duration_s | 0.1 |
| disturbance.collision_force_range_n | [100.0, 300.0] |
| disturbance.lateral_probability | 0.8 |
| disturbance.phase2_start_iteration | 4000 |
| air_rewards.joint_limit | -10.0 |
| air_rewards.wheel_center | 10.0 |
| air_rewards.wheel_center_sigma | null（未配置/待填） |
| air_rewards.wheel_torque | 20.0 |
| air_rewards.wheel_torque_sigma | 1.5 |
| air_rewards.wheel_speed_alignment | -10.0 |
| command_curriculum.min_completed_episodes | 4096 |
| command_curriculum.initial_fraction | 0.25 |
| command_curriculum.increment | 0.05 |
| command_curriculum.success_fraction | 0.75 |
| command_curriculum.velocity_error_threshold_m_s | null（未配置/待填） |
| command_curriculum.yaw_error_threshold_rad_s | null（未配置/待填） |
| command_curriculum.relative_error | 0.25 |
| command_curriculum.height_error_threshold_m | null（未配置/待填） |
| height_wide_anneal.final_weight | 0.5 |
| height_wide_anneal.start_iteration | 2000 |
| height_wide_anneal.ramp_iterations | 500 |
| transition_reset.probability | 0.0 |
| transition_reset.states_npz | null（未配置/待填） |


</details>


### flat


| 奖励项 | 合并后权重 | 生效说明 |
|---|---|---|
| track_lin_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| lin_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_ang_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| ang_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_height | 1.0 | 需再结合dt、状态mask、事件定义 |
| track_height_wide | 1.0 | 需再结合dt、状态mask、事件定义 |
| height_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| flat_roll | 1.0 | 需再结合dt、状态mask、事件定义 |
| flat_pitch | 1.0 | 需再结合dt、状态mask、事件定义 |
| roll_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| pitch_penalty | -3.0 | 需再结合dt、状态mask、事件定义 |
| vertical_velocity | -4.0 | 需再结合dt、状态mask、事件定义 |
| angular_xy | -0.2 | 需再结合dt、状态mask、事件定义 |
| no_fork | -1.0 | 需再结合dt、状态mask、事件定义 |
| no_fork_square | -1.0 | 需再结合dt、状态mask、事件定义 |
| undesired_contact | -2.0 | 需再结合dt、状态mask、事件定义 |
| stand_still | -2.0 | 需再结合dt、状态mask、事件定义 |
| joint_torque | -0.0001 | 需再结合dt、状态mask、事件定义 |
| wheel_power | -0.0001 | 需再结合dt、状态mask、事件定义 |
| action_rate | -0.01 | 需再结合dt、状态mask、事件定义 |
| leg_joint_vel | -0.005 | 需再结合dt、状态mask、事件定义 |
| leg_joint_acc | -2e-06 | 需再结合dt、状态mask、事件定义 |
| wheel_vel | -1e-05 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_leg | -0.05 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_wheel | -0.01 | 需再结合dt、状态mask、事件定义 |
| termination | -4.0 | 需再结合dt、状态mask、事件定义 |
| leg_symmetry | 0.0 | 关闭 |



<details markdown="1"><summary>完整阶段设置：含事件/额外奖励、地形和状态阈值</summary>


| 字段 | 原值 |
|---|---|
| air_reset_probability | 0.0 |
| recovery_probability | 0.0 |
| disturbance_phase | 1 |
| reward_overrides | {} |


</details>


### landing


| 奖励项 | 合并后权重 | 生效说明 |
|---|---|---|
| track_lin_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| lin_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_ang_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| ang_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_height | 1.0 | 需再结合dt、状态mask、事件定义 |
| track_height_wide | 1.5 | 需再结合dt、状态mask、事件定义 |
| height_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| flat_roll | 1.0 | 需再结合dt、状态mask、事件定义 |
| flat_pitch | 1.0 | 需再结合dt、状态mask、事件定义 |
| roll_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| pitch_penalty | -3.0 | 需再结合dt、状态mask、事件定义 |
| vertical_velocity | -4.0 | 需再结合dt、状态mask、事件定义 |
| angular_xy | -0.2 | 需再结合dt、状态mask、事件定义 |
| no_fork | -1.0 | 需再结合dt、状态mask、事件定义 |
| no_fork_square | -1.0 | 需再结合dt、状态mask、事件定义 |
| undesired_contact | -2.0 | 需再结合dt、状态mask、事件定义 |
| stand_still | -2.0 | 需再结合dt、状态mask、事件定义 |
| joint_torque | -0.0001 | 需再结合dt、状态mask、事件定义 |
| wheel_power | -0.0001 | 需再结合dt、状态mask、事件定义 |
| action_rate | -0.002 | 需再结合dt、状态mask、事件定义 |
| leg_joint_vel | -0.001 | 需再结合dt、状态mask、事件定义 |
| leg_joint_acc | -4e-07 | 需再结合dt、状态mask、事件定义 |
| wheel_vel | -2e-06 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_leg | -0.01 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_wheel | -0.002 | 需再结合dt、状态mask、事件定义 |
| termination | -4.0 | 需再结合dt、状态mask、事件定义 |
| leg_symmetry | 0.0 | 关闭 |



<details markdown="1"><summary>完整阶段设置：含事件/额外奖励、地形和状态阈值</summary>


| 字段 | 原值 |
|---|---|
| landing_reward.progress_budget | 0.75 |
| landing_reward.success_bonus | 1.5 |
| landing_reward.failure_cost | 1.0 |
| landing_reward.contact_force_n | 3.0 |
| landing_reward.support_force_n | 20.0 |
| landing_reward.contact_timeout_s | 2.0 |
| landing_reward.settle_support_s | 0.1 |
| landing_reward.cushion_max_s | 0.5 |
| landing_reward.window_s | 3.0 |
| landing_reward.stable_s | 0.5 |
| landing_reward.tilt_rad | 0.17453292519943295 |
| landing_reward.angular_xy_rad_s | 0.5 |
| landing_reward.vertical_velocity_m_s | 0.2 |
| landing_reward.height_error_m | 0.05 |
| landing_reward.wheel_center_weight | 4.0 |
| landing_reward.wheel_center_sigma | 0.02 |
| landing_reward.wheel_speed_weight | 6.0 |
| landing_reward.wheel_speed_sigma | 1.0 |
| landing_reward.contact_multiplier | 8.0 |
| landing_reward.guide_body_regex | .*_guide_link |
| landing_reward.guide_hard_speed_m_s | 1.0 |
| landing_reward.guide_speed_cost | 0.5 |
| landing_reward.leg_extension_weight | 3.0 |
| landing_reward.leg_extension_target_m | null（未配置/待填） |
| landing_reward.leg_extension_scale_m | 0.1 |
| landing_diagnostics.first_contact_force_n | 3.0 |
| landing_diagnostics.support_force_n | 20.0 |
| landing_diagnostics.first_contact_timeout_s | 2.0 |
| landing_diagnostics.observation_window_s | 3.0 |
| landing_diagnostics.stable_duration_s | 0.5 |
| landing_diagnostics.touchdown_difference_s | 0.05 |
| landing_diagnostics.tilt_rad | 0.17453292519943295 |
| landing_diagnostics.angular_xy_rad_s | 0.5 |
| landing_diagnostics.vertical_velocity_m_s | 0.2 |
| landing_diagnostics.height_error_m | 0.05 |
| air_reset_probability | 0.4 |
| air_height_offset_m | [0.12, 0.42] |
| air_vx_range_m_s | [-2.5, 2.5] |
| air_tilt_rad | [0.1, 0.2] |
| air_vy_range_m_s | [-0.5, 0.5] |
| air_angular_velocity_rad_s | [0.05, 0.1, 0.5] |
| air_leg_length_range_m | null（未配置/待填） |
| air_leg_angle_range_rad | null（未配置/待填） |
| air_command_limit_s | 3.0 |
| air_command_vx_limit_m_s | 2.5 |
| air_command_wz_limit_rad_s | 1.5707963267948966 |
| air_vx_command_probability | 0.8 |
| air_vx_command_noise_m_s | 0.3 |
| air_height_curriculum.levels_m | [0.2, 0.24, 0.28, 0.32, 0.36, 0.42] |
| air_height_curriculum.min_events | 1024 |
| air_height_curriculum.success_rate | 0.8 |
| command_curriculum_landing_gate.min_events | 256 |
| command_curriculum_landing_gate.success_rate | 0.75 |
| recovery_probability | 0.0 |
| disturbance_phase | 1 |
| reward_overrides.track_height_wide | 1.5 |
| reward_overrides.action_rate | -0.002 |
| reward_overrides.action_smoothness_leg | -0.01 |
| reward_overrides.action_smoothness_wheel | -0.002 |
| reward_overrides.leg_joint_vel | -0.001 |
| reward_overrides.leg_joint_acc | -4e-07 |
| reward_overrides.wheel_vel | -2e-06 |


</details>


### stairs


| 奖励项 | 合并后权重 | 生效说明 |
|---|---|---|
| track_lin_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| lin_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_ang_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| ang_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_height | 1.0 | 需再结合dt、状态mask、事件定义 |
| track_height_wide | 1.0 | 需再结合dt、状态mask、事件定义 |
| height_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| flat_roll | 1.0 | 需再结合dt、状态mask、事件定义 |
| flat_pitch | 1.0 | 需再结合dt、状态mask、事件定义 |
| roll_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| pitch_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| vertical_velocity | -0.5 | 需再结合dt、状态mask、事件定义 |
| angular_xy | -0.05 | 需再结合dt、状态mask、事件定义 |
| no_fork | -1.0 | 需再结合dt、状态mask、事件定义 |
| no_fork_square | -1.0 | 需再结合dt、状态mask、事件定义 |
| undesired_contact | -2.0 | 需再结合dt、状态mask、事件定义 |
| stand_still | -2.0 | 需再结合dt、状态mask、事件定义 |
| joint_torque | -1e-05 | 需再结合dt、状态mask、事件定义 |
| wheel_power | -1e-05 | 需再结合dt、状态mask、事件定义 |
| action_rate | -0.002 | 需再结合dt、状态mask、事件定义 |
| leg_joint_vel | -0.001 | 需再结合dt、状态mask、事件定义 |
| leg_joint_acc | -4e-07 | 需再结合dt、状态mask、事件定义 |
| wheel_vel | -2e-06 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_leg | -0.01 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_wheel | -0.002 | 需再结合dt、状态mask、事件定义 |
| termination | -4.0 | 需再结合dt、状态mask、事件定义 |
| leg_symmetry | 0.0 | 关闭 |



| 项 | 台阶基值 | flat | grid | slope | rough |
|---|---|---|---|---|---|
| action_rate | -0.002 | -0.01 | -0.005 | -0.0075 | -0.006 |
| action_smoothness_leg | -0.01 | -0.05 | -0.025 | -0.0375 | -0.03 |
| action_smoothness_wheel | -0.002 | -0.01 | -0.005 | -0.0075 | -0.006 |
| ang_vel_error | -1.0 | -1.0 | -1.0 | -1.0 | -1.0 |
| angular_xy | -0.05 | -0.2 | -0.1 | -0.15 | -0.15 |
| flat_pitch | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| flat_roll | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| height_error | -1.0 | -1.0 | -1.0 | -1.0 | -1.0 |
| joint_torque | -1e-05 | -0.0001 | -3e-05 | -5e-05 | -5e-05 |
| leg_joint_acc | -4e-07 | -2e-06 | -1e-06 | -1.5e-06 | -1.2e-06 |
| leg_joint_vel | -0.001 | -0.005 | -0.0025 | -0.00375 | -0.003 |
| leg_symmetry | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| lin_vel_error | -1.0 | -1.0 | -1.0 | -1.0 | -1.0 |
| no_fork | -1.0 | -1.0 | -1.0 | -1.0 | -1.0 |
| no_fork_square | -1.0 | -1.0 | -1.0 | -1.0 | -1.0 |
| pitch_penalty | -2.0 | -3.0 | -2.5 | -2.25 | -2.75 |
| roll_penalty | -2.0 | -2.0 | -2.0 | -2.0 | -2.0 |
| stand_still | -2.0 | -2.0 | -2.0 | -2.0 | -2.0 |
| termination | -4.0 | -4.0 | -4.0 | -4.0 | -4.0 |
| track_ang_vel | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| track_height | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| track_height_wide | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| track_lin_vel | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| undesired_contact | -2.0 | -2.0 | -2.0 | -2.0 | -2.0 |
| vertical_velocity | -0.5 | -4.0 | -1 | -1.5 | -2 |
| wheel_power | -1e-05 | -0.0001 | -3e-05 | -5e-05 | -5e-05 |
| wheel_vel | -2e-06 | -1e-05 | -5e-06 | -7.5e-06 | -6e-06 |



| 地形 | 占比 | 模式 | 最低档vx | 最终vx | wz范围配置 | 高度 |
|---|---|---|---|---|---|---|
| flat | 0.3 | motion | null（未配置/待填） | null（未配置/待填） | [-5.0, 5.0] | null（未配置/待填） |
| up_one | 0.1 | traverse | null（未配置/待填） | null（未配置/待填） | [-0.1, 0.1] | null（未配置/待填） |
| down_one | 0.1 | traverse | null（未配置/待填） | null（未配置/待填） | [-0.1, 0.1] | null（未配置/待填） |
| mixed_one | 0.05 | traverse | null（未配置/待填） | null（未配置/待填） | [-0.1, 0.1] | null（未配置/待填） |
| mixed_fast | 0.05 | traverse | null（未配置/待填） | null（未配置/待填） | [-0.1, 0.1] | null（未配置/待填） |
| up_two | 0.05 | traverse | null（未配置/待填） | null（未配置/待填） | [-0.1, 0.1] | null（未配置/待填） |
| down_two | 0.05 | traverse | null（未配置/待填） | null（未配置/待填） | [-0.1, 0.1] | null（未配置/待填） |
| mixed_two | 0.1 | traverse | null（未配置/待填） | null（未配置/待填） | [-0.1, 0.1] | null（未配置/待填） |
| grid | 0.1 | free | null（未配置/待填） | null（未配置/待填） | [0.5, 2.0] | null（未配置/待填） |
| slope | 0.05 | traverse | null（未配置/待填） | null（未配置/待填） | [-0.1, 0.1] | null（未配置/待填） |
| rough | 0.05 | free | null（未配置/待填） | null（未配置/待填） | [0.5, 2.0] | null（未配置/待填） |



<details markdown="1"><summary>完整阶段设置：含事件/额外奖励、地形和状态阈值</summary>


| 字段 | 原值 |
|---|---|
| air_reset_probability | 0.0 |
| air_height_offset_m | [0.12, 0.42] |
| air_vx_range_m_s | [-2.5, 2.5] |
| air_tilt_rad | [0.1, 0.2] |
| air_vy_range_m_s | [-0.5, 0.5] |
| air_angular_velocity_rad_s | [0.05, 0.1, 0.5] |
| air_leg_length_range_m | null（未配置/待填） |
| air_leg_angle_range_rad | null（未配置/待填） |
| air_command_limit_s | 3.0 |
| air_command_vx_limit_m_s | 2.5 |
| air_command_wz_limit_rad_s | 1.5707963267948966 |
| recovery_probability | 0.0 |
| terrain.tile_size_m | [8.0, 8.0] |
| terrain.rows | 8 |
| terrain.columns | 20 |
| terrain.step_height_range_m | null（未配置/待填） |
| terrain.step_width_m | null（未配置/待填） |
| terrain.slope_angle_range_rad | [0.0, 0.4363323129985824] |
| terrain.rough_noise_range_m | [0.0, 0.03] |
| terrain.rough_noise_step_m | 0.005 |
| terrain.rough_downsampled_scale_m | 0.2 |
| terrain.heightfield_border_width_m | 1.0 |
| terrain.border_width_m | 5.0 |
| terrain.boundary_margin_m | 0.5 |
| terrain.spawn_x_m | 0.8 |
| terrain.entry_x_m | 2.4 |
| terrain.surface_x_range_m | [2.0, 6.2] |
| terrain.exit_x_m | 5.6 |
| terrain.finish_x_m | 6.6 |
| terrain.ground_thickness_m | 0.1 |
| terrain.seed | 42 |
| terrain.surface_resolution_m | 0.2 |
| terrain.grid.width_range_m | [0.08, 0.12] |
| terrain.grid.height_range_m | [0.025, 0.045] |
| terrain.grid.spacing_range_m | [0.55, 0.7] |
| terrain.grid.half_span_m | 3.8 |
| terrain.profiles.flat.proportion | 0.3 |
| terrain.profiles.flat.kind | flat |
| terrain.profiles.flat.step_count | 0 |
| terrain.profiles.flat.speed_range_m_s | null（未配置/待填） |
| terrain.profiles.flat.command_mode | motion |
| terrain.profiles.flat.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.flat.yaw_range_rad_s | [-5.0, 5.0] |
| terrain.profiles.flat.height_range_m | null（未配置/待填） |
| terrain.profiles.flat.start_speed_range_m_s | null（未配置/待填） |
| terrain.profiles.up_one.proportion | 0.1 |
| terrain.profiles.up_one.kind | up |
| terrain.profiles.up_one.step_count | 1 |
| terrain.profiles.up_one.speed_range_m_s | null（未配置/待填） |
| terrain.profiles.up_one.command_mode | traverse |
| terrain.profiles.up_one.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.up_one.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.up_one.height_range_m | null（未配置/待填） |
| terrain.profiles.up_one.start_speed_range_m_s | null（未配置/待填） |
| terrain.profiles.down_one.proportion | 0.1 |
| terrain.profiles.down_one.kind | down |
| terrain.profiles.down_one.step_count | 1 |
| terrain.profiles.down_one.speed_range_m_s | null（未配置/待填） |
| terrain.profiles.down_one.command_mode | traverse |
| terrain.profiles.down_one.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.down_one.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.down_one.height_range_m | null（未配置/待填） |
| terrain.profiles.down_one.start_speed_range_m_s | null（未配置/待填） |
| terrain.profiles.mixed_one.proportion | 0.05 |
| terrain.profiles.mixed_one.kind | mixed |
| terrain.profiles.mixed_one.step_count | 1 |
| terrain.profiles.mixed_one.speed_range_m_s | null（未配置/待填） |
| terrain.profiles.mixed_one.command_mode | traverse |
| terrain.profiles.mixed_one.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.mixed_one.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.mixed_one.height_range_m | null（未配置/待填） |
| terrain.profiles.mixed_one.start_speed_range_m_s | null（未配置/待填） |
| terrain.profiles.mixed_fast.proportion | 0.05 |
| terrain.profiles.mixed_fast.kind | mixed |
| terrain.profiles.mixed_fast.step_count | 1 |
| terrain.profiles.mixed_fast.speed_range_m_s | null（未配置/待填） |
| terrain.profiles.mixed_fast.command_mode | traverse |
| terrain.profiles.mixed_fast.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.mixed_fast.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.mixed_fast.height_range_m | null（未配置/待填） |
| terrain.profiles.mixed_fast.start_speed_range_m_s | null（未配置/待填） |
| terrain.profiles.up_two.proportion | 0.05 |
| terrain.profiles.up_two.kind | up |
| terrain.profiles.up_two.step_count | 2 |
| terrain.profiles.up_two.speed_range_m_s | null（未配置/待填） |
| terrain.profiles.up_two.command_mode | traverse |
| terrain.profiles.up_two.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.up_two.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.up_two.height_range_m | null（未配置/待填） |
| terrain.profiles.up_two.start_speed_range_m_s | null（未配置/待填） |
| terrain.profiles.down_two.proportion | 0.05 |
| terrain.profiles.down_two.kind | down |
| terrain.profiles.down_two.step_count | 2 |
| terrain.profiles.down_two.speed_range_m_s | null（未配置/待填） |
| terrain.profiles.down_two.command_mode | traverse |
| terrain.profiles.down_two.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.down_two.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.down_two.height_range_m | null（未配置/待填） |
| terrain.profiles.down_two.start_speed_range_m_s | null（未配置/待填） |
| terrain.profiles.mixed_two.proportion | 0.1 |
| terrain.profiles.mixed_two.kind | mixed |
| terrain.profiles.mixed_two.step_count | 2 |
| terrain.profiles.mixed_two.speed_range_m_s | null（未配置/待填） |
| terrain.profiles.mixed_two.command_mode | traverse |
| terrain.profiles.mixed_two.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.mixed_two.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.mixed_two.height_range_m | null（未配置/待填） |
| terrain.profiles.mixed_two.start_speed_range_m_s | null（未配置/待填） |
| terrain.profiles.grid.proportion | 0.1 |
| terrain.profiles.grid.kind | grid |
| terrain.profiles.grid.step_count | 0 |
| terrain.profiles.grid.speed_range_m_s | null（未配置/待填） |
| terrain.profiles.grid.command_mode | free |
| terrain.profiles.grid.free_yaw_limit_range_rad_s | [0.5, 2.0] |
| terrain.profiles.grid.heading_yaw_limit_rad_s | 0.5 |
| terrain.profiles.grid.yaw_range_rad_s | [-0.3, 0.3] |
| terrain.profiles.grid.height_range_m | null（未配置/待填） |
| terrain.profiles.grid.start_speed_range_m_s | null（未配置/待填） |
| terrain.profiles.slope.proportion | 0.05 |
| terrain.profiles.slope.kind | slope |
| terrain.profiles.slope.step_count | 0 |
| terrain.profiles.slope.speed_range_m_s | null（未配置/待填） |
| terrain.profiles.slope.command_mode | traverse |
| terrain.profiles.slope.heading_yaw_limit_rad_s | 0.5 |
| terrain.profiles.slope.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.slope.height_range_m | null（未配置/待填） |
| terrain.profiles.slope.start_speed_range_m_s | null（未配置/待填） |
| terrain.profiles.rough.proportion | 0.05 |
| terrain.profiles.rough.kind | rough |
| terrain.profiles.rough.step_count | 0 |
| terrain.profiles.rough.speed_range_m_s | null（未配置/待填） |
| terrain.profiles.rough.command_mode | free |
| terrain.profiles.rough.free_yaw_limit_range_rad_s | [0.5, 2.0] |
| terrain.profiles.rough.heading_yaw_limit_rad_s | 0.5 |
| terrain.profiles.rough.yaw_range_rad_s | [-0.3, 0.3] |
| terrain.profiles.rough.height_range_m | null（未配置/待填） |
| terrain.profiles.rough.start_speed_range_m_s | null（未配置/待填） |
| terrain.rough_proportion | 0.05 |
| disturbance_phase | 2 |
| reward_overrides.track_height_wide | 1.0 |
| reward_overrides.action_rate | -0.002 |
| reward_overrides.action_smoothness_leg | -0.01 |
| reward_overrides.action_smoothness_wheel | -0.002 |
| reward_overrides.leg_joint_vel | -0.001 |
| reward_overrides.leg_joint_acc | -4e-07 |
| reward_overrides.wheel_vel | -2e-06 |
| reward_overrides.pitch_penalty | -2.0 |
| reward_overrides.vertical_velocity | -0.5 |
| reward_overrides.angular_xy | -0.05 |
| reward_overrides.joint_torque | -1e-05 |
| reward_overrides.wheel_power | -1e-05 |
| step_height_margin_m | 0.01 |
| step_height_clearance_range_m | null（未配置/待填） |
| step_height_hold_s | 0.3 |
| course.episode_length_s | 30.0 |
| course.flat_curriculum.levels | [[0.2, 0.2, 0.45], [0.2, 0.2, 0.7], [0.35, 0.35, 0.7], [0.35, 0.35, 1.0], [0.5, 0.5, 1.0], [0.7, 0.7, 1.0], [0.85, 0.85, 1.0], [1.0, 1.0, 1.0]] |
| course.flat_curriculum.min_completed_episodes | 4096 |
| course.flat_curriculum.promote_rate | 0.6 |
| course.flat_curriculum.demote_rate | 0.2 |
| course.flat_curriculum.error_thresholds | [0.15, 0.25, 0.06] |
| course.flat_curriculum.relative_error | 0.25 |
| course.initial_speed_fraction | 0.4 |
| course.minimum_speed_fraction | 0.3 |
| course.speed_increment | 0.05 |
| course.speed_window_episodes | 256 |
| course.speed_promote_rate | 0.6 |
| course.speed_demote_rate | 0.3 |
| course.tracking_sigma | 0.5 |
| course.tracking_promote | 0.6 |
| course.tracking_demote | 0.4 |
| course.minimum_episode_s | 2.0 |
| course.tracking_warmup_s | 1.0 |
| course.reverse_probability | 0.25 |
| course.yaw_jitter_rad | 0.05 |
| course.heading_kp | 5.0 |
| course.segment_duration_s | [3.0, 7.0] |
| course.height_duration_s | [3.0, 7.0] |
| course.edge_clearance_m | 0.15 |
| course.finish_hold_s | 0.4 |
| course.finish_tilt_rad | 0.25 |
| course.finish_angular_rad_s | 0.5 |
| course.finish_speed_m_s | 0.15 |
| course.scan_resolution_m | 0.1 |
| course.scan_half_length_m | 1.0 |
| course.scan_half_width_m | 0.6 |
| course.scan_lane_half_width_m | 0.15 |
| course.scan_min_rays | 2 |
| course.edge_height_m | 0.04 |
| course.edge_gradient_excess_m | 0.025 |
| course.detection_distance_m | 0.6 |
| course.trigger_distance_m | 0.5 |
| course.detection_hold_s | 0.15 |
| course.contact_force_n | 20.0 |
| course.guide_body_regex | .*_guide_link |
| course.guide_contact_scale | 0.5 |
| course.min_flight_s | 0.02 |
| course.min_drop_m | 0.04 |
| course.impact_free_speed_m_s | 0.3 |
| course.impact_speed_scale_m_s | 1.0 |
| course.impact_clip | 4.0 |
| course.cushion_s | 0.15 |
| course.impact_weight | -0.5 |
| course.air_wheel_speed_weight | 2.0 |
| course.air_wheel_speed_sigma | 1.0 |
| course.yaw_deadzone_rad_s | 0.02 |
| course.heading_probability | 0.5 |
| course.traversal_hold_s | 0.15 |
| course.free_segment_probabilities | [0.15, 0.35, 0.2, 0.3] |
| course.free_surface_min_s | 3.0 |
| course.free_tracking_error_floor | [0.15, 0.3] |
| course.free_tracking_relative_error | 0.35 |
| course.free_tracking_promote | 0.5 |
| course.free_tracking_demote | 0.25 |
| course.motion_segment_probabilities | [0.25, 0.25, 0.25, 0.25] |
| course.small_turn_probability | 0.5 |
| course.small_turn_range_rad_s | [0.2, 1.0] |
| course.traversal_tilt_rad | 0.45 |
| course.traversal_angular_rad_s | 1.5 |
| course.traversal_height_error_m | 0.08 |
| terrain_reward_overrides.grid.pitch_penalty | -2.5 |
| terrain_reward_overrides.grid.angular_xy | -0.1 |
| terrain_reward_overrides.grid.vertical_velocity | -1 |
| terrain_reward_overrides.grid.action_rate | -0.005 |
| terrain_reward_overrides.grid.action_smoothness_leg | -0.025 |
| terrain_reward_overrides.grid.action_smoothness_wheel | -0.005 |
| terrain_reward_overrides.grid.leg_joint_vel | -0.0025 |
| terrain_reward_overrides.grid.leg_joint_acc | -1e-06 |
| terrain_reward_overrides.grid.wheel_vel | -5e-06 |
| terrain_reward_overrides.grid.joint_torque | -3e-05 |
| terrain_reward_overrides.grid.wheel_power | -3e-05 |
| terrain_reward_overrides.slope.pitch_penalty | -2.25 |
| terrain_reward_overrides.slope.angular_xy | -0.15 |
| terrain_reward_overrides.slope.vertical_velocity | -1.5 |
| terrain_reward_overrides.slope.action_rate | -0.0075 |
| terrain_reward_overrides.slope.action_smoothness_leg | -0.0375 |
| terrain_reward_overrides.slope.action_smoothness_wheel | -0.0075 |
| terrain_reward_overrides.slope.leg_joint_vel | -0.00375 |
| terrain_reward_overrides.slope.leg_joint_acc | -1.5e-06 |
| terrain_reward_overrides.slope.wheel_vel | -7.5e-06 |
| terrain_reward_overrides.slope.joint_torque | -5e-05 |
| terrain_reward_overrides.slope.wheel_power | -5e-05 |
| terrain_reward_overrides.rough.pitch_penalty | -2.75 |
| terrain_reward_overrides.rough.angular_xy | -0.15 |
| terrain_reward_overrides.rough.vertical_velocity | -2 |
| terrain_reward_overrides.rough.action_rate | -0.006 |
| terrain_reward_overrides.rough.action_smoothness_leg | -0.03 |
| terrain_reward_overrides.rough.action_smoothness_wheel | -0.006 |
| terrain_reward_overrides.rough.leg_joint_vel | -0.003 |
| terrain_reward_overrides.rough.leg_joint_acc | -1.2e-06 |
| terrain_reward_overrides.rough.wheel_vel | -6e-06 |
| terrain_reward_overrides.rough.joint_torque | -5e-05 |
| terrain_reward_overrides.rough.wheel_power | -5e-05 |
| spawn_xy_jitter_m.flat.x | [-1.0, 1.0] |
| spawn_xy_jitter_m.flat.y | [-1.0, 1.0] |
| spawn_xy_jitter_m.grid.x | [0.0, 0.3] |
| spawn_xy_jitter_m.grid.y | [-1.0, 1.0] |
| spawn_xy_jitter_m.rough.x | [0.0, 0.3] |
| spawn_xy_jitter_m.rough.y | [-1.0, 1.0] |
| spawn_footprint_margin_m | null（未配置/待填） |
| motion_reward_overrides.pitch_penalty | -3.0 |
| motion_reward_overrides.angular_xy | -0.2 |
| motion_reward_overrides.vertical_velocity | -4.0 |
| motion_reward_overrides.action_rate | -0.01 |
| motion_reward_overrides.action_smoothness_leg | -0.05 |
| motion_reward_overrides.action_smoothness_wheel | -0.01 |
| motion_reward_overrides.leg_joint_vel | -0.005 |
| motion_reward_overrides.leg_joint_acc | -2e-06 |
| motion_reward_overrides.wheel_vel | -1e-05 |
| motion_reward_overrides.joint_torque | -0.0001 |
| motion_reward_overrides.wheel_power | -0.0001 |


</details>


### recovery


| 奖励项 | 合并后权重 | 生效说明 |
|---|---|---|
| track_lin_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| lin_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_ang_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| ang_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_height | 1.0 | 需再结合dt、状态mask、事件定义 |
| track_height_wide | 1.0 | 需再结合dt、状态mask、事件定义 |
| height_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| flat_roll | 1.0 | 需再结合dt、状态mask、事件定义 |
| flat_pitch | 1.0 | 需再结合dt、状态mask、事件定义 |
| roll_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| pitch_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| vertical_velocity | -0.5 | 需再结合dt、状态mask、事件定义 |
| angular_xy | -0.05 | 需再结合dt、状态mask、事件定义 |
| no_fork | -1.0 | 需再结合dt、状态mask、事件定义 |
| no_fork_square | -1.0 | 需再结合dt、状态mask、事件定义 |
| undesired_contact | -2.0 | 需再结合dt、状态mask、事件定义 |
| stand_still | -2.0 | 需再结合dt、状态mask、事件定义 |
| joint_torque | -0.0001 | 需再结合dt、状态mask、事件定义 |
| wheel_power | -0.0001 | 需再结合dt、状态mask、事件定义 |
| action_rate | -0.002 | 需再结合dt、状态mask、事件定义 |
| leg_joint_vel | -0.001 | 需再结合dt、状态mask、事件定义 |
| leg_joint_acc | -4e-07 | 需再结合dt、状态mask、事件定义 |
| wheel_vel | -2e-06 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_leg | -0.01 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_wheel | -0.002 | 需再结合dt、状态mask、事件定义 |
| termination | -4.0 | 需再结合dt、状态mask、事件定义 |
| leg_symmetry | 0.0 | 关闭 |



<details markdown="1"><summary>完整阶段设置：含事件/额外奖励、地形和状态阈值</summary>


| 字段 | 原值 |
|---|---|
| air_reset_probability | 0.3 |
| air_height_offset_m | [0.12, 0.42] |
| air_vx_range_m_s | [-2.5, 2.5] |
| air_tilt_rad | [0.1, 0.2] |
| air_vy_range_m_s | [-0.5, 0.5] |
| air_angular_velocity_rad_s | [0.05, 0.1, 0.5] |
| air_leg_length_range_m | null（未配置/待填） |
| air_leg_angle_range_rad | null（未配置/待填） |
| air_command_limit_s | 3.0 |
| air_command_vx_limit_m_s | 2.5 |
| air_command_wz_limit_rad_s | 1.5707963267948966 |
| recovery_probability | 0.15 |
| recovery_root_height_m | null（未配置/待填） |
| recovery_forward_probability | 0.4 |
| recovery_leg_length_m | null（未配置/待填） |
| recovery_leg_height_m | null（未配置/待填） |
| recovery_forward_leg_height_m | null（未配置/待填） |
| rise_duration_s | 1.5 |
| zero_torque_s | 0.2 |
| recovery_timeout_s | 5.0 |
| disturbance_phase | 2 |
| reward_overrides.action_rate | -0.002 |
| reward_overrides.action_smoothness_leg | -0.01 |
| reward_overrides.action_smoothness_wheel | -0.002 |
| reward_overrides.leg_joint_vel | -0.001 |
| reward_overrides.leg_joint_acc | -4e-07 |
| reward_overrides.wheel_vel | -2e-06 |
| reward_overrides.pitch_penalty | -2.0 |
| reward_overrides.vertical_velocity | -0.5 |
| reward_overrides.angular_xy | -0.05 |
| terrain.tile_size_m | [8.0, 8.0] |
| terrain.rows | 8 |
| terrain.columns | 10 |
| terrain.flat_proportion | 0.3 |
| terrain.step_height_range_m | null（未配置/待填） |
| terrain.step_width_m | null（未配置/待填） |
| terrain.slope_proportion | 0.1 |
| terrain.bump_proportion | 0.1 |
| terrain.slope_angle_range_rad | [0.0, 0.4363323129985824] |
| terrain.bump_height_range_m | null（未配置/待填） |
| terrain.bump_spacing_m | null（未配置/待填） |
| terrain.bump_width_m | null（未配置/待填） |
| terrain.rough_proportion | 0.1 |
| terrain.rough_noise_range_m | [0.0, 0.03] |
| terrain.rough_noise_step_m | 0.005 |
| terrain.rough_downsampled_scale_m | 0.2 |
| terrain.heightfield_border_width_m | 1.0 |
| terrain.border_width_m | 5.0 |
| terrain.boundary_margin_m | 0.5 |
| stair_detection_distance_m | 0.5 |
| stair_detection_height_m | 0.05 |
| stair_false_positive | 0.1 |
| stair_false_negative | 0.1 |
| progress_weight | 1.0 |
| stuck_weight | -1.0 |
| impact_weight | -0.001 |
| stuck_window_s | 1.0 |
| stuck_distance_m | 0.05 |
| step_height_boost_m | 0.16 |
| step_height_hold_s | 2.0 |
| step_height_trigger_distance_m | 0.14 |


</details>


## config\policies\p2\policy_meta.yaml

[配置来源](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/config/policies/p2/policy_meta.yaml>)

| 字段 | 原值 |
|---|---|
| name | p2_spin |
| obs_version | 2 |
| hidden_dims | [256, 128, 64] |
| activation | elu |
| observation_scales.command | [1.0, 1.0, 1.0] |
| observation_scales.height | 5.0 |
| observation_scales.angular_velocity | 0.5 |
| observation_scales.gravity | 1.0 |
| observation_scales.joint_position | 1.0 |
| observation_scales.joint_velocity | 0.1 |
| action_scales | [0.5, 0.5, 10.0, 0.5, 0.5, 10.0] |
| action_clip | null（未配置/待填） |
| kp | [null, null, null, null, null, null] |
| kd | [null, null, null, null, null, null] |
| torque_limit_nm | [null, null, null, null, null, null] |
| history_estimator.frames | 0 |
| history_estimator.hidden_dims | [128, 64] |
| policy_family | p2 |
| mode_semantics | ["zero", "spin", "translation_speed_m_s", "sin_heading_reference", "cos_heading_reference", "sin_reference_relative_body", "cos_reference_relative_body"] |
| guide_version | 2.2 |



<details markdown="1"><summary>完整training：命令/奖励参数/PPO/课程/评测/扰动</summary>


| 字段 | 原值 |
|---|---|
| seed | 42 |
| num_envs | 4096 |
| rollout_steps | 48 |
| max_iterations | 20000 |
| save_interval | 500 |
| episode_length_s | 40.0 |
| init_noise_std | 1.0 |
| reward_clip | 2.5 |
| history_estimator.learning_rate | 0.001 |
| history_estimator.velocity_loss_coef | 1.0 |
| history_estimator.contact_loss_coef | 1.0 |
| ppo.value_loss_coef | 2.0 |
| ppo.use_clipped_value_loss | true |
| ppo.clip_param | 0.2 |
| ppo.entropy_coef | 0.005 |
| ppo.num_learning_epochs | 5 |
| ppo.num_mini_batches | 4 |
| ppo.learning_rate | 0.0001 |
| ppo.schedule | adaptive |
| ppo.gamma | 0.995 |
| ppo.lam | 0.95 |
| ppo.desired_kl | 0.01 |
| ppo.max_grad_norm | 1.0 |
| commands.segment_duration_s | [3.0, 15.0] |
| commands.height_duration_s | [2.0, 6.0] |
| commands.vx_range_m_s | null（未配置/待填） |
| commands.wz_range_rad_s | null（未配置/待填） |
| commands.height_range_m | null（未配置/待填） |
| commands.linear_slew_m_s2 | 2.0 |
| commands.angular_slew_rad_s2 | 10.0 |
| commands.height_slew_m_s | null（未配置/待填） |
| commands.segment_probabilities | [0.1, 0.25, 0.15, 0.25, 0.1, 0.15] |
| commands.dash_range_m_s | null（未配置/待填） |
| reward_parameters.linear_sigma | 0.5 |
| reward_parameters.angular_sigma | 0.25 |
| reward_parameters.height_sigma | 0.001 |
| reward_parameters.height_gate_full_error_m | 0.05 |
| reward_parameters.height_gate_zero_error_m | 0.1 |
| reward_parameters.roll_sigma | 0.01 |
| reward_parameters.pitch_sigma | 0.02 |
| reward_parameters.pitch_velocity_amplitude | 2.0 |
| reward_parameters.pitch_velocity_sigma | 3.0 |
| reward_parameters.pitch_velocity_offset | 2.0 |
| reward_parameters.fork_deadzone_m | 0.05 |
| reward_parameters.stand_deadzone | 0.1 |
| reward_parameters.contact_force_n | 3.0 |
| reward_parameters.spin_velocity_sigma | 0.25 |
| reward_parameters.spin_heading_sigma | 0.025 |
| reward_parameters.air_wheel_torque_sigma | 1.5 |
| reward_parameters.fork_square_scale | 5.0 |
| reward_parameters.leg_length_symmetry_scale | 10.0 |
| rewards.track_lin_vel | 0.0 |
| rewards.lin_vel_error | 0.0 |
| rewards.track_ang_vel | 1.0 |
| rewards.ang_vel_error | -1.0 |
| rewards.track_height | 1.0 |
| rewards.height_error | -1.0 |
| rewards.flat_roll | 1.0 |
| rewards.flat_pitch | 1.0 |
| rewards.roll_penalty | -2.0 |
| rewards.pitch_penalty | -2.0 |
| rewards.vertical_velocity | -0.5 |
| rewards.angular_xy | -0.05 |
| rewards.no_fork | -1.0 |
| rewards.no_fork_square | -1.0 |
| rewards.undesired_contact | -2.0 |
| rewards.stand_still | -1.0 |
| rewards.joint_torque | -1e-05 |
| rewards.wheel_power | -1e-05 |
| rewards.action_rate | -0.01 |
| rewards.termination | -4.0 |
| rewards.spin_velocity | 1.0 |
| rewards.spin_speed | 1.0 |
| rewards.spin_heading | 5.0 |
| rewards.spin_velocity_error | -0.2 |
| rewards.spin_speed_error | -0.2 |
| rewards.leg_symmetry | 0.0 |
| evaluation.observation_delay_steps | null（未配置/待填） |
| evaluation.action_delay_steps | null（未配置/待填） |
| evaluation.duration_s | 30.0 |
| evaluation.settling_s | 1.0 |
| evaluation.episodes_per_case | 16 |
| evaluation.seed | 123 |
| evaluation.height_m | null（未配置/待填） |
| evaluation.vx_values_m_s | null（未配置/待填） |
| evaluation.wz_values_rad_s | null（未配置/待填） |
| evaluation.combined_commands | null（未配置/待填） |
| disturbance.baseline_evaluation_passed | false |
| disturbance.ramp_iterations | 3000 |
| disturbance.final_push_velocity_m_s | 1.25 |
| disturbance.collision_interval_s | [8.0, 15.0] |
| disturbance.collision_duration_s | 0.1 |
| disturbance.collision_force_range_n | [100.0, 300.0] |
| disturbance.lateral_probability | 0.8 |
| disturbance.phase2_start_iteration | null（未配置/待填） |
| air_rewards.joint_limit | -10.0 |
| air_rewards.wheel_center | 10.0 |
| air_rewards.wheel_center_sigma | null（未配置/待填） |
| air_rewards.wheel_torque | 20.0 |
| air_rewards.wheel_torque_sigma | 1.5 |
| air_rewards.wheel_speed_alignment | -10.0 |
| command_curriculum.min_completed_episodes | 4096 |
| command_curriculum.initial_fraction | 1.0 |
| command_curriculum.increment | 0.05 |
| command_curriculum.success_fraction | 0.8 |
| command_curriculum.velocity_error_threshold_m_s | null（未配置/待填） |
| command_curriculum.yaw_error_threshold_rad_s | null（未配置/待填） |
| transition_reset.probability | 0.0 |
| transition_reset.states_npz | null（未配置/待填） |


</details>


### spin


| 奖励项 | 合并后权重 | 生效说明 |
|---|---|---|
| track_lin_vel | 0.0 | 关闭 |
| lin_vel_error | 0.0 | 关闭 |
| track_ang_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| ang_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_height | 1.0 | 需再结合dt、状态mask、事件定义 |
| height_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| flat_roll | 1.0 | 需再结合dt、状态mask、事件定义 |
| flat_pitch | 1.0 | 需再结合dt、状态mask、事件定义 |
| roll_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| pitch_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| vertical_velocity | -0.5 | 需再结合dt、状态mask、事件定义 |
| angular_xy | -0.05 | 需再结合dt、状态mask、事件定义 |
| no_fork | -1.0 | 需再结合dt、状态mask、事件定义 |
| no_fork_square | -1.0 | 需再结合dt、状态mask、事件定义 |
| undesired_contact | -2.0 | 需再结合dt、状态mask、事件定义 |
| stand_still | -1.0 | 需再结合dt、状态mask、事件定义 |
| joint_torque | -1e-05 | 需再结合dt、状态mask、事件定义 |
| wheel_power | -1e-05 | 需再结合dt、状态mask、事件定义 |
| action_rate | -0.01 | 需再结合dt、状态mask、事件定义 |
| termination | -4.0 | 需再结合dt、状态mask、事件定义 |
| spin_velocity | 1.0 | 需再结合dt、状态mask、事件定义 |
| spin_speed | 1.0 | 需再结合dt、状态mask、事件定义 |
| spin_heading | 5.0 | 需再结合dt、状态mask、事件定义 |
| spin_velocity_error | -0.2 | 需再结合dt、状态mask、事件定义 |
| spin_speed_error | -0.2 | 需再结合dt、状态mask、事件定义 |
| leg_symmetry | 0.0 | 关闭 |



<details markdown="1"><summary>完整阶段设置：含事件/额外奖励、地形和状态阈值</summary>


| 字段 | 原值 |
|---|---|
| terrain.tile_size_m | [9.0, 9.0] |
| terrain.rows | 8 |
| terrain.columns | 10 |
| terrain.difficulty_range | [0.0, 1.0] |
| terrain.flat_proportion | 0.5 |
| terrain.rough_proportion | 0.3 |
| terrain.slope_proportion | 0.2 |
| terrain.rough_noise_range_m | [0.0, 0.03] |
| terrain.rough_noise_step_m | 0.005 |
| terrain.rough_downsampled_scale_m | 0.2 |
| terrain.heightfield_border_width_m | 1.0 |
| terrain.border_width_m | 5.0 |
| terrain.boundary_margin_m | 0.5 |
| terrain.slope_angle_range_rad | [-0.1, 0.1] |
| translation_speed_range_m_s | null（未配置/待填） |
| spin_low_range_rad_s | null（未配置/待填） |
| spin_high_range_rad_s | null（未配置/待填） |
| reference_frame | fixed_world_yaw |
| reference_yaw_rad | 0.0 |
| disturbance_phase | 2 |


</details>


## config\policies\p3\policy_meta.yaml

[配置来源](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/config/policies/p3/policy_meta.yaml>)

| 字段 | 原值 |
|---|---|
| name | p3_jump |
| obs_version | 2 |
| hidden_dims | [256, 128, 64] |
| activation | elu |
| observation_scales.command | [1.0, 1.0, 1.0] |
| observation_scales.height | 5.0 |
| observation_scales.angular_velocity | 0.5 |
| observation_scales.gravity | 1.0 |
| observation_scales.joint_position | 1.0 |
| observation_scales.joint_velocity | 0.1 |
| action_scales | [0.5, 0.5, 10.0, 0.5, 0.5, 10.0] |
| action_clip | null（未配置/待填） |
| kp | [null, null, null, null, null, null] |
| kd | [null, null, null, null, null, null] |
| torque_limit_nm | [null, null, null, null, null, null] |
| policy_family | p3 |
| mode_semantics | ["zero", "zero", "zero", "zero", "jump_active", "target_height_scaled", "phase"] |
| guide_version | 2.2 |



<details markdown="1"><summary>完整training：命令/奖励参数/PPO/课程/评测/扰动</summary>


| 字段 | 原值 |
|---|---|
| seed | 42 |
| num_envs | 4096 |
| rollout_steps | 48 |
| max_iterations | 20000 |
| save_interval | 500 |
| episode_length_s | 20.0 |
| init_noise_std | 1.0 |
| reward_clip | 2.5 |
| ppo.value_loss_coef | 2.0 |
| ppo.use_clipped_value_loss | true |
| ppo.clip_param | 0.2 |
| ppo.entropy_coef | 0.005 |
| ppo.num_learning_epochs | 5 |
| ppo.num_mini_batches | 4 |
| ppo.learning_rate | 0.0001 |
| ppo.schedule | adaptive |
| ppo.gamma | 0.995 |
| ppo.lam | 0.95 |
| ppo.desired_kl | 0.01 |
| ppo.max_grad_norm | 1.0 |
| commands.segment_duration_s | [3.0, 15.0] |
| commands.height_duration_s | [2.0, 6.0] |
| commands.vx_range_m_s | null（未配置/待填） |
| commands.wz_range_rad_s | null（未配置/待填） |
| commands.height_range_m | null（未配置/待填） |
| commands.linear_slew_m_s2 | 2.0 |
| commands.angular_slew_rad_s2 | 10.0 |
| commands.height_slew_m_s | null（未配置/待填） |
| commands.segment_probabilities | [0.1, 0.25, 0.15, 0.25, 0.1, 0.15] |
| commands.dash_range_m_s | null（未配置/待填） |
| reward_parameters.linear_sigma | 0.5 |
| reward_parameters.angular_sigma | 0.25 |
| reward_parameters.height_sigma | 0.001 |
| reward_parameters.roll_sigma | 0.01 |
| reward_parameters.pitch_sigma | 0.02 |
| reward_parameters.pitch_velocity_amplitude | 2.0 |
| reward_parameters.pitch_velocity_sigma | 3.0 |
| reward_parameters.pitch_velocity_offset | 2.0 |
| reward_parameters.fork_deadzone_m | 0.05 |
| reward_parameters.stand_deadzone | 0.1 |
| reward_parameters.contact_force_n | 3.0 |
| reward_parameters.spin_velocity_sigma | 0.25 |
| reward_parameters.spin_heading_sigma | 0.025 |
| reward_parameters.air_wheel_torque_sigma | 1.5 |
| reward_parameters.fork_square_scale | 5.0 |
| reward_parameters.leg_length_symmetry_scale | 10.0 |
| rewards.track_lin_vel | 1.0 |
| rewards.lin_vel_error | -1.0 |
| rewards.track_ang_vel | 1.0 |
| rewards.ang_vel_error | -1.0 |
| rewards.track_height | 1.0 |
| rewards.height_error | -1.0 |
| rewards.flat_roll | 1.0 |
| rewards.flat_pitch | 1.0 |
| rewards.roll_penalty | -2.0 |
| rewards.pitch_penalty | -2.0 |
| rewards.vertical_velocity | -0.5 |
| rewards.angular_xy | -0.05 |
| rewards.no_fork | -1.0 |
| rewards.no_fork_square | -1.0 |
| rewards.undesired_contact | -2.0 |
| rewards.stand_still | -1.0 |
| rewards.joint_torque | -0.0001 |
| rewards.wheel_power | -0.0001 |
| rewards.action_rate | -0.01 |
| rewards.termination | -4.0 |
| rewards.jump_apex | 5.0 |
| rewards.jump_landing | 3.0 |
| rewards.jump_flight | 0.15 |
| rewards.jump_crouch | 0.5 |
| rewards.jump_takeoff | 2.5 |
| rewards.jump_push_symmetry | 0.05 |
| rewards.jump_tuck | 1.7 |
| rewards.jump_prepare | 0.5 |
| rewards.jump_impact | -0.0001 |
| rewards.jump_asymmetric_landing | -1.0 |
| rewards.uncommanded_flight | -1.0 |
| rewards.leg_symmetry | 0.0 |
| evaluation.observation_delay_steps | null（未配置/待填） |
| evaluation.action_delay_steps | null（未配置/待填） |
| evaluation.duration_s | 10.0 |
| evaluation.settling_s | 1.0 |
| evaluation.episodes_per_case | 16 |
| evaluation.seed | 123 |
| evaluation.height_m | null（未配置/待填） |
| evaluation.vx_values_m_s | null（未配置/待填） |
| evaluation.wz_values_rad_s | null（未配置/待填） |
| evaluation.combined_commands | null（未配置/待填） |
| evaluation.jump_velocity_m_s | null（未配置/待填） |
| disturbance.baseline_evaluation_passed | false |
| disturbance.ramp_iterations | 3000 |
| disturbance.final_push_velocity_m_s | 1.25 |
| disturbance.collision_interval_s | [8.0, 15.0] |
| disturbance.collision_duration_s | 0.1 |
| disturbance.collision_force_range_n | [100.0, 300.0] |
| disturbance.lateral_probability | 0.8 |
| disturbance.phase2_start_iteration | null（未配置/待填） |
| air_rewards.joint_limit | -10.0 |
| air_rewards.wheel_center | 10.0 |
| air_rewards.wheel_center_sigma | null（未配置/待填） |
| air_rewards.wheel_torque | 20.0 |
| air_rewards.wheel_torque_sigma | 1.5 |
| air_rewards.wheel_speed_alignment | -10.0 |
| command_curriculum.min_completed_episodes | 4096 |
| command_curriculum.initial_fraction | 1.0 |
| command_curriculum.increment | 0.05 |
| command_curriculum.success_fraction | 0.8 |
| command_curriculum.velocity_error_threshold_m_s | null（未配置/待填） |
| command_curriculum.yaw_error_threshold_rad_s | null（未配置/待填） |
| transition_reset.probability | 0.0 |
| transition_reset.states_npz | null（未配置/待填） |


</details>


### jump


| 奖励项 | 合并后权重 | 生效说明 |
|---|---|---|
| track_lin_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| lin_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_ang_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| ang_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_height | 1.0 | 需再结合dt、状态mask、事件定义 |
| height_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| flat_roll | 1.0 | 需再结合dt、状态mask、事件定义 |
| flat_pitch | 1.0 | 需再结合dt、状态mask、事件定义 |
| roll_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| pitch_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| vertical_velocity | -0.5 | 需再结合dt、状态mask、事件定义 |
| angular_xy | -0.05 | 需再结合dt、状态mask、事件定义 |
| no_fork | -1.0 | 需再结合dt、状态mask、事件定义 |
| no_fork_square | -1.0 | 需再结合dt、状态mask、事件定义 |
| undesired_contact | -2.0 | 需再结合dt、状态mask、事件定义 |
| stand_still | -1.0 | 需再结合dt、状态mask、事件定义 |
| joint_torque | -0.0001 | 需再结合dt、状态mask、事件定义 |
| wheel_power | -0.0001 | 需再结合dt、状态mask、事件定义 |
| action_rate | -0.01 | 需再结合dt、状态mask、事件定义 |
| termination | -4.0 | 需再结合dt、状态mask、事件定义 |
| jump_apex | 5.0 | 需再结合dt、状态mask、事件定义 |
| jump_landing | 3.0 | 需再结合dt、状态mask、事件定义 |
| jump_flight | 0.15 | 需再结合dt、状态mask、事件定义 |
| jump_crouch | 0.5 | 需再结合dt、状态mask、事件定义 |
| jump_takeoff | 2.5 | 需再结合dt、状态mask、事件定义 |
| jump_push_symmetry | 0.05 | 需再结合dt、状态mask、事件定义 |
| jump_tuck | 1.7 | 需再结合dt、状态mask、事件定义 |
| jump_prepare | 0.5 | 需再结合dt、状态mask、事件定义 |
| jump_impact | -0.0001 | 需再结合dt、状态mask、事件定义 |
| jump_asymmetric_landing | -1.0 | 需再结合dt、状态mask、事件定义 |
| uncommanded_flight | -1.0 | 需再结合dt、状态mask、事件定义 |
| leg_symmetry | 0.0 | 关闭 |



<details markdown="1"><summary>完整阶段设置：含事件/额外奖励、地形和状态阈值</summary>


| 字段 | 原值 |
|---|---|
| event_duration_s | 1.2 |
| first_trigger_range_s | [2.0, 5.0] |
| between_events_s | [3.0, 5.0] |
| jump_count_probabilities | [0.2, 0.7, 0.1] |
| height_range_m | null（未配置/待填） |
| feasible_height_m | null（未配置/待填） |
| crouch_duration_s | 0.25 |
| crouch_leg_length_m | null（未配置/待填） |
| tuck_leg_length_m | null（未配置/待填） |
| landing_leg_length_m | null（未配置/待填） |
| landing_prepare_time_s | 0.1 |
| landing_stable_s | 1.0 |
| max_touchdown_difference_s | 0.05 |
| apex_sigma | null（未配置/待填） |
| landing_tilt_rad | null（未配置/待填） |
| landing_speed_error_m_s | null（未配置/待填） |
| non_event_tracking_scale | 0.5 |
| guidance_final_scale | 0.3 |
| guidance_decay_iterations | 2000 |
| guidance_success_threshold | 0.7 |
| disturbance_phase | 2 |
| curriculum_min_events | 100 |
| height_tolerance_m | 0.05 |


</details>


### tunnel


| 奖励项 | 合并后权重 | 生效说明 |
|---|---|---|
| track_lin_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| lin_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_ang_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| ang_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_height | 1.0 | 需再结合dt、状态mask、事件定义 |
| height_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| flat_roll | 1.0 | 需再结合dt、状态mask、事件定义 |
| flat_pitch | 1.0 | 需再结合dt、状态mask、事件定义 |
| roll_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| pitch_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| vertical_velocity | -0.5 | 需再结合dt、状态mask、事件定义 |
| angular_xy | -0.05 | 需再结合dt、状态mask、事件定义 |
| no_fork | -1.0 | 需再结合dt、状态mask、事件定义 |
| no_fork_square | -1.0 | 需再结合dt、状态mask、事件定义 |
| undesired_contact | -2.0 | 需再结合dt、状态mask、事件定义 |
| stand_still | -1.0 | 需再结合dt、状态mask、事件定义 |
| joint_torque | -0.0001 | 需再结合dt、状态mask、事件定义 |
| wheel_power | -0.0001 | 需再结合dt、状态mask、事件定义 |
| action_rate | -0.01 | 需再结合dt、状态mask、事件定义 |
| termination | -4.0 | 需再结合dt、状态mask、事件定义 |
| jump_apex | 5.0 | 需再结合dt、状态mask、事件定义 |
| jump_landing | 3.0 | 需再结合dt、状态mask、事件定义 |
| jump_flight | 0.15 | 需再结合dt、状态mask、事件定义 |
| jump_crouch | 0.5 | 需再结合dt、状态mask、事件定义 |
| jump_takeoff | 2.5 | 需再结合dt、状态mask、事件定义 |
| jump_push_symmetry | 0.05 | 需再结合dt、状态mask、事件定义 |
| jump_tuck | 1.7 | 需再结合dt、状态mask、事件定义 |
| jump_prepare | 0.5 | 需再结合dt、状态mask、事件定义 |
| jump_impact | -0.0001 | 需再结合dt、状态mask、事件定义 |
| jump_asymmetric_landing | -1.0 | 需再结合dt、状态mask、事件定义 |
| uncommanded_flight | -1.0 | 需再结合dt、状态mask、事件定义 |
| leg_symmetry | 0.0 | 关闭 |



<details markdown="1"><summary>完整阶段设置：含事件/额外奖励、地形和状态阈值</summary>


| 字段 | 原值 |
|---|---|
| event_duration_s | 1.2 |
| first_trigger_range_s | [2.0, 5.0] |
| between_events_s | [3.0, 5.0] |
| jump_count_probabilities | [0.2, 0.7, 0.1] |
| height_range_m | null（未配置/待填） |
| feasible_height_m | null（未配置/待填） |
| crouch_duration_s | 0.25 |
| crouch_leg_length_m | null（未配置/待填） |
| tuck_leg_length_m | null（未配置/待填） |
| landing_leg_length_m | null（未配置/待填） |
| landing_prepare_time_s | 0.1 |
| landing_stable_s | 1.0 |
| max_touchdown_difference_s | 0.05 |
| apex_sigma | null（未配置/待填） |
| landing_tilt_rad | null（未配置/待填） |
| landing_speed_error_m_s | null（未配置/待填） |
| non_event_tracking_scale | 0.5 |
| guidance_final_scale | 0.3 |
| guidance_decay_iterations | 2000 |
| guidance_success_threshold | 0.7 |
| tunnel.vx_range_m_s | null（未配置/待填） |
| tunnel.beam_height_m | 0.27 |
| tunnel.beam_length_m | 0.35 |
| tunnel.beam_thickness_m | 0.02 |
| tunnel.no_jump_beam_pose | [0.0, 0.0, -1.0, 1.0, 0.0, 0.0, 0.0] |
| tunnel.lane_width_m | 0.8 |
| tunnel.rail_height_m | 0.2 |
| tunnel.lane_length_m | 2.9 |
| tunnel.rail_thickness_m | null（未配置/待填） |
| tunnel.approach_distance_m | null（未配置/待填） |
| tunnel.trigger_distance_m | null（未配置/待填） |
| tunnel.height_curriculum_m | [0.1, 0.15, 0.2, 0.27, 0.3] |
| tunnel.clearance_margin_m | 0.03 |
| tunnel.landing_margin_m | 0.05 |
| tunnel.initial_yaw_range_rad | [-0.0872664626, 0.0872664626] |
| tunnel.crossing_weight | 5.0 |
| tunnel.obstacle_contact_weight | -5.0 |
| tunnel.top_contact_weight | -10.0 |
| tunnel.approach_jitter_m | null（未配置/待填） |
| tunnel.height_jitter_m | [-0.01, 0.01] |
| disturbance_phase | 2 |
| curriculum_min_events | 100 |
| height_tolerance_m | 0.05 |


</details>


## config\reference\scut_p1.yaml

[配置来源](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/config/reference/scut_p1.yaml>)

| 字段 | 原值 |
|---|---|
| name | scut_p1_latest_from_scratch |
| obs_version | 2 |
| hidden_dims | [256, 128, 64] |
| activation | elu |
| observation_scales.command | [1.0, 1.0, 1.0] |
| observation_scales.height | 5.0 |
| observation_scales.angular_velocity | 0.5 |
| observation_scales.gravity | 1.0 |
| observation_scales.joint_position | 1.0 |
| observation_scales.joint_velocity | 0.1 |
| action_scales | [0.5, 0.5, 10.0, 0.5, 0.5, 10.0] |
| action_clip | null（未配置/待填） |
| kp | [60, 60, 0, 60, 60, 0] |
| kd | [2, 2, 0.2, 2, 2, 0.2] |
| torque_limit_nm | [40, 40, 5, 40, 40, 5] |
| history_estimator.frames | 0 |
| history_estimator.hidden_dims | [128, 64] |
| policy_family | p1 |
| mode_semantics | ["normal", "stair", "zero", "recover", "zero", "zero", "zero"] |
| guide_version | 2.2 |
| reference_notes | P1-flat baseline only. Ranges/classifier thresholds are simulation design choices. Other stages retain their readiness requirements. |



<details markdown="1"><summary>完整training：命令/奖励参数/PPO/课程/评测/扰动</summary>


| 字段 | 原值 |
|---|---|
| seed | 42 |
| num_envs | 4096 |
| rollout_steps | 48 |
| max_iterations | 20000 |
| save_interval | 200 |
| episode_length_s | 20.0 |
| init_noise_std | 1.0 |
| reward_clip | 2.5 |
| history_estimator.learning_rate | 0.001 |
| history_estimator.velocity_loss_coef | 1.0 |
| history_estimator.contact_loss_coef | 1.0 |
| ppo.value_loss_coef | 4.0 |
| ppo.use_clipped_value_loss | true |
| ppo.clip_param | 0.2 |
| ppo.entropy_coef | 0.005 |
| ppo.num_learning_epochs | 5 |
| ppo.num_mini_batches | 4 |
| ppo.learning_rate | 0.0001 |
| ppo.schedule | adaptive |
| ppo.gamma | 0.995 |
| ppo.lam | 0.95 |
| ppo.desired_kl | 0.01 |
| ppo.max_grad_norm | 1.0 |
| commands.segment_duration_s | [3.0, 15.0] |
| commands.height_duration_s | [2.0, 6.0] |
| commands.vx_range_m_s | [-2.7, 2.7] |
| commands.wz_range_rad_s | [-5.0, 5.0] |
| commands.height_range_m | [0.2, 0.35] |
| commands.linear_slew_m_s2 | 2.0 |
| commands.angular_slew_rad_s2 | 10.0 |
| commands.height_slew_m_s | 0.1 |
| commands.segment_probabilities | [0.1, 0.25, 0.15, 0.25, 0.1, 0.15] |
| commands.dash_range_m_s | [-3.0, 3.0] |
| commands.combined_wz_limit_rad_s | 3.0 |
| reward_parameters.linear_sigma | 0.5 |
| reward_parameters.angular_sigma | 0.25 |
| reward_parameters.height_sigma | 0.001 |
| reward_parameters.height_wide_sigma | 0.025 |
| reward_parameters.height_gate_full_error_m | 0.05 |
| reward_parameters.height_gate_zero_error_m | 0.1 |
| reward_parameters.roll_sigma | 0.01 |
| reward_parameters.pitch_sigma | 0.02 |
| reward_parameters.pitch_velocity_amplitude | 1.0 |
| reward_parameters.pitch_velocity_sigma | 4.0 |
| reward_parameters.pitch_velocity_offset | 3.0 |
| reward_parameters.fork_deadzone_m | 0.05 |
| reward_parameters.stand_deadzone | 0.1 |
| reward_parameters.contact_force_n | 3.0 |
| reward_parameters.spin_velocity_sigma | 0.25 |
| reward_parameters.spin_heading_sigma | 0.025 |
| reward_parameters.air_wheel_torque_sigma | 1.5 |
| reward_parameters.fork_square_scale | 5.0 |
| reward_parameters.leg_length_symmetry_scale | 10.0 |
| rewards.track_lin_vel | 1.0 |
| rewards.lin_vel_error | -8.0 |
| rewards.track_ang_vel | 1.0 |
| rewards.ang_vel_error | -1.0 |
| rewards.track_height | 1.0 |
| rewards.track_height_wide | 2.0 |
| rewards.height_error | -1.0 |
| rewards.flat_roll | 1.0 |
| rewards.flat_pitch | 1.0 |
| rewards.roll_penalty | -2.0 |
| rewards.pitch_penalty | -3.0 |
| rewards.vertical_velocity | -4.0 |
| rewards.angular_xy | -0.2 |
| rewards.no_fork | -1.0 |
| rewards.no_fork_square | -1.0 |
| rewards.undesired_contact | -4.0 |
| rewards.stand_still | -2.0 |
| rewards.joint_torque | -0.0001 |
| rewards.wheel_power | -0.0001 |
| rewards.action_rate | -0.01 |
| rewards.leg_joint_vel | -0.005 |
| rewards.leg_joint_acc | -2e-06 |
| rewards.wheel_vel | -1e-05 |
| rewards.action_smoothness_leg | -0.05 |
| rewards.action_smoothness_wheel | -0.01 |
| rewards.termination | -4.0 |
| rewards.leg_symmetry | 0.0 |
| evaluation.flat_suite.height_samples | 3 |
| evaluation.flat_suite.speed_fractions | [0.25, 0.5, 1.0] |
| evaluation.flat_suite.combined_fractions | [0.5, 1.0] |
| evaluation.flat_suite.seeds | [123, 456] |
| evaluation.flat_suite.startup_s | 2.0 |
| evaluation.flat_suite.hold_s | 20.0 |
| evaluation.flat_suite.stand_window_s | 10.0 |
| evaluation.flat_suite.transition_settling_s | 2.0 |
| evaluation.flat_suite.stable_hold_s | 0.5 |
| evaluation.flat_suite.recovery_deadline_s | 3.0 |
| evaluation.flat_suite.push_after_s | 4.0 |
| evaluation.flat_suite.push_velocity_m_s | 0.25 |
| evaluation.flat_suite.delay_command_fraction | 0.5 |
| evaluation.flat_suite.delay_pairs_steps | [[3, 3], [8, 5]] |
| evaluation.flat_suite.trace_stride | 5 |
| evaluation.flat_suite.acceptance.stand_drift_m | 0.2 |
| evaluation.flat_suite.acceptance.tilt_p95_rad | 0.17453292519943295 |
| evaluation.flat_suite.acceptance.contact_fraction | 0.01 |
| evaluation.observation_delay_steps | 5 |
| evaluation.action_delay_steps | 4 |
| evaluation.duration_s | 10.0 |
| evaluation.settling_s | 1.0 |
| evaluation.episodes_per_case | 16 |
| evaluation.seed | 123 |
| evaluation.height_m | 0.22 |
| evaluation.vx_values_m_s | [-2.0, -1.0, -0.5, 0, 0.5, 1.0, 2.0] |
| evaluation.wz_values_rad_s | [-4.0, -2.0, -1.0, 1.0, 2.0, 4.0] |
| evaluation.combined_commands | [[1.0, 0, 1.0], [-1.0, 0, -1.0]] |
| disturbance.baseline_evaluation_passed | true |
| disturbance.ramp_iterations | 3000 |
| disturbance.final_push_velocity_m_s | 1.25 |
| disturbance.collision_interval_s | [8.0, 15.0] |
| disturbance.collision_duration_s | 0.1 |
| disturbance.collision_force_range_n | [100.0, 300.0] |
| disturbance.lateral_probability | 0.8 |
| disturbance.phase2_start_iteration | 4000 |
| air_rewards.joint_limit | -10.0 |
| air_rewards.wheel_center | 10.0 |
| air_rewards.wheel_center_sigma | 0.02 |
| air_rewards.wheel_torque | 20.0 |
| air_rewards.wheel_torque_sigma | 1.5 |
| air_rewards.wheel_speed_alignment | -10.0 |
| command_curriculum.min_completed_episodes | 4096 |
| command_curriculum.initial_fraction | 0.4 |
| command_curriculum.increment | 0.05 |
| command_curriculum.success_fraction | 0.75 |
| command_curriculum.velocity_error_threshold_m_s | 0.1 |
| command_curriculum.yaw_error_threshold_rad_s | 0.1 |
| command_curriculum.relative_error | 0.25 |
| command_curriculum.height_error_threshold_m | 0.05 |
| height_wide_anneal.final_weight | 0.5 |
| height_wide_anneal.start_iteration | 2000 |
| height_wide_anneal.ramp_iterations | 500 |
| transition_reset.probability | 0.0 |
| transition_reset.states_npz | null（未配置/待填） |


</details>


### flat


| 奖励项 | 合并后权重 | 生效说明 |
|---|---|---|
| track_lin_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| lin_vel_error | -8.0 | 需再结合dt、状态mask、事件定义 |
| track_ang_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| ang_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_height | 1.0 | 需再结合dt、状态mask、事件定义 |
| track_height_wide | 2.0 | 需再结合dt、状态mask、事件定义 |
| height_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| flat_roll | 1.0 | 需再结合dt、状态mask、事件定义 |
| flat_pitch | 1.0 | 需再结合dt、状态mask、事件定义 |
| roll_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| pitch_penalty | -3.0 | 需再结合dt、状态mask、事件定义 |
| vertical_velocity | -4.0 | 需再结合dt、状态mask、事件定义 |
| angular_xy | -0.2 | 需再结合dt、状态mask、事件定义 |
| no_fork | -1.0 | 需再结合dt、状态mask、事件定义 |
| no_fork_square | -1.0 | 需再结合dt、状态mask、事件定义 |
| undesired_contact | -4.0 | 需再结合dt、状态mask、事件定义 |
| stand_still | -2.0 | 需再结合dt、状态mask、事件定义 |
| joint_torque | -0.0001 | 需再结合dt、状态mask、事件定义 |
| wheel_power | -0.0001 | 需再结合dt、状态mask、事件定义 |
| action_rate | -0.01 | 需再结合dt、状态mask、事件定义 |
| leg_joint_vel | -0.005 | 需再结合dt、状态mask、事件定义 |
| leg_joint_acc | -2e-06 | 需再结合dt、状态mask、事件定义 |
| wheel_vel | -1e-05 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_leg | -0.05 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_wheel | -0.01 | 需再结合dt、状态mask、事件定义 |
| termination | -4.0 | 需再结合dt、状态mask、事件定义 |
| leg_symmetry | 0.0 | 关闭 |



<details markdown="1"><summary>完整阶段设置：含事件/额外奖励、地形和状态阈值</summary>


| 字段 | 原值 |
|---|---|
| air_reset_probability | 0.0 |
| recovery_probability | 0.0 |
| disturbance_phase | 1 |
| reward_overrides | {} |


</details>


### landing


| 奖励项 | 合并后权重 | 生效说明 |
|---|---|---|
| track_lin_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| lin_vel_error | -8.0 | 需再结合dt、状态mask、事件定义 |
| track_ang_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| ang_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_height | 1.0 | 需再结合dt、状态mask、事件定义 |
| track_height_wide | 1.5 | 需再结合dt、状态mask、事件定义 |
| height_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| flat_roll | 1.0 | 需再结合dt、状态mask、事件定义 |
| flat_pitch | 1.0 | 需再结合dt、状态mask、事件定义 |
| roll_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| pitch_penalty | -3.0 | 需再结合dt、状态mask、事件定义 |
| vertical_velocity | -4.0 | 需再结合dt、状态mask、事件定义 |
| angular_xy | -0.2 | 需再结合dt、状态mask、事件定义 |
| no_fork | -1.0 | 需再结合dt、状态mask、事件定义 |
| no_fork_square | -1.0 | 需再结合dt、状态mask、事件定义 |
| undesired_contact | -4.0 | 需再结合dt、状态mask、事件定义 |
| stand_still | -2.0 | 需再结合dt、状态mask、事件定义 |
| joint_torque | -0.0001 | 需再结合dt、状态mask、事件定义 |
| wheel_power | -0.0001 | 需再结合dt、状态mask、事件定义 |
| action_rate | -0.002 | 需再结合dt、状态mask、事件定义 |
| leg_joint_vel | -0.001 | 需再结合dt、状态mask、事件定义 |
| leg_joint_acc | -4e-07 | 需再结合dt、状态mask、事件定义 |
| wheel_vel | -2e-06 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_leg | -0.01 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_wheel | -0.002 | 需再结合dt、状态mask、事件定义 |
| termination | -4.0 | 需再结合dt、状态mask、事件定义 |
| leg_symmetry | 0.0 | 关闭 |



<details markdown="1"><summary>完整阶段设置：含事件/额外奖励、地形和状态阈值</summary>


| 字段 | 原值 |
|---|---|
| landing_reward.progress_budget | 0.75 |
| landing_reward.success_bonus | 1.5 |
| landing_reward.failure_cost | 1.0 |
| landing_reward.contact_force_n | 3.0 |
| landing_reward.support_force_n | 20.0 |
| landing_reward.contact_timeout_s | 2.0 |
| landing_reward.settle_support_s | 0.1 |
| landing_reward.cushion_max_s | 0.5 |
| landing_reward.window_s | 3.0 |
| landing_reward.stable_s | 0.5 |
| landing_reward.tilt_rad | 0.17453292519943295 |
| landing_reward.angular_xy_rad_s | 0.5 |
| landing_reward.vertical_velocity_m_s | 0.2 |
| landing_reward.height_error_m | 0.05 |
| landing_reward.wheel_center_weight | 4.0 |
| landing_reward.wheel_center_sigma | 0.02 |
| landing_reward.wheel_speed_weight | 6.0 |
| landing_reward.wheel_speed_sigma | 1.0 |
| landing_reward.contact_multiplier | 8.0 |
| landing_reward.guide_body_regex | .*_guide_link |
| landing_reward.guide_hard_speed_m_s | 1.0 |
| landing_reward.guide_speed_cost | 0.5 |
| landing_reward.leg_extension_weight | 3.0 |
| landing_reward.leg_extension_target_m | 0.28 |
| landing_reward.leg_extension_scale_m | 0.1 |
| landing_diagnostics.first_contact_force_n | 3.0 |
| landing_diagnostics.support_force_n | 20.0 |
| landing_diagnostics.first_contact_timeout_s | 2.0 |
| landing_diagnostics.observation_window_s | 3.0 |
| landing_diagnostics.stable_duration_s | 0.5 |
| landing_diagnostics.touchdown_difference_s | 0.05 |
| landing_diagnostics.tilt_rad | 0.17453292519943295 |
| landing_diagnostics.angular_xy_rad_s | 0.5 |
| landing_diagnostics.vertical_velocity_m_s | 0.2 |
| landing_diagnostics.height_error_m | 0.05 |
| air_reset_probability | 0.4 |
| air_height_offset_m | [0.12, 0.42] |
| air_vx_range_m_s | [-2.5, 2.5] |
| air_tilt_rad | [0.1, 0.2] |
| air_vy_range_m_s | [-0.5, 0.5] |
| air_angular_velocity_rad_s | [0.05, 0.1, 0.5] |
| air_leg_length_range_m | [0.15, 0.35] |
| air_leg_angle_range_rad | [-0.7853981633974483, 0.7853981633974483] |
| air_command_limit_s | 3.0 |
| air_command_vx_limit_m_s | 2.5 |
| air_command_wz_limit_rad_s | 1.5707963267948966 |
| air_vx_command_probability | 0.8 |
| air_vx_command_noise_m_s | 0.3 |
| air_height_curriculum.levels_m | [0.2, 0.24, 0.28, 0.32, 0.36, 0.42] |
| air_height_curriculum.min_events | 1024 |
| air_height_curriculum.success_rate | 0.8 |
| command_curriculum_landing_gate.min_events | 256 |
| command_curriculum_landing_gate.success_rate | 0.75 |
| recovery_probability | 0.0 |
| disturbance_phase | 1 |
| reward_overrides.track_height_wide | 1.5 |
| reward_overrides.action_rate | -0.002 |
| reward_overrides.action_smoothness_leg | -0.01 |
| reward_overrides.action_smoothness_wheel | -0.002 |
| reward_overrides.leg_joint_vel | -0.001 |
| reward_overrides.leg_joint_acc | -4e-07 |
| reward_overrides.wheel_vel | -2e-06 |


</details>


### stairs


| 奖励项 | 合并后权重 | 生效说明 |
|---|---|---|
| track_lin_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| lin_vel_error | -8.0 | 需再结合dt、状态mask、事件定义 |
| track_ang_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| ang_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_height | 1.0 | 需再结合dt、状态mask、事件定义 |
| track_height_wide | 1.0 | 需再结合dt、状态mask、事件定义 |
| height_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| flat_roll | 1.0 | 需再结合dt、状态mask、事件定义 |
| flat_pitch | 1.0 | 需再结合dt、状态mask、事件定义 |
| roll_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| pitch_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| vertical_velocity | -0.5 | 需再结合dt、状态mask、事件定义 |
| angular_xy | -0.05 | 需再结合dt、状态mask、事件定义 |
| no_fork | -1.0 | 需再结合dt、状态mask、事件定义 |
| no_fork_square | -1.0 | 需再结合dt、状态mask、事件定义 |
| undesired_contact | -4.0 | 需再结合dt、状态mask、事件定义 |
| stand_still | -2.0 | 需再结合dt、状态mask、事件定义 |
| joint_torque | -1e-05 | 需再结合dt、状态mask、事件定义 |
| wheel_power | -1e-05 | 需再结合dt、状态mask、事件定义 |
| action_rate | -0.002 | 需再结合dt、状态mask、事件定义 |
| leg_joint_vel | -0.001 | 需再结合dt、状态mask、事件定义 |
| leg_joint_acc | -4e-07 | 需再结合dt、状态mask、事件定义 |
| wheel_vel | -2e-06 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_leg | -0.01 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_wheel | -0.002 | 需再结合dt、状态mask、事件定义 |
| termination | -4.0 | 需再结合dt、状态mask、事件定义 |
| leg_symmetry | 0.0 | 关闭 |



| 项 | 台阶基值 | flat | grid | slope | rough |
|---|---|---|---|---|---|
| action_rate | -0.002 | -0.01 | -0.005 | -0.0075 | -0.006 |
| action_smoothness_leg | -0.01 | -0.05 | -0.025 | -0.0375 | -0.03 |
| action_smoothness_wheel | -0.002 | -0.01 | -0.005 | -0.0075 | -0.006 |
| ang_vel_error | -1.0 | -1.0 | -1.0 | -1.0 | -1.0 |
| angular_xy | -0.05 | -0.2 | -0.1 | -0.15 | -0.15 |
| flat_pitch | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| flat_roll | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| height_error | -1.0 | -1.0 | -1.0 | -1.0 | -1.0 |
| joint_torque | -1e-05 | -0.0001 | -3e-05 | -5e-05 | -5e-05 |
| leg_joint_acc | -4e-07 | -2e-06 | -1e-06 | -1.5e-06 | -1.2e-06 |
| leg_joint_vel | -0.001 | -0.005 | -0.0025 | -0.00375 | -0.003 |
| leg_symmetry | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| lin_vel_error | -8.0 | -8.0 | -8.0 | -8.0 | -8.0 |
| no_fork | -1.0 | -1.0 | -1.0 | -1.0 | -1.0 |
| no_fork_square | -1.0 | -1.0 | -1.0 | -1.0 | -1.0 |
| pitch_penalty | -2.0 | -3.0 | -2.5 | -2.25 | -2.75 |
| roll_penalty | -2.0 | -2.0 | -2.0 | -2.0 | -2.0 |
| stand_still | -2.0 | -2.0 | -2.0 | -2.0 | -2.0 |
| termination | -4.0 | -4.0 | -4.0 | -4.0 | -4.0 |
| track_ang_vel | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| track_height | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| track_height_wide | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| track_lin_vel | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| undesired_contact | -4.0 | -4.0 | -4.0 | -4.0 | -4.0 |
| vertical_velocity | -0.5 | -4.0 | -1 | -1.5 | -2 |
| wheel_power | -1e-05 | -0.0001 | -3e-05 | -5e-05 | -5e-05 |
| wheel_vel | -2e-06 | -1e-05 | -5e-06 | -7.5e-06 | -6e-06 |



| 地形 | 占比 | 模式 | 最低档vx | 最终vx | wz范围配置 | 高度 |
|---|---|---|---|---|---|---|
| flat | 0.3 | motion | [0.0, 2.7] | [0.0, 2.7] | [-5.0, 5.0] | [0.2, 0.43885688] |
| up_one | 0.1 | traverse | [0.3, 0.6] | [0.5, 1.5] | [-0.1, 0.1] | [0.22, 0.34] |
| down_one | 0.1 | traverse | [0.3, 0.6] | [0.5, 1.5] | [-0.1, 0.1] | [0.22, 0.34] |
| mixed_one | 0.05 | traverse | [0.3, 0.6] | [0.5, 1.5] | [-0.1, 0.1] | [0.22, 0.34] |
| mixed_fast | 0.05 | traverse | [0.6, 1.0] | [1.5, 2.7] | [-0.1, 0.1] | [0.22, 0.34] |
| up_two | 0.05 | traverse | [0.3, 0.6] | [0.5, 1.5] | [-0.1, 0.1] | [0.22, 0.34] |
| down_two | 0.05 | traverse | [0.3, 0.6] | [0.5, 1.5] | [-0.1, 0.1] | [0.22, 0.34] |
| mixed_two | 0.1 | traverse | [0.3, 0.6] | [0.5, 1.5] | [-0.1, 0.1] | [0.22, 0.34] |
| grid | 0.1 | free | [0.25, 0.5] | [0.3, 1.2] | [0.5, 2.0] | [0.22, 0.38] |
| slope | 0.05 | traverse | [0.25, 0.6] | [0.4, 1.5] | [-0.1, 0.1] | [0.24, 0.34] |
| rough | 0.05 | free | [0.25, 0.5] | [0.3, 1.5] | [0.5, 2.0] | [0.22, 0.38] |



<details markdown="1"><summary>完整阶段设置：含事件/额外奖励、地形和状态阈值</summary>


| 字段 | 原值 |
|---|---|
| air_reset_probability | 0.0 |
| air_height_offset_m | [0.12, 0.42] |
| air_vx_range_m_s | [-2.5, 2.5] |
| air_tilt_rad | [0.1, 0.2] |
| air_vy_range_m_s | [-0.5, 0.5] |
| air_angular_velocity_rad_s | [0.05, 0.1, 0.5] |
| air_leg_length_range_m | [0.15, 0.35] |
| air_leg_angle_range_rad | [-0.7853981633974483, 0.7853981633974483] |
| air_command_limit_s | 3.0 |
| air_command_vx_limit_m_s | 2.5 |
| air_command_wz_limit_rad_s | 1.5707963267948966 |
| recovery_probability | 0.0 |
| terrain.tile_size_m | [8.0, 8.0] |
| terrain.rows | 8 |
| terrain.columns | 20 |
| terrain.step_height_range_m | [0.02, 0.24] |
| terrain.step_width_m | 0.8 |
| terrain.slope_angle_range_rad | [0.0, 0.4363323129985824] |
| terrain.rough_noise_range_m | [0.0, 0.03] |
| terrain.rough_noise_step_m | 0.005 |
| terrain.rough_downsampled_scale_m | 0.2 |
| terrain.heightfield_border_width_m | 1.0 |
| terrain.border_width_m | 5.0 |
| terrain.boundary_margin_m | 0.5 |
| terrain.spawn_x_m | 0.8 |
| terrain.entry_x_m | 2.4 |
| terrain.surface_x_range_m | [2.0, 6.2] |
| terrain.exit_x_m | 5.6 |
| terrain.finish_x_m | 6.6 |
| terrain.ground_thickness_m | 0.1 |
| terrain.seed | 42 |
| terrain.surface_resolution_m | 0.2 |
| terrain.grid.width_range_m | [0.08, 0.12] |
| terrain.grid.height_range_m | [0.025, 0.045] |
| terrain.grid.spacing_range_m | [0.55, 0.7] |
| terrain.grid.half_span_m | 3.8 |
| terrain.profiles.flat.proportion | 0.3 |
| terrain.profiles.flat.kind | flat |
| terrain.profiles.flat.step_count | 0 |
| terrain.profiles.flat.speed_range_m_s | [0.0, 2.7] |
| terrain.profiles.flat.command_mode | motion |
| terrain.profiles.flat.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.flat.yaw_range_rad_s | [-5.0, 5.0] |
| terrain.profiles.flat.height_range_m | [0.2, 0.43885688] |
| terrain.profiles.flat.start_speed_range_m_s | [0.0, 2.7] |
| terrain.profiles.up_one.proportion | 0.1 |
| terrain.profiles.up_one.kind | up |
| terrain.profiles.up_one.step_count | 1 |
| terrain.profiles.up_one.speed_range_m_s | [0.5, 1.5] |
| terrain.profiles.up_one.command_mode | traverse |
| terrain.profiles.up_one.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.up_one.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.up_one.height_range_m | [0.22, 0.34] |
| terrain.profiles.up_one.start_speed_range_m_s | [0.3, 0.6] |
| terrain.profiles.down_one.proportion | 0.1 |
| terrain.profiles.down_one.kind | down |
| terrain.profiles.down_one.step_count | 1 |
| terrain.profiles.down_one.speed_range_m_s | [0.5, 1.5] |
| terrain.profiles.down_one.command_mode | traverse |
| terrain.profiles.down_one.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.down_one.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.down_one.height_range_m | [0.22, 0.34] |
| terrain.profiles.down_one.start_speed_range_m_s | [0.3, 0.6] |
| terrain.profiles.mixed_one.proportion | 0.05 |
| terrain.profiles.mixed_one.kind | mixed |
| terrain.profiles.mixed_one.step_count | 1 |
| terrain.profiles.mixed_one.speed_range_m_s | [0.5, 1.5] |
| terrain.profiles.mixed_one.command_mode | traverse |
| terrain.profiles.mixed_one.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.mixed_one.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.mixed_one.height_range_m | [0.22, 0.34] |
| terrain.profiles.mixed_one.start_speed_range_m_s | [0.3, 0.6] |
| terrain.profiles.mixed_fast.proportion | 0.05 |
| terrain.profiles.mixed_fast.kind | mixed |
| terrain.profiles.mixed_fast.step_count | 1 |
| terrain.profiles.mixed_fast.speed_range_m_s | [1.5, 2.7] |
| terrain.profiles.mixed_fast.command_mode | traverse |
| terrain.profiles.mixed_fast.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.mixed_fast.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.mixed_fast.height_range_m | [0.22, 0.34] |
| terrain.profiles.mixed_fast.start_speed_range_m_s | [0.6, 1.0] |
| terrain.profiles.up_two.proportion | 0.05 |
| terrain.profiles.up_two.kind | up |
| terrain.profiles.up_two.step_count | 2 |
| terrain.profiles.up_two.speed_range_m_s | [0.5, 1.5] |
| terrain.profiles.up_two.command_mode | traverse |
| terrain.profiles.up_two.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.up_two.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.up_two.height_range_m | [0.22, 0.34] |
| terrain.profiles.up_two.start_speed_range_m_s | [0.3, 0.6] |
| terrain.profiles.down_two.proportion | 0.05 |
| terrain.profiles.down_two.kind | down |
| terrain.profiles.down_two.step_count | 2 |
| terrain.profiles.down_two.speed_range_m_s | [0.5, 1.5] |
| terrain.profiles.down_two.command_mode | traverse |
| terrain.profiles.down_two.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.down_two.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.down_two.height_range_m | [0.22, 0.34] |
| terrain.profiles.down_two.start_speed_range_m_s | [0.3, 0.6] |
| terrain.profiles.mixed_two.proportion | 0.1 |
| terrain.profiles.mixed_two.kind | mixed |
| terrain.profiles.mixed_two.step_count | 2 |
| terrain.profiles.mixed_two.speed_range_m_s | [0.5, 1.5] |
| terrain.profiles.mixed_two.command_mode | traverse |
| terrain.profiles.mixed_two.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.mixed_two.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.mixed_two.height_range_m | [0.22, 0.34] |
| terrain.profiles.mixed_two.start_speed_range_m_s | [0.3, 0.6] |
| terrain.profiles.grid.proportion | 0.1 |
| terrain.profiles.grid.kind | grid |
| terrain.profiles.grid.step_count | 0 |
| terrain.profiles.grid.speed_range_m_s | [0.3, 1.2] |
| terrain.profiles.grid.command_mode | free |
| terrain.profiles.grid.free_yaw_limit_range_rad_s | [0.5, 2.0] |
| terrain.profiles.grid.heading_yaw_limit_rad_s | 0.5 |
| terrain.profiles.grid.yaw_range_rad_s | [-0.3, 0.3] |
| terrain.profiles.grid.height_range_m | [0.22, 0.38] |
| terrain.profiles.grid.start_speed_range_m_s | [0.25, 0.5] |
| terrain.profiles.slope.proportion | 0.05 |
| terrain.profiles.slope.kind | slope |
| terrain.profiles.slope.step_count | 0 |
| terrain.profiles.slope.speed_range_m_s | [0.4, 1.5] |
| terrain.profiles.slope.command_mode | traverse |
| terrain.profiles.slope.heading_yaw_limit_rad_s | 0.5 |
| terrain.profiles.slope.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.slope.height_range_m | [0.24, 0.34] |
| terrain.profiles.slope.start_speed_range_m_s | [0.25, 0.6] |
| terrain.profiles.rough.proportion | 0.05 |
| terrain.profiles.rough.kind | rough |
| terrain.profiles.rough.step_count | 0 |
| terrain.profiles.rough.speed_range_m_s | [0.3, 1.5] |
| terrain.profiles.rough.command_mode | free |
| terrain.profiles.rough.free_yaw_limit_range_rad_s | [0.5, 2.0] |
| terrain.profiles.rough.heading_yaw_limit_rad_s | 0.5 |
| terrain.profiles.rough.yaw_range_rad_s | [-0.3, 0.3] |
| terrain.profiles.rough.height_range_m | [0.22, 0.38] |
| terrain.profiles.rough.start_speed_range_m_s | [0.25, 0.5] |
| terrain.rough_proportion | 0.05 |
| disturbance_phase | 2 |
| reward_overrides.track_height_wide | 1.0 |
| reward_overrides.action_rate | -0.002 |
| reward_overrides.action_smoothness_leg | -0.01 |
| reward_overrides.action_smoothness_wheel | -0.002 |
| reward_overrides.leg_joint_vel | -0.001 |
| reward_overrides.leg_joint_acc | -4e-07 |
| reward_overrides.wheel_vel | -2e-06 |
| reward_overrides.pitch_penalty | -2.0 |
| reward_overrides.vertical_velocity | -0.5 |
| reward_overrides.angular_xy | -0.05 |
| reward_overrides.joint_torque | -1e-05 |
| reward_overrides.wheel_power | -1e-05 |
| step_height_margin_m | 0.01 |
| step_height_clearance_range_m | [0.19, 0.27] |
| step_height_hold_s | 0.3 |
| course.episode_length_s | 30.0 |
| course.flat_curriculum.levels | [[0.2, 0.2, 0.45], [0.2, 0.2, 0.7], [0.35, 0.35, 0.7], [0.35, 0.35, 1.0], [0.5, 0.5, 1.0], [0.7, 0.7, 1.0], [0.85, 0.85, 1.0], [1.0, 1.0, 1.0]] |
| course.flat_curriculum.min_completed_episodes | 4096 |
| course.flat_curriculum.promote_rate | 0.6 |
| course.flat_curriculum.demote_rate | 0.2 |
| course.flat_curriculum.error_thresholds | [0.15, 0.25, 0.06] |
| course.flat_curriculum.relative_error | 0.25 |
| course.initial_speed_fraction | 0.4 |
| course.minimum_speed_fraction | 0.3 |
| course.speed_increment | 0.05 |
| course.speed_window_episodes | 256 |
| course.speed_promote_rate | 0.6 |
| course.speed_demote_rate | 0.3 |
| course.tracking_sigma | 0.5 |
| course.tracking_promote | 0.6 |
| course.tracking_demote | 0.4 |
| course.minimum_episode_s | 2.0 |
| course.tracking_warmup_s | 1.0 |
| course.reverse_probability | 0.25 |
| course.yaw_jitter_rad | 0.05 |
| course.heading_kp | 5.0 |
| course.segment_duration_s | [3.0, 7.0] |
| course.height_duration_s | [3.0, 7.0] |
| course.edge_clearance_m | 0.15 |
| course.finish_hold_s | 0.4 |
| course.finish_tilt_rad | 0.25 |
| course.finish_angular_rad_s | 0.5 |
| course.finish_speed_m_s | 0.15 |
| course.scan_resolution_m | 0.1 |
| course.scan_half_length_m | 1.0 |
| course.scan_half_width_m | 0.6 |
| course.scan_lane_half_width_m | 0.15 |
| course.scan_min_rays | 2 |
| course.edge_height_m | 0.04 |
| course.edge_gradient_excess_m | 0.025 |
| course.detection_distance_m | 0.6 |
| course.trigger_distance_m | 0.5 |
| course.detection_hold_s | 0.15 |
| course.contact_force_n | 20.0 |
| course.guide_body_regex | .*_guide_link |
| course.guide_contact_scale | 0.5 |
| course.min_flight_s | 0.02 |
| course.min_drop_m | 0.04 |
| course.impact_free_speed_m_s | 0.3 |
| course.impact_speed_scale_m_s | 1.0 |
| course.impact_clip | 4.0 |
| course.cushion_s | 0.15 |
| course.impact_weight | -0.5 |
| course.air_wheel_speed_weight | 2.0 |
| course.air_wheel_speed_sigma | 1.0 |
| course.yaw_deadzone_rad_s | 0.02 |
| course.heading_probability | 0.5 |
| course.traversal_hold_s | 0.15 |
| course.free_segment_probabilities | [0.15, 0.35, 0.2, 0.3] |
| course.free_surface_min_s | 3.0 |
| course.free_tracking_error_floor | [0.15, 0.3] |
| course.free_tracking_relative_error | 0.35 |
| course.free_tracking_promote | 0.5 |
| course.free_tracking_demote | 0.25 |
| course.motion_segment_probabilities | [0.25, 0.25, 0.25, 0.25] |
| course.small_turn_probability | 0.5 |
| course.small_turn_range_rad_s | [0.2, 1.0] |
| course.traversal_tilt_rad | 0.45 |
| course.traversal_angular_rad_s | 1.5 |
| course.traversal_height_error_m | 0.08 |
| terrain_reward_overrides.grid.pitch_penalty | -2.5 |
| terrain_reward_overrides.grid.angular_xy | -0.1 |
| terrain_reward_overrides.grid.vertical_velocity | -1 |
| terrain_reward_overrides.grid.action_rate | -0.005 |
| terrain_reward_overrides.grid.action_smoothness_leg | -0.025 |
| terrain_reward_overrides.grid.action_smoothness_wheel | -0.005 |
| terrain_reward_overrides.grid.leg_joint_vel | -0.0025 |
| terrain_reward_overrides.grid.leg_joint_acc | -1e-06 |
| terrain_reward_overrides.grid.wheel_vel | -5e-06 |
| terrain_reward_overrides.grid.joint_torque | -3e-05 |
| terrain_reward_overrides.grid.wheel_power | -3e-05 |
| terrain_reward_overrides.slope.pitch_penalty | -2.25 |
| terrain_reward_overrides.slope.angular_xy | -0.15 |
| terrain_reward_overrides.slope.vertical_velocity | -1.5 |
| terrain_reward_overrides.slope.action_rate | -0.0075 |
| terrain_reward_overrides.slope.action_smoothness_leg | -0.0375 |
| terrain_reward_overrides.slope.action_smoothness_wheel | -0.0075 |
| terrain_reward_overrides.slope.leg_joint_vel | -0.00375 |
| terrain_reward_overrides.slope.leg_joint_acc | -1.5e-06 |
| terrain_reward_overrides.slope.wheel_vel | -7.5e-06 |
| terrain_reward_overrides.slope.joint_torque | -5e-05 |
| terrain_reward_overrides.slope.wheel_power | -5e-05 |
| terrain_reward_overrides.rough.pitch_penalty | -2.75 |
| terrain_reward_overrides.rough.angular_xy | -0.15 |
| terrain_reward_overrides.rough.vertical_velocity | -2 |
| terrain_reward_overrides.rough.action_rate | -0.006 |
| terrain_reward_overrides.rough.action_smoothness_leg | -0.03 |
| terrain_reward_overrides.rough.action_smoothness_wheel | -0.006 |
| terrain_reward_overrides.rough.leg_joint_vel | -0.003 |
| terrain_reward_overrides.rough.leg_joint_acc | -1.2e-06 |
| terrain_reward_overrides.rough.wheel_vel | -6e-06 |
| terrain_reward_overrides.rough.joint_torque | -5e-05 |
| terrain_reward_overrides.rough.wheel_power | -5e-05 |
| spawn_xy_jitter_m.flat.x | [-1.0, 1.0] |
| spawn_xy_jitter_m.flat.y | [-1.0, 1.0] |
| spawn_xy_jitter_m.grid.x | [0.0, 0.3] |
| spawn_xy_jitter_m.grid.y | [-1.0, 1.0] |
| spawn_xy_jitter_m.rough.x | [0.0, 0.3] |
| spawn_xy_jitter_m.rough.y | [-1.0, 1.0] |
| spawn_footprint_margin_m | 0.55 |
| motion_reward_overrides.pitch_penalty | -3.0 |
| motion_reward_overrides.angular_xy | -0.2 |
| motion_reward_overrides.vertical_velocity | -4.0 |
| motion_reward_overrides.action_rate | -0.01 |
| motion_reward_overrides.action_smoothness_leg | -0.05 |
| motion_reward_overrides.action_smoothness_wheel | -0.01 |
| motion_reward_overrides.leg_joint_vel | -0.005 |
| motion_reward_overrides.leg_joint_acc | -2e-06 |
| motion_reward_overrides.wheel_vel | -1e-05 |
| motion_reward_overrides.joint_torque | -0.0001 |
| motion_reward_overrides.wheel_power | -0.0001 |


</details>


### recovery


| 奖励项 | 合并后权重 | 生效说明 |
|---|---|---|
| track_lin_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| lin_vel_error | -8.0 | 需再结合dt、状态mask、事件定义 |
| track_ang_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| ang_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_height | 1.0 | 需再结合dt、状态mask、事件定义 |
| track_height_wide | 2.0 | 需再结合dt、状态mask、事件定义 |
| height_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| flat_roll | 1.0 | 需再结合dt、状态mask、事件定义 |
| flat_pitch | 1.0 | 需再结合dt、状态mask、事件定义 |
| roll_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| pitch_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| vertical_velocity | -0.5 | 需再结合dt、状态mask、事件定义 |
| angular_xy | -0.05 | 需再结合dt、状态mask、事件定义 |
| no_fork | -1.0 | 需再结合dt、状态mask、事件定义 |
| no_fork_square | -1.0 | 需再结合dt、状态mask、事件定义 |
| undesired_contact | -4.0 | 需再结合dt、状态mask、事件定义 |
| stand_still | -2.0 | 需再结合dt、状态mask、事件定义 |
| joint_torque | -0.0001 | 需再结合dt、状态mask、事件定义 |
| wheel_power | -0.0001 | 需再结合dt、状态mask、事件定义 |
| action_rate | -0.002 | 需再结合dt、状态mask、事件定义 |
| leg_joint_vel | -0.001 | 需再结合dt、状态mask、事件定义 |
| leg_joint_acc | -4e-07 | 需再结合dt、状态mask、事件定义 |
| wheel_vel | -2e-06 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_leg | -0.01 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_wheel | -0.002 | 需再结合dt、状态mask、事件定义 |
| termination | -4.0 | 需再结合dt、状态mask、事件定义 |
| leg_symmetry | 0.0 | 关闭 |



<details markdown="1"><summary>完整阶段设置：含事件/额外奖励、地形和状态阈值</summary>


| 字段 | 原值 |
|---|---|
| air_reset_probability | 0.3 |
| air_height_offset_m | [0.12, 0.42] |
| air_vx_range_m_s | [-2.5, 2.5] |
| air_tilt_rad | [0.1, 0.2] |
| air_vy_range_m_s | [-0.5, 0.5] |
| air_angular_velocity_rad_s | [0.05, 0.1, 0.5] |
| air_leg_length_range_m | [0.15, 0.35] |
| air_leg_angle_range_rad | [-0.7853981633974483, 0.7853981633974483] |
| air_command_limit_s | 3.0 |
| air_command_vx_limit_m_s | 2.5 |
| air_command_wz_limit_rad_s | 1.5707963267948966 |
| recovery_probability | 0.15 |
| recovery_root_height_m | 0.25 |
| recovery_forward_probability | 0.4 |
| recovery_leg_length_m | [0.14, 0.36] |
| recovery_leg_height_m | [-0.06, 0.12] |
| recovery_forward_leg_height_m | [-0.06, 0.0] |
| rise_duration_s | 1.5 |
| zero_torque_s | 0.2 |
| recovery_timeout_s | 5.0 |
| disturbance_phase | 2 |
| reward_overrides.action_rate | -0.002 |
| reward_overrides.action_smoothness_leg | -0.01 |
| reward_overrides.action_smoothness_wheel | -0.002 |
| reward_overrides.leg_joint_vel | -0.001 |
| reward_overrides.leg_joint_acc | -4e-07 |
| reward_overrides.wheel_vel | -2e-06 |
| reward_overrides.pitch_penalty | -2.0 |
| reward_overrides.vertical_velocity | -0.5 |
| reward_overrides.angular_xy | -0.05 |
| terrain.tile_size_m | [8.0, 8.0] |
| terrain.rows | 8 |
| terrain.columns | 10 |
| terrain.flat_proportion | 0.3 |
| terrain.step_height_range_m | [0.02, 0.24] |
| terrain.step_width_m | 0.8 |
| terrain.slope_proportion | 0.1 |
| terrain.bump_proportion | 0.1 |
| terrain.slope_angle_range_rad | [0.0, 0.4363323129985824] |
| terrain.bump_height_range_m | [0.01, 0.07] |
| terrain.bump_spacing_m | 0.24 |
| terrain.bump_width_m | 0.12 |
| terrain.rough_proportion | 0.1 |
| terrain.rough_noise_range_m | [0.0, 0.03] |
| terrain.rough_noise_step_m | 0.005 |
| terrain.rough_downsampled_scale_m | 0.2 |
| terrain.heightfield_border_width_m | 1.0 |
| terrain.border_width_m | 5.0 |
| terrain.boundary_margin_m | 0.5 |
| stair_detection_distance_m | 0.5 |
| stair_detection_height_m | 0.05 |
| stair_false_positive | 0.1 |
| stair_false_negative | 0.1 |
| progress_weight | 1.0 |
| stuck_weight | -1.0 |
| impact_weight | -0.001 |
| stuck_window_s | 1.0 |
| stuck_distance_m | 0.05 |
| step_height_boost_m | 0.16 |
| step_height_hold_s | 2.0 |
| step_height_trigger_distance_m | 0.14 |


</details>


## config\reference\scut_p2.yaml

[配置来源](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/config/reference/scut_p2.yaml>)

| 字段 | 原值 |
|---|---|
| name | scut_p2_spin_reference |
| obs_version | 2 |
| hidden_dims | [256, 128, 64] |
| activation | elu |
| observation_scales.command | [1.0, 1.0, 1.0] |
| observation_scales.height | 5.0 |
| observation_scales.angular_velocity | 0.5 |
| observation_scales.gravity | 1.0 |
| observation_scales.joint_position | 1.0 |
| observation_scales.joint_velocity | 0.1 |
| action_scales | [0.5, 0.5, 10.0, 0.5, 0.5, 10.0] |
| action_clip | null（未配置/待填） |
| kp | [60, 60, 0, 60, 60, 0] |
| kd | [2, 2, 0.2, 2, 2, 0.2] |
| torque_limit_nm | [40, 40, 5, 40, 40, 5] |
| history_estimator.frames | 0 |
| history_estimator.hidden_dims | [128, 64] |
| policy_family | p2 |
| mode_semantics | ["zero", "spin", "translation_speed_m_s", "sin_heading_reference", "cos_heading_reference", "sin_reference_relative_body", "cos_reference_relative_body"] |
| guide_version | 2.2 |



<details markdown="1"><summary>完整training：命令/奖励参数/PPO/课程/评测/扰动</summary>


| 字段 | 原值 |
|---|---|
| seed | 42 |
| num_envs | 4096 |
| rollout_steps | 48 |
| max_iterations | 20000 |
| save_interval | 500 |
| episode_length_s | 40.0 |
| init_noise_std | 1.0 |
| reward_clip | 2.5 |
| history_estimator.learning_rate | 0.001 |
| history_estimator.velocity_loss_coef | 1.0 |
| history_estimator.contact_loss_coef | 1.0 |
| ppo.value_loss_coef | 4.0 |
| ppo.use_clipped_value_loss | true |
| ppo.clip_param | 0.2 |
| ppo.entropy_coef | 0.005 |
| ppo.num_learning_epochs | 5 |
| ppo.num_mini_batches | 4 |
| ppo.learning_rate | 0.0001 |
| ppo.schedule | adaptive |
| ppo.gamma | 0.995 |
| ppo.lam | 0.95 |
| ppo.desired_kl | 0.01 |
| ppo.max_grad_norm | 1.0 |
| commands.segment_duration_s | [3.0, 15.0] |
| commands.height_duration_s | [2.0, 6.0] |
| commands.vx_range_m_s | null（未配置/待填） |
| commands.wz_range_rad_s | null（未配置/待填） |
| commands.height_range_m | [0.2, 0.35] |
| commands.linear_slew_m_s2 | 2.0 |
| commands.angular_slew_rad_s2 | 10.0 |
| commands.height_slew_m_s | 0.1 |
| commands.segment_probabilities | [0.1, 0.25, 0.15, 0.25, 0.1, 0.15] |
| commands.dash_range_m_s | null（未配置/待填） |
| reward_parameters.linear_sigma | 0.5 |
| reward_parameters.angular_sigma | 0.25 |
| reward_parameters.height_sigma | 0.001 |
| reward_parameters.height_gate_full_error_m | 0.05 |
| reward_parameters.height_gate_zero_error_m | 0.1 |
| reward_parameters.roll_sigma | 0.01 |
| reward_parameters.pitch_sigma | 0.02 |
| reward_parameters.pitch_velocity_amplitude | 2.0 |
| reward_parameters.pitch_velocity_sigma | 3.0 |
| reward_parameters.pitch_velocity_offset | 2.0 |
| reward_parameters.fork_deadzone_m | 0.05 |
| reward_parameters.stand_deadzone | 0.1 |
| reward_parameters.contact_force_n | 3.0 |
| reward_parameters.spin_velocity_sigma | 0.25 |
| reward_parameters.spin_heading_sigma | 0.025 |
| reward_parameters.air_wheel_torque_sigma | 1.5 |
| reward_parameters.fork_square_scale | 5.0 |
| reward_parameters.leg_length_symmetry_scale | 10.0 |
| reward_parameters.height_wide_sigma | 0.025 |
| reward_parameters.spin_heading_square_scale | 4.0 |
| rewards.track_lin_vel | 0.0 |
| rewards.lin_vel_error | 0.0 |
| rewards.track_ang_vel | 1.0 |
| rewards.ang_vel_error | -0.1 |
| rewards.track_height | 1.0 |
| rewards.height_error | -1.0 |
| rewards.flat_roll | 1.0 |
| rewards.flat_pitch | 1.0 |
| rewards.roll_penalty | -2.0 |
| rewards.pitch_penalty | -2.0 |
| rewards.vertical_velocity | -0.5 |
| rewards.angular_xy | -0.05 |
| rewards.no_fork | -1.0 |
| rewards.no_fork_square | -1.0 |
| rewards.undesired_contact | -4.0 |
| rewards.stand_still | -1.0 |
| rewards.joint_torque | -1e-05 |
| rewards.wheel_power | -1e-05 |
| rewards.action_rate | -0.01 |
| rewards.termination | -4.0 |
| rewards.spin_velocity | 1.0 |
| rewards.spin_speed | 1.0 |
| rewards.spin_heading | 5.0 |
| rewards.spin_velocity_error | -0.2 |
| rewards.spin_speed_error | -0.2 |
| rewards.leg_symmetry | 0.0 |
| rewards.track_height_wide | 2.0 |
| rewards.spin_heading_error | -0.02 |
| rewards.leg_joint_vel | -0.005 |
| rewards.wheel_vel | -1e-05 |
| rewards.action_smoothness_leg | -0.05 |
| rewards.action_smoothness_wheel | -0.01 |
| evaluation.observation_delay_steps | 0 |
| evaluation.action_delay_steps | 0 |
| evaluation.duration_s | 30.0 |
| evaluation.settling_s | 1.0 |
| evaluation.episodes_per_case | 16 |
| evaluation.seed | 123 |
| evaluation.height_m | 0.22 |
| evaluation.vx_values_m_s | null（未配置/待填） |
| evaluation.wz_values_rad_s | null（未配置/待填） |
| evaluation.combined_commands | null（未配置/待填） |
| disturbance.baseline_evaluation_passed | false |
| disturbance.ramp_iterations | 3000 |
| disturbance.final_push_velocity_m_s | 1.25 |
| disturbance.collision_interval_s | [8.0, 15.0] |
| disturbance.collision_duration_s | 0.1 |
| disturbance.collision_force_range_n | [100.0, 300.0] |
| disturbance.lateral_probability | 0.8 |
| disturbance.phase2_start_iteration | null（未配置/待填） |
| air_rewards.joint_limit | -10.0 |
| air_rewards.wheel_center | 10.0 |
| air_rewards.wheel_center_sigma | 0.02 |
| air_rewards.wheel_torque | 20.0 |
| air_rewards.wheel_torque_sigma | 1.5 |
| air_rewards.wheel_speed_alignment | -10.0 |
| command_curriculum.min_completed_episodes | 4096 |
| command_curriculum.initial_fraction | 1.0 |
| command_curriculum.increment | 0.05 |
| command_curriculum.success_fraction | 0.8 |
| command_curriculum.velocity_error_threshold_m_s | null（未配置/待填） |
| command_curriculum.yaw_error_threshold_rad_s | null（未配置/待填） |
| transition_reset.probability | 0.0 |
| transition_reset.states_npz | null（未配置/待填） |


</details>


### spin


| 奖励项 | 合并后权重 | 生效说明 |
|---|---|---|
| track_lin_vel | 0.0 | 关闭 |
| lin_vel_error | 0.0 | 关闭 |
| track_ang_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| ang_vel_error | -0.1 | 需再结合dt、状态mask、事件定义 |
| track_height | 1.0 | 需再结合dt、状态mask、事件定义 |
| height_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| flat_roll | 1.0 | 需再结合dt、状态mask、事件定义 |
| flat_pitch | 1.0 | 需再结合dt、状态mask、事件定义 |
| roll_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| pitch_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| vertical_velocity | -0.5 | 需再结合dt、状态mask、事件定义 |
| angular_xy | -0.05 | 需再结合dt、状态mask、事件定义 |
| no_fork | -1.0 | 需再结合dt、状态mask、事件定义 |
| no_fork_square | -1.0 | 需再结合dt、状态mask、事件定义 |
| undesired_contact | -4.0 | 需再结合dt、状态mask、事件定义 |
| stand_still | -1.0 | 需再结合dt、状态mask、事件定义 |
| joint_torque | -1e-05 | 需再结合dt、状态mask、事件定义 |
| wheel_power | -1e-05 | 需再结合dt、状态mask、事件定义 |
| action_rate | -0.01 | 需再结合dt、状态mask、事件定义 |
| termination | -4.0 | 需再结合dt、状态mask、事件定义 |
| spin_velocity | 1.0 | 需再结合dt、状态mask、事件定义 |
| spin_speed | 1.0 | 需再结合dt、状态mask、事件定义 |
| spin_heading | 5.0 | 需再结合dt、状态mask、事件定义 |
| spin_velocity_error | -0.2 | 需再结合dt、状态mask、事件定义 |
| spin_speed_error | -0.2 | 需再结合dt、状态mask、事件定义 |
| leg_symmetry | 0.0 | 关闭 |
| track_height_wide | 2.0 | 需再结合dt、状态mask、事件定义 |
| spin_heading_error | -0.02 | 需再结合dt、状态mask、事件定义 |
| leg_joint_vel | -0.005 | 需再结合dt、状态mask、事件定义 |
| wheel_vel | -1e-05 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_leg | -0.05 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_wheel | -0.01 | 需再结合dt、状态mask、事件定义 |



<details markdown="1"><summary>完整阶段设置：含事件/额外奖励、地形和状态阈值</summary>


| 字段 | 原值 |
|---|---|
| terrain.tile_size_m | [9.0, 9.0] |
| terrain.rows | 8 |
| terrain.columns | 10 |
| terrain.difficulty_range | [0.0, 1.0] |
| terrain.flat_proportion | 0.5 |
| terrain.rough_proportion | 0.3 |
| terrain.slope_proportion | 0.2 |
| terrain.rough_noise_range_m | [0.0, 0.03] |
| terrain.rough_noise_step_m | 0.005 |
| terrain.rough_downsampled_scale_m | 0.2 |
| terrain.heightfield_border_width_m | 1.0 |
| terrain.border_width_m | 5.0 |
| terrain.boundary_margin_m | 0.5 |
| terrain.slope_angle_range_rad | [-0.1, 0.1] |
| translation_speed_range_m_s | [0.0, 0.75] |
| spin_low_range_rad_s | [7.5398223686155035, 9.42477796076938] |
| spin_high_range_rad_s | [9.42477796076938, 11.309733552923255] |
| reference_frame | fixed_world_yaw |
| reference_yaw_rad | 0.0 |
| disturbance_phase | 1 |


</details>


## active_fd012a9_revision7

[配置来源](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/runs/stairs_viewer/fd012a9_latest/params/policy_meta.yaml>)

| 字段 | 原值 |
|---|---|
| name | scut_p1_latest_from_scratch |
| obs_version | 2 |
| hidden_dims | [256, 128, 64] |
| activation | elu |
| observation_scales.command | [1.0, 1.0, 1.0] |
| observation_scales.height | 5.0 |
| observation_scales.angular_velocity | 0.5 |
| observation_scales.gravity | 1.0 |
| observation_scales.joint_position | 1.0 |
| observation_scales.joint_velocity | 0.1 |
| action_scales | [0.5, 0.5, 10.0, 0.5, 0.5, 10.0] |
| action_clip | null（未配置/待填） |
| kp | [60, 60, 0, 60, 60, 0] |
| kd | [2, 2, 0.2, 2, 2, 0.2] |
| torque_limit_nm | [40, 40, 5, 40, 40, 5] |
| history_estimator.frames | 0 |
| history_estimator.hidden_dims | [128, 64] |
| policy_family | p1 |
| mode_semantics | ["normal", "stair", "zero", "recover", "zero", "zero", "zero"] |
| guide_version | 2.2 |
| reference_notes | P1-flat baseline only. Ranges/classifier thresholds are simulation design choices. Other stages retain their readiness requirements. |



<details markdown="1"><summary>完整training：命令/奖励参数/PPO/课程/评测/扰动</summary>


| 字段 | 原值 |
|---|---|
| seed | 42 |
| num_envs | 4096 |
| rollout_steps | 48 |
| max_iterations | 20000 |
| save_interval | 200 |
| episode_length_s | 20.0 |
| init_noise_std | 0.35 |
| reward_clip | 2.5 |
| history_estimator.learning_rate | 0.001 |
| history_estimator.velocity_loss_coef | 1.0 |
| history_estimator.contact_loss_coef | 1.0 |
| ppo.value_loss_coef | 4.0 |
| ppo.use_clipped_value_loss | true |
| ppo.clip_param | 0.2 |
| ppo.entropy_coef | 0.005 |
| ppo.num_learning_epochs | 5 |
| ppo.num_mini_batches | 4 |
| ppo.learning_rate | 0.0001 |
| ppo.schedule | adaptive |
| ppo.gamma | 0.995 |
| ppo.lam | 0.95 |
| ppo.desired_kl | 0.01 |
| ppo.max_grad_norm | 1.0 |
| commands.segment_duration_s | [3.0, 15.0] |
| commands.height_duration_s | [2.0, 6.0] |
| commands.vx_range_m_s | [-2.7, 2.7] |
| commands.wz_range_rad_s | [-5.0, 5.0] |
| commands.height_range_m | [0.2, 0.35] |
| commands.linear_slew_m_s2 | 2.0 |
| commands.angular_slew_rad_s2 | 10.0 |
| commands.height_slew_m_s | 0.1 |
| commands.segment_probabilities | [0.1, 0.25, 0.15, 0.25, 0.1, 0.15] |
| commands.dash_range_m_s | [-3.0, 3.0] |
| commands.combined_wz_limit_rad_s | 3.0 |
| reward_parameters.linear_sigma | 0.5 |
| reward_parameters.angular_sigma | 0.25 |
| reward_parameters.height_sigma | 0.001 |
| reward_parameters.height_wide_sigma | 0.025 |
| reward_parameters.height_gate_full_error_m | 0.05 |
| reward_parameters.height_gate_zero_error_m | 0.1 |
| reward_parameters.roll_sigma | 0.01 |
| reward_parameters.pitch_sigma | 0.02 |
| reward_parameters.pitch_velocity_amplitude | 1.0 |
| reward_parameters.pitch_velocity_sigma | 4.0 |
| reward_parameters.pitch_velocity_offset | 3.0 |
| reward_parameters.fork_deadzone_m | 0.05 |
| reward_parameters.stand_deadzone | 0.1 |
| reward_parameters.contact_force_n | 3.0 |
| reward_parameters.spin_velocity_sigma | 0.25 |
| reward_parameters.spin_heading_sigma | 0.025 |
| reward_parameters.air_wheel_torque_sigma | 1.5 |
| reward_parameters.fork_square_scale | 5.0 |
| reward_parameters.leg_length_symmetry_scale | 10.0 |
| rewards.track_lin_vel | 1.0 |
| rewards.lin_vel_error | -8.0 |
| rewards.track_ang_vel | 1.0 |
| rewards.ang_vel_error | -1.0 |
| rewards.track_height | 1.0 |
| rewards.track_height_wide | 2.0 |
| rewards.height_error | -1.0 |
| rewards.flat_roll | 1.0 |
| rewards.flat_pitch | 1.0 |
| rewards.roll_penalty | -2.0 |
| rewards.pitch_penalty | -3.0 |
| rewards.vertical_velocity | -4.0 |
| rewards.angular_xy | -0.2 |
| rewards.no_fork | -1.0 |
| rewards.no_fork_square | -1.0 |
| rewards.undesired_contact | -4.0 |
| rewards.stand_still | -2.0 |
| rewards.joint_torque | -0.0001 |
| rewards.wheel_power | -0.0001 |
| rewards.action_rate | -0.01 |
| rewards.leg_joint_vel | -0.005 |
| rewards.leg_joint_acc | -2e-06 |
| rewards.wheel_vel | -1e-05 |
| rewards.action_smoothness_leg | -0.05 |
| rewards.action_smoothness_wheel | -0.01 |
| rewards.termination | -4.0 |
| rewards.leg_symmetry | 0.0 |
| evaluation.flat_suite.height_samples | 3 |
| evaluation.flat_suite.speed_fractions | [0.25, 0.5, 1.0] |
| evaluation.flat_suite.combined_fractions | [0.5, 1.0] |
| evaluation.flat_suite.seeds | [123, 456] |
| evaluation.flat_suite.startup_s | 2.0 |
| evaluation.flat_suite.hold_s | 20.0 |
| evaluation.flat_suite.stand_window_s | 10.0 |
| evaluation.flat_suite.transition_settling_s | 2.0 |
| evaluation.flat_suite.stable_hold_s | 0.5 |
| evaluation.flat_suite.recovery_deadline_s | 3.0 |
| evaluation.flat_suite.push_after_s | 4.0 |
| evaluation.flat_suite.push_velocity_m_s | 0.25 |
| evaluation.flat_suite.delay_command_fraction | 0.5 |
| evaluation.flat_suite.delay_pairs_steps | [[3, 3], [8, 5]] |
| evaluation.flat_suite.trace_stride | 5 |
| evaluation.flat_suite.acceptance.stand_drift_m | 0.2 |
| evaluation.flat_suite.acceptance.tilt_p95_rad | 0.17453292519943295 |
| evaluation.flat_suite.acceptance.contact_fraction | 0.01 |
| evaluation.observation_delay_steps | 5 |
| evaluation.action_delay_steps | 4 |
| evaluation.duration_s | 10.0 |
| evaluation.settling_s | 1.0 |
| evaluation.episodes_per_case | 16 |
| evaluation.seed | 123 |
| evaluation.height_m | 0.22 |
| evaluation.vx_values_m_s | [-2.0, -1.0, -0.5, 0, 0.5, 1.0, 2.0] |
| evaluation.wz_values_rad_s | [-4.0, -2.0, -1.0, 1.0, 2.0, 4.0] |
| evaluation.combined_commands | [[1.0, 0, 1.0], [-1.0, 0, -1.0]] |
| disturbance.baseline_evaluation_passed | true |
| disturbance.ramp_iterations | 3000 |
| disturbance.final_push_velocity_m_s | 1.25 |
| disturbance.collision_interval_s | [8.0, 15.0] |
| disturbance.collision_duration_s | 0.1 |
| disturbance.collision_force_range_n | [100.0, 300.0] |
| disturbance.lateral_probability | 0.8 |
| disturbance.phase2_start_iteration | 4000 |
| air_rewards.joint_limit | -10.0 |
| air_rewards.wheel_center | 10.0 |
| air_rewards.wheel_center_sigma | 0.02 |
| air_rewards.wheel_torque | 20.0 |
| air_rewards.wheel_torque_sigma | 1.5 |
| air_rewards.wheel_speed_alignment | -10.0 |
| command_curriculum.min_completed_episodes | 4096 |
| command_curriculum.initial_fraction | 0.4 |
| command_curriculum.increment | 0.05 |
| command_curriculum.success_fraction | 0.75 |
| command_curriculum.velocity_error_threshold_m_s | 0.1 |
| command_curriculum.yaw_error_threshold_rad_s | 0.1 |
| command_curriculum.relative_error | 0.25 |
| command_curriculum.height_error_threshold_m | 0.05 |
| height_wide_anneal.final_weight | 0.5 |
| height_wide_anneal.start_iteration | 2000 |
| height_wide_anneal.ramp_iterations | 500 |
| transition_reset.probability | 0.0 |
| transition_reset.states_npz | null（未配置/待填） |


</details>


### flat


| 奖励项 | 合并后权重 | 生效说明 |
|---|---|---|
| track_lin_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| lin_vel_error | -8.0 | 需再结合dt、状态mask、事件定义 |
| track_ang_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| ang_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_height | 1.0 | 需再结合dt、状态mask、事件定义 |
| track_height_wide | 2.0 | 需再结合dt、状态mask、事件定义 |
| height_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| flat_roll | 1.0 | 需再结合dt、状态mask、事件定义 |
| flat_pitch | 1.0 | 需再结合dt、状态mask、事件定义 |
| roll_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| pitch_penalty | -3.0 | 需再结合dt、状态mask、事件定义 |
| vertical_velocity | -4.0 | 需再结合dt、状态mask、事件定义 |
| angular_xy | -0.2 | 需再结合dt、状态mask、事件定义 |
| no_fork | -1.0 | 需再结合dt、状态mask、事件定义 |
| no_fork_square | -1.0 | 需再结合dt、状态mask、事件定义 |
| undesired_contact | -4.0 | 需再结合dt、状态mask、事件定义 |
| stand_still | -2.0 | 需再结合dt、状态mask、事件定义 |
| joint_torque | -0.0001 | 需再结合dt、状态mask、事件定义 |
| wheel_power | -0.0001 | 需再结合dt、状态mask、事件定义 |
| action_rate | -0.01 | 需再结合dt、状态mask、事件定义 |
| leg_joint_vel | -0.005 | 需再结合dt、状态mask、事件定义 |
| leg_joint_acc | -2e-06 | 需再结合dt、状态mask、事件定义 |
| wheel_vel | -1e-05 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_leg | -0.05 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_wheel | -0.01 | 需再结合dt、状态mask、事件定义 |
| termination | -4.0 | 需再结合dt、状态mask、事件定义 |
| leg_symmetry | 0.0 | 关闭 |



<details markdown="1"><summary>完整阶段设置：含事件/额外奖励、地形和状态阈值</summary>


| 字段 | 原值 |
|---|---|
| air_reset_probability | 0.0 |
| recovery_probability | 0.0 |
| disturbance_phase | 1 |
| reward_overrides | {} |


</details>


### landing


| 奖励项 | 合并后权重 | 生效说明 |
|---|---|---|
| track_lin_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| lin_vel_error | -8.0 | 需再结合dt、状态mask、事件定义 |
| track_ang_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| ang_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_height | 1.0 | 需再结合dt、状态mask、事件定义 |
| track_height_wide | 1.5 | 需再结合dt、状态mask、事件定义 |
| height_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| flat_roll | 1.0 | 需再结合dt、状态mask、事件定义 |
| flat_pitch | 1.0 | 需再结合dt、状态mask、事件定义 |
| roll_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| pitch_penalty | -3.0 | 需再结合dt、状态mask、事件定义 |
| vertical_velocity | -4.0 | 需再结合dt、状态mask、事件定义 |
| angular_xy | -0.2 | 需再结合dt、状态mask、事件定义 |
| no_fork | -1.0 | 需再结合dt、状态mask、事件定义 |
| no_fork_square | -1.0 | 需再结合dt、状态mask、事件定义 |
| undesired_contact | -4.0 | 需再结合dt、状态mask、事件定义 |
| stand_still | -2.0 | 需再结合dt、状态mask、事件定义 |
| joint_torque | -0.0001 | 需再结合dt、状态mask、事件定义 |
| wheel_power | -0.0001 | 需再结合dt、状态mask、事件定义 |
| action_rate | -0.002 | 需再结合dt、状态mask、事件定义 |
| leg_joint_vel | -0.001 | 需再结合dt、状态mask、事件定义 |
| leg_joint_acc | -4e-07 | 需再结合dt、状态mask、事件定义 |
| wheel_vel | -2e-06 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_leg | -0.01 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_wheel | -0.002 | 需再结合dt、状态mask、事件定义 |
| termination | -4.0 | 需再结合dt、状态mask、事件定义 |
| leg_symmetry | 0.0 | 关闭 |



<details markdown="1"><summary>完整阶段设置：含事件/额外奖励、地形和状态阈值</summary>


| 字段 | 原值 |
|---|---|
| landing_reward.progress_budget | 0.75 |
| landing_reward.success_bonus | 1.5 |
| landing_reward.failure_cost | 1.0 |
| landing_reward.contact_force_n | 3.0 |
| landing_reward.support_force_n | 20.0 |
| landing_reward.contact_timeout_s | 2.0 |
| landing_reward.settle_support_s | 0.1 |
| landing_reward.cushion_max_s | 0.5 |
| landing_reward.window_s | 3.0 |
| landing_reward.stable_s | 0.5 |
| landing_reward.tilt_rad | 0.17453292519943295 |
| landing_reward.angular_xy_rad_s | 0.5 |
| landing_reward.vertical_velocity_m_s | 0.2 |
| landing_reward.height_error_m | 0.05 |
| landing_reward.wheel_center_weight | 4.0 |
| landing_reward.wheel_center_sigma | 0.02 |
| landing_reward.wheel_speed_weight | 6.0 |
| landing_reward.wheel_speed_sigma | 1.0 |
| landing_reward.contact_multiplier | 8.0 |
| landing_reward.guide_body_regex | .*_guide_link |
| landing_reward.guide_hard_speed_m_s | 1.0 |
| landing_reward.guide_speed_cost | 0.5 |
| landing_reward.leg_extension_weight | 3.0 |
| landing_reward.leg_extension_target_m | 0.28 |
| landing_reward.leg_extension_scale_m | 0.1 |
| landing_diagnostics.first_contact_force_n | 3.0 |
| landing_diagnostics.support_force_n | 20.0 |
| landing_diagnostics.first_contact_timeout_s | 2.0 |
| landing_diagnostics.observation_window_s | 3.0 |
| landing_diagnostics.stable_duration_s | 0.5 |
| landing_diagnostics.touchdown_difference_s | 0.05 |
| landing_diagnostics.tilt_rad | 0.17453292519943295 |
| landing_diagnostics.angular_xy_rad_s | 0.5 |
| landing_diagnostics.vertical_velocity_m_s | 0.2 |
| landing_diagnostics.height_error_m | 0.05 |
| air_reset_probability | 0.4 |
| air_height_offset_m | [0.12, 0.42] |
| air_vx_range_m_s | [-2.5, 2.5] |
| air_tilt_rad | [0.1, 0.2] |
| air_vy_range_m_s | [-0.5, 0.5] |
| air_angular_velocity_rad_s | [0.05, 0.1, 0.5] |
| air_leg_length_range_m | [0.15, 0.35] |
| air_leg_angle_range_rad | [-0.7853981633974483, 0.7853981633974483] |
| air_command_limit_s | 3.0 |
| air_command_vx_limit_m_s | 2.5 |
| air_command_wz_limit_rad_s | 1.5707963267948966 |
| air_vx_command_probability | 0.8 |
| air_vx_command_noise_m_s | 0.3 |
| air_height_curriculum.levels_m | [0.2, 0.24, 0.28, 0.32, 0.36, 0.42] |
| air_height_curriculum.min_events | 1024 |
| air_height_curriculum.success_rate | 0.8 |
| command_curriculum_landing_gate.min_events | 256 |
| command_curriculum_landing_gate.success_rate | 0.75 |
| recovery_probability | 0.0 |
| disturbance_phase | 1 |
| reward_overrides.track_height_wide | 1.5 |
| reward_overrides.action_rate | -0.002 |
| reward_overrides.action_smoothness_leg | -0.01 |
| reward_overrides.action_smoothness_wheel | -0.002 |
| reward_overrides.leg_joint_vel | -0.001 |
| reward_overrides.leg_joint_acc | -4e-07 |
| reward_overrides.wheel_vel | -2e-06 |


</details>


### stairs


| 奖励项 | 合并后权重 | 生效说明 |
|---|---|---|
| track_lin_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| lin_vel_error | -8.0 | 需再结合dt、状态mask、事件定义 |
| track_ang_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| ang_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_height | 1.0 | 需再结合dt、状态mask、事件定义 |
| track_height_wide | 1.0 | 需再结合dt、状态mask、事件定义 |
| height_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| flat_roll | 1.0 | 需再结合dt、状态mask、事件定义 |
| flat_pitch | 1.0 | 需再结合dt、状态mask、事件定义 |
| roll_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| pitch_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| vertical_velocity | -0.5 | 需再结合dt、状态mask、事件定义 |
| angular_xy | -0.05 | 需再结合dt、状态mask、事件定义 |
| no_fork | -1.0 | 需再结合dt、状态mask、事件定义 |
| no_fork_square | -1.0 | 需再结合dt、状态mask、事件定义 |
| undesired_contact | -4.0 | 需再结合dt、状态mask、事件定义 |
| stand_still | -2.0 | 需再结合dt、状态mask、事件定义 |
| joint_torque | -1e-05 | 需再结合dt、状态mask、事件定义 |
| wheel_power | -1e-05 | 需再结合dt、状态mask、事件定义 |
| action_rate | -0.002 | 需再结合dt、状态mask、事件定义 |
| leg_joint_vel | -0.001 | 需再结合dt、状态mask、事件定义 |
| leg_joint_acc | -4e-07 | 需再结合dt、状态mask、事件定义 |
| wheel_vel | -2e-06 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_leg | -0.01 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_wheel | -0.002 | 需再结合dt、状态mask、事件定义 |
| termination | -4.0 | 需再结合dt、状态mask、事件定义 |
| leg_symmetry | 0.0 | 关闭 |



| 项 | 台阶基值 | flat | grid | slope | rough |
|---|---|---|---|---|---|
| action_rate | -0.002 | -0.01 | -0.005 | -0.0075 | -0.006 |
| action_smoothness_leg | -0.01 | -0.05 | -0.025 | -0.0375 | -0.03 |
| action_smoothness_wheel | -0.002 | -0.01 | -0.005 | -0.0075 | -0.006 |
| ang_vel_error | -1.0 | -1.0 | -1.0 | -1.0 | -1.0 |
| angular_xy | -0.05 | -0.2 | -0.1 | -0.15 | -0.15 |
| flat_pitch | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| flat_roll | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| height_error | -1.0 | -1.0 | -1.0 | -1.0 | -1.0 |
| joint_torque | -1e-05 | -0.0001 | -3e-05 | -5e-05 | -5e-05 |
| leg_joint_acc | -4e-07 | -2e-06 | -1e-06 | -1.5e-06 | -1.2e-06 |
| leg_joint_vel | -0.001 | -0.005 | -0.0025 | -0.00375 | -0.003 |
| leg_symmetry | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| lin_vel_error | -8.0 | -8.0 | -8.0 | -8.0 | -8.0 |
| no_fork | -1.0 | -1.0 | -1.0 | -1.0 | -1.0 |
| no_fork_square | -1.0 | -1.0 | -1.0 | -1.0 | -1.0 |
| pitch_penalty | -2.0 | -3.0 | -2.5 | -2.25 | -2.75 |
| roll_penalty | -2.0 | -2.0 | -2.0 | -2.0 | -2.0 |
| stand_still | -2.0 | -2.0 | -2.0 | -2.0 | -2.0 |
| termination | -4.0 | -4.0 | -4.0 | -4.0 | -4.0 |
| track_ang_vel | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| track_height | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| track_height_wide | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| track_lin_vel | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| undesired_contact | -4.0 | -4.0 | -4.0 | -4.0 | -4.0 |
| vertical_velocity | -0.5 | -4.0 | -1 | -1.5 | -2 |
| wheel_power | -1e-05 | -0.0001 | -3e-05 | -5e-05 | -5e-05 |
| wheel_vel | -2e-06 | -1e-05 | -5e-06 | -7.5e-06 | -6e-06 |



| 地形 | 占比 | 模式 | 最低档vx | 最终vx | wz范围配置 | 高度 |
|---|---|---|---|---|---|---|
| flat | 0.3 | motion | [0.0, 2.7] | [0.0, 2.7] | [-5.0, 5.0] | [0.2, 0.43885687750064795] |
| up_one | 0.1 | traverse | [0.3, 0.6] | [0.5, 1.5] | [-0.1, 0.1] | [0.22, 0.34] |
| down_one | 0.1 | traverse | [0.3, 0.6] | [0.5, 1.5] | [-0.1, 0.1] | [0.22, 0.34] |
| mixed_one | 0.05 | traverse | [0.3, 0.6] | [0.5, 1.5] | [-0.1, 0.1] | [0.22, 0.34] |
| mixed_fast | 0.05 | traverse | [0.6, 1.0] | [1.5, 2.7] | [-0.1, 0.1] | [0.22, 0.34] |
| up_two | 0.05 | traverse | [0.3, 0.6] | [0.5, 1.5] | [-0.1, 0.1] | [0.22, 0.34] |
| down_two | 0.05 | traverse | [0.3, 0.6] | [0.5, 1.5] | [-0.1, 0.1] | [0.22, 0.34] |
| mixed_two | 0.1 | traverse | [0.3, 0.6] | [0.5, 1.5] | [-0.1, 0.1] | [0.22, 0.34] |
| grid | 0.1 | free | [0.25, 0.5] | [0.3, 1.2] | [0.5, 2.0] | [0.22, 0.38] |
| slope | 0.05 | traverse | [0.25, 0.6] | [0.4, 1.5] | [-0.1, 0.1] | [0.24, 0.34] |
| rough | 0.05 | free | [0.25, 0.5] | [0.3, 1.5] | [0.5, 2.0] | [0.22, 0.38] |



<details markdown="1"><summary>完整阶段设置：含事件/额外奖励、地形和状态阈值</summary>


| 字段 | 原值 |
|---|---|
| air_reset_probability | 0.0 |
| air_height_offset_m | [0.12, 0.42] |
| air_vx_range_m_s | [-2.5, 2.5] |
| air_tilt_rad | [0.1, 0.2] |
| air_vy_range_m_s | [-0.5, 0.5] |
| air_angular_velocity_rad_s | [0.05, 0.1, 0.5] |
| air_leg_length_range_m | [0.15, 0.35] |
| air_leg_angle_range_rad | [-0.7853981633974483, 0.7853981633974483] |
| air_command_limit_s | 3.0 |
| air_command_vx_limit_m_s | 2.5 |
| air_command_wz_limit_rad_s | 1.5707963267948966 |
| recovery_probability | 0.0 |
| terrain.tile_size_m | [8.0, 8.0] |
| terrain.rows | 8 |
| terrain.columns | 20 |
| terrain.step_height_range_m | [0.02, 0.24] |
| terrain.step_width_m | 0.8 |
| terrain.slope_angle_range_rad | [0.0, 0.4363323129985824] |
| terrain.rough_noise_range_m | [0.0, 0.03] |
| terrain.rough_noise_step_m | 0.005 |
| terrain.rough_downsampled_scale_m | 0.2 |
| terrain.heightfield_border_width_m | 1.0 |
| terrain.border_width_m | 5.0 |
| terrain.boundary_margin_m | 0.5 |
| terrain.spawn_x_m | 0.8 |
| terrain.entry_x_m | 2.4 |
| terrain.surface_x_range_m | [2.0, 6.2] |
| terrain.exit_x_m | 5.6 |
| terrain.finish_x_m | 6.6 |
| terrain.ground_thickness_m | 0.1 |
| terrain.seed | 42 |
| terrain.surface_resolution_m | 0.2 |
| terrain.grid.width_range_m | [0.08, 0.12] |
| terrain.grid.height_range_m | [0.025, 0.045] |
| terrain.grid.spacing_range_m | [0.55, 0.7] |
| terrain.grid.half_span_m | 3.8 |
| terrain.profiles.flat.proportion | 0.3 |
| terrain.profiles.flat.kind | flat |
| terrain.profiles.flat.step_count | 0 |
| terrain.profiles.flat.speed_range_m_s | [0.0, 2.7] |
| terrain.profiles.flat.command_mode | motion |
| terrain.profiles.flat.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.flat.yaw_range_rad_s | [-5.0, 5.0] |
| terrain.profiles.flat.height_range_m | [0.2, 0.43885687750064795] |
| terrain.profiles.flat.start_speed_range_m_s | [0.0, 2.7] |
| terrain.profiles.up_one.proportion | 0.1 |
| terrain.profiles.up_one.kind | up |
| terrain.profiles.up_one.step_count | 1 |
| terrain.profiles.up_one.speed_range_m_s | [0.5, 1.5] |
| terrain.profiles.up_one.command_mode | traverse |
| terrain.profiles.up_one.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.up_one.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.up_one.height_range_m | [0.22, 0.34] |
| terrain.profiles.up_one.start_speed_range_m_s | [0.3, 0.6] |
| terrain.profiles.down_one.proportion | 0.1 |
| terrain.profiles.down_one.kind | down |
| terrain.profiles.down_one.step_count | 1 |
| terrain.profiles.down_one.speed_range_m_s | [0.5, 1.5] |
| terrain.profiles.down_one.command_mode | traverse |
| terrain.profiles.down_one.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.down_one.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.down_one.height_range_m | [0.22, 0.34] |
| terrain.profiles.down_one.start_speed_range_m_s | [0.3, 0.6] |
| terrain.profiles.mixed_one.proportion | 0.05 |
| terrain.profiles.mixed_one.kind | mixed |
| terrain.profiles.mixed_one.step_count | 1 |
| terrain.profiles.mixed_one.speed_range_m_s | [0.5, 1.5] |
| terrain.profiles.mixed_one.command_mode | traverse |
| terrain.profiles.mixed_one.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.mixed_one.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.mixed_one.height_range_m | [0.22, 0.34] |
| terrain.profiles.mixed_one.start_speed_range_m_s | [0.3, 0.6] |
| terrain.profiles.mixed_fast.proportion | 0.05 |
| terrain.profiles.mixed_fast.kind | mixed |
| terrain.profiles.mixed_fast.step_count | 1 |
| terrain.profiles.mixed_fast.speed_range_m_s | [1.5, 2.7] |
| terrain.profiles.mixed_fast.command_mode | traverse |
| terrain.profiles.mixed_fast.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.mixed_fast.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.mixed_fast.height_range_m | [0.22, 0.34] |
| terrain.profiles.mixed_fast.start_speed_range_m_s | [0.6, 1.0] |
| terrain.profiles.up_two.proportion | 0.05 |
| terrain.profiles.up_two.kind | up |
| terrain.profiles.up_two.step_count | 2 |
| terrain.profiles.up_two.speed_range_m_s | [0.5, 1.5] |
| terrain.profiles.up_two.command_mode | traverse |
| terrain.profiles.up_two.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.up_two.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.up_two.height_range_m | [0.22, 0.34] |
| terrain.profiles.up_two.start_speed_range_m_s | [0.3, 0.6] |
| terrain.profiles.down_two.proportion | 0.05 |
| terrain.profiles.down_two.kind | down |
| terrain.profiles.down_two.step_count | 2 |
| terrain.profiles.down_two.speed_range_m_s | [0.5, 1.5] |
| terrain.profiles.down_two.command_mode | traverse |
| terrain.profiles.down_two.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.down_two.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.down_two.height_range_m | [0.22, 0.34] |
| terrain.profiles.down_two.start_speed_range_m_s | [0.3, 0.6] |
| terrain.profiles.mixed_two.proportion | 0.1 |
| terrain.profiles.mixed_two.kind | mixed |
| terrain.profiles.mixed_two.step_count | 2 |
| terrain.profiles.mixed_two.speed_range_m_s | [0.5, 1.5] |
| terrain.profiles.mixed_two.command_mode | traverse |
| terrain.profiles.mixed_two.heading_yaw_limit_rad_s | 1.0 |
| terrain.profiles.mixed_two.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.mixed_two.height_range_m | [0.22, 0.34] |
| terrain.profiles.mixed_two.start_speed_range_m_s | [0.3, 0.6] |
| terrain.profiles.grid.proportion | 0.1 |
| terrain.profiles.grid.kind | grid |
| terrain.profiles.grid.step_count | 0 |
| terrain.profiles.grid.speed_range_m_s | [0.3, 1.2] |
| terrain.profiles.grid.command_mode | free |
| terrain.profiles.grid.free_yaw_limit_range_rad_s | [0.5, 2.0] |
| terrain.profiles.grid.heading_yaw_limit_rad_s | 0.5 |
| terrain.profiles.grid.yaw_range_rad_s | [-0.3, 0.3] |
| terrain.profiles.grid.height_range_m | [0.22, 0.38] |
| terrain.profiles.grid.start_speed_range_m_s | [0.25, 0.5] |
| terrain.profiles.slope.proportion | 0.05 |
| terrain.profiles.slope.kind | slope |
| terrain.profiles.slope.step_count | 0 |
| terrain.profiles.slope.speed_range_m_s | [0.4, 1.5] |
| terrain.profiles.slope.command_mode | traverse |
| terrain.profiles.slope.heading_yaw_limit_rad_s | 0.5 |
| terrain.profiles.slope.yaw_range_rad_s | [-0.1, 0.1] |
| terrain.profiles.slope.height_range_m | [0.24, 0.34] |
| terrain.profiles.slope.start_speed_range_m_s | [0.25, 0.6] |
| terrain.profiles.rough.proportion | 0.05 |
| terrain.profiles.rough.kind | rough |
| terrain.profiles.rough.step_count | 0 |
| terrain.profiles.rough.speed_range_m_s | [0.3, 1.5] |
| terrain.profiles.rough.command_mode | free |
| terrain.profiles.rough.free_yaw_limit_range_rad_s | [0.5, 2.0] |
| terrain.profiles.rough.heading_yaw_limit_rad_s | 0.5 |
| terrain.profiles.rough.yaw_range_rad_s | [-0.3, 0.3] |
| terrain.profiles.rough.height_range_m | [0.22, 0.38] |
| terrain.profiles.rough.start_speed_range_m_s | [0.25, 0.5] |
| terrain.rough_proportion | 0.05 |
| disturbance_phase | 2 |
| reward_overrides.track_height_wide | 1.0 |
| reward_overrides.action_rate | -0.002 |
| reward_overrides.action_smoothness_leg | -0.01 |
| reward_overrides.action_smoothness_wheel | -0.002 |
| reward_overrides.leg_joint_vel | -0.001 |
| reward_overrides.leg_joint_acc | -4e-07 |
| reward_overrides.wheel_vel | -2e-06 |
| reward_overrides.pitch_penalty | -2.0 |
| reward_overrides.vertical_velocity | -0.5 |
| reward_overrides.angular_xy | -0.05 |
| reward_overrides.joint_torque | -1e-05 |
| reward_overrides.wheel_power | -1e-05 |
| step_height_margin_m | 0.01 |
| step_height_clearance_range_m | [0.19, 0.27] |
| step_height_hold_s | 0.3 |
| course.episode_length_s | 30.0 |
| course.initial_speed_fraction | 0.4 |
| course.minimum_speed_fraction | 0.3 |
| course.speed_increment | 0.05 |
| course.speed_window_episodes | 256 |
| course.speed_promote_rate | 0.6 |
| course.speed_demote_rate | 0.3 |
| course.tracking_sigma | 0.5 |
| course.tracking_promote | 0.6 |
| course.tracking_demote | 0.4 |
| course.minimum_episode_s | 2.0 |
| course.tracking_warmup_s | 1.0 |
| course.reverse_probability | 0.25 |
| course.yaw_jitter_rad | 0.05 |
| course.heading_kp | 5.0 |
| course.segment_duration_s | [3.0, 7.0] |
| course.height_duration_s | [3.0, 7.0] |
| course.edge_clearance_m | 0.15 |
| course.finish_hold_s | 0.4 |
| course.finish_tilt_rad | 0.25 |
| course.finish_angular_rad_s | 0.5 |
| course.finish_speed_m_s | 0.15 |
| course.scan_resolution_m | 0.1 |
| course.scan_half_length_m | 1.0 |
| course.scan_half_width_m | 0.6 |
| course.scan_lane_half_width_m | 0.15 |
| course.scan_min_rays | 2 |
| course.edge_height_m | 0.04 |
| course.edge_gradient_excess_m | 0.025 |
| course.detection_distance_m | 0.6 |
| course.trigger_distance_m | 0.5 |
| course.detection_hold_s | 0.15 |
| course.contact_force_n | 20.0 |
| course.guide_body_regex | .*_guide_link |
| course.guide_contact_scale | 0.5 |
| course.min_flight_s | 0.02 |
| course.min_drop_m | 0.04 |
| course.impact_free_speed_m_s | 0.3 |
| course.impact_speed_scale_m_s | 1.0 |
| course.impact_clip | 4.0 |
| course.cushion_s | 0.15 |
| course.impact_weight | -0.5 |
| course.air_wheel_speed_weight | 2.0 |
| course.air_wheel_speed_sigma | 1.0 |
| course.yaw_deadzone_rad_s | 0.02 |
| course.heading_probability | 0.5 |
| course.traversal_hold_s | 0.15 |
| course.free_segment_probabilities | [0.15, 0.35, 0.2, 0.3] |
| course.free_surface_min_s | 3.0 |
| course.free_tracking_error_floor | [0.1, 0.1] |
| course.free_tracking_relative_error | 0.25 |
| course.motion_segment_probabilities | [0.25, 0.25, 0.25, 0.25] |
| course.small_turn_probability | 0.5 |
| course.small_turn_range_rad_s | [0.2, 1.0] |
| course.traversal_tilt_rad | 0.45 |
| course.traversal_angular_rad_s | 1.5 |
| course.traversal_height_error_m | 0.08 |
| terrain_reward_overrides.grid.pitch_penalty | -2.5 |
| terrain_reward_overrides.grid.angular_xy | -0.1 |
| terrain_reward_overrides.grid.vertical_velocity | -1 |
| terrain_reward_overrides.grid.action_rate | -0.005 |
| terrain_reward_overrides.grid.action_smoothness_leg | -0.025 |
| terrain_reward_overrides.grid.action_smoothness_wheel | -0.005 |
| terrain_reward_overrides.grid.leg_joint_vel | -0.0025 |
| terrain_reward_overrides.grid.leg_joint_acc | -1e-06 |
| terrain_reward_overrides.grid.wheel_vel | -5e-06 |
| terrain_reward_overrides.grid.joint_torque | -3e-05 |
| terrain_reward_overrides.grid.wheel_power | -3e-05 |
| terrain_reward_overrides.slope.pitch_penalty | -2.25 |
| terrain_reward_overrides.slope.angular_xy | -0.15 |
| terrain_reward_overrides.slope.vertical_velocity | -1.5 |
| terrain_reward_overrides.slope.action_rate | -0.0075 |
| terrain_reward_overrides.slope.action_smoothness_leg | -0.0375 |
| terrain_reward_overrides.slope.action_smoothness_wheel | -0.0075 |
| terrain_reward_overrides.slope.leg_joint_vel | -0.00375 |
| terrain_reward_overrides.slope.leg_joint_acc | -1.5e-06 |
| terrain_reward_overrides.slope.wheel_vel | -7.5e-06 |
| terrain_reward_overrides.slope.joint_torque | -5e-05 |
| terrain_reward_overrides.slope.wheel_power | -5e-05 |
| terrain_reward_overrides.rough.pitch_penalty | -2.75 |
| terrain_reward_overrides.rough.angular_xy | -0.15 |
| terrain_reward_overrides.rough.vertical_velocity | -2 |
| terrain_reward_overrides.rough.action_rate | -0.006 |
| terrain_reward_overrides.rough.action_smoothness_leg | -0.03 |
| terrain_reward_overrides.rough.action_smoothness_wheel | -0.006 |
| terrain_reward_overrides.rough.leg_joint_vel | -0.003 |
| terrain_reward_overrides.rough.leg_joint_acc | -1.2e-06 |
| terrain_reward_overrides.rough.wheel_vel | -6e-06 |
| terrain_reward_overrides.rough.joint_torque | -5e-05 |
| terrain_reward_overrides.rough.wheel_power | -5e-05 |
| spawn_xy_jitter_m.flat.x | [-1.0, 1.0] |
| spawn_xy_jitter_m.flat.y | [-1.0, 1.0] |
| spawn_xy_jitter_m.grid.x | [0.0, 0.3] |
| spawn_xy_jitter_m.grid.y | [-1.0, 1.0] |
| spawn_xy_jitter_m.rough.x | [0.0, 0.3] |
| spawn_xy_jitter_m.rough.y | [-1.0, 1.0] |
| spawn_footprint_margin_m | 0.55 |
| motion_reward_overrides.pitch_penalty | -3.0 |
| motion_reward_overrides.angular_xy | -0.2 |
| motion_reward_overrides.vertical_velocity | -4.0 |
| motion_reward_overrides.action_rate | -0.01 |
| motion_reward_overrides.action_smoothness_leg | -0.05 |
| motion_reward_overrides.action_smoothness_wheel | -0.01 |
| motion_reward_overrides.leg_joint_vel | -0.005 |
| motion_reward_overrides.leg_joint_acc | -2e-06 |
| motion_reward_overrides.wheel_vel | -1e-05 |
| motion_reward_overrides.joint_torque | -0.0001 |
| motion_reward_overrides.wheel_power | -0.0001 |


</details>


### recovery


| 奖励项 | 合并后权重 | 生效说明 |
|---|---|---|
| track_lin_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| lin_vel_error | -8.0 | 需再结合dt、状态mask、事件定义 |
| track_ang_vel | 1.0 | 需再结合dt、状态mask、事件定义 |
| ang_vel_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| track_height | 1.0 | 需再结合dt、状态mask、事件定义 |
| track_height_wide | 2.0 | 需再结合dt、状态mask、事件定义 |
| height_error | -1.0 | 需再结合dt、状态mask、事件定义 |
| flat_roll | 1.0 | 需再结合dt、状态mask、事件定义 |
| flat_pitch | 1.0 | 需再结合dt、状态mask、事件定义 |
| roll_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| pitch_penalty | -2.0 | 需再结合dt、状态mask、事件定义 |
| vertical_velocity | -0.5 | 需再结合dt、状态mask、事件定义 |
| angular_xy | -0.05 | 需再结合dt、状态mask、事件定义 |
| no_fork | -1.0 | 需再结合dt、状态mask、事件定义 |
| no_fork_square | -1.0 | 需再结合dt、状态mask、事件定义 |
| undesired_contact | -4.0 | 需再结合dt、状态mask、事件定义 |
| stand_still | -2.0 | 需再结合dt、状态mask、事件定义 |
| joint_torque | -0.0001 | 需再结合dt、状态mask、事件定义 |
| wheel_power | -0.0001 | 需再结合dt、状态mask、事件定义 |
| action_rate | -0.002 | 需再结合dt、状态mask、事件定义 |
| leg_joint_vel | -0.001 | 需再结合dt、状态mask、事件定义 |
| leg_joint_acc | -4e-07 | 需再结合dt、状态mask、事件定义 |
| wheel_vel | -2e-06 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_leg | -0.01 | 需再结合dt、状态mask、事件定义 |
| action_smoothness_wheel | -0.002 | 需再结合dt、状态mask、事件定义 |
| termination | -4.0 | 需再结合dt、状态mask、事件定义 |
| leg_symmetry | 0.0 | 关闭 |



<details markdown="1"><summary>完整阶段设置：含事件/额外奖励、地形和状态阈值</summary>


| 字段 | 原值 |
|---|---|
| air_reset_probability | 0.3 |
| air_height_offset_m | [0.12, 0.42] |
| air_vx_range_m_s | [-2.5, 2.5] |
| air_tilt_rad | [0.1, 0.2] |
| air_vy_range_m_s | [-0.5, 0.5] |
| air_angular_velocity_rad_s | [0.05, 0.1, 0.5] |
| air_leg_length_range_m | [0.15, 0.35] |
| air_leg_angle_range_rad | [-0.7853981633974483, 0.7853981633974483] |
| air_command_limit_s | 3.0 |
| air_command_vx_limit_m_s | 2.5 |
| air_command_wz_limit_rad_s | 1.5707963267948966 |
| recovery_probability | 0.15 |
| recovery_root_height_m | 0.25 |
| recovery_forward_probability | 0.4 |
| recovery_leg_length_m | [0.14, 0.36] |
| recovery_leg_height_m | [-0.06, 0.12] |
| recovery_forward_leg_height_m | [-0.06, 0.0] |
| rise_duration_s | 1.5 |
| zero_torque_s | 0.2 |
| recovery_timeout_s | 5.0 |
| disturbance_phase | 2 |
| reward_overrides.action_rate | -0.002 |
| reward_overrides.action_smoothness_leg | -0.01 |
| reward_overrides.action_smoothness_wheel | -0.002 |
| reward_overrides.leg_joint_vel | -0.001 |
| reward_overrides.leg_joint_acc | -4e-07 |
| reward_overrides.wheel_vel | -2e-06 |
| reward_overrides.pitch_penalty | -2.0 |
| reward_overrides.vertical_velocity | -0.5 |
| reward_overrides.angular_xy | -0.05 |
| terrain.tile_size_m | [8.0, 8.0] |
| terrain.rows | 8 |
| terrain.columns | 10 |
| terrain.flat_proportion | 0.3 |
| terrain.step_height_range_m | [0.02, 0.24] |
| terrain.step_width_m | 0.8 |
| terrain.slope_proportion | 0.1 |
| terrain.bump_proportion | 0.1 |
| terrain.slope_angle_range_rad | [0.0, 0.4363323129985824] |
| terrain.bump_height_range_m | [0.01, 0.07] |
| terrain.bump_spacing_m | 0.24 |
| terrain.bump_width_m | 0.12 |
| terrain.rough_proportion | 0.1 |
| terrain.rough_noise_range_m | [0.0, 0.03] |
| terrain.rough_noise_step_m | 0.005 |
| terrain.rough_downsampled_scale_m | 0.2 |
| terrain.heightfield_border_width_m | 1.0 |
| terrain.border_width_m | 5.0 |
| terrain.boundary_margin_m | 0.5 |
| stair_detection_distance_m | 0.5 |
| stair_detection_height_m | 0.05 |
| stair_false_positive | 0.1 |
| stair_false_negative | 0.1 |
| progress_weight | 1.0 |
| stuck_weight | -1.0 |
| impact_weight | -0.001 |
| stuck_window_s | 1.0 |
| stuck_distance_m | 0.05 |
| step_height_boost_m | 0.16 |
| step_height_hold_s | 2.0 |
| step_height_trigger_distance_m | 0.14 |


</details>


## 基础rewards之外的追加/替换

flat宽核按height_wide_anneal退火。landing事件progress/outcome/guide_contact不乘dt，飞行轮居中/轮速/伸腿为有界非正项。stairs另有stair_impact事件、air_wheel_speed连续罚、air_joint_limits。recovery保留progress/stuck、连续髋力矩impact；recovery/P3另加air_wheel_torque、air_wheel_center、air_wheel_alignment、air_joint_limits。tunnel越过结果+5、障碍接触-5/s、顶面接触-10/s。完整生效代码见定义附录。


## 机器人合同 robot.yaml
[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/config/robot.yaml>)
<details markdown="1"><summary>完整机械/随机化/观测clip/延迟/终止合同</summary>


| 字段 | 原值 |
|---|---|
| name | srm_wheelleg_nogimbal |
| variant | chassis_only |
| control_hz | 500 |
| policy_hz | 100 |
| wheel_reduction_ratio | 15.76 |
| spring_nominal_force_n | 450.0 |
| spring_stroke_m | 0.075 |
| joint_order | ["left_front", "left_rear", "left_wheel", "right_front", "right_rear", "right_wheel"] |
| leg_indices | [0, 1, 3, 4] |
| wheel_indices | [2, 5] |
| q_default_rad | [null, null, null, null, null, null] |
| q_zero_offset_rad | [null, null, null, null, null, null] |
| motor_direction | [null, null, null, null, null, null] |
| can_bus | [1, 1, 1, 2, 2, 2] |
| pending_measurements.cad_closed_chain_geometry | null（未配置/待填） |
| pending_measurements.chassis_mass_com_inertia | null（未配置/待填） |
| pending_measurements.wheel_radius_m | null（未配置/待填） |
| pending_measurements.leg_joint_limits_rad | null（未配置/待填） |
| pending_measurements.motor_ids_and_protocol_readback | null（未配置/待填） |
| pending_measurements.imu_mounting_rotation | null（未配置/待填） |
| pending_measurements.hip_torque_calibration_and_envelope | null（未配置/待填） |
| pending_measurements.wheel_torque_calibration_and_envelope | null（未配置/待填） |
| pending_measurements.motor_sweep_and_held_out_validation | null（未配置/待填） |
| pending_measurements.spring_left_f0_k_hysteresis_damping | null（未配置/待填） |
| pending_measurements.spring_right_f0_k_hysteresis_damping | null（未配置/待填） |
| pending_measurements.measured_sensor_and_action_delay | null（未配置/待填） |
| pending_measurements.power_controller_limits | null（未配置/待填） |
| asset.usd_path | null（未配置/待填） |
| asset.active_joint_names | [null, null, null, null, null, null] |
| asset.spring_joint_names | [null, null] |
| asset.passive_joint_names | null（未配置/待填） |
| asset.wheel_body_names | [null, null] |
| asset.base_body_name | null（未配置/待填） |
| asset.undesired_contact_body_names | null（未配置/待填） |
| asset.termination_contact_body_names | null（未配置/待填） |
| asset.initial_root_position_m | [0.0, 0.0, null] |
| asset.initial_joint_positions_rad | null（未配置/待填） |
| asset.collision_body_names | null（未配置/待填） |
| training.observation_clip.command | [-100.0, 100.0] |
| training.observation_clip.height | [0.0, 1.0] |
| training.observation_clip.angular_velocity | [-100.0, 100.0] |
| training.observation_clip.gravity | [-100.0, 100.0] |
| training.observation_clip.joint_position | [-100.0, 100.0] |
| training.observation_clip.joint_velocity | [-200.0, 200.0] |
| training.observation_clip.previous_action | [-100.0, 100.0] |
| training.observation_clip.mode | [-100.0, 100.0] |
| training.observation_clip.base_linear_velocity | [-100.0, 100.0] |
| training.observation_clip.base_height | [-10.0, 10.0] |
| training.observation_clip.torque | [-100.0, 100.0] |
| training.observation_clip.wheel_linear_velocity | [-100.0, 100.0] |
| training.observation_clip.kp | [-100.0, 100.0] |
| training.observation_clip.kd | [-100.0, 100.0] |
| training.observation_clip.delay_steps | [-100.0, 100.0] |
| training.observation_clip.mass_ratio | [-10.0, 10.0] |
| training.observation_clip.wheel_contact | [0.0, 1.0] |
| training.observation_clip.material | [-100.0, 100.0] |
| training.observation_clip.spring_force | [-1000.0, 1000.0] |
| training.observation_clip.voltage_scale | [-100.0, 100.0] |
| training.observation_clip.power_scale | [-100.0, 100.0] |
| training.observation_clip.command_error | [-100.0, 100.0] |
| training.observation_clip.height_scan | [-10.0, 10.0] |
| training.numerical_safety.joint_velocity_abs_max | 500.0 |
| training.numerical_safety.base_linear_velocity_abs_max | 100.0 |
| training.numerical_safety.base_angular_velocity_abs_max | 200.0 |
| training.critic_torque_scale | 0.05 |
| training.spawn_clearance_m | 0.01 |
| training.spawn_clearance_max_m | 0.03 |
| training.spring_extension_height_m | null（未配置/待填） |
| training.stairs_passive_joint_limits_rad | {} |
| training.env_spacing_m | 8.0 |
| training.gravity_m_s2 | 9.81 |
| training.ground_material.static_friction | 1.0 |
| training.ground_material.dynamic_friction | 1.0 |
| training.ground_material.friction_combine_mode | multiply |
| training.ground_material.restitution | 1.0 |
| training.ground_material.restitution_combine_mode | multiply |
| training.solver_position_iterations | 12 |
| training.solver_velocity_iterations | 6 |
| training.wheel_radius_m | null（未配置/待填） |
| training.joint_lower_rad | [null, null, null, null, null, null] |
| training.joint_upper_rad | [null, null, null, null, null, null] |
| training.joint_target_margin_rad | 0.05 |
| training.hip_pivot_positions_b_m | [null, null] |
| training.joint_armature | [null, null, null, null, null, null] |
| training.joint_viscous_friction | [null, null, null, null, null, null] |
| training.joint_dynamic_friction | [null, null, null, null, null, null] |
| training.joint_coulomb_friction | [null, null, null, null, null, null] |
| training.no_load_speed_rad_s | [null, null, null, null, null, null] |
| training.saturation_torque_nm | [null, null, null, null, null, null] |
| training.wheel_speed_limit_rad_s | null（未配置/待填） |
| training.passive_damping | null（未配置/待填） |
| training.passive_effort_limit | null（未配置/待填） |
| training.spring.reference_q_m | [null, null] |
| training.spring.direction | [null, null] |
| training.spring.f0_n | [null, null] |
| training.spring.stiffness_n_m | [null, null] |
| training.spring.damping_n_s_m | [null, null] |
| training.spring.hysteresis_n | [null, null] |
| training.spring.force_limit_n | [null, null] |
| training.observation_noise.angular_velocity | 0.25 |
| training.observation_noise.gravity | 0.05 |
| training.observation_noise.joint_position | 0.025 |
| training.observation_noise.leg_velocity | 0.5 |
| training.observation_noise.wheel_velocity | 1.0 |
| training.randomization.joint_zero_bias_rad | [-0.01, 0.01] |
| training.randomization.inertia_scale | [0.9, 1.1] |
| training.randomization.imu_roll_pitch_bias_rad | [-0.017453292519943295, 0.017453292519943295] |
| training.randomization.base_mass_scale | [0.9, 1.3] |
| training.randomization.limb_mass_scale | [0.9, 1.1] |
| training.randomization.com_offset_m | [0.04, 0.02, 0.02] |
| training.randomization.static_friction | [0.5, 1.2] |
| training.randomization.dynamic_friction | [0.4, 1.0] |
| training.randomization.restitution | [0.0, 0.2] |
| training.randomization.body_materials | null（未配置/待填） |
| training.randomization.hip_static_friction_add | [0.25, 1.0] |
| training.randomization.hip_dynamic_friction_add | [0.25, 1.0] |
| training.randomization.hip_viscous_friction_add | [0.05, 0.2] |
| training.randomization.wheel_static_friction_add | [0.05, 0.25] |
| training.randomization.gain_scale | [0.75, 1.25] |
| training.randomization.hip_torque_scale | [0.8, 1.1] |
| training.randomization.wheel_torque_scale | [0.9, 1.1] |
| training.randomization.spring_bias_n | [-50.0, 50.0] |
| training.randomization.wheel_power_scale | [0.7, 1.0] |
| training.randomization.voltage_scale | [0.85, 1.0] |
| training.randomization.episode_voltage_drop | [0.0, 0.1] |
| training.randomization.observation_delay_steps | [3, 8] |
| training.randomization.action_delay_steps | [3, 5] |
| training.randomization.push_interval_s | [5.0, 10.0] |
| training.randomization.push_velocity_m_s | 0.25 |
| training.randomization.external_force_n | 10.0 |
| training.randomization.external_torque_nm | 1.0 |
| training.randomization.external_wrench_duration_s | 10.0 |
| training.termination.tilt_rad | 0.6981317007977318 |
| training.termination.airborne_tilt_rad | null（未配置/待填） |
| training.termination.contact_force_n | 3.0 |
| training.termination.duration_s | 0.4 |
| training.termination.release_s | 2.0 |
| training.leg_reset.joint_names | null（未配置/待填） |
| training.leg_reset.link_lengths_m | null（未配置/待填） |
| training.leg_reset.angle_offsets_rad | null（未配置/待填） |
| training.leg_reset.length_range_m | null（未配置/待填） |
| training.leg_reset.angle_range_rad | null（未配置/待填） |
| training.leg_reset.root_tilt_rad | 0.15 |
| training.leg_reset.min_root_height_m | null（未配置/待填） |
| training.leg_reset.settle_s | 1.0 |
| training.airborne.contact_force_n | 20.0 |
| training.airborne.enter_duration_s | 0.02 |
| training.airborne.exit_duration_s | 0.3 |
| training.airborne.max_duration_s | 1.0 |
| training.airborne.wheel_clearance_m | null（未配置/待填） |
| training.airborne.base_height_m | null（未配置/待填） |


</details>


## 机器人合同 scut_robot.template.yaml
[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/config/reference/scut_robot.template.yaml>)
<details markdown="1"><summary>完整机械/随机化/观测clip/延迟/终止合同</summary>


| 字段 | 原值 |
|---|---|
| name | scut_v14_2_reference |
| variant | reference_simulation_only |
| control_hz | 500 |
| policy_hz | 100 |
| wheel_reduction_ratio | 15.764705882352942 |
| spring_nominal_force_n | 400.0 |
| spring_stroke_m | 0.08 |
| joint_order | ["left_front", "left_rear", "left_wheel", "right_front", "right_rear", "right_wheel"] |
| leg_indices | [0, 1, 3, 4] |
| wheel_indices | [2, 5] |
| q_default_rad | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] |
| q_zero_offset_rad | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] |
| motor_direction | [1, 1, 1, 1, 1, 1] |
| can_bus | [1, 1, 1, 2, 2, 2] |
| pending_measurements | {} |
| asset.usd_path | null（未配置/待填） |
| asset.active_joint_names | ["left_front1_joint", "left_rear1_joint", "left_wheel_joint", "right_front1_joint", "right_rear1_joint", "right_wheel_joint"] |
| asset.spring_joint_names | ["left_spring2_joint", "right_spring2_joint"] |
| asset.passive_joint_names | [] |
| asset.wheel_body_names | ["left_wheel_link", "right_wheel_link"] |
| asset.base_body_name | base_link |
| asset.undesired_contact_body_names | ["base_link", ".*_rear1_link", ".*_rear2_link", ".*_front1_link", ".*_front2_link", ".*_front3_link", ".*_front4_link", "gimbal_yaw_link", "gimbal_pitch_link", ".*_guide_link"] |
| asset.termination_contact_body_names | ["base_link", "gimbal_yaw_link", "gimbal_pitch_link", ".*_guide_link", ".*_rear1_link", ".*_rear2_link", ".*_front1_link", ".*_front2_link", ".*_front3_link", ".*_front4_link"] |
| asset.initial_root_position_m | [0, 0, null] |
| asset.initial_joint_positions_rad..* | 0.0 |
| asset.collision_body_names | null（未配置/待填） |
| asset.reference_preset | scut_v14_2 |
| asset.reference_package | null（未配置/待填） |
| training.observation_clip.command | [-100.0, 100.0] |
| training.observation_clip.height | [0.0, 1.0] |
| training.observation_clip.angular_velocity | [-100.0, 100.0] |
| training.observation_clip.gravity | [-100.0, 100.0] |
| training.observation_clip.joint_position | [-100.0, 100.0] |
| training.observation_clip.joint_velocity | [-200.0, 200.0] |
| training.observation_clip.previous_action | [-100.0, 100.0] |
| training.observation_clip.mode | [-100.0, 100.0] |
| training.observation_clip.base_linear_velocity | [-100.0, 100.0] |
| training.observation_clip.base_height | [-10.0, 10.0] |
| training.observation_clip.torque | [-100.0, 100.0] |
| training.observation_clip.wheel_linear_velocity | [-100.0, 100.0] |
| training.observation_clip.kp | [-100.0, 100.0] |
| training.observation_clip.kd | [-100.0, 100.0] |
| training.observation_clip.delay_steps | [-100.0, 100.0] |
| training.observation_clip.mass_ratio | [-10.0, 10.0] |
| training.observation_clip.wheel_contact | [0.0, 1.0] |
| training.observation_clip.material | [-100.0, 100.0] |
| training.observation_clip.spring_force | [-1000.0, 1000.0] |
| training.observation_clip.voltage_scale | [-100.0, 100.0] |
| training.observation_clip.power_scale | [-100.0, 100.0] |
| training.observation_clip.command_error | [-100.0, 100.0] |
| training.observation_clip.height_scan | [-10.0, 10.0] |
| training.numerical_safety.joint_velocity_abs_max | 500.0 |
| training.numerical_safety.base_linear_velocity_abs_max | 100.0 |
| training.numerical_safety.base_angular_velocity_abs_max | 200.0 |
| training.critic_torque_scale | 0.05 |
| training.spawn_clearance_m | 0.01 |
| training.spawn_clearance_max_m | 0.03 |
| training.spring_extension_height_m | 0.44885688 |
| training.stairs_passive_joint_limits_rad.left_front2_joint | [-1.4867696477775674, 0.09999999284490206] |
| training.stairs_passive_joint_limits_rad.right_front2_joint | [-1.4867697635171315, 0.09999999284490206] |
| training.stairs_passive_joint_limits_rad.left_rear2_joint | [-0.019999998568980413, 1.4867696477775674] |
| training.stairs_passive_joint_limits_rad.right_rear2_joint | [-0.019999998568980413, 1.4867697635171315] |
| training.env_spacing_m | 16.0 |
| training.gravity_m_s2 | 9.81 |
| training.ground_material.static_friction | 1.0 |
| training.ground_material.dynamic_friction | 1.0 |
| training.ground_material.friction_combine_mode | multiply |
| training.ground_material.restitution | 1.0 |
| training.ground_material.restitution_combine_mode | multiply |
| training.solver_position_iterations | 12 |
| training.solver_velocity_iterations | 6 |
| training.wheel_radius_m | 0.06 |
| training.joint_lower_rad | [-3.14, -3.14, -3.14, -3.14, -3.14, -3.14] |
| training.joint_upper_rad | [3.14, 3.14, 3.14, 3.14, 3.14, 3.14] |
| training.joint_target_margin_rad | 0.0 |
| training.hip_pivot_positions_b_m | [null, null] |
| training.joint_armature | [0.015795, 0.015795, 0, 0.015795, 0.015795, 0] |
| training.joint_viscous_friction | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] |
| training.joint_dynamic_friction | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] |
| training.joint_coulomb_friction | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] |
| training.no_load_speed_rad_s | [null, null, null, null, null, null] |
| training.saturation_torque_nm | [null, null, null, null, null, null] |
| training.wheel_speed_limit_rad_s | 100.0 |
| training.passive_damping | 0.01 |
| training.passive_effort_limit | 50.0 |
| training.spring.reference_q_m | [0.06076, 0.06076] |
| training.spring.direction | [-1, -1] |
| training.spring.f0_n | [400.0, 400.0] |
| training.spring.stiffness_n_m | [2857.142857142857, 2857.142857142857] |
| training.spring.damping_n_s_m | [50.0, 50.0] |
| training.spring.hysteresis_n | [0.0, 0.0] |
| training.spring.force_limit_n | [1000.0, 1000.0] |
| training.observation_noise.angular_velocity | 0.25 |
| training.observation_noise.gravity | 0.05 |
| training.observation_noise.joint_position | 0.025 |
| training.observation_noise.leg_velocity | 0.5 |
| training.observation_noise.wheel_velocity | 1.0 |
| training.randomization.joint_zero_bias_rad | [-0.01, 0.01] |
| training.randomization.inertia_scale | [0.9, 1.1] |
| training.randomization.imu_roll_pitch_bias_rad | [-0.017453292519943295, 0.017453292519943295] |
| training.randomization.base_mass_scale | [0.9, 1.3] |
| training.randomization.limb_mass_scale | [0.9, 1.1] |
| training.randomization.com_offset_m | [0.04, 0.02, 0.02] |
| training.randomization.static_friction | [0.5, 1.2] |
| training.randomization.dynamic_friction | [0.4, 1.0] |
| training.randomization.restitution | [0.0, 0.2] |
| training.randomization.body_materials | [{"body_names": ["base_link"], "static_friction": [0.01, 0.1], "dynamic_friction": [0.01, 0.1], "restitution": [0.0, 0.2], "buckets": 64}, {"body_names": [".*_guide_link"], "static_friction": [0.1, 0.7], "dynamic_friction": [0.1, 0.7], "restitution": [0.0, 0.1], "buckets": 8}] |
| training.randomization.hip_static_friction_add | [0.25, 1.0] |
| training.randomization.hip_dynamic_friction_add | [0.25, 1.0] |
| training.randomization.hip_viscous_friction_add | [0.05, 0.2] |
| training.randomization.wheel_static_friction_add | [0.05, 0.25] |
| training.randomization.gain_scale | [0.75, 1.25] |
| training.randomization.hip_torque_scale | [0.8, 1.1] |
| training.randomization.wheel_torque_scale | [0.9, 1.1] |
| training.randomization.spring_bias_n | [-50.0, 50.0] |
| training.randomization.wheel_power_scale | [0.7, 1.0] |
| training.randomization.voltage_scale | [0.85, 1.0] |
| training.randomization.episode_voltage_drop | [0.0, 0.1] |
| training.randomization.observation_delay_steps | [3, 8] |
| training.randomization.action_delay_steps | [3, 5] |
| training.randomization.push_interval_s | [5.0, 10.0] |
| training.randomization.push_velocity_m_s | 0.25 |
| training.randomization.external_force_n | 10.0 |
| training.randomization.external_torque_nm | 1.0 |
| training.randomization.external_wrench_duration_s | 10.0 |
| training.termination.tilt_rad | 0.6981317007977318 |
| training.termination.airborne_tilt_rad | 1.0 |
| training.termination.contact_force_n | 3.0 |
| training.termination.duration_s | 0.4 |
| training.termination.release_s | 2.0 |
| training.leg_reset.joint_names | ["left_front1_joint", "right_front1_joint", "left_rear1_joint", "right_rear1_joint", "left_front2_joint", "right_front2_joint", "left_front3_joint", "right_front3_joint", "left_front4_joint", "right_front4_joint", "left_rear2_joint", "right_rear2_joint"] |
| training.leg_reset.link_lengths_m | [0.1134, 0.135, 0.21] |
| training.leg_reset.angle_offsets_rad | [-0.11536626355682518, 3.141592653589793, 0.5183627878423159, 1.9895008143483361, 0.5183627878423159, 0.5183627878423159] |
| training.leg_reset.length_range_m | [0.13, 0.32] |
| training.leg_reset.angle_range_rad | [-0.6, 0.6] |
| training.leg_reset.root_tilt_rad | 0.15 |
| training.leg_reset.min_root_height_m | 0.25 |
| training.leg_reset.settle_s | 1.0 |
| training.airborne.contact_force_n | 20.0 |
| training.airborne.enter_duration_s | 0.02 |
| training.airborne.exit_duration_s | 0.3 |
| training.airborne.max_duration_s | 1.0 |
| training.airborne.wheel_clearance_m | 0.02 |
| training.airborne.base_height_m | 0.3 |
| provenance.asset_and_PD | SCUT assets/wheelbipe_V14_2.py; 40 Nm legs, 5 Nm wheels, PD60/2, wheelD0.2 |
| provenance.spring | SCUT V14 env_cfg spring_settings: offset .06076m, 400..600N over .07m; actuator damping50 |
| provenance.geometry | USD-inspected anchors/bodies; no fabricated SRM measurements |
| provenance.simulation_only | CAN/zero/direction are simulation conventions, not hardware calibration |
| provenance.target_bounds | SCUT +/-3.14rad position-target clamp, NOT mechanical limits; not written to USD |
| provenance.other_designs | Commands, airborne thresholds and friction0 are explicit simulation baseline choices |


</details>


## 机器人合同 robot.yaml
[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/runs/stairs_viewer/fd012a9_latest/params/robot.yaml>)
<details markdown="1"><summary>完整机械/随机化/观测clip/延迟/终止合同</summary>


| 字段 | 原值 |
|---|---|
| name | scut_v14_2_reference |
| variant | reference_simulation_only |
| control_hz | 500 |
| policy_hz | 100 |
| wheel_reduction_ratio | 15.764705882352942 |
| spring_nominal_force_n | 400.0 |
| spring_stroke_m | 0.07999999728053808 |
| joint_order | ["left_front", "left_rear", "left_wheel", "right_front", "right_rear", "right_wheel"] |
| leg_indices | [0, 1, 3, 4] |
| wheel_indices | [2, 5] |
| q_default_rad | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] |
| q_zero_offset_rad | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] |
| motor_direction | [1, 1, 1, 1, 1, 1] |
| can_bus | [1, 1, 1, 2, 2, 2] |
| pending_measurements | {} |
| asset.usd_path | /root/gpufree-data/wheelleg/srm_scut_cloud/reference/agent_world/agent_world/assets/usd_files/wheelbipeV14_2_1/wheelbipeV14_2.usd |
| asset.active_joint_names | ["left_front1_joint", "left_rear1_joint", "left_wheel_joint", "right_front1_joint", "right_rear1_joint", "right_wheel_joint"] |
| asset.spring_joint_names | ["left_spring2_joint", "right_spring2_joint"] |
| asset.passive_joint_names | [] |
| asset.wheel_body_names | ["left_wheel_link", "right_wheel_link"] |
| asset.base_body_name | base_link |
| asset.undesired_contact_body_names | ["base_link", "gimbal_yaw_link", "gimbal_pitch_link", "left_bottom1_guide_link", "left_bottom2_guide_link", "left_bottom3_guide_link", "left_bottom4_guide_link", "left_front1_guide_link", "left_front1_link", "left_front2_link", "left_front3_link", "left_front4_link", "left_front_guide_link", "left_rear1_link", "left_rear2_link", "left_rear2_guide_link", "left_rear_guide_link", "right_bottom1_guide_link", "right_bottom2_guide_link", "right_bottom3_guide_link", "right_bottom4_guide_link", "right_front1_guide_link", "right_front1_link", "right_front2_link", "right_front3_link", "right_front4_link", "right_front_guide_link", "right_rear1_link", "right_rear2_link", "right_rear2_guide_link", "right_rear_guide_link"] |
| asset.termination_contact_body_names | ["base_link", "gimbal_yaw_link", "gimbal_pitch_link", "left_bottom1_guide_link", "left_bottom2_guide_link", "left_bottom3_guide_link", "left_bottom4_guide_link", "left_front1_guide_link", "left_front1_link", "left_front2_link", "left_front3_link", "left_front4_link", "left_front_guide_link", "left_rear1_link", "left_rear2_link", "left_rear2_guide_link", "left_rear_guide_link", "right_bottom1_guide_link", "right_bottom2_guide_link", "right_bottom3_guide_link", "right_bottom4_guide_link", "right_front1_guide_link", "right_front1_link", "right_front2_link", "right_front3_link", "right_front4_link", "right_front_guide_link", "right_rear1_link", "right_rear2_link", "right_rear2_guide_link", "right_rear_guide_link"] |
| asset.initial_root_position_m | [0, 0, 0.19483000010252] |
| asset.initial_joint_positions_rad..* | 0.0 |
| asset.collision_body_names | ["base_link", "gimbal_yaw_link", "gimbal_pitch_link", "left_bottom1_guide_link", "left_bottom2_guide_link", "left_bottom3_guide_link", "left_bottom4_guide_link", "left_front1_guide_link", "left_front1_link", "left_front2_link", "left_front3_link", "left_front4_link", "left_front_guide_link", "left_rear1_link", "left_rear2_link", "left_rear2_guide_link", "left_wheel_link", "left_spring1_link", "left_spring2_link", "left_rear_guide_link", "right_bottom1_guide_link", "right_bottom2_guide_link", "right_bottom3_guide_link", "right_bottom4_guide_link", "right_front1_guide_link", "right_front1_link", "right_front2_link", "right_front3_link", "right_front4_link", "right_front_guide_link", "right_rear1_link", "right_rear2_link", "right_rear2_guide_link", "right_wheel_link", "right_spring1_link", "right_spring2_link", "right_rear_guide_link"] |
| asset.reference_preset | scut_v14_2 |
| asset.reference_package | /root/gpufree-data/wheelleg/srm_scut_cloud/reference/agent_world |
| training.observation_clip.command | [-100.0, 100.0] |
| training.observation_clip.height | [0.0, 1.0] |
| training.observation_clip.angular_velocity | [-100.0, 100.0] |
| training.observation_clip.gravity | [-100.0, 100.0] |
| training.observation_clip.joint_position | [-100.0, 100.0] |
| training.observation_clip.joint_velocity | [-200.0, 200.0] |
| training.observation_clip.previous_action | [-100.0, 100.0] |
| training.observation_clip.mode | [-100.0, 100.0] |
| training.observation_clip.base_linear_velocity | [-100.0, 100.0] |
| training.observation_clip.base_height | [-10.0, 10.0] |
| training.observation_clip.torque | [-100.0, 100.0] |
| training.observation_clip.wheel_linear_velocity | [-100.0, 100.0] |
| training.observation_clip.kp | [-100.0, 100.0] |
| training.observation_clip.kd | [-100.0, 100.0] |
| training.observation_clip.delay_steps | [-100.0, 100.0] |
| training.observation_clip.mass_ratio | [-10.0, 10.0] |
| training.observation_clip.wheel_contact | [0.0, 1.0] |
| training.observation_clip.material | [-100.0, 100.0] |
| training.observation_clip.spring_force | [-1000.0, 1000.0] |
| training.observation_clip.voltage_scale | [-100.0, 100.0] |
| training.observation_clip.power_scale | [-100.0, 100.0] |
| training.observation_clip.command_error | [-100.0, 100.0] |
| training.observation_clip.height_scan | [-10.0, 10.0] |
| training.numerical_safety.joint_velocity_abs_max | 500.0 |
| training.numerical_safety.base_linear_velocity_abs_max | 100.0 |
| training.numerical_safety.base_angular_velocity_abs_max | 200.0 |
| training.critic_torque_scale | 0.05 |
| training.spawn_clearance_m | 0.01 |
| training.spawn_clearance_max_m | 0.03 |
| training.spring_extension_height_m | 0.44885687750064795 |
| training.stairs_passive_joint_limits_rad.left_front2_joint | [-1.4867696477775674, 0.09999999284490206] |
| training.stairs_passive_joint_limits_rad.left_rear2_joint | [-0.019999998568980413, 1.4867696477775674] |
| training.stairs_passive_joint_limits_rad.right_front2_joint | [-1.4867697635171315, 0.09999999284490206] |
| training.stairs_passive_joint_limits_rad.right_rear2_joint | [-0.019999998568980413, 1.4867697635171315] |
| training.env_spacing_m | 16.0 |
| training.gravity_m_s2 | 9.81 |
| training.ground_material.static_friction | 1.0 |
| training.ground_material.dynamic_friction | 1.0 |
| training.ground_material.friction_combine_mode | multiply |
| training.ground_material.restitution | 1.0 |
| training.ground_material.restitution_combine_mode | multiply |
| training.solver_position_iterations | 12 |
| training.solver_velocity_iterations | 6 |
| training.wheel_radius_m | 0.06 |
| training.joint_lower_rad | [-3.14, -3.14, -3.14, -3.14, -3.14, -3.14] |
| training.joint_upper_rad | [3.14, 3.14, 3.14, 3.14, 3.14, 3.14] |
| training.joint_target_margin_rad | 0.0 |
| training.hip_pivot_positions_b_m | [[0.0, 0.17924999445676804, 0.0], [0.0, -0.17924999445676804, 0.0]] |
| training.joint_armature | [0.015795, 0.015795, 0, 0.015795, 0.015795, 0] |
| training.joint_viscous_friction | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] |
| training.joint_dynamic_friction | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] |
| training.joint_coulomb_friction | [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] |
| training.no_load_speed_rad_s | [null, null, null, null, null, null] |
| training.saturation_torque_nm | [null, null, null, null, null, null] |
| training.wheel_speed_limit_rad_s | 100.0 |
| training.passive_damping | 0.01 |
| training.passive_effort_limit | 50.0 |
| training.spring.reference_q_m | [0.06076, 0.06076] |
| training.spring.direction | [-1, -1] |
| training.spring.f0_n | [400.0, 400.0] |
| training.spring.stiffness_n_m | [2857.142857142857, 2857.142857142857] |
| training.spring.damping_n_s_m | [50.0, 50.0] |
| training.spring.hysteresis_n | [0.0, 0.0] |
| training.spring.force_limit_n | [1000.0, 1000.0] |
| training.observation_noise.angular_velocity | 0.25 |
| training.observation_noise.gravity | 0.05 |
| training.observation_noise.joint_position | 0.025 |
| training.observation_noise.leg_velocity | 0.5 |
| training.observation_noise.wheel_velocity | 1.0 |
| training.randomization.joint_zero_bias_rad | [-0.01, 0.01] |
| training.randomization.inertia_scale | [0.9, 1.1] |
| training.randomization.imu_roll_pitch_bias_rad | [-0.017453292519943295, 0.017453292519943295] |
| training.randomization.base_mass_scale | [0.9, 1.3] |
| training.randomization.limb_mass_scale | [0.9, 1.1] |
| training.randomization.com_offset_m | [0.04, 0.02, 0.02] |
| training.randomization.static_friction | [0.5, 1.2] |
| training.randomization.dynamic_friction | [0.4, 1.0] |
| training.randomization.restitution | [0.0, 0.2] |
| training.randomization.body_materials | [{"body_names": ["base_link"], "static_friction": [0.01, 0.1], "dynamic_friction": [0.01, 0.1], "restitution": [0.0, 0.2], "buckets": 64}, {"body_names": [".*_guide_link"], "static_friction": [0.1, 0.7], "dynamic_friction": [0.1, 0.7], "restitution": [0.0, 0.1], "buckets": 8}] |
| training.randomization.hip_static_friction_add | [0.25, 1.0] |
| training.randomization.hip_dynamic_friction_add | [0.25, 1.0] |
| training.randomization.hip_viscous_friction_add | [0.05, 0.2] |
| training.randomization.wheel_static_friction_add | [0.05, 0.25] |
| training.randomization.gain_scale | [0.75, 1.25] |
| training.randomization.hip_torque_scale | [0.8, 1.1] |
| training.randomization.wheel_torque_scale | [0.9, 1.1] |
| training.randomization.spring_bias_n | [-50.0, 50.0] |
| training.randomization.wheel_power_scale | [0.7, 1.0] |
| training.randomization.voltage_scale | [0.85, 1.0] |
| training.randomization.episode_voltage_drop | [0.0, 0.1] |
| training.randomization.observation_delay_steps | [3, 8] |
| training.randomization.action_delay_steps | [3, 5] |
| training.randomization.push_interval_s | [5.0, 10.0] |
| training.randomization.push_velocity_m_s | 0.25 |
| training.randomization.external_force_n | 10.0 |
| training.randomization.external_torque_nm | 1.0 |
| training.randomization.external_wrench_duration_s | 10.0 |
| training.termination.tilt_rad | 0.6981317007977318 |
| training.termination.airborne_tilt_rad | 1.0 |
| training.termination.contact_force_n | 3.0 |
| training.termination.duration_s | 0.4 |
| training.termination.release_s | 2.0 |
| training.leg_reset.joint_names | ["left_front1_joint", "right_front1_joint", "left_rear1_joint", "right_rear1_joint", "left_front2_joint", "right_front2_joint", "left_front3_joint", "right_front3_joint", "left_front4_joint", "right_front4_joint", "left_rear2_joint", "right_rear2_joint"] |
| training.leg_reset.link_lengths_m | [0.1134, 0.135, 0.21] |
| training.leg_reset.angle_offsets_rad | [-0.11536626355682518, 3.141592653589793, 0.5183627878423159, 1.9895008143483361, 0.5183627878423159, 0.5183627878423159] |
| training.leg_reset.length_range_m | [0.13, 0.32] |
| training.leg_reset.angle_range_rad | [-0.6, 0.6] |
| training.leg_reset.root_tilt_rad | 0.15 |
| training.leg_reset.min_root_height_m | 0.25 |
| training.leg_reset.settle_s | 1.0 |
| training.airborne.contact_force_n | 20.0 |
| training.airborne.enter_duration_s | 0.02 |
| training.airborne.exit_duration_s | 0.3 |
| training.airborne.max_duration_s | 1.0 |
| training.airborne.wheel_clearance_m | 0.02 |
| training.airborne.base_height_m | 0.3 |
| provenance.asset_and_PD | SCUT assets/wheelbipe_V14_2.py; 40 Nm legs, 5 Nm wheels, PD60/2, wheelD0.2 |
| provenance.spring | SCUT V14 env_cfg spring_settings: offset .06076m, 400..600N over .07m; actuator damping50 |
| provenance.geometry | USD-inspected anchors/bodies; no fabricated SRM measurements |
| provenance.simulation_only | CAN/zero/direction are simulation conventions, not hardware calibration |
| provenance.target_bounds | SCUT +/-3.14rad position-target clamp, NOT mechanical limits; not written to USD |
| provenance.other_designs | Commands, airborne thresholds and friction0 are explicit simulation baseline choices |


</details>

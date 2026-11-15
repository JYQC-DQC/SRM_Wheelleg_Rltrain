# 附录D：公式、状态机、裁剪和课程源码定义

[返回总览](README.md)

摘录不是新训练代码。同名函数若历史实现不同，分别展示并列适用配置ID。

## 我们 rewards.py


<details markdown="1"><summary>track_lin_vel</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:6>)
~~~python
def track_lin_vel(s, p):
    return torch.exp(-s["linear_error"].square() / p["linear_sigma"]) * s["tracking_mask"] * s["height_gate"]
~~~

</details>


<details markdown="1"><summary>lin_vel_error</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:10>)
~~~python
def lin_vel_error(s, p):
    return (0.25 * s["linear_error"]).square() * s["tracking_mask"] * s["height_gate"]
~~~

</details>


<details markdown="1"><summary>track_ang_vel</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:14>)
~~~python
def track_ang_vel(s, p):
    return torch.exp(-s["angular_error"].square() / p["angular_sigma"]) * s["tracking_mask"] * s["height_gate"]
~~~

</details>


<details markdown="1"><summary>ang_vel_error</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:18>)
~~~python
def ang_vel_error(s, p):
    return (0.5 * s["angular_error"]).square() * s["tracking_mask"] * s["height_gate"]
~~~

</details>


<details markdown="1"><summary>track_height</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:22>)
~~~python
def track_height(s, p):
    return torch.exp(-s["height_error"].square() / p["height_sigma"]) * s["height_mask"]
~~~

</details>


<details markdown="1"><summary>track_height_wide</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:26>)
~~~python
def track_height_wide(s, p):
    # 改自 SCUT wheelbipe25_v3/env.py:3831 (track_height_exp，V14 的 height_sigma=0.025)：
    # 紧核在误差 7 cm 处只有 0.007，没有梯度；宽核让腿折叠的姿态也能感到“再高一点更好”。
    return torch.exp(-s["height_error"].square() / p["height_wide_sigma"]) * s["height_mask"]
~~~

</details>


<details markdown="1"><summary>height_error</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:32>)
~~~python
def height_error(s, p):
    # ground_mask: 腾空时不罚，SCUT V14/env_cfg.py:1560 (track_height_square → 0)。
    return (10 * s["height_error"]).square() * s["height_mask"] * s["ground_mask"]
~~~

</details>


<details markdown="1"><summary>flat_roll</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:37>)
~~~python
def flat_roll(s, p):
    return torch.exp(-s["gravity"][:, 1].square() / p["roll_sigma"])
~~~

</details>


<details markdown="1"><summary>flat_pitch</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:41>)
~~~python
def flat_pitch(s, p):
    return torch.exp(-s["gravity"][:, 0].square() / p["pitch_sigma"])
~~~

</details>


<details markdown="1"><summary>roll_penalty</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:45>)
~~~python
def roll_penalty(s, p):
    return ((2 * torch.exp(-s["heading_velocity"][:, 0].square() / 3) + 2) * s["gravity"][:, 1]).square()
~~~

</details>


<details markdown="1"><summary>pitch_penalty</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:49>)
~~~python
def pitch_penalty(s, p):
    # ground_mask: 腾空时不罚，SCUT V14/env_cfg.py:1551 (flat_orientation_y_v → 0)。
    # 保留原来的指数衰减形式；P1 系数 1/4/3 使 3 m/s 时平方后的强度约为零速的 60%。
    factor = (
        p["pitch_velocity_amplitude"] * torch.exp(-s["heading_velocity"][:, 0].square() / p["pitch_velocity_sigma"])
        + p["pitch_velocity_offset"]
    )
    return (factor * s["gravity"][:, 0]).square() * s["ground_mask"]
~~~

</details>


<details markdown="1"><summary>vertical_velocity</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:59>)
~~~python
def vertical_velocity(s, p):
    # World vz relative to the height-reference rate: commanded height changes are free, bobbing is not.
    # The body-frame vz used before (SCUT V14 lin_vel_z) also charged forward speed whenever the body leaned.
    return (s["velocity_w"][:, 2] - s["height_target_rate"]).square() * s["height_mask"]
~~~

</details>


<details markdown="1"><summary>angular_xy</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:65>)
~~~python
def angular_xy(s, p):
    return s["angular_velocity"][:, :2].square().sum(-1)
~~~

</details>


<details markdown="1"><summary>no_fork</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:69>)
~~~python
def no_fork(s, p):
    dx = (s["wheel_position_b"][:, 0, 0] - s["wheel_position_b"][:, 1, 0]).abs()
    return (dx > p["fork_deadzone_m"]).float()
~~~

</details>


<details markdown="1"><summary>no_fork_square</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:74>)
~~~python
def no_fork_square(s, p):
    dx = (s["wheel_position_b"][:, 0, 0] - s["wheel_position_b"][:, 1, 0]).abs()
    return (p["fork_square_scale"] * (dx - p["fork_deadzone_m"]).clamp_min(0)).square()
~~~

</details>


<details markdown="1"><summary>leg_symmetry</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:79>)
~~~python
def leg_symmetry(s, p):
    return (s["leg_angle"][:, 0] - s["leg_angle"][:, 1]).square() + p["leg_length_symmetry_scale"] * (
        s["leg_length"][:, 0] - s["leg_length"][:, 1]
    ).square()
~~~

</details>


<details markdown="1"><summary>undesired_contact</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:85>)
~~~python
def undesired_contact(s, p):
    # 改自 SCUT wheelbipe25_v3/env.py:3929-3935: 二值项，名单变长后不随触地刚体数放大。
    return (s["undesired_force"] > p["contact_force_n"]).any(-1).float() * s["contact_multiplier"]
~~~

</details>


<details markdown="1"><summary>stand_still</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:90>)
~~~python
def stand_still(s, p):
    # 改自 SCUT wheelbipe25_v3/env.py:3748-3751 (stand_still_lin_vel): 绝对值，慢速溜车也有梯度。
    # Heading-frame horizontal velocity, so vertical motion of a pitched body does not count as drifting.
    return s["heading_velocity"].abs().sum(-1) * (s["requested_speed"] < p["stand_deadzone"])
~~~

</details>


<details markdown="1"><summary>joint_torque</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:96>)
~~~python
def joint_torque(s, p):
    return s["torque"].square().sum(-1)
~~~

</details>


<details markdown="1"><summary>wheel_power</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:100>)
~~~python
def wheel_power(s, p):
    return (s["wheel_torque"] * s["wheel_velocity"]).abs().sum(-1)
~~~

</details>


<details markdown="1"><summary>action_rate</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:104>)
~~~python
def action_rate(s, p):
    return (s["action"] - s["previous_action"]).square().sum(-1)
~~~

</details>


<details markdown="1"><summary>leg_joint_vel</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:109>)
~~~python
def leg_joint_vel(s, p):
    return s["hip_velocity"].square().sum(-1)
~~~

</details>


<details markdown="1"><summary>leg_joint_acc</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:113>)
~~~python
def leg_joint_acc(s, p):
    # 改自 SCUT wheelbipe25_v3/env.py:3508 (V14 权重 -5e-7)；本项目按策略步差分，SCUT 读取 joint_acc。
    return s["hip_acceleration"].square().sum(-1)
~~~

</details>


<details markdown="1"><summary>wheel_vel</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:118>)
~~~python
def wheel_vel(s, p):
    return s["wheel_velocity"].square().sum(-1)
~~~

</details>


<details markdown="1"><summary>action_smoothness_leg</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:122>)
~~~python
def action_smoothness_leg(s, p):
    return s["leg_action_second_difference"].square().sum(-1)
~~~

</details>


<details markdown="1"><summary>action_smoothness_wheel</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:126>)
~~~python
def action_smoothness_wheel(s, p):
    return s["wheel_action_second_difference"].square().sum(-1)
~~~

</details>


<details markdown="1"><summary>termination</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:130>)
~~~python
def termination(s, p):
    return s["terminated"].float() * s["termination_multiplier"]
~~~

</details>


<details markdown="1"><summary>spin_velocity</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:135>)
~~~python
def spin_velocity(s, p):
    return torch.exp(-s["translation_error"].square().sum(-1) / p["spin_velocity_sigma"]) * s["height_gate"]
~~~

</details>


<details markdown="1"><summary>spin_speed</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:139>)
~~~python
def spin_speed(s, p):
    return torch.exp(-s["speed_error"].square() / p["spin_velocity_sigma"]) * s["height_gate"]
~~~

</details>


<details markdown="1"><summary>spin_heading</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:143>)
~~~python
def spin_heading(s, p):
    return (
        torch.exp(-s["heading_error"].square() / p["spin_heading_sigma"])
        * (s["requested_speed"] > p["stand_deadzone"])
        * s["height_gate"]
    )
~~~

</details>


<details markdown="1"><summary>spin_heading_error</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:151>)
~~~python
def spin_heading_error(s, p):
    # 改自 SCUT wheelbipe_V14/env.py:1049 (gimbal_spin_heading_error_square)，门控与 spin_heading 相同。
    return (p["spin_heading_square_scale"] * s["heading_error"]).square() * (s["requested_speed"] > p["stand_deadzone"])
~~~

</details>


<details markdown="1"><summary>spin_velocity_error</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:156>)
~~~python
def spin_velocity_error(s, p):
    return s["translation_error"].square().sum(-1)
~~~

</details>


<details markdown="1"><summary>spin_speed_error</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:160>)
~~~python
def spin_speed_error(s, p):
    return s["speed_error"].square()
~~~

</details>


<details markdown="1"><summary>jump_apex</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:164>)
~~~python
def jump_apex(s, p):
    error = (s["jump"].height - (s["jump"].apex_z - s["jump"].start_z)).clamp_min(0)
    return torch.exp(-error.square() / s["jump"].settings["apex_sigma"]) * s["jump"].apex_pulse
~~~

</details>


<details markdown="1"><summary>jump_landing</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:169>)
~~~python
def jump_landing(s, p):
    return s["jump"].landing_pulse.float()
~~~

</details>


<details markdown="1"><summary>jump_flight</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:173>)
~~~python
def jump_flight(s, p):
    return s["jump_ref"]["flight"].float()
~~~

</details>


<details markdown="1"><summary>jump_crouch</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:177>)
~~~python
def jump_crouch(s, p):
    error = (s["leg_length"] - s["jump"].settings["crouch_leg_length_m"]).abs().sum(-1)
    return torch.exp(-4 * error) * s["jump_ref"]["crouch"] * s["guidance_scale"]
~~~

</details>


<details markdown="1"><summary>jump_takeoff</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:182>)
~~~python
def jump_takeoff(s, p):
    target = s["jump_ref"]["takeoff_velocity"]
    ratio = s["velocity_w"][:, 2] / target.clamp_min(torch.finfo(target.dtype).eps)
    return ratio.clamp(0, 1) * s["jump_ref"]["push"] * s["guidance_scale"]
~~~

</details>


<details markdown="1"><summary>jump_push_symmetry</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:188>)
~~~python
def jump_push_symmetry(s, p):
    force = s["wheel_force"].clamp_min(0)
    return (1 - (force[:, 0] - force[:, 1]).abs() / force.sum(-1).clamp_min(1)) * s["jump_ref"]["push"]
~~~

</details>


<details markdown="1"><summary>jump_tuck</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:193>)
~~~python
def jump_tuck(s, p):
    error = (s["leg_length"] - s["jump"].settings["tuck_leg_length_m"]).abs().sum(-1)
    return torch.exp(-4 * error) * s["jump_ref"]["tuck"] * s["guidance_scale"]
~~~

</details>


<details markdown="1"><summary>jump_prepare</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:198>)
~~~python
def jump_prepare(s, p):
    error = (s["leg_length"] - s["jump"].settings["landing_leg_length_m"]).abs().sum(-1)
    return torch.exp(-4 * error) * s["jump_ref"]["prepare"] * s["guidance_scale"]
~~~

</details>


<details markdown="1"><summary>jump_impact</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:203>)
~~~python
def jump_impact(s, p):
    return (s["hip_torque"].square().amax(-1) + s["hip_velocity"].square().sum(-1)) * s["jump"].touchdown_pulse
~~~

</details>


<details markdown="1"><summary>jump_asymmetric_landing</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:207>)
~~~python
def jump_asymmetric_landing(s, p):
    times = s["jump"].touchdown_time
    return ((times[:, 0] - times[:, 1]).abs() > s["jump"].settings["max_touchdown_difference_s"]).float() * s[
        "jump"
    ].touchdown_pulse
~~~

</details>


<details markdown="1"><summary>uncommanded_flight</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:214>)
~~~python
def uncommanded_flight(s, p):
    return (s["airborne"] & ~s["jump"].active & ~s["jump"].landing_pulse).float()
~~~

</details>


<details markdown="1"><summary>compute_rewards</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/rewards.py:286>)
~~~python
def compute_rewards(state: dict, parameters: dict, weights: dict, dt: float, clip: float) -> dict[str, torch.Tensor]:
    # Event weights are total payouts: neither dt nor the continuous-term clip applies.
    return {
        name: TERMS[name](state, parameters) * weight
        if name in EVENT_TERMS
        else (TERMS[name](state, parameters) * weight * dt).clamp(-clip, clip)
        for name, weight in weights.items()
        if weight != 0
    }
~~~

</details>


## 我们 landing_rewards.py


<details markdown="1"><summary>__init__</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/landing_rewards.py:21>)
~~~python
def __init__(self, count: int, wheels: list[int], guides: list[int], body_count: int, settings: dict, device: str):
        self.p = settings
        self.wheels = wheels
        self.nonwheel = torch.ones(body_count, dtype=torch.bool, device=device)
        self.nonwheel[wheels] = False
        self.guide = torch.zeros(body_count, dtype=torch.bool, device=device)
        self.guide[guides] = True
        self.hard = self.nonwheel & ~self.guide
        self.guide_count = len(guides)
        self.active = torch.zeros(count, dtype=torch.bool, device=device)
        self.hold = self.active.clone()
        self.bad = self.active.clone()  # hard non-wheel collision
        self.guide_bad = self.active.clone()  # guide impact with little cushioning
        self.guide_touched = self.active.clone()  # logging only: strict success excludes any guide contact
        # Guide contact and downward speed at the previous physics sample, (N, guides), for rising-edge grading.
        self.guide_previous = torch.zeros(count, len(guides), dtype=torch.bool, device=device)
        self.guide_previous_down = torch.zeros(count, len(guides), device=device)
        self.guide_previous_valid = self.active.clone()  # False until one physics sample after reset
        self.invalid = self.active.clone()
        self.support = self.active.clone()
        self.settled = self.active.clone()
        self.born = torch.zeros(count, dtype=torch.long, device=device)
        self.last_tick = torch.full_like(self.born, -1)
        self.touch = torch.full((count,), -1.0, device=device)
        self.supported = torch.zeros(count, device=device)
        self.held = self.supported.clone()
        self.best = self.supported.clone()
        self.since_touch = self.supported.clone()
        self.age = self.supported.clone()
        self.progress = self.supported.clone()
        self.outcome = self.supported.clone()
        self.guide_cost = self.supported.clone()  # accumulated over the physics samples of one policy step
        self.resolved = self.active.clone()
        self.succeeded = self.active.clone()
        self.stats = {}
~~~

</details>


<details markdown="1"><summary>_add</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/landing_rewards.py:57>)
~~~python
def _add(self, name: str, value: torch.Tensor) -> None:
        self.stats[name] = self.stats[name] + value.detach() if name in self.stats else value.detach().clone()
~~~

</details>


<details markdown="1"><summary>reset</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/landing_rewards.py:60>)
~~~python
def reset(self, ids: torch.Tensor, air: torch.Tensor, tick: int) -> None:
        # Only exogenous air-reset births open an event. Hops and contact chatter cannot reopen it.
        self.active[ids] = air
        self.hold[ids] = air
        self.born[ids] = tick
        self.last_tick[ids] = tick
        self.touch[ids] = -1
        for value in (
            self.bad,
            self.guide_bad,
            self.guide_touched,
            self.guide_previous,
            self.guide_previous_down,
            self.guide_previous_valid,
            self.invalid,
            self.support,
            self.settled,
            self.supported,
            self.held,
            self.best,
            self.since_touch,
            self.age,
            self.progress,
            self.outcome,
            self.guide_cost,
        ):
            value[ids] = 0
        self._add("births", air.sum())
~~~

</details>


<details markdown="1"><summary>begin_step</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/landing_rewards.py:89>)
~~~python
def begin_step(self) -> None:
        # Support must remain present throughout every physical sample of the policy interval.
        self.support.fill_(True)
        self.guide_cost.zero_()
~~~

</details>


<details markdown="1"><summary>sample</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/landing_rewards.py:94>)
~~~python
def sample(self, tick: int, physics_dt: float, forces: torch.Tensor, guide_down: torch.Tensor) -> None:
        """forces (N, bodies) contact force magnitudes; guide_down (N, guides) downward speed of each guide body."""
        use = self.active & (tick > self.last_tick)
        self.last_tick[use] = tick
        finite = torch.isfinite(forces).all(-1)
        contact = forces > self.p["contact_force_n"]
        first = use & finite & (self.touch < 0) & contact.any(-1)
        self.touch[first] = ((tick - self.born) * physics_dt)[first]
        self.invalid |= use & ~finite
        self.bad |= use & finite & contact[:, self.hard].any(-1)
        if self.guide_count:
            # A non-finite guide speed is no evidence of a cushioned contact: the event becomes invalid instead.
            speed_ok = torch.isfinite(guide_down).all(-1)
            self.invalid |= use & ~speed_ok
            guide = contact[:, self.guide] & (use & finite & speed_ok)[:, None]
            onset = guide & ~self.guide_previous
            # Pre-contact speed: the sample before the contact, not after the impact has already slowed the body.
            speed = torch.where(onset, self.guide_previous_down, 0.0).amax(-1)
            touched = onset.any(-1)
            # No sample before it (contact at the first physics step after reset): unknown speed counts as hard.
            unknown = touched & ~self.guide_previous_valid
            severe = touched & ((speed >= self.p["guide_hard_speed_m_s"]) | unknown)
            self.guide_bad |= severe
            light = touched & ~severe
            cost = self.p["guide_speed_cost"] * speed / self.p["guide_hard_speed_m_s"]
            self.guide_cost -= torch.where(light, cost, 0.0)
            self.guide_touched |= touched
            # Counted per environment sample with a new guide contact, not per guide body: guides that start
            # touching in the same 2 ms sample are graded and charged once, at the fastest of them.
            self._add("guide_contacts", touched.sum())
            self._add("guide_contact_without_prior_sample", unknown.sum())
            self._add("guide_impact_speed_m_s/sum", torch.where(touched & ~unknown, speed, 0.0).sum())
            self._add("guide_impact_speed_m_s/count", (touched & ~unknown).sum())
            down = torch.nan_to_num(guide_down, nan=0.0, posinf=0.0, neginf=0.0).clamp_min(0)
            stored = use & speed_ok
            self.guide_previous = torch.where(stored[:, None], guide, self.guide_previous)
            self.guide_previous_down = torch.where(stored[:, None], down, self.guide_previous_down)
            self.guide_previous_valid |= stored
        both = (forces[:, self.wheels] > self.p["support_force_n"]).all(-1)
        self.support &= ~use | (finite & both & ~contact[:, self.nonwheel].any(-1))
~~~

</details>


<details markdown="1"><summary>flight</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/landing_rewards.py:135>)
~~~python
def flight(self) -> torch.Tensor:
        return self.active & (self.touch < 0)
~~~

</details>


<details markdown="1"><summary>cushion</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/landing_rewards.py:138>)
~~~python
def cushion(self) -> torch.Tensor:
        # One-shot transition after the first touch; its deadline runs from first contact, so bounces cannot extend it.
        return self.active & (self.touch >= 0) & ~self.settled
~~~

</details>


<details markdown="1"><summary>update</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/landing_rewards.py:142>)
~~~python
def update(
        self,
        tick: int,
        physics_dt: float,
        dt: float,
        state: dict,
        terminated: torch.Tensor,
        timeout: torch.Tensor,
        numerical: torch.Tensor,
    ) -> None:
        self.progress.zero_()
        self.outcome.zero_()
        age = (tick - self.born) * physics_dt
        self.age = torch.where(self.hold, age, 0.0)
        collided = self.bad | self.guide_bad
        tilt = torch.stack((state["roll"], state["pitch"]), -1).abs().amax(-1)
        omega = state["angular_velocity"][:, :2].abs().amax(-1)
        vz = state["velocity_w"][:, 2].abs()
        height = state["height_error"].abs()
        values = torch.stack((tilt, omega, vz, height), -1)
        finite = torch.isfinite(values).all(-1)
        self.invalid |= self.active & (~finite | numerical)
        done = terminated | timeout | numerical
        contacted = self.touch >= 0
        self.since_touch = torch.where(self.hold & contacted, age - self.touch, 0.0)
        supported = self.active & contacted & self.support & ~collided & ~self.invalid & ~done
        self.supported = torch.where(supported, self.supported + dt, 0.0)
        # Durations accumulate float32 steps; half a step of tolerance keeps the hold exactly N steps long.
        tolerance = 0.5 * dt
        self.settled |= (
            self.active
            & contacted
            & (
                (self.supported >= self.p["settle_support_s"] - tolerance)
                | (self.since_touch >= self.p["cushion_max_s"])
            )
        )
        scales = values.new_tensor(
            [self.p[k] for k in ("tilt_rad", "angular_xy_rad_s", "vertical_velocity_m_s", "height_error_m")]
        )
        # Squared, normalized, bounded quality; never multiply an unchecked NaN by a mask.
        quality = torch.exp(-0.25 * (torch.nan_to_num(values / scales, nan=1e6).clamp(-1e6, 1e6)).square().sum(-1))
        quality = torch.where(supported, quality, 0.0)
        higher = torch.maximum(self.best, quality)
        self.progress.copy_((higher - self.best) * self.p["progress_budget"])
        self.best.copy_(higher)
        stable = supported & (values <= scales).all(-1)
        self.held = torch.where(stable, self.held + dt, 0.0)
        success = stable & (self.held >= self.p["stable_s"] - tolerance)
        expired = contacted & (self.since_touch >= self.p["window_s"])
        missing = ~contacted & (age >= self.p["contact_timeout_s"])
        failed = self.active & ~success & (done | collided | self.invalid | expired | missing)
        # An early exogenous time limit (randomized initial episode age) is not a landing failure.
        neutral = failed & timeout & ~terminated & ~numerical & ~collided & ~self.invalid
        failed &= ~neutral
        self.outcome[failed] = -self.p["failure_cost"]
        self.outcome[success] = self.p["success_bonus"]
        # Mutually exclusive causes, in priority order.
        causes = {
            "invalid": failed & self.invalid,
            "collision": failed & ~self.invalid & self.bad,
            "guide_impact": failed & ~self.invalid & ~self.bad & self.guide_bad,
            "terminated": failed & ~self.invalid & ~collided & terminated,
            "no_contact": failed & ~self.invalid & ~collided & ~terminated & missing,
        }
        causes["unstable"] = failed & ~torch.stack(list(causes.values())).any(0)
        self._add("success", success.sum())
        # Strict reference: success without any guide contact, comparable with the rule before guide grading.
        self._add("success_no_guide", (success & ~self.guide_touched).sum())
        self._add("neutral_timeout", neutral.sum())
        for name, mask in causes.items():
            self._add(f"failure/{name}", mask.sum())
        self._add("success_time_s/sum", torch.where(success, self.since_touch, 0.0).sum())
        self.active[success | failed | neutral] = False
        # Read by the air-height curriculum: events resolved this step, exogenous timeouts excluded.
        self.resolved = success | failed
        self.succeeded = success
        # Same end as the diagnostic window: a failed event (e.g. a collision) keeps the commands frozen so the
        # diagnostic recovery that follows is not mixed with responses to new commands.
        self.hold &= ~(done | expired | missing)
~~~

</details>


<details markdown="1"><summary>terms</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/landing_rewards.py:223>)
~~~python
def terms(self, state: dict, wheel_radius: float, dt: float) -> dict[str, torch.Tensor]:
        # All flight terms are nonpositive, so they add nothing for staying airborne. The attitude rewards and the
        # relaxed ground terms still apply in flight; watch Landing/first_contact_s for a drift toward later touchdowns.
        flight = self.flight()
        center = torch.exp(-state["wheel_heading_x"].square() / self.p["wheel_center_sigma"]).mean(-1)
        # Approximate no-slip target: the heading-frame body speed, ignoring leg swing, body rotation and wheel heading.
        # The actor sees only the command, which matches it for most births; a command target would teach braking
        # on mismatched ones.
        yaw = state["yaw"]
        forward = state["velocity_w"][:, 0] * yaw.cos() + state["velocity_w"][:, 1] * yaw.sin()
        speed_error = state["wheel_velocity"] * wheel_radius - forward[:, None]
        speed = torch.exp(-speed_error.square().mean(-1) / self.p["wheel_speed_sigma"])
        # Legs extended before touchdown leave cushioning stroke; only a shortfall below the target costs.
        shortfall = (self.p["leg_extension_target_m"] - state["leg_length"]).clamp_min(0).mean(-1)
        extension = (shortfall / self.p["leg_extension_scale_m"]).clamp(max=1.0)
        return {
            "landing_progress": self.progress,
            "landing_outcome": self.outcome,
            "landing_guide_contact": self.guide_cost,
            "landing_wheel_center": torch.where(flight, -self.p["wheel_center_weight"] * dt * (1 - center), 0.0),
            "landing_wheel_speed": torch.where(flight, -self.p["wheel_speed_weight"] * dt * (1 - speed), 0.0),
            "landing_leg_extension": torch.where(flight, -self.p["leg_extension_weight"] * dt * extension, 0.0),
        }
~~~

</details>


<details markdown="1"><summary>features</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/landing_rewards.py:247>)
~~~python
def features(self) -> torch.Tensor:
        """Event state the critic needs to predict the payouts; (N, FEATURES), each in [0, 1]."""
        active, flight, cushion = self.active.float(), self.flight().float(), self.cushion().float()
        return torch.stack(
            (
                active,
                flight,
                cushion,
                (self.since_touch / self.p["window_s"]).clamp(0, 1),
                (self.held / self.p["stable_s"]).clamp(0, 1) * active,
                self.best * active,
                (self.age / self.p["contact_timeout_s"]).clamp(0, 1) * flight,  # no-contact deadline
                (self.supported / self.p["settle_support_s"]).clamp(0, 1) * cushion,  # cushion exit
                self.hold.float(),  # commands stay frozen
            ),
            -1,
        )
~~~

</details>


<details markdown="1"><summary>take_log</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/landing_rewards.py:265>)
~~~python
def take_log(self) -> dict[str, float]:
        values = {key: float(value.item()) for key, value in self.stats.items()}
        self.stats = {}
        result = {f"LandingReward/{k}": v for k, v in values.items() if not k.endswith(("/sum", "/count"))}
        result["LandingReward/pending"] = float(self.active.sum().item())
        failures = sum(v for k, v in values.items() if k.startswith("failure/"))
        resolved = values.get("success", 0.0) + failures
        if resolved:
            # First 0.5 s stable hold reached; says nothing about staying stable afterwards. Exogenous timeouts
            # are excluded from the denominator: they say nothing about the landing.
            result["LandingReward/first_recovery_rate"] = values["success"] / resolved
            result["LandingReward/first_recovery_no_guide_rate"] = values["success_no_guide"] / resolved
        if values.get("success"):
            result["LandingReward/success_time_s/mean"] = values["success_time_s/sum"] / values["success"]
        if values.get("guide_impact_speed_m_s/count"):
            # Downward speed of the touching guide body 2 ms before each new guide contact sample.
            result["LandingReward/guide_impact_speed_m_s/mean"] = (
                values["guide_impact_speed_m_s/sum"] / values["guide_impact_speed_m_s/count"]
            )
        return result
~~~

</details>


## 我们 jump.py


<details markdown="1"><summary>tunnel_landing</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/jump.py:151>)
~~~python
def tunnel_landing(
    wheel_position: torch.Tensor,
    wheel_radius: float,
    body_position: torch.Tensor,
    beam_end_x: torch.Tensor,
    ground_z: torch.Tensor,
    margin: float,
    ground_tolerance: float,
) -> torch.Tensor:
    wheels_beyond = (wheel_position[:, :, 0] - wheel_radius > beam_end_x[:, None] + margin).all(-1)
    body_beyond = (body_position[:, :, 0] > beam_end_x[:, None] + margin).all(-1)
    on_ground = (wheel_position[:, :, 2] - wheel_radius - ground_z[:, None]).abs().amax(-1) < ground_tolerance
    return wheels_beyond & body_beyond & on_ground
~~~

</details>


<details markdown="1"><summary>__init__</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/jump.py:9>)
~~~python
def __init__(self, settings: dict, count: int, device: str):
        self.settings, self.device = settings, device
        self.active = torch.zeros(count, dtype=torch.bool, device=device)
        self.remaining = torch.zeros(count, dtype=torch.long, device=device)
        self.elapsed = torch.zeros(count, device=device)
        self.next_trigger = torch.zeros_like(self.elapsed)
        self.height = torch.zeros_like(self.elapsed)
        self.start_z = torch.zeros_like(self.elapsed)
        self.apex_z = torch.zeros_like(self.elapsed)
        self.air_time = torch.zeros_like(self.elapsed)
        self.stable_time = torch.zeros_like(self.elapsed)
        self.touchdown_time = torch.full((count, 2), -1.0, device=device)
        self.took_off = self.active.clone()
        self.landed = self.active.clone()
        self.apex_paid = self.active.clone()
        self.landing_paid = self.active.clone()
        self.invalid = self.active.clone()
        self.apex_pulse = self.active.clone()
        self.landing_pulse = self.active.clone()
        self.touchdown_pulse = self.active.clone()
        self.finished = self.active.clone()
        self.first_touch = self.active.clone()
~~~

</details>


<details markdown="1"><summary>reset</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/jump.py:32>)
~~~python
def reset(self, ids: torch.Tensor) -> None:
        for value in (
            self.active,
            self.took_off,
            self.landed,
            self.apex_paid,
            self.landing_paid,
            self.invalid,
            self.apex_pulse,
            self.landing_pulse,
            self.touchdown_pulse,
            self.finished,
            self.first_touch,
        ):
            value[ids] = False
        for value in (self.elapsed, self.height, self.air_time, self.stable_time, self.start_z, self.apex_z):
            value[ids] = 0
        self.touchdown_time[ids] = -1
        self.remaining[ids] = torch.multinomial(
            self.elapsed.new_tensor(self.settings["jump_count_probabilities"]), len(ids), replacement=True
        )
        self.next_trigger[ids] = uniform(self.settings["first_trigger_range_s"], (len(ids),), self.device)
~~~

</details>


<details markdown="1"><summary>trigger</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/jump.py:55>)
~~~python
def trigger(
        self,
        age: torch.Tensor,
        z: torch.Tensor,
        allowed: torch.Tensor,
        target_height: torch.Tensor | None = None,
        *,
        require_trigger_time: bool = True,
    ) -> None:
        start = ~self.active & (self.remaining > 0) & allowed
        if require_trigger_time:
            start &= age >= self.next_trigger
        ids = start.nonzero().flatten()
        if not len(ids):
            return
        self.active[ids] = True
        self.remaining[ids] -= 1
        for value in (self.took_off, self.landed, self.apex_paid, self.landing_paid, self.invalid):
            value[ids] = False
        self.first_touch[ids] = False
        self.elapsed[ids] = 0
        self.air_time[ids] = 0
        self.stable_time[ids] = 0
        self.touchdown_time[ids] = -1
        self.height[ids] = (
            uniform(self.settings["height_range_m"], (len(ids),), self.device)
            if target_height is None
            else target_height[ids]
        )
        self.start_z[ids] = z[ids]
        self.apex_z[ids] = z[ids]
~~~

</details>


<details markdown="1"><summary>update</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/jump.py:87>)
~~~python
def update(
        self,
        dt: float,
        age: torch.Tensor,
        z: torch.Tensor,
        vz: torch.Tensor,
        contact: torch.Tensor,
        stable: torch.Tensor,
        valid_landing: torch.Tensor,
        obstacle_contact: torch.Tensor,
    ) -> None:
        self.apex_pulse.zero_()
        self.landing_pulse.zero_()
        self.touchdown_pulse.zero_()
        self.finished.zero_()
        self.elapsed += dt * self.active
        no_contact = ~contact.any(-1)
        can_takeoff = self.active & ~self.landed & (self.elapsed >= self.settings["crouch_duration_s"])
        self.took_off |= can_takeoff & no_contact
        flight = self.active & self.took_off & ~self.landed
        self.air_time += dt * flight * no_contact
        self.apex_z = torch.where(flight, torch.maximum(self.apex_z, z), self.apex_z)
        self.apex_pulse = flight & (vz <= 0) & ~self.apex_paid
        self.apex_paid |= self.apex_pulse
        self.invalid |= self.active & obstacle_contact
        # Invalid first touchdown cannot become success by driving off the roof later.
        new_touch = flight & contact.all(-1) & ~self.first_touch
        self.invalid |= new_touch & ~valid_landing
        self.first_touch |= new_touch
        first_touch = flight[:, None] & contact & (self.touchdown_time < 0)
        self.touchdown_time = torch.where(first_touch, self.elapsed[:, None], self.touchdown_time)
        self.touchdown_pulse = flight & contact.all(-1)
        self.landed |= self.touchdown_pulse
        landing_ok = self.active & self.landed & contact.all(-1) & stable & valid_landing & ~self.invalid
        self.stable_time = torch.where(landing_ok, self.stable_time + dt, 0)
        self.landing_pulse = (self.stable_time >= self.settings["landing_stable_s"]) & ~self.landing_paid
        self.landing_paid |= self.landing_pulse
        # Keep the event alive through the required post-landing validation window.
        expired = self.elapsed >= self.settings["event_duration_s"] + self.settings["landing_stable_s"]
        finished = self.active & (expired | self.landing_pulse)
        self.finished = finished
        ids = finished.nonzero().flatten()
        self.next_trigger[ids] = age[ids] + uniform(self.settings["between_events_s"], (len(ids),), self.device)
        self.active[ids] = False
~~~

</details>


<details markdown="1"><summary>phase</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/jump.py:133>)
~~~python
def phase(self) -> torch.Tensor:
        return (self.elapsed / self.settings["event_duration_s"]).clamp(0, 1)
~~~

</details>


<details markdown="1"><summary>references</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/jump.py:136>)
~~~python
def references(self, vz: torch.Tensor, wheel_clearance: torch.Tensor, gravity: float) -> dict[str, torch.Tensor]:
        flight = self.active & self.took_off & ~self.landed
        # Ballistic time remaining, evaluated only for the descending phase.
        time_to_ground = (vz + torch.sqrt(vz.square() + 2 * gravity * wheel_clearance.clamp_min(0))) / gravity
        prepare = flight & (vz < 0) & (time_to_ground < self.settings["landing_prepare_time_s"])
        return {
            "crouch": self.active & (self.elapsed < self.settings["crouch_duration_s"]),
            "push": self.active & ~self.took_off & (self.elapsed >= self.settings["crouch_duration_s"]),
            "flight": flight,
            "prepare": prepare,
            "tuck": flight & ~prepare,
            "takeoff_velocity": torch.sqrt(2 * gravity * self.height),
        }
~~~

</details>


## 我们 curriculum.py


<details markdown="1"><summary>__init__</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/curriculum.py:147>)
~~~python
def __init__(self, settings: dict, device: str, levels: tuple[float, ...] | None = None):
        self.settings = settings
        self.levels = (
            torch.linspace(*settings["height_range_m"], 5, device=device)
            if levels is None
            else torch.tensor(levels, device=device)
        )
        self.attempts = torch.zeros_like(self.levels)
        self.successes = torch.zeros_like(self.levels)
        self.anneal_start = torch.full_like(self.levels, -1)
        self.maximum_level = 0
~~~

</details>


<details markdown="1"><summary>record_landing</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/curriculum.py:24>)
~~~python
def record_landing(self, successful: torch.Tensor) -> None:
        self.landing_events += successful.numel()
        self.landing_successes += int(successful.sum())
~~~

</details>


<details markdown="1"><summary>discard_landing</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/curriculum.py:28>)
~~~python
def discard_landing(self) -> None:
        """Drop the landing counts of the open window, e.g. when they belong to a height band no longer newest."""
        self.landing_events = self.landing_successes = 0
        self.last_landing_rate = None
~~~

</details>


<details markdown="1"><summary>restart</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/curriculum.py:96>)
~~~python
def restart(self) -> None:
        """Back to the first level with a fresh window, e.g. to resume a run from the easiest heights."""
        self.level = self.events = self.successes = 0
        self.last_rate = None
~~~

</details>


<details markdown="1"><summary>record</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/curriculum.py:163>)
~~~python
def record(self, bins: torch.Tensor, successful: torch.Tensor, iteration: float) -> None:
        if not bins.numel():
            return
        self.attempts.scatter_add_(0, bins, torch.ones_like(bins, dtype=torch.float))
        self.successes.scatter_add_(0, bins, successful.float())
        rate = self.successes / self.attempts.clamp_min(1)
        learned = (self.attempts >= self.settings["curriculum_min_events"]) & (
            rate >= self.settings["guidance_success_threshold"]
        )
        self.anneal_start = torch.where(learned & (self.anneal_start < 0), iteration, self.anneal_start)
        if bool(learned[self.maximum_level]) and self.maximum_level < len(self.levels) - 1:
            self.maximum_level += 1
~~~

</details>


<details markdown="1"><summary>state_dict</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/curriculum.py:182>)
~~~python
def state_dict(self) -> dict:
        return dict(
            attempts=self.attempts,
            successes=self.successes,
            anneal_start=self.anneal_start,
            maximum_level=self.maximum_level,
        )
~~~

</details>


<details markdown="1"><summary>load_state_dict</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/curriculum.py:190>)
~~~python
def load_state_dict(self, state: dict) -> None:
        self.attempts.copy_(state["attempts"])
        self.successes.copy_(state["successes"])
        self.anneal_start.copy_(state["anneal_start"])
        self.maximum_level = state["maximum_level"]
~~~

</details>


<details markdown="1"><summary>upper</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/curriculum.py:89>)
~~~python
def upper(self) -> float:
        return self.levels[self.level]
~~~

</details>


<details markdown="1"><summary>band_floor</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/curriculum.py:93>)
~~~python
def band_floor(self) -> float:
        return self.levels[self.level - 1] if self.level else self.low
~~~

</details>


<details markdown="1"><summary>sample</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/curriculum.py:159>)
~~~python
def sample(self, count: int) -> tuple[torch.Tensor, torch.Tensor]:
        bins = torch.randint(self.maximum_level + 1, (count,), device=self.levels.device)
        return bins, self.levels[bins]
~~~

</details>


<details markdown="1"><summary>guidance</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/curriculum.py:176>)
~~~python
def guidance(self, bins: torch.Tensor, iteration: float) -> torch.Tensor:
        start = self.anneal_start[bins]
        progress = ((iteration - start) / self.settings["guidance_decay_iterations"]).clamp(0, 1)
        progress = torch.where(start >= 0, progress, 0)
        return 1 - progress * (1 - self.settings["guidance_final_scale"])
~~~

</details>


## 我们 commands.py


<details markdown="1"><summary>uniform</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/commands.py:10>)
~~~python
def uniform(bounds: tuple[float, float], shape: tuple[int, ...], device: str) -> torch.Tensor:
    return bounds[0] + torch.rand(shape, device=device) * (bounds[1] - bounds[0])
~~~

</details>


<details markdown="1"><summary>__init__</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/commands.py:15>)
~~~python
def __init__(self, cfg: TrainingConfig, count: int, device: str):
        self.cfg, self.device = cfg, device
        self.family = TASKS[cfg.task].policy
        self.settings = cfg.settings["commands"]
        self.value = torch.zeros(count, 3, device=device)
        self.target = torch.zeros_like(self.value)
        self.height = torch.zeros(count, 1, device=device)
        self.height_rate = torch.zeros(count, device=device)  # slewed height command rate, m/s
        self.target_height = torch.zeros_like(self.height)
        self.remaining = torch.zeros(count, device=device)
        self.height_remaining = torch.zeros_like(self.remaining)
        self.translation = torch.zeros(count, 2, device=device)
        self.translation_target = torch.zeros_like(self.translation)
        self.reference_yaw = torch.zeros_like(self.remaining)
        self.rates = self.value.new_tensor(
            [self.settings["linear_slew_m_s2"], self.settings["linear_slew_m_s2"], self.settings["angular_slew_rad_s2"]]
        )
        self.command_fraction = cfg.settings["command_curriculum"]["initial_fraction"]
        self.free_started = torch.zeros(count, dtype=torch.bool, device=device)
        self.course = None
~~~

</details>


<details markdown="1"><summary>reset</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/commands.py:36>)
~~~python
def reset(self, ids: torch.Tensor) -> None:
        self.free_started[ids] = False
        self.value[ids] = 0
        self.remaining[ids] = 0
        self.height_remaining[ids] = 0
        self.translation[ids] = 0
        self._resample(ids)
        self._resample_height(ids)
        self.height[ids] = self.target_height[ids]
        self.height_rate[ids] = 0
~~~

</details>


<details markdown="1"><summary>_resample</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/commands.py:47>)
~~~python
def _resample(self, ids: torch.Tensor) -> None:
        n = len(ids)
        if not n:
            return
        self.remaining[ids] = uniform(self.settings["segment_duration_s"], (n,), self.device)
        self.target[ids] = 0
        if self.cfg.task == "p1-stairs":
            course = self.course
            self.remaining[ids] = uniform(self.cfg.stage["course"]["segment_duration_s"], (n,), self.device)
            for k, name in enumerate(course.names):
                selected = ids[course.group[ids] == k]
                profile = self.cfg.stage["terrain"]["profiles"][name]
                bounds = profile["speed_range_m_s"]
                if profile["command_mode"] == "free":
                    fraction = (course.episode_speed_fraction[selected] - course.p["minimum_speed_fraction"]) / (
                        1 - course.p["minimum_speed_fraction"]
                    )
                    start = self.value.new_tensor(profile["start_speed_range_m_s"])
                    scaled = start + fraction[:, None] * (self.value.new_tensor(bounds) - start)
                    speed = scaled[:, 0] + torch.rand(len(selected), device=self.device) * (scaled[:, 1] - scaled[:, 0])
                    limits = profile["free_yaw_limit_range_rad_s"]
                    yaw_limit = limits[0] + fraction * (limits[1] - limits[0])
                    yaw = (2 * torch.rand(len(selected), device=self.device) - 1) * yaw_limit
                    kinds = (
                        torch.multinomial(
                            self.value.new_tensor(course.p["free_segment_probabilities"]),
                            len(selected),
                            replacement=True,
                        )
                        if len(selected)
                        else selected
                    )
                    sign = torch.where(torch.rand(len(selected), device=self.device) < 0.5, -1.0, 1.0)
                    vx = torch.where((kinds == 1) | (kinds == 3), speed * sign, 0.0)
                    wz = torch.where((kinds == 2) | (kinds == 3), yaw, 0.0)
                    # Reach the obstacle surface before allowing stand/spin samples on the safe spawn pad.
                    entered = course.surface_time[selected] > 0
                    self.target[selected, 0] = torch.where(entered, vx, speed * course.forward_sign[selected])
                    self.target[selected, 2] = torch.where(entered, wz, 0.0)
                    continue
                # SCUT cfg_utils.py:281-313: axis-aligned travel, slow/fast ranges, limited turning.
                if profile["command_mode"] == "motion":
                    kinds = (
                        torch.multinomial(
                            self.value.new_tensor(course.p["motion_segment_probabilities"]),
                            len(selected),
                            replacement=True,
                        )
                        if len(selected)
                        else selected
                    )
                    speed = uniform((-bounds[1], bounds[1]), (len(selected),), self.device)
                    yaw = uniform(profile["yaw_range_rad_s"], (len(selected),), self.device)
                    envelope = course.flat_levels[course.episode_flat_level[selected]]
                    speed *= envelope[:, 0]
                    yaw *= envelope[:, 1]
                    small = uniform(course.p["small_turn_range_rad_s"], (len(selected),), self.device)
                    small *= torch.where(torch.rand(len(selected), device=self.device) < 0.5, -1.0, 1.0)
                    small *= envelope[:, 1]
                    yaw = torch.where(
                        torch.rand(len(selected), device=self.device) < course.p["small_turn_probability"], small, yaw
                    )
                    self.target[selected, 0] = torch.where((kinds == 1) | (kinds == 3), speed, 0.0)
                    self.target[selected, 2] = torch.where((kinds == 2) | (kinds == 3), yaw, 0.0)
                    self.target[selected, 2] = torch.where(
                        kinds == 3,
                        self.target[selected, 2].clamp(
                            -self.settings["combined_wz_limit_rad_s"], self.settings["combined_wz_limit_rad_s"]
                        ),
                        self.target[selected, 2],
                    )
                else:
                    fraction = (course.episode_speed_fraction[selected] - course.p["minimum_speed_fraction"]) / (
                        1 - course.p["minimum_speed_fraction"]
                    )
                    start = self.value.new_tensor(profile["start_speed_range_m_s"])
                    scaled = start + fraction[:, None] * (self.value.new_tensor(bounds) - start)
                    speed = scaled[:, 0] + torch.rand(len(selected), device=self.device) * (scaled[:, 1] - scaled[:, 0])
                    self.target[selected, 0] = speed * course.forward_sign[selected]
                    self.target[selected, 2] = uniform(profile["yaw_range_rad_s"], (len(selected),), self.device)
            return
        if self.cfg.task == "p3-tunnel":
            self.target[ids, 0] = uniform(self.cfg.stage["tunnel"]["vx_range_m_s"], (n,), self.device)
            return
        if self.family == "p2":
            stage = self.cfg.stage
            low = uniform(stage["spin_low_range_rad_s"], (n,), self.device)
            high = uniform(stage["spin_high_range_rad_s"], (n,), self.device)
            self.target[ids, 2] = torch.where(torch.rand(n, device=self.device) < 0.5, low, high)
            self.target[ids, 2] *= torch.where(torch.rand(n, device=self.device) < 0.5, -1.0, 1.0)
            speed = uniform(stage["translation_speed_range_m_s"], (n,), self.device)
            heading = uniform((-math.pi, math.pi), (n,), self.device)
            self.translation_target[ids] = torch.stack((speed * heading.cos(), speed * heading.sin()), -1)
            self.reference_yaw[ids] = stage["reference_yaw_rad"]
            return
        kinds = torch.multinomial(self.value.new_tensor(self.settings["segment_probabilities"]), n, replacement=True)
        vx = uniform(self.settings["vx_range_m_s"], (n,), self.device) * self.command_fraction
        wz = uniform(self.settings["wz_range_rad_s"], (n,), self.device) * self.command_fraction
        if self.family == "p1":
            # “直行加转向”片段的转向单独封顶：课程放大后的转向上限超过 combined_wz_limit_rad_s 时，
            # 把这类片段的转向等比例缩到该上限以内（仍是均匀分布）；纯转向、纯直行和冲刺片段不变。
            wz_limit = max(abs(v) for v in self.settings["wz_range_rad_s"]) * self.command_fraction  # rad/s
            scale = min(1.0, self.settings["combined_wz_limit_rad_s"] / wz_limit)
            wz = torch.where(kinds == 3, wz * scale, wz)
        self.target[ids, 0] = torch.where((kinds == 1) | (kinds >= 3), vx, 0)
        self.target[ids, 2] = torch.where((kinds == 2) | (kinds == 3), wz, 0)
        dash = uniform(self.settings["dash_range_m_s"], (n,), self.device) * self.command_fraction
        self.target[ids, 0] = torch.where(kinds == 4, dash, self.target[ids, 0])
        # Stop/reverse segments depend on the preceding segment, not independent random commands.
        reverse = -self.value[ids, 0]
        reverse = torch.where(torch.rand(n, device=self.device) < 0.5, reverse, 0)
        self.target[ids, 0] = torch.where(kinds == 5, reverse, self.target[ids, 0])
~~~

</details>


<details markdown="1"><summary>_resample_height</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/commands.py:160>)
~~~python
def _resample_height(self, ids: torch.Tensor) -> None:
        if self.cfg.task == "p1-stairs":
            p = self.cfg.stage["course"]
            for k, name in enumerate(self.course.names):
                selected = ids[self.course.group[ids] == k]
                bounds = self.cfg.stage["terrain"]["profiles"][name]["height_range_m"]
                if self.cfg.stage["terrain"]["profiles"][name]["kind"] == "flat":
                    # Cover the full usable extension range, including after USD geometry is regenerated.
                    bounds = (
                        bounds[0],
                        self.cfg.shared["spring_extension_height_m"] - self.cfg.stage["step_height_margin_m"],
                    )
                    fraction = self.course.flat_levels[self.course.episode_flat_level[selected], 2]
                    self.target_height[selected, 0] = (
                        bounds[0] + torch.rand(len(selected), device=self.device) * (bounds[1] - bounds[0]) * fraction
                    )
                    continue
                self.target_height[selected, 0] = uniform(bounds, (len(selected),), self.device)
            self.height_remaining[ids] = uniform(p["height_duration_s"], (len(ids),), self.device)
            return
        self.target_height[ids, 0] = uniform(self.settings["height_range_m"], (len(ids),), self.device)
        self.height_remaining[ids] = uniform(self.settings["height_duration_s"], (len(ids),), self.device)
~~~

</details>


<details markdown="1"><summary>step</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/commands.py:183>)
~~~python
def step(self, dt: float, frozen: torch.Tensor) -> None:
        if self.cfg.task == "p1-stairs":
            entered = self.course.free_commands & (self.course.surface_time > 0)
            self.remaining[entered & ~self.free_started] = 0
            self.free_started |= entered
        self.remaining -= dt
        self.height_remaining -= dt
        self._resample(((self.remaining <= 0) & ~frozen).nonzero().flatten())
        self._resample_height(((self.height_remaining <= 0) & ~frozen).nonzero().flatten())
        self.value = torch.where(frozen[:, None], self.value, slew(self.value, self.target, self.rates, dt))
        previous = self.height
        self.height = torch.where(
            frozen[:, None], self.height, slew(self.height, self.target_height, self.settings["height_slew_m_s"], dt)
        )
        self.height_rate.copy_((self.height - previous)[:, 0] / dt)
        self.translation = slew(self.translation, self.translation_target, self.settings["linear_slew_m_s2"], dt)
~~~

</details>


<details markdown="1"><summary>mode</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/commands.py:200>)
~~~python
def mode(
        self,
        yaw: torch.Tensor,
        stair: torch.Tensor,
        recovering: torch.Tensor,
        jump_active: torch.Tensor,
        jump_height: torch.Tensor,
        phase: torch.Tensor,
    ) -> torch.Tensor:
        mode = self.value.new_zeros(len(yaw), 7)
        if self.family == "p1":
            mode[:, 0] = 1
            mode[:, 1] = stair
            mode[:, 3] = recovering
        elif self.family == "p2":
            mode[:, 1] = 1
            mode[:, 2] = torch.linalg.vector_norm(self.translation, dim=-1)
            heading = torch.atan2(self.translation[:, 1], self.translation[:, 0])
            mode[:, 3], mode[:, 4] = heading.sin(), heading.cos()
            relative = self.reference_yaw - yaw
            mode[:, 5], mode[:, 6] = relative.sin(), relative.cos()
        else:
            mode[:, 4] = jump_active
            mode[:, 5] = jump_height * self.cfg.policy.height_scale * jump_active
            mode[:, 6] = phase * jump_active
        return mode
~~~

</details>


<details markdown="1"><summary>world_translation</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/commands.py:227>)
~~~python
def world_translation(self) -> torch.Tensor:
        return rotate_xy(self.translation, self.reference_yaw)
~~~

</details>


## 我们 stairs.py


<details markdown="1"><summary>advance_height_assist</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/stairs.py:9>)
~~~python
def advance_height_assist(
    trigger: torch.Tensor,
    supported: torch.Tensor,
    remaining: torch.Tensor,
    target: torch.Tensor,
    previous_trigger: torch.Tensor,
    stage: dict,
    dt: float,
    ceiling: float,
    command_height: torch.Tensor,
    step_rise: torch.Tensor,
    randomize: bool,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    # Keep assistance throughout a slow approach, then hold briefly after the edge leaves the scan.
    # Actual guide contact cancels it for retraction; no contact-termination exemption is added.
    entered = trigger & ~previous_trigger & (remaining <= 0) & ~supported
    # Root clearance above the next tread; clamp the interval BEFORE sampling so
    # short steps keep height diversity instead of accumulating samples at the ceiling.
    low, high = stage["step_height_clearance_range_m"]
    lower = torch.maximum(command_height, step_rise + low).clamp(max=ceiling)
    upper = torch.maximum(lower, step_rise + high).clamp(max=ceiling)
    fraction = torch.rand_like(target) if randomize else 0.5
    sampled = lower + fraction * (upper - lower)
    target = torch.where(entered, sampled, target)
    remaining = torch.where(
        trigger & (entered | (remaining > 0)), stage["step_height_hold_s"], (remaining - dt).clamp_min(0)
    )
    remaining = torch.where(supported, 0.0, remaining)
    return remaining, target, trigger
~~~

</details>


<details markdown="1"><summary>terrain_columns</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/stairs.py:40>)
~~~python
def terrain_columns(profiles: dict, columns: int) -> list[str]:
    """Same deterministic column assignment as terrain_generator.py:241-249."""
    names = list(profiles)
    cumulative = np.cumsum([profiles[k]["proportion"] for k in names])
    return [names[int(np.searchsorted(cumulative, i / columns + 0.001, side="right"))] for i in range(columns)]
~~~

</details>


<details markdown="1"><summary>step_layout</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/stairs.py:47>)
~~~python
def step_layout(terrain: dict, profile: dict, difficulty: float) -> tuple[list[float], list[float]]:
    """Tile-local x edges and interval heights (m); positive travel is world +x."""
    count = profile["step_count"]
    low, high = terrain["step_height_range_m"]
    h = low + difficulty * (high - low)
    width = terrain["step_width_m"]
    entry, exit_x = terrain["entry_x_m"], terrain["exit_x_m"]
    if profile["kind"] == "up":
        return [entry + i * width for i in range(count)], [i * h for i in range(count + 1)]
    if profile["kind"] == "down":
        return [entry + i * width for i in range(count)], [(count - i) * h for i in range(count + 1)]
    if profile["kind"] == "mixed":
        edges = [entry + i * width for i in range(count)]
        edges += [exit_x - (count - 1 - i) * width for i in range(count)]
        return edges, [i * h for i in range(count + 1)] + [i * h for i in reversed(range(count))]
    if "surface_x_range_m" in terrain and profile["kind"] in ("grid", "slope", "rough"):
        return list(terrain["surface_x_range_m"]), [0.0, 0.0, 0.0]
    return [entry, exit_x], [0.0, 0.0, 0.0]
~~~

</details>


<details markdown="1"><summary>grid_layout</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/stairs.py:67>)
~~~python
def grid_layout(terrain: dict, difficulty: float) -> tuple[list[tuple[float, float, float, float]], float]:
    """Shared non-overlapping bar rectangles for Isaac and MuJoCo; old snapshots keep their four bars."""
    g = terrain["grid"]
    rng = np.random.default_rng(np.random.SeedSequence([terrain["seed"], round(difficulty * 1000000)]))
    width = rng.uniform(*g["width_range_m"])
    height = g["height_range_m"][0] + difficulty * np.ptp(g["height_range_m"])
    spacing_x, spacing_y = rng.uniform(*g["spacing_range_m"], size=2)
    start, end = (
        terrain["surface_x_range_m"] if "surface_x_range_m" in terrain else (terrain["entry_x_m"], terrain["exit_x_m"])
    )
    cx, cy = (start + end) / 2, terrain["tile_size_m"][1] / 2
    if "surface_x_range_m" in terrain:
        nx = int((end - start - width) / (2 * spacing_x))
        ny = int((2 * g["half_span_m"] - width) / (2 * spacing_y))
        xs = cx + np.arange(-nx, nx + 1) * spacing_x
        ys = cy + np.arange(-ny, ny + 1) * spacing_y
    else:
        xs = cx + np.array([-0.5, 0.5]) * spacing_x
        ys = cy + np.array([-0.5, 0.5]) * spacing_y
    vertical = [(x - width / 2, x + width / 2) for x in xs]
    rectangles = [(a, b, cy - g["half_span_m"], cy + g["half_span_m"]) for a, b in vertical]
    for y in ys:
        left = start
        for a, b in [*vertical, (end, end)]:
            if a > left:
                rectangles.append((left, a, y - width / 2, y + width / 2))
            left = b
    return rectangles, float(height)
~~~

</details>


<details markdown="1"><summary>scan_course</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/stairs.py:97>)
~~~python
def scan_course(
    hits: torch.Tensor,
    position: torch.Tensor,
    yaw: torch.Tensor,
    wheels: torch.Tensor,
    direction: torch.Tensor,
    fallback: torch.Tensor,
    settings: dict,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Wheel ground, up/down distances and nearest upward riser height, all in metres."""
    valid = torch.isfinite(hits).all(-1)
    clean = torch.where(valid[..., None], hits, position[:, None])
    delta = clean[:, :, :2] - position[:, None, :2]
    c, s = yaw.cos()[:, None], yaw.sin()[:, None]
    x = c * delta[:, :, 0] + s * delta[:, :, 1]
    y = -s * delta[:, :, 0] + c * delta[:, :, 1]
    wd = wheels[:, :, :2] - position[:, None, :2]
    wx = c * wd[:, :, 0] + s * wd[:, :, 1]
    wy = -s * wd[:, :, 0] + c * wd[:, :, 1]
    # A narrow ray neighbourhood around each wheel, not the median of both sides of a step.
    distance = (clean[:, None, :, :2] - wheels[:, :, None, :2]).square().sum(-1)
    distance = torch.where(valid[:, None], distance, float("inf"))
    nearest = distance.argmin(-1)
    support = clean[:, :, 2].gather(1, nearest)
    local = distance.amin(-1) <= settings["scan_resolution_m"] ** 2
    support = torch.where(local, support, fallback[:, None])
    ground = support.mean(-1)
    # Bin yaw-aligned rays in x, averaging only rays in the corresponding wheel lane.
    spacing, half = settings["scan_resolution_m"], settings["scan_half_length_m"]
    bins = round(2 * half / spacing) + 1
    index = ((x + half) / spacing).round().long().clamp(0, bins - 1)
    lane = valid[:, None] & ((y[:, None] - wy[:, :, None]).abs() <= settings["scan_lane_half_width_m"])
    total = x.new_zeros((len(x), 2, bins))
    counts = torch.zeros_like(total)
    indices = index[:, None].expand(-1, 2, -1)
    total.scatter_add_(2, indices, torch.where(lane, clean[:, None, :, 2], 0.0))
    counts.scatter_add_(2, indices, lane.float())
    z = total / counts.clamp_min(1)
    up = torch.full_like(ground, float("inf"))
    down = up.clone()
    rise = torch.zeros_like(ground)
    # One/two-bin jumps handle a riser split by slight yaw; same-sign outer gradients reject a slope.
    # Opposite-sign neighbours are allowed: a narrow bar genuinely has adjacent up/down edges.
    for span in (1, 2):
        start = z[:, :, 1 : -span - 1]
        end = z[:, :, 1 + span : -1]
        heights = end - start
        left = start - z[:, :, : -span - 2]
        right = z[:, :, span + 2 :] - end
        gradient = torch.maximum((left * heights.sign()).clamp_min(0), (right * heights.sign()).clamp_min(0))
        good = counts.unfold(-1, span + 3, 1).amin(-1) >= settings["scan_min_rays"]
        good &= heights.abs() - span * gradient >= settings["edge_gradient_excess_m"]
        centers = (torch.arange(start.shape[-1], device=x.device) + 1 + span / 2) * spacing - half
        ahead = (centers[None, None] - wx[:, :, None]) * direction[:, None, None]
        good &= (ahead > 0) & (ahead <= settings["detection_distance_m"])
        signed = heights * direction[:, None, None]
        up_ahead = torch.where(good & (signed >= settings["edge_height_m"]), ahead, float("inf"))
        nearest_up = up_ahead.amin((1, 2))
        nearest_rise = torch.where(
            torch.isfinite(up_ahead) & (up_ahead == nearest_up[:, None, None]), signed, 0.0
        ).amax((1, 2))
        rise = torch.where(
            nearest_up < up, nearest_rise, torch.where(nearest_up == up, torch.maximum(rise, nearest_rise), rise)
        )
        up = torch.minimum(up, nearest_up)
        down = torch.minimum(
            down, torch.where(good & (signed <= -settings["edge_height_m"]), ahead, float("inf")).amin((1, 2))
        )
    return ground, up, down, rise
~~~

</details>


<details markdown="1"><summary>__init__</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/stairs.py:169>)
~~~python
def __init__(self, count: int, stage: dict, device: str):
        self.p, self.terrain = stage["course"], stage["terrain"]
        self.names = list(self.terrain["profiles"])
        columns = terrain_columns(self.terrain["profiles"], self.terrain["columns"])
        self.column_groups = torch.tensor([self.names.index(k) for k in columns], device=device)
        self.terrain_type = torch.zeros(count, dtype=torch.long, device=device)
        self.first_column = torch.tensor([columns.index(k) for k in self.names], device=device)
        self.last_column = torch.tensor([len(columns) - 1 - columns[::-1].index(k) for k in self.names], device=device)
        self.group = torch.zeros(count, dtype=torch.long, device=device)
        self.motion_groups = torch.tensor(
            [self.terrain["profiles"][k]["command_mode"] == "motion" for k in self.names], device=device
        )
        self.motion = torch.zeros(count, dtype=torch.bool, device=device)
        self.free_groups = torch.tensor(
            [self.terrain["profiles"][k]["command_mode"] == "free" for k in self.names], device=device
        )
        self.free_commands = torch.zeros_like(self.motion)
        self.surface_time = torch.zeros(count, device=device)
        self.step_groups = torch.tensor(
            [self.terrain["profiles"][k]["kind"] in ("up", "down", "mixed") for k in self.names],
            device=device,
        )
        self.steps = torch.zeros_like(self.motion)
        self.heading = torch.zeros_like(self.motion)
        self.training_level = torch.zeros(count, dtype=torch.long, device=device)
        self.motion_boundary = torch.zeros_like(self.motion)
        self.traversed = torch.zeros_like(self.motion)
        self.traverse_hold = torch.zeros(count, device=device)
        self.guide_support = torch.zeros_like(self.motion)
        self.yaw_track_sum = torch.zeros(count, device=device)
        self.drop_terrain = torch.tensor(
            [self.terrain["profiles"][k]["kind"] in ("down", "mixed", "grid") for k in self.names],
            device=device,
        )
        self.age = torch.zeros(count, device=device)
        self.diagnostics = torch.zeros(count, 13, device=device)
        self.crossed = torch.zeros(count, 4, dtype=torch.bool, device=device)
        self.edges = torch.full((count, 4), float("inf"), device=device)
        self.edge_count = torch.zeros(count, dtype=torch.long, device=device)
        self.arrived = torch.zeros_like(self.motion)
        self.success = torch.zeros_like(self.motion)
        self.finished = torch.zeros_like(self.motion)
        self.escaped = torch.zeros_like(self.motion)
        self.hold = torch.zeros(count, device=device)
        self.track_sum = torch.zeros(count, device=device)
        self.track_count = torch.zeros(count, device=device)
        self.last_x = torch.zeros(count, device=device)
        self.seen_support = torch.zeros(count, 2, dtype=torch.bool, device=device)
        self.contact = torch.zeros_like(self.seen_support)
        self.flight_time = torch.zeros(count, 2, device=device)
        self.support_z = torch.zeros(count, 2, device=device)
        self.previous_down = torch.zeros(count, 2, device=device)
        self.last_tick = torch.full((count,), -1, dtype=torch.long, device=device)
        self.impact = torch.zeros(count, device=device)
        self.cushion = torch.zeros(count, device=device)
        self.flying = torch.zeros(count, dtype=torch.bool, device=device)
        self.forward_sign = torch.ones(count, device=device)
        # A low step cannot promote speeds for an unmastered high step.
        self.speed_fraction = torch.full(
            (len(self.names), self.terrain["rows"]), self.p["initial_speed_fraction"], device=device
        )
        self.completed = torch.zeros_like(self.speed_fraction)
        self.passed = torch.zeros_like(self.speed_fraction)
        self.latest_pass = torch.zeros_like(self.speed_fraction)
        self.episode_speed_fraction = torch.zeros(count, device=device)
        # Per-rollout counts: resets, eligible, successes, crossings, stops, neutral exits.
        self.reset_counts = torch.zeros(len(self.names), 6, device=device)
        flat = self.p["flat_curriculum"]
        self.flat_levels = torch.tensor(flat["levels"], device=device)
        self.flat_level = torch.zeros((), dtype=torch.long, device=device)
        self.flat_completed = torch.zeros((), device=device)
        self.flat_passed = torch.zeros((), device=device)
        self.flat_latest_pass = torch.zeros((), device=device)
        self.episode_flat_level = torch.zeros(count, dtype=torch.long, device=device)
        self.flat_error_sum = torch.zeros(count, 3, device=device)
        self.flat_command_sum = torch.zeros(count, 2, device=device)
        self.flat_sample_count = torch.zeros(count, device=device)
~~~

</details>


<details markdown="1"><summary>reset</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/stairs.py:247>)
~~~python
def reset(self, ids: torch.Tensor, terrain_types: torch.Tensor, origin: torch.Tensor, tick: int) -> None:
        self.group[ids] = self.column_groups[terrain_types]
        self.terrain_type[ids] = terrain_types
        self.episode_speed_fraction[ids] = self.speed_fraction[self.group[ids], self.training_level[ids]]
        self.motion[ids] = self.motion_groups[self.group[ids]]
        # Freeze the command envelope for each episode; old-stage finishes cannot grade a new stage.
        self.episode_flat_level[ids] = self.flat_level
        self.episode_speed_fraction[ids] = torch.where(
            self.motion[ids], self.flat_levels[self.flat_level, 0], self.episode_speed_fraction[ids]
        )
        self.free_commands[ids] = self.free_groups[self.group[ids]]
        self.steps[ids] = self.step_groups[self.group[ids]]
        self.heading[ids] = (~self.motion[ids] & ~self.free_commands[ids]) & (
            torch.rand(len(ids), device=ids.device) < self.p["heading_probability"]
        )
        self.forward_sign[ids] = torch.where(
            torch.rand(len(ids), device=ids.device) < self.p["reverse_probability"], -1.0, 1.0
        )
        self.edges[ids] = float("inf")
        for k, name in enumerate(self.names):
            selected = ids[self.group[ids] == k]
            edges, _ = step_layout(self.terrain, self.terrain["profiles"][name], 0.0)
            self.edges[selected, : len(edges)] = self.edges.new_tensor(edges) - self.terrain["spawn_x_m"]
            self.edge_count[selected] = len(edges)
        for field in (
            self.age,
            self.flat_error_sum,
            self.flat_command_sum,
            self.flat_sample_count,
            self.surface_time,
            self.diagnostics,
            self.crossed,
            self.arrived,
            self.success,
            self.finished,
            self.escaped,
            self.hold,
            self.track_sum,
            self.track_count,
            self.last_x,
            self.seen_support,
            self.contact,
            self.flight_time,
            self.previous_down,
            self.impact,
            self.cushion,
            self.flying,
            self.motion_boundary,
            self.traversed,
            self.traverse_hold,
            self.guide_support,
            self.yaw_track_sum,
        ):
            field[ids] = 0
        self.support_z[ids] = origin[:, 2:3]
        self.last_tick[ids] = tick
~~~

</details>


<details markdown="1"><summary>begin_step</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/stairs.py:304>)
~~~python
def begin_step(self) -> None:
        self.impact.zero_()
~~~

</details>


<details markdown="1"><summary>sample</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/stairs.py:307>)
~~~python
def sample(
        self,
        tick: int,
        dt: float,
        force: torch.Tensor,
        wheel_z: torch.Tensor,
        wheel_vz: torch.Tensor,
        guide_supported: torch.Tensor,
    ) -> None:
        use = tick > self.last_tick
        self.last_tick[use] = tick
        contact = force > self.p["contact_force_n"]
        duration = torch.where(contact, 0.0, self.flight_time + dt)
        landing = use[:, None] & contact & ~self.contact & self.seen_support
        landing &= self.drop_terrain[self.group, None]
        landing &= self.flight_time >= self.p["min_flight_s"]
        landing &= self.support_z - wheel_z >= self.p["min_drop_m"]
        # Down-step impact only: pre-contact vertical wheel speed, once per wheel flight; no hip-torque penalty.
        speed = (
            (self.previous_down - self.p["impact_free_speed_m_s"]).clamp_min(0) / self.p["impact_speed_scale_m_s"]
        ).square()
        self.impact += torch.where(landing, speed.clamp_max(self.p["impact_clip"]), 0.0).sum(-1) / 2
        # One bounded cushioning interval per drop, not extended by contact chatter.
        start_cushion = landing.any(-1) & (self.cushion <= 0)
        self.cushion.copy_(torch.where(start_cushion, self.p["cushion_s"], (self.cushion - dt * use).clamp_min(0)))
        self.flight_time.copy_(torch.where(use[:, None], duration, self.flight_time))
        self.support_z.copy_(torch.where(use[:, None] & contact, wheel_z, self.support_z))
        self.seen_support |= use[:, None] & contact
        self.contact.copy_(torch.where(use[:, None], contact, self.contact))
        self.previous_down.copy_(torch.where(use[:, None], (-wheel_vz).clamp_min(0), self.previous_down))
        self.flying.copy_(
            (self.flight_time >= self.p["min_flight_s"]).all(-1) & self.seen_support.all(-1) & ~guide_supported
        )
~~~

</details>


<details markdown="1"><summary>update</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/stairs.py:341>)
~~~python
def update(
        self, state: dict, origin: torch.Tensor, dt: float, terminated: torch.Tensor, reward_parameters: dict
    ) -> None:
        self.age += dt
        x = state["wheel_position_w"][:, :, 0] - origin[:, 0:1]
        center = x.mean(-1)
        sx, sy = self.terrain["tile_size_m"]
        margin = self.terrain["boundary_margin_m"]
        x_margin = self.p["edge_clearance_m"]
        x_low = torch.where(self.motion, -sx / 2 + margin, x_margin - self.terrain["spawn_x_m"])
        x_high = torch.where(self.motion, sx / 2 - margin, sx - self.terrain["spawn_x_m"] - x_margin)
        y_half = sy / 2 - margin
        y_max = (state["wheel_position_w"][:, :, 1] - origin[:, 1:2]).abs().amax(-1)
        # A pure boundary exit is a neutral truncation; physical termination stays separate.
        self.escaped.copy_((x.amin(-1) < x_low) | (x.amax(-1) > x_high) | (y_max > y_half))
        # Flat tiles form one contiguous homogeneous block; other kinds stay in their own difficulty tile.
        wx = state["wheel_position_w"][:, :, 0]
        wy = state["wheel_position_w"][:, :, 1] - origin[:, 1:2]
        left = (self.first_column[self.group] - self.terrain_type - 0.5) * sy + margin
        right = (self.last_column[self.group] - self.terrain_type + 0.5) * sy - margin
        flat_exit = (
            (wx.abs() > self.terrain["rows"] * sx / 2 - margin) | (wy < left[:, None]) | (wy > right[:, None])
        ).any(-1)
        self.escaped.copy_(torch.where(self.motion, flat_exit, self.escaped))
        self.motion_boundary.copy_(self.motion & self.escaped)
        surface_start, surface_end = self.terrain["surface_x_range_m"]
        on_surface = (
            (x.amin(-1) >= surface_start - self.terrain["spawn_x_m"])
            & (x.amax(-1) <= surface_end - self.terrain["spawn_x_m"])
            & ~self.escaped
        )
        reached = (x.amin(-1)[:, None] >= self.edges + self.p["edge_clearance_m"]) & ~self.escaped[:, None]
        self.crossed |= reached
        goal = self.terrain["finish_x_m"] - self.terrain["spawn_x_m"]
        self.arrived.copy_(
            (x.amin(-1) >= goal)
            & (self.crossed.sum(-1) >= self.edge_count)
            & ~self.escaped
            & ~self.motion
            & ~self.free_commands
        )
        tracking = torch.exp(-state["linear_error"].square() / self.p["tracking_sigma"])
        # Recovery already grades height; do not grade it again through the speed score.
        tracking = torch.where(terminated, 0.0, tracking)
        yaw_tracking = torch.exp(-state["angular_error"].square() / reward_parameters["angular_sigma"])
        yaw_tracking = torch.where(terminated, 0.0, yaw_tracking)
        # At 0.25 m/s, the old exp(-error^2/0.5) grants a stationary robot 0.88.
        # Free-command grading must distinguish tracking from merely remaining upright.
        tolerance = state["tracked_command"].abs() * self.p["free_tracking_relative_error"]
        tolerance += tolerance.new_tensor(self.p["free_tracking_error_floor"])
        free_tracking = torch.exp(-(state["linear_error"] / tolerance[:, 0]).square())
        free_yaw_tracking = torch.exp(-(state["angular_error"] / tolerance[:, 1]).square())
        tracking = torch.where(self.free_commands & ~terminated, free_tracking, tracking)
        yaw_tracking = torch.where(self.free_commands & ~terminated, free_yaw_tracking, yaw_tracking)
        counted = (
            ~self.arrived
            & ~self.flying
            & ~self.guide_support
            & (self.cushion <= 0)
            & (self.age > self.p["tracking_warmup_s"])
        )
        counted &= ~self.free_commands | on_surface
        self.surface_time += dt * (self.free_commands & on_surface & counted)
        self.track_sum += torch.where(counted, tracking, 0.0)
        self.yaw_track_sum += torch.where(counted, yaw_tracking, 0.0)
        self.track_count += counted
        flat_counted = counted & self.motion
        errors = torch.stack(
            (state["linear_error"].abs(), state["angular_error"].abs(), state["height_error"].abs()), -1
        )
        self.flat_error_sum += torch.where(flat_counted[:, None], errors, 0.0)
        self.flat_command_sum += torch.where(flat_counted[:, None], state["tracked_command"].abs(), 0.0)
        self.flat_sample_count += flat_counted
        stable = state["wheel_contact"].all(-1) & ~terminated & ~self.escaped
        stable &= state["undesired_force"].amax(-1) <= reward_parameters["contact_force_n"]
        recovered = stable & (state["height_error"].abs() <= self.p["traversal_height_error_m"])
        recovered &= (state["roll"].abs() < self.p["traversal_tilt_rad"]) & (
            state["pitch"].abs() < self.p["traversal_tilt_rad"]
        )
        recovered &= state["angular_velocity"][:, :2].abs().amax(-1) < self.p["traversal_angular_rad_s"]
        stable &= state["height_error"].abs() <= reward_parameters["height_gate_full_error_m"]
        stable &= (state["roll"].abs() < self.p["finish_tilt_rad"]) & (state["pitch"].abs() < self.p["finish_tilt_rad"])
        stable &= state["angular_velocity"][:, :2].abs().amax(-1) < self.p["finish_angular_rad_s"]
        # Past crossings are diagnostic history: recovery must occur beyond the last edge now.
        cleared = (reached.sum(-1) >= self.edge_count) & ~self.escaped & ~self.motion
        self.traverse_hold.copy_(torch.where(cleared & recovered, self.traverse_hold + dt, 0.0))
        self.traversed |= self.traverse_hold >= self.p["traversal_hold_s"]
        stopped = stable & self.arrived & (state["heading_velocity"].norm(dim=-1) < self.p["finish_speed_m_s"])
        self.hold.copy_(torch.where(stopped, self.hold + dt, 0.0))
        self.finished.copy_(self.hold >= self.p["finish_hold_s"])
        mean = self.track_sum / self.track_count.clamp_min(1)
        task_done = torch.where(
            self.free_commands,
            recovered & on_surface & (self.surface_time >= self.p["free_surface_min_s"]),
            self.traversed | (self.motion & recovered & (self.age >= self.p["minimum_episode_s"])),
        )
        yaw_mean = self.yaw_track_sum / self.track_count.clamp_min(1)
        promote = torch.where(self.free_commands, self.p["free_tracking_promote"], self.p["tracking_promote"])
        self.success.copy_(
            task_done & ~terminated & ~self.escaped & (self.track_count > 0) & (mean >= promote) & (yaw_mean >= promote)
        )
        flat = self.p["flat_curriculum"]
        samples = self.flat_sample_count.clamp_min(1)[:, None]
        allowed = self.flat_error_sum.new_tensor(flat["error_thresholds"]).expand_as(self.flat_error_sum).clone()
        allowed[:, :2] += flat["relative_error"] * self.flat_command_sum / samples
        flat_success = (self.flat_error_sum / samples <= allowed).all(-1)
        flat_success &= task_done & ~terminated & ~self.escaped & (self.flat_sample_count > 0)
        self.success.copy_(torch.where(self.motion, flat_success, self.success))
        self.last_x.copy_(center)
~~~

</details>


<details markdown="1"><summary>curriculum</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/stairs.py:451>)
~~~python
def curriculum(
        self, ids: torch.Tensor, terminated: torch.Tensor, neutral_exit: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        ran = self.age[ids] > 0
        valid = ran & ~neutral_exit
        counts = torch.stack(
            (
                ran,
                valid,
                self.success[ids] & valid & ~terminated,
                self.traversed[ids] & valid & ~terminated,
                self.finished[ids] & valid & ~terminated,
                neutral_exit & ran,
            ),
            -1,
        ).float()
        self.reset_counts.index_add_(0, self.group[ids], counts)
        flat = self.p["flat_curriculum"]
        flat_counted = valid & self.motion[ids] & (self.episode_flat_level[ids] == self.flat_level)
        self.flat_completed += flat_counted.sum()
        self.flat_passed += (flat_counted & self.success[ids] & ~terminated).sum()
        if self.flat_completed >= flat["min_completed_episodes"]:
            self.flat_latest_pass.copy_(self.flat_passed / self.flat_completed)
            delta = (self.flat_latest_pass >= flat["promote_rate"]).long()
            delta -= (self.flat_latest_pass < flat["demote_rate"]).long()
            self.flat_level.copy_((self.flat_level + delta).clamp(0, len(self.flat_levels) - 1))
            self.flat_completed.zero_()
            self.flat_passed.zero_()
        eligible = (
            ((self.age[ids] >= self.p["minimum_episode_s"]) | self.traversed[ids]) & (self.age[ids] > 0) & ~neutral_exit
        )
        average = self.track_sum[ids] / self.track_count[ids].clamp_min(1)
        up = eligible & self.success[ids] & ~terminated
        demote = torch.where(self.free_commands[ids], self.p["free_tracking_demote"], self.p["tracking_demote"])
        down = eligible & ~up & (terminated | ((self.track_count[ids] > 0) & (average < demote)))
        # Premature physical failure is evidence even when the minimum normal evaluation duration was not reached.
        down |= (self.age[ids] > 0) & ~neutral_exit & terminated
        group, level = self.group[ids], self.training_level[ids]
        cell = group * self.terrain["rows"] + level
        current_speed = (self.episode_speed_fraction[ids] - self.speed_fraction[group, level]).abs() < 1e-6
        counted = ~self.motion[ids] & current_speed & ~neutral_exit
        self.completed.view(-1).scatter_add_(0, cell, ((eligible | down) & counted).float())
        self.passed.view(-1).scatter_add_(0, cell, (up & counted).float())
        ready = self.completed >= self.p["speed_window_episodes"]
        rate = self.passed / self.completed.clamp_min(1)
        increase = ready & (rate >= self.p["speed_promote_rate"])
        decrease = ready & (rate < self.p["speed_demote_rate"])
        next_speed = (self.speed_fraction + self.p["speed_increment"] * (increase.float() - decrease.float())).clamp(
            self.p["minimum_speed_fraction"], 1
        )
        changed = next_speed != self.speed_fraction
        self.speed_fraction.copy_(next_speed)
        self.latest_pass.copy_(torch.where(ready, rate, self.latest_pass))
        self.completed[ready] = 0
        self.passed[ready] = 0
        advance = ~self.motion[ids] & current_speed & ~changed[group, level]
        return up & advance, down & advance
~~~

</details>


<details markdown="1"><summary>features</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/stairs.py:509>)
~~~python
def features(self, state: dict, origin: torch.Tensor) -> torch.Tensor:
        length = self.terrain["finish_x_m"] - self.terrain["spawn_x_m"]
        result = torch.cat(
            (
                (self.last_x / length)[:, None],
                (self.crossed.sum(-1) / self.edge_count.clamp_min(1))[:, None],
                (
                    (state["wheel_position_w"][:, :, 1].mean(-1) - origin[:, 1])
                    / (self.terrain["tile_size_m"][1] / 2 - self.terrain["boundary_margin_m"])
                )[:, None],
                (self.hold / self.p["finish_hold_s"])[:, None],
                self.flight_time,
                self.support_z - state["wheel_position_w"][:, :, 2],
                self.seen_support.float(),
                (self.cushion / self.p["cushion_s"])[:, None],
                self.arrived.float()[:, None],
                (self.track_sum / self.track_count.clamp_min(1))[:, None],
                self.episode_speed_fraction[:, None],
                self.motion.float()[:, None],
                self.traversed.float()[:, None],
                (self.traverse_hold / self.p["traversal_hold_s"])[:, None],
                self.guide_support.float()[:, None],
                (self.yaw_track_sum / self.track_count.clamp_min(1))[:, None],
                self.free_commands.float()[:, None],
                (self.surface_time / self.p["free_surface_min_s"])[:, None],
            ),
            -1,
        ).clamp(-1, 1)
        return torch.nan_to_num(result)
~~~

</details>


## 我们 history.py


<details markdown="1"><summary>actor_input_dim</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/history.py:19>)
~~~python
def actor_input_dim(policy: PolicyConfig) -> int:
    return OBS_DIM + (ESTIMATE_DIM if policy.history_frames else 0)
~~~

</details>


<details markdown="1"><summary>estimator_loss</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/history.py:43>)
~~~python
def estimator_loss(
    raw: torch.Tensor, target: torch.Tensor, velocity_coef: float, contact_coef: float
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Velocity MSE plus contact BCE; target is (..., 5) with contacts as 0/1."""
    velocity = F.mse_loss(raw[..., :3], target[..., :3])
    contact = F.binary_cross_entropy_with_logits(raw[..., 3:], target[..., 3:])
    return velocity_coef * velocity + contact_coef * contact, velocity, contact
~~~

</details>


<details markdown="1"><summary>expand_actor_input</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/history.py:93>)
~~~python
def expand_actor_input(actor_state: dict, input_dim: int) -> dict:
    """Zero columns for new actor inputs: the expanded actor reproduces the old one exactly at the start."""
    weight = actor_state["0.weight"]
    if weight.shape[1] > input_dim:
        raise ValueError(f"Cannot shrink the actor input from {weight.shape[1]} to {input_dim}")
    padded = weight.new_zeros(weight.shape[0], input_dim)
    padded[:, : weight.shape[1]] = weight
    return {**actor_state, "0.weight": padded}
~~~

</details>


<details markdown="1"><summary>__init__</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/history.py:73>)
~~~python
def __init__(self, num_envs: int, frames: int, width: int, device: str | torch.device) -> None:
        self.frames = torch.zeros(num_envs, frames, width, device=device)
        self.fresh = torch.ones(num_envs, dtype=torch.bool, device=device)
~~~

</details>


<details markdown="1"><summary>forward</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/history.py:60>)
~~~python
def forward(self, obs: torch.Tensor, obs_history: torch.Tensor | None = None) -> torch.Tensor:
        if self.estimator is None:
            return self.actor(obs)
        return self.actor(torch.cat((obs, self.estimator.features(obs_history)), -1))
~~~

</details>


<details markdown="1"><summary>features</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/history.py:38>)
~~~python
def features(self, history: torch.Tensor) -> torch.Tensor:
        raw = self(history)
        return torch.cat((raw[..., :3], torch.sigmoid(raw[..., 3:])), -1)
~~~

</details>


<details markdown="1"><summary>reset</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/history.py:77>)
~~~python
def reset(self, ids: torch.Tensor) -> None:
        self.fresh[ids] = True
~~~

</details>


<details markdown="1"><summary>update</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/history.py:80>)
~~~python
def update(self, frame: torch.Tensor, new_step: bool) -> None:
        """Append on a new policy step; a repeated read within one step only refreshes the newest frame."""
        if new_step:
            self.frames.copy_(torch.roll(self.frames, -1, dims=1))
        self.frames[:, -1] = frame
        fresh = self.fresh.nonzero().flatten()
        self.frames[fresh] = frame[fresh, None].expand(-1, self.frames.shape[1], -1)
        self.fresh.zero_()
~~~

</details>


<details markdown="1"><summary>flat</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/wheelleg/history.py:89>)
~~~python
def flat(self) -> torch.Tensor:
        return self.frames.flatten(1)
~~~

</details>


## 我们env追加奖励/mask


<details markdown="1"><summary>_measure</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/isaac/wheelleg_tasks/env.py:582>)
~~~python
def _measure(self) -> dict:
        t = self.training
        data = self.robot.data
        q = data.root_quat_w
        roll, pitch, yaw = euler_xyz_from_quat(q)
        roll, pitch = wrap_to_pi(roll), wrap_to_pi(pitch)
        wheels_w = data.body_pos_w[:, self.wheels]
        relative = wheels_w - data.root_pos_w[:, None]
        wheel_b = quat_apply_inverse(q[:, None].expand(-1, 2, -1).reshape(-1, 4), relative.reshape(-1, 3)).reshape(
            -1, 2, 3
        )
        wheel_vel = quat_apply_inverse(
            q[:, None].expand(-1, 2, -1).reshape(-1, 4), data.body_lin_vel_w[:, self.wheels].reshape(-1, 3)
        ).reshape(-1, 2, 3)
        ground = self.terrain.env_origins[:, 2]
        if self.stair_course is not None:
            ground, up, down, rise = scan_course(
                self.scanner.data.ray_hits_w,
                data.root_pos_w,
                yaw,
                wheels_w,
                self.stair_course.forward_sign,
                self.last_ground,
                t.stage["course"],
            )
            self.stair_up_distance.copy_(up)
            self.stair_down_distance.copy_(down)
            self.stair_up_rise.copy_(rise)
            self.last_ground.copy_(ground)
        elif self.scanner is not None:
            ground = ground_from_hits(self.scanner.data.ray_hits_w[:, :, 2], self.last_ground)
            # In-place: buffers reassigned under the rollout's inference_mode cannot be reset outside it.
            self.last_ground.copy_(ground)
        base_height = data.root_pos_w[:, 2] - ground
        clearance = wheels_w[:, :, 2] - ground[:, None] - t.shared["wheel_radius_m"]
        force = self.contact_peaks[:, self.contact_wheels]
        contact = force > t.shared["airborne"]["contact_force_n"]
        height_target = self.commands.height[:, 0]
        # Height-reference rate for the vertical velocity term. The stairs boost is a step change with no rate.
        height_rate = self.commands.height_rate
        if self.stair_course is not None:
            height_target = torch.where(self.height_boost_remaining > 0, self.height_boost_target, height_target)
            height_rate = torch.where(self.height_boost_remaining > 0, 0.0, height_rate)
        elif t.task == "p1-recovery":
            height_target = height_target + t.stage["step_height_boost_m"] * (self.height_boost_remaining > 0)
            height_upper = t.settings["commands"]["height_range_m"][1]
            height_target = height_target.clamp(max=height_upper)
        age = self.episode_length_buf * self.step_dt
        if t.task == "p1-recovery":
            rise = smooth_height(self.recovery_start_height, height_target, age, t.stage["rise_duration_s"])
            rise_rate = smooth_height_rate(
                self.recovery_start_height, height_target, height_rate, age, t.stage["rise_duration_s"]
            )
            height_target = torch.where(self.recovery_episode, rise, height_target)
            height_rate = torch.where(self.recovery_episode, rise_rate, height_rate)
        # 改自 SCUT wheelbipe25_v3/env.py:3573-3582: 死区内的指令按 0 跟踪，避免同时要求“跟小速度”和“别动”。
        deadzone = t.settings["reward_parameters"]["stand_deadzone"]
        tracked = torch.where(self.commands.value.abs() < deadzone, 0.0, self.commands.value)
        if self.stair_course is not None:
            tracked[:, 2] = torch.where(
                self.commands.value[:, 2].abs() < t.stage["course"]["yaw_deadzone_rad_s"],
                0.0,
                self.commands.value[:, 2],
            )
        # World velocity in the yaw-only heading frame. The body-frame vx * cos(pitch) used before (SCUT V14) leaks
        # vertical velocity into forward speed whenever the body pitches, which bobbing in phase with pitch exploits.
        heading_velocity = rotate_xy(data.root_lin_vel_w[:, :2], -yaw)
        linear_error = heading_velocity[:, 0] - tracked[:, 0]
        angular_error = data.root_ang_vel_b[:, 2] - tracked[:, 2]
        height_error = base_height - height_target
        leg_vector = wheel_b - wheel_b.new_tensor(t.shared["hip_pivot_positions_b_m"])
        second_difference = self.raw_action - 2 * self.previous_action + self.previous_previous_action
        return dict(
            tracked_command=tracked[:, [0, 2]],
            leg_action_second_difference=second_difference[:, self.legs],
            wheel_action_second_difference=second_difference[:, self.wheel_channels],
            velocity=data.root_lin_vel_b,
            velocity_w=data.root_lin_vel_w,
            heading_velocity=heading_velocity,
            height_target_rate=height_rate,
            angular_velocity=data.root_ang_vel_b,
            gravity=data.projected_gravity_b,
            roll=roll,
            pitch=pitch,
            yaw=yaw,
            base_height=base_height,
            ground=ground,
            wheel_position_w=wheels_w,
            wheel_position_b=wheel_b,
            # Wheel x in the yaw-only heading frame: zero means directly below the base along gravity.
            wheel_heading_x=relative[:, :, 0] * yaw.cos()[:, None] + relative[:, :, 1] * yaw.sin()[:, None],
            wheel_velocity_b=wheel_vel,
            clearance=clearance,
            wheel_contact=contact,
            wheel_force=force,
            linear_error=linear_error,
            angular_error=angular_error,
            height_error=height_error,
            undesired_force=self.contact_peaks[:, self.contact_bad],
            guide_support_force=(
                self.contact.data.net_forces_w[:, self.stair_guides, 2].clamp_min(0).sum(-1)
                if self.stair_course is not None
                else torch.zeros(self.num_envs, device=self.device)
            ),
            leg_length=leg_vector[:, :, [0, 2]].norm(dim=-1),
            leg_angle=torch.atan2(leg_vector[:, :, 0], -leg_vector[:, :, 2]),
            torque=self.torque,
            wheel_torque=self.torque[:, self.wheel_channels],
            wheel_velocity=data.joint_vel[:, self.joints][:, self.wheel_channels],
            hip_torque=self.torque[:, self.legs],
            hip_velocity=data.joint_vel[:, self.joints][:, self.legs],
            action=self.raw_action,
            previous_action=self.previous_action,
        )
~~~

</details>


<details markdown="1"><summary>_get_dones</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/isaac/wheelleg_tasks/env.py:697>)
~~~python
def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        self.numerical_bad = numerical_failure(
            self.robot.data.joint_vel,
            self.robot.data.root_lin_vel_b,
            self.robot.data.root_ang_vel_b,
            self.training.shared["numerical_safety"],
        ) | nonfinite_pose(self.robot.data.root_pos_w, self.robot.data.root_quat_w, self.robot.data.joint_pos)
        self.iteration_numerical_terminations += self.numerical_bad.sum()
        self._record_contacts(self._sim_step_counter)
        s = self._measure()
        t, dt = self.training, self.step_dt
        if self.stair_course is not None:
            # Upward guide force is support, not proof of contact with the upper platform.
            # Release height guidance for retraction, but retain the ordinary contact termination timer.
            self.stair_course.guide_support.copy_(
                (s["guide_support_force"] > t.stage["course"]["contact_force_n"]) & self.stair_course.steps
            )
        if self.family == "p1":
            # Preserve the phase before transitions: the last cushioning interval must remain unpenalized.
            if self.stair_course is not None:
                s["hip_acceleration_relaxed"] = (
                    self.stair_course.flying | self.stair_course.guide_support | (self.stair_course.cushion > 0)
                )
            elif self.landing_reward is not None:
                s["hip_acceleration_relaxed"] = self.landing_reward.flight() | self.landing_reward.cushion()
            else:
                s["hip_acceleration_relaxed"] = self.airborne.clone()
        if airborne_enabled(t.task):
            air = t.shared["airborne"]
            candidate = ~s["wheel_contact"].any(-1) & (s["clearance"].amin(-1) > air["wheel_clearance_m"])
            candidate &= s["base_height"] > air["base_height_m"]
            if self.stair_course is not None:
                candidate &= s["guide_support_force"] <= self.stair_course.p["contact_force_n"]
            self.air_enter = torch.where(candidate, self.air_enter + dt, 0)
            self.air_exit = torch.where(s["wheel_contact"].any(-1), self.air_exit + dt, 0)
            self.airborne |= self.air_enter >= air["enter_duration_s"]
            self.air_elapsed = torch.where(self.airborne, self.air_elapsed + dt, 0)
            self.airborne &= (self.air_exit < air["exit_duration_s"]) & (self.air_elapsed < air["max_duration_s"])
            if self.stair_course is not None:
                self.airborne &= s["guide_support_force"] <= self.stair_course.p["contact_force_n"]
            if self.landing_reward is not None:
                # Later real flights remain exempt, but the airborne exit dwell cannot prolong ground cushioning.
                s["hip_acceleration_relaxed"] |= self.airborne & candidate
            tilt_limit = torch.where(
                self.airborne, t.shared["termination"]["airborne_tilt_rad"], t.shared["termination"]["tilt_rad"]
            )
        else:
            self.airborne.zero_()
            tilt_limit = t.shared["termination"]["tilt_rad"]
        tilt_fail = (s["roll"].abs() > tilt_limit) | (s["pitch"].abs() > tilt_limit)
        body_hit = (self.contact_peaks[:, self.contact_terminal] > t.shared["termination"]["contact_force_n"]).any(-1)
        # 改自 SCUT wheelbipe25_v3/env.py:4863-4895, 5017-5022: 倾倒/触地累计满 duration_s 才终止，
        # 否则随机出生的瞬时触地会让回合立刻结束；数值异常仍立即终止。
        # 与 SCUT 不同：条件中断时计数慢慢回落而不是清零。清零时策略靠“碰一下抬一下”
        # 在约 40% 的时间里撑地也从不终止（standup2 的曲线）。
        physical = (tilt_fail | body_hit) & ~self.recovery_episode
        # 随机腿姿出生后先落地，起立窗口内不按倾倒/触地终止；触地惩罚照常累计。所有任务共用。
        if self.landing_reward is not None:
            # PPO randomizes the episode clock; landing grace uses real physics age instead.
            birth_age = (self._sim_step_counter - self.landing_reward.born) * self.physics_dt
            physical &= birth_age >= t.shared["leg_reset"]["settle_s"]
        else:
            birth_age = self.stair_course.age if self.stair_course is not None else self.episode_length_buf * dt
            physical &= birth_age >= t.shared["leg_reset"]["settle_s"]
        self.termination_steps = torch.where(
            physical, self.termination_steps + 1, (self.termination_steps - self.termination_leak).clamp_min(0)
        )
        terminated = (self.termination_steps >= self.termination_duration_steps) | self.bad_action | self.numerical_bad
        timeout = self.episode_length_buf >= self.max_episode_length - 1
        if t.task == "p1-recovery":
            timeout |= self.recovery_episode & (self.episode_length_buf * dt >= t.stage["recovery_timeout_s"])
        if self.bounded_terrain:
            # Timeout, not termination: no penalty, and PPO bootstraps the value at the edge.
            terrain = t.stage["terrain"]
            self.out_of_bounds.copy_(
                outside_terrain(
                    self.robot.data.root_pos_w[:, :2], terrain_half_extent(terrain), terrain["boundary_margin_m"]
                )
            )
            timeout |= self.out_of_bounds
        if self.stair_course is not None:
            self.stair_course.update(s, self.terrain.env_origins, dt, terminated, t.settings["reward_parameters"])
            # Outer map exits must not retain a success latched on the last in-bounds observation.
            self.stair_course.success &= ~self.out_of_bounds
            # PPO may randomize episode_length_buf; a course must still receive its full traversal time.
            timeout = (
                (self.stair_course.age >= self.max_episode_length_s)
                | self.out_of_bounds
                | self.stair_course.finished
                | self.stair_course.motion_boundary
            )
            if not self.cfg.evaluation:
                timeout |= self.stair_course.traversed & ~self.stair_course.free_commands
            # A map boundary is not a control failure. Physical failures take precedence over bootstrapping.
            timeout |= self.stair_course.escaped
            timeout &= ~terminated
        if self.jump is not None:
            stable = (s["roll"].abs() < t.stage["landing_tilt_rad"]) & (s["pitch"].abs() < t.stage["landing_tilt_rad"])
            stable &= (s["linear_error"].abs() < t.stage["landing_speed_error_m_s"]) & ~terminated
            stable &= self.jump.apex_z - self.jump.start_z >= self.jump.height - t.stage["height_tolerance_m"]
            valid = torch.ones_like(stable)
            if t.task == "p3-tunnel":
                p = t.stage["tunnel"]
                end = self.terrain.env_origins[:, 0] + self.beam_start_x + p["beam_length_m"]
                valid = tunnel_landing(
                    s["wheel_position_w"],
                    t.shared["wheel_radius_m"],
                    self.robot.data.body_pos_w,
                    end,
                    self.terrain.env_origins[:, 2],
                    p["landing_margin_m"],
                    p["clearance_margin_m"],
                )
            self.jump.update(
                dt,
                self.episode_length_buf * dt,
                self.robot.data.root_pos_w[:, 2],
                s["velocity_w"][:, 2],
                s["wheel_contact"],
                stable,
                valid,
                self.obstacle_hit,
            )
            if not self.cfg.evaluation:
                finished = self.jump.finished.nonzero().flatten()
                iteration = self.training_iteration_offset + self.common_step_counter / t.settings["rollout_steps"]
                self.jump_curriculum.record(self.jump_bins[finished], self.jump.landing_pulse[finished], iteration)
        if self.first_landing is not None:
            self.first_landing.update(
                self._sim_step_counter,
                self.physics_dt,
                dt,
                s,
                terminated,
                timeout,
                self.numerical_bad | self.bad_action,
            )
        if self.landing_reward is not None:
            self.landing_reward.update(
                self._sim_step_counter,
                self.physics_dt,
                dt,
                s,
                terminated,
                timeout,
                self.numerical_bad | self.bad_action,
            )
            resolved = self.landing_reward.resolved
            offsets, succeeded = self.air_height_offset[resolved], self.landing_reward.succeeded[resolved]
            # The command gate counts the newest height band only, so speed cannot outrun the hardest landings.
            # The band is read before the height curriculum may promote on this same batch; after a promotion the
            # gate's open window held the old band only, so it is discarded and refilled from the new band.
            newest = offsets >= self.air_height_curriculum.band_floor
            self.command_curriculum.record_landing(succeeded[newest])
            if self.air_height_curriculum.record(offsets, succeeded):
                self.command_curriculum.discard_landing()
        s["terminated"] = terminated
        self.state = s
        return terminated, timeout
~~~

</details>


<details markdown="1"><summary>_get_rewards</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/isaac/wheelleg_tasks/env.py:857>)
~~~python
def _get_rewards(self) -> torch.Tensor:
        t, s = self.training, self.state
        n = self.num_envs
        one = torch.ones(n, device=self.device)
        relaxed = torch.zeros_like(self.airborne)
        if self.landing_reward is not None:
            flight = self.landing_reward.flight()
            relaxed = flight | self.landing_reward.cushion()
        if self.stair_course is not None:
            relaxed = self.stair_course.flying | self.stair_course.guide_support | (self.stair_course.cushion > 0)
        # The command curriculum grades driving under commands; flight and cushion steps, where the tracking
        # rewards are off, are left out of its averages.
        counted = ~relaxed[:, None]
        errors = torch.stack((s["linear_error"].abs(), s["angular_error"].abs(), s["height_error"].abs()), -1)
        self.command_error_sum += torch.where(counted, errors, 0.0)
        self.command_abs_sum += torch.where(counted, s["tracked_command"].abs(), 0.0)
        self.command_sample_count += (~relaxed).long()
        # Policy-step differencing (100 Hz). Always update history, including masked flight/cushion steps,
        # so resuming the penalty never accumulates a velocity change across the entire disabled interval.
        s["hip_acceleration"] = (s["hip_velocity"] - self.previous_hip_velocity) / self.step_dt
        self.previous_hip_velocity.copy_(s["hip_velocity"])
        s.update(
            tracking_mask=one,
            height_mask=one,
            height_gate=one,
            # 改自 SCUT V14/env_cfg.py:1549-1562 (airborne reward_scales)：腾空时关闭俯仰惩罚和高度平方惩罚，
            # 空中机身高度和俯仰不由策略决定，继续罚只会干扰落地动作。
            ground_mask=(~self.airborne).float(),
            requested_speed=self.commands.value[:, :2].norm(dim=-1),
            airborne=self.airborne,
            contact_multiplier=torch.where(self.airborne, 25.0, 1.0),
            termination_multiplier=torch.where(self.airborne, 6.0, 1.0),
        )
        if self.family in ("p1", "p2"):
            # 改自 SCUT wheelbipe25_v3/env.py:3842-3866 (linear_band)：高度没到位时压低速度/转速跟踪奖励，
            # 防止趴低追速度。与 SCUT env.py:3887-3893 一致，跟踪奖励和误差惩罚都乘门控。
            # P1 的全部阶段和 P2 共用；腾空时高度误差没有意义，门控置 1。
            p = t.settings["reward_parameters"]
            band = p["height_gate_zero_error_m"] - p["height_gate_full_error_m"]
            gate = ((p["height_gate_zero_error_m"] - s["height_error"].abs()) / band).clamp(0, 1)
            # Landing uses its own flight/cushion phases, not the airborne classifier's exit dwell.
            free = relaxed if self.landing_reward is not None or self.stair_course is not None else self.airborne
            s["height_gate"] = torch.where(free, 1.0, gate)
        if self.family == "p2":
            actual = rotate_xy(s["velocity_w"][:, :2], -self.commands.reference_yaw)
            target = self.commands.translation
            s["translation_error"] = actual - target
            s["requested_speed"] = target.norm(dim=-1)
            s["speed_error"] = actual.norm(dim=-1) - s["requested_speed"]
            s["heading_error"] = wrap_to_pi(
                torch.atan2(actual[:, 1], actual[:, 0]) - torch.atan2(target[:, 1], target[:, 0])
            )
            s["linear_error"] = s["translation_error"].norm(dim=-1)
        if self.jump is not None:
            s["jump"] = self.jump
            s["jump_ref"] = self.jump.references(
                s["velocity_w"][:, 2], s["clearance"].amin(-1), t.shared["gravity_m_s2"]
            )
            s["height_mask"] = (~self.jump.active).float()
            s["tracking_mask"] = torch.where(self.jump.active, 1.0, t.stage["non_event_tracking_scale"])
            s["guidance_scale"] = self.guidance_scale
        if t.task == "p1-landing":
            # Stable penalty scales cannot depend on an airborne-classifier dwell timer: the heavier contact cost is
            # gated by the landing window (birth to first contact + window_s), where the cushioning collisions occur.
            s["contact_multiplier"] = (
                torch.where(self.landing_reward.hold, t.stage["landing_reward"]["contact_multiplier"], 1.0)
                if self.landing_reward is not None
                else one
            )
            s["termination_multiplier"] = one
        if self.landing_reward is not None:
            # Flight and the one-shot cushion after first touch relax tracking/height targets; attitude rewards stay on.
            # Pitch penalty is off only in flight (SCUT V14/env_cfg.py:1551), not while cushioning on the wheels.
            # Still on the airborne classifier: air_joint_limits and the airborne tilt termination limit.
            s["tracking_mask"] = (~relaxed).float()
            s["height_mask"] = (~relaxed).float()
            s["ground_mask"] = (~flight).float()
        if self.stair_course is not None:
            s["tracking_mask"] = (~relaxed).float()
            s["height_mask"] = (~relaxed).float()
            s["ground_mask"] = (~self.stair_course.flying).float()
            # Guide-only support costs less; any simultaneous body/link contact keeps the full binary cost.
            other_hit = (
                self.contact_peaks[:, self.stair_non_guide_contacts]
                > t.settings["reward_parameters"]["contact_force_n"]
            ).any(-1)
            s["contact_multiplier"] = torch.where(
                self.stair_course.steps & ~other_hit, t.stage["course"]["guide_contact_scale"], 1.0
            )
            s["termination_multiplier"] = one
        weights = self.reward_weights
        if t.task == "p1-flat":
            # 宽核高度奖励在起立阶段提供梯度；站稳后它接近常数，按训练轮数线性退到 final_weight，
            # 保留一个下限是因为每回合仍从随机腿姿起立。
            anneal = t.settings["height_wide_anneal"]
            iteration = self.training_iteration_offset + self.common_step_counter / t.settings["rollout_steps"]
            progress = min(max((iteration - anneal["start_iteration"]) / anneal["ramp_iterations"], 0.0), 1.0)
            initial = weights["track_height_wide"]
            weights = {**weights, "track_height_wide": initial + progress * (anneal["final_weight"] - initial)}
        terms = compute_rewards(s, t.settings["reward_parameters"], weights, self.step_dt, t.settings["reward_clip"])
        if self.stair_course is not None:
            motion_terms = compute_rewards(
                s,
                t.settings["reward_parameters"],
                t.stage["motion_reward_overrides"],
                self.step_dt,
                t.settings["reward_clip"],
            )
            for name, value in motion_terms.items():
                terms[name] = torch.where(self.stair_course.motion, value, terms[name])
            power_weight = torch.full_like(s["height_error"], weights["wheel_power"])
            for kind, overrides in t.stage["terrain_reward_overrides"].items():
                selected = torch.zeros_like(self.stair_course.motion)
                for group, name in enumerate(self.stair_course.names):
                    if t.stage["terrain"]["profiles"][name]["kind"] == kind:
                        selected |= self.stair_course.group == group
                terrain_terms = compute_rewards(
                    s, t.settings["reward_parameters"], overrides, self.step_dt, t.settings["reward_clip"]
                )
                for name, value in terrain_terms.items():
                    terms[name] = torch.where(selected, value, terms[name])
                power_weight = torch.where(selected, overrides["wheel_power"], power_weight)
            # SCUT wheelbipe25_v3/env.py:3542-3544 charges positive motor work, not braking work.
            positive_work = (s["wheel_torque"] * s["wheel_velocity"]).clamp_min(0).sum(-1)
            terms["wheel_power"] = torch.where(
                self.stair_course.motion, terms["wheel_power"], power_weight * self.step_dt * positive_work
            )
        if self.family == "p1" and "leg_joint_acc" in terms:
            disabled = s["hip_acceleration_relaxed"] | relaxed
            if self.landing_reward is None and self.stair_course is None:
                disabled |= self.airborne
            terms["leg_joint_acc"] = torch.where(disabled, 0.0, terms["leg_joint_acc"])
        if t.task in ("p1-landing", "p1-recovery", "p3-jump", "p3-tunnel"):
            ar = t.settings["air_rewards"]
            terms["air_wheel_torque"] = (
                ar["wheel_torque"]
                * self.step_dt
                * torch.exp(-s["wheel_torque"].square().sum(-1) / ar["wheel_torque_sigma"])
                * self.airborne
            )
            excess = (self.lower[self.legs] - self.robot.data.joint_pos[:, self.joints][:, self.legs]).clamp_min(0)
            excess += (self.robot.data.joint_pos[:, self.joints][:, self.legs] - self.upper[self.legs]).clamp_min(0)
            terms["air_joint_limits"] = ar["joint_limit"] * self.step_dt * excess.sum(-1) * self.airborne
            terms["air_wheel_center"] = (
                ar["wheel_center"]
                * self.step_dt
                * torch.exp(-s["wheel_position_b"][:, :, 0].square().sum(-1) / ar["wheel_center_sigma"])
                * self.airborne
            )
            wheel_speed_error = s["wheel_velocity"] * t.shared["wheel_radius_m"] - s["velocity"][:, 0:1]
            terms["air_wheel_alignment"] = (
                ar["wheel_speed_alignment"] * self.step_dt * wheel_speed_error.square().sum(-1) * self.airborne
            )
        if t.task == "p1-landing":
            # Remove the old +20/s and +10/s airborne bounties and unconstrained wheel-speed loss.
            for key in ("air_wheel_torque", "air_wheel_center", "air_wheel_alignment"):
                terms[key] = torch.zeros_like(one)
            if self.landing_reward is not None:
                terms["stand_still"] = torch.where(relaxed, 0.0, terms["stand_still"])
                terms.update(self.landing_reward.terms(s, t.shared["wheel_radius_m"], self.step_dt))
        if self.stair_course is not None:
            p = t.stage["course"]
            terms["stair_impact"] = p["impact_weight"] * self.stair_course.impact
            # No survival bounty in flight: bounded wheel-speed matching, disabled as soon as wheels touch.
            error = s["wheel_velocity"] * t.shared["wheel_radius_m"] - s["heading_velocity"][:, 0:1]
            terms["stair_air_wheel_speed"] = torch.where(
                self.stair_course.flying,
                -p["air_wheel_speed_weight"]
                * self.step_dt
                * (1 - torch.exp(-error.square().mean(-1) / p["air_wheel_speed_sigma"])),
                0.0,
            )
            excess = (self.lower[self.legs] - self.robot.data.joint_pos[:, self.joints][:, self.legs]).clamp_min(0)
            excess += (self.robot.data.joint_pos[:, self.joints][:, self.legs] - self.upper[self.legs]).clamp_min(0)
            terms["air_joint_limits"] = (
                t.settings["air_rewards"]["joint_limit"] * self.step_dt * excess.sum(-1) * self.stair_course.flying
            )
            terms["stand_still"] = torch.where(relaxed, 0.0, terms["stand_still"])
            # Command tracking replaces world-x progress and stuck costs for arbitrary headings.
            diagnostic_sample = torch.stack(
                (
                    self.commands.value[:, 0].abs(),
                    self.commands.value[:, 2].abs(),
                    self.commands.height[:, 0],
                    (self.commands.value[:, 2].abs() > p["yaw_deadzone_rad_s"]).float(),
                    (self.height_boost_remaining > 0).float(),
                    s["roll"].square(),
                    s["pitch"].square(),
                    (s["guide_support_force"] > p["contact_force_n"]).float(),
                    s["heading_velocity"][:, 0].abs(),
                    s["linear_error"].abs(),
                    s["angular_error"].abs(),
                    (self.commands.value[:, 0].abs() >= t.settings["reward_parameters"]["stand_deadzone"]).float(),
                    (
                        (self.commands.value[:, 0].abs() >= t.settings["reward_parameters"]["stand_deadzone"])
                        & (s["heading_velocity"][:, 0].abs() < t.settings["reward_parameters"]["stand_deadzone"])
                        & ~relaxed
                    ).float(),
                ),
                -1,
            )
            self.stair_course.diagnostics += (
                torch.where(self.numerical_bad[:, None], 0.0, torch.nan_to_num(diagnostic_sample)) * self.step_dt
            )
        if t.task == "p1-recovery":
            position = self.robot.data.root_pos_w
            delta_b = quat_apply_inverse(self.robot.data.root_quat_w, position - self.previous_position)
            terms["progress"] = t.stage["progress_weight"] * delta_b[:, 0] * self.commands.value[:, 0].sign()
            self.stuck_time += self.step_dt
            ready = self.stuck_time >= t.stage["stuck_window_s"]
            moved = (position - self.stuck_start)[:, :2].norm(dim=-1)
            self.stuck = torch.where(
                ready, (moved < t.stage["stuck_distance_m"]) & (self.commands.value[:, 0].abs() > 0.1), self.stuck
            )
            self.stuck_start[ready] = position[ready]
            self.stuck_time[ready] = 0
            terms["stuck"] = t.stage["stuck_weight"] * self.step_dt * self.stuck
            terms["stair_impact"] = t.stage["impact_weight"] * self.step_dt * s["hip_torque"].square().amax(-1)
        if t.task == "p3-tunnel":
            p = t.stage["tunnel"]
            terms["tunnel_crossing"] = p["crossing_weight"] * self.jump.landing_pulse
            terms["obstacle_contact"] = p["obstacle_contact_weight"] * self.step_dt * self.obstacle_hit
            terms["obstacle_top_contact"] = p["top_contact_weight"] * self.step_dt * self.obstacle_top_hit
        self.previous_position.copy_(self.robot.data.root_pos_w)
        for name, value in terms.items():
            event = name in EVENT_TERMS and (name != "stair_impact" or self.stair_course is not None)
            terms[name] = value if event else value.clamp(-t.settings["reward_clip"], t.settings["reward_clip"])
            # SCUT wheelbipe25_v3/env.py:4007-4018: mask with where, never NaN * 0.
            if t.task == "p1-landing" and name == "termination":
                # Numerical escape must still pay the existing, finite termination cost.
                terms[name] = torch.where(self.numerical_bad, float(t.settings["rewards"]["termination"]), terms[name])
            elif t.task == "p1-landing" and name == "landing_outcome":
                pass  # The event module already emits a finite cost, once, only for active events.
            else:
                terms[name] = torch.where(self.numerical_bad, 0.0, terms[name])
            if name not in self.reward_sums:
                self.reward_sums[name] = torch.zeros(n, device=self.device)
            self.reward_sums[name] += terms[name]
        # Preserve pre-reset measurements for evaluation; reset environments cannot contaminate metrics.
        self.extras["evaluation"] = {
            "errors": torch.stack((s["linear_error"], s["angular_error"], s["height_error"]), -1).detach().clone(),
            "failed": s["terminated"].detach().clone(),
            "position": self.robot.data.root_pos_w.detach().clone(),
            "jump_success": self.jump.landing_pulse.clone()
            if self.jump is not None
            else torch.zeros_like(self.airborne),
        }
        if self.stair_course is not None:
            self.extras["evaluation"]["stair_success"] = self.stair_course.success.detach().clone()
            self.extras["evaluation"]["stair_escaped"] = self.stair_course.escaped.detach().clone()
            self.extras["evaluation"]["stair_neutral_exit"] = (
                ((self.stair_course.escaped | self.out_of_bounds) & ~s["terminated"]).detach().clone()
            )
            self.extras["evaluation"]["stair_traversed"] = self.stair_course.traversed.detach().clone()
            self.extras["evaluation"]["stair_stopped"] = self.stair_course.finished.detach().clone()
            if self.cfg.evaluation:
                root = self.robot.data.root_state_w.clone()
                root[:, :3] -= self.terrain.env_origins
                self.extras["evaluation"].update(
                    root_state=root,
                    joint_position=self.robot.data.joint_pos.clone(),
                    joint_velocity=self.robot.data.joint_vel.clone(),
                    stair_tracking=(self.stair_course.track_sum / self.stair_course.track_count.clamp_min(1)).clone(),
                )
        if self.cfg.evaluation and t.task == "p1-flat":
            # DirectRLEnv.step resets before returning: capture diagnostics before that reset.
            self.extras["evaluation"].update(
                attitude=torch.stack((s["roll"], s["pitch"], s["yaw"]), -1).detach().clone(),
                velocity=s["velocity"].detach().clone(),
                angular_velocity=s["angular_velocity"].detach().clone(),
                height=s["base_height"].detach().clone(),
                contact_force=s["undesired_force"].amax(-1).detach().clone(),
                wheel_force=s["wheel_force"].detach().clone(),
                torque=self.torque.detach().clone(),
                joint_velocity=self.robot.data.joint_vel[:, self.joints].detach().clone(),
                numerical_failure=(self.numerical_bad | self.bad_action).detach().clone(),
            )
        return torch.stack(list(terms.values())).sum(0)
~~~

</details>


<details markdown="1"><summary>_reset_tunnel</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/isaac/wheelleg_tasks/env.py:1632>)
~~~python
def _reset_tunnel(self, ids: torch.Tensor) -> None:
        p = self.training.stage["tunnel"]
        count = len(ids)
        if self.cfg.evaluation:
            self.beam_start_x[ids] = p["approach_distance_m"]
            self.beam_top_z[ids] = p["beam_height_m"]
            self.tunnel_bins[ids] = 0
        else:
            self.beam_start_x[ids] = p["approach_distance_m"] + uniform(p["approach_jitter_m"], (count,), self.device)
            levels = self.raw_action.new_tensor(p["height_curriculum_m"])
            rows = torch.randint(min(self.jump_curriculum.maximum_level + 1, len(levels)), (count,), device=self.device)
            self.tunnel_bins[ids] = rows
            self.beam_top_z[ids] = levels[rows] + uniform(p["height_jitter_m"], (count,), self.device)
        pose = self.beam.data.default_root_state[ids, :7].clone()
        pose[:, :3] = self.terrain.env_origins[ids]
        pose[:, 0] += self.beam_start_x[ids] + p["beam_length_m"] / 2
        pose[:, 2] += self.beam_top_z[ids] - p["beam_thickness_m"] / 2
        # Decide once at episode reset, not after the last requested jump is consumed.
        no_jump = self.jump.remaining[ids] == 0
        pose[no_jump] = pose.new_tensor(p["no_jump_beam_pose"])
        pose[no_jump, :3] += self.terrain.env_origins[ids[no_jump]]
        self.beam.write_root_pose_to_sim(pose, ids)
~~~

</details>


## SCUT wheelbipe25_v3/env.py


<details markdown="1"><summary>_get_rewards</summary>

[源码](<D:/WHEEL_LEG_RL/wheeled-legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py:3474>)
~~~python
def _get_rewards(self) -> torch.Tensor:
        self._update_ground_height_estimate()
        # prepare
        root_quat_inv, wheel_pos_b, wheel_pos_heading_b, wheel_lin_vel_b, wheel_lin_vel_heading_b = (
            self._get_root_quat_inv_and_wheel_pos_b()
        )
        left_leg_length = torch.norm(wheel_pos_heading_b[:,0],dim=-1)
        right_leg_length = torch.norm(wheel_pos_heading_b[:,1],dim=-1)
        left_leg_angle = torch.atan2(-wheel_pos_heading_b[:,0,0],-wheel_pos_heading_b[:,0,2])
        right_leg_angle = torch.atan2(-wheel_pos_heading_b[:,1,0],-wheel_pos_heading_b[:,1,2])
        left_wheel_pos_b_normal = wheel_pos_heading_b[:,0]/left_leg_length.unsqueeze(-1)
        right_wheel_pos_b_normal = wheel_pos_heading_b[:,1]/right_leg_length.unsqueeze(-1)
        left_leg_length_dot = torch.sum(wheel_lin_vel_heading_b[:,0]*left_wheel_pos_b_normal,dim=-1)
        right_leg_length_dot = torch.sum(wheel_lin_vel_heading_b[:,1]*right_wheel_pos_b_normal,dim=-1)
        # leg_ang_vel = self.joint_vel[:,self._front1_joint_idx] - self.joint_vel[:,self._rear1_joint_idx]

        wheel_power = self.robot.data.applied_torque[:,self._wheel_idx]*self.joint_vel[:,self._wheel_idx]
        comsume_wheel_power = torch.clamp(wheel_power,min=0)

        # both_height_cmd = self.height_cmd.unsqueeze(-1).repeat((1,2))
        # deviation_joints = self._inverse_kinematics(both_height_cmd,torch.zeros_like(both_height_cmd,dtype=torch.float,device=self.device)).transpose(-2,-1).reshape(self.num_envs,-1)[:,:len(self._deviation_joint_idx)]

        # 起身训练：整个落地+起身阶段速度命令和角速度命令强制为0（reward 计算用）
        # if getattr(self.cfg, 'enable_standup_training', False):
        #     in_standup_phase = (self._standup_phase == 0) | (self._standup_phase == 1)
        #     self.command[in_standup_phase, :3] = 0.0

        # alive
        rew_termination = self.reset_terminated
        rew_epi_len = self.episode_length_buf

        # regularization
        joint_acc = self.robot.data.joint_acc
        rew_joint_acc = torch.sum(torch.square(joint_acc[:,self._actuate_idx]), dim=1)
        rew_leg_joint_acc = torch.sum(torch.square(joint_acc[:,self._legs_act_idx]), dim=1)
        rew_leg_joint_com_acc = torch.sum(torch.square(0.5*(joint_acc[:,self._legs_front_idx]+joint_acc[:,self._legs_rear_idx])), dim=1)
        rew_leg_joint_diff_acc = torch.sum(torch.square(0.5*(joint_acc[:,self._legs_front_idx]-joint_acc[:,self._legs_rear_idx])), dim=1)
        rew_wheel_acc = torch.sum(torch.square(joint_acc[:,self._wheel_idx]), dim=1)
        rew_wheel_com_acc = torch.square(0.5*(joint_acc[:,self._wheel_idx[0]]+joint_acc[:,self._wheel_idx[1]]))
        rew_wheel_diff_acc = torch.square(0.5*(joint_acc[:,self._wheel_idx[0]]-joint_acc[:,self._wheel_idx[1]]))
        rew_joint_vel = torch.sum(torch.square(self.joint_vel[:,self._actuate_idx]), dim=1)
        rew_leg_joint_vel = torch.sum(torch.square(self.joint_vel[:,self._legs_act_idx]), dim=1)
        rew_leg_joint_com_vel = torch.sum(torch.square(0.5*(self.joint_vel[:,self._legs_front_idx]+self.joint_vel[:,self._legs_rear_idx])), dim=1)
        rew_leg_joint_diff_vel = torch.sum(torch.square(0.5*(self.joint_vel[:,self._legs_front_idx]-self.joint_vel[:,self._legs_rear_idx])), dim=1)
        left_leg_pair_idx, right_leg_pair_idx = self._left_right_leg_joint_pair_idx
        if left_leg_pair_idx and right_leg_pair_idx:
            leg_pair_pos_diff = wrap_to_pi(self.joint_pos[:, left_leg_pair_idx] - self.joint_pos[:, right_leg_pair_idx])
            rew_leg_joint_pair_pos_diff = torch.sum(torch.square(leg_pair_pos_diff), dim=-1)
        else:
            rew_leg_joint_pair_pos_diff = torch.zeros(self.num_envs, dtype=torch.float, device=self.device)
        rew_wheel_vel = torch.sum(torch.square(self.joint_vel[:,self._wheel_idx]), dim=-1)
        rew_wheel_com_vel = torch.square(0.5*(self.joint_vel[:,self._wheel_idx[0]]+self.joint_vel[:,self._wheel_idx[1]]))
        rew_wheel_diff_vel = torch.square(0.5*(self.joint_vel[:,self._wheel_idx[0]]-self.joint_vel[:,self._wheel_idx[1]]))
        applied_torque = self.robot.data.applied_torque
        rew_joint_torque = torch.sum(torch.square(applied_torque[:,self._actuate_idx]), dim=1)
        torque_rate = applied_torque - self._previous_applied_torque
        torque_second_diff = (
            applied_torque
            - 2.0 * self._previous_applied_torque
            + self._before_previous_applied_torque
        )
        rew_torque_rate = torch.sum(torch.square(torque_rate[:, self._actuate_idx]), dim=-1)
        rew_torque_smoothness_leg = torch.sum(
            torch.square(torque_second_diff[:, self._legs_act_idx]), dim=-1
        )
        rew_torque_smoothness_wheel = torch.sum(
            torch.square(torque_second_diff[:, self._wheel_idx]), dim=-1
        )
        self._before_previous_applied_torque.copy_(self._previous_applied_torque)
        self._previous_applied_torque.copy_(applied_torque)
        wheel_power = applied_torque[:,self._wheel_idx]*self.joint_vel[:,self._wheel_idx]
        comsume_wheel_power = torch.clamp(wheel_power,min=0)
        rew_wheel_power = torch.sum(comsume_wheel_power, dim=-1)
        # if self.cfg.use_leg_length_as_height:
        #     rew_lin_vel_z = torch.square(left_leg_length_dot+right_leg_length_dot)
        # else:
        rew_leg_len_vel = torch.square(left_leg_length_dot) + torch.square(right_leg_length_dot)
        rew_lin_vel_z = torch.square(self.robot.data.root_lin_vel_b[:, 2])
        rew_lin_vel_z_exp = torch.exp(-rew_lin_vel_z / self.cfg.lin_vel_z_sigma)
        rew_ang_vel_xy = torch.sum(torch.square(self.robot.data.root_ang_vel_b[:, :2]), dim=1)
        rew_action_rate = torch.sum(torch.square(self._actions - self._previous_actions), dim=1)
        action_second_diff = self._actions - 2 * self._previous_actions + self._before_previous_actions
        rew_action_smoothness = torch.sum(torch.square(action_second_diff), dim=-1)
        leg_action_slice, wheel_action_slice = self._get_policy_action_slices()
        rew_action_rate_leg = torch.sum(torch.square(self._actions[:, leg_action_slice] - self._previous_actions[:, leg_action_slice]), dim=1)
        rew_action_rate_wheel = torch.sum(torch.square(self._actions[:, wheel_action_slice] - self._previous_actions[:, wheel_action_slice]), dim=1)
        rew_action_smoothness_leg = torch.sum(torch.square(action_second_diff[:, leg_action_slice]), dim=-1)
        rew_action_smoothness_wheel = torch.sum(torch.square(action_second_diff[:, wheel_action_slice]), dim=-1)
        # rew_joint_deviation_l2 = torch.sum(torch.square(self.joint_pos[:,self._deviation_joint_idx]-deviation_joints),dim=-1)
        # rew_joint_deviation_l1 = torch.sum(torch.abs(self.joint_pos[:,self._deviation_joint_idx]-deviation_joints),dim=-1)

        # print(self.robot.data.root_lin_vel_b[:, 0])
        # print(self.robot.data.applied_torque[:,self._wheel_idx])

        # tasks
        reward_command = self.command
        tracking_command = reward_command
        stand_still_lin_mask = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        stand_still_yaw_mask = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        if bool(getattr(self.cfg, "stand_still_deadzone_enabled", False)):
            stand_still_threshold = max(
                float(getattr(self.cfg, "stand_still_deadzone_threshold", 0.2)),
                0.0,
            )
            stand_still_lin_mask = torch.abs(reward_command[:, 0]) < stand_still_threshold
            stand_still_yaw_mask = torch.abs(reward_command[:, 2]) < stand_still_threshold
            tracking_command = reward_command.clone()
            tracking_command[stand_still_lin_mask, 0] = 0.0
            tracking_command[stand_still_yaw_mask, 2] = 0.0

        pgb = self.robot.data.projected_gravity_b[:, :2]
        # pgb[:,0] = pgb[:,0]-0.02
        # rew_flat_orientation = torch.sum(torch.square(self.robot.data.projected_gravity_b[:, :2]), dim=1)
        rew_flat_orientation = torch.sum(torch.square(pgb), dim=-1)
        rew_flat_orientation_y = torch.square(self.cfg.orientation_y_square_sigma*pgb[:,0])
        rew_flat_orientation_x = torch.square(self.cfg.orientation_x_square_sigma*pgb[:,1])
        rew_flat_orientation_y_exp = torch.exp(-torch.square(pgb[:,0]) / self.cfg.orientation_y_exp_sigma)
        rew_flat_orientation_x_exp = torch.exp(-torch.square(pgb[:,1]) / self.cfg.orientation_x_exp_sigma)
        lin_vel_x_cmd = torch.square(reward_command[:,0])
        rew_flat_orientation_y_v = torch.square(
            (
                self.cfg.orientation_y_A * torch.exp(-lin_vel_x_cmd / self.cfg.orientation_y_sigma)
                + self.cfg.orientation_y_bias
            )
            * pgb[:, 0]
        )
        rew_flat_orientation_x_v = torch.square((self.cfg.orientation_x_A * torch.exp(-lin_vel_x_cmd/self.cfg.orientation_x_sigma) + self.cfg.orientation_x_bias)*pgb[:,1])
        # rew_flat_orientation = torch.square(self.robot.data.projected_gravity_b[:, 1])

        # ========== 姿态门控：只有接近水平时速度/角速度 tracking 奖励才高 ==========
        # upright_err: projected_gravity_b 的水平分量平方和，越小越水平
        upright_err = rew_flat_orientation
        if bool(getattr(self.cfg, "vel_upright_gate_enabled", False)):
            sigma = float(getattr(self.cfg, "vel_upright_gate_sigma", 0.02))
            sigma = max(sigma, 1e-6)
            vel_upright_gate = torch.exp(-upright_err / sigma)
        else:
            vel_upright_gate = 1.0

        vel_orientation_x_gate_enabled = self._get_vel_orientation_x_gate_enabled()
        if torch.is_tensor(vel_orientation_x_gate_enabled) or bool(vel_orientation_x_gate_enabled):
            orientation_x_angle = torch.asin(torch.clamp(torch.abs(pgb[:, 1]), max=1.0))
            full_angle_deg = torch.clamp(
                self._as_reward_gate_tensor(self._get_vel_orientation_x_gate_full_deg(), orientation_x_angle),
                min=0.0,
            )
            zero_angle_deg = torch.maximum(
                torch.clamp(
                    self._as_reward_gate_tensor(self._get_vel_orientation_x_gate_zero_deg(), orientation_x_angle),
                    min=0.0,
                ),
                full_angle_deg,
            )
            full_angle = torch.deg2rad(full_angle_deg)
            zero_angle = torch.deg2rad(zero_angle_deg)
            angle_band = zero_angle - full_angle
            vel_orientation_x_gate = torch.where(
                angle_band <= 0.0,
                (orientation_x_angle <= full_angle).float(),
                torch.clamp(
                    (zero_angle - orientation_x_angle) / torch.clamp(angle_band, min=1.0e-6),
                    min=0.0,
                    max=1.0,
                ),
            )
            if torch.is_tensor(vel_orientation_x_gate_enabled):
                vel_orientation_x_gate = torch.where(
                    self._as_reward_gate_bool_tensor(vel_orientation_x_gate_enabled, orientation_x_angle),
                    vel_orientation_x_gate,
                    torch.ones_like(vel_orientation_x_gate),
                )
        else:
            vel_orientation_x_gate = 1.0

        vel_orientation_y_gate_enabled = self._get_vel_orientation_y_gate_enabled()
        if torch.is_tensor(vel_orientation_y_gate_enabled) or bool(vel_orientation_y_gate_enabled):
            orientation_y_angle = torch.asin(torch.clamp(torch.abs(pgb[:, 0]), max=1.0))
            full_angle_deg = torch.clamp(
                self._as_reward_gate_tensor(self._get_vel_orientation_y_gate_full_deg(), orientation_y_angle),
                min=0.0,
            )
            zero_angle_deg = torch.maximum(
                torch.clamp(
                    self._as_reward_gate_tensor(self._get_vel_orientation_y_gate_zero_deg(), orientation_y_angle),
                    min=0.0,
                ),
                full_angle_deg,
            )
            full_angle = torch.deg2rad(full_angle_deg)
            zero_angle = torch.deg2rad(zero_angle_deg)
            angle_band = zero_angle - full_angle
            vel_orientation_y_gate = torch.where(
                angle_band <= 0.0,
                (orientation_y_angle <= full_angle).float(),
                torch.clamp(
                    (zero_angle - orientation_y_angle) / torch.clamp(angle_band, min=1.0e-6),
                    min=0.0,
                    max=1.0,
                ),
            )
            if torch.is_tensor(vel_orientation_y_gate_enabled):
                vel_orientation_y_gate = torch.where(
                    self._as_reward_gate_bool_tensor(vel_orientation_y_gate_enabled, orientation_y_angle),
                    vel_orientation_y_gate,
                    torch.ones_like(vel_orientation_y_gate),
                )
        else:
            vel_orientation_y_gate = 1.0

        if bool(getattr(self.cfg, "height_upright_gate_enabled", False)):
            height_sigma = float(getattr(self.cfg, "height_upright_gate_sigma", 0.02))
            height_sigma = max(height_sigma, 1e-6)
            height_upright_gate = torch.exp(-upright_err / height_sigma)
        else:
            height_upright_gate = 1.0

        # 相对地面高度（默认模式）/ 绝对或腿长高度模式（按当前 cfg 保持原定义）
        obs_height = self._get_observed_height(wheel_pos_b)
        if self._use_absolute_height() or self._use_leg_length_height():
            relative_obs_height = obs_height
        else:
            relative_obs_height = obs_height - self.ground_z_est
        wheel_relative_ground_heights = self._get_wheel_relative_ground_heights_raw()
        self.wheel_relative_ground_heights = wheel_relative_ground_heights
        wheel_height_w = self.robot.data.body_pos_w[:, self._wheel_link_idx, 2]
        height_reward_ref = self._get_height_reward_reference_height(relative_obs_height, wheel_height_w)
        # print(height_reward_ref)
        # 普通速度 tracking 仍按“水平前进速度”计算：
        # 使用机体系前向 x 速度，再通过机身 pitch 投影到水平面，避免直接拿机体系 x 导致冲坡时高估水平速度。
        root_rpy = euler_xyz_from_quat(self.robot.data.root_quat_w)
        pitch = wrap_to_pi(root_rpy[1])
        roll = wrap_to_pi(root_rpy[0])
        rew_flat_pitch_l1 = torch.abs(pitch*self.cfg.flat_pitch_l1_sigma)
        rew_flat_pitch_tanh = 1 - torch.tanh(torch.abs(pitch)/self.cfg.flat_pitch_tanh_sigma)
        rew_flat_roll_l1 = torch.abs(roll*self.cfg.flat_roll_l1_sigma)
        rew_flat_roll_tanh = 1 - torch.tanh(torch.abs(roll)/self.cfg.flat_roll_tanh_sigma)

        forward_lin_vel_horizontal = self.robot.data.root_lin_vel_b[:, 0] * torch.cos(pitch)
        lin_vel_err = tracking_command[:, 0] - forward_lin_vel_horizontal
        if self.cfg.lin_vel_err_constraint is not None:
            track_lin_vel_err = torch.square(torch.clamp(lin_vel_err,
                                                         min=-self.cfg.lin_vel_err_constraint,
                                                         max=self.cfg.lin_vel_err_constraint))
        else:
            track_lin_vel_err = torch.square(lin_vel_err)
        rew_track_lin_vel_xy = torch.exp(-track_lin_vel_err / self.cfg.lin_vel_xy_sigma)
        rew_track_lin_vel_xy_soft = torch.exp(-track_lin_vel_err / self.cfg.lin_vel_xy_soft_sigma)
        rew_track_lin_vel_xy_tight = torch.exp(-track_lin_vel_err / self.cfg.lin_vel_xy_tight_sigma)
        rew_track_lin_vel_xy_huge_gap = track_lin_vel_err>self.cfg.lin_vel_xy_torlarance_gap
        rew_track_lin_vel_xy_square = torch.square(
            lin_vel_err * self.cfg.lin_vel_xy_square_sigma
        )
        lin_vel_abs_err = torch.abs(tracking_command[:, 0]) - torch.abs(forward_lin_vel_horizontal)
        rew_pen_high_speed = torch.square(torch.clamp(lin_vel_abs_err, max=0.)*self.cfg.high_speed_pen_sigma)

        ang_vel_err = tracking_command[:, 2] - self.robot.data.root_ang_vel_b[:, 2]
        if self.cfg.ang_vel_err_constraint is not None:
            track_yaw_rate_err = torch.square(torch.clamp(ang_vel_err,
                                                         min=-self.cfg.ang_vel_err_constraint,
                                                         max=self.cfg.ang_vel_err_constraint))
        else:
            track_yaw_rate_err = torch.square(ang_vel_err)
        rew_track_ang_vel_z = torch.exp(-track_yaw_rate_err / self.cfg.ang_vel_z_sigma)
        rew_track_ang_vel_z_soft = torch.exp(-track_yaw_rate_err / self.cfg.amg_vel_z_soft_sigma)
        rew_track_ang_vel_z_huge_gap = track_yaw_rate_err>self.cfg.ang_vel_z_torlarance_gap
        rew_track_ang_vel_z_square = torch.square(ang_vel_err*self.cfg.ang_vel_z_square_sigma)
        ang_vel_abs_err = torch.abs(tracking_command[:, 2]) - torch.abs(self.robot.data.root_ang_vel_b[:, 2])
        rew_pen_high_angVel = torch.square(torch.clamp(ang_vel_abs_err, max=0.)*self.cfg.high_angVel_pen_sigma)

        rew_stand_still = (
            torch.sum(torch.square(self.robot.data.root_lin_vel_b[:, :2]), dim=1)
            * stand_still_lin_mask.float()
            + torch.square(self.robot.data.root_ang_vel_b[:, 2]) * stand_still_yaw_mask.float()
        )
        rew_stand_still_lin_vel = (
            torch.sum(torch.abs(self.robot.data.root_lin_vel_b[:, :2]), dim=1)
            * stand_still_lin_mask.float()
        )

        # 约束加减速足端位置
        # foot_bound_square = torch.square(wheel_pos_heading_b[:,:,0])
        # rew_foot_bound = torch.sum(torch.abs(wheel_pos_heading_b[:,:,0])>self.cfg.foot_bound_dist,dim=1)
        # rew_foot_bound_square = torch.sum(torch.square(wheel_pos_heading_b[:,:,0]*self.cfg.foot_bound_square_sigma),dim=1)
        # rew_foot_bound_exp_pen = torch.sum(1-torch.exp(-foot_bound_square/self.cfg.foot_bound_exp_pen_sigma),dim=1)
        # rew_foot_bound_exp = torch.sum(torch.exp(-foot_bound_square/self.cfg.foot_bound_sigma),dim=1)
        # rew_foot_bound_ssquare = torch.sum(torch.square(foot_bound_square*self.cfg.foot_bound_ssquare_sigma),dim=1)

        rew_stand_nice = torch.sum(torch.square(wheel_pos_heading_b[:,:,0]),dim=-1)
        rew_no_fork_raw = torch.abs(wheel_pos_b[:,0,0]-wheel_pos_b[:,1,0])>self.cfg.no_fork_distance
        rew_no_fork = rew_no_fork_raw.float()
        # exp 平滑的 no_fork 约束：仅在超过阈值后逐渐加大惩罚（与 no_fork 的硬阈值互补）
        no_fork_dist = torch.abs(wheel_pos_b[:,0,0]-wheel_pos_b[:,1,0])
        no_fork_over = torch.clamp(no_fork_dist - self.cfg.no_fork_distance, min=0.0)
        rew_no_fork_exp = 1.0 - torch.exp(-no_fork_over / self.cfg.no_fork_exp_sigma)
        no_fork_z_distance = float(getattr(self.cfg, "no_fork_z_distance", self.cfg.no_fork_distance))
        rew_no_fork_z_raw = torch.abs(wheel_pos_b[:,0,2]-wheel_pos_b[:,1,2]) > no_fork_z_distance
        rew_no_fork_z = rew_no_fork_z_raw.float()
        no_fork_z_dist = torch.abs(wheel_pos_b[:,0,2]-wheel_pos_b[:,1,2])
        no_fork_z_over = torch.clamp(no_fork_z_dist - no_fork_z_distance, min=0.0)
        no_fork_z_exp_sigma = float(getattr(self.cfg, "no_fork_z_exp_sigma", self.cfg.no_fork_exp_sigma))
        rew_no_fork_z_exp = 1.0 - torch.exp(-no_fork_z_over / no_fork_z_exp_sigma)
        # 起身训练：落地阶段 no_fork 惩罚缩小
        # if getattr(self.cfg, 'enable_standup_training', False):
        #     landing_mask = (self._standup_phase == 0).float()
        #     no_fork_landing_scale = getattr(self.cfg, 'no_fork_landing_scale', 0.1)
        #     rew_no_fork = rew_no_fork_raw.float() * (1.0 - landing_mask * (1.0 - no_fork_landing_scale))
        # else:
        #     rew_no_fork = rew_no_fork_raw
        rew_no_fork_square = torch.square((wheel_pos_b[:,0,0]-wheel_pos_b[:,1,0])*self.cfg.no_fork_square_sigma)
        no_fork_z_square_sigma = float(getattr(self.cfg, "no_fork_z_square_sigma", self.cfg.no_fork_square_sigma))
        rew_no_fork_z_square = torch.square((wheel_pos_b[:,0,2]-wheel_pos_b[:,1,2]) * no_fork_z_square_sigma)
        # 兼容旧 reward key 名称：实际约束的是左右腿向量与世界重力方向对齐。
        wheel_motor_z_axis_align_err_sq = self._get_wheel_motor_z_axis_align_error_sq()
        wheel_motor_z_axis_align_sigma = max(
            float(
                getattr(
                    self.cfg,
                    "wheel_motor_z_axis_align_sigma",
                    getattr(self.cfg, "wheel_body_x_zero_sigma", 0.02),
                )
            ),
            1e-6,
        )
        wheel_motor_z_axis_align_tight_sigma = max(
            float(
                getattr(
                    self.cfg,
                    "wheel_motor_z_axis_align_tight_sigma",
                    getattr(self.cfg, "wheel_body_x_zero_tight_sigma", 0.002),
                )
            ),
            1e-6,
        )
        rew_wheel_motor_z_axis_align_exp = torch.exp(
            -wheel_motor_z_axis_align_err_sq / wheel_motor_z_axis_align_sigma
        )
        rew_wheel_motor_z_axis_align_exp_tight = torch.exp(
            -wheel_motor_z_axis_align_err_sq / wheel_motor_z_axis_align_tight_sigma
        )
        # rew_leg_end_vel = torch.sum(torch.square(wheel_lin_vel_b[:,:,0]),dim=-1)
        # rew_leg_angle_l2 = torch.sum(torch.square(torch.stack([left_leg_angle,right_leg_angle],dim=-1)),dim=-1)
        # rew_leg_angle_l1 = torch.sum(torch.abs(torch.stack([left_leg_angle,right_leg_angle],dim=-1)),dim=-1)
        # rew_leg_ang_vel_l2 = torch.sum(torch.square(leg_ang_vel),dim=-1)
        # rew_leg_ang_vel_l1 = torch.sum(torch.abs(leg_ang_vel),dim=-1)
        rew_l_leg_ang_exp = torch.exp(-torch.square(left_leg_angle)/self.cfg.l_leg_ang_exp_sigma)
        rew_r_leg_ang_exp = torch.exp(-torch.square(right_leg_angle)/self.cfg.r_leg_ang_exp_sigma)

        height_reward_target = self._get_height_reward_target_height()
        height_err = height_reward_ref - height_reward_target
        if self.cfg.height_err_constraint is not None:
            track_height_err = torch.square(torch.clamp(height_err,
                                                         min=-self.cfg.height_err_constraint,
                                                         max=self.cfg.height_err_constraint))
        else:
            track_height_err = torch.square(height_err)
        rew_track_height_square = torch.square(self.cfg.height_square_sigma * (height_err))
        rew_track_height_l1 = torch.abs(self.cfg.height_l1_sigma * (height_err))
        rew_track_height_exp = torch.exp(-track_height_err / self.cfg.height_sigma)
        rew_track_height_exp_soft = torch.exp(-track_height_err / self.cfg.height_soft_sigma)
        rew_track_height_exp_tight = torch.exp(-track_height_err / self.cfg.height_tight_sigma)
        rew_track_height_tanh = 1 - torch.tanh(torch.abs(height_err)/self.cfg.height_tanh_sigma)
        rew_pen_base_too_low = torch.square(torch.clamp((self.cfg.base_height_bound-height_reward_ref), min=0.)*self.cfg.pen_base_too_low_sigma)

        # 速度高度门控：高度没跟住时降低速度/角速度 tracking 奖励，避免 policy 为了追速度牺牲高度。
        vel_height_gate_enabled = self._get_vel_height_gate_enabled()
        # enabled 可以是全局 bool，也可以是 per-env bool tensor；tensor 用于不同任务/状态单独开关。
        if torch.is_tensor(vel_height_gate_enabled) or bool(vel_height_gate_enabled):
            vel_height_gate_mode = str(getattr(self.cfg, "vel_height_gate_mode", "exp")).lower()
            if vel_height_gate_mode in ("linear_band", "band", "piecewise_linear"):
                height_abs_err = torch.abs(height_reward_ref - height_reward_target)
                # full_error 内门控为 1；zero_error 外门控为 0；中间线性衰减。
                full_error = torch.clamp(
                    self._as_reward_gate_tensor(self._get_vel_height_gate_full_error(), height_abs_err),
                    min=0.0,
                )
                zero_error = torch.maximum(
                    torch.clamp(
                        self._as_reward_gate_tensor(self._get_vel_height_gate_zero_error(), height_abs_err),
                        min=0.0,
                    ),
                    full_error,
                )
                height_band = zero_error - full_error
                vel_height_gate = torch.where(
                    # 若 full_error == zero_error，则退化为硬阈值，避免除以 0。
                    height_band <= 0.0,
                    (height_abs_err <= full_error).float(),
                    torch.clamp(
                        (zero_error - height_abs_err) / torch.clamp(height_band, min=1.0e-6),
                        min=0.0,
                        max=1.0,
                    ),
                )
            else:
                # 指数模式：默认复用高度 tracking reward，也可单独配置 tracker sigma。
                vel_gate_sigma_cfg = getattr(self.cfg, "vel_height_gate_tracker_sigma", None)
                if vel_gate_sigma_cfg is None:
                    vel_height_gate = rew_track_height_exp
                else:
                    vel_gate_sigma = max(float(vel_gate_sigma_cfg), 1e-6)
                    vel_height_gate = torch.exp(-track_height_err / vel_gate_sigma)
            if torch.is_tensor(vel_height_gate_enabled):
                # 对未启用高度门控的 env，门控置 1，相当于不影响速度 tracking 奖励。
                vel_height_gate = torch.where(
                    self._as_reward_gate_bool_tensor(vel_height_gate_enabled, height_reward_ref),
                    vel_height_gate,
                    torch.ones_like(vel_height_gate),
                )
        else:
            vel_height_gate = 1.0

        # 叠加门控
        vel_reward_gate = vel_upright_gate * vel_orientation_x_gate * vel_orientation_y_gate * vel_height_gate
        rew_track_lin_vel_xy = rew_track_lin_vel_xy * vel_reward_gate
        rew_track_lin_vel_xy_soft = rew_track_lin_vel_xy_soft * vel_reward_gate
        rew_track_lin_vel_xy_tight = rew_track_lin_vel_xy_tight * vel_reward_gate
        rew_track_lin_vel_xy_square = rew_track_lin_vel_xy_square * vel_reward_gate
        rew_track_ang_vel_z = rew_track_ang_vel_z * vel_reward_gate
        rew_track_ang_vel_z_soft = rew_track_ang_vel_z_soft * vel_reward_gate
        rew_track_ang_vel_z_square = rew_track_ang_vel_z_square * vel_reward_gate
        rew_track_lin_vel_xy_huge_gap = rew_track_lin_vel_xy_huge_gap.float()
        rew_track_ang_vel_z_huge_gap = rew_track_ang_vel_z_huge_gap.float()

        rew_track_height_exp = rew_track_height_exp * height_upright_gate
        rew_track_height_exp_soft = rew_track_height_exp_soft * height_upright_gate
        rew_track_height_exp_tight = rew_track_height_exp_tight * height_upright_gate
        rew_track_height_huge_gap = height_reward_target - obs_height > self.cfg.height_torlarance_gap
        # print(torch.abs(wheel_pos_b[:,0,0]-wheel_pos_b[:,1,0]))
        # print('tar',self.height_cmd)
        # print('cur',obs_height)

        # undesired contacts
        net_contact_forces = self.contact_sensor.data.net_forces_w_history
        undesired_contact_force_threshold = float(
            getattr(self.cfg, "undesired_contact_force_threshold", 5.0)
        )
        desired_contact_force_threshold = float(
            getattr(self.cfg, "desired_contact_force_threshold", 1.0)
        )
        wheel_contact_force_peaks = self._get_wheel_contact_force_peaks(net_contact_forces)
        if wheel_contact_force_peaks.shape[1] >= 2:
            both_wheels_contact = torch.all(
                wheel_contact_force_peaks > desired_contact_force_threshold, dim=1
            )
        else:
            both_wheels_contact = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        rew_wheel_air_spin = self._get_wheel_air_spin_reward(
            wheel_contact_force_peaks,
            desired_contact_force_threshold,
        )
        rew_track_height_exp_both_wheels_contact = (
            rew_track_height_exp_soft * both_wheels_contact.float()
        )

        # 计算总的有害接触奖励 (用于训练)
        if net_contact_forces is not None:
            harmful_contact_mask = (
                torch.norm(net_contact_forces[:, :, self._undesired_contact_link_idx], dim=-1)
                > undesired_contact_force_threshold
            )
            is_contact = torch.max(torch.max(harmful_contact_mask, dim=1)[0], dim=1)[0]
            rew_undesired_contact = is_contact.float()
        else:
            rew_undesired_contact = torch.zeros(self.num_envs, device=self.device)

        self._debug_print_undesired_contacts(net_contact_forces)

        # [内置] 实时终端打印 (已移除)

        # desired contacts (车轮触地奖励/惩罚)
        if wheel_contact_force_peaks.shape[1] > 0:
            # 检查车轮是否在历史窗口内有接触
            is_not_contact = wheel_contact_force_peaks < desired_contact_force_threshold
            rew_desired_contact = torch.sum(is_not_contact.float(), dim=1)
        else:
            rew_desired_contact = torch.zeros(self.num_envs, device=self.device)

        # dof limits
        if bool(getattr(self.cfg, "front_rear_joint_limit_rewards_enabled", True)):
            limits_actions_joint_error = [(self.leg_actions[:,0]-self.leg_actions[:,1]).unsqueeze(-1),
                                  (self.leg_actions[:,2]-self.leg_actions[:,3]).unsqueeze(-1)]
            limits_actions_joint_error = torch.cat(limits_actions_joint_error,dim=-1)
            upper_error = limits_actions_joint_error > self.cfg.leg_front_rear_range[1]
            lower_error = limits_actions_joint_error < self.cfg.leg_front_rear_range[0]
            rew_actions_joint_limits = torch.sum(upper_error+lower_error,dim=-1)

            limits_joint_error = self.joint_pos[:,self._legs_front_idx] - self.joint_pos[:,self._legs_rear_idx]
            soft_range = [0.,0.]
            scale_range = abs(self.cfg.leg_front_rear_range[1]-self.cfg.leg_front_rear_range[0])*(1-self.cfg.soft_range_scale)
            soft_range[0] = self.cfg.leg_front_rear_range[0] + scale_range
            soft_range[1] = self.cfg.leg_front_rear_range[1] - scale_range
            upper_error = limits_joint_error > soft_range[1]
            lower_error = limits_joint_error < soft_range[0]
            rew_current_joint_limits = torch.sum(upper_error+lower_error,dim=-1)
        else:
            rew_actions_joint_limits = torch.zeros(self.num_envs, device=self.device)
            rew_current_joint_limits = torch.zeros(self.num_envs, device=self.device)

        (
            rew_rear2_rear1_joint_pos_limits,
            rew_rear2_rear1_joint_pos_limits_torque,
            rew_rear2_rear1_joint_pos_limits_vel,
        ) = self._get_rear2_rear1_joint_limit_terms()

        # 起身训练奖励（仅 phase=1 起身阶段非零）
        # in_standup = (self._standup_phase == 1) if getattr(self.cfg, 'enable_standup_training', False) else False
        # if getattr(self.cfg, 'enable_standup_training', False):
        #     standup_mask = in_standup.float()
        #     rew_standup_height = obs_height * standup_mask
        #     rew_standup_vel_z = torch.clamp(self.robot.data.root_lin_vel_b[:, 2], min=0.0) * standup_mask
        #     rew_standup_smoothness = rew_action_smoothness * standup_mask
        #     rew_standup_joint_torque = rew_joint_torque * standup_mask
        #     rew_standup_wheel_power = rew_wheel_power * standup_mask
        #     rew_standup_leg_joint_acc = rew_leg_joint_acc * standup_mask
        #     rew_standup_wheel_vel = rew_wheel_vel * standup_mask
        # else:
        #     rew_standup_height = torch.zeros(self.num_envs, device=self.device)
        #     rew_standup_vel_z = torch.zeros(self.num_envs, device=self.device)
        #     rew_standup_smoothness = torch.zeros(self.num_envs, device=self.device)
        #     rew_standup_joint_torque = torch.zeros(self.num_envs, device=self.device)
        #     rew_standup_wheel_power = torch.zeros(self.num_envs, device=self.device)
        #     rew_standup_leg_joint_acc = torch.zeros(self.num_envs, device=self.device)
        #     rew_standup_wheel_vel = torch.zeros(self.num_envs, device=self.device)

        reward_terms = {k[4:]: v for k, v in locals().items() if k.startswith("rew_")}
        reward_terms = self._postprocess_reward_terms(reward_terms)

        # gather rewards
        rewards = {k: v * self.step_dt for k, v in reward_terms.items()}
        # 用 .get() 防止 cfg.rewards 里存在但对应 rew_* 变量被注释掉的键（如 standup 相关）
        _zero_rew = torch.zeros(self.num_envs, device=self.device)
        rewards = {k: w * rewards.get(k, _zero_rew) for k, w in self.cfg.rewards.items()}

        # 数值保护：
        # 1. 将每个 reward term 内部产生的 NaN/Inf 直接归零，防止污染 rollout。
        # 2. 对本 step 已判定物理爆炸的 env，整条 reward 置零，避免坏状态参与 PPO 更新。
        bad_reward_envs = self._numerical_safety_reset_buf
        if bad_reward_envs.any():
            bad_reward_envs_f = bad_reward_envs.float()
            keep_reward_envs_f = (~bad_reward_envs).float()
        for key, value in rewards.items():
            sanitized_value = torch.nan_to_num(value, nan=0.0, posinf=0.0, neginf=0.0)
            if bad_reward_envs.any():
                sanitized_value = sanitized_value * keep_reward_envs_f
            rewards[key] = sanitized_value
        self._last_reward_terms = {key: value.detach() for key, value in rewards.items()}

        if bool(getattr(self.cfg, "reward_groups_enabled", False)):
            group_names = tuple(getattr(self.cfg, "reward_group_names", ("task", "safety", "energy")))
            group_index = {name: idx for idx, name in enumerate(group_names)}
            term_groups = dict(getattr(self.cfg, "reward_term_groups", {}))
            reward_groups = torch.zeros(
                self.num_envs,
                len(group_names),
                dtype=torch.float,
                device=self.device,
            )
            default_group = group_index.get("task", 0)
            for key, value in rewards.items():
                group_name = term_groups.get(key, "task")
                group_id = group_index.get(group_name, default_group)
                reward_groups[:, group_id] += value
            self.extras["reward_groups"] = torch.nan_to_num(
                reward_groups,
                nan=0.0,
                posinf=0.0,
                neginf=0.0,
            )

        # Stepping command
        sync_cmd_iteration = getattr(self, "_sync_command_generator_training_iteration", None)
        if sync_cmd_iteration is not None:
            sync_cmd_iteration()
        self.command_generator.compute(self.step_dt)
        self._resample_custom_cmd(self.command_generator.command_counter)
        self.command = self.command_generator.command.clone()
        self._on_command_updated()
        self._apply_predefined_reset_air_command_limits()

        # Logging rewards
        for key, value in rewards.items():
            if key not in self._episode_sums:
                self._episode_sums[key] = torch.zeros(self.num_envs, dtype=torch.float, device=self.device)
            self._episode_sums[key] += value
        rewards_tensor = torch.stack([rewards[k] for k in self.cfg.rewards.keys()], dim=-1)
        total_reward = torch.sum(rewards_tensor, dim=-1)
        total_reward = torch.nan_to_num(total_reward, nan=0.0, posinf=0.0, neginf=0.0)
        self._last_total_reward = total_reward.detach()
        self._debug_print_reward_and_state_stats(rewards, total_reward)
        return total_reward
~~~

</details>


<details markdown="1"><summary>_get_dones</summary>

[源码](<D:/WHEEL_LEG_RL/wheeled-legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py:4911>)
~~~python
def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        # contact termination
        reset_contact_force = torch.norm(
            self.contact_sensor.data.net_forces_w[:, self._reset_contact_link_idx], dim=-1)
        time_out = self.episode_length_buf >= self.max_episode_length - 1
        terminate = torch.any(reset_contact_force > 1.0, dim=-1)

        # ------------------------------------------------------------------
        # Numerical safety termination
        # - NaN/Inf in key states -> terminate immediately
        # - Large outliers in velocities -> terminate immediately
        # This prevents a single "bad" env from polluting rollout with NaNs.
        # ------------------------------------------------------------------
        joint_vel_act = self.joint_vel[:, self._actuate_idx]
        root_lin_vel_b = self.robot.data.root_lin_vel_b
        root_ang_vel_b = self.robot.data.root_ang_vel_b

        nan_terminate = (
            ~torch.isfinite(joint_vel_act).all(dim=-1)
            | ~torch.isfinite(root_lin_vel_b).all(dim=-1)
            | ~torch.isfinite(root_ang_vel_b).all(dim=-1)
        )

        joint_vel_abs_th = float(getattr(self.cfg, "terminate_joint_vel_abs", 500))
        root_ang_vel_abs_th = float(getattr(self.cfg, "terminate_root_ang_vel_abs", 200.0))
        root_lin_vel_abs_th = float(getattr(self.cfg, "terminate_root_lin_vel_abs", 100.0))

        joint_vel_abs = torch.amax(torch.abs(joint_vel_act), dim=-1)
        root_ang_vel_abs = torch.amax(torch.abs(root_ang_vel_b), dim=-1)
        root_lin_vel_abs = torch.amax(torch.abs(root_lin_vel_b), dim=-1)

        outlier_terminate = (
            (joint_vel_abs > joint_vel_abs_th)
            | (root_ang_vel_abs > root_ang_vel_abs_th)
            | (root_lin_vel_abs > root_lin_vel_abs_th)
        )
        self._numerical_safety_reset_buf.copy_(nan_terminate | outlier_terminate)
        # 数值安全类终止（NaN/Inf + Outlier）必须立即生效，不受 termination_duration 限制
        immediate_terminate = nan_terminate | outlier_terminate
        # 3. 精准打印逻辑
        if bool(getattr(self.cfg, "debug_numerical_safety_print", False)) and outlier_terminate.any():
            # 获取触发异常的环境索引 (env_ids)
            outlier_indices = torch.where(outlier_terminate)[0]

            print(f"\n[!!!] 检测到 {len(outlier_indices)} 个环境数值爆炸:")
            for idx in outlier_indices:
                env_id = idx.item()
                print(f"--- Env ID: {env_id} ---")
                print(f"  关节速度最大值: {joint_vel_abs[env_id]:.4f} (阈值: {joint_vel_abs_th})")
                print(f"  机身角速度最大值: {root_ang_vel_abs[env_id]:.4f} (阈值: {root_ang_vel_abs_th})")
                print(f"  机身线速度最大值: {root_lin_vel_abs[env_id]:.4f} (阈值: {root_lin_vel_abs_th})")
            print("########################################################################")

        terminate |= immediate_terminate

        # ------------------------------------------------------------------
        # Observation safety termination
        # - raw obs / raw privileged obs 非有限或超过阈值 -> terminate
        # 说明：raw obs 在 _get_observations() 里缓存，确保包含 actions 等未 clip 的输入。
        # ------------------------------------------------------------------
        if self._terminate_on_obs_outlier and self._value_debug_step > 10:
            obs_abs_th = self._terminate_obs_abs if self._terminate_obs_abs > 0.0 else float(getattr(self.cfg, "debug_obs_alert_threshold", 0.0))
            obs_outlier_terminate = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)

            if obs_abs_th > 0.0:
                obs_outlier_terminate |= self._obs_raw_policy_max_abs > obs_abs_th
                if self.cfg.state_space is not None:
                    obs_outlier_terminate |= self._obs_raw_critic_max_abs > obs_abs_th

            obs_outlier_terminate |= self._obs_raw_policy_has_nonfinite
            if self.cfg.state_space is not None:
                obs_outlier_terminate |= self._obs_raw_critic_has_nonfinite

            if obs_outlier_terminate.any():
                self._terminate_obs_print_counter += 1
                if self._terminate_obs_print_interval <= 1 or (self._terminate_obs_print_counter % self._terminate_obs_print_interval == 0):
                    bad_ids = torch.where(obs_outlier_terminate)[0]
                    print(f"\n[ObsReset] 检测到 {len(bad_ids)} 个环境 raw obs 异常，将触发 reset. th={obs_abs_th}")
                    print(f"[ObsReset] env_ids={bad_ids.detach().cpu().tolist()}")

            immediate_terminate |= obs_outlier_terminate
            terminate |= obs_outlier_terminate

        # orientation termination
        root_rpy = euler_xyz_from_quat(self.robot.data.root_quat_w)
        roll_limit_rad = torch.deg2rad(
            torch.tensor(float(getattr(self.cfg, "termination_roll_deg", 40.0)), device=self.device)
        )
        pitch_limit_rad = torch.deg2rad(
            torch.tensor(float(getattr(self.cfg, "termination_pitch_deg", 40.0)), device=self.device)
        )
        terminate |= torch.abs(wrap_to_pi(root_rpy[0])) > roll_limit_rad
        terminate |= torch.abs(wrap_to_pi(root_rpy[1])) > pitch_limit_rad
        if bool(getattr(self.cfg, "reset_heading_target_terminate_enabled", False)):
            reset_heading_target_threshold_rad = torch.deg2rad(
                torch.tensor(
                    float(getattr(self.cfg, "reset_heading_target_terminate_threshold_deg", 2.0)),
                    device=self.device,
                )
            )
            reset_heading_error = torch.abs(wrap_to_pi(self.robot.data.heading_w - self.reset_heading_target))
            terminate |= reset_heading_error > reset_heading_target_threshold_rad
        # 根据不同状态机覆盖终止需求
        terminate, time_out = self.state_machine_manager.apply_done_masks(
            self, terminate, time_out
        )
        # 可以设置终止连续条件，持续N步满足才真正终止
        # 注意：数值安全类终止（NaN/Inf/Outlier/观测异常）不受 duration 限制，立即生效，
        # 以避免 NaN 环境在延迟窗口内持续污染仿真和 PPO rollout。
        delayed_terminate = terminate & ~immediate_terminate
        delayed_terminate = self._apply_termination_duration(delayed_terminate)
        terminate = delayed_terminate | immediate_terminate

        # others
        if self.cfg.play is True and not bool(getattr(self.cfg, "play_keep_done_reset", False)):
            terminate = torch.zeros_like(terminate)

        return terminate, time_out
~~~

</details>


<details markdown="1"><summary>_update_ground_height_estimate</summary>

[源码](<D:/WHEEL_LEG_RL/wheeled-legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py:5669>)
~~~python
def _update_ground_height_estimate(self):
        """使用RayCaster估计地面高度。"""
        if self._cached_ground_height_valid:
            return
        # 使用 height_scanner 获取地面高度
        if self.height_scanner is None or self._use_absolute_height() or self._use_leg_length_height():
            self.ground_z_est.zero_()
            self._cached_ground_height_valid = True
            return

        ray_hits = getattr(self.height_scanner.data, "ray_hits_w", None)
        if ray_hits is None or ray_hits.ndim != 3 or ray_hits.shape[1] == 0:
            self.ground_z_est = self.terrain.env_origins[:, 2]
            self._cached_ground_height_valid = True
            return

        ray_hits_z = ray_hits[:, :, 2]
        valid_mask = torch.isfinite(ray_hits_z)
        fallback_z = self.terrain.env_origins[:, 2]
        env_any_valid = torch.any(valid_mask, dim=1)
        sum_z = torch.sum(ray_hits_z.masked_fill(~valid_mask, 0.0), dim=1)
        count_z = torch.sum(valid_mask.float(), dim=1)
        mean_z = sum_z / torch.clamp(count_z, min=1.0)
        self.ground_z_est = torch.where(env_any_valid, mean_z, fallback_z)
        self._cached_ground_height_valid = True
~~~

</details>


## SCUT wheelbipe_V14/env.py


<details markdown="1"><summary>_get_rough_terrain_boundary_time_out</summary>

[源码](<D:/WHEEL_LEG_RL/wheeled-legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env.py:541>)
~~~python
def _get_rough_terrain_boundary_time_out(self) -> torch.Tensor:
        cfg = get_rough_terrain_boundary_reset_cfg(self.cfg)
        if not bool(cfg["enabled"]):
            return torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)

        terrain_cfg = getattr(self.cfg, "terrain", None)
        terrain_gen = getattr(terrain_cfg, "terrain_generator", None)
        if terrain_gen is None:
            return torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)

        size = getattr(terrain_gen, "size", None)
        if size is None or len(size) < 2:
            return torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)

        half_x = 0.5 * float(getattr(terrain_gen, "num_rows", 0)) * float(size[0])
        half_y = 0.5 * float(getattr(terrain_gen, "num_cols", 0)) * float(size[1])
        if not bool(cfg["use_inner_terrain_area"]):
            border_width = float(getattr(terrain_gen, "border_width", 0.0))
            half_x += border_width
            half_y += border_width

        margin = max(float(cfg["margin"]), 0.0)
        half_x = max(half_x - margin, 0.0)
        half_y = max(half_y - margin, 0.0)
        root_pos_w = self.robot.data.root_pos_w
        return (torch.abs(root_pos_w[:, 0]) > half_x) | (torch.abs(root_pos_w[:, 1]) > half_y)
~~~

</details>


<details markdown="1"><summary>_get_gimbal_spin_translate_reward_terms</summary>

[源码](<D:/WHEEL_LEG_RL/wheeled-legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env.py:988>)
~~~python
def _get_gimbal_spin_translate_reward_terms(self) -> dict[str, torch.Tensor]:
        zero = torch.zeros(self.num_envs, dtype=torch.float, device=self.device)
        if not hasattr(self, "_gimbal_spin_translate_active") or not torch.any(self._gimbal_spin_translate_active):
            return {
                "gimbal_spin_track_lin_vel_yaw_frame": zero,
                "gimbal_spin_track_lin_speed": zero,
                "gimbal_spin_track_lin_heading": zero,
                "gimbal_spin_lin_vel_yaw_square": zero,
                "gimbal_spin_lin_speed_overshoot": zero,
                "gimbal_spin_heading_error_square": zero,
                "gimbal_spin_stand_still_lin_vel": zero,
                "gimbal_spin_track_lin_heading_v2": zero,
                "gimbal_spin_heading_error_square_v2": zero,
            }

        active = self._gimbal_spin_translate_active.float()
        cmd_yaw = self._gimbal_spin_translate_lin_vel_yaw
        meas_yaw = self._get_gimbal_spin_translate_measured_lin_vel_yaw()
        err_yaw = cmd_yaw - meas_yaw
        err_yaw_sq = torch.sum(torch.square(err_yaw), dim=-1)

        speed_cmd = torch.linalg.norm(cmd_yaw, dim=-1)
        speed_meas = torch.linalg.norm(meas_yaw, dim=-1)
        speed_err = speed_cmd - speed_meas

        heading_cmd = torch.atan2(cmd_yaw[:, 1], cmd_yaw[:, 0])
        heading_meas = torch.atan2(meas_yaw[:, 1], meas_yaw[:, 0])
        heading_err = wrap_to_pi(heading_cmd - heading_meas)
        # Vector-based heading error: single atan2(cross, dot), naturally in [-π, π]
        heading_err_v2 = torch.atan2(
            cmd_yaw[:, 0] * meas_yaw[:, 1] - cmd_yaw[:, 1] * meas_yaw[:, 0],
            cmd_yaw[:, 0] * meas_yaw[:, 0] + cmd_yaw[:, 1] * meas_yaw[:, 1],
        )
        heading_gate = (
            (speed_cmd > float(getattr(self.cfg, "gimbal_spin_heading_cmd_speed_min", 0.1)))
            & (speed_meas > float(getattr(self.cfg, "gimbal_spin_heading_meas_speed_min", 0.05)))
        ).float()

        lin_vel_sigma = max(float(getattr(self.cfg, "gimbal_spin_lin_vel_yaw_sigma", 0.25)), 1.0e-6)
        speed_sigma = max(float(getattr(self.cfg, "gimbal_spin_lin_speed_sigma", 0.25)), 1.0e-6)
        heading_sigma = max(float(getattr(self.cfg, "gimbal_spin_lin_heading_sigma", 0.25)), 1.0e-6)
        lin_square_sigma = float(getattr(self.cfg, "gimbal_spin_lin_vel_yaw_square_sigma", 1.0))
        overshoot_sigma = float(getattr(self.cfg, "gimbal_spin_lin_speed_overshoot_sigma", 1.0))
        heading_square_sigma = float(getattr(self.cfg, "gimbal_spin_heading_error_square_sigma", 1.0))
        stand_still_speed_threshold = float(
            getattr(
                self.cfg,
                "gimbal_spin_stand_still_speed_threshold",
                self._get_gimbal_spin_translate_cfg().get("lin_vel_yaw_speed_deadzone", 0.05),
            )
        )
        stand_still_mask = (speed_cmd <= max(stand_still_speed_threshold, 0.0)).float()

        return {
            "gimbal_spin_track_lin_vel_yaw_frame": torch.exp(-err_yaw_sq / lin_vel_sigma) * active,
            "gimbal_spin_track_lin_speed": torch.exp(-torch.square(speed_err) / speed_sigma) * active,
            "gimbal_spin_track_lin_heading": torch.exp(-torch.square(heading_err) / heading_sigma) * active * heading_gate * (1.0 - stand_still_mask),
            "gimbal_spin_lin_vel_yaw_square": (lin_square_sigma ** 2) * err_yaw_sq * active,
            "gimbal_spin_lin_speed_overshoot": torch.square(
                torch.clamp(speed_meas - speed_cmd, min=0.0) * overshoot_sigma
            ) * active * (1.0 - stand_still_mask),
            "gimbal_spin_heading_error_square": torch.square(heading_err * heading_square_sigma) * active * heading_gate * (1.0 - stand_still_mask),
            "gimbal_spin_stand_still_lin_vel": torch.sum(torch.abs(meas_yaw), dim=-1) * active * stand_still_mask,
            "gimbal_spin_track_lin_heading_v2": torch.exp(-torch.square(heading_err_v2) / heading_sigma) * active * heading_gate * (1.0 - stand_still_mask),
            "gimbal_spin_heading_error_square_v2": torch.square(heading_err_v2 * heading_square_sigma) * active * heading_gate * (1.0 - stand_still_mask),
        }
~~~

</details>


<details markdown="1"><summary>_postprocess_reward_terms</summary>

[源码](<D:/WHEEL_LEG_RL/wheeled-legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env.py:1151>)
~~~python
def _postprocess_reward_terms(self, reward_terms: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        reward_terms = super()._postprocess_reward_terms(reward_terms)
        if hasattr(self, "_gimbal_spin_translate_active") and torch.any(self._gimbal_spin_translate_active):
            keep_mask = (~self._gimbal_spin_translate_active).float()
            suppressed_terms = getattr(
                self.cfg,
                "gimbal_spin_suppressed_reward_terms",
                (
                    "track_lin_vel_xy",
                    "track_lin_vel_xy_soft",
                    "track_lin_vel_xy_tight",
                    "track_lin_vel_xy_huge_gap",
                    "track_lin_vel_xy_square",
                    "stand_still_lin_vel",
                ),
            )
            for name in suppressed_terms:
                if name in reward_terms:
                    reward_terms[name] = reward_terms[name] * keep_mask
        reward_terms.update(self._get_gimbal_spin_translate_reward_terms())
        return reward_terms
~~~

</details>


## SCUT state_machines/airborne.py


<details markdown="1"><summary>_get_directional_wheel_speed_score</summary>

[源码](<D:/WHEEL_LEG_RL/wheeled-legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/airborne.py:588>)
~~~python
def _get_directional_wheel_speed_score(
        self,
        env,
        addition_cfg: dict,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        zero = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)
        wheel_idx = getattr(env, "_wheel_idx", [])
        if len(wheel_idx) == 0:
            return zero, zero

        reward_mask = self._get_reward_window_mask(env, addition_cfg)
        command_x = self._get_reward_command_lin_vel_x(env, addition_cfg)
        root_vel_x = env.robot.data.root_lin_vel_b[:, 0]
        command_threshold = max(float(addition_cfg.get("command_x_threshold", 1.0)), 0.0)
        root_vel_threshold = max(float(addition_cfg.get("root_x_threshold", 1.0)), 0.0)

        positive_mask = (command_x > command_threshold) & (root_vel_x > root_vel_threshold)
        negative_mask = (command_x < -command_threshold) & (root_vel_x < -root_vel_threshold)
        direction_gate = positive_mask | negative_mask
        direction = torch.zeros_like(command_x)
        direction[positive_mask] = 1.0
        direction[negative_mask] = -1.0

        speed_start = float(addition_cfg.get("start", 0.0))
        speed_full = float(addition_cfg.get("full", 10.0))
        denom = max(speed_full - speed_start, 1.0e-6)
        wheel_vel = env.joint_vel[:, wheel_idx]
        directional_speed = wheel_vel * direction.unsqueeze(-1)
        wheel_scores = torch.clamp((directional_speed - speed_start) / denom, 0.0, 1.0)

        reduce = addition_cfg.get("reduce", "min")
        if reduce == "min":
            score = wheel_scores.min(dim=1).values
        elif reduce == "mean":
            score = wheel_scores.mean(dim=1)
        elif reduce == "max":
            score = wheel_scores.max(dim=1).values
        else:
            raise ValueError(f"Unsupported directional wheel speed reduce mode: {reduce}")

        gate_f = (reward_mask & direction_gate).float()
        return gate_f * score, gate_f
~~~

</details>


<details markdown="1"><summary>get_height_reward_reference_height</summary>

[源码](<D:/WHEEL_LEG_RL/wheeled-legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/airborne.py:911>)
~~~python
def get_height_reward_reference_height(
        self,
        env,
        relative_obs_height: torch.Tensor,
        wheel_height_w: torch.Tensor,
    ) -> torch.Tensor:
        self.on_observation_step(env)
        cfg = self._cfg(env)
        if not self._height_reward_override_enabled(cfg):
            return relative_obs_height
        landing_active = getattr(env, "airborne_landing_traj_active", None)
        if landing_active is None:
            landing_active = torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
        # 普通状态下使用“机身相对地面高度”；airborne 状态下改用轮位置构造的高度参考。
        # 腿长模式本身就是轮心口径；非腿长模式要加回轮半径，保持 root-to-ground 高度口径。
        body_minus_highest_wheel_z = env.robot.data.root_pos_w[:, 2] - torch.amax(
            wheel_height_w, dim=1
        )
        if getattr(env, "_use_leg_length_height", None) is not None and env._use_leg_length_height():
            airborne_reference_height = body_minus_highest_wheel_z
        else:
            wheel_radius = float(self._cfg(env).get("enter", {})["wheel_radius"])
            airborne_reference_height = body_minus_highest_wheel_z + wheel_radius
        return torch.where(
            env.height_reward_airborne_state & (~landing_active),
            airborne_reference_height,
            relative_obs_height,
        )
~~~

</details>


<details markdown="1"><summary>get_height_reward_target_height</summary>

[源码](<D:/WHEEL_LEG_RL/wheeled-legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/airborne.py:940>)
~~~python
def get_height_reward_target_height(
        self, env, target_height: torch.Tensor
    ) -> torch.Tensor:
        cfg = self._cfg(env)
        if not bool(cfg.get("enabled", False)):
            return target_height
        landing_active = getattr(env, "airborne_landing_traj_active", None)
        if landing_active is None:
            landing_active = torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
        if torch.any(landing_active):
            landing_h_ref, _ = self._get_landing_trajectory_reference(env)
            target_height = torch.where(landing_active, landing_h_ref, target_height)
        if not self._height_reward_override_enabled(cfg):
            return target_height

        # airborne 时可临时抬高高度目标，引导机器人保持更合适的腾空姿态。
        target_height_cfg = cfg.get("target_height", {})
        airborne_bias = float(target_height_cfg["bias"])
        airborne_cmd_max = target_height_cfg["max"]
        if airborne_cmd_max is not None:
            max_height_target = float(airborne_cmd_max)
        else:
            height_range = getattr(env.cfg, "height_range", None)
            if height_range is not None and len(height_range) > 0:
                max_height_target = float(height_range[-1])
            else:
                max_height_target = float("inf")
        if getattr(env, "_use_leg_length_height", None) is not None and env._use_leg_length_height():
            wheel_radius = float(cfg.get("enter", {})["wheel_radius"])
            if max_height_target != float("inf"):
                # 腿长高度模式的 target 不含轮半径，因此上限也要对应减去轮半径。
                max_height_target = max(max_height_target - wheel_radius, 0.0)

        airborne_target_height = torch.clamp(
            target_height + airborne_bias,
            max=max_height_target,
        )
        return torch.where(
            env.height_reward_airborne_state & (~landing_active),
            airborne_target_height,
            target_height,
        )
~~~

</details>


<details markdown="1"><summary>apply_reward_term_scales</summary>

[源码](<D:/WHEEL_LEG_RL/wheeled-legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/airborne.py:983>)
~~~python
def apply_reward_term_scales(
        self, env, reward_terms: dict[str, torch.Tensor]
    ) -> dict[str, torch.Tensor]:
        airborne_mask_f = env.height_reward_airborne_state.float()
        reward_full = self._cfg(env).get("reward_full", {})
        for term_name, full_value in reward_full.items():
            if term_name not in reward_terms:
                continue
            reward_terms[term_name] = torch.where(
                env.height_reward_airborne_state,
                torch.full_like(reward_terms[term_name], float(full_value)),
                reward_terms[term_name],
            )

        reward_scales = self._cfg(env).get("reward_scales", {})
        for term_name, boost_scale in reward_scales.items():
            if term_name not in reward_terms:
                continue
            if term_name in reward_full:
                continue
            scale = 1.0 + airborne_mask_f * (float(boost_scale) - 1.0)
            reward_terms[term_name] = reward_terms[term_name] * scale

        reward_additions = self._cfg(env).get("reward_additions", {})
        reward_weights = getattr(env.cfg, "rewards", {})
        for term_name, addition_cfg in reward_additions.items():
            # reward_additions are materialized before cfg.rewards filters terms.
            # Skip disabled additions here so expensive contact/kinematics terms do
            # not run every step when their final reward weight is zero or absent.
            reward_weight = reward_weights.get(term_name, None)
            if reward_weight is None or float(reward_weight) == 0.0:
                continue
            if isinstance(addition_cfg, dict):
                addition_type = addition_cfg.get("type", "constant")
                if addition_type == "constant":
                    added_reward = airborne_mask_f * float(addition_cfg["value"])
                elif addition_type == "body_height_below":
                    threshold = float(addition_cfg["threshold"])
                    mode = addition_cfg.get("mode", "l1")
                    square_sigma = float(addition_cfg.get("square_sigma", 1.0))
                    body_relative_ground_height = env.robot.data.root_pos_w[:, 2] - env.ground_z_est
                    height_deficit = torch.clamp(
                        threshold - body_relative_ground_height,
                        min=0.0,
                    )
                    if mode == "l1":
                        added_reward = airborne_mask_f * height_deficit
                    elif mode == "l2":
                        added_reward = airborne_mask_f * square_sigma * torch.square(height_deficit)
                    elif mode == "binary":
                        added_reward = airborne_mask_f * (height_deficit > 0.0).float()
                    else:
                        raise ValueError(f"Unsupported body_height_below reward mode: {mode}")
                elif addition_type == "undesired_contact_force":
                    net_contact_forces = getattr(
                        getattr(getattr(env, "contact_sensor", None), "data", None),
                        "net_forces_w_history",
                        None,
                    )
                    if net_contact_forces is None or len(getattr(env, "_undesired_contact_link_idx", [])) == 0:
                        added_reward = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)
                    else:
                        force_threshold = float(
                            addition_cfg.get(
                                "force_threshold",
                                getattr(env.cfg, "undesired_contact_force_threshold", 5.0),
                            )
                        )
                        mode = addition_cfg.get("mode", "l2")
                        square_sigma = float(addition_cfg.get("square_sigma", 1.0))
                        contact_forces = torch.norm(
                            net_contact_forces[:, :, env._undesired_contact_link_idx].flatten(start_dim=1),
                            dim=-1,
                        )
                        force_over = torch.clamp(
                            contact_forces - force_threshold,
                            min=0.0,
                        )
                        added_reward = airborne_mask_f * self._shape_penalty(
                            force_over, mode, square_sigma=square_sigma
                        )
                elif addition_type == "wheel_contact_force_over":
                    net_contact_forces = getattr(
                        getattr(getattr(env, "contact_sensor", None), "data", None),
                        "net_forces_w_history",
                        None,
                    )
                    if net_contact_forces is None or len(getattr(env, "_desired_contact_link_idx", [])) == 0:
                        added_reward = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)
                    else:
                        force_threshold = float(
                            addition_cfg.get(
                                "force_threshold",
                                getattr(env.cfg, "desired_contact_force_threshold", 5.0),
                            )
                        )
                        mode = addition_cfg.get("mode", "l1")
                        square_sigma = float(addition_cfg.get("square_sigma", 1.0))
                        reduce = addition_cfg.get("reduce", "sum")
                        wheel_forces = torch.amax(
                            torch.norm(net_contact_forces[:, :, env._desired_contact_link_idx], dim=-1),
                            dim=1,
                        )
                        force_over = torch.clamp(wheel_forces - force_threshold, min=0.0)
                        wheel_penalty = self._shape_penalty(
                            force_over, mode, square_sigma=square_sigma
                        )
                        if reduce == "mean":
                            added_reward = airborne_mask_f * wheel_penalty.mean(dim=1)
                        elif reduce == "max":
                            added_reward = airborne_mask_f * wheel_penalty.max(dim=1).values
                        elif reduce == "sum":
                            added_reward = airborne_mask_f * wheel_penalty.sum(dim=1)
                        else:
                            raise ValueError(f"Unsupported wheel_contact_force_over reduce mode: {reduce}")
                elif addition_type == "landing_wheel_max_contact_force":
                    contact_forces_w = self._get_current_contact_forces(env)
                    if contact_forces_w is None or len(getattr(env, "_desired_contact_link_idx", [])) == 0:
                        added_reward = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)
                    else:
                        reward_mask = self._get_wheel_contact_started_mask(env, addition_cfg)
                        reward_mask &= self._get_wheel_contact_force_mask(env, addition_cfg)
                        force_start = float(addition_cfg.get("force_start", 200.0))
                        force_full = float(addition_cfg.get("force_full", 400.0))
                        denom = max(force_full - force_start, 1.0e-6)
                        wheel_forces = torch.norm(
                            contact_forces_w[:, env._desired_contact_link_idx], dim=-1
                        )
                        max_wheel_force = wheel_forces.max(dim=1).values
                        added_reward = reward_mask.float() * torch.clamp(
                            (max_wheel_force - force_start) / denom,
                            0.0,
                            1.0,
                        )
                elif addition_type == "landing_wheel_body_x_positive":
                    reward_mask = self._get_wheel_contact_started_mask(env, addition_cfg)
                    reward_mask &= self._get_wheel_contact_force_mask(env, addition_cfg)
                    command_x_min = float(addition_cfg.get("command_x_min", 1.0))
                    command_x = self._get_reward_command_lin_vel_x(env, addition_cfg)
                    reward_mask &= command_x > command_x_min
                    target_x = float(addition_cfg.get("target_x", 0.03))
                    sigma = max(float(addition_cfg.get("sigma", target_x)), 1.0e-6)
                    _, _, wheel_pos_heading_b, _, _ = env._get_root_quat_inv_and_wheel_pos_b()
                    wheel_x_min = wheel_pos_heading_b[:, :, 0].min(dim=1).values
                    deficit = torch.clamp(target_x - wheel_x_min, min=0.0)
                    added_reward = reward_mask.float() * torch.exp(-deficit / sigma)
                elif addition_type == "wheel_zero_torque_exp":
                    wheel_idx = getattr(env, "_wheel_idx", [])
                    if len(wheel_idx) == 0:
                        added_reward = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)
                    else:
                        reward_mask_f = self._get_reward_window_mask(env, addition_cfg).float()
                        sigma = max(float(addition_cfg.get("sigma", 1.5)), 1.0e-6)
                        wheel_torque = env.robot.data.applied_torque[:, wheel_idx]
                        max_wheel_torque = torch.abs(wheel_torque).max(dim=1).values
                        added_reward = reward_mask_f * torch.exp(
                            -torch.square(max_wheel_torque / sigma)
                        )
                elif addition_type == "wheel_directional_speed":
                    speed_score, _ = self._get_directional_wheel_speed_score(env, addition_cfg)
                    added_reward = speed_score
                elif addition_type == "wheel_directional_speed_shortfall":
                    speed_score, gate_f = self._get_directional_wheel_speed_score(env, addition_cfg)
                    added_reward = gate_f * (1.0 - speed_score)
                elif addition_type == "landing_traj_height_exp":
                    self._ensure_landing_trajectory_buffers(env)
                    active_f = env.airborne_landing_traj_active.float()
                    sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)
                    h_ref, _ = self._get_landing_trajectory_reference(env)
                    height = self._get_body_relative_ground_height(env)
                    added_reward = active_f * torch.exp(-torch.square(height - h_ref) / sigma)
                elif addition_type == "landing_traj_vel_z_exp":
                    self._ensure_landing_trajectory_buffers(env)
                    active_f = env.airborne_landing_traj_active.float()
                    sigma = max(float(addition_cfg.get("sigma", 0.25)), 1.0e-6)
                    _, v_ref = self._get_landing_trajectory_reference(env)
                    vel_z = env.robot.data.root_lin_vel_w[:, 2]
                    added_reward = active_f * torch.exp(-torch.square(vel_z - v_ref) / sigma)
                elif addition_type == "negative_lin_vel_z_after_wheel_contact":
                    wheel_exit_time = getattr(env, "airborne_wheel_contact_exit_time", None)
                    if wheel_exit_time is None:
                        added_reward = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)
                    else:
                        start_duration_s = max(float(addition_cfg.get("start_duration_s", 0.02)), 0.0)
                        use_world_frame = bool(addition_cfg.get("use_world_frame", True))
                        mode = addition_cfg.get("mode", "l2")
                        square_sigma = float(addition_cfg.get("square_sigma", 1.0))
                        wheel_contact_started = torch.any(wheel_exit_time >= start_duration_s, dim=1)
                        if use_world_frame:
                            lin_vel_z = env.robot.data.root_lin_vel_w[:, 2]
                        else:
                            lin_vel_z = env.robot.data.root_lin_vel_b[:, 2]
                        down_vel = torch.clamp(-lin_vel_z, min=0.0)
                        added_reward = (
                            airborne_mask_f
                            * wheel_contact_started.float()
                            * self._shape_penalty(down_vel, mode, square_sigma=square_sigma)
                        )
                elif addition_type == "negative_lin_vel_z_after_wheel_contact_exp":
                    wheel_exit_time = getattr(env, "airborne_wheel_contact_exit_time", None)
                    if wheel_exit_time is None:
                        added_reward = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)
                    else:
                        start_duration_s = max(float(addition_cfg.get("start_duration_s", 0.02)), 0.0)
                        use_world_frame = bool(addition_cfg.get("use_world_frame", True))
                        sigma = max(float(addition_cfg.get("sigma", 1.0)), 1.0e-6)
                        wheel_contact_started = torch.any(wheel_exit_time >= start_duration_s, dim=1)
                        if use_world_frame:
                            lin_vel_z = env.robot.data.root_lin_vel_w[:, 2]
                        else:
                            lin_vel_z = env.robot.data.root_lin_vel_b[:, 2]
                        added_reward = (
                            airborne_mask_f
                            * wheel_contact_started.float()
                            * torch.exp(-torch.square(lin_vel_z) / sigma)
                        )
                elif addition_type == "leg_retraction":
                    reward_mask_f = self._get_reward_window_mask(env, addition_cfg).float()
                    leg_lengths = self._get_leg_lengths(env)
                    mean_leg_length = leg_lengths.mean(dim=1)
                    target = float(addition_cfg.get("target", 0.22))
                    mode = addition_cfg.get("mode", "above_target")
                    if mode == "raw":
                        added_reward = reward_mask_f * mean_leg_length
                    elif mode == "above_target":
                        added_reward = reward_mask_f * torch.clamp(mean_leg_length - target, min=0.0)
                    elif mode == "above_target_per_leg":
                        added_reward = reward_mask_f * torch.clamp(leg_lengths - target, min=0.0).mean(dim=1)
                    elif mode == "below_target":
                        added_reward = reward_mask_f * torch.clamp(target - mean_leg_length, min=0.0)
                    elif mode == "below_target_per_leg":
                        added_reward = reward_mask_f * torch.clamp(target - leg_lengths, min=0.0).mean(dim=1)
                    elif mode == "exp":
                        sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)
                        added_reward = reward_mask_f * torch.exp(
                            -torch.square(mean_leg_length - target) / sigma
                        )
                    elif mode == "exp_per_leg":
                        sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)
                        added_reward = reward_mask_f * torch.exp(
                            -torch.square(leg_lengths - target) / sigma
                        ).mean(dim=1)
                    else:
                        raise ValueError(f"Unsupported airborne leg_retraction reward mode: {mode}")
                elif addition_type == "wheel_height_below_base_exp":
                    reward_mask_f = self._get_reward_window_mask(env, addition_cfg).float()
                    target = float(addition_cfg.get("target", 0.22))
                    sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)
                    rel_wheel_bottom_z = self._get_wheel_bottom_relative_to_base_z(env)
                    target_rel_wheel_bottom_z = -target
                    added_reward = reward_mask_f * torch.exp(
                        -torch.square(rel_wheel_bottom_z - target_rel_wheel_bottom_z) / sigma
                    ).mean(dim=1)
                elif addition_type == "wheel_heading_x_centering":
                    reward_mask_f = self._get_contact_timer_below_mask(env, addition_cfg).float()
                    sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)
                    _, _, wheel_pos_heading_b, _, _ = env._get_root_quat_inv_and_wheel_pos_b()
                    wheel_heading_z_max = addition_cfg.get("wheel_heading_z_max", None)
                    if wheel_heading_z_max is not None:
                        wheel_z_below = torch.all(
                            wheel_pos_heading_b[:, :, 2] < float(wheel_heading_z_max),
                            dim=1,
                        )
                        reward_mask_f = reward_mask_f * wheel_z_below.float()
                    wheel_x = wheel_pos_heading_b[:, :, 0]
                    added_reward = reward_mask_f * torch.exp(-torch.square(wheel_x) / sigma).mean(dim=1)
                elif addition_type == "wheel_bottom_slip_exp":
                    reward_mask_f = self._get_contact_timer_below_mask(env, addition_cfg).float()
                    sigma = max(float(addition_cfg.get("sigma", 0.25)), 1.0e-6)
                    wheel_radius = float(addition_cfg.get("wheel_radius", self._get_wheel_radius(env)))
                    wheel_lin_vel_w = env.robot.data.body_lin_vel_w[:, env._wheel_link_idx]
                    wheel_ang_vel_w = env.robot.data.body_ang_vel_w[:, env._wheel_link_idx]
                    bottom_offset_w = torch.zeros_like(wheel_lin_vel_w)
                    bottom_offset_w[..., 2] = -wheel_radius
                    wheel_bottom_vel_w = wheel_lin_vel_w + torch.cross(
                        wheel_ang_vel_w, bottom_offset_w, dim=-1
                    )
                    slip_speed = torch.linalg.norm(wheel_bottom_vel_w[..., :2], dim=-1)
                    wheel_reward = torch.exp(-torch.square(slip_speed) / sigma)

                    wheel_height_threshold = addition_cfg.get("wheel_height_threshold", None)
                    if wheel_height_threshold is not None:
                        wheel_heights = env._get_wheel_relative_ground_heights_raw()
                        near_ground = wheel_heights < float(wheel_height_threshold)
                        near_ground_f = near_ground.float()
                        near_ground_count = torch.clamp(near_ground_f.sum(dim=1), min=1.0)
                        added_reward = reward_mask_f * (
                            (wheel_reward * near_ground_f).sum(dim=1) / near_ground_count
                        ) * torch.any(near_ground, dim=1).float()
                    else:
                        added_reward = reward_mask_f * wheel_reward.mean(dim=1)
                elif addition_type in (
                    "rear2_rear1_joint_pos_limits",
                    "rear2_rear1_joint_pos_limits_vel_reg",
                ):
                    pos_penalty, vel_penalty = self._get_rear2_rear1_joint_limit_terms(env)
                    if addition_type == "rear2_rear1_joint_pos_limits":
                        added_reward = airborne_mask_f * pos_penalty
                    else:
                        added_reward = airborne_mask_f * vel_penalty
                else:
                    raise ValueError(f"Unsupported airborne reward addition type: {addition_type}")
            else:
                added_reward = airborne_mask_f * float(addition_cfg)
            if term_name in reward_terms:
                reward_terms[term_name] = reward_terms[term_name] + added_reward
            else:
                reward_terms[term_name] = added_reward

        return reward_terms
~~~

</details>


## SCUT state_machines/step_up.py


<details markdown="1"><summary>on_command_updated</summary>

[源码](<D:/WHEEL_LEG_RL/wheeled-legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/step_up.py:33>)
~~~python
def on_command_updated(self, env) -> None:
        # 没启用轮前向扫描时，清空本状态机维护的运行时状态，避免旧 episode 残留。
        cfg = self._cfg(env)
        if not bool(cfg.get("enabled", False)):
            env.wheel_forward_height_cmd_hold_remaining_time.zero_()
            env.wheel_forward_height_cmd_hold_value.zero_()
            env.wheel_forward_wall_reset.zero_()
            env.wheel_forward_step_detect_event.zero_()
            return

        # hold 是一个持续时间状态：每个 control step 递减，直到自动失效。
        env.wheel_forward_height_cmd_hold_remaining_time = torch.clamp(
            env.wheel_forward_height_cmd_hold_remaining_time - env.step_dt,
            min=0.0,
        )
        # step/wall 事件是单步检测结果，每次 command 更新前先清空再重新计算。
        env.wheel_forward_wall_reset.zero_()
        env.wheel_forward_step_detect_event.zero_()

        # 使用轮前方 raycast 的时间差分高度：当前前方地面高度 - 上一步前方地面高度。
        # 这样可以识别“前方突然抬高”的台阶/墙，而不是单纯依赖绝对高度。
        wheel_forward_height_diffs = env._get_wheel_forward_temporal_height_diffs_raw()
        if wheel_forward_height_diffs.shape[1] == 0:
            return

        # 高度差在 step_min 和 step_max 之间视为可跨越台阶；超过 wall_threshold 视为墙。
        detect_cfg = cfg.get("detect", {})
        height_cmd_cfg = cfg.get("height_cmd", {})
        step_min = float(detect_cfg.get("step_height_min", 0.15))
        step_max = float(detect_cfg.get("step_height_max", 0.25))
        wall_threshold = float(detect_cfg.get("wall_height", step_max))
        height_cmd_bias = float(height_cmd_cfg.get("bias", 0.05))
        hold_duration_s = max(float(height_cmd_cfg.get("hold_s", 2.0)), 0.0)

        # 墙优先级高于台阶：如果高度差过大，不再触发 step_up assist，而是结束该 episode。
        wall_reset_mask = torch.any(wheel_forward_height_diffs > wall_threshold, dim=1)
        step_detect_mask = torch.any(
            (wheel_forward_height_diffs > step_min)
            & (wheel_forward_height_diffs < step_max),
            dim=1,
        ) & (~wall_reset_mask)

        env.wheel_forward_wall_reset.copy_(wall_reset_mask)
        env.wheel_forward_step_detect_event.copy_(step_detect_mask)
        if torch.any(wall_reset_mask):
            # 碰到墙时取消任何已保持的抬高命令，避免下一次 reset/可视化继续显示旧状态。
            env.wheel_forward_height_cmd_hold_remaining_time[wall_reset_mask] = 0.0
            env.wheel_forward_height_cmd_hold_value[wall_reset_mask] = 0.0

        if torch.any(step_detect_mask) and hold_duration_s > 0.0:
            # 检测到台阶后，在原始 height_cmd 上加 bias，并按配置或 height_range 上限截断。
            wheel_forward_cmd_max = height_cmd_cfg.get("max", None)
            if wheel_forward_cmd_max is not None:
                max_height_target = float(wheel_forward_cmd_max)
            else:
                height_range = getattr(env.cfg, "height_range", None)
                if height_range is not None and len(height_range) > 0:
                    max_height_target = float(height_range[-1])
                else:
                    max_height_target = float("inf")
            env.wheel_forward_height_cmd_hold_value[step_detect_mask] = torch.clamp(
                env.height_cmd[step_detect_mask] + height_cmd_bias,
                max=max_height_target,
            )
            env.wheel_forward_height_cmd_hold_remaining_time[step_detect_mask] = hold_duration_s
~~~

</details>


<details markdown="1"><summary>apply_done_masks</summary>

[源码](<D:/WHEEL_LEG_RL/wheeled-legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/step_up.py:99>)
~~~python
def apply_done_masks(
        self,
        env,
        terminate: torch.Tensor,
        time_out: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        # 墙阻挡不是策略失败，而是地形不可通过/需要换环境，因此转成 time_out 而非 terminate。
        time_out = time_out | env.wheel_forward_wall_reset
        terminate = terminate & (~env.wheel_forward_wall_reset)
        return terminate, time_out
~~~

</details>


## 复旦全部已发现函数变体


<details markdown="1"><summary>check_termination / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:209>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:209>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:209>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:209>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:210>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:209>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:210>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:209>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:209>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:210>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:210>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:213>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:213>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:214>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:213>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:213>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:209>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:209>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:209>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:209>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:209>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:209>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:209>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:209>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:209>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:209>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:209>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:209>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:209>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:209>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:209>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:209>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:209>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:209>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:209>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:209>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:209>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:209>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:209>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:209>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:209>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:209>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:213>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:209>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:209>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:209>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:213>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:213>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:256>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:256>)
~~~python
def check_termination(self):
        """Check if environments need to be reset"""
        fail_buf = torch.any(
            torch.norm(
                self.contact_forces[:, self.termination_contact_indices, :], dim=-1
            )
            > 10.0,
            dim=1,
        )
        fail_buf |= self.projected_gravity[:, 2] > -0.1
        self.fail_buf *= fail_buf
        self.fail_buf += fail_buf
        self.time_out_buf = (
            self.episode_length_buf > self.max_episode_length
        )  # no terminal reward for time-outs
        if self.cfg.terrain.mesh_type in ["heightfield", "trimesh"]:
            self.edge_reset_buf = self.base_position[:, 0] > self.terrain_x_max - 1
            self.edge_reset_buf |= self.base_position[:, 0] < self.terrain_x_min + 1
            self.edge_reset_buf |= self.base_position[:, 1] > self.terrain_y_max - 1
            self.edge_reset_buf |= self.base_position[:, 1] < self.terrain_y_min + 1
        self.reset_buf = (
            (self.fail_buf > self.cfg.env.fail_to_terminal_time_s / self.dt)
            | self.time_out_buf
            | self.edge_reset_buf
        )
~~~

</details>


<details markdown="1"><summary>compute_reward / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:317>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:317>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:317>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:317>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:319>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:317>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:319>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:314>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:314>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:319>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:319>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:319>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:319>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:321>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:319>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:319>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:314>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:314>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:317>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:317>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:317>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:317>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:317>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:317>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:317>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:317>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:317>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:317>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:317>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:317>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:317>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:317>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:317>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:317>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:317>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:317>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:317>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:317>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:317>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:314>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:314>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:314>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:319>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:314>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:314>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:314>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:319>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:319>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:364>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:364>)
~~~python
def compute_reward(self):
        """Compute rewards
        Calls each reward function which had a non-zero scale (processed in self._prepare_reward_function())
        adds each terms to the episode sums and to the total reward
        """
        self.rew_buf[:] = 0.0
        for i in range(len(self.reward_functions)):
            name = self.reward_names[i]
            rew = self.reward_functions[i]() * self.reward_scales[name]
            rew = torch.clip(
                rew,
                -self.cfg.rewards.clip_single_reward * self.dt,
                self.cfg.rewards.clip_single_reward * self.dt,
            )
            self.rew_buf += rew
            self.episode_sums[name] += rew
        if self.cfg.rewards.only_positive_rewards:
            self.rew_buf[:] = torch.clip(self.rew_buf[:], min=0.0)
        # add termination reward after clipping
        if "termination" in self.reward_scales:
            rew = self._reward_termination() * self.reward_scales["termination"]
            self.rew_buf += rew
            self.episode_sums["termination"] += rew
~~~

</details>


<details markdown="1"><summary>compute_proprioception_observations / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:341>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:341>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:341>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:341>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:343>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:341>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:343>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:338>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:338>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:343>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:343>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:343>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:343>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:345>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:343>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:343>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:338>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:338>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:341>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:341>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:341>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:341>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:341>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:341>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:341>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:341>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:341>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:341>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:341>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:341>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:341>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:341>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:341>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:341>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:341>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:341>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:341>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:341>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:341>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:338>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:338>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:338>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:343>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:338>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:338>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:338>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:343>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:343>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:388>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:388>)
~~~python
def compute_proprioception_observations(self):
        # note that observation noise need to modified accordingly !!!
        obs_buf = torch.cat(
            (
                # self.base_lin_vel * self.obs_scales.lin_vel,
                self.base_ang_vel * self.obs_scales.ang_vel,
                self.projected_gravity,
                self.commands[:, :3] * self.commands_scale,
                (
                    self.dof_pos[:, [0, 1, 3, 4]]
                    - self.default_dof_pos[:, [0, 1, 3, 4]]
                )
                * self.obs_scales.dof_pos,
                self.dof_vel * self.obs_scales.dof_vel,
                self.actions,
            ),
            dim=-1,
        )
        return obs_buf
~~~

</details>


<details markdown="1"><summary>_resample_commands / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:684>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:684>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:684>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:684>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:686>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:684>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:686>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:681>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:681>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:686>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:686>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:686>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:686>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:688>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:686>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:686>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:681>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:681>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:684>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:684>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:684>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:684>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:684>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:684>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:684>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:684>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:684>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:684>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:684>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:684>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:684>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:684>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:684>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:684>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:684>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:684>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:684>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:684>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:684>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:681>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:681>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:681>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:686>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:681>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:681>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:681>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:686>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:686>)
~~~python
def _resample_commands(self, env_ids):
        """Randommly select commands of some environments

        Args:
            env_ids (List[int]): Environments ids for which new commands are needed
        """
        self.commands[env_ids, 0] = (
            self.command_ranges["lin_vel_x"][env_ids, 1]
            - self.command_ranges["lin_vel_x"][env_ids, 0]
        ) * torch.rand(len(env_ids), device=self.device) + self.command_ranges[
            "lin_vel_x"
        ][
            env_ids, 0
        ]
        self.commands[env_ids, 1] = (
            self.command_ranges["ang_vel_yaw"][env_ids, 1]
            - self.command_ranges["ang_vel_yaw"][env_ids, 0]
        ) * torch.rand(len(env_ids), device=self.device) + self.command_ranges[
            "ang_vel_yaw"
        ][
            env_ids, 0
        ]
        self.commands[env_ids, 2] = (
            self.command_ranges["height"][env_ids, 1]
            - self.command_ranges["height"][env_ids, 0]
        ) * torch.rand(len(env_ids), device=self.device) + self.command_ranges[
            "height"
        ][
            env_ids, 0
        ]

        # # 清空 jump_height
        # self.commands[env_ids, self.jump_cmd_idx] = 0.0

        # # 采样 jump_height（像 diablo 一样：先采样，再用 mask 置 0）
        # jl, jr = self.cfg.commands.ranges.jump_height
        # jump_heights = torch.rand(len(env_ids), device=self.device) * (jr - jl) + jl

        # # threshold 越大 => 越多置 0 => 越不跳
        # mask = torch.rand(len(env_ids), device=self.device) < self.cfg.commands.threshold
        # jump_heights[mask] = 0.0

        # self.commands[env_ids, self.jump_cmd_idx] = jump_heights

        # # 你想要的 jump 状态机（全局更新）
        # self.jump = self.commands[:, self.jump_cmd_idx] != 0


        if self.cfg.commands.heading_command:
            self.commands[env_ids, 3] = torch_rand_float(
                self.command_ranges["heading"][0],
                self.command_ranges["heading"][1],
                (len(env_ids), 1),
                device=self.device,
            ).squeeze(1)
~~~

</details>


<details markdown="1"><summary>_reset_dofs / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:765>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:765>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:765>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:765>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:767>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:765>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:767>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:762>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:762>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:767>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:767>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:767>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:767>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:769>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:767>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:771>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:762>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:762>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:888>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:888>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:888>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:888>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:888>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:765>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:888>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:888>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:765>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:765>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:765>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:765>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:765>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:765>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:765>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:765>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:765>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:765>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:765>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:765>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:765>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:762>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:762>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:762>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:767>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:762>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:762>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:762>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:767>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:767>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:773>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:773>)
~~~python
def _reset_dofs(self, env_ids):
        """Resets DOF position and velocities of selected environmments
        Positions are randomly selected within 0.5:1.5 x default positions.
        Velocities are set to zero.

        Args:
            env_ids (List[int]): Environemnt ids
        """
        self.dof_pos[env_ids] = self.default_dof_pos[env_ids, :]
        self.dof_vel[env_ids] = 0.0

        env_ids_int32 = env_ids.to(dtype=torch.int32)
        self.gym.set_dof_state_tensor_indexed(
            self.sim,
            gymtorch.unwrap_tensor(self.dof_state),
            gymtorch.unwrap_tensor(env_ids_int32),
            len(env_ids_int32),
        )
~~~

</details>


<details markdown="1"><summary>_reset_root_states / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:784>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:784>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:784>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:784>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:786>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:784>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:786>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:781>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:781>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:786>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:786>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:786>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:786>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:788>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:786>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:790>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:781>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:781>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:907>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:907>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:907>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:907>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:907>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:784>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:907>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:907>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:784>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:784>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:784>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:784>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:784>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:784>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:784>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:784>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:784>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:784>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:784>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:784>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:784>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:781>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:781>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:781>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:786>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:781>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:781>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:781>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:786>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:786>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:792>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:792>)
~~~python
def _reset_root_states(self, env_ids):
        """Resets ROOT states position and velocities of selected environmments
            Sets base position based on the curriculum
            Selects randomized base velocities within -0.5:0.5 [m/s, rad/s]
        Args:
            env_ids (List[int]): Environemnt ids
        """
        # base position
        if self.custom_origins:
            self.root_states[env_ids] = self.base_init_state
            self.root_states[env_ids, :3] += self.env_origins[env_ids]
            self.root_states[env_ids, :2] += torch_rand_float(
                -1.0, 1.0, (len(env_ids), 2), device=self.device
            )  # xy position within 1m of the center
        else:
            self.root_states[env_ids] = self.base_init_state
            self.root_states[env_ids, :3] += self.env_origins[env_ids]
        # base velocities
        self.root_states[env_ids, 7:13] = torch_rand_float(
            -0.5, 0.5, (len(env_ids), 6), device=self.device
        )  # [7:10]: lin vel, [10:13]: ang vel
        env_ids_int32 = env_ids.to(dtype=torch.int32)
        self.gym.set_actor_root_state_tensor_indexed(
            self.sim,
            gymtorch.unwrap_tensor(self.root_states),
            gymtorch.unwrap_tensor(env_ids_int32),
            len(env_ids_int32),
        )
~~~

</details>


<details markdown="1"><summary>_update_terrain_curriculum / F01,F02,F03,F04,F05,F06,F07,F10,F11,F19,F20,F21,F22,F23,F24,F25,F26,F27,F29,F30,F31,F32,F33,F34,F35,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:848>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:848>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:848>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:848>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:850>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:848>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:850>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:850>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:850>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:971>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:971>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:971>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:971>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:971>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:848>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:971>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:971>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:848>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:848>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:848>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:848>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:848>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:848>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:848>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:848>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:856>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:856>)
~~~python
def _update_terrain_curriculum(self, env_ids):
        """Implements the game-inspired curriculum.

        Args:
            env_ids (List[int]): ids of environments being reset
        """
        # Implement Terrain curriculum
        if not self.init_done:
            # don't change on initial reset
            return
        distance = torch.norm(
            self.root_states[env_ids, :2] - self.env_origins[env_ids, :2], dim=1
        )
        # robots that walked far enough progress to harder terains
        move_up = distance > self.terrain.env_length / 4  #原本是/2
        # robots that walked less than half of their required distance go to simpler terrains
        move_down = (
            self.episode_sums["tracking_lin_vel"][env_ids] / self.max_episode_length_s
            < (self.reward_scales["tracking_lin_vel"] / self.dt) * 0.4
        ) * ~move_up
        self.terrain_levels[env_ids] += 1 * move_up - 1 * move_down
        mask = self.terrain_levels[env_ids] >= self.max_terrain_level
        self.success_ids = env_ids[mask]
        mask = self.terrain_levels[env_ids] < 0
        self.fail_ids = env_ids[mask]
        # Robots that solve the last level are sent to a random one
        self.terrain_levels[env_ids] = torch.where(
            self.terrain_levels[env_ids] >= self.max_terrain_level,
            torch.randint_like(self.terrain_levels[env_ids], self.max_terrain_level),
            torch.clip(self.terrain_levels[env_ids], 0),
        )  # (the minumum level is zero)
        self.env_origins[env_ids] = self.terrain_origins[
            self.terrain_levels[env_ids], self.terrain_types[env_ids]
        ]
        if self.cfg.commands.curriculum:
            self.command_ranges["lin_vel_x"][self.fail_ids, 0] = torch.clip(
                self.command_ranges["lin_vel_x"][self.fail_ids, 0] + 0.25,
                -self.cfg.commands.basic_max_curriculum,
                -1,
            )
            self.command_ranges["lin_vel_x"][self.fail_ids, 1] = torch.clip(
                self.command_ranges["lin_vel_x"][self.fail_ids, 1] - 0.25,
                1,
                self.cfg.commands.basic_max_curriculum,
            )
~~~

</details>


<details markdown="1"><summary>update_command_curriculum / F01,F02,F03,F04,F05,F06,F07,F10,F11,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:894>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:894>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:894>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:894>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:896>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:894>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:896>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:896>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:896>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1017>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1017>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1017>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1017>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1017>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:894>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1017>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1017>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:894>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:894>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:894>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:894>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:894>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:894>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:894>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:894>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:894>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:894>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:894>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:894>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:894>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:902>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:902>)
~~~python
def update_command_curriculum(self, env_ids):
        """Implements a curriculum of increasing commands

        Args:
            env_ids (List[int]): ids of environments being reset
        """
        # If the tracking reward is above 80% of the maximum, increase the range of commands
        if self.cfg.terrain.curriculum and len(self.success_ids) != 0:
            # self.basic_terrain_idx = torch.cat((self.stair_up_idx, self.discrete_idx))
            # self.advanced_terrain_idx
            mask = (
                self.episode_sums["tracking_lin_vel"][self.success_ids]
                / self.max_episode_length
                > self.cfg.commands.curriculum_threshold
                * self.reward_scales["tracking_lin_vel"]
            )
            success_ids = self.success_ids[mask]
            basic_ids = torch.any(
                success_ids.unsqueeze(1) == self.basic_terrain_idx.unsqueeze(0), dim=1
            )
            basic_ids = success_ids[basic_ids]
            self.command_ranges["lin_vel_x"][success_ids, 0] -= 0.05
            self.command_ranges["lin_vel_x"][success_ids, 1] += 0.05
            self.command_ranges["lin_vel_x"][basic_ids, 0] -= 0.45
            self.command_ranges["lin_vel_x"][basic_ids, 1] += 0.45

            self.command_ranges["lin_vel_x"][self.basic_terrain_idx, :] = torch.clip(
                self.command_ranges["lin_vel_x"][self.basic_terrain_idx, :],
                -self.cfg.commands.basic_max_curriculum,
                self.cfg.commands.basic_max_curriculum,
            )
            self.command_ranges["lin_vel_x"][self.advanced_terrain_idx, :] = torch.clip(
                self.command_ranges["lin_vel_x"][self.advanced_terrain_idx, :],
                -self.cfg.commands.advanced_max_curriculum,
                self.cfg.commands.advanced_max_curriculum,
            )
        if self.cfg.terrain.curriculum == False:
            if (
                torch.mean(self.episode_sums["tracking_lin_vel"][env_ids])
                / self.max_episode_length
                > self.cfg.commands.curriculum_threshold
                * self.reward_scales["tracking_lin_vel"]
                and torch.mean(self.episode_sums["tracking_ang_vel"][env_ids])
                / self.max_episode_length
                > self.cfg.commands.curriculum_threshold
                * self.reward_scales["tracking_ang_vel"]
                * 0.8
            ):
                self.command_ranges["lin_vel_x"][:, 0] = torch.clip(
                    self.command_ranges["lin_vel_x"][:, 0] - 0.1,
                    -self.cfg.commands.basic_max_curriculum,
                    0.0,
                )
                self.command_ranges["lin_vel_x"][:, 1] = torch.clip(
                    self.command_ranges["lin_vel_x"][:, 1] + 0.1,
                    0.0,
                    self.cfg.commands.basic_max_curriculum,
                )
~~~

</details>


<details markdown="1"><summary>_prepare_reward_function / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1265>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1265>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1265>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1265>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1305>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1265>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1305>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1315>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1315>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1305>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1305>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1393>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1393>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1396>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1393>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1398>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1315>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1315>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1390>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1390>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1390>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1390>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1390>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1265>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1390>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1390>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1265>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1265>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1265>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1265>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1265>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1265>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1265>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1265>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1265>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1265>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1265>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1265>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1265>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1315>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1315>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1315>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1393>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1315>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1315>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1315>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1393>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1393>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1278>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1278>)
~~~python
def _prepare_reward_function(self):
        """Prepares a list of reward functions, whcih will be called to compute the total reward.
        Looks for self._reward_<REWARD_NAME>, where <REWARD_NAME> are names of all non zero reward scales in the cfg.
        """
        # remove zero scales + multiply non-zero ones by dt
        for key in list(self.reward_scales.keys()):
            scale = self.reward_scales[key]
            if scale == 0:
                self.reward_scales.pop(key)
            else:
                self.reward_scales[key] *= self.dt
        # prepare list of functions
        self.reward_functions = []
        self.reward_names = []
        for name, scale in self.reward_scales.items():
            if name == "termination":
                continue
            self.reward_names.append(name)
            name = "_reward_" + name
            self.reward_functions.append(getattr(self, name))

        # reward episode sums
        self.episode_sums = {
            name: torch.zeros(
                self.num_envs,
                dtype=torch.float,
                device=self.device,
                requires_grad=False,
            )
            for name in self.reward_scales.keys()
        }
~~~

</details>


<details markdown="1"><summary>_reward_lin_vel_z / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1719>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1719>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1719>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1719>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1759>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1719>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1759>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1806>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1806>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1759>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1759>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1897>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1897>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1900>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1897>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1902>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1806>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1806>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1844>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1844>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1844>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1844>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1844>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1719>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1844>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1844>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1719>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1719>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1719>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1719>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1719>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1719>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1719>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1719>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1719>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1719>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1719>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1719>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1719>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1806>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1806>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1806>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1897>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1806>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1806>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1806>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1897>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1897>)
~~~python
def _reward_lin_vel_z(self):
        # Penalize z axis base linear velocity
        return torch.square(self.base_lin_vel[:, 2])
~~~

</details>


<details markdown="1"><summary>_reward_ang_vel_xy / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1723>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1723>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1723>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1723>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1763>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1723>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1763>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1810>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1810>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1763>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1763>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1901>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1901>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1904>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1901>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1906>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1810>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1810>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1848>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1848>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1848>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1848>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1848>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1723>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1848>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1848>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1723>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1723>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1723>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1723>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1723>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1723>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1723>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1723>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1723>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1723>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1723>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1723>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1723>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1810>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1810>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1810>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1901>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1810>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1810>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1810>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1901>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1901>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1796>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1796>)
~~~python
def _reward_ang_vel_xy(self):
        # Penalize xy axes base angular velocity
        return torch.sum(torch.square(self.base_ang_vel[:, :2]), dim=1)
~~~

</details>


<details markdown="1"><summary>_reward_orientation / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1727>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1727>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1727>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1727>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1767>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1727>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1767>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1814>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1814>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1767>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1767>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1905>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1905>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1908>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1905>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1910>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1814>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1814>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1852>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1852>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1852>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1852>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1852>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1727>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1852>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1852>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1727>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1727>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1727>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1727>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1727>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1727>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1727>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1727>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1727>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1727>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1727>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1727>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1727>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1814>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1814>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1814>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1905>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1814>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1814>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1814>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1905>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1905>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1799>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1799>)
~~~python
def _reward_orientation(self):
        # Penalize non flat base orientation
        return torch.sum(torch.square(self.projected_gravity[:, :2]), dim=1)
~~~

</details>


<details markdown="1"><summary>_reward_base_height / F01,F02,F03,F04,F05,F06,F07,F10,F11,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1731>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1731>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1731>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1731>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1771>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1731>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1771>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1771>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1771>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1856>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1856>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1856>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1856>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1856>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1731>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1856>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1856>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1731>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1731>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1731>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1731>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1731>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1731>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1731>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1731>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1731>)
~~~python
def _reward_base_height(self):
        # Penalize base height away from target
        # print(self.commands[0, 2], self.base_height[0])
        if self.reward_scales["base_height"] < 0:
            return torch.abs(self.base_height - self.commands[:, 2])
        else:
            base_height_error = torch.square(self.base_height - self.commands[:, 2])
            return torch.exp(-base_height_error / 0.001)
~~~

</details>


<details markdown="1"><summary>_reward_base_height_enhance / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1740>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1740>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1740>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1740>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1780>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1740>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1780>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1827>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1827>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1780>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1780>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1918>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1918>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1921>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1918>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1923>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1827>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1827>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1865>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1865>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1865>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1865>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1865>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1740>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1865>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1865>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1740>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1740>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1740>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1740>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1740>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1740>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1740>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1740>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1740>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1740>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1740>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1740>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1740>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1827>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1827>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1827>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1918>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1827>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1827>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1827>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1918>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1918>)
~~~python
def _reward_base_height_enhance(self):
        base_height_error = torch.square(self.base_height - self.commands[:, 2])
        return torch.exp(-base_height_error / 0.001 / 10) - 1
~~~

</details>


<details markdown="1"><summary>_reward_torques / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1744>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1744>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1744>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1744>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1784>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1744>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1784>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1831>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1831>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1784>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1784>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1922>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1922>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1925>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1922>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1927>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1831>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1831>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1869>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1869>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1869>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1869>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1869>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1744>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1869>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1869>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1744>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1744>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1744>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1744>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1744>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1744>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1744>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1744>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1744>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1744>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1744>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1744>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1744>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1831>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1831>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1831>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1922>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1831>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1831>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1831>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1922>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1922>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1803>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1803>)
~~~python
def _reward_torques(self):
        # Penalize torques
        return torch.sum(torch.square(self.torques), dim=1)
~~~

</details>


<details markdown="1"><summary>_reward_power / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1748>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1748>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1748>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1748>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1788>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1748>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1788>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1835>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1835>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1788>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1788>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1926>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1926>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1929>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1926>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1931>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1835>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1835>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1873>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1873>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1873>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1873>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1873>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1748>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1873>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1873>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1748>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1748>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1748>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1748>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1748>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1748>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1748>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1748>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1748>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1748>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1748>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1748>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1748>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1835>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1835>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1835>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1926>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1835>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1835>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1835>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1926>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1926>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1807>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1807>)
~~~python
def _reward_power(self):
        # Penalize torques
        return torch.sum(torch.abs(self.torques * self.dof_vel), dim=1)
~~~

</details>


<details markdown="1"><summary>_reward_dof_vel / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1752>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1752>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1752>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1752>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1792>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1752>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1792>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1839>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1839>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1792>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1792>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1930>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1930>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1933>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1930>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1935>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1839>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1839>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1877>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1877>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1877>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1877>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1877>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1752>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1877>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1877>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1752>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1752>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1752>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1752>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1752>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1752>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1752>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1752>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1752>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1752>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1752>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1752>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1752>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1839>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1839>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1839>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1930>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1839>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1839>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1839>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1930>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1930>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1811>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1811>)
~~~python
def _reward_dof_vel(self):
        # Penalize dof velocities
        return torch.sum(torch.square(self.dof_vel[:, :2]), dim=1) + torch.sum(
            torch.square(self.dof_vel[:, 3:5]), dim=1
        )
~~~

</details>


<details markdown="1"><summary>_reward_dof_acc / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1758>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1758>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1758>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1758>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1798>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1758>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1798>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1845>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1845>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1798>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1798>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1936>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1936>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1939>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1936>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1941>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1845>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1845>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1883>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1883>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1883>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1883>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1883>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1758>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1883>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1883>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1758>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1758>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1758>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1758>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1758>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1758>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1758>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1758>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1758>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1758>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1758>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1758>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1758>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1845>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1845>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1845>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1936>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1845>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1845>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1845>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1936>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1936>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1817>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1817>)
~~~python
def _reward_dof_acc(self):
        # Penalize dof accelerations
        return torch.sum(torch.square(self.dof_acc), dim=1)
~~~

</details>


<details markdown="1"><summary>_reward_action_rate / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1762>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1762>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1762>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1762>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1802>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1762>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1802>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1849>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1849>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1802>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1802>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1940>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1940>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1943>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1940>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1945>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1849>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1849>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1887>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1887>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1887>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1887>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1887>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1762>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1887>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1887>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1762>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1762>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1762>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1762>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1762>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1762>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1762>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1762>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1762>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1762>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1762>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1762>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1762>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1849>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1849>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1849>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1940>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1849>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1849>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1849>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1940>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1940>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1821>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1821>)
~~~python
def _reward_action_rate(self):
        # Penalize changes in actions
        return torch.sum(torch.square(self.last_actions[:, :, 0] - self.actions), dim=1)
~~~

</details>


<details markdown="1"><summary>_reward_action_smooth / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1766>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1766>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1766>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1766>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1806>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1766>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1806>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1853>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1853>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1806>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1806>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1944>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1944>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1947>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1944>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1949>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1853>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1853>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1891>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1891>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1891>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1891>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1891>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1766>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1891>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1891>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1766>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1766>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1766>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1766>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1766>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1766>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1766>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1766>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1766>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1766>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1766>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1766>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1766>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1853>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1853>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1853>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1944>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1853>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1853>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1853>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1944>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1944>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1825>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1825>)
~~~python
def _reward_action_smooth(self):
        # Penalize changes in actions
        return torch.sum(
            torch.square(
                self.actions[:, :2]
                - 2 * self.last_actions[:, :2, 0]
                + self.last_actions[:, :2, 1]
            ),
            dim=1,
        ) + torch.sum(
            torch.square(
                self.actions[:, 3:5]
                - 2 * self.last_actions[:, 3:5, 0]
                + self.last_actions[:, 3:5, 1]
            ),
            dim=1,
        )
~~~

</details>


<details markdown="1"><summary>_reward_collision / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1784>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1784>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1784>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1784>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1824>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1784>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1824>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1871>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1871>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1824>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1824>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1962>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1962>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1975>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1962>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1967>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1871>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1871>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1909>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1909>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1909>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1909>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1909>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1784>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1909>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1909>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1784>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1784>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1784>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1784>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1784>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1784>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1784>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1784>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1784>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1784>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1784>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1784>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1784>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1871>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1871>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1871>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1962>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1871>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1871>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1871>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1962>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1962>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1843>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1843>)
~~~python
def _reward_collision(self):
        # Penalize collisions on selected bodies
        return torch.sum(
            1.0
            * (
                torch.norm(
                    self.contact_forces[:, self.penalised_contact_indices, :], dim=-1
                )
                > 0.1
            ),
            dim=1,
        )
~~~

</details>


<details markdown="1"><summary>_reward_termination / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1797>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1797>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1797>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1797>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1837>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1797>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1837>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1884>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1884>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1837>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1837>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1975>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1975>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1988>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1975>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1980>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1884>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1884>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1922>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1922>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1922>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1922>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1922>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1797>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1922>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1922>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1797>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1797>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1797>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1797>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1797>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1797>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1797>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1797>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1797>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1797>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1797>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1797>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1797>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1884>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1884>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1884>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1975>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1884>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1884>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1884>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1975>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1975>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1856>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1856>)
~~~python
def _reward_termination(self):
        # Terminal reward / penalty
        return self.reset_buf * ~self.time_out_buf
~~~

</details>


<details markdown="1"><summary>_reward_dof_pos_limits / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1801>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1801>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1801>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1801>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1841>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1801>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1841>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1888>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1888>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1841>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1841>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1979>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1979>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1992>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1979>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1984>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1888>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1888>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1926>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1926>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1926>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1926>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1926>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1801>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1926>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1926>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1801>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1801>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1801>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1801>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1801>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1801>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1801>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1801>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1801>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1801>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1801>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1801>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1801>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1888>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1888>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1888>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1979>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1888>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1888>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1888>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1979>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1979>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1860>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1860>)
~~~python
def _reward_dof_pos_limits(self):
        # Penalize dof positions too close to the limit
        out_of_limits = -(self.dof_pos[:, :2] - self.dof_pos_limits[:2, 0]).clip(
            max=0.0
        )  # lower limit
        out_of_limits += (self.dof_pos[:, :2] - self.dof_pos_limits[:2, 1]).clip(
            min=0.0
        )
        out_of_limits += -(self.dof_pos[:, 3:5] - self.dof_pos_limits[3:5, 0]).clip(
            max=0.0
        )  # lower limit
        out_of_limits += (self.dof_pos[:, 3:5] - self.dof_pos_limits[3:5, 1]).clip(
            min=0.0
        )
        return torch.sum(out_of_limits, dim=1)
~~~

</details>


<details markdown="1"><summary>_reward_dof_vel_limits / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1817>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1817>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1817>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1817>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1857>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1817>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1857>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1904>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1904>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1857>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1857>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1995>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1995>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2008>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1995>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2000>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1904>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1904>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1942>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1942>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1942>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1942>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1942>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1817>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1942>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1942>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1817>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1817>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1817>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1817>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1817>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1817>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1817>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1817>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1817>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1817>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1817>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1817>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1817>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1904>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1904>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1904>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1995>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1904>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1904>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1904>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1995>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1995>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1876>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1876>)
~~~python
def _reward_dof_vel_limits(self):
        # Penalize dof velocities too close to the limit
        # clip to max error = 1 rad/s per joint to avoid huge penalties
        return torch.sum(
            (
                torch.abs(self.dof_vel)
                - self.dof_vel_limits * self.cfg.rewards.soft_dof_vel_limit
            ).clip(min=0.0, max=1.0),
            dim=1,
        )
~~~

</details>


<details markdown="1"><summary>_reward_torque_limits / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F15,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1828>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1828>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1828>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1828>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1868>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1828>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1868>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1915>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1915>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1868>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1868>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2006>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2006>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2006>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1915>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1915>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1953>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1953>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1953>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1953>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1953>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1828>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1953>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1953>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1828>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1828>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1828>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1828>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1828>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1828>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1828>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1828>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1828>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1828>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1828>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1828>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1828>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1915>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1915>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1915>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2006>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1915>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1915>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1915>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2006>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2006>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1887>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1887>)
~~~python
def _reward_torque_limits(self):
        # penalize torques too close to the limit
        return torch.sum(
            (
                torch.abs(self.torques)
                - self.torque_limits * self.cfg.rewards.soft_torque_limit
            ).clip(min=0.0),
            dim=1,
        )
~~~

</details>


<details markdown="1"><summary>_reward_tracking_lin_vel / F01,F02,F03,F04,F05,F06,F07,F10,F11,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1838>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1838>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1838>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1838>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1878>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1838>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1878>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1878>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1878>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1963>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1963>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1963>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1963>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1963>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1838>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1963>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1963>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1838>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1838>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1838>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1838>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1838>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1838>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1838>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1838>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1838>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1838>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1838>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1838>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1838>)
~~~python
def _reward_tracking_lin_vel(self):
        # Tracking of linear velocity commands (x axes)
        lin_vel_error = torch.square(self.commands[:, 0] - self.base_lin_vel[:, 0])
        return torch.exp(-lin_vel_error / self.cfg.rewards.tracking_sigma)
~~~

</details>


<details markdown="1"><summary>_reward_tracking_lin_vel_enhance / F01,F02,F03,F04,F05,F06,F07,F10,F11,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1843>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1843>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1843>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1843>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1883>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1843>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1883>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1883>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1883>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1968>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1968>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1968>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1968>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1968>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1843>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1968>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1968>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1843>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1843>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1843>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1843>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1843>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1843>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1843>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1843>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1843>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1843>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1843>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1843>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1843>)
~~~python
def _reward_tracking_lin_vel_enhance(self):
        # Tracking of linear velocity commands (x axes)
        lin_vel_error = torch.square(self.commands[:, 0] - self.base_lin_vel[:, 0])
        return torch.exp(-lin_vel_error / self.cfg.rewards.tracking_sigma / 10) - 1
~~~

</details>


<details markdown="1"><summary>_reward_tracking_ang_vel / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1848>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1848>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1848>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1848>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1888>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1848>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1888>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1935>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1935>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1888>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1888>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2026>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2026>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2040>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2026>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2027>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1935>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1935>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1973>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1973>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1973>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1973>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1973>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1848>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1973>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1973>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1848>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1848>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1848>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1848>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1848>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1848>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1848>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1848>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1848>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1848>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1848>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1848>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1848>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1935>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1935>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1935>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2026>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1935>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1935>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1935>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2026>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2026>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1911>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1911>)
~~~python
def _reward_tracking_ang_vel(self):
        # Tracking of angular velocity commands (yaw)
        ang_vel_error = torch.square(self.commands[:, 1] - self.base_ang_vel[:, 2])
        return torch.exp(-ang_vel_error / self.cfg.rewards.tracking_sigma)
~~~

</details>


<details markdown="1"><summary>_reward_tracking_ang_vel_enhance / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1853>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1853>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1853>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1853>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1893>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1853>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1893>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1940>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1940>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1893>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1893>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2031>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2031>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2045>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2031>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2032>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1940>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1940>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1978>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1978>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1978>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1978>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1978>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1853>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1978>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1978>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1853>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1853>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1853>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1853>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1853>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1853>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1853>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1853>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1853>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1853>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1853>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1853>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1853>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1940>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1940>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1940>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2031>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1940>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1940>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1940>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2031>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2031>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1916>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1916>)
~~~python
def _reward_tracking_ang_vel_enhance(self):
        # Tracking of angular velocity commands (x axes)
        ang_vel_error = torch.square(self.commands[:, 1] - self.base_ang_vel[:, 2])
        return torch.exp(-ang_vel_error / self.cfg.rewards.tracking_sigma / 10) - 1
~~~

</details>


<details markdown="1"><summary>_reward_theta0_equ_0 / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1858>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1858>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1858>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1858>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1898>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1858>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1898>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1945>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1945>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1898>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1898>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2036>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2036>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2050>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2036>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2037>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1945>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1945>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1983>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1983>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1983>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1983>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1983>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1858>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1983>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1983>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1858>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1858>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1858>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1858>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1858>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1858>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1858>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1858>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1858>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1858>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1858>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1858>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1858>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1945>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1945>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1945>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2036>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1945>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1945>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1945>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2036>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2036>)
~~~python
def _reward_theta0_equ_0(self):
        left_theta0_error = torch.square(self.theta0[:, 0])
        right_theta0_error = torch.square(self.theta0[:, 1])

        return torch.exp(-(left_theta0_error + right_theta0_error) / self.cfg.rewards.tracking_sigma)
~~~

</details>


<details markdown="1"><summary>_reward_tracking_lin_vel_pbrs / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1864>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1864>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1864>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1864>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1904>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1864>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1904>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1951>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1951>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1904>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1904>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2053>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2053>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2067>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2053>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2054>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1951>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1951>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1989>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1989>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1989>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1989>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1989>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1864>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1989>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1989>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1864>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1864>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1864>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1864>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1864>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1864>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1864>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1864>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1864>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1864>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1864>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1864>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1864>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1951>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1951>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1951>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2053>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1951>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1951>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1951>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2053>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2053>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1921>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1921>)
~~~python
def _reward_tracking_lin_vel_pbrs(self):
        delta_phi = ~self.reset_buf * (
            self._reward_tracking_lin_vel() - self.rwd_linVelTrackPrev
        )
        # return lin_vel_error
        return delta_phi
~~~

</details>


<details markdown="1"><summary>_reward_tracking_ang_vel_pbrs / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1871>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1871>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1871>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1871>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1911>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1871>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1911>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1958>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1958>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1911>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1911>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2060>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2060>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2074>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2060>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2061>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1958>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1958>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:1996>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:1996>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:1996>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:1996>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:1996>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1871>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:1996>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:1996>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1871>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1871>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1871>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1871>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1871>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1871>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1871>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1871>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1871>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1871>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1871>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1871>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1871>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1958>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1958>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1958>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2060>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1958>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1958>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1958>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2060>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2060>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1928>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1928>)
~~~python
def _reward_tracking_ang_vel_pbrs(self):
        delta_phi = ~self.reset_buf * (
            self._reward_tracking_ang_vel() - self.rwd_angVelTrackPrev
        )
        # return ang_vel_error
        return delta_phi
~~~

</details>


<details markdown="1"><summary>_reward_stumble / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1878>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1878>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1878>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1878>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1918>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1878>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1918>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1965>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1965>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1918>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1918>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2067>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2067>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2081>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2067>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2068>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1965>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1965>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:2003>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:2003>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:2003>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:2003>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:2003>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1878>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:2003>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:2003>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1878>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1878>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1878>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1878>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1878>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1878>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1878>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1878>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1878>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1878>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1878>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1878>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1878>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1965>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1965>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1965>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2067>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1965>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1965>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1965>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2067>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2067>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1935>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1935>)
~~~python
def _reward_stumble(self):
        # Penalize feet hitting vertical surfaces
        return torch.any(
            torch.norm(self.contact_forces[:, self.feet_indices, :2], dim=2)
            > 5 * torch.abs(self.contact_forces[:, self.feet_indices, 2]),
            dim=1,
        )
~~~

</details>


<details markdown="1"><summary>_reward_stand_still / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1886>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1886>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1886>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1886>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1926>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1886>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1926>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1973>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1973>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1926>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1926>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2075>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2075>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2089>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2075>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2076>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1973>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1973>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:2011>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:2011>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:2011>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:2011>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:2011>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1886>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:2011>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:2011>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1886>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1886>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1886>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1886>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1886>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1886>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1886>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1886>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1886>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1886>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1886>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1886>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1886>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1973>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1973>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1973>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2075>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1973>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1973>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1973>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2075>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2075>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1943>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1943>)
~~~python
def _reward_stand_still(self):
        # Penalize motion at zero commands
        return torch.sum(torch.abs(self.dof_pos - self.default_dof_pos), dim=1) * (
            torch.norm(self.commands[:, :2], dim=1) < 0.1
        )
~~~

</details>


<details markdown="1"><summary>_reward_nominal_state / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1892>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1892>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1892>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1892>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1932>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1892>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1932>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1979>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1979>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1932>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1932>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2081>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2081>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2095>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2081>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2082>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1979>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1979>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:2017>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:2017>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:2017>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:2017>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:2017>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1892>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:2017>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:2017>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1892>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1892>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1892>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1892>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1892>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1892>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1892>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1892>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1892>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1892>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1892>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1892>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1892>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1979>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1979>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1979>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2081>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1979>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1979>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1979>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2081>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2081>)
~~~python
def _reward_nominal_state(self):
        # return torch.square(self.theta0[:, 0] - self.theta0[:, 1])
        if self.reward_scales["nominal_state"] < 0:
            return torch.square(self.theta0[:, 0] - self.theta0[:, 1])
        else:
            ang_diff = torch.square(self.theta0[:, 0] - self.theta0[:, 1])
            return torch.exp(-ang_diff / 0.1)
~~~

</details>


<details markdown="1"><summary>_reward_feet_contact_forces / F01,F02,F03,F04,F05,F06,F07,F08,F09,F10,F11,F12,F13,F14,F15,F16,F17,F18,F19,F20,F21,F22,F23,F24,F25,F26,F27,F28,F29,F30,F31,F32,F33,F34,F35,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48,F49,F50</summary>

适用：[F01](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/envs/base/legged_robot.py:1900>) · [F02](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+/legged_robot.py:1900>) · [F03](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz++/legged_robot.py:1900>) · [F04](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++/legged_robot.py:1900>) · [F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1940>) · [F06](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++继续训练但是调小范围了/legged_robot.py:1900>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1940>) · [F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1987>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1987>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1940>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1940>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2089>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2089>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2103>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2089>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2090>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1987>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1987>) · [F19](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=101.00.2_randization=normal/legged_robot.py:2025>) · [F20](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=201.00.2_randization=normal/legged_robot.py:2025>) · [F21](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new/legged_robot.py:2025>) · [F22](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=51.50.25_randization=normal_new_suijidixing/legged_robot.py:2025>) · [F23](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=3.0pd=61.00.2_randization=normal/legged_robot.py:2025>) · [F24](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=4.0pd=101.00.2_randization=normal/legged_robot.py:1900>) · [F25](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=hard/legged_robot.py:2025>) · [F26](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=mid/legged_robot.py:2025>) · [F27](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/linx_scales=5.0pd=151.00.2_randization=normal/legged_robot.py:1900>) · [F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:1900>) · [F29](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai/legged_robot.py:1900>) · [F30](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajia/legged_robot.py:1900>) · [F31](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia/legged_robot.py:1900>) · [F32](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajia/legged_robot.py:1900>) · [F33](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajia/legged_robot.py:1900>) · [F34](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajia/legged_robot.py:1900>) · [F35](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground_yuntai_height_jiajiajiajiajiajia_angz_jiajiajiajiajiajiajiajiajiajiajiajia/legged_robot.py:1900>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1900>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1900>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1900>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1900>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1987>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1987>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1987>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2089>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1987>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1987>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1987>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2089>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2089>) · [F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1961>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1961>)
~~~python
def _reward_feet_contact_forces(self):
        # penalize high contact forces
        return torch.sum(
            (
                torch.norm(self.contact_forces[:, self.feet_indices, :], dim=-1)
                - self.cfg.rewards.max_contact_force
            ).clip(min=0.0),
            dim=1,
        )
~~~

</details>


<details markdown="1"><summary>_reward_wheel_vel_abs_match / F05,F07,F10,F11</summary>

适用：[F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1951>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1951>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1951>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1951>)
~~~python
def _reward_wheel_vel_abs_match(self):
        # For in-place yaw motion, the two wheel speeds should be opposite in sign
        # but close in magnitude.
        left_wheel_vel = torch.abs(self.dof_vel[:, self.left_wheel_idx])
        right_wheel_vel = torch.abs(self.dof_vel[:, self.right_wheel_idx])
        vel_error = (left_wheel_vel - right_wheel_vel) / self.wheel_vel_limit_reward
        return torch.exp(-torch.square(vel_error) / 0.25)
~~~

</details>


<details markdown="1"><summary>_reward_wheel_torque_abs_match / F05,F07,F10,F11</summary>

适用：[F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1959>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1959>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1959>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1959>)
~~~python
def _reward_wheel_torque_abs_match(self):
        # Use abs torque here as well, since spinning in place usually needs
        # symmetric magnitude instead of identical sign.
        wheel_torques = torch.abs(self.torques[:, self.wheel_indices])
        torque_error = (
            wheel_torques[:, 0] - wheel_torques[:, 1]
        ) / self.wheel_torque_mean_limit_reward

        return torch.exp(-torch.square(torque_error) / 0.25)
~~~

</details>


<details markdown="1"><summary>_reward_wheel_torque_smooth / F05,F07,F10,F11</summary>

适用：[F05](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_angz+++_zengjiajiangli/legged_robot.py:1969>) · [F07](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+/legged_robot.py:1969>) · [F10](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2/legged_robot.py:1969>) · [F11](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_40_5.0_0.2_recover/legged_robot.py:1969>)
~~~python
def _reward_wheel_torque_smooth(self):
        wheel_torque_delta = (
            self.torques[:, self.wheel_indices] - self.last_wheel_torques_reward
        ) / self.wheel_torque_limits_reward.unsqueeze(0)
        smooth_error = torch.sum(torch.square(wheel_torque_delta), dim=1)

        smooth_reward = torch.exp(-smooth_error / 0.25)
        return torch.where(
            self.episode_length_buf > 1,
            smooth_reward,
            torch.ones_like(smooth_reward),
        )
~~~

</details>


<details markdown="1"><summary>_update_terrain_curriculum / F08,F09,F12,F13,F14,F15,F16,F17,F18,F40,F41,F42,F43,F44,F45,F46,F47,F48</summary>

适用：[F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:845>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:845>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:919>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:919>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:921>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:919>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:923>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:845>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:845>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:845>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:845>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:845>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:919>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:845>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:845>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:845>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:919>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:919>)
~~~python
def _update_terrain_curriculum(self, env_ids):
        """Implements the game-inspired curriculum.

        Args:
            env_ids (List[int]): ids of environments being reset
        """
        # Implement Terrain curriculum
        if not self.init_done:
            # don't change on initial reset
            return
        distance = torch.norm(
            self.root_states[env_ids, :2] - self.env_origins[env_ids, :2], dim=1
        )
        # robots that walked far enough progress to harder terains
        move_up = distance > self.terrain.env_length / 2  #原本是/2
        # robots that walked less than half of their required distance go to simpler terrains
        move_down = (
            self.episode_sums["tracking_lin_vel"][env_ids] / self.max_episode_length_s
            < (self.reward_scales["tracking_lin_vel"] / self.dt) * 0.4
        ) * ~move_up
        self.terrain_levels[env_ids] += 1 * move_up - 1 * move_down
        mask = self.terrain_levels[env_ids] >= self.max_terrain_level
        self.success_ids = env_ids[mask]
        mask = self.terrain_levels[env_ids] < 0
        self.fail_ids = env_ids[mask]
        # Robots that solve the last level are sent to a random one
        self.terrain_levels[env_ids] = torch.where(
            self.terrain_levels[env_ids] >= self.max_terrain_level,
            torch.randint_like(self.terrain_levels[env_ids], self.max_terrain_level),
            torch.clip(self.terrain_levels[env_ids], 0),
        )  # (the minumum level is zero)
        self.env_origins[env_ids] = self.terrain_origins[
            self.terrain_levels[env_ids], self.terrain_types[env_ids]
        ]
        if self.cfg.commands.curriculum:
            self._shrink_command_range(
                "lin_vel_x",
                self.fail_ids,
                step=0.25,
                min_abs=1.0,
                max_abs=self.cfg.commands.basic_max_curriculum,
            )
            self._shrink_command_range(
                "ang_vel_yaw",
                self.fail_ids,
                step=0.5,
                min_abs=1.0,
                max_abs=self.cfg.commands.basic_max_ang_vel_curriculum,
            )
~~~

</details>


<details markdown="1"><summary>update_command_curriculum / F08,F09,F12,F13,F14,F15,F16,F17,F18,F40,F41,F42,F43,F44,F45,F46,F47,F48</summary>

适用：[F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:895>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:895>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:969>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:969>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:971>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:969>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:973>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:895>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:895>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:895>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:895>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:895>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:969>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:895>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:895>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:895>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:969>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:969>)
~~~python
def update_command_curriculum(self, env_ids):
        """Implements a curriculum of increasing commands

        Args:
            env_ids (List[int]): ids of environments being reset
        """
        # If the tracking rewards are high enough, increase the range of commands.
        if self.cfg.terrain.curriculum and len(self.success_ids) != 0:
            mask = (
                self.episode_sums["tracking_lin_vel"][self.success_ids]
                / self.max_episode_length
                > self.cfg.commands.curriculum_threshold
                * self.reward_scales["tracking_lin_vel"]
            ) & (
                self.episode_sums["tracking_ang_vel"][self.success_ids]
                / self.max_episode_length
                > self.cfg.commands.curriculum_threshold
                * self.reward_scales["tracking_ang_vel"]
            )
            success_ids = self.success_ids[mask]
            basic_ids = torch.any(
                success_ids.unsqueeze(1) == self.basic_terrain_idx.unsqueeze(0), dim=1
            )
            basic_ids = success_ids[basic_ids]
            self._grow_command_range(
                "lin_vel_x", success_ids, basic_ids, advanced_step=0.05, basic_extra=0.45
            )
            self._grow_command_range(
                "ang_vel_yaw",
                success_ids,
                basic_ids,
                advanced_step=0.1,
                basic_extra=0.4,
            )
            self._clip_command_range(
                "lin_vel_x",
                self.cfg.commands.basic_max_curriculum,
                self.cfg.commands.advanced_max_curriculum,
            )
            self._clip_command_range(
                "ang_vel_yaw",
                self.cfg.commands.basic_max_ang_vel_curriculum,
                self.cfg.commands.advanced_max_ang_vel_curriculum,
            )
        if self.cfg.terrain.curriculum == False:
            if (
                torch.mean(self.episode_sums["tracking_lin_vel"][env_ids])
                / self.max_episode_length
                > self.cfg.commands.curriculum_threshold
                * self.reward_scales["tracking_lin_vel"]
                and torch.mean(self.episode_sums["tracking_ang_vel"][env_ids])
                / self.max_episode_length
                > self.cfg.commands.curriculum_threshold
                * self.reward_scales["tracking_ang_vel"]
                * 0.8
            ):
                self.command_ranges["lin_vel_x"][:, 0] -= 0.1
                self.command_ranges["lin_vel_x"][:, 1] += 0.1
                self.command_ranges["ang_vel_yaw"][:, 0] -= 0.2
                self.command_ranges["ang_vel_yaw"][:, 1] += 0.2
                self.command_ranges["lin_vel_x"][:, :] = torch.clip(
                    self.command_ranges["lin_vel_x"][:, :],
                    -self.cfg.commands.basic_max_curriculum,
                    self.cfg.commands.basic_max_curriculum,
                )
                self.command_ranges["ang_vel_yaw"][:, :] = torch.clip(
                    self.command_ranges["ang_vel_yaw"][:, :],
                    -self.cfg.commands.basic_max_ang_vel_curriculum,
                    self.cfg.commands.basic_max_ang_vel_curriculum,
                )
~~~

</details>


<details markdown="1"><summary>_shrink_command_range / F08,F09,F12,F13,F14,F15,F16,F17,F18,F40,F41,F42,F43,F44,F45,F46,F47,F48</summary>

适用：[F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:966>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:966>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1040>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1040>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1042>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1040>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1044>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:966>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:966>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:966>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:966>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:966>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1040>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:966>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:966>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:966>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1040>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1040>)
~~~python
def _shrink_command_range(self, command_name, env_ids, step, min_abs, max_abs):
        if len(env_ids) == 0:
            return
        self.command_ranges[command_name][env_ids, 0] = torch.clip(
            self.command_ranges[command_name][env_ids, 0] + step,
            -max_abs,
            -min_abs,
        )
        self.command_ranges[command_name][env_ids, 1] = torch.clip(
            self.command_ranges[command_name][env_ids, 1] - step,
            min_abs,
            max_abs,
        )
~~~

</details>


<details markdown="1"><summary>_grow_command_range / F08,F09,F12,F13,F14,F15,F16,F17,F18,F40,F41,F42,F43,F44,F45,F46,F47,F48</summary>

适用：[F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:980>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:980>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1054>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1054>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1056>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1054>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1058>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:980>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:980>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:980>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:980>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:980>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1054>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:980>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:980>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:980>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1054>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1054>)
~~~python
def _grow_command_range(self, command_name, success_ids, basic_ids, advanced_step, basic_extra):
        if len(success_ids) == 0:
            return
        self.command_ranges[command_name][success_ids, 0] -= advanced_step
        self.command_ranges[command_name][success_ids, 1] += advanced_step
        if len(basic_ids) != 0:
            self.command_ranges[command_name][basic_ids, 0] -= basic_extra
            self.command_ranges[command_name][basic_ids, 1] += basic_extra
~~~

</details>


<details markdown="1"><summary>_clip_command_range / F08,F09,F12,F13,F14,F15,F16,F17,F18,F40,F41,F42,F43,F44,F45,F46,F47,F48</summary>

适用：[F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:989>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:989>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1063>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1063>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1065>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1063>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1067>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:989>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:989>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:989>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:989>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:989>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1063>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:989>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:989>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:989>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1063>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1063>)
~~~python
def _clip_command_range(self, command_name, basic_max, advanced_max):
        if len(self.basic_terrain_idx) != 0:
            self.command_ranges[command_name][self.basic_terrain_idx, :] = torch.clip(
                self.command_ranges[command_name][self.basic_terrain_idx, :],
                -basic_max,
                basic_max,
            )
        if len(self.advanced_terrain_idx) != 0:
            self.command_ranges[command_name][self.advanced_terrain_idx, :] = torch.clip(
                self.command_ranges[command_name][self.advanced_terrain_idx, :],
                -advanced_max,
                advanced_max,
            )
~~~

</details>


<details markdown="1"><summary>_reward_base_height / F08,F09,F12,F13,F14,F15,F16,F17,F18,F36,F37,F38,F39,F40,F41,F42,F43,F44,F45,F46,F47,F48</summary>

适用：[F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1818>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1818>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:1909>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:1909>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1912>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:1909>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:1914>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1818>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1818>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:1731>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:1731>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:1731>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:1731>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1818>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1818>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1818>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:1909>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1818>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1818>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1818>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:1909>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:1909>)
~~~python
def _reward_base_height(self):
        # Penalize base height away from target
        # print(self.commands[0, 2], self.base_height[0])
        if self.reward_scales["base_height"] < 0:
            return torch.abs(self.base_height - self.commands[:, 2])
        else:
            base_height_error = torch.square(self.base_height - self.commands[:, 2])
            return torch.exp(-base_height_error * 1000) * 1.5
~~~

</details>


<details markdown="1"><summary>_reward_tracking_lin_vel / F08,F09,F12,F13,F14,F15,F16,F17,F18,F40,F41,F42,F43,F44,F45,F46,F47,F48</summary>

适用：[F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1925>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1925>) · [F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2016>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2016>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2030>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2016>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2017>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1925>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1925>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1925>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1925>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1925>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2016>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1925>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1925>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1925>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2016>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2016>)
~~~python
def _reward_tracking_lin_vel(self):
        # Tracking of linear velocity commands (x axes)
        lin_vel_error = torch.square(self.commands[:, 0] - self.base_lin_vel[:, 0])
        return torch.exp(-lin_vel_error / self.cfg.rewards.tracking_sigma) * 1.3
~~~

</details>


<details markdown="1"><summary>_reward_tracking_lin_vel_enhance / F08,F09,F17,F18,F40,F41,F42,F43,F44,F45,F46,F48</summary>

适用：[F08](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji/legged_robot.py:1930>) · [F09](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/25_20_1.0_0.2_orientation+_suiji继续训练了很久/legged_robot.py:1930>) · [F17](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd201.00.2terrian/legged_robot.py:1930>) · [F18](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/history10latent16_pd602.00.2terrian/legged_robot.py:1930>) · [F40](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v1/legged_robot.py:1930>) · [F41](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v2/legged_robot.py:1930>) · [F42](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+添加随机地形，进一步训练v3_速度上限拉大因为原本发现飞坡速度不够/legged_robot.py:1930>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2021>) · [F44](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第一版本recover/legged_robot.py:1930>) · [F45](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第三版本加入随机地形继续训练很久recover/legged_robot.py:1930>) · [F46](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第二版本加入随机地形recover/legged_robot.py:1930>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2021>)
~~~python
def _reward_tracking_lin_vel_enhance(self):
        # Tracking of linear velocity commands (x axes)
        lin_vel_error = torch.square(self.commands[:, 0] - self.base_lin_vel[:, 0])
        return (torch.exp(-lin_vel_error / self.cfg.rewards.tracking_sigma / 10) - 1) * 1.3
~~~

</details>


<details markdown="1"><summary>_reward_tracking_lin_vel_enhance / F12,F13,F14,F15,F16,F47</summary>

适用：[F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2021>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2021>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2035>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2021>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2022>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2021>)
~~~python
def _reward_tracking_lin_vel_enhance(self):
        # Tracking of linear velocity commands (x axes)
        lin_vel_error = torch.square(self.commands[:, 0] - self.base_lin_vel[:, 0])
        return (torch.exp(-lin_vel_error / self.cfg.rewards.tracking_sigma / 10) - 1) * 1.45
~~~

</details>


<details markdown="1"><summary>_reward_wheel_air_theta0 / F12,F13,F14,F15,F16,F43,F47,F48</summary>

适用：[F12](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2/legged_robot.py:2042>) · [F13](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0/legged_robot.py:2042>) · [F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2056>) · [F15](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0/legged_robot.py:2042>) · [F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2043>) · [F43](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊特殊版本 把力矩上限调整50发现解决了站起来失力问题但是由于奖励离地theta导致会小碎步recover/legged_robot.py:2042>) · [F47](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第五版本/legged_robot.py:2042>) · [F48](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/腿熊第四版本随机地形分布改进难度降低发现力矩限制在30不太行因为车太重了recover/legged_robot.py:2042>)
~~~python
def _reward_wheel_air_theta0(self):
        wheel_contact = (
            torch.norm(self.contact_forces[:, self.wheel_indices, :], dim=-1)
            > self.cfg.rewards.wheel_contact_force_threshold
        )
        wheel_air = ~wheel_contact
        theta0_error = torch.square(self.theta0[:, : self.wheel_indices.shape[0]])
        theta0_reward = torch.exp(-theta0_error / self.cfg.rewards.tracking_sigma)

        return torch.sum(theta0_reward * wheel_air.float(), dim=1)
~~~

</details>


<details markdown="1"><summary>_reward_leg_action_l2 / F14</summary>

适用：[F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1965>)
~~~python
def _reward_leg_action_l2(self):
        """Penalize large leg commands without suppressing wheel rotation commands."""
        return torch.sum(torch.square(self.actions[:, :2]), dim=1) + torch.sum(
            torch.square(self.actions[:, 3:5]), dim=1
        )
~~~

</details>


<details markdown="1"><summary>_reward_torque_rate / F14</summary>

适用：[F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:1971>)
~~~python
def _reward_torque_rate(self):
        """Penalize step-to-step motor torque changes for smoother actuation."""
        return torch.sum(torch.square(self.torques - self.last_torques), dim=1)
~~~

</details>


<details markdown="1"><summary>_reward_torque_limits / F14</summary>

适用：[F14](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.20.20.00.30.30.0加大了惩罚/legged_robot.py:2019>)
~~~python
def _reward_torque_limits(self):
        # Penalize wheel torques above the soft limit. The two wheel joints are
        # indices 2 and 5 in this six-DOF robot.
        wheel_torques = self.torques[:, [2, 5]]
        wheel_limits = self.torque_limits[[2, 5]]
        soft_limit = wheel_limits * self.cfg.rewards.soft_torque_limit
        return torch.sum(
            (torch.abs(wheel_torques) - soft_limit).clip(min=0.0),
            dim=1,
        )
~~~

</details>


<details markdown="1"><summary>_reward_wheel_torques / F16</summary>

适用：[F16](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/6010.2加入随机地形terrain_proportions0.50.20.10.10.10.0加大了惩罚/legged_robot.py:2011>)
~~~python
def _reward_wheel_torques(self):
        """Penalize wheel torque requests outside the [-3, 3] N*m dead zone."""
        wheel_torques = self.unclipped_torques[:, [2, 5]]
        excess = (torch.abs(wheel_torques) - 3.0).clip(min=0.0)
        return torch.sum(torch.square(excess), dim=1)
~~~

</details>


<details markdown="1"><summary>_update_terrain_curriculum / F28,F36,F37,F38,F39</summary>

适用：[F28](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/recover_from_lied_on_ground/legged_robot.py:848>) · [F36](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶1/legged_robot.py:848>) · [F37](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶2/legged_robot.py:848>) · [F38](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3/legged_robot.py:848>) · [F39](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/logs/wheel_legged/上台阶3_angz+/legged_robot.py:848>)
~~~python
def _update_terrain_curriculum(self, env_ids):
        """Implements the game-inspired curriculum.

        Args:
            env_ids (List[int]): ids of environments being reset
        """
        # Implement Terrain curriculum
        if not self.init_done:
            # don't change on initial reset
            return
        distance = torch.norm(
            self.root_states[env_ids, :2] - self.env_origins[env_ids, :2], dim=1
        )
        # robots that walked far enough progress to harder terains
        move_up = distance > self.terrain.env_length / 2  #原本是/2
        # robots that walked less than half of their required distance go to simpler terrains
        move_down = (
            self.episode_sums["tracking_lin_vel"][env_ids] / self.max_episode_length_s
            < (self.reward_scales["tracking_lin_vel"] / self.dt) * 0.4
        ) * ~move_up
        self.terrain_levels[env_ids] += 1 * move_up - 1 * move_down
        mask = self.terrain_levels[env_ids] >= self.max_terrain_level
        self.success_ids = env_ids[mask]
        mask = self.terrain_levels[env_ids] < 0
        self.fail_ids = env_ids[mask]
        # Robots that solve the last level are sent to a random one
        self.terrain_levels[env_ids] = torch.where(
            self.terrain_levels[env_ids] >= self.max_terrain_level,
            torch.randint_like(self.terrain_levels[env_ids], self.max_terrain_level),
            torch.clip(self.terrain_levels[env_ids], 0),
        )  # (the minumum level is zero)
        self.env_origins[env_ids] = self.terrain_origins[
            self.terrain_levels[env_ids], self.terrain_types[env_ids]
        ]
        if self.cfg.commands.curriculum:
            self.command_ranges["lin_vel_x"][self.fail_ids, 0] = torch.clip(
                self.command_ranges["lin_vel_x"][self.fail_ids, 0] + 0.25,
                -self.cfg.commands.basic_max_curriculum,
                -1,
            )
            self.command_ranges["lin_vel_x"][self.fail_ids, 1] = torch.clip(
                self.command_ranges["lin_vel_x"][self.fail_ids, 1] - 0.25,
                1,
                self.cfg.commands.basic_max_curriculum,
            )
~~~

</details>


<details markdown="1"><summary>check_jump / F49,F50</summary>

适用：[F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:239>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:239>)
~~~python
def check_jump(self):
        """ Check if the robot has jumped
        """
        self.was_in_flight[:] = False
        contact = self.contact_forces[:, self.feet_indices, 2] > 1.0         #contect: (num_envs, num_feet:2)
        # print("contact",contact)
        self.contact_filt =torch.logical_or(contact, self.last_contacts)    #self.contact_filt: (num_envs, num_feet:2)
        self.last_contacts=contact.clone()

        jump_filter = torch.all(~self.contact_filt , dim=1)     #jump_filter: (num_envs,)  True表示两只脚都没有接触地面

        # was_in_flight=torch.logical_and(jump_filter,self.commands[:,2]>0)
        was_in_flight = jump_filter
        self.was_in_flight[was_in_flight] = True
~~~

</details>


<details markdown="1"><summary>_resample_commands / F49,F50</summary>

适用：[F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:708>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:708>)
~~~python
def _resample_commands(self, env_ids):
        """Randommly select commands of some environments

        Args:
            env_ids (List[int]): Environments ids for which new commands are needed
        """
        self.commands[env_ids, 0] = (
            self.command_ranges["lin_vel_x"][env_ids, 1]
            - self.command_ranges["lin_vel_x"][env_ids, 0]
        ) * torch.rand(len(env_ids), device=self.device) + self.command_ranges[
            "lin_vel_x"
        ][
            env_ids, 0
        ]
        self.commands[env_ids, 1] = (
            self.command_ranges["ang_vel_yaw"][env_ids, 1]
            - self.command_ranges["ang_vel_yaw"][env_ids, 0]
        ) * torch.rand(len(env_ids), device=self.device) + self.command_ranges[
            "ang_vel_yaw"
        ][
            env_ids, 0
        ]
        self.commands[env_ids, 2] = (
            self.command_ranges["height"][env_ids, 1]
            - self.command_ranges["height"][env_ids, 0]
        ) * torch.rand(len(env_ids), device=self.device) + self.command_ranges[
            "height"
        ][
            env_ids, 0
        ]


        if self.cfg.commands.heading_command:
            self.commands[env_ids, 3] = torch_rand_float(
                self.command_ranges["heading"][0],
                self.command_ranges["heading"][1],
                (len(env_ids), 1),
                device=self.device,
            ).squeeze(1)
~~~

</details>


<details markdown="1"><summary>_reward_encourage_jump / F49,F50</summary>

适用：[F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1729>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1729>)
~~~python
def _reward_encourage_jump(self):

        first_contact = (self.base_air_time > 0.0) * ~self.was_in_flight
        self.base_air_time += self.dt * torch.clip(
            self.root_states[:, 2],
            torch.tensor(0.0, device=self.device),
            0.50,
        )

        rew_airTime = (self.base_air_time - 5e-5) * first_contact * 0.15

        rew_airTime += (
            torch.maximum(
                torch.tensor(0.0, device=self.device), self.root_states[:, 9]
            )

        )  * 0.15

        self.base_air_time *= ~self.was_in_flight
        return rew_airTime
~~~

</details>


<details markdown="1"><summary>_reward_air_time / F49,F50</summary>

适用：[F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1750>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1750>)
~~~python
def _reward_air_time(self):

        self.base_air_time += self.dt * self.was_in_flight

        rew_airTime = self.base_air_time - 5e-5

        return rew_airTime
~~~

</details>


<details markdown="1"><summary>_reward_line_z / F49,F50</summary>

适用：[F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1759>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1759>)
~~~python
def _reward_line_z(self):
        #在初始化后和落地之前z轴线速度越大越好
        rew=(self.root_states[:, 9]>0)*self.root_states[:, 9] * (self.was_in_flight)
        return rew
~~~

</details>


<details markdown="1"><summary>_reward_leg_tuck / F49,F50</summary>

适用：[F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1764>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1764>)
~~~python
def _reward_leg_tuck(self):
        # Reward tucking legs in air (shorter virtual leg length) during flight.
        leg_tuck_err = torch.sum(torch.abs(self.L0 - 0.16), dim=1)
        rew = torch.exp(-leg_tuck_err * 4.0) * (self.was_in_flight)
        return rew
~~~

</details>


<details markdown="1"><summary>_reward_base_height_flight / F49,F50</summary>

适用：[F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1770>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1770>)
~~~python
def _reward_base_height_flight(self):
        #跳跃的高度奖励
        base_height_flight = (self.root_states[:, 2] - 0.65)
        rew= torch.exp(-torch.abs(base_height_flight)*6.0)*(self.was_in_flight)
        return rew
~~~

</details>


<details markdown="1"><summary>_reward_takeoff_extend / F49,F50</summary>

适用：[F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1776>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1776>)
~~~python
def _reward_takeoff_extend(self):
        # Reward extending the virtual leg during the push-off phase.
        takeoff_mask = torch.any(self.contact_filt, dim=1) & (self.root_states[:, 9] > 0.15)
        target_l0 = 0.31
        l0_err = torch.sum(torch.abs(self.L0 - target_l0), dim=1)
        rew = torch.exp(-l0_err * 4.0) * takeoff_mask
        return rew
~~~

</details>


<details markdown="1"><summary>_reward_L0_flight / F49,F50</summary>

适用：[F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1784>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1784>)
~~~python
def _reward_L0_flight(self):
        #跳跃的高度奖励
        L0_err = (self.L0 - 0.40)
        rew= torch.exp(-torch.sum(torch.abs(L0_err), dim=1)*5.0)*(~self.was_in_flight)
        return rew
~~~

</details>


<details markdown="1"><summary>_reward_flight / F49,F50</summary>

适用：[F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1791>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1791>)
~~~python
def _reward_flight(self):
        # Penalize dof velocities
        return self.was_in_flight
~~~

</details>


<details markdown="1"><summary>_reward_tracking_lin_vel / F49,F50</summary>

适用：[F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1897>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1897>)
~~~python
def _reward_tracking_lin_vel(self):
        # Tracking of linear velocity commands (x axes)
        lin_vel_error = torch.square(self.commands[:, 0] - self.base_lin_vel[:, 0])
        return torch.exp(-lin_vel_error / self.cfg.rewards.tracking_sigma) * 2
~~~

</details>


<details markdown="1"><summary>_reward_tracking_lin_vel_enhance / F49,F50</summary>

适用：[F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1906>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1906>)
~~~python
def _reward_tracking_lin_vel_enhance(self):
        # Tracking of linear velocity commands (x axes)
        lin_vel_error = torch.square(self.commands[:, 0] - self.base_lin_vel[:, 0])
        return (torch.exp(-lin_vel_error / self.cfg.rewards.tracking_sigma / 10) - 1) * 2
~~~

</details>


<details markdown="1"><summary>_reward_nominal_state / F49,F50</summary>

适用：[F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1949>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1949>)
~~~python
def _reward_nominal_state(self):
        # return torch.square(self.theta0[:, 0] - self.theta0[:, 1])
        a = torch.square(self.theta0[:, 0] - self.theta0[:, 1])
        b = 10 * torch.square(self.L0[:, 0] - self.L0[:, 1])
        return a + b
~~~

</details>


<details markdown="1"><summary>_reward_pen_theta_no0 / F49,F50</summary>

适用：[F49](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py:1957>) · [F50](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/logs/wheel_legged/p60.50.2目前测试下来最好的/legged_robot.py:1957>)
~~~python
def _reward_pen_theta_no0(self):
        # Penalize non-zero theta0 to encourage legs to be under the body
        return torch.sum(torch.square(self.theta0), dim=1)
~~~

</details>


<details markdown="1"><summary>复旦当前 plane/rsl_rl/modules/actor_critic_sequence.py</summary>

[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/rsl_rl/modules/actor_critic_sequence.py>)
~~~python
# SPDX-FileCopyrightText: Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Copyright (c) 2021 ETH Zurich, Nikita Rudin

import numpy as np

import torch
import torch.nn as nn
from torch.distributions import Normal
from torch.nn.modules import rnn


class ActorCriticSequence(nn.Module):
    is_recurrent = False
    is_sequence = True

    def __init__(
        self,
        num_obs,
        num_critic_obs,
        num_actions,
        num_encoder_obs,
        latent_dim,
        encoder_hidden_dims=[256, 256, 256],
        actor_hidden_dims=[256, 256, 256],
        critic_hidden_dims=[256, 256, 256],
        activation="elu",
        orthogonal_init=False,
        init_noise_std=1.0,
        **kwargs,
    ):
        if kwargs:
            print(
                "ActorCriticVAE.__init__ got unexpected arguments, which will be ignored: "
                + str([key for key in kwargs.keys()])
            )
        super(ActorCriticSequence, self).__init__()

        self.orthogonal_init = orthogonal_init
        self.latent_dim = latent_dim

        activation = get_activation(activation)

        # Encoder
        encoder_layers = []
        encoder_layers.append(nn.Linear(num_encoder_obs, encoder_hidden_dims[0]))
        if self.orthogonal_init:
            torch.nn.init.orthogonal_(encoder_layers[-1].weight, np.sqrt(2))
        encoder_layers.append(activation)
        for l in range(len(encoder_hidden_dims)):
            if l == len(encoder_hidden_dims) - 1:
                encoder_layers.append(
                    nn.Linear(encoder_hidden_dims[l], self.latent_dim)
                )
                if self.orthogonal_init:
                    torch.nn.init.orthogonal_(encoder_layers[-1].weight, 0.01)
                    torch.nn.init.constant_(encoder_layers[-1].bias, 0.0)
            else:
                encoder_layers.append(
                    nn.Linear(encoder_hidden_dims[l], encoder_hidden_dims[l + 1])
                )
                if self.orthogonal_init:
                    torch.nn.init.orthogonal_(encoder_layers[-1].weight, np.sqrt(2))
                    torch.nn.init.constant_(encoder_layers[-1].bias, 0.0)
                encoder_layers.append(activation)
                # actor_layers.append(torch.nn.LayerNorm(actor_hidden_dims[l + 1]))
        self.encoder = nn.Sequential(*encoder_layers)

        # Policy
        actor_layers = []
        actor_layers.append(nn.Linear(num_obs + self.latent_dim, actor_hidden_dims[0]))
        if self.orthogonal_init:
            torch.nn.init.orthogonal_(actor_layers[-1].weight, np.sqrt(2))
        actor_layers.append(activation)
        for l in range(len(actor_hidden_dims)):
            if l == len(actor_hidden_dims) - 1:
                actor_layers.append(nn.Linear(actor_hidden_dims[l], num_actions))
                if self.orthogonal_init:
                    torch.nn.init.orthogonal_(actor_layers[-1].weight, 0.01)
                    torch.nn.init.constant_(actor_layers[-1].bias, 0.0)
            else:
                actor_layers.append(
                    nn.Linear(actor_hidden_dims[l], actor_hidden_dims[l + 1])
                )
                if self.orthogonal_init:
                    torch.nn.init.orthogonal_(actor_layers[-1].weight, np.sqrt(2))
                    torch.nn.init.constant_(actor_layers[-1].bias, 0.0)
                actor_layers.append(activation)
                # actor_layers.append(torch.nn.LayerNorm(actor_hidden_dims[l + 1]))
        self.actor = nn.Sequential(*actor_layers)

        # Value function
        critic_layers = []
        critic_layers.append(nn.Linear(num_critic_obs, critic_hidden_dims[0]))
        critic_layers.append(activation)
        for l in range(len(critic_hidden_dims)):
            if l == len(critic_hidden_dims) - 1:
                critic_layers.append(nn.Linear(critic_hidden_dims[l], 1))
                if self.orthogonal_init:
                    torch.nn.init.orthogonal_(critic_layers[-1].weight, 0.01)
                    torch.nn.init.constant_(critic_layers[-1].bias, 0.0)
            else:
                critic_layers.append(
                    nn.Linear(critic_hidden_dims[l], critic_hidden_dims[l + 1])
                )
                if self.orthogonal_init:
                    torch.nn.init.orthogonal_(critic_layers[-1].weight, np.sqrt(2))
                    torch.nn.init.constant_(critic_layers[-1].bias, 0.0)
                critic_layers.append(activation)
                # critic_layers.append(torch.nn.LayerNorm(critic_hidden_dims[l + 1]))
        self.critic = nn.Sequential(*critic_layers)

        print(f"Encoder MLP: {self.encoder}")
        print(f"Actor MLP: {self.actor}")
        print(f"Critic MLP: {self.critic}")

        # Action noise
        self.std = nn.Parameter(init_noise_std * torch.ones(num_actions))
        self.distribution = None
        # disable args validation for speedup
        Normal.set_default_validate_args = False

        # seems that we get better performance without init
        # self.init_memory_weights(self.memory_a, 0.001, 0.)
        # self.init_memory_weights(self.memory_c, 0.001, 0.)

    @staticmethod
    # not used at the moment
    def init_weights(sequential, scales):
        [
            torch.nn.init.orthogonal_(module.weight, gain=scales[idx])
            for idx, module in enumerate(
                mod for mod in sequential if isinstance(mod, nn.Linear)
            )
        ]

    def reset(self, dones=None):
        pass

    def forward(self):
        raise NotImplementedError

    @property
    def action_mean(self):
        return self.distribution.mean

    @property
    def action_std(self):
        return self.distribution.stddev

    @property
    def entropy(self):
        return self.distribution.entropy().sum(dim=-1)

    def update_distribution(self, observations, observation_history):
        self.latent = self.encoder(observation_history)
        mean = self.actor(torch.cat((observations, self.latent.detach()), dim=-1))                    ############################这里
        self.distribution = Normal(mean, mean*0. + self.std)

    def act(self, observations, observation_history, **kwargs):
        self.update_distribution(observations, observation_history)
        return self.distribution.sample()

    def get_actions_log_prob(self, actions):
        return self.distribution.log_prob(actions).sum(dim=-1)

    def get_latent(self, **kwargs):
        return self.latent

    def act_inference(self, observations, observation_history):
        self.latent = self.encoder(observation_history)
        actions_mean = self.actor(torch.cat((observations, self.latent), dim=-1))
        return actions_mean, self.latent

    def evaluate(self, critic_observations, **kwargs):
        value = self.critic(critic_observations)
        return value

    def encode(self, observation_history, **kwargs):
        latent = self.encoder(observation_history)
        return latent


def get_activation(act_name):
    if act_name == "elu":
        return nn.ELU()
    elif act_name == "selu":
        return nn.SELU()
    elif act_name == "relu":
        return nn.ReLU()
    elif act_name == "crelu":
        return nn.ReLU()
    elif act_name == "lrelu":
        return nn.LeakyReLU()
    elif act_name == "tanh":
        return nn.Tanh()
    elif act_name == "sigmoid":
        return nn.Sigmoid()
    else:
        print("invalid activation function!")
        return None

~~~

</details>


<details markdown="1"><summary>复旦当前 plane/rsl_rl/algorithms/ppo.py</summary>

[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/rsl_rl/algorithms/ppo.py>)
~~~python
#  Copyright 2021 ETH Zurich, NVIDIA CORPORATION
#  SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import torch
import torch.nn as nn
import torch.optim as optim

from wheel_legged_gym.rsl_rl.modules import ActorCritic
from wheel_legged_gym.rsl_rl.storage import RolloutStorage


class PPO:
    actor_critic: ActorCritic

    def __init__(
        self,
        actor_critic,
        num_learning_epochs=1,
        num_mini_batches=1,
        clip_param=0.2,
        gamma=0.998,
        lam=0.95,
        value_loss_coef=1.0,
        entropy_coef=0.0,
        learning_rate=1e-3,
        extra_learning_rate=1e-3,
        max_grad_norm=1.0,
        use_clipped_value_loss=True,
        schedule="fixed",
        desired_kl=0.01,
        kl_decay=0,
        device="cpu",
    ):
        self.device = device

        self.desired_kl = desired_kl
        self.kl_decay = max(kl_decay, 0)
        self.schedule = schedule
        self.learning_rate = learning_rate

        # PPO components
        self.actor_critic = actor_critic
        self.actor_critic.to(self.device)
        self.storage = None  # initialized later
        self.optimizer = optim.Adam(
            [
                {"params": self.actor_critic.actor.parameters()},
                {"params": self.actor_critic.critic.parameters()},
                {"params": self.actor_critic.std},
            ],
            lr=learning_rate,
        )
        self.extra_optimizer = None
        if self.actor_critic.is_sequence:
            self.extra_optimizer = optim.Adam(
                [
                    {"params": self.actor_critic.encoder.parameters()},
                ],
                lr=extra_learning_rate,
            )
        self.transition = RolloutStorage.Transition()

        # PPO parameters
        self.clip_param = clip_param
        self.num_learning_epochs = num_learning_epochs
        self.num_mini_batches = num_mini_batches
        self.value_loss_coef = value_loss_coef
        self.entropy_coef = entropy_coef
        self.gamma = gamma
        self.lam = lam
        self.max_grad_norm = max_grad_norm
        self.use_clipped_value_loss = use_clipped_value_loss

    def init_storage(
        self,
        num_envs,
        num_transitions_per_env,
        actor_obs_shape,
        critic_obs_shape,
        obs_history_shape,
        action_shape,
    ):
        self.storage = RolloutStorage(
            num_envs,
            num_transitions_per_env,
            actor_obs_shape,
            critic_obs_shape,
            obs_history_shape,
            action_shape,
            self.device,
        )

    def test_mode(self):
        self.actor_critic.test()

    def train_mode(self):
        self.actor_critic.train()

    def act(self, obs, obs_history, critic_obs):
        if self.actor_critic.is_recurrent:
            self.transition.hidden_states = self.actor_critic.get_hidden_states()
        # Compute the actions and values
        if self.actor_critic.is_sequence:
            self.transition.actions = self.actor_critic.act(obs, obs_history).detach()
            latent = self.actor_critic.get_latent()
            critic_obs = torch.cat((critic_obs, latent), dim=-1)
        else:
            self.transition.actions = self.actor_critic.act(obs).detach()
        self.transition.values = self.actor_critic.evaluate(critic_obs).detach()
        self.transition.actions_log_prob = self.actor_critic.get_actions_log_prob(
            self.transition.actions
        ).detach()
        self.transition.action_mean = self.actor_critic.action_mean.detach()
        self.transition.action_sigma = self.actor_critic.action_std.detach()
        # need to record obs and critic_obs before env.step()
        self.transition.observations = obs.clone()
        self.transition.observation_history = obs_history.clone()
        self.transition.critic_observations = critic_obs.clone()
        return self.transition.actions

    def process_env_step(self, rewards, dones, infos, next_obs=None):
        self.transition.rewards = rewards.clone()
        self.transition.dones = dones
        # Bootstrapping on time outs
        if "time_outs" in infos:
            self.transition.rewards += self.gamma * torch.squeeze(
                self.transition.values
                * infos["time_outs"].unsqueeze(1).to(self.device),
                1,
            )

        # Record the transition
        self.transition.next_observations = next_obs
        self.storage.add_transitions(self.transition)
        self.transition.clear()
        self.actor_critic.reset(dones)

    def compute_returns(self, last_critic_obs):
        last_values = self.actor_critic.evaluate(last_critic_obs).detach()
        self.storage.compute_returns(last_values, self.gamma, self.lam)

    def update(self):
        if self.kl_decay != 0:
            self.desired_kl = max(self.desired_kl - self.kl_decay, 0.001)
        num_updates = 0
        mean_value_loss = 0
        mean_surrogate_loss = 0
        mean_kl = 0
        if self.actor_critic.is_recurrent:
            generator = self.storage.reccurent_mini_batch_generator(
                self.num_mini_batches, self.num_learning_epochs
            )
        else:
            generator = self.storage.mini_batch_generator(
                self.num_mini_batches, self.num_learning_epochs
            )
        for (
            obs_batch,
            obs_history_batch,
            critic_obs_batch,
            actions_batch,
            target_values_batch,
            advantages_batch,
            returns_batch,
            old_actions_log_prob_batch,
            old_mu_batch,
            old_sigma_batch,
            hid_states_batch,
            masks_batch,
        ) in generator:
            if self.actor_critic.is_sequence:
                self.actor_critic.act(
                    obs_batch,
                    obs_history_batch,
                    masks=masks_batch,
                    hidden_states=hid_states_batch[0],
                )
            else:
                self.actor_critic.act(
                    obs_batch, masks=masks_batch, hidden_states=hid_states_batch[0]
                )
            actions_log_prob_batch = self.actor_critic.get_actions_log_prob(
                actions_batch
            )
            value_batch = self.actor_critic.evaluate(
                critic_obs_batch, masks=masks_batch, hidden_states=hid_states_batch[1]
            )
            mu_batch = self.actor_critic.action_mean
            sigma_batch = self.actor_critic.action_std
            entropy_batch = self.actor_critic.entropy

            # KL
            with torch.inference_mode():
                kl = torch.sum(
                    torch.log(sigma_batch / old_sigma_batch + 1.0e-5)
                    + (
                        torch.square(old_sigma_batch)
                        + torch.square(old_mu_batch - mu_batch)
                    )
                    / (2.0 * torch.square(sigma_batch))
                    - 0.5,
                    axis=-1,
                )
                kl_mean = torch.mean(kl)

                if self.desired_kl is not None and self.schedule == "adaptive":
                    if kl_mean > self.desired_kl * 2.0:
                        self.learning_rate = max(1e-5, self.learning_rate / 1.5)
                    elif kl_mean < self.desired_kl / 2.0 and kl_mean > 0.0:
                        self.learning_rate = min(1e-2, self.learning_rate * 1.5)

                    for param_group in self.optimizer.param_groups:
                        param_group["lr"] = self.learning_rate

            # Surrogate loss
            ratio = torch.exp(
                actions_log_prob_batch - torch.squeeze(old_actions_log_prob_batch)
            )
            surrogate = -torch.squeeze(advantages_batch) * ratio
            surrogate_clipped = -torch.squeeze(advantages_batch) * torch.clamp(
                ratio, 1.0 - self.clip_param, 1.0 + self.clip_param
            )
            surrogate_loss = torch.max(surrogate, surrogate_clipped).mean()

            # Value function loss
            if self.use_clipped_value_loss:
                value_clipped = target_values_batch + (
                    value_batch - target_values_batch
                ).clamp(-self.clip_param, self.clip_param)
                value_losses = (value_batch - returns_batch).pow(2)
                value_losses_clipped = (value_clipped - returns_batch).pow(2)
                value_loss = torch.max(value_losses, value_losses_clipped).mean()
            else:
                value_loss = (returns_batch - value_batch).pow(2).mean()

            loss = (
                surrogate_loss
                + self.value_loss_coef * value_loss
                - self.entropy_coef * entropy_batch.mean()
            )

            # Gradient step
            self.optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(self.actor_critic.parameters(), self.max_grad_norm)
            self.optimizer.step()

            mean_value_loss += value_loss.item()
            mean_surrogate_loss += surrogate_loss.item()
            mean_kl += kl_mean.item()
            num_updates += 1

        num_updates_extra = 0
        mean_extra_loss = 0
        if self.extra_optimizer is not None:
            generator = self.storage.encoder_mini_batch_generator(
                self.num_mini_batches, self.num_learning_epochs
            )
            for next_obs_batch, critic_obs_batch, obs_history_batch in generator:
                if self.actor_critic.is_sequence:
                    latent_batch = self.actor_critic.encode(obs_history_batch)
                    vel_est_loss = (
                        (latent_batch[:, :3] - critic_obs_batch[:, :3]).pow(2).mean()
                    )
                    if self.actor_critic.latent_dim > 3:
                        obs_denoise_loss = (
                            (
                                latent_batch[:, 3 : self.actor_critic.latent_dim]
                                - critic_obs_batch[:, 3 : self.actor_critic.latent_dim]
                            )
                            .pow(2)
                            .mean()
                        )
                        extra_loss = vel_est_loss + obs_denoise_loss
                    else:
                        extra_loss = vel_est_loss

                self.extra_optimizer.zero_grad()
                extra_loss.backward()
                nn.utils.clip_grad_norm_(self.actor_critic.parameters(), 0.1)
                self.extra_optimizer.step()

                mean_extra_loss += extra_loss.item()
                num_updates_extra += 1

        mean_value_loss /= num_updates
        mean_surrogate_loss /= num_updates
        mean_kl /= num_updates
        if num_updates_extra > 0:
            mean_extra_loss /= num_updates_extra
        self.storage.clear()

        return (mean_value_loss, mean_surrogate_loss, mean_kl, mean_extra_loss)

~~~

</details>


<details markdown="1"><summary>复旦当前 plane/utils/terrain.py</summary>

[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/plane/wheel_legged_gym/utils/terrain.py>)
~~~python
# SPDX-FileCopyrightText: Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Copyright (c) 2021 ETH Zurich, Nikita Rudin

import numpy as np
from numpy.random import choice
from scipy import interpolate

from isaacgym import terrain_utils
from wheel_legged_gym.envs.base.legged_robot_config import LeggedRobotCfg


class Terrain:
    def __init__(self, cfg: LeggedRobotCfg.terrain, num_robots) -> None:

        self.cfg = cfg
        self.num_robots = num_robots
        self.type = cfg.mesh_type
        if self.type in ["none", "plane"]:
            return
        self.env_length = cfg.terrain_length
        self.env_width = cfg.terrain_width
        self.proportions = [
            np.sum(cfg.terrain_proportions[: i + 1])
            for i in range(len(cfg.terrain_proportions))
        ]

        self.cfg.num_sub_terrains = cfg.num_rows * cfg.num_cols
        self.env_origins = np.zeros((cfg.num_rows, cfg.num_cols, 3))

        self.width_per_env_pixels = int(self.env_width / cfg.horizontal_scale)
        self.length_per_env_pixels = int(self.env_length / cfg.horizontal_scale)

        self.border = int(cfg.border_size / self.cfg.horizontal_scale)
        self.tot_cols = int(cfg.num_cols * self.width_per_env_pixels) + 2 * self.border
        self.tot_rows = int(cfg.num_rows * self.length_per_env_pixels) + 2 * self.border

        self.height_field_raw = np.zeros((self.tot_rows, self.tot_cols), dtype=np.int16)
        if cfg.curriculum:
            self.curiculum()
        elif cfg.selected:
            self.selected_terrain()
        else:
            self.randomized_terrain()

        self.heightsamples = self.height_field_raw
        if self.type == "trimesh":
            self.vertices, self.triangles = (
                terrain_utils.convert_heightfield_to_trimesh(
                    self.height_field_raw,
                    self.cfg.horizontal_scale,
                    self.cfg.vertical_scale,
                    self.cfg.slope_treshold,
                )
            )

    def randomized_terrain(self):
        for k in range(self.cfg.num_sub_terrains):
            # Env coordinates in the world
            (i, j) = np.unravel_index(k, (self.cfg.num_rows, self.cfg.num_cols))

            choice = np.random.uniform(0, 1)
            difficulty = np.random.choice([0.5, 0.75, 0.9])
            terrain = self.make_terrain(choice, difficulty)
            self.add_terrain_to_map(terrain, i, j)

    def curiculum(self):
        for j in range(self.cfg.num_cols):
            for i in range(self.cfg.num_rows):
                difficulty = i / self.cfg.num_rows
                choice = j / self.cfg.num_cols + 0.001

                terrain = self.make_terrain(choice, difficulty)
                self.add_terrain_to_map(terrain, i, j)

    def selected_terrain(self):
        terrain_type = self.cfg.terrain_kwargs.pop("type")
        for k in range(self.cfg.num_sub_terrains):
            # Env coordinates in the world
            (i, j) = np.unravel_index(k, (self.cfg.num_rows, self.cfg.num_cols))

            terrain = terrain_utils.SubTerrain(
                "terrain",
                width=self.width_per_env_pixels,
                length=self.width_per_env_pixels,
                vertical_scale=self.vertical_scale,
                horizontal_scale=self.horizontal_scale,
            )

            eval(terrain_type)(terrain, **self.cfg.terrain_kwargs.terrain_kwargs)
            self.add_terrain_to_map(terrain, i, j)

    def make_terrain(self, choice, difficulty):
        terrain = terrain_utils.SubTerrain(
            "terrain",
            width=self.width_per_env_pixels,
            length=self.width_per_env_pixels,
            vertical_scale=self.cfg.vertical_scale,
            horizontal_scale=self.cfg.horizontal_scale,
        )
        slope = difficulty * 0.5
        random_height = 0.05 + difficulty * 0.05
        step_height = 0.05 + 0.18 * difficulty
        discrete_obstacles_height = 0.05 + difficulty * 0.1
        stepping_stones_size = 1.5 * (1.05 - difficulty)
        stone_distance = 0.05 if difficulty == 0 else 0.1
        gap_size = 1.0 * difficulty
        pit_depth = 1.0 * difficulty
        if choice < self.proportions[0]:
            terrain_utils.pyramid_sloped_terrain(terrain, slope=0, platform_size=3.0)
        elif choice < self.proportions[1]:
            if (
                choice
                < self.proportions[0] + (self.proportions[1] - self.proportions[0]) / 2
            ):
                slope *= -1
            terrain_utils.pyramid_sloped_terrain(
                terrain, slope=slope, platform_size=3.0
            )
        elif choice < self.proportions[2]:
            if (
                choice
                < self.proportions[1] + (self.proportions[2] - self.proportions[1]) / 2
            ):
                slope *= -1
            terrain_utils.pyramid_sloped_terrain(
                terrain, slope=slope * 0.5, platform_size=3.0
            )
            terrain_utils.random_uniform_terrain(
                terrain,
                min_height=-random_height,
                max_height=random_height,
                step=0.005,
                downsampled_scale=0.2,
            )
        elif choice < self.proportions[4]:
            if choice < self.proportions[3]:
                step_height *= -1
            terrain_utils.pyramid_stairs_terrain(
                terrain, step_width=0.7, step_height=step_height, platform_size=4.0
            )
        elif choice < self.proportions[5]:
            num_rectangles = 20
            rectangle_min_size = 1.0
            rectangle_max_size = 2.0
            terrain_utils.discrete_obstacles_terrain(
                terrain,
                discrete_obstacles_height,
                rectangle_min_size,
                rectangle_max_size,
                num_rectangles,
                platform_size=3.0,
            )
        elif choice < self.proportions[6]:
            terrain_utils.stepping_stones_terrain(
                terrain,
                stone_size=stepping_stones_size,
                stone_distance=stone_distance,
                max_height=0.0,
                platform_size=4.0,
            )
        elif choice < self.proportions[7]:
            gap_terrain(terrain, gap_size=gap_size, platform_size=3.0)
        else:
            pit_terrain(terrain, depth=pit_depth, platform_size=4.0)

        return terrain

    def add_terrain_to_map(self, terrain, row, col):
        i = row
        j = col
        # map coordinate system
        start_x = self.border + i * self.length_per_env_pixels
        end_x = self.border + (i + 1) * self.length_per_env_pixels
        start_y = self.border + j * self.width_per_env_pixels
        end_y = self.border + (j + 1) * self.width_per_env_pixels
        self.height_field_raw[start_x:end_x, start_y:end_y] = terrain.height_field_raw

        env_origin_x = (i + 0.5) * self.env_length
        env_origin_y = (j + 0.5) * self.env_width
        x1 = int((self.env_length / 2.0 - 1) / terrain.horizontal_scale)
        x2 = int((self.env_length / 2.0 + 1) / terrain.horizontal_scale)
        y1 = int((self.env_width / 2.0 - 1) / terrain.horizontal_scale)
        y2 = int((self.env_width / 2.0 + 1) / terrain.horizontal_scale)
        env_origin_z = (
            np.max(terrain.height_field_raw[x1:x2, y1:y2]) * terrain.vertical_scale
        )
        self.env_origins[i, j] = [env_origin_x, env_origin_y, env_origin_z]


def gap_terrain(terrain, gap_size, platform_size=1.0):
    gap_size = int(gap_size / terrain.horizontal_scale)
    platform_size = int(platform_size / terrain.horizontal_scale)

    center_x = terrain.length // 2
    center_y = terrain.width // 2
    x1 = (terrain.length - platform_size) // 2
    x2 = x1 + gap_size
    y1 = (terrain.width - platform_size) // 2
    y2 = y1 + gap_size

    terrain.height_field_raw[
        center_x - x2 : center_x + x2, center_y - y2 : center_y + y2
    ] = -1000
    terrain.height_field_raw[
        center_x - x1 : center_x + x1, center_y - y1 : center_y + y1
    ] = 0


def pit_terrain(terrain, depth, platform_size=1.0):
    depth = int(depth / terrain.vertical_scale)
    platform_size = int(platform_size / terrain.horizontal_scale / 2)
    x1 = terrain.length // 2 - platform_size
    x2 = terrain.length // 2 + platform_size
    y1 = terrain.width // 2 - platform_size
    y2 = terrain.width // 2 + platform_size
    terrain.height_field_raw[x1:x2, y1:y2] = -depth

~~~

</details>


<details markdown="1"><summary>复旦当前 jump/rsl_rl/modules/actor_critic_sequence.py</summary>

[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/rsl_rl/modules/actor_critic_sequence.py>)
~~~python
# SPDX-FileCopyrightText: Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Copyright (c) 2021 ETH Zurich, Nikita Rudin

import numpy as np

import torch
import torch.nn as nn
from torch.distributions import Normal
from torch.nn.modules import rnn


class ActorCriticSequence(nn.Module):
    is_recurrent = False
    is_sequence = True

    def __init__(
        self,
        num_obs,
        num_critic_obs,
        num_actions,
        num_encoder_obs,
        latent_dim,
        encoder_hidden_dims=[256, 256, 256],
        actor_hidden_dims=[256, 256, 256],
        critic_hidden_dims=[256, 256, 256],
        activation="elu",
        orthogonal_init=False,
        init_noise_std=1.0,
        **kwargs,
    ):
        if kwargs:
            print(
                "ActorCriticVAE.__init__ got unexpected arguments, which will be ignored: "
                + str([key for key in kwargs.keys()])
            )
        super(ActorCriticSequence, self).__init__()

        self.orthogonal_init = orthogonal_init
        self.latent_dim = latent_dim

        activation = get_activation(activation)

        # Encoder
        encoder_layers = []
        encoder_layers.append(nn.Linear(num_encoder_obs, encoder_hidden_dims[0]))
        if self.orthogonal_init:
            torch.nn.init.orthogonal_(encoder_layers[-1].weight, np.sqrt(2))
        encoder_layers.append(activation)
        for l in range(len(encoder_hidden_dims)):
            if l == len(encoder_hidden_dims) - 1:
                encoder_layers.append(
                    nn.Linear(encoder_hidden_dims[l], self.latent_dim)
                )
                if self.orthogonal_init:
                    torch.nn.init.orthogonal_(encoder_layers[-1].weight, 0.01)
                    torch.nn.init.constant_(encoder_layers[-1].bias, 0.0)
            else:
                encoder_layers.append(
                    nn.Linear(encoder_hidden_dims[l], encoder_hidden_dims[l + 1])
                )
                if self.orthogonal_init:
                    torch.nn.init.orthogonal_(encoder_layers[-1].weight, np.sqrt(2))
                    torch.nn.init.constant_(encoder_layers[-1].bias, 0.0)
                encoder_layers.append(activation)
                # actor_layers.append(torch.nn.LayerNorm(actor_hidden_dims[l + 1]))
        self.encoder = nn.Sequential(*encoder_layers)

        # Policy
        actor_layers = []
        actor_layers.append(nn.Linear(num_obs + self.latent_dim, actor_hidden_dims[0]))
        if self.orthogonal_init:
            torch.nn.init.orthogonal_(actor_layers[-1].weight, np.sqrt(2))
        actor_layers.append(activation)
        for l in range(len(actor_hidden_dims)):
            if l == len(actor_hidden_dims) - 1:
                actor_layers.append(nn.Linear(actor_hidden_dims[l], num_actions))
                if self.orthogonal_init:
                    torch.nn.init.orthogonal_(actor_layers[-1].weight, 0.01)
                    torch.nn.init.constant_(actor_layers[-1].bias, 0.0)
            else:
                actor_layers.append(
                    nn.Linear(actor_hidden_dims[l], actor_hidden_dims[l + 1])
                )
                if self.orthogonal_init:
                    torch.nn.init.orthogonal_(actor_layers[-1].weight, np.sqrt(2))
                    torch.nn.init.constant_(actor_layers[-1].bias, 0.0)
                actor_layers.append(activation)
                # actor_layers.append(torch.nn.LayerNorm(actor_hidden_dims[l + 1]))
        self.actor = nn.Sequential(*actor_layers)

        # Value function
        critic_layers = []
        critic_layers.append(nn.Linear(num_critic_obs, critic_hidden_dims[0]))
        critic_layers.append(activation)
        for l in range(len(critic_hidden_dims)):
            if l == len(critic_hidden_dims) - 1:
                critic_layers.append(nn.Linear(critic_hidden_dims[l], 1))
                if self.orthogonal_init:
                    torch.nn.init.orthogonal_(critic_layers[-1].weight, 0.01)
                    torch.nn.init.constant_(critic_layers[-1].bias, 0.0)
            else:
                critic_layers.append(
                    nn.Linear(critic_hidden_dims[l], critic_hidden_dims[l + 1])
                )
                if self.orthogonal_init:
                    torch.nn.init.orthogonal_(critic_layers[-1].weight, np.sqrt(2))
                    torch.nn.init.constant_(critic_layers[-1].bias, 0.0)
                critic_layers.append(activation)
                # critic_layers.append(torch.nn.LayerNorm(critic_hidden_dims[l + 1]))
        self.critic = nn.Sequential(*critic_layers)

        print(f"Encoder MLP: {self.encoder}")
        print(f"Actor MLP: {self.actor}")
        print(f"Critic MLP: {self.critic}")

        # Action noise
        self.std = nn.Parameter(init_noise_std * torch.ones(num_actions))
        self.distribution = None
        # disable args validation for speedup
        Normal.set_default_validate_args = False

        # seems that we get better performance without init
        # self.init_memory_weights(self.memory_a, 0.001, 0.)
        # self.init_memory_weights(self.memory_c, 0.001, 0.)

    @staticmethod
    # not used at the moment
    def init_weights(sequential, scales):
        [
            torch.nn.init.orthogonal_(module.weight, gain=scales[idx])
            for idx, module in enumerate(
                mod for mod in sequential if isinstance(mod, nn.Linear)
            )
        ]

    def reset(self, dones=None):
        pass

    def forward(self):
        raise NotImplementedError

    @property
    def action_mean(self):
        return self.distribution.mean

    @property
    def action_std(self):
        return self.distribution.stddev

    @property
    def entropy(self):
        return self.distribution.entropy().sum(dim=-1)

    def update_distribution(self, observations, observation_history):
        self.latent = self.encoder(observation_history)
        mean = self.actor(torch.cat((observations, self.latent.detach()), dim=-1))                    ############################这里
        self.distribution = Normal(mean, mean*0. + self.std)

    def act(self, observations, observation_history, **kwargs):
        self.update_distribution(observations, observation_history)
        return self.distribution.sample()

    def get_actions_log_prob(self, actions):
        return self.distribution.log_prob(actions).sum(dim=-1)

    def get_latent(self, **kwargs):
        return self.latent

    def act_inference(self, observations, observation_history):
        self.latent = self.encoder(observation_history)
        actions_mean = self.actor(torch.cat((observations, self.latent), dim=-1))
        return actions_mean, self.latent

    def evaluate(self, critic_observations, **kwargs):
        value = self.critic(critic_observations)
        return value

    def encode(self, observation_history, **kwargs):
        latent = self.encoder(observation_history)
        return latent


def get_activation(act_name):
    if act_name == "elu":
        return nn.ELU()
    elif act_name == "selu":
        return nn.SELU()
    elif act_name == "relu":
        return nn.ReLU()
    elif act_name == "crelu":
        return nn.ReLU()
    elif act_name == "lrelu":
        return nn.LeakyReLU()
    elif act_name == "tanh":
        return nn.Tanh()
    elif act_name == "sigmoid":
        return nn.Sigmoid()
    else:
        print("invalid activation function!")
        return None

~~~

</details>


<details markdown="1"><summary>复旦当前 jump/rsl_rl/algorithms/ppo.py</summary>

[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/rsl_rl/algorithms/ppo.py>)
~~~python
#  Copyright 2021 ETH Zurich, NVIDIA CORPORATION
#  SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import torch
import torch.nn as nn
import torch.optim as optim

from wheel_legged_gym.rsl_rl.modules import ActorCritic
from wheel_legged_gym.rsl_rl.storage import RolloutStorage


class PPO:
    actor_critic: ActorCritic

    def __init__(
        self,
        actor_critic,
        num_learning_epochs=1,
        num_mini_batches=1,
        clip_param=0.2,
        gamma=0.998,
        lam=0.95,
        value_loss_coef=1.0,
        entropy_coef=0.0,
        learning_rate=1e-3,
        extra_learning_rate=1e-3,
        max_grad_norm=1.0,
        use_clipped_value_loss=True,
        schedule="fixed",
        desired_kl=0.01,
        kl_decay=0,
        device="cpu",
    ):
        self.device = device

        self.desired_kl = desired_kl
        self.kl_decay = max(kl_decay, 0)
        self.schedule = schedule
        self.learning_rate = learning_rate

        # PPO components
        self.actor_critic = actor_critic
        self.actor_critic.to(self.device)
        self.storage = None  # initialized later
        self.optimizer = optim.Adam(
            [
                {"params": self.actor_critic.actor.parameters()},
                {"params": self.actor_critic.critic.parameters()},
                {"params": self.actor_critic.std},
            ],
            lr=learning_rate,
        )
        self.extra_optimizer = None
        if self.actor_critic.is_sequence:
            self.extra_optimizer = optim.Adam(
                [
                    {"params": self.actor_critic.encoder.parameters()},
                ],
                lr=extra_learning_rate,
            )
        self.transition = RolloutStorage.Transition()

        # PPO parameters
        self.clip_param = clip_param
        self.num_learning_epochs = num_learning_epochs
        self.num_mini_batches = num_mini_batches
        self.value_loss_coef = value_loss_coef
        self.entropy_coef = entropy_coef
        self.gamma = gamma
        self.lam = lam
        self.max_grad_norm = max_grad_norm
        self.use_clipped_value_loss = use_clipped_value_loss

    def init_storage(
        self,
        num_envs,
        num_transitions_per_env,
        actor_obs_shape,
        critic_obs_shape,
        obs_history_shape,
        action_shape,
    ):
        self.storage = RolloutStorage(
            num_envs,
            num_transitions_per_env,
            actor_obs_shape,
            critic_obs_shape,
            obs_history_shape,
            action_shape,
            self.device,
        )

    def test_mode(self):
        self.actor_critic.test()

    def train_mode(self):
        self.actor_critic.train()

    def act(self, obs, obs_history, critic_obs):
        if self.actor_critic.is_recurrent:
            self.transition.hidden_states = self.actor_critic.get_hidden_states()
        # Compute the actions and values
        if self.actor_critic.is_sequence:
            self.transition.actions = self.actor_critic.act(obs, obs_history).detach()
            latent = self.actor_critic.get_latent()
            critic_obs = torch.cat((critic_obs, latent), dim=-1)
        else:
            self.transition.actions = self.actor_critic.act(obs).detach()
        self.transition.values = self.actor_critic.evaluate(critic_obs).detach()
        self.transition.actions_log_prob = self.actor_critic.get_actions_log_prob(
            self.transition.actions
        ).detach()
        self.transition.action_mean = self.actor_critic.action_mean.detach()
        self.transition.action_sigma = self.actor_critic.action_std.detach()
        # need to record obs and critic_obs before env.step()
        self.transition.observations = obs.clone()
        self.transition.observation_history = obs_history.clone()
        self.transition.critic_observations = critic_obs.clone()
        return self.transition.actions

    def process_env_step(self, rewards, dones, infos, next_obs=None):
        self.transition.rewards = rewards.clone()
        self.transition.dones = dones
        # Bootstrapping on time outs
        if "time_outs" in infos:
            self.transition.rewards += self.gamma * torch.squeeze(
                self.transition.values
                * infos["time_outs"].unsqueeze(1).to(self.device),
                1,
            )

        # Record the transition
        self.transition.next_observations = next_obs
        self.storage.add_transitions(self.transition)
        self.transition.clear()
        self.actor_critic.reset(dones)

    def compute_returns(self, last_critic_obs):
        last_values = self.actor_critic.evaluate(last_critic_obs).detach()
        self.storage.compute_returns(last_values, self.gamma, self.lam)

    def update(self):
        if self.kl_decay != 0:
            self.desired_kl = max(self.desired_kl - self.kl_decay, 0.001)
        num_updates = 0
        mean_value_loss = 0
        mean_surrogate_loss = 0
        mean_kl = 0
        if self.actor_critic.is_recurrent:
            generator = self.storage.reccurent_mini_batch_generator(
                self.num_mini_batches, self.num_learning_epochs
            )
        else:
            generator = self.storage.mini_batch_generator(
                self.num_mini_batches, self.num_learning_epochs
            )
        for (
            obs_batch,
            obs_history_batch,
            critic_obs_batch,
            actions_batch,
            target_values_batch,
            advantages_batch,
            returns_batch,
            old_actions_log_prob_batch,
            old_mu_batch,
            old_sigma_batch,
            hid_states_batch,
            masks_batch,
        ) in generator:
            if self.actor_critic.is_sequence:
                self.actor_critic.act(
                    obs_batch,
                    obs_history_batch,
                    masks=masks_batch,
                    hidden_states=hid_states_batch[0],
                )
            else:
                self.actor_critic.act(
                    obs_batch, masks=masks_batch, hidden_states=hid_states_batch[0]
                )
            actions_log_prob_batch = self.actor_critic.get_actions_log_prob(
                actions_batch
            )
            value_batch = self.actor_critic.evaluate(
                critic_obs_batch, masks=masks_batch, hidden_states=hid_states_batch[1]
            )
            mu_batch = self.actor_critic.action_mean
            sigma_batch = self.actor_critic.action_std
            entropy_batch = self.actor_critic.entropy

            # KL
            with torch.inference_mode():
                kl = torch.sum(
                    torch.log(sigma_batch / old_sigma_batch + 1.0e-5)
                    + (
                        torch.square(old_sigma_batch)
                        + torch.square(old_mu_batch - mu_batch)
                    )
                    / (2.0 * torch.square(sigma_batch))
                    - 0.5,
                    axis=-1,
                )
                kl_mean = torch.mean(kl)

                if self.desired_kl is not None and self.schedule == "adaptive":
                    if kl_mean > self.desired_kl * 2.0:
                        self.learning_rate = max(1e-5, self.learning_rate / 1.5)
                    elif kl_mean < self.desired_kl / 2.0 and kl_mean > 0.0:
                        self.learning_rate = min(1e-2, self.learning_rate * 1.5)

                    for param_group in self.optimizer.param_groups:
                        param_group["lr"] = self.learning_rate

            # Surrogate loss
            ratio = torch.exp(
                actions_log_prob_batch - torch.squeeze(old_actions_log_prob_batch)
            )
            surrogate = -torch.squeeze(advantages_batch) * ratio
            surrogate_clipped = -torch.squeeze(advantages_batch) * torch.clamp(
                ratio, 1.0 - self.clip_param, 1.0 + self.clip_param
            )
            surrogate_loss = torch.max(surrogate, surrogate_clipped).mean()

            # Value function loss
            if self.use_clipped_value_loss:
                value_clipped = target_values_batch + (
                    value_batch - target_values_batch
                ).clamp(-self.clip_param, self.clip_param)
                value_losses = (value_batch - returns_batch).pow(2)
                value_losses_clipped = (value_clipped - returns_batch).pow(2)
                value_loss = torch.max(value_losses, value_losses_clipped).mean()
            else:
                value_loss = (returns_batch - value_batch).pow(2).mean()

            loss = (
                surrogate_loss
                + self.value_loss_coef * value_loss
                - self.entropy_coef * entropy_batch.mean()
            )

            # Gradient step
            self.optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(self.actor_critic.parameters(), self.max_grad_norm)
            self.optimizer.step()

            mean_value_loss += value_loss.item()
            mean_surrogate_loss += surrogate_loss.item()
            mean_kl += kl_mean.item()
            num_updates += 1

        num_updates_extra = 0
        mean_extra_loss = 0
        if self.extra_optimizer is not None:
            generator = self.storage.encoder_mini_batch_generator(
                self.num_mini_batches, self.num_learning_epochs
            )
            for next_obs_batch, critic_obs_batch, obs_history_batch in generator:
                if self.actor_critic.is_sequence:
                    latent_batch = self.actor_critic.encode(obs_history_batch)
                    vel_est_loss = (
                        (latent_batch[:, :3] - critic_obs_batch[:, :3]).pow(2).mean()
                    )
                    if self.actor_critic.latent_dim > 3:
                        obs_denoise_loss = (
                            (
                                latent_batch[:, 3 : self.actor_critic.latent_dim]
                                - critic_obs_batch[:, 3 : self.actor_critic.latent_dim]
                            )
                            .pow(2)
                            .mean()
                        )
                        extra_loss = vel_est_loss + obs_denoise_loss
                    else:
                        extra_loss = vel_est_loss

                self.extra_optimizer.zero_grad()
                extra_loss.backward()
                nn.utils.clip_grad_norm_(self.actor_critic.parameters(), 0.1)
                self.extra_optimizer.step()

                mean_extra_loss += extra_loss.item()
                num_updates_extra += 1

        mean_value_loss /= num_updates
        mean_surrogate_loss /= num_updates
        mean_kl /= num_updates
        if num_updates_extra > 0:
            mean_extra_loss /= num_updates_extra
        self.storage.clear()

        return (mean_value_loss, mean_surrogate_loss, mean_kl, mean_extra_loss)

~~~

</details>


<details markdown="1"><summary>复旦当前 jump/utils/terrain.py</summary>

[源码](<D:/WHEEL_LEG_RL/fudan_rl_wheel_leg/jump/wheel_legged_gym/utils/terrain.py>)
~~~python
# SPDX-FileCopyrightText: Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Copyright (c) 2021 ETH Zurich, Nikita Rudin

import numpy as np
from numpy.random import choice
from scipy import interpolate

from isaacgym import terrain_utils
from wheel_legged_gym.envs.base.legged_robot_config import LeggedRobotCfg


class Terrain:
    def __init__(self, cfg: LeggedRobotCfg.terrain, num_robots) -> None:

        self.cfg = cfg
        self.num_robots = num_robots
        self.type = cfg.mesh_type
        if self.type in ["none", "plane"]:
            return
        self.env_length = cfg.terrain_length
        self.env_width = cfg.terrain_width
        self.proportions = [
            np.sum(cfg.terrain_proportions[: i + 1])
            for i in range(len(cfg.terrain_proportions))
        ]

        self.cfg.num_sub_terrains = cfg.num_rows * cfg.num_cols
        self.env_origins = np.zeros((cfg.num_rows, cfg.num_cols, 3))

        self.width_per_env_pixels = int(self.env_width / cfg.horizontal_scale)
        self.length_per_env_pixels = int(self.env_length / cfg.horizontal_scale)

        self.border = int(cfg.border_size / self.cfg.horizontal_scale)
        self.tot_cols = int(cfg.num_cols * self.width_per_env_pixels) + 2 * self.border
        self.tot_rows = int(cfg.num_rows * self.length_per_env_pixels) + 2 * self.border

        self.height_field_raw = np.zeros((self.tot_rows, self.tot_cols), dtype=np.int16)
        if cfg.curriculum:
            self.curiculum()
        elif cfg.selected:
            self.selected_terrain()
        else:
            self.randomized_terrain()

        self.heightsamples = self.height_field_raw
        if self.type == "trimesh":
            self.vertices, self.triangles = (
                terrain_utils.convert_heightfield_to_trimesh(
                    self.height_field_raw,
                    self.cfg.horizontal_scale,
                    self.cfg.vertical_scale,
                    self.cfg.slope_treshold,
                )
            )

    def randomized_terrain(self):
        for k in range(self.cfg.num_sub_terrains):
            # Env coordinates in the world
            (i, j) = np.unravel_index(k, (self.cfg.num_rows, self.cfg.num_cols))

            choice = np.random.uniform(0, 1)
            difficulty = np.random.choice([0.5, 0.75, 0.9])
            terrain = self.make_terrain(choice, difficulty)
            self.add_terrain_to_map(terrain, i, j)

    def curiculum(self):
        for j in range(self.cfg.num_cols):
            for i in range(self.cfg.num_rows):
                difficulty = i / self.cfg.num_rows
                choice = j / self.cfg.num_cols + 0.001

                terrain = self.make_terrain(choice, difficulty)
                self.add_terrain_to_map(terrain, i, j)

    def selected_terrain(self):
        terrain_type = self.cfg.terrain_kwargs.pop("type")
        for k in range(self.cfg.num_sub_terrains):
            # Env coordinates in the world
            (i, j) = np.unravel_index(k, (self.cfg.num_rows, self.cfg.num_cols))

            terrain = terrain_utils.SubTerrain(
                "terrain",
                width=self.width_per_env_pixels,
                length=self.width_per_env_pixels,
                vertical_scale=self.vertical_scale,
                horizontal_scale=self.horizontal_scale,
            )

            eval(terrain_type)(terrain, **self.cfg.terrain_kwargs.terrain_kwargs)
            self.add_terrain_to_map(terrain, i, j)

    def make_terrain(self, choice, difficulty):
        terrain = terrain_utils.SubTerrain(
            "terrain",
            width=self.width_per_env_pixels,
            length=self.width_per_env_pixels,
            vertical_scale=self.cfg.vertical_scale,
            horizontal_scale=self.cfg.horizontal_scale,
        )
        slope = difficulty * 0.5
        random_height = 0.05 + difficulty * 0.05
        step_height = 0.05 + 0.18 * difficulty
        discrete_obstacles_height = 0.05 + difficulty * 0.1
        stepping_stones_size = 1.5 * (1.05 - difficulty)
        stone_distance = 0.05 if difficulty == 0 else 0.1
        gap_size = 1.0 * difficulty
        pit_depth = 1.0 * difficulty
        if choice < self.proportions[0]:
            terrain_utils.pyramid_sloped_terrain(terrain, slope=0, platform_size=3.0)
        elif choice < self.proportions[1]:
            if (
                choice
                < self.proportions[0] + (self.proportions[1] - self.proportions[0]) / 2
            ):
                slope *= -1
            terrain_utils.pyramid_sloped_terrain(
                terrain, slope=slope, platform_size=3.0
            )
        elif choice < self.proportions[2]:
            if (
                choice
                < self.proportions[1] + (self.proportions[2] - self.proportions[1]) / 2
            ):
                slope *= -1
            terrain_utils.pyramid_sloped_terrain(
                terrain, slope=slope * 0.5, platform_size=3.0
            )
            terrain_utils.random_uniform_terrain(
                terrain,
                min_height=-random_height,
                max_height=random_height,
                step=0.005,
                downsampled_scale=0.2,
            )
        elif choice < self.proportions[4]:
            if choice < self.proportions[3]:
                step_height *= -1
            terrain_utils.pyramid_stairs_terrain(
                terrain, step_width=0.7, step_height=step_height, platform_size=4.0
            )
        elif choice < self.proportions[5]:
            num_rectangles = 20
            rectangle_min_size = 1.0
            rectangle_max_size = 2.0
            terrain_utils.discrete_obstacles_terrain(
                terrain,
                discrete_obstacles_height,
                rectangle_min_size,
                rectangle_max_size,
                num_rectangles,
                platform_size=3.0,
            )
        elif choice < self.proportions[6]:
            terrain_utils.stepping_stones_terrain(
                terrain,
                stone_size=stepping_stones_size,
                stone_distance=stone_distance,
                max_height=0.0,
                platform_size=4.0,
            )
        elif choice < self.proportions[7]:
            gap_terrain(terrain, gap_size=gap_size, platform_size=3.0)
        else:
            pit_terrain(terrain, depth=pit_depth, platform_size=4.0)

        return terrain

    def add_terrain_to_map(self, terrain, row, col):
        i = row
        j = col
        # map coordinate system
        start_x = self.border + i * self.length_per_env_pixels
        end_x = self.border + (i + 1) * self.length_per_env_pixels
        start_y = self.border + j * self.width_per_env_pixels
        end_y = self.border + (j + 1) * self.width_per_env_pixels
        self.height_field_raw[start_x:end_x, start_y:end_y] = terrain.height_field_raw

        env_origin_x = (i + 0.5) * self.env_length
        env_origin_y = (j + 0.5) * self.env_width
        x1 = int((self.env_length / 2.0 - 1) / terrain.horizontal_scale)
        x2 = int((self.env_length / 2.0 + 1) / terrain.horizontal_scale)
        y1 = int((self.env_width / 2.0 - 1) / terrain.horizontal_scale)
        y2 = int((self.env_width / 2.0 + 1) / terrain.horizontal_scale)
        env_origin_z = (
            np.max(terrain.height_field_raw[x1:x2, y1:y2]) * terrain.vertical_scale
        )
        self.env_origins[i, j] = [env_origin_x, env_origin_y, env_origin_z]


def gap_terrain(terrain, gap_size, platform_size=1.0):
    gap_size = int(gap_size / terrain.horizontal_scale)
    platform_size = int(platform_size / terrain.horizontal_scale)

    center_x = terrain.length // 2
    center_y = terrain.width // 2
    x1 = (terrain.length - platform_size) // 2
    x2 = x1 + gap_size
    y1 = (terrain.width - platform_size) // 2
    y2 = y1 + gap_size

    terrain.height_field_raw[
        center_x - x2 : center_x + x2, center_y - y2 : center_y + y2
    ] = -1000
    terrain.height_field_raw[
        center_x - x1 : center_x + x1, center_y - y1 : center_y + y1
    ] = 0


def pit_terrain(terrain, depth, platform_size=1.0):
    depth = int(depth / terrain.vertical_scale)
    platform_size = int(platform_size / terrain.horizontal_scale / 2)
    x1 = terrain.length // 2 - platform_size
    x2 = terrain.length // 2 + platform_size
    y1 = terrain.width // 2 - platform_size
    y2 = terrain.width // 2 + platform_size
    terrain.height_field_raw[x1:x2, y1:y2] = -depth
~~~

</details>


<details markdown="1"><summary>地形/历史模块 terrain.py</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/isaac/wheelleg_tasks/terrain.py>)
~~~python
from dataclasses import MISSING

import numpy as np
import trimesh
from isaaclab.terrains import SubTerrainBaseCfg
from isaaclab.utils import configclass

from wheelleg.stairs import grid_layout, step_layout


def steps_terrain(difficulty: float, cfg) -> tuple[list, np.ndarray]:
    """Flat / single / double step, with ascent and descent on each patch."""
    sx, sy = cfg.size
    mesh = trimesh.creation.box((sx, sy, 0.1))
    mesh.apply_translation((sx / 2, sy / 2, -0.05))
    meshes = [mesh]
    height = cfg.step_height_range[0] + difficulty * (cfg.step_height_range[1] - cfg.step_height_range[0])
    for level in range(cfg.step_count):  # Mesh construction, never a loop over simulation environments.
        width = (2 * (cfg.step_count - level) + 1) * cfg.step_width
        step = trimesh.creation.box((width, sy, height))
        step.apply_translation((sx / 2, sy / 2, (level + 0.5) * height))
        meshes.append(step)
    # Recovery still uses this legacy geometry. Spawn midway through its clear approach, never on a riser.
    if cfg.step_count == 0:
        return meshes, np.array((sx / 4, sy / 2, 0.0))
    edge = sx / 2 - (2 * cfg.step_count + 1) * cfg.step_width / 2
    return meshes, np.array((max(edge, 0.0) / 2, sy / 2, 0.0))


@configclass
class StepsCfg(SubTerrainBaseCfg):
    function = steps_terrain
    step_count: int = 1
    step_height_range: tuple[float, float] = MISSING
    step_width: float = MISSING


def slope_terrain(difficulty: float, cfg) -> tuple[list, np.ndarray]:
    sx, sy = cfg.size
    angle = cfg.angle_range[0] + difficulty * (cfg.angle_range[1] - cfg.angle_range[0])
    xs = np.array([0.0, sx / 4, sx / 2, 3 * sx / 4, sx])
    zs = np.array([0.0, 0.0, np.tan(angle) * sx / 4, 0.0, 0.0])
    vertices = np.array([(x, y, z) for x, z in zip(xs, zs, strict=True) for y in (0.0, sy)])
    faces = []
    for i in range(4):
        faces.extend(((2 * i, 2 * i + 2, 2 * i + 1), (2 * i + 1, 2 * i + 2, 2 * i + 3)))
    return [trimesh.Trimesh(vertices=vertices, faces=np.array(faces), process=False)], np.array((sx / 8, sy / 2, 0.0))


@configclass
class SlopeCfg(SubTerrainBaseCfg):
    function = slope_terrain
    angle_range: tuple[float, float] = MISSING


def spin_slope_terrain(difficulty: float, cfg) -> tuple[list, np.ndarray]:
    """Spawn on the slope: a stationary spinning policy must actually experience it."""
    meshes, _ = slope_terrain(difficulty, cfg)
    sx, sy = cfg.size
    angle = cfg.angle_range[0] + difficulty * (cfg.angle_range[1] - cfg.angle_range[0])
    return meshes, np.array((3 * sx / 8, sy / 2, np.tan(angle) * sx / 8))


@configclass
class SpinSlopeCfg(SlopeCfg):
    function = spin_slope_terrain


def bumps_terrain(difficulty: float, cfg) -> tuple[list, np.ndarray]:
    sx, sy = cfg.size
    ground = trimesh.creation.box((sx, sy, 0.1))
    ground.apply_translation((sx / 2, sy / 2, -0.05))
    meshes = [ground]
    height = cfg.height_range[0] + difficulty * (cfg.height_range[1] - cfg.height_range[0])
    for x in np.arange(sx / 3, 2 * sx / 3, cfg.spacing):
        bump = trimesh.creation.box((cfg.width, sy, height))
        bump.apply_translation((x, sy / 2, height / 2))
        meshes.append(bump)
    return meshes, np.array((sx / 8, sy / 2, 0.0))


@configclass
class BumpsCfg(SubTerrainBaseCfg):
    function = bumps_terrain
    height_range: tuple[float, float] = MISSING
    spacing: float = MISSING
    width: float = MISSING


def course_terrain(difficulty: float, cfg) -> tuple[list, np.ndarray]:
    """One-way traversal tiles with flat spawn/exit pads; all coordinates are tile-local metres."""
    p, profile = cfg.parameters, cfg.profile
    sx, sy = cfg.size
    meshes = []

    def box(x0, x1, y0, y1, z0, z1):
        mesh = trimesh.creation.box((x1 - x0, y1 - y0, z1 - z0))
        mesh.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
        meshes.append(mesh)

    kind = profile["kind"]
    if kind in ("up", "down", "mixed"):
        edges, heights = step_layout(p, profile, difficulty)
        boundaries = [0.0, *edges, sx]
        for start, end, height in zip(boundaries[:-1], boundaries[1:], heights, strict=True):
            box(start, end, 0, sy, -p["ground_thickness_m"], height)
        spawn_height = heights[0]
    elif kind in ("slope", "rough"):
        resolution = p["surface_resolution_m"]
        xs = np.linspace(0, sx, round(sx / resolution) + 1)
        ys = np.linspace(0, sy, round(sy / resolution) + 1)
        z = np.zeros((len(xs), len(ys)))
        surface_start, surface_end = p["surface_x_range_m"]
        inside = (xs >= surface_start) & (xs <= surface_end)
        if kind == "slope":
            angle = p["slope_angle_range_rad"][0] + difficulty * np.ptp(p["slope_angle_range_rad"])
            # Widen coverage without raising the peak at an unchanged difficulty row.
            rise_run = np.minimum(xs - surface_start, surface_end - xs).clip(0, (p["exit_x_m"] - p["entry_x_m"]) / 2)
            z[:] = (rise_run * np.tan(angle))[:, None]
        else:
            # Small uniform surface noise, clear approach and exit pads; no unsupported ray API needed.
            rng = np.random.default_rng(np.random.SeedSequence([p["seed"], round(difficulty * 1000000)]))
            amplitude = p["rough_noise_range_m"][0] + difficulty * np.ptp(p["rough_noise_range_m"])
            z[inside] = rng.uniform(-amplitude, amplitude, (inside.sum(), len(ys)))
        vertices = np.array([(x, y, z[i, j]) for i, x in enumerate(xs) for j, y in enumerate(ys)])
        faces = []
        for i in range(len(xs) - 1):
            for j in range(len(ys) - 1):
                a = i * len(ys) + j
                faces.extend(((a, a + len(ys), a + 1), (a + 1, a + len(ys), a + len(ys) + 1)))
        meshes.append(trimesh.Trimesh(vertices=vertices, faces=np.array(faces), process=False))
        spawn_height = 0.0
    else:
        box(0, sx, 0, sy, -p["ground_thickness_m"], 0)
        spawn_height = 0.0
        if kind == "grid":
            # Shared geometry keeps the training and sim2sim obstacle coverage identical.
            rectangles, height = grid_layout(p, difficulty)
            for x0, x1, y0, y1 in rectangles:
                box(x0, x1, y0, y1, 0, height)
    spawn_x = sx / 2 if profile["command_mode"] == "motion" else p["spawn_x_m"]
    return meshes, np.array((spawn_x, sy / 2, spawn_height))


@configclass
class CourseTerrainCfg(SubTerrainBaseCfg):
    function = course_terrain
    parameters: dict = MISSING
    profile: dict = MISSING

~~~

</details>


<details markdown="1"><summary>地形/历史模块 env_cfg.py</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/isaac/wheelleg_tasks/env_cfg.py>)
~~~python
from types import SimpleNamespace

import isaaclab.envs.mdp as mdp
import isaaclab.sim as sim_utils
from isaaclab.actuators import IdealPDActuatorCfg
from isaaclab.assets import ArticulationCfg
from isaaclab.envs import DirectRLEnvCfg
from isaaclab.managers import EventTermCfg, SceneEntityCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import ContactSensorCfg, RayCasterCfg, patterns
from isaaclab.terrains import HfRandomUniformTerrainCfg, TerrainGeneratorCfg, TerrainImporterCfg
from isaaclab.utils import configclass

from wheelleg.landing_rewards import FEATURES as LANDING_FEATURES
from wheelleg.stairs import FEATURES as STAIR_FEATURES
from wheelleg.training import TrainingConfig, mutable

from .events import randomize_inertia
from .terrain import BumpsCfg, CourseTerrainCfg, SlopeCfg, SpinSlopeCfg, StepsCfg


@configclass
class WheelLegEnvCfg(DirectRLEnvCfg):
    action_space = 6
    observation_space = 35
    state_space = 81
    training: TrainingConfig = None
    evaluation: bool = False
    evaluation_random_reset: bool = False
    evaluation_delay_capacity: tuple[int, int] = (0, 0)
    robot: ArticulationCfg = None
    terrain: TerrainImporterCfg = None
    contact_sensor: ContactSensorCfg = None
    height_scanner: RayCasterCfg = None
    obstacle_contact_sensors: dict[str, ContactSensorCfg] = {}


def make_env_cfg(t: TrainingConfig, num_envs: int, device: str, *, evaluation: bool = False) -> WheelLegEnvCfg:
    t.require_ready(evaluation=evaluation)
    asset, physics = t.asset, t.shared
    names = list(asset["active_joint_names"])
    # The explicit motor envelope and randomized PD run every physics step in _apply_action.
    active = IdealPDActuatorCfg(
        joint_names_expr=names,
        stiffness=0.0,
        damping=0.0,
        effort_limit={
            n: (
                t.policy.torque_limit_nm[i]
                if asset.get("reference_preset") == "scut_v14_2"
                else max(t.policy.torque_limit_nm[i], physics["saturation_torque_nm"][i])
            )
            * physics["randomization"]["hip_torque_scale" if i in t.robot.leg_indices else "wheel_torque_scale"][1]
            for i, n in enumerate(names)
        },
        armature=dict(zip(names, physics["joint_armature"], strict=True)),
        friction=dict(zip(names, physics["joint_coulomb_friction"], strict=True)),
        dynamic_friction=dict(zip(names, physics["joint_dynamic_friction"], strict=True)),
        viscous_friction=dict(zip(names, physics["joint_viscous_friction"], strict=True)),
    )
    actuators = {
        "active": active,
        "spring": IdealPDActuatorCfg(
            joint_names_expr=list(asset["spring_joint_names"]),
            stiffness=0.0,
            damping=0.0,
            effort_limit=max(physics["spring"]["force_limit_n"]),
        ),
    }
    if asset["passive_joint_names"]:
        actuators["passive"] = IdealPDActuatorCfg(
            joint_names_expr=list(asset["passive_joint_names"]),
            stiffness=0.0,
            damping=physics["passive_damping"],
            effort_limit=physics["passive_effort_limit"],
        )
    robot = ArticulationCfg(
        prim_path="/World/envs/env_.*/Robot",
        spawn=sim_utils.UsdFileCfg(
            usd_path=asset["usd_path"],
            activate_contact_sensors=True,
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=False,
                solver_position_iteration_count=physics["solver_position_iterations"],
                solver_velocity_iteration_count=physics["solver_velocity_iterations"],
            ),
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=tuple(asset["initial_root_position_m"]),
            joint_pos=mutable(asset["initial_joint_positions_rad"]),
            joint_vel={".*": 0.0},
        ),
        actuators=actuators,
    )
    if asset.get("reference_preset") == "scut_v14_2":
        # Preserve source passive/guide and gimbal actuators; replace only the six motors and springs.
        import sys

        sys.path.insert(0, asset["reference_package"])
        from agent_world.assets.wheelbipe_V14_2 import Wheelbipe_V14_2_CFG

        reference = Wheelbipe_V14_2_CFG.copy()
        reference.prim_path = robot.prim_path
        reference.spawn.usd_path = asset["usd_path"]
        reference.init_state = robot.init_state
        active.velocity_limit = {
            **reference.actuators["legs_act"].velocity_limit,
            ".*_wheel_joint": reference.actuators["wheel"].velocity_limit,
        }
        actuators["spring"].armature = reference.actuators["spring"].armature
        for name in ("legs_act", "wheel", "spring"):
            del reference.actuators[name]
        reference.actuators.update(actuators)
        robot = reference
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
        num_envs=num_envs,
        env_spacing=physics["env_spacing_m"],
        physics_material=sim_utils.RigidBodyMaterialCfg(**mutable(physics["ground_material"])),
    )
    terrain.max_init_terrain_level = 0 if not evaluation else None
    scanner = None
    if t.task == "p1-stairs":
        s = t.stage["terrain"]
        terrain.terrain_type = "generator"
        terrain.terrain_generator = TerrainGeneratorCfg(
            seed=t.settings["seed"],
            size=tuple(s["tile_size_m"]),
            num_rows=s["rows"],
            num_cols=s["columns"],
            border_width=s["border_width_m"],
            curriculum=True,
            sub_terrains={
                name: CourseTerrainCfg(proportion=p["proportion"], parameters=mutable(s), profile=mutable(p))
                for name, p in s["profiles"].items()
            },
        )
    if t.task == "p1-recovery":
        s = t.stage["terrain"]
        terrain.terrain_type = "generator"
        step_proportion = (
            1 - s["flat_proportion"] - s["slope_proportion"] - s["bump_proportion"] - s["rough_proportion"]
        ) / 2
        terrain.terrain_generator = TerrainGeneratorCfg(
            seed=t.settings["seed"],
            size=tuple(s["tile_size_m"]),
            num_rows=s["rows"],
            num_cols=s["columns"],
            border_width=s["border_width_m"],
            curriculum=not evaluation,
            sub_terrains={
                "flat": StepsCfg(
                    proportion=s["flat_proportion"],
                    step_count=0,
                    step_height_range=tuple(s["step_height_range_m"]),
                    step_width=s["step_width_m"],
                ),
                "one": StepsCfg(
                    proportion=step_proportion,
                    step_count=1,
                    step_height_range=tuple(s["step_height_range_m"]),
                    step_width=s["step_width_m"],
                ),
                "two": StepsCfg(
                    proportion=step_proportion,
                    step_count=2,
                    step_height_range=tuple(s["step_height_range_m"]),
                    step_width=s["step_width_m"],
                ),
                "slope": SlopeCfg(proportion=s["slope_proportion"], angle_range=tuple(s["slope_angle_range_rad"])),
                "bumps": BumpsCfg(
                    proportion=s["bump_proportion"],
                    height_range=tuple(s["bump_height_range_m"]),
                    spacing=s["bump_spacing_m"],
                    width=s["bump_width_m"],
                ),
                # 改自 SCUT manager/mdp/isaaclab/terrains.py:109-115 (RANDOM_UNIFORM_FOR_RM)。
                "rough": HfRandomUniformTerrainCfg(
                    proportion=s["rough_proportion"],
                    noise_range=tuple(s["rough_noise_range_m"]),
                    noise_step=s["rough_noise_step_m"],
                    downsampled_scale=s["rough_downsampled_scale_m"],
                    border_width=s["heightfield_border_width_m"],
                ),
            },
        )
    if t.task == "p2-spin":
        # SCUT terrains.py:672-699 mixes flat/low slopes/rough terrain for rotation.
        # Keep a fixed mild mixture in this task, with no displacement-based promotion.
        s = t.stage["terrain"]
        terrain.terrain_type = "generator"
        terrain.max_init_terrain_level = None
        terrain.terrain_generator = TerrainGeneratorCfg(
            seed=t.settings["seed"],
            size=tuple(s["tile_size_m"]),
            num_rows=s["rows"],
            num_cols=s["columns"],
            curriculum=True,
            border_width=s["border_width_m"],
            difficulty_range=tuple(s["difficulty_range"]),
            sub_terrains={
                "flat": StepsCfg(
                    proportion=s["flat_proportion"],
                    step_count=0,
                    step_height_range=(0.0, 0.0),
                    step_width=s["tile_size_m"][0],
                ),
                # Same noise parameters as SCUT RANDOM_UNIFORM_FOR_RM (terrains.py:109-115).
                "rough": HfRandomUniformTerrainCfg(
                    proportion=s["rough_proportion"],
                    noise_range=tuple(s["rough_noise_range_m"]),
                    noise_step=s["rough_noise_step_m"],
                    downsampled_scale=s["rough_downsampled_scale_m"],
                    border_width=s["heightfield_border_width_m"],
                ),
                "slope": SpinSlopeCfg(proportion=s["slope_proportion"], angle_range=tuple(s["slope_angle_range_rad"])),
            },
        )
    if t.task in ("p1-stairs", "p1-recovery", "p2-spin"):
        scan_size = (1.0, 0.6)
        scan_resolution = 0.1
        if t.task == "p1-stairs":
            scan_size = (2 * t.stage["course"]["scan_half_length_m"], 2 * t.stage["course"]["scan_half_width_m"])
            scan_resolution = t.stage["course"]["scan_resolution_m"]
        scanner = RayCasterCfg(
            prim_path=f"/World/envs/env_.*/Robot/{asset['base_body_name']}",
            offset=RayCasterCfg.OffsetCfg(pos=(0.0, 0.0, 20.0)),
            ray_alignment="yaw",
            pattern_cfg=patterns.GridPatternCfg(resolution=scan_resolution, size=scan_size),
            mesh_prim_paths=["/World/ground"],
            debug_vis=False,
        )
    cfg = WheelLegEnvCfg(
        training=t,
        evaluation=evaluation,
        seed=t.settings["seed"],
        decimation=t.robot.decimation,
        episode_length_s=t.stage["course"]["episode_length_s"]
        if t.task == "p1-stairs"
        else t.settings["episode_length_s"],
        sim=sim_utils.SimulationCfg(
            dt=1 / t.robot.control_hz,
            render_interval=t.robot.decimation,
            device=device,
            gravity=(0.0, 0.0, -physics["gravity_m_s2"]),
        ),
        scene=InteractiveSceneCfg(num_envs=num_envs, env_spacing=physics["env_spacing_m"], replicate_physics=True),
        robot=robot,
        terrain=terrain,
        contact_sensor=ContactSensorCfg(
            prim_path="/World/envs/env_.*/Robot/.*", history_length=3, update_period=0.0, track_air_time=True
        ),
        height_scanner=scanner,
        state_space=(
            (81 + round(scan_size[0] / scan_resolution + 1) * round(scan_size[1] / scan_resolution + 1))
            if scanner
            else 81
        )
        + (LANDING_FEATURES if t.task == "p1-landing" else 0)
        + (STAIR_FEATURES if t.task == "p1-stairs" else 0),
    )
    if t.task == "p3-tunnel":
        # contact_sensor_cfg.py:63-68: one sensing body per environment, not Robot/.*.
        cfg.obstacle_contact_sensors = {
            name: ContactSensorCfg(
                prim_path=f"/World/envs/env_.*/Robot/{name}",
                update_period=0.0,
                history_length=0,
                filter_prim_paths_expr=[
                    f"/World/envs/env_.*/{target}" for target in ("TunnelBeam", "RailLeft", "RailRight")
                ],
            )
            for name in asset["collision_body_names"]
        }
    if not evaluation:
        r = physics["randomization"]
        base = SceneEntityCfg("robot", body_names=[asset["base_body_name"]])
        limb_pattern = f"(?!{asset['base_body_name']}$).*"
        cfg.events = SimpleNamespace(
            base_mass=EventTermCfg(
                func=mdp.randomize_rigid_body_mass,
                mode="startup",
                params={
                    "asset_cfg": base,
                    "mass_distribution_params": tuple(r["base_mass_scale"]),
                    "operation": "scale",
                },
            ),
            limb_mass=EventTermCfg(
                func=mdp.randomize_rigid_body_mass,
                mode="startup",
                params={
                    "asset_cfg": SceneEntityCfg("robot", body_names=[limb_pattern]),
                    "mass_distribution_params": tuple(r["limb_mass_scale"]),
                    "operation": "scale",
                },
            ),
            inertia=EventTermCfg(
                func=randomize_inertia, mode="startup", params={"scale_range": tuple(r["inertia_scale"])}
            ),
            com=EventTermCfg(
                func=mdp.randomize_rigid_body_com,
                mode="startup",
                params={
                    "asset_cfg": base,
                    "com_range": {k: (-v, v) for k, v in zip("xyz", r["com_offset_m"], strict=True)},
                },
            ),
            material=EventTermCfg(
                func=mdp.randomize_rigid_body_material,
                mode="startup",
                params={
                    "asset_cfg": SceneEntityCfg("robot", body_names=list(asset["wheel_body_names"])),
                    "static_friction_range": tuple(r["static_friction"]),
                    "dynamic_friction_range": tuple(r["dynamic_friction"]),
                    "restitution_range": tuple(r["restitution"]),
                    "num_buckets": 64,
                    "make_consistent": True,
                },
            ),
        )
        # 改自 SCUT V14/env_cfg.py:136-159: 机身、导轮等非轮子刚体的摩擦。按配置条目循环，不是按环境循环。
        for i, entry in enumerate(r["body_materials"]):
            setattr(
                cfg.events,
                f"body_material_{i}",
                EventTermCfg(
                    func=mdp.randomize_rigid_body_material,
                    mode="startup",
                    params={
                        "asset_cfg": SceneEntityCfg("robot", body_names=list(entry["body_names"])),
                        "static_friction_range": tuple(entry["static_friction"]),
                        "dynamic_friction_range": tuple(entry["dynamic_friction"]),
                        "restitution_range": tuple(entry["restitution"]),
                        "num_buckets": entry["buckets"],
                        "make_consistent": True,
                    },
                ),
            )
    return cfg

~~~

</details>


<details markdown="1"><summary>地形/历史模块 history_policy.py</summary>

[源码](<D:/WHEEL_LEG_RL/SRM_Wheelleg_Rltrain/isaac/wheelleg_tasks/history_policy.py>)
~~~python
"""rsl_rl 3.1.2 integration of the optional history estimator (wheelleg/history.py).

The rollout storage keeps every observation group returned by the environment, so the history and the
estimator target ride along with PPO's own data. PPO never back-propagates into the estimator: the actor
sees a detached estimate, and the estimator is fitted separately after each PPO update on the same batch.
"""

import torch
from rsl_rl.algorithms import PPO
from rsl_rl.modules import ActorCritic
from rsl_rl.networks import MLP
from tensordict import TensorDict
from torch import nn

from wheelleg.history import ESTIMATE_DIM, HistoryEstimator, estimator_loss


class HistoryActorCritic(ActorCritic):
    def __init__(
        self,
        obs: TensorDict,
        obs_groups: dict[str, list[str]],
        num_actions: int,
        history_frames: int,
        estimator_hidden_dims: list[int],
        **kwargs,
    ) -> None:
        super().__init__(obs, obs_groups, num_actions, **kwargs)
        if self.actor_obs_normalization or self.state_dependent_std:
            raise ValueError("The history policy supports neither actor normalization nor state-dependent std")
        inputs = sum(obs[group].shape[-1] for group in obs_groups["policy"]) + ESTIMATE_DIM
        self.actor = MLP(inputs, num_actions, kwargs["actor_hidden_dims"], kwargs["activation"])
        self.estimator = HistoryEstimator(history_frames, estimator_hidden_dims)

    def get_actor_obs(self, obs: TensorDict) -> torch.Tensor:
        return torch.cat((super().get_actor_obs(obs), self.estimator.features(obs["history"]).detach()), -1)


class HistoryPPO(PPO):
    def __init__(
        self,
        policy: HistoryActorCritic,
        estimator_learning_rate: float,
        velocity_loss_coef: float,
        contact_loss_coef: float,
        **kwargs,
    ) -> None:
        super().__init__(policy, **kwargs)
        if self.is_multi_gpu:
            raise NotImplementedError("The history estimator update is single-GPU only")
        self.estimator_optimizer = torch.optim.Adam(policy.estimator.parameters(), lr=estimator_learning_rate)
        self.velocity_loss_coef = velocity_loss_coef
        self.contact_loss_coef = contact_loss_coef

    def update(self) -> dict[str, float]:
        # PPO.update clears the storage, so keep this rollout's estimator data first.
        observations = self.storage.observations.flatten(0, 1)
        history = observations["history"].clone()
        target = observations["estimator_target"].clone()
        loss_dict = super().update()
        estimator = self.policy.estimator
        count = history.shape[0]
        size = count // self.num_mini_batches
        sums = torch.zeros(2, device=history.device)
        for _ in range(self.num_learning_epochs):
            order = torch.randperm(count, device=history.device)
            for i in range(self.num_mini_batches):
                index = order[i * size : (i + 1) * size]
                loss, velocity, contact = estimator_loss(
                    estimator(history[index]), target[index], self.velocity_loss_coef, self.contact_loss_coef
                )
                self.estimator_optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(estimator.parameters(), self.max_grad_norm)
                self.estimator_optimizer.step()
                sums += torch.stack((velocity.detach(), contact.detach()))
        sums /= self.num_learning_epochs * self.num_mini_batches
        loss_dict["estimator_velocity"] = sums[0].item()
        loss_dict["estimator_contact"] = sums[1].item()
        return loss_dict

~~~

</details>


<details markdown="1"><summary>地形/历史模块 height_field.py</summary>

[源码](<D:/WHEEL_LEG_RL/wheeled-legged_RL/source/agent_world/agent_world/terrains/height_field.py>)
~~~python
# =============================================================================
# Copyright (c) 2026 SCUTRobotLab
# SPDX-License-Identifier: MIT
#
# Part of the wheeled-legged_RL project.
# See LICENSE for full license terms.
#
# Authors:
#     Zhang Zhirui <2231625449@qq.com>
#     Cui Yu       <ctty694@gmail.com>
# =============================================================================

from __future__ import annotations

import os
from dataclasses import MISSING
from collections.abc import Mapping

import numpy as np
import scipy.interpolate as interpolate
import trimesh

from isaaclab.terrains import HfTerrainBaseCfg, SubTerrainBaseCfg
from isaaclab.terrains.height_field.utils import height_field_to_mesh
from isaaclab.utils import configclass


def discretize_size_to_pixels(size: float, scale: float) -> int:
    """Convert a metric size to a discrete height-field resolution robustly."""

    return int(np.round(size / scale))


def _resolve_fixed_or_difficulty_value(
    fixed_value: float | None,
    value_range: tuple[float, float] | None,
    difficulty: float,
    name: str,
) -> float:
    """Resolve a terrain parameter from a fixed value or a difficulty-interpolated range."""

    if fixed_value is not None:
        return float(fixed_value)
    if value_range is None:
        raise ValueError(f"Either '{name}' or '{name}_range' must be specified.")
    lower, upper = value_range
    if lower > upper:
        raise ValueError(f"The range for '{name}' must satisfy lower <= upper. Got: {value_range}.")
    return float(lower + difficulty * (upper - lower))


def _resolve_fixed_or_difficulty_int(
    fixed_value: int | None,
    value_range: tuple[int, int] | None,
    difficulty: float,
    name: str,
) -> int:
    """Resolve an integer terrain parameter from a fixed value or a difficulty-interpolated range."""

    if fixed_value is not None:
        return int(fixed_value)
    if value_range is None:
        raise ValueError(f"Either '{name}' or '{name}_range' must be specified.")
    lower, upper = value_range
    if lower > upper:
        raise ValueError(f"The range for '{name}' must satisfy lower <= upper. Got: {value_range}.")
    return int(np.rint(lower + difficulty * (upper - lower)))


_FOUR_QUADRANT_KEYS = ("front_left", "front_right", "rear_left", "rear_right")


def _resolve_four_quadrant_cfgs(cfg: "FourQuadrantTerrainCfg") -> dict[str, SubTerrainBaseCfg]:
    """Resolve a single terrain cfg or a partial quadrant mapping into four quadrant cfgs."""

    quadrants = cfg.quadrants
    if isinstance(quadrants, SubTerrainBaseCfg):
        return {key: quadrants for key in _FOUR_QUADRANT_KEYS}
    if not isinstance(quadrants, Mapping) or len(quadrants) == 0:
        raise ValueError("'quadrants' must be a SubTerrainBaseCfg or a non-empty mapping.")

    default_cfg = cfg.default_quadrant
    if default_cfg is None:
        default_cfg = next(iter(quadrants.values()))
    return {key: quadrants.get(key, default_cfg) for key in _FOUR_QUADRANT_KEYS}


def four_quadrant_terrain(
    difficulty: float, cfg: "FourQuadrantTerrainCfg"
) -> tuple[list[trimesh.Trimesh], np.ndarray]:
    """Generate a terrain tile split into four independently configured quadrants."""

    size_x, size_y = float(cfg.size[0]), float(cfg.size[1])
    sub_size = (0.5 * size_x, 0.5 * size_y)
    offsets = {
        "rear_left": (0.0, 0.0),
        "rear_right": (sub_size[0], 0.0),
        "front_left": (0.0, sub_size[1]),
        "front_right": (sub_size[0], sub_size[1]),
    }
    quadrant_cfgs = _resolve_four_quadrant_cfgs(cfg)

    meshes_list: list[trimesh.Trimesh] = []
    origin_z_values: list[float] = []
    for key in _FOUR_QUADRANT_KEYS:
        sub_cfg = quadrant_cfgs[key].copy()
        sub_cfg.size = sub_size
        sub_meshes, sub_origin = sub_cfg.function(difficulty, sub_cfg)
        transform = np.eye(4)
        transform[0, -1], transform[1, -1] = offsets[key]
        for mesh in sub_meshes:
            mesh = mesh.copy()
            mesh.apply_transform(transform)
            meshes_list.append(mesh)
        if sub_origin is not None and len(sub_origin) >= 3:
            origin_z_values.append(float(sub_origin[2]))

    origin = np.asarray(
        [0.5 * size_x, 0.5 * size_y, max(origin_z_values) if origin_z_values else 0.0],
        dtype=float,
    )
    return meshes_list, origin


@configclass
class FourQuadrantTerrainCfg(SubTerrainBaseCfg):
    """Configuration for a tile split into four equal terrain quadrants."""

    function = four_quadrant_terrain

    quadrants: SubTerrainBaseCfg | dict[str, SubTerrainBaseCfg] = MISSING
    """Single terrain cfg for all quadrants, or a mapping keyed by front/rear + left/right."""

    default_quadrant: SubTerrainBaseCfg | None = None
    """Fallback cfg for missing quadrant keys. Defaults to the first mapping value."""


def _resolve_int_bounds(
    fixed_value: int | None,
    value_range: tuple[int, int] | None,
    name: str,
) -> tuple[int, int]:
    """Return the valid integer bounds for a fixed-or-ranged count parameter."""

    if fixed_value is not None:
        value = int(fixed_value)
        return value, value
    if value_range is None:
        raise ValueError(f"Either '{name}' or '{name}_range' must be specified.")
    lower, upper = value_range
    if lower > upper:
        raise ValueError(f"The range for '{name}' must satisfy lower <= upper. Got: {value_range}.")
    return int(lower), int(upper)


def _force_even_count(
    value: int,
    fixed_value: int | None,
    value_range: tuple[int, int] | None,
    name: str,
) -> int:
    """Adjust an odd resolved count to the nearest valid even count."""

    if value % 2 == 0:
        return value

    lower, upper = _resolve_int_bounds(fixed_value, value_range, name)
    candidates = [candidate for candidate in (value + 1, value - 1) if lower <= candidate <= upper]
    if candidates:
        return int(candidates[0])

    raise ValueError(
        f"'force_even_counts' requires '{name}' to resolve to an even value or have an adjacent even value within"
        f" its range. Got resolved value {value} with bounds ({lower}, {upper})."
    )


def _resolve_height_offset_curriculum(
    difficulty: float, cfg: "HfCliffInvertedPyramidStairsTerrainCfg"
) -> tuple[float, float]:
    """Resolve row-bucket scale and local interpolation difficulty for height offsets."""

    if not cfg.height_offset_curriculum_scale_by_difficulty:
        return 1.0, difficulty

    num_levels = max(int(cfg.height_offset_curriculum_num_levels), 1)
    if num_levels <= 1:
        return 1.0, difficulty

    clipped_difficulty = float(np.clip(difficulty, 0.0, 1.0))
    scaled_difficulty = clipped_difficulty * num_levels
    level = int(np.floor(scaled_difficulty))
    level = int(np.clip(level, 0, num_levels - 1))
    local_difficulty = float(np.clip(scaled_difficulty - level, 0.0, 1.0))
    return float(level) / float(num_levels - 1), local_difficulty


@height_field_to_mesh
def import_custom_npy_terrain(difficulty: float, cfg: "HfCustomNpyTerrainCfg") -> np.ndarray:
    """Load a custom height field from an NPY file."""

    del difficulty

    if not os.path.exists(cfg.npy_path):
        raise FileNotFoundError(f"Height field file not found: {cfg.npy_path}")

    height_field_raw = np.load(cfg.npy_path).astype(np.float32)

    width_pixels = discretize_size_to_pixels(cfg.size[0], cfg.horizontal_scale)
    length_pixels = discretize_size_to_pixels(cfg.size[1], cfg.horizontal_scale)

    x_src = np.linspace(0.0, 1.0, height_field_raw.shape[0])
    y_src = np.linspace(0.0, 1.0, height_field_raw.shape[1])
    interp_func = interpolate.RectBivariateSpline(x_src, y_src, height_field_raw)
    x_dst = np.linspace(0.0, 1.0, width_pixels)
    y_dst = np.linspace(0.0, 1.0, length_pixels)
    height_field_resized = interp_func(x_dst, y_dst)

    return np.rint(height_field_resized / cfg.vertical_scale).astype(np.int16)


@configclass
class HfCustomNpyTerrainCfg(HfTerrainBaseCfg):
    """Configuration for loading a custom NPY height field."""

    function = import_custom_npy_terrain

    npy_path: str = MISSING
    """Absolute or relative path to the NPY height field file."""


def _symmetric_bar_centers(count: int, lower: float, upper: float, bar_width: float, name: str) -> np.ndarray:
    """Return bar centers with equal clear gaps and symmetric side margins."""

    if count <= 0:
        return np.zeros((0,), dtype=np.float32)
    usable_width = upper - lower
    if usable_width <= 0.0:
        raise ValueError(f"No usable terrain span for {name}: lower={lower}, upper={upper}.")
    if count * bar_width > usable_width:
        raise ValueError(
            f"{count} '{name}' bars with bar_width ({bar_width}) exceed the usable span ({usable_width})."
        )

    if count == 1:
        return np.array([(lower + upper) * 0.5], dtype=np.float32)
    gap = (usable_width - count * bar_width) / (count + 1)
    first_center = lower + gap + 0.5 * bar_width
    center_step = bar_width + gap
    return (first_center + np.arange(count, dtype=np.float32) * center_step).astype(np.float32)


def _centered_fraction_span(lower: float, upper: float, fraction: float, name: str) -> tuple[float, float]:
    """Return a centered sub-span covering a fraction of the input span."""

    if not 0.0 < fraction <= 1.0:
        raise ValueError(f"'{name}' must be in (0, 1]. Got: {fraction}.")
    span = upper - lower
    if span <= 0.0:
        raise ValueError(f"No usable span for {name}: lower={lower}, upper={upper}.")
    margin = 0.5 * span * (1.0 - fraction)
    return lower + margin, upper - margin


def _resolve_grid_bars_params(
    difficulty: float,
    cfg: "HfCustomGridBarsTerrainCfg | MeshCustomGridBarsTerrainCfg | MeshCustomSplitGridBarsTerrainCfg",
) -> tuple[int, int, float, float]:
    """Resolve and validate common grid-bar terrain parameters."""

    horizontal_count_difficulty = difficulty
    vertical_count_difficulty = difficulty
    if getattr(cfg, "randomize_bar_count_difficulty", False):
        horizontal_count_difficulty = float(np.random.uniform(0.0, 1.0))
        vertical_count_difficulty = float(np.random.uniform(0.0, 1.0))

    width_difficulty = difficulty
    if getattr(cfg, "randomize_bar_width_difficulty", False):
        width_difficulty = float(np.random.uniform(0.0, 1.0))

    num_horizontal = _resolve_fixed_or_difficulty_int(
        cfg.num_horizontal, cfg.num_horizontal_range, horizontal_count_difficulty, "num_horizontal"
    )
    num_vertical = _resolve_fixed_or_difficulty_int(
        cfg.num_vertical, cfg.num_vertical_range, vertical_count_difficulty, "num_vertical"
    )
    force_even_counts = bool(getattr(cfg, "force_even_counts", False))
    if force_even_counts:
        num_horizontal = _force_even_count(
            num_horizontal, cfg.num_horizontal, cfg.num_horizontal_range, "num_horizontal"
        )
        num_vertical = _force_even_count(num_vertical, cfg.num_vertical, cfg.num_vertical_range, "num_vertical")

    if getattr(cfg, "force_unequal_counts", False) and num_horizontal == num_vertical:
        vertical_min, vertical_max = _resolve_int_bounds(cfg.num_vertical, cfg.num_vertical_range, "num_vertical")
        horizontal_min, horizontal_max = _resolve_int_bounds(
            cfg.num_horizontal, cfg.num_horizontal_range, "num_horizontal"
        )
        count_step = 2 if force_even_counts else 1
        if num_vertical + count_step <= vertical_max:
            num_vertical += count_step
        elif num_vertical - count_step >= vertical_min:
            num_vertical -= count_step
        elif num_horizontal + count_step <= horizontal_max:
            num_horizontal += count_step
        elif num_horizontal - count_step >= horizontal_min:
            num_horizontal -= count_step
        else:
            raise ValueError(
                "'force_unequal_counts' requires at least one count range that can change the resolved value."
            )
    bar_width = _resolve_fixed_or_difficulty_value(cfg.bar_width, cfg.bar_width_range, width_difficulty, "bar_width")
    bar_height = _resolve_fixed_or_difficulty_value(cfg.bar_height, cfg.bar_height_range, difficulty, "bar_height")

    if num_horizontal < 0:
        raise ValueError(f"'num_horizontal' must be non-negative. Got: {num_horizontal}.")
    if num_vertical < 0:
        raise ValueError(f"'num_vertical' must be non-negative. Got: {num_vertical}.")
    if num_horizontal == 0 and num_vertical == 0:
        raise ValueError("At least one of 'num_horizontal' or 'num_vertical' must be positive.")
    if bar_width <= 0.0:
        raise ValueError(f"'bar_width' must be positive. Got: {bar_width}.")
    if bar_height < 0.0:
        raise ValueError(f"'bar_height' must be non-negative. Got: {bar_height}.")

    return num_horizontal, num_vertical, bar_width, bar_height


@height_field_to_mesh
def grid_bars_terrain(difficulty: float, cfg: "HfCustomGridBarsTerrainCfg") -> np.ndarray:
    """Generate a centered hash/grid terrain made from horizontal and vertical rectangular bars."""

    num_horizontal, num_vertical, bar_width, bar_height = _resolve_grid_bars_params(difficulty, cfg)
    width_pixels = discretize_size_to_pixels(cfg.size[0], cfg.horizontal_scale)
    length_pixels = discretize_size_to_pixels(cfg.size[1], cfg.horizontal_scale)
    bar_height_pixels = int(np.rint(bar_height / cfg.vertical_scale))

    hf_raw = np.zeros((width_pixels, length_pixels), dtype=np.float32)

    # ``height_field_to_mesh`` handles cfg.border_width by shrinking cfg.size before calling this function.
    x_lower, x_upper = 0.0, float(cfg.size[0])
    y_lower, y_upper = 0.0, float(cfg.size[1])
    x_bar_lower, x_bar_upper = _centered_fraction_span(
        x_lower, x_upper, float(getattr(cfg, "bar_length_ratio", 0.95)), "bar_length_ratio"
    )
    y_bar_lower, y_bar_upper = _centered_fraction_span(
        y_lower, y_upper, float(getattr(cfg, "bar_length_ratio", 0.95)), "bar_length_ratio"
    )

    x_positions = (np.arange(width_pixels, dtype=np.float32) + 0.5) * cfg.horizontal_scale
    y_positions = (np.arange(length_pixels, dtype=np.float32) + 0.5) * cfg.horizontal_scale
    x_center_inside = (x_positions >= x_lower) & (x_positions < x_upper)
    y_center_inside = (y_positions >= y_lower) & (y_positions < y_upper)
    x_bar_inside = (x_positions >= x_bar_lower) & (x_positions < x_bar_upper)
    y_bar_inside = (y_positions >= y_bar_lower) & (y_positions < y_bar_upper)

    horizontal_centers = _symmetric_bar_centers(num_horizontal, y_lower, y_upper, bar_width, "horizontal")
    vertical_centers = _symmetric_bar_centers(num_vertical, x_lower, x_upper, bar_width, "vertical")
    half_width = 0.5 * bar_width

    def _bar_mask(positions: np.ndarray, inside: np.ndarray, center: float) -> np.ndarray:
        mask = (np.abs(positions - center) <= half_width) & inside
        if not mask.any():
            inside_indices = np.flatnonzero(inside)
            if inside_indices.size > 0:
                nearest_idx = inside_indices[np.argmin(np.abs(positions[inside_indices] - center))]
                mask[nearest_idx] = True
        return mask

    for center_y in horizontal_centers:
        y_mask = _bar_mask(y_positions, y_center_inside, center_y)
        hf_raw[np.ix_(x_bar_inside, y_mask)] = np.maximum(
            hf_raw[np.ix_(x_bar_inside, y_mask)], bar_height_pixels
        )

    for center_x in vertical_centers:
        x_mask = _bar_mask(x_positions, x_center_inside, center_x)
        hf_raw[np.ix_(x_mask, y_bar_inside)] = np.maximum(
            hf_raw[np.ix_(x_mask, y_bar_inside)], bar_height_pixels
        )

    return np.rint(hf_raw).astype(np.int16)


@configclass
class HfCustomGridBarsTerrainCfg(HfTerrainBaseCfg):
    """Configuration for a centered grid of rectangular bars."""

    function = grid_bars_terrain

    num_horizontal: int | None = None
    """Fixed number of horizontal bars running along the terrain x direction."""

    num_horizontal_range: tuple[int, int] | None = None
    """Difficulty-interpolated range for the number of horizontal bars."""

    num_vertical: int | None = None
    """Fixed number of vertical bars running along the terrain y direction."""

    num_vertical_range: tuple[int, int] | None = None
    """Difficulty-interpolated range for the number of vertical bars."""

    randomize_bar_count_difficulty: bool = False
    """Whether to use independent random difficulties for horizontal and vertical bar counts."""

    force_unequal_counts: bool = False
    """Whether to force horizontal and vertical bar counts to be different after interpolation."""

    force_even_counts: bool = False
    """Whether to force horizontal and vertical bar counts to even values after interpolation."""

    bar_width: float | None = None
    """Fixed bar width in meters."""

    bar_width_range: tuple[float, float] | None = None
    """Difficulty-interpolated range for bar width in meters."""

    randomize_bar_width_difficulty: bool = False
    """Whether to use a random difficulty for bar width instead of the incoming terrain difficulty."""

    bar_height: float | None = None
    """Fixed bar height in meters."""

    bar_height_range: tuple[float, float] | None = None
    """Difficulty-interpolated range for bar height in meters."""

    bar_length_ratio: float = 0.95
    """Fraction of the terrain span covered by each bar along its long direction."""


def mesh_grid_bars_terrain(
    difficulty: float, cfg: "MeshCustomGridBarsTerrainCfg"
) -> tuple[list[trimesh.Trimesh], np.ndarray]:
    """Generate a centered grid terrain from rectangular bar meshes.

    Vertical bars are kept as full-length boxes. Horizontal bars are split at
    vertical-bar spans so the intersection is occupied by one box only instead
    of two overlapping boxes. This keeps the top-down shape equivalent to
    max-compositing while avoiding duplicate coplanar contact surfaces.
    """

    num_horizontal, num_vertical, bar_width, bar_height = _resolve_grid_bars_params(difficulty, cfg)
    if cfg.ground_thickness < 0.0:
        raise ValueError(f"'ground_thickness' must be non-negative. Got: {cfg.ground_thickness}.")

    x_lower, x_upper = 0.0, float(cfg.size[0])
    y_lower, y_upper = 0.0, float(cfg.size[1])
    x_bar_lower, x_bar_upper = _centered_fraction_span(x_lower, x_upper, cfg.bar_length_ratio, "bar_length_ratio")
    y_bar_lower, y_bar_upper = _centered_fraction_span(y_lower, y_upper, cfg.bar_length_ratio, "bar_length_ratio")
    horizontal_centers = _symmetric_bar_centers(num_horizontal, y_lower, y_upper, bar_width, "horizontal")
    vertical_centers = _symmetric_bar_centers(num_vertical, x_lower, x_upper, bar_width, "vertical")

    meshes_list = []

    def _append_box(dims: tuple[float, float, float], pos: tuple[float, float, float]) -> None:
        transform = trimesh.transformations.translation_matrix(pos)
        meshes_list.append(trimesh.creation.box(dims, transform))

    if cfg.ground_thickness > 0.0:
        dims = (cfg.size[0], cfg.size[1], cfg.ground_thickness)
        pos = (0.5 * cfg.size[0], 0.5 * cfg.size[1], -0.5 * cfg.ground_thickness)
        _append_box(dims, pos)

    vertical_spans = [
        (
            max(x_bar_lower, float(center_x) - 0.5 * bar_width),
            min(x_bar_upper, float(center_x) + 0.5 * bar_width),
        )
        for center_x in vertical_centers
    ]
    vertical_spans = [(span_start, span_end) for span_start, span_end in vertical_spans if span_end > span_start]
    vertical_spans.sort()

    for center_y in horizontal_centers:
        segment_start = x_bar_lower
        for span_start, span_end in vertical_spans:
            segment_end = min(max(span_start, segment_start), x_bar_upper)
            segment_length = segment_end - segment_start
            if segment_length > 1.0e-6:
                dims = (segment_length, bar_width, bar_height)
                pos = (segment_start + 0.5 * segment_length, float(center_y), 0.5 * bar_height)
                _append_box(dims, pos)
            segment_start = max(segment_start, min(max(span_end, x_bar_lower), x_bar_upper))
        segment_length = x_bar_upper - segment_start
        if segment_length > 1.0e-6:
            dims = (segment_length, bar_width, bar_height)
            pos = (segment_start + 0.5 * segment_length, float(center_y), 0.5 * bar_height)
            _append_box(dims, pos)

    for center_x in vertical_centers:
        v_length = y_bar_upper - y_bar_lower
        dims = (bar_width, v_length, bar_height)
        pos = (float(center_x), y_bar_lower + 0.5 * v_length, 0.5 * bar_height)
        _append_box(dims, pos)

    origin = np.asarray([0.5 * cfg.size[0], 0.5 * cfg.size[1], bar_height])
    return meshes_list, origin


def mesh_split_grid_bars_terrain(
    difficulty: float, cfg: "MeshCustomSplitGridBarsTerrainCfg"
) -> tuple[list[trimesh.Trimesh], np.ndarray]:
    """Generate a split terrain with horizontal bars on one half and vertical bars on the other.

    This keeps the same bar count/width/height randomization as
    ``MeshCustomGridBarsTerrainCfg`` but avoids cross intersections entirely:
    one side of the tile contains only bars running along x, and the other side
    contains only bars running along y.
    """

    num_horizontal, num_vertical, bar_width, bar_height = _resolve_grid_bars_params(difficulty, cfg)
    if cfg.ground_thickness < 0.0:
        raise ValueError(f"'ground_thickness' must be non-negative. Got: {cfg.ground_thickness}.")

    split_ratio = float(cfg.split_ratio)
    if not 0.0 < split_ratio < 1.0:
        raise ValueError(f"'split_ratio' must be in (0, 1). Got: {split_ratio}.")

    split_side = str(np.random.choice(("x", "-x", "y", "-y"))) if bool(cfg.randomize_side) else None
    if split_side is None:
        split_axis = str(cfg.split_axis).lower().replace("+", "")
        if split_axis not in ("x", "-x", "y", "-y"):
            raise ValueError(f"'split_axis' must be one of 'x', '-x', 'y', '-y'. Got: {cfg.split_axis!r}.")
        if split_axis.startswith("-"):
            split_side = split_axis
        else:
            horizontal_side = str(cfg.horizontal_side).lower()
            if horizontal_side not in ("negative", "positive"):
                raise ValueError(f"'horizontal_side' must be 'negative' or 'positive'. Got: {cfg.horizontal_side!r}.")
            split_side = f"-{split_axis}" if horizontal_side == "negative" else split_axis

    x_lower, x_upper = 0.0, float(cfg.size[0])
    y_lower, y_upper = 0.0, float(cfg.size[1])
    x_span = x_upper - x_lower
    y_span = y_upper - y_lower

    if split_side == "-x":
        x_split = x_lower + split_ratio * x_span
        horizontal_region = (x_lower, x_split, y_lower, y_upper)
        vertical_region = (x_split, x_upper, y_lower, y_upper)
    elif split_side == "x":
        x_split = x_upper - split_ratio * x_span
        horizontal_region = (x_split, x_upper, y_lower, y_upper)
        vertical_region = (x_lower, x_split, y_lower, y_upper)
    elif split_side == "-y":
        y_split = y_lower + split_ratio * y_span
        vertical_region = (x_lower, x_upper, y_lower, y_split)
        horizontal_region = (x_lower, x_upper, y_split, y_upper)
    elif split_side == "y":
        y_split = y_upper - split_ratio * y_span
        vertical_region = (x_lower, x_upper, y_split, y_upper)
        horizontal_region = (x_lower, x_upper, y_lower, y_split)
    else:
        raise ValueError(f"'split_side' must be one of 'x', '-x', 'y', '-y'. Got: {split_side!r}.")

    # For y-splits the selected split_ratio side is vertical bars, so rotate the count concepts too.
    if split_side in ("y", "-y"):
        num_horizontal, num_vertical = num_vertical, num_horizontal

    meshes_list = []

    def _append_box(dims: tuple[float, float, float], pos: tuple[float, float, float]) -> None:
        transform = trimesh.transformations.translation_matrix(pos)
        meshes_list.append(trimesh.creation.box(dims, transform))

    if cfg.ground_thickness > 0.0:
        dims = (cfg.size[0], cfg.size[1], cfg.ground_thickness)
        pos = (0.5 * cfg.size[0], 0.5 * cfg.size[1], -0.5 * cfg.ground_thickness)
        _append_box(dims, pos)

    h_x_lower, h_x_upper, h_y_lower, h_y_upper = horizontal_region
    h_bar_x_lower, h_bar_x_upper = _centered_fraction_span(
        h_x_lower, h_x_upper, cfg.bar_length_ratio, "bar_length_ratio"
    )
    h_length = h_bar_x_upper - h_bar_x_lower
    horizontal_centers = _symmetric_bar_centers(num_horizontal, h_y_lower, h_y_upper, bar_width, "horizontal")
    for center_y in horizontal_centers:
        dims = (h_length, bar_width, bar_height)
        pos = (h_bar_x_lower + 0.5 * h_length, float(center_y), 0.5 * bar_height)
        _append_box(dims, pos)

    v_x_lower, v_x_upper, v_y_lower, v_y_upper = vertical_region
    v_bar_y_lower, v_bar_y_upper = _centered_fraction_span(
        v_y_lower, v_y_upper, cfg.bar_length_ratio, "bar_length_ratio"
    )
    v_length = v_bar_y_upper - v_bar_y_lower
    vertical_centers = _symmetric_bar_centers(num_vertical, v_x_lower, v_x_upper, bar_width, "vertical")
    for center_x in vertical_centers:
        dims = (bar_width, v_length, bar_height)
        pos = (float(center_x), v_bar_y_lower + 0.5 * v_length, 0.5 * bar_height)
        _append_box(dims, pos)

    origin = np.asarray([0.5 * cfg.size[0], 0.5 * cfg.size[1], bar_height])
    return meshes_list, origin


@configclass
class MeshCustomGridBarsTerrainCfg(SubTerrainBaseCfg):
    """Configuration for a centered grid of rectangular bars generated as box meshes."""

    function = mesh_grid_bars_terrain

    num_horizontal: int | None = None
    """Fixed number of horizontal bars running along the terrain x direction."""

    num_horizontal_range: tuple[int, int] | None = None
    """Difficulty-interpolated range for the number of horizontal bars."""

    num_vertical: int | None = None
    """Fixed number of vertical bars running along the terrain y direction."""

    num_vertical_range: tuple[int, int] | None = None
    """Difficulty-interpolated range for the number of vertical bars."""

    randomize_bar_count_difficulty: bool = False
    """Whether to use independent random difficulties for horizontal and vertical bar counts."""

    force_unequal_counts: bool = False
    """Whether to force horizontal and vertical bar counts to be different after interpolation."""

    force_even_counts: bool = False
    """Whether to force horizontal and vertical bar counts to even values after interpolation."""

    bar_width: float | None = None
    """Fixed bar width in meters."""

    bar_width_range: tuple[float, float] | None = None
    """Difficulty-interpolated range for bar width in meters."""

    randomize_bar_width_difficulty: bool = False
    """Whether to use a random difficulty for bar width instead of the incoming terrain difficulty."""

    bar_height: float | None = None
    """Fixed bar height in meters."""

    bar_height_range: tuple[float, float] | None = None
    """Difficulty-interpolated range for bar height in meters."""

    bar_length_ratio: float = 0.95
    """Fraction of the terrain span covered by each bar along its long direction."""

    ground_thickness: float = 0.05
    """Thickness of the flat ground box below the bars in meters. Set to 0.0 to disable it."""


@configclass
class MeshCustomSplitGridBarsTerrainCfg(MeshCustomGridBarsTerrainCfg):
    """Configuration for split rectangular bars generated as box meshes.

    The tile is split into two regions. One region contains only horizontal
    bars, and the other contains only vertical bars, which removes bar-bar
    intersections while preserving the same randomization controls as the
    regular grid-bar terrain.
    """

    function = mesh_split_grid_bars_terrain

    split_axis: str = "x"
    """Selected split side. Use 'x', '-x', 'y', or '-y'."""

    split_ratio: float = 0.5
    """Fraction of the tile area assigned to the selected side."""

    horizontal_side: str = "negative"
    """Side sign used when split_axis is unsigned. Use 'negative' or 'positive'."""

    randomize_side: bool = False
    """Whether to randomly choose the selected side from 'x', '-x', 'y', and '-y'."""


@height_field_to_mesh
def cliff_inverted_pyramid_stairs_terrain(
    difficulty: float, cfg: "HfCliffInvertedPyramidStairsTerrainCfg"
) -> np.ndarray:
    """Generate an inverted pyramid stairs terrain elevated above the surrounding border."""

    step_height = cfg.step_height_range[0] + difficulty * (cfg.step_height_range[1] - cfg.step_height_range[0])
    step_height *= -1
    height_offset_scale, height_offset_difficulty = _resolve_height_offset_curriculum(difficulty, cfg)
    height_offset = _resolve_fixed_or_difficulty_value(
        cfg.height_offset,
        (
            tuple(value * height_offset_scale for value in cfg.height_offset_range)
            if cfg.height_offset_range is not None
            else None
        ),
        height_offset_difficulty,
        "height_offset",
    )

    width_pixels = discretize_size_to_pixels(cfg.size[0], cfg.horizontal_scale)
    length_pixels = discretize_size_to_pixels(cfg.size[1], cfg.horizontal_scale)
    step_width = max(1, discretize_size_to_pixels(cfg.step_width, cfg.horizontal_scale))
    step_height_pixels = int(np.rint(step_height / cfg.vertical_scale))
    platform_width = discretize_size_to_pixels(cfg.platform_width, cfg.horizontal_scale)
    height_offset_pixels = int(np.rint(height_offset / cfg.vertical_scale))

    hf_raw = np.full((width_pixels, length_pixels), height_offset_pixels, dtype=np.float32)

    current_step_height = 0
    start_x, start_y = 0, 0
    stop_x, stop_y = width_pixels, length_pixels
    while (stop_x - start_x) > platform_width and (stop_y - start_y) > platform_width:
        start_x += step_width
        stop_x -= step_width
        start_y += step_width
        stop_y -= step_width
        current_step_height += step_height_pixels
        hf_raw[start_x:stop_x, start_y:stop_y] = height_offset_pixels + current_step_height

    return np.rint(hf_raw).astype(np.int16)


@configclass
class HfCliffInvertedPyramidStairsTerrainCfg(HfTerrainBaseCfg):
    """Configuration for a raised inverted pyramid stairs terrain with a cliff at the border."""

    function = cliff_inverted_pyramid_stairs_terrain

    step_height_range: tuple[float, float] = MISSING
    """The minimum and maximum height of the steps (in m)."""

    step_width: float = MISSING
    """The width of the steps (in m)."""

    platform_width: float = 1.0
    """The width of the square platform at the center of the terrain (in m)."""

    height_offset: float | None = None
    """The fixed z-offset applied to the whole internal terrain (in m)."""

    height_offset_range: tuple[float, float] | None = None
    """The range of z-offset values, interpolated from terrain difficulty (in m)."""

    height_offset_curriculum_scale_by_difficulty: bool = False
    """Whether to scale ``height_offset_range`` by a difficulty bucket before interpolation."""

    height_offset_curriculum_num_levels: int = 11
    """Number of difficulty buckets used by the height-offset curriculum scale."""


@height_field_to_mesh
def raised_inverted_pyramid_sloped_terrain(
    difficulty: float, cfg: "HfCustomRaisedInvertedPyramidSlopedTerrainCfg"
) -> np.ndarray:
    """Generate a raised inverted pyramid terrain."""

    raised_height = _resolve_fixed_or_difficulty_value(
        cfg.raised_height, cfg.raised_height_range, difficulty, "raised_height"
    )
    slope_angle_deg = _resolve_fixed_or_difficulty_value(
        cfg.slope_angle_deg, cfg.angle_range, difficulty, "slope_angle_deg"
    )
    ramp_length = _resolve_fixed_or_difficulty_value(cfg.ramp_length, cfg.ramp_length_range, difficulty, "ramp_length")

    width_pixels = discretize_size_to_pixels(cfg.size[0], cfg.horizontal_scale)
    length_pixels = discretize_size_to_pixels(cfg.size[1], cfg.horizontal_scale)
    ramp_length_pixels = discretize_size_to_pixels(ramp_length, cfg.horizontal_scale)
    platform_width_pixels = discretize_size_to_pixels(cfg.platform_width, cfg.horizontal_scale)

    if ramp_length_pixels <= 0:
        raise ValueError(
            f"Ramp length must discretize to at least one pixel. Got: {ramp_length} m with"
            f" horizontal scale {cfg.horizontal_scale}."
        )
    if platform_width_pixels <= 0:
        raise ValueError(f"Platform width must discretize to at least one pixel. Got: {cfg.platform_width}.")

    depressed_region_pixels = platform_width_pixels + 2 * ramp_length_pixels
    if depressed_region_pixels > width_pixels or depressed_region_pixels > length_pixels:
        raise ValueError(
            "Ramp length and platform width leave no room for the raised inverted pyramid region:"
            f" ramp_length={ramp_length}, platform_width={cfg.platform_width}, size={cfg.size}."
        )

    raised_height_pixels = int(np.rint(raised_height / cfg.vertical_scale))
    ramp_run = ramp_length_pixels * cfg.horizontal_scale
    depth = np.tan(np.deg2rad(slope_angle_deg)) * ramp_run
    depth_pixels = int(np.rint(depth / cfg.vertical_scale))

    hf_raw = np.full((width_pixels, length_pixels), raised_height_pixels, dtype=np.float32)

    center_x = width_pixels // 2
    center_y = length_pixels // 2
    start_x = center_x - depressed_region_pixels // 2
    start_y = center_y - depressed_region_pixels // 2
    stop_x = start_x + depressed_region_pixels
    stop_y = start_y + depressed_region_pixels

    local_center = depressed_region_pixels // 2
    x_profile = (local_center - np.abs(local_center - np.arange(depressed_region_pixels))) / max(local_center, 1)
    y_profile = (local_center - np.abs(local_center - np.arange(depressed_region_pixels))) / max(local_center, 1)
    inner_hf = -depth_pixels * x_profile[:, None] * y_profile[None, :]

    platform_half_width = platform_width_pixels // 2
    x_pf = np.clip(depressed_region_pixels // 2 - platform_half_width, 0, depressed_region_pixels - 1)
    y_pf = np.clip(depressed_region_pixels // 2 - platform_half_width, 0, depressed_region_pixels - 1)
    z_pf = inner_hf[x_pf, y_pf]
    inner_hf = np.clip(inner_hf, min(0, z_pf), max(0, z_pf))

    hf_raw[start_x:stop_x, start_y:stop_y] = raised_height_pixels + inner_hf
    return np.rint(hf_raw).astype(np.int16)


@configclass
class HfCustomRaisedInvertedPyramidSlopedTerrainCfg(HfTerrainBaseCfg):
    """Configuration for a raised inverted pyramid sloped terrain."""

    function = raised_inverted_pyramid_sloped_terrain

    raised_height: float | None = None
    """The fixed amount by which the whole terrain is raised above the ground (in m)."""

    raised_height_range: tuple[float, float] | None = None
    """The range of raised heights interpolated from terrain difficulty (in m)."""

    slope_angle_deg: float | None = None
    """The fixed angle of the inverted pyramid faces in degrees."""

    angle_range: tuple[float, float] | None = None
    """The range of inverted pyramid face angles in degrees."""

    ramp_length: float | None = None
    """The fixed horizontal projection length of each inverted pyramid face (in m)."""

    ramp_length_range: tuple[float, float] | None = None
    """The range of horizontal projection lengths interpolated from terrain difficulty (in m)."""

    platform_width: float = 1.0
    """The width of the square platform at the bottom of the inverted pyramid (in m)."""


@height_field_to_mesh
def directional_wave_terrain(difficulty: float, cfg: "HfCustomDirectionalWaveTerrainCfg") -> np.ndarray:
    """Generate a sinusoidal terrain profile along a single axis."""

    del difficulty

    if cfg.frequency < 0.0:
        raise ValueError(f"Wave frequency must be non-negative. Got: {cfg.frequency}.")

    width_pixels = discretize_size_to_pixels(cfg.size[0], cfg.horizontal_scale)
    length_pixels = discretize_size_to_pixels(cfg.size[1], cfg.horizontal_scale)
    amplitude_pixels = cfg.amplitude / cfg.vertical_scale

    hf_raw = np.zeros((width_pixels, length_pixels), dtype=np.float32)

    if cfg.axis == "x":
        positions = np.arange(width_pixels) * cfg.horizontal_scale
        profile = amplitude_pixels * np.sin(2.0 * np.pi * cfg.frequency * positions + cfg.phase)
        hf_raw[:] = profile[:, None]
    elif cfg.axis == "y":
        positions = np.arange(length_pixels) * cfg.horizontal_scale
        profile = amplitude_pixels * np.sin(2.0 * np.pi * cfg.frequency * positions + cfg.phase)
        hf_raw[:] = profile[None, :]
    else:
        raise ValueError(f"Unknown axis '{cfg.axis}'. Must be 'x' or 'y'.")

    return np.rint(hf_raw).astype(np.int16)


@configclass
class HfCustomDirectionalWaveTerrainCfg(HfTerrainBaseCfg):
    """Configuration for a single-axis sinusoidal wave height field terrain."""

    function = directional_wave_terrain

    amplitude: float = MISSING
    """The amplitude of the wave (in m)."""

    frequency: float = MISSING
    """The wave frequency in cycles per meter."""

    axis: str = "x"
    """The axis along which the wave varies. Supported values are ``x`` and ``y``."""

    phase: float = 0.0
    """The phase offset of the wave (in radians)."""


@height_field_to_mesh
def truncated_sloped_terrain(difficulty: float, cfg: "HfCustomTruncatedSlopedTerrainCfg") -> np.ndarray:
    """Generate one or more truncated single-axis ramps."""

    if cfg.num_ramps <= 0:
        raise ValueError(f"Number of ramps must be positive. Got: {cfg.num_ramps}.")

    width_pixels = discretize_size_to_pixels(cfg.size[0], cfg.horizontal_scale)
    length_pixels = discretize_size_to_pixels(cfg.size[1], cfg.horizontal_scale)
    bias_pixels = int(np.rint(cfg.bias / cfg.horizontal_scale))
    spacing_pixels = int(np.rint(cfg.ramp_spacing / cfg.horizontal_scale))

    hf_raw = np.zeros((width_pixels, length_pixels), dtype=np.float32)

    def _resolve_ramp_specs() -> tuple[list[float], list[float]]:
        if cfg.slope_angle_deg is not None:
            ramp_angles = [cfg.slope_angle_deg] * cfg.num_ramps
        elif cfg.randomize_each_ramp:
            ramp_angles = np.random.uniform(cfg.angle_range[0], cfg.angle_range[1], size=cfg.num_ramps).tolist()
        else:
            angle = cfg.angle_range[0] + difficulty * (cfg.angle_range[1] - cfg.angle_range[0])
            ramp_angles = [angle] * cfg.num_ramps

        if cfg.ramp_length is not None:
            ramp_lengths = [cfg.ramp_length] * cfg.num_ramps
        elif cfg.randomize_each_ramp:
            ramp_lengths = np.random.uniform(
                cfg.ramp_length_range[0], cfg.ramp_length_range[1], size=cfg.num_ramps
            ).tolist()
        else:
            length = cfg.ramp_length_range[0] + difficulty * (
                cfg.ramp_length_range[1] - cfg.ramp_length_range[0]
            )
            ramp_lengths = [length] * cfg.num_ramps

        return ramp_angles, ramp_lengths

    def _place_ramps_in_domain(domain_pixels: int):
        ramp_angles, ramp_lengths = _resolve_ramp_specs()
        ramps = []
        for ramp_id, (ramp_angle_deg, ramp_length) in enumerate(zip(ramp_angles, ramp_lengths, strict=True)):
            if ramp_length <= 0.0:
                raise ValueError(f"Ramp length must be positive. Got: {ramp_lengths}.")
            start = base_start + ramp_id * spacing_pixels
            ramp_length_pixels = min(max(1, discretize_size_to_pixels(ramp_length, cfg.horizontal_scale)), domain_pixels)
            if 0 <= start and start + ramp_length_pixels <= domain_pixels:
                slope = np.tan(np.deg2rad(ramp_angle_deg))
                positions = np.arange(ramp_length_pixels) * cfg.horizontal_scale
                ramp_profile = slope * positions / cfg.vertical_scale
                ramps.append((start, ramp_length_pixels, ramp_profile))
        return ramps

    base_start = (width_pixels if cfg.axis == "x" else length_pixels) // 2
    if not cfg.centered:
        base_start += bias_pixels
    domain_pixels = width_pixels if cfg.axis == "x" else length_pixels
    base_start = int(np.clip(base_start, 0, domain_pixels - 1))

    if cfg.axis == "x":
        for start, ramp_length_pixels, ramp_profile in _place_ramps_in_domain(width_pixels):
            hf_raw[start : start + ramp_length_pixels, :] = ramp_profile[:, None]
    elif cfg.axis == "y":
        for start, ramp_length_pixels, ramp_profile in _place_ramps_in_domain(length_pixels):
            hf_raw[:, start : start + ramp_length_pixels] = ramp_profile[None, :]
    else:
        raise ValueError(f"Unknown axis '{cfg.axis}'. Must be 'x' or 'y'.")

    return np.rint(hf_raw).astype(np.int16)


@configclass
class HfCustomTruncatedSlopedTerrainCfg(HfTerrainBaseCfg):
    """Configuration for a single-axis ramp that truncates back to the ground."""

    function = truncated_sloped_terrain

    slope_angle_deg: float | None = None
    """The fixed ramp angle in degrees."""

    angle_range: tuple[float, float] | None = None
    """The ramp angle range in degrees."""

    ramp_length: float | None = None
    """The fixed ramp footprint length along the varying axis (in m)."""

    ramp_length_range: tuple[float, float] | None = None
    """The ramp length range along the varying axis (in m)."""

    axis: str = "x"
    """The axis along which the ramp varies. Supported values are ``x`` and ``y``."""

    centered: bool = True
    """Whether to place the first ramp foot at the center along the varying axis."""

    bias: float = 0.0
    """Signed offset of the first ramp foot along the varying axis (in m)."""

    num_ramps: int = 1
    """Number of ramps to place along the varying axis."""

    ramp_spacing: float = 0.0
    """Signed spacing between consecutive ramp feet along the varying axis (in m)."""

    randomize_each_ramp: bool = False
    """Whether to independently sample each ramp from the provided ranges."""

~~~

</details>

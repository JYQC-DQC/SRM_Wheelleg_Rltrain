"""Fixed flat scenarios and physical metrics, independent of Isaac and training rewards."""

from dataclasses import asdict, dataclass
from itertools import product

import numpy as np

from .training import TrainingConfig, null_fields


@dataclass(frozen=True)
class FlatCase:
    name: str
    group: str
    targets: tuple[tuple[float, float, float], ...]  # vx m/s, wz rad/s, height m
    random_reset: bool = False
    delay_steps: tuple[int, int] = (0, 0)  # observation/action, physics ticks
    push_velocity_b: tuple[float, float] = (0.0, 0.0)


def flat_cases(cfg: TrainingConfig) -> list[FlatCase]:
    e, c = cfg.settings["evaluation"], cfg.settings["commands"]
    f = e["flat_suite"]
    delays = (e["observation_delay_steps"], e["action_delay_steps"])
    cases = []
    for hi, height in enumerate(np.linspace(*c["height_range_m"], f["height_samples"])):
        height = float(height)
        stand = (0.0, 0.0, height)
        commands = [("stand", stand)]
        for fraction in f["speed_fractions"]:
            commands.extend(("straight", (v * fraction, 0.0, height)) for v in c["vx_range_m_s"])
            commands.extend(("turn", (0.0, w * fraction, height)) for w in c["wz_range_rad_s"])
        for fraction in f["combined_fractions"]:
            commands.extend(
                ("combined", (v * fraction, sign * c["combined_wz_limit_rad_s"] * fraction, height))
                for v, sign in product(c["vx_range_m_s"], (-1, 1))
            )
        commands.extend(("dash", (v, 0.0, height)) for v in c["dash_range_m_s"])
        for index, (group, target) in enumerate(commands):
            cases.append(FlatCase(f"h{hi}_{group}_{index}", group, (target,), delay_steps=delays))
        vmin, vmax = c["vx_range_m_s"]
        wmin, wmax = c["wz_range_rad_s"]
        transitions = {
            "brake_forward": ((vmax, 0.0, height), stand),
            "brake_reverse": ((vmin, 0.0, height), stand),
            "reverse": ((vmax, 0.0, height), (vmin, 0.0, height)),
            "turn_reverse": ((0.0, wmax, height), (0.0, wmin, height)),
        }
        for name, targets in transitions.items():
            cases.append(FlatCase(f"h{hi}_{name}", "transition", targets, delay_steps=delays))
        cases.append(FlatCase(f"h{hi}_random_start", "random_start", (stand,), True, delays))
        for axis, sign in product(range(2), (-1, 1)):
            push = [0.0, 0.0]
            push[axis] = sign * f["push_velocity_m_s"]
            cases.append(FlatCase(f"h{hi}_push_{axis}_{sign}", "push", (stand,), False, delays, tuple(push)))
        for index, delay in enumerate(f["delay_pairs_steps"]):
            target = (vmax * f["delay_command_fraction"], c["combined_wz_limit_rad_s"], height)
            cases.append(FlatCase(f"h{hi}_delay_{index}", "delay", (target,), delay_steps=tuple(delay)))
    low, high = c["height_range_m"]
    for index, vx in enumerate((0.0, c["vx_range_m_s"][1] * f["delay_command_fraction"])):
        cases.append(
            FlatCase(
                f"height_cycle_{index}",
                "height_transition",
                ((vx, 0.0, low), (vx, 0.0, high), (vx, 0.0, low)),
                delay_steps=delays,
            )
        )
    return cases


def validate_flat_suite(cfg: TrainingConfig) -> None:
    """Only the detailed evaluator requires these fields; old training snapshots remain loadable."""
    e = cfg.settings["evaluation"]
    try:
        f = e["flat_suite"]
        for key in (
            "startup_s",
            "hold_s",
            "transition_settling_s",
            "stable_hold_s",
            "push_velocity_m_s",
            "push_after_s",
            "recovery_deadline_s",
            "stand_window_s",
        ):
            if not np.isfinite(f[key]) or f[key] <= 0:
                raise ValueError(f"evaluation.flat_suite.{key} must be finite and positive")
        for key in ("height_samples", "trace_stride"):
            if type(f[key]) is not int or f[key] < 1:
                raise ValueError(f"evaluation.flat_suite.{key} must be a positive integer")
        if f["height_samples"] < 3:
            raise ValueError("flat_suite.height_samples must cover low/middle/high (>=3)")
        for key in ("speed_fractions", "combined_fractions"):
            if not f[key] or any(not 0 < v <= 1 for v in f[key]) or 1.0 not in f[key]:
                raise ValueError(f"flat_suite.{key} must include 1.0 and contain fractions in (0,1]")
        if not 0 < f["delay_command_fraction"] <= 1:
            raise ValueError("flat_suite.delay_command_fraction must be in (0,1]")
        if (
            not f["seeds"]
            or len(set(f["seeds"])) != len(f["seeds"])
            or any(type(seed) is not int or seed < 0 for seed in f["seeds"])
        ):
            raise ValueError("flat_suite.seeds must be distinct nonnegative integers")
        for pair in f["delay_pairs_steps"]:
            if len(pair) != 2 or any(type(v) is not int or v < 0 for v in pair):
                raise ValueError("flat_suite.delay_pairs_steps must contain nonnegative integer pairs")
        if not f["delay_pairs_steps"]:
            raise ValueError("flat_suite.delay_pairs_steps must not be empty")
        if f["transition_settling_s"] + f["stable_hold_s"] >= f["hold_s"]:
            raise ValueError("flat_suite.hold_s must leave time for steady measurements")
        if f["push_after_s"] + f["recovery_deadline_s"] + f["stable_hold_s"] >= f["hold_s"]:
            raise ValueError("flat_suite.hold_s must cover push and recovery")
        if f["push_after_s"] + f["transition_settling_s"] + f["stand_window_s"] >= f["hold_s"]:
            raise ValueError("flat_suite.hold_s must cover post-push drift measurement")
        for key in ("observation_delay_steps", "action_delay_steps"):
            if type(e[key]) is not int or e[key] < 0:
                raise ValueError(f"evaluation.{key} must be a nonnegative integer")
        if f["startup_s"] < cfg.shared["leg_reset"]["settle_s"]:
            raise ValueError("flat_suite.startup_s must cover the configured spawn settling window")
        for key in ("stand_drift_m", "tilt_p95_rad", "contact_fraction"):
            if not np.isfinite(f["acceptance"][key]) or f["acceptance"][key] <= 0:
                raise ValueError(f"flat_suite.acceptance.{key} must be finite and positive")
        curriculum = cfg.settings["command_curriculum"]
        for key in (
            "velocity_error_threshold_m_s",
            "yaw_error_threshold_rad_s",
            "relative_error",
            "height_error_threshold_m",
        ):
            value = curriculum[key]
            if value is None or not np.isfinite(value) or value < 0:
                raise ValueError(f"command_curriculum.{key} must be finite and nonnegative for flat evaluation")
        if f["acceptance"]["contact_fraction"] > 1:
            raise ValueError("flat_suite.acceptance.contact_fraction must not exceed 1")
        if type(e["episodes_per_case"]) is not int or e["episodes_per_case"] < 1:
            raise ValueError("evaluation.episodes_per_case must be a positive integer")
        for key in ("vx_range_m_s", "wz_range_rad_s", "dash_range_m_s", "height_range_m"):
            bounds = cfg.settings["commands"][key]
            if bounds is None or len(bounds) != 2 or not np.isfinite(bounds).all():
                raise ValueError(f"commands.{key} must be finite for flat evaluation")
        for key in ("linear_slew_m_s2", "angular_slew_rad_s2", "height_slew_m_s", "combined_wz_limit_rad_s"):
            value = cfg.settings["commands"][key]
            if value is None or not np.isfinite(value) or value <= 0:
                raise ValueError(f"commands.{key} must be finite and positive for flat evaluation")
        missing = null_fields(cfg.shared["leg_reset"], "robot.training.leg_reset")
        if missing:
            raise ValueError(f"random-start evaluation requires robot.training.leg_reset: {missing}")
    except KeyError as error:
        raise ValueError(f"{cfg.policy_path}: detailed flat evaluation missing {error.args[0]}") from error


def flat_metrics(trace: dict[str, np.ndarray], cfg: TrainingConfig) -> dict:
    """Full-rate trace (time, environment, ...); no post-reset measurements contribute."""
    f = cfg.settings["evaluation"]["flat_suite"]
    limits = f["acceptance"]
    dt = 1 / cfg.robot.policy_hz
    valid = trace["valid"]
    finite = np.isfinite(trace["errors"]).all(-1) & np.isfinite(trace["attitude"]).all(-1)
    finite &= np.isfinite(trace["action"]).all(-1) & np.isfinite(trace["torque"]).all(-1)
    finite &= np.isfinite(trace["contact_force"]) & np.isfinite(trace["position"]).all(-1)
    finite &= np.isfinite(trace["velocity"]).all(-1) & np.isfinite(trace["angular_velocity"]).all(-1)
    finite &= np.isfinite(trace["joint_velocity"]).all(-1) & np.isfinite(trace["wheel_force"]).all(-1)
    valid_finite = valid & finite
    steady = valid_finite & trace["steady"][:, None]
    failed = (trace["failed"] & valid).any(0) | (valid & ~finite).any(0)
    numerical = (trace["numerical_failure"] & valid).any(0) | (valid & ~finite).any(0)
    completed = valid[-1] & ~failed & ~trace["timeout"].any(0)
    errors = np.abs(trace["errors"])
    # Same rule as the training command curriculum (env.py _reset_idx): allowed mean error =
    # floor + relative_error * mean |command| for vx/wz, a fixed bound for height, strict comparison.
    curriculum = cfg.settings["command_curriculum"]
    floor = np.array([curriculum["velocity_error_threshold_m_s"], curriculum["yaw_error_threshold_rad_s"]])
    command_abs = np.abs(trace["command"][..., :2])
    height_bound = curriculum["height_error_threshold_m"]

    def mean_over(mask: np.ndarray, values: np.ndarray, empty: float) -> np.ndarray:
        count = mask.sum(0)[:, None]
        return np.divide(
            np.where(mask[..., None], values, 0).sum(0),
            count,
            out=np.full(values.shape[1:], empty),
            where=count > 0,
        )

    def allowed(mask: np.ndarray) -> np.ndarray:
        bound = floor + curriculum["relative_error"] * mean_over(mask, command_abs, 0.0)
        return np.concatenate((bound, np.full((valid.shape[1], 1), height_bound)), -1)

    count = steady.sum(0)
    mean_error = mean_over(steady, errors, np.inf)
    threshold = allowed(steady)
    error_ratio = mean_error / threshold
    contact = trace["contact_force"] > cfg.settings["reward_parameters"]["contact_force_n"]
    post_start = valid_finite & (trace["time_s"] >= f["startup_s"])[:, None]
    contact_fraction = np.divide(
        (contact & post_start).sum(0), post_start.sum(0), out=np.ones(valid.shape[1]), where=post_start.sum(0) > 0
    )
    tilt = np.abs(trace["attitude"][..., :2]).max(-1)
    tilt_p95 = np.array(
        [
            np.percentile(tilt[post_start[:, i], i], 95) if post_start[:, i].any() else np.inf
            for i in range(valid.shape[1])
        ]
    )
    passed = completed & (mean_error < threshold).all(-1)
    passed &= (contact_fraction <= limits["contact_fraction"]) & (tilt_p95 <= limits["tilt_p95_rad"])
    recovery, drift_segments, segment_results = [], [], []
    sample_threshold = np.concatenate(
        (floor + curriculum["relative_error"] * command_abs, np.full(errors.shape[:2] + (1,), height_bound)), -1
    )
    stable = (errors < sample_threshold).all(-1) & (tilt <= limits["tilt_p95_rad"]) & ~contact & valid_finite
    hold = max(1, round(f["stable_hold_s"] / dt))
    for segment in np.unique(trace["segment"]):
        selected = trace["segment"] == segment
        indices = np.flatnonzero(selected)
        segment_mask = steady & selected[:, None]
        segment_mae = mean_over(segment_mask, errors, np.inf)
        segment_threshold = allowed(segment_mask)
        passed &= (segment_mae < segment_threshold).all(-1)
        # Recovery starts after the requested command has finished slewing (or at the push).
        ready = indices[trace["command_reached"][indices]]
        recovered = np.full(valid.shape[1], np.nan)
        if len(ready):
            run = np.zeros(valid.shape[1], dtype=int)
            for step in indices[indices >= ready[0]]:
                run = np.where(stable[step], run + 1, 0)
                newly = (run >= hold) & np.isnan(recovered)
                recovered[newly] = max(0, step - ready[0] - hold + 1) * dt
        passed &= np.isfinite(recovered) & (recovered <= f["recovery_deadline_s"])
        recovery.append(recovered)
        segment_results.append(
            dict(
                segment=int(segment),
                requested=trace["requested"][indices[-1]].tolist(),
                mae_per_episode=[[float(v) if np.isfinite(v) else None for v in row] for row in segment_mae],
                allowed_per_episode=[[float(v) for v in row] for row in segment_threshold],
            )
        )
        # Drift is measured from the steady zero-command position, separately for every stop.
        if np.all(trace["requested"][indices, :2] == 0) and (
            not trace["push_applied"].any() or trace["push_applied"][indices].all()
        ):
            eligible = indices[trace["steady"][indices]]
            window = round(f["stand_window_s"] / dt)
            drift = np.full(valid.shape[1], np.inf)
            if len(eligible) >= window:
                eligible = eligible[:window]
                origin = trace["position"][eligible[0], :, :2]
                displacement = np.linalg.norm(trace["position"][eligible, :, :2] - origin, axis=-1)
                drift = np.max(np.where(valid_finite[eligible], displacement, 0), axis=0)
                drift[~valid_finite[eligible[0]]] = np.inf
            passed &= drift <= limits["stand_drift_m"]
            drift_segments.append(drift)

    def stats(values: np.ndarray) -> dict:
        values = values[np.isfinite(values)]
        if not values.size:
            return dict(mean=None, rms=None, p95=None, maximum=None)
        return dict(
            mean=float(values.mean()),
            rms=float(np.sqrt(np.mean(values**2))),
            p95=float(np.percentile(values, 95)),
            maximum=float(values.max()),
        )

    consecutive = np.zeros(valid.shape[1], dtype=int)
    maximum_contact = consecutive.copy()
    for row in contact & post_start:
        consecutive = np.where(row, consecutive + 1, 0)
        maximum_contact = np.maximum(maximum_contact, consecutive)
    # Action statistics exclude the startup stand-up window so they describe controlled motion only.
    action_delta = np.diff(trace["action"], axis=0)
    pair_valid = post_start[1:] & post_start[:-1]
    torque_limit = np.asarray(cfg.policy.torque_limit_nm)
    torque_utilization = np.abs(trace["torque"]) / torque_limit
    per_episode = []
    recovery_array = np.stack(recovery)
    for i in range(valid.shape[1]):
        per_episode.append(
            dict(
                index=i,
                failed=bool(failed[i]),
                numerical_failure=bool(numerical[i]),
                completed=bool(completed[i]),
                passed=bool(passed[i]),
                valid_duration_s=float(valid[:, i].sum() * dt),
                steady_samples=int(count[i]),
                mae=[float(v) if np.isfinite(v) else None for v in mean_error[i]],
                allowed_mae=[float(v) for v in threshold[i]],
                error_ratio=[float(v) if np.isfinite(v) else None for v in error_ratio[i]],
                contact_fraction=float(contact_fraction[i]),
                tilt_p95_rad=float(tilt_p95[i]) if np.isfinite(tilt_p95[i]) else None,
                recovery_s=[float(v) if np.isfinite(v) else None for v in recovery_array[:, i]],
                stand_drift_m=[float(v[i]) if np.isfinite(v[i]) else None for v in drift_segments],
                longest_contact_s=float(maximum_contact[i] * dt),
            )
        )
    finite_ratio = error_ratio[np.isfinite(error_ratio).all(-1)]
    return dict(
        episodes=valid.shape[1],
        failures=int(failed.sum()),
        numerical_failures=int(numerical.sum()),
        completed=int(completed.sum()),
        passed=int(passed.sum()),
        pass_rate=float(passed.mean()),
        steady_error={key: stats(errors[..., i][steady]) for i, key in enumerate(("vx_m_s", "wz_rad_s", "height_m"))},
        # Steady MAE divided by the curriculum allowance, mean over episodes with steady samples; <1 passes.
        steady_error_ratio=dict(
            zip(
                ("vx", "wz", "height", "mean"),
                [float(v) for v in finite_ratio.mean(0)] + [float(finite_ratio.mean())]
                if len(finite_ratio)
                else [None] * 4,
            )
        ),
        full_error={
            key: stats(errors[..., i][valid_finite]) for i, key in enumerate(("vx_m_s", "wz_rad_s", "height_m"))
        },
        tilt_rad=stats(tilt[post_start]),
        contact_fraction=stats(contact_fraction),
        roll_abs_rad=stats(np.abs(trace["attitude"][..., 0][post_start])),
        pitch_abs_rad=stats(np.abs(trace["attitude"][..., 1][post_start])),
        longest_contact_s=stats(maximum_contact * dt),
        stand_drift_m=stats(np.stack(drift_segments)) if drift_segments else None,
        recovery_s=stats(recovery_array),
        unrecovered_segments=int(np.isnan(recovery_array).sum()),
        raw_action_abs=stats(np.abs(trace["action"][post_start])),
        torque_abs_nm=stats(np.abs(trace["torque"][valid_finite])),
        nominal_torque_utilization=stats(torque_utilization[valid_finite]),
        # Policy-rate samples, not a claim about the maximum over 500 Hz actuator substeps.
        nominal_torque_limit_fraction=float((torque_utilization[valid_finite] >= 0.99).mean())
        if valid_finite.any()
        else None,
        action_delta_abs=stats(np.abs(action_delta[pair_valid])),
        action_abs_per_channel=[stats(np.abs(trace["action"][..., i][post_start])) for i in range(6)],
        joint_velocity_abs_per_channel=[stats(np.abs(trace["joint_velocity"][..., i][valid_finite])) for i in range(6)],
        wheel_force_n=stats(trace["wheel_force"][valid_finite]),
        leg_target_clipped_fraction=float(trace["leg_target_clipped"][post_start].mean()) if post_start.any() else None,
        wheel_target_clipped_fraction=float(trace["wheel_target_clipped"][post_start].mean())
        if post_start.any()
        else None,
        per_episode=per_episode,
        segments=segment_results,
    )


def case_description(case: FlatCase) -> dict:
    return asdict(case)

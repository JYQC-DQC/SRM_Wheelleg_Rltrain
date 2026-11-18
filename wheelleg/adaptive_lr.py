def install_adaptive_lr_limit(algorithm, ceiling: float, growth: float) -> None:
    """Limit rsl_rl's KL proposal before each Adam step, including its feedback into the next proposal."""
    last = algorithm.learning_rate
    algorithm.iteration_peak_lr = 0.0

    def before_step(optimizer, args, kwargs):
        nonlocal last
        last = min(algorithm.learning_rate, last * growth, ceiling)
        algorithm.learning_rate = last
        for group in optimizer.param_groups:
            group["lr"] = last
        algorithm.iteration_peak_lr = max(algorithm.iteration_peak_lr, last)

    algorithm.optimizer.register_step_pre_hook(before_step)

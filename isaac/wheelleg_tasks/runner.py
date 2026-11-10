from rsl_rl.runners import OnPolicyRunner


class WheelLegRunner(OnPolicyRunner):
    """Persist task curriculum state alongside upstream PPO state."""

    def save(self, path: str, infos: dict | None = None) -> None:
        extra = {} if infos is None else dict(infos)
        env = self.env.unwrapped
        extra["command_fraction"] = env.commands.command_fraction
        if env.command_curriculum is not None:
            extra["command_curriculum"] = env.command_curriculum.state_dict()
        if env.jump_curriculum is not None:
            extra["jump_curriculum"] = env.jump_curriculum.state_dict()
        super().save(path, extra)

    def load(self, path: str, load_optimizer: bool = True, map_location=None) -> dict:
        infos = super().load(path, load_optimizer=load_optimizer, map_location=map_location)
        env = self.env.unwrapped
        env.commands.command_fraction = infos["command_fraction"]
        if env.command_curriculum is not None:
            env.command_curriculum.load_state_dict(infos["command_curriculum"])
        if env.jump_curriculum is not None:
            env.jump_curriculum.load_state_dict(infos["jump_curriculum"])
        return infos

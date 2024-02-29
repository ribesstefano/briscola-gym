from gym.envs.registration import register

register(
    id='briscola-v0',
    entry_point='briscola_gym.envs:BriscolaEnv',
)

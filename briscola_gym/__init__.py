from gym.envs.registration import register

register(
    id='briscola-v0',
    entry_point='gym_briscola.envs:BriscolaEnv',
)
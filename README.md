# Briscola Gym

This is a simple implementation of the Italian card game Briscola, using the OpenAI Gym interface.

## Installation

```bash
pip install git+
```

## Usage

```python
import gym
import briscola_gym

num_players = 2
MAX_POINTS = 120

env = gym.make('bruscola_gym:briscola-v0', num_players=num_players)
num_actions = env.action_space.n  # 3
num_actions
```
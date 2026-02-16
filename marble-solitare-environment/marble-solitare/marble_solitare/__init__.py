from gymnasium.envs.registration import register

from marble_solitare.envs.marble_solitare_env import MarbleSolitareEnv
from marble_solitare.envs.marble_solitare_model import MarbleSolitareModel
from marble_solitare.envs.marble_solitare_model import MarbleSolitareState

register(
    # marble_solitare is this folder name
    # -v0 is because this first version
    # MarbleSolitare is the pretty name for gym.make
    id="marble_solitare/MarbleSolitare-v0",
    
    # marble_solitare.envs is the path marble_solitare/envs
    # MarbleSolitareEnv is the class name
    entry_point="marble_solitare.envs:MarbleSolitareEnv",
    
    # configure the automatic wrapper to truncate after 1200 steps
    max_episode_steps=700,
)

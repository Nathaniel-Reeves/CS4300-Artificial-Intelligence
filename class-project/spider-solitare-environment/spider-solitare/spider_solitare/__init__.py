from gymnasium.envs.registration import register

from spider_solitare.envs.spider_solitare_env import SpiderSolitareEnv
from spider_solitare.envs.spider_solitare_model import SpiderSolitareModel
from spider_solitare.envs.spider_solitare_model import SpiderSolitareState

register(
    # spider_solitare is this folder name
    # -v0 is because this first version
    # SpiderSolitare is the pretty name for gym.make
    id="spider_solitare/SpiderSolitare-v0",
    
    # spider_solitare.envs is the path spider_solitare/envs
    # SpiderSolitareEnv is the class name
    entry_point="spider_solitare.envs:SpiderSolitareEnv",
    
    # configure the automatic wrapper to truncate after 1200 steps
    max_episode_steps=700,
)

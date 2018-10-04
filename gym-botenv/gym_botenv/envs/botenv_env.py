import gym
import numpy as np
import uuid
import itertools
import random
from gym_botenv.envs.environment import Website, State
from gym import error, spaces, utils


def generate_fakeSites(nSites: int, nSP: int, probSP: float, probFP: float, probBB: float):
    """

    :param nSites: Amount of fake websites generated
    :param nSP: Amount of security providers
    :param probSP: Probability that a website has a security provider
    :param probFP: Probability that a website has browser fingerprinting capabilities
    :param probBB: Probability that a website block bots
    :return: list of nSites fake websites containing a tuple of values
    """
    A = [security_provider for security_provider in range(nSP+1)]
    probsSP = np.ones(nSP+1, dtype=float) * probSP/nSP
    probsSP[0] = 1-probSP

    probsFP = np.ones(2, dtype=float) * probFP
    probsFP[1] = 1 - probFP

    probsBB = np.ones(2, dtype=float) * probBB
    probsBB[1] = 1 - probBB

    listWebsite = []
    for i in range(nSites):
        id = uuid.uuid4()
        SP = np.random.choice(A,p=probsSP)
        FP = np.random.choice([0,1], p=probsFP) #0 : doesnt use fp, 1:use fp
        BB = np.random.choice([0,1], p=probsBB) #0: doesnt block bots, 1 block bots
        num_page_visit = 0
        website_obj = Website(id, SP, FP, BB, num_page_visit)
        listWebsite.append(website_obj)

    return listWebsite

def generate_states(listWebsite: list, numBinaryParams: int):
    """

    :param listWebsite: List of website's
    :param numBinaryParams: Amount of binary features
    :return: A tuple of states
    """
    rangeVisitedPage = 10
    maxVisitedPage = 100
    listRangeVisitedPage = []
    for i in range(0, maxVisitedPage-rangeVisitedPage+1, rangeVisitedPage):
        listRangeVisitedPage.append((i,i+rangeVisitedPage-1))

    numWebsite = len(listWebsite)
    rangePageSecuProvider = int(numWebsite / 100)
    listRangePageSecuProvider = []
    for i in range(0, numWebsite-rangePageSecuProvider+1, rangePageSecuProvider):
        listRangePageSecuProvider.append((i,i+rangePageSecuProvider-1))

    listStatesFeatures = []
    for i in range(numBinaryParams):
        listStatesFeatures.append(list(range(2)))

    listStatesFeatures.append(listRangeVisitedPage)
    listStatesFeatures.append(listRangePageSecuProvider)

    statesTuple = list(itertools.product(*listStatesFeatures))
    random.shuffle(statesTuple)
    states = []
    for state in statesTuple:
        states.append(State(state))

    return states

def isBotBlocked(website: Website):
    #Applying 


class BotenvEnv(gym.Env):
    """ Simple bot environment

    Botenv is a fake environment allowing to mimic a website's defenses against bots.

    On it's first versions, Botenv should allow to mimic wether the website has or no
    fingerprinting capabilities, if it does or do not block bots, etc...

    The observation is the website current configuration and if it has blocked the bot or no. The action is selected among
    an action space containing IP change, UA change, and the feature we want to jump in.

    The reward function depend on under which configuration the bot got blocked. For instance,
    if the security provider is extremely good at it's job, the negative reward should have less impact than
    if the bot got blocked because of a bad security provider.

    """
    reward_range = (-50, 10)

    def __init__(self, nSites=1000):
        self.action_space = spaces.Discrete(3) #3 actions for now



    def step(self, action):
        assert self.action_space.contains(action)
        pass



    def reset(self):
        pass

    def render(self, mode='human', close=False):
        pass
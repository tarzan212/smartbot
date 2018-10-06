import gym
import numpy as np
import uuid
import itertools
import random
import operator
from gym_botenv.envs.environment import Website, State
from gym import error, spaces, utils


def generate_fake_sites(nSites: int, nSP: int, probSP: float, probFP: float, probBB: float):
    """

    :param nSites: Amount of fake websites generated
    :param nSP: Amount of security providers
    :param probSP: Probability that a website has a security provider
    :param probFP: Probability that a website has browser fingerprinting capabilities
    :param probBB: Probability that a website block bots
    :return: list of nSites fake websites containing a tuple of values
    """
    A = [security_provider for security_provider in range(nSP + 1)]
    probsSP = np.ones(nSP + 1, dtype=float) * probSP / nSP
    probsSP[0] = 1 - probSP

    probsFP = np.ones(2, dtype=float) * probFP
    probsFP[1] = 1 - probFP

    probsBB = np.ones(2, dtype=float) * probBB
    probsBB[1] = 1 - probBB

    list_website = []
    for i in range(nSites):
        id = uuid.uuid4()
        SP = np.random.choice(A, p=probsSP)
        FP = np.random.choice([0, 1], p=probsFP)  # 0 : doesnt use fp, 1:use fp
        BB = np.random.choice([0, 1], p=probsBB)  # 0: doesnt block bots, 1 block bots
        num_page_visit = 0
        website_obj = Website(id, SP, FP, BB, num_page_visit)
        list_website.append(website_obj)

    return list_website


def generate_states(list_website: list, numBinaryParams: int):
    """

    :param list_website: List of website's
    :param numBinaryParams: Amount of binary features
    :return: A tuple of states
    """
    range_visited_page = 10
    maxVisitedPage = 100
    listRangeVisitedPage = []
    for i in range(0, maxVisitedPage - range_visited_page + 1, range_visited_page):
        listRangeVisitedPage.append((i, i + range_visited_page - 1))

    num_website = len(list_website)
    range_page_secu_provider = int(num_website / 100)
    list_range_page_secu_provider = []
    for i in range(0, num_website - range_page_secu_provider + 1, range_page_secu_provider):
        list_range_page_secu_provider.append((i, i + range_page_secu_provider - 1))

    list_states_features = []
    for i in range(numBinaryParams):
        list_states_features.append(list(range(2)))

    list_states_features.append(listRangeVisitedPage)
    list_states_features.append(list_range_page_secu_provider)

    states_tuple = list(itertools.product(*list_states_features))
    random.shuffle(states_tuple)
    states = []
    for state in states_tuple:
        states.append(State(state))

    return states


def randomize_security_provider(nSP: int, limits: tuple, seed=1000):
    random.seed(seed)

    return {x: random.randint(limits[0], limits[1] + 1) for x in range(1, nSP + 1)}


def init_security_provider_freq(nSP: int):
    return {x: 0 for x in range(1, nSP + 1)}


def normalized_websites_values(list_website: list, security_provider_freq: dict, security_provider_grades: dict):
    values = {}
    for website in list_website:
        website.compute_value(security_provider_grades, security_provider_freq)
        values[website.id] = website.value

    maximum = max(values.items(), key=operator.itemgetter(1))[1]
    minimum = min(values.items(), key=operator.itemgetter(1))[1]

    for id, value in values.items():
        values[id] = float(float(value - minimum) / float(maximum - minimum))

    return values


def is_bot_blocked(website: Website, values_dict: dict):
    probs = np.ones(2, dtype=float) * values_dict[website.id]
    probs[0] = 1 - probs[1]

    return int(np.random.choice([0, 1], p=probs))


def websites_to_state(list_websites: list, list_states: list, dict_sp: dict):
    state_map = {}
    copy_list_website = list_websites
    for state in list_states:
        state_map[state] = []
        for index, website in enumerate(copy_list_website):
            if state.useFP != website.hasFingerprinting:
                continue
            elif state.useBB != website.blockbots:
                continue
            elif website.amount_page_visited not in range(state.rangeVisitedPage[0], state.rangeVisitedPage[1] + 1):
                continue
            else:
                security_provider = website.securityProvider
                if security_provider == 0:
                    state_map[state].append(website)
                    copy_list_website.pop(index)
                else:
                    if dict_sp[security_provider] in range(state.rangeVisitedSecuProvider[0],
                                                           state.rangeVisitedSecuProvider[1] + 1):
                        state_map[state].append(website)
                        copy_list_website.pop(index)

    return state_map


def upgrade_state_list(website, state, state_map: dict, dict_sp: dict):
    state_map[state].pop(state_map[state].index(website))
    for state, _ in state_map.items():
        if state.useFP != website.hasFingerprinting:
            continue
        elif state.useBB != website.blockbots:
            continue
        elif website.amount_page_visited not in range(state.rangeVisitedPage[0], state.rangeVisitedPage[1] + 1):
            continue
        else:
            security_provider = website.securityProvider
            if security_provider == 0:
                state_map[state].append(website)
                break
            else:
                if dict_sp[security_provider] in range(state.rangeVisitedSecuProvider[0],
                                                       state.rangeVisitedSecuProvider[1] + 1):
                    state_map[state].append(website)
                    break


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

    def __init__(self, nSites=1000, nSP=10, prob_sp=1 / 10, prob_fp=1 / 4, prob_bb=1 / 50):
        self.action_space = spaces.Discrete(3)  # 3 actions for now
        self.observation_space = spaces.Tuple(
            spaces.Tuple(spaces.Discrete(4)),
            spaces.Discrete(1)
        )

        self.sites = generate_fake_sites(nSites, nSP, prob_sp, prob_fp, prob_bb)
        self.states = generate_states(self.sites, 2)
        self.security_provider_grades = randomize_security_provider(nSP, (0, 10))
        self.security_provider_freq = init_security_provider_freq(nSP)

        self.states_map = websites_to_state(self.sites, self.states, self.security_provider_freq)
        self.reset()

    def step(self, action):
        assert self.action_space.contains(action)

    def _get_obs(self):
        pass

    def reset(self):
        pass

    def render(self, mode='human', close=False):
        pass

import gym
import numpy as np
import uuid
import itertools
import random
import operator
from gym_botenv.envs.environment import Website, State, SecurityProvider, Actions
from gym import error, spaces, utils


def generate_security_providers(nSP: int, limits: tuple):
    """
    """
    list_security_providers = {}
    for i in range(nSP):
        grade = random.randint(limits[0], limits[1] + 1)
        list_security_providers[i] = SecurityProvider(i, grade)

    return list_security_providers


def generate_fake_sites(nSites: int, security_providers: dict, probSP: float, probFP: float, probBB: float):
    """

    :param nSites: Amount of fake websites generated
    :param nSP: Amount of security providers
    :param probSP: Probability that a website has a security provider
    :param probFP: Probability that a website has browser fingerprinting capabilities
    :param probBB: Probability that a website block bots
    :return: list of nSites fake websites containing a tuple of values
    """
    nSP = len(security_providers)
    probsSP = np.ones(nSP, dtype=float) * probSP / (nSP - 1)
    probsSP[0] = 1 - probSP

    probsFP = np.ones(2, dtype=float) * probFP
    probsFP[1] = 1 - probFP

    probsBB = np.ones(2, dtype=float) * probBB
    probsBB[1] = 1 - probBB

    list_website = []
    for i in range(nSites):
        id = uuid.uuid4()
        SP = np.random.choice(list(security_providers.keys()), p=probsSP)
        FP = np.random.choice([0, 1], p=probsFP)  # 0 : doesnt use fp, 1:use fp
        BB = np.random.choice([0, 1], p=probsBB)  # 0: doesnt block bots, 1 block bots
        num_page_visit = 0
        website_obj = Website(id, SP, FP, BB, num_page_visit)
        list_website.append(website_obj)

    return list_website


def generate_states(list_website: list, num_binary_params: int, params_pages: tuple, params_secu_provider: tuple):
    """

    :param list_website: List of website's
    :param num_binary_params: Amount of binary features
    :param params_pages: Tuple containing (max, step)
    :param params_secu_provider: Tuple containing (max, step)
    :return: A tuple of states
    """

    max_visited_page = params_pages[0]
    range_visited_page = params_pages[1]
    list_range_visited_page = []
    for i in range(0, max_visited_page, range_visited_page):
        list_range_visited_page.append((i, i + range_visited_page - 1))

    max_security_provider = params_secu_provider[0]
    range_page_secu_provider = params_secu_provider[1]
    list_range_page_secu_provider = []
    for i in range(0, max_security_provider, range_page_secu_provider):
        list_range_page_secu_provider.append((i, i + range_page_secu_provider - 1))

    list_states_features = []
    for i in range(num_binary_params):
        list_states_features.append(list(range(2)))

    list_states_features.append(list_range_visited_page)
    list_states_features.append(list_range_page_secu_provider)

    states_tuple = list(itertools.product(*list_states_features))
    random.shuffle(states_tuple)
    states = []
    for state in states_tuple:
        states.append(State(state))

    return states


def generate_actions(list_states: list):
    """

    :param list_states:
    :return:
    """
    dict_actions = {}
    len_states = len(list_states)
    for i in range(len_states + 2):
        if i >= len_states:
            dict_actions[i] = ()
            continue
        dict_actions[i] = list_states[i]

    return dict_actions


def normalized_websites_values(list_website: list, security_providers: dict):
    values = {}
    for website in list_website:
        website.compute_value(security_providers)
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


def websites_to_state(list_websites: list, list_states: list, security_providers: dict):
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
                security_provider = website.security_provider
                if security_provider == 0:
                    state_map[state].append(website)
                    copy_list_website.pop(index)
                else:
                    if security_providers[security_provider].counter_visited in range(state.rangeVisitedSecuProvider[0],
                                                           state.rangeVisitedSecuProvider[1] + 1):
                        state_map[state].append(website)
                        copy_list_website.pop(index)

    return state_map


def upgrade_state_list(website, state, state_map: dict, security_providers: dict):
    state_map[state].pop(state_map[state].index(website))
    for state, _ in state_map.items():
        if state.useFP != website.hasFingerprinting:
            continue
        elif state.useBB != website.blockbots:
            continue
        elif website.amount_page_visited not in range(state.rangeVisitedPage[0], state.rangeVisitedPage[1] + 1):
            continue
        else:
            security_provider = website.security_provider
            if security_provider == 0:
                state_map[state].append(website)
                break
            else:
                if security_providers[security_provider].counter_visited in range(state.rangeVisitedSecuProvider[0],
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

    def __init__(self, n_sites=1000, nSP=10, prob_sp=1 / 10, prob_fp=1 / 4, prob_bb=1 / 50):

        self.security_providers = generate_security_providers(nSP, (0, 10))
        self.sites = generate_fake_sites(n_sites, self.security_providers, prob_sp, prob_fp, prob_bb)
        self.states = generate_states(self.sites, 2)
        self.actions = generate_actions(self.states)

        self.nA = len(self.actions)

        self.states_map = websites_to_state(self.sites, self.states, self.security_provider_freq)
        self.reset()

    def step(self, current_state, action, bot):

        action_bundle = Actions(self.action)
        reward = 0
        done = False
        state = current_state
        # TODO: Make actions, launch bot, wait for return signal and return state, reward, done or no
        if action in range(0, 401):
            state = action
            #TODO: Compute rewards
        else:
            pass
        # How do we know when its done ? Threshold of steps ?

        return state, reward, done

    def _get_obs(self):
        pass

    def reset(self):
        pass

    def render(self, mode='human', close=False):
        pass

#TODO: How to take into consideration that an IP visited a website ?
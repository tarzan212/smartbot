import uuid
import itertools


class SecurityProvider:

    def __init__(self, id_sp: int, grade_sp: int):
        self.id = id_sp
        self.grade = grade_sp

        self.counter_visited = 0
        self.list_websites = []

        self.list_blocked_ip = []

    def block_ip(self, ip, limit_ip:int):
        if len(self.list_blocked_ip) < limit_ip:
            self.list_blocked_ip = [ip] + self.list_blocked_ip
        else:
            self.list_blocked_ip.pop(limit_ip-1)
            self.list_blocked_ip = [ip] + self.list_blocked_ip

    def increment_counter(self):
        self.counter_visited += 1

    def add_website(self, website):
        self.list_websites.append(website)


class Website:

    def __init__(self, uid: uuid, SP: SecurityProvider, FP: bool, BB: bool, page_visited: int):
        self.id = uid
        self.security_provider = SP
        self.hasFingerprinting = FP
        self.blockbots = BB
        self.amount_page_visited = page_visited

    def compute_value(self, security_providers: dict):
        if self.security_provider != 0:
            self.value = security_providers[self.security_provider].grade * 15 + \
                         security_providers[self.security_provider].counter_visited * 10 \
                         + int(self.hasFingerprinting) * 12 + int(self.blockbots) * 20 + \
                         self.amount_page_visited * 10
        else:
            self.value = int(self.hasFingerprinting) * 12 + int(self.blockbots) * 20 + self.amount_page_visited * 10

    def increment_visited_page(self):
        self.amount_page_visited += 1

    def __str__(self):
        return """{ 'id' : %s, 'security_provider' : %d, 'fp' : %r, 'bb' : %r, 'visited' : %d } """ \
                   % (self.id, self.security_provider, self.hasFingerprinting, self.blockbots, self.amount_page_visited)


class State:
    """
    Class representing states.
    One state is represented by binaries representing fingerprinting, blocking bots features.
    And two tuples of ranges of visited pages, and visited pages among one security provider.
    """

    def __init__(self, state: tuple):
        assert len(state) >= 4
        self.useFP = state[0]
        self.useBB = state[1]
        self.rangeVisitedPage = state[2]
        self.rangeVisitedSecuProvider = state[3]

    def __str__(self):
        return """ {'fp' : %r, 'bb' : %r, 'visited' : %s, 'range_secu_provider' : %s }""" \
               % (self.useFP, self.useBB, self.rangeVisitedPage, self.rangeVisitedSecuProvider)


def read_last_entry(filename: str):
    f = open(filename, 'r')
    line = f.readline()
    f.close()

    return line


def update_file(filename: str):
    """
    Util function to push the last used item in a file to its last position. It
    pops it and save it at the end of the file.
    :param filename:
    :return:
    """
    f = open(filename, "w")
    

class Actions:
    """
    Class mapping actions to their behavior and various utils methods.
    """

    def __init__(self, main_actions: list):
        self.main_actions = main_actions

    def generate_actions_combination(self):
        """
        Total amount of combinations is computable by the sum for i to N, with i starting
         at 1 (C(N,i))
        :return: list of tuples of possible combinations
        """
        list_actions = []
        for index in range(1, len(self.main_actions)+1):
            elements = itertools.combinations(self.main_actions, index)
            for element in elements:
                list_actions.append(element)

        return list_actions

    def map_actions(self, actions: tuple, bot: Bot):
        assert actions is type(tuple)

        for action in actions:
            if action == 0:
                continue
                # TODO: How to pick a state ?
                # Randomly ?
            elif action == 1:
                continue
                # TODO: Pick one UA in list of UA in a file
            elif action == 2:
                continue
                # TODO: Pick IP in list of IP in a file

        pass


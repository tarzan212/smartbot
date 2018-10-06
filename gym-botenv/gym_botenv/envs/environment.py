import uuid
import itertools

class Website:

    def __init__(self, uid: uuid, SP: int, FP: bool, BB: bool, page_visited: int):
        self.id = uid
        self.securityProvider = SP
        self.hasFingerprinting = FP
        self.blockbots = BB
        self.amount_page_visited = page_visited

    def compute_value(self, securityprovider: dict, visitedPageSecuProvider: dict):
        if self.securityProvider != 0:
            self.value = securityprovider[self.securityProvider] * 15 + visitedPageSecuProvider[
                self.securityProvider] * 10 \
                         + int(self.hasFingerprinting) * 12 + int(self.blockbots) * 20 + self.amount_page_visited * 10
        else:
            self.value = int(self.hasFingerprinting) * 12 + int(self.blockbots) * 20 + self.amount_page_visited * 10

    def increment_visited_page(self):
        self.amount_page_visited += 1

    def __str__(self):
        return """{ 'id' : %s, 'security_provider' : %d, 'fp' : %r, 'bb' : %r, 'visited' : %d } """ \
                   % (self.id, self.securityProvider, self.hasFingerprinting, self.blockbots, self.amount_page_visited)


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
        for index in range(1,len(self.main_actions)+1):
            elements = itertools.combinations(self.main_actions, index)
            for element in elements:
                list_actions.append(element)

        return list_actions

    def map_action(self, action: tuple):
        pass


class SecurityProvider:
    pass

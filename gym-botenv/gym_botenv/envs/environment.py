import uuid


class Website:

    def __init__(self, uid: uuid, SP: int, FP: bool, BB: bool, page_visited: int):
        self.id = uid
        self.securityProvider = SP
        self.hasFingerprinting = FP
        self.blockbots = BB
        self.amount_page_visited = page_visited


    def __str__(self):
        return """ID : %s \n
                  securityProviderId : %d \n
                  hasFingerprinting : %b \n
                  blockbots : %b \n
                  Amount of visited pages : %d \n
                  """ % (self.id, self.securityProvider, self.hasFingerprinting, self.blockbots, self.amount_page_visited)

    def computeValue(self, securityprovider: dict, visitedPageSecuProvider: dict):
        if self.securityProvider != 0:
            self.value = securityprovider[self.securityProvider] * 15 + visitedPageSecuProvider[
                self.securityProvider] * 10 \
                         + int(self.hasFingerprinting) * 12 + int(self.blockbots) * 20 + self.amount_page_visited * 10
        else:
            self.value = int(self.hasFingerprinting) * 12 + int(self.blockbots) * 20 + self.amount_page_visited * 10

    def incrementVisitedPage(self):
        self.amount_page_visited = self.amount_page_visited + 1;

class State:

    def __init__(self, state: tuple):
        assert len(state) >= 4
        self.useFP = state[0]
        self.useBB = state[1]
        self.rangeVisitedPage = state[2]
        self.rangeVisitedSecuProvider = state[3]

    def __str__(self):
        return """ Fingerprinting capabilities : %r \n
        Blocking bot website : %r \n
        Amount of times visited : %s \n
        Amount of times visited under one security provider : %s \n
        """ % (self.useFP, self.useBB, self.rangeVisitedPage, self.rangeVisitedSecuProvider)


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


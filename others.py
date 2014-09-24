from linker import Linker, Location


#################   START OTHER CLASSES   #################
# Player Faction


class Player(Location):
    def __init__(self, name=''):
        Location.__init__(self, name)
        self.type_string = 'player'
        self.in_team_pref = 'mid'
        self.status = 1
        self.winded = 0
        self.fac_order_pref = 'first'

    def fac_order(self):
        if self.fac_order_pref == 'first':
            return -1
        elif self.fac_order_pref == 'last':
            return 1
        else:
            return 0

    def in_team_order(self):
        if self.in_team_pref == 'first':
            return 0
        elif self.in_team_pref == 'last':
            return 2
        else:
            return 1

    def pretty_name(self):
        return self.des

    def can_see(self, other):
        self.link(other, 'veiw')

    def private_info(self):
        return self.check('veiw')
    
    def stat(self):
        return self.status

    def discard_hand(self):
        for i in self.check('has')[0].check()[:]:
            i.discard()

    def interact(self, other, kind=0):
        x = other.type_string
        if x == 'hand':
            self.aquire(other)
        elif x == 'faction':
            self.link(other)
        elif x == 'token':
            self.greedy_link(other, 'owns', 'owned')
        elif x == 'card':
            self.can_see(other)
        else:
            pass

class Faction(Location):
    def __init__(self, name=''):
        Location.__init__(self, name)
        self.type_string = 'faction'
        self.public = 1
        self.points = 0

    def pretty_name(self):
        return 'The '+self.des

    def score(self, mod =0):
        self.points += mod
        return self.points

    def interact(self, other, kind=0):
        x = other.type_string
        if x == 'token':
            self.link(other)
        elif x == 'player':
            self.link(other)
        else:
            pass

#################   END OTHER CLASSES   #################




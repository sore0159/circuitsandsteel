from linker import Linker, Location
import random


#####################START CARD CLASSES######################
# Card Hand Deck GraveYard

class Card(Linker):
    def __init__(self, graveyard, value=0):
        Linker.__init__(self)
        self.value=value
        self.type_string = 'card'
        self.public = 0
        self.grave_loc = graveyard

    def pretty_name(self):
        return 'a card numbered %d' % self.value

    def reveal(self, reverse=0):
        self.public = 1
        if reverse:
            self.public = 0
            for i in self.check('veiw'):
                self.delink(i, 'veiw')
        return self.value

    def discard(self):
        self.interact(self.grave_loc)

    def interact(self, other, kind=0):
        x = other.type_string
        if x == 'deck':
            other.greedy_link(self)
            self.reveal(1)
            other.shuffle()
        elif x == 'hand' or x == 'graveyard' or x == 'player':
            other.interact(self)
        else:
            pass

class Deck(Location):
    def __init__(self, graveyard, cycles=0):
        Location.__init__(self, 'deck')
        self.type_string = 'deck'
        self.cycles = cycles
        self.graveyard = graveyard

    def top_card(self):
        x = self.check()
        if x:
            return x[0]
        else:
            return []

    def try_recycle(self):
        return self.interact(self.graveyard)

    def pretty_name(self):
        return 'a deck of cards'

    def shuffle(self):
        random.shuffle(self.check())

    def interact(self, other, kind=0):
        x = other.type_string
        if x == 'graveyard':
            if self.cycles:
                self.cycles -= 1
                for i in x.check():
                    i.reveal(1)
                    self.greedy_link(i)
                self.shuffle()
                return 1
            else:
                return 0
        elif x == 'hand':
            return other.interact(self)
        elif x == 'card':
            other.reveal(1)
            return self.greedy_link(other)
        else:
            pass

class Hand(Location):
    def __init__(self, name=''):
        Location.__init__(self, name)
        self.type_string = 'hand'

    def interact(self, other, kind=0):
        x = other.type_string
        if x == 'deck':
            y = other.top_card()
            if y:
                return self.interact(y)
            else:
                other.try_recycle()
        elif x == 'player':
            other.aquire(self)
        elif x == 'card':
            self.greedy_link(other)
            self.check('at')[0].interact(other)
        else:
            pass

class GraveYard(Location):
    def __init__(self, name=''):
        Location.__init__(self, name)
        self.type_string = 'graveyard'

    def pretty_name(self):
        return 'a discard area'

    def interact(self, other, kind=0):
        x = other.type_string
        if x == 'deck':
            self.greedy_link(other.top_card())
        elif x == 'card':
            self.greedy_link(other)
            other.reveal()
        else:
            pass
######################END CARD CLASSES###########################




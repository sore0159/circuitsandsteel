

class Temp(Linker):
    def __init__(self, name=''):
        Linker.__init__(self, name)

    def interact(self, other, kind=0):
        x = other.type_string
        if x == 'opt1':
            self.dostuff(other)
        elif x in ['opt2', 'opt3']:
            self.dostuff(other)
        elif x == 'opt4':
            self.dostuff(othre)
        elif kind != -1:
            other.interact(self, -1)
        else:
            return 0




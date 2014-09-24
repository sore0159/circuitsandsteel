

########################START GENERIC CLASSES##################
# Linker Location

class Linker(object):
    def __init__(self, name=''):
        self.des = name
        self.linked = {}

    def check(self, genus='connected'):
        if genus not in self.linked:
            self.linked[genus] = []
        return self.linked[genus]

    def link(self, other, my_genus='connected', other_genus=''):
        if not other_genus:
            other_genus = my_genus
        else:
            self.check(other_genus)
        self.check(my_genus).append(other)
        other.outside_link(self, other_genus)

    def outside_link(self, other, my_genus):
        self.check(my_genus).append(other)

    def delink(self, other, my_genus='connected', other_genus='', external=0):
        if not other_genus:
            other_genus = my_genus
        x = self.check(my_genus)
        while other in x:
            x.remove(other)
        if not external:
            other.delink(self, other_genus, my_genus, 1)

    def drop_genus(self, genus='connected', other_genus=''):
        if not other_genus:
            other_genus = genus
        for i in self.check(genus):
            self.delink(i, genus, other_genus)
    
    def greedy_link(self, other, genus='connected', other_genus=''):
        if not other_genus:
            other_genus = genus
        other.drop_genus(other_genus, genus)
        self.link(other, genus, other_genus)

    def destroy(self):
        # could miss someone who knows me without my knowledge
        for my_genus in self.linked.keys():
            for other in self.linked[my_genus]:
                for genus in other.linked:
                    other.delink(self, genus, genus, 1)
                self.delink(other, my_genus, my_genus, 1)

    def interact(self, other, kind=0):
        if True:
            return 1
        elif kind != -1:
            other.interact(self, -1)
        else:
            return 0

    def debug(self):
        x = '\n'+'-'*30+'DEBUG'+'-'*30+'\n'
        for i in self.linked.keys():
            x += i+ ': '
            for j in self.linked[i]:
                x += j.type_string + ' '
            x += '\n'
        x += '-'*65+'\n'
        return x

class Location(Linker):
    def __init__(self, name=''):
        Linker.__init__(self, name)
        self.type_string = 'location'

    def aquire(self, obj):
        self.greedy_link(obj, 'has', 'at')

    def one_way_passage(self, other):
        self.outside_link(other, 'connected')

    def contains(self):
        return self.check('contains')

    def interact(self, other, kind=0):
        if other.type_string == 'location':
            if kind:
                self.one_way_passage(other)
            else:
                self.link(other)
        else:
            self.aquire(other)

#########################END GENERIC CLASSES#####################

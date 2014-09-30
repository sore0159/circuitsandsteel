from linker import Linker, Location

#################START GAMEBOARD CLASSES####################
# Token GameSpace
# ideas: where-at, ordered-paths-avail



class Token(Linker):
    def __init__(self, name=''):
        Linker.__init__(self, name)
        self.type_string = 'token'
        self.public = 1
        self.status = 1
        self.winded = 0
        self.dragon = 0
        
    def color(self):
        return self.des

    def pretty_name(self):
        return 'a '+self.des+' colored token'
    
    def take_hit(self):
        self.status -= 1
        self.check('owned')[0].status = self.status
        if self.status < 1:
            self.die()
            return 0
        return 1

    def die(self):
        self.check('owned')[0].discard_hand()
        self.drop_genus('at', 'has')
        self.status = 0
        self.drop_genus()

    def winded(self, set_to=-1):
        if set_to != -1:
            self.winded = set_to
            self.check('owned')[0].winded = set_to
        return self.winded

    def stat(self, status=-1):
        if status != -1:
            self.status = status
            self.check('owned')[0].status = status

        return self.status

    def closest_enemy(self):
        fac = self.check('connected')[0]
        enemy_fac = fac.check('rival')[0]
        my_spot = self.check('at')[0]
        enemy_spots = []
        for i in enemy_fac.check():
            if i.type_string == 'token':
                enemy_spots.append(i.check('at')[0])
        target = (100,100)
        for spot in enemy_spots:
            x = my_spot.how_far(spot)
            if x[0] < target[0]: target = x
        return target

    def faction(self):
        try:
            return self.check()[0]
        except:
            return None

    def home_dir(self):
        en_dir = self.closest_enemy()[1]
        if en_dir == 'up':
            return 'down'
        else:
            return 'up'

    def interact(self, other, kind=0):
        x = other.type_string
        if x == 'faction':
            other.greedy_link(self)
        elif x == 'gamespace':
            check = 0
            for i in other.check('has'):
                for j in self.check():
                    if j.type_string == 'faction':
                        if i not in j.check():
                            check = 1
            if not check:
                other.aquire(self)
        elif x == 'player':
            other.greedy_link(self, 'owns', 'owned')

        elif x == 'option':
            movement = abs(kind)
            if kind > 0: direction = 'up'
            else: direction = 'down'
            for i in range(movement):
                loc = self.check('at')[0]
                y = loc.check(direction)
                if y: 
                    self.interact(y[0])
                else: pass

        else:
            pass

class GameSpace(Location):
    def __init__(self, hue='dark', name=''):
        Location.__init__(self, name)
        self.type_string = 'gamespace'
        self.hue = hue
        self.public = 1

    def pretty_name(self):
        return 'a '+self.hue+' square numbered '+self.des

    def count(self, amount, direction):
        if amount == 0:
            return self
        elif self.check(direction):
            return self.check(direction)[0].count(amount-1, direction)
        else:
            return False

    def val(self):
        return int(self.des)

    def safe_count(self, amount, direction, faction):
        rivals = set (faction.check('rival')[0].check())
        target = self
        for i in range(amount):
            test = target.count(1, direction)
            if test and not set(test.check('has'))&rivals:
                target = test
        return target

    def closest_token(self):
        direction = 'up'
        target = self
        check = target.check('has')
        if check:
            return check[0]
        else:
            token = (20,0)
            i = 0
            dist = 0
            while i < 2:
                next_tar = target.count(1, direction)
                if next_tar == False:
                    i += 1
                    direction = 'down'
                    dist = 0
                    target = self
                else:
                    target = next_tar
                    dist += 1
                    check = target.check('has')
                    if check:
                        i += 1
                        direction = 'down'
                        dist = 0
                        target = self
                        if token[0] > dist:
                            token = (dist, check[0])
        return token[1]


    def how_far(self, spot):
        amount = 0
        direction = 'up'
        target = self
        while target not in [False, spot]:
            target = target.count(1, 'up')
            amount += 1
        if not target:
            target = self
            amount = 0
            direction = 'down'
        while target not in [False, spot]:
            target = target.count(1, 'down')
            amount += 1
        return (amount, direction)

    def interact(self, other, kind=0):
        x = other.type_string
        if x == 'gamespace':
            self.link(other, 'down', 'up')
        elif x == 'token':
            self.aquire(other)
        else:
            pass



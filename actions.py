from linker import Linker, Location
import random



#from actions import Suffering, Attack, Defend, DashingStrike, OptionTray, Move, Push, Retreat, RequestDashingAid, DashingBlock, DenyAid, TakeTheHit

# Make a tray, then pass that tray as 'owner' arg for option creation
# Suffering doesn't itself make a tray, but the game can check for players suffering then make a tray
# Suffering Types:  'attack', 'dashing strike', 'cry'
# cry on multiple people simultan: order by turn order?
#######################  TEMPLATE CLASSES  ##################
class Option(Linker):
    def __init__(self, owner):
        Linker.__init__(self)
        self.type_string = 'option'
        self.link(owner, 'tray', 'option')
        self.movement = 0
        self.des = 'template'
        self.id_string = ''
        self.actor = owner.check('owner')[0].pretty_name()

    def pretty_name(self):
        target = 'nothing'
        print '-'*40
        try:
            print self.target, self.target.pretty_name()
            target = self.target.pretty_name()
        except:
            pass
        return self.des + ' at ' + target

    def iden(self):
        return self.id_string

    def interact(self, other, kind=0):
        x = other.type_string
        if x == 'card':
            other.discard()
        elif x == 'tray':
            other.interact(self)
        elif x == 'token':
            other.interact(self, self.movement)
        elif x == 'suffering':
            other.interact(self, kind)
        else:
            pass

class OptionTray(Location):
    def __init__(self, owner):
        Linker.__init__(self)
        self.type_string = 'tray'
        self.action = 1
        self.link(owner, 'owner', 'tray')
        self.id_num = random.randint(100, 999)
        self.choice_ids = []

    def tray_id(self):
        return self.id_num

    def choices(self):
        return self.check('option')

    def moves(self):
        choices =choices()
        moves = []
        for i in choices:
            if i.id_string[0] == 'm':
                pass

    def attacks(self):
        choices()

    def pushes(self):
        choices()

    def dashes(self):
        choices()

    def tray_destroy(self):
        for i in self.choices():
            i.destroy()
        self.destroy()

    def resolve(self, choice):
        if choice in self.choice_ids:
            x = self.choices()
            for test in x:
                if test.iden() == choice:
                    choice_obj = test
            output = choice_obj.activate()
            self.tray_destroy()

            return output
        else:
            raise Error

    def interact(self, other, kind=0):
        x = other.type_string
        if x == 'option':
            self.greedy_link(other, 'option', 'tray')
        elif x == 'player':
            other.greedy_link(self, 'tray', 'owner')
        else:
            pass

class Suffering(Linker):
    def __init__(self, token, player, suf_type, amount=1, distance=0, victim_cards=[]):
        Linker.__init__(self)
        self.type_string = 'suffering'
        self.link(token, 'token', 'suffering')
        self.link(player, 'player', 'suffering')
        self.amount = amount
        self.suf_type = suf_type
        if suf_type in ['attack', 'dashing strike']:
            self.can_call_for_aid = 1
        else:
            self.can_call_for_aid = 0
        self.distance = distance
        self.victim_cards = victim_cards

    def pretty_name(self):
        return self.suf_type + ' on '+self.check('player')[0].pretty_name()

    def source_player(self):
        if self.suf_type == 'cry':
            return self.check('suffering')[0].check('player')[0]
        else:
            return 0

    def destroy(self):
        for tray in self.check('tray'):
            tray.tray_destroy()

        # could miss someone who knows me without my knowledge
        for my_genus in self.linked.keys():
            for other in self.linked[my_genus]:
                for genus in other.linked:
                    other.delink(self, genus, genus, 1)
                self.delink(other, my_genus, my_genus, 1)


    def interact(self, other, kind=0):
        x = other.type_string
        if x == 'option':
            y = other.sub_type 
            if y == 'relief':
                if self.suf_type == 'cry':
                    self.destroy()
                else:
                    self.amount -= kind
                    for tray in self.check('tray'):
                        pass    
                    if self.amount < 1:
                        self.destroy()
            elif y == 'cry':
                self.can_call_for_aid = 0
            elif y == 'flee' and self.suf_type =='dashing strike':
                self.destroy()
            elif y =='endure':
                self.destroy()
        elif x == 'suffering':
            if self.suf_type == 'cry':
                self.link(other, 'suffering', 'cry')
        else:
            pass



#####################  SPECIFIC TYPES  ####################

  ###################  ATTACK OPTIONS  ##################
class Attack(Option):
    def __init__(self, owner, target, cards):
        Option.__init__(self, owner)
        self.target = target #space
        self.cards = cards
        self.distance = cards[0].value #int  COULD BE PROBLEM WITH POWERS
        self.strength = len(cards)  #int
        self.des = 'attack'
        self.id_string ='a'+str(self.distance)*self.strength
        owner.choice_ids.append(self.id_string)

    def activate(self):
        actor = self.check('tray')[0].check('owner')[0]
        actor.winded = 1
        for i in self.target.check('has'):
            player_i = i.check('owned')[0]
            Suffering(i, player_i, 'attack', self.strength, self.distance)
            for j in self.cards:
                j.discard()
        return actor.pretty_name()+' attacked '+self.target.pretty_name()+' with %d cards' % self.strength

    def pretty_name(self):
        return "Attack spot %s with %d cards (val: %d)" % (self.target.pretty_name(), self.strength, self.distance)


class Move(Option):
    def __init__(self, owner, mover, card, direction):
        Option.__init__(self, owner)
        self.movement = card.value
        ## trickery ##
        en_dir = mover.closest_enemy()[1]
        if direction == en_dir: dir_str = 'f'
        else: dir_str = 'b'
        self.id_string =dir_str+str(self.movement)
        owner.choice_ids.append(self.id_string)
        if direction == 'down': self.movement *= -1
        self.mover = mover
        self.des = 'Move %s %d' % (direction, card.value)
        self.card = card

    def pretty_name(self):
        return self.des

    def activate(self):
        self.interact(self.mover)
        self.check('tray')[0].check('owner')[0].winded = 1
        final_loc = self.mover.check('at')[0].pretty_name()
        self.card.discard()
        return self.actor+' moved to '+final_loc



class DashingStrike(Option):
    def __init__(self, owner, target, mover, direction, move_card, attk_cards):
        Option.__init__(self, owner)
        self.movement = move_card.value
        if direction == 'down': self.movement *= -1
        self.distance = attk_cards[0].value #int
        self.strength = len(attk_cards)  #int
        self.mover = mover
        self.target = target
        self.move_card = move_card
        self.attk_cards = attk_cards
        self.des =  'Dashing Strike, moving forward %d then attacking ' %  move_card.value
        self.id_string ='d'+str(move_card.value)+str(self.distance)*self.strength
        owner.choice_ids.append(self.id_string)

    def pretty_name(self):
        return "Dash forward %d, then strike spot %s with %d cards (val: %d)" % (self.move_card.value, self.target.pretty_name(), self.strength, self.distance)

    def activate(self):
        self.interact(self.mover)
        actor = self.check('tray')[0].check('owner')[0]
        actor.winded = 1
        for i in self.target.check('has'):
            player_i = i.check('owned')[0]
            Suffering(i, player_i, 'dashing strike', self.strength, self.distance)
        self.move_card.discard()
        for i in self.attk_cards:
            i.discard()
        final_loc = self.mover.check('at')[0].pretty_name()
        plural = ''
        if self.strength > 1: plural = 's'
        return actor.pretty_name()+' dashed to '+final_loc+ ' and struck at '+self.target.pretty_name()+' with %d card' % self.strength + plural

class Push(Option):
    def __init__(self, owner, target, card, direction):
        Option.__init__(self, owner)
        #self.distance = card.value
        self.target = target
        self.movement = card.value
        if direction == 'down': self.movement *= -1
        self.card = card
        self.des = 'push'
        self.id_string ='s'+str(card.value)
        owner.choice_ids.append(self.id_string)

    def pretty_name(self):
        return "Shove tokens adjacent away %d spaces" % self.movement
    def activate(self):
        victims = ''
        push_list = self.target.check('has')[:] # need a copy because mod in action?
        for i in push_list:
            victims += i.check('owned')[0].pretty_name() + ', '
            self.interact(i)
            final_loc = i.check('at')[0].pretty_name()
        victims = victims[:-2]
        self.card.discard()
        self.check('tray')[0].check('owner')[0].winded = 1
        return self.actor+' shoved '+victims+' to '+final_loc


  ###################  DEFENSE OPTIONS  ##################

class Defend(Option):
    def __init__(self, owner, suffering, blk_cards):
        Option.__init__(self, owner)
        self.distance = blk_cards[0].value #int
        self.strength = len(blk_cards)  #int
        self.sub_type = 'relief'
        self.suffering = suffering
        self.cards = blk_cards
        self.des = 'parry'
        self.id_string = 'p'
        owner.choice_ids.append(self.id_string)

    def pretty_name(self):
        return "Parry the incoming attack"

    def activate(self):
        self.interact(self.suffering, self.strength)
        for i in self.cards:
            i.discard()
        return self.actor+' parried the attack!'

class Retreat(Option):
    def __init__(self, owner, suffering, mover, direction, move_card):
        Option.__init__(self, owner)
        self.movement = move_card.value #int
        self.sub_type = 'flee'
        self.movement = move_card.value
        if direction == 'down': self.movement *= -1
        self.suffering = suffering
        self.mover = mover
        self.card = move_card
        self.des = 'Retreat %s %d' % (direction, move_card.value)
        self.id_string = 'r'+str(move_card.value)
        owner.choice_ids.append(self.id_string)

    def pretty_name(self):
        return self.des

    def activate(self):
        self.check('tray')[0].check('owner')[0].winded = 1
        self.interact(self.suffering)
        self.interact(self.mover)
        self.card.discard()
        final_loc = self.mover.check('at')[0].pretty_name()
        return self.actor+ ' retreats to '+final_loc

class RequestDashingAid(Option):
    def __init__(self, owner, victim_cards, targets, suffering, amount):
        Option.__init__(self, owner)
        self.sub_type = 'cry'
        self.targets=targets
        self.suffering = suffering
        self.des = 'request help'
        self.needed_dist =  suffering.distance
        self.needed_amount = amount
        self.id_string = 'c'+str(suffering.distance)*amount
        owner.choice_ids.append(self.id_string)
        self.victim_cards = victim_cards

    def pretty_name(self):
        return "Request any who can to dashing block for you, adding %d cards" % self.amount

    def activate(self):
        victims = ''
        for i in self.targets:
            if i.type_string == 'token':
                player_i = i.check('owned')[0]
                victims += player_i.pretty_name()+', '
                cry = Suffering(i, player_i, 'cry', self.needed_amount, self.needed_dist, self.victim_cards)
                cry.interact(self.suffering)
        self.interact(self.suffering)
        victims = victims[:-2]
        plural = ''
        if self.needed_amount > 1: plural = 's'
        return self.actor + ' calls for help, needing %d "%d" card%s from '%(self.needed_amount, self.needed_dist, plural)+victims

class DashingBlock(Option):
    def __init__(self, owner, cry, attack_suf, mover, direction,  move_card, blk_cards):
        Option.__init__(self, owner)
        self.distance = blk_cards[0].value
        self.strength = len(blk_cards)
        self.cards = blk_cards
        if move_card:
            self.cards.append( move_card)
            self.movement = move_card.value
            if direction == 'down': self.movement *= -1
        else:
            self.movement = 0
        self.sub_type = 'relief'
        self.cry = cry
        self.victim_cards = cry.victim_cards
        self.attack_suf = attack_suf
        self.mover = mover
        self.cards += self.victim_cards
        self.des = 'Dashing Block, moving %s %d then adding %d cards valued %d to the block' % (direction, abs(self.movement), self.strength, self.distance)
        self.id_string = 'i'+str(abs(self.movement))+str(self.distance)*self.strength
        owner.choice_ids.append(self.id_string)


    def pretty_name(self):
        return self.des

    def activate(self):
        for i in self.attack_suf.check('cry'):
            i.interact(self)
        if self.movement: self.interact(self.mover)
        final_loc = self.mover.check('at')[0].pretty_name()
        self.interact(self.attack_suf, self.strength+len(self.victim_cards))
        for i in self.cards:
            i.discard()
        plural = ''
        if self.strength > 1: plural = 's'
        return self.actor+' dashes to '+final_loc+' and interposes with %d card'%self.strength +plural+'!'

  #################  DENY OPTIONS  ###################

class DenyAid(Option):
    def __init__(self, owner, suffering):
        Option.__init__(self, owner)
        self.suffering = suffering
        self.sub_type = 'relief'
        self.des = 'deny aid'
        self.id_string = 'x'
        owner.choice_ids.append(self.id_string)

    def pretty_name(self):
        return "Deny the request for aid."

    def activate(self):
        self.suffering.interact(self)
        return self.actor+' denies the call for aid'
        

class TakeTheHit(Option):
    def __init__(self, owner, target, suffering):
        Option.__init__(self, owner)
        self.target = target
        self.sub_type = 'endure'
        self.suffering = suffering
        self.des = 'take the hit'
        self.id_string = 't'
        owner.choice_ids.append(self.id_string)

    def pretty_name(self):
        return "Take the Hit"
    def activate(self):
        self.target.take_hit()
        self.interact(self.suffering)
        return self.actor + ' takes the blow!'





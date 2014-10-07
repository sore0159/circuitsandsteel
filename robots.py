import random
import printers
import game
import copy

   ###################  BEGIN ROBOT INTERFACE PROTOCOL  ##################
def robot_control(snapshot, flag=''):
    snapshot_list = []
    if 'choices' in snapshot:
        controller = snapshot[snapshot['choices'][0]]['controller']
    else:
        controller = 'human'
    while controller != 'human':
        print "CONTROLLER: ", controller
        if controller in robot_lookup_table:
            robot_name = snapshot['choices'][0]
            robot_snap = game.player_snap_from_master(snapshot, robot_name)
            robot = robot_lookup_table[controller]()
            robot_choice = robot.make_choice(robot_snap)
            print "%s CHOICE: %s"%(robot_name, robot_choice)
            snapshot = game.do_things(snapshot, robot_choice)
            snapshot_list.append(copy.deepcopy(snapshot))
            if flag: print printers.print_from_snapshot(snapshot)
            if 'choices' in snapshot:
                controller = snapshot[snapshot['choices'][0]]['controller']
            else:
                controller = 'human'
        else:
            print '\n+++++\n'+controller+'\n++++++\n'
            raise Exception # Bad Robot Type
    print "CONTROLLER: ", controller
    return snapshot_list
   ###################  END ROBOT INTERFACE PROTOCOL  ##################

  ################### BEGIN ROBOT PARTS #################

def which_kind(options):  # works for lists and dictionaries I think!
    opt_letters = set(val[0] for val in options)
    if set(['a', 's', 'b', 'f', 'd']) & opt_letters:
        return 1
    elif set(['p', 'r', 'c', 't']) & opt_letters:
        return 2
    elif set(['i', 'x'])  & opt_letters:
        return 3
    else:
        return 0

def cards_left(snapshot):
    if snapshot['game'][0] in [0, 2]:
        total_cards = 25
    elif snapshot['game'][0] == 5 :
        total_cards = 40
    else:
        total_cards = 50
    num_each = total_cards/5
    counted = [None]+[num_each]*5
    for card in snapshot['grave'][0]:
        counted[card] -= 1
    for card in snapshot['mycards'][1]:
        counted[card] -= 1
    return counted

def pow(option):  # Be aware you are overwriting a builtin
    if option[0] == 'a': opt_l = len(opt)
    elif option[0] == 'd': opt_l = len(opt) - 1
    else: opt_l = 0
    return opt_l

def val(option):
    return option[-1]

def mov(option):
    if option[0] in ('r', 'b', 'f', 'd', 's', 'i'):  # s?
        return option[1]
    else:
        return 0

def sort_pow(options):
    # attacks, dashing strikes
    sorted_opts = []
    for opt in options:
        check_len = len(sorted_opts)
        for s_opt in sorted_opts:
            if pow(s_opt[0]) == pow(opt):
                s_opt.append(opt)
        if len(sorted_opts) == check_len:
            sorted_opts.append([opt])
    return sorted_opts

def non_dumb(snapshot):
    opts = snapshot['choices'][1][:]
    if len(opts) > 1:
        bad_choices = []
        if 't' in opts: bad_choices += 't'
        if am_i_adj_en(snapshot):
            for choice in opts:
                if choice[0] == 'f':
                    bad_choices.append(choice)
        if am_i_at_edge(snapshot):
            for choice in opts:
                if choice[0] == 'b':
                    bad_choices.append(choice)
        #print "Bad choices: ", bad_choices
        #print "Considering: ", list( set(opts) ^ set(bad_choices))
        return list( set(opts) ^ set(bad_choices))
    else:
        return opts
    
def am_i_adj_en(snapshot):
    my_name = snapshot['choices'][0]
    my_spot = snapshot[my_name]['spot']
    en_faction = 'leftfaction'
    if my_name in snapshot['leftfaction']['players']: en_faction = 'rightfaction'
    check = 0
    for enemy in snapshot[en_faction]['players']:
        if snapshot[enemy]['spot'] and abs(snapshot[enemy]['spot'] - my_spot) == 1:
            check = 1
    return check

def am_i_at_edge(snapshot):
    my_name = snapshot['choices'][0]
    my_spot = snapshot[my_name]['spot']
    if my_spot in [1,18]:
        return 1
    else:
        return 0

def default_def(opts):  # opts in dictionary form
    if 'p' in opts:
        best = 'p'
    elif 'r' in opts:
        best = opts[0]
    else:
        best = 't'
    return best

def default_atk(opts):
    if 'a' in opts:
        atks = opts['a']
        best = atks[0]
    elif 'd' in opts:
        dashs = opts['d']
        best = dashs[-1]  # highest movement, highest val, highest pow
    elif 's' in opts:
        shoves = opts['s']
        best = shoves[-1]
    else:
        moves = opts['f']
        best = move[-1]

def opts_dictionary(snapshot):
    choice_list = snapshot['choices'][1]
    choice_dict = {}
    for choice in choice_list:
        if choice[0] not in choice_dict:
            choice_dict[choice[0]] = []
        choice_dict[choice[0]].append(choice)
    for choice in choice_dict:
        choice_dict[choice].sort()  # I think this sorts each entry, null first
                                    # so move, val, pow
    return choice_dict


  ##################### END ROBOT PARTS #################
  ####################  BEGIN STOCK ROBOT  ####################
class Robot(object):
    def __init__(self, name='Stock Robot'):
        self.name = self.check_name(name)
        self.color_pref = ['red', 'blue', 'green', 'purple']
        self.fac_order_pref = 'first'
        self.in_team_pref = 'mid'
        self.faction = 'Stock Faction'

    def check_name(self, name):
        prohibited = ['log', 'turnorder', 'whosturn', 'imp', 'deck', 'mycards', 'choices', 'dragon', 'grave', 'game', 'rightfaction', 'leftfaction']
        if name in prohibited:
            raise Exception # bad name!
        else:
            return name

    def make_choice(self, snapshot):
        opts_d = opts_dictionary(snapshot)
        kind = which_kind(opts_d)
        if kind == 1:
            choice = self.default_atk(snapshot, opts_d)
        elif kind == 2:
            choice = self.default_def(snapshot, opts_d)
        elif kind == 3:
            choice = self.default_cry(snapshot, opts_d)
        return choice
    def default_atk(self, snapshot, opts_d):
        # active choices =['a', 'd', 's', 'f', 'b' ]
        return random.choice(non_dumb(snapshot))
    def default_def(self, snapshot, opts_d):
        # defensive choices =['r', 'p', 't', 'c']
        return random.choice(non_dumb(snapshot))
    def default_cry(self, snapshot, opts_d):
        # cry respond choices = ['x', 'i']
        return random.choice(non_dumb(snapshot))

    def forder_vote(self, snapshot):
        return self.fac_order_pref

    def torder_vote(self, snapshot):
        return self.in_team_pref

  ####################  END STOCK ROBOT  ####################

  ###################  BEGIN REFERENCE HUMOR  ##################
  # Also puns

class LittleBobby(Robot):
    def __init__(self):
        Robot.__init__(self, 'Little Bobby Tables')
        self.faction='Ridgeview Elementary'

    def make_choice(self, snapshot):
        my_choice = ''
        my_name = snapshot['choices'][0]
        if my_name in snapshot['rightfaction']['players']:
            my_faction = 'rightfaction'
        else:
            my_faction = 'leftfaction'
        choice_list = snapshot['choices'][1]
        choice_dict = {}
        for choice in choice_list:
            if choice[0] not in choice_dict:
                choice_dict[choice[0]] = []
            choice_dict[choice[0]].append(choice)
        #possible_choices =['f', 'r', 'a', 'd', 'b', 't', 'x', 'p', 'i', 'c', 's']
        #split into: 
            # active choices =['a', 'd', 's', 'f', 'b' ]
        if 'a' in choice_dict:
            attacks = choice_dict['a']
            attacks.sort()
            longest = ['']
            for choice in attacks:  # find the strongest
                if len(choice) > len(longest[0]):
                    longest = [choice]
                elif len(choice) == len(longest[0]):
                    longest.append(choice)
            my_choice = 'z6'
            for choice in longest: # of them pick the closest
                if choice[1] < my_choice[1]:
                    my_choice = choice
        elif 'd' in choice_dict:
            my_choice = 'd6'
            for choice in choice_dict['d']:
                if choice[1] < my_choice[1]:  # move the least
                    my_choice = choice
                elif choice[1] == my_choice and len(choice) > len(mychoice):
                    my_choice = choice        # hit the hardest
        elif 'f' in choice_dict:
            my_choice = 'f0'
            for choice in choice_dict['f']: #move toward the enemy the fastest
                if choice[1] > my_choice[1]:
                    my_choice = choice
        # defensive choices =['r', 'p', 't', 'c']
        elif 'p' in choice_dict:
            my_choice = 'p'
        elif 'r' in choice_dict:
            retreats = choice_dict['r']
            retreats.sort()
            my_choice = retreats[-1] # retreat the farthest away you can
        elif 't' in choice_dict:
            my_choice = 't'
        # cry respond choices = ['x', 'i']
        elif 'x' in choice_dict:
            my_choice = 'x'
        return my_choice

class RobotChicken(Robot):
    def __init__(self):
        Robot.__init__(self, 'Robot Chicken')
        self.faction='Acme Comedy Club'
        self.color_pref = ['yellow', 'blue', 'green', 'purple']
        self.fac_order_pref = 'last'
        self.in_team_pref = 'last'

class BadRobot(Robot):
    def __init__(self):
        Robot.__init__(self, 'Bad Robot')
        self.faction='Acme Comedy Club'
        self.color_pref = ['taupe', 'mauve', 'olive', 'cyrulian']
        self.fac_order_pref = 'mid'
        self.in_team_pref = 'mid'

    def make_choice(self, snapshot):
        return random.choice(snapshot['choices'][1])

class Rockem(Robot):
    def __init__(self):
        Robot.__init__(self, 'Rockem')
        self.faction='Old Timers'
        self.color_pref = ['red', 'orange', 'tan', 'grey']
        self.fac_order_pref = 'first'
        self.in_team_pref = 'last'

class Sockem(Robot):
    def __init__(self):
        Robot.__init__(self, 'Sockem')
        self.faction='Old Timers'
        self.color_pref = ['blue', 'navy', 'green', 'gray']
        self.fac_order_pref = 'first'
        self.in_team_pref = 'first'

class Bender(Robot):
    def __init__(self):
        Robot.__init__(self, 'Bending Unit 22')
        self.faction='The Future'
        self.color_pref = ['grey', 'gray', 'silver', 'metal']
        self.fac_order_pref = 'mid'
        self.in_team_pref = 'mid'

class Roomba(Robot):
    def __init__(self):
        Robot.__init__(self, 'Roomba')
        self.faction='Old Timers'
        self.fac_order_pref = 'first'
        self.in_team_pref = 'first'

class EyeRobot(Robot):
    def __init__(self):
        Robot.__init__(self, 'Eye Robot')
        self.faction='The Future'
        self.fac_order_pref = 'first'
        self.in_team_pref = 'last'

  ##################### END REFERENCE HUMOR ###################
class Human(object):   # need something for prefs, maybe user form fillout later
    def __init__(self):
        self.name = 'Player'
        self.faction='Humans Rule'
        self.fac_order_pref = 'first'
        self.in_team_pref = 'mid'
        self.color_pref = ['purple', 'red', 'blue', 'green', 'yellow']

    def forder_vote(self, snapshot):
        return self.fac_order_pref

    def torder_vote(self, snapshot):
        return self.in_team_pref


robot_lookup_table = {'human':Human,'LittleBobby':LittleBobby, 'RobotChicken':RobotChicken, 'BadRobot':BadRobot, 'Rockem':Rockem, 'Sockem':Sockem, 'Bender':Bender, 'Roomba':Roomba, 'EyeRobot':EyeRobot}

def random_robots(num=4, table=robot_lookup_table):
    if num > 5: num = 5
    table2 = table.keys()
    table2.remove('human')
    return random.sample(table2, num)

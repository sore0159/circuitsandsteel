
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
        my_choice = ''
        my_name = snapshot['choices'][0]
        if my_name in snapshot['rightfaction']['players']:
            my_faction = 'rightfaction'
            en_dir = 'u'
        else:
            my_faction = 'leftfaction'
            en_dir = 'd'
        choice_list = snapshot['choices'][1]
        choice_dict = {}
        for choice in choice_list:
            if choice[0] not in choice_dict:
                choice_dict[choice[0]] = []
            choice_dict[choice[0]].append(choice)
        #possible_choices =['r', 'a', 'd', 'b', 't', 'x', 'p', 'm', 'c', 's']
        #split into: 
            # active choices =['a', 'd', 'p', 'm' ]
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
                    
        elif 'm' in choice_dict:
            my_choice = 'm'+en_dir+'0'
            for choice in choice_dict['m']: #move toward the enemy the fastest
                if choice[1] == en_dir and choice[2] > my_choice[2]:
                    my_choice = choice
        # defensive choices =['r', 'b', 't', 'c']
        elif 'b' in choice_dict:
            my_choice = 'b'
        elif 'r' in choice_dict:
            retreats = choice_dict['r']
            retreats.sort()
            my_choice = retreats[-1] # retreat the farthest away you can
        elif 't' in choice_dict:
            my_choice = 't'
        # cry respond choices = ['x', 's']
        elif 'x' in choice_dict:
            my_choice = 'x'
        return my_choice
  ####################  END STOCK ROBOT  ####################

class LittleBobby(Robot):
    def __init__(self):
        Robot.__init__(self, 'Little Bobby Tables')
        self.faction='Ridgeview Elementary'

robot_lookup_table = {'LittleBobby':LittleBobby}

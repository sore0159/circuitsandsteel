import cPickle as pickle
import copy
import random
from robots import robot_lookup_table
import printers


  ##################  START SNAPSHOT GEN  ###############
######################## START GAME ASSEMBLY ############################
def assemble_game(player_list=['human']*5, game_type=0, game_id=0 ):
    #########  START ARGUMENT SCRUBBING  #########
    game_id = str(game_id)
    if game_id[0] == 'g':
        game_id = game_id[1:]
    try:
        game_id = int(game_id)
    except:
        game_id = 0

    try:
        game_type = int(game_type)
    except:
        game_type = 0
    for player in player_list[:]:
        if player not in robot_lookup_table:
            player_list.remove(player)
    while len(player_list) < 5:
        player_list.append('human')
    #########  END ARGUMENT SCRUBBING  #########
    snapshot = {'game':(game_type, game_id)}
    # Game log
    logstrings = [
        'One Vs One',
        'Two Vs Two',
        'One Vs One, With Powers',
        'Two Vs Two, With Powers',
        'Two Vs DRAGON',
        'Three Vs DRAGON',
        'Four Vs DRAGON' ]
    game_log = ['Game Created: '+ logstrings[game_type]]
    snapshot['log'] = game_log

    # How many players
    if game_type in [0,2]: num_players = 2
    elif game_type in [1,3]: num_players = 4
    else: num_players = game_type -1
    # what are the factions?
    if game_type in [1,3]: fac1_size = num_players -2
    else: fac1_size = num_players -1
    # is there a dragon?
    if game_type in [4,5,6]: dragon = 1
    else: dragon = 0 
    # are there powers?  HAH
    if game_type in [0,1]: powers = 0
    else: powers = 1

    # Okay let's create player dictionaries
    players = []
    for i in range(num_players):
        players.append({'controller':player_list[i]})
    # vote on names
    name_vote(players)
    # vote on colors
    color_vote(players)
    # assign rand IDs
    id_list = [0]
    for i in range(len(players)):
        rand_num = 0
        while rand_num in id_list:
            rand_num = random.randint(10,99)
        id_list.append(rand_num)
        players[i]['id_num'] = rand_num
        
    # assign l/r faction (also dragon setting)
    random.shuffle(players)
    snapshot['leftfaction'] = {'name':'templeft', 'score':0, 'players':[]}
    snapshot['rightfaction'] = {'name':'tempright', 'score':0, 'players':[]}
    for player in players[:fac1_size]:
        snapshot['leftfaction']['players'].append(player['name'])
        player['dragon']=0
    for player in players[fac1_size:]:
        snapshot['rightfaction']['players'].append(player['name'])
        if dragon: 
            player['dragon']=1
            player['color'] = 'black'
        else: player['dragon']=0
    # put player dictionaries in the snapshot
    for player in players:
        player['num_cards'] = 0
        player['health'] = 0
        player['winded'] = 0
        player['cards'] = []
        player['spot'] = None
        snapshot[player['name']] = player
        del player['name']

    # vote on fac name
    faction_name_vote(snapshot)
    # All done!  Let's start the game
    start_match(snapshot)
    return snapshot

  #####################  START ASSEMBLY TOOLS  ####################
def name_vote(players):
    random.shuffle(players)
    name_list = []
    prohibited = ['log', 'turnorder', 'whosturn', 'imp', 'deck', 'mycards', 'choices', 'dragon', 'grave', 'game', 'rightfaction', 'leftfaction']
    for player in players:
        flag = 0
        robot = robot_lookup_table[player['controller']]()
        name = getattr(robot, 'name', '')
        if not name or name in prohibited: name = 'Anonymous Robot'
        while name in name_list:
            if flag:
                name = name[:-1]+str(flag+2)
            else:
                name = name+' '+str(flag+2)
            flag += 1
        name_list.append(name)
        player['name'] = name
    return players # not needed?

def color_vote(players):
       #### Matrix Assembly ####
    num_players = len(players)
    color_defaults = ['green', 'yellow', 'maroon', 'blue', 'purple']
    color_matrix = []
    for player in players:
        # collect
        robot = robot_lookup_table[player['controller']]()
        temp_color_pref = robot.color_pref
        # scrub
        temp_color_pref = list(set(temp_color_pref)) # remove duplicates
        for j in range(len(temp_color_pref)):
            color = temp_color_pref[j]
            if not color or color == 'black':  # clean bad entries
                temp_color_pref.pop(j)
        if len(temp_color_pref) >num_players:  # cut
            temp_color_pref = temp_color_pref[:num_players]
        elif len(temp_color_pref) < num_players:  # grow
            for color in color_defaults:
                if color not in temp_color_pref and len(temp_color_pref)<num_players:
                    temp_color_pref.append(color)
        #add
        color_matrix.append(temp_color_pref)
     #### Voting ####
     # color_matrix should be nxn [i] = player [j] = jth fav color
    color_list = [0,0,0,0,0]
    for vote_num in range(num_players):
        vote_dict = {}
        for p_num in range(num_players):
            if not color_list[p_num]: # if she doesn't have a color
                color = color_matrix[p_num][vote_num] # pick her ith fav color
                if color not in color_list: # if it's free
                    if color not in vote_dict:
                        vote_dict[color] = []
                    vote_dict[color].append(p_num)  # she votes for it
        #after all votes collected
        for color in vote_dict:
            winner = random.choice(vote_dict[color]) 
            if 'color' not in players[winner]:
                color_list[winner]= color
                players[winner]['color'] = color
            else:
                raise Exception # Bad voting
    return players  #not needed?

def faction_name_vote(snapshot):
    name_suggestions = {'l':[], 'r':[]}
    for faction in ['leftfaction', 'rightfaction']:
        players = snapshot[faction]['players']
        for player in players:

            robot = robot_lookup_table[snapshot[player]['controller']]()
            suggestion = getattr(robot, 'faction', '')
            if suggestion:  # can leave blank if they don't care about faction
                name_suggestions[faction[0]].append(suggestion)
    # check if either side doesn't care
    defaults = ['U.S. Robots', 'The Academy'] #, 'Unaligned', 'Mavericks', 'Defective Robot Alliance', 'Battlebots' ]
    if not name_suggestions['l'] and not name_suggestions['r']:
        random.shuffle(defaults)
        snapshot['leftfaction']['name'], snapshot['rightfaction']['name'] = defaults
    elif not name_suggestions['r']:
        l_name = random.choice(name_suggestions['l'])
        snapshot['leftfaction']['name']= l_name
        if l_name == defaults[0]:
            snapshot['rightfaction']['name']= defaults[1]
        else:
            snapshot['rightfaction']['name']= defaults[0]
        
    elif not name_suggestions['l']:
        r_name = random.choice(name_suggestions['r'])
        snapshot['rightfaction']['name']= r_name
        if r_name == defaults[0]:
            snapshot['leftfaction']['name']= defaults[1]
        else:
            snapshot['leftfaction']['name']= defaults[0]
    # if both sides care:
    elif name_suggestions['l'] == name_suggestions['r'] and len(name_suggestions['l']) == 1:  # but they both only want the same one name
        if name_suggestions['l'][0] == defaults[0]:
            defaults = [name_suggestions['l'][0], defaults[1]]
        else:
            defaults = [name_suggestions['l'][0], defaults[0]]
        random.shuffle(defaults)
        snapshot['leftfaction']['name'], snapshot['rightfaction']['name'] = defaults
    else:  # otherwise
        l_name = r_name = 0
        while l_name == r_name:
            l_name = random.choice(name_suggestions['l'])
            r_name = random.choice(name_suggestions['r'])
        snapshot['leftfaction']['name'], snapshot['rightfaction']['name'] = l_name, r_name
    return snapshot

  #####################  END ASSEMBLY TOOLS  ####################
######################## END GAME ASSEMBLY ############################

 #####################  START MATCH SETUP  #####################

def start_match(snapshot, lastwinner=''):
    game_type = snapshot['game'][0]
    #what round is it?  Ignores ties
    match_num = 1 + snapshot['leftfaction']['score'] + snapshot['rightfaction']['score']
    snapshot['log'].append('Round %d Begins!'% match_num)
    # which side goes first
    if lastwinner == 'l' or lastwinner == 'leftfaction':
        lastwinner='leftfaction'
    elif lastwinner == 'r' or lastwinner == 'rightfaction':
        lastwinner='rightfaction'
    elif not lastwinner or lastwinner == 't':
        if random.choice([0,1]):
            lastwinner='leftfaction'
        else:
            lastwinner='rightfaction'
    else:
        print lastwinner
        raise Exception # Bad last winner
    if game_type not in [4,5,6]:
        if lastwinner == 'leftfaction':
            l_first = not forder_vote(snapshot, 'rightfaction')
        else:
            l_first = forder_vote(snapshot, 'leftfaction')
    else:
        l_first = 1  
    # who goes first in-team
    l_order = torder_vote(snapshot, 'leftfaction')
    r_order = torder_vote(snapshot, 'rightfaction')
    # put in all together!
    turn_order = []
    if l_first: 
        if game_type in [4,5,6]: 
            turn_order = l_order+r_order # dragon goes after all
        else:
            for i in range(len(l_order)): turn_order.extend([l_order[i], r_order[i]])
    else:
        for i in range(len(l_order)): turn_order.extend([r_order[i], l_order[i]])
    log_string = "Turn Order Set: "
    for player in turn_order:
        log_string += player+', '
    log_string = log_string[:-2]
    snapshot['log'].append(log_string)
    snapshot['turnorder']= turn_order
    snapshot['whosturn']= turn_order[0]
    if game_type in [5,6]: cycles = 1
    else: cycles = 0
    if game_type in [1,3,4,6]: num_cards = 10
    elif game_type == 5: num_cards = 8
    else: num_cards = 5
    deck = []
    for i in range(1,6):
        for j in range(num_cards):
            deck.append(i)
    random.shuffle(deck)
    for p in player_list(snapshot):
        player = snapshot[p]
        if player['dragon']:
            player['health'] = game_type - 2
            player['num_cards'] = game_type + 3
        else:
            player['health'] = 1
            player['num_cards'] = 5
        player['cards']= []
        for i in range(player['num_cards']):
            player['cards'].append(deck.pop())
        if p in snapshot['leftfaction']['players']:
            player['spot'] = 1
        else:
            player['spot'] = 18
    snapshot['deck'] = (deck, cycles)
    snapshot['grave'] = []
    action_choices(snapshot)
    return snapshot

  #####################  START MATCH SETUP TOOLS  ####################
def forder_vote(snapshot, faction):
    players = snapshot[faction]['players']
    vote_total = 0
    for player in players:
        robot = robot_lookup_table[snapshot[player]['controller']]()
        vote = robot.forder_vote(snapshot)
        if vote == 'first':
            vote_total += 1
        elif vote == 'last':
            vote_total -= 1
    if vote_total == 0:
        me_first = random.choice([0,1])
    elif vote_total < 0:
        me_first = 0
    else:
        me_first = 1
    return me_first

def torder_vote(snapshot, faction):
    players = snapshot[faction]['players']
    if len(players) == 1:
        return players
    else:
        sorted_players = [[],[],[]]
        for player in players:
            robot = robot_lookup_table[snapshot[player]['controller']]()
            vote = robot.torder_vote(snapshot) 
            if vote == 'first':
                sorted_players[0].append(player)
            elif vote == 'last':
                sorted_players[2].append(player)
            else:
                sorted_players[1].append(player)
    turn_order = []
    for i in range(3):
        random.shuffle(sorted_players[i])
        turn_order += sorted_players[i]
    return turn_order

def player_list(snapshot):
    return snapshot['leftfaction']['players'] + snapshot['rightfaction']['players']

  #####################  END MATCH SETUP TOOLS  ####################

####################  END MATCH SETUP  ########################


  ##################  START SNAPSHOT PROCESSING  #############

def action_choices(snapshot):
    choices = []
    player = snapshot['whosturn']
    my_spot = snapshot[player]['spot']
    if player in snapshot['leftfaction']['players']:
        enemies = snapshot['rightfaction']['players']
    else:
        enemies = snapshot['leftfaction']['players']
    dist_list = [abs(my_spot - snapshot[enemy]['spot']) for enemy in enemies]
    card_count = [None, 0, 0, 0, 0, 0]
    cards = snapshot[player]['cards']
    for card in cards:
        card_count[card] += 1
    #move
    for card in range(1,6):
        if card_count[card]:
            choices.extend(['f%d'%card, 'b%d'%card])
    #shove
    if 1 in dist_list:
        for card in range(1,6):
            if card_count[card]:
                choices.append('s%d'%card)
    #attack
    for card in range(1,6):
        if card_count[card] and card in dist_list:
            for num in range(card_count[card]):
                choices.append('a'+str(card)*(num+1))
    #dashing strike
    for move_card in range(1,6):
        if card_count[move_card]:
            duplicate_count = card_count[:]
            duplicate_count[move_card] -= 1
            moved = min( min(dist_list)-1, move_card)
            for card in range(1,6):
                if duplicate_count[card] and card + moved in dist_list:
                    for num in range(duplicate_count[card]):
                        choices.append('d'+str(move_card)+str(card)*(num+1))
    choice_tuple = (player, choices)
    snapshot['choices'] = choice_tuple


def suffering_choices(snapshot):
    if 'imp' not in snapshot:
        raise Exception # No suffering to analyse!
    cry = 0
    attks = []
    for suffering in snapshot['imp']:
        if suffering['crier']:
            if cry:
                raise Exception # Multiple cries!
            else:
                cry = suffering
        else:
            attks.append(suffering)
    choices = []
    if cry:
        # deny
        choices.append('x')
        # interpose
        dash_spot = snapshot[cry['crier']]['spot']
        actor = cry['victims'][0]
        my_spot = snapshot[actor]['spot']
        my_cards = snapshot[actor]['cards']
        dist = abs(dash_spot - my_spot)
        needed = cry['cards'] + [dist]
        if needed < my_cards:
            choices.append('i'+str(dist)+str(needed[0])*len(needed-1))
    else:
        #pick the best
        # furthest back, then turn order
        victim = (0, [])
        for i in range(len(attks)):
            target = attks[i]['victims']
            dist_from_en = 0
            if dist_from_en > victim[0]:
                victim[0] = dist_from_en
                victim[1] = [(target,i)]
            if dist_from_en == victim[0]:
                victim[1].append((target,i))
        target = (0,20, 10)
        for j in victim[1]:
            check_guy, suff_index = j[0], j[1]
            check_order = snapshot['turnorder'].index(check_guy)
            if check_order < target[1]: target = (check_guy, check_order, suff_index)
        print attks, target[2]
        attack = attks[target[2]]
        # now analyze:
        actor = attack['victims']
        my_spot = snapshot[actor]['spot']
        my_cards = snapshot[actor]['cards']
        counted_cards = [None, 0, 0, 0, 0, 0]
        for i in my_cards:
            counted_cards[i] += 1
        # takehit
        choices.append('t')
        # retreat
        if attack['can_retreat'] and my_spot not in [1,18]:
            for card in range(1,6):
                if counted_cards[card]:
                    choices.append('r'+str(card))
        # parry
        needed = attack['cards']
        if counted_cards[needed[0]] >= len(needed):
            choices.append('p')
        # cry
        if attack['can_cry']:
            can_cry = 0
            if actor in snapshot['leftfaction']['players']: 
                check = range(max(1, my_spot-5),my_spot+1)
                allies = snapshot['leftfaction']['players']
            else: 
                check = range(my_spot, min(my_spot + 6, 19))
                allies = snapshot['rightfaction']['players']
            for player in allies:
                if snapshot[player]['spot'] in check:
                    can_cry = 1
                    break
            if can_cry:
                min_needed = max(len(needed)-counted_cards[needed[0]], 0)
                for i in range(min_needed, len(needed)+1):
                    choices.append('c'+str(needed[0])*i)
    snapshot['choices'] = (actor, choices)


def refresh(snapshot, player):
    snapshot[player]['winded'] = 0
    game_type = snapshot['game'][0]
    if game_type in [4,5,6] and not snapshot[player]['dragon']:
        if player == snapshot['turnorder'][-2]:
            for ally in snapshot['leftfaction']['players']:
                refill_hand(snapshot, ally)
    else:
        refill_hand(snapshot, player)

def refill_hand(snapshot, player):
    game_type = snapshot['game'][0]
    dragon = snapshot[player]['dragon']
    hand = snapshot[player]['cards']
    hand_len = len(hand)
    deck = snapshot['deck'][0]
    if not dragon:
        max_hand = 5
    else:
        max_hand = game_type + 3
    if hand_len > max_hand: hand_len = max_hand
    elif max_hand - hand_len > len(deck): hand_len= max_hand-len(deck)
    for i in range(max_hand-hand_len):
        hand.append(deck.pop())

def end_turn(snapshot):
    if 'imp' in snapshot or 'choices' in snapshot:
        raise Exception # Turn is not over yet!
    cur_player = snapshot['whosturn']
    turn_order = snapshot['turnorder']
    snapshot[cur_player]['winded'] = 1  # Just for a second

    while snapshot[cur_player]['winded'] and not match_over(snapshot):
        refresh(snapshot, cur_player)
        #who's next?
        if cur_player == turn_order[-1]:
            cur_player = turn_order[0]
        else:
            index = turn_order.index(cur_player)
            cur_player = turn_order[index+1]
    snapshot['whosturn'] = cur_player
    if match_over(snapshot):
        conclude_match(snapshot)
    else:
        action_choices(snapshot)

def match_over(snapshot):
    over = 0
    for faction in 'leftfaction', 'rightfaction':
        alive = 0
        for player in snapshot[faction]['players']:
            alive += snapshot[player]['health']
        if not alive:
            if over:
                raise Exception # Everyone dead on both sides?
            over = 1
    if not over:
        deck_len, cycles = snapshot['deck']
        if not deck_len and not cycles:
            over = 1
        else: # Game on!
            over = 0
    return over 

def conclude_match(snapshot):
    match_winner = 0
    rival = {'l':'r', 'r':'l'}
    for faction in 'leftfaction', 'rightfaction':
        alive = 0
        for player in snapshot[faction]['players']:
            alive += snapshot[player]['health']
        if not alive:
            if match_winner:
                raise Exception # Everyone dead on both sides?
            match_winner = rival[faction[0]]
    if not match_winner:
        deck_len, cycles = snapshot['deck']
        if not deck_len and not cycles:
            match_winner = timeout(snapshot)  # 't', 'l', 'r'
        else:
            raise Exception # Game Called Prematurely
    if match_winner == 'l':    
        snapshot['leftfaction']['score'] += 1
        snapshot['log'].append('%s Win the Match!'%snapshot['leftfaction']['name'])
    elif match_winner == 'r':    
        snapshot['rightfaction']['score'] += 1
        snapshot['log'].append('%s Win the Match!'%snapshot['rightfaction']['name'])
    else:
        snapshot['log'].append('The Match ends in a Tie!')
    if game_over(snapshot):
        conclude_game(snapshot)
    else:
        start_match(snapshot, match_winner)

def game_over(snapshot):
    max_score = max(snapshot['leftfaction']['score'], snapshot['rightfaction']['score'] )
    if max_score > 2:
        return 1
    else:
        return 0

def conclude_game(snapshot):
    l_score, r_score = snapshot['leftfaction']['score'], snapshot['rightfaction']['score']
    if l_score > r_score:
        winner = snapshot['leftfaction']['name']
        snapshot['log'].append('%s Win the game, %d to %d!' % (winner, l_score, r_score))
    elif r_score > l_score:
        winner = snapshot['rightfaction']['name']
        snapshot['log'].append('%s Win the game, %d to %d!' % (winner, r_score, l_score))
    else:
        raise Exception # How did the game get called?
    if choices in snapshot: del snapshot['choices']
    if imp in snapshot: del snapshot['imp']

def timeout(snapshot):
    # last hits
    hit_dict = {'l':{}, 'r':{}}
    for faction in ['leftfaction', 'rightfaction']:
        for player in snapshot[faction]['players']:
            use_dict = hit_dict[faction[0]]
            spot = snapshot[player]['spot']
            if spot not in use_dict: use_dict[spot] = {'cards':[],'players':[]}
            use_dict[spot]['cards'] += snapshot[player]['cards']
            use_dict[spot]['players'].append(player)
    for l in hit_dict['l']:
        for r in hit_dict['r']:
            dist = r - l
            l_spot, r_spot = hit_dict['l'][l], hit_dict['r'][r]
            l_count = l_spot['cards'].count(dist)
            r_count = r_spot['cards'].count(dist)
            if l_count > r_count: 
                snapshot['log'].append('Spot %s last-hits spot %s' %(l,r))
                for player in r_spot['players']:
                    snapshot[player]['health'] -= 1
            elif r_count > l_count:
                snapshot['log'].append('Spot %s last-hits spot %s' %(r,l))
                for player in l_spot['players']:
                    snapshot[player]['health'] -= 1
    # both sides still up?
    rival = {'l':'r', 'r':'l'}
    match_winner = 0
    for faction in 'leftfaction', 'rightfaction':
        alive = 0
        for player in snapshot[faction]['players']:
            alive += snapshot[player]['health']
        if alive < 0:
            if match_winner:
               match_winner = 't'  # Double KO!  (Check rules on this)
            else:
                match_winner = rival[faction[0]]
    # who's the farthest
    if not match_winner:
        snapshot['log'].append('The match is decided by distance!')
        l_best = max([snapshot[player]['spot'] for player in snapshot['leftfaction']['players']])
        r_best = max([(19 - snapshot[player]['spot']) for player in snapshot['rightfaction']['players']])
        if l_best > r_best: match_winner = 'l'
        elif l_best < r_best: match_winner = 'r'
        else: match_winner = 't'
    return match_winner # 'r', 'l', 't'

  ##################  END SNAPSHOT PROCESSING  #############

   ###################  BEGIN ROBOT INTERFACE PROTOCOL  ##################
def robot_control(snapshot, flag=''):
    if 'choices' in snapshot:
        controller = snapshot[snapshot['choices'][0]]['controller']
    else:
        controller = 'human'
    while controller != 'human':
        print "CONTROLLER: ", controller
        if controller in robot_lookup_table:
            robot_name = snapshot['choices'][0]
            robot_snap = player_snap_from_master(snapshot, robot_name)
            robot = robot_lookup_table[controller]()
            robot_choice = robot.make_choice(robot_snap)
            print "%s CHOICE: %s"%(robot_name, robot_choice)
            snapshot = do_things(snapshot, robot_choice)
            complete_archive(snapshot)
            if flag: print printers.print_from_snapshot(snapshot)
            if 'choices' in snapshot:
                controller = snapshot[snapshot['choices'][0]]['controller']
            else:
                controller = 'human'
        else:
            print '\n+++++\n'+controller+'\n++++++\n'
            raise Exception # Bad Robot Type
    print "CONTROLLER: ", controller
    return snapshot
   ###################  END ROBOT INTERFACE PROTOCOL  ##################

#################  START LOGGING/DIPLAY FUNCTIONALITY  ####################
def player_snap_from_master(master_snap, player_name=''):
    if player_name.isdigit():
        name_dict = names_from_ids(master_snap)
        p_id = int(player_name)
        if p_id in name_dict:
            player_name = name_dict[p_id]
        else:
            player_name = 'p0'
    snapshot = copy.deepcopy(master_snap)  # hope this works
    if 'choices' in snapshot and player_name != snapshot['choices'][0]:
        del snapshot['choices']
    for faction in ['leftfaction','rightfaction']:
        for player in snapshot[faction]['players']:
            player_info = snapshot[player]
            if player == player_name:
                snapshot['mycards'] = (player, player_info['cards'])
            else:
                del snapshot[player]['id_num']
            del player_info['cards']
    return snapshot
    

def names_from_ids(mastersnapshot):
    id_dict = {}
    for player in full_player_list(mastersnapshot):
        id_dict[mastersnapshot[player]['id_num']] = player
    return id_dict


 ################  START FILE PICKLING  #################
def file_snap(snapshot, game_id='', player_id=-1):
    if player_id != -1: 
        player_id = str(player_id)
        if player_id.isdigit(): player_id = 'p'+player_id
    else:
        player_id = ''
    if not game_id:
        game_id=snapshot['game'][1]
    game_id = str(game_id)
    if game_id.isdigit() : game_id = 'g'+game_id
    archive_file = 'data/'+game_id+player_id+'_archive.pkl'
    #print "Reading File: " + archive_file
    try:
        check2_file = open(archive_file, 'rb')
        archive_list = pickle.load(check2_file)
        check2_file.close()
        #print "File Read!"
    except IOError:
        archive_list = []
    archive_list.append(snapshot)
    #print "Writing File: " + archive_file
    log_file = open(archive_file, 'wb')
    pickle.dump(archive_list, log_file, -1)
    log_file.close()

def file_recov(game_id='g0'):
    archive_file = 'data/'+str(game_id)+'_archive.pkl'
    #print "Reading File: " + archive_file
    try:
        snap_file = open(archive_file, 'rb')
        snapshot_list = pickle.load(snap_file)
        snapshot = snapshot_list[-1]
        #print "File Read!"
    except IOError: snapshot = 0
    return snapshot

def player_snap_files(snapshot):
    game_id = 'g'+str(snapshot['game'][1])
    for faction in ['leftfaction', 'rightfaction']:
        for player in snapshot[faction]['players']:
            player_info = snapshot[player]
            player_id = player_info['id_num']
            player_snap = player_snap_from_master(snapshot, player)
            file_snap(player_snap, game_id, player_id)
    snapshot = player_snap_from_master(snapshot)
    file_snap(snapshot, game_id, 'p0')

def complete_archive(snapshot):
    file_snap(snapshot)
    player_snap_files(snapshot)
 ################  END FILE PICKLING  #################
#################  END LOGGING/DIPLAY FUNCTIONALITY  ####################

 ################### START ACTION FUNCTIONS #######################
def do_things(snapshot, choice):
    if choice in snapshot['choices'][1]:
        enact_choice(snapshot, choice)
        del snapshot['choices']
        if match_over(snapshot):
            conclude_match(snapshot)
        elif 'imp' in snapshot:
            suffering_choices(snapshot)
        else:
            end_turn(snapshot)
    else:
        raise Exception # Choice not in available choices
    return snapshot

def enact_choice(snapshot, choice):
    choice_type = choice[0]
    if choice_type in ['r']:
    #if choice_type in ['a', 's', 'd', 'f', 'b', 'r']:
        snapshot[snapshot['choices'][0]]['winded'] = 1
    # Action Options
    if choice_type == 'a':
        atk_val = int(choice[1])
        atk_amnt = len(choice) - 1
        attack(snapshot, atk_val, atk_amnt)
    elif choice_type == 's':
        dist = int(choice[1])
        shove(snapshot, dist)
    elif choice_type == 'f':
        if snapshot['choices'][0] in snapshot['leftfaction']['players']:
            en_dir = 1
        else: en_dir = -1
        dist = int(choice[1])*en_dir
        move(snapshot, dist)
    elif choice_type == 'b':
        if snapshot['choices'][0] in snapshot['leftfaction']['players']:
            en_dir = 1
        else: en_dir = -1
        dist = int(choice[1])*en_dir*-1
        move(snapshot, dist)
        pass
    elif choice_type == 'd':
        atk_val = int(choice[2])
        move_dist = int(choice[1])
        atk_amnt = len(choice)-2
        dash(snapshot, atk_val, atk_amnt, move_dist)
    # Defensive Options
    elif choice_type == 'p':
        parry(snapshot)
    elif choice_type == 'r':
        dist = int(choice[1])
        retreat(snapshot, dist)
    elif choice_type == 't':
        take_hit(snapshot)
    elif choice_type == 'c':
        val_needed = int(choice[1])
        amnt_needed = len(choice)-1
        cry_for_help(snapshot, val_needed, amnt_needed)
    # Response Options
    elif choice_type == 'x':
        pass
        deny_help(snapshot)
    elif choice_type == 'i':
        move_dist = int(choice[1])
        donate_val = int(choice[2])
        donate_amnt = len(choice) - 2
        interpose(snapshot,move_dist, donate_val, donate_amnt )
    else:
        raise Exception # Unknown choice type
###############  TOOLS  ################
def action_init(snapshot):
    actor = snapshot['choices'][0]
    if actor in snapshot['leftfaction']['players']:
        en_dir = 1
        en_fac = 'rightfaction'
    else:
        en_dir = -1
        en_fac = 'leftfaction'
    my_spot = snapshot[actor]['spot']
    return actor, en_dir, my_spot, en_fac

def discard(snapshot, player, cards):
    hand = snapshot[player]['cards']
    for card in cards:
        hand.remove(card)
        snapshot['grave'].append(card)

###############  ACTIONS  ##################
def attack(snapshot, atk_val, atk_amnt):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    target_spot = my_spot + atk_val*en_dir
    log_str = 'a'+str(atk_val)*atk_amnt+':'+actor+' attacked '
    snapshot['imp'] = []
    for player in snapshot[en_fac]['players']:
        if snapshot[player]['spot'] == target_spot:
            log_str += player+', '
            #  HIT THEM IN THE FACE
            suffering = {'can_retreat':0, 'can_cry':1,'cards':[atk_val]*atk_amnt, 'victims':player, 'crier':0}
            snapshot['imp'].append(suffering)
    log_str = log_str[:-2]+' with %d %d-value cards.' % (atk_amnt, atk_val)
    snapshot['log'].append(log_str)
    discard(snapshot, actor, [atk_val]*atk_amnt)

def shove(snapshot, dist):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    target_spot = my_spot + en_dir
    final_spot = target_spot + dist*en_dir
    if final_spot > 18: final_spot = 18
    elif final_spot < 1: final_spot = 1
    log_str = 's'+str(dist)+':'+actor+' shoved '
    for player in snapshot[en_fac]['players']:
        if snapshot[player]['spot'] == target_spot:
            log_str += player+', '
            snapshot[player]['spot'] = final_spot
    log_str = log_str[:-2]+' to spot %d' % final_spot
    snapshot['log'].append(log_str)
    discard(snapshot, actor, [abs(dist)])

def move(snapshot, dist):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    en_player_spots = [snapshot[enemy]['spot'] for enemy in snapshot[en_fac]['players']]
    for i in range(abs(dist)):
        test_spot = my_spot + dist/abs(dist)
        if test_spot in en_player_spots+[0,19]:
            break
        else:
            my_spot = test_spot
        
    snapshot[actor]['spot'] = my_spot
    if dist*en_dir > 0: log_str = 'f'
    else: log_str = 'b'
    snapshot['log'].append(log_str+'%d:'%abs(dist)+actor+' moved to spot %d' %my_spot)
    discard(snapshot, actor, [abs(dist)])


def dash(snapshot, atk_val, atk_amnt, move_dist):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    # Dash!
    discard(snapshot, actor, [move_dist]+[atk_val]*atk_amnt)
    en_player_spots = [snapshot[enemy]['spot'] for enemy in snapshot[en_fac]['players']]
    final_spot = my_spot
    for i in range(move_dist):
        if final_spot + en_dir in en_player_spots+[0,19]:
            break
        else:
            final_spot += en_dir
    # Strike!
    target_spot = final_spot + atk_val*en_dir
    log_str = ''
    for player in snapshot[en_fac]['players']:
        if snapshot[player]['spot'] == target_spot:
            log_str += player+', '
            #  HIT THEM IN THE FACE
            suffering = {'can_retreat':1, 'can_cry':1,'cards':[atk_val]*atk_amnt, 'victims':player, 'crier':0}
            snapshot['imp'] = [suffering]
    snapshot['log'].append('d'+str(move_dist)+str(atk_val)*atk_amnt+':'+actor+' retreated to spot %d!'% final_spot)

#############  DEFENSES  ###################
def parry(snapshot):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    snapshot['log'].append('p:'+actor+' parried the attack!')
    for suffering in snapshot['imp']:
        if snapshot['victims'] == actor:
            discard(snapshot, actor, suffering['cards'])
            snapshot['imp'].remove(suffering)
            break

def retreat(snapshot, dist):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    if en_dir == 1:
        final_spot = max(1, my_spot-dist)
    else:
        final_spot = min(18, my_spot+dist)
    discard(snapshot, actor, [dist])
    snapshot[actor]['spot'] = final_spot
    for suffering in snapshot['imp']:
        if suffering['victims'] == actor:
            snapshot['imp'].remove(suffering)
            break
    snapshot['log'].append('r:'+actor+' retreats to spot %d!' % final_spot)

def take_hit(snapshot):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    snapshot['log'].append('t:'+actor+' took the hit!')
    snapshot[actor]['health'] += 1
    if snapshot[actor]['health'] < 1:
        snapshot[actor]['spot'] = None
        log_str = actor+' is out of the match!'
    else:
        log_str = actor+' is too tough to be beaten so easily!  He has %d hits left to go!' % snapshot[actor]['health']
    for suffering in snapshot['imp']:
        if suffering['victims'] == actor: # is mine:
            snapshot['imp'].remove(suffering)
            break

def cry_for_help(snapshot, val_needed, amnt_needed):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    # find the source attack
    for suffering in snapshot['imp']:
        if suffering['victims'] == actor:
            atk_suff = suffering
    # pre-discard your contrib - dragons can't call for help
    # so you're parring or discarding all either way
    applied_cards = atk_suff['cards'][amnt_needed:]  
    atk_suff['cards'] = atk_suff['cards'][:amnt_needed]
    discard(snapshot, actor, applied_cards)
    atk_suff['can_cry'] = 0
    # find the valid aiders
    log_str = ''
    if en_fac == 1:
        allies = snapshot['leftfaction']['players']
        check = range(1, my_spot+1)
    else:
        allies = snapshot['rightfaction']['players']
        check = range(my_spot, 19)
    cry_targets = []
    for dist in range(min(6, len(check))):
        for player in allies:
            if snapshot[player]['spot'] == dist:
                    cry_targets.append(player)  # closest to farthest
                    log_str += player
    log_str = log_str[:-2]
    # ask them for help
    suffering = {'can_retreat':0, 'can_cry':0,'cards':[val_needed]*amnt_needed, 'victims':cry_targets, 'crier':actor}
    snapshot['imp'].append(suffering)
    snapshot['log'].append('c'+str(val_needed)*amnt_needed+':'+actor+' calls to '+log_str+' for aid!')
###########  RESPONSES  #################

def deny_help(snapshot):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    snapshot['log'].append('x:'+actor+' denies the call for aid!')
    for suffering in snapshot['imp']:
        if suffering['crier']:
            suffering['victims'].remove(actor)
            if not suffering['victims']:
                snapshot['imp'].remove(suffering)
            break

def interpose(snapshot, move_dist, donate_val, donate_amnt):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    # Find the cry and the attack we're dealing with
    for suffering in snapshot['imp']:
        if suffering['crier']:
            cry_suff = suffering
            break
    crier = cry_suff['crier']
    for suffering in snapshot['imp']:
        if suffering['victims'] == crier:
            atk_suff = suffering
            break
    # go there and help
    final_spot = snapshot[crier]['spot']
    needed = [abs(final_spot-my_spot)]+cry_suff['cards']
    snapshot[actor]['spot'] = final_spot
    discard(snapshot, actor, needed)
    # remove the sufferings
    snapshot['imp'].remove(cry_suff)
    snapshot['imp'].remove(atk_suff) # defender pre-discarded her part
    snapshot['log'].append('i'+str(abs(move_dist))+str(donate_val)*donate_amnt+':'+actor+' moved to spot %d and interposed himself before %s with %d cards!' %(final_spot, crier, donate_amnt))

 #################### END ACTION FUNCTIONS ####################

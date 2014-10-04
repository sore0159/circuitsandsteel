import cPickle as pickle
import copy
import random
from robots import robot_lookup_table
  ##################  START SNAPSHOT GEN  ###############
######################### START PREGAME PREF REGISTRATION #################
def assemble_pref_list(controller_list, game_type):
    color_list = []
    name_list = []
    fac_list = []
    turn_pref = []
    fac_turn_pref = []
    fac1_name_votebooth =[] 
    fac2_name_votebooth = []
    i = 0
    if game_type in [0,2]:
        fac1_size = 1
        num_players = 2
    elif game_type in [1,3]:
        fac1_size = 2
        num_players = 4
    elif game_type in [4,5,6]:
        fac1_size = game_type - 2
        num_players = fac1_size + 1

    color_matrix = []
    for controller in controller_list[:num_players]:
        player = robot_lookup_table[controller]()
        i += 1
        turn_pref.append(player.in_team_pref)
        fac_turn_pref.append(player.fac_order_pref)
        if i <= fac1_size:
            fac1_name_votebooth.append(player.faction)
        else:
            fac2_name_votebooth.append(player.faction)
        temp_color_pref = player.color_pref
        temp_color_pref = list(set(temp_color_pref))
        for j in range(len(temp_color_pref)):
            color = temp_color_pref[j]
            if not color or color == 'black':
                temp_color_pref.pop(j)
        if len(temp_color_pref) >4:
            temp_color_pref = temp_color_pref[:4]
        elif len(temp_color_pref) < 4:
            for color in ['purple', 'red', 'blue', 'green']:
                if color not in temp_color_pref and len(temp_color_pref)<4:
                    temp_color_pref.append(color)
        color_matrix.append(temp_color_pref)
        for name in [player.name+'I'*num for num in [0,2,3,4,5]]:
            if name not in name_list:
                name_list.append(name)
                break
    fac_list = [random.choice(fac1_name_votebooth), random.choice(fac2_name_votebooth)]
    color_list = color_vote2(color_matrix) # turn order voting is outsourced already
    index_order = str_turn_order(fac1_size, turn_pref, fac_turn_pref)
    turn_order = []
    for index in index_order:
        turn_order.append(name_list[index])
    return (color_list, name_list, fac_list, turn_pref, fac_turn_pref)

def color_vote2(color_matrix): # 5 x 4 matrix
    color_list = [0,0,0,0,'black']
    for vote_num in range(4):
        vote_dict = {}
        for p_num in range(min(4, len(color_matrix))): # we don't care what dragon wants
            if not color_list[p_num]: # if she doesn't have a color
                color = color_matrix[p_num][vote_num] # pick her ith fav color
                if color not in vote_dict:
                    vote_dict[color] = []
                vote_dict[color].append(p_num)  # she votes for it
        #after all votes collected
        for color in vote_dict:
            color_list[random.choice(vote_dict[color])] = color

    return color_list

def str_turn_order(fac1_size, turn_prefs, fac_turn_prefs, who_won=-1):
    fac1_vote = 0
    fac2_vote = 0
    skip_count = 0
    for i in range(len(fac_turn_prefs)):#collect votes for factions
        if i >= fac1_size: skip_count = 1
        vote = fac_turn_prefs[i]
        if vote == 'first':
            vote = -1
        elif vote == 'last':
            vote = 1
        else:
            vote = 0
        if skip_count: fac1_vote += vote
        else: fac2_vote += vote
    if who_won == 1: #only losers get to vote
        final_vote = fac1_vote
    elif who_won == 0:
        final_vote = fac2_vote*-1
    else: # no losers, it's random which team picks
        if random.randint(0,1):
            final_vote = fac1_vote
        else:
            final_vote = fac2_vote*-1
    if final_vote == 0: # if that team doesn't care then hey
        final_vote = random.choice([0,1])
    elif final_vote > 0: 
        final_vote = 1
    else: final_vote = 0
    fac2_size = len(turn_prefs) - fac1_size
    #final_vote is 0 for fac1 or +1 for fac2
    fac_p_list = [0,0]
    fac_p_list[0] = inter_turn_order(turn_prefs[:fac1_size])
    if fac2_size == 1 and fac1_size > 1: #DRAGON
        turn_order = fac_p_list[0] + [fac1_size] # he always goes last
    else: # team sizes are equal
        turn_order = []
        fac_p_list[1] = [x + fac1_size for x in inter_turn_order(turn_prefs[fac1_size:])]
        for i in range(fac1_size):
            turn_order.append(fac_p_list[final_vote][i])
            turn_order.append(fac_p_list[final_vote-1][i])
    return turn_order #returns turn order in indicies for players as given
        # (index# for first to go), (index# for 2nd to go), etc.

def inter_turn_order(pref_list):
    #opts: first last mid
    sorted_turns = [[],[],[]]
    turns = []
    for i in range(len(pref_list)):
        x = pref_list[i]
        if x == 'last':
            sorted_turns[2].append(i)
        elif x == 'first':
            sorted_turns[0].append(i)
        else:
            sorted_turns[1].append(i)
    for i in range(3):
        random.shuffle(sorted_turns[i])
        turns += sorted_turns[i]
    return turns #returns list indicies in turn order

######################### END PREGAME PREF REGISTRATION #################
def name_vote(players):
    pass
    # player[i] = {'controller':cont_obj}

def color_vote(players):
    pass
    # player[i] = {'controller':cont_obj}

def faction_name_vote(players):
    pass
    # player[i] = {'controller':cont_obj}

######################## START GAME ASSEMBLY ############################
def assemble_snapshot(game_type=0, game_id=0, player_list=['human']*5):
    #########  START ARGUMENT SCRUBBING  #########
    try:
        if game_id[0] == 'g':
            game_id = game_id[1:]
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

    # How many players
    if game_type in [0,2]: num_players = 2
    elif game_type in [1,3]: num_players = 4
    else: num_players = gametype -1
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
    players = [{}]*num_players
    # cut down to size
    for i in num_players:
        players[i]['controller'] = player_list[i]
    random.shuffle(players)
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
    snapshot['leftfaction'] = {'name':'templeft', 'score':0, 'players':[]}
    snapshot['rightfaction'] = {'name':'tempright', 'score':0, 'players':[]}
    for player in players[:fac1_size]:
        snapshot['leftfaction']['players'].append(player['name'])
        player['dragon']=0
    for player in players[fac1_size:]:
        snapshot['rightfaction']['players'].append(player['name'])
        if dragon: player['dragon']=1
        else: player['dragon']=0


    # per faction:
    # vote on fac name
    fac_name_vote(snapshot)

    skip_count = 0
    fac_string = 'leftfaction'
    is_dragon = 0
    p_health = 1
    player_id_list = [0]
    hand_size = 5
    spot = 1
    for i in range(num_players):
        if i >= fac1_size:
            skip_count = 1
            fac_string = 'rightfaction'
            spot = 18
        if skip_count and game_type in [4, 5, 6 , 7]:
            is_dragon = 1
            p_health = dragon[0]
            hand_size = dragon[1]
        rand_num = 0
        while rand_num in player_id_list:
        player_id_list.append(rand_num)
        player_cards = []
        player_dict = {'dragon': is_dragon, 'num_cards': 0, 'spot':None , 'health': 0, 'winded':0, 'color':color_list[i] , 'id_num':rand_num, 'cards':[], 'controller':controller_list[i]}
        snapshot[name_list[i]] = player_dict
        snapshot[fac_string]['players'].append(name_list[i])
    return snapshot

 #####################  START GAMEBOARD SETUP  #########################

def forder_vote(snapshot, faction):
    players = snapshot[faction]['players']
    vote = 0
    for player in players:
        robot = robot_lookup_table[snapshot[player]['controller']]()
        vote = robot.forder_vote(snapshot)
        if vote == 'first':
            vote += 1
        elif vote == 'last':
            vote -= 1
    if vote = 0:
        me_first = random.choice([0,1])
    elif vote < 0:
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

def startmatch(snapshot, lastwinner=''):
    game_type = snapshot['game'][0]
    # which side goes first
    if not lastwinner:
        if random.choice([0,1]):
            lastwinner='leftfaction'
        else:
            lastwinner='rightfaction'

    if game_type not in [4,5,6]:
        if lastwinner = 'leftfaction':
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
            for i in len(l_order): turn_order.extend(l_order(i), r_order(i))
    else:
        for i in len(l_order): turn_order.extend(r_order(i), l_order(i))

    
    snapshot['turnorder']= turn_order
    snapshot['whosturn']= turn_order[0]
    if game_type in [5,6]: cycles = 1
    else: cycles = 0
    if game_type in [1,3,4,6]: num_cards = 10
    elif game_type == 5: num_cards = 8
    else: num_cards = 5
    deck = []
    for i in range(1,5):
        for j in range(num_cards):
            deck.append(i)
    random.shuffle(deck)
    #for player in players
    #    if dragon health = gametype -2 hand_size = gametype + 5
    #    else health = 1 hand_size = 5
    #    for j in range(hand_size):
    #        player_cards.append(deck.pop())
    #    player num_cards = len(cards)
    #    if leftfaction spot = 1
    #    elif rightfaction spot = 18
    # new call to turnorder function
    
    snapshot['deck'] = (deck, cycles)
    snapshot['grave'] = []
    snapshot['log'] = game_log
    choice_tuple = choices_from_snapshot(snapshot) # DANGER!
    snapshot['choices'] = choice_tuple
    return snapshot


  ##################  END SNAPSHOT GEN  #################

  ##################  START SNAPSHOT PROCESSING  #############

def choices_from_snapshot(snapshot):
    if len(snapshot['log']) > 2:
        raise Exception # As the wise men laid the final seal, even then the prophecy was spoken of the day it would be undone and doom would fall.
    player = snapshot['whosturn']
    choices = []
    card_count = [None, 0, 0, 0, 0, 0]
    cards = snapshot[player]['cards']
    for card in cards:
        card_count[card] += 1
    #move
    for card in range(1,6):
        if card_count[card]:
            choices.extend(['f%d'%card, 'b%d'%card])
    #push
    #attack
    #dashing strike
    choice_tuple = (player, choices)
    return choice_tuple


def suff_opts_from_snap(snapshot):
    pass

def game_over_from_snap(snapshot):
    game_over = 0
    for faction in 'leftfaction', 'rightfaction':
        alive = 0
        for player in snapshot[faction]['players']:
            alive += snapshot[player]['health']
        if not alive:
            game_over = 1
    if not game_over:
        deck_len, cycles = snapshot['deck']
        if not deck_len and not cycles:
            timeout = 1
        else:
            timeout = 0
        if timeout:
            game_over = 1
        else:
            game_over = 0
    return game_over

def player_snap_from_master(master_snap, player_name=''):
    if player_name.isdigit():
        name_dict = names_from_ids(master_snap)
        p_id = int(player_name)
        if p_id in name_dict:
            player_name = name_dict[p_id]
        else:
            player_name = 'p0'
    snapshot = copy.deepcopy(master_snap)  # hope this works
    snapshot['HELLO']='hi'
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
    
def full_player_list(snapshot):
    return snapshot['leftfaction']['players'] + snapshot['rightfaction']['players']

def names_from_ids(mastersnapshot):
    id_dict = {}
    for player in full_player_list(mastersnapshot):
        id_dict[mastersnapshot[player]['id_num']] = player
    return id_dict


  ##################  END SNAPSHOT PROCESSING  #############
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


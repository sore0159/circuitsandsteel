import cPickle as pickle
  ##################  START SNAPSHOT GEN  ###############

def random_gamestart_snapshot(self, game_type=0, game_id=0):
    try:
        if game_id[0] == 'g':
            game_id = game_id[1:]
        game_id = int(game_id)
    except:
        game_id = 0
    snapshot = {'game':(game_type, game_id)}
    cycles = 0 
    extra_cards = 0 
    num_players = 2
    fac1_size = 1
    dragon = 0 # hp, cards, abils
    powers = 1
    if game_type == 1: #two vs two, no powers
        num_players = 4
        fac1_size = 2
        powers = 0
        extra_cards = 5
    elif game_type == 2: #1v1 powers
        powers = 1
    elif game_type == 3: #2v2 powers
        num_players = 4
        fac1_size = 2
        extra_cards = 5
    elif game_type == 4: #2vD
        num_players = 2
        fac1_size = 2
        dragon = (2, 7, 4)
        extra_cards = 5
    elif game_type == 5: #3vD
        num_players = 3
        fac1_size = 3
        dragon = (3, 8, 6)
        extra_cards = 3
        cycles = 1
    elif game_type == 6: #4vD
        num_players = 4
        fac1_size = 4
        dragon = (4, 9, 8)
        extra_cards = 5
        cycles = 1
    elif game_type == 7: #3vD+T  not sure how to do traitor
        num_players = 4
        fac1_size = 4
        dragon = (3, 8, 6)
        extra_cards = 5
        cycles = 1
    else:
        powers = 0 #default, 1v1 no powers
    deck = range(1,6)*(5+extra_cards)
    random.shuffle(deck)

    #############  THINGS NEED TO BE PASSED AS ARGS LATER  ############
    color_list = ['red', 'blue', 'green', 'yellow']
    name_list = ['Player One', 'Player Two', 'Player Three', 'Player Four', 'Player Five'] 
    fac_list = ['The Robo-Jets', 'The Mecha-Sharks']
    turn_pref= ['mid','mid','mid','mid','mid']
    fac_turn_pref = ['first', 'first', 'first', 'first', 'first' ]
    turn_pref = turn_pref[:num_players]
    fac_turn_pref = fac_turn_pref[:num_players]
    #############  END THINGS TO BE PASSED AS ARGS LATER  ############
    ##############  FACTIONS  ##############
    snapshot['leftfaction'] = {'name':fac_list[0], 'score':0, 'players':[]}
    snapshot['rightfaction'] = {'name':fac_list[1], 'score':0, 'players':[]}
    ############## END FACTIONS ############
    game_log = []
    game_log.append('Game Start, Game Type %d' % game_type)
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
            rand_num = random.randint(100,999)
        player_cards = []
        for j in range(hand_size):
            player_cards.append(deck.pop())
        player_dict = {'dragon': is_dragon, 'num_cards': len(player_cards) , 'spot':spot , 'health': p_health, 'winded':0, 'color':color_list[i] , 'id_num':rand_num, 'cards':player_cards}
        snapshot[name_list[i]] = player_dict
        snapshot[fac_string]['players'].append(name_list[i])

    index_order = self.str_turn_order(fac1_size, turn_pref, fac_turn_pref)
    turn_order = []
    logstring = 'Turn Order Set: '
    for index in index_order:
        turn_order.append(name_list[index])
        logstring += turn_order[-1]+', '
    logstring = logstring[:-2]
    game_log.append(logstring)
    snapshot['turnorder']= turn_order
    snapshot['whosturn']= turn_order[0]
    snapshot['deck'] = (deck, cycles)
    snapshot['grave'] = []
    snapshot['log'] = game_log
    choice_tuple = choices_from_snapshot(snapshot) # DANGER!
    snapshot['choices'] = choice_tuple
    return snapshot

def str_turn_order(self, fac1_size, turn_prefs, fac_turn_prefs, who_won=-1):
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
    fac_p_list[0] = self.inter_turn_order(turn_prefs[:fac1_size])
    if fac2_size == 1 and fac1_size > 1: #DRAGON
        turn_order = fac_p_list[0] + [fac1_size] # he always goes last
    else: # team sizes are equal
        turn_order = []
        fac_p_list[1] = [x + fac1_size for x in self.inter_turn_order(turn_prefs[fac1_size:])]
        for i in range(fac1_size):
            turn_order.append(fac_p_list[final_vote][i])
            turn_order.append(fac_p_list[final_vote-1][i])
    return turn_order #returns turn order in indicies for players as given
        # (index# for first to go), (index# for 2nd to go), etc.

def inter_turn_order(self, pref_list):
    #opts: first last mid
    sorted_turns = [[],[],[]]
    turns = []
    for i in range(len(pref_list)):
        x = pref_list[i]
        if x == 'mid':
            sorted_turns[1].append(i)
        elif x == 'first':
            sorted_turns[0].append(i)
        else:
            sorted_turns[2].append(i)
    for i in range(3):
        random.shuffle(sorted_turns[i])
        turns += sorted_turns[i]
    return turns #returns list indicies in turn order


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
            choices.extend(['mu%d'%card, 'md%d'%card])
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


  ##################  END SNAPSHOT PROCESSING  #############
 ################  START FILE PICKLING  #################
def file_snap(snapshot, game_id='g0', player_id=-1):
    if player_id != -1: 
        player_id = str(player_id)
        if player_id.isdigit(): player_id = 'p'+player_id
    else:
        player_id = ''
    game_id = str(game_id)
    if game_id.isdigit() : game_id = 'g'+game_id
    archive_file = 'data/'+game_id+player_id+'_archive.pkl'
    print "Reading File: " + archive_file
    try:
        check2_file = open(archive_file, 'rb')
        archive_list = pickle.load(check2_file)
        check2_file.close()
        print "File Read!"
    except IOError:
        archive_list = []
    archive_list.append(snapshot)
    print "Writing File: " + archive_file
    log_file = open(archive_file, 'wb')
    pickle.dump(archive_list, log_file, -1)
    log_file.close()

def file_recov(game_id='g0'):
    archive_file = 'data/'+str(game_id)+'_archive.pkl'
    print "Reading File: " + archive_file
    try:
        snap_file = open(archive_file, 'rb')
        snapshot_list = pickle.load(snap_file)
        snapshot = snapshot_list[-1]
        print "File Read!"
    except IOError: snapshot = 0
    return snapshot

def player_snap_files(game):
    game_id = 'g'+str(game.game_id)
    for player in game.gameboard['player']:
        player_id = player.id_num
        snapshot = game.snapshot(player_id)
        file_snap(snapshot, game_id, player_id)
    snapshot = game.snapshot()
    file_snap(snapshot, game_id, 'p0')
 ################  END FILE PICKLING  #################


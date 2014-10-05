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

def enact_choice(snapshot, choice):
    choice_type = choice[0]
    if choice_type in ['r']:
    #if choice_type in ['a', 's', 'd', 'f', 'b', 'r']:
        snapshot[actor]['winded'] = 1
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
        dist = int(choice[1]*en_dir
        move(snapshot, dist)
    elif choice_type == 'b':
        if snapshot['choices'][0] in snapshot['leftfaction']['players']:
            en_dir = 1
        else: en_dir = -1
        dist = int(choice[1]*en_dir*-1
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
    for player in snapshot[en_fac]['players']:
        if snapshot[player]['spot'] == target_spot:
            log_str += player+', '
            #  HIT THEM IN THE FACE
    # suffering = {'can_retreat', 'can_cry', 'cards', 'victims', 'crier'}
            # TODO
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
        
    if dist*en_dir > 0: log_str = 'f'
    else: log_str = 'b'
    snapshot['log'].append(log_str+'%d:'%abs(dist)+actor+' moved to spot %d' %my_spot)
    discard(snapshot, actor, [abs(dist)])


def dash(snapshot, atk_val, atk_amnt, move_dist):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    final_spot = ''
    discard(snapshot, actor, [atk_val]*atk_amnt)
    snapshot['log'].append('d'+str(move_dist)+str(atk_val)*atk_amnt+':'+actor+' retreated to spot %d!'% final_spot)
    # suffering = {'can_retreat', 'can_cry', 'cards', 'victims', 'crier'}

#############  DEFENSES  ###################
def parry(snapshot):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    discard(snapshot, actor, [atk_val]*atk_amnt)
    snapshot['log'].append('p:'+actor+' parried the attack!')
    # suffering = {'can_retreat', 'can_cry', 'cards', 'victims', 'crier'}

def retreat(snapshot, dist):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    final_spot = ''
    discard(snapshot, actor, [atk_val]*atk_amnt)
    snapshot['log'].append('r:'+actor+' retreats to spot %d!' % final_spot)
    # suffering = {'can_retreat', 'can_cry', 'cards', 'victims', 'crier'}

def take_hit(snapshot):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    snapshot[actor]['health'] += 1
    for suffering in snapshot['imp']:
        if suffering: # is mine:
            snapshot['imp'].remove(suffering)
    snapshot['log'].append('t:'+actor+' took the hit!')
    # suffering = {'can_retreat', 'can_cry', 'cards', 'victims', 'crier'}

def cry_for_help(snapshot, val_needed, amnt_needed):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    for dist in range(min(6, len(check))):
        for player in allies:
            if snapshot[player]['spot'] == dist:
                    cry_targets.append(player)  # closest to farthest
    log_str = ''
    # find the valid aiders
    # suffering = {'can_retreat', 'can_cry', 'cards', 'victims', 'crier'}
    log_str = log_str[:-2]
    snapshot['log'].append('c'+str(val_needed)*amnt_needed+':'+actor+' calls to '+log_str+' for aid!')
###########  RESPONSES  #################

def deny_help(snapshot):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    snapshot['log'].append('x:'+actor+' denies the call for aid!')

    # suffering = {'can_retreat', 'can_cry', 'cards', 'victims', 'crier'}
def interpose(snapshot, move_dist, donate_val, donate_amnt):
    actor, en_dir, my_spot, en_fac  = action_init(snapshot)
    final_spot = ''
    victim = ''
    # suffering = {'can_retreat', 'can_cry', 'cards', 'victims', 'crier'}
    discard(snapshot, actor, [atk_val]*atk_amnt)
    snapshot['log'].append('i'+str(abs(move_dist))+str(donate_val)*donate_amnt+':'+actor+' moved to spot %d and interposed himself before %s with %d cards!' %(final_spot, victim, donate_amount))





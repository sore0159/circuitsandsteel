import game

####   QUERY GAME TYPE  ####
####   QUERY PLAYER COLORS, TEAMS  ####
####   QUERY POWER SELECTION   ####
####   SETUP GAME   ####

####   START TURN: WHOSE TURN?   ####
####   PRESENT, CHOOSE, EXECUTE ACTION   ####
####   DRAW TO FIVE   ####


####   WHENEVER HALTS:   ####
####   CREATE REPORT OBJECT   ####
####   CREATE QUERY OBJECT   ####
####   FORMAT R & Q OBJECTS   ####
####   PRESENT UPON REQUEST FORMATTED OUTPUT   ####

####            Present Option List, ask for input  ####
####                Default option list: what game? ####
####                Execute Action                  ####
####               if not firstturn: Draw to 5      ####
####                Who's turn is it?               ####
####             What options do they have?         ####
####                Create Option List              ####


def list_stuff(obj_list):
    for i in obj_list:
        print i.pretty_name(),
    print ' '

#for i in game.gameboard.keys():
    #print i, len(game.gameboard[i])

def report(game):
    x = game.gameboard['player'][0]
    y = game.gameboard['player'][1]
    print '-'*40
    print "Public Info:"
    list_stuff(game.public_info)
    print '-'*40
    print "Private Info Player 1:"
    list_stuff(x.private_info())
    print '-'*40
    print "Private Info Player 2:"
    list_stuff(y.private_info())
    print '-'*40
    print "Turn Order:"
    list_stuff(game.turn_order)
    print '-'*40
    print "Current Options:"
    for j in game.gameboard['tray']:
        print "Option Tray:"
        for i in  j.choice_ids:
            print  i,
        print ' '

def overlap(list1, list2):
    return set(list1) & set(list2)

def map(game):
    charset = ['^^ ', 'XX ',  '   ', '@/ ', '\\@ ', 'u', 'd', '   ']
    charset_len = 3
    fac1_tokens = []
    fac2_tokens = []
    rival_tokens = game.next_tray.check('owner')[0].check()[0].check('rival')[0].check()
    for i in game.gameboard['token']:
        if i.status >0 and i.check()[0] == game.gameboard['faction'][0]:
            fac1_tokens.append(i)
        else:
            fac2_tokens.append(i)
    cur_token = game.next_tray.check('owner')[0].check('owns')[0]
    cur_spot = cur_token.check('at')[0]
    map_string = ''
    line1 = ''
    line2 = ''
    top1 = ''
    top2 = ''
    top3 = ''
    under = ''
    for i in range(18):
        spot = game.gameboard['gamespace'][i]
        dist = cur_spot.how_far(spot)
        z = overlap(rival_tokens, spot.check('has'))
        if z:
            if dist[0] <10: under += '0'
            under += str(dist[0])+' '
        elif dist[0] <10:
            if dist[0] == 0:
                under += charset[7]
            elif dist[1] == 'up':
                under += charset[5]+str(dist[0])+' '
            else:
                under += charset[6]+str(dist[0])+' '
        else:
            under += charset[7]

        x = overlap(fac1_tokens, spot.check('has'))
        y = overlap(fac2_tokens, spot.check('has'))
        if x:
            line1 += charset[3]
            if len(x) == 2:
                top1 += charset[3]
            else:
                top1 += charset[2]
            if len(x) == 3:
                top2 += charset[3]
            else:
                top2 += charset[2]
            if len(x) == 4:
                top3 += charset[3]
            else:
                top3 += charset[2]

        elif y:
            line1 += charset[4]
            if len(y) == 2:
                top1 += charset[4]
            else:
                top1 += charset[2]
            if len(y) == 3:
                top2 += charset[4]
            else:
                top2 += charset[2]
            if len(y) == 4:
                top3 += charset[4]
            else:
                top3 += charset[2]
        else:
            line1 += charset[2]
            top1 += charset[2]
            top2 += charset[2]
            top3 += charset[2]
        if spot.hue == 'light':
            line2 += charset[0]
        elif spot.hue == 'dark':
            line2 += charset[1]
    map_string = top3+'\n'+top2+'\n'+top1+'\n'+line1 +'\n'+line2+'\n'+under
    return map_string
        
def abrev(name):
    name_dict = {'Player One':'P1', 'Player Two':'P2', 'Player Three':'P3', 'Player Four':'P4'} 
    if name in name_dict:
        return name_dict[name]
    else:
        return name[:2].upper()
    
def ascii_print(game):
    print '='*54
    fac1 = game.gameboard['faction'][0].pretty_name()
    fac2 = game.gameboard['faction'][1].pretty_name()
    fac1_players = []
    fac2_players = []
    for player in game.gameboard['faction'][0].check():
        if player.type_string == 'player':
            fac1_players.append(player)
    for player in game.gameboard['faction'][1].check():
        if player.type_string == 'player':
            fac2_players.append(player)
    if len(fac1) > 16: fac1 = fac1[:16]
    if len(fac2) > 16: fac2 = fac2[:16]
    fac_str = fac1 + ' '*(54-len(fac1+fac2))+fac2
    print fac_str
    print '%d'% game.gameboard['faction'][0].points + ' '*21 + '==VERSUS=='+ ' '*21+'%d'% game.gameboard['faction'][1].points
    print '\n'+map(game)
          ################# CARD AREA #################
    hand1 =abrev(fac1_players[0].pretty_name())+':'
    for card in fac1_players[0].cards():
        hand1 += str(card.value)+ ' '
    hand2 =''
    for card in fac2_players[0].cards():
        hand2 += ' '+ str(card.value)
    hand2 += ':'+abrev(fac2_players[0].pretty_name())


    if len(fac1_players) > 1:
        hand3 = abrev(fac1_players[1].pretty_name())+":"
        for card in fac1_players[1].cards():
            hand3 += str(card.value) + ' '
    else:
        hand3 = ''
    hand4 = ''
    if len(fac2_players) > 1:
        for card in fac2_players[1].cards():
            hand4 += ' '+str(card.value)
        hand4 += ':'+abrev(fac2_players[1].pretty_name())
        
    print '-'*54
    print hand1+' '*(54-len(hand1+hand2))+hand2
    if hand3 or hand4:
        print hand3+' '*(54-len(hand3+hand4))+hand4
    cards_left = len(game.deck().check())
    print "Cards left: %d" % cards_left
    
def present_options(game):
    if game.gameboard['tray']:
        tray = game.gameboard['tray'][0]
        #choice_nums = range(len(tray.choice_ids))
        print_str = '%s Choices: ' % tray.check('owner')[0].pretty_name()
        for choice in tray.choice_ids:
            print_str += choice + ' '
        print_str += '\n'
        return print_str

def query_option(game):
    if game.next_tray:
        tray = game.next_tray
        choice = -1
        opts = tray.choice_ids
    #    print present_options(game)
        print '%s Choices: ' % tray.check('owner')[0].pretty_name()
        while choice not in opts:
            try:
                choice = raw_input("%s:?" % opts)
            except Exception:
                pass
        return choice


def file_snap(snapshot):
    snap_file = file('snap_file', 'a')
    snap_file.write(str(snapshot))
    snap_file.write('\n\n')
    snap_file.close()

def file_recov():
    try:
        snap_file = file('snap_file')
        final = ''
        for line in snap_file.readlines():
            if line.lstrip():
                final = line
        if final: snapshot = eval(final)
        else: snapshot = 0
    except: snapshot = 0
    return snapshot
    
game = game.Game()
#game.game_type = 1
#game.spawn(1)
game_type = 1
snapshot = game.random_gamestart_snapshot(game_type)
#game.spawn_from_snapshot(snapshot)
snap2 = file_recov()
if not snap2:
    snap2 = game.random_gamestart_snapshot(game_type)
game.spawn_from_snapshot(snap2)
#print snap2

# GET
ascii_print(game)
if len(game.read_log()) > 2: print game.read_log()[-3]
if len(game.read_log()) > 1: print game.read_log()[-2]
if len(game.read_log()): print game.read_log()[-1]

# POST
if not game.is_game_over():
    choice = query_option(game)
    tray_id = game.next_tray.id_num
    game.make_choice(choice, tray_id)
    file_snap(game.master_snapshot())
    ascii_print(game)
    if len(game.read_log()) > 6: print game.read_log()[-7]
    if len(game.read_log()) > 5: print game.read_log()[-6]
    if len(game.read_log()) > 4: print game.read_log()[-5]
    if len(game.read_log()) > 3: print game.read_log()[-4]
    if len(game.read_log()) > 2: print game.read_log()[-3]
    if len(game.read_log()) > 1: print game.read_log()[-2]
    if len(game.read_log()): print game.read_log()[-1]



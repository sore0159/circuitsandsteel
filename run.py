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
        if i.check()[0] == game.gameboard['faction'][0]:
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
        
def ascii_print(game):
    print '='*54
    fac1 = game.gameboard['faction'][0].pretty_name()
    fac2 = game.gameboard['faction'][1].pretty_name()
    if len(fac1) > 16: fac1 = fac1[:16]
    if len(fac2) > 16: fac2 = fac2[:16]
    fac_str = fac1 + ' '*(54-len(fac1+fac2))+fac2
    print fac_str
    print '%d'% game.gameboard['faction'][0].points + ' '*21 + '==VERSUS=='+ ' '*21+'%d'% game.gameboard['faction'][1].points
    print '\n'+map(game)
    hand1 ='P1:'
    for card in game.gameboard['player'][0].check('has')[0].check():
        hand1 += str(card.value)+ ' '
    hand2 =''
    for card in game.gameboard['player'][2].check('has')[0].check():
        hand2 += ' '+ str(card.value)
    hand2 += ':P3'
    if game.game_type == 1:
        hand3 ='P2:'
        for card in game.gameboard['player'][1].check('has')[0].check():
            hand3 += str(card.value)+ ' '
        hand4 =''
        for card in game.gameboard['player'][3].check('has')[0].check():
            hand4 += ' '+ str(card.value)
        hand4 += ':P4'
        
    print '-'*54
    print hand1+' '*(54-len(hand1+hand2))+hand2
    if game.game_type == 1:
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

game = game.Game()
game.game_type = 1
game.spawn(1)

#for i in range(10):
#    game.deck().top_card().discard()
game.gameboard['token'][0].interact(game.gameboard['gamespace'][8])
game.gameboard['token'][1].interact(game.gameboard['gamespace'][8])
game.gameboard['token'][2].interact(game.gameboard['gamespace'][9])
game.gameboard['token'][3].interact(game.gameboard['gamespace'][9])
for i in range(12):
    card = game.gameboard['card'][i]
    hand = game.gameboard['hand'][i/3]
    print card.pretty_name(), hand.check('at')[0].pretty_name()
    card.interact(hand)


# GET
ascii_print(game)
if len(game.read_log()) > 2: print game.read_log()[-3]
if len(game.read_log()) > 1: print game.read_log()[-2]
if len(game.read_log()): print game.read_log()[-1]

# POST
while not game.is_game_over():
    choice = query_option(game)
    tray_id = game.next_tray.id_num
    game.make_choice(choice, tray_id)
    ascii_print(game)
    if len(game.read_log()) > 6: print game.read_log()[-7]
    if len(game.read_log()) > 5: print game.read_log()[-6]
    if len(game.read_log()) > 4: print game.read_log()[-5]
    if len(game.read_log()) > 3: print game.read_log()[-4]
    if len(game.read_log()) > 2: print game.read_log()[-3]
    if len(game.read_log()) > 1: print game.read_log()[-2]
    if len(game.read_log()): print game.read_log()[-1]



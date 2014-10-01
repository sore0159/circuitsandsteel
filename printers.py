 #################  PRINT FROM GAME OBJECT  #################
def query_option(game, flag=0):
    if game.next_tray:
        tray = game.next_tray
        choice = -1
        opts = tray.choice_ids
        print '%s Choices: ' % tray.check('owner')[0].pretty_name()
        if flag: print "%s:?" % opts
        while choice not in opts and not flag:
            try:
                choice = raw_input("%s:?" % opts)
            except Exception:
                pass
        return choice
def overlap(list1, list2):
    return set(list1) & set(list2)

def map(game):
    charset = ['^^ ', 'XX ',  '   ', '@/ ', '\\@ ', 'u', 'd', '   ']
    charset_len = 3
    fac1 = game.gameboard['faction'][0]
    fac2 = game.gameboard['faction'][1]
    fac1_tokens = fac1.tokens()
    fac2_tokens = fac2.tokens()
    left_fac = game.gameboard['faction'][0]
    #left_fac = game.gameboard['faction'][flip]
    if not game.is_game_over():    
        rival_tokens = game.next_tray.check('owner')[0].faction().rival().tokens()
    else:
        rival_tokens = []
    for i in game.gameboard['token']:
        if i.status >0 and i.check()[0] == left_fac:
            fac1_tokens.append(i)
        else:
            fac2_tokens.append(i)
    if game.next_tray:
        cur_token = game.next_tray.check('owner')[0].check('owns')[0]
        cur_spot = cur_token.check('at')[0]
    else:
        cur_token = 0
        cur_spot = 0
    map_string = ''
    line1 = ''
    line2 = ''
    top1 = ''
    top2 = ''
    top3 = ''
    under = ''
    for i in range(18):
        spot = game.gameboard['gamespace'][i]
        if cur_spot: dist = cur_spot.how_far(spot)
        else: dist = 0
        has_str = ''
        for j in spot.check('has'):
            has_str += j.check()[0].pretty_name()+', '
        if has_str: has_str = has_str[:-2]

        z = overlap(rival_tokens, spot.check('has'))
        if dist and z:
            if dist[0] <10: under += '0'
            under += str(dist[0])+' '
        elif dist and dist[0] <10:
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
    left_fac = game.gameboard['faction'][0]
    right_fac = game.gameboard['faction'][1]
    #flip = 0
    #if left_fac.tokens(0).closest_enemy()[1] == 'up':
    #    left_fac, right_fac = right_fac, left_fac
    #    flip = 1
    fac1 = left_fac.pretty_name()
    fac2 = right_fac.pretty_name()
    fac1_players = []
    fac2_players = []
    for player in left_fac.check():
        if player.type_string == 'player':
            fac1_players.append(player)
    for player in right_fac.check():
        if player.type_string == 'player':
            fac2_players.append(player)
    if len(fac1) > 16: fac1 = fac1[:16]
    if len(fac2) > 16: fac2 = fac2[:16]
    fac_str = fac1 + ' '*(54-len(fac1+fac2))+fac2
    print fac_str
    print '%d'% left_fac.points + ' '*21 + '==VERSUS=='+ ' '*21+'%d'% right_fac.points
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

def read_log(game, length=3):
    for i in range(length):
        try:
            print game.read_log()[-length+i]
        except:
            pass
 ################# END PRINT FROM GAME OBJECT  #################

        
def abrev(name):
    name_dict = {'Player One':'P1', 'Player Two':'P2', 'Player Three':'P3', 'Player Four':'P4'} 
    if name in name_dict:
        return name_dict[name]
    else:
        return name[:2].upper()
    

 ##################  PRINT FROM SNAPSHOT  ###################
def print_from_snapshot(snapshot):
    print_str = ''
    width = 54
    #decorative border
    print_str += '='*width+'\n'
    #factions
    leftname = snapshot['leftfaction']['name']
    leftscore = str(snapshot['leftfaction']['score'])
    rightname = snapshot['rightfaction']['name']
    rightscore = str(snapshot['rightfaction']['score'])
    gap = width /2 - 7
    if len(leftname) >gap : leftname = leftname[:gap]
    if len(rightname) > gap: rightname = rightname[:gap]
    print_str += leftname+' '*(width-len(leftname+rightname))+rightname+'\n'
    #score and VERSUS decoration
    deco = '==VERSUS=='
    padding = width -2 - len(deco)
    half_pad = padding / 2
    if padding % 2: padding = ' '
    else: padding = ''
    score_str = leftscore+' '*half_pad+padding+deco+' '*half_pad+rightscore
    print_str += score_str + '\n'

    #tokens  TODO
        #card prep while we're here: righthands lefthands for later
    tokenspots = {}
    lefthands = []
    for player_name in snapshot['leftfaction']['players']:
        player_info = snapshot[player_name]

        if player_info['spot']: 
            spot=player_info['spot']
            if spot not in tokenspots:
                tokenspots[spot] = []
            char_string = '@/ '
            if 'imp' in snapshot:
                for suffering in snapshot['imp']:
                    if player_name == suffering['victim']:
                        if suffering['type'] == 'cry':
                            char_string = char_string[:-1]+'?'
                        else:
                            char_string = '@!'+char_string[-1]
            tokenspots[spot].append(char_string)
        else: spot = None
        #card prep
        hand_str = abrev(player_name)+':'
        if 'game' in snapshot: cards = player_info['cards']
        elif 'mycards' in snapshot and snapshot['mycards'][0] == player_name: cards = snapshot['mycards'][1]
        else: cards = 0
        if cards:
            for card in cards:
                hand_str += str(card)+' '
        else: 
            hand_str+='X '*player_info['num_cards']
        if hand_str: hand_str = hand_str[:-1]
        lefthands.append(hand_str)

    righthands = []
    for player_name in snapshot['rightfaction']['players']:
        player_info = snapshot[player_name]
        if player_info['spot']: 
            spot=player_info['spot']
            if spot not in tokenspots:
                tokenspots[spot] = []
            char_string = '\\@ '
            if 'imp' in snapshot:
                for suffering in snapshot['imp']:
                    if player_name == suffering['victim']:
                        if suffering['type'] == 'cry':
                            char_string = char_string[:-1]+'?'
                        else:
                            char_string = '!@'+char_string[-1]
            tokenspots[spot].append(char_string)
        else: spot = None
        #card info
        hand_str = ''
        if 'game' in snapshot: cards = player_info['cards']
        elif 'mycards' in snapshot and snapshot['mycards'][0] == player_name: cards = snapshot['mycards'][1]
        else: cards = 0
        if cards:
            for card in cards:
                hand_str += str(card)+' '
        else: 
            hand_str+='X '*player_info['num_cards']
        if hand_str: hand_str = hand_str[:-1]
        hand_str += ':'+abrev(player_name)
        righthands.append(hand_str)


        #done with card prep, now token work:
        # tokenspots
        #dragon charset:  '\\V/'
        #optional:         '+ +'
        #                ,'\\_/'
    full_lines = ['']*4
    for i in range(1,19):
        for j in range(4):
            try:
                full_lines[j] += tokenspots[i][j]
            except IndexError:
                full_lines[j] += '   '
            except KeyError:
                full_lines[j] += '   '
    for i in range(1,5):
        print_str += full_lines[-i]+'\n'
    #bridge
    bridge_str = 'XX XX ^^ ^^ '*5
    bridge_str = bridge_str[:-6]
    print_str += bridge_str +'\n'
    #distance counter
    if 'choices' in snapshot:
        dist_line = distance_str(snapshot, snapshot['choices'][0])
    elif 'mycards' in snapshot:
        dist_line = distance_str(snapshot, snapshot['mycards'][0])
    else:
        dist_line = ' '*width
    print_str += dist_line+'\n'

    #decorative divider
    print_str += '-'*width+'\n'
    #graveyard
    grave = snapshot['grave']
    count = [None,0,0,0,0,0]
    for value in grave:
        count[value] += 1
    grave_str = 'Discard Pile:'
    for num in range(1,6):
        grave_str += ' '+str(num)+'x'
        if max(count)>9 and count[num]<10: grave_str += '0'
        grave_str += str(count[num])
    print_str += grave_str + '\n'
    #deck count, turn order
        #deck
    deck = snapshot['deck']
    try:
        decklen = len(deck[0])
    except:
        decklen = deck[0]
    deck_count = '%s Cards Left' % decklen
    if deck[1]: deck_count += ' (%s Cycle Remaining)'
        #turn
    turn_str = 'Turn Order: '
    for name in snapshot['turnorder']:
        if name == snapshot['whosturn']:
            turn_str += '>'+abrev(name)+'<, '
        else:
            turn_str += abrev(name)+', '
    if turn_str: turn_str = turn_str[:-2]
        #all together now
    deck_line = turn_str +' '*(width - len (deck_count+turn_str))+ deck_count
    print_str += deck_line+'\n'
    # player hands: count or reveal if master
        # lefthands and righthands from above
    card_line = ['', '']
    for i in range(5):
        try:
            card_line[0] = lefthands[i]
        except IndexError:
            card_line[0] = ''
        try:
            card_line[1] = righthands[i]
        except IndexError:
            card_line[1] = ''
        if card_line[0] or card_line[1]: 
            print_str += card_line[0]+ ' '*(width -len(card_line[0]+card_line[1]))+card_line[1]+'\n'
    #log
    for i in range(5):
        if 5-i <= len(snapshot['log']):
            print_str += snapshot['log'][-5+i]+'\n'
    # choices available
    #print_str += snapshot['choices']
    if 'choices' in snapshot:
        print_str += snapshot['choices'][0]+"'s Options:\n"
        print_str += str(snapshot['choices'][1])+'\n'
    return print_str

def distance_str(snapshot, player_name):
    cur_spot = snapshot[player_name]['spot']
    enemy_spots = []
    if player_name in snapshot['leftfaction']['players']:
        rival = 'rightfaction'
    else:
        rival = 'leftfaction'
    for player in snapshot[rival]['players']:
        spot = snapshot[player]['spot']
        if spot and spot not in enemy_spots:
            enemy_spots.append(spot)
    counter_str = ''
    for i in range(1,19):
        dist = i - cur_spot
        if i in enemy_spots:
            dist = abs(dist)
            if dist < 10:
                d_string = '0'+str(dist)
            else:
                d_string = str(dist)
        else:
            if 10 > dist > 0:
                d_string = 'd'+str(dist)
            elif -10 < dist < 0:
                d_string = 'u'+str(abs(dist))
            else:
                d_string = '  '
        counter_str += d_string+' '
    return counter_str

 ################  END PRINT FROM SNAPSHOT  #################








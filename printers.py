

def abrev(name):
    name_dict = {'Player One':'P1', 'Player Two':'P2', 'Player Three':'P3', 'Player Four':'P4'} 
    if name in name_dict:
        return name_dict[name]
    else:
        words= name.split(' ')
        if len(words) > 1:
            abr = words[0][0].upper()+words[1][0].upper()
        else: 
            abr = name[:2].upper()
            #abr = name[0].upper()+name[-1].upper()
        return abr
    

 ##################  PRINT FROM SNAPSHOT  ###################
def print_from_snapshot(snapshot):
    print_str = ''
    width = 54
    l_pad = '\n'+' '*5
    print_str += l_pad
    #decorative border
    game_name = 'CIRCUITS AND STEEL'
    deco_len = (width-len(game_name))/2
    side_deco = '='*(deco_len-2)
    half_pad = ''+'='*((width-len(game_name))%2)
    deco_str = side_deco+half_pad+'  '+game_name+'  '+side_deco
    print_str += deco_str+l_pad
    #factions
    leftname = snapshot['leftfaction']['name']
    leftscore = str(snapshot['leftfaction']['score'])
    rightname = snapshot['rightfaction']['name']
    rightscore = str(snapshot['rightfaction']['score'])
    gap = width /2 - 7
    if len(leftname) >gap : leftname = leftname[:gap]
    if len(rightname) > gap: rightname = rightname[:gap]
    print_str += leftname+' '*(width-len(leftname+rightname))+rightname+l_pad
    #score and VERSUS decoration
    deco = '==VERSUS=='
    padding = width -2 - len(deco) # scores each always have len 1
    half_pad = padding / 2
    if padding % 2: padding = ' '
    else: padding = ''
    score_str = leftscore+' '*half_pad+padding+deco+' '*half_pad+rightscore
    print_str += score_str + l_pad

    #tokens
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
            if player_info['winded'] and player_name != snapshot['whosturn']:
                char_string = char_string[:1]+' '+char_string[2:]
            if 'imp' in snapshot:
                for suffering in snapshot['imp']:
                    if player_name == suffering['victim']:
                        if suffering['type'] == 'cry':
                            char_string = char_string[:-1]+'?'
                        else:
                            char_string = '!'+char_string[1:]
            tokenspots[spot].append(char_string)
        else: spot = None
        #card prep
        hand_str = abrev(player_name)+':'
        if 'cards' in player_info: cards = player_info['cards']
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
        if player_info['spot'] and not player_info['dragon']:  
            spot=player_info['spot']
            if spot not in tokenspots:
                tokenspots[spot] = []
            char_string = '\\@ '
            if player_info['winded'] and player_name != snapshot['whosturn']:
                char_string = ' '+char_string[1:]
            if 'imp' in snapshot:
                for suffering in snapshot['imp']:
                    if player_name == suffering['victim']:
                        if suffering['type'] == 'cry':
                            char_string = char_string[:-1]+'?'
                        else:
                            char_string = char_string[0]+'!'+char_string[-1]
            tokenspots[spot].append(char_string)
        elif player_info['spot']: # DRAGON
            headspot = player_info['spot']
            tokenspots[headspot] = ['\\_/','+ +', '/V\\','   ']
            bodychars = ( ('__/',  '\\/ ', '  _'),
                          ('\\__', ' \\/', '_WW'),
                          ('/\\_', '  \\', '__ '),
                          ('_/\\', '/  ',  ' __'))
            if player_info['winded']:
                tokenspots[player_info['spot']][1] = '> <'
            if headspot < 18:
                for spot in range(headspot+1, 19):
                    tokenspots[spot] = bodychars[(spot-headspot-1)%4]

            if 'imp' in snapshot and player_name in [suffering['victim'] for suffering in snapshot['imp']]:
                tokenspots[player_info['spot']][3] = '!!!'
        else: spot = None
        #card info
        hand_str = ''
        if 'cards' in player_info: cards = player_info['cards']
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
        print_str += full_lines[-i]+l_pad
    #bridge
    bridge_str = 'XX XX ^^ ^^ '*5
    bridge_str = bridge_str[:-6]
    print_str += bridge_str +l_pad
    #distance counter
    if 'choices' in snapshot:
        dist_line = distance_str(snapshot, snapshot['choices'][0])
    elif 'mycards' in snapshot:
        dist_line = distance_str(snapshot, snapshot['mycards'][0])
    else:
        dist_line = ' '*width
    print_str += dist_line+l_pad

    #decorative divider
    print_str += '-'*width+l_pad
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
    print_str += grave_str + l_pad
    #deck count, turn order
        #deck
    deck = snapshot['deck']
    try:
        decklen = len(deck[0])
    except:
        decklen = deck[0]
    deck_count = '%s Cards Left' % decklen
    if deck[1]: deck_count += ' (%s Cycle Remaining)' % deck[1]
        #turn
    turn_str = 'Turn Order: '
    for name in snapshot['turnorder']:
        if name == snapshot['whosturn']:
            turn_str += '>'+abrev(name)+'<, '
        else:
            turn_str += abrev(name)+', '
    if turn_str: turn_str = turn_str[:-2]
        #all together now
    if len(turn_str + deck_count) > width:
        deck_line = turn_str +l_pad
        deck_line += ' '*(width - len (deck_count))+ deck_count
    else:
        deck_line = turn_str +' '*(width - len (deck_count+turn_str))+ deck_count
    print_str += deck_line+l_pad
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
            print_str += card_line[0]+ ' '*(width -len(card_line[0]+card_line[1]))+card_line[1]+l_pad
    #log
    no_pad = '\n'
    print_str = print_str[:-len(l_pad)]+no_pad
    for i in range(5):
        if 5-i <= len(snapshot['log']):
            print_str += snapshot['log'][-5+i]+no_pad
    # choices available
    #print_str += snapshot['choices']
    if 'choices' in snapshot:
        snapshot['choices'][1].sort()
        print_str += snapshot['choices'][0]+"'s Options:"+l_pad
        print_str += str(snapshot['choices'][1])+no_pad
    return print_str

def distance_str(snapshot, player_name):
    cur_spot = snapshot[player_name]['spot']
    enemy_spots = []
    if player_name in snapshot['leftfaction']['players']:
        rival = 'rightfaction'
        dir_strs = ('f','b')
    else:
        rival = 'leftfaction'
        dir_strs = ('b','f')
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
                d_string = dir_strs[0]+str(dist)
            elif -10 < dist < 0:
                d_string = dir_strs[1] +str(abs(dist))
            else:
                d_string = '  '
        counter_str += d_string+' '
    return counter_str

 ################  END PRINT FROM SNAPSHOT  #################








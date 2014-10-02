from linker import Linker, Location
from cards import Card, Hand, GraveYard, Deck
from board import Token, GameSpace
from others import Player, Faction
from actions import Suffering, Attack, Defend, DashingStrike, OptionTray, Move, Push, Retreat, RequestDashingAid, DashingBlock, DenyAid, TakeTheHit
import random

###################CONTROL CLASSES#####################

class Game(Linker):
    def __init__(self):
        self.gameboard = {}
        self.public_info = []
        self.turn_order = []
        self.game_type = 0
        self.whos_turn = 0
        self.next_tray = 0
        self.winner = 0
        self.game_log = []
        self.game_id = 0

###############OBJECT REGISTRATION ACT##############
#also internal investigations

    def register(self, obj):
        x = obj.type_string
        if x not in self.gameboard:
            self.gameboard[x] = []
        self.gameboard[x].append(obj)
        if obj not in self.public_info and getattr(obj, 'public', 0):
            self.public_info.append(obj)
        return obj

    def deregister(self, obj):
        x = obj.type_string
        if x in self.gameboard:
            self.gameboard[x].remove(obj)


    def spaces(self):
        if 'gamespace' not in self.gameboard:
            self.gameboard['gamespace'] = []
        if len(self.gameboard['gamespace']) > 18:
            raise Error #Only 18 spaces in this game
        return self.gameboard['gamespace']

    def deck(self):
        if 'deck' not in self.gameboard:
            self.gameboard['deck'] = []
        if len(self.gameboard['deck']) > 1:
            raise Error #Only one deck in this game
        return self.gameboard['deck'][0]

    def veiw(self, player):
        return self.public_info + player.private_info()

    def is_game_over(self):   # 0 game on  1 time_out   fac_obj: winner!
        winner = 0
        for i in self.gameboard['faction']:
            alive = 0
            for j in i.check('connected'): #players
                if j.type_string == 'token':
                    alive += j.stat()
            if not alive: winner = i.check('rival')[0]
        if not winner:
            if not self.deck().cycles and not self.deck().top_card():
                return 1
            else:
                return 0
        else:
            return winner

    def log(self, text):
        self.game_log.append(text)

    def read_log(self):
        return self.game_log

    def snapshot(self, player_id=0):
        this_player = 0
        suff_dict_list = []
        suff_list =[]
        for player in self.gameboard['player']:
            suff_list += player.check('suffering')
        for suff in suff_list:
            suff_dict = {'type': suff.suf_type, 'can_call':suff.can_call_for_aid , 'source':0 , 'victim':suff.check('player')[0].pretty_name() , 'amount': suff.amount, 'distance':suff.distance , 'cards': [card.value for card in suff.victim_cards]
                    }
            if suff.suf_type == 'cry':
                suff_dict['source'] = suff.source_player().pretty_name()
            suff_dict_list.append(suff_dict)
        if self.next_tray:
            choice_tuple = (self.next_tray.check('owner')[0].pretty_name(),
                    self.next_tray.choice_ids
                    )
        else: choice_tuple = (0,0)

        snapshot = {
                'log': self.game_log,
                'turnorder':[player.pretty_name() for player in self.turn_order], 
                'whosturn': self.whos_turn.pretty_name() ,
                'imp':suff_dict_list,
                'deck': (len(self.gameboard['deck'][0].check()), self.gameboard['deck'][0].cycles),
                'grave': [card.value for card in self.gameboard['graveyard'][0].check()]
                }
        en_dir = 'down'
        for faction in self.gameboard['faction']:
            points = faction.points
            name = faction.pretty_name()
            players = [player.pretty_name() for player in faction.players()]
            if en_dir == 'down':
                snapshot['leftfaction'] = {'name':name, 'score':points, 'players':players}
            elif en_dir == 'up':
                snapshot['rightfaction'] = {'name':name, 'score':points, 'players':players}
            en_dir = 'up'

        for player in self.gameboard['player']:
            player_name = player.pretty_name()
            while player_name in snapshot or player_name in ['choices', 'game', 'mycards']:
                #player_name += random.randint(0,9)
                    #can't because faction link, turnorder link =/
                raise Exception #Bad Player Name
            snapshot[player_name] = {'dragon':player.is_dragon(), 'num_cards':len(player.cards()), 'spot':player.token_spot_val(), 'health':player.stat(), 'winded':player.winded, 'faction':player.check()[0].pretty_name(), 'score':player.score(), 'color':player.check('owns')[0].color(), 'controller':player.controller}
            if player_id == player.id_num:
                this_player = player
        if this_player:
            snapshot['mycards'] = (this_player.pretty_name(), [card.value for card in this_player.cards()])
            if this_player.pretty_name() == choice_tuple[0]:
                snapshot['choices'] = choice_tuple
        return snapshot

    def master_snapshot(self):
        snapshot = self.snapshot()
        for player in self.gameboard['player']:
            player_cards = [card.value for card in player.cards()]
            snapshot[player.pretty_name()]['cards'] = player_cards
            snapshot[player.pretty_name()]['id_num'] = player.id_num
        snapshot['deck'] = ([card.value for card in self.gameboard['deck'][0].check()], self.gameboard['deck'][0].cycles)
        snapshot['game'] = (self.game_type, self.game_id)
        if self.next_tray:
            choice_tuple = (self.next_tray.check('owner')[0].pretty_name(),
                    self.next_tray.choice_ids
                    )
            snapshot['choices'] = choice_tuple
        return snapshot


##############END OBJECT REGISTRATION ACT###########
#############CREATE GAME###############

    def spawn_from_snapshot(self, snapshot):
        self.game_id = snapshot['game'][1]
        self.game_type = snapshot['game'][0]
        self.game_log = snapshot['log']
        self.gameboard = {}

        ##############GAME BOARD#############
        # always the same
        x = 'dark'
        for i in range(9):
            y = self.register(GameSpace(x))
            z = self.register(GameSpace(x))
            y.des = str(2*i+1)
            z.des = str(2*i+2)
            if x == 'dark':
                x = 'light' 
            else:
                x = 'dark'

        for i in range(len(self.spaces())-1):
            self.spaces()[i].interact(self.spaces()[i+1])

        ############FACTIONS#################

        fac1_name = snapshot['leftfaction']['name']
        fac1_score = snapshot['leftfaction']['score']
        fac2_name = snapshot['rightfaction']['name']
        fac2_score = snapshot['rightfaction']['score']
        fac1 = self.register(Faction(fac1_name))
        fac1.points = fac1_score
        fac2 = self.register(Faction(fac2_name))
        fac2.points = fac2_score
        fac1.link(fac2, 'rival')

        ##############CARD GRAVEYARD############## 
        grave = self.register(GraveYard())
        self.gameboard['deadtoken'] = []
        for card_val in snapshot['grave']:
            grave.interact(self.register(Card(grave, card_val)))
        ##############CARD DECK############## 
        deck = self.register(Deck(grave, snapshot['deck'][1]))
        for card_val in snapshot['deck'][0]:
            deck.interact(self.register(Card(grave, card_val)))
        deck.shuffle()

        ############PLAYERS##################
        ##############TOKENS#################
        #############HHANDS###################
        #fac1_name
        for fac_string in ['leftfaction', 'rightfaction']: 
            for player_name in snapshot[fac_string]['players']:
                player_info = snapshot[player_name]
                x = self.register(Player(self.game_id, player_info['id_num'], player_name))
                self.turn_order.append(x)
                x.winded = player_info['winded']
                x.status = player_info['health']
                x.dragon = player_info['dragon']
                x.controller = player_info['controller']
                token = self.register(Token(player_info['color']))
                x.interact(token)
                token.status = x.status
                token.winded = x.winded
                token.dragon = x.dragon

                if fac_string == 'leftfaction':
                    x.interact(fac1)
                else:
                    x.interact(fac2)
                p_hand = self.register(Hand())
                x.interact(p_hand)
                if(token.status >0):
                    gamespot = self.gameboard['gamespace'][player_info['spot']-1]
                    gamespot.interact(token)
                    token.interact(x.check()[0])
                    player_info['token'] = token
                    player_info['gamespot'] = gamespot
                for card_val in player_info['cards']:
                    card = self.register(Card(grave, card_val))
                    p_hand.interact(card)
                player_info['object'] = x
                player_info['hand'] = p_hand
        self.turn_order = []
        for player in snapshot['turnorder']:
            self.turn_order.append(snapshot[player]['object'])
        self.whos_turn = snapshot[snapshot['whosturn']]['object']

    ############ ACTION TRAY ############
        if not self.is_game_over():
            cries = []
            not_cries = []
            try:
                impending = snapshot['imp']
            except:
                impending = []
            #impending = getattr(snapshot, 'imp', [])
            for suffering in impending:
                if suffering['type'] == 'cry':
                    cries.append(suffering)
                else:
                    not_cries.append(suffering)
            for suffering in not_cries:
                suf_obj = self.gen_suff_from_snap(suffering, snapshot)
                snapshot[suffering['victim']]['suffering'] = suf_obj
            for suffering in cries:
                suf_obj = self.gen_suff_from_snap(suffering, snapshot)
                suf_obj.interact(snapshot[suffering['source']]['suffering'])
            if not impending:
                self.next_tray = self.make_action_tray(self.whos_turn)
            else:
                self.update_next_tray()
        else:
            self.next_tray = 0


    def gen_suff_from_snap(self, suffering, snapshot):
        victim = suffering['victim']
        source = suffering['source']
        token = snapshot[victim]['token']
        p_obj = snapshot[victim]['object']
        if source:
            source_obj = snapshot[source]['object']
            source_hand = snapshot[source]['hand']
        victim_cards = []
        if suffering['cards']:
            cards = source_hand.check()[:]
            for card_val in suffering['cards']:
                for card in cards:
                    if card.value == card_val and len(victim_cards) < len(suffering['cards']):
                        cards.remove(card)
                        victim_cards.append(card)

        suf_obj = Suffering(token, p_obj, suffering['type'],suffering['amount'],  suffering['distance'], victim_cards)
        suf_obj.can_call_for_aid = suffering['can_call']
        return suf_obj


    #############DRAGON##################
    ###############TRAITOR###############
    ################POWERS###############

    #                TBI                # 
        
###########END CREATE GAME#############

  #################  START TRAY CONSTRUCTION  ##################

    def make_action_tray(self, player):
        #move attack push dashing strike
        tray = self.register(OptionTray(player))
        p_token = player.check('owns')[0]
        p_token_space = p_token.check('at')[0]
        cards = player.check('has')[0].check('connected')
        unique_cards = {}
        for i in cards:
            if i.value not in unique_cards: unique_cards[i.value] =[]
            unique_cards[i.value].append(i)
        rival_tokens = []
        for i in player.check('connected')[0].check('rival')[0].check('connected'):
            if i.type_string == 'token':
                rival_tokens.append(i)
        #okay fine let's figure out what direction the enemy is
        enemy_direction = p_token.closest_enemy()[1]
        for i in unique_cards:
            #Move
            Move(tray, p_token, unique_cards[i][0], 'up')
            Move(tray, p_token, unique_cards[i][0], 'down')
            #Attack
            x = p_token_space.count(i, enemy_direction)
            if x:
                if set( x.check('has')) & set( rival_tokens):
                    for j in range(1, len(unique_cards[i])+1):
                        Attack(tray, x, unique_cards[i][:j])
            #Push
            x = p_token_space.count(1, enemy_direction)
            if x and x.count(1, enemy_direction):
                if set( x.check('has')) & set( rival_tokens):
                    Push(tray, x, unique_cards[i][0], enemy_direction)
            #Dashing Strike
            dash_stop = p_token_space.safe_count(i, enemy_direction, p_token.check()[0])
            for k in unique_cards: 
                if k != i or len(unique_cards[i]) > 1:
                    if k == i:
                        attk_cards = unique_cards[k][1:]
                    else:
                        attk_cards = unique_cards[k]
                    x = dash_stop.count(k, enemy_direction)
                    if x:
                        if set( x.check('has')) & set( rival_tokens):
                            for j in range(1, len(attk_cards)+1):
                                DashingStrike(tray, x, p_token, enemy_direction, unique_cards[i][0], attk_cards[:j])

            
        return tray


    def make_suffering_tray(self, suffering):
        tray = self.register(OptionTray(suffering.check('player')[0]))
        tray.action = 0
        suffering.link(tray, 'tray', 'suffering')
        token = suffering.check('token')[0]
        spot = token.check('at')[0]
        cards = suffering.check('player')[0].check('has')[0].check() 
        amount = suffering.amount
        distance = suffering.distance
        card_values = []
        unique_cards = {}
        for i in cards:
            if i.value not in card_values: 
                unique_cards[i.value]=[i]
            else:
                unique_cards[i.value].append(i)
            card_values.append(i.value)
                # Cry
        if suffering.suf_type == 'cry':
            source_suf = suffering.check('suffering')[0]
            s_spot = source_suf.check('token')[0].check('at')[0]
            move_val, direction = spot.how_far(s_spot)
            try:
                if move_val:
                    move_card = unique_cards[move_val].pop()
                else:
                    move_card = 0
                blk_cards = []
                for i in range(amount):
                    blk_cards.append(unique_cards[distance].pop())
                can_aid = 1
            except KeyError:
                can_aid = 0 
            except IndexError:
                can_aid = 0
            DenyAid(tray, suffering)

            if can_aid:
                DashingBlock(tray, suffering, source_suf, token, direction, move_card, blk_cards)
                # Attack  Dashing Strike
        elif suffering.suf_type in  ['dashing strike', 'attack']:
            if suffering.can_call_for_aid and ( self.game_type in [1, 3] or (self.game_type > 3 and token.dragon == 0)) :
                enemy_dir = token.closest_enemy()[1]
                if enemy_dir == 'up': cry_dir = 'down'
                else: cry_dir = 'up'
                if distance not in unique_cards: unique_cards[distance] = []
                min_needed = amount - len(unique_cards[distance])
                if min_needed < 1: min_needed = 1

                targets1 = token.check()[0].check()
                targets = []
                for i in targets1: # same faction tokens
                    if i.type_string == 'token':
                        i_player = i.check('owned')[0]
                        if i_player.winded == 0 and i_player != suffering.check('player')[0]:
                            i_dist = spot.how_far(i.check('at')[0])
                            if i_dist[0]==0 or (i_dist[1] == cry_dir and i_dist[0] < 6):
                                targets.append(i)

                if targets:
                    for requested_amount in range(min_needed, amount+1):
                        #my_cards = amount-i
                        my_cards = unique_cards[distance][:amount-requested_amount]
                        #hope above doesn't break!
                        
                        RequestDashingAid(tray, my_cards, targets, suffering, requested_amount)

            #print "can we defend?", distance, unique_cards, amount
            if distance in unique_cards:
                if len(unique_cards[distance]) >= amount:
                    Defend(tray, suffering, unique_cards[distance][:amount])
            TakeTheHit(tray, token, suffering)
        else:
            raise Exception # no other suff types!

        if suffering.suf_type == 'dashing strike':
            en_dir = token.closest_enemy()[1]
            if en_dir == 'up': run_dir = 'down'
            else: run_dir = 'up'
            if spot.count(1, run_dir):
                for run_value in unique_cards:
                    if unique_cards[run_value]:
                        Retreat(tray, suffering, token, run_dir, unique_cards[run_value][0])
                    

  #################  END TRAY CONSTRUCTION  ##################

  #################  BEGIN FLOW CONTROL FUNCITONS  #################
    def reset_match(self, who_won=''):
        for i in self.gameboard['tray']:
            i.destroy()
            self.deregister(i)
        for player in self.gameboard['player']:
            token = player.check('owns')[0]
            faction = player.check()[0]
            if not token.check():
                token.interact(faction)

        for i in self.gameboard['faction'][0].check():
            if i.type_string == 'token':
                i.stat(1)
                i.interact(self.spaces()[0]) #hope they're still in order!
        for i in self.gameboard['faction'][1].check():
            if i.type_string == 'token':
                i.stat(1)
                i.interact(self.spaces()[-1]) #hope they're still in order!

        deck = self.deck()
        for i in self.gameboard['card']:
            i.interact(deck)
        deck.shuffle()
        if self.game_type in [5,6,7]:
            deck.cycles = 1
        else:
            deck.cycles = 0
        for i in self.gameboard['hand']:
            for j in range(5):
                i.interact(deck)
	for i in self.gameboard['player']:
		i.winded = 0
        self.turn_order = self.create_turn_order(who_won)
        self.whos_turn = self.turn_order[0]
        self.next_tray = self.make_action_tray(self.whos_turn)
        self.log('New match begins!')
        log_string = ''
        for i in self.turn_order:
            log_string += i.pretty_name()+' '
        self.log('Turn Order set: '+log_string)

    def create_turn_order(self, who_won=''):
        factions = self.gameboard['faction']
        if not who_won:
            who_won = factions[random.choice([0,1])]
        fac1_order = [[],[],[]]
        fac1_vote = 0
        for i in factions[0].check():
            if i.type_string == 'player':
                fac1_order[i.in_team_order()].append(i)
                fac1_vote+=i.fac_order()
        random.shuffle(fac1_order[0]) 
        random.shuffle(fac1_order[1]) 
        random.shuffle(fac1_order[2]) 
        fac1_order = fac1_order[0]+fac1_order[1]+fac1_order[2]

        fac2_order = [[],[],[]]
        fac2_vote = 0
        for i in factions[1].check():
            if i.type_string == 'player':
                fac2_order[i.in_team_order()].append(i)
                fac2_vote+=i.fac_order()
        random.shuffle(fac2_order[0]) 
        random.shuffle(fac2_order[1]) 
        random.shuffle(fac2_order[2]) 
        fac2_order = fac2_order[0]+fac2_order[1]+fac2_order[2]
        fac_order = [fac1_order, fac2_order]
        
        turn_order = []
        if self.game_type > 3 : # DRAGON
            turn_order = fac1_order + fac2_order
        else: # no dragon
            if who_won == factions[1] and fac1_vote:
                if fac1_vote > 0: choice = 1
                else: choice = 0
            elif who_won == factions[0] and fac2_vote:
                if fac2_vote > 0: choice = 0
                else: choice = 1
            else:
                choice = random.choice([0,1])
            for i in range(len(fac_order[0])):
                turn_order.append(fac_order[choice][i])
                turn_order.append(fac_order[1-choice][i])
        return turn_order


    def time_out(self):
        fac_tokens = []
        for i in self.gameboard['faction']:
            fac_tokens.append({})
            for j in i.check('connected'): #players
                if j.type_string == 'player':
                    cards = j.check('has')[0].check('connected') 
                    token = j.check('owns')[0]
                    t_space = token.check('at')[0]
                    if t_space not in fac_tokens[-1]: fac_tokens[-1][t_space] = [[],{}]
                    fac_tokens[-1][t_space][0].append(token) # trusts factions can't share spots
                    x2 = fac_tokens[-1][t_space][1]
                    for i2 in cards:
                        if i2.value not in x2: x2[i2.value] = []
                        x2[i2.value].append(i2)
        # okay so we made fac_tokens list of { gamespace:[[tokens],{card_val:[cards]}]}
        # okay now fac_tokens[1] vs fac_tokens[0]
        # try to trade last-hits
        fac1_list = fac_tokens[0]
        fac2_list = fac_tokens[1]
        for f1_space in fac1_list:
            f1_card_dict = fac1_list[f1_space][1]
            f1_token = fac1_list[f1_space][0][0]
            enemy_dir = f1_token.closest_enemy()[1]
            for card_val in f1_card_dict:
                f1_cards = f1_card_dict[card_val]
                possible_target = f1_space.count(card_val, enemy_dir) 
                if possible_target in fac2_list:
                    if card_val in fac2_list[possible_target][1]:
                        f2_cards = fac2_list[possible_target][1].pop(card_val) #must pop so no double-counting
                    else:
                        f2_cards = []
                    if len(f1_cards) > len(f2_cards):
                        self.log(self.gameboard['faction'][0].pretty_name()+' deliver a last-hit to '+possible_target.pretty_name())
                        for guy in possible_target.check('has'):
                            guy.take_hit()
                    if len(f1_cards) < len(f2_cards):
                        self.log(self.gameboard['faction'][1].pretty_name()+' deliver a last-hit to '+f1_space.pretty_name())
                        for guy in f1_space.check('has'):
                            guy.take_hit()
        
                    # intentional to not remove cards contributed by now dead guys
                    # everyone stabs at once in the melee!
                    # (maybe check the rules on that)

        for f2_space in fac2_list:
            f2_card_dict = fac2_list[f2_space][1]
            f2_token = fac2_list[f2_space][0][0]
            # need to update token list in case people died
            # but no, even if they died they can strike at others
            # look, we know this is the rightguys
            enemy_dir = 'up'  # HACK
            for card_val in f2_card_dict:
                f2_cards = f2_card_dict[card_val]
                possible_target = f2_space.count(card_val, enemy_dir) 
                if possible_target in fac1_list:
                    if card_val in fac1_list[possible_target][1]:
                        f1_cards = fac1_list[possible_target][1].pop(card_val) # now we pop because we can't stop
                    else:
                        f1_cards = []
                    if len(f2_cards) > len(f1_cards):
                        self.log(self.gameboard['faction'][1].pretty_name()+' deliver a last-hit to '+possible_target.pretty_name())
                        for guy in possible_target.check('has'):
                            guy.take_hit()
                    if len(f2_cards) < len(f1_cards):
                        self.log(self.gameboard['faction'][0].pretty_name()+' deliver a last-hit to '+f2_space.pretty_name())
                        for guy in f1_space.check('has'):
                            guy.take_hit()
            #really hope that cut and paste went okay
       
                                
        # if both sides still up after trading blows
        winner = 0
        fac1_token = 0
        fac2_token = 0
        for fac in self.gameboard['faction']:
            any_alive = 0
            for token in fac.check('connected'):
                if token.type_string == 'token':
                    if fac == self.gameboard['faction'][0]:
                        fac1_token = token
                    else:
                        fac2_token = token
                    any_alive += token.stat()
            if not any_alive:
                winner = fac.check('rival')[0]   
        #then measure who got the farthest
        if not winner:
            fac2_dist = fac1_token.closest_enemy()[0] + fac1_token.check('at')[0].how_far(self.gameboard['gamespace'][0])[0]
            fac1_dist = fac2_token.closest_enemy()[0] + fac2_token.check('at')[0].how_far(self.gameboard['gamespace'][17])[0]
            if fac1_dist < fac2_dist:
                winner = self.gameboard['faction'][0]
                self.log(winner.pretty_name()+' won by distance')
            if fac1_dist > fac2_dist:
                winner = self.gameboard['faction'][1]
                self.log(winner.pretty_name()+' won by distance')
        else:
            self.log(winner.pretty_name()+' won by final blows')
        return winner 

    def make_choice(self, choice):
        if choice in self.next_tray.choice_ids:
            self.log(choice+':'+self.next_tray.resolve(choice))
            self.gameboard['tray'].remove(self.next_tray)
            self.next_tray = 0
            for token in self.gameboard['token']:
                owner = token.check('owned')[0]
                if token.status == 0:
                    self.gameboard['token'].remove(token)
                    self.gameboard['deadtoken'].append(token)
                    if owner in self.turn_order:
                        self.turn_order.remove(owner)
            self.update_next_tray()

        

    def update_next_tray(self):
        if not self.is_game_over():
            if not self.next_tray:
                suffering = []
                for i in self.gameboard['player']:
                    x = i.check('suffering')
                    for j in x:
                        if not j.check('tray'):
                            suffering.append(j)
                #Need to change this to only make tray for the best suffering
                cry_suffs = []
                noncry_suffs = []
                for i in suffering:
                    if i.suf_type == 'cry':
                        cry_suffs.append(i)
                    else:
                        noncry_suffs.append(i)
                if cry_suffs:#pick best
                    cause_origin = cry_suffs[0].check('suffering')[0].check('token')[0].check('at')[0] #hope that works!
                    best_suff = [20,cry_suffs[0]]
                    for x in cry_suffs:
                    #best is the closest to cause_suf_spot, then first in turn order
                        y = cause_origin.how_far(x.check('token')[0].check('at')[0])[0] 
                        if y == best_suff[0]:
                            cur_suff_turn_num = self.turn_order.index(best_suff[1].check('player')[0])
                            new_suff_turn_num = self.turn_order.index(y.check('player')[0])
                            if cur_suff_turn_num > new_suff_turn_num:
                                best_suff[0] = y
                                best_suff[1] = x

                        elif y < best_suff[0]:
                            best_suff[0] = y
                            best_suff[1] = x
                    self.make_suffering_tray(best_suff[1])
                elif noncry_suffs: #pick best
                    #best is the farthest back, then first in turn order
                    chosen_suff = [0,noncry_suffs[0]]
                    for x in noncry_suffs:
                        dist_to_en = x.check('token')[0].closest_enemy()[0] 
                        if dist_to_en > chosen_suff[0]:
                            chosen_suff = [dist_to_en, x]
                        elif dist_to_en == chosen_suff[0]:
                            cur_suff_turn_num = self.turn_order.index(chosen_suff[1].check('player')[0])
                            new_suff_turn_num = self.turn_order.index(x.check('player')[0])
                            if cur_suff_turn_num > new_suff_turn_num:
                                chosen_suff[0] = dist_to_en
                                chosen_suff[1] = x



                    self.make_suffering_tray(chosen_suff[1])

                if self.gameboard['tray']: #check for existing trays
                    #pick the best
                    cries = []
                    not_cries = [] # multple attacked at once!
                    for tray in self.gameboard['tray']:
                        if not tray.check('suffering'):
                            self.gameboard['tray'].remove(tray)
                            #raise Exception # shouldn't be action tray same time as suffering
                        else:
                            if tray.check('suffering')[0].suf_type == 'cry':
                                cries.append(tray)
                            else:
                                not_cries.append(tray)
                    rev_order = self.turn_order[:]
                    rev_order.reverse()
                    pick = 0
                    if cries:
                        for player in rev_order:
                            for tray in cries:
                                if player in tray.check('owner'):
                                    pick = tray
                    else:
                        for player in rev_order: # distance order?
                            for tray in not_cries:
                                if player in tray.check('owner'):
                                    pick = tray
                    self.next_tray = pick
                # if all the existing trays were garbage removed
                if not self.next_tray:
                    while self.whos_turn.winded == 1 and not self.is_game_over():
                        self.turn_wrap_up()
                    if self.is_game_over():
                        self.game_over_stuff()
                    else:
                        self.next_tray = self.make_action_tray(self.whos_turn)
        else:
            self.game_over_stuff()


    def turn_wrap_up(self):
        if self.game_type <4 or self.whos_turn == self.turn_order[-1]:
            hand = self.whos_turn.check('has')[0].check('connected')
            num_cards = 5 - len(hand)
            if num_cards < 0: num_cards = 0
            for i in range(num_cards):
                self.whos_turn.check('has')[0].interact(self.deck())

        elif self.whos_turn == self.turn_order[-2] and self.game_type > 3:
            hand = self.whos_turn.check('has')[0].check('connected')
        self.whos_turn.winded = 0
        if self.whos_turn == self.turn_order[-1]:
            self.whos_turn = self.turn_order[0]
        else:
            ind = self.turn_order.index(self.whos_turn) + 1 
            self.whos_turn = self.turn_order[ind]

    def game_over_stuff(self):
        game_over = self.is_game_over()
        if game_over == 0:
            raise Error
        elif game_over == 1:
            self.log('The match timed out!')
            winner = self.time_out()
            if winner: 
                winner.score(1)
        else:
            winner = game_over
            winner.score(1)
            self.log(winner.pretty_name()+ ' win the match.')
        if winner:
            if winner.score() < 3 and self.game_type < 4:
                self.reset_match(winner)
            else:
                self.next_tray = 0
                self.winner = winner # Game winner!
                self.log('The game is over, with %s winning %d to %d!' % (winner.pretty_name(), winner.points, winner.check('rival')[0].points))
        else:
            self.log('The match was a tie!')
            self.reset_match()


  #################  END FLOW CONTROL FUNCITONS  #################

####################END CONTROL CLASSES#####################




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

        dead_players = []
        for player in self.gameboard['player']:
            if player not in self.turn_order:
                dead_players.append(player)
        snapshot = {
                'log': self.game_log,
                'turnorder':[player.pretty_name() for player in self.turn_order], 
                'dead':[player.pretty_name() for player in dead_players],
                'whosturn': self.whos_turn.pretty_name() ,
                'imp':suff_dict_list,
                'deck': (len(self.gameboard['deck'][0].check()), self.gameboard['deck'][0].cycles),
                'grave': [card.value for card in self.gameboard['graveyard'][0].check()]
                }
        for player in self.gameboard['player']:
            player_name = player.pretty_name()
            while player_name in snapshot or player_name in ['game', 'mycards']:
                player_name += 'I'
                #maybe just an erorr =/
                raise Exception #Bad Player Name
            snapshot[player_name] = {'dragon':player.is_dragon(), 'num_cards':len(player.cards()), 'spot':player.token_spot_val(), 'health':player.stat(), 'winded':player.winded, 'faction':player.check()[0].pretty_name(), 'score':player.score(), 'color':player.check('owns')[0].color()}
            if player_id == player.id_num:
                this_player = player
        if this_player:
            snapshot['mycards'] = [card.value for card in this_player.cards()]
        return snapshot

    def master_snapshot(self):
        snapshot = self.snapshot()
        for player in self.gameboard['player']:
            player_cards = [card.value for card in player.cards()]
            snapshot[player.pretty_name()]['cards'] = player_cards
            snapshot[player.pretty_name()]['id_num'] = player.id_num
        snapshot['deck'] = ([card.value for card in self.gameboard['deck'][0].check()], self.gameboard['deck'][0].cycles)
        snapshot['game'] = (self.game_type, self.game_id, self.game_start)
        return snapshot


##############END OBJECT REGISTRATION ACT###########
#############CREATE GAME###############
    def random_gamestart_snapshot(self, game_type=0):
        rand_id = random.randint(1000,9999)
        #check against other games in progress
        snapshot = {'game':(game_type, rand_id, 1)}
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
        game_log = []
        game_log.append('Game Start, Game Type %d' % game_type)
        skip_count = 0
        is_dragon = 0
        p_health = 1
        player_id_list = [0]
        hand_size = 5
        spot = 1
        for i in range(num_players):
            if i >= fac1_size:
                skip_count = 1
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
            player_dict = {'dragon': is_dragon, 'num_cards': len(player_cards) , 'spot':spot , 'health': p_health, 'winded':0, 'faction':fac_list[skip_count] , 'score':0, 'color':color_list[i] , 'id_num':rand_num, 'cards':player_cards}
            snapshot[name_list[i]] = player_dict

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
        return snapshot

    def spawn_from_snapshot(self, snapshot):
        self.game_id = snapshot['game'][1]
        self.game_type = snapshot['game'][0]
        self.game_start = snapshot['game'][2]
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
        p1_name = snapshot['turnorder'][0]
        fac1_name = snapshot[p1_name]['faction']
        fac1_score = snapshot[p1_name]['score']
        fac2_name = ''
        for player in snapshot['turnorder']:
            x = snapshot[player]['faction'] 
            if x != fac1_name:
                fac2_name = x
                fac2_score = snapshot[player]['score']
        if not fac2_name:
            for player in snapshot['dead']:
                x = snapshot[player]['faction']
                if x != fac1_name:
                    fac2_name = x
                    fac2_score = snapshot[player]['score']
        if not fac2_name:
            raise Exception # Can't find second faction
        fac1 = self.register(Faction(fac1_name))
        fac1.score = fac1_score
        fac2 = self.register(Faction(fac2_name))
        fac2.score = fac2_score
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
        self.turn_order = []
        if 'dead' in snapshot: dead_list = snapshot['dead']
        else: dead_list = []
        for player_name in dead_list:
            player_info = snapshot[player_name]
            x = self.register(Player(self.game_id, player_info['id_num'], player_name))
            p_hand = self.register(Hand())
            x.interact(p_hand)
            x.status = player_info['health']
            x.winded = player_info['winded']
            x.dragon = player_info['dragon']
            token = self.register(Token(player_info['color']))
            x.interact(token)
            token.status = x.status
            token.winded = x.winded
            token.dragon = x.dragon
            if player_info['faction'] == fac1_name:
                x.interact(fac1)
            else:
                x.interact(fac2)

        for player_name in snapshot['turnorder']:
            player_info = snapshot[player_name]
            x = self.register(Player(self.game_id, player_info['id_num'], player_name))
            self.turn_order.append(x)
            x.winded = player_info['winded']
            x.status = player_info['health']
            x.dragon = player_info['dragon']
            token = self.register(Token(player_info['color']))
            x.interact(token)
            token.status = x.status
            token.winded = x.winded
            token.dragon = x.dragon
            if(token.status >0):
                gamespot = self.gameboard['gamespace'][player_info['spot']-1]
                gamespot.interact(token)

            if player_info['faction'] == fac1_name:
                x.interact(fac1)
                token.interact(fac1)
            else:
                x.interact(fac2)
                token.interact(fac2)
            p_hand = self.register(Hand())
            x.interact(p_hand)
            for card_val in player_info['cards']:
                card = self.register(Card(grave, card_val))
                p_hand.interact(card)
            player_info['object'] = x
            player_info['token'] = token
            player_info['gamespot'] = gamespot
            player_info['hand'] = p_hand

        self.whos_turn = snapshot[snapshot['whosturn']]['object']
    ############ ACTION TRAY ############
        cries = []
        not_cries = []
        try:
            impending = snapshot['imp']
        except:
            impending = []
        #impending = getattr(snapshot, 'imp', [])
        print '-'*60
        print impending
        print '-'*60
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
            #self.game_start = 0
        else:
            self.update_next_tray()


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


    def spawn(self, game_type=0, color_list=['red', 'blue', 'green', 'yellow']):
        self.game_id = random.randint(1000,9999)
        #check against other existing gamenums when we have files and stuff
        self.gameboard = {}
        self.log('Game Start')

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
    # There are always two
        fac1 = self.register(Faction('The Mecha-Sharks'))
        fac2 = self.register(Faction('The Robo-Jets'))
        fac1.link(fac2, 'rival')

    #############GAME TYPE################
    # num tokens (query for color)
    # teams
    # powers avail
    # DRAGON!?!?!
    # deck vars: cycles, extra_cards

        cycles = 0 
        extra_cards = 0 
        num_players = 2
        fac1_size = 1
        dragon = 0 # hp, cards, abils
        powers = 1
        if len(color_list) < num_players:
            color_list = ['red', 'blue', 'green', 'yellow']

        self.game_type = game_type
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

    ##############CARD GRAVEYARD############## 
        grave = self.register(GraveYard())
        self.gameboard['deadtoken'] = []
    ##############CARD DECK############## 
        deck = self.register(Deck(grave, cycles)) #cycles set above
        for i in range(1,6):
            for j in range(5+(extra_cards)): # extra_cards set above
                deck.interact(self.register(Card(grave, i)))
        deck.shuffle()

    ############PLAYERS##################
    ##############TOKENS#################
    #############HANDS###################
        skip_count = 0
        names = ['One', 'Two', 'Three', 'Four', 'Five']
        player_id_list = [0]
        for i in range(num_players):
            if i >= fac1_size:
                skip_count = 1
            rand_num = 0
            while rand_num in player_id_list:
                rand_num = random.randint(100,999)
            x = self.register(Player(self.game_id, rand_num))
            x.des = 'Player '+names[i]
            y = self.register(Token(color_list[i]))
            z = self.register(Hand())
            x.interact(y)
            x.interact(z)
            x.interact(self.gameboard['faction'][skip_count])
            y.interact(self.gameboard['faction'][skip_count])
            self.spaces()[-skip_count].interact(y) #hope they're still in order!
            for i in range(5):
                z.interact(deck)

    #############TURN ORDER##############
        self.turn_order= self.create_turn_order()
        self.whos_turn = self.turn_order[0]
        log_string = ''
        for i in self.turn_order:
            log_string += i.pretty_name()+' '
        self.log('Turn Order set: '+log_string)
    ############ ACTION TRAY ############
        self.next_tray = self.make_action_tray(self.whos_turn)

    #############DRAGON##################
    ###############TRAITOR###############
    ################POWERS###############

    #                TBI                # 
        
###########END CREATE GAME#############

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
            final_vote = random.choice([-1,1])
        elif final_vote > 0: 
            final_vote = 1
        else: final_vote = -1
        fac2_size = len(turn_prefs) - fac1_size
        #final_vote is -1 for fac1 or +1 for fac2
        fac_p_list = [0,0]
        fac_p_list[0] = self.inter_turn_order(turn_prefs[:fac1_size])
        if fac2_size == 1 and fac1_size > 1: #DRAGON
            turn_order = fac_p_list[0] + [fac1_size] # he always goes last
        else: # team sizes are equal
            turn_order = []
            fac_p_list[1] = [x + fac1_size for x in self.inter_turn_order(turn_prefs[fac1_size:])]
            for i in range(fac1_size):
                turn_order.append(fac_p_list[final_vote-1][i])
                turn_order.append(fac_p_list[final_vote][i])
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
        for token in self.gameboard['deadtoken']:
            self.gameboard['token'].append(token)
            token.interact(token.check('owned')[0].check()[0])
        self.gameboard['deadtoken'] = []
        for i in self.gameboard['tray']:
            i.destroy()
            self.deregister(i)
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
            enemy_dir = f2_token.closest_enemy()[1]
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

    def make_choice(self, choice, id_num):
        if id_num == self.next_tray.id_num and choice in self.next_tray.choice_ids:
            #a = self.next_tray.check('owner')[0]
            #actor = a.pretty_name()
            #self.log(actor+' took action '+choice)
            self.log(choice+':'+self.next_tray.resolve(choice))
            #b = a.check('owns')[0].check('at')
            #if b: ender =', ending on '+b[0].pretty_name()
            #else: ender = ' and died!'
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
            self.log(winner.pretty_name()+ ' wins the match.')
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




import game
from sys import argv
from printers import print_from_snapshot
from snapshots import random_gamestart_snapshot, file_snap, file_recov, player_snap_files, game_over_from_snap, player_snap_from_master
import robots  # robot_lootup_table LittleBobby


def robot_control(snapshot, table=0):
    if 'choices' in snapshot:
        controller = snapshot[snapshot['choices'][0]]['controller']
    else:
        controller = 'human'
    if controller != 'human' and not table:
        table = game.Game()
        table.spawn_from_snapshot(snapshot)
    while controller != 'human':
        print "CONTROLLER: ", controller
        if controller in robots.robot_lookup_table:
            robot_name = snapshot['choices'][0]
            robot_snap = player_snap_from_master(snapshot, robot_name)
            robot = robots.robot_lookup_table[controller]()
            robot_choice = robot.make_choice(robot_snap)
            print "%s CHOICE: %s"%(robot_name, robot_choice)
            table.make_choice(robot_choice)
            snapshot = table.master_snapshot()
            file_snap(snapshot)
            player_snap_files(snapshot)
            if 'choices' in snapshot:
                controller = snapshot[snapshot['choices'][0]]['controller']
            else:
                controller = 'human'
        else:
            print '\n+++++\n'+controller+'\n++++++\n'
            raise Exception # Bad Robot Type
    print "LAST CONTROLLER: ", controller
    return snapshot
        
   
   ###################   BEGIN SCRIPTING CONTROL  ####################
possible_choices =['r', 'a', 'd', 'b', 't', 'x', 'p', 'm', 'c', 's']
game_id = ''
player_id = None
choice = None
for arg in argv[1:]:
    if arg[0] == 'g':
        if game_id:
            print 'Bad arg:', arg
            raise Exception #Multiple GameID args
        else:
            id_split = arg.split('p')
            if len(id_split) == 2 and id_split[0][1:].isdigit() and id_split[1].isdigit():
                game_id, player_id = id_split
            elif len(id_split) == 1 and id_split[0][1:].isdigit():
                game_id = id_split[0]
            else:
                print 'Bad arg:', arg
                raise Exception # Mangled GameID arg
    if arg[0] in possible_choices:
        if choice:
            print 'Bad arg:', arg
            raise Exception # Multiple Choice args
        else:
            if len(arg) == 1 or arg[1:].isdigit() or (arg[0]=='m' and arg[2:].isdigit()):
                choice = arg
            else:
                print 'Bad arg:', arg
                raise Exception # Mangled Choice arg
if not game_id:
    game_id = 'g0'

if game_id == 'g10':
    game_type = 0
else:
    game_type = 1
snap2 = file_recov(game_id)
player_list = ['human']+['LittleBobby']*4
check = 0
if not snap2:
    snap2 = random_gamestart_snapshot(game_type, game_id, player_list)
    check = 1
snap2['game'] = snap2['game'][0], int(game_id[1:])  # update game_id in case
                                                    # files have split
if check: 
    player_snap_files(snap2)
    file_snap(snap2)

snap2 = robot_control(snap2)
if 'choices' in snap2:
    if choice:
        print 'CHOICE: ', choice
        table = game.Game()
        table.spawn_from_snapshot(snap2)
        table.make_choice(choice)
        snap2= table.master_snapshot()
        snap2 = robot_control(snap2, table)
#if player_id:
    #snap2 = file_recov(game_id+'p'+str(player_id))
    #if not snap2:  # can't find archive for that id, try public archive
        #snap2 = file_recov(game_id+'p0')
    #if not snap2:
        #raise Exception # No matching player and no public snapshot!
# OR now that player_snap can find names from IDs
if player_id:
    snap2 = player_snap_from_master(snap2, player_id)

print print_from_snapshot(snap2),

   ###################   END SCRIPTING CONTROL  ####################

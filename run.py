import random
from sys import argv
from game import do_things, assemble_game, file_recov, player_snap_from_master, complete_archive, robot_control
from printers import print_from_snapshot
import robots  # robot_lootup_table random_robots robot_control

   
   ###################   BEGIN SCRIPTING CONTROL  ####################
possible_choices =['r', 'a', 'd', 'b', 't', 'x', 'p', 'c', 's', 'i', 'f']
game_id = ''
player_id = None
choice = None
robot = ''
player_list = ['human']+robots.random_robots(4)
try:
    if argv[1] == 'robots':
        game_id = 'g2714'
        robot = "ON"
        player_list = robots.random_robots(4)
        argv = ['1']
except:
    pass
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

   ###################   END SCRIPTING CONTROL  ####################
        ############### IT HAS BEGUN ################
snap = file_recov(game_id)
check = 0
if not snap:
    snap = assemble_game(player_list, game_type, game_id)
    #snapshot = assemble_game(['LittleBobby','Roomba','Bender','Rockem','Sockem'], 6, 3)
    check = 1
snap['game'] = snap['game'][0], int(game_id[1:])  # update game_id in case
                                                    # files have split
if check: 
    complete_archive(snap)
elif 'choices' in snap and choice:
    snap= do_things(snap, choice)
    complete_archive(snap)

snap = robot_control(snap, robot)
if player_id:
    snap = player_snap_from_master(snap, player_id)

print print_from_snapshot(snap),
        ############## IT HAS ENDED #################




import random
from sys import argv
from game import do_things, assemble_game, player_snap_from_master
from printers import print_from_snapshot
from storage import file_recov, file_snap
import robots  # robot_lootup_table random_robots robot_control
import copy

   
   ###################   BEGIN SCRIPTING CONTROL  ####################
possible_choices =['r', 'a', 'd', 'b', 't', 'x', 'p', 'c', 's', 'i', 'f']
game_id = ''
player_id = None
choice = None
robot = ''
fac1 = []
fac2 = []
game_run = 1
try:
    test = argv[1]
except:
    test = ''
if test == 'robots':
    robot = 'ON'
    try:
        f1, f2 = int(argv[2]), int(argv[3])
    except:
        f1, f2 = 2,2
    if f2 > 2: f2 = 2
    elif f2 < 1: f2 = 1
    if f2 == 1:
        if f1 > 4: f1 = 4
        elif f1 < 1: f1 = 1
    else:
        f1 = 2
    game_id = 'g'+str(random.randint(100,999))
    print "Game created as ID#", game_id
    robot = "ON"
    robot_list = robots.random_robots(f1+f2)
    fac1 = robot_list[:f1]
    fac2 = robot_list[f1:]
    print fac1, fac2
    argv = ['1']
elif test == 'create':
    game_id = argv[2]
    if game_id[0] != 'g' or len(game_id) < 2 or not game_id[0:].isdigit():
        game_id = 'g'+str(random.randint(100,999))
        print "Game created as ID#", game_id
    i = 3
    while argv[i] != 'vs' and i < len(argv):
        fac1.append(argv[i])
        i += 1
    i += 1
    while i < len(argv):
        fac2.append(argv[i])
        i += 1
elif test == 'list':
    count = 0
    print ' '*2,
    for robot in robots.robot_lookup_table:
        print robot,
        if count > 1:
            count = 0
            print '\n'+' '*2,
        else:
            print ' '*(20-len(robot)),
            count += 1
    game_run = 0
else:
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

   ###################   END SCRIPTING CONTROL  ####################
        ############### IT HAS BEGUN ################
if game_run:
    snap = file_recov(game_id)
    check = 0
    to_archive = []
    if not snap:
        snap = assemble_game(fac1, fac2, game_id)
        check = 1
    snap['game'] = snap['game'][0], int(game_id[1:])  # update game_id in case
                                                        # files have split
    if check: 
        to_archive.append(copy.deepcopy(snap))
    elif 'choices' in snap and choice:
        snap= do_things(snap, choice)
        to_archive.append(copy.deepcopy(snap))

    to_archive.extend(robots.robot_control(snap, robot))
    if to_archive:
        file_snap(to_archive)
        snap = to_archive[-1]
    if player_id:
        snap = player_snap_from_master(snap, player_id)

    print print_from_snapshot(snap),
        ############## IT HAS ENDED #################




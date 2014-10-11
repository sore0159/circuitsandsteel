#!/usr/bin/env python
import random
from sys import argv
from game import do_things, assemble_game 
from interfaces import print_from_snapshot, player_snap_from_master, file_recov, file_snap
import robots  # robot_lootup_table random_robots robot_control
import copy

   
   ###################   BEGIN SCRIPTING CONTROL  ####################
possible_choices =['r', 'a', 'd', 'b', 't', 'x', 'p', 'c', 's', 'i', 'f']
game_id = ''
player_id = 0
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
    robot = "ON"
    robot_list = robots.random_robots(f1+f2)
    fac1 = robot_list[:f1]
    fac2 = robot_list[f1:]
    argv = ['1']
elif test == 'create':
    try:
        g_id = argv[2]
    except:
        g_id = 0
        i = 4  # no robot names given
    if g_id:
        if g_id[0] == 'g' and g_id[1:].isdigit():
            game_id = g_id
            i=3 # skip over that arg while making robots
        else:
            i=2 # whoops that was a robot name!
            game_id = 'g'+str(random.randint(100,999))
    else:
        game_id = 'g'+str(random.randint(100,999))
    while i < len(argv) and argv[i] != 'vs':
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
                if len(id_split) == 2 and id_split[0][1:].isdigit() and (id_split[1].isdigit() or id_split[1] == 'm'):
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
    if test in ['create', 'robots']:
        snap = assemble_game(fac1, fac2, game_id)
        check = 1
    elif not snap:
        raise Exception # No such game ID found!
    snap['game'] = snap['game'][0], int(game_id[1:])  # update game_id in case
                                                        # files have split
    player_list = []
    long_name_str = ''
    for faction in ['leftfaction', 'rightfaction']:
        for player in snap[faction]['players']:
            player_list.append(player)
    tic = 0
    for player in player_list:
        name_str = '     '+player+": "+str(snap[player]['id_num'])
        long_name_str +=  name_str+' '*(30-len(name_str))
        if tic % 2: long_name_str += '\n'
        tic += 1

    if check: 
        to_archive.append(copy.deepcopy(snap))
    elif 'choices' in snap and choice:
        if player_id in ['m', str(snap[snap['choices'][0]]['id_num'])]:
            snap= do_things(snap, choice)
            to_archive.append(copy.deepcopy(snap))
        else:
            print print_from_snapshot(snap, '0'),
            raise Exception # Player ID does not match active player!

    to_archive.extend(robots.robot_control(snap, robot))
    if to_archive:
        file_snap(to_archive)
        snap = to_archive[-1]

if test == 'create':
    print print_from_snapshot(snap, 0),
    print "+"*70
    print "Game stored as ID#", game_id
elif test == 'robots':
    print print_from_snapshot(snap),
    print "+"*70
    print "Game stored as ID#", game_id
else:
    print print_from_snapshot(snap, player_id),


        ############## IT HAS ENDED #################




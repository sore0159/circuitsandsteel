import game
from sys import argv
import cPickle as pickle
from printers import print_from_snapshot


 ################  START FILE PICKLING  #################
def file_snap(snapshot, game_id='g0', player_id=-1):
    if player_id != -1: 
        player_id = str(player_id)
        if player_id.isdigit(): player_id = 'p'+player_id
    else:
        player_id = ''
    game_id = str(game_id)
    if game_id.isdigit() : game_id = 'g'+game_id
    archive_file = 'data/'+game_id+player_id+'_archive.pkl'
    print "Reading File: " + archive_file
    try:
        check2_file = open(archive_file, 'rb')
        archive_list = pickle.load(check2_file)
        check2_file.close()
        print "File Read!"
    except IOError:
        archive_list = []
    archive_list.append(snapshot)
    print "Writing File: " + archive_file
    log_file = open(archive_file, 'wb')
    pickle.dump(archive_list, log_file, -1)
    log_file.close()

def file_recov(game_id='g0'):
    archive_file = 'data/'+str(game_id)+'_archive.pkl'
    print "Reading File: " + archive_file
    try:
        snap_file = open(archive_file, 'rb')
        snapshot_list = pickle.load(snap_file)
        snapshot = snapshot_list[-1]
        print "File Read!"
    except IOError: snapshot = 0
    return snapshot

def player_snap_files(game):
    game_id = 'g'+str(game.game_id)
    for player in game.gameboard['player']:
        player_id = player.id_num
        snapshot = game.snapshot(player_id)
        file_snap(snapshot, game_id, player_id)
    snapshot = game.snapshot()
    file_snap(snapshot, game_id, 'p0')
 ################  END FILE PICKLING  #################
    
possible_choices =['r', 'a', 'd', 'b', 't', 'x', 'p', 'm', 'c', 's']
try:
    choice = argv[2]
except:
    choice = 0
try:
    game_id = argv[1]
except:
    game_id = 'g0'
if game_id[0] != 'g' and game_id[0] in possible_choices:
    choice = game_id
    game_id = 'g0'

game = game.Game()
game_type = 1
snap2 = file_recov(game_id)
check = 0
if not snap2:
    snap2 = game.random_gamestart_snapshot(game_type)
    file_snap(snap2, game_id)
    check = 1
game.spawn_from_snapshot(snap2)
if check: player_snap_files(game)


if not game.is_game_over():
    if choice:
        tray_id = game.next_tray.id_num # can eliminate this step
        game.make_choice(choice, tray_id)
        snap2= game.master_snapshot()
        file_snap(snap2, game_id)
        player_snap_files(game)
print print_from_snapshot(snap2),


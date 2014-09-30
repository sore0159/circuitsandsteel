import game
from sys import argv
import cPickle as pickle
from printers import ascii_print, query_option


def file_snap(snapshot, game_id=0):
    game_id = 'data/'+str(game_id)
    try:
        check_file = open(game_id+'latest.pkl', 'rb')
        existing = check_file.readlines()
    except: existing = 0
    if existing:
        check_file.seek(0)
        last_snap = pickle.load(check_file)
        try:
            check2_file = open(game_id+'archive.pkl', 'rb')
            archive_list = pickle.load(check2_file)
            check2_file.close()
        except:
            archive_list = []
        archive_list.append(last_snap)
        log_file = open(game_id+'archive.pkl', 'wb')
        pickle.dump(archive_list, log_file)
        log_file.close()
        check_file.close()
    snap_file = open(game_id+'latest.pkl', 'wb')
    pickle.dump(snapshot, snap_file, -1)
    snap_file.close()

def file_recov(game_id=0):
    game_id = 'data/'+str(game_id)
    try:
        snap_file = open(game_id+'latest.pkl', 'rb')
        snapshot = pickle.load(snap_file)
    except: snapshot = 0
    return snapshot

def read_log(game, length=3):
    for i in range(length):
        try:
            print game.read_log()[-length+i]
        except:
            pass
    

try:
    choice = argv[2]
except:
    choice = 0
try:
    game_id = argv[1]
except:
    game_id = 0
game = game.Game()
game_type = 1
snap2 = file_recov(game_id)
if not snap2:
    snap2 = game.random_gamestart_snapshot(game_type)
    file_snap(snap2, game_id)
game.spawn_from_snapshot(snap2)


if not game.is_game_over():
    if choice:
        tray_id = game.next_tray.id_num
        game.make_choice(choice, tray_id)
        file_snap(game.master_snapshot(), game_id)
ascii_print(game)
read_log(game, 4)
if not game.is_game_over():
    query_option(game, 1)


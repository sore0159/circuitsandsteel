import game
from sys import argv
from printers import print_from_snapshot
from snapshots import random_gamestart_snapshot, file_snap, file_recov, player_snap_files, game_over_from_snap
    
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

if game_id == 'g10':
    game_type = 0
else:
    game_type = 1
snap2 = file_recov(game_id)
check = 0
if not snap2:
    snap2 = random_gamestart_snapshot(game_type, game_id)
    file_snap(snap2, game_id)
    check = 1
if check: player_snap_files(game)


if not game_over_from_snap(snap2):
    if choice:
        game = game.Game()
        game.spawn_from_snapshot(snap2)
        tray_id = game.next_tray.id_num # can eliminate this step
        game.make_choice(choice, tray_id)
        snap2= game.master_snapshot()
        file_snap(snap2, game_id)
        player_snap_files(game)
print print_from_snapshot(snap2),


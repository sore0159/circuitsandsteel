#!/usr/bin/env python

import cPickle as pickle
import pprint
from interfaces import print_from_snapshot
from sys import argv

target_file = argv[1]
isolate_file = 'isolate.pkl'
try:
    flag = argv[2]
except:
    flag = 'a'
if flag and flag not in ['a', 'd']:
    flag = 'a'
print 'Reading File '+target_file
target = open(target_file, 'rb')
obj = pickle.load(target)
num_arcs = len(obj)
pick = str(num_arcs)
while pick != 'q':
    if pick == 'n' and num < num_arcs-1:
        num += 1
    elif pick == 'b' and num > 0:
        num += -1
    elif pick == 'd':
        flag = 'd'
    elif pick == 'a':
        flag = 'a'
    elif pick == 'f':
        num = 0
    elif pick == 'l':
        num = num_arcs-1
    elif pick == 'i':
        print '+'*60+'\n'+"Isolating snapshot to file "+isolate_file+'+'*60+'\n'
        iso_file = open(isolate_file, 'wb')
        pickle.dump([obj[num]], iso_file, -1)
    elif pick.isdigit() and int(pick)-1 in range(num_arcs): num = int(pick)-1
    else: print '+'*60+'\n'+"Invalid Choice\n"+'+'*60+'\n'
    print "Reading Snapshot %d out of %d" %(num+1, num_arcs)
    if flag == 'a': print print_from_snapshot( obj[num])
    if flag == 'd': pprint.pprint( obj[num])
    pick = ''
    while pick not in ['i', 'l', 'n', 'a', 'd', 'b', 'f', 'q'] and not pick.isdigit():
        pick = raw_input('[(i)solate, (a)scii, (d)ata, (f)irst, (l)ast, (1)-(%d), (b)ack (n)ext, (q)uit]:?' % num_arcs)

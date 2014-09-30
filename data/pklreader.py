#!/usr/bin/env python

import cPickle as pickle
import pprint
from sys import argv

target_file = argv[1]
try:
    num = int(argv[2])
except:
    num = 'a'
print 'Reading File '+target_file
target = open(target_file, 'rb')
try:
    while True:
        obj = pickle.load(target)
        if num != 'a':
            pprint.pprint( obj[num])
        else:
            pprint.pprint( obj)
except:
    pass


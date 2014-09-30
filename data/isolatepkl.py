#!/usr/bin/env python

import cPickle as pickle
from sys import argv

target_file = argv[1]
num = int(argv[2])
print 'Reading File '+target_file
print 'Isolating element %s to file isolate.pkl' % num
target = open(target_file, 'rb')
isolate_tar = open('isolate.pkl', 'wb')
obj_list =  pickle.load(target)
pickle.dump(obj_list[num], isolate_tar, -1)




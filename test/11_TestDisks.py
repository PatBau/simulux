#!/usr/bin/env python
import unittest
from simulux.exceptions import SimuluxDiskException
from simulux.disks import Disks


class DisksTest(unittest.TestCase):
    
    
    def test_shorten_path_top_folder(self):
        disks = Disks()
        test_paths_rel = [ '../', 'a/../../a', 'b/../../b',\
        'a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p/q/r/s/t/u/v/w/x/y/z/../../../../../../../../../../../../../../../../../../../../../../../../../../../../' ]
        
        test_paths_abs = [ '/../', '/a/../../a/..'\
        '/a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p/q/r/s/t/u/v/w/x/y/z/../../../../../../../../../../../../../../../../../../../../../../../../../../../../' ]
        
        #test 1 rel
        for path in test_paths_rel:
            with self.assertRaises(SimuluxDiskException):
                disks.shorten_path(path)
        #test 2 abs
        for path in test_paths_abs:
            self.assertEqual(disks.shorten_path(path), "/")
        
        
    def test_shorten_path_misc(self):
        disks = Disks()
        test_paths_rel = [ './', '', 'a/b/c/d./././', 'a/b/c/d././../', 'a/b/c', 'a/b/../c', 'a/b/./c' ]
        test_paths_abs = [ '/', '', '/./././', '/a/b/././././', '/a/b/c', '/a/b/../c', '/a/b/./c', '/./', '/./././', '/a/../../a/', '/b/../../b' ]
        
        correct_paths_rel = [ '.', '', 'a/b/c/d.', 'a/b/c', 'a/b/c', 'a/c', 'a/b/c']
        correct_paths_abs = [ '/', '', '/', '/a/b', '/a/b/c', '/a/c', '/a/b/c', '/', '/', '/a', '/b' ]
        
        #test 1 rel
        for i in range(0,len(test_paths_rel)):
            self.assertEqual(disks.shorten_path(test_paths_rel[i]), correct_paths_rel[i])
        #test 2 abs
        for i in range(0,len(test_paths_abs)):
            self.assertEqual(disks.shorten_path(test_paths_abs[i]), correct_paths_abs[i])
        
if __name__ == '__main__':
    unittest.main()

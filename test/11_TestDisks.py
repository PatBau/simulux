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
        test_paths_abs = [ '/', '/./././', '/a/b/././././', '/a/b/c', '/a/b/../c', '/a/b/./c', '/./', '/./././', '/a/../../a/', '/b/../../b', '/t/' ]
        
        
        correct_paths_rel = [ '.', '', 'a/b/c/d.', 'a/b/c', 'a/b/c', 'a/c', 'a/b/c']
        correct_paths_abs = [ '/', '/', '/a/b', '/a/b/c', '/a/c', '/a/b/c', '/', '/', '/a', '/b', '/t' ]
        
        #test 1
        print("test_shorten_path_misc.1")
        for i in range(0,len(test_paths_abs)):
            self.assertEqual(disks.shorten_path(test_paths_abs[i]), correct_paths_abs[i])
            
    def test_make_absolute(self):
        disks = Disks()
        
        test_paths_rel = [ '', './', 'a/b', '../a/b']
        test_paths_abs = [ '/a/b', '/../a/b']
        correct_paths = ['/abs/path', '/abs/path/./', '/abs/path/a/b', '/abs/path/../a/b']
        
        test_work_dir_none = ''
        test_work_dir_rel = 'rel/path'
        test_work_dir_abs = '/abs/path'
        
        #test 1
        print("test_make_absolute.1")
        for path in test_paths_rel:
            with self.assertRaises(SimuluxDiskException):
                disks._make_absolute(path, test_work_dir_none)
                disks._make_absolute(path, test_work_dir_rel)
                
        #test 2
        print("test_make_absolute.2")
        for path in test_paths_abs:
            self.assertEqual(disks._make_absolute(path, test_work_dir_none), path)
            self.assertEqual(disks._make_absolute(path, test_work_dir_rel), path)
            
        #test 3
        print("test_make_absolute.3")
        for i in range(0,len(test_paths_abs)):
            self.assertEqual(disks._make_absolute(test_paths_rel[i], test_work_dir_abs), correct_paths[i])
        
        
        
if __name__ == '__main__':
    unittest.main()

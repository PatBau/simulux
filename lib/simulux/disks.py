import os
from simulux.utils import load_json
from simulux.constants import DIST_DEFAULTS_PATH, FILES_DEFAULT_PATH
from simulux.exceptions import SimuluxDiskException

DEFAULT_LAYOUT = os.path.join(DIST_DEFAULTS_PATH, 'disks_layout.json')

def load_layout(layout_file=None):
    '''
    Load the layout from the config file (structured and hierarchical)
    '''
    if not layout_file:
        layout_file = DEFAULT_LAYOUT
    return load_json(layout_file)

'''
Disk object 

Defines the operaton related to the Disk, including:
- disk space (disk / partition / folders)
- io operation 

'''

class Disks(object):
    """Define a Disks object"""
    def __init__(self, conf=None):
        super(Disks, self).__init__()
        
        self.disks = {}
        self.partitions = {}
        self.files = {}
        self.scenario_name = None
        
        # Add default layout
        self.add_layout()
        
        # Add scenario specific disks
        if conf:
            self.disks.update(conf.get('disks', {}))
            self.partitions.update(conf.get('partitions', {}))
            self.scenario_name = conf.get('scenario_name', None)
            # Need to process files for more conveniency
            files = conf.get('files', {})
            self._process_mounts(files)
        

    def add_layout(self, layout_file=None):
        '''
        Add an extra disk layout definition; override any existing disk, partition
        and file
        '''
        layout = load_layout(layout_file)

        self.disks.update(layout.get('disks', {}))
        self.partitions.update(layout.get('partitions', {}))

        # Need to process files for more conveniency
        files = layout.get('files', {})
        self._process_mounts(files)

    def _process_mounts(self, files={}):
        '''
        Need to process the files per mount point, and make it a flat structure 
        to simplify search later on.
        '''
        for root, content in files.iteritems():
            '''
            root: base dir that is defined as a mount point
            content: object describing the files / folders within that root
            '''
            # mount = True will prevent further recursion and will propagate size
            #       to the partition instead of parent folder
            # TODO: add the partition info here?
            partitions = [ part for name, part in self.partitions.iteritems() if 
                        part.get('mount') == root ]
            if len(partitions) == 1:
                partition = partitions[0]
            else:
                print "Associated partition with mount point %s is missing" % (root,)
                partition = {}
            # Cheating ownership (for now)
            result = {
                'mount': True,
                'size': partition.get('used', 0),
                'owner': 'root',
                'group': 'root',
                'mode': 755
            }
            self.files.update({root: result})
            self._process_files(root, content)

    def _process_files(self, base='/', files={}):
        '''
        Process the files, inheriting from the base path
        '''
        for name, details in files.iteritems():
            root = os.path.join(base, name)
            data = details.copy()
            if data.get('filetype') == 'folder':
                # Sub files are in `data.content`
                self._process_files(root, data.get('content', {}))
                # For the folder itself we don't need the subfiles in content
                del data['content']
            self.files.update({root: data})
    
    def shorten_path(self, path):
        # special case
        if not path:
            return ''
        
        new_path = list()
        path_exploded = path.split('/')
        # delete all empty string which are caused by wrong path syntax or "/" at end/beginning
        while '' in path_exploded:
            path_exploded.remove('')
        
        is_absolute = False
        if path.startswith('/'):
            is_absolute = True

        for elem in path_exploded:
            if elem == '..':
                if len(new_path) > 0:
                    new_path.pop()
                    continue
                # ../ over top-directory of path
                # check if path is relative or absolute
                # relative: work with working dir
                # absolute: do nothing, "/" is top-folder
                if not is_absolute:
                    raise SimuluxDiskException("Can not go higher then top-level in a relative path")
                # absolute, do nothing
                # "/" is the top-folder
            elif elem == '.':
                continue
            else:
                new_path.append(elem)

        if is_absolute:        
            return '/' + '/'.join(new_path)
        ret = '/'.join(new_path)
        if ret == '':
            # this case occurs, when origin path is "./"
            return '.'
        return ret
        
    #def shorten_path(self, path, working_dir=None):
        #'''
        #Returns shorten paths like /x with input: /x/z.././
        #'''
        ## special cases
        #if not path:
            #if not working_dir:
                #raise SimuluxDiskException("path is null")
            #return working_dir
        #if working_dir:
            #if not working_dir.startswith('/'):
                #raise SimuluxDiskException("Working directory must be absolute")
            #if path == '' or path == '/':
                #return working_dir
        #if path == '':
            #return ''
            
        ##need this to differentiate return value
        #absolute =  True if path.startswith('/') else False
        
        #if working_dir and not absolute:
            ##glue working_dir and relative path together to one absolute path
            #if working_dir.endswith('/'):
                #path = working_dir + path 
            #else:
                #path = working_dir + '/' + path  
                 
        #new_path = list()
        #array = path.split('/')
        ## delete all empty string which are caused by wrong path syntax or "/" at end/beginning
        #while '' in array:
            #array.remove('')

        #for elem in array:
            #if elem == '..':
                #if len(new_path) > 0:
                    #new_path.pop()
                    #continue
                #if not working_dir:
                    #raise SimuluxDiskException("Can not go higher than a top level dir in a relative path (no work_dir given)")
            #elif elem == '.':
                #continue
            #else:
                #new_path.append(elem)
        #if working_dir or absolute:
            #ret = '/' + '/'.join(new_path)
        #else:
            #ret = '/'.join(new_path)
        #if ret == '' and not absolute:
            ##if the new_path is an empty string this is caused by the original string: './', '././', ...
            #return '.'
        #return ret
    
    def exists(self, path, working_dir=None):
        '''
        Return if a path exists in the tree
        '''
        path = self.shorten_path(path, working_dir)

        if path in self.files:
            return True
        return False

    def is_folder(self, path, working_dir=None):
        '''
        Return whether a path is a folder
        '''
        path = self.shorten_path(path, working_dir)
            
        if not self.exists(path, working_dir):
            return False
        details = self.get_details(path)
        if details.get('mount') == True:
            return True
        if details.get('filetype') == 'folder':
            return True
        return False
        
    def is_file(self, path, working_dir=None):
        '''
        Return whether a path is a file
        '''
        path = self.shorten_path(path, working_dir)
             
        if not self.exists(path, working_dir):
            return False
        details = self.get_details(path)
        if details.get('filetype') == 'file':
            return True
        return False

    def get_childrens_path(self, path):
        '''
        Return an array of path that are direct childrens of the provided path
        '''
        childrens = [ child for child, data in self.files.iteritems() if 
                        child.startswith(path) and os.path.dirname(child) == path 
                        and child != path ]
        return childrens

    def get_parent_path(self, path):
        '''
        Return an array of path that are direct childrens of the provided path
        '''
        return os.path.dirname(path)

    def get_details(self, path=None):
        '''
        Returns the details of a specific path
        '''
        details = self.files.get(path)
        if not details:
            print '%s: No such file or directory' % (path,)
            return {}        
        return details

    def add_file(self, path, filetype='file', size=0, owner='root', group='root', mode=755):
        '''
        Add file/folder to the layout, updating sizes if needed
        '''
        # It should not exist yet
        if self.files.get(path):
            print '%s: file or directory already exists' % (path,)
            return False
        details = {
            'size': int(size),
            'owner': owner,
            'group': group,
            'filetype': filetype,
            'mode': mode
        }
        self.files.update({path: details})
        if int(size) != 0:
            self._update_parent_size(path, int(size))
        return True

    def update_file(self, path, **kwargs):
        '''
        Update existing file; can change only size, owner, group and mode. 
        Can not update filetype (file/folder)
        '''
        details = self.get_details(path)
        if not details:
            return False
        for k, v in kwargs.iteritems():
            if k not in ['size', 'owner', 'group', 'mode']:
                print 'Invalid key: %s' % (k)
                return False
        for k, v in kwargs.iteritems():
            if k == 'size':
                # Need to update the size
                prev_size = details.get('size')
                new_size = int(v)
                self._update_parent_size(path, new_size - prev_size)
                details.update({k: new_size})
            else:
                details.update({k: v})
        self.files.update({path: details})

    def remove_file(self, path, recursive=False):
        '''
        Remove file/folder, releasing used space.
        Can not remove if; not existing or mount point
        '''
        # Handle recursivity first...
        if recursive:
            childrens = self.get_childrens_path(path)
            for child_path in childrens:
                success = self.remove_file(child_path, recursive=True)
                if not success:
                    return False

        details = self.get_details(path)
        if not details:
            return False
        size = details.get('size', 0)
        if details.get('mount') == True:
            print "rm: cannot remove `%s': Device or resource busy" % (path,)
            return False
        if details.get('filetype') == 'folder' and not recursive:
            print "rm: cannot remove `%s': Is a directory" % (path,)
            return False
        if size == 0:
            del self.files[path]
            return True
        self._update_parent_size(path, -size)
        del self.files[path]
        return True

    def _update_parent_size(self, path, size):
        '''
        Update the size recusively until the 'mount'
        '''
        # We want to manipulate the parent of the provided path
        parent_path = self.get_parent_path(path)

        details = self.get_details(parent_path)
        new_size = details.get('size') + size
        details.update({'size': new_size})
        self.files.update({parent_path: details})
        # If mount level file / folder, exit
        if details.get('mount') == True:
            return
        # Else recurse to the parent
        self._update_parent_size(parent_path, size)
    
    def get_file_content(self, filename, working_dir=None):
        '''
        Opens a file if it exists
        '''
        
        # check if the file exists etc.
        filename = self.shorten_path(filename, working_dir)
        if not self.is_file(filename, working_dir):
            return None
        details = self.get_details(filename)
        real_file = details.get('real_filename', None)
        if not real_file:
            return None
        real_path = os.path.join(FILES_DEFAULT_PATH, real_file)  if not self.scenario_name \
        else os.path.join(FILES_DEFAULT_PATH, self.scenario_name, real_file)
        
        if not os.path.isfile( real_path ):
            return None
            
        #open file and return content
        
        content = ''
        with open( real_path ) as f:
            content = f.readlines()
        return content

import os
import json

DEFAULT_LAYOUT = 'default_layout.json'

def load_layout(layout_file=None):
    '''
    Load the layout from the config file (structured and hierarchical)
    '''
    if not layout_file:
        layout_file = DEFAULT_LAYOUT
    try:
        content = json.loads(open(layout_file).read())
    except Exception as e:
        print 'Error loading disk layout: %s' % (e,)
        content = {}
    return content

'''
Disk object 

Defines the operaton related to the Disk, including:
- disk space (disk / partition / folders)
- io operation 

'''

class Disks(object):
    """Define a Disks object"""
    def __init__(self):
        super(Disks, self).__init__()
        # Set the fs layout
        self.disks = {}
        self.partitions = {}
        self.files = {}
        # Add default layout
        self.add_layout()

    def add_layout(self, layout_file):
        '''
        Add an extra disk layout definition; override any existing disk, partition
        and file
        '''
        layout = load_layout()

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
            else
                print "Associated partition with mount point %s is missing" % (root,)
                partition = {}
            # Cheating ownership (for now)
            result = {
                'mount': True
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

    def get_childrens_path(self, path):
        '''
        Return an array of path that are direct childrens of the provided path
        '''
        childrens = [ child for child, data in self.files.iteritems() if 
                        child.startswith(path) and os.path.dirname(child) == path ]
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
                details.update({k, new_size})
            else:
                details.update({k, v})
        self.files.update({path: details})

    def remove_file(self, path):
        '''
        Remove file/folder, releasing used space.
        Can not remove if; not existing or mount point
        '''
        details = self.get_details(path)
        if not details:
            return False
        size = details.get('size', 0)
        if details.get('mount') == True:
            print '%s: is a mount point; it can not be removed' % (path,)
            return False
        if size == 0:
            del self.files[path]
            return True
        self._update_parent_size(path, size)
        del self.files[path]
        return True

    def _update_parent_size(self, path, size):
        '''
        Update the size recusively until the 'mount'
        '''
        # We want to manipulate the parent of the provided path
        parent_path = get_parent_path(path)

        details = self.get_details(parent_path)
        new_size = details.get('size') + size
        details.update({'size': new_size})
        self.files.update({parent_path: details})
        # If mount level file / folder, exit
        if details.get('mount') == True:
            return
        # Else recurse to the parent
        self._update_parent_size(parent_path, size)
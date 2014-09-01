import json
import os

def load_json(filename):
    '''
    Load json file
    '''
    if not os.path.exists(filename):
        print "File %s does not exist" % (filename)
        return False
    try:
        content = json.loads(open(filename).read())
    except Exception as e:
        print 'Error loading JSON file %s: %s' % (filename, e,)
        content = {}
    return content

def load_layout(default_layout, layout_file=None):
    '''
    Load the layout from the config file (structured and hierarchical)
    '''
    if not layout_file:
        layout_file = default_layout
    return load_json(layout_file)


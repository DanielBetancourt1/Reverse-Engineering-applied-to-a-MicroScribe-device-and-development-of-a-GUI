
#@author: Juan Daniel Isaza.
import sys
filename = 'requirements.txt'

## - If you are using a proxy you must use: 
#    main(['install', '--proxy=user:password@proxy:port', package])

def install(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:

        from pip._internal import main
        main(['install', package])

f = open(filename, "r" )

for line in f:
    pos = line.rfind('=')-1
    name = line[0:pos]
    
    if not name in sys.modules:
        print('Required module', name)
        install(line)  # Install in the required version.
    else:
        print('Available module', name)
            
print('Attention: Some available modules may have a non-compatible version')
f.close
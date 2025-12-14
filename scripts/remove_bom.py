import os
files=['app/ui/views/sidebar.py']
for fn in files:
    b=open(fn,'rb').read()
    if b.startswith(b'\xef\xbb\xbf'):
        print('Removing BOM from', fn)
        open(fn,'wb').write(b[3:])
    else:
        print('No BOM in', fn)

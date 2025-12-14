fn='app/ui/views/sidebar.py'
s=open(fn,'r',encoding='utf-8').read()
if '\\"' in s:
    s2=s.replace('\\"','"')
    open(fn,'w',encoding='utf-8').write(s2)
    print('Rewrote',fn)
else:
    print('No escaped quotes found')

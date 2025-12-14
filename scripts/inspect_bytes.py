files = [
    'app/integrations/google_calendar.py',
    'app/ui/views/calendar_panel.py',
    'app/ui/views/kanban.py',
    'app/ui/views/sidebar.py',
]
for fn in files:
    try:
        b = open(fn,'rb').read()
    except Exception as e:
        print(fn, 'ERROR', e)
        continue
    print('\n====', fn, '====')
    print('len=', len(b))
    print(repr(b[:128]))
    print('\nfirst 6 lines:')
    s = b.decode('utf-8', errors='replace')
    for i,l in enumerate(s.splitlines()[:6],1):
        print(f'{i:2}: {l!r}')

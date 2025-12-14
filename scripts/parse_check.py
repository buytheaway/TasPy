import ast
files = [
    'app/integrations/google_calendar.py',
    'app/ui/views/calendar_panel.py',
    'app/ui/views/kanban.py',
    'app/ui/views/sidebar.py',
]
for fn in files:
    print('\n----', fn)
    s=open(fn,'r',encoding='utf-8').read()
    try:
        ast.parse(s)
        print('OK')
    except SyntaxError as e:
        print('SyntaxError:', e)
        lines=s.splitlines()
        ln=e.lineno-1
        for i in range(max(0,ln-3), min(len(lines), ln+3)):
            print(f"{i+1:4}: {lines[i]!r}")

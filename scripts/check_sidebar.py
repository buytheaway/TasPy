import ast
s=open('app/ui/views/sidebar.py','r',encoding='utf-8').read()
try:
    ast.parse(s)
    print('PARSE OK')
except SyntaxError as e:
    print('SyntaxError:', e)
    lines=s.splitlines()
    ln=e.lineno-1
    for i in range(max(0,ln-3), min(len(lines), ln+3)):
        print(f"{i+1:4}: {lines[i]!r}")

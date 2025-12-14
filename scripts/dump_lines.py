fn='app/ui/views/sidebar.py'
s=open(fn,'rb').read()
print('bytes repr start 0..120:')
print(repr(s[:120]))
text=s.decode('utf-8','replace')
lines=text.splitlines()
for i in range(1,41):
    print(f"{i:3}: {repr(lines[i-1])}")

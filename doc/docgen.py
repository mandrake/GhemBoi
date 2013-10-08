from jinja2 import Environment, FileSystemLoader
import json

env = Environment(loader = FileSystemLoader('./templates'))

def with_file(fun, fname, mode, *params):
    f = open(fname, mode)
    x = fun(*map(lambda x: f if x == '%' else x, params))
    f.close()
    return x

j = with_file(json.load, '../src/opcodes/z80gb.json', 'r', '%')

t = env.get_template('opcodes-table.html')
f = open('opcodes-table.html', 'w')
f.write(t.render(prefix = '', opcodes = j).encode('utf-8'))
f.close()

t = env.get_template('opcodes-list.html')
f = open('opcodes-list.html', 'w')
f.write(t.render(prefix = '', opcodes = j).encode('utf-8'))
f.close()

t = env.get_template('instructions/nop.html')
f = open('nop.html', 'w')
f.write(t.render().encode('utf-8'))
f.close()
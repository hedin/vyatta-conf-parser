# coding:utf-8
import re
import sys
from collections import defaultdict

if sys.version < '3':
    def u(x):
        return x.decode('utf-8')
else:
    unicode = str

    def u(x):
        return x

rxh = re.compile(r'^([\w\-]+) \{$', re.UNICODE)
rxl = re.compile(r'^([\w\-]+) ([\w\-\"\./]+) \{$', re.UNICODE)
rxv = re.compile(r'^([\w\-]+) ([\w\-\"\.,/:@\*»« ]+)$', re.UNICODE)
rxu = re.compile(r'^([\w\-]+)$', re.UNICODE)


class ParserException(Exception):
    pass


def tree():
    return defaultdict(tree)


def update_tree(config, path, val):
    t = config
    for n, i in enumerate(path):
        t = t[list(i.keys())[0]]
    if isinstance(t, dict):
        if isinstance(val, dict):
            if list(val.keys())[0] not in list(t.keys()):
                t.update(val)
            elif isinstance(t[list(val.keys())[0]], unicode):
                t.update({list(val.keys())[0]: [t[list(val.keys())[0]], list(val.values())[0]]})
            elif isinstance(t[list(val.keys())[0]], list):
                t.update({list(val.keys())[0]: t[list(val.keys())[0]] + list(val.values())})
        else:
            t.update({val: {}})
    elif isinstance(t, list):
        t.append(val)
    else:
        t = val
    return config


def parse_node(config, raw, headers=None, i=0):
    if not headers:
        headers = []

    try:
        line = raw[i]
        line = line.strip()
        if not line:
            return config
    except IndexError:
        return config

    if rxh.match(line):
        h = rxh.match(line).groups()[0]
        if headers:
            update_tree(config, headers, {h: {}})
        headers.append({h: 'd'})

    elif rxl.match(line):
        h, n = rxl.match(line).groups()
        update_tree(config, headers, {h: {}})
        headers.append({h: 'l'})
        update_tree(config, headers, {n: {}})
        headers.append({n: 'd'})

    elif rxv.match(line):
        k, v = rxv.match(line).groups()
        update_tree(config, headers, {k: v})
    elif rxu.match(line):
        kv = rxu.match(line).group()
        update_tree(config, headers, {kv: kv})

    elif line == '}' and headers:
        hq = [list(h.values())[0] for h in headers]
        headers.pop()
        if len(hq) > 1 and hq[-2:] == ['l', 'd']:
            headers.pop()

    else:
        raise ParserException('Parse error: "%s", Line: %d' % (line, i))

    parse_node(config, raw, headers, i + 1)


def parse_conf(string):
    if string:
        string = u(string).split('\n')
        c = tree()
        parse_node(c, string)
        return c
    raise ParserException('Empty config passed')

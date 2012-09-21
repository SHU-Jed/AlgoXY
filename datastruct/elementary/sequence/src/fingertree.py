#!usr/bin/python

import random

# As there is no fold-right in python
def foldR(f, xs, z):
    for x in reversed(xs):
        z = f(x, z)
    return z

# definition
class Node:
    def __init__(self, s, xs):
        self.size = s
        self.children = xs

    def str(self):
        if self.size == 1:
            return ", ".join([str(x) for x in self.children])
        else:
            return "(" + ", ".join([x.str() for x in self.children]) + ")"

class Tree:
    def __init__(self, s, f, m, r):
        self.size = s
        self.front = f
        self.rear = r
        self.mid = m

    def empty(self):
        return self.size == 0

    def str(self):
        if self.empty():
            return "."
        else:
            return "{" + ns2str(self.front) + " " +  tr2str(self.mid) + " "+ ns2str(self.rear) + "}"

# Auxiliary functions for debugging

def ns2str(ns):
    return "[" + ", ".join([n.str() for n in ns]) + "]"

def tr2str(t):
    return "." if t is None else t.str()

# Helper functions
def sizeNs(xs):
    return sum(map(lambda x: x.size, xs))

def sizeT(t):
    if t is None:
        return 0 
    else: 
        return t.size

def wrap(x):
    return Node(1, [x])

def wraps(xs):
    return Node(sizeNs(xs), xs)

def leaf(x):
    return Tree(x.size, [x], None, [])

def empty():
    return Tree(0, [], None, [])

def nodes(xs):
    res = []
    while len(xs) > 4:
        res.append(wraps(xs[:3]))
        xs = xs[3:]
    if len(xs) == 4:
        res.append(wraps(xs[:2]))
        res.append(wraps(xs[2:]))
    elif xs != []:
        res.append(wraps(xs))
    return res

def frontFull(t):
    return t is not None and len(t.front) >= 3

def rearFull(t):
    return t is not None and len(t.rear) >= 3

def isLeaf(t):
    return t is not None and len(t.front) == 1 and t.rear ==[]

def isBranch(t):
    return t is not None and (not isLeaf(t))

def normalize(t):
    if t is not None and t.front == [] and len(t.rear) == 1:
        (t.front, t.rear) = (t.rear, t.front)
    return t

def insert(x, t):
    return prepend_node(wrap(x), t)

# inserting a node in single-pass manner
def prepend_node(n, t):
    root = t
    prev = None
    while frontFull(t):
        f = t.front
        t.front = [n] + f[:1]
        t.size = t.size + n.size
        n = wraps(f[1:])
        prev = t
        t = t.mid
    if t is None:
        t = Tree(n.size, [n], None, [])
    elif isLeaf(t):
        t = Tree(n.size + t.size, [n], None, t.front)
    else:
        t = Tree(n.size + t.size, [n]+t.front, t.mid, t.rear)
    if prev is not None:
        prev.mid = t
    else:
        root = t
    return root

# extract the first NODE from tree
# assume t is not None
# TODO: handle ill-formed tree
def extract_head(t):
    root = t
    prev = None
    x = first_node(t) 
    # a repeat - until loop
    while True:
        t.size = t.size - t.front[0].size
        t.front = t.front[1:]
        if t.mid is not None and t.front == []:
            prev = t
            t = t.mid
            prev.front = t.front[0].children
        else:
            break
    if t.mid is None and t.front == []:
        if t.rear == []:
            t = None
        elif len(t.rear) == 1:
            t = Tree(t.size, t.rear, None, [])
        else:
            t = Tree(t.size, t.rear[:1], None, t.rear[1:])
    if prev is not None:
        prev.mid = t
    else:
        root = t
    return (x, root)

# return the first ELEMENT
def first(t):
    return first_node(t).children[0]

# return the first NODE
def first_node(t):
    return t.front[0]

def tail(t):
    (_, t1) = extract_head(t)
    return t1

def append(t, x):
    return append_node(t, wrap(x))

def append_node(t, n):
    root = t
    prev = None
    while rearFull(t):
        r = t.rear
        t.rear = r[-1:] + [n]
        t.size = t.size + n.size
        n = wraps(r[:-1])
        prev = t
        t = t.mid
    if t is None:
        t = Tree(n.size, [n], None, [])
    elif len(t.rear) == 1 and t.front == []:
        t = Tree(n.size + t.size, t.rear, None, [n])
    else:
        t = Tree(n.size + t.size, t.front, t.mid, t.rear + [n])
    if prev is not None:
        prev.mid = t
    else:
        root = t
    return root

# TODO: handle ill-formed tree
def extract_tail(t):
    root = t
    prev = None
    x = last_node(t)
    if t.size == 1:
        return (x, None)
    while True:
        t.size = t.size - t.rear[-1].size # BUG: rear == [] ???
        t.rear = t.rear[:-1]
        if t.mid is not None and t.rear == []:
            prev = t
            t = t.mid
            if isLeaf(t):
                t = Tree(t.size, [], None, t.front)
            prev.rear = t.rear[-1].children
        else:
            break
    if t.mid is None and t.rear == []:
        if t.front == []:
            t = None
        else:
            t = Tree(t.size, t.front[:-1], None, t.front[-1:])
    if prev is not None:
        prev.mid = t
    else:
        root = t
    return (x, normalize(root))

def last(t):
    return last_node(t).children[-1]

def last_node(t):
    if t.rear == [] and t.front != []:
        return t.front[-1]
    return t.rear[-1]

def init(t):
    (_, t1) = extract_tail(t)
    return t1

def concat(t1, t2):
    return merge(t1, [], t2)

def merge(t1, ns, t2):
    root = None
    prev = empty() #sentinel dummy tree
    while isBranch(t1) and isBranch(t2):
        t = Tree(t1.size + t2.size + sizeNs(ns), t1.front, None, t2.rear)
        if root is None:
            root = t
        prev.mid = t
        prev = t
        ns = nodes(t1.rear + ns + t2.front)
        t1 = t1.mid
        t2 = t2.mid
    if isLeaf(t1):
        ns = t1.front + ns
        t1 = None
    if isLeaf(t2):
        ns = ns + t2.front
        t2 = None
    t = None
    if t1 is None:
        t = t2
        for n in reversed(ns):
            t = prepend_node(n, t)
    elif t2 is None:
        t = t1
        for n in ns:
            t = append_node(t, n)
    prev.mid = t
    if root is None:
        root = t
    return root

def getAt(t, i):
    return applyAt(t, i, lambda x : x) # applying id function

def setAt(t, i, x):
    return applyAt(t, i, lambda y : x)

# apply function f to the element at i position
# return the original element before applying f
def applyAt(t, i, f):
    while t.size > 1:
        szf = sizeNs(t.front)
        szm = sizeT(t.mid)
        if i < szf:
            return lookupNs(t.front, i, f)
        elif i < szf + szm:
            t = t.mid
            i = i - szf
        else:
            return lookupNs(t.rear, i - szf - szm, f)
    x = first(t)
    t.front[0].children[0] = f(x)
    return x

# lookup in a list of node for position i, and 
# apply function f to the element
# return the original element before applying f
def lookupNs(ns, i, f):
    while True:
        for n in ns:
            if n.size == 1 and i == 0:
                x = n.children[0]
                n.children[0] = f(x)
                return x
            if i < n.size:
                ns = n.children
                break
            i = i - n.size

# TODO: splitAt, removeAt

# split(t, i) ==> (t1, x, t2)
def splitAt(t, i):
    # TODO: handle leaf case???
    # 1st top-down pass
    (t1_prev, t2_prev) = (empty(), empty())
    (t1, t2) = (t1_prev, t2_prev)
    (s1, s2) = (i, t.size - i - 1)
    szf = szm = 0
    while True:
        print "split", tr2str(t), "at", i
        szf = sizeNs(t.front)
        szm = sizeT(t.mid)
        if szf <= i and i < szf + szm:
            fst = Tree(0, t.front, None, [])
            snd = Tree(0, [], None, t.rear)
            (t1_prev.mid, t2_prev.mid) = (fst, snd)
            (t1_prev, t2_prev) = (t1_prev.mid, t2_prev.mid)
            t = t.mid
            i = i - szf
        else:
            break

    if i < szf:
        (xs, y, ys) = splitNs(t.front, i)
        sz = t.size - sizeNs(xs) - y.size
        (fst, n, snd) = (fromNodes(xs), y, Tree(sz, ys, t.mid, t.rear))
    elif szf + szm <= i:
        (xs, y, ys) = splitNs(t.rear, i - szf - szm)
        sz = t.size - sizeNs(ys) - y.size
        (fst, n, snd) = (Tree(sz, t.front, t.mid, xs), y, fromNodes(ys))
    (t1_prev.mid, t2_prev.mid) = (fst, snd)

    # 2nd top-down pass
    (t1_prev, t2_prev) = (t1.mid, t2.mid)
    i = i - sizeT(fst)
    while y.size > 1:
        (xs, y, ys) = splitNs(y.children, i)
        i = i - sizeNs(xs)
        (t1_prev.rear, t2_prev.front) = (xs, ys) # Need further balance if xs or ys is []
        (t1_prev.size, t2_prev.size) = (s1, s2)
        s1 = s1 - sizeNs(t1_prev.front) - sizeNs(t1_prev.rear)
        s2 = s2 - sizeNs(t2_prev.front) - sizeNs(t2_prev.rear)
        (t1_prev, t2_prev) = (t1_prev.mid, t2_prev.mid)

    # compress one useless level if neccessary
    if t1.size == 0 and t2.size == 0:
        (t1, t2) = (t1.mid, t2.mid)
    
    print "==>t1=", tr2str(t1), "x=", y.children[0], "t2=", tr2str(t2)
    return (balance(t1), y.children[0], balance(t2))

def splitNs(ns, i):
    print "split nodes", ns2str(ns), "at", i
    for j in range(len(ns)):
        if i < ns[j].size:
            print "==>", ns2str(ns[:j]), ns[j].str(), ns2str(ns[j+1:])
            return (ns[:j], ns[j], ns[j+1:])
        i = i - ns[j].size

def unbalanced(t):
    return t.mid is not None and (t.front == [] or t.rear == [])

# TODO: eliminate recursion.
def balance(t):
    print "before balance:", tr2str(t)
    if t is None:
        print "after balance:", tr2str(t)
        return t
    else:
        t.mid = balance(t.mid)
        if unbalanced(t):
            if t.front == []:
                (n, t.mid) = extract_head(t.mid)
                t.front = n.children
                t.size = t.size + n.size
            elif t.rear == []:
                (t.mid, n) = extract_tail(t.mid)
                t.rear = n.children
                t.size = t.size + n.size
        if t.mid is None:
            if t.front == []:
                t = fromNodes(t.rear)
            elif t.rear == []:
                print "here"
                t = fromNodes(t.front)
                print "t=", tr2str(t)
    print "after balance:", tr2str(t)
    return t
            
# Auxiliary functions for verification

def fromListR(xs):
    return foldR(insert, xs, None)

def toListR(t):
    xs = []
    while t is not None:
        (n, t) = extract_head(t)
        xs.append(n.children[0])
    return xs

def fromListL(xs):
    return reduce(append, xs, None)

def toListL(t):
    xs = []
    while t is not None:
        (n, t) = extract_tail(t)
        xs.insert(0, n.children[-1])
    return xs

def fromNodes(ns):
    return foldR(prepend_node, ns, None)

def __assert(xs, ys):
    if xs != ys:
        print "assertion failed!"
        print xs
        print ys
        quit()

def test_rebuild():
    for i in range(100):
        xs = range(i)
        assert toListR(fromListR(xs)) == xs
        assert toListR(fromListL(xs)) == xs
        assert toListL(fromListR(xs)) ==xs
        assert toListL(fromListL(xs)) == xs

def test_concat():
    m = 100
    for i in range(m):
        xs = random.sample(range(m), random.randint(0, m))
        ys = random.sample(range(m), random.randint(0, m))
        assert toListR(concat(fromListR(xs), fromListR(ys))) == (xs + ys)

def test_random_access():
    xs = range(100)
    t = fromListR(xs)
    ys = [getAt(t, i) for i in xs]
    assert xs == ys
    [setAt(t, i, 99 - xs[i]) for i in xs]
    ys = [getAt(t, i) for i in xs]
    xs.reverse()
    __assert(xs, ys)

def test_split():
    for i in range(100):
        lst = range(100)
        (xs, y, ys) = (lst[:i], lst[i], lst[i+1:])
        t = fromListR(lst)
        (t1, x, t2) = splitAt(t, i)
        __assert(xs, toListR(t1))
        __assert(ys, toListR(t2))
        assert(x == y)

if __name__ == "__main__":
    test_rebuild()
    test_concat()
    test_random_access()
    test_split()
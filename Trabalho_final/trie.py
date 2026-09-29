class Node:
    def __init__(self, R):
        self.val = None
        self.next = [None] * R

class Trie:
    def __init__ (self):
        self.root = None
        self.R = 256
    
    def Value_get(self, key):
        x = self.Node_get(self.root, key, 0)
        if x is None:
            return None
        return x.val
    
    def Node_get(self, x, key, d):
        if (x is None):
            return None
        if d == len(key):
            return x
        c = key[d]
        return self.Node_get(x.next[ord(c)], key, d+1)
    
    def put(self, key, val):
        self.root = self.Node_put(self.root, key, val, 0)

    def Node_put(self, x, key, val, d):
        if x is None:
            x = Node(self.R)
        if d == len(key):
            x.val = val
            return x
        c = key[d]
        x.next[ord(c)] = self.Node_put(x.next[ord(c)], key, val, d+1)
        return x
    
    def buscar_prefixo(self, prefixo):
        Node_pref = self.Node_get(self.root, prefixo, 0)
        if Node_pref is None:
            return []
        ids = []
        self.colect(Node_pref, ids)
        return ids
    
    def colect(self, x, lista):
        if x is None:
            return
        if x.val is not None:
            lista.append((x.val))
        for c in range(self.R):
            if x.next[c] is not None:
                self.colect(x.next[c], lista)
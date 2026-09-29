class HashTable:
    def __init__(self, M):
        self.M = M
        self.tabela = [[] for i in range(self.M)] #lista encadeada
        
    def hash_function(self, key):
        if isinstance(key, int): return key % self.M
        elif isinstance(key, str):
            h = 0
            for char in key:
                h = (33 * h + ord(char)) % self.M
            return h
        
    def inserir(self, key, value):
        i = self.hash_function(key)
        for j in self.tabela[i]:
            if j[0] == key:
                j[1] = value
                return
        self.tabela[i].append([key, value]) #insere no final da lista encadeada
        
    def buscar(self, key):
        i = self.hash_function(key)
        for value in self.tabela[i]:
            if  value[0] == key:
                return value[1]
        return None
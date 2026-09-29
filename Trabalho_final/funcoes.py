import csv
from pathlib import Path
from classes import Movie, Usuario, Tag
import time

def carregar_dados(
    hash_filmes,
    trie_filmes,
    hash_user,
    hash_tags,
    diretorio="dados-trabalho-completo",
    arquivo_ratings="ratings.csv",
    progresso=None,
):
    """Carrega o MovieLens nas estruturas desenvolvidas no trabalho.

    ``progresso`` recebe mensagens e percentuais e permite que interfaces
    exibam o carregamento sem misturar a regra de negócio com a apresentação.
    """
    diretorio = Path(diretorio)
    caminhos = {
        "ratings": diretorio / arquivo_ratings,
        "movies": diretorio / "movies.csv",
        "tags": diretorio / "tags.csv",
    }
    ausentes = [str(caminho) for caminho in caminhos.values() if not caminho.exists()]
    if ausentes:
        raise FileNotFoundError("Arquivos de dados não encontrados: " + ", ".join(ausentes))

    def atualizar(mensagem, percentual):
        print(mensagem)
        if progresso:
            progresso(mensagem, percentual)

    start_time = time.time()
    atualizar("Indexando filmes na Hash Table e na Trie...", 20)
    with caminhos["movies"].open(encoding="utf-8", newline="") as arquivo:
        for row in csv.DictReader(arquivo):
            movie_id = int(row["movieId"])
            year = int(row["year"]) if row.get("year") else None
            movie = Movie(movie_id, row["title"], row["genres"], year)
            hash_filmes.inserir(key=movie_id, value=movie)
            key_limpa = row["title"].lower().encode('ascii', 'ignore').decode('ascii')
            trie_filmes.put(key=key_limpa, val=movie_id)
    end_time = time.time()
    print("Tempo de carregamento dos dados: {:.2f} segundos".format(end_time - start_time))
    
    start_time = time.time()
    atualizar("Processando avaliações dos usuários...", 50)
    ultimo_user_id = -1
    user_atual = None
    total_avaliacoes = 0
    with caminhos["ratings"].open(encoding="utf-8", newline="") as arquivo:
        for row in csv.DictReader(arquivo):
            user_id = int(row["userId"])
            movie_id = int(row["movieId"])
            rating = float(row["rating"])
            if user_id != ultimo_user_id:
                ultimo_user_id = user_id
                user_atual = hash_user.buscar(ultimo_user_id)
                if user_atual is None:
                    user_atual = Usuario(ultimo_user_id)
                    hash_user.inserir(key=ultimo_user_id, value=user_atual)
            user_atual.adicionar_rating(movie_id, rating)
            filme = hash_filmes.buscar(movie_id)
            if filme is not None:
                filme.add_rating(rating)
            total_avaliacoes += 1
    end_time = time.time()
    print("Tempo de carregamento dos ratings: {:.2f} segundos".format(end_time - start_time))
    
    start_time = time.time()
    atualizar("Criando índice de tags...", 80)
    with caminhos["tags"].open(encoding="utf-8", newline="") as arquivo:
        for row in csv.DictReader(arquivo):
            if not row.get("tag"):
                continue
            tag_str = row["tag"].lower()
            movie_id = int(row["movieId"])
            tag_obj = hash_tags.buscar(key=tag_str)
            if tag_obj is None:
                tag_obj = Tag(tag_str)
                hash_tags.inserir(key=tag_str, value=tag_obj)
            tag_obj.adicionar_movie(movie_id)
    end_time = time.time()
    print("Tempo de carregamento das tags: {:.2f} segundos".format(end_time - start_time))
    atualizar("Dados prontos para consulta.", 100)

    return {
        "filmes": len(hash_filmes),
        "usuarios": len(hash_user),
        "tags": len(hash_tags),
        "avaliacoes": total_avaliacoes,
    }

def shell_sort(lista, key):
    n = len(lista)
    if n <= 1:
        return lista
    gaps_ciura = [1, 4, 10, 27, 72, 187, 488, 1272, 3317, 8649, 22551, 58803, 153329, 399863, 1042656, 2718423, 7088195, 18482496, 48197771, 125690021] 
    for i in range(len(gaps_ciura)): #percorre pelo ultimo ao primeiro
        if gaps_ciura[i] < n:
            gap = i
        else: break
        
    while gap >= 0:
        h = gaps_ciura[gap]
        for i in range(h, n):
            temp = lista[i]
            temp_key = key(temp)
            j = i
            while j >= h and key(lista[j - h]) < temp_key:
                lista[j] = lista[j-h]
                j -= h
            lista[j] = temp
        gap -= 1
    return lista

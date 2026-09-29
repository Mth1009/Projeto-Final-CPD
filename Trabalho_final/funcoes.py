import pandas as pd
from classes import Movie, Usuario, Tag
import time

def carregar_dados(hash_filmes, trie_filmes, hash_user, hash_tags):
    df_ratings = pd.read_csv("dados-trabalho-completo/ratings.csv")
    df_movies = pd.read_csv("dados-trabalho-completo/movies.csv")
    df_tags = pd.read_csv("dados-trabalho-completo/tags.csv")
    
    start_time = time.time()
    print("Carregando dados..." )
    for row in df_movies.itertuples():
        year = int(row.year) if pd.notna(row.year) else None
        movie = Movie(row.movieId, row.title, row.genres, year)
        hash_filmes.inserir(key=row.movieId, value=movie)
        key_limpa = row.title.lower().encode('ascii', 'ignore').decode('ascii')
        trie_filmes.put(key=key_limpa, val=row.movieId)
    end_time = time.time()
    print("Tempo de carregamento dos dados: {:.2f} segundos".format(end_time - start_time))
    
    start_time = time.time()
    print("Carregando ratings..." )
    ultimo_user_id = -1
    user_atual = None
    for row in df_ratings.itertuples():
        if row.userId != ultimo_user_id:
            ultimo_user_id = row.userId
            user_atual = hash_user.buscar(ultimo_user_id)
            if user_atual is None:
                user_atual = Usuario(ultimo_user_id)
                hash_user.inserir(key=ultimo_user_id, value=user_atual)
        user_atual.adicionar_rating(row.movieId, row.rating)
        filme = hash_filmes.buscar(row.movieId)
        if filme is not None:
            filme.add_rating(row.rating)
    end_time = time.time()
    print("Tempo de carregamento dos ratings: {:.2f} segundos".format(end_time - start_time))
    
    start_time = time.time()
    print("Carregando tags..." )
    for row in df_tags.itertuples():
        if pd.isna(row.tag):
            continue
        tag_str = str(row.tag).lower() # Normaliza para minúsculo
        movie_id = row.movieId
        tag_obj = hash_tags.buscar(key=tag_str)
        if tag_obj is None:
            tag_obj = Tag(tag_str)
            hash_tags.inserir(key=tag_str, value=tag_obj)
        tag_obj.adicionar_movie(movie_id)
    end_time = time.time()
    print("Tempo de carregamento das tags: {:.2f} segundos".format(end_time - start_time))

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
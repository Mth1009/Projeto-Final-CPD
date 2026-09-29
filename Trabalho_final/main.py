
import time
import sys

from hash_table import HashTable
from trie import Node, Trie
from classes import Movie, Usuario, Tag
from funcoes import shell_sort, carregar_dados 

def do_search_prefixo(hash_filmes, trie_filmes, command_parts):
    if len(command_parts) < 2:
        print("Erro: Formato inválido. Use: prefixo <nome do filme>")
        return
    prefixo = " ".join(command_parts[1:])
    key_limpa = prefixo.lower().encode('ascii', 'ignore').decode('ascii')
    ids_encontrados = trie_filmes.buscar_prefixo(key_limpa)
    if not ids_encontrados:
        print(f"Nenhum filme encontrado com o prefixo: '{prefixo}'")
        return
    resultados = []
    for movie_id in ids_encontrados:
        filme = hash_filmes.buscar(key=movie_id)
        if filme:
            resultados.append(filme)
    shell_sort(resultados, key=lambda movie: movie.get_average_rating())
    print(f"--- Filmes encontrados para '{prefixo}' ({len(resultados)}): ---")
    print("-" * 130)
    print(f"{'Movie ID':<10} | {'Título':<45} | {'Gênero':<30} | {'Ano':<10} | {'Global':<10} | {'Counting':<10}")
    for filme in resultados:
        print(f"{filme.movieId:<10} | {filme.title[:43]:<45} | {filme.genres[:28]:<30} | {filme.year:<10} | {filme.get_average_rating():<10.6f} | {filme.avaliacoes:<10}")
    print("-" * 130)
    pass

def do_search_user(hash_filmes, hash_user, command_parts):
    user_id = int(command_parts[1])
    user = hash_user.buscar(user_id)
    if user is None:
        print("Usuário com ID {} não foi encontrado.".format(user_id))
        return
    else: print(f"--- Ratings do Usuário {user_id} ---")
    ratings = user.obter_ratings()
    lista_filmes = []
    for movie_id, user_rating in ratings:
        filme = hash_filmes.buscar(movie_id)
        if(filme):
            lista_filmes.append((user_rating, filme.get_average_rating(), filme))
    shell_sort(lista_filmes, key=lambda item: (item[0], item[1]))  # Ordena por rating
    print("-" * 130)
    print(f"{'Movie ID':<10} | {'Título':<45} | {'Gênero':<30} | {'Ano':<10} | {'Global':<10} | {'Counting':<10}| {'Rating':<10}")
    for user_rating, nota_global, filme_objeto in lista_filmes[:20]:
            print(f"{filme_objeto.movieId:<10} | {filme_objeto.title[:43]:<45} | {filme_objeto.genres[:28]:<30} | {filme_objeto.year:<10} | {nota_global:<10.6f}| {filme_objeto.avaliacoes:<10}| {user_rating:<10}")
    print("-" * 130)
    pass

def do_search_top(hash_filmes, command_parts):
    if (len(command_parts) < 3):
        print("Erro: Formato inválido. Use: top N <gênero>")
        return
    N = int(command_parts[1])
    genero = "".join(command_parts[2:])
    resultados = []
    for bloco in hash_filmes.tabela:
        for movieId, filme in bloco:
            if filme.avaliacoes < 10:
                continue
            if genero.lower() in filme.genres.lower():
                resultados.append(filme)
    if not resultados:
        print(f"Nenhum filme encontrado para o gênero: '{genero}'")
        return
    shell_sort(resultados, key=lambda movie: movie.get_average_rating())
    print(f"--- Top {N} filmes para o gênero '{genero}' ---")
    print("-" * 130)
    print(f"{'Movie ID':<10} | {'Título':<45} | {'Gênero':<30} | {'Ano':<10} | {'Global':<10} | {'Counting':<10}")
    for filme in resultados[:N]:
        print(f"{filme.movieId:<10} | {filme.title[:43]:<45} | {filme.genres[:28]:<30} | {filme.year:<10} | {filme.get_average_rating():<10.6f} | {filme.avaliacoes:<10}")
    print("-" * 130)
    pass

def do_search_tags(hash_filmes, hash_tags, command):
    if len(command) < 2:
        print("Erro: Formato inválido. Use: tags 'tag 1' 'tag 2' ...")
        return
    nometag1 = ''.join(command[1])
    nometag2 = ''.join(command[2])
    tag1 = nometag1.replace("'", "").replace('"', '').strip().lower()
    tag2 = nometag2.replace("'", "").replace('"', '').strip().lower()
    tag_obj1 = hash_tags.buscar(tag1)
    tag_obj2 = hash_tags.buscar(tag2)
    if tag_obj1 is None or tag_obj2 is None:
        print("Uma ou ambas as tags não foram encontradas.")
        return
    movie_ids_tag1 = set(tag_obj1.obter_movies())
    movie_ids_tag2 = set(tag_obj2.obter_movies())
    resultado = movie_ids_tag1.intersection(movie_ids_tag2)
    if not resultado:
        print(f'Nenhum filme encontrado com as tags: {tag1} e {tag2}')
        return
    print(f'--- Filmes econtrados com as tags {tag1} e {tag2}---')
    print(f'--- {len(resultado)} filmes encontrados ---')
    print("-" * 130)
    print(f"{'Movie ID':<10} | {'Título':<45} | {'Gênero':<30} | {'Ano':<10} | {'Global':<10} | {'Counting':<10}")
    filmes_ordenados = []
    for movie_id in resultado:
        filme = hash_filmes.buscar(movie_id)
        if filme:
            filmes_ordenados.append(filme)
    shell_sort(filmes_ordenados, key=lambda movie: movie.get_average_rating())
    for filme in filmes_ordenados:
        print(f"{filme.movieId:<10} | {filme.title[:43]:<45} | {filme.genres[:28]:<30} | {filme.year:<10} | {filme.get_average_rating():<10.6f} | {filme.avaliacoes:<10}")
    print("-" * 130)
    pass

def do_search_best(hash_filmes, command_parts):
    N = int(command_parts[1])
    year1 =int(command_parts[2])
    year2 = int(command_parts[3])
    resultados = []
    for bloco in hash_filmes.tabela:
        for movieId, filme in bloco:
            if filme.avaliacoes <1000:
                continue
            if filme.year is not None and year1 <= filme.year <= year2:
                resultados.append(filme)
    if not resultados:
        print(f"Nenhum filme encontrado entre os anos: '{year1}' e '{year2}'")
        return
    shell_sort(resultados, key=lambda movie: movie.get_average_rating())
    print(f"--- Top {N} filmes entre os anos '{year1}' e '{year2}' ---")
    print("-" * 130)
    print(f"{'Movie ID':<10} | {'Título':<45} | {'Gênero':<30} | {'Ano':<10} | {'Global':<10} | {'Counting':<10}")
    for filme in resultados[:N]:
        print(f"{filme.movieId:<10} | {filme.title[:43]:<45} | {filme.genres[:28]:<30} | {filme.year:<10} | {filme.get_average_rating():<10.6f} | {filme.avaliacoes:<10}")
    print("-" * 130)
    pass

def main():
    hash_filmes = HashTable(M=25273)
    trie_filmes = Trie()
    hash_user = HashTable(M=150001)
    hash_tags = HashTable(M=500009)
    start_time = time.time()
    carregar_dados(hash_filmes, trie_filmes, hash_user, hash_tags)
    end_time = time.time()
    print(f"\n--- Dados Carregados em {end_time - start_time:.4f} segundos ---")
    
    while True:
        print("\n--- Modo Console ---")
        print("Comandos: prefixo, user, top N, tags 'tag 1' 'tag 2', best, exit")
        print("-" * 130)
        command = input("\nDigite seu comando: ").strip()
        if not command: continue
            
        parts = command.split()
        cmd = parts[0].lower()

        if cmd == "prefixo":
            do_search_prefixo(hash_filmes, trie_filmes, parts)
        elif cmd == "user":
            do_search_user(hash_filmes, hash_user, parts)
        elif cmd == "top":
            do_search_top(hash_filmes, parts)
        elif cmd == "tags":
            do_search_tags(hash_filmes, hash_tags, parts)
        elif cmd == "best":
            do_search_best(hash_filmes, parts)
        elif cmd == "exit" or cmd == "quit":
            print("Saindo...")
            break
        else:
            print(f"Comando desconhecido: '{cmd}'")
# --- Ponto de Entrada do Script ---
if __name__ == "__main__":
    if "--gui" in sys.argv:
        from gui import executar

        executar()
    else:
        main()

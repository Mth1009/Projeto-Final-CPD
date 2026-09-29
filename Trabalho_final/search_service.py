"""Camada de consultas compartilhada pela interface gráfica e pelo console."""

from dataclasses import dataclass
from pathlib import Path

from funcoes import carregar_dados, shell_sort
from hash_table import HashTable
from trie import Trie


@dataclass(frozen=True)
class ResultadoFilme:
    movie_id: int
    titulo: str
    generos: str
    ano: int | None
    nota_global: float
    avaliacoes: int
    nota_usuario: float | None = None


def normalizar(texto):
    return texto.lower().encode("ascii", "ignore").decode("ascii")


class MovieSearchService:
    """Orquestra as estruturas de dados sem depender de terminal ou GUI."""

    def __init__(self):
        self.hash_filmes = HashTable(M=25273)
        self.trie_filmes = Trie()
        self.hash_usuarios = HashTable(M=150001)
        self.hash_tags = HashTable(M=500009)
        self.estatisticas = {}
        self.carregado = False
        self.modo_dados = "amostra"

    def carregar(self, modo="amostra", progresso=None):
        self.modo_dados = modo
        raiz = Path(__file__).resolve().parent
        if modo == "completo":
            diretorio = raiz / "dados-trabalho-completo"
            ratings = "ratings.csv"
        else:
            diretorio = raiz / "dados-trabalho-pequeno"
            ratings = "miniratings.csv"

        self.estatisticas = carregar_dados(
            self.hash_filmes,
            self.trie_filmes,
            self.hash_usuarios,
            self.hash_tags,
            diretorio=diretorio,
            arquivo_ratings=ratings,
            progresso=progresso,
        )
        self.carregado = True
        return self.estatisticas

    @staticmethod
    def _resultado(filme, nota_usuario=None):
        return ResultadoFilme(
            movie_id=filme.movieId,
            titulo=filme.title,
            generos=filme.genres.replace("|", ", "),
            ano=filme.year,
            nota_global=filme.get_average_rating(),
            avaliacoes=filme.avaliacoes,
            nota_usuario=nota_usuario,
        )

    def buscar_prefixo(self, prefixo):
        prefixo = prefixo.strip()
        if not prefixo:
            raise ValueError("Digite o início do título do filme.")
        ids = self.trie_filmes.buscar_prefixo(normalizar(prefixo))
        filmes = [self.hash_filmes.buscar(movie_id) for movie_id in ids]
        filmes = [filme for filme in filmes if filme is not None]
        shell_sort(filmes, key=lambda filme: filme.get_average_rating())
        return [self._resultado(filme) for filme in filmes]

    def buscar_usuario(self, user_id, limite=20):
        try:
            user_id = int(user_id)
        except (TypeError, ValueError) as exc:
            raise ValueError("Informe um ID de usuário válido.") from exc
        usuario = self.hash_usuarios.buscar(user_id)
        if usuario is None:
            return []
        resultados = []
        for movie_id, nota_usuario in usuario.obter_ratings():
            filme = self.hash_filmes.buscar(movie_id)
            if filme:
                resultados.append((nota_usuario, filme.get_average_rating(), filme))
        shell_sort(resultados, key=lambda item: (item[0], item[1]))
        return [self._resultado(filme, nota) for nota, _, filme in resultados[:limite]]

    def buscar_top_genero(self, quantidade, genero):
        quantidade = self._validar_quantidade(quantidade)
        genero = genero.strip()
        if not genero:
            raise ValueError("Informe um gênero.")
        filmes = [
            filme
            for filme in self.hash_filmes.valores()
            if filme.avaliacoes >= 10 and genero.lower() in filme.genres.lower()
        ]
        shell_sort(filmes, key=lambda filme: filme.get_average_rating())
        return [self._resultado(filme) for filme in filmes[:quantidade]]

    def buscar_tags(self, tag_1, tag_2):
        tag_1, tag_2 = tag_1.strip().lower(), tag_2.strip().lower()
        if not tag_1 or not tag_2:
            raise ValueError("Informe as duas tags para combinar.")
        objeto_1 = self.hash_tags.buscar(tag_1)
        objeto_2 = self.hash_tags.buscar(tag_2)
        if objeto_1 is None or objeto_2 is None:
            return []
        ids = set(objeto_1.obter_movies()).intersection(objeto_2.obter_movies())
        filmes = [self.hash_filmes.buscar(movie_id) for movie_id in ids]
        filmes = [filme for filme in filmes if filme is not None]
        shell_sort(filmes, key=lambda filme: filme.get_average_rating())
        return [self._resultado(filme) for filme in filmes]

    def buscar_melhores_periodo(self, quantidade, ano_inicial, ano_final):
        quantidade = self._validar_quantidade(quantidade)
        try:
            ano_inicial, ano_final = int(ano_inicial), int(ano_final)
        except (TypeError, ValueError) as exc:
            raise ValueError("Informe anos válidos.") from exc
        if ano_inicial > ano_final:
            raise ValueError("O ano inicial deve ser menor ou igual ao ano final.")
        # A amostra tem somente 10 mil avaliações; o limite proporcional mantém
        # esta consulta demonstrável. Na base completa vale o requisito original.
        minimo_avaliacoes = 10 if self.modo_dados == "amostra" else 1000
        filmes = [
            filme
            for filme in self.hash_filmes.valores()
            if filme.avaliacoes >= minimo_avaliacoes
            and filme.year is not None
            and ano_inicial <= filme.year <= ano_final
        ]
        shell_sort(filmes, key=lambda filme: filme.get_average_rating())
        return [self._resultado(filme) for filme in filmes[:quantidade]]

    @staticmethod
    def _validar_quantidade(quantidade):
        try:
            quantidade = int(quantidade)
        except (TypeError, ValueError) as exc:
            raise ValueError("Informe uma quantidade válida.") from exc
        if not 1 <= quantidade <= 100:
            raise ValueError("A quantidade deve estar entre 1 e 100.")
        return quantidade

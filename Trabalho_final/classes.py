class Tag:
    def __init__(self, tag_name):
        self.tag_name = tag_name
        self.movie_ids = []
        
    def adicionar_movie(self, movie_id):
        if movie_id not in self.movie_ids:
            self.movie_ids.append(movie_id)
        
    def obter_movies(self):
        return self.movie_ids
    
class Usuario:
    def __init__(self, user_id):
        self.user_id = user_id
        self.ratings = []
    
    def adicionar_rating(self, movie_id, rating):
        self.ratings.append((movie_id, rating))
        
    def obter_ratings(self):
        return self.ratings
    
class Movie:
    def __init__(self, movieId, title, genres, year):
        self.movieId = movieId
        self.title = title
        self.genres = genres
        self.year = year
        self.avaliacoes = 0
        self.soma_rating = 0    
        
    def add_rating(self, rating):
        self.soma_rating += rating
        self.avaliacoes += 1
        
    def get_average_rating(self):
        if self.avaliacoes == 0:
            return 0
        return self.soma_rating / self.avaliacoes
    
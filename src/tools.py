from langchain.tools import tool
from typing import Optional
import pandas as pd
from .api import call_omdb_api, OMDBAPIError
from .config import CSV_DATASET_PATH


__all__ = ("tools",)

try:
    df = pd.read_csv(CSV_DATASET_PATH)
except Exception as e:
    print(f"Warning: Could not load CSV dataset: {e}")
    df = None


def format_movie_info(movie_data: dict) -> str:
    """
    Format movie data from OMDB API into readable string.

    Args:
        movie_data: Dictionary containing movie information from OMDB API

    Returns:
        Formatted string with movie information
    """
    title = movie_data.get("Title", "N/A")
    year = movie_data.get("Year", "N/A")
    rated = movie_data.get("Rated", "N/A")
    released = movie_data.get("Released", "N/A")
    runtime = movie_data.get("Runtime", "N/A")
    genre = movie_data.get("Genre", "N/A")
    director = movie_data.get("Director", "N/A")
    actors = movie_data.get("Actors", "N/A")
    plot = movie_data.get("Plot", "N/A")
    language = movie_data.get("Language", "N/A")
    country = movie_data.get("Country", "N/A")
    awards = movie_data.get("Awards", "N/A")
    imdb_rating = movie_data.get("imdbRating", "N/A")
    imdb_votes = movie_data.get("imdbVotes", "N/A")

    return f"""Название: {title}
Год: {year}
Рейтинг: {rated}
Дата выхода: {released}
Длительность: {runtime}
Жанр: {genre}
Режиссер: {director}
Актеры: {actors}
Описание: {plot}
Язык: {language}
Страна: {country}
Награды: {awards}
IMDb рейтинг: {imdb_rating}/10 ({imdb_votes} голосов)"""


def format_movie_from_csv(movie_row) -> str:
    """
    Format movie data from CSV dataset into readable string.

    Args:
        movie_row: pandas Series containing movie information from CSV

    Returns:
        Formatted string with movie information
    """
    return f"""Название: {movie_row['Series_Title']}
Год: {movie_row['Released_Year']}
Рейтинг IMDb: {movie_row['IMDB_Rating']}/10
Жанр: {movie_row['Genre']}
Режиссер: {movie_row['Director']}
Актеры: {movie_row['Star1']}, {movie_row['Star2']}, {movie_row['Star3']}, {movie_row['Star4']}
Описание: {movie_row['Overview']}

(Источник: IMDb Top 1000 локальный датасет)"""


@tool
def search_movie_by_title(title: str, year: Optional[str] = None) -> str:
    """
    Поиск подробной информации о фильме по точному названию.
    Сначала ищет через OMDB API, если не найдено - проверяет локальный датасет IMDb Top 1000.

    Args:
        title: Название фильма (точное или близкое к точному)
        year: Год выпуска фильма (опционально, для уточнения поиска)

    Returns:
        Детальная информация о фильме или сообщение об ошибке
    """
    # Try OMDB API first
    try:
        params = {"t": title}
        if year:
            params["y"] = year

        result = call_omdb_api(params)

        if result is not None:
            return format_movie_info(result)

    except OMDBAPIError as e:
        pass  # Fall through to CSV search

    # Fallback to CSV dataset
    if df is not None:
        result = df[df["Series_Title"].str.contains(title, case=False, na=False)]
        if not result.empty:
            movie = result.iloc[0]
            return format_movie_from_csv(movie)

    return f"Фильм '{title}' не найден ни в OMDB API, ни в локальном датасете IMDb Top 1000. Попробуйте использовать search_movies_list для поиска по частичному совпадению."


@tool
def search_movies_list(query: str, year: Optional[str] = None) -> str:
    """
    Поиск списка фильмов по частичному совпадению названия.

    Args:
        query: Поисковый запрос (часть названия фильма)
        year: Год выпуска (опционально)

    Returns:
        Список найденных фильмов с годом и IMDb ID или сообщение об ошибке
    """
    try:
        params = {"s": query}
        if year:
            params["y"] = year

        result = call_omdb_api(params)

        if result is None or result.get("totalResults") == "0":
            return f"Фильмы по запросу '{query}' не найдены."

        movies = result.get("Search", [])
        if not movies:
            return f"Фильмы по запросу '{query}' не найдены."

        output = f"Найдено {result.get('totalResults', len(movies))} фильмов по запросу '{query}':\n\n"
        for i, movie in enumerate(movies[:10], 1):  # Показываем первые 10
            title = movie.get("Title", "N/A")
            year = movie.get("Year", "N/A")
            movie_type = movie.get("Type", "N/A")
            output += f"{i}. {title} ({year}) - {movie_type}\n"

        output += "\nИспользуйте search_movie_by_title с точным названием для получения подробной информации."
        return output

    except OMDBAPIError as e:
        return f"Ошибка при поиске фильмов: {str(e)}"


@tool
def compare_two_movies(title1: str, title2: str) -> str:
    """
    Сравнение двух фильмов по различным параметрам.

    Args:
        title1: Название первого фильма
        title2: Название второго фильма

    Returns:
        Сравнительная таблица характеристик двух фильмов
    """
    try:
        result1 = call_omdb_api({"t": title1})
        result2 = call_omdb_api({"t": title2})

        if result1 is None:
            return f"Первый фильм '{title1}' не найден."

        if result2 is None:
            return f"Второй фильм '{title2}' не найден."

        comparison = f"""Сравнение фильмов:

ФИЛЬМ 1: {result1.get('Title', 'N/A')}
ФИЛЬМ 2: {result2.get('Title', 'N/A')}

Год выпуска:
  • {result1.get('Title', 'N/A')}: {result1.get('Year', 'N/A')}
  • {result2.get('Title', 'N/A')}: {result2.get('Year', 'N/A')}

Жанр:
  • {result1.get('Title', 'N/A')}: {result1.get('Genre', 'N/A')}
  • {result2.get('Title', 'N/A')}: {result2.get('Genre', 'N/A')}

Режиссер:
  • {result1.get('Title', 'N/A')}: {result1.get('Director', 'N/A')}
  • {result2.get('Title', 'N/A')}: {result2.get('Director', 'N/A')}

IMDb рейтинг:
  • {result1.get('Title', 'N/A')}: {result1.get('imdbRating', 'N/A')}/10
  • {result2.get('Title', 'N/A')}: {result2.get('imdbRating', 'N/A')}/10

Длительность:
  • {result1.get('Title', 'N/A')}: {result1.get('Runtime', 'N/A')}
  • {result2.get('Title', 'N/A')}: {result2.get('Runtime', 'N/A')}

Актеры:
  • {result1.get('Title', 'N/A')}: {result1.get('Actors', 'N/A')}
  • {result2.get('Title', 'N/A')}: {result2.get('Actors', 'N/A')}

Награды:
  • {result1.get('Title', 'N/A')}: {result1.get('Awards', 'N/A')}
  • {result2.get('Title', 'N/A')}: {result2.get('Awards', 'N/A')}"""

        return comparison

    except OMDBAPIError as e:
        return f"Ошибка при сравнении фильмов: {str(e)}"


@tool
def get_movie_by_id(imdb_id: str) -> str:
    """
    Получить информацию о фильме по IMDb ID.

    Args:
        imdb_id: IMDb идентификатор фильма (например, tt0111161)

    Returns:
        Детальная информация о фильме
    """
    try:
        result = call_omdb_api({"i": imdb_id})

        if result is None:
            return f"Фильм с ID '{imdb_id}' не найден."

        return format_movie_info(result)

    except OMDBAPIError as e:
        return f"Ошибка при получении информации о фильме: {str(e)}"


@tool
def search_movies_by_year_and_type(
    query: str, year: str, movie_type: str = "movie"
) -> str:
    """
    Поиск фильмов по названию, году и типу.

    Args:
        query: Поисковый запрос (часть названия)
        year: Год выпуска
        movie_type: Тип медиа (movie, series, episode)

    Returns:
        Список найденных фильмов
    """
    try:
        params = {"s": query, "y": year, "type": movie_type}

        result = call_omdb_api(params)

        if result is None or result.get("totalResults") == "0":
            return f"Фильмы по запросу '{query}' ({year}, {movie_type}) не найдены."

        movies = result.get("Search", [])
        if not movies:
            return f"Фильмы по запросу '{query}' не найдены."

        output = f"Найдено {result.get('totalResults', len(movies))} фильмов ({year}, {movie_type}):\n\n"
        for i, movie in enumerate(movies, 1):
            title = movie.get("Title", "N/A")
            year = movie.get("Year", "N/A")
            output += f"{i}. {title} ({year})\n"

        return output

    except OMDBAPIError as e:
        return f"Ошибка при поиске: {str(e)}"


# CSV Dataset tools
@tool
def get_top_movies_by_genre(genre: str, limit: int = 5) -> str:
    """
    Получить топ фильмов по жанру из локального датасета IMDb Top 1000.

    Args:
        genre: Жанр фильма (например, Action, Drama, Comedy)
        limit: Количество фильмов (по умолчанию 5)

    Returns:
        Список топ фильмов указанного жанра с рейтингами
    """
    if df is None:
        return "Локальный датасет IMDb Top 1000 недоступен."

    filtered = df[df["Genre"].str.contains(genre, case=False, na=False)]

    if filtered.empty:
        return f"Фильмы жанра '{genre}' не найдены в датасете."

    top_movies = filtered.nlargest(limit, "IMDB_Rating")

    result = f"Топ-{limit} фильмов жанра {genre} (из IMDb Top 1000):\n\n"
    for idx, movie in top_movies.iterrows():
        result += f"{movie['Series_Title']} ({movie['Released_Year']}) - {movie['IMDB_Rating']}/10\n"

    return result


@tool
def get_movies_by_director(director: str) -> str:
    """
    Найти все фильмы режиссера из локального датасета IMDb Top 1000.

    Args:
        director: Имя режиссера (полное или частичное)

    Returns:
        Список фильмов указанного режиссера с годами и рейтингами
    """
    if df is None:
        return "Локальный датасет IMDb Top 1000 недоступен."

    result = df[df["Director"].str.contains(director, case=False, na=False)]

    if result.empty:
        return f"Фильмы режиссера '{director}' не найдены в датасете IMDb Top 1000."

    movies = "\n".join(
        [
            f"{row['Series_Title']} ({row['Released_Year']}) - {row['IMDB_Rating']}/10"
            for _, row in result.iterrows()
        ]
    )
    return f"Фильмы режиссера {director} (из IMDb Top 1000):\n\n{movies}"


@tool
def get_movies_by_actor(actor: str) -> str:
    """
    Найти фильмы с участием актера из локального датасета IMDb Top 1000.

    Args:
        actor: Имя актера (полное или частичное)

    Returns:
        Список фильмов с указанным актером, годами и рейтингами
    """
    if df is None:
        return "Локальный датасет IMDb Top 1000 недоступен."

    mask = (
        df["Star1"].str.contains(actor, case=False, na=False)
        | df["Star2"].str.contains(actor, case=False, na=False)
        | df["Star3"].str.contains(actor, case=False, na=False)
        | df["Star4"].str.contains(actor, case=False, na=False)
    )

    result = df[mask]

    if result.empty:
        return f"Фильмы с актером '{actor}' не найдены в датасете IMDb Top 1000."

    movies = "\n".join(
        [
            f"{row['Series_Title']} ({row['Released_Year']}) - {row['IMDB_Rating']}/10"
            for _, row in result.iterrows()
        ]
    )
    return f"Фильмы с {actor} (из IMDb Top 1000):\n\n{movies}"


@tool
def get_movies_by_rating(
    min_rating: float = 8.0, genre: Optional[str] = None, limit: int = 10
) -> str:
    """
    Найти фильмы по минимальному рейтингу из локального датасета IMDb Top 1000.

    Args:
        min_rating: Минимальный рейтинг IMDb (по умолчанию 8.0)
        genre: Опциональный жанр для фильтрации
        limit: Максимальное количество фильмов (по умолчанию 10)

    Returns:
        Список фильмов с рейтингом не ниже указанного
    """
    if df is None:
        return "Локальный датасет IMDb Top 1000 недоступен."

    filtered = df[df["IMDB_Rating"] >= min_rating]

    if genre:
        filtered = filtered[filtered["Genre"].str.contains(genre, case=False, na=False)]

    if filtered.empty:
        genre_text = f" жанра {genre}" if genre else ""
        return f"Фильмы{genre_text} с рейтингом ≥ {min_rating} не найдены в датасете."

    # Sort by rating and get top results
    top_movies = filtered.nlargest(limit, "IMDB_Rating")

    genre_text = f" ({genre})" if genre else ""
    result = f"Фильмы{genre_text} с рейтингом ≥ {min_rating} (из IMDb Top 1000):\n\n"
    for _, movie in top_movies.iterrows():
        result += f"{movie['Series_Title']} ({movie['Released_Year']}) - {movie['IMDB_Rating']}/10\n"
        result += f"  Жанр: {movie['Genre']}\n"
        result += f"  Режиссер: {movie['Director']}\n\n"

    return result


tools = [
    search_movie_by_title,
    search_movies_list,
    compare_two_movies,
    get_movie_by_id,
    search_movies_by_year_and_type,
    get_top_movies_by_genre,
    get_movies_by_director,
    get_movies_by_actor,
    get_movies_by_rating,
]

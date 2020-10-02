from src.gql_client.client import GQLClient
from src.scraper.imdb_scraper import IMDbScraper

if __name__ == '__main__':
    scraper = IMDbScraper()
    client = GQLClient("http://localhost:8080/graphql")
    scraper.load_title_page("the wolf of wall street")
    title = scraper.get_title_contents()

    try:
        amdb.create_title(title)
    except Exception as e:
        print(e)

    title_relations = scraper.get_title_relation_contents()
    print(title_relations)

    directors = []
    for d in title_relations["directors"]:
        scraper.load_person_page(d)
        director = scraper.get_person_contents()
        directors.append(director)

    for director in directors:
        amdb.create_person(director)
        amdb.create_directed_relation(director, title)

    writers = []
    for w in title_relations["writers"]:
        scraper.load_person_page(w)
        writer = scraper.get_person_contents()
        writers.append(writer)

    for writer in writers:
        amdb.create_person(writer)
        amdb.create_wrote_relation(writer, title)


    genres = title_relations["genres"]

    cast = {}
    for k, v in title_relations["cast"].items():
        scraper.load_person_page(k)
        actor = scraper.get_person_contents()
        cast[actor] = v

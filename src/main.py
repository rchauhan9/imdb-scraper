from src.gql_client.client import GQLClient
from src.scraper.imdb_scraper import IMDbScraper
from src.services.amdb_service import AMDbService


if __name__ == '__main__':
    scraper = IMDbScraper()
    client = GQLClient("http://localhost:8080/graphql")
    amdb = AMDbService(client)

    scraper.load_title_page("the wolf of wall street")
    title = scraper.get_title_contents()

    amdb.create_title(title)

    title_relations = scraper.get_title_relation_contents()

    # Create Director Relations
    directors = []
    for d in title_relations["directors"]:
        scraper.load_person_page(d)
        director = scraper.get_person_contents()
        directors.append(director)

    for director in directors:
        amdb.create_person(director)
        amdb.create_directed_relation(director, title)

    # Create Writer Relations
    writers = {}
    for k, v in title_relations["writers"].items():
        scraper.load_person_page(k)
        try:
            writer = scraper.get_person_contents()
            writers[writer] = v
        except Exception as e:
            continue

    for writer, items in writers.items():
        amdb.create_person(person=writer)
        amdb.create_wrote_relation(person=writer, title=title, items=items)

    # Create Producer Relations
    producers = {}
    for k, v in title_relations["producers"].items():
        scraper.load_person_page(k)
        try:
            producer = scraper.get_person_contents()
            producers[producer] = v
        except Exception as e:
            continue

    for producer, items in producers.items():
        amdb.create_person(person=producer)
        amdb.create_produced_relation(person=producer, title=title, items=items)

    # Create Genre Relations
    genres = title_relations["genres"]
    for g in genres:
        amdb.create_genre(g)
        amdb.create_genre_relation(title=title, genre_name=g)

    # Create Cast Relations
    cast = {}
    billing = 0
    for actor, chars in title_relations["cast"].items():
        scraper.load_person_page(actor)
        person = scraper.get_person_contents()
        cast[person] = (chars, billing)
        billing = billing + 1

    for actor, items in cast.items():
        amdb.create_person(person=actor)
        amdb.create_acted_in_relation(person=actor, title=title, characters=items[0], billing=items[1])

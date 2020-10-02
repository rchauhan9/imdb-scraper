import os
import sys
import logging

from src.model.person import Person
from src.model.title import Title
from src.model.award import Award

logging.basicConfig(format='%(asctime)s %(levelname)s %(process)d --- %(name)s %(funcName)20s() : %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    level=logging.INFO)


class AMDbService:
    logger = logging.getLogger('AMDbService')

    def __init__(self, client):
        self.GRAPH_QL_PATH = os.path.join(sys.path[0], "resources/graphql/")
        self.client = client

    def create_acted_in_relation(self, person: Person, title: Title, characters: list, billing: int):
        self.logger.info(f"Creating ActedInRelation between {person.__short_str__()} and {title.__short_str__()}, "
                         f"characters: {characters}, billing: {billing}.")
        variables = {
            "personName": person.name,
            "personDOB": person.get_dob("%d-%b-%Y"),
            "titleName": title.name,
            "titleReleased": title.released,
            "characters": characters,
            "billing": billing
        }
        return self.__execute_graphql_request(filename="createActedInRelation.graphql", variables=variables)

    def create_award(self, name: str, organisation: str):
        self.logger.info(f"Creating Award with name: {name} and organisation: {organisation}.")
        variables = {
            "name": name,
            "organisation": organisation
        }
        return self.__execute_graphql_request(filename="createAward.graphql", variables=variables)

    def create_directed_relation(self, person: Person, title: Title):
        self.logger.info(f"Creating DirectedRelation between {person.__short_str__()} and {title.__short_str__()}.")
        variables = {
            "personName": person.name,
            "personDOB": person.get_dob("%d-%b-%Y"),
            "titleName": title.name,
            "titleReleased": title.released
        }
        self.__execute_graphql_request(filename="createDirectedRelation.graphql", variables=variables)

    def create_genre(self, name: str):
        self.logger.info(f"Creating Genre with name: {name}.")
        variables = {
            "name": name
        }
        self.__execute_graphql_request(filename="createGenre.graphql", variables=variables)

    def create_genre_relation(self, title: Title, genre_name: str):
        self.logger.info(f"Creating GenreRelation between {title.__short_str__()} and Genre({genre_name}).")
        variables = {
            "titleName": title.name,
            "titleReleased": title.released,
            "genreName": genre_name
        }
        self.__execute_graphql_request(filename="createGenreRelation.graphql", variables=variables)

    def create_nominated_relation(self, person: Person, award: Award, organisation: str):
        self.logger.info(
            f"Creating NominatedRelation between {person.__short_str__()} and Award({award.name}, {organisation}).")
        variables = {
            "personName": person.name,
            "personDOB": person.get_dob("%d-%b-%Y"),
            "awardName": award.name,
            "awardOrganisation": organisation,
            "nominationYear": award.year,
            "titleName": award.title_name,
            "titleReleased": award.title_released
        }
        self.__execute_graphql_request(filename="createNominatedRelation.graphql", variables=variables)

    def create_person(self, person: Person):
        self.logger.info(f"Creating {person.__short_str__()}.")
        variables = {
            "name": person.name,
            "dateOfBirth": person.get_dob("%Y-%m-%d")
        }
        self.__execute_graphql_request(filename="createPerson.graphql", variables=variables)

    def create_produced_relation(self, person: Person, title: Title, items: list):
        self.logger.info(
            f"Creating ProducedRelation between {person.__short_str__()} and {title.__short_str__()}, items: {items}.")
        variables = {
            "personName": person.name,
            "personDOB": person.get_dob("%d-%b-%Y"),
            "titleName": title.name,
            "titleReleased": title.released,
            "items": items
        }
        self.__execute_graphql_request(filename="createProducedRelation.graphql", variables=variables)

    def create_title(self, title: Title):
        self.logger.info(f"Creating {title.__short_str__()}")
        variables = {
            "name": title.name,
            "summary": title.summary,
            "released": title.released,
            "certificateRating": title.certificate_rating,
            "titleLengthInMins": title.title_length_in_mins,
            "storyline": title.storyline,
            "tagline": title.tagline
        }
        self.__execute_graphql_request(filename="createTitle.graphql", variables=variables)

    def create_won_relation(self, person: Person, award: Award, organisation: str):
        self.logger.info(
            f"Creating WonRelation between {person.__short_str__()} and Award({award.name}, {organisation}).")
        variables = {
            "personName": person.name,
            "personDOB": person.get_dob("%d-%b-%Y"),
            "awardName": award.name,
            "awardOrganisation": organisation,
            "wonYear": award.year,
            "titleName": award.title_name,
            "titleReleased": award.title_released
        }
        self.__execute_graphql_request(filename="createWonRelation.graphql", variables=variables)

    def create_wrote_relation(self, person: Person, title: Title, items: list):
        self.logger.info(
            f"Creating WroteRelation between {person.__short_str__()} and {title.__short_str__()}, items: {items}.")
        variables = {
            "personName": person.name,
            "personDOB": person.get_dob("%d-%b-%Y"),
            "titleName": title.name,
            "titleReleased": title.released,
            "items": items
        }
        self.__execute_graphql_request(filename="createWroteRelation.graphql", variables=variables)

    def __execute_graphql_request(self, filename: str, variables: dict):
        try:
            return self.client.execute(filepath=self.GRAPH_QL_PATH + filename, variables=variables)
        except Exception as e:
            self.logger.error(e, exc_info=True)

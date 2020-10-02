from enum import Enum


class AwardOrganisation(Enum):
    ACADEMY_AWARDS = "Academy Awards"
    GOLDEN_GLOBES = "Golden Globes"
    BAFTA_AWARDS = "BAFTA Awards"


class Award():
    """
    A model class that stores the basic information to create an Award and Nominated/Won Relations for AMDb.
    """
    def __init__(self, name: str, outcome: str, year: int, title_name: str, title_released: int):
        self.name = name
        self.outcome = outcome
        self.year = year
        self.title_name = title_name
        self.title_released = title_released

    def __str__(self):
        return "Award(name: {0}, year: {1}, outcome: {2}, title: {3} ({4}))".format(self.name, 
                                    self.year, self.outcome, self.title_name, self.title_released)

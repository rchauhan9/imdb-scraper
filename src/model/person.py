from datetime import datetime


class Person:
    """
    A model class that stores the basic information to create a Person for AMDb.
    """

    def __init__(self, name: str, date_of_birth: datetime):
        self.name = name
        self.date_of_birth = date_of_birth

    def __str__(self):
        return "Person(name: " + self.name + \
                ", date_of_birth: " + self.get_dob("%d-%b-%Y") + \
                ")"

    def get_dob(self, format) -> str:
        """
        A method to represent a person's date of birth in a particular format.

        Args:
            format: A string representing the desired format of the person's date of birth. E.g. %d-%b-%Y returns the
            date of birth in format 01-Jan-2000.

        Returns:
            A string with the date of birth in the desired format
        """
        return self.date_of_birth.strftime(format)

    def __short_str__(self) -> str:
        """
        A method to represent a person object in a shorter string format.
        """
        return "Person({0} - {1})".format(self.name, self.get_dob("%d-%b-%Y"))

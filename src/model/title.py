class Title():

    def __init__(self, name: str, summary: str, released: int, certificate_rating: str,
                 title_length_in_mins: int, storyline: str, tagline: str):
        self.name = name
        self.summary = summary
        self.released = released
        self.certificate_rating = certificate_rating
        self.title_length_in_mins = title_length_in_mins
        self.storyline = storyline
        self.tagline = tagline

    def __str__(self):
        return "Title(name: " + self.name + \
               ", summary: " + self.summary + \
               ", released: " + str(self.released) + \
               ", certificate_rating: " + self.certificate_rating + \
               ", title_length_in_mins: " + str(self.title_length_in_mins) + \
               ", storyline: " + self.storyline + \
               ", tagline: " + self.tagline + \
               ")"

    def __short_str__(self):
        """
        A method to represent a title object in a shorter string format.
        """
        return "Title({0} ({1}))".format(self.name, self.released)

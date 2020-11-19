import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import re

from src.model.person import Person
from src.model.award import Award, AwardOrganisation
from src.model.title import Title
from src.error.exception import ParseError

BASE_URL = "https://www.imdb.com"
SEARCH_PREFIX = "/find?q="
SEARCH_SUFFIX = "&ref_=nv_sr_sm"
AWARDS_SUFFIX = "awards?ref_=nm_ql_2"
BIO_SUFFIX = "bio?ref_=nm_ov_bio_sm"
FULL_CREDITS_SUFFIX = "fullcredits?ref_=tt_ql_1"
TITLE_SIGNATURE = "title/tt"
NAME_SIGNATURE = "name/nm"

logging.basicConfig(format='%(asctime)s %(levelname)s %(process)d --- %(name)s %(funcName)20s() : %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    level=logging.INFO)


class IMDbScraper:
    logger = logging.getLogger('IMDbScraper')

    def __init__(self):
        self.soup = None
        self.search_page_url = ""
        self.first_result_url = ""
        self.full_credits_url = ""
        self.awards_url = ""
        self.bio_url = ""

    def load_title_page(self, query):
        """
        Loads the first IMDb title page based on query into 'soup' object and initialises the necessary URLs for
        scraping the page of the desired content.

        Args:
            query: The searched for title.
        """
        self.logger.info(f"Loading title page for {query}")
        self.__initialise_soup_and_urls(query)
        self.set_full_credits_url()
        self.awards_url = ""

    def load_person_page(self, query):
        """
        Loads the first IMDb person page based on query into 'soup' object and initialises the necessary URLs for
        scraping the page of the desired content.

        Args:
            query: The searched for title.
        """
        self.logger.info(f"Loading person page for {query}")
        self.__initialise_soup_and_urls(query)
        self.set_awards_url()
        self.set_bio_url()
        self.full_credits_url = ""

    def get_title_contents(self) -> Title:
        """
        Scrapes an IMDb title page for contents.

        Returns:
            A Title object containing all the scraped data.
        """
        self.logger.info(f"Getting title contents from {self.first_result_url}")
        return Title(
            name=self.get_title_name(),
            summary=self.get_title_summary(),
            released=self.get_title_release_year(),
            certificate_rating=self.get_title_certificate_rating(),
            title_length_in_mins=self.get_title_length_in_mins(),
            storyline=self.get_title_storyline(),
            tagline=self.get_title_tagline()
        )

    def get_person_contents(self) -> Person:
        """
        Scrapes an IMDb name page for contents.

        Returns:
            A Person object containing all the scraped data.
        """
        self.logger.info(f"Getting person contents from {self.first_result_url}")
        return Person(name=self.get_person_name(), date_of_birth=self.get_person_dob(), bio=self.get_person_bio())

    def get_title_relation_contents(self) -> dict:
        """
        Scrapes an IMDb title page for contents regarding it's relationships.

        Returns:
            A dict object containing all the scraped data.
        """
        self.logger.info(f"Getting title relation contents from {self.first_result_url}")
        return {
            "directors": self.get_title_directors(),
            "writers": self.get_title_writers(),
            "producers": self.get_title_producers(),
            "genres": self.get_title_genres(),
            "cast": self.get_title_cast()
        }

    def get_person_relation_contents(self):
        """
        Scrapes an IMDb name page for contents regarding it's relationships.

        Returns:
            A dict object containing all the scraped data.
        """
        self.logger.info(f"Getting person relation contents from {self.first_result_url}")
        return {
            "Academy Awards": self.get_awards_for_organisation(AwardOrganisation.ACADEMY_AWARDS.value),
            "Golden Globes": self.get_awards_for_organisation(AwardOrganisation.GOLDEN_GLOBES.value),
            "BAFTA Awards": self.get_awards_for_organisation(AwardOrganisation.BAFTA_AWARDS.value),
        }

    def set_search_url(self, query: str):
        """
        Constructs an IMDB search URL for the given query string and sets it to the 'search_page_url' instance
        attribute.

        Args:
            query: The name of the item to search IMDB for e.g. 'Leonardo DiCaprio' or 'Inception'
        """
        query_word_list = query.lower().split(' ')
        part_search_term = ""
        for tw in query_word_list[:-1]:
            part_search_term = part_search_term + tw + "+"
        search_url = BASE_URL + SEARCH_PREFIX + part_search_term + query_word_list[-1] + SEARCH_SUFFIX
        self.search_page_url = search_url

    def set_first_result_url(self):
        """
        Scans the page of IMDB search results and generates a url to the page of the first result.
        """
        if SEARCH_SUFFIX not in self.search_page_url:
            raise Exception("An IMDb search page is not loaded. Cannot create first_result_url.")

        search_results = requests.get(self.search_page_url)
        self.soup = BeautifulSoup(search_results.content, 'html.parser')

        search_results_table = self.soup.find(class_="findList")
        first_result = search_results_table.find_all('a')[0]
        result_suffix = first_result.get('href')
        result_suffix = result_suffix[:result_suffix.rfind('/')+1]
        first_result_url = BASE_URL + result_suffix
        self.first_result_url = first_result_url

    def set_full_credits_url(self):
        """
        Sets the full_credits_url so title relationship data can be scraped.
        """
        if TITLE_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb title page is not loaded. Cannot create full_credits_url.")
        self.full_credits_url = self.first_result_url + FULL_CREDITS_SUFFIX

    def set_awards_url(self):
        """
        Sets the awards_url so person relationship data can be scraped.
        """
        if NAME_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb name page is not loaded. Cannot create awards_url")
        self.awards_url = self.first_result_url + AWARDS_SUFFIX

    def set_bio_url(self):
        """
        Sets the bio_url so person relationship data can be scraped.
        """
        if NAME_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb name page is not loaded. Cannot create bio_url")
        self.bio_url = self.first_result_url + BIO_SUFFIX

    def get_title_name(self) -> str:
        """
        Extracts the name from any given title page i.e. a Movie or TV show.

        Returns:
            A string containing the name of the loaded title page.
        """
        if TITLE_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb title page is not loaded. Cannot extract title name.")
        self.__load_soup_with_first_result_page()
        headers = self.soup.find_all("h1")
        return headers[0].contents[0].string.strip()

    def get_title_summary(self) -> str:
        """
        Extracts the summary from any given title page i.e. a Movie or TV show.

        Returns:
            A string containing the summary of the loaded title page.
        """
        if TITLE_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb title page is not loaded. Cannot extract title summary.")
        self.__load_soup_with_first_result_page()
        title_summary = self.soup.find(class_="summary_text")
        summary_string = ""
        for item in title_summary.contents:
            summary_string += self.__remove_html_elements_from_string(item.string)
        summary_string = ' '.join(summary_string.split())
        return summary_string

    def get_title_release_year(self) -> int:
        """
        Extracts the release year from any given title page i.e. a Movie or TV show.

        Returns:
            A integer representing the release year of the loaded title page.
        """
        if TITLE_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb title page is not loaded. Cannot extract title release year.")
        self.__load_soup_with_first_result_page()
        title_year = self.soup.find(id="titleYear")
        return int(title_year.find('a').text.strip())

    def get_title_certificate_rating(self) -> str:
        """
        Extracts the certificate rating from any given title page i.e. a Movie or TV show.

        Returns:
            A string containing the certificate rating of the loaded title page.
        """
        if TITLE_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb title page is not loaded. Cannot extract title certificate rating.")
        self.__load_soup_with_first_result_page()
        subtext = self.soup.find(class_="subtext")
        return str(subtext.contents[0]).replace("\n", "").strip()

    def get_title_length_in_mins(self) -> int:
        """
        Extracts the title length in minutes from any given title page i.e. a Movie or TV show.

        Returns:
            A integer representing the length of the title in minutes of the loaded title page.
        """
        if TITLE_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb title page is not loaded. Cannot extract title length in minutes.")
        self.__load_soup_with_first_result_page()
        subtext = self.soup.find(class_="subtext")
        film_length_str = subtext.find('time').text.strip()
        return self.__parse_title_length(film_length_str)

    def get_title_storyline(self) -> str:
        """
        Extracts the storyline from any given title page i.e. a Movie or TV show.

        Returns:
            A string containing the storyline of the loaded title page.
        """
        if TITLE_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb title page is not loaded. Cannot extract title storyline.")
        self.__load_soup_with_first_result_page()
        storyline = self.soup.find(class_="inline canwrap")
        storyline_raw = self.__remove_html_elements_from_string(storyline.contents[1].text)
        storyline_clean = storyline_raw.strip().replace("\n", " ")
        return storyline_clean

    def get_title_tagline(self) -> str:
        """
        Extracts the tagline from any given title page i.e. a Movie or TV show.

        Returns:
            A string containing the tagline of the loaded title page.
        """
        if TITLE_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb title page is not loaded. Cannot extract title tagline.")
        self.__load_soup_with_first_result_page()
        txt_block_tags = self.soup.findAll("div", {"class": "txt-block"})
        raw_tagline = self.__remove_html_elements_from_string(txt_block_tags[0].text)
        start = raw_tagline.find("Taglines:") + len("Taglines:")
        end = raw_tagline.find("See more")
        tagline_clean = raw_tagline[start:end].strip()
        return tagline_clean

    def get_title_genres(self) -> list:
        """
        Extracts the list of genres from any given title page i.e. a Movie or TV show.

        Returns:
            A list of genres relating to the loaded title page.
        """
        if TITLE_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb title page is not loaded. Cannot extract title genres.")
        self.__load_soup_with_first_result_page()
        subtext = self.soup.find_all(class_="see-more inline canwrap")[1]
        potential_genres = subtext.find_all('a')
        genres = []
        for pg in potential_genres:
            if 'genre' in pg['href']:
                genres.append(pg.text.strip())
        return genres

    def get_title_cast(self) -> dict:
        """
        Extracts the main cast from any given title page i.e. a Movie or TV show.

        Returns:
            A dict containing the cast of the loaded title page. The keys are actors names and the values are the
            character(s) they played in the loaded title page.
        """
        if TITLE_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb title page is not loaded. Cannot extract title cast.")

        cast_list_table = self.soup.find(class_="cast_list")
        cast_trs = cast_list_table.find_all('tr')

        cast_map = {}
        for member in cast_trs:
            cast_tds = member.find_all('td')
            if self.__main_cast_obtained(cast_tds):
                break
            if len(cast_tds) > 1:
                actor_name, character = self.__extract_actor_and_character(cast_tds)
                cast_map[actor_name] = character
        return cast_map

    def get_title_directors(self) -> list:
        """
        Extracts the director(s) from any given IMDb title (Movie or TV show) full credits page.

        Returns:
            A list of strings containing the director(s) name(s).
        """
        if TITLE_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb title page is not loaded. Cannot extract title director(s).")
        self.__load_soup_with_full_credits_page()

        director_credits = self.__get_table_for(block="fullcredits_content", header="Directed by")
        director_anchors = director_credits.find_all("a")

        return [x.contents[0].string.strip() for x in director_anchors]

    def get_title_writers(self) -> dict:
        """
        Extracts the writer(s) from any given IMDb title (Movie or TV show) full credits page.

        Returns:
            A list of strings containing the writer(s) name(s).
        """
        if TITLE_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb title page is not loaded. Cannot extract title writer(s).")

        self.__load_soup_with_full_credits_page()
        writer_credits = self.__get_table_for(block="fullcredits_content", header="Writing Credits")

        writer_name_anchors = writer_credits.find_all("a")
        writer_role_tags = writer_credits.find_all(class_="credit")

        writer_names = [x.contents[0].string.strip() for x in writer_name_anchors]
        writer_roles = [self.__extract_role(x.contents[0].string) for x in writer_role_tags]

        return self.__zip_names_and_roles(writer_names, writer_roles)

    def get_title_producers(self) -> dict:
        """
        Extracts the producer(s) from any given IMDb title (Movie or TV show) full credits page.

        Returns:
            A list of strings containing the writer(s) name(s).
        """
        if TITLE_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb title page is not loaded. Cannot extract title producer(s).")
        self.__load_soup_with_full_credits_page()
        producer_credits = self.__get_table_for(block="fullcredits_content", header="Produced by")

        producer_name_anchors = producer_credits.find_all("a")
        producer_role_tags = producer_credits.find_all(class_="credit")

        producer_names = [x.contents[0].string.strip() for x in producer_name_anchors]
        producer_roles = [x.contents[0].string.strip() for x in producer_role_tags]

        return self.__zip_names_and_roles(producer_names, producer_roles)

    def get_person_name(self) -> str:
        """
        Extracts a person's name from any given IMDb name main page.

        Returns:
            A string containing the name of the person.
        """
        if NAME_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb name page is not loaded. Cannot extract person name.")
        self.__load_soup_with_first_result_page()
        headers = self.soup.find_all("h1")
        item_prop = headers[0].find(class_="itemprop")
        return item_prop.contents[0].string.strip()

    def get_person_dob(self) -> datetime:
        """
        Extracts a person's date of birth from any given IMDb name main page.

        Returns:
            A datetime object containing the date of birth of the person.
        """
        if NAME_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb name page is not loaded. Cannot extract person date of birth.")
        self.__load_soup_with_first_result_page()
        date_info = self.soup.find("time")
        if date_info is None:
            self.logger.error(f"Could not extract person date of birth from {self.first_result_url}.")
            raise ParseError("Could not extract person date of birth.")
        dob_str = date_info["datetime"]
        year, month, day = dob_str.split("-")
        return datetime(year=int(year), month=int(month), day=int(day))

    def get_person_bio(self) -> str:
        """
        Extracts a person's bio from any given IMDb name main page.

        Returns:
            A str containing the bio of the person.
        """
        if NAME_SIGNATURE not in self.first_result_url:
            raise Exception("An IMDb name page is not loaded. Cannot extract person date of birth.")
        self.__load_soup_with_bio_page()
        bio_block = self.soup.find(class_="soda odd")
        raw_bio = bio_block.find("p").contents
        bio_list = [str(x) for x in raw_bio]
        bio = "".join(bio_list)
        bio = bio.replace("<br>", "\n").replace("<br/>", "\n").replace("</br>", "\n").strip()
        bio = self.__remove_html_elements_from_string(bio)
        return bio

    def get_awards_for_organisation(self, organisation: str) -> list:
        """
        Extracts a person's awards for a given organisation e.g. Academy Awards from any given IMDb name awards page.

        Returns:
            A list of 'Award' objects.
        """
        if NAME_SIGNATURE not in self.awards_url:
            raise Exception("An IMDb name awards page is not loaded. Cannot extract {0}.".format(organisation))
        self.__load_soup_with_awards_page()
        awards = []
        awards_table = self.__get_table_for(block="article listo", header=organisation)
        award_items = awards_table.find_all("tr")
        ay_marker, ao_marker = 0, ""
        for i in range(0, len(award_items)):
            award_name = award_items[i].find(class_="award_description").contents[0].string.strip()
            if award_name is None or award_name == "":
                award_name = award_items[i].find(class_="award_category").contents[0].string.strip()
            award_year, ay_marker = self.__set_award_year(award_items[i], ay_marker)
            award_outcome, ao_marker = self.__set_award_outcome(award_items[i], ao_marker)
            award_title_row = award_items[i].find("a", href=re.compile("title"))
            if award_title_row is None:
                continue
            award_title_name = award_title_row.contents[0].string.strip()
            award_title_release = int(
                award_items[i].find(class_="title_year").contents[0].string.strip().replace('(', '').replace(')', ''))
            awards.append(Award(name=award_name, outcome=award_outcome, year=award_year, title_name=award_title_name,
                                title_released=award_title_release))
        return awards

    def __initialise_soup_and_urls(self, query: str):
        """
        Sets the search url, the first result url and loads the soup object with the HTML of the first result.

        Args:
            query: The search term used to generate the IMDb URLs.
        """
        self.set_search_url(query)
        self.set_first_result_url()
        self.__load_soup_with_first_result_page()

    def __load_soup_with_first_result_page(self):
        if (NAME_SIGNATURE not in self.first_result_url) and (TITLE_SIGNATURE not in self.first_result_url):
            raise Exception("An IMDb name or title page is not loaded. Cannot load soup with first_result_url.")
        first_result_page = requests.get(self.first_result_url)
        self.soup = BeautifulSoup(first_result_page.content, 'html.parser')

    def __load_soup_with_bio_page(self):
        if NAME_SIGNATURE not in self.awards_url:
            raise Exception("An IMDb name page is not loaded. Cannot load soup with bio_url.")
        bio_page = requests.get(self.bio_url)
        self.soup = BeautifulSoup(bio_page.content, 'html.parser')

    def __load_soup_with_full_credits_page(self):
        if TITLE_SIGNATURE not in self.full_credits_url:
            raise Exception("An IMDb title page is not loaded. Cannot load soup with full_credits_url.")
        full_credits_page = requests.get(self.full_credits_url)
        self.soup = BeautifulSoup(full_credits_page.content, 'html.parser')

    def __load_soup_with_awards_page(self):
        if NAME_SIGNATURE not in self.awards_url:
            raise Exception("An IMDb name page is not loaded. Cannot load soup with awards_url.")
        awards_page = requests.get(self.awards_url)
        self.soup = BeautifulSoup(awards_page.content, 'html.parser')

    def __get_table_for(self, block: str, header: str):
        """
        Extracts a block from the HTML loaded into the soup object as defined by its 'id' or 'class' and then
        extracts a table pertaining to a particular header on the IMDb page.

        Args:
            block: The html block the table of interested is located in.
            header: The header of the table.

        Returns:
            A soup ResultSet containing the table desired.
        """
        if "credit" in block:
            table_block = self.soup.find(id=block)
        elif "article listo" in block:
            table_block = self.soup.find(class_=block)
        for i in range(0, len(table_block.contents)):
            if header in str(table_block.contents[i]):
                return table_block.contents[i + 2]

        raise Exception("Could not find table for header: " + header)

    @staticmethod
    def __set_award_year(award_item, ay_marker) -> (int, int):
        """
        A method to help with the parsing of award information. An award year marker ('ay_marker') is kept in the
        event a person is up for multiple awards in the same year and parsing of the table does not follow the
        typical row by row format.

        Args:
            award_item: The soup item representing a row on the awards table.
            ay_marker: A year marker to use as a fallback for year assignment in the event of multiple award
                win/nominations in one year.

        Returns:
            The parsed award year and the award year marker.
        """
        try:
            award_year = int(award_item.find("a", href=re.compile("event")).contents[0].string.strip())
            ay_marker = award_year
        except:
            if ay_marker != 0:
                award_year = ay_marker
            else:
                raise ParseError("Unable to parse award year")
        return award_year, ay_marker

    @staticmethod
    def __set_award_outcome(award_item, ao_marker) -> (str, str):
        """
        A method to help with the parsing of award information. An award outcome marker ('ao_marker') is kept in the
        event a person is up for multiple awards in the same year and parsing of the table does not follow the
        typical row by row format.

        Args:
            award_item: The soup item representing a row on the awards table.
            ay_marker: An outcome marker to use as a fallback for outcome assignment in the event of multiple award
                win/nominations in one year.

        Returns:
            The parsed award outcome and the award outcome marker.
        """
        try:
            award_outcome = award_item.find(class_="award_outcome").contents[1].contents[0].string.strip()
            ao_marker = award_outcome
        except:
            if ao_marker != "":
                award_outcome = ao_marker
            else:
                raise ParseError("Unable to parse award outcome")
        return award_outcome, ao_marker

    @staticmethod
    def __main_cast_obtained(cast_td) -> bool:
        """
        A method to determine when to stop parsing the cast. This will prevent a bloated database as only the most
        relevant cast will be stored.

        Args:
            cast_tds: An HTML <td> object containing a cast member or a string denoting where the rest of the cast
                will be listed alphabetically from here on in.

        Returns:
            A bool to determine whether all of the main cast has been scraped yet or not.
        """
        if len(cast_td) == 1:
            try:
                if "Rest of cast listed alphabetically:" in cast_td[0].contents[0].strip():
                    return True
            except Exception as e:
                pass
        return False

    @staticmethod
    def __extract_actor_and_character(cast_td) -> (str, list):
        """
        A method that extracts an actor name and character list from an IMDb cast table row.

        Args:
            cast_td: An HTML <td> object containing a cast member and their portrayed character(s) for a particular
            title.

        Returns:
            The actor name in a string and a list of strings of portrayed characters.
        """
        actor_name = cast_td[1].find('a').string.replace("\n", "").strip()
        try:
            character = [c.string.strip() for c in cast_td[3].find_all('a')]
        except:
            character = [cast_td[3].contents[0].strip()]
        return actor_name, character

    @staticmethod
    def __extract_role(string: str) -> str:
        """
        Extracts the role of a person from it's parentheses.

        Args:
            string: The role of a person wrapped in parentheses e.g. (producer)

        Returns:
            The role of a person free from it's parentheses e.g. producer
        """
        start = string.find('(')
        end = string.find(')')
        return string[start+1:end]

    @staticmethod
    def __zip_names_and_roles(names: list, roles: list) -> dict:
        """
        Given a lists people names and roles, they are zipped to form a dict of names (key) and lists of roles (value).
        The ith name in names has their role in the ith index of roles. Given the same name in names, a list of roles
        with length > 1 will be formed.

        Args:
            names: A list of people names.
            roles: A list of people roles.

        Returns:
            A zipped dict of names (key) to list of roles (value).
        """
        writer_map = {}
        len_wn, len_wr = len(names), len(roles)
        if len_wn != len_wr:
            raise ValueError("Length of writer names: {0} is not equal to length of writer roles: {1}".format(
                len_wn, len_wr))
        for i in range(0, len_wn):
            name, role = names[i], roles[i]
            if writer_map.get(name):
                writer_map[name].append(role)
            else:
                writer_map[name] = [role]

        return writer_map

    @staticmethod
    def __parse_title_length(title_length: str) -> int:
        """
        A private function to parse the film length string obtained from an IMDB title page and
        represent it as an integer of film length in minutes.

        Args:
            title_length: A string representing title length in format '1h 23min'

        Returns:
            An integer representing the title length in minutes.
        """
        hrs_and_mins = title_length.split(' ')
        hrs, mins = ("", "")
        for i in range(0, len(hrs_and_mins)):
            if "h" in hrs_and_mins[i]:
                hrs = hrs_and_mins[i].replace("h", "")
            elif "min" in hrs_and_mins[i]:
                mins = hrs_and_mins[i].replace("min", "")
        hrs_int = int(hrs) if hrs else 0
        mins_int = int(mins) if mins else 0

        return (hrs_int * 60) + mins_int

    @staticmethod
    def __remove_html_elements_from_string(string: str):
        """
        A private function that removes all html tags from a given string.

        Args:
            string: The string that requires the removal of HTML tags.

        Returns:
            A new HTML tag-free string.
        """
        start = string.find('<')
        end = string.find('>')
        while start != -1 and end != -1:
            string = string[:start] + string[end + 1:]
            start = string.find('<')
            end = string.find('>')
        return string

from src.scraper.imdb_scraper import IMDbScraper

import json
import mock
import os
import pytest
import sys

IMDB_TITLE_PATH = os.path.join(sys.path[0], "test/resources/imdb_pages/title/")
IMDB_NAME_PATH = os.path.join(sys.path[0], "test/resources/imdb_pages/name/")
EXPECTED_RESULTS_PATH = os.path.join(sys.path[0], "test/resources/expected_results/")


def get_imdb_page(filepath: str):
    f = open(filepath, "r")
    return f.read()


def _mock_response(status=200, content="CONTENT", json_data=None, raise_for_status=None):
    mock_resp = mock.Mock()
    mock_resp.raise_for_status = mock.Mock()
    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status
    mock_resp.status_code = status
    mock_resp.content = content
    if json_data:
        mock_resp.json = mock.Mock(return_value=json_data)
    return mock_resp


@pytest.fixture
def scraper():
    return IMDbScraper()


@pytest.fixture
def expected_title_contents():
    with open(EXPECTED_RESULTS_PATH+"titles.json") as json_file:
        return json.load(json_file)


@pytest.fixture
def expected_name_contents():
    with open(EXPECTED_RESULTS_PATH+"names.json") as json_file:
        return json.loads(json_file.read())


@pytest.fixture
def mock_req_title(request):
    if request.param == "wows":
        return {
            "main": _mock_response(status=200, content=get_imdb_page(IMDB_TITLE_PATH + "wolf_of_wall_st_main.htm")),
            "credits": _mock_response(status=200,
                                      content=get_imdb_page(IMDB_TITLE_PATH + "wolf_of_wall_st_credits.htm")),
            "search": _mock_response(status=200, content=get_imdb_page(IMDB_TITLE_PATH + "wolf_of_wall_st_search.htm"))
        }
    elif request.param == "dk":
        return {
            "search": _mock_response(status=200,
                                     content=get_imdb_page(IMDB_TITLE_PATH + "the_dark_knight_search.htm")),
            "main": _mock_response(200, get_imdb_page(IMDB_TITLE_PATH + "the_dark_knight_main.htm")),
            "credits": _mock_response(200, get_imdb_page(IMDB_TITLE_PATH + "the_dark_knight_credits.htm"))
        }
    elif request.param == "ae":
        return {
            "search": _mock_response(status=200,
                                     content=get_imdb_page(IMDB_TITLE_PATH + "avengers_endgame_search.htm")),
            "main": _mock_response(status=200, content=get_imdb_page(IMDB_TITLE_PATH + "avengers_endgame_main.htm")),
            "credits": _mock_response(status=200,
                                      content=get_imdb_page(IMDB_TITLE_PATH + "avengers_endgame_credits.htm"))
        }


@pytest.fixture
def mock_req_name(request):
    if request.param == "ld":
        return {
            "search": _mock_response(status=200,
                                     content=get_imdb_page(IMDB_NAME_PATH + "leonardo_dicaprio_search.htm")),
            "main": _mock_response(status=200,
                                   content=get_imdb_page(IMDB_NAME_PATH + "leonardo_dicaprio_main.htm")),
            "awards": _mock_response(status=200,
                                     content=get_imdb_page(IMDB_NAME_PATH + "leonardo_dicaprio_awards.htm"))
        }
    elif request.param == "cb":
        return {
            "search": _mock_response(status=200,
                                     content=get_imdb_page(IMDB_NAME_PATH + "christian_bale_search.htm")),
            "main": _mock_response(status=200, content=get_imdb_page(IMDB_NAME_PATH + "christian_bale_main.htm")),
            "awards": _mock_response(status=200,
                                     content=get_imdb_page(IMDB_NAME_PATH + "christian_bale_awards.htm"))
        }
    elif request.param == "gp":
        return {
            "search": _mock_response(status=200,
                                     content=get_imdb_page(IMDB_NAME_PATH + "gwyneth_paltrow_search.htm")),
            "main": _mock_response(status=200, content=get_imdb_page(IMDB_NAME_PATH + "gwyneth_paltrow_main.htm")),
            "awards": _mock_response(status=200,
                                     content=get_imdb_page(IMDB_NAME_PATH + "gwyneth_paltrow_awards.htm"))
        }


@pytest.mark.parametrize("mock_req_title, query", [("ae", "Avengers Endgame"), ("wows", "The Wolf of Wall Street"),
                                                   ("dk", "The Dark Knight")], indirect=["mock_req_title"])
@mock.patch('requests.get')
def test_load_title_page(mock_request_get, scraper, expected_title_contents, mock_req_title, query):
    mock_request_get.side_effect = [mock_req_title['search'], mock_req_title['main']]
    expected = expected_title_contents[query]
    scraper.load_title_page(query)
    assert (scraper.search_page_url == expected["search_uri"])
    assert (scraper.first_result_url == expected["main_uri"])
    assert (scraper.full_credits_url == expected["credits_uri"])


@pytest.mark.parametrize("mock_req_title, query", [("ae", "Avengers Endgame"), ("wows", "The Wolf of Wall Street"),
                                                   ("dk", "The Dark Knight")], indirect=["mock_req_title"])
@mock.patch('requests.get')
def test_get_title_contents(mock_request_get, scraper, expected_title_contents, mock_req_title, query):
    mock_request_get.side_effect = [mock_req_title['search']] + [mock_req_title['main']] * 8
    expected = expected_title_contents[query]["contents"]
    scraper.load_title_page(query)
    title = scraper.get_title_contents()
    assert(title.__dict__ == expected)


@pytest.mark.parametrize("mock_req_title, query", [("ae", "Avengers Endgame"), ("wows", "The Wolf of Wall Street"),
                                                   ("dk", "The Dark Knight")], indirect=["mock_req_title"])
@mock.patch('requests.get')
def test_get_title_relation_contents(mock_request_get, scraper, expected_title_contents, mock_req_title, query):
    mock_request_get.side_effect = [mock_req_title['search'], mock_req_title['main'], mock_req_title['credits'],
                                    mock_req_title['credits'], mock_req_title['credits'], mock_req_title['main'],
                                    mock_req_title['main']]
    expected = expected_title_contents[query]["relations"]
    scraper.load_title_page(query)
    title_relations = scraper.get_title_relation_contents()
    assert(title_relations == expected)


@pytest.mark.parametrize("mock_req_name, query", [("ld", "Leonardo DiCaprio"), ("cb", "Christian Bale"),
                                                   ("gp", "Gwyneth Paltrow")], indirect=["mock_req_name"])
@mock.patch('requests.get')
def test_load_person_page(mock_request_get, scraper, expected_name_contents, mock_req_name, query):
    mock_request_get.side_effect = [mock_req_name['search'], mock_req_name['main']]
    expected = expected_name_contents[query]
    scraper.load_person_page(query)
    assert (scraper.search_page_url == expected["search_uri"])
    assert (scraper.first_result_url == expected["main_uri"])
    assert (scraper.awards_url == expected["awards_uri"])


@pytest.mark.parametrize("mock_req_name, query", [("ld", "Leonardo DiCaprio"), ("cb", "Christian Bale"),
                                                   ("gp", "Gwyneth Paltrow")], indirect=["mock_req_name"])
@mock.patch('requests.get')
def test_get_person_contents(mock_request_get, scraper, expected_name_contents, mock_req_name, query):
    mock_request_get.side_effect = [mock_req_name["search"]] + [mock_req_name["main"]] * 3
    expected = expected_name_contents[query]["contents"]
    scraper.load_person_page(query)
    person = scraper.get_person_contents()
    assert (person.name == expected["name"])
    assert (person.get_dob("%d-%b-%Y") == expected["date_of_birth"])


@pytest.mark.parametrize("mock_req_name, query", [("ld", "Leonardo DiCaprio"), ("cb", "Christian Bale"),
                                                   ("gp", "Gwyneth Paltrow")], indirect=["mock_req_name"])
@mock.patch('requests.get')
def test_get_person_relation_contents(mock_request_get, scraper, expected_name_contents, mock_req_name, query):
    mock_request_get.side_effect = [mock_req_name["search"]] + [mock_req_name["main"]] + [mock_req_name["awards"]] * 3
    expected = expected_name_contents[query]["relations"]
    scraper.load_person_page(query)
    person_relations = scraper.get_person_relation_contents()
    for i in range(len(person_relations["Academy Awards"])):
        assert(person_relations["Academy Awards"][i].__dict__ == expected["Academy Awards"][i])
    for i in range(len(person_relations["Golden Globes"])):
        assert(person_relations["Golden Globes"][i].__dict__ == expected["Golden Globes"][i])
    for i in range(len(person_relations["BAFTA Awards"])):
        assert(person_relations["BAFTA Awards"][i].__dict__ == expected["BAFTA Awards"][i])

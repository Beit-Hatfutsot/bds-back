# -*- coding: utf-8 -*-
from common import *
from mocks import MOVIES_SPAIN
from copy import deepcopy


def test_from_search_to_item(client, app):
    movie = deepcopy(MOVIES_SPAIN)
    movie["slug_en"] = "video_spain-2"
    movie["slug_he"] = "וידאו_רגעים-ספרד-2"
    movie["slugs"] = [movie["slug_en"], movie["slug_he"]]
    movie["source_id"] = "666"
    given_local_elasticsearch_client_with_test_data(app, "test_item::test_search_to_item", additional_index_docs={"movies": [movie]})
    res = client.get("/v1/search?q=Living+Moments+in+Jewish+Spain")
    # we have 2 matches, need to get the right onw
    assert len(res.json["hits"]) == 2
    hits = {hit["source_id"]: hit for hit in res.json["hits"]}
    # these are the slugs we get from search and will be used to link to the item
    assert hits["130323"]["slugs"] == [u'video_living-moments-in-jewish-spain', u'וידאו_רגעים-עם-יהודי-ספרד']
    assert hits["130323"]["slug_en"] == u'video_living-moments-in-jewish-spain'
    assert hits["130323"]["slug_he"] == u'וידאו_רגעים-עם-יהודי-ספרד'
    for slug in hits["130323"]["slugs"]:
        items = assert_client_get(client, u"/v1/item/{}".format(slug))
        assert len(items) == 1
        item = items[0]
        assert item["collection"] == "movies"
        assert item["title_en"] == "Living Moments in Jewish Spain (English jews)"
    for slug in hits["666"]["slugs"]:
        items = assert_client_get(client, u"/v1/item/{}".format(slug))
        assert len(items) == 1
        item = items[0]
        assert item["collection"] == "movies"
        assert item["title_en"] == "Living Moments in Jewish Spain (English jews)"

def test_item_embedded_google_map(client, app):
    given_local_elasticsearch_client_with_test_data(app, "test_item::test_item_embedded_google_map",
                                                    additional_index_docs={"places": [PLACES_GERMANY]})
    res = assert_client_get(client, u"/v1/item/place_germany")
    assert res[0]["google_map_embed"] == "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3639100.5693534394!2d7.6804282320147825!3d50.96213621113465!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x479a721ec2b1be6b%3A0x75e85d6b8e91e55b!2sGermany!5e0!3m2!1sen!2sil!4v1498978137451"


# import pytest
# from bhs_api.item import enrich_item
# from pytest_flask.plugin import client
# The documentation for client is at http://werkzeug.pocoo.org/docs/0.9/test/
# TODO: re-enable when item API is modified for new data schema
def skip_test_enrich_item(app, mock_db):
    with app.app_context():
        item = enrich_item({'Pictures':
                        [
                            { 'IsPreview': 1, 'PictureId': 'ID' },
                        ],
                    },
                    mock_db)
    assert item['main_image_url'] == \
               'https://storage.googleapis.com/bhs-flat-pics/ID.jpg'
    assert item['thumbnail_url'] == \
               'https://storage.googleapis.com/bhs-thumbnails/ID.jpg'

# TODO: re-enable when item API is modified for new data schema
def skip_test_enrich_item_no_preview(app, mock_db):
    with app.app_context():
        item = enrich_item({'Pictures':
                        [
                            { 'IsPreview': 0, 'PictureId': 'ID' },
                        ],
                    },
                    mock_db)
    assert item['main_image_url'] == \
               'https://storage.googleapis.com/bhs-flat-pics/ID.jpg'

# TODO: re-enable when item API is modified for new data schema
def skip_test_enrich_item_no_pictures(app, mock_db):
    with app.app_context():
        item = enrich_item({}, mock_db)
    assert 'main_image_url' not in item

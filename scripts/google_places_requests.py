import requests
import json
import time


class GooglePlaces(object):
    def __init__(self, apiKey):
        super(GooglePlaces, self).__init__()
        self.apiKey = apiKey

    # Text search URL
    # url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

    # Nearby search URL Example
    # https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=28.4810971,-81.5089239&radius=1500&type=restaurant&key=
    def search_places_by_coordinate(self, location, radius, types):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        places = []
        params = {
            "location": location,
            "radius": radius,
            "types": types,
            "key": self.apiKey,
        }
        headers = {
            "content-type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:63.0) Gecko/20100101 Firefox/63.0",
        }
        res = requests.get(endpoint_url, params=params, headers=headers)
        results = json.loads(res.content)
        places.extend(results["results"])
        time.sleep(3)
        while "next_page_token" in results:
            params["pagetoken"] = (results["next_page_token"],)
            res = requests.get(endpoint_url, params=params, headers=headers)
            results = json.loads(res.content)
            places.extend(results["results"])
            time.sleep(3)
        return places

    def get_place_details(self, place_id, fields):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {"placeid": place_id, "fields": ",".join(fields), "key": self.apiKey}
        headers = {
            "content-type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:63.0) Gecko/20100101 Firefox/63.0",
        }
        res = requests.get(endpoint_url, params=params, headers=headers)
        place_details = json.loads(res.content)
        return place_details


if __name__ == "__main__":
    api = GooglePlaces("Your API key")
    places = api.search_places_by_coordinate(
        "28.4810971,-81.5089239", "100", "restaurant"
    )
    fields = [
        "name",
        "formatted_address",
        "international_phone_number",
        "website",
        "rating",
        "review",
    ]
    for place in places:
        details = api.get_place_details(place["place_id"], fields)
        try:
            website = details["result"]["website"]
        except KeyError:
            website = ""

        try:
            name = details["result"]["name"]
        except KeyError:
            name = ""

        try:
            address = details["result"]["formatted_address"]
        except KeyError:
            address = ""

        try:
            phone_number = details["result"]["international_phone_number"]
        except KeyError:
            phone_number = ""

        try:
            reviews = details["result"]["reviews"]
        except KeyError:
            reviews = []
        print("===================PLACE===================")
        print("Name:", name)
        print("Website:", website)
        print("Address:", address)
        print("Phone Number", phone_number)
        print("==================REVIEWS==================")
        for review in reviews:
            author_name = review["author_name"]
            rating = review["rating"]
            text = review["text"]
            time = review["relative_time_description"]
            profile_photo = review["profile_photo_url"]
            print("Author Name:", author_name)
            print("Rating:", rating)
            print("Text:", text)
            print("Time:", time)
            print("Profile photo:", profile_photo)
            print("-----------------------------------------")

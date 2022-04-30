import os
import requests
import json
from util import get_data, read_file, write_file

DISTRICT_CODES = {
    "黄浦区":	"310101",
    "徐汇区":	"310104",
    "长宁区":	"310105",
    "静安区":	"310106",
    "普陀区":	"310107",
    "虹口区":	"310109",
    "杨浦区":	"310110",
    "闵行区":	"310112",
    "宝山区":	"310113",
    "嘉定区":	"310114",
    "浦东新区":	"310115",
    "金山区":	"310116",
    "松江区":	"310117",
    "青浦区":	"310118",
    "奉贤区":	"310120",
    "崇明区":	"310151"
}

geo_cached_filename = "data/place/geo_cached.json"
places_filename = "data/place/places.json"
key = os.environ.get("AMAP_KEY")


def get_places():
    # if os.path.exists(places_filename):
    #     return json.loads(read_file(places_filename))

    return []


def save_places(places):
    write_file(json.dumps(places, ensure_ascii=False, indent=4,
               separators=(',', ':')), places_filename)


def get_geo_cached():
    if os.path.exists(geo_cached_filename):
        return json.loads(read_file(geo_cached_filename))

    return {}


def save_geo_cached(geo_cached):
    write_file(json.dumps(geo_cached, ensure_ascii=False, indent=4,
               separators=(',', ':')), geo_cached_filename)


def geocode_geo(district_code, address):
    """
    Geocode an address using the Geo API
    """
    url = f"https://restapi.amap.com/v3/geocode/geo?key={key}&address={address}&adcode={district_code}&output=JSON"
    r = requests.get(url)
    if r.status_code != 200:
        return False, 0, 0

    geo_res = r.json()

    try:
        localtion = geo_res['geocodes'][0]['location']
        point = localtion.split(',')
        return True, point[0], point[1]
    except KeyError or IndexError:
        return False, 0, 0


def generate_places(cases=[]):
    geo_cached = get_geo_cached()
    places = get_places()
    for case in cases:
        date = case["date"]
        districts = case["districts"]
        for district in districts:
            district_name = district["district_name"]
            print(f"\n{district_name}@{date}:")
            for place_name in district["places"]:
                if place_name in geo_cached:
                    point = geo_cached[place_name]
                    lng = point["lng"]
                    lat = point["lat"]
                else:
                    (ret, lng, lat) = geocode_geo(
                        DISTRICT_CODES[district_name], place_name)
                    if ret:
                        geo_cached[place_name] = dict(lng=lng, lat=lat)
                place = dict(date=date, district_name=district_name,
                             place_name=place_name, lng=lng, lat=lat)
                places.append(place)
                print(place)

    save_geo_cached(geo_cached)
    save_places(places)


if __name__ == "__main__":
    cases = get_data()
    generate_places(cases)

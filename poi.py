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


def get_geo_cached():
    if os.path.exists(geo_cached_filename):
        return json.loads(read_file(geo_cached_filename))

    return {}


def geocode_geo(key, district_code, address):
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


if __name__ == "__main__":
    key = os.environ.get("AMAP_KEY")

    cases = get_data()
    geo_cached = get_geo_cached()
    for case in cases:
        date = case["date"]
        districts = case["districts"]
        for district in districts:
            district_name = district["district_name"]
            print(f"\n{district_name}@{date}:")
            for place in district["places"]:
                if place in geo_cached:
                    point = geo_cached[place]
                    lng = point["lng"]
                    lat = point["lat"]
                else:
                    (ret, lng, lat) = geocode_geo(
                        key, DISTRICT_CODES[district_name], place)
                    if ret:
                        geo_cached[place] = dict(lng=lng, lat=lat)
                print(f"{place}: {lng},{lat}")

    write_file(json.dumps(geo_cached, ensure_ascii=False, indent=4,
               separators=(',', ':')), geo_cached_filename)

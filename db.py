import os
import csv
import peewee
from peewee import DatabaseProxy, Model, SqliteDatabase
from util import get_data, get_place_data, get_overview_data
from openpyxl import Workbook

database_proxy = DatabaseProxy()


class Base(Model):
    class Meta:
        database = database_proxy
        legacy_table_names = False


class Overview(Base):
    id = peewee.AutoField()
    date = peewee.DateField(null=False, index=True)
    total = peewee.IntegerField(null=False)
    confirmed = peewee.IntegerField(null=False)
    asymptomatic = peewee.IntegerField(null=False)
    asymptomatic_to_confirmed = peewee.IntegerField(null=False)
    deaths = peewee.IntegerField(null=False)


class DisctrictOverview(Base):
    id = peewee.AutoField()
    date = peewee.DateField(null=False, index=True)
    district_name = peewee.CharField(null=False, index=True)
    total = peewee.IntegerField(null=False)
    confirmed = peewee.IntegerField(null=False)
    asymptomatic = peewee.IntegerField(null=False)


class Place(Base):
    id = peewee.AutoField()
    date = peewee.DateField(null=False, index=True)
    district_name = peewee.CharField(null=False, index=True)
    place_name = peewee.CharField(null=False, index=True)
    lng = peewee.DoubleField(null=False)
    lat = peewee.DoubleField(null=False)


def write_csv(filename: str, rows: list, recreate=True):
    if recreate and os.path.exists(filename):
        os.remove(filename)

    with open(filename, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            spamwriter.writerow(row)


def write_excel(filename: str, sheets: list, recreate=True):
    if recreate and os.path.exists(filename):
        os.remove(filename)

    wb = Workbook()
    for sheet in sheets:
        ws = wb.create_sheet(sheet['name'])
        for row in sheet['rows']:
            ws.append(row)
    wb.save(filename)


def create_db_files():
    db_location = "./data/db/covid19-shanghai-lockdown.db"
    if os.path.exists(db_location):
        os.remove(db_location)

    database = SqliteDatabase(db_location, pragmas={
        'journal_mode': 'wal',
        'cache_size': -1 * 8000,
        'foreign_keys': 1,
        'ignore_check_constraints': 0,
        'synchronous': 0})
    database_proxy.initialize(database)
    database.create_tables(
        [Overview, DisctrictOverview, Place], safe=True)
    # Overview.truncate_table()
    # DisctrictOverview.truncate_table()
    # Place.truncate_table()

    sheets = []

    overview_data = get_overview_data()
    overview_rows = [['Date', 'Total', 'Confirmed', 'Deaths',
                      'Asymptomatic', 'Asymptomatic to Confirmed']]
    for date, item in overview_data.items():
        Overview.create(date=date, total=item['total'], confirmed=item['confirmed'], deaths=item['deaths'],
                        asymptomatic=item['asymptomatic'], asymptomatic_to_confirmed=item['asymptomatic_to_confirmed'])
        overview_rows.append([date, item['total'], item['confirmed'], item['deaths'],
                              item['asymptomatic'], item['asymptomatic_to_confirmed']])

    sheets.append({'name': 'Overview', 'rows': overview_rows})
    write_csv("./data/db/overview.csv", overview_rows)

    data = get_data()
    district_overview_rows = [
        ['Date', 'District', 'Total', 'Confirmed', 'Asymptomatic']]
    for item in data:
        date = item['date']
        districts = item['districts']
        for district in districts:
            DisctrictOverview.create(date=date, district_name=district['district_name'],
                                     total=district['total'], confirmed=district['confirmed'],
                                     asymptomatic=district['asymptomatic'])
            district_overview_rows.append([date, district['district_name'],
                                           district['total'], district['confirmed'],
                                           district['asymptomatic']])

    sheets.append({'name': 'District Overview',
                  'rows': district_overview_rows})
    write_csv("./data/db/district_overview.csv", district_overview_rows)

    places = get_place_data()
    place_rows = [["Date", "District", "Place", "Lng", "Lat"]]
    for place in places:
        Place.create(date=place['date'], district_name=place['district_name'],
                     place_name=place['place_name'],
                     lng=place['lnglat'][0], lat=place['lnglat'][1])

        place_rows.append([place['date'], place['district_name'], place['place_name'],
                           place['lnglat'][0], place['lnglat'][1]])
    sheets.append({'name': 'Place', 'rows': place_rows})
    write_csv("./data/db/place.csv", place_rows)

    write_excel("./data/db/covid19-shanghai-lockdown.xlsx", sheets)


if __name__ == "__main__":
    # If you want to get the latest db files,
    # uncomment the underline and run this file
    #
    # create_db_files()
    pass

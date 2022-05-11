import os
import peewee
from peewee import DatabaseProxy, Model, SqliteDatabase

database_proxy = DatabaseProxy()


class Base(Model):
    class Meta:
        database = database_proxy
        legacy_table_names = False


class Overview(Base):
    id = peewee.CharField(primary_key=True)
    date = peewee.DateField(null=False)
    total = peewee.IntegerField(null=False)
    confirmed = peewee.IntegerField(null=False)
    asymptomatic = peewee.IntegerField(null=False)
    asymptomatic_to_confirmed = peewee.IntegerField(null=False)
    deaths = peewee.IntegerField(null=False)


class DisctrictOverview(Base):
    id = peewee.CharField(primary_key=True)
    date = peewee.DateField(null=False)
    district_name = peewee.CharField(null=False)
    total = peewee.IntegerField(null=False)
    confirmed = peewee.IntegerField(null=False)
    asymptomatic = peewee.IntegerField(null=False)
    asymptomatic_to_confirmed = peewee.IntegerField(null=False)


class Place(Base):
    id = peewee.CharField(primary_key=True)
    date = peewee.DateField(null=False)
    district_name = peewee.CharField(null=False)
    place_name = peewee.CharField(null=False)
    lng = peewee.DoubleField(null=False)
    lat = peewee.DoubleField(null=False)


if __name__ == "__main__":
    data_location = "./data/summary"
    database = SqliteDatabase(os.path.join(data_location, "summary.db"), pragmas={
        'journal_mode': 'wal',
        'cache_size': -1 * 8000,
        'foreign_keys': 1,
        'ignore_check_constraints': 0,
        'synchronous': 0})
    database_proxy.initialize(database)
    database.create_tables(
        [Overview, DisctrictOverview, Place], safe=True)

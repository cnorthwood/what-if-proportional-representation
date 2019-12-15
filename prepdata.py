#!/usr/bin/env python3

from collections import defaultdict
import csv
import json
from os import makedirs
from shapely.geometry import mapping, shape
from shapely.ops import cascaded_union
import sys

CONSTITUENCIES = {}


# 1. Get our new, combined, constituencies
with open("data/constituency-allocations.csv", encoding="utf-8-sig") as data_file:
    csv_reader = csv.reader(data_file)
    for row in csv_reader:
        CONSTITUENCIES[row[0]] = {
            "electorate": row[1].strip(),
            "seats": int(row[2]),
            "formed_from": [constituency for constituency in row[3:] if constituency],
            "formed_from_ids": set(),
            "votes": defaultdict(int),
        }


# 2. Load in the election results
RESULTS = defaultdict(dict)
with open("data/results-2017.csv", encoding="utf-8-sig") as data_file:
    csv_reader = csv.reader(data_file)
    for row in csv_reader:
        constituency_id = row[0]
        constituency_name = row[2]
        party = row[6]
        votes = int(row[7])
        for constituency in CONSTITUENCIES.values():
            if constituency_name in constituency["formed_from"]:
                constituency["formed_from_ids"].add(constituency_id)
                constituency["votes"][party] += votes
                break
        else:
            print(f"{constituency_name} does not appear to have been merged in anywhere??")
            sys.exit(1)


# 3. Load in constituency boundaries
GEOMETRIES = {}
with open("data/gb.geojson") as gb_geojson_file:
    data = json.load(gb_geojson_file)
    for feature in data["features"]:
        constituency_id = feature["properties"]["CODE"]
        GEOMETRIES[constituency_id] = shape(feature["geometry"])

with open("data/ni.geojson") as ni_geojson_file:
    data = json.load(ni_geojson_file)
    for feature in data["features"]:
        constituency_id = feature["properties"]["PC_ID"]
        GEOMETRIES[constituency_id] = shape(feature["geometry"])


# 4. Check we've correctly parsed everything
assert(all(len(constituency["formed_from"]) == len(constituency["formed_from_ids"]) for constituency in CONSTITUENCIES.values()))
assert(all(all(constituency_id in GEOMETRIES for constituency_id in constituency["formed_from_ids"]) for constituency in CONSTITUENCIES.values()))


# 5. Create combined boundaries
for constituency in CONSTITUENCIES.values():
    constituency["geometry"] = cascaded_union([GEOMETRIES[constituency_id] for constituency_id in constituency["formed_from_ids"]])


# 6. Run D'Hondt
def dhondt(votes, seats_available):
    allocations = defaultdict(int)
    while sum(allocations.values()) < seats_available:
        winning_party = max(votes.keys(), key=lambda party: votes[party] / (allocations[party] + 1))
        allocations[winning_party] += 1
    return allocations


PARLIAMENT = defaultdict(int)
for constituency in CONSTITUENCIES.values():
    seat_allocations = dhondt(constituency["votes"], constituency["seats"])
    constituency["seat_allocations"] = seat_allocations
    for party, seats in seat_allocations.items():
        if seats == 0:
            continue
        PARLIAMENT[party] += seats

with open("src/data.json", "w") as output_file:
    json.dump({
        "parliament": PARLIAMENT,
        "constituencies": {
            constituency_name: {
                "electorate": constituency["electorate"],
                "seats": constituency["seats"],
                "formedFrom": constituency["formed_from"],
                "votes": constituency["votes"],
                "seatAllocations": constituency["seat_allocations"],
            } for constituency_name, constituency in CONSTITUENCIES.items()}
    }, output_file)

makedirs("public/geometries/", exist_ok=True)
for constituency_name, constituency in CONSTITUENCIES.items():
    with open(f"public/geometries/{constituency_name}.geojson", "w") as geojson_file:
        json.dump({
            "type": "Feature",
            "properties": {"name": constituency_name},
            "geometry": mapping(constituency["geometry"])
        }, geojson_file)
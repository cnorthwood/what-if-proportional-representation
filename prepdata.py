#!/usr/bin/env python3

from collections import defaultdict
import csv
import json
from os import makedirs
import requests
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
            "seats_topup": int(row[3]),
            "formed_from": [constituency for constituency in row[4:] if constituency],
            "formed_from_ids": set(),
            "votes": defaultdict(int),
        }


# 2. Load in the election results
RESULTS = defaultdict(dict)
response = requests.get("https://interactive.guim.co.uk/2019/12/ukelection2019-data/prod/snap/full.json")
response.raise_for_status()
for seat in response.json():
    seat_name = seat["name"].replace("&", "and").replace(",", "").replace("Hull", "Kingston upon Hull")
    for constituency in CONSTITUENCIES.values():
        if any(set(seat_name.lower().split(" ")) == set(formed_from.lower().replace(",", "").strip(" 56").split(" ")) for formed_from in constituency["formed_from"]):
            constituency["formed_from_ids"].add(seat["ons"])
            for candidate in seat["candidates"]:
                party = f"{candidate['firstName']} {candidate['surname']}" if candidate["party"] == "Ind" else candidate["party"]
                constituency["votes"][party] += candidate["votes"]
            break
    else:
        print(f"{seat_name} does not appear to have been merged in anywhere??")
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
for name, constituency in CONSTITUENCIES.items():
    if len(constituency["formed_from"]) != len(constituency["formed_from_ids"]):
        print(name, constituency)
assert(all(len(constituency["formed_from"]) == len(constituency["formed_from_ids"]) for constituency in CONSTITUENCIES.values()))
assert(all(constituency_id in GEOMETRIES for constituency in CONSTITUENCIES.values() for constituency_id in constituency["formed_from_ids"]))


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


MM_PARLIAMENT = defaultdict(int)
for constituency in CONSTITUENCIES.values():
    seat_allocations = dhondt(constituency["votes"], constituency["seats"])
    constituency["seat_allocations"] = seat_allocations
    for party, seats in seat_allocations.items():
        if seats == 0:
            continue
        MM_PARLIAMENT[party] += seats


TOPUP_PARLIAMENT = defaultdict(int)
TOTAL_VOTES = defaultdict(int)
for constituency in CONSTITUENCIES.values():
    seat_allocations = dhondt(constituency["votes"], constituency["seats_topup"])
    for party, votes in constituency["votes"].items():
        TOTAL_VOTES[party] += votes
    constituency["seat_allocations_topup"] = seat_allocations
    for party, seats in seat_allocations.items():
        if seats == 0:
            continue
        TOPUP_PARLIAMENT[party] += seats

NUM_TOPUP_SEATS = 300
TOPUP_SEATS = dhondt(TOTAL_VOTES, NUM_TOPUP_SEATS)
for party, seats in TOPUP_SEATS.items():
    if seats == 0:
        continue
    TOPUP_PARLIAMENT[party] += seats

with open("src/data.json", "w") as output_file:
    json.dump({
        "multimember": {
            "parliament": MM_PARLIAMENT,
            "constituencies": {
                constituency_name: {
                    "electorate": constituency["electorate"],
                    "seats": constituency["seats"],
                    "formedFrom": constituency["formed_from"],
                    "votes": constituency["votes"],
                    "seatAllocations": constituency["seat_allocations"],
                } for constituency_name, constituency in CONSTITUENCIES.items()
            },
        },
        "withTopup": {
            "parliament": TOPUP_PARLIAMENT,
            "constituencies": {
                constituency_name: {
                    "electorate": constituency["electorate"],
                    "seats": constituency["seats_topup"],
                    "formedFrom": constituency["formed_from"],
                    "votes": constituency["votes"],
                    "seatAllocations": constituency["seat_allocations_topup"],
                } for constituency_name, constituency in CONSTITUENCIES.items()
            },
            "topup": TOPUP_SEATS,
        }
    }, output_file)

makedirs("public/geometries/", exist_ok=True)
for constituency_name, constituency in CONSTITUENCIES.items():
    with open(f"public/geometries/{constituency_name}.geojson", "w") as geojson_file:
        json.dump(
            {
                "type": "Feature",
                "properties": {"name": constituency_name},
                "geometry": mapping(constituency["geometry"])
            },
            geojson_file
        )

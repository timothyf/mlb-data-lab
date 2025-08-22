# save as schema_from_savant.py
import json, requests
from genson import SchemaBuilder
import argparse
import sys

# Usage:
# python generate_schema.py "https://baseballsavant.mlb.com/gf?game_pk=776673" > schema.json


def fetch_schema(url):
    r2 = requests.get(url, headers={"Accept": "application/json"})
    r2.raise_for_status()
    data2 = r2.json()
    b2 = SchemaBuilder(schema_uri="http://json-schema.org/draft-07/schema#")
    b2.add_object(data2)
    print(json.dumps(b2.to_schema(), indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate JSON schema from JSON API URL.")
    parser.add_argument("url", help="JSON API URL (e.g. https://baseballsavant.mlb.com/gf?game_pk=776673)")
    args = parser.parse_args()
    # Optionally avoid duplicate output if default code already ran with same URL
    fetch_schema(args.url)
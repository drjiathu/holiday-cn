#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Script for updating data."""

import argparse
from datetime import datetime, timedelta, tzinfo
import json
import os
from pathlib import Path
import re
import subprocess
from tempfile import mkstemp
from threading import Thread
from typing import Iterator
from zipfile import ZipFile

from pymongo import MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure
from tqdm import tqdm

from .fetch import CustomJSONEncoder, fetch_holidays
from .generate_ics import generate_ics
from .filetools import workspace_path, dataspace_path


class ChinaTimezone(tzinfo):
    """Timezone of China."""

    def tzname(self, __dt: datetime | None) -> str | None:
        return "UTC+8"

    def utcoffset(self, __dt: datetime | None) -> timedelta | None:
        return timedelta(hours=8)

    def dst(self, __dt: datetime | None) -> timedelta | None:
        return timedelta()


class MongoDBConnection:
    def __init__(
        self,
        host="localhost",
        port: int = 27017,
        database: str | None = None,
        username=None,
        password=None,
        auth_source="admin",
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.auth_source = auth_source
        self.client = None

    def __enter__(self):
        try:
            self.client = MongoClient(
                self.host,
                self.port,
                username=self.username,
                password=self.password,
                authSource=self.auth_source,
            )
            if self.database:
                self.db = self.client[self.database]
            return self
        except ConnectionFailure as e:
            print(f"Connection error: {str(e)}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()

    def upsert_one(self, collection, record):
        col = self.db[collection]
        unique_names = []
        for k, v in col.index_information().items():
            if k != "_id_" and v["unique"]:
                unique_names += [c[0] for c in v["key"]]
        col.update_one(
            {n: record[n] for n in unique_names}, {"$set": record}, upsert=True
        )

    def upsert_many(self, collection, records):
        col = self.db[collection]
        unique_names = []
        for k, v in col.index_information().items():
            if k != "_id_" and v["unique"]:
                unique_names += [c[0] for c in v["key"]]
        operations = [
            UpdateOne({n: r[n] for n in unique_names}, {"$set": r}, upsert=True)
            for r in records
        ]
        col.bulk_write(operations)


def update_data(year: int) -> Iterator[Path]:
    """Update and store data for a year."""
    json_filename = dataspace_path(f"{year}.json")
    ics_filename = dataspace_path(f"{year}.ics")
    data = fetch_holidays(year)

    def _dump_json():
        with open(json_filename, "w", encoding="utf-8", newline="\n") as f:
            json.dump(
                dict(
                    (
                        (
                            "$schema",
                            "https://raw.githubusercontent.com/drjiathu/holiday-cn/master/schema.json",
                        ),
                        (
                            "$id",
                            f"https://raw.githubusercontent.com/drjiathu/holiday-cn/master/data/{year}.json",
                        ),
                        *data.items(),
                    )
                ),
                f,
                indent=4,
                ensure_ascii=False,
                cls=CustomJSONEncoder,
            )

    def _dump_mongo():
        if data is None:
            return
        papers = data["papers"]
        records: list[dict] = []
        for d in data["days"]:
            d["papers"] = papers
            d["date"] = d["date"].isoformat()
            records.append(d)
        with MongoDBConnection(
            host="192.168.106.21",
            database="others",
            username="prod",
            password="prod@Yuanhui",
            auth_source="others",
        ) as conn:
            if isinstance(records, dict):
                conn.upsert_one("holiday_cn", records)
            else:
                conn.upsert_many("holiday_cn", records)

    t1 = Thread(target=_dump_json)
    t2 = Thread(target=_dump_mongo)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
    # _dump_json()
    # _dump_mongo()

    yield json_filename
    generate_ics(data["days"], ics_filename)
    yield ics_filename


def update_main_ics(fr_year, to_year):
    all_days = []
    for year in range(fr_year, to_year + 1):
        filename = dataspace_path(f"{year}.json")
        if not filename.is_file():
            continue
        with open(filename, "r", encoding="utf8") as in_f:
            data = json.loads(in_f.read())
            all_days.extend(data.get("days"))

    filename = dataspace_path("holiday-cn.ics")
    generate_ics(all_days, filename)

    return filename


def pack_data(file):
    """Pack data json in zipfile."""
    zip_file = ZipFile(file, "w")
    for i in dataspace_path().iterdir():
        if not re.match(r"\d+\.json", i.name):
            continue
        zip_file.write(dataspace_path(i), i)


def github_push(*filenames, is_release=False):
    subprocess.run(["git", "add", *filenames], check=True)
    diff = subprocess.run(
        ["git", "diff", "--stat", "--cached", "*.json", "*.ics"],
        check=True,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    ).stdout
    if not diff:
        print("Already up to date.")
        return
    if not is_release:
        print("Updated repository data, skip release since not specified `--release`")
        return

    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "chore(release): update holiday data",
            "-m",
            "[skip ci]",
        ],
        check=True,
    )
    subprocess.run(["git", "push"], check=True)

    tag = datetime.now(ChinaTimezone()).strftime("%Y.%m.%d")
    temp_note_fd, temp_note_name = mkstemp()
    with open(temp_note_fd, "w", encoding="utf-8") as f:
        f.write(tag + "\n\n```diff\n" + diff + "\n```\n")
    workspace_path("dist").mkdir(exist_ok=True)
    zip_path = workspace_path("dist", f"holiday-cn-{tag}.zip")
    pack_data(zip_path)

    subprocess.run(
        [
            "gh",
            "release",
            "create",
            "-F",
            temp_note_name,
            tag,
            f"{zip_path}#JSON数据",
        ],
        check=True,
    )
    os.unlink(temp_note_name)


def update(all=False, release=False):
    now = datetime.now(ChinaTimezone())

    filenames = []
    progress = tqdm(range(2007 if all else now.year, now.year + 2))
    for i in progress:
        progress.set_description(f"Updating {i} data ...")
        filenames += list(update_data(i))
    progress.set_description("Updating holiday-cn.ics")
    filenames.append(update_main_ics(now.year - 4, now.year + 1))
    print("")
    github_push(*filenames, is_release=release)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--all",
        action="store_true",
        help="Update all years since 2007, default is this year and next year",
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="create new release if repository data is not up to date",
    )
    args = parser.parse_args()

    update(args.all, args.release)


if __name__ == "__main__":
    main()

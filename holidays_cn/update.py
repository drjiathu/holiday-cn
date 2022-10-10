#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Script for updating date."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from datetime import datetime, timedelta, tzinfo
from typing import Iterator
from zipfile import ZipFile
import subprocess
from tempfile import mkstemp

from tqdm import tqdm

from fetch_holidays import CustomJSONEncoder, fetch_holidays
from generate_ics import generate_ics


class ChinaTimezone(tzinfo):
    """Timezone of China."""

    def tzname(self, __dt: datetime | None) -> str | None:
        return "UTC+8"

    def utcoffset(self, __dt: datetime | None) -> timedelta | None:
        return timedelta(hours=8)

    def dst(self, __dt: datetime | None) -> timedelta | None:
        return timedelta()


__dirname__ = Path(__file__).parent


def _data_path(*other):

    return Path(__dirname__).parent.joinpath('data', *other)


def update_data(year: int) -> Iterator[str]:
    """Update and store data for a year."""
    json_filename = _data_path(f"{year}.json")
    ics_filename = _data_path(f"{year}.ics")
    with open(json_filename, "w", encoding="utf-8", newline="\n") as f:
        data = fetch_holidays(year)
        json.dump(
            dict(
                (
                    (
                        "$schema",
                        "https://raw.githubusercontent.com/drjiathu/holiday-cn/main/schema.json",  # noqa
                    ),
                    (
                        "$id",
                        f"https://raw.githubusercontent.com/drjiathu/holiday-cn/main/{year}.json",  # noqa
                    ),
                    *data.items(),
                )
            ),
            f,
            indent=4,
            ensure_ascii=False,
            cls=CustomJSONEncoder,
        )

    yield json_filename
    generate_ics(data["days"], ics_filename)
    yield ics_filename


def update_main_ics(fr_year, to_year):
    all_days = []
    for year in range(fr_year, to_year + 1):
        filename = _data_path(f"{year}.json")
        if not filename.is_file():
            continue
        with open(filename, "r", encoding="utf8") as in_f:
            data = json.loads(in_f.read())
            all_days.extend(data.get("days"))

    filename = _data_path("holiday-cn.ics")
    generate_ics(all_days, filename)

    return filename


def pack_data(file):
    """Pack data json in zipfile."""
    zip_file = ZipFile(file, 'w')
    for i in __dirname__.iterdir():
        if not re.match(r"\d+\.json", i):
            continue
        zip_file.write(_data_path(i), i)


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

    now = datetime.now(ChinaTimezone())
    is_release = args.release

    filenames = []
    progress = tqdm(range(2007 if args.all else now.year, now.year + 2))
    for i in progress:
        progress.set_description(f"Updating {i} data ...")
        filenames += list(update_data(i))
    progress.set_description("Updating holiday-cn.ics")
    filenames.append(update_main_ics(now.year - 4, now.year + 1))
    print("")

    subprocess.run(["hub", "add", *filenames], check=True)
    diff = subprocess.run(
        ["hub", "diff", "--stat", "--cached", "*.json", "*.ics"],
        check=True,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    ).stdout
    if not diff:
        print("Already up to date.")
        return
    if not is_release:
        print("Updated repository data, skip release since not specified "
              "`--release`")
        return

    subprocess.run(
        [
            "hub",
            "commit",
            "-m",
            "chore(release): update holiday data",
            "-m",
            "[skip ci]",
        ],
        check=True,
    )
    subprocess.run(["hub", "push"], check=True)

    tag = now.strftime("%Y.%m.%d")
    temp_note_fd, temp_note_name = mkstemp()
    with open(temp_note_fd, "w", encoding="utf-8") as f:
        f.write(tag + "\n\n```diff\n" + diff + "\n```\n")
    _data_path("dist").mkdir(exist_ok=True)
    zip_path = _data_path("dist", f"holiday-cn-{tag}.zip")
    pack_data(zip_path)

    subprocess.run(
        [
            "hub",
            "release",
            "create",
            "-F",
            temp_note_name,
            "-a",
            f"{zip_path}#JSON数据",
            tag,
        ],
        check=True,
    )
    os.unlink(temp_note_name)


if __name__ == '__main__':
    main()

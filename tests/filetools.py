#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from pathlib import Path

__dirname__: Path = Path(__file__).parent


def _file_path(*other) -> Path:
    return __dirname__.joinpath(*other)

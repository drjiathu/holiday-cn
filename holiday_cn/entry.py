#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import click

from .update import update


@click.command()
@click.option(
    "--all",
    is_flag=True,
    help="Update all years since 2007, default is this year and next year",
)
@click.option(
    "--release",
    is_flag=True,
    help="create new release if repository data is not up to date",
)
def cli(all, release):
    update(all, release)


if __name__ == "__main__":
    cli()

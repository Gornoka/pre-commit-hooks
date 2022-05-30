# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import io
import logging
import pathlib
import re
import tokenize
from typing import Sequence
import pprint
import json
import os
from subprocess import Popen, PIPE

logging.basicConfig(level=logging.DEBUG, filemode="a", filename="branch_name_test.log")


def get_branch_name_from_path(path="."):
    """
    returns currently checked out branch name on the
    git repository at the given path
    """
    cmd_args = ["git", "rev-parse",
                "--abbrev-ref", "HEAD"]
    wd = pathlib.Path(path).absolute()  # get absolute path to make windows happy
    if wd.is_file():
        wd = wd.parent  # get parent directory if path is a file
    p = Popen(cmd_args, stdout=PIPE, cwd=wd)
    p.wait(1)  # this operation should be done in the order of milliseconds
    stdout, stderr = p.communicate()
    if stderr is not None:
        print(f"unable to get branch name with {stderr.decode('utf-8')}")
        logging.error("failed to get branch name with %s", stderr, )
        return None
    branch_name = stdout.decode('utf-8').replace("\n", "")  # remove trailing \n from branch name
    return branch_name


def main(argv: Sequence[str] | None = None) -> int:
    # get current branch name

    parser = argparse.ArgumentParser()

    default_regex = r"^(master|main|staging)$|^((feat|docs|chore|debug|test)\/\d+\/[\w_\d-]+)$"
    logging.debug(f"default_regex: {default_regex}")

    parser.add_argument('--branch-regex', nargs="?",
                        default=default_regex,
                        help='regex to use to match branch name')
    parser.add_argument('filenames', nargs='*', help='Filenames to check.')
    parser.add_argument('--fast-mode', nargs="?", help="skips branch name check for all files except for the first one",
                        default="true")

    args = parser.parse_args(argv)
    # this should behave predictably for testing as well as other usages
    # the cost of evaluating it for multiple files ( which should be redundant) is negligible
    # can be turned off by setting --fast-mode to false ( or not true to be more specific)
    branch_names = [get_branch_name_from_path(path) for path in args.filenames]

    if args.fast_mode.lower() == "true":
        branch_names = branch_names[:1]

    try:
        branch_regex = re.compile(args.branch_regex)
    except re.error as e:
        print(f"failed to compile regex {args.branch_regex}")
        logging.error("failed to compile regex %s \nwith%s", args.branch_regex, e)
        return 1
    r_value = 1
    for bn in branch_names:
        if bn is None:
            continue
        if not branch_regex.search(bn):  # be aware of matches behavior
            print(f"branch name {bn} does not match regex {args.branch_regex}")
            logging.error("branch name %s does not match regex %s", bn, args.branch_regex)
        else:
            logging.info("branch name %s matches regex %s", bn, args.branch_regex)
            r_value = 0

    return r_value

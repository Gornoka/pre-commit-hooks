from __future__ import annotations

import argparse
import logging
import pathlib
import re
from subprocess import PIPE
from subprocess import Popen
from typing import Sequence

logging.basicConfig(
    level=logging.WARNING, filemode='w',
    filename='branch_name_test.log',
)
DEFAULT_REGEX = '^(master|main|staging)$|' \
                '^((feat|docs|chore|debug|test)\\/' \
                '(\\d+|quick)\\/[\\w\\d\\-\\_]+)$'
# validates against the branches
# master main staging
# and feature brances following the style
# type/number/name
# where type is one of feat, docs, chore, debug, test


def get_branch_name_from_path(
    path: str = '.',
    verbose: bool = True,
) -> str | None:
    """
    get the branch name for a given file or folder pathlike object or str
    Returns None in case of an error
    Args:
        verbose (): whether to print error to stdout mainly for testing
        path (): path of target file or folder

    Returns: str or None

    """
    # cmd args to get the git branch of a folder
    cmd_args = [
        'git', 'rev-parse',
        '--abbrev-ref', 'HEAD',
    ]
    # get absolute path to make windows happy
    target_workdir = pathlib.Path(path).absolute()
    if target_workdir.is_file():  # get parent directory if path is a file
        target_workdir = target_workdir.parent
    p = Popen(cmd_args, stdout=PIPE, cwd=target_workdir)
    # this operation should be done in the order of milliseconds,
    # timeout just to prevent hangs
    p.wait(1)
    stdout, stderr = p.communicate()
    if stderr is not None:
        if verbose:
            print(f"unable to get branch name with {stderr.decode('utf-8')}")
        logging.error('failed to get branch name with %s', stderr)
        return None
    # remove trailing \n from branch name
    branch_name = stdout.decode('utf-8').replace('\n', '')
    return branch_name


def check_branches(
        branch_regex: re.Pattern[str],
        branch_names: list[str | None],
        verbose: bool = True,
) -> int:
    """
    check if the given branch names match the given regex
    Args:
        branch_regex : regex to check
        branch_names : branch name to check

    Returns:

    """
    r_value = 0  # interaction with submodules untested
    for bn in branch_names:
        if bn is None:
            # all files should be resolvable and have a git
            # folder this should not be called
            logging.error(
                'failed to get branch name for one of  %s',
                branch_names,
            )
            if verbose:
                print(
                    'failed to get branch name for a file '
                    'see logs for details',
                )
            return 1

        if not branch_regex.search(bn):
            if verbose:
                print(f'branch name {bn} does not match regex {branch_names}')
            logging.error(
                'branch name %s does not '
                'match regex %s', bn, branch_names,
            )
            r_value = 1
        else:
            logging.info('branch name %s matches regex %s', bn, branch_names)

    return r_value


def main(argv: Sequence[str] | None = None) -> int:
    """
    main function to check whether the branches of a list of changed files
    match the given regex
    Args:
        argv ():

    Returns:

    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--branch-regex', nargs='?',
        default=DEFAULT_REGEX,
        help='regex to use to match branch name',
    )
    parser.add_argument(
        'filenames', nargs='*',
        help='Filenames to check.',
    )
    parser.add_argument(
        '--fast-mode', nargs='?',
        help='skips branch name check for all files except for the first one',
        default='true',
    )

    args = parser.parse_args(argv)
    # this should behave predictably for testing as well as other usages
    # the cost of evaluating it for multiple files ( which should be redundant)
    # is negligible can be turned off by setting --fast-mode to false
    branch_names = [get_branch_name_from_path(path) for path in args.filenames]

    if args.fast_mode.lower() == 'true':
        branch_names = branch_names[:1]
    try:
        branch_regex = re.compile(args.branch_regex)
    except re.error as e:
        print(f'failed to compile regex {args.branch_regex}')
        logging.error(
            'failed to compile regex %s \nwith%s',
            args.branch_regex, e,
        )
        return 1

    return check_branches(branch_regex, branch_names)

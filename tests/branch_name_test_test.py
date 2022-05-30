from __future__ import annotations

import re

import pytest

from pre_commit_hooks.branch_name_test import check_branches
from pre_commit_hooks.branch_name_test import DEFAULT_REGEX

# checking whether default branch pattern works as expected

default_regex = re.compile(DEFAULT_REGEX)
TEST_CASES = [

]

static_branch_names = [
    # validating that master branch is valid
    (default_regex, ['master'], 0),
    (default_regex, ['master2'], 1),
    (default_regex, ['2master'], 1),
    # validating that staging branch is valid
    (default_regex, ['staging'], 0),
    (default_regex, ['staging2'], 1),
    (default_regex, ['2staging'], 1),
    # validating that main branch is valid
    (default_regex, ['main'], 0),
    (default_regex, ['main2'], 1),
    (default_regex, ['2main'], 1),
]

TEST_CASES.extend(static_branch_names)

expected_branch_types = ['demo,staging,main']


@pytest.mark.parametrize(
    ('branch_regex', 'branch_names', 'expected_retval'),
    TEST_CASES,
)
def test_default_regex(branch_regex, branch_names, expected_retval):
    """
    Test default regex
    """
    retval = check_branches(
        branch_regex=branch_regex,
        branch_names=branch_names,
    )
    assert retval == expected_retval

from __future__ import annotations

import itertools
import re

import pytest

from pre_commit_hooks.branch_name_test import check_branches
from pre_commit_hooks.branch_name_test import DEFAULT_REGEX

# checking whether default branch pattern works as expected
default_regex = re.compile(DEFAULT_REGEX)
TEST_CASES: list[tuple[re.Pattern[str], list[str], int]] = [

]


# generates test cases for the following branch patterns
# master main staging
# and feature brances following the style
# type/number/name
# where type is one of feat, docs, chore, debug, test


def append_errors(primary_text: str, error_texts: list[str]) -> list[str]:
    """
    Append around text to primary text
    """

    combined_errors_ = []
    for ct in itertools.product(error_texts, repeat=2):
        combined_errors_.append('/'.join(ct))
    for ct in itertools.product(error_texts, repeat=2):
        combined_errors_.append('_'.join(ct))
    for ct in itertools.product(error_texts, repeat=2):
        combined_errors_.append('-'.join(ct))

    errors_combined_with_primary = []
    for ct in itertools.product([primary_text], combined_errors_):
        errors_combined_with_primary.append(''.join(ct))
    return errors_combined_with_primary


static_branch_names: list[tuple[re.Pattern[str], list[str], int]] = [
    (default_regex, ['master'], 0),
    (default_regex, ['staging'], 0),
    (default_regex, ['main'], 0),

]
TEST_CASES.extend(static_branch_names)

error_text_components = ['asdf', '123', '1', 'a', 'A', '']
primary_branch_types = ['master', 'staging', 'main']
for pb in primary_branch_types:
    error_permutations = append_errors(
        primary_text=pb,
        error_texts=error_text_components,
    )
    cases = []
    for error_permutation in error_permutations:
        cases.append((default_regex, [error_permutation], 1))
    TEST_CASES.extend(cases)

secondary_branch_types = (
    'feat', 'docs', 'chore',
    'debug', 'test',
)

issue_numbers = ['1', '11', '111', '1111', 'quick']

issue_text_components = ['asdf', '123', '1', 'a', 'A']
issue_text = []
for ct in itertools.product(issue_text_components, repeat=2):
    issue_text.append(''.join(ct))

for ct in itertools.product(issue_text_components, repeat=2):
    issue_text.append('_'.join(ct))

for ct in itertools.product(issue_text_components, repeat=2):
    issue_text.append('-'.join(ct))

cases = []
for t in itertools.product(secondary_branch_types, issue_numbers, issue_text):
    cases.append((default_regex, [r'/'.join(t)], 0))
TEST_CASES.extend(
    cases,
)


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
        verbose=False,
    )
    assert retval == expected_retval


if __name__ == '__main__':
    error_text_components = ['asdf', '123', '1', 'a', 'A', '']

    combined_errors = append_errors(
        primary_text='master',
        error_texts=error_text_components,
    )

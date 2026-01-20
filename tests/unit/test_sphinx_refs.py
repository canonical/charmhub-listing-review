# Copyright 2025 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test the Sphinx reference conversion functionality."""

import pytest

from charmhub_listing_review.sphinx_refs import convert_sphinx_refs


@pytest.mark.parametrize(
    'input_text,expected',
    [
        # Reference with display text and target
        (
            '{external+charmcraft:ref}`Initialise a charm <initialise-a-charm>`',
            '[Initialise a charm](https://documentation.ubuntu.com/charmcraft/en/latest/howto/manage-charms/#initialise-a-charm)',
        ),
        # Reference with just target
        (
            '{external+charmcraft:ref}`initialise-a-charm`',
            '[initialise-a-charm](https://documentation.ubuntu.com/charmcraft/en/latest/howto/manage-charms/#initialise-a-charm)',
        ),
        # Reference to charmcraft.yaml key
        (
            '{external+charmcraft:ref}`name <charmcraft-yaml-key-name>`',
            '[name](https://documentation.ubuntu.com/charmcraft/en/latest/reference/files/charmcraft-yaml-file/#charmcraft-yaml-key-name)',
        ),
        # Reference to actions key
        (
            '{external+charmcraft:ref}`actions <charmcraft-yaml-key-actions>`',
            '[actions](https://documentation.ubuntu.com/charmcraft/en/latest/reference/files/charmcraft-yaml-file/#charmcraft-yaml-key-actions)',
        ),
        # Reference to config key
        (
            '{external+charmcraft:ref}`config <charmcraft-yaml-key-config>`',
            '[config](https://documentation.ubuntu.com/charmcraft/en/latest/reference/files/charmcraft-yaml-file/#charmcraft-yaml-key-config)',
        ),
        # Reference to requires key with custom display text
        (
            '{external+charmcraft:ref}`<endpoint role> <charmcraft-yaml-key-requires>`',
            '[<endpoint role>](https://documentation.ubuntu.com/charmcraft/en/latest/reference/files/charmcraft-yaml-file/#charmcraft-yaml-key-requires)',
        ),
        # Reference with pipe character in display text
        (
            '{external+charmcraft:ref}`Charmcraft | Specify a name <specify-a-name>`',
            '[Charmcraft | Specify a name](https://documentation.ubuntu.com/charmcraft/en/latest/howto/manage-charms/#specify-a-name)',
        ),
        # Juju reference
        (
            '{external+juju:ref}`juju model-config <command-juju-model-config>`',
            '[juju model-config](https://documentation.ubuntu.com/juju/3.6/reference/juju-cli/list-of-juju-cli-commands/model-config/#command-juju-model-config)',
        ),
        # Unknown reference falls back to display text
        (
            '{external+charmcraft:ref}`unknown <unknown-target>`',
            'unknown',
        ),
        # Unknown source falls back to display text
        (
            '{external+unknown:ref}`text <target>`',
            'text',
        ),
        # Text without references is unchanged
        (
            'This is plain text without any Sphinx references.',
            'This is plain text without any Sphinx references.',
        ),
        # Multiple references in same text
        (
            'See {external+charmcraft:ref}`initialise-a-charm` '
            'and {external+charmcraft:ref}`specify-a-name`.',
            'See [initialise-a-charm]'
            '(https://documentation.ubuntu.com/charmcraft/en/latest/'
            'howto/manage-charms/#initialise-a-charm) '
            'and [specify-a-name]'
            '(https://documentation.ubuntu.com/charmcraft/en/latest/'
            'howto/manage-charms/#specify-a-name).',
        ),
    ],
)
def test_convert_sphinx_refs(input_text, expected):
    assert convert_sphinx_refs(input_text) == expected


def test_convert_sphinx_refs_multiline():
    """Test that conversion works across multiple lines."""
    input_text = """
- Name the repository using the pattern. See {external+charmcraft:ref}`specify-a-name`.
- Use the {external+charmcraft:ref}`name <charmcraft-yaml-key-name>` field.
"""
    result = convert_sphinx_refs(input_text)
    charmcraft_base = 'https://documentation.ubuntu.com/charmcraft/en/latest/'
    assert f'[specify-a-name]({charmcraft_base}howto/manage-charms/#specify-a-name)' in result
    yaml_file = 'reference/files/charmcraft-yaml-file/'
    assert f'[name]({charmcraft_base}{yaml_file}#charmcraft-yaml-key-name)' in result


def test_convert_sphinx_refs_preserves_surrounding_text():
    """Test that text surrounding references is preserved."""
    input_text = 'Before {external+charmcraft:ref}`initialise-a-charm` after.'
    charmcraft_base = 'https://documentation.ubuntu.com/charmcraft/en/latest/'
    expected = (
        f'Before [initialise-a-charm]({charmcraft_base}'
        'howto/manage-charms/#initialise-a-charm) after.'
    )
    assert convert_sphinx_refs(input_text) == expected

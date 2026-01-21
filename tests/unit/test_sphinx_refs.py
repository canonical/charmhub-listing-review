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

from charmhub_listing_review.sphinx_refs import _SPHINX_TO_MARKDOWN, convert_sphinx_refs


@pytest.mark.parametrize('sphinx_ref,markdown_link', list(_SPHINX_TO_MARKDOWN.items()))
def test_convert_sphinx_refs_all_mappings(sphinx_ref, markdown_link):
    """Test that all mapped references are converted correctly."""
    assert convert_sphinx_refs(sphinx_ref) == markdown_link


def test_convert_sphinx_refs_plain_text_unchanged():
    """Test that plain text without references is unchanged."""
    text = 'This is plain text without any Sphinx references.'
    assert convert_sphinx_refs(text) == text


def test_convert_sphinx_refs_multiple_references():
    """Test that multiple references in the same text are converted."""
    input_text = (
        'See {external+charmcraft:ref}`initialise-a-charm` '
        'and {external+charmcraft:ref}`specify-a-name`.'
    )
    result = convert_sphinx_refs(input_text)
    charmcraft_manage = (
        'https://documentation.ubuntu.com/charmcraft/en/latest/howto/manage-charms/'
    )
    assert f'[initialise-a-charm]({charmcraft_manage}#initialise-a-charm)' in result
    assert f'[specify-a-name]({charmcraft_manage}#specify-a-name)' in result


def test_convert_sphinx_refs_preserves_surrounding_text():
    """Test that text surrounding references is preserved."""
    input_text = 'Before {external+charmcraft:ref}`initialise-a-charm` after.'
    result = convert_sphinx_refs(input_text)
    assert result.startswith('Before ')
    assert result.endswith(' after.')
    assert '[initialise-a-charm]' in result


def test_convert_sphinx_refs_unknown_reference_unchanged():
    """Test that unknown references are left unchanged."""
    input_text = '{external+unknown:ref}`unknown-target`'
    assert convert_sphinx_refs(input_text) == input_text

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

"""Convert Sphinx inter-documentation references to Markdown links.

This module provides functionality to convert Sphinx inter-docutils references
(like ``{external+charmcraft:ref}`text <target>```) to proper Markdown links
that work in GitHub issues and other Markdown contexts.
"""

import re

# Base URLs for different documentation sources
_BASE_URLS = {
    'charmcraft': 'https://documentation.ubuntu.com/charmcraft/en/latest/',
    'juju': 'https://documentation.ubuntu.com/juju/3.6/',
    'ops': 'https://documentation.ubuntu.com/ops/latest/',
}

# Mapping of Sphinx reference targets to their relative URLs and fragments.
# The format is: target -> (relative_path, fragment)
# If fragment is None, the fragment is the same as the target.
_CHARMCRAFT_REFS = {
    'initialise-a-charm': ('howto/manage-charms/', None),
    'specify-a-name': ('howto/manage-charms/', None),
    'publish-a-resource': ('howto/manage-resources/', None),
    'charmcraft-yaml-key-name': ('reference/files/charmcraft-yaml-file/', None),
    'charmcraft-yaml-key-actions': ('reference/files/charmcraft-yaml-file/', None),
    'charmcraft-yaml-key-config': ('reference/files/charmcraft-yaml-file/', None),
    'charmcraft-yaml-key-requires': ('reference/files/charmcraft-yaml-file/', None),
    'charmcraft-yaml-key-provides': ('reference/files/charmcraft-yaml-file/', None),
    'charmcraft-yaml-key-documentation': ('reference/files/charmcraft-yaml-file/', None),
}

_JUJU_REFS = {
    'command-juju-model-config': (
        'reference/juju-cli/list-of-juju-cli-commands/model-config/',
        None,
    ),
}

_REF_MAPPINGS = {
    'charmcraft': _CHARMCRAFT_REFS,
    'juju': _JUJU_REFS,
}


def _get_url(source: str, target: str) -> str | None:
    """Get the full URL for a Sphinx reference target.

    Args:
        source: The documentation source (e.g., 'charmcraft', 'juju').
        target: The reference target (e.g., 'initialise-a-charm').

    Returns:
        The full URL, or None if the target is not found.
    """
    if source not in _BASE_URLS or source not in _REF_MAPPINGS:
        return None
    refs = _REF_MAPPINGS[source]
    if target not in refs:
        return None
    base_url = _BASE_URLS[source]
    path, fragment = refs[target]
    if fragment is None:
        fragment = target
    return f'{base_url}{path}#{fragment}'


# Pattern to match Sphinx inter-docutils references:
# {external+source:ref}`text <target>` or {external+source:ref}`target`
_SPHINX_REF_PATTERN = re.compile(
    r'\{external\+([a-z-]+):ref\}`'  # {external+source:ref}`
    r'([^`]+)'  # content inside backticks
    r'`'
)


def convert_sphinx_refs(text: str) -> str:
    """Convert Sphinx inter-docutils references to Markdown links.

    Converts references like:
    - ``{external+charmcraft:ref}`Initialise a charm <initialise-a-charm>```
      -> ``[Initialise a charm](https://...)``
    - ``{external+charmcraft:ref}`initialise-a-charm```
      -> ``[initialise-a-charm](https://...)``

    If a reference cannot be resolved, it is converted to plain text
    (just the display text without the Sphinx markup).

    Args:
        text: The text containing Sphinx references.

    Returns:
        The text with Sphinx references converted to Markdown links.
    """
    # Pattern to extract target from content like "display text <target>"
    target_pattern = re.compile(r'^(.*?)\s*<([a-z0-9-]+)>$')

    def replace_ref(match: re.Match[str]) -> str:
        source = match.group(1)
        content = match.group(2).strip()

        # Check if content has format "display text <target>"
        target_match = target_pattern.match(content)
        if target_match:
            display_text = target_match.group(1).strip()
            target = target_match.group(2)
        else:
            # Content is just the target
            target = content
            display_text = content

        url = _get_url(source, target)
        if url:
            return f'[{display_text}]({url})'
        # If we can't resolve, just return the display text
        return display_text

    return _SPHINX_REF_PATTERN.sub(replace_ref, text)

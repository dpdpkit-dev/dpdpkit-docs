"""Griffe extension: render Sphinx roles in dpdpkit docstrings as inline code.

The source docstrings use ``:class:`~dpdpkit.models.RootHash``` so they read well in IDEs and help();
mkdocstrings does not understand roles, so they are rewritten to ``RootHash`` before rendering.
"""

import re
from typing import Any

import griffe

_ROLE = re.compile(r":(?:class|meth|func|attr|mod|exc|data|obj):`(~?)([^`]+)`")


def _replace(match: re.Match[str]) -> str:
    short, target = match.group(1), match.group(2)
    name = target.rsplit(".", 1)[-1] if short else target
    return f"`{name}`"


class SphinxRoles(griffe.Extension):
    def on_instance(self, *, obj: griffe.Object, **kwargs: Any) -> None:
        if obj.docstring is not None:
            obj.docstring.value = _ROLE.sub(_replace, obj.docstring.value)

"""Shared BibTeX preparation and author-based ordering."""
from copy import deepcopy
import re

from pybtex.richtext import Text
from unidecode import unidecode


def bibliography_entry_for_html(entry):
    """Keep a TeX-only publication link usable in the HTML bibliography."""
    link = re.fullmatch(r"\s*\\href\{(https?://[^{}]+)\}\{([^{}]+)\}\s*",
                        entry.fields.get("howpublished", ""))
    if link is None:
        return entry
    result = deepcopy(entry)
    result.fields["howpublished"] = link[2]
    result.fields.setdefault("url", link[1])
    return result


def bibliography_sort_key(entry):
    """Sort structured surnames and coauthors, then year and title."""
    def normalize(value):
        return unidecode(Text.from_latex(value).render_as("text")).casefold()

    people = entry.persons.get("author") or entry.persons.get("editor", [])
    names = "   ".join(
        "  ".join(normalize(" ".join(parts)) for parts in (
            person.prelast_names + person.last_names,
            person.first_names + person.middle_names,
            person.lineage_names,
        )) for person in people
    )
    fields = entry.fields
    return [names or normalize(fields.get("organization") or fields.get("title", "")),
            normalize(fields.get("year", "")), normalize(fields.get("title", ""))]

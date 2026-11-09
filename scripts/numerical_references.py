"""Render the unnumbered figure-methods and visual-credit page."""
from html import escape
from pathlib import Path

from pybtex.database import parse_file
from pybtex.plugin import find_plugin

from bibliography_metadata import bibliography_entry_for_html, bibliography_sort_key

ROOT = Path(__file__).resolve().parents[1]


def page():
    content = (ROOT / 'content' / 'numerical-references.html').read_text()
    database = parse_file(ROOT / 'content' / 'numerical-references.bib')
    style = find_plugin('pybtex.style.formatting', 'plain')()
    backend = find_plugin('pybtex.backends', 'html')()
    records = []
    for key, entry in sorted(database.entries.items(),
                             key=lambda item: (bibliography_sort_key(item[1]), item[0])):
        formatted = next(iter(style.format_entries([bibliography_entry_for_html(entry)])))
        records.append(f'<article class="bibliography-entry" id="{escape(key, quote=True)}">'
                       f'<h3 class="reference-key">[{escape(key)}]</h3>'
                       f'<p>{formatted.text.render(backend)}</p>'
                       f'<p>{escape(entry.fields["annote"])}</p></article>')
    return content.replace('<!-- numerical-bibliography -->', '\n'.join(records))

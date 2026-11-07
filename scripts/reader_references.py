"""Page-local citations and links back from the shared bibliography."""
from html import escape
import re
from bs4 import BeautifulSoup


def citation_label(source, key):
    """Hide the catalogue's internal namespace without changing source keys."""
    if source == "gmt-foundations" and re.match(r"Cat(?=[A-Z])", key):
        return key[3:]
    return key


def reference_label(record):
    return ", ".join(dict.fromkeys(citation_label(item["source"], item["key"])
                                  for item in record["sources"]))


def page_references(content, references, root):
    soup = BeautifulSoup(content, "html.parser")
    used = {}
    for anchor in soup.select("a[data-reference]"):
        identifier = anchor["data-reference"]
        record = references[identifier]
        occurrences = used.setdefault(identifier, [])
        citation_id = f"cite-{identifier}-{len(occurrences) + 1}"
        occurrences.append(citation_id)
        anchor["id"] = citation_id
        anchor["href"] = "#reference-" + identifier
        anchor["class"] = [*anchor.get("class", []), "reference-link"]
        anchor["title"] = BeautifulSoup(record["html"], "html.parser").get_text(" ", strip=True)
    if not used:
        return content, []
    section = '<section class="page-references" aria-label="References on this page"><h2>References on this page</h2><ol>'
    for identifier, occurrences in used.items():
        record = references[identifier]
        keys = reference_label(record)
        section += f'<li id="reference-{identifier}"><span class="reference-key">[{escape(keys)}]</span> {record["html"]}'
        section += f'<span class="reference-actions"><a href="{root}references/#{identifier}">All uses in this project</a>'
        for number, citation_id in enumerate(occurrences, 1):
            section += f' <a href="#{citation_id}" aria-label="Back to citation {number} of {escape(keys, quote=True)}">↩ {number}</a>'
        section += '</span></li>'
    return str(soup) + section + '</ol></section>', list(used)


def bibliography(references, uses):
    content = '<h1>Bibliography</h1><p>References are listed alphabetically by author surname, then by coauthors, year, and title. Follow a reference to the reading pages that use it. Citations within a page open its local reference list, with return links to the text.</p>'
    if not references:
        return content + '<p>No references have been added yet.</p>'
    ordered = sorted(references.items(), key=lambda item: (
        item[1].get("sort_key", [BeautifulSoup(item[1]["html"], "html.parser").get_text().casefold(), "", ""]),
        item[0],
    ))
    for identifier, record in ordered:
        keys = reference_label(record)
        content += f'<article class="bibliography-entry" id="{identifier}"><h2 class="reference-key">[{escape(keys)}]</h2><p>{record["html"]}</p>'
        pages = uses.get(identifier, {})
        if pages:
            content += '<details class="reference-uses"><summary>Used in this project (' + str(len(pages)) + ' pages)</summary><ul>'
            for route, title in pages.items():
                content += f'<li><a href="../{route}/#reference-{identifier}">{escape(title)}</a></li>'
            content += '</ul></details>'
        content += '</article>'
    return content


def source_catalogue(inventory, source, reference_map, root):
    files = inventory.get("files", [])
    if not files:
        return ""
    groups = {"Cited sources and checked passages": [], "Catalogued for further study": []}
    for item in files:
        cited = (source, item.get("bibliography_key")) in reference_map
        groups["Cited sources and checked passages" if cited else "Catalogued for further study"].append(item)
    html = '<section id="reference-library"><h2>Reference library</h2><p>The library records supplied files and their study status. A catalogue entry does not mean that its results have been incorporated. Original books, scans, and extracted text are not distributed.</p>'
    for heading, items in groups.items():
        if not items:
            continue
        html += f'<details class="source-catalogue"><summary>{heading} ({len(items)} files)</summary><ul>'
        for item in sorted(items, key=lambda item: item.get("title", item["filename"]).casefold()):
            title = escape(item.get("title", item["filename"]))
            identifier = reference_map.get((source, item.get("bibliography_key")))
            if identifier:
                title = f'<a href="{root}references/#{identifier}">{title}</a>'
            html += f'<li>{title}<small>{escape(item.get("author", ""))} · {escape(item.get("edition", ""))}</small>'
            html += f'<small>{escape(item.get("role", ""))}</small>'
            if item.get("same_content_as"):
                html += f'<small>Identical file content: {escape(item["same_content_as"])}</small>'
            html += '</li>'
        html += '</ul></details>'
    return html + '</section>'

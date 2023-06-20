# Imports
import json

import requests
from bs4 import BeautifulSoup

PATCH_NUMBER = 12


# Build the patch URL (only season 13)
def build_patch_url(patch: int):
    return f"https://www.leagueoflegends.com/en-us/news/game-updates/patch-13-{patch}-notes/"


# Parse the changes of a champion
def parse_champion_changes():
    # Find champion name
    champion = change.find("h3").text

    # Find champion icon
    icon = change.find("img")["src"]
    icon = icon.replace("https://am-a.akamaihd.net/image?f=", "")

    # Find change summary
    summary = change.find("p", {"class": "summary"})
    summary = summary.text

    # Find change context
    context = change.find("blockquote").text.strip()
    context = context.replace("\n\n\t\t\t\t\t", " <br> ")

    # Find changes
    changes = []
    for ch in change.find_all("h4"):
        # Find spell name
        spell = ch.text

        # Find spell changes
        spell_change_elements = ch.next_sibling.next_sibling.find_all("li")
        spell_changes = parse_spell_changes(spell_change_elements)

        changes.append({"spell": spell, "changes": spell_changes})

        # Return champion changes
        return {
            "champion": champion,
            "icon": icon,
            "summary": summary,
            "context": context,
            "changes": changes,
        }


# Parse the changes of a spell
def parse_spell_changes(spell_changes):
    changes = []
    # Parse spell changes
    for spell_change in spell_changes:
        # Find change type
        type = spell_change.find("strong").text

        # Find previous and next values
        prevNext = spell_change.text.replace(type, "").split("⇒")
        previous = ""
        new = ""

        # Two cases :
        # - a previous value is replaced by a new value
        # - the change is the addition or the removal of a mechanic
        if len(prevNext) == 2:
            previous = prevNext[0].replace(":", "").strip()
            new = prevNext[1].replace(":", "").strip()
        else:
            new = prevNext[0].replace(":", "").strip()

        # Append change to list
        changes.append({"type": type, "previous": previous, "new": new})

    # Return changes
    return changes


# Main entry of the app
if __name__ == "__main__":
    # Send a GET request to the website
    url = build_patch_url(PATCH_NUMBER)
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Init output
    output = {}

    # Get section list
    sections = soup.find_all("header")

    # Parse the sections
    for section in sections:
        section_title = section.text.strip()
        if section_title == "":
            continue

        # Add section to output
        output[section_title] = []

        # Parse section
        for change in section.find_next_siblings():
            if any(title.text == change.text for title in sections):
                break

            # Switch changes
            changes = {}
            if section_title == "Champions":
                changes = parse_champion_changes()

            # Add to output
            output[section_title].append(changes)

    # Write output to file
    with open(f"patch-13-{PATCH_NUMBER}.json", "w", encoding="utf-8") as f:
        print(f"Wrote output to patch-13-{PATCH_NUMBER}.json")
        json.dump(output, f, ensure_ascii=False, indent=4)

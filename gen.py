#!/usr/bin/env python3
from typing import Optional, Any
import os
import sys
import argparse
import re
import genanki  # type: ignore


def main(
    nome_file: str, deck_name: str, version: int, obsidian_assets_folder: Optional[str]
) -> None:
    # Define Anki note model
    model_id = 1345664314
    model = genanki.Model(
        model_id,
        "Custom Model",
        fields=[
            {"name": "Question"},
            {"name": "Answer"},
        ],
        templates=[
            {
                "name": "QA",
                "qfmt": "{{Question}}",
                "afmt": "{{Answer}}",
            },
            # {
            #     'name': 'AQ',
            #     'qfmt': '{{Answer}}',
            #     'afmt': '{{Question}}',
            # },
        ],
    )

    # Generate Anki cards and add them to a deck
    deck_id = 3145744450
    deck = genanki.Deck(deck_id, deck_name)

    if version == 1:
        count, media_files = generate_v1(nome_file, model, deck, obsidian_assets_folder)
    elif version == 2:
        count = generate_v2(nome_file, model, deck)
        # TODO: Hardcoded media files
        media_files = []
    else:
        exit(1)

    # Save the deck to an Anki package (*.apkg) file
    file_dir = os.path.dirname(nome_file)

    # Fix media files path
    media_files = fix_media_files_path(file_dir, media_files)

    # Generate output
    output = f"{deck_name.lower().replace(' ', '_')}.apkg"
    package = genanki.Package(deck)
    package.media_files = media_files
    package.write_to_file(os.path.join(file_dir, output))
    print("Saved", count, "flashcards")


def fix_media_files_path(dir: str, media_files: list[str]) -> list[str]:
    fixed_media_files = []
    for media in media_files:
        fixed_media_files.append(os.path.join(dir, media))

    return fixed_media_files


def save_question_v1(
    dict: dict[str, list[tuple[str, str]]],
    current_title: Any,
    question_rows: list[str],
    answer_rows: list[str],
) -> None:
    if question_rows and answer_rows:
        dict[current_title].append(("\n".join(question_rows), "\n".join(answer_rows)))


def save_question_v2(
    dict: dict[str, list[tuple[str, str, str, str]]],
    current_chapter: Any,
    current_subchapter: Any,
    current_subsubchapter: Any,
    question_rows: list[str],
    answer_rows: list[str],
) -> None:
    if question_rows and answer_rows:
        dict[current_chapter].append(
            (
                current_subchapter,
                current_subsubchapter,
                "\n".join(question_rows),
                "\n".join(answer_rows),
            )
        )


def fix_string(content: str) -> str:
    content = (
        content.strip()
        .replace("<", "&lt")
        .replace(">", "&gt")
        .replace("# ", "")
        .replace("#", "")
    )

    # Find the index of the first letter in the alphabet
    match = re.search(r"[A-Za-z]", content)
    if match is None:
        return content

    first_letter_index = match.start()

    # Make the first letter uppercase
    stringa_modificata = (
        content[:first_letter_index]
        + content[first_letter_index].upper()
        + content[first_letter_index + 1 :]
    )

    return stringa_modificata


def parse_media_images(
    markdown_text: str, obsidian_assets_folder: Optional[str]
) -> tuple[str, list[str]]:
    def markdown_to_html_images(markdown_text: str) -> tuple[str, list[str]]:
        image_paths = []  # Inizializza il vettore per i percorsi delle immagini

        def replace_image(match: re.Match[str]) -> str:
            alt_text = (
                match.group(1) if match.group(1) else ""
            )  # Gestisci l'assenza dell'alt text
            image_path = match.group(2)
            image_paths.append(
                image_path
            )  # Aggiungi il percorso dell'immagine alla lista
            image_filename = image_path.split("/")[-1]  # Estrai solo il nome del file
            image_tag = f'<img src="{image_filename}" alt="{alt_text}">'
            return image_tag

        # Trova tutte le immagini in formato Markdown e sostituiscile con i tag HTML
        pattern = r"\!\[([^\]]*)\]\(([^)]+)\)"
        html_text = re.sub(pattern, replace_image, markdown_text)

        return html_text, image_paths

    def obsidian_md_to_html_images(
        markdown_text: str, obsidian_assets_folder: str
    ) -> tuple[str, list[str]]:
        image_paths = []  # Inizializza il vettore per i percorsi delle immagini

        def replace_image(match: re.Match[str]) -> str:
            image_path = match.group(1)
            full_image_path = os.path.join(obsidian_assets_folder, image_path)
            image_paths.append(full_image_path)  # Add Obsidian image path to the list
            image_filename = image_path.split("/")[-1]  # Estrai solo il nome del file
            return f'<img src="{image_filename}">'

        # Trova tutte le immagini nel formato Markdown di Obsidian e sostituiscile con i tag HTML
        pattern = r"\!\[\[([^\]]+)\]\]"
        html_text = re.sub(pattern, replace_image, markdown_text)

        return html_text, image_paths

    # START FUNCTION
    if obsidian_assets_folder is not None:
        return obsidian_md_to_html_images(markdown_text, obsidian_assets_folder)
    else:
        return markdown_to_html_images(markdown_text)


def generate_v1(
    nome_file: str,
    model: genanki.Model,
    deck: genanki.Deck,
    obsidian_assets_folder: Optional[str],
) -> tuple[int, list[str]]:
    media_files = []
    text_parsed_data = md_question_parse_v1(nome_file)
    count = 0
    for chapter in text_parsed_data:
        # print("- Chapter:", chapter)
        for q, a in text_parsed_data[chapter]:
            # print("    Q:", q.replace('\n', ' | '))
            # print("      A:", a.replace('\n', ' | '))

            # Search Images in Question
            q, media = parse_media_images(q, obsidian_assets_folder)
            # Append media files to the list
            for media_file in media:
                media_files.append(media_file)

            # Search Images in Answer
            a, media = parse_media_images(a, obsidian_assets_folder)
            # Append media files to the list
            for media_file in media:
                media_files.append(media_file)

            # Fix other
            q = q.replace("\n", "<br>")
            q = f"<h1>{chapter}</h1>{q}"
            a = a.replace("\n", "<br>")
            note = genanki.Note(model=model, fields=[q, a])
            deck.add_note(note)
            count += 1
    return count, media_files


def generate_v2(nome_file: str, model: genanki.Model, deck: genanki.Deck) -> int:
    text_parsed_data = md_question_parse_v2(nome_file)
    count = 0
    for chapter in text_parsed_data:
        # print("#  ", chapter)
        for c2, c3, q, a in text_parsed_data[chapter]:
            # print("## ", c2)
            # print("###", c3)
            # print("    Q:", q.replace('\n', ' | '))
            # print("      A:", a.replace('\n', ' | '))
            q = q.replace("\n", "<br>")
            q = f"<h3>{c3}</h3>{q}"
            q = f"<h2>{c2}</h2>{q}"
            q = f"<h1>{chapter}</h1>{q}"
            a = a.replace("\n", "<br>")
            note = genanki.Note(model=model, fields=[q, a])
            deck.add_note(note)
            count += 1
    return count


def md_question_parse_v2(nome_file: str) -> dict[str, list[tuple[str, str, str, str]]]:
    dict_parsed: dict[str, list[tuple[str, str, str, str]]] = {}
    current_chapter = None
    current_subchapter = None
    current_subsubchapter = None
    question_rows: list[str] = []
    answer_rows: list[str] = []
    is_question = True

    with open(nome_file, "r") as file:
        contenuto = file.readlines()

    for riga in contenuto:
        if riga.startswith("# "):
            save_question_v2(
                dict_parsed,
                current_chapter,
                current_subchapter,
                current_subsubchapter,
                question_rows,
                answer_rows,
            )
            question_rows = []
            answer_rows = []

            current_chapter = fix_string(riga)
            current_subchapter = None
            current_subsubchapter = None
            dict_parsed[current_chapter] = []

        elif riga.startswith("## "):
            save_question_v2(
                dict_parsed,
                current_chapter,
                current_subchapter,
                current_subsubchapter,
                question_rows,
                answer_rows,
            )
            question_rows = []
            answer_rows = []

            current_subchapter = fix_string(riga)
            current_subsubchapter = None

        elif riga.startswith("### "):
            save_question_v2(
                dict_parsed,
                current_chapter,
                current_subchapter,
                current_subsubchapter,
                question_rows,
                answer_rows,
            )
            question_rows = []
            answer_rows = []

            current_subsubchapter = fix_string(riga)

        elif riga.startswith("#### "):
            save_question_v2(
                dict_parsed,
                current_chapter,
                current_subchapter,
                current_subsubchapter,
                question_rows,
                answer_rows,
            )
            question_rows = []
            answer_rows = []

            question_rows.append(fix_string(riga))
            is_question = True

        elif riga.strip() == "---":
            is_question = False

        else:
            if is_question:
                question_rows.append(fix_string(riga))
            else:
                answer_rows.append(fix_string(riga))

    # Save last flashcard
    save_question_v2(
        dict_parsed,
        current_chapter,
        current_subchapter,
        current_subsubchapter,
        question_rows,
        answer_rows,
    )

    return dict_parsed


def md_question_parse_v1(nome_file: str) -> dict[str, list[tuple[str, str]]]:
    dict_parsed: dict[str, list[tuple[str, str]]] = {}
    current_title = None
    question_rows: list[str] = []
    answer_rows: list[str] = []
    is_question = True

    with open(nome_file, "r") as file:
        contenuto = file.readlines()

    for riga in contenuto:
        if riga.startswith("# "):
            save_question_v1(dict_parsed, current_title, question_rows, answer_rows)
            question_rows = []
            answer_rows = []

            current_title = fix_string(riga[2:])  # removes '# ' and whitespaces
            dict_parsed[current_title] = []

        elif riga.startswith("## "):
            save_question_v1(dict_parsed, current_title, question_rows, answer_rows)
            question_rows = []
            answer_rows = []

            question_rows.append(fix_string(riga[3:]))
            is_question = True

        elif riga.strip() == "---":
            is_question = False

        else:
            if is_question:
                question_rows.append(fix_string(riga))
            else:
                answer_rows.append(fix_string(riga))

    save_question_v1(dict_parsed, current_title, question_rows, answer_rows)

    return dict_parsed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Markdown to Anki Deck")

    default_nome_file = "___default_file_name_error___"
    default_obsidian_assets = "___default_obsidian-assets_error___"

    parser.add_argument(
        "input_file", nargs="?", default=default_nome_file, help="Input Markdown file"
    )
    parser.add_argument(
        "-o", "--output", default="MD2AnkiDeckOutput", help="Output Anki Deck name"
    )
    parser.add_argument(
        "-v",
        "--version",
        type=int,
        choices=[1, 2],
        default=1,
        help="Anki Deck version (1 or 2)",
    )
    parser.add_argument(
        "--use-obsidian-format",
        action="store_true",
        help="Use Obsidian Markdown format",
    )
    parser.add_argument(
        "-a",
        "--obsidian-assets",
        default=default_obsidian_assets,
        help="Obsidian Assets Folder path",
    )

    args = parser.parse_args()

    # Check Input File Name
    input_file = args.input_file

    if input_file == default_nome_file:
        print("Errore: specificare un file di input.")
        sys.exit(1)
    elif not os.path.isfile(input_file):
        print(f"Errore: il file '{input_file}' non esiste.")
        sys.exit(1)

    # Check Obsidian Assets Folder
    use_obsidian_format = args.use_obsidian_format
    obsidian_assets = args.obsidian_assets
    obsidian_assets_folder = None
    if use_obsidian_format:
        if obsidian_assets == default_obsidian_assets:
            print("Errore: specificare la cartella degli assets di Obsidian.")
            sys.exit(1)
        elif not os.path.isdir(
            os.path.join(os.path.dirname(input_file), obsidian_assets)
        ):
            print(f"Errore: la cartella '{obsidian_assets}' non esiste.")
            sys.exit(1)
        else:
            obsidian_assets_folder = obsidian_assets

    # Altri parametri
    output_deck = args.output
    deck_version = args.version

    # Stampa i valori utilizzati
    print(
        f'Converting file: {input_file} to: {output_deck}.apkg\nVersion: {deck_version}\nUse Obsidian Format: {use_obsidian_format} (Path: "{obsidian_assets_folder}")'
    )
    main(input_file, output_deck, int(deck_version), obsidian_assets_folder)

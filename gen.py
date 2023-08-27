#!/usr/bin/env python3
import os
import sys
import argparse
import re
import genanki

def main(nome_file, deck_name, version, use_obsidian_format):
  # Define Anki note model
  model_id = 1345664314
  model = genanki.Model(
      model_id,
      'Custom Model',
      fields=[
          {'name': 'Question'},
          {'name': 'Answer'},
      ],
      templates=[
          {
              'name': 'QA',
              'qfmt': '{{Question}}',
              'afmt': '{{Answer}}',
          },
          # {
          #     'name': 'AQ',
          #     'qfmt': '{{Answer}}',
          #     'afmt': '{{Question}}',
          # },
      ])
  
  # Generate Anki cards and add them to a deck
  deck_id = 3145744450
  deck = genanki.Deck(deck_id, deck_name)

  if version == 1:
    count, media_files = generate_v1(nome_file, model, deck, use_obsidian_format)
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
  print("Saved" ,count, "flashcards")

def fix_media_files_path(dir, media_files):
  fixed_media_files = []
  for media in media_files:
    fixed_media_files.append(os.path.join(dir, media))
  
  return fixed_media_files
  

def save_question_v1(dict, current_title, question_rows, answer_rows):
  if question_rows and answer_rows:
    dict[current_title].append(('\n'.join(question_rows), '\n'.join(answer_rows)))


def save_question_v2(dict, current_chapter, current_subchapter, current_subsubchapter, question_rows, answer_rows):
  if question_rows and answer_rows:
    dict[current_chapter].append((current_subchapter, current_subsubchapter, '\n'.join(question_rows), '\n'.join(answer_rows)))


def fix_string(content):
    content = content.strip().replace('<', '&lt').replace('>', '&gt').replace('# ', '').replace('#', '')
  
    # Find the index of the first letter in the alphabet
    match = re.search(r'[A-Za-z]', content)
    if match is None:
      return content
    
    first_letter_index = match.start()

    # Make the first letter uppercase
    stringa_modificata = content[:first_letter_index] + content[first_letter_index].upper() + content[first_letter_index+1:]

    return stringa_modificata

  
def parse_media_images(markdown_text, use_obsidian_format):
    def markdown_to_html_images(markdown_text):
        image_paths = []  # Inizializza il vettore per i percorsi delle immagini
        
        def replace_image(match):
            alt_text = match.group(1) if match.group(1) else ""  # Gestisci l'assenza dell'alt text
            image_path = match.group(2)
            image_paths.append(image_path)  # Aggiungi il percorso dell'immagine alla lista
            image_filename = image_path.split('/')[-1]  # Estrai solo il nome del file
            image_tag = f'<img src="{image_filename}" alt="{alt_text}">'
            return image_tag
        
        # Trova tutte le immagini in formato Markdown e sostituiscile con i tag HTML
        pattern = r'\!\[([^\]]*)\]\(([^)]+)\)'
        html_text = re.sub(pattern, replace_image, markdown_text)
        
        return html_text, image_paths
      
    def obsidian_md_to_html_images(markdown_text):
        image_paths = []  # Inizializza il vettore per i percorsi delle immagini
        
        def replace_image(match):
            image_path = match.group(1)
            image_paths.append(image_path)  # Aggiungi il percorso dell'immagine alla lista
            image_filename = image_path.split('/')[-1]  # Estrai solo il nome del file
            return f'<img src="{image_filename}">'
        
        # Trova tutte le immagini nel formato Markdown di Obsidian e sostituiscile con i tag HTML
        pattern = r'\!\[\[([^\]]+)\]\]'
        html_text = re.sub(pattern, replace_image, markdown_text)
        
        return html_text, image_paths

    # START FUNCTION
    if use_obsidian_format:
        return obsidian_md_to_html_images(markdown_text)
    else:
        return markdown_to_html_images(markdown_text)


def generate_v1(nome_file, model, deck, use_obsidian_format):
  media_files = []
  text_parsed_data = md_question_parse_v1(nome_file)
  count = 0
  for chapter in text_parsed_data:
    # print("- Chapter:", chapter)
    for q, a in text_parsed_data[chapter]:
      # print("    Q:", q.replace('\n', ' | '))
      # print("      A:", a.replace('\n', ' | '))

      # Search Images in Question
      q, media = parse_media_images(q, use_obsidian_format)
      # Append media files to the list
      for media_file in media:
          media_files.append(media_file)

      # Search Images in Answer
      a, media = parse_media_images(a, use_obsidian_format)
      # Append media files to the list
      for media_file in media:
          media_files.append(media_file)

      # Fix other
      q = q.replace('\n', '<br>')
      q = f"<h1>{chapter}</h1>{q}"
      a = a.replace('\n', '<br>')
      note = genanki.Note(model=model, fields=[q, a])
      deck.add_note(note)
      count += 1  
  return count, media_files


def generate_v2(nome_file, model, deck):
  text_parsed_data = md_question_parse_v2(nome_file)
  count = 0
  for chapter in text_parsed_data:
    # print("#  ", chapter)
    for c2, c3, q, a in text_parsed_data[chapter]:
      # print("## ", c2)
      # print("###", c3)
      # print("    Q:", q.replace('\n', ' | '))
      # print("      A:", a.replace('\n', ' | '))
      q = q.replace('\n', '<br>')
      q = f"<h3>{c3}</h3>{q}"
      q = f"<h2>{c2}</h2>{q}"
      q = f"<h1>{chapter}</h1>{q}"
      a = a.replace('\n', '<br>')
      note = genanki.Note(model=model, fields=[q, a])
      deck.add_note(note)
      count += 1  
  return count


def md_question_parse_v2(nome_file):
    dict_parsed = {}
    current_chapter = None
    current_subchapter = None
    current_subsubchapter = None
    question_rows = []
    answer_rows = []
    is_question = True
  
    with open(nome_file, 'r') as file:
        contenuto = file.readlines()
    
    for riga in contenuto:
        if riga.startswith('# '):
            save_question_v2(dict_parsed, current_chapter, current_subchapter, current_subsubchapter, question_rows, answer_rows)
            question_rows = []
            answer_rows = []
            
            current_chapter = fix_string(riga)
            current_subchapter = None
            current_subsubchapter = None
            dict_parsed[current_chapter] = []
        
        elif riga.startswith('## '):
            save_question_v2(dict_parsed, current_chapter, current_subchapter, current_subsubchapter, question_rows, answer_rows)
            question_rows = []
            answer_rows = []
                        
            current_subchapter = fix_string(riga)
            current_subsubchapter = None
        
        elif riga.startswith('### '):
            save_question_v2(dict_parsed, current_chapter, current_subchapter, current_subsubchapter, question_rows, answer_rows)
            question_rows = []
            answer_rows = []
                        
            current_subsubchapter = fix_string(riga)
        
        elif riga.startswith('#### '):
            save_question_v2(dict_parsed, current_chapter, current_subchapter, current_subsubchapter, question_rows, answer_rows)
            question_rows = []
            answer_rows = []
                        
            question_rows.append(fix_string(riga))
            is_question = True
        
        elif riga.strip() == '---':
            is_question = False
        
        else:
          if is_question:
            question_rows.append(fix_string(riga))
          else:
            answer_rows.append(fix_string(riga))
    
    # Save last flashcard
    save_question_v2(dict_parsed, current_chapter, current_subchapter, current_subsubchapter, question_rows, answer_rows)
    
    return dict_parsed


def md_question_parse_v1(nome_file):
    dict_parsed = {}
    current_title = None
    question_rows = []
    answer_rows = []
    is_question = True
  
    with open(nome_file, 'r') as file:
        contenuto = file.readlines()
    
    for riga in contenuto:
        if riga.startswith('# '):
            save_question_v1(dict_parsed, current_title, question_rows, answer_rows)
            question_rows = []
            answer_rows = []
            
            current_title = fix_string(riga[2:]) # removes '# ' and whitespaces
            dict_parsed[current_title] = []
        
        elif riga.startswith('## '):
            save_question_v1(dict_parsed, current_title, question_rows, answer_rows)
            question_rows = []
            answer_rows = []
                        
            question_rows.append(fix_string(riga[3:]))
            is_question = True
        
        elif riga.strip() == '---':
            is_question = False
        
        else:
          if is_question:
            question_rows.append(fix_string(riga))
          else:
            answer_rows.append(fix_string(riga))
    
    save_question_v1(dict_parsed, current_title, question_rows, answer_rows)
    
    return dict_parsed


if __name__ == '__main__':
  # if len(sys.argv) < 3:
  #   print("Usage: python3 gen.py <nome_file> <nome_deck> <version>")
  #   exit(1)  

  # _, nome_file, nome_deck, version = sys.argv
  # main(nome_file, nome_deck, int(version))
  
  ###########
  
  # Parser degli argomenti da riga di comando
  parser = argparse.ArgumentParser(description='Convert Markdown to Anki Deck')
  
  default_nome_file = '___default_file_name_error___'
  
  parser.add_argument('input_file', nargs='?', default=default_nome_file, help='Input Markdown file')
  parser.add_argument('-o', '--output', default='MD2AnkiDeckOutput', help='Output Anki Deck name')
  parser.add_argument('-v', '--version', type=int, choices=[1, 2], default=1, help='Anki Deck version (1 or 2)')
  parser.add_argument('--use-obsidian-format', action='store_true', help='Use Obsidian Markdown format')
  
  args = parser.parse_args()
  
  # Estrai i valori dagli argomenti
  input_file = args.input_file
  
  if input_file == default_nome_file:
      print("Errore: specificare un file di input.")
      sys.exit(1)
  elif not os.path.isfile(input_file):
      print(f"Errore: il file '{input_file}' non esiste.")
      sys.exit(1)
  
  # Altri parametri
  output_deck = args.output
  deck_version = args.version
  use_obsidian_format = args.use_obsidian_format
  
  # Stampa i valori utilizzati
  print(f'Converting file: {input_file} to: {output_deck}.apkg\nVersion: {deck_version}\nUse Obsidian Format: {use_obsidian_format}')
  main(input_file, output_deck, int(deck_version), use_obsidian_format)
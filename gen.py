#!/usr/bin/env python3
import os
import sys
import re
import genanki

def main(nome_file, deck_name, version):
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
    count = generate_v1(nome_file, model, deck)
  elif version == 2:
    count = generate_v2(nome_file, model, deck)
  else:
    exit(1)

  # Save the deck to an Anki package (*.apkg) file
  file_dir = os.path.dirname(nome_file)
  output = f"{deck_name.lower().replace(' ', '_')}.apkg"
  genanki.Package(deck).write_to_file(os.path.join(file_dir, output))
  print("Saved" ,count, "flashcards")


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


def generate_v1(nome_file, model, deck):
  text_parsed_data = md_question_parse_v1(nome_file)
  count = 0
  for chapter in text_parsed_data:
    # print("- Chapter:", chapter)
    for q, a in text_parsed_data[chapter]:
      # print("    Q:", q.replace('\n', ' | '))
      # print("      A:", a.replace('\n', ' | '))
      q = q.replace('\n', '<br>')
      q = f"<h1>{chapter}</h1>{q}"
      a = a.replace('\n', '<br>')
      note = genanki.Note(model=model, fields=[q, a])
      deck.add_note(note)
      count += 1  
  return count


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
  if len(sys.argv) < 3:
    print("Usage: python3 gen.py <nome_file> <nome_deck> <version>")
    exit(1)  

  _, nome_file, nome_deck, version = sys.argv
  main(nome_file, nome_deck, int(version))
import sys
import re
import genanki

def main(nome_file, deck_name):
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

  text_parsed_data = md_question_parse(nome_file)
  count = 0
  for chapter in text_parsed_data:
    for q, a in text_parsed_data[chapter]:
      q = q.replace('\n', '<br>')
      q = f"<h1>{chapter}</h1>{q}"
      a = a.replace('\n', '<br>')
      note = genanki.Note(model=model, fields=[q, a])
      deck.add_note(note)
      count += 1

  # Save the deck to an Anki package (*.apkg) file
  genanki.Package(deck).write_to_file(f"out/{deck_name.lower().replace(' ', '_')}.apkg")
  print("Saved" ,count, "flashcards")


def md_question_parse(nome_file):
    dict_parsed = {}
    current_title = None
    question_rows = []
    answer_rows = []
    is_question = True
    
    def save_question(dict, current_title, question_rows, answer_rows):
      if question_rows and answer_rows:
        dict[current_title].append(('\n'.join(question_rows), '\n'.join(answer_rows)))

    def fix_string(content):
        content = content.strip().replace('<', '&lt').replace('>', '&gt')
      
        # Find the index of the first letter in the alphabet
        match = re.search(r'[A-Za-z]', content)
        if match is None:
          return content
        
        first_letter_index = match.start()

        # Make the first letter uppercase
        stringa_modificata = content[:first_letter_index] + content[first_letter_index].upper() + content[first_letter_index+1:]

        return stringa_modificata
  
  
    with open(nome_file, 'r') as file:
        contenuto = file.readlines()
    
    
    for riga in contenuto:
        if riga.startswith('# '):
            save_question(dict_parsed, current_title, question_rows, answer_rows)
            question_rows = []
            answer_rows = []
            
            current_title = fix_string(riga[2:]) # removes '# ' and whitespaces
            dict_parsed[current_title] = []
        
        elif riga.startswith('## '):
            save_question(dict_parsed, current_title, question_rows, answer_rows)
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
    
    save_question(dict_parsed, current_title, question_rows, answer_rows)
    
    return dict_parsed


if __name__ == '__main__':
  if len(sys.argv) < 2:
    print("Usage: python3 gen.py <nome_file> <nome_deck>")
    exit(1)  

  _, nome_file, nome_deck = sys.argv
  main(nome_file, nome_deck)
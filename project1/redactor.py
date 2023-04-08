import sys
import usaddress
import argparse
import glob
import os
import re
import spacy
import datefinder
from spacy.matcher import Matcher

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--input", nargs='+', required=True, help="Incident summary url.")
  parser.add_argument("--names",  action='store_true', help="Redact names.")
  parser.add_argument("--dates",  action='store_true', help="Redact dates.")  
  parser.add_argument("--phones",  action='store_true', help="Redact phone numbers.")
  parser.add_argument("--genders",  action='store_true', help="Redact genders.")
  parser.add_argument("--address",  action='store_true', help="Redact actual physical addresses.")
  parser.add_argument('--output', type=str, required=True, help='Output directory for redacted files')
  parser.add_argument('--stats', type=str, default=None, help='File or location to write redaction statistics') 
  args = parser.parse_args()

  nlp = spacy.load('en_core_web_sm')

  matcher = Matcher(nlp.vocab)

  input_files = []
  for type in args.input:
    input_files += glob.glob(type)
  if not input_files:
    print("No input files")
    exit()
  if not os.path.exists(args.output):
    os.makedirs(args.output)

  genders = ['boyfriend','girlfriend','mistress','lady','he','himself', 'herself','sir','madam','dude','mister',
             'fiance','spouse','wife','husband','housewife','widow','bride','she', 'him', 'her', 'his', 'hers',
             'gent','masculine','bloke','widower','mister' ,'woman','man','groom', 'his', 'female', 'male', 'Mr','Mrs',
             'son','daughter','dude','Miss', 'Ms', 'boy','girl','father','hubby','duchess','diva','mistress','mama','feminine',
             'mother','guy', 'brother', 'sister','man','woman','nephew','neice','gal','prince','princess']
  phone_pattern2 = re.compile(r"\+?1?[-\s]?(?:\(\d{3}\)|\d{3})[-\s]?\d{3}[-\s]?\d{4}")
  pattern_name = [{"ENT_TYPE": "PERSON"}]
  matcher.add("PERSON", [pattern_name])
  date_patterns =[re.compile(r"\d{1,2}\/\d{1,2}\/\d{2,4}"),
                  re.compile(r"\d{1,2}[\s]?[A-Z][a-z]{2}[\s]?\d{4}"),
                  re.compile(r"\b[A-Z][a-z]{2,10}[.,]?\s\d{1,2}\b")]
  pattern_addy = [re.compile(r"\b\d+\s+\w+\s?\w+\s?,?\s*\b"), re.compile(r"\b\d{5}-\d{4}\b")]

  redactions = {}
  if args.names:
        redactions['names'] = True
  if args.genders:
        redactions['genders'] = True
  if args.dates:
        redactions['dates'] = True
  if args.phones:
        redactions['phones'] = True
  if args.address:
        redactions['address'] = True

  for file in input_files:
    with open(file, 'r') as f:
     text = f.read()

    doc = nlp(text)

    names = []
    count_names = 0
    if not redactions.get('names'):
       pass
    else:
      for match_id, start, end in matcher(doc):
        span = doc[start:end]
        if len(span.text) > 2 and not re.search(r'[^\w\s]', span.text):
          names.append(span.text)
          names = [item.strip() for item in names if item.strip()]
          count_names = len(names)
          text = re.sub(r'{}'.format(re.escape(span.text)),'█'*len(span.text) + " ", text, flags=re.IGNORECASE)

    genders_found = []
    count_genders = 0
    if not redactions.get('genders'):
       pass
    else:
         for terms in genders:
          gender_match = re.findall(terms, text)
          genders_found.append(gender_match)
          genders_found = [sublist for sublist in genders_found if sublist != []]
          count_genders = len(genders_found)
          text = re.sub(r'\b{}\b'.format(terms),'█'*len(terms), text, flags=re.IGNORECASE)

    numbers_found= []
    count_numbers = 0
    if not redactions.get('phones'):
       pass
    else:
        number_matches = re.findall(phone_pattern2, text)
        for number in number_matches:
            if len(number) > 11:
             numbers_found.append(number)
             numbers_found = [s.replace('\n','') for s in numbers_found]
             count_numbers = len(numbers_found)
             text = phone_pattern2.sub(lambda match: re.sub(r'\d', '█', match.group(0)), text) 

    dates_found = []
    count_dates = 0
    if not redactions.get('dates'):
       pass
    else:
        for patterns in date_patterns:
           matches_dates = re.findall(patterns, text)
           for dates in matches_dates:
             dates_found.append(dates)
             count_dates = len(dates_found)
             text = patterns.sub(lambda match: re.sub(r'\w', '█', match.group(0)), text)
  
    addys_found = []
    count_addys = 0
    if not redactions.get('address'):
       pass
    else:
       for patterns_a in pattern_addy:
         addy_matches = re.findall(patterns_a, text)
         for addys in addy_matches:
           addys_found.append(addys)
           addys_found = [s for s in addys_found if s.find('\n') == -1]
           count_addys = len(addys_found)
           text = patterns_a.sub(lambda match: re.sub(r'\w', '█', match.group(0)), text)


    stats_file = open(args.stats,'w')
    stats_file.write(f"Statistics from redaction process for {os.path.basename(file)}:\n")
    stats_file.write(f"\n")
    stats_file.write(f"Names that got redacted were: {names} and the number of redacted names were: {count_names} \n")
    stats_file.write(f"\n")
    stats_file.write(f"Genders that got redacted were: {genders_found} and the number of genders found were: {count_genders}\n")
    stats_file.write(f"\n")
    stats_file.write(f"Numbers that got redacted were: {numbers_found} and the number of numbers found were: {count_numbers}\n")
    stats_file.write(f"\n")
    stats_file.write(f"Dates that got redacted were: {dates_found} and the number of Dates found were: {count_dates}\n")
    stats_file.write(f"\n")
    stats_file.write(f"Addresses and zipcodes that got redacted were: {addys_found} and the number of Addresses and zipcodes found were: {count_addys}\n")
    stats_file.write(f"\n")
    stats_file.close()


    output_filename = os.path.basename(file) + ".redacted"
    output_path = os.path.join(args.output, output_filename)
    with open(output_path, 'w') as f:
      f.write(text)


if __name__ == '__main__':
   main()


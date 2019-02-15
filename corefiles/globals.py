import re
import os
import nltk
from yattag import Doc
from corefiles.defect import *

try:
	nltk.data.find('tokenizers/punkt')
except:
	nltk.download('punkt')
	
try:
	nltk.data.find('taggers/averaged_perceptron_tagger')
except:
	nltk.download('averaged_perceptron_tagger')

doc, tag, text = Doc().tagtext()

# Indicators and the like
ROLE_INDICATORS = ["^As an ", "^As a ", "^As "]
MEANS_INDICATORS = ["[, ]I'm able to ", "[, ]I am able to ", "[, ]I want to ", "[, ]I wish to ", "[, ]I can ", "[, ]I want ", "[, ]I should be able to "]
ENDS_INDICATORS = ["[, ]So that ", "[, ]In order to ", "[, ]So "]
CONJUNCTIONS = [' and ', '&', '\+', ' or ', '>', '<', '/', '\\']
PUNCTUATION = ['.', ';', ':', '‒', '–', '—', '―', '‐', '-', '?', '*']
BRACKETS = [['(', ')'], ['[', ']'], ['{', '}'], ['⟨', '⟩']]
ERROR_KINDS = { 'well_formed_content': [
                  { 'subkind': 'means', 'rule': 'Analyzer.well_formed_content_rule(story.means, "means", ["means"])', 'severity':'medium', 'highlight':'str("Make sure the means includes a verb and a noun. Our analysis shows the means currently includes: ") + Analyzer.well_formed_content_highlight(story.means, "means")'},
                  { 'subkind': 'role', 'rule': 'Analyzer.well_formed_content_rule(story.role, "role", ["NP"])', 'severity':'medium', 'highlight':'str("Make sure the role includes a person noun. Our analysis shows the role currently includes: ") + Analyzer.well_formed_content_highlight(story.role, "role")'},
                ],

                'atomic': [
                  { 'subkind':'conjunctions', 'rule':"Analyzer.atomic_rule(getattr(story,chunk), chunk)", 'severity':'high', 'highlight':"Analyzer.highlight_text(story, CONJUNCTIONS, 'high')"}
                ],
                'unique': [
                  { 'subkind':'identical', 'rule':"Analyzer.identical_rule(story,allStories)", 'severity':'high', 'highlight':'str("Remove all duplicate user stories")' }
                ],
                'uniform': [
                  { 'subkind':'uniform', 'rule':"Analyzer.uniform_rule(story,allStories)", 'severity':'medium', 'highlight':'"Use the most common template: %s" % allStories.format'}
                ],

              }
CHUNK_GRAMMAR = """
      NP: {<DT|JJ|NN.*>}
      NNP: {<NNP.*>}
      AP: {<RB.*|JJ.*>}
      VP: {<VB.*><NP>*}
      MEANS: {<AP>?<VP>}
      ENDS: {<AP>?<VP>}
    """
SPECIAL_WORDS = {'import': 'VP', "export": 'VP', 'select': 'VP', 'support': 'VP'}

defects = []

def init_format(output_format):
	global oformat
	oformat = output_format

def extract_indicator_phrases(text, indicator_type):
  if text:
    indicator_phrase = []
    for indicator in eval(indicator_type.upper() + '_INDICATORS'):
      if re.compile('(%s)' % indicator.lower().replace('[, ]', '')).search(text.lower()): indicator_phrase += [indicator.replace('^', '').replace('[, ]', '')]
    return max(indicator_phrase, key=len) if indicator_phrase else None
  else:
    return text
	
def add_defect(story_id, kind, subkind, message, story_title):
	defects.append(Defect(story_id, kind, subkind, message, story_title))
	

import os
import nltk
from nltk.corpus import wordnet
from nltk.metrics import edit_distance
import re
import operator
import collections
from corefiles.stories import *
from corefiles.globals import *

class Stories:
	def __init__(self, project):
		self.project = project
		self.stories = []

	def add_story(self, story):
		self.stories.append(story)

	def has_story(self, other_story):
		if len(self.stories) == 0:
			return False
		for story in self.stories:
			if story.equals_to(other_story):
				return True
		return False

class Story:
	def __init__(self, id, title):
		self.id = id
		self.title = title
		self.role = ""
		self.means = ""
		self.ends = ""

	def chunk(self):
		StoryChunker.chunk_on_indicators(self)
		return self

	def equals_to(self, another):
		self_role = self.role[len(extract_indicator_phrases(self.role, 'role')):]
		another_role = another.role[len(extract_indicator_phrases(another.role, 'role')):]
		self_means = self.means[len(extract_indicator_phrases(self.means, 'means')):]
		another_means = another.means[len(extract_indicator_phrases(another.means, 'means')):]
		if self_role == another_role and self_means == another_means:
			return True
		return False


class StoryChunker:
  def chunk_story(story):
    if story.means is None:
      potential_means = story.title
      if story.role is not None:
        potential_means = potential_means.replace(story.role, "", 1).strip()
      if story.ends is not None:
        potential_means = potential_means.replace(story.ends, "", 1).strip()
      StoryChunker.means_tags_present(story, potential_means)
    return story.role, story.means, story.ends

  def chunk_on_indicators(story):
    from corefiles.analyzer import Analyzer
    indicators = StoryChunker.detect_indicators(story)
    if indicators['means'] is not None and indicators['ends'] is not None:
      indicators = StoryChunker.correct_erroneous_indicators(story, indicators)
    if indicators['role'] is not None and indicators['means'] is not None:
      story.role = story.title[indicators['role']:indicators['means']].strip()
      story.means = story.title[indicators['means']:indicators['ends']].strip()
    elif indicators['role'] is not None and indicators['means'] is None:
      role = StoryChunker.detect_indicator_phrase(story.title, 'role')
      text = StoryChunker.remove_special_characters(story.title)
      new_text = text.replace(role[1], '')
      sentence = Analyzer.content_chunk(new_text, 'role')
      NPs_after_role = StoryChunker.keep_if_NP(sentence)
      if NPs_after_role:
        story.role = story.title[indicators['role']:(len(role[1]) + 1 + len(NPs_after_role))].strip()
    if indicators['ends']: story.ends = story.title[indicators['ends']:None].strip()
    return story

  def detect_indicators(story):
    indicators = {'role': None, "means": None, 'ends': None}
    for indicator in indicators:
      indicator_phrase = StoryChunker.detect_indicator_phrase(story.title, indicator)
      if indicator_phrase[0]:
        indicators[indicator.lower()] = story.title.lower().index(indicator_phrase[1].lower())
    return indicators

  def detect_all_indicators(story):
    indicators = {'role': [], "means": [], 'ends': []}
    for indicator in indicators:
      for indicator_phrase in eval(indicator.upper() + '_INDICATORS'):
        if story.title:
          for indicator_match in re.compile('(%s)' % indicator_phrase.lower()).finditer(story.title.lower()):
            indicators[indicator] += [indicator_match.span()]
    return indicators

  # get longest from overlapping indicator hits
  def remove_overlapping_tuples(tuple_list):
    for hit in tuple_list:
      duplicate_tuple_list = list(tuple_list)
      duplicate_tuple_list.remove(hit)
      for duplicate in duplicate_tuple_list:
        if hit[0] <= duplicate[0] and hit[1] >= duplicate[1]:
          tuple_list.remove(duplicate)
        elif hit[0] >= duplicate[0] and hit[1] <= duplicate[1]:
          tuple_list.remove(hit)
    return tuple_list

  def remove_special_characters(text):
    return ''.join( e if (e.isalnum() or e.isspace() or e == "\'" or e == "\"" ) else ' ' for e in text).strip()

  def detect_indicator_phrase(text, indicator_type):
    result = False
    detected_indicators = ['']
    no_special_char_text = StoryChunker.remove_special_characters(text)
    for indicator_phrase in eval(indicator_type.upper() + '_INDICATORS'):
      if text:
        if re.compile('(%s)' % indicator_phrase.lower()).search(no_special_char_text.lower()):
          stripped_indicator = indicator_phrase.replace('^', '').replace('[, ]', '').strip()
          if stripped_indicator.lower() in text.lower():
            result = True
            detected_indicators.append(stripped_indicator)
    return (result, max(detected_indicators, key=len))


  def keep_if_NP(parsed_tree):
    return_string = []
    for leaf in parsed_tree:
      if type(leaf) is not tuple:
        if leaf[0][0] == 'I':
          break
        elif leaf.label() == 'NP':
          return_string.append(leaf[0][0])
        else:
          break
      elif leaf == (',', ','): return_string.append(',')
    return ' '.join(return_string)

  def means_tags_present(story, string):
    from corefiles.analyzer import Analyzer
    if not Analyzer.well_formed_content_rule(string, 'means', ['MEANS']):
      story.means = string
    return story

  def correct_erroneous_indicators(story, indicators):
    # means is larger than ends
    if indicators['means'] > indicators['ends']:
      new_means = StoryChunker.detect_indicator_phrase(story.title[:indicators['ends']], 'means')
      #replication of #427 - refactor?
      if new_means[0]:
        indicators['means'] = story.title.lower().index(new_means[1].lower())
      else:
        indicators['means'] = None
    return indicators

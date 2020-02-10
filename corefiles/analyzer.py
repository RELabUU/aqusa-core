import os
import nltk
from nltk.corpus import wordnet
from nltk.metrics import edit_distance
import re
import operator
import collections
from corefiles.globals import *
from corefiles.stories import *

class Analyzer:
  def atomic(story):
    for chunk in ['"role"', '"means"', '"ends"']:
      Analyzer.generate_defects('atomic', story, chunk=chunk)
    return story

  def unique(story,allStories):
    Analyzer.generate_defects('unique', story, allStories)
    return story

  def uniform(story,allStories):
    Analyzer.generate_defects('uniform', story, allStories)
    return story

  def generate_defects(kind, story, allStories=[], **kwargs):
    for kwarg in kwargs:
      exec(kwarg+'='+ str(kwargs[kwarg]))
    for defect_type in ERROR_KINDS[kind]:
      if eval(defect_type['rule']):
        add_defect(str(story.id), kind, defect_type['subkind'], eval(defect_type['highlight']), story.title)

  def atomic_rule(chunk, kind):
    sentences_invalid = []
    if chunk:
      for x in CONJUNCTIONS:
        if x in chunk.lower():
          if kind == 'means':
            for means in re.split(x, chunk, flags=re.IGNORECASE):
              if means:
                sentences_invalid.append(Analyzer.well_formed_content_rule(means, 'means', ['MEANS']))
          if kind == 'role':
            kontinue = True
            if x in ['&', '+']: kontinue = Analyzer.symbol_in_role_exception(chunk, x)
            if kontinue:
              for role in re.split(x, chunk, flags=re.IGNORECASE):
                if role:
                  sentences_invalid.append(Analyzer.well_formed_content_rule(role, "role", ["NP"]))
    return sentences_invalid.count(False) > 1

  def symbol_in_role_exception(chunk, conjunction):
    surrounding_words = Analyzer.get_surrounding_words(chunk, conjunction)
    exception = [False, False, False]
    exception[0] = Analyzer.space_before_or_after_conjunction(chunk, conjunction)
    exception[1] = Analyzer.surrounding_words_bigger_than(3, surrounding_words)
    exception[2] = Analyzer.surrounding_words_valid(surrounding_words)
    return exception.count(True) >= 2

  def space_before_or_after_conjunction(chunk, conjunction):
    idx = chunk.lower().index(conjunction.lower())
    space = chunk[idx-1].isspace() or chunk[idx+len(conjunction)].isspace()
    return space

  def get_surrounding_words(chunk, conjunction):
    parts = chunk.split(conjunction)
    words = []
    for index, part in enumerate(parts):
      if index % 2 == 0:
        words += [part.split()[-1]]
      else:
        words += [part.split()[0]]
    return words

  def surrounding_words_bigger_than(number, word_array):
    result = False
    for word in word_array:
      if len(word) > number: result = True
    return result

  def surrounding_words_valid(word_array):
    result = False
    for word in word_array:
      if not wordnet.synsets(word): result = True
    return result


  def identical_rule(story, allStories):
    if allStories.has_story(story):
      return True
    return False

  def highlight_text(story, word_array, severity):
    indices = []
    for word in word_array:
      if word in story.title.lower(): indices += [ [story.title.lower().index(word), word] ]
    return Analyzer.highlight_text_with_indices(story.title, indices, severity)

  def highlight_text_with_indices(text, indices, severity):
    indices.sort(reverse=True)
    for index, word in indices:
      text = text[:index] + " [*" + word + "*] " + text[index+len(word):]
    return text

  # result indicates whether the story_part contains a well_formed error
  def well_formed_content_rule(story_part, kind, tags):
    result = Analyzer.content_chunk(story_part, kind)
    well_formed = True
    for tag in tags:
      for x in result.subtrees():
        if tag.upper() in x.label(): well_formed = False
    return well_formed

  def uniform_rule(story, allStories):
    project_format = allStories.format.split(',')
    chunks = []
    for chunk in ['role', 'means', 'ends']:
      chunks += [extract_indicator_phrases(getattr(story,chunk), chunk)]
    chunks = list(filter(None, chunks))
    chunks = [c.strip() for c in chunks]
    result = False
    if len(chunks) == 1: result = True
    for x in range(0,len(chunks)):
      if edit_distance(chunks[x].lower(), project_format[x].lower()) > 3:
        result = True
    return result

  def well_formed_content_highlight(story_part, kind):
    return str(Analyzer.content_chunk(story_part, kind))

  def content_chunk(chunk, kind):
    sentence = nltk.word_tokenize(chunk)
    sentence = nltk.pos_tag(sentence)
    sentence = Analyzer.strip_indicators_pos(chunk, sentence, kind)
    sentence = Analyzer.replace_tag_of_special_words(sentence)
    cp = nltk.RegexpParser(CHUNK_GRAMMAR)
    result = cp.parse(sentence)
    return result

  def replace_tag_of_special_words(sentence):
    index = 0
    for word in sentence:
      if word[0] in SPECIAL_WORDS:
        lst = list(sentence[index])
        lst[1] = SPECIAL_WORDS[word[0]]
        sentence[index] = tuple(lst)
      index+=1
    return sentence


  def strip_indicators_pos(text, pos_text, indicator_type):
    for indicator in eval(indicator_type.upper() + '_INDICATORS'):
      if indicator.lower().strip() in text.lower():
        indicator_words = nltk.word_tokenize(indicator)
        pos_text = [x for x in pos_text if x[0] not in indicator_words]
    return pos_text

  def get_common_format(all_stories):
    most_common_format = []
    for chunk in ['role', 'means', 'ends']:
      chunks = [extract_indicator_phrases(getattr(story,chunk), chunk) for story in all_stories.stories]
      chunks = list(filter(None, chunks))
      try:
        most_common_format += [collections.Counter(chunks).most_common(1)[0][0].strip()]
      except:
        print('')
      all_stories.format = ', '.join(most_common_format)
    if all_stories.format == "": all_stories.format = "As a, I want to, So that"
    return all_stories

class MinimalAnalyzer:
  def minimal(story):
    MinimalAnalyzer.punctuation(story)
    MinimalAnalyzer.brackets(story)
    MinimalAnalyzer.indicator_repetition(story)
    return story

  def punctuation(story):
    if any(re.compile('(\%s .)' % x).search(story.title.lower()) for x in PUNCTUATION):
      highlight = MinimalAnalyzer.punctuation_highlight(story, 'high')
      add_defect(str(story.id), 'minimal', 'punctuation', highlight, story.title)
    return story

  def punctuation_highlight(story, severity):
    highlighted_text = story.title
    indices = []
    for word in PUNCTUATION:
      if re.search('(\%s .)' % word, story.title.lower()): indices += [ [story.title.index(word), word] ]
    first_punct = min(indices)
    highlighted_text = highlighted_text[:first_punct[0]] + " [*" + highlighted_text[first_punct[0]:] + "*] "
    return highlighted_text

  def brackets(story):
    if any(re.compile('(\%s' % x[0] + '.*\%s(\W|\Z))' % x[1]).search(story.title.lower()) for x in BRACKETS):
      highlight = MinimalAnalyzer.brackets_highlight(story, 'high')
      add_defect(str(story.id), 'minimal', 'brackets', highlight, story.title)
    return story

  def brackets_highlight(story, severity):
    highlighted_text = story.title
    matches = []
    for x in BRACKETS:
      split_string = '[^\%s' % x[1] + ']+\%s' % x[1]
      strings = re.findall(split_string, story.title)
      match_string = '(\%s' % x[0] + '.*\%s(\W|\Z))' % x[1]
      string_length = 0
      for string in strings:
        result = re.compile(match_string).search(string.lower())
        if result:
          span = tuple(map(operator.add, result.span(), (string_length, string_length)))
          matches += [ [span, result.group()] ]
        string_length += len(string)
    matches.sort(reverse=True)
    for index, word in matches:
      highlighted_text = highlighted_text[:index[0]] + " [*" + word + "*] " + highlighted_text[index[1]:]
    return highlighted_text

  def indicator_repetition(story):
    from corefiles.stories import StoryChunker
    indicators = StoryChunker.detect_all_indicators(story)
    for indicator in indicators: indicators[indicator] = StoryChunker.remove_overlapping_tuples(indicators[indicator])
    indicators = MinimalAnalyzer.remove_indicator_repetition_exceptions(indicators, story)
    for indicator in indicators:
      if len(indicators[indicator]) >= 2:
        highlight = MinimalAnalyzer.indicator_repetition_highlight(story.title, indicators[indicator], 'high')
        add_defect(str(story.id), 'minimal', 'indicator_repetition', highlight, story.title)
    return story

  def indicator_repetition_highlight(text, ranges, severity):
    indices = []
    for rang in ranges:
      indices += [[rang[0], text[ rang[0]:rang[1] ] ]]
    return Analyzer.highlight_text_with_indices(text, indices, severity)

  def remove_indicator_repetition_exceptions(indicators, story):
    # exception #1: means indicator after ends indicator
    for means_indicator in indicators['means']:
      for ends_indicator in indicators['ends']:
        if ends_indicator[1] >= means_indicator[0] and ends_indicator[1] <= means_indicator[1]:
          indicators['means'].remove(means_indicator)
    return indicators

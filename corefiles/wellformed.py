from corefiles.globals import *

class WellFormedAnalyzer:
  def well_formed(story):
    WellFormedAnalyzer.means(story)
    WellFormedAnalyzer.role(story)
    # return story

  def means(story):
    if not story.means:
      add_defect(str(story.id), 'well_formed', 'no_means', 'Add what you want to achieve', story.title)
    return story

  def role(story):
    if not story.role:
      add_defect(str(story.id), 'well_formed', 'no_role', 'Add for who this story is', story.title)
    return story
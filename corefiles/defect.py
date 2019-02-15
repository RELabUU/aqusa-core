import html

class Defect:
	def __init__(self, story_id, kind, subkind, message, story_title):
		self.story_id = story_id
		self.kind = kind
		self.subkind = subkind
		self.message = message
		self.story_title = story_title
		
	def print_txt(self):
		return 'Story #' + self.story_id + ': "' + self.story_title + '"\n' + '   Defect type: ' + self.kind + '.' + self.subkind + '\n' + '   Message: ' + self.message + '\n'
		
	def print_html(self, doc, tag, text):
		with tag('tr'):
			with tag('td'):
				text(self.story_id)
			with tag('td'):
				text(self.story_title)
			with tag('td'):
				text(self.kind)
			with tag('td'):
				text(self.subkind)
			with tag('td'):
				doc.asis(self.message.replace("[*","<mark>").replace("*]", "</mark>"))
			
	
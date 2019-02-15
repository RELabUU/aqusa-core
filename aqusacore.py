import os, sys, getopt

from corefiles.wellformed import *
from corefiles.analyzer import *
from corefiles.globals import *
from corefiles.stories import *
from argparse import ArgumentParser

def main(argv):
	inputfile = ''
	outputfile = ''
	outputformat = 'txt'
	
	print ('======================================================\n' +
		'                     AQUSA-Core\n' +
		'    Requirements Engineering Lab, Utrecht University\n' +
		'           Fabiano Dalpiaz, Garm Lucassen\n' +
		'======================================================\n')
	try:
		opts, args = getopt.getopt(argv,"i:o:f:",["ifile=","ofile=","oformat="])
	except getopt.GetoptError:
		print ('  The right way to invoke the program is: \n  python aqusacore.py -i <inputfile>  [-o <outputfile>] [-f <outputformat>] ,\n  with <outputformat> being txt or html')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print ('  The right way to invoke the program is: \n  python aqusacore.py -i <inputfile>  [-o <outputfile>] [-f <outputformat>] ,\n  with <outputformat> being txt or html')
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = arg
			print ('Input file: input/' + inputfile)
		elif opt in ("-f", "--oformat"):
			outputformat = arg
			print ('Output format: ' + outputformat)
		elif opt in ("-o", "--ofile"):
			outputfile = arg
			print ('Outputfile file: output/' + outputfile)

	if inputfile == '':
		print (' You need to specify a valid input file')
		sys.exit()
	
	if os.path.exists('input/' + inputfile):
		with open('input/' + inputfile) as f:
			raw = f.readlines()
	else: 
		print ('The input file "input/' + inputfile + '" does not exist')
		sys.exit(2)
		
	allStories = Stories(inputfile)
	init_format(outputformat)


		
	i = 0
	for r in raw: 
	   i = i + 1
	   if r.strip() == "":
	      continue
	   story = Story(id = i, title = r.strip())
	   story = story.chunk()
	   WellFormedAnalyzer.well_formed(story)
	   Analyzer.atomic(story)
	   MinimalAnalyzer.minimal(story)
	   Analyzer.unique(story,allStories)
	   allStories.add_story(story)
	   
	allStories = Analyzer.get_common_format(allStories)

	for story in allStories.stories:
		Analyzer.uniform(story,allStories)
	
	output_text = ""
	
	if outputformat == 'html':
		with tag('html'):
			with tag('head'):
				with tag('script', src='sorttable.js', type='text/javascript'):
					pass
				with tag('link', rel='stylesheet', href='styles.css'):
					pass
			with tag('body'):
				with tag('table', klass='sortable'):
					with tag('thead'):
						with tag('tr'):
							with tag('th'):
								text('ID')
							with tag('th'):
								text('User Story')
							with tag('th'):
								text('Defect kind')
							with tag('th'):
								text('Subkind')
							with tag('th'):
								text('Message')
					with tag('tbody'):
						for defect in defects:
							defect.print_html(doc, tag, text)
		output_text = doc.getvalue()
	else:
		for defect in defects:
			output_text = output_text + defect.print_txt()

	if outputfile == '':
		print (output_text)
	else:
		f = open("output/" + outputfile + "." + outputformat, "w")
		f.write(output_text) 
	
if __name__ == "__main__":
   main(sys.argv[1:])

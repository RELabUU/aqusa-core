# aqusa-core
A command line version of the AQUSA tool, which identifies quality defects in user story requirements. AQUSA-core takes as input a text file that includes a collection of user stories (one user story per line), it executes linguistic processing to identify defects, and it returns a report either in text format (txt) or as an HTML page.

### Installation
  * Tested with Python 3.7
  * Install libraries using `pip install -r requirements.txt`
  
### Usage
`python aqusacore.py -i <inputfile>  [-o <outputfile>] [-f <outputformat>]`
  where
  * -i <inputfile> indicates the input txt file stored in the ./input folder
  * -o <outputfile> indicates the output file, which will be stored in the ./output folder
  * -f <outputformat> can be either txt or html, and indicates the type of output that is desired
 
 If you wish to share the html page that is created by the tool, you also need to copy the styles.css and the sorttable.js files.

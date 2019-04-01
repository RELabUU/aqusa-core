# aqusa-core
A command line version of the AQUSA tool<sup>1</sup>, which identifies quality defects in user story requirements. AQUSA-core takes as input a text file that includes a collection of user stories (one user story per line), it executes linguistic processing to identify defects, and it returns a report either in text format (txt) or as an HTML page. This tool is a command-line version of the tool described in a 2016 paper published in the Requirements Engineering journal<sup>2</sup>.

### Installation
  * Tested with Python 3.7
  * Install libraries using `pip install -r requirements.txt`
  
### Usage
`python aqusacore.py -i <inputfile>  [-o <outputfile>] [-f <outputformat>]`
  where
  * -i <inputfile> indicates the input txt file stored in the ./input folder
  * -o <outputfile> indicates the output file, which will be stored in the ./output folder
  * -f <outputformat> can be either txt or html, and indicates the type of output that is desired
 
AQUSA-core comes with a few example files that can be found in the ./input folder
 
If you wish to share the html page that is created by the tool, you also need to copy the styles.css and the sorttable.js files.

### References and links
<sup>1</sup> https://github.com/gglucass/AQUSA

<sup>2</sup> Garm Lucassen, Fabiano Dalpiaz, Jan Martijn E. M. van der Werf, Sjaak Brinkkemper. Improving Agile Requirements: the Quality User Story Framework and Tool, In Requirements Engineering, volume 21, 2016.

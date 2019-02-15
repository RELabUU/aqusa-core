# aqusa-core
A command line version of the AQUSA tool, which identifies quality defects in user story requirements.

### Installation
  * Tested with Python 3.7
  * Install libraries using `pip install -r requirements.txt`
  
### Usage
`python aqusacore.py -i <inputfile>  [-o <outputfile>] [-f <outputformat>]`
  where
  * -i <inputfile> indicates the input txt file stored in the ./input folder
  * -o <outputfile> indicates the output file, which will be stored in the ./output folder
  * -f <outputformat> can be either txt or html, and indicates the type of output that is desired

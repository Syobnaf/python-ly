"""
This file is merely a utility to be used with command:
python3 -m ly2xml </path/to/input.ly> </path/to/output.musicxml>
"""
import os, sys  # Help from https://stackoverflow.com/questions/9427037/relative-path-not-working-even-with-init-py
sys.path.insert(0, os.path.abspath(".."))
import ly.musicxml

def ly2xml(inFile, outFile):
    """Function to read in a lilypond input and write to a musicxml output"""
    # Read
    e = ly.musicxml.writer()
    f = open(inFile, 'r', encoding='utf-8')
    e.parse_text(f.read(), inFile)
    f.close()
    # Write
    xml = e.musicxml()
    xml.write(outFile)

if len(sys.argv) != 3:
    print("Command must be in form ly2xml </path/to/input.ly> </path/to/output.musicxml>")
else:
    ly2xml(sys.argv[1], sys.argv[2])

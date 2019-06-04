"""
This file is merely a utility to be used with command:
python3 -m ly2xml </path/to/input.ly> </path/to/output.musicxml>
"""
import os, sys
sys.path.insert(0, os.path.abspath(".."))  # from https://stackoverflow.com/questions/9427037/relative-path-not-working-even-with-init-py
import ly.musicxml
if len(sys.argv) != 3:
    print("Command must be in form ly2xml </path/to/input.ly> </path/to/output.musicxml>")
else:
    ipath = sys.argv[1]
    opath = sys.argv[2]
    # read
    e = ly.musicxml.writer()
    f = open(ipath, 'r', encoding='utf-8')
    e.parse_text(f.read(), ipath)
    f.close()
    # write
    xml = e.musicxml()
    xml.write(opath)

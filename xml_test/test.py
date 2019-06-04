"""
Tests for XML output.
Taken from /python-ly/tests/test_xml.py as a model
"""
import sys, os, io
sys.path.insert(0, os.path.abspath(".."))  # from https://stackoverflow.com/questions/9427037/relative-path-not-working-even-with-init-py
import datetime
import difflib
import ly.musicxml
from lxml import etree

def test_all():
    """Test all input files against output files in /test_media"""
    for i in range(1, 10):
        input("Press enter to test file {}".format(i))
        compare_output(str(i))

def ly_to_xml(filename):
    """Read Lilypond file and return XML string."""
    writer = ly.musicxml.writer()
    with open(filename, 'r', encoding='utf-8') as lyfile:
        writer.parse_text(lyfile.read())
    xml = writer.musicxml()
    return ly.musicxml.create_musicxml.xml_decl_txt.format(encoding='UTF-8') + "\n" + ly.musicxml.create_musicxml.doctype_txt + "\n" + xml.tostring(encoding='unicode')

def read_expected_xml(filename):
    """Return string with expected XML from file."""
    with open(filename, 'r') as xmlfile:
        output = xmlfile.read()
    # Replace date in XML file with today's date
    output = output.replace("2019-06-04", str(datetime.date.today()))
    return output

def compare_output(filename):
    """Compare XML output with expected output."""
    filebase = os.path.join(os.path.dirname(__file__), 'test_media',
                            filename)

    output = ly_to_xml(filebase + '.ly')
    expected_output = read_expected_xml(filebase + '.musicxml')

    assert_multi_line_equal(expected_output, output, filename)


def assert_multi_line_equal(first, second, filename, msg=None):
    """Assert that two multi-line strings are equal.

    If they aren't, show a nice diff.
    """
    assert isinstance(first, str), 'First argument is not a string'
    assert isinstance(second, str), 'Second argument is not a string'

    if first == second:
        print("Test succeeded for file {}".format(filename))
    else:
        message = ''.join(difflib.ndiff(first.splitlines(True),
            second.splitlines(True)))
        if msg:
            message += " : " + msg

        print(message)  # print diff
        print("Test failed for file {}, diff is above".format(filename))

    # assert first==second, "Multi-line strings are unequal:\n" + message  # prints diff

test_all()

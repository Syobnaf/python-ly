"""
Tests for XML output.
/python-ly/tests/test_xml.py taken as a model
Use with command: python3 -m test
"""
import sys, os, io  # Help from https://stackoverflow.com/questions/9427037/relative-path-not-working-even-with-init-py
sys.path.insert(0, os.path.abspath(".."))
import datetime
import difflib
import ly.musicxml
from lxml import etree

def test_all():
    """Test all input files against output files in /test_media"""
    failed_tests = 0
    for i in range(1, 10):  # Performs 9 tests
        input("Press enter to test file {}\n".format(i))
        if not compare_output(str(i)):
            failed_tests += 1
    assert failed_tests == 0, "{} test(s) failed\n".format(failed_tests)
    print("All tests passed\n")  # Prints if no tests failed

def test():
    """Test only the designated test file against its expected output in /test_media"""
    assert compare_output("test"), "MusicXML output does not match expected output"

def ly_to_xml(filename):
    """Read Lilypond file and return XML string."""
    writer = ly.musicxml.writer()
    with open(filename, 'r', encoding='utf-8') as lyfile:
        writer.parse_text(lyfile.read())
    xml = writer.musicxml()
    return (ly.musicxml.create_musicxml.xml_decl_txt.format(encoding='UTF-8') + "\n"
        + ly.musicxml.create_musicxml.doctype_txt + "\n"
        + xml.tostring(encoding='unicode'))

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

    return are_multi_line_equal(expected_output, output, filename)


def are_multi_line_equal(first, second, filename, msg=None):
    """
    Returns whether or not two multi-line strings are equal.
    If they are, indicate that the test succeeded for filename
    If they aren't, indicate that the test failed for filename
        and show a nice diff.
    """
    assert isinstance(first, str), 'First argument is not a string\n'
    assert isinstance(second, str), 'Second argument is not a string\n'

    if first == second:
        print("Test succeeded for file {}\n".format(filename))
        return True
    else:
        message = ''.join(difflib.ndiff(first.splitlines(True),
            second.splitlines(True)))
        if msg:
            message += " : " + msg

        print(message)  # Print diff
        print("Test failed for file {}, diff is above\n".format(filename))
        return False

# test_all()
test()

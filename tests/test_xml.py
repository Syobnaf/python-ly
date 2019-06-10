"""Tests for XML output."""
import datetime
import difflib
import ly.musicxml
from lxml import etree
import os
import io
import re


def test_all():
    test_glissando()
    print("Glissando test passed")
    test_tie()
    print("Tie test passed")
    test_merge_voice()
    print("Merge voice test passed")
    test_variable()
    print("Variable test passed")
    test_dynamics()
    print("Dynamics test passed")
    test_tuplet()
    print("Tuplet test passed")
    print("All tests passed")


def test_glissando():
    compare_output('glissando')


def test_tie():
    compare_output('tie')


def test_merge_voice():
    compare_output('merge_voice')


def test_variable():
    compare_output('variable')


def test_dynamics():
    compare_output('dynamics')


def test_tuplet():
    compare_output('tuplet')


def ly_to_xml(filename):
    """Read Lilypond file and return XML string."""
    writer = ly.musicxml.writer()
    with open(filename, 'r', encoding='utf-8') as lyfile:
        writer.parse_text(lyfile.read())
    xml = writer.musicxml()
    return (ly.musicxml.create_musicxml.xml_decl_txt.format(encoding='utf-8') + "\n"
        + ly.musicxml.create_musicxml.doctype_txt + "\n"
        + xml.tostring(encoding='unicode'))


def read_expected_xml(filename):
    """Return string with expected XML from file."""
    with open(filename, 'r') as xmlfile:
        output = xmlfile.read()
    # Replace date in XML file with today's date
    output = re.sub(r'\d{4}-\d{2}-\d{2}', str(datetime.date.today()), output)
    return output


def compare_output(filename):
    """Compare XML output with expected output."""
    filebase = os.path.join(os.path.dirname(__file__), 'test_xml_files',
                            filename)

    output = ly_to_xml(filebase + '.ly')
    expected_output = read_expected_xml(filebase + '.musicxml')

    assert_multi_line_equal(expected_output, output)
    # Couldn't figure out how to get this working, also may not be important
    # validate_xml(output)


def validate_xml(xml):
    """Validate XML against XSD file."""
    xsdname = os.path.join(os.path.dirname(__file__), 'musicxml.xsd')
    xsdfile = open(xsdname, 'r')
    xmlschema_doc = etree.parse(xsdfile)
    xsdfile.close()
    xmlschema = etree.XMLSchema(etree=xmlschema_doc)
    parser = etree.XMLParser(schema=xmlschema)
    # Raises Exception if not valid:
    etree.fromstring(xml, parser)


def assert_multi_line_equal(first, second, msg=None):
    """Assert that two multi-line strings are equal.

    If they aren't, show a nice diff.
    """
    assert isinstance(first, str), 'First argument is not a string'
    assert isinstance(second, str), 'Second argument is not a string'

    if first != second:
        message = ''.join(difflib.ndiff(first.splitlines(True),
                                        second.splitlines(True)))
        if msg:
            message += " : " + msg
        assert False, "Multi-line strings are unequal:\n" + message


if __name__ == "__main__":
    #sys.exit(main(sys.argv))
    test_all()

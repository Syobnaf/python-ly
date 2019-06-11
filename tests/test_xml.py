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
    print("\nGlissando test passed\n")
    test_tie()
    print("\nTie test passed\n")
    test_merge_voice()
    print("\nMerge voice test passed\n")
    test_variable()
    print("\nVariable test passed\n")
    test_dynamics()
    print("\nDynamics test passed\n")
    test_tuplet()
    print("\nTuplet test passed\n")
    test_pickup()
    print("\nPickup test passed\n")
    test_lyrics()
    print("\nLyrics test passed\n")
    test_barlines()
    print("\nBarlines test passed\n")
    print("\nAll tests passed\n")


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


def test_pickup():
    compare_output('pickup')


def test_lyrics():
    compare_output('lyrics')


def test_barlines():
    compare_output('barlines')


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
    validate_xml(output)


def validate_xml(xml):
    """Validate XML against XSD file."""
    # see https://www.w3.org/2011/prov/track/issues/480
    # and https://stackoverflow.com/questions/49534700/how-to-use-xlink-data-types-in-xsd
    # and https://stackoverflow.com/questions/15830421/xml-unicode-strings-with-encoding-declaration-are-not-supported
    xml = xml.encode('utf-8')
    xsdname = os.path.join(os.path.dirname(__file__), 'musicxml.xsd')
    xmlschema = etree.XMLSchema(file=xsdname)
    parser = etree.XMLParser(schema=xmlschema, encoding='utf-8')
    # Raises Exception if not valid:
    etree.fromstring(xml, parser=parser)


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

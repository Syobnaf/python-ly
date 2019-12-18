# This file is part of python-ly, https://pypi.python.org/pypi/python-ly
#
# Copyright (c) 2008 - 2015 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
The information of the parsed source is organised into an object
structure with help of the classes in ly.musicxml.xml_objs.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

from fractions import Fraction

import sys
import ly.duration
import ly.pitch

from . import xml_objs


def eprint(*args, **kwargs):
    """
    From https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
    Prints to stderr
    """
    print(*args, file=sys.stderr, **kwargs)


class Mediator():
    """Help class that acts as mediator between the ly source parser
    and the XML creating modules."""

    def __init__(self):
        """ create global lists """
        # the current number of flats/sharps in key (ex: -3 indicates 3 flats in the key)
        self.num_accidentals_in_key = 0
        # keeps track of the most recent number of flats/sharps applied to all notes (ex: 'B':-2 is double flat B)
        self.current_accidentals_dict = {'C': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0, 'A': 0, 'B': 0}
        self.score = xml_objs.Score()
        self.sections = []
        self.permanent_sections = []
        """ default and initial values """
        self.insert_into = None
        self.current_attr = None
        self.current_note = None
        self.prev_note = None
        self.current_lynote = None
        self.current_is_rest = False
        self.action_onnext = []
        self.divisions = 1
        self.dur_token = "4"
        self.dur_tokens = ()
        self.dots = 0
        self.tie_list = []
        self.tie_line = 'solid'
        self.voice = 1
        self.voice_sep_sections = 0
        self.voice_name = None
        self.staff = 0
        self.part = None
        self.group = None
        self.group_num = 0
        self.current_chord = []
        self.q_chord = []
        self.prev_pitch = None
        self.prev_chord_pitch = None
        self.prev_bar = None
        self.store_voicenr = 0
        self.staff_id_dict = {}
        self.store_unset_staff = False
        self.staff_unset_notes = {}
        self.lyric_sections = {}
        self.lyric = None
        self.lyric_syll = False
        self.lyric_nr = 1
        self.ongoing_wedge = False
        self.ongoing_dashes = False
        self.octdiff = 0
        self.prev_tremolo = 8
        self.tupl_dur = 0
        self.tupl_sum = 0
        self.ly_to_xml_oct = 3  # xml octave values are 3 higher than lilypond
        self.current_chord_or_note = []

    def new_header_assignment(self, name, value):
        """Distributing header information."""
        creators = ['composer', 'arranger', 'poet', 'lyricist']
        if name == 'title':
            self.score.title = value
        elif name == 'subtitle':
            self.score.subtitle = value
        elif name == 'copyright':
            self.score.rights = value
        elif name in creators:
            self.score.creators[name] = value
        else:
            self.score.info[name] = value

    def new_section(self, name, glob=False):
        name = self.check_name(name)
        section = xml_objs.ScoreSection(name, glob)
        self.insert_into = section
        self.sections.append(section)
        self.permanent_sections.append(section)
        self.bar = None

    def new_snippet(self, name):
        name = self.check_name(name)
        snippet = xml_objs.Snippet(name, self.insert_into)
        self.insert_into = snippet
        self.sections.append(snippet)
        self.permanent_sections.append(snippet)
        self.bar = None

    def new_lyric_section(self, name, voice_id):
        name = self.check_name(name)
        lyrics = xml_objs.LyricsSection(name, voice_id)
        self.insert_into = lyrics
        self.lyric_sections[name] = lyrics

    def check_name(self, name, nr=1):
        n = self.get_var_byname(name)
        if n:
            name = name+str(nr)
            name = self.check_name(name, nr+1)
        return name

    def get_var_byname(self, name):
        for n in self.permanent_sections:
            if n.name == name:
                return n

    def new_group(self):
        parent = self.group
        self.group_num += 1
        self.group = xml_objs.ScorePartGroup(self.group_num, "bracket")
        if parent:  # nested group
            self.group.parent = parent
            parent.partlist.append(self.group)
        else:
            self.score.partlist.append(self.group)

    def close_group(self):
        if self.group.parent:
            self.group = self.group.parent
        else:
            self.group = None

    def change_group_bracket(self, system_start):
        self.group.set_bracket(get_group_symbol(system_start))

    def new_part(self, pid=None, to_part=None, piano=False):
        if piano:
            self.part = xml_objs.ScorePart(2, pid, to_part)
        else:
            self.part = xml_objs.ScorePart(part_id=pid, to_part=to_part)
        if not to_part:
            if self.group:
                self.group.partlist.append(self.part)
            else:
                self.score.partlist.append(self.part)
        self.insert_into = self.part
        self.bar = None

    def part_not_empty(self):
        return self.part and self.part.barlist

    def get_part_by_id(self, pid, partholder=None):
        if not partholder:
            partholder = self.score
        ret = False
        for part in partholder.partlist:
            if isinstance(part, xml_objs.ScorePartGroup):
                ret = self.get_part_by_id(pid, part)
            else:
                if part.part_id == pid:
                    ret = part
        return ret

    def set_voicenr(self, command=None, add=False, nr=0, piano=0):
        if add:
            self.voice += 1
        elif nr:
            self.voice = nr
        else:
            self.voice = get_voice(command)
            if piano > 2:
                self.voice += piano+1

    def set_staffnr(self, staffnr, staff_id=None):
        self.store_unset_staff = False
        if staffnr:
            self.staff = staffnr
        elif staff_id in self.staff_id_dict:
            self.staff = self.staff_id_dict[staff_id]
        elif staff_id:
            self.store_unset_staff = True
            self.staff = staff_id

    def add_staff_id(self, staff_id):
        self.store_unset_staff = False
        if staff_id:
            if staff_id in self.staff_id_dict:
                self.staff = self.staff_id_dict[staff_id]
            else:
                self.staff_id_dict[staff_id] = self.staff
            if staff_id in self.staff_unset_notes:
                for n in self.staff_unset_notes[staff_id]:
                    n.staff = self.staff

    def add_snippet(self, snippet_name):
        """ Adds snippet to previous barlist.
        A snippet can be shorter than a full bar,
        so this can also mean continuing a previous bar."""
        def continue_barlist(insert_into):
            self.insert_into = insert_into
            if insert_into.barlist:
                self.prev_bar = self.bar
                self.bar = insert_into.barlist[-1]
            else:
                self.new_bar(False)

        snippet = self.get_var_byname(snippet_name)
        continue_barlist(snippet.merge_barlist)
        for bb in snippet.barlist:
            for b in bb.obj_list:
                self.bar.add(b)
            if bb.list_full:
                self.new_bar()

    def check_voices(self):
        """ Checks active sections. The two latest created are merged.
        Also checks for empty sections. """
        if self.sections[-1].glob:
            self.score.merge_globally(self.sections[-1])
            self.score.glob_section.merge_voice(self.section[-1])
        if len(self.sections) > 2:
            if not self.sections[-2].barlist:
                self.sections.pop(-2)
                self.check_voices()
            elif not self.sections[-1].barlist:
                self.sections.pop()
                self.check_voices()
            else:
                self.sections[-2].merge_voice(self.sections[-1])
                self.sections.pop()

    def check_voices_by_nr(self):
        """ Used for snippets. Merges all active snippets
        created after the stored voice number."""
        sect_len = len(self.sections)
        if sect_len > 2:
            if self.voice > 1:
                voices_skipped = (self.voice - self.store_voicenr) - (self.voice_sep_sections - 1)
                for n in range(self.store_voicenr, self.voice - voices_skipped):
                    self.check_voices()
                if isinstance(self.sections[-1], xml_objs.Snippet):
                    self.add_snippet(self.sections[-1].name)
                    self.sections.pop()
                else:
                    eprint("WARNING: problem adding snippet!")

    def check_lyrics(self, voice_id):
        """Check the finished lyrics section and merge it into
        the referenced voice."""
        if self.lyric is not None and self.lyric[1] == 'middle':
            self.lyric[1] = 'end'
        lyrics_section = self.lyric_sections['lyricsto'+voice_id]
        voice_section = self.sections[-1]
        if voice_section:
            voice_section.merge_lyrics(lyrics_section)
        else:
            eprint("Warning can't merge in lyrics!", voice_section)
        self.lyric = None  # Clear final lyric

    def check_part(self):
        """Adds the latest active section to the part."""
        if len(self.sections) > 1:
            if self.score.is_empty():
                self.new_part()
            if self.sections[-1].glob:
                self.part.merge_voice(self.sections[-1])
            else:
                self.part.barlist.extend(self.sections[-1].barlist)
                self.sections.pop()
        if self.part and self.part.to_part:
            self.part.merge_part_to_part()
        self.part.merge_voice(self.score.glob_section)
        name = self.check_name("glob")
        self.score.glob_section = self.part.extract_global_to_section(name)
        self.part = None

    def check_simultan(self):
        """Check done after simultanoues (<< >>) section."""
        if self.part:
            self.part.merge_voice(self.sections[-1])
        elif len(self.sections) > 1:
            self.sections[-2].merge_voice(self.sections[-1])
        if len(self.sections) > 0:
            self.sections.pop()

    def check_score(self):
        """
        Check score

        If no part were created, place first variable (fallback) as part.

        Apply the latest global section.
        """
        if self.score.is_empty():
            self.new_part()
            self.part.barlist.extend(self.get_first_var())
        self.score.merge_globally(self.score.glob_section, False)

    def reset_current_accidentals_dict(self, fifths):
        """Resets self.current_accidentals_dict to only include the accidentals in the current key"""
        ORDER_OF_FIFTHS = ('B', 'E', 'A', 'D', 'G', 'C', 'F')
        # Reset all notes to natural, and remove any notes with octaves
        self.current_accidentals_dict = {'C': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0, 'A': 0, 'B': 0}
        if fifths < 0:  # flat key
            for f in ORDER_OF_FIFTHS[:abs(fifths)]:
                self.current_accidentals_dict[f] = -1
        elif fifths > 0:  # sharp key
            for s in ORDER_OF_FIFTHS[-fifths:]:
                self.current_accidentals_dict[s] = 1

    def is_acc_needed(self, name, octave, alter):
        """
        Check if a given note needs an accidental
        given the current state of accidentals

        name is the name of the note ('A', 'B', 'C', 'D', 'E', 'F', 'G')
        alter is a number representing the flat/sharp status of the note (-1 is flat, +1 is sharp, 0 is natural)
        """
        abs_note = name + str(octave)
        if self.check_for_tie_end(name, octave, alter) is not None:  # subsequent tied notes never need accidentals
            return False
        if abs_note in self.current_accidentals_dict:
            # Same note in same octave had same alter
            if self.current_accidentals_dict[abs_note] == alter:
                return False
            # Same note in same octave had different alter
            else:
                self.current_accidentals_dict[abs_note] = alter
                return True
        # No previous same notes in same octave, but key matches alter
        elif self.current_accidentals_dict[name] == alter:
            self.current_accidentals_dict[abs_note] = alter
            return False
        # No previous same notes in same octave, and key has different alter
        else:
            self.current_accidentals_dict[abs_note] = alter
            return True
        eprint("Warning: Invalid note checked for accidental!")
        return False

    def get_first_var(self):
        if self.sections:
            return self.sections[0].barlist

    def new_bar(self, fill_prev=True):
        self.reset_current_accidentals_dict(self.num_accidentals_in_key)
        if self.bar and fill_prev:
            self.bar.list_full = True
        self.current_attr = xml_objs.BarAttr()
        self.prev_bar = self.bar
        self.bar = xml_objs.Bar()
        self.bar.obj_list = [self.current_attr]
        self.insert_into.barlist.append(self.bar)

    def add_to_bar(self, obj):
        if self.bar is None:
            self.new_bar()
        self.bar.add(obj)

    def change_end_type(self, bar, from_type, to_type):
        """ Changes ending in bar of from_type to to_type. """
        obj = bar.obj_list[0]
        if isinstance(obj, xml_objs.BarAttr):
            for end in obj.endings:
                if end.etype == from_type:
                    end.etype = to_type
                    return

    def update_ending(self, bl, bar):
        """ Updates whether an ending has a downward jog based on what type of barline is added (bl). """
        if bl in ['|.', '.|']:  # 'light-heavy' or 'heavy-light'
            # Add downward jog to ending
            self.change_end_type(bar, 'discontinue', 'stop')
        else:
            # Remove downward jog from ending
            self.change_end_type(bar, 'stop', 'discontinue')

    def create_barline(self, bl):
        self.update_ending(bl, self.bar)
        barline = xml_objs.BarAttr()
        barline.set_barline(bl)
        self.bar.add(barline)
        self.new_bar()

    def new_repeat(self, rep, prev=False):
        """ Create a repeat sign (forward or backward). """
        # Start a new bar when None or forward repeat in middle of measure
        if self.bar is None or (rep == 'forward' and self.bar.has_music()):
            self.new_bar()
        # Determine whether the repeat should be in this measure or the previous
        bar = None
        if prev or (rep == 'backward' and not self.bar.has_music()):
            bar = self.prev_bar
        else:
            bar = self.bar
        # Determine whether a new attribute is needed
        attr = None
        if rep == 'backward':
            if isinstance(bar.obj_list[-1], xml_objs.BarAttr):
                attr = bar.obj_list[-1]
            else:
                attr = xml_objs.BarAttr()
                bar.add(attr)
        else:
            attr = bar.obj_list[0]
        # Set the barline (or left barline for forward repeats), but do not overwrite existing special barlines
        existing_barline = False
        if rep == 'forward':
            if self.prev_bar is not None:
                for obj in self.prev_bar.obj_list:
                    if isinstance(obj, xml_objs.BarAttr):
                        # Backward repeats with 'light-heavy' barlines don't count as special barlines
                        if obj.repeat == 'backward':
                            if obj.barline != 'light-heavy':
                                existing_barline = True
                                break
                        elif obj.barline is not None:
                            existing_barline = True
                            break
            if not existing_barline:
                attr.set_left_barline(rep)
        else:
            for obj in bar.obj_list:
                if isinstance(obj, xml_objs.BarAttr):
                    if obj.barline is not None:
                        existing_barline = True
                        break
            if not existing_barline:
                attr.set_barline(rep)
        # Create the repeat
        attr.repeat = rep
        # Start a new bar if necessary
        if not prev and rep == 'backward' and self.bar.has_music():
            self.new_bar()

    def new_ending(self, start, end, etype, staff_nr):
        """ Create an alternate ending to a repeat. """
        if self.bar is None:
            self.new_bar()
        # Choose the appropriate bar, create necessary repeats between endings,
        #     and create empty barlines at the start and end of the alternate endings (if they occur in the middle of a measure)
        bar = None
        if not self.bar.has_music():
            if etype == 'start':
                bar = self.bar
            else:
                bar = self.prev_bar
                if etype == 'stop':
                    self.new_repeat('backward', prev=True)
        else:
            if etype == 'start':
                self.create_barline('')
                bar = self.bar
            elif etype == 'discontinue':
                bar = self.bar
                self.create_barline('')
            elif etype == 'stop':
                bar = self.bar
                self.new_repeat('backward')
        # If the final ending in a set of alternate endings ends on a 'light-heavy' barline, give it a "downward jog"
        if etype == 'discontinue':
            for obj in bar.obj_list:
                if isinstance(obj, xml_objs.BarAttr):
                    if obj.barline in ['light-heavy', 'heavy-light']:
                        etype = 'stop'
                        break
        elif etype == 'stop':
            for obj in bar.obj_list:
                if isinstance(obj, xml_objs.BarAttr):
                    if obj.barline is not None and obj.barline not in ['light-heavy', 'heavy-light']:
                        etype = 'discontinue'
                        break
        # Mark the ending only if this is the first staff
        if staff_nr == 1:
            attr = bar.obj_list[0]
            attr.add_ending(start, end, etype)

    def new_key(self, key_name, mode):
        self.num_accidentals_in_key = get_fifths(key_name, mode)
        self.reset_current_accidentals_dict(self.num_accidentals_in_key)
        if self.bar is None:
            self.new_bar()
        if self.bar.has_music():
            new_bar_attr = xml_objs.BarAttr()
            new_bar_attr.set_key(get_fifths(key_name, mode), mode)
            self.add_to_bar(new_bar_attr)
        else:
            self.current_attr.set_key(get_fifths(key_name, mode), mode)

    def new_time(self, num, den, numeric=False):
        if self.bar is None:
            self.new_bar()
        self.current_attr.set_time([num, den], numeric)

    def new_clef(self, clefname):
        self.clef = clefname2clef(clefname)
        if self.bar is None:
            self.new_bar()
        if self.bar.has_music():
            new_bar_attr = xml_objs.BarAttr()
            new_bar_attr.set_clef(self.clef)
            self.add_to_bar(new_bar_attr)
        else:
            if self.staff:
                self.current_attr.multiclef.append((self.clef, self.staff))
            else:
                self.current_attr.set_clef(self.clef)

    def set_sys_break(self):
        if self.bar is None:
            self.new_bar()
        if self.bar.has_music():
            self.new_bar()
            new_bar_attr = xml_objs.BarAttr()
            new_bar_attr.sys_break = True
            self.add_to_bar(new_bar_attr)
        else:
            self.current_attr.sys_break = True

    def set_relative(self, note):
        self.prev_pitch = note.pitch

    def new_note(self, note, rel=False, is_unpitched=False):
        self.current_is_rest = False
        self.clear_chord()
        if is_unpitched:
            self.prev_note = self.current_note
            self.current_note = self.create_unpitched(note)
            self.check_current_note(is_unpitched=True)
        else:
            self.prev_note = self.current_note
            self.current_note = self.create_barnote_from_note(note, rel)
            self.current_lynote = note
            self.check_current_note(rel)
        self.current_chord_or_note = [self.current_note]
        self.do_action_onnext(self.current_note)
        self.action_onnext = []

    def new_iso_dura(self, note, rel=False, is_unpitched=False):
        """
        Isolated durations in music sequences.

        An isolated duration in LilyPond is rendered as a normal note but the
        pitch information is missing and has to be filled in by some other
        means, usually by the previous pitch. (RhythmicStaff is an exception
        since it ignores specified pitches anyway).

        """
        if self.current_chord:
            self.copy_prev_chord(note.duration)
        else:
            if not is_unpitched:
                note.pitch = self.current_lynote.pitch
            self.new_note(note, rel, is_unpitched)

    def create_unpitched(self, unpitched):
        """Create a xml_objs.Unpitched from ly.music.items.Unpitched."""
        dura = unpitched.duration
        return xml_objs.Unpitched(dura, voice=self.voice, voice_name=self.voice_name)

    def create_barnote_from_note(self, note, relative):
        """Create a xml_objs.BarNote from ly.music.items.Note."""
        p_copy = note.pitch.copy()
        if relative:
            p_copy.makeAbsolute(self.prev_pitch)
        octave = p_copy.octave + self.ly_to_xml_oct
        p = getNoteName(note.pitch.note)
        alt = get_xml_alter(note.pitch.alter)
        try:
            acc = note.accidental_token  # special accidentals (?, !)
        except AttributeError:
            acc = None
        if acc is None and self.is_acc_needed(p, octave, alt):  # check if a normal accidental should be printed
            acc = 'normal'
        dura = note.duration
        return xml_objs.BarNote(p, alt, acc, dura, self.voice, self.voice_name)

    def copy_barnote_basics(self, bar_note):
        """Create a copy of a xml_objs.BarNote."""
        octave = bar_note.octave
        p = bar_note.base_note
        alt = bar_note.alter
        try:
            if bar_note.accidental_token != 'normal':
                acc = bar_note.accidental_token  # special accidentals (?, !)
            else:
                acc = None
        except AttributeError:
            acc = None
        if acc is None and self.is_acc_needed(p, octave, alt):  # check if a normal accidental should be printed
            acc = 'normal'
        dura = bar_note.duration
        voc = bar_note.voice
        voc_name = bar_note.voice_name
        copy = xml_objs.BarNote(p, alt, acc, dura, voc, voc_name)
        copy.octave = bar_note.octave
        copy.chord = bar_note.chord
        return copy

    def new_duration_token(self, token, tokens):
        self.dur_token = token
        self.dur_tokens = tokens
        self.check_duration(self.current_is_rest)

    def check_current_note(self, rel=False, rest=False, is_unpitched=False):
        """ Perform checks common for all new notes and rests. """
        if not rest and not is_unpitched:
            self.set_octave(rel)
        if not rest:
            note = self.current_note
            tie_idx = self.check_for_tie_end(note.base_note, note.octave, note.alter)
            if tie_idx is not None:
                self.tie_list.pop(tie_idx)
                note.set_tie('stop', self.tie_line)
        self.check_duration(rest)
        self.check_divs()
        if self.staff:
            self.current_note.set_staff(self.staff)
            if self.store_unset_staff:
                if self.staff in self.staff_unset_notes:
                    self.staff_unset_notes[self.staff].append(self.current_note)
                else:
                    self.staff_unset_notes[self.staff] = [self.current_note]
        self.add_to_bar(self.current_note)

    def check_chord_note_for_staff(self, chord_note):
        if self.staff:
            chord_note.set_staff(self.staff)

    def set_octave(self, relative):
        """Set octave by getting the octave of an absolute note + self.ly_to_xml_oct (3)."""
        p = self.current_lynote.pitch.copy()
        if relative:
            p.makeAbsolute(self.prev_pitch)
        self.prev_pitch = p
        self.current_note.set_octave(p.octave + self.ly_to_xml_oct)

    def do_action_onnext(self, note):
        """Perform the stored action on the next note."""
        for action in self.action_onnext:
            func_call = getattr(self, action[0])
            func_call(note, *action[1])

    def check_duration(self, rest):
        """Check the duration for the current note."""
        dots, rs = self.duration_from_tokens(self.dur_tokens)
        if rest and rs:  # special case of multibar rest
            if not self.current_note.show_type or self.current_note.skip:
                bs = self.current_note.duration
                if rs == bs[1]:
                    self.current_note.duration = (bs[0], 1)
                    self.current_note.dot = 0
                    self.scale_rest(rs)
                    return
        self.current_note.dot = dots
        self.dots = dots
        self.current_note.set_durtype(durval2type(self.dur_token))
        if self.current_chord:
            for c in self.current_chord:
                c.set_durtype(durval2type(self.dur_token))

    def new_chord(self, note, duration=None, rel=False, chord_base=True):
        if chord_base:
            self.new_chordbase(note, duration, rel)
            self.current_chord.append(self.current_note)
        else:
            self.current_chord.append(self.new_chordnote(note, rel))
        self.do_action_onnext(self.current_chord[-1])

    def new_chordbase(self, note, duration, rel=False):
        self.prev_note = self.current_note
        self.current_note = self.create_barnote_from_note(note, rel)
        self.current_note.set_duration(duration)
        self.current_lynote = note
        self.current_chord_or_note = [self.current_note]
        self.check_current_note(rel)

    def new_chordnote(self, note, rel):
        chord_note = self.create_barnote_from_note(note, rel)
        chord_note.set_duration(self.current_note.duration)
        chord_note.set_durtype(durval2type(self.dur_token))
        chord_note.dots = self.dots
        chord_note.tuplet = self.current_note.tuplet
        if not self.prev_chord_pitch:
            self.prev_chord_pitch = self.prev_pitch
        p = note.pitch.copy()
        if(rel):
            p.makeAbsolute(self.prev_chord_pitch)
        chord_note.set_octave(p.octave + self.ly_to_xml_oct)
        self.prev_chord_pitch = p
        chord_note.chord = True
        self.current_chord_or_note.append(chord_note)
        self.bar.add(chord_note)
        self.check_chord_note_for_staff(chord_note)
        tie_idx = self.check_for_tie_end(chord_note.base_note, chord_note.octave, chord_note.alter)
        if tie_idx is not None:
            self.tie_list.pop(tie_idx)
            chord_note.set_tie('stop', self.tie_line)
        return chord_note

    def copy_prev_chord(self, duration):
        self.current_chord_or_note = []
        if self.current_chord:
            prev_chord = self.current_chord
            self.clear_chord()
        else:
            prev_chord = self.q_chord
        for i, pc in enumerate(prev_chord):
            cn = self.copy_barnote_basics(pc)
            cn.set_staff(pc.staff)
            pc_dot = 0
            if duration == pc.duration:  # Carry over dots from prev chord if this copy has same duration
                pc_dot = pc.dot
            cn.set_duration(duration, dot=pc_dot)
            cn.set_durtype(durval2type(self.dur_token))
            if i == 0:
                self.prev_note = self.current_note
                self.current_note = cn
            self.current_chord.append(cn)
            self.current_chord_or_note.append(cn)
            tie_idx = self.check_for_tie_end(cn.base_note, cn.octave, cn.alter)
            if tie_idx is not None:
                self.tie_list.pop(tie_idx)
                cn.set_tie('stop', self.tie_line)
            self.bar.add(cn)
            if i == 0:  # On base note of chord, update divisions
                self.check_duration(False)
                self.check_divs()
        self.current_chord_or_note.append('end')

    def clear_chord(self):
        self.q_chord = self.current_chord
        self.current_chord = []
        self.prev_chord_pitch = None

    def chord_end(self):
        """Actions when chord is parsed."""
        self.current_chord_or_note.append('end')
        self.action_onnext = []

    def new_rest(self, rest):
        self.current_is_rest = True
        self.clear_chord()
        rtype = rest.token
        dur = rest.duration
        if rtype == 'r':
            self.prev_note = self.current_note
            self.current_note = xml_objs.BarRest(dur, self.voice, self.voice_name)
        elif rtype == 'R':
            self.prev_note = self.current_note
            self.current_note = xml_objs.BarRest(dur, self.voice, self.voice_name, show_type=False)
        elif rtype == 's' or rtype == '\\skip' or rtype == '_':
            self.prev_note = self.current_note
            self.current_note = xml_objs.BarRest(dur, self.voice, self.voice_name, skip=True)
        self.check_current_note(rest=True)

    def note2rest(self):
        """Note used as rest position transformed to rest."""
        dur = self.current_note.duration
        voc = self.current_note.voice
        voc_name = self.current_note.voice_name
        pos = [self.current_note.base_note, self.current_note.octave]
        self.prev_note = self.current_note
        self.current_note = xml_objs.BarRest(dur, voice=voc, voice_name=voc_name, pos=pos)
        self.check_duration(rest=True)
        self.bar.obj_list.pop()
        self.bar.add(self.current_note)

    def scale_rest(self, multp):
        """ create multiple whole bar rests """
        dur = self.current_note.duration
        voc = self.current_note.voice
        voc_name = self.current_note.voice_name
        st = self.current_note.show_type
        sk = self.current_note.skip
        for i in range(1, int(multp)):
            self.new_bar()
            rest_copy = xml_objs.BarRest(dur, voice=voc, voice_name=voc_name, show_type=st, skip=sk)
            self.add_to_bar(rest_copy)

    def change_to_tuplet(self, tfraction, ttype, nr, length=None):
        """Change the current note into a tuplet note."""
        tuplscaling = Fraction(tfraction[0], tfraction[1])
        if self.tupl_dur:
            if self.tupl_sum == 0:
                ttype = "start"
            base, scaling = self.current_lynote.duration
            self.tupl_sum += (1 / tuplscaling) * base * scaling
            if self.tupl_sum == self.tupl_dur:
                ttype = "stop"
                self.tupl_sum = 0
        if length:
            acttype = normtype = durval2type(self.calc_tupl_den(tfraction, length))
            self.current_note.set_tuplet(tfraction, ttype, nr, acttype, normtype)
        else:
            self.current_note.set_tuplet(tfraction, ttype, nr)

    def change_tuplet_type(self, index, newtype):
        self.current_note.tuplet[index].ttype = newtype

    def set_tuplspan_dur(self, token=None, tokens=None, fraction=None):
        """
        Catch duration set by the tupletSpannerDuration property.

        Set the fraction directly or calculate it from tokens.
        """
        if fraction:
            self.tupl_dur = fraction
        else:
            base, scaling = ly.duration.base_scaling((token,) + tokens)
            self.tupl_dur = base * scaling

    def unset_tuplspan_dur(self):
        """Reset tuplet duration sum and tuplet spanner duration."""
        self.tupl_sum = 0
        self.tupl_dur = 0

    def calc_tupl_den(self, tfraction, length):
        """Calculate the tuplet denominator from
        fraction and duration of tuplet."""
        return tfraction[1] / length

    def tie_to_next(self, line):
        """ Begin a tie on an entire chord or an individual note. """
        tie_type = 'start'
        self.tie_line = line
        if self.current_chord_or_note:
            if self.current_chord_or_note[-1] == 'end':
                # Apply tie to entire chord if it comes after
                for note in self.current_chord_or_note:
                    if note != 'end':
                        note.set_tie(tie_type, line)
                        self.tie_list.append(note)
            else:
                # Apply tie to only most recent note
                note = self.current_chord_or_note[-1]
                note.set_tie(tie_type, line)
                self.tie_list.append(note)
        else:
            eprint("Warning: No proper note/chord found for tie!")
            note = self.current_note
            note.set_tie(tie_type, line)
            self.tie_list.append(note)

    def check_for_tie_end(self, name, octave, alter):
        """ If there is an unfinished tie which matches note, then return its list index else return None. """
        if self.tie_list:
            count = 0
            for tie in self.tie_list:
                if tie.base_note == name and tie.octave == octave and tie.alter == alter:
                    return count
                count += 1
        return None

    def set_slur(self, nr, slur_type, phrasing=False, line='solid', grace=False):
        """
        Set the slur start or stop for the current note. """
        self.current_note.set_slur(nr, slur_type, phrasing, line, grace)

    def new_articulation(self, art_token):
        """
        An articulation, fingering, string number, or other symbol.

        Grouped as articulations, ornaments, technical and others.
        """
        if isinstance(art_token, ly.lex.lilypond.Fingering):
            self.current_note.add_fingering(art_token)
        else:
            ret = artic_token2xml_name(art_token)
            if ret == 'ornament':
                self.current_note.add_ornament(art_token[1:])
            elif ret == 'other':
                self.current_note.add_other_notation(art_token[1:])
            elif ret:
                self.current_note.add_articulation(ret)

    def new_dynamics(self, dynamics):
        hairpins = {'<': 'crescendo', '>': 'diminuendo'}
        text_dyn = {'cresc': 'cresc.', 'decresc': 'descresc.',
                    'dim': 'dim.'}
        if dynamics == '!':
            if self.ongoing_wedge:
                self.current_note.set_dynamics_wedge('stop')
                self.ongoing_wedge = False
            if self.ongoing_dashes:
                self.current_note.set_dynamics_dashes('stop')
                self.ongoing_dashes = False
        elif dynamics in hairpins:
            self.current_note.set_dynamics_wedge(hairpins[dynamics])
            self.ongoing_wedge = True
        elif dynamics in text_dyn:
            self.current_note.set_dynamics_text(text_dyn[dynamics])
            self.current_note.set_dynamics_dashes('start', before=False)
            self.ongoing_dashes = True
        elif self.ongoing_wedge:
            self.current_note.set_dynamics_wedge('stop')
            self.current_note.set_dynamics_mark(dynamics)
            self.ongoing_wedge = False
        elif self.ongoing_dashes:
            self.current_note.set_dynamics_dashes('stop')
            self.current_note.set_dynamics_mark(dynamics)
            self.ongoing_dashes = False
        else:
            self.current_note.set_dynamics_mark(dynamics)

    def new_grace(self, slash=0):
        self.current_note.set_grace(slash)

    def new_chord_grace(self, slash=0):
        self.current_chord[-1].set_grace(slash)

    def new_gliss(self, line=None):
        if line:
            line = get_line_style(line)
        if self.current_chord:
            for n, c in enumerate(self.current_chord):
                c.set_gliss(line, nr=n+1)
        else:
            self.current_note.set_gliss(line)
        self.action_onnext.append(("end_gliss", (line, )))

    def end_gliss(self, note, line):
        if self.current_chord:
            n = len(self.current_chord)
        else:
            n = 1
        note.set_gliss(line, endtype="stop", nr=n)

    def set_breathe(self):
        self.current_note.add_articulation('breath-mark')

    def set_tremolo(self, trem_type='single', duration=0, repeats=0, note_count=1):
        if self.current_note.tremolo[1]:  # tremolo already set
            self.current_note.set_tremolo(trem_type)
        else:
            if repeats:
                duration = int(self.dur_token)
                bs, durtype, dot_num = calc_trem_dur(repeats, self.current_note.duration, duration, note_count)
                self.current_note.duration = bs
                self.current_note.type = durtype
                self.current_note.dot = dot_num
            elif not duration:
                duration = self.prev_tremolo
            else:
                self.prev_tremolo = duration
            self.current_note.set_tremolo(trem_type, duration)

    def new_trill_spanner(self, end=None):
        if not end:
            self.current_note.add_ornament('trill')
            end = "start"
        self.current_note.add_adv_ornament('wavy-line', end)

    def new_ottava(self, octdiff):
        octdiff = int(octdiff)
        if self.octdiff == octdiff:
            return
        if self.octdiff:
            if self.octdiff < 0:
                plac = "below"
            else:
                plac = "above"
            size = abs(self.octdiff) * 7 + 1
            self.current_note.set_oct_shift(plac, "stop", size)
        if octdiff:
            if octdiff < 0:
                plac = "below"
                octdir = "up"
            else:
                plac = "above"
                octdir = "down"
            size = abs(octdiff) * 7 + 1
            self.action_onnext.append(("set_ottava", (plac, octdir, size)))
        self.octdiff = octdiff

    def set_ottava(self, note, plac, octdir, size):
        note.set_oct_shift(plac, octdir, size)

    def new_tempo(self, unit, dur_tokens, tempo, string):
        dots, rs = self.duration_from_tokens(dur_tokens)
        if tempo:
            beats = tempo[0]
        else:
            beats = 0
        try:
            text = string.value()
        except AttributeError:
            text = None
        tempo = xml_objs.BarAttr()
        unittype = durval2type(unit) if unit else ''
        tempo.set_tempo(unit, unittype, beats, dots, text)
        self.add_to_bar(tempo)

    def set_by_property(self, prprty, value, group=False):
        """Generic setter for different properties."""
        if prprty == 'instrumentName':
            if group:
                self.set_groupname(value)
            else:
                self.set_partname(value)
        elif prprty == 'shortInstrumentName':
            if group:
                self.set_groupabbr(value)
            else:
                self.set_partabbr(value)
        elif prprty == 'midiInstrument':
            self.set_partmidi(value)
        elif prprty == 'stanza':
            self.new_lyric_nr(value)
        elif prprty == 'systemStartDelimiter':
            self.change_group_bracket(value)

    def set_partname(self, name):
        if self.score.is_empty():
            self.new_part()
        self.part.name = name

    def set_partabbr(self, abbr):
        if self.score.is_empty():
            self.new_part()
        self.part.abbr = abbr

    def set_groupname(self, name):
        if self.group:
            self.group.name = name

    def set_groupabbr(self, abbr):
        if self.group:
            self.group.abbr = abbr

    def set_partmidi(self, midi):
        if self.score.is_empty():
            self.new_part()
        self.part.midi = midi

    def new_lyric_nr(self, num):
        self.lyric_nr = num

    def new_lyrics_text(self, txt):
        if not txt:
            txt = "ERROR"
            eprint("Warning: Lyric text not readable, marked with ERROR!")
        if self.lyric:
            if self.lyric_syll:
                if self.lyric[1] in ['begin', 'middle']:
                    self.lyric = [txt, 'middle', self.lyric_nr]
            else:
                if self.lyric[1] in ['begin', 'middle']:
                    self.lyric[1] = 'end'
                self.lyric = [txt, 'single', self.lyric_nr]
        else:
            self.lyric = [txt, 'single', self.lyric_nr]
        self.insert_into.barlist.append(self.lyric)
        self.lyric_syll = False

    def new_lyrics_item(self, item):
        if item == '--':
            if self.lyric:
                if self.lyric[1] == 'single':
                    self.lyric[1] = 'begin'
                self.lyric_syll = True
        elif item == '__':
            self.lyric.append("extend")
        elif item == '\\skip' or item == '_':
            self.insert_into.barlist.append("skip")
        elif isinstance(item, list) and item[-1] == "command":
            self.insert_into.barlist.append(item)  # Item should be of form ["commandName", args, "command"]
        else:
            eprint("Warning: Lyric item", str(item), "not implemented!")

    def duration_from_tokens(self, tokens):
        """Calculate dots and multibar rests from tokens."""
        dots = 0
        rs = 0
        for t in tokens:
            if t == '.':
                dots += 1
            elif '*' in t and '/' not in t:
                rs = int(t[1:])
        return (dots, rs)

    def check_divs(self):
        """ The new duration is checked against current divisions """
        base = self.current_note.duration[0]
        scaling = self.current_note.duration[1]
        divs = self.divisions
        tupl = self.current_note.tuplet
        a = 4
        if base:
            b = 1/base
        else:
            b = 1
            eprint("Warning problem checking duration!")
        c = a * divs * scaling
        predur, mod = divmod(c, b)
        if mod > 0:
            mult = get_mult(a, b)
            self.divisions = divs*mult


##
# Translation functions
##

def getNoteName(index):
    noteNames = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    return noteNames[index]


def get_xml_alter(alter):
    """ Convert alter to the specified format,
    i e int if it's int and float otherwise.
    Also multiply with 2."""
    alter *= 2
    if float(alter).is_integer():
        return alter
    else:
        return float(alter)


def durval2type(durval):
    """Convert LilyPond duration to MusicXML duration type."""
    xml_types = [
        "maxima", "long", "breve", "whole",
        "half", "quarter", "eighth",
        "16th", "32nd", "64th",
        "128th", "256th", "512th", "1024th", "2048th"
    ]  # Note: 2048 is supported by ly but not by MusicXML!
    try:
        type_index = ly.duration.durations.index(str(durval))
    except ValueError:
        type_index = 5
    return xml_types[type_index]


def get_fifths(key, mode):
    """Returns current number of sharps/flats in the key (negative = flats, positive = sharps)"""
    fifths = 0
    sharpkeys = ['c', 'g', 'd', 'a', 'e', 'b', 'fis', 'cis', 'gis',
                 'dis', 'ais', 'eis', 'bis', 'fisis', 'cisis']
    flatkeys = ['c', 'f', 'bes', 'es', 'as', 'des', 'ges', 'ces', 'fes',
                'beses', 'eses', 'ases']
    if key in sharpkeys:
        fifths = sharpkeys.index(key)
    elif key in flatkeys:
        fifths = -flatkeys.index(key)
    if mode == 'minor':
        return fifths-3
    elif mode == 'dorian':
        return fifths-2
    elif mode == 'major':
        return fifths


def clefname2clef(clefname):
    """
    To add a clef look up the clef name in LilyPond
    and the corresponding definition in musicXML.
    Add it to the python dictionary below.
    """
    clef_dict = {
        "treble": ('G', 2, 0),
        "violin": ('G', 2, 0),
        "G": ('G', 2, 0),
        "bass": ('F', 4, 0),
        "F": ('F', 4, 0),
        "alto": ('C', 3, 0),
        "C": ('C', 3, 0),
        "tenor": ('C', 4, 0),
        "treble_8": ('G', 2, -1),
        "treble_15": ('G', 2, -2),
        "bass_8": ('F', 4, -1),
        "bass_15": ('F', 4, -2),
        "treble^8": ('G', 2, 1),
        "treble^15": ('G', 2, 2),
        "bass^8": ('F', 4, 1),
        "bass^15": ('F', 4, 2),
        "percussion": ('percussion', 0, 0),
        "tab": ('TAB', 5, 0),
        "soprano": ('C', 1, 0),
        "mezzosoprano": ('C', 2, 0),
        "baritone": ('C', 5, 0),
        "varbaritone": ('F', 3, 0),
        "baritonevarF": ('F', 3, 0),
        "french": ('G', 1, 0),
        "subbass": ('F', 5, 0),
        # From here on the clefs will end up with wrong symbols
        "GG": ('G', 2, -1),
        "tenorG": ('G', 2, -1),
        "varC": ('C', 3, 0),
        "altovarC": ('C', 3, 0),
        "tenorvarC": ('C', 4, 0),
        "baritonevarC": ('C', 5, 0),

    }
    try:
        clef = clef_dict[clefname]
    except KeyError:
        clef = 0
    return clef


def get_mult(num, den):
    simple = Fraction(num, den)
    return simple.denominator


def get_voice(c):
    voices = ["voiceOne", "voiceTwo", "voiceThree", "voiceFour"]
    return voices.index(c)+1


def artic_token2xml_name(art_token):
    """
    From Articulations in ly.music.items.
    Grouped as articulations, ornaments and others.

    To add an articulation look up the name or abbreviation
    in LilyPond and the corresponding node name in musicXML.
    Add it to the python dictionary below.
    """
    artic_dict = {
        ".": "staccato", "-": "tenuto", ">": "accent",
        "_": "detached-legato", "!": "staccatissimo",
        "\\staccatissimo": "staccatissimo"
    }
    ornaments = ['\\trill', '\\prall', '\\mordent', '\\turn']
    others = ['\\fermata']
    try:
        return artic_dict[art_token]
    except KeyError:
        if art_token in ornaments:
            return "ornament"
        elif art_token in others:
            return "other"
        else:
            return False


def length_to_duration(length):
    """
    Convert a note length fraction (such as 3/4) into a lilypond duration (str) and a number of dots
        lilypond duration could be: '\\maxima' (8), '\\longa' (4), '\\breve' (2), or '1', '2', '4', ..., '2048' for fractions (1/#)

    Ex: length of 3/4 -> ('2', 1) because 3/4 is a dotted half note
        length of 7/2 -> ('\\breve', 2) because 7/2 is a double dotted breve
    """
    durations = [
        8, 4, 2, 1, Fraction(1, 2), Fraction(1, 4), Fraction(1, 8), Fraction(1, 16), Fraction(1, 32),
        Fraction(1, 64), Fraction(1, 128), Fraction(1, 256), Fraction(1, 512), Fraction(1, 1024), Fraction(1, 2048)
    ]  # Note: 2048 is supported by ly but not by MusicXML!
    index = durations.index(Fraction(1, 2048))
    dots = dur = add = 0
    # Calculate the index of the first duration shorter than length
    for i in range(len(durations)):
        if length >= durations[i]:
            if length < 16:  # Prevents infinite recursion
                dur = durations[i]
                dot_length = dur * Fraction(1, 2)
                # Calculate number of needed dots
                while(length > dur):  # Limit of dur is durations[i] * 2
                    dots += 1
                    dur += dot_length
                    dot_length *= Fraction(1, 2)
            else:
                eprint("Warning: Length of note is too long!")
            index = i
            break
    if index == durations.index(Fraction(1, 2048)):
        eprint("Warning: Length of note is too short for MusicXML!")
    return ly.duration.durations[index], dots


def calc_trem_dur(repeats, base_scaling, duration, note_count):
    """
    Calculate tremolo duration, note type, and number of dots from:
        number of repeats, initial duration, and number of notes in the tremolo.
    """
    base = base_scaling[0]
    scale = base_scaling[1]
    duration, dots = length_to_duration(base * scale * repeats * note_count)
    new_base = base * repeats
    new_type = durval2type(duration)
    return (new_base, scale), new_type, dots


def get_line_style(style):
    style_dict = {
        "dashed-line": "dashed",
        "dotted-line": "dotted",
        "trill": "wavy",
        "zigzag": "wavy"
    }
    try:
        return style_dict[style]
    except KeyError:
        return False


def get_group_symbol(lily_sys_start):
    symbol_dict = {
        "SystemStartBrace": "brace",
        "SystemStartSquare": "square"
        }
    try:
        return symbol_dict[lily_sys_start]
    except KeyError:
        return False

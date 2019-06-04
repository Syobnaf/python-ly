%
% Generated by flexscore.php on 2014-11-11 04:39:32
%
% Score configuration:
% <?xml version="1.0"?>
% <Accompaniment>
%   <staff1>t-dcc</staff1>
%   <staff2>c-ccc</staff2>
%   <staff3>ta-scc-acc</staff3>
%   <!-- combine when lilypond partcombine/lyric bug fixed -->
%   <staff4>ba-tcc-bcc</staff4>
%   <staff5>p</staff5>
%   <requires>Alto,Tenor,Bass|Keyboard</requires>
%   <showSubtitle>false</showSubtitle>
%   <useKeyboard>true</useKeyboard>
%   <useHarmonyChords>true</useHarmonyChords>
%   <stanzas>all</stanzas>
%   <showPartNames>false</showPartNames>
%   <showVocalMarkup>false</showVocalMarkup>
%   <lilypond>true</lilypond>
%   <staffSize>25</staffSize>
%   <lyricSize>1</lyricSize>
%   <paperSize>letter</paperSize>
%   <orientation>portrait</orientation>
%   <showMeasureNumbers>true</showMeasureNumbers>
%   <showHymnNumber>true</showHymnNumber>
%   <separateDescant>false</separateDescant>
%   <separateStanzas>false</separateStanzas>
%   <iPad>true</iPad>
%   <includeNotes>true</includeNotes>
%   <autoResizeTitle>true</autoResizeTitle>
%   <maxInlineStanzas>5</maxInlineStanzas>
%   <overflowLyricSize>0</overflowLyricSize>
%   <staff1Name>descant</staff1Name>
%   <staff2Name>chords</staff2Name>
%   <staff3Name>treble</staff3Name>
%   <staff4Name>bass</staff4Name>
%   <staff5Name>percussion</staff5Name>
%   <staff6Name>keyboard</staff6Name>
%   <hymnalID>BH2008</hymnalID>
%   <number>673</number>
%   <textHymnalID>BH2008</textHymnalID>
%   <textNumber>673</textNumber>
%   <tuneHymnalID>BH2008</tuneHymnalID>
%   <tuneNumber>673</tuneNumber>
%   <instrument>Accompaniment</instrument>
%   <hymnType>normal_flexscore</hymnType>
%   <hymnID/>
%   <hash>4a6304</hash>
%   <hasSoprano>true</hasSoprano>
%   <hasAlto>true</hasAlto>
%   <hasTenor>true</hasTenor>
%   <hasBass>true</hasBass>
%   <hasSopranoResponse>true</hasSopranoResponse>
%   <hasAltoResponse>true</hasAltoResponse>
%   <hasTenorResponse>true</hasTenorResponse>
%   <hasBassResponse>true</hasBassResponse>
%   <useStanzas>StanzaOne</useStanzas>
%   <inlineStanzas>1</inlineStanzas>
%   <hasResponseLyrics>true</hasResponseLyrics>
%   <keySignature>cmaj</keySignature>
%   <stanzaSpecificResponseLyrics>false</stanzaSpecificResponseLyrics>
% </Accompaniment>
% 
\include "definitions.ly"


%%%%%   text   %%%%%

\header{
   title = \markup { \fontsize #-1.02 "The Lord Bless You and Keep You" }
}

StanzaOne = \lyricmode {
  The Lord bless you and keep you;
  The Lord lift His coun -- te -- nance up -- on you,
  And give you peace,
  and give you peace;
  The Lord _ make His face to shine up -- on you,
  And be gra -- cious un -- to you,
  be gra -- cious, The Lord be gra -- cious,
  gra -- cious un -- to you.
}

SopranoResponse = \lyricmode {
  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
  A -- men, A -- men, A -- _ men,
  A -- men, A -- men.
}

AltoResponse = \lyricmode {
  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
  A -- men, A -- men, A -- men, A -- _ men,
  A -- _ men, A -- men.
}

TenorResponse = \lyricmode {
  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
  _ _ _ _ _ _ _ _
  The Lord _ make His face to shine up -- on you,
  \skip 1 _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
  A -- men, A -- men, A -- men, A -- men,
  A -- men, A -- men, A -- men.
}

BassResponse = \lyricmode {
  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
  on you, and give you peace,
  and give you peace;
  _ _ _ _ _ _ _ _ _ _ _ _
  And be gra -- cious,
  and be gra -- cious,
  _ _ _ _ _ _ _ _ _ _
  A -- men, A -- men, A -- men, A -- men,
  A -- _ men, A -- men, A -- men.
}



%%%%%   tune   %%%%%

\language "english"

hasChords     = ##f
hasDescant    = ##f

\header{
   fsTuneCredit = \markup { \wordwrap { MUSIC (BENEDICTION, Irregular Meter): Peter Christian Lutkin } }
}

keyTime = {
    \time 4/4
    \numericTimeSignature
    \key c \major
    \partial 4
}

Soprano = \relative g' {
  \voiceOne
  \keyTime
  \hideSlur
    g4
  | g2 e4 c8 c
  | d4( f) e4. g8
  | g4 e8[ g] c8.[ b16] a8[ e]
  | g4( fs) g2
  | \override Staff.Rest #'staff-position = #0 r8 e f[ e] a4 r
  | r8 g a[ g] c \revert Staff.Rest #'staff-position r r g
  | g[ e] g[ c] e8.[ c16] g8[ e]
  | g4( f) e e8 a
  | a2~ a8[ g] e[ g]
  | c4. c8 c4 a
  | \override Staff.Rest #'staff-position = #0 r4 r8 a g4. c,8
  | a' g r4 g f
  | e2 d
  | c4 \bar "||" r r2 \revert Staff.Rest #'staff-position
  | R1
  | r4 b'( e d)
  | c e( g f
  | e d c b)
  | a2. b8 a
  | g2. a8( g
  | f4 d) g( a)
  | g1
  | g1 \bar "|."
}

Alto = \relative c' {
  \voiceTwo
  \keyTime
  \hideSlur
    c4
  | c2 c4 c8 c
  | c4( b) c4. e8
  | e4 c8[ e] e8.[ e16] e8[ e]
  | d2 d
  | \override Staff.Rest #'staff-position = #0 r8 cs cs[ cs] d4 r
  | s8 d d[ d] c[ g'] g[ f]
  | e[ c] e4 e8.[ e16] e8[ c]
  | e4( d) c \revert Staff.Rest #'staff-position r
  | r c8[ d] e[ e] r4
  | r f8 g a4 f
  | \override Staff.Rest #'staff-position = #0 r r8 c c4. c8
  | c c r4 cs d
  | c2 b
  | c4 \bar "||" r r2 \revert Staff.Rest #'staff-position
  | s4 c( f e)
  | d2 e(~
  | e4 fs) g2
  | g4( gs) a( e~
  | e4) f8 e d2~
  | d4 e8 d cs2
  | d4( b c2~
  | c4 d8 c b2)
  | c1 \bar "|."
}

Tenor = \relative e {
  \voiceOne
  \keyTime
  \hideSlur
    e4
  | e2 g4 e8 e
  | a4( g) g4. c8
  | c4 g8[ g] a8.[ gs16] a8[ a]
  | b4( a) b r
  | r8 a a[ a] a4 r
  | r8 b c[ b] c[ g] a[ b]
  | c4 c c8.[ c16] c8 c
  | c4( b) c \override Staff.Rest #'staff-position = #0 r
  | r a8[ b] c[ c] r4
  | r c8 bf a4 c
  | r r8 c bf4. bf8
  | bf bf r4 a a
  | g2. f4
  | e4 \revert Staff.Rest #'staff-position \bar "||" g( c b)
  | a4 a( d c)
  | b2 g4( a8 b)
  | c2 b4( c8 d)
  | e2.( b4)
  | c4( d8 c b2~
  | b4 c8 b) a2
  | a4( af g gf)
  | f2 f
  | e1 \bar "|."
}

Bass = \relative c {
  \voiceTwo
  \keyTime
  \hideSlur
    c4
  | c2 c4 c8 c
  | f,4( g) c4. c8
  | c4 c8[ c] a8.[ b16] c8[ c]
  | d2 g8[ g] g[ g]
  | g2( f8)[ f] f[ f]
  | f2( e8) e d4
  | c8[ c'] g[ e] c8.[ g'16] g8 g
  | g4( gs) a \override Staff.Rest #'staff-position = #0 r
  | r f8[ f] e[ e] r4
  | r d8 e f4 f
  | r r8 f e4. e8
  | f e r4 e d
  | g,2 g
  | c4 \revert Staff.Rest #'staff-position \bar "||" r c( d8 e)
  | f2 d4( e8 f)
  | g2 e4( f8 g)
  | a2 g4( a8 b
  | c4 b a g)
  | f2. g8 f
  | e2. f8( e
  | d4 f e ef)
  | d2 g,
  | c1 \bar "|."
}



%%%%%   Accompaniment template   %%%%%

#(set-global-staff-size 25)
#(set-default-paper-size "letter" 'portrait)
\header {
  subtitle = ""
}

\layout {
	\context { \Lyrics
		\override LyricText #'font-size = #1
	}
}

\score
{
  <<
		\new Staff = "treble" \with {
	}
    <<
		\clef "treble"
		\new Voice = "SopranoVoice" \removeWithTag #'vocalMarkup \Soprano
		\new Voice = "AltoVoice" \removeWithTag #'vocalMarkup \Alto
		\lyricsto SopranoVoice \new Lyrics \StanzaOne
		\new Lyrics \with { alignAboveContext = "treble" }  { \lyricsto SopranoVoice \SopranoResponse  }
		\new Lyrics \with { alignBelowContext = "treble" }  { \lyricsto AltoVoice \AltoResponse  }
	>>

		\new Staff = "bass" \with {
	}
    <<
		\clef "bass"
		\new Voice = "TenorVoice" \removeWithTag #'vocalMarkup \Tenor
		\new Voice = "BassVoice" \removeWithTag #'vocalMarkup \Bass
		\new Lyrics \with { alignAboveContext = "bass" }  { \lyricsto TenorVoice \TenorResponse  }
		\new Lyrics \with { alignBelowContext = "bass" }  { \lyricsto BassVoice \BassResponse  }
	>>

  >>
}

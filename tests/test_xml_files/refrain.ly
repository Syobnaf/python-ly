\version "2.18.2"

StanzaOne = \lyricmode {
  \set stanza = "1."
  %refrain  Start  
  La di la di
  %endrefrain 
  la di la di
  %refrainname=End
  la di la di
}

StanzaTwo = \lyricmode {
  \set stanza = "2."
  Da li da li
  da li da li
  %refrain:End
}

\language "english"

keyTime = {
    \time 4/4
    \numericTimeSignature
    \key c \major
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    b4 b b b
    b b b b 
    b b b b
}

\score
{
  <<
		\new Staff = "treble" \with {
	}
    <<
		\clef "treble"
		\new Voice = "SopranoVoice" \Soprano
		\lyricsto SopranoVoice \new Lyrics \StanzaOne
		\lyricsto SopranoVoice \new Lyrics \StanzaTwo
	>>
  >>
}
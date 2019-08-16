\version "2.18.2"

StanzaOne = \lyricmode {
  %refrain  Start  
  La di la di
  %endrefrain 
  la di la di
  %refrainname=End
  la di la di
}

StanzaTwo = \lyricmode {
  Da li da li
  da li da li
  %refrain:End
}

\language "english"

keyTime = {
    \time 4/4
    \key c \major
}

Soprano = \relative c'' {
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
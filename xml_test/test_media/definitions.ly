%
%  Standard definitions and defaults for Hymnary.org FlexScores
%
\version "2.16.0"
\language "english"

\layout
{
	indent = 0.0\in
	\context 
	{ 
		\ChordNames
		\consists "Stanza_number_engraver"
		\override ChordName #'font-size = #-1
	}
	\context 
	{ 
		\Score
		#(set-accidental-style 'modern 'Score)
	}
	\context 
	{ 
		\Lyrics
		\override LyricText #'font-size = #-0.5
	}
	\context 
	{ 
		\Staff 
		\RemoveEmptyStaves 
	}
}

\numericTimeSignature

\paper
{
	top-margin    = 0.6\in
	bottom-margin = 0.6\in
	left-margin   = 0.75\in
	right-margin  = 0.75\in
	indent        = 0.0\in
	ragged-right  = ##f
	ragged-bottom = ##t
	markup-system-spacing #'padding = #3
	system-system-spacing #'padding = #3
	top-system-spacing #'padding = #5

	oddHeaderMarkup = \markup
	{
		\on-the-fly #not-first-page  \column
		{  
			\normalsize \fill-line 
			{
				\fromproperty #'header:fsHymnNumber
				\fromproperty #'header:title   
				\null     
			}
			\small \fill-line 
			{
				\fromproperty #'header:instrument        
			}
		}
	} % end of oddHeaderMarkup
	
	evenHeaderMarkup = \oddHeaderMarkup

	oddFooterMarkup = \markup
	{
		\fontsize #-6.0 \column
		{
			\on-the-fly #first-page 
			{
				\line { \italic \fromproperty #'header:note }
				\line { \transparent _ }
			}
		
			\line { \italic \fromproperty #'header:fsHymnal 
				\fromproperty #'header:fsHymnNumberOriginal }
			\line { \fromproperty #'header:fsTextCredit }
			\line { \fromproperty #'header:fsTuneCredit }
		
			\on-the-fly #first-page 
			{
				\hspace #0
				\fill-line { \line { \center-column { \sans \fromproperty #'header:fsURL } } }
			}
		}
	} % end of oddFooterMarkup

	evenFooterMarkup = \oddFooterMarkup

	scoreTitleMarkup  = \markup \null

	bookTitleMarkup = \markup
	{
		\column
		{
			 \fill-line
			{
				\fontsize #4.5 \fromproperty #'header:fsHymnNumber
				\fontsize #4.5 \fromproperty #'header:title
				\null
			}
			
			\fill-line { \fontsize #1 \fromproperty #'header:subtitle }
			\fill-line { \fontsize #1 \fromproperty #'header:instrument }
			
			\fill-line 
			{ 
				\null
				\fontsize #0 \fromproperty #'header:fsAuthor 
			}	
		}
	} % end of scoreTitleMarkup

} % end of paper options

%
% if a voice uses \removeWithTag #'vocalMarkup, items tagged thus won't be shown
%
hideSlur = 
{
	\override Slur #'transparent = ##t
	\tag #'vocalMarkup  \override Slur #'transparent = ##f
}

% Add a custom "projection" paper size
#(set! paper-alist (cons '("projection" . (cons (* 6 in) (* 4 in))) paper-alist))



--------------------------------------------------------------------------------
AuCoPro - Splitting
--------------------------------------------------------------------------------

Creator(s):
  Menno van Zaanen (1) & Gerhard B. van Huyssteen (2)

  (1) Tilburg centre for Cognition and Communication,
  School of Humanities, Tilburg University,
  http://ticc.uvt.nl
  
  (2) Centre for Text Technology (CTexT),
  North-West University, South Africa
  http://www.nwu.ac.za/ctext

Version: 2014-01-31
Language: Dutch & Afrikaans

This dataset is available at http://tinyurl.com/aucopro

License:
  The dataset is licensed under a Creative Commons Attribution 3.0
  Unported License. Please read the terms of use carefully.
  http://creativecommons.org/licenses/by/3.0/
  (Full legal code enclosed: License.txt)

Description:
  The AuCoPro-Splitting dataset contains compounds annotated with
  their compound boundaries and linking morphemes.  The dataset
  consists of two files, one for Afrikaans and one for Dutch.  The
  annotation was performed according to annotation guidelines as
  described in Verhoeven, van Huyssteen, van Zaanen, & Daelemans
  (2014).
  
If you use this dataset in your research, make sure to cite the
following paper:

  van Zaanen, M., van Huyssteen, G., Aussems, S., Emmery, C., &
  Eiselen, R.  2014.  The Development of Dutch and Afrikaans Language
  Resources for Compound Boundary Analysis.  In: Proceedings of the
  9th International Conference on Language Resources and Evaluation
  (LREC 2014). Reykjavik, Iceland.


Acknowledgement:
  This dataset was created within the 'Automatic Compound Processing
  (AuCoPro)' project that was funded by the Dutch Language Union
  (Nederlandse Taalunie), the Department of Arts and Culture (DAC) of
  South Africa and the National Research Foundation (NRF) of South
  Africa.

--------------------------------------------------------------------------------
Specifics
--------------------------------------------------------------------------------

Reference for the annotation schemes:

  Verhoeven, B., van Huyssteen, G.B., van Zaanen, M., & Daelemans, W.
  (2014).  Annotation Guidelines for Compound Analysis. CLiPS
  Technical Report Series, 5.
  
Dataset name encoding:

  Afr: language of dataset is Afrikaans
  Ned: language of dataset is Dutch
  
Files included:

  Afr   List.AUCOPRO.AfrikaansSplitting.txt
  Ned   List.AUCOPRO.DutchSplitting.txt
  
File format:

  Each file contains a list of compounds (each compound is described
  on one line).  Compound boundaries are indicated by a + sign and
  the _ sign indicate the start of a linking morpheme.  The _ and +
  signs are surrounded by a single space.

Terms explained:

  IAA or inter-annotator agreement is a percentage of agreement
  between two annotators, indicating how often they assign the same
  annotation to an item.
  
  Kappa is another measure of agreement between two annotators. It is
  considered to be a better indication of annotation quality because
  it takes the class distribution of the annotation into account.
  When calculating IAA or Kappa for more than two annotators, we
  compute the pair-wise average (i.e. the average of the score for
  each pair of annotators).
  
  For Dutch, the list of potential compounds was divided into files of
  1000 words each.  The first file was annotated by both annotators,
  then each annotator annotated two files and each third file was
  annotated by both annotators.  This allowed us to compute IAA and
  Kappa.

  For Afrikaans, files of 1000 words each have been annotated by two
  of annotators each.  IAA and Kappa are computed based on these
  files.
  
--------------------------------------------------------------------------------
Data statistics
--------------------------------------------------------------------------------

---------------
  Afr
---------------

Initial number of items:       25266
Items used for IAA/Kappa:      12818
Number of remaining compounds: 18503
Number of annotators:              7

Average IAA:         96.8% (sd=2.1)
Average Kappa:       98.6  (sd=0.8)

---------------
  Ned
---------------

Initial number of items:       26000
Items used for IAA/Kappa:       6000
Number of remaining compounds: 21997
Number of annotators:              2

Average IAA:         95.3% (sd=1.8)
Average Kappa:       97.6  (sd=0.7)

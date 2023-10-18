# FugueStat

Perform visual music-based fugal analysis using subjects, countersubjects, and their transformations.

## Setup

Requires: **python-3.10+**

```bash
python3 -m pip install -r requirements.txt
```

Libraries: **pyyaml**, **numpy**, **pytest**

## Usage

```bash
python3 -m main.py <path-to-musicxml-file>
```

## Terminology
**Fugue**: A contrapuntal composition in which a short melody or phrase (the subject) is introduced by one part and successively taken up by others and developed by interweaving the parts.

*Notable examples for solo piano*:
- Johann Sebastian Bach: *Well-Tempered Clavier 1 & 2* (48 fugues total of all key signatures)
- Ludwig van Beethoven: *Grosse Fuge, Op. 133*
- Ludwig van Beethoven: *Piano Sonata No.28, 29, 31*
- Dmitri Shostakovich: *24 Preludes and Fugues, Op. 87*
- Karol Szymanowski: *Piano Sonata No.2, 3*
- Elliott Carter: *Piano Sonata*
- Kaikhosru Shapurji Sorabji: *Opus Clavicembalisticum* (+ many others)

*(I currently work on the most accurate solo piano performance rendition of "Opus Clavicembalisticum" in history.)*

**Voice**: In a contrapuntal composition, a contiguous and related series of notes which forms a single layer. Like a human voice, it is often both independent and dependent on the concurrent progression of other voices. The majority of fugues are written with 3-4 voices, though some by *Kaikhosru Sorabji* can go up to 8 concurrent voices.

**Interval**: The semitone distance between any two notes. + for ascending, - for descending.

**Subject**: A musical theme introduced as a solo voice at the start of a fugue. The subject is the main focus of the fugue and can undergo subtle to dramatic alterations and transformations as the fugue progresses.

*Alterations include*:
- Entire translation up/down in pitch
- Decreasing/increasing 1 or more intervals' sizes.
- Contiguous partial statement of the subject/countersubject.
- Inserting/deleting a small number of notes from fugal elements.

*Transformations include*:
- *Reversal*: Stating the subject with all the intervals in reverse order.
- *Inversion*: Stating the subject with all the intervals' directions inverted.
- *Reversal & Inversion*: Stating the subject with simultaneous *reversal* and *inversion*.
- *Augmentation*: Stating the subject where each note's duration is 2 or more times longer in duration.
- *Diminution*: Stating the subject where each note's duration is 2 or more times shorter in duration.

**Countersubject**: Material articulated by a second voice which accompanies the second statement of the subject immediately after the first statement completes.

*Countersubjects can undergo similar alterations and transformations as the subject.*

## Problem

In standard music theory, common tasks include performing manual analysis of fugal elements in a piece of music either for academic purposes or to aid in the process of learning to play such pieces of music. Typically, such procedures, done manually, are completely manageable within a reasonable timeframe and have very high accuracy as identification of fugal elements are, more intuitively, a human task. However, personally being a [greenfield performer](https://www.youtube.com/playlist?list=PLIDZcmE0XODBZjc2ISVcJB9--pTWaWRME) of *Kaikhosru Sorabji*'s solo piano works which often contain fugues ranging from 10 minutes to 2 hours in length along with some of the most complex contrapuntal conceptions in all of history, automated analysis could save a massive amount of time.

*Example: Fugue 1's subject from Bach's Well-Tempered Clavier 1*
![WTC1 fugue 1 subject](images/WTC1_fugue_1_subject.png)

*Example: Contrapuntally dense section from Fugue 1 from Bach's Well-Tempered Clavier 1*
![WTC1 fugue 1 excerpt 1](images/WTC1_fugue_1_excerpt_1.png)

With increasing complexity, this process becomes much less trivial (yes, that is solo piano):
*Example: "XI. Fuga IV [Dux Tertius]" from Sorabji's Opus Clavicembalisticum*
![OC Fuga IV excerpt](images/OC_fuga_4_excerpt.png)

## Solution

The solution is inspired by the domain of fuzzy string matching. Fuzzy string matching involves determining whether two strings $A$ and $B$ have some degree of close enough similarity to be considered a match. Applications commonly include DNA sequencing and auto-correction. *e.g.* `"heapt"` has close resemblance to `"heart"`.

The metric for closeness I employ in my algorithm design is the well-known *edit distance*, with many alterations to account for the additional requirements that matching music notes imposes.

However, unlike typical applications of *edit distance*, it is not matched based on the absolute pitch of each note. Because the entire nature of a fugue consists of modulation to other keys and thematic exploration, it is to be expected that entire translations of the initial subject is the norm. Thus, the intervals between the notes encode more information than the notes themselves.

![WTC fugue 1 subject intervals](images/WTC1_fugue_1_subject_intervals.png)

Using the sequence of *intervals* as the basis for fuzzy matching, it's now possible to account for interval contractions/dilations in subsequent subject statements. One can think also of this as "soft" matching.

In the code and here, we will refer to a *voice* as a **note sequence** or **stream**. The subject is synonymously called the **pattern**. The *stream* is almost always longer than the *pattern*, and like its name suggests, the *stream* continuously provides a window (i.e. a buffer) for the *pattern* to iteratively match over the entire piece of music. Again, recall that the *intervals* are used, not the absolute pitches. Let's refer to the length of the sequence of intervals for the stream and pattern to, respectively, be $S$ and $P$. Note, it should be apparent that, in code, voices are treated as separate entities as *note sequences* and are processed independently, even though notes do coincide between voices.

![stream-pattern matching](images/stream_pattern_matching.jpeg)

There are two clear issues with what is shown above. Because note insertion/deletion is possible for the stream, a window size fixed to the length of the pattern is insufficient to capture all likely alterations. Thus, a reasonable assumption to make is that the number of matched notes in the stream is at most some factor $n$ times the size of the pattern sequence intervals $P$. A typical factor is $2$.

There are two levels to the entire algorithm. The lower-level algorithm does something analogous to fuzzy substring matching and the higher-level algorithm controls optimized window propagation.

### Window matching

Let us assume we have a stream window of length $2P$ and pattern length $P$. A typical implementation of edit distance between the stream and pattern calculates the distance between both entire sequences. The issue with this approach is that intermediate edit distance values calculate distance from the start of the stream, which would include costs that are irrelevant.

Assuming the memoization matrix is of dimension $(S + 1) \times (P + 1)$, a known solution is to begin the algorithm by filling the first column with $0$ (to indicate $0$ cost of shifts) and the typical cumulative sum of costs of the absolute value of each interval value in the pattern sequence for the first row. The matrix is then filled *bottom-up* based on the diagram below and associated recurrence relation where the *stream* and *pattern* are denoted *s* and *p* respectively. Edit distance function is denoted by $E$.

![edit distance table](images/edit_distance_table.png)

![recurrence relation](images/recursive_definition.png)

Observe that, unlike typical edit distance, there are two additional cases at the bottom which are unique to this context. $c_\text{sub}$ refers to the substition of an interval, i.e. contraction/dilation. $c_\text{ins}$ and $c_\text{del}$ are typical necessary edit distance computation features. $c_\text{ins+}$ accounts for the case of note insertion and $c_\text{del+}$ accounts for the case of note deletion. The formal definition of the various costs:

![edit distance costs](images/cost_definitions.png)

Operators and values with an asterisk denote edge case handling for rests in the music where intervals are not applicable (i.e. interval between note and rest does not exist). These edge cases are important and do actually affect the outcome of the matching results. Absolute differences are used to model "distance". Finally, a scaling function $f$ is applied to the absolute difference to level off cost as the difference grows. The function is typically $f(x)=\sqrt{cx}$ for some $c\in\mathbb{N^+}$ to avoid one single large interval deviation from preventing the pattern from matching.

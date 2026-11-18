# Reference calculation

The answer is **35,794 equivalence classes**. The model receives only `prompt.txt`, not this solution or the reference programs. This is a reasoning-only counting challenge; its evaluation must distinguish a wrong mathematical claim from an honest inability to complete the calculation.

Represent a schedule by its cyclic list of gaps. Rotating the binary schedule or choosing another starting one rotates that list; reflecting reverses it up to rotation. Thus binary dihedral classes correspond to gap dihedral classes. A symmetry must map ones to ones, so the numbers of rotational and reflection symmetries agree in the two representations. A rotational stabilizer has size dividing all three gap multiplicities, hence divides six; the reflections fixing a word form either an empty set or a coset of its rotational stabilizer.

For a fixed first and second gap, a finite recurrence counts completions. Its state is the remaining multiplicities, previous two values, and the accumulated counts of 11 and unordered 24 edges. Reject 141 when appending; at termination add the last-to-first edge and check both boundary-crossing triples. Sum over the nine choices for the first two gaps. `reference.py` implements this recurrence using integer arithmetic.

Let T_d count rooted gap words invariant under repeating a block d times. The reduced block has length 24/d, multiplicities (12/d,6/d,6/d), and both edge targets 6/d. The recurrence gives:

| d | T_d | Fixes reflection i → −i | Fixes reflection i → 1−i |
|---|---:|---:|---:|
| 1 | 1,707,552 | 600 | 200 |
| 2 | 800 | 0 | 0 |
| 3 | 72 | 6 | 2 |
| 6 | 8 | 0 | 0 |

The reflection counts come from assigning gap values to the singleton/pair orbits of each indicated involution and checking all constraints. Each reflection type occurs half the reduced block length times. For a full length-24 word obtained by repeating a block d times, each reflection of the block has d lifts.

The rotation fixed-point sum is 1,707,552 + 800 + 2×72 + 2×8 = 1,708,512. The reflection fixed-point sum is 12×(600+200) = 9,600. Burnside's lemma therefore gives (1,708,512+9,600)/48 = 35,794.

Subtract counts for larger stabilizers to obtain E_d, the rooted words with exactly d rotations. This yields E_1=1,706,688, E_2=792, E_3=64, E_6=8. Let H_d=d×(24/d)/2 times the sum of the two reduced reflection counts; subtract H contributions from strictly larger stabilizers, then divide by d to get the rooted reflective words with exactly d rotations. These counts are 9,504, 0, 32, 0 for d=1,2,3,6. A reflective gap orbit has 24/d words; a nonreflective orbit has 48/d words.

| r | f | Classes |
|---:|---:|---:|
| 1 | 0 | 35,358 |
| 1 | 1 | 396 |
| 2 | 0 | 33 |
| 2 | 2 | 0 |
| 3 | 0 | 2 |
| 3 | 3 | 4 |
| 6 | 0 | 1 |
| 6 | 6 | 0 |

There are 1,707,552 rooted gap sequences. Counting binary schedules with a marked one gives 24 times the labelled binary count and also 72 times the rooted gap count. Consequently there are **5,122,656 labelled binary schedules**. As another check, summing each class count times 144/(r+f) recovers this labelled count.

## Independent check and limitations

`small_enumeration.py` exhaustively enumerates the analogous 16-gap case, canonicalizing each orbit directly without the recurrence or divisor inversion. It agrees with `reference.solve(16)` on all counts and nonzero stabilizer cells: 9,800 rooted words and 327 classes. The two saved small-case JSON records retain that comparison; the full case is verified by the recurrence, reflection enumeration, and orbit-size consistency checks, not by a second exhaustive full-size enumeration.

Likely failure modes are omitting boundary triples, dividing by 48 despite nontrivial stabilizers, treating gap and bit rootings as the same count, or counting reflection-fixed words as classes without stabilizer correction. None establishes a model failure unless it actually appears in the recorded answer.

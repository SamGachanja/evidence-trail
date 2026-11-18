There are **35,794 equivalence classes**. The intermediate counts are **1,707,552 rooted admissible gap sequences** and **5,122,656 labelled admissible binary schedules**.

### From binary schedules to gap sequences

Write \(x_i\) for the position of the \(i\)-th one in clockwise order, so \(x_{i+1}-x_i=g_i+1\) modulo 72. A gap rotation \(g_i\mapsto g_{i+k}\) that fixes the gap word lifts to the binary translation sending \(x_0\) to \(x_k\). A gap reflection \(i\mapsto c-i\) that fixes the gap word lifts to the binary reflection \(x\mapsto x_0+x_{c+1}-x\). Each lift is unique because its direction and the image of \(x_0\) determine it. Conversely, every binary symmetry induces one of these gap symmetries. Thus gap words give the same dihedral classes and the same stabilizer counts as the binary schedules.

A gap word with \(r\) rotational symmetries consists of \(r\) repeats of a shortest block. Its symbol counts and circular pair counts are multiples of \(r\), so \(r\mid 6\). If a reflection fixes the word, composing it with the \(r\) rotations gives all its fixing reflections, since the product of any two reflections is a rotation. Hence \(f\) is either \(0\) or \(r\), and the eight requested cells exhaust the possibilities. The orbit and stabilizer counting used below follows the standard group-action argument. [MIT 18.310, Counting Patterns](https://math.mit.edu/~djk/18.310/Lecture-Notes/counting_patterns.html)

### Rooted counts

For each divisor \(d\) of 6, count blocks whose \(d\)-fold repeat is admissible. Put \(m=6/d\). The block has length \(4m\), with \(2m\) copies of \(1\), \(m\) copies each of \(2\) and \(4\), and \(m\) pairs of each specified kind. The \(m\) pairs \(11\) leave exactly \(m\) runs of \(1\), alternating around the circle with \(m\) runs of symbols from \(\{2,4\}\). These latter runs have \(2m-m=m\) internal edges in total. All of those edges must switch symbols. The forbidden triple therefore excludes exactly the singleton run \(4\).

Let \(S_m\) count the ordered lists of \(m\) alternating \(\{2,4\}\)-runs with \(m\) copies of each symbol and no singleton \(4\). To calculate it by inclusion–exclusion, force \(j\) named runs to be singleton \(4\), leaving \(k=m-j\) runs. If \(h\) of the remaining runs have even length, they contribute an even number of symbols, and the odd-length runs each contribute one extra symbol beyond their matched pairs. Every remaining run has length equal to its number of switches plus one. The \(m\) switches therefore require \(h+2p=m\), where \(p\) counts the additional pairs of switches beyond the first switch in each even-length run. Among the \(k-h\) odd-length runs, exactly \(p\) must start with \(2\) to give \(m\) copies of \(2\). This gives
\[
S_m=\sum_{j=0}^{m-1}(-1)^j\binom mj
\sum_{\substack{0\le h\le m-j\\m-h\ {\rm even}}}
\binom{k}{h}2^h\binom{k+p-1}{p}\binom{k-h}{p},
\qquad k=m-j,\quad p=(m-h)/2.
\]
Here the middle binomial distributes the \(p\) additional pairs of switches among the \(k\) runs. The unsigned inner sums and resulting counts are:

| \(m\) | Inner sums in order of \(j\), omitting trailing zeros | \(S_m\) | Rooted blocks |
|---:|:---|---:|---:|
| 1 | \(2\) | 2 | 8 |
| 2 | \(8,1\) | 6 | 72 |
| 3 | \(44,8\) | 20 | 800 |
| 6 | \(11624,2550,320,10\) | 924 | 1,707,552 |

The rooted-block column is \(4\binom{2m-1}{m-1}S_m\). To see the factor \(4\), mark one of the \(m\) starts of a \(1\)-run. Choose its position in \(4m\) ways, choose the ordered positive lengths of the \(1\)-runs, and choose the ordered \(\{2,4\}\)-runs. Dividing by \(m\) removes the mark, including on periodic words.

For the labelled binary count, a rooted gap word and a choice of the position of its starting one give a schedule with a distinguished one. Each labelled schedule has 24 choices of that one, so the labelled count is \(72(1{,}707{,}552)/24=5{,}122{,}656\).

### Reflection counts and exact stabilizers

Work first with rotation classes of the length-\(4m\) blocks. Index the alternating runs starting at a \(1\)-run. There are \(m\) possible reflection axes on this indexed run circle that preserve the two run types. Each such reflection reverses the contents of the runs. A reflection-symmetric rotation class with \(s\) fixing rotations has \(m/s\) indexed representations, each fixed by \(s\) axes. It therefore contributes \(m\) to the total number of fixed incidences. Dividing that total by \(m\) gives the number \(A_m\) of reflection-symmetric rotation classes, even when the block is periodic.

For odd \(m\) an axis fixes one run of each type. The fixed \(\{2,4\}\)-run must account for an odd count of each symbol, since all other such runs are paired. A fixed alternating run is a palindrome of odd length, making those two odd counts impossible. Thus \(A_1=A_3=0\).

For even \(m=2q\), half the axes fix two \(1\)-runs and half fix two \(\{2,4\}\)-runs.

- **Two fixed \(1\)-runs.** The paired \(\{2,4\}\)-runs give \(S_q\) choices. The positive \(1\)-run lengths must sum to \(4q\), counting each of the \(q-1\) paired lengths twice. There are \(3\) choices for \(q=1\). For \(q=3\), the two paired lengths can sum to \(u=2,3,4,5\), giving \(\sum_{u=2}^{5}(u-1)(11-2u)=30\) choices. The fixed counts are \(3\cdot2=6\) and \(30\cdot20=600\).
- **Two fixed \(\{2,4\}\)-runs.** The paired \(1\)-runs give \(\binom{2q-1}{q-1}\) choices. Write the two fixed alternating palindromes as lengths \(2a+1\) and \(2b+1\). For \(q=1\), the only assignments are the two orders of \(2\) and \(424\). For \(q=3\), the two remaining pairs of alternating runs must use half the symbol counts left by the fixed runs. The enumeration is below. This gives fixed counts \(2\) and \(10\cdot20=200\).

| \(a+b\), for \(q=3\) | Fixed runs and choices for the two remaining run pairs | Count |
|---:|:---|---:|
| 0 | Both fixed runs are \(2\). The remaining lengths are \(2,3\) in either order, with two starts for the even run. | 4 |
| 1 | The fixed runs are \(2,424\) in either order. The remaining lengths are \(1,3\) in either order or \(2,2\) with four choices of starts. | 12 |
| 2 | The sole contributing choice has both fixed runs equal to \(424\). The remaining lengths are \(1,2\) in either order, with two starts for the even run. | 4 |
| 3 | Both remaining runs would be singletons, with one required to be \(4\). | 0 |

Averaging the two axis counts gives \(A_2=4\) and \(A_6=400\).

The rooted counts for \(d=1,2,3,6\) include every word whose rotational stabilizer order is a multiple of \(d\). Subtracting the proper multiples gives exact rooted counts of \(1{,}706{,}688,\ 792,\ 64,\ 8\), respectively. Dividing by the corresponding rotation orbit sizes \(24/r\) gives \(71{,}112,\ 66,\ 8,\ 2\) rotation classes. Reflection symmetry descends to the shorter block and lifts on repetition, so the same subtraction applied to \(A_{6/d}\) gives \(396,\ 0,\ 4,\ 0\) reflection-symmetric rotation classes of exact orders \(1,2,3,6\). Each such class is already a dihedral class. The remaining rotation classes join in pairs under reflection.

```json
{
  "rooted_gap_sequences": 1707552,
  "labelled_binary_schedules": 5122656,
  "dihedral_orbits": 35794,
  "profiles": [
    {"r": 1, "f": 0, "orbits": 35358},
    {"r": 1, "f": 1, "orbits": 396},
    {"r": 2, "f": 0, "orbits": 33},
    {"r": 2, "f": 2, "orbits": 0},
    {"r": 3, "f": 0, "orbits": 2},
    {"r": 3, "f": 3, "orbits": 4},
    {"r": 6, "f": 0, "orbits": 1},
    {"r": 6, "f": 6, "orbits": 0}
  ]
}
```
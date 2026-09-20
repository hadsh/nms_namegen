# Can the generator predict dissonance?

Labelled set: 1002 non-purple systems, 573 dissonant and 429 clean, joined on
`(sysaddress, galaxy_namegen)` from the two ground-truth fixtures. Positives
come from `nms-dissonant-non-purple-ground-truth-2026-09-18.json`, which
carries no `false` rows at all; negatives come only from
`nms-systems-ground-truth-2026-08-23.json` where `dissonant` is literally
`False`, since a null there means the field was not recorded. The two corpora
contradict each other on nothing.

**The 57% dissonant rate of that joined set is an artefact and is never used
as a prevalence.** It pools a full eligible pool of positives with a
per-colour capped sample of negatives. The real non-purple prevalence, taken
from the balanced corpus alone, is 15.7%. Section 5 is the only honest
accuracy comparison in this report; everything before it measures separation,
not skill.

Purple is excluded throughout. Purple systems are 96% dissonant and purple is
a plain SSI window, so including them would score that window.

## 1. What a candidate has to beat

| Baseline (development set, n=806, 460 dissonant) | Agreement |
|---|---|
| always predict false | 0.5707 |
| best constant per star type | **0.7469** |
| best constant per body count | 0.6129 |
| star type x body count | 0.7469 |
| every field the library predicts, 432 cells (pure overfit ceiling) | 0.8821 |

Star type alone reaches 0.7469 *without any candidate reading at all*,
because star colour is confounded with the label by the sampling. That, not
0.5707, is the number a candidate has to improve on, and every figure below
is scored with a threshold fitted per star type so the comparison is like for
like.

## 2. The controls

A search that finds nothing proves nothing unless it can be shown to find
something that is there. Two controls, both run by `sweep.py` over the
identical candidate set:

| Control | Top candidate | Stratified agreement |
|---|---|---|
| the library's own `uncharted` reading | `W:uncharted.lo` | **0.9975** (next best 0.9926) |
| planted any-body `pname+3 rng(28)==0`, 16.5% positive | `B:pname+3.lo` | **1.0000** |
| planted any-body `mix+11 rng(28)==0`, 19.6% positive | `B:mix+11.lo` | **1.0000** |
| planted any-body `plan+1 rng(32)==0`, 13.8% positive | `B:plan+1.lo` | **1.0000** |
| planted any-body `plain+7 rng(20)==0`, 24.9% positive | `B:plain+7.lo` | **1.0000** |

The first proves the sweep finds a real *system-level* reading; it recovers
the exact word `systemAttributes()` compares against `EMPTY_SYSTEM_THRESHOLD`,
from scratch, top of 819 candidates. The four planted rules prove it finds a
real *per-body* one, at the shape and marginal rate being hunted.

Two details of the scorer are load-bearing, and the `uncharted` control fails
without either. Thresholds must sit only between distinct score values, or a
tie-splitting walk lets a *constant* candidate score 100%. And thresholds must
be fitted per star type, because every probability gate the route contains is
a per-star-type table.

## 3. The sweep

819 threshold candidates: every word the library consumes mid-stream
(economy, wealth, conflict, race, abandoned, uncharted, prime), forty forward
peeks off each of the four stream origins (`sysStart`, `sysTail`,
`planStart`, `planTail`) in both halves, and forty words downstream of every
body seed under six reseedings (`plain`, `pname`, `sys`, `plan`, `mix`,
`mixplan`), plus the raw body seeds and the pre-draw stream words. Per-body
candidates are aggregated with `min`, which is exactly "at least one body
fired".

| Candidate | Stratified | Flat |
|---|---|---|
| star-type-only baseline (no candidate) | 0.7469 | 0.5707 |
| `S:sysStart+9.hi` | 0.7854 | 0.5732 |
| `W:prime.lo` | 0.7854 | 0.5707 |
| `W:uncharted.lo` | 0.7804 | 0.5707 |
| `S:sysTail+1.lo` (the pirate peek word) | 0.7655 | 0.5819 |
| `B:plain+35.hi` | 0.7618 | 0.5980 |

Best of 819: **0.7854**, which is **+0.0385** over using no candidate. The
controls put a correct reading at +0.25 on the same scale.

161,419 boolean candidates then cover the shapes a threshold cannot express -
`rng.random(N) == k` for every k and 25 moduli, all 32 single-bit tests, and
per-body aggregation by `all` and by `first body` as well as `any`:

| | Agreement | Gain over baseline |
|---|---|---|
| star-type-only baseline | 0.7469 | - |
| best of 161,419 boolean candidates | 0.7556 | **+0.0087** |

+0.87 of a point is below what the maximum of 161k noise candidates is
expected to reach by chance. There is nothing there.

## 4. Not an address window either

Purple is not drawn; it is the SSI range `0x3E9-0x429`. Dissonance could have
been the same shape. It is not: no field holds a contiguous window worth
anything against the 0.5719 majority.

| Field | Best window | Agreement |
|---|---|---|
| SSI | none exists | 0.5719 |
| SSI mod 8 / mod 16 / >> 4 | none exists | 0.5719 |
| X | 4-4095 | 0.5998 |
| Z | 7-4095 | 0.5968 |
| Y | 1-255 | 0.5739 |
| galaxy | 0-254 | 0.5739 |
| renegade count | 0-112 | 0.5848 |
| body count | 4-6 | 0.6028 |
| star type | 0-0 | 0.7405 (the sampling artefact) |
| best single address bit (bit 10) | - | 0.5788 |

## 5. The held-out fifth, and true prevalence

The held-out 20% is fixed by a hash of the address and was looked at once,
after the search was finished.

| Held-out (n=196, 113 dissonant) | Agreement | Precision | Recall |
|---|---|---|---|
| always predict false | 0.4235 | - | 0.0000 |
| star type only (no candidate) | 0.7245 | 0.7757 | 0.7345 |
| best dev candidate `S:sysStart+9.hi` | 0.7653 | 0.7965 | 0.7965 |
| `#bodies` | 0.7092 | 0.7745 | 0.6991 |
| `B:plain+35.hi` | 0.7296 | 0.7679 | 0.7611 |

The candidate carries +4.1 points over star type alone, and star type is the
sampling. On the unbiased balanced corpus, where the prevalence is real, the
same rules are worse than saying nothing:

| Balanced corpus, non-purple (n=509, 15.7% dissonant) | Agreement | Precision | Recall |
|---|---|---|---|
| **always predict false** | **0.8428** | - | 0.0000 |
| `S:sysStart+9.hi` (thresholds from dev) | 0.6778 | 0.1500 | 0.2250 |
| `#bodies` | 0.6857 | 0.1552 | 0.2250 |
| `B:plain+35.hi` | 0.6798 | 0.1783 | 0.2875 |

Refitted directly on that corpus with no held-out at all - the most generous
test that can be constructed - the same candidates reach 0.8428, 0.8428 and
0.8487. Even allowed to overfit, they cannot beat always-predict-false by
more than six tenths of a point.

## 6. Body count, the one real signal

| Predicted bodies | Dissonant | Clean | Rate |
|---|---|---|---|
| 2 | 17 | 36 | 0.321 |
| 3 | 38 | 50 | 0.432 |
| 4 | 75 | 71 | 0.514 |
| 5 | 100 | 83 | 0.546 |
| 6 | 343 | 189 | 0.645 |

Monotone, and the same curve comes out of the corpus's own observed body
counts rather than the predicted ones. This is what an independent per-body
draw looks like, and it is consistent with dissonance being an overlay on a
body rather than a property of the system. It is also useless as a predictor:
row 6 alone would misclassify a third of its systems, and at true prevalence
it scores below always-predict-false.

## 7. What this rules out, and what it does not

Ruled out: any reading - threshold or boolean, consuming or peeked - of any
word at any of the probed positions in the `systemAttributes` stream or the
`planetSeeds` stream, including forty words downstream of every body seed
under six reseedings; and any window or bit test on the address.

Not ruled out, and the place to look next: the per-planet attribute
generator. The library agrees with the corpus at 98-99% on every downstream
field in both streams, so no unaccounted *consuming* draw exists in either -
one would desync everything after it and that agreement would collapse. But
`planetSeeds()` produces a body seed per body and stops there. Nothing in
this library turns a body seed into body attributes - biome, terrain,
sentinel level. Dissonance is a sentinel-level property of a body. It is
almost certainly drawn in that generator, from the body seed, which means it
is reachable in principle and simply is not ported. Porting it is the work.

Also not ruled out: that `dissonant` does not mean what we assumed. It is the
one field the balanced corpus's `method` block does not document and `codes`
has no entry for it. Everything here reads it as "this system contains at
least one dissonant body". Nothing in the results contradicts that - the
body-count trend mildly supports it - and nothing confirms it.

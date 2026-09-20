# Dissonance research

Question: `nms_namegen` derives star colour, economy, wealth, conflict, race,
body counts and the uncharted / abandoned / pirate flags from a portal
address, at 98-99% agreement. Can it derive **dissonance** too?

Answer (see `report.md` for the numbers): **no, and not for want of looking.**

* **No reading of either PRNG stream predicts it.** 819 threshold candidates
  and 161,419 boolean ones, covering every word this library consumes, forty
  forward peeks off each of the four stream origins, and forty words
  downstream of every body seed under six different reseedings. The best of
  them lands 3.9 points above a baseline that uses no candidate at all, where
  a correct reading lands 25 points above it.
* **It is not an address window either.** Purple is a plain SSI range, so
  dissonance could have been the same shape. No field of the address - SSI,
  X, Y, Z, galaxy, distance band, modular residue, or any single bit - holds
  a window better than 0.60 against a 0.57 majority.
* **At true prevalence nothing beats always-predict-false.** On the unbiased
  balanced corpus (15.7% dissonant), always-false scores 84.28%; the best
  candidate refitted on that very corpus reaches 84.87%, and applied honestly
  it scores 67.8%.
* **Body count is the only real signal, and it is weak.** Dissonance rises
  monotonically with the number of bodies, which is what an independent
  per-body draw looks like, but it separates nothing: 0.32 at two bodies to
  0.65 at six.

The searches are controlled, which is the only reason a null result here is
worth writing down. The same sweep recovers the library's own `uncharted`
reading at 0.9975 from scratch, and recovers four planted per-body rules -
"some body fired a 1-in-N draw at word i of its own stream", the exact shape
being hunted - at 1.0000 each. It is not blind to what it failed to find.

**Where dissonance most likely lives.** The library agrees with the corpus at
98-99% on every field downstream in both streams, so there is no unaccounted
*consuming* draw anywhere in either: one would desync everything after it and
that agreement would collapse. A dissonance draw can therefore only be a
non-consuming peek - all of which were probed - or live somewhere this
library does not go. It does not go far: `planetSeeds()` produces a body
*seed* for each body and stops. Nothing here generates body *attributes* -
biome, terrain, sentinel level. Dissonance is a sentinel-level property of a
body, so it is decided in the per-planet attribute generator, which is not
ported. Porting that is the work; scoring more candidates is not.

On the label. `dissonant` means one planet in the system is dissonant. It
is the single field the balanced corpus's `method` block does not document
and `codes` has no entry for it, so that comes from the corpus's compiler,
not the file. It is a per-body overlay reported at the system level, which
is why it can only be scored in aggregate here.

## Scripts

Run with a Python that has numpy (the ggf venv). Everything is scored against
the two fixtures under `test/fixtures/`; neither is written to.

```
python build_corpus.py     # the two fixtures -> data/joined.json (1002 systems)
python trace.py            # assert the instrumented route still matches the library
python sweep.py            # controls, then the threshold sweep   (~10s)
python sweep_boolean.py    # the boolean sweep, 161k candidates   (~3m)
python address_windows.py  # the purple-shaped hypothesis
python evaluate.py         # the held-out fifth, and true prevalence
```

`data/` is git-ignored and every file in it is rebuilt by `build_corpus.py`.

The development / held-out split is fixed by a hash of the address, so it
does not move between runs. The held-out fifth was looked at once, by
`evaluate.py`, after the search was finished.

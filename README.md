# NMS NAMEGEN

Fork of [stuart/nms_namegen](https://github.com/stuart/nms_namegen).

`namegen.py` generates names for regions, systems and planets in the game
No Man's Sky, the same way the game does. It also exposes the raw
system-generation data (planet/moon counts, star type, safe start planet,
voxel flags) that the game derives from the same seeds.

You can use the modules in the `nms_namegen` folder directly in your own
code, or use `namegen.py` as a command line utility.

## How often it is right

Measured against `test/fixtures/nms-systems-ground-truth-2026-08-23.json`:
1000 star systems recorded by hand by players on the community wiki, 200
per star colour, spread over 64 galaxies. Every address is derived from
the portal coordinates and confirmed twice, by the region name and by the
distance to the galactic centre. Every record is post-Origins. No value in
that file is computed, predicted or completed by this library or any
other, which is what makes it usable as a scoreboard.

| Field | Agreement | Sample |
|---|---|---|
| Star colour | 99.10% | 991/1000 |
| Uncharted system | 99.80% | 998/1000 |
| Dominant race | 99.10% | 991/1000 |
| Conflict level | 99.03% | 817/825 |
| Economy category | 99.02% | 811/819 |
| Wealth tier | 98.90% | 811/820 |
| Planet count | 98.80% | 988/1000 |
| Planet and moon counts, both | 98.40% | 984/1000 |

Samples differ because a record only counts for a field it actually
carries: the corpus never fills a blank in.

## What this fork changes

Compared to upstream:

* [GoodGuysFree](https://github.com/GoodGuysFree) fixed Threefish/Skein
  64-bit mixing in `iprng.py` (unmasked additions previously corrupted
  ~10% of universal addresses), and restored the black hole / Atlas
  station anomaly handling, the purple star window, an abandoned-system
  draw, and a proper purple gas-giant gate in `system.py`. Corpus-verified
  against the [glyphs.had.sh](https://glyphs.had.sh/) spatial database
  (wiki-Euclid/AGT data, ~1,091 labelled purple systems); see the comments
  in `nms_namegen/system.py` and `nms_namegen/iprng.py` for the numbers
  behind each fix.
* GoodGuysFree also added the `attributes` CLI command, exposing system
  composition (planet counts, safe start, gas giant, rendered planet/moon
  split) as JSON.
* This fork additionally restores `star_type` to `systemAttributes()`'s
  return dict (dropped when `attributes` was added), and adds CLI
  commands (`system-attributes`, `planet-seeds`, `voxel`) exposing the
  remaining raw library functions as JSON.
* The planet/moon split in `planetSeeds()` was reworked. The extra-body
  loop now draws its size class before its seed and can turn extra bodies
  into moons (it previously did neither, and burnt a stray draw), the
  safe-start draw spans `0..planet_count` rather than one slot more, and
  purple systems route all their bodies through that loop behind two
  nested probability draws instead of one flat gate. The defect was
  specific to purple systems: planet counts go from 58.1% to 94.1% on
  1,041 labelled purple systems, and gas-giant precision from 80.3% to
  94.7%. Ordinary systems were already close and move from 93.0% to 93.3%
  (7,314 systems). See the comments in `nms_namegen/system.py`.
* `voxelAttributes()` now truncates the galactic-centre distance to an
  integer before the central-gap test and the renegade subtraction, which
  is where a slice of voxels was landing in the wrong band. This is a
  fidelity fix only, with no measurable effect on either corpus.

Corpus figures above are measured against community records discovered in
2025 or later. The game has regenerated its universe several times, most
visibly at the Origins update, and older records describe a universe this
generator no longer produces: single-body systems are 7.1% of pre-2021
records and 0.2% of recent ones, and body counts match at 59% against 95%.
Measuring across all eras scores the archive, not the generator.
* `voxelAttributes()` also folds the x/y/z portal-code coordinates to
  signed offsets from the galactic centre before computing distance,
  instead of using the raw unsigned bits. That was skewing the
  `star_type` renegade override for systems near the coordinate
  boundary (0.00% median error vs a corpus of 5531 wiki region pages).
* `systemAttributes()` now also derives `economy_type`, `wealth`,
  `conflict_level` and `dominant_race`, reusing four RNG draws that
  were already being consumed but previously discarded. See the
  Library section below for details and corpus match rates.
* `systemAttributes()` now also reports whether a system is `uncharted`,
  `abandoned` or `pirate`. The first two come from draws the library was
  already making and throwing away, the third from a draw the generator
  peeks at without consuming, so none of them moves the RNG stream. An
  uncharted system has no faction, and `dominant_race` now returns 0 for
  it rather than a race the game never shows.
* The corpus figures for the four infobox fields are now measured on a
  1000-system ground truth (`test/fixtures/`) recorded by hand by
  players, with addresses confirmed by two independent checks and every
  record post-Origins. See the Library section.
* `planetSeeds()` additionally exposes `sizes`, the per-slot size roll
  it already computes internally to decide moon placement. Marked
  experimental, see Library below.

## Installation

The project uses [Pipenv](https://pipenv.pypa.io/en/latest/). Install
dependencies with `pipenv update`, or just use pip.

## Dependencies

This code requires only one dependency:
* numpy ~=2.4

## Usage

```
namegen.py [-h] [-p PSSSYYZZZXXX] [-g GALAXY] [-s SEED] {region,system,planet,attributes,system-attributes,planet-seeds,voxel}
```

*Note that the argument format has changed recently and is not backward
compatible.*

### Commands

| Command | Returns | Needs |
|---|---|---|
| `region` | Region name | `-p`, `-g` |
| `system` | System name | `-p`, `-g` |
| `planet` | Planet name | `-p`, `-g` or `-s` |
| `attributes` | System composition as JSON: planet counts, safe start planet, gas giant flag, star type, rendered planet/moon split | `-p`, `-g` |
| `system-attributes` | Raw `systemAttributes()` dict as JSON (same fields as `attributes`, without the rendered planet/moon split) | `-p`, `-g` |
| `planet-seeds` | Raw `planetSeeds()` dict as JSON: planet seeds, rendered planet/moon counts | `-p`, `-g` |
| `voxel` | Raw `voxelAttributes()` dict as JSON: black hole / Atlas station / central gap flags | `-p` only, ignores `-g` |

`attributes` is a convenience command: `planet_count`/`prime_planet_count`
are the logical bodies the game assigns, while `rendered_planets`/
`rendered_moons` are how those bodies are actually split for display. The
two differ whenever moons are placed, since every moon takes one of the
logical body slots. `system-attributes` and `planet-seeds` expose the two underlying
dicts unmerged, for callers that need the raw fields (see Library below).

### Options

* `-h, --help` : show help message and exit.
* `-p, --portal_code PSSSYYZZZXXX` : the portal code of the region, system
  or planet. A 12 digit hexadecimal number, format `PSSSYYZZZXXX`. For
  regions the planet and system parts are ignored, for systems the planet
  id is ignored.
* `-g, --galaxy GALAXY` : the galaxy id for the object to be named. Must
  be in the range 0-255. Defaults to 0 (Euclid).
* `-s, --seed SEED` : the seed of a planet. Must be a hexadecimal number.
  It can be found in save game files. Using this overrides `portal_code`
  and `galaxy`. Has no effect for regions or systems.

## Examples

System name. Galaxy defaults to 0.
```bash
./namegen.py system -p 03E9F3545C3E
#output: Abarof-Dulin
```

Region name.
```bash
./namegen.py region -p 03E9F3545C3E -g 0
#output: Yihelli Quadrant
```

Planet name from save seed.
```bash
./namegen.py planet -s 0xC911CCCD7395E842
#output: Nutsvill Sigma
```

Planet name from portal code and galaxy.
```bash
./namegen.py planet -p 1001ff218345 -g 4
#output: Edershar K25
```

System composition attributes as JSON.
```bash
./namegen.py attributes -p 003df8f87945 -g 0
#output: {"planet_count": 3, "prime_planet_count": 1, "safe_start_planet": 3, "gas_giant": false, "star_type": 0, "rendered_planets": 3, "rendered_moons": 1}
```

Raw system attributes (includes `star_type`, `economy_type`, `wealth`,
`conflict_level`, `dominant_race`, and the `uncharted` / `abandoned` /
`pirate` flags).
```bash
./namegen.py system-attributes -p 003df8f87945 -g 0
#output: {"planet_count": 3, "prime_planet_count": 1, "safe_start_planet": 3, "gas_giant": false, "star_type": 0, "economy_type": 6, "wealth": 2, "conflict_level": 2, "dominant_race": 3, "uncharted": false, "abandoned": false, "pirate": false}
```

Raw planet seeds for a system (includes the experimental `sizes` field).
```bash
./namegen.py planet-seeds -p 003df8f87945 -g 0
#output: {"planet_seeds": [6957366409789192041, 11872164497817189863, 12193988597400712801, 6531008701629202253], "planet_count": 3, "moon_count": 1, "sizes": [0, 0, 1]}
```

Voxel flags (black hole / Atlas station / central gap) for a portal code.
```bash
./namegen.py voxel -p 003df8f87945
#output: {"guide_star_count": 120, "black_hole_count": 1, "atlas_station_count": 1, "inside_gap": 0, "guide_star_renegade_count": 0}
```

## Library

`nms_namegen.system.systemAttributes(portal_code, galaxy)` returns a dict with:

* `planet_count`, `prime_planet_count`, `safe_start_planet` : logical body
  counts and the safe-start planet index, as rolled by the game's RNG.
* `gas_giant` : `True` if the system uses the gas-giant layout, a single
  giant planet orbited by every other body as a moon (see `planetSeeds`).
  Purple systems only. Most of these hold six bodies, so 1 planet and 5
  moons, but smaller ones exist.
* `star_type` : star colour class, 0-4 (yellow/white, green, blue, red,
  purple/exotic). Exposed by both the `attributes` and `system-attributes`
  CLI commands, and by `systemComposition()`.
* `economy_type` : economy category, 1-7 (1=trading, 2=advanced
  materials, 3=scientific, 4=mining, 5=manufacturing, 6=technology,
  7=power generation). 99.02% agreement on the ground truth below.
* `wealth` : wealth tier, 1-3 (1=low, 2=medium, 3=high). 98.90%.
* `conflict_level` : conflict level, 1-3 (1=low, 2=medium, 3=high).
  99.03%. Pirate systems are reported through the `pirate` flag rather
  than as a conflict level, see below.
* `dominant_race` : dominant race, 1-3 (1=Gek, 2=Korvax, 3=Vy'keen), or
  0 when the system is uncharted and has none. 99.10%.
* `uncharted` : `True` when the system carries no faction at all, which
  the game shows as an Uncharted system. The ground truth holds 181 of
  them, this predicts 181, and 180 are the same ones: precision and
  recall both 99.4%.
* `abandoned` : `True` for an abandoned system. Rare - one system in a
  thousand - so this flag comes from the generation route and the corpus
  can neither confirm nor deny it. It also drops `wealth` and
  `conflict_level` to their lowest tier, which is what the route does.
* `pirate` : `True` for a pirate-controlled system, read from a draw the
  generator peeks at without consuming. Community records carry no
  pirate field, so this one is unvalidated; note that the systems it
  flags carry ordinary wealth and conflict values in those records,
  which is why neither field is overridden here.

The percentages above come from the ground truth described at the top of
this README. Older figures elsewhere in these notes were measured on
larger but unfiltered wiki dumps, which mix in records describing
universes the game has since regenerated.

`economy_type`, `wealth`, `conflict_level` and `dominant_race` reuse
four RNG draws consumed by the game right after the planet/prime counts
but before `star_type`; the draws themselves were already being made by
this library, only the resulting words were discarded. The formulas and
code-to-label tables were derived independently against a wiki-labeled
corpus, not sourced from any third-party tool - see the comments above
each draw in `nms_namegen/system.py` for the derivation.

`nms_namegen.system.planetSeeds(portal_code, galaxy)` additionally
returns `sizes`, the per-slot size class (0-2) rolled for each planet
slot. It was already being computed internally to decide moon
placement; this just exposes it. **Experimental**: a system-level sanity
check (predicted moon count vs an independently observed moon count)
shows only 62.67% exact agreement, well below the 94-98% match rate of
the fields above, likely because the per-slot RNG order isn't confirmed
to match in-game display order. Do not treat `sizes` as validated at
the per-slot level.

## Testing

```bash
python -m unittest discover -s test
```

`test/test_golden_vectors.py` cross-checks this library against an
independent second implementation across 443 portal codes spanning a
range of galaxies: region/system/planet names, `systemAttributes()`,
`planetSeeds()` (including the `sizes` field) and `voxelAttributes()`
are all compared field by field against `test/fixtures/golden_vectors.json`,
with 0 mismatches.

## Caveats

Region and system name generation was originally tested by Stuart against
a corpus of ~600 system names from AGT data. The system-attribute fixes listed
above (star type, planet/moon counts, purple systems) are separately
corpus-verified against the [glyphs.had.sh](https://glyphs.had.sh/)
spatial database (extract, ~1,091 ground-truth purple
systems); see the comments in `nms_namegen/system.py` and
`nms_namegen/iprng.py` for the specific numbers behind each fix.

Of course it has no knowledge of system names that have been changed by
travellers, it only provides the original naming.

## Development

This code is independently produced and not associated with Hello Games.

## Thanks

Thanks to Stuart Coyle for the original
[nms_namegen](https://github.com/stuart/nms_namegen) this fork is based
on.

Thanks to [GoodGuysFree](https://github.com/GoodGuysFree) for co-authoring
this fork.

Thanks also to Andraemon and [monkeyman192](https://github.com/monkeyman192)
for the earlier code Stuart's version was itself based on
([SystemNameCalculator](https://github.com/andraemon/SystemNameCalculator.git)).

Thanks to [AGT](https://www.nms-agt.com/) for supplying test data.

Thanks to [NMSCD](https://github.com/NMSCD).

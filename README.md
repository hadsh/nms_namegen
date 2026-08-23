# NMS NAMEGEN

Fork of [stuart/nms_namegen](https://github.com/stuart/nms_namegen).

`namegen.py` generates names for regions, systems and planets in the game
No Man's Sky, the same way the game does. It also exposes the raw
system-generation data the game derives from the same seeds: planet and
moon counts, star colour, economy, wealth, conflict, dominant race, and
the uncharted / abandoned / pirate flags.

Everything is computed from a 12-digit portal code and a galaxy number.
Nothing is looked up, downloaded, or read from the game.

Use the modules in the `nms_namegen` folder directly in your own code, or
`namegen.py` as a command line utility.

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

Names are deliberately absent from that table. The corpus uses region
names to confirm its own addresses, so scoring names against it would
measure the filter it was built with, not the generator.

## Installation

Python 3.13 or later, and numpy.

```bash
pip install -e .
```

`pyproject.toml` is the only place dependencies are declared.

## Dependencies

numpy, and nothing else. It is used for the exact float32 and float64
rounding the generator depends on, which plain Python floats do not
reproduce at the comparison edges.

## Usage

```
namegen.py [-h] [-p PSSSYYZZZXXX] [-g GALAXY] [-s SEED] {region,system,planet,attributes,system-attributes,planet-seeds,voxel}
```

*Note that the argument format changed in 2.0 and is not backward
compatible.*

### Commands

| Command | Returns | Needs |
|---|---|---|
| `region` | Region name | `-p`, `-g` |
| `system` | System name | `-p`, `-g` |
| `planet` | Planet name | `-p`, `-g` or `-s` |
| `attributes` | System composition as JSON: planet counts, safe start planet, gas giant flag, star type, rendered planet/moon split | `-p`, `-g` |
| `system-attributes` | Raw `systemAttributes()` dict as JSON | `-p`, `-g` |
| `planet-seeds` | Raw `planetSeeds()` dict as JSON: planet seeds, rendered planet/moon counts, sizes | `-p`, `-g` |
| `voxel` | Raw `voxelAttributes()` dict as JSON: black hole / Atlas station / central gap flags | `-p` only, ignores `-g` |

`attributes` is a convenience command: `planet_count` and
`prime_planet_count` are the logical bodies the game assigns, while
`rendered_planets` and `rendered_moons` are how those bodies are actually
split for display. The two differ whenever moons are placed, since every
moon takes one of the logical body slots. `system-attributes` and
`planet-seeds` expose the two underlying dicts unmerged, for callers that
need the raw fields (see Library below).

### Options

* `-h, --help` : show help message and exit.
* `-p, --portal_code PSSSYYZZZXXX` : the portal code of the region, system
  or planet. A 12 digit hexadecimal number, format `PSSSYYZZZXXX`. For
  regions the planet and system parts are ignored, for systems the planet
  id is ignored.
* `-g, --galaxy GALAXY` : the galaxy id for the object to be named. Must
  be in the range 0-255, counting from 0, so Euclid is 0. Defaults to 0.
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

Raw system attributes.
```bash
./namegen.py system-attributes -p 003df8f87945 -g 0
#output: {"planet_count": 3, "prime_planet_count": 1, "safe_start_planet": 3, "gas_giant": false, "star_type": 0, "economy_type": 6, "wealth": 2, "conflict_level": 2, "dominant_race": 3, "uncharted": false, "abandoned": false, "pirate": false}
```

Raw planet seeds for a system, including the experimental `sizes` field.
```bash
./namegen.py planet-seeds -p 003df8f87945 -g 0
#output: {"planet_seeds": [6957366409789192041, 11872164497817189863, 12193988597400712801, 6531008701629202253], "planet_count": 3, "moon_count": 1, "sizes": [0, 0, 0]}
```

Voxel flags for a portal code.
```bash
./namegen.py voxel -p 003df8f87945
#output: {"guide_star_count": 120, "black_hole_count": 1, "atlas_station_count": 1, "inside_gap": 0, "guide_star_renegade_count": 0}
```

## Library

### Names

* `nms_namegen.region.regionName(portal_code, galaxy)` : region name.
* `nms_namegen.system.systemName(portal_code, galaxy)` : system name.
* `nms_namegen.planet.planetName(portal_code, galaxy)` : planet name. The
  planet digit of the portal code selects the body.

### `nms_namegen.system.systemAttributes(portal_code, galaxy)`

Returns a dict with:

* `planet_count`, `prime_planet_count`, `safe_start_planet` : logical body
  counts and the safe-start planet index, as rolled by the game's RNG.
  For the planet/moon split as displayed, use `planetSeeds()` below.
* `gas_giant` : `True` if the system uses the gas-giant layout, a single
  giant planet orbited by every other body as a moon. Purple systems
  only. Most of these hold six bodies, so 1 planet and 5 moons, but
  smaller ones exist.
* `star_type` : star colour class, 0-4 (0 yellow/white, 1 green, 2 blue,
  3 red, 4 purple/exotic). 99.10%.
* `economy_type` : economy category, 1-7 (1 trading, 2 advanced
  materials, 3 scientific, 4 mining, 5 manufacturing, 6 technology,
  7 power generation). 99.02%.
* `wealth` : wealth tier, 1-3 (1 low, 2 medium, 3 high). 98.90%.
* `conflict_level` : conflict level, 1-3 (1 low, 2 medium, 3 high).
  99.03%.
* `dominant_race` : dominant race, 1-3 (1 Gek, 2 Korvax, 3 Vy'keen), or 0
  when the system is uncharted and has none. 99.10%.
* `uncharted` : `True` when the system carries no faction at all, which
  the game shows as an Uncharted system. The ground truth holds 181 of
  them, this predicts 181, and 180 are the same ones: precision and
  recall both 99.4%.
* `abandoned` : `True` for an abandoned system, and it also drops
  `wealth` and `conflict_level` to their lowest tier. Rare: one system in
  the thousand, so the corpus can neither confirm nor deny this one.
* `pirate` : `True` for a pirate-controlled system. Community records
  carry no pirate field, so this flag is unvalidated. Note that the
  systems it flags carry ordinary wealth and conflict values in those
  records, which is why neither field is overridden for them.

The percentages are the ground-truth figures from the top of this README.

`economy_type`, `wealth`, `conflict_level` and `dominant_race` reuse four
RNG draws made right after the planet counts and before `star_type`;
`uncharted` and `abandoned` reuse two more. All six draws were already
being made by this library, only their results were discarded, so reading
them moves nothing in the RNG stream. `pirate` reads a draw that is
peeked at without being consumed, which likewise leaves the stream where
it was. The formulas and the code-to-label tables were derived against a
wiki-labelled corpus; see the comments above each draw in
`nms_namegen/system.py`.

### `nms_namegen.system.planetSeeds(portal_code, galaxy)`

Returns the per-body seeds, plus `planet_count` and `moon_count`: the
rendered split, after moons have taken their slots.

It also returns `sizes`, the per-slot size class (0-2) rolled for each
body, which it already computes internally to decide moon placement.
**Experimental.** A system-level sanity check (predicted moon count
against an independently observed one) shows 62.67% exact agreement over
3584 systems, far below every field in the table above, most likely
because the per-slot generation order is not confirmed to match the order
the game displays bodies in. Do not treat `sizes` as validated at the
per-slot level.

### `nms_namegen.region.voxelAttributes(portal_code)`

Returns the per-voxel counts that steer system generation: guide stars,
black holes, Atlas stations, the central gap flag, and the renegade guide
star count. Galaxy-independent, so it takes no galaxy argument.

## What this fork changes

Compared to upstream:

* [GoodGuysFree](https://github.com/GoodGuysFree) fixed Threefish/Skein
  64-bit mixing in `iprng.py`, where unmasked additions were corrupting
  about 10% of universal addresses, and restored black hole / Atlas
  station anomaly handling, the purple star window, an abandoned-system
  draw and a purple gas-giant gate in `system.py`. GoodGuysFree also
  added the `attributes` CLI command.
* This fork restores `star_type` to the `systemAttributes()` return dict,
  which was dropped when `attributes` was added, and adds the
  `system-attributes`, `planet-seeds` and `voxel` CLI commands so every
  raw library function is reachable from the command line.
* `systemAttributes()` now derives `economy_type`, `wealth`,
  `conflict_level` and `dominant_race`, and reports whether a system is
  `uncharted`, `abandoned` or `pirate`, all from draws that were being
  made and thrown away.
* The planet/moon split in `planetSeeds()` was reworked. The extra-body
  loop now draws its size class before its seed and can turn extra bodies
  into moons, where it previously did neither and burnt a stray draw; the
  safe-start draw spans `0..planet_count` rather than one slot more; and
  purple systems route all their bodies through that loop behind two
  nested probability draws instead of one flat gate. The defect was
  specific to purple systems: planet counts went from 58.1% to 94.1% on
  1041 labelled purple systems, and gas-giant precision from 80.3% to
  94.7%.
* `voxelAttributes()` folds the x/y/z portal-code coordinates to signed
  offsets from the galactic centre before computing distance, instead of
  using the raw unsigned bits, and truncates that distance to an integer
  before the central-gap test and the renegade subtraction. Two shells of
  voxels change branch as a result, and they carry most of the gain on
  the attribute fields.

Corpus figures in this section were measured before the ground truth
above existed, against community records discovered in 2025 or later. The
game has regenerated its universe several times, most visibly at the
Origins update, and older records describe a universe this generator no
longer produces: single-body systems are 7.1% of pre-2021 records and
0.2% of recent ones. Measuring across all eras scores the archive, not
the generator.

## Testing

```bash
python -m unittest discover -s test
```

52 tests, covering names, system attributes, planet seeds, voxel
attributes and the CLI.

`test/fixtures/golden_vectors.json` pins the full output of this library
for 443 portal codes across a range of galaxies: region, system and
planet names, `systemAttributes()`, `planetSeeds()` including `sizes`,
and `voxelAttributes()`. `test/test_golden_vectors.py` replays them, so
it catches any unintended change in behaviour. The file is generated from
this library, which makes it a regression net rather than an independent
check; the same 443 vectors are also verified field by field against a
second, independent implementation maintained outside this repository,
which currently agrees on every one.

## Caveats

It has no knowledge of names changed by travellers or by Discovery
Services. It generates the original procedural name only.

Name generation and the system attributes are verified against the whole
[glyphs.had.sh](https://glyphs.had.sh/) spatial database, not a sample of
it. The ground truth shipped in `test/fixtures/` comes out of that work
and is published with this library so the figures above can be checked
rather than taken on trust.

Star colour maps to what players record as a colour, not to a spectral
class: the game shows several spectral classes per colour.

This code is independently produced and not associated with Hello Games.

## Licence

MIT, see `LICENCE`.

## Thanks

Thanks to Stuart Coyle for the original
[nms_namegen](https://github.com/stuart/nms_namegen) this fork is based
on.

Thanks to [GoodGuysFree](https://github.com/GoodGuysFree) for co-authoring
this fork.

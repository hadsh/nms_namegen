# NMS NAMEGEN

Fork of [stuart/nms_namegen](https://github.com/stuart/nms_namegen).

`namegen.py` generates names for regions, systems and planets in the game
No Man's Sky, the same way the game does. It also exposes the raw
system-generation data (planet/moon counts, star type, safe start planet,
voxel flags) that the game derives from the same seeds.

You can use the modules in the `nms_namegen` folder directly in your own
code, or use `namegen.py` as a command line utility.

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
two differ for gas giants, which `planetSeeds` fixes at 1 planet + 5
moons. `system-attributes` and `planet-seeds` expose the two underlying
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

Raw system attributes (includes `star_type`).
```bash
./namegen.py system-attributes -p 003df8f87945 -g 0
#output: {"planet_count": 3, "prime_planet_count": 1, "safe_start_planet": 3, "gas_giant": false, "star_type": 0}
```

Raw planet seeds for a system.
```bash
./namegen.py planet-seeds -p 003df8f87945 -g 0
#output: {"planet_seeds": [6957366409789192041, 11872164497817189863, 12193988597400712801, 6531008701629202253], "planet_count": 3, "moon_count": 1}
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
* `gas_giant` : `True` if the purple gas-giant gate collapsed the system
  to a single gas giant with five moons (see `planetSeeds`).
* `star_type` : star colour class, 0-4 (yellow/white, green, blue, red,
  purple/exotic). Exposed by both the `attributes` and `system-attributes`
  CLI commands, and by `systemComposition()`.

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

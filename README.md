# NMS NAMEGEN

nms_namegen.py is a python program that generates names for 
regions and systems in the game No Man's Sky. 

It generates them in the same way that the game does.

You may use the modules included in the /nms_namegen folder in your own work or use the namegen.py as a command line utility. 

## Installation 
The project uses [Pipenv](https://pipenv.pypa.io/en/latest/)
You can install dependecies with ```pipenv update```
Or just use pip.

## Dependencies
This code requires only two dependencies:
    - numpy ~=2.4
    - roman ~=5.2

## Usage 

*namegen.py command portal_code galaxy_id*

command is one of: *system*, *region* or *help* 

Portal code must be the 12 hexadecimal (0-F) digit portal code. For systems the first digit (planet id) is ignored, just set it to 0 if you want. For regions the first four digits are ignored (planet and system id)

The galaxy id is the galaxy number with Euclid starting at 0 and the last
galaxy being 255.

For planet names the command is: 

*namegen.py planet planet_seed* 

The *planet_seed* is a 16 digit hexadecimal seed. 
You can find them in save files under BaseContext -> PlayerStateData -> PlanetSeeds

Currently I have not worked out any way to dermine planet seeds given portal_code and galaxy.

Examples: 

```bash
 ./namegen.py system 03E9F3545C3E 0
 #output: Abarof-Dulin
```

```bash
 ./namegen.py region 03E9F3545C3E 0
 #output:Yihelli Quadrant
```

```bash
./namegen.py planet 0xC911CCCD7395E842
 #output:Nutsvill
```
(I like when I find a funny name!)

## Caveats 
As far as I can tell this generates the correct names for regions and 
systems. The system name generation has been tested on a corpus of ~600 system names
from AGT data. It differs only where a profanity filter has changed the system name.
Planet names have not been as thoroughly tested yet. If someone has a load of correct planet_code, name pairs they
want to share, I'd be happy. 
Of course it has no knowledge of system names that have been changed by travellers, it only provides the original naming. 

## Development 
The code was written by Stuart Coyle. 

It is based on C Sharp code from [SystemNameCalculator](https://github.com/andraemon/SystemNameCalculator.git) by Andraemon.

This code is independently produced and not associated with Hello Games. 

## Thanks 
Thanks go to Andraemon and (monkeyman192)[https://github.com/monkeyman192] for the original code this is based on. 

Thanks to had of (had.sh)[https://had.sh/] and the (AGT)[https://www.nms-agt.com/] for supplying test data to enable 
the extension of the system name code. 

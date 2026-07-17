# fork of
# NMS NAMEGEN

namegen.py is a python program that generates names for 
regions, systems and planets in the game No Man's Sky. 

It generates them in the same way that the game does.

You may use the modules included in the /nms_namegen folder in your own work or use the namegen.py as a command line utility. 

## Installation 
The project uses [Pipenv](https://pipenv.pypa.io/en/latest/)
You can install dependecies with ```pipenv update```
Or just use pip.

## Dependencies
This code requires only one dependencies:
    - numpy ~=2.4

## Usage 
*Note that the argument format has changed recently and is not backward compatible*

    namegen.py [-h] [-p PSSSYYZZZXXX] [-g GALAXY] [-s SEED] {region,system,planet}

Generates names for regions, systems and planets in the game No Man's Sky.


* {region,system,planet} : The type of object to get the name of.

### Options:

* *-h, --help*  
Show help message and exit

* *-p, --portal_code* PSSSYYZZZXXX  
The portal code of the region, system or planet. A 12 digit hexadecimal
number, format: PSSSYYZZZXXX. For regions the planet and system parts are
ignored, for systems the planet id is ignored.

* *-g, --galaxy* GALAXY  
The galaxy id for the object to be named. Must be in the range 0-255.
Defaults to 0 (Euclid).

*  *-s, --seed* SEED        
This is the seed of a planet. Must be a hexidecimal number. It can be
found in save game files. Using this overrides portal_code and galaxy
options. Has no effect for regions or systems.

## Examples: 

Galaxy defaults to 0.
```bash
 ./namegen.py system -p 03E9F3545C3E
 #output: Abarof-Dulin
```

Region name generation.
```bash
 ./namegen.py region -p 03E9F3545C3E -g 0
 #output:Yihelli Quadrant
```

Planet name from save seed.
```bash
./namegen.py planet -s 0xC911CCCD7395E842
 #output:Nutsvill Sigma
```

Planet name from portal code and galaxy.
```bash
./namegen.py planet -p 1001ff218345 -g 4
#output:Edershar K25
```

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

Thanks to had of (had.sh)[https://had.sh/] and the (AGT)[https://www.nms-agt.com/] for supplying test data to enable the extension of the system name code and planet naming. 

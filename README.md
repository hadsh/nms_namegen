# NMS NAMEGEN

nms_namegen.py is a python program that generates names for 
regions and systems in the game No Man's Sky. 

It generates them in the same way that the game does.

You may use the modules included in the /nms_namegen folder in your own work or use the namegen.py as a command line utility. 

## Installation 
The project uses [Pipenv](https://pipenv.pypa.io/en/latest/)


## Usage 

*namegen.py command portal_code galaxy_id*

command is one of: *system*, *region* or *help* 

Portal code must be the 12 hexadecimal (0-F) digit portal code. For systems the first digit (planet id) is ignored, just set it to 0 if you want. For regions the first four digits are ignored (planet and system id)

The galaxy id is the galaxy number with Euclid starting at 0 and the last
galaxy being 255.

Example: 

>
> ./namegen.py system 03E9F3545C3E 0
> Abarof-Dulin
>

## Caveats 
As far as I can tell this generates the correct names for regions and 
systems. The system name generation has been tested on a corpus of ~600 system names
from AGT data. It differs only where a profanity filter has changed the system name.

## Development 
The code was written by Stuart Coyle. 

It is based on C Sharp code from [SystemNameCalculator](https://github.com/andraemon/SystemNameCalculator.git) by Andraemon.


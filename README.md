# tildaNICCC
ST-NICCC renderer for MicroPython on the EMF Camp "Tildagon" badge

## huh? how do I use this?
You'll need to know how to interact with the filesystem on your badge using `mpremote` - I won't go into specifics here.

Create a folder at `/apps/tildaNICCC/`, then copy everything from this repo into that folder. Please note that this demo will use approx. 720kb out of a 3mb flash chip, so you may fill up your badge in the process. If that happens, I don't know of the consequences, but it may involve needing to reflash the badge to erase the internal memory, including any downloaded apps.

Reboop your badge, then run tildaNICCC from the menu. Enjoy!

## Video
[here](https://youtu.be/GS-TlzXmO1E)

## Credit
Credits to Oxygene for the original demo (the data of which is replicated here), and to the EMF Camp badge team for the cool hardware to poke at!

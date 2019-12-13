# Curvatura
A FontForge plug-in to harmonize or tunnify or add inflection points to the selected parts. 
This is the successor to [harmonize-tunnify-inflection](https://github.com/linusromer/harmonize-tunnify-inflection).

## Prerequisites
On Linux you must have installed Python along with FontForge. 
On Windows FontForge embeds an own version of Python. 
Hence, you do not have to install Python additionaly. 
FontForge has to be at least the version from May, 26 2019. 

If you are on Ubuntu/Xubuntu/Kubuntu 18.04 you may consider a manual update:
```bash
sudo add-apt-repository ppa:fontforge/fontforge

sudo apt remove libgdraw5 libfontforge1 fontforge-common fontforge python-fontforge

sudo apt install libgdraw4=20190413-27-g1acfefa-0ubuntu1~bionic libfontforge1=20190413-27-g1acfefa-0ubuntu1~bionic fontforge-common=20190413-27-g1acfefa-0ubuntu1~bionic fontforge=20190413-27-g1acfefa-0ubuntu1~bionic python-fontforge=20190413-27-g1acfefa-0ubuntu1~bionic
```
If you are bound to an older version of FontForge, you may try 
[harmonize-tunnify-inflection](https://github.com/linusromer/harmonize-tunnify-inflection) instead, 
which should work with older versions of FontForge too.

## Installation
According to the documentation of FontForge you have to copy the file Curvatura.py to 
`$(PREFIX)/share/fontforge/python` or `~/.FontForge/python` but for me (on Ubuntu) it works at
`~/.config/fontforge/python` and for Windows it might be at
`C:\Users\[YOUR USERNAME HERE]\AppData\Roaming\FontForge\python`.

## New Tools Added By Curvatura
After installation, FontForge will show in the Tools menu 4 new entries: "Harmonize", "Harmonize (variant)" ,"Tunnify (balance)", "Add points of inflection". The first three tools are all some kind of smoothing the bezier curves. Their effects are visualized in the following image (you will not see the light blue curvature combs in FontForge, they have been added here for documentation reasons):

<img width="1227" alt="curvatura tools for cubic beziers" src="https://user-images.githubusercontent.com/11213578/70742200-48271780-1d1d-11ea-856f-9b00c33cb17b.png">

The last tool ("Add points of inflection") adds points of inflection (FontForge can natively display them but not natively add them):

<img width="520" alt="inflection-all" src="https://user-images.githubusercontent.com/11213578/70742783-9c7ec700-1d1e-11ea-8dcf-9d488496cebc.png">

### Curvatura Tools For Quadratic Bezier Splines
If you are working with quadratic bezier splines the tools "Tunnify (balance)" and "Add points of inflection" will have no effect, because quadratic bezier splines are already tunnified and point of inflections may only occur at the nodes of the splines. 
The "Harmonize" tool uses the same algorithm as for cubic bezier splines (but of course speed optimized). The "Harmonize (variant)" tool has the same effect as applying the "Harmonize (variant)" tools infinitely often.

<img width="680" alt="curvatura tools for quadratic beziers" src="https://user-images.githubusercontent.com/11213578/70742199-48271780-1d1d-11ea-98d1-95f92222635b.png">

## Comparison To harmonize-tunnify-inflection.py
* Due to a bug, earlier versions of FontForge could not use `fontforge.point.type`. Therefore, I have written a workaround in `harmonize-tunnify-inflection.py`. The workaround is way slower than just checking `fontforge.point.type`. `Curvatura.py` now uses the faster `fontforge.point.type`.
* `harmonize-tunnify-inflection.py` cannot handle quadratic bezier splines, whereas `Curvatura.py` can handle them.
* Some computations in `Curvatura.py` have been optimized in comparison to `harmonize-tunnify-inflection.py` (e.g. square roots are less frequently)
* The design of `Curvatura.py` allows the use as a FontForge plugin, as a python class and as a command line program. `harmonize-tunnify-inflection.py` only served as a FontForge plugin. `Curvatura.py` implements additionaly the computation of the curvature at time *t* of a bezier spline as a helping method.
* `harmonize-tunnify-inflection.py` had no sub menu. The menu entries of `Curvatura.py` are contained in a sub menu called "Curvatura". This makes the tools easier distinctable from tools of other suppliers. 

## Use `Curvatura.py` In Command Line
You can use `Curvatura.py` in the command line. It will harmonize all glyhps in a font and needs exactely 2 arguments:
```
python Curvatura.py input_font_file output_font_file
```
The input font file and output font file can be any file formats that FontForge understands (e.g. `*.sfd`, `*.otf`, `*.ttf`, `*.pfb`).

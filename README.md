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
which should work with older versions of FontForge too (but is not being developped anymore).

## Installation
According to the documentation of FontForge you have to copy the file Curvatura.py to 
`$(PREFIX)/share/fontforge/python` or `~/.FontForge/python` but for me (on Ubuntu) it works at
`~/.config/fontforge/python` and for Windows it might be at
`C:\Users\[YOUR USERNAME HERE]\AppData\Roaming\FontForge\python`.

If you want to use hotkeys as well, you can replace the `hotkeys` file in the parent directory
by the `hotkeys` file of this repository.

## New Tools Added By Curvatura
After installation, FontForge will show in the Tools menu 4 new entries: "Harmonize", "Make G3-continuous" ,"Tunnify (balance)" and "Add points of inflection". The first two tools are smoothing the curvature of the Bézier curves. 
Their effects are visualized in the following image (you will not see the light blue curvature combs in FontForge, 
they have been added here for documentation reasons):

<img width="800" alt="curvatura tools for cubic beziers" src="https://user-images.githubusercontent.com/11213578/83176179-51663e00-a11d-11ea-9f52-8f72907ab12d.png">

Note that "Harmonize" moves the node between its handles, whereas "Harmonize handles" scales the handles (see the [documention of the formulae](https://github.com/linusromer/curvatura/blob/master/curvatura-doc.pdf)). 

<img width="400" src="https://user-images.githubusercontent.com/11213578/83176392-a904a980-a11d-11ea-97ad-89021ed38aff.gif">
<img width="400" src="https://user-images.githubusercontent.com/11213578/83176431-ba4db600-a11d-11ea-8980-ea43499f32ae.gif">

<img width="400" src="https://user-images.githubusercontent.com/11213578/83176569-ee28db80-a11d-11ea-9dbc-71e55a1e1685.gif">
<img width="400" src="https://user-images.githubusercontent.com/11213578/83176571-ee28db80-a11d-11ea-9ccb-2dbb7601df70.gif">

"Tunnify (balance)" moves the handles of a cubic Bézier segment such that the line between the handles is parallel to the line between the nodes. This tool is advantageous if you are working with several masters, as it makes them more consistent.

<img width="400" src="https://user-images.githubusercontent.com/11213578/83176638-0f89c780-a11e-11ea-9c67-08f823c2cbe1.gif">
<img width="400" src="https://user-images.githubusercontent.com/11213578/83176642-10225e00-a11e-11ea-954d-eae34fdd9c95.gif">
<img width="400" src="https://user-images.githubusercontent.com/11213578/83176643-10225e00-a11e-11ea-9ca8-c6d8be1ea1ca.gif">
<img width="400" src="https://user-images.githubusercontent.com/11213578/83176823-64c5d900-a11e-11ea-91ed-7a889134f4a9.gif">
<img width="400" src="https://user-images.githubusercontent.com/11213578/83176824-64c5d900-a11e-11ea-9c11-8eae59c48cb5.gif">

The last tool ("Add points of inflection") adds points of inflection (FontForge can natively display them but not natively add them):

<img width="600" alt="inflection-all" src="https://user-images.githubusercontent.com/11213578/70742783-9c7ec700-1d1e-11ea-8dcf-9d488496cebc.png">

### Curvatura Tools For Quadratic Bezier Splines
If you are working with quadratic bezier splines the tools "Tunnify (balance)", "Add points of inflection" will have no effect, because quadratic bezier splines are already tunnified and point of inflections may only occur at the nodes of the splines. 
"Harmonize handles" does not have a meaning for quadratic Bézier splines and therefore do not affect paths, neither. 

The "Harmonize" tool uses a similar algorithm as for cubic Bézier splines (see the [documention of the formulae](https://github.com/linusromer/curvatura/blob/master/curvatura-doc.pdf)). As it is a iterated algorithm, results may change slightly if applied two times.

<img width="400" src="https://user-images.githubusercontent.com/11213578/83176822-642d4280-a11e-11ea-9b11-f8225ac24a37.gif">

## Comparison To harmonize-tunnify-inflection.py
* Due to a bug, earlier versions of FontForge could not use `fontforge.point.type`. Therefore, I have written a workaround in `harmonize-tunnify-inflection.py`. The workaround is way slower than just checking `fontforge.point.type`. `Curvatura.py` now uses the faster `fontforge.point.type`.
* `harmonize-tunnify-inflection.py` cannot handle quadratic bezier splines, whereas `Curvatura.py` can handle them.
* Some computations in `Curvatura.py` have been optimized in comparison to `harmonize-tunnify-inflection.py` (e.g. square roots are less frequently)
* The design of `Curvatura.py` allows the use as a FontForge plugin, as a python class and as a command line program. `harmonize-tunnify-inflection.py` only served as a FontForge plugin.
* `harmonize-tunnify-inflection.py` had no sub menu. The menu entries of `Curvatura.py` are contained in a sub menu called "Curvatura". This makes the tools easier distinctable from tools of other suppliers. 
* `Curvatura.py` implements the additional method "Harmonize handles".

## Use `Curvatura.py` In Command Line
You can use `Curvatura.py` in the command line. It will harmonize all glyhps in a font and needs exactely 2 arguments:
```
python Curvatura.py input_font_file output_font_file
```
The input font file and output font file can be any file formats that FontForge understands (e.g. `*.sfd`, `*.otf`, `*.ttf`, `*.pfb`).

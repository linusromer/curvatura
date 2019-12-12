# Curvatura
A FontForge plug-in to harmonize or tunnify or add inflection points to the selected parts. 

## Prerequisites
You must have installed Python along with FontForge. 

## Installation
According to the documentation of FontForge you have to copy the file Curvatura.py to 
`$(PREFIX)/share/fontforge/python` or `~/.FontForge/python` but for me (on Ubuntu) it works at
`~/.config/fontforge/python` and for Windows it might be at
`C:\Users\[YOUR USERNAME HERE]\AppData\Roaming\FontForge\python`.

## New Tools added by harmonize-tunnify-inflection
After installation, FontForge will show in the Tools menu 4 new entries: "Harmonize", "Harmonize (variant)" ,"Tunnify (balance)", "Add points of inflection". The first three tools are all some kind of smoothing the bezier curves. Their effects are visualized in the following image (you will not see the light blue curvature combs in FontForge, they have been added here for documentation reasons):

<img width="1227" alt="dots-all" src="https://user-images.githubusercontent.com/11213578/70742200-48271780-1d1d-11ea-856f-9b00c33cb17b.png">

The last tool ("Add points of inflection") adds points of inflection (FontForge can natively display them but not natively add them):

<img width="420" alt="inflection-all" src="https://user-images.githubusercontent.com/11213578/69477605-826d5b00-0de8-11ea-8baf-bf3b87c4c836.png">



<img width="500" alt="dots-all" src="https://user-images.githubusercontent.com/11213578/70742199-48271780-1d1d-11ea-98d1-95f92222635b.png">

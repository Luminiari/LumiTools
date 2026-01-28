# LumiTools
### Or: "Why don't I just automate most of this shit instead of waiting for other people to update their own tools?" 
<sub><Sup>(If you look carefully it's actually a solid collection of shitposts.) </Sup></sub><br />
<sub><Sup><sub><Sup>Formerly Random Blender Stuff</Sup></sub></Sup></sub>

I made a Blender addon yay.

Automates very specific repetitive tasks because I am very lazy and I know Python now. You get fancy buttons in your sidebar. You're welcome.

Works in Blender versions 3.6+, 4.x, and 5.x. Don't ask me why I still have 3.6 installed <sub><Sup>~~i am old and i am scared of change~~</Sup></sub>

## What it do
This was mostly made for making ports between bodies easier in FFXIV using Cordy's porting tool, and then using my own BG3 version of that to do the same thing until Volno made the objectively better Lazy Tailor but I'm actually even lazier and can't be bothered adding shapekeys for the other body mods like PST, TMTS, and SBBF so there you go.

### Magic Make Mod Button
Go ahead. Click it. See what happens (:

### Clean Merge (XIV)
Select your meshes and click. Performs the Merge (By Distance), Smooth (Beauty) and Triangulate functions in succession on all selected meshes. Useful if you use [Cordy's tool](https://docs.google.com/document/d/1GGzXbMy11xi_8uRIWGpG3Y-pXZTlt9z68rpdpMbiHCU) to ~~upscale~~ refit gear between bodies. <sub><Sup>If you call refitting meshes 'upscaling' I'm coming after you and taking a dump in every single one of your shoes.</Sup></sub>

### Morph Setup
1. Modifier Setup: Applies the Surface Deform and Smooth Corrective modifiers to the selected meshes and places them above any Armature modifiers. Does NOT bind anything.
2. Bind Surface Deform: Batch bind to a selected mesh. Use the eyedropper or type the target mesh directly into the Morph Target field.
3. Clean-Up: Applies the Surface Deform and Smooth Corrective modifiers on selected objects, and adds an Armature modifier if one doesn't exist. If you target an Armature as a target, it will assign it to the Armature modifier as well.

### Corrections
Flip weights by renaming anything with _L and _R. Made to work with FFXIV and BG3 rigs. Mostly BG3 because, again, lazy and I can't be bothered fixing the x-flip on export.

## How use thing
Install in Blender.👍`Edit` > `Preferences` > `Add-ons`.


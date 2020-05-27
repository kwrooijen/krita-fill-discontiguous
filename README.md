# Krita Fill Contiguous

A Krita plugin to replace a single color in one or multiple layers. This is is
useful for things such as pixel art, where you might want to change a color in
all layers.

## Usage

Your current foreground color will be replaced in any selected layers. You can
use the eyedropper tool to select a color to replace. Next click the `Replace
foreground` button, and choose a color as a replacement.

## Demo

![](assets/demo.gif)

## Caveats

### No native undo history

Currently there's no API to access the undo history. Which means when you apply
this plugins function you won't be able to use Krita's undo. Instead there's an
undo button in the Fill Contiguous docker.

### Accidentally merging colors

If you replace your foreground color with a color that already exists in your
piece, you won't be able to undo this change properly. This is because the
custom undo function reverses the color replacement. If the replacement color
was already there, it will be changed to the foreground color as well on
undo. 

![](assets/accidental-color-merge.gif)

## Todo
[ ] Create a custom fill tool. Currently we use the foreground color to decide
what to replace. Instead it would be nice to use the foreground color as the
replacement color, and have some kind of fill tool which will choose the color
to replace.

[ ] Replace in all keyframes. AFAIK keyframe API is very limited. It would be
nice to be able to use the fill tool on all keyframes

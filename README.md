# Macro Place Challenge 2026 

lightweight submission for the **Partcl / Hudson River Trading Macro Placement Challenge**.  

## Overview

The algorithm places hard macros onto rows ("shelves") across the chip canvas, with horizontal and vertical spreading to generate legal placements quickly.

## How It Optimises

Although lightweight, the solver includes several implicit optimisation strategies:

### Size-First Placement
Larger macros are placed first (sorted by height), reducing the chance of later fragmentation and improving packability.

### Alternating Row Direction
Rows alternate left-to-right and right-to-left placement. This reduces edge bias and creates a more balanced spatial distribution.

### Vertical Utilisation Scaling
After packing, all macro y-positions are scaled so the occupied region expands across the full canvas height. This lowers local density concentration.

### Horizontal Shelf Expansion
Each shelf is independently stretched to use the available width, increasing spacing between macros and improving overall spread, lowering density.

### Legalisation Margin
A small configurable gap is added to macro dimensions during placement. 






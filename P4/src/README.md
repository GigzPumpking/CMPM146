huminguy (Hung Nguyen)
esaltzhe (Elroy Saltzherr) 

Heuristic:
- In declare_methods, produce_wood actions were sorted from fastest to slowest (iron == stone < wooden < punching)
- Added two sets of state booleans (made_item, should_make_item) for each item in "Tools" in the data
- made_item ensures that tools are only made once
- should_make_item determines whether or not a tool should be made (for optimization)
    - Set in the beginning of the add_heuristic as well as in the heuristic
    - Calculates the number of wood and crafting time needed, if punching wood can obtain all necessary wood within the time limit, remove all axes from the pool.
    - If iron axes were not a part of the goals, never make an iron axe (same efficiency as stone axe, but more costly)
- Edge Case added to heuristic to stop it from making an iron_pickaxe in order to mine cobble to make a stone_pickaxe
    - Ideally, this would've been solved by a pickaxe heuristic, but we did not have enough time for this.
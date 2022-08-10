# Some Notes

Here we'll store comments which deserve to be written down, but aren't worth addressing now

- [ ] MealCollection (and other collections). I should be able to iterate over the collection directly without doing each for x in m.meals
    - Can this inherit from a general Collection class?
    - Should we be using a dataclass or some STL implementation of this?

- [ ] Replace any occurrences of /home/conor/Programming with project configuration / MEALPREP TOPDIR type construct

- [ ] In constructors, check that IDs are different everywhere. I.e. we should be making copies of data everywhere

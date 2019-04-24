# CodeHighp help

CodeHighp is an online judge system with contests and problems
focused on writing optimal code.

## Flavors

Each problem has a flavor, which dictates how the
problem is judged and what languages can be used.
Currently, following flavors are available:

 - [native](/help/flavors/native)

## Scoring

Most contests use standard scoring rules: each problem has
different groups of tests, the more you pass, the more primary points you'll have.
Secondary points are granted based on percentage of CPU time and memory usage
out of problem's limits. The more efficient your program is, the greater your
secondary score will be.

Scores for each problem in the contest are multiplied by each problem's weight
and added together. Participants are ordered by decreasing primary score,
and then by decreasing secondary score.

## Rating

Each participant who has participated in at least one rated contest
has rating, an integer, which shows how good they are in competing in contests.
Rating can only change by participating in rated contests (they are marked as
such on the contests page).

`RATING_TABLE`

This table is subject to change though, 
since I'm still testing this whole rating thing out.

## FAQ

### Seeing reports

If your solution successfully compiles and runs, you will be shown
your score. You can see detailed log by clicking on run ID.

### Why do I get `Accepted` result but no points?

`Accepted` result only implies that your solution compiles and runs.
If it doesn't produce correct output on the very first test, you'll get zero points
for it.

### I'd like to prepare a problem or contest

Great! Write an email about your ideas to `coordinator@codehighp.site` and
we'll grant your access to problem authoring interface.
Please include `[CodeHighp]` in title, so your email is not classified as spam.
Also, don't forget to specify your CodeHighp username.

### I'd like to host a private contest for educational purposes

Algorithm is the same as in the previous question.

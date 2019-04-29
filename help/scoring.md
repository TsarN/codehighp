# Scoring

Most contests use standard scoring rules: each problem has
different groups of tests, the more you pass, the more primary points you'll have.
Secondary points are granted based on percentage of CPU time and memory usage
out of problem's limits. The more efficient your program is, the greater your
secondary score will be.

Scores for each problem in the contest are multiplied by each problem's weight
and added together. Participants are ordered by decreasing primary score,
and then by decreasing secondary score.

Secondary score is calculated as fraction of time used out of problem's time limit
plus fraction of memory used out of problem's memory limit, all divided by 2.

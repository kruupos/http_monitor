# Improvements

## Major

 * First and foremost - testing every single function.

 * Using a circular buffer that read x BYTES at every cycle rather than `readline()`.
   It happen very often that `readline()` reach EOF before the line have been completly written, thus making corrupted data instead of missing data.
   
   In addition of that, I decided to await for 1sec for each corrupted data to be able to handle slower flow.
   But this compromise make me output a false hits/sec rate because it reads at most 4000requests per sec (on my machine)

 * Make more use of the data collected by `LogParser` because this is both a waste of CPU cycle and time. This is also the goal of this tool.

## Minor

 * Using a logging tools to catch error in the app, escpecially for the edge cases of the `LogParser`.

 * Create a temporary log file to remember the alert after a crash or a volontary SIGINT.

 * Improve the design of the interface to make it more user friendly and beautiful

 * Making a real use of `urwid` by allowing any user to change threshold real-time on the console.

 * Make another function to handle apache error log, thus having the possibility to monitor them both at the same time.
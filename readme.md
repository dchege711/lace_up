# Notes

* [Getting Started Guide](https://github.com/dchege711/lace_up/blob/master/getting_started.md)
* [Navigating and Contributing to the Code Base](https://github.com/dchege711/lace_up/blob/master/navigating_the_code_base.md)

## Usage Tips

* The browser usually caches files for faster performance, but inconveniences debugging. Following this [thread](https://stackoverflow.com/questions/41144565/flask-does-not-see-change-in-js-file) from Stack Overflow, hit `Cmd+Shift+R` for MacOS to force a hard refresh any time you change files and wish to see the changes in the browser immediately.

## Dear Santa, All I want for the master branch is...

:soon: Maintain a [session](https://www.owasp.org/index.php/Session_Management_Cheat_Sheet) once the user logs in or registers. This enables us to load other URLs e.g. `lace-up/account/` without requiring a second login.

:soon: Clicking on the logo shouldn't log the user out. Take them to `/lace-up/home/`. Clean up `/lace-up/`, the home URL. It currently shows stuff from Tiger Rides.

:soon: Allow users to edit games that they've already created `/lace-up/<GAME_ID>/`.

:soon: Allow users to create new events at `/lace-up/create/`. (Alex is working on this)

:soon: Filter and recommended games through the user's home feed at `/lace-up/home/`.

:soon: Prepare and deliver the user's stats.

:soon: Design the `/lace-up/home/`. Split the home page to show games on one half and stats on the other. Wire up links to relevant pages e.g. `/lace-up/account/`

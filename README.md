# Selenium racing
## Prerequisites
1. Python (something new, surely at least 3.5, but nothing before 3.11 has been tested)
2. `selenium`

## Running
1. Set `URL` in `main.py` to the live-timing webpage address (and optionally `US` to your car number)
2. `python racing/main.py <track-data-directory> [optional-last-seen-json]`
3. Wait till the live-timing webpage loads
4. Press `ENTER` in the terminal
5. ???
6. Profit

## Notes
1. It's made of wood, cardboard and duct tape - stuff might not work
2. Logs are kept in `selenium_racing.log`, which is never cleared automatically
3. Information about pit times will be saved to `last_seen.json`. You don't need it after race ends, just to preserve state after crashes
4. ...and it will crash for sure - once it does, just reset it
5. Before starting everything with the `ENTER`, it's better not to resize the window. However, after that resizing it so that the map is as large as possible is recommended

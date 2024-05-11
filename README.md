# Instagram Travel Posts Geolocator

## Description:
If you're looking to keep track of interesting places as you and your friends/family scroll Instagram, you can use this repository to geolocate them on a map.

It contains a Python script that extracts and geolocates place names from Instagram posts/reels captions which you have forwarded to a Telegram group.

_Since you can add other people to the Telegram group, making a Telegram group for everyone to forward Instagram posts/reels is a nice way of keeping track of all the places you want to visit._

## To set up the project:
1. Create a Telegram group to forward Instagram posts/reels to.
2. When you're ready to geolocate them, export (click the three dots on the top right of the Telegram chat window and click Export Chat History, selecting JSON format).
3. Then in `main.py` manually set the paths and keys. You will need [Anthropic](https://www.anthropic.com/api) and [Google Maps](https://developers.google.com/maps/documentation/geocoding/overview) API keys.
4. Run the script.

## Visualizing results:
I haven't included code to visualize results, and instead just use [Tableau Public](https://public.tableau.com/app/discover) (which is free) to quickly plot and chart results. 

If you also use Tableau, make sure to go into [Actions -> Go to URL](https://help.tableau.com/current/pro/desktop/en-us/actions_url.htm) so you can hyperlink the original Instagram posts.

Some other great easy charting/mapping platforms include [Google Data Studio](https://datastudio.google.com/), [Flourish Studio](https://flourish.studio/), [DataWrapper](https://www.datawrapper.de/).

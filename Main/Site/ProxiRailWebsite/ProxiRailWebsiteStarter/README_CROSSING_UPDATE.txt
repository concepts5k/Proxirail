PROXIRAIL CROSSING PAGE + FADE TRANSITION UPDATE

This continues the current prototype website and adds the changes discussed:

- The pedestrian is displayed from the front.
- The crossing demonstration has its own Flask page:
      http://127.0.0.1:5000/crossing-demo
- The home page now links to the separate demonstration.
- The train is shown from the front as it approaches.
- The camera uses an animated CSS beam.
- The yellow control must be held to move the train forward.
- At the end of the demonstration, the page slowly fades out and returns
  to the Welcome title.
- No external character or train image is required; the scene is built
  with HTML, CSS, and transformation rules.

FILES INCLUDED

app.py
templates/index.html
templates/intersection.html
templates/crossing_demo.html
static/styles.css
static/app.js
data/intersections.json

INSTALL

1. Stop Flask with Ctrl+C.

2. Extract this ZIP into:

   C:\Users\isense\Documents\ProxiRailWebsite\ProxiRailWebsiteStarter

3. Allow Windows to replace the existing files.

4. Restart:

   python app.py

5. Refresh the browser with:

   Ctrl+Shift+R

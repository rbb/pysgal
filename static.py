"""Variables for gallery.py."""

root = False
n_thumbs = 3              # number of thumbnails to display on index page

header = ("""<!doctype html>
<html>
<head>
  <title>%s</title>
  <meta charset="utf-8" />
  <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style type="text/css">
    body {
      background-color: %s;
      color: #839496;
      font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 0;
    }
    div {
      background-color: %s;
      border-radius: 0.25em;
      margin: 1em auto;
      padding: 2em;
      width: 90%%;
    }
    div.figure {
      align: center;
      //margin: 1em auto;
      margin: 0.1em;
      margin-bottom: 3em;
      padding: 2em;
      width: 100%%;
      padding: 0.1em;
      font-size: 60%%;
      //line-height: 60%%;
      //vertical-align: top;
      //color: #808080;
    }
    p {
      //font-size: medium;
      //padding-bottom: 1.5em;
    }
    a:link, a:visited {
      //color: #93a1a1;
      //font-size: 24px;
      text-decoration: underline;
    }
    img {
      padding: 0.1em;
      border-radius: 0.25em;
    }
    .module {
       float: left;
       width: 25%%;
       padding: 10px;
    }
    .clearfix::after {
       content: "";
       clear: both;
       display: table;
    }
    .container {
        overflow: auto;
    }
  </style>
</head>
<body>
<div>
""")


# Based off code from:
# https://css-tricks.com/snippets/css/css-grid-starter-layouts/
header_grid = ("""<!doctype html>
<html>
<head>
<title>%s</title>
<meta charset="utf-8" />
<meta http-equiv="Content-type" content="text/html; charset=utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style type="text/css">
body {
    background-color: %s;
    color: #839496;
    font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
    margin: 0 auto;
    max-width: 90%%; //56em;
    padding: 1em 0;
}
div {
    background-color: %s;
}
.header {
    display: flex;
    align-items: center;
    font-size: calc(16px + (26 - 16) * ((100vw - 300px) / (1600 - 300)));
    justify-content: center;
    //background: #000;
    color: #fff;
    //min-height: 10vh;
    text-align: center;
    margin: 0;
    padding: 0;
    border-width: 0;
}
.headsub {
    width: 25%%;
    max-width: 25%%;
    margin: 0;
    padding: 0;
    border-width: 0;
}
.grid {
    /* Grid Fallback */
    display: flex;
    flex-wrap: wrap;
    
    /* Supports Grid */
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250, 1fr));
    grid-auto-rows: minmax(250px, auto);
    grid-gap: 1em;
}

.figure {
  align: center;
  //margin: 1em auto;
  margin: 0.1em;
  margin-bottom: 3em;
  width: 100%%;
  padding: 0.1em;
  font-size: 60%%;
  //line-height: 60%%;
  //vertical-align: top;
  //color: #808080;
}

.module {
    /* Demo-Specific Styles */
    #background: #eaeaea;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 250px;
    
    /* Flex Fallback */
    margin-left: 5px;
    margin-right: 5px;
    flex: 1 1 250px;
}

/* If Grid is supported, remove the margin we set for the fallback */
@supports (display: grid) {
    .module {
        margin: 0;
    }
}
.container {
    overflow: auto;
    padding: 0.1em;
}
a:link, a:visited {
  //color: #93a1a1;
  //font-size: 24px;
  text-decoration: underline;
}
</style>
</head>
<body>
<div id=body>
""")


"""
    div.dir {
      //align: center;
      display: inline-block;
      margin: 1em auto;
      //margin-bottom: 3em;
      padding: 2em;
      //width: 100%%;
      padding: 0.1em;
      //font-size: 60%%;
      //line-height: 60%%;
      //vertical-align: top;
      //color: #808080;
    }
"""

br = '\n<br>'
footer = '\n</div></body></html>'
img_src = '\n<img src="%s">'
timestamp = '\n<p>This page was created on %s</p>'
#url_dir = '\n<p><a href="%s" target="_blank">%s</a></p>'
url_dir = '\n<a href="%s"><img title="%s" src="%s">%s</a><br>'
#url_img = '\n<a href="%s" target="_blank"><img title="%s" src="%s"></a>'
url_img = '\n<a href="%s"><img title="%s" src="%s" width="100%%"></a>'

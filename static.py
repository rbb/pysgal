"""Variables for gallery.py."""

root = False
n_thumbs = 3              # number of thumbnails to display on index page
min_size = 500,500        # minimum dimensions required to create thumbnail
thumb_size = 250,250      # dimensions of thumbnail to create

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
      margin: 1em auto;
      margin-bottom: 3em;
      padding: 2em;
      width: 100%%;
      padding: 0.1em;
      magin: 0.1em;
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
  </style>
</head>
<body>
<div>
""")

br = '\n<br>'
footer = '\n</div></body></html>'
img_src = '\n<img src="%s">'
timestamp = '\n<p>This page was created on %s</p>'
#url_dir = '\n<p><a href="%s" target="_blank">%s</a></p>'
url_dir = '\n<a href="%s"><img title="%s" src="%s">%s</a><br>'
#url_img = '\n<a href="%s" target="_blank"><img title="%s" src="%s"></a>'
url_img = '\n<a href="%s"><img title="%s" src="%s" width="100%%"></a>'

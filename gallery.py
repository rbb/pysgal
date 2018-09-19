#!/usr/bin/env python
# create a static HTML gallery

import datetime
import glob
import fnmatch
import os
import random
import re
import shutil
import sys
import time
import argparse
import PIL.ExifTags
import exifread

root = False

try:
    from PIL import Image
except ImportError:
    try:
        import Image
    except ImportError:
        print 'Requires Python Imaging Library. See README.'
        sys.exit(1)

def remove_thumbs_from_list(flist):
    """Remove all the "_thumb" filenames from a list"""
    mylist = list(flist)
    tstr = "_" +opts.thumb

    # Note: we can't remove(f) in the first for loop, because it messes up the
    # indexing of f, and we don't (always) get the proper results
    remove = []
    for f in mylist:
        if tstr in f.lower():
            remove.append(f)
    for f in remove:
        mylist.remove(f)
    return mylist

def random_image_from_dir(loc, d, remove_thumbs=True):
    """Returns path to random image from a given directory."""
    # TODO: pefer wide images over tall ones

    #if opts.verbose:
    #    print "random_image_from_dir: loc = " +str(loc)
    #    print "random_image_from_dir: d = " +str(d)
    #images = glob.glob(os.path.join(opts.dir, d, '*.[Jj][Pp][Gg]'))
    images = glob.glob(os.path.join(loc, d, '*.[Jj][Pp][Gg]'))
    if remove_thumbs:
        images = remove_thumbs_from_list(images)
    #if opts.verbose:
    #    print "random_image_from_dir: images = " +str(images)
    if images:
        image = random.choice(images)
        tail = image.replace(loc +'/', '')
        if opts.verbose:
            print "random_image_from_dir: image = " +str(image)
            print "random_image_from_dir: tail = " +str(tail)
    elif remove_thumbs:
        tail = random_image_from_dir(loc, d, False)
    else:
        tail = False

    return tail

def thumbnail(jpg):
    """Generates a thumbnail of an image."""

    thumb = ''
    try:
        im = Image.open(jpg)
        thumb = '%s_%s.%s' % (jpg.split('.')[0], opts.thumb, 'jpg')
        #im.thumbnail([opts.thumbsize, opts.thumbsize], Image.ANTIALIAS)
        im.thumbnail([opts.thumbsize, opts.thumbsize])
        im.save(thumb, 'JPEG')
    except IOError as e:
        print 'Problem with %s: %s, moving to %s' % (jpg, e, opts.tmp)
        try:
            shutil.move(jpg, opts.tmp)
        except shutil.Error:
            print 'Could not move %s' % jpg
            pass
    return thumb

def wr_exif_tag(fp, tags, tag, label='none'):
    #print "wr_exif_tag: tag = " + str(tag)
    #print "wr_exif_tag: label = " + str(label)
    if tag in tags:
        v = str(tags[tag])
        if 'nl' in label:
            fp.write('\n<br>' +v)
        elif 'none' in label:
            fp.write('    ' +v)
        else:
            fp.write('\n      <br>'+label +': ' +v)
        #print "wr_exif_tag: v = " +v

def wr_img(fp, name, loc):
    fp.write('\n   <div class=figure>')
    fp.write('\n      <a href="' +name +'"><img title="' +name +'" src="' +name
            +'" width="100%%"></a><b>' +name +'</b>')

    tags = {}
    if opts.verbose:
        print "name = " +name
    fimg = open(os.path.join(loc, name), 'rb')
    try :
        tags = exifread.process_file(fimg)
        wr_exif_tag(fp, tags, 'Image DateTime')
        wr_exif_tag(fp, tags, 'Image ImageDescription')
        #wr_exif_tag(fp, tags, 'EXIF ApertureValue', 'Aperture')
        fp.write('\n      <br>Exposure: f' +str(tags['EXIF FNumber']) +' at '
                +str(tags['EXIF ExposureTime']) +' sec, ISO '
                +str(tags['EXIF ISOSpeedRatings']) )
        wr_exif_tag(fp, tags, 'EXIF FocalLength', 'Focal Length')
        wr_exif_tag(fp, tags, 'EXIF Flash', 'Flash')
        #wr_exif_tag(fp, tags, 'EXIF ExposureMode')
        wr_exif_tag(fp, tags, 'Image Model', 'Model')

        fp.write('\n')
    except:
        print "Error collecting EXIF data from " +name
    #print "tags: " +str(tags)      # DEBUG

    fp.write('   </div>')

def wr_page(loc, flist, dlist):
    """Writes a gallery page for jpgs in path.

    Args:
    loc: str, name of page under root directory.
    flist: list of files in the dir. <src> tags are created for images.
    dlist: list of directories in the dir. Links are created for each dir
    """
    global root
    fout = os.path.join(loc, opts.index)

    # Calculate our relative directory depth, and how many '../' references we
    # need to get to where the folder.png and folder_up.png files are located.
    tail = loc.replace(root, '')
    depth = tail.count('/')
    if tail:
        depth += 1
    root_url = ''
    for n in range(depth):
        root_url += '../'

    if opts.verbose:
        print "wr_page: root = " +root
        print "wr_page: loc = " +loc
        print "wr_page: flist = " +str(flist)
        print "wr_page: dlist = " +str(dlist)
        print "wr_page: tail = " +str(tail)
        print "wr_page: depth = " +str(depth)
        print "wr_page: root_url = " +str(root_url)

    with open(fout, 'w') as index_file:
        index_file.write(header_grid(loc))
        index_file.write('\n<div id="nav" class=header>')
        if tail:
            index_file.write("<div class=headsub>Gallery: " +tail +"</div>\n")

        #------ Navigation
        if root_url:
            print "Generating div id=nav"
            image = root_url +opts.folder_image
            image_up = root_url +opts.folder_up_image

            index_file.write('\n   <div class=headsub>')
            index_file.write('\n   <a href="' +root_url +'">Home</a>')
            index_file.write('\n   </div>')
            index_file.write('\n   <div class=headsub>')
            index_file.write('\n   <a href="../">Up</a>')
            index_file.write('\n   </div>')
        index_file.write('\n</div>')

        #------ Directories
        if dlist:
            print "Generating div id=Albums"
            index_file.write('\n<div id="Albums" class=container>')
            for d in sorted(dlist):
                if opts.verbose:
                    print "wr_page: d = " +d
                thumbtxt = os.path.join(loc, d, opts.thumb_txt)
                thumbimg = False
                if os.path.exists(thumbtxt):
                    if opts.verbose:
                        print "      FOUND thumb.txt: " +thumbtxt
                    fthumbtxt = open(thumbtxt, 'rb')
                    thumbimg = fthumbtxt.readline().rstrip()
                    while '#' in thumbimg:
                        thumbimg = fthumbtxt.readline().rstrip()
                    if opts.verbose:
                        print "      thumbimg: " +thumbimg
                    thumbimg = os.path.join(loc, d, thumbimg)
                    if opts.verbose:
                        print "      thumbimg: " +thumbimg
                    if not os.path.exists(thumbimg):
                        thumbimg = False
                    elif not 'jpg' in thumbimg and not 'png' in thumbimg:
                        thumbimg = False
                    elif not opts.thumb in thumbimg:
                        # TODO Create the thumbnail file from the full size jpg
                        thumbimg = False
                    if opts.verbose:
                        print "      thumbimg: " +str(thumbimg)
                    fthumbtxt.close()

                if not thumbimg:
                    print loc
                    print d
                    rimg = random_image_from_dir(loc, d)
                    if rimg:
                        thumbimg = thumbnail( os.path.join(loc, rimg) )
                        #thumbimg = os.path.join(loc, rimg)
                        if opts.verbose:
                            print "      thumbimg from random: " +str(thumbimg)

                if not thumbimg:
                    thumbimg = opts.folder_image
                    if opts.verbose:
                        print "      thumbimg from folder_image: " +str(thumb)

                fullimg = thumbimg.replace('_'+opts.thumb, '')
                if thumbimg != opts.folder_image and not os.path.exists(thumbimg) and os.path.exists(fullimg):
                    print '      Creating thumbnail ' +thumbimg
                    thumb = thumbnail( fullimg )
                else:
                    thumb = thumbimg


                thumbtail = thumb.replace(loc, '')
                dir_thumb = d +'_'+opts.thumb+'.jpg'
                dst_thumb = os.path.join(loc, dir_thumb)
                copy_file(thumb, dst_thumb, opts.overwrite)
                index_file.write('\n   <div class=module>')
                index_file.write('\n   <a href="' +d +'"><img title="' +d +'" src="' +dir_thumb +'"><br>' +d +'</a>')
                #index_file.write('\n   <a href="' +d +'"><img title="' +d +'/' +opts.index +'" src="' +dir_thumb +'"><br>' +d +'</a>')
                index_file.write('\n   </div>')
            index_file.write('\n</div>\n')


        #------ Images
        if opts.folder_image in flist:
            flist.remove(opts.folder_image)
        if opts.folder_up_image in flist:
            flist.remove(opts.folder_up_image)
        flist = remove_thumbs_from_list(flist)

        if flist:
            index_file.write("<hr>\n")
            index_file.write('\n<div id="images" class=container>')
            for f in sorted(flist):
                if f.lower().endswith('.png') or f.lower().endswith('.jpg') or f.lower().endswith('.tiff'):
                    wr_img(index_file, f, loc)
                else:
                    if opts.verbose:
                        print "wr_page skipping non-image file " +loc +"/" +f
            index_file.write('\n</div>\n')


        t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        index_file.write('\n<p>This page was updated on ' +t +'</p>')
        index_file.write('\n</div></body></html>')


def copy_file(src, dst, overwrite=False):
    if (os.path.isfile(src) and not os.path.isfile(dst)) or (os.path.isfile(src) and overwrite):
        if opts.verbose:
            print "copy_file: " +src +" to " +dst
        shutil.copyfile(src, dst)

def process_dir(d):
    global root
    for dirName, subdirList, fileList in os.walk(d):
        if not root:
            root = dirName
        print('---------------------------------')
        print('Found directory: %s' % dirName)
        print('---------------------------------')
        if opts.cleanup:
            print('cleaning directory: %s' % dirName)
            print('---------------------------------')
            if fileList:
                for f in fileList:
                    if opts.thumb in f:
                        print "deleteing " +f
                        os.remove(os.path.join(dirName, f))
        wr_page(dirName, fileList, subdirList)

# Based off code from:
# https://css-tricks.com/snippets/css/css-grid-starter-layouts/
def header_grid (title):
    header = """<!doctype html>
<html>
<head>
<title>""" +title +"""</title>
<meta charset="utf-8" />
<meta http-equiv="Content-type" content="text/html; charset=utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style type="text/css">
body {
    background-color: """ +opts.bcolor +""";
    color: #839496;
    font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
    margin: 0 auto;
    max-width: 90%%; //56em;
    padding: 1em 0;
}
div {
    background-color: """ +opts.dcolor +""";
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
    margin-left: 0.5em;
    margin-right: 0.5em;
    margin-top: 0.1em;
    margin-bottom: 0.1em;
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
    display: inline-block;
    align-items: center;
    justify-content: center;
    //height: 250px;
    margin: 5px;
    margin-bottom: 10px;
    
    /* Flex Fallback */
    //margin-left: 5px;
    //margin-right: 5px;
    //margin-bottom: 5px;
    //flex: 1 1 250px;
}

/* If Grid is supported, remove the margin we set for the fallback */
@supports (display: grid) {
    .module {
        margin: 5px;
        margin-bottom: 10px;
    }
}
.container {
    overflow: auto;
    padding: 0.1em;
}
a:link {
  color: """ +opts.lcolor +""";
  text-decoration: underline;
}
a:visited {
  color: """ +opts.vcolor +""";
  text-decoration: underline;
}
</style>
</head>
<body>
<div id=body>
"""
    return header

def main():
    """Main function."""

    if opts.organize:
        OrganizeRoot()

    process_dir(opts.dir)

    # TODO: do we actually need to copy these?
    copy_file(opts.folder_image, os.path.join(opts.dir, opts.folder_image) )
    copy_file(opts.folder_up_image, os.path.join(opts.dir, opts.folder_up_image) )

    if opts.rsync:
        rsync_cmd ='rsync -avz -e "ssh" ' +opts.dir +" " +opts.rsync_dest
        print "Attempting '" +rsync_cmd +"'"
        os.system(rsync_cmd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process directory tree of jpgs to create a static webpage')
    parser.add_argument('-d', '--dir', dest='dir', default='www',
                        help='directory to search for jpgs [%(default)s]')
    parser.add_argument('-t', '--tmp', dest='tmp', default='/tmp',
                        help='temporary folder to move corrupt files to [%(default)s]')
    parser.add_argument('-i', '--index', dest='index', default='index.html',
                        help='filename for html files [%(default)s]')
    parser.add_argument('--bg-color', dest='bcolor', default='#101010',
                        metavar='C',
                        help='Background color for body div [%(default)s]')
    parser.add_argument('--div-bg-color', dest='dcolor', default='#202020',
                        metavar='C',
                        help='Background color for all other div blocks [%(default)s]')
    parser.add_argument('--link-color', dest='lcolor', default='#707070',
                        metavar='C',
                        help='link text color [%(default)s]')
    parser.add_argument('--visited-color', dest='vcolor', default='#404040',
                        metavar='C',
                        help='visited link text color [%(default)s]')
    parser.add_argument('--folder-image', dest='folder_image',
                        default='folder.png', metavar='F',
                        help='filename for folder image [%(default)s]')
    parser.add_argument('--thumb', dest='thumb', default='thumb',
                        help='text to append to base of image filename for thumbnails [%(default)s]')
    parser.add_argument('--thumbsize', dest='thumbsize', metavar='N', default=200,
                        help='thumbnail size [%(default)s]')
    parser.add_argument('--thumb-txt', dest='thumb_txt', default='thumb.txt',
                        metavar='F',
                        help='text file with name of thumbnail for directory [%(default)s].'
                        ' lines with "#" in them are considered comments.')
    parser.add_argument('--folder-up-image', dest='folder_up_image',
                        default='folder_up.png', metavar='F',
                        help='filename for folder image [%(default)s]')
    #parser.add_argument('-x', '--exclude', dest='exclude', nargs='+', default=[],
    #                    help='list of folders to exclude [%(default)s]')
    parser.add_argument('--organize', dest='organize', action='store_true',
                        default=False,
                        help='Create directories for jpgs, by date')
    parser.add_argument('-c', dest='cleanup', action='store_true',
                        default=False,
                        help='Clean up thumbnails (delete old ones)')
    parser.add_argument('-v', dest='verbose', action='store_true',
                        default=False,
                        help='print extra messages')
    parser.add_argument('-s', '--rsync', dest='rsync', action='store_true',
                        default=False,
                        help='Do an rync after done')
    parser.add_argument('-o', '--overwrite', dest='overwrite', action='store_true',
                        default=False,
                        help='overwrite thumbnails')
    parser.add_argument('--rsync-dest', dest='rsync_dest',
                        default='russandbecky.org:public_html/lr_gallery/',
                        help='destination for rsync [%(default)s]')

    opts = parser.parse_args()
    #opts.verbose=True                     # DEBUG for ipython
    #opts.overwrite=True                    # DEBUG for ipython
    #opts.dir='/Users/russell/Pictures/_gallery/'     # DEBUG for ipython
    #opts.dir='/var/www/html/gallery/'     # DEBUG for ipython
    #opts.dir='/Users/russell/Pictures/albums/'     # DEBUG for ipython

    main()

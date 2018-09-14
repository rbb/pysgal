#!/usr/bin/env python
# create a static HTML gallery

import datetime
import glob
import fnmatch
import os
import random
import re
import shutil
import static
import sys
import time
import argparse
#import exifread
import PIL.ExifTags


try:
    from PIL import Image
except ImportError:
    try:
        import Image
    except ImportError:
        print 'Requires Python Imaging Library. See README.'
        sys.exit(1)


def ListFiles(regex, path):
    """Returns list of matching files in path."""
    rule = re.compile(fnmatch.translate(regex), re.IGNORECASE)
    return [name for name in os.listdir(path) if rule.match(name)] or None


#def ListDirs(path):
#    """Returns list of directories in path."""
#    return [d for d in os.listdir(path) if os.path.isdir(
#        os.path.join(path, d))]


def Now(time=True):
    """Returns formatted current time."""
    if time:
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        return datetime.datetime.now().strftime('%Y%m%d')

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

def random_image_from_dir(loc, d):
    """Returns path to random image from a given directory."""
    #if opts.verbose:
    #    print "random_image_from_dir: loc = " +str(loc)
    #    print "random_image_from_dir: d = " +str(d)
    #images = glob.glob(os.path.join(opts.dir, d, '*.[Jj][Pp][Gg]'))
    images = glob.glob(os.path.join(loc, d, '*.[Jj][Pp][Gg]'))
    images = remove_thumbs_from_list(images)
    #if opts.verbose:
    #    print "random_image_from_dir: images = " +str(images)
    if images:
        image = random.choice(images)
        tail = image.replace(loc +'/', '')
        if opts.verbose:
            print "random_image_from_dir: image = " +str(image)
            print "random_image_from_dir: tail = " +str(tail)
    else:
        tail = False
    return tail


def OrganizeRoot():
    """Creates directories for images in root directory."""
    try:
        os.chdir(opts.dir)
    except OSError:
        print 'Could not cd into %s' % opts.dir
        sys.exit(1)

    fs = ListFiles('*.jpg', '.')
    if fs:
        for jpg in fs:
            datehour = Now(time=False)
            if not os.path.exists(datehour):
                print 'Creating directory: %s' % datehour
                os.makedirs(datehour)
            if not os.path.exists(os.path.join(datehour, jpg)):
                shutil.move(jpg, datehour)
            else:
                print '%s already exists' % os.path.join(datehour, jpg)


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
    #fp.write('\n      <img title="' +name +'" src="' +name +'" width="100%"></a>')

    # Open image file for reading (binary mode)
    #f = open(os.path.join(loc, name), 'rb')
    # Return Exif tags
    #tags = exifread.process_file(f)
    #print "tags: " +str(tags)

    tags = {}
    if opts.verbose:
        print "name = " +name
    fimg = PIL.Image.open(os.path.join(loc, name))
    try :
        for k, v in fimg._getexif().items():
            if k in PIL.ExifTags.TAGS:
                key = PIL.ExifTags.TAGS[k]
                #if 'MakerNote' not in key:
                #    print str(key) +' = ' +str(v)
                #print "key = " +str(key)
                #print "k = " +str(k)
                #print "v = " +str(v)
                tags[key] = v
        #fp.write('\n      <div class=figure>' +name )
        wr_exif_tag(fp, tags, 'DateTime')
        #wr_exif_tag(fp, tags, 'DateTimeOriginal')
        wr_exif_tag(fp, tags, 'ExposureTime', 'Exposure')
        wr_exif_tag(fp, tags, 'FNumber', 'F Number')
        wr_exif_tag(fp, tags, 'FocalLength', 'Focal Length')
        wr_exif_tag(fp, tags, 'ISOSpeedRatings', 'ISO')
        #wr_exif_tag(fp, tags, 'Make')
        wr_exif_tag(fp, tags, 'Model', 'nl')
        #fp.write('\n      </div>')
        fp.write('\n')
    except:
        print "Error collecting EXIF data from " +name
    #print "tags: " +str(tags)
    fp.write('   </div>')

def wr_dir(fp, d, root_url, image=''):
    if not image:
        image = root_url +opts.folder_image
    fp.write('\n   <br><a href="' +d +'"><img title="' +d +'" src="' +image +'">' +d +'</a><br>')

def WriteGalleryPage(loc, flist, dlist):
    """Writes a gallery page for jpgs in path.

    Args:
    loc: str, name of page under root directory.
    flist: list of files in the dir. <src> tags are created for images.
    dlist: list of directories in the dir. Links are created for each dir
    """
    fout = os.path.join(loc, opts.index)

    # Calculate our relative directory depth, and how many '../' references we
    # need to get to where the folder.png and folder_up.png files are located.
    tail = loc.replace(static.root, '')
    depth = tail.count('/')
    if tail:
        depth += 1
    root_url = ''
    for n in range(depth):
        root_url += '../'

    if opts.verbose:
        print "WriteGalleryPage: loc = " +loc
        print "WriteGalleryPage: flist = " +str(flist)
        print "WriteGalleryPage: dlist = " +str(dlist)
        print "WriteGalleryPage: root = " +str(static.root)
        print "WriteGalleryPage: tail = " +str(tail)
        print "WriteGalleryPage: depth = " +str(depth)
        print "WriteGalleryPage: root_url = " +str(root_url)

    with open(fout, 'w') as index_file:
        index_file.write(static.header_grid %
            (loc, opts.bcolor, opts.dcolor))
        if tail:
            index_file.write("<p>" +tail +"</p>\n")

        #------ Navigation
        index_file.write('\n<div id="nav" class=container>')
        if root_url:
            image = root_url +opts.folder_image
            image_up = root_url +opts.folder_up_image
            """
            index_file.write('\n<div id="nav">')
            index_file.write('\n   <table width="100%"><tr>')
            #index_file.write('\n   <a href="' +root_url +'"><img title="root" src="' +image +'">Home</a><br>')
            index_file.write('\n      <td><a href="' +root_url +'">Home</a></td>')
            #index_file.write('\n   <a href="../"><img title="up" src="' +image_up +'">Up</a><br>')
            index_file.write('\n      <td><a href="../">Up</a></td>')
            index_file.write('\n   </tr></table">')
            #index_file.write('\n</div>')
            """

            index_file.write('\n   <div class=module>')
            index_file.write('\n   <a href="' +root_url +'">Home</a>')
            index_file.write('\n   <a href="../">Up</a>')
            index_file.write('\n   </div>')
            index_file.write('\n</div>')

        #------ Directories
        if dlist:
            index_file.write('\n<div id="Albums" class=container>')
            for d in dlist:
                if opts.verbose:
                    print "WriteGalleryPage: d = " +d
                rimage = random_image_from_dir(loc, d)
                if rimage:
                    thumb = thumbnail( os.path.join(loc, rimage) )
                else:
                    thumb = opts.folder_image

                thumbtail = thumb.replace(loc, '')
                dir_thumb = d +'_'+opts.thumb+'.jpg'
                copy_file(thumb, os.path.join(loc, dir_thumb))
                #wr_dir(index_file, d, root_url, dir_thumb)
                index_file.write('\n   <div class=module>')
                index_file.write('\n   <a href="' +d +'"><img title="' +d +'" src="' +dir_thumb +'"><br>' +d +'</a>')
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
            for f in flist:
                if f.lower().endswith('.png') or f.lower().endswith('.jpg') or f.lower().endswith('.tiff'):
                    wr_img(index_file, f, loc)
                #else:
                #    print "WriteGalleryPage skipping " +loc +"/" +f
            index_file.write('\n</div>\n')


        index_file.write(static.timestamp % Now())
        index_file.write(static.footer)


def copy_file(src, dst):
    if os.path.isfile(src) and not os.path.isfile(dst):
        if opts.verbose:
            print "copy_file: " +src +" to " +dst
        shutil.copyfile(src, dst)

def process_dir(d):
    for dirName, subdirList, fileList in os.walk(d):
        if not static.root:
            static.root = dirName
        print('---------------------------------')
        print('Found directory: %s' % dirName)
        print('---------------------------------')
        WriteGalleryPage(dirName, fileList, subdirList)


def main():
    """Main function."""


    if opts.organize:
        OrganizeRoot()

    process_dir(opts.dir)
    #WriteGalleryPages()
    #if file.endswith('.tgz') and not file.startswith('.'):
    #WriteIndex()
    copy_file(opts.folder_image, os.path.join(opts.dir, opts.folder_image) )
    copy_file(opts.folder_up_image, os.path.join(opts.dir, opts.folder_up_image) )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process directory tree of jpgs to create a static webpage')
    parser.add_argument('-d', '--dir', dest='dir', default='www',
                        help='directory to search for jpgs [%(default)s]')
    parser.add_argument('-t', '--tmp', dest='tmp', default='/tmp',
                        help='temporary folder to move corrupt files to [%(default)s]')
    parser.add_argument('-i', '--index', dest='index', default='index.html',
                        help='filename for html files [%(default)s]')
    parser.add_argument('--background-color', dest='bcolor', default='#202020',
                        help='Background color [%(default)s]')
    parser.add_argument('--div-background-color', dest='dcolor', default='#2b2b2b',
                        help='Background color [%(default)s]')
    parser.add_argument('--folder-image', dest='folder_image',
                        default='folder.png',
                        help='filename for folder image [%(default)s]')
    parser.add_argument('--thumb', dest='thumb', default='thumb',
                        help='text to append to base of image filename for thumbnails [%(default)s]')
    parser.add_argument('--thumbsize', dest='thumbsize', metavar='N', default=100,
                        help='thumbnail size [%(default)s]')
    parser.add_argument('--folder-up-image', dest='folder_up_image',
                        default='folder_up.png',
                        help='filename for folder image [%(default)s]')
    #parser.add_argument('-x', '--exclude', dest='exclude', nargs='+', default=[],
    #                    help='list of folders to exclude [%(default)s]')
    parser.add_argument('--organize', dest='organize', action='store_true',
                        default=False,
                        help='Create directories for jpgs, by date')
    parser.add_argument('-v', dest='verbose', action='store_true',
                        default=False,
                        help='print extra messages')
    # TODO: add rsync option to implement:
    # rsync -avz -e "ssh" . russandbecky.org:public_html/lr_gallery/

    opts = parser.parse_args()
    #opts.verbose=True                     # DEBUG for ipython
    #opts.dir='/var/www/html/gallery/'     # DEBUG for ipython

    main()

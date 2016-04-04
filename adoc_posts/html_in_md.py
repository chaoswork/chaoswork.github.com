#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

def main():
    """make a markdown file to wrap the html file.
    :returns: 

    """
    if len(sys.argv) < 2:
        print "Usage: html_in_md.py origin_name"
        sys.exit(1)
    html_file = sys.argv[1]
    if not html_file.endswith(".html"):
        print "the input file must be a html file"
        sys.exit(1)
    origin_name = '.'.join((html_file.strip().split('.')[:-1]))
    filename = origin_name.split('/')[-1]
    date = '-'.join((filename.strip().split('-')[:3]))

    # get title
    title = ""
    with open(origin_name + '.adoc') as f:
        for line in f:
            if line.startswith('= '):
                title = line[2:]
                break
    md_file = "../_posts/%s.md" % (filename)
    fout = open(md_file,'w')
    fout.write("---\n")
    fout.write("author: Chao Huang\n")
    fout.write("date: %s\n" % (date))
    fout.write("title: %s\n" % (title))
    fout.write("layout: post\n")
    fout.write("---\n")
    fout.write("{%% include adoc_posts/%s %%}" % (filename + ".html"))
    fout.close()



if __name__ == "__main__":
    main()
#!/usr/bin/env python
# Forked from https://github.com/johnz2/markdown-to-google-sites

from __future__ import print_function
import argparse
#import logging
import sys

import markdown
from markdown.util import etree


def eprint(*args, **kwargs):
    """ Print an error to stderr; behaves like print() """
    print(*args, file=sys.__stderr__, **kwargs)


class ReplaceCodeBlocksTreeprocessor(markdown.treeprocessors.Treeprocessor):
    """ Replace <pre><code> blocks with additional HTML to help Google Sites
        apply its "Blockquote Code" style." """
    def run(self, root):
        self.replace_code_blocks(root)
        return root

    @staticmethod
    def replace_code_blocks(element):
        """ Given a Markdown root tree, wrap all the code blocks with GSites's
        code styling class """
        blocks = element.getiterator('pre')
        for block in blocks:
            children = block.getchildren()
            if len(children) == 1 and children[0].tag == 'code':
                code_element = children[0]
                block.remove(children[0])
                div = etree.SubElement(block, "div")
                div.set("class", "sites-codeblock sites-codesnippet-block")
                div.append(code_element)


class GoogleSitesExtension(markdown.Extension):
    """ Markdown extension to Google Sites-ify certain syntax. """
    def __init__(self, *args, **configs):
        # define default configs
        self.config = {'replace_code_blocks' : [True, "Format code blocks for Google Sites"]}
        super(GoogleSitesExtension, self).__init__(*args, **configs)

    def extendMarkdown(self, md, md_globals):
        # Insert a tree-processor that adds the configured CSS class to P tags
        if self.getConfig('replace_code_blocks'):
            replace_code_blocks = ReplaceCodeBlocksTreeprocessor(md)
            md.treeprocessors.add('replace_code_blocks', replace_code_blocks, '_end')


def markdown_to_google_site(text):
    """ Given Markdown, convert it to GSites HTML """
    do_conversion = False if OPTS.debug else True
    googlesites_ext = GoogleSitesExtension(replace_code_blocks=do_conversion)
    return markdown.markdown(text, extensions=[googlesites_ext])


def read_file(filename):
    """ Reads in a file, or stdin if None """
    if filename is None:
        return sys.stdin.read()
    else:
        try:
            input_file = open(filename, mode='r')
            return input_file.read()
        except (IOError, OSError) as output:
            exit("Couldn't open file: {0}".format(output))
        finally:
            input_file.close()


def write_file(filename, contents):
    """ (TODO: Writes out a file, or) prints to stdout if filename is None """
    if filename is None:
        print(contents)


if __name__ == "__main__":
    ARGP = argparse.ArgumentParser(
        description='Convert Markdown to Google Sites-flavored HTML')
    ARGP.add_argument(
        'file', type=str, nargs='?', help='File to read, defaults to stdin')
    ARGP.add_argument(
        '-o', '--outfile', type=str, help='File to write to (default: stdout)')
    #ARGP.add_argument(
    #    '-v', '--verbose', action='store_true', help='Be verbose')
    ARGP.add_argument(
        '-d', '--debug', action='store_true', help='Here be dragons')
    OPTS = ARGP.parse_args()

    #LOG = logging.getLogger()
    #LOG.setLevel(logging.INFO if OPTS.verbose else logging.WARNING)
    #LOG.info(OPTS)
    #LOG.info(LOG.getEffectiveLevel())

    write_file(OPTS.outfile, (markdown_to_google_site(read_file(OPTS.file))))

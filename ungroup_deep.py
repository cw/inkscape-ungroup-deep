#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
http://tutorials.jenkov.com/svg/g-element.html

see #inkscape.html and
https://github.com/nikitakit/svg2sif/blob/master/synfig_prepare.py#L370
for an exmaple how to do the transform of parent to children.
"""

from __future__ import division, print_function
import logging
logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
    level=logging.DEBUG)

try:
    import inkex
    #from inkex import unittouu
except ImportError:
    raise ImportError("""No module named inkex in {0}.""".format(__file__))
from ungroup_utils import propagate_attribs

SVG_NS = "http://www.w3.org/2000/svg"
INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"


class Ungroup(inkex.Effect):
    def _ungroup(self, obj):
        if (obj.tag == inkex.addNS('g', 'svg')):
            propagate_attribs(obj)
            logging.debug("group element = %s, id = %s", obj, obj.attrib["id"])
            children = list(obj)
            obj_parent = obj.getparent()
            obj_index = list(obj_parent).index(obj)
            obj_parent.replace(obj, children[0])
            for child in reversed(children[1:]):
                obj_parent.insert(obj_index, child)

            for elem in children:
                self._ungroup(elem)

        else:
            logging.debug("non-group element = %s", obj)

    def effect(self):
        if len(self.selected):
            for elem in self.selected.itervalues():
                self._ungroup(elem)
        else:
            for elem in self.document.getroot():
                self._ungroup(elem)

if __name__ == '__main__':
    effect = Ungroup()
    effect.affect()

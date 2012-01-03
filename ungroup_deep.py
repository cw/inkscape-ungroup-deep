#!/usr/bin/python

"""
http://tutorials.jenkov.com/svg/g-element.html

"""

from __future__ import division, print_function
import sys

# INKEX MODULE
# If you get the "No module named inkex" error, uncomment the relevant line
# below by removing the '#' at the start of the line.
#
#sys.path += ['/usr/share/inkscape/extensions']                     # If you're using a standard Linux installation
#sys.path += ['/usr/local/share/inkscape/extensions']               # If you're using a custom Linux installation
#sys.path += ['C:\\Program Files\\Inkscape\\share\\extensions']     # If you're using a standard Windows installation

SVG_NS = "http://www.w3.org/2000/svg"
INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"

try:
    import inkex
    from inkex import unittouu
except ImportError:
    raise ImportError("""No module named inkex.
Please edit the file {0} and see the section titled 'INKEX MODULE'""".format(__file__))

class Ungroup(inkex.Effect):
    def _ungroup(self, obj):
        print("obj.tag = {0}".format(obj.tag), file=sys.stderr)
        if (obj.tag == inkex.addNS('g', 'svg')):
            print("Found group tag: {0}".format(obj.tag), file=sys.stderr)
            children = list(obj)
            obj_parent = obj.getparent()
            obj_index = list(obj_parent).index(obj)
            list(obj_parent)[obj_index] = children
            for elem in children:
                self._ungroup(elem)
        else:
            print("Found other tag: {0}".format(obj.tag), file=sys.stderr)

    def effect(self):
        if len(self.selected):
            for id, elem in self.selected.iteritems():
                self._ungroup(elem)
        else:
            for elem in self.document.getroot():
                self._ungroup(elem)

if __name__ == '__main__':
    effect = Ungroup()
    effect.affect()

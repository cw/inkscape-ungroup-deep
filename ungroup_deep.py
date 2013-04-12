#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
see #inkscape on Freenode and
https://github.com/nikitakit/svg2sif/blob/master/synfig_prepare.py#L370
for an example how to do the transform of parent to children.
"""

__version__ = "0.1"  # Works but in terms of maturity, still unsure

from inkex import addNS
import logging
import simplestyle
import simpletransform
logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
    level=logging.INFO)

try:
    import inkex
except ImportError:
    raise ImportError("""No module named inkex in {0}.""".format(__file__))

SVG_NS = "http://www.w3.org/2000/svg"
INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"


class Ungroup(inkex.Effect):

    def _get_dimension(s="1024"):
        """Convert an SVG length string from arbitrary units to pixels"""
        if s == "":
            return 0
        try:
            last = int(s[-1])
        except:
            last = None
    
        if type(last) == int:
            return float(s)
        elif s[-1] == "%":
            return 1024
        elif s[-2:] == "px":
            return float(s[:-2])
        elif s[-2:] == "pt":
            return float(s[:-2]) * 1.25
        elif s[-2:] == "em":
            return float(s[:-2]) * 16
        elif s[-2:] == "mm":
            return float(s[:-2]) * 3.54
        elif s[-2:] == "pc":
            return float(s[:-2]) * 15
        elif s[-2:] == "cm":
            return float(s[:-2]) * 35.43
        elif s[-2:] == "in":
            return float(s[:-2]) * 90
        else:
            return 1024

    def _ungroup(self, node):
        """Propagate style and transform to remove inheritance
        Originally from
        https://github.com/nikitakit/svg2sif/blob/master/synfig_prepare.py#L370
        """
    
        # using iteration instead of recursion to avoid hitting Python
        # max recursion depth limits, which is a problem in converted PDFs

        # Start the queue with empty inherited style and transform.
        q = [(node, {}, [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])]
    
        while q:
            current = q.pop()
            node = current[0]
            parent_style = current[1]
            parent_transform = current[2]
    
	    # Don't enter non-graphical portions of the document
	    if (node.tag == addNS("namedview", "sodipodi")
	        or node.tag == addNS("defs", "svg")
	        or node.tag == addNS("metadata", "svg")
	        or node.tag == addNS("foreignObject", "svg")):
	        continue
    
	    # Compose the transformations
	    if node.tag == addNS("svg", "svg") and node.get("viewBox"):
	        vx, vy, vw, vh = [_get_dimension(x)
		    for x in node.get("viewBox").split()]
	        dw = _get_dimension(node.get("width", vw))
	        dh = _get_dimension(node.get("height", vh))
	        t = "translate(%f, %f) scale(%f, %f)" % (-vx, -vy, dw / vw, dh / vh)
	        this_transform = simpletransform.parseTransform(t, parent_transform)
	        this_transform = simpletransform.parseTransform(node.get("transform"),
		    this_transform)
	        del node.attrib["viewBox"]
	    else:
	        this_transform = simpletransform.parseTransform(node.get("transform"),
		    parent_transform)
    
	    # Compose the style attribs
	    this_style = simplestyle.parseStyle(node.get("style", ""))
	    remaining_style = {}  # Style attributes that are not propagated
    
	    non_propagated = ["filter"]  # Filters should remain on the top ancestor
	    for key in non_propagated:
	        if key in this_style.keys():
		    remaining_style[key] = this_style[key]
		    del this_style[key]
    
	    # Create a copy of the parent style, and merge this style into it
	    parent_style_copy = parent_style.copy()
	    parent_style_copy.update(this_style)
	    this_style = parent_style_copy
    
	    # Merge in any attributes outside of the style
	    style_attribs = ["fill", "stroke"]
	    for attrib in style_attribs:
	        if node.get(attrib):
		    this_style[attrib] = node.get(attrib)
		    del node.attrib[attrib]
    
	    if (node.tag == addNS("svg", "svg")
	        or node.tag == addNS("g", "svg")
	        or node.tag == addNS("a", "svg")
	        or node.tag == addNS("switch", "svg")):
	        # Leave only non-propagating style attributes
	        if len(remaining_style) == 0:
		    if "style" in node.keys():
		        del node.attrib["style"]
	        else:
		    node.set("style", simplestyle.formatStyle(remaining_style))
    
	        # Remove the transform attribute
	        if "transform" in node.keys():
		    del node.attrib["transform"]
    
	        # Queue any subelements for propagation
	        for c in node.iterchildren():
		    q.append((c, this_style, this_transform))
    
                # Flatten grouping if this is a group element
                # and remove leftover empty group
                # N.B. Do this last, as it destroys the parent/child relation.
                if (node.tag == inkex.addNS('g', 'svg')):
                    logging.debug("group element = %s, id = %s", node, node.attrib["id"])
                    node_parent = node.getparent()
                    node_index = list(node_parent).index(node)
	            for c in node.iterchildren():
                        node_parent.insert(node_index, c)
                    node_parent.remove(node)
                else:
                    logging.debug("non-group element = %s", node)

	    else:
	        # This element is not a container
    
	        # Merge remaining_style into this_style
	        this_style.update(remaining_style)
    
	        # Set the element's style and transform attribs
	        node.set("style", simplestyle.formatStyle(this_style))
	        node.set("transform", simpletransform.formatTransform(this_transform))

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

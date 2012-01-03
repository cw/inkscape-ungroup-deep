# -*- coding: utf-8 -*-
from inkex import addNS
import simplestyle
import simpletransform


def get_dimension(s="1024"):
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


def propagate_attribs(node, parent_style={},
        parent_transform=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]):
    """Propagate style and transform to remove inheritance
    Originally from
    https://github.com/nikitakit/svg2sif/blob/master/synfig_prepare.py#L370
    """

    # Don't enter non-graphical portions of the document
    if (node.tag == addNS("namedview", "sodipodi")
        or node.tag == addNS("defs", "svg")
        or node.tag == addNS("metadata", "svg")
        or node.tag == addNS("foreignObject", "svg")):
        return

    # Compose the transformations
    if node.tag == addNS("svg", "svg") and node.get("viewBox"):
        vx, vy, vw, vh = [get_dimension(x)
            for x in node.get("viewBox").split()]
        dw = get_dimension(node.get("width", vw))
        dh = get_dimension(node.get("height", vh))
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

        # Continue propagating on subelements
        for c in node.iterchildren():
            propagate_attribs(c, this_style, this_transform)
    else:
        # This element is not a container

        # Merge remaining_style into this_style
        this_style.update(remaining_style)

        # Set the element's style and transform attribs
        node.set("style", simplestyle.formatStyle(this_style))
        node.set("transform", simpletransform.formatTransform(this_transform))

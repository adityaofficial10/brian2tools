import re

from brian2.units.allunits import all_units


name_to_unit = {u.dispname: u for u in all_units}


def from_string(rep):
    """
    Returns `Quantity` object from text representation of a value.

    Parameters
    ----------
    rep : `str`
        text representation of a value with unit

    Returns
    -------
    q : `Quantity`
        Brian Quantity object
    """
    # match value
    m = re.match('-?[0-9]+\.?([0-9]+)?[eE]?-?([0-9]+)?', rep)
    if m:
        value = rep[0:m.end()]
        rep = rep[m.end():]
    else:
        raise ValueError("Empty value given")
    # match unit
    m = re.match(' ?([a-zA-Z]+)', rep)
    unit = None
    per = None
    if m:
        unit = rep[0:m.end()].strip()
        # special case with per
        if unit == 'per':
            mper = re.match(' ?per_([a-zA-Z]+)', rep)
            per = rep[0:mper.end()].strip()[4:]
            m = mper
        rep = rep[m.end():]
    # match exponent
    m = re.match('-?([0-9]+)?', rep)
    exponent = None
    if len(rep) > 0 and m:
        exponent = rep[0:m.end()]
    if unit:
        if per:
            b2unit = 1. / name_to_unit[per]
        else:
            b2unit = name_to_unit[unit]
        if value and exponent:
            return float(value) * b2unit**float(exponent)
        elif value:
            return float(value) * b2unit
    else:
        return float(value)


def string_to_quantity(rep):
    """
        Returns `Quantity` object from text representation of a value.

        Parameters
        ----------
        rep : `str`
            text representation of a value with unit

        Returns
        -------
        q : `Quantity`
            Brian Quantity object
    """
    if len(rep.split("_per_")) < 2:
        post = None
        pre = rep
    else:
        pre, post = rep.split("_per_")

    m = re.match('-?[0-9]+\.?([0-9]+)?[eE]?-?([0-9]+)?', pre)
    if m:
        value = pre[0:m.end()]
        pre = pre[m.end():]
    numerator = None
    deno = None

    for u in pre.strip().split("_"):
        m = re.search(r'\d+$', u)
        if m:
            u = u[:m.start()] + '^' + u[m.start():]
        numerator = name_to_unit[u] if numerator is None else numerator * \
                                                              name_to_unit[u]

    if post is not None:
        for u in post.strip().split("_"):
            m = re.search(r'\d+$', u)
            if m:
                u = u[:m.start()] + '^' + u[m.start():]
            deno = name_to_unit[u] if deno is None else deno * name_to_unit[u]
        return float(value) * (numerator / deno)
    return float(value) * numerator

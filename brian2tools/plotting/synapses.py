"""
Module to plot synaptic connections.
"""
from collections import Counter

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable

__all__ = ['plot_synapses']


def plot_synapses(sources, targets, values=None, var_unit=None,
                  var_name=None, axes=None, **kwds):
    '''
    Parameters
    ----------
    sources : `~numpy.ndarray` of int
        The source indices of the connections (as returned by
        ``Synapses.i``).
    targets : `~numpy.ndarray` of int
        The target indices of the connections (as returned by
        ``Synapses.j``).
    values : `~brian2.units.fundamentalunits.Quantity`, `~numpy.ndarray`
        The values to plot, a 1D array of the same size as ``sources`` and
        ``targets``.
    var_unit : `~brian2.units.fundamentalunits.Unit`, optional
        The unit to use to plot the ``values`` (e.g. ``mV`` for a membrane
        potential). If none is given (the default), an attempt is made to
        find a good scale automatically based on the ``values``.
    var_name : str, optional
        The name of the variable that is plotted. Used for the axis label.
    axes : `~matplotlib.axes.Axes`, optional
        The `~matplotlib.axes.Axes` instance used for plotting. Defaults to
        ``None`` which means that a new `~matplotlib.axes.Axes` will be
        created for the plot.
    kwds : dict, optional
        Any additional keywords command will be handed over to matplotlib's
        `~matplotlib.axes.Axes.scatter` command. This can be used to set plot
        properties such as the ``marker``.

    Returns
    -------
    axes : `~matplotlib.axes.Axes`
        The `~matplotlib.axes.Axes` instance that was used for plotting. This
        object allows to modify the plot further, e.g. by setting the plotted
        range, the axis labels, the plot title, etc.
    '''
    # Avoid circular import issues
    from brian2tools.plotting.base import _setup_axes_matplotlib
    axes = _setup_axes_matplotlib(axes)

    if not len(sources) == len(targets):
        raise TypeError('Length of sources and targets does not match.')

    # Get some information out of the values if provided
    if values is not None:
        if len(values) != len(sources):
            raise TypeError('Length of values and sources/targets does not '
                            'match.')
        if var_name is None:
            var_name = getattr(values, 'name', None)  # works for a VariableView
        if var_unit is None:
            try:
                var_unit = values[:]._get_best_unit()
            except AttributeError:
                pass
        if var_unit is not None:
            values = values / var_unit

    connection_count = Counter(zip(sources, targets))
    multiple_synapses = np.any(np.array(list(connection_count.values())) > 1)

    edgecolor = kwds.pop('edgecolor', 'none')

    if multiple_synapses:
        if values is not None:
            raise NotImplementedError('Plotting variables with multiple '
                                      'synapses per source-target pair is not '
                                      'implemented yet.')
        unique_sources, unique_targets = zip(*connection_count.keys())
        n_synapses = list(connection_count.values())
        cmap = mpl.cm.get_cmap(kwds.pop('cmap', 'Accent'), max(n_synapses))
        bounds = np.arange(max(n_synapses) + 1) + 0.5
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
        axes.scatter(unique_sources, unique_targets, c=n_synapses,
                     edgecolor=edgecolor, cmap=cmap, **kwds)
        locatable_axes = make_axes_locatable(axes)
        cax = locatable_axes.append_axes('right', size='5%', pad=0.05)
        mpl.colorbar.ColorbarBase(cax, cmap=cmap,
                                  norm=norm,
                                  ticks=bounds-0.5,
                                  spacing='proportional')
        cax.set_ylabel('number of synapses')
    else:
        if values is None:
            axes.scatter(sources, targets, edgecolor=edgecolor, **kwds)
        else:
            s = axes.scatter(sources, targets, c=values, edgecolor=edgecolor,
                             **kwds)
            locatable_axes = make_axes_locatable(axes)
            cax = locatable_axes.append_axes('right', size='7.5%', pad=0.05)
            plt.colorbar(s, cax=cax)
            if var_name is None:
                if var_unit is not None:
                    cax.set_ylabel('in units of %s' % str(var_unit))
            else:
                label = var_name
                if var_unit is not None:
                    label += ' (%s)' % str(var_unit)
                cax.set_ylabel(label)

    axes.set_xlim(-1, max(sources)+1)
    axes.set_ylim(-1, max(targets)+1)
    axes.set_xlabel('source neuron index')
    axes.set_ylabel('target neuron index')

    return axes

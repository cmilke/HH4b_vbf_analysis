import pickle

import numpy
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt


_output_dir = 'figures/'
_output_ext = '.png'
#_output_ext = '.pdf'


class Hist1():
    def __init__(self, plot_name, plot_title, overlay_list, bin_count, bin_range, **kwargs):
        arg_vals = { 
            'normalize': True, 'legend_args':{}, 'xlabel':'', 'ylabel':'',
            'xlim':None, 'ylim':None, 'ylog':False, 'labelmaker':None,
            'cumulative': 0, 'zooms': []
        }
        self.plot_name = plot_name
        self.plot_title = plot_title
        self.data = { label:([],[]) for label in overlay_list }
        self.bins = bin_count
        self.range = bin_range

        arg_vals.update(kwargs)
        for kw,arg in arg_vals.items(): setattr(self, kw, arg)


    def fill(self, value, key=None, weight=1):
        if key == None: key = list(self.data)[0]
        self.data[key][0].append(value)
        self.data[key][1].append(weight)


    def generate_plot(self, cache, refresh=None):
        print('Plotting '+self.plot_name)
        if refresh == None and cache != None: self.data = cache
        elif refresh: cache[self.plot_name] = self.data
        else: self.data = cache[self.plot_name]

        plot_values = {'x':[],'weights':[],'label':[]}
        for label, (values, weights) in self.data.items():
            counts, bins = numpy.histogram(values, weights=weights, bins=self.bins, range=self.range)
            if counts.sum() == 0: 
                print('WARNING: '+self.plot_name + ' has no data for label ' + str(label))
                if len(values) == 0:
                    print('Label list is empty')
                else:
                    print( 'Label list contains {} values between {} and {}'.format(len(values), min(values), max(values)) )
                return
            binned_vals = counts / counts.sum() if self.normalize else counts
            if self.cumulative != 0:
                if isinstance(self.cumulative,dict):
                    sumdir = self.cumulative[label]
                else:
                    sumdir = self.cumulative
                binned_vals = binned_vals[::sumdir].cumsum()[::sumdir]

            plot_values['x'].append( bins[:-1] )
            plot_values['weights'].append(binned_vals)
            label_text = label if self.labelmaker == None else self.labelmaker(label)
            plot_values['label'].append(label_text)
        plot_values['range'] = self.range
        plot_values['bins'] = self.bins
            
        fig,ax = plt.subplots()
        counts, bins, hist = plt.hist( **plot_values, linewidth=2, histtype='step')

        if len(plot_values['label']) > 1: ax.legend(**self.legend_args)
        plt.grid()
        if self.ylog: plt.yscale('log')
        if self.xlim != None: plt.xlim(*self.xlim)
        if self.ylim != None: plt.ylim(*self.ylim)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.plot_title)
        dpi=500
        fig.savefig(_output_dir+self.plot_name+_output_ext, dpi=dpi)
        for index, (xlim, ylim) in enumerate(self.zooms):
            plt.xlim(xlim)
            plt.ylim(ylim)
            plt.savefig(_output_dir+self.plot_name+f'_zoom{index}'+_output_ext, dpi=dpi)
        plt.close()



class Hist2():
    def __init__(self, plot_name, plot_title, bin_count, bin_range, **kwargs):
        arg_vals = { 'normalize': True, 'xlabel':'', 'ylabel':'', 'zlim':None }
        self.plot_name = plot_name
        self.plot_title = plot_title
        self.data = ([],[])
        self.bins = bin_count
        self.range = bin_range

        arg_vals.update(kwargs)
        for kw,arg in arg_vals.items(): setattr(self, kw, arg)


    def fill(self, value0, value1):
        self.data[0].append(value0)
        self.data[1].append(value1)


    def generate_plot(self, cache, refresh=None):
        print('Plotting '+self.plot_name)
        if refresh == None and cache != None: self.data = cache
        elif refresh: cache[self.plot_name] = self.data
        else: self.data = cache[self.plot_name]

        hist_counts, xedges, yedges = numpy.histogram2d(*self.data, bins=self.bins, range=self.range)
        flat_counts = hist_counts.flatten()
        if flat_counts.sum() == 0: 
            print('WARNING: '+self.plot_name + ' has no data')
            print(*self.data)
            return
        if self.normalize: flat_counts /= hist_counts.sum()
        bin_edges = numpy.array([ (x,y) for x in xedges[:-1] for y in yedges[:-1] ]).transpose()

        fig,ax = plt.subplots()
        counts, xbins, ybins, hist = plt.hist2d( *bin_edges, weights=flat_counts, bins=self.bins, range=self.range)

        cbar = plt.colorbar()
        if self.zlim != None: plt.clim(self.zlim)

        #plt.grid()
        #plt.yscale('log')
        #plt.ylim(10e-6, 1)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.plot_title)
        fig.savefig(_output_dir+self.plot_name+_output_ext)
        plt.close()



class Roc():
    def __init__(self, plot_name, plot_title, overlay_list, **kwargs):
        arg_vals = { 
            'legend_args':{}, 'labelmaker':None, 'normalize': True, 'scale_to_y': False,
            'zooms': []
        }
        self.plot_name = plot_name
        self.plot_title = plot_title
        self.data = { label:( ([],[]), ([],[]) ) for label in overlay_list }
        self.marker_requests = { label:[] for label in overlay_list }

        arg_vals.update(kwargs)
        for kw,arg in arg_vals.items(): setattr(self, kw, arg)


    def add_marker(self, label, marker_value, **kwargs):
        if 'annotation' not in kwargs: kwargs['annotation'] = ''
        self.marker_requests[label].append( (marker_value, kwargs) )


    def fill(self, value, bgd, key=None, weight=1):
        if key == None: key = list(self.data)[0]
        self.data[key][bgd][0].append(value)
        self.data[key][bgd][1].append(weight)


    def generate_plot(self, cache, refresh=None):
        print('Plotting '+self.plot_name)
        if refresh == None and cache != None: self.data = cache
        elif refresh: cache[self.plot_name] = self.data
        else: self.data = cache[self.plot_name]

        roc_ax = plt.subplots()
        marker_list = []

        num_bins = 10000
        for label, (signal,background) in self.data.items():
            maximum = max( max(signal[0]), max(background[0]) )
            minimum = min( min(signal[0]), min(background[0]) )
            efficiency,bin_list = numpy.histogram( signal[0], weights=signal[1], bins=num_bins, range=(minimum, maximum) )
            rejection = numpy.histogram( background[0], weights=background[1], bins=num_bins, range=(minimum, maximum) )[0]
            efficiency = ( efficiency/efficiency.sum() )[::-1].cumsum()[::-1]
            rejection = ( rejection/rejection.sum() ).cumsum()
            plt.plot(efficiency, rejection, label=label, linewidth=1)

            bin_width = bin_list[1] - bin_list[0]
            for marker_val, kwargs in self.marker_requests[label]:
                bin_index = int( (marker_val-minimum) / bin_width )
                location = (efficiency[bin_index], rejection[bin_index])
                print(f'Marker: {label}={marker_val} @ {location[0]},{location[1]}')
                marker_list.append( (location, kwargs) )

        plt.legend(prop={'size':6})
        plt.xlabel('Signal Efficiency')
        plt.ylabel('Background Rejection')
        plt.title(self.plot_title)
        plt.grid(True)
        for location, kwargs in marker_list:
            annotation_text = kwargs.pop('annotation')
            plt.annotate(annotation_text, xy=location, fontsize='x-small')
            plt.plot(*location, **kwargs)

        dpi=500
        plt.savefig(_output_dir+self.plot_name+_output_ext, dpi=dpi)
        for index, (xlim, ylim) in enumerate(self.zooms):
            plt.xlim(xlim)
            plt.ylim(ylim)
            plt.savefig(_output_dir+self.plot_name+f'_zoom{index}'+_output_ext, dpi=dpi)
        plt.close()



class plot_wrapper():
    def __init__(self, blacklist):
        self.plot_dict = {}
        self.blacklist = blacklist

    def add_hist1(self, plot_name, *args, **kwargs):
        self.plot_dict[plot_name] = Hist1(plot_name, *args, **kwargs)

    def add_hist2(self, plot_name, *args, **kwargs):
        self.plot_dict[plot_name] = Hist2(plot_name, *args, **kwargs)

    def add_roc(self, plot_name, *args, **kwargs):
        self.plot_dict[plot_name] = Roc(plot_name, *args, **kwargs)

    def plot_all(self, refresh, cache):
        for key,plot in self.plot_dict.items():
            blacklisted = False
            for substring in self.blacklist:
                if substring in key:
                    blacklisted = True
                    break
            if not blacklisted: plot.generate_plot(cache, refresh=refresh)

    def __getitem__(self, plot_name):
        return self.plot_dict[plot_name]


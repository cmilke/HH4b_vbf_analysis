#!/usr/bin/python3

import sys
import uproot
from matplotlib import pyplot as plt

_stages_to_print = [
    'Trigger',
    '6 jets, pT > 30 GeV',
    'VBF Pair',
    'VBF dEta',
    'VBF mjj',
    'VBF BDT',
    '4 good jets (w/o IS), >= 2 tagged',
    'Multi Tagged',
    #'Two Tagged',
    'Valid',
    'VBF pTsum',
    'pT(h)s',
    'dEta_hh',
    'Main Xwt'
]

_cvv_values = [0,0.5,1,1.5,2,4]
#_cvv_values = [0,0.5,1,1.5,2]
#_cvv_values = [1]


def get_cutflow_values(outputname, hist_name, stages_to_print):
    directory = uproot.open(outputname)
    cutflow_hist = directory[hist_name]
    labeled_values = { k:v for k,v in zip(cutflow_hist.xlabels, cutflow_hist.values) }
    recorded_values = [ labeled_values[key] for key in stages_to_print ]
    return recorded_values


def main():
    base_names = {}
    base_names['ggF'] = 'ggF-HH-bbbb'
    base_names.update( { val:'VBF-HH-bbbb_cvv'+str(val).replace('.','p') for val in _cvv_values } )

    plot_data = {'x':[],'weights':[],'label':[],'histtype':'step','linewidth':2}
    x_values = list(range(len(_stages_to_print)))
    cutflow_type = 'FourTagCutflow'
    #cutflow_type = 'TwoTagCutflow'
    for cvv, base in base_names.items():
        #outputname = '../nano_ntuples/V5/output_MC16d_'+base+'.root'
        outputname = '../nano_ntuples/V12_c0p05/output_MC16d_'+base+'_cut.root'
        cutflow_values = get_cutflow_values(outputname,cutflow_type, _stages_to_print)
        plot_data['x'].append(x_values)
        plot_data['weights'].append(cutflow_values)
        plot_data['label'].append( cvv if cvv == 'ggF' else '$C_{2V}$='+str(cvv) )

    fig,ax = plt.subplots()
    counts, bins, hist = ax.hist(**plot_data, bins=len(x_values), range=(0,len(x_values)) )
    plt.grid()
    plt.legend(fontsize=5)
    x_tick_labels = _stages_to_print.copy()
    x_tick_labels[ x_tick_labels.index('4 good jets (w/o IS), >= 2 tagged') ] = '4 w/o IS'
    x_tick_labels[ x_tick_labels.index('Multi Tagged') ] = '4Tag'
    x_tick_labels[ x_tick_labels.index('6 jets, pT > 30 GeV') ] = '6 Jets'
    plt.xticks(ticks=bins, labels=x_tick_labels, rotation=45, fontsize='xx-small')
    plt.ylabel('Weight Sum (Events / $fb^{-1}$ of data)')
    plt.yscale('log')
    plt.ylim(1e-3, 50)
    plt.title(cutflow_type)
    plt.setp( ax.xaxis.get_majorticklabels(), ha='left')
    #plt.tight_layout()
    plt.savefig('figures/cutflow_4tag_new_bad.png', dpi=500)



if __name__ == "__main__": main()

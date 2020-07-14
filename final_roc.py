#!/usr/bin/python3

import uproot
import numpy
import re
from matplotlib import pyplot as plt



def get_final_sig(outputname, hist_name, stage_to_print):
    directory = uproot.open(outputname)
    cutflow_hist = directory[hist_name]
    labeled_values = { k:v for k,v in zip(cutflow_hist.xlabels, cutflow_hist.values) }
    #for key, val in labeled_values.items(): print(key, val)
    #exit()
    return labeled_values[stage_to_print]
        


def main():
    ntupledir = '../nano_ntuple_maker/run/'
    base_names = { val:'VBF-HH-bbbb_cvv'+str(val).replace('.','p') for val in [ 0, 0.5, 1, 1.5, 2 ] }
    base_names['ggF'] = 'ggF-HH-bbbb'

    cutvalues = numpy.arange(-0.25, 0.5, 0.01)
    cutstrlist = []
    for cutval in cutvalues:
        cutstrlist.append(re.sub('0(?=[.])', '', f'{cutval:.02f}'))
    #cutstrlist[ cutstrlist.index('-.20') ] = '-0.2'
    cutstrlist[ cutstrlist.index('.00') ] = '0'
    cutlist = list( zip(cutvalues, cutstrlist) )

    main_cut = 'Main Xwt'
    signal_region = 'FourTagCutflow'
    #signal_region = 'TwoTagCutflow'
    


    #print(' 6Jet | Pair | VSel | Deta | mjj  |  HH  |')
    data = {}
    base_sig = {}
    for cvv, base in base_names.items():
        data[cvv] = ([],[])
        print(cvv)
        for cutval, cutstr in cutlist:
            ntuple = ntupledir+'scan01/output_MC16d_'+base+'_scanVBFcut_'+cutstr+'.root'
            significance = get_final_sig(ntuple, signal_region, main_cut)
            data[cvv][0].append(cutval)
            data[cvv][1].append(significance)
        base_ntuple = ntupledir+'V9/output_MC16d_'+base+'_dump.root'
        base_sig[cvv] = get_final_sig(base_ntuple, signal_region, main_cut)
    print(base_sig)
    base_points = { cvv:( vbf_sig, base_sig['ggF'] ) for cvv, vbf_sig in base_sig.items() if cvv != 'ggF' }
    print(base_points)

    #for key, (cuts,sigs) in data.items():
    #    print(key)
    #    for cut,sig in zip(cuts,sigs): print(f'{cut:.02f}: {sig:.05f}')
    #    print()

    for key, (cuts,sigs) in data.items():
        title = key if key == 'ggF' else '$C_{2V}$='+str(key)
        plt.plot(cuts, sigs, label=title)
    plt.legend()
    plt.grid(True)
    plt.xlabel('VBF-BDT Cut Value')
    plt.ylabel(r'Event Weight Sum (Events / $fb^{-1}$ of data)')
    #plt.ylim(0,0.33)
    plt.yscale('log')
    plt.title('Cut VS \"'+main_cut+'\" Event Weight Sum ('+signal_region+')')
    plt.savefig('figures/final_weight_comparison_'+signal_region+'.png')
    plt.close()

    signal_dict = { key:val[1] for key,val in data.items() if key != 'ggF' }
    background= data['ggF'][1]

    for key, signal in signal_dict.items(): 
        title = key if key == 'ggF' else '$C_{2V}$='+str(key)
        plt.plot(signal, background, label=title)
    plt.axhline(base_sig['ggF'], color='black')

    plt.legend()
    plt.grid(True)
    plt.xlabel('VBF Weight Sum (Events / $fb^{-1}$ of data)')
    plt.ylabel('ggF Weight Sum (Events / $fb^{-1}$ of data)')
    plt.xlim(1e-3,0.33)
    plt.xscale('log')
    plt.ylim(1e-3,0.33)
    plt.yscale('log')
    plt.title('ggF VS VBF \"'+main_cut+'\" Event Weight Sum ('+signal_region+')')

    sig_colors = {
        0:   'blue',
        0.5: 'orange',
        1:   'green',
        1.5: 'red',
        2:   'purple'
    }
    for cvv, (x,y) in base_points.items():
        plt.plot(x,y, label=cvv, color=sig_colors[cvv], marker='x')


    plt.savefig('figures/final_roc_'+signal_region+'.png')
    plt.close()






if __name__ == "__main__": main()

#!/usr/bin/python3

import sys
import argparse
import pickle
import numpy
import itertools
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from uproot_methods import TLorentzVector as LV
from uproot_wrapper import event_iterator
from plotting_utils import plot_wrapper
import analysis_utils as autils
from tagger_methods import Tagger_options as Tag


#_cvv_vals = [0, 0.5, 1, 1.5, 2, 4]
_cvv_vals = [-1,1]
_VBF_samples = {
#    0  : 'MC16d_VBF-HH-bbbb_cvv0',
#    0.5: 'MC16d_VBF-HH-bbbb_cvv0p5',
    1  : 'MC16d_VBF-HH-bbbb_cvv1',
#    1.5: 'MC16d_VBF-HH-bbbb_cvv1p5',
#    2  : 'MC16d_VBF-HH-bbbb_cvv2',
#    4  : 'MC16d_VBF-HH-bbbb_cvv4'
}
_blacklist = [
    'Deta_of_VBF_mjjmax_mass',
    #'roc',
    #'mjjmax_',
    'roc_example', 
    'rocs_2jet', 'rocs_3jet',
    'fox-wolfram',
    'centrality'
]
_plots = plot_wrapper(_blacklist)

_cvv_labelmaker = lambda cvv: 'ggF' if cvv==-1 else '$C_{2V}$='f'{cvv}'

_plots.add_hist1('num_VBF_candidates', 'Number of Available VBF Candidates',
        [-1,1], 8, (0,8), xlabel='Number of Jets', normalize=False,
        labelmaker=_cvv_labelmaker)

_plots.add_hist1('num_non_btagged', 'Number of non-B-Tagged Jets',
        [-1,1], 8, (0,8), xlabel='Number of Jets', normalize=False,
        labelmaker=_cvv_labelmaker)

_plots.add_hist1('pt', '$p_T$ Distribution of VBF Candidate Jets',
        [''], 100, (0,200), xlabel='$p_T$ (GeV)', normalize=False)
_plots.add_hist1('eta', '$\eta$ Distribution of VBF Candidate Jets',
        [''], 100, (-6,6), xlabel='$\eta$', normalize=False)

_plots.add_hist1('mjjmax', 'Leading $M_{jj}$ Distribution of VBF Candidate Jets',
        [-1,1], 100, (0,3000), xlabel='Leading $M_{jj}$', normalize=False,
        labelmaker=_cvv_labelmaker)

_plots.add_hist1('mjjmax_cumulative', 'Leading $M_{jj}$ Distribution of VBF Candidate Jets,\nCumulatively Summed',
        [-1,1], 100, (0,3000), xlabel='Leading $M_{jj}$', normalize=False, cumulative=-1,
        labelmaker=_cvv_labelmaker)

_plots.add_hist1('mjjmax_cumulative_norm', 'Leading $M_{jj}$ Distribution of VBF Candidate Jets,\nCumulatively Summed and Normalized',
        [-1,1], 100, (0,3000), xlabel='Leading $M_{jj}$', cumulative={-1:1,1:-1},
        labelmaker=_cvv_labelmaker)

_plots.add_hist1('mjjmax_Deta3_cumulative_norm', 'Leading $M_{jj}$ Distribution of VBF Candidate Jets (Post $\Delta \eta > 3$ Cut) ,\nCumulatively Summed and Normalized',
        [-1,1], 1000, (-2,3000), xlabel='Leading $M_{jj}$', cumulative={-1:1,1:-1},
        labelmaker=_cvv_labelmaker)

_plots.add_hist1('BDT1_cumulative_norm', 'Cumulative Distribution of BDT 1 Response',
        [-1,1], 10000, (-1,1), xlabel='BDT Response', cumulative={-1:1,1:-1},
        zooms=[((-.1,.2),(0,1)), ((-0.03,-0.02),(0.8,0.82))], labelmaker=_cvv_labelmaker)

_plots.add_hist1('centrality3jet', 'Centrality of 3-Jet Events',
        [-1,1], 20, (-1,1), xlabel=r'$2 \times (\frac{\eta_C - \eta_L}{\eta_R - \eta_L}) - 1$',
        labelmaker=_cvv_labelmaker)

_plots.add_hist1('centralityGT3jet', 'Centrality of Events with $\geq$ Four Jets',
        [-1,1], 20, (-1,1), xlabel=r'$2 \times (\frac{\eta_C - \eta_L}{\eta_R - \eta_L}) - 1$',
        labelmaker=_cvv_labelmaker)

_plots.add_hist1('centralityPtGT3jet', 'Centrality of Events with $\geq$ Four Jets,\nJets Chosen by Highest $p_T$',
        [-1,1], 20, (-1,1), xlabel=r'$2 \times (\frac{\eta_C - \eta_L}{\eta_R - \eta_L}) - 1$',
        labelmaker=_cvv_labelmaker)

_plots.add_hist1('centrality', 'Centrality of Events with $\geq$ Three Jets',
        [-1,1], 20, (-1,1), xlabel=r'$2 \times (\frac{\eta_C - \eta_L}{\eta_R - \eta_L}) - 1$',
        labelmaker=_cvv_labelmaker)


_fw_moments = [ fwi for fwi in range(11) ]
for fwi in _fw_moments:
    _plots.add_hist1(f'fox-wolfram_{fwi}', f'Fox-Wolfram Moment {fwi} of All Non-B-Tagged Jets',
        _cvv_vals, 100, (0,3), labelmaker=_cvv_labelmaker)

for mass in [0, 1000]:
    _plots.add_hist1(f'Deta_of_VBF_mjjmax_mass{mass}', '$\Delta \eta$ Distribution of VBF Jets w/ $M_{jj}>$'f'{mass} GeV',
            _cvv_vals, 40, (0,10), xlabel='$\Delta \eta$', normalize=False, labelmaker=_cvv_labelmaker)

_simple_taggers = ['mjjmax_Deta3', 'mjjmax']
#_BDT_taggers = ['BDT: mjj-Deta', 'BDT: mjj-Deta-FW', 'BDT: mjj-Deta-FW-Cent']#, 'BDT: mjjLSL_Deta_Cent_FW']
_BDT_taggers = ['BDT: mjj-Deta-FW']
_taggers = _simple_taggers + _BDT_taggers

_plots.add_roc('roc_example', 'Efficiency/Rejection Performance\nof Various VBF/ggF Discriminators', ['mjjmax'] )
#_plots.add_roc('rocs_base', 'Efficiency/Rejection Performance\nof Various VBF/ggF Discriminators', _taggers )
_plots.add_roc('rocs_weighted', 'Weighted Efficiency/Rejection Performance\nof Various VBF/ggF Discriminators', _taggers, zooms=[((0.2,0.6),(0.6,1))] )
_plots.add_roc('rocs_2jet', 'Efficiency/Rejection Performance of Various VBF/ggF Discriminators\nFor Events with 2 VBF Candidate Jets', _taggers)
_plots.add_roc('rocs_3jet', 'Efficiency/Rejection Performance of Various VBF/ggF Discriminators\nFor Events with 3 or More VBF Candidate Jets', _taggers)

#_plots['rocs'].add_marker('mjjmax_Deta3', 1000, annotation='1000 GeV', marker='.', color='red')
_plots['rocs_weighted'].add_marker('mjjmax_Deta3', 1000, annotation='1000 GeV', marker='.', color='blue')
_plots['rocs_weighted'].add_marker('BDT: mjj-Deta-FW', 0.3, annotation='', marker='.', color='green')
#_plots['rocs'].add_marker('mjjmax', 1000, annotation='1000 GeV', marker='.', color='blue')
#_plots['rocs_2jet'].add_marker('mjjSL', 735, annotation='735 GeV', marker='*', color='red')
#_plots['rocs_3jet'].add_marker('mjjSL', 735, annotation='735 GeV', marker='*', color='red')


_output_branches = [
    'run_number', 'event_number', 'mc_sf', 'ntag', 'njets',
    'n_vbf_candidates',
    ('jets', ['vbf_candidates_E', 'vbf_candidates_pT', 'vbf_candidates_eta', 'vbf_candidates_phi'])
]
_output_branches+=[f'FoxWolfram{i}' for i in _fw_moments]


make_reco_vector = lambda jet: LV.from_ptetaphie(jet['resolvedJets_pt'], jet['resolvedJets_eta'], jet['resolvedJets_phi'], jet['resolvedJets_E'])
make_nano_vector = lambda jet: LV.from_ptetaphie(jet['vbf_candidates_pT'], jet['vbf_candidates_eta'], jet['vbf_candidates_phi'], jet['vbf_candidates_E'])


def process_events(events, skip_num=0, bgd=False, cvv_value=-1):
    basic_efficiency_count = [0,0,0]
    num_jets = [0]*20
    num_shared = 0
    num_not_shared = 0
    num_pt_matched = 0
    num_pt_not_matched= 0
    num_negative_weighted=0
    for event_index, event in enumerate(events):
        if event_index < skip_num: continue
        weight = event['mc_sf'][0]
        if weight < 0: continue #num_negative_weighted+=1

        vecs = [ make_nano_vector(jet) for jet in event['jets'] ]
        num_jets[len(vecs)] += 1
        _plots['num_non_btagged'].fill( len(vecs), cvv_value )
        _plots['num_VBF_candidates'].fill( event['n_vbf_candidates'], cvv_value )

        for fwi in _fw_moments: _plots[f'fox-wolfram_{fwi}'].fill(event[f'FoxWolfram{fwi}'], cvv_value)

        basic_efficiency_count[0] += weight
        # Handle Roc Curves
        if len(vecs) > 1 and (cvv_value == 1 or bgd):
            basic_efficiency_count[1] += weight
            # Deal with Simple Taggers
            for tagger in _simple_taggers:
                tag_value = Tag[tagger](vecs)
                #_plots['rocs'].fill( tag_value, bgd, tagger)
                _plots['rocs_weighted'].fill( tag_value, bgd, tagger, weight=weight)
                if len(vecs) == 2: _plots['rocs_2jet'].fill( tag_value, bgd, tagger)
                else: _plots['rocs_3jet'].fill( tag_value, bgd, tagger)
                if tagger == 'mjjmax_Deta3': 
                    _plots['mjjmax_Deta3_cumulative_norm'].fill(tag_value, cvv_value, weight)
                    if tag_value > 1000: basic_efficiency_count[2] += weight
                if tagger == 'mjjmax':
                    _plots['mjjmax'].fill(tag_value, cvv_value)
                    _plots['mjjmax_cumulative'].fill(tag_value, cvv_value)
                    _plots['mjjmax_cumulative_norm'].fill(tag_value, cvv_value)
                    _plots['roc_example'].fill(tag_value, bgd)
            # Deal with the not simple taggers
            #_plots['rocs'].fill( Tag['BDT1'](cvv_value, event_index), bgd, 'BDT1')
            #_plots['rocs_weighted'].fill( Tag['BDT1'](cvv_value, event_index), bgd, 'BDT1', weight=weight)
            for bdt in _BDT_taggers:
                bdt_value = Tag[bdt](event=event, vectors=vecs)
                #print(bdt_value, event[f'FoxWolfram1'])
                _plots['rocs_weighted'].fill( bdt_value, bgd, bdt, weight=weight)
                _plots['BDT1_cumulative_norm'].fill(bdt_value, cvv_value, weight)

        # Look into Centrality
        if len(vecs) == 3 and (cvv_value == 1 or bgd):
            etas = sorted([ v.eta for v in vecs ])
            centrality = 2*(etas[1] - etas[0]) / (etas[2] - etas[0]) - 1
            _plots['centrality3jet'].fill(centrality, cvv_value)
            _plots['centrality'].fill(centrality, cvv_value)

            
        if len(vecs) > 3 and (cvv_value == 1 or bgd):
            mjj_pairs = [ ( (vecs[i]+vecs[j]).mass, (i,j) ) for i,j in itertools.combinations(range(len(vecs)), 2) ]
            mjj_pairs.sort(reverse=True)
            chosen_jets = { i:vecs[i] for i in mjj_pairs[0][1] }
            possible_additions = [ (i,vecs[i]) for i in mjj_pairs[1][1] if i not in chosen_jets ]
            possible_additions.sort(key=lambda t: t[1].pt, reverse=True)
            if len(possible_additions) > 1: num_not_shared += 1
            else: num_shared += 1
            chosen_jets[ possible_additions[0][0] ] = possible_additions[0][1]
            etas = sorted([ jet.eta for jet in chosen_jets.values() ])
            centrality = 2*(etas[1] - etas[0]) / (etas[2] - etas[0]) - 1
            _plots['centralityGT3jet'].fill(centrality, cvv_value)
            _plots['centrality'].fill(centrality, cvv_value)

            pt_chosen_jets = { i:vec for i,vec in enumerate( sorted(vecs, key=lambda v: v.pt, reverse=True)[:3] ) }
            etas = sorted([ jet.eta for jet in pt_chosen_jets.values() ])
            centrality = 2*(etas[1] - etas[0]) / (etas[2] - etas[0]) - 1
            _plots['centralityPtGT3jet'].fill(centrality, cvv_value)

            mjj_keys = sorted( chosen_jets.keys() )
            pt_keys = sorted( pt_chosen_jets.keys() )
            if mjj_keys == pt_keys: num_pt_matched += 1
            else: num_pt_not_matched += 1





        # Create Delta-eta of leading mjj pair distribution
        if not bgd and len(vecs) > 1:
            deta_mjj_list = [ ( (i+j).mass, abs(i.eta - j.eta) ) for i,j in itertools.combinations(vecs, 2) ]
            deta_mjj_list.sort() # Sort by mjj
            Deta_filtered = [ (mass,Deta) for mass, Deta in deta_mjj_list ] #if Deta > 3 ]
            for mass in [0,1000]:
                mass_filtered = [ pair for pair in Deta_filtered if pair[0] > mass ]
                if len(mass_filtered) > 0: 
                    vbf_pair = mass_filtered[0]
                    _plots[f'Deta_of_VBF_mjjmax_mass{mass}'].fill(vbf_pair[1], cvv_value)

        if cvv_value == 1:
            for v in vecs:
                _plots['pt'].fill(v.pt)
                _plots['eta'].fill(v.eta)
    jet_counts = numpy.array(num_jets[0:10])
    #print(jet_counts)
    #for count,frac in enumerate(jet_counts/jet_counts.sum()): print(f'{count}: {frac*100:4.1f}')
    print(num_shared, num_not_shared)
    print(num_pt_matched, num_pt_not_matched)
    print(f'Negative={num_negative_weighted}')
    #print(basic_efficiency_count)



def extract_data(num_events, events_to_skip):
    for cvv_value, vbf_sample in _VBF_samples.items():
        sig_events = event_iterator(autils.NanoNtuples[vbf_sample], 'VBF_tree', _output_branches, num_events)
        process_events(sig_events, skip_num=events_to_skip , cvv_value=cvv_value)

    bgd_events = event_iterator(autils.NanoNtuples['MC16d_ggF-HH-bbbb'], 'VBF_tree', _output_branches, num_events)
    process_events(bgd_events, skip_num=events_to_skip, bgd=True)



def draw_distributions():
    parser = argparse.ArgumentParser()
    parser.add_argument( "-r", required = False, default = False, action = 'store_true', help = "Refresh cache",) 
    parser.add_argument( "-p", required = False, default = False, action = 'store_true', help = "Print only, do not plot",) 
    parser.add_argument( "-n", required = False, default = 1e4, type=float, help = "How many events to run over",)
    parser.add_argument( "-s", required = False, default = 0, type=float, help = "How many events to skip",)
    args = parser.parse_args()

    refresh = args.r
    num_events = int(args.n) if args.n > 0 else None
    events_to_skip = int(args.s)
    cache = {}
    cache_file = '.cache/general_plots.p'
    if refresh: extract_data(num_events, events_to_skip)
    else: cache = pickle.load( open(cache_file, 'rb') )
    if not args.p:
        print('Data extracted, plotting...')
        _plots.plot_all(refresh, cache)
        if refresh: pickle.dump( cache, open(cache_file, 'wb') )

draw_distributions()

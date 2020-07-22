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
_blacklist = [ ]
_plots = plot_wrapper(_blacklist)

_cvv_labelmaker = lambda cvv: 'ggF' if cvv==-1 else '$C_{2V}$='f'{cvv}'

_plots.add_hist1('truth_num_non_btagged', 'Number of non-B (Truth-matched) Jets',
        [-1,1], 8, (0,8), xlabel='Number of Jets', normalize=False,
        labelmaker=_cvv_labelmaker, zooms=[((0,8),(0,300000)),((0,8),(0,50000))])

_plots.add_hist1('truth_num_non_btagged_pt-gt30', 'Number of non-B (Truth-matched) Jets with $p_T$ > 30 GeV',
        [-1,1], 8, (0,8), xlabel='Number of Jets', normalize=False,
        labelmaker=_cvv_labelmaker, zooms=[((0,8),(0,300000)),((0,8),(0,50000))])

_plots.add_hist1('truthMatched_num_non_btagged', 'Number of non-B (Truth-matched) Jets in Matched Events',
        [-1,1], 8, (0,8), xlabel='Number of Jets', normalize=True,
        labelmaker=_cvv_labelmaker)

_input_branches = [
    'eventNumber',
    'nresolvedJets',
    ('tjs', ['truth_pdgId', 'truth_status', 'truth_barcode', 'truth_nParents', 'truth_parent_pdgId']),
    ('resolved_jets', [ 'resolvedJets_pt', 'resolvedJets_phi', 'resolvedJets_eta', 'resolvedJets_E', #resolved pt in GeV
        'resolvedJets_HadronConeExclTruthLabelID'
    ])
]

_output_branches = [
    'run_number', 'event_number', 'mc_sf', 'ntag', 'njets',
    'n_vbf_candidates',
    ('jets', ['vbf_candidates_E', 'vbf_candidates_pT', 'vbf_candidates_eta', 'vbf_candidates_phi'])
]



make_reco_vector = lambda jet: LV.from_ptetaphie(jet['resolvedJets_pt'], jet['resolvedJets_eta'], jet['resolvedJets_phi'], jet['resolvedJets_E'])
make_nano_vector = lambda jet: LV.from_ptetaphie(jet['vbf_candidates_pT'], jet['vbf_candidates_eta'], jet['vbf_candidates_phi'], jet['vbf_candidates_E'])


def process_events(in_events, out_events, bgd=False, cvv_value=-1):
    #out_event_dictionary = {}
    #for event_index, event in enumerate(out_events):
    #    out_event_dictionary[ event['event_number'] ] = [ make_nano_vector(jet) for jet in event['jets'] ]

    base_pdg = [-5,-5,5,5,25,25]
    for event_index, event in enumerate(in_events):
        pdgs = []
        for tj in event['tjs']:
            pdgs.append(tj['truth_pdgId'])
        pdgs.sort()
        print(pdgs)
        #in_vecs = []
        #in_vecs_ptGT30 = []
        #for jet in event['resolved_jets']:
        #    if jet['resolvedJets_HadronConeExclTruthLabelID'] == 5: continue
        #    vec = make_reco_vector(jet) 
        #    in_vecs.append(vec)
        #    if jet['resolvedJets_pt'] > 30: in_vecs_ptGT30.append(vec)
        ##in_vecs = [ make_reco_vector(jet) for jet in event['resolved_jets'] ]
        ##print( len(out_vecs), len(in_vecs) )
        #_plots['truth_num_non_btagged'].fill(len(in_vecs), cvv_value)
        #_plots['truth_num_non_btagged_pt-gt30'].fill(len(in_vecs_ptGT30), cvv_value)
        ##if event['eventNumber'] in out_event_dictionary:
        ##    _plots['truthMatched_num_non_btagged'].fill(len(in_vecs_ptGT30), cvv_value)
        ##out_vecs = out_event_dictionary[ event['eventNumber'] ]


        



def extract_data(num_events):
    #for cvv_value, vbf_sample in _VBF_samples.items():
    #    in_sig_events = event_iterator(autils.input_datasets[vbf_sample], 'XhhMiniNtuple', _input_branches, num_events)
    #    out_sig_events = event_iterator(autils.output_datasets[vbf_sample], 'VBF_tree', _output_branches, num_events)
    #    process_events(in_sig_events, out_sig_events, cvv_value=cvv_value)

    #in_bgd_events = event_iterator(autils.input_datasets['MC16d_ggF-HH-bbbb'], 'XhhMiniNtuple', _input_branches, num_events)
    #out_bgd_events = event_iterator(autils.output_datasets['MC16d_ggF-HH-bbbb'], 'VBF_tree', _output_branches, num_events)
    #process_events(in_bgd_events, out_bgd_events, bgd=True)
    process_events( event_iterator(['../mc16_13TeV.450044.MGH7EvtGen_MMHT2014_hh_bbbb_vbf_l1cvv1cv1.deriv.DAOD_EXOT8.e7254_s3126_r9364_p4089.root'], 'XhhMiniNtuple', _input_branches, num_events) , None)



def draw_distributions():
    parser = argparse.ArgumentParser()
    parser.add_argument( "-r", required = False, default = False, action = 'store_true', help = "Refresh cache",) 
    parser.add_argument( "-p", required = False, default = False, action = 'store_true', help = "Print only, do not plot",) 
    parser.add_argument( "-n", required = False, default = 1e4, type=float, help = "How many events to run over",)
    args = parser.parse_args()

    refresh = args.r
    num_events = int(args.n) if args.n > 0 else None
    cache = {}
    cache_file = '.cache/truth_plots.p'
    if refresh: extract_data(num_events)
    else: cache = pickle.load( open(cache_file, 'rb') )
    if not args.p:
        print('Data extracted, plotting...')
        _plots.plot_all(refresh, cache)
        if refresh: pickle.dump( cache, open(cache_file, 'wb') )

draw_distributions()

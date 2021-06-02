# -*- coding: utf-8 -*-

import trackpy as tp
import skimage.measure as measure
from skimage.util import img_as_uint
from skimage.morphology import remove_small_objects
import pandas as pd
import numpy as np


def track(df, displace=40, gap_fill=5):
    """Track and relabel mask with trackID.

    Args:
        df (pandas.DataFrame): Data frame with fields:
            - Center_of_the_object_0: x location of each object
            - Center_of_the_object_1: y location of each object
            - frame: time location
            - (other optional columns)

        displace (int): maximum distance an object can move between frames.
        gap_fill (int): temporal filling fo tracks.
    
    Return:
        (pandas.DataFrame): tracked object table.
    """

    f = df[['Center_of_the_object_0', 'Center_of_the_object_1', 'frame']]
    f.columns = ['x', 'y', 'frame']
    t = tp.link(f, search_range=displace, memory=gap_fill, adaptive_stop=0.4 * displace)
    t.columns = ['Center_of_the_object_0', 'Center_of_the_object_1', 'frame', 'trackId']
    out = pd.merge(df, t, on=['Center_of_the_object_0', 'Center_of_the_object_1', 'frame'])
    #  change format for downstream
    out['trackId'] += 1
    out['lineageId'] = out['trackId']
    out['parentTrackId'] = 0
    out = out[
        ['frame', 'trackId', 'lineageId', 'parentTrackId', 'Center_of_the_object_0', 'Center_of_the_object_1', 'phase',
         'Probability of G1/G2', 'Probability of S', 'Probability of M', 'continuous_label', 'major_axis', 'minor_axis',
         'mean_intensity', 'emerging', 'background_mean']]
    names = list(out.columns)
    names[4] = 'Center_of_the_object_1'
    names[5] = 'Center_of_the_object_0'
    names[6] = 'predicted_class'
    out.columns = names
    out = out.sort_values(by=['trackId', 'frame'])

    return out


def track_mask(mask, displace=40, gap_fill=5, render_phase=False,
               phase_dic={10: 'G1/G2', 50: 'S', 100: 'M', 200: 'G1/G2'}, size_min=100):
    """Track binary mask objects.

    Args:
        mask (numpy.ndarray): dtype=uint8, can either be binary or labeled with cell cycle phases.
        displace (int): distance restriction, see track().
        gap_fill (int): time restriction, see track().
        render_phase (bool): whether to deduce cell cycle phase from the labeled mask.
        phase_dic (dict): mapping of object label and cell cycle phase.
        size_min (int): remove object smaller then some size, in case the mask labeling is not precise.
    """

    p = pd.DataFrame()
    mask_lbd = np.zeros(mask.shape)
    
    for i in range(mask.shape[0]):
        # remove small objects: may have unexpected behavior
        mask[i, :, :] = remove_small_objects(mask[i, :, :], min_size=size_min, connectivity=1)
        mask_lbd[i, :, :] = measure.label(mask[i, :, :], connectivity=1)
    if np.max(mask_lbd) <= 255:
        mask_lbd = mask_lbd.astype('uint8')
    else:
        mask_lbd = img_as_uint(mask_lbd)
        
    if render_phase:
        for i in range(mask.shape[0]):
            props = measure.regionprops_table(mask_lbd[i, :, :], intensity_image=mask[i, :, :], 
                                              properties=('centroid', 'label', 'max_intensity', 'major_axis_length', 'minor_axis_length'))
            props = pd.DataFrame(props)
            props.columns = ['Center_of_the_object_0', 'Center_of_the_object_1', 'continuous_label', 'mean_intensity',
                             'major_axis', 'minor_axis']
            l = props['mean_intensity']
            phase = []
            probG = []
            probS = []
            probM = []
            e = []
            for k in range(props.shape[0]):
                ps = phase_dic[int(l[k])]
                if int(l[k]) == 200:
                    e.append(1)
                else:
                    e.append(0)
                phase.append(ps)
                if ps == 'G1/G2':
                    probG.append(1)
                    probS.append(0)
                    probM.append(0)
                elif ps == 'S':
                    probG.append(0)
                    probS.append(1)
                    probM.append(0)
                else:
                    probG.append(0)
                    probS.append(0)
                    probM.append(1)

            props['Probability of G1/G2'] = probG
            props['Probability of S'] = probS
            props['Probability of M'] = probM
            props['emerging'] = e
            props['phase'] = phase
            props['frame'] = i
            p = p.append(props)

    else:
        for i in range(mask.shape[0]):
            props = measure.regionprops_table(measure.label(mask[i, :, :], connectivity=1), properties=(
                'centroid', 'label', 'major_axis_length', 'minor_axis_length'))
            props = pd.DataFrame(props)
            props.columns = ['Center_of_the_object_0', 'Center_of_the_object_1', 'continuous_label', 'major_axis',
                             'minor_axis']
            props['Probability of G1/G2'] = 0
            props['Probability of S'] = 0
            props['Probability of M'] = 0
            props['phase'] = 0
            props['frame'] = i
            props['mean_intensity'] = 0
            props['emerging'] = 0
            p = p.append(props)
    
    p['background_mean'] = 0
    track_out = track(p, displace=displace, gap_fill=gap_fill)
    return track_out, mask_lbd

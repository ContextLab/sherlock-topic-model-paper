"""
This module contains analysis functions used across multiple notebooks,
as well as some functions to view them from the notebooks
"""

import re
from inspect import getsource
from typing import Iterator

import matplotlib.patches as patches
import numpy as np
import pandas as pd
from fastdtw import fastdtw
from IPython.display import display, HTML
from IPython.core.oinspect import pylight
from scipy.spatial.distance import correlation

from .constants import EDGECOLOR, GRID_SCALE


########################################
#     TEXT PREPROCESSING & MODELING    #
########################################

def format_text(text):
    if isinstance(text, pd.Series):
        text = ' '.join(list(text.dropna()))
        pattern = "[^\w\s]+"
    else:
        pattern = "[^.\w\s]+"

    no_possessive = text.lower().replace("'s", '')
    return re.sub(pattern, '', no_possessive)


def get_video_timepoints(window_spans, annotations):
    timepoints = []
    for first, last in window_spans:
        window_onset = annotations.loc[first, 'Start Time (s) ']
        window_offset = annotations.loc[last - 1, 'End Time (s) ']
        timepoints.append((window_onset + window_offset) / 2)

    return np.array(timepoints)


def parse_windows(textlist, wsize):
    windows = []
    window_bounds = []
    for ix in range(1, wsize):
        start, end = 0, ix
        window_bounds.append((start, end))
        windows.append(' '.join(textlist[start:end]))

    for ix in range(len(textlist)):
        start = ix
        end = ix + wsize if ix + wsize <= len(textlist) else len(textlist)
        window_bounds.append((start, end))
        windows.append(' '.join(textlist[start:end]))

    return windows, window_bounds


########################################
#         STATS/MATH FUNCTIONS         #
########################################

def corr_mean(rs, axis=0):
    return z2r(np.nanmean([r2z(r) for r in rs], axis=axis))


def r2z(r):
    with np.errstate(invalid='ignore', divide='ignore'):
        return 0.5 * (np.log(1 + r) - np.log(1 - r))


def z2r(z):
    with np.errstate(invalid='ignore', divide='ignore'):
        return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)


########################################
#          PLOTTING FUNCTIONS          #
########################################

def add_arrows(axes, x, y, **kwargs):
    # spacing of arrows
    aspace = .05 * GRID_SCALE
    # distance spanned between pairs of points
    r = [0]
    for i in range(1, len(x)):
        dx = x[i] - x[i - 1]
        dy = y[i] - y[i - 1]
        r.append(np.sqrt(dx * dx + dy * dy))

    r = np.array(r)
    # cumulative sum of r, used to save time
    rtot = []
    for i in range(len(r)):
        rtot.append(r[0:i].sum())
    rtot.append(r.sum())
    # will hold tuple(x, y, theta) for each arrow
    arrow_data = []
    # current point on walk along data
    arrow_pos = 0
    rcount = 1
    while arrow_pos < r.sum():
        x1, x2 = x[rcount - 1], x[rcount]
        y1, y2 = y[rcount - 1], y[rcount]
        da = arrow_pos - rtot[rcount]
        theta = np.arctan2((x2 - x1), (y2 - y1))
        ax = np.sin(theta) * da + x1
        ay = np.cos(theta) * da + y1
        arrow_data.append((ax, ay, theta))
        arrow_pos += aspace
        while arrow_pos > rtot[rcount + 1]:
            rcount += 1
            if arrow_pos > rtot[-1]:
                break

    for ax, ay, theta in arrow_data:
        # use aspace as a guide for size and length of things
        # scaling factors were chosen by experimenting a bit
        axes.arrow(ax,
                   ay,
                   np.sin(theta) * aspace / 10,
                   np.cos(theta) * aspace / 10,
                   head_width=aspace / 3,
                   **kwargs)


def draw_bounds(ax, model):
    bounds = np.where(np.diff(np.argmax(model.segments_[0], axis=1)))[0]
    bounds_aug = np.concatenate(([0], bounds, [model.segments_[0].shape[0]]))
    for i in range(len(bounds_aug) - 1):
        rect = patches.Rectangle((bounds_aug[i], bounds_aug[i]),
                                 bounds_aug[i + 1] - bounds_aug[i],
                                 bounds_aug[i + 1] - bounds_aug[i],
                                 linewidth=1,
                                 edgecolor=EDGECOLOR,
                                 facecolor='none')
        ax.add_patch(rect)

    return ax

########################################
#            BRAIN ANALYSES            #
########################################


def create_diag_mask(corrmat, diag_limit=None):
    diag_mask = np.zeros_like(corrmat, dtype=bool)
    if diag_limit is None:
        diag_limit = find_diag_limit(corrmat)

    for k in range(1, diag_limit):
        ix = kth_diag_indices(diag_mask, k)
        diag_mask[ix] = True

    return diag_mask


def find_diag_limit(corrmat):
    for k in range(corrmat.shape[0]):
        d = np.diag(corrmat, k=k)
        if ~(d > 0).any():
            return k


def kth_diag_indices(arr, k):
    row_ix, col_ix = np.diag_indices_from(arr)
    return row_ix[:-k], col_ix[k:]


def warp_recall(recall_traj, video_traj, return_paths=False):
    dist, path = fastdtw(video_traj, recall_traj, dist=correlation)
    recall_path = [i[1] for i in path]
    warped_recall = recall_traj[recall_path]
    if return_paths:
        video_path = [i[0] for i in path]
        return warped_recall, video_path, recall_path
    else:
        return warped_recall


########################################
#          NOTEBOOK DISPLAYS           #
########################################

def multicol_display(*outputs,
                     ncols=2,
                     caption=None,
                     col_headers=None,
                     table_css=None,
                     caption_css=None,
                     header_css=None,
                     row_css=None,
                     cell_css=None):
    def _fmt_python_types(obj):
        # formats some common Python objects for display
        if isinstance(obj, str):
            return obj.replace('\n', '<br>')
        elif isinstance(obj, (int, float)):
            return str(obj)
        elif (isinstance(obj, (list, tuple, set, Iterator))
              or type(obj).__module__ == 'numpy'):
            return ', '.join(obj)
        elif isinstance(obj, dict):
            return '<br><br>'.join(f'<b>{k}</b>:&emsp;{_fmt_python_types(v)}'
                                   for k, v in obj.items())
        elif isinstance(obj, pd.DataFrame):
            return obj.to_html()
        elif isinstance(obj, pd.Series):
            return obj.to_frame().to_html()
        else:
            return obj

    if col_headers is None:
        col_headers = []
    else:
        col_headers = list(col_headers)
        assert len(col_headers) == ncols

    outs_fmt = []
    for out in outputs:
        outs_fmt.append(_fmt_python_types(out))

    table_css = {} if table_css is None else table_css
    caption_css = {} if caption_css is None else caption_css
    header_css = {} if header_css is None else header_css
    row_css = {} if row_css is None else row_css
    cell_css = {} if cell_css is None else cell_css

    # set some reasonable default style properties
    table_css_defaults = {
        'width': '100%',
        'border': '0px',
        'margin-left': 'auto',
        'margin-right': 'auto'
    }
    caption_css_defaults = {
        'color': 'unset',
        'text-align': 'center',
        'font-size': '2em',
        'font-weight': 'bold'
    }
    header_css_defaults = {
        'border': '0px',
        'font-size': '16px',
        'text-align': 'center'
    }
    row_css_defaults = {'border': '0px'}
    cell_css_defaults = {
        'border': '0px',
        'width': f'{100 / ncols}%',
        'vertical-align': 'top',
        'font-size': '14px',
        'text-align': 'center'
    }

    # update/overwrite style defaults with passed properties
    table_css = dict(table_css_defaults, **table_css)
    caption_css = dict(caption_css_defaults, **caption_css)
    header_css = dict(header_css_defaults, **header_css)
    row_css = dict(row_css_defaults, **row_css)
    cell_css = dict(cell_css_defaults, **cell_css)

    # format for string replacement in style tag
    table_style = ";".join(f"{prop}:{val}" for prop, val in table_css.items())
    caption_style = ";".join(f"{prop}:{val}" for prop, val in caption_css.items())
    header_style = ";".join(f"{prop}:{val}" for prop, val in header_css.items())
    row_style = ";".join(f"{prop}:{val}" for prop, val in row_css.items())
    cell_style = ";".join(f"{prop}:{val}" for prop, val in cell_css.items())

    # string templates for individual elements
    html_table = f"<table style={table_style}>{{caption}}{{header}}{{content}}</table>"
    html_caption = f"<caption style={caption_style}>{{content}}</caption>"
    html_header = f"<th style={header_style}>{{content}}</th>"
    html_row = f"<tr style={row_style}>{{content}}</tr>"
    html_cell = f"<td style={cell_style}>{{content}}</td>"

    # fill element templates with content
    cap = html_caption.format(content=caption) if caption is not None else ''
    headers = [html_header.format(content=h) for h in col_headers]
    cells = [html_cell.format(content=out) for out in outs_fmt]
    rows = [html_row.format(content="".join(cells[i:i+ncols])) for i in range(0, len(cells), ncols)]
    # render notebook display cell
    display(HTML(html_table.format(caption=cap,
                                   header="".join(headers),
                                   content="".join(rows))))


def show_source(obj):
    try:
        src = getsource(obj)
    except TypeError as e:
        src = obj
    try:
        return HTML(pylight(src))
    except AttributeError:
        return src

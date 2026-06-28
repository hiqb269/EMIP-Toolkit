# Gender, Code Comprehension, and Eye Movement Analysis

This repository contains analysis materials for a research project on gender and code comprehension. The project examines whether gender is associated with comprehension accuracy and eye-movement behaviour while accounting for factors such as programming expertise, task, stimulus variant, source-line structure, and semantic code category.

The project is motivated by the idea that code-comprehension performance is only one part of the story: eye-tracking data can also show how participants allocate visual attention while reading source code. The analysis therefore combines outcome-level measures, such as task correctness, with process-level measures, such as fixation time, scanpath length, line revisits, and attention to semantic code constructs. This makes it possible to ask whether observed differences are better explained by gender or by other factors such as prior programming experience, task demands, and properties of the source code itself.

The work uses eye-tracking and code-task data to study four related questions:

- RQ1: whether gender predicts code-comprehension accuracy after controlling for programming expertise and task effects.
- RQ2: whether gender is associated with global process-level cognitive effort, such as fixation counts, total fixation time, fixation duration, saccade distance, and scanpath length.
- RQ3: whether gender is associated with line-level reading behaviour, including line dwell time, first-fixation order, revisits, and line coverage.
- RQ4: whether gender is associated with attention allocation across semantic source-code construct categories.

The current analysis should be read conservatively: the available RQ2-RQ4 results do not provide strong evidence that gender explains the measured eye-movement outcomes. The clearer patterns are linked to expertise, task, stimulus variant, line structure, and semantic code category.

## Repository Contents

- `JupyterNotebooks/`: analysis notebooks for RQ1-RQ4.
- `emtk/`: the adapted EMIP Toolkit code used to support parsing, fixation processing, AOI mapping, and related analysis steps.
- `requirements.txt`: core Python dependencies.

## Raw Data Setup

The raw EMIP data is not checked into this repository. Download the EMIP replication package from OSF:

https://osf.io/j6vt3/download

Extract the downloaded archive into `emtk/datasets/EMIP/` so the folder structure matches the paths expected by the parser:

```text
emtk/
  datasets/
    EMIP/
      EMIP-Toolkit- replication package/
        emip_dataset/
          rawdata/
          stimuli/
          emip_metadata.csv
```

The `emtk.parsers.EMIP()` loader checks for `emtk/datasets/EMIP/EMIP-Toolkit- replication package/emip_dataset/rawdata`. If that directory is missing, the toolkit will try to download and unzip the OSF package automatically, but placing the archive contents in the structure above is the most reliable setup.

## Citation

This project builds on the EMIP Toolkit. If you use the toolkit components or derived processing workflow, cite:

Al Madi, N., Guarnera, D. T., Sharif, B., and Maletic, J. I. (2021). *EMIP Toolkit: A Python Library for Customized Post-processing of the Eye Movements in Programming Dataset*. ACM Symposium on Eye Tracking Research and Applications. https://doi.org/10.1145/3448018.3457425

```bibtex
@inproceedings{almadi2021emip,
  title = {EMIP Toolkit: A Python Library for Customized Post-processing of the Eye Movements in Programming Dataset},
  author = {Al Madi, Naser and Guarnera, Drew T. and Sharif, Bonita and Maletic, Jonathan I.},
  booktitle = {ACM Symposium on Eye Tracking Research and Applications},
  pages = {1--6},
  year = {2021},
  doi = {10.1145/3448018.3457425}
}
```

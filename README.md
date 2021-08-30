# pcnaDeep: a deep-learning based single-cell cycle profiler with PCNA signal

<img src="/assets/icon.png" alt="banner" width="200" align="top" />

Welcome! pcnaDeep integrates cutting-edge detection techniques with tracking and cell cycle resolving models.
Using the Mask R-CNN model under FAIR's Detectron2 framework, pcnaDeep is able to detect and resolve very dense cell tracks with __PCNA fluorescent Only__.

<!--![image](/assets/res_demo.gif)-->

## Installation
1. PyTorch (torch >= 1.7.1) installation and CUDA GPU support are essential. Visit [PyTorch homepage](https://pytorch.org/) for specific installation schedule.
2. Install modified __Detectron2 v0.4__ in this directory ([original package homepage](https://github.com/facebookresearch/detectron2))
   ```angular2html
      cd detectron2-04_mod
      pip install .
   ```
   - In pcnaDeep, the detectron2 v0.4 dependency has been modified in two ways:
      1. To generate confidence score output of the instance classification, the method `detectron2.modeling.roi_heads.fast_rcnn.fast_rcnn_inference_single_image` has been modified.
      2. A customized dataset mapper function has been implemented as `detectron2.data.dataset_mapper.read_PCNA_training`.
   - To build Detectron2 on __Windows__ may require the following change of `torch` package. [Reference (Chinese)](https://blog.csdn.net/weixin_42644340/article/details/109178660).
    ```angular2html
       In torch\include\torch\csrc\jit\argument_spec.h,
       static constexpr size_t DEPTH_LIMIT = 128;
          change to -->
       static const size_t DEPTH_LIMIT = 128;
    ```
3. Install pcnaDeep from source in this directory
   ```
   cd bin
   python setup.py install
   ```
4. (optional, for training data annotation only) Download [VGG Image Annotator 2](https://www.robots.ox.ac.uk/~vgg/software/via/) software.
5. (optional, for visualisation only) Install [Fiji (ImageJ)](https://fiji.sc/) with [TrackMate CSV Importer](https://github.com/tinevez/TrackMate-CSVImporter) plugin.

## Download pre-trained Mask R-CNN weights

The Mask R-CNN is trained on 60X microscopic images sized 1200X1200 square pixels. [Download here]().

## Getting started

See [a quick tutorial](tutorial/getting_started.ipynb) to get familiar with pcnaDeep.

You may also go through other tutorials for advanced usages.

## API Documentation

API documentation is available [here]().

## Licence

pcnaDeep is released under the [Apache 2.0 license]().

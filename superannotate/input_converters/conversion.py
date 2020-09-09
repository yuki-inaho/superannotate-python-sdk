import sys
import os
from argparse import Namespace

from .coco_conversions import coco_to_sa, sa_to_coco
from .voc_conversions import voc_to_sa

AVAILABLE_DATASET_FORMAT_CONVERTERS = ["COCO", "VOC"]


def export_annotation_format(
    input_dir,
    output_dir,
    dataset_format,
    dataset_name,
    project_type="Vector",
    task="object_detection",
    train_val_split_ratio=100,
    copyQ=True
):
    """Converts SuperAnnotate annotation formate to the other annotation formats.

    :param input_dir: Path to the dataset folder that you want to convert.
    :type input_dir: str
    :param output_dir: Path to the folder, where you want to have converted dataset.
    :type output_dir: str
    :param dataset_format: One of the formats that are possible to convert. Choose from ["COCO"]
    :type dataset_format: str
    :param dataset_name: Name of the dataset.
    :type dataset_name: str
    :param project_type: Project type is either 'Vector' or 'Pixel' (Default: 'Vector')
    :type project_type: str
    :param task: Choose one from possible candidates. ['panoptic_segmentation', 'instance_segmentation', 'keypoint_detection', 'object_detection'] (Default: "objec_detection")
    :type task: str
    :param train_val_split_ratio: Percentage of data to split between test and train. (Default: 100)
    :type train_val_split_ratio: float, optional
    :param copyQ: Copy original images or move (Default: True, copies) 
    :type copyQ: boolean, optional
    """

    if dataset_format not in AVAILABLE_DATASET_FORMAT_CONVERTERS:
        raise ValueError(
            "'{}' converter doesn't exist. Possible candidates are '{}'".format(
                dataset_format, AVAILABLE_DATASET_FORMAT_CONVERTERS
            )
        )

    args = Namespace(
        input_dir=input_dir,
        output_dir=output_dir,
        dataset_format=dataset_format,
        dataset_name=dataset_name,
        project_type=project_type,
        task=task,
        train_val_split_ratio=train_val_split_ratio,
        copyQ=copyQ
    )

    if dataset_format == "COCO":
        sa_to_coco(args)
    elif dataset_format == "VOC":
        pass
    else:
        pass


def import_annotation_format(
    input_dir,
    output_dir,
    dataset_format,
    dataset_name,
    project_type="Vector",
    task="object_detection",
    copyQ=True
):
    """Converts other annotation formats to SuperAnnotate annotation format.

    :param input_dir: Path to the dataset folder that you want to convert.
    :type input_dir: str
    :param output_dir: Path to the folder, where you want to have converted dataset.
    :type output_dir: str
    :param dataset_format: One of the formats that are possible to convert. Choose from ["COCO"]
    :type dataset_format: str
    :param dataset_name: Name of the dataset.
    :type dataset_name: str
    :param project_type: Project type is either 'Vector' or 'Pixel'. (Default: 'Vector')
    :type project_type: str
    :param task: Choose one from possible candidates. ['panoptic_segmentation', 'instance_segmentation', 'keypoint_detection', 'object_detection']. (Default: 'object_detection')
    :type task: str
    :param copyQ: Copy original images or move (Default: True, copies) 
    :type copyQ: boolean, optional
    """

    if dataset_format not in AVAILABLE_DATASET_FORMAT_CONVERTERS:
        raise ValueError(
            "'{}' converter doesn't exist. Possible candidates are '{}'".format(
                dataset_format, AVAILABLE_DATASET_FORMAT_CONVERTERS
            )
        )

    args = Namespace(
        input_dir=input_dir,
        output_dir=output_dir,
        dataset_format=dataset_format,
        dataset_name=dataset_name,
        project_type=project_type,
        task=task,
        copyQ=copyQ
    )

    if dataset_format == "COCO":
        coco_to_sa(args)
    elif dataset_format == "VOC":
        voc_to_sa(args)
    else:
        pass

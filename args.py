"""
adapted from : 
EASY - Ensemble Augmented-Shot Y-shaped Learning: State-Of-The-Art Few-Shot Classification with Simple Ingredients.
(https://github.com/ybendou/easy)
(to load a model without training)
"""

import argparse
import os
import sys


def parse_evaluation_args(parser):

    # dataset features
    parser.add_argument(
        "--dataset-path", type=str, default="data/", help="dataset path"
    )
    parser.add_argument("--batch-size", type=int, default=1, help="batch size")
    parser.add_argument(
        "--num-classes-dataset", type=int, default=10, help="number of class in dataset"
    )

    ### few-shot parameters

    parser.add_argument("--n-ways", type=int, default=5, help="number of few-shot ways")
    parser.add_argument(
        "--n-shots",
        type=int,
        default=5,
        help="how many shots per few-shot run, can be int or list of ints. In case of episodic training, use first item of list as number of shots.",
    )
    parser.add_argument(
        "--n-runs", type=int, default=1000, help="number of few-shot runs"
    )
    parser.add_argument(
        "--n-queries", type=int, default=15, help="number of few-shot queries"
    )
    parser.add_argument("--batch-size-fs", type=int, default=20)
    # to be incorporate (to evaluation and demonstration):
    # parser.add_argument("--sample-aug", type=int, default=1, help="number of versions of support/query samples (using random crop) 1 means no augmentation")


def parse_model_params(parser):
    parser.add_argument(
        "--framework_backbone",
        type=str,
        default="tensil_model",
        help="wich module should we use",
    )

    # usefull only for pytorch

    parser.add_argument(
        "--device-pytorch",
        type=str,
        default="cuda:0",
        help="for pytorch only. Device on wich the backbone will be run",
    )

    parser.add_argument("--backbone-type", default="easy-resnet12-cifar", help="model to load")

    # only usefull for the pynk
    parser.add_argument(
        "--path_bit",
        default="/home/xilinx/jupyter_notebooks/l20leche/base_tensil_hdmi.bit",
        type=str,
    )
    parser.add_argument(
        "--path_tmodel",
        default="/home/xilinx/resnet12_32_32_small_onnx_pynqz1.tmodel",
        type=str,
    )

    # only usefull for onnx
    parser.add_argument(
        "--path-onnx", default="weight/resnet12_32_32_64.onnx", type=str
    )
    # only usefull for pytorch
    parser.add_argument(
        "--path-pytorch-weight", default=None, type=str
    )

    # classification head
    parser.add_argument("--classifier_type", default="ncm", type=str)
    parser.add_argument("--number_neiboors", default=5, type=int)


def parse_args_demonstration(parser):
    parser.add_argument("--camera-specification", type=str, default="0")
    parser.add_argument("--no-display", action="store_true")
    parser.add_argument("--save-video", action="store_true")
    parser.add_argument("--video-format", type=str, default="DIVX")
    parser.add_argument("--max_number_of_frame", type=int)
    parser.add_argument("--use-saved-sample", action="store_true")
    parser.add_argument("--path_shots_video", type=str, default="data/catvsdog")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--button-keyboard", default="keyboard")


def process_arguments(args):
    """
    process relative to both demo and cifar evaluation
    """

    if args.framework_backbone == "pytorch":

        # backbone arguments :
        args.backbone_specs = {
            "type": args.framework_backbone,
            "device": args.device_pytorch,
            "model_name": args.backbone_type,
        }

        #weights hardcoded for convinience

        if args.path_pytorch_weight is None:
            
            if args.backbone_type == "easy-resnet12-small-cifar":
                args.backbone_specs["weight"] = "weight/smallcifar1.pt1"
            elif args.backbone_type == "easy-resnet12-cifar":
                args.backbone_specs["weight"] = "weight/cifar1.pt1"
            elif args.backbone_type == "easy-resnet12-tiny-cifar":
                args.backbone_specs["weight"] = "weight/tinycifar1.pt1"
            else:
                raise UserWarning(
                    f"weights for {args.backbone_type} is not hardcoded, provide the path yourself or check name validity"
                )
        else:
            args.backbone_specs["weight"]=args.path_pytorch_weight
        print(args.backbone_specs)

    elif args.framework_backbone == "tensil_model":
        # backbone arguments :
        import Overlay

        args.overlay = Overlay(args.path_bit)
        args.backbone_specs = {
            "type": args.framework_backbone,
            "overlay": args.overlay,
            "path_tmodel": args.path_tmodel,
        }
    elif args.framework_backbone == "onnx":
        args.backbone_specs = {
            "type": args.framework_backbone,
            "path_onnx": args.path_onnx,
        }

    if args.framework_backbone == "pynk":
        print("adding path to local variable")
        sys.path.append("/home/xilinx")
        sys.path.append("/home/xilinx/jupyter_notebooks/l20leche")
        sys.path.append("/usr/local/lib/python3.8/dist-packages")
        sys.path.append("/root/.ipython")
        sys.path.append(
            "/usr/local/share/pynq-venv/lib/python3.8/site-packages/IPython/extensions"
        )
        sys.path.append("/usr/lib/python3/dist-packages")
        sys.path.append("/usr/local/share/pynq-venv/lib/python3.8/site-packages")
        sys.path.append("/usr/lib/python3.8/dist-packages")
        # backbone arguments :
        args.backbone_specs = {
            "type": args.framework_backbone,
            "path_bit": args.path_bit,
            "path_tmodel": args.path_tmodel,
        }
    elif args.framework_backbone == "onnx":
        args.backbone_specs = {
            "type": args.framework_backbone,
            "path_onnx": args.path_onnx,
        }

    # classifier arguments
    args.classifier_specs = {"model_name": args.classifier_type}

    if args.classifier_type == "knn":
        args.classifier_specs["kwargs"] = {"number_neighboors": args.number_neiboors}


def process_args_evaluation(args):
    process_arguments(args)
    args.dataset_path = os.path.join(os.getcwd(), args.dataset_path)
    return args


def get_args_evaluation():
    parser = argparse.ArgumentParser(
        description="""
        Launch the evaluation of the dataset
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # specifics args
    parse_evaluation_args(parser)
    parse_model_params(parser)

    args = parser.parse_args()
    process_args_evaluation(args)

    print("input args : ", args)
    return args


def process_args_demo(args):
    process_arguments(args)
    ### process remaining arguments

    # resolution
    if len(args.resolution_input) == 1:

        res_x = args.resolution_input[0]
        args.resolution_input = (res_x, res_x)
    args.resolution_input = tuple(args.resolution_input)

    if args.camera_specification == "None":
        args.camera_specification = None
    else:
        try:
            args.camera_specification = int(args.camera_specification)
        except:
            print("using a video file")

    print("input args : ", args)
    return args


def get_args_demo():

    parser = argparse.ArgumentParser(
        description="""
        Launch the evaluation of the dataset
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # specifics args
    parse_args_demonstration(parser)
    parse_model_params(parser)

    args = parser.parse_args()
    print("input args : ", args)
    args = process_args_demo(args)
    return args


# print(args.dataset_path)

"""
General utility methods
"""
import os
import argparse
import datetime
from shutil import copyfile

from hparams import Hparams

def initialize_session(mode):
    """Helper method for initializing a chatbot training session 
    by loading the model dir from command line args and reading the hparams in

    Args:
        mode: "train" or "chat"
    """
    parser = argparse.ArgumentParser("Train a chatbot model" if mode == "train" else "Chat with a trained chatbot model")
    if mode == "train":
        ex_group = parser.add_mutually_exclusive_group(required=True)
        ex_group.add_argument("--datasetdir", "-d", help="Path structured as datasets/dataset_name. A new model will be trained using the dataset contained in this directory.")
        ex_group.add_argument("--checkpointfile", "-c", help="Path structured as 'models/dataset_name/model_name/checkpoint_name.ckpt'. Training will resume from the selected checkpoint. The hparams.json file should exist in the same directory as the checkpoint.")
    
    
    elif mode == "chat":
        #parser.add_argument("checkpointfile", help="Path structured as 'models/dataset_name/model_name/checkpoint_name.ckpt'. The hparams.json file and the vocabulary file(s) should exist in the same directory as the checkpoint.")
        parser.add_argument("datasets/cornell_movie_dialog/trained_model_v1/best_weights_training.ckpt", help="Path structured as 'models/dataset_name/model_name/checkpoint_name.ckpt'. The hparams.json file and the vocabulary file(s) should exist in the same directory as the checkpoint.")
    
    else:
        raise ValueError("Unsupported session mode. Choose 'train' or 'chat'.")
    args = parser.parse_args()
    
    #Make sure script was run in the correct working directory
    models_dir = "models"
    datasets_dir = "datasets"
    if not os.path.isdir(models_dir) or not os.path.isdir(datasets_dir):
        raise NotADirectoryError("Cannot find models directory 'models' and datasets directory 'datasets' within working directory '{0}'. Make sure to set the working directory to the chatbot root folder."
                                    .format(os.getcwd()))

    if mode == "train" and args.datasetdir:
        #Make sure dataset exists
        dataset_dir = os.path.relpath(args.datasetdir)
        if not os.path.isdir(dataset_dir):
            raise NotADirectoryError("Cannot find dataset directory '{0}'".format(os.path.realpath(dataset_dir)))
        #Create the new model directory
        dataset_name = os.path.basename(dataset_dir)
        model_dir = os.path.join("models", dataset_name, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(model_dir, exist_ok=True)
        copyfile("hparams.json", os.path.join(model_dir, "hparams.json"))
        checkpoint = None
    elif args.checkpointfile:
        # 학습 과정에서 만들어진 체크포인트와 하이퍼파라미터 값이 있어야 됨
        checkpoint_filepath = os.path.relpath(args.checkpointfile)
        if not os.path.isfile(checkpoint_filepath + ".meta"): #파일이 없다면
            raise FileNotFoundError("The checkpoint file '{0}' was not found.".format(os.path.realpath(checkpoint_filepath))) #파일 없다고 출력
        # 모델 디렉토리에서 체크포인트 값 가져오기
        checkpoint = os.path.basename(checkpoint_filepath) 
        model_dir = os.path.dirname(checkpoint_filepath)
        dataset_name = os.path.basename(os.path.dirname(model_dir))
        dataset_dir = os.path.join(datasets_dir, dataset_name)
    else:
        raise ValueError("Invalid arguments. Use --help for proper usage.")

    #Load the hparams from file
    hparams_filepath = os.path.join(model_dir, "hparams.json")
    hparams = Hparams.load(hparams_filepath)

    return dataset_dir, model_dir, hparams, checkpoint #데이터와 모델 디렉토리, 하이퍼파라미터값, 체크포인트 값 리턴(결과로 나옴)
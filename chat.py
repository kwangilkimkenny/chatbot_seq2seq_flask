"""
Script for chatting with a trained chatbot model
"""
import datetime
import os
from os import path
import argparse
import general_utils
import chat_command_handler
from chat_settings import ChatSettings
from chatbot_model import ChatbotModel
from vocabulary import Vocabulary
from hparams import Hparams


# datasets/cornell_movie_dialog/trained_model_v1/best_weights_training.ckpt

def chat_start(data):

    #Read the hyperparameters and configure paths  하이퍼파라미터 설정값을 읽어온다.
    # parser = argparse.ArgumentParser()
    # parser.add_argument("./datasets/cornell_movie_dialog/trained_model_v1/best_weights_training.ckpt", help="Path structured as 'models/dataset_name/model_name/checkpoint_name.ckpt'. The hparams.json file and the vocabulary file(s) should exist in the same directory as the checkpoint.")
    # args = parser.parse_args()
    # print('args:', args)
    
    #Make sure script was run in the correct working directory
    #models_dir = "models"
    models_dir = "./datasets/cornell_movie_dialog/trained_model_v1"
    datasets_dir = "./datasets"
    if not os.path.isdir(models_dir) or not os.path.isdir(datasets_dir):
        raise NotADirectoryError("Cannot find models directory 'models' and datasets directory 'datasets' within working directory '{0}'. Make sure to set the working directory to the chatbot root folder."
                                    .format(os.getcwd()))


    # 학습 과정에서 만들어진 체크포인트와 하이퍼파라미터 값이 있어야 됨
    #checkpoint_filepath = os.path.relpath(args.checkpointfile)
    checkpoint_filepath = os.path.relpath('./datasets/cornell_movie_dialog/trained_model_v1/best_weights_training.ckpt')
    if not os.path.isfile(checkpoint_filepath + ".meta"): #파일이 없다면
        raise FileNotFoundError("The checkpoint file '{0}' was not found.".format(os.path.realpath(checkpoint_filepath))) #파일 없다고 출력
    # 모델 디렉토리에서 체크포인트 값 가져오기
    checkpoint = os.path.basename(checkpoint_filepath) 
    model_dir = os.path.dirname(checkpoint_filepath)
    dataset_name = os.path.basename(os.path.dirname(model_dir))
    dataset_dir = os.path.join(datasets_dir, dataset_name)


    #Load the hparams from file
    hparams_filepath = os.path.join(model_dir, "hparams.json")
    hparams = Hparams.load(hparams_filepath)

    # _, model_dir, hparams, checkpoint = general_utils.initialize_session("chat")

    #Load the vocabulary
    print()
    print ("Loading vocabulary...")
    if hparams.model_hparams.share_embedding:
        shared_vocab_filepath = path.join(model_dir, Vocabulary.SHARED_VOCAB_FILENAME)
        input_vocabulary = Vocabulary.load(shared_vocab_filepath)
        output_vocabulary = input_vocabulary
    else:
        input_vocab_filepath = path.join(model_dir, Vocabulary.INPUT_VOCAB_FILENAME)
        input_vocabulary = Vocabulary.load(input_vocab_filepath)
        output_vocab_filepath = path.join(model_dir, Vocabulary.OUTPUT_VOCAB_FILENAME)
        output_vocabulary = Vocabulary.load(output_vocab_filepath)

    #Create the model
    print ("Initializing model...")
    print()
    with ChatbotModel(mode = "infer",
                    model_hparams = hparams.model_hparams,
                    input_vocabulary = input_vocabulary,
                    output_vocabulary = output_vocabulary,
                    model_dir = model_dir) as model:

        #Load the weights
        print()
        print ("Loading model weights...")
        model.load(checkpoint)

        # Setting up the chat
        chatlog_filepath = path.join(model_dir, "chat_logs", "chatlog_{0}.txt".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
        chat_settings = ChatSettings(hparams.inference_hparams)
        chat_command_handler.print_commands()

        question  = data

        #If it is not a command (it is a question), pass it on to the chatbot model to get the answer
        question_with_history, answer = model.chat(question, chat_settings)
        
        #Print the answer or answer beams and log to chat log
        if chat_settings.show_question_context:
            print("Question with history (context): {0}".format(question_with_history))
        
        if chat_settings.show_all_beams:
            for i in range(len(answer)):
                print("ChatBot (Beam {0}): {1}".format(i, answer[i]))
        else:
            print("ChatBot: {0}".format(answer))
            result = format(answer)
            
        print()
        
        if chat_settings.inference_hparams.log_chat:
            chat_command_handler.append_to_chatlog(chatlog_filepath, question, answer)

    return result



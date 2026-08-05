import json

repos = [
    {
        "full_name": "dogeplusplus/cat-alan",
        "html_url": "https://github.com/dogeplusplus/cat-alan",
        "description": "Audio classification of domestic cats sounds (hungry, angry, purring, etc) using raw waveforms. PyTorch implementation of M5 architecture.",
        "stargazers_count": 23,
        "language": "Python",
        "topics": [],
        "updated_at": "2022-01-19",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "meow", "sound", "classification"]
    },
    {
        "full_name": "1fmusic/Audio_cat_dog_classification",
        "html_url": "https://github.com/1fmusic/Audio_cat_dog_classification",
        "description": "Classification of WAV files from cats and dogs",
        "stargazers_count": 21,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2017-12-02",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "dog", "audio", "classification"]
    },
    {
        "full_name": "CrispenGari/animal-sound-classification",
        "html_url": "https://github.com/CrispenGari/animal-sound-classification",
        "description": "A simple artificial neural network model using deep learning and torch-audio to classify cats and dog sounds.",
        "stargazers_count": 8,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2022-01-25",
        "is_pet_sound_related": True,
        "match_keywords": ["animal", "sound", "cat", "dog", "classification"]
    },
    {
        "full_name": "EricDavidWells/MeowDetector",
        "html_url": "https://github.com/EricDavidWells/MeowDetector",
        "description": "Doing some Fourier Transform processing on audio signals to detect cat meows",
        "stargazers_count": 4,
        "language": "Python",
        "topics": [],
        "updated_at": "2019-02-04",
        "is_pet_sound_related": True,
        "match_keywords": ["meow", "detector", "audio", "cat"]
    },
    {
        "full_name": "JoeDelK/DOMESTIC-CATS-SOUND-CLASSIFICATION-USING-DEEP-LEARNING",
        "html_url": "https://github.com/JoeDelK/DOMESTIC-CATS-SOUND-CLASSIFICATION-USING-DEEP-LEARNING",
        "description": "Domestic cats are animals able to vocalise a wide range of sounds with different and distinguished meanings. Recognising these sounds can help understand cat behaviour.",
        "stargazers_count": 4,
        "language": None,
        "topics": [],
        "updated_at": "2020-10-28",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "sound", "classification", "deep learning"]
    },
    {
        "full_name": "graceugochinneji/Audio-Identification-and-Categorization",
        "html_url": "https://github.com/graceugochinneji/Audio-Identification-and-Categorization",
        "description": "Audio sound classification using deep learning techniques including cat/dog sound identification.",
        "stargazers_count": 3,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2022-03-30",
        "is_pet_sound_related": True,
        "match_keywords": ["audio", "cat", "dog", "identification"]
    },
    {
        "full_name": "antoszy/CatCom",
        "html_url": "https://github.com/antoszy/CatCom",
        "description": "Project aim is to extend intercom capabilities with cat meowing detection. Raspberry Pi zero is used to achieve that.",
        "stargazers_count": 2,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2024-02-13",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "meowing", "detection", "raspberry pi"]
    },
    {
        "full_name": "MuhammadHananAsghar/Cat-Sound-Classification-Using-Tensorflow",
        "html_url": "https://github.com/MuhammadHananAsghar/Cat-Sound-Classification-Using-Tensorflow",
        "description": "Cat Sound Classification Using Tensorflow",
        "stargazers_count": 2,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2022-05-14",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "sound", "classification", "tensorflow"]
    },
    {
        "full_name": "Ezuniga13/AI-sound-classification-deep-learning",
        "html_url": "https://github.com/Ezuniga13/AI-sound-classification-deep-learning",
        "description": "Final Metis project: Took wave files from a Kaggle dataset of dogs and cats and built a classification model from scratch using a convolutional neural network.",
        "stargazers_count": 2,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2022-05-02",
        "is_pet_sound_related": True,
        "match_keywords": ["sound", "classification", "cat", "dog", "deep learning"]
    },
    {
        "full_name": "digs1998/Audio-Classification-Cats-and-Dogs",
        "html_url": "https://github.com/digs1998/Audio-Classification-Cats-and-Dogs",
        "description": "Using Simple Machine Learning algorithms to detect Cats and Dogs audio sounds with high accuracies",
        "stargazers_count": 2,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2021-04-11",
        "is_pet_sound_related": True,
        "match_keywords": ["audio", "classification", "cat", "dog"]
    },
    {
        "full_name": "ntakokevin/Audio-Classification-using-Machine-Learning-and-Deep-Learning-Cat-and-Dog-Sound-Detection",
        "html_url": "https://github.com/ntakokevin/Audio-Classification-using-Machine-Learning-and-Deep-Learning-Cat-and-Dog-Sound-Detection",
        "description": "The aim is to use machine learning and deep learning algorithms to classify dog and cat audio.",
        "stargazers_count": 2,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2023-09-13",
        "is_pet_sound_related": True,
        "match_keywords": ["audio", "classification", "cat", "dog", "detection"]
    },
    {
        "full_name": "Mark-Kitur/cats_dog_classification",
        "html_url": "https://github.com/Mark-Kitur/cats_dog_classification",
        "description": "Predicts whether sound is for cat or dog",
        "stargazers_count": 1,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2025-07-21",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "dog", "classification", "sound"]
    },
    {
        "full_name": "mohasbks/dog-cat-sound-classification",
        "html_url": "https://github.com/mohasbks/dog-cat-sound-classification",
        "description": "Deep learning model to classify dog and cat sounds using audio processing.",
        "stargazers_count": 1,
        "language": "Python",
        "topics": [],
        "updated_at": "2025-01-03",
        "is_pet_sound_related": True,
        "match_keywords": ["dog", "cat", "sound", "classification"]
    },
    {
        "full_name": "Charan-Nandarapu/Cat-and-Dog-Audio-Classification",
        "html_url": "https://github.com/Charan-Nandarapu/Cat-and-Dog-Audio-Classification",
        "description": "Audio Deep Learning Classification of sounds of Cats and Dogs Using CNN",
        "stargazers_count": 1,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2022-12-01",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "dog", "audio", "classification", "cnn"]
    },
    {
        "full_name": "youth17000/Audio-classification",
        "html_url": "https://github.com/youth17000/Audio-classification",
        "description": "Audio files with cat/dog sounds and noise; task is to classify which one belongs to cat, dog, or background.",
        "stargazers_count": 1,
        "language": "Python",
        "topics": [],
        "updated_at": "2018-05-03",
        "is_pet_sound_related": True,
        "match_keywords": ["audio", "classification", "cat", "dog"]
    },
    {
        "full_name": "tayden/cat-detector",
        "html_url": "https://github.com/tayden/cat-detector",
        "description": "Detects a tabby cat using pre-trained ResNet-50 deep network and meows at it.",
        "stargazers_count": 1,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2018-01-23",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "detector", "meow"]
    },
    {
        "full_name": "moh12950/Cat-VS-Dog-Detection",
        "html_url": "https://github.com/moh12950/Cat-VS-Dog-Detection",
        "description": "This notebook implements a simple binary audio classification model that can distinguish between dog barks and cat meows",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2025-09-01",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "dog", "detection", "audio", "bark", "meow"]
    },
    {
        "full_name": "JunboWang3/Capstone-Project---AI-controlled-Pet-Feeder",
        "html_url": "https://github.com/JunboWang3/Capstone-Project---AI-controlled-Pet-Feeder",
        "description": "Capstone project integrating pet detection, meow recognition, cat breed classification, weight-based feeding, and behavior prediction",
        "stargazers_count": 0,
        "language": None,
        "topics": [],
        "updated_at": "2025-05-05",
        "is_pet_sound_related": True,
        "match_keywords": ["pet", "meow", "recognition", "cat"]
    },
    {
        "full_name": "Jacobtent/right-meow",
        "html_url": "https://github.com/Jacobtent/right-meow",
        "description": "Cat Vocalization Classification using Deep Learning for Intent Recognition",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2025-12-11",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "vocalization", "classification", "deep learning"]
    },
    {
        "full_name": "fangkuaizhu/cat-sound-recognition",
        "html_url": "https://github.com/fangkuaizhu/cat-sound-recognition",
        "description": "Browser-based cat vocalization emotion recognition. Record or upload cat sounds, get real-time emotion classification across 10 categories.",
        "stargazers_count": 0,
        "language": "HTML",
        "topics": [],
        "updated_at": "2025-05-17",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "sound", "recognition", "vocalization", "emotion"]
    },
    {
        "full_name": "shruti353/AI-Based-Cat-Emotion-Recognition-System-Using-Facial-and-Vocal-Analysis",
        "html_url": "https://github.com/shruti353/AI-Based-Cat-Emotion-Recognition-System-Using-Facial-and-Vocal-Analysis",
        "description": "The system aims to analyze cat emotions through facial expressions and vocalizations using deep learning techniques.",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2025-01-29",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "vocal", "emotion", "recognition"]
    },
    {
        "full_name": "KhutejaX/Cat_Dog-Voice-Recognizer-Model",
        "html_url": "https://github.com/KhutejaX/Cat_Dog-Voice-Recognizer-Model",
        "description": "A machine learning model for audio classification that distinguish between cat and dog vocalizations.",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2025-11-15",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "dog", "voice", "recognizer"]
    },
    {
        "full_name": "kayla-kam/Dogs-v-Cats-Sound-Detector",
        "html_url": "https://github.com/kayla-kam/Dogs-v-Cats-Sound-Detector",
        "description": "I created a model that recognizes the differences between a cat's meow and a dog's barking.",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2023-10-23",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "dog", "sound", "detector", "meow", "bark"]
    },
    {
        "full_name": "Faizi1/pet_emotion_detection",
        "html_url": "https://github.com/Faizi1/pet_emotion_detection",
        "description": "Allows pet owners to understand pet emotions using AI-powered emotion detection, analyzes audio or visual input from pets.",
        "stargazers_count": 0,
        "language": "Python",
        "topics": [],
        "updated_at": "2025-06-21",
        "is_pet_sound_related": True,
        "match_keywords": ["pet", "emotion", "detection"]
    },
    {
        "full_name": "Fadhilahgusti/CatSound",
        "html_url": "https://github.com/Fadhilahgusti/CatSound",
        "description": "Cat Sounds Classification",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2022-11-22",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "sound", "classification"]
    },
    {
        "full_name": "lievcin/sound_classifier_qmul",
        "html_url": "https://github.com/lievcin/sound_classifier_qmul",
        "description": "Cats and dogs sounds classification challenge",
        "stargazers_count": 0,
        "language": "Python",
        "topics": [],
        "updated_at": "2021-10-13",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "dog", "sound", "classifier"]
    },
    {
        "full_name": "MarkusJu233/cat-meow",
        "html_url": "https://github.com/MarkusJu233/cat-meow",
        "description": "Detect cat's sound for classification",
        "stargazers_count": 0,
        "language": "Python",
        "topics": [],
        "updated_at": "2025-07-13",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "meow", "sound", "classification"]
    },
    {
        "full_name": "oumarkouf/CatDogSoundsClassification",
        "html_url": "https://github.com/oumarkouf/CatDogSoundsClassification",
        "description": "Two models to classify a sound as Dog or Cat",
        "stargazers_count": 0,
        "language": None,
        "topics": [],
        "updated_at": "2019-05-19",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "dog", "sounds", "classification"]
    },
    {
        "full_name": "tomk23/Cat-and-dog-sound-classification",
        "html_url": "https://github.com/tomk23/Cat-and-dog-sound-classification",
        "description": "Cat and dog sound classification using Neural Network",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2021-01-27",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "dog", "sound", "classification"]
    },
    {
        "full_name": "aljinovic-ante/Keras-Sound-Classification",
        "html_url": "https://github.com/aljinovic-ante/Keras-Sound-Classification",
        "description": "Keras-based classification to distinguish between dog and cat sounds",
        "stargazers_count": 0,
        "language": "Python",
        "topics": [],
        "updated_at": "2021-03-28",
        "is_pet_sound_related": True,
        "match_keywords": ["sound", "classification", "cat", "dog", "keras"]
    },
    {
        "full_name": "Grawikos/Cat-Sound-Classification",
        "html_url": "https://github.com/Grawikos/Cat-Sound-Classification",
        "description": "Cat Sound Classification - Data Analysis project",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2025-01-25",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "sound", "classification"]
    },
    {
        "full_name": "Harkhymadhe/cat-sound-classification",
        "html_url": "https://github.com/Harkhymadhe/cat-sound-classification",
        "description": "Cat sound classification project",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2022-06-12",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "sound", "classification"]
    },
    {
        "full_name": "iam-stanis/dog-cat-sound-classification",
        "html_url": "https://github.com/iam-stanis/dog-cat-sound-classification",
        "description": "Classificate cats and dogs sounds using CNN model by Tensorflow",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2021-09-13",
        "is_pet_sound_related": True,
        "match_keywords": ["dog", "cat", "sound", "classification", "cnn"]
    },
    {
        "full_name": "risydamftr/Cat_Dog_Sound_Classification",
        "html_url": "https://github.com/risydamftr/Cat_Dog_Sound_Classification",
        "description": "Cat Dog Sound Classification using CNN. The dataset available on Kaggle consists of many wav files.",
        "stargazers_count": 0,
        "language": "Python",
        "topics": [],
        "updated_at": "2025-02-14",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "dog", "sound", "classification", "cnn"]
    },
    {
        "full_name": "Ayaabdelmoneam/Cat-Dog-Sound-Classification",
        "html_url": "https://github.com/Ayaabdelmoneam/Cat-Dog-Sound-Classification",
        "description": "Cat and dog sound classification project",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2024-08-29",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "dog", "sound", "classification"]
    },
    {
        "full_name": "CyberMeteor/CatSoundClassificationPaper.github.io",
        "html_url": "https://github.com/CyberMeteor/CatSoundClassificationPaper.github.io",
        "description": "This is the website of Cat Sound Classification Project Paper",
        "stargazers_count": 0,
        "language": "HTML",
        "topics": [],
        "updated_at": "2024-05-02",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "sound", "classification", "paper"]
    },
    {
        "full_name": "zzeyne/Animal_sound_classification",
        "html_url": "https://github.com/zzeyne/Animal_sound_classification",
        "description": "Animal sound classification project using audio data from cats, dogs, lambs, and roosters.",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2025-12-20",
        "is_pet_sound_related": True,
        "match_keywords": ["animal", "sound", "classification", "cat", "dog"]
    },
    {
        "full_name": "akpinaralper/DeepLearning_Cat-Dog-Sound-Classification",
        "html_url": "https://github.com/akpinaralper/DeepLearning_Cat-Dog-Sound-Classification",
        "description": "Kedi ve kopek seslerini MFCC ve CNN kullanarak siniflandiran bir derin ogrenme uygulamasi (Cat-Dog sound classification with MFCC+CNN).",
        "stargazers_count": 0,
        "language": "Python",
        "topics": ["machine-learning", "deep-learning", "cnn", "pytorch", "mfcc"],
        "updated_at": "2025-12-28",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "dog", "sound", "classification", "deep learning"]
    },
    {
        "full_name": "OrbsVerse/CaVoLab-cat-sound-classification-system",
        "html_url": "https://github.com/OrbsVerse/CaVoLab-cat-sound-classification-system",
        "description": "CaVoLab cat sound classification system",
        "stargazers_count": 0,
        "language": "Python",
        "topics": [],
        "updated_at": "2025-12-01",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "sound", "classification"]
    },
    {
        "full_name": "Azazurrehman13/Cats-and-Dogs-Audio-Classification",
        "html_url": "https://github.com/Azazurrehman13/Cats-and-Dogs-Audio-Classification",
        "description": "Implements a deep learning model to classify cat and dog sounds using mel spectrograms, built with PyTorch",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2025-08-05",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "dog", "audio", "classification", "pytorch"]
    },
    {
        "full_name": "shankongar/Cats-And-Dogs-Audio-Classification",
        "html_url": "https://github.com/shankongar/Cats-And-Dogs-Audio-Classification",
        "description": "Systematic study of cat/dog audio classification using machine learning and deep learning methods - compares 9 ML algorithms and 8 neural approaches",
        "stargazers_count": 0,
        "language": "Python",
        "topics": [],
        "updated_at": "2025-06-26",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "dog", "audio", "classification"]
    },
    {
        "full_name": "basmllaakram22/Speech-Recognition-updated",
        "html_url": "https://github.com/basmllaakram22/Speech-Recognition-updated",
        "description": "Classification project with deep learning to classify the audios of dogs and cats",
        "stargazers_count": 0,
        "language": None,
        "topics": [],
        "updated_at": "2024-08-29",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "dog", "speech", "recognition"]
    },
    {
        "full_name": "gauravit131/AUDIO_CLASSIFICATION_SYSTEM",
        "html_url": "https://github.com/gauravit131/AUDIO_CLASSIFICATION_SYSTEM",
        "description": "Build an AI model that classifies audio clips as either a cat or dog sound using Deep Learning techniques",
        "stargazers_count": 0,
        "language": None,
        "topics": [],
        "updated_at": "2025-06-15",
        "is_pet_sound_related": True,
        "match_keywords": ["audio", "classification", "cat", "dog"]
    },
    {
        "full_name": "Ujjwal9302/dog_bark_vs_cat_meow_classifier",
        "html_url": "https://github.com/Ujjwal9302/dog_bark_vs_cat_meow_classifier",
        "description": "Deep Learning audio classification project using Mel Spectrograms and CNNs to classify Dog Barks vs Cat Meows",
        "stargazers_count": 0,
        "language": "Python",
        "topics": [],
        "updated_at": "2025-05-22",
        "is_pet_sound_related": True,
        "match_keywords": ["dog", "bark", "cat", "meow", "classifier"]
    },
    {
        "full_name": "PraatikMadekar/Dogs-Cats-Classifier",
        "html_url": "https://github.com/PraatikMadekar/Dogs-Cats-Classifier",
        "description": "A Dog-Cat classifier using an RNN for audio classification task to distinguish between sounds of cats and dogs",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2025-10-09",
        "is_pet_sound_related": True,
        "match_keywords": ["dog", "cat", "classifier", "audio", "rnn"]
    },
    {
        "full_name": "senaa123/PawCare",
        "html_url": "https://github.com/senaa123/PawCare",
        "description": "A real-time intelligent system that detects, recognizes individual cats, analyzes their behavior and sounds, and automates alerts and feeding.",
        "stargazers_count": 0,
        "language": "Python",
        "topics": [],
        "updated_at": "2025-07-08",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "sound", "detect", "recognize"]
    },
    {
        "full_name": "ivy-mondal/meow_or_woof",
        "html_url": "https://github.com/ivy-mondal/meow_or_woof",
        "description": "Meow-Woof detector AI",
        "stargazers_count": 0,
        "language": None,
        "topics": [],
        "updated_at": "2024-09-26",
        "is_pet_sound_related": True,
        "match_keywords": ["meow", "woof", "detector"]
    },
    {
        "full_name": "manheima/MeowDetector",
        "html_url": "https://github.com/manheima/MeowDetector",
        "description": "Uses Coral Dev Board Micro to detect Meows",
        "stargazers_count": 0,
        "language": "C++",
        "topics": [],
        "updated_at": "2025-04-26",
        "is_pet_sound_related": True,
        "match_keywords": ["meow", "detector"]
    },
    {
        "full_name": "hulsey314/MeowX",
        "html_url": "https://github.com/hulsey314/MeowX",
        "description": "Sound detector and logger",
        "stargazers_count": 0,
        "language": "Python",
        "topics": [],
        "updated_at": "2021-01-19",
        "is_pet_sound_related": True,
        "match_keywords": ["sound", "detector", "meow"]
    },
    {
        "full_name": "knovvX/513_Project",
        "html_url": "https://github.com/knovvX/513_Project",
        "description": "Training a cat translation tool for Cat Meow Classification dataset",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2025-05-30",
        "is_pet_sound_related": True,
        "match_keywords": ["cat", "meow", "classification"]
    },
    {
        "full_name": "himanshkr03/MiNi_Wildlife-Identification-Using-Audio_ML",
        "html_url": "https://github.com/himanshkr03/MiNi_Wildlife-Identification-Using-Audio_ML",
        "description": "Python-based audio classification project using deep learning for wildlife sound recognition.",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": ["deep", "librosa", "soundrecognition"],
        "updated_at": "2025-01-03",
        "is_pet_sound_related": True,
        "match_keywords": ["audio", "classification", "animal", "sound", "recognition"]
    }
]

# Sort by stars descending
repos.sort(key=lambda x: x["stargazers_count"], reverse=True)

# Print summary
print(f"Total repos: {len(repos)}")
for r in repos:
    print(f"  {r['stargazers_count']:>3}* {r['full_name']} ({r['language']})")

# Write JSON
with open(r"D:\mydoc\workskill\code\cat-meow-search\result.json", "w", encoding="utf-8") as f:
    json.dump(repos, f, ensure_ascii=False, indent=2)

print("\nJSON written to code/cat-meow-search/result.json")

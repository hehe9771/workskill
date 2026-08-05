import json

# All repos collected from 3 searches (already filtered: excluding image-only repos)
all_repos = []

# Search 1: animal audio classification deep learning in:name,description
s1 = [
    {
        "full_name": "rawbeen248/audio_classification_finetuning",
        "html_url": "https://github.com/rawbeen248/audio_classification_finetuning",
        "description": "This project focuses on the classification of animal sounds using deep learning. The core idea is to utilize audio processing techniques and a fine-tuned version of the hubert-base-ls960 model to accurately classify different animal sounds.",
        "stargazers_count": 10,
        "language": "Python",
        "topics": [],
        "updated_at": "2026-05-29T22:58:42Z"
    },
    {
        "full_name": "CrispenGari/animal-sound-classification",
        "html_url": "https://github.com/CrispenGari/animal-sound-classification",
        "description": "this is a simple artificial neural network model using deep learning and torch-audio to classify cats and dog sounds.",
        "stargazers_count": 8,
        "language": "Jupyter Notebook",
        "topics": ["artificial-intelligence", "artificial-neural-networks", "audio", "audio-processing", "deep-learning", "deep-neural-networks", "machine-learning", "python", "pytorch", "rnn", "torchaudio"],
        "updated_at": "2025-07-16T05:19:19Z"
    },
    {
        "full_name": "anamika2507/Automated-Classification-of-Animal-Vocalization-into-Estrus-and-Non-Estrus-Phase",
        "html_url": "https://github.com/anamika2507/Automated-Classification-of-Animal-Vocalization-into-Estrus-and-Non-Estrus-Phase",
        "description": "Extraction of important features from the audio data was done, creating mel-spectrograms for the same, and utilising different machine learning and neural network models to perform an analysis for the same. CNN, RNN, CRNN and ResNet34 models were explored for the analysis of deep learning models in animal vocalization classification",
        "stargazers_count": 1,
        "language": "Python",
        "topics": [],
        "updated_at": "2024-01-01T07:40:11Z"
    },
    {
        "full_name": "Satyasri04/animal-species-sound-recognition",
        "html_url": "https://github.com/Satyasri04/animal-species-sound-recognition",
        "description": "An AI-based Animal Species Recognition System that classifies animal sounds using deep learning. The system leverages YAMNet for feature extraction and a DCNN model for multi-class classification, with a Flask-based web interface for real-time audio prediction.",
        "stargazers_count": 1,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2026-06-22T05:25:16Z"
    },
    {
        "full_name": "harshbrahamwanshi/Animal-Sound-Classification-Using-MFCC-Features-and-Deep-Neural-Networks",
        "html_url": "https://github.com/harshbrahamwanshi/Animal-Sound-Classification-Using-MFCC-Features-and-Deep-Neural-Networks",
        "description": "Machine Learning Lab Audio Dataset",
        "stargazers_count": 0,
        "language": "HTML",
        "topics": [],
        "updated_at": "2026-04-07T14:11:56Z"
    },
    {
        "full_name": "smadan755/DeepAudioNet",
        "html_url": "https://github.com/smadan755/DeepAudioNet",
        "description": "Deep Learning-Based Spectrogram Analysis for Animal Sound Classification. This repository contains the implementation of a Convolutional Neural Network (CNN) for classifying animal sounds using spectrogram analysis.",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2024-12-12T05:48:02Z"
    },
    {
        "full_name": "GabrielBertolini/Sound-Classification-Animals",
        "html_url": "https://github.com/GabrielBertolini/Sound-Classification-Animals",
        "description": "Deep learning project for animal sound classification using CNNs and MFCC audio features (Python, TensorFlow, Librosa).",
        "stargazers_count": 0,
        "language": "HTML",
        "topics": [],
        "updated_at": "2026-03-09T20:06:50Z"
    },
    {
        "full_name": "gauravit131/AUDIO_CLASSIFICATION_SYSTEM",
        "html_url": "https://github.com/gauravit131/AUDIO_CLASSIFICATION_SYSTEM",
        "description": "Build an AI model that classifies audio clips as either a cat or dog sound using Deep Learning techniques. Differentiating animal sounds helps in Pet activity monitoring, Smart home automation (e.g., notify when pet barks/meows), Animal welfare applications, Voice-enabled pet interaction systems",
        "stargazers_count": 0,
        "language": None,
        "topics": [],
        "updated_at": "2026-06-14T06:09:20Z"
    },
    {
        "full_name": "damar-iswara/mel-spectrogram-animal-sound-classification",
        "html_url": "https://github.com/damar-iswara/mel-spectrogram-animal-sound-classification",
        "description": "This project leverages deep learning to classify different animal species based on their acoustic signals. By transforming raw 1D audio waveforms into 2D Mel-Spectrogram images, the project utilizes a Convolutional Neural Network (CNN) to effectively extract audio features and recognize distinct animal sound patterns with high accuracy.",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2026-02-27T18:59:40Z"
    },
    {
        "full_name": "immy-1/Deep-Learning-Approaches-for-Acoustic-Classification-of-Pipistrellus-pipistrellus-behavioural-calls",
        "html_url": "https://github.com/immy-1/Deep-Learning-Approaches-for-Acoustic-Classification-of-Pipistrellus-pipistrellus-behavioural-calls",
        "description": "This study evaluates whether deep neural networks can classify three behavioural states of Pipistrellus pipistrellus - search, feeding buzz, and social calls - using public PAM audio from Bat Detective, Xeno-canto, and the Animal Sound Archive.",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2025-10-30T22:22:22Z"
    },
    {
        "full_name": "Yaldram69/Animal-Sound-Recognition",
        "html_url": "https://github.com/Yaldram69/Animal-Sound-Recognition",
        "description": "Animal Sound Recognition is an audio classification project that identifies animal sounds from recorded audio using machine learning/deep learning. It includes a real-time microphone-based prediction pipeline (with preprocessing like noise reduction) and a training pipeline for learning animal classes from labeled datasets.",
        "stargazers_count": 0,
        "language": "Python",
        "topics": [],
        "updated_at": "2026-02-25T19:00:41Z"
    },
]

# Search 2: cat dog sound classification deep learning in:name,description
# Excluded: Gaurav-1213/CNN-Project-of-Cat-and-Dog-image-Classification-By-Keras (image, not audio)
# Excluded: Soumyatrivedi3099/Neuralnetwork (image, not audio)
s2 = [
    {
        "full_name": "ntakokevin/Audio-Classification-using-Machine-Learning-and-Deep-Learning-Cat-and-Dog-Sound-Detection",
        "html_url": "https://github.com/ntakokevin/Audio-Classification-using-Machine-Learning-and-Deep-Learning-Cat-and-Dog-Sound-Detection",
        "description": "The aim is to use machine learning and deep learning algorithms to classify dog and cat audio.",
        "stargazers_count": 2,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2025-03-03T09:18:28Z"
    },
    {
        "full_name": "mohasbks/dog-cat-sound-classification",
        "html_url": "https://github.com/mohasbks/dog-cat-sound-classification",
        "description": "Deep learning model to classify dog and cat sounds using audio processing.",
        "stargazers_count": 1,
        "language": "Python",
        "topics": [],
        "updated_at": "2025-02-19T14:41:14Z"
    },
    {
        "full_name": "Charan-Nandarapu/Cat-and-Dog-Audio-Classification",
        "html_url": "https://github.com/Charan-Nandarapu/Cat-and-Dog-Audio-Classification",
        "description": "Audio Deep Learning Classification of sounds of Cats and Dogs Using CNN",
        "stargazers_count": 1,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2023-02-01T17:29:52Z"
    },
    {
        "full_name": "akpinaralper/DeepLearning_Cat-Dog-Sound-Classification",
        "html_url": "https://github.com/akpinaralper/DeepLearning_Cat-Dog-Sound-Classification",
        "description": "Kedi ve kopek seslerini MFCC ve CNN kullanarak siniflandiran bir derin ogrenme uygulamasi. (Cat and dog sound classification using MFCC and CNN)",
        "stargazers_count": 0,
        "language": "Python",
        "topics": ["audio-classification", "cnn", "deep-learning", "machine-learning", "mfcc", "pytorch"],
        "updated_at": "2025-12-28T13:57:04Z"
    },
    {
        "full_name": "Azazurrehman13/Cats-and-Dogs-Audio-Classification",
        "html_url": "https://github.com/Azazurrehman13/Cats-and-Dogs-Audio-Classification",
        "description": "This repository implements a deep learning model to classify cat and dog sounds using mel spectrograms, built with PyTorch.",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2025-08-05T15:25:01Z"
    },
    {
        "full_name": "KhutejaX/Cat_Dog-Voice-Recognizer-Model",
        "html_url": "https://github.com/KhutejaX/Cat_Dog-Voice-Recognizer-Model",
        "description": "A machine learning model for audio classification that distinguish between cat and dog vocalizations. Audio classification project utilizing MFCCs and a Convolutional Neural Network to identify whether a sound is a cat meow or a dog bark.",
        "stargazers_count": 0,
        "language": "Jupyter Notebook",
        "topics": [],
        "updated_at": "2025-12-08T13:08:05Z"
    },
]

# Search 3: pet sound recognition deep learning in:name,description
s3 = [
    {
        "full_name": "UmeshPrajapati01/Development-of-an-AI-Based-Cat-Emotion-Recognition-System-Using-Facial-and-Vocal-Analysis",
        "html_url": "https://github.com/UmeshPrajapati01/Development-of-an-AI-Based-Cat-Emotion-Recognition-System-Using-Facial-and-Vocal-Analysis",
        "description": "Develop an intelligent system capable of detecting cat emotions using both facial expressions and vocal sounds. The system is designed to help users understand pet behavior through AI-based analysis using deep learning models.",
        "stargazers_count": 1,
        "language": None,
        "topics": [],
        "updated_at": "2026-05-25T07:14:53Z"
    },
]

# Merge all
all_repos = s1 + s2 + s3

# Deduplicate by full_name (keep first occurrence which has higher stars)
seen = set()
deduped = []
for r in all_repos:
    if r["full_name"] not in seen:
        seen.add(r["full_name"])
        deduped.append(r)

# Sort by stars descending
deduped.sort(key=lambda x: (-x["stargazers_count"], x["full_name"]))

# Determine is_cat_dog_related: check name/description/topics for keywords
keywords = ["cat", "dog", "pet", "animal", "bark", "meow"]
for r in deduped:
    text_to_check = (r["full_name"] + " " + (r["description"] or "") + " " + " ".join(r["topics"])).lower()
    r["is_cat_dog_related"] = any(kw in text_to_check for kw in keywords)

print(json.dumps(deduped, ensure_ascii=False, indent=2))

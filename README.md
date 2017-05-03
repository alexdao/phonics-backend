# Phonics Server
Backend for Phonics written in Node.js. Can also be used stand-alone as a series of Python3 scripts to train on and analyze text locally. Optionally uses YOLO, a real-time object detection ML framework for processing images and identifying objects to match with a previously NLP-trained dataset. Interfaces with the Phonics Android app and the Phonics Google Home app.

The following setup and usage instructions have only been tested on MacOS 10.12.4, but they likely also work on other \*nix machines.


## Setup
1. Clone this repo.

2. Make sure you have python3 and pip3 installed. It is recommended to use a virtualenv.

3. Install required python3 modules which are found in `requirements.txt`
```
$pip3 install -r requirements.txt
```

4. Download CoreNLP 3.7.0 from [here](https://stanfordnlp.github.io/CoreNLP/) and place the extracted folder in the root directory of this repo.

## Usage
Run the `main.py` file with the following arguments:
```
$python3 main.py --demo
```
This will open a local web page with a visualization of verb-object analysis. Click on a verb in the swirling globe on the left side to view the objects occurrences with that verb.

This visualization comes from the `app/data/p2.csv` file. A freshly cloned repo comes with a pre-trained csv file on the first chapter of Moby Dick (a duplicate file can be found at `mobydickdata/p2.csv`).

You can also train on arbitrary text using the following command:
```
$python3 main.py --text arbitrary_text.txt
```
This will generate a new `app/data/p2.csv` file that you can then run the above --demo command to see the visualization.

## Optional features
Additionally, we've added a way to reverse the analysis, and show the verb occurrences when given a list of objects. This can be done using the following command:
```
$python3 main.py --nouns app/data/nouns.txt
```

The `nouns.txt` format is simply a list of nouns separated by objects.

### Using the YOLO image analysis framework
You can also use YOLO to identify nouns within an image for analysis with the above optional feature. We've provided a modified version of the YOLO framework in this repo for this purpose.

##### Setup
You will need to download and install the YOLO system with the following commands:
```
git clone https://github.com/pjreddie/darknet
cd darknet
make
```

and also install a pre-trained weight file (256 MB):
```
wget http://pjreddie.com/media/files/yolo.weights
```

##### Usage
Reset the nouns file:
```
$rm app/data/nouns.txt
$touch app/data/nouns.txt
```
Analyze an image (named `out.png`):
```
$./darknet detect cfg/yolo.cfg yolo.weights out.png
```
Match to pre-trained NLP model and display visualization:
```
$cp predictions.png app/data/phonphoto.png
$python3 main.py --nouns app/data/nouns.txt
```

## Clients (Optional)
Google home app can be found [here](https://github.com/alexdao/phonics-google-home-app)

Android app can be found [here](https://github.com/alexdao/phonics-android)

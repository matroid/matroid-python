# Matroid API Python Client

Use our Python client to access the Matroid API for image and video classification.

## Full documentation

Navigate to any detector's page, such as the [Famous Places Detector](https://app.matroid.com/detector/58d010c75bcac50d00ad85ed?tab=api), and click on the "Overview" tab. The "Overview" section contains the full specifications for each REST endpoint.

## Installation

```
pip install matroid
```

You can pass in your API credentials directly to the API client or save them as environment variables where the client will use them automatically. Here is a bash example:

```
nano .bash_profile
```

Inside your `.bash_profile`, add the following lines, replacing the placeholder with the real values from the [API documentation's](https://app.matroid.com/detector/58d010c75bcac50d00ad85ed?tab=api) "Account Info" section

```
export MATROID_CLIENT_ID=PLACEHOLDER
export MATROID_CLIENT_SECRET=PLACEHOLDER
```

Then run `source ~/.bash_profile` on the command line to ensure the environment variables are loaded.

## Example API client usage

```
import matroid
from matroid.client import Matroid

api = Matroid(client_id = 'abc', client_secret = '123')

# List available detectors
detectors_to_use = api.search_detectors()

# Classifying a picture from a URL
logo_classification_result = api.classify_image(detectorId = 'test', url = 'https://app.matroid.com/images/logo2.png', num_results = 5)

# Classifying a picture from a file path
stadium_classification_result = api.classify_image(detectorId = 'test', file = '/Users/matroid/Desktop/stadium.jpg')

# Classifying pictures from multiple file paths
famous_people_results = api.classify_image(detectorId = 'test', file = ['/home/matroid/taylor.png', '/home/matroid/kanye.jpeg'])

# Begin video classification
classifying_video = api.classify_video(detectorId = 'test', file = '/home/matroid/video.mp4')

# Classify YouTube video
classifying_youtube_video = api.classify_video(detectorId = 'test', url = 'https://youtube.com/watch?v=abc')

# Get video results
video_results = api.get_video_results(videoId = classifying_video['videoId'], threshold = 0.3, format = 'json')

# Register stream on Matroid
registered_stream = api.create_stream(options = {})

# Monitor stream
options = {
  'start_time': '2017-06-20T20:56:19.096Z',
  'end_time': '2017-06-21T20:00:00.000Z',
  'thresholds': {
    'cat': 0.5,
    'dog': 0.7
  }
  'endpoint': 'http://mydomain.fake:9000/matroid_detections'
}
monitored_stream = api.monitor_stream(streamId = registered_stream['stream_id'], detectorId = 'test', **options)
# Parameters sent to endpoint: name, detectedAt, detector, screenshotUrl, clipUrl, detections

# Create and train a detector
"""
  zip_file: a zip file containing the images to be used in the detector creation
            the root folder should contain only directories which will become the labels for detection
            each of these directories should contain only a images corresponding to that label
    structure example:
      cat/
        garfield.jpg
        nermal.png
      dog/
        odie.tiff
"""
detector_id = api.create_detector(file = '/home/matroid/catdog.zip', name='my-test-det', detectorType = 'general')['detectorId']
api.finalize_detector(detector_id)

# Check on training progress
api.get_detector_info(detector_id)

# Check your Matroid Credits balance
api.account_info()

# Add feedback to a detector from a local file
feedback = [
  {
    'feedbackType': 'positive',
    'label': 'cat',
    'boundingBox': {
      'top': .1,
      'left': .1,
      'height': .1,
      'width': .1,
     },
   },
  {
    'feedbackType': 'negative',
    'label': 'dog',
    'boundingBox': {
      'top': .2,
      'left': .2,
      'height': .35,
      'width': .35,
     },
   },
]

api.add_feedback(detectorId = 'your-detector-id', feedback = feedback, file = '/Users/matroid/image.png')

# Add feedback to a detector from a URL
url = 'https://app.matroid.com/images/logo2.png'
feedback = [
  {
    'feedbackType': 'positive',
    'label': 'cat',
    'boundingBox': {
      'top': .1,
      'left': .1,
      'height': .1,
      'width': .1,
     },
   },
]

api.add_feedback(detectorId = 'your-detector-id', feedback = feedback, url = url)

# Delete feedback from a detector
api.delete_feedback(feedbackId = 'your-feedback-id', detectorId = 'your-detector-id')
```

## API Response samples

#### Sample detectors listing

```
[
  {
    "detector_name": "cat-dog-47",
    "human_name": "cats vs dogs",
    "labels": ["cat", "dog"],
    "permission_level": "open",
    "owner": "true"
  }
]
```

#### Sample Image Classification

```
{
  "results": [
    {
      "file": {
        "name": "image1.png",
        "url": "https://myimages.1.png",
        "thumbUrl": "https://myimages.1_t.png",
        "filetype": "image/png"
      },
      "predictions": [
        {
          "bbox": {
            "left": 0.7533333333333333,
            "top": 0.4504347826086956,
            "height": 0.21565217391304348,
            "aspectRatio": 1.0434782608695652
          },
          "labels": {
            "cat face": 0.7078468322753906,
            "dog face": 0.29215322732925415
          }
        },
        {
          "bbox": {
            "left": 0.4533333333333333,
            "top": 0.6417391304347826,
            "width": 0.20833333333333334,
            "height": 0.21739130434782608,
            "aspectRatio": 1.0434782608695652
          },
          "labels": {
            "cat face": 0.75759859402753906,
            "dog face": 0.45895322732925415
          }
        }, {
          ...
        }
      ]
    }
  ]
}
```

#### Sample video classification tracking ID

```
{
  "video_id": "58489472ff22bb2d3f95728c"
}
```

#### Sample video classification results

```
{
  "download_progress": 100,
  "classification_progress": 8,
  "status": "Video Download Complete. Classifying Video",
  "label_dict": {"0":"cat","1":"dog"},
  "state": "running",
  "detections": {
       "1.5": [{ "labels": { "0": 0.10 } }],
       "2": [{ "labels": { "0": 0.98, "1": 0.10 } }],
       "5": [{ "labels": { "0": 0.75 } }]
   }
}

{
  "download_progress": 100,
  "classification_progress": 8,
  "status": "Video Download Complete. Classifying Video",
  "label_dict": {"0":"man","1":"woman"},
  "state": "running",
  "detections": {
    "89": [
      {
        "labels": {
          "0": 0.95
        },
        "bbox": {
         "left": 0.2377,
         "top": 0.2021,
         "width": 0.1628,
         "height": 0.3896,
       }
      }
    ],
    "92": [
      {
        "labels": {
          "0": 0.16,
          "2": 0.80
        },
        "bbox": {
          "left": 0.7576,
          "top": 0.2375,
          "width": 0.0597,
          "height": 0.1313,
        }
      },
      {
        "labels": {
          "0": 0.89,
        },
        "bbox": {
          "left": 0.5047,
          "top": 0.1708,
          "width": 0.055,
          "height": 0.1292,
        }
      },
    ]
  }
}
```

#### Sample stream creation

```
{
  "stream_id": "58489472ff22bb2d3f95728c"
}
```

#### Sample stream monitoring

```
{
  "stream_id": "58489472ff22bb2d3f95728c",
  "monitoring_id": "68489472ff22bb2d3f95728c",
}
```

#### Sample detector creation ID

```
{
  "detector_id": "58489472ff22bb2d3f95728c"
}
```

#### Sample detector information and training progress response

```
{
  "detector": {
    "labels": [{
      "label_id": "58471afdc3d3516158d3b441",
      "name": "bread"
    }],
    "state": "training",
    "permission_level": "private",
    "training": {
      "progress": 100,
      "accuracy": 89.9,
      "total_images": 250,
      "queue_position": 0,
      "training_requested_at": "2016-01-01T20:20:13.739Z",
      "estimated_start_time": "2016-01-01T20:21:30.193Z",
      "estimated_time_remaining": 3,
      "estimated_completion_time": "2016-01-01T20:24:30.193Z"
    }
  }
}
```

#### Sample add feedback response

```
{
  "feedback": [
    {
      "id": "58471afdc3d3516158d3b441",
      "label": "cat",
      "feedbackType": "negative",
      "boundingBox": {
        "top": 0.1,
        "left": 0.1,
        "width": 0.73,
        "height": 0.44,
      },
    },
    {
      "id": "58471afdc3d3516158d3b442",
      "label": "cat",
      "feedbackType": "positive",
      "boundingBox": {
        "top": 0.3,
        "left": 0.3,
        "width": 0.13,
        "height": 0.24,
      },
    },
  ]
}
```

#### Sample delete feedback respoonse

```
{
  "feedbackId": ": "58471afdc3d3516158d3b441",
}
```

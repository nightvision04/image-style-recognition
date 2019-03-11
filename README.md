# image-style-recognition

This project uses a scikit pipeline to predict and sort the quality of photos across several metrics, such as:

- Filmic color style
- Modern color style
- Framing style
- Texture and interest
- Geometric interest

It has the ability to detect professional photos with a tolerance of 3-5% and provides a granular score between 0.01 and 1.00 to the user with a variety of sorting options. It is particularily useful for projects who may wish to algorithmically:

- Reject Amatuer Images
- Prioritize Inspiring Images
- Optimize Viewer Engagement
- Optimize Brand Image
- Automatically Promote Attractive Content

# Dependencies

- Python 3.6 (Anaconda)
- Pandas
- Numpy
- Flask
- Javascript
- Opencv-python
- Scikit-learn
- Mysql

# Screenshots

<img src="/snapshots/j1.png" width="680">

The app features an easy-to-use interface where clients can easily drag and drop files to have them analyzed.

<img src="/snapshots/h4.png" width="680">

The site is also customized for an intuitive mobile experience that lets the user quickly curate pictures from their camera.

 
 <img src="/snapshots/h3.png" width="680">
 
 # Machine Learning Pipeline
 
 The pipeline currently combines several nodes of Principal Component Analysis, and Random Forest classifiers in a convoultion design to traverse image data. This allows for the model to stay flexible when handling unique image shapes.
 
Training data is currently around 90,000 samples and applies a broad variance.

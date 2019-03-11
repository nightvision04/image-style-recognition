import numpy as np

def runfilter(img,filter):

    if filter=='grayscale':
        img = grayscale(img)

    if filter=='': # Default
        pass


    return img



def grayscale(img):
    '''expects the img in bgr mode, but will convert to grayscale
    '''

    import cv2

    new_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # uncomment these for higher contrast
    #array_alpha = np.array([2.5])
    #array_beta = np.array([-50.0])

    # add a beta value to every pixel
    #cv2.add(new_img, array_beta, new_img)

    # multiply every pixel value by alpha
    #cv2.multiply(new_img, array_alpha, new_img)


    return new_img

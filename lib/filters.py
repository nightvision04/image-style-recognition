import numpy as np

def runfilter(img,filter):

    if filter=='grayscale_high_contrast':
        img = grayscale_high_contrast(img)

    if filter=='': # Default
        pass


    return img



def grayscale_high_contrast(img):
    '''expects the img in bgr mode, but will convert to grayscale
    '''

    import cv2

    cv2.imshow('oldImage',img)
    new_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    array_alpha = np.array([2.5])
    array_beta = np.array([-50.0])

    # add a beta value to every pixel
    cv2.add(new_img, array_beta, new_img)

    # multiply every pixel value by alpha
    cv2.multiply(new_img, array_alpha, new_img)

    # cv2.imshow('newImage1',new_img)
    #
    #
    # # Close figure window and click on other window
    # # Then press any keyboard key to close all windows
    # closeWindow = -1
    # while closeWindow<0:
    #     closeWindow = cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # This needs to be changed to new grayscale img
    return new_img

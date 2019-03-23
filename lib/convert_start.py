import time
import model_creator as mc





if __name__ == "__main__":


    # # Flush history in db
    # t1 = time.time()
    import convert_flickr
    import convert_lookslikefilm
    # import convert_imgur
    import convert_unsplash
    # t2 = time.time()
    # print("Took {} seconds for training data generation".format(t2-t1))

    # Flush models in db
    t1 = time.time()

    mc.start_model('lookslikefilm','grayscale')
    mc.start_model('lookslikefilm','convolution')
    mc.start_model('unsplash','grayscale')
    mc.start_model('unsplash','convolution')
    t2 = time.time()
    print("Took {} seconds for model generation".format(t2-t1))


import pandas as pd
import numpy as np
import json

def gallery_view_html(image_list,active_curators):

    arr = np.array(image_list)
    df = pd.DataFrame()

    active_curator_score = arr[:,0]

    # For each entry, check the list of active curators,
    # and sum their scores.
    active_curator_score_mod = np.zeros(len(active_curator_score))
    for i in range(len(active_curator_score)):
        score=0
        for key in active_curators:
            score += json.loads(active_curator_score[i])[key]
        active_curator_score_mod[i] = score

    df['active_scores'] = active_curator_score_mod
    df['quality'] = active_curator_score
    df['filepaths'] = arr[:,1]
    df['filepaths_thumb'] = arr[:,2]
    df = df.sort_values(by='quality',ascending=False)
    df = df.drop_duplicates(subset='filepaths', keep="last")

    quality = df['active_scores'].values
    filepaths = df['filepaths'].values
    filepaths_thumb = df['filepaths_thumb'].values

    html= '''
<link rel="stylesheet" href="href="https://cdnjs.cloudflare.com/ajax/libs/ekko-lightbox/5.2.0/ekko-lightbox.min.css">
<div class="container">
<div class="row">
'''


    for i in range(0,len(quality)):


        html+='''

            <a href="'''+str(filepaths[i])+'''" data-toggle="lightbox" data-gallery="gallery" class="col-md-2 v-pad">
              <img src="'''+str(filepaths_thumb[i])+'''" class="img-fluid rounded align-middle vertical-align">
            </a>
            '''

    html+='''
    </div>
    </div>

<script>

$(document).on("click", '[data-toggle="lightbox"]', function(event) {
  event.preventDefault();
  $(this).ekkoLightbox();
});
</script>
        '''

    image_list = [[df['quality'].values[i],
                filepaths[i],
                filepaths_thumb[i]] for i in range(len(quality))]


    return image_list,html

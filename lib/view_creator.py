
import pandas as pd
import numpy as np

def gallery_view_html(session,sort_method):

    obj = session

    arr = np.array(obj)
    df = pd.DataFrame()
    df['quality'] = arr[:,0]
    df['filepaths'] = arr[:,1]
    df['filepaths_thumb'] = arr[:,2]
    df = df.sort_values(by=sort_method,ascending=False)

    quality = df['quality'].values
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


    return session,html

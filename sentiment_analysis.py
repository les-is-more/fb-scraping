import os, ast
import pandas as pd
import numpy as np

# Loading the combined dataset
os.chdir('/Users/apple/Documents/Work/FB scraper/data')
feat_cols = ['Page Source','Post', 'Link','Posting Date', 'Image','Reactions', 'Comments', 'Shares']
full_data = pd.read_csv('./combined.csv')
full_data.columns = feat_cols


# For FWD only
comments = full_data[full_data['Page Source'] == 'fwdlife.ph']['Comments']
comments_dict = [ast.literal_eval(comment) for comment in comments]
combined_comments = list()

test_json = full_data[full_data['Page Source'] == 'fwdlife.ph']
# test_json = test_json.to_dict('records')    


for comment in comments_dict:
    for profiles in comment.keys():
        if 'text' in comment[profiles].keys():
            combined_comments.append(comment[profiles]['text'])


combined_comments = pd.DataFrame(combined_comments, columns = ['Comments'])
                    

# for posts in comments_dict:
#     if len(posts) > 0:
#         for key in posts.keys():
#             for attrib in posts[key].keys():
#                 if attrib == 'text':
#                     combined_comments.append([posts[key]['post_date'],key,posts[key]['text']])
                    
# combined_comments = pd.DataFrame(combined_comments, columns = ['Posting Date', 'Posted By','Comments'])
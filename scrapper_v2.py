from facebook_scraper import get_posts

for post in get_posts('fwdlife.ph', pages = 1):
    print(post)
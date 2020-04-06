import argparse
import time
import json
import csv

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs


def _extract_html(bs_data):
    k = bs_data.find_all(class_="_5pcr userContentWrapper")
    postBigDict = list()

    for item in k:

        # Post Text        
        actualPosts = item.find_all(attrs={"data-testid": "post_message"})
        
        postDict = dict()
        if actualPosts :
            for posts in actualPosts:
                paragraphs = posts.find_all('p')
                text = ""
                for index in range(0, len(paragraphs)):
                    text += paragraphs[index].text

                postDict['Post'] = text

        else:
            postDict['Post'] = ""

        # Links
        postLinks = item.find(class_="_5pcq")            
        if postLinks is not None:
            postDict['Link'] =  "https://web.facebook.com/" + postLinks.get('href')


        # Content Date
        postLinks = item.find(class_="_5ptz")            
        if postLinks is not None:
            utc_dt = int(postLinks.get('data-utime'))
            postDict['content_date'] = datetime.utcfromtimestamp(utc_dt).strftime('%Y-%m-%d %H:%M:%S') 


        # Images

        postPictures = item.find_all(class_="scaledImageFitWidth img")
        postDict['Image'] = ""
        for postPicture in postPictures:
            postDict['Image'] = postPicture.get('src')


        # Reactions
        postDict['Reactions'] = dict()

        postReactsTotal = item.find("span", class_ ="_81hb").text
        postDict['Reactions']['Total'] = postReactsTotal

        postReacts = item.find_all(class_="_1n9l")
        for reacts in postReacts:
            if reacts is not None:
                x = reacts.get("aria-label")
                num, reaction = x.split(" ", 1)
                postDict['Reactions'][reaction] = num

        # Shares
        postShares= item.find_all(class_="_3rwx")
        postDict['Shares'] = ""
        for postShare in postShares:
            
            x = postShare.string
            if x is not None:
                x = x.split(" ",1)[0]
                postDict['Shares'] = x
            else:
                postDict['Shares'] = "0"

        # Comments

        postComments = item.find_all(attrs={"aria-label" :"Comment"})

        postDict['Comments'] = dict()

        #print(postDict)

        for comment in postComments:

            if comment.find(class_="_6qw4") is None:
                continue

            commenter = comment.find(class_="_6qw4").text
            postDict['Comments'][commenter] = dict()

            comment_text = comment.find("span", class_="_3l3x")

            if comment_text is not None:
                postDict['Comments'][commenter]["text"] = comment_text.text
        
            comment_link = comment.find(class_="_ns_")
            if comment_link is not None:
                postDict['Comments'][commenter]["link"] = comment_link.get("href")

            comment_pic = comment.find(class_="_2txe")
            if comment_pic is not None:
                postDict['Comments'][commenter]["image"] = comment_pic.find(class_="img").get("src")

            comment_date = comment.find("abbr", class_ = "livetimestamp")
            if comment_date is not None:
                postDict['Comments'][commenter]["post_date"] = comment_date.get("data-utime")



            #TODO: management comments of comments, the reply button has the same class (class="_4sxc _42ft)
            # as the button see more comments, for this reason they are extracted from the web page

            #HINT: use this methods and class to extract them
            #post_replies=item.find_all(attrs={"aria-label" :"Comment reply"})




        # # Reactions
        #
        # toolBar = item.find_all(attrs={"role": "toolbar"})
        #
        # if not toolBar:  # pretty fun
        #     continue
        #
        # postDict['Reaction'] = dict()
        #
        # for toolBar_child in toolBar[0].children:
        #
        #     str = toolBar_child['data-testid']
        #     reaction = str.split("UFI2TopReactions/tooltip_")[1]
        #
        #     postDict['Reaction'][reaction] = 0
        #
        #     for toolBar_child_child in toolBar_child.children:
        #
        #         num = toolBar_child_child['aria-label'].split()[0]
        #
        #         # fix weird ',' happening in some reaction values
        #         num = num.replace(',', '.')
        #
        #         if 'K' in num:
        #             realNum = float(num[:-1]) * 1000
        #         else:
        #             realNum = float(num)
        #
        #         postDict['Reaction'][reaction] = realNum

        postBigDict.append(postDict)

    return postBigDict


def extract(page, numOfPost, infinite_scroll=False, scrape_comment=False):
    with open('./facebook_credentials.txt') as file:
        email = file.readline().split('"')[1]
        password = file.readline().split('"')[1]

    option = Options()

    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")

    # Pass the argument 1 to allow and 2 to block
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    browser = webdriver.Chrome(executable_path=r"C:\Users\PHLLCA\Documents\FOR INSTALLATION_to_delete\chromedriver.exe", options=option)
    browser.get("https://facebook.com")
    browser.maximize_window()
    browser.find_element_by_name("email").send_keys(email)
    browser.find_element_by_name("pass").send_keys(password)
    browser.find_element_by_id('loginbutton').click()
    
    time.sleep(10)
    
    browser.get("https://facebook.com/" + page + "/posts")
    
    time.sleep(10)

    if infinite_scroll:
        lenOfPage = browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    else:
        # roughly 8 post per scroll kindaOf
        lenOfPage = int(numOfPost / 8)

    print("Number Of Scrolls Needed " + str(lenOfPage))

    lastCount = -1
    match = False

    while not match:
        if infinite_scroll:
            lastCount = lenOfPage
        else:
            lastCount += 1

        # wait for the browser to load, this time can be changed slightly ~3 seconds with no difference, but 5 seems
        # to be stable enough
        time.sleep(5)

        if infinite_scroll:
            lenOfPage = browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                "lenOfPage;")
        else:
            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                "lenOfPage;")

        if lastCount == lenOfPage:
            match = True

    # click on all the comments to scrape them all!
    # TODO: need to add more support for additional second level comments
    # TODO: ie. comment of a comment

    if scrape_comment:

        moreComments = browser.find_elements_by_xpath('//a[@class="_4sxc _42ft"]')
        print("Scrolling through to click on more comments")
        while len(moreComments) != 0:
            for moreComment in moreComments:
                action = webdriver.common.action_chains.ActionChains(browser)
                try:
                    # move to where the comment button is
                    action.move_to_element_with_offset(moreComment, 5, 5)
                    action.perform()
                    moreComment.click()
                except:
                    # do nothing right here
                    pass

            moreComments = browser.find_elements_by_xpath('//a[@class="_4sxc _42ft"]')

    # Now that the page is fully scrolled, grab the source code.
    source_data = browser.page_source

    # Throw your source into BeautifulSoup and start parsing!
    bs_data = bs(source_data, 'html.parser')

    postBigDict = _extract_html(bs_data)
    browser.close()

    return postBigDict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Facebook Page Scraper")
    required_parser = parser.add_argument_group("required arguments")
    required_parser.add_argument('-page', '-p', help="The Facebook Public Page you want to scrape", required=True)
    required_parser.add_argument('-len', '-l', help="Number of Posts you want to scrape", type=int, required=True)
    optional_parser = parser.add_argument_group("optional arguments")
    optional_parser.add_argument('-infinite', '-i',
                                 help="Scroll until the end of the page (1 = infinite) (Default is 0)", type=int,
                                 default=0)
    optional_parser.add_argument('-usage', '-u', help="What to do with the data: "
                                                      "Print on Screen (PS), "
                                                      "Write to Text File (WT) (Default is WT)", default="CSV")

    optional_parser.add_argument('-comments', '-c', help="Scrape ALL Comments of Posts (y/n) (Default is n). When "
                                                         "enabled for pages where there are a lot of comments it can "
                                                         "take a while", default="No")
    args = parser.parse_args()
    infinite = False
    if args.infinite == 1:
        infinite = True

    scrape_comment = False
    if args.comments == 'y':
        scrape_comment = True

    postBigDict = extract(page=args.page, numOfPost=args.len, infinite_scroll=infinite, scrape_comment=scrape_comment)

    if args.usage == "WT":
        with open('output.txt', 'w', encoding="utf-8") as file:
            for post in postBigDict:
                file.write(json.dumps(post))  # use json load to recover

    elif args.usage == "CSV":
        with open(args.page + 'data.csv', 'w', encoding="utf-8", newline = '') as csvfile:
           writer = csv.writer(csvfile)
           writer.writerow(['Post', 'Link','Posting Date', 'Image','Reactions', 'Comments', 'Shares'])

           for post in postBigDict:
              writer.writerow([post['Post'], post['Link'],post['content_date'],post['Image'],post['Reactions'], post['Comments'], post['Shares']])

    else:
        for post in postBigDict:
            print("\n")

    print("Finished")

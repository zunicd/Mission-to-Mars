# Web Scraping Homework - Mission to Mars

# Import BeautifulSoup
from bs4 import BeautifulSoup as bs
# Import Pandas
import pandas as pd
# Import Splinter and set the chromedriver path
from splinter import Browser

def init_browser():
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    # Create mars_data dictionary that we can insert into mongo
    mars_data = {}

    # ===== NASA Mars News ====================================
    # Visit the NASA Mars News Site 
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    browser.is_element_present_by_css(".list_text", 1)
    # Scrape the browser into soup 
    html = browser.html
    soup = bs(html, 'html.parser')

    # Find latest news title
    div_text = soup.find('div', class_='list_text')
    news_title = div_text.find('div', class_='content_title').a.text
    # Find latest news paragraph
    news_p = div_text.find('div', class_='article_teaser_body').text
    mars_data['news_title'] = news_title
    mars_data['news_paragraph'] = news_p

    # ===== JPL Mars Space Images - Featured Image ============
    # Visit the following URL
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)
    browser.is_element_present_by_id("full_image", 1)
    # Scrape the browser into soup 
    html = browser.html
    soup = bs(html, 'html.parser')

    # Find first featured image and open link with full image
    browser.find_by_id('full_image').first.click()
    browser.is_element_present_by_css(".fancybox-image", 1)
    # Scrape the browser into soup 
    html = browser.html
    soup = bs(html, 'html.parser')

    # Use soup to find full resolution image and save its url to variable `img_url`
    img_url = soup.find("img", class_='fancybox-image')['src']
    featured_image_url = f"https://www.jpl.nasa.gov{img_url}"
    mars_data['featured_image'] = featured_image_url

    # ====== Mars Weather =====================================
    # Visit Mars Weather twitter account
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)
    # browser.is_element_present_by_css(".css-901oao.css-16my406.r-1qd0xha.r-ad9z0x.r-bcqeeo.r-qvutc0", 1)
    browser.is_element_present_by_css("css-901oao.r-hkyrab.r-1qd0xha.r-a023e6.r-16dba41.r-ad9z0x.r-bcqeeo.r-bnwqim.r-qvutc0", 2)
    # Scrape the browser into soup 
    html = browser.html
    soup = bs(html, 'html.parser')

    # Use soup to find element with latest weather tweet
    w_div = soup.select('div.css-901oao.r-hkyrab.r-1qd0xha.r-a023e6.r-16dba41.r-ad9z0x.r-bcqeeo.r-bnwqim.r-qvutc0')[0]
    # Save the tweet text
    mars_weather = w_div.span.text
    mars_data['weather'] = mars_weather

    # ===== Mars Facts ========================================
    # Visit Mars Facts webpage
    url = 'https://space-facts.com/mars/'
    # Use Pandas' `read_html` to parse the url
    tables = pd.read_html(url)
    # Find Mars facts DataFrame in the list of DataFrames
    # Assign the columns `['description', 'value']
    mars_facts = tables[0]
    mars_facts.columns = ['description', 'value']
    # Set index to 'description' column
    mars_facts.set_index('description', inplace=True)
    # Save Dataframe to html table
    html_mars_facts = mars_facts.to_html(justify='left')
    # Strip unwanted newlines to clean up the table
    html_mars_facts = html_mars_facts.replace('\n', '')
    mars_data['facts'] = html_mars_facts

    # ===== Mars Hemispheres ==================================
    # Visit USGS Astrogeology webpage
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)

    # First loop to extract titles and links to pages with full images
    # ----------------------------------------------------------------
    # Design an XPATH selector to grab anchor with title
    # and link to bring up the full resolution image
    xpath = '//div[@class="description"]/a'
    browser.is_element_present_by_xpath(xpath, 1)
    # Find elements with titles and links to full images
    results = browser.find_by_xpath(xpath)
    # Initialize lists
    titles = []
    links = []
    # loop for all 4 images
    for i in range(len(results)):     
        # Set title
        titles.append(results[i].text)
        # Set links to pages with full image
        links.append(results[i]['href'])
                    
    # Second loop to extract full resolution images
    # ---------------------------------------------
    # Save them with titles to a dictionary; append the dictionaries to the list
    # Initialize list
    hemisphere_image_urls = []
    for i in range(len(links)):
        # Initialize loop dictionary
        img_dict = {}
        # Visist URLs
        browser.visit(links[i])
        browser.is_element_present_by_text("Sample", 1)
        # Use soup to find full resolution image
        html = browser.html
        soup = bs(html, 'html.parser')
        img_url = soup.find("a", text='Sample')['href']
        
        # Create dictionary for one hemisphere
        img_dict['title'] = titles[i]
        img_dict['img_url'] = img_url
        # Append it to list
        hemisphere_image_urls.append(img_dict) 
    mars_data['hemispheres'] = hemisphere_image_urls
    
    browser.quit()
    return mars_data

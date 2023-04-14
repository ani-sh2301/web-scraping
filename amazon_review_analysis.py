from bs4 import BeautifulSoup
from selenium import webdriver
from textblob import TextBlob as tb
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as mat
from scipy.stats import norm

#lists to store specific details
name_list=[]
rating_list=[]
rv_sum_list=[]
rv_date_list=[]
rv_country_list=[]

#scraping the given source code
def get_review_data(soup):
    review_cover=soup.find('div',class_='a-section a-spacing-none reviews-content a-size-base')
    reviews_list=review_cover.find_all('div',class_='a-section review aok-relative')

    for review_block in reviews_list:
        review=review_block.find('div',class_='a-section celwidget')

        name=review.find('span',class_='a-profile-name').text
        try:
            stars=int(float(review.find('span',class_='a-icon-alt').text.split()[0]))
        except:
            stars=int(float(review.find('span',class_='a-icon-alt').text.split()[0]))

        try:
            review_summary=review.find('a',class_='a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold').span.text
        except:
            review_summary=review.find('span',class_='cr-original-review-content').text

        review_place=review.find('span',class_='a-size-base a-color-secondary review-date').text
        review_date=review_place.split()[:-4:-1]
        review_country=review_place.split()[2]
        #review_text=review.find('span',class_='a-size-base review-text review-text-content').span.text
        name_list.append(name)
        rating_list.append(stars)#stars
        rv_sum_list.append(review_summary)
        rv_date_list.append(review_date)  
        rv_country_list.append(review_country)


#function scraps the review of a product and saves as a csv file
def retrieve_review():
    #product link after removing the page no. at end
    url=""
    # example, url="https://www.amazon.in/Samsung-Mystique-Storage-Purchased-Separately/product-reviews/B09TWGDY4W/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber="

    #using the webdriver to open link in browser and get source code
    driver = webdriver.Firefox()
    driver.minimize_window()

    #n number of pages to scrape
    for i in range(1,n):
        driver.get(url+str(i))
        html_text = driver.page_source
        soup=BeautifulSoup(html_text,'lxml')
        get_review_data(soup)

    driver.quit()

    file_name="amazon_review.csv"
    with open(file_name,'w',encoding='utf-8') as f:
        f.write=csv.writer(f)
        f.write.writerow(['Name','Rating','Summary','Date','Country'])

        for i in range(len(name_list)):
            f.write.writerow([name_list[i],rating_list[i],rv_sum_list[i],f"{rv_date_list[i][-1]}/{rv_date_list[i][1]}/{rv_date_list[i][0]}",rv_country_list[i]])

#function to read from csv file and do sentimental analysis using TextBlob library
def analyse():
    df=pd.read_csv('amazon_review.csv')
    df.dropna(inplace=True)

    sentiment=[]
    rating=[]
    for index, sum in (df.iterrows()):
        blob=tb(sum['Summary'])
        sentiment.append(blob.sentiment.polarity)
        rating.append(int(sum['Rating']))

    #using normal distribution to get probability of positive response for a product
    x=np.array(sentiment)
    mean=np.mean(x)
    sd=np.std(x)
    cdf_upper_limit=norm(mean,sd).cdf(1)
    cdf_lower_limit=norm(mean,sd).cdf(0)
    prob=(cdf_upper_limit-cdf_lower_limit)*100
    print("The mean is: ",round((mean)*100,2))
    print(f'The probablity that the person has a sentiment polarity between 0 to 1 is : {round(prob,2)}%')

    y=np.array(rating)
    mean2=np.mean(y)
    prob2=(mean2/5)*100
    print(f'The average rating is : {round(mean2,2)} ie {round(prob2,2)}%')
    mat.scatter(x,norm.pdf(x,mean,sd))
    mat.show()

retrieve_review()
analyse()


from bs4 import BeautifulSoup
from selenium import webdriver
from textblob import TextBlob as tb
from tkinter import *
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as m
from scipy.stats import norm

root=Tk()
#full screen window
root.state('zoomed')
root.title("Review Sentimental Analysis")

class amazon:
    def __init__(self):
        self.name_list=[]
        self.rating_list=[]
        self.rv_sum_list=[]
        self.rv_date_list=[]
        self.rv_country_list=[]
        self.url=StringVar()
        self.soup=""
        self.sentiment=[]
        self.rating=[]
        self.display()

    #function to display the title and get url input
    def display(self):
        h1=Label(root, text="Amazon Product Review Sentimental Analysis", width=50,fg="red", font=("times", 20, "bold"))
        h1.pack()

        frame_entry=Frame(root)
        frame_entry.pack(padx=100,pady=80,anchor='w')
        h2=Label(frame_entry, text=f"Enter the Product Review page url (remove the number after '=')",fg="black", font=("times", 15))
        h2.pack(anchor='w')
        #getting url from user
        l=Entry(frame_entry,textvariable=self.url,bg="White",width=150)
        l.pack(pady=10)
        #submit button
        button = Button(frame_entry, text="Submit",command=self.scrape, width=10,bg="green",fg="white",font=("times",16,"bold"))
        button.pack(anchor='w',pady=30)

    #funtion to call the retrieve_html and analyse functions
    def scrape(self):
        self.retrieve_html()
        self.analyse()

    #function to get the source code of the webpage
    def retrieve_html(self):
        driver = webdriver.Firefox()
        driver.minimize_window()

        for i in range(1,10):
            driver.get(str(self.url.get())+str(i))
            html_text = driver.page_source
            self.soup=BeautifulSoup(html_text,'lxml')
            self.get_review_data()

        driver.quit()
        #getting data from website
        self.get_review_data()
        #name of the file- where data to be saved 
        file_name="amazon_reviewTemp.csv"
        #writing to a file
        self.write(file_name)
        
    #function to scrape the useful information from the page source code    
    def get_review_data(self):
        review_cover=self.soup.find('div',class_='a-section a-spacing-none reviews-content a-size-base')
        reviews_list=review_cover.find_all('div',class_='a-section review aok-relative')

        for review_block in reviews_list:
            review=review_block.find('div',class_='a-section celwidget')

            #reviewer name
            name=review.find('span',class_='a-profile-name').text
            try:
                stars=int(float(review.find('span',class_='a-icon-alt').text.split()[0]))
            except:
                stars=int(float(review.find('span',class_='a-icon-alt').text.split()[0]))

            #reviewer's review summary
            try:
                review_summary=review.find('a',class_='a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold').span.text
            except:
                review_summary=review.find('span',class_='cr-original-review-content').text

            #date and country of the reviewer
            review_place=review.find('span',class_='a-size-base a-color-secondary review-date').text
            #date when posted
            review_date=review_place.split()[:-4:-1]
            #country where posted
            review_country=review_place.split()[2]

            #for full review text add this
            #review_text=review.find('span',class_='a-size-base review-text review-text-content').span.text

            #adding all the details to respective lists
            self.name_list.append(name)
            self.rating_list.append(stars)
            self.rv_sum_list.append(review_summary)
            self.rv_date_list.append(review_date)  
            self.rv_country_list.append(review_country)

    #function to write to a csv file
    def write(self,file_name):
        with open(file_name,'w',encoding='utf-8') as f:
            f.write=csv.writer(f)
            f.write.writerow(['Name','Rating','Summary','Date','Country'])

            for i in range(len(self.name_list)):
                f.write.writerow([self.name_list[i],self.rating_list[i],self.rv_sum_list[i],f"{self.rv_date_list[i][-1]}/{self.rv_date_list[i][1]}/{self.rv_date_list[i][0]}",self.rv_country_list[i]])

    #function to read and analyse the data 
    def analyse(self):
        #creating a data frame
        df=pd.read_csv('amazon_review.csv')
        #removing empty rows
        df.dropna(inplace=True)

        #Creating a frame for output
        frame=Frame(root)
        frame.pack(anchor='w',padx=100)

        #calculating the polarity of review using textblob and adding to the list 'sentiment'
        #iterating over all the rows
        for index, sum in (df.iterrows()):
            blob=tb(sum['Summary'])
            self.sentiment.append(blob.sentiment.polarity)
            self.rating.append(int(sum['Rating']))

        x=np.array(self.sentiment)
        #mean
        mean=np.mean(x)
        #standard deviation
        sd=np.std(x)

        cdf_upper_limit=norm(mean,sd).cdf(1)
        cdf_lower_limit=norm(mean,sd).cdf(0)

        prob=(cdf_upper_limit-cdf_lower_limit)*100

        if(mean>0.1):
            product_sentiment='Positive'
        elif(mean<(-0.1)):
            product_sentiment='Negative'
        else:
            product_sentiment='Neutral'

        mean_text=f"The Product has a '{product_sentiment}' sentiment with a mean of: {round((mean),2)}"
        prob_text=f'The probablity that the person will have a positive sentiment (0-1) is : {round(prob,2)}%'

        y=np.array(self.rating)
        mean2=np.mean(y)
        prob2=(mean2/5)*100
        avgRating_text=(f'The average rating is : {round(mean2,2)} ie {round(prob2,2)}%')

        #displaying in the tkinter window
        h=Label(frame,text="The Analysis of Data: ",fg="black", font=("times", 15, "bold"))
        h.pack(anchor='w', pady=20)
        a1=Label(frame,text=mean_text,fg="blue", font=("times", 14, "bold"))
        a1.pack(anchor='w')
        a2=Label(frame,text=prob_text,fg="blue", font=("times", 14))
        a2.pack(anchor='w')
        a3=Label(frame,text=avgRating_text,fg="blue", font=("times", 14))
        a3.pack(anchor='w')
        #creating a normal distribution scatter plot
        m.scatter(x,norm.pdf(x,mean,sd))
        m.show()

#creating the object of the class amazon      
obj=amazon()

root.mainloop()


'''
sample url


https://www.amazon.in/Samsung-Mystique-Storage-Purchased-Separately/product-reviews/B09TWGDY4W/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber=
'''

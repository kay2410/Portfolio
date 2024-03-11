# Imports

import time  # this allows time to scrape the webpages

from selenium import webdriver

from selenium.webdriver.chrome.service import Service as ChromeService

from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup as BS

from datetime import date

import re

# Imports for Dataframe

import pandas as pd

import os  # for extracting into csv.

from random import randint  # For avoiding throttling.

# Main PY

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

postUrl = []



def GetListings(page):

    global pageNumber

    pageNumber = int(page)

    url = "https://vancouver.craigslist.org/search/apa#search=1~gallery~"

    global postUrl

    driver.get(url + str(pageNumber))

    driver.maximize_window()

    # allow time for page to load

    time.sleep(randint(3, 5))

    for i in range(0, 20):

        # Get individual posts.

        posts = driver.find_elements(By.CLASS_NAME, "gallery-card")

        # Get the individual listings

        for post in posts:

            listing = post.get_attribute("innerHTML")

            soup = BS(listing, 'lxml')

            # find images of the postings, this allows to select only posts with images
            postImage = soup.find("img")

            priceTag = soup.find("span", class_='priceinfo')

            anchor = soup.find("a")

            if postImage is not None and priceTag is not None:

                link = anchor.get("href")

                postUrl.append(link)





        # Go to the Next page.

        pageNumber += 1

        urlNext = url + str(pageNumber)

        driver.get(urlNext)

        driver.maximize_window()

        time.sleep(randint(4, 6))


def checkPets(aText):
    if aText.find('cats are OK') == -1 or aText.find('dogs are OK') == -1:
        pets.append('no')
    else:
        pets.append('yes')


def checkLaundry(aText):
    if aText.find('laundry in bldg') != -1:
        laundry.append('in building')

    elif aText.find('w/d') != -1:
        laundry.append('w/d')

    elif aText.find('laundry on site') != -1:
        laundry.append('on site')

    else:
        laundry.append('no laundry')


def checkParking(aText):
    if aText.find('off-street parking') != -1:
        parking.append('off-street')

    elif aText.find('attached garage') != -1:
        parking.append('attached-garage')

    elif aText.find('street parking') != -1:
        parking.append('street-parking')

    elif aText.find('valet parking') != -1:
        parking.append('valet-parking')

    elif aText.find('detached garage') != -1:
        parking.append('detached-garage')

    elif aText.find('carport') != -1:
        parking.append('car-port')

    else:
        parking.append('no-parking')


def checkAvailability(aList):
    if 0 <= 2 <= len(aList):
        availability.append(aList[2].text)

    else:
        availability.append('N/A')


def removeEntry(aList, aList1, aList2, aList3, aList4):
    aList.pop()
    aList1.pop()
    aList2.pop()
    aList3.pop()
    aList4.pop()

# attributes to select viable postings







def getPostingDetails(webpage):

    global priceList, latitude, longitude, city, postalCode, availability, \
            size, pets, listType, laundry, parking, noBeds, noBaths, postLink

    priceList = []

    # Location data
    latitude = []
    longitude = []
    city = []
    postalCode = []

    # Posting attributes to Create Dataframe
    availability = []
    size = []
    pets = []
    listType = []
    laundry = []
    parking = []
    postLink = []
    noBeds = []
    noBaths = []

    for i, element in enumerate(webpage):

        driver.get(element)  # Opens the posting webpage
        driver.maximize_window()

        time.sleep(randint(1, 3))

        content = driver.find_element(By.CLASS_NAME, "body")
        getPost = content.get_attribute("innerHTML")
        postSoup = BS(getPost, 'lxml')
        findAddress = postSoup.find('h2', class_='street-address')

        if findAddress is None:
            postUrl.remove(element)


        else:
            # Get price of listing.
            getPrice = postSoup.find('span', class_="price")
            priceTag = getPrice.text
            price = float(priceTag[1:].replace(',', ''))

            priceList.append(price)




            # Get location of listing.

            # Get latitude and longitude for specific geolocation of listings.

            latLong = postSoup.find(attrs={"data-latitude": True, "data-longitude": True})
            latitude.append(latLong['data-latitude'])
            longitude.append(latLong['data-longitude'])


            # Get street address for data visualization labels.

            getAddress = postSoup.find('h2', class_="street-address").text
            firstComma = getAddress.find(',')
            lastComma = getAddress.find(',', firstComma + 1)
            findProv = getAddress.find('BC')
            city.append(getAddress[firstComma+1:lastComma].strip())
            postalCode.append(getAddress[findProv+3:])

            # Get attributes of listing.
            attributes = postSoup.find('div', class_='mapAndAttrs')
            pTags = attributes.find_all('div', class_='attrgroup')
            mapTags = attributes.find_all('span', class_='attr important')



            # Exclude/remove entries if attributes can't be extracted.

            if pTags is None or mapTags is None:
                removeEntry(longitude, latitude, postalCode, city, priceList)


            elif 0 <= 3 <= len(pTags) and 0 <= 3 <= len(mapTags):
                sizeDetails = mapTags[0].text   # GEt listing Size
                listSize = mapTags[1]
                atrContent = pTags[2].text

                # Get listing layout
                findDivider = sizeDetails.find('/')
                bed = sizeDetails[0:findDivider - 3]
                bath = sizeDetails[findDivider + 1:findDivider + 3].strip()

                if listSize is None or sizeDetails is None:
                    removeEntry(longitude, latitude, postalCode, city, priceList)


                else:
                    # Create list of Necessary Attributes.

                    # Type
                    house = atrContent.find("house")
                    apartment = atrContent.find("apartment")
                    condo = atrContent.find("condo")
                    townhouse = atrContent.find("townhouse")

                    # Checks if listing includes listing type, excludes listings without housing type
                    if house and apartment == -1 and condo and townhouse == -1:
                        removeEntry(longitude, latitude, postalCode, city, priceList)

                    elif house != -1:
                        size.append(listSize.text)
                        noBaths.append(bath)
                        noBeds.append(bed)
                        postLink.append(webpage[i])
                        listType.append('house')
                        checkPets(atrContent)
                        checkLaundry(atrContent)
                        checkParking(atrContent)
                        checkAvailability(mapTags)

                    elif apartment != -1:
                        noBaths.append(bath)
                        noBeds.append(bed)
                        size.append(listSize.text)
                        postLink.append(webpage[i])
                        listType.append('apartment')
                        checkPets(atrContent)
                        checkLaundry(atrContent)
                        checkParking(atrContent)
                        checkAvailability(mapTags)

                    elif condo != -1:
                        noBaths.append(bath)
                        noBeds.append(bed)
                        size.append(listSize.text)
                        postLink.append(webpage[i])
                        listType.append('condo')
                        checkPets(atrContent)
                        checkLaundry(atrContent)
                        checkParking(atrContent)
                        checkAvailability(mapTags)

                    elif townhouse != -1:
                        noBaths.append(bath)
                        noBeds.append(bed)
                        size.append(listSize.text)
                        postLink.append(webpage[i])
                        listType.append('townhouse')
                        checkPets(atrContent)
                        checkLaundry(atrContent)
                        checkParking(atrContent)
                        checkAvailability(mapTags)

                    time.sleep(randint(2, 4))

            else:
                removeEntry(longitude, latitude, postalCode, city, priceList)



    driver.close()

# Create Dataframe


def createDF(page):
    Date = date.today()
    dataSet = {'Price': priceList, 'Housing Type': listType, 'Size': size, 'Parking Type': parking,
               'Laundry Type': laundry, 'Pet allowed': pets, 'City': city, 'Postal Code': postalCode,
               'Latitude': latitude, 'Longitude': longitude, 'Baths': noBaths, 'Beds': noBeds, 'Link': postLink,
               'Availability': availability}

    df = pd.DataFrame(dataSet)

    pd.set_option('display.max_columns', None)

    df.to_excel(f"pages {page+20}_{Date}.xlsx", index=False)

    print(f"/Data frame created")
    print(df)








# run code




GetListings(65)
getPostingDetails(postUrl)
createDF(65)













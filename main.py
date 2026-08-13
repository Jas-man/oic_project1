
#OIC project - August 2026
#Title - Live Window Efficiency Score Calculator
#Code to calculate the live window efficiency score based on the following parameters: area, internal, ambient and outdoor temperature, humidity, wind conditions, solar radiation and heat transferered 

import time as dt
import requests


#intro and explanation to the user
print("Welcome to WESH, the Live Window Efficiency Score Calculator!")
print("This program will give you a better insight into your the thermal efficiency of your windows based on live parameters - and will help you to save money in the long run! Let's get started!")

#user input section
name = input("Please enter your name: ") 
postcode = input("Please enter your Postcode: ")
propertyType = input("What kind of property is this for? (Please type 'house', 'flat' or 'business'): ")


windowType = input("What type of window do you have? (Please type 'single-glazed', 'double-glazed', 'triple-glazed' or 'idk'): ")
windowHeight = float(input("Please enter your window height (in meters): "))
windowWidth = float(input("Please enter your window width (in meters): "))

ans= input("Have you installed the WESH sensor? (Please type 'yes' or 'no'): ")

area = windowHeight * windowWidth

if ans == "no":
    print ("Please install the WESH sensor to access live data and calculate your live window efficiency score! WESH")
else: 
    print ("Great! Let's continue getting you set up :)")


#weather API integration
BASE_URL = "https://openweathermap.org/data/2.5/weather?"
API_KEY = open('api_key','r').read()    
CITY = postcode

URL = BASE_URL + "appid=" + API_KEY + "&q=" + CITY

response = requests.get(URL).json()
print(response)
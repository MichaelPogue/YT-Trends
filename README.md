# YT-Trends
Developed By: Michael Pogue
Created:      2023.02.22

## Project Overview
### Purpose:
The purpose for this code is to generate data scraped from YouTube's auto-generated video game streams and stream it to Rabbit MQ. Once received, the values will be evaluated and finally a warning via email will be dispatched should the said values reach a specific number.

The idea behind this is to monitor a website and create alerts in the event that a user-specified limit has been reached. 

## Project Requirements
### Necessary Modules:
1. pika
1. sys
1. time
1. os
1. ssl
1. smtplib
1. collections
1. time
1. dotenv 
1. email.message

### Environmental Factors:
A .env or other environmental systems will be required in order to hide the sender's email password if this code is to be uploaded to GitHub.
This is the structure of the environment: 
![image](https://user-images.githubusercontent.com/115908053/221733609-b4b0f2ff-3a5f-4ee3-ae6a-ea8b9a48253d.png)


## Results

Details of each functioning system:
![image](https://user-images.githubusercontent.com/115908053/221660845-5c4687e5-fe7a-4bce-8a63-9a3a3b13a67d.png)



Accuracy:
![image](https://user-images.githubusercontent.com/115908053/221660465-27ee8762-f6fa-47da-8336-c50053e2384e.png)


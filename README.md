
# HandongRemy
#### An API server for KakaoTalk chat bot

21900050 Eunhyeok Kwon

Presentation Video link : https://youtu.be/j5TErKd7nEY

## What does this project do?
This project has started with a goal to help students of Handong Global University(HGU) by providing more convenient way to access function in the school webpage. 

The name HandongRemy came from a cat called Remy that lives in HGU. Because, like the cat, I wanted this project to be very accessible to the students in HGU.

For that reason, I chose to create an API server for KakaoTalk chat bot, which is the most popular messenger app in South Korea.

This project can currently do 5 functions:
1. Return random number between 1 ~ 10 (inclusive)
2. Return today's menu of cafeteria
3. Return reservation status of conference room (1~10) at given time
4. Reserve conference room at specific time
5. Apply for sleepover for dormitory

## Why is this project useful?
In my opinion, there is a problem with our school webpage that is the functions for viewing conference room reservation status or applying for reservation is not very easy to access, especially using mobile device. 

By creating an API server that can do those functions, and connecting it to KakaoTalk chat bot, it becomes interactive and much more accessible.

## How to get started?
1. Create KakaoTalk Channel from https://center-pf.kakao.com/
2. Apply for KakaoTalk Open Builder (OBT) from https://i.kakao.com/
3. Refer to the documentation to create and connect each 'scenario' to appropriate skill server url(API) (You can also contact me about this)*
4. Install Python and install Flask and requests libraries
5. Clone this repo on your device
6. Use [pagekite](https://pagekite.net/downloads) to make local server visible to the world
7. run flask in src directory
8. Your chat bot should be ready to serve!

## My contribution to this project
The entire source codes are created from scratch! (by me)
For the implementation of Kakaotalk chat bot I referred to the 

## Important notice about this project
'String.py' is intentionally ommitted in the src file because it contains web urls that are only visible to memebers and I thought exposing those internal urls could cause secuity issue.

If you contact me and prove that you are a member of HGU I will definitely provide the file!

### Contact
You can contact me via eunhyeoq@gmail.com if you have any question or need help about this project!

> Written with [StackEdit](https://stackedit.io/).

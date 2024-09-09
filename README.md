# lineinradio
lineinradio is a 24/7 online radio station which plays sets uploaded by users. 
Sets can range from 30 minutes to 2 hours and span all genres. 
Although sets can be any energy level, slower sets will be played in the mornings and more fast paced music in the evenings.
This is paired with a simple user interface.

![profile screenshot](https://raw.githubusercontent.com/mgurga/lineinradio/master/docs/profile.png)
![schedule screenshot](https://raw.githubusercontent.com/mgurga/lineinradio/master/docs/schedule.png)

# Technical Details
The project is written in Python 3 and utilizes the Django framework. 
All templating and database management is handled by Django.
Task scheduling is handled by django_q.
Downloading from external services uses the ytdlp library.
The project is split into 3 different apps:

## website
The frontend is written in lightweight HTML, CSS, and minimal Javascript.

Its main features are:
- User registration, sign up, and session management
- Show and Episode creator
- Profile customization

## scheduler
The scheduler runs tasks throughout to make sure all episodes are ready to be played. It also generates a new schedule every night.

Its main functions are:
- Orders sets based on what time they will play (slower in the morning, faster in the evening)
- Downloads all episodes that are going to be played in the next bloc
- Plans around important sets that need to be played at certain times

## radio
The radio app is a compact WebSocket server that streams chunks of audio to everyone listening in.

Its main functions are:
- Maps the time to the bytes in an audio file 
- Stream chunk of data to the client
- Utilize MediaSource to buffer audio so radio plays without interruptions

# How to run
First setup the environment
```
pip install -r requirements.txt
./setup.sh
```
Then run both these commands at the same time: 
```
python manage.py runserver
python manage.py qcluster
```
The former starts the Django frontend and latter runs tasks periodically like downloading episodes and generating schedules.

You will also need to serve the media directory under the ```/media/``` endpoint when Django is running in production.
This is usually done with nginx or another web server.

# Credits
- The original inspiration for a community ran radio show was created by the [WHEN Collective](https://whenco.site/), many shows from their website continue on lineinradio.
- Audio streaming code adapted from [WebSocketAudio](https://github.com/SamuelFisher/WebSocketAudio)
- Royalty free radio static from [Pixabay](https://pixabay.com/sound-effects/static-radio-noise-and-searching-for-stations-48537/)

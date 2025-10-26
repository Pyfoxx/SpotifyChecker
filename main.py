import os
import random
import string
# from PIL import Image
import threading
import tkinter
from base64 import urlsafe_b64encode
from hashlib import sha256
from time import sleep
from tkinter import *
from urllib.parse import urlparse, parse_qs

import requests
from PIL import ImageTk, Image, ImageOps, ImageDraw
from dotenv import load_dotenv, set_key

from exceptions import *

load_dotenv()

clientID = os.getenv('API_CLIENT_ID')
secret = os.getenv('API_SECRET')
token_API = "https://accounts.spotify.com/api/token"
api = "https://api.spotify.com/v1"
redirect_uri = 'http://google.com/callback/'
lastCallHash = ""
plonk = False
isPlaying = False


def tokenRefresh(f):
    def wrap(*args, **kwargs):
        while True:
            try:
                v = f(*args, **kwargs)
                return v
            except TokenExpired:
                print('Token expired, refreshing...')
                try:
                    refreshToken()
                except RefreshExpired:
                    print('Refresh token expired, logging in again...')
                    login()
                except InvalidToken:
                    exit(1)
            except InvalidToken:
                exit(1)

    return wrap


def id_generator(size=16, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def getToken(code):
    combo = urlsafe_b64encode(f"{clientID}:{secret}".encode()).decode()
    token = requests.post(token_API, headers={"Content-Type": "application/x-www-form-urlencoded",
                                              "Authorization": f"Basic {combo}"},
                          data=f"grant_type=authorization_code&code={code}&redirect_uri={redirect_uri}")

    if token.status_code == 200:
        print(token.json())
        return token.json()["access_token"], token.json()["refresh_token"]
    else:
        return token.json()["error"], token.json()["error"]


def refreshToken():
    global clientID, refresh, token
    combo = urlsafe_b64encode(f"{clientID}:{secret}".encode()).decode()
    print("Attempting refresh token...")
    t = requests.post(token_API,
                      headers={"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Basic {combo}"},
                      data=f"grant_type=refresh_token&refresh_token={refresh}")
    print(t)
    print(t.json())
    if t.status_code == 200:
        print(t.json().keys())
        token = t.json()["access_token"]
        if "refresh_token" in t.json().keys(): refresh = t.json()["refresh_token"]
        set_key(".env", "TOKEN", token)
        set_key(".env", "REFRESH", refresh)
        return
    elif t.status_code == 400:
        raise InvalidToken


def login():
    scope = 'user-read-playback-state'
    print(
        'https://accounts.spotify.com/authorize?' + f'response_type=code&client_id={clientID}&scope={scope}&redirect_uri={redirect_uri}&state={id_generator()}')
    uri = input('paste redirected >>> ')
    return parse_qs(urlparse(uri).query)['code']


@tokenRefresh
def getPlaying():
    global token
    playback = requests.get(f"{api}/me/player?market=FR", headers={"Authorization": f"Bearer {token}"})
    if playback.status_code == 200:
        js = playback.json()
        return js['item']['artists'][0]['id'], js['item']['album']['images'][0]['url'], js['item']['name'], js[
            'is_playing']
    elif playback.status_code == 401:
        raise TokenExpired
    else:
        raise Exception


def getArtist(token, artistID):
    artist = requests.get(f"{api}/artists/{artistID}", headers={"Authorization": f"Bearer {token}"})
    js = artist.json()
    return js['name']


def checkLoop():
    global lastCallHash, CallHash, song, artistName, plonk, isPlaying
    while True:
        try:
            artistID, albumImage, song, isPlaying = getPlaying()
            artistName = getArtist(token, artistID)
            CallHash = sha256(f"{artistID}{song}{albumImage}".encode()).hexdigest()
            if not CallHash == lastCallHash:
                img_data = requests.get(albumImage).content
                with open('../spotifyChecker/albumImage.jpg', 'wb') as handler:
                    handler.write(img_data)
                print(f"{song} by {artistName}")
                lastCallHash = CallHash
                plonk = True
        except Exception:
            pass
        sleep(2)


def mainImage():
    global frame, root, framesIter, frames, plonk, c
    root = Tk()
    root.attributes("-fullscreen", True)
    root.configure(bg="black")
    root.geometry("640x640")
    frame = Frame(root, bg="black", width=640, height=640)
    frame.grid(row=0, column=0)
    plonk = True
    panel = Label(frame, compound="center")
    panel.place(anchor=tkinter.CENTER, x=340, y=340)
    panel.pack()
    title = Label(frame)
    title.place(anchor=tkinter.CENTER, x=340, y=400)
    title.pack()
    c = 0
    frames = []
    framesIter = iter(frames)

    def next_image():
        global frame, plonk, root, framesIter, frames, c, isPlaying
        size = (640, 640)
        mask = Image.new('L', size, 255)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=0)

        if plonk:
            print("plonk received by spotifyChecker thread")
            c = 0
            print("new image")
            title.configure(text=f"{song} by {artistName}")
            title.text = f"{song} by {artistName}"
            image = Image.open('albumImage.jpg')
            output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
            output.paste(0, mask=mask)
            output.convert('P', palette=Image.ADAPTIVE)
            frames = []
            img = ImageTk.PhotoImage(output)
            panel.configure(image=img)
            panel.image = img
            print("generating every frames")
            for i in range(360, 0, -1):
                t = i
                for x in range(1, 10): frames.append(output.rotate(angle=t - (x / 10), expand=False))
            print("generated every frames")
            # frames[0].save(
            #     "output.gif",
            #     save_all=True,
            #     append_images=frames,
            #     optimize=False,
            #     duration=40,  # Set the frame duration to 40 milliseconds
            #     loop=0
            # )
            print(len(frames))
            plonk = False
            print("finished making the gif")
            root.after(1, next_image)
        else:
            if isPlaying:
                image = frames[c]
                img = ImageTk.PhotoImage(image)
                panel.configure(image=img)
                panel.image = img
                c += 1
                if c == len(frames): c = 0
                root.after(33, next_image)
            else:
                root.after(33, next_image)

    root.after(100, next_image)
    root.mainloop()


if __name__ == '__main__':
    global token
    threads = []
    token, refresh = os.getenv('TOKEN'), os.getenv('REFRESH')
    if not token or not refresh:
        code = login()[0]
        token, refresh = getToken(code=code)
        set_key(".env", "TOKEN", token)
        set_key(".env", "REFRESH", refresh)

    t = threading.Thread(target=checkLoop)
    threads.append(t)
    i = threading.Thread(target=mainImage)
    threads.append(i)
    t.start()
    sleep(2)
    i.start()

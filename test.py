import smtplib

server = smtplib.SMTP('smtp.gmail.com', 587)

server.starttls()
message = """From: From System
To: To Person <sir/madam@iiti.ac.in>
Subject: Experiment is Completed!!!

Master! Your Experiment is completed... 
"""
server.login('saipranaydeepjonnalagadda2888@gmail.com', 'nrtjwumgsagpsmrc')

server.sendmail('saipranaydeepjonnalagadda2888@gmail.com', 'cse220001003@iiti.ac.in', message)



# import pyautogui
# # Holds down the alt key
# pyautogui.keyDown("alt")

# # Presses the tab key once
# pyautogui.press("tab")

# pyautogui.press("enter")

# import pygame

# pygame.mixer.music.load("path")
# pygame.mixer.music.play()
# pygame.mixer.music.stop()


# import customtkinter as ctk
# from PIL import Image

# STOP_MUSIC_WIDGET = ctk.CTk()
# BELL_IMAGE = ctk.CTkImage(Image.open('Software-Project\comp.png'), size=(150,150))
# ctk.CTkLabel(STOP_MUSIC_WIDGET, image=BELL_IMAGE, text="").grid(row=0, column=1, pady=10)
# STOP_MUSIC_WIDGET.mainloop()
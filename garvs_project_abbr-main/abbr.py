import kivy 
import re
# Import kivy dependencies first
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout 
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.app import App, Builder
from kivy.core.window import Window
from kivy.lang import builder

# Import kivy UX components
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

# Import other kivy stuff
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle

import pyttsx3
engine = pyttsx3.init()

import random
import os

layout = BoxLayout
black = [0, 0, 0, 0]
white=[1, 1, 1, 1]
red = [1, 0, 0, 1] 
green = [0, 1, 0, 1] 
blue = [0, 0, 1, 1] 
purple = [1, 0, 1, 1] 
grayish=[220,220,220,225]
light_blue=[0,1,1,1]

g_first_letter_input=[]

g_abbr=""
g_story=""

#Builder.load_file("medium.kv")

from transformers import pipeline, TextGenerationPipeline, GPT2LMHeadModel, AutoTokenizer

model_name = "aspis/gpt2-genre-story-generation"
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
generator = TextGenerationPipeline(model=model, tokenizer=tokenizer)

class AbbrPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 2

        # Main layout components 
        self.input_string = TextInput(text='Enter Your Input String', multiline=True, font_size=18)
        self.output_abbr = Label(
            text="Abbreviation",
            font_size=18)
        self.button = Button(text="Submit", on_press=self.submit, background_color=light_blue, font_size=18)
        self.pg_change = Button(text="Get the Full Story", on_press=self.page_change, background_color=blue, font_size=18)

        # Add items to layout
        self.add_widget(self.input_string)
        self.add_widget(self.output_abbr)
        self.add_widget(self.button)
        self.add_widget(self.pg_change)

    def submit(self, *args):

        final_abbr=self.abbr_finder()
        final_abbr=str(final_abbr)

        global g_abbr
        g_abbr=final_abbr

        self.output_abbr.text=final_abbr.upper()

    def abbr_finder(self, *args):

        #find abbreviation
        input_list=str(self.input_string.text).split()
        first_letter_input=[]
        for i in input_list:
            first_letter_input.append(i[0])
        global g_first_letter_input
        g_first_letter_input=first_letter_input
        final_abbr=str("".join(first_letter_input))

        #generate story

        genre_list=["romance", "adventure", "mystery-&-detective", "fantasy","humor-&-comedy","paranormal","science-fiction"]
        genre_use=random.choice(genre_list)
        st_op=""
        input_prompt="<BOS> <"+str(genre_use)+"> "+str(self.input_string.text)
        st_op=st_op+str(generator(input_prompt, max_length=30, do_sample=True, repetition_penalty=1.5, temperature=1.2,top_p=0.95, top_k=50))+"\n"

        chset=["[","]","generated_text","'","<BOS>",":",'"',"/","{","}", genre_use,"<",">","_","(",")"]
        for i in chset:
            st_op=st_op.replace(i,"")

        global g_story
        g_story=st_op
        print(g_story)

        return str(final_abbr)
    
    def page_change(self, *args):
        cam_app.screen_manager.current = 'Story'

class StoryPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 2

        # Add items to layout
        self.add_widget(Button(text ='Get the abbreviation', background_color=blue, on_press=self.change_text_abbr, font_size=18))
        self.abbrev = Label(text=str(g_abbr), font_size=18)
        self.add_widget(self.abbrev)
        self.add_widget(Button(text ='Get the story',  background_color=red, on_press=self.change_text_story, font_size=18))
        self.storie = Label(text=str(g_story), font_size=10)
        self.add_widget(self.storie)


    def change_text_abbr(self, *args):
        self.abbrev.text = str(g_abbr).upper()

    def change_text_story(self, *args):
        self.storie.text=str(g_story)
        self.audio()

    def audio(self, *args):
        engine.setProperty('rate', 155) # setting up new voice rate
        rate = engine.getProperty('rate')   # getting details of current speaking rate
        print (rate)                        #printing current voice rate
        engine.say(g_story)
        engine.runAndWait()


class CamApp(App):
    def build(self):

        self.screen_manager = ScreenManager()

        # Info page
        self.abbr_page = AbbrPage()
        screen = Screen(name='Abbrreviation')
        screen.add_widget(self.abbr_page)
        self.screen_manager.add_widget(screen)

        self.Story_page= StoryPage()
        screen = Screen(name='Story')
        screen.add_widget(self.Story_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

if __name__ == '__main__':
    print(kivy.__version__)
    cam_app=CamApp()
    cam_app.run()
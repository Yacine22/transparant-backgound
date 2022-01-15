# -*- coding: utf-8 -*-
"""
@author: yacine22
"""
from skimage.filters import threshold_otsu
import numpy as np
import os
from tkinter import *     
from tkinter import ttk, messagebox
from PIL import ImageTk, Image, ImageGrab
from tkinter.filedialog import askopenfilename
import cv2 as cv 
import time, datetime

try:
    os.mkdir("./masks/")
except:
    pass
    
icons = "./sources/"

class fenetre:
    def __init__(self): 
        self.window = Tk()
        self.window.attributes("-fullscreen", True)
        self.window.title("To Mask image transform")
        self.window.configure(bg="#220794")
        
        self.exit_frame = Frame(self.window, bg="#220794")
        self.frame = Frame(self.window, bg="#220794")
        
        
        ### ------------------- GET ICONS ------------------------------
        self.exit_icon = Image.open(icons+"exit.png")
        self.exit_button_icon = ImageTk.PhotoImage(self.exit_icon.resize((75, 75)), Image.BILINEAR)
        
        self.upload_icon = Image.open(icons+"upload.png")
        self.upload_button_icon = ImageTk.PhotoImage(self.upload_icon, Image.BILINEAR)
        
        self.project_icon = Image.open(icons+"projects.png")
        self.project_icon_icon = ImageTk.PhotoImage(self.project_icon, Image.BILINEAR)
        
        ####### -------------------------------------------------------
        
        self.label = Label(self.frame, text="      Hello :) ", bg="#220794", fg="#FFF3AE", 
                           font=("Roboto Mono", 48, "bold"))
        
        self.exit_button = Button(self.exit_frame, text='Exit', bg="#220780",
                                  relief="flat", command=self.destroy)
        
        
        self.exit_button['image'] = self.exit_button_icon
        
        self.upload_button = Button(self.frame, text='Upload image', bg="#220794",
                                    relief="flat", command=self.upload_image)     
        self.upload_button['image'] = self.upload_button_icon
        
        self.view_project = Button(self.frame, text='View Masks', bg="#220794",
                                    relief="flat")
        self.view_project['image'] = self.project_icon_icon
        
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)
        
        self.exit_frame.grid(row=0, column=0, sticky="ne")
        self.frame.grid(row=0, column=0, sticky="n")
        
        self.label.grid(row=0, column=2, padx=5, sticky='news')
        self.exit_button.grid(row=0, column=3, sticky='news')
        self.upload_button.grid(row=4, column=2, padx=5, pady=20, sticky="n")
        self.view_project.grid(row=4, column=3, padx=10, pady=20, sticky="n")
        
        
    def mainloop(self):
        self.window.mainloop()
        
    def destroy(self): 
        time.sleep(0.01)
        self.window.destroy()
        
    def upload_image(self): 
        global state
        global image_path
        self.filename = askopenfilename()
        image_path = self.filename
        if len(image_path) == 0:
            print("No Image Selected !")
            messagebox.showwarning("Please select image", "No image file selected!")
        
        # if image_path
        extensions = {".jpg", ".png", ".PNG", ".JPG"}
        image_file_check = any(image_path.endswith(ext) for ext in extensions)
        print(image_path)
        
        if image_file_check == True :
            self.view_project['state'] = DISABLED
            self.upload_button['text'] = "Start transformation"
            
            self.start_icon = Image.open(icons+"start.png")
            self.start_button_icon = ImageTk.PhotoImage(self.start_icon, Image.BILINEAR)
            
            self.upload_button['image'] = self.start_button_icon
            self.upload_button['command'] = self.image_transform
            state = True
            
        elif image_file_check == False and len(image_path) != 0:
            messagebox.showwarning("Please select image", "No image selected!")
            
    def image_transform(self):
        self.window_2 = Toplevel()
        self.window_2.attributes("-fullscreen", True)
        self.window_2.title("To Mask image transform")
        self.window_2.configure(bg="#220794")
        
        self.progress_frame = Frame(self.window_2, bg="#220794")
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient=HORIZONTAL, length=450)
        
        self.img = cv.imread(image_path)
        
        file_name = str(datetime.datetime.now().strftime("%d%m%Y%H%M%S"))
        
        gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        
        # threshold input image as mask
        mask = cv.threshold(gray, 250, 255, cv.THRESH_BINARY)[1]
        
        # negate mask
        mask = 255 - mask
        
        # apply morphology to remove isolated extraneous noise
        # use borderconstant of black since foreground touches the edges
        kernel = np.ones((3,3), np.uint8)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
        
        # blur alpha channel
        mask = cv.GaussianBlur(mask, (0,0), sigmaX=2, sigmaY=2, borderType = cv.BORDER_DEFAULT)
        
        # linear stretch so that 127.5 goes to 0, but 255 stays 255
        mask = (2*(mask.astype(np.float32))-255.0).clip(0,255).astype(np.uint8)
        
        # put mask into alpha channel
        result = self.img.copy()
        result = cv.cvtColor(result, cv.COLOR_BGR2BGRA)
        result[:, :, 3] = mask
        
        # save resulting masked image
        cv.imwrite('./masks/'+file_name+'_bg.png', result)
        
        
        image = cv.imread('./masks/'+file_name+'_bg.png', cv.IMREAD_GRAYSCALE)
    
        (thresh, im_bw) = cv.threshold(image, 128, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)

        thresh = threshold_otsu(image) 
        binary = image > thresh
        binary = binary.astype(np.int)
        if (len(image.shape) == 2) :
            binary = np.ones((image.shape[0], image.shape[1])) - binary
        elif (len(image.shape) == 3):
            binary = np.ones((binary.shape[0], binary.shape[1], binary.shape[2])) - binary
                            
        binary[binary<1] = 0
        cv.imwrite("./masks/"+file_name+"_mask.png", 255*binary)
        
        for i in range(10):
            self.progress_bar['value'] += 100/10
            time.sleep(0.1)
        
        if state == True:
            self.upload_button['image'] = self.upload_button_icon
            self.upload_button['command'] = self.upload_image
            self.view_project['state'] = NORMAL
                  
        self.progress_frame.grid(row=0, column=0, pady=30,  sticky="s")
        self.progress_bar.grid(row=0, column=0, sticky="s")
        
        time.sleep(1)
        self.window_2.destroy()

if __name__ == "__main__":
    fenetre = fenetre()
    fenetre.mainloop()

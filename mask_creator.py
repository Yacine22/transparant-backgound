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
                                    relief="flat", command=self.view_project)
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
        
    def view_project(self): 
        self.project_wind = Toplevel()
        self.project_wind.attributes('-fullscreen', True)
        self.project_wind.title("To Mask image transform")
        self.project_wind.configure(bg="#220794")
        self.w = self.project_wind.winfo_screenwidth()
    
        self.project_frame = Frame(self.project_wind, bg="#220794")
        self.project_frame.grid(row=0, column=0, sticky="news")
        
        self.label_frame = Frame(self.project_wind, bg="#220794")
        self.label_frame.grid(row=0, column=0, padx=int(self.w/10), pady=int(self.w/10), sticky="n")
        
        self.label_display = Label(self.label_frame)
        self.label_display['bd'] = 2
        self.label_display['relief'] = "flat"
        
        self.exit_button2 = Button(self.project_frame, text='Back', bg="#FF07FF", width=5, 
                                   height=2, fg="#210196", font=('TkDefaultFont',15,'bold'), 
                                  relief="ridge", command=self.project_wind.destroy)
        
        self.exit_button2.pack(side=RIGHT, anchor=NW)
        
        self.exit_button3 = Button(self.project_frame, text='Delet', state=DISABLED, bg="#FF07FF", width=5, 
                                   height=2, fg="#210196", font=('TkDefaultFont',15,'bold'), 
                                  relief="ridge", command=self.message_box)
        self.exit_button3.pack(side=RIGHT, anchor=NW)
        
        self.list_project = os.listdir("./masks/")
        self.list_project.sort()
        
        self.scrollbar = Scrollbar(self.project_frame, width=40)
        
        self.listeProjet = Listbox(self.project_frame, height=45, 
                                   yscrollcommand=self.scrollbar.set, 
                                       font=('TkDefaultFont', 12,'bold'))
        
        for projet in self.list_project:
            self.listeProjet.insert(END, projet)
        self.listeProjet.bind("<<ListboxSelect>>", self.selection)
        self.listeProjet.bind("<Return>", self.selection)
        
        self.project_wind.rowconfigure(0, weight=1)
        self.project_wind.columnconfigure(0, weight=1)
        
        self.scrollbar.pack(side=LEFT, anchor=NW, fill=Y)
        self.listeProjet.pack(side=LEFT, fill=Y)
        
        self.label_display.pack(anchor=CENTER)
        
              
    def selection(self, event):  
        self.exit_button3['state'] = NORMAL
        self.w = self.project_wind.winfo_screenwidth()
        projet_select = self.listeProjet.get(self.listeProjet.curselection())
        
        self.previewImg = Image.open("./masks/"+projet_select).resize((int(self.w/2), int(self.w/3)))
        self.image__ = ImageTk.PhotoImage(self.previewImg, Image.BILINEAR)
        
        self.label_display.configure(image=self.image__)
        
    
    def message_box(self):
        self.message_box = Toplevel()
        self.message_box.attributes('-fullscreen', True)
        self.message_box.configure(bg="#220794")
        
        projet_select = self.listeProjet.get(self.listeProjet.curselection())
        self.label_deleting = Label(self.message_box, text="Voulez-vous supprimer le Projet : "+str(projet_select), font=('Arial', 12, 'bold'))
        self.button_yes = Button(self.message_box, text="Yes", width=10, height=5, command=self.remove_selected)
        self.button_No = Button(self.message_box, text="No", width=10, height=5, command=self.message_box.destroy)
        
        self.message_box.rowconfigure(0, weight=1)
        self.message_box.columnconfigure(0, weight=1)
        
        self.label_deleting.grid(row=0, column=0, pady=5, sticky='news')
        self.button_yes.grid(row=1, column=0, pady=5, sticky='news')
        self.button_No.grid(row=2, column=0, pady=5, sticky='news')
        
    def remove_selected(self):
        projet_select = self.listeProjet.get(self.listeProjet.curselection())
        directotory_to_remove = "./masks/"+str(projet_select)
        os.remove(directotory_to_remove)
        self.message_box.destroy()
        self.project_wind.destroy()
        
        
          
        

if __name__ == "__main__":
    fenetre = fenetre()
    fenetre.mainloop()

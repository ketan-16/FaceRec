import tkinter as tk

def greet_user(name,f):
    popup = tk.Tk()
    windowWidth = popup.winfo_reqwidth()
    windowHeight = popup.winfo_reqheight()
    positionRight = int(popup.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(popup.winfo_screenheight()/2 - windowHeight/2)
    popup.geometry("440x150+{}+{}".format((positionRight-100), positionDown))
    popup.title(' ')
    popup.iconbitmap('favicon.ico')
    popup.resizable(0,0)
    if(f==0):
        greeting='Welcome, '+name
    else:
        greeting='Goodbye, '+name    
    greet_message = tk.Label(popup, text=greeting)
    greet_message.config(font=('', 20))
    greet_message.pack(pady=32)
    close_button = tk.Button(popup, text="        Close        ", command=popup.destroy)
    close_button.pack()
    popup.after(5000, lambda: popup.destroy())
    tk.mainloop()

greet_user('ketan',0)
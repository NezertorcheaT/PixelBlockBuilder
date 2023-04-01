from tkinter import *
from tkinter.filedialog import asksaveasfile, askopenfilename

from PIL import ImageTk

from main import *


def pl():
    blocksMatrix.place_id(IDDropString.get(), (int(XEntry.get()), int(YEntry.get()), int(ZEntry.get())))
    updc()


def sav():
    f = asksaveasfile(mode='w', initialfile='new pixel matrix.pbn', defaultextension=".pbn",
                      filetypes=[("All Files", "*.*"), ("Pixel Block Files", "*.pbn")])
    if f is None:
        return
    f.write(blocksMatrix.topbn())
    f.close()
    updc()


def opp():
    filename = askopenfilename(initialdir='/', title="Select .pbn File",
                               filetypes=(("Pixel Block Files", "*.pbn"), ("All Files", "*.*")))
    if filename == '':
        return
    global blocksMatrix
    blocksMatrix = BlocksMatrix(filename)
    updc()


def updc():
    global pilImage, image, c
    c.delete(ALL)
    pilImage = blocksMatrix.render()
    pilImage = pilImage.resize((c.winfo_width(), c.winfo_height()), Image.NEAREST)
    image = ImageTk.PhotoImage(pilImage)
    c.create_image(pilImage.width // 2, pilImage.height // 2, image=image)


def newbm():
    def cr():
        global blocksMatrix
        blocksMatrix = BlocksMatrix(size=(int(XEntry.get()), int(YEntry.get()), int(ZEntry.get())))

        newbmwindow.destroy()

    newbmwindow = Tk()
    newbmwindow.title("Create new Blocks Matrix")
    newbmwindow.geometry('200x70')
    newbmwindow.resizable(False, False)

    Poss = Frame(newbmwindow)
    POSLabel = Label(Poss, text="Size :")
    XEntry = Entry(Poss, width=8)
    YEntry = Entry(Poss, width=8)
    ZEntry = Entry(Poss, width=8)

    Label(newbmwindow, text="Create new Blocks Matrix").pack()
    POSLabel.pack(side=LEFT)
    XEntry.pack(side=LEFT)
    YEntry.pack(side=LEFT)
    ZEntry.pack(side=LEFT)
    Poss.pack()
    Button(newbmwindow, text='Create', command=cr).pack()

    newbmwindow.mainloop()


window = Tk()
window.title("Pixel Block Builder by NezertorcheaT")
window.geometry('200x350')
window.minsize(200, 350)

blocksMatrix = BlocksMatrix("", (5, 5, 5))

f = Frame(window)
c = Canvas(f, width=200, height=200, bg='white')

blocksMatrix.place_id("pb.box", (0, 0, 0))
blocksMatrix.place_id("pb.box", (1, 0, 0))

pilImage = blocksMatrix.render()
image = ImageTk.PhotoImage(pilImage)
c.create_image(pilImage.width, pilImage.height, image=image)

Poss = Frame(window)
idss = Frame(window)

POSLabel = Label(Poss, text="Pos:")
XEntry = Entry(Poss, width=8)
YEntry = Entry(Poss, width=8)
ZEntry = Entry(Poss, width=8)

IDDropString = StringVar()

# initial menu text
IDDropString.set("null")

# Create Dropdown menu
IDDrop = OptionMenu(idss, IDDropString, *all_ids)
IDLabel = Label(idss, text="ID")

opsavbats = Frame(window)

btnPlace = Button(window, text='Place', command=pl)
btnSave = Button(opsavbats, text='Save', command=sav)
btnOpen = Button(opsavbats, text='Open', command=opp)

btnSave.pack(side=LEFT)
btnOpen.pack(side=RIGHT)
Button(opsavbats, text='New Matrix', command=newbm).pack()
opsavbats.pack()

f.pack(fill=BOTH, expand=YES)
c.pack(fill=BOTH, expand=YES)

POSLabel.pack(side=LEFT)
XEntry.pack(side=LEFT)
YEntry.pack(side=LEFT)
ZEntry.pack(side=LEFT)
Poss.pack()

IDLabel.pack(side=LEFT)
IDDrop.pack()
idss.pack()

btnPlace.pack()


def update():
    updc()
    window.after(100, update)


window.after(0, update)
window.mainloop()

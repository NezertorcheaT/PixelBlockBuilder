from tkinter import *
from tkinter.filedialog import asksaveasfile, askopenfilename

from PIL import ImageTk

from main import *


def pl():
    blocksMatrix.place_id(IDEntry.get(), (int(XEntry.get()), int(YEntry.get()), int(ZEntry.get())))
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
    image = ImageTk.PhotoImage(pilImage)
    c.create_image(pilImage.width, pilImage.height, image=image)

window = Tk()
window.title("Pixel Block Builder by NezertorcheaT")
window.geometry('200x300')

blocksMatrix = BlocksMatrix("", (5, 5, 5))

c = Canvas(window, width=200, height=200, bg='white')
c.pack()

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

IDLabel = Label(idss, text="ID")
IDEntry = Entry(idss, width=16)

opsavbats = Frame(window)

btnPlace = Button(window, text='Place', command=pl)
btnSave = Button(opsavbats, text='Save', command=sav)
btnOpen = Button(opsavbats, text='Open', command=opp)


btnSave.pack(side=LEFT)
btnOpen.pack(side=RIGHT)
opsavbats.pack()

c.pack()

POSLabel.pack(side=LEFT)
XEntry.pack(side=LEFT)
YEntry.pack(side=LEFT)
ZEntry.pack(side=LEFT)
Poss.pack()

IDLabel.pack(side=LEFT)
IDEntry.pack(side=LEFT)
idss.pack()

btnPlace.pack()

window.mainloop()

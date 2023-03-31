import json
from random import randint

import glm
import numpy as np
from PIL import Image


class Block:
    def __init__(self, ID: str = ""):
        self.ID = ID

    @staticmethod
    def get_path_from_id(ID: str) -> str:
        if ID == "null":
            return ""

        with open(f'images/ids.json', "r") as fh:
            l = json.load(fh).get(ID, None)
            if l is None:
                return ""
            else:
                return "images/" + l


class BlocksMatrix:
    def __init__(self, path: str = "", size: "tuple[int,int,int] | list[int,int,int]" = None):
        if path == "":
            if size is None:
                self.blocksMatrix: np.array = np.full((5, 5, 5), "", np.dtype("<U256"))
                self.maxx = 5
                self.maxy = 5
                self.maxz = 5
            else:
                self.blocksMatrix: np.array = np.full(size, "", np.dtype("<U256"))
                self.maxx, self.maxy, self.maxz = size
        else:
            with open(path, "r") as fh:
                fhr = fh.read()
                ff = str.split(fhr, "\n")
                self.maxx = int(ff[0])
                self.maxy = int(ff[1])
                self.maxz = int(ff[2])
                ff = np.array(ff[3:])
                ff = ff.reshape((self.maxx, self.maxy, self.maxz))
                ff = np.vectorize(Block.get_path_from_id)(ff)
                self.blocksMatrix = ff

    def topbn(self):
        with open(f'images/ids.json', "r") as fh:
            ff: dict = json.load(fh)
            ff: dict = dict(zip(ff.values(), ff.keys()))
            st: str = f'{self.maxx}\n{self.maxy}\n{self.maxz}\n'
            for z in np.arange(self.maxz):
                for x in np.arange(self.maxx):
                    for y in np.arange(self.maxy):
                        st += ff.get(self.blocksMatrix[x, y, z].replace('images/',''), "null")
                        st += '\n'
            return st[:-1]

    @staticmethod
    def random_matrix(size: "tuple[int,int,int] | list[int,int,int]"):
        with open(f'images/ids.json', "r") as fh:
            ff: dict = json.load(fh)
            bm = BlocksMatrix(size=size)
            print(bm.blocksMatrix.dtype)
            for z in np.arange(bm.maxz):
                for x in np.arange(bm.maxx):
                    for y in np.arange(bm.maxy):
                        n = list(ff.values())[randint(0, len(ff.values()) - 1)]
                        if n != "":
                            n = f"images/{n}"
                        bm.blocksMatrix[x, y, z] = n
                        print(bm.blocksMatrix[x, y, z])
            print(bm.blocksMatrix)
            return bm

    def place(self, block: Block, pos: tuple[int, int, int]):
        self.blocksMatrix[pos] = Block.get_path_from_id(block.ID)

    def place_id(self, ID: str, pos: tuple[int, int, int]):
        self.blocksMatrix[pos] = Block.get_path_from_id(ID)

    def render(self):
        im = Image.new("RGBA",
                       (self.maxx * 8 + self.maxy * 8, self.maxx * 4 + (self.maxy - 1) * 4 + self.maxz * 10 + 2))
        pcs = 0
        for z in np.arange(self.maxz):
            for x in np.arange(self.maxx):
                for y in np.arange(self.maxy):
                    if self.blocksMatrix[x, y, z] == "":
                        continue

                    pos = glm.vec2(z * -8, z * 4)
                    pos += glm.vec2(y * 8, y * 4)
                    pos += glm.vec2(0, x * -10)
                    pos += glm.vec2(int(im.size[0] * (24 / 64)), int(im.size[1] * (30 / 70)))

                    topaste = Image.open(self.blocksMatrix[x, y, z])
                    neww = Image.new("RGBA", (im.width, im.height))

                    neww.paste(topaste, (int(pos.x), int(pos.y)))

                    im.alpha_composite(neww)
                    pcs += 1
        return im

# print(BlocksMatrix("Pixel Block by NezertorcheaT.pbn").render())
# print(Block.get_path_from_id("pbb.ramp_up_z_270"))
# print(Block("pb.ramp_up_z_270").ID)

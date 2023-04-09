import json
import os
import shutil
from random import randint
from tkinter.messagebox import showerror

import glm
import numpy as np
from PIL import Image


def clamp(num: 'int|float', min_value: 'int|float', max_value: 'int|float'):
    return max(min(num, max_value), min_value)




class IDHandler:
    def __init__(self):
        self.path = f'{os.path.dirname(__file__)}\\images'

        if not os.path.exists(self.path):
            showerror(title="Path Error!", message=f"Path \"{self.path}\" does not exist")
            raise FileExistsError(f"Path \"{self.path}\" does not exist")

        self.folders = next(os.walk(self.path))[1]
        self.full = {}
        self.all_ids = []
        self.all_ids_to_ui = []
        self.all_values = []
        self.all_datas = []

        for i in self.folders:
            with open(f'{self.path}\\{i}\\ids.json', "r") as fh:
                this_full = json.load(fh)
                self.full.update(this_full)
                this_ids = list(this_full.keys())
                self.all_ids += this_ids
                for j in this_full:
                    if this_full[j]['hidden'] is False:
                        self.all_ids_to_ui += [j]
                this_values = list(self.full.values())
                self.all_values += this_values
                self.all_datas += list(
                    (f'{self.path}\\{i}\\{this_full[j].get("data", "")}' if this_full[j].get("data", "") != '' else '')
                    for j in this_full)
        j = 0
        for i in self.full:
            self.full[i]["data"] = self.all_datas[j]
            j += 1
        self.dataToId = dict(zip((i.get("data", "") for i in self.all_values), self.all_ids))


idsHandler = IDHandler()


class Block:
    def __init__(self, ID: str = ""):
        self.ID = ID
        self.color = (255, 255, 255, 255)

    @staticmethod
    def get_param_from_id(ID: str, param: str = "data") -> str:
        l = idsHandler.full.get(ID, None)
        return '' if l is None else l.get(param)

    @staticmethod
    def matrix_pos_to_image_pos(pos: tuple[int, int, int]) -> tuple[int, int]:
        x, y, z = pos
        new_pos = glm.vec2(x * -8, x * 4)
        new_pos += glm.vec2(y * 8, y * 4)
        new_pos += glm.vec2(0, z * -8)
        return int(new_pos.x), int(new_pos.y)

    @staticmethod
    def matrix_pos_to_image_pos_glm(pos: glm.vec3) -> glm.vec2:
        return glm.vec2((pos.y - pos.x) * 8, (pos.x + pos.y) * 4 + pos.z * -9)


def clear_render_folder(path: str):
    folder = path
    for filename in os.listdir(folder):
        if 'null.png' in filename:
            continue
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


class BlocksMatrix:
    def __init__(self, path: str = "", size: "tuple[int,int,int] | list[int,int,int]" = None):
        if path == "":
            if size is None:
                self.blocksMatrix: np.array = np.full((5, 5, 5), {'id': 'null', 'color': (255, 255, 255, 255)})
                self.maxx = 5
                self.maxy = 5
                self.maxz = 5
            else:
                self.blocksMatrix: np.array = np.full(size, {'id': 'null', 'color': (255, 255, 255, 255)})
                self.maxx, self.maxy, self.maxz = size
        else:
            with open(path, "r") as fh:
                fhr = fh.read()
                ff = str.split(fhr, "\n")
                ids = []
                for i in ff:
                    if len(str.split(i, ";")) == 1:
                        ids += [i]
                        continue

                    aids = str.split(i, ";")
                    idd_colors = str.split(aids[1], ',')
                    idd_colors_int = ()

                    for j in idd_colors:
                        idd_colors_int += (int(j),)

                    ids += [[aids[0], idd_colors_int]]

                mm = str.split(ids[0], ',')
                self.maxx = int(mm[0])
                self.maxy = int(mm[1])
                self.maxz = int(mm[2])

                ids = ids[1:]
                d = []

                for i in ids:
                    d += [{'id': i[0], 'color': i[1]}]

                self.blocksMatrix = np.array(d).reshape((self.maxx, self.maxy, self.maxz))
        self.size = (self.maxx, self.maxy, self.maxz)

    def topbn(self):
        st: str = f'{self.maxx},{self.maxy},{self.maxz}\n'
        for x in np.arange(self.maxx):
            for y in np.arange(self.maxy):
                for z in np.arange(self.maxz):
                    print(self.blocksMatrix[x, y, z]["color"])
                    st += f'{self.blocksMatrix[x, y, z]["id"]};{self.blocksMatrix[x, y, z]["color"][0]},{self.blocksMatrix[x, y, z]["color"][1]},{self.blocksMatrix[x, y, z]["color"][2]},{self.blocksMatrix[x, y, z]["color"][3]}\n'
        return st[:-1]

    @staticmethod
    def random_matrix(size: "tuple[int,int,int] | list[int,int,int]"):
        bm = BlocksMatrix(size=size)
        for z in np.arange(bm.maxz):
            for x in np.arange(bm.maxx):
                for y in np.arange(bm.maxy):
                    n = list(idsHandler.full.values())[randint(0, len(idsHandler.full.values()) - 1)]
                    if n != "":
                        n = f"images\\{n}"
                    bm.blocksMatrix[x, y, z] = n
        return bm

    def place(self, block: Block, pos: tuple[int, int, int], color=(255, 255, 255, 255)):
        if block.ID in idsHandler.all_ids:
            self.blocksMatrix[pos] = {'id': block.ID, 'color': color}

    def place_id(self, ID: str, pos: tuple[int, int, int], color=(255, 255, 255, 255)):
        if ID in idsHandler.all_ids:
            self.blocksMatrix[pos] = {'id': ID, 'color': color}

    def get_brightness(self, pos: tuple[int, int, int]) -> float:
        x, y, z = pos

        if z == self.maxz - 1:
            return 1

        for i in np.arange(z + 1, self.maxz, 1):
            if i == self.maxz - 1:
                return 1
            if self.blocksMatrix[
                clamp(x, -self.maxx + 1, self.maxx - 1),
                clamp(y, -self.maxy + 1, self.maxy - 1),
                clamp(i, -self.maxz + 1, self.maxz - 1)
            ]['id'] == 'null':
                return 1
            else:
                return self.get_brightness((x, y, i)) / 2
        return 0

    def get_image_size(self) -> tuple[int, int]:

        max_x00 = Block.matrix_pos_to_image_pos_glm(glm.vec3(self.maxx, 0, 0))
        max_xy0 = Block.matrix_pos_to_image_pos_glm(glm.vec3(self.maxx, self.maxy, 0))
        max_0xz = Block.matrix_pos_to_image_pos_glm(glm.vec3(0, self.maxy, self.maxz))
        max_0y0 = Block.matrix_pos_to_image_pos_glm(glm.vec3(0, self.maxy, 0))
        max_00z = Block.matrix_pos_to_image_pos_glm(glm.vec3(0, 0, self.maxz))

        return int((min(max_x00.x, max_xy0.x, max_0xz.x, max_0y0.x, max_00z.x)) * -2), \
               int((max(max_x00.y, max_xy0.y, max_0xz.y, max_0y0.y, max_00z.y) + 4) * 2)

    def clamped_get_from_blocksMatrix(self, x: int, y: int, z: int) -> str:
        return self.blocksMatrix[clamp(x, 0, self.maxx - 1), clamp(y, 0, self.maxy - 1), clamp(z, 0, self.maxz - 1)]

    def render(self, save_frames=False, path=f'{os.path.dirname(__file__)}\\render', shadows=True):
        if save_frames:
            clear_render_folder(path)
        im = Image.new("RGBA", self.get_image_size(), color=(0, 0, 0, 0))
        pcs = 0

        for z in np.arange(self.maxz):
            for y in np.arange(self.maxy):
                for x in np.arange(self.maxx):

                    if self.blocksMatrix[x, y, z]['id'] == "null":
                        continue

                    pos = Block.matrix_pos_to_image_pos_glm(glm.vec3(x, y, z))
                    pos += glm.vec2(im.size[0] / 2 - 8, im.size[1] / 2 - 4)

                    topaste = Image.open(Block.get_param_from_id(self.blocksMatrix[x, y, z]['id']))
                    topaste = topaste.convert('RGBA')
                    datas = topaste.getdata()

                    newData = []

                    for i in datas:
                        newData.append((int(i[0] * self.blocksMatrix[x, y, z]['color'][0] / 255 *
                                            (self.get_brightness((x, y, z)) if shadows else 1)),
                                        int(i[1] * self.blocksMatrix[x, y, z]['color'][1] / 255 *
                                            (self.get_brightness((x, y, z)) if shadows else 1)),
                                        int(i[2] * self.blocksMatrix[x, y, z]['color'][2] / 255 *
                                            (self.get_brightness((x, y, z)) if shadows else 1)),
                                        int(i[3] * self.blocksMatrix[x, y, z]['color'][3] / 255)))

                    topaste.putdata(newData)
                    topaste.convert("RGBA")

                    neww = Image.new("RGBA", (im.width, im.height))

                    neww.paste(topaste, (int(pos.x), int(pos.y)))

                    im.alpha_composite(neww)
                    pcs += 1

                    if save_frames:
                        im.save(f"{path}\\m_Image {pcs} ({x}, {y}, {z}).png")

        return im

# print(BlocksMatrix('C:/Users/tigri/PycharmProjects/PixelBlockBuilder/PixelBlockBuilder/examples/box.pbn').blocksMatrix)

import json
import os
import shutil
from random import randint
from typing import Any

import glm
import numpy as np
from PIL import Image, ImageEnhance


def clamp(num: 'int|float', min_value: 'int|float', max_value: 'int|float'):
    return max(min(num, max_value), min_value)


class IDHandler:
    def __init__(self):
        self.path = f'{os.path.dirname(__file__)}\\images'
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

    @staticmethod
    def get_param_from_id(ID: str, param: str = "data") -> Any:
        l = idsHandler.full.get(ID, None)
        return '' if l is None else l.get(param)

    @staticmethod
    def matrix_pos_to_image_pos(pos: tuple[int, int, int]) -> tuple[int, int]:
        x, y, z = pos
        new_pos = glm.vec2(x * -8, x * 4)
        new_pos += glm.vec2(y * 8, y * 4)
        new_pos += glm.vec2(0, z * -9)
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
                self.blocksMatrix: np.array = np.full((5, 5, 5), "null", np.dtype("<U256"))
                self.maxx = 5
                self.maxy = 5
                self.maxz = 5
            else:
                self.blocksMatrix: np.array = np.full(size, "null", np.dtype("<U256"))
                self.maxx, self.maxy, self.maxz = size
        else:
            with open(path, "r") as fh:
                fhr = fh.read()
                ff = str.split(fhr, "\n")
                mm = str.split(ff[0], ',')
                self.maxx = int(mm[0])
                self.maxy = int(mm[1])
                self.maxz = int(mm[2])
                ff = np.array(ff[1:], np.dtype("<U256"))
                ff = ff.reshape((self.maxx, self.maxy, self.maxz))
                self.blocksMatrix = ff
        self.size = (self.maxx, self.maxy, self.maxz)

    def topbn(self):
        st: str = f'{self.maxx},{self.maxy},{self.maxz}\n'
        for x in np.arange(self.maxx):
            for y in np.arange(self.maxy):
                for z in np.arange(self.maxz):
                    st += f'{self.blocksMatrix[x, y, z]}\n'
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

    def place(self, block: Block, pos: tuple[int, int, int]):
        if block.ID in idsHandler.all_ids:
            self.blocksMatrix[pos] = Block.get_param_from_id(block.ID)

    def place_id(self, ID: str, pos: tuple[int, int, int]):
        if ID in idsHandler.all_ids:
            self.blocksMatrix[pos] = ID

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
            ] == 'null':
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

    def render(self, save_frames=False, path=f'{os.path.dirname(__file__)}\\render'):
        if save_frames:
            clear_render_folder(path)
        im = Image.new("RGBA", self.get_image_size(), color=(0, 0, 0, 0))
        pcs = 0

        for z in np.arange(self.maxz):
            for y in np.arange(self.maxy):
                for x in np.arange(self.maxx):

                    if self.blocksMatrix[x, y, z] == "null":
                        continue

                    pos = Block.matrix_pos_to_image_pos_glm(glm.vec3(x, y, z))
                    pos += glm.vec2(im.size[0] / 2 - 8, im.size[1] / 2 - 4)

                    topaste = Image.open(Block.get_param_from_id(self.blocksMatrix[x, y, z]))
                    topaste = topaste.convert('RGBA')
                    filter = ImageEnhance.Brightness(topaste)
                    topaste = filter.enhance(self.get_brightness((x, y, z)))

                    neww = Image.new("RGBA", (im.width, im.height))

                    neww.paste(topaste, (int(pos.x), int(pos.y)))

                    im.alpha_composite(neww)
                    pcs += 1

                    if save_frames:
                        im.save(f"{path}\\m_Image {pcs} ({x}, {y}, {z}).png")
        return im

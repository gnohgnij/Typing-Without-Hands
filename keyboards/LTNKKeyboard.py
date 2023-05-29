import cv2
from enum import Enum
from time import time
import json
import csv
import pandas as pd

class ProgressBar():

    def __init__(self, pos, size=[40, 5]):
        self.size = size
        self.percentage = 0
        self.color = (0, 0, 0)
        self.pos = pos
        self.start = None

class Button:
    '''
    Button parent class
    '''
    def __init__(self, pos, text, color, size):
        self.pos = pos
        self.text = text
        self.size = size
        self.clicked = False
        self.color = color
        self.text_color = (0, 0, 0)
        self.progress = ProgressBar((pos[0]+30, pos[1]+100))
    
    def draw(self, img, textOffset):
        # draw the button
        x, y = self.pos
        w, h = self.size
        cv2.rectangle(img, self.pos, (x+w, y+h), self.color, cv2.FILLED)
        cv2.line(img, self.pos, (x, y+h), (0, 0, 0), 2)
        cv2.line(img, self.pos, (x+w, y), (0, 0, 0), 2)
        cv2.line(img, (x+w, y), (x+w, y+h), (0, 0, 0), 2)
        cv2.line(img, (x, y+h), (x+w, y+h), (0, 0, 0), 2)

        if self.text.lower() == 'abcdefghij' or self.text.lower() == 'klmnopqrst' or self.text.lower() == 'uvwxyz' or self.text == '!@#$%^&*()' or self.text == '-=[]\\;\',./' or self.text == '_+{}|:"<>?':
            cv2.putText(img, self.text[:5], (x+textOffset[0], y+textOffset[1]), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, self.text_color, 1, cv2.LINE_AA)
            cv2.putText(img, self.text[5:], (x+textOffset[0], y+textOffset[1]+30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, self.text_color, 1, cv2.LINE_AA)
        else:
            cv2.putText(img, self.text, (x+textOffset[0], y+textOffset[1]), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, self.text_color, 1, cv2.LINE_AA)

        # draw the progress bar
        x, y = self.progress.pos
        w, h = self.progress.size
        cv2.rectangle(img, self.progress.pos, (x+w, y+h), self.progress.color)
        progress_width = int(self.progress.percentage/100 * w)
        cv2.rectangle(img, self.progress.pos, (x+progress_width, y+h), self.progress.color, cv2.FILLED)

    def is_inside(self, x, y):
        '''
        Returns true if the button is within the given coordinates
        '''
        x1, y1 = self.pos
        x2, y2 = x1 + self.size[0], y1 + self.size[1]
        if x1 <= x <= x2 and y1 <= y <= y2:
            return True

        return False

    def is_clicked(self, x, y):
        '''
        Returns true if the button is clicked
        '''
        return self.is_inside(x, y)
       

    def is_hovered_over(self, x, y):
        '''
        Returns true if the button is being hovered over
        '''
        return self.is_inside(x, y)

    def mid_point(self):
        """
        Returns the mid point of the button
        """
        x1, y1 = self.pos
        x2, y2 = x1 + self.size[0], y1 + self.size[1]
        return (int((x1+x2)//2 * 1.125), int((y1+y2)//2 * 1.25))

class NormalButton(Button):
    '''
    A normal button like 'a', 'b', 'c', '1', '2', '3' etc.
    '''
    def __init__(self, pos, text, color, size=[125, 125]):
        super().__init__(pos, text, color, size)
    
    def draw(self, img, textOffset=[10, 35]):
        super().draw(img, textOffset)

class Switch(Button):
    def __init__(self, pos, text, color, size=[194, 125]):
        super().__init__(pos, text, color, size)
    
    def draw(self, img, textOffset=[10, 35]):
        super().draw(img, textOffset)

class Delete(Button):
    '''
    A delete button
    '''
    def __init__(self, pos, color, text="Delete", size=[194, 125]):
        super().__init__(pos, text, color, size)
    
    def draw(self, img, textOffset=[10, 35]):
        super().draw(img, textOffset)

class Enter(Button):
    '''
    An enter button
    '''
    def __init__(self, pos, color, text="Enter", size=[194, 125]):
        super().__init__(pos, text, color, size)
    
    def draw(self, img, textOffset=[10, 35]):
        super().draw(img, textOffset)

class Shift(Button):
    '''
    A shift button
    '''
    def __init__(self, pos, color, text="Shift", size=[194, 125]):
        super().__init__(pos, text, color, size)
    
    def draw(self, img, textOffset=[10, 35]):
        super().draw(img, textOffset)

class SpaceBar(Button):
    '''
    A space bar button
    '''
    def __init__(self, pos, color, text="Space", size=[625, 125]):
        self.pos = pos
        self.text = text
        self.size = size
        self.clicked = False
        self.color = color
        self.text_color = (0, 0, 0)
        self.progress = ProgressBar((pos[0]+300, pos[1]+70))
    
    def draw(self, img, textOffset=[280, 35]):
        super().draw(img, textOffset)

class Back(Button):
    '''
    A back button
    '''
    def __init__(self, pos, color, text="...", size=[194, 125]):
        super().__init__(pos, text, color, size)
    
    def draw(self, img, textOffset=[10, 35]):
        super().draw(img, textOffset)

class Keyboard_Page(Enum):
    DEFAULT = 0
    DEFAULT_CAPS = 1
    A_TO_J = 2
    A_TO_J_CAPS = 3
    K_TO_T = 4
    K_TO_T_CAPS = 5
    U_TO_Z = 6
    U_TO_Z_CAPS = 7
    NUMS = 8
    NUMS_CAPS = 9
    SYMBOLS_1 = 10
    SYMBOLS_1_CAPS = 11
    SYMBOLS_2 = 12
    SYMBOLS_2_CAPS = 13
    SYMBOLS_3 = 14
    SYMBOLS_3_CAPS = 15

class LTNKKeyboard:
    
    def __init__(self):
        self.keyboard_page = Keyboard_Page.DEFAULT

        self.default_keys = [['abcdefghij', 'klmnopqrst', 'uvwxyz', '0-9', '!@#$%^&*()'],
                            ['-=[]\\;\',./', '_+{}|:"<>?']]

        self.default_caps_keys = [['ABCDEFGHIJ', 'KLMNOPQRST', 'UVWXYZ', '0-9', '!@#$%^&*()'],
                                ['-=[]\\;\',./', '_+{}|:"<>?']]

        self.a_to_j_keys = [['a', 'b', 'c', 'd', 'e'], ['f', 'g', 'h', 'i', 'j']]

        self.a_to_j_caps_keys = [['A', 'B', 'C', 'D', 'E'], ['F', 'G', 'H', 'I', 'J']]

        self.k_to_t_keys = [['k', 'l', 'm', 'n', 'o'], ['p', 'q', 'r', 's', 't']]

        self.k_to_t_caps_keys = [['K', 'L', 'M', 'N', 'O'], ['P', 'Q', 'R', 'S', 'T']]

        self.u_to_z_keys = [['u', 'v', 'w', 'x', 'y'], ['z']]

        self.u_to_z_caps_keys = [['U', 'V', 'W', 'X', 'Y'], ['Z']]

        self.number_keys = [['0', '1', '2', '3', '4'], ['5', '6', '7', '8', '9']]

        self.symbols1_keys = [['!', '@', '#', '$', '%'], ['^', '&', '*', '(', ')']]

        self.symbols2_keys = [['-', '=', '[', ']', '\\'], [';', "'", ',', '.', '/']]

        self.symbols3_keys = [['_', '+', '{', '}', '|'], [':', '"', '<', '>', '?']]

        self.button_list = []

        self.test_letters = ['']
        self.inputs = []
        self.index = 0
        self.start_time = None
        self.all_times = []

        self.set_default_keys()

    def set_default_keys(self):
        self.button_list.clear()

        self.button_list.append(Back((134, 172), (174, 174, 174)))

        for i in range(len(self.default_keys[0])):
            self.button_list.append(NormalButton((125 * i + 328, 172), self.default_keys[0][i], (255, 255, 255)))

        self.button_list.append(Delete((953, 172), (255, 255, 255)))

        self.button_list.append(Shift((134, 297), (255, 255, 255)))
        
        for i in range(len(self.default_keys[1])):
            self.button_list.append(NormalButton((125 * i + 328, 297), self.default_keys[1][i], (255, 255, 255)))

        self.button_list.append(Enter((953, 297), (255, 255, 255)))

        self.button_list.append(SpaceBar((328, 422), (255, 255, 255)))

    def set_default_caps_keys(self):
        self.button_list.clear()

        self.button_list.append(Back((134, 172), (174, 174, 174)))

        for i in range(len(self.default_caps_keys[0])):
            self.button_list.append(NormalButton((125 * i + 328, 172), self.default_caps_keys[0][i], (255, 255, 255)))

        self.button_list.append(Delete((953, 172), (255, 255, 255)))

        self.button_list.append(Shift((134, 297), (255, 255, 255)))
        
        for i in range(len(self.default_caps_keys[1])):
            self.button_list.append(NormalButton((125 * i + 328, 297), self.default_caps_keys[1][i], (255, 255, 255)))

        self.button_list.append(Enter((953, 297), (255, 255, 255)))

        self.button_list.append(SpaceBar((328, 422), (255, 255, 255)))

    def set_a_to_j_keys(self):
        self.button_list.clear()

        self.button_list.append(Back((134, 172), (255, 255, 255)))

        for i in range(len(self.a_to_j_keys[0])):
            self.button_list.append(NormalButton((125 * i + 328, 172), self.a_to_j_keys[0][i], (255, 255, 255)))

        self.button_list.append(Delete((953, 172), (255, 255, 255)))

        self.button_list.append(Shift((134, 297), (255, 255, 255)))
        
        for i in range(len(self.a_to_j_keys[1])):
            self.button_list.append(NormalButton((125 * i + 328, 297), self.a_to_j_keys[1][i], (255, 255, 255)))

        self.button_list.append(Enter((953, 297), (255, 255, 255)))

        self.button_list.append(SpaceBar((328, 422), (255, 255, 255)))

        self.button_list.append(Switch((134, 422), '_+{}|:"<>?', (255, 255, 255)))

        self.button_list.append(Switch((953, 422), 'klmnopqrst', (255, 255, 255)))


    def set_a_to_j_caps_keys(self):
        self.button_list.clear()

        self.button_list.append(Back((134, 172), (255, 255, 255)))

        for i in range(len(self.a_to_j_caps_keys[0])):
            self.button_list.append(NormalButton((125 * i + 328, 172), self.a_to_j_caps_keys[0][i], (255, 255, 255)))

        self.button_list.append(Delete((953, 172), (255, 255, 255)))

        self.button_list.append(Shift((134, 297), (255, 255, 255)))
        
        for i in range(len(self.a_to_j_caps_keys[1])):
            self.button_list.append(NormalButton((125 * i + 328, 297), self.a_to_j_caps_keys[1][i], (255, 255, 255)))

        self.button_list.append(Enter((953, 297), (255, 255, 255)))

        self.button_list.append(SpaceBar((328, 422), (255, 255, 255)))

        self.button_list.append(Switch((134, 422), '_+{}|:"<>?', (255, 255, 255)))

        self.button_list.append(Switch((953, 422), 'KLMNOPQRST', (255, 255, 255)))

    def set_k_to_t_keys(self):
        self.button_list.clear()

        self.button_list.append(Back((134, 172), (255, 255, 255)))

        for i in range(len(self.k_to_t_keys[0])):
            self.button_list.append(NormalButton((125 * i + 328, 172), self.k_to_t_keys[0][i], (255, 255, 255)))

        self.button_list.append(Delete((953, 172), (255, 255, 255)))

        self.button_list.append(Shift((134, 297), (255, 255, 255)))
        
        for i in range(len(self.k_to_t_keys[1])):
            self.button_list.append(NormalButton((125 * i + 328, 297), self.k_to_t_keys[1][i], (255, 255, 255)))

        self.button_list.append(Enter((953, 297), (255, 255, 255)))

        self.button_list.append(SpaceBar((328, 422), (255, 255, 255)))

        self.button_list.append(Switch((134, 422), 'abcdefghij', (255, 255, 255)))

        self.button_list.append(Switch((953, 422), 'uvwxyz', (255, 255, 255)))

    def set_k_to_t_caps_keys(self):
        self.button_list.clear()

        self.button_list.append(Back((134, 172), (255, 255, 255)))

        for i in range(len(self.k_to_t_caps_keys[0])):
            self.button_list.append(NormalButton((125 * i + 328, 172), self.k_to_t_caps_keys[0][i], (255, 255, 255)))

        self.button_list.append(Delete((953, 172), (255, 255, 255)))

        self.button_list.append(Shift((134, 297), (255, 255, 255)))
        
        for i in range(len(self.k_to_t_caps_keys[1])):
            self.button_list.append(NormalButton((125 * i + 328, 297), self.k_to_t_caps_keys[1][i], (255, 255, 255)))

        self.button_list.append(Enter((953, 297), (255, 255, 255)))

        self.button_list.append(SpaceBar((328, 422), (255, 255, 255)))

        self.button_list.append(Switch((134, 422), 'ABCDEFGHIJ', (255, 255, 255)))

        self.button_list.append(Switch((953, 422), 'UVWXYZ', (255, 255, 255)))

    def set_u_to_z_keys(self):
        self.button_list.clear()

        self.button_list.append(Back((134, 172), (255, 255, 255)))

        for i in range(len(self.u_to_z_keys[0])):
            self.button_list.append(NormalButton((125 * i + 328, 172), self.u_to_z_keys[0][i], (255, 255, 255)))

        self.button_list.append(Delete((953, 172), (255, 255, 255)))

        self.button_list.append(Shift((134, 297), (255, 255, 255)))
        
        for i in range(len(self.u_to_z_keys[1])):
            self.button_list.append(NormalButton((125 * i + 328, 297), self.u_to_z_keys[1][i], (255, 255, 255)))

        self.button_list.append(Enter((953, 297), (255, 255, 255)))

        self.button_list.append(SpaceBar((328, 422), (255, 255, 255)))

        self.button_list.append(Switch((134, 422), 'klmnopqrst', (255, 255, 255)))

        self.button_list.append(Switch((953, 422), '0-9', (255, 255, 255)))

    def set_u_to_z_caps_keys(self):
        self.button_list.clear()

        self.button_list.append(Back((134, 172), (255, 255, 255)))

        for i in range(len(self.u_to_z_caps_keys[0])):
            self.button_list.append(NormalButton((125 * i + 328, 172), self.u_to_z_caps_keys[0][i], (255, 255, 255)))

        self.button_list.append(Delete((953, 172), (255, 255, 255)))

        self.button_list.append(Shift((134, 297), (255, 255, 255)))
        
        for i in range(len(self.u_to_z_caps_keys[1])):
            self.button_list.append(NormalButton((125 * i + 328, 297), self.u_to_z_caps_keys[1][i], (255, 255, 255)))

        self.button_list.append(Enter((953, 297), (255, 255, 255)))

        self.button_list.append(SpaceBar((328, 422), (255, 255, 255)))

        self.button_list.append(Switch((134, 422), 'KLMNOPQRST', (255, 255, 255)))

        self.button_list.append(Switch((953, 422), '0-9', (255, 255, 255)))

    def set_number_keys(self):
        self.button_list.clear()

        self.button_list.append(Back((134, 172), (255, 255, 255)))

        for i in range(len(self.number_keys[0])):
            self.button_list.append(NormalButton((125 * i + 328, 172), self.number_keys[0][i], (255, 255, 255)))

        self.button_list.append(Delete((953, 172), (255, 255, 255)))

        self.button_list.append(Shift((134, 297), (255, 255, 255)))
        
        for i in range(len(self.number_keys[1])):
            self.button_list.append(NormalButton((125 * i + 328, 297), self.number_keys[1][i], (255, 255, 255)))

        self.button_list.append(Enter((953, 297), (255, 255, 255)))

        self.button_list.append(SpaceBar((328, 422), (255, 255, 255)))

        self.button_list.append(Switch((134, 422), 'uvwxyz', (255, 255, 255)))

        self.button_list.append(Switch((953, 422), '!@#$%^&*()', (255, 255, 255)))

    def set_number_keys_caps(self):
        self.button_list.clear()

        self.button_list.append(Back((134, 172), (255, 255, 255)))

        for i in range(len(self.number_keys[0])):
            self.button_list.append(NormalButton((125 * i + 328, 172), self.number_keys[0][i], (255, 255, 255)))

        self.button_list.append(Delete((953, 172), (255, 255, 255)))

        self.button_list.append(Shift((134, 297), (255, 255, 255)))
        
        for i in range(len(self.number_keys[1])):
            self.button_list.append(NormalButton((125 * i + 328, 297), self.number_keys[1][i], (255, 255, 255)))

        self.button_list.append(Enter((953, 297), (255, 255, 255)))

        self.button_list.append(SpaceBar((328, 422), (255, 255, 255)))

        self.button_list.append(Switch((134, 422), 'UVWXYZ', (255, 255, 255)))

        self.button_list.append(Switch((953, 422), '!@#$%^&*()', (255, 255, 255)))

    def set_symbols1_keys(self):
        self.button_list.clear()

        self.button_list.append(Back((134, 172), (255, 255, 255)))

        for i in range(len(self.symbols1_keys[0])):
            self.button_list.append(NormalButton((125 * i + 328, 172), self.symbols1_keys[0][i], (255, 255, 255)))

        self.button_list.append(Delete((953, 172), (255, 255, 255)))

        self.button_list.append(Shift((134, 297), (255, 255, 255)))
        
        for i in range(len(self.symbols1_keys[1])):
            self.button_list.append(NormalButton((125 * i + 328, 297), self.symbols1_keys[1][i], (255, 255, 255)))

        self.button_list.append(Enter((953, 297), (255, 255, 255)))

        self.button_list.append(SpaceBar((328, 422), (255, 255, 255)))

        self.button_list.append(Switch((134, 422), '0-9', (255, 255, 255)))

        self.button_list.append(Switch((953, 422), "-=[]\;',./", (255, 255, 255)))

    def set_symbols2_keys(self):
        self.button_list.clear()

        self.button_list.append(Back((134, 172), (255, 255, 255)))

        for i in range(len(self.symbols2_keys[0])):
            self.button_list.append(NormalButton((125 * i + 328, 172), self.symbols2_keys[0][i], (255, 255, 255)))

        self.button_list.append(Delete((953, 172), (255, 255, 255)))

        self.button_list.append(Shift((134, 297), (255, 255, 255)))
        
        for i in range(len(self.symbols2_keys[1])):
            self.button_list.append(NormalButton((125 * i + 328, 297), self.symbols2_keys[1][i], (255, 255, 255)))

        self.button_list.append(Enter((953, 297), (255, 255, 255)))

        self.button_list.append(SpaceBar((328, 422), (255, 255, 255)))

        self.button_list.append(Switch((134, 422), '!@#$%^&*()', (255, 255, 255)))

        self.button_list.append(Switch((953, 422), '_+{}|:"<>?', (255, 255, 255)))
    
    def set_symbols3_keys(self):
        self.button_list.clear()

        self.button_list.append(Back((134, 172), (255, 255, 255)))

        for i in range(len(self.symbols3_keys[0])):
            self.button_list.append(NormalButton((125 * i + 328, 172), self.symbols3_keys[0][i], (255, 255, 255)))

        self.button_list.append(Delete((953, 172), (255, 255, 255)))

        self.button_list.append(Shift((134, 297), (255, 255, 255)))
        
        for i in range(len(self.symbols3_keys[1])):
            self.button_list.append(NormalButton((125 * i + 328, 297), self.symbols3_keys[1][i], (255, 255, 255)))

        self.button_list.append(Enter((953, 297), (255, 255, 255)))

        self.button_list.append(SpaceBar((328, 422), (255, 255, 255)))

        self.button_list.append(Switch((134, 422), "-=[]\;',./", (255, 255, 255)))

        self.button_list.append(Switch((953, 422), "abcdefghij", (255, 255, 255)))

    def set_symbols3_keys_caps(self):
        self.button_list.clear()

        self.button_list.append(Back((134, 172), (255, 255, 255)))

        for i in range(len(self.symbols3_keys[0])):
            self.button_list.append(NormalButton((125 * i + 328, 172), self.symbols3_keys[0][i], (255, 255, 255)))

        self.button_list.append(Delete((953, 172), (255, 255, 255)))

        self.button_list.append(Shift((134, 297), (255, 255, 255)))
        
        for i in range(len(self.symbols3_keys[1])):
            self.button_list.append(NormalButton((125 * i + 328, 297), self.symbols3_keys[1][i], (255, 255, 255)))

        self.button_list.append(Enter((953, 297), (255, 255, 255)))

        self.button_list.append(SpaceBar((328, 422), (255, 255, 255)))

        self.button_list.append(Switch((134, 422), "-=[]\;',./", (255, 255, 255)))

        self.button_list.append(Switch((953, 422), "ABCDEFGHIJ", (255, 255, 255)))

    def set_keyboard_page(self, mode):
        self.keyboard_page = mode

    def draw(self, img):
        cv2.rectangle(img, (134, 172), (1147, 547), (0, 0, 0), cv2.FILLED)

        for button in self.button_list:
            button.draw(img)

        height, width, _ = img.shape
        cv2.circle(img, (int(width/2), int(height/2)), 1, (0, 255, 255), 5)
        cv2.circle(img, (int(width/2), int(height/2)), 5, (0, 0, 0), 2)
        cv2.rectangle(img, (25, 25), (1255, 125), (255, 255, 255), cv2.FILLED)
        cv2.putText(img, self.test_letters[self.index], (615, 100), cv2.FONT_HERSHEY_COMPLEX_SMALL, 4, (0, 0, 0), 4)

        return img

    def adjust_cursor(self, x, y):
        for button in self.button_list:
            if button.is_hovered_over(x, y):
                return button.mid_point()

        return (x, y)

    def on_mouse(self, event, x, y, flags, param):
        '''
        Mouse callback function
        '''
        global x1, y1
        if event == cv2.EVENT_MOUSEMOVE:
            x1, y1 = x, y

            for button in self.button_list:
                if button.is_hovered_over(x1, y1):
                    button.color = (174, 174, 174)

                    if button.text == '...' and (self.keyboard_page == Keyboard_Page.DEFAULT or self.keyboard_page == Keyboard_Page.DEFAULT_CAPS):
                        button.progress.percentage = 0
                    else:
                        if button.progress.percentage == 0:
                            button.progress.start = time()

                        button.progress.percentage += 4

                    if button.progress.percentage >= 100:
                        print(time() - button.progress.start)
                        if button.text == 'Shift':
                            if self.keyboard_page == Keyboard_Page.DEFAULT:
                                self.set_keyboard_page(Keyboard_Page.DEFAULT_CAPS)
                                self.set_default_caps_keys()

                            elif self.keyboard_page == Keyboard_Page.A_TO_J:
                                self.set_keyboard_page(Keyboard_Page.A_TO_J_CAPS)
                                self.set_a_to_j_caps_keys()
                                
                            elif self.keyboard_page == Keyboard_Page.K_TO_T:
                                self.set_keyboard_page(Keyboard_Page.K_TO_T_CAPS)
                                self.set_k_to_t_caps_keys()

                            elif self.keyboard_page == Keyboard_Page.U_TO_Z:
                                self.set_keyboard_page(Keyboard_Page.U_TO_Z_CAPS)
                                self.set_u_to_z_caps_keys()

                            elif self.keyboard_page == Keyboard_Page.DEFAULT_CAPS:
                                self.set_keyboard_page(Keyboard_Page.DEFAULT)
                                self.set_default_keys()

                            elif self.keyboard_page == Keyboard_Page.A_TO_J_CAPS:
                                self.set_keyboard_page(Keyboard_Page.A_TO_J)
                                self.set_a_to_j_keys()
                                
                            elif self.keyboard_page == Keyboard_Page.K_TO_T_CAPS:
                                self.set_keyboard_page(Keyboard_Page.K_TO_T)
                                self.set_k_to_t_keys()

                            elif self.keyboard_page == Keyboard_Page.U_TO_Z_CAPS:
                                self.set_keyboard_page(Keyboard_Page.U_TO_Z)
                                self.set_u_to_z_keys()

                            elif self.keyboard_page == Keyboard_Page.NUMS:
                                self.set_keyboard_page(Keyboard_Page.NUMS_CAPS)
                                self.set_number_keys_caps()

                            elif self.keyboard_page == Keyboard_Page.SYMBOLS_1:
                                self.set_keyboard_page(Keyboard_Page.SYMBOLS_1_CAPS)

                            elif self.keyboard_page == Keyboard_Page.SYMBOLS_2:
                                self.set_keyboard_page(Keyboard_Page.SYMBOLS_2_CAPS)

                            elif self.keyboard_page == Keyboard_Page.SYMBOLS_3:
                                self.set_keyboard_page(Keyboard_Page.SYMBOLS_3_CAPS)
                                self.set_symbols3_keys_caps()

                            elif self.keyboard_page == Keyboard_Page().NUMS_CAPS:
                                self.set_keyboard_page(Keyboard_Page.NUMS)
                                self.set_number_keys()
                            
                            elif self.keyboard_page == Keyboard_Page.SYMBOLS_1_CAPS:
                                self.set_keyboard_page(Keyboard_Page.SYMBOLS_1)

                            elif self.keyboard_page == Keyboard_Page.SYMBOLS_2_CAPS:
                                self.set_keyboard_page(Keyboard_Page.SYMBOLS_2)

                            elif self.keyboard_page == Keyboard_Page.SYMBOLS_3_CAPS:
                                self.set_keyboard_page(Keyboard_Page.SYMBOLS_3)
                                self.set_symbols3_keys()

                        elif button.text == "abcdefghij":
                            self.set_keyboard_page(Keyboard_Page.A_TO_J)
                            self.set_a_to_j_keys()

                        elif button.text == "ABCDEFGHIJ":
                            self.set_keyboard_page(Keyboard_Page.A_TO_J_CAPS)
                            self.set_a_to_j_caps_keys()

                        elif button.text == "klmnopqrst":
                            self.set_keyboard_page(Keyboard_Page.K_TO_T)
                            self.set_k_to_t_keys()

                        elif button.text == "KLMNOPQRST":
                            self.set_keyboard_page(Keyboard_Page.K_TO_T_CAPS)
                            self.set_k_to_t_caps_keys()

                        elif button.text == "uvwxyz":
                            self.set_keyboard_page(Keyboard_Page.U_TO_Z)
                            self.set_u_to_z_keys()

                        elif button.text == "UVWXYZ":
                            self.set_keyboard_page(Keyboard_Page.U_TO_Z_CAPS)
                            self.set_u_to_z_caps_keys()

                        elif button.text == "0-9":
                            if self.keyboard_page == Keyboard_Page.DEFAULT or self.keyboard_page == Keyboard_Page.U_TO_Z or self.keyboard_page == Keyboard_Page.SYMBOLS_1:
                                self.set_keyboard_page(Keyboard_Page.NUMS)
                                self.set_number_keys()
                            elif self.keyboard_page == Keyboard_Page.DEFAULT_CAPS or self.keyboard_page == Keyboard_Page.U_TO_Z_CAPS or self.keyboard_page == Keyboard_Page.SYMBOLS_1_CAPS:
                                self.set_keyboard_page(Keyboard_Page.NUMS_CAPS)
                                self.set_number_keys_caps()

                        elif button.text == "!@#$%^&*()":
                            if self.keyboard_page == Keyboard_Page.DEFAULT or self.keyboard_page == Keyboard_Page.NUMS or self.keyboard_page == Keyboard_Page.SYMBOLS_2:
                                self.set_keyboard_page(Keyboard_Page.SYMBOLS_1)
                            elif self.keyboard_page == Keyboard_Page.DEFAULT_CAPS or self.keyboard_page == Keyboard_Page.NUMS_CAPS or self.keyboard_page == Keyboard_Page.SYMBOLS_2_CAPS:
                                self.set_keyboard_page(Keyboard_Page.SYMBOLS_1_CAPS)
                            self.set_symbols1_keys()

                        elif button.text == '-=[]\\;\',./':
                            if self.keyboard_page == Keyboard_Page.DEFAULT or self.keyboard_page == Keyboard_Page.SYMBOLS_1 or self.keyboard_page == Keyboard_Page.SYMBOLS_3:
                                self.set_keyboard_page(Keyboard_Page.SYMBOLS_2)
                            elif self.keyboard_page == Keyboard_Page.DEFAULT_CAPS or self.keyboard_page == Keyboard_Page.SYMBOLS_1_CAPS or self.keyboard_page == Keyboard_Page.SYMBOLS_3_CAPS:
                                self.set_keyboard_page(Keyboard_Page.SYMBOLS_2_CAPS)
                            self.set_symbols2_keys()

                        elif button.text == "_+{}|:\"<>?":
                            if self.keyboard_page == Keyboard_Page.DEFAULT or self.keyboard_page == Keyboard_Page.SYMBOLS_2 or self.keyboard_page == Keyboard_Page.A_TO_J:
                                self.set_keyboard_page(Keyboard_Page.SYMBOLS_3)
                                self.set_symbols3_keys()
                            elif self.keyboard_page == Keyboard_Page.DEFAULT_CAPS or self.keyboard_page == Keyboard_Page.SYMBOLS_2_CAPS or self.keyboard_page == Keyboard_Page.A_TO_J_CAPS:
                                self.set_keyboard_page(Keyboard_Page.SYMBOLS_3_CAPS)
                                self.set_symbols3_keys_caps()

                        elif button.text == "...":
                            if self.keyboard_page == Keyboard_Page.A_TO_J or self.keyboard_page == Keyboard_Page.K_TO_T or self.keyboard_page == Keyboard_Page.U_TO_Z\
                                or self.keyboard_page == Keyboard_Page.SYMBOLS_1 or self.keyboard_page == Keyboard_Page.SYMBOLS_2 or self.keyboard_page == Keyboard_Page.SYMBOLS_3\
                                or self.keyboard_page == Keyboard_Page.NUMS:
                                self.set_keyboard_page(Keyboard_Page.DEFAULT)
                                self.set_default_keys()

                            elif self.keyboard_page == Keyboard_Page.A_TO_J_CAPS or self.keyboard_page == Keyboard_Page.K_TO_T_CAPS or self.keyboard_page == Keyboard_Page.U_TO_Z_CAPS\
                                or self.keyboard_page == Keyboard_Page.SYMBOLS_1_CAPS or self.keyboard_page == Keyboard_Page.SYMBOLS_2_CAPS or self.keyboard_page == Keyboard_Page.SYMBOLS_3_CAPS\
                                or self.keyboard_page == Keyboard_Page.NUMS_CAPS:
                                self.set_keyboard_page(Keyboard_Page.DEFAULT_CAPS)
                                self.set_default_caps_keys()
                            
                        # elif button.text == 'Delete':
                        #     self.transcribed_text = self.transcribed_text[:-1]

                        # elif button.text == 'Space':
                        #     self.transcribed_text += ' '

                        elif button.text == 'Enter':
                            self.test_letters = ['0', '4', '5', '9', '%', '$', '#', '@', '!', '^', ')', '\\', '-', '/', ':', '-', '=', '[', ']', '\\']
                            self.start_time = time()
                            
                        else:
                            time_taken = time() - self.start_time
                            self.inputs.append(button.text)
                            self.all_times.append(time_taken)
                            if self.index + 1 < len(self.test_letters):
                                self.index += 1
                                self.start_time = time()
                            else:
                                data = {
                                    'test_letters': self.test_letters,
                                    'inputs': self.inputs,
                                    'all_times': self.all_times
                                }
                                df = pd.DataFrame(data)
                                # TODO: rename file
                                df.to_csv('jh_ltnk.csv', index=False)
                                self.test_letters = ['Test Completed']
                                self.index = 0
                                
                        button.progress.percentage = 0

                else :
                    button.progress.percentage = 0

                    if button.text == 'Shift' and (self.keyboard_page == Keyboard_Page.DEFAULT_CAPS or self.keyboard_page == Keyboard_Page.A_TO_J_CAPS\
                        or self.keyboard_page == Keyboard_Page.K_TO_T_CAPS or self.keyboard_page == Keyboard_Page.U_TO_Z_CAPS or self.keyboard_page == Keyboard_Page.SYMBOLS_1_CAPS\
                        or self.keyboard_page == Keyboard_Page.SYMBOLS_2_CAPS or self.keyboard_page == Keyboard_Page.SYMBOLS_3_CAPS or self.keyboard_page == Keyboard_Page.NUMS_CAPS):
                        button.color = (174, 174, 174)
                    
                    elif button.text == '...' and (self.keyboard_page == Keyboard_Page.DEFAULT or self.keyboard_page == Keyboard_Page.DEFAULT_CAPS):
                        button.color = (174, 174, 174)
                        
                    else:
                        button.color = (255, 255, 255)
                        # if self.keyboard_page == Keyboard_Page.DEFAULT or self.keyboard_page == Keyboard_Page.DEFAULT_CAPS:
                        #     button.color = (255, 255, 255)
                        # else:
                        #     button.color = (255, 255, 255)
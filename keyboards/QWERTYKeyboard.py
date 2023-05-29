import cv2
from enum import Enum
from time import time
import json
import csv
import pandas as pd

class ProgressBar():
    """
    Progress bar class
    """
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
        self.progress = ProgressBar((pos[0]+20, pos[1]+50))
    
    def draw(self, img, textOffset):
        # draw the button
        x, y = self.pos
        w, h = self.size
        cv2.rectangle(img, self.pos, (x+w, y+h), self.color, cv2.FILLED)
        cv2.putText(img, self.text, (x+textOffset[0], y+textOffset[1]), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, self.text_color, 1, cv2.LINE_AA)
        cv2.line(img, self.pos, (x, y+h), (0, 0, 0), 2)
        cv2.line(img, self.pos, (x+w, y), (0, 0, 0), 2)
        cv2.line(img, (x+w, y), (x+w, y+h), (0, 0, 0), 2)
        cv2.line(img, (x, y+h), (x+w, y+h), (0, 0, 0), 2)

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
    def __init__(self, pos, text, color, size=[75, 75]):
        super().__init__(pos, text, color, size)
    
    def draw(self, img, textOffset=[28, 35]):
        super().draw(img, textOffset)

class SpaceBar(Button):
    '''
    A space bar button
    '''
    def __init__(self, pos, color, text="Space", size=[375, 75]):
        self.pos = pos
        self.text = text
        self.size = size
        self.clicked = False
        self.color = color
        self.text_color = (0, 0, 0)
        self.progress = ProgressBar((pos[0]+130, pos[1]+50))
    
    def draw(self, img, textOffset=[100, 35]):
        super().draw(img, textOffset)

class Backspace(Button):
    '''
    A backspace button
    '''
    def __init__(self, pos, color, text="Delete", size=[113, 75]):
        self.pos = pos
        self.text = text
        self.size = size
        self.clicked = False
        self.color = color
        self.text_color = (0, 0, 0)
        self.progress = ProgressBar((pos[0]+35, pos[1]+50))
    
    def draw(self, img, textOffset=[10, 30]):
        super().draw(img, textOffset)

class Enter(Button):
    '''
    An enter button
    '''
    def __init__(self, pos, color, text="Enter", size=[113, 75]):
        self.pos = pos
        self.text = text
        self.size = size
        self.clicked = False
        self.color = color
        self.text_color = (0, 0, 0)
        self.progress = ProgressBar((pos[0]+35, pos[1]+50))
    
    def draw(self, img, textOffset=[10, 30]):
        super().draw(img, textOffset)

class Shift(Button):
    '''
    A shift button
    '''
    def __init__(self, pos, color, text="Shift", size=[150, 75]):
        self.pos = pos
        self.text = text
        self.size = size
        self.clicked = False
        self.color = color
        self.text_color = (0, 0, 0)
        self.progress = ProgressBar((pos[0]+74, pos[1]+50))
    
    def draw(self, img, textOffset=[50, 30]):
        super().draw(img, textOffset)


class Key_Mode(Enum):
    DEFAULT = 0
    SHIFTED = 1

class QWERTYKeyboard:
    def __init__(self):

        self.key_mode = Key_Mode.DEFAULT

        self.default_keys = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='],
                    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'], 
                    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\''], 
                    ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/']]

        self.shifted_keys = [['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+'],
                            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', '|'],
                            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':', '"'],
                            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?']]

        self.button_list = []

        self.test_letters = ['']
        self.inputs = []
        self.index = 0
        self.start_time = None
        self.all_times = []

        self.set_default_keys()

    def set_default_keys(self):
        self.button_list.clear()

        for i in range(len(self.default_keys[0])):
            self.button_list.append(NormalButton((75 * i + 134, 172), self.default_keys[0][i], (255, 255, 255)))
        
        for i in range(len(self.default_keys[1])):
            self.button_list.append(NormalButton((75 * i + 171, 247), self.default_keys[1][i], (255, 255, 255)))

        for i in range(len(self.default_keys[2])):
            self.button_list.append(NormalButton((75 * i + 209, 322), self.default_keys[2][i], (255, 255, 255)))

        for i in range(len(self.default_keys[3])):
            self.button_list.append(NormalButton((75 * i + 246, 397), self.default_keys[3][i], (255, 255, 255)))

        self.button_list.append(SpaceBar((396, 472), (255, 255, 255)))

        self.button_list.append(Backspace((1034, 172), (255, 255, 255)))

        self.button_list.append(Enter((1034, 322), (255, 255, 255)))

        self.button_list.append(Shift((996, 397), (255, 255, 255)))

    def set_shifted_keys(self):
        self.button_list.clear()

        for i in range(len(self.default_keys[0])):
            self.button_list.append(NormalButton((75 * i + 134, 172), self.shifted_keys[0][i], (255, 255, 255)))
        
        for i in range(len(self.shifted_keys[1])):
            self.button_list.append(NormalButton((75 * i + 171, 247), self.shifted_keys[1][i], (255, 255, 255)))

        for i in range(len(self.shifted_keys[2])):
            self.button_list.append(NormalButton((75 * i + 209, 322), self.shifted_keys[2][i], (255, 255, 255)))

        for i in range(len(self.shifted_keys[3])):
            self.button_list.append(NormalButton((75 * i + 246, 397), self.shifted_keys[3][i], (255, 255, 255)))

        self.button_list.append(SpaceBar((396, 472), (255, 255, 255)))

        self.button_list.append(Backspace((1034, 172), (255, 255, 255)))

        self.button_list.append(Enter((1034, 322), (255, 255, 255)))

        self.button_list.append(Shift((996, 397), (255, 255, 255)))

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

    def set_key_mode(self, mode):
        self.key_mode = mode

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
            hover = False

            for button in self.button_list:
                if button.is_hovered_over(x1, y1):
                    button.color = (174, 174, 174)

                    if button.progress.percentage == 0:
                        button.progress.start = time()

                    button.progress.percentage += 19
                    if button.progress.percentage >= 100:
                        print(time() - button.progress.start)

                        # if shift button is clicked, set shifted keys
                        if button.text == 'Shift':
                            self.set_shifted_keys()
                            self.set_key_mode(Key_Mode.SHIFTED)
                        
                        # if shift is on and a button is clicked, turn it off
                        elif self.key_mode == Key_Mode.SHIFTED:
                            self.input_stream += button.text
                            self.transcribe_text += button.text
                            self.set_default_keys()
                            self.set_key_mode(Key_Mode.DEFAULT)
                        
                        # elif button.text == 'Delete':
                        #     self.transcribed_text = self.transcribed_text[:-1]
                        #     self.input_stream += "[Delete]"

                        # elif button.text == 'Space':
                        #     self.transcribed_text += ' '
                        #     self.input_stream += ' '

                        elif button.text == 'Enter':
                            self.test_letters = ['1', '7', 'z', 'm', 'e', 'r', '5', '6', 'y', 'u', 'q', 'l', 'd', '0', '4', '3', 'w', 's', 'a', 'z']
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
                                df.to_csv('jh_qwerty.csv', index=False)
                                self.test_letters = ['Test Completed']
                                self.index = 0

                        button.progress.percentage = 0
                else:
                    button.progress.percentage = 0

                    # ensure shift button is always highlighted when in shift mode
                    if button.text == 'Shift' and self.key_mode == Key_Mode.SHIFTED:
                        button.color = (174, 174, 174)

                    else:
                        button.color = (255, 255, 255)       
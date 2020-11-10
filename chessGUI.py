import tkinter as tk
import threading
import time
import re
import unidecode
import chess
import chess.svg
import cairosvg
import speech_recognition as sr
from PIL import Image, ImageTk


def recognize_move_from_mic(recognizer, microphone):
    ''' Transcribe speech from recorded from `microphone`.

    returns: {
        'error':   `None` if no error occured, otherwise a string containing an error message,
        'move': `None` if speech could not be transcribed, otherwise a string containing the move played
    }
    '''
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError('`recognizer` must be `Recognizer` instance')

    if not isinstance(microphone, sr.Microphone):
        raise TypeError('`microphone` must be `Microphone` instance')

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        'error': None,
        'move': None
    }

    print('Got an audio! Fetching google API.')
    try:
        response['move'] = recognizer.recognize_google(audio, language="pt-BR")
    except sr.RequestError:
        # API was unreachable or unresponsive
        response['error'] = 'API unavailable'
    except sr.UnknownValueError:
        # speech was unintelligible
        response['error'] = 'Unable to recognize speech'

    return response


size = 400

r = sr.Recognizer()
mic = sr.Microphone()
board = chess.Board()

last_move = None

root = tk.Tk()

root.geometry('400x400')

root.title("SpeeChess")

frame = tk.Canvas(root, width=size, height=size)


def generateBoardImage():
  global last_move
  while True:
    if last_move == None or board.move_stack[-1] != last_move:
      if len(board.move_stack) > 0:
        last_move = board.move_stack[-1]
      cairosvg.svg2png(bytestring=chess.svg.board(board), write_to='board.png')

      img = Image.open('board.png')
      pimg = ImageTk.PhotoImage(img)

      frame.pack()
      frame.create_image(0,0,anchor='nw',image=pimg)
      time.sleep(0.1)

def invalid_move(move):
    print('{} is a invalid move. Please try again'.format(move))

def switch_player(player):
    if player == 'White':
        player = 'Black'
    else:
        player = White

def clean_move_string(raw_str):
    replacements = {
        # Words to replace
        'um': '1',
        'dois': '2',
        'tres': '3',
        'quatro': '4',
        'cinco': '5',
        'seis': '6',
        'sete': '7',
        'oito': '8',
        'rei' : 'K',
        'rainha' : 'Q',
        'torre' : 'R',
        'cavalo' : 'N',
        'bispo' : 'B',
        'peão' : 'P',

        # Common mistakes
        'se': 'c',
        'de': 'd',

        # Words to remove
        'para': '',
        ' ': '',
        '-': '',

        'rock': 'O-O',
        'roquegrand': 'O-O-O',
    }

    clean_str = unidecode.unidecode(raw_str.lower())

    for old_str, new_str in replacements.items():
        clean_str = clean_str.replace(old_str, new_str)

    return clean_str


def play():
    print('Recording!')
    player = 'White'
    while(True):
        recognize_response = recognize_move_from_mic(r, mic)

        move = None
        if recognize_response['move']:
            move = recognize_response['move']
        else:
            print('{}. Try again please.'.format(recognize_response['error']))
            continue
        
        move = clean_move_string(move)
        print(move)

        if re.search('^([a-h])([1-8])([a-h])([1-8])$', move):
            move_notation = board.parse_uci
        else:
            move_notation = board.parse_san

        try:
            parsed_move = move_notation(move)
        except ValueError:
            print('{} is a invalid move. Please try again'.format(move))
            continue
        
        print('{} was played!'.format(board.san(parsed_move)))
        board.push(parsed_move)

        if board.is_stalemate():
            print('Stalemate!')
        elif board.is_insufficient_material():
            print('Insufficient Material')
        elif board.is_game_over():
            print('{} has won!'.format(player))
        
        switch_player(player)

x = threading.Thread(target=play)
y = threading.Thread(target=generateBoardImage)
x.start()
y.start()

root.mainloop()

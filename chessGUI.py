import tkinter as tk
import threading
import time
from PIL import Image, ImageTk
import chess
import chess.svg
import cairosvg
import speech_recognition as sr

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
        response['move'] = recognizer.recognize_google(audio)
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


def play():
  print('Recording!')
  while(True):
      recognize_response = recognize_move_from_mic(r, mic)

      move = None
      if recognize_response['move']:
          move = recognize_response['move']
      else:
          print('{}. Try again please.'.format(recognize_response['error']))
          continue    
        
      if move == "chess":
          chess.svg.board(size=350)
          print(board)
          continue

      if len(move) == 2:
          move = move.lower()
      elif len(move) == 3:
          move = '{}{}'.format(move[0].upper(), move[1:].lower())
      else:
          print('{} is a invalid move. Please try again'.format(move))
          continue

      try:
          parsed_move = board.parse_san(move)
      except ValueError:
          print('{} is a invalid move. Please try again'.format(move))
          continue
        
      print('{} was played!'.format(board.san(parsed_move)))
      board.push(parsed_move)
  

x = threading.Thread(target=play)
y = threading.Thread(target=generateBoardImage)
x.start()
y.start()

root.mainloop()
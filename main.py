import speech_recognition as sr
import chess

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


r = sr.Recognizer()
mic = sr.Microphone()
board = chess.Board()

print('Recording!')
while(True):
    recognize_response = recognize_move_from_mic(r, mic)

    move = None
    if recognize_response['move']:
        move = recognize_response['move']
    else:
        print('{}. Try again please.'.format(recognize_response['error']))
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
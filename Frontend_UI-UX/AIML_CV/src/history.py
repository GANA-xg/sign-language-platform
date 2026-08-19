history = []

def add_prediction(record):
    history.append(record)

def get_history():
    return history

def clear_history():
    history.clear()
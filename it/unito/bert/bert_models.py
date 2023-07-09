from transformers import pipeline

def get_model():
    return pipeline('fill-mask', model='bert-large-uncased')


if __name__ == '__main__':
    
    unmasker = pipeline('fill-mask', model='bert-large-uncased')
    unmasker("woodwind instrument is a part of [MASK].")
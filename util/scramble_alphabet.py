from random import shuffle


def shuffle_alphabet(alphabet):

    alphabet = list(alphabet)
    shuffle(alphabet)
    return ''.join(alphabet)


if __name__ == '__main__':
    alphabet = 'abcdefghijklmnpqrstuvABCDEFGHIJKLMNPQRSTUV123456789'
    print(shuffle_alphabet(alphabet))
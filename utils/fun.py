from secrets import randbelow

loss_messages = []
with open('utils/loss.txt', 'r') as file:
    loss_messages.extend(file.readlines())


def get_random_loss_message():
    return loss_messages[randbelow(len(loss_messages))]


if __name__ == '__main__':
    print(get_random_loss_message())

import web.message


def test_local_message():
    data = {'test': 1}

    message = web.message.LocalMessage()
    message.push(data)

    for msg in message.polling():
        assert msg == data
        break

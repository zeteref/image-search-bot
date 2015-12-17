import requests
import sys

def print_response(text):
    r = requests.post('http://localhost:8080/webhook', json={
                                                             "update_id": "1",
                                                             "message" : {
                                                                             "message_id" : "-1",
                                                                             "date": "",
                                                                             "text" : text,
                                                                             "from" : "test",
                                                                             "chat" : {"id":1}
                                                                         }
                                                            })


    print r.text

def main():
    print_response(' '.join(sys.argv[1:]))

if __name__ == '__main__':
    main()


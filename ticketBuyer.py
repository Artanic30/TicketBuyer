import requests
import re
import time
import threading


class Threading(threading.Thread):
    def __init__(self, threadID, blocks, seat_info):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.block_text = blocks
        self.seat_info = seat_info

    def run(self):
        for block in self.block_text:
            rows = block.strip().split('\n')
            ST = re.findall('[0-1]', rows[11])
            PT = re.findall('[0-1]', rows[12])
            RW = re.findall('[0-9]+', rows[6])
            if (RW[0] == '5' or RW[0] == '6' or RW[0] == '7') and ST[0] == '0' and PT[0] == '0':
                self.seat_info.append(re.findall('[0-9]+', rows[0])[0])


class TicketBuyer:
    def __init__(self, isTest):
        self.max_num = 0
        self.current_num = 0

        # manually assign cookie value
        self.template_headers = {
            'authority': 'seat.shcstheatre.com',
            'method': 'POST',
            'scheme': 'https',
            'accept': 'application / json, text / javascript, * / *; q = 0.01',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': '',
            'origin': 'https://seat.shcstheatre.com',
            'referer': 'https://seat.shcstheatre.com/SelectSeats.aspx',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like \\'
                          'Gecko) Chrome/83.0.4103.116 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        self.urls = [
            
        ]

        # eventID can be obtain by call ""
        if isTest:
            self.process(88431, 3)
        else:
            self.event_ids = [
                {
                    'event_id': 88438 + 3,
                    'max_num': 4
                },
                {
                    'event_id': 88438,
                    'max_num': 2
                },
                {
                    'event_id': 88438 + 7,
                    'max_num': 1
                },
                {
                    'event_id': 88454 + 3,
                    'max_num': 3
                }
            ]
            for event in self.event_ids:
                self.process(event['event_id'], event['max_num'])

    def process(self, event_id, max_tickit):
        if max_tickit >= 4:
            self.max_num = 4
        else:
            self.max_num = max_tickit

        self.current_num = 0
        seat_info = []

        self.get_seat_ids(event_id, seat_info)

        for seat in seat_info:
            #self.lock_seat(seat)
            if self.current_num >= self.max_num:
                break
        print("event id:", event_id)
        print('Ticket number: ' + str(self.current_num))

    # abandoned
    def get_event_list(self):
        local_headers = self.template_headers
        local_headers['content-length'] = '51'
        local_headers['path'] = '/SK_WebAPI.ashx?op=GetSelectSeats_EventList'
        data = {
            'token': '0b41ae08-19c4-4ac5-80d0-4e0bea6b238f',
            'id': '34585'
        }
        r = requests.post(self.urls[0],
                          headers=local_headers,
                          data=data)
        if r.status_code != 200:
            print('Request fail!\nTry reload your cookie value')

    def get_seat_ids(self, event_id, seat_info):
        time_start = time.time()
        local_headers = self.template_headers
        local_headers['content-length'] = '27'
        local_headers['path'] = '/SK_WebAPI.ashx?op=GetSeatsByID'
        data = {
            'event_id': str(event_id)
        }
        r = requests.post(self.urls[1],
                          headers=local_headers,
                          data=data)
        if r.status_code != 200:
            print('Request fail!\nTry reload your cookie value')
        response_text = r.text.split('"seat":{')[1]
        block_text = response_text.split('},\n')
        split_num = int(len(block_text) / 3)
        tem_result1 = []
        tem_result2 = []
        tem_result3 = []
        thread1 = Threading(1, block_text[0:split_num], tem_result1)
        thread2 = Threading(2, block_text[split_num:split_num*2], tem_result2)
        thread3 = Threading(3, block_text[split_num*2:-1], tem_result3)
        thread1.start()
        thread2.start()
        thread3.start()
        thread1.join()
        thread2.join()
        thread3.join()

        seat_info += tem_result3 + tem_result2 + tem_result1




        time_end = time.time()
        print('totally cost', time_end - time_start)

    def lock_seat(self, event_id):
            local_headers = self.template_headers
            local_headers['content-length'] = '27'
            local_headers['path'] = '/SK_WebAPI.ashx?op=LockSeatsInsertShoppingCart'
            data = {
                'iEventSeat_ids': str(event_id)
            }
            r = requests.post(self.urls[2],
                              headers=local_headers,
                              data=data)
            re_msg = r.text.strip().split('\n')[4]
            if "操作成功" in re_msg:
                self.current_num += 1
            else:
                print('Request fail!\nTry reload your cookie value')
                print(r.text)


if __name__ == "__main__":
    T = TicketBuyer(isTest=True)


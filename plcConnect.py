import socket
import binascii
import time

#10進数をバイナリーデータに変換させるクラス
class TransDigit10ToVariousDigit:
    def __init__ (self,decimal_number,digit_format):
        self.decimal_number = decimal_number
        plane_bit = "bit"
        ascii_code = 'ascii_code'
        digit16 = '16decimal_bit'
        d10b16  = '10decimal_16bit'
        d10b32  = '10decimal_32bit'
        zero5   = "00000"
        self.trans_data =""

         # 「00000」のasciiコードの場合は何もないことを示す。
        #     # 「0」ではなく何もない。None,null

        if self.decimal_number == zero5 and digit_format == ascii_code:
            self.trans_data = ""

        #アスキーコードに変換・洗浄
        elif digit_format == ascii_code:
            self.trans_data = self.bit10_to_ascii_via_bit16()

        #16進数に変換・洗浄
        elif digit_format == digit16:
            self.trans_data = self.digit10_to_binadigit16()

        #10進数に変換・洗浄
        elif digit_format == d10b16 \
            or digit_format == d10b32 \
            or digit_format == plane_bit:
            self.trans_data = str(int(self.decimal_number))


    #10進数から16進数に変換してstring型変換
    def digit10_to_digit16(self):
        bit16_str = str(hex(int(self.decimal_number)))
        #余計なデータを取り除く
        noise_datas = [' ','0x','\t','\r\n']
        to_nothing  = ""
        for noise_data in noise_datas:
            bit16_str = (bit16_str.replace(noise_data,to_nothing))
        return bit16_str


    #10進数から16進数に変換後、asciiコードに変換
    def bit10_to_ascii_via_bit16(self):
        try:
            clean_bit16_str = self.digit10_to_digit16()
            ascii_data = binascii.unhexlify(clean_bit16_str.encode())

            del_character = ['b',"'",r"\x00",r"\x000"]
            for del_chara in del_character:
                ascii_data = (str(ascii_data).replace(del_chara,''))
            return ascii_data
        except:
            return "0"


    #10進数から16進数に変換後、16新数のバイナリデータに変換
    def digit10_to_binadigit16(self):
        clean_bit16_str = self.digit10_to_digit16()

        if int(clean_bit16_str) < 100:
            clean_bit16_str = "00" + clean_bit16_str
        elif int(clean_bit16_str) < 1000:
            clean_bit16_str = "0" + clean_bit16_str
        return clean_bit16_str


# デバイス名の値をすべて取り出す。
class RecievePLCPlaneData(object) :
    def __init__(self,ip,port):
        self.ip = ip
        self.port = int(port)


    # 問い合わせのコマンドを送る。自動でPLCが返送する。
    def socket_send(self,command):
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((self.ip,self.port))
        s.send(command.encode('ascii'))
        recv_data = s.recv(1024).decode("ascii")
        return recv_data


    #値を取り出す
    def recv_from(self,device_list):
        try:
            device_list[1] = str(device_list[1])
            command = "RDS {}.S {}\r".format(device_list[0],device_list[1])
            recv_data = self.socket_send(command)
            return str(recv_data)
        except:
            return -1


    #ビットで取り出したいときデバイス名ＭＲなど
    def recv_as_bit_from(self,device_list):
        try:
            device_list[1] = str(device_list[1])
            command = "RDS {} {}\r".format(device_list[0],device_list[1])
            recv_data  = self.socket_send(command)
            return str(recv_data)
        except:
            return -1


    # 10進数32ビットで取り出したい場合
    def recv_as_10digit32bit_from(self,device_list):
        try:
            device_list[1] = str(device_list[1])
            command = "RDS {}.D {}\r".format(device_list[0],device_list[1])
            recv_data = self.socket_send(command)
            recv_data = recv_data.replace(" ","")
            recv_data = int(recv_data)
            return str(recv_data)

        except:
            return -1


    #フォーマットによりコマンド名が違うので場合分け
    def recv_10digi16bit_or_32bit(self,device_list):
        if   device_list[2] == '10decimal_32bit':
            recv_data = self.recv_as_10digit32bit_from(device_list)

        elif device_list[2] == 'bit':
            recv_data = self.recv_as_bit_from(device_list)

        else:
            recv_data = self.recv_from(device_list)

        return recv_data


# 取り出してきたデータを指定のフォーマットに変える
class ReceiveTruePLCValue(RecievePLCPlaneData):

    """
    引数はdevice_data_list = [["デバイス名",ワード数,"format"]]
    リストのリストの構造で受け付ける。
    formatは"bit",'ascii_code','16decimal_bit',
            '10decimal_16bit','10decimal_32bit'
    # 辞書{デバイス名:格納している値}を返す
    """,
    # 辞書型{デバイス名:格納している値}を返す
    def receive_plc_data(self,plc_list):
        if type(plc_list[0]) == list:
            device_data_lists = plc_list
            plc_datas = {device_data_list[0]:self.clean_recv_data(device_data_list)
                        for device_data_list in device_data_lists}
        else:
            device_data_lists = plc_list
            plc_datas = self.clean_recv_data(device_data_lists)

        return plc_datas


    #データを取得してバイナリーデータに変換
    def clean_recv_data(self,device_list):
        word_length = device_list[1]
        format_name = device_list[2]
        plan_bit    = "bit"
        ascii_code  = 'ascii_code'
        digit16     = '16decimal_bit'
        d10b16      = '10decimal_16bit'
        d10b32      = '10decimal_32bit'
        zero5       = "00000"

        # デバイス名とワード数
        recv_data = self.recv_10digi16bit_or_32bit(device_list)

        if recv_data != -1 :#返信が確認できる場合
            #データをリスト結合させる。
            # str型「+00001 +00000」形式で取得するので余計なものを除去してリスト化
            PLC_data_list = [recv_data[7*i:7*i+6].replace("+","")
                            for i in range(int(word_length))]
            changed_data_list = []
            for PLC_data in PLC_data_list:
                tr = TransDigit10ToVariousDigit(PLC_data,format_name)
                changed_data_list.append(tr.trans_data)
                value = "".join(changed_data_list)#リストを全て結合
            return value

        else:
            return -1


#PLCに値を送信するクラス
class SendMessageToPLC(object):
    def __init__ (self,facility_info_list):
        self.ip = facility_info_list[0]
        self.port = int(facility_info_list[1])

    #デバイス１つのみ対応
    def message_to(self,device_name,message):
        try:
            message = str(message)
            command_sentence = "WR {}.S {}\r".format(device_name,message)
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.connect((self.ip,self.port))
            s.send(command_sentence.encode('ascii'))
            recv_data = s.recv(1024).decode("ascii")
            return recv_data
        except:
            return -1



# フォーマットを指定して値をもらう。
# 以下の文字列で指定できる。右からビット、アスキー,16進数,10進数16ビット,10進数32ビット
# 'bit','ascii_code','16decimal_bit','10decimal_16bit','10decimal_32bit'
def recv_plc(ip, port, device_name, data_length,format_name):
    recv = ReceiveTruePLCValue(ip, port)
    recv_data = recv.receive_plc_data([device_name, data_length, format_name])
    return recv_data


# ビットで値をもらう
def recv_bit(ip, port, device_name, data_length):
    recv = ReceiveTruePLCValue(ip, port)
    recv_data = recv.receive_plc_data([device_name, data_length, 'bit'])
    return recv_data


# asciiで値をもらう
def recv_ascii(ip, port, device_name, data_length):
    recv = ReceiveTruePLCValue(ip, port)
    recv_data = recv.receive_plc_data([device_name, data_length, 'ascii_code'])
    return recv_data


# 16進数で値をもらう
def recv_16deci(ip, port, device_name, data_length):
    recv = ReceiveTruePLCValue(ip, port)
    recv_data = recv.receive_plc_data([device_name, data_length,
                                       '16decimal_bit'])
    return recv_data


# 10進数16ビットで値をもらう
def recv_10deci16bit(ip, port, device_name, data_length):
    recv = ReceiveTruePLCValue(ip, port)
    recv_data = recv.receive_plc_data([device_name, data_length,
                                       '10decimal_16bit'])
    return recv_data


# 10進数32ビットで値をもらう
def recv_10deci32bit(ip, port, device_name, data_length):
    recv = ReceiveTruePLCValue(ip, port)
    recv_data = recv.receive_plc_data([device_name, data_length,
                                       '10decimal_32bit'])
    return recv_data


# PLCに値を送る。フォーマットの指定はしなくてよい。
def send_to_plc(ip, port, device_name,message):
    smp = SendMessageToPLC([ip, port])
    smp.message_to(device_name, message)


if __name__ =='__main__':
    # テスト的に利用
    device_names = ["EM1320","EM1360","EM1380","EM1400","EM1420","EM1440"]
    ip = '10.50.100.11'
    port = 8501
    for device_name in device_names:
        time.sleep(0.1)
        ascii_data = recv_ascii(ip,port,device_name,1)
        deci16_data = recv_16deci(ip,port,device_name,2)
        print(ascii_data,deci16_data)

## 初始版本
import time
import threading
import can
from queue import Queue
import queue
import random
import serial.tools.list_ports

Bus = None
recv_queue = Queue()
send_queue = Queue()
global_msg = []
DEBUG = False



def convert_to_hex_string_list(int_list):
    hex_string_list = [f"0x{num:02X}" for num in int_list]
    return hex_string_list

def sender(stop_event):
    """发送消息的线程函数"""
    print("sender start!")
    while not stop_event.is_set():
        msg = send_queue.get()  # 从发送队列中获取消息
        if msg:
            Bus.send(msg)  # 发送消息
            data = " ".join(f"{byte:02X}" for byte in list(msg.data))
            print(f"发送消息 -> ID: {hex(msg.arbitration_id)} Data: {data}")
            ## 存储消息
            record = {
                'type': 'send',
                'msg':msg,
                'time': time.time()
            }
            global_msg.append(record)
        send_queue.task_done()

def receiver(stop_event,filter):
    print("receiver start!")
    """接收消息的线程函数"""
    while not stop_event.is_set():
        msg = Bus.recv(0)
        if msg:
            if msg.arbitration_id not in filter:
                recv_queue.put(msg)  # 将接收到的消息放入接收队列
                ## 存储消息
                record = {
                    'type': 'receive',
                    'msg': msg,
                    'time': time.time()
                }
                global_msg.append(record)

def print_received_messages(stop_event):
    """从接收队列中打印消息的函数"""
    print("start print received messages!")
    while not stop_event.is_set() or not recv_queue.empty():
        try:
            msg = recv_queue.get(timeout=5)
            if msg:
                t = 'CANFD' if msg.is_fd else 'CAN'
                b = 'BRS' if msg.bitrate_switch else ''
                data = " ".join(f"{byte:02X}" for byte in list(msg.data))
                print(f"接收: {msg.timestamp} TYPE: {t} {b} ID: {hex(msg.arbitration_id)} DLC: {msg.dlc} Data: {data}")
                recv_queue.task_done()
        except queue.Empty:
            continue

def print_message(msg):
    if msg:
        t = 'CANFD' if msg.is_fd else 'CAN'
        b = 'BRS' if msg.bitrate_switch else ''
        data = " ".join(f"{byte:02X}" for byte in list(msg.data))
        print(f"接收: {msg.timestamp} TYPE: {t} {b} ID: {hex(msg.arbitration_id)} DLC: {msg.dlc} Data: {data}")



def build_message(id, dlc, data, fd=False, extended=False, remote=False, brs=False):
    """
    构造一个CAN或CAN FD消息。

    :param id: 消息ID。
    :param dlc: 数据长度代码（DLC）。
    :param data: 消息数据，一个字节列表。
    :param fd: 是否为CAN FD消息。
    :param extended: 是否使用扩展ID。
    :param remote: 是否为远程帧。
    :param brs: 是否启用比特率切换（仅CAN FD）。
    :return: 一个can.Message对象。
    """
        # 验证数据长度
    if fd:
        # CAN FD允许的最大DLC为15，对应64字节数据
        max_dlc = 15
    else:
        # 标准CAN的最大DLC为8
        max_dlc = 8

    if dlc > max_dlc:
        raise ValueError(f"DLC超出允许的范围：{dlc} > {max_dlc}")
    # 构造消息 还有一些需要设置的 TODO
    message = can.Message(
        arbitration_id=id,
        is_extended_id=extended,
        is_remote_frame=remote,
        is_fd=fd,
        bitrate_switch=brs,
        dlc=dlc,
        data=data
    )
    return message

def set_port():
    # 选择接口
    ports = serial.tools.list_ports.comports()
    print("设置接口：")
    ports_list = {}
    i = 1
    for port, desc, hwid in sorted(ports):
        print(f"\t{i}> {port}: {desc} [{hwid}]")
        ports_list[i] = port
        i += 1
    
    # 限制输入为整数
    while True:
        try:
            chpi = input("请输入bitrate(默认为COM3)：")
            if chpi == '':
                # 如果输入为空，检查是否存在COM3
                if "COM3" in ports_list.values():
                    x_port = "COM3"
                    break
                else:
                    # 如果ports_list没有COM3，但是列表不为空，则默认选取第一个端口
                    if ports_list:
                        x_port = ports_list[1]
                        print(f"未指定接口序号，使用默认端口：{x_port}")
                        break
                    else:
                        print("没有可用的接口。")
                        return
            chpi = int(chpi)  # 尝试将输入转换为整数
            # 校验输入是否有效
            if chpi in ports_list:
                x_port = ports_list[chpi]
                print(f"选定的接口为：{x_port}")
                break
            else:
                print("输入的序号无效，请重新输入。")
        except ValueError:
            print("请输入有效的整数序号。")
    
    # 返回选择的端口
    return x_port
    
def set_can():
    print("设置CAN参数：")
    CAN_BTR_LIST = {
                0:10000,
                1:20000,
                2:50000,
                3:100000,
                4:125000,
                5:250000,
                6:500000,
                7:750000,
                8:1000000,
                9:833000,
            }
    for k,v in CAN_BTR_LIST.items():
        print(f"\t{k}> {v}")
    bitrate = 0
    extended = False
    remote = False
    # 限制输入为整数
    while True:
        try:
            chpi = input("请输入CAN bitrate(默认为500000)：")
            if chpi == '':
                bitrate = 500000
                break
            chpi = int(chpi)  # 尝试将输入转换为整数
            # 校验输入是否有效
            if chpi in CAN_BTR_LIST:
                bitrate = CAN_BTR_LIST[chpi]
                print(f"选定的bitrate：{bitrate}")
                break
            else:
                print("输入的序号无效，请重新输入。")
        except ValueError:
            print("请输入有效的整数序号。")

    ## Extended
    while True:
        c = input("是否开启extended? Y/N(N):")
        if c=="":
            extended = False
            break
        elif c=="N" or c=='n':
            extended = False
            break
        elif c=="Y" or c=='y': 
            extended = True
            break
        else:
            print("输入错误，请重新输入。")
    ## remote TODO
    while True:
        c = input("remote? Y/N(N):")
        if c=="":
            remote = False
            break
        elif c=="N" or c=='n':
            remote = False
            break
        elif c=="Y" or c=='y': 
            remote = True
            break
        else:
            print("输入错误，请重新输入。")
    
    return bitrate,extended,remote
    
def set_canfd():
    print("设置CANFD参数：")
    CANFD_BTR_LIST = {
        1:1000000,
        2:2000000,
        4:4000000,
        5:5000000
    }
    for k,v in CANFD_BTR_LIST.items():
        print(f"\t{k}> {v}")
    bitrate = 0
    extended = False
    brs = False
    # 限制输入为整数
    while True:
        try:
            chpi = input("请输入CAN bitrate(默认为2000000)：")
            if chpi == '':
                bitrate = 2000000
                break
            chpi = int(chpi)  # 尝试将输入转换为整数
            # 校验输入是否有效
            if chpi in CANFD_BTR_LIST:
                bitrate = CANFD_BTR_LIST[chpi]
                print(f"选定的bitrate：{bitrate}")
                break
            else:
                print("输入的序号无效，请重新输入。")
        except ValueError:
            print("请输入有效的整数序号。")
    ## TODO extended
    while True:
        c = input("是否开启extended? Y/N(N):")
        if c=="":
            extended = False
            break
        elif c=="N" or c=='n':
            extended = False
            break
        elif c=="Y" or c=='y': 
            extended = True
            break
        else:
            print("输入错误，请重新输入。")
    ## TODO BRS
    while True:
        c = input("是否开启BRS? Y/N(N):")
        if c=="":
            brs = False
            break
        elif c=="N" or c=='n':
            brs = False
            break
        elif c=="Y" or c=='y': 
            brs = True
            break
        else:
            print("输入错误，请重新输入。")
    
    return bitrate,extended,brs

def setting():
    global Bus
    port = set_port()
    ## 二选一 选择CAN或者CANFD
    fd = False
    bitrate = 0
    extended = False
    brs = False
    remote = False

    while True:
        try:
            t = input("请选择CAN或者CANFD(默认CAN):\n\t1.CAN\n\t2.CANFD\n请输入序号：")
            if t == '':
                fd = False
                bitrate,extended,remote = set_can()
                break
            t_t = int(t)
            if t_t == 1:
                fd = False
                bitrate,extended,remote = set_can()
                break
            elif t_t == 2:
                fd = True
                bitrate,extended,brs = set_canfd()
                break
            else:
                print("输入的序号无效，请重新输入。")
        except ValueError:
            print("选择错误 请重新选择")

    ## TODO 设置模式 - 默认读写模式 可设置为只听模式  需要在库中配置一下
    ## TODO ttyBaudrate 默认 1000000 暂时无需修改
    baudrate = 1000000
    ## TODO rtscts
    rtscts = False
            
    print(f"设置 port={port},fd={fd},bitrate={bitrate},extended={extended},remote={remote},brs={brs}")
    if fd:
        ## 使用其他的设备的话 这里需要改掉
        Bus =  can.Bus(interface="canable2", channel=port, fd=True, fd_bitrate=bitrate, rtscts=rtscts)
    else:
        Bus =  can.Bus(interface="canable2", channel=port, fd=False, bitrate=bitrate, rtscts=rtscts)
    Bus.flush()
    return fd,extended,remote,brs

def set_frame_filter():
    ## 默认不过滤
    ids = []
    if DEBUG:
        ids = [0x159,0x153,0x155,0x157,0x121,0x669]
    while True:
        ids_i = input("请输入需要过滤接收的帧ID(16进制)(多个ID以,分割,eg:0x11,0x22):")
        if ids_i=="":
            break
        else:
            try:
                ids = [int(p,16) for p in ids_i.split(",")]
                break
            except ValueError:
                print("输入错误，请重新输入。")
    print(f"过滤的帧ID LIST = {ids}")
    return ids

# def send_recv_msg(msg):
#     # 发送一条消息并且打印回复的一条消息
#     send_queue.put(msg)


                # record = {
                #     'type': 'receive',
                #     'msg': msg,
                #     'time': time.time()
                # }

def print_filter_msg(id,time_s=None,type="receive"):
    # 按照 type  、 id 、 time 过滤。一般按id过滤即可  默认也只打印receive的消息
    ## 这里的time值是 几秒内的时间
    # 从global_msg中打印过滤的消息
    current_time = time.time()  # 获取当前时间
    msg_list = []
    for m in global_msg:
        if m.get("msg").arbitration_id == id and (m['type'] == type):
            # 设置time过滤
            if time is not None:
                message_time = m['time']
                # 如果消息在指定时间范围内，则添加到列表
                if current_time - message_time <= time_s:
                    msg_list.append(m)
            else:
                # 如果没有指定时间，则不进行时间过滤
                msg_list.append(m)
    
    ## 排序打印
    sorted_records = sorted(msg_list, key=lambda x: x['time'])
    for mm in sorted_records:
        print_message(mm.get('msg'))
    return sorted_records

def uds_seeds_test(uds_addr,uds_addr_rep,fd,extended,remote,brs):
    # uds_addr = input('请输入uds,进行UDS seeds安全性测试')
    msg1 = build_message(id=uds_addr,data=[0x02,0x10,0x01,0x00,0x00,0x00,0x00,0x00],dlc=8,fd=fd,extended=extended,remote=remote,brs=brs)
    msg2 = build_message(id=uds_addr,data=[0x02,0x10,0x03,0x00,0x00,0x00,0x00,0x00],dlc=8,fd=fd,extended=extended,remote=remote,brs=brs)
    msg_req_seed = build_message(id=uds_addr,data=[0x02,0x27,0x01,0x00,0x00,0x00,0x00,0x00],dlc=8,fd=fd,extended=extended,remote=remote,brs=brs)
    ## 循环发送5次请求seed的
    send_queue.put(msg1)
    time.sleep(1)
    for i in range(5):
        send_queue.put(msg2)
        time.sleep(1)
        send_queue.put(msg_req_seed)
        time.sleep(1)
    ## 打印10s内所有的消息
    time.sleep(2)
    msgs = print_filter_msg(uds_addr_rep,time_s=10)
    ## TODO msgs 用于 自动判断结果
    print("seed值是否相同或者可预测？")
    ## TODO 发送seed测试 先msg2 在msg_req_seed 再将获取的到的seed 使用06 27 02 [seed] 发送

## 简化版本
def did_read_test(uds_addr, uds_addr_rep, fd, extended, remote, brs):
    # 随机选择DID
    for did in range(0x100, 0xFFF):

    # did = random.randint(0x100, 0xFFF)
        # 构造DID读取消息
        read_did_msg = build_message(id=uds_addr, data=[0x02, 0x22, did >> 8, did & 0xFF], dlc=8, fd=fd, extended=extended, remote=remote, brs=brs)
        send_queue.put(read_did_msg)
        print(f"Sent DID read request for: 0x{did:X}")
        time.sleep(2)  # 等待响应

## 简化版本
def did_write_test(uds_addr, uds_addr_rep, fd, extended, remote, brs):
    # 随机选择DID
    # did = random.randint(0x100, 0xFFF)
    # 随机生成要写入的值，这里简化为单字节值
    for did in range(0x100, 0xFFF):
        value = random.randint(0x00, 0xFF)
        # 构造DID写入消息
        write_did_msg = build_message(id=uds_addr, data=[0x03, 0x2E, did >> 8, did & 0xFF, value], dlc=8, fd=fd, extended=extended, remote=remote, brs=brs)
        send_queue.put(write_did_msg)
        print(f"Sent DID write request for: 0x{did:X} with value 0x{value:X}")
        time.sleep(2)  # 等待响应

def can_ddos_test(uds_addr,uds_addr_rep,fd,extended,remote,brs):
    # 构造大量消息
    for i in range(10000):  # 10000
        # 随机生成消息内容
        data = [0x02, 0x10, 0x03] + [0x00] * 5  # 示例数据
        msg = build_message(id=uds_addr, data=data, dlc=8, fd=fd, extended=extended, remote=remote, brs=brs)
        send_queue.put(msg)
        if i % 100 == 0:
            print(f"Sending message {i}")
            time.sleep(0.5)  # 避免过快发送
    print("DDoS test messages sent.")

## 简化版本
def can_fuzz_test(uds_addr,uds_addr_rep,fd,extended,remote,brs):
    # 发送随机数据消息
    for i in range(5000):  # 假定发送5000条随机消息
        # 生成随机数据内容
        data = [random.randint(0, 0xFF) for _ in range(8)]
        msg = build_message(id=uds_addr, data=data, dlc=8, fd=fd, extended=extended, remote=remote, brs=brs)
        send_queue.put(msg)
        if i % 50 == 0:
            print(f"Sending fuzz message {i}")
            time.sleep(0.1)  # 避免过快发送
    print("Fuzz test messages sent.")

def test_uds_address(msg,rid):
    send_queue.put(msg)
    start_time = time.time()
    while True:
        current_time = time.time()
        ## 10s后还是接收到没有说明不是
        if current_time - start_time >= 10:
            break
        try:
            r_msg = recv_queue.get(timeout=1)
            if r_msg:
                print_message(r_msg)
                if r_msg.arbitration_id == rid:
                    return True
                time.sleep(0.1)
        except queue.Empty:
            continue
    return False

def get_usd_address(fd,extended,remote,brs):
    ## 爆破诊断地址 0x700 - 0x7FF
    for id in range(0x700,0x800):
        msg = build_message(id=id,data=[0x02,0x10,0x01,0x00,0x00,0x00,0x00,0x00],dlc=8,fd=fd,extended=extended,remote=remote,brs=brs)
        send_queue.put(msg)

    start_time = time.time()
    while True:
        current_time = time.time()
        ## 20s吧
        if current_time - start_time >= 20:
            break
        r_msg = recv_queue.get(timeout=10)
        if r_msg:
            t_id = r_msg.arbitration_id
            if t_id in range(0x700,0x800):
                print_message(r_msg)
                rdata = list(r_msg.data)
                if rdata[0] == 0x06 and rdata[1] == 0x50 and rdata[2] == 0x01:
                    recv_queue.task_done() #停止
                    uds_rep_addr = t_id
                    ## TODO 确定一下 UDS地址 +0x20 还是0x40?bug 不规范的话不好判断
                    t1_uds_a = uds_rep_addr - 0x40 #标准值
                    t1_uds_b = uds_rep_addr - 0x80
                    msg1 = build_message(id=t1_uds_a,data=[0x02,0x10,0x01,0x00,0x00,0x00,0x00,0x00],dlc=8,fd=fd,extended=extended,remote=remote,brs=brs)
                    msg2 = build_message(id=t1_uds_b,data=[0x02,0x10,0x01,0x00,0x00,0x00,0x00,0x00],dlc=8,fd=fd,extended=extended,remote=remote,brs=brs)
                    if test_uds_address(msg1,uds_rep_addr) : ##BUG 进行两次确认
                        return t1_uds_a,uds_rep_addr
                    elif test_uds_address(msg2,uds_rep_addr):
                        return t1_uds_b,uds_rep_addr
                    else:
                        print("不规范 无法确定，请向相关开发人员确定此地址")
                        return 0x0,uds_rep_addr

def test(fd,extended,remote,brs):
    uds_addr = 0x0
    uds_addr_rep = 0x0
    while True:
        ## 找开发要比较好 爆破有时候不准确
        a = input("是否需要爆破诊断地址(已知则无需测试) Y/N(N):")
        if a == "" or a == 'N' or a == 'n':
            ## 假设已知并且不会输入错误
            while True:
                try:
                    addr = input("请输入诊断物理请求地址(16进制)：")
                    resp_addr = input("请输入诊断物理响应地址(16进制)：")
                    if addr != "" and resp_addr != "":
                        uds_addr = int(addr,16)
                        uds_addr_rep = int(resp_addr,16)
                        break
                    else:
                        pass
                except ValueError:
                    pass
            break
        elif a=="y" or a=="Y":
            uds_addr,uds_addr_rep = get_usd_address(fd,extended,remote,brs)
            break
        else:
            print("输入错误，请重新输入。")
    print(f"UDS 诊断地址为：{hex(uds_addr)} ->  ||  <- {hex(uds_addr_rep)}")
    ## seed测试
    while True:
        a = input("是否进行安全诊断seed测试 Y/N(N):")
        if a == "" or a == 'N' or a == 'n':
            ## 假设已知并且不会输入错误
            break
        elif a=="y" or a=="Y":
            uds_seeds_test(uds_addr,uds_addr_rep,fd,extended,remote,brs)
            time.sleep(1)
            print("Seed 安全测试完成")
            break
        else:
            print("输入错误，请重新输入。")

    ## DID 读测试  这里需要注意 27服务的解锁
    while True:
        a = input("是否进行DID读测试测试 Y/N(N):")
        if a == "" or a == 'N' or a == 'n':
            ## 假设已知并且不会输入错误
            break
        elif a=="y" or a=="Y":
            did_read_test(uds_addr,uds_addr_rep,fd,extended,remote,brs)
            break
        else:
            print("输入错误，请重新输入。")
    time.sleep(1)        
    ## DID 写测试  DID可以导入或者全部随机  需要注意 27服务的解锁
    while True:
        a = input("是否进行DID写测试 Y/N(N):")
        if a == "" or a == 'N' or a == 'n':
            ## 假设已知并且不会输入错误
            break
        elif a=="y" or a=="Y":
            did_write_test(uds_addr,uds_addr_rep,fd,extended,remote,brs)
            break
        else:
            print("输入错误，请重新输入。")
    time.sleep(1)
    ## CAN DDOS测试
    while True:
        a = input("是否进行CAN DDOS测试 Y/N(N):")
        if a == "" or a == 'N' or a == 'n':
            ## 假设已知并且不会输入错误
            break
        elif a=="y" or a=="Y":
            can_ddos_test(uds_addr,uds_addr_rep,fd,extended,remote,brs)
            break
        else:
            print("输入错误，请重新输入。")
    time.sleep(1)        
    ## CAN Fuzz测试  此项默认测试5小时
    while True:
        a = input("是否进行CAN Fuzz测试 Y/N(N):")
        if a == "" or a == 'N' or a == 'n':
            ## 假设已知并且不会输入错误
            break
        elif a=="y" or a=="Y":
            can_fuzz_test(uds_addr,uds_addr_rep,fd,extended,remote,brs)
            break
        else:
            print("输入错误，请重新输入。")
    time.sleep(1)

def main():
    global DEBUG
    DEBUG = True
    ## TODO 改为选项和配置文件二选一的模式比较方便
    fd,extended,remote,brs = setting()
    ## 输入需要过滤的帧ID
    filter_frame_id_list = set_frame_filter()
    ## 开启接收和打印线程
    stop_event = threading.Event()
    print_stop_event = threading.Event()

    t_recv = threading.Thread(target=receiver, args=(stop_event,filter_frame_id_list))
    t_send = threading.Thread(target=sender, args=(stop_event,))
    t_print = threading.Thread(target=print_received_messages, args=(print_stop_event,))

    t_recv.start()
    t_send.start()
    ## debug
    if DEBUG:
        t_print.start()

    ## 运行测试 需要停止掉print_received_messages线程 -> 改为直接不开
    while True:
        opt = input("\n是否需要进行CAN UDS Test? Y/N(N)")
        if opt == "" or opt == "N" or opt=='n':
            if not DEBUG:
                t_print.start()
            break
        elif opt == "Y" or opt == 'y':
            # print_stop_event.set()
            # t_print.join()
            # time.sleep(2) ##等待线程停止
            test(fd,extended,remote,brs)
            break
        else:
            print("输入错误，请重新输入")

    try:
        while True:
            time.sleep(1)  # 这里只是简单地保持主线程运行，实际应用中可以根据需要进行更复杂的操作
    except KeyboardInterrupt:
        stop_event.set()
        print_stop_event.set()
        t_recv.join()
        t_send.join()
        t_print.join()
        print("Stopped script")
        exit(0)

if __name__ == "__main__":
    main()


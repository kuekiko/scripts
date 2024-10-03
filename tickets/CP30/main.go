package main

import (
	"crypto/rand"
	"flag"
	"fmt"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/blinkbean/dingtalk"
	"github.com/sirupsen/logrus"
)

// CP30 的 "eventMainId": 1729,
var log = logrus.New()
var dingBot *dingtalk.DingTalk

// init 函数用于设置 logrus 的配置
func init() {
	// 设置日志级别为 InfoLevel（可以改为其他级别，如 DebugLevel, WarnLevel 等）
	log.SetLevel(logrus.DebugLevel)

	// 设置日志格式为文本格式，并包含完整时间戳
	log.SetFormatter(&logrus.TextFormatter{
		FullTimestamp: true, // 打印完整时间
	})

	// 设置日志输出到标准输出
	log.SetOutput(os.Stdout)

	// 也可以将日志输出到文件，具体可以设置为需要的文件路径
	// file, err := os.OpenFile("logrus.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	// if err == nil {
	//     log.SetOutput(file)
	// } else {
	//     log.Warn("无法打开日志文件，使用默认标准输出")
	// }

	var dingToken string = ""
	dingBot = dingtalk.InitDingTalkWithSecret(dingToken, "")
}

func generateRandomHexString(length int) (string, error) {
	bytes := make([]byte, length/2) // 长度为16的字节数组，对应32个hex字符
	_, err := rand.Read(bytes)
	if err != nil {
		return "", err
	}
	// 将字节数组转换为16进制字符串
	return fmt.Sprintf("%x", bytes), nil
}

// TaskInfo 定义
type TaskInfo struct {
	Account        string   //手机号
	Password       string   //密码
	EventMainId    int      //活动的ID
	RealnameList   []string // 买票人信息
	TicketNameList []string // 票名
	RealnameAuth   bool
	Count          int
}

// 票信息
type needTicket struct {
	ID   int
	Name string
}

func main() {
	// 定义命令行参数
	var account string
	var password string
	var eventMainId int
	var realnameList string
	var ticketNameList string
	var needRealnameAuth bool
	var count int

	// 设置命令行参数
	flag.StringVar(&account, "u", "", "账户名")
	flag.StringVar(&password, "p", "", "密码")
	flag.IntVar(&eventMainId, "t", 1729, "活动的ID，默认1729 (cp30)")
	flag.StringVar(&realnameList, "n", "", "购票人名称，多个名称以英文逗号','分隔。eg:张三,李四")
	flag.StringVar(&ticketNameList, "e", "", "票名，多个名称以英文逗号','分隔，中间有空格需要去掉。eg:10月3日VIP票,10月4日VIP票。可以模糊匹配，比如：10月3日,10月4日 表示抢包含有这两个字符串的所有票")
	flag.BoolVar(&needRealnameAuth, "a", true, "是否需要实名（默认需要）")
	flag.IntVar(&count, "c", 0, "购买人数，如果不实名，需要填写这个（一般会限制2-4张），实名可忽略填写")

	// 解析命令行参数
	flag.Parse()

	// 检查 account 和 password 是否为空
	if account == "" || password == "" {
		fmt.Println("账户名 (-u) 和密码 (-p) 是必填项！")
		flag.Usage() // 显示帮助信息
		os.Exit(1)   // 退出程序并返回错误状态
	}

	// 将 realnameList 和 ticketNameList 转换为 []string
	realnames := []string{}
	if realnameList != "" {
		realnames = strings.Split(realnameList, ",")
	}

	ticketNameL := []string{}
	if ticketNameList != "" {
		ticketNameL = strings.Split(ticketNameList, ",")
	}

	// 创建 TaskInfo 实例
	taskInfo := TaskInfo{
		Account:        account,
		Password:       password,
		EventMainId:    eventMainId,
		RealnameList:   realnames,
		TicketNameList: ticketNameL,
		RealnameAuth:   needRealnameAuth,
		Count:          count,
	}

	// log.Debug(taskInfo)
	StartTask(&taskInfo)
}

// todo 登陆失效的问题

func StartTask(task *TaskInfo) {
	// 0 初始化配置
	randomHex, _ := generateRandomHexString(32)
	apiClinet := ApiClient{
		appVersion:    "3.14.7",
		deviceVersion: "33",
		bid:           "cn.comicup.apps.cppub",
		deviceId:      randomHex, //随机
		equipmentType: "1",
		deviceSpec:    "2106118C", //随机
		userAgent:     "okhttp/3.14.7",
	}
	// 1.登陆 获取token
	_, _, err := apiClinet.login(task.Account, task.Password)
	if err != nil {
		log.Info("登录失败:", err)
		return
	}
	purchasereIds := []Purchaser{}

	if task.RealnameAuth {
		// 2.获取 匹配 购票人信息
		purchasereList, err := apiClinet.getPurchaserList()
		if err != nil {
			log.Info("获取购票人信息失败:", err)
			return
		}
		if len(purchasereList) <= 0 {
			log.Info("请先添加购票人:")
			return
		}
		if len(task.RealnameList) > 0 {
			// 根据 realname 匹配购票人信息
			for _, purchasere := range purchasereList {
				for _, realname := range task.RealnameList {
					if purchasere.RealName == realname {
						purchasereIds = append(purchasereIds, purchasere)
					}
				}
			}
		} else {
			// 如果没有指定 realnameList，将所有购票人 ID 加入 ids 列表
			purchasereIds = append(purchasereIds, purchasereList...)
		}
		if len(purchasereIds) == 0 {
			log.Info("没有匹配到购票人信息")
			return
		}
		task.Count = len(purchasereIds)
	}

	// 3.获取票务信息 目前直接for 因为还未开票 需要等待开票，已开票直接或就过去
	// ticketIdList := []int{}
	var startTime time.Time

	ticketIdList := []needTicket{}

	for {
		ticketInfo, err := apiClinet.getTicketType(task.EventMainId)
		if err != nil {
			log.Info("查询票务信息失败:", err)
			return
		}
		log.Infof("查询%v的票务信息", ticketInfo.TicketMain.EventName)
		if len(ticketInfo.TicketTypeList) > 0 {
			timestamp := int64(ticketInfo.TicketTypeList[0].SellStartTime)
			t := time.Unix(0, timestamp*int64(time.Millisecond))
			// 设置中国时区 (UTC+8)
			location, err := time.LoadLocation("Asia/Shanghai")
			if err != nil {
				fmt.Println("加载时区出错:", err)
				return
			}

			// 将时间转换为中国时区的时间
			startTime = t.In(location)

			// 打印时间
			// log.Infof("抢票时间 (UTC+8)::%v", startTime.Format("2006-01-02 15:04:05"))

			// 筛选票务信息，获取符合条件的票 ID 和票名
			for _, ticket := range ticketInfo.TicketTypeList {
				log.Printf("\tId: %v, Name: %v", ticket.ID, ticket.TicketName)
				ticketNameWithoutSpaces := strings.ReplaceAll(ticket.TicketName, " ", "")
				if len(task.TicketNameList) > 0 {
					// 根据 TicketNameList 模糊匹配票名
					for _, ticketName := range task.TicketNameList {
						ticketNameWithoutSpacesToMatch := strings.ReplaceAll(ticketName, " ", "")
						if strings.Contains(ticketNameWithoutSpaces, ticketNameWithoutSpacesToMatch) {
							ticketIdList = append(ticketIdList, needTicket{ID: ticket.ID, Name: ticket.TicketName})
							log.Printf("匹配到指定票: %v", ticket.TicketName)
						}
					}
				} else {
					// 如果没有指定票名，默认将所有票加入列表
					ticketIdList = append(ticketIdList, needTicket{ID: ticket.ID, Name: ticket.TicketName})
				}
			}
			break
		} else {
			log.Infof("%v还未开票，请等待", ticketInfo.TicketMain.EventName)
			time.Sleep(time.Minute * 10)
		}
	}
	// 启动一个协程用于刷新token
	go apiClinet.KeepTokenActive(task.Account, task.Password)
	//执行抢票
	execPurchase(&apiClinet, task, ticketIdList, purchasereIds, startTime, task.Count, 4)
}

// 比较简陋的抢票
func execPurchase(apiClinet *ApiClient, task *TaskInfo, ticketList []needTicket, purchasereIds []Purchaser, startTime time.Time, count int, totalTickets int) {
	// 4.开启抢票任务
	log.Println("抢票任务...")
	log.Debugf("抢票时间 (UTC+8)::%v", startTime.Format("2006-01-02 15:04:05"))
	for _, t := range ticketList {
		log.Infof("票信息：%v-%v", t.ID, t.Name)
	}
	var logPurchasereIds string

	if len(purchasereIds) > 0 {
		for _, p := range purchasereIds {
			log.Infof("购票人：%v", p.RealName)
			logPurchasereIds += p.RealName + " "
		}
	} else {
		log.Infof("无需实名购买")
	}

	for {
		timeUntilStart := time.Until(startTime)

		// 如果距离开始抢票时间小于或等于 2 分钟，退出循环
		if timeUntilStart <= 2*time.Minute {
			fmt.Printf("\r距离开始抢票（提前 2 分钟）还剩：%v天%v小时%v分%v秒\n",
				int(timeUntilStart.Hours())/24,
				int(timeUntilStart.Hours())%24,
				int(timeUntilStart.Minutes())%60,
				int(timeUntilStart.Seconds())%60)
			break
		}

		// 打印倒计时，刷新输出
		fmt.Printf("\r距离开始抢票（提前 2 分钟）还剩：%v天%v小时%v分%v秒",
			int(timeUntilStart.Hours())/24,
			int(timeUntilStart.Hours())%24,
			int(timeUntilStart.Minutes())%60,
			int(timeUntilStart.Seconds())%60)

		// 每秒更新一次倒计时
		time.Sleep(time.Second)
	}
	log.Println("开始执行抢票任务...")
	dingBot.SendTextMessage(fmt.Sprintf("开始抢票，购票人信息：%v,要抢的票：%v", logPurchasereIds, ticketList))

	// 协程池设置：最多 20 个协程池
	maxWorkers := 20
	taskChan := make(chan needTicket, maxWorkers)

	// 用于累计抢购到的总票数
	totalSuccessTickets := 0
	var totalMu sync.Mutex // 保护对 totalSuccessTickets 的并发访问

	// 开启协程池，处理抢票任务
	var wg sync.WaitGroup
	for i := 0; i < maxWorkers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for ticket := range taskChan {
				// 每个票 ID 最少 2 个协程，最多 5 个
				successChan := make(chan struct{})
				stopChan := make(chan struct{})

				// 创建协程来执行抢票任务
				for j := 0; j < 5; j++ {
					go func(workerID int) {
						for {
							select {
							case <-stopChan:
								log.Printf("协程 %d 停止抢票：%v (ticketID: %d)", workerID, ticket.Name, ticket.ID)
								return
							default:
								// 尝试抢票
								success, err := apiClinet.buyTicketAlipay(ticket.ID, purchasereIds, count)
								if err != nil {
									log.Printf("协程 %d 抢票失败: %v (ticketID: %d)", workerID, err, ticket.ID)
								} else if success {
									msg := fmt.Sprintf("账号：%v,协程 %d 成功抢到票: %v (ticketID: %d)。购票人：%v，一共%v张", task.Account, workerID, ticket.Name, ticket.ID, logPurchasereIds, count)
									log.Printf(msg)
									dingBot.SendTextMessage(msg)
									successChan <- struct{}{} // 通知其他协程停止
									return
								} else {
									log.Printf("协程 %d 未能成功抢到票: %v (ticketID: %d)", workerID, ticket.Name, ticket.ID)
								}
							}
						}
					}(j)
				}

				// 等待抢票结果

				<-successChan
				// 抢票成功后，关闭 stopChan 通知所有协程停止
				close(stopChan)
				totalMu.Lock()
				totalSuccessTickets++
				if totalSuccessTickets >= totalTickets {
					log.Println("已达到抢票目标，停止所有任务")
					close(taskChan) // 关闭任务通道，停止所有协程
				}
				totalMu.Unlock()
			}
		}()
	}

	// 分配任务
	for _, ticket := range ticketList {
		taskChan <- ticket
	}

	// 关闭任务通道，等待所有任务完成
	close(taskChan)
	wg.Wait()

	log.Println("抢票任务全部完成")
}

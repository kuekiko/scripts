package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/sirupsen/logrus"
)

var httpClient = resty.New()

type ApiClient struct {
	cookie string
	//
	token         string
	appVersion    string
	deviceVersion string
	bid           string
	deviceId      string
	equipmentType string
	deviceSpec    string
	// headers
	userAgent string
}

// 登录获取Token
// 登录获取Token并返回token和cookie
func (client *ApiClient) login(account, password string) (string, string, error) {
	url := "https://user.allcpp.cn/api/login/normal"
	payload := map[string]string{
		"account":       account,
		"password":      password,
		"appVersion":    client.appVersion,
		"deviceVersion": client.deviceVersion,
		"bid":           client.bid,
		"deviceId":      client.deviceId,
		"equipmentType": client.equipmentType,
		"deviceSpec":    client.deviceSpec,
		"token":         "", // Assuming the token is the correct one
	}

	log.WithFields(logrus.Fields{
		"account": account,
	}).Info("开始登录请求")

	// 发送 POST 请求
	resp, err := httpClient.R().
		SetHeaders(map[string]string{
			"Content-Type":    "application/x-www-form-urlencoded",
			"Cookie":          "",
			"accept-encoding": "gzip",
			"user-agent":      "okhttp/3.14.7",
			"appheader":       "mobile",
			"equipmenttype":   client.equipmentType,
			"deviceversion":   client.deviceVersion,
			"devicespec":      client.deviceSpec,
			"appversion":      client.appVersion,
			"mobilesource":    "Android",
		}).
		SetFormData(payload).
		Post(url)

	if err != nil {
		log.WithError(err).Error("登录请求失败")
		return "", "", err
	}

	// 打印 Response Header 信息
	log.WithFields(logrus.Fields{
		"Headers": resp.Header(),
	}).Debug("登录响应头信息")

	// 打印 Response Body 信息
	log.Debugf("登录响应内容: %s", resp.String())

	// 解析 Body
	var result map[string]interface{}
	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		log.WithError(err).Error("解析登录响应失败")
		return "", "", err
	}

	// 获取 body 中的 token
	token, ok := result["token"].(string)
	if !ok {
		log.Error("登录失败，未获取到 token")
		return "", "", errors.New("登录失败，未获取到 token")
	}

	// 获取 header 中的 set-cookie
	setCookie := resp.Header().Get("Set-Cookie")
	// 去掉 'path=/;' 部分
	setCookieClean := strings.ReplaceAll(setCookie, "path=/; ", "")

	cookieParts := strings.Split(setCookieClean, ";")
	var jsessionID string
	for _, part := range cookieParts {
		if strings.HasPrefix(part, "JSESSIONID") {
			jsessionID = strings.TrimSpace(part)
		}
	}

	// 拼接返回的 cookie，并添加 body 中的 token
	cookie := jsessionID + "; " + `token="` + token + `"`

	// 存储到 ApiClient
	client.token = token
	client.cookie = cookie

	// 打印获取到的 token 和 cookie
	log.WithFields(logrus.Fields{
		"token":  token,
		"cookie": cookie,
	}).Info("登录成功，获取到 token 和 cookie")

	return token, cookie, nil
}

// 购票人信息
// 定义自定义结构体，用于解析购票人信息
type Purchaser struct {
	ID        int    `json:"id"`
	IDCard    string `json:"idcard"`
	Mobile    string `json:"mobile"`
	RealName  string `json:"realname"`
	ValidType int    `json:"validType"`
}

// 获取购票人信息
func (client *ApiClient) getPurchaserList() ([]Purchaser, error) {
	url := "https://www.allcpp.cn/allcpp/user/purchaser/getList.do"

	log.Info("获取购票人信息请求发起")

	resp, err := httpClient.R().
		SetQueryParams(map[string]string{
			"appVersion":    client.appVersion,
			"deviceVersion": client.deviceVersion,
			"bid":           client.bid,
			"deviceId":      client.deviceId,
			"deviceSpec":    client.deviceSpec,
			"token":         client.token,
			"equipmentType": client.equipmentType,
		}).
		SetHeaders(map[string]string{
			"User-Agent":      client.userAgent,
			"Cookie":          client.cookie,
			"accept-encoding": "gzip",
		}).
		Get(url)

	if err != nil {
		log.WithError(err).Error("获取购票人信息请求失败")
		return nil, err
	}

	var purchasers []Purchaser
	if err := json.Unmarshal(resp.Body(), &purchasers); err != nil {
		log.WithError(err).Error("解析购票人信息响应失败")
		return nil, err
	}

	log.Debugf("购票人原始信息：%v", purchasers)
	return purchasers, nil
}

// 添加购票人信息 todo 还需修正
func (client *ApiClient) addPurchaserInfo(realname, idcard, mobile string) error {
	url := "https://www.allcpp.cn/allcpp/user/purchaser/addModel.do"
	body := map[string]interface{}{
		"code":      "", //todo 验证码
		"id":        0,
		"idcard":    idcard,
		"mobile":    mobile,
		"realname":  realname,
		"validType": 0,
	}
	resp, err := httpClient.R().
		SetHeaders(map[string]string{
			"Content-Type":  "application/json",
			"User-Agent":    client.userAgent,
			"appheader":     "mobile",
			"equipmenttype": client.equipmentType,
			"deviceversion": client.deviceVersion,
			"appversion":    client.appVersion,
			"mobilesource":  "Android",
			"Cookie":        client.cookie,
		}).
		SetBody(body).
		Post(url)

	if err != nil {
		return err
	}

	log.Debugf("添加购票人信息返回: %v", string(resp.Body()))
	return nil
}

// 票相关信息
type TicketMain struct {
	ID               int         `json:"id"`
	Name             string      `json:"name"`
	EventName        string      `json:"eventName"`
	Description      string      `json:"description"`
	EventDescription string      `json:"eventDescription"`
	CoverPicId       int         `json:"coverPicId"`
	CoverPicUrl      string      `json:"coverPicUrl"`
	PicId            int         `json:"picId"`
	Priority         int         `json:"priority"`
	Enabled          int         `json:"enabled"`
	EventMainID      int         `json:"eventMainId"`
	Type             int         `json:"type"`
	CreateTime       int64       `json:"createTime"`
	UpdateTime       int64       `json:"updateTime"`
	ConfirmableVO    interface{} `json:"confirmableVO"` // 处理 null 值
}

type TicketType struct {
	ID                int         `json:"id"`
	EventID           int         `json:"eventId"`
	TicketMainID      int         `json:"ticketMainId"`
	TicketName        string      `json:"ticketName"`
	TicketAttribute   int         `json:"ticketAttribute"`
	TicketPrice       int         `json:"ticketPrice"`
	PurchaseNum       int         `json:"purchaseNum"`
	RemainderNum      int         `json:"remainderNum"`
	LockNum           int         `json:"lockNum"`
	Session           int         `json:"session"`
	SellStartTime     int64       `json:"sellStartTime"`
	SellEndTime       int64       `json:"sellEndTime"`
	OpenTimer         int         `json:"openTimer"`
	TicketDescription string      `json:"ticketDescription"`
	TicketGPStartTime int64       `json:"ticketGPStartTime"`
	TicketGPEndTime   int64       `json:"ticketGPEndTime"`
	RealnameAuth      bool        `json:"realnameAuth"`
	Square            string      `json:"square"`
	CreateTime        interface{} `json:"createTime"`
	UpdateTime        int64       `json:"updateTime"`
}

// 顶层结构体
type TicketResponse struct {
	TicketMain     TicketMain   `json:"ticketMain"`
	TicketTypeList []TicketType `json:"ticketTypeList"`
}

// 获取票的类别
func (client *ApiClient) getTicketType(eventMainId int) (*TicketResponse, error) {
	url := "https://www.allcpp.cn/allcpp/ticket/getTicketTypeList.do"

	resp, err := httpClient.R().
		SetQueryParams(map[string]string{
			"appVersion":    client.appVersion,
			"deviceVersion": client.deviceVersion,
			"bid":           client.bid,
			"deviceId":      client.deviceId,
			"deviceSpec":    client.deviceSpec,
			"token":         client.token,
			"equipmentType": client.equipmentType,
			"eventMainId":   fmt.Sprintf("%d", eventMainId),
			"ticketMainId":  "0",
		}).
		SetHeaders(map[string]string{
			"encoding":   "gzip",
			"User-Agent": client.userAgent,
			"Cookie":     client.token, // assuming client.token contains the cookie value
			"Connection": "keep-alive",
		}).
		Get(url)

	if err != nil {
		return nil, err
	}

	// 定义用于存储完整响应的结构体
	var result TicketResponse

	// 将响应数据反序列化到 result 结构体中
	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		log.WithError(err).Error("解析票种信息失败")
		return nil, err
	}

	// 返回完整的票信息（TicketMain 和 TicketTypeList）
	return &result, nil
}

func (client *ApiClient) buyTicketAlipay(ticketTypeId int, purchaserIds []Purchaser, count int) (bool, error) {
	baseURL := "https://www.allcpp.cn/api/ticket/buyticketalipay.do"

	// 将 []int 类型的 purchaserIds 转换为 []string
	var purchaserIdsStr []string
	var purchaserIdsArgs string
	if len(purchaserIds) > 0 {
		for _, u := range purchaserIds {
			purchaserIdsStr = append(purchaserIdsStr, fmt.Sprintf("%d", u.ID))
		}
		purchaserIdsArgs = strings.Join(purchaserIdsStr, ",")
		// 按人数配置
		count = len(purchaserIds)
	} else {
		purchaserIdsArgs = ""
	}

	// 设置请求表单数据
	formData := map[string]string{
		"count":         fmt.Sprintf("%d", count),
		"purchaserIds":  purchaserIdsArgs,
		"ticketTypeId":  fmt.Sprintf("%d", ticketTypeId),
		"appVersion":    client.appVersion,
		"deviceVersion": client.deviceVersion,
		"bid":           client.bid,
		"deviceId":      client.deviceId,
		"equipmentType": client.equipmentType,
		"deviceSpec":    client.deviceSpec,
		"token":         client.token, // Assuming the token is the correct one
	}

	// 发起 POST 请求
	resp, err := httpClient.R().
		SetHeaders(map[string]string{
			"Content-Type":    "application/x-www-form-urlencoded",
			"Cookie":          client.cookie, // Assuming client.cookie contains the necessary cookie
			"accept-encoding": "gzip",
			"user-agent":      "okhttp/3.14.7",
			"appheader":       "mobile",
			"equipmenttype":   client.equipmentType,
			"deviceversion":   client.deviceVersion,
			"devicespec":      client.deviceSpec,
			"appversion":      client.appVersion,
			"mobilesource":    "Android",
		}).
		SetFormData(formData). // 使用 SetFormData 发送表单数据
		Post(baseURL)

	if err != nil {
		fmt.Println("请求抢票失败:", err)
		return false, err
	}

	// 解析返回的 JSON
	var result map[string]interface{}
	if err := json.Unmarshal(resp.Body(), &result); err != nil {
		log.Println("解析抢票返回失败:", err)
		return false, err
	}

	// 检查是否成功
	if isSuccess, ok := result["isSuccess"].(bool); ok && isSuccess {
		log.Println("抢票成功!")

		// 获取 result 数据
		if resultData, ok := result["result"].(map[string]interface{}); ok {
			outTradeNo := resultData["outTradeNo"].(string)
			orderInfo := resultData["orderInfo"].(string)
			log.Printf("订单号: %s\n订单信息: %s\n", outTradeNo, orderInfo)
		}

		// 抢票成功，返回 true
		return true, nil
	} else {
		// 输出失败信息
		log.Println("抢票失败:", string(resp.Body()))
	}

	// 抢票失败，返回 false
	return false, nil
}

// 用于保活和刷新
func (client *ApiClient) KeepTokenActive(account, password string) {
	// 使用token请求某写页面检测是否失效，如果失效则刷写token
	// 每 10 分钟执行一次的无限循环
	for {
		// 构建请求 URL
		url := "https://user.allcpp.cn/rest/my"

		// 发起 GET 请求
		resp, err := httpClient.R().
			SetQueryParams(map[string]string{
				"appVersion":    client.appVersion,
				"deviceVersion": client.deviceVersion,
				"bid":           client.bid,
				"deviceId":      client.deviceId,
				"deviceSpec":    client.deviceSpec,
				"token":         client.token,
				"equipmentType": client.equipmentType,
			}).
			SetHeaders(map[string]string{
				"encoding":   "gzip",
				"User-Agent": client.userAgent,
				"Cookie":     client.token,
				"Connection": "keep-alive",
			}).
			Get(url)

		// 检查请求是否成功
		if err != nil {
			log.Errorf("检测 token 是否失效时发生错误: %v", err)
		} else if resp.StatusCode() != 200 {
			log.Warn("Token 已失效，准备刷新 token...")
			client.login(account, password)
		} else {
			log.Println("Token 有效，继续保活...")
		}
		// 每 10 分钟执行一次
		time.Sleep(10 * time.Minute)
	}
}

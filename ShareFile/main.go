package main

import (
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"text/template"
)

var (
	// maxUploadSize = 1024 * 1024 * 2014 //最大上传1GB
	uploadPath = "/tmp" //上传保存位置
)

func main() {
	var path string
	var port string
	flag.StringVar(&path, "d", "./", "downPath")
	flag.StringVar(&port, "p", "8888", "Port")
	flag.StringVar(&uploadPath, "o", "/tmp", "uploadPath")
	flag.Parse()
	// 下载服务
	http.Handle("/", http.FileServer(http.Dir(path)))
	// 上传服务
	http.HandleFunc("/up", uploadFileHandler())
	fmt.Printf("Download server linsten Address http://0.0.0.0:%v\npath is %v\n", port, path)
	fmt.Printf("Upload server linsten Address http://0.0.0.0:%v/up\n", port)
	http.ListenAndServe(":"+port, nil)
}

func uploadFileHandler() http.HandlerFunc {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		tmpl := template.New("upload")
		tmpl = template.Must(tmpl.Parse(
			`<!DOCTYPE html>
			<html lang="en">
			<head>
			  <meta http-equiv="Content-Type" content="multipart/form-data; charset=utf-8" />
			  <title>Upload</title>
			</head>
			<body>
			  <form action="up" method="post" enctype="multipart/form-data">
				<input name="file" type="file"/>
				<input type="submit" value="提交">
			  </form>
			<text>{{.}}<text>
			</body>`))
		fmt.Println("method:", r.Method) // 获取请求的方法
		if r.Method == "GET" {
			// 显示上传页面
			tmpl.Execute(w, "")
		} else if r.Method == "POST" {
			// 存储文件
			r.ParseMultipartForm(32 << 20)
			file, handler, err := r.FormFile("file")
			if err != nil {
				fmt.Println(err)
				return
			}
			defer file.Close()
			// todo 上传文件限制
			// uploadPath 创建  权限不足的问题
			os.MkdirAll(uploadPath, 0777)
			// todo 安全问题 未做文件名校验 可以直接遍历上传
			f, err := os.OpenFile(uploadPath+"/"+handler.Filename, os.O_WRONLY|os.O_CREATE, 0666)
			if err != nil {
				fmt.Println(err)
				return
			}
			defer f.Close()
			io.Copy(f, file)
			//缓冲区
			data := fmt.Sprintf("文件上传成功: %v\n", uploadPath+"/"+handler.Filename)
			tmpl.Execute(w, data)

		} else {
			// 请求方法不对
			fmt.Printf("请求Method %v error\n", r.Method)
			fmt.Fprintf(w, "请求Method %v error\n", "r.Method")
		}
	})
}

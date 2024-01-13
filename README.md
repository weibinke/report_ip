# report_ip

## 服务端部署
```
git clone https://github.com/weibinke/report_ip.git
cd report_ip
pip install -r requirements.txt
python main.py
```

配置开机自动运行。

## 客户端定期上报
- 访问：http://127.0.0.1:6222/
- 上报接口：http://127.0.0.1:6222/report?hostname=[主机名]&internal_ip=[内网IP]
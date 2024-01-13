# report_ip

## 服务端部署
### 启动服务
```
git clone https://github.com/weibinke/report_ip.git
cd report_ip
pip install -r requirements.txt
python main.py
```

- 查看记录：http://127.0.0.1:6222/
- 上报接口：http://127.0.0.1:6222/report?hostname=[主机名]&internal_ip=[内网IP]


### 配置开机自动运行。
Given the location of your script at `/home/ec2-user/report_ip/main.py`, you can create a systemd service file to run this script at boot and in the background. Here i
s how you can do that:

1. **Create a systemd service file:**

   Open a new service file in the `/etc/systemd/system` directory with a text editor. You can name the file something like `report_ip.service`.

   ```sh
   sudo nano /etc/systemd/system/report_ip.service
   ```

   Add the following content to the file:

   ```ini
   [Unit]
   Description=Report IP Service
   After=network.target

   [Service]
   Type=simple
   User=ec2-user
   Group=ec2-user
   WorkingDirectory=/home/ec2-user/report_ip
   ExecStart=/usr/bin/python /home/ec2-user/report_ip/main.py
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```

   Make sure to replace `/usr/bin/python` with the path to the correct Python interpreter if you are using a different version, such as Python 3 (`/usr/bin/python3`).

2. **Reload systemd manager configuration:**

   Reload the systemd manager configuration to recognize the new service:

   ```sh
   sudo systemctl daemon-reload
   ```

3. **Enable the service:**

   Enable the service to start on boot:

   ```sh
   sudo systemctl enable report_ip.service
   ```

4. **Start the service:**

   Start the service immediately without rebooting:

   ```sh
   sudo systemctl start report_ip.service
   ```

5. **Check the status of the service:**

   Check that the service is running properly:

   ```sh
   sudo systemctl status report_ip.service
   ```

Now your `main.py` script should start automatically when the system boots up and run in the background. If it fails, systemd will attempt to restart it automatically, as specified by the `Restart=on-failure` directive.

You can view the logs for your service at any time with:

```sh
journalctl -u report_ip.service
```

This will show the logs generated by your script, which can be useful for debugging and monitoring its activity.

## 客户端定期上报
写脚本自动更新外网ip到服务器，方便外面ssh连接。

使用方法：
1）把下面的脚本放到服务器的某个目录，然后修改host的值为自己想要看到的名字，注意这里不要有特殊字符和空格。

执行chmod +x  auto_update_ip.sh，这里文件名根据自己保存的修改。

```
#!/bin/sh

host="weibin_home"
base_dir=$(cd "$(dirname "$0")"; pwd)
local_ip=`/sbin/ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d "addr:"`

url="http://your_server_ip:6222/report?hostname=$host&internal_ip=$local_ip"

echo "report start\n"                                                                                                                                                 
curl $url
echo "\nreport end.\n"
```

2）添加系统定时任务，例如每5分钟执行一次ip上报：

crontab -e

在末尾添加一行，内容为：这里的5，表示5分钟执行一次，可以根据自己需要改，sh和log的路径根据自己实际情况来。

*/5 * * * * /bin/sh /home/pi/weibin/tools/./auto_update_ip.sh>>/home/pi/weibin/tools/log.txt

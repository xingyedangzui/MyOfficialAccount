# 微信公众号服务部署指南

## 快速部署

### 1. 上传文件到服务器
将所有文件上传到你的Linux服务器上的某个目录，例如：`/home/ubuntu/wechat-service`

### 2. 安装依赖
```bash
# 安装Python3和pip（如果没有的话）
sudo apt update
sudo apt install python3 python3-pip -y

# 安装项目依赖
pip3 install -r requirements.txt
```

### 3. 一键部署
```bash
# 给部署脚本执行权限
chmod +x deploy.sh

# 运行部署脚本（需要sudo权限）
sudo bash deploy.sh
```

## 服务管理命令

### 查看服务状态
```bash
sudo systemctl status wechat-service
```

### 查看实时日志
```bash
sudo journalctl -u wechat-service -f
```

### 重启服务
```bash
sudo systemctl restart wechat-service
```

### 停止服务
```bash
sudo systemctl stop wechat-service
```

### 启动服务
```bash
sudo systemctl start wechat-service
```

### 禁用开机自启
```bash
sudo systemctl disable wechat-service
```

## 服务特性

✅ **自动重启**：程序崩溃时自动重启
✅ **开机自启**：服务器重启后自动启动
✅ **日志管理**：统一的日志管理和查看
✅ **端口绑定**：监听所有网络接口的80端口
✅ **后台运行**：退出SSH连接后继续运行

## 注意事项

1. **防火墙设置**：确保服务器的80端口对外开放
   ```bash
   # Ubuntu/Debian
   sudo ufw allow 80
   
   # CentOS/RHEL
   sudo firewall-cmd --permanent --add-port=80/tcp
   sudo firewall-cmd --reload
   ```

2. **微信公众号配置**：将微信公众号的服务器URL设置为：
   ```
   http://你的服务器IP/wx
   ```

3. **HTTPS配置**：生产环境建议使用nginx反向代理配置HTTPS

## 故障排查

### 查看最近的错误日志
```bash
sudo journalctl -u wechat-service -n 50
```

### 查看服务是否在运行
```bash
sudo systemctl is-active wechat-service
```

### 手动测试程序
```bash
# 先停止服务
sudo systemctl stop wechat-service

# 手动运行程序测试
cd /path/to/your/project
python3 main.py
```
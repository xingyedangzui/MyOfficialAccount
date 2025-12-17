# JSON数据持久化系统使用说明

## 概述

本项目实现了一个完整的JSON数据持久化系统，用于在微信公众号项目中存储和管理数据。系统包含两个主要组件：

- **JSONDataManager**: 通用的JSON数据管理器
- **UserDataManager**: 专门用于微信用户数据管理的工具

## 目录结构

```
MyOfficialAccount/
├── data/                    # JSON数据文件存储目录（自动创建）
│   ├── users.json          # 用户信息数据
│   ├── user_messages.json  # 用户消息记录
│   ├── statistics.json     # 统计数据
│   ├── reply_rules.json    # 自定义回复规则
│   └── config.json         # 配置数据
├── script/
│   ├── data_manager.py     # 数据管理模块
│   ├── handle.py           # 已集成数据持久化的消息处理器
│   └── examples_data_usage.py # 使用示例
└── README_数据持久化.md
```

## 快速开始

### 1. 基础使用

```python
from script.data_manager import data_manager, user_data_manager

# 保存配置数据
config = {
    "app_name": "我的微信公众号",
    "version": "1.0.0",
    "debug": True
}
data_manager.save_data("config", config)

# 读取配置数据
config = data_manager.load_data("config")
print(config)  # {'app_name': '我的微信公众号', 'version': '1.0.0', 'debug': True}
```

### 2. 用户数据管理

```python
# 保存用户信息
user_info = {
    "nickname": "张三",
    "city": "北京",
    "gender": "男"
}
user_data_manager.save_user_info("user_openid_123", user_info)

# 记录用户消息
user_data_manager.record_user_message("user_openid_123", "text", "你好")

# 获取用户信息
user = user_data_manager.get_user_info("user_openid_123")

# 获取用户消息历史
messages = user_data_manager.get_user_messages("user_openid_123", limit=10)
```

## 核心功能

### JSONDataManager

#### 主要方法

- `save_data(filename, data)` - 保存数据到JSON文件
- `load_data(filename, default_value)` - 从JSON文件加载数据
- `update_data(filename, update_func)` - 更新JSON文件中的数据
- `delete_file(filename)` - 删除JSON文件
- `list_files()` - 列出所有JSON文件

#### 使用示例

```python
from script.data_manager import JSONDataManager

# 创建数据管理器（数据存储在 data/ 目录）
dm = JSONDataManager()

# 保存数据
success = dm.save_data("test", {"name": "测试", "count": 1})

# 加载数据
data = dm.load_data("test", {"name": "默认", "count": 0})

# 更新数据
def increment_count(current_data):
    if current_data is None:
        current_data = {"count": 0}
    current_data["count"] += 1
    return current_data

dm.update_data("test", increment_count)
```

### UserDataManager

#### 用户信息管理

```python
# 保存用户信息
user_info = {
    "nickname": "用户昵称",
    "avatar": "头像URL",
    "city": "城市",
    "province": "省份",
    "country": "国家"
}
user_data_manager.save_user_info("openid", user_info)

# 获取用户信息
user = user_data_manager.get_user_info("openid")
```

#### 消息记录管理

```python
# 记录文本消息
user_data_manager.record_user_message("openid", "text", "用户发送的文本")

# 记录图片消息
user_data_manager.record_user_message("openid", "image", "图片MediaId: xxx")

# 记录菜单点击
user_data_manager.record_user_message("openid", "menu_click", "菜单点击: MENU_HELP")

# 获取用户消息历史（最近10条）
messages = user_data_manager.get_user_messages("openid", limit=10)
```

#### 统计数据管理

```python
# 更新统计数据
user_data_manager.update_statistics("subscribe")      # 关注事件
user_data_manager.update_statistics("text_message")   # 文本消息
user_data_manager.update_statistics("image_message")  # 图片消息
user_data_manager.update_statistics("menu_click")     # 菜单点击

# 获取统计数据
stats = user_data_manager.get_statistics()
print(stats)
```

## 高级功能

### 1. 自定义回复规则

```python
# 设置回复规则
reply_rules = {
    "你好": "你好！很高兴为您服务！",
    "帮助": "这里是帮助信息...",
    "时间": "当前时间是: {time}",  # 支持动态替换
    "拜拜": "再见！期待下次与您交流！"
}

data_manager.save_data("reply_rules", reply_rules)

# 在消息处理中使用
def get_reply(user_input):
    rules = data_manager.load_data("reply_rules", {})
    if user_input in rules:
        reply = rules[user_input]
        if "{time}" in reply:
            import time
            reply = reply.replace("{time}", time.strftime('%Y-%m-%d %H:%M:%S'))
        return reply
    return "默认回复"
```

### 2. 创建专用数据目录

```python
from script.data_manager import JSONDataManager

# 创建日志管理器（数据存储在 logs/ 目录）
logs_manager = JSONDataManager("logs")

# 创建缓存管理器（数据存储在 cache/ 目录）
cache_manager = JSONDataManager("cache")
```

### 3. 批量数据操作

```python
# 批量保存用户数据
users = [
    {"openid": "user1", "name": "张三"},
    {"openid": "user2", "name": "李四"},
    {"openid": "user3", "name": "王五"}
]

for user in users:
    user_data_manager.save_user_info(user["openid"], {"nickname": user["name"]})
```

## 数据文件说明

### users.json - 用户信息

```json
{
  "用户openid": {
    "nickname": "用户昵称",
    "status": "subscribed",
    "subscribe_time": "1702713000",
    "subscribe_time_str": "2024-12-16 14:50:00",
    "source": "wechat_official_account",
    "first_subscribe": true,
    "last_update": 1702713000.123,
    "last_update_str": "2024-12-16 14:50:00"
  }
}
```

### user_messages.json - 用户消息

```json
{
  "用户openid": [
    {
      "type": "text",
      "content": "你好",
      "timestamp": 1702713000.123,
      "time_str": "2024-12-16 14:50:00"
    }
  ]
}
```

### statistics.json - 统计数据

```json
{
  "daily": {
    "2024-12-16": {
      "subscribe": 5,
      "text_message": 120,
      "image_message": 15,
      "menu_click": 30
    }
  },
  "total": {
    "subscribe": 1250,
    "text_message": 15600,
    "image_message": 890,
    "menu_click": 3200
  }
}
```

## 在微信公众号中的集成

系统已经完全集成到 `handle.py` 中：

1. **关注事件**: 自动保存用户信息和更新统计
2. **取消关注**: 更新用户状态为取消关注
3. **文本消息**: 记录消息内容和更新统计
4. **图片消息**: 记录MediaId和更新统计
5. **菜单点击**: 记录点击事件和更新统计

## 运行示例

```bash
# 运行示例代码
cd script
python examples_data_usage.py
```

## 特性

✅ **线程安全**: 使用锁机制确保并发操作安全  
✅ **自动创建**: 数据目录和文件自动创建  
✅ **错误处理**: 完善的异常处理机制  
✅ **灵活配置**: 支持自定义数据存储目录  
✅ **数据清理**: 自动清理过期数据（如30天前的统计数据）  
✅ **统计分析**: 内置日统计和总统计功能  
✅ **用户追踪**: 完整的用户生命周期管理  

## 注意事项

1. **文件权限**: 确保应用有权限在项目目录下创建和写入文件
2. **磁盘空间**: 定期检查数据文件大小，避免占用过多磁盘空间
3. **备份策略**: 建议定期备份重要的数据文件
4. **并发访问**: 系统已实现线程安全，但在高并发场景下建议进行压力测试
5. **数据验证**: 在保存重要数据前建议进行数据格式验证

## 扩展建议

1. **数据压缩**: 对于大量数据可以考虑gzip压缩
2. **数据库迁移**: 数据量很大时可以考虑迁移到SQLite或其他数据库
3. **定时任务**: 可以添加定时清理和数据汇总任务
4. **监控告警**: 添加数据异常监控和告警机制
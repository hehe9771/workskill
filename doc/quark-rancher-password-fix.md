# 夸克浏览器 Rancher 密码自动填充修复

## 问题描述
在 Rancher 登录页面（https://rancher.nbmarket.cn/dashboard/auth/login）输入 admin 时，夸克浏览器无法自动带出保存的密码。

## 根因分析
经过诊断发现两个问题：

1. **Login Data 数据库 action_url 为空**
   - Chromium 密码管理器需要通过 `action_url` 匹配登录表单
   - Rancher 的记录中 `action_url` 为空，导致无法匹配

2. **Rancher 页面设置了 `autocomplete="off"`**
   - 用户名和密码输入框都有此属性
   - 浏览器默认尊重此设置，不自动填充密码

## 已应用的修复

### 1. 修复 Login Data 数据库
- 文件：`%LOCALAPPDATA%\Quark\User Data\Default\Login Data`
- 修改：将 `action_url` 从空值更新为 `https://rancher.nbmarket.cn/dashboard/auth/login`
- 备份：`Login Data.backup_fix`

### 2. 添加浏览器启动参数
- `--enable-password-force-saving` - 强制启用密码保存
- `--disable-features=PasswordManagerAutocompleteOff` - 忽略网站的 autocomplete=off

### 3. 创建专用快捷方式
- 位置：`C:\Users\wuyan\Desktop\夸克-Rancher.lnk`
- 描述：夸克浏览器（启用密码自动填充，忽略 autocomplete=off）

## 使用方法

### 方法1：使用桌面快捷方式（推荐）
1. 双击桌面上的 **"夸克-Rancher"** 快捷方式
2. 在地址栏输入 `https://rancher.nbmarket.cn/dashboard/auth/login`
3. 点击用户名输入框
4. 应该弹出密码建议列表，选择 `admin`
5. 密码自动填充

### 方法2：手动触发密码填充
如果使用普通方式打开夸克浏览器：
1. 打开 Rancher 登录页面
2. 点击用户名输入框
3. 按 `Ctrl+Shift+F` 或点击地址栏的钥匙图标
4. 选择保存的密码

### 方法3：通过密码管理器
1. 点击夸克菜单 → 设置 → 密码和自动填充
2. 搜索 "rancher"
3. 点击编辑，确保用户名和密码正确
4. 返回登录页面，手动选择填充

## 验证步骤
1. 关闭所有夸克浏览器窗口
2. 使用桌面快捷方式重新启动
3. 访问 Rancher 登录页面
4. 点击用户名输入框，观察是否弹出密码建议
5. 选择 admin，确认密码自动填充

## 技术细节

### 数据库修复
```python
import sqlite3
conn = sqlite3.connect('Login Data')
cursor = conn.cursor()
cursor.execute("""
    UPDATE logins
    SET action_url = 'https://rancher.nbmarket.cn/dashboard/auth/login'
    WHERE origin_url = 'https://rancher.nbmarket.cn/'
""")
conn.commit()
conn.close()
```

### 启动参数说明
- `--enable-password-force-saving`: 强制浏览器保存和提供密码建议
- `--disable-features=PasswordManagerAutocompleteOff`: 让密码管理器忽略 autocomplete=off 属性

## 故障排除

### 如果仍然无法自动填充：
1. 检查是否使用了正确的快捷方式（带启动参数）
2. 确认夸克浏览器设置中"自动登录"已开启
3. 检查密码管理器中是否有 rancher.nbmarket.cn 的记录
4. 尝试删除旧密码记录，重新登录让浏览器保存

### 检查密码记录：
```powershell
# 使用 Python 检查 Login Data
python -c "
import sqlite3
conn = sqlite3.connect(r'C:\Users\wuyan\AppData\Local\Quark\User Data\Default\Login Data')
cursor = conn.cursor()
cursor.execute('SELECT origin_url, action_url, username_value FROM logins WHERE origin_url LIKE \"%rancher%\"')
for row in cursor.fetchall():
    print(f'Origin: {row[0]}')
    print(f'Action: {row[1]}')
    print(f'User: {row[2]}')
conn.close()
"
```

## 修复时间
2026-07-01

## 相关文件
- 密码数据库：`%LOCALAPPDATA%\Quark\User Data\Default\Login Data`
- 浏览器配置：`%LOCALAPPDATA%\Quark\User Data\Default\Preferences`
- 桌面快捷方式：`C:\Users\wuyan\Desktop\夸克-Rancher.lnk`
- 备份文件：
  - `Login Data.backup_fix`
  - `Preferences.backup_autofill_*`

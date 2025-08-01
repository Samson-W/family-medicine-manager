# 家庭慢性病患者药物管理系统

这是一个基于Python Tkinter的家庭慢性病患者药物管理系统，具有图形用户界面，支持多用户药物信息的录入、查询、修改、删除和智能买药提醒功能。

## 需要依赖
```
python>=3.10
tkcalendar
```

## Debian系列版本(目前Linux mint 21.3&Debian 12验证通过)
```
sudo apt-get install  /full-path-name/family-medicine-manager_1.0.0-1_all.deb
```

## Windows版本
windows-version目录下的medicine_manager.exe可直接运行，medicine_manager.py可直接在命令行中使用python命令行进行运行。

## 功能特性

### 1. 多用户药物管理
- **使用人管理**: 支持爸爸、妈妈、爷爷、奶奶、外婆、外爷、儿子、女儿等家庭成员
- **个性化管理**: 每个家庭成员可以独立管理自己的药物
- **可编辑使用人**: 支持自定义使用人名称

### 2. 药物信息管理
- **添加药物**: 录入新的药物信息
- **编辑药物**: 双击表格行快速编辑药物信息
- **删除药物**: 删除不需要的药物记录
- **搜索药物**: 支持按药物名称、使用人和备注搜索
- **清空输入**: 快速清空输入框

### 3. 药物信息字段
- **使用人**: 药物使用者（下拉选择 + 可编辑）
- **品名及规格**: 药物名称和规格
- **每日服用片数**: 每日服用剂量（支持0.25, 0.5, 1-100）
- **每盒片数**: 每盒药物的片数（1-100）
- **购买盒数**: 购买的盒数（1-100）
- **购药日期**: 购买日期（日期选择器）
- **下次需买药时间**: 自动计算的下次购买时间
- **备注**: 备注信息

### 4. 智能计算功能
系统会根据以下公式自动计算下次需买药时间：
```
下次需买药时间 = 本次购药时间 + (购买盒数 × 每盒片数) ÷ 每日服用片数
```

### 5. 智能买药提醒功能
- **实时提醒**: 当药物即将用完时自动弹出提醒
- **分类提醒**: 按状态分类显示（已过期、今天、明天、即将过期）
- **滚动显示**: 支持大量条目的滚动查看，避免内容显示不全
- **内容复制**: 支持将提醒内容复制到剪贴板
- **防重复弹出**: 确保提醒窗口未关闭时不会重复弹出
- **自定义间隔**: 支持1-60分钟自定义提醒检查间隔时间
- **实时生效**: 设置修改后立即生效，无需重启程序
- **手动查看**: 提供"查看需要购买药物清单"按钮
- **后台运行**: 自动检查提醒，支持实时设置变化检测
- **优化体验**: 启动时只显示一次提醒，避免重复

### 6. 用户界面优化
- **隐藏ID列**: 界面更简洁，不显示技术性ID信息
- **按购药时间排序**: 默认按购药时间升序显示
- **下拉选择**: 数字字段使用下拉选择，提高输入效率
- **日期选择器**: 购药日期使用日期选择器，避免格式错误
- **响应式布局**: 界面自适应窗口大小
- **提醒窗口优化**: 使用默认位置显示，避免闪烁问题
- **设置界面**: 支持断药提前检测天数和自动提醒间隔时间设置

## 安装和运行

### 环境要求
- Python 3.6+
- tkinter (通常随Python一起安装)
- pandas
- tkcalendar
- sqlite3 (Python内置)

### 安装依赖
```bash
pip install pandas tkcalendar
```

### 运行应用
1. 首先导入Excel数据（可选）：
```bash
python3 import_excel_data.py
```

2. 启动主应用：
```bash
python3 medicine_manager.py
```

## 使用说明

### 添加药物
1. 在输入框中填写药物信息
   - 使用人：从下拉列表选择或直接输入
   - 品名及规格：输入药物名称和规格
   - 每日服用片数：从下拉列表选择（支持0.25, 0.5, 1-100）
   - 每盒片数：从下拉列表选择（1-100）
   - 购买盒数：从下拉列表选择（1-100）
   - 购药日期：使用日期选择器选择
   - 备注：可选填写
2. 点击"添加药物"按钮
3. 系统会自动计算下次需买药时间

### 编辑药物
1. **双击表格中的任意一行**（推荐方式）
2. 药物信息会自动加载到输入框中
3. 修改需要更新的信息
4. 点击"保存修改"按钮保存更改

### 删除药物
1. 在表格中选择要删除的药物
2. 点击"删除药物"按钮
3. 确认删除

### 搜索药物
在搜索框中输入药物名称、使用人或备注，系统会实时过滤显示匹配的记录。

### 查看购买清单
点击"查看需要购买药物清单"按钮，可以手动查看所有需要购买的药物，按状态分类显示。

### 买药提醒
- **自动提醒**: 系统会在后台自动检查，支持自定义检查间隔时间
- **智能分类**: 按状态分类显示提醒信息
- **滚动查看**: 当条目较多时支持滚动查看完整内容
- **内容复制**: 可以将提醒内容复制到剪贴板
- **防重复**: 确保提醒窗口未关闭时不会重复弹出
- **实时设置**: 设置修改后立即生效，无需重启程序
- **启动优化**: 程序启动时只显示一次提醒，避免重复

## 数据存储

- 使用SQLite数据库存储药物信息
- 数据库文件：`medicine.db`
- 支持数据的持久化存储
- 自动处理数据库结构升级

## 文件说明

- `medicine_manager.py`: 主应用程序
- `import_excel_data.py`: Excel数据导入脚本
- `read_excel.py`: Excel文件读取脚本
- `medicine.db`: SQLite数据库文件（运行后自动创建）
- `README.md`: 使用说明文档

## 技术特性

### 数据库设计
- 支持多用户药物管理
- 自动计算下次购买时间
- 数据完整性检查
- 重复药物名称检测

### 用户界面
- 现代化的Tkinter界面
- 响应式布局设计
- 直观的操作方式
- 友好的错误提示

### 提醒系统
- 多线程后台运行
- 智能提醒分类
- 滚动显示支持
- 内容复制功能
- 防重复弹出机制
- 自定义检查间隔时间
- 实时设置变化检测
- 避免重复提醒
- 实时状态更新

## 注意事项

1. **日期格式**: 使用日期选择器，自动格式化为 `YYYY-MM-DD`
2. **数字输入**: 使用下拉选择，确保输入有效性
3. **重复检测**: 系统会检测重复的药物名称，避免重复录入
4. **提醒功能**: 系统启动后会自动开始检查提醒，每5分钟检查一次
5. **数据备份**: 建议定期备份 `medicine.db` 文件
6. **使用人管理**: 支持预定义的家庭成员，也支持自定义输入

## 更新日志

### v2.2 (当前版本)
- ✅ 新增自动提醒间隔时间设置，支持1-60分钟自定义间隔
- ✅ 优化"提前提醒天数"更名为"断药提前检测天数"，更准确描述功能
- ✅ 实现设置实时生效功能，无需重启程序
- ✅ 修复SQLite跨线程问题，确保提醒线程正常工作
- ✅ 取消自动提醒间隔时间下拉框编辑功能，改为只读模式

### v2.1
- ✅ 增强提醒窗口功能，支持滚动显示和内容复制
- ✅ 优化提醒系统，防止重复弹出提醒窗口
- ✅ 简化提醒窗口显示，使用默认位置避免闪烁
- ✅ 改进用户体验，支持大量条目的完整显示

### v2.0
- ✅ 新增多用户药物管理功能
- ✅ 优化用户界面，隐藏ID列
- ✅ 改进提醒系统，避免重复提醒
- ✅ 添加每日服用片数的小数值支持（0.25, 0.5）
- ✅ 优化编辑功能，支持双击编辑
- ✅ 改进排序功能，默认按购药时间排序
- ✅ 增强搜索功能，支持按使用人搜索

### v1.0
- 基础药物管理功能
- 自动计算下次购买时间
- 基础提醒功能

## 许可证

本项目采用 GNU General Public License v3.0 (GPL-3.0) 许可证。

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

## 技术支持

如有问题或建议，请联系开发人员。 
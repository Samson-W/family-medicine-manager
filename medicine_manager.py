#!/usr/bin/env python3
"""
家庭慢性病患者药物管理系统
Family Chronic Disease Patient Medication Management System

作者: Baichua Wen
邮箱: sccxboy@gmail.com
许可证: GPL-3+
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import sqlite3
from datetime import datetime, timedelta
import threading
import time
from tkcalendar import DateEntry

class MedicineManager:
    def __init__(self, root):
        self.root = root
        self.root.title("家庭慢性病患者药物管理系统")
        self.root.geometry("1200x700")
        
        # 初始化数据库
        self.init_database()
        
        # 创建界面
        self.create_widgets()
        
        # 提醒窗口状态标志
        self.reminder_window_open = False
        
        # 加载保存的设置（在所有界面组件创建完成后）
        self.load_settings()
        
        # 启动提醒线程
        self.start_reminder_thread()
        
        # 加载数据
        self.load_data()
    
    def init_database(self):
        """初始化数据库"""
        import os
        # 获取用户主目录
        home_dir = os.path.expanduser("~")
        db_dir = os.path.join(home_dir, ".family-medicine-manager")
        
        # 创建配置目录
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # 数据库文件路径
        db_path = os.path.join(db_dir, "medicine.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # 创建药物信息表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_spec TEXT NOT NULL,
                user_name TEXT NOT NULL,
                daily_pills REAL NOT NULL,
                pills_per_box INTEGER NOT NULL,
                boxes_purchased INTEGER NOT NULL,
                purchase_date TEXT NOT NULL,
                next_purchase_date TEXT NOT NULL,
                notes TEXT
            )
        ''')
        
        # 创建设置表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_name TEXT UNIQUE NOT NULL,
                setting_value TEXT NOT NULL
            )
        ''')
        
        # 初始化默认设置
        self.cursor.execute('''
            INSERT OR IGNORE INTO settings (setting_name, setting_value) 
            VALUES ('reminder_days', '2')
        ''')
        
        self.cursor.execute('''
            INSERT OR IGNORE INTO settings (setting_name, setting_value) 
            VALUES ('reminder_interval', '5')
        ''')
        
        self.conn.commit()
        print("数据库初始化完成，默认设置已创建")
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="家庭慢性病患者药物管理系统", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text="药物信息录入", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 输入字段
        ttk.Label(input_frame, text="使用人:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.user_name_var = tk.StringVar()
        self.user_name_combo = ttk.Combobox(input_frame, textvariable=self.user_name_var, width=8,
                                           values=["爸爸", "妈妈", "爷爷", "奶奶", "外婆", "外爷", "儿子", "女儿"], 
                                           state="normal")
        self.user_name_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(input_frame, text="品名及规格:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.name_var, width=30).grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(input_frame, text="每日服用片数:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.daily_pills_var = tk.StringVar(value="1")
        # 添加0.25, 0.5和1-100的数值
        daily_pills_values = ["0.25", "0.5"] + [str(i) for i in range(1, 101)]
        self.daily_pills_combo = ttk.Combobox(input_frame, textvariable=self.daily_pills_var, width=8,
                                             values=daily_pills_values, state="readonly")
        self.daily_pills_combo.grid(row=0, column=5, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(input_frame, text="每盒片数:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.pills_per_box_var = tk.StringVar(value="1")
        self.pills_per_box_combo = ttk.Combobox(input_frame, textvariable=self.pills_per_box_var, width=8,
                                               values=[str(i) for i in range(1, 101)], state="readonly")
        self.pills_per_box_combo.grid(row=1, column=1, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(input_frame, text="购买盒数:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5))
        self.boxes_var = tk.StringVar(value="1")
        self.boxes_combo = ttk.Combobox(input_frame, textvariable=self.boxes_var, width=8,
                                       values=[str(i) for i in range(1, 101)], state="readonly")
        self.boxes_combo.grid(row=1, column=3, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(input_frame, text="购药日期:").grid(row=1, column=4, sticky=tk.W, padx=(0, 5))
        self.purchase_date_var = tk.StringVar()
        # 创建日期选择器
        self.date_picker = DateEntry(input_frame, width=15, background='darkblue',
                                   foreground='white', borderwidth=2, 
                                   date_pattern='yyyy-mm-dd',
                                   textvariable=self.purchase_date_var)
        self.date_picker.grid(row=1, column=5, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(input_frame, text="备注:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5))
        self.notes_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.notes_var, width=50).grid(row=2, column=1, columnspan=5, sticky=tk.W)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(button_frame, text="添加药物", command=self.add_medicine).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="保存修改", command=self.save_edit).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="删除药物", command=self.delete_medicine).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="清空输入", command=self.clear_inputs).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="查看需要购买药物清单", command=self.show_purchase_list).pack(side=tk.LEFT, padx=(0, 5))
        
        # 搜索和设置区域
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 搜索功能
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=(5, 10))
        
        # 提醒设置
        ttk.Label(search_frame, text="断药提前检测天数:").pack(side=tk.LEFT, padx=(20, 5))
        self.reminder_days_var = tk.StringVar()
        self.reminder_days_combo = ttk.Combobox(search_frame, textvariable=self.reminder_days_var, width=8,
                                               values=[str(i) for i in range(1, 15)], state="readonly")
        self.reminder_days_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # 自动提醒间隔时间设置
        ttk.Label(search_frame, text="自动提醒间隔时间:").pack(side=tk.LEFT, padx=(20, 5))
        self.reminder_interval_var = tk.StringVar()
        self.reminder_interval_combo = ttk.Combobox(search_frame, textvariable=self.reminder_interval_var, width=8,
                                                   values=[str(i) for i in range(1, 61)], state="readonly")
        self.reminder_interval_combo.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(search_frame, text="分钟").pack(side=tk.LEFT, padx=(0, 10))
        
        # 绑定设置变化事件
        self.reminder_days_trace_id = self.reminder_days_var.trace('w', self.on_setting_changed)
        self.reminder_interval_trace_id = self.reminder_interval_var.trace('w', self.on_setting_changed)
        
        # 也绑定Combobox的选择事件
        self.reminder_days_combo.bind('<<ComboboxSelected>>', self.on_setting_changed)
        self.reminder_interval_combo.bind('<<ComboboxSelected>>', self.on_setting_changed)
        
        # 数据表格
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建表格 - 隐藏ID列，按照数据库实际列顺序
        columns = ('id', 'name_spec', 'user_name', 'daily_pills', 'pills_per_box', 'boxes_purchased', 
                  'purchase_date', 'next_purchase_date', 'notes')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # 隐藏ID列
        self.tree.column('id', width=0, stretch=False)
        self.tree.heading('id', text='')
        
        # 设置列标题
        column_headers = {
            'id': 'ID',
            'name_spec': '品名及规格',
            'user_name': '使用人',
            'daily_pills': '每日服用片数',
            'pills_per_box': '每盒片数',
            'boxes_purchased': '购买盒数',
            'purchase_date': '购药日期',
            'next_purchase_date': '下次需买药时间',
            'notes': '备注'
        }
        
        for col in columns:
            if col != 'id':  # 跳过ID列，不设置标题和宽度
                self.tree.heading(col, text=column_headers[col])
                if col == 'name_spec':
                    self.tree.column(col, width=200)
                elif col == 'user_name':
                    self.tree.column(col, width=80)
                elif col == 'notes':
                    self.tree.column(col, width=150)
                else:
                    self.tree.column(col, width=120)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # 设置默认日期为当前日期
        current_date = datetime.now()
        self.date_picker.set_date(current_date)
    
    def load_settings(self):
        """加载设置"""
        try:
            # 暂时禁用设置变化事件，避免加载时触发保存
            self.reminder_days_var.trace_remove('write', self.reminder_days_trace_id)
            self.reminder_interval_var.trace_remove('write', self.reminder_interval_trace_id)
            
            # 加载断药提前检测天数
            self.cursor.execute('SELECT setting_value FROM settings WHERE setting_name = ?', ('reminder_days',))
            result = self.cursor.fetchone()
            if result:
                self.reminder_days_var.set(result[0])
                print(f"加载断药提前检测天数: {result[0]}天")
            else:
                self.reminder_days_var.set("2")
                print("使用默认断药提前检测天数: 2天")
            
            # 加载自动提醒间隔时间
            self.cursor.execute('SELECT setting_value FROM settings WHERE setting_name = ?', ('reminder_interval',))
            result = self.cursor.fetchone()
            if result:
                self.reminder_interval_var.set(result[0])
                print(f"加载自动提醒间隔时间: {result[0]}分钟")
            else:
                self.reminder_interval_var.set("5")
                print("使用默认自动提醒间隔时间: 5分钟")
                
            # 确保界面显示当前值
            days_value = self.reminder_days_var.get()
            interval_value = self.reminder_interval_var.get()
            print(f"设置界面显示: 断药提前检测天数={days_value}, 自动提醒间隔时间={interval_value}")
            self.reminder_days_combo.set(days_value)
            self.reminder_interval_combo.set(interval_value)
            
            # 验证界面显示
            print(f"验证界面显示: 断药提前检测天数={self.reminder_days_combo.get()}, 自动提醒间隔时间={self.reminder_interval_combo.get()}")
            
            # 重新启用设置变化事件
            self.reminder_days_trace_id = self.reminder_days_var.trace('w', self.on_setting_changed)
            self.reminder_interval_trace_id = self.reminder_interval_var.trace('w', self.on_setting_changed)
                
        except Exception as e:
            print(f"加载设置失败: {str(e)}")
            self.reminder_days_var.set("2")  # 默认值
            self.reminder_interval_var.set("5")  # 默认值
            print("设置加载失败，使用默认值")
            # 确保界面显示默认值
            self.reminder_days_combo.set("2")
            self.reminder_interval_combo.set("5")
            
            # 重新启用设置变化事件
            self.reminder_days_trace_id = self.reminder_days_var.trace('w', self.on_setting_changed)
            self.reminder_interval_trace_id = self.reminder_interval_var.trace('w', self.on_setting_changed)
    
    def save_settings(self):
        """保存设置"""
        try:
            reminder_days = self.reminder_days_var.get()
            reminder_interval = self.reminder_interval_var.get()
            
            print(f"正在保存设置: 断药提前检测天数={reminder_days}天, 自动提醒间隔时间={reminder_interval}分钟")
            
            # 检查值是否为空
            if not reminder_days or reminder_days.strip() == "":
                print("警告: 断药提前检测天数为空，使用默认值2")
                reminder_days = "2"
            
            if not reminder_interval or reminder_interval.strip() == "":
                print("警告: 自动提醒间隔时间为空，使用默认值5")
                reminder_interval = "5"
            
            # 保存断药提前检测天数
            self.cursor.execute('''
                INSERT OR REPLACE INTO settings (setting_name, setting_value) 
                VALUES (?, ?)
            ''', ('reminder_days', reminder_days))
            
            # 保存自动提醒间隔时间
            self.cursor.execute('''
                INSERT OR REPLACE INTO settings (setting_name, setting_value) 
                VALUES (?, ?)
            ''', ('reminder_interval', reminder_interval))
            
            self.conn.commit()
            print(f"设置已保存: 断药提前检测天数 = {reminder_days}天, 自动提醒间隔时间 = {reminder_interval}分钟")
            
            # 验证保存结果
            self.cursor.execute('SELECT setting_value FROM settings WHERE setting_name = ?', ('reminder_interval',))
            result = self.cursor.fetchone()
            if result:
                print(f"验证: 数据库中reminder_interval = {result[0]}")
            else:
                print("验证: 数据库中reminder_interval未找到")
        except Exception as e:
            print(f"保存设置失败: {str(e)}")
    
    def on_setting_changed(self, *args):
        """设置变化事件处理"""
        print("检测到设置变化，正在保存...")
        self.save_settings()
    
    def calculate_next_purchase_date(self, daily_pills, pills_per_box, boxes_purchased, purchase_date):
        """计算下次需买药时间"""
        try:
            total_pills = boxes_purchased * pills_per_box
            days_supply = total_pills / daily_pills
            purchase_dt = datetime.strptime(purchase_date, '%Y-%m-%d')
            next_date = purchase_dt + timedelta(days=days_supply)
            return next_date.strftime('%Y-%m-%d')
        except:
            return None
    
    def add_medicine(self):
        """添加药物"""
        # 检查是否在编辑模式
        if hasattr(self, 'editing_id'):
            messagebox.showwarning("警告", "当前正在编辑药物，请点击'保存修改'按钮或'清空输入'按钮")
            return
            
        try:
            name = self.name_var.get().strip()
            user_name = self.user_name_var.get().strip()
            daily_pills = float(self.daily_pills_var.get())
            pills_per_box = int(self.pills_per_box_var.get())
            boxes_purchased = int(self.boxes_var.get())
            purchase_date = self.purchase_date_var.get()
            notes = self.notes_var.get().strip()
            
            if not name or not user_name or daily_pills <= 0 or pills_per_box <= 0 or boxes_purchased <= 0:
                messagebox.showerror("错误", "请填写完整的药物信息")
                return
            
            # 检查品名及规格是否已存在
            self.cursor.execute('SELECT id FROM medicines WHERE name_spec = ?', (name,))
            existing_medicine = self.cursor.fetchone()
            
            if existing_medicine:
                messagebox.showerror("错误", f"品名及规格 '{name}' 已存在，请使用不同的名称或修改现有记录")
                return
            
            # 计算下次需买药时间
            next_purchase_date = self.calculate_next_purchase_date(
                daily_pills, pills_per_box, boxes_purchased, purchase_date
            )
            
            if not next_purchase_date:
                messagebox.showerror("错误", "日期格式错误")
                return
            
            # 插入数据库 - 按照实际数据库列顺序
            self.cursor.execute('''
                INSERT INTO medicines (name_spec, daily_pills, pills_per_box, boxes_purchased, 
                                     purchase_date, next_purchase_date, notes, user_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, daily_pills, pills_per_box, boxes_purchased, 
                  purchase_date, next_purchase_date, notes, user_name))
            self.conn.commit()
            
            messagebox.showinfo("成功", "药物信息添加成功")
            self.clear_inputs()
            self.load_data()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
        except Exception as e:
            messagebox.showerror("错误", f"添加失败: {str(e)}")
    
    def edit_medicine(self):
        """修改药物信息"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要修改的药物")
            return
        
        item = self.tree.item(selected[0])
        medicine_id = item['values'][0]
        
        # 获取当前选中的药物信息
        self.cursor.execute('SELECT * FROM medicines WHERE id = ?', (medicine_id,))
        medicine = self.cursor.fetchone()
        
        if not medicine:
            messagebox.showerror("错误", "药物信息不存在")
            return
        
        # 填充输入框 - 根据实际数据库列顺序调整索引
        # 实际数据库列顺序: id, name_spec, user_name, daily_pills, pills_per_box, boxes_purchased, purchase_date, next_purchase_date, notes
        self.name_var.set(medicine[1])  # name_spec
        self.user_name_var.set(medicine[2])  # user_name
        self.daily_pills_var.set(str(medicine[3]))  # daily_pills
        self.pills_per_box_var.set(str(medicine[4]))  # pills_per_box
        self.boxes_var.set(str(medicine[5]))  # boxes_purchased
        # 设置日期选择器
        try:
            purchase_date = datetime.strptime(medicine[6], '%Y-%m-%d')  # purchase_date
            self.date_picker.set_date(purchase_date)
        except:
            # 如果日期格式有问题，设置为当前日期
            self.date_picker.set_date(datetime.now())
        self.notes_var.set(medicine[8] or "")  # notes
        
        # 保存当前编辑的药物ID
        self.editing_id = medicine_id
        
        messagebox.showinfo("提示", "药物信息已加载到输入框，请修改后点击'保存修改'按钮")
    
    def save_edit(self):
        """保存修改的药物信息"""
        if not hasattr(self, 'editing_id'):
            messagebox.showwarning("警告", "没有正在编辑的药物")
            return
        
        try:
            # 保存editing_id到局部变量，避免在异常处理中丢失
            editing_id = self.editing_id
            
            name = self.name_var.get().strip()
            user_name = self.user_name_var.get().strip()
            daily_pills = float(self.daily_pills_var.get())
            pills_per_box = int(self.pills_per_box_var.get())
            boxes_purchased = int(self.boxes_var.get())
            purchase_date = self.purchase_date_var.get()
            notes = self.notes_var.get().strip()
            
            if not name or not user_name or daily_pills <= 0 or pills_per_box <= 0 or boxes_purchased <= 0:
                messagebox.showerror("错误", "请填写完整的药物信息")
                return
            
            # 检查品名及规格是否与其他记录重复（排除当前编辑的记录）
            self.cursor.execute('SELECT id FROM medicines WHERE name_spec = ? AND id != ?', (name, editing_id))
            existing_medicine = self.cursor.fetchone()
            
            if existing_medicine:
                messagebox.showerror("错误", f"品名及规格 '{name}' 已存在，请使用不同的名称")
                return
            
            # 计算下次需买药时间
            next_purchase_date = self.calculate_next_purchase_date(
                daily_pills, pills_per_box, boxes_purchased, purchase_date
            )
            
            if not next_purchase_date:
                messagebox.showerror("错误", "日期格式错误")
                return
            
            # 更新数据库 - 按照实际数据库列顺序
            self.cursor.execute('''
                UPDATE medicines 
                SET name_spec=?, daily_pills=?, pills_per_box=?, boxes_purchased=?, 
                    purchase_date=?, next_purchase_date=?, notes=?, user_name=?
                WHERE id=?
            ''', (name, daily_pills, pills_per_box, boxes_purchased, 
                  purchase_date, next_purchase_date, notes, user_name, editing_id))
            self.conn.commit()
            
            messagebox.showinfo("成功", "药物信息修改成功")
            self.load_data()
            self.clear_inputs()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
        except Exception as e:
            messagebox.showerror("错误", f"修改失败: {str(e)}")
            # 确保在异常情况下也清除编辑状态
            if hasattr(self, 'editing_id'):
                delattr(self, 'editing_id')
    
    def delete_medicine(self):
        """删除药物"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的药物")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的药物吗？"):
            for item in selected:
                medicine_id = self.tree.item(item)['values'][0]
                self.cursor.execute('DELETE FROM medicines WHERE id = ?', (medicine_id,))
            
            self.conn.commit()
            messagebox.showinfo("成功", "药物信息删除成功")
            self.load_data()
    
    def clear_inputs(self):
        """清空输入框"""
        self.name_var.set("")
        self.user_name_var.set("")
        self.daily_pills_var.set("1")
        self.pills_per_box_var.set("1")
        self.boxes_var.set("1")
        # 重置日期选择器为当前日期
        current_date = datetime.now()
        self.date_picker.set_date(current_date)
        self.notes_var.set("")
        
        # 清除编辑状态
        if hasattr(self, 'editing_id'):
            delattr(self, 'editing_id')
    
    def load_data(self):
        """加载数据到表格"""
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 查询数据 - 按购药时间升序排序
        self.cursor.execute('SELECT * FROM medicines ORDER BY purchase_date')
        medicines = self.cursor.fetchall()
        
        # 插入数据
        for medicine in medicines:
            self.tree.insert('', 'end', values=medicine)
    
    def on_search(self, *args):
        """搜索功能"""
        search_term = self.search_var.get().strip()
        
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if search_term:
            # 搜索数据
            self.cursor.execute('''
                SELECT * FROM medicines 
                WHERE name_spec LIKE ? OR user_name LIKE ? OR notes LIKE ?
                ORDER BY purchase_date
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        else:
            # 显示所有数据
            self.cursor.execute('SELECT * FROM medicines ORDER BY purchase_date')
        
        medicines = self.cursor.fetchall()
        
        # 插入数据
        for medicine in medicines:
            self.tree.insert('', 'end', values=medicine)
    
    def on_double_click(self, event):
        """双击编辑"""
        self.edit_medicine()
    
    def show_purchase_list(self):
        """显示需要购买药物清单"""
        today = datetime.now()
        
        # 获取用户设置的断药提前检测天数
        try:
            reminder_days = int(self.reminder_days_var.get())
        except:
            reminder_days = 2  # 默认值
        
        # 计算提醒日期（当前日期 + 提前天数）
        reminder_date = today + timedelta(days=reminder_days)
        
        # 查询所有过期和即将过期的药物（包括已过期的）
        self.cursor.execute('''
            SELECT name_spec, user_name, next_purchase_date, notes
            FROM medicines 
            WHERE next_purchase_date <= ?
            ORDER BY next_purchase_date
        ''', (reminder_date.strftime('%Y-%m-%d'),))
        
        medicines = self.cursor.fetchall()
        
        if medicines:
            # 创建详细清单文本
            list_text = "=== 需要购买药物清单 ===\n\n"
            list_text += f"检查时间: {today.strftime('%Y-%m-%d %H:%M:%S')}\n"
            list_text += f"断药提前检测天数: {reminder_days}天\n"
            list_text += f"需要购买的药物数量: {len(medicines)}\n\n"
            
            # 按状态分类
            expired_medicines = []
            today_medicines = []
            tomorrow_medicines = []
            other_medicines = []
            
            for medicine in medicines:
                name = medicine[0]  # name_spec
                user_name = medicine[1]  # user_name (在查询结果中的位置)
                next_date = medicine[2]  # next_purchase_date
                notes = medicine[3] or ""  # notes
                
                next_dt = datetime.strptime(next_date, '%Y-%m-%d')
                days_left = (next_dt - today).days
                
                if days_left < 0:
                    expired_medicines.append((name, user_name, next_date, days_left, notes))
                elif days_left == 0:
                    today_medicines.append((name, user_name, next_date, days_left, notes))
                elif days_left == 1:
                    tomorrow_medicines.append((name, user_name, next_date, days_left, notes))
                else:
                    other_medicines.append((name, user_name, next_date, days_left, notes))
            
            # 显示已过期的药物
            if expired_medicines:
                list_text += "🚨 已过期的药物:\n"
                for name, user_name, next_date, days_left, notes in expired_medicines:
                    list_text += f"   • {name} (使用人: {user_name})\n"
                    list_text += f"     断药时间: {next_date} (已过期{abs(days_left)}天)\n"
                    if notes:
                        list_text += f"     备注: {notes}\n"
                    list_text += "\n"
            
            # 显示今天需要购买的药物
            if today_medicines:
                list_text += "⚠️ 今天需要购买的药物:\n"
                for name, user_name, next_date, days_left, notes in today_medicines:
                    list_text += f"   • {name} (使用人: {user_name})\n"
                    list_text += f"     断药时间: {next_date}\n"
                    if notes:
                        list_text += f"     备注: {notes}\n"
                    list_text += "\n"
            
            # 显示明天需要购买的药物
            if tomorrow_medicines:
                list_text += "📅 明天需要购买的药物:\n"
                for name, user_name, next_date, days_left, notes in tomorrow_medicines:
                    list_text += f"   • {name} (使用人: {user_name})\n"
                    list_text += f"     断药时间: {next_date}\n"
                    if notes:
                        list_text += f"     备注: {notes}\n"
                    list_text += "\n"
            
            # 显示其他即将用完的药物
            if other_medicines:
                list_text += "📋 即将用完的药物:\n"
                for name, user_name, next_date, days_left, notes in other_medicines:
                    list_text += f"   • {name} (使用人: {user_name})\n"
                    list_text += f"     断药时间: {next_date} (还有{days_left}天)\n"
                    if notes:
                        list_text += f"     备注: {notes}\n"
                    list_text += "\n"
            
            # 显示滚动提醒窗口
            self.show_scrolled_reminder("需要购买药物清单", list_text)
        else:
            messagebox.showinfo("药物清单", "当前没有需要购买的药物！\n\n所有药物的购买时间都在未来。")
    
    def check_reminders(self):
        """检查提醒"""
        today = datetime.now()
        
        # 获取用户设置的断药提前检测天数
        try:
            reminder_days = int(self.reminder_days_var.get())
        except:
            reminder_days = 2  # 默认值
        
        # 计算提醒日期（当前日期 + 提前天数）
        reminder_date = today + timedelta(days=reminder_days)
        
        # 查询所有过期和即将过期的药物（包括已过期的）
        self.cursor.execute('''
            SELECT name_spec, user_name, next_purchase_date 
            FROM medicines 
            WHERE next_purchase_date <= ?
            ORDER BY next_purchase_date
        ''', (reminder_date.strftime('%Y-%m-%d'),))
        
        medicines = self.cursor.fetchall()
        
        print(f"提醒检查: 找到 {len(medicines)} 种需要提醒的药物")
        
        if medicines:
            reminder_text = "以下药物需要购买：\n\n"
            for medicine in medicines:
                name = medicine[0]  # name_spec
                user_name = medicine[1]  # user_name (在查询结果中的位置)
                next_date = medicine[2]  # next_purchase_date
                
                # 计算距离下次购买的天数
                next_dt = datetime.strptime(next_date, '%Y-%m-%d')
                days_left = (next_dt - today).days
                
                if days_left < 0:
                    status = f"已过期{days_left}天"
                elif days_left == 0:
                    status = "今天需要购买"
                elif days_left == 1:
                    status = "明天需要购买"
                else:
                    status = f"还有{days_left}天"
                
                reminder_text += f"• {name} (使用人: {user_name})\n"
                reminder_text += f"  断药时间: {next_date} ({status})\n\n"
            
            print("显示提醒弹窗...")
            # 在主线程中显示滚动提醒
            self.root.after(0, lambda: self.show_scrolled_reminder("买药提醒", reminder_text))
    
    def show_scrolled_reminder(self, title, content):
        """显示带滚动条的提醒窗口"""
        # 检查是否已有提醒窗口打开
        if self.reminder_window_open:
            print("提醒窗口已打开，跳过重复提醒")
            return
        
        # 设置提醒窗口状态为打开
        self.reminder_window_open = True
        
        # 创建新窗口
        reminder_window = tk.Toplevel(self.root)
        reminder_window.title(title)
        reminder_window.geometry("600x400")
        reminder_window.resizable(True, True)
        
        # 设置窗口模态
        reminder_window.transient(self.root)
        reminder_window.grab_set()
        

        
        # 创建主框架
        main_frame = ttk.Frame(reminder_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建滚动文本框
        text_widget = scrolledtext.ScrolledText(
            main_frame, 
            wrap=tk.WORD, 
            width=70, 
            height=20,
            font=("Arial", 10)
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=(0, 0), pady=(0, 10))
        
        # 插入内容
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)  # 设置为只读
        
        # 创建按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 窗口关闭回调函数
        def on_window_close():
            self.reminder_window_open = False
            reminder_window.destroy()
        
        # 确定按钮
        ok_button = ttk.Button(button_frame, text="确定", command=on_window_close)
        ok_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 复制按钮
        copy_button = ttk.Button(button_frame, text="复制内容", 
                                command=lambda: self.copy_to_clipboard(content))
        copy_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 设置焦点到确定按钮
        ok_button.focus_set()
        
        # 绑定回车键关闭窗口
        reminder_window.bind('<Return>', lambda e: on_window_close())
        reminder_window.bind('<Escape>', lambda e: on_window_close())
        
        # 绑定窗口关闭协议
        reminder_window.protocol("WM_DELETE_WINDOW", on_window_close)
        
        # 等待窗口关闭
        reminder_window.wait_window()
    
    def copy_to_clipboard(self, text):
        """复制文本到剪贴板"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("提示", "内容已复制到剪贴板！")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {str(e)}")
    
    def get_reminder_interval(self):
        """获取提醒间隔时间（在主线程中调用）"""
        try:
            self.cursor.execute('SELECT setting_value FROM settings WHERE setting_name = ?', ('reminder_interval',))
            result = self.cursor.fetchone()
            if result:
                return int(result[0])
            else:
                return 5  # 默认5分钟
        except Exception as e:
            print(f"获取提醒间隔时间出错: {str(e)}")
            return 5  # 默认5分钟
    
    def start_reminder_thread(self):
        """启动提醒线程"""
        def reminder_loop():
            # 在提醒线程中创建新的数据库连接
            import os
            home_dir = os.path.expanduser("~")
            db_dir = os.path.join(home_dir, ".family-medicine-manager")
            db_path = os.path.join(db_dir, "medicine.db")
            
            try:
                thread_conn = sqlite3.connect(db_path)
                thread_cursor = thread_conn.cursor()
            except Exception as e:
                print(f"提醒线程创建数据库连接失败: {str(e)}")
                thread_conn = None
                thread_cursor = None
            
            # 启动时立即检查一次
            self.root.after(0, self.check_reminders)
            
            # 获取初始间隔时间
            interval_minutes = 5  # 默认值
            if thread_cursor:
                try:
                    thread_cursor.execute('SELECT setting_value FROM settings WHERE setting_name = ?', ('reminder_interval',))
                    result = thread_cursor.fetchone()
                    if result:
                        interval_minutes = int(result[0])
                        print(f"提醒线程: 当前间隔时间设置为 {interval_minutes}分钟")
                    else:
                        print(f"提醒线程: 数据库中未找到reminder_interval设置，使用默认间隔时间 {interval_minutes}分钟")
                except Exception as e:
                    print(f"提醒线程: 读取设置时出错 {str(e)}，使用默认间隔时间 {interval_minutes}分钟")
            
            while True:
                try:
                    interval_seconds = interval_minutes * 60
                    
                    # 分段睡眠，每10秒检查一次设置是否变化
                    sleep_chunks = interval_seconds // 10
                    for _ in range(sleep_chunks):
                        time.sleep(10)
                        # 检查设置是否发生变化
                        if thread_cursor:
                            try:
                                thread_cursor.execute('SELECT setting_value FROM settings WHERE setting_name = ?', ('reminder_interval',))
                                result = thread_cursor.fetchone()
                                new_interval_minutes = int(result[0]) if result else 5
                                if new_interval_minutes != interval_minutes:
                                    print(f"检测到提醒间隔设置变化: {interval_minutes}分钟 -> {new_interval_minutes}分钟")
                                    interval_minutes = new_interval_minutes  # 更新当前间隔时间
                                    print(f"提醒线程: 更新间隔时间设置为 {interval_minutes}分钟")
                                    break  # 跳出循环，重新开始
                            except Exception as e:
                                print(f"提醒线程: 检查设置变化时出错 {str(e)}")
                    
                    # 在主线程中执行提醒检查
                    self.root.after(0, self.check_reminders)
                except Exception as e:
                    print(f"提醒检查出错: {str(e)}")
                    time.sleep(60)  # 出错时等待1分钟再试
            
            # 关闭线程数据库连接
            if thread_conn:
                thread_conn.close()
        
        reminder_thread = threading.Thread(target=reminder_loop, daemon=True)
        reminder_thread.start()
        print("提醒线程已启动")
    
    def __del__(self):
        """析构函数，关闭数据库连接"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    root = tk.Tk()
    app = MedicineManager(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
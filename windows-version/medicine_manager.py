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
        self.root.geometry("1400x800")
        
        # 设置窗口图标（如果有的话）
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # 设置现代化主题
        self.setup_modern_theme()
        
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
    
    def setup_modern_theme(self):
        """设置现代化主题"""
        # 定义颜色主题
        self.colors = {
            'primary': '#2196F3',      # 主色调 - 蓝色
            'secondary': '#FF9800',    # 次要色调 - 橙色
            'success': '#4CAF50',      # 成功色 - 绿色
            'warning': '#FFC107',      # 警告色 - 黄色
            'danger': '#F44336',       # 危险色 - 红色
            'light': '#F5F5F5',        # 浅色背景
            'dark': '#212121',         # 深色文字
            'white': '#FFFFFF',        # 白色
            'border': '#E0E0E0'        # 边框色
        }
        
        # 配置ttk样式
        style = ttk.Style()
        
        # 配置主题
        style.theme_use('clam')
        
        # 配置主框架样式
        style.configure('Main.TFrame', background=self.colors['light'])
        
        # 配置标题样式
        style.configure('Title.TLabel', 
                       font=('Microsoft YaHei UI', 18, 'bold'),
                       foreground=self.colors['primary'],
                       background=self.colors['light'])
        
        # 配置输入框样式
        style.configure('Input.TFrame', 
                       background=self.colors['white'],
                       relief='solid',
                       borderwidth=1)
        
        # 配置按钮样式
        style.configure('Primary.TButton',
                       font=('Microsoft YaHei UI', 10),
                       background=self.colors['primary'],
                       foreground=self.colors['white'],
                       padding=(10, 5))
        
        style.configure('Success.TButton',
                       font=('Microsoft YaHei UI', 10),
                       background=self.colors['success'],
                       foreground=self.colors['white'],
                       padding=(10, 5))
        
        style.configure('Warning.TButton',
                       font=('Microsoft YaHei UI', 10),
                       background=self.colors['warning'],
                       foreground=self.colors['dark'],
                       padding=(10, 5))
        
        style.configure('Danger.TButton',
                       font=('Microsoft YaHei UI', 10),
                       background=self.colors['danger'],
                       foreground=self.colors['white'],
                       padding=(10, 5))
        
        # 配置标签框样式
        style.configure('Card.TLabelframe',
                       background=self.colors['white'],
                       relief='solid',
                       borderwidth=1)
        
        style.configure('Card.TLabelframe.Label',
                       font=('Microsoft YaHei UI', 11, 'bold'),
                       foreground=self.colors['primary'],
                       background=self.colors['white'])
        
        # 配置表格样式
        style.configure('Treeview',
                       font=('Microsoft YaHei UI', 9),
                       rowheight=25,
                       background=self.colors['white'],
                       fieldbackground=self.colors['white'])
        
        style.configure('Treeview.Heading',
                       font=('Microsoft YaHei UI', 9, 'bold'),
                       background=self.colors['primary'],
                       foreground=self.colors['white'])
        
        # 设置根窗口背景色
        self.root.configure(bg=self.colors['light'])
        
        style.configure('Card.TLabelframe.Label',
                       font=('Microsoft YaHei UI', 11, 'bold'),
                       foreground=self.colors['primary'],
                       background=self.colors['white'])
        
        # 配置表格样式
        style.configure('Treeview',
                       font=('Microsoft YaHei UI', 9),
                       rowheight=25,
                       background=self.colors['white'],
                       fieldbackground=self.colors['white'])
        
        style.configure('Treeview.Heading',
                       font=('Microsoft YaHei UI', 9, 'bold'),
                       background=self.colors['primary'],
                       foreground=self.colors['white'])
        
        # 设置根窗口背景色
        self.root.configure(bg=self.colors['light'])
    
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
        main_frame = ttk.Frame(self.root, style='Main.TFrame', padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 标题区域
        title_frame = ttk.Frame(main_frame, style='Main.TFrame')
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 标题图标和文字
        title_label = ttk.Label(title_frame, text="💊 家庭慢性病患者药物管理系统", style='Title.TLabel')
        title_label.pack()
        
        # 副标题
        subtitle_label = ttk.Label(title_frame, text="智能管理药物，及时提醒购买", 
                                 font=('Microsoft YaHei UI', 10),
                                 foreground=self.colors['secondary'],
                                 background=self.colors['light'])
        subtitle_label.pack(pady=(5, 0))
        
        # 输入区域 - 使用卡片样式
        input_frame = ttk.LabelFrame(main_frame, text="📝 药物信息录入", style='Card.TLabelframe', padding="15")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 第一行输入字段
        row1_frame = ttk.Frame(input_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 使用人
        user_frame = ttk.Frame(row1_frame)
        user_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(user_frame, text="👤 使用人:", font=('Microsoft YaHei UI', 9)).pack(anchor=tk.W)
        self.user_name_var = tk.StringVar()
        self.user_name_combo = ttk.Combobox(user_frame, textvariable=self.user_name_var, width=10,
                                           values=["爸爸", "妈妈", "爷爷", "奶奶", "外婆", "外爷", "儿子", "女儿"], 
                                           state="normal", font=('Microsoft YaHei UI', 9))
        self.user_name_combo.pack(pady=(5, 0))
        
        # 品名及规格
        name_frame = ttk.Frame(row1_frame)
        name_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(name_frame, text="💊 品名及规格:", font=('Microsoft YaHei UI', 9)).pack(anchor=tk.W)
        self.name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_var, width=35, font=('Microsoft YaHei UI', 9)).pack(pady=(5, 0))
        
        # 每日服用片数
        daily_frame = ttk.Frame(row1_frame)
        daily_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(daily_frame, text="📅 每日服用片数:", font=('Microsoft YaHei UI', 9)).pack(anchor=tk.W)
        self.daily_pills_var = tk.StringVar(value="1")
        daily_pills_values = ["0.25", "0.5"] + [str(i) for i in range(1, 101)]
        self.daily_pills_combo = ttk.Combobox(daily_frame, textvariable=self.daily_pills_var, width=8,
                                             values=daily_pills_values, state="readonly", font=('Microsoft YaHei UI', 9))
        self.daily_pills_combo.pack(pady=(5, 0))
        
        # 第二行输入字段
        row2_frame = ttk.Frame(input_frame)
        row2_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 每盒片数
        pills_frame = ttk.Frame(row2_frame)
        pills_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(pills_frame, text="📦 每盒片数:", font=('Microsoft YaHei UI', 9)).pack(anchor=tk.W)
        self.pills_per_box_var = tk.StringVar(value="1")
        self.pills_per_box_combo = ttk.Combobox(pills_frame, textvariable=self.pills_per_box_var, width=8,
                                               values=[str(i) for i in range(1, 101)], state="readonly", font=('Microsoft YaHei UI', 9))
        self.pills_per_box_combo.pack(pady=(5, 0))
        
        # 购买盒数
        boxes_frame = ttk.Frame(row2_frame)
        boxes_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(boxes_frame, text="🛒 购买盒数:", font=('Microsoft YaHei UI', 9)).pack(anchor=tk.W)
        self.boxes_var = tk.StringVar(value="1")
        self.boxes_combo = ttk.Combobox(boxes_frame, textvariable=self.boxes_var, width=8,
                                       values=[str(i) for i in range(1, 101)], state="readonly", font=('Microsoft YaHei UI', 9))
        self.boxes_combo.pack(pady=(5, 0))
        
        # 购药日期
        date_frame = ttk.Frame(row2_frame)
        date_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(date_frame, text="📅 购药日期:", font=('Microsoft YaHei UI', 9)).pack(anchor=tk.W)
        self.purchase_date_var = tk.StringVar()
        self.date_picker = DateEntry(date_frame, width=15, background=self.colors['primary'],
                                   foreground=self.colors['white'], borderwidth=2, 
                                   date_pattern='yyyy-mm-dd',
                                   textvariable=self.purchase_date_var,
                                   font=('Microsoft YaHei UI', 9))
        self.date_picker.pack(pady=(5, 0))
        
        # 第三行 - 备注
        row3_frame = ttk.Frame(input_frame)
        row3_frame.pack(fill=tk.X)
        
        notes_frame = ttk.Frame(row3_frame)
        notes_frame.pack(fill=tk.X)
        ttk.Label(notes_frame, text="📝 备注:", font=('Microsoft YaHei UI', 9)).pack(anchor=tk.W)
        self.notes_var = tk.StringVar()
        ttk.Entry(notes_frame, textvariable=self.notes_var, width=80, font=('Microsoft YaHei UI', 9)).pack(pady=(5, 0), fill=tk.X)
        
        # 按钮区域 - 使用现代化按钮
        button_frame = ttk.Frame(main_frame, style='Main.TFrame')
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 15))
        
        # 按钮容器
        btn_container = ttk.Frame(button_frame)
        btn_container.pack()
        
        ttk.Button(btn_container, text="➕ 添加药物", style='Success.TButton', command=self.add_medicine).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_container, text="💾 保存修改", style='Primary.TButton', command=self.save_edit).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_container, text="🗑️ 删除药物", style='Danger.TButton', command=self.delete_medicine).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_container, text="🔄 清空输入", style='Warning.TButton', command=self.clear_inputs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_container, text="📋 查看购买清单", style='Primary.TButton', command=self.show_purchase_list).pack(side=tk.LEFT, padx=(0, 10))
        
        # 搜索和设置区域 - 使用卡片样式
        control_frame = ttk.LabelFrame(main_frame, text="⚙️ 搜索与设置", style='Card.TLabelframe', padding="10")
        control_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 搜索功能
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(side=tk.LEFT, padx=(0, 30))
        
        ttk.Label(search_frame, text="🔍 搜索:", font=('Microsoft YaHei UI', 9)).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)
        ttk.Entry(search_frame, textvariable=self.search_var, width=25, font=('Microsoft YaHei UI', 9)).pack(side=tk.LEFT, padx=(5, 0))
        
        # 提醒设置
        reminder_frame = ttk.Frame(control_frame)
        reminder_frame.pack(side=tk.LEFT, padx=(0, 30))
        
        ttk.Label(reminder_frame, text="⏰ 断药提前检测天数:", font=('Microsoft YaHei UI', 9)).pack(side=tk.LEFT)
        self.reminder_days_var = tk.StringVar()
        self.reminder_days_combo = ttk.Combobox(reminder_frame, textvariable=self.reminder_days_var, width=6,
                                               values=[str(i) for i in range(1, 15)], state="readonly", font=('Microsoft YaHei UI', 9))
        self.reminder_days_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # 自动提醒间隔时间设置
        interval_frame = ttk.Frame(control_frame)
        interval_frame.pack(side=tk.LEFT)
        
        ttk.Label(interval_frame, text="⏱️ 自动提醒间隔:", font=('Microsoft YaHei UI', 9)).pack(side=tk.LEFT)
        self.reminder_interval_var = tk.StringVar()
        self.reminder_interval_combo = ttk.Combobox(interval_frame, textvariable=self.reminder_interval_var, width=6,
                                                   values=[str(i) for i in range(1, 61)], state="readonly", font=('Microsoft YaHei UI', 9))
        self.reminder_interval_combo.pack(side=tk.LEFT, padx=(5, 5))
        ttk.Label(interval_frame, text="分钟", font=('Microsoft YaHei UI', 9)).pack(side=tk.LEFT)
        
        # 绑定设置变化事件
        self.reminder_days_trace_id = self.reminder_days_var.trace('w', self.on_setting_changed)
        self.reminder_interval_trace_id = self.reminder_interval_var.trace('w', self.on_setting_changed)
        
        # 也绑定Combobox的选择事件
        self.reminder_days_combo.bind('<<ComboboxSelected>>', self.on_setting_changed)
        self.reminder_interval_combo.bind('<<ComboboxSelected>>', self.on_setting_changed)
        
        # 数据表格区域 - 使用卡片样式
        table_frame = ttk.LabelFrame(main_frame, text="📊 药物数据列表", style='Card.TLabelframe', padding="10")
        table_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建表格容器
        tree_container = ttk.Frame(table_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建表格 - 隐藏ID列，按照数据库实际列顺序
        columns = ('id', 'name_spec', 'user_name', 'daily_pills', 'pills_per_box', 'boxes_purchased', 
                  'purchase_date', 'next_purchase_date', 'notes')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=12)
        
        # 隐藏ID列
        self.tree.column('id', width=0, stretch=False)
        self.tree.heading('id', text='')
        
        # 设置列标题
        column_headers = {
            'id': 'ID',
            'name_spec': '💊 品名及规格',
            'user_name': '👤 使用人',
            'daily_pills': '📅 每日服用片数',
            'pills_per_box': '📦 每盒片数',
            'boxes_purchased': '🛒 购买盒数',
            'purchase_date': '📅 购药日期',
            'next_purchase_date': '⏰ 下次需买药时间',
            'notes': '📝 备注'
        }
        
        for col in columns:
            if col != 'id':  # 跳过ID列，不设置标题和宽度
                self.tree.heading(col, text=column_headers[col])
                if col == 'name_spec':
                    self.tree.column(col, width=250)
                elif col == 'user_name':
                    self.tree.column(col, width=80)
                elif col == 'notes':
                    self.tree.column(col, width=200)
                else:
                    self.tree.column(col, width=120)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # 设置默认日期为当前日期
        current_date = datetime.now()
        self.date_picker.set_date(current_date)
        
        # 添加状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪 - 系统已启动，等待操作...")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              font=('Microsoft YaHei UI', 8),
                              foreground=self.colors['secondary'],
                              background=self.colors['light'])
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
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
            self.status_var.set("⚠️ 当前正在编辑药物，请点击'保存修改'按钮或'清空输入'按钮")
            self.show_error_message("编辑模式", "当前正在编辑药物，请点击'保存修改'按钮或'清空输入'按钮")
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
                self.status_var.set("❌ 请填写完整的药物信息")
                self.show_error_message("输入错误", "请填写完整的药物信息")
                return
            
            # 检查品名及规格是否已存在
            self.cursor.execute('SELECT id FROM medicines WHERE name_spec = ?', (name,))
            existing_medicine = self.cursor.fetchone()
            
            if existing_medicine:
                self.status_var.set(f"❌ 品名及规格 '{name}' 已存在")
                self.show_error_message("重复记录", f"品名及规格 '{name}' 已存在，请使用不同的名称或修改现有记录")
                return
            
            # 计算下次需买药时间
            next_purchase_date = self.calculate_next_purchase_date(
                daily_pills, pills_per_box, boxes_purchased, purchase_date
            )
            
            if not next_purchase_date:
                self.status_var.set("❌ 日期格式错误")
                self.show_error_message("日期错误", "日期格式错误")
                return
            
            # 插入数据库 - 按照实际数据库列顺序
            self.cursor.execute('''
                INSERT INTO medicines (name_spec, daily_pills, pills_per_box, boxes_purchased, 
                                     purchase_date, next_purchase_date, notes, user_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, daily_pills, pills_per_box, boxes_purchased, 
                  purchase_date, next_purchase_date, notes, user_name))
            self.conn.commit()
            
            self.status_var.set("✅ 药物信息添加成功")
            self.show_info_message("添加成功", "药物信息添加成功")
            self.clear_inputs()
            self.load_data()
            
        except ValueError:
            self.status_var.set("❌ 请输入有效的数字")
            self.show_error_message("输入错误", "请输入有效的数字")
        except Exception as e:
            self.status_var.set(f"❌ 添加失败: {str(e)}")
            self.show_error_message("添加失败", f"添加失败: {str(e)}")
    
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
            # 创建美化版的无药物提示窗口
            no_medicines_window = tk.Toplevel(self.root)
            no_medicines_window.title("✅ 药物清单检查")
            no_medicines_window.geometry("500x300")
            no_medicines_window.resizable(False, False)
            no_medicines_window.configure(bg=self.colors['light'])
            
            # 设置窗口模态
            no_medicines_window.transient(self.root)
            no_medicines_window.grab_set()
            
            # 创建主框架
            main_frame = ttk.Frame(no_medicines_window, style='Main.TFrame', padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 图标和标题
            icon_label = ttk.Label(main_frame, text="✅", 
                                 font=('Microsoft YaHei UI', 48),
                                 foreground=self.colors['success'],
                                 background=self.colors['light'])
            icon_label.pack(pady=(20, 10))
            
            title_label = ttk.Label(main_frame, text="药物清单检查完成", 
                                  font=('Microsoft YaHei UI', 16, 'bold'),
                                  foreground=self.colors['primary'],
                                  background=self.colors['light'])
            title_label.pack(pady=(0, 10))
            
            message_label = ttk.Label(main_frame, text="当前没有需要购买的药物！\n\n所有药物的购买时间都在未来。", 
                                    font=('Microsoft YaHei UI', 11),
                                    foreground=self.colors['dark'],
                                    background=self.colors['light'],
                                    justify=tk.CENTER)
            message_label.pack(pady=(0, 20))
            
            # 确定按钮
            ok_button = ttk.Button(main_frame, text="✅ 确定", 
                                 style='Success.TButton',
                                 command=no_medicines_window.destroy)
            ok_button.pack()
            
            # 设置焦点
            ok_button.focus_set()
            
            # 绑定回车键
            no_medicines_window.bind('<Return>', lambda e: no_medicines_window.destroy())
            no_medicines_window.bind('<Escape>', lambda e: no_medicines_window.destroy())
            
            # 等待窗口关闭
            no_medicines_window.wait_window()
    
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
        reminder_window.title(f"⚠️ {title}")
        reminder_window.geometry("700x500")
        reminder_window.resizable(True, True)
        
        # 设置窗口模态和样式
        reminder_window.transient(self.root)
        reminder_window.grab_set()
        reminder_window.configure(bg=self.colors['light'])
        
        # 创建主框架
        main_frame = ttk.Frame(reminder_window, style='Main.TFrame', padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题区域
        title_frame = ttk.Frame(main_frame, style='Main.TFrame')
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(title_frame, text=f"🔔 {title}", 
                               font=('Microsoft YaHei UI', 14, 'bold'),
                               foreground=self.colors['warning'],
                               background=self.colors['light'])
        title_label.pack()
        
        # 创建滚动文本框
        text_frame = ttk.LabelFrame(main_frame, text="📋 提醒内容", style='Card.TLabelframe', padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        text_widget = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=20,
            font=("Microsoft YaHei UI", 10),
            bg=self.colors['white'],
            fg=self.colors['dark'],
            relief='solid',
            borderwidth=1
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # 插入内容
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)  # 设置为只读
        
        # 创建按钮框架
        button_frame = ttk.Frame(main_frame, style='Main.TFrame')
        button_frame.pack(fill=tk.X)
        
        # 窗口关闭回调函数
        def on_window_close():
            self.reminder_window_open = False
            reminder_window.destroy()
        
        # 复制按钮
        copy_button = ttk.Button(button_frame, text="📋 复制内容", 
                                style='Primary.TButton',
                                command=lambda: self.copy_to_clipboard(content))
        copy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 确定按钮
        ok_button = ttk.Button(button_frame, text="✅ 确定", 
                              style='Success.TButton',
                              command=on_window_close)
        ok_button.pack(side=tk.RIGHT)
        
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
            # 更新状态栏
            self.status_var.set("✅ 内容已复制到剪贴板！")
            # 使用美化版的消息框
            self.show_info_message("复制成功", "内容已复制到剪贴板！")
        except Exception as e:
            self.status_var.set(f"❌ 复制失败: {str(e)}")
            self.show_error_message("复制失败", f"复制失败: {str(e)}")
    
    def show_info_message(self, title, message):
        """显示美化版的信息提示框"""
        info_window = tk.Toplevel(self.root)
        info_window.title(f"ℹ️ {title}")
        info_window.geometry("400x200")
        info_window.resizable(False, False)
        info_window.configure(bg=self.colors['light'])
        
        # 设置窗口模态
        info_window.transient(self.root)
        info_window.grab_set()
        
        # 创建主框架
        main_frame = ttk.Frame(info_window, style='Main.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 图标和标题
        icon_label = ttk.Label(main_frame, text="ℹ️", 
                             font=('Microsoft YaHei UI', 36),
                             foreground=self.colors['primary'],
                             background=self.colors['light'])
        icon_label.pack(pady=(10, 10))
        
        title_label = ttk.Label(main_frame, text=title, 
                              font=('Microsoft YaHei UI', 14, 'bold'),
                              foreground=self.colors['primary'],
                              background=self.colors['light'])
        title_label.pack(pady=(0, 10))
        
        message_label = ttk.Label(main_frame, text=message, 
                                font=('Microsoft YaHei UI', 10),
                                foreground=self.colors['dark'],
                                background=self.colors['light'],
                                justify=tk.CENTER)
        message_label.pack(pady=(0, 15))
        
        # 确定按钮
        ok_button = ttk.Button(main_frame, text="✅ 确定", 
                             style='Primary.TButton',
                             command=info_window.destroy)
        ok_button.pack()
        
        # 设置焦点
        ok_button.focus_set()
        
        # 绑定回车键
        info_window.bind('<Return>', lambda e: info_window.destroy())
        info_window.bind('<Escape>', lambda e: info_window.destroy())
        
        # 等待窗口关闭
        info_window.wait_window()
    
    def show_error_message(self, title, message):
        """显示美化版的错误提示框"""
        error_window = tk.Toplevel(self.root)
        error_window.title(f"❌ {title}")
        error_window.geometry("400x200")
        error_window.resizable(False, False)
        error_window.configure(bg=self.colors['light'])
        
        # 设置窗口模态
        error_window.transient(self.root)
        error_window.grab_set()
        
        # 创建主框架
        main_frame = ttk.Frame(error_window, style='Main.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 图标和标题
        icon_label = ttk.Label(main_frame, text="❌", 
                             font=('Microsoft YaHei UI', 36),
                             foreground=self.colors['danger'],
                             background=self.colors['light'])
        icon_label.pack(pady=(10, 10))
        
        title_label = ttk.Label(main_frame, text=title, 
                              font=('Microsoft YaHei UI', 14, 'bold'),
                              foreground=self.colors['danger'],
                              background=self.colors['light'])
        title_label.pack(pady=(0, 10))
        
        message_label = ttk.Label(main_frame, text=message, 
                                font=('Microsoft YaHei UI', 10),
                                foreground=self.colors['dark'],
                                background=self.colors['light'],
                                justify=tk.CENTER)
        message_label.pack(pady=(0, 15))
        
        # 确定按钮
        ok_button = ttk.Button(main_frame, text="✅ 确定", 
                             style='Danger.TButton',
                             command=error_window.destroy)
        ok_button.pack()
        
        # 设置焦点
        ok_button.focus_set()
        
        # 绑定回车键
        error_window.bind('<Return>', lambda e: error_window.destroy())
        error_window.bind('<Escape>', lambda e: error_window.destroy())
        
        # 等待窗口关闭
        error_window.wait_window()
    
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
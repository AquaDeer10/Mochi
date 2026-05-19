"""UI 布局尺寸常量。

集中管理所有与布局/尺寸相关的数值，方便统一调试。
修改这里即可全局影响窗口大小、间距、控件尺寸与图表边距。
"""

# ---------------- 主窗口 ----------------
APP_GEOMETRY = "1080x680"           # 主窗口默认宽高（启动时）
APP_MIN_WIDTH = 960                  # 主窗口最小宽度
APP_MIN_HEIGHT = 600                 # 主窗口最小高度

SIDE_WIDTH = 240                     # 左侧猫咪列表栏固定宽度
RADIUS_NONE = 0                      # 无圆角的统一值
BORDER_NONE = 0                      # 无边框的统一值
BORDER_THIN = 1                      # 细边框的统一值
TITLE_FONT_SIZE = 18                 # 左侧标题字号（“我的猫咪”）
SIDE_TITLE_PADX = 16                 # 左侧标题水平外边距
SIDE_TITLE_PADY = (20, 10)           # 左侧标题垂直外边距（上/下）
ADD_CAT_BTN_HEIGHT = 36              # “添加猫咪”按钮高度
SIDE_ADD_PADX = 16                   # “添加猫咪”按钮水平外边距
SIDE_ADD_PADY = 4                    # “添加猫咪”按钮垂直外边距
CAT_LIST_PADX = 8                    # 猫咪列表容器水平外边距
CAT_LIST_PADY = 10                   # 猫咪列表容器垂直外边距
CAT_ITEM_HEIGHT = 40                 # 猫咪列表单项按钮高度
CAT_ITEM_PADX = 4                    # 猫咪列表单项按钮水平间距
CAT_ITEM_PADY = 2                    # 猫咪列表单项按钮垂直间距

EMPTY_TOP_PADY = 120                 # 空状态整体距离顶部间距
EMPTY_ICON_FONT_SIZE = 80            # 空状态猫咪图标字号
EMPTY_TEXT_FONT_SIZE = 16            # 空状态提示文字字号
EMPTY_TEXT_PADY = 12                 # 空状态提示文字上方间距

DETAIL_CARD_CORNER = 16              # 顶部资料卡圆角
DETAIL_CARD_PAD = 24                 # 顶部资料卡外边距（四周）
PHOTO_PAD = 20                       # 资料卡中照片区域外边距
NAME_ROW_PADX = 10                   # 名称行水平外边距
NAME_ROW_PADY = (20, 4)              # 名称行垂直外边距（上/下）
NAME_FONT_SIZE = 28                  # 猫咪名称字号
HEADER_BTN_WIDTH = 60                # 资料卡头部常规按钮宽度（编辑/删除）
HEADER_BTN_HEIGHT = 28               # 资料卡头部按钮高度
WEIGHT_BTN_WIDTH = 86                # “体重管理”按钮宽度
HEADER_BTN_PADX = 10                 # 资料卡头部按钮间距

INFO_PADX = 10                       # 资料信息区水平外边距
INFO_PADY = (4, 20)                  # 资料信息区垂直外边距（上/下）
CHIP_CORNER = 10                     # 信息芯片圆角
CHIP_PADX = 12                       # 信息芯片内部水平内边距
CHIP_TOP_PADY = (8, 0)               # 信息芯片标题的内边距（上/下）
CHIP_BOTTOM_PADY = (0, 8)            # 信息芯片数值的内边距（上/下）
CHIP_OUTER_PADX = 10                 # 信息芯片之间水平间距
CHIP_OUTER_PADY = 4                  # 信息芯片垂直间距
CHIP_LABEL_FONT = 11                 # 信息芯片标题字号
CHIP_VALUE_FONT = 15                 # 信息芯片数值字号

DATA_ROW_PADX = 10                   # 数据目录行水平外边距
DATA_ROW_PADY = (0, 16)              # 数据目录行垂直外边距（上/下）
DATA_DIR_FONT = 12                   # 数据目录路径文字字号
OPEN_DIR_BTN_WIDTH = 84              # “打开目录”按钮宽度
OPEN_DIR_BTN_HEIGHT = 26             # “打开目录”按钮高度
OPEN_DIR_BTN_PADX = (8, 0)           # “打开目录”按钮左侧间距

EVENT_SCROLL_Y_INCREMENT = 3         # 事件滚动区每次滚动步长（像素）
SECTION_CORNER = 16                  # 事件分区容器圆角
SECTION_PADX = 24                    # 事件分区容器水平外边距
SECTION_PADY = (0, 16)               # 事件分区容器垂直外边距（上/下）
SECTION_HEAD_PADX = 16               # 分区标题栏水平内边距
SECTION_HEAD_PADY = 12               # 分区标题栏垂直内边距
SECTION_TITLE_FONT = 18              # 分区标题字号
SECTION_COUNT_FONT = 12              # 分区数量文本字号
SECTION_COUNT_PADX = (0, 10)         # 分区数量文本右侧间距
SECTION_ADD_BTN_WIDTH = 80           # 分区“添加”按钮宽度
SECTION_EMPTY_CORNER = 12            # 分区空状态卡片圆角
SECTION_EMPTY_HEIGHT = 60            # 分区空状态最小高度
SECTION_BODY_PADX = 12               # 分区内容区水平外边距
SECTION_BODY_PADY = (0, 14)          # 分区内容区垂直外边距（上/下）
EVENT_CARD_GRID_PADX = 6             # 事件卡片在列表中的水平间距
EVENT_CARD_GRID_PADY = 6             # 事件卡片在列表中的垂直间距

CAT_PHOTO_SIZE = 140                 # 猫咪照片显示尺寸（正方形）
CAT_PHOTO_FALLBACK_FONT = 72         # 无照片时猫咪 emoji 字号

# 事件卡片
EVENT_CARD_CORNER = 14               # 事件卡片圆角
EVENT_CARD_BORDER_WIDTH = 1          # 事件卡片边框粗细
EVENT_CARD_FIXED_HEIGHT = 254        # 事件卡片固定高度（单列列表）
EVENT_STRIP_WIDTH = 4                # 卡片左侧状态色条宽度
EVENT_STRIP_CORNER = 2               # 状态色条圆角
EVENT_STRIP_PADX = (8, 0)            # 状态色条水平外边距
EVENT_STRIP_PADY = 12                # 状态色条垂直外边距
EVENT_TITLE_PADX = 14                # 卡片标题区水平内边距
EVENT_TITLE_PADY = (14, 4)           # 卡片标题区垂直内边距（上/下）
EVENT_TITLE_FONT = 15                # 事件标题字号
EVENT_BADGE_FONT = 11                # 右上角状态徽章字号
EVENT_BADGE_CORNER = 8               # 状态徽章圆角
EVENT_BADGE_PADX = 8                 # 状态徽章水平内边距
EVENT_BADGE_PADY = 2                 # 状态徽章垂直内边距
EVENT_BADGE_HEIGHT = 20              # 状态徽章高度
EVENT_BADGE_GAP = (0, 6)             # 多个徽章之间的水平间距

EVENT_DATE_FONT = 13                 # 日期行字号
EVENT_DATE_PADX = 14                 # 日期行水平外边距
EVENT_DATE_PADY = (0, 8)             # 日期行垂直外边距（上/下）
EVENT_CHIPS_PADX = 14                # 年龄芯片行水平外边距
EVENT_CHIPS_PADY = (0, 8)            # 年龄芯片行垂直外边距（上/下）
EVENT_META_FONT = 12                 # 元信息行字号（距今/重复）
EVENT_META_PADX = 14                 # 元信息行水平外边距
EVENT_META_PADY = (0, 8)             # 元信息行垂直外边距（上/下）

EVENT_NOTE_CORNER = 8                # 备注区容器圆角
EVENT_NOTE_PADX = 14                 # 备注区容器水平外边距
EVENT_NOTE_PADY = (0, 10)            # 备注区容器垂直外边距（上/下）
EVENT_NOTE_TEXT_HEIGHT = 36          # 备注文本框高度（超出可滚动）
EVENT_NOTE_TEXT_PAD = 8              # 备注文本框内边距
EVENT_NOTE_EMPTY_PAD = 10            # 无备注占位文本边距

EVENT_ACTION_PADX = 10               # 底部操作区水平外边距
EVENT_ACTION_PADY = (0, 10)          # 底部操作区垂直外边距（上/下）
EVENT_ACTION_BTN_WIDTH = 58          # 底部操作按钮宽度
EVENT_ACTION_BTN_HEIGHT = 28         # 底部操作按钮高度
EVENT_ACTION_BTN_GAP = (0, 6)        # 底部操作按钮间距

MINI_CHIP_FONT = 11                  # 小芯片字号
MINI_CHIP_CORNER = 6                 # 小芯片圆角
MINI_CHIP_PADX = 8                   # 小芯片水平内边距
MINI_CHIP_PADY = 2                   # 小芯片垂直内边距
MINI_CHIP_HEIGHT = 22                # 小芯片高度
MINI_CHIP_GAP = (0, 6)               # 小芯片间距

# ---------------- 日期选择器 ----------------
DATE_PICKER_YEAR_WIDTH = 85          # 日期选择器：年份下拉宽度
DATE_PICKER_MONTH_WIDTH = 70         # 日期选择器：月份下拉宽度
DATE_PICKER_DAY_WIDTH = 70           # 日期选择器：日期下拉宽度
DATE_PICKER_ITEM_PADX = 2            # 日期选择器：各下拉控件间距

# ---------------- 事件对话框 ----------------
EVENT_DIALOG_WIDTH = 460             # 事件对话框宽度
EVENT_DIALOG_FUTURE_HEIGHT = 620     # 未来计划对话框高度
EVENT_DIALOG_PAST_HEIGHT = 520       # 已完成事件对话框高度
DIALOG_SIDE_PAD = 16                 # 通用对话框左右内边距
DIALOG_LABEL_PADY = 6                # 通用标签上下外边距
EVENT_TITLE_QUICK_PADY = (6, 0)      # 快捷事件按钮区垂直外边距
EVENT_QUICK_BTN_HEIGHT = 26          # 快捷事件按钮高度
EVENT_QUICK_BTN_PAD = 2              # 快捷事件按钮网格间距
EVENT_INPUT_PADY = 8                 # 日期输入区垂直外边距
EVENT_REPEAT_WRAP_PADY = (8, 0)      # 周期重复开关区垂直外边距
EVENT_REPEAT_ROW_PADY = (4, 0)       # 周期重复参数行垂直外边距
EVENT_REPEAT_VALUE_WIDTH = 70        # 周期数值输入框宽度
EVENT_REPEAT_UNIT_WIDTH = 80         # 周期单位下拉框宽度
EVENT_REPEAT_VALUE_PADX = 6          # 周期数值输入框左右间距
EVENT_NOTE_HEIGHT = 70               # 事件备注输入框高度
EVENT_BUTTON_ROW_PADY = 14           # 对话框底部按钮行垂直外边距
EVENT_BUTTON_PADX = 4                # 对话框底部按钮间距
EVENT_WEEK_INPUT_WIDTH = 70          # 周龄模式输入框宽度
EVENT_YM_INPUT_WIDTH = 60            # 年月龄模式输入框宽度

# ---------------- 猫咪编辑对话框 ----------------
CAT_DIALOG_GEOMETRY = "420x360"     # 猫咪编辑对话框默认尺寸
CAT_LABEL_TOP_PADY = (16, 4)         # 第一组标签顶部外边距
CAT_SECTION_PADY = (12, 4)           # 各字段分组标签上下外边距
CAT_PHOTO_BUTTON_WIDTH = 80          # 照片“选择”按钮宽度
CAT_BUTTON_ROW_PADY = 20             # 猫咪编辑底部按钮行垂直外边距

# ---------------- 体重对话框 ----------------
WEIGHT_DIALOG_GEOMETRY = "760x620"  # 体重管理对话框默认尺寸
WEIGHT_DIALOG_MIN_WIDTH = 700        # 体重管理最小宽度
WEIGHT_DIALOG_MIN_HEIGHT = 560       # 体重管理最小高度
WEIGHT_SECTION_PADX = 16             # 体重管理各分区左右内边距
WEIGHT_CHART_PADY = (16, 10)         # 图表分区垂直外边距
WEIGHT_CHART_TITLE_FONT = 15         # 图表标题字号
WEIGHT_CHART_TITLE_PADX = 12         # 图表标题左右内边距
WEIGHT_CHART_TITLE_PADY = (10, 6)    # 图表标题上下内边距
WEIGHT_CANVAS_HEIGHT = 260           # 图表 Canvas 高度
WEIGHT_CANVAS_PADX = 12              # 图表 Canvas 左右内边距
WEIGHT_CANVAS_PADY = (0, 12)         # 图表 Canvas 上下内边距
WEIGHT_ENTRY_ROW_PADY = (0, 10)      # 录入行垂直外边距
WEIGHT_ENTRY_LABEL_PADX = (12, 6)    # 录入行标签左右间距
WEIGHT_ENTRY_LABEL_PADY = 12         # 录入行标签上下间距
WEIGHT_ENTRY_DP_PADX = (0, 10)       # 日期选择器左右间距
WEIGHT_ENTRY_DP_PADY = 10            # 日期选择器上下间距
WEIGHT_INPUT_WIDTH = 120             # 体重输入框宽度
WEIGHT_SAVE_BTN_WIDTH = 90           # “保存记录”按钮宽度
WEIGHT_SAVE_BTN_PADX = (0, 8)        # “保存记录”按钮左侧间距
WEIGHT_LIST_PADY = (0, 10)           # 记录列表容器垂直外边距
WEIGHT_LIST_TITLE_FONT = 14          # 记录列表标题字号
WEIGHT_LIST_TITLE_PADX = 12          # 记录列表标题左右内边距
WEIGHT_LIST_TITLE_PADY = (10, 6)     # 记录列表标题上下内边距
WEIGHT_LIST_HEIGHT = 170             # 记录列表滚动区固定高度
WEIGHT_LIST_PADX = 8                 # 记录列表滚动区左右外边距
WEIGHT_CLOSE_ROW_PADY = (0, 14)      # 关闭按钮行垂直外边距
WEIGHT_CHART_DEBOUNCE_MS = 60        # 图表重绘防抖时间（毫秒）
WEIGHT_EMPTY_LIST_PAD = 8            # 无记录提示的外边距
WEIGHT_RECORD_ROW_CORNER = 8         # 单条体重记录行圆角
WEIGHT_RECORD_ROW_PADX = 6           # 单条体重记录行左右外边距
WEIGHT_RECORD_ROW_PADY = 4           # 单条体重记录行上下外边距
WEIGHT_RECORD_DATE_WIDTH = 120       # 记录日期列宽度
WEIGHT_RECORD_DATE_PADX = (10, 8)    # 记录日期列左右内边距
WEIGHT_RECORD_DATE_PADY = 8          # 记录日期列上下内边距
WEIGHT_RECORD_DELETE_WIDTH = 56      # 记录删除按钮宽度
WEIGHT_RECORD_DELETE_HEIGHT = 24     # 记录删除按钮高度
WEIGHT_RECORD_DELETE_PADX = 8        # 记录删除按钮右侧外边距

# 图表绘制边距与尺寸
CHART_MIN_WIDTH = 300                # 图表最小宽度（防止窗口过窄）
CHART_MIN_HEIGHT = 220               # 图表最小高度
CHART_PAD_LEFT = 50                  # 图表绘图区左边距（留给 y 轴刻度）
CHART_PAD_RIGHT = 20                 # 图表绘图区右边距
CHART_PAD_TOP = 18                   # 图表绘图区上边距
CHART_PAD_BOTTOM = 34                # 图表绘图区下边距（留给日期标签）
CHART_EMPTY_FONT_SIZE = 10           # 无数据时提示文本字号
CHART_TICK_FONT_SIZE = 9             # 坐标轴刻度字号
CHART_AXIS_TICK_COUNT = 5            # y 轴刻度数量
CHART_POINT_RADIUS = 3               # 折线节点圆点半径
CHART_LINE_WIDTH = 2                 # 折线宽度
CHART_LAST_LABEL_OFFSET_X = 6        # 最新点标签 x 方向偏移
CHART_LAST_LABEL_OFFSET_Y = 8        # 最新点标签 y 方向偏移

import sys
import os
import shutil
import json
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QTextEdit, QVBoxLayout, QPushButton,
    QFileDialog, QLineEdit, QHBoxLayout, QDateEdit, QMessageBox,
    QGroupBox, QGridLayout, QButtonGroup, QRadioButton
)
from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import QDate
from datetime import datetime
from openpyxl import load_workbook
import subprocess

SAVE_PATH = "data.xlsx"
PHOTO_DIR = "photos"
REWARD_FILE = "reward_balance.json"
PLAN_PATH = "日程计划表.xlsx"

os.makedirs(PHOTO_DIR, exist_ok=True)
if not os.path.exists(REWARD_FILE):
    with open(REWARD_FILE, 'w') as f:
        json.dump({"total": 0}, f)


# def get_today_task():
#     if not os.path.exists(PLAN_PATH):
#         return None
#     try:
#         df = pd.read_excel(PLAN_PATH)
#         today = datetime.now().strftime("%Y-%m-%d")
#         df_today = df[df['日期'] == today]
#         if not df_today.empty:
#             row = df_today.iloc[0]
#             task = row['训练安排']
#             return f"🎯 今日训练安排：{task}，完成可获得 +10 元 💰"
#     except Exception as e:
#         print("读取计划表失败：", e)
    # return None
def get_today_task():
    if not os.path.exists(PLAN_PATH):
        return None
    try:
        df = pd.read_excel(PLAN_PATH)
        today = datetime.now().strftime("%Y-%m-%d")
        df_today = df[df['日期'] == today]
        now = datetime.now().time()
        if not df_today.empty:
            row = df_today.iloc[0]
            task = row['训练安排']
            return (f"🎯 今日训练安排：\t\n"
                    f"🎯 今{task} \t\n"
                    # f"中午：{row['任务']}\n"
                    # f"晚上：休息\n"
                    f"完成后可获得：+10 元 💰")
    except Exception as e:
        print("读取计划表失败：", e)
    return None

class FitnessLogger(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("运动饮食记录器")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(1200, 1500)

        font = QFont("Arial", 20)
        self.setFont(font)

        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                border: 2px solid #cccccc;
                border-radius: 20px;
                font-size: 30px;
            }
            QLabel {
                font-weight: bold;
                color: #333333;
                font-size: 30px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 20px;
                padding: 6px 12px;
                font-size: 30px;
            }
            QPushButton:hover {
                background-color: #005ea0;
            }
            QLineEdit, QTextEdit, QDateEdit {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 4px;
                font-size: 30px;
            }
        """)

        self.layout = QVBoxLayout()

        hint = get_today_task()
        if hint:
            QMessageBox.information(self, "今日任务提醒", hint)

        self.date_label = QLabel("日期：")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        self.train_label = QLabel("训练部位：")
        self.train_group = QGroupBox()
        self.train_grid = QGridLayout()
        self.train_buttons = QButtonGroup(self)

        self.train_parts = ["未训练", "胸部", "背部", "腿部", "有氧-爬坡", "有氧-跑步"]
        for i, part in enumerate(self.train_parts):
            btn = QRadioButton(part)
            btn.setStyleSheet("font-size: 20px;")
            self.train_buttons.addButton(btn, i)
            self.train_grid.addWidget(btn, i // 3, i % 3)
        self.train_group.setLayout(self.train_grid)

        self.train_remark_label = QLabel("训练备注：")
        self.train_remark_edit = QTextEdit()
        self.train_remark_edit.setFixedHeight(60)

        self.food_label = QLabel("饮食记录：")
        self.food_morning = QLineEdit()
        self.food_morning.setPlaceholderText("早餐")
        self.food_lunch = QLineEdit()
        self.food_lunch.setPlaceholderText("午餐")
        self.food_dinner = QLineEdit()
        self.food_dinner.setPlaceholderText("晚餐")

        self.weight_label = QLabel("今日体重（斤）：")
        self.weight_input = QLineEdit()

        self.photo_label = QLabel("上传图片路径：")
        self.photo_path = QLineEdit()
        self.photo_path.setReadOnly(True)
        self.upload_button = QPushButton("上传照片")
        self.upload_button.clicked.connect(self.upload_photo)

        self.image_preview = QLabel("[暂无预览]")
        self.image_preview.setFixedHeight(60)
        self.image_preview.setStyleSheet("font-size: 14px;")

        self.save_button = QPushButton("保存记录")
        self.save_button.clicked.connect(self.save_record)

        self.layout.addWidget(self.date_label)
        self.layout.addWidget(self.date_edit)
        self.layout.addWidget(self.train_label)
        self.layout.addWidget(self.train_group)
        self.layout.addWidget(self.train_remark_label)
        self.layout.addWidget(self.train_remark_edit)
        self.layout.addWidget(self.food_label)
        self.layout.addWidget(self.food_morning)
        self.layout.addWidget(self.food_lunch)
        self.layout.addWidget(self.food_dinner)
        self.layout.addWidget(self.weight_label)
        self.layout.addWidget(self.weight_input)
        self.layout.addWidget(self.photo_label)
        photo_row = QHBoxLayout()
        photo_row.addWidget(self.photo_path)
        photo_row.addWidget(self.upload_button)
        self.layout.addLayout(photo_row)
        self.layout.addWidget(self.image_preview)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    # 其余部分保持不变


    # 其余部分保持不变
    def upload_photo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择照片", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_name:
            date_str = self.date_edit.date().toString("yyyyMMdd")
            ext = os.path.splitext(file_name)[1]
            new_name = os.path.join(PHOTO_DIR, f"{date_str}_{datetime.now().strftime('%H%M%S')}{ext}")
            shutil.copy(file_name, new_name)
            self.photo_path.setText(new_name)
            pixmap = QPixmap(new_name).scaledToHeight(180)
            self.image_preview.setPixmap(pixmap)

    def merge_parts(self, existing, new):
        existing_set = set([p.strip() for p in existing.split("、") if p]) if existing else set()
        new_set = set([p.strip() for p in new.split("、") if p]) if new else set()
        combined = existing_set.union(new_set)
        return "、".join(sorted(combined))

    def save_record(self):
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        selected_btn = self.train_buttons.checkedButton()
        selected_train = selected_btn.text() if selected_btn and selected_btn.isChecked() else ""

        weight = self.weight_input.text()
        food = f"早：{self.food_morning.text()} / 午：{self.food_lunch.text()} / 晚：{self.food_dinner.text()}"
        remark = self.train_remark_edit.toPlainText()
        train_done = "否" if selected_train == "未训练" or not selected_train else "是"

        reward = 10 if train_done == "是" else 0
        with open(REWARD_FILE, 'r') as f:
            data = json.load(f)
        data["total"] += reward
        with open(REWARD_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        new_row = {
            "日期": date_str,
            "体重": str(weight),
            "饮食记录": food,
            "训练部位": selected_train,
            "训练备注": remark,
            "训练完成": train_done,
            "本次奖励": str(reward),
            "累计奖励": str(data["total"])
        }

        if os.path.exists(SAVE_PATH):
            df = pd.read_excel(SAVE_PATH)
            if date_str in df["日期"].values:
                for key, value in new_row.items():
                    if key == "饮食记录":
                        existing_food = df.loc[df["日期"] == date_str, key].values[0]
                        combined_food = self.merge_food(existing_food, food)
                        df.loc[df["日期"] == date_str, key] = combined_food
                    elif key == "训练部位":
                        existing_part = df.loc[df["日期"] == date_str, key].values[0]
                        combined_part = self.merge_parts(existing_part, value)
                        df.loc[df["日期"] == date_str, key] = combined_part
                    else:
                        df.loc[df["日期"] == date_str, key] = str(value)
            else:
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df = pd.DataFrame([new_row])

        df.to_excel(SAVE_PATH, index=False)

        try:
            wb = load_workbook(SAVE_PATH)
            ws = wb.active
            for col in ws.columns:
                max_len = max((len(str(cell.value)) for cell in col if cell.value), default=8)
                col_letter = col[0].column_letter
                ws.column_dimensions[col_letter].width = max_len + 6
            wb.save(SAVE_PATH)
        except Exception as e:
            print("自动设置列宽失败：", e)

        QMessageBox.information(self, "保存成功",
                                f"记录已保存到 Excel\n🎉 今日奖励：+{reward} 元，累计：{data['total']} 元")

        try:
            os.startfile(SAVE_PATH)
        except Exception as e:
            print("打开 Excel 失败：", e)

        self.close()

    def merge_food(self, existing, new):
        def parse(section):
            return section.split("：")[-1].strip() if "：" in section else ""

        e_parts = existing.split("/") if existing else ["", "", ""]
        n_parts = new.split("/") if new else ["", "", ""]
        final = []
        for i in range(3):
            label = ["早", "午", "晚"][i]
            e = parse(e_parts[i]) if i < len(e_parts) else ""
            n = parse(n_parts[i]) if i < len(n_parts) else ""
            final.append(f"{label}：{n if n else e}")

        return " / ".join(final)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FitnessLogger()
    window.show()
    sys.exit(app.exec_())

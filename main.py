import sys
from PySide6.QtCore import QThread, Signal, QObject,QTimer
from PySide6.QtWidgets import QApplication,QDialog
from qt6UI.BossKill_ui import Ui_BossKillProject
import time
from datetime import datetime, timedelta
from PySide6.QtGui import QPixmap
from threading import Thread


class Boss():
    all_bosses = {}

    def __init__(self, name: str, start_time: str, end_time: str):
        self.workers = {}  # 保存worker对象
        self.ui_widgets = {}  # 保存UI控件
        self.threads = {}  # 保存线程
        self.name = name
        self.start_time = start_time
        self.end_time = end_time

        h, m = map(int, start_time.split(':'))
        self.start_time_second = h * 3600 + m * 60

        h, m = map(int, end_time.split(':'))
        self.end_time_second = h * 3600 + m * 60

        self.kill_time = None
        Boss.all_bosses[name] = self

    @classmethod
    def find_by_name(cls, name):
        return cls.all_bosses.get(name)

    def get_status(self, lineEdit_Refresh, label_Stata, idx: int):
        """快速重启计时器 - 重用线程，仅重启worker"""
        print(f"重启计时器 {idx}")

        # 保存UI控件
        self.ui_widgets[idx] = {
            'lineEdit_Refresh': lineEdit_Refresh,
            'label_Stata': label_Stata
        }

        # 如果worker已存在，先停止
        if idx in self.workers:
            print(f"停止现有worker {idx}")
            self.workers[idx].stop()
            # 断开旧的信号连接
            try:
                self.workers[idx].update_ui.disconnect()
                self.workers[idx].thread_finished.disconnect()
            except:
                pass
        else:
            # 创建新线程
            print(f"创建新线程 {idx}")
            thread = QThread()
            thread.setObjectName(f"BossThread_{idx}")
            self.threads[idx] = thread

        # 创建新的worker
        worker = TimegoWorker(
            start_time=self.start_time_second,
            end_time=self.end_time_second,
            idx=idx
        )

        # 保存worker引用
        self.workers[idx] = worker

        # 移动到对应线程
        worker.moveToThread(self.threads[idx])

        # 连接信号
        worker.update_ui.connect(self.on_update_ui)
        worker.thread_finished.connect(self.on_thread_finished)

        # 如果线程未运行，启动它
        if not self.threads[idx].isRunning():
            self.threads[idx].start()

        # 延迟一小段时间后启动worker，确保线程已准备好
        QTimer.singleShot(50, worker.start_worker)

        print(f"计时器 {idx} 重启成功")
        return True

    def on_update_ui(self, text, color, idx):
        """更新UI"""
        try:
            if idx in self.ui_widgets:
                widgets = self.ui_widgets[idx]

                lineEdit = widgets.get('lineEdit_Refresh')
                if lineEdit:
                    lineEdit.setText(text)
                    lineEdit.setStyleSheet(color)

                label = widgets.get('label_Stata')
                if label:
                    # label.setText(text)
                    label.setStyleSheet(color)

        except Exception as e:
            print(f"更新UI异常 (idx={idx}): {e}")

    def on_thread_finished(self, idx):
        """线程完成时的处理"""
        print(f"计时器 {idx} 已完成计时")
        # 可以在这里执行额外的清理工作

    def stop_worker(self, idx):
        """停止指定worker"""
        if idx in self.workers:
            print(f"停止worker {idx}")
            self.workers[idx].stop()
            # 可以不断开信号连接，worker会在重启时重新连接

    def stop_all_workers(self):
        """停止所有worker"""
        for idx in list(self.workers.keys()):
            self.stop_worker(idx)

    def cleanup(self):
        """清理所有资源"""
        self.stop_all_workers()

        # 停止所有线程
        for idx, thread in self.threads.items():
            if thread.isRunning():
                thread.quit()
                thread.wait()
            thread.deleteLater()

        self.threads.clear()
        self.workers.clear()
        self.ui_widgets.clear()

    def miss_status(self):
        """计算丢失状态（原有方法）"""
        from datetime import datetime

        if not self.kill_time:
            return "未击杀"

        current_time = datetime.now()
        second_since_kill = current_time.timestamp() - self.kill_time.timestamp()
        hour_since_kill = round(second_since_kill / 3600, 2)

        if second_since_kill < self.start_time_second:
            return "未刷新"
        elif self.start_time_second <= second_since_kill < (self.start_time_second + self.end_time_second) / 2:
            return f"经过{hour_since_kill}小时，小概率丢失"
        elif (self.start_time_second + self.end_time_second) / 2 <= second_since_kill < self.end_time_second:
            return f"经过{hour_since_kill}小时，大概率丢失"
        elif second_since_kill >= self.end_time_second:
            return f"经过{hour_since_kill}小时，已丢失"

    def set_kill_time(self, kill_time_str=None):
        from datetime import datetime

        if kill_time_str:
            self.kill_time = datetime.strptime(kill_time_str, "%Y-%m-%d %H:%M:%S")
        else:
            self.kill_time = datetime.now()

Boss_疯狂喵Z客 = Boss('疯狂喵Z客', '00:00', '01:50')
Boss_僵尸蘑菇王 = Boss('僵尸蘑菇王', '03:15', '03:45')
Boss_巴洛古 = Boss('巴洛古', '06:45', '09:00')
# Boss_巴洛古 = Boss('巴洛古', '00:00', '00:01')
Boss_蘑菇王 = Boss('蘑菇王', '03:15', '03:45')
Boss_雪毛怪人 = Boss('雪毛怪人', '00:45', '01:08')
Boss_喷火龙 = Boss('喷火龙', '00:59', '01:00')
Boss_格瑞芬多 = Boss('格瑞芬多', '00:59', '01:00')
Boss_寒霜冰龙 = Boss('寒霜冰龙', '04:00', '12:00')
Boss_海怒斯 = Boss('海怒斯', '03:00', '05:00')
Boss_仙人娃娃 = Boss('仙人娃娃', '02:38', '03:00')
Boss_蓝色蘑菇王 = Boss('蓝色蘑菇王', '12:00', '23:59')
Boss_黑轮王 = Boss('黑轮王', '13:00', '17:00')
Boss_九尾妖狐 = Boss('九尾妖狐', '03:30', '09:30')






class BossKillProject(Ui_BossKillProject, QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        # 下拉栏连接文本槽
        self.comboBox_Name.currentIndexChanged.connect(self.MinMaxtime)

        for i in range(115):
            btn = getattr(self,f"pushButton_Killrecord_{i}")
            btn.clicked.connect( lambda checked, idx=i: self.recordtime(idx))
            btn.clicked.connect(lambda checked, idx=i: self.Refreshstata(idx))
            btn = getattr(self, f"pushButton_Norefresh_{i}")
            btn.clicked.connect(lambda checked, idx=i: self.misstime(idx))



    # 记录击杀时间的函数，对应击杀时间栏
    def recordtime(self,idx:int):
        self.kill_time = datetime.now()
        time_now = datetime.now().strftime("%H:%M:%S")
        lineEdit=getattr(self,f"lineEdit_Killtime_{idx}")
        lineEdit_Miss =getattr(self,f"lineEdit_Miss_{idx}")
        lineEdit.setText(time_now)
        lineEdit_Miss .setText('')
        lineEdit_Miss.setStyleSheet("background-color: white;")

    # 下次可能刷新的时间函数。对应丢失/下次可能刷新的逻辑
    def misstime(self, idx: int):
        lineEdit_Killtime = getattr(self, f"lineEdit_Killtime_{idx}").text()
        if lineEdit_Killtime == "":
            lineEdit = getattr(self, f"lineEdit_Miss_{idx}")
            lineEdit.setText('未知')
        else:
            target_name = self.comboBox_Name.currentText()
            found_boss = Boss.find_by_name(target_name)
            found_boss.kill_time = self.kill_time
            miss_status = found_boss.miss_status()
            lineEdit = getattr(self, f"lineEdit_Miss_{idx}")
            if '已丢失' in miss_status :
                lineEdit.setText(miss_status)
                lineEdit.setStyleSheet("background-color: rgb(255, 0, 0);")
            else:
                lineEdit.setText(miss_status)
                lineEdit.setStyleSheet("background-color: rgb(255, 255, 255);")


    # 读取刷新时间函数
    def MinMaxtime(self):
        target_name = self.comboBox_Name.currentText()
        found_boss = Boss.find_by_name(target_name)
        self.lineEdit_Mintime.setText(found_boss.start_time)
        self.lineEdit_Maxtime.setText(found_boss.end_time)
        self.label_Boss.setPixmap(QPixmap(f":/img/Image/{found_boss.name}.png"))
        self.comboBox_Name.setEnabled(False)

    #刷新状态函数
    def Refreshstata(self,idx:int):
        target_name = self.comboBox_Name.currentText()
        found_boss = Boss.find_by_name(target_name)
        found_boss.kill_time = self.kill_time
        if self.kill_time == None:
            Refresh_stata = "未知刷新状态"
            lineEdit = getattr(self, f"lineEdit_Refresh_{idx}")
            lineEdit.setText(Refresh_stata)
        else:
            found_boss.kill_time = self.kill_time
            lineEdit_Refresh = getattr(self, f"lineEdit_Refresh_{idx}")
            label_Stata = getattr(self, f"label_Stata_{idx}")
            found_boss.get_status(lineEdit_Refresh,label_Stata,idx)

# 创建一个线程类，继承和重写
class TimegoWorker(QObject):
    update_ui = Signal(str, str, int)
    thread_finished = Signal(int)

    def __init__(self, start_time: int, end_time: int, idx: int):
        super().__init__()
        self.start_time = start_time
        self.end_time = end_time
        self.refreshtime = 0
        self.running = False  # 初始为False，等待start_worker启动
        self.idx = idx
        self.timer = None
        self.thread_start_time = 0

    def start_worker(self):
        """启动worker计时"""
        if self.timer:
            self.timer.stop()
            self.timer.deleteLater()

        self.running = True
        self.refreshtime = 0
        self.thread_start_time = time.time()

        # 创建定时器，每10秒触发一次
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_interval)
        self.timer.start(10000)  # 10秒

        # 立即执行一次
        self.run_interval()

    def run_interval(self):
        """定时器触发的运行逻辑"""
        if not self.running:
            return

        # 计算从线程启动开始的经过时间
        elapsed_time = time.time() - self.thread_start_time
        self.refreshtime = int(elapsed_time)  # 转换为整数秒

        try:
            if self.refreshtime < self.start_time:
                lineEdit_Refresh_text = '未刷新'
                color_background = "background-color: rgb(255, 255, 255);"
            elif self.start_time <= self.refreshtime < (self.start_time + self.end_time) / 2:
                lineEdit_Refresh_text = '小概率刷新'
                color_background = "background-color: rgb(240,255,240);"
            elif (self.start_time + self.end_time) / 2 <= self.refreshtime < self.end_time:
                lineEdit_Refresh_text = '大概率刷新'
                color_background = "background-color: rgb(0, 255, 0);"
            elif self.end_time <= self.refreshtime < (self.end_time + 100):
                lineEdit_Refresh_text = '已经刷新'
                color_background = "background-color: rgb(255, 255, 0);"
            elif self.refreshtime >= (self.end_time + 100):
                print(f'线程 {self.idx} 已经达到时间，线程结束')
                lineEdit_Refresh_text = '线程结束'
                color_background = "background-color: rgb(255, 0, 0);"
                self.running = False
                self.timer.stop()
                self.thread_finished.emit(self.idx)

            self.update_ui.emit(lineEdit_Refresh_text, color_background, self.idx)

        except Exception as e:
            print(f"线程 {self.idx} 异常: {e}")
            self.running = False

    def stop(self):
        """停止worker"""
        self.running = False
        if self.timer:
            self.timer.stop()
            self.timer.deleteLater()
            self.timer = None






if __name__ == "__main__":

    app = QApplication(sys.argv)

    bossKillProject = BossKillProject()

    sys.exit(app.exec())
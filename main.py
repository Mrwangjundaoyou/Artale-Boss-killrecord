import sys
from PySide6.QtWidgets import QApplication,QDialog
from qt6UI.BossKill_ui import Ui_BossKillProject
import time
from datetime import datetime, timedelta
from PySide6.QtGui import QPixmap
from threading import Thread



class Boss():
    all_bosses = {}
    def __init__(self,name:str,start_time:str,end_time:str):
        # 创建线程字典来管理线程
        self.threads = {}
        self.name = name
        self.start_time = start_time
        h, m = map(int, start_time.split(':'))
        self.start_time_second = h * 3600 + m * 60
        self.end_time = end_time
        h, m = map(int, end_time.split(':'))
        self.end_time_second = h * 3600 + m * 60
        self.kill_time = None
        # 自动注册到类变量中
        Boss.all_bosses[name] = self

    @classmethod
    def find_by_name(cls, name):
        """根据名称查找Boss"""
        return cls.all_bosses.get(name)

    # 对应预计刷新状态栏的文字栏
    def get_status(self,lineEdit,label_Stata,idx:int):
        if idx in self.threads:
            # 如果线程已存在，停止它
            if self.threads[idx].is_alive():
                self.threads[idx].stop()

            # 创建新线程
        thread_name = f"TimegoThread_{idx}"
        new_thread = TimegoThread(self.start_time_second,self.end_time_second,lineEdit,label_Stata)
        new_thread.name = thread_name  # 设置线程名称

        # 存入字典
        self.threads[idx] = new_thread
        # 启动线程
        new_thread.start()




    # 对应丢失/可能刷新的时间栏文字
    def miss_status(self):
        current_time = datetime.now()
        second_since_kill = (current_time - self.kill_time).total_seconds()
        hour_since_kill = round(second_since_kill/3600,2)

        if second_since_kill < self.start_time_second:
            return "未刷新"
        elif second_since_kill >= self.start_time_second and second_since_kill < (self.start_time_second+self.end_time_second)/2:
            return f"经过{hour_since_kill}小时，小概率丢失"
        elif second_since_kill >= (self.start_time_second+self.end_time_second)/2 and second_since_kill < self.end_time_second:
            return f"经过{hour_since_kill}小时，大概率丢失"
        elif second_since_kill >= self.end_time_second:
            return f"经过{hour_since_kill}小时，已丢失"

Boss_疯狂喵Z客 = Boss('疯狂喵Z客', '00:00', '01:50')
Boss_僵尸蘑菇王 = Boss('僵尸蘑菇王', '03:15', '03:45')
Boss_巴洛古 = Boss('巴洛古', '06:45', '09:00')
Boss_蘑菇王 = Boss('蘑菇王', '03:15', '03:45')
Boss_雪毛怪人 = Boss('雪毛怪人', '00:45', '01:08')
Boss_喷火龙 = Boss('喷火龙', '01:00', '01:00')
Boss_格瑞芬多 = Boss('格瑞芬多', '01:00', '01:00')
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
        lineEdit.setText(time_now)

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
class TimegoThread(Thread):
    # 在这里传参，然后写属性
    def __init__(self,start_time:int,end_time:int,lineEdit_Refresh,label_Stata):
        super().__init__()
        self.start_time = start_time
        self.end_time = end_time
        self.refreshtime = 0
        self.lineEdit_Refresh = lineEdit_Refresh
        self.label_Stata = label_Stata
        self._running = True  # 添加运行标志

    # 这个run方法就是以后线程要一直做的事情
    def run(self):
        while self._running:
            try:
                if self.refreshtime < self.start_time:
                    self.lineEdit_Refresh.setText('未刷新')
                    self.lineEdit_Refresh.setStyleSheet("background-color: rgb(255, 255, 255);")
                    self.label_Stata.setStyleSheet("background-color: rgb(255, 255, 255);")
                elif self.refreshtime >= self.start_time and self.refreshtime < (self.start_time + self.end_time) / 2:
                    self.lineEdit_Refresh.setText('小概率刷新')
                    self.lineEdit_Refresh.setStyleSheet("background-color: rgb(240,255,240);")
                    self.label_Stata.setStyleSheet("background-color: rgb(240,255,240);")
                elif self.refreshtime >= (self.start_time + self.end_time) / 2 and self.refreshtime < self.end_time:
                    self.lineEdit_Refresh.setText('大概率刷新')
                    self.lineEdit_Refresh.setStyleSheet("background-color: rgb(0, 255, 0);")
                    self.label_Stata.setStyleSheet("background-color: rgb(0, 255, 0);")
                elif self.refreshtime >= self.end_time:
                    self.lineEdit_Refresh.setText('已经刷新')
                    self.lineEdit_Refresh.setStyleSheet("background-color: rgb(255, 255, 0);")
                    self.label_Stata.setStyleSheet("background-color: rgb(255, 255, 0);")


                time.sleep(10)
                # 整数型用加法更新
                self.refreshtime += 10
                # self.runstata = True
                # 字符串用updata
                # self.refreshtime.update()
            except Exception as e:
                break
    def stop(self):  # 添加stop方法
        """停止线程"""
        self._running = False






if __name__ == "__main__":

    app = QApplication(sys.argv)

    bossKillProject = BossKillProject()

    sys.exit(app.exec())
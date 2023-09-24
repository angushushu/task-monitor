# task-monitor
A task monitor for self-regulation (clarification: there's no guarantee on the effect of this app)
It records the ratio and time you spent on each task, you can use it to track your focus shift (you have to start & stop recording manually).

Today|Across days
:-------------------------:|:-------------------------:
![tab1](https://github.com/angushushu/task-monitor/blob/main/screenshot1.jpg?raw=false) | ![tab2](https://github.com/angushushu/task-monitor/blob/main/screenshot2.jpg?raw=false)

#### How to deploy (beta version)

**.exe (for Windows):**<br>
Download and double-click. Notice the single file version doesn't have the icon.

**.zip (for Windows):**<br>
Download and unzip, double click the App.exe in the extracted folder<be>

**Linux and MacOS:**<be>
Forgive my laziness, but you can download the source code and use pyinstaller to make the package with the command line
`pyinstaller -D -i "icon.ico" --onefile App.py --noconsole`

**.py:**<br>
pip install numpy<br>
pip install pyside6<br>
pip install apscheduler<br>
python3 App.py

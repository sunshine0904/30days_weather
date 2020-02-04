默认获取所有城市当前时间之后15天的天气及当前时间之前的当月的天气

获取指定城市天气方法：
在need_city.txt文件下写入需要获取的城市即可获取指定城市的天气；（文件为空时获取所有城市）

依赖安装：
python3.7
pip install requests
pip install bs4
pip install lxml
pip install xlwt


使用：
win下右键以管理员权限运行run.bat即可；
linux下执行python weather.py
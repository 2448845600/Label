---
typora-root-url: image
---

## 用户手册

该标注系统包含两个模块，Step1App和Step2App。Step1App用于标注数据，得到原始的正标签和负标签；Step2App处理Step1App得到的xml文件，将正标签扩张，得到新的标签（其以原中心点，长边为边长的正方形框），负标签大小调整为扩张后的正标签边长。

### 使用流程

解压后，先利用Step1App标注初始的标签，之后运行Step2App调整框。

#### 下载安装

下载Label文件，解压后即可使用。**注意**，解压路径不能包含中文字符

#### Step1App

1. 打开Step1App文件夹，点击run.bat，进入用户界面

2. 导入文件夹

   点击左侧标签栏 “Open Dir”

3. 增加标签

   点击左侧标签栏 “Create RectBox”，或者点击键盘“w”

4. 删除标签

   点击左侧标签栏 “Delete RectBox”

5. 保存

   点击左侧标签栏 “Save”

6. 关闭

![1](/1.png)



#### Step2App

1. 打开Step2App文件夹，点击run.bat，进入用户界面；

2. 选择文件夹；

3. 结束。

   ![2](/2.png)



### 注意事项

- 解压路径不能包含中文字符










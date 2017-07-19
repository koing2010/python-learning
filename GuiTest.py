#!/usr/bin/python
# -*- coding: UTF-8 -*-

#!/usr/bin/python
# -*- coding: UTF-8 -*-

from tkinter import *           # 导入 tkinter 库
root = Tk()                     # 创建窗口对象的背景色
root.title("GUI TEST")
root.title("entry-test")    # 设置窗口标题
root.geometry("500x400")    # 设置窗口大小 注意：是x 不是*
root.resizable(width=False, height=False) # 设置窗口是否可以变化长/宽，False不可变，True可变，默认为True

                                # 创建两个列表
li     = ['C','python','php','html','SQL','java']
movie  = ['CSS','jQuery','Bootstrap']
listb  = Listbox(root)          #  创建两个列表组件
listb2 = Listbox(root)
DisText = Text(root)
DisText.config(width = 40,height = 4)
InText = Text(root)
InText.config(width = 40,height = 4)
for item in li:                 # 第一个小部件插入数据
    listb.insert(0,item)

for item in movie:              # 第二个小部件插入数据
    listb2.insert(0,item)


def EnterKeyProcess():
    DisText.insert(END,InText.get('1.0',END))

def ClearKeyProcess():
    DisText.delete('1.0',END)
    InText.delete('1.0', END)





InLable = Label(root,height= 3,width =10,text = "12345678",anchor = "w")
#listb.pack()                    # 将小部件放置到主窗口中
#listb2.pack()
DisText.pack()


Button(root, text="Enter", command=EnterKeyProcess ,width = 6,height = 2,fg="blue").pack(side=LEFT, padx=100, pady=7)
Button(root, text="Clear", command=ClearKeyProcess ,width = 6,height = 2,fg="blue").pack(side=LEFT, padx=0, pady=7)

InText.pack()
root.mainloop()                 # 进入消息循环

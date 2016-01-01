'''
Created by suemi on 15/12/30.
@summary: 此文件自动读取task.json配置,依次执行所有任务
'''

import os,sys,subprocess
sys.path.append(".")

import json
filePath=sys.argv[1] if len(sys.argv)>1 else "task.json"
taskList=json.loads(open(filePath,"r").read())
for task in taskList:
    excuteStr="python "+task["script"]
    for op in task["options"]:
        excuteStr+=" "+op
    for arg in task["arguments"]:
        excuteStr+=" "+arg
    output=subprocess.check_output(excuteStr,shell=True)
    print(output)
    print(task["script"]+" done!")

sys.exit(0)
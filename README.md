# 明日方舟音乐下载脚本

## 功能： 
 - 批量下载开服至今的明日方舟BGM(解放双手)
 - 并且以后音乐源若有更新，此工具可同步增量更新(保持目录结构)

## 使用说明：
 - 运行对应系统的可执行文件即可开启下载进程
 - 目前提供 macOS_arm64, macOS_intel, windows_x64 和 centos_x64 平台的可执行文件，不在其列的可使用源码打包
 - 通常会有网络异常的情况，多下载几次就能下下来

## 下载源： 
 - https://arknightsost.nbh.workers.dev

## 默认下载路径：
 - MacOS：~/bgm/
 - Windows： main_win_x64.exe 的同级目录的 bgm 文件夹下
 - Linux：同 Windows(在 CentOS7 下测得)

## 若自己打包，则需要用安装依赖，命令：
 - pip install requests tqdm retrying
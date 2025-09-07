import os
import re
import subprocess
from mcrcon import MCRcon
import secrets
import sys
import threading
import importlib
import function
import settings
import json

concheck = False # RCON接続確認用
disconcheck = False # RCON切断確認用

sets = settings.settings() # 設定クラスをインスタンス化
sets.__init__() # 設定クラスの初期化

sets.check() # 設定確認
sets.rconcheck() # RCON設定確認

func = function.function() # functionクラスをインスタンス化
func.__init__() # functionクラスの初期化

server = subprocess.Popen(['java','-Xms%s' % sets.memory,'-Xmx%s' % sets.memory,'-jar', sets.jar,'--nogui'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True,text=True,encoding='utf-8') # サーバーを起動

serverstd = [] # サーバーの出力を格納するリスト

def rcon(): # RCON動作
  mcr = MCRcon("localhost", sets.rconpass) # MCRcon起動
  mcr.connect() # 接続
  func.mcrset(mcr) # MCRconをfunctionに引き渡し
  func.load() # functionのload関数を実行
  func.rconops = sets.rconops # 管理権限リストをfunctionに引き渡し
  while(not disconcheck and func.enable): # メイン処理
    for i in serverstd[:]: # サーバーの出力を読み取る
      func.stdout(i) # 標準出力読み取り
      serverstd.pop(0)
    try:
      func.loop() # ループ処理
    except Exception as e:
      print(f"[RCON ERROR] {str(e)}")
      mcr.command(f'/tellraw @a "[RCON ERROR] {str(e)}"')
      mcr.command('/tellraw @a "RCON stopped!"')
      func.enable = False
      mcr.disconnect
  mcr.disconnect() # 切断

def reload(): # 再起動処理
  global func
  importlib.reload(function)
  newfunc = function.function() # functionクラスをインスタンス化
  newfunc.__init__() # functionクラスの初期化
  newfunc.takeover(func) # MCRconをfunctionに引き渡し
  func = newfunc # functionを更新
  func.enable = True
  print("[RCON INFO] Function reloaded") # メッセージを表示

for i in server.stdout:
  print(i,end="") # サーバーの出力を表示
  if concheck == True and disconcheck == False and func.enable: # RCON接続が確立されている場合
    serverstd.append(i) # サーバーの出力を引き渡し
  if len(i.split()) > 3: # サーバーの出力が3単語以上の場合
    # 構文解析開始
    temp = i
    if re.search(r"\[\d{2}:\d{2}:\d{2}\]", temp) != None:
      time = re.search(r"\[\d{2}:\d{2}:\d{2}\]", temp).group() # 時間を取得
      temp = temp.replace("%s " % time, "") # テキストから時間を削除
    if re.search(r"\[.*?\]", temp) != None:
      type = re.search(r"\[.*?\]", temp).group() # タイプを取得
      temp = temp.replace("%s: " % type, "") # テキストからタイプを削除
    if concheck == False and temp == "Thread RCON Listener started\n": # RCONのListen開始
      concheck = True
      rconth = threading.Thread(target=rcon,args=())
      rconth.start()
    if temp == "Reloading!\n": # サーバーの再起動(サーバー実行)
      reload()
    if re.search(r"\[.*?: Reloading!\]\n", temp) != None: # サーバーの再起動(コマンド実行)
      reload()
    if re.search(r"<.*?>", temp) != None: # プレイヤーが発言した場合
      player = re.search(r"<.*?>", temp).group()[1:-1] # プレイヤー名を取得
      temp = temp.replace("<%s> " % player, "") # テキストからプレイヤー名を削除
      player = re.sub(r"\[.*?\]", "", player)
      if temp == "rcon >>setup\n": # RCONセットアップコマンド
        serverstd = []
        disconcheck = True
        rconth.join()
        disconcheck = False
        newrconth = threading.Thread(target=rcon, args=()) # RCONスレッドを作成
        newrconth.start() # RCONスレッドを起動
        rconth = newrconth # RCONスレッドを更新
      elif temp == "rcon >>shutdown\n":
        serverstd = []
        disconcheck = True
        rconth.join()
    if disconcheck == False and temp == "Stopping server\n": # サーバーの停止
      disconcheck = True

os.system("Pause") # プログラムの終了処理
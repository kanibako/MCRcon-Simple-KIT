import random
from mcrcon import MCRcon
import json
import re
import os

class function():
  def __init__(self):
    self.playernum = 0 # プレイヤー数
    self.players = [] # プレイヤーリスト
    self.mcr: MCRcon = None # RCON接続
    self.enable = True
    self.rconops = [] # 管理権限リスト
    self.protect = False # 保護モード
    self.protectlist = [] # 保護モードの対象リスト

  def mcrset(self, mcr:MCRcon):
    self.mcr = mcr

  def takeover(self, function) :
    self.__dict__ = function.__dict__
  
  def stdout(self, text:str): # 標準出力読み取り
    if self.enable:
      if re.search(r"\[\d{2}:\d{2}:\d{2}\]", text) != None:
        time = re.search(r"\[\d{2}:\d{2}:\d{2}\]", text).group() # 時間を取得
        text = text.replace("%s " % time, "") # テキストから時間を削除

      if re.search(r"\[.*?\]", text) != None:
        type = re.search(r"\[.*?\]", text).group() # タイプを取得
        text = text.replace("%s: " % type, "") # テキストからタイプを削除

      if re.match(r"<.*?>", text) != None: # プレイヤーが発言した場合
        player = re.search(r"<.*?>", text).group()[1:-1] # プレイヤー名を取得
        player = re.sub(r"[.*?]", "", player) # チーム表示削除(1回目)
        player = re.sub(r"[.*?]", "", player) # チーム表示削除(2回目)
        text = text.replace("<%s> " % player, "") # テキストからプレイヤー名を削除

        if re.match(r"rcon >>", text) != None: # RCONコマンドが入力された場合
          text = text.replace("rcon >>", "") # テキストからRCONコマンドを削除
          text = text.replace("\n", "") # テキストから改行を削除
          if text == "setup" or text == "shutdown": # セットアップコマンド・シャットダウンコマンド
            pass
          elif re.match(r"^protect", text) != None: # 保護モード設定コマンド
            text = text.split(" ")
            if player in self.rconops: # 管理権限リストに含まれている場合
              if len(text) == 1:
                if self.protect:
                  self.protect = False
                  self.mcr.command("/tellraw %s \"保護モードを解除しました\"" % player)
                else:
                  self.protect = True
                  self.mcr.command("/tellraw %s \"保護モードを有効にしました\"" % player)
              elif len(text) != 1:
                if text[1] == "list":
                  self.mcr.command("/tellraw %s \"保護モードプレイヤー:%s\"" % (player, self.protectlist))
                elif text[1] == "add":
                  if text[2] not in self.protectlist:
                    self.protectlist.append(text[2])
                    self.mcr.command("/tellraw %s \"%sを保護モードに追加しました\"" % (player, text[2]))
                  else:
                    self.mcr.command("/tellraw %s \"%sは保護モードに登録済みです\"" % (player, text[2]))
                elif text[1] == "remove":
                  if text[2] in self.protectlist:
                    self.protectlist.remove(text[2])
                    self.mcr.command("/tellraw %s \"%sを保護モードから削除しました\"" % (player, text[2]))
                  else:
                    self.mcr.command("/tellraw %s \"%sは保護モードに登録されていません\"" % (player, text[2]))
            else:
              self.mcr.command("/tellraw %s \"保護モード設定は管理者のみ有効です\"" % player)
          else:
            if(text != "setup" and text != "shutdown"): # その他処理
              # 任意テキストの処理
              # 特定のコマンドを打った時に任意の処理ができます(特定のメッセージを送ったり、特定のアイテムを配布したり出来ます)
              pass

  def load(self): # 読み込み/再読み込み処理
    # 読み込み表示
    print("[RCON INFO] Function loaded")

  def loop(self): # 常時実行処理
    if self.enable:
      # ログインチェック
      res = self.mcr.command("/list")
      temp = res.split(" ")
      self.playernum = int(temp[2])
      playerstemp = temp[10:]
      for i in range(len(playerstemp)):
        playerstemp[i] = re.sub(r"\[.*?\]", "", playerstemp[i])
        playerstemp[i] = re.sub(r"[,]", "", playerstemp[i])
      if self.playernum != 0:
        for i in playerstemp:
          # self.mcr.command("/item replace entity %s hotbar.8 with paper{display:{Name:'{\"text\":\"%s\",\"italic\":false}'}}" % (i ,i))
          if i in self.players:
            continue
          else:
            self.players.append(i)
            self.login(i)

      # ログアウトチェック
      for i in self.players:
        if i in playerstemp:
          continue
        else:
          self.players.remove(i)
          self.logout(i)
      
      # 常時実行処理をここに記載
      # サーバーの監視や定期的な処理ができます
      pass

  def login(self, username:str): # ログイン処理
    # 保護モード
    if self.protect and username not in self.protectlist:
      self.mcr.command("/kick %s 現在サーバーには入れません" % username)
    
    # ログイン時メイン処理
    # 参加者に対してメッセージを表示することが出来ます
    pass
    
    # ログイン表示
    print("[RCON INFO] %s is logged in" % username)

  def logout(self, username:str): # ログアウト処理
    # ログアウト時メイン処理
    pass

    # ログアウト表示
    print("[RCON INFO] %s is logged out" % username)
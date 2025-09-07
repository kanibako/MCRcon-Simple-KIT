import os
import secrets
import sys

class settings():
  def __init__(self):
    self.jar = 'server.jar' # サーバーjarファイルのパス
    self.rconpass = "" # サーバーのRCONパスワード
    self.memory = "4G" # サーバーのメモリ数設定
    self.setting = "rconsetting.txt" # 設定ファイル名
    self.properties = "server.properties" # サーバープロパティファイル名
    self.rconops = [] # RCONの管理権限リスト
    self.check1 = False 
    self.check2 = False 
  
  def rconsetup(self): # RCON新規設定
    file = open(self.setting,'w') # 設定ファイルを作成
    file.write("jar=server.jar\n") # デフォルトのjarファイル名を書き込む
    self.rconpass = secrets.token_hex(16) # パスワードを生成
    file.write("password=" + self.rconpass + "\n") # パスワードを書き込む
    file.write("Memory=4G\n") # メモリを書き込む
    file.write("rconops=\n") # 管理権限リストを書き込む
    file.close() # ファイルを閉じる
    print("[RCON INFO] RCON is setup") # メッセージを表示

  def rcontakeover(self): # RCON引き継ぎ
    file = open(self.setting,'w') # 設定ファイルを作成
    file.write("jar=server.jar\n") # デフォルトのjarファイル名を書き込む
    file.write("password=" + self.rconpass) # パスワードを書き込む
    file.write("Memory=4G\n") # メモリを書き込む
    file.write("rconops=\n") # 管理権限リストを書き込む
    file.close() # ファイルを閉じる
    print("[RCON INFO] RCON is setuped") # メッセージを表示

  def rconenable(self, rconindex:int, passindex:int): # RCON有効化
    file = open(self.properties,'r',encoding="utf-8") # ファイルを読み込む
    prop = file.readlines() # ファイルの内容を取得
    file.close()
    prop[rconindex] = "enable-rcon=true\n" # RCONを有効にする
    if self.rconpass == "":
      self.rconpass = secrets.token_hex(16) # パスワードを生成
    prop[passindex] = "rcon.password=" + self.rconpass + "\n" # RCONのパスワードを設定
    file = open(self.properties,'w',encoding="utf-8") # ファイルを書き込みモードで開く
    file.writelines(prop) # ファイルに書き込む
    file.close() # ファイルを閉じる
    print("[RCON INFO] RCON is enabled") # メッセージを表示

  def rconcheck(self): # RCON設定確認
    file = open(self.setting,'r') # 設定ファイルを読み込む
    temp = file.readlines() # ファイルの内容を取得
    file.close() # ファイルを閉じる
    if len(temp) < 3: # RCON設定が不適切な場合
      self.rconsetup() # RCON設定
    else: # RCON設定が適切な場合
      if temp[0][:4] == "jar=": # jarファイル名が設定されているか確認
        if temp[0][4] == "\n": # jarファイル名が空の場合
          sys.exit("[RCON ERROR] JAR file is empty") # エラーを表示
        else: # jarファイル名が設定されている場合
          self.jar = temp[0][4:-1] # jarファイル名を取得
          if os.path.exists(self.jar) == False: # jarファイルが存在しない場合
            sys.exit("[RCON ERROR] JAR file is not found") # エラーを表示
      else: # jarファイル名が設定されていない場合
        if os.path.exists("server.jar") == False: # デフォルトのjarファイルが存在しない場合
          sys.exit("[RCON ERROR] JAR file is not found") # エラーを表示
        temp[0] = "jar=server.jar\n" # デフォルトのjarファイル名を設定

      if temp[1][:9] == "password=": # パスワードが設定されているか確認
        self.rconpass = temp[1][9:-1] # パスワードを取得
      else: # パスワードが設定されていない場合
        self.rconpass = secrets.token_hex(16) # パスワードを生成
        temp[1] = "password=" + self.rconpass + "\n" # パスワードを設定

      if temp[2][:7] == "Memory=": # メモリが設定されているか確認
        self.memory = temp[2][7:-1] # メモリを取得
      else: # メモリが設定されていない場合
        temp[2] = "Memory=4G\n" # メモリを設定

      if temp[3][:8] == "rconops=": # 管理権限リストが設定されているか確認
        self.rconops = temp[3][8:-1].split(",") # 管理権限リストを取得
      else: # 管理権限リストが設定されていない場合
        temp[3] = "rconops=\n" # 管理権限リストを設定
        
      file = open(self.setting,'w') # 設定ファイルを書き込みモードで開く
      file.writelines(temp) # ファイルに書き込む
      file.close() # ファイルを閉じる
  
  def check(self):
    self.check1 = os.path.exists(self.setting) # 設定ファイルの存在確認
    self.check2 = os.path.exists(self.properties) # サーバープロパティファイルの存在確認
    
    if self.check2 == False: # サーバープロパティファイルが存在しない場合
      if self.check1 == False: # 設定ファイルが存在しない場合
        # サーバー初回起動 & RCON初回設定 (server.propetiesの設定は後で)
        self.rconpass = self.rconsetup() # RCON設定

    else: # サーバープロパティファイルが存在する場合
      # サーバー2回目以降起動
      file = open(self.properties,'r',encoding="utf-8") # ファイルを読み込む
      prop = file.readlines() # ファイルの内容を取得
      file.close()
      for i in prop: # ファイルの内容を1行ずつ確認
        if i[:12] == "enable-rcon=": # RCONが有効になっているか確認
          rconindex = prop.index(i) # RCONの行番号を取得
        if i[:14] == "rcon.password=": # RCONのパスワードが設定されているか確認
          passindex = prop.index(i) # RCONのパスワードの行番号を取得

      if prop[rconindex][12:] == "true\n": # RCONが有効になっている場合
        if prop[passindex][14:] == "\n": # RCONのパスワードが設定されていない場合
          self.rconenable(rconindex, passindex) # RCON有効化
        else: # RCONのパスワードが設定されている場合
          self.rconpass = prop[passindex][14:] # RCONのパスワードを取得
        if self.check1 == False: # 設定ファイルが存在しない場合
          self.rcontakeover() # RCON引き継ぎ

      else: # RCONが有効になっていない場合
        if self.check1 == True: # 設定ファイルが存在する場合
          self.rconcheck() # RCON設定確認
          self.rconenable(rconindex, passindex) # RCON有効化
        else: # 設定ファイルが存在しない場合
          self.rconenable(rconindex, passindex) # RCON有効化
          self.rcontakeover() # RCON引き継ぎ
#----------------------------------------------------------------------
# 箱庭諸島 ver2.30
# ターン進行モジュール(ver1.02)
# 使用条件、使用方法等は、hako-readme.txtファイルを参照
#
# 箱庭諸島のページ: http://www.bekkoame.ne.jp/~tokuoka/hakoniwa.html
#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Hakoniwa R.A. Final Edition
# メインスクリプト(箱庭諸島 ver2.30)
# 使用条件、使用方法等は、read-renas.txtファイルを参照
#
# KEI PAGE: http://www5b.biglobe.ne.jp/~k-e-i/
#----------------------------------------------------------------------

#周囲2ヘックスの座標
my(@ax) = (0, 1, 1, 1, 0,-1, 0, 1, 2, 2, 2, 1, 0,-1,-1,-2,-1,-1, 0);
my(@ay) = (0,-1, 0, 1, 1, 0,-1,-2,-1, 0, 1, 2, 2, 2, 1, 0,-1,-2,-2);

#----------------------------------------------------------------------
# 島の新規作成モード
#----------------------------------------------------------------------
# メイン
sub newIslandMain {
    # 島がいっぱいでないかチェック
    if($HislandNumber >= $HmaxIsland) {
	unlock();
	tempNewIslandFull();
	return;
    }

    # 名前があるかチェック
    if($HcurrentName eq '') {
	unlock();
	tempNewIslandNoName();
	return;
    }

    # 名前があるかチェック
    if($HcurrentOwnerName eq '') {
	unlock();
	tempNewIslandNoName();
	return;
    }

    # 名前があるかチェック
    if($Hmessage eq '') {
	unlock();
	tempNewIslandNoName();
	return;
    }

    # 名前が正当かチェック
    if($HcurrentName =~ /[,\?\(\)\<\>\$]|^無人$/) {
	# 使えない名前
	unlock();
	tempNewIslandBadName();
	return;
    }

    # 名前の重複チェック
    if(nameToNumber($HcurrentName) != -1) {
	# すでに発見ずみ
	unlock();
	tempNewIslandAlready();
	return;
    }

    # passwordの存在判定
    if($HinputPassword eq '') {
	# password無し
	unlock();
	tempNewIslandNoPassword();
	return;
    }

    # 確認用パスワード
    if($HinputPassword2 ne $HinputPassword) {
	# password間違い
	unlock();
	tempWrongPassword();
	return;
    }

	# IPゲット
	$speaker = $ENV{'REMOTE_HOST'};
	$speaker = $ENV{'REMOTE_ADDR'} if ($speaker eq '');

    # IPの重複チェック
    if($IPcut == 1) {
    if(ipToNumber($speaker) != -1) {
	# すでに発見ずみ
	unlock();
	tempIPIslandAlready();
	return;
    }
    }

    # 新しい島の番号を決める
    $HcurrentNumber = $HislandNumber;
    $HislandNumber++;
    $Hislands[$HcurrentNumber] = makeNewIsland();
    my($island) = $Hislands[$HcurrentNumber];

    # 各種の値を設定
    $island->{'name'} = $HcurrentName;
    $island->{'id'} = $HislandNextID;
    $HislandNextID ++;
    $island->{'absent'} = $HgiveupTurn - 3;
    $island->{'comment'} = htmlEscape($Hmessage);
    $island->{'password'} = encode($HinputPassword);
    $island->{'eisei1'} = 0;
    $island->{'eisei2'} = 0;
    $island->{'eisei3'} = '0,0,0,0,0';
    $island->{'eisei4'} = '0,0,0,0,0,0,0,0,0,0,0';
    $island->{'eisei5'} = '0,0,0,0,0,0,0';
    $island->{'eisei6'} = '0,0,0,0,0,0,0,0,0,0,0,0';
    $island->{'eis1'} = 0;
    $island->{'eis2'} = 0;
    $island->{'eis3'} = 0;
    $island->{'eis4'} = 0;
    $island->{'eis5'} = 0;
    $island->{'eis6'} = 0;
    $island->{'eis7'} = 0;
    $island->{'eis8'} = '(未登録)';
    $island->{'taiji'} = 0;
    $island->{'onm'} = htmlEscape($HcurrentOwnerName);
    $island->{'ownername'} = htmlEscape($HcurrentOwnerName);
    $island->{'id1'} = $HislandNextID;
    $island->{'totoyoso'} = '(未登録)';
    $island->{'totoyoso2'}= 555;
    $island->{'kei'} = 0;
    $island->{'rena'} = 0;
    $island->{'momotan'} = 0;
    $island->{'fore'} = 0;
    $island->{'pika'} = 0;
    $island->{'hamu'} = 0;
    $island->{'monta'} = 0;
    $island->{'tare'} = 0;
    $island->{'zipro'} = 0;
    $island->{'leje'} = 0;

    $island->{'ipname'} = $HcurrentName;
    $island->{'ip0'} = "$speaker";
    $island->{'ip1'} = "$speaker";
    $island->{'ip2'} = "$speaker";
    $island->{'ip3'} = "$speaker";
    $island->{'ip4'} = "$speaker";
    $island->{'ip5'} = "$speaker";
    $island->{'ip6'} = 0;
    $island->{'ip7'} = 0;
    $island->{'ip8'} = 0;
    $island->{'ip9'} = 0;
    $island->{'etc0'} = 0;
    $island->{'etc1'} = 0;
    $island->{'etc2'} = 0;
    $island->{'etc3'} = 0;
    $island->{'etc4'} = 0;
    $island->{'etc5'} = '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0';
    $island->{'etc6'} = '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0';
    $island->{'etc7'} = '0,0,0';
    $island->{'etc8'} = '0,0,0,0,0,0,0';
    $island->{'etc9'} = '0,0,0,0,0,0,0';
    $island->{'auc0'} = '0,0,0,0,0';
    $island->{'auc1'} = 0;
    $island->{'auc2'} = 0;
    $island->{'auc3'} = 0;
    $island->{'auc4'} = '0,0,0';
    $island->{'auc5'} = '0,0,0,0,0';
    $island->{'auc6'} = '0,0,0';
    $island->{'auc7'} = 0;
    $island->{'auc8'} = 0;
    $island->{'auc9'} = '0,0,0,0,0';

    if($anothermood == 1) {
	my($onm);
	$onm = $island->{'onm'};
	$island->{'totoyoso2'} = "$onmシティー";
	$island->{'shu'}++;
	$island->{'eisei1'} = 7;
    }

	    if(random(100) < 50) {
	       $island->{'eis1'} = 200;
	    } else {
	       $island->{'eis2'} = 200;
	    }

    # 人口その他算出
    estimate($HcurrentNumber);

    # データ書き出し
    writeIslandsFile($island->{'id'});
    logDiscover($HcurrentName); # ログ

    # 開放
    unlock();

    # 発見画面
    tempNewIslandHead($HcurrentName); # 発見しました!!
    islandInfo(); # 島の情報
    islandMap(1); # 島の地図、ownerモード
}

# 新しい島を作成する
sub makeNewIsland {
    # 地形を作る
    my($land, $landValue) = makeNewLand();

    # 初期コマンドを生成
    my(@command, $i);
    for($i = 0; $i < $HcommandMax; $i++) {
	 $command[$i] = {
	     'kind' => $HcomDoNothing,
	     'target' => 0,
	     'x' => 0,
	     'y' => 0,
	     'arg' => 0
	 };
    }

    # 初期掲示板を作成
    my(@lbbs);
    for($i = 0; $i < $HlbbsMax; $i++) {
         $lbbs[$i] = "0<<0>>";
    }

    # 島にして返す
    return {
	'land' => $land,
	'landValue' => $landValue,
	'command' => \@command,
	'lbbs' => \@lbbs,
	'money' => $HinitialMoney,
	'food' => $HinitialFood,
	'prize' => '0,0,',
        'monsterlive' => 0,
        'monsterlivetype' => 0,
    };
}

# 新しい島の地形を作成する
sub makeNewLand {
    # 基本形を作成
    my(@land, @landValue, $x, $y, $i);

    # 海に初期化
    for($y = 0; $y < $HislandSize; $y++) {
	 for($x = 0; $x < $HislandSize; $x++) {
	     $land[$x][$y] = $HlandSea;
	     $landValue[$x][$y] = 0;
	 }
    }

    # 中央の4*4に荒地を配置
    my($center) = $HislandSize / 2 - 1;
    for($y = $center - 1; $y < $center + 3; $y++) {
	 for($x = $center - 1; $x < $center + 3; $x++) {
	     $land[$x][$y] = $HlandWaste;
	 }
    }

    # 8*8範囲内に陸地を増殖
    for($i = 0; $i < 120; $i++) {
	 # ランダム座標
	 $x = random(8) + $center - 3;
	 $y = random(8) + $center - 3;

	 my($tmp) = countAround(\@land, $x, $y, $HlandSea, 7);
	 if(countAround(\@land, $x, $y, $HlandSea, 7) != 7){
	     # 周りに陸地がある場合、浅瀬にする
	     # 浅瀬は荒地にする
	     # 荒地は平地にする
	     if($land[$x][$y] == $HlandWaste) {
		 $land[$x][$y] = $HlandPlains;
		 $landValue[$x][$y] = 0;
	     } else {
		 if($landValue[$x][$y] == 1) {
                     $land[$x][$y] = $HlandWaste;
                     $landValue[$x][$y] = 0;
		 } else {
		     $landValue[$x][$y] = 1;
		 }
	     }
	 }
    }

    # 森を作る
    my($count) = 0;
    while($count < 4) {
	 # ランダム座標
	 $x = random(4) + $center - 1;
	 $y = random(4) + $center - 1;

	 # そこがすでに森でなければ、森を作る
	 if($land[$x][$y] != $HlandForest) {
	     $land[$x][$y] = $HlandForest;
	     $landValue[$x][$y] = 5; # 最初は500本
	     $count++;
	 }
    }

    # 町を作る
    $count = 0;
    while($count < 2) {
	 # ランダム座標
	 $x = random(4) + $center - 1;
	 $y = random(4) + $center - 1;

	 # そこが森か町でなければ、町を作る
	 if(($land[$x][$y] != $HlandTown) &&
	    ($land[$x][$y] != $HlandForest)) {
	     $land[$x][$y] = $HlandTown;
	     $landValue[$x][$y] = 5; # 最初は500人
	     $count++;
	 }
    }

    # 山を作る
    $count = 0;
    while($count < 1) {
	 # ランダム座標
	 $x = random(4) + $center - 1;
	 $y = random(4) + $center - 1;

	 # そこが森か町でなければ、町を作る
	 if(($land[$x][$y] != $HlandTown) &&
	    ($land[$x][$y] != $HlandForest)) {
	     $land[$x][$y] = $HlandMountain;
	     $landValue[$x][$y] = 0; # 最初は採掘場なし
	     $count++;
	 }
    }

    # 基地を作る
    $count = 0;
    while($count < 1) {
	 # ランダム座標
	 $x = random(4) + $center - 1;
	 $y = random(4) + $center - 1;

	 # そこが森か町か山でなければ、基地
	 if(($land[$x][$y] != $HlandTown) &&
	    ($land[$x][$y] != $HlandForest) &&
	    ($land[$x][$y] != $HlandMountain)) {
	     $land[$x][$y] = $HlandBase;
	     $landValue[$x][$y] = 0;
	     $count++;
	 }
    }

    # ニュータウンを作る
    $count = 0;
    while($count < 1) {
	 # ランダム座標
	 $x = random(4) + $center - 1;
	 $y = random(4) + $center - 1;

	 # そこが森か町か山でなければ、基地
	 if(($land[$x][$y] != $HlandTown) &&
	    ($land[$x][$y] != $HlandForest) &&
	    ($land[$x][$y] != $HlandBase) &&
	    ($land[$x][$y] != $HlandMountain)) {
	     $land[$x][$y] = $HlandNewtown;
	     $landValue[$x][$y] = 10;
	     $count++;
	 }
    }

    # 大学を作る
    $count = 0;
    while($count < 1) {
	 # ランダム座標
	 $x = random(4) + $center - 1;
	 $y = random(4) + $center - 1;

	 # そこが森か町か山でなければ、基地
	 if(($land[$x][$y] != $HlandTown) &&
	    ($land[$x][$y] != $HlandForest) &&
	    ($land[$x][$y] != $HlandBase) &&
	    ($land[$x][$y] != $HlandNewtown) &&
	    ($land[$x][$y] != $HlandMountain)) {
	     $land[$x][$y] = $HlandCollege;
	     $landValue[$x][$y] = random(3);

	     $count++;
	 }
    }

    # 港を作る
    $count = 0;
    while($count < 1) {
	 # ランダム座標
	 $x = random(4) + $center - 1;
	 $y = random(4) + $center - 1;

	# 周りに陸があるかチェック
	my($seaCount) =
	    countAround($land, $x, $y, $HlandSea, 7);

        if($seaCount == 0) {

	 } else {
	 # そこが森か町か山でなければ、基地
	 if(($land[$x][$y] != $HlandTown) &&
	    ($land[$x][$y] != $HlandForest) &&
	    ($land[$x][$y] != $HlandBase) &&
	    ($land[$x][$y] != $HlandNewtown) &&
	    ($land[$x][$y] != $HlandCollege) &&
	    ($land[$x][$y] != $HlandMountain)) {
	     $land[$x][$y] = $HlandMinato;
	     $landValue[$x][$y] = 5;
	     $count++;
	 }
	 }
    }

    # 発電所を作る
    $count = 0;
    while($count < 1) {
	 # ランダム座標
	 $x = random(4) + $center - 1;
	 $y = random(4) + $center - 1;

	 # そこが森か町か山でなければ、基地
	 if(($land[$x][$y] != $HlandTown) &&
	    ($land[$x][$y] != $HlandForest) &&
	    ($land[$x][$y] != $HlandBase) &&
	    ($land[$x][$y] != $HlandNewtown) &&
	    ($land[$x][$y] != $HlandCollege) &&
	    ($land[$x][$y] != $HlandMinato) &&
	    ($land[$x][$y] != $HlandMountain)) {
	     $land[$x][$y] = $HlandEneWd;
	     $landValue[$x][$y] = 50;
	     $count++;
	 }
    }

    # 発電所を作る
    $count = 0;
    while($count < 1) {
	 # ランダム座標
	 $x = random(4) + $center - 1;
	 $y = random(4) + $center - 1;

	 # そこが森か町か山でなければ、基地
	 if(($land[$x][$y] != $HlandTown) &&
	    ($land[$x][$y] != $HlandForest) &&
	    ($land[$x][$y] != $HlandBase) &&
	    ($land[$x][$y] != $HlandNewtown) &&
	    ($land[$x][$y] != $HlandCollege) &&
	    ($land[$x][$y] != $HlandMinato) &&
	    ($land[$x][$y] != $HlandEneWd) &&
	    ($land[$x][$y] != $HlandMountain)) {
	     $land[$x][$y] = $HlandConden;
	     $landValue[$x][$y] = 100;

		if(random(100) < 10) {
	     	$land[$x][$y] = $HlandConden3;
	     	$landValue[$x][$y] = 0;
		}

	     $count++;
	 }
    }

    if($anothermood == 1) {
    # 発電所を作る
    $count = 0;
    while($count < 1) {
	 # ランダム座標
	 $x = random(4) + $center - 1;
	 $y = random(4) + $center - 1;

	 # そこが森か町か山でなければ、基地
	 if(($land[$x][$y] != $HlandTown) &&
	    ($land[$x][$y] != $HlandForest) &&
	    ($land[$x][$y] != $HlandBase) &&
	    ($land[$x][$y] != $HlandNewtown) &&
	    ($land[$x][$y] != $HlandCollege) &&
	    ($land[$x][$y] != $HlandMinato) &&
	    ($land[$x][$y] != $HlandEneWd) &&
	    ($land[$x][$y] != $HlandConden) &&
	    ($land[$x][$y] != $HlandConden3) &&
	    ($land[$x][$y] != $HlandMountain)) {
	     $land[$x][$y] = $HlandShuto;
	     $landValue[$x][$y] = 50;
	     $count++;
	 }
    }
    # 発電所を作る
    $count = 0;
    while($count < 1) {
	 # ランダム座標
	 $x = random(4) + $center - 1;
	 $y = random(4) + $center - 1;

	 # そこが森か町か山でなければ、基地
	 if(($land[$x][$y] != $HlandTown) &&
	    ($land[$x][$y] != $HlandForest) &&
	    ($land[$x][$y] != $HlandBase) &&
	    ($land[$x][$y] != $HlandNewtown) &&
	    ($land[$x][$y] != $HlandCollege) &&
	    ($land[$x][$y] != $HlandMinato) &&
	    ($land[$x][$y] != $HlandEneWd) &&
	    ($land[$x][$y] != $HlandConden) &&
	    ($land[$x][$y] != $HlandConden3) &&
	    ($land[$x][$y] != $HlandShuto) &&
	    ($land[$x][$y] != $HlandMountain)) {
	     $land[$x][$y] = $HlandHouse;
	     $landValue[$x][$y] = 0;
	     $count++;
	 }
    }
    }


    return (\@land, \@landValue);
}

#----------------------------------------------------------------------
# 情報変更モード
#----------------------------------------------------------------------
# メイン
sub changeMain {
    # idから島を取得
    $HcurrentNumber = $HidToNumber{$HcurrentID};
    my($island) = $Hislands[$HcurrentNumber];
    my($flag) = 0;

    # パスワードチェック
    if($HoldPassword eq $HspecialPassword) {
	# 特殊パスワード
	$island->{'money'} = 999999;
	$island->{'food'} = 99999;
    } elsif($HoldPassword eq $HshutoPassword) {
	$island->{'totoyoso2'} = htmlEscape($HcurrentOwnerName);
	$flag = 1;
    } elsif($HoldPassword eq $HomamoriPassword) {
	    $etc8 = $island->{'etc8'};
	    $etc8 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($toto1, $toto2, $toto3, $toto4, $toto5, $toto6, $toto7) = ($1, $2, $3, $4, $5, $6, $7);
	    $toto2++;
	    $island->{'etc8'} = "$toto1,$toto2,$toto3,$toto4,$toto5,$toto6,$toto7";
	$flag = 1;
    } elsif($HoldPassword eq $HijiriPassword) {
	$sthenko = htmlEscape($HcurrentOwnerName);

	if($sthenko eq id) {
	    rename("${HdirName}/island.$island->{'id'}", "${HdirName}/island.$HcurrentName");
	}

	    $eisei5 = $island->{'eisei5'};
	    $eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tetsub) = ($1, $2, $3, $4, $5, $6, $7);

	if($sthenko eq msexe) {
	    $island->{'eisei5'} = "$mshp,$msap,$msdp,$mssp,$mswin,$HcurrentName,$tetsub";
	} elsif($sthenko eq mshp) {
	    $island->{'eisei5'} = "$HcurrentName,$msap,$msdp,$mssp,$mswin,$msexe,$tetsub";
	} elsif($sthenko eq msap) {
	    $island->{'eisei5'} = "$mshp,$HcurrentName,$msdp,$mssp,$mswin,$msexe,$tetsub";
	} elsif($sthenko eq msdp) {
	    $island->{'eisei5'} = "$mshp,$msap,$HcurrentName,$mssp,$mswin,$msexe,$tetsub";
	} elsif($sthenko eq mssp) {
	    $island->{'eisei5'} = "$mshp,$msap,$msdp,$HcurrentName,$mswin,$msexe,$tetsub";
	} else {
	    $island->{"$sthenko"} = "$HcurrentName";
	}

	writeIslandsFile($HcurrentID);
	unlock();
	tempChange();
	return;
    } elsif($HoldPassword eq $HipPassword) {
	$island->{'ip0'} = 0;
	$island->{'ip1'} = 0;
	$island->{'ip2'} = 0;
	$island->{'ip3'} = 0;
	$island->{'ip4'} = 0;
	$island->{'ip5'} = 0;
	$island->{'ip6'} = 0;
	$island->{'ip7'} = 0;
	$island->{'ip8'} = 0;
	$island->{'ip9'} = 0;
	$flag = 1;
    } elsif(!checkPassword($island->{'password'},$HoldPassword)) {
	# password間違い
	unlock();
	tempWrongPassword();
	return;
    }

    # 確認用パスワード
    if($HinputPassword2 ne $HinputPassword) {
	# password間違い
	unlock();
	tempWrongPassword();
	return;
    }

    if($HcurrentName ne '') {
	# 名前変更の場合	
	# 名前が正当かチェック
	if($HcurrentName =~ /[,\?\(\)\<\>]|^無人$/) {
	    # 使えない名前
	    unlock();
	    tempNewIslandBadName();
	    return;
	}

	# 名前の重複チェック
	if(nameToNumber($HcurrentName) != -1) {
	    # すでに発見ずみ
	    unlock();
	    tempNewIslandAlready();
	    return;
	}

	if($island->{'money'} < $HcostChangeName) {
	    # 金が足りない
	    unlock();
	    tempChangeNoMoney();
	    return;
	}

	# 代金
	if($HoldPassword ne $HspecialPassword) {
	    $island->{'money'} -= $HcostChangeName;
	}

	# 名前を変更
	logChangeName($island->{'name'}, $HcurrentName);
	$island->{'name'} = $HcurrentName;
	$flag = 1;
    }

    # password変更の場合
    if($HinputPassword ne '') {
	# パスワードを変更
	$island->{'password'} = encode($HinputPassword);
	$flag = 1;
    }

    if($HcurrentOwnerName ne '') {
	$island->{'onm'} = htmlEscape($HcurrentOwnerName);
	$flag = 1;
    }

    if(($flag == 0) && ($HoldPassword ne $HspecialPassword)) {
	# どちらも変更されていない
	unlock();
	tempChangeNothing();
	return;
    }

    # データ書き出し
    writeIslandsFile($HcurrentID);
    unlock();

    # 変更成功
    tempChange();
}

sub changeOwner {
  # idから島を取得
  $HcurrentNumber = $HidToNumber{$HcurrentID};
  my($island) = $Hislands[$HcurrentNumber];
  my($flag) = 0;

  if(!checkPassword($island->{'password'},$HoldPassword)) {
    # password間違い
    unlock();
    tempWrongPassword();
    return;
  }
  # オーナー名を変更
  $island->{'ownername'} = htmlEscape($HcurrentOwnerName);
  $flag = 1;

  # データ書き出し
  writeIslandsOwner($HcurrentID);
  unlock();

  # 変更成功
  tempChange();
}

#----------------------------------------------------------------------
# ターン進行モード
#----------------------------------------------------------------------
# メイン
sub turnMain {
    # 最終更新時間を更新
    $HislandLastTime += $HunitTime;

    # ログファイルを後ろにずらす
    my($i, $j, $s, $d);
    for($i = ($HlogMax - 1); $i >= 0; $i--) {
	$j = $i + 1;
	my($s) = "${HdirName}/hakojima.log$i";
	my($d) = "${HdirName}/hakojima.log$j";
	unlink($d);
	rename($s, $d);
    }

    # 座標配列を作る
    makeRandomPointArray();

    # ターン番号
    $HislandTurn++;

    # 順番決め
    my(@order) = randomArray($HislandNumber);

    # 収入、消費フェイズ
    for($i = 0; $i < $HislandNumber; $i++) {

	estimate($order[$i]);
	income($Hislands[$order[$i]]);

	# ターン開始前の人口をメモる
	$Hislands[$order[$i]]->{'oldPop'} = $Hislands[$order[$i]]->{'pop'};
	$Hislands[$order[$i]]->{'oldMoney'} = $Hislands[$order[$i]]->{'money'};
	$Hislands[$order[$i]]->{'oldPts'} = $Hislands[$order[$i]]->{'pts'};
    }

    $island->{'Typhoonflag'} = 0;

    # コマンド処理
    for($i = 0; $i < $HislandNumber; $i++) {
	# 戻り値1になるまで繰り返し
	while(doCommand($Hislands[$order[$i]]) == 0){};
    }

    # 成長および単ヘックス災害
    for($i = 0; $i < $HislandNumber; $i++) {
	doEachHex($Hislands[$order[$i]]);
    }

    # 島全体処理
    my($remainNumber) = $HislandNumber;
    my($island);
    for($i = 0; $i < $HislandNumber; $i++) {
	$island = $Hislands[$order[$i]];
	doIslandProcess($order[$i], $island); 

	doIslandunemployed($order[$i], $island); 

    }

    if(($HislandTurn % 100) == 41) {
	islandSortHC();

	for($i = 0; $i < 8; $i++) {
	$island = $Hislands[$i];
	$eisei4 = $island->{'eisei4'};
	$eisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($sto, $std, $stk, $stwin, $stdrow, $stlose, $stwint, $stdrowt, $stloset, $styusho, $stshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);

	if($stshoka != 0) {

	$stshoka = 6;
	$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
	$stsin .= "$island->{'name'}島、";
	    }
	    }
	logHCsin($id, $name, $stsin);
    }

	islandSortPop();
            my($islandp) = $Hislands[0];
	islandSortFarm();
            my($islandfm) = $Hislands[0];
	islandSortFactory();
            my($islandfc) = $Hislands[0];
	islandSortMountain();
            my($islandm) = $Hislands[0];
	islandSortMonument();
            my($islandf) = $Hislands[0];
	islandSortLive();
            my($islandl) = $Hislands[0];
	islandSortRena();
            my($islandr) = $Hislands[0];
	islandSortKill();
            my($islandk) = $Hislands[0];
	islandSortFore();
            my($islandw) = $Hislands[0];
	islandSortTare();
            my($islandtare) = $Hislands[0];
	islandSortZipro();
            my($islandzipro) = $Hislands[0];
	islandSortLeje();
            my($islandleje) = $Hislands[0];
	islandSortForce();
            my($islandforce) = $Hislands[0];
	islandSortEisei2();
            my($islandeisei2) = $Hislands[0];
	islandSortUni();
            my($islanduni) = $Hislands[0];

	islandSorthck();
            my($islandhck) = $Hislands[0];
	islandSorthckt();
            my($islandhckt) = $Hislands[0];
	islandSorthcr();
            my($islandhcr) = $Hislands[0];
	islandSorthcy();
            my($islandhcy) = $Hislands[0];
	islandSorthct();
            my($islandhct) = $Hislands[0];

	    $islandp->{'bumon'} ++;
	    $islandfm->{'bumon'} ++;
	    $islandfc->{'bumon'} ++;
	    $islandm->{'bumon'} ++;
	    $islandf->{'bumon'} ++;
	    $islandl->{'bumon'} ++;
	    $islandr->{'bumon'} ++;
	    $islandk->{'bumon'} ++;
	    $islandw->{'bumon'} ++;
	    $islandtare->{'bumon'} ++;
	    $islandzipro->{'bumon'} ++;
	    $islandleje->{'bumon'} ++;
	    $islandforce->{'bumon'} ++;
	    $islandeisei2->{'bumon'} ++;
	    $islanduni->{'bumon'} ++;
	    $islandhck->{'bumon'} ++;
	    $islandhckt->{'bumon'} ++;
	    $islandhcr->{'bumon'} ++;
	    $islandhcy->{'bumon'} ++;
	    $islandhct->{'bumon'} ++;

    my($remainNumber) = $HislandNumber;
    my($island);
    for($i = 0; $i < $HislandNumber; $i++) {
	estimate($order[$i]);

	$island = $Hislands[$order[$i]];
	# 死滅判定
	if($island->{'dead'} == 1) {
	    $island->{'pop'} = 0;
	    $island->{'pts'} = 0;
	    $remainNumber--;
	} elsif($island->{'pop'} == 0) {
	    $island->{'dead'} = 1;
	    $island->{'pts'} = 0;
	    $remainNumber--;
	    # 死滅メッセージ
	    my($tmpid) = $island->{'id'};
	    logDead($tmpid, $island->{'name'});
	    unlink("island.$tmpid");
	}

    }

    if(($HislandTurn % $HturnPrizeUnit) == 0) {

	islandSortac4();

	my($island, $ii, $j);
	for($ii = 0; $ii < $HislandNumber; $ii++) {
	    $j = $ii + 1;
	    $island = $Hislands[$ii];
	    $auc0 = $island->{'auc0'};
	    $auc0 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($auc0a, $auc0b, $auc0c, $auc0d, $auc0e) = ($1, $2, $3, $4, $5);
	    $island->{'auc0'} = "$auc0a,$auc0b,$auc0c,$auc0d,$j";

		    $auc4 = $island->{'auc4'};
		    $auc4 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
		    ($auc4a, $auc4b, $auc4c) = ($1, $2, $3);

		if($ii == 0) {
		    $auc4a++;
		    $auc4b++;
			if($auc4b >= $aucshouhin) {
			    $auc4b = $aucshouhin;
			}
		    $island->{'auc4'} = "$auc4a,$auc4b,$auc4c";
		} else {
		    $island->{'auc4'} = "$auc4a,0,0";
		}

	}

	my($island) = $Hislands[0];
	    my($value, $str);
	    $value = $HislandTurn + random(1001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";

		    $str .= "/お守り1個";
		    $etc8 = $island->{'etc8'};
		    $etc8 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($toto1, $toto2, $toto3, $toto4, $toto5, $toto6, $toto7) = ($1, $2, $3, $4, $5, $6, $7);
		    $toto2+=1;
		    $island->{'etc8'} = "$toto1,$toto2,$toto3,$toto4,$toto5,$toto6,$toto7";

	    logPrizeAuc($island->{'id'}, $island->{'name'}, "$HislandTurn${Hprize[0]}", $str);

    }

    # 人口順にソート
    islandSort();

    # ターン杯対象ターンだったら、その処理
    if(($HislandTurn % $HturnPrizeUnit) == 0) {
	my($island) = $Hislands[0];
	    my($value, $str);
	    $value = $HislandTurn + random(1001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	logPrizet($island->{'id'}, $island->{'name'}, "$HislandTurn${Hprize[0]}", $str);
	    if($island->{'sin'} > 0) {
	    my($value, $str);
	    $value = $HislandTurn + random(1001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logSinMoney($island->{'id'}, $island->{'name'}, $str);
	    }
	    if($island->{'jin'} > 0) {
	    my($value, $str);
	    $value = $HislandTurn + random(1001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logJinMoney($island->{'id'}, $island->{'name'}, $str);
	    }
	$island->{'prize'} .= "${HislandTurn},";
    }

    if(($HislandTurn % $HturnPrizeUnit) == 0) {

	$auction1 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($shuppin1, $avalue1, $ajoutai1, $topvalue1, $topid1) = ($1, $2, $3, $4, $5);

	$shuppin = random(28)+1;
	    $value = 0;
	    if($shuppin == 9) {
		$value = 1 + random(5);
	    } elsif($shuppin == 10) {
		$value = 1000 + random(1500);
	    } elsif($shuppin == 11) {
		$value = 500 + random(1000);
	    } elsif($shuppin == 12) {
		$value = 2000 + random(2000);
	    } elsif($shuppin == 17) {
		$value = 500 + random(750);
	    } elsif($shuppin == 18) {
		$value = 300 + random(500);
	    } elsif($shuppin == 22) {
		$value = 1 + random(4);
	    } elsif($shuppin == 23) {
		$value = 1 + random(4);
	    } elsif($shuppin == 24) {
		$value = 1 + random(999);
	    } elsif($shuppin == 25) {
		$value = 80 + random(3);
	    } elsif($shuppin == 27) {
		$value = 500 + random(2000);
	    } elsif($shuppin == 28) {
		$value = 500 + random(2000);
	    }

	    $ajoutai = 0;

	    if(($aucflag1 < 90) && ($shuppin1 != 29)) {
		$shuppin = 29;
		$ajoutai = 15;
	    }

		$motone = random($shuppin);

	$auction1 = "$shuppin,$value,$ajoutai,$motone,0";


	$auction2 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($shuppin2, $avalue2, $ajoutai2, $topvalue2, $topid2) = ($1, $2, $3, $4, $5);

	$shuppin = random(28)+1;
	    $value = 0;
	    if($shuppin == 9) {
		$value = 1 + random(5);
	    } elsif($shuppin == 10) {
		$value = 1000 + random(1500);
	    } elsif($shuppin == 11) {
		$value = 500 + random(1000);
	    } elsif($shuppin == 12) {
		$value = 2000 + random(2000);
	    } elsif($shuppin == 17) {
		$value = 500 + random(750);
	    } elsif($shuppin == 18) {
		$value = 300 + random(500);
	    } elsif($shuppin == 22) {
		$value = 1 + random(4);
	    } elsif($shuppin == 23) {
		$value = 1 + random(4);
	    } elsif($shuppin == 24) {
		$value = 1 + random(999);
	    } elsif($shuppin == 25) {
		$value = 80 + random(3);
	    } elsif($shuppin == 27) {
		$value = 500 + random(2000);
	    } elsif($shuppin == 28) {
		$value = 500 + random(2000);
	    }

	    if($HislandNumber < 20) {
		$shuppin = 29;
	    }
	    if(random(1000) < 100-$HislandNumber+$oyasumiritu*25) {
		$shuppin = 29;
	    }

	    $ajoutai = 0;
	    if($shuppin == 29) {
		$ajoutai = 15;
	    }

	    if(($aucflag2 < 120) && ($shuppin2 != 29)) {
		$shuppin = 29;
		$ajoutai = 15;
	    }

		$motone = random($shuppin)*2;

	$auction2 = "$shuppin,$value,$ajoutai,$motone,0";


	$auction3 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($shuppin3, $avalue3, $ajoutai3, $topvalue3, $topid3) = ($1, $2, $3, $4, $5);

	$shuppin = random(28)+1;
	    $value = 0;
	    if($shuppin == 9) {
		$value = 1 + random(5);
	    } elsif($shuppin == 10) {
		$value = 1000 + random(1500);
	    } elsif($shuppin == 11) {
		$value = 500 + random(1000);
	    } elsif($shuppin == 12) {
		$value = 2000 + random(2000);
	    } elsif($shuppin == 17) {
		$value = 500 + random(750);
	    } elsif($shuppin == 18) {
		$value = 300 + random(500);
	    } elsif($shuppin == 22) {
		$value = 1 + random(4);
	    } elsif($shuppin == 23) {
		$value = 1 + random(4);
	    } elsif($shuppin == 24) {
		$value = 1 + random(999);
	    } elsif($shuppin == 25) {
		$value = 80 + random(3);
	    } elsif($shuppin == 27) {
		$value = 500 + random(2000);
	    } elsif($shuppin == 28) {
		$value = 500 + random(2000);
	    }

	    if($HislandNumber < 30) {
		$shuppin = 29;
	    }

	    if(random(1000) < $oyasumiritu*12.5) {
		$shuppin = 29;
	    }

	    $ajoutai = 0;
	    if($shuppin == 29) {
		$ajoutai = 15;
	    }

	    if(($aucflag3 < 60) && ($shuppin3 != 29)) {
		$shuppin = 29;
		$ajoutai = 15;
	    }

		$motone = random($shuppin);

	$auction3 = "$shuppin,$value,$ajoutai,$motone,0";
    }

    $auction1 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($shuppin1, $avalue1, $ajoutai1, $topvalue1, $topid1) = ($1, $2, $3, $4, $5);
	if($ajoutai1 < 15) {
	    $ajoutai1++;
	}
	if((($HislandTurn % $HturnPrizeUnit) > 74) && (random(100) < 5)) {
	    $ajoutai1 = 15;
	}
    $auction1 = "$shuppin1,$avalue1,$ajoutai1,$topvalue1,$topid1";

    $auction2 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($shuppin2, $avalue2, $ajoutai2, $topvalue2, $topid2) = ($1, $2, $3, $4, $5);
	if($ajoutai2 < 15) {
	    $ajoutai2++;
	}
	if((($HislandTurn % $HturnPrizeUnit) > 74) && (random(100) < 5)) {
	    $ajoutai2 = 15;
	}
    $auction2 = "$shuppin2,$avalue2,$ajoutai2,$topvalue2,$topid2";

    $auction3 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($shuppin3, $avalue3, $ajoutai3, $topvalue3, $topid3) = ($1, $2, $3, $4, $5);
	if($ajoutai3 < 15) {
	    $ajoutai3++;
	}
	if((($HislandTurn % $HturnPrizeUnit) > 74) && (random(100) < 5)) {
	    $ajoutai3 = 15;
	}
    $auction3 = "$shuppin3,$avalue3,$ajoutai3,$topvalue3,$topid3";

    # 島数カット
    $HislandNumber = $remainNumber;

##### ここから
    # toto の処理
    unless ($HislandTurn % $HturnPrizeUnit) {
      # ターン杯のターンなら

      # toto の正解を計算する
      my(@totoAns, $island);
      foreach $island (@Hislands[0..4, 9, 19, 29]) {
        push(@totoAns, (defined $island->{'id'} ? $island->{'id'} : '0'));
      }

      # 正解のログ作成
      logHistory("${HtagName_}第${HislandTurn}ターン ｔｏｔｏ${H_tagName} <B>： @totoAns</B>");

      # toto の的中判定をする
      my($allBet, @totoID);
      my(@totoBet, $i, $j, $n);
      for ($i = 0; $i < $HislandNumber; $i++) {
        $island = $Hislands[$i];
        next unless (@totoBet = ($island->{'eis8'} =~ /\(toto\@(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)\)/));

        # toto 購入希望なら
        my $betCost = 1000; # 購入費用 1000 億円
        if ($island->{'money'} < $betCost) {
          # 購入費用がない
          logNoMoney($island->{'id'}, $island->{'name'}, 'ｔｏｔｏ購入');
        } else {
          # 購入費用がある
          $island->{'money'} -= $betCost;
          $allBet += $betCost;

          # 的中点数の判定
          for ($n = 0, $j = 0; $j <= $#totoAns; $j++) {
            $n++ if ($totoAns[$j] == $totoBet[$j]);
          }

          # 購入結果を記憶
          $totoID[$n] .= "$i,";
        }
      }

      # 的中点数ごとの払い戻し率
      my @rate;
      $rate[8] = 20;
      $rate[7] =  8;
      $rate[6] =  2;

      # toto の払い戻しをする
      # （６点的中〜８点的中）
      my(@id, $bet);
      foreach $i (6..8) {
        if ($totoID[$i] ne '') {
          # 正解者がいる
          @id  = split(/,/, $totoID[$i]);
          $bet = int($allBet * $rate[$i] / ($#id + 1));

          # 配当金額のログ作成
          logHistory("${HtagName_}第${HislandTurn}ターン ｔｏｔｏ${H_tagName} ${i}点的中☆配当Auction補助金 $bet$HunitMoney");

          foreach $n (@id) {
            $island = $Hislands[$n];

		$auc9 = $island->{'auc9'};
		$auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);
		$auc9c += $bet;
		$auc9c2 = int($auc9c/10000);
		$auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
		$island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";

	    $totoget=$i-5;
            logOut("${HtagName_}$island->{'name'}島${H_tagName} ${HtagName_}ｔｏｔｏ${H_tagName} ${i}点的中！お守り${totoget}個ゲット！", $island->{'id'});

	    $etc8 = $island->{'etc8'};
	    $etc8 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($toto1, $toto2, $toto3, $toto4, $toto5, $toto6, $toto7) = ($1, $2, $3, $4, $5, $6, $7);
	    $toto1++;
	    $toto2+=$i-5;
	    $island->{'etc8'} = "$toto1,$toto2,$toto3,$toto4,$toto5,$toto6,$toto7";

          }
        } else {
          # 正解者がいない
          $rate[$i + 1] += $rate[$i]; # 予算を上位の等級に回す
        }
      }
    }
##### ここまで

    # HCtoto の処理

      if((($HislandTurn % 100) == 50) && (($yushouflag == 1) || ($yushouflag == 2))) {

      # toto の正解を計算する

      my @totoAns = ($yushounamber, $yushounamber2);

      # 正解のログ作成
      logHistory("${HtagName_}第${HislandTurn}ターン Hakoniwa Cup toto${H_tagName} <B>： @totoAns</B>");
      # toto の的中判定をする
      my($allBet, @totoID);
      my(@totoBet, $i, $j, $n);
      for ($i = 0; $i < $HislandNumber; $i++) {
        $island = $Hislands[$i];
        next unless (@totoBet = ($island->{'eis8'} =~ /\(hc\@(\d+)\.(\d+)\)/));

        # toto 購入希望なら
        my $betCost = 10000; # 購入費用 1000 億円
        if ($island->{'money'} < $betCost) {
          # 購入費用がない
          logNoMoney($island->{'id'}, $island->{'name'}, 'Hakoniwa Cup toto');
        } else {
          # 購入費用がある
          $island->{'money'} -= $betCost;
          $allBet += $betCost;

          # 的中点数の判定
          for ($n = 0, $j = 0; $j <= $#totoAns; $j++) {
            $n++ if ($totoAns[$j] == $totoBet[$j]);
          }

          # 購入結果を記憶
          $totoID[$n] .= "$i,";
        }
      }

      # 的中点数ごとの払い戻し率
      my @rate;
      $rate[2] = 10;
      $rate[1] =  3;

      # toto の払い戻しをする
      # （６点的中〜８点的中）
      my(@id, $bet);
      foreach $i (1..2) {
        if ($totoID[$i] ne '') {
          # 正解者がいる
          @id  = split(/,/, $totoID[$i]);
          $bet = int($allBet * $rate[$i] / ($#id + 1));

          # 配当金額のログ作成
          logHistory("${HtagName_}第${HislandTurn}ターン Hakoniwa Cup toto${H_tagName} ${i}点的中☆配当Auction補助金 $bet$HunitMoney");

          foreach $n (@id) {
            $island = $Hislands[$n];

		$auc9 = $island->{'auc9'};
		$auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);
		$auc9c += $bet;
		$auc9c2 = int($auc9c/10000);
		$auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
		$island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";

		if($i == 1) {
		    $totoget=1;
		}
		if($i == 2) {
		    $totoget=2;
		}

	    $etc8 = $island->{'etc8'};
	    $etc8 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($toto1, $toto2, $toto3, $toto4, $toto5, $toto6, $toto7) = ($1, $2, $3, $4, $5, $6, $7);
	    $toto1++;
	    $toto2+=$totoget;
	    $island->{'etc8'} = "$toto1,$toto2,$toto3,$toto4,$toto5,$toto6,$toto7";

            logOut("${HtagName_}$island->{'name'}島${H_tagName} ${HtagName_}Hakoniwa Cup toto${H_tagName} ${i}点的中！お守り${totoget}個ゲット！", $island->{'id'});

          }
        } else {
          # 正解者がいない
          $rate[$i + 1] += $rate[$i]; # 予算を上位の等級に回す
        }
      }
    }

##### ここまで

    # Numbers3 の処理

      if(($HislandTurn % 20) == 0) {

      # toto の正解を計算する
      my @totoAns = (random(999));

      # 正解のログ作成
      logHistory("${HtagName_}第${HislandTurn}ターン Numbers3${H_tagName} <B>： @totoAns</B>");

      # toto の的中判定をする
      my($allBet, @totoID);
      my(@totoBet, $i, $j, $n);
      for ($i = 0; $i < $HislandNumber; $i++) {
        $island = $Hislands[$i];
        next unless (@totoBet = ($island->{'eis8'} =~ /\(n3\@(\d+)\)/));

        # toto 購入希望なら
        my $betCost = 200; # 購入費用 200 億円
        if ($island->{'money'} < $betCost) {
          # 購入費用がない
          logNoMoney($island->{'id'}, $island->{'name'}, 'Numbers3購入');
        } else {
          # 購入費用がある
          $island->{'money'} -= $betCost;
          $allBet += $betCost;

          # 的中点数の判定
          for ($n = 0, $j = 0; $j <= $#totoAns; $j++) {
            $n++ if ($totoAns[$j] == $totoBet[$j]);
          }

          # 購入結果を記憶
          $totoID[$n] .= "$island->{'id'},";
        }
      }

      # 的中点数ごとの払い戻し率
      my @rate;
      $rate[1] = 100;

      # toto の払い戻しをする
      # （６点的中〜８点的中）
      my(@id, $bet);
      foreach $i (1) {
        if ($totoID[$i] ne '') {
          # 正解者がいる
          @id  = split(/,/, $totoID[$i]);
          $bet = int($allBet * $rate[$i] / ($#id + 1));

          # 配当金額のログ作成
          logHistory("${HtagName_}第${HislandTurn}ターン Numbers3${H_tagName} 的中☆配当金 $bet$HunitMoney");

          foreach $n (@id) {
            $island = $Hislands[$HidToNumber{$n}];
            $island->{'money'} += $bet;
            logOut("${HtagName_}$island->{'name'}島${H_tagName} ${HtagName_}Numbers3${H_tagName} 的中！", $n);
          }
        } else {
          # 正解者がいない
          $rate[$i + 1] += $rate[$i]; # 予算を上位の等級に回す
        }
      }
    }
##### ここまで

    # Numbers4 の処理

      if(($HislandTurn % 20) == 10) {

      # toto の正解を計算する
      my @totoAns = (random(9999));

      # 正解のログ作成
      logHistory("${HtagName_}第${HislandTurn}ターン Numbers4${H_tagName} <B>： @totoAns</B>");

      # toto の的中判定をする
      my($allBet, @totoID);
      my(@totoBet, $i, $j, $n);
      for ($i = 0; $i < $HislandNumber; $i++) {
        $island = $Hislands[$i];
        next unless (@totoBet = ($island->{'eis8'} =~ /\(n4\@(\d+)\)/));

        # toto 購入希望なら
        my $betCost = 200; # 購入費用 200 億円
        if ($island->{'money'} < $betCost) {
          # 購入費用がない
          logNoMoney($island->{'id'}, $island->{'name'}, 'Numbers4購入');
        } else {
          # 購入費用がある
          $island->{'money'} -= $betCost;
          $allBet += $betCost;

          # 的中点数の判定
          for ($n = 0, $j = 0; $j <= $#totoAns; $j++) {
            $n++ if ($totoAns[$j] == $totoBet[$j]);
          }

          # 購入結果を記憶
          $totoID[$n] .= "$island->{'id'},";
        }
      }

      # 的中点数ごとの払い戻し率
      my @rate;
      $rate[1] = 200;

      # toto の払い戻しをする
      # （６点的中〜８点的中）
      my(@id, $bet);
      foreach $i (1) {
        if ($totoID[$i] ne '') {
          # 正解者がいる
          @id  = split(/,/, $totoID[$i]);
          $bet = int($allBet * $rate[$i] / ($#id + 1));

          # 配当金額のログ作成
          logHistory("${HtagName_}第${HislandTurn}ターン Numbers4${H_tagName} 的中☆配当金 $bet$HunitMoney");

          foreach $n (@id) {
            $island = $Hislands[$HidToNumber{$n}];
            $island->{'money'} += $bet;
            logOut("${HtagName_}$island->{'name'}島${H_tagName} ${HtagName_}Numbers4${H_tagName} 的中！", $n);
          }
        } else {
          # 正解者がいない
          $rate[$i + 1] += $rate[$i]; # 予算を上位の等級に回す
        }
      }
    }
##### ここまで

    if(($HislandTurn % 100) == 0) {
    $stsanka = $stsanka - 1;
    logHC($id, $name, $stsanka);
    }

    if($AnkeitoOnOff == 0) {
	$an1 = 0;
	$an2 = 0;
	$an3 = 0;
	$an4 = 0;
	$an5 = 0;
    }

    # バックアップターンであれば、書く前にrename
    if(($HislandTurn % $HbackupTurn) == 0) {
	my($i);
	my($tmp) = $HbackupTimes - 1;
	myrmtree("${HdirName}.bak$tmp");
	for($i = ($HbackupTimes - 1); $i > 0; $i--) {
	    my($j) = $i - 1;
	    rename("${HdirName}.bak$j", "${HdirName}.bak$i");
	}
	rename("${HdirName}", "${HdirName}.bak0");
	mkdir("${HdirName}", $HdirMode);

	# ログファイルだけ戻す
	for($i = 0; $i <= $HlogMax; $i++) {
	    rename("${HdirName}.bak0/hakojima.log$i",
		   "${HdirName}/hakojima.log$i");
	}
	rename("${HdirName}.bak0/hakojima.his",
	       "${HdirName}/hakojima.his");
	rename("${HdirName}.bak0/hakojima.lhc",
	       "${HdirName}/hakojima.lhc");
	rename("${HdirName}.bak0/hakojima.auc",
	       "${HdirName}/hakojima.auc");
    }

    # ファイルに書き出し
    writeIslandsFile(-1);

    my($uti, $sti, $cuti, $csti) = times();
    $uti += $cuti;
    $sti += $csti;
    my($cpu) = $uti + $sti;
    logOut("<SMALL>負荷計測 CPU($cpu) : user($uti) system($sti) Ver.050309</SMALL>",0);

    # ログ書き出し
    logFlush();

    # 記録ログ調整
    logHistoryTrim();

    logHcupTrim();

    logAucTrim();

    # トップへ
    topPageMain();
}

# ディレクトリ消し
sub myrmtree {
    my($dn) = @_;
    opendir(DIN, "$dn/");
    my($fileName);
    while($fileName = readdir(DIN)) {
	unlink("$dn/$fileName");
    } 
    closedir(DIN);
    rmdir($dn);
}

# 収入、消費フェイズ
sub income {
    my($island) = @_;
    my($pop, $farm, $factory, $mountain) = 
	(      
	 $island->{'pop'},
	 $island->{'farm'} * 10,
	 $island->{'factory'},
	 $island->{'mountain'}
	 );

	$factory =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($factory1, $factory2, $co0, $co1, $htf, $shtf, $co95, $co95, $co95, $co95) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10);

    $island->{'incomemoney'} = 0;

    # 収入
    if($pop > $farm) {
	# 農業だけじゃ手が余る場合
	$island->{'food'} += $farm * ($island->{'co0'} + 1); # 農場フル稼働


	    if($factory2 * 10 > ($pop - $farm)) {

		    $auc9 = $island->{'auc9'};
		    $auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);

			$auc9c += int(($pop - $farm) / 10);

		    $auc9c2 = int($auc9c/10000);
		    $auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
		    $island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";

	    } else {

		    $auc9 = $island->{'auc9'};
		    $auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);

			$auc9c += $factory2;

		    if($island->{'shouhi'} > $island->{'ene'}) {

			$island->{'money'} +=
			    min(int(($pop - $farm - $factory2*10) / 20),
				 int(($factory1 + $mountain)/2));
			$island->{'incomemoney'} +=
			    min(int(($pop - $farm - $factory2*10) / 20),
				 int(($factory1 + $mountain)/2));
			logStarve2($island->{'id'}, $island->{'name'});
		    } else {
			$island->{'money'} +=
			    min(int(($pop - $farm - $factory2*10) / 10),
				 $factory1 + $mountain) * ($island->{'co1'} + 1);
			$island->{'incomemoney'} +=
			    min(int(($pop - $farm - $factory2*10) / 10),
				 $factory1 + $mountain) * ($island->{'co1'} + 1);
		    }

		    $auc9c2 = int($auc9c/10000);
		    $auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
		    $island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";
	    }

    } else {
	# 農業だけで手一杯の場合
	$island->{'food'} += $pop * ($island->{'co0'} + 1); # 全員野良仕事
    }

    # 食料消費
    $island->{'food'} = int(($island->{'food'}) - ($pop * $HeatenFood));
}


# コマンドフェイズ
sub doCommand {
    my($island) = @_;

    # コマンド取り出し
    my($comArray, $command);
    $comArray = $island->{'command'};
    $command = $comArray->[0]; # 最初のを取り出し
    slideFront($comArray, 0); # 以降を詰める

    # 各要素の取り出し
    my($kind, $target, $x, $y, $arg) = 
	(
	 $command->{'kind'},
	 $command->{'target'},
	 $command->{'x'},
	 $command->{'y'},
	 $command->{'arg'}
	 );

    # 導出値
    my($name) = $island->{'name'};
    my($id) = $island->{'id'};
    my($land) = $island->{'land'};
    my($landValue) = $island->{'landValue'};
    my($landKind) = $land->[$x][$y];
    my($lv) = $landValue->[$x][$y];
    my($cost) = $HcomCost[$kind];
    my($comName) = $HcomName[$kind];
    my($point) = "($x, $y)";
    my($landName) = landName($landKind, $lv);

	$jikkouarg = 0;

    if($kind == $HcomDoNothing) {
	# 資金繰り
	logDoNothing($id, $name, $comName);
	$island->{'money'} += 100;
	$island->{'money'} += random(100);
		    if(random(100) < 5) {
		    my($value, $str, $lName);
		    $lName = landName($landKind, $lv);
		    $value = 1+ random(1999);
		    $island->{'money'} += $value;
		    $str = "$value$HunitMoney";
	            # 収入ログ
	            logEnjo($id, $name, $lName, "($x, $y)", $str) if ($value > 0);
		    }
	$island->{'absent'} ++;
	
	# 自動放棄
	if($island->{'absent'} >= $HgiveupTurn) {
	    $comArray->[0] = {
		'kind' => $HcomGiveup,
		'target' => 0,
		'x' => 0,
		'y' => 0,
		'arg' => 0
	    }
	}
	return 1;
    }

    $island->{'absent'} = 0;

    if($anothermood == 1) {
	    if($kind == $HcomHouse) {
		$cost = $island->{'pts'}*2;
	    }
	    if($kind == $HcomKai) {
		$cost = $island->{'pts'}*2;
	    }
	    if($kind == $HcomBoku2) {
		$cost = $island->{'pts'}*4;
	    }
    } else {
	    if($kind == $HcomHouse) {
		$cost = $island->{'pts'}*3;
	    }
	    if($kind == $HcomBettown) {
		$cost = $island->{'pts'};
	    }
	    if($kind == $HcomKai) {
		$cost = $island->{'pts'};
	    }
	    if($kind == $HcomBoku2) {
		$cost = $island->{'pts'}*4;
	    }
    }

			        if($island->{'pts'} > $HouseLevel9) {
			 	    $costx = 2;
			        } elsif($island->{'pts'} > $HouseLevel8) {
			 	    $costx = 1.8;
			        } elsif($island->{'pts'} > $HouseLevel7) {
				    $costx = 1.8;
			        } elsif($island->{'pts'} > $HouseLevel6) {
			 	    $costx = 1.6;
			        } elsif($island->{'pts'} > $HouseLevel5) {
				    $costx = 1.6;
			        } elsif($island->{'pts'} > $HouseLevel4) {
			 	    $costx = 1.4;
			        } elsif($island->{'pts'} > $HouseLevel3) {
				    $costx = 1.4;
			        } elsif($island->{'pts'} > $HouseLevel2) {
			 	    $costx = 1.2;
			        } elsif($island->{'pts'} > $HouseLevel1) {
				    $costx = 1;
			        } else {
				    $costx = 1;
			        }

    if (($anothermood != 1) && ($kind != $HcomKura) && ($kind != $HcomKura2) && ($kind != $HcomKuraf) && ($kind != $HcomHouse) && ($kind != $HcomBettown) && ($kind != $HcomKai) && ($kind != $HcomBoku2) && ($kind != $HcomEneCs) && ($kind != $HcomEneNF) && ($kind != $HcomEisei) && ($kind != $HcomSell) && ($kind != $HcomMoney) && ($kind != $HcomFood) && ($kind != $HcomGivefood)) {
	$cost = $cost * $costx;
    }

    if (($island->{'htf'} > 0) && ($kind != $HcomKura) && ($kind != $HcomKura2) && ($kind != $HcomKuraf) && ($kind != $HcomSell) && ($kind != $HcomMoney) && ($kind != $HcomFood) && ($kind != $HcomGivefood)) {
	$cost = int($cost * 2 / 3);
    } elsif (($island->{'shtf'} > 0) && ($kind != $HcomKura) && ($kind != $HcomKura2) && ($kind != $HcomKuraf) && ($kind != $HcomSell) && ($kind != $HcomMoney) && ($kind != $HcomFood) && ($kind != $HcomGivefood)) {
	$cost = int($cost * 9 / 10);
    }

    $costco95 = 0.975**$island->{'co95'};

	    if($costco95 < 0.9) {
		$costco95 = 0.9;
	    }

    if (($island->{'co95'} > 0) && ($kind != $HcomKura) && ($kind != $HcomKura2) && ($kind != $HcomKuraf) && ($kind != $HcomSell) && ($kind != $HcomMoney) && ($kind != $HcomFood) && ($kind != $HcomGivefood)) {
	$cost = int($cost * $costco95);
    }

    $etc5 = $island->{'etc5'};
    $etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

    $costseisaku = $s01+$s03+$s05+$s07+$s09+$s11+$s13+$s15+$s17+$s19+$s21+$s23+$s25+$s27+$s29+$s02+$s04+$s06+$s08+$s10+$s12+$s14+$s16+$s18+$s20+$s22+$s24+$s26+$s28+$s30;
    $costseisaku2 = 0.9975**$costseisaku;

    if($costseisaku2 < 0.75) {
	$costseisaku2 = 0.75;
    }

    if (($s00 > 0) && ($kind != $HcomKura) && ($kind != $HcomKura2) && ($kind != $HcomKuraf) && ($kind != $HcomSell) && ($kind != $HcomMoney) && ($kind != $HcomFood) && ($kind != $HcomGivefood)) {
	$cost = int($cost * $costseisaku2);
    }

    $s12b = int($s12/5)+1;
    if($s12b > 10) {$s12b = 10;}

    $costmoney = $island->{'money'}/5/(999999*$s12b)+0.8;

    if (($kind != $HcomKura) && ($kind != $HcomKura2) && ($kind != $HcomKuraf) && ($kind != $HcomSell) && ($kind != $HcomMoney) && ($kind != $HcomFood) && ($kind != $HcomGivefood)) {
	$cost = int($cost * $costmoney);
    }

    # コストチェック
    if($cost > 0) {
	# 金の場合
	if($island->{'money'} < $cost) {
	if((($landKind == $HlandFarmchi) && ($kind == $HcomFarmcpc)) ||
	   (($landKind == $HlandFarmpic) && ($kind == $HcomFarmcpc)) ||
	   (($landKind == $HlandFarmcow) && ($kind == $HcomFarmcpc))) {
	} else {
	    logNoMoney($id, $name, $comName);
	    return 0;
	}
	}
    } elsif($cost < 0) {
	# 食料の場合
	if($island->{'food'} < (-$cost)) {
	    logNoFood($id, $name, $comName);
	    return 0;
	}
    }

    # コマンドで分岐
    if(($kind == $HcomPrepare) ||
       ($kind == $HcomPrepare2)) {
	# 整地、地ならし
	if(($landKind == $HlandSea) || 
	   ($landKind == $HlandSbase) ||
	   ($landKind == $HlandSeacity) ||
	   ($landKind == $HlandSeatown) ||
	   ($landKind == $HlandOil) ||
	   ($landKind == $HlandIce) ||
	   ($landKind == $HlandFune) ||
	   ($landKind == $HlandFrocity) ||
           ($landKind == $HlandNursery) ||
	   ($landKind == $HlandUmiamu) ||
	   ($landKind == $HlandGold) ||
	   ($landKind == $HlandRottenSea) ||
	   ($landKind == $HlandMountain) ||
	   ($landKind == $HlandUmishuto) ||
	   ($landKind == $HlandMonster)) {
	    # 海、海底基地、油田、山、怪獣は整地できない
	    logLandFail($id, $name, $comName, $landName, $point);
	    return 0;
	}

        if ((($landKind == $HlandMonument) && ($lv == 80)) ||
	    (($landKind == $HlandMonument) && ($lv == 81)) ||
	    (($landKind == $HlandMonument) && ($lv == 82)) ||
	    (($landKind == $HlandMonument) && ($lv == 83))) {
		$island->{'food'} += 20000; # 食べちゃえ
	}

        if ((($landKind == $HlandMonument) && ($lv == 74)) ||
	    (($landKind == $HlandMonument) && ($lv == 75)) ||
	    (($landKind == $HlandMonument) && ($lv == 76)) ||
	    (($landKind == $HlandMonument) && ($lv == 77)) ||
	    (($landKind == $HlandMonument) && ($lv == 78)) ||
	    (($landKind == $HlandMonument) && ($lv == 79))) {
		$island->{'money'} += 20000; # 宝石会社売却
	}

	# 目的の場所を平地にする
	$land->[$x][$y] = $HlandPlains;
	$landValue->[$x][$y] = 0;

	logLandSuc($id, $name, '整地', $point);

	# 金を差し引く
	$island->{'money'} -= $cost;

	if($kind == $HcomPrepare2) {
	    # 地ならし
	    $island->{'prepare2'}++;
	    
	    # ターン消費せず
	    return 0;
	} else {
	    # 整地なら、埋蔵金の可能性あり
	    if(random(1000) < $HdisMaizo) {
		my($v) = 100 + random(901);
		$island->{'money'} += $v;
		logMaizo($id, $name, $comName, $v);
	    }
	    return 1;
	}
    } elsif(($kind == $HcomReclaim) ||
	    ($kind == $HcomReclaim2) ||
	    ($kind == $HcomReclaim3)) {
	# 埋め立て
	if(($landKind != $HlandSea) &&
	   ($landKind != $HlandPlains) &&
	   ($landKind != $HlandPlains2) &&
	   ($landKind != $HlandWaste) &&
	   ($landKind != $HlandOil) &&
           ($landKind != $HlandNursery) &&
	   ($landKind != $HlandUmiamu) &&
	   ($landKind != $HlandSbase) &&
	   ($landKind != $HlandSeatown) &&
	   ($landKind != $HlandUmishuto) &&
	   ($landKind != $HlandSeacity)) {
	    # 海、海底基地、油田しか埋め立てできない
	    logLandFail($id, $name, $comName, $landName, $point);
	    return 0;
	}

	# 周りに陸があるかチェック
	my($seaCount) =
	    countAround($land, $x, $y, $HlandSea, 7) +
	    countAround($land, $x, $y, $HlandOil, 7) +
	    countAround($land, $x, $y, $HlandIce, 7) +
	    countAround($land, $x, $y, $HlandSbase, 7) +
	    countAround($land, $x, $y, $HlandFune, 7) +
	    countAround($land, $x, $y, $HlandFrocity, 7) +
            countAround($land, $x, $y, $HlandNursery, 7) +
	    countAround($land, $x, $y, $HlandUmiamu, 7) +
	    countAround($land, $x, $y, $HlandSeatown, 7) +
	    countAround($land, $x, $y, $HlandUmishuto, 7) +
            countAround($land, $x, $y, $HlandSeacity, 7);

        if(($seaCount == 7) &&
	   (($kind == $HcomReclaim)||($kind == $HcomReclaim3))) {
	    # 全部海だから埋め立て不能
	    logNoLandAround($id, $name, $comName, $point);
	    return 0;
	}

	if(($landKind == $HlandSea) && ($lv == 1)) {
	    # 浅瀬の場合
	    # 目的の場所を荒地にする
	    $land->[$x][$y] = $HlandWaste;
	    $landValue->[$x][$y] = 0;

		if($kind == $HcomReclaim3) {
		    $land->[$x][$y] = $HlandMountain;
		    $landValue->[$x][$y] = 0;
		}

	    logLandSuc($id, $name, $comName, $point);
	    $island->{'area'}++;

	    if($seaCount <= 4) {
		# 周りの海が3ヘックス以内なので、浅瀬にする
		my($i, $sx, $sy);

		for($i = 1; $i < 7; $i++) {
		    $sx = $x + $ax[$i];
		    $sy = $y + $ay[$i];

		    # 行による位置調整
		    if((($sy % 2) == 0) && (($y % 2) == 1)) {
			$sx--;
		    }

		    if(($sx < 0) || ($sx >= $HislandSize) ||
		       ($sy < 0) || ($sy >= $HislandSize)) {
		    } else {
			# 範囲内の場合
			if($land->[$sx][$sy] == $HlandSea) {
			    $landValue->[$sx][$sy] = 1;
			}
		    }
		}
	    }
	} elsif($landKind == $HlandPlains || $landKind == $HlandPlains2 || $landKind == $HlandWaste) {
	    # 海なら、目的の場所を浅瀬にする
	    $land->[$x][$y] = $HlandMountain;
	    $landValue->[$x][$y] = 0;
	    logLandSuc($id, $name, $comName, $point);
	} elsif(($kind == $HcomReclaim3) && ($landKind == $HlandSea) && ($lv == 1)) {
	    # 海なら、目的の場所を浅瀬にする
	    $land->[$x][$y] = $HlandMountain;
	    $landValue->[$x][$y] = 0;
	    logLandSuc($id, $name, $comName, $point);
	} elsif($kind == $HcomReclaim3) {
	    # 海なら、目的の場所を浅瀬にする
	    $land->[$x][$y] = $HlandWaste;
	    $landValue->[$x][$y] = 0;
	    logLandSuc($id, $name, $comName, $point);
	} else {
	    # 海なら、目的の場所を浅瀬にする
	    $land->[$x][$y] = $HlandSea;
	    $landValue->[$x][$y] = 1;
	    logLandSuc($id, $name, $comName, $point);
	}
	
	# 金を差し引く
	$island->{'money'} -= $cost;
	return 1;
    } elsif($kind == $HcomMinato) {
	# 港
	if(($landKind != $HlandSea) &&
	   ($landKind != $HlandOil) &&
	   ($landKind != $HlandSbase) &&
           ($landKind != $HlandNursery) &&
	   ($landKind != $HlandUmiamu) &&
	   ($landKind != $HlandSeatown) &&
	   ($landKind != $HlandUmishuto) &&
	   ($landKind != $HlandSeacity)) {
	    # 海、海底基地、油田しか埋め立てできない
	    logLandFail($id, $name, $comName, $landName, $point);
	    return 0;
	}

	# 周りに陸があるかチェック
	my($seaCount) =
	    countAround($land, $x, $y, $HlandSea, 7) +
	    countAround($land, $x, $y, $HlandOil, 7) +
	    countAround($land, $x, $y, $HlandIce, 7) +
	    countAround($land, $x, $y, $HlandSbase, 7) +
	    countAround($land, $x, $y, $HlandFune, 7) +
	    countAround($land, $x, $y, $HlandFrocity, 7) +
            countAround($land, $x, $y, $HlandNursery, 7) +
	    countAround($land, $x, $y, $HlandUmiamu, 7) +
	    countAround($land, $x, $y, $HlandSeatown, 7) +
	    countAround($land, $x, $y, $HlandUmishuto, 7) +
            countAround($land, $x, $y, $HlandSeacity, 7);

        if($seaCount == 7) {
	    # 全部海だから埋め立て不能
	    logNoLandAround($id, $name, $comName, $point);
	    return 0;
	}

	if(($landKind == $HlandSea) && ($lv == 1)) {
	    # 浅瀬の場合
	    # 目的の場所を荒地にする
	    $land->[$x][$y] = $HlandMinato;
	    $landValue->[$x][$y] = 0;
	    logLandSuc($id, $name, $comName, $point);
	    $island->{'area'}++;

	    if($seaCount <= 4) {
		# 周りの海が3ヘックス以内なので、浅瀬にする
		my($i, $sx, $sy);

		for($i = 1; $i < 7; $i++) {
		    $sx = $x + $ax[$i];
		    $sy = $y + $ay[$i];

		    # 行による位置調整
		    if((($sy % 2) == 0) && (($y % 2) == 1)) {
			$sx--;
		    }

		    if(($sx < 0) || ($sx >= $HislandSize) ||
		       ($sy < 0) || ($sy >= $HislandSize)) {
		    } else {
			# 範囲内の場合
			if($land->[$sx][$sy] == $HlandSea) {
			    $landValue->[$sx][$sy] = 1;
			}
		    }
		}
	    }
	} else {
	    # 海なら、目的の場所を浅瀬にする
	    $land->[$x][$y] = $HlandSea;
	    $landValue->[$x][$y] = 1;
	    logLandSuc($id, $name, $comName, $point);
	}
	
	# 金を差し引く
	$island->{'money'} -= $cost;
	return 1;

    } elsif($kind == $HcomFune) {
	# 船
	if(($landKind != $HlandSea) &&
	   ($landKind != $HlandOil) &&
	   ($landKind != $HlandSbase) &&
           ($landKind != $HlandNursery) &&
	   ($landKind != $HlandUmiamu) &&
	   ($landKind != $HlandSeatown) &&
	   ($landKind != $HlandUmishuto) &&
	   ($landKind != $HlandSeacity)) {
	    # 海、海底基地、油田しか埋め立てできない
	    logLandFail($id, $name, $comName, $landName, $point);
	    return 0;
	}

	# 周りに陸があるかチェック
	my($seaCount) =
	    countAround($land, $x, $y, $HlandMinato, 7);

        if($seaCount == 0) {
	    # 全部海だから埋め立て不能
	    logNoLandAroundm($id, $name, $comName, $point);
	    return 0;
	}

	if($landKind == $HlandSea) {
	    # 浅瀬の場合
	    # 目的の場所を荒地にする
			if($arg == 77) {
			$land->[$x][$y] = $HlandFrocity;
			$landValue->[$x][$y] = 1;
			# 金を差し引く
			$value = min($arg * ($cost), $island->{'money'});
			$island->{'money'} -= $value;
			logLandSuc($id, $name, $comName, $point);
			return 1;
			}

	    $land->[$x][$y] = $HlandFune;
		if(($arg >= $HfuneNumber) ||
		   ($arg == 0)) {
		    $arg = 1;
		}
		$landValue->[$x][$y] = $arg;
		logLandSuc($id, $name, $comName, $point);
			if(($arg == 1) ||
			   ($arg == 2) ||
			   ($arg == 5) ||
			   ($arg == 6) ||
			   ($arg == 11)) {
			    $island->{'gyo'}++;
			}

	} else {
	    logLandFail($id, $name, $comName, $landName, $point);
	    return 0;
	}
	
	# 金を差し引く
	$value = min($arg * ($cost), $island->{'money'});
	$island->{'money'} -= $value;
	return 1;

    } elsif($kind == $HcomSeki) {
	# 関所
	if(($landKind != $HlandSea) &&
	   ($landKind != $HlandOil) &&
	   ($landKind != $HlandSbase) &&
           ($landKind != $HlandNursery) &&
	   ($landKind != $HlandUmiamu) &&
	   ($landKind != $HlandSeatown) &&
	   ($landKind != $HlandUmishuto) &&
	   ($landKind != $HlandSeacity)) {
	    # 海、海底基地、油田しか埋め立てできない
	    logLandFail($id, $name, $comName, $landName, $point);
	    return 0;
	}

	my($seaCount) =
	    countAround($land, $x, $y, $HlandSea, 7) +
	    countAround($land, $x, $y, $HlandOil, 7) +
	    countAround($land, $x, $y, $HlandIce, 7) +
	    countAround($land, $x, $y, $HlandSbase, 7) +
	    countAround($land, $x, $y, $HlandFune, 7) +
	    countAround($land, $x, $y, $HlandFrocity, 7) +
            countAround($land, $x, $y, $HlandNursery, 7) +
	    countAround($land, $x, $y, $HlandUmiamu, 7) +
	    countAround($land, $x, $y, $HlandSeatown, 7) +
	    countAround($land, $x, $y, $HlandUmishuto, 7) +
            countAround($land, $x, $y, $HlandSeacity, 7);

	if(($landKind == $HlandSea) && ($lv == 1)) {
	    # 浅瀬の場合
	    # 目的の場所を荒地にする
	    $land->[$x][$y] = $HlandSeki;
	    $landValue->[$x][$y] = 0;
	    logLandSuc($id, $name, $comName, $point);
	    $island->{'area'}++;

	    if($seaCount <= 4) {
		# 周りの海が3ヘックス以内なので、浅瀬にする
		my($i, $sx, $sy);

		for($i = 1; $i < 7; $i++) {
		    $sx = $x + $ax[$i];
		    $sy = $y + $ay[$i];

		    # 行による位置調整
		    if((($sy % 2) == 0) && (($y % 2) == 1)) {
			$sx--;
		    }

		    if(($sx < 0) || ($sx >= $HislandSize) ||
		       ($sy < 0) || ($sy >= $HislandSize)) {
		    } else {
			# 範囲内の場合
			if($land->[$sx][$sy] == $HlandSea) {
			    $landValue->[$sx][$sy] = 1;
			}
		    }
		}
	    }
	} else {
	    # 海なら、目的の場所を浅瀬にする
	    logLandFail($id, $name, $comName, $landName, $point);
	    return 0;
	}
	
	# 金を差し引く
	$island->{'money'} -= $cost;
	return 1;

    } elsif(($kind == $HcomDestroy)||($kind == $HcomDestroy3)) {
	# 掘削
	if(($landKind == $HlandSbase) ||
	   ($landKind == $HlandSeacity) ||
	   ($landKind == $HlandSeatown) ||
	   ($landKind == $HlandOil) ||
	   ($landKind == $HlandFune) ||
	   ($landKind == $HlandFrocity) ||
           ($landKind == $HlandNursery) ||
	   ($landKind == $HlandUmiamu) ||
	   ($landKind == $HlandRottenSea) ||
	   ($landKind == $HlandUmishuto) ||
	   ($landKind == $HlandMonster)) {
	    # 海底基地、油田、怪獣は掘削できない
	    logLandFail($id, $name, $comName, $landName, $point);
	    return 0;
	}

	if(($landKind == $HlandSea) && ($lv == 0)) {
	    # 海なら、油田探し
	    # 投資額決定
	    if($arg == 0) { $arg = 1; }
	    my($value, $str, $p);
	    $value = min($arg * ($cost), $island->{'money'});
	    $str = "$value$HunitMoney";
	    $p = int($value / $cost);
	    $island->{'money'} -= $value;

	    # 見つかるか判定
            if($p > random(100) + $island->{'oil'} * 25) {
		# 油田見つかる
		logOilFound($id, $name, $point, $comName, $str);
		$land->[$x][$y] = $HlandOil;
		$landValue->[$x][$y] = 0;
		$island->{'oil'}++;

	    if($island->{'sin'} > 0) {
	    my($value, $str);
	    $value = random(1001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logSinMoney($id, $name, $str);
	    }
	    if($island->{'jin'} > 0) {
	    my($value, $str);
	    $value = random(1001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logJinMoney($id, $name, $str);
	    }

	    } else {
		# 無駄撃ちに終わる
		logOilFail($id, $name, $point, $comName, $str);
	    }
	    return 1;
	}

	# 目的の場所を海にする。山なら荒地に。浅瀬なら海に。
	if($landKind == $HlandMountain) {
	    $land->[$x][$y] = $HlandWaste;
	    $landValue->[$x][$y] = 0;
		if($kind == $HcomDestroy3) {
		    $land->[$x][$y] = $HlandSea;
		    $landValue->[$x][$y] = 1;
		}
	} elsif($landKind == $HlandGold) {
	    $land->[$x][$y] = $HlandWaste;
	    $landValue->[$x][$y] = 0;
		if($kind == $HcomDestroy3) {
		    $land->[$x][$y] = $HlandSea;
		    $landValue->[$x][$y] = 1;
		}
	} elsif($landKind == $HlandIce) {
	    $land->[$x][$y] = $HlandSea;
	    $landValue->[$x][$y] = 1;
		if($kind == $HcomDestroy3) {
		    $land->[$x][$y] = $HlandSea;
		    $landValue->[$x][$y] = 0;
		}
	} elsif($kind == $HcomDestroy3) {
	    $land->[$x][$y] = $HlandSea;
	    $landValue->[$x][$y] = 0;
	} elsif($landKind == $HlandSea) {
	    $landValue->[$x][$y] = 0;
	} else {
	    $land->[$x][$y] = $HlandSea;
	    $landValue->[$x][$y] = 1;
	    $island->{'area'}--;
	}
	logLandSuc($id, $name, $comName, $point);

	# 金を差し引く
	$island->{'money'} -= $cost;
	return 1;


    } elsif($kind == $HcomOnsen) {
	# 温泉掘削
	if($landKind != $HlandMountain) {
	    # 山以外は掘削できない
	    logLandFail($id, $name, $comName, $landName, $point);
	    return 0;
	}

	if(($landKind == $HlandMountain) && ($lv == 0)) {
	    # 山なら、温泉探し
	    # 投資額決定
	    if($arg == 0) { $arg = 1; }
	    my($value, $str, $p);
	    $value = min($arg * ($cost), $island->{'money'});
	    $str = "$value$HunitMoney";
	    $p = int($value / $cost);
	    $island->{'money'} -= $value;

	    # 見つかるか判定
	    if(random(10000) < $p * 15) {
		my($v) = 1000 + random(2001);
		$island->{'money'} += $v;
		$land->[$x][$y] = $HlandGold;
		$landValue->[$x][$y] = 1;
		logGold($id, $name, $comName, $v);

	    if($island->{'sin'} > 0) {
	    my($value, $str);
	    $value = random(1001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logSinMoney($id, $name, $str);
	    }
	    if($island->{'jin'} > 0) {
	    my($value, $str);
	    $value = random(1001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logJinMoney($id, $name, $str);
	    }

	    } elsif(random(1000) < 50) {
		logEggFound($id, $name, $comName, $value);
		$land->[$x][$y] = $HlandMonument;
		$eggnum = 80+random(3);
		$landValue->[$x][$y] = $eggnum;
	    } elsif((random(1000) < 50) && ($island->{'m84'} < 4)) {
		logIsekiFound($id, $name, $comName, $value);
		$land->[$x][$y] = $HlandMonument;
		$landValue->[$x][$y] = 84;
	    } elsif($p > random(100) + $island->{'hot'} * 30) {
		# 油田見つかる
		logHotFound($id, $name, $point, $comName, $str);
		$land->[$x][$y] = $HlandOnsen;
		$landValue->[$x][$y] = 1;
	    } else {
		# 無駄撃ちに終わる
		logHotFail($id, $name, $point, $comName, $str);
	    }

	    if(random(1000) < 15) {
		my($v) = 100 + random(901);
		$island->{'money'} += $v;
		logMaizo($id, $name, $comName, $v);
	    }

		# 金を差し引く
		$island->{'money'} -= $cost;
	    return 1;
	}

    } elsif($kind == $HcomSellTree) {
	# 伐採
	if($landKind != $HlandForest) {
	    # 森以外は伐採できない
	    logLandFail($id, $name, $comName, $landName, $point);
	    return 0;
	}

	# 目的の場所を平地にする
	$land->[$x][$y] = $HlandPlains;
	$landValue->[$x][$y] = 0;
	logLandSuc($id, $name, $comName, $point);
	    if(random(1000) < 75) {
		logEggFound($id, $name, $comName, $value);
		$land->[$x][$y] = $HlandMonument;
		$eggnum = 80+random(3);
		$landValue->[$x][$y] = $eggnum;
	    }

	# 売却金を得る
	$island->{'money'} += $HtreeValue * $lv;
	return 0;
    } elsif(($kind == $HcomPlant) ||
	    ($kind == $HcomFarm) ||
	    ($kind == $HcomEneAt) ||
	    ($kind == $HcomEneFw) ||
	    ($kind == $HcomEneWt) ||
	    ($kind == $HcomEneWd) ||
	    ($kind == $HcomEneBo) ||
	    ($kind == $HcomEneSo) ||
	    ($kind == $HcomEneCs) ||
	    ($kind == $HcomEneNF) ||
	    ($kind == $HcomConden) ||
	    ($kind == $HcomFoodim) ||
	    ($kind == $HcomFarmcpc) ||
	    ($kind == $HcomCollege) ||
	    ($kind == $HcomFactory) ||
	    ($kind == $HcomBase) ||
	    ($kind == $HcomMonument) ||
	    ($kind == $HcomHaribote) ||
	    ($kind == $HcomMonbuy) ||
	    ($kind == $HcomMonbuyt) ||
            ($kind == $HcomPark) ||
            ($kind == $HcomZoo) ||
            ($kind == $HcomMine) ||
            ($kind == $HcomNursery) ||
            ($kind == $HcomKyujo) ||
            ($kind == $HcomUmiamu) ||
            ($kind == $HcomNewtown) ||
            ($kind == $HcomRizort) ||
            ($kind == $HcomYoyaku) ||
            ($kind == $HcomYakusho) ||
            ($kind == $HcomKura) ||
            ($kind == $HcomKuraf) ||
            ($kind == $HcomKura2) ||
            ($kind == $HcomTrain) ||
	    ($kind == $HcomDbase)) {

	# 地上建設系
	if(!
	   (($landKind == $HlandPlains) ||
	    ($landKind == $HlandPlains2) ||
	    ($landKind == $HlandTown) ||
	    (($landKind == $HlandMinato) && ($kind == $HcomMinato)) ||
	    (($landKind == $HlandPark) && ($kind == $HcomPark)) ||
	    (($landKind == $HlandZoo) && ($kind == $HcomZoo)) ||
	    (($landKind == $HlandIce) && ($kind == $HcomPark)) ||
	    (($landKind == $HlandUmiamu) && ($kind == $HcomUmiamu)) ||
	    (($landKind == $HlandSea) && ($lv == 0) && ($kind == $HcomUmiamu)) ||
	    (($landKind == $HlandMonument) && ($kind == $HcomMonument)) ||
	    (($landKind == $HlandFarm) && ($kind == $HcomFarm)) ||
	    (($landKind == $HlandEneAt) && ($kind == $HcomEneAt)) ||
	    (($landKind == $HlandEneFw) && ($kind == $HcomEneFw)) ||
	    (($landKind == $HlandEneWt) && ($kind == $HcomEneWt)) ||
	    (($landKind == $HlandEneWd) && ($kind == $HcomEneWd)) ||
	    (($landKind == $HlandEneBo) && ($kind == $HcomEneBo)) ||
	    (($landKind == $HlandEneSo) && ($kind == $HcomEneSo)) ||
	    (($landKind == $HlandEneCs) && ($kind == $HcomEneCs)) ||
	    (($landKind == $HlandFarmchi) && ($kind == $HcomFarmcpc)) ||
	    (($landKind == $HlandFarmpic) && ($kind == $HcomFarmcpc)) ||
	    (($landKind == $HlandFarmcow) && ($kind == $HcomFarmcpc)) ||
	    (($landKind == $HlandCollege) && ($kind == $HcomCollege)) ||
	    (($landKind == $HlandFoodim) && ($kind == $HcomFoodim)) ||
	    (($landKind == $HlandFactory) && ($kind == $HcomFactory)) ||
            (($landKind == $HlandSea) && ($lv == 1) && ($kind == $HcomNursery)) ||
            (($landKind == $HlandCollege) && ($lv == 77) && ($kind == $HcomYakusho)) ||
            (($landKind == $HlandCollege) && ($lv == 78) && ($kind == $HcomYakusho)) ||
            (($landKind == $HlandCollege) && ($lv == 79) && ($kind == $HcomYakusho)) ||
            (($landKind == $HlandCollege) && ($lv == 80) && ($kind == $HcomYakusho)) ||
            (($landKind == $HlandNursery) && ($kind == $HcomNursery)) ||
            (($landKind == $HlandKura) && ($kind == $HcomKura)) ||
            (($landKind == $HlandKuraf) && ($kind == $HcomKuraf)) ||
            (($landKind == $HlandKura) && ($kind == $HcomKura2)) ||
            (($landKind == $HlandKuraf) && ($kind == $HcomKura2)) ||
	    (($landKind == $HlandTrain) && ($lv == 0) && ($kind == $HcomTrain)) ||
	    (($landKind == $HlandDefence) && ($kind == $HcomDbase)))) {
	    # 不適当な地形
	    logLandFail($id, $name, $comName, $landName, $point);
	    return 0;
	}

	# 種類で分岐
	if($kind == $HcomPlant) {
	    # 目的の場所を森にする。
	    $land->[$x][$y] = $HlandForest;
	    $landValue->[$x][$y] = 1; # 木は最低単位
	    logPBSuc($id, $name, $comName, $point);
	} elsif($kind == $HcomMonbuy) {
	    # 目的の場所を怪獣にする。
	    $kind = random($HmonsterLevel3) + 1;
	    $lv = $lv = ($kind << 4)
		+ $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
	    $land->[$x][$y] = $HlandMonster;
	    $landValue->[$x][$y] = $lv;
	    # 怪獣情報
	    my($mKind, $mName, $mHp) = monsterSpec($lv);
	    # メッセージ
	    logMonsFree($id, $name, $mName, $point);
	} elsif($kind == $HcomMonbuyt) {
	    # 目的の場所を怪獣にする。
	    $kind = 29;
	    $lv = $lv = ($kind << 4)
		+ $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
	    $land->[$x][$y] = $HlandMonster;
	    $landValue->[$x][$y] = $lv;
	    # 怪獣情報
	    my($mKind, $mName, $mHp) = monsterSpec($lv);
	    # メッセージ
	    logMonsFree($id, $name, $mName, $point);
	} elsif($kind == $HcomBase) {
	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}
	    # 目的の場所をミサイル基地にする。
	    $land->[$x][$y] = $HlandBase;
	    $landValue->[$x][$y] = 0; # 経験値0
	    logPBSuc($id, $name, $comName, $point);
	} elsif($kind == $HcomHaribote) {
	    # 目的の場所をハリボテにする
	    $land->[$x][$y] = $HlandHaribote;
	    $landValue->[$x][$y] = 0;
	    logHariSuc($id, $name, $comName, $HcomName[$HcomDbase], $point);
        } elsif($kind == $HcomPark) {
	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}
            # 目的の場所を遊園地にする
	    if($landKind == $HlandPark) {
		# すでに遊園地の場合
		$landValue->[$x][$y] += 30; # 規模 + 10000人
		if($landValue->[$x][$y] > 100) {
		    $landValue->[$x][$y] = 100; # 最大 100000人
		}
	    } elsif($landKind == $HlandIce) {
		# すでに遊園地の場合
		$landValue->[$x][$y] += 25; # 規模 + 10000人
		if($landValue->[$x][$y] > 100) {
		    $landValue->[$x][$y] = 100; # 最大 100000人
		}
	    } else {
		# 目的の場所を遊園地に
		$land->[$x][$y] = $HlandPark;
		$landValue->[$x][$y] = 10; # 規模 = 10000人
		$island->{'par'}++;
	    }
	    logLandSuc($id, $name, $comName, $point);
        } elsif($kind == $HcomZoo) {

        if ($arg > 30) {
            $arg = 30;
        }

	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}
            # 目的の場所を遊園地にする
	    if($landKind == $HlandZoo) {

		$etc6 = $island->{'etc6'};
		$etc6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		($z0,$z1,$z2,$z3,$z4,$z5,$z6,$z7,$z8,$z9,$z10,$z11,$z12,$z13,$z14,$z15,$z16,$z17,$z18,$z19,$z20,$z21,$z22,$z23,$z24,$z25,$z26,$z27,$z28,$z29,$z30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
		($z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);


		$nigekaiju = $arg;
		$nigeflag = 0;
	            if ($z->{"$nigekaiju"} > 0) {

			my($i, $sx, $sy, $kind, $lv);
			for($i = 1; $i < 7; $i++) {
			    $sx = $x + $ax[$i];
			    $sy = $y + $ay[$i];

			    # 行による位置調整
			    if((($sy % 2) == 0) && (($y % 2) == 1)) {
				$sx--;
			    }

			    $landKind = $land->[$sx][$sy];
			    $lv = $landValue->[$sx][$sy];
			    $point = "($sx, $sy)";

			    if(($sx < 0) || ($sx >= $HislandSize) ||
			       ($sy < 0) || ($sy >= $HislandSize)) {
			    } else {
				# 範囲内の場合
				$landKind = $land->[$sx][$sy];
				$lv = $landValue->[$sx][$sy];
				$point = "($sx, $sy)";
				if(($landKind == $HlandSea) ||
				   ($landKind == $HlandIce) ||
				   ($landKind == $HlandOil) ||
				   ($landKind == $HlandFune) ||
				   ($landKind == $HlandFrocity) ||
				   ($landKind == $HlandUmiamu) ||
				   ($landKind == $HlandSeacity) ||
				   ($landKind == $HlandSeatown) ||
				   ($landKind == $HlandMonster) ||
				   ($landKind == $HlandZoo) ||
				   ($landKind == $HlandUmishuto) ||
				   ($landKind == $HlandSbase)) {
				} else {
					if ($nigeflag < 1) {
						$nigeflag++;
						$z->{"$nigekaiju"} -= 1;
						$kind = $nigekaiju;
						$lv = $lv = ($kind << 4)
						+ $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
						$land->[$sx][$sy] = $HlandMonster;
						$landValue->[$sx][$sy] = $lv;
						my($mKind, $mName, $mHp) = monsterSpec($lv);
						logNige2($id, $name, landName($landKind, $lv), $mName, "($x, $y)");
						$island->{'etc6'} = "$z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}";
					}
				}
			    }
			}


				if ($nigeflag < 1) {
				    $kind = $nigekaiju;
				    $lv = ($kind << 4)
					+ $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
				    # どこに現れるか決める
				    my($bx, $by, $i);
				    for($i = 0; $i < $HpointNumber; $i++) {
					$bx = $Hrpx[$i];
					$by = $Hrpy[$i];
					if(($land->[$bx][$by] == $HlandTown) ||
					   ($land->[$bx][$by] == $HlandBigtown) ||
					   ($land->[$bx][$by] == $HlandBettown) ||
					   ($land->[$bx][$by] == $HlandSkycity) ||
					   ($land->[$bx][$by] == $HlandUmicity) ||
					   ($land->[$bx][$by] == $HlandRizort) ||
					   ($land->[$bx][$by] == $HlandKajino) ||
					   ($land->[$bx][$by] == $HlandBigRizort) ||
					   ($land->[$bx][$by] == $HlandNewtown)) {
			
					    # 地形名
					    my($lName) = landName($HlandTown, $landValue->[$bx][$by]);

					    # そのヘックスを怪獣に
					    $land->[$bx][$by] = $HlandMonster;
					    $landValue->[$bx][$by] = $lv;

					    $z->{"$nigekaiju"} -= 1;
					    $island->{'etc6'} = "$z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}";

					    # 怪獣情報
					    my($mKind, $mName, $mHp) = monsterSpec($lv);

					    # メッセージ
					    logMonsCome($id, $name, $mName, "($bx, $by)", $lName);
					    last;
					}
				    }
	            		}


	            }
			return 0;
	    } else {
		# 目的の場所を遊園地に
		$land->[$x][$y] = $HlandZoo;
		$landValue->[$x][$y] = 10; # 規模 = 10000人

		    if($island->{'zoo'} < 1) {
			my($first);
			$first = 1;
			while((random(5) != 0) || ($first == 1)) {
			    $first = 0;
			    $mKind = random(12);

			$etc6 = $island->{'etc6'};
			$etc6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
			($z0,$z1,$z2,$z3,$z4,$z5,$z6,$z7,$z8,$z9,$z10,$z11,$z12,$z13,$z14,$z15,$z16,$z17,$z18,$z19,$z20,$z21,$z22,$z23,$z24,$z25,$z26,$z27,$z28,$z29,$z30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
			($z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

			$z->{"$mKind"}++;
			$island->{'zoo'}++;
			$island->{'etc6'} = "$z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}";
			}
		    }

	    }
	    logLandSuc($id, $name, $comName, $point);
        } elsif($kind == $HcomMine) {
            # 目的の場所を地雷にする
            if ($arg == 0) {
                $arg = 1;
            } elsif ($arg > 9) {
                $arg = 9;
            }
            $arg = min($arg, int($island->{'money'} / $cost));
            $cost *= $arg;
            $land->[$x][$y] = $HlandMine;
            $landValue->[$x][$y] = $arg;
            logPBSuc($id, $name, $comName, $point);
        } elsif($kind == $HcomConden) {
            if ($arg == 0) {
                $arg = 1;
            } elsif ($arg >= 2) {
                $arg = 2;
            }
            $arg = min($arg, int($island->{'money'} / $cost));
            $cost *= $arg;
            if ($arg == 1) {
            $land->[$x][$y] = $HlandConden;
            } elsif ($arg == 2) {
            $land->[$x][$y] = $HlandConden2;
            }
            $landValue->[$x][$y] = 0;
            logLandSuc($id, $name, $comName, $point);
        } elsif($kind == $HcomTrain) {
	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}
            if ($arg > 9) {
                $arg = 0;
            }
            if(($landKind == $HlandTrain) && ($lv == 0) && ($arg == 1)) {
	            $landValue->[$x][$y] = 10;
            } elsif (($landKind == $HlandTrain) && ($lv == 0) && ($arg == 2)) {
	            $landValue->[$x][$y] = 20;
            } else {
		$land->[$x][$y] = $HlandTrain;
		$landValue->[$x][$y] = $arg;
            }
            logLandSuc($id, $name, $comName, $point);

        } elsif($kind == $HcomKura) {
            if ($arg == 0) {
                $arg = 1;
            }

	    $seq = int($lv/100);
	    $choki = $lv%100;
            $arg = min($arg, int($island->{'money'} / $cost));
            $cost *= $arg;

	    if($landKind == $HlandKura) {
		$choki += $arg;
		if($choki > 99) {
		    $choki = 99;
		}
		$landValue->[$x][$y] = $seq*100+$choki;
            } else {
		$land->[$x][$y] = $HlandKura;
		$landValue->[$x][$y] = $seq*100+$arg;
	    }

            logLandSuc($id, $name, $comName, $point);

        } elsif($kind == $HcomKuraf) {
	    if ($arg == 0) {
	        $arg = 1;
	    } elsif ($arg > 9) {
	        $arg = 9;
	    }

	    $choki = int($lv/10);
	    $kibo = $lv%10;
            $arg = min($arg, int($island->{'food'} / -$cost));
            $cost *= $arg;

	    if($landKind == $HlandKuraf) {
		$choki += $arg;
		if($choki > 400-40*(9-$kibo)) {
		    $choki = 400-40*(9-$kibo);
		}
		$landValue->[$x][$y] = $choki*10+$kibo;
            } else {
		$choki = 0;
		$kibo = 0;
		$land->[$x][$y] = $HlandKuraf;
		$landValue->[$x][$y] = $arg*10;
	    }
	    $island->{'food'} -= 10000*$arg;
            logLandSuc($id, $name, $comName, $point);

        } elsif($kind == $HcomKura2) {
            if ($arg == 0) {
                $arg = 1;
            }

	    $seq = int($lv/100);
	    $choki = $lv%100;
            if ($arg > $choki) {
                $arg = $choki;
            }
            $cost *= $arg;

	    if($landKind == $HlandKura) {
		$choki -= $arg;
		if($choki < 0) {
		    $choki = 0;
		}
		$landValue->[$x][$y] = $seq*100+$choki;
		$island->{'money'} += 10000*$arg;
		logLandSuc($id, $name, $comName, $point);
                return 0;

            } elsif($landKind == $HlandKuraf) {
		    if ($arg == 0) {
		        $arg = 1;
		    } elsif ($arg > 9) {
		        $arg = 9;
		    }
	    $choki = int($lv/10);
	    $kibo = $lv%10;
            if ($arg > $choki) {
                $arg = $choki;
            }
            $cost *= $arg;

		$choki -= $arg;
		if($choki < 0) {
		    $choki = 0;
		}
		$landValue->[$x][$y] = $choki*10+$kibo;
		$island->{'food'} += 10000*$arg;
		logLandSuc($id, $name, $comName, $point);
                return 0;

            } else {
                # 不適当な地形
                logLandFail($id, $name, $comName, $landName, $point);
                return 0;
	    }

        } elsif($kind == $HcomYoyaku) {
                $jikkouarg ++;
            $jikkouarg = min($jikkouarg, int($island->{'money'} / $cost));
            $cost *= $jikkouarg;
            $cost *= $jikkouarg;
            $land->[$x][$y] = $HlandPlains2;
            $landValue->[$x][$y] = 0;
            logLandSuc($id, $name, $comName, $point);
	    return 0;
        } elsif($kind == $HcomNursery) {
            # 養殖場
            if($landKind == $HlandNursery) {
                # すでに養殖場の場合
                $landValue->[$x][$y] += 5; # 規模 + 5000人
                if($landValue->[$x][$y] > 100) {
                    $landValue->[$x][$y] = 100; # 最大 100000人
                }
            } elsif(($landKind == $HlandSea) && ($lv == 1)) {
                # 目的の場所を養殖場に
                $land->[$x][$y] = $HlandNursery;
                $landValue->[$x][$y] = 20; # 規模 = 20000人
            } else {
                # 不適当な地形
                logLandFail($id, $name, $comName, $landName, $point);
                return 0;
            }
            logLandSuc($id, $name, $comName, $point);
        } elsif($kind == $HcomYakusho) {
	my($shutoCount) =
	    countAround($land, $x, $y, $HlandShuto, 7) +
	    countAround($land, $x, $y, $HlandUmishuto, 7);

	    if(($island->{'shu'} == 0) || ($shutoCount == 0)) {
		logJoFail($id, $name, $comName, $landName, $point);
		return 0;
	    }

            if(($landKind == $HlandCollege) && ($lv == 77) && ($costseisaku > 35)) {
		$land->[$x][$y] = $HlandCollege;
		$landValue->[$x][$y] = 78;
		logLandSuc($id, $name, $comName, $point);
            } elsif(($landKind == $HlandCollege) && ($lv == 78) && ($costseisaku > 60)) {
		$land->[$x][$y] = $HlandCollege;
		$landValue->[$x][$y] = 79;
		logLandSuc($id, $name, $comName, $point);
            } elsif(($landKind == $HlandCollege) && ($lv == 79) && ($costseisaku > 110)) {
		$land->[$x][$y] = $HlandCollege;
		$landValue->[$x][$y] = 80;
		logLandSuc($id, $name, $comName, $point);
            } elsif($landKind == $HlandCollege) {
		$land->[$x][$y] = $HlandCollege;
		$landValue->[$x][$y] = 77;
		logLandSuc($id, $name, $comName, $point);
            } else {
		$land->[$x][$y] = $HlandYakusho;
		$landValue->[$x][$y] = 0;
		logLandSuc($id, $name, $comName, $point);
            }

        } elsif($kind == $HcomKyujo) {
	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}
            # 目的の場所を野球場にする
            $land->[$x][$y] = $HlandKyujo;
            $landValue->[$x][$y] = 0;
            logLandSuc($id, $name, $comName, $point);
        } elsif($kind == $HcomNewtown) {
            # 目的の場所を野球場にする
            $land->[$x][$y] = $HlandNewtown;
            $landValue->[$x][$y] = 1;
            logLandSuc($id, $name, $comName, $point);
        } elsif($kind == $HcomRizort) {
	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}
            # 目的の場所を野球場にする
            $land->[$x][$y] = $HlandRizort;
            $landValue->[$x][$y] = 1;
            logLandSuc($id, $name, $comName, $point);
        } elsif($kind == $HcomUmiamu) {
	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}
            # 目的の場所を海あみゅにする
	    if($landKind == $HlandUmiamu) {
		# すでに海あみゅの場合
		$landValue->[$x][$y] += 30; # 規模 + 30000人
		if($landValue->[$x][$y] > 1000) {
		    $landValue->[$x][$y] = 1000; # 最大 1000000人
		}
	    } elsif(($landKind == $HlandSea) && ($lv == 0)) {
		# 目的の場所を海あみゅに
		$land->[$x][$y] = $HlandUmiamu;
		$landValue->[$x][$y] = 50; # 規模 = 50000人
            } else {
                # 不適当な地形
                logLandFail($id, $name, $comName, $landName, $point);
                return 0;
	    }
	    logLandSuc($id, $name, $comName, $point);
	} elsif($kind == $HcomFarm) {
	    # 農場
	    if($landKind == $HlandFarm) {
		# すでに農場の場合
		$landValue->[$x][$y] += 2; # 規模 + 2000人
		if($landValue->[$x][$y] > 50) {
		    $landValue->[$x][$y] = 50; # 最大 50000人
		}
	    } else {
		# 目的の場所を農場に
		$land->[$x][$y] = $HlandFarm;
		$landValue->[$x][$y] = 10; # 規模 = 10000人
	    }
	    logLandSuc($id, $name, $comName, $point);
	} elsif($kind == $HcomEneAt) {
	    if($landKind == $HlandEneAt) {
		$landValue->[$x][$y] += 30;
		if($landValue->[$x][$y] > 1500) {
		    $landValue->[$x][$y] = 1500;
		}
	    } else {
		$land->[$x][$y] = $HlandEneAt;
		$landValue->[$x][$y] = 50;
	    }
	    logLandSuc($id, $name, $comName, $point);
	} elsif($kind == $HcomEneFw) {

	my($seaCount) =
	    countAround($land, $x, $y, $HlandSea, 7) +
	    countAround($land, $x, $y, $HlandOil, 7) +
	    countAround($land, $x, $y, $HlandIce, 7) +
	    countAround($land, $x, $y, $HlandSbase, 7) +
	    countAround($land, $x, $y, $HlandFune, 7) +
	    countAround($land, $x, $y, $HlandFrocity, 7) +
            countAround($land, $x, $y, $HlandNursery, 7) +
	    countAround($land, $x, $y, $HlandUmiamu, 7) +
	    countAround($land, $x, $y, $HlandSeatown, 7) +
	    countAround($land, $x, $y, $HlandUmishuto, 7) +
            countAround($land, $x, $y, $HlandSeacity, 7);

	        if($seaCount == 0) {
		    # 全部海だから埋め立て不能
		    logNoLandArounde($id, $name, $comName, $point, "海");
		    return 0;
		}

	    if($landKind == $HlandEneFw) {
		$landValue->[$x][$y] += 30;
		if($landValue->[$x][$y] > 500) {
		    $landValue->[$x][$y] = 500;
		}
	    } else {
		$land->[$x][$y] = $HlandEneFw;
		$landValue->[$x][$y] = 20;
	    }
	    logLandSuc($id, $name, $comName, $point);
	} elsif($kind == $HcomEneWt) {

	my($mountainCount) =
	    countAround($land, $x, $y, $HlandMountain, 7) +
            countAround($land, $x, $y, $HlandGold, 7);

	        if($mountainCount == 0) {
		    # 全部海だから埋め立て不能
		    logNoLandArounde($id, $name, $comName, $point, "山");
		    return 0;
		}

	    if($landKind == $HlandEneWt) {
		$landValue->[$x][$y] += 15;
		if($landValue->[$x][$y] > 250) {
		    $landValue->[$x][$y] = 250;
		}
	    } else {
		$land->[$x][$y] = $HlandEneWt;
		$landValue->[$x][$y] = 10;
	    }
	    logLandSuc($id, $name, $comName, $point);
	} elsif($kind == $HcomEneWd) {

	my($PlainsCount) =
	    countAround($land, $x, $y, $HlandPlains, 7) +
            countAround($land, $x, $y, $HlandPlains2, 7);

	        if($PlainsCount == 0) {
		    # 全部海だから埋め立て不能
		    logNoLandArounde($id, $name, $comName, $point, "平地");
		    return 0;
		}

	    if($landKind == $HlandEneWd) {
		$landValue->[$x][$y] += 25;
		if($landValue->[$x][$y] > 150) {
		    $landValue->[$x][$y] = 150;
		}
	    } else {
		$land->[$x][$y] = $HlandEneWd;
		$landValue->[$x][$y] = 25;
	    }
	    logLandSuc($id, $name, $comName, $point);
	} elsif($kind == $HcomEneBo) {

	my($FoodimCount) = countAround($land, $x, $y, $HlandFoodim, 7);

	        if($FoodimCount == 0) {
		    # 全部海だから埋め立て不能
		    logNoLandArounde($id, $name, $comName, $point, "食物研究所");
		    return 0;
		}

	    if($landKind == $HlandEneBo) {
		$landValue->[$x][$y] += 50;
		if($landValue->[$x][$y] > 2000) {
		    $landValue->[$x][$y] = 2000;
		}
	    } else {
		$land->[$x][$y] = $HlandEneBo;
		$landValue->[$x][$y] = 100;
	    }
	    logLandSuc($id, $name, $comName, $point);
	} elsif($kind == $HcomEneCs) {

	        if($island->{'eis7'} == 0) {
	        logNesEisei($id, $name, $comName);
		    return 0;
		}

	    if($landKind == $HlandEneCs) {
		$landValue->[$x][$y] += 200;
		if($landValue->[$x][$y] > 4000) {
		    $landValue->[$x][$y] = 4000;
		}
	    } else {
		$land->[$x][$y] = $HlandEneCs;
		$landValue->[$x][$y] = 400;
	    }
	    logLandSuc($id, $name, $comName, $point);
	} elsif($kind == $HcomEneSo) {

	    if($landKind == $HlandEneSo) {
		$landValue->[$x][$y] += 1000;
		if($landValue->[$x][$y] > 1000) {
		    $landValue->[$x][$y] = 1000;
		}
	    } else {
		$land->[$x][$y] = $HlandEneSo;
		$landValue->[$x][$y] = 1000;
	    }
	    logLandSuc($id, $name, $comName, $point);
	} elsif($kind == $HcomEneNF) {
	    $etc9 = $island->{'etc9'};
	    $etc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($co7, $magicf, $magici, $magica, $magicw, $magicl, $magicd) = ($1, $2, $3, $4, $5, $6, $7);
	    if(($magica != $magicl) || ($magicl == 0) || ($island->{'con99'} > 0) || ($island->{'co77'} == 0)) {
		logEiseifail($id, $name, $comName, $point);
		# 広域被害ルーチン
		wideDamage($id, $name, $land, $landValue, $x, $y);
                return 0;
	    } else {
		$land->[$x][$y] = $HlandConden4;
		$landValue->[$x][$y] = 99;
	    }
	    logLandSuc($id, $name, $comName, $point);
	} elsif($kind == $HcomFoodim) {
	    if($landKind == $HlandFoodim) {
		# すでに農場の場合
		$landValue->[$x][$y] += 10; # 規模 + 10000人
		if($landValue->[$x][$y] > 500) {
		    $landValue->[$x][$y] = 500; # 最大 500000人
		}
	    } else {
		# 目的の場所を農場に
		$land->[$x][$y] = $HlandFoodim;
		$landValue->[$x][$y] = 30; # 規模 = 30000人
	    }
	    logLandSuc($id, $name, $comName, $point);
	} elsif($kind == $HcomCollege) {

	    if(($landKind == $HlandCollege) && ($lv == 4)) {
		$landValue->[$x][$y] = 96;
		logLandSuc($id, $name, $comName, $point);
                return 0;
	    } elsif(($landKind == $HlandCollege) && ($lv == 98)) {
		$landValue->[$x][$y] = 97;
		logLandSuc($id, $name, $comName, $point);
                return 0;
	    } elsif(($landKind == $HlandCollege) && ($lv == 96)) {
		$landValue->[$x][$y] = 4;
		logLandSuc($id, $name, $comName, $point);
                return 0;
	    } elsif(($landKind == $HlandCollege) && ($lv == 97)) {
		$landValue->[$x][$y] = 98;
		logLandSuc($id, $name, $comName, $point);
                return 0;
	    } elsif(($landKind == $HlandCollege) && ($lv == 6)) {
			if($island->{'money'} < 250000) {
			logNoMoney($id, $name, $comName);
			return 0;
			}
		$landValue->[$x][$y] = 95;
		$island->{'money'} -= 250000;
	    } elsif(($landKind == $HlandCollege) && ($lv == 95)) {
		$landValue->[$x][$y] = 6;
		$island->{'money'} += 250000;
		logLandSuc($id, $name, $comName, $point);
                return 0;
	    } else {
		$land->[$x][$y] = $HlandCollege;
	    if(random(100) < 30) {
		$landValue->[$x][$y] = 0;

		    if(random(100) < 40) {
			$landValue->[$x][$y] = 8;
		    }

	    } elsif(random(100) < 30) {
		$landValue->[$x][$y] = 1;

		    if(random(100) < 30) {
			$landValue->[$x][$y] = 7;
		    }

	    } elsif(random(100) < 25) {
		$landValue->[$x][$y] = 6;
	    } elsif(random(100) < 15) {
		$landValue->[$x][$y] = 2;
	    } elsif(random(100) < 15) {
		$landValue->[$x][$y] = 3;
	    } elsif(random(100) < 15) {
		$landValue->[$x][$y] = 4;
		if(($island->{'co4'} == 0) &&
		   ($island->{'co99'} == 0) &&
		   ($island->{'c28'} == 0)) {
		$island->{'eisei5'} = "3,5,5,5,0,0,0";
		}
	    } else {
		$landValue->[$x][$y] = 5;
	    }
	    }
	    logLandSuc($id, $name, $comName, $point);


		$etc5 = $island->{'etc5'};
		$etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

		$s10b = int($s10/5)+1;

		if(($island->{'co77'} > 0) && ($arg < 10) && ($arg != 0) && ($arg-1 < $s10b)) {
			if($arg == 0) {
			    $arg = 1;
			}
		$landValue->[$x][$y] = $arg-1;
		$island->{'money'} -= $arg * 10000;
			if(($arg == 4) &&
			   ($island->{'co4'} == 0) &&
		   	   ($island->{'co99'} == 0) &&
		   	   ($island->{'c28'} == 0)) {
			$island->{'eisei5'} = "3,5,5,5,0,0,0";
			}
		}

	} elsif($kind == $HcomFarmcpc) {
	    # 牧場
	    if(($arg >= 4) ||
	       ($arg == 0)) {
	        $arg = 1;
	    }
	    if(($landKind == $HlandFarmchi) ||
		($landKind == $HlandFarmpic) ||
		($landKind == $HlandFarmcow)) {
		# すでに牧場の場合
		if($landKind == $HlandFarmchi) {
		$island->{'money'} += $lv * 10;
		$land->[$x][$y] = $HlandFarmchi;
		$landValue->[$x][$y] = 1;
	        } elsif($landKind == $HlandFarmpic) {
		$island->{'money'} += $lv * 20;
		$land->[$x][$y] = $HlandFarmpic;
		$landValue->[$x][$y] = 1;
	        } elsif($landKind == $HlandFarmcow) {
		$island->{'money'} += $lv * 50;
		$land->[$x][$y] = $HlandFarmcow;
		$landValue->[$x][$y] = 1;
	        }
		logLandSuc($id, $name, $comName, $point);
	        $cost *= 0;
		return 0;
	    } else {
		if($arg == 1) {
		$land->[$x][$y] = $HlandFarmchi;
		$landValue->[$x][$y] = 1;
	        } elsif($arg == 2) {
		$land->[$x][$y] = $HlandFarmpic;
		$landValue->[$x][$y] = 1;
	        } elsif($arg == 3) {
		$land->[$x][$y] = $HlandFarmcow;
		$landValue->[$x][$y] = 1;
	        }
		# 金を差し引く
	        $arg = min($arg, int($island->{'money'} / $cost));
	        $cost *= $arg;
	    }
	    logLandSuc($id, $name, $comName, $point);
	} elsif($kind == $HcomFactory) {
	    # 工場
	    if($landKind == $HlandFactory) {
		# すでに工場の場合
		$landValue->[$x][$y] += 10; # 規模 + 10000人
		if($landValue->[$x][$y] > 100) {
		    $landValue->[$x][$y] = 100; # 最大 100000人
		}
	    } else {
		# 目的の場所を工場に
		$land->[$x][$y] = $HlandFactory;
		$landValue->[$x][$y] = 30; # 規模 = 10000人
	    }
	    logLandSuc($id, $name, $comName, $point);
	} elsif($kind == $HcomDbase) {
	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}
	    # 防衛施設
	    if($landKind == $HlandDefence) {
		# すでに防衛施設の場合
		$landValue->[$x][$y] = 1; # 自爆装置セット
		logBombSet($id, $name, $landName, $point);
	    } else {
		# 目的の場所を防衛施設に
		$land->[$x][$y] = $HlandDefence;
		$landValue->[$x][$y] = 0;
		logLandSuc($id, $name, $comName, $point);
	    }
	} elsif($kind == $HcomMonument) {
	    # 記念碑
	    if($landKind == $HlandMonument) {
		# すでに記念碑の場合
		# ターゲット取得
		my($tn) = $HidToNumber{$target};
		if($tn eq '') {
		    # ターゲットがすでにない
		    # 何も言わずに中止
		    return 0;
		}
		my($tIsland) = $Hislands[$tn];

                # 自島の人口が少ないか、目標島の人口が少ないなら、実行は許可されない
                if (($island->{'pop'} < $HguardPop) || ($tIsland->{'pop'} < $HguardPop)) {
                    logForbidden($id, $name, $comName);
                    return 0;
                }

		if($lovePeace == 1) {
		$island->{'bigmissile'}++;
		$island->{'money'} = 0;

		    my($i,$sx,$sy);
		    for($i = 0; $i < $HpointNumber; $i++){
			$sx = $Hrpx[$i];
			$sy = $Hrpy[$i];
		    if($land->[$sx][$sy] == $HlandSbase) {
				$land->[$sx][$sy] = $HlandSea;
				$landValue->[$sx][$sy] = 0;
		    } elsif(($land->[$sx][$sy] == $HlandBase) ||
			    ($land->[$sx][$sy] == $HlandMonument)) {
				$land->[$sx][$sy] = $HlandWaste;
				$landValue->[$sx][$sy] = 0;

		    }
		}
		logNiwaren($id, $name);

	        } else {
		$tIsland->{'bigmissile'}++;
	        }

		# その場所は荒地に
		$land->[$x][$y] = $HlandWaste;
		$landValue->[$x][$y] = 0;
		logMonFly($id, $name, $landName, $point);
	    } else {
		# 目的の場所を記念碑に
		$land->[$x][$y] = $HlandMonument;

		my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
		my $day = ('日','月','火','水','木','金','土')[$wday];
		$year = $year + 1900;
		$mon = $mon + 1;
		my $date = sprintf("%04d/%02d/%02d(%s) %02d:%02d:%02d",$year,$mon,$mday,$day,$hour,$min,$sec);

		if(($arg == 88) && ($mon > 2) && ($mon < 6)) {
		    $arg = 88;
		}

		elsif(($arg == 73) && ($mon > 2) && ($mon < 6)) {
		    $arg = 73;
		}

		elsif(($arg == 89) && ($mon > 5) && ($mon < 9)) {
		    $arg = 89;
		}

		elsif(($arg == 94) && ($mon > 5) && ($mon < 9)) {
		    $arg = 94;
		}

		elsif(($arg == 90) && ($mon > 8) && ($mon < 12)) {
		    $arg = 90;
		}

		elsif(($arg == 92) && ($mon > 11) && ($mon < 3)) {
		    $arg = 92;
		}

		elsif(($arg == 85) && ($mon == 12) && ($mday == 24)) {
		    $arg = 85;
		}

		elsif(($arg == 91) && ($mon == 12) && ($mday == 25)) {
		    $arg = 91;
		}

		elsif(($arg == 95) && ($mon == 12)) {
		    $arg = 95;
		}

		elsif($arg >= $HmonumentNumber) {
		    $arg = 0;
		}
		$landValue->[$x][$y] = $arg;
		logLandSuc($id, $name, $comName, $point);
	    }
	}

	# 金を差し引く
	$island->{'money'} -= $cost;

	# 回数付きなら、コマンドを戻す
	if(($kind == $HcomFarm) ||
           ($kind == $HcomFoodim) ||
           ($kind == $HcomNursery) ||
           ($kind == $HcomEneAt) ||
           ($kind == $HcomEneFw) ||
           ($kind == $HcomEneWt) ||
           ($kind == $HcomEneWd) ||
           ($kind == $HcomEneBo) ||
           ($kind == $HcomEneSo) ||
           ($kind == $HcomEneCs) ||
           ($kind == $HcomPark) ||
           ($kind == $HcomUmiamu) ||
	   ($kind == $HcomFactory)) {
	    if($arg > 1) {
		my($command);
		$arg--;
		slideBack($comArray, 0);
		$comArray->[0] = {
		    'kind' => $kind,
		    'target' => $target,
		    'x' => $x,
		    'y' => $y,
		    'arg' => $arg
		    };
	    }
	}

	return 1;
    } elsif($kind == $HcomMountain) {
	# 採掘場
            if($landKind == $HlandMountain) {
                # すでに採掘場の場合
                $landValue->[$x][$y] += 5; # 規模 + 5000人
                if($landValue->[$x][$y] > 200) {
                    $landValue->[$x][$y] = 200; # 最大 200000人
                }
            } elsif($landKind == $HlandGold) {
                # すでに金山の場合
                $landValue->[$x][$y] += 20; # 規模 + 20000人
                if($landValue->[$x][$y] > 200) {
                    $landValue->[$x][$y] = 200; # 最大 200000人
                }
            } else {
                # 不適当な地形
                logLandFail($id, $name, $comName, $landName, $point);
                return 0;
            }
            logLandSuc($id, $name, $comName, $point);

	# 金を差し引く
	$island->{'money'} -= $cost;
	if($arg > 1) {
	    my($command);
	    $arg--;
	    slideBack($comArray, 0);
	    $comArray->[0] = {
		'kind' => $kind,
		'target' => $target,
		'x' => $x,
		'y' => $y,
		'arg' => $arg
		};
	}

	    if(random(1000) < 9) {
		my($v) = 1000 + random(4001);
		$island->{'money'} += $v;
		$land->[$x][$y] = $HlandGold;
		logGold($id, $name, $comName, $v);

	    if($island->{'sin'} > 0) {
	    my($value, $str);
	    $value = random(1001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logSinMoney($id, $name, $str);
	    }
	    if($island->{'jin'} > 0) {
	    my($value, $str);
	    $value = random(1001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logJinMoney($id, $name, $str);
	    }

	    }

	return 1;

    } elsif($kind == $HcomHTget) {
	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}
	# ハイテク
            if($landKind == $HlandHTFactory) {
                # すでに採掘場の場合
                $landValue->[$x][$y] += 10; # 規模 + 10000人
                if($landValue->[$x][$y] > 500) {
                    $landValue->[$x][$y] = 500; # 最大 500000人
                }
            } elsif($landKind == $HlandFactory) {
			if($lv == 100) {
			    $land->[$x][$y] = $HlandHTFactory;
			} else {
			logJoFail($id, $name, $comName, $landName, $point);
			return 0;
			}
            } else {
                # 不適当な地形
                logLandFail($id, $name, $comName, $landName, $point);
                return 0;
            }
            logLandSuc($id, $name, $comName, $point);

	# 金を差し引く
	$island->{'money'} -= $cost;
	if($arg > 1) {
	    my($command);
	    $arg--;
	    slideBack($comArray, 0);
	    $comArray->[0] = {
		'kind' => $kind,
		'target' => $target,
		'x' => $x,
		'y' => $y,
		'arg' => $arg
		};
	}
	return 1;

	} elsif($kind == $HcomHouse) {
	    if($island->{'hou'} > 0) {
		$island->{'eisei1'} = $arg;
	        logLandSuc($id, $name, $comName, $point);
                return 0;

	    } else {
		if(!
		   (($landKind == $HlandPlains) ||
		    ($landKind == $HlandPlains2) ||
		    ($landKind == $HlandTown))) {
		    # 不適当な地形
		    logLandFail($id, $name, $comName, $landName, $point);
		    return 0;
		} else {
		if($arg == 0) {
		   $arg = 5;
		}
		$island->{'eisei1'} = $arg;
		$land->[$x][$y] = $HlandHouse;



	        if($island->{'pts'} > $HouseLevel9) {
		    $landValue->[$x][$y] = 9;
	        } elsif($island->{'pts'} > $HouseLevel8) {
	 	    $landValue->[$x][$y] = 8;
	        } elsif($island->{'pts'} > $HouseLevel7) {
		    $landValue->[$x][$y] = 7;
	        } elsif($island->{'pts'} > $HouseLevel6) {
	 	    $landValue->[$x][$y] = 6;
	        } elsif($island->{'pts'} > $HouseLevel5) {
		    $landValue->[$x][$y] = 5;
	        } elsif($island->{'pts'} > $HouseLevel4) {
	 	    $landValue->[$x][$y] = 4;
	        } elsif($island->{'pts'} > $HouseLevel3) {
		    $landValue->[$x][$y] = 3;
	        } elsif($island->{'pts'} > $HouseLevel2) {
	 	    $landValue->[$x][$y] = 2;
	        } elsif($island->{'pts'} > $HouseLevel1) {
		    $landValue->[$x][$y] = 1;
	        } else {
		    $landValue->[$x][$y] = 0;
	        }
		logLandSuc($id, $name, $comName, $point);
		# 金を差し引く
		$island->{'money'} -= $cost;
		return 1;
		}
	    }

	} elsif($kind == $HcomBettown) {
	my($shutoCount) =
	    countAround($land, $x, $y, $HlandShuto, 7) +
	    countAround($land, $x, $y, $HlandUmishuto, 7);
	my($betCount) =
	    countAround($land, $x, $y, $HlandBettown, 7);

		if($landKind != $HlandBigtown){
		    # 不適当な地形
		    logLandFail($id, $name, $comName, $landName, $point);
		    return 0;
		}

			if(($island->{'shu'} > 0) &&
			  (($shutoCount > 0) ||
			   ($betCount > 1))) {
			    $land->[$x][$y] = $HlandBettown;
			logLandSuc($id, $name, $comName, $point);
			# 金を差し引く
			$island->{'money'} -= $cost;
			return 1;
			} else {
			logJoFail($id, $name, $comName, $landName, $point);
			return 0;
			}

	} elsif($kind == $HcomKai) {
	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}
		if($landKind == $HlandKyujo) {

			if($island->{'ky2'} == 0) {
			$island->{'eisei4'} = "1,1,1,0,0,0,0,0,0,0,10";
			}

		$land->[$x][$y] = $HlandKyujokai;
		$landValue->[$x][$y] = 0;
			logLandSuc($id, $name, $comName, $point);
			# 金を差し引く
			$island->{'money'} -= $cost;
			return 1;
		} elsif($landKind == $HlandKyujokai) {
			$eisei4 = $island->{'eisei4'};
			$eisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
			($sto, $std, $stk, $stwin, $stdrow, $stlose, $stwint, $stdrowt, $stloset, $styusho, $stshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);
			$sto++;
			$std++;
			$stk++;
			$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
			logLandSuc($id, $name, $comName, $point);
			# 金を差し引く
			$island->{'money'} -= $cost;
			if($arg > 1) {
			    my($command);
			    $arg--;
			    slideBack($comArray, 0);
			    $comArray->[0] = {
				'kind' => $kind,
				'target' => $target,
				'x' => $x,
				'y' => $y,
				'arg' => $arg
				};
			}
			return 1;
		} elsif(($landKind == $HlandConden4) && ($lv == 2)) {
			$land->[$x][$y] = $HlandConden2;
			$landValue->[$x][$y] = 0;
			logLandSuc($id, $name, $comName, $point);
			# 金を差し引く
			$island->{'money'} -= $cost;
			return 1;
		} elsif(($landKind == $HlandConden4) && ($lv == 3)) {
			$land->[$x][$y] = $HlandConden3;
			$landValue->[$x][$y] = 0;
			logLandSuc($id, $name, $comName, $point);
			# 金を差し引く
			$island->{'money'} -= $cost;
			return 1;
		} elsif(($landKind == $HlandFune) && ($lv == 10)) {
			$landValue->[$x][$y] = 19;
			logLandSuc($id, $name, $comName, $point);
			# 金を差し引く
			$island->{'money'} -= $cost;
			return 1;
		} elsif(($landKind == $HlandFoodim) && ($lv >= 480)) {
			$land->[$x][$y] = $HlandFoodka;
			$landValue->[$x][$y] = 1;
			logLandSuc($id, $name, $comName, $point);
			# 金を差し引く
			$island->{'money'} -= $cost;
			return 1;
		} elsif($landKind == $HlandEneSo) {
			$landValue->[$x][$y] = 1250;
			logLandSuc($id, $name, $comName, $point);
			# 金を差し引く
			$island->{'money'} -= $cost;
			return 1;
		} elsif($landKind == $HlandZoo) {
			$landValue->[$x][$y] += 10;
			if($landValue->[$x][$y] > int($island->{'rena'}/75)) {
			    $landValue->[$x][$y] = int($island->{'rena'}/75);
			}
			if($landValue->[$x][$y] > 200) {
			    $landValue->[$x][$y] = 200;
			}
			logLandSuc($id, $name, $comName, $point);
			# 金を差し引く
			$island->{'money'} -= $cost;
			if($arg > 1) {
			    my($command);
			    $arg--;
			    slideBack($comArray, 0);
			    $comArray->[0] = {
				'kind' => $kind,
				'target' => $target,
				'x' => $x,
				'y' => $y,
				'arg' => $arg
				};
			}
			return 1;
		} elsif($landKind == $HlandDefence) {
			$landValue->[$x][$y] = 77;
			logLandSuc($id, $name, $comName, $point);
			# 金を差し引く
			$island->{'money'} -= $cost;
			return 1;
		} elsif($landKind == $HlandHTFactory) {
			$land->[$x][$y] = $HlandSHTF;
			logLandSuc($id, $name, $comName, $point);
			# 金を差し引く
			$island->{'money'} -= $cost;
			return 1;
		} elsif($landKind == $HlandSHTF) {
			$land->[$x][$y] = $HlandHTFactory;
			logLandSuc($id, $name, $comName, $point);
			# 金を差し引く
			$island->{'money'} -= $cost;
			return 1;
		} elsif($landKind == $HlandKura) {

		    $seq = int($lv/100);
		    $choki = $lv%100;
			$seq ++;
			if($seq > 9) {
			    $seq = 9;
			}
			$landValue->[$x][$y] = $seq*100+$choki;

			logLandSuc($id, $name, $comName, $point);
			# 金を差し引く
			$island->{'money'} -= $cost;
			if($arg > 1) {
			    my($command);
			    $arg--;
			    slideBack($comArray, 0);
			    $comArray->[0] = {
				'kind' => $kind,
				'target' => $target,
				'x' => $x,
				'y' => $y,
				'arg' => $arg
				};
			}
			return 1;

		} elsif($landKind == $HlandKuraf) {

		    $choki = int($lv/10);
		    $kibo = $lv%10;
			$kibo ++;
			if($kibo > 9) {
			    $kibo = 9;
			}
			$landValue->[$x][$y] = $choki*10+$kibo;

			logLandSuc($id, $name, $comName, $point);
			# 金を差し引く
			$island->{'money'} -= $cost;
			if($arg > 1) {
			    my($command);
			    $arg--;
			    slideBack($comArray, 0);
			    $comArray->[0] = {
				'kind' => $kind,
				'target' => $target,
				'x' => $x,
				'y' => $y,
				'arg' => $arg
				};
			}
			return 1;

		} elsif($landKind == $HlandRizort) {
		my($seaCount) =
		    countAround($land, $x, $y, $HlandSea, 7) +
		    countAround($land, $x, $y, $HlandOil, 7) +
		    countAround($land, $x, $y, $HlandIce, 7) +
		    countAround($land, $x, $y, $HlandSbase, 7) +
		    countAround($land, $x, $y, $HlandFune, 7) +
		    countAround($land, $x, $y, $HlandFrocity, 7) +
	            countAround($land, $x, $y, $HlandNursery, 7) +
		    countAround($land, $x, $y, $HlandUmiamu, 7) +
		    countAround($land, $x, $y, $HlandSeatown, 7) +
		    countAround($land, $x, $y, $HlandUmishuto, 7) +
	            countAround($land, $x, $y, $HlandSeacity, 7);
		my($rizortCount) =
		    countAround($land, $x, $y, $HlandRizort, 7) +
		    countAround($land, $x, $y, $HlandKajino, 7) +
		    countAround($land, $x, $y, $HlandBigRizort, 7);
            my($value);
            $value = $lv+$island->{'eis1'}+$island->{'eis2'}+$island->{'eis3'}+$island->{'eis5'}+int($island->{'fore'}/10)+int($island->{'rena'}/10)-$island->{'monsterlive'}*100;
			if(($seaCount > 1) &&
			   ($value > 500) &&
			   ($rizortCount > 2)) {
			    $land->[$x][$y] = $HlandBigRizort;
			logLandSuc($id, $name, $comName, $point);
			# 金を差し引く
			$island->{'money'} -= $cost;
			return 1;
			} else {
			logJoFail($id, $name, $comName, $landName, $point);
			return 0;
			}

		} elsif($landKind == $HlandBigRizort) {
			if($island->{'rena'} < 15000) {
			logJo2Fail($id, $name, $comName, $landName, $point);
			return 0;
			} else {
			$land->[$x][$y] = $HlandKajino;
			logLandSuc($id, $name, $comName, $point);
			# 金を差し引く
			$island->{'money'} -= $cost;
			return 1;
			}

		} else {
		    # 不適当な地形
		    logLandFail($id, $name, $comName, $landName, $point);
		    return 0;
		}

    } elsif($kind == $HcomSbase) {
	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}
	# 海底基地
	if(($landKind != $HlandSea) || ($lv != 0)){
	    # 海以外には作れない
	    logLandFail($id, $name, $comName, $landName, $point);
	    return 0;
	}

	$land->[$x][$y] = $HlandSbase;
	$landValue->[$x][$y] = 0; # 経験値0
	logLandSuc($id, $name, $comName, '(?, ?)');

	# 金を差し引く
	$island->{'money'} -= $cost;
	return 1;
    } elsif($kind == $HcomSeacity) {
	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}
	# 海底都市
	if(($landKind != $HlandSea) || ($lv != 0)){
	    # 海以外には作れない
	    logLandFail($id, $name, $comName, $landName, $point);
	    return 0;
	}

	$land->[$x][$y] = $HlandSeacity;
	$landValue->[$x][$y] = 0; # 人口0
	logLandSuc($id, $name, $comName, '(?, ?)');

	# 金を差し引く
	$island->{'money'} -= $cost;
	return 1;
    } elsif($kind == $HcomProcity) {
	# 防災化
	if(($landKind != $HlandTown) || ($lv != 100)){
	    # 海以外には作れない
	    logLandFail($id, $name, $comName, $landName, $point);
	    return 0;
	}

	$land->[$x][$y] = $HlandProcity;
	$landValue->[$x][$y] = 100; # 経験値0
	logLandSuc($id, $name, $comName, $point);

	# 金を差し引く
	$island->{'money'} -= $cost;
	return 1;
    } elsif($kind == $HcomBigtown) {
	# 現代化
	if(($landKind != $HlandNewtown) || ($lv < 149)){
	    # 海以外には作れない
	    logJoFail($id, $name, $comName, $landName, $point);
	    return 0;
	}
	my($townCount) =
	    countAround($land, $x, $y, $HlandTown, 19) +
	    countAround($land, $x, $y, $HlandProcity, 19) +
            countAround($land, $x, $y, $HlandNewtown, 19) +
	    countAround($land, $x, $y, $HlandBigtown, 19) +
	    countAround($land, $x, $y, $HlandBettown, 19) +
	    countAround($land, $x, $y, $HlandSkycity, 19) +
	    countAround($land, $x, $y, $HlandUmicity, 19) +
	    countAround($land, $x, $y, $HlandSeatown, 19) +
	    countAround($land, $x, $y, $HlandRizort, 19) +
	    countAround($land, $x, $y, $HlandKajino, 19) +
	    countAround($land, $x, $y, $HlandBigRizort, 19) +
	    countAround($land, $x, $y, $HlandShuto, 19) +
	    countAround($land, $x, $y, $HlandUmishuto, 19) +
	    countAround($land, $x, $y, $HlandMinato, 19) +
	    countAround($land, $x, $y, $HlandFrocity, 19) +
	    countAround($land, $x, $y, $HlandOnsen, 19) +
            countAround($land, $x, $y, $HlandSeacity, 19);
        if($townCount < 16) {
	    # 全部海だから埋め立て不能
	    logJoFail($id, $name, $comName, $landName, $point);
	    return 0;
	}

	$land->[$x][$y] = $HlandBigtown;
	logLandSuc($id, $name, $comName, $point);

	# 金を差し引く
	$island->{'money'} -= $cost;
	return 1;
    } elsif($kind == $HcomSeatown) {
	# 現代化
	if(($landKind != $HlandSeacity) || ($lv < 200)){
	    # 海以外には作れない
	    logJoFail($id, $name, $comName, $landName, '(?, ?)');
	    return 0;
	}
	my($townCount) =
	    countAround($land, $x, $y, $HlandTown, 19) +
	    countAround($land, $x, $y, $HlandProcity, 19) +
            countAround($land, $x, $y, $HlandNewtown, 19) +
	    countAround($land, $x, $y, $HlandBigtown, 19) +
	    countAround($land, $x, $y, $HlandBettown, 19) +
	    countAround($land, $x, $y, $HlandSkycity, 19) +
	    countAround($land, $x, $y, $HlandUmicity, 19) +
	    countAround($land, $x, $y, $HlandSeatown, 19) +
	    countAround($land, $x, $y, $HlandRizort, 19) +
	    countAround($land, $x, $y, $HlandKajino, 19) +
	    countAround($land, $x, $y, $HlandBigRizort, 19) +
	    countAround($land, $x, $y, $HlandShuto, 19) +
	    countAround($land, $x, $y, $HlandUmishuto, 19) +
	    countAround($land, $x, $y, $HlandMinato, 19) +
	    countAround($land, $x, $y, $HlandFrocity, 19) +
	    countAround($land, $x, $y, $HlandOnsen, 19) +
            countAround($land, $x, $y, $HlandSeacity, 19);
        if($townCount < 16) {
	    # 全部海だから埋め立て不能
	    logJoFail($id, $name, $comName, $landName, '(?, ?)');
	    return 0;
	}

	$land->[$x][$y] = $HlandSeatown;
	logLandSuc($id, $name, $comName, '(?, ?)');

	# 金を差し引く
	$island->{'money'} -= $cost;
	return 1;
    } elsif($kind == $HcomBoku) {
	# 僕の引越し
	if($landKind != $HlandProcity){
	    # 海以外には作れない
	    logBokuFail($id, $name, $comName, $landName, $point);
	    return 0;
	}

	# 周りに陸があるかチェック
	my($townCount) =
	    countAround($land, $x, $y, $HlandTown, 19);

        if($townCount == 0) {
	    # 全部海だから埋め立て不能
	    logNoTownAround($id, $name, $comName, $point);
	    return 0;
	}

	$landValue->[$x][$y] += 10; # 規模 + 1000人
	if($landValue->[$x][$y] > 200) {
	    $landValue->[$x][$y] = 200; # 最大 20000人
	}
	    my($i,$sx,$sy);
	    for($i = 1; $i < 19; $i++) {
	        $sx = $x + $ax[$i];
	        $sy = $y + $ay[$i];
	    if($land->[$sx][$sy] == $HlandTown){
	       $landValue->[$sx][$sy] -= int(20/$townCount);
			if($landValue->[$sx][$sy] <= 0) {
			    # 平地に戻す
			    $land->[$sx][$sy] = $HlandPlains;
			    $landValue->[$sx][$sy] = 0;
			    next;
			}
	    }
	    }
	logLandSuc($id, $name, $comName, $point);

	# 金を差し引く
	$island->{'money'} -= $cost;
	if($arg > 1) {
	    my($command);
	    $arg--;
	    slideBack($comArray, 0);
	    $comArray->[0] = {
		'kind' => $kind,
		'target' => $target,
		'x' => $x,
		'y' => $y,
		'arg' => $arg
		};
	}
	return 1;

    } elsif($kind == $HcomBoku2) {
	# 僕の引越し2

	if($landKind == $HlandMonster) {
	my($mKind, $mName, $mHp) = monsterSpec($landValue->[$x][$y]);
	my($special) = $HmonsterSpecial[$mKind];
	    logBokuFail2($id, $name, $comName, $mName, $point);
	return 0;
	}

	if((($landKind == $HlandPlains) || ($landKind == $HlandSea)) && ($island->{'stockflag'} == 55)) {
		$land->[$x][$y] = $island->{'stocklandkind'};
		$landValue->[$x][$y] = $island->{'stocklandvalue'};
		$island->{'pointb'} .= "($x, $y)";
		logLandSuc($id, $name, $comName, $island->{'pointb'});

		if($HislandSize > 16) {
		$sizekeisu = 5;
		} else {
		$sizekeisu = 1;
		}

		if(($island->{'stocklandkind'} == $HlandHouse) && ($island->{'stocklandvalue'} == 9) && ($island->{'co01'} > $sizekeisu) && ($island->{'co8'} > $sizekeisu)) {

		$island->{'condenmekki'} = 0;

                my($i, $sx, $sy, $kind, $lv);
                for($i = 1; $i < 7; $i++) {
                    $sx = $x + $ax[$i];
                    $sy = $y + $ay[$i];

                    # 行による位置調整
                    if((($sy % 2) == 0) && (($y % 2) == 1)) {
                        $sx--;
                    }
		    if(($sx < 0) || ($sx >= $HislandSize) ||
		       ($sy < 0) || ($sy >= $HislandSize)) {
		        # 範囲外
		        next;
		    }

                    $kind = $land->[$sx][$sy];
                    $lv   = $landValue->[$sx][$sy];
		    my($mKind, $mName, $mHp) = monsterSpec($lv);

		    if (($kind == $HlandMonster) && ($mKind == 14)) {
		    $island->{'condenmekki'} = 3;
		    }

		    }

		if ($island->{'condenmekki'} == 3) {

	                my($i, $sx, $sy, $kind, $lv);
	                for($i = 1; $i < 19; $i++) {
	                    $sx = $x + $ax[$i];
	                    $sy = $y + $ay[$i];

	                    # 行による位置調整
	                    if((($sy % 2) == 0) && (($y % 2) == 1)) {
	                        $sx--;
	                    }
			    if(($sx < 0) || ($sx >= $HislandSize) ||
			       ($sy < 0) || ($sy >= $HislandSize)) {
			        # 範囲外
			        next;
			    }

	                    $kind = $land->[$sx][$sy];
	                    $lv   = $landValue->[$sx][$sy];

	                    if ($kind == $HlandConden2) {
	                    $land->[$sx][$sy] = $HlandConden3;
	                    logConsFire($id, $name, landName($kind, $lv), "($sx, $sy)", $comName);
			    return 1;
			    }
			    }

		}

		}

		$island->{'money'} -= $cost;

	return 1;

	} elsif(($landKind == $HlandMountain) && ($island->{'stockflag'} == 55) && ((($island->{'stocklandkind'} == $HlandBettown) && ($island->{'stocklandvalue'} > 1500)) || (($island->{'stocklandkind'} == $HlandKajino) && ($island->{'stocklandvalue'} > 2000)))) {

		$land->[$x][$y] = $HlandSkycity;
		$landValue->[$x][$y] = $island->{'stocklandvalue'};
		$island->{'pointb'} .= "($x, $y)";
		logLandSuc($id, $name, $comName, $island->{'pointb'});

		$island->{'money'} -= $cost;

	return 1;

	} elsif(($landKind == $HlandFrocity) && ($island->{'stockflag'} == 55) && ((($island->{'stocklandkind'} == $HlandBettown) && ($island->{'stocklandvalue'} > 1500)) || (($island->{'stocklandkind'} == $HlandKajino) && ($island->{'stocklandvalue'} > 2000)))) {

		$land->[$x][$y] = $HlandUmicity;
		$landValue->[$x][$y] += $island->{'stocklandvalue'};
		$island->{'pointb'} .= "($x, $y)";
		logLandSuc($id, $name, $comName, $island->{'pointb'});

		$island->{'money'} -= $cost;

	return 1;

	} else {
		$island->{'stocklandkind'} = $land->[$x][$y];
		$island->{'stocklandvalue'} = $landValue->[$x][$y];
		$land->[$x][$y] = $HlandPlains;
		$landValue->[$x][$y] = 0;
		$island->{'pointb'} = "($x, $y)〜";
		$island->{'stockflag'} = 55;
	return 0;
	}


    } elsif($kind == $HcomAuction) {

	$auc6 = $island->{'auc6'};
	$auc6 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
	($auc6a, $auc6x, $auc6y) = ($1, $2, $3);

	$landKind = $land->[$x][$y];
	$lv = $landValue->[$x][$y];
	$aucland = $landKind * $lv;

	if($auc6a != 1) {
	    logMsNoEne3($id, $name, $comName);
	    return 0;
	}

	$auction1 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($shuppin1, $avalue1, $ajoutai1, $topvalue1, $topid1) = ($1, $2, $3, $4, $5);
	$auction2 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($shuppin2, $avalue2, $ajoutai2, $topvalue2, $topid2) = ($1, $2, $3, $4, $5);
	$auction3 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($shuppin3, $avalue3, $ajoutai3, $topvalue3, $topid3) = ($1, $2, $3, $4, $5);

	if($shuppin1 == 29) {
	    $island->{'auc6'} = "2,$x,$y";
	    $island->{'auc7'} = "$name島($x, $y)の$landName";
	    $auction1 = "30,$id,0,$arg,$aucland";
		$island->{'money'} -= $cost;
		logLandSuc($id, $name, $comName, $point);
		return 1;
	} elsif($shuppin2 == 29) {
	    $island->{'auc6'} = "2,$x,$y";
	    $island->{'auc7'} = "$name島($x, $y)の$landName";
	    $auction2 = "30,$id,0,$arg,$aucland";
		$island->{'money'} -= $cost;
		logLandSuc($id, $name, $comName, $point);
		return 1;
	} elsif($shuppin3 == 29) {
	    $island->{'auc6'} = "2,$x,$y";
	    $island->{'auc7'} = "$name島($x, $y)の$landName";
	    $auction3 = "30,$id,0,$arg,$aucland";
		$island->{'money'} -= $cost;
		logLandSuc($id, $name, $comName, $point);
		return 1;
	}

	    logMsNoEne4($id, $name, $comName);
	    return 0;

    } elsif($kind == $HcomGivefood) {
	# エサ
            if($landKind == $HlandMonster) {
	    my($mKind, $mName, $mHp) = monsterSpec($landValue->[$x][$y]);
	    my($special) = $HmonsterSpecial[$mKind];
		if($mHp < 10){$lv+=random(5);}
		$landValue->[$x][$y] = $lv;
            } elsif((($landKind == $HlandCollege) && ($lv == 4)) ||
		    (($landKind == $HlandCollege) && ($lv == 96)) ||
		    (($landKind == $HlandCollege) && ($lv == 97)) ||
		    (($landKind == $HlandCollege) && ($lv == 98))) {
		$eisei5 = $island->{'eisei5'};
		$eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tet) = ($1, $2, $3, $4, $5, $6, $7);
		    if(rand(100) < 30) {
		    $msap++;
		    } elsif (rand(100) < 30) {
		    $msdp++;
		    } elsif (rand(100) < 30) {
		    $mssp++;
		    } else {
		    $mshp++;
			if($mshp > 15){
			$mshp = 15;
			}
		    }
		    $island->{'eisei5'} = "$mshp,$msap,$msdp,$mssp,$mswin,$msexe,$tet";
            } else {
                # 不適当な地形
                logLandFail($id, $name, $comName, $landName, $point);
                return 0;
            }
            logLandSuc($id, $name, $comName, $point);

	# 金を差し引く
	$island->{'food'} += $cost;
	if($arg > 1) {
	    my($command);
	    $arg--;
	    slideBack($comArray, 0);
	    $comArray->[0] = {
		'kind' => $kind,
		'target' => $target,
		'x' => $x,
		'y' => $y,
		'arg' => $arg
		};
	}
	return 1;

    } elsif($kind == $HcomEisei) {

	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}

	if($arg == 99) {
	    $arg = 99;
	} elsif(($arg >= 7) ||
	   ($arg == 0)) {
	    $arg = 1;
	}
	if($arg == 1) {
	    if($island->{'m17'} < 1) {
		logNoRoke($id, $name, $comName, $point);
	    return 0;
	    }
	    if($island->{'rena'} < 10) {
		logNoTech($id, $name, $comName, $point);
	    return 0;
	    }
	    if(random(100) > 70+$island->{'rena'}) {
		logEiseifail($id, $name, $comName, $point);
		# 金を差し引く
		$value = min($arg * ($cost), $island->{'money'});
		$island->{'money'} -= $value;
	    return 1;
	    }
	   $island->{'eis1'} = 100;
	logLandSucmini($id, $name, $comName, $point);
	}
	if($arg == 2) {
	    if($island->{'m17'} < 1) {
		logNoRoke($id, $name, $comName, $point);
	    return 0;
	    }
	    if($island->{'rena'} < 40) {
		logNoTech($id, $name, $comName, $point);
	    return 0;
	    }
	    if(random(100) > 50+$island->{'rena'}) {
		logEiseifail($id, $name, $comName, $point);
		# 金を差し引く
		$value = min($arg * ($cost), $island->{'money'});
		$island->{'money'} -= $value;
	    return 1;
	    }
	   $island->{'eis2'} = 100;
	logLandSucmini($id, $name, $comName, $point);
	}
	if($arg == 3) {
	    if($island->{'m17'} < 2) {
		logNoRoke($id, $name, $comName, $point);
	    return 0;
	    }
	    if($island->{'rena'} < 100) {
		logNoTech($id, $name, $comName, $point);
	    return 0;
	    }
	    if(random(1000) > 600+$island->{'rena'}) {
		logEiseifail($id, $name, $comName, $point);
		# 金を差し引く
		$value = min($arg * ($cost), $island->{'money'});
		$island->{'money'} -= $value;
	    return 1;
	    }
	   $island->{'eis3'} = 100;
	logLandSucmini($id, $name, $comName, $point);
	}
	if($arg == 4) {
	    if($island->{'m17'} < 3) {
		logNoRoke($id, $name, $comName, $point);
	    return 0;
	    }
	    if($island->{'rena'} < 250) {
		logNoTech($id, $name, $comName, $point);
	    return 0;
	    }
	    if(random(1000) > 400+$island->{'rena'}) {
		logEiseifail($id, $name, $comName, $point);
		# 金を差し引く
		$value = min($arg * ($cost), $island->{'money'});
		$island->{'money'} -= $value;
	    return 1;
	    }
	   $island->{'eis4'} = 100;
	logLandSucmini($id, $name, $comName, $point);
	}
	if($arg == 5) {
	    if($island->{'m17'} < 4) {
		logNoRoke($id, $name, $comName, $point);
	    return 0;
	    }
	    if($island->{'rena'} < 1000) {
		logNoTech($id, $name, $comName, $point);
	    return 0;
	    }
	    if(random(1000) > 200+$island->{'rena'}) {
		logEiseifail($id, $name, $comName, $point);
		# 金を差し引く
		$value = min($arg * ($cost), $island->{'money'});
		$island->{'money'} -= $value;
	    return 1;
	    }
	   $island->{'eis5'} = 100;
	logLandSucmini($id, $name, $comName, $point);
	}
	if($arg == 6) {
	    if($island->{'m17'} < 10) {
		logNoRoke($id, $name, $comName, $point);
	    return 0;
	    }
	    if($island->{'rena'} < 2000) {
		logNoTech($id, $name, $comName, $point);
	    return 0;
	    }
	    if(random(10000) > 3000+$island->{'rena'}) {
		logEiseifail($id, $name, $comName, $point);
		# 金を差し引く
		$value = min($arg * ($cost), $island->{'money'});
		$island->{'money'} -= $value;
	    return 1;
	    }
	   $island->{'eis6'} = 250;
	logLandSucmini($id, $name, $comName, $point);
	}
	if($arg == 99) {
	    if($island->{'money'} < 1000000) {
		logNoMoney($id, $name, $comName);
		return 0;
	    }
	    if($island->{'m17'} < 10) {
		logNoRoke($id, $name, $comName, $point);
	    return 0;
	    }
	    if($island->{'rena'} < 5000) {
		logNoTech($id, $name, $comName, $point);
	    return 0;
	    }
	    if(random(10000) > 3000+$island->{'rena'}) {
		logEiseifail($id, $name, $comName, $point);
		# 金を差し引く
		$island->{'money'} -= 1000000;
	    return 1;
	    }
	   $island->{'eis7'} = 124;
	logLandSucmini($id, $name, $comName, $point);
	$island->{'money'} -= 1000000;
	return 1;
	}
	
	# 金を差し引く
	$value = min($arg * ($cost), $island->{'money'});
	$island->{'money'} -= $value;
	return 1;
    } elsif($kind == $HcomEiseimente) {

	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}

	if($arg == 99) {
	    $arg = 99;
	} elsif(($arg >= 6) ||
	   ($arg == 0)) {
	    $arg = 1;
	}
	if($arg == 1) {
	    if($island->{'eis1'} >= 1) {
	       $island->{'eis1'} = 150;
		logLandSucmini($id, $name, $comName, $point);
	    } else {
	    logNoEisei($id, $name, $comName);
		return 0;
	    }
	}
	if($arg == 2) {
	    if($island->{'eis2'} >= 1) {
	       $island->{'eis2'} = 150;
		logLandSucmini($id, $name, $comName, $point);
	    } else {
	    logNoEisei($id, $name, $comName);
		return 0;
	    }
	}
	if($arg == 3) {
	    if($island->{'eis3'} >= 1) {
	       $island->{'eis3'} = 150;
		logLandSucmini($id, $name, $comName, $point);
	    } else {
	    logNoEisei($id, $name, $comName);
		return 0;
	    }
	}
	if($arg == 4) {
	    if($island->{'eis4'} >= 1) {
	       $island->{'eis4'} = 150;
		logLandSucmini($id, $name, $comName, $point);
	    } else {
	    logNoEisei($id, $name, $comName);
		return 0;
	    }
	}
	if($arg == 5) {
	    if($island->{'eis5'} >= 1) {
	       $island->{'eis5'} = 150;
		logLandSucmini($id, $name, $comName, $point);
	    } else {
	    logNoEisei($id, $name, $comName);
		return 0;
	    }
	}
	if($arg == 99) {
	    $eis7 = $island->{'eis7'};
	    $cstpop = int($eis7/100);
	    $csten = $eis7%100;
	    if($csten >= 1) {
	       $csten += 25;

	    if($csten > 99) {
		$csten = 99;
		$cstpop+=100;
	    }
		logLandSucmini($id, $name, $comName, $point);
	       $island->{'eis7'} = $cstpop*100+$csten;
	    } else {
	    logNoEisei($id, $name, $comName);
		return 0;
	    }
	}
	
	# 金を差し引く
	$island->{'money'} -= $cost;
	return 1;

    } elsif($kind == $HcomEiseiAtt) {
	if($arg == 99) {
	    $arg = 99;
	} elsif(($arg >= 7) ||
	   ($arg == 0)) {
	    $arg = 1;
	}
	# ターゲット取得
	my($tn) = $HidToNumber{$target};
	if($tn eq '') {
	    # ターゲットがすでにない
	    logMsNoTarget($id, $name, $comName);
	    return 0;
	}
	# 事前準備
	my($tIsland) = $Hislands[$tn];
	my($tName) = $tIsland->{'name'};
	my($tEisei1) = $tIsland->{'eis1'};
	my($tEisei2) = $tIsland->{'eis2'};
	my($tEisei3) = $tIsland->{'eis3'};
	my($tEisei4) = $tIsland->{'eis4'};
	my($tEisei5) = $tIsland->{'eis5'};
	my($tEisei6) = $tIsland->{'eis6'};
	my($tEisei7) = $tIsland->{'eis7'};


	$etc7 = $island->{'etc7'};
	$etc7 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
	($msjotai, $nokotan, $msid) = ($1, $2, $3);
	if((($msjotai != 2) ||
	   ($tIsland->{'id'} != $msid)) && ($lovePeace == 1)) {
		logNiwaren3($id, $name, $comName);
		return 1;
        }


	if($island->{'eis6'} >= 1) {
	    if($arg == 1) {
	        if($tEisei1 >= 1) {
		    if(random(100) < 100) {
	               $tIsland->{'eis1'} = 0;
	                logEiseiAtts($id, $tId, $name, $tName, $comName, "気象衛星");
	            } else {
	                logEiseiAttf($id, $tId, $name, $tName, $comName, "気象衛星");
		    }
	        } else {
	        logNoEisei($id, $name, $comName);
		    return 0;
	        }
	    }
	    if($arg == 2) {
	        if($tEisei2 >= 1) {
		    if(random(100) < 90) {
	               $tIsland->{'eis2'} = 0;
	                logEiseiAtts($id, $tId, $name, $tName, $comName, "観測衛星");
	            } else {
	                logEiseiAttf($id, $tId, $name, $tName, $comName, "観測衛星");
		    }
	        } else {
	        logNoEisei($id, $name, $comName);
		    return 0;
	        }
	    }
	    if($arg == 3) {
	        if($tEisei3 >= 1) {
		    if(random(100) < 80) {
	               $tIsland->{'eis3'} = 0;
	                logEiseiAtts($id, $tId, $name, $tName, $comName, "迎撃衛星");
	            } else {
	                logEiseiAttf($id, $tId, $name, $tName, $comName, "迎撃衛星");
		    }
	        } else {
	        logNoEisei($id, $name, $comName);
		    return 0;
	        }
	    }
	    if($arg == 4) {
	        if($tEisei4 >= 1) {
		    if(random(100) < 70) {
	               $tIsland->{'eis4'} = 0;
	                logEiseiAtts($id, $tId, $name, $tName, $comName, "軍事衛星");
	            } else {
	                logEiseiAttf($id, $tId, $name, $tName, $comName, "軍事衛星");
		    }
	        } else {
	        logNoEisei($id, $name, $comName);
		    return 0;
	        }
	    }
	    if($arg == 5) {
	        if($tEisei5 >= 1) {
		    if(random(100) < 60) {
	               $tIsland->{'eis5'} = 0;
	                logEiseiAtts($id, $tId, $name, $tName, $comName, "防衛衛星");
	            } else {
	                logEiseiAttf($id, $tId, $name, $tName, $comName, "防衛衛星");
		    }
	        } else {
	        logNoEisei($id, $name, $comName);
		    return 0;
	        }
	    }
	    if($arg == 6) {
	        if($tEisei6 >= 1) {
		    if(random(100) < 50) {
	               $tIsland->{'eis6'} = 0;
	                logEiseiAtts($id, $tId, $name, $tName, $comName, "イレギュラー");
	            } else {
	                logEiseiAttf($id, $tId, $name, $tName, $comName, "イレギュラー");
		    }
	        } else {
	        logNoEisei($id, $name, $comName);
		    return 0;
	        }
	    }
	    if($arg == 99) {
	        if($tEisei7 >= 1) {
			$tcstpop = int($tEisei7/100);
			$tcsten = $tEisei7%100;
			$tdmg = random(100);
			$tcstpop = int($tcstpop*$tdmg/100);
			$tcsten = int($tcsten*$tdmg/100);
			$tIsland->{'eis7'} = $tcstpop*100+$tcsten;
			$tdmg = 100-$tdmg;
	                logEiseiAttcst($id, $tId, $name, $tName, $comName, "宇宙ステーション", $tdmg);

			if($tcsten < $tdmg) {
			$tIsland->{'eis7'} = 0;
			logEiseiEnd($id, $name, "宇宙ステーション");
			}

	        } else {
	        logNoEisei($id, $name, $comName);
		    return 0;
	        }
	    }
	# 金を差し引く
        $island->{'eis6'} -= 30;
        if($island->{'eis6'} < 1) {
           $island->{'eis6'} = 0;
		logEiseiEnd($id, $name, "イレギュラー");
        }
	$island->{'money'} -= $cost;
	return 1;
	}
	elsif($island->{'eis4'} >= 1) {
	    if($arg == 1) {
	        if($tEisei1 >= 1) {
		    if(random(100) < 70) {
	               $tIsland->{'eis1'} = 0;
	                logEiseiAtts($id, $tId, $name, $tName, $comName, "気象衛星");
	            } else {
	                logEiseiAttf($id, $tId, $name, $tName, $comName, "気象衛星");
		    }
	        } else {
	        logNoEisei($id, $name, $comName);
		    return 0;
	        }
	    }
	    if($arg == 2) {
	        if($tEisei2 >= 1) {
		    if(random(100) < 60) {
	              $tIsland->{'eis2'} = 0;
	                logEiseiAtts($id, $tId, $name, $tName, $comName, "観測衛星");
	            } else {
	                logEiseiAttf($id, $tId, $name, $tName, $comName, "観測衛星");
		    }
	        } else {
	        logNoEisei($id, $name, $comName);
		    return 0;
	        }
	    }
	    if($arg == 3) {
	        if($tEisei3 >= 1) {
		    if(random(100) < 50) {
	               $tIsland->{'eis3'} = 0;
	                logEiseiAtts($id, $tId, $name, $tName, $comName, "迎撃衛星");
	            } else {
	                logEiseiAttf($id, $tId, $name, $tName, $comName, "迎撃衛星");
		    }
	        } else {
	        logNoEisei($id, $name, $comName);
		    return 0;
	        }
	    }
	    if($arg == 4) {
	        if($tEisei4 >= 1) {
		    if(random(100) < 40) {
	               $tIsland->{'eis4'} = 0;
	                logEiseiAtts($id, $tId, $name, $tName, $comName, "軍事衛星");
	            } else {
	                logEiseiAttf($id, $tId, $name, $tName, $comName, "軍事衛星");
		    }
	        } else {
	        logNoEisei($id, $name, $comName);
		    return 0;
	        }
	    }
	    if($arg == 5) {
	        if($tEisei5 >= 1) {
		    if(random(100) < 30) {
	               $tIsland->{'eis5'} = 0;
	                logEiseiAtts($id, $tId, $name, $tName, $comName, "防衛衛星");
	            } else {
	                logEiseiAttf($id, $tId, $name, $tName, $comName, "防衛衛星");
		    }
	        } else {
	        logNoEisei($id, $name, $comName);
		    return 0;
	        }
	    }
	    if($arg == 6) {
	        if($tEisei6 >= 1) {
		    if(random(100) < 20) {
	               $tIsland->{'eis6'} = 0;
	                logEiseiAtts($id, $tId, $name, $tName, $comName, "イレギュラー");
	            } else {
	                logEiseiAttf($id, $tId, $name, $tName, $comName, "イレギュラー");
		    }
	        } else {
	        logNoEisei($id, $name, $comName);
		    return 0;
	        }
	    }
	    if($arg == 99) {
	        if($tEisei7 >= 1) {
			$tcstpop = int($tEisei7/100);
			$tcsten = $tEisei7%100;
			$tdmg = random(100);
			$tcstpop = int($tcstpop*$tdmg/100);
			$tcsten = int($tcsten*$tdmg/100);
			$tIsland->{'eis7'} = $tcstpop*100+$tcsten;
			$tdmg = 100-$tdmg;
	                logEiseiAttcst($id, $tId, $name, $tName, $comName, "宇宙ステーション", $tdmg);

			if($tcsten < $tdmg) {
			$tIsland->{'eis7'} = 0;
			logEiseiEnd($id, $name, "宇宙ステーション");
			}

	        } else {
	        logNoEisei($id, $name, $comName);
		    return 0;
	        }
	    }
	# 金を差し引く
        $island->{'eis4'} -= 30;
        if($island->{'eis4'} < 1) {
           $island->{'eis4'} = 0;
		logEiseiEnd($id, $name, "軍事衛星");
        }
	$island->{'money'} -= $cost;
	return 1;
	} else {
	        logNesEisei($id, $name, $comName);
		    return 0;
        }


    } elsif($kind == $HcomEiseiLzr) {
	my($tn) = $HidToNumber{$target};
	if($tn eq '') {
	    # ターゲットがすでにない
	    logMsNoTarget($id, $name, $comName);
	    return 0;
	}
	# 事前準備
	my($tIsland) = $Hislands[$tn];
	my($tName) = $tIsland->{'name'};
	my($tLand) = $tIsland->{'land'};
	my($tLandValue) = $tIsland->{'landValue'};
	my($tx, $ty);


	$etc7 = $island->{'etc7'};
	$etc7 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
	($msjotai, $nokotan, $msid) = ($1, $2, $3);
	if((($msjotai != 2) ||
	   ($tIsland->{'id'} != $msid)) && ($lovePeace == 1)) {
		logNiwaren3($id, $name, $comName);
		return 1;
        }


        # 自島の人口が少ないか、目標島の人口が少ないなら、実行は許可されない
        if (($island->{'pop'} < $HguardPop) || ($tIsland->{'pop'} < $HguardPop)) {
            logForbidden($id, $name, $comName);
            return 0;
        }
		# 着弾点算出
		$err = 1;
		my($r) = random($err);
		$tx = $x + $ax[$r];
		$ty = $y + $ay[$r];
		if((($ty % 2) == 0) && (($y % 2) == 1)) {
		    $tx--;
		}

		# 着弾点の地形等算出
		my($tL) = $tLand->[$tx][$ty];
		my($tLv) = $tLandValue->[$tx][$ty];
		my($tLname) = landName($tL, $tLv);
		my($tPoint) = "($tx, $ty)";

	if($island->{'eis6'} >= 1){
	    if(($tL == $HlandSea) ||
	       ($tL == $HlandWaste) ||
	       ($tL == $HlandMountain) ||
	       ($tL == $HlandGold) ||
	       ($tL == $HlandSeacity) ||
	       ($tL == $HlandSeatown) ||
	       ($tL == $HlandUmishuto) ||
	       ($tL == $HlandUmiamu) ||
	       ($tL == $HlandSbase)) {
		logLzrefc($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint);
	    } elsif(($tL == $HlandOil) ||
	       ($tL == $HlandNursery) ||
	       ($tL == $HlandFrocity) ||
	       ($tL == $HlandIce) ||
	       ($tL == $HlandFune)) {
		logLzrhit($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint);
                        $tLand->[$tx][$ty] = $HlandSea;
                        $tLandValue->[$tx][$ty] = 1;
	    } elsif($tL == $HlandOnsen) {
		logLzrhit($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint);
                        $tLand->[$tx][$ty] = $HlandMountain;
                        $tLandValue->[$tx][$ty] = 0;
	    } else {
		logLzrhit($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint);
                        $tLand->[$tx][$ty] = $HlandWaste;
                        $tLandValue->[$tx][$ty] = 0;
		                if (rand(1000) < 100) {
		                    $land->[$tx][$ty] = $HlandMonument;
		                    $landValue->[$tx][$ty] = 79;
		                }
	    }
	 	$island->{'eis6'} -= 5;
		if($island->{'eis6'} < 1) {
		   $island->{'eis6'} = 0;
		    logEiseiEnd($id, $name, "イレギュラー");
		}
		$island->{'money'} -= $cost;
		return 1;
	} elsif($island->{'eis4'} >= 1){
	    if(($tL == $HlandSea) ||
	       ($tL == $HlandWaste) ||
	       ($tL == $HlandMountain) ||
	       ($tL == $HlandGold) ||
	       ($tL == $HlandSeacity) ||
	       ($tL == $HlandSeatown) ||
	       ($tL == $HlandUmishuto) ||
	       ($tL == $HlandUmiamu) ||
	       ($tL == $HlandSbase)) {
		logLzrefc($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint);
	    } elsif(($tL == $HlandOil) ||
	       ($tL == $HlandNursery) ||
	       ($tL == $HlandFrocity) ||
	       ($tL == $HlandIce) ||
	       ($tL == $HlandFune)) {
		logLzrhit($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint);
                        $tLand->[$tx][$ty] = $HlandSea;
                        $tLandValue->[$tx][$ty] = 1;
	    } elsif($tL == $HlandOnsen) {
		logLzrhit($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint);
                        $tLand->[$tx][$ty] = $HlandMountain;
                        $tLandValue->[$tx][$ty] = 0;
	    } else {
		logLzrhit($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint);
                        $tLand->[$tx][$ty] = $HlandWaste;
                        $tLandValue->[$tx][$ty] = 0;
		                if (rand(1000) < 100) {
		                    $land->[$tx][$ty] = $HlandMonument;
		                    $landValue->[$tx][$ty] = 79;
		                }
	    }
	 	$island->{'eis4'} -= 10;
		if($island->{'eis4'} < 1) {
		   $island->{'eis4'} = 0;
		    logEiseiEnd($id, $name, "軍事衛星");
		}
		$island->{'money'} -= $cost;
		return 1;
	} else {
	        logNesEisei($id, $name, $comName);
		    return 0;
        }


    } elsif(($kind == $HcomMissileNM) ||
	    ($kind == $HcomMissilePP) ||
	    ($kind == $HcomMissileSPP) ||
	    ($kind == $HcomMissileST) ||
	    ($kind == $HcomMissileSS) ||
	    ($kind == $HcomMissileLR) ||
	    ($kind == $HcomMissileLD)) {
	# ミサイル系
	# ターゲット取得
	my($tn) = $HidToNumber{$target};
	if($tn eq '') {
	    # ターゲットがすでにない
	    logMsNoTarget($id, $name, $comName);
	    return 0;
	}

	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}

	my($flag) = 0;
	if($arg == 0) {
	    # 0の場合は撃てるだけ
	    $arg = 100;
	}

	# 事前準備
	my($tIsland) = $Hislands[$tn];
	my($tName) = $tIsland->{'name'};
	my($tLand) = $tIsland->{'land'};
	my($tLandValue) = $tIsland->{'landValue'};
	my($tx, $ty, $err);

	$etc7 = $island->{'etc7'};
	$etc7 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
	($msjotai, $nokotan, $msid) = ($1, $2, $3);

	my($doumei) = 0;

	    my($dx, $dy, $landKindd, $ttlv, $i);
	    for($i = 0; $i < $HpointNumber; $i++) {
		$dx = $Hrpx[$i];
		$dy = $Hrpy[$i];
		$landKindd = $land->[$dx][$dy];
		if($landKindd == $HlandTaishi) {
		    $ttlv = $landValue->[$dx][$dy];
		    if($ttlv == $tIsland->{'id'}) {
			$doumei = 1;
	            }
		}
	    }

		if(($lovePeace == 1) &&
		   ($msjotai == 2) &&
		   ($tIsland->{'id'} == $msid)) {

	        } elsif(($lovePeace == 1) &&
		   ($doumei == 1) &&
		   ($island->{'id'} != $tIsland->{'id'})) {

	        } elsif(($lovePeace == 1) &&
		   ($tIsland->{'monsterlive'} == 0) &&
		   ($tIsland->{'rot'} == 0) &&
		   ($island->{'id'} != $tIsland->{'id'})) {

		$island->{'money'} = 0;

		logNiwaren2($id, $name, $comName);
		return 0;
	        } elsif(($lovePeace == 1) &&
			($kind != $HcomMissileSPP) &&
			($island->{'id'} != $tIsland->{'id'})) {
		logNiwaren3($id, $name, $comName);
		return 0;
	        }


        # 自島の人口が少ないか、目標島の人口が少ないなら、実行は許可されない
        if ((($island->{'pop'} < $HguardPop) || ($tIsland->{'pop'} < $HguardPop)) && ($tIsland->{'rot'} == 0)) {
            logForbidden($id, $name, $comName);
            return 0;
        }

	# 難民の数
	my($boat) = 0;

	# 誤差
	if($kind == $HcomMissilePP) {
	    $err = 7;
	} elsif($kind == $HcomMissileSS) {
	    $err = 7;
	} elsif($kind == $HcomMissileSPP) {
	    $err = 1;
	} else {
	    $err = 19;
	}

	$mukou = 0;
	$bouei = 0;
	$kaijumukou = 0;
	$kaijuhit = 0;
	$total = 0;
	$fuhatu = 0;

	# 金が尽きるか指定数に足りるか基地全部が撃つまでループ
	my($bx, $by, $count) = (0,0,0);
	while(($arg > 0) &&
	      ($island->{'money'} >= $cost)) {
	    # 基地を見つけるまでループ
	    while($count < $HpointNumber) {
		$bx = $Hrpx[$count];
		$by = $Hrpy[$count];
		if(($land->[$bx][$by] == $HlandBase) ||
		   ($land->[$bx][$by] == $HlandSbase)) {
		    last;
		}
		$count++;
	    }
	    if($count >= $HpointNumber) {
		# 見つからなかったらそこまで
		last;
	    }

	    # 最低一つ基地があったので、flagを立てる
	    $flag = 1;	   

	    # 基地のレベルを算出
	    my($level) = expToLevel($land->[$bx][$by], $landValue->[$bx][$by]);
	    # 基地内でループ
	    while(($level > 0) &&
		  ($arg > 0) &&
		  ($island->{'money'} > $cost)) {
			if(rand(300) < $alltotal-int($island->{'rena'}/100)) {
			$level--;
			$arg--;
			$island->{'money'} -= $cost;
			$total++;
			$alltotal++;
			$fuhatu++;
			}
		# 撃ったのが確定なので、各値を消耗させる
		$level--;
		$arg--;
		$island->{'money'} -= $cost;
		$total++;
		$alltotal++;
		# 着弾点算出
		my($r) = random($err);
		$tx = $x + $ax[$r];
		$ty = $y + $ay[$r];
		if((($ty % 2) == 0) && (($y % 2) == 1)) {
		    $tx--;
		}

		# 着弾点範囲内外チェック
		if(($tx < 0) || ($tx >= $HislandSize) ||
		   ($ty < 0) || ($ty >= $HislandSize)) {
		    # 範囲外
		    if($kind == $HcomMissileST) {
			$mukou++;
		    } else {
			$mukou++;
		    }
		    next;
		}

		# 着弾点の地形等算出
		my($tL) = $tLand->[$tx][$ty];
		my($tLv) = $tLandValue->[$tx][$ty];
		my($tLname) = landName($tL, $tLv);
		my($tPoint) = "($tx, $ty)";

		# 防衛施設判定
		my($defence) = 0;
		if($kind == $HcomMissileSPP) {
		    $defence = 1;
		}
		if($HdefenceHex[$id][$tx][$ty] == 1) {
		    $defence = 1;
		} elsif($HdefenceHex[$id][$tx][$ty] == -1) {
		    $defence = 0;
		} else {
		    if(($tL == $HlandDefence) ||
		      (($tL == $HlandProcity) && ($tLv < 160))) {
			# 防衛施設に命中
			# フラグをクリア
			my($i, $count, $sx, $sy);
			for($i = 0; $i < 19; $i++) {
			    $sx = $tx + $ax[$i];
			    $sy = $ty + $ay[$i];

			    # 行による位置調整
			    if((($sy % 2) == 0) && (($ty % 2) == 1)) {
				$sx--;
			    }

			    if(($sx < 0) || ($sx >= $HislandSize) ||
			       ($sy < 0) || ($sy >= $HislandSize)) {
				# 範囲外の場合何もしない
			    } else {
				# 範囲内の場合
				$HdefenceHex[$id][$sx][$sy] = 0;
			    }
			}
		    } elsif((countAround($tLand, $tx, $ty, $HlandDefence, 19))&&($island->{'sabun'} > 0)) {
			$HdefenceHex[$id][$tx][$ty] = 1;
			$defence = 1;
		    } elsif((countAround($tLand, $tx, $ty, $HlandProcity, 7))&&($island->{'sabun'} > 0)) {
			$HdefenceHex[$id][$tx][$ty] = 1;
			$defence = 1;
		    } elsif((countAround($tLand, $tx, $ty, $HlandHouse, 1))&&($island->{'sabun'} > 0)) {
			$HdefenceHex[$id][$tx][$ty] = 1;
			$defence = 1;
		    } elsif((countAround($tLand, $tx, $ty, $HlandShuto, 7))&&($island->{'sabun'} > 0)) {
			$HdefenceHex[$id][$tx][$ty] = 1;
			$defence = 1;
		    } else {
			$HdefenceHex[$id][$tx][$ty] = -1;
			$defence = 0;
		    }
		}
		
		if($defence == 1) {
		    # 空中爆破
		    if($kind == $HcomMissileST) {
			$bouei++;
		    } else {
			$bouei++;
		    }
		    next;
		}

	        if($tIsland->{'eis5'} >= 1) {
		    if(random(5000) < $tIsland->{'rena'}) {
	               $tIsland->{'eis5'} -= 2;
			if($tIsland->{'eis5'} < 1) {
			   $tIsland->{'eis5'} = 0;
			    logEiseiEnd($id, $name, "防衛衛星");
			}
			$bouei++;
		    next;
		    }
	        }

	        if($tIsland->{'c23'} >= 1) {
			$kaijumukou++;
		    next;
	        }

	        if(($tIsland->{'h10'} >= 1) && ($island->{'id'} != $tIsland->{'id'})) {
			$bouei++;
		    next;
	        }

		# 「効果なし」hexを最初に判定
		if(($kind != $HcomMissileLR) &&
		   ((($tL == $HlandSea) && ($tLv == 0)) || # 深い海
		   ((($tL == $HlandSea) ||   # 海または・・・
		     ($tL == $HlandSbase) ||   # 海底基地または・・・
		     ($tL == $HlandSeacity) ||
		     ($tL == $HlandSeatown) ||
		     ($tL == $HlandUmishuto) ||
		     ($tL == $HlandUmiamu) ||
		     ($tL == $HlandGold) ||
		     ($tL == $HlandMountain)) # 山で・・・
		    && ($kind != $HcomMissileLD)))){ # 陸破弾以外
		    # 海底基地の場合、海のフリ
		    if(($tL == $HlandSbase) ||
		       ($tL == $HlandSeatown) ||
		       ($tL == $HlandUmishuto) ||
		       ($tL == $HlandSeacity)) {
			$tL = $HlandSea;
		    }
		    $tLname = landName($tL, $tLv);

		    # 無効化
		    if($kind == $HcomMissileST) {
			# ステルス
			$mukou++;
		    } else {
			# 通常系
			$mukou++;
		    }
		    next;
		}

		# 弾の種類で分岐
      if($kind == $HcomMissileLR) {
        if(($tL == $HlandMountain) ||
	   ($tL == $HlandGold)) {
          # 山に着弾した場合無効
			$mukou++;
          next;
        }
        if($tL == $HlandSbase) {
          # 海底基地なら、目的の場所を浅瀬にする
          $land->[$tx][$ty] = $HlandSea;
          $landValue->[$tx][$ty] = 1;
          logMsLRSbase($id, $target, $name, $tName,
                       $comName, $tLname, $point, $tPoint);
          next;
        } elsif($tL == $HlandSeacity) {
          # 海底基地なら、目的の場所を浅瀬にする
          $land->[$tx][$ty] = $HlandSea;
          $landValue->[$tx][$ty] = 1;
          logMsLRSbase($id, $target, $name, $tName,
                     $comName, $tLname, $point, $tPoint);
          next;
        } elsif($tL == $HlandUmishuto) {
          # 海底基地なら、目的の場所を浅瀬にする
          $land->[$tx][$ty] = $HlandSea;
          $landValue->[$tx][$ty] = 1;
          logMsLRSbase($id, $target, $name, $tName,
                     $comName, $tLname, $point, $tPoint);
          next;
        } elsif($tL == $HlandSeatown) {
          # 海底基地なら、目的の場所を浅瀬にする
          $land->[$tx][$ty] = $HlandSea;
          $landValue->[$tx][$ty] = 1;
          logMsLRSbase($id, $target, $name, $tName,
                     $comName, $tLname, $point, $tPoint);
          next;
        } elsif($tL == $HlandOil) {
          # 海底基地なら、目的の場所を浅瀬にする
          $land->[$tx][$ty] = $HlandSea;
          $landValue->[$tx][$ty] = 1;
          logMsLRSbase($id, $target, $name, $tName,
                     $comName, $tLname, $point, $tPoint);
          next;
        } elsif($tL == $HlandFune) {
          # 海底基地なら、目的の場所を浅瀬にする
          $land->[$tx][$ty] = $HlandSea;
          $landValue->[$tx][$ty] = 1;
          logMsLRSbase($id, $target, $name, $tName,
                     $comName, $tLname, $point, $tPoint);
          next;
        } elsif($tL == $HlandFrocity) {
          # 海底基地なら、目的の場所を浅瀬にする
          $land->[$tx][$ty] = $HlandSea;
          $landValue->[$tx][$ty] = 1;
          logMsLRSbase($id, $target, $name, $tName,
                     $comName, $tLname, $point, $tPoint);
          next;
        } elsif($tL == $HlandUmiamu) {
          # 海底基地なら、目的の場所を浅瀬にする
          $land->[$tx][$ty] = $HlandSea;
          $landValue->[$tx][$ty] = 1;
          logMsLRSbase($id, $target, $name, $tName,
                     $comName, $tLname, $point, $tPoint);
          next;
        } elsif($tL == $HlandRottenSea) {
          # 海底基地なら、目的の場所を浅瀬にする
          $land->[$tx][$ty] = $HlandMountain;
          $landValue->[$tx][$ty] = 0;
          logMsLRSeaRotten($id, $target, $name, $tName,
                     $comName, $tLname, $point, $tPoint);
          next;
        } elsif(($tL == $HlandSea) ||
		($tL == $HlandIce)) {
          if($tLv == 1){
            # 浅瀬の場合
            $tLand->[$tx][$ty] = $HlandWaste;
            $tLandValue->[$tx][$ty] = 0;
            logMsLRSea1($id, $target, $name, $tName,
                        $comName, $tLname, $point, $tPoint);

            $tIsland->{'area'}++;

            if($seaCount <= 4) {
              # 周りの海が3ヘックス以内なので、浅瀬にする
              my($i, $sx, $sy);
              for($i = 1; $i < 7; $i++) {
                $sx = $x + $ax[$i];
                $sy = $y + $ay[$i];

                # 行による位置調整
                if((($sy % 2) == 0) && (($y % 2) == 1)) {
                  $sx--;
                }

                if(($sx < 0) || ($sx >= $HislandSize) ||
                   ($sy < 0) || ($sy >= $HislandSize)) {
                } else {
                # 範囲内の場合
                  if($tLand->[$sx][$sy] == $HlandSea) {
                    $tLandValue->[$sx][$sy] = 1;
                  }
                }
              }
            }
            next;
          } else {
            # 海なら、目的の場所を浅瀬にする
            $tLand->[$tx][$ty] = $HlandSea;
            $tLandValue->[$tx][$ty] = 1;
            logMsLRSbase($id, $target, $name, $tName,
                       $comName, $tLname, $point, $tPoint);

            next;

          }
        } elsif($tL == $HlandMonster){
          logMsLRMonster($id, $target, $name, $tName,
                         $comName, $tLname, $point, $tPoint);
          # 山になる
          $tLand->[$tx][$ty] = $HlandMountain;
          $tLandValue->[$tx][$ty] = 0;
          next;
        }

        logMsLRLand($id, $target, $name, $tName,
                    $comName, $tLname, $point, $tPoint);
        # 山になる
        $tLand->[$tx][$ty] = $HlandMountain;
        $tLandValue->[$tx][$ty] = 0;
		                if (rand(1000) < 22) {
		                    $tLand->[$tx][$ty] = $HlandMonument;
		                    $tLandValue->[$tx][$ty] = 75;
		                }
        next;
		    # 経験値
		    if(($tL == $HlandTown) ||
			 ($tL == $HlandMinato) ||
			 ($tL == $HlandOnsen) ||
			 ($tL == $HlandNewtown) ||
			 ($tL == $HlandBigtown)) {
			if(($land->[$bx][$by] == $HlandBase) ||
			($land->[$bx][$by] == $HlandSbase)) {
			# まだ基地の場合のみ
			$landValue->[$bx][$by] += int($tLv / 20);
			if($landValue->[$bx][$by] > $HmaxExpPoint) {
			$landValue->[$bx][$by] = $HmaxExpPoint;
			}
			}
		        logMsLRLand($id, $target, $name, $tName,
		                    $comName, $tLname, $point, $tPoint);
		        # 山になる
		        $tLand->[$tx][$ty] = $HlandMountain;
		        $tLandValue->[$tx][$ty] = 0;
		        next;
		    } else {
		    # その他
		    logMsLRLand($id, $target, $name, $tName,
		                $comName, $tLname, $point, $tPoint);
		    # 山になる
		    $tland->[$tx][$ty] = $HlandMountain;
 		    $tlandValue->[$tx][$ty] = 0;

		                if (rand(1000) < 20) {
		                    $tland->[$tx][$ty] = $HlandMonument;
		                    $tlandValue->[$tx][$ty] = 75;
		                }

		    next;
		    }


		} elsif($kind == $HcomMissileSS) {
			logMsSS($id, $target, $name, $tName,
				    $comName, $tLname, $point, $tPoint);
		wideDamageli($target, $tName, $tLand, $tLandValue, $tx, $ty);

		} elsif($kind == $HcomMissileLD) {
		    # 陸地破壊弾
		    if(($tL == $HlandMountain) ||
		       ($tL == $HlandOnsen) ||
		       ($tL == $HlandGold)) {
			# 山(荒地になる)
			logMsLDMountain($id, $target, $name, $tName,
					 $comName, $tLname, $point, $tPoint);
			# 荒地になる
			$tLand->[$tx][$ty] = $HlandWaste;
			$tLandValue->[$tx][$ty] = 0;
			next;

		    } elsif(($tL == $HlandSbase) ||
			    ($tL == $HlandFune) ||
			    ($tL == $HlandFrocity) ||
			    ($tL == $HlandUmiamu) ||
			    ($tL == $HlandSeatown) ||
			    ($tL == $HlandUmishuto) ||
		            ($tL == $HlandSeacity)) {
			# 海底基地 海底都市
			logMsLDSbase($id, $target, $name, $tName,
				      $comName, $tLname, $point, $tPoint);
		    } elsif($tL == $HlandMonster) {
			# 怪獣
			logMsLDMonster($id, $target, $name, $tName,
					$comName, $tLname, $point, $tPoint);
		    } elsif($tL == $HlandRottenSea) {
			# 怪獣
			logMsLDSeaRotten($id, $target, $name, $tName,
					$comName, $tLname, $point, $tPoint);
		    } elsif(($tL == $HlandSea) ||
			    ($tL == $HlandIce)) {
			# 浅瀬
			logMsLDSea1($id, $target, $name, $tName,
				    $comName, $tLname, $point, $tPoint);
		    } else {
			# その他
			logMsLDLand($id, $target, $name, $tName,
				     $comName, $tLname, $point, $tPoint);
		    }
		    
		    # 経験値
		    if(($tL == $HlandTown) ||
			 ($tL == $HlandMinato) ||
			 ($tL == $HlandNewtown) ||
			 ($tL == $HlandBigtown)) {
			if(($land->[$bx][$by] == $HlandBase) ||
			   ($land->[$bx][$by] == $HlandSbase)) {
			    # まだ基地の場合のみ
			    $landValue->[$bx][$by] += int($tLv / 20);
			    if($landValue->[$bx][$by] > $HmaxExpPoint) {
				$landValue->[$bx][$by] = $HmaxExpPoint;
			    }
			}
		    }

		    # 浅瀬になる
		    $tLand->[$tx][$ty] = $HlandSea;
		    $tIsland->{'area'}--;
		    $tLandValue->[$tx][$ty] = 1;

		    # でも油田、浅瀬、海底基地だったら海
		    if(($tL == $HlandOil) ||
			($tL == $HlandSea) ||
			($tL == $HlandIce) ||
			($tL == $HlandSeacity) ||
			($tL == $HlandSeatown) ||
			($tL == $HlandUmishuto) ||
			($tL == $HlandFune) ||
			($tL == $HlandFrocity) ||
			($tL == $HlandUmiamu) ||
		       ($tL == $HlandSbase)) {
			$tLandValue->[$tx][$ty] = 0;
		    }
		} else {
		    # その他ミサイル
		    if($tL == $HlandWaste) {
			# 荒地(被害なし)
			if($kind == $HcomMissileST) {
			$mukou++;
			} else {
			$mukou++;
			}
		    } elsif($tL == $HlandRottenSea) {
			if($kind == $HcomMissileST) {
			    # ステルス
			    logMsNormalSRotten($id, $target, $name, $tName,
					 $comName, $tLname, $point, $tPoint);
			} else {
			    # 通常
			    logMsNormalRotten($id, $target, $name, $tName,
					$comName, $tLname, $point, $tPoint);
			}
		    } elsif($tL == $HlandMonster) {
			# 怪獣
			my($mKind, $mName, $mHp) = monsterSpec($tLv);
			my($special) = $HmonsterSpecial[$mKind];

			# 硬化中?
			if((($special == 3) && (($HislandTurn % 2) == 1)) ||
                           (($special == 8) && ((seqnum($HislandTurn) % 2) == 0)) ||
			   (($special == 4) && (($HislandTurn % 2) == 0))) {
			    # 硬化中
			    if($kind == $HcomMissileST) {
				# ステルス
				$kaijumukou++;
			    } else {
				# 通常弾
				$kaijumukou++;
			    }
			    next;
			} else {
			    # 硬化中じゃない
			    if(($special == 5 && random(1000)+$island->{'co4'}*100+$island->{'co99'}*100 < $HmonsterDefence) ||
				($mKind == 15 && random(1000)+$island->{'co4'}*100+$island->{'co99'}*100 < $HmonsterDefence)) {
			      if($kind == $HcomMissileST) {
				$kaijumukou++;
			    } else{
				$kaijumukou++;
			    }
			    next;
			    }elsif(($mKind == 13 && random(1000)+$island->{'co4'}*100+$island->{'co99'}*100 < 900) ||
				   ($mKind == 20 && random(1000)+$island->{'co4'}*100+$island->{'co99'}*100 < 800) ||
				   ($mKind == 21 && random(1000)+$island->{'co4'}*100+$island->{'co99'}*100 < 700) ||
				   ($mKind == 22 && random(1000)+$island->{'co4'}*100+$island->{'co99'}*100 < 750) ||
				   ($mKind == 18 && random(1000)+$island->{'co4'}*100+$island->{'co99'}*100 < (600+random(400))) ||
				   ($mKind == 30 && random(1000)+$island->{'co4'}*100+$island->{'co99'}*100 < (950+random(50))) ||
				   ($mKind == 19 && random(1000)+$island->{'co4'}*100+$island->{'co99'}*100 < (666+random(400)))) {
			      if($kind == $HcomMissileST) {
				$kaijumukou++;
			    } else{
				$kaijumukou++;
			    }
			    next;
			    }elsif($mKind == 14 && random(1000)+$island->{'co4'}*100+$island->{'co99'}*100 < 400){
			      if($kind == $HcomMissileST) {
				$kaijumukou++;
			    } else{
				$kaijumukou++;
			    }
			    next;
			    }elsif($mKind == 17 && random(1000)+$island->{'co4'}*100+$island->{'co99'}*100 < (400+random(500))){
			      if($kind == $HcomMissileST) {
				$kaijumukou++;
			    } else{
				$kaijumukou++;
			    }
			    next;
			  }
			    if($mHp == 1) {
				# 怪獣しとめた
				if(($land->[$bx][$by] == $HlandBase) ||
				   ($land->[$bx][$by] == $HlandSbase)) {
				    # 経験値
				    $landValue->[$bx][$by] += $HmonsterExp[$mKind];
				    if($landValue->[$bx][$by] > $HmaxExpPoint) {
					$landValue->[$bx][$by] = $HmaxExpPoint;
				    }
				}

                                if ($mKind == 8) { # オームなら
                                    # 腐海発生
                                    my($point) = "($tx, $ty)";
                                    logRottenSeaBorn($id, $name, $point);
                                    $tLand->[$tx][$ty] = $HlandRottenSea;
                                    $tLandValue->[$tx][$ty] = 1;
                                    next;
                                }

				if($kind == $HcomMissileST) {
				    # ステルス
				    logMsMonKillS($id, $target, $name, $tName,
						  $comName, $mName, $point,
						  $tPoint);
				} else {
				    # 通常
				    logMsMonKill($id, $target, $name, $tName,
						 $comName, $mName, $point,
						 $tPoint);
				}

				# 収入
				my($value) = $HmonsterValue[$mKind];
				if($value > 0) {
				    $tIsland->{'money'} += $value;
				    logMsMonMoney($target, $mName, $value);

	    if($island->{'sin'} > 0) {
	    my($value, $str);
	    $value = $HmonsterValue[$mKind] + random(101);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logSinMoney($id, $name, $str);
	    }
	    if($island->{'jin'} > 0) {
	    my($value, $str);
	    $value = $HmonsterValue[$mKind] + random(101);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logJinMoney($id, $name, $str);
	    }

				}

                                # 怪獣退治数
                                $island->{'taiji'}++;

				# 賞関係
				my($prize) = $island->{'prize'};
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				my($flags) = $1;
				my($monsters) = $2;
				my($turns) = $3;
				my($v) = 2 ** $mKind;
				$monsters |= $v;
				$island->{'prize'} = "$flags,$monsters,$turns";
			    } else {
				# 怪獣生きてる
				if($kind == $HcomMissileST) {
				    # ステルス
					$kaijuhit++;
				} else {
				    # 通常
					$kaijuhit++;
				}
				# HPが1減る
				$tLandValue->[$tx][$ty]--;
				next;
			    }

			}
		    } else {
			# 通常地形
			if($kind == $HcomMissileST) {
			    # ステルス
			    logMsNormalS($id, $target, $name, $tName,
					   $comName, $tLname, $point,
					   $tPoint);
			} else {
			    # 通常
			    logMsNormal($id, $target, $name, $tName,
					 $comName, $tLname, $point,
					 $tPoint);
			}
		    }
		    # 経験値
		    if(($tL == $HlandTown) ||
			($tL == $HlandMinato) ||
			($tL == $HlandNewtown) ||
			($tL == $HlandBigtown)) {
			if(($land->[$bx][$by] == $HlandBase) ||
			    ($land->[$bx][$by] == $HlandSbase)) {
			    $landValue->[$bx][$by] += int($tLv / 20);
			    $boat += $tLv; # 通常ミサイルなので難民にプラス
			    if($landValue->[$bx][$by] > $HmaxExpPoint) {
				$landValue->[$bx][$by] = $HmaxExpPoint;
			    }
			}
		    }
		    
                    # 荒地になる
		    $tLand->[$tx][$ty] = $HlandWaste;
		    $tLandValue->[$tx][$ty] = 1; # 着弾点

		    my($mKind, $mName, $mHp) = monsterSpec($tLv);
		    my($special) = $HmonsterSpecial[$mKind];
		    if(($mKind == 17) && ($tL == $HlandMonster)) {
			$tLand->[$tx][$ty] = $HlandMonument;
			$tLandValue->[$tx][$ty] = 86;
		    }

		    if(($tLv == 25) && ($tL == $HlandMonument) && (random(10000) < $island->{'rena'}) && ($island->{'rena'} > 2000)) {
		    $kind = random($HmonsterLevel4) + 1;
		    $lv = $lv = ($kind << 4)
			+ $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
		    $tLand->[$tx][$ty] = $HlandMonster;
		    $tLandValue->[$tx][$ty] = $lv;
		    # 怪獣情報
		    my($mKind, $mName, $mHp) = monsterSpec($lv);

		    # メッセージ
		    logMonsComemagic($id, $name, $mName, "($bx, $by)", $lName);
		    }

		    # でも油田だったら海
		    if(($tL == $HlandOil) ||
		       ($tL == $HlandFrocity) ||
		       ($tL == $HlandFune)) {
			$tLand->[$tx][$ty] = $HlandSea;
			$tLandValue->[$tx][$ty] = 0;
		    }
                    # でも養殖場なら浅瀬
                    if($tL == $HlandNursery) {
                        $tLand->[$tx][$ty] = $HlandSea;
                        $tLandValue->[$tx][$ty] = 1;
                    }
                    if($tL == $HlandIce) {
                        $tLand->[$tx][$ty] = $HlandSea;
                        $tLandValue->[$tx][$ty] = 1;
                    }
                    if($tL == $HlandOnsen) {
                        $tLand->[$tx][$ty] = $HlandMountain;
                        $tLandValue->[$tx][$ty] = 0;
                    }
		} 
	    }

	    # カウント増やしとく
	    $count++;
	}
	    # ログ
		if($kind == $HcomMissileST) {
			    # ステルス
		logMsTotalS($id, $target, $name, $tName, $comName, $tLname, $point, $tPoint, $total, $mukou, $bouei, $kaijumukou, $kaijuhit, $fuhatu);

		} else {
			    # 通常
		logMsTotal($id, $target, $name, $tName, $comName, $tLname, $point, $tPoint, $total, $mukou, $bouei, $kaijumukou, $kaijuhit, $fuhatu);

			}

	if($flag == 0) {
	    # 基地が一つも無かった場合
	    logMsNoBase($id, $name, $comName);
	    return 0;
	}

	# 難民判定
	$boat = int($boat / 2);
	if(($boat > 0) && ($id != $target) && ($kind != $HcomMissileST)) {
	    # 難民漂着
	    my($achive); # 到達難民
	    my($i);
	    for($i = 0; ($i < $HpointNumber && $boat > 0); $i++) {
		$bx = $Hrpx[$i];
		$by = $Hrpy[$i];
		if($land->[$bx][$by] == $HlandTown) {
		    # 町の場合
		    my($lv) = $landValue->[$bx][$by];
		    if($boat > 50) {
			$lv += 50;
			$boat -= 50;
			$achive += 50;
		    } else {
			$lv += $boat;
			$achive += $boat;
			$boat = 0;
		    }
		    if($lv > 200) {
			$boat += ($lv - 200);
			$achive -= ($lv - 200);
			$lv = 200;
		    }
		    $landValue->[$bx][$by] = $lv;
		} elsif($land->[$bx][$by] == $HlandPlains) {
		    # 平地の場合
		    $land->[$bx][$by] = $HlandTown;;
		    if($boat > 10) {
			$landValue->[$bx][$by] = 5;
			$boat -= 10;
			$achive += 10;
		    } elsif($boat > 5) {
			$landValue->[$bx][$by] = $boat - 5;
			$achive += $boat;
			$boat = 0;
		    }
		}
		if($boat <= 0) {
		    last;
		}
	    }
	    if($achive > 0) {
		# 少しでも到着した場合、ログを吐く
		logMsBoatPeople($id, $name, $achive);

		# 難民の数が一定数以上なら、平和賞の可能性あり
		if($achive >= 200) {
		    my($prize) = $island->{'prize'};
		    $prize =~ /([0-9]*),([0-9]*),(.*)/;
		    my($flags) = $1;
		    my($monsters) = $2;
		    my($turns) = $3;

		    if((!($flags & 8)) &&  $achive >= 200){
			$flags |= 8;
			logPrize($id, $name, $Hprize[4]);
		    } elsif((!($flags & 16)) &&  $achive > 500){
			$flags |= 16;
			logPrize($id, $name, $Hprize[5]);
		    } elsif((!($flags & 32)) &&  $achive > 800){
			$flags |= 32;
			logPrize($id, $name, $Hprize[6]);
		    }
		    $island->{'prize'} = "$flags,$monsters,$turns";
		}
	    }
	}
	return 1;
    } elsif($kind == $HcomSendMonster) {
	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}
	# 怪獣派遣
	# ターゲット取得
	my($tn) = $HidToNumber{$target};
	my($tIsland) = $Hislands[$tn];
	my($tName) = $tIsland->{'name'};

	if($tn eq '') {
	    # ターゲットがすでにない
	    logMsNoTarget($id, $name, $comName);
	    return 0;
	}

        # 自島の人口が少ないか、目標島の人口が少ないなら、実行は許可されない
        if (($island->{'pop'} < $HguardPop) || ($tIsland->{'pop'} < $HguardPop)) {
            logForbidden($id, $name, $comName);
            return 0;
        }

	$etc7 = $island->{'etc7'};
	$etc7 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
	($msjotai, $nokotan, $msid) = ($1, $2, $3);
	if(($msjotai != 2) ||
	   ($tIsland->{'id'} != $msid)) {
		logNiwaren3($id, $name, $comName);
		return 0;
        }

        if ($arg > 30) {
            $arg = 30;
        }

	$kind = $arg;
	$lv = ($kind << 4)
	    + $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
	my($mKind, $mName, $mHp) = monsterSpec($lv);

		if($lovePeace == 1) {

		    $etc6 = $island->{'etc6'};
		    $etc6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($z0,$z1,$z2,$z3,$z4,$z5,$z6,$z7,$z8,$z9,$z10,$z11,$z12,$z13,$z14,$z15,$z16,$z17,$z18,$z19,$z20,$z21,$z22,$z23,$z24,$z25,$z26,$z27,$z28,$z29,$z30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
		    ($z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

		    $etc6t = $tIsland->{'etc6'};
		    $etc6t =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($z0t,$z1t,$z2t,$z3t,$z4t,$z5t,$z6t,$z7t,$z8t,$z9t,$z10t,$z11t,$z12t,$z13t,$z14t,$z15t,$z16t,$z17t,$z18t,$z19t,$z20t,$z21t,$z22t,$z23t,$z24t,$z25t,$z26t,$z27t,$z28t,$z29t,$z30t) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
		    ($zt->{'0'},$zt->{'1'},$zt->{'2'},$zt->{'3'},$zt->{'4'},$zt->{'5'},$zt->{'6'},$zt->{'7'},$zt->{'8'},$zt->{'9'},$zt->{'10'},$zt->{'11'},$zt->{'12'},$zt->{'13'},$zt->{'14'},$zt->{'15'},$zt->{'16'},$zt->{'17'},$zt->{'18'},$zt->{'19'},$zt->{'20'},$zt->{'21'},$zt->{'22'},$zt->{'23'},$zt->{'24'},$zt->{'25'},$zt->{'26'},$zt->{'27'},$zt->{'28'},$zt->{'29'},$zt->{'30'}) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

		    $eisei5 = $island->{'eisei5'};
		    $eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tetsub) = ($1, $2, $3, $4, $5, $6, $7);

		    $eisei5t = $tIsland->{'eisei5'};
		    $eisei5t =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($mshpt, $msapt, $msdpt, $msspt, $mswint, $msexet, $tetsubt) = ($1, $2, $3, $4, $5, $6, $7);

		    $tradeexe = $HmonsterExp[$arg] * 2;

	            if (($z->{"$arg"} > 0) && ($tIsland->{'zoo'} > 0) && ($msexet > $tradeexe) && ($tIsland->{'rena'} > $arg*500)) {
			$z->{"$arg"} -= 1;
			$zt->{"$arg"} += 1;
			$island->{'etc6'} = "$z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}";
			$tIsland->{'etc6'} = "$zt->{'0'},$zt->{'1'},$zt->{'2'},$zt->{'3'},$zt->{'4'},$zt->{'5'},$zt->{'6'},$zt->{'7'},$zt->{'8'},$zt->{'9'},$zt->{'10'},$zt->{'11'},$zt->{'12'},$zt->{'13'},$zt->{'14'},$zt->{'15'},$zt->{'16'},$zt->{'17'},$zt->{'18'},$zt->{'19'},$zt->{'20'},$zt->{'21'},$zt->{'22'},$zt->{'23'},$zt->{'24'},$zt->{'25'},$zt->{'26'},$zt->{'27'},$zt->{'28'},$zt->{'29'},$zt->{'30'}";

			$msexe += $tradeexe;
			$msexet -= $tradeexe;
			$island->{'eisei5'} = "$mshp,$msap,$msdp,$mssp,$mswin,$msexe,$tetsub";
			$tIsland->{'eisei5'} = "$mshpt,$msapt,$msdpt,$msspt,$mswint,$msexet,$tetsubt";

			$cost *= $arg;
			$island->{'money'} += $cost;
			$tIsland->{'money'} -= $cost;

			logMonsSend2($id, $target, $name, $tName, $mName);

		    } else {
			logNoMoney2($id, $name, $comName);
			return 0;
		    }


	        } else {

		    $etc6 = $island->{'etc6'};
		    $etc6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($z0,$z1,$z2,$z3,$z4,$z5,$z6,$z7,$z8,$z9,$z10,$z11,$z12,$z13,$z14,$z15,$z16,$z17,$z18,$z19,$z20,$z21,$z22,$z23,$z24,$z25,$z26,$z27,$z28,$z29,$z30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
		    ($z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

	            if ($z->{"$arg"} > 0) {
			$z->{"$arg"} -= 1;
			$island->{'etc6'} = "$z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}";
		    }

		$tIsland->{'monstersend'}++;
		$tIsland->{'monstersendkind'} = $arg;

		$cost *= $arg;
		$island->{'money'} -= $cost;

		# メッセージ
		logMonsSend($id, $target, $name, $tName, $mName);

	        }

	return 1;
    } elsif($kind == $HcomTaishi) {
	# 大使派遣
	# ターゲット取得
	my($tn) = $HidToNumber{$target};
	my($tIsland) = $Hislands[$tn];
	my($tName) = $tIsland->{'name'};
	my($tLand) = $tIsland->{'land'};
	my($tLandValue) = $tIsland->{'landValue'};
	my($tx, $ty, $err);

	if($tn eq '') {
	    # ターゲットがすでにない
	    logMsNoTarget($id, $name, $comName);
	    return 0;
	}

	if($island->{'id'} > 4090) {
	    # ターゲットが大きい
            logForbidden($id, $name, $comName);
	    return 0;
	}

        # 自島の人口が少ないか、目標島の人口が少ないなら、実行は許可されない
        if (($island->{'pop'} < $HguardPop) || ($tIsland->{'pop'} < $HguardPop)) {
            logForbidden($id, $name, $comName);
            return 0;
        }

        # 同idなら、実行は許可されない
        if ($island->{'id'} == $tIsland->{'id'}) {
            logForbidden($id, $name, $comName);
            return 0;
        }

        # 自島の人口が少ないか、目標島の人口が少ないなら、実行は許可されない
        if ($tIsland->{'tai'} > 2) {
            logForbidden($id, $name, $comName);
            return 0;
        }

	$etc7 = $island->{'etc7'};
	$etc7 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
	($msjotai, $nokotan, $msid) = ($1, $2, $3);

	if(($lovePeace == 1) &&
	   ($msjotai != 2) &&
	   ($tIsland->{'id'} != $msid)) {
            logForbidden($id, $name, $comName);
            return 0;
        }

	$tx = $x;
	$ty = $y;
	if((($ty % 2) == 0) && (($y % 2) == 1)) {
	    $tx--;
	}

	# 着弾点範囲内外チェック
	if(($tx < 0) || ($tx >= $HislandSize) ||
	   ($ty < 0) || ($ty >= $HislandSize)) {
	    next;
	}

	# 着弾点の地形等算出
	my($tL) = $tLand->[$tx][$ty];
	my($tLv) = $tLandValue->[$tx][$ty];
	my($tLname) = landName($tL, $tLv);
	my($tPoint) = "($tx, $ty)";
	$id = $island->{'id'};

	if($tL != $HlandPlains) {
	    logLandFail($id, $name, $comName, $tLname, $tPoint);
	    return 0;
	}

          $tLand->[$tx][$ty] = $HlandTaishi;
          $tLandValue->[$tx][$ty] = $id;

	logTaishi($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint);

	$island->{'money'} -= $cost;
	return 1;

    } elsif($kind == $HcomMagic) {

	if($island->{'shouhi'} > $island->{'ene'}) {
	    logMsNoEne($id, $name, $comName);
	    return 0;
	}

	# 魔術師派遣
	# ターゲット取得
	my($tn) = $HidToNumber{$target};
	my($tIsland) = $Hislands[$tn];
	my($tName) = $tIsland->{'name'};
	my($tLand) = $tIsland->{'land'};
	my($tLandValue) = $tIsland->{'landValue'};
	my($tx, $ty, $err);

	$etc9 = $island->{'etc9'};
	$etc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($co7, $magicf, $magici, $magica, $magicw, $magicl, $magicd) = ($1, $2, $3, $4, $5, $6, $7);

	if($tn eq '') {
	    # ターゲットがすでにない
	    logMsNoTarget($id, $name, $comName);
	    return 0;
	}

	if($co7 == 0) {
	    logMagicNoTarget($id, $name, $comName);
	    return 0;
	}

	$tx = $x;
	$ty = $y;
	if((($ty % 2) == 0) && (($y % 2) == 1)) {
	    $tx--;
	}

	# 着弾点範囲内外チェック
	if(($tx < 0) || ($tx >= $HislandSize) ||
	   ($ty < 0) || ($ty >= $HislandSize)) {
	    next;
	}

	# 着弾点の地形等算出
	my($tL) = $tLand->[$tx][$ty];
	my($tLv) = $tLandValue->[$tx][$ty];
	my($tLname) = landName($tL, $tLv);
	my($tPoint) = "($tx, $ty)";
	$id = $island->{'id'};

	if($arg >= 8) {
	    $arg = 0;
	}
	    if($arg == 0) {
		$t = "炎系魔術師派遣";
	    }
	    if($arg == 1) {
		$t = "氷系魔術師派遣";
	    }
	    if($arg == 2) {
		$t = "地系魔術師派遣";
	    }
	    if($arg == 3) {
		$t = "風系魔術師派遣";
	    }
	    if($arg == 4) {
		$t = "光系魔術師派遣";
	    }
	    if($arg == 5) {
		$t = "闇系魔術師派遣";
	    }
	    if($arg == 6) {
		$t = "天空城砲撃";
	    }
	    if($arg == 7) {
		$t = "動物園飼育係派遣";
	    }

        if ($island->{'id'} == $tIsland->{'id'}) {

		if($tL == $HlandMonster) {

			logTaishi2($id, $tIsland->{'id'}, $name, $tName, $comName, $tLname, $point, $tPoint, $t);

		    if(($arg == 0)&&($island->{'ene'} > 4000+$magicf*400)) {
			# 対象となる怪獣の各要素取り出し
				my($tKind, $tName, $tHp) = monsterSpec($landValue->[$tx][$ty]);
				my($tlv) = $landValue->[$tx][$ty];
				my($tspecial) = $HmonsterSpecial[$tKind];
				$dpoint = $magicf;
			    $island->{'shouhi'} += 4000+$magicf*400;
			    $island->{'money'} -= $cost;
			    logIreAttackt2($id, $name, "炎系魔術師", "灼熱の炎", $dpoint, $tName, $tPoint);

			    $tHp -= $dpoint;
			    $tlv -= $dpoint;
				$landValue->[$tx][$ty] = $tlv;
			    if($tHp < 1){
			    # 対象の怪獣が倒れて荒地になる
				$land->[$tx][$ty] = $HlandWaste;
				$landValue->[$tx][$ty] = 0;
			    # 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $island->{'money'} += $value;
				   logMsMonMoney($id, $tName, $value);
                                # 怪獣退治数
                                $island->{'taiji'}++;

				# 賞関係
				my($prize) = $island->{'prize'};
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				my($flags) = $1;
				my($monsters) = $2;
				my($turns) = $3;
				my($v) = 2 ** $tKind;
				$monsters |= $v;
				$island->{'prize'} = "$flags,$monsters,$turns";
				}
			    next;
		    }
		    if(($arg == 1)&&($island->{'ene'} > 6000+$magici*500)) {
			# 対象となる怪獣の各要素取り出し
				my($tKind, $tName, $tHp) = monsterSpec($landValue->[$tx][$ty]);
				my($tlv) = $landValue->[$tx][$ty];
				my($tspecial) = $HmonsterSpecial[$tKind];
				$dpoint = $magici+random($magici);
			    $island->{'shouhi'} += 6000+$magici*500;
			    $island->{'money'} -= $cost;
			    logIreAttackt2($id, $name, "氷系魔術師", "アイシクルアロー", $dpoint, $tName, $tPoint);

			    $tHp -= $dpoint;
			    $tlv -= $dpoint;
				$landValue->[$tx][$ty] = $tlv;
			    if($tHp < 1){
			    # 対象の怪獣が倒れて荒地になる
				$land->[$tx][$ty] = $HlandIce;
				$landValue->[$tx][$ty] = 0;
			    # 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $island->{'money'} += $value;
				   logMsMonMoney($id, $tName, $value);
                                # 怪獣退治数
                                $island->{'taiji'}++;

				# 賞関係
				my($prize) = $island->{'prize'};
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				my($flags) = $1;
				my($monsters) = $2;
				my($turns) = $3;
				my($v) = 2 ** $tKind;
				$monsters |= $v;
				$island->{'prize'} = "$flags,$monsters,$turns";
				}
			    next;
		    }
		    if(($arg == 2)&&($island->{'ene'} > 10000)) {
			# 対象となる怪獣の各要素取り出し
				my($tKind, $tName, $tHp) = monsterSpec($landValue->[$tx][$ty]);
				my($tlv) = $landValue->[$tx][$ty];
				my($tspecial) = $HmonsterSpecial[$tKind];
				$dpoint = $magica*2;
			    $island->{'shouhi'} += 10000;
			    $island->{'money'} -= $cost;
			    logIreAttackt2($id, $name, "地系魔術師", "アースクエイク", $dpoint, $tName, $tPoint);

			    $tHp -= $dpoint;
			    $tlv -= $dpoint;
				$landValue->[$tx][$ty] = $tlv;
			    if($tHp < 1){
			    # 対象の怪獣が倒れて荒地になる
				$land->[$tx][$ty] = $HlandMountain;
				$landValue->[$tx][$ty] = 0;
			    # 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $island->{'money'} += $value;
				   logMsMonMoney($id, $tName, $value);
                                # 怪獣退治数
                                $island->{'taiji'}++;

				# 賞関係
				my($prize) = $island->{'prize'};
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				my($flags) = $1;
				my($monsters) = $2;
				my($turns) = $3;
				my($v) = 2 ** $tKind;
				$monsters |= $v;
				$island->{'prize'} = "$flags,$monsters,$turns";
				}
			    next;
		    }
		    if(($arg == 3)&&($island->{'ene'} > 1000+$magicw*1000)) {
			# 対象となる怪獣の各要素取り出し
				my($tKind, $tName, $tHp) = monsterSpec($landValue->[$tx][$ty]);
				my($tlv) = $landValue->[$tx][$ty];
				my($tspecial) = $HmonsterSpecial[$tKind];
				$dpoint = random($magicw*2);
			    $island->{'shouhi'} += 1000+$magicw*1000;
			    $island->{'money'} -= $cost;
			    logIreAttackt2($id, $name, "風系魔術師", "疾風の刃", $dpoint, $tName, $tPoint);

			    $tHp -= $dpoint;
			    $tlv -= $dpoint;
				$landValue->[$tx][$ty] = $tlv;
			    if($tHp < 1){
			    # 対象の怪獣が倒れて荒地になる
				$land->[$tx][$ty] = $HlandWaste;
				$landValue->[$tx][$ty] = 0;
			    # 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $island->{'money'} += $value;
				   logMsMonMoney($id, $tName, $value);
                                # 怪獣退治数
                                $island->{'taiji'}++;

				# 賞関係
				my($prize) = $island->{'prize'};
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				my($flags) = $1;
				my($monsters) = $2;
				my($turns) = $3;
				my($v) = 2 ** $tKind;
				$monsters |= $v;
				$island->{'prize'} = "$flags,$monsters,$turns";
				}
			    next;
		    }
		    if(($arg == 4)&&($island->{'ene'} > 10000)) {
			# 対象となる怪獣の各要素取り出し
				my($tKind, $tName, $tHp) = monsterSpec($landValue->[$tx][$ty]);
				my($tlv) = $landValue->[$tx][$ty];
				my($tspecial) = $HmonsterSpecial[$tKind];
				$dpoint = random($magicl*4);
			    $island->{'shouhi'} += 10000;
			    $island->{'money'} -= $cost;
			    logIreAttackt2($id, $name, "光系魔術師", "ライトニングボルト", $dpoint, $tName, $tPoint);

			    $tHp -= $dpoint;
			    $tlv -= $dpoint;
				$landValue->[$tx][$ty] = $tlv;
			    if($tHp < 1){
			    # 対象の怪獣が倒れて荒地になる
				$land->[$tx][$ty] = $HlandWaste;
				$landValue->[$tx][$ty] = 0;
			    # 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $island->{'money'} += $value;
				   logMsMonMoney($id, $tName, $value);
                                # 怪獣退治数
                                $island->{'taiji'}++;

				# 賞関係
				my($prize) = $island->{'prize'};
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				my($flags) = $1;
				my($monsters) = $2;
				my($turns) = $3;
				my($v) = 2 ** $tKind;
				$monsters |= $v;
				$island->{'prize'} = "$flags,$monsters,$turns";
				}
			    next;
		    }
		    if(($arg == 5)&&($island->{'ene'} > 10000)) {
			# 対象となる怪獣の各要素取り出し
				my($tKind, $tName, $tHp) = monsterSpec($landValue->[$tx][$ty]);
				my($tlv) = $landValue->[$tx][$ty];
				my($tspecial) = $HmonsterSpecial[$tKind];
				$dpoint = random($magicd*3);
			    $island->{'shouhi'} += 10000;
			    $island->{'money'} -= $cost;
			    logIreAttackt3($id, $name, "闇系魔術師", "ダークアロー", $dpoint, $tName, $tPoint);

			    if(random(100) < $magicd*10){
			    # 対象の怪獣が倒れて荒地になる
				$land->[$tx][$ty] = $HlandWaste;
				$landValue->[$tx][$ty] = 0;
			    # 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $island->{'money'} += $value;
				   logMsMonMoney($id, $tName, $value);
                                # 怪獣退治数
                                $island->{'taiji'}++;

				# 賞関係
				my($prize) = $island->{'prize'};
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				my($flags) = $1;
				my($monsters) = $2;
				my($turns) = $3;
				my($v) = 2 ** $tKind;
				$monsters |= $v;
				$island->{'prize'} = "$flags,$monsters,$turns";
				}
			    next;
		    }
		    if(($arg == 7)&&($island->{'zoo'} > 0)) {

			    my($i,$sx,$sy);
			    my($zlv) = (0);
			    for($i = 0; $i < $HpointNumber; $i++){
				$sx = $Hrpx[$i];
				$sy = $Hrpy[$i];
			    if($land->[$sx][$sy] == $HlandZoo){
				$zlv += $landValue->[$sx][$sy];
			    }
			    }

			$etc6 = $island->{'etc6'};
			$etc6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
			($z0,$z1,$z2,$z3,$z4,$z5,$z6,$z7,$z8,$z9,$z10,$z11,$z12,$z13,$z14,$z15,$z16,$z17,$z18,$z19,$z20,$z21,$z22,$z23,$z24,$z25,$z26,$z27,$z28,$z29,$z30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
			($z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

			$zookazu = $z0+$z1+$z2+$z3+$z4+$z5+$z6+$z7+$z8+$z9+$z10+$z11+$z12+$z13+$z14+$z15+$z16+$z17+$z18+$z19+$z20+$z21+$z22+$z23+$z24+$z25+$z26+$z27+$z28+$z29+$z30;

			# 対象となる怪獣の各要素取り出し
				my($tKind, $tName, $tHp) = monsterSpec($landValue->[$tx][$ty]);
				my($tlv) = $landValue->[$tx][$ty];
				my($tspecial) = $HmonsterSpecial[$tKind];
				$dpoint = random($magicd*3);

				if($tKind*1000+1000 > $island->{'ene'}) {
				    $island->{'money'} -= $cost;
				    logMsNoEne2($id, $name, $comName);
				    return 0;
				}

				$island->{'shouhi'} += $tKind*1000;
				$island->{'money'} -= $cost;

				$prize = $island->{'prize'};
				my($flags, $monsters, $turns);
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				$flags = $1;
				$monsters= $2;
				$turns = $3;
				$prize = '';
				$f = 1;
				for($i = 0; $i < $HmonsterNumber; $i++) {
				    if($monsters & $f) {
					$taiji->{"$i"}++;
				    }
				    $f *= 2;
				}


			    if(($tKind*500*$tHp < $island->{'rena'}+$island->{'co4'}*1000+$island->{'co99'}*1000) && ($taiji->{"$tKind"} > 0)) {


					    if($zlv < $zookazu){

						logIreAttackt7($id, $name, "動物園飼育係", "捕獲グッツ", $dpoint, $tName, $tPoint);

					    } else {

					    logIreAttackt5($id, $name, "動物園飼育係", "捕獲グッツ", $dpoint, $tName, $tPoint);
					    # 対象の怪獣が倒れて荒地になる
						$land->[$tx][$ty] = $HlandWaste;
						$landValue->[$tx][$ty] = 0;

						$etc6 = $island->{'etc6'};
						$etc6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
						($z0,$z1,$z2,$z3,$z4,$z5,$z6,$z7,$z8,$z9,$z10,$z11,$z12,$z13,$z14,$z15,$z16,$z17,$z18,$z19,$z20,$z21,$z22,$z23,$z24,$z25,$z26,$z27,$z28,$z29,$z30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
						($z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

						$z->{"$tKind"}++;
						$island->{'etc6'} = "$z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}";

					    }

				} else {
				logIreAttackt6($id, $name, "動物園飼育係", "捕獲グッツ", $dpoint, $tName, $tPoint);
				}
			return 1;
		    }
		}

        } else {
		if(($tL == $HlandPlains)&&($island->{'ene'} > 2000)) {
		    if(($arg == 0)&&($magicf>2)) {
			$tLand->[$tx][$ty] = $HlandMonument;
			$tLandValue->[$tx][$ty] = 96+$arg;
		    }
		    if(($arg == 1)&&($magici>2)) {
			$tLand->[$tx][$ty] = $HlandMonument;
			$tLandValue->[$tx][$ty] = 96+$arg;
		    }
		    if(($arg == 2)&&($magica>2)) {
			$tLand->[$tx][$ty] = $HlandMonument;
			$tLandValue->[$tx][$ty] = 96+$arg;
		    }
		    if(($arg == 3)&&($magicw>2)) {
			$tLand->[$tx][$ty] = $HlandMonument;
			$tLandValue->[$tx][$ty] = 96+$arg;
		    }
		    if(($arg == 4)&&($magicl>2)) {
			$tLand->[$tx][$ty] = $HlandMonument;
			$tLandValue->[$tx][$ty] = 96+$arg;
		    }
		    if(($arg == 5)&&($magicd>2)) {
			$tLand->[$tx][$ty] = $HlandMonument;
			$tLandValue->[$tx][$ty] = 96+$arg;
		    }
		    if(($arg == 6)&&($island->{'h11'}>0)) {
			$tLand->[$tx][$ty] = $HlandMonument;
			$tLandValue->[$tx][$ty] = 100;
		    }
		$island->{'shouhi'} += 2000;
		$island->{'money'} -= $cost;
		}


		if($tL == $HlandRottenSea) {
		    if($arg == 0) {
			logTaishi2($id, $tIsland->{'id'}, $name, $tName, $comName, $tLname, $point, $tPoint, $t);
			$magicshouhiene = 600-$magicf*50;
			$magicnenshoene = 0;
			if($magicshouhiene < 300) {
			$magicshouhiene = 300;
			}
			    for($i = 0; $i < 19; $i++) {
				$sx = $tx + $ax[$i];
				$sy = $ty + $ay[$i];

				# 行による位置調整
				if((($sy % 2) == 0) && (($ty % 2) == 1)) {
				    $sx--;
				}
    
				$landKind = $tLand->[$sx][$sy];
				$lv = $tLandValue->[$sx][$sy];
				$landName = landName($landKind, $lv);
				$point = "($sx, $sy)";

				# 範囲外判定
				if(($sx < 0) || ($sx >= $HislandSize) ||
				   ($sy < 0) || ($sy >= $HislandSize)) {
				    next;
				}
				if($landKind == $HlandRottenSea) {
				    $tLand->[$sx][$sy] = $HlandWaste;
				    $tLandValue->[$sx][$sy] = 0;
				    $island->{'shouhi'} += $magicshouhiene;
				    $magicnenshoene++;
				}
				if($island->{'shouhi'} > $island->{'ene'}) {
				    $island->{'money'} -= $cost;
				    logIreAttackt4($tIsland->{'id'}, $name, "炎系魔術師", "灼熱の炎", $magicnenshoene, "腐海", "焼き尽くし");
				return 1;
				}
			    }
				    $island->{'money'} -= $cost;
				    logIreAttackt4($tIsland->{'id'}, $name, "炎系魔術師", "灼熱の炎", $magicnenshoene, "腐海", "焼き尽くし");
				return 1;
		    }
		    if($arg == 4) {
			logTaishi2($id, $tIsland->{'id'}, $name, $tName, $comName, $tLname, $point, $tPoint, $t);
			$magicshouhiene = 700-$magicl*100;
			$magicnenshoene = 0;
			if($magicshouhiene < 500) {
			$magicshouhiene = 500;
			}

			    for($i = 0; $i < $HpointNumber; $i++){
				$sx = $Hrpx[$i];
				$sy = $Hrpy[$i];

				$landKind = $tLand->[$sx][$sy];
				$lv = $tLandValue->[$sx][$sy];
				$landName = landName($landKind, $lv);
				$point = "($sx, $sy)";

				if(($landKind == $HlandRottenSea)&&(random(10) < $magicl)) {
				    $tLand->[$sx][$sy] = $HlandWaste;
				    $tLandValue->[$sx][$sy] = 0;
				    $island->{'shouhi'} += $magicshouhiene;
				    $magicnenshoene++;
				}
				if($island->{'shouhi'} > $island->{'ene'}) {
				    $island->{'money'} -= $cost;
				    logIreAttackt4($tIsland->{'id'}, $name, "光系魔術師", "ライトニングボルト", $magicnenshoene, "腐海", "焼き尽くし");
				return 1;
				}
			    }
				    $island->{'money'} -= $cost;
				    logIreAttackt4($tIsland->{'id'}, $name, "光系魔術師", "ライトニングボルト", $magicnenshoene, "腐海", "焼き尽くし");
				return 1;
		    }
		    if($arg == 5) {
			logTaishi2($id, $tIsland->{'id'}, $name, $tName, $comName, $tLname, $point, $tPoint, $t);
			$magicshouhiene = 200;
			$magicnenshoene = 0;
			if($magicshouhiene < 200) {
			$magicshouhiene = 200;
			}

			    for($i = 0; $i < $HpointNumber; $i++){
				$sx = $Hrpx[$i];
				$sy = $Hrpy[$i];

				$landKind = $tLand->[$sx][$sy];
				$lv = $tLandValue->[$sx][$sy];
				$landName = landName($landKind, $lv);
				$point = "($sx, $sy)";

				if(($landKind == $HlandRottenSea)&&(random(5) < $magicd)) {
				    $tLandValue->[$sx][$sy] += 10+$magicd;
				    $island->{'shouhi'} += $magicshouhiene;
				    $magicnenshoene++;
				}
				if($island->{'shouhi'} > $island->{'ene'}) {
				    $island->{'money'} -= $cost;
				    logIreAttackt4($tIsland->{'id'}, $name, "闇系魔術師", "ダークアロー", $magicnenshoene, "腐海", "老化させ");
				return 1;
				}
			    }
				    $island->{'money'} -= $cost;
				    logIreAttackt4($tIsland->{'id'}, $name, "闇系魔術師", "ダークアロー", $magicnenshoene, "腐海", "老化させ");
				return 1;
		    }

		    if($arg == 6) {
			logTaishi2($id, $tIsland->{'id'}, $name, $tName, $comName, $tLname, $point, $tPoint, $t);
			$magicnenshoene = 0;
			    for($i = 0; $i < $HpointNumber; $i++){
				$sx = $Hrpx[$i];
				$sy = $Hrpy[$i];

				$landKind = $tLand->[$sx][$sy];
				$lv = $tLandValue->[$sx][$sy];
				$landName = landName($landKind, $lv);
				$point = "($sx, $sy)";

				if($landKind == $HlandRottenSea) {
				    $tLand->[$sx][$sy] = $HlandWaste;
				    $tLandValue->[$sx][$sy] = 1;
				    $island->{'shouhi'} += random(2500);
				    $magicnenshoene++;
				}
				if($island->{'shouhi'} > $island->{'ene'}) {
				    $island->{'money'} -= $cost;
				    logIreAttackt4($tIsland->{'id'}, $name, "天空城", "天の裁き", $magicnenshoene, "腐海", "吹き飛ばし");
				return 1;
				}
			    }
				    $island->{'money'} -= $cost;
				    logIreAttackt4($tIsland->{'id'}, $name, "天空城", "天の裁き", $magicnenshoene, "腐海", "吹き飛ばし");
				return 1;
		    }

		}

		if($tL == $HlandMonster) {

		    if(($arg == 0)&&($island->{'ene'} > 4000+$magicf*400)) {
			# 対象となる怪獣の各要素取り出し
				my($tKind, $tName, $tHp) = monsterSpec($tLandValue->[$tx][$ty]);
				my($tlv) = $tLandValue->[$tx][$ty];
				my($tspecial) = $HmonsterSpecial[$tKind];
				$dpoint = $magicf;
			    $island->{'shouhi'} += 4000+$magicf*400;
			    $island->{'money'} -= $cost;
			    logIreAttackt2($tIsland->{'id'}, $name, "炎系魔術師", "灼熱の炎", $dpoint, $tName, $tPoint);

			    $tHp -= $dpoint;
			    $tlv -= $dpoint;
				$tLandValue->[$tx][$ty] = $tlv;
			    if($tHp < 1){
			    # 対象の怪獣が倒れて荒地になる
				$tLand->[$tx][$ty] = $HlandWaste;
				$tLandValue->[$tx][$ty] = 0;
			    # 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $tIsland->{'money'} += $value;
				   logMsMonMoney($tIsland->{'id'}, $tName, $value);
                                # 怪獣退治数
                                $island->{'taiji'}++;

				# 賞関係
				my($prize) = $island->{'prize'};
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				my($flags) = $1;
				my($monsters) = $2;
				my($turns) = $3;
				my($v) = 2 ** $tKind;
				$monsters |= $v;
				$island->{'prize'} = "$flags,$monsters,$turns";
				}
		    }
		    if(($arg == 1)&&($island->{'ene'} > 6000+$magici*500)) {
			# 対象となる怪獣の各要素取り出し
				my($tKind, $tName, $tHp) = monsterSpec($tLandValue->[$tx][$ty]);
				my($tlv) = $tLandValue->[$tx][$ty];
				my($tspecial) = $HmonsterSpecial[$tKind];
				$dpoint = $magici+random($magici);
			    $island->{'shouhi'} += 6000+$magici*500;
			    $island->{'money'} -= $cost;
			    logIreAttackt2($tIsland->{'id'}, $name, "氷系魔術師", "アイシクルアロー", $dpoint, $tName, $tPoint);

			    $tHp -= $dpoint;
			    $tlv -= $dpoint;
				$tLandValue->[$tx][$ty] = $tlv;
			    if($tHp < 1){
			    # 対象の怪獣が倒れて荒地になる
				$tLand->[$tx][$ty] = $HlandIce;
				$tLandValue->[$tx][$ty] = 0;
			    # 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $tIsland->{'money'} += $value;
				   logMsMonMoney($tIsland->{'id'}, $tName, $value);
                                # 怪獣退治数
                                $island->{'taiji'}++;

				# 賞関係
				my($prize) = $island->{'prize'};
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				my($flags) = $1;
				my($monsters) = $2;
				my($turns) = $3;
				my($v) = 2 ** $tKind;
				$monsters |= $v;
				$island->{'prize'} = "$flags,$monsters,$turns";
				}
		    }
		    if(($arg == 2)&&($island->{'ene'} > 10000)) {
			# 対象となる怪獣の各要素取り出し
				my($tKind, $tName, $tHp) = monsterSpec($tLandValue->[$tx][$ty]);
				my($tlv) = $tLandValue->[$tx][$ty];
				my($tspecial) = $HmonsterSpecial[$tKind];
				$dpoint = $magica*2;
			    $island->{'shouhi'} += 10000;
			    $island->{'money'} -= $cost;
			    logIreAttackt2($tIsland->{'id'}, $name, "地系魔術師", "アースクエイク", $dpoint, $tName, $tPoint);

			    $tHp -= $dpoint;
			    $tlv -= $dpoint;
				$tLandValue->[$tx][$ty] = $tlv;
			    if($tHp < 1){
			    # 対象の怪獣が倒れて荒地になる
				$tLand->[$tx][$ty] = $HlandMountain;
				$tLandValue->[$tx][$ty] = 0;
			    # 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $tIsland->{'money'} += $value;
				   logMsMonMoney($tIsland->{'id'}, $tName, $value);
                                # 怪獣退治数
                                $island->{'taiji'}++;

				# 賞関係
				my($prize) = $island->{'prize'};
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				my($flags) = $1;
				my($monsters) = $2;
				my($turns) = $3;
				my($v) = 2 ** $tKind;
				$monsters |= $v;
				$island->{'prize'} = "$flags,$monsters,$turns";
				}
		    }
		    if(($arg == 3)&&($island->{'ene'} > 1000+$magicw*1000)) {
			# 対象となる怪獣の各要素取り出し
				my($tKind, $tName, $tHp) = monsterSpec($tLandValue->[$tx][$ty]);
				my($tlv) = $tLandValue->[$tx][$ty];
				my($tspecial) = $HmonsterSpecial[$tKind];
				$dpoint = random($magicw*2);
			    $island->{'shouhi'} += 1000+$magicw*1000;
			    $island->{'money'} -= $cost;
			    logIreAttackt2($tIsland->{'id'}, $name, "風系魔術師", "疾風の刃", $dpoint, $tName, $tPoint);

			    $tHp -= $dpoint;
			    $tlv -= $dpoint;
				$tLandValue->[$tx][$ty] = $tlv;
			    if($tHp < 1){
			    # 対象の怪獣が倒れて荒地になる
				$tLand->[$tx][$ty] = $HlandWaste;
				$tLandValue->[$tx][$ty] = 0;
			    # 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $tIsland->{'money'} += $value;
				   logMsMonMoney($tIsland->{'id'}, $tName, $value);
                                # 怪獣退治数
                                $island->{'taiji'}++;

				# 賞関係
				my($prize) = $island->{'prize'};
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				my($flags) = $1;
				my($monsters) = $2;
				my($turns) = $3;
				my($v) = 2 ** $tKind;
				$monsters |= $v;
				$island->{'prize'} = "$flags,$monsters,$turns";
				}
		    }
		    if(($arg == 4)&&($island->{'ene'} > 10000)) {
			# 対象となる怪獣の各要素取り出し
				my($tKind, $tName, $tHp) = monsterSpec($tLandValue->[$tx][$ty]);
				my($tlv) = $tLandValue->[$tx][$ty];
				my($tspecial) = $HmonsterSpecial[$tKind];
				$dpoint = random($magicl*4);
			    $island->{'shouhi'} += 10000;
			    $island->{'money'} -= $cost;
			    logIreAttackt2($tIsland->{'id'}, $name, "光系魔術師", "ライトニングボルト", $dpoint, $tName, $tPoint);

			    $tHp -= $dpoint;
			    $tlv -= $dpoint;
				$tLandValue->[$tx][$ty] = $tlv;
			    if($tHp < 1){
			    # 対象の怪獣が倒れて荒地になる
				$tLand->[$tx][$ty] = $HlandWaste;
				$tLandValue->[$tx][$ty] = 0;
			    # 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $tIsland->{'money'} += $value;
				   logMsMonMoney($tIsland->{'id'}, $tName, $value);
                                # 怪獣退治数
                                $island->{'taiji'}++;

				# 賞関係
				my($prize) = $island->{'prize'};
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				my($flags) = $1;
				my($monsters) = $2;
				my($turns) = $3;
				my($v) = 2 ** $tKind;
				$monsters |= $v;
				$island->{'prize'} = "$flags,$monsters,$turns";
				}
		    }
		    if(($arg == 5)&&($island->{'ene'} > 10000)) {
			# 対象となる怪獣の各要素取り出し
				my($tKind, $tName, $tHp) = monsterSpec($tLandValue->[$tx][$ty]);
				my($tlv) = $tLandValue->[$tx][$ty];
				my($tspecial) = $HmonsterSpecial[$tKind];
				$dpoint = random($magicd*3);
			    $island->{'shouhi'} += 10000;
			    $island->{'money'} -= $cost;
			    logIreAttackt3($tIsland->{'id'}, $name, "闇系魔術師", "ダークアロー", $dpoint, $tName, $tPoint);

			    if(random(100) < $magicd*10){
			    # 対象の怪獣が倒れて荒地になる
				$tLand->[$tx][$ty] = $HlandWaste;
				$tLandValue->[$tx][$ty] = 0;
			    # 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $tIsland->{'money'} += $value;
				   logMsMonMoney($tIsland->{'id'}, $tName, $value);
                                # 怪獣退治数
                                $island->{'taiji'}++;

				# 賞関係
				my($prize) = $island->{'prize'};
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				my($flags) = $1;
				my($monsters) = $2;
				my($turns) = $3;
				my($v) = 2 ** $tKind;
				$monsters |= $v;
				$island->{'prize'} = "$flags,$monsters,$turns";
				}
		    }
		    if(($arg == 6)&&($island->{'h11'} > 0)) {
			# 対象となる怪獣の各要素取り出し
				my($tKind, $tName, $tHp) = monsterSpec($tLandValue->[$tx][$ty]);
				my($tlv) = $tLandValue->[$tx][$ty];
				my($tspecial) = $HmonsterSpecial[$tKind];
			    $island->{'shouhi'} += random(20000);
			    $island->{'money'} -= $cost;
			    logIreAttackt3($tIsland->{'id'}, $name, "天空城", "天の裁き", $dpoint, $tName, $tPoint);

			    # 対象の怪獣が倒れて荒地になる
				$tLand->[$tx][$ty] = $HlandWaste;
				$tLandValue->[$tx][$ty] = 1;
			    # 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $tIsland->{'money'} += $value;
				   logMsMonMoney($tIsland->{'id'}, $tName, $value);
                                # 怪獣退治数
                                $island->{'taiji'}++;

				# 賞関係
				my($prize) = $island->{'prize'};
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				my($flags) = $1;
				my($monsters) = $2;
				my($turns) = $3;
				my($v) = 2 ** $tKind;
				$monsters |= $v;
				$island->{'prize'} = "$flags,$monsters,$turns";
		    }

		}
        }

	logTaishi2($id, $tIsland->{'id'}, $name, $tName, $comName, $tLname, $point, $tPoint, $t);
	return 1;

    } elsif($kind == $HcomSell) {
	# 輸出量決定
	if($arg == 0) { $arg = 1; }
	my($value) = min($arg * (-$cost), $island->{'food'});

	# 輸出ログ
	logSell($id, $name, $comName, $value);
	$island->{'food'} -=  $value;
	$island->{'money'} += ($value / 10);
	return 0;
    } elsif(($kind == $HcomFood) ||
	    ($kind == $HcomMoney)) {
	# 援助系
	# ターゲット取得
	my($tn) = $HidToNumber{$target};
	my($tIsland) = $Hislands[$tn];
	my($tName) = $tIsland->{'name'};

        # 自島の人口が少ないなら、実行は許可されない
        if ($island->{'pop'} < $HguardPop) {
            logForbidden($id, $name, $comName);
            return 0;
        }

	# 援助量決定
	if($arg == 0) { $arg = 1; }
	my($value, $str);
	if($cost < 0) {
	    $value = min($arg * (-$cost), $island->{'food'});
	    $str = "$value$HunitFood";
	} else {
	    $value = min($arg * ($cost), $island->{'money'});
	    $str = "$value$HunitMoney";
	}

	# 援助ログ
	logAid($id, $target, $name, $tName, $comName, $str);

	if($cost < 0) {
	    $island->{'food'} -= $value;
	    $tIsland->{'food'} += $value;
	} else {
	    $island->{'money'} -= $value;
	    $tIsland->{'money'} += $value;
	}
	return 0;
    } elsif($kind == $HcomEneGive) {
	my($tn) = $HidToNumber{$target};
	my($tIsland) = $Hislands[$tn];
	my($tName) = $tIsland->{'name'};
	my($tLand) = $tIsland->{'land'};
	my($tLandValue) = $tIsland->{'landValue'};

	# 援助量決定
	if($arg == 0) { $arg = 1; }
	my($value, $str);

	    $value = min($arg * ($cost), $island->{'ene'});
	    $str = "$value万kW";

	# 援助ログ
	logAid($id, $target, $name, $tName, $comName, $str);

	    $island->{'money'} -= $value;
	    $island->{'shouhi'} += $value;
	    $tIsland->{'sabun'} = $value;

	    if ($tIsland->{'sabun'} > 0) {
		my($x, $y, $landKind, $lv, $i);
		for($i = 0; $i < $HpointNumber; $i++) {
		    $x = $Hrpx[$i];
		    $y = $Hrpy[$i];
		    $landKind = $tLand->[$x][$y];
		    $lv = $tLandValue->[$x][$y];
		    if(($landKind == $HlandConden) && ($lv < 2000)) {

	                    $n = int((2000 - $lv) / 2);
	                    $n = min(int($n + $n), $tIsland->{'sabun'});
	                    $tIsland->{'sabun'} -= $n;
	                    $tLandValue->[$x][$y] += $n;
			if ($value > 2000) {
	                    $tLandValue->[$x][$y] = 2000;
			}

		    }
	 	    if(($landKind == $HlandConden2) && ($lv < 4000)) {

	                    $n = int((4000 - $lv) / 10);
	                    $n = min(int($n*9 + rand($n)), $tIsland->{'sabun'});
	                    $tIsland->{'sabun'} -= $n;
	                    $tLandValue->[$x][$y] += $n;
			if ($value > 4000) {
	                    $tLandValue->[$x][$y] = 4000;
			}

		    }
		    if(($landKind == $HlandConden3) && ($lv < 7000)) {

	                    $n = int((7000 - $lv) / 2);
	                    $n = min(int($n + $n), $tIsland->{'sabun'});
	                    $tIsland->{'sabun'} -= $n/2;
	                    $tLandValue->[$x][$y] += $n/2;
			if ($value > 7000) {
	                    $tLandValue->[$x][$y] = 7000;
			}

		    }

	                last if ($tIsland->{'sabun'} <= 0);
		}
	    }
	return 1;
    } elsif($kind == $HcomPropaganda) {
	# 誘致活動
	logPropaganda($id, $name, $comName);
	$island->{'propaganda'} = 1;
	$island->{'money'} -= $cost;
	if($arg > 1) {
	    my($command);
	    $arg--;
	    slideBack($comArray, 0);
	    $comArray->[0] = {
		'kind' => $kind,
		'target' => $target,
		'x' => $x,
		'y' => $y,
		'arg' => $arg
		};
	}
	return 1;
    } elsif($kind == $HcomGiveup) {
	# 放棄
	logGiveup($id, $name);
	$island->{'dead'} = 1;
	unlink("island.$id");
	return 1;
    }

    return 1;
}


# 成長および単ヘックス災害
sub doEachHex {
    my($island) = @_;
    my(@monsterMove);

    # 導出値
    my($name) = $island->{'name'};
    my($id) = $island->{'id'};
    my($land) = $island->{'land'};
    my($landValue) = $island->{'landValue'};

    if($anothermood == 1) {
	$island->{'amarimoney'} = $island->{'money'};
	$island->{'money'} = 0;
    }

    $etc5 = $island->{'etc5'};
    $etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
    $s06b = int($s06/5);
    $s08b = int($s08/5);
    $s12b = int($s12/5)+1;
    if($s12b > 10) {$s12b = 10;}

    if(random(20000000)+$s12b*1500000 < $island->{'fukeikimoney'}-$island->{'co6'}*100000) {
	logFukeiki($id, $name);
	$island->{'money'} += 10;
	return 1;
    }

    $aucflag1 = 0;
    $aucflag2 = 0;
    $aucflag3 = 0;

    $zooflag = 0;
    $seisakuflag = 1;

    $msseigen = 0;
    $kougekiseigen = 0;
    $kougekiseigenm = 0;

    $oilincome = 0;
    $parkincome = 0;
    $rizortincome = 0;
    $m84income = 0;
    $gyosenincome = 0;
    $island->{'trainmoney'} = 0;
    $island->{'trainmoney2'} = 0;
    $island->{'hcsankaflag'} = 0;
    $island->{'roudenflag'} = 0;
    $island->{'urikireflag'} = 0;

    # 増える人口のタネ値
    my($addpop)  = 10;  # 村、町
    my($addpop2) = 0; # 都市
    if($island->{'food'} < 0) {
	# 食料不足
	$addpop = -30;
    } elsif($island->{'propaganda'} == 1) {
	# 誘致活動中
	$addpop = 30;
	$addpop2 = 3;
    } elsif((rand(1000)+$island->{'m73'}*250) < $island->{'rot'} * 50) {
	# 胞子！？

	if($island->{'ownfe'} == 1) {
	    logRotsick($id, $name);
	    $value = $island->{'pop'}*3 + random($island->{'pop'})*5;
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";

		if(random(100) < 20) {
		    $island->{'urikireflag'} = 1;
		    logMiyage2c($id, $name, "$island->{'onm'}", $str, "腐海の毒消し薬");
		} else {
		    logMiyage2b($id, $name, "$island->{'onm'}", $str, "腐海の毒消し薬");
		}

	} elsif($island->{'ownfe'} > 1) {

	} else {
	    logRotsick($id, $name);
	    $addpop = -10;
	}

    } elsif(random(1000) < $island->{'c21'} * 500) {
	# 疫病！？
	$addpop = -3;
	$island->{'food'} -= int($island->{'food'} / 2);
	logSatansick($id, $name);
    } elsif($island->{'fim'} > 0) {
	# 副作用？！
	    if(random(1000) < 10) {
		$addpop = -20;
		logStarvefood($id, $name);
	    }
    }

    # ループ
    my($x, $y, $i);
    for($i = 0; $i < $HpointNumber; $i++) {
	$x = $Hrpx[$i];
	$y = $Hrpy[$i];
	my($landKind) = $land->[$x][$y];
	my($lv) = $landValue->[$x][$y];


	    if(($landKind == $HlandPlains) && (($island->{'co78'} > 0) || ($island->{'co80'} > 0) || ($island->{'yaku'} > 0))) {
		$land->[$x][$y] = $HlandPlains2;
		$landValue->[$x][$y] = 0;
		$island->{'money'} -= 10000*$seisakuflag;
		$seisakuflag++;
	    }
	    if((($landKind == $HlandWaste) || ($landKind == $HlandSunahama)) && (($island->{'co79'} > 0) || ($island->{'co80'} > 0))) {
		$land->[$x][$y] = $HlandPlains;
		$landValue->[$x][$y] = 0;
		$island->{'money'} -= 30000*$seisakuflag;
		$seisakuflag++;
	    }


	if(($landKind == $HlandTown) ||
	   ($landKind == $HlandMinato) ||
	   ($landKind == $HlandSeacity)) {
	    # 町系


	my($monsterCount) =
	    countAround($land, $x, $y, $HlandMonster, 7);
            if($monsterCount > 0) {
	    $lv -= random(20)+10;
	    $landValue->[$x][$y] = $lv;
	    logMonsAttacks($id, $name, landName($landKind, $lv), "($x, $y)");
		if(($lv <= 0) &&
		   ($landKind == $HlandSeacity)) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandSea;
		    $landValue->[$x][$y] = 0;
		    next;
		} elsif($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandWaste;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    }


	my($townCount) =
	    countAround($land, $x, $y, $HlandTown, 19) +
	    countAround($land, $x, $y, $HlandProcity, 19) +
            countAround($land, $x, $y, $HlandNewtown, 19) +
	    countAround($land, $x, $y, $HlandBigtown, 19) +
	    countAround($land, $x, $y, $HlandBettown, 19) +
	    countAround($land, $x, $y, $HlandSkycity, 19) +
	    countAround($land, $x, $y, $HlandUmicity, 19) +
	    countAround($land, $x, $y, $HlandSeatown, 19) +
	    countAround($land, $x, $y, $HlandRizort, 19) +
	    countAround($land, $x, $y, $HlandKajino, 19) +
	    countAround($land, $x, $y, $HlandBigRizort, 19) +
	    countAround($land, $x, $y, $HlandShuto, 19) +
	    countAround($land, $x, $y, $HlandUmishuto, 19) +
	    countAround($land, $x, $y, $HlandMinato, 19) +
	    countAround($land, $x, $y, $HlandFrocity, 19) +
	    countAround($land, $x, $y, $HlandOnsen, 19) +
            countAround($land, $x, $y, $HlandSeacity, 19);
            if($townCount > 17) {
	        if(random(1000) < 1) {
		    if($lv > 195) {
			if($landKind == $HlandTown) {
		            $land->[$x][$y] = $HlandBigtown;
		        }
		    }
		}
	    }
	    if($addpop < 0) {
		# 不足
		$lv -= (random(-$addpop) + 1);
		if($lv <= 0) {
			if($landKind == $HlandSeacity) {
		    	$land->[$x][$y] = $HlandSea;
		    	$landValue->[$x][$y] = 0;
		    	next;
			}
		    # 平地に戻す
		    $land->[$x][$y] = $HlandPlains;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    } else {
		# 成長
		if($lv < 100) {
		    $lv += random($addpop) + 1;
		    if($lv > 100) {
			$lv = 100;
		    }
		} else {
		    # 都市になると成長遅い
		    if($addpop2 > 0) {
			$lv += random($addpop2) + 1;
		    }
		}
	    }
	    if($lv > 200) {
		$lv = 200;
	    }
	    $landValue->[$x][$y] = $lv;
	} elsif($landKind == $HlandPlains) {
	    # 平地
	    if(random(5) == 0) {
		# 周りに農場、町があれば、ここも町になる
	        if(countGrow($land, $landValue, $x, $y)){
		    $land->[$x][$y] = $HlandTown;
		    $landValue->[$x][$y] = 1;
		    if(random(1000) < $island->{'nto'}*3) {
		        $land->[$x][$y] = $HlandNewtown;
		        $landValue->[$x][$y] = 1;
		    }
		}
	    }
	} elsif($landKind == $HlandFarmchi) {

	my($FarmCount) = countAround($land, $x, $y, $HlandFarm, 7);
	my($FoodkaCount) = countAround($land, $x, $y, $HlandFoodka, 7);

		$value = $lv;

		if(($FoodkaCount > 0) && ($island->{'shouhi'} < $island->{'ene'})) {
	            $valuek = int($lv/$FoodkaCount);
		    my($i,$sx,$sy);
		    for($i = 1; $i < 7; $i++) {
		        $sx = $x + $ax[$i];
		        $sy = $y + $ay[$i];
			    # 行による位置調整
			    if((($sy % 2) == 0) && (($y % 2) == 1)) {
				$sx--;
			    }
			    if(($sx < 0) || ($sx >= $HislandSize) ||
			       ($sy < 0) || ($sy >= $HislandSize)) {
			    } else {

				if(($land->[$sx][$sy] == $HlandFoodka) && ($landValue->[$sx][$sy] == 1)) {
					$island->{'money'} += int($valuek*0.175);
					$island->{'shouhi'} += int($valuek*0.005);
				} elsif(($land->[$sx][$sy] == $HlandFoodka) && ($landValue->[$sx][$sy] == 2)) {
					$island->{'money'} += int($valuek*0.25);
					$island->{'shouhi'} += int($valuek*0.015);
				} elsif(($land->[$sx][$sy] == $HlandFoodka) && ($landValue->[$sx][$sy] == 3)) {
					$island->{'money'} += int($valuek*0.4);
					$island->{'shouhi'} += int($valuek*0.03);
				} else {

				}
			    }
			}
                } else {
	            $island->{'food'} += $value;
                }

		    $lv += random(8 + $FarmCount * 3) + 5 + $s08b;

                if($lv > 4000) {
                    $lv = 4000;
                }

	    $landValue->[$x][$y] = $lv;

	} elsif($landKind == $HlandFarmpic) {

	my($FarmCount) = countAround($land, $x, $y, $HlandFarm, 7);
	my($FoodkaCount) = countAround($land, $x, $y, $HlandFoodka, 7);

		$value = 2 * $lv;

		if(($FoodkaCount > 0) && ($island->{'shouhi'} < $island->{'ene'})) {
	            $valuek = int($lv*2/$FoodkaCount);
		    my($i,$sx,$sy);
		    for($i = 1; $i < 7; $i++) {
		        $sx = $x + $ax[$i];
		        $sy = $y + $ay[$i];
			    # 行による位置調整
			    if((($sy % 2) == 0) && (($y % 2) == 1)) {
				$sx--;
			    }
			    if(($sx < 0) || ($sx >= $HislandSize) ||
			       ($sy < 0) || ($sy >= $HislandSize)) {
			    } else {

				if(($land->[$sx][$sy] == $HlandFoodka) && ($landValue->[$sx][$sy] == 1)) {
					$island->{'money'} += int($valuek*0.175);
					$island->{'shouhi'} += int($valuek*0.005);
				} elsif(($land->[$sx][$sy] == $HlandFoodka) && ($landValue->[$sx][$sy] == 2)) {
					$island->{'money'} += int($valuek*0.25);
					$island->{'shouhi'} += int($valuek*0.015);
				} elsif(($land->[$sx][$sy] == $HlandFoodka) && ($landValue->[$sx][$sy] == 3)) {
					$island->{'money'} += int($valuek*0.4);
					$island->{'shouhi'} += int($valuek*0.03);
				} else {

				}
			    }
			}
                } else {
	            $island->{'food'} += $value;
                }

		    $lv += random(4 + $FarmCount * 2 + $s08b) + 3 + $s08b;

                if($lv > 4000) {
                    $lv = 4000;
                }

	    $landValue->[$x][$y] = $lv;

	} elsif($landKind == $HlandFarmcow) {

	my($FarmCount) = countAround($land, $x, $y, $HlandFarm, 7);
	my($FoodkaCount) = countAround($land, $x, $y, $HlandFoodka, 7);

		$value = 3 * $lv;

		if(($FoodkaCount > 0) && ($island->{'shouhi'} < $island->{'ene'})) {
	            $valuek = int($lv*3/$FoodkaCount);
		    my($i,$sx,$sy);
		    for($i = 1; $i < 7; $i++) {
		        $sx = $x + $ax[$i];
		        $sy = $y + $ay[$i];
			    # 行による位置調整
			    if((($sy % 2) == 0) && (($y % 2) == 1)) {
				$sx--;
			    }
			    if(($sx < 0) || ($sx >= $HislandSize) ||
			       ($sy < 0) || ($sy >= $HislandSize)) {

			    } else {

				if(($land->[$sx][$sy] == $HlandFoodka) && ($landValue->[$sx][$sy] == 1)) {
					$island->{'money'} += int($valuek*0.175);
					$island->{'shouhi'} += int($valuek*0.005);
				} elsif(($land->[$sx][$sy] == $HlandFoodka) && ($landValue->[$sx][$sy] == 2)) {
					$island->{'money'} += int($valuek*0.25);
					$island->{'shouhi'} += int($valuek*0.015);
				} elsif(($land->[$sx][$sy] == $HlandFoodka) && ($landValue->[$sx][$sy] == 3)) {
					$island->{'money'} += int($valuek*0.4);
					$island->{'shouhi'} += int($valuek*0.03);
				} else {

				}
			    }
			}

                } else {
	            $island->{'food'} += $value;
                }

		    $lv += random(4 + $FarmCount + $s08b) + 1 + int($s08b/2);

                if($lv > 4000) {
                    $lv = 4000;
                }

	    $landValue->[$x][$y] = $lv;

	} elsif($landKind == $HlandFoodka) {
	my($FarmchiCount) = countAround($land, $x, $y, $HlandFarmchi, 7);
	my($FarmpicCount) = countAround($land, $x, $y, $HlandFarmpic, 7);
	my($FarmcowCount) = countAround($land, $x, $y, $HlandFarmcow, 7);
	my($FarmCount) = countAround($land, $x, $y, $HlandFarm, 7);
	my($townCount) =
	    countAround($land, $x, $y, $HlandTown, 19) +
	    countAround($land, $x, $y, $HlandProcity, 19) +
            countAround($land, $x, $y, $HlandNewtown, 19) +
	    countAround($land, $x, $y, $HlandBigtown, 19) +
	    countAround($land, $x, $y, $HlandBettown, 19) +
	    countAround($land, $x, $y, $HlandSkycity, 19) +
	    countAround($land, $x, $y, $HlandUmicity, 19) +
	    countAround($land, $x, $y, $HlandSeatown, 19) +
	    countAround($land, $x, $y, $HlandRizort, 19) +
	    countAround($land, $x, $y, $HlandKajino, 19) +
	    countAround($land, $x, $y, $HlandBigRizort, 19) +
	    countAround($land, $x, $y, $HlandShuto, 19) +
	    countAround($land, $x, $y, $HlandUmishuto, 19) +
	    countAround($land, $x, $y, $HlandMinato, 19) +
	    countAround($land, $x, $y, $HlandFrocity, 19) +
	    countAround($land, $x, $y, $HlandOnsen, 19) +
            countAround($land, $x, $y, $HlandSeacity, 19);
	my($townCounta) =
	    countAround($land, $x, $y, $HlandTown, 19) +
            countAround($land, $x, $y, $HlandNewtown, 19) +
	    countAround($land, $x, $y, $HlandBigtown, 19) +
	    countAround($land, $x, $y, $HlandBettown, 19) +
	    countAround($land, $x, $y, $HlandSkycity, 19) +
	    countAround($land, $x, $y, $HlandUmicity, 19) +
	    countAround($land, $x, $y, $HlandRizort, 19) +
	    countAround($land, $x, $y, $HlandKajino, 19) +
	    countAround($land, $x, $y, $HlandBigRizort, 19);
	    if($island->{'shouhi'} > $island->{'ene'}) {
		    $lv = 0;
                } elsif(($FarmCount > 0) && ($FarmcowCount > 0) && ($FarmchiCount > 0) && ($townCounta > 3)) {
		    $lv = 3;
                } elsif(($FarmCount > 0) && ($FarmcowCount > 0) && ($townCount > 2)) {
		    $lv = 2;
                } elsif(($FarmchiCount > 0) || ($FarmpicCount > 0) || ($FarmcowCount > 0)) {
		    $lv = 1;
                } else {
		    $lv = 0;
                }
	    $landValue->[$x][$y] = $lv;

	} elsif($landKind == $HlandEneBo) {
	            $island->{'food'} -= $lv*5;

	} elsif($landKind == $HlandEneSo) {
		$landValue->[$x][$y] -= random(20);
		if($landValue->[$x][$y] <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandPlains;
		    $landValue->[$x][$y] = 0;
		    next;
		}

	} elsif($landKind == $HlandEneAt) {
		if(random(1000) < (50-int($lv/100))) {
		    $AtAttackslog = 0;
		    my($sx, $sy, $i, $landKind, $landName, $lv, $point);
		    for($i = 0; $i < 19; $i++) {
			$sx = $x + $ax[$i];
			$sy = $y + $ay[$i];

			# 行による位置調整
			if((($sy % 2) == 0) && (($y % 2) == 1)) {
			    $sx--;
			}

			$landKind = $land->[$sx][$sy];
			$lv = $landValue->[$sx][$sy];
			$landName = landName($landKind, $lv);
			$point = "($sx, $sy)";

			# 範囲外判定
			if(($sx < 0) || ($sx >= $HislandSize) ||
			   ($sy < 0) || ($sy >= $HislandSize)) {
			    next;
			}
	                if((($landKind == $HlandTown) && ($lv > 1)) ||
			  (($landKind == $HlandMinato) && ($lv > 1)) ||
			  (($landKind == $HlandProcity) && ($lv > 1)) ||
			  (($landKind == $HlandFrocity) && ($lv > 1)) ||
			  (($landKind == $HlandNewtown) && ($lv > 1)) ||
			  (($landKind == $HlandBigtown) && ($lv > 1)) ||
			  (($landKind == $HlandBettown) && ($lv > 1)) ||
			  (($landKind == $HlandSkycity) && ($lv > 1)) ||
			  (($landKind == $HlandUmicity) && ($lv > 1)) ||
			  (($landKind == $HlandRizort) && ($lv > 1)) ||
			  (($landKind == $HlandKajino) && ($lv > 1)) ||
			  (($landKind == $HlandBigRizort) && ($lv > 1)) ||
			  (($landKind == $HlandShuto) && ($lv > 1)) ||
			  (($landKind == $HlandOnsen) && ($lv > 1))) {
	                    # 町
				$landValue->[$sx][$sy] -= random(25);
				if($lv <= 0) {
				    # 平地に戻す
				    $land->[$sx][$sy] = $HlandPlains;
				    $landValue->[$sx][$sy] = 0;
				    next;
				}
				if($AtAttackslog <= 0) {
				$landKind = $land->[$x][$y];
				$lv = $landValue->[$x][$y];
				$landName = landName($landKind, $lv);
				logAtAttacks($id, $name, landName($landKind, $lv), "($x, $y)");
				$AtAttackslog++;
				}
	                }
		    }
		}

	} elsif($landKind == $HlandHTFactory) {

		if ($island->{'pika'} > 0) {
                	$landValue->[$x][$y] += 2;
                	if($landValue->[$x][$y] > 500) {
                	    $landValue->[$x][$y] = 500;
                	}
		}

	} elsif($landKind == $HlandSHTF) {

		if ($island->{'pika'} > 0) {
                	$landValue->[$x][$y] += 1;
                	if($landValue->[$x][$y] > 500) {
                	    $landValue->[$x][$y] = 500;
                	}
		}

	} elsif($landKind == $HlandForest) {
	    my($forestCount) = countAround($land, $x, $y, $HlandForest, 19);
	    # 森
	    if($lv < 200+$forestCount*200) {
		# 木を増やす
		$landValue->[$x][$y] += 1+random($forestCount)+$s08b;
	    }

	    if($lv > 200+$forestCount*200) {
		$landValue->[$x][$y] = 200+$forestCount*200;
	    }

	} elsif($landKind == $HlandTrain) {
	    if($lv == 10) {
		if(random(100) < 50) {
		$sx = $x + 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 1) || ($slv == 2) || ($slv == 3) || ($slv == 6) || ($slv == 8))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x - 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 1) || ($slv == 4) || ($slv == 5) || ($slv == 7) || ($slv == 9))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 11) {
		if(random(100) < 50) {
		$sx = $x + 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 2) || ($slv == 3) || ($slv == 6) || ($slv == 8))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x - 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 4) || ($slv == 5) || ($slv == 7) || ($slv == 9))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 12) {
		if(random(100) < 50) {
		$sx = $x + 1;
		$sy = $y - 1;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 5) || ($slv == 7) || ($slv == 8))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x - 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 4) || ($slv == 5) || ($slv == 7) || ($slv == 9))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 13) {
		if(random(100) < 50) {
		$sx = $x + 1;
		$sy = $y + 1;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 4) || ($slv == 7))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x - 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 4) || ($slv == 5) || ($slv == 7) || ($slv == 9))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 14) {
		if(random(100) < 50) {
		$sx = $x + 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 2) || ($slv == 3) || ($slv == 6) || ($slv == 8))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x - 1;
		$sy = $y - 1;
		# 行による位置調整
		if((($sy % 2) == 1) && (($y % 2) == 0)) {
		    $sx++;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 3) || ($slv == 6) || ($slv == 9))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 15) {
		if(random(100) < 50) {
		$sx = $x + 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 2) || ($slv == 3) || ($slv == 6) || ($slv == 8))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x - 1;
		$sy = $y + 1;
		# 行による位置調整
		if((($sy % 2) == 1) && (($y % 2) == 0)) {
		    $sx++;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 2) || ($slv == 6))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 16) {
		if(random(100) < 33) {
		$sx = $x + 1;
		$sy = $y - 1;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 5) || ($slv == 7) || ($slv == 8))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
	    } elsif(random(100) < 50) {
		$sx = $x + 1;
		$sy = $y + 1;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 4) || ($slv == 7))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x - 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 4) || ($slv == 5) || ($slv == 7) || ($slv == 9))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 17) {
		if(random(100) < 33) {
		$sx = $x - 1;
		$sy = $y - 1;
		# 行による位置調整
		if((($sy % 2) == 1) && (($y % 2) == 0)) {
		    $sx++;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 3) || ($slv == 6) || ($slv == 9))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
	    } elsif(random(100) < 50) {
		$sx = $x - 1;
		$sy = $y + 1;
		# 行による位置調整
		if((($sy % 2) == 1) && (($y % 2) == 0)) {
		    $sx++;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 2) || ($slv == 6))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x + 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 2) || ($slv == 3) || ($slv == 6) || ($slv == 8))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 18) {
		if(random(100) < 50) {
		$sx = $x - 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 4) || ($slv == 5) || ($slv == 7) || ($slv == 9))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x - 1;
		$sy = $y + 1;
		# 行による位置調整
		if((($sy % 2) == 1) && (($y % 2) == 0)) {
		    $sx++;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 2) || ($slv == 6))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 19) {
		if(random(100) < 50) {
		$sx = $x + 0;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 2) || ($slv == 3) || ($slv == 6) || ($slv == 8))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x + 1;
		$sy = $y + 1;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 4) || ($slv == 7))) {

			$landValue->[$sx][$sy] += 10;
			$landValue->[$x][$y] -= 10;
			$island->{'money'} += 1000;
			$island->{'trainmoney'} += 1000;
			$island->{'shouhi'} += 100;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 10;
				logStarve3($id, $name, "普通電車", "($sx, $sy)");
		            }

			}
		}
	    }

	    if($lv == 20) {
		if(random(100) < 50) {
		$sx = $x + 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 1) || ($slv == 2) || ($slv == 3) || ($slv == 6) || ($slv == 8))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x - 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 1) || ($slv == 4) || ($slv == 5) || ($slv == 7) || ($slv == 9))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 21) {
		if(random(100) < 50) {
		$sx = $x + 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 2) || ($slv == 3) || ($slv == 6) || ($slv == 8))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x - 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 4) || ($slv == 5) || ($slv == 7) || ($slv == 9))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 22) {
		if(random(100) < 50) {
		$sx = $x + 1;
		$sy = $y - 1;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 5) || ($slv == 7) || ($slv == 8))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x - 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 4) || ($slv == 5) || ($slv == 7) || ($slv == 9))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 23) {
		if(random(100) < 50) {
		$sx = $x + 1;
		$sy = $y + 1;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 4) || ($slv == 7))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x - 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 4) || ($slv == 5) || ($slv == 7) || ($slv == 9))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 24) {
		if(random(100) < 50) {
		$sx = $x + 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 2) || ($slv == 3) || ($slv == 6) || ($slv == 8))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x - 1;
		$sy = $y - 1;
		# 行による位置調整
		if((($sy % 2) == 1) && (($y % 2) == 0)) {
		    $sx++;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 3) || ($slv == 6) || ($slv == 9))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 25) {
		if(random(100) < 50) {
		$sx = $x + 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 2) || ($slv == 3) || ($slv == 6) || ($slv == 8))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x - 1;
		$sy = $y + 1;
		# 行による位置調整
		if((($sy % 2) == 1) && (($y % 2) == 0)) {
		    $sx++;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 2) || ($slv == 6))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 26) {
		if(random(100) < 33) {
		$sx = $x + 1;
		$sy = $y - 1;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 5) || ($slv == 7) || ($slv == 8))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
	    } elsif(random(100) < 50) {
		$sx = $x + 1;
		$sy = $y + 1;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 4) || ($slv == 7))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x - 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 4) || ($slv == 5) || ($slv == 7) || ($slv == 9))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 27) {
		if(random(100) < 33) {
		$sx = $x - 1;
		$sy = $y - 1;
		# 行による位置調整
		if((($sy % 2) == 1) && (($y % 2) == 0)) {
		    $sx++;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 3) || ($slv == 6) || ($slv == 9))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
	    } elsif(random(100) < 50) {
		$sx = $x - 1;
		$sy = $y + 1;
		# 行による位置調整
		if((($sy % 2) == 1) && (($y % 2) == 0)) {
		    $sx++;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 2) || ($slv == 6))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x + 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 2) || ($slv == 3) || ($slv == 6) || ($slv == 8))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 28) {
		if(random(100) < 50) {
		$sx = $x - 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 4) || ($slv == 5) || ($slv == 7) || ($slv == 9))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x - 1;
		$sy = $y + 1;
		# 行による位置調整
		if((($sy % 2) == 1) && (($y % 2) == 0)) {
		    $sx++;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 2) || ($slv == 6))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
		}
	    } elsif($lv == 29) {
		if(random(100) < 50) {
		$sx = $x + 1;
		$sy = $y + 0;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 0) || ($slv == 1) || ($slv == 2) || ($slv == 3) || ($slv == 6) || ($slv == 8))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
	    } else {
		$sx = $x + 1;
		$sy = $y + 1;
		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}
		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}
			my($sl) = $land->[$sx][$sy];
			my($slv) = $landValue->[$sx][$sy];
			if(($land->[$sx][$sy] == $HlandTrain) && (($slv == 4) || ($slv == 7))) {

			$landValue->[$sx][$sy] += 20;
			$landValue->[$x][$y] -= 20;
			$island->{'money'} += 500;
			$island->{'trainmoney2'} += 500;
			$island->{'shouhi'} += 10;

			    if($island->{'shouhi'} > $island->{'ene'}) {
				$landValue->[$sx][$sy] -= 20;
				logStarve3($id, $name, "貨物列車", "($sx, $sy)");
		            }

			}
		}
	    }

	} elsif($landKind == $HlandKura) {
	    $seq = int($lv/100);
	    $choki = $lv%100;
	    if(random(100) < 9-$seq) {
		$choki = int($choki/100*random(100));
		$seq--;
			if($seq < 0) {
			$seq = 0;
			}
		$landValue->[$x][$y] = $seq*100+$choki;
		my($lName) = &landName($landKind, $lv);
		logKuralupin($id, $name, $lName, "($x, $y)");
	    }

	    if($anothermood == 1) {
		$choki -= int($choki/100*$seq);
			if($choki < 0) {
			$choki = 0;
			}
		$landValue->[$x][$y] = $seq*100+$choki;
	    }

	} elsif($landKind == $HlandHouse) {

		$zeikin = int($island->{'pop'}*($lv+1)*$island->{'eisei1'}/100);

		if($anothermood == 1) {
                    $island->{'money'} += $zeikin;
		}else{

		if($zeikin > 10000) {
		    if($HislandTurn % 5 == 0) {
                    $island->{'money'} += $zeikin;
		    }else{
		    }
		}elsif($zeikin > 5000) {
		    if($HislandTurn % 2 == 0) {
                    $island->{'money'} += $zeikin;
		    }else{
		    }
		}else{
                    $island->{'money'} += $zeikin;
		}

		}

	} elsif($landKind == $HlandDefence) {
	    if($lv == 1) {
		# 防衛施設自爆
		my($lName) = &landName($landKind, $lv);
		logBombFire($id, $name, $lName, "($x, $y)");

		# 広域被害ルーチン
		wideDamage($id, $name, $land, $landValue, $x, $y);
	    }
	} elsif($landKind == $HlandProcity) {
	    # 防災都市
	    if($addpop < 0) {
		# 不足
		$lv -= (random(-$addpop) + 1);
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandPlains;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    } else {
		# 成長
		if($lv < 100) {
		    $lv += random($addpop) + 1;
		    if($lv > 100) {
			$lv = 100;
		    }
		} else {
		    # 都市になると成長遅い
		    if($addpop2 > 0) {
			$lv += random($addpop2) + 1;
		    }
		}
	    }
	    if($lv > 200) {
		$lv = 200;
	    }
	    $landValue->[$x][$y] = $lv;

	    if($lv == 200) {

	    my($i,$sx,$sy);
	    for($i = 1; $i < 7; $i++) {
	        $sx = $x + $ax[$i];
	        $sy = $y + $ay[$i];
	    if($land->[$sx][$sy] == $HlandMonster){
		# 周囲2Hexに別の怪獣がいる場合、その怪獣を攻撃する

		# 対象となる怪獣の各要素取り出し
		my($tKind, $tName, $tHp) = monsterSpec($landValue->[$sx][$sy]);
		my($tlv) = $landValue->[$sx][$sy];
		my($tspecial) = $HmonsterSpecial[$tKind];

		    logBariaAttack($id, $name, $tName, "($sx, $sy)");
	    # 対象の怪獣が倒れて荒地になる
		$land->[$sx][$sy] = $HlandWaste;
		$landValue->[$sx][$sy] = 1;
	    next;
	    }
	    }
	    }

	} elsif($landKind == $HlandNewtown) {
	    # ニュータウン系
	my($townCount) =
	    countAround($land, $x, $y, $HlandTown, 19) +
	    countAround($land, $x, $y, $HlandProcity, 19) +
            countAround($land, $x, $y, $HlandNewtown, 19) +
	    countAround($land, $x, $y, $HlandBigtown, 19) +
	    countAround($land, $x, $y, $HlandBettown, 19) +
	    countAround($land, $x, $y, $HlandSkycity, 19) +
	    countAround($land, $x, $y, $HlandUmicity, 19) +
	    countAround($land, $x, $y, $HlandSeatown, 19) +
	    countAround($land, $x, $y, $HlandRizort, 19) +
	    countAround($land, $x, $y, $HlandKajino, 19) +
	    countAround($land, $x, $y, $HlandBigRizort, 19) +
	    countAround($land, $x, $y, $HlandShuto, 19) +
	    countAround($land, $x, $y, $HlandUmishuto, 19) +
	    countAround($land, $x, $y, $HlandMinato, 19) +
	    countAround($land, $x, $y, $HlandFrocity, 19) +
	    countAround($land, $x, $y, $HlandOnsen, 19) +
            countAround($land, $x, $y, $HlandSeacity, 19);
            if($townCount > 17) {
	        if(random(1000) < 3) {
		    if($lv > 295) {
		        $land->[$x][$y] = $HlandBigtown;
		    }
		}
	    }
	    if($addpop < 0) {
		# 不足
		$lv -= (random(-$addpop) + 1);
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandPlains;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    } else {
		# 成長
		if($lv < 100) {
		    $lv += random($addpop) + 1;
		    if($lv > 100) {
			$lv = 100;
		    }
		} else {
		    # 都市になると成長遅い
		    if($addpop2 > 0) {
			$lv += random($addpop2) + 1;
		    }
		}
	    }
	    if($lv > 300) {
		$lv = 300;
	    }
	    $landValue->[$x][$y] = $lv;

	} elsif($landKind == $HlandBigtown) {


	my($monsterCount) =
	    countAround($land, $x, $y, $HlandMonster, 7);
            if($monsterCount > 0) {
	    $lv -= random(20)+10;
	    $landValue->[$x][$y] = $lv;
	    logMonsAttacks($id, $name, landName($landKind, $lv), "($x, $y)");
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandWaste;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    }


	my($townCount) =
	    countAround($land, $x, $y, $HlandTown, 19) +
	    countAround($land, $x, $y, $HlandProcity, 19) +
            countAround($land, $x, $y, $HlandNewtown, 19) +
	    countAround($land, $x, $y, $HlandBigtown, 19) +
	    countAround($land, $x, $y, $HlandBettown, 19) +
	    countAround($land, $x, $y, $HlandSkycity, 19) +
	    countAround($land, $x, $y, $HlandUmicity, 19) +
	    countAround($land, $x, $y, $HlandSeatown, 19) +
	    countAround($land, $x, $y, $HlandRizort, 19) +
	    countAround($land, $x, $y, $HlandKajino, 19) +
	    countAround($land, $x, $y, $HlandBigRizort, 19) +
	    countAround($land, $x, $y, $HlandShuto, 19) +
	    countAround($land, $x, $y, $HlandUmishuto, 19) +
	    countAround($land, $x, $y, $HlandMinato, 19) +
	    countAround($land, $x, $y, $HlandFrocity, 19) +
	    countAround($land, $x, $y, $HlandOnsen, 19) +
            countAround($land, $x, $y, $HlandSeacity, 19);
	my($houseCount) =
	    countAround($land, $x, $y, $HlandHouse, 7);
            if(($island->{'shu'} == 0) &&
		($houseCount == 1) &&
		($townCount > 16) &&
		(random(1000) < 300)) {
		        $land->[$x][$y] = $HlandShuto;
			my($onm);
			$onm = $island->{'onm'};
			$island->{'totoyoso2'} = "$onmシティー";
				logShuto($id, $name, landName($landKind, $lv), "$onmシティー", "($x, $y)");
		    $island->{'shu'}++;
	    }
	    # 現代都市系
	    if($addpop < 0) {
		# 不足
		$lv -= (random(-$addpop) + 1);
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandPlains;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    } else {
		# 成長
		if($lv < 200) {
		    $lv += random($addpop) + 1;
		    if($lv > 200) {
			$lv = 200;
		    }
		} else {
		    # 都市になると成長遅い
		    if($addpop2 > 0) {
			$lv += random($addpop2) + 1;
		    }
		}
	    }
	    if($lv > 500) {
		$lv = 500;
	    }
	    $landValue->[$x][$y] = $lv;

	} elsif($landKind == $HlandSeatown) {
	    # 海底新都市系
	my($townCount) =
	    countAround($land, $x, $y, $HlandTown, 19) +
	    countAround($land, $x, $y, $HlandProcity, 19) +
            countAround($land, $x, $y, $HlandNewtown, 19) +
	    countAround($land, $x, $y, $HlandBigtown, 19) +
	    countAround($land, $x, $y, $HlandBettown, 19) +
	    countAround($land, $x, $y, $HlandSkycity, 19) +
	    countAround($land, $x, $y, $HlandUmicity, 19) +
	    countAround($land, $x, $y, $HlandSeatown, 19) +
	    countAround($land, $x, $y, $HlandRizort, 19) +
	    countAround($land, $x, $y, $HlandKajino, 19) +
	    countAround($land, $x, $y, $HlandBigRizort, 19) +
	    countAround($land, $x, $y, $HlandShuto, 19) +
	    countAround($land, $x, $y, $HlandUmishuto, 19) +
	    countAround($land, $x, $y, $HlandMinato, 19) +
	    countAround($land, $x, $y, $HlandFrocity, 19) +
	    countAround($land, $x, $y, $HlandOnsen, 19) +
            countAround($land, $x, $y, $HlandSeacity, 19);
	my($houseCount) =
	    countAround($land, $x, $y, $HlandHouse, 7);
            if(($island->{'shu'} == 0) &&
		($houseCount == 1) &&
		($townCount > 16) &&
		(random(1000) < 300)) {
		        $land->[$x][$y] = $HlandUmishuto;
			my($onm);
			$onm = $island->{'onm'};
			$island->{'totoyoso2'} = "$onmシティー";
				logShuto($id, $name, landName($landKind, $lv), "$onmシティー", "($x, $y)");
		    $island->{'shu'}++;
	    }
	    if($addpop < 0) {
		# 不足
		$lv -= (random(-$addpop) + 1);
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandSea;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    } else {
		# 成長
		if($lv < 250) {
		    $lv += random($addpop) + 1;
		    if($lv > 250) {
			$lv = 250;
		    }
		} else {
		    # 都市になると成長遅い
		    if($addpop2 > 0) {
			$lv += random($addpop2) + 1;
		    }
		}
	    }
	    if($lv > 400) {
		$lv = 400;
	    }
	    $landValue->[$x][$y] = $lv;



	} elsif($landKind == $HlandBettown) {


	my($monsterCount) =
	    countAround($land, $x, $y, $HlandMonster, 7);
            if($monsterCount > 0) {
	    $lv -= random(20)+10;
	    $landValue->[$x][$y] = $lv;
	    logMonsAttacks($id, $name, landName($landKind, $lv), "($x, $y)");
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandWaste;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    }

	my($shutoCount) =
	    countAround($land, $x, $y, $HlandShuto, 7) +
	    countAround($land, $x, $y, $HlandUmishuto, 7);
	my($betCount) =
	    countAround($land, $x, $y, $HlandBettown, 7);

	    if($addpop < 0) {
		# 不足
		$lv -= (random(-$addpop) + 1);
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandPlains;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    } else {
		# 成長

		if(($island->{'shu'} > 0) &&
		  (($shutoCount > 0) ||
		   ($betCount > 1))) {

		if($lv < 1000) {
		    $lv += random($addpop) + 1;
		    if($lv > 1000) {
			$lv = 1000;
		    }
		} else {
		    # 都市になると成長遅い
		    if($addpop2 > 0) {
			$lv += random($addpop2) + 1;
		    }
		}

		}

	    }
	    if($lv > 2000) {
		$lv = 2000;
	    }
	    $landValue->[$x][$y] = $lv;

	} elsif($landKind == $HlandSkycity) {


	my($monsterCount) =
	    countAround($land, $x, $y, $HlandMonster, 7);
            if($monsterCount > 0) {
	    $lv -= random(20)+10;
	    $landValue->[$x][$y] = $lv;
	    logMonsAttacks($id, $name, landName($landKind, $lv), "($x, $y)");
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandWaste;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    }

	    if($addpop < 0) {
		# 不足
		$lv -= (random(-$addpop) + 1);
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandPlains;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    } else {
		# 成長

		if($lv < 2250) {
		    $lv += random($addpop) + 1;
		} else {
		    # 都市になると成長遅い
		    if($addpop2 > 0) {
			$lv += random($addpop2) + 1;
		    }
		}

	    }
	    if($lv > 3000) {
		$lv = 3000;
	    }
	    $landValue->[$x][$y] = $lv;

	} elsif($landKind == $HlandUmicity) {

	my($monsterCount) =
	    countAround($land, $x, $y, $HlandMonster, 7);
            if($monsterCount > 0) {
	    $lv -= random(20)+10;
	    $landValue->[$x][$y] = $lv;
	    logMonsAttacks($id, $name, landName($landKind, $lv), "($x, $y)");
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandSea;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    }

	    if($addpop < 0) {
		# 不足
		$lv -= (random(-$addpop) + 1);
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandSea;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    } else {
		# 成長

		if($lv < 2500) {
		    $lv += random($addpop) + 1;
		} else {
		    # 都市になると成長遅い
		    if($addpop2 > 0) {
			$lv += random($addpop2) + 1;
		    }
		}

	    }
	    if($lv > 3000) {
		$lv = 3000;
	    }
	    $landValue->[$x][$y] = $lv;

	} elsif(($landKind == $HlandShuto) ||
		($landKind == $HlandUmishuto)) {
	    # 首都系

		if($island->{'shu'} > 1) {
		    $land->[$x][$y] = $HlandPlains2;
		    $landValue->[$x][$y] = 0;
		    $island->{'shu'} -= 1;
		}

	my($monsterCount) =
	    countAround($land, $x, $y, $HlandMonster, 7);
            if($monsterCount > 0) {
	    $lv -= random(100)+200;
	    $landValue->[$x][$y] = $lv;
	    logMonsAttacks($id, $name, landName($landKind, $lv), "($x, $y)");
		if(($lv <= 0) &&
		   ($landKind == $HlandUmishuto)) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandSea;
		    $landValue->[$x][$y] = 0;
		    next;
		}
		if(($lv <= 0) &&
		   ($landKind == $HlandShuto)) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandPlains;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    }

	    if($addpop < 0) {
		# 不足
		$lv -= (random(-$addpop) + 1);
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandSea;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    } else {
		# 成長
		if($lv < 750) {
		    $lv += random($addpop) + 1;
		    if($lv > 750) {
			$lv = 750;
		    }
		} else {
		    # 都市になると成長遅い
		    if($addpop2 > 0) {
			$lv += random($addpop2) + 1;
		    }
		}
	    }
	    if($lv > 4000) {
		$lv = 4000;
	    }
	    $landValue->[$x][$y] = $lv;

	} elsif($landKind == $HlandRizort) {
	    # リゾート系

    # 観光はいいよねー
    if(($lv < 400) && (rand(500) < 15+$s06b*2)) {
        my(@order) = randomArray($HislandNumber);
        my($migrate);

        # 観光先を探す
        my($tIsland);
        my($n) = min($HislandNumber, 5);
        my($i);
        for($i = 0; $i < $n; $i++) { # ５島まで調べる
            $tIsland = $Hislands[$order[$i]];

	    $tetc5 = $tIsland->{'etc5'};
	    $tetc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($ts00,$ts01,$ts02,$ts03,$ts04,$ts05,$ts06,$ts07,$ts08,$ts09,$ts10,$ts11,$ts12,$ts13,$ts14,$ts15,$ts16,$ts17,$ts18,$ts19,$ts20,$ts21,$ts22,$ts23,$ts24,$ts25,$ts26,$ts27,$ts28,$ts29,$ts30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
	    $ts06b = int($ts06/5);

            # 人口の多い島に観光する
            if ($island->{'pop'} < $tIsland->{'pop'}) {
		my($seaCount) = countAround($land, $x, $y, $HlandSea, 19);
		my($forestCount) = countAround($land, $x, $y, $HlandForest, 19);
		my($mountainCount) = countAround($land, $x, $y, $HlandMountain, 19);
		my($parkCount) = countAround($land, $x, $y, $HlandPark, 19);
		my($kyujoCount) = countAround($land, $x, $y, $HlandKyujo, 19);
		my($kyujoCount) = countAround($land, $x, $y, $HlandKyujokai, 19);
		my($umiamuCount) = countAround($land, $x, $y, $HlandUmiamu, 19);
		my($sunahamaCount) = countAround($land, $x, $y, $HlandSunahama, 19);
		my($rizortCount) = (countAround($land, $x, $y, $HlandRizort, 19) + countAround($land, $x, $y, $HlandKajino, 19) + countAround($land, $x, $y, $HlandBigRizort, 19));
                $landKind = $land->[$x][$y];
                $lv = $landValue->[$x][$y];
		$migrate = $seaCount*3 + $forestCount*3 + $mountainCount*3 + $parkCount*4 + $kyujoCount*4 + $umiamuCount*7 + $sunahamaCount*10 + $rizortCount*5 + $s06b*10 - $ts06b*10;

			if ($migrate < 0) {
			    $migrate = 1;
			}

		$lv += $migrate;
            logKankouMigrate($id, $tIsland->{'id'}, $name, landName($landKind, $lv), $tIsland->{'name'}, "($x, $y)", $migrate);
            }
                last if ($employed <= 0);
        }

            $island->{'eisei2'} += $migrate;
            $island->{'pop'} += $migrate;
            $tIsland->{'pop'} -= $migrate;

            # 観光にきてくれた分人口減少
            my($tLand) = $tIsland->{'land'};
            my($tLandValue) = $tIsland->{'landValue'};
            my($employed) = $migrate;
            my($x, $y, $landKind, $lv);
            for($i = 0; $i < $HpointNumber; $i++) {
                $x = $Hrpx[$i];
                $y = $Hrpy[$i];
                $landKind = $tLand->[$x][$y];
                $lv = $tLandValue->[$x][$y];

                if((($landKind == $HlandTown) && ($lv > 1)) ||
		  (($landKind == $HlandMinato) && ($lv > 1)) ||
		  (($landKind == $HlandProcity) && ($lv > 1)) ||
		  (($landKind == $HlandFrocity) && ($lv > 1)) ||
		  (($landKind == $HlandNewtown) && ($lv > 1)) ||
		  (($landKind == $HlandBigtown) && ($lv > 1)) ||
		  (($landKind == $HlandBettown) && ($lv > 1)) ||
		  (($landKind == $HlandSkycity) && ($lv > 1)) ||
		  (($landKind == $HlandUmicity) && ($lv > 1)) ||
		  (($landKind == $HlandSeatown) && ($lv > 1)) ||
		  (($landKind == $HlandRizort) && ($lv > 1)) ||
		  (($landKind == $HlandKajino) && ($lv > 1)) ||
		  (($landKind == $HlandBigRizort) && ($lv > 1)) ||
		  (($landKind == $HlandShuto) && ($lv > 1)) ||
		  (($landKind == $HlandUmishuto) && ($lv > 1)) ||
		  (($landKind == $HlandOnsen) && ($lv > 1)) ||
		  (($landKind == $HlandSeacity) && ($lv > 1))) {
                    # 町
                    $n = min($lv - 1, $employed);
                    $tLandValue->[$x][$y] -= $n;
                    $employed -= $n;

			if($tLandValue->[$x][$y] <= 0) {
			    $tLand->[$x][$y] = $HlandPlains;
			    $tLandValue->[$x][$y] = 0;
			}

                }
            }
	}

	    if($addpop < 0) {
		# 不足
		$lv -= (random(-$addpop) + 1);
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandPlains;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    } else {
		# 成長
		if($lv < 10) {
		    $lv += random($addpop) + 1;
		    if($lv > 10) {
			$lv = 10;
		    }
		} else {
		    if($addpop2 > 0) {
			$lv += random($addpop2) + 1;
		    }
		}
	    }
	    if($lv > 400) {
		$lv = 400;
	    }
	    $landValue->[$x][$y] = $lv;

		my($seaCount) = countAround($land, $x, $y, $HlandSea, 7);
		my($forestCount) = countAround($land, $x, $y, $HlandForest, 7);
		my($mountainCount) = countAround($land, $x, $y, $HlandMountain, 7);
		my($sunahamaCount) = countAround($land, $x, $y, $HlandSunahama, 7);
		my($onsenCount) = countAround($land, $x, $y, $HlandOnsen, 7);
		my($parkCount) = countAround($land, $x, $y, $HlandPark, 7);
		my($kajinoCount) = countAround($land, $x, $y, $HlandKajino, 7);

		$miryoku = ((2*$seaCount/10)+(5*$forestCount/10)+(5*$mountainCount/10)+(20*$sunahamaCount/10)+(20*$onsenCount/10)+(10*$parkCount/10)+(2*$kajinoCount/10))+1;

            my($value);
            $value = $miryoku * ($lv+$island->{'eis1'}+$island->{'eis2'}+$island->{'eis3'}+$island->{'eis5'}+int($island->{'fore'}/10)+int($island->{'rena'}/25)-$island->{'monsterlive'}*100);

	    if($island->{'shouhi'} > $island->{'ene'}) {
            $value = int($value/2);
            }

            if ($value > 0) {
                $rizortincome += int($value);
		$island->{'money'} += int($value);
            }

	} elsif($landKind == $HlandBigRizort) {
	    # リゾート系

    # 観光はいいよねー
    if(($lv < 1000) && (rand(500) < 20+$s06b*2)) {
        my(@order) = randomArray($HislandNumber);
        my($migrate);

        # 観光先を探す
        my($tIsland);
        my($n) = min($HislandNumber, 5);
        my($i);
        for($i = 0; $i < $n; $i++) { # ５島まで調べる
            $tIsland = $Hislands[$order[$i]];

	    $tetc5 = $tIsland->{'etc5'};
	    $tetc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($ts00,$ts01,$ts02,$ts03,$ts04,$ts05,$ts06,$ts07,$ts08,$ts09,$ts10,$ts11,$ts12,$ts13,$ts14,$ts15,$ts16,$ts17,$ts18,$ts19,$ts20,$ts21,$ts22,$ts23,$ts24,$ts25,$ts26,$ts27,$ts28,$ts29,$ts30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
	    $ts06b = int($ts06/5);

            # 人口の多い島に観光する
            if ($island->{'pop'} < $tIsland->{'pop'}) {
		my($seaCount) = countAround($land, $x, $y, $HlandSea, 19);
		my($forestCount) = countAround($land, $x, $y, $HlandForest, 19);
		my($mountainCount) = countAround($land, $x, $y, $HlandMountain, 19);
		my($parkCount) = countAround($land, $x, $y, $HlandPark, 19);
		my($kyujoCount) = countAround($land, $x, $y, $HlandKyujo, 19);
		my($kyujoCount) = countAround($land, $x, $y, $HlandKyujokai, 19);
		my($umiamuCount) = countAround($land, $x, $y, $HlandUmiamu, 19);
		my($sunahamaCount) = countAround($land, $x, $y, $HlandSunahama, 19);
		my($rizortCount) = (countAround($land, $x, $y, $HlandRizort, 19) + countAround($land, $x, $y, $HlandKajino, 19) + countAround($land, $x, $y, $HlandBigRizort, 19));
                $landKind = $land->[$x][$y];
                $lv = $landValue->[$x][$y];
		$migrate = $seaCount*3 + $forestCount*3 + $mountainCount*3 + $parkCount*4 + $kyujoCount*4 + $umiamuCount*7 + $sunahamaCount*10 + $rizortCount*5 + $s06b*10 - $ts06b*10;

			if ($migrate < 0) {
			    $migrate = 1;
			}

		$lv += $migrate;
            logKankouMigrate($id, $tIsland->{'id'}, $name, landName($landKind, $lv), $tIsland->{'name'}, "($x, $y)", $migrate);
            }
                last if ($employed <= 0);
        }

            $island->{'eisei2'} += $migrate;
            $island->{'pop'} += $migrate;
            $tIsland->{'pop'} -= $migrate;

            # 観光にきてくれた分人口減少
            my($tLand) = $tIsland->{'land'};
            my($tLandValue) = $tIsland->{'landValue'};
            my($employed) = $migrate;
            my($x, $y, $landKind, $lv);
            for($i = 0; $i < $HpointNumber; $i++) {
                $x = $Hrpx[$i];
                $y = $Hrpy[$i];
                $landKind = $tLand->[$x][$y];
                $lv = $tLandValue->[$x][$y];

                if((($landKind == $HlandTown) && ($lv > 1)) ||
		  (($landKind == $HlandMinato) && ($lv > 1)) ||
		  (($landKind == $HlandProcity) && ($lv > 1)) ||
		  (($landKind == $HlandFrocity) && ($lv > 1)) ||
		  (($landKind == $HlandNewtown) && ($lv > 1)) ||
		  (($landKind == $HlandBigtown) && ($lv > 1)) ||
		  (($landKind == $HlandBettown) && ($lv > 1)) ||
		  (($landKind == $HlandSkycity) && ($lv > 1)) ||
		  (($landKind == $HlandUmicity) && ($lv > 1)) ||
		  (($landKind == $HlandSeatown) && ($lv > 1)) ||
		  (($landKind == $HlandRizort) && ($lv > 1)) ||
		  (($landKind == $HlandKajino) && ($lv > 1)) ||
		  (($landKind == $HlandBigRizort) && ($lv > 1)) ||
		  (($landKind == $HlandShuto) && ($lv > 1)) ||
		  (($landKind == $HlandUmishuto) && ($lv > 1)) ||
		  (($landKind == $HlandOnsen) && ($lv > 1)) ||
		  (($landKind == $HlandSeacity) && ($lv > 1))) {
                    # 町
                    $n = min($lv - 1, $employed);
                    $tLandValue->[$x][$y] -= $n;
                    $employed -= $n;

			if($tLandValue->[$x][$y] <= 0) {
			    $tLand->[$x][$y] = $HlandPlains;
			    $tLandValue->[$x][$y] = 0;
			}

                }
            }
	}

	    if($addpop < 0) {
		# 不足
		$lv -= (random(-$addpop) + 1);
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandPlains;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    } else {
		# 成長
		if($lv < 10) {
		    $lv += random($addpop) + 1;
		    if($lv > 10) {
			$lv = 10;
		    }
		} else {
		    if($addpop2 > 0) {
			$lv += random($addpop2) + 1;
		    }
		}
	    }
	    if($lv > 1000) {
		$lv = 1000;
	    }
	    $landValue->[$x][$y] = $lv;

	my($monsterCount) =
	    countAround($land, $x, $y, $HlandMonster, 7);
            if($monsterCount > 0) {
	    $lv -= random(20)+10;
	    $landValue->[$x][$y] = $lv;
	    logMonsAttacks($id, $name, landName($landKind, $lv), "($x, $y)");
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandWaste;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    }
	} elsif($landKind == $HlandKajino) {
	    # リゾート系

    # 観光はいいよねー
    if(($lv < 2000) && (rand(500) < 15+$s06b*2)) {
        my(@order) = randomArray($HislandNumber);
        my($migrate);

        # 観光先を探す
        my($tIsland);
        my($n) = min($HislandNumber, 5);
        my($i);
        for($i = 0; $i < $n; $i++) { # ５島まで調べる
            $tIsland = $Hislands[$order[$i]];

	    $tetc5 = $tIsland->{'etc5'};
	    $tetc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($ts00,$ts01,$ts02,$ts03,$ts04,$ts05,$ts06,$ts07,$ts08,$ts09,$ts10,$ts11,$ts12,$ts13,$ts14,$ts15,$ts16,$ts17,$ts18,$ts19,$ts20,$ts21,$ts22,$ts23,$ts24,$ts25,$ts26,$ts27,$ts28,$ts29,$ts30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
	    $ts06b = int($ts06/5);

            # 人口の多い島に観光する
            if ($island->{'pop'} < $tIsland->{'pop'}) {
		my($seaCount) = countAround($land, $x, $y, $HlandSea, 19);
		my($forestCount) = countAround($land, $x, $y, $HlandForest, 19);
		my($mountainCount) = countAround($land, $x, $y, $HlandMountain, 19);
		my($parkCount) = countAround($land, $x, $y, $HlandPark, 19);
		my($kyujoCount) = countAround($land, $x, $y, $HlandKyujo, 19);
		my($kyujoCount) = countAround($land, $x, $y, $HlandKyujokai, 19);
		my($umiamuCount) = countAround($land, $x, $y, $HlandUmiamu, 19);
		my($sunahamaCount) = countAround($land, $x, $y, $HlandSunahama, 19);
		my($rizortCount) = (countAround($land, $x, $y, $HlandRizort, 19) + countAround($land, $x, $y, $HlandKajino, 19) + countAround($land, $x, $y, $HlandBigRizort, 19));
                $landKind = $land->[$x][$y];
                $lv = $landValue->[$x][$y];
		$migrate = $seaCount*3 + $forestCount*3 + $mountainCount*3 + $parkCount*4 + $kyujoCount*4 + $umiamuCount*7 + $sunahamaCount*10 + $rizortCount*5 + $s06b*10 - $ts06b*10;

			if ($migrate < 0) {
			    $migrate = 1;
			}

		$lv += $migrate;
            logKankouMigrate($id, $tIsland->{'id'}, $name, landName($landKind, $lv), $tIsland->{'name'}, "($x, $y)", $migrate);
            }
                last if ($employed <= 0);
        }

            $island->{'eisei2'} += $migrate;
            $island->{'pop'} += $migrate;
            $tIsland->{'pop'} -= $migrate;

            # 観光にきてくれた分人口減少
            my($tLand) = $tIsland->{'land'};
            my($tLandValue) = $tIsland->{'landValue'};
            my($employed) = $migrate;
            my($x, $y, $landKind, $lv);
            for($i = 0; $i < $HpointNumber; $i++) {
                $x = $Hrpx[$i];
                $y = $Hrpy[$i];
                $landKind = $tLand->[$x][$y];
                $lv = $tLandValue->[$x][$y];

                if((($landKind == $HlandTown) && ($lv > 1)) ||
		  (($landKind == $HlandMinato) && ($lv > 1)) ||
		  (($landKind == $HlandProcity) && ($lv > 1)) ||
		  (($landKind == $HlandFrocity) && ($lv > 1)) ||
		  (($landKind == $HlandNewtown) && ($lv > 1)) ||
		  (($landKind == $HlandBigtown) && ($lv > 1)) ||
		  (($landKind == $HlandBettown) && ($lv > 1)) ||
		  (($landKind == $HlandSkycity) && ($lv > 1)) ||
		  (($landKind == $HlandUmicity) && ($lv > 1)) ||
		  (($landKind == $HlandSeatown) && ($lv > 1)) ||
		  (($landKind == $HlandRizort) && ($lv > 1)) ||
		  (($landKind == $HlandKajino) && ($lv > 1)) ||
		  (($landKind == $HlandBigRizort) && ($lv > 1)) ||
		  (($landKind == $HlandShuto) && ($lv > 1)) ||
		  (($landKind == $HlandUmishuto) && ($lv > 1)) ||
		  (($landKind == $HlandOnsen) && ($lv > 1)) ||
		  (($landKind == $HlandSeacity) && ($lv > 1))) {
                    # 町
                    $n = min($lv - 1, $employed);
                    $tLandValue->[$x][$y] -= $n;
                    $employed -= $n;

			if($tLandValue->[$x][$y] <= 0) {
			    $tLand->[$x][$y] = $HlandPlains;
			    $tLandValue->[$x][$y] = 0;
			}

                }
            }
	}

	    if($addpop < 0) {
		# 不足
		$lv -= (random(-$addpop) + 1);
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandPlains;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    } else {
		# 成長
		if($lv < 10) {
		    $lv += random($addpop) + 1;
		    if($lv > 10) {
			$lv = 10;
		    }
		} else {
		    if($addpop2 > 0) {
			$lv += random($addpop2) + 1;
		    }
		}
	    }
	    if($lv > 2500) {
		$lv = 2500;
	    }
	    $landValue->[$x][$y] = $lv;

		my($seaCount) = countAround($land, $x, $y, $HlandSea, 7);
		my($forestCount) = countAround($land, $x, $y, $HlandForest, 7);
		my($mountainCount) = countAround($land, $x, $y, $HlandMountain, 7);
		my($sunahamaCount) = countAround($land, $x, $y, $HlandSunahama, 7);
		my($onsenCount) = countAround($land, $x, $y, $HlandOnsen, 7);
		my($parkCount) = countAround($land, $x, $y, $HlandPark, 7);
		my($kajinoCount) = countAround($land, $x, $y, $HlandRizort, 7);

		$miryoku = ((2*$seaCount/10)+(5*$forestCount/10)+(5*$mountainCount/10)+(20*$sunahamaCount/10)+(20*$onsenCount/10)+(10*$parkCount/10)+(2*$kajinoCount/10))+1;

            my($value);
            $value = int(($lv+$island->{'eis1'}+$island->{'eis2'}+$island->{'eis3'}+$island->{'eis5'}+int($island->{'fore'}/10)+int($island->{'rena'}/10)-$island->{'monsterlive'}*100) / 5 * $miryoku);

	    if($island->{'shouhi'} > $island->{'ene'}) {
            $value = -($value*10);

		$lv -= (random(250) + 100);
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandPlains;
		    $landValue->[$x][$y] = 0;
		    next;
		}
		$landValue->[$x][$y] = $lv;

            }

                $rizortincome += int($value);
		$island->{'money'} += int($value);

	my($monsterCount) =
	    countAround($land, $x, $y, $HlandMonster, 7);
            if($monsterCount > 0) {
	    $lv -= random(20)+10;
	    $landValue->[$x][$y] = $lv;
	    logMonsAttacks($id, $name, landName($landKind, $lv), "($x, $y)");
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandWaste;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    }

	} elsif($landKind == $HlandOnsen) {
	    # 温泉系
	    if($addpop < 0) {
		# 不足
		$lv -= (random(-$addpop) + 1);
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandPlains;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    } else {
		# 成長
		if($lv < 50) {
		    $lv += random($addpop) + 1;
		    if($lv > 50) {
			$lv = 50;
		    }
		} else {
		    # 都市になると成長遅い
		    if($addpop2 > 0) {
			$lv += random($addpop2) + 1;
		    }
		}
	    }
	    if($lv > 100) {
		$lv = 100;
	    }
	    $landValue->[$x][$y] = $lv;

            my($nt) = (countAround($land, $x, $y, $HlandTown, 19) + countAround($land, $x, $y, $HlandProcity, 19) + countAround($land, $x, $y, $HlandMinato, 19) + countAround($land, $x, $y, $HlandSeacity, 19) + countAround($land, $x, $y, $HlandFrocity, 19) + countAround($land, $x, $y, $HlandNewtown, 19) + countAround($land, $x, $y, $HlandBigtown, 19) + countAround($land, $x, $y, $HlandBettown, 19) + countAround($land, $x, $y, $HlandSkycity, 19) + countAround($land, $x, $y, $HlandUmicity, 19) + countAround($land, $x, $y, $HlandSeatown, 19) + countAround($land, $x, $y, $HlandOnsen, 19) + countAround($land, $x, $y, $HlandShuto, 19) + countAround($land, $x, $y, $HlandUmishuto, 19) + countAround($land, $x, $y, $HlandRizort, 19) + countAround($land, $x, $y, $HlandKajino, 19) + countAround($land, $x, $y, $HlandBigRizort, 19));
            my($value);
            $value = random($nt * 20 + $lv * 5 + int($island->{'pop'} / 20)) + random(100) + 100;
            if ($value > 0) {
                $island->{'money'} += $value;

                # 収入ログ
                my($str) = "$value$HunitMoney";
                logOilMoney($id, $name, landName($landKind, $lv), "($x, $y)", $str);
            }

	    # 枯渇判定
	    if(random(1000) < 10) {
		# 枯渇
		logOilEnd($id, $name, landName($landKind, $lv), "($x, $y)");
		$land->[$x][$y] = $HlandMountain;
		$landValue->[$x][$y] = 0;
	    }

	} elsif($landKind == $HlandOil) {
	    # 海底油田
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = $HoilMoney+ random(1001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    $oilincome += $value;

	    # 枯渇判定
	    if(random(1000) < $HoilRatio) {
		# 枯渇
		logOilEnd($id, $name, $lName, "($x, $y)");
		$land->[$x][$y] = $HlandSea;
		$landValue->[$x][$y] = 0;
	    }

	} elsif(($landKind == $HlandSea) && ($lv == 1)) {
	    # 浅瀬
	    if(random(100) < 5) {

		$land->[$x][$y] = $HlandSunahama;
		$landValue->[$x][$y] = 0;

	    }
	    if(random(100) < 1) {

		$land->[$x][$y] = $HlandIce;
		$landValue->[$x][$y] = 0;

	    }

	} elsif($landKind == $HlandSunahama) {
	    # 浅瀬
	    if(random(100) < 30) {

		$land->[$x][$y] = $HlandSea;
		$landValue->[$x][$y] = 1;

	    }

	} elsif($landKind == $HlandIce) {
	    # 浅瀬
	    my($lv) = $landValue->[$x][$y];

	    if($lv > 0) {
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = $lv * 25 + random(501);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logOilMoney($id, $name, $lName, "($x, $y)", $str);
	    }

	    if(random(100) < 10) {
		$land->[$x][$y] = $HlandSea;
		$landValue->[$x][$y] = 1;
	    }

	} elsif($landKind == $HlandSeki) {
	    # 関所
	    if(random(1000) < 7) {

	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = $HoilMoney+ random(1001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";

	    # 収入ログ
	    logSekiMoney($id, $name, $lName, "($x, $y)", $str);

	    }

	} elsif($landKind == $HlandYakusho) {

		if(($island->{'co0'} > 0) &&
		   ($island->{'co01'} > 0) &&
		   ($island->{'co2'} > 0) &&
		   ($island->{'co3'} > 0) &&
		   ($island->{'co4'} > 0) &&
		   ($island->{'co5'} > 0) &&
		   ($island->{'co6'} > 0) &&
		   ($island->{'co7'} > 0) &&
		   ($island->{'co8'} > 0) &&
		   ($island->{'eis7'} > 1000000) &&
		   ($island->{'rena'} > 10000) &&
		   ($island->{'pts'} > $HouseLevel7)) {
		$land->[$x][$y] = $HlandCollege;
		$landValue->[$x][$y] = 77;
		}

	} elsif($landKind == $HlandGold) {
	    # 金山
	    my($lv) = $landValue->[$x][$y];
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = $lv * 25 + random(501);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";

	    # 収入ログ
	    logOilMoney($id, $name, $lName, "($x, $y)", $str);

	    # 枯渇判定
	    if(random(100) < 7) {
		# 枯渇
		logGoldEnd($id, $name, $lName, "($x, $y)");
		$land->[$x][$y] = $HlandMountain;
	    }

        } elsif($landKind == $HlandPark) {
            # 遊園地
            if ($island->{'par'} > 5) {
            } else {
            my($lName);
            $lName = landName($landKind, $lv);
            my($nv) = (countAround($land, $x, $y, $HlandPark, 7) + countAround($land, $x, $y, $HlandKyujo, 7) + countAround($land, $x, $y, $HlandKyujokai, 7) + countAround($land, $x, $y, $HlandUmiamu, 7));
            my($nx) = $nv + 10;
            my($value);
            $value = int(int($island->{'pop'} / 50) * 3 * $nx / 10);

	    if($island->{'shouhi'} > $island->{'ene'}) {
            $value = int($value/10);
            }

            if ($value > 0) {
                $island->{'money'} += $value;
            $str = "$value$HunitMoney";
	    $parkincome += $value;
            }
            }

            # イベント判定
            if(random(100) < 3) { # 毎ターン 30% の確率でイベントが発生する
                # 遊園地のイベント
                $value = int($island->{'pop'} / 50) * 10; # 人口５千人ごとに1000トンの食料消費
                $island->{'food'} -= $value;
                $str = "$value$HunitFood";

                logParkEvent($id, $name, landName($landKind, $lv), "($x, $y)", $str) if ($value > 0);
            }

            # 老朽化判定
            if(random(100) < 2) {
                # 施設が老朽化したため閉園
                logParkEnd($id, $name, landName($landKind, $lv), "($x, $y)");
                $land->[$x][$y] = $HlandPlains;
                $landValue->[$x][$y] = 0;
            }


        } elsif($landKind == $HlandZoo) {

	    $etc6 = $island->{'etc6'};
	    $etc6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($z0,$z1,$z2,$z3,$z4,$z5,$z6,$z7,$z8,$z9,$z10,$z11,$z12,$z13,$z14,$z15,$z16,$z17,$z18,$z19,$z20,$z21,$z22,$z23,$z24,$z25,$z26,$z27,$z28,$z29,$z30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
	    ($z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

	    $zookazu = $z0+$z1+$z2+$z3+$z4+$z5+$z6+$z7+$z8+$z9+$z10+$z11+$z12+$z13+$z14+$z15+$z16+$z17+$z18+$z19+$z20+$z21+$z22+$z23+$z24+$z25+$z26+$z27+$z28+$z29+$z30;
	    $zookazus = $z0*2+$z1+$z2+$z3+$z4+$z5+$z6+$z7+$z8*2+$z9+$z10+$z11+$z12*2+$z13*3+$z14*3+$z15*3+$z16*3+$z17*4+$z18*4+$z19*5+$z20*4+$z21*5+$z22*3+$z23*3+$z24*3+$z25*3+$z26*3+$z27*3+$z28*4+$z29+$z30*4;

            # 遊園地
            if ($zooflag > 0) {

            } else {

	    $zooflag = 1;
	    $mshurui = 0;
	    foreach $i (0..30) {
		    if($z->{"$i"} > 0) {
			$mshurui++;
		    }
	    }

            my($lName);
            $lName = landName($landKind, $lv);
            my($value);
            $value = $zookazus*15+$mshurui*150;
            $valuef = $zookazu*250;

	    if($island->{'shouhi'} > $island->{'ene'}) {
            $value = int($value/10);
            }


            if(random(1000) < 25 + $s08) {
		my($i,$sx,$sy);
		my($zlv) = (0);
		for($i = 0; $i < $HpointNumber; $i++){
		    $sx = $Hrpx[$i];
		    $sy = $Hrpy[$i];
			if($land->[$sx][$sy] == $HlandZoo){
			    $zlv += $landValue->[$sx][$sy];
			}
		}

		my($siire);
		$siire = random(12);
	            if(random(100) < 20) {
			$siire = random(10)+13;
	            }

		$prize = $island->{'prize'};
		my($flags, $monsters, $turns);
		$prize =~ /([0-9]*),([0-9]*),(.*)/;
		$flags = $1;
		$monsters= $2;
		$turns = $3;
		$prize = '';
		$f = 1;
		for($i = 0; $i < $HmonsterNumber; $i++) {
		    if($monsters & $f) {
			$taiji->{"$i"}++;
		    }
		    $f *= 2;
		}

		if(($taiji->{"$siire"} > 0) && ($zlv > $zookazu)) {
		$z->{"$siire"}++;
		$value = $value*$siire;
                logSiire($id, $name, landName($landKind, $lv), "$HmonsterName[$siire]", "($x, $y)");
		$island->{'etc6'} = "$z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}";
		}

            }

            if ($value > 0) {
                $island->{'money'} += $value;
                # 収入ログ
                my($str) = "$value$HunitMoney";
                my($str2) = "$valuef$HunitFood";
                logOilMoney2($id, $name, landName($landKind, $lv), "($x, $y)", $str, $str2);
            }

            }


		if(($island->{'rena'} < $zookazus*25) && (random(100) < 15)) {
		$nigekaiju = random(30);
	            if ($z->{"$nigekaiju"} > 0) {
			$z->{"$nigekaiju"} -= 1;
			$kind = $nigekaiju;
			$lv = $lv = ($kind << 4)
			+ $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
			$land->[$x][$y] = $HlandMonster;
			$landValue->[$x][$y] = $lv;
			my($mKind, $mName, $mHp) = monsterSpec($lv);
			logNige($id, $name, landName($landKind, $lv), $mName, "($x, $y)");
			logMonsMove($id, $name, landName($landKind, $lv), "($x, $y)", $mName);
			$island->{'etc6'} = "$z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}";
	            }
		}

		if(($island->{'rena'} < $zookazus*50) || ($island->{'shouhi'} > $island->{'ene'})) {
		$nigekaiju = random(30);
	            if ($z->{"$nigekaiju"} > 0) {
			$nigeflag = 0;
			my($i, $sx, $sy, $kind, $lv);
			for($i = 1; $i < 7; $i++) {
			    $sx = $x + $ax[$i];
			    $sy = $y + $ay[$i];

			    # 行による位置調整
			    if((($sy % 2) == 0) && (($y % 2) == 1)) {
				$sx--;
			    }

			    $landKind = $land->[$sx][$sy];
			    $lv = $landValue->[$sx][$sy];
			    $point = "($sx, $sy)";

			    if(($sx < 0) || ($sx >= $HislandSize) ||
			       ($sy < 0) || ($sy >= $HislandSize)) {
			    } else {
				# 範囲内の場合
				$landKind = $land->[$sx][$sy];
				$lv = $landValue->[$sx][$sy];
				$point = "($sx, $sy)";
				if(($landKind == $HlandSea) ||
				   ($landKind == $HlandIce) ||
				   ($landKind == $HlandOil) ||
				   ($landKind == $HlandFune) ||
				   ($landKind == $HlandFrocity) ||
				   ($landKind == $HlandUmiamu) ||
				   ($landKind == $HlandSeacity) ||
				   ($landKind == $HlandSeatown) ||
				   ($landKind == $HlandMonster) ||
				   ($landKind == $HlandZoo) ||
				   ($landKind == $HlandUmishuto) ||
				   ($landKind == $HlandSbase)) {
				} else {
				    if ($nigeflag == 0) {
					$nigeflag++;
					$z->{"$nigekaiju"} -= 1;
					$kind = $nigekaiju;
					$lv = $lv = ($kind << 4)
					+ $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
					$land->[$sx][$sy] = $HlandMonster;
					$landValue->[$sx][$sy] = $lv;
					my($mKind, $mName, $mHp) = monsterSpec($lv);
					logNige($id, $name, landName($landKind, $lv), $mName, "($x, $y)");
					$island->{'etc6'} = "$z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}";
				    }
				}
			    }

			}
	            }
		}

        } elsif($landKind == $HlandKyujokai) {

	$yosengameendm=0;
	if($HmaxIsland < 21) {
	    $hcgameseigen=1;
	} else {
	    $hcgameseigen=3;
	}

	$eisei4 = $island->{'eisei4'};
	$eisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($sto, $std, $stk, $stwin, $stdrow, $stlose, $stwint, $stdrowt, $stloset, $styusho, $stshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);

	    if(($HislandTurn % 100) == 0) {
		$stwin = 0;
		$stdrow = 0;
		$stlose = 0;
		$stshoka = 1;

		if($island->{'hcsankaflag'} == 0) {
		$stsanka++;
		$island->{'hcsankaflag'} = 1;
		}


		$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";

		if ($stsanka == 1) {
		$island->{'stsankahantei'}++;
		}

	    }

	    foreach $i (1..10) {
	    if(($HislandTurn % 100) == $i) {

		if(($stshoka == 1) &&
		   ($yosengameendm == 0) &&
		   ($yosengameend < $hcgameseigen)) {
	        my($tIsland);
	        my($i);
	        for($i = 0; $i < $HislandNumber; $i++) {
	            $tIsland = $Hislands[$i];

		    if ($island->{'id'} == $tIsland->{'id'}){
		    } else {

			$tEisei4 = $tIsland->{'eisei4'};
			$tEisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
			($tSto, $tStd, $tStk, $tStwin, $tStdrow, $tStlose, $tStwint, $tStdrowt, $tStloset, $tStyusho, $tStshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);


		    if (($tStshoka == 1) &&
			($yosengameendm == 0) &&
			($yosengameend < $hcgameseigen)) {

			$goal=0;
			$tgoal=0;


			for($k = 0; $k < 5; $k++) {
			    if((random($sto)>random($tStd)) &&
				(random($sto)>random($tStk))) {
				$goal++;
			    }
			}
			for($k = 0; $k < 3; $k++) {
			    if((random($tSto)>random($std)) &&
				(random($tSto)>random($stk))) {
				$tgoal++;
			    }
			}

			if($goal > $tgoal) {
			$stwin++;
			$stwint++;
			$stshoka++;
			$tStshoka++;
			$tStlose++;
			$tStloset++;
			$yosengameend++;
			$yosengameendm++;
				my($value);
				$value = (($stwin * 3 + $stdrow) * 1000);

				$auc9 = $island->{'auc9'};
				$auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);
				$auc9c += $value;
				$auc9c2 = int($auc9c/10000);
				$auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
				$island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";
				$str = "Auction補助金$value$HunitMoney";

				logHCwin($id, $name, "勝利", $str);
				my($stup);
				$stup = random(3);
				$uphey = int(($sto+$std+$stk)/3);
				$tuphey = int(($tSto+$tStd+$tStk)/3);
				$uppoint = int(($uphey-$tuphey)/2)+5;
				if($stup == 0) {
				    $tSto += $uppoint;
				    $tStd += $uppoint;
				} elsif($stup == 1) {
				    $tStd += $uppoint;
				    $tStk += $uppoint;
				} else {
				    $tStk += $uppoint;
				    $tSto += $uppoint;
				}
			} elsif($goal < $tgoal) {
			$tStwin++;
			$tStwint++;
			$stshoka++;
			$tStshoka++;
			$stlose++;
			$stloset++;
			$yosengameend++;
			$yosengameendm++;
				my($value);
				$value = (($tStwin * 3 + $tStdrow) * 1000);

				$tauc9 = $tIsland->{'auc9'};
				$tauc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($tauc9a, $tauc9b, $tauc9c, $tauc9d, $tauc9e) = ($1, $2, $3, $4, $5);
				$tauc9c += $value;
				$tauc9c2 = int($tauc9c/10000);
				$tauc9a = $tauc9b + $tauc9c2 + $tauc9d + $tauc9e;
				$tIsland->{'auc9'} = "$tauc9a,$tauc9b,$tauc9c,$tauc9d,$tauc9e";
				$str = "Auction補助金$value$HunitMoney";

				logHCwin($tIsland->{'id'}, $tIsland->{'name'}, "勝利", $str);
				my($stup);
				$stup = random(3);
				$uphey = int(($sto+$std+$stk)/3);
				$tuphey = int(($tSto+$tStd+$tStk)/3);
				$uppoint = int(($tuphey-$uphey)/2)+5;
				if($stup == 0) {
				    $sto += $uppoint;
				    $std += $uppoint;
				} elsif($stup == 1) {
				    $std += $uppoint;
				    $stk += $uppoint;
				} else {
				    $stk += $uppoint;
				    $sto += $uppoint;
				}
			} else {
			$stdrow++;
			$stdrowt++;
			$tStdrow++;
			$tStdrowt++;
			$stshoka++;
			$tStshoka++;
			$yosengameend++;
			$yosengameendm++;
			}

			logHCgame($id, $tIsland->{'id'}, $name, $tIsland->{'name'}, landName($landKind, $lv), "Hakoniwa Cup 予選第１戦", $goal, $tgoal);

		    }

			$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
			$tIsland->{'eisei4'} = "$tSto,$tStd,$tStk,$tStwin,$tStdrow,$tStlose,$tStwint,$tStdrowt,$tStloset,$tStyusho,$tStshoka";
		}
		}
		}
	    }
	    }

	    if(($HislandTurn % 100) == 11) {
		if($stshoka == 1) {
			$stwin++;
			$stwint++;
			$stshoka++;
			logHCantiwin($id, $name, "Hakoniwa Cup 予選第１戦は不戦勝");
			$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
	    }
	    }

	    foreach $i (11..20) {
	    if(($HislandTurn % 100) == $i) {

		if(($stshoka == 2) &&
		   ($yosengameendm == 0) &&
		   ($yosengameend < $hcgameseigen)) {
	        my($tIsland);
	        my($i);
	        for($i = 0; $i < $HislandNumber; $i++) {
	            $tIsland = $Hislands[$i];

		    if ($island->{'id'} == $tIsland->{'id'}){
		    } else {

			$tEisei4 = $tIsland->{'eisei4'};
			$tEisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
			($tSto, $tStd, $tStk, $tStwin, $tStdrow, $tStlose, $tStwint, $tStdrowt, $tStloset, $tStyusho, $tStshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);


		    if (($tStshoka == 2) &&
			($yosengameendm == 0) &&
			($yosengameend < $hcgameseigen)) {

			$goal=0;
			$tgoal=0;


			for($k = 0; $k < 5; $k++) {
			    if((random($sto)>random($tStd)) &&
				(random($sto)>random($tStk))) {
				$goal++;
			    }
			}
			for($k = 0; $k < 3; $k++) {
			    if((random($tSto)>random($std)) &&
				(random($tSto)>random($stk))) {
				$tgoal++;
			    }
			}

			if($goal > $tgoal) {
			$stwin++;
			$stwint++;
			$stshoka++;
			$tStshoka++;
			$tStlose++;
			$tStloset++;
			$yosengameend++;
			$yosengameendm++;
				my($value);
				$value = (($stwin * 3 + $stdrow) * 1000);

				$auc9 = $island->{'auc9'};
				$auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);
				$auc9c += $value;
				$auc9c2 = int($auc9c/10000);
				$auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
				$island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";
				$str = "Auction補助金$value$HunitMoney";

				logHCwin($id, $name, "勝利", $str);
				my($stup);
				$stup = random(3);
				$uphey = int(($sto+$std+$stk)/3);
				$tuphey = int(($tSto+$tStd+$tStk)/3);
				$uppoint = int(($uphey-$tuphey)/2)+5;
				if($stup == 0) {
				    $tSto += $uppoint;
				    $tStd += $uppoint;
				} elsif($stup == 1) {
				    $tStd += $uppoint;
				    $tStk += $uppoint;
				} else {
				    $tStk += $uppoint;
				    $tSto += $uppoint;
				}
			} elsif($goal < $tgoal) {
			$tStwin++;
			$tStwint++;
			$stshoka++;
			$tStshoka++;
			$stlose++;
			$stloset++;
			$yosengameend++;
			$yosengameendm++;
				my($value);
				$value = (($tStwin * 3 + $tStdrow) * 1000);

				$tauc9 = $tIsland->{'auc9'};
				$tauc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($tauc9a, $tauc9b, $tauc9c, $tauc9d, $tauc9e) = ($1, $2, $3, $4, $5);
				$tauc9c += $value;
				$tauc9c2 = int($tauc9c/10000);
				$tauc9a = $tauc9b + $tauc9c2 + $tauc9d + $tauc9e;
				$tIsland->{'auc9'} = "$tauc9a,$tauc9b,$tauc9c,$tauc9d,$tauc9e";
				$str = "Auction補助金$value$HunitMoney";

				logHCwin($tIsland->{'id'}, $tIsland->{'name'}, "勝利", $str);
				my($stup);
				$stup = random(3);
				$uphey = int(($sto+$std+$stk)/3);
				$tuphey = int(($tSto+$tStd+$tStk)/3);
				$uppoint = int(($tuphey-$uphey)/2)+5;
				if($stup == 0) {
				    $sto += $uppoint;
				    $std += $uppoint;
				} elsif($stup == 1) {
				    $std += $uppoint;
				    $stk += $uppoint;
				} else {
				    $stk += $uppoint;
				    $sto += $uppoint;
				}
			} else {
			$stdrow++;
			$stdrowt++;
			$tStdrow++;
			$tStdrowt++;
			$stshoka++;
			$tStshoka++;
			$yosengameend++;
			$yosengameendm++;
			}

			logHCgame($id, $tIsland->{'id'}, $name, $tIsland->{'name'}, landName($landKind, $lv), "Hakoniwa Cup 予選第２戦", $goal, $tgoal);

		    }

			$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
			$tIsland->{'eisei4'} = "$tSto,$tStd,$tStk,$tStwin,$tStdrow,$tStlose,$tStwint,$tStdrowt,$tStloset,$tStyusho,$tStshoka";
		}
		}
		}
	    }
	    }

	    if(($HislandTurn % 100) == 21) {
		if($stshoka == 2) {
			$stwin++;
			$stwint++;
			$stshoka++;
			logHCantiwin($id, $name, "Hakoniwa Cup 予選第２戦は不戦勝");
			$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
	    }
	    }

	    foreach $i (21..30) {
	    if(($HislandTurn % 100) == $i) {

		if(($stshoka == 3) &&
		   ($yosengameendm == 0) &&
		   ($yosengameend < $hcgameseigen)) {
	        my($tIsland);
	        my($i);
	        for($i = 0; $i < $HislandNumber; $i++) {
	            $tIsland = $Hislands[$i];

		    if ($island->{'id'} == $tIsland->{'id'}){
		    } else {

			$tEisei4 = $tIsland->{'eisei4'};
			$tEisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
			($tSto, $tStd, $tStk, $tStwin, $tStdrow, $tStlose, $tStwint, $tStdrowt, $tStloset, $tStyusho, $tStshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);


		    if (($tStshoka == 3) &&
			($yosengameendm == 0) &&
			($yosengameend < $hcgameseigen)) {

			$goal=0;
			$tgoal=0;


			for($k = 0; $k < 5; $k++) {
			    if((random($sto)>random($tStd)) &&
				(random($sto)>random($tStk))) {
				$goal++;
			    }
			}
			for($k = 0; $k < 3; $k++) {
			    if((random($tSto)>random($std)) &&
				(random($tSto)>random($stk))) {
				$tgoal++;
			    }
			}

			if($goal > $tgoal) {
			$stwin++;
			$stwint++;
			$stshoka++;
			$tStshoka++;
			$tStlose++;
			$tStloset++;
			$yosengameend++;
			$yosengameendm++;
				my($value);
				$value = (($stwin * 3 + $stdrow) * 1000);

				$auc9 = $island->{'auc9'};
				$auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);
				$auc9c += $value;
				$auc9c2 = int($auc9c/10000);
				$auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
				$island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";
				$str = "Auction補助金$value$HunitMoney";

				logHCwin($id, $name, "勝利", $str);
				my($stup);
				$stup = random(3);
				$uphey = int(($sto+$std+$stk)/3);
				$tuphey = int(($tSto+$tStd+$tStk)/3);
				$uppoint = int(($uphey-$tuphey)/2)+5;
				if($stup == 0) {
				    $tSto += $uppoint;
				    $tStd += $uppoint;
				} elsif($stup == 1) {
				    $tStd += $uppoint;
				    $tStk += $uppoint;
				} else {
				    $tStk += $uppoint;
				    $tSto += $uppoint;
				}
			} elsif($goal < $tgoal) {
			$tStwin++;
			$tStwint++;
			$stshoka++;
			$tStshoka++;
			$stlose++;
			$stloset++;
			$yosengameend++;
			$yosengameendm++;
				my($value);
				$value = (($tStwin * 3 + $tStdrow) * 1000);

				$tauc9 = $tIsland->{'auc9'};
				$tauc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($tauc9a, $tauc9b, $tauc9c, $tauc9d, $tauc9e) = ($1, $2, $3, $4, $5);
				$tauc9c += $value;
				$tauc9c2 = int($tauc9c/10000);
				$tauc9a = $tauc9b + $tauc9c2 + $tauc9d + $tauc9e;
				$tIsland->{'auc9'} = "$tauc9a,$tauc9b,$tauc9c,$tauc9d,$tauc9e";
				$str = "Auction補助金$value$HunitMoney";

				logHCwin($tIsland->{'id'}, $tIsland->{'name'}, "勝利", $str);
				my($stup);
				$stup = random(3);
				$uphey = int(($sto+$std+$stk)/3);
				$tuphey = int(($tSto+$tStd+$tStk)/3);
				$uppoint = int(($tuphey-$uphey)/2)+5;
				if($stup == 0) {
				    $sto += $uppoint;
				    $std += $uppoint;
				} elsif($stup == 1) {
				    $std += $uppoint;
				    $stk += $uppoint;
				} else {
				    $stk += $uppoint;
				    $sto += $uppoint;
				}
			} else {
			$stdrow++;
			$stdrowt++;
			$tStdrow++;
			$tStdrowt++;
			$stshoka++;
			$tStshoka++;
			$yosengameend++;
			$yosengameendm++;
			}

			logHCgame($id, $tIsland->{'id'}, $name, $tIsland->{'name'}, landName($landKind, $lv), "Hakoniwa Cup 予選第３戦", $goal, $tgoal);

		    }

			$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
			$tIsland->{'eisei4'} = "$tSto,$tStd,$tStk,$tStwin,$tStdrow,$tStlose,$tStwint,$tStdrowt,$tStloset,$tStyusho,$tStshoka";
		}
		}
		}
	    }
	    }

	    if(($HislandTurn % 100) == 31) {
		if($stshoka == 3) {
			$stwin++;
			$stwint++;
			$stshoka++;
			logHCantiwin($id, $name, "Hakoniwa Cup 予選第３戦は不戦勝");
			$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
	    }
	    }

	    foreach $i (31..40) {
	    if(($HislandTurn % 100) == $i) {

		if(($stshoka == 4) &&
		   ($yosengameendm == 0) &&
		   ($yosengameend < $hcgameseigen)) {
	        my($tIsland);
	        my($i);
	        for($i = 0; $i < $HislandNumber; $i++) {
	            $tIsland = $Hislands[$i];

		    if ($island->{'id'} == $tIsland->{'id'}){
		    } else {

			$tEisei4 = $tIsland->{'eisei4'};
			$tEisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
			($tSto, $tStd, $tStk, $tStwin, $tStdrow, $tStlose, $tStwint, $tStdrowt, $tStloset, $tStyusho, $tStshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);


		    if (($tStshoka == 4) &&
			($yosengameendm == 0) &&
			($yosengameend < $hcgameseigen)) {

			$goal=0;
			$tgoal=0;


			for($k = 0; $k < 5; $k++) {
			    if((random($sto)>random($tStd)) &&
				(random($sto)>random($tStk))) {
				$goal++;
			    }
			}
			for($k = 0; $k < 3; $k++) {
			    if((random($tSto)>random($std)) &&
				(random($tSto)>random($stk))) {
				$tgoal++;
			    }
			}

			if($goal > $tgoal) {
			$stwin++;
			$stwint++;
			$stshoka++;
			$tStshoka++;
			$tStlose++;
			$tStloset++;
			$yosengameend++;
			$yosengameendm++;
				my($value);
				$value = (($stwin * 3 + $stdrow) * 1000);

				$auc9 = $island->{'auc9'};
				$auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);
				$auc9c += $value;
				$auc9c2 = int($auc9c/10000);
				$auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
				$island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";
				$str = "Auction補助金$value$HunitMoney";

				logHCwin($id, $name, "勝利", $str);
				my($stup);
				$stup = random(3);
				$uphey = int(($sto+$std+$stk)/3);
				$tuphey = int(($tSto+$tStd+$tStk)/3);
				$uppoint = int(($uphey-$tuphey)/2)+5;
				if($stup == 0) {
				    $tSto += $uppoint;
				    $tStd += $uppoint;
				} elsif($stup == 1) {
				    $tStd += $uppoint;
				    $tStk += $uppoint;
				} else {
				    $tStk += $uppoint;
				    $tSto += $uppoint;
				}
			} elsif($goal < $tgoal) {
			$tStwin++;
			$tStwint++;
			$stshoka++;
			$tStshoka++;
			$stlose++;
			$stloset++;
			$yosengameend++;
			$yosengameendm++;
				my($value);
				$value = (($tStwin * 3 + $tStdrow) * 1000);

				$tauc9 = $tIsland->{'auc9'};
				$tauc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($tauc9a, $tauc9b, $tauc9c, $tauc9d, $tauc9e) = ($1, $2, $3, $4, $5);
				$tauc9c += $value;
				$tauc9c2 = int($tauc9c/10000);
				$tauc9a = $tauc9b + $tauc9c2 + $tauc9d + $tauc9e;
				$tIsland->{'auc9'} = "$tauc9a,$tauc9b,$tauc9c,$tauc9d,$tauc9e";
				$str = "Auction補助金$value$HunitMoney";

				logHCwin($tIsland->{'id'}, $tIsland->{'name'}, "勝利", $str);
				my($stup);
				$stup = random(3);
				$uphey = int(($sto+$std+$stk)/3);
				$tuphey = int(($tSto+$tStd+$tStk)/3);
				$uppoint = int(($tuphey-$uphey)/2)+5;
				if($stup == 0) {
				    $sto += $uppoint;
				    $std += $uppoint;
				} elsif($stup == 1) {
				    $std += $uppoint;
				    $stk += $uppoint;
				} else {
				    $stk += $uppoint;
				    $sto += $uppoint;
				}
			} else {
			$stdrow++;
			$stdrowt++;
			$tStdrow++;
			$tStdrowt++;
			$stshoka++;
			$tStshoka++;
			$yosengameend++;
			$yosengameendm++;
			}

			logHCgame($id, $tIsland->{'id'}, $name, $tIsland->{'name'}, landName($landKind, $lv), "Hakoniwa Cup 予選第４戦", $goal, $tgoal);

		    }

			$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
			$tIsland->{'eisei4'} = "$tSto,$tStd,$tStk,$tStwin,$tStdrow,$tStlose,$tStwint,$tStdrowt,$tStloset,$tStyusho,$tStshoka";
		}
		}
		}
	    }
	    }

	    if(($HislandTurn % 100) == 41) {
		if($stshoka == 4) {
			$stwin++;
			$stwint++;
			$stshoka++;
			logHCantiwin($id, $name, "Hakoniwa Cup 予選第４戦は不戦勝");
			$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
	    }
	    }

	    foreach $i (42..46) {
	    if(($HislandTurn % 100) == $i) {

		if($stshoka < 6) {
		$stshoka = 11;
		$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
		}

		if(($stshoka == 6) &&
		   ($yosengameendm == 0) &&
		   ($yosengameend < 1)) {
	        my($tIsland);
	        my($i);
	        for($i = 0; $i < $HislandNumber; $i++) {
	            $tIsland = $Hislands[$i];

		    if ($island->{'id'} == $tIsland->{'id'}){
		    } else {

			$tEisei4 = $tIsland->{'eisei4'};
			$tEisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
			($tSto, $tStd, $tStk, $tStwin, $tStdrow, $tStlose, $tStwint, $tStdrowt, $tStloset, $tStyusho, $tStshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);


		    if (($tStshoka == 6) &&
			($yosengameendm == 0) &&
			($yosengameend < 1)) {

			$goal=0;
			$tgoal=0;


			for($k = 0; $k < 3; $k++) {
			    if((random($sto)>random($tStd)) &&
				(random($sto)>random($tStk))) {
				$goal++;
			    }
			}
			for($k = 0; $k < 3; $k++) {
			    if((random($tSto)>random($std)) &&
				(random($tSto)>random($stk))) {
				$tgoal++;
			    }
			}
			if($goal == $tgoal) {
				if(random(100) < 60) {
				    $goal++;
				} else {
				    $tgoal++;
				}
			}
			if($goal > $tgoal) {
			$stwin++;
			$stwint++;
			$stshoka++;
			$tStshoka = 12;
			$tStlose++;
			$tStloset++;
			$yosengameend++;
			$yosengameendm++;
				my($value);
				$value = (($stwin * 3 + $stdrow) * 1000);

				$auc9 = $island->{'auc9'};
				$auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);
				$auc9c += $value;
				$auc9c2 = int($auc9c/10000);
				$auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
				$island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";
				$str = "Auction補助金$value$HunitMoney";

				logHCwin($id, $name, "準決勝進出", $str);
				my($stup);
				$stup = random(3);
				if($stup == 0) {
				    $tSto += 30;
				} elsif($stup == 1) {
				    $tStd += 30;
				} else {
				    $tStk += 30;
				}
			} elsif($goal < $tgoal) {
			$tStwin++;
			$tStwint++;
			$tStshoka++;
			$stshoka = 12;
			$stlose++;
			$stloset++;
			$yosengameend++;
			$yosengameendm++;
				my($value);
				$value = (($tStwin * 3 + $tStdrow) * 1000);

				$tauc9 = $tIsland->{'auc9'};
				$tauc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($tauc9a, $tauc9b, $tauc9c, $tauc9d, $tauc9e) = ($1, $2, $3, $4, $5);
				$tauc9c += $value;
				$tauc9c2 = int($tauc9c/10000);
				$tauc9a = $tauc9b + $tauc9c2 + $tauc9d + $tauc9e;
				$tIsland->{'auc9'} = "$tauc9a,$tauc9b,$tauc9c,$tauc9d,$tauc9e";
				$str = "Auction補助金$value$HunitMoney";

				logHCwin($tIsland->{'id'}, $tIsland->{'name'}, "準決勝進出", $str);
				my($stup);
				$stup = random(3);
				if($stup == 0) {
				    $sto += 30;
				} elsif($stup == 1) {
				    $std += 30;
				} else {
				    $stk += 30;
				}
			} else {
			$stdrow++;
			$stdrowt++;
			$tStdrow++;
			$tStdrowt++;
			$stshoka++;
			$tStshoka++;
			$yosengameend++;
			$yosengameendm++;
			}

			logHCgame($id, $tIsland->{'id'}, $name, $tIsland->{'name'}, landName($landKind, $lv), "Hakoniwa Cup 準々決勝戦", $goal, $tgoal);

		    }

			$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
			$tIsland->{'eisei4'} = "$tSto,$tStd,$tStk,$tStwin,$tStdrow,$tStlose,$tStwint,$tStdrowt,$tStloset,$tStyusho,$tStshoka";
		}
		}
		}
	    }
	    }

	    if(($HislandTurn % 100) == 46) {
		if($stshoka == 6) {
			$stwin++;
			$stwint++;
			$stshoka++;
			logHCantiwin($id, $name, "Hakoniwa Cup 準々決勝戦は不戦勝");
			$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
	    }
	    }

	    foreach $i (47..49) {
	    if(($HislandTurn % 100) == $i) {

		if(($stshoka == 7) &&
		   ($yosengameendm == 0) &&
		   ($yosengameend < 1)) {
	        my($tIsland);
	        my($i);
	        for($i = 0; $i < $HislandNumber; $i++) {
	            $tIsland = $Hislands[$i];

		    if ($island->{'id'} == $tIsland->{'id'}){
		    } else {

			$tEisei4 = $tIsland->{'eisei4'};
			$tEisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
			($tSto, $tStd, $tStk, $tStwin, $tStdrow, $tStlose, $tStwint, $tStdrowt, $tStloset, $tStyusho, $tStshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);


		    if (($tStshoka == 7) &&
			($yosengameendm == 0) &&
			($yosengameend < 1)) {

			$goal=0;
			$tgoal=0;


			for($k = 0; $k < 3; $k++) {
			    if((random($sto)>random($tStd)) &&
				(random($sto)>random($tStk))) {
				$goal++;
			    }
			}
			for($k = 0; $k < 3; $k++) {
			    if((random($tSto)>random($std)) &&
				(random($tSto)>random($stk))) {
				$tgoal++;
			    }
			}
			if($goal == $tgoal) {
				if(random(100) < 60) {
				    $goal++;
				} else {
				    $tgoal++;
				}
			}
			if($goal > $tgoal) {
			$stwin++;
			$stwint++;
			$stshoka++;
			$tStshoka = 13;
			$tStlose++;
			$tStloset++;
			$yosengameend++;
			$yosengameendm++;
				my($value);
				$value = (($stwin * 3 + $stdrow) * 1000);

				$auc9 = $island->{'auc9'};
				$auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);
				$auc9c += $value;
				$auc9c2 = int($auc9c/10000);
				$auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
				$island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";
				$str = "Auction補助金$value$HunitMoney";

				logHCwin($id, $name, "決勝進出", $str);
				my($stup);
				$stup = random(3);
				if($stup == 0) {
				    $tSto += 30;
				} elsif($stup == 1) {
				    $tStd += 30;
				} else {
				    $tStk += 30;
				}
			} elsif($goal < $tgoal) {
			$tStwin++;
			$tStwint++;
			$tStshoka++;
			$stshoka = 13;
			$stlose++;
			$stloset++;
			$yosengameend++;
			$yosengameendm++;
				my($value);
				$value = (($tStwin * 3 + $tStdrow) * 1000);

				$tauc9 = $tIsland->{'auc9'};
				$tauc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($tauc9a, $tauc9b, $tauc9c, $tauc9d, $tauc9e) = ($1, $2, $3, $4, $5);
				$tauc9c += $value;
				$tauc9c2 = int($tauc9c/10000);
				$tauc9a = $tauc9b + $tauc9c2 + $tauc9d + $tauc9e;
				$tIsland->{'auc9'} = "$tauc9a,$tauc9b,$tauc9c,$tauc9d,$tauc9e";
				$str = "Auction補助金$value$HunitMoney";

				logHCwin($tIsland->{'id'}, $tIsland->{'name'}, "決勝進出", $str);
				my($stup);
				$stup = random(3);
				if($stup == 0) {
				    $sto += 30;
				} elsif($stup == 1) {
				    $std += 30;
				} else {
				    $stk += 30;
				}
			} else {
			$stdrow++;
			$stdrowt++;
			$tStdrow++;
			$tStdrowt++;
			$stshoka++;
			$tStshoka++;
			$yosengameend++;
			$yosengameendm++;
			}

			logHCgame($id, $tIsland->{'id'}, $name, $tIsland->{'name'}, landName($landKind, $lv), "Hakoniwa Cup 準決勝戦", $goal, $tgoal);

		    }

			$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
			$tIsland->{'eisei4'} = "$tSto,$tStd,$tStk,$tStwin,$tStdrow,$tStlose,$tStwint,$tStdrowt,$tStloset,$tStyusho,$tStshoka";
		}
		}
		}
	    }
	    }

	    if(($HislandTurn % 100) == 49) {
		if($stshoka == 7) {
			$stwin++;
			$stwint++;
			$stshoka++;
			logHCantiwin($id, $name, "Hakoniwa Cup 準決勝戦は不戦勝");
			$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
	    }
	    }

	    foreach $i (50..51) {
	    if(($HislandTurn % 100) == $i) {

		if(($stshoka == 8) &&
		   ($yosengameendm == 0) &&
		   ($yosengameend < 1)) {
	        my($tIsland);
	        my($i);
	        for($i = 0; $i < $HislandNumber; $i++) {
	            $tIsland = $Hislands[$i];

		    if ($island->{'id'} == $tIsland->{'id'}){
		    } else {

			$tEisei4 = $tIsland->{'eisei4'};
			$tEisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
			($tSto, $tStd, $tStk, $tStwin, $tStdrow, $tStlose, $tStwint, $tStdrowt, $tStloset, $tStyusho, $tStshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);


		    if (($tStshoka == 8) &&
			($yosengameendm == 0) &&
			($yosengameend < 1)) {

			$goal=0;
			$tgoal=0;


			for($k = 0; $k < 3; $k++) {
			    if((random($sto)>random($tStd)) &&
				(random($sto)>random($tStk))) {
				$goal++;
			    }
			}
			for($k = 0; $k < 3; $k++) {
			    if((random($tSto)>random($std)) &&
				(random($tSto)>random($stk))) {
				$tgoal++;
			    }
			}
			if($goal == $tgoal) {
				if(random(100) < 60) {
				    $goal++;
				} else {
				    $tgoal++;
				}
			}
			if($goal > $tgoal) {
			$stwin++;
			$stwint++;
			$styusho++;
			$stshoka++;
			$tStshoka = 14;
			$tStlose++;
			$tStloset++;
			$yosengameend++;
			$yosengameendm++;
				my($value);
				$value = (($stwin * 3 + $stdrow) * 1000)*2;

				$auc9 = $island->{'auc9'};
				$auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);
				$auc9c += $value;
				$auc9c2 = int($auc9c/10000);
				$auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
				$island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";
				$str = "Auction補助金$value$HunitMoney";

				$yushouflag = 1;
				$yushounamber = $island->{'id'};
				$yushounamber2 = $tIsland->{'id'};

				logHCwin($id, $name, "優勝", $str);
				$hcturn = int($HislandTurn/100)*100;
				logHCwintop($id, $name, $hcturn);
				my($stup);
				$stup = random(3);
				if($stup == 0) {
				    $tSto += 50;
				} elsif($stup == 1) {
				    $tStd += 50;
				} else {
				    $tStk += 50;
				}
			} elsif($goal < $tgoal) {
			$tStwin++;
			$tStwint++;
			$tStyusho++;
			$tStshoka++;
			$stshoka = 14;
			$stlose++;
			$stloset++;
			$yosengameend++;
			$yosengameendm++;
				my($value);
				$value = (($tStwin * 3 + $tStdrow) * 1000)*2;

				$tauc9 = $tIsland->{'auc9'};
				$tauc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($tauc9a, $tauc9b, $tauc9c, $tauc9d, $tauc9e) = ($1, $2, $3, $4, $5);
				$tauc9c += $value;
				$tauc9c2 = int($tauc9c/10000);
				$tauc9a = $tauc9b + $tauc9c2 + $tauc9d + $tauc9e;
				$tIsland->{'auc9'} = "$tauc9a,$tauc9b,$tauc9c,$tauc9d,$tauc9e";
				$str = "Auction補助金$value$HunitMoney";

				$yushouflag = 2;
				$yushounamber = $tIsland->{'id'};
				$yushounamber2 = $island->{'id'};

				logHCwin($tIsland->{'id'}, $tIsland->{'name'}, "優勝", $str);
				$hcturn = int($HislandTurn/100)*100;
				logHCwintop($tIsland->{'id'}, $tIsland->{'name'}, $hcturn);
				my($stup);
				$stup = random(3);
				if($stup == 0) {
				    $sto += 50;
				} elsif($stup == 1) {
				    $std += 50;
				} else {
				    $stk += 50;
				}
			} else {
			$stdrow++;
			$stdrowt++;
			$tStdrow++;
			$tStdrowt++;
			$stshoka++;
			$tStshoka++;
			$yosengameend++;
			$yosengameendm++;
			}

			logHCgame($id, $tIsland->{'id'}, $name, $tIsland->{'name'}, landName($landKind, $lv), "Hakoniwa Cup 決勝戦", $goal, $tgoal);

		    }

			$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
			$tIsland->{'eisei4'} = "$tSto,$tStd,$tStk,$tStwin,$tStdrow,$tStlose,$tStwint,$tStdrowt,$tStloset,$tStyusho,$tStshoka";
		}
		}
		}
	    }
	    }

	    if(($HislandTurn % 100) == 51) {
		if($stshoka == 8) {
			$stwin++;
			$stwint++;
			$stshoka++;
			$styusho++;
			logHCantiwin($id, $name, "Hakoniwa Cup 決勝戦は不戦勝");
				my($value);
				$value = (($stwin * 3 + $stdrow) * 1000)*2;

				$auc9 = $island->{'auc9'};
				$auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);
				$auc9c += $value;
				$auc9c2 = int($auc9c/10000);
				$auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
				$island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";
				$str = "Auction補助金$value$HunitMoney";

				logHCwin($id, $name, "とりあえずの優勝", $str);
				$hcturn = int($HislandTurn/100)*100;
				logHCwintop($id, $name, $hcturn);
			$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
	    }
	    }

	    if(($HislandTurn % 100) == 52) {
		if($stshoka != 9) {
		$stshoka = 10;
		$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
		}
	    }

	    if(($stshoka == 10) ||
		($stshoka == 11)) {
		my($stup);
		$stup = random(3);
		if($stup == 0) {
		    $sto++;
		} elsif($stup == 1) {
		    $std++;
		} else {
		   $stk++;
		}
		$island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
	    }

            # 野球場改
            if (($island->{'kyu'} > 1) ||
		($island->{'amu'} > 1)) {
            } else {
            my($nt) = (countAround($land, $x, $y, $HlandTown, 19) + countAround($land, $x, $y, $HlandProcity, 19) + countAround($land, $x, $y, $HlandMinato, 19) + countAround($land, $x, $y, $HlandSeacity, 19) + countAround($land, $x, $y, $HlandFrocity, 19) + countAround($land, $x, $y, $HlandNewtown, 19) + countAround($land, $x, $y, $HlandBigtown, 19) + countAround($land, $x, $y, $HlandBettown, 19) + countAround($land, $x, $y, $HlandSkycity, 19) + countAround($land, $x, $y, $HlandUmicity, 19) + countAround($land, $x, $y, $HlandSeatown, 19) + countAround($land, $x, $y, $HlandOnsen, 19) + countAround($land, $x, $y, $HlandShuto, 19) + countAround($land, $x, $y, $HlandUmishuto, 19) + countAround($land, $x, $y, $HlandRizort, 19) + countAround($land, $x, $y, $HlandKajino, 19) + countAround($land, $x, $y, $HlandBigRizort, 19) - 6);
            my($ns) = ( 1 + 2 * countAround($land, $x, $y, $HlandPark, 19));
            my($nr) = ( 1 + 3 * countAround($land, $x, $y, $HlandUmiamu, 19));
            my($nu) = ( 10 + random(10));
            my($value);
            $value = ($nt * $nu * $ns * $nr + int($island->{'pop'} / 25));

	    if($island->{'shouhi'} > $island->{'ene'}) {
            $value = int($value/5);
            }

            if ($value > 0) {
                $island->{'money'} += $value;

                # 収入ログ
                my($str) = "$value$HunitMoney";
                logOilMoney($id, $name, landName($landKind, $lv), "($x, $y)", $str);
            }
            }

            # イベント判定
            if(random(100) < 10) { # 毎ターン 30% の確率でイベントが発生する
                # 野球場のイベント
                $value = int($island->{'pop'} / 50) * 10; # 人口５千人ごとに1000トンの食料消費
                $island->{'food'} -= $value;
                $str = "$value$HunitFood";

                logParkEvent($id, $name, landName($landKind, $lv), "($x, $y)", $str) if ($value > 0);
            }


        } elsif($landKind == $HlandKyujo) {
            # 野球場
            if (($island->{'kyu'} > 1) ||
		($island->{'amu'} > 1)) {
            } else {
            my($nt) = (countAround($land, $x, $y, $HlandTown, 19) + countAround($land, $x, $y, $HlandProcity, 19) + countAround($land, $x, $y, $HlandMinato, 19) + countAround($land, $x, $y, $HlandSeacity, 19) + countAround($land, $x, $y, $HlandFrocity, 19) + countAround($land, $x, $y, $HlandNewtown, 19) + countAround($land, $x, $y, $HlandBigtown, 19) + countAround($land, $x, $y, $HlandBettown, 19) + countAround($land, $x, $y, $HlandSkycity, 19) + countAround($land, $x, $y, $HlandUmicity, 19) + countAround($land, $x, $y, $HlandSeatown, 19) + countAround($land, $x, $y, $HlandOnsen, 19) + countAround($land, $x, $y, $HlandShuto, 19) + countAround($land, $x, $y, $HlandUmishuto, 19) + countAround($land, $x, $y, $HlandRizort, 19) + countAround($land, $x, $y, $HlandKajino, 19) + countAround($land, $x, $y, $HlandBigRizort, 19) - 6);
            my($ns) = ( 1 + 2 * countAround($land, $x, $y, $HlandPark, 19));
            my($nr) = ( 1 + 3 * countAround($land, $x, $y, $HlandUmiamu, 19));
            my($nu) = ( 10 + random(10));
            my($value);
            $value = ($nt * $nu * $ns * $nr + int($island->{'pop'} / 25));

	    if($island->{'shouhi'} > $island->{'ene'}) {
            $value = int($value/5);
            }

            if ($value > 0) {
                $island->{'money'} += $value;

                # 収入ログ
                my($str) = "$value$HunitMoney";
                logOilMoney($id, $name, landName($landKind, $lv), "($x, $y)", $str);
            }
            }

            # イベント判定
            if(random(100) < 10) { # 毎ターン 30% の確率でイベントが発生する
                # 野球場のイベント
                $value = int($island->{'pop'} / 50) * 10; # 人口５千人ごとに1000トンの食料消費
                $island->{'food'} -= $value;
                $str = "$value$HunitFood";

                logParkEvent($id, $name, landName($landKind, $lv), "($x, $y)", $str) if ($value > 0);
            }

            # 老朽化判定
            if(random(100) < 1) {
                # 施設が老朽化したため閉園
                logParkEnd($id, $name, landName($landKind, $lv), "($x, $y)");
                $land->[$x][$y] = $HlandPlains;
                $landValue->[$x][$y] = 0;
            }
	    if(random(100) < 3) {
	        my($value, $str, $lName);
	        $lName = landName($landKind, $lv);
	        $value = 500+ random(500);
	        $island->{'money'} += $value;
	        $str = "$value$HunitMoney";
                # 収入ログ
                logYusho($id, $name, $lName, "($x, $y)", $str) if ($value > 0);
	    }

        } elsif($landKind == $HlandUmiamu) {
            # 海あみゅ
            if (($island->{'kyu'} > 1) ||
		($island->{'amu'} > 1)) {
            } else {
            my($no) = (countAround($land, $x, $y, $HlandTown, 19) + countAround($land, $x, $y, $HlandProcity, 19) + countAround($land, $x, $y, $HlandMinato, 19) + countAround($land, $x, $y, $HlandSeacity, 19) + countAround($land, $x, $y, $HlandFrocity, 19) + countAround($land, $x, $y, $HlandNewtown, 19) + countAround($land, $x, $y, $HlandBigtown, 19) + countAround($land, $x, $y, $HlandBettown, 19) + countAround($land, $x, $y, $HlandSkycity, 19) + countAround($land, $x, $y, $HlandUmicity, 19) + countAround($land, $x, $y, $HlandSeatown, 19) + countAround($land, $x, $y, $HlandOnsen, 19) + countAround($land, $x, $y, $HlandShuto, 19) + countAround($land, $x, $y, $HlandUmishuto, 19) + countAround($land, $x, $y, $HlandRizort, 19) + countAround($land, $x, $y, $HlandKajino, 19) + countAround($land, $x, $y, $HlandBigRizort, 19) - 3);
            my($np) = ( 1 + 3 * countAround($land, $x, $y, $HlandPark, 19));
            my($nq) = ( 1 + 4 * countAround($land, $x, $y, $HlandKyujo, 19));
            my($nqk) = ( 1 + 4 * countAround($land, $x, $y, $HlandKyujokai, 19));
            my($nu) = ( 5 + random(5));
            my($value);
            $value = ($no * $np * $nq * $nqk * $nu + int($island->{'pop'} / 25)+ random(200));

	    if($island->{'shouhi'} > $island->{'ene'}) {
            $value = int($value/7);
            }

            if ($value > 0) {
                $island->{'money'} += $value;

                # 収入ログ
                my($str) = "$value$HunitMoney";
                logOilMoney($id, $name, landName($landKind, $lv), "($x, $y)", $str);
            }
            }

            # イベント判定
            if(random(100) < 10) { # 毎ターン 30% の確率でイベントが発生する
                # 野球場のイベント
                $value = int($island->{'pop'} / 50) * 10; # 人口５千人ごとに1000トンの食料消費
                $island->{'food'} -= $value;
                $str = "$value$HunitFood";

                logParkEvent($id, $name, landName($landKind, $lv), "($x, $y)", $str) if ($value > 0);
            }

        } elsif(($landKind == $HlandRottenSea) && ($lv < 20)) {
        # 腐海
	$landValue->[$x][$y]++;
        my($i, $sx, $sy, $kind, $lv);
            for($i = 1; $i < 7; $i++) {
                $sx = $x + $ax[$i];
                $sy = $y + $ay[$i];

                    # 行による位置調整
                    if((($sy % 2) == 0) && (($y % 2) == 1)) {
                        $sx--;
                    }

		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    # 範囲外
		    next;
		}

                $landKind = $land->[$sx][$sy];
                $lv   = $landValue->[$sx][$sy];
	        $lName = landName($landKind, $lv);
		# 海、海基、海底都市、油田、怪獣、山、記念碑以外
		if(($land->[$sx][$sy] != $HlandSea) &&
		   ($land->[$sx][$sy] != $HlandSbase) &&
		   ($land->[$sx][$sy] != $HlandIce) &&
		   ($land->[$sx][$sy] != $HlandSeacity) &&
		   ($land->[$sx][$sy] != $HlandSeatown) &&
		   ($land->[$sx][$sy] != $HlandUmishuto) &&
		   ($land->[$sx][$sy] != $HlandFune) &&
		   ($land->[$sx][$sy] != $HlandFrocity) &&
		   ($land->[$sx][$sy] != $HlandUmiamu) &&
		   ($land->[$sx][$sy] != $HlandOil) &&
		   ($land->[$sx][$sy] != $HlandNursery) &&
		   ($land->[$sx][$sy] != $HlandRottenSea)) {
	        my($n) = countAround($land, $sx, $sy, $HlandRottenSea, 7);
	        my($point) = "($sx, $sy)";
	            if (($n >= 4) && ((rand(1000)+$island->{'m73'}*100) < 300)) {
	                # 周囲に腐海が４マス以上あれば ６０% の確率で飲み込む
	                 logRottenSeaGrow($id, $name, $lName, $point);
	                 $land->[$sx][$sy] = $HlandRottenSea;
	                 $landValue->[$sx][$sy] = 1;
	            } elsif ($n && ((rand(1000)+$island->{'m73'}*100) < 200)) {
	                 # 周囲に腐海が１マス以上あれば２０% の確率で飲み込む
	                 logRottenSeaGrow($id, $name, $lName, $point);
	                 $land->[$sx][$sy] = $HlandRottenSea;
	                 $landValue->[$sx][$sy] = 1;
	            }
	        }
	    }

        } elsif(($landKind == $HlandRottenSea) && ($lv >= 20)) {
	$landValue->[$x][$y]++;
		if($landValue->[$x][$y] > 4000) {
		    $land->[$x][$y] = $HlandWaste;
		    $landValue->[$x][$y] = 0;
		} elsif(($landValue->[$x][$y] > 1000) && (random(250) == 0)) {
		    $land->[$x][$y] = $HlandMonument;
		    $landValue->[$x][$y] = 80+random(3);
		} elsif(($landValue->[$x][$y] > 750) && (random(250) == 0)) {
		    $land->[$x][$y] = $HlandMonument;
		    $landValue->[$x][$y] = 73;
		} elsif(($landValue->[$x][$y] > 500) && (random(250) == 0)) {
		    $land->[$x][$y] = $HlandMonument;
		    $landValue->[$x][$y] = 74+random(5);
		} elsif(($landValue->[$x][$y] > 250) && (random(250) == 0)) {
		    $land->[$x][$y] = $HlandMonument;
		    $landValue->[$x][$y] = 87;
		} elsif(($landValue->[$x][$y] > 125) && (random(250) == 0) && ($island->{'m84'} < 4)) {
		    $land->[$x][$y] = $HlandMonument;
		    $landValue->[$x][$y] = 84;
		}

	} elsif($landKind == $HlandCollege) {
	    # 各要素の取り出し
	    my($clv) = $landValue->[$x][$y];

	    if($clv == 4) {

	    my($i,$sx,$sy);
	    for($i = 0; $i < $HpointNumber; $i++){
		$sx = $Hrpx[$i];
		$sy = $Hrpy[$i];
	    if($land->[$sx][$sy] == $HlandMonster) {
		# 対象となる怪獣の各要素取り出し
		my($tKind, $tName, $tHp) = monsterSpec($landValue->[$sx][$sy]);
		my($tlv) = $landValue->[$sx][$sy];
		my($tspecial) = $HmonsterSpecial[$tKind];
		if($tKind == 28) {
		} else {
		    my($ssx, $ssy, $i, $landKind, $landName, $lv, $point);
		    for($i = 0; $i < 7; $i++) {
			$ssx = $sx + $ax[$i];
			$ssy = $sy + $ay[$i];

			# 行による位置調整
			if((($ssy % 2) == 0) && (($sy % 2) == 1)) {
			    $ssx--;
			}

			$landKind = $land->[$ssx][$ssy];
			$lv = $landValue->[$ssx][$ssy];
			$landName = landName($landKind, $lv);
			$point = "($ssx, $ssy)";

			# 範囲外判定
			if(($ssx < 0) || ($ssx >= $HislandSize) ||
			   ($ssy < 0) || ($ssy >= $HislandSize)) {
			    next;
			}

			# 範囲による分岐
			if($i < 1) {
				next;
			} else {
			    # 2ヘックス
			    if($take < 1) {
			    if(($landKind == $HlandWaste) &&
				($island->{'c28'} == 0)) {
				$eisei5 = $island->{'eisei5'};
				$eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tet) = ($1, $2, $3, $4, $5, $6, $7);

				$kind = 28;
				$lv = $lv = ($kind << 4)
				+ $HmonsterBHP[$kind] + random($HmonsterDHP[$kind])+$mshp;
				$land->[$ssx][$ssy] = $HlandMonster;
				$landValue->[$ssx][$ssy] = $lv;
				logMstakeon($id, $name, "生物大学のマスコットいのら","($x, $y)");

				$landValue->[$x][$y] = 99;
				$take++;
				$island->{'co99'}++;
				$island->{'monsterlive'}++;
				}
			    }
			}
		    }
		    }
		}
		}
	    }

	    if($clv == 98) {

	    my($i,$sx,$sy);
	    for($i = 0; $i < $HpointNumber; $i++){
		$sx = $Hrpx[$i];
		$sy = $Hrpy[$i];
	    if($land->[$sx][$sy] == $HlandMonster) {
		# 対象となる怪獣の各要素取り出し
		my($tKind, $tName, $tHp) = monsterSpec($landValue->[$sx][$sy]);
		my($tlv) = $landValue->[$sx][$sy];
		my($tspecial) = $HmonsterSpecial[$tKind];
		if($tKind == 30) {
		} else {
		    my($ssx, $ssy, $i, $landKind, $landName, $lv, $point);
		    for($i = 0; $i < 7; $i++) {
			$ssx = $sx + $ax[$i];
			$ssy = $sy + $ay[$i];

			# 行による位置調整
			if((($ssy % 2) == 0) && (($sy % 2) == 1)) {
			    $ssx--;
			}

			$landKind = $land->[$ssx][$ssy];
			$lv = $landValue->[$ssx][$ssy];
			$landName = landName($landKind, $lv);
			$point = "($ssx, $ssy)";

			# 範囲外判定
			if(($ssx < 0) || ($ssx >= $HislandSize) ||
			   ($ssy < 0) || ($ssy >= $HislandSize)) {
			    next;
			}

			# 範囲による分岐
			if($i < 1) {
				next;
			} else {
			    # 2ヘックス
			    if($take < 1) {
			    if(($landKind == $HlandWaste) &&
				($island->{'c28'} == 0)) {
				$eisei5 = $island->{'eisei5'};
				$eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tet) = ($1, $2, $3, $4, $5, $6, $7);

				$kind = 30;
				$lv = $lv = ($kind << 4)
				+ $HmonsterBHP[$kind] + random($HmonsterDHP[$kind])+$mshp;
				$land->[$ssx][$ssy] = $HlandMonster;
				$landValue->[$ssx][$ssy] = $lv;
				logMstakeon($id, $name, "超神獣テトラ","($x, $y)");

				$landValue->[$x][$y] = 99;
				$take++;
				$island->{'co99'}++;
				$island->{'monsterlive'}++;
				}
			    }
			}
		    }
		    }
		}
		}
	    }

	    if($clv == 99) {
		if($island->{'c28'} == 0) {
                $land->[$x][$y] = $HlandPlains;
                $landValue->[$x][$y] = 0;
		logMstakeoff($id, $name, landName($landKind, $lv),"($x, $y)");
		}
	    }

	    if($clv == 80) {
		my($shutoCount) = (0);
		my($houseCount) = (0);
		my($foodimCount) = (0);
		my($htfCount) = (0);
		my($shtfCount) = (0);
		my($i, $sx, $sy, $kind, $lv);
		for($i = 1; $i < 7; $i++) {
		    $sx = $x + $ax[$i];
		    $sy = $y + $ay[$i];

		    # 行による位置調整
		    if((($sy % 2) == 0) && (($y % 2) == 1)) {
			$sx--;
		    }

		    $landKind = $land->[$sx][$sy];
		    $lv = $landValue->[$sx][$sy];
		    $point = "($sx, $sy)";

		    if(($sx < 0) || ($sx >= $HislandSize) ||
		       ($sy < 0) || ($sy >= $HislandSize)) {
		    } else {
			# 範囲内の場合
			$landKind = $land->[$sx][$sy];
			$lv = $landValue->[$sx][$sy];
			$point = "($sx, $sy)";
			if(($landKind == $HlandShuto) || ($landKind == $HlandUmishuto)) {
			    $shutoCount++;
			} elsif($landKind == $HlandHouse) {
			    $houseCount++;
			} elsif(($landKind == $HlandFoodim) && ($lv == 500)) {
			    $foodimCount++;
			} elsif(($landKind == $HlandHTFactory) && ($lv == 500)) {
			    $htfCount++;
			} elsif(($landKind == $HlandSHTF) && ($lv == 500)) {
			    $shtfCount++;
			}
		    }
		}

		if(($island->{'ownf'} == 0) && ($shutoCount == 1) && ($houseCount == 1) && ($foodimCount == 1) && ($htfCount == 1) && ($shtfCount == 1)) {
		    my($onm);
		    $onm = $island->{'onm'};
		    logOwnFac($id, $name, landName($land->[$x][$y], $landValue->[$x][$y]),"($x, $y)", "$onm");
		    $land->[$x][$y] = $HlandOWNF;
		    $landValue->[$x][$y] = 111;
			my($i, $sx, $sy, $kind, $lv);
			for($i = 1; $i < 7; $i++) {
			    $sx = $x + $ax[$i];
			    $sy = $y + $ay[$i];
			    if((($sy % 2) == 0) && (($y % 2) == 1)) {
				$sx--;
			    }
			    $landKind = $land->[$sx][$sy];
			    $lv = $landValue->[$sx][$sy];
			    $point = "($sx, $sy)";
			    if(($sx < 0) || ($sx >= $HislandSize) ||
			       ($sy < 0) || ($sy >= $HislandSize)) {
			    } else {
				$landKind = $land->[$sx][$sy];
				$lv = $landValue->[$sx][$sy];
				$point = "($sx, $sy)";
				if(($landKind == $HlandFoodim) && ($lv == 500)) {
				    $land->[$sx][$sy] = $HlandPlains2;
				    $landValue->[$sx][$sy] = 0;
				} elsif(($landKind == $HlandHTFactory) && ($lv == 500)) {
				    $land->[$sx][$sy] = $HlandPlains2;
				    $landValue->[$sx][$sy] = 0;
				} elsif(($landKind == $HlandSHTF) && ($lv == 500)) {
				    $land->[$sx][$sy] = $HlandPlains2;
				    $landValue->[$sx][$sy] = 0;
				}
			    }
			}
		}

	    }

	    if(($clv == 77) || ($clv == 78) || ($clv == 79) || ($clv == 80)) {
		if(($island->{'co0'} < 1) ||
		   ($island->{'co01'} < 1) ||
		   ($island->{'co2'} < 1) ||
		   ($island->{'co3'} < 1) ||
		   ($island->{'co4'} < 1) ||
		   ($island->{'co5'} < 1) ||
		   ($island->{'co6'} < 1) ||
		   ($island->{'co7'} < 1) ||
		   ($island->{'co8'} < 1) ||
		   ($island->{'eis7'} < 1000000) ||
		   ($island->{'rena'} < 10000) ||
		   ($island->{'pts'} < $HouseLevel7)) {
		$land->[$x][$y] = $HlandYakusho;
		$landValue->[$x][$y] = 0;
		}
	    }

	} elsif($landKind == $HlandOWNF) {
	    $ownfe = int($lv/1000);
	    $shts = int($lv/100)%10;
	    $hts = int($lv%100/10);
	    $noujous = $lv%10;
	    $totals = $shts + $hts + $noujous;
	    $etc5 = $island->{'etc5'};
	    $etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
	    $costseisaku = $s01+$s03+$s05+$s07+$s09+$s11+$s13+$s15+$s17+$s19+$s21+$s23+$s25+$s27+$s29+$s02+$s04+$s06+$s08+$s10+$s12+$s14+$s16+$s18+$s20+$s22+$s24+$s26+$s28+$s30;

	    my($onm);
	    $onm = $island->{'onm'};
	    my($unemployed);
	    $unemployed = ($island->{'pop'} - ($island->{'farm'} + $island->{'factoryt'} + $island->{'mountain'}) * 10) / $island->{'pop'} * 100;
		if($unemployed < 0) {
		    $unemployed = -1*$unemployed;
		}
		if($island->{'ownf'} > 1) {
		    $land->[$x][$y] = $HlandPlains2;
		    $landValue->[$x][$y] = 0;
		    $island->{'ownf'} -= 1;
		}

	            if($island->{'urikireflag'} == 1) {
			$landValue->[$x][$y] = "$shts$hts$noujous";
		    }

	            if((random(1000) < int($island->{'rena'}/1000)) && ($ownfe == 0)) {
			$landValue->[$x][$y] = "1$shts$hts$noujous";
			logMiyage2($id, $name, "$onm", "($x, $y)", "腐海の毒消し薬");
		    }

		my($shutoCount) = (0);
		my($houseCount) = (0);
		my($i, $sx, $sy, $kind, $lv);
		for($i = 1; $i < 7; $i++) {
		    $sx = $x + $ax[$i];
		    $sy = $y + $ay[$i];

		    # 行による位置調整
		    if((($sy % 2) == 0) && (($y % 2) == 1)) {
			$sx--;
		    }

		    $landKind = $land->[$sx][$sy];
		    $lv = $landValue->[$sx][$sy];
		    $point = "($sx, $sy)";

		    if(($sx < 0) || ($sx >= $HislandSize) ||
		       ($sy < 0) || ($sy >= $HislandSize)) {
		    } else {
			# 範囲内の場合
			$landKind = $land->[$sx][$sy];
			$lv = $landValue->[$sx][$sy];
			$point = "($sx, $sy)";
			if(($landKind == $HlandShuto) || ($landKind == $HlandUmishuto)) {
			    $shutoCount++;
			} elsif($landKind == $HlandHouse) {
			    $houseCount++;
			}
		    }
		}
			my($i, $sx, $sy, $kind, $lv);
			for($i = 1; $i < 7; $i++) {
			    $sx = $x + $ax[$i];
			    $sy = $y + $ay[$i];
			    if((($sy % 2) == 0) && (($y % 2) == 1)) {
				$sx--;
			    }
			    $landKind = $land->[$sx][$sy];
			    $lv = $landValue->[$sx][$sy];
			    $point = "($sx, $sy)";
			    if(($sx < 0) || ($sx >= $HislandSize) ||
			       ($sy < 0) || ($sy >= $HislandSize)) {
			    } else {
				$landKind = $land->[$sx][$sy];
				$lv = $landValue->[$sx][$sy];
				$point = "($sx, $sy)";
				if(($landKind == $HlandFoodim) && ($lv == 500) && ($noujous < 8) && ((8-$noujous)*20 > $unemployed) && ($shutoCount == 1) && ($houseCount == 1) && ($noujous*15 < $costseisaku) && ((24-$totals)*5 > $unemployed) && ($totals*5 < $costseisaku) && ($totals*800 < $island->{'rena'}) && ($noujous*1875 < $island->{'rena'})) {
					logOwnFac2($id, $name, landName($land->[$x][$y], $landValue->[$x][$y]), landName($land->[$sx][$sy], $landValue->[$sx][$sy]),"($x, $y)", "$onm");
				    $land->[$sx][$sy] = $HlandPlains2;
				    $landValue->[$sx][$sy] = 0;
				    $landValue->[$x][$y] += 1;
				    $noujous++;
				    $totals++;
				} elsif(($landKind == $HlandHTFactory) && ($lv == 500) && ($hts < 8) && ((8-$hts)*20 > $unemployed) && ($shutoCount == 1) && ($houseCount == 1) && ($hts*15 < $costseisaku) && ((24-$totals)*5 > $unemployed) && ($totals*5 < $costseisaku) && ($totals*800 < $island->{'rena'}) && ($hts*1875 < $island->{'rena'})) {
					logOwnFac2($id, $name, landName($land->[$x][$y], $landValue->[$x][$y]), landName($land->[$sx][$sy], $landValue->[$sx][$sy]),"($x, $y)", "$onm");
				    $land->[$sx][$sy] = $HlandPlains2;
				    $landValue->[$sx][$sy] = 0;
				    $landValue->[$x][$y] += 10;
				    $hts++;
				    $totals++;
				} elsif(($landKind == $HlandSHTF) && ($lv == 500) && ($shts < 8) && ((8-$shts)*20 > $unemployed) && ($shutoCount == 1) && ($houseCount == 1) && ($shts*15 < $costseisaku) && ((24-$totals)*5 > $unemployed) && ($totals*5 < $costseisaku) && ($totals*800 < $island->{'rena'}) && ($shts*1875 < $island->{'rena'})) {
					logOwnFac2($id, $name, landName($land->[$x][$y], $landValue->[$x][$y]), landName($land->[$sx][$sy], $landValue->[$sx][$sy]),"($x, $y)", "$onm");
				    $land->[$sx][$sy] = $HlandPlains2;
				    $landValue->[$sx][$sy] = 0;
				    $landValue->[$x][$y] += 100;
				    $shts++;
				    $totals++;
				}
			    }
			}

	} elsif($landKind == $HlandMonument) {

	     # 各要素の取り出し
	     my($molv) = $landValue->[$x][$y];

	     if(($molv == 0) ||
		($molv == 15) ||
		($molv == 16) ||
	        ($molv == 10)) {
	            if(random(100) < 5) {
		    # 収穫
		    my($value, $str, $lName);
		    $lName = landName($landKind, $lv);
		    $value = 1+ random(49);
		    $island->{'money'} += $value;
		    $str = "$value$HunitMoney";
	            logMiyage($id, $name, $lName, "($x, $y)", $str) if ($value > 0);
		    }
	    } elsif($molv == 1) {
	            if(random(100) < 1) {
		    # 収穫
		    my($value, $str, $lName);
		    $lName = landName($landKind, $lv);
	            $value = int($island->{'pop'} / 100) * 10+ random(11); # 人口５千人ごとに1000トンの食料消費
	            $island->{'food'} += $value;
	            $str = "$value$HunitFood";

	                logParkEventt($id, $name, $lName, "($x, $y)", $str) if ($value > 0);
		    }

	    } elsif($molv == 80) {
	            if(random(100) < 5) {
		    # 卵復活
		    for($i = 0; $i < 7; $i++) {
			$sx = $x + $ax[$i];
			$sy = $y + $ay[$i];

			# 行による位置調整
			if((($sy % 2) == 0) && (($y % 2) == 1)) {
			    $sx--;
			}

			$landKind = $land->[$sx][$sy];
			$lv = $landValue->[$sx][$sy];
			$landName = landName($landKind, $lv);
			$point = "($sx, $sy)";

			# 範囲外判定
			if(($sx < 0) || ($sx >= $HislandSize) ||
			   ($sy < 0) || ($sy >= $HislandSize)) {
			    next;
			}

			# 範囲による分岐
			if($i < 1) {
			    # 中心、および1ヘックス
		            if(random(100) < 5) {
				$kind = 13;  # ミカエル
			    } elsif(random(100) < 25) {
				$kind = 29;  # テトラ
			    } elsif(random(100) < 35) {
				$kind = 14;  # スラレジェ
			    } elsif(random(100) < 25) {
				$kind = 12;  # はねはむ
			    } else {
				$kind = 1;  # いのら(はずれ)
			    }

				$lv = $lv = ($kind << 4)
				    + $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
				$land->[$sx][$sy] = $HlandMonster;
				$landValue->[$sx][$sy] = $lv;
				    my($mKind, $mName, $mHp) = monsterSpec($lv);
				    logEggBomb($id, $name, $landName, $mName, $point);

			} else {
			    # 2ヘックス
			    if(($landKind == $HlandSea) ||
			       ($landKind == $HlandOil) ||
			       ($landKind == $HlandMountain) ||
			       ($landKind == $HlandGold) ||
			       ($landKind == $HlandOnsen) ||
			       ($landKind == $HlandSeacity) ||
			       ($landKind == $HlandUmishuto) ||
			       ($landKind == $HlandSeatown) ||
			       ($landKind == $HlandUmiamu) ||
			       ($landKind == $HlandFune) ||
			       ($landKind == $HlandFrocity) ||
			       ($landKind == $HlandSbase)) {
				next;
			    } else {
				$landName = landName($landKind, $lv);
				logEggDamage($id, $name, $landName, $point);
				$land->[$sx][$sy] = $HlandSea;
				$landValue->[$sx][$sy] = 0;
			    }
			}
		    }
		}

	    } elsif($molv == 81) {
	            if(random(100) < 3) {
		    # 卵復活
		    for($i = 0; $i < 7; $i++) {
			$sx = $x + $ax[$i];
			$sy = $y + $ay[$i];

			# 行による位置調整
			if((($sy % 2) == 0) && (($y % 2) == 1)) {
			    $sx--;
			}

			$landKind = $land->[$sx][$sy];
			$lv = $landValue->[$sx][$sy];
			$landName = landName($landKind, $lv);
			$point = "($sx, $sy)";

			# 範囲外判定
			if(($sx < 0) || ($sx >= $HislandSize) ||
			   ($sy < 0) || ($sy >= $HislandSize)) {
			    next;
			}

			# 範囲による分岐
			if($i < 1) {
			    # 中心、および1ヘックス
		            if(random(100) < 3) {
				$kind = 13;  # ミカエル
			    } elsif(random(100) < 20) {
				$kind = 29;  # テトラ
			    } elsif(random(100) < 40) {
				$kind = 14;  # スラレジェ
			    } elsif(random(100) < 15) {
				$kind = 12;  # はねはむ
			    } else {
				$kind = 1;  # いのら(はずれ)
			    }

				$lv = $lv = ($kind << 4)
				    + $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
				$land->[$sx][$sy] = $HlandMonster;
				$landValue->[$sx][$sy] = $lv;
				    my($mKind, $mName, $mHp) = monsterSpec($lv);
				    logEggBomb($id, $name, $landName, $mName, $point);

			} else {
			    # 2ヘックス
			    if(($landKind == $HlandSea) ||
			       ($landKind == $HlandOil) ||
			       ($landKind == $HlandMountain) ||
			       ($landKind == $HlandGold) ||
			       ($landKind == $HlandOnsen) ||
			       ($landKind == $HlandSeacity) ||
			       ($landKind == $HlandSeatown) ||
			       ($landKind == $HlandUmishuto) ||
			       ($landKind == $HlandUmiamu) ||
			       ($landKind == $HlandFune) ||
			       ($landKind == $HlandFrocity) ||
			       ($landKind == $HlandSbase)) {
				next;
			    } else {
				$landName = landName($landKind, $lv);
				logEggDamage($id, $name, $landName, $point);
				$land->[$sx][$sy] = $HlandSea;
				$landValue->[$sx][$sy] = 0;
			    }
			}
		    }
		}

	    } elsif($molv == 82) {
	            if(random(100) < 3) {
		    # 卵復活
		    for($i = 0; $i < 7; $i++) {
			$sx = $x + $ax[$i];
			$sy = $y + $ay[$i];

			# 行による位置調整
			if((($sy % 2) == 0) && (($y % 2) == 1)) {
			    $sx--;
			}

			$landKind = $land->[$sx][$sy];
			$lv = $landValue->[$sx][$sy];
			$landName = landName($landKind, $lv);
			$point = "($sx, $sy)";

			# 範囲外判定
			if(($sx < 0) || ($sx >= $HislandSize) ||
			   ($sy < 0) || ($sy >= $HislandSize)) {
			    next;
			}

			# 範囲による分岐
			if($i < 1) {
			    # 中心、および1ヘックス
		            if(random(100) < 3) {
				$kind = 13;  # ミカエル
			    } elsif(random(100) < 30) {
				$kind = 29;  # テトラ
			    } elsif(random(100) < 40) {
				$kind = 14;  # スラレジェ
			    } elsif(random(100) < 30) {
				$kind = 12;  # はねはむ
			    } else {
				$kind = 1;  # いのら(はずれ)
			    }

				$lv = $lv = ($kind << 4)
				    + $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
				$land->[$sx][$sy] = $HlandMonster;
				$landValue->[$sx][$sy] = $lv;
				    my($mKind, $mName, $mHp) = monsterSpec($lv);
				    logEggBomb($id, $name, $landName, $mName, $point);

			} else {
			    # 2ヘックス
			    if(($landKind == $HlandSea) ||
			       ($landKind == $HlandOil) ||
			       ($landKind == $HlandMountain) ||
			       ($landKind == $HlandGold) ||
			       ($landKind == $HlandOnsen) ||
			       ($landKind == $HlandSeacity) ||
			       ($landKind == $HlandSeatown) ||
			       ($landKind == $HlandUmishuto) ||
			       ($landKind == $HlandUmiamu) ||
			       ($landKind == $HlandFune) ||
			       ($landKind == $HlandFrocity) ||
			       ($landKind == $HlandSbase)) {
				next;
			    } else {
				$landName = landName($landKind, $lv);
				logEggDamage($id, $name, $landName, $point);
				$land->[$sx][$sy] = $HlandSea;
				$landValue->[$sx][$sy] = 0;
			    }
			}
		    }
		}

	    } elsif($molv == 83) {
	            if(random(100) < 5) {
		    # 卵復活
		    for($i = 0; $i < 7; $i++) {
			$sx = $x + $ax[$i];
			$sy = $y + $ay[$i];

			# 行による位置調整
			if((($sy % 2) == 0) && (($y % 2) == 1)) {
			    $sx--;
			}

			$landKind = $land->[$sx][$sy];
			$lv = $landValue->[$sx][$sy];
			$landName = landName($landKind, $lv);
			$point = "($sx, $sy)";

			# 範囲外判定
			if(($sx < 0) || ($sx >= $HislandSize) ||
			   ($sy < 0) || ($sy >= $HislandSize)) {
			    next;
			}

			# 範囲による分岐
			if($i < 1) {
			    # 中心、および1ヘックス
		            if(random(100) < 10) {
				$kind = 13;  # ミカエル
			    } elsif(random(100) < 25) {
				$kind = 29;  # テトラ
			    } elsif(random(100) < 30) {
				$kind = 14;  # スラレジェ
			    } elsif(random(100) < 30) {
				$kind = 12;  # はねはむ
			    } else {
				$kind = 1;  # いのら(はずれ)
			    }

				$lv = $lv = ($kind << 4)
				    + $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
				$land->[$sx][$sy] = $HlandMonster;
				$landValue->[$sx][$sy] = $lv;
				    my($mKind, $mName, $mHp) = monsterSpec($lv);
				    logEggBomb($id, $name, $landName, $mName, $point);

			} else {
			    # 2ヘックス
			    if(($landKind == $HlandSea) ||
			       ($landKind == $HlandOil) ||
			       ($landKind == $HlandMountain) ||
			       ($landKind == $HlandGold) ||
			       ($landKind == $HlandOnsen) ||
			       ($landKind == $HlandSeacity) ||
			       ($landKind == $HlandSeatown) ||
			       ($landKind == $HlandUmishuto) ||
			       ($landKind == $HlandUmiamu) ||
			       ($landKind == $HlandFune) ||
			       ($landKind == $HlandFrocity) ||
			       ($landKind == $HlandSbase)) {
				next;
			    } else {
				$landName = landName($landKind, $lv);
				logEggDamage($id, $name, $landName, $point);
				$land->[$sx][$sy] = $HlandSea;
				$landValue->[$sx][$sy] = 0;
			    }
			}
		    }
		}

	    } elsif($molv == 84) {
	            if(random(100) < 75) {
		    # 収穫
		    my($lName);
		    $lName = landName($landKind, $lv);
	            my($nt) = (countAround($land, $x, $y, $HlandTown, 19) + countAround($land, $x, $y, $HlandProcity, 19) + countAround($land, $x, $y, $HlandMinato, 19) + countAround($land, $x, $y, $HlandSeacity, 19) + countAround($land, $x, $y, $HlandFrocity, 19) + countAround($land, $x, $y, $HlandNewtown, 19) + countAround($land, $x, $y, $HlandBigtown, 19) + countAround($land, $x, $y, $HlandBettown, 19) + countAround($land, $x, $y, $HlandSkycity, 19) + countAround($land, $x, $y, $HlandUmicity, 19) + countAround($land, $x, $y, $HlandSeatown, 19) + countAround($land, $x, $y, $HlandOnsen, 19) + countAround($land, $x, $y, $HlandShuto, 19) + countAround($land, $x, $y, $HlandUmishuto, 19) + countAround($land, $x, $y, $HlandRizort, 19) + countAround($land, $x, $y, $HlandKajino, 19) + countAround($land, $x, $y, $HlandBigRizort, 19));
	            my($value);
	            $value = random($nt * 20 + $lv * 5 + int($island->{'pop'} / 20)) + random(100) + 100;
	            if ($value > 0) {
	                $island->{'money'} += $value;

			$m84income += $value;
	            }
		    }
	    } elsif($molv == 93) {
		    # 幸運
		    my($value, $str, $lName);
		    $lName = landName($landKind, $lv);
		    $value = $HoilMoney+ random(500);
		    $island->{'money'} += $value;
		    $str = "$value$HunitMoney";

	            $value = int($island->{'pop'} / 20) + random(11); # 人口５千人ごとに1000トンの食料消費
	            $island->{'food'} += $value;
	            $str = "$value$HunitFood";

	    } elsif($molv == 94) {

		    my($i,$sx,$sy);
		    for($i = 1; $i < 7; $i++) {
		        $sx = $x + $ax[$i];
		        $sy = $y + $ay[$i];
			    if($land->[$sx][$sy] == $HlandMonster){
				# 周囲2Hexに別の怪獣がいる場合、その怪獣を攻撃する

				# 対象となる怪獣の各要素取り出し
				my($tKind, $tName, $tHp) = monsterSpec($landValue->[$sx][$sy]);
				my($tlv) = $landValue->[$sx][$sy];
				my($tspecial) = $HmonsterSpecial[$tKind];

				    logBariaAttack($id, $name, $tName, "($sx, $sy)");
			    # 対象の怪獣が倒れて荒地になる
				$land->[$sx][$sy] = $HlandWaste;
				$landValue->[$sx][$sy] = 1;
			    next;
			    }
		    }
	    }

	} elsif($landKind == $HlandFrocity) {

	    if($addpop < 0) {
		# 不足
		$lv -= (random(-$addpop) + 1);
		if($lv <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandPlains;
		    $landValue->[$x][$y] = 0;
		    next;
		}
	    } else {
		# 成長
		if($lv < 100) {
		    $lv += random($addpop) + 1;
		    if($lv > 100) {
			$lv = 100;
		    }
		} else {
		    # 都市になると成長遅い
		    if($addpop2 > 0) {
			$lv += random($addpop2) + 1;
		    }
		}
	    }
	    if($lv > 200) {
		$lv = 200;
	    }
	    $landValue->[$x][$y] = $lv;

	    # 動く方向を決定
	    my($d, $sx, $sy);
	    my($i);
	    for($i = 0; $i < 3; $i++) {
		$d = random(6) + 1;
		$sx = $x + $ax[$d];
		$sy = $y + $ay[$d];

		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}

		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}

		# 海、海基、海底都市、油田、怪獣、山、記念碑以外
		if(($land->[$sx][$sy] != $HlandWaste) &&
		   ($land->[$sx][$sy] != $HlandPlains) &&
		   ($land->[$sx][$sy] != $HlandPlains2) &&
		   ($land->[$sx][$sy] != $HlandTown) &&
		   ($land->[$sx][$sy] != $HlandForest) &&
		   ($land->[$sx][$sy] != $HlandFarm) &&
		   ($land->[$sx][$sy] != $HlandEneAt) &&
		   ($land->[$sx][$sy] != $HlandEneFw) &&
		   ($land->[$sx][$sy] != $HlandEneWt) &&
		   ($land->[$sx][$sy] != $HlandEneWd) &&
		   ($land->[$sx][$sy] != $HlandEneBo) &&
		   ($land->[$sx][$sy] != $HlandEneSo) &&
		   ($land->[$sx][$sy] != $HlandEneCs) &&
		   ($land->[$sx][$sy] != $HlandConden) &&
		   ($land->[$sx][$sy] != $HlandConden2) &&
		   ($land->[$sx][$sy] != $HlandConden3) &&
		   ($land->[$sx][$sy] != $HlandConden4) &&
		   ($land->[$sx][$sy] != $HlandFoodim) &&
		   ($land->[$sx][$sy] != $HlandFoodka) &&
		   ($land->[$sx][$sy] != $HlandFarmchi) &&
		   ($land->[$sx][$sy] != $HlandFarmpic) &&
		   ($land->[$sx][$sy] != $HlandFarmcow) &&
		   ($land->[$sx][$sy] != $HlandCollege) &&
		   ($land->[$sx][$sy] != $HlandYakusho) &&
		   ($land->[$sx][$sy] != $HlandFactory) &&
		   ($land->[$sx][$sy] != $HlandHTFactory) &&
		   ($land->[$sx][$sy] != $HlandSHTF) &&
		   ($land->[$sx][$sy] != $HlandOWNF) &&
		   ($land->[$sx][$sy] != $HlandBase) &&
		   ($land->[$sx][$sy] != $HlandDefence) &&
		   ($land->[$sx][$sy] != $HlandMinato) &&
		   ($land->[$sx][$sy] != $HlandSeki) &&
		   ($land->[$sx][$sy] != $HlandPark) &&
		   ($land->[$sx][$sy] != $HlandHaribote) &&
		   ($land->[$sx][$sy] != $HlandSbase) &&
		   ($land->[$sx][$sy] != $HlandSeacity) &&
		   ($land->[$sx][$sy] != $HlandFune) &&
		   ($land->[$sx][$sy] != $HlandIce) &&
		   ($land->[$sx][$sy] != $HlandFrocity) &&
		   ($land->[$sx][$sy] != $HlandUmiamu) &&
		   ($land->[$sx][$sy] != $HlandOil) &&
		   ($land->[$sx][$sy] != $HlandGold) &&
		   ($land->[$sx][$sy] != $HlandMountain) &&
		   ($land->[$sx][$sy] != $HlandOnsen) &&
		   ($land->[$sx][$sy] != $HlandMonument) &&
		   ($land->[$sx][$sy] != $HlandMine) &&
		   ($land->[$sx][$sy] != $HlandNursery) &&
		   ($land->[$sx][$sy] != $HlandKyujo) &&
		   ($land->[$sx][$sy] != $HlandKyujokai) &&
		   ($land->[$sx][$sy] != $HlandZoo) &&
		   ($land->[$sx][$sy] != $HlandRottenSea) &&
		   ($land->[$sx][$sy] != $HlandProcity) &&
		   ($land->[$sx][$sy] != $HlandNewtown) &&
		   ($land->[$sx][$sy] != $HlandBigtown) &&
		   ($land->[$sx][$sy] != $HlandBettown) &&
		   ($land->[$sx][$sy] != $HlandSkycity) &&
		   ($land->[$sx][$sy] != $HlandUmicity) &&
		   ($land->[$sx][$sy] != $HlandSeatown) &&
		   ($land->[$sx][$sy] != $HlandRizort) &&
		   ($land->[$sx][$sy] != $HlandKajino) &&
		   ($land->[$sx][$sy] != $HlandBigRizort) &&
		   ($land->[$sx][$sy] != $HlandShuto) &&
		   ($land->[$sx][$sy] != $HlandUmishuto) &&
		   ($land->[$sx][$sy] != $HlandHouse) &&
		   ($land->[$sx][$sy] != $HlandTaishi) &&
		   ($land->[$sx][$sy] != $HlandTrain) &&
		   ($land->[$sx][$sy] != $HlandKura) &&
		   ($land->[$sx][$sy] != $HlandKuraf) &&
		   ($land->[$sx][$sy] != $HlandMonster)) {
		    last;
		}
	    }

	    if($i == 3) {
		# 動かなかった
		next;
	    }

	    # 動いた先の地形によりメッセージ
	    my($l) = $land->[$sx][$sy];
	    my($lv) = $landValue->[$sx][$sy];
	    my($lName) = landName($l, $lv);
	    my($point) = "($sx, $sy)";

	    # 移動
	    $land->[$sx][$sy] = $land->[$x][$y];
	    $landValue->[$sx][$sy] = $landValue->[$x][$y];

	    # もと居た位置を荒地に
	    $land->[$x][$y] = $HlandSea;
	    $landValue->[$x][$y] = 0;

	} elsif($landKind == $HlandFune) {
	    # 怪獣
	    if($funeMove[$x][$y] == 2) {
		# すでに動いた後
		next;
	    }

	    # 各要素の取り出し
	    my($flv) = $landValue->[$x][$y];
	    my($funespe) = $HfuneSpecial[$lv];

            # 老朽化判定
	    my($lName) = &landName($landKind, $lv);
	    if(($flv == 8) ||
	       ($flv == 9) ||
	       ($flv == 19) ||
	       ($flv == 10)) {
		if(random(1000) < 5) {
                # 施設が老朽化したため閉園
                logParkEndf($id, $name, $lName, "($x, $y)");
                $land->[$x][$y] = $HlandSea;
                $landValue->[$x][$y] = 0;
                }
            } else {
		if(random(100) < 3) {
                # 施設が老朽化したため閉園
                logParkEndf($id, $name, $lName, "($x, $y)");
                $land->[$x][$y] = $HlandSea;
                $landValue->[$x][$y] = 0;
                }
            }

	    my($flv) = $landValue->[$x][$y];
	    my($funespe) = $HfuneSpecial[$lv];

	    if($flv == 0) {
	    # 収穫
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = 1+ random(399);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
            logHoken($id, $name, $lName, "($x, $y)", $str) if ($value > 0);

	    }
	    elsif($flv == 1) {
	    # 収穫
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = 5;
	    $island->{'money'} -= $value;
	    $str = "$value$HunitMoney";

            $value = 290+ random(30); # 
            $island->{'food'} += $value;
            $str = "$value$HunitFood";
            $gyosenincome += $value;

	    }
	    elsif($flv == 2) {
	    # 収穫
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = 20;
	    $island->{'money'} -= $value;
	    $str = "$value$HunitMoney";

            $value = 490+ random(40); # 
            $island->{'food'} += $value;
            $str = "$value$HunitFood";
            $gyosenincome += $value;

	    }
	    elsif($flv == 3) {
	    # 収穫
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = 300;
	    $island->{'money'} -= $value;
	    $str = "$value$HunitMoney";

		    if(random(1000) < 5) {
		    my($value, $str, $lName);
		    $lName = landName($landKind, $lv);
		    $value = 1+ random(49999);
		    $island->{'money'} += $value;
		    $str = "$value$HunitMoney";
	            # 収入ログ
	            logTansaku($id, $name, $lName, "($x, $y)", $str) if ($value > 0);
		    }
	    }
	    elsif($flv == 4) {
	    # 収穫
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = 150+ random(250);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
            # 収入ログ
            logParkMoneyf($id, $name, $lName, "($x, $y)", $str) if ($value > 0);

            $value = 1000; # 
            $island->{'food'} -= $value;
            $str = "$value$HunitFood";
	    }
	    elsif($flv == 5) {
	    # 収穫
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = 60;
	    $island->{'money'} -= $value;
	    $str = "$value$HunitMoney";

            $value = 690+ random(40); # 
            $island->{'food'} += $value;
            $str = "$value$HunitFood";
            $gyosenincome += $value;

	    }
	    elsif($flv == 6) {
	    # 収穫
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = 30;
	    $island->{'money'} -= $value;
	    $str = "$value$HunitMoney";

            $value = 490+ random(40); # 
            $island->{'food'} += $value;
            $str = "$value$HunitFood";
            $gyosenincome += $value;

	    }
	    elsif($flv == 7) {
	    # 収穫
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = 500;
	    $island->{'money'} -= $value;
	    $str = "$value$HunitMoney";

		    if(random(100) < 1) {
		    my($value, $str, $lName);
		    $lName = landName($landKind, $lv);
		    $value = 1+ random(29999);
		    $island->{'money'} += $value;
		    $str = "$value$HunitMoney";
	            # 収入ログ
	            logTansaku($id, $name, $lName, "($x, $y)", $str) if ($value > 0);
		    }
	    }
	    elsif($flv == 8) {
	    # 収穫
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = 1500+  int($island->{'pop'} / 10) * 1;
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
            # 収入ログ
            logParkMoneyf($id, $name, $lName, "($x, $y)", $str) if ($value > 0);
            $value = 3000; # 
            $island->{'food'} -= $value;
            $str = "$value$HunitFood";
            if(random(100) < 10) {
                # 施設が老朽化したため閉園
                logTitanic($id, $name, $lName, "($x, $y)");
	    $lName = landName($landKind, $lv);
	    $value = int($island->{'pop'} / 10) * 2;
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
            # 収入ログ
            logTitanicEnd($id, $name, $lName, "($x, $y)", $str) if ($value > 0);

                $land->[$x][$y] = $HlandIce;
                $landValue->[$x][$y] = 0;
            }
	    }

	    elsif($flv == 9) {
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = 100;
	    $island->{'money'} -= $value;
	    $str = "$value$HunitMoney";

	    my($i,$sx,$sy);
	    for($i = 0; $i < $HpointNumber; $i++){
		$sx = $Hrpx[$i];
		$sy = $Hrpy[$i];
	    if($land->[$sx][$sy] == $HlandMonster) {
		if($kougekiseigen < 2) {
		# 周囲2Hexに別の怪獣がいる場合、その怪獣を攻撃する

		# 対象となる怪獣の各要素取り出し
		my($tKind, $tName, $tHp) = monsterSpec($landValue->[$sx][$sy]);
		my($tlv) = $landValue->[$sx][$sy];
		my($tspecial) = $HmonsterSpecial[$tKind];

		if((($tspecial == 3) && (($HislandTurn % 2) == 1)) ||
                   (($tspecial == 8) && ((seqnum($HislandTurn) % 2) == 0)) ||
		   (($tspecial == 4) && (($HislandTurn % 2) == 0))) {
		# 対象が硬化中なら効果なし
	    next;
	    }

	    logMonsAttackt($id, $name, $lName, "($x, $y)", $tName, $tPoint);
	    $kougekiseigen++;

	    $tHp--;
	    if($tHp != 0){
	    # 対象の体力を減らす
	    $tlv--;
		$landValue->[$sx][$sy] = $tlv;
	    }else{
	    # 対象の怪獣が倒れて荒地になる
		$land->[$sx][$sy] = $HlandWaste;
		$landValue->[$sx][$sy] = 0;
	    # 報奨金
		my($value) = $HmonsterValue[$tKind];
		   $island->{'money'} += $value;
		   logMsMonMoney($id, $tName, $value);
		}
	    next;
	    }
	    }
	}
	}
	    elsif($flv == 10) {
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = 400;
	    $island->{'money'} -= $value;
	    $str = "$value$HunitMoney";

	    my($i,$sx,$sy);
	    for($i = 0; $i < $HpointNumber; $i++){
		$sx = $Hrpx[$i];
		$sy = $Hrpy[$i];
	    if($land->[$sx][$sy] == $HlandMonster){
		# 周囲2Hexに別の怪獣がいる場合、その怪獣を攻撃する
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = 3000;
	    $island->{'money'} -= $value;
	    $str = "$value$HunitMoney";

		# 対象となる怪獣の各要素取り出し
		my($tKind, $tName, $tHp) = monsterSpec($landValue->[$sx][$sy]);
		my($tlv) = $landValue->[$sx][$sy];
		my($tspecial) = $HmonsterSpecial[$tKind];
		    logFuneAttack($id, $name, $lName, "($x, $y)", $tName, "($sx, $sy)");

		    my($ssx, $ssy, $i, $landKind, $landName, $lv, $point);

		    for($i = 0; $i < 7; $i++) {
			$ssx = $sx + $ax[$i];
			$ssy = $sy + $ay[$i];

			# 行による位置調整
			if((($ssy % 2) == 0) && (($sy % 2) == 1)) {
			    $ssx--;
			}

			$landKind = $land->[$ssx][$ssy];
			$lv = $landValue->[$ssx][$ssy];
			$landName = landName($landKind, $lv);
			$point = "($ssx, $ssy)";

			# 範囲外判定
			if(($ssx < 0) || ($ssx >= $HislandSize) ||
			   ($ssy < 0) || ($ssy >= $HislandSize)) {
			    next;
			}

			# 範囲による分岐
			if($i < 1) {
			    # 中心、および1ヘックス
				$land->[$ssx][$ssy] = $HlandSea;
				$landValue->[$ssx][$ssy] = 1;
				    logFuneMonsterSea($id, $name, $landName, $point);

			} else {
			    # 2ヘックス
			    if(($landKind == $HlandSea) ||
			       ($landKind == $HlandOil) ||
			       ($landKind == $HlandIce) ||
			       ($landKind == $HlandWaste) ||
			       ($landKind == $HlandMountain) ||
			       ($landKind == $HlandGold) ||
			       ($landKind == $HlandOnsen) ||
			       ($landKind == $HlandSeacity) ||
			       ($landKind == $HlandSeatown) ||
			       ($landKind == $HlandUmishuto) ||
			       ($landKind == $HlandUmiamu) ||
			       ($landKind == $HlandFune) ||
			       ($landKind == $HlandFrocity) ||
			       ($landKind == $HlandSbase)) {
				next;
			    } elsif($landKind == $HlandMonster) {
				logWideDamageMonster($id, $name, $landName, $point);
				$land->[$ssx][$ssy] = $HlandWaste;
				$landValue->[$ssx][$ssy] = 0;
			    } else {
				logWideDamageWaste($id, $name, $landName, $point);
				$land->[$ssx][$ssy] = $HlandWaste;
				$landValue->[$ssx][$ssy] = 0;
			    }
			}
		    }

	    next;
	    }
	}
	}
	    elsif($flv == 11) {
	    # 収穫
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = 60;
	    $island->{'money'} -= $value;
	    $str = "$value$HunitMoney";

            $value = 690+ random(40); # 
            $island->{'food'} += $value;
            $str = "$value$HunitFood";
            $gyosenincome += $value;

	    }

	    elsif($flv == 19) {
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = 1000;
	    $island->{'money'} -= $value;
	    $str = "$value$HunitMoney";

	    my($i,$sx,$sy);
	    for($i = 0; $i < $HpointNumber; $i++){
		$sx = $Hrpx[$i];
		$sy = $Hrpy[$i];
	    if($land->[$sx][$sy] == $HlandMonster){
		# 周囲2Hexに別の怪獣がいる場合、その怪獣を攻撃する
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = 50000;
	    $island->{'money'} -= $value;
	    $str = "$value$HunitMoney";

		# 対象となる怪獣の各要素取り出し
		my($tKind, $tName, $tHp) = monsterSpec($landValue->[$sx][$sy]);
		my($tlv) = $landValue->[$sx][$sy];
		my($tspecial) = $HmonsterSpecial[$tKind];
		    logFuneAttackSSS($id, $name, $lName, "($x, $y)", $tName, "($sx, $sy)");
			$land->[$sx][$sy] = $HlandWaste;
			$landValue->[$sx][$sy] = 0;
			$heat++;

		$rena = $island->{'rena'};
		if (rand($rena) > (3000+$heat*1000)) {
		    logFuneAttackSSSR($id, $name, $lName, "($x, $y)", $tName, "($sx, $sy)");
		} else {

		    logFuneAttackSSST($id, $name, $lName, "($x, $y)", $tName, "($sx, $sy)");
		    my($ssx, $ssy, $i, $landKind, $landName, $lv, $point);

		    for($i = 0; $i < 4; $i++) {
			$ssx = $x + $ax[$i];
			$ssy = $y + $ay[$i];

			# 行による位置調整
			if((($ssy % 2) == 0) && (($y % 2) == 1)) {
			    $ssx--;
			}

			$landKind = $land->[$ssx][$ssy];
			$lv = $landValue->[$ssx][$ssy];
			$landName = landName($landKind, $lv);
			$point = "($ssx, $ssy)";

			# 範囲外判定
			if(($ssx < 0) || ($ssx >= $HislandSize) ||
			   ($ssy < 0) || ($ssy >= $HislandSize)) {
			    next;
			}

			# 範囲による分岐
			if($i < 1) {
			    # 中心、および1ヘックス
				$land->[$ssx][$ssy] = $HlandSea;
				$landValue->[$ssx][$ssy] = 0;
			} else {
			    # 2ヘックス
			    if(($landKind == $HlandSea) ||
			       ($landKind == $HlandOil) ||
			       ($landKind == $HlandIce) ||
			       ($landKind == $HlandWaste) ||
			       ($landKind == $HlandMountain) ||
			       ($landKind == $HlandGold) ||
			       ($landKind == $HlandOnsen) ||
			       ($landKind == $HlandSeacity) ||
			       ($landKind == $HlandSeatown) ||
			       ($landKind == $HlandUmishuto) ||
			       ($landKind == $HlandUmiamu) ||
			       ($landKind == $HlandFune) ||
			       ($landKind == $HlandFrocity) ||
			       ($landKind == $HlandSbase)) {
				next;
			    } elsif($landKind == $HlandMonster) {
				logWideDamageMonster($id, $name, $landName, $point);
				$land->[$ssx][$ssy] = $HlandWaste;
				$landValue->[$ssx][$ssy] = 0;
			    } else {
				logWideDamageWaste($id, $name, $landName, $point);
				$land->[$ssx][$ssy] = $HlandWaste;
				$landValue->[$ssx][$ssy] = 0;
			    }
			}
		    }
		}

	    next;
	    }
	}
	}

	    # 動く方向を決定
	    my($d, $sx, $sy);
	    my($i);
	    for($i = 0; $i < 3; $i++) {
		$d = random(6) + 1;
		$sx = $x + $ax[$d];
		$sy = $y + $ay[$d];

		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}

		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}

		# 海、海基、海底都市、油田、怪獣、山、記念碑以外
		if(($land->[$sx][$sy] != $HlandWaste) &&
		   ($land->[$sx][$sy] != $HlandPlains) &&
		   ($land->[$sx][$sy] != $HlandPlains2) &&
		   ($land->[$sx][$sy] != $HlandTown) &&
		   ($land->[$sx][$sy] != $HlandForest) &&
		   ($land->[$sx][$sy] != $HlandFarm) &&
		   ($land->[$sx][$sy] != $HlandEneAt) &&
		   ($land->[$sx][$sy] != $HlandEneFw) &&
		   ($land->[$sx][$sy] != $HlandEneWt) &&
		   ($land->[$sx][$sy] != $HlandEneWd) &&
		   ($land->[$sx][$sy] != $HlandEneBo) &&
		   ($land->[$sx][$sy] != $HlandEneSo) &&
		   ($land->[$sx][$sy] != $HlandEneCs) &&
		   ($land->[$sx][$sy] != $HlandConden) &&
		   ($land->[$sx][$sy] != $HlandConden2) &&
		   ($land->[$sx][$sy] != $HlandConden3) &&
		   ($land->[$sx][$sy] != $HlandConden4) &&
		   ($land->[$sx][$sy] != $HlandFoodim) &&
		   ($land->[$sx][$sy] != $HlandFoodka) &&
		   ($land->[$sx][$sy] != $HlandFarmchi) &&
		   ($land->[$sx][$sy] != $HlandFarmpic) &&
		   ($land->[$sx][$sy] != $HlandFarmcow) &&
		   ($land->[$sx][$sy] != $HlandCollege) &&
		   ($land->[$sx][$sy] != $HlandYakusho) &&
		   ($land->[$sx][$sy] != $HlandFactory) &&
		   ($land->[$sx][$sy] != $HlandHTFactory) &&
		   ($land->[$sx][$sy] != $HlandSHTF) &&
		   ($land->[$sx][$sy] != $HlandOWNF) &&
		   ($land->[$sx][$sy] != $HlandBase) &&
		   ($land->[$sx][$sy] != $HlandDefence) &&
		   ($land->[$sx][$sy] != $HlandMinato) &&
		   ($land->[$sx][$sy] != $HlandSeki) &&
		   ($land->[$sx][$sy] != $HlandPark) &&
		   ($land->[$sx][$sy] != $HlandHaribote) &&
		   ($land->[$sx][$sy] != $HlandSbase) &&
		   ($land->[$sx][$sy] != $HlandSeacity) &&
		   ($land->[$sx][$sy] != $HlandFune) &&
		   ($land->[$sx][$sy] != $HlandIce) &&
		   ($land->[$sx][$sy] != $HlandFrocity) &&
		   ($land->[$sx][$sy] != $HlandUmiamu) &&
		   ($land->[$sx][$sy] != $HlandOil) &&
		   ($land->[$sx][$sy] != $HlandGold) &&
		   ($land->[$sx][$sy] != $HlandMountain) &&
		   ($land->[$sx][$sy] != $HlandOnsen) &&
		   ($land->[$sx][$sy] != $HlandMonument) &&
		   ($land->[$sx][$sy] != $HlandMine) &&
		   ($land->[$sx][$sy] != $HlandNursery) &&
		   ($land->[$sx][$sy] != $HlandKyujo) &&
		   ($land->[$sx][$sy] != $HlandKyujokai) &&
		   ($land->[$sx][$sy] != $HlandZoo) &&
		   ($land->[$sx][$sy] != $HlandRottenSea) &&
		   ($land->[$sx][$sy] != $HlandProcity) &&
		   ($land->[$sx][$sy] != $HlandNewtown) &&
		   ($land->[$sx][$sy] != $HlandBigtown) &&
		   ($land->[$sx][$sy] != $HlandBettown) &&
		   ($land->[$sx][$sy] != $HlandSkycity) &&
		   ($land->[$sx][$sy] != $HlandUmicity) &&
		   ($land->[$sx][$sy] != $HlandSeatown) &&
		   ($land->[$sx][$sy] != $HlandRizort) &&
		   ($land->[$sx][$sy] != $HlandKajino) &&
		   ($land->[$sx][$sy] != $HlandBigRizort) &&
		   ($land->[$sx][$sy] != $HlandShuto) &&
		   ($land->[$sx][$sy] != $HlandUmishuto) &&
		   ($land->[$sx][$sy] != $HlandHouse) &&
		   ($land->[$sx][$sy] != $HlandTaishi) &&
		   ($land->[$sx][$sy] != $HlandTrain) &&
		   ($land->[$sx][$sy] != $HlandKura) &&
		   ($land->[$sx][$sy] != $HlandKuraf) &&
		   ($land->[$sx][$sy] != $HlandMonster)) {
		    last;
		}
	    }

	    if($i == 3) {
		# 動かなかった
		next;
	    }

	    # 動いた先の地形によりメッセージ
	    my($l) = $land->[$sx][$sy];
	    my($lv) = $landValue->[$sx][$sy];
	    my($lName) = landName($l, $lv);
	    my($point) = "($sx, $sy)";

	    # 移動
	    $land->[$sx][$sy] = $land->[$x][$y];
	    $landValue->[$sx][$sy] = $landValue->[$x][$y];

	    # もと居た位置を荒地に
	    $land->[$x][$y] = $HlandSea;
	    $landValue->[$x][$y] = 0;

		if ($flv == 3) { # 油田見っけ
		if (rand(1000) < 30 - $island->{'oil'} * 3)
		{
	        my($l) = $land->[$sx][$sy];
	        my($lv) = $landValue->[$sx][$sy];
	        my($lName) = landName($l, $lv);
	        my($point) = "($x, $y)";
		logTansakuoil($id, $name, $lName, $point);
		$land->[$x][$y] = $HlandOil;
		$landValue->[$x][$y] = 0;
		$island->{'oil'}++;
		}
		}
		elsif ($flv == 7) { # 油田見っけ
		if (rand(1000) < 40 - $island->{'oil'} * 4)
		{
	        my($l) = $land->[$sx][$sy];
	        my($lv) = $landValue->[$sx][$sy];
	        my($lName) = landName($l, $lv);
	        my($point) = "($x, $y)";
		logTansakuoil($id, $name, $lName, $point);
		$land->[$x][$y] = $HlandOil;
		$landValue->[$x][$y] = 0;
		$island->{'oil'}++;
		}
		}

	    # 移動済みフラグ
	    if($funespe == 2) {
		# 移動済みフラグは立てない
	    } elsif($funespe == 1) {
		# 速い怪獣
		$funeMove[$sx][$sy] = $funeMove[$x][$y] + 1;
	    } else {
		# 普通の怪獣
		$funeMove[$sx][$sy] = 2;
	    }

	} elsif($landKind == $HlandMonster) {
	    # 怪獣
	    if($monsterMove[$x][$y] == 2) {
		# すでに動いた後
		next;
	    }

	    # 各要素の取り出し
	    my($mKind, $mName, $mHp) = monsterSpec($landValue->[$x][$y]);
	    my($special) = $HmonsterSpecial[$mKind];

	    if($mKind == 13) {
	    # 幸運
	    my($value, $str, $lName);
	    $lName = landName($landKind, $lv);
	    $value = $HoilMoney+ random(500);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";

            $value = int($island->{'pop'} / 20) + random(11); # 人口５千人ごとに1000トンの食料消費
            $island->{'food'} += $value;
            $str = "$value$HunitFood";

	    }

	    # 硬化中?
	    if((($special == 3) && (($HislandTurn % 2) == 1)) ||
               (($special == 8) && ((seqnum($HislandTurn) % 2) == 0)) ||
	       (($special == 4) && (($HislandTurn % 2) == 0))) {
		# 硬化中
		next;


	    } elsif (($mKind == 16)&&(($HislandTurn % 2) == 0)&&($mHp < 4)&&(rand(1000) < 700)) {
                    logMonsBomb($id, $name, $lName, "($x, $y)", $mName);
		# 広域被害ルーチン
		wideDamage($id, $name, $land, $landValue, $x, $y);
		                if (rand(1000) < 250) {
		                    $land->[$x][$y] = $HlandMonument;
		                    $landValue->[$x][$y] = 78;
		                }

            } elsif ($mKind == 17) {
		my($tx, $ty, $landKind, $lv, $point);
		# 発射
		$tx = random($HislandSize);
		$ty = random($HislandSize);
		$landKind = $land->[$tx][$ty];
		$lv = $landValue->[$tx][$ty];
		$point = "($tx, $ty)";

		if (rand(1000) < 600) {

		      if(($landKind == $HlandSea) ||
			($landKind == $HlandMountain) ||
			($landKind == $HlandGold) ||
			($landKind == $HlandOnsen) ||
			($landKind == $HlandIce) ||
			($landKind == $HlandSeacity) ||
			($landKind == $HlandSeatown) ||
			($landKind == $HlandUmishuto) ||
			($landKind == $HlandUmiamu) ||
			($landKind == $HlandSbase)) {
			logMekaNdamage($id, $name, $mName, "($x, $y)", landName($landKind, $lv), "($tx, $ty)");

			next;
		        }

			$land->[$tx][$ty] = $HlandWaste;
			$landValue->[$tx][$ty] = 1;
			logMekaNmiss($id, $name, $mName, "($x, $y)", landName($landKind, $lv), "($tx, $ty)");


		} elsif (rand(1000) < 400) {
			logMekaSmiss($id, $name, $mName, "($x, $y)", landName($landKind, $lv), "($tx, $ty)");
		    my($ssx, $ssy, $i, $landKind, $landName, $lv, $point);
		    for($i = 0; $i < 7; $i++) {
			$ssx = $tx + $ax[$i];
			$ssy = $ty + $ay[$i];

			# 行による位置調整
			if((($ssy % 2) == 0) && (($ty % 2) == 1)) {
			    $ssx--;
			}

			$landKind = $land->[$ssx][$ssy];
			$lv = $landValue->[$ssx][$ssy];
			$landName = landName($landKind, $lv);
			$point = "($ssx, $ssy)";

			# 範囲外判定
			if(($ssx < 0) || ($ssx >= $HislandSize) ||
			   ($ssy < 0) || ($ssy >= $HislandSize)) {
			    next;
			}

			# 範囲による分岐
			if($i < 1) {
			    # 中心、および1ヘックス
			    if(($landKind == $HlandSea) ||
			       ($landKind == $HlandSeacity) ||
			       ($landKind == $HlandSeatown) ||
			       ($landKind == $HlandUmishuto) ||
			       ($landKind == $HlandUmiamu) ||
			       ($landKind == $HlandSbase)) {
				next;
			       }
				$land->[$ssx][$ssy] = $HlandSea;
				$landValue->[$ssx][$ssy] = 1;
				    logFuneMonsterSea($id, $name, $landName, $point);

			} else {
			    # 2ヘックス
			    if(($landKind == $HlandSea) ||
			       ($landKind == $HlandOil) ||
			       ($landKind == $HlandIce) ||
			       ($landKind == $HlandWaste) ||
			       ($landKind == $HlandMountain) ||
			       ($landKind == $HlandGold) ||
			       ($landKind == $HlandOnsen) ||
			       ($landKind == $HlandSeacity) ||
			       ($landKind == $HlandSeatown) ||
			       ($landKind == $HlandUmishuto) ||
			       ($landKind == $HlandUmiamu) ||
			       ($landKind == $HlandFune) ||
			       ($landKind == $HlandFrocity) ||
			       ($landKind == $HlandSbase)) {
				next;
			    } elsif($landKind == $HlandMonster) {
				logWideDamageMonster($id, $name, $landName, $point);
				$land->[$ssx][$ssy] = $HlandWaste;
				$landValue->[$ssx][$ssy] = 0;
			    } else {
				logWideDamageWaste($id, $name, $landName, $point);
				$land->[$ssx][$ssy] = $HlandWaste;
				$landValue->[$ssx][$ssy] = 0;
			    }
			}
		    }
	        }
		      elsif (rand(1000) < 200) {
			my($sx, $sy, $landKind, $lv, $point);
			# 落下
			$sx = random($HislandSize);
			$sy = random($HislandSize);
			$landKind = $land->[$sx][$sy];
			$lv = $landValue->[$sx][$sy];
			$point = "($sx, $sy)";

			# メッセージ
			logMekaAB($id, $name, $mName, "($x, $y)", landName($landKind, $lv), "($sx, $sy)");

			# 広域被害ルーチン
			wideDamage($id, $name, $land, $landValue, $sx, $sy);
		    }

            } elsif ($mKind == 18) {
		    my($i,$sx,$sy);
		    for($i = 0; $i < $HpointNumber; $i++){
			$sx = $Hrpx[$i];
			$sy = $Hrpy[$i];
		    if($land->[$sx][$sy] == $HlandMonster) {
			# 周囲2Hexに別の怪獣がいる場合、その怪獣を攻撃する

			# 対象となる怪獣の各要素取り出し
			my($tKind, $tName, $tHp) = monsterSpec($landValue->[$sx][$sy]);
			my($tlv) = $landValue->[$sx][$sy];
			my($tspecial) = $HmonsterSpecial[$tKind];

		        if((($tspecial == 3) && (($HislandTurn % 2) == 1)) ||
	                   (($tspecial == 8) && ((seqnum($HislandTurn) % 2) == 0)) ||
			   (($tspecial == 4) && (($HislandTurn % 2) == 0))) {
			# 対象が硬化中なら効果なし
		        next;
		        }
			if (rand(1000) < 600) {
		            if ($tKind == 18) {
			    } elsif(($tKind == 28) ||
				    ($tKind == 30)) {

			    logItiAttackms($id, $name, $mName, "($x, $y)", $tName, $tPoint);
				$dmge = random(4);
				$tHp -= $dmge;
				$tlv -= $dmge;
				$landValue->[$sx][$sy] = $tlv;

				if($tHp < 1){
				# 対象の怪獣が倒れて荒地になる
				$land->[$sx][$sy] = $HlandWaste;
				$landValue->[$sx][$sy] = 0;
				# 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $island->{'money'} += $value;
				    logMsMonMoney($id, $tName, $value);
				}

			    }else{
			    logItiAttack($id, $name, $mName, "($x, $y)", $tName, $tPoint);

			    # 対象の怪獣が倒れて荒地になる
				$land->[$sx][$sy] = $HlandWaste;
				$landValue->[$sx][$sy] = 0;
			    # 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $island->{'money'} += $value;
				   logMsMonMoney($id, $tName, $value);
			    }
			}
		    }
		}
		if (rand(1000) < 600) {
		my($tx, $ty, $landKind, $lv, $point);
		# 発射
		$tx = random($HislandSize);
		$ty = random($HislandSize);
		$landKind = $land->[$tx][$ty];
		$lv = $landValue->[$tx][$ty];
		$point = "($tx, $ty)";

		      if(($landKind == $HlandSea) ||
			($landKind == $HlandMountain) ||
			($landKind == $HlandGold)) {
			next;
		        }

			$land->[$tx][$ty] = $HlandSea;
			$landValue->[$tx][$ty] = 1;
			logUrieruMeteo($id, $name, $mName, "($x, $y)", landName($landKind, $lv), "($tx, $ty)");

		                if (rand(1000) < 100) {
		                    $land->[$tx][$ty] = $HlandMonument;
		                    $landValue->[$tx][$ty] = 79;
		                }

		}


            } elsif ($mKind == 22) {
		    my($i,$sx,$sy);
		    for($i = 0; $i < $HpointNumber; $i++){
			$sx = $Hrpx[$i];
			$sy = $Hrpy[$i];
		    if($land->[$sx][$sy] == $HlandMonster) {
			# 周囲2Hexに別の怪獣がいる場合、その怪獣を攻撃する

			# 対象となる怪獣の各要素取り出し
			my($tKind, $tName, $tHp) = monsterSpec($landValue->[$sx][$sy]);
			my($tlv) = $landValue->[$sx][$sy];
			my($tspecial) = $HmonsterSpecial[$tKind];

		        if((($tspecial == 3) && (($HislandTurn % 2) == 1)) ||
	                   (($tspecial == 8) && ((seqnum($HislandTurn) % 2) == 0)) ||
			   (($tspecial == 4) && (($HislandTurn % 2) == 0))) {
			# 対象が硬化中なら効果なし
		        next;
		        }
			if (rand(1000) < 600) {
		            if ($tKind == 22) {
			    } elsif(($tKind == 28) ||
				    ($tKind == 30)) {

			    logIceAttack($id, $name, $mName, "($x, $y)", $tName, "($sx, $sy)");
				$dmge = random(4);
				$tHp -= $dmge;
				$tlv -= $dmge;
				$landValue->[$sx][$sy] = $tlv;

				if($tHp < 1){
				# 対象の怪獣が倒れて荒地になる
				$land->[$sx][$sy] = $HlandWaste;
				$landValue->[$sx][$sy] = 0;
				# 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $island->{'money'} += $value;
				    logMsMonMoney($id, $tName, $value);
				}
			    }else{
			    logIceAttack($id, $name, $mName, "($x, $y)", $tName, "($sx, $sy)");

			    # 対象の怪獣が倒れて荒地になる
				$land->[$sx][$sy] = $HlandIce;
				$landValue->[$sx][$sy] = 0;

		                if (rand(1000) < 100) {
		                    $land->[$sx][$sy] = $HlandMonument;
		                    $landValue->[$sx][$sy] = 76;
		                }
			    # 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $island->{'money'} += $value;
				   logMsMonMoney($id, $tName, $value);
			    }
			}
		    } elsif(($land->[$sx][$sy] == $HlandBase) ||
			    ($land->[$sx][$sy] == $HlandDefence) ||
			    ($land->[$sx][$sy] == $HlandOil) ||
			    ($land->[$sx][$sy] == $HlandFune)) {
			# 対象となる怪獣の各要素取り出し
			$tKind = $land->[$sx][$sy];
			$tlv = $landValue->[$sx][$sy];

			if (rand(1000) < 200) {
			    logIceAttack($id, $name, $mName, "($x, $y)", landName($tKind, $tlv), "($sx, $sy)");
				$land->[$sx][$sy] = $HlandIce;
				$landValue->[$sx][$sy] = 0;
		                if (rand(1000) < 100) {
		                    $land->[$sx][$sy] = $HlandMonument;
		                    $landValue->[$sx][$sy] = 76;
		                }
			}
		    }
		}


	    } elsif ($mKind == 19) {
	      if (rand(1000) < 333) {
			logMgMeteo($id, $name, $mName, "($x, $y)");
		my($sx, $sy, $landKind, $lv, $point, $first);
		$first = 1;
		while((random(3) == 0) || ($first == 1)) {
		    $first = 0;
		    # 落下
		    $sx = random($HislandSize);
		    $sy = random($HislandSize);
		    $landKind = $land->[$sx][$sy];
		    $lv = $landValue->[$sx][$sy];
		    $point = "($sx, $sy)";

		    if(($landKind == $HlandSea) && ($lv == 0)){
			# 海ポチャ
			logMeteoSea($id, $name, landName($landKind, $lv),
				    $point);
		    } elsif($landKind == $HlandMountain) {
			# 山破壊
			logMeteoMountain($id, $name, landName($landKind, $lv),
					 $point);
			$land->[$sx][$sy] = $HlandWaste;
			$landValue->[$sx][$sy] = 0;
			next;
		    } elsif($landKind == $HlandGold) {
			# 山破壊
			logMeteoMountain($id, $name, landName($landKind, $lv),
					 $point);
			$land->[$sx][$sy] = $HlandWaste;
			$landValue->[$sx][$sy] = 0;
			next;
		    } elsif($landKind == $HlandOnsen) {
			# 山破壊
			logMeteoMountain($id, $name, landName($landKind, $lv),
					 $point);
			$land->[$sx][$sy] = $HlandWaste;
			$landValue->[$sx][$sy] = 0;
			next;
		    } elsif($landKind == $HlandSbase) {
			logMeteoSbase($id, $name, landName($landKind, $lv),
				      $point);
		    } elsif($landKind == $HlandSeacity) {
			logMeteoSbase($id, $name, landName($landKind, $lv),
				      $point);
		    } elsif($landKind == $HlandSeatown) {
			logMeteoSbase($id, $name, landName($landKind, $lv),
				      $point);
		    } elsif($landKind == $HlandUmishuto) {
			logMeteoSbase($id, $name, landName($landKind, $lv),
				      $point);
		    } elsif($landKind == $HlandFune) {
			logMeteoSbase($id, $name, landName($landKind, $lv),
				      $point);
		    } elsif($landKind == $HlandFrocity) {
			logMeteoSbase($id, $name, landName($landKind, $lv),
				      $point);
		    } elsif($landKind == $HlandUmiamu) {
			logMeteoSbase($id, $name, landName($landKind, $lv),
				      $point);
		    } elsif($landKind == $HlandMonster) {
			logMeteoMonster($id, $name, landName($landKind, $lv),
					$point);
		    } elsif($landKind == $HlandSea) {
			# 浅瀬
			logMeteoSea1($id, $name, landName($landKind, $lv),
				     $point);
		    } elsif($landKind == $HlandIce) {
			# 浅瀬
			logMeteoSea1($id, $name, landName($landKind, $lv),
				     $point);
		    } else {
			logMeteoNormal($id, $name, landName($landKind, $lv),
				       $point);
		    }
		    $land->[$sx][$sy] = $HlandSea;
		    $landValue->[$sx][$sy] = 0;
		    }
		}

	      if (rand(1000) < 400) {
			logMgMeteo($id, $name, $mName, "($x, $y)");
		my($sx, $sy, $landKind, $lv, $point);

		# 落下
		$sx = random($HislandSize);
		$sy = random($HislandSize);
		$landKind = $land->[$sx][$sy];
		$lv = $landValue->[$sx][$sy];
		$point = "($sx, $sy)";

		# メッセージ
		logHugeMeteo($id, $name, $point);

		# 広域被害ルーチン
		wideDamage($id, $name, $land, $landValue, $sx, $sy);
	    }

	    if(random(1000) < 450) {
		logMgEarthquake($id, $name, $mName, "($x, $y)");

		# 地震発生
		logEarthquake($id, $name);
		my($sx, $sy, $landKind, $lv, $i);
		for($i = 0; $i < $HpointNumber; $i++) {
		    $sx = $Hrpx[$i];
		    $sy = $Hrpy[$i];
		    $landKind = $land->[$sx][$sy];
		    $lv = $landValue->[$sx][$sy];

		    if((($landKind == $HlandTown) && ($lv >= 100)) ||
		       (($landKind == $HlandFoodim) && ($lv < 480)) ||
		       (($landKind == $HlandProcity) && ($lv < 130)) ||
		       (($landKind == $HlandNewtown) && ($lv < 300)) ||
		       (($landKind == $HlandBigtown) && ($lv < 300)) ||
		       (($landKind == $HlandHTFactory) && ($lv < 500)) ||
		       (($landKind == $HlandSHTF) && ($lv < 500)) ||
		       ($landKind == $HlandRizort) ||
		       ($landKind == $HlandKajino) ||
		       ($landKind == $HlandBigRizort) ||
		       ($landKind == $HlandHaribote) ||
	               ($landKind == $HlandPark) ||
		       ($landKind == $HlandMinato) ||
	               ($landKind == $HlandKyujo) ||
	               ($landKind == $HlandKyujokai) ||
	               ($landKind == $HlandOnsen) ||
		       ($landKind == $HlandFactory)) {
			# 1/4で壊滅
			if(random(4) == 0) {
			    logEQDamage($id, $name, landName($landKind, $lv),
					"($sx, $sy)");
			    $land->[$sx][$sy] = $HlandWaste;
			    $landValue->[$sx][$sy] = 0;
				if ($kind == $HlandOnsen) {
                        	# 金山は山に戻る
                        	$land->[$sx][$sy] = $HlandMountain; # 海になる
                        	$landValue->[$sx][$sy] = 0;
                    		}
			}
		    }

		}
	    }

		    my($i,$sx,$sy);
		    for($i = 0; $i < $HpointNumber; $i++){
			$sx = $Hrpx[$i];
			$sy = $Hrpy[$i];
		    if($land->[$sx][$sy] == $HlandMonster){
			my($tKind, $tName, $tHp) = monsterSpec($landValue->[$sx][$sy]);
			my($tlv) = $landValue->[$sx][$sy];
			my($tspecial) = $HmonsterSpecial[$tKind];
		    if($tKind != 19){
		    if($tHp > $mHp){
			if((($tspecial == 3) && (($HislandTurn % 2) == 1)) ||
	                   (($tspecial == 8) && ((seqnum($HislandTurn) % 2) == 0)) ||
			   (($tspecial == 4) && (($HislandTurn % 2) == 0))) {
		    next;
		    }

		    logMgDrain($id, $name, $mName, $tName, "($x, $y)");


		    $tlv-=($tHp-$mHp);
			$landValue->[$sx][$sy] = $tlv;
		    if($mHp < 9){$lv+=($tHp-$mHp);}
			$landValue->[$x][$y] = $lv;
		    }else{
		    }
		    next;
		    }
		    }
		}


	    } elsif ($mKind == 20) {
	        $lv+=2;
		$landValue->[$x][$y] = $lv;
		if (random(1000) < 200) {
		$island->{'food'} -= int($island->{'food'} / 2);
		logFushoku($id, $name, $mName, "($x, $y)");
            	}
		if ($mHp > 13) {
		logUmlimit($id, $name, $mName, "($x, $y)");
		# 広域被害ルーチン
		wideDamage($id, $name, $land, $landValue, $x, $y);

		my($sx, $sy, $landKind, $lv, $i);
		for($i = 0; $i < $HpointNumber; $i++) {
		    $sx = $Hrpx[$i];
		    $sy = $Hrpy[$i];
		    $landKind = $land->[$sx][$sy];
		    $lv = $landValue->[$sx][$sy];

		    if((($landKind == $HlandTown) && ($lv >= 100)) ||
		       (($landKind == $HlandFoodim) && ($lv < 480)) ||
		       (($landKind == $HlandProcity) && ($lv < 130)) ||
		       ($landKind == $HlandHaribote) ||
	               ($landKind == $HlandPark) ||
		       ($landKind == $HlandMinato) ||
	               ($landKind == $HlandKyujo) ||
	               ($landKind == $HlandKyujokai) ||
		       ($landKind == $HlandBase) ||
		       ($landKind == $HlandFactory)) {
			# 1/6で壊滅
			if(random(6) == 0) {
			    logUmlimitDamage($id, $name, $mName, landName($landKind, $lv),
					"($sx, $sy)");
			    $land->[$sx][$sy] = $HlandWaste;
			    $landValue->[$sx][$sy] = 0;

		                if (rand(1000) < 150) {
		                    $land->[$sx][$sy] = $HlandMonument;
		                    $landValue->[$sx][$sy] = 74;
		                }
			}
		    }
		}
		    $kind = 21;
		    $lv = $lv = ($kind << 4)
			+ $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
		    $land->[$x][$y] = $HlandMonster;
		    $landValue->[$x][$y] = $lv;
            	}


	    } elsif ($mKind == 21) {
		if($mHp < 9){$lv+=3;}
		$landValue->[$x][$y] = $lv;
		if (random(1000) < 150) {
		$island->{'money'} -= int($island->{'money'} / 2);
		logKyoukou($id, $name, $mName, "($x, $y)");
            	}
		if (random(1000) < 200) {
		$island->{'food'} = 0;
		logFushoku($id, $name, $mName, "($x, $y)");
            	}
		    my($i,$sx,$sy);
		    for($i = 0; $i < $HpointNumber; $i++){
			$sx = $Hrpx[$i];
			$sy = $Hrpy[$i];
			 if(($land->[$sx][$sy] == $HlandPlains) ||
			    ($land->[$sx][$sy] == $HlandPlains2) ||
			    ($land->[$sx][$sy] == $HlandForest) ||
			    ($land->[$sx][$sy] == $HlandNursery) ||
			    ($land->[$sx][$sy] == $HlandFarmchi) ||
			    ($land->[$sx][$sy] == $HlandFarmpic) ||
			    ($land->[$sx][$sy] == $HlandFarmcow) ||
			    ($land->[$sx][$sy] == $HlandRottenSea)) {
			# 対象となる怪獣の各要素取り出し
			$tKind = $land->[$sx][$sy];
			$tlv = $landValue->[$sx][$sy];

			if (rand(1000) < 200) {
			    logHellAttack($id, $name, $mName, "($x, $y)", landName($tKind, $tlv), "($sx, $sy)");
				$land->[$sx][$sy] = $HlandWaste;
				$landValue->[$sx][$sy] = 0;
		                if (rand(1000) < 100) {
		                    $land->[$sx][$sy] = $HlandMonument;
		                    $landValue->[$sx][$sy] = 78;
		                }
		                if (rand(1000) < 100) {
		                    $land->[$sx][$sy] = $HlandMonument;
		                    $landValue->[$sx][$sy] = 74;
		                }
			}
		    }
		}

	    } elsif ($mKind == 30) {


	    if($island->{'monsterlive'} - $island->{'c28'} == 0){
		# テトラちゃんだけ？
		if($island->{'co99'} == 0){
			logMstakeiede($id, $name, "出撃中の超神獣テトラ","($sx, $sy)",landName($landKind, $lv));
	        } else {
			my($i,$sx,$sy);
			for($i = 1; $i < $HpointNumber; $i++){
			    $sx = $Hrpx[$i];
			    $sy = $Hrpy[$i];
				$landKind = $land->[$sx][$sy];
				$lv = $landValue->[$sx][$sy];
				$landName = landName($landKind, $lv);
			if(($land->[$sx][$sy] == $HlandCollege) && ($lv == 99)){
			$landValue->[$sx][$sy] = 98;
			logMstakeokaeri($id, $name, "出撃中の超神獣テトラ","($sx, $sy)",landName($landKind, $lv));
		        }
		        }
		}
		    $land->[$x][$y] = $HlandWaste;
		    $landValue->[$x][$y] = 0;
	    }


	    my($i,$sx,$sy);
	    for($i = 1; $i < $HpointNumber; $i++){
		$sx = $Hrpx[$i];
		$sy = $Hrpy[$i];
	    if($land->[$sx][$sy] == $HlandMonster){
		if($msseigen < 1) {
		# 周囲2Hexに別の怪獣がいる場合、その怪獣を攻撃する

		# 対象となる怪獣の各要素取り出し
		my($tKind, $tName, $tHp) = monsterSpec($landValue->[$sx][$sy]);
		my($tlv) = $landValue->[$sx][$sy];
		my($tspecial) = $HmonsterSpecial[$tKind];

		if(($tKind == 30)||($tKind == 23)) {
		} else {

		$eisei5 = $island->{'eisei5'};
		$eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tet) = ($1, $2, $3, $4, $5, $6, $7);

		$attackdamege = random($msap-$tKind);
		$counterdamege = random($tKind-$msdp);
		if($attackdamege < 1){
		$attackdamege = 2;
		}
		if($counterdamege < 1){
		$counterdamege = 1;
		}

		if(rand(5+$tKind) > $mssp){
		$attackdamege = 0;
		}
		if(rand(5+$tKind) < $mssp){
		$counterdamege = 0;
		}

		logMsAttackt($id, $name, "超神獣テトラ", $attackdamege, $counterdamege, $tName, "($sx, $sy)");
		$msseigen++;
		$tHp -= $attackdamege;
		$tlv -= $attackdamege;
		$landValue->[$sx][$sy] = $tlv;
		$mHp -= $counterdamege;
		$lv -= $counterdamege;
		$landValue->[$x][$y] = $lv;

		if($tHp < 1){
		# 対象の怪獣が倒れて荒地になる
		$land->[$sx][$sy] = $HlandWaste;
		$landValue->[$sx][$sy] = 0;
		if($tKind == 13) {
		$land->[$sx][$sy] = $HlandMonument;
		$landValue->[$sx][$sy] = 93;
		logMsAttackmika($id, $name, "超神獣テトラ", $attackdamege, $counterdamege, $tName, $tPoint);
		}
		# 報奨金
		my($value) = $HmonsterValue[$tKind];
		   $island->{'money'} += $value;

		if(rand(1000) < $value) {
		    if(rand(100) < 30) {
		    $msap++;
		    } elsif (rand(100) < 30) {
		    $msdp++;
		    } elsif (rand(100) < 30) {
		    $mssp++;
		    } else {
		    $mshp++;
			if($mshp > 15){
			$mshp = 15;
			}
		    }
		}

		    $msexe += $HmonsterExp[$tKind];
		    $mswin ++;
                                # 怪獣退治数
                                $island->{'taiji'}++;

				# 賞関係
				my($prize) = $island->{'prize'};
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				my($flags) = $1;
				my($monsters) = $2;
				my($turns) = $3;
				my($v) = 2 ** $tKind;
				$monsters |= $v;
				$island->{'prize'} = "$flags,$monsters,$turns";

		    $island->{'eisei5'} = "$mshp,$msap,$msdp,$mssp,$mswin,$msexe,$tet";
		    logMsMonMoney($id, $tName, $value);
		}
		if($mHp < 1){
		# 対象の怪獣が倒れて荒地になる
		$land->[$x][$y] = $HlandWaste;
		$landValue->[$x][$y] = 0;
		# 報奨金
		my($value) = $HmonsterValue[$mKind];
		   $island->{'money'} += $value;
		   logMsMonMoney($id, $mName, $value);
		}
	    }
	    }
	    next;
	    }
	    }



	    } elsif ($mKind == 29) {

	    if($island->{'monsterlive'} == 1){
		# 今テトラちゃんだけ？
		if($island->{'co99'} == 0){
	        } else {
			my($i,$sx,$sy);
			for($i = 1; $i < $HpointNumber; $i++){
			    $sx = $Hrpx[$i];
			    $sy = $Hrpy[$i];
				$landKind = $land->[$sx][$sy];
				$lv = $landValue->[$sx][$sy];
				$landName = landName($landKind, $lv);
			if(($land->[$sx][$sy] == $HlandCollege) && ($lv == 99)){
			$landValue->[$sx][$sy] = 98;
			$land->[$x][$y] = $HlandWaste;
			$landValue->[$x][$y] = 0;
			logMstakeokaeri($id, $name, "テトラ","($sx, $sy)",landName($landKind, $lv));
		        }
		        }
		}
	    }


	    } elsif ($mKind == 28) {

	    if($island->{'monsterlive'} - $island->{'c28'} == 0){
		# マスコットいのらちゃんだけ？
		if($island->{'co99'} == 0){
			logMstakeiede($id, $name, "出撃中のマスコットいのら","($sx, $sy)",landName($landKind, $lv));
	        } else {
			my($i,$sx,$sy);
			for($i = 1; $i < $HpointNumber; $i++){
			    $sx = $Hrpx[$i];
			    $sy = $Hrpy[$i];
				$landKind = $land->[$sx][$sy];
				$lv = $landValue->[$sx][$sy];
				$landName = landName($landKind, $lv);
			if(($land->[$sx][$sy] == $HlandCollege) && ($lv == 99)){
			$landValue->[$sx][$sy] = 4;
			logMstakeokaeri($id, $name, "出撃中のマスコットいのら","($sx, $sy)",landName($landKind, $lv));
		        }
		        }
		}
		    $land->[$x][$y] = $HlandWaste;
		    $landValue->[$x][$y] = 0;
	    }


	    my($i,$sx,$sy);
	    for($i = 1; $i < $HpointNumber; $i++){
		$sx = $Hrpx[$i];
		$sy = $Hrpy[$i];
	    if($land->[$sx][$sy] == $HlandMonster){
		if($msseigen < 1) {
		# 周囲2Hexに別の怪獣がいる場合、その怪獣を攻撃する

		# 対象となる怪獣の各要素取り出し
		my($tKind, $tName, $tHp) = monsterSpec($landValue->[$sx][$sy]);
		my($tlv) = $landValue->[$sx][$sy];
		my($tspecial) = $HmonsterSpecial[$tKind];

		if(($tKind == 28)||($tKind == 23)) {
		} else {

		$eisei5 = $island->{'eisei5'};
		$eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tet) = ($1, $2, $3, $4, $5, $6, $7);

		$attackdamege = random($msap-$tKind);
		$counterdamege = random($tKind-$msdp);
		if($attackdamege < 1){
		$attackdamege = 1;
		}
		if($counterdamege < 1){
		$counterdamege = 1;
		}

		if(rand(5+$tKind) > $mssp){
		$attackdamege = 0;
		}
		if(rand(5+$tKind) < $mssp){
		$counterdamege = 0;
		}

		logMsAttackt($id, $name, "マスコットいのら", $attackdamege, $counterdamege, $tName, "($sx, $sy)");
		$msseigen++;
		$tHp -= $attackdamege;
		$tlv -= $attackdamege;
		$landValue->[$sx][$sy] = $tlv;
		$mHp -= $counterdamege;
		$lv -= $counterdamege;
		$landValue->[$x][$y] = $lv;

		if($tHp < 1){
		# 対象の怪獣が倒れて荒地になる
		$land->[$sx][$sy] = $HlandWaste;
		$landValue->[$sx][$sy] = 0;
		# 報奨金
		my($value) = $HmonsterValue[$tKind];
		   $island->{'money'} += $value;

		if(rand(1000) < $value) {
		    if(rand(100) < 30) {
		    $msap++;
		    } elsif (rand(100) < 30) {
		    $msdp++;
		    } elsif (rand(100) < 30) {
		    $mssp++;
		    } else {
		    $mshp++;
			if($mshp > 15){
			$mshp = 15;
			}
		    }
		}

		    $msexe += $HmonsterExp[$tKind];
		    $mswin ++;
                                # 怪獣退治数
                                $island->{'taiji'}++;

				# 賞関係
				my($prize) = $island->{'prize'};
				$prize =~ /([0-9]*),([0-9]*),(.*)/;
				my($flags) = $1;
				my($monsters) = $2;
				my($turns) = $3;
				my($v) = 2 ** $tKind;
				$monsters |= $v;
				$island->{'prize'} = "$flags,$monsters,$turns";

		    $island->{'eisei5'} = "$mshp,$msap,$msdp,$mssp,$mswin,$msexe,$tet";
		    logMsMonMoney($id, $tName, $value);
		}
		if($mHp < 1){
		# 対象の怪獣が倒れて荒地になる
		$land->[$x][$y] = $HlandWaste;
		$landValue->[$x][$y] = 0;
		# 報奨金
		my($value) = $HmonsterValue[$mKind];
		   $island->{'money'} += $value;
		   logMsMonMoney($id, $mName, $value);
		}
	    }
	    }
	    next;
	    }
	    }



	    } elsif(($special == 6) ||
		  ($mKind == 13)) {
	    my($i,$sx,$sy);
	    for($i = 0; $i < $HpointNumber; $i++){
		$sx = $Hrpx[$i];
		$sy = $Hrpy[$i];
	    if($land->[$sx][$sy] == $HlandMonster){
		if($kougekiseigenm < 2) {
		# 周囲2Hexに別の怪獣がいる場合、その怪獣を攻撃する

		# 対象となる怪獣の各要素取り出し
		my($tKind, $tName, $tHp) = monsterSpec($landValue->[$sx][$sy]);
		my($tlv) = $landValue->[$sx][$sy];
		my($tspecial) = $HmonsterSpecial[$tKind];

	    if($mHp > $tHp){ # 対象より体力が多かった場合
		if((($tspecial == 3) && (($HislandTurn % 2) == 1)) ||
                   (($tspecial == 8) && ((seqnum($HislandTurn) % 2) == 0)) ||
		   (($tspecial == 4) && (($HislandTurn % 2) == 0))) {
		# 対象が硬化中なら効果なし
	    next;
	    }

	    if($mKind == 13) {
	    logMonsAttackt($id, $name, $mName, "($x, $y)", $tName, $tPoint);
	    }else{
	    logMonsAttack($id, $name, $mName, "($x, $y)", $tName, $tPoint);
	    }

	    $kougekiseigenm++;

	    $tHp--;
	    if($tHp != 0){
	    # 対象の体力を減らす
	    $tlv--;
		$landValue->[$sx][$sy] = $tlv;
	    }else{
	    # 対象の怪獣が倒れて荒地になる
		$land->[$sx][$sy] = $HlandWaste;
		$landValue->[$sx][$sy] = 0;
	    # 報奨金
		my($value) = $HmonsterValue[$tKind];
		   $island->{'money'} += $value;
		   logMsMonMoney($id, $tName, $value);
		}
	    # 対象の怪獣の体力を奪って自分の体力を回復
	    if($mHp < 9){$lv++;}
		$landValue->[$x][$y] = $lv;
	    }else{ # 対象より体力が低かった場合
	    # 何もしない
	    }
	    next;
	    }
	    }
	}
	}

	    # 動く方向を決定
	    my($d, $sx, $sy);
	    my($i);
	    for($i = 0; $i < 3; $i++) {
		$d = random(6) + 1;
		$sx = $x + $ax[$d];
		$sy = $y + $ay[$d];

		# 行による位置調整
		if((($sy % 2) == 0) && (($y % 2) == 1)) {
		    $sx--;
		}

		# 範囲外判定
		if(($sx < 0) || ($sx >= $HislandSize) ||
		   ($sy < 0) || ($sy >= $HislandSize)) {
		    next;
		}

		# 海、海基、海底都市、油田、怪獣、山、記念碑以外
		if(($land->[$sx][$sy] != $HlandSea) &&
		   ($land->[$sx][$sy] != $HlandSbase) &&
		   ($land->[$sx][$sy] != $HlandSeacity) &&
		   ($land->[$sx][$sy] != $HlandSeatown) &&
		   ($land->[$sx][$sy] != $HlandBigtown) &&
		   ($land->[$sx][$sy] != $HlandBettown) &&
		   ($land->[$sx][$sy] != $HlandSkycity) &&
		   ($land->[$sx][$sy] != $HlandUmicity) &&
		   ($land->[$sx][$sy] != $HlandShuto) &&
		   ($land->[$sx][$sy] != $HlandUmishuto) &&
		   ($land->[$sx][$sy] != $HlandFune) &&
		   ($land->[$sx][$sy] != $HlandFrocity) &&
		   ($land->[$sx][$sy] != $HlandUmiamu) &&
		   ($land->[$sx][$sy] != $HlandOil) &&
		   ($land->[$sx][$sy] != $HlandZoo) &&
		   ($land->[$sx][$sy] != $HlandNursery) &&
		   ($land->[$sx][$sy] != $HlandBigRizort) &&
		   ($land->[$sx][$sy] != $HlandKajino) &&
		   ($land->[$sx][$sy] != $HlandGold) &&
		   ($land->[$sx][$sy] != $HlandMountain) &&
		   ($land->[$sx][$sy] != $HlandOnsen) &&
		   ($land->[$sx][$sy] != $HlandMonument) &&
		   ($land->[$sx][$sy] != $HlandRottenSea) &&
		   ($land->[$sx][$sy] != $HlandHouse) &&
		   ($land->[$sx][$sy] != $HlandTaishi) &&
		   ($land->[$sx][$sy] != $HlandMonster)) {
		    last;
		}
	    }

	    if($i == 3) {
		# 動かなかった
		next;
	    }

	    if (($mKind == 28) ||
		($mKind == 30)) {
		if($land->[$sx][$sy] != $HlandWaste) {
		    next;
		}
	    }

	    # 動いた先の地形によりメッセージ
	    my($l) = $land->[$sx][$sy];
	    my($lv) = $landValue->[$sx][$sy];
	    my($lName) = landName($l, $lv);
	    my($point) = "($sx, $sy)";

	    # 移動
	    $land->[$sx][$sy] = $land->[$x][$y];
	    $landValue->[$sx][$sy] = $landValue->[$x][$y];

	    # もと居た位置を荒地に
	    $land->[$x][$y] = $HlandWaste;
	    $landValue->[$x][$y] = 0;

		if ($mKind == 11) {
		    if((rand(1000) < 900) &&
		       ($island->{'monsterlive'} < 7)) { # スライムなら９０% の確率で分裂する
		    my($point) = "($x, $y)";
		    $kind = 11;
		    $lv = $lv = ($kind << 4)
			+ $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
		    $land->[$x][$y] = $HlandMonster;
		    $landValue->[$x][$y] = $lv;
		    } elsif((rand(20000) < 400-$island->{'monsterlive'}) &&
		       ($island->{'monsterlive'} > 7)) {
		    my($point) = "($x, $y)";
		    $kind = 11;
		    $lv = $lv = ($kind << 4)
			+ $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
		    $land->[$x][$y] = $HlandMonster;
		    $landValue->[$x][$y] = $lv;
			lognewMonsterBorn($id, $name, $point);
		    }
		}

		if (($mKind == 15) ||
		    ($mKind == 19)) { # スライムなら(いのらを流用)
		if ((rand(1000) < 600) &&
		($island->{'monsterlive'} < 7)) {
		my($point) = "($x, $y)";
		    $kind = random($HmonsterLevel3) + 1;
		    $lv = $lv = ($kind << 4)
			+ $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
		    $land->[$x][$y] = $HlandMonster;
		    $landValue->[$x][$y] = $lv;
		    my($mKind, $mName, $mHp) = monsterSpec($lv);
		if ($mKind == 15) {
			lognewKaiju($id, $name, $mName, $point);
		}else{
		    my($l) = $land->[$sx][$sy];
		    my($lv) = $landValue->[$sx][$sy];
		    my($nName) = landName($l, $lv);
			logShoukan($id, $name, $nName, $mName, $point);
		}
		}
		}

            if ($mKind == 8) { # オームなら　ここから追加
                if (rand(1000) < 400) {
                    # 0.1% の確率で腐海が生まれる
                    my($point) = "($x, $y)";
                    logRottenSeaBorn($id, $name, $point);
                    $land->[$x][$y] = $HlandRottenSea;
                    $landValue->[$x][$y] = 1;
                } elsif (rand(1000) < 200) {
                    # 脱皮
                    my($point) = "($x, $y)";
                    logNuginugi($id, $name, $point);
                    $land->[$x][$y] = $HlandMonument;
                    $landValue->[$x][$y] = 87;
		    $kind = 8;
		    $lv = $lv = ($kind << 4)
			+ $HmonsterBHP[$kind] + random(3);
		    $land->[$sx][$sy] = $HlandMonster;
		    $landValue->[$sx][$sy] = $lv;
                }
            }#ここまで追加

            # 怪獣が周囲を焼き尽くす能力
            if (($special == 7) ||
		($mKind == 16)) {
                my($i, $ssx, $ssy, $kind, $lv);
                for($i = 1; $i < 7; $i++) {
                    $ssx = $sx + $ax[$i];
                    $ssy = $sy + $ay[$i];

                    # 行による位置調整
                    if((($ssy % 2) == 0) && (($sy % 2) == 1)) {
                        $ssx--;
                    }
		    if(($ssx < 0) || ($ssx >= $HislandSize) ||
		       ($ssy < 0) || ($ssy >= $HislandSize)) {
		        # 範囲外
		        next;
		    }

                    $kind = $land->[$ssx][$ssy];
                    $lv   = $landValue->[$ssx][$ssy];

                    if (($kind == $HlandSea) ||
                        ($kind == $HlandSeacity) ||
                        ($kind == $HlandSeatown) ||
                        ($kind == $HlandUmishuto) ||
                        ($kind == $HlandIce) ||
                        ($kind == $HlandWaste) ||
                        ($kind == $HlandUmiamu) ||
                        ($kind == $HlandSbase)) {
                        # 海と海底基地は焼かれない
                        next;
                    } elsif ($kind == $HlandOil) {
                        # 油田は海に戻る
                        $land->[$ssx][$ssy] = $HlandSea; # 海になる
                        $landValue->[$ssx][$ssy] = 0;
                    } elsif ($kind == $HlandFune) {
                        # 油田は海に戻る
                        $land->[$ssx][$ssy] = $HlandSea; # 海になる
                        $landValue->[$ssx][$ssy] = 0;
                    } elsif ($kind == $HlandFrocity) {
                        # 油田は海に戻る
                        $land->[$ssx][$ssy] = $HlandSea; # 海になる
                        $landValue->[$ssx][$ssy] = 0;
                    } elsif ($kind == $HlandNursery) {
                        # 油田は海に戻る
                        $land->[$ssx][$ssy] = $HlandSea; # 海になる
                        $landValue->[$ssx][$ssy] = 1;
	            } elsif ($kind == $HlandGold) {
                        # 金山は山に戻る
                        $land->[$ssx][$ssy] = $HlandMountain; # 海になる
                        $landValue->[$ssx][$ssy] = 0;
	            } elsif ($kind == $HlandOnsen) {
                        # 金山は山に戻る
                        $land->[$ssx][$ssy] = $HlandMountain; # 海になる
                        $landValue->[$ssx][$ssy] = 0;
                    } elsif (($kind == $HlandMountain) && ($lv > 0)) {
                        # 採掘場は山に戻る
                        $landValue->[$ssx][$ssy] = 0; # 採掘場の作業員は壊滅
	            } elsif ($kind == $HlandMonster) {
                        # 怪獣は
			# 対象となる怪獣の各要素取り出し
			my($tKind, $tName, $tHp) = monsterSpec($landValue->[$ssx][$ssy]);
			my($tlv) = $landValue->[$ssx][$ssy];
			my($tspecial) = $HmonsterSpecial[$tKind];
			    if(($tKind == 28) ||
				($tKind == 30)) {
				$dmge = random(4);
				$tHp -= $dmge;
				$tlv -= $dmge;
				$landValue->[$ssx][$ssy] = $tlv;

				if($tHp < 1){
				# 対象の怪獣が倒れて荒地になる
				$land->[$ssx][$ssy] = $HlandWaste;
				$landValue->[$ssx][$ssy] = 0;
				# 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $island->{'money'} += $value;
				    logMsMonMoney($id, $tName, $value);
				}
			    }

                    } else {
                        # 全てが焼き尽くされる
                        $land->[$ssx][$ssy] = $HlandWaste; # 荒れ地になる
                        $landValue->[$ssx][$ssy] = 0;
                    }

                    # ログを作成する
                    logMonsFire($id, $name, landName($kind, $lv), "($ssx, $ssy)", $mName);
                }
            }
            # 怪獣が周囲を焼き尽くす能力
            if (($mKind == 13) ||
		($mKind == 18)) {
                my($i, $ssx, $ssy, $kind, $lv);
                for($i = 1; $i < 19; $i++) {
                    $ssx = $sx + $ax[$i];
                    $ssy = $sy + $ay[$i];

                    # 行による位置調整
                    if((($ssy % 2) == 0) && (($sy % 2) == 1)) {
                        $ssx--;
                    }
		    if(($ssx < 0) || ($ssx >= $HislandSize) ||
		       ($ssy < 0) || ($ssy >= $HislandSize)) {
		        # 範囲外
		        next;
		    }

                    $kind = $land->[$ssx][$ssy];
                    $lv   = $landValue->[$ssx][$ssy];

                    if (($kind == $HlandSea) ||
                        ($kind == $HlandIce) ||
                        ($kind == $HlandSeacity) ||
                        ($kind == $HlandSeatown) ||
                        ($kind == $HlandUmishuto) ||
                        ($kind == $HlandWaste) ||
                        ($kind == $HlandUmiamu) ||
                        ($kind == $HlandSbase)) {
                        # 海と海底基地は焼かれない
                        next;
                    } elsif ($kind == $HlandOil) {
                        # 油田は海に戻る
                        $land->[$ssx][$ssy] = $HlandSea; # 海になる
                        $landValue->[$ssx][$ssy] = 0;
                    } elsif ($kind == $HlandFune) {
                        # 油田は海に戻る
                        $land->[$ssx][$ssy] = $HlandSea; # 海になる
                        $landValue->[$ssx][$ssy] = 0;
                    } elsif ($kind == $HlandFrocity) {
                        # 油田は海に戻る
                        $land->[$ssx][$ssy] = $HlandSea; # 海になる
                        $landValue->[$ssx][$ssy] = 0;
                    } elsif ($kind == $HlandNursery) {
                        # 油田は海に戻る
                        $land->[$ssx][$ssy] = $HlandSea; # 海になる
                        $landValue->[$ssx][$ssy] = 1;
	            } elsif ($kind == $HlandGold) {
                        # 金山は山に戻る
                        $land->[$ssx][$ssy] = $HlandMountain; # 海になる
                        $landValue->[$ssx][$ssy] = 0;
	            } elsif ($kind == $HlandOnsen) {
                        # 金山は山に戻る
                        $land->[$ssx][$ssy] = $HlandMountain; # 海になる
                        $landValue->[$ssx][$ssy] = 0;
                    } elsif (($kind == $HlandMountain) && ($lv > 0)) {
                        # 採掘場は山に戻る
                        $landValue->[$ssx][$ssy] = 0; # 採掘場の作業員は壊滅

	            } elsif ($kind == $HlandMonster) {
                        # 怪獣は
			# 対象となる怪獣の各要素取り出し
			my($tKind, $tName, $tHp) = monsterSpec($landValue->[$ssx][$ssy]);
			my($tlv) = $landValue->[$ssx][$ssy];
			my($tspecial) = $HmonsterSpecial[$tKind];
			    if(($tKind == 28) ||
				($tKind == 30)) {
				$dmge = random(4);
				$tHp -= $dmge;
				$tlv -= $dmge;
				$landValue->[$ssx][$ssy] = $tlv;

				if($tHp < 1){
				# 対象の怪獣が倒れて荒地になる
				$land->[$ssx][$ssy] = $HlandWaste;
				$landValue->[$ssx][$ssy] = 0;
				# 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $island->{'money'} += $value;
				    logMsMonMoney($id, $tName, $value);
				}
			    }

                    } else {
                        # 全てが焼き尽くされる
                        $land->[$ssx][$ssy] = $HlandWaste; # 荒れ地になる
                        $landValue->[$ssx][$ssy] = 0;
                    }

                    # ログを作成する
                    logMonsFire($id, $name, landName($kind, $lv), "($ssx, $ssy)", $mName);
                }
            }


            # フリーズストーム
            if (($special == 9) ||
		($mKind == 22)) {
                my($i, $ssx, $ssy, $kind, $lv);
                for($i = 1; $i < 7; $i++) {
                    $ssx = $sx + $ax[$i];
                    $ssy = $sy + $ay[$i];

                    # 行による位置調整
                    if((($ssy % 2) == 0) && (($sy % 2) == 1)) {
                        $ssx--;
                    }
		    if(($ssx < 0) || ($ssx >= $HislandSize) ||
		       ($ssy < 0) || ($ssy >= $HislandSize)) {
		        # 範囲外
		        next;
		    }

                    $kind = $land->[$ssx][$ssy];
                    $lv   = $landValue->[$ssx][$ssy];

                    if (($kind == $HlandSeacity) ||
                        ($kind == $HlandSeatown) ||
                        ($kind == $HlandUmishuto) ||
                        ($kind == $HlandIce) ||
                        ($kind == $HlandUmiamu) ||
                        ($kind == $HlandSbase)) {
                        # 海と海底基地は焼かれない
                        next;
                    } elsif ($kind == $HlandOil) {
                        # 油田は海に戻る
                        $land->[$ssx][$ssy] = $HlandIce; # 海になる
                        $landValue->[$ssx][$ssy] = 0;
                    } elsif ($kind == $HlandFune) {
                        # 油田は海に戻る
                        $land->[$ssx][$ssy] = $HlandIce; # 海になる
                        $landValue->[$ssx][$ssy] = 0;
                    } elsif ($kind == $HlandFrocity) {
                        # 油田は海に戻る
                        $land->[$ssx][$ssy] = $HlandIce; # 海になる
                        $landValue->[$ssx][$ssy] = 0;
                    } elsif ($kind == $HlandNursery) {
                        # 油田は海に戻る
                        $land->[$ssx][$ssy] = $HlandIce; # 海になる
                        $landValue->[$ssx][$ssy] = 1;
	            } elsif ($kind == $HlandMonster) {
                        # 怪獣は
			# 対象となる怪獣の各要素取り出し
			my($tKind, $tName, $tHp) = monsterSpec($landValue->[$ssx][$ssy]);
			my($tlv) = $landValue->[$ssx][$ssy];
			my($tspecial) = $HmonsterSpecial[$tKind];
			    if(($tKind == 28) ||
				($tKind == 30)) {
				$dmge = random(4);
				$tHp -= $dmge;
				$tlv -= $dmge;
				$landValue->[$ssx][$ssy] = $tlv;

				if($tHp < 1){
				# 対象の怪獣が倒れて荒地になる
				$land->[$ssx][$ssy] = $HlandIce;
				$landValue->[$ssx][$ssy] = 0;
				# 報奨金
				my($value) = $HmonsterValue[$tKind];
				   $island->{'money'} += $value;
				    logMsMonMoney($id, $tName, $value);
				}
			    }
                    } else {
                        # 全てが焼き尽くされる
                        $land->[$ssx][$ssy] = $HlandIce; # 荒れ地になる
                        $landValue->[$ssx][$ssy] = 0;
                    }

                    # ログを作成する
                    logMonsCold($id, $name, landName($kind, $lv), "($ssx, $ssy)", $mName);
                }
            }


            if (($mKind == 14) &&
		($island->{'monsterlive'} < 7)) {
                my($i, $ssx, $ssy, $kind, $lv);
                for($i = 1; $i < 7; $i++) {
                    $ssx = $sx + $ax[$i];
                    $ssy = $sy + $ay[$i];

                    # 行による位置調整
                    if((($ssy % 2) == 0) && (($sy % 2) == 1)) {
                        $ssx--;
                    }
		    if(($ssx < 0) || ($ssx >= $HislandSize) ||
		       ($ssy < 0) || ($ssy >= $HislandSize)) {
		        # 範囲外
		        next;
		    }

                    $kind = $land->[$ssx][$ssy];
                    $lv   = $landValue->[$ssx][$ssy];

                    if (($kind == $HlandSea) ||
                        ($kind == $HlandSeacity) ||
                        ($kind == $HlandSeatown) ||
                        ($kind == $HlandUmishuto) ||
                        ($kind == $HlandOil) ||
                        ($kind == $HlandFune) ||
                        ($kind == $HlandFrocity) ||
                        ($kind == $HlandNursery) ||
                        ($kind == $HlandUmiamu) ||
                        ($kind == $HlandMountain) ||
                        ($kind == $HlandGold) ||
                        ($kind == $HlandOnsen) ||
                        ($kind == $HlandMonster) ||
                        ($kind == $HlandSbase)) {
                        # 海と海底基地は焼かれない
                        next;
                    } else {
                        # 全てが焼き尽くされる
		    $kind = 11;
		    $lv = $lv = ($kind << 4)
			+ $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);
		    $land->[$ssx][$ssy] = $HlandMonster;
		    $landValue->[$ssx][$ssy] = $lv;
                    }
		                if (rand(1000) < 50) {
		                    $land->[$ssx][$ssy] = $HlandMonument;
		                    $landValue->[$ssx][$ssy] = 77;
		                }
                    # ログを作成する
		    lognewMonsterBorn($id, $name, "($ssx, $ssy)");
                }
            }

	    # 移動済みフラグ
	    if($HmonsterSpecial[$mKind] == 2) {
		# 移動済みフラグは立てない
	    } elsif($HmonsterSpecial[$mKind] == 1) {
		# 速い怪獣
		$monsterMove[$sx][$sy] = $monsterMove[$x][$y] + 1;
	    } else {
		# 普通の怪獣
		$monsterMove[$sx][$sy] = 2;
	    }

	    if(($l == $HlandDefence) && ($HdBaseAuto == 1)) {
		# 防衛施設を踏んだ
		logMonsMoveDefence($id, $name, $lName, $point, $mName);

		# 広域被害ルーチン
		wideDamage($id, $name, $land, $landValue, $sx, $sy);
            } elsif ($l == $HlandMine) {
                # 地雷を踏んだ
                if ($mHp < $lv) {
                    # 死亡して死体が飛び散った
                    logMonsMineKill($id, $name, $lName, $point, $mName);
                } elsif ($mHp == $lv) {
                    # 死亡して死体が残った
                    logMonsMineDead($id, $name, $lName, $point, $mName);

                    # 収入
                    my($value) = $HmonsterValue[$mKind];
                    if($value > 0) {
                        $island->{'money'} += $value;
                        logMsMonMoney($id, $mName, $value);
                    }

                                # 怪獣退治数
                                $island->{'taiji'}++;

                    # 賞関係
                    my($prize) = $island->{'prize'};
                    $prize =~ /([0-9]*),([0-9]*),(.*)/;
                    my($flags) = $1;
                    my($monsters) = $2;
                    my($turns) = $3;
                    my($v) = 2 ** $mKind;
                    $monsters |= $v;
                    $island->{'prize'} = "$flags,$monsters,$turns";
                } else {
                    # 生き残った
                    logMonsMineHit($id, $name, $lName, $point, $mName);
                    $landValue->[$sx][$sy] -= $lv;
                    next;
                }

                # 怪獣は荒地に
                $land->[$sx][$sy] = $HlandWaste;
                $landValue->[$sx][$sy] = 1;
	    } else {
		# 行き先が荒地になる
                    if ($l == $HlandWaste) {
                    } else {
		    logMonsMove($id, $name, $lName, $point, $mName);
                    }
	    }
	}

	if(($landKind == $HlandConden4) && ($lv == 99)) {
	    my($l) = $land->[$x][$y];
	    my($lv) = $landValue->[$x][$y];
	    my($point) = "($x, $y)";
	    my($lName) = landName($l, $lv);
	    $etc9 = $island->{'etc9'};
	    $etc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($co7, $magicf, $magici, $magica, $magicw, $magicl, $magicd) = ($1, $2, $3, $4, $5, $6, $7);

	    if($magica != $magicl) {
	    logRouden2($id, $name, $lName, $point);

		    my($sx, $sy, $i, $landKind, $landName, $lv, $point);

		    my($yh) = 19;
			# 範囲外判定
			if($s02 >= 25) {
			    $yh = 7;
			}

		    for($i = 1; $i < $yh; $i++) {
			$sx = $x + $ax[$i];
			$sy = $y + $ay[$i];

			# 行による位置調整
			if((($sy % 2) == 0) && (($y % 2) == 1)) {
			    $sx--;
			}

			$landKind = $land->[$sx][$sy];
			$lv = $landValue->[$sx][$sy];
			$landName = landName($landKind, $lv);
			$point = "($sx, $sy)";

			# 範囲外判定
			if(($sx < 0) || ($sx >= $HislandSize) ||
			   ($sy < 0) || ($sy >= $HislandSize)) {
			    next;
			}

			# 範囲による分岐
			if($i < 7) {
			    # 中心、および1ヘックス
			    if($landKind == $HlandSea) {
				$landValue->[$sx][$sy] = 0;
				next;
			    } elsif(($landKind == $HlandSbase) ||
				    ($landKind == $HlandSeacity) ||
				    ($landKind == $HlandSeatown) ||
				    ($landKind == $HlandUmishuto) ||
				    ($landKind == $HlandFune) ||
				    ($landKind == $HlandIce) ||
				    ($landKind == $HlandFrocity) ||
				    ($landKind == $HlandUmiamu) ||
				    ($landKind == $HlandOil)) {
				logWideDamageSea2($id, $name, $landName, $point);
				$land->[$sx][$sy] = $HlandSea;
				$landValue->[$sx][$sy] = 0;
			    } else {

				    logBariaAttack($id, $name, $landName, $point);

				$land->[$sx][$sy] = $HlandSea;
				if($i == 0) {
				    # 海
				    $landValue->[$sx][$sy] = 0;
				} else {
				    # 浅瀬
				    $landValue->[$sx][$sy] = 1;
				}
			    }
			} else {
			    # 2ヘックス
			    if(($landKind == $HlandSea) ||
			       ($landKind == $HlandIce) ||
			       ($landKind == $HlandOil) ||
			       ($landKind == $HlandWaste) ||
			       ($landKind == $HlandMountain) ||
			       ($landKind == $HlandGold) ||
			       ($landKind == $HlandOnsen) ||
			       ($landKind == $HlandSeacity) ||
			       ($landKind == $HlandUmishuto) ||
			       ($landKind == $HlandSeatown) ||
			       ($landKind == $HlandFune) ||
			       ($landKind == $HlandFrocity) ||
			       ($landKind == $HlandUmiamu) ||
			       ($landKind == $HlandSbase)) {
				next;
			    } else {
				logBariaAttack($id, $name, $landName, $point);
				$land->[$sx][$sy] = $HlandWaste;
				$landValue->[$sx][$sy] = 0;
			    }
			}
		    }

	    }
	}

	if((($landKind == $HlandConden2) || ($landKind == $HlandConden3)) && ($island->{'roudenflag'} == 0)) {
	    my($l) = $land->[$x][$y];
	    my($lv) = $landValue->[$x][$y];
	    my($point) = "($x, $y)";
	    my($lName) = landName($l, $lv);

	    if(random(150000) < 125+$island->{'co8'}/2.5) {
	    logRouden($id, $name, $lName, $point);
	    $land->[$x][$y] = $HlandConden4;
	    $island->{'roudenflag'}++;

		if($landKind == $HlandConden2) {
		$landValue->[$x][$y] = 2;
		}
		if($landKind == $HlandConden3) {
		$landValue->[$x][$y] = 3;
		}
	    }
	}

	if((($landKind == $HlandConden2) || ($landKind == $HlandConden3) || (($landKind == $HlandCollege) && ($lv == 8))) && ($island->{'roudenflag'} == 0)) {
	    my($l) = $land->[$x][$y];
	    my($lv) = $landValue->[$x][$y];
	    my($point) = "($x, $y)";
	    my($lName) = landName($l, $lv);
	# 中型隕石判定

	if((random(333333) < 100+$island->{'co8'}/3) && ($island->{'ene'} > 5000000)) {

	    my($i, $count, $sx, $sy);
	    $count = 0;
	    for($i = 0; $i < 7; $i++) {
		 $sx = $x + $ax[$i];
		 $sy = $y + $ay[$i];

		 # 行による位置調整
		 if((($sy % 2) == 0) && (($y % 2) == 1)) {
		     $sx--;
		 }

		 if(($sx < 0) || ($sx >= $HislandSize) ||
		    ($sy < 0) || ($sy >= $HislandSize)) {
		     # 範囲外の場合
		     if($kind == $HlandSea) {
			 # 海なら加算
			 $count++;
		     }
		 } else {
		     # 範囲内の場合
		     if(($land->[$sx][$sy] == $HlandDefence) && ($landValue->[$sx][$sy] == 77)) {
			logTrainEnd2($id, $name, "防衛施設・改", "($sx, $sy)");
			$land->[$sx][$sy] = $HlandWaste;
			$landValue->[$sx][$sy] = 0;
			 $count++;
		     }
		 }
	    }

	        if(($count > 0) && ($island->{'eis5'} >= 1)) {

		logMidMeteo2($id, $name, $point);
		$island->{'roudenflag'}++;
		$island->{'eis5'} -= random(50);
		        if($island->{'eis5'} < 1) {
		           $island->{'eis5'} = 0;
				logEiseiEnd($id, $name, "防衛衛星");
		        }

		} else {

		logMidMeteo($id, $name, $point);
		$island->{'roudenflag'}++;

		    for($i = 0; $i < 7; $i++) {
			$sx = $x + $ax[$i];
			$sy = $y + $ay[$i];

			# 行による位置調整
			if((($sy % 2) == 0) && (($y % 2) == 1)) {
			    $sx--;
			}

			$landKind = $land->[$sx][$sy];
			$lv = $landValue->[$sx][$sy];
			$landName = landName($landKind, $lv);
			$point = "($sx, $sy)";

			# 範囲外判定
			if(($sx < 0) || ($sx >= $HislandSize) ||
			   ($sy < 0) || ($sy >= $HislandSize)) {
			    next;
			}

			# 範囲による分岐
			if($i < 1) {
			    if($landKind == $HlandSea) {
				$landValue->[$sx][$sy] = 0;
				next;
			    } elsif(($landKind == $HlandSbase) ||
				    ($landKind == $HlandSeacity) ||
				    ($landKind == $HlandSeatown) ||
				    ($landKind == $HlandUmishuto) ||
				    ($landKind == $HlandFune) ||
				    ($landKind == $HlandIce) ||
				    ($landKind == $HlandFrocity) ||
				    ($landKind == $HlandUmiamu) ||
				    ($landKind == $HlandOil)) {
				logWideDamageSea2($id, $name, $landName, $point);
				$land->[$sx][$sy] = $HlandSea;
				$landValue->[$sx][$sy] = 1;
			    }
			    # 中心、および1ヘックス
				logWideDamageSea($id, $name, $landName, $point);
				$land->[$sx][$sy] = $HlandSea;
				$landValue->[$sx][$sy] = 1;
			    } else {
			    if(($landKind == $HlandSea) ||
				    ($landKind == $HlandSbase) ||
				    ($landKind == $HlandSeacity) ||
				    ($landKind == $HlandSeatown) ||
				    ($landKind == $HlandUmishuto) ||
				    ($landKind == $HlandFune) ||
				    ($landKind == $HlandIce) ||
				    ($landKind == $HlandFrocity) ||
				    ($landKind == $HlandUmiamu) ||
				    ($landKind == $HlandWaste) ||
				    ($landKind == $HlandOil)) {
				next;
			    }
				if(random(100) < 40) {
				logWideDamageWaste($id, $name, $landName, $point);
				$land->[$sx][$sy] = $HlandWaste;
				$landValue->[$sx][$sy] = 0;
				}
			    }
		    }
		}
	    }
	}

	# 火災判定
	if((($landKind == $HlandTown) && ($lv > 30)) ||
	   ($landKind == $HlandHaribote) ||
	   ($landKind == $HlandMinato) ||
	   ($landKind == $HlandFoodim) ||
	   ($landKind == $HlandFoodka) ||
	   ($landKind == $HlandOnsen) ||
	   ($landKind == $HlandKura) ||
	   ($landKind == $HlandKuraf) ||
	   ($landKind == $HlandHTFactory) ||
	   ($landKind == $HlandSHTF) ||
	   ($landKind == $HlandFactory)) {
	    if(random(1000) < $HdisFire-int($island->{'eis1'}/20)) {
		# 周囲の森と記念碑を数える
		if((countAround($land, $x, $y, $HlandForest, 7) +
		    countAround($land, $x, $y, $HlandProcity, 7) +
		    countAround($land, $x, $y, $HlandHouse, 7) +
		    countAround($land, $x, $y, $HlandTaishi, 7) +
		    countAround($land, $x, $y, $HlandMonument, 7)) == 0) {
		    # 無かった場合、火災で壊滅
		    my($l) = $land->[$x][$y];
		    my($lv) = $landValue->[$x][$y];
		    my($point) = "($x, $y)";
		    my($lName) = landName($l, $lv);
		    logFire($id, $name, $lName, $point);
		    $land->[$x][$y] = $HlandWaste;
		    $landValue->[$x][$y] = 0;
				if ($kind == $HlandOnsen) {
                        	# 金山は山に戻る
                        	$land->[$x][$y] = $HlandMountain; # 海になる
                        	$landValue->[$x][$y] = 0;
                    		}
		}
	    }
	} 

	# 火災判定2
	if(($landKind == $HlandNewtown) ||
	   ($landKind == $HlandRizort) ||
	   ($landKind == $HlandKajino) ||
	   ($landKind == $HlandBigRizort) ||
	   ($landKind == $HlandBettown) ||
	   ($landKind == $HlandSkycity) ||
	   ($landKind == $HlandUmicity) ||
	   ($landKind == $HlandBigtown)) {
	    if(random(750) < $HdisFire-int($island->{'eis1'}/20)) {
		# 周囲の森と記念碑を数える
		if((countAround($land, $x, $y, $HlandForest, 7) +
		    countAround($land, $x, $y, $HlandProcity, 7) +
		    countAround($land, $x, $y, $HlandHouse, 7) +
		    countAround($land, $x, $y, $HlandTaishi, 7) +
		    countAround($land, $x, $y, $HlandMonument, 7)) == 0) {
		    # 無かった場合、火災で壊滅
		    my($l) = $land->[$x][$y];
		    my($lv) = $landValue->[$x][$y];
		    my($point) = "($x, $y)";
		    my($lName) = landName($l, $lv);
		    logFirenot($id, $name, $lName, $point);
	            $landValue->[$x][$y] -= random(100)+50;
		}
			if($landValue->[$x][$y] <= 0) {
			    # 平地に戻す
			    my($l) = $land->[$x][$y];
			    my($lv) = $landValue->[$x][$y];
			    my($point) = "($x, $y)";
			    my($lName) = landName($l, $lv);
			    $land->[$x][$y] = $HlandWaste;
			    $landValue->[$x][$y] = 0;
		    	    logFire($id, $name, $lName, $point);
			    next;
			}
	    }
	} 
    }

    if ($rizortincome > 0) {
    logParkMoney($id, $name, "$rizortincome$HunitMoney", $island->{'riz'},"リゾート施設");
    }

    if ($m84income > 0) {
    logParkMoney($id, $name, "$m84income$HunitMoney", $island->{'m84'},"古代遺跡");
    }

    if ($island->{'par'} > 0) {
    logParkMoney($id, $name, "$parkincome$HunitMoney", $island->{'par'},"遊園地");
    }

    if ($island->{'oil'} > 0) {
    logParkMoney($id, $name, "$oilincome$HunitMoney", $island->{'oil'},"油田");
    }

    if ($island->{'gyo'} > 0) {
    logParkMoney($id, $name, "$gyosenincome$HunitFood", $island->{'gyo'},"漁船");
    }

    if ($island->{'trainmoney'} > 0) {
    logParkMoney($id, $name, "$island->{'trainmoney'}$HunitMoney", $island->{'tra1'},"普通電車");
    }
    if ($island->{'trainmoney2'} > 0) {
    logParkMoney($id, $name, "$island->{'trainmoney2'}$HunitMoney", $island->{'tra2'},"貨物列車");
    }

}


# 周囲の町、農場があるか判定
sub countGrow {
    my($land, $landValue, $x, $y) = @_;
    my($i, $sx, $sy);
    for($i = 1; $i < 7; $i++) {
	 $sx = $x + $ax[$i];
	 $sy = $y + $ay[$i];

	 # 行による位置調整
	 if((($sy % 2) == 0) && (($y % 2) == 1)) {
	     $sx--;
	 }

	 if(($sx < 0) || ($sx >= $HislandSize) ||
	    ($sy < 0) || ($sy >= $HislandSize)) {
	 } else {
	     # 範囲内の場合
	     if(($land->[$sx][$sy] == $HlandTown) ||
		($land->[$sx][$sy] == $HlandProcity) ||
		($land->[$sx][$sy] == $HlandNewtown) ||
		($land->[$sx][$sy] == $HlandRizort) ||
		($land->[$sx][$sy] == $HlandKajino) ||
		($land->[$sx][$sy] == $HlandBigRizort) ||
		($land->[$sx][$sy] == $HlandBettown) ||
		($land->[$sx][$sy] == $HlandSkycity) ||
		($land->[$sx][$sy] == $HlandUmicity) ||
		($land->[$sx][$sy] == $HlandBigtown) ||
		($land->[$sx][$sy] == $HlandFarm)) {
		 if($landValue->[$sx][$sy] != 1) {
		     return 1;
		 }
	     }
	 }
    }
    return 0;
}


# 失業者はどこへ？
sub doIslandunemployed {
    my($number, $island) = @_;

    # 導出値
    my($name) = $island->{'name'};
    my($id) = $island->{'id'};
    my($land) = $island->{'land'};
    my($landValue) = $island->{'landValue'};

    # 失業者の移民
    if(($island->{'unemployed'} >= 100) && (rand(100) < 25)) {
        # 失業者が１万人以上いると 25% の確率で移民を希望する

        my(@order) = randomArray($HislandNumber);
        my($migrate);

        # 移民先を探す
        my($tIsland);
        my($n) = min($HislandNumber, 5);
        my($i);
        for($i = 0; $i < $n; $i++) { # ５島まで調べる
            $tIsland = $Hislands[$order[$i]];

            # 仕事のある島に移民する
            if ($tIsland->{'unemployed'} < 0) {
                $migrate = min($island->{'unemployed'}, -$tIsland->{'unemployed'});
		$migrate2 = $migrate;
                last;
            }
        }

        if ($i >= $n) {
            # 移民先が見つからなければ、暴動かデモ行進

            $migrate = random($island->{'unemployed'} - 100) + 100;
            $n = 0;
            my($x, $y, $landKind, $lv);
            for($i = 0; $i < $HpointNumber; $i++) {
                $x = $Hrpx[$i];
                $y = $Hrpy[$i];
                $landKind = $land->[$x][$y];
                $lv = $landValue->[$x][$y];

                if(($landKind == $HlandFarm) ||
                   ($landKind == $HlandFactory) ||
                   ($landKind == $HlandHTFactory) ||
                   ($landKind == $HlandSHTF) ||
                   ($landKind == $HlandOWNF) ||
                   ($landKind == $HlandFarmchi) ||
                   ($landKind == $HlandFarmpic) ||
                   ($landKind == $HlandFarmcow) ||
                   ($landKind == $HlandEneAt) ||
                   ($landKind == $HlandEneFw) ||
                   ($landKind == $HlandEneWt) ||
                   ($landKind == $HlandEneWd) ||
                   ($landKind == $HlandEneBo) ||
                   ($landKind == $HlandEneSo) ||
                   ($landKind == $HlandEneCs) ||
                   ($landKind == $HlandCollege) ||
                   ($landKind == $HlandYakusho) ||
                   ($landKind == $HlandBase) ||
		   ($landKind == $HlandFoodim) ||
		   ($landKind == $HlandFoodka) ||
	           ($landKind == $HlandNursery) ||
	           ($landKind == $HlandMine) ||
                   ($landKind == $HlandPark) ||
                   ($landKind == $HlandKyujo) ||
                   ($landKind == $HlandKyujokai) ||
                   ($landKind == $HlandZoo) ||
                   ($landKind == $HlandKura) ||
                   ($landKind == $HlandKuraf) ||
                   ($landKind == $HlandDefence)) {
                    # 25% の確率で壊滅
                    if(rand(100) < 25) {
                        $n++;
                        logUnemployedRiot($id, $name, landName($landKind, $lv), $migrate2, "($x, $y)");
                        $land->[$x][$y] = $HlandWaste;
                        $landValue->[$x][$y] = 0;
                    }
                }
            }

            # 何も壊さないときはデモ行進を行う
            logUnemployedDemo($id, $name, $migrate2) if ($n == 0);

        } else {
            # 移民先が見つかったので移民
            my($tLand) = $tIsland->{'land'};
            my($tLandValue) = $tIsland->{'landValue'};

            my($employed) = $migrate;
            my($x, $y, $landKind, $lv);
            for($i = 0; $i < $HpointNumber; $i++) {
                $x = $Hrpx[$i];
                $y = $Hrpy[$i];
                $landKind = $tLand->[$x][$y];
                $lv = $tLandValue->[$x][$y];

	        if($landKind == $HlandSeki) {
                   logUnemployedReturn($id, $tIsland->{'id'}, $name, landName($landKind, $lv), $tIsland->{'name'}, $migrate2);
		 return 1;
		 }
	    }

            # 移民先の町に家を用意する
            my($employed) = $migrate;
            my($x, $y, $landKind, $lv);
            for($i = 0; $i < $HpointNumber; $i++) {
                $x = $Hrpx[$i];
                $y = $Hrpy[$i];
                $landKind = $tLand->[$x][$y];
                $lv = $tLandValue->[$x][$y];

                if(($landKind == $HlandTown) ||
                   ($landKind == $HlandMinato) ||
                   ($landKind == $HlandNewtown) ||
                   ($landKind == $HlandFrocity) ||
                   ($landKind == $HlandOnsen) ||
                   ($landKind == $HlandSeacity)) {
                    # 町
                    $n = int((255 - $lv) / 2);
                    $n = min(int($n + rand($n)), $employed);
                    $employed -= $n;
                    $tLandValue->[$x][$y] += $n;
                } elsif ($landKind == $HlandPlains) {
                    # 平地
                    $n = int((255 - $lv) / 2);
                    $n = min(int($n + rand($n)), $employed);
                    $employed -= $n;
                    $tLand->[$x][$y] = $HlandTown;
                    $tLandValue->[$x][$y] = $n;
                }

                last if ($employed <= 0);
            }
            $migrate -= $employed;
            $island->{'unemployed'} -= $migrate;
            $tIsland->{'unemployed'} += $migrate;
            $island->{'pop'} -= $migrate;
            $tIsland->{'pop'} += $migrate;

            # 今まで住んでいた家を処分する
            $employed = $migrate;
            for($i = 0; $i < $HpointNumber; $i++) {
                $x = $Hrpx[$i];
                $y = $Hrpy[$i];
                $landKind = $land->[$x][$y];
                $lv = $landValue->[$x][$y];

                if((($landKind == $HlandTown) && ($lv > 1)) ||
		  (($landKind == $HlandMinato) && ($lv > 1)) ||
		  (($landKind == $HlandProcity) && ($lv > 1)) ||
		  (($landKind == $HlandFrocity) && ($lv > 1)) ||
		  (($landKind == $HlandNewtown) && ($lv > 1)) ||
		  (($landKind == $HlandBigtown) && ($lv > 1)) ||
		  (($landKind == $HlandBettown) && ($lv > 1)) ||
		  (($landKind == $HlandSkycity) && ($lv > 1)) ||
		  (($landKind == $HlandUmicity) && ($lv > 1)) ||
		  (($landKind == $HlandSeatown) && ($lv > 1)) ||
		  (($landKind == $HlandShuto) && ($lv > 1)) ||
		  (($landKind == $HlandUmishuto) && ($lv > 1)) ||
		  (($landKind == $HlandOnsen) && ($lv > 1)) ||
		  (($landKind == $HlandSeacity) && ($lv > 1))) {
                    # 町
                    $n = min($lv - 1, $employed);
                    $landValue->[$x][$y] -= $n;
                    $employed -= $n;

			if($landValue->[$x][$y] <= 0) {
			    $land->[$x][$y] = $HlandPlains;
			    $landValue->[$x][$y] = 0;
			}

                }
            }

            logUnemployedMigrate($id, $tIsland->{'id'}, $name, $tIsland->{'name'}, $migrate2);
        }
    }
}

# 島全体
sub doIslandProcess {
    my($number, $island) = @_;

    # 導出値
    my($name) = $island->{'name'};
    my($id) = $island->{'id'};
    my($land) = $island->{'land'};
    my($landValue) = $island->{'landValue'};


    $etc5 = $island->{'etc5'};
    $etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);


    $etc7 = $island->{'etc7'};
    $etc7 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
    ($msjotai, $nokotan, $msid) = ($1, $2, $3);
	$nokotan -= 1;
	$island->{'etc7'} = "$msjotai,$nokotan,$msid";
	if ($nokotan < 1) {
	    $island->{'etc7'} = '0,0,0';
	}

    if ($island->{'stsankahantei'} == 1) {
	$value = $stsanka*random(2000);
	$island->{'money'} += $value;
	$str = "$value$HunitMoney";
	logHCstart($id, $name, $str);
    }


    if ($island->{'htf'} > 0) {
	    if($anothermood == 1) {
		$pika2 = int($island->{'amarimoney'}/2)
	    } else {
		$pika2 = int($island->{'pika'}/2);
	    }
	if ($pika2 < 0) {
	    $pika2 = 0;
	}
	$island->{'money'} -= $pika2;
    }

    elsif ($island->{'shtf'} > 0) {
	    if($anothermood == 1) {
		$pika2 = int($island->{'amarimoney'}/5)
	    } else {
		$pika2 = int($island->{'pika'}/5);
	    }
	if ($pika2 < 0) {
	    $pika2 = 0;
	}
	$island->{'money'} -= $pika2;
    }

    if(($HislandTurn % 100) == 0) {
	$island->{'ip8'} = 0;
    }

	$etc8 = $island->{'etc8'};
	$etc8 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($toto1, $toto2, $toto3, $toto4, $toto5, $toto6, $toto7) = ($1, $2, $3, $4, $5, $6, $7);


        # リゾート飽きられました
    if(($island->{'riz'} > 0) && (rand(40) > $s06) && (rand(500+$s06*2) < 15)) {

        my(@order) = randomArray($HislandNumber);
        my($migrate);

        # 移民先を探す
        my($tIsland);
        my($n) = min($HislandNumber, 5);
        my($i);
        for($i = 0; $i < $n; $i++) { # ５島まで調べる
            $tIsland = $Hislands[$order[$i]];

	    $tetc5 = $tIsland->{'etc5'};
	    $tetc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($ts00,$ts01,$ts02,$ts03,$ts04,$ts05,$ts06,$ts07,$ts08,$ts09,$ts10,$ts11,$ts12,$ts13,$ts14,$ts15,$ts16,$ts17,$ts18,$ts19,$ts20,$ts21,$ts22,$ts23,$ts24,$ts25,$ts26,$ts27,$ts28,$ts29,$ts30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
	    $ts06b = int($ts06/5);

            # 仕事のある島に移民する
            if (($island->{'pop'} > $tIsland->{'pop'}) && ($tIsland->{'riz'} > 0) && ($s06 <= $ts06) && ($island->{'id'} != $tIsland->{'id'})) {
                $migrate = ($ts06 - $s06 + 1) * (random(5) + 1);
		        if ($migrate <= 0) {
			    $migrate = 1;
		        }
		$migrate2 = $migrate;
                last;
            }
        }

        if ($i >= $n) {

        } else {
            # 移民先が見つかったので移民
            my($tLand) = $tIsland->{'land'};
            my($tLandValue) = $tIsland->{'landValue'};
            my($employed) = $migrate;

            # 移民先の町に家を用意する
            my($employed) = $migrate;
            my($x, $y, $landKind, $lv);
            for($i = 0; $i < $HpointNumber; $i++) {
                $x = $Hrpx[$i];
                $y = $Hrpy[$i];
                $landKind = $tLand->[$x][$y];
                $lv = $tLandValue->[$x][$y];

                if($landKind == $HlandRizort) {
                    # 町
                    $n = int((350 - $lv) / 2);
                    $n = min(int($n + rand($n)), $employed);
                    $employed -= $n;
                    $tLandValue->[$x][$y] += $n;
                } elsif ($landKind == $HlandBigRizort) {
                    # 平地
                    $n = int((800 - $lv) / 2);
                    $n = min(int($n + rand($n)), $employed);
                    $employed -= $n;
                    $tLandValue->[$x][$y] += $n;
                 } elsif ($landKind == $HlandKajino) {
                    # 平地
                    $n = int((2000 - $lv) / 2);
                    $n = min(int($n + rand($n)), $employed);
                    $employed -= $n;
                    $tLandValue->[$x][$y] += $n;
                }

                last if ($employed <= 0);
            }
            $migrate -= $employed;
            $island->{'pop'} -= $migrate;
            $tIsland->{'pop'} += $migrate;

            # 今まで住んでいた家を処分する
            $employed = $migrate;
            for($i = 0; $i < $HpointNumber; $i++) {
                $x = $Hrpx[$i];
                $y = $Hrpy[$i];
                $landKind = $land->[$x][$y];
                $lv = $landValue->[$x][$y];

                if((($landKind == $HlandRizort) && ($lv > 1)) ||
		  (($landKind == $HlandBigRizort) && ($lv > 1))) {
                    # 町
                    $n = min($lv - 1, $employed);
                    $landValue->[$x][$y] -= $n;
                    $employed -= $n;

			if($landValue->[$x][$y] <= 0) {
			    $land->[$x][$y] = $HlandPlains;
			    $landValue->[$x][$y] = 0;
			}

                }
            }

            logUnemployedMigrate2($id, $tIsland->{'id'}, $name, $tIsland->{'name'}, $migrate2);
        }
    }   elsif(($island->{'riz'} > 0) && (rand(20) > $s06) && (rand(500+$s06) < 20)) {

        my(@order) = randomArray($HislandNumber);
        my($migrate);

        # 移民先を探す
        my($tIsland);
        my($n) = min($HislandNumber, 5);
        my($i);
        for($i = 0; $i < $n; $i++) { # ５島まで調べる
            $tIsland = $Hislands[$order[$i]];

            # 仕事のある島に移民する
            if (($island->{'pop'} > $tIsland->{'pop'}) &&($island->{'id'} != $tIsland->{'id'})) {
                $migrate = (25 - $s06 + 1) * (random(3) + 1);
		        if ($migrate <= 0) {
			    $migrate = 1;
		        }
		$migrate2 = $migrate;
                last;
            }
        }

        if ($i >= $n) {

        } else {
            # 移民先が見つかったので移民
            my($tLand) = $tIsland->{'land'};
            my($tLandValue) = $tIsland->{'landValue'};
            my($employed) = $migrate;
            my($sekiflag) = 0;

            my($x, $y, $landKind, $lv);
            for($i = 0; $i < $HpointNumber; $i++) {
                $x = $Hrpx[$i];
                $y = $Hrpy[$i];
                $landKind = $tLand->[$x][$y];
                $lv = $tLandValue->[$x][$y];

	        if($landKind == $HlandSeki) {
                    logUnemployedReturn2($id, $tIsland->{'id'}, $name, landName($landKind, $lv), $tIsland->{'name'}, $migrate2);
                    $sekiflag++;
		    $migrate = 0;
		}

	    }

            # 移民先の町に家を用意する
            my($employed) = $migrate;
            my($x, $y, $landKind, $lv);
            for($i = 0; $i < $HpointNumber; $i++) {
                $x = $Hrpx[$i];
                $y = $Hrpy[$i];
                $landKind = $tLand->[$x][$y];
                $lv = $tLandValue->[$x][$y];

                if(($landKind == $HlandTown) ||
		  ($landKind == $HlandMinato) ||
		  ($landKind == $HlandProcity) ||
		  ($landKind == $HlandFrocity) ||
		  ($landKind == $HlandNewtown) ||
		  ($landKind == $HlandBigtown) ||
		  ($landKind == $HlandBettown) ||
		  ($landKind == $HlandSeatown) ||
		  ($landKind == $HlandOnsen) ||
		  ($landKind == $HlandSeacity)) {
                    # 町
                    $n = int((2000 - $lv) / 2);
                    $n = min(int($n + rand($n)), $employed);
                    $employed -= $n;
                    $tLandValue->[$x][$y] += $n;
                } elsif ($landKind == $HlandPlains) {
                    # 平地
                    $n = int((255 - $lv) / 2);
                    $n = min(int($n + rand($n)), $employed);
                    $employed -= $n;
                    $tLand->[$x][$y] = $HlandTown;
                    $tLandValue->[$x][$y] = $n;
                }

                last if ($employed <= 0);
            }
            $migrate -= $employed;
            $island->{'pop'} -= $migrate;
            $tIsland->{'pop'} += $migrate;

            # 今まで住んでいた家を処分する
            $employed = $migrate;
            for($i = 0; $i < $HpointNumber; $i++) {
                $x = $Hrpx[$i];
                $y = $Hrpy[$i];
                $landKind = $land->[$x][$y];
                $lv = $landValue->[$x][$y];

                if((($landKind == $HlandRizort) && ($lv > 1)) ||
		  (($landKind == $HlandBigRizort) && ($lv > 1)) ||
		  (($landKind == $HlandKajino) && ($lv > 1))) {
                    # 町
                    $n = min($lv - 1, $employed);
                    $landValue->[$x][$y] -= $n;
                    $employed -= $n;

			if($landValue->[$x][$y] <= 0) {
			    $land->[$x][$y] = $HlandPlains;
			    $landValue->[$x][$y] = 0;
			}

                }
            }

	        if($sekiflag == 0) {
		    logUnemployedMigrate3($id, $tIsland->{'id'}, $name, $tIsland->{'name'}, $migrate2);
		}

        }
    }


    # 地震判定
    if(random(1000) < (($island->{'prepare2'} + 1) * $HdisEarthquake)-int($island->{'eis2'}/15)-int($s04/10)) {
	# 地震発生
	logEarthquake($id, $name);

    if($toto2 > 0) {
	$toto2--;
	$island->{'etc8'} = "$toto1,$toto2,$toto3,$toto4,$toto5,$toto6,$toto7";
	logOmamori($id, $name);
    } else {

	my($x, $y, $landKind, $lv, $i);
	for($i = 0; $i < $HpointNumber; $i++) {
	    $x = $Hrpx[$i];
	    $y = $Hrpy[$i];
	    $landKind = $land->[$x][$y];
	    $lv = $landValue->[$x][$y];

	    if((($landKind == $HlandTown) && ($lv >= 100)) ||
	       (($landKind == $HlandFoodim) && ($lv < 480)) ||
	       (($landKind == $HlandProcity) && ($lv < 130)) ||
	       ($landKind == $HlandHaribote) ||
               ($landKind == $HlandPark) ||
	       ($landKind == $HlandMinato) ||
	       ($landKind == $HlandOnsen) ||
               ($landKind == $HlandKyujo) ||
               ($landKind == $HlandKyujokai) ||
	       ($landKind == $HlandFactory)) {
		# 1/4で壊滅
		if(random(4+$island->{'co5'}*5) == 0) {
		    logEQDamage($id, $name, landName($landKind, $lv),
				"($x, $y)");
		    $land->[$x][$y] = $HlandWaste;
		    $landValue->[$x][$y] = 0;
				if ($kind == $HlandOnsen) {
                        	# 金山は山に戻る
                        	$land->[$x][$y] = $HlandMountain; # 海になる
                        	$landValue->[$x][$y] = 0;
                    		}
		}
	    }
	    if((($landKind == $HlandBigtown) && ($lv >= 100)) ||
	       (($landKind == $HlandBettown) && ($lv >= 100)) ||
	       (($landKind == $HlandSkycity) && ($lv >= 100)) ||
	       (($landKind == $HlandShuto) && ($lv >= 100)) ||
	       (($landKind == $HlandUmishuto) && ($lv >= 100)) ||
	       (($landKind == $HlandRizort) && ($lv >= 10)) ||
	       (($landKind == $HlandKajino) && ($lv >= 10)) ||
	       (($landKind == $HlandBigRizort) && ($lv >= 10)) ||
	       (($landKind == $HlandHTFactory) && ($lv >= 10)) ||
	       (($landKind == $HlandSHTF) && ($lv >= 10)) ||
	       (($landKind == $HlandNewtown) && ($lv >= 100))) {
		# 1/4で壊滅
		if(random(3+$island->{'co5'}*5) == 0) {
		    logEQDamagenot($id, $name, landName($landKind, $lv),
				"($x, $y)");
	            $landValue->[$x][$y] -= random(100)+50;
		}
			if($landValue->[$x][$y] <= 0) {
			    # 平地に戻す
			    $land->[$x][$y] = $HlandWaste;
			    $landValue->[$x][$y] = 0;
		    	    logEQDamage($id, $name, landName($landKind, $lv),
				"($x, $y)");
			    next;
			}
	    }
	    if(($landKind == $HlandFarmchi) ||
               ($landKind == $HlandFarmpic) ||
	       ($landKind == $HlandFarmcow)) {
		if(random(6) == 0) {
		    logEQDamagenot($id, $name, landName($landKind, $lv),
				"($x, $y)");
	            $landValue->[$x][$y] -= random(400)+50;
		}
		if($landValue->[$x][$y] <= 0) {
		    # 平地に戻す
		    $land->[$x][$y] = $HlandWaste;
		    $landValue->[$x][$y] = 0;
		        logEQDamage($id, $name, landName($landKind, $lv),
			"($x, $y)");
		    next;
		}
	    }
	}
    }
    }



    # 重税にきれる住民
    if(random(100) < $island->{'eisei1'}-10-random(5)) {
	# 不足メッセージ
	logKire($id, $name);

	my($x, $y, $landKind, $lv, $i);
	for($i = 0; $i < $HpointNumber; $i++) {
	    $x = $Hrpx[$i];
	    $y = $Hrpy[$i];
	    $landKind = $land->[$x][$y];
	    $lv = $landValue->[$x][$y];

	    if(($landKind == $HlandFarm) ||
               ($landKind == $HlandCollege) ||
               ($landKind == $HlandYakusho) ||
	       ($landKind == $HlandFactory) ||
	       ($landKind == $HlandSHTF) ||
	       ($landKind == $HlandOWNF) ||
	       ($landKind == $HlandHTFactory) ||
               ($landKind == $HlandNursery) ||
               ($landKind == $HlandEneAt) ||
               ($landKind == $HlandEneFw) ||
               ($landKind == $HlandEneWt) ||
               ($landKind == $HlandEneWd) ||
               ($landKind == $HlandEneBo) ||
               ($landKind == $HlandEneSo) ||
               ($landKind == $HlandEneCs) ||
	       ($landKind == $HlandBase) ||
	       ($landKind == $HlandPark) ||
	       ($landKind == $HlandKyujo) ||
	       ($landKind == $HlandKyujokai) ||
	       ($landKind == $HlandZoo) ||
	       ($landKind == $HlandHouse) ||
	       ($landKind == $HlandTaishi) ||
	       ($landKind == $HlandTrain) ||
	       ($landKind == $HlandKura) ||
	       ($landKind == $HlandKuraf) ||
	       ($landKind == $HlandDefence)) {
		# 1/4で壊滅
		if(random(100) < $island->{'eisei1'}) {
		    logKireDamage($id, $name, landName($landKind, $lv),
				"($x, $y)");
		    $land->[$x][$y] = $HlandWaste;
		    $landValue->[$x][$y] = 0;
                    # でも養殖場なら浅瀬
                    if($landKind == $HlandNursery) {
                        $land->[$x][$y] = $HlandSea;
                        $landValue->[$x][$y] = 1;
                    }
		}
	    }
	    if(($landKind == $HlandTown) ||
               ($landKind == $HlandMinato) ||
	       ($landKind == $HlandFoodim) ||
               ($landKind == $HlandProcity) ||
	       ($landKind == $HlandFarmchi) ||
	       ($landKind == $HlandFarmpic) ||
	       ($landKind == $HlandFarmcow)) {
		# 1/4で壊滅
		if(random(100) < $island->{'eisei1'}-30) {
		    logKireDamage($id, $name, landName($landKind, $lv),
				"($x, $y)");
		    $land->[$x][$y] = $HlandWaste;
		    $landValue->[$x][$y] = 0;
		}
	    }
	    if(($landKind == $HlandSbase) ||
	       ($landKind == $HlandSeacity) ||
	       ($landKind == $HlandUmiamu) ||
	       ($landKind == $HlandFrocity)) {
		# 1/4で壊滅
		if(random(100) < $island->{'eisei1'}-60) {
		    logKireDamage($id, $name, landName($landKind, $lv),
				"($x, $y)");
		    $land->[$x][$y] = $HlandSea;
		    $landValue->[$x][$y] = 0;
		}
	    }

	}
    }



    # 食料不足
    if($island->{'food'} <= 0) {
	# 不足メッセージ
	logStarve($id, $name);
	$island->{'food'} = 0;


    if($island->{'eis7'} >= 1) {
	$eis7 = $island->{'eis7'};
	    $cstpop = int($eis7/100);
	    $csten = $eis7%100;
	    $tdmg = random(1000);
	    $cstpop = int($cstpop*$tdmg/1000);
           $island->{'eis7'} = $cstpop*100+$csten;
			if($cstpop < $tdmg) {
			$island->{'eis7'} = 0;
			logEiseiEndNopop($id, $name, "宇宙ステーション");
			}

	}


	my($x, $y, $landKind, $lv, $i);
	for($i = 0; $i < $HpointNumber; $i++) {
	    $x = $Hrpx[$i];
	    $y = $Hrpy[$i];
	    $landKind = $land->[$x][$y];
	    $lv = $landValue->[$x][$y];

	    if(($landKind == $HlandFarm) ||
	       ($landKind == $HlandFoodim) ||
	       ($landKind == $HlandFoodka) ||
               ($landKind == $HlandFarmchi) ||
               ($landKind == $HlandFarmpic) ||
               ($landKind == $HlandFarmcow) ||
               ($landKind == $HlandCollege) ||
               ($landKind == $HlandYakusho) ||
	       ($landKind == $HlandFactory) ||
	       ($landKind == $HlandHTFactory) ||
	       ($landKind == $HlandSHTF) ||
	       ($landKind == $HlandOWNF) ||
               ($landKind == $HlandNursery) ||
	       ($landKind == $HlandBase) ||
               ($landKind == $HlandMine) ||
               ($landKind == $HlandKura) ||
	       ($landKind == $HlandKuraf) ||
	       ($landKind == $HlandDefence)) {
		# 1/4で壊滅
		if(random(4) == 0) {
		    logSvDamage($id, $name, landName($landKind, $lv),
				"($x, $y)");
		    $land->[$x][$y] = $HlandWaste;
		    $landValue->[$x][$y] = 0;
                    # でも養殖場なら浅瀬
                    if($landKind == $HlandNursery) {
                        $land->[$x][$y] = $HlandSea;
                        $landValue->[$x][$y] = 1;
                    }
		}
	    }
	}
    }

    # 津波判定
    if(random(1000) < $HdisTsunami-int($island->{'eis2'}/15)-int($s04/10)) {
	# 津波発生
	logTsunami($id, $name);

    if($toto2 > 0) {
	$toto2--;
	$island->{'etc8'} = "$toto1,$toto2,$toto3,$toto4,$toto5,$toto6,$toto7";
	logOmamori($id, $name);
    } else {

	my($x, $y, $landKind, $lv, $i);
	for($i = 0; $i < $HpointNumber; $i++) {
	    $x = $Hrpx[$i];
	    $y = $Hrpy[$i];
	    $landKind = $land->[$x][$y];
	    $lv = $landValue->[$x][$y];

	    if(($landKind == $HlandTown) ||
	       (($landKind == $HlandProcity) && ($lv < 110)) ||
	       ($landKind == $HlandFarm) ||
	       ($landKind == $HlandFarmchi) ||
	       ($landKind == $HlandFarmpic) ||
	       ($landKind == $HlandFarmcow) ||
	       ($landKind == $HlandEneAt) ||
	       ($landKind == $HlandEneFw) ||
	       ($landKind == $HlandEneWt) ||
	       ($landKind == $HlandEneWd) ||
	       ($landKind == $HlandEneBo) ||
	       ($landKind == $HlandEneSo) ||
	       ($landKind == $HlandEneCs) ||
	       ($landKind == $HlandConden) ||
	       ($landKind == $HlandConden2) ||
	       ($landKind == $HlandConden3) ||
	       ($landKind == $HlandConden4) ||
	       ($landKind == $HlandTrain) ||
	       ($landKind == $HlandCollege) ||
	       ($landKind == $HlandYakusho) ||
	       ($landKind == $HlandFoodim) ||
	       ($landKind == $HlandFoodka) ||
	       ($landKind == $HlandFactory) ||
	       ($landKind == $HlandHTFactory) ||
	       ($landKind == $HlandSHTF) ||
	       ($landKind == $HlandOWNF) ||
	       ($landKind == $HlandBase) ||
	       ($landKind == $HlandDefence) ||
               ($landKind == $HlandPark) ||
	       ($landKind == $HlandMinato) ||
	       ($landKind == $HlandFune) ||
	       ($landKind == $HlandSeki) ||
               ($landKind == $HlandMine) ||
               ($landKind == $HlandNursery) ||
               ($landKind == $HlandKyujo) ||
               ($landKind == $HlandKyujokai) ||
               ($landKind == $HlandZoo) ||
               ($landKind == $HlandNewtown) ||
               ($landKind == $HlandBigtown) ||
               ($landKind == $HlandBettown) ||
               ($landKind == $HlandRizort) ||
               ($landKind == $HlandKajino) ||
               ($landKind == $HlandUmicity) ||
               ($landKind == $HlandBigRizort) ||
               ($landKind == $HlandShuto) ||
               ($landKind == $HlandKura) ||
	       ($landKind == $HlandKuraf) ||
	       ($landKind == $HlandHaribote)) {
		# 1d12 <= (周囲の海 - 1) で崩壊
		if(random(12+$island->{'co5'}*5) <
		   (countAround($land, $x, $y, $HlandOil, 7) +
		    countAround($land, $x, $y, $HlandSbase, 7) +
		    countAround($land, $x, $y, $HlandSeacity, 7) +
		    countAround($land, $x, $y, $HlandSeatown, 7) +
		    countAround($land, $x, $y, $HlandUmishuto, 7) +
		    countAround($land, $x, $y, $HlandFune, 7) +
		    countAround($land, $x, $y, $HlandFrocity, 7) +
		    countAround($land, $x, $y, $HlandUmiamu, 7) +
		    countAround($land, $x, $y, $HlandSea, 7) - 1)) {
		    logTsunamiDamage($id, $name, landName($landKind, $lv),
				     "($x, $y)");
		    if($landKind == $HlandFune) {
		    $land->[$x][$y] = $HlandSea;
		    $landValue->[$x][$y] = 0;
                    # でも養殖場なら浅瀬
                    } elsif($landKind == $HlandNursery) {
                        $land->[$x][$y] = $HlandSea;
                        $landValue->[$x][$y] = 1;
		    } else {
		    $land->[$x][$y] = $HlandWaste;
		    $landValue->[$x][$y] = 0;
		    }
		}
	    }
	}
    }
    }

    # 怪獣判定
    my($r) = random(10000);
    my($pop) = $island->{'pop'};
    do{
	if((($r < ($HdisMonster * $island->{'area'})) &&
	    ($pop >= $HdisMonsBorder1)) ||
	   ($island->{'monstersend'} > 0)) {
	    # 怪獣出現
	    # 種類を決める
	    my($lv, $kind);
	    if($island->{'monstersend'} > 0) {
		# 人造
		$kind = $island->{'monstersendkind'};
		$island->{'monstersend'}--;
	    } elsif($pop >= $HdisMonsBorder4) {
		# level4まで
		$kind = random($HmonsterLevel4) + 1;
	    } elsif($pop >= $HdisMonsBorder3) {
		# level3まで
		$kind = random($HmonsterLevel3) + 1;
	    } elsif($pop >= $HdisMonsBorder2) {
		# level2まで
		$kind = random($HmonsterLevel2) + 1;
	    } else {
		# level1のみ
		$kind = random($HmonsterLevel1) + 1;
	    }

	    # lvの値を決める
	    $lv = ($kind << 4)
		+ $HmonsterBHP[$kind] + random($HmonsterDHP[$kind]);

	    # どこに現れるか決める
	    my($bx, $by, $i);
	    for($i = 0; $i < $HpointNumber; $i++) {
		$bx = $Hrpx[$i];
		$by = $Hrpy[$i];
		if(($land->[$bx][$by] == $HlandTown) ||
		   ($land->[$bx][$by] == $HlandBigtown) ||
		   ($land->[$bx][$by] == $HlandBettown) ||
		   ($land->[$bx][$by] == $HlandSkycity) ||
		   ($land->[$bx][$by] == $HlandUmicity) ||
		   ($land->[$bx][$by] == $HlandRizort) ||
		   ($land->[$bx][$by] == $HlandKajino) ||
		   ($land->[$bx][$by] == $HlandBigRizort) ||
		   ($land->[$bx][$by] == $HlandNewtown)) {

		    # 地形名
		    my($lName) = landName($HlandTown, $landValue->[$bx][$by]);

		    # そのヘックスを怪獣に
		    $land->[$bx][$by] = $HlandMonster;
		    $landValue->[$bx][$by] = $lv;

		    # 怪獣情報
		    my($mKind, $mName, $mHp) = monsterSpec($lv);

		    # メッセージ
		    logMonsCome($id, $name, $mName, "($bx, $by)", $lName);
		    last;
		}
	    }
	}
    } while($island->{'monstersend'} > 0);

    # 地盤沈下判定
    if(($island->{'area'} > $HdisFallBorder) &&
       (random(1000) < $HdisFalldown)) {
	# 地盤沈下発生
	logFalldown($id, $name);

	my($x, $y, $landKind, $lv, $i);
	for($i = 0; $i < $HpointNumber; $i++) {
	    $x = $Hrpx[$i];
	    $y = $Hrpy[$i];
	    $landKind = $land->[$x][$y];
	    $lv = $landValue->[$x][$y];

	    if(($landKind != $HlandSea) &&
	       ($landKind != $HlandIce) &&
	       ($landKind != $HlandSbase) &&
	       ($landKind != $HlandSeacity) &&
	       ($landKind != $HlandSeatown) &&
	       ($landKind != $HlandUmishuto) &&
	       ($landKind != $HlandFune) &&
	       ($landKind != $HlandUmiamu) &&
	       ($landKind != $HlandOil) &&
	       ($landKind != $HlandGold) &&
	       ($landKind != $HlandOnsen) &&
	       ($landKind != $HlandMountain)) {

		# 周囲に海があれば、値を-1に
		if(countAround($land, $x, $y, $HlandSea, 7) + 
		   countAround($land, $x, $y, $HlandSeacity, 7) + 
		   countAround($land, $x, $y, $HlandSeatown, 7) + 
		   countAround($land, $x, $y, $HlandUmishuto, 7) + 
		   countAround($land, $x, $y, $HlandFune, 7) + 
		   countAround($land, $x, $y, $HlandUmiamu, 7) +
		   countAround($land, $x, $y, $HlandSbase, 7)) {
		    logFalldownLand($id, $name, landName($landKind, $lv),
				"($x, $y)");
		    $land->[$x][$y] = -1;
		    $landValue->[$x][$y] = 0;
		}
	    }
	}

	for($i = 0; $i < $HpointNumber; $i++) {
	    $x = $Hrpx[$i];
	    $y = $Hrpy[$i];
	    $landKind = $land->[$x][$y];

	    if($landKind == -1) {
		# -1になっている所を浅瀬に
		$land->[$x][$y] = $HlandSea;
		$landValue->[$x][$y] = 1;
	    } elsif ($landKind == $HlandSea) {
		# 浅瀬は海に
		$landValue->[$x][$y] = 0;
	    }

	}
    }

    # 台風判定
    if(random(1000) < $HdisTyphoon-int($island->{'eis1'}/10)) {
	# 台風発生
	logTyphoon($id, $name);
	$island->{'Typhoonflag'} = 1;

    if($toto2 > 0) {
	$toto2--;
	$island->{'etc8'} = "$toto1,$toto2,$toto3,$toto4,$toto5,$toto6,$toto7";
	logOmamori($id, $name);
    } else {

	my($x, $y, $landKind, $lv, $i);
	for($i = 0; $i < $HpointNumber; $i++) {
	    $x = $Hrpx[$i];
	    $y = $Hrpy[$i];
	    $landKind = $land->[$x][$y];
	    $lv = $landValue->[$x][$y];

	    if(($landKind == $HlandFarm) ||
	       ($landKind == $HlandEneWd) ||
	       ($landKind == $HlandHaribote)) {

		# 1d12 <= (6 - 周囲の森) で崩壊
		if(random(12+$island->{'co5'}*5) < 
		   (6
		    - countAround($land, $x, $y, $HlandForest, 7)
		    - countAround($land, $x, $y, $HlandMonument, 7))) {
		    logTyphoonDamage($id, $name, landName($landKind, $lv),
				     "($x, $y)");
		    $land->[$x][$y] = $HlandPlains;
		    $landValue->[$x][$y] = 0;
		}
	    }

	    if(($landKind == $HlandFune) ||
	       ($landKind == $HlandNursery)) {

		if(random(100+$island->{'co5'}*50) < 10) {
		    logTyphoonHason($id, $name, landName($landKind, $lv),
				     "($x, $y)");
                        $land->[$x][$y] = $HlandSea;
                        $landValue->[$x][$y] = 1;
		}
	    }

	}
    }
    }

    # 巨大隕石判定
    if(random(1000) < $HdisHugeMeteo-int($island->{'eis3'}/50)-int($s04/10)) {
	my($x, $y, $landKind, $lv, $point);

	# 落下
	$x = random($HislandSize);
	$y = random($HislandSize);
	$landKind = $land->[$x][$y];
	$lv = $landValue->[$x][$y];
	$point = "($x, $y)";

	# メッセージ
	logHugeMeteo($id, $name, $point);

    if($island->{'h10'} >= 1) {
	logOmamori2($id, $name);
	$land->[$x][$y] = $HlandSea;
	$landValue->[$x][$y] = 0;
    } elsif($toto2 > 1) {
	$toto2--;
	$toto2--;
	$island->{'etc8'} = "$toto1,$toto2,$toto3,$toto4,$toto5,$toto6,$toto7";
	logOmamori($id, $name);
	$land->[$x][$y] = $HlandSea;
	$landValue->[$x][$y] = 0;
    } else {

	# 広域被害ルーチン
	wideDamage($id, $name, $land, $landValue, $x, $y);
		                if (rand(1000) < 100) {
		                    $land->[$x][$y] = $HlandMonument;
		                    $landValue->[$x][$y] = 79;
		                }
    }
    }

    # 巨大ミサイル判定
    while($island->{'bigmissile'} > 0) {
	$island->{'bigmissile'} --;

	my($x, $y, $landKind, $lv, $point);

	# 落下
	$x = random($HislandSize);
	$y = random($HislandSize);
	$landKind = $land->[$x][$y];
	$lv = $landValue->[$x][$y];
	$point = "($x, $y)";

	# メッセージ
	logMonDamage($id, $name, $point);

	# 広域被害ルーチン
	wideDamage($id, $name, $land, $landValue, $x, $y);
    }

    # 隕石判定
    if(random(1000) < $HdisMeteo-int($island->{'eis3'}/40)-int($s04/10)) {

    if($island->{'h10'} >= 1) {
	# 落下
	$x = random($HislandSize);
	$y = random($HislandSize);
	$landKind = $land->[$x][$y];
	$lv = $landValue->[$x][$y];
	$point = "($x, $y)";
	$land->[$x][$y] = $HlandSea;
	$landValue->[$x][$y] = 0;
	# メッセージ
	logHugeMeteo4($id, $name, $point);
	logOmamori2($id, $name);
    } elsif($toto2 > 0) {
	# 落下
	$x = random($HislandSize);
	$y = random($HislandSize);
	$landKind = $land->[$x][$y];
	$lv = $landValue->[$x][$y];
	$point = "($x, $y)";
	$land->[$x][$y] = $HlandSea;
	$landValue->[$x][$y] = 0;
	# メッセージ
	logHugeMeteo4($id, $name, $point);
	$toto2--;
	$island->{'etc8'} = "$toto1,$toto2,$toto3,$toto4,$toto5,$toto6,$toto7";
	logOmamori($id, $name);
    } else {

	my($x, $y, $landKind, $lv, $point, $first);
	$first = 1;
	while((random(2) == 0) || ($first == 1)) {
	    $first = 0;
	    
	    # 落下
	    $x = random($HislandSize);
	    $y = random($HislandSize);
	    $landKind = $land->[$x][$y];
	    $lv = $landValue->[$x][$y];
	    $point = "($x, $y)";



	    my($i, $count, $sx, $sy);
	    $count = 0;
	    for($i = 0; $i < 19; $i++) {
		 $sx = $x + $ax[$i];
		 $sy = $y + $ay[$i];

		 # 行による位置調整
		 if((($sy % 2) == 0) && (($y % 2) == 1)) {
		     $sx--;
		 }

		 if(($sx < 0) || ($sx >= $HislandSize) ||
		    ($sy < 0) || ($sy >= $HislandSize)) {
		     # 範囲外の場合
		     if($kind == $HlandSea) {
			 # 海なら加算
			 $count++;
		     }
		 } else {
		     # 範囲内の場合
		     if(($land->[$sx][$sy] == $HlandDefence) && ($landValue->[$sx][$sy] == 77)) {
		                if (rand(100) < 30) {
		                $land->[$sx][$sy] = $HlandWaste;
				$landValue->[$sx][$sy] = 0;
				logTrainEnd2($id, $name, "防衛施設・改", "($sx, $sy)");
		                }
			 $count++;
		     }
		 }
	    }

	        if(($count > 0) && ($island->{'eis5'} >= 1)) {

		logMidMeteo3($id, $name, $point);
		$island->{'roudenflag'}++;
		$island->{'eis5'} -= random(50);
		        if($island->{'eis5'} < 1) {
		           $island->{'eis5'} = 0;
				logEiseiEnd($id, $name, "防衛衛星");
		        }

		} else {

		    if(($landKind == $HlandSea) && ($lv == 0)){
			# 海ポチャ
			logMeteoSea($id, $name, landName($landKind, $lv),
				    $point);
		    } elsif($landKind == $HlandMountain) {
			# 山破壊
			logMeteoMountain($id, $name, landName($landKind, $lv),
					 $point);
			$land->[$x][$y] = $HlandWaste;
			$landValue->[$x][$y] = 0;
			next;
		    } elsif($landKind == $HlandGold) {
			# 山破壊
			logMeteoMountain($id, $name, landName($landKind, $lv),
					 $point);
			$land->[$x][$y] = $HlandWaste;
			$landValue->[$x][$y] = 0;
			next;
		    } elsif($landKind == $HlandOnsen) {
			# 山破壊
			logMeteoMountain($id, $name, landName($landKind, $lv),
					 $point);
			$land->[$x][$y] = $HlandWaste;
			$landValue->[$x][$y] = 0;
			next;
		    } elsif($landKind == $HlandSbase) {
			logMeteoSbase($id, $name, landName($landKind, $lv),
				      $point);
		    } elsif($landKind == $HlandSeacity) {
			logMeteoSbase($id, $name, landName($landKind, $lv),
				      $point);
		    } elsif($landKind == $HlandUmishuto) {
			logMeteoSbase($id, $name, landName($landKind, $lv),
				      $point);
		    } elsif($landKind == $HlandSeatown) {
			logMeteoSbase($id, $name, landName($landKind, $lv),
				      $point);
		    } elsif($landKind == $HlandFune) {
			logMeteoSbase($id, $name, landName($landKind, $lv),
				      $point);
		    } elsif($landKind == $HlandFrocity) {
			logMeteoSbase($id, $name, landName($landKind, $lv),
				      $point);
		    } elsif($landKind == $HlandUmiamu) {
			logMeteoSbase($id, $name, landName($landKind, $lv),
				      $point);
		    } elsif($landKind == $HlandMonster) {
			logMeteoMonster($id, $name, landName($landKind, $lv),
					$point);
		    } elsif($landKind == $HlandSea) {
			# 浅瀬
			logMeteoSea1($id, $name, landName($landKind, $lv),
				     $point);
		    } elsif($landKind == $HlandIce) {
			# 浅瀬
			logMeteoSea1($id, $name, landName($landKind, $lv),
				     $point);
		    } else {
			logMeteoNormal($id, $name, landName($landKind, $lv),
				       $point);
		    }
		    $land->[$x][$y] = $HlandSea;
		    $landValue->[$x][$y] = 0;
		                if (rand(1000) < 50) {
		                    $land->[$x][$y] = $HlandMonument;
		                    $landValue->[$x][$y] = 79;
		                }
		    }
	    }
        }
    }

    # 噴火判定
    if(random(1000) < $HdisEruption-int($island->{'eis2'}/40)-int($s04/10)) {
	my($x, $y, $sx, $sy, $i, $landKind, $lv, $point);
	$x = random($HislandSize);
	$y = random($HislandSize);
	$landKind = $land->[$x][$y];
	$lv = $landValue->[$x][$y];
	$point = "($x, $y)";
	logEruption($id, $name, landName($landKind, $lv),
		    $point);
	$land->[$x][$y] = $HlandMountain;
	$landValue->[$x][$y] = 0;

        if($toto2 > 1) {
	$toto2--;
	$toto2--;
	$island->{'etc8'} = "$toto1,$toto2,$toto3,$toto4,$toto5,$toto6,$toto7";
	logOmamori($id, $name);
        } else {

		                if (rand(1000) < 50) {
		                    $land->[$x][$y] = $HlandMonument;
		                    $landValue->[$x][$y] = 78;
		                }
		                if (rand(1000) < 100) {
		                    $land->[$x][$y] = $HlandMonument;
		                    $landValue->[$x][$y] = 75;
		                }
	for($i = 1; $i < 7; $i++) {
	    $sx = $x + $ax[$i];
	    $sy = $y + $ay[$i];

	    # 行による位置調整
	    if((($sy % 2) == 0) && (($y % 2) == 1)) {
		$sx--;
	    }

	    $landKind = $land->[$sx][$sy];
	    $lv = $landValue->[$sx][$sy];
	    $point = "($sx, $sy)";

	    if(($sx < 0) || ($sx >= $HislandSize) ||
	       ($sy < 0) || ($sy >= $HislandSize)) {
	    } else {
		# 範囲内の場合
		$landKind = $land->[$sx][$sy];
		$lv = $landValue->[$sx][$sy];
		$point = "($sx, $sy)";
		if(($landKind == $HlandSea) ||
		   ($landKind == $HlandIce) ||
		   ($landKind == $HlandOil) ||
		   ($landKind == $HlandFune) ||
		   ($landKind == $HlandFrocity) ||
		   ($landKind == $HlandUmiamu) ||
		   ($landKind == $HlandSeacity) ||
		   ($landKind == $HlandSeatown) ||
		   ($landKind == $HlandUmishuto) ||
		   ($landKind == $HlandSbase)) {
		    # 海の場合
		    if(($lv == 1) ||
		       ($landKind == $HlandIce)) {
			# 浅瀬
			logEruptionSea1($id, $name, landName($landKind, $lv),
					$point);
		    } else {
			logEruptionSea($id, $name, landName($landKind, $lv),
				       $point);
			$land->[$sx][$sy] = $HlandSea;
			$landValue->[$sx][$sy] = 1;
			next;
		    }
		} elsif(($landKind == $HlandMountain) ||
			($landKind == $HlandMonster) ||
			($landKind == $HlandGold) ||
			($landKind == $HlandOnsen) ||
			($landKind == $HlandWaste)) {
		    next;
		} else {
		    # それ以外の場合
		    logEruptionNormal($id, $name, landName($landKind, $lv),
				      $point);
		}
		$land->[$sx][$sy] = $HlandWaste;
		$landValue->[$sx][$sy] = 0;
		                if (rand(1000) < 50) {
		                    $land->[$sx][$sy] = $HlandMonument;
		                    $landValue->[$sx][$sy] = 75;
		                }
	    }
	}
    }
    }

    if($island->{'eis1'} >= 1) {
       $island->{'eis1'} -= random(2);
        if($island->{'eis1'} < 1) {
           $island->{'eis1'} = 0;
		logEiseiEnd($id, $name, "気象衛星");
        }
    }
    if($island->{'eis2'} >= 1) {
       $island->{'eis2'} -= random(2);
        if($island->{'eis2'} < 1) {
           $island->{'eis2'} = 0;
		logEiseiEnd($id, $name, "観測衛星");
        }
    }
    if($island->{'eis3'} >= 1) {
       $island->{'eis3'} -= random(2);
        if($island->{'eis3'} < 1) {
           $island->{'eis3'} = 0;
		logEiseiEnd($id, $name, "迎撃衛星");
        }
    }
    if($island->{'eis4'} >= 1) {
       $island->{'eis4'} -= random(2);
        if($island->{'eis4'} < 1) {
           $island->{'eis4'} = 0;
		logEiseiEnd($id, $name, "軍事衛星");
        }
    }
    if($island->{'eis5'} >= 1) {
       $island->{'eis5'} -= random(2);
        if($island->{'eis5'} < 1) {
           $island->{'eis5'} = 0;
		logEiseiEnd($id, $name, "防衛衛星");
        }
    }
    if($island->{'eis6'} >= 1) {
	    my($i,$sx,$sy);
	    for($i = 0; $i < $HpointNumber; $i++){
		$sx = $Hrpx[$i];
		$sy = $Hrpy[$i];
	    if($land->[$sx][$sy] == $HlandMonster){
		my($tKind, $tName, $tHp) = monsterSpec($landValue->[$sx][$sy]);
		my($tlv) = $landValue->[$sx][$sy];
		my($tspecial) = $HmonsterSpecial[$tKind];
		$point = int($island->{'rena'}/1000);

	    logIreAttackt($id, $name, "イレギュラー", $point, $tName, "($sx, $sy)");

	    $island->{'eis6'} -= 10;

	    $tHp -= int($island->{'rena'}/1000);
	    $tlv -= int($island->{'rena'}/1000);
		$landValue->[$sx][$sy] = $tlv;
	    if($tHp < 1){
	    # 対象の怪獣が倒れて荒地になる
		$land->[$sx][$sy] = $HlandWaste;
		$landValue->[$sx][$sy] = 0;
	    # 報奨金
		my($value) = $HmonsterValue[$tKind];
		   $island->{'money'} += $value;
		   logMsMonMoney($id, $tName, $value);
		}
	    next;
	    }
	}

       $island->{'eis6'} -= random(2);
        if($island->{'eis6'} < 1) {
           $island->{'eis6'} = 0;
		logEiseiEnd($id, $name, "イレギュラー");
        }
    }

    if($island->{'eis7'} >= 1) {
	$eis7 = $island->{'eis7'};
	    $cstpop = int($eis7/100);
	    $csten = $eis7%100;

	    if($island->{'m17'} < int($cstpop/10000)+1) {
		logNoRokeCst($id, $name, $comName, $point);
		$cstpop -= 1000;
	    } else {
		$island->{'money'} -= $cstpop;
	    }

           $island->{'eis7'} = $cstpop*100+$csten;

        if($cstpop < 1) {
           $island->{'eis7'} = 0;
		logEiseiEndNopop($id, $name, "宇宙ステーション");
        }
        if($csten < 1) {
           $island->{'eis7'} = 0;
		logEiseiEnd($id, $name, "宇宙ステーション");
        }
    }

    if(($island->{'h11'} >= 1) && ($island->{'shouhi'} < $island->{'ene'})) {
	    my($i,$sx,$sy);
	    for($i = 0; $i < $HpointNumber; $i++){
		$sx = $Hrpx[$i];
		$sy = $Hrpy[$i];
	    if($land->[$sx][$sy] == $HlandMonster){
		my($tKind, $tName, $tHp) = monsterSpec($landValue->[$sx][$sy]);
		my($tlv) = $landValue->[$sx][$sy];
		my($tspecial) = $HmonsterSpecial[$tKind];
		$point = int($island->{'rena'}/1000);
		$island->{'shouhi'} += random(20000);
		logFuneAttackSSS3($id, $name, "天空城", $point, $tName, "($sx, $sy)");

	    # 対象の怪獣が倒れて荒地になる
		$land->[$sx][$sy] = $HlandWaste;
		$landValue->[$sx][$sy] = 1;
            }
        }
    }


    $auc4 = $island->{'auc4'};
    $auc4 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
    ($auc4a, $auc4b, $auc4c) = ($1, $2, $3);

    if((($HislandTurn % $HturnPrizeUnit) == 0) || ($auc4b == $aucshouhin)) {

	$hcturn = int($HislandTurn/100)*100;

	$auc9 = $island->{'auc9'};
	$auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);
	$auc9c2 = int($auc9c/10000);
	$auc9c3 = int($auc9c/10000)*10000;

	$auction1 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($shuppin1, $avalue1, $ajoutai1, $topvalue1, $topid1) = ($1, $2, $3, $4, $5);


	$auc6 = $island->{'auc6'};
	$auc6 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
	($auc6a, $auc6x, $auc6y) = ($1, $2, $3);
	    if($auc6a > 2) {
		$auc6a--;
		$island->{'auc6'} = "$auc6a,$auc6x,$auc6y";
	    }

	if(($island->{'auc1'} == $topvalue1) && ($topvalue1 != 0) && ($island->{'money'}+$auc9c3 < $topvalue1*10000) && ($auc4b != $aucshouhin)) {
	    $island->{'auc6'} = "7,0,0";
	}

	if(($island->{'auc1'} == $topvalue1) && ($topvalue1 != 0) && ($island->{'money'}+$auc9c3 > $topvalue1*10000) && ($auc4b != $aucshouhin)) {

	    $shouhiauc9 = $auc9c2 - $topvalue1;

	    if($shouhiauc9 < 0) {
		$island->{'money'} -= ($topvalue1-$auc9c2)*10000;
		$auc9c2 = 0;
		$auc9c = $auc9c%10000;
		$auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
		$island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";
	    } else {
		$auc9c -= $topvalue1*10000;
		$auc9c2 = int($auc9c/10000);
		$auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
		$island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";
	    }

	    if($shuppin1 != 30) {
		$auc6 = $island->{'auc6'};
		$auc6 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
		($auc6a, $auc6x, $auc6y) = ($1, $2, $3);
		$auc6a = 1;
		$island->{'auc6'} = "$auc6a,$auc6x,$auc6y";
	    }


	    $aucflag1 += $topvalue1;

	    $auc0 = $island->{'auc0'};
	    $auc0 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($auc0a, $auc0b, $auc0c, $auc0d, $auc0e) = ($1, $2, $3, $4, $5);
	    if($topvalue1 > $auc0c) {
	    $island->{'auc0'} = "$shuppin1,$avalue1,$topvalue1,$hcturn,$auc0e";
	    }

	    if($shuppin1 == 0) {
		    $ac = '闇石';
		} elsif($shuppin1 == 1) {
		    $ac = '地石';
		} elsif($shuppin1 == 2) {
		    $ac = '氷石';
		} elsif($shuppin1 == 3) {
		    $ac = '風石';
		} elsif($shuppin1 == 4) {
		    $ac = '炎石';
		} elsif($shuppin1 == 5) {
		    $ac = '光石';
		} elsif($shuppin1 == 6) {
		    $ac = '天使ミカエル';
		} elsif($shuppin1 == 7) {
		    $ac = 'アイススコーピオン';
		} elsif($shuppin1 == 8) {
		    $ac = 'スライムレジェンド';
		} elsif($shuppin1 == 9) {
		    $ac = "お守り$avalue1個";
		} elsif($shuppin1 == 10) {
		    $avalue1s = $avalue1 * 1000;
		    $ac = "海あみゅ$avalue1s人規模";
		} elsif($shuppin1 == 11) {
		    $avalue1s = $avalue1 * 1000;
		    $ac = "食研$avalue1s人規模";
		} elsif($shuppin1 == 12) {
		    $ac = "コスモ$avalue1万ｋＷ";
		} elsif($shuppin1 == 13) {
		    $ac = '闇石';
		} elsif($shuppin1 == 14) {
		    $ac = '衛星６種';
		} elsif($shuppin1 == 15) {
		    $ac = '宇宙ステーション';
		} elsif($shuppin1 == 16) {
		    $ac = '黄金のコンデンサ';
		} elsif($shuppin1 == 17) {
		    $avalue1s = $avalue1 * 1000;
		    $ac = "金山$avalue1s人規模";
		} elsif($shuppin1 == 18) {
		    $avalue1s = $avalue1 * 1000;
		    $ac = "養殖場$avalue1s人規模";
		} elsif($shuppin1 == 19) {
		    $ac = '人造怪獣f02';
		} elsif($shuppin1 == 20) {
		    $ac = '魔王サタン';
		} elsif($shuppin1 == 21) {
		    $ac = 'unknown';
		} elsif($shuppin1 == 22) {
		    $ac = "サッカーチーム力1.$avalue1倍";
		} elsif($shuppin1 == 23) {
		    $ac = "生物大学能力1.$avalue1倍";
		} elsif($shuppin1 == 24) {
		    $ac = "生物大学経験値$avalue1";
		} elsif($shuppin1 == 25) {
		    $ac = '卵';
		} elsif($shuppin1 == 26) {
		    $ac = '生物大学';
		} elsif($shuppin1 == 27) {
		    $ac = "風力$avalue1万ｋＷ";
		} elsif($shuppin1 == 28) {
		    $ac = "バイオマス$avalue1万ｋＷ";
		} elsif($shuppin1 == 29) {
		    $ac = '今回はお休み';
		} elsif($shuppin1 == 30) {
		    my($island, $j, $name, $id, $ii);
		    for($ii = 0; $ii < $HislandNumber; $ii++) {
			$j = $ii + 1;
			$island = $Hislands[$ii];
			$id = $island->{'id'};
				if($avalue1 == $island->{'id'}) {
				    $dashiname = $island->{'auc7'};
				}
			}
		    $ac = "$dashiname";
		} else {
		    $ac = '？';
		}

	    if(($shuppin1 == 6) || ($shuppin1 == 7) || ($shuppin1 == 8) || ($shuppin1 == 19) || ($shuppin1 == 20) || ($shuppin1 == 21)) {

		my($i,$sx,$sy);
		my($zlv) = (0);
		for($i = 0; $i < $HpointNumber; $i++){
		    $sx = $Hrpx[$i];
		    $sy = $Hrpy[$i];
			if($land->[$sx][$sy] == $HlandZoo){
			    $zlv += $landValue->[$sx][$sy];
			}
		}

		$etc6 = $island->{'etc6'};
		$etc6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		($z0,$z1,$z2,$z3,$z4,$z5,$z6,$z7,$z8,$z9,$z10,$z11,$z12,$z13,$z14,$z15,$z16,$z17,$z18,$z19,$z20,$z21,$z22,$z23,$z24,$z25,$z26,$z27,$z28,$z29,$z30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
		($z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

		$zookazu = $z0+$z1+$z2+$z3+$z4+$z5+$z6+$z7+$z8+$z9+$z10+$z11+$z12+$z13+$z14+$z15+$z16+$z17+$z18+$z19+$z20+$z21+$z22+$z23+$z24+$z25+$z26+$z27+$z28+$z29+$z30;

			if(($zlv > $zookazu) && ($island->{'zoo'} > 0)) {

				if($shuppin1 == 6) {
				    $ack = 13;
				} elsif($shuppin1 == 7) {
				    $ack = 22;
				} elsif($shuppin1 == 8) {
				    $ack = 14;
				} elsif($shuppin1 == 19) {
				    $ack = 17;
				} elsif($shuppin1 == 20) {
				    $ack = 21;
				} elsif($shuppin1 == 21) {
				    $ack = 23;
				}

				logMonsCome2($id, $name, $ac, $topvalue1);
				$z->{"$ack"}++;
				$island->{'etc6'} = "$z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}";

			}

		} elsif($shuppin1 == 9) {

		    $etc8 = $island->{'etc8'};
		    $etc8 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($toto1, $toto2, $toto3, $toto4, $toto5, $toto6, $toto7) = ($1, $2, $3, $4, $5, $6, $7);
		    $toto2 += $avalue1;
		    $island->{'etc8'} = "$toto1,$toto2,$toto3,$toto4,$toto5,$toto6,$toto7";

		    logMonsCome2($id, $name, $ac, $topvalue1);

		} elsif($shuppin1 == 14) {

		    $island->{'eis1'} = 200;
		    $island->{'eis2'} = 200;
		    $island->{'eis3'} = 200;
		    $island->{'eis4'} = 200;
		    $island->{'eis5'} = 200;
		    $island->{'eis6'} = 200;

		    logMonsCome2($id, $name, $ac, $topvalue1);

		} elsif($shuppin1 == 15) {

		    $island->{'eis7'} = 100099;

		    logMonsCome2($id, $name, $ac, $topvalue1);

		} elsif($shuppin1 == 22) {

		    $eisei4 = $island->{'eisei4'};
		    $eisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($sto, $std, $stk, $stwin, $stdrow, $stlose, $stwint, $stdrowt, $stloset, $styusho, $stshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);
		    $sto += int($sto * $avalue1 / 10);
		    $std += int($std * $avalue1 / 10);
		    $stk += int($stk * $avalue1 / 10);
		    $island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";

		    logMonsCome2($id, $name, $ac, $topvalue1);

		} elsif($shuppin1 == 23) {

		    $eisei5 = $island->{'eisei5'};
		    $eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tet) = ($1, $2, $3, $4, $5, $6, $7);
		    $msap += int($msap * $avalue1 / 10);
		    $msdp += int($msdp * $avalue1 / 10);
		    $mssp += int($mssp * $avalue1 / 10);
		    $island->{'eisei5'} = "$mshp,$msap,$msdp,$mssp,$mswin,$msexe,$tet";

		    logMonsCome2($id, $name, $ac, $topvalue1);

		} elsif($shuppin1 == 24) {

		    $eisei5 = $island->{'eisei5'};
		    $eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tet) = ($1, $2, $3, $4, $5, $6, $7);
		    $msexe += $avalue1;
		    $island->{'eisei5'} = "$mshp,$msap,$msdp,$mssp,$mswin,$msexe,$tet";

		    logMonsCome2($id, $name, $ac, $topvalue1);

		} else {

		    # どこに現れるか決める
		    my($bx, $by, $i);
		    for($i = 0; $i < $HpointNumber; $i++) {
			$bx = $Hrpx[$i];
			$by = $Hrpy[$i];
			if(($land->[$bx][$by] == $HlandPlains) ||
			   ($land->[$bx][$by] == $HlandPlains2)) {

				if($shuppin1 == 0) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 74;
				} elsif($shuppin1 == 1) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 75;
				} elsif($shuppin1 == 2) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 76;
				} elsif($shuppin1 == 3) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 77;
				} elsif($shuppin1 == 4) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 78;
				} elsif($shuppin1 == 5) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 79;
				} elsif($shuppin1 == 10) {
				    $land->[$bx][$by] = $HlandUmiamu;
				    $landValue->[$bx][$by] = $avalue1;
				} elsif($shuppin1 == 11) {
				    $land->[$bx][$by] = $HlandFoodim;
				    $landValue->[$bx][$by] = $avalue1;
				} elsif($shuppin1 == 12) {
				    $land->[$bx][$by] = $HlandEneCs;
				    $landValue->[$bx][$by] = $avalue1;
				} elsif($shuppin1 == 13) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 74;
				} elsif($shuppin1 == 16) {
				    $land->[$bx][$by] = $HlandConden3;
				    $landValue->[$bx][$by] = 0;
				} elsif($shuppin1 == 17) {
				    $land->[$bx][$by] = $HlandGold;
				    $landValue->[$bx][$by] = $avalue1;
				} elsif($shuppin1 == 18) {
				    $land->[$bx][$by] = $HlandNursery;
				    $landValue->[$bx][$by] = $avalue1;
				} elsif($shuppin1 == 25) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = $avalue1;
				} elsif($shuppin1 == 26) {
				    $land->[$bx][$by] = $HlandCollege;
				    $landValue->[$bx][$by] = 4;
				} elsif($shuppin1 == 27) {
				    $land->[$bx][$by] = $HlandEneWd;
				    $landValue->[$bx][$by] = $avalue1;
				} elsif($shuppin1 == 28) {
				    $land->[$bx][$by] = $HlandEneBo;
				    $landValue->[$bx][$by] = $avalue1;
				} elsif($shuppin1 == 30) {
				    my($tn) = $HidToNumber{$avalue1};
				    if($tn eq '') {

				    } else {
				    my($tIsland) = $Hislands[$tn];
				    my($tName) = $tIsland->{'name'};
				    my($tLand) = $tIsland->{'land'};
				    my($tLandValue) = $tIsland->{'landValue'};
					$tauc6 = $tIsland->{'auc6'};
					$tauc6 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
					($tauc6a, $tauc6x, $tauc6y) = ($1, $2, $3);
					$tIsland->{'auc6'} = "0,0,0";
				    my($tx, $ty);
					$tx = $tauc6x;
					$ty = $tauc6y;
				    my($tL) = $tLand->[$tx][$ty];
				    my($tLv) = $tLandValue->[$tx][$ty];
				    my($tLname) = landName($tL, $tLv);
					$island->{'stocklandkind'} = $tLand->[$tx][$ty];
					$island->{'stocklandvalue'} = $tLandValue->[$tx][$ty];
					$tLand->[$tx][$ty] = $HlandPlains;
					$tLandValue->[$tx][$ty] = 0;
					$land->[$bx][$by] = $island->{'stocklandkind'};
					$landValue->[$bx][$by] = $island->{'stocklandvalue'};

					$tauc9 = $tIsland->{'auc9'};
					$tauc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
					($tauc9a, $tauc9b, $tauc9c, $tauc9d, $tauc9e) = ($1, $2, $3, $4, $5);
					$tauc9c += $topvalue1*10000;
					$tauc9c2 = int($tauc9c/10000);
					$tauc9a = $tauc9b + $tauc9c2 + $tauc9d + $tauc9e;
					$tIsland->{'auc9'} = "$tauc9a,$tauc9b,$tauc9c,$tauc9d,$tauc9e";

					$island->{'auc8'} = "$tName島出品の$tLname";

					$aucland = $tL * $tLv;

						if($aucland != $topid1) {
							$tIsland->{'auc6'} = "77,0,0";
						}
				    }

				}

			    # メッセージ
			    logMonsCome2($id, $name, $ac, $topvalue1);
			    last;
			}
		    }
		}
	    }


	$auction2 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($shuppin2, $avalue2, $ajoutai2, $topvalue2, $topid2) = ($1, $2, $3, $4, $5);

	if(($island->{'auc2'} == $topvalue2) && ($topvalue2 != 0) && ($island->{'money'}+$auc9c3 < $topvalue2*10000) && ($auc4b != $aucshouhin)) {
	    $island->{'auc6'} = "7,0,0";
	}

	if(($island->{'auc2'} == $topvalue2) && ($topvalue2 != 0) && ($island->{'money'}+$auc9c3 > $topvalue2*10000) && ($auc4b != $aucshouhin)) {

	    $shouhiauc9 = $auc9c2 - $topvalue2;

	    if($shouhiauc9 < 0) {
		$island->{'money'} -= ($topvalue2-$auc9c2)*10000;
		$auc9c2 = 0;
		$auc9c = $auc9c%10000;
		$auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
		$island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";
	    } else {
		$auc9c -= $topvalue2*10000;
		$auc9c2 = int($auc9c/10000);
		$auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
		$island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";
	    }

	    if($shuppin2 != 30) {
		$auc6 = $island->{'auc6'};
		$auc6 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
		($auc6a, $auc6x, $auc6y) = ($1, $2, $3);
		$auc6a = 1;
		$island->{'auc6'} = "$auc6a,$auc6x,$auc6y";
	    }

	    $aucflag2 += $topvalue2;

	    $auc0 = $island->{'auc0'};
	    $auc0 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($auc0a, $auc0b, $auc0c, $auc0d, $auc0e) = ($1, $2, $3, $4, $5);
	    if($topvalue2 > $auc0c) {
	    $island->{'auc0'} = "$shuppin2,$avalue2,$topvalue2,$hcturn,$auc0e";
	    }

	    if($shuppin2 == 0) {
		    $ac = '闇石';
		} elsif($shuppin2 == 1) {
		    $ac = '地石';
		} elsif($shuppin2 == 2) {
		    $ac = '氷石';
		} elsif($shuppin2 == 3) {
		    $ac = '風石';
		} elsif($shuppin2 == 4) {
		    $ac = '炎石';
		} elsif($shuppin2 == 5) {
		    $ac = '光石';
		} elsif($shuppin2 == 6) {
		    $ac = '天使ミカエル';
		} elsif($shuppin2 == 7) {
		    $ac = 'アイススコーピオン';
		} elsif($shuppin2 == 8) {
		    $ac = 'スライムレジェンド';
		} elsif($shuppin2 == 9) {
		    $ac = "お守り$avalue2個";
		} elsif($shuppin2 == 10) {
		    $avalue2s = $avalue2 * 1000;
		    $ac = "海あみゅ$avalue2s人規模";
		} elsif($shuppin2 == 11) {
		    $avalue2s = $avalue2 * 1000;
		    $ac = "食研$avalue2s人規模";
		} elsif($shuppin2 == 12) {
		    $ac = "コスモ$avalue2万ｋＷ";
		} elsif($shuppin2 == 13) {
		    $ac = '闇石';
		} elsif($shuppin2 == 14) {
		    $ac = '衛星６種';
		} elsif($shuppin2 == 15) {
		    $ac = '宇宙ステーション';
		} elsif($shuppin2 == 16) {
		    $ac = '黄金のコンデンサ';
		} elsif($shuppin2 == 17) {
		    $avalue2s = $avalue2 * 1000;
		    $ac = "金山$avalue2s人規模";
		} elsif($shuppin2 == 18) {
		    $avalue2s = $avalue2 * 1000;
		    $ac = "養殖場$avalue2s人規模";
		} elsif($shuppin2 == 19) {
		    $ac = '人造怪獣f02';
		} elsif($shuppin2 == 20) {
		    $ac = '魔王サタン';
		} elsif($shuppin2 == 21) {
		    $ac = 'unknown';
		} elsif($shuppin2 == 22) {
		    $ac = "サッカーチーム力1.$avalue2倍";
		} elsif($shuppin2 == 23) {
		    $ac = "生物大学能力1.$avalue2倍";
		} elsif($shuppin2 == 24) {
		    $ac = "生物大学経験値$avalue2";
		} elsif($shuppin2 == 25) {
		    $ac = '卵';
		} elsif($shuppin2 == 26) {
		    $ac = '生物大学';
		} elsif($shuppin2 == 27) {
		    $ac = "風力$avalue2万ｋＷ";
		} elsif($shuppin2 == 28) {
		    $ac = "バイオマス$avalue2万ｋＷ";
		} elsif($shuppin2 == 29) {
		    $ac = '今回はお休み';
		} elsif($shuppin2 == 30) {
		    my($island, $j, $name, $id, $ii);
		    for($ii = 0; $ii < $HislandNumber; $ii++) {
			$j = $ii + 1;
			$island = $Hislands[$ii];
			$id = $island->{'id'};
				if($avalue2 == $island->{'id'}) {
				    $dashiname = $island->{'auc7'};
				}
			}
		    $ac = "$dashiname";
		} else {
		    $ac = '？';
		}

	    if(($shuppin2 == 6) || ($shuppin2 == 7) || ($shuppin2 == 8) || ($shuppin2 == 19) || ($shuppin2 == 20) || ($shuppin2 == 21)) {

		my($i,$sx,$sy);
		my($zlv) = (0);
		for($i = 0; $i < $HpointNumber; $i++){
		    $sx = $Hrpx[$i];
		    $sy = $Hrpy[$i];
			if($land->[$sx][$sy] == $HlandZoo){
			    $zlv += $landValue->[$sx][$sy];
			}
		}

		$etc6 = $island->{'etc6'};
		$etc6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		($z0,$z1,$z2,$z3,$z4,$z5,$z6,$z7,$z8,$z9,$z10,$z11,$z12,$z13,$z14,$z15,$z16,$z17,$z18,$z19,$z20,$z21,$z22,$z23,$z24,$z25,$z26,$z27,$z28,$z29,$z30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
		($z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

		$zookazu = $z0+$z1+$z2+$z3+$z4+$z5+$z6+$z7+$z8+$z9+$z10+$z11+$z12+$z13+$z14+$z15+$z16+$z17+$z18+$z19+$z20+$z21+$z22+$z23+$z24+$z25+$z26+$z27+$z28+$z29+$z30;

			if(($zlv > $zookazu) && ($island->{'zoo'} > 0)) {

				if($shuppin2 == 6) {
				    $ack = 13;
				} elsif($shuppin2 == 7) {
				    $ack = 22;
				} elsif($shuppin2 == 8) {
				    $ack = 14;
				} elsif($shuppin2 == 19) {
				    $ack = 17;
				} elsif($shuppin2 == 20) {
				    $ack = 21;
				} elsif($shuppin2 == 21) {
				    $ack = 23;
				}

				logMonsCome2($id, $name, $ac, $topvalue2);
				$z->{"$ack"}++;
				$island->{'etc6'} = "$z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}";

			}

		} elsif($shuppin2 == 9) {

		    $etc8 = $island->{'etc8'};
		    $etc8 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($toto1, $toto2, $toto3, $toto4, $toto5, $toto6, $toto7) = ($1, $2, $3, $4, $5, $6, $7);
		    $toto2 += $avalue2;
		    $island->{'etc8'} = "$toto1,$toto2,$toto3,$toto4,$toto5,$toto6,$toto7";

		    logMonsCome2($id, $name, $ac, $topvalue2);

		} elsif($shuppin2 == 14) {

		    $island->{'eis1'} = 200;
		    $island->{'eis2'} = 200;
		    $island->{'eis3'} = 200;
		    $island->{'eis4'} = 200;
		    $island->{'eis5'} = 200;
		    $island->{'eis6'} = 200;

		    logMonsCome2($id, $name, $ac, $topvalue2);

		} elsif($shuppin2 == 15) {

		    $island->{'eis7'} = 100099;

		    logMonsCome2($id, $name, $ac, $topvalue2);

		} elsif($shuppin2 == 22) {

		    $eisei4 = $island->{'eisei4'};
		    $eisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($sto, $std, $stk, $stwin, $stdrow, $stlose, $stwint, $stdrowt, $stloset, $styusho, $stshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);
		    $sto += int($sto * $avalue2 / 10);
		    $std += int($std * $avalue2 / 10);
		    $stk += int($stk * $avalue2 / 10);
		    $island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";

		    logMonsCome2($id, $name, $ac, $topvalue2);

		} elsif($shuppin2 == 23) {

		    $eisei5 = $island->{'eisei5'};
		    $eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tet) = ($1, $2, $3, $4, $5, $6, $7);
		    $msap += int($msap * $avalue2 / 10);
		    $msdp += int($msdp * $avalue2 / 10);
		    $mssp += int($mssp * $avalue2 / 10);
		    $island->{'eisei5'} = "$mshp,$msap,$msdp,$mssp,$mswin,$msexe,$tet";

		    logMonsCome2($id, $name, $ac, $topvalue2);

		} elsif($shuppin2 == 24) {

		    $eisei5 = $island->{'eisei5'};
		    $eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tet) = ($1, $2, $3, $4, $5, $6, $7);
		    $msexe += $avalue2;
		    $island->{'eisei5'} = "$mshp,$msap,$msdp,$mssp,$mswin,$msexe,$tet";

		    logMonsCome2($id, $name, $ac, $topvalue2);

		} else {

		    # どこに現れるか決める
		    my($bx, $by, $i);
		    for($i = 0; $i < $HpointNumber; $i++) {
			$bx = $Hrpx[$i];
			$by = $Hrpy[$i];
			if(($land->[$bx][$by] == $HlandPlains) ||
			   ($land->[$bx][$by] == $HlandPlains2)) {

				if($shuppin2 == 0) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 74;
				} elsif($shuppin2 == 1) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 75;
				} elsif($shuppin2 == 2) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 76;
				} elsif($shuppin2 == 3) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 77;
				} elsif($shuppin2 == 4) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 78;
				} elsif($shuppin2 == 5) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 79;
				} elsif($shuppin2 == 10) {
				    $land->[$bx][$by] = $HlandUmiamu;
				    $landValue->[$bx][$by] = $avalue2;
				} elsif($shuppin2 == 11) {
				    $land->[$bx][$by] = $HlandFoodim;
				    $landValue->[$bx][$by] = $avalue2;
				} elsif($shuppin2 == 12) {
				    $land->[$bx][$by] = $HlandEneCs;
				    $landValue->[$bx][$by] = $avalue2;
				} elsif($shuppin2 == 13) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 74;
				} elsif($shuppin2 == 16) {
				    $land->[$bx][$by] = $HlandConden3;
				    $landValue->[$bx][$by] = 0;
				} elsif($shuppin2 == 17) {
				    $land->[$bx][$by] = $HlandGold;
				    $landValue->[$bx][$by] = $avalue2;
				} elsif($shuppin2 == 18) {
				    $land->[$bx][$by] = $HlandNursery;
				    $landValue->[$bx][$by] = $avalue2;
				} elsif($shuppin2 == 25) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = $avalue2;
				} elsif($shuppin2 == 26) {
				    $land->[$bx][$by] = $HlandCollege;
				    $landValue->[$bx][$by] = 4;
				} elsif($shuppin2 == 27) {
				    $land->[$bx][$by] = $HlandEneWd;
				    $landValue->[$bx][$by] = $avalue2;
				} elsif($shuppin2 == 28) {
				    $land->[$bx][$by] = $HlandEneBo;
				    $landValue->[$bx][$by] = $avalue2;
				} elsif($shuppin2 == 30) {
				    my($tn) = $HidToNumber{$avalue2};
				    if($tn eq '') {

				    } else {
				    my($tIsland) = $Hislands[$tn];
				    my($tName) = $tIsland->{'name'};
				    my($tLand) = $tIsland->{'land'};
				    my($tLandValue) = $tIsland->{'landValue'};
					$tauc6 = $tIsland->{'auc6'};
					$tauc6 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
					($tauc6a, $tauc6x, $tauc6y) = ($1, $2, $3);
					$tIsland->{'auc6'} = "0,0,0";
				    my($tx, $ty);
					$tx = $tauc6x;
					$ty = $tauc6y;
				    my($tL) = $tLand->[$tx][$ty];
				    my($tLv) = $tLandValue->[$tx][$ty];
				    my($tLname) = landName($tL, $tLv);
					$island->{'stocklandkind'} = $tLand->[$tx][$ty];
					$island->{'stocklandvalue'} = $tLandValue->[$tx][$ty];
					$tLand->[$tx][$ty] = $HlandPlains;
					$tLandValue->[$tx][$ty] = 0;
					$land->[$bx][$by] = $island->{'stocklandkind'};
					$landValue->[$bx][$by] = $island->{'stocklandvalue'};

					$tauc9 = $tIsland->{'auc9'};
					$tauc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
					($tauc9a, $tauc9b, $tauc9c, $tauc9d, $tauc9e) = ($1, $2, $3, $4, $5);
					$tauc9c += $topvalue2*10000;
					$tauc9c2 = int($tauc9c/10000);
					$tauc9a = $tauc9b + $tauc9c2 + $tauc9d + $tauc9e;
					$tIsland->{'auc9'} = "$tauc9a,$tauc9b,$tauc9c,$tauc9d,$tauc9e";

					$island->{'auc8'} = "$tName島出品の$tLname";

					$aucland = $tL * $tLv;

						if($aucland != $topid2) {
							$tIsland->{'auc6'} = "77,0,0";
						}
				    }

				}

			    # メッセージ
			    logMonsCome2($id, $name, $ac, $topvalue2);
			    last;
			}
		    }
		}
	    }


	$auction3 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($shuppin3, $avalue3, $ajoutai3, $topvalue3, $topid3) = ($1, $2, $3, $4, $5);

	if(($island->{'auc3'} == $topvalue3) && ($topvalue3 != 0) && ($island->{'money'}+$auc9c3 < $topvalue3*10000) && ($auc4b != $aucshouhin)) {
	    $island->{'auc6'} = "7,0,0";
	}

	if((($island->{'auc3'} == $topvalue3) && ($topvalue3 != 0) && ($island->{'money'}+$auc9c3 > $topvalue3*10000)) || ($auc4b == $aucshouhin)) {

	    if($auc4b == $aucshouhin) {

		    $auc0 = $island->{'auc0'};
		    $auc0 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($auc0a, $auc0b, $auc0c, $auc0d, $auc0e) = ($1, $2, $3, $4, $5);
		    $shuppin3 = $auc0a;
		    $avalue3 = $auc0b;
		    $auc4c++;

		    $auc5 = $island->{'auc5'};
		    $auc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($auc5a, $auc5b, $auc5c, $auc5d, $auc5e) = ($1, $2, $3, $4, $5);

	    } else {

		    $shouhiauc9 = $auc9c2 - $topvalue3;

		    if($shouhiauc9 < 0) {
			$island->{'money'} -= ($topvalue3-$auc9c2)*10000;
			$auc9c2 = 0;
			$auc9c = $auc9c%10000;
			$auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
			$island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";
		    } else {
			$auc9c -= $topvalue3*10000;
			$auc9c2 = int($auc9c/10000);
			$auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;
			$island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";
		    }

		    if($shuppin3 != 30) {
			$auc6 = $island->{'auc6'};
			$auc6 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
			($auc6a, $auc6x, $auc6y) = ($1, $2, $3);
			$auc6a = 1;
			$island->{'auc6'} = "$auc6a,$auc6x,$auc6y";
		    }

		    $aucflag3 += $topvalue3;

		    $auc0 = $island->{'auc0'};
		    $auc0 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($auc0a, $auc0b, $auc0c, $auc0d, $auc0e) = ($1, $2, $3, $4, $5);
		    if($topvalue3 > $auc0c) {
		    $island->{'auc0'} = "$shuppin3,$avalue3,$topvalue3,$hcturn,$auc0e";
		    }

	    }

	    if($shuppin3 == 0) {
		    $ac = '闇石';
		} elsif($shuppin3 == 1) {
		    $ac = '地石';
		} elsif($shuppin3 == 2) {
		    $ac = '氷石';
		} elsif($shuppin3 == 3) {
		    $ac = '風石';
		} elsif($shuppin3 == 4) {
		    $ac = '炎石';
		} elsif($shuppin3 == 5) {
		    $ac = '光石';
		} elsif($shuppin3 == 6) {
		    $ac = '天使ミカエル';
		} elsif($shuppin3 == 7) {
		    $ac = 'アイススコーピオン';
		} elsif($shuppin3 == 8) {
		    $ac = 'スライムレジェンド';
		} elsif($shuppin3 == 9) {
		    $ac = "お守り$avalue3個";
		} elsif($shuppin3 == 10) {
		    $avalue3s = $avalue3 * 1000;
		    $ac = "海あみゅ$avalue3s人規模";
		} elsif($shuppin3 == 11) {
		    $avalue3s = $avalue3 * 1000;
		    $ac = "食研$avalue3s人規模";
		} elsif($shuppin3 == 12) {
		    $ac = "コスモ$avalue3万ｋＷ";
		} elsif($shuppin3 == 13) {
		    $ac = '闇石';
		} elsif($shuppin3 == 14) {
		    $ac = '衛星６種';
		} elsif($shuppin3 == 15) {
		    $ac = '宇宙ステーション';
		} elsif($shuppin3 == 16) {
		    $ac = '黄金のコンデンサ';
		} elsif($shuppin3 == 17) {
		    $avalue3s = $avalue3 * 1000;
		    $ac = "金山$avalue3s人規模";
		} elsif($shuppin3 == 18) {
		    $avalue3s = $avalue3 * 1000;
		    $ac = "養殖場$avalue3s人規模";
		} elsif($shuppin3 == 19) {
		    $ac = '人造怪獣f02';
		} elsif($shuppin3 == 20) {
		    $ac = '魔王サタン';
		} elsif($shuppin3 == 21) {
		    $ac = 'unknown';
		} elsif($shuppin3 == 22) {
		    $ac = "サッカーチーム力1.$avalue3倍";
		} elsif($shuppin3 == 23) {
		    $ac = "生物大学能力1.$avalue3倍";
		} elsif($shuppin3 == 24) {
		    $ac = "生物大学経験値$avalue3";
		} elsif($shuppin3 == 25) {
		    $ac = '卵';
		} elsif($shuppin3 == 26) {
		    $ac = '生物大学';
		} elsif($shuppin3 == 27) {
		    $ac = "風力$avalue3万ｋＷ";
		} elsif($shuppin3 == 28) {
		    $ac = "バイオマス$avalue3万ｋＷ";
		} elsif($shuppin3 == 29) {
		    $ac = '今回はお休み';
		} elsif($shuppin3 == 30) {
		    my($island, $j, $name, $id, $ii);
		    for($ii = 0; $ii < $HislandNumber; $ii++) {
			$j = $ii + 1;
			$island = $Hislands[$ii];
			$id = $island->{'id'};
				if($avalue3 == $island->{'id'}) {
				    $dashiname = $island->{'auc7'};
				}
			}
		    $ac = "$dashiname";
		} else {
		    $ac = '？';
		}

	    if(($shuppin3 == 6) || ($shuppin3 == 7) || ($shuppin3 == 8) || ($shuppin3 == 19) || ($shuppin3 == 20) || ($shuppin3 == 21)) {

		my($i,$sx,$sy);
		my($zlv) = (0);
		for($i = 0; $i < $HpointNumber; $i++){
		    $sx = $Hrpx[$i];
		    $sy = $Hrpy[$i];
			if($land->[$sx][$sy] == $HlandZoo){
			    $zlv += $landValue->[$sx][$sy];
			}
		}

		$etc6 = $island->{'etc6'};
		$etc6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		($z0,$z1,$z2,$z3,$z4,$z5,$z6,$z7,$z8,$z9,$z10,$z11,$z12,$z13,$z14,$z15,$z16,$z17,$z18,$z19,$z20,$z21,$z22,$z23,$z24,$z25,$z26,$z27,$z28,$z29,$z30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
		($z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

		$zookazu = $z0+$z1+$z2+$z3+$z4+$z5+$z6+$z7+$z8+$z9+$z10+$z11+$z12+$z13+$z14+$z15+$z16+$z17+$z18+$z19+$z20+$z21+$z22+$z23+$z24+$z25+$z26+$z27+$z28+$z29+$z30;

			if(($zlv > $zookazu) && ($island->{'zoo'} > 0)) {

				if($shuppin3 == 6) {
				    $ack = 13;
				} elsif($shuppin3 == 7) {
				    $ack = 22;
				} elsif($shuppin3 == 8) {
				    $ack = 14;
				} elsif($shuppin3 == 19) {
				    $ack = 17;
				} elsif($shuppin3 == 20) {
				    $ack = 21;
				} elsif($shuppin3 == 21) {
				    $ack = 23;
				}

				if($auc4b == $aucshouhin) {
				    logPrizeAuc2($id, $name, $ac, $topvalue3);
				    $island->{'auc4'} = "$auc4a,0,$auc4c";
					    if($auc4c >= $aucdendou) {
						if($auc0c > $auc5c) {
						    $island->{'auc5'} = "$auc0a,$auc0b,$auc0c,$auc0d,$auc4a";
						} else {
						    $island->{'auc5'} = "$auc5a,$auc5b,$auc5c,$auc5d,$auc5e";
						}
						$island->{'auc0'} = "0,0,0,0,11";
						$island->{'auc4'} = "0,0,0";
					    }
				} else {
				    logMonsCome2($id, $name, $ac, $topvalue3);
				}

				$z->{"$ack"}++;
				$island->{'etc6'} = "$z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}";

			}

		} elsif($shuppin3 == 9) {

		    $etc8 = $island->{'etc8'};
		    $etc8 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($toto1, $toto2, $toto3, $toto4, $toto5, $toto6, $toto7) = ($1, $2, $3, $4, $5, $6, $7);
		    $toto2 += $avalue3;
		    $island->{'etc8'} = "$toto1,$toto2,$toto3,$toto4,$toto5,$toto6,$toto7";

			if($auc4b == $aucshouhin) {
			    logPrizeAuc2($id, $name, $ac, $topvalue3);
			    $island->{'auc4'} = "$auc4a,0,$auc4c";
					    if($auc4c >= $aucdendou) {
						if($auc0c > $auc5c) {
						    $island->{'auc5'} = "$auc0a,$auc0b,$auc0c,$auc0d,$auc4a";
						} else {
						    $island->{'auc5'} = "$auc5a,$auc5b,$auc5c,$auc5d,$auc5e";
						}
						$island->{'auc0'} = "0,0,0,0,11";
						$island->{'auc4'} = "0,0,0";
					    }
			} else {
			    logMonsCome2($id, $name, $ac, $topvalue3);
			}

		} elsif($shuppin3 == 14) {

		    $island->{'eis1'} = 200;
		    $island->{'eis2'} = 200;
		    $island->{'eis3'} = 200;
		    $island->{'eis4'} = 200;
		    $island->{'eis5'} = 200;
		    $island->{'eis6'} = 200;

			if($auc4b == $aucshouhin) {
			    logPrizeAuc2($id, $name, $ac, $topvalue3);
			    $island->{'auc4'} = "$auc4a,0,$auc4c";
					    if($auc4c >= $aucdendou) {
						if($auc0c > $auc5c) {
						    $island->{'auc5'} = "$auc0a,$auc0b,$auc0c,$auc0d,$auc4a";
						} else {
						    $island->{'auc5'} = "$auc5a,$auc5b,$auc5c,$auc5d,$auc5e";
						}
						$island->{'auc0'} = "0,0,0,0,11";
						$island->{'auc4'} = "0,0,0";
					    }
			} else {
			    logMonsCome2($id, $name, $ac, $topvalue3);
			}

		} elsif($shuppin3 == 15) {

		    $island->{'eis7'} = 100099;

			if($auc4b == $aucshouhin) {
			    logPrizeAuc2($id, $name, $ac, $topvalue3);
			    $island->{'auc4'} = "$auc4a,0,$auc4c";
					    if($auc4c >= $aucdendou) {
						if($auc0c > $auc5c) {
						    $island->{'auc5'} = "$auc0a,$auc0b,$auc0c,$auc0d,$auc4a";
						} else {
						    $island->{'auc5'} = "$auc5a,$auc5b,$auc5c,$auc5d,$auc5e";
						}
						$island->{'auc0'} = "0,0,0,0,11";
						$island->{'auc4'} = "0,0,0";
					    }
			} else {
			    logMonsCome2($id, $name, $ac, $topvalue3);
			}

		} elsif($shuppin3 == 22) {

		    $eisei4 = $island->{'eisei4'};
		    $eisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($sto, $std, $stk, $stwin, $stdrow, $stlose, $stwint, $stdrowt, $stloset, $styusho, $stshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);
		    $sto += int($sto * $avalue3 / 10);
		    $std += int($std * $avalue3 / 10);
		    $stk += int($stk * $avalue3 / 10);
		    $island->{'eisei4'} = "$sto,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";

			if($auc4b == $aucshouhin) {
			    logPrizeAuc2($id, $name, $ac, $topvalue3);
			    $island->{'auc4'} = "$auc4a,0,$auc4c";
					    if($auc4c >= $aucdendou) {
						if($auc0c > $auc5c) {
						    $island->{'auc5'} = "$auc0a,$auc0b,$auc0c,$auc0d,$auc4a";
						} else {
						    $island->{'auc5'} = "$auc5a,$auc5b,$auc5c,$auc5d,$auc5e";
						}
						$island->{'auc0'} = "0,0,0,0,11";
						$island->{'auc4'} = "0,0,0";
					    }
			} else {
			    logMonsCome2($id, $name, $ac, $topvalue3);
			}

		} elsif($shuppin3 == 23) {

		    $eisei5 = $island->{'eisei5'};
		    $eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tet) = ($1, $2, $3, $4, $5, $6, $7);
		    $msap += int($msap * $avalue3 / 10);
		    $msdp += int($msdp * $avalue3 / 10);
		    $mssp += int($mssp * $avalue3 / 10);
		    $island->{'eisei5'} = "$mshp,$msap,$msdp,$mssp,$mswin,$msexe,$tet";

			if($auc4b == $aucshouhin) {
			    logPrizeAuc2($id, $name, $ac, $topvalue3);
			    $island->{'auc4'} = "$auc4a,0,$auc4c";
					    if($auc4c >= $aucdendou) {
						if($auc0c > $auc5c) {
						    $island->{'auc5'} = "$auc0a,$auc0b,$auc0c,$auc0d,$auc4a";
						} else {
						    $island->{'auc5'} = "$auc5a,$auc5b,$auc5c,$auc5d,$auc5e";
						}
						$island->{'auc0'} = "0,0,0,0,11";
						$island->{'auc4'} = "0,0,0";
					    }
			} else {
			    logMonsCome2($id, $name, $ac, $topvalue3);
			}

		} elsif($shuppin3 == 24) {

		    $eisei5 = $island->{'eisei5'};
		    $eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tet) = ($1, $2, $3, $4, $5, $6, $7);
		    $msexe += $avalue3;
		    $island->{'eisei5'} = "$mshp,$msap,$msdp,$mssp,$mswin,$msexe,$tet";

			if($auc4b == $aucshouhin) {
			    logPrizeAuc2($id, $name, $ac, $topvalue3);
			    $island->{'auc4'} = "$auc4a,0,$auc4c";
					    if($auc4c >= $aucdendou) {
						if($auc0c > $auc5c) {
						    $island->{'auc5'} = "$auc0a,$auc0b,$auc0c,$auc0d,$auc4a";
						} else {
						    $island->{'auc5'} = "$auc5a,$auc5b,$auc5c,$auc5d,$auc5e";
						}
						$island->{'auc0'} = "0,0,0,0,11";
						$island->{'auc4'} = "0,0,0";
					    }
			} else {
			    logMonsCome2($id, $name, $ac, $topvalue3);
			}

		} else {

		    # どこに現れるか決める
		    my($bx, $by, $i);
		    for($i = 0; $i < $HpointNumber; $i++) {
			$bx = $Hrpx[$i];
			$by = $Hrpy[$i];
			if(($land->[$bx][$by] == $HlandPlains) ||
			   ($land->[$bx][$by] == $HlandPlains2)) {

				if($shuppin3 == 0) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 74;
				} elsif($shuppin3 == 1) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 75;
				} elsif($shuppin3 == 2) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 76;
				} elsif($shuppin3 == 3) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 77;
				} elsif($shuppin3 == 4) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 78;
				} elsif($shuppin3 == 5) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 79;
				} elsif($shuppin3 == 10) {
				    $land->[$bx][$by] = $HlandUmiamu;
				    $landValue->[$bx][$by] = $avalue3;
				} elsif($shuppin3 == 11) {
				    $land->[$bx][$by] = $HlandFoodim;
				    $landValue->[$bx][$by] = $avalue3;
				} elsif($shuppin3 == 12) {
				    $land->[$bx][$by] = $HlandEneCs;
				    $landValue->[$bx][$by] = $avalue3;
				} elsif($shuppin3 == 13) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = 74;
				} elsif($shuppin3 == 16) {
				    $land->[$bx][$by] = $HlandConden3;
				    $landValue->[$bx][$by] = 0;
				} elsif($shuppin3 == 17) {
				    $land->[$bx][$by] = $HlandGold;
				    $landValue->[$bx][$by] = $avalue3;
				} elsif($shuppin3 == 18) {
				    $land->[$bx][$by] = $HlandNursery;
				    $landValue->[$bx][$by] = $avalue3;
				} elsif($shuppin3 == 25) {
				    $land->[$bx][$by] = $HlandMonument;
				    $landValue->[$bx][$by] = $avalue3;
				} elsif($shuppin3 == 26) {
				    $land->[$bx][$by] = $HlandCollege;
				    $landValue->[$bx][$by] = 4;
				} elsif($shuppin3 == 27) {
				    $land->[$bx][$by] = $HlandEneWd;
				    $landValue->[$bx][$by] = $avalue3;
				} elsif($shuppin3 == 28) {
				    $land->[$bx][$by] = $HlandEneBo;
				    $landValue->[$bx][$by] = $avalue3;
				} elsif(($shuppin3 == 30) && ($auc4b != $aucshouhin)) {
				    my($tn) = $HidToNumber{$avalue3};
				    if($tn eq '') {

				    } else {
				    my($tIsland) = $Hislands[$tn];
				    my($tName) = $tIsland->{'name'};
				    my($tLand) = $tIsland->{'land'};
				    my($tLandValue) = $tIsland->{'landValue'};
					$tauc6 = $tIsland->{'auc6'};
					$tauc6 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
					($tauc6a, $tauc6x, $tauc6y) = ($1, $2, $3);
					$tIsland->{'auc6'} = "0,0,0";
				    my($tx, $ty);
					$tx = $tauc6x;
					$ty = $tauc6y;
				    my($tL) = $tLand->[$tx][$ty];
				    my($tLv) = $tLandValue->[$tx][$ty];
				    my($tLname) = landName($tL, $tLv);
					$island->{'stocklandkind'} = $tLand->[$tx][$ty];
					$island->{'stocklandvalue'} = $tLandValue->[$tx][$ty];
					$tLand->[$tx][$ty] = $HlandPlains;
					$tLandValue->[$tx][$ty] = 0;
					$land->[$bx][$by] = $island->{'stocklandkind'};
					$landValue->[$bx][$by] = $island->{'stocklandvalue'};

					$tauc9 = $tIsland->{'auc9'};
					$tauc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
					($tauc9a, $tauc9b, $tauc9c, $tauc9d, $tauc9e) = ($1, $2, $3, $4, $5);
					$tauc9c += $topvalue3*10000;
					$tauc9c2 = int($tauc9c/10000);
					$tauc9a = $tauc9b + $tauc9c2 + $tauc9d + $tauc9e;
					$tIsland->{'auc9'} = "$tauc9a,$tauc9b,$tauc9c,$tauc9d,$tauc9e";

					$island->{'auc8'} = "$tName島出品の$tLname";

					$aucland = $tL * $tLv;

						if($aucland != $topid3) {
							$tIsland->{'auc6'} = "77,0,0";
						}
				    }

				} elsif(($shuppin3 == 30) && ($auc4b == $aucshouhin)) {
					$ac="なし";
				}

			    # メッセージ
				if($auc4b == $aucshouhin) {
				    logPrizeAuc2($id, $name, $ac, $topvalue3);
				    $island->{'auc4'} = "$auc4a,0,$auc4c";
					    if($auc4c >= $aucdendou) {
						if($auc0c > $auc5c) {
						    $island->{'auc5'} = "$auc0a,$auc0b,$auc0c,$auc0d,$auc4a";
						} else {
						    $island->{'auc5'} = "$auc5a,$auc5b,$auc5c,$auc5d,$auc5e";
						}
						$island->{'auc0'} = "0,0,0,0,11";
						$island->{'auc4'} = "0,0,0";
					    }
				} else {
				    logMonsCome2($id, $name, $ac, $topvalue3);
				}
			    last;
			}
		    }
		}
	    }

	$island->{'auc1'} = 0;
	$island->{'auc2'} = 0;
	$island->{'auc3'} = 0;

    }



    if($s01 > $s02) {$s02 += 1;}
    if($s02 > $s01+10) {$s02 -= 2;}
    if($s03 > $s04) {$s04 += 1;}
    if($s04 > $s03+5) {$s04 -= 3;}
    if($s05 > $s06) {$s06 += 2;}
    if($s06 > $s05+15) {$s06 -= 1;}
    if($s07 > $s08) {$s08 += 2;}
    if($s08 > $s07+20) {$s08 -= 1;}
    if($s09 > $s10) {$s10 += 5;}
    if($s10 > $s09+50) {$s10 -= 1;}
    if($s11 > $s12) {$s12 += 5;}
    if($s12 > $s11+1) {$s12 -= 5;}

    $island->{'money'} -= ($s01+$s03+$s05+$s07+$s09+$s11+$s13+$s15+$s17+$s19+$s21+$s23+$s25+$s27+$s29)*10000;

    $island->{'etc5'} = "$s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30";


    $s12b = int($s12/5)+1;
    if($s12b > 10) {$s12b = 10;}

    # 食料があふれてたら換金
    if($island->{'food'} > 99999*$s12b) {
	$island->{'money'} += int(($island->{'food'} - 99999*$s12b) / 10);
	$island->{'food'} = 99999*$s12b;
    } 

    # 収入チェック
    $island->{'pika'} = $island->{'money'} - $island->{'oldMoney'};

    # 金があふれてたら切り捨て
    if(($island->{'money'} > 999999*$s12b) && ($anothermood != 1)) {

        if($island->{'tai'} > 0) {
	$kifu = "";
	$kifukin = int(($island->{'money'}-999999*$s12b)/$island->{'tai'});
	my($x, $y, $landKind, $lv, $i);
	for($i = 0; $i < $HpointNumber; $i++) {
	    $x = $Hrpx[$i];
	    $y = $Hrpy[$i];
	    $landKind = $land->[$x][$y];
	    if($landKind == $HlandTaishi) {
		$ttlv = $landValue->[$x][$y];
		my($tn) = $HidToNumber{$ttlv};
			if($tn eq '') {
			    # ターゲットがすでにない
			    $land->[$x][$y] = $HlandPlains;
			    $landValue->[$x][$y] = 0;
			}else{
			my($tIsland) = $Hislands[$tn];
			my($tName) = $tIsland->{'name'};
			my($tLand) = $tIsland->{'land'};
			$tIsland->{'money'} += $kifukin;
			$kifu .= "$tName島、";
        	}
            }
        }
	logKifu($id, $tId, $name, $tName, $kifu, "$kifukin億円");
        }
	$island->{'money'} = 999999*$s12b;
    }


    $anotherkifu = 0;
    if(($anothermood == 1) && ($island->{'amarimoney'} > 0) && ($anotherkifu < 10)) {
        if($island->{'tai'} > 0) {
	$kifu = "";
	$kifukin = int($island->{'amarimoney'}/$island->{'tai'}/10);
	my($x, $y, $landKind, $lv, $i);
	for($i = 0; $i < $HpointNumber; $i++) {
	    $x = $Hrpx[$i];
	    $y = $Hrpy[$i];
	    $landKind = $land->[$x][$y];
	    if($landKind == $HlandTaishi) {
		$ttlv = $landValue->[$x][$y];
		my($tn) = $HidToNumber{$ttlv};
			if($tn eq '') {
			    # ターゲットがすでにない
			    $land->[$x][$y] = $HlandPlains;
			    $landValue->[$x][$y] = 0;
			}else{
			my($tIsland) = $Hislands[$tn];
			my($tName) = $tIsland->{'name'};
			my($tLand) = $tIsland->{'land'};
			$tIsland->{'money'} += $kifukin;
			$kifu .= "$tName島、";
        	}
            }
        }
	logKifu($id, $tId, $name, $tName, $kifu, "$kifukin億円");
	$anotherkifu++;
        }
    }


    # 各種の値を計算
    estimate($number);

    # 繁栄、災難賞
    $pop = $island->{'pop'};
    my($damage) = $island->{'oldPop'} - $pop;
    my($prize) = $island->{'prize'};
    $prize =~ /([0-9]*),([0-9]*),(.*)/;
    my($flags) = $1;
    my($monsters) = $2;
    my($turns) = $3;

    $island->{'hamu'} = $island->{'pop'} - $island->{'oldPop'};
    $island->{'monta'} = $island->{'pts'} - $island->{'oldPts'};

    # 繁栄賞
    if((!($flags & 1)) &&  $pop >= 3000){
	$flags |= 1;
	logPrize($id, $name, $Hprize[1]);
	    if($island->{'sin'} > 0) {
	    my($value, $str);
	    $value = random(3001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logSinMoney($id, $name, $str);
	    }
	    if($island->{'jin'} > 0) {
	    my($value, $str);
	    $value = random(3001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logJinMoney($id, $name, $str);
	    }
    } elsif((!($flags & 2)) &&  $pop >= 5000){
	$flags |= 2;
	logPrize($id, $name, $Hprize[2]);
	    if($island->{'sin'} > 0) {
	    my($value, $str);
	    $value = random(4001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logSinMoney($id, $name, $str);
	    }
	    if($island->{'jin'} > 0) {
	    my($value, $str);
	    $value = random(4001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logJinMoney($id, $name, $str);
	    }
    } elsif((!($flags & 4)) &&  $pop >= 10000){
	$flags |= 4;
	logPrize($id, $name, $Hprize[3]);
	    if($island->{'sin'} > 0) {
	    my($value, $str);
	    $value = random(5001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logSinMoney($id, $name, $str);
	    }
	    if($island->{'jin'} > 0) {
	    my($value, $str);
	    $value = random(5001);
	    $island->{'money'} += $value;
	    $str = "$value$HunitMoney";
	    # 収入ログ
	    logJinMoney($id, $name, $str);
	    }
    }

    # 災難賞
    if((!($flags & 64)) &&  $damage >= 500){
	$flags |= 64;
	logPrize($id, $name, $Hprize[7]);
    } elsif((!($flags & 128)) &&  $damage >= 1000){
	$flags |= 128;
	logPrize($id, $name, $Hprize[8]);
    } elsif((!($flags & 256)) &&  $damage >= 2000){
	$flags |= 256;
	logPrize($id, $name, $Hprize[9]);
    }

    $island->{'prize'} = "$flags,$monsters,$turns";
}


sub islandSortPop {
my($flag, $i, $tmp);

# 人口が同じときは直前のターンの順番のまま
my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'pop'} <=> $Hislands[$a]->{'pop'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}
sub islandSortFarm {
my($flag, $i, $tmp);

# 農業規模が同じときは直前のターンの順番のまま
my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'farm'} <=> $Hislands[$a]->{'farm'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}
sub islandSortFactory {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'factoryt'} <=> $Hislands[$a]->{'factoryt'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}
sub islandSortMountain {

my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'mountain'} <=> $Hislands[$a]->{'mountain'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}

sub islandSortMonument {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'kei'} <=> $Hislands[$a]->{'kei'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}
sub islandSortLive {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'monsterlive2'} <=> $Hislands[$a]->{'monsterlive2'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}
sub islandSortRena {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'rena'} <=> $Hislands[$a]->{'rena'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}
sub islandSortKill {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'taiji'} <=> $Hislands[$a]->{'taiji'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}
sub islandSortFore {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'fore'} <=> $Hislands[$a]->{'fore'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}

sub islandSortTare {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'tare'} <=> $Hislands[$a]->{'tare'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}
sub islandSortZipro {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'zipro'} <=> $Hislands[$a]->{'zipro'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}
sub islandSortLeje {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'leje'} <=> $Hislands[$a]->{'leje'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}

sub islandSortForce {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'force'} <=> $Hislands[$a]->{'force'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}

sub islandSortEisei2 {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'eisei2'} <=> $Hislands[$a]->{'eisei2'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}

sub islandSortUni {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'uni'} <=> $Hislands[$a]->{'uni'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}

sub islandSorthck {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'ene'} <=> $Hislands[$a]->{'ene'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}

sub islandSorthckt {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'etc0'} <=> $Hislands[$a]->{'etc0'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}

sub islandSorthcr {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'shoritu'} <=> $Hislands[$a]->{'shoritu'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}

sub islandSorthcy {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'styusho'} <=> $Hislands[$a]->{'styusho'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}

sub islandSorthct {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'teamforce'} <=> $Hislands[$a]->{'teamforce'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}


sub islandSortHC {
my($flag, $i, $tmp);
my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'kachiten'} <=> $Hislands[$a]->{'kachiten'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}

sub islandSortac4 {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'auc0c'} <=> $Hislands[$a]->{'auc0c'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}

# Point順にソート
sub islandSort {
    my($flag, $i, $tmp);

    # 人口が同じときは直前のターンの順番のまま
    my @idx = (0..$#Hislands);
    @idx = sort { $Hislands[$b]->{'pts'} <=> $Hislands[$a]->{'pts'} || $a <=> $b } @idx;
    @Hislands = @Hislands[@idx];
}

# 広域被害ルーチン
sub wideDamage {
    my($id, $name, $land, $landValue, $x, $y) = @_;
    my($sx, $sy, $i, $landKind, $landName, $lv, $point);

    for($i = 0; $i < 19; $i++) {
	$sx = $x + $ax[$i];
	$sy = $y + $ay[$i];

	# 行による位置調整
	if((($sy % 2) == 0) && (($y % 2) == 1)) {
	    $sx--;
	}
    
	$landKind = $land->[$sx][$sy];
	$lv = $landValue->[$sx][$sy];
	$landName = landName($landKind, $lv);
	$point = "($sx, $sy)";

	# 範囲外判定
	if(($sx < 0) || ($sx >= $HislandSize) ||
	   ($sy < 0) || ($sy >= $HislandSize)) {
	    next;
	}

	# 範囲による分岐
	if($i < 7) {
	    # 中心、および1ヘックス
	    if($landKind == $HlandSea) {
		$landValue->[$sx][$sy] = 0;
		next;
	    } elsif(($landKind == $HlandSbase) ||
		    ($landKind == $HlandSeacity) ||
		    ($landKind == $HlandSeatown) ||
		    ($landKind == $HlandUmishuto) ||
		    ($landKind == $HlandFune) ||
		    ($landKind == $HlandIce) ||
		    ($landKind == $HlandFrocity) ||
		    ($landKind == $HlandUmiamu) ||
		    ($landKind == $HlandOil)) {
		logWideDamageSea2($id, $name, $landName, $point);
		$land->[$sx][$sy] = $HlandSea;
		$landValue->[$sx][$sy] = 0;
	    } else {
		if($landKind == $HlandMonster) {
	            my($mKind, $mName, $mHp) = monsterSpec($lv);
			if((($mKind == 20)&&($i == 0))||(($mKind == 21)&&($i == 0))){next;}
		    logWideDamageMonsterSea($id, $name, $landName, $point);
		} else {
		    logWideDamageSea($id, $name, $landName, $point);
		}
		$land->[$sx][$sy] = $HlandSea;
		if($i == 0) {
		    # 海
		    $landValue->[$sx][$sy] = 0;
		} else {
		    # 浅瀬
		    $landValue->[$sx][$sy] = 1;
		}
	    }
	} else {
	    # 2ヘックス
	    if(($landKind == $HlandSea) ||
	       ($landKind == $HlandIce) ||
	       ($landKind == $HlandOil) ||
	       ($landKind == $HlandWaste) ||
	       ($landKind == $HlandMountain) ||
	       ($landKind == $HlandGold) ||
	       ($landKind == $HlandOnsen) ||
	       ($landKind == $HlandSeacity) ||
	       ($landKind == $HlandUmishuto) ||
	       ($landKind == $HlandSeatown) ||
	       ($landKind == $HlandFune) ||
	       ($landKind == $HlandFrocity) ||
	       ($landKind == $HlandUmiamu) ||
	       ($landKind == $HlandSbase)) {
		next;
	    } elsif($landKind == $HlandMonster) {
		logWideDamageMonster($id, $name, $landName, $point);
		$land->[$sx][$sy] = $HlandWaste;
		$landValue->[$sx][$sy] = 0;
	    } else {
		logWideDamageWaste($id, $name, $landName, $point);
		$land->[$sx][$sy] = $HlandWaste;
		$landValue->[$sx][$sy] = 0;
	    }
	}
    }
}

# 広域被害ルーチン・ミニ
sub wideDamageli {
my($target, $tName, $tLand, $tLandValue, $tx, $ty) = @_;
my($sx, $sy, $i, $landKind, $landName, $lv, $point);

for($i = 0; $i < 19; $i++) {
$sx = $tx + $ax[$i];
$sy = $ty + $ay[$i];

# 行による位置調整
if((($sy % 2) == 0) && (($ty % 2) == 1)) {
$sx--;
}

$landKind = $tLand->[$sx][$sy];
$lv = $tLandValue->[$sx][$sy];
$landName = landName($landKind, $lv);
$point = "($sx, $sy)";

# 範囲外判定
if(($sx < 0) || ($sx >= $HislandSize) ||
($sy < 0) || ($sy >= $HislandSize)) {
next;
}
if(($landKind == $HlandSea) ||
($landKind == $HlandOil) ||
($landKind == $HlandWaste) ||
($landKind == $HlandIce) ||
($landKind == $HlandSeacity) ||
($landKind == $HlandSeatown) ||
($landKind == $HlandUmishuto) ||
($landKind == $HlandFune) ||
($landKind == $HlandFrocity) ||
($landKind == $HlandUmiamu) ||
($landKind == $HlandSbase)) {
next;
} elsif($landKind == $HlandMonster) {
logWideDamageMonster($target, $tName, $landName, $point);
$tLand->[$sx][$sy] = $HlandWaste;
$tLandValue->[$sx][$sy] = 0;
} elsif($landKind == $HlandTown) {
logWideDamageWaste($target, $tName, $landName, $point);
$tLand->[$sx][$sy] = $HlandWaste;
$tLandValue->[$sx][$sy] = 0;
} else {
logWideDamageWaste($target, $tName, $landName, $point);
$tLand->[$sx][$sy] = $HlandWaste;
$tLandValue->[$sx][$sy] = 0;
}
}
}


# ログへの出力
# 第1引数:メッセージ
# 第2引数:当事者
# 第3引数:相手
# 通常ログ
sub logOut {
    push(@HlogPool,"0,$HislandTurn,$_[1],$_[2],$_[0]");
}

# 遅延ログ
sub logLate {
    push(@HlateLogPool,"0,$HislandTurn,$_[1],$_[2],$_[0]");
}

# 機密ログ
sub logSecret {
    push(@HsecretLogPool,"1,$HislandTurn,$_[1],$_[2],$_[0]");
}

# 記録ログ
sub logHistory {
    open(HOUT, ">>${HdirName}/hakojima.his");
    print HOUT "$HislandTurn,$_[0]\n";
    close(HOUT);
}

# 記録ログ調整
sub logHistoryTrim {
    open(HIN, "${HdirName}/hakojima.his");
    my(@line, $l, $count);
    $count = 0;
    while($l = <HIN>) {
	chomp($l);
	push(@line, $l);
	$count++;
    }
    close(HIN);

    if($count > $HhistoryMax) {
	open(HOUT, ">${HdirName}/hakojima.his");
	my($i);
	for($i = ($count - $HhistoryMax); $i < $count; $i++) {
	    print HOUT "$line[$i]\n";
	}
	close(HOUT);
    }
}

# Hakoniwa Cupログ
sub logHcup {
    open(COUT, ">>${HdirName}/hakojima.lhc");
    print COUT "$HislandTurn,$_[0]\n";
    close(COUT);
}

# Hakoniwa Cupログ調整
sub logHcupTrim {
    open(CIN, "${HdirName}/hakojima.lhc");
    my(@line, $l, $count);
    $count = 0;
    while($l = <CIN>) {
	chomp($l);
	push(@line, $l);
	$count++;
    }
    close(CIN);

    if($count > $HhcMax) {
	open(COUT, ">${HdirName}/hakojima.lhc");
	my($i);
	for($i = ($count - $HhcMax); $i < $count; $i++) {
	    print COUT "$line[$i]\n";
	}
	close(COUT);
    }
}

# Hakoniwa Auctionログ
sub logAuc {
    open(AOUT, ">>${HdirName}/hakojima.auc");
    print AOUT "$HislandTurn,$_[0]\n";
    close(AOUT);
}

# Hakoniwa Auctionログ調整
sub logAucTrim {
    open(AIN, "${HdirName}/hakojima.auc");
    my(@line, $l, $count);
    $count = 0;
    while($l = <AIN>) {
	chomp($l);
	push(@line, $l);
	$count++;
    }
    close(AIN);

    if($count > 10) {
	open(AOUT, ">${HdirName}/hakojima.auc");
	my($i);
	for($i = ($count - 10); $i < $count; $i++) {
	    print AOUT "$line[$i]\n";
	}
	close(AOUT);
    }
}

# ログ書き出し
sub logFlush {
    open(LOUT, ">${HdirName}/hakojima.log0");

    # 全部逆順にして書き出す
    my($i);
    for($i = $#HsecretLogPool; $i >= 0; $i--) {
	print LOUT $HsecretLogPool[$i];
	print LOUT "\n";
    }
    for($i = $#HlateLogPool; $i >= 0; $i--) {
	print LOUT $HlateLogPool[$i];
	print LOUT "\n";
    }
    for($i = $#HlogPool; $i >= 0; $i--) {
	print LOUT $HlogPool[$i];
	print LOUT "\n";
    }
    close(LOUT);
}

#----------------------------------------------------------------------
# ログテンプレート
#----------------------------------------------------------------------
# 資金足りない
sub logNoMoney {
    my($id, $name, $comName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}$comName${H_tagComName}は、資金不足のため中止されました。",$id);
}

sub logNoMoney2 {
    my($id, $name, $comName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}$comName${H_tagComName}は、条件不足のため中止されました。",$id);
}

# 食料足りない
sub logNoFood {
    my($id, $name, $comName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}$comName${H_tagComName}は、備蓄食料不足のため中止されました。",$id);
}

# 衛星ない
sub logNoEisei {
    my($id, $name, $comName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}$comName${H_tagComName}は、指定の人工衛星がないため中止されました。",$id);
}

# 衛星ない改
sub logNesEisei {
    my($id, $name, $comName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}$comName${H_tagComName}は、必要な人工衛星がないため中止されました。",$id);
}

# 許可されない
sub logForbidden {
    my($id, $name, $comName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}$comName${H_tagComName}は、実行が許可されませんでした。",$id);
}

# 箱庭連合軍
sub logNiwaren {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}は、<B>箱庭連合軍</B>に${HtagDisaster_}攻撃${H_tagDisaster}されました。",$id);
}

# 箱庭連合軍２
sub logNiwaren2 {
    my($id, $name, $comName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の${HtagComName_}$comName${H_tagComName}は、${HtagDisaster_}賠償金${H_tagDisaster}を支払うはめになりました。",$id);
}

# 箱庭連合軍３
sub logNiwaren3 {
    my($id, $name, $comName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}$comName${H_tagComName}は、<B>援助射撃の許可が取れてない</B>ため中止されました。",$id);
}

# 首都でき
sub logShuto {
    my($id, $name, $lName, $sName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は、<B>首都$sName</B>として島の中心的都市へとなりました。",$id);
    logHistory("${HtagName_}${name}島${H_tagName}に<B>首都$sName</B>が出来ました。");
END
}

# 対象地形の種類による失敗
sub logLandFail {
    my($id, $name, $comName, $kind, $point) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}$comName${H_tagComName}は、予定地の${HtagName_}$point${H_tagName}が<B>$kind</B>だったため中止されました。",$id);
END
}

# 対象地形の条件による失敗
sub logJoFail {
    my($id, $name, $comName, $kind, $point) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}$comName${H_tagComName}は、予定地の${HtagName_}$point${H_tagName}が条件を満たしていない<B>$kind</B>のため中止されました。",$id);
END
}

# 対象地形の条件による失敗2
sub logJo2Fail {
    my($id, $name, $comName, $kind, $point) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}$comName${H_tagComName}ですが、まずは、十分な治安を守るために<B>軍事力</B>を確保しましょう。",$id);
END
}

# 都市の種類による失敗
sub logBokuFail {
    my($id, $name, $comName, $kind, $point) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}$comName${H_tagComName}は、予定地の${HtagName_}$point${H_tagName}が条件を満たした都市でなかったため中止されました。",$id);
END
}

# 怪獣の拒否による失敗
sub logBokuFail2 {
    my($id, $name, $comName, $kind, $point) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}$comName${H_tagComName}は、予定地${HtagName_}$point${H_tagName}の<b>$kind</b>が嫌々をしたため中止されました。",$id);
END
}

# 周りに陸がなくて埋め立て失敗
sub logNoLandAround {
    my($id, $name, $comName, $point) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}$comName${H_tagComName}は、予定地の${HtagName_}$point${H_tagName}の周辺に陸地がなかったため中止されました。",$id);
END
}

# 周りに港がなくて船失敗
sub logNoLandAroundm {
    my($id, $name, $comName, $point) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}$comName${H_tagComName}は、予定地の${HtagName_}$point${H_tagName}の周辺に港町がなかったため中止されました。",$id);
END
}

# 周りに港がなくて船失敗
sub logNoLandArounde {
    my($id, $name, $comName, $point, $lName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}$comName${H_tagComName}は、予定地の${HtagName_}$point${H_tagName}の周辺に<B>$lName</B>がなかったため中止されました。",$id);
END
}

# 周りに町がなくて埋め立て失敗
sub logNoTownAround {
    my($id, $name, $comName, $point) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}$comName${H_tagComName}は、予定地の${HtagName_}$point${H_tagName}の周辺に人口がいなかったため中止されました。",$id);
END
}

# 整地系成功
sub logLandSuc {
    my($id, $name, $comName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}で${HtagComName_}${comName}${H_tagComName}が行われました。",$id);
END
}

# 整地系成功改
sub logLandSucmini {
    my($id, $name, $comName, $point) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で${HtagComName_}${comName}${H_tagComName}が行われました。",$id);
END
}

# 衛星失敗
sub logNoRoke {
    my($id, $name, $comName, $point) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}${comName}${H_tagComName}はロケットが足りないため中止されました。",$id);
END
}

# ステーション食料不足
sub logNoRokeCst {
    my($id, $name, $comName, $point) = @_;
    logOut("${HtagName_}${name}島${H_tagName}は${HtagDisaster_}ロケット不足${H_tagDisaster}により<B>宇宙ステーション</B>に食料が運べません！！",$id);
END
}

# 衛星失敗改
sub logNoTech {
    my($id, $name, $comName, $point) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}${comName}${H_tagComName}は軍事技術が足りないため中止されました。",$id);
END
}

# 衛星撃沈
sub logEiseifail {
    my($id, $name, $comName, $point) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で${HtagComName_}${comName}${H_tagComName}が行われましたが${HtagComName_}${comName}${H_tagComName}は${HtagDisaster_}失敗${H_tagDisaster}したようです。",$id);
END
}

# 油田発見
sub logOilFound {
    my($id, $name, $point, $comName, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}で<B>$str</B>の予算をつぎ込んだ${HtagComName_}${comName}${H_tagComName}が行われ、<B>油田が掘り当てられました</B>。",$id);
END
}

# 温泉発見
sub logHotFound {
    my($id, $name, $point, $comName, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}で<B>$str</B>の予算をつぎ込んだ${HtagComName_}${comName}${H_tagComName}が行われ、<B>温泉が掘り当てられました</B>。",$id);
END
}

# 油田発見ならず
sub logOilFail {
    my($id, $name, $point, $comName, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}で<B>$str</B>の予算をつぎ込んだ${HtagComName_}${comName}${H_tagComName}が行われましたが、油田は見つかりませんでした。",$id);
END
}

# 温泉発見ならず
sub logHotFail {
    my($id, $name, $point, $comName, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}で<B>$str</B>の予算をつぎ込んだ${HtagComName_}${comName}${H_tagComName}が行われましたが、温泉は見つかりませんでした。",$id);
END
}

# 油田からの収入
sub logOilMoney {
    my($id, $name, $lName, $point, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>から、<B>$str</B>の収益が上がりました。",$id);
END
}

# 油田からの収入
sub logOilMoney2 {
    my($id, $name, $lName, $point, $str, $str2) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>から、<B>$str</B>の収益が上がりました。(食料<B>$str2</B>消費)",$id);
END
}

# 神殿からの収入
sub logSinMoney {
    my($id, $name, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>神殿</B>で祝いの祭りが行われ、<B>$str</B>の収益が上がりました。",$id);
END
}

# 神社からの収入
sub logJinMoney {
    my($id, $name, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>神社</B>で祝いの祭りが行われ、<B>$str</B>の収益が上がりました。",$id);
END
}

# 油田枯渇
sub logOilEnd {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は枯渇したようです。",$id);
END
}

# 関所からの収入
sub logSekiMoney {
    my($id, $name, $lName, $point, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>から、<B>$str</B>の関税収益が上がりました。",$id);
END
}

# 金枯渇
sub logGoldEnd {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>から金が採れなくなったようです。",$id);
END
}
# 電車故障
sub logTrainEnd {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は故障したようです。",$id);
END
}
# 電車故障2
sub logTrainEnd2 {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は壊滅したようです。",$id);
END
}
# 遊園地からの収入
sub logParkMoney {
    my($id, $name, $str, $point, $lName) = @_;
    logOut("${HtagName_}${name}島の$pointヶ所${H_tagName}の<B>$lName</B>から、<B>合計$str</B>の収益が上がりました。",$id);
END
}

# 遊園地のイベント
sub logParkEvent {
    my($id, $name, $lName, $point, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>でイベントが開催され、<B>$str</B>の食料が消費されました。",$id);
END
}

# 遊園地が閉園
sub logParkEnd {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は施設が老朽化したため取り壊されました。",$id);
END
}

# 怪獣仕入れ
sub logSiire {
    my($id, $name, $lName, $mName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は<B>$mName</B>を入荷し話題をよんでいます。",$id);
END
}

# 保険からの収入
sub logHoken {
    my($id, $name, $lName, $point, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>の事故により、<B>$str</B>の保険がおりました。",$id);
END
}

# 土産からの収入
sub logMiyage {
    my($id, $name, $lName, $point, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName記念碑公園</B>のお土産屋さんから<B>$str</B>の収入がありました。",$id);
END
}

# Ｏ社からの収入
sub logMiyage2 {
    my($id, $name, $lName, $point, $dName) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName社</B>は、<B>$dName</B>を開発しました。",$id);
END
}

# Ｏ社からの収入
sub logMiyage2b {
    my($id, $name, $lName, $str, $dName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の<B>$lName社</B>が所有する<B>$dName</B>は爆発的に売れ、<B>$str</B>の経済効果をもたらしました。",$id);
END
}

# Ｏ社からの収入
sub logMiyage2c {
    my($id, $name, $lName, $str, $dName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の<B>$lName社</B>が所有する<B>$dName</B>は爆発的に売れ、<B>$str</B>の経済効果をもたらしました。ちなみに薬は売り切れました。",$id);
END
}

# 優勝からの収入
sub logYusho {
    my($id, $name, $lName, $point, $str) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の野球チームは${HtagName_}$point${H_tagName}の<B>$lName</B>で行われた箱庭リーグ決勝戦でみごと優勝し、<B>$str</B>の経済効果があがりました。",$id);
END
}

# 帆船からの収入
sub logParkMoneyf {
    my($id, $name, $lName, $point, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>から、<B>$str</B>の観光収入が上がりました。",$id);
END
}

# 帆船からの収入
sub logTitanicEnd {
    my($id, $name, $lName, $point, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>の沈没は映画化され、多くの人が涙を流しました。(<B>$str</B>の利益収入)",$id);
END
}

# 海底探索からの収入
sub logTansaku {
    my($id, $name, $lName, $point, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>が財宝を発見！<B>$str</B>の価値があることがわかりました。",$id);
END
}

# 海底探索の油田
sub logTansakuoil {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}で<B>$lName</B>が油田を発見！",$id);
END
}

# 援助金からの収入
sub logEnjo {
    my($id, $name, $lName, $point, $str) = @_;
    logOut("開発進行委員会から${HtagName_}${name}島${H_tagName}に<B>$str</B>の援助金が支給されたようです！",$id);
END
}

# 船、老朽化
sub logParkEndf {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は事故ため沈没しました。",$id);
END
}

# TITANIC撃沈
sub logTitanic {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は氷山に激突し真っ二つになり沈没しました。",$id);
END
}

# 幸運
sub logOilMoneyt {
    my($id, $name, $lName, $point, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>が落とした羽根に<B>$str</B>の値が付きました。",$id);
END
}

# 幸運２
sub logParkEventt {
    my($id, $name, $lName, $point, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>がもたらした豊作により、さらに<B>$str</B>の食料が出来ました。",$id);
END
}

# 船の収穫
sub logParkEventf {
    my($id, $name, $lName, $point, $str) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は、<B>$str</B>の食料を得ました。",$id);
END
}

# 防衛施設、自爆セット
sub logBombSet {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>の<B>自爆装置がセット</B>されました。",$id);
END
}

# 防衛施設、自爆作動
sub logBombFire {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>、${HtagDisaster_}自爆装置作動！！${H_tagDisaster}",$id);
END
}

# 大怪盗が侵入
sub logKuralupin {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>へ${HtagDisaster_}大怪盗が侵入したようです！！${H_tagDisaster}",$id);
END
}

# 記念碑、発射
sub logMonFly {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>が<B>轟音とともに飛び立ちました</B>。",$id);
END
}

# 記念碑、落下
sub logMonDamage {
    my($id, $name, $point) = @_;
    logOut("<B>何かとてつもないもの</B>が${HtagName_}${name}島$point${H_tagName}地点に落下しました！！",$id);
}

# 植林orミサイル基地
sub logPBSuc {
    my($id, $name, $comName, $point) = @_;
    logSecret("${HtagName_}${name}島$point${H_tagName}で${HtagComName_}${comName}${H_tagComName}が行われました。",$id);
    logOut("こころなしか、${HtagName_}${name}島${H_tagName}の<B>森</B>が増えたようです。",$id);
END
}

# ハリボテ
sub logHariSuc {
    my($id, $name, $comName, $comName2, $point) = @_;
    logSecret("${HtagName_}${name}島$point${H_tagName}で${HtagComName_}${comName}${H_tagComName}が行われました。",$id);
    logLandSuc($id, $name, $comName2, $point);
END
}

# ミサイル撃とうとした(or 怪獣派遣しようとした)がターゲットがいない
sub logMsNoTarget {
    my($id, $name, $comName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}${comName}${H_tagComName}は、目標の島に人が見当たらないため中止されました。",$id);
END
}

# ミサイル撃とうとした(or 怪獣派遣しようとした)が電力がいない
sub logMsNoEne {
    my($id, $name, $comName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}${comName}${H_tagComName}は、電力が不足しているのにと、島民が許しませんでした。",$id);
END
}

# ミサイル撃とうとした(or 怪獣派遣しようとした)が電力がいない
sub logMsNoEne2 {
    my($id, $name, $comName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた<B>捕獲グッツ使用</B>は、電力が不足する可能性があるため中止しました。",$id);
END
}

# ミサイル撃とうとした(or 怪獣派遣しようとした)が電力がいない
sub logMsNoEne3 {
    my($id, $name, $comName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}${comName}${H_tagComName}は出品権利がないため中止となりました。",$id);
END
}

# ミサイル撃とうとした(or 怪獣派遣しようとした)が電力がいない
sub logMsNoEne4 {
    my($id, $name, $comName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}${comName}${H_tagComName}は出品枠が空いてないため中止となりました。",$id);
END
}

# 魔術師撃とうとしたが魔法ガッこない
sub logMagicNoTarget {
    my($id, $name, $comName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}${comName}${H_tagComName}は、魔法学校がないため偽者を派遣してみました。",$id);
END
}

# ミサイル撃とうとしたが基地がない
sub logMsNoBase {
    my($id, $name, $comName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で予定されていた${HtagComName_}${comName}${H_tagComName}は、<B>ミサイル設備を保有していない</B>ために実行できませんでした。",$id);
END
}

# ミサイル撃ったが範囲外
sub logMsOut {
    my($id, $tId, $name, $tName, $comName, $point) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、<B>領域外の海</B>に落ちた模様です。",$id, $tId);
}

# 衛星破壊成功
sub logEiseiAtts {
    my($id, $tId, $name, $tName, $comName, $tEiseiname) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島${H_tagName}に向けて${HtagComName_}${comName}${H_tagComName}を行い、<B>$tEiseiname</B>に命中。<B>$tEiseiname</B>は跡形もなく消し飛びました。",$id, $tId);
}

# 宇宙ステーション破壊成功
sub logEiseiAttcst {
    my($id, $tId, $name, $tName, $comName, $tEiseiname, $tdmg) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島${H_tagName}に向けて${HtagComName_}${comName}${H_tagComName}を行い、<B>$tEiseiname</B>に命中。<B>$tdmg%</B>の損害を与えました。",$id, $tId);
}

# 衛星破壊失敗
sub logEiseiAttf {
    my($id, $tId, $name, $tName, $comName, $tEiseiname) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島${H_tagName}の<B>$tEiseiname</B>に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、何にも命中せず宇宙の彼方へと飛び去ってしまいました。。",$id, $tId);
}

# ステルスミサイル撃ったが範囲外
sub logMsOutS {
    my($id, $tId, $name, $tName, $comName, $point) = @_;
    logSecret("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、<B>領域外の海</B>に落ちた模様です。",$id, $tId);
    logLate("<B>何者か</B>が${HtagName_}${tName}島$point${H_tagName}へ向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、<B>領域外の海</B>に落ちた模様です。",$tId);
}

# ミサイル撃ったが防衛施設でキャッチ
sub logMsCaught {
    my($id, $tId, $name, $tName, $comName, $point, $tPoint) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}地点上空にて力場に捉えられ、<B>空中爆発</B>しました。",$id, $tId);
}

# ステルスミサイル撃ったが防衛施設でキャッチ
sub logMsCaughtS {
    my($id, $tId, $name, $tName, $comName, $point, $tPoint) = @_;
    logSecret("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}地点上空にて力場に捉えられ、<B>空中爆発</B>しました。",$id, $tId);
    logLate("<B>何者か</B>が${HtagName_}${tName}島$point${H_tagName}へ向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}地点上空にて力場に捉えられ、<B>空中爆発</B>しました。",$tId);
}

# ミサイル撃ったが防衛衛星でキャッチ
sub logMsCaughtE {
    my($id, $tId, $name, $tName, $comName, $point, $tPoint) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、<B>防衛衛星</B>に撃ち落とされました。",$id, $tId);
}

# ミサイル撃ったが効果なし
sub logMsNoDamage {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に落ちたので被害がありませんでした。",$id, $tId);
}

# ステルスミサイル撃ったが効果なし
sub logMsNoDamageS {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logSecret("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に落ちたので被害がありませんでした。",$id, $tId);

    logLate("<B>何者か</B>が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に落ちたので被害がありませんでした。",$tId);
}

# 陸地破壊弾、山に命中
sub logMsLDMountain {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に命中。<B>$tLname</B>は消し飛び、荒地と化しました。",$id, $tId);
}

# 陸地破壊弾、海底基地に命中
sub logMsLDSbase {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}$tPoint${H_tagName}に着水後爆発、同地点にあった<B>$tLname</B>は跡形もなく吹き飛びました。",$id, $tId);
}

# 陸地隆起弾、海底基地に命中
sub logMsLRSbase {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}$tPoint${H_tagName}に着水後爆発、同地点にあった<B>$tLname</B>は隆起して浅瀬になりました。",$id, $tId);
}

# 陸地破壊弾、怪獣に命中
sub logMsLDMonster {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}$tPoint${H_tagName}に着弾し爆発。陸地は<B>$tLname</B>もろとも水没しました。",$id, $tId);
}

# 陸地隆起弾、怪獣に命中
sub logMsLRMonster {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}$tPoint${H_tagName}に着弾し爆発。陸地は<B>$tLname</B>もろとも隆起し山が出来ました。",$id, $tId);
}

# 陸地破壊弾、浅瀬に命中
sub logMsLDSea1 {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に着弾。海底がえぐられました。",$id, $tId);
}

# 陸地隆起弾、浅瀬に命中
sub logMsLRSea1 {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に着弾。隆起し荒地となりました。",$id, $tId);
}

# 陸地破壊弾、その他の地形に命中
sub logMsLDLand {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に着弾。陸地は水没しました。",$id, $tId);
}

# 陸地隆起弾、その他の地形に命中
sub logMsLRLand {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に着弾。隆起し山が出来ました。",$id, $tId);
}

# 通常ミサイル、荒地に着弾
sub logMsWaste {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に落ちました。",$id, $tId);
}

# ステルスミサイル、荒地に着弾
sub logMsWasteS {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logSecret("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に落ちました。",$id, $tId);
    logLate("<B>何者か</B>が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に落ちました。",$tId);
}

# 核ミサイル、着弾
sub logMsSS {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に着弾し大爆発しました。",$id, $tId);
}

# 通常ミサイル、怪獣に命中、硬化中にて無傷
sub logMsMonNoDamage {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行い、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に命中、しかし硬化状態だったため効果がありませんでした。",$id, $tId);
}

# ステルスミサイル、怪獣に命中、硬化中にて無傷
sub logMsMonNoDamageS {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logSecret("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行い、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に命中、しかし硬化状態だったため効果がありませんでした。",$id, $tId);
    logOut("<B>何者か</B>が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行い、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に命中、しかし硬化状態だったため効果がありませんでした。",$tId);
}

# 通常ミサイル、怪獣に命中、殺傷
sub logMsMonKill {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に命中。<B>$tLname</B>は力尽き、倒れました。",$id, $tId);
}

# ステルスミサイル、怪獣に命中、殺傷
sub logMsMonKillS {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logSecret("${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に命中。<B>$tLname</B>は力尽き、倒れました。",$id, $tId);
    logLate("${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に命中。<B>$tLname</B>は力尽き、倒れました。", $tId);
}

# 通常ミサイル、怪獣に命中、ダメージ
sub logMsMonster {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行い、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に命中。<B>$tLname</B>は苦しそうに咆哮しました。",$id, $tId);
}

# ステルスミサイル、怪獣に命中、ダメージ
sub logMsMonsterS {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logSecret("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行い、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に命中。<B>$tLname</B>は苦しそうに咆哮しました。",$id, $tId);
    logLate("<B>何者か</B>が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行い、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に命中。<B>$tLname</B>は苦しそうに咆哮しました。",$tId);
}

# 怪獣の死体
sub logMsMonMoney {
    my($tId, $mName, $value) = @_;
    logOut("<B>$mName</B>の残骸には、<B>$value$HunitMoney</B>の値が付きました。",$tId);
}

# ミサイルまとめログ
sub logMsTotal {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint, $count, $mukou, $bouei, $kaijumukou, $kaijuhit, $fuhatu) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}$count発の${comName}${H_tagComName}を行いました。<br>${HtagNumber_}ターン${HislandTurn}${H_tagNumber}：${HtagName_}結果${H_tagName}⇒(無効$mukou発/防衛$bouei発/怪獣相殺$kaijumukou発/怪獣命中$kaijuhit発/不発弾$fuhatu発)",$id, $tId);
}

# ステルスミサイルまとめログ
sub logMsTotalS {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint, $count, $mukou, $bouei, $kaijumukou, $kaijuhit, $fuhatu) = @_;
    logSecret("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}$count発の${comName}${H_tagComName}を行いました。<br>${HtagNumber_}ターン${HislandTurn}${H_tagNumber}：${HtagName_}結果${H_tagName}⇒(無効$mukou発/防衛$bouei発/怪獣相殺$kaijumukou発/怪獣命中$kaijuhit発/不発弾$fuhatu発)",$id, $tId);
    logLate("<B>何者か</B>が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}$count発の${comName}${H_tagComName}を行いました。<br>${HtagNumber_}ターン${HislandTurn}${H_tagNumber}：${HtagName_}結果${H_tagName}⇒(無効$mukou発/防衛$bouei発/怪獣相殺$kaijumukou発/怪獣命中$kaijuhit発)",$id, $tId);
}

# 通常ミサイル通常地形に命中
sub logMsNormal {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に命中、一帯が壊滅しました。",$id, $tId);
}

# ステルスミサイル通常地形に命中
sub logMsNormalS {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logSecret("${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に命中、一帯が壊滅しました。",$id, $tId);
    logLate("${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に命中、一帯が壊滅しました。",$tId);
}

# ミサイル難民到着
sub logMsBoatPeople {
    my($id, $name, $achive) = @_;
    logOut("${HtagName_}${name}島${H_tagName}にどこからともなく<B>$achive${HunitPop}もの難民</B>が漂着しました。${HtagName_}${name}島${H_tagName}は快く受け入れたようです。",$id);
}

# ステルスミサイル、怪獣にたたき落とされる
sub logMsMonsCautS {
  my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
  logSecret("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>にたたき落とされました。",$id, $tId);
}

# 通常ミサイル、怪獣にたたき落とされる(ステルス以外)
sub logMsMonsCaut {
  my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
  logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>にたたき落とされました。",$id, $tId);
}

# ステルスミサイル、天使にたたき落とされる
sub logMsMonsCauttS {
  my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
  logSecret("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に打ち消されました。",$id, $tId);
}

# 通常ミサイル、天使にたたき落とされる(ステルス以外)
sub logMsMonsCautt {
  my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
  logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に打ち消されました。",$id, $tId);
}

# ステルスミサイル、スライムにたたき落とされる
sub logMsMonsCautlS {
  my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
  logSecret("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に飲み込まれました。",$id, $tId);
}

# 通常ミサイル、スライムにたたき落とされる(ステルス以外)
sub logMsMonsCautl {
  my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
  logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に飲み込まれました。",$id, $tId);
}

# ステルスミサイル、メカにたたき落とされる
sub logMsMonsCautmS {
  my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
  logSecret("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>による迎撃ミサイルに撃ち落されました。",$id, $tId);
}

# 通常ミサイル、メカにたたき落とされる(ステルス以外)
sub logMsMonsCautm {
  my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
  logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いましたが、${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>による迎撃ミサイルに撃ち落されました。",$id, $tId);
}

# 怪獣が攻撃する
sub logMonsAttack {
  my($id, $name, $mName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島$point${H_tagName}の<B>$mName</B>が${HtagName_}$tPoint${H_tagName}の<B>$tName</B>に向かって炎を吐きつけました。",$id, $tId);
}

# 天使が攻撃する
sub logMonsAttackt {
  my($id, $name, $mName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島$point${H_tagName}の<B>$mName</B>が${HtagName_}$tPoint${H_tagName}の<B>$tName</B>を攻撃しました。",$id, $tId);
}

# 首都を攻撃する
sub logMonsAttacks {
  my($id, $name, $lName, $point) = @_;
  logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は怪獣に${HtagDisaster_}攻撃${H_tagDisaster}され被害を受けました。",$id);
}

# 放射能漏れ
sub logAtAttacks {
  my($id, $name, $lName, $point) = @_;
  logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>での${HtagDisaster_}放射能漏れ${H_tagDisaster}が噂され、付近の住民への不安が広がってます。",$id);
}

# イレが攻撃する
sub logIreAttackt {
  my($id, $name, $mName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島${H_tagName}の<B>$mName</B>が${HtagName_}$tPoint${H_tagName}の<B>$tName</B>を攻撃し${HtagDisaster_}$point${H_tagDisaster}のダメージを与えました。",$id, $tId);
}

# 魔術師が攻撃する
sub logIreAttackt2 {
  my($id, $name, $mName, $maName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島${H_tagName}の<B>$mName</B>が引き起こした<B>$maName</B>は${HtagName_}$tPoint${H_tagName}の<B>$tName</B>に${HtagDisaster_}$point${H_tagDisaster}のダメージを与えました。",$id, $tId);
}

# 魔術師が攻撃する
sub logIreAttackt3 {
  my($id, $name, $mName, $maName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島${H_tagName}の<B>$mName</B>が引き起こした<B>$maName</B>は${HtagName_}$tPoint${H_tagName}の<B>$tName</B>を撃破！",$id, $tId);
}

# 魔術師が攻撃する
sub logIreAttackt4 {
  my($id, $name, $mName, $maName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島${H_tagName}の<B>$mName</B>が引き起こした<B>$maName</B>は${HtagDisaster_}$point${H_tagDisaster}ヶ所の<B>$tName</B>を$tPointました！",$id, $tId);
}

# 魔術師が攻撃する
sub logIreAttackt5 {
  my($id, $name, $mName, $maName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島${H_tagName}の<B>$mName</B>が持ってきた<B>$maName</B>は${HtagName_}$tPoint${H_tagName}の<B>$tName</B>をゲット！",$id, $tId);
}

# 魔術師が攻撃する
sub logIreAttackt6 {
  my($id, $name, $mName, $maName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島${H_tagName}の<B>$mName</B>が持ってきた<B>$maName</B>は${HtagName_}$tPoint${H_tagName}の<B>$tName</B>の捕獲に失敗！",$id, $tId);
}

# 魔術師が攻撃する
sub logIreAttackt7 {
  my($id, $name, $mName, $maName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島${H_tagName}の<B>$mName</B>が持ってきた<B>$maName</B>は${HtagName_}$tPoint${H_tagName}の<B>$tName</B>をゲット！できますが、動物園にはこれ以上入りません。",$id, $tId);
}

# マスコットが攻撃する
sub logMsAttackt {
  my($id, $name, $mName, $point, $cPoint, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島${H_tagName}の<B>$mName</B>が${HtagName_}$tPoint${H_tagName}の<B>$tName</B>を攻撃し${HtagDisaster_}$point${H_tagDisaster}のダメージを与え${HtagDisaster_}$cPoint${H_tagDisaster}のダメージを受けました。",$id, $tId);
}

# ミカエル像完成
sub logMsAttackmika {
  my($id, $name, $mName, $point, $cPoint, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島${H_tagName}の<B>$mName</B>と<B>$tName</B>の戦いは伝説となり、島民は<B>幸福の女神像</B>を建造しました。",$id, $tId);
}

# 攻撃で首はね
sub logItiAttack {
  my($id, $name, $mName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島$point${H_tagName}の<B>$mName</B>が${HtagName_}$tPoint${H_tagName}の<B>$tName</B>の首を刎ねました。",$id, $tId);
}

# 攻撃で首はね
sub logItiAttackms {
  my($id, $name, $mName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島$point${H_tagName}の<B>$mName</B>が${HtagName_}$tPoint${H_tagName}の<B>$tName</B>を斬りつけました。",$id, $tId);
}


# 氷で串刺し
sub logIceAttack {
  my($id, $name, $mName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島$point${H_tagName}の<B>$mName</B>の発する氷の矢は${HtagName_}$tPoint${H_tagName}の<B>$tName</B>の中心を貫きました。",$id, $tId);
}

# ヘルファイア
sub logHellAttack {
  my($id, $name, $mName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島$point${H_tagName}の<B>$mName</B>の呼び起こした地獄の炎は${HtagName_}$tPoint${H_tagName}の<B>$tName</B>を焼き尽くしました。",$id, $tId);
}

# 力場で怪獣あうち
sub logBariaAttack {
  my($id, $name, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島$tPoint${H_tagName}の<B>$tName</B>が<B>強力な力場</B>に押し潰されました。",$id, $tId);
}

# 新型軍艦が攻撃する
sub logFuneAttack {
  my($id, $name, $lName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>が多弾頭ミサイルを発射し、<B>$tName</B>に命中しました。",$id, $tId);
}

# 天空城が攻撃する
sub logFuneAttackSSS3 {
  my($id, $name, $lName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島${H_tagName}の<B>$lName</B>が<B>エネルギー砲</B>を発射し、${HtagName_}$tPoint${H_tagName}の<B>$tName</B>に命中。跡形もなく吹き飛びました。",$id, $tId);
}

# 新型軍艦が攻撃する
sub logFuneAttackSSS {
  my($id, $name, $lName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>が<B>エネルギー砲</B>を発射し、<B>$tName</B>に命中しました。",$id, $tId);
}

# 新型軍艦が攻撃する
sub logFuneAttackSSSR {
  my($id, $name, $lName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島${H_tagName}の<B>$tName</B>は<B>木っ端微塵</B>になりました。",$id, $tId);
}

# 新型軍艦が攻撃する
sub logFuneAttackSSST {
  my($id, $name, $lName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島${H_tagName}の<B>$tName</B>は<B>木っ端微塵</B>になり、<B>$lName</B>は${HtagDisaster_}オーバーヒート${H_tagDisaster}により${HtagDisaster_}大爆発${H_tagDisaster}しました。",$id, $tId);
}

# 怪獣瞬殺
sub logFuneMonsterSea {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は吹き飛び水没しました。",$id);
}

# 卵孵化
sub logEggBomb {
    my($id, $name, $lName, $mName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>から<B>$mName</B>が出現しました。",$id);
}

# 魔法メテオ
sub logMgMeteo {
    my($id, $name, $mName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$mName</B>は${HtagDisaster_}禁呪メテオ${H_tagDisaster}を唱えました。",$id);
}

# 魔法クエイク
sub logMgEarthquake {
    my($id, $name, $mName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$mName</B>は${HtagDisaster_}クエイク${H_tagDisaster}を唱えました。",$id);
}

# 魔法ドレイン
sub logMgDrain {
    my($id, $name, $mName, $tName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$mName</B>は<B>$tName</B>に対して${HtagDisaster_}ドレイン${H_tagDisaster}を唱えました。",$id);
}

# 召喚
sub logShoukan {
my($id, $name, $nName, $mName, $point) = @_;
logOut("<B>$nName</B>は${HtagName_}${name}島$point${H_tagName}に<B>$mName</B>を${HtagDisaster_}召喚${H_tagDisaster}しました。",$id);
}

# 召喚
sub logNige {
my($id, $name, $lName, $mName, $point) = @_;
logOut("${HtagName_}${name}島$point${H_tagName}の<B>動物園</B>から<B>$mName</B>が${HtagDisaster_}脱走${H_tagDisaster}しました。",$id);
}

# 召喚
sub logNige2 {
my($id, $name, $lName, $mName, $point) = @_;
logOut("${HtagName_}${name}島$point${H_tagName}の<B>動物園</B>から<B>$mName</B>を${HtagDisaster_}脱走${H_tagDisaster}させました。",$id);
}

# 大恐慌
sub logKyoukou {
    my($id, $name, $mName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$mName</B>は${HtagName_}${name}島${H_tagName}に${HtagDisaster_}大恐慌${H_tagDisaster}をもたらしました。",$id);
}

# 腐食
sub logFushoku {
    my($id, $name, $mName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$mName</B>は${HtagName_}${name}島${H_tagName}の蓄えていた<B>食料</B>を${HtagDisaster_}腐敗${H_tagDisaster}させてしまったようです。",$id);
}

# big迎撃？！
sub logEiseiBigcome {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の<B>迎撃衛星</B>は${HtagName_}${name}島${H_tagName}に向かってくる${HtagDisaster_}巨大隕石${H_tagDisaster}を撃ち落としたようです！！",$id);
}

# 迎撃？！
sub logEiseicome {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の<B>迎撃衛星</B>は${HtagName_}${name}島${H_tagName}に向かってくる${HtagDisaster_}隕石${H_tagDisaster}を撃ち落としたようです！！",$id);
}

# 衛星消滅？！
sub logEiseiEnd {
    my($id, $name, $tEiseiname) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の<B>$tEiseiname</B>は${HtagDisaster_}崩壊${H_tagDisaster}したようです！！",$id);
}

# 衛星消滅２？！
sub logEiseiEndNopop {
    my($id, $name, $tEiseiname) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の<B>$tEiseiname</B>は${HtagDisaster_}人がいなくなった${H_tagDisaster}ようです！！",$id);
}

# 封印解除
sub logUmlimit {
    my($id, $name, $mName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$mName</B>の<B>封印</B>が${HtagDisaster_}解除${H_tagDisaster}してしまったようです。",$id);
}

# 封印解除被害
sub logUmlimitDamage {
    my($id, $name, $mName, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は<B>$mName</B>の${HtagDisaster_}解放されたエネルギー${H_tagDisaster}により壊滅しました。",$id);
}

# 卵解除被害
sub logEggDamage {
    my($id, $name, $landName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$landName</B>は${HtagDisaster_}卵の破裂によるエネルギー${H_tagDisaster}により水没しました。",$id);
}

# ウリエルのコメット〜
sub logUrieruMeteo {
  my($id, $name, $lName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>が引き寄せた${HtagDisaster_}小隕石${H_tagDisaster}が${HtagName_}$tPoint${H_tagName}の<B>$tName</B>に落下し一帯が壊滅しました。",$id, $tId);
}

# メカのミサイル
sub logMekaNmiss {
  my($id, $name, $lName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>が発射したミサイルが${HtagName_}$tPoint${H_tagName}の<B>$tName</B>に着弾し一帯が壊滅しました。",$id, $tId);
}

# メカのダメージなし
sub logMekaNdamage {
  my($id, $name, $lName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>が発射したミサイルが${HtagName_}$tPoint${H_tagName}の<B>$tName</B>に着弾しました。",$id, $tId);
}

# メカの多弾頭
sub logMekaSmiss {
  my($id, $name, $lName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>が発射した${HtagDisaster_}多弾頭ミサイル${H_tagDisaster}が${HtagName_}$tPoint${H_tagName}の<B>$tName</B>に着弾しました。",$id, $tId);
}

# メカのアトミックボム
sub logMekaAB {
  my($id, $name, $lName, $point, $tName, $tPoint) = @_;
  logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>が発射した${HtagDisaster_}アトミック☆ボム${H_tagDisaster}が${HtagName_}$tPoint${H_tagName}の<B>$tName</B>に着弾し大爆発しました。",$id, $tId);
}

# 腐海が生まれた
sub logRottenSeaBorn {
    my($id, $name, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}に<B>王蟲</B>から<B>腐海</B>が生まれました。",$id);
}

# 腐海に飲み込まれた
sub logRottenSeaGrow {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は<B>腐海</B>に飲み込まれました。",$id);
}

# いのら出撃
sub logMstakeon {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は<B>怪獣退治</B>に向かいました。",$id);
}

# いのら帰宅
sub logMstakeokaeri {
    my($id, $name, $lName, $point, $tName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の<B>$lName</B>が${HtagName_}$point${H_tagName}の<B>$tName</B>に帰ってきました。おつかれさま。",$id);
}

# いのら家出
sub logMstakeiede {
    my($id, $name, $lName, $point, $tName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の<B>$lName</B>は帰るべき家がないために旅に出ました。",$id);
}

# いのら行方不明
sub logMstakeoff {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は<B>マスコットいのら</B>損失のため運営困難になりました。",$id);
}

# 吸収合併
sub logOwnFac {
    my($id, $name, $lName, $point, $sName) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は周囲の施設を吸収し、<B>$sName社</B>となりました。",$id);
}

# 吸収合併2
sub logOwnFac2 {
    my($id, $name, $lName, $lName2, $point, $sName) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$sName社</B>は<B>$lName2</B>を吸収合併しました。",$id);
}

# 脱皮してみた
sub logNuginugi {
    my($id, $name, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}に<B>王蟲</B>が脱皮しました。",$id);
}

# 陸地破壊弾、腐海に命中
sub logMsLDSeaRotten {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に着弾。腐海は海に沈みました。",$id, $tId);
}

# 陸地隆起弾、腐海に命中
sub logMsLRSeaRotten {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に着弾。腐海は隆起し山になりました。",$id, $tId);
}

# ステルスミサイル腐海に命中
sub logMsNormalSRotten {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logSecret("${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に命中、腐海は焼き払われました。",$id, $tId);
    logLate("{HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に命中、腐海は焼き払われました。",$tId);
}

# 通常ミサイル腐海に命中
sub logMsNormalRotten {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}$tPoint${H_tagName}の<B>$tLname</B>に命中、腐海は焼き払われました。",$id, $tId);
}

# レーザー命中
sub logLzrhit {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行い、<B>$tLname</B>に命中、<B>$tLname</B>は焼き払われました。",$id, $tId);
}

# レーザー命中でも、、
sub logLzrefc {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行い、<B>$tLname</B>に命中、<B>$tLname</B>は暖かくなりました。",$id, $tId);
}

# 大使館でも、、
sub logTaishi {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${comName}${H_tagComName}を行いました。",$id, $tId);
}

# 魔術師、、
sub logTaishi2 {
    my($id, $tId, $name, $tName, $comName, $tLname, $point, $tPoint, $magickind) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島$point${H_tagName}地点に向けて${HtagComName_}${magickind}${H_tagComName}を行いました。",$id, $tId);
}

# 大使館でも、、
sub logKifu {
    my($id, $tId, $name, $tName, $kifu, $kifukin) = @_;
    logOut("${HtagName_}${name}島${H_tagName}は持ちきれなかった<B>$kifukin</B>を${HtagName_}$kifu大使館${H_tagName}に寄付しました。",$id, $tId);
}

# 怪獣派遣
sub logMonsSend {
    my($id, $tId, $name, $tName, $mName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が<B>$mName</B>を脱走させ、${HtagName_}${tName}島${H_tagName}へ送りこみました。",$id, $tId);
}

# 怪獣派遣
sub logMonsSend2 {
    my($id, $tId, $name, $tName, $mName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の<B>$mName</B>は、${HtagName_}${tName}島${H_tagName}へ派遣されました。",$id, $tId);
}

# 資金繰り
sub logDoNothing {
    my($id, $name, $comName) = @_;
#    logOut("${HtagName_}${name}島${H_tagName}で${HtagComName_}${comName}${H_tagComName}が行われました。",$id);
}

# 輸出
sub logSell {
    my($id, $name, $comName, $value) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が<B>$value$HunitFood</B>の${HtagComName_}${comName}${H_tagComName}を行いました。",$id);
}

# 援助
sub logAid {
    my($id, $tId, $name, $tName, $comName, $str) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が${HtagName_}${tName}島${H_tagName}へ<B>$str</B>の${HtagComName_}${comName}${H_tagComName}を行いました。",$id, $tId);
}

# 誘致活動
sub logPropaganda {
    my($id, $name, $comName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で${HtagComName_}${comName}${H_tagComName}が行われました。",$id);
}

# 放棄
sub logGiveup {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}は放棄され、<B>無人島</B>になりました。",$id);
    logHistory("${HtagName_}${name}島${H_tagName}、放棄され<B>無人島</B>となる。");
}

# 死滅
sub logDead {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}から人がいなくなり、<B>無人島</B>になりました。",$id);
    logHistory("${HtagName_}${name}島${H_tagName}、人がいなくなり<B>無人島</B>となる。");
}

# 発見
sub logDiscover {
    my($name) = @_;
    logHistory("${HtagName_}${name}島${H_tagName}が発見される。");
}

# 名前の変更
sub logChangeName {
    my($name1, $name2) = @_;
    logHistory("${HtagName_}${name1}島${H_tagName}、名称を${HtagName_}${name2}島${H_tagName}に変更する。");
}

# 飢餓
sub logStarve {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の${HtagDisaster_}食料が不足${H_tagDisaster}しています！！",$id);
}

# 電力飢餓
sub logStarve2 {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の${HtagDisaster_}電力が不足${H_tagDisaster}しています！！",$id);
}

# 電力飢餓電車
sub logStarve3 {
    my($id, $name, $tname, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$tname</B>は${HtagDisaster_}電力不足${H_tagDisaster}により停止しました！！",$id);
}

# 重税逆ギレ
sub logKire {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の<B>重税</B>に島民は${HtagDisaster_}キレ${H_tagDisaster}ました！！",$id);
}

# 副作用？！
sub logStarvefood {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の<B>遺伝子組換え食物</B>に${HtagDisaster_}副作用${H_tagDisaster}があったようです！！",$id);
}

# 不景気？！
sub logFukeiki {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}は${HtagDisaster_}不景気${H_tagDisaster}により成長が停滞気味のようです！！",$id);
}

# 胞子？！
sub logRotsick {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の<B>腐海</B>が生み出した<B>胞子</B>は${HtagName_}${name}島${H_tagName}に${HtagDisaster_}疫病${H_tagDisaster}をもたらしたようです！！",$id);
}

# 疫病？！
sub logSatansick {
    my($id, $name) = @_;
    logOut("<B>魔王サタン</B>は${HtagName_}${name}島${H_tagName}の<B>食料</B>を${HtagDisaster_}腐敗${H_tagDisaster}させ、${HtagName_}${name}島${H_tagName}では${HtagDisaster_}疫病${H_tagDisaster}が流行っているようです！！",$id);
}

# 怪獣現る
sub logMonsCome {
    my($id, $name, $mName, $point, $lName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}に<B>$mName</B>出現！！${HtagName_}$point${H_tagName}の<B>$lName</B>が踏み荒らされました。",$id);
}

# 怪獣現る
sub logMonsCome2 {
    $hcturn = int($HislandTurn/100)*100;
    my($id, $name, $ac, $topvalue) = @_;
    logAuc("${HtagName_}${name}島様${H_tagName}、<B>Hakoniwa Auction$hcturn </B>にて<FONT COLOR=\"MEDIUMSEAGREEN\"><B>$ac</B></font>を<B>$topvalue兆円</B>でお買い上げありがとうございます。",$id);
}

# 怪獣現る
sub logPrizeAuc2 {
    my($id, $name, $ac, $topvalue) = @_;
    logAuc("${HtagName_}${name}島様${H_tagName}、<FONT COLOR=\"royalblue\"><B>$aucshouhin連続ランキング１位！</B></font>（賞品 <FONT COLOR=\"MEDIUMSEAGREEN\"><B>$ac</B></font>)",$id);
}

# 怪獣現る
sub logPrizeAuc {
    $hcturn = int($HislandTurn/100)*100;
    my($id, $name, $pName, $value) = @_;
    logAuc("${HtagName_}${name}島様${H_tagName}、<B>Hakoniwa Auction$hcturn 高額落札ランキング１位！</B>（賞金<B>$value</B>)",$id);
}

# 怪獣現る(魔方陣)
sub logMonsComemagic {
    my($id, $name, $mName, $point, $lName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}の破壊された<B>魔方陣</B>から<B>$mName</B>出現！！",$id);
}

# 怪獣放つ
sub logMonsFree {
    my($id, $name, $mName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}で<B>$mName</B>を購入・放置しました。",$id);
}

# 怪獣動く
sub logMonsMove {
    my($id, $name, $lName, $point, $mName) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>が<B>$mName</B>に踏み荒らされました。",$id);
}

# スライムが分裂した
sub lognewMonsterBorn {
my($id, $name, $point) = @_;
logOut("${HtagName_}${name}島$point${H_tagName}に<B>スライム</B>が分裂しました。",$id);
}

# 助け呼んだ
sub lognewKaiju {
my($id, $name, $mName, $point) = @_;
logOut("${HtagName_}${name}島$point${H_tagName}に<B>$mName</B>が助けに来ました。",$id);
}

# 怪獣、自爆です
sub logMonsBomb {
    my($id, $name, $lName, $point, $mName) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$mName</B>が${HtagDisaster_}メルトダウン${H_tagDisaster}を起こし自爆しました。",$id);
}

# 怪獣、周囲を焼き尽くす
sub logMonsFire {
    my($id, $name, $lName, $point, $mName) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>が<B>$mName</B>による衝撃波で壊滅しました。",$id);
}

# コンデンサあっぷ
sub logConsFire {
    my($id, $name, $lName, $point, $comName) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は${HtagComName_}$comName${H_tagComName}で余った黄金によりメッキが施されました。",$id);
}

# 怪獣、周囲を凍て尽くす
sub logMonsCold {
    my($id, $name, $lName, $point, $mName) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は<B>$mName</B>を取り巻く冷気により凍てつきました。",$id);
}

# 怪獣、防衛施設を踏む
sub logMonsMoveDefence {
    my($id, $name, $lName, $point, $mName) = @_;
    logOut("<B>$mName</B>が${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>へ到達、<B>${lName}の自爆装置が作動！！</B>",$id);
}

# 怪獣、地雷を踏んで死亡、死体なし
sub logMonsMineKill {
    my($id, $name, $lName, $point, $mName) = @_;
    logOut("<B>怪獣$mName</B>が${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>を踏んで爆発、<B>怪獣$mName</B>は消し飛びました。",$id);
}

# 怪獣、地雷を踏んで死亡、死体あり
sub logMonsMineDead {
    my($id, $name, $lName, $point, $mName) = @_;
    logOut("<B>怪獣$mName</B>が${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>を踏んで爆発、<B>怪獣$mName</B>は力尽き、倒れました。",$id);
}

# 怪獣、地雷を踏んでダメージ
sub logMonsMineHit {
    my($id, $name, $lName, $point, $mName) = @_;
    logOut("<B>怪獣$mName</B>が${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>を踏んで爆発、<B>怪獣$mName</B>は苦しそうに咆哮しました。",$id);
}

# 火災
sub logFire {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>が${HtagDisaster_}火災${H_tagDisaster}により壊滅しました。",$id);
}
# 漏電
sub logRouden {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は${HtagDisaster_}漏電${H_tagDisaster}をしているようです。",$id);
}
# 漏電2
sub logRouden2 {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は${HtagDisaster_}エネルギーバランスが不均衡${H_tagDisaster}になっているようです。",$id);
}
# 火災未遂
sub logFirenot {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>が${HtagDisaster_}火災${H_tagDisaster}により被害を受けました。",$id);
}

# 埋蔵金
sub logMaizo {
    my($id, $name, $comName, $value) = @_;
    logOut("${HtagName_}${name}島${H_tagName}での${HtagComName_}$comName${H_tagComName}中に、<B>$value$HunitMoneyもの埋蔵金</B>が発見されました。",$id);
}

# 金塊
sub logGold {
    my($id, $name, $comName, $value) = @_;
    logOut("${HtagName_}${name}島${H_tagName}での${HtagComName_}$comName${H_tagComName}中に、<B>金塊</B>が発見され<B>$value$HunitMoney</B>の利益があがりました。",$id);
}

# 卵
sub logEggFound {
    my($id, $name, $comName, $value) = @_;
    logOut("${HtagName_}${name}島${H_tagName}での${HtagComName_}$comName${H_tagComName}中に、<B>何かの卵</B>が発見され${HtagComName_}$comName業者${H_tagComName}には破壊が無理なので放置することにしました。",$id);
}

# 遺跡
sub logIsekiFound {
    my($id, $name, $comName, $value) = @_;
    logOut("${HtagName_}${name}島${H_tagName}での${HtagComName_}$comName${H_tagComName}中に、<B>古代遺跡</B>が発見され<B>島の重要埋蔵文化財</B>に指定されました。",$id);
}

# 地震発生
sub logEarthquake {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で大規模な${HtagDisaster_}地震${H_tagDisaster}が発生！！",$id);
}

# お守り
sub logOmamori {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}所有の<B>お守り</B>のお陰でしょうか、${HtagDisaster_}被害${H_tagDisaster}が少なかったようです！！",$id);
}

# 魔塔バリア
sub logOmamori2 {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}を取り巻く<B>バリア</B>のお陰で${HtagDisaster_}被害${H_tagDisaster}が少なかったようです！！",$id);
}

# 地震被害
sub logEQDamage {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は${HtagDisaster_}地震${H_tagDisaster}により壊滅しました。",$id);
}

# 地震被害未遂
sub logEQDamagenot {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は${HtagDisaster_}地震${H_tagDisaster}により被害を受けました。",$id);
}

# 食料不足被害
sub logSvDamage {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>に<B>食料を求めて住民が殺到</B>。<B>$lName</B>は壊滅しました。",$id);
}

# 重税被害
sub logKireDamage {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は${HtagDisaster_}暴れる島民${H_tagDisaster}によって${HtagDisaster_}破壊${H_tagDisaster}されました。",$id);
}

# 津波発生
sub logTsunami {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}付近で${HtagDisaster_}津波${H_tagDisaster}発生！！",$id);
}

# 津波被害
sub logTsunamiDamage {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は${HtagDisaster_}津波${H_tagDisaster}により崩壊しました。",$id);
}

# 台風発生
sub logTyphoon {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}に${HtagDisaster_}台風${H_tagDisaster}上陸！！",$id);
}

# 台風被害
sub logTyphoonDamage {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は${HtagDisaster_}台風${H_tagDisaster}で飛ばされました。",$id);
}

# 台風被害・船
sub logTyphoonHason {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は${HtagDisaster_}台風${H_tagDisaster}によって破損しました。",$id);
}

# 隕石、海
sub logMeteoSea {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>に${HtagDisaster_}隕石${H_tagDisaster}が落下しました。",$id);
}

# 隕石、山
sub logMeteoMountain {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>に${HtagDisaster_}隕石${H_tagDisaster}が落下、<B>$lName</B>は消し飛びました。",$id);
}

# 隕石、海底基地
sub logMeteoSbase {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>に${HtagDisaster_}隕石${H_tagDisaster}が落下、<B>$lName</B>は崩壊しました。",$id);
}

# 隕石、怪獣
sub logMeteoMonster {
    my($id, $name, $lName, $point) = @_;
    logOut("<B>$lName</B>がいた${HtagName_}${name}島$point${H_tagName}地点に${HtagDisaster_}隕石${H_tagDisaster}が落下、陸地は<B>$lName</B>もろとも水没しました。",$id);
}

# 隕石、浅瀬
sub logMeteoSea1 {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}地点に${HtagDisaster_}隕石${H_tagDisaster}が落下、海底がえぐられました。",$id);
}

# 隕石、その他
sub logMeteoNormal {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}地点の<B>$lName</B>に${HtagDisaster_}隕石${H_tagDisaster}が落下、一帯が水没しました。",$id);
}

# 隕石、その他
sub logHugeMeteo {
    my($id, $name, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}地点に${HtagDisaster_}巨大隕石${H_tagDisaster}が落下！！",$id);
}
# 隕石、その他
sub logMidMeteo {
    my($id, $name, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}地点に${HtagDisaster_}小彗星${H_tagDisaster}が落下！！",$id);
}
# 隕石、その他
sub logMidMeteo2 {
    my($id, $name, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}地点に${HtagDisaster_}小彗星${H_tagDisaster}が落下！！しましたが、周囲の<b>防衛施設・改</b>が防衛したようです。",$id);
}
# 隕石、その他
sub logMidMeteo3 {
    my($id, $name, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}地点に${HtagDisaster_}隕石${H_tagDisaster}が落下！！しましたが、周囲の<b>防衛施設・改</b>が防衛したようです。",$id);
}
# 隕石、その他
sub logHugeMeteo4 {
    my($id, $name, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}地点に${HtagDisaster_}隕石${H_tagDisaster}が落下！！",$id);
}

# 噴火
sub logEruption {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}地点で${HtagDisaster_}火山が噴火${H_tagDisaster}、<B>山</B>が出来ました。",$id);
}

# 噴火、浅瀬
sub logEruptionSea1 {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}地点の<B>$lName</B>は、${HtagDisaster_}噴火${H_tagDisaster}の影響で陸地になりました。",$id);
}

# 噴火、海or海基
sub logEruptionSea {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}地点の<B>$lName</B>は、${HtagDisaster_}噴火${H_tagDisaster}の影響で海底が隆起、浅瀬になりました。",$id);
}

# 噴火、その他
sub logEruptionNormal {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}地点の<B>$lName</B>は、${HtagDisaster_}噴火${H_tagDisaster}の影響で壊滅しました。",$id);
}

# 地盤沈下発生
sub logFalldown {
    my($id, $name) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で${HtagDisaster_}地盤沈下${H_tagDisaster}が発生しました！！",$id);
}

# 地盤沈下被害
sub logFalldownLand {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は海の中へ沈みました。",$id);
}

# 広域被害、水没
sub logWideDamageSea {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は<B>水没</B>しました。",$id);
}

# 広域被害、海の建設
sub logWideDamageSea2 {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は跡形もなくなりました。",$id);
}

# 広域被害、怪獣水没
sub logWideDamageMonsterSea {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の陸地は<B>$lName</B>もろとも水没しました。",$id);
}

# 広域被害、怪獣
sub logWideDamageMonster {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は消し飛びました。",$id);
}

# 広域被害、荒地
sub logWideDamageWaste {
    my($id, $name, $lName, $point) = @_;
    logOut("${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>は一瞬にして<B>荒地</B>と化しました。",$id);
}

# 受賞
sub logPrize {
    my($id, $name, $pName) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が<B>$pName</B>を受賞しました。",$id);
    logHistory("${HtagName_}${name}島${H_tagName}、<B>$pName</B>を受賞");
}

# 受賞
sub logPrizet {
    my($id, $name, $pName, $value) = @_;
    logOut("${HtagName_}${name}島${H_tagName}が<B>$pName</B>を受賞しました。",$id);
    logHistory("${HtagName_}${name}島${H_tagName}、<B>$pName</B>を受賞（賞金<B>$value</B>)");
}

# 箱庭カップ
sub logHC {
    my($id, $name, $stsanka) = @_;
    logHistory("${HtagName_}Hakoniwa Cup$HislandTurn${H_tagName}開催！参加数$stsanka島！");
    logHcup("${HtagName_}Hakoniwa Cup$HislandTurn${H_tagName}開催！参加数$stsanka島！");
}

# 箱庭カップ開会式
sub logHCstart {
    my($id, $name, $str) = @_;
    logHistory("${HtagName_}${name}島${H_tagName}で<B>Hakoniwa Cup開会式</B>が行なわれ、<B>$str</B>の経済効果を巻き起こしました。",$id);
    logHcup("${HtagName_}${name}島${H_tagName}で<B>Hakoniwa Cup開会式</B>が行なわれ、<B>$str</B>の経済効果を巻き起こしました。",$id);
}

# 箱庭カップ試合
sub logHCgame {
    my($id, $tId, $name, $tName, $lName, $gName, $goal, $tgoal) = @_;
    logLate("${HtagName_}${name}島${H_tagName}で<B>$gName</B>が行われました。${HtagName_}${name}島代表${H_tagName}<B>VS</B>${HtagName_}${tName}島代表${H_tagName} ⇒ <B>$goal−$tgoal</B>",$id, $tId);
    logHcup("${HtagName_}${gName}${H_tagName}、${HtagName_}${name}島代表${H_tagName}<B>VS</B>${HtagName_}${tName}島代表${H_tagName} ⇒ <B>$goal−$tgoal</B>",$id, $tId);
}

# 箱庭カップ勝利
sub logHCwin {
    my($id, $name, $cName, $str) = @_;
    logLate("${HtagName_}${name}島代表${H_tagName}は、<B>$str</B>を獲得しました。",$id);
}

# 箱庭カップ優勝
sub logHCwintop {
    my($id, $name, $cName) = @_;
    logHistory("${HtagName_}${name}島代表${H_tagName}、<B>Hakoniwa Cup$cName優勝！</B>",$id);
    logHcup("${HtagName_}${name}島代表${H_tagName}、<B>Hakoniwa Cup$cName優勝！</B>",$id);
}

# 箱庭カップ不戦勝
sub logHCantiwin {
    my($id, $name, $gName) = @_;
    logLate("${HtagName_}${name}島代表${H_tagName}は<B>対戦チーム</B>がいないため<B>$gName</B>となりました。",$id);
    logHcup("${HtagName_}${name}島代表${H_tagName}は<B>対戦チーム</B>がいないため<B>$gName</B>。",$id);
}

# 箱庭カップ
sub logHCsin {
    my($id, $name, $stsin) = @_;
    logHistory("${HtagName_}Hakoniwa Cup決勝トーナメント進出島!!${H_tagName}<br><font size=\"-1\"><B>$stsin</B></font>");
    logHcup("${HtagName_}Hakoniwa Cup決勝トーナメント進出島!!${H_tagName}<br><font size=\"-1\"><B>$stsin</B></font>");
}

# 島がいっぱいな場合
sub tempNewIslandFull {
    out(<<END);
${HtagBig_}申し訳ありません、島が一杯で登録できません！！${H_tagBig}$HtempBack
END
}

# 新規で名前がない場合
sub tempNewIslandNoName {
    out(<<END);
${HtagBig_}入力が不十分です。${H_tagBig}$HtempBack
END
}

# 新規で名前が不正な場合
sub tempNewIslandBadName {
    out(<<END);
${HtagBig_}',?()<>\$'とか入ってたり、「無人島」とかいった変な名前はやめましょうよ〜${H_tagBig}$HtempBack
END
}

# すでにその名前の島がある場合
sub tempNewIslandAlready {
    out(<<END);
${HtagBig_}その島ならすでに発見されています。${H_tagBig}$HtempBack
END
}

# すでに同じＩＰの島がある場合
sub tempIPIslandAlready {
    out(<<END);
${HtagBig_}あなたと同じＩＰの島がすでに発見されています。<br>重複登録防止にご協力ください。${H_tagBig}$HtempBack
END
}

# パスワードがない場合
sub tempNewIslandNoPassword {
    out(<<END);
${HtagBig_}パスワードが必要です。${H_tagBig}$HtempBack
END
}

# 島を発見しました!!
sub tempNewIslandHead {
    out(<<END);
<CENTER>
${HtagBig_}島を発見しました！！${H_tagBig}<BR>
${HtagBig_}${HtagName_}「${HcurrentName}島」${H_tagName}と命名します。${H_tagBig}<BR>
$HtempBack<BR>
</CENTER>
END
}

# 地形の呼び方
sub landName {
    my($land, $lv) = @_;

    if($land == $HlandSea) {
	if($lv == 1) {
            return '浅瀬';
        } else {
            return '海';
	}
    } elsif($land == $HlandIce) {
	if($lv > 0) {
            return '天然スケート場';
        } else {
            return '氷河';
	}
    } elsif($land == $HlandWaste) {
	return '荒地';
    } elsif($land == $HlandPlains) {
	return '平地';
    } elsif($land == $HlandPlains2) {
	return '開発予定地';
    } elsif($land == $HlandTown) {
	if($lv < 30) {
	    return '村';
	} elsif($lv < 100) {
	    return '町';
	} else {
	    return '都市';
	}
    } elsif($land == $HlandProcity) {
	return '防災都市';
    } elsif($land == $HlandNewtown) {
	return 'ニュータウン';
    } elsif($land == $HlandBigtown) {
	return '現代都市';
    } elsif($land == $HlandBettown) {
	return '輝ける都市';
    } elsif($land == $HlandSkycity) {
	return '空中都市';
    } elsif($land == $HlandUmicity) {
	return '海都市';
    } elsif($land == $HlandSeatown) {
	return '海底新都市';
    } elsif($land == $HlandRizort) {
	return 'リゾート地';
    } elsif($land == $HlandKajino) {
	return 'カジノ';
    } elsif($land == $HlandBigRizort) {
	return '臨海リゾートホテル';
    } elsif($land == $HlandShuto) {
	return '首都';
    } elsif($land == $HlandUmishuto) {
	return '海底首都';
    } elsif($land == $HlandForest) {
	return '森';
    } elsif($land == $HlandFarm) {
	return '農場';
    } elsif($land == $HlandEneAt) {
	return '原子力発電所';
    } elsif($land == $HlandEneFw) {
	return '火力発電所';
    } elsif($land == $HlandEneWt) {
	return '水力発電所';
    } elsif($land == $HlandEneWd) {
	return '風力発電所';
    } elsif($land == $HlandEneBo) {
	return 'バイオマス発電所';
    } elsif($land == $HlandEneSo) {
	return 'ソーラー発電所';
    } elsif($land == $HlandEneCs) {
	return 'コスモ発電所';
    } elsif($land == $HlandConden) {
	return 'コンデンサ';
    } elsif($land == $HlandConden2) {
	return 'コンデンサ・改';
    } elsif($land == $HlandConden3) {
	return '黄金のコンデンサ';
    } elsif($land == $HlandConden4) {
	if($lv == 3) {
	    return '黄金のコンデンサ(漏電中)';
	} elsif($lv == 2) {
	    return 'コンデンサ・改(漏電中)';
	} elsif($lv == 99) {
	    return '核融合発電所';
	} else {
	    return '黄金のコンデンサ(漏電中)';
	}
    } elsif($land == $HlandFoodka) {
	return '食品加工工場';
    } elsif($land == $HlandFoodim) {
	if($lv < 480) {
	    return '食物研究所';
	} else {
	    return '防災型食物研究所';
	}
    } elsif($land == $HlandFarmchi) {
	return '養鶏場';
    } elsif($land == $HlandFarmpic) {
	return '養豚場';
    } elsif($land == $HlandFarmcow) {
	return '牧場';
    } elsif($land == $HlandYakusho) {
	return '島役所';
    } elsif($land == $HlandCollege) {
	if($lv == 0) {
	    return '農業大学';
	} elsif($lv == 1) {
	    return '工業大学';
	} elsif($lv == 2) {
	    return '総合大学';
	} elsif($lv == 3) {
	    return '軍事大学';
	} elsif($lv == 4) {
	    return '生物大学(待機中)';
	} elsif($lv == 98) {
	    return '生物大学(待機中)';
	} elsif($lv == 96) {
	    return '生物大学(出禁中)';
	} elsif($lv == 97) {
	    return '生物大学(出禁中)';
	} elsif($lv == 99) {
	    return '生物大学(出動中)';
	} elsif($lv == 5) {
	    return '気象大学';
	} elsif($lv == 6) {
	    return '経済大学';
	} elsif($lv == 7) {
	    return '魔法学校';
	} elsif($lv == 8) {
	    return '電工大学';
	} elsif($lv == 77) {
	    return '文部科学省';
	} elsif($lv == 78) {
	    return '文部科学省';
	} elsif($lv == 79) {
	    return '文部科学省';
	} elsif($lv == 80) {
	    return '文部科学省';
	} elsif($lv == 95) {
	    return '経済大学(貯金中)';
	} else {
	    return '気象大学';
	}
    } elsif($land == $HlandHouse) {
	if($lv == 0) {
	    return '小屋';
	} elsif($lv == 1) {
	    return '簡易住宅';
	} elsif($lv == 2) {
	    return '住宅';
	} elsif($lv == 3) {
	    return '高級住宅';
	} elsif($lv == 4) {
	    return '豪邸';
	} elsif($lv == 5) {
	    return '大豪邸';
	} elsif($lv == 6) {
	    return '高級豪邸';
	} elsif($lv == 7) {
	    return '城';
	} elsif($lv == 8) {
	    return '巨城';
	} else {
	    return '黄金城';
	}
    } elsif($land == $HlandTrain) {
	if($lv == 0) {
	    return '駅';
	} elsif($lv < 10) {
	    return '線路';
	} elsif($lv == 10) {
	    return '駅(普通電車停車中)';
	} elsif($lv < 20) {
	    return '普通電車';
	} elsif($lv == 20) {
	    return '駅(貨物列車停車中)';
	} elsif($lv < 30) {
	    return '貨物列車';
	}
    } elsif($land == $HlandTaishi) {
	return '大使館';
    } elsif($land == $HlandKura) {
	return '倉庫';
    } elsif($land == $HlandKuraf) {
	return '倉庫';
    } elsif($land == $HlandFactory) {
	return '工場';
    } elsif($land == $HlandHTFactory) {
	return 'ハイテク多国籍企業';
    } elsif($land == $HlandSHTF) {
	return 'ハイテク多国籍企業・改';
    } elsif($land == $HlandOWNF) {
	return '島営企業';
    } elsif($land == $HlandBase) {
	return 'ミサイル基地';
    } elsif($land == $HlandDefence) {
	if($lv == 77) {
	    return '防衛施設・改';
	} else {
	    return '防衛施設';
	}
    } elsif($land == $HlandMountain) {
	return '山';
    } elsif($land == $HlandGold) {
	return '金山';
    } elsif($land == $HlandOnsen) {
	return '温泉街';
    } elsif($land == $HlandMonster) {
	my($kind, $name, $hp) = monsterSpec($lv);
	return $name;
    } elsif($land == $HlandSbase) {
	return '海底基地';
    } elsif($land == $HlandSeacity) {
	return '海底都市';
    } elsif($land == $HlandOil) {
	return '海底油田';
    } elsif($land == $HlandMonument) {
	return $HmonumentName[$lv];
    } elsif($land == $HlandHaribote) {
	return 'ハリボテ';
    } elsif($land == $HlandPark) {
        return '遊園地';
    } elsif($land == $HlandMinato) {
	return '港町';
    } elsif($land == $HlandFune) {
	return $HfuneName[$lv];
    } elsif($land == $HlandFrocity) {
	return '海上都市';
    } elsif($land == $HlandSunahama) {
	return '砂浜';
    } elsif($land == $HlandMine) {
        return '地雷';
    } elsif($land == $HlandNursery) {
        return '養殖場';
    } elsif($land == $HlandKyujo) {
        return '野球場';
    } elsif($land == $HlandKyujokai) {
        return '多目的スタジアム';
    } elsif($land == $HlandZoo) {
        return '動物園';
    } elsif($land == $HlandUmiamu) {
        return '海あみゅ';
    } elsif($land == $HlandSeki) {
	return '関所';
    } elsif($land == $HlandRottenSea) {
	if($lv < 20) {
	    return '腐海';
	} else {
	    return '枯死海';
	}
    }
}

# 人口その他の値を算出
sub estimate {
    my($number) = $_[0];
    my($island);
    my($pop, $area, $farm, $mountain) = (0, 0, 0, 0);
    my($factory1, $factory2) = (0, 0);
    my($monslive, $monslivetype) = (0, 0);
    my($kei, $rena, $fore, $tare, $zipro, $leje) = (0, 0, 0, 0, 0, 0);
    my($oil) = (0);
    my($bas) = (0);
    my($kyu) = (0);
    my($amu) = (0);
    my($par) = (0);
    my($riz) = (0);
    my($fim) = (0);
    my($rot) = (0);
    my($sci) = (0);
    my($sba) = (0);
    my($pro) = (0);
    my($kin) = (0);
    my($nto) = (0);
    my($m26) = (0);
    my($m27) = (0);
    my($m17) = (0);
    my($c11) = (0);
    my($c13) = (0);
    my($c21) = (0);
    my($c28) = (0);
    my($c23) = (0);
    my($co0) = (0);
    my($co1) = (0);
    my($co2) = (0);
    my($co3) = (0);
    my($co4) = (0);
    my($co5) = (0);
    my($co6) = (0);
    my($co7) = (0);
    my($co8) = (0);
    my($co99) = (0);
    my($co77) = (0);
    my($co78) = (0);
    my($co79) = (0);
    my($co80) = (0);
    my($yaku) = (0);
    my($co01) = (0);
    my($co95) = (0);
    my($tet) = (0);
    my($hot) = (0);
    my($hou) = (0);
    my($shu) = (0);
    my($sin) = (0);
    my($jin) = (0);
    my($m74) = (0);
    my($m75) = (0);
    my($m76) = (0);
    my($m77) = (0);
    my($m78) = (0);
    my($m79) = (0);
    my($m84) = (0);
    my($m93) = (0);
    my($m96) = (0);
    my($m97) = (0);
    my($m98) = (0);
    my($m99) = (0);
    my($m100) = (0);
    my($m101) = (0);
    my($m73) = (0);
    my($gyo) = (0);
    my($ky2) = (0);
    my($zoo) = (0);
    my($htf) = (0);
    my($shtf) = (0);
    my($ownf) = (0);
    my($tai) = (0);
    my($tra) = (0);
    my($tra1) = (0);
    my($tra2) = (0);
    my($ene) = (0);
    my($h10) = (0);
    my($h11) = (0);
    my($con99) = (0);
    my($choki2) = (0);
    my($ownfe) = (0);

    # 地形を取得
    $island = $Hislands[$number];
    my($land) = $island->{'land'};
    my($landValue) = $island->{'landValue'};

    $etc5 = $island->{'etc5'};
    $etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

    if ($island->{'fukeikimoney'} < $island->{'money'}) {
	$island->{'fukeikimoney'} = $island->{'money'};
    }

    # 数える
    my($x, $y, $kind, $value);
    for($y = 0; $y < $HislandSize; $y++) {
	for($x = 0; $x < $HislandSize; $x++) {
	    $kind = $land->[$x][$y];
	    $value = $landValue->[$x][$y];
	    my($mKind, $mName, $mHp) = monsterSpec($value);
	    if(($kind != $HlandSea) &&
	       ($kind != $HlandIce) &&
	       ($kind != $HlandSbase) &&
	       ($kind != $HlandFune) &&
	       ($kind != $HlandFrocity) &&
	       ($kind != $HlandUmicity) &&
               ($kind != $HlandNursery) &&
               ($kind != $HlandUmiamu) &&
               ($kind != $HlandSeacity) &&
               ($kind != $HlandSeatown) &&
               ($kind != $HlandUmishuto) &&
	       ($kind != $HlandOil)){
		$area++;
		if(($kind == $HlandTown) ||
		   ($kind == $HlandProcity) ||
		   ($kind == $HlandOnsen) ||
		   ($kind == $HlandShuto) ||
		   ($kind == $HlandMinato)) {
		    # 町
		    $pop += $value;
		} elsif(($kind == $HlandFarm) ||
			($kind == $HlandFoodim)) {
		    # 農場
		    $farm += $value;
		} elsif(($kind == $HlandFoodka) && ($value > 0)) {
		    $factory1 += $value*200;
		    $farm += $value*200;
		} elsif($kind == $HlandFarmchi) {
		    $tare += $value;
		    $factory1 += int($value/100)+1;
		} elsif($kind == $HlandFarmpic) {
		    $zipro += $value;
		    $factory1 += int($value/80)+1;
		} elsif($kind == $HlandFarmcow) {
		    $leje += $value;
		    $factory1 += int($value/50)+1;
		} elsif(($kind == $HlandFactory) ||
			($kind == $HlandHTFactory) ||
			($kind == $HlandPark)) {
		    # 工場
		    $factory1 += $value;
		} elsif($kind == $HlandSHTF) {
		    $factory2 += $value;
		} elsif($kind == $HlandOWNF) {
		    $ownfe = int($value/1000);
		    $factory2 += int($value/100)%10*250;
		    $factory1 += int($value%100/10)*250;
		    $farm += $value%10*250;
		} elsif(($kind == $HlandMountain) ||
			($kind == $HlandGold)) {
		    # 山
		    $mountain += $value;
		} elsif($kind == $HlandForest) {
		    $fore += $value;
		} elsif($kind == $HlandNewtown) {
		    # ニュータウン
		    $pop += $value;
		    $nwork =  int($value/15);
		    $factory1 += $nwork;
		} elsif($kind == $HlandBigtown) {
		    # 現代都市
		    $pop += $value;
		    $mwork =  int($value/20);
		    $lwork =  int($value/30);
		    $factory1 += $mwork;
		    $farm += $lwork;
		} elsif($kind == $HlandBettown) {
		    # 輝ける都市
		    $pop += $value;
		} elsif($kind == $HlandSkycity) {
		    # 空中都市
		    $pop += $value;
		    $factory2 += int($value/60);
		    $farm += int($value/60);
		    $island->{'shouhi'} += int($value/2*(100-$s02)/100);
		} elsif($kind == $HlandRizort) {
		    # リゾート地
		    $pop += $value;
		} elsif($kind == $HlandKajino) {
		    # リゾート地
		    $pop += $value;
		    $island->{'shouhi'} += int($value/10*(100-$s02)/100);
		} elsif($kind == $HlandBigRizort) {
		    # リゾート地
		    $pop += $value;
		} elsif($kind == $HlandBase) {
		    # 基地
		    $bas += $value;
		    $rena += $value;
		    $island->{'shouhi'} += int($value/4*(100-$s02)/100);
		}
            } elsif ($kind == $HlandNursery) {
                # 養殖場は農場の一種
                $farm += $value;
            } elsif ($kind == $HlandUmiamu) {
                $factory1 += $value;
            } elsif ($kind == $HlandSeacity) {
                $pop += $value;
            } elsif ($kind == $HlandFrocity) {
                $pop += $value;
            } elsif ($kind == $HlandUmicity) {
                $pop += $value;
		$factory2 += int($value/60);
		$farm += int($value/60);
		$island->{'shouhi'} += int($value/2*(100-$s02)/100);
            } elsif ($kind == $HlandUmishuto) {
                $pop += $value;
            } elsif ($kind == $HlandSeatown) {
                $pop += $value;
		    $owork =  int($value/40);
		    $factory1 += $owork;
		    $farm += $owork;
            } elsif ($kind == $HlandSbase) {
                $bas += $value;
		$rena += $value;
		$island->{'shouhi'} += int($value/2*(100-$s02)/100);
	    }

            $oil++ if ($kind == $HlandOil);
            $htf++ if ($kind == $HlandHTFactory);
            $shtf++ if ($kind == $HlandSHTF);
            $ownf++ if ($kind == $HlandOWNF);
            $kei++ if ($kind == $HlandMonument);
            $kyu++ if ($kind == $HlandKyujo);
            $kyu++ if ($kind == $HlandKyujokai);
            $ky2++ if ($kind == $HlandKyujokai);
            $zoo++ if ($kind == $HlandZoo);
            $amu++ if ($kind == $HlandUmiamu);
            $par++ if ($kind == $HlandPark);
            $riz++ if ($kind == $HlandRizort);
            $riz++ if ($kind == $HlandKajino);
            $fim++ if (($kind == $HlandFoodim) && ($value < 480));
            $rot++ if (($kind == $HlandRottenSea) && ($value < 20));
            $sci++ if ($kind == $HlandSeacity);
            $sci++ if ($kind == $HlandSeatown);
            $sci++ if ($kind == $HlandSeatown);
            $sba++ if ($kind == $HlandSbase);
            $pro++ if ($kind == $HlandProcity);
            $pro++ if ($kind == $HlandFrocity);
            $kin++ if ($kind == $HlandGold);
            $nto++ if ($kind == $HlandNewtown);
            $m73++ if (($kind == $HlandMonument) && ($value == 73));
            $m96++ if (($kind == $HlandMonument) && ($value == 96));
            $m97++ if (($kind == $HlandMonument) && ($value == 97));
            $m98++ if (($kind == $HlandMonument) && ($value == 98));
            $m99++ if (($kind == $HlandMonument) && ($value == 99));
            $m100++ if (($kind == $HlandMonument) && ($value == 100));
            $m101++ if (($kind == $HlandMonument) && ($value == 101));
            $m26++ if (($kind == $HlandMonument) && ($value == 86));
            $m27++ if (($kind == $HlandMonument) && ($value == 87));
            $m74++ if (($kind == $HlandMonument) && ($value == 74));
            $m75++ if (($kind == $HlandMonument) && ($value == 75));
            $m76++ if (($kind == $HlandMonument) && ($value == 76));
            $m77++ if (($kind == $HlandMonument) && ($value == 77));
            $m78++ if (($kind == $HlandMonument) && ($value == 78));
            $m79++ if (($kind == $HlandMonument) && ($value == 79));
            $m84++ if (($kind == $HlandMonument) && ($value == 84));
            $m93++ if (($kind == $HlandHouse) && ($value == 10));
            $m93++ if (($kind == $HlandHouse) && ($value == 11));
            $h10++ if (($kind == $HlandHouse) && ($value == 10));
            $h11++ if (($kind == $HlandHouse) && ($value == 11));
            $m17++ if (($kind == $HlandMonument) && ($value == 17));
            $m17++ if ($kind == $HlandEneCs);
            $sin++ if (($kind == $HlandMonument) && ($value == 26));
            $jin++ if (($kind == $HlandMonument) && ($value == 27));
            $c11++ if (($kind == $HlandMonster) && ($mKind == 11));
            $c13++ if (($kind == $HlandMonster) && ($mKind == 13));
            $c13++ if (($kind == $HlandMonument) && ($value == 93));
            $c21++ if (($kind == $HlandMonster) && ($mKind == 21));
            $c28++ if (($kind == $HlandMonster) && ($mKind == 28));
            $c28++ if (($kind == $HlandMonster) && ($mKind == 30));
            $c23++ if (($kind == $HlandMonster) && ($mKind == 23));
            $co0++ if (($kind == $HlandCollege) && ($value == 0));
            $co1++ if (($kind == $HlandCollege) && ($value == 1));
            $co01++ if (($kind == $HlandCollege) && ($value == 1));
            $co1++ if (($kind == $HlandCollege) && ($value == 8));
            $co2++ if (($kind == $HlandCollege) && ($value == 2));
            $co1++ if (($kind == $HlandCollege) && ($value == 2));
            $co0++ if (($kind == $HlandCollege) && ($value == 2));
            $co3++ if (($kind == $HlandCollege) && ($value == 3));
            $co4++ if (($kind == $HlandCollege) && ($value == 4));
            $co4++ if (($kind == $HlandCollege) && ($value == 98));
            $co4++ if (($kind == $HlandCollege) && ($value == 97));
            $co4++ if (($kind == $HlandCollege) && ($value == 96));
            $co99++ if (($kind == $HlandCollege) && ($value == 99));
            $co5++ if (($kind == $HlandCollege) && ($value == 5));
            $co6++ if (($kind == $HlandCollege) && ($value == 6));
            $co6++ if (($kind == $HlandCollege) && ($value == 95));
            $co95++ if (($kind == $HlandCollege) && ($value == 95));
            $co7++ if (($kind == $HlandCollege) && ($value == 7));
            $co8++ if (($kind == $HlandCollege) && ($value == 8));
            $co77++ if (($kind == $HlandCollege) && ($value == 77));
            $co77++ if (($kind == $HlandCollege) && ($value == 78));
            $co77++ if (($kind == $HlandCollege) && ($value == 79));
            $co77++ if (($kind == $HlandCollege) && ($value == 80));
            $co78++ if (($kind == $HlandCollege) && ($value == 78));
            $co79++ if (($kind == $HlandCollege) && ($value == 79));
            $co80++ if (($kind == $HlandCollege) && ($value == 80));
            $yaku++ if ($kind == $HlandYakusho);
            $tet++ if (($kind == $HlandCollege) && ($value == 98));
            $tet++ if (($kind == $HlandCollege) && ($value == 97));
            $tet++ if (($kind == $HlandMonster) && ($mKind == 30));
            $hot++ if ($kind == $HlandOnsen);
            $hou++ if ($kind == $HlandHouse);
            $tai++ if ($kind == $HlandTaishi);
            $shu++ if ($kind == $HlandShuto);
            $shu++ if ($kind == $HlandUmishuto);
            $gyo++ if (($kind == $HlandFune) && ($value == 1));
            $gyo++ if (($kind == $HlandFune) && ($value == 2));
            $gyo++ if (($kind == $HlandFune) && ($value == 5));
            $gyo++ if (($kind == $HlandFune) && ($value == 6));
            $gyo++ if (($kind == $HlandFune) && ($value == 11));
            $tra++ if ($kind == $HlandTrain);
            $tra1++ if (($kind == $HlandTrain) && (($value == 10) || ($value == 11) || ($value == 12) || ($value == 13) || ($value == 14) || ($value == 15) || ($value == 16) || ($value == 17) || ($value == 18) || ($value == 19)));
            $tra2++ if (($kind == $HlandTrain) && (($value == 20) || ($value == 21) || ($value == 22) || ($value == 23) || ($value == 24) || ($value == 25) || ($value == 26) || ($value == 27) || ($value == 28) || ($value == 29)));

	    if($kind == $HlandEneAt) {
		    $ene += $value;
	    }
	    if($kind == $HlandEneBo) {
		    $ene += $value;
	    }
	    if($kind == $HlandEneWt) {
		    $ene += int($value*(random(80)+70)/100);
			if($island->{'Typhoonflag'} == 1) {
			$ene += int($value*(random(80)+70)/100);
			}
	    }
	    if(($kind == $HlandEneSo) && ($island->{'Typhoonflag'} != 1)) {
		    $ene += int($value*(random(25)+75)/100);
	    }
	    if($kind == $HlandEneWd) {
		    $ene += int($value*(random(75)+50)/100);
			if($island->{'Typhoonflag'} == 1) {
			$ene += int($value*(random(75)+50)/100);
			}
	    }
	    if(($kind == $HlandEneFw) && ($island->{'oil'} > 0)) {
		    $ene += $value;
		    $ene += $value;
	    } elsif(($kind == $HlandEneFw) && ($island->{'mountain'} > 0)) {
		    $ene += $value;
	    }
	    if(($kind == $HlandEneCs) && ($island->{'eis7'} > 0)) {
		    $ene += $value;
	    }
	    if(($kind == $HlandConden4) && ($value == 99)) {
		    $con99++;
	    }
	    if($kind == $HlandConden) {
		    $ene += $value;
		    $landValue->[$x][$y] = 0;
	    }
	    if($kind == $HlandConden2) {
		    $ene += $value;
		    $landValue->[$x][$y] = 0;
	    }
	    if($kind == $HlandConden3) {
		    $ene += $value;
		    $ene += $value;
		    $landValue->[$x][$y] = 0;
	    }

            if ($kind == $HlandMonster) {
                my($mKind, $mName, $mHp) = monsterSpec($value);
                $monslive++;
                $monslivetype |= (2 ** $mKind);
            }

            if ($kind == $HlandTaishi) {
	    my($tn) = $HidToNumber{$value};
	    my($tIsland) = $Hislands[$tn];
	        if ($tIsland->{'money'} > $island->{'money'}) {
		    $island->{'fukeikimoney'} = $tIsland->{'money'};
	        }
            }

            if ($kind == $HlandKura) {
		$seq = int($value/100);
		$choki = $value%100;
		$choki2 += $choki;
            }

	}
    }


    if($con99 > 0) {
	    $magicl = $m79 + int($m100/2);
	    $magica = $m75 + int($m98/2);
		if ($island->{'h10'} > 0) {
		    $magicf += 10;
		    $magici += 10;
		    $magica += 10;
		    $magicw += 10;
		    $magicd += 10;
		}
		if ($island->{'h11'} > 0) {
		    $magicl += 10;
		}
	    if($magica != $magicl) {
		$ene += random($magicl*15000+50000);
		$ene -= int(random($magicl*15000+50000) * (50-$s02)/50);
	    } else {
		$ene += $magicl*15000+50000+$s02*1000;
	    }
    }


    if($island->{'eis7'} >= 1) {
	$eis7 = $island->{'eis7'};
	$cstpop = int($eis7/100);
	$csten = $eis7%100;
	$pop += $cstpop;
    }


    # 代入
    $island->{'pop'}      = $pop;
    $island->{'area'}     = $area;
    $island->{'farm'}     = $farm;
    $island->{'factory'}  = "$factory1,$factory2,$co0,$co1,$htf,$shtf,$co95,$co95,$co95,$co95";
    $island->{'factory1'}  = $factory1;
    $island->{'factory2'}  = $factory2;
    $island->{'factoryt'}  = $factory1+$factory2;
    $island->{'mountain'} = $mountain;

    $island->{'oil'}      = $oil;
    $island->{'bas'}      = $bas;
    $island->{'kyu'}      = $kyu;
    $island->{'ky2'}      = $ky2;
    $island->{'zoo'}      = $zoo;
    $island->{'amu'}      = $amu;
    $island->{'par'}      = $par;
    $island->{'riz'}      = $riz;
    $island->{'fim'}      = $fim;
    $island->{'rot'}      = $rot;
    $island->{'sci'}      = $sci;
    $island->{'sba'}      = $sba;
    $island->{'pro'}      = $pro;
    $island->{'kin'}      = $kin;
    $island->{'nto'}      = $nto;
    $island->{'m26'}      = $m26;
    $island->{'m27'}      = $m27;
    $island->{'m17'}      = $m17;
    $island->{'c11'}      = $c11;
    $island->{'c13'}      = $c13;
    $island->{'c21'}      = $c21;
    $island->{'c28'}      = $c28;
    $island->{'c23'}      = $c23;
    $island->{'co0'}      = $co0;
    $island->{'co1'}      = $co1;
    $island->{'co01'}      = $co01;
    $island->{'co2'}      = $co2;
    $island->{'co3'}      = $co3;
    $island->{'co4'}      = $co4;
    $island->{'co5'}      = $co5;
    $island->{'co6'}      = $co6;
    $island->{'co7'}      = $co7;
    $island->{'co8'}      = $co8;
    $island->{'co99'}      = $co99;
    $island->{'co77'}      = $co77;
    $island->{'co78'}      = $co78;
    $island->{'co79'}      = $co79;
    $island->{'co80'}      = $co80;
    $island->{'yaku'}      = $yaku;
    $island->{'tet'}      = $tet;
    $island->{'hot'}      = $hot;
    $island->{'hou'}      = $hou;
    $island->{'tai'}      = $tai;
    $island->{'shu'}      = $shu;
    $island->{'sin'}      = $sin;
    $island->{'jin'}      = $jin;
    $island->{'m96'}      = $m96;
    $island->{'m97'}      = $m97;
    $island->{'m98'}      = $m98;
    $island->{'m99'}      = $m99;
    $island->{'m100'}      = $m100;
    $island->{'m101'}      = $m101;
    $island->{'m74'}      = $m74;
    $island->{'m75'}      = $m75;
    $island->{'m76'}      = $m76;
    $island->{'m77'}      = $m77;
    $island->{'m78'}      = $m78;
    $island->{'m79'}      = $m79;
    $island->{'m84'}      = $m84;
    $island->{'m93'}      = $m93;
    $island->{'m73'}      = $m73;
    $island->{'h10'}      = $h10;
    $island->{'h11'}      = $h11;
    $island->{'gyo'}      = $gyo;
    $island->{'htf'}      = $htf;
    $island->{'shtf'}      = $shtf;
    $island->{'ownf'}      = $ownf;
    $island->{'tra'}      = $tra;
    $island->{'tra1'}      = $tra1;
    $island->{'tra2'}      = $tra2;
    $island->{'etc0'}      = $tra+int($island->{'trainmoney'}/1000)+int($island->{'trainmoney2'}/500);
    $island->{'ownfe'}     = $ownfe;

    $ene = int($ene*(1+$island->{'co8'}/10));
    if($ene < 0) {
	$ene = 0;
    }

    $island->{'shouhi'} += int($pop/200*(100-$s02)/100)+int($factory1/20*(100-$s02)/100)+int($factory2/10*(100-$s02)/100);
    $island->{'shouhi'} += int($island->{'pts'}/300*(100-$s02)/100);
    $island->{'shouhi'} += int($island->{'rena'}/30*(100-$s02)/100);
    $island->{'shouhi'} += int($island->{'rena'}/30*(100-$s02)/100);
    $island->{'sabun'} = $ene-$island->{'shouhi'};
    $island->{'eisei3'}    = "$ene,$island->{'shouhi'},$island->{'shouhi'},$ene,$ene";

    $island->{'ene'}      = $ene;
    $island->{'con99'}      = $con99;

    if($island->{'pts'} > $HouseLevel9) {
	$enekeisu = 2.5;
    } elsif($island->{'pts'} > $HouseLevel8) {
	$enekeisu = 2.35;
    } elsif($island->{'pts'} > $HouseLevel7) {
	$enekeisu = 2.2;
    } elsif($island->{'pts'} > $HouseLevel6) {
	$enekeisu = 2.15;
    } elsif($island->{'pts'} > $HouseLevel5) {
	$enekeisu = 1.9;
    } elsif($island->{'pts'} > $HouseLevel4) {
	$enekeisu = 1.75;
    } elsif($island->{'pts'} > $HouseLevel3) {
	$enekeisu = 1.6;
    } elsif($island->{'pts'} > $HouseLevel2) {
	$enekeisu = 1.45;
    } elsif($island->{'pts'} > $HouseLevel1) {
	$enekeisu = 1.2;
    } else {
	$enekeisu = 1;
    }

    if($HislandSize < 16) {
	$enekeisu = 1;
    }

    $enepoint = int($ene/(10*$enekeisu));

    $magicf = $m78 + int($m96/2);
    $magici = $m76 + int($m97/2);
    $magica = $m75 + int($m98/2);
    $magicw = $m77 + int($m99/2);
    $magicl = $m79 + int($m100/2);
    $magicd = $m74 + int($m101/2);

    if ($island->{'h10'} > 0) {
    $magicf += 10;
    $magici += 10;
    $magica += 10;
    $magicw += 10;
    $magicd += 10;
    }
    if ($island->{'h11'} > 0) {
    $magicl += 10;
    }
    $island->{'etc9'} = "$co7,$magicf,$magici,$magica,$magicw,$magicl,$magicd";

    if ($island->{'sabun'} > 0) {
	my($x, $y, $landKind, $lv, $i);
	for($i = 0; $i < $HpointNumber; $i++) {
	    $x = $Hrpx[$i];
	    $y = $Hrpy[$i];
	    $landKind = $land->[$x][$y];
	    $lv = $landValue->[$x][$y];
	    if(($landKind == $HlandConden) && ($lv < 2000)) {

                    $n = int((2000 - $lv) / 2);
                    $n = min(int($n + $n), $island->{'sabun'});
                    $island->{'sabun'} -= $n;
                    $landValue->[$x][$y] += $n;
		if ($value > 2000) {
                    $landValue->[$x][$y] = 2000;
		}

	    }
 	    if(($landKind == $HlandConden2) && ($lv < 4000)) {

                    $n = int((4000 - $lv) / 10);
                    $n = min(int($n*9 + rand($n)), $island->{'sabun'});
                    $island->{'sabun'} -= $n;
                    $landValue->[$x][$y] += $n;
		if ($value > 4000) {
                    $landValue->[$x][$y] = 4000;
		}

	    }
	    if(($landKind == $HlandConden3) && ($lv < 7000)) {

                    $n = int((7000 - $lv) / 2);
                    $n = min(int($n + $n), $island->{'sabun'});
                    $island->{'sabun'} -= $n/2;
                    $landValue->[$x][$y] += $n/2;
		if ($value > 7000) {
                    $landValue->[$x][$y] = 7000;
		}

	    }

                last if ($island->{'sabun'} <= 0);
	}
    }

    # 島主の家判定
    if($island->{'hou'} == 0) {
	$island->{'eisei1'} = 0;
    }

    # 首都判定
    if($island->{'shu'} == 0) {
	$island->{'totoyoso2'} = 555;
    } elsif($island->{'totoyoso2'} == 555) {
	my($onm);
	$onm = $island->{'onm'};
	$island->{'totoyoso2'} = "$onmシティー";
    }

    # 通算観光者
    if($island->{'eisei2'} < 0) {
	$island->{'eisei2'} = 0;
    }

    $eisei4 = $island->{'eisei4'};
    $eisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($sto, $std, $stk, $stwin, $stdrow, $stlose, $stwint, $stdrowt, $stloset, $styusho, $stshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);
    $kachiten = $stwin*3 + $stdrow;
    $island->{'kachiten'} = $kachiten;

    if($island->{'ky2'} == 0) {
	$island->{'eisei4'} = "$sto,$std,$stk,0,0,0,$stwint,$stdrowt,$stloset,$styusho,0";
    }


    if(($island->{'co77'} == 0) || ($island->{'etc5'} == 0)) {
	$island->{'etc5'} = '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0';
    }


    $etc5 = $island->{'etc5'};
    $etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

    $island->{'etc5'} = "$co77,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30";


    if($island->{'zoo'} == 0) {
	$island->{'etc6'} = '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0';
    }

    $etc6 = $island->{'etc6'};
    $etc6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($z00,$z01,$z02,$z03,$z04,$z05,$z06,$z07,$z08,$z09,$z10,$z11,$z12,$z13,$z14,$z15,$z16,$z17,$z18,$z19,$z20,$z21,$z22,$z23,$z24,$z25,$z26,$z27,$z28,$z29,$z30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
    $zookazu = $z0+$z1+$z2+$z3+$z4+$z5+$z6+$z7+$z8+$z9+$z10+$z11+$z12+$z13+$z14+$z15+$z16+$z17+$z18+$z19+$z20+$z21+$z22+$z23+$z24+$z25+$z26+$z27+$z28+$z29+$z30;

    $island->{'etc6'} = "$z00,$z01,$z02,$z03,$z04,$z05,$z06,$z07,$z08,$z09,$z10,$z11,$z12,$z13,$z14,$z15,$z16,$z17,$z18,$z19,$z20,$z21,$z22,$z23,$z24,$z25,$z26,$z27,$z28,$z29,$z30";

    $island->{'monsterlive'} = $monslive; # 怪獣出現数
    $island->{'monsterlivetype'} = $monslivetype; # 怪獣出現種類
    $monsterlive2 = $monslive + $zookazu;
    $island->{'monsterlive2'} = $monsterlive2; # 怪獣出現数

    $island->{'kei'} = $kei;
	$eisei5 = $island->{'eisei5'};
	$eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tetsub) = ($1, $2, $3, $4, $5, $6, $7);
    $island->{'rena'} = $rena + $co2*100 + $co3*500 + $msexe;
    $island->{'fore'} = $fore;
    $island->{'tare'} = $tare;
    $island->{'zipro'} = $zipro;
    $island->{'leje'} = $leje;

    # マスコット判定
    if(($island->{'co4'} == 0) &&
	($island->{'co99'} == 0) &&
	($island->{'c28'} == 0)) {
    $island->{'eisei5'} = "0,0,0,0,0,0,0";
    }

    $eisei5 = $island->{'eisei5'};
    $eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tetsub) = ($1, $2, $3, $4, $5, $6, $7);
    $island->{'eisei5'} = "$mshp,$msap,$msdp,$mssp,$mswin,$msexe,$tet";

    $island->{'eisei6'} = "$c13,$shu,$m26,$m27,$m74,$m75,$m76,$m77,$m78,$m79,$m84,$m93";

    # 失業者数
    $island->{'unemployed'} = $pop - ($farm + $factory1 + $factory2 + $mountain) * 10;


    my($eiseip1) = (0);
    my($eiseip2) = (0);
    my($eiseip3) = (0);
    my($eiseip4) = (0);
    my($eiseip5) = (0);
    my($eiseip6) = (0);


    if($island->{'eis1'} >= 1) {
	$eiseip1 = 100 + $island->{'eis1'}*2;
    }
    if($island->{'eis2'} >= 1) {
	$eiseip2 = 300 + $island->{'eis2'}*2;
    }
    if($island->{'eis3'} >= 1) {
	$eiseip3 = 500 + $island->{'eis3'}*2;
    }
    if($island->{'eis4'} >= 1) {
	$eiseip4 = 900 + $island->{'eis4'}*2;
    }
    if($island->{'eis5'} >= 1) {
	$eiseip5 = 1500 + $island->{'eis5'}*2;
    }
    if($island->{'eis6'} >= 1) {
	$eiseip6 = 2000 + $island->{'eis6'}*2;
    }


    $etc8 = $island->{'etc8'};
    $etc8 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($toto1, $toto2, $toto3, $toto4, $toto5, $toto6, $toto7) = ($1, $2, $3, $4, $5, $6, $7);
    $island->{'etc8'} = "$toto1,$toto2,$toto3,$toto4,$toto5,$toto6,$toto7";

    $totoyoso2 = $island->{'totoyoso2'};
    $island->{'totoyoso2'} = "$totoyoso2";
    $totoyoso = $island->{'totoyoso'};
    $island->{'totoyoso'} = "$totoyoso";

    $auc1 = $island->{'auc1'};
    $island->{'auc1'} = "$auc1";
    $auc2 = $island->{'auc2'};
    $island->{'auc2'} = "$auc2";
    $auc3 = $island->{'auc3'};
    $island->{'auc3'} = "$auc3";

    $auc4 = $island->{'auc4'};
    $auc4 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
    ($auc4a, $auc4b, $auc4c) = ($1, $2, $3);
    $island->{'auc4'} = "$auc4a,$auc4b,$auc4c";

    $auc0 = $island->{'auc0'};
    $auc0 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($auc0a, $auc0b, $auc0c, $auc0d, $auc0e) = ($1, $2, $3, $4, $5);
    $island->{'auc0'} = "$auc0a,$auc0b,$auc0c,$auc0d,$auc0e";
    $island->{'auc0c'} = $auc0c;

    $auc5 = $island->{'auc5'};
    $auc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($auc5a, $auc5b, $auc5c, $auc5d, $auc5e) = ($1, $2, $3, $4, $5);
    $island->{'auc5'} = "$auc5a,$auc5b,$auc5c,$auc5d,$auc5e";
    $island->{'auc5c'} = $auc5c;

    $auc6 = $island->{'auc6'};
    $auc6 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
    ($auc6a, $auc6x, $auc6y) = ($1, $2, $3);
    $island->{'auc6'} = "$auc6a,$auc6x,$auc6y";

    if($auc6a == 1) {
	$oyasumiritu++;
    }

    $auc7 = $island->{'auc7'};
    $island->{'auc7'} = $auc7;
    $auc8 = $island->{'auc8'};
    $island->{'auc8'} = $auc8;

    $auc9 = $island->{'auc9'};
    $auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);

    $auc9c2 = int($auc9c/10000);

    $auc9b = $co95*25+$choki2;

    $auc9a = $auc9b + $auc9c2 + $auc9d + $auc9e;

    $island->{'auc9'} = "$auc9a,$auc9b,$auc9c,$auc9d,$auc9e";

    $auc0es = (11-$auc0e)*500;
    if($auc0c == 0) {
	$auc0es = 0;
    }
    if($auc0es < 0) {
	$auc0es = 0;
    }


    if($AnkeitoOnOff == 0) {
	$island->{'anflag'} = 0;
    }


    $etc5 = $island->{'etc5'};
    $etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

    $s12b = int($s12/5)+1;
    if($s12b > 10) {$s12b = 10;}

    if($island->{'money'} > 999999*$s12b) {
	$moneypts = 9999*$s12b + (($island->{'money'}-999999*$s12b)/100)**0.75;
    } else {
	$moneypts = $island->{'money'}/100;
    }

    # 総合Point
    $island->{'pts'} = int($pop + $moneypts + $island->{'food'}/100 + ($farm*2 + $factory1 + $factory2*2 + $mountain*2) + $bas + $area*5 + int($fore/15) + $sci*30 + $pro*20 + $sba*10 + $amu*10 + $oil*500 + $kin*500 + $m26*500 + $m27*500 + $m74*750 + $m75*750 + $m76*750 + $m77*750 + $m78*750 + $m79*750 + $m93*2000 + int($tare/15) + int($zipro/12) + int($leje/10) + int($island->{'rena'}/10) + $eiseip1 + $eiseip2 + $eiseip3 + $eiseip4 + $eiseip5 + $eiseip6 + $hou*500 + $enepoint + $tra1*150 + $tra2*150 + $auc0es);

	$eisei4 = $island->{'eisei4'};
	$eisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($sto, $std, $stk, $stwin, $stdrow, $stlose, $stwint, $stdrowt, $stloset, $styusho, $stshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);
	$kachiten = $stwin*3 + $stdrow;
	$kachitent = $stwint*3 + $stdrowt;
	$siaisu = $stwint + $stdrowt + $stloset;
	if($siaisu == 0) {
	    $siaisu = 1;
	}
	$shoritu = int($stwint / $siaisu * 100);
	$teamforce = $sto + $std + $stk;

	$island->{'kachitent'} = $kachitent;
	$island->{'shoritu'} = $shoritu;
	$island->{'styusho'} = $styusho;
	$island->{'teamforce'} = $teamforce;

	$eisei5 = $island->{'eisei5'};
	$eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tet) = ($1, $2, $3, $4, $5, $6, $7);
	$force = $mshp+$msap+$msdp+$mssp;
	$island->{'force'} = $force;

	$eisei6 = $island->{'eisei6'};
	$eisei6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($unimika, $unishuto, $unimeka, $unioumu, $unianseki, $unitiseki, $unihyouseki, $unifuseki, $unienseki, $unikouseki, $uniiseki, $uniden) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12);

	$unimika3 = ($unimika == 0) ? "0" : "1";
	$unishuto3 = ($unishuto == 0) ? "0" : "1";
	$unimeka3 = ($unimeka == 0) ? "0" : "1";
	$unioumu3 = ($unioumu == 0) ? "0" : "1";
	$unianseki3 = ($unianseki == 0) ? "0" : "1";
	$unitiseki3 = ($unitiseki == 0) ? "0" : "1";
	$unihyouseki3 = ($unihyouseki == 0) ? "0" : "1";
	$unifuseki3 = ($unifuseki == 0) ? "0" : "1";
	$unienseki3 = ($unienseki == 0) ? "0" : "1";
	$unikouseki3 = ($unikouseki == 0) ? "0" : "1";
	$uniiseki3 = ($uniiseki == 0) ? "0" : "1";
	$uniden3 = ($uniden == 0) ? "0" : "1";

	$tuni = $unimika+$unishuto+$unimeka+$unioumu+$unianseki+$unitiseki+$unihyouseki+$unifuseki+$unienseki+$unikouseki+$uniiseki+$uniden;
	$uni = $unimika3+$unishuto3+$unimeka3+$unioumu3+$unianseki3+$unitiseki3+$unihyouseki3+$unifuseki3+$unienseki3+$unikouseki3+$uniiseki3+$uniden3;
	$island->{'uni'} = $uni;
	$island->{'tuni'} = $tuni;

    $island->{'pts'} += $island->{'bumon'}*100*$HislandNumber;

    if($anothermood == 1) {
    $island->{'money'} += $island->{'bumon'}*100*$HislandNumber + $auc0es;
    $island->{'pts'} = $island->{'money'}+$island->{'incomemoney'};
    }


    if($island->{'hou'} > 0) {
	    my($x, $y, $i);
	    for($i = 0; $i < $HpointNumber; $i++) {
		$x = $Hrpx[$i];
		$y = $Hrpy[$i];
		my($landKind) = $land->[$x][$y];
		my($lv) = $landValue->[$x][$y];

			if($landKind == $HlandHouse) {
				$etc8 = $island->{'etc8'};
				$etc8 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
				($toto1, $toto2, $toto3, $toto4, $toto5, $toto6, $toto7) = ($1, $2, $3, $4, $5, $6, $7);

			        if(($island->{'pts'} > $HouseLevel9) && ($island->{'m75'} > 0) && ($island->{'m76'} > 0) && ($island->{'m77'} > 0) && ($island->{'m78'} > 0) && ($island->{'c13'} > 0) && ($island->{'shu'} > 0) && ($island->{'m26'} > 0) && ($island->{'m27'} > 0) && ($island->{'m84'} > 0) && ($toto2 > 0)) {
					if(($island->{'m74'} > 0) || ($island->{'m79'} > 0)) {
					$landValue->[$x][$y] = 11;
						if($island->{'m74'} >= $island->{'m79'}) {
						$landValue->[$x][$y] = 10;
						}
					}
			        } elsif($island->{'pts'} > $HouseLevel9) {
			 	    $landValue->[$x][$y] = 9;
			        } elsif($island->{'pts'} > $HouseLevel8) {
			 	    $landValue->[$x][$y] = 8;
			        } elsif($island->{'pts'} > $HouseLevel7) {
				    $landValue->[$x][$y] = 7;
			        } elsif($island->{'pts'} > $HouseLevel6) {
			 	    $landValue->[$x][$y] = 6;
			        } elsif($island->{'pts'} > $HouseLevel5) {
				    $landValue->[$x][$y] = 5;
			        } elsif($island->{'pts'} > $HouseLevel4) {
			 	    $landValue->[$x][$y] = 4;
			        } elsif($island->{'pts'} > $HouseLevel3) {
				    $landValue->[$x][$y] = 3;
			        } elsif($island->{'pts'} > $HouseLevel2) {
			 	    $landValue->[$x][$y] = 2;
			        } elsif($island->{'pts'} > $HouseLevel1) {
				    $landValue->[$x][$y] = 1;
			        } else {
				    $landValue->[$x][$y] = 0;
			        }
			}
		}
	}


	# 死滅判定2
	if($island->{'dead'} == 1) {
	    $island->{'pop'} = 0;
	    $island->{'pts'} = 0;
	} elsif($island->{'pop'} == 0) {
	    $island->{'dead'} = 1;
	    $island->{'pts'} = 0;
	}

}


# 範囲内の地形を数える
sub countAround {
    my($land, $x, $y, $kind, $range) = @_;
    my($i, $count, $sx, $sy);
    $count = 0;
    for($i = 0; $i < $range; $i++) {
	 $sx = $x + $ax[$i];
	 $sy = $y + $ay[$i];

	 # 行による位置調整
	 if((($sy % 2) == 0) && (($y % 2) == 1)) {
	     $sx--;
	 }

	 if(($sx < 0) || ($sx >= $HislandSize) ||
	    ($sy < 0) || ($sy >= $HislandSize)) {
	     # 範囲外の場合
	     if($kind == $HlandSea) {
		 # 海なら加算
		 $count++;
	     }
	 } else {
	     # 範囲内の場合
	     if($land->[$sx][$sy] == $kind) {
		 $count++;
	     }
	 }
    }
    return $count;
}
# 範囲内の地形を数える
sub countAround {
    my($land, $x, $y, $kind, $range) = @_;
    my($i, $count, $sx, $sy);
    $count = 0;
    for($i = 0; $i < $range; $i++) {
	 $sx = $x + $ax[$i];
	 $sy = $y + $ay[$i];

	 # 行による位置調整
	 if((($sy % 2) == 0) && (($y % 2) == 1)) {
	     $sx--;
	 }

	 if(($sx < 0) || ($sx >= $HislandSize) ||
	    ($sy < 0) || ($sy >= $HislandSize)) {
	     # 範囲外の場合
	     if($kind == $HlandSea) {
		 # 海なら加算
		 $count++;
	     }
	 } else {
	     # 範囲内の場合
	     if($land->[$sx][$sy] == $kind) {
		 $count++;
	     }
	 }
    }
    return $count;
}

# 0から(n - 1)までの数字が一回づつ出てくる数列を作る
sub randomArray {
    my($n) = @_;
    my(@list, $i);

    # 初期値
    if($n == 0) {
	$n = 1;
    }
    @list = (0..$n-1);

    # シャッフル
    for ($i = $n; --$i; ) {
	my($j) = int(rand($i+1));
	if($i == $j) { next; };
	@list[$i,$j] = @list[$j,$i];
    }

    return @list;
}

# 名前変更失敗
sub tempChangeNothing {
    out(<<END);
${HtagBig_}名前、パスワードともに空欄です${H_tagBig}$HtempBack
END
}

# 名前変更資金足りず
sub tempChangeNoMoney {
    out(<<END);
${HtagBig_}資金不足のため変更できません${H_tagBig}$HtempBack
END
}

# 名前変更成功
sub tempChange {
    out(<<END);
${HtagBig_}変更完了しました${H_tagBig}$HtempBack
END
}

# 失業者がデモ
sub logUnemployedDemo {
    my($id, $name, $pop) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で仕事を求める<B>$pop${HunitPop}</B>がデモ行進を行いました。",$id);
}

# 失業者が暴動
sub logUnemployedRiot {
    my($id, $name, $lName, $pop, $point) = @_;
    logOut("${HtagName_}${name}島${H_tagName}で仕事を求める<B>$pop${HunitPop}</B>が暴動を起こして${HtagName_}$point${H_tagName}地点の<B>$lName</B>に<B>殺到</B>。<B>$lName</B>は壊滅しました。",$id);
}

# 失業者が移民
sub logUnemployedMigrate {
    my($id, $tId, $name, $tName, $pop) = @_;
    logOut("${HtagName_}${name}島${H_tagName}から${HtagName_}${tName}島${H_tagName}へ仕事を求める<B>$pop${HunitPop}</B>の移民が到着しました。${HtagName_}${tName}島${H_tagName}は快く受け入れたようです。",$id, $tId);
}

# 観光ありがとうございます
sub logKankouMigrate {
    my($id, $tId, $name, $lName, $tName, $point, $pop) = @_;
    logOut("${HtagName_}${tName}島${H_tagName}から${HtagName_}${name}島$point${H_tagName}の<B>$lName</B>へ<B>$pop${HunitPop}</B>の観光者が来てくれました。ありがとうございます。",$id, $tId);
}

# 失業者が移民
sub logUnemployedMigrate2 {
    my($id, $tId, $name, $tName, $pop) = @_;
    logOut("${HtagName_}${name}島${H_tagName}のリゾート施設は魅力不足により、${HtagName_}${tName}島${H_tagName}へ<B>$pop${HunitPop}</B>の観光者が移りました。",$id, $tId);
}

# 失業者が移民
sub logUnemployedMigrate3 {
    my($id, $tId, $name, $tName, $pop) = @_;
    logOut("${HtagName_}${name}島${H_tagName}のリゾート施設は魅力不足により、${HtagName_}${tName}島${H_tagName}へ<B>$pop${HunitPop}</B>の観光者が帰ってきました。おかえりなさい。",$id, $tId);
}

# 移民いやーん
sub logUnemployedReturn {
    my($id, $tId, $name, $lName, $tName, $pop) = @_;
    logOut("${HtagName_}${name}島${H_tagName}から${HtagName_}${tName}島${H_tagName}へ仕事を求める<B>$pop${HunitPop}</B>の移民が到着しましたが、${HtagName_}${tName}島${H_tagName}の<B>$lName</B>は受け入れを拒否したようです。",$id, $tId);
}

# 移民いやーん
sub logUnemployedReturn2 {
    my($id, $tId, $name, $lName, $tName, $pop) = @_;
    logOut("${HtagName_}${name}島${H_tagName}に飽きた<B>$pop${HunitPop}</B>の観光者は${HtagName_}${tName}島${H_tagName}へ観光にきました。しかし${HtagName_}${tName}島${H_tagName}の<B>$lName</B>は受け入れを拒否したようです。",$id, $tId);
}

1;

#----------------------------------------------------------------------
# 箱庭諸島 ver2.30
# 地図モードモジュール(ver1.00)
# 使用条件、使用方法等は、hako-readme.txtファイルを参照
#
# 箱庭諸島のページ: http://www.bekkoame.ne.jp/~tokuoka/hakoniwa.html
#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Hakoniwa R.A. ver1.11
# メインスクリプト(箱庭諸島 ver2.30)
# 使用条件、使用方法等は、read-renas.txtファイルを参照
#
# KEI PAGE: http://www5b.biglobe.ne.jp/~k-e-i/
#----------------------------------------------------------------------


#----------------------------------------------------------------------
# 観光モード
#----------------------------------------------------------------------
# メイン
sub printIslandMain {
    # 開放
    unlock();

    # idから島番号を取得
    $HcurrentNumber = $HidToNumber{$HcurrentID};

    # なぜかその島がない場合
    if($HcurrentNumber eq '') {
	tempProblem();
	return;
    }

    # 名前の取得
    $HcurrentName = $Hislands[$HcurrentNumber]->{'name'};

    # 観光画面
    tempPrintIslandHead(); # ようこそ!!
    islandInfo(); # 島の情報
    islandMap(0); # 島の地図、観光モード

    # ○○島ローカル掲示板
    if($HuseLbbs) {
	tempLbbsHead();     # ローカル掲示板
	tempLbbsInput();   # 書き込みフォーム
	tempLbbsContents(); # 掲示板内容
    }

    # 近況
    tempRecent(0);
}

#----------------------------------------------------------------------
# 開発モード
#----------------------------------------------------------------------
# メイン
sub ownerMain {
    # 開放
    unlock();

    # モードを明示
    $HmainMode = 'owner';

    # idから島を取得
    $HcurrentNumber = $HidToNumber{$HcurrentID};
    my($island) = $Hislands[$HcurrentNumber];
    $HcurrentName = $island->{'name'};

    if(checkPassword($masterPassword,$HinputPassword)) {
	$HmainMode2 = 'ijiri';
    }

    # パスワード
    if(!checkPassword($island->{'password'},$HinputPassword)) {
	# password間違い
	tempWrongPassword();
	return;
    }

    # 開発画面
    tempOwner(); # 「開発計画」

    # ○○島ローカル掲示板
    if($HuseLbbs) {
	tempLbbsHead();     # ローカル掲示板
	tempLbbsInputOW();   # 書き込みフォーム
	tempLbbsContents(); # 掲示板内容
    }

    # 近況
    tempRecent(1);
}

#----------------------------------------------------------------------
# コマンドモード
#----------------------------------------------------------------------
# メイン
sub commandMain {
    # idから島を取得
    $HcurrentNumber = $HidToNumber{$HcurrentID};
    my($island) = $Hislands[$HcurrentNumber];
    $HcurrentName = $island->{'name'};

    # パスワード
    if(!checkPassword($island->{'password'},$HinputPassword)) {
	# password間違い
	unlock();
	tempWrongPassword();
	return;
    }

    # モードで分岐
    my($command) = $island->{'command'};

    if($HcommandMode eq 'delete') {
	slideFront($command, $HcommandPlanNumber);
	tempCommandDelete();
    } elsif(($HcommandKind == $HcomAutoPrepare) ||
	    ($HcommandKind == $HcomAutoPrepare2)) {
	# フル整地、フル地ならし
	# 座標配列を作る
	makeRandomPointArray();
	my($land) = $island->{'land'};

	# コマンドの種類決定
	my($kind) = $HcomPrepare;
	if($HcommandKind == $HcomAutoPrepare2) {
	    $kind = $HcomPrepare2;
	}

	my($i) = 0;
	my($j) = 0;
	while(($j < $HpointNumber) && ($i < $HcommandMax)) {
	    my($x) = $Hrpx[$j];
	    my($y) = $Hrpy[$j];
	    if($land->[$x][$y] == $HlandWaste) {
		slideBack($command, $HcommandPlanNumber);
		$command->[$HcommandPlanNumber] = {
		    'kind' => $kind,
		    'target' => 0,
		    'x' => $x,
		    'y' => $y,
		    'arg' => 0
		    };
		$i++;
	    }
	    $j++;
	}
	tempCommandAdd();
    } elsif($HcommandKind == $HcomAutoReclaim) {
        # 浅瀬埋め立て
        makeRandomPointArray();
        my($land) = $island->{'land'};
        my($landValue) = $island->{'landValue'};

        my($x, $y, $kind, $lv, $i, $n);
        $n = 0;
        for ($i = 0; ($i < $HpointNumber) && ($n < $HcommandMax); $i++) {
            $x = $Hrpx[$i];
            $y = $Hrpy[$i];
            $kind = $land->[$x][$y];
            $lv = $landValue->[$x][$y];

            if (($kind == $HlandSea) && ($lv == 1)) {
                # 浅瀬
                slideBack($command, $HcommandPlanNumber);
                $command->[$HcommandPlanNumber] = {
                    'kind' => $HcomReclaim, # 埋め立て
                    'target' => 0,
                    'x' => $x,
                    'y' => $y,
                    'arg' => 0
                    };
                $n++;
            }
        }
        tempCommandAdd();
    } elsif($HcommandKind == $HcomAutoDestroy) {
        # 浅瀬掘削
        makeRandomPointArray();
        my($land) = $island->{'land'};
        my($landValue) = $island->{'landValue'};

        my($x, $y, $kind, $lv, $i, $n);
        $n = 0;
        for ($i = 0; ($i < $HpointNumber) && ($n < $HcommandMax); $i++) {
            $x = $Hrpx[$i];
            $y = $Hrpy[$i];
            $kind = $land->[$x][$y];
            $lv = $landValue->[$x][$y];

            if (($kind == $HlandSea) && ($lv == 1)) {
                # 浅瀬
                slideBack($command, $HcommandPlanNumber);
                $command->[$HcommandPlanNumber] = {
                    'kind' => $HcomDestroy, # 掘削
                    'target' => 0,
                    'x' => $x,
                    'y' => $y,
                    'arg' => 0
                    };
                $n++;
            }
        }
        tempCommandAdd();
    } elsif($HcommandKind == $HcomAutoSellTree) {
        # 伐採
        # （数量×２００本より多い森だけが対象）
        makeRandomPointArray();
        my($land) = $island->{'land'};
        my($landValue) = $island->{'landValue'};

        my($x, $y, $kind, $lv, $i, $n);
        $n = 0;
        for ($i = 0; ($i < $HpointNumber) && ($n < $HcommandMax - 1); $i++) {
            $x = $Hrpx[$i];
            $y = $Hrpy[$i];
            $kind = $land->[$x][$y];
            $lv = $landValue->[$x][$y];

            if (($kind == $HlandForest) && ($lv > $HcommandArg * 2)) {
                # 森
                slideBack($command, $HcommandPlanNumber);
                $command->[$HcommandPlanNumber] = {
                    'kind' => $HcomSellTree, # 伐採
                    'target' => 0,
                    'x' => $x,
                    'y' => $y,
                    'arg' => 0
                    };
                $n += 2;
            }
        }
        tempCommandAdd();
    } elsif($HcommandKind == $HcomAutoForestry) {
        # 伐採と植林
        # （数量×２００本より多い森だけが対象）
        makeRandomPointArray();
        my($land) = $island->{'land'};
        my($landValue) = $island->{'landValue'};

        my($x, $y, $kind, $lv, $i, $n);
        $n = 0;
        for ($i = 0; ($i < $HpointNumber) && ($n < $HcommandMax - 1); $i++) {
            $x = $Hrpx[$i];
            $y = $Hrpy[$i];
            $kind = $land->[$x][$y];
            $lv = $landValue->[$x][$y];

            if (($kind == $HlandForest) && ($lv > $HcommandArg * 2)) {
                # 森
                slideBack($command, $HcommandPlanNumber);
                $command->[$HcommandPlanNumber] = {
                    'kind' => $HcomPlant, # 植林
                    'target' => 0,
                    'x' => $x,
                    'y' => $y,
                    'arg' => 0
                    };
                slideBack($command, $HcommandPlanNumber);
                $command->[$HcommandPlanNumber] = {
                    'kind' => $HcomSellTree, # 伐採
                    'target' => 0,
                    'x' => $x,
                    'y' => $y,
                    'arg' => 0
                    };
                $n += 2;
            }
        }
        tempCommandAdd();
    } elsif($HcommandKind == $HcomAutoYoyaku) {
        # 開発予定計画自動入力
        makeRandomPointArray();
        my($land) = $island->{'land'};
        my($landValue) = $island->{'landValue'};

        my($x, $y, $kind, $lv, $i, $n);
        $n = 0;
        for ($i = 0; ($i < $HpointNumber) && ($n < $HcommandMax); $i++) {
            $x = $Hrpx[$i];
            $y = $Hrpy[$i];
            $kind = $land->[$x][$y];
            $lv = $landValue->[$x][$y];

            if ($kind == $HlandPlains) {
                slideBack($command, $HcommandPlanNumber);
                $command->[$HcommandPlanNumber] = {
                    'kind' => $HcomYoyaku, # 埋め立て
                    'target' => 0,
                    'x' => $x,
                    'y' => $y,
                    'arg' => 0
                    };
                $n++;
            }
        }
        tempCommandAdd();
    } elsif($HcommandKind == $HcomAutoUchuste) {
        # 開発予定計画自動入力
	if(($HcommandArg >= $HcommandMax) ||
	   ($HcommandArg == 0)) {
	    $HcommandArg = 1;
	}
        my($i);
	for($i = 0; $i < $HcommandArg; $i++) {
                slideBack($command, $HcommandPlanNumber);
                $command->[$HcommandPlanNumber] = {
                    'kind' => $HcomEiseimente, # 埋め立て
                    'target' => 0,
                    'x' => $x,
                    'y' => $y,
                    'arg' => 99
                    };
        }
        tempCommandAdd();
    } elsif($HcommandKind == $HcomAutoDelete) {
	# 全消し
	my($i);
	for($i = 0; $i < $HcommandMax; $i++) {
	    slideFront($command, $HcommandPlanNumber);
	}
	tempCommandDelete();
    } elsif($HcommandKind == $HcomIjiri) {

	if($lamount2 == '') {
	    $lamount2 = 0;
	}

	if($lamount1 == -1) {
	    $eisei5 = $island->{'eisei5'};
	    $eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tetsub) = ($1, $2, $3, $4, $5, $6, $7);
	    $island->{'eisei5'} = "$mshp,$msap,$msdp,$mssp,$mswin,$lamount2,$tetsub";
	} elsif($lamount1 == -2) {
            $island->{'eis7'} = $lamount2*100+99;
	} elsif($lamount1 == -3) {
	    $island->{'totoyoso2'} = "$lamount2";
	} elsif($lamount1 == -4) {
	    $island->{'eis6'} = "$lamount2";
	} elsif($lamount1 == -5) {
	    $island->{'eis5'} = "$lamount2";
	} elsif($lamount1 == -6) {
	    $island->{'eis4'} = "$lamount2";
	} elsif($lamount1 == -7) {
	    $island->{'eis3'} = "$lamount2";
	} elsif($lamount1 == -8) {
	    $island->{'eis2'} = "$lamount2";
	} elsif($lamount1 == -9) {
	    $island->{'eis1'} = "$lamount2";
	} elsif($lamount1 == -10) {
	    $etc8 = $island->{'etc8'};
	    $etc8 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($toto1, $toto2, $toto3, $toto4, $toto5, $toto6, $toto7) = ($1, $2, $3, $4, $5, $6, $7);
	    $island->{'etc8'} = "$toto1,$lamount2,$toto3,$toto4,$toto5,$toto6,$toto7";
	} elsif($lamount1 == -11) {
	    if($lamount2 > 15) {
		$lamount2 = 15;
	    }
	    $eisei5 = $island->{'eisei5'};
	    $eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tetsub) = ($1, $2, $3, $4, $5, $6, $7);
	    $island->{'eisei5'} = "$lamount2,$msap,$msdp,$mssp,$mswin,$msexe,$tetsub";
	} elsif($lamount1 == -12) {
	    $eisei5 = $island->{'eisei5'};
	    $eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tetsub) = ($1, $2, $3, $4, $5, $6, $7);
	    $island->{'eisei5'} = "$mshp,$lamount2,$msdp,$mssp,$mswin,$msexe,$tetsub";
	} elsif($lamount1 == -13) {
	    $eisei5 = $island->{'eisei5'};
	    $eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tetsub) = ($1, $2, $3, $4, $5, $6, $7);
	    $island->{'eisei5'} = "$mshp,$msap,$lamount2,$mssp,$mswin,$msexe,$tetsub";
	} elsif($lamount1 == -14) {
	    $eisei5 = $island->{'eisei5'};
	    $eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tetsub) = ($1, $2, $3, $4, $5, $6, $7);
	    $island->{'eisei5'} = "$mshp,$msap,$msdp,$lamount2,$mswin,$msexe,$tetsub";
	} elsif($lamount1 == -15) {
	    if($lamount2 > 30) {
		$lamount2 = 30;
	    }
	    if($lamount2 == 24) {
		$lamount2 = 7;
	    }
	    if($lamount2 == 25) {
		$lamount2 = 7;
	    }
	    if($lamount2 == 26) {
		$lamount2 = 7;
	    }
	    if($lamount2 == 27) {
		$lamount2 = 7;
	    }
	    $etc6 = $island->{'etc6'};
	    $etc6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($z0,$z1,$z2,$z3,$z4,$z5,$z6,$z7,$z8,$z9,$z10,$z11,$z12,$z13,$z14,$z15,$z16,$z17,$z18,$z19,$z20,$z21,$z22,$z23,$z24,$z25,$z26,$z27,$z28,$z29,$z30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
	    ($z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
	    if($HcommandArg == 1) {
		for($y2 = 0; $y2 < 24; $y2++) {
		    $z->{"$y2"}++;
		}
		for($y2 = 28; $y2 < 31; $y2++) {
		    $z->{"$y2"}++;
		}
		$island->{'etc6'} = "$z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}";
	    } elsif($HcommandArg > 1) {
		$z->{"$lamount2"} += $HcommandArg;
		$island->{'etc6'} = "$z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}";
	    } else {
		$z->{"$lamount2"}++;
		$island->{'etc6'} = "$z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}";
	    }
	} elsif($lamount1 == -16) {
	    my($sto, $std, $stk, $stwin, $stdrow, $stlose, $stwint, $stdrowt, $stloset, $styusho, $stshoka) = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
	    $eisei4 = $island->{'eisei4'};
	    $eisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($sto, $std, $stk, $stwin, $stdrow, $stlose, $stwint, $stdrowt, $stloset, $styusho, $stshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);
	    if($stshoka == 0) {
		$stshoka = 16;
            }
	    $island->{'eisei4'} = "$lamount2,$std,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
	} elsif($lamount1 == -17) {
	    my($sto, $std, $stk, $stwin, $stdrow, $stlose, $stwint, $stdrowt, $stloset, $styusho, $stshoka) = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
	    $eisei4 = $island->{'eisei4'};
	    $eisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($sto, $std, $stk, $stwin, $stdrow, $stlose, $stwint, $stdrowt, $stloset, $styusho, $stshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);
	    if($stshoka == 0) {
		$stshoka = 16;
            }
	    $island->{'eisei4'} = "$sto,$lamount2,$stk,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
	} elsif($lamount1 == -18) {
	    my($sto, $std, $stk, $stwin, $stdrow, $stlose, $stwint, $stdrowt, $stloset, $styusho, $stshoka) = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
	    $eisei4 = $island->{'eisei4'};
	    $eisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($sto, $std, $stk, $stwin, $stdrow, $stlose, $stwint, $stdrowt, $stloset, $styusho, $stshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);
	    if($stshoka == 0) {
		$stshoka = 16;
            }
	    $island->{'eisei4'} = "$sto,$std,$lamount2,$stwin,$stdrow,$stlose,$stwint,$stdrowt,$stloset,$styusho,$stshoka";
	} else {
	    my($land) = $island->{'land'};
	    my($landValue) = $island->{'landValue'};
	    if($lamount2 > 4000) {
		$lamount2 = 4000;
	    }
	    if($HcommandArg == 1) {
		for($y = 0; $y < $HislandSize; $y++) {
		    for($x = 0; $x < $HislandSize; $x++) {
			$land->[$x][$y] = $lamount1;
			$landValue->[$x][$y] = $lamount2;
		    }
		}
	    } else {
		$land->[$HcommandX][$HcommandY] = $lamount1;
		$landValue->[$HcommandX][$HcommandY] = $lamount2;
	    }
	}
    } else {
	if($HcommandMode eq 'insert') {
	    slideBack($command, $HcommandPlanNumber);
	}
	tempCommandAdd();
	# コマンドを登録
	$command->[$HcommandPlanNumber] = {
	    'kind' => $HcommandKind,
	    'target' => $HcommandTarget,
	    'x' => $HcommandX,
	    'y' => $HcommandY,
	    'arg' => $HcommandArg
	    };
    }

    # ＩＰ登録されてない場合、この時引き抜き
	$speaker = $ENV{'REMOTE_HOST'};
	$speaker = $ENV{'REMOTE_ADDR'} if ($speaker eq '');

    if($island->{'ip0'} eq '0') {
	# IPゲット
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
    }
    if($island->{'ip0'} eq '') {
	# IPゲット
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
    }

    if($island->{'ip5'} != "$speaker") {
	# IPゲット
	$island->{'ip1'} = $island->{'ip2'};
	$island->{'ip2'} = $island->{'ip3'};
	$island->{'ip3'} = $island->{'ip4'};
	$island->{'ip4'} = $island->{'ip5'};
	$island->{'ip5'} = "$speaker";
	$island->{'ip6'} = 0;
	$island->{'ip7'} = 0;
	$island->{'ip8'}++;
	$island->{'ip9'}++;
    }

    # データの書き出し
    writeIslandsFile($HcurrentID);

    # owner modeへ
    ownerMain();

}

#----------------------------------------------------------------------
# コメント入力モード
#----------------------------------------------------------------------
# メイン
sub commentMain {
    # idから島を取得
    $HcurrentNumber = $HidToNumber{$HcurrentID};
    my($island) = $Hislands[$HcurrentNumber];
    $HcurrentName = $island->{'name'};

    # パスワード
    if(!checkPassword($island->{'password'},$HinputPassword)) {
	# password間違い
	unlock();
	tempWrongPassword();
	return;
    }

    # メッセージを更新
    $island->{'comment'} = htmlEscape($Hmessage);

    # データの書き出し
    writeIslandsFile($HcurrentID);

    # コメント更新メッセージ
    tempComment();

    # owner modeへ
    ownerMain();
}

#----------------------------------------------------------------------
# toto入力モード
#----------------------------------------------------------------------
# メイン
sub totoMain {
    # idから島を取得
    $HcurrentNumber = $HidToNumber{$HcurrentID};
    my($island) = $Hislands[$HcurrentNumber];
    $HcurrentName = $island->{'name'};

    foreach $i (76..99) {
        if(($HislandTurn % 100) == $i) {
	unlock();
	tempTotoend();
	return;
        }
    }

    foreach $i (26..49) {
        if(($HislandTurn % 100) == $i) {
	unlock();
	tempTotoend();
	return;
        }
    }

    # パスワード
    if(!checkPassword($island->{'password'},$HinputPassword)) {
	# password間違い
	unlock();
	tempWrongPassword();
	return;
    }

    # メッセージを更新
    $island->{'eis8'} = htmlEscape($HyosoMessage);

    # データの書き出し
    writeIslandsFile($HcurrentID);

    # コメント更新メッセージ
    tempToto();

    # owner modeへ
    ownerMain();
}

#----------------------------------------------------------------------
# totos入力モード
#----------------------------------------------------------------------
# メイン
sub totosMain {
    # idから島を取得
    $HcurrentNumber = $HidToNumber{$HcurrentID};
    my($island) = $Hislands[$HcurrentNumber];
    $HcurrentName = $island->{'name'};

    # パスワード
    if(!checkPassword($island->{'password'},$HinputPassword)) {
	# password間違い
	unlock();
	tempWrongPassword();
	return;
    }

    # メッセージを更新
    $island->{'totoyoso2'} = htmlEscape($HshutoMessage);

    # データの書き出し
    writeIslandsFile($HcurrentID);

    # コメント更新メッセージ
    tempToto2();

    # owner modeへ
    ownerMain();
}
#----------------------------------------------------------------------
# 政策入力モード
#----------------------------------------------------------------------
# メイン
sub shoueneMain {
    # idから島を取得
    $HcurrentNumber = $HidToNumber{$HcurrentID};
    my($island) = $Hislands[$HcurrentNumber];
    $HcurrentName = $island->{'name'};

    # パスワード
    if(!checkPassword($island->{'password'},$HinputPassword)) {
	# password間違い
	unlock();
	tempWrongPassword();
	return;
    }

    if($island->{'etc5'} == 0) {
	$island->{'etc5'} = '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0';
    }

    if($HcommandArg > 50) {
	$HcommandArg = 50;
    }

    # メッセージを更新
    $etc5 = $island->{'etc5'};
    $etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

    $island->{'etc5'} = "$s00,$HcommandArg,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30";

    # データの書き出し
    writeIslandsFile($HcurrentID);

    # コメント更新メッセージ
    tempToto2();

    # owner modeへ
    ownerMain();
}
sub bousaiMain {
    # idから島を取得
    $HcurrentNumber = $HidToNumber{$HcurrentID};
    my($island) = $Hislands[$HcurrentNumber];
    $HcurrentName = $island->{'name'};

    # パスワード
    if(!checkPassword($island->{'password'},$HinputPassword)) {
	# password間違い
	unlock();
	tempWrongPassword();
	return;
    }

    if($island->{'etc5'} == 0) {
	$island->{'etc5'} = '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0';
    }

    if($HcommandArg > 50) {
	$HcommandArg = 50;
    }

    # メッセージを更新
    $etc5 = $island->{'etc5'};
    $etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

    $island->{'etc5'} = "$s00,$s01,$s02,$HcommandArg,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30";

    # データの書き出し
    writeIslandsFile($HcurrentID);

    # コメント更新メッセージ
    tempToto2();

    # owner modeへ
    ownerMain();
}
sub kankouMain {
    # idから島を取得
    $HcurrentNumber = $HidToNumber{$HcurrentID};
    my($island) = $Hislands[$HcurrentNumber];
    $HcurrentName = $island->{'name'};

    # パスワード
    if(!checkPassword($island->{'password'},$HinputPassword)) {
	# password間違い
	unlock();
	tempWrongPassword();
	return;
    }

    if($island->{'etc5'} == 0) {
	$island->{'etc5'} = '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0';
    }

    if($HcommandArg > 50) {
	$HcommandArg = 50;
    }

    # メッセージを更新
    $etc5 = $island->{'etc5'};
    $etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

    $island->{'etc5'} = "$s00,$s01,$s02,$s03,$s04,$HcommandArg,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30";

    # データの書き出し
    writeIslandsFile($HcurrentID);

    # コメント更新メッセージ
    tempToto2();

    # owner modeへ
    ownerMain();
}
sub sizenMain {
    # idから島を取得
    $HcurrentNumber = $HidToNumber{$HcurrentID};
    my($island) = $Hislands[$HcurrentNumber];
    $HcurrentName = $island->{'name'};

    # パスワード
    if(!checkPassword($island->{'password'},$HinputPassword)) {
	# password間違い
	unlock();
	tempWrongPassword();
	return;
    }

    if($island->{'etc5'} == 0) {
	$island->{'etc5'} = '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0';
    }

    if($HcommandArg > 50) {
	$HcommandArg = 50;
    }

    # メッセージを更新
    $etc5 = $island->{'etc5'};
    $etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

    $island->{'etc5'} = "$s00,$s01,$s02,$s03,$s04,$s05,$s06,$HcommandArg,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30";

    # データの書き出し
    writeIslandsFile($HcurrentID);

    # コメント更新メッセージ
    tempToto2();

    # owner modeへ
    ownerMain();
}
sub kyouikuMain {
    # idから島を取得
    $HcurrentNumber = $HidToNumber{$HcurrentID};
    my($island) = $Hislands[$HcurrentNumber];
    $HcurrentName = $island->{'name'};

    # パスワード
    if(!checkPassword($island->{'password'},$HinputPassword)) {
	# password間違い
	unlock();
	tempWrongPassword();
	return;
    }

    if($island->{'etc5'} == 0) {
	$island->{'etc5'} = '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0';
    }

    if($HcommandArg > 50) {
	$HcommandArg = 50;
    }

    # メッセージを更新
    $etc5 = $island->{'etc5'};
    $etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

    $island->{'etc5'} = "$s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$HcommandArg,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30";

    # データの書き出し
    writeIslandsFile($HcurrentID);

    # コメント更新メッセージ
    tempToto2();

    # owner modeへ
    ownerMain();
}
sub chochikuMain {
    # idから島を取得
    $HcurrentNumber = $HidToNumber{$HcurrentID};
    my($island) = $Hislands[$HcurrentNumber];
    $HcurrentName = $island->{'name'};

    # パスワード
    if(!checkPassword($island->{'password'},$HinputPassword)) {
	# password間違い
	unlock();
	tempWrongPassword();
	return;
    }

    if($island->{'etc5'} == 0) {
	$island->{'etc5'} = '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0';
    }

    if($HcommandArg > 50) {
	$HcommandArg = 50;
    }

    # メッセージを更新
    $etc5 = $island->{'etc5'};
    $etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
    ($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

    $island->{'etc5'} = "$s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$HcommandArg,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30";

    # データの書き出し
    writeIslandsFile($HcurrentID);

    # コメント更新メッセージ
    tempToto2();

    # owner modeへ
    ownerMain();
}

#----------------------------------------------------------------------
# オークション入力モード
#----------------------------------------------------------------------

sub auctionMain {
    # idから島を取得
    $HcurrentNumber = $HidToNumber{$HcurrentID};
    my($island) = $Hislands[$HcurrentNumber];
    $HcurrentName = $island->{'name'};

    # パスワード
    if(!checkPassword($island->{'password'},$HinputPassword)) {
	# password間違い
	unlock();
	tempWrongPassword();
	return;
    }

    if($HAucNumber == 1) {

	if(($island->{'auc2'} != 0) || ($island->{'auc3'} != 0)) {
		unlock();
		tempNoMoney3();
		return;
	}

	    $auction1 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($shuppin1, $avalue1, $ajoutai1, $topvalue1, $topid1) = ($1, $2, $3, $4, $5);

	    if(($island->{'auc1'} == $topvalue1) && ($topvalue1 != 0)) {
		unlock();
		tempNoMoney2();
		return;
	    }

	    if($ajoutai1 == 15) {
		unlock();
		tempNoMoney4();
		return;
	    }

	    $topvalue1 += $HcommandArg;

	    $auc9 = $island->{'auc9'};
	    $auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);
	    $auc9c3 = int($auc9c/10000)*10000;

	    if($island->{'money'} + $island->{'pika'} + $auc9a*10000 < $topvalue1*10000) {
		unlock();
		tempNoMoney();
		return;
	    }

	    $auction1 = "$shuppin1,$avalue1,0,$topvalue1,$topid1";
	    $island->{'auc1'} = $topvalue1;

	    if((($HislandTurn % $HturnPrizeUnit) > 89) && (random(100) < 3)) {
		$ajoutai1 = 15;
		$auction1 = "$shuppin1,$avalue1,$ajoutai1,$topvalue1,$topid1";
	    }

	    # データの書き出し
	    writeIslandsFile($HcurrentID);

	    # コメント更新メッセージ
	    tempToto3();

	    # owner modeへ
	    ownerMain();

    }

    elsif($HAucNumber == 2) {

	if(($island->{'auc1'} != 0) || ($island->{'auc3'} != 0)) {
		unlock();
		tempNoMoney3();
		return;
	}

	    $auction2 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($shuppin2, $avalue2, $ajoutai2, $topvalue2, $topid2) = ($1, $2, $3, $4, $5);

	    if(($island->{'auc2'} == $topvalue2) && ($topvalue2 != 0)) {
		unlock();
		tempNoMoney2();
		return;
	    }

	    if($ajoutai2 == 15) {
		unlock();
		tempNoMoney4();
		return;
	    }

	    $topvalue2 += $HcommandArg;

	    $auc9 = $island->{'auc9'};
	    $auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);
	    $auc9c3 = int($auc9c/10000)*10000;

	    if($island->{'money'} + $island->{'pika'} + $auc9a*10000 < $topvalue2*10000) {
		unlock();
		tempNoMoney();
		return;
	    }

	    $auction2 = "$shuppin2,$avalue2,0,$topvalue2,$topid2";
	    $island->{'auc2'} = $topvalue2;

	    if((($HislandTurn % $HturnPrizeUnit) > 89) && (random(100) < 3)) {
		$ajoutai2 = 15;
		$auction2 = "$shuppin2,$avalue2,$ajoutai2,$topvalue2,$topid2";
	    }

	    # データの書き出し
	    writeIslandsFile($HcurrentID);

	    # コメント更新メッセージ
	    tempToto3();

	    # owner modeへ
	    ownerMain();

    }

    elsif($HAucNumber == 3) {

	if(($island->{'auc1'} != 0) || ($island->{'auc2'} != 0)) {
		unlock();
		tempNoMoney3();
		return;
	}

	    $auction3 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($shuppin3, $avalue3, $ajoutai3, $topvalue3, $topid3) = ($1, $2, $3, $4, $5);

	    if(($island->{'auc3'} == $topvalue3) && ($topvalue3 != 0)) {
		unlock();
		tempNoMoney2();
		return;
	    }

	    if($ajoutai3 == 15) {
		unlock();
		tempNoMoney4();
		return;
	    }

	    $topvalue3 += $HcommandArg;

	    $auc9 = $island->{'auc9'};
	    $auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    ($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);
	    $auc9c3 = int($auc9c/10000)*10000;

	    if($island->{'money'} + $island->{'pika'} + $auc9a*10000 < $topvalue3*10000) {
		unlock();
		tempNoMoney();
		return;
	    }

	    $auction3 = "$shuppin3,$avalue3,0,$topvalue3,$topid3";
	    $island->{'auc3'} = $topvalue3;

	    if((($HislandTurn % $HturnPrizeUnit) > 89) && (random(100) < 3)) {
		$ajoutai3 = 15;
		$auction3 = "$shuppin3,$avalue3,$ajoutai3,$topvalue3,$topid3";
	    }

	    # データの書き出し
	    writeIslandsFile($HcurrentID);

	    # コメント更新メッセージ
	    tempToto3();

	    # owner modeへ
	    ownerMain();

    }

}

#----------------------------------------------------------------------
# mskyoka入力モード
#----------------------------------------------------------------------
# メイン
sub msMain {
    # idから島を取得
    $HcurrentNumber = $HidToNumber{$HcurrentID};
    my($island) = $Hislands[$HcurrentNumber];
    $HcurrentName = $island->{'name'};

    # パスワード
    if(!checkPassword($island->{'password'},$HinputPassword)) {
	# password間違い
	unlock();
	tempWrongPassword();
	return;
    }

    # メッセージを更新
    $island->{'etc7'} = "1,$HcommandArg,$HcommandTarget";

    if ($HcommandArg == 0) {
	$island->{'etc7'} = '0,0,0';
    }

    # データの書き出し
    writeIslandsFile($HcurrentID);

    # コメント更新メッセージ
    tempMs();

    # owner modeへ
    ownerMain();
}

#----------------------------------------------------------------------
# ms2kyoka入力モード
#----------------------------------------------------------------------
# メイン
sub ms2Main {
    # idから島を取得
    $HcurrentNumber = $HidToNumber{$HcommandTarget};
    my($island) = $Hislands[$HcurrentNumber];
    $HcurrentName = $island->{'name'};

    $etc7 = $island->{'etc7'};
    $etc7 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
    ($msjotai, $nokotan, $msid) = ($1, $2, $3);

    if ($msjotai == 1) {
    $island->{'etc7'} = "2,$HcommandArg,$HcurrentID";

    # データの書き出し
    writeIslandsFile($HcurrentID);

    # コメント更新メッセージ
    tempMs();

    }

    # owner modeへ
    ownerMain();

}

#----------------------------------------------------------------------
# ローカル掲示板モード
#----------------------------------------------------------------------
# メイン

sub localBbsMain {
    # idから島番号を取得
    $HcurrentNumber = $HidToNumber{$HcurrentID};
    my($island) = $Hislands[$HcurrentNumber];
    my($speaker) = "0<";


    # なぜかその島がない場合
    if($HcurrentNumber eq '') {
	unlock();
	tempProblem();
	return;
    }

    # 削除モードじゃなくて名前かメッセージがない場合
    if($HlbbsMode != 2) {
	if(($HlbbsName eq '') || ($HlbbsName eq '')) {
	    unlock();
	    tempLbbsNoMessage();
	    return;
	}
    }

    # 観光者モードじゃない時はパスワードチェック
    if($HlbbsMode != 0) {
	if(!checkPassword($island->{'password'},$HinputPassword)) {
	    # password間違い
	    unlock();
	    tempWrongPassword();
	    return;
	}
    }

    elsif ($HlbbsMode == 0) {
        # 観光者モード
        my($island);

        if ($HlbbsType ne 'ANON') {
            # 公開と極秘

            # idから島番号を取得
            my($number) = $HidToNumber{$HspeakerID};
            $island = $Hislands[$number];

            # なぜかその島がない場合
            if($number eq '') {
                unlock();
                tempProblem();
                return;
            }

            # パスワードチェック
            if(!checkPassword($island->{'password'},$HinputPassword)) {
                # password間違い
                unlock();
                tempWrongPassword();
                return;
            }

            # 通信費用を払う
            my($cost) = ($HlbbsType eq 'PUBLIC') ? $HlbbsMoneyPublic : $HlbbsMoneySecret;
            if (($HlbbsType eq 'SECRET') && ($island->{'money'} < $cost)) {
                # 費用不足
                unlock();
                tempLbbsNoMoney();
                return;
            }
            $island->{'money'} -= $cost;
        }

        # 発言者を記憶する
        if ($HlbbsType ne 'ANON') {
            # 公開と極秘
            $speaker = $island->{'name'} . '島';
        } else {
            # 匿名
            $speaker = $ENV{'REMOTE_HOST'};
            $speaker = $ENV{'REMOTE_ADDR'} if ($speaker eq '');
        }
        if ($HlbbsType ne 'SECRET') {
            # 公開と匿名
            $speaker = "0<$speaker";
        } else {
            # 極秘
            $speaker = "1<$speaker";
        }
    }

    my($lbbs);
    $lbbs = $island->{'lbbs'};

    # モードで分岐
    if($HlbbsMode == 2) {
	# 削除モード
	# メッセージを前にずらす
	slideBackLbbsMessage($lbbs, $HcommandPlanNumber);
	tempLbbsDelete();
    } else {
	# 記帳モード
	# メッセージを後ろにずらす
	slideLbbsMessage($lbbs);

	# メッセージ書き込み
	my($message);
	if($HlbbsMode == 0) {
	    $message = '0';
	} else {
	    $message = '1';
	}
	$HlbbsName = "$HislandTurn：" . htmlEscape($HlbbsName);
	$HlbbsMessage = htmlEscape($HlbbsMessage);
        $lbbs->[0] = "$speaker<$message>$HlbbsName>$HlbbsMessage";

	tempLbbsAdd();
    }

    # データ書き出し
    writeIslandsFile($HcurrentID);

    # もとのモードへ
    if($HlbbsMode == 0) {
	printIslandMain();
    } else {
	ownerMain();
    }
}

sub changeAnkeito {

  $HcurrentNumber = $HidToNumber{$HcurrentID};
  my($island) = $Hislands[$HcurrentNumber];

  if(!checkPassword($island->{'password'},$HinputPassword)) {
    # password間違い
    unlock();
    tempWrongPassword();
    return;
  }

  if($AnnType == '') {
    unlock();
    tempWrongPassword6();
    return;
  }

  if($island->{'anflag'} == 2) {
    unlock();
    tempWrongPassword4();
    return;
  }

  if($AnnType == 1) {
    $an1++;
  } elsif($AnnType == 2) {
    $an2++;
  } elsif($AnnType == 3) {
    $an3++;
  } elsif($AnnType == 4) {
    $an4++;
  } elsif($AnnType == 5) {
    $an5++;
  }

    $island->{'anflag'} = 2;

    # データ書き出し
    writeIslandsFile($HcurrentID);
    unlock();

    # 変更成功
    tempChange2();

}

# ローカル掲示板のメッセージを一つ後ろにずらす
sub slideLbbsMessage {
    my($lbbs) = @_;
    my($i);
#    pop(@$lbbs);
#    push(@$lbbs, $lbbs->[0]);
    pop(@$lbbs);
    unshift(@$lbbs, $lbbs->[0]);
}

# ローカル掲示板のメッセージを一つ前にずらす
sub slideBackLbbsMessage {
    my($lbbs, $number) = @_;
    my($i);
    splice(@$lbbs, $number, 1);
    $lbbs->[$HlbbsMax - 1] = '0<<0>>';
}

#----------------------------------------------------------------------
# 島の地図
#----------------------------------------------------------------------

# 情報の表示
sub islandInfo {
    my($island) = $Hislands[$HcurrentNumber];
    # 情報表示
    my($rank) = $HcurrentNumber + 1;
    my($pop) = $island->{'pop'};
    my($farm) = $island->{'farm'};
    my($factory) = $island->{'factory'};
	$factory =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($factory1, $factory2, $co0, $co1, $htf, $shtf, $co95, $co95, $co95, $co95) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10);
	$factoryt = $factory1 + $factory2;
    my($mountain) = $island->{'mountain'};
    my($pts) = $island->{'pts'};
    my($rena) = $rena = $island->{'rena'};
       $renae = int($rena / 10 ) + 1;
    my($unemployed);
    $unemployed = ($island->{'pop'} - ($farm + $factoryt + $mountain) * 10) / $island->{'pop'} * 100;
    $unemployed = '<font color="' . ($unemployed < 0 ? 'black' : 'red') . '">' . sprintf("%.2f%%", $unemployed) . '</font>';

    my($foodincome, $htincome, $moneyincome) = (0, 0, 0);

    # 収入
    if($pop > $farm * 10) {
	# 農業だけじゃ手が余る場合
	$foodincome += $farm * 10 * ($co0 + 1); # 農場フル稼働

	    if($factory2 * 10 > ($pop - $farm * 10)) {

		    $auc9 = $island->{'auc9'};
		    $auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);

			$htincome += int(($pop - $farm * 10) / 10);

	    } else {

		    $auc9 = $island->{'auc9'};
		    $auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		    ($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);

			$htincome += $factory2;
			$moneyincome +=
			    min(int(($pop - $farm * 10 - $factory2*10) / 10),
				 $factory1 + $mountain) * ($co1 + 1);
	    }

    } else {
	# 農業だけで手一杯の場合
	$foodincome += $pop * ($co0 + 1); # 全員野良仕事
    }


    $farm1b = ($foodincome == 0) ? "食料見込みなし" : "食料＋${foodincome}$HunitFood";
    $factory1 = ($factory1 == 0) ? "保有せず" : "${factory1}0$HunitPop";
    $factory1b = ($moneyincome == 0) ? "資金見込みなし" : "資金＋${moneyincome}$HunitMoney";
    $factory2 = ($factory2 == 0) ? "保有せず" : "${factory2}0$HunitPop";
    $factory2b = ($htincome == 0) ? "補助金見込みなし" : "補助金＋${htincome}$HunitMoney";

	$alt = "収入見込み";
	$alt2 = "普通職場…$factory1<br>ＨＴ職場…$factory2<hr>$farm1b<br>$factory1b<br>$factory2b";


    $farm = ($farm == 0) ? "保有せず" : "<p onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi2($HislandSize, 'black.gif', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">${farm}0$HunitPop</p>";
    $factoryt = ($factoryt == 0) ? "保有せず" : "<p onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi2($HislandSize, 'black.gif', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">${factoryt}0$HunitPop</p>";
    $mountain = ($mountain == 0) ? "保有せず" : "<p onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi2($HislandSize, 'black.gif', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">${mountain}0$HunitPop</p>";
    $pts = ($pts == 0) ? "0pts." : "${pts}pts.";
    $monsterlive = $island->{'monsterlive'};
    $monsi = ($monsterlive == 0) ? "" : "${monsterlive}$HunitMonster";
    $monsm = ($monsterlive == 0) ? "" : "${monsterlive}$HunitMonster出現中!!";


	$auc9 = $island->{'auc9'};
	$auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);

	$auc9c2 = int($auc9c/10000);

	$alt = "へそくり";
	$alt2 = "貯金…$auc9b兆円<br>Auction補助金…$auc9c2兆円<hr>合計…$auc9a兆円";
	$image2 = 'auc.gif';

	if ($auc9a >= 1)
	    {$auchojo = "＋<IMG SRC=\"auc.gif\" ALT=\"へそくり\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi2($HislandSize, '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">"};
	if ($auc9a == 0)
	    {$auchojo = ""};


    my($mStr1) = '';
    my($mStr2) = '';
    if(($HhideMoneyMode == 1) || ($HmainMode eq 'owner')) {
	# 無条件またはownerモード
	$mStr1 = "<TH $HbgTitleCell nowrap=nowrap><NOBR>${HtagTH_}資金${H_tagTH}</NOBR></TH>";
	$mStr2 = "<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>$island->{'money'}$HunitMoney$auchojo</NOBR></TD>";
    } elsif($HhideMoneyMode == 2) {
	my($mTmp) = aboutMoney($island->{'money'});

	# 1000億単位モード
	$mStr1 = "<TH $HbgTitleCell nowrap=nowrap><NOBR>${HtagTH_}資金${H_tagTH}</NOBR></TH>";
	$mStr2 = "<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>$mTmp$auchojo</NOBR></TD>";
    }


	$eisei3 = $island->{'eisei3'};
	$eisei3 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($ene, $shouhi, $sabun, $chikuden, $ene) = ($1, $2, $3, $4, $5);
	$sabun = $ene-$shouhi;
	if ($sabun < 0)
	    {$sabun2 = "<font color=red>不足中！</font>"};
	if ($sabun >= 0)
	    {$sabun2 = ""};

	$alt = "使用状況";
	$alt2 = "消費$shouhi万ｋＷ<br>過不足$sabun万ｋＷ";
	$image2 = "ele.gif";

	$eleinfo = "<IMG SRC=\"ele.gif\" ALT=\"使用状況(消費$shouhi万ｋＷ／過不足$sabun万ｋＷ)\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi2($HislandSize, '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">$sabun2";
	$island->{'ene'} = $ene;


	$prize = $island->{'prize'};
	my($flags, $monsters, $turns);
	$prize =~ /([0-9]*),([0-9]*),(.*)/;
	$flags = $1;
	$monsters= $2;
	$turns = $3;
	$prize = '';

        # ターン杯の表示
        my($alt);
        while($turns =~ s/([0-9]*),//) {
            $alt .= "$1${Hprize[0]} ";
        }
        $prize .= "<IMG SRC=\"prize0.gif\" ALT=\"$alt\" WIDTH=16 HEIGHT=16> " if ($alt ne '');

	# 名前に賞の文字を追加
	my($f) = 1;
	my($i);
	for($i = 1; $i < 10; $i++) {
	    if($flags & $f) {
		$prize .= "<IMG SRC=\"prize${i}.gif\" ALT=\"${Hprize[$i]}\" WIDTH=16 HEIGHT=16> ";
	    }
	    $f *= 2;
	}

	# 倒した怪獣リスト
	$f = 1;
	my($max) = -1;
	my($mNameList) = '';
	for($i = 0; $i < $HmonsterNumber; $i++) {
	    if($monsters & $f) {
		$mNameList .= "[$HmonsterName[$i]] ";
		$max = $i;
	    }
	    $f *= 2;
	}
	if($max != -1) {
	    $prize .= "<IMG SRC=\"${HmonsterImage[$max]}\" ALT=\"$mNameList\" WIDTH=16 HEIGHT=16>$island->{'taiji'}$HunitMonster退治";
	}

        # 出現中の怪獣リスト
        $f = 1;
        $max = -1;
        $mNameList = '';
        my($monslivetype) = $island->{'monsterlivetype'};
        my($monsliveimg);
        for($i = 0; $i < $HmonsterNumber; $i++) {
            if($monslivetype & $f) {
                $mNameList .= "[$HmonsterName[$i]] ";
                $max = $i;
            }
            $f *= 2;
        }
        if($max != -1) {
            $monsliveimg = "<IMG SRC=\"${HmonsterImage[$max]}\" ALT=\"$mNameList\" WIDTH=16 HEIGHT=16> ";
        }

	# 人工衛星打ち上げ
	my($me_sat) = "";
	$eis1 = $island->{'eis1'};
	$eis2 = $island->{'eis2'};
	$eis3 = $island->{'eis3'};
	$eis4 = $island->{'eis4'};
	$eis5 = $island->{'eis5'};
	$eis6 = $island->{'eis6'};
	$eis7 = $island->{'eis7'};
	    $cstpop = int($eis7/100);
	    $csten = $eis7%100+1;
	    $csroke = int($cstpop/10000)+1;
	if ($eis1 >= 1)
	    {$me_sat .= "<IMG SRC=\"kisho.gif\" ALT=\"気象衛星\" WIDTH=16 HEIGHT=\"16\">$eis1%"};
	if ($eis2 >= 1)
	    {$me_sat .= "<IMG SRC=\"kansoku.gif\" ALT=\"観測衛星\" WIDTH=16 HEIGHT=\"16\">$eis2%"};
	if ($eis3 >= 1)
	    {$me_sat .= "<IMG SRC=\"geigeki.gif\" ALT=\"迎撃衛星\" WIDTH=16 HEIGHT=\"16\">$eis3%"};
	if ($eis4 >= 1)
	    {$me_sat .= "<IMG SRC=\"gunji.gif\" ALT=\"軍事衛星\" WIDTH=16 HEIGHT=\"16\">$eis4%"};
	if ($eis5 >= 1)
	    {$me_sat .= "<IMG SRC=\"bouei.gif\" ALT=\"防衛衛星\" WIDTH=16 HEIGHT=\"16\">$eis5%"};
	if ($eis6 >= 1)
	    {$me_sat .= "<IMG SRC=\"ire.gif\" ALT=\"イレギュラー\" WIDTH=16 HEIGHT=\"16\">$eis6%"};

		$alt = "宇宙ステーション";
		$alt2 = "$cstpop$HunitPop滞在<br>人口維持ロケット数…$csroke個<br>人口維持コスト…$cstpop$HunitMoney";
		$image2 = "cst.gif";

	if ($eis7 >= 1)
	    {$me_sat .= "<IMG SRC=\"cst.gif\" ALT=\"宇宙ステーション／$cstpop$HunitPop滞在\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi2($HislandSize, '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">$csten%"};
	if ($eis1 == 0 && $eis2 == 0 && $eis3 == 0 && $eis4 == 0 && $eis5 == 0 && $eis6 == 0 && $eis7 == 0)
	    {$me_sat = ""};

	# 牧場系
	my($Farmcpc) = "";
	$tare = $island->{'tare'};
	$zipro = $island->{'zipro'};
	$leje = $island->{'leje'};
	if ($tare >= 1)
	    {$Farmcpc .= "<IMG SRC=\"niwatori.gif\" ALT=\"にわとり\" WIDTH=16 HEIGHT=\"16\">$tare万羽"};
	if ($zipro >= 1)
	    {$Farmcpc .= "<IMG SRC=\"buta.gif\" ALT=\"ぶた\" WIDTH=16 HEIGHT=\"16\">$zipro万頭"};
	if ($leje >= 1)
	    {$Farmcpc .= "<IMG SRC=\"ushi.gif\" ALT=\"うし\" WIDTH=16 HEIGHT=\"16\">$leje万頭"};
	if ($tare == 0 && $zipro == 0 && $leje == 0)
	    {$Farmcpc = ""};

	$eisei6 = $island->{'eisei6'};
	$eisei6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($unimika, $unishuto, $unimeka, $unioumu, $unianseki, $unitiseki, $unihyouseki, $unifuseki, $unienseki, $unikouseki, $uniiseki, $uniden) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12);
	$etc8 = $island->{'etc8'};
	$etc8 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($toto1, $toto2, $toto3, $toto4, $toto5, $toto6, $toto7) = ($1, $2, $3, $4, $5, $6, $7);

	# 家
	my($house) = "";
	$eisei1 = $island->{'eisei1'};
	$pts = $island->{'pts'};
	        if(($island->{'pts'} > $HouseLevel9) && ($unienseki>0) && ($unitiseki>0) && ($unihyouseki>0) && ($unifuseki>0) && ($unimika>0) && ($unishuto>0) && ($unimeka>0) && ($unioumu>0) && ($uniiseki>0) && ($toto2>0)) {
		    $hlv = 9;
			if(($unikouseki>0) || ($unianseki>0)) {
			$hlv = 11;
				if($unianseki >= $unikouseki) {
				$hlv = 10;
				}
			}
	        } elsif($island->{'pts'} > $HouseLevel9) {
	 	    $hlv = 9;
	        } elsif($island->{'pts'} > $HouseLevel8) {
	 	    $hlv = 8;
	        } elsif($island->{'pts'} > $HouseLevel7) {
		    $hlv = 7;
	        } elsif($island->{'pts'} > $HouseLevel6) {
	 	    $hlv = 6;
	        } elsif($island->{'pts'} > $HouseLevel5) {
		    $hlv = 5;
	        } elsif($island->{'pts'} > $HouseLevel4) {
	 	    $hlv = 4;
	        } elsif($island->{'pts'} > $HouseLevel3) {
		    $hlv = 3;
	        } elsif($island->{'pts'} > $HouseLevel2) {
	 	    $hlv = 2;
	        } elsif($island->{'pts'} > $HouseLevel1) {
		    $hlv = 1;
	        } else {
		    $hlv = 0;
	        }
	$onm = $island->{'onm'};
	if($hlv == 0) {
	    $n = 'の小屋';
	} elsif($hlv == 1) {
	    $n = 'の簡易住宅';
	} elsif($hlv == 2) {
	    $n = 'の住宅';
	} elsif($hlv == 3) {
	    $n = 'の高級住宅';
	} elsif($hlv == 4) {
	    $n = 'の豪邸';
	} elsif($hlv == 5) {
	    $n = 'の大豪邸';
	} elsif($hlv == 6) {
	    $n = 'の高級豪邸';
	} elsif($hlv == 7) {
	    $n = 'の城';
	} elsif($hlv == 8) {
	    $n = 'の巨城';
	} elsif($hlv == 9) {
	    $n = 'の黄金城';
	} elsif($hlv == 10) {
	    $n = 'の魔塔';
	} else {
	    $n = 'の天空城';
	}

	$zeikin = int($island->{'pop'}*($hlv+1)*$eisei1/100);

	$alt = "$onm$n";
	$alt2 = "税率$eisei1％($zeikin$HunitMoney)";
	$image2 = "house${hlv}.gif";

	if ($eisei1 > 0)
	    {$house .= "<IMG SRC=\"house${hlv}.gif\" ALT=\"$onm$n\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi2($HislandSize, '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">税率$eisei1％($zeikin$HunitMoney)"};
	if ($eisei1 == 0)
	    {$house = ""};

	$totoyoso2 = $island->{'totoyoso2'};
	if ($totoyoso2 == 0)
	    {$shutohen .= "<INPUT TYPE=\"submit\" VALUE=\"首都名変更\" NAME=\"TotosButton$Hislands[$HcurrentNumber]->{'id'}\">"};
	if ($totoyoso2 == 555)
	    {$shutohen = ""};

	$kakushuyoso = "";
        if (((($HislandTurn % 100) >= 0) && ((($HislandTurn % 100) < 26))) || ((($HislandTurn % 100) >= 50) && ((($HislandTurn % 100) < 76))))
	    {$kakushuyoso .= "<INPUT TYPE=\"submit\" VALUE=\"各種予想\" NAME=\"TotoButton$Hislands[$HcurrentNumber]->{'id'}\">"};

	$auc6 = $island->{'auc6'};
	$auc6 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
	($auc6a, $auc6x, $auc6y) = ($1, $2, $3);
	$nyuusatu = "";
        if ($auc6a <= 2)
	    {$nyuusatu .= "<INPUT TYPE=\"submit\" VALUE=\"入札する\" NAME=\"AuctionButton$Hislands[$HcurrentNumber]->{'id'}\">"};

	$etc5 = $island->{'etc5'};
	$etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

	$s04b = int($s04/10);
	$s06b = int($s06/5);
	$s08b = int($s08/5);
	$s10b = int($s10/5)+1;
	if($s10b > 9) {$s10b = 9;}
	$s12b = int($s12/5)+1;
	if($s12b > 10) {$s12b = 10;}

	if ($s00 != 0)
	    {$seisaku .= "<hr><B>政策(数量0〜50で指定してください)</B><br>"};
	    {$seisaku .= "<table border=\"0\" cellpadding=\"0\" cellspacing=\"0\"><tr><td><INPUT TYPE=\"submit\" VALUE=\"省エネ\" NAME=\"ShoueneButton$Hislands[$HcurrentNumber]->{'id'}\"></td><td>　予算$s01兆円/消費電力-$s02%</td><tr><td><INPUT TYPE=\"submit\" VALUE=\" 教育 \" NAME=\"KyouikuButton$Hislands[$HcurrentNumber]->{'id'}\"></td><td>　予算$s09兆円/指定可能+$s10b</td></tr><tr><td><INPUT TYPE=\"submit\" VALUE=\" 防災 \" NAME=\"BousaiButton$Hislands[$HcurrentNumber]->{'id'}\"></td><td>　予算$s03兆円/予測精度+$s04b</td></tr><tr><td><INPUT TYPE=\"submit\" VALUE=\" 観光 \" NAME=\"KankouButton$Hislands[$HcurrentNumber]->{'id'}\"></td><td>　予算$s05兆円/人気+$s06b</td></tr><tr><td><INPUT TYPE=\"submit\" VALUE=\" 自然 \" NAME=\"SizenButton$Hislands[$HcurrentNumber]->{'id'}\"></td><td>　予算$s07兆円/清浄+$s08b</td></tr><tr><td><INPUT TYPE=\"submit\" VALUE=\" 貯蓄 \" NAME=\"ChochikuButton$Hislands[$HcurrentNumber]->{'id'}\"></td><td>　予算$s11兆円/貯蓄$s12b倍</td></tr></table>"};
	if ($s00 == 0)
	    {$seisaku = ""};

	if ($anothermood == 1)
	    {$ptsname = "経済力"};
	if ($anothermood == 0)
	    {$ptsname = "総合Point"};


    out(<<END);
<CENTER>
<TABLE BORDER>
<TR>
<TH $HbgTitleCell nowrap=nowrap><NOBR>${HtagTH_}順位${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell nowrap=nowrap><NOBR>${HtagTH_}$ptsname${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell nowrap=nowrap><NOBR>${HtagTH_}人口${H_tagTH}</NOBR></TH>
$mStr1
<TH $HbgTitleCell nowrap=nowrap><NOBR>${HtagTH_}食料${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell nowrap=nowrap><NOBR>${HtagTH_}面積${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell nowrap=nowrap><NOBR>${HtagTH_}農場${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell nowrap=nowrap><NOBR>${HtagTH_}職場${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell nowrap=nowrap><NOBR>${HtagTH_}採掘場${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell nowrap=nowrap><NOBR>${HtagTH_}発電力${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell nowrap=nowrap><NOBR>${HtagTH_}失業率${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell nowrap=nowrap><NOBR>${HtagTH_}軍事技術${H_tagTH}</NOBR></TH>
</TR>
<TR>
<TD $HbgNumberCell ROWSPAN=2 align=middle nowrap=nowrap><NOBR>${HtagNumber_}$rank${H_tagNumber}</NOBR></TD>
<TD $HbgPoinCell align=right nowrap=nowrap><NOBR>${pts}</NOBR></TD>
<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>$island->{'pop'}$HunitPop</NOBR></TD>
$mStr2
<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>$island->{'food'}$HunitFood</NOBR></TD>
<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>$island->{'area'}$HunitArea</NOBR></TD>
<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>${farm}</NOBR></TD>
<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>${factoryt}</NOBR></TD>
<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>${mountain}</NOBR></TD>
<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>${ene}万ｋＷ</NOBR></TD>
<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>${unemployed}</NOBR></TD>
<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>Ｌｖ${renae}</NOBR></TD>
</TR>
<TR>
<TD $HbgCommentCell COLSPAN=11 align=left nowrap=nowrap><NOBR>${HtagtTH_}info：<font size="-1"><font color="SALMON">$house</font>$monsliveimg<font color="hotpink">$monsm</font>$Farmcpc$me_sat</font></font>$eleinfo</NOBR></TD>
</TR>
</TABLE></CENTER>


<SCRIPT Language="JavaScript">
<!--

function MM_displayStatusMsg(msgStr) {
    window.status=msgStr;
}

function Navi(HislandSize, position, position2, x, y, img, title, title2, text, exp) {
	StyElm = document.getElementById("NaviView");
	StyElm.style.visibility = "visible";

	if(HislandSize < 15) {
		if(position == 1) {
			if(position2 == 1) {
			    StyElm.style.marginLeft = -32;
			    StyElm.style.marginTop = -360;
			} else {
			    StyElm.style.marginLeft = -32;
			    StyElm.style.marginTop = -120;
			}
		} else {
		    StyElm.style.marginLeft = 240;
		    StyElm.style.marginTop = -240;
		}

	} else {

		if(position == 1) {
		    StyElm.style.marginLeft = 32;
		    StyElm.style.marginTop = (y - 19) * 32;
		} else {
		    StyElm.style.marginLeft = 336;
		    StyElm.style.marginTop = (y - 19) * 32;
		}

	}


	if(HislandSize < 15) {
	    StyElm.innerHTML = "<table><tr><td class='M'><img class='NaviImg' src=" + img + "><\/td><td class='M'><div class='NaviTitle'>" + title + " (" + x + "," + y + ")<\/div><div class='NaviText'><hr>" + title2 + " <\/div><\/td><\/tr><\/table>";
	} else {
	    StyElm.innerHTML = "<table><tr><td class='M'><img class='NaviImg' src=" + img + "><\/td><td class='M' width=256><div class='NaviTitle'>" + title + " (" + x + "," + y + ")<\/div><div class='NaviText'><hr>" + title2 + " <\/div><\/td><\/tr><\/table>";
	}


}

function Navi2(HislandSize,img, title, title2, text, exp) {
	StyElm = document.getElementById("NaviView");
	StyElm.style.visibility = "visible";

	if(HislandSize < 15) {

		    StyElm.style.marginLeft = 0;
		    StyElm.style.marginTop = -400;

	} else {

		    StyElm.style.marginLeft = 0;
		    StyElm.style.marginTop = -656;

	}

	    StyElm.innerHTML = "<table><tr><td class='M'><img class='NaviImg' src=" + img + "><\/td><td class='M'><div class='NaviTitle'>" + title + "<\/div><div class='NaviText'><hr>" + title2 + " <\/div><\/td><\/tr><\/table>";

}

function NaviClose() {
	StyElm = document.getElementById("NaviView");
	StyElm.style.visibility = "hidden";
}

//-->
</SCRIPT>

END
}

# 地図の表示
# 引数が1なら、ミサイル基地等をそのまま表示
sub islandMap {
    my($mode) = @_;
    my($island);
    $island = $Hislands[$HcurrentNumber];

    out(<<END);
<CENTER><TABLE BORDER><TR><TD>
END
    # 地形、地形値を取得
    my($land) = $island->{'land'};
    my($landValue) = $island->{'landValue'};
    my($l, $lv);

	my($onm);
	$onm = $island->{'onm'};
	my($totoyoso2);
	$totoyoso2 = $island->{'totoyoso2'};
	my($eis1);
	$eis1 = $island->{'eis1'};
	my($eis2);
	$eis2 = $island->{'eis2'};
	my($eis3);
	$eis3 = $island->{'eis3'};
	my($eis5);
	$eis5 = $island->{'eis5'};
	my($area);
	$area = $island->{'area'};
	my($fore);
	$fore = $island->{'fore'};

	my($pop);
	$pop = $island->{'pop'};
	$mikomi = int($pop * 3 * 11 / 500);

	$eisei5 = $island->{'eisei5'};
	$eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tet) = ($1, $2, $3, $4, $5, $6, $7);

	$eisei4 = $island->{'eisei4'};
	$eisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($sto, $std, $stk, $stwin, $stdrow, $stlose, $stwint, $stdrowt, $stloset, $styusho, $stshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);
	$kachiten = $stwin*3 + $stdrow;

	if($stshoka == 0) {
	    $nn = '練習中';
	} elsif($stshoka == 1) {
	    $nn = '予選第１戦待ち';
	} elsif($stshoka == 2) {
	    $nn = '予選第２戦待ち';
	} elsif($stshoka == 3) {
	    $nn = '予選第３戦待ち';
	} elsif($stshoka == 4) {
	    $nn = '予選第４戦待ち';
	} elsif($stshoka == 5) {
	    $nn = '予選終了待ち';
	} elsif($stshoka == 6) {
	    $nn = '準々決勝戦待ち';
	} elsif($stshoka == 7) {
	    $nn = '準決勝戦待ち';
	} elsif($stshoka == 8) {
	    $nn = '決勝戦待ち';
	} elsif($stshoka == 9) {
	    $nn = '優勝！';
	} elsif($stshoka == 10) {
	    $nn = '練習中';
	} elsif($stshoka == 11) {
	    $nn = '予選落ち';
	} elsif($stshoka == 12) {
	    $nn = '準々決勝負け';
	} elsif($stshoka == 13) {
	    $nn = '準決勝負け';
	} elsif($stshoka == 14) {
	    $nn = '第２位';
	} else {
	    $nn = '練習中';
	}

	$etc9 = $island->{'etc9'};
	$etc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($co7, $magicf, $magici, $magica, $magicw, $magicl, $magicd) = ($1, $2, $3, $4, $5, $6, $7);


	$etc6 = $island->{'etc6'};
	$etc6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($z0,$z1,$z2,$z3,$z4,$z5,$z6,$z7,$z8,$z9,$z10,$z11,$z12,$z13,$z14,$z15,$z16,$z17,$z18,$z19,$z20,$z21,$z22,$z23,$z24,$z25,$z26,$z27,$z28,$z29,$z30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
	($z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);


	$zookazu = $z0+$z1+$z2+$z3+$z4+$z5+$z6+$z7+$z8+$z9+$z10+$z11+$z12+$z13+$z14+$z15+$z16+$z17+$z18+$z19+$z20+$z21+$z22+$z23+$z24+$z25+$z26+$z27+$z28+$z29+$z30;
	$zookazus = $z0*2+$z1+$z2+$z3+$z4+$z5+$z6+$z7+$z8*2+$z9+$z10+$z11+$z12*2+$z13*3+$z14*3+$z15*3+$z16*3+$z17*4+$z18*4+$z19*5+$z20*4+$z21*5+$z22*3+$z23*3+$z24*3+$z25*3+$z26*3+$z27*3+$z28*4+$z29+$z30*4;

	$bariaA = $island->{'rena'}-$zookazus*25;
	$bariaB = $island->{'rena'}-$zookazus*50;

	$mshurui = 0;
	foreach $i (0..30) {

	$zoos = $z->{"$i"};

	    if($zoos > 0) {
		$mNameList .= "[$HmonsterName[$i]$zoos匹] ";
		$mshurui++;
	    }
	}

	$auc6 = $island->{'auc6'};
	$auc6 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
	($auc6a, $auc6x, $auc6y) = ($1, $2, $3);

	$auction1 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($shuppin1, $avalue1, $ajoutai1, $topvalue1, $topid1) = ($1, $2, $3, $4, $5);

	if($shuppin1 == 0) {
	    $ac1 = '？';
	} elsif($shuppin1 == 1) {
	    $ac1 = '地石';
	} elsif($shuppin1 == 2) {
	    $ac1 = '氷石';
	} elsif($shuppin1 == 3) {
	    $ac1 = '風石';
	} elsif($shuppin1 == 4) {
	    $ac1 = '炎石';
	} elsif($shuppin1 == 5) {
	    $ac1 = '光石';
	} elsif($shuppin1 == 6) {
	    $ac1 = '天使ミカエル';
	} elsif($shuppin1 == 7) {
	    $ac1 = 'アイススコーピオン';
	} elsif($shuppin1 == 8) {
	    $ac1 = 'スライムレジェンド';
	} elsif($shuppin1 == 9) {
	    $ac1 = "お守り$avalue1個";
	} elsif($shuppin1 == 10) {
	    $avalue1 = $avalue1 * 1000;
	    $ac1 = "海あみゅ$avalue1人規模";
	} elsif($shuppin1 == 11) {
	    $avalue1 = $avalue1 * 1000;
	    $ac1 = "食研$avalue1人規模";
	} elsif($shuppin1 == 12) {
	    $ac1 = "コスモ$avalue1万ｋＷ";
	} elsif($shuppin1 == 13) {
	    $ac1 = '闇石';
	} elsif($shuppin1 == 14) {
	    $ac1 = '衛星６種';
	} elsif($shuppin1 == 15) {
	    $ac1 = '宇宙ステーション';
	} elsif($shuppin1 == 16) {
	    $ac1 = '黄金のコンデンサ';
	} elsif($shuppin1 == 17) {
	    $avalue1 = $avalue1 * 1000;
	    $ac1 = "金山$avalue1人規模";
	} elsif($shuppin1 == 18) {
	    $avalue1 = $avalue1 * 1000;
	    $ac1 = "養殖場$avalue1人規模";
	} elsif($shuppin1 == 19) {
	    $ac1 = '人造怪獣f02';
	} elsif($shuppin1 == 20) {
	    $ac1 = '魔王サタン';
	} elsif($shuppin1 == 21) {
	    $ac1 = 'unknown';
	} elsif($shuppin1 == 22) {
	    $ac1 = "サッカーチーム力1.$avalue1倍";
	} elsif($shuppin1 == 23) {
	    $ac1 = "生物大学能力1.$avalue1倍";
	} elsif($shuppin1 == 24) {
	    $ac1 = "生物大学経験値$avalue1";
	} elsif($shuppin1 == 25) {
	    $ac1 = '卵';
	} elsif($shuppin1 == 26) {
	    $ac1 = '生物大学';
	} elsif($shuppin1 == 27) {
	    $ac1 = "風力$avalue1万ｋＷ";
	} elsif($shuppin1 == 28) {
	    $ac1 = "バイオマス$avalue1万ｋＷ";
	} elsif($shuppin1 == 29) {
	    $ac1 = '今回はお休み';
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
	    $ac1 = "$dashiname";
	} else {
	    $ac1 = '？';
	}

	if($ajoutai1 == 15) {
	    $acjo1 = "<font color=\"red\">(落札済み)</font>";
	} else {
	    $acjot1 = 15-$ajoutai1;
	    $acjo1 = "(残り$acjot1ターン)";
	}

	$auction2 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($shuppin2, $avalue2, $ajoutai2, $topvalue2, $topid2) = ($1, $2, $3, $4, $5);

	if($shuppin2 == 0) {
	    $ac2 = '闇石';
	} elsif($shuppin2 == 1) {
	    $ac2 = '地石';
	} elsif($shuppin2 == 2) {
	    $ac2 = '氷石';
	} elsif($shuppin2 == 3) {
	    $ac2 = '風石';
	} elsif($shuppin2 == 4) {
	    $ac2 = '炎石';
	} elsif($shuppin2 == 5) {
	    $ac2 = '光石';
	} elsif($shuppin2 == 6) {
	    $ac2 = '天使ミカエル';
	} elsif($shuppin2 == 7) {
	    $ac2 = 'アイススコーピオン';
	} elsif($shuppin2 == 8) {
	    $ac2 = 'スライムレジェンド';
	} elsif($shuppin2 == 9) {
	    $ac2 = "お守り$avalue2個";
	} elsif($shuppin2 == 10) {
	    $avalue2 = $avalue2 * 1000;
	    $ac2 = "海あみゅ$avalue2人規模";
	} elsif($shuppin2 == 11) {
	    $avalue2 = $avalue2 * 1000;
	    $ac2 = "食研$avalue2人規模";
	} elsif($shuppin2 == 12) {
	    $ac2 = "コスモ$avalue2万ｋＷ";
	} elsif($shuppin2 == 13) {
	    $ac2 = '闇石';
	} elsif($shuppin2 == 14) {
	    $ac2 = '衛星６種';
	} elsif($shuppin2 == 15) {
	    $ac2 = '宇宙ステーション';
	} elsif($shuppin2 == 16) {
	    $ac2 = '黄金のコンデンサ';
	} elsif($shuppin2 == 17) {
	    $avalue2 = $avalue2 * 1000;
	    $ac2 = "金山$avalue2人規模";
	} elsif($shuppin2 == 18) {
	    $avalue2 = $avalue2 * 1000;
	    $ac2 = "養殖場$avalue2人規模";
	} elsif($shuppin2 == 19) {
	    $ac2 = '人造怪獣f02';
	} elsif($shuppin2 == 20) {
	    $ac2 = '魔王サタン';
	} elsif($shuppin2 == 21) {
	    $ac2 = 'unknown';
	} elsif($shuppin2 == 22) {
	    $ac2 = "サッカーチーム力1.$avalue2倍";
	} elsif($shuppin2 == 23) {
	    $ac2 = "生物大学能力1.$avalue2倍";
	} elsif($shuppin2 == 24) {
	    $ac2 = "生物大学経験値$avalue2";
	} elsif($shuppin2 == 25) {
	    $ac2 = '卵';
	} elsif($shuppin2 == 26) {
	    $ac2 = '生物大学';
	} elsif($shuppin2 == 27) {
	    $ac2 = "風力$avalue2万ｋＷ";
	} elsif($shuppin2 == 28) {
	    $ac2 = "バイオマス$avalue2万ｋＷ";
	} elsif($shuppin2 == 29) {
	    $ac2 = '今回はお休み';
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
	    $ac2 = "$dashiname";
	} else {
	    $ac2 = '？';
	}

	if($ajoutai2 == 15) {
	    $acjo2 = "<font color=\"red\">(落札済み)</font>";
	} else {
	    $acjot2 = 15-$ajoutai2;
	    $acjo2 = "(残り$acjot2ターン)";
	}

	$auction3 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($shuppin3, $avalue3, $ajoutai3, $topvalue3, $topid3) = ($1, $2, $3, $4, $5);

	if($shuppin3 == 0) {
	    $ac3 = '闇石';
	} elsif($shuppin3 == 1) {
	    $ac3 = '地石';
	} elsif($shuppin3 == 2) {
	    $ac3 = '氷石';
	} elsif($shuppin3 == 3) {
	    $ac3 = '風石';
	} elsif($shuppin3 == 4) {
	    $ac3 = '炎石';
	} elsif($shuppin3 == 5) {
	    $ac3 = '光石';
	} elsif($shuppin3 == 6) {
	    $ac3 = '天使ミカエル';
	} elsif($shuppin3 == 7) {
	    $ac3 = 'アイススコーピオン';
	} elsif($shuppin3 == 8) {
	    $ac3 = 'スライムレジェンド';
	} elsif($shuppin3 == 9) {
	    $ac3 = "お守り$avalue2個";
	} elsif($shuppin3 == 10) {
	    $avalue3 = $avalue3 * 1000;
	    $ac3 = "海あみゅ$avalue3人規模";
	} elsif($shuppin3 == 11) {
	    $avalue3 = $avalue3 * 1000;
	    $ac3 = "食研$avalue3人規模";
	} elsif($shuppin3 == 12) {
	    $ac3 = "コスモ$avalue3万ｋＷ";
	} elsif($shuppin3 == 13) {
	    $ac3 = '闇石';
	} elsif($shuppin3 == 14) {
	    $ac3 = '衛星６種';
	} elsif($shuppin3 == 15) {
	    $ac3 = '宇宙ステーション';
	} elsif($shuppin3 == 16) {
	    $ac3 = '黄金のコンデンサ';
	} elsif($shuppin3 == 17) {
	    $avalue3 = $avalue3 * 1000;
	    $ac3 = "金山$avalue3人規模";
	} elsif($shuppin3 == 18) {
	    $avalue3 = $avalue3 * 1000;
	    $ac3 = "養殖場$avalue3人規模";
	} elsif($shuppin3 == 19) {
	    $ac3 = '人造怪獣f02';
	} elsif($shuppin3 == 20) {
	    $ac3 = '魔王サタン';
	} elsif($shuppin3 == 21) {
	    $ac3 = 'unknown';
	} elsif($shuppin3 == 22) {
	    $ac3 = "サッカーチーム力1.$avalue3倍";
	} elsif($shuppin3 == 23) {
	    $ac3 = "生物大学能力1.$avalue3倍";
	} elsif($shuppin3 == 24) {
	    $ac3 = "生物大学経験値$avalue3";
	} elsif($shuppin3 == 25) {
	    $ac3 = '卵';
	} elsif($shuppin3 == 26) {
	    $ac3 = '生物大学';
	} elsif($shuppin3 == 27) {
	    $ac3 = "風力$avalue3万ｋＷ";
	} elsif($shuppin3 == 28) {
	    $ac3 = "バイオマス$avalue3万ｋＷ";
	} elsif($shuppin3 == 29) {
	    $ac3 = '今回はお休み';
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
	    $ac3 = "$dashiname";
	} else {
	    $ac3 = '？';
	}

	if($ajoutai3 == 15) {
	    $acjo3 = "<font color=\"red\">(落札済み)</font>";
	} else {
	    $acjot3 = 15-$ajoutai3;
	    $acjo3 = "(残り$acjot3ターン)";
	}

    # コマンド取得
    my($command) = $island->{'command'};
    my($com, @comStr, $i);
    if($HmainMode eq 'owner') {
	for($i = 0; $i < $HcommandMax; $i++) {
	    my($j) = $i + 1;
	    $com = $command->[$i];
	    if($com->{'kind'} < 31) {
		$comStr[$com->{'x'}][$com->{'y'}] .=
		    " [${j}]$HcomName[$com->{'kind'}]";
	    }
	    foreach $i (70..79) {
		if($com->{'kind'} == $i) {
		    $comStr[$com->{'x'}][$com->{'y'}] .=
		        " [${j}]$HcomName[$com->{'kind'}]";
	        }
	    }
	    foreach $i (100..130) {
		if($com->{'kind'} == $i) {
		    $comStr[$com->{'x'}][$com->{'y'}] .=
		        " [${j}]$HcomName[$com->{'kind'}]";
	        }
	    }
	}
    }

	if($HislandSize == 20) {
	    $bar = 'xbar_20.gif';
	} else {
	    $bar = 'xbar.gif';
	}

    # 座標(上)を出力
    out("<IMG SRC=\"$bar\"><BR>");

    # 各地形および改行を出力
    my($x, $y);
    for($y = 0; $y < $HislandSize; $y++) {
	# 偶数行目なら番号を出力
        if(($y % 2) == 0) {
	    out("<IMG SRC=\"space${y}.gif\" width=16 height=32>");
	}

	# 各地形を出力
	for($x = 0; $x < $HislandSize; $x++) {
	    $l = $land->[$x][$y];
	    $lv = $landValue->[$x][$y];

	    landString($l, $lv, $x, $y, $mode, $comStr[$x][$y]);
	}

	# 奇数行目なら番号を出力
        if(($y % 2) == 1) {
	    out("<IMG SRC=\"space${y}.gif\" width=16 height=32>");
	}

	# 改行を出力
	out("<BR>");
    }
    out("<div id=\"NaviView\"></div>");
    out("</TD></TR></TABLE></CENTER>\n");
}

sub landString {
    my($l, $lv, $x, $y, $mode, $comStr) = @_;
    my($point) = "($x,$y)";
    my($image, $alt);

    $alt2 = '';
    $n2 = '';

    if($l == $HlandSea) {

	if($lv == 1) {
	    # 浅瀬
	    $image = 'land14.gif';
	    $alt = '海(浅瀬)';
        } else {
            # 海
	    $image = 'land0.gif';
	    $alt = '海';
        }
    } elsif($l == $HlandWaste) {
	# 荒地
	if($lv == 1) {
	    $image = 'land13.gif'; # 着弾点
	    $alt = '荒地';
	} else {
	    $image = 'land1.gif';
	    $alt = '荒地';
	}
    } elsif($l == $HlandPlains) {
	# 平地
	$image = 'land2.gif';
	$alt = '平地';
    } elsif($l == $HlandPlains2) {
	# 平地２
	$image = 'land53.gif';
	$alt = '開発予定地';
    } elsif($l == $HlandYakusho) {
	# 役所
	$image = 'land52.gif';
	$alt = '島役所';
    } elsif($l == $HlandKura) {
	# 倉庫
	$seq = int($lv/100);
	$choki = $lv%100;
	$image = 'land55.gif';
	$alt = "倉庫";
	$alt2 = "セキュリティーLevel${seq}／貯金${choki}兆円";
    } elsif($l == $HlandKuraf) {
	# 倉庫Food
	$choki = int($lv/10);
	$kibo = $lv%10;
	$image = 'land55.gif';
	$alt = "倉庫";
	$alt2 = "規模Level${kibo}／貯食${choki}00万トン";
    } elsif($l == $HlandForest) {
	# 森
	if($mode == 1) {
	    $image = 'land6.gif';
	    $alt = "森";
	    $alt2 = "${lv}$HunitTree";
	} else {
	    # 観光者の場合は木の本数隠す
	    $image = 'land6.gif';
	    $alt = '森';
	}

    } elsif($l == $HlandHouse) {
	# 島主の家
	my($p, $n);

	if($lv == 0) {
	    $n = "$onmの小屋";
	} elsif($lv == 1) {
	    $n = "$onmの簡易住宅";
	} elsif($lv == 2) {
	    $n = "$onmの住宅";
	} elsif($lv == 3) {
	    $n = "$onmの高級住宅";
	} elsif($lv == 4) {
	    $n = "$onmの豪邸";
	} elsif($lv == 5) {
	    $n = "$onmの大豪邸";
	} elsif($lv == 6) {
	    $n = "$onmの高級豪邸";
	} elsif($lv == 7) {
	    $n = "$onmの城";
	} elsif($lv == 8) {
	    $n = "$onmの巨城";
	} elsif($lv == 9) {
	    $n = "$onmの黄金城";
	} elsif($lv == 10) {
	    $n = "$onmの魔塔";
	} else {
	    $n = "$onmの天空城";
	}

	$image = "house${lv}.gif";
	$alt = "$n";
	$alt2 = "税率$eisei1％($zeikin$HunitMoney)";

    } elsif($l == $HlandTrain) {
	# 電車でごー
	my($p, $n);

	if($lv == 0) {
	    $n = "駅";
	} elsif($lv < 10) {
	    $n = "線路";
	} elsif($lv == 10) {
	    $n = "駅(普通電車停車中)";
	} elsif($lv < 20) {
	    $n = "普通電車";
	} elsif($lv == 20) {
	    $n = "駅(貨物列車停車中)";
	} elsif($lv < 30) {
	    $n = "貨物列車";
	} else {
	    $n = "路線";
	}

	$image = "train${lv}.gif";
	$alt = "$n";

    } elsif($l == $HlandTaishi) {

	my($tn) = $HidToNumber{$lv};
	$tIsland = $Hislands[$tn];
	$ttname = $tIsland->{'name'};
	$image = "land51.gif";
	$alt = "$ttname島大使館";

    } elsif($l == $HlandTown) {
	# 町
	my($p, $n);
	if($lv < 30) {
	    $p = 3;
	    $n = '村';
	} elsif($lv < 100) {
	    $p = 4;
	    $n = '町';
	} else {
	    $p = 5;
	    $n = '都市';
	}

	$image = "land${p}.gif";
	$alt = "$n";
	$alt2 = "${lv}$HunitPop";
    } elsif($l == $HlandProcity) {
	# 町
	my($c);
	if($lv < 110) {
	    $c = '防災都市ランクＥ';
	} elsif($lv < 130) {
	    $c = '防災都市ランクＤ';
	} elsif($lv < 160) {
	    $c = '防災都市ランクＣ';
	} elsif($lv < 200) {
	    $c = '防災都市ランクＢ';
	} else {
	    $c = '防災都市ランクＡ';
	}

	$image = "land26.gif";
	$alt = "$c";
	$alt2 = "${lv}$HunitPop";

    } elsif($l == $HlandCollege) {
	# 大学
	my($p, $n);
	if($lv == 0) {
	    $p = 34;
	    $n = '農業大学';
	} elsif($lv == 1) {
	    $p = 35;
	    $n = '工業大学';
	} elsif($lv == 2) {
	    $p = 36;
	    $n = '総合大学';
	} elsif($lv == 3) {
	    $p = 37;
	    $n = '軍事大学';
	} elsif($lv == 4) {
	    $p = 44;
	    $n = "生物大学";
	    $n2 = "待機/HP$mshp.AP$msap.DP$msdp.SP$mssp/$mswin匹撃破/経験値$msexe";
	} elsif($lv == 98) {
	    $p = 48;
	    $n = "生物大学";
	    $n2 = "待機/HP$mshp.AP$msap.DP$msdp.SP$mssp/$mswin匹撃破/経験値$msexe";
	} elsif($lv == 96) {
	    $p = 44;
	    $n = "生物大学";
	    $n2 = "出禁/HP$mshp.AP$msap.DP$msdp.SP$mssp/$mswin匹撃破/経験値$msexe";
	} elsif($lv == 97) {
	    $p = 48;
	    $n = "生物大学";
	    $n2 = "出禁/HP$mshp.AP$msap.DP$msdp.SP$mssp/$mswin匹撃破/経験値$msexe";
	} elsif($lv == 99) {
	    $p = 47;
	    $n = '生物大学(出動中)';
	} elsif($lv == 5) {
	    $p = 46;
	    $n = '気象大学';
	} elsif($lv == 6) {
	    $p = 47;
	    $n = '経済大学';
	} elsif($lv == 7) {
	    $p = 65;
	    $n = "魔法学校";
	    $n2 = "炎:lv$magicf氷:lv$magici地:lv$magica風:lv$magicw光:lv$magicl闇:lv$magicd";
	} elsif($lv == 8) {
	    $p = 71;
	    $n = '電工大学';
	} elsif($lv == 77) {
	    $p = 75;
	    $n = "文部科学省";
	    $n2 = "消費電力-$s02%/指定可能+$s10b/予測精度+$s04b/人気+$s06b/清浄+$s08b/貯蓄$s12b倍";
	} elsif($lv == 78) {
	    $p = 75;
	    $n = "文部科学省";
	    $n2 = "消費電力-$s02%/指定可能+$s10b/予測精度+$s04b/人気+$s06b/清浄+$s08b/貯蓄$s12b倍<br><font color = royalblue>(自動開発予定地実施中)</font>";
	} elsif($lv == 79) {
	    $p = 75;
	    $n = "文部科学省";
	    $n2 = "消費電力-$s02%/指定可能+$s10b/予測精度+$s04b/人気+$s06b/清浄+$s08b/貯蓄$s12b倍<br><font color = royalblue>(自動地ならし実施中)</font>";
	} elsif($lv == 80) {
	    $p = 75;
	    $n = "文部科学省";
	    $n2 = "消費電力-$s02%/指定可能+$s10b/予測精度+$s04b/人気+$s06b/清浄+$s08b/貯蓄$s12b倍<br><font color = royalblue>(自動開発予定地実施中)<br>(自動地ならし実施中)</font>";
	} elsif($lv == 95) {
	    $p = 54;
	    $n = '経済大学(貯金中)';
	} else {
	    $p = 46;
	    $n = '気象大学';
	}

	$image = "land${p}.gif";
	$alt = "$n";
	$alt2 = "$n2";
    } elsif($l == $HlandKyujokai) {
        # 野球場
        $image = 'land23.gif'; # 記念碑の画像を流用
        $alt = "多目的スタジアム";
        $alt2 = "選手$nn(攻($sto)守($std)KP($stk)チーム成績(勝点$kachiten/$stwin勝$stlose敗$stdrow分/通算$stwint勝$stloset敗$stdrowt分/優勝$styusho回)";
    } elsif($l == $HlandZoo) {
        # 動物園
        $image = 'land84.gif'; # 記念碑の画像を流用
        $alt = "動物園Lv${lv}";
        $alt2 = "$mshurui種類$zookazu匹/$mNameList<br>バリアＡ[$bariaA]バリアＢ[$bariaB]";
    } elsif($l == $HlandFarm) {
	# 農場
	$image = 'land7.gif';
	$alt = "農場";
	$alt2 = "${lv}0${HunitPop}規模";
    } elsif($l == $HlandEneAt) {
	$image = 'land62.gif';
	$alt = "原子力発電所";
	$alt2 = "出力${lv}万ｋＷ";
    } elsif($l == $HlandEneFw) {
	$image = 'land61.gif';
	$alt = "火力発電所";
	$alt2 = "出力${lv}万ｋＷ";
    } elsif($l == $HlandEneWt) {
	$image = 'land63.gif';
	$alt = "水力発電所";
	$alt2 = "出力${lv}万ｋＷ/70-150%変動";
    } elsif($l == $HlandEneBo) {
	$image = 'land67.gif';
	$alt = "バイオマス発電所";
	$alt2 = "出力${lv}万ｋＷ";
    } elsif($l == $HlandEneWd) {
	$image = 'land66.gif';
	$alt = "風力発電所";
	$alt2 = "出力${lv}万ｋＷ/50-125%変動";
    } elsif($l == $HlandEneCs) {
	$image = 'land70.gif';
	$alt = "コスモ発電所";
	$alt2 = "出力${lv}万ｋＷ";
    } elsif($l == $HlandEneSo) {
	$image = 'land68.gif';
	$alt = "ソーラー発電所";
	$alt2 = "出力${lv}万ｋＷ/75-100%変動";
    } elsif($l == $HlandConden) {
	$image = 'land64.gif';
	$alt = "コンデンサ";
	$alt2 = "蓄電${lv}万ｋＷ";
    } elsif($l == $HlandConden2) {
	$image = 'land64.gif';
	$alt = "コンデンサ・改";
	$alt2 = "蓄電${lv}万ｋＷ";
    } elsif($l == $HlandConden3) {
	$vlt = $lv*2;
	$image = 'land76.gif';
	$alt = "黄金のコンデンサ";
	$alt2 = "蓄電${vlt}万ｋＷ";
    } elsif($l == $HlandConden4) {
	if($lv == 3) {
	    $n = '黄金のコンデンサ';
	    $n2 = '漏電中';
	    $image = "land78.gif";
	} elsif($lv == 2) {
	    $n = 'コンデンサ・改';
	    $n2 = '漏電中';
	    $image = "land77.gif";
	} elsif($lv == 99) {

	    if($magicl == $magica) {
	    $vlt = $magicl*15000+50000;
	    $n = "核融合発電所";
	    $n2 = "${vlt}万ｋＷ";
	    } else {
	    $n = '核融合発電所';
	    $n2 = '不安定';
	    }
	    $image = "land79.gif";
	}
	$alt = "$n";
	$alt2 = "$n2";
    } elsif($l == $HlandFoodim) {
	# 研究所
	my($f);
	if($lv < 480) {
	    $f = '食物研究所';
	} else {
	    $f = '防災型食物研究所';
	}
	$image = "land25.gif";
	$alt = "$f";
	$alt2 = "農場換算${lv}0${HunitPop}規模";

    } elsif($l == $HlandFoodka) {
	# 研究所
	$klv = $lv*200;
	if($lv == 0) {
	    $n = '加工工場';
	    $n2 = '休業中';
	} elsif($lv == 1) {
	    $n = "精肉工場";
	    $n2 = "100トン＆50kWで0.175億円・農場＆普通職場${klv}0${HunitPop}規模";
	} elsif($lv == 2) {
	    $n = "ハンバーガー工場";
	    $n2 = "100トン＆150kWで0.25億円・農場＆普通職場${klv}0${HunitPop}規模";
	} elsif($lv == 3) {
	    $n = "ケーキ工場";
	    $n2 = "100トン＆300kWで0.4億円・農場＆普通職場${klv}0${HunitPop}規模";
	}
	$image = "land73.gif";
	$alt = "$n";
	$alt2 = "$n2";

    } elsif($l == $HlandFarmchi) {
	$works = $lv;
	$image = 'land31.gif';
	$alt = "養鶏場";
	$alt2 = "${lv}万羽/生産力${works}$HunitFood";
    } elsif($l == $HlandFarmpic) {
	$works = $lv*2;
	$image = 'land32.gif';
	$alt = "養豚場";
	$alt2 = "${lv}万頭/生産力${works}$HunitFood";
    } elsif($l == $HlandFarmcow) {
	$works = $lv*3;
	$image = 'land33.gif';
	$alt = "牧場";
	$alt2 = "${lv}万頭/生産力${works}$HunitFood";
    } elsif($l == $HlandFactory) {
	# 工場
	$image = 'land8.gif';
	$alt = "工場";
	$alt2 = "${lv}0${HunitPop}規模";
    } elsif($l == $HlandHTFactory) {
	# ハイテク工場
	$image = 'land50.gif';
	$alt = "ハイテク多国籍企業";
	$alt2 = "${lv}0${HunitPop}規模";
    } elsif($l == $HlandSHTF) {
	$image = 'land85.gif';
	$alt = "ハイテク多国籍企業・改";
	$alt2 = "ＨＴ職場${lv}0${HunitPop}規模";
    } elsif($l == $HlandOWNF) {
	$image = 'land86.gif';

	$ownfe = int($lv/1000);
	$shts = int($lv/100)%10*250;
	$hts = int($lv%100/10)*250;
	$noujous = $lv%10*250;

	$n = '';
	if($ownfe > 0) {
	    $n .= '<br><font color = royalblue>(腐海の毒消し薬所有)</font>';
	}
	if($ownfe > 1) {
	    $n .= '<br><font color = royalblue>(ウィルスワクチン所有)</font>';
	}
	if($ownfe > 2) {
	    $n .= '<br><font color = royalblue>(長寿薬所有)</font>';
	}

	$alt = "$onm社";
	$alt2 = "農場${noujous}0${HunitPop}規模<br>職場${hts}0${HunitPop}規模<br>ＨＴ職場${shts}0${HunitPop}規模${n}";
    } elsif($l == $HlandBase) {
	if($mode == 0) {
	    # 観光者の場合は森のふり
	    $image = 'land6.gif';
	    $alt = '森';
	} else {
	    # ミサイル基地
	    my($level) = expToLevel($l, $lv);
	    $image = 'land9.gif';
	    $alt = "ミサイル基地";
	    $alt2 = "レベル ${level}/経験値 $lv";
	}
    } elsif($l == $HlandSbase) {
	# 海底基地
	if($mode == 0) {
	    # 観光者の場合は海のふり
	    $image = 'land0.gif';
	    $alt = '海';
	} else {
	    my($level) = expToLevel($l, $lv);
	    $image = 'land12.gif';
	    $alt = "海底基地";
	    $alt2 = "レベル ${level}/経験値 $lv";
	}
    } elsif($l == $HlandSeacity) {
	# 海底都市
	if($mode == 0) {
	    # 観光者の場合は海のふり
	    $image = 'land0.gif';
	    $alt = '海';
	} else {
	    my($level) = expToLevel($l, $lv);
	    $image = 'land17.gif';
	    $alt = "海底都市";
	    $alt2 = "${lv}$HunitPop";
	}
    } elsif($l == $HlandFrocity) {
	# 海上都市
	my($level) = expToLevel($l, $lv);
	$image = 'land39.gif';
	$alt = "海上都市メガフロート";
 	$alt2 = "${lv}$HunitPop";
    } elsif($l == $HlandMinato) {
	# 港
	my($level) = expToLevel($l, $lv);
	$image = 'land21.gif';
	$alt = "港町";
	$alt2 = "${lv}$HunitPop";
    } elsif($l == $HlandOnsen) {
	# 温泉
	my($level) = expToLevel($l, $lv);
	$image = 'land40.gif';
	$alt = "温泉街";
	$alt2 = "${lv}$HunitPop";
    } elsif($l == $HlandSunahama) {
	# 砂浜
	$image = 'land38.gif';
	$alt = '砂浜';
    } elsif($l == $HlandDefence) {
	if($lv == 77) {
	    $image = 'land80.gif';
	    $alt = "防衛施設・改";
	} else {
	    $image = 'land10.gif';
	    $alt = '防衛施設';
	}
    } elsif($l == $HlandHaribote) {
	# ハリボテ
	$image = 'land10.gif';
	if($mode == 0) {
	    # 観光者の場合は防衛施設のふり
	    $alt = '防衛施設';
	} else {
	    $alt = 'ハリボテ';
	}
    } elsif($l == $HlandNursery) {
        # 養殖場
        $image = 'nursery.gif';
        $alt = "養殖場";
        $alt2 = "${lv}0${HunitPop}規模";
    } elsif($l == $HlandMine) {
        if($mode == 0) {
            # 観光者の場合は森のふり
            $image = 'land6.gif';
            $alt = '森';
        } else {
            # 地雷
            $image = 'land22.gif'; # 記念碑の画像を流用
            $alt = "地雷";
            $alt2 = "ダメージ$lv";
        }
    } elsif($l == $HlandIce) {

	if($lv > 0) {
	    $image = 'land42.gif';
	    $alt = "天然スケート場";
	} else {
	    $image = 'land41.gif';
	    $alt = '氷河';
	}
    } elsif($l == $HlandOil) {
	# 海底油田
	$image = 'land16.gif';
	$alt = '海底油田';
    } elsif($l == $HlandGold) {
	# 金山
	$image = 'land15.gif';
	$alt = "金山";
	$alt2 = "採掘場${lv}0${HunitPop}規模";
    } elsif($l == $HlandMountain) {
	# 山
	my($str);
	$str = '';
	if($lv > 0) {
	    $image = 'land15.gif';
	    $alt = "山";
	    $alt2 = "採掘場${lv}0${HunitPop}規模";
	} else {
	    $image = 'land11.gif';
	    $alt = '山';
	}
    } elsif($l == $HlandMonument) {
	# 記念碑
	$image = $HmonumentImage[$lv];
	$alt = $HmonumentName[$lv];
    } elsif($l == $HlandFune) {
	# fune
	$image = $HfuneImage[$lv];
	$alt = $HfuneName[$lv];
    } elsif($l == $HlandMonster) {
	# 怪獣
	my($kind, $name, $hp) = monsterSpec($lv);
	my($special) = $HmonsterSpecial[$kind];
	$image = $HmonsterImage[$kind];

	# 硬化中?
	if((($special == 3) && (($HislandTurn % 2) == 1)) ||
           (($special == 8) && ((seqnum($HislandTurn) % 2) == 0)) ||
	   (($special == 4) && (($HislandTurn % 2) == 0))) {
	    # 硬化中
	    $image = $HmonsterImage2[$kind];
	}
	$alt = "$name";
	$alt2 = "体力${hp}";
    } elsif($l == $HlandPark) {
        # 遊園地
        $image = 'land19.gif'; # 記念碑の画像を流用
	$alt = "遊園地";
	$alt2 = "従業員${lv}0${HunitPop}/収益見込${mikomi}$HunitMoney以上";
    } elsif($l == $HlandKyujo) {
        # 野球場
        $image = 'land23.gif'; # 記念碑の画像を流用
        $alt = '野球場';
    } elsif($l == $HlandUmiamu) {
        # 海あみゅ
        $image = 'land24.gif'; # 記念碑の画像を流用
	$alt = "海あみゅ";
	$alt2 = "従業員${lv}0${HunitPop}";
    } elsif($l == $HlandSeki) {
        # 関所
        $image = 'land27.gif'; # 記念碑の画像を流用
        $alt = '関所';
    } elsif($l == $HlandRottenSea) {
         # 腐海
	if($lv > 20) {
	    $image = 'land72.gif';
	    $alt = "枯死海";
	    $alt2 = "樹齢$lvターン";
	} else {
	    $image = 'land20.gif';
	    $alt = "腐海";
	    $alt2 = "樹齢$lvターン";
	}
    } elsif($l == $HlandNewtown) {
	# ニュータウン
	my($level) = expToLevel($l, $lv);
	$nwork =  int($lv/15);
	$image = 'land28.gif';
	$alt = "ニュータウン";
	$alt2 = "${lv}$HunitPop/普通職場${nwork}0$HunitPop";
    } elsif($l == $HlandBigtown) {
	# 現代都市
	my($level) = expToLevel($l, $lv);
	$mwork =  int($lv/20);
	$lwork =  int($lv/30);
	$image = 'land29.gif';
	$alt = "現代都市";
	$alt2 = "${lv}$HunitPop/普通職場${mwork}0$HunitPop/農場${lwork}0$HunitPop";
    } elsif($l == $HlandRizort) {
	# リゾート地
	my($level) = expToLevel($l, $lv);
	$rwork =  $lv+$eis1+$eis2+$eis3+$eis5+int($fore/10)+int($rena/25)-$monsterlive*100;
	$image = 'land43.gif';
	$alt = "リゾート地";
	$alt2 = "滞在観光客${lv}$HunitPop";
    } elsif($l == $HlandKajino) {
	# カジノ
	my($level) = expToLevel($l, $lv);
	$rwork =  int(($lv+$eis1+$eis2+$eis3+$eis5+int($fore/10)+int($rena/10)-$monsterlive*100)/5);
	$image = 'land74.gif';
	$alt = "カジノ";
	$alt2 = "滞在観光客${lv}$HunitPop";
    } elsif($l == $HlandBigRizort) {
	# リゾート地
	my($level) = expToLevel($l, $lv);
	$image = 'land49.gif';
	$alt = "臨海リゾートホテル";
	$alt2 = "滞在観光客${lv}$HunitPop";
    } elsif($l == $HlandShuto) {
	# 首都
	my($level) = expToLevel($l, $lv);
	$image = 'land29.gif';
	$alt = "首都$totoyoso2";
	$alt2 = "${lv}$HunitPop";
    } elsif($l == $HlandUmishuto) {
	# 海首都
	if($mode == 0) {
	    # 観光者の場合は海のふり
	    $image = 'land0.gif';
	    $alt = '海';
	} else {
	my($level) = expToLevel($l, $lv);
	$image = 'land30.gif';
	$alt = "海底首都$totoyoso2";
	$alt2 = "${lv}$HunitPop";
	}
    } elsif($l == $HlandBettown) {
	# 輝ける都市
	my($level) = expToLevel($l, $lv);
	$image = 'land45.gif';
	$alt = "輝ける都市";
	$alt2 = "${lv}$HunitPop";
    } elsif($l == $HlandSkycity) {
	# 空中都市
	my($level) = expToLevel($l, $lv);
	$mwork =  int($lv/60);
	$lwork =  int($lv/60);
	$ework =  int($lv/2)*3;
	$image = 'land81.gif';
	$alt = "空中都市";
	$alt2 = "${lv}$HunitPop/ＨＴ職場${mwork}0$HunitPop/農場${lwork}0$HunitPop/電力消費${ework}万ｋＷ";
    } elsif($l == $HlandUmicity) {
	# 海都市
	my($level) = expToLevel($l, $lv);
	$mwork =  int($lv/60);
	$lwork =  int($lv/60);
	$ework =  int($lv/2)*3;
	$image = 'land82.gif';
	$alt = "海都市";
	$alt2 = "${lv}$HunitPop/ＨＴ職場${mwork}0$HunitPop/農場${lwork}0$HunitPop/電力消費${ework}万ｋＷ";
    } elsif($l == $HlandSeatown) {
	# 海底新都市
	if($mode == 0) {
	    # 観光者の場合は海のふり
	    $image = 'land0.gif';
	    $alt = '海';
	} else {
	my($level) = expToLevel($l, $lv);
	$owork =  int($lv/40);
	$image = 'land30.gif';
	$alt = "海底新都市";
	$alt2 = "${lv}$HunitPop/普通職場${owork}0$HunitPop/農場${owork}0$HunitPop";
	}
    }

    # 開発画面の場合は、座標設定
    if($mode == 1) {
	out("<A HREF=\"JavaScript:void(0);\" onclick=\"ps($x,$y)\">");

    }

    if($x < $HislandSize / 2) {
	$position = 0;
    } else {
	$position = 1;
    }
    if($y < $HislandSize / 2) {
	$position2 = 0;
    } else {
	$position2 = 1;
    }

    if($HmainMode2 eq 'ijiri') {
	$alt2 .= "<br>land = <font color = red>${l}</font><br>landValue = <font color = red>${lv}</font>";
    }

    out("<IMG SRC=\"$image\" width=32 height=32 BORDER=0 onMouseOver=\"MM_displayStatusMsg('$point $alt $alt2 $comStr'); Navi($HislandSize, $position, $position2, $x, $y,'$image', '$alt', '$alt2<br>$comStr', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">");

    # 座標設定閉じ
    if($mode == 1) {
	out("</A>");
    }
}

#----------------------------------------------------------------------
# テンプレートその他
#----------------------------------------------------------------------
# 個別ログ表示
sub logPrintLocal {
    my($mode) = @_;
    my($i);
    for($i = 0; $i < $HlogMax; $i++) {
	logFilePrint($i, $HcurrentID, $mode);
    }
}

# ○○島へようこそ！！
sub tempPrintIslandHead {
    out(<<END);
<CENTER>
${HtagBig_}${HtagName_}「${HcurrentName}島」${H_tagName}へようこそ！！${H_tagBig}<BR>
$HtempBack<BR>
</CENTER>
END
}

# ○○島開発計画
sub tempOwner {
    out(<<END);
<CENTER>
${HtagBig_}${HtagName_}${HcurrentName}島${H_tagName}開発計画${H_tagBig}<BR>
$HtempBack<BR>
</CENTER>

<SCRIPT Language="JavaScript">
<!--
function ps(x, y) {
    document.forms[0].elements[4].options[x].selected = true;
    document.forms[0].elements[5].options[y].selected = true;
    return true;
}

function ns(x) {
    document.forms[0].elements[2].options[x].selected = true;
    return true;
}

//-->
</SCRIPT>
END

    islandInfo();

    out(<<END);
<CENTER>
<TABLE BORDER>
<TR>
<TD $HbgInputCell >
<CENTER>
<FORM action="$HthisFile" method=POST>
<INPUT TYPE=submit VALUE="計画送信" NAME=CommandButton$Hislands[$HcurrentNumber]->{'id'}>
<HR>
<B>パスワード</B></BR>
<INPUT TYPE=password NAME=PASSWORD VALUE="$HdefaultPassword">
<HR>
<B>計画番号</B><SELECT NAME=NUMBER>
END
    # 計画番号
    my($j, $i);
    for($i = 0; $i < $HcommandMax; $i++) {
	$j = $i + 1;
	out("<OPTION VALUE=$i>$j\n");
    }

    out(<<END);
</SELECT><BR>
<HR>
END


    my($island) = $Hislands[$HcurrentNumber];

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

	$costxx = "";

    if ($anothermood != 1) {
	    $costshusei = $costx;
	    $costxx = "<br>開発度修正…x${costx}";
	} else {
	    $costshusei = 1;
	}

    my($factory) = $island->{'factory'};
	$factory =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($factory1, $factory2, $co0, $co1, $htf, $shtf, $co95, $co95, $co95, $co95) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10);

	$costco95 = int(0.975**$co95*1000)/1000;

	    if($costco95 < 0.9) {
		$costco95 = 0.9;
	    }

	$costhtf = "";
	$costshtf = "";
	$costco95b = "";

	    if($htf > 0) {
		$costhtf = "<br>ハイテク多国籍企業…x0.666";
		$costshusei = $costshusei*2/3;
	    }
	    elsif($shtf > 0) {
		$costshtf = "<br>ハイテク多国籍企業・改…x0.9";
		$costshusei = $costshusei*9/10;
	    }
	    if($co95 > 0) {
		$costco95b = "<br>経済大学(貯金中)…x${costco95}";
		$costshusei = $costshusei*$costco95;
	    }

	$etc5 = $island->{'etc5'};
	$etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);

	$costseisaku = $s01+$s03+$s05+$s07+$s09+$s11+$s13+$s15+$s17+$s19+$s21+$s23+$s25+$s27+$s29+$s02+$s04+$s06+$s08+$s10+$s12+$s14+$s16+$s18+$s20+$s22+$s24+$s26+$s28+$s30;
	$costseisaku2 = int(0.9975**$costseisaku*1000)/1000;
	$costseisaku3 = "";

	    if($costseisaku2 < 0.75) {
		$costseisaku2 = 0.75;
	    }

	    if($s00 > 0) {
		$costseisaku3 = "<br>文部科学省…x${costseisaku2}";
		$costshusei = $costshusei*$costseisaku2;
	    }

	$s12b = int($s12/5)+1;
	if($s12b > 10) {$s12b = 10;}

	$costmoney = int(($island->{'money'}/5/(999999*$s12b)+0.8)*1000)/1000;
	$costmoney2 = "所持資金…x${costmoney}";
	$costshusei = $costshusei*$costmoney;

	$costshusei = int($costshusei*1000)/1000;

	$costshusei = ($costshusei == 1) ? "なし" : "x${costshusei}";

	$alt = "コスト修正($costshusei)";
	$alt2 = "$costmoney2$costxx$costseisaku3$costhtf$costshtf$costco95b";

    out(<<END);

<B>開発計画</B><BR>
<FONT size=-1>
<SELECT NAME=COMMAND onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi2($HislandSize, 'black.gif', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\"></font>
END

    #コマンド
    my($kind, $cost, $s);

    if($HmainMode2 eq 'ijiri') {
	    out("<OPTION VALUE=$HcomIjiri $s>$HcomName[$HcomIjiri]\n");
    }

    for($i = 0; $i < $HcommandTotal; $i++) {
	$kind = $HcomList[$i];
	$cost = $HcomCost[$kind];

    my($island) = $Hislands[$HcurrentNumber];

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

    if (($anothermood != 1) && ($kind != $HcomKura) && ($kind != $HcomKura2) && ($kind != $HcomKuraf) && ($kind != $HcomHouse) && ($kind != $HcomBettown) && ($kind != $HcomKai) && ($kind != $HcomBoku2) && ($kind != $HcomEneCs) && ($kind != $HcomEneNF) && ($kind != $HcomEisei) && ($kind != $HcomSell) && ($kind != $HcomMoney) && ($kind != $HcomFood) && ($kind != $HcomGivefood)) {
	$cost = $cost * $costx;
    }

    if (($htf > 0) && ($kind != $HcomKura) && ($kind != $HcomKura2) && ($kind != $HcomKuraf) && ($kind != $HcomSell) && ($kind != $HcomMoney) && ($kind != $HcomFood) && ($kind != $HcomGivefood)) {
	$cost = int($cost * 2 / 3);
    } elsif (($shtf > 0) && ($kind != $HcomKura) && ($kind != $HcomKura2) && ($kind != $HcomKuraf) && ($kind != $HcomSell) && ($kind != $HcomMoney) && ($kind != $HcomFood) && ($kind != $HcomGivefood)) {
	$cost = int($cost * 9 / 10);
    }
    if (($co95 > 0) && ($kind != $HcomKura) && ($kind != $HcomKura2) && ($kind != $HcomKuraf) && ($kind != $HcomSell) && ($kind != $HcomMoney) && ($kind != $HcomFood) && ($kind != $HcomGivefood)) {
	$cost = int($cost * $costco95);
    }
    if (($s00 > 0) && ($kind != $HcomKura) && ($kind != $HcomKura2) && ($kind != $HcomKuraf) && ($kind != $HcomSell) && ($kind != $HcomMoney) && ($kind != $HcomFood) && ($kind != $HcomGivefood)) {
	$cost = int($cost * $costseisaku2);
    }
    if (($kind != $HcomKura) && ($kind != $HcomKura2) && ($kind != $HcomKuraf) && ($kind != $HcomSell) && ($kind != $HcomMoney) && ($kind != $HcomFood) && ($kind != $HcomGivefood)) {
	$cost = int($cost * $costmoney);
    }

	if($cost == 0) {
	    $cost = '無料';
	} elsif($cost < 0) {
	    $cost = - $cost;
	    $cost .= $HunitFood;
	} else {
	    $cost .= $HunitMoney;
	}
	if($kind == $HdefaultKind) {
	    $s = 'SELECTED';
	} else {
	    $s = '';
	}

	out("<OPTION VALUE=$kind $s>$HcomName[$kind]($cost)\n");
    }

    my($rank) = $HcurrentNumber + 1;

	$auc6 = $island->{'auc6'};
	$auc6 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
	($auc6a, $auc6x, $auc6y) = ($1, $2, $3);
	$auction1 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($shuppin1, $avalue1, $ajoutai1, $topvalue1, $topid1) = ($1, $2, $3, $4, $5);
	$auction2 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($shuppin2, $avalue2, $ajoutai2, $topvalue2, $topid2) = ($1, $2, $3, $4, $5);
	$auction3 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($shuppin3, $avalue3, $ajoutai3, $topvalue3, $topid3) = ($1, $2, $3, $4, $5);

    if(($rank < 50) && ($auc6a == 1) && (($shuppin1 == 29) || ($shuppin2 == 29) || ($shuppin3 == 29))) {
	    out("<OPTION VALUE=$HcomAuction $s>$HcomName[$HcomAuction]($cost)\n");
    }

    out(<<END);
</SELECT>
<HR>
<B>座標(</B>
<SELECT NAME=POINTX>

END
    for($i = 0; $i < $HislandSize; $i++) {
	if($i == $HdefaultX) {
	    out("<OPTION VALUE=$i SELECTED>$i\n");
        } else {
	    out("<OPTION VALUE=$i>$i\n");
        }
    }

    out(<<END);
</SELECT>, <SELECT NAME=POINTY>
END

    for($i = 0; $i < $HislandSize; $i++) {
	if($i == $HdefaultY) {
	    out("<OPTION VALUE=$i SELECTED>$i\n");
        } else {
	    out("<OPTION VALUE=$i>$i\n");
        }
    }
    out(<<END);
</SELECT><B>)</B>
<HR>


END
    if($HmainMode2 eq 'ijiri') {
    out(<<END);
    <SELECT NAME=LAMOUNT1>
END

	    out("<OPTION VALUE='-15' SELECTED>動物園入荷\n");
	    out("<OPTION VALUE='-10' SELECTED>お守り数\n");
	    out("<OPTION VALUE='-9' SELECTED>気象衛星\n");
	    out("<OPTION VALUE='-8' SELECTED>観測衛星\n");
	    out("<OPTION VALUE='-7' SELECTED>迎撃衛星\n");
	    out("<OPTION VALUE='-6' SELECTED>軍事衛星\n");
	    out("<OPTION VALUE='-5' SELECTED>防衛衛星\n");
	    out("<OPTION VALUE='-4' SELECTED>イレギュラー\n");
	    out("<OPTION VALUE='-3' SELECTED>首都の名前\n");
	    out("<OPTION VALUE='-2' SELECTED>宇宙ステ人口\n");
	    out("<OPTION VALUE='-18' SELECTED>サッカー(KP)\n");
	    out("<OPTION VALUE='-17' SELECTED>サッカー(守)\n");
	    out("<OPTION VALUE='-16' SELECTED>サッカー(攻)\n");
	    out("<OPTION VALUE='-14' SELECTED>生物大ＳＰ\n");
	    out("<OPTION VALUE='-13' SELECTED>生物大ＤＰ\n");
	    out("<OPTION VALUE='-12' SELECTED>生物大ＡＰ\n");
	    out("<OPTION VALUE='-11' SELECTED>生物大ＨＰ\n");
	    out("<OPTION VALUE='-1' SELECTED>生物大経験値\n");

    for($i = 0; $i < 71; $i++) {
	$landName = landName($i, 0);

	if($i == $HdefaultLamount1) {
	    out("<OPTION VALUE=$i SELECTED>$landName\n");
        } else {
	    out("<OPTION VALUE=$i>$landName\n");
        }

    }
    out(<<END);
</SELECT>
<INPUT TYPE=text NAME=LAMOUNT2 SIZE=4 VALUE="$lamount2">
<hr>
END
}
    out(<<END);


<B>数量</B><SELECT NAME=AMOUNT>
END

    # 数量
    for($i = 0; $i < 100; $i++) {

	if($HmainMode2 eq 'ijiri') {
	    if($i == 0) {
		$i2 = '単体';
	    } elsif($i == 1) {
		$i2 = '一括';
	    } else {
		$i2 = $i;
	    }
	} else {
	    $i2 = $i;
	}

	out("<OPTION VALUE=$i>$i2\n");
    }

    out(<<END);
</SELECT>
<HR>
<B>目標の島</B><BR>
<FONT size=-1><SELECT NAME=TARGETID>
$HtargetList<BR>
</SELECT></FONT>
<HR>
<B>動作</B><BR>
<INPUT TYPE=radio NAME=COMMANDMODE VALUE=insert CHECKED>挿入
<INPUT TYPE=radio NAME=COMMANDMODE VALUE=write>上書き<BR>
<INPUT TYPE=radio NAME=COMMANDMODE VALUE=delete>削除
<HR>
<INPUT TYPE=submit VALUE="計画送信" NAME=CommandButton$Hislands[$HcurrentNumber]->{'id'}>
$seisaku
</CENTER>
</FORM>
</TD>
<TD $HbgMapCell>
END
    islandMap(1);    # 島の地図、所有者モード
    out(<<END);
<CENTER>
<FORM action="$HthisFile" method="POST" target="_blank">
<B>観光する島</B><SELECT NAME=TARGETID>$HtargetList<BR></SELECT>
<INPUT TYPE="submit" VALUE="画面を開く" NAME="SightButton"><br><br>
</FORM>
END

    my($island) = $Hislands[$HcurrentNumber];
    # 情報表示
    my($rank) = $HcurrentNumber + 1;
	if ($rank > 20)
	    {$aucs3 .= "<br>��<font color=\"royalblue\"><B>$ac3</B></font>／<font color=\"SALMON\"><B>$topvalue3兆円以上</B></font>$acjo3"};
	if ($rank < 21)
	    {$aucs3 = ""};

	if (($rank < 51) && ($auc6a == 1) && (($shuppin1 == 29) || ($shuppin2 == 29) || ($shuppin3 == 29)))
	    {$aucs6 .= "<font color=\"red\">(出品可能)</font>"};
	if (($rank > 50) || ($auc6a != 1) || (($shuppin1 != 29) && ($shuppin2 != 29) && ($shuppin3 != 29)))
	    {$aucs6 = ""};

	if ($auc6a > 2)
	    {$aucs6 .= "<font color=\"red\">(入札不可)</font>"};

    out(<<END);

<FORM action="$HthisFile" method=POST>
<B>Hakoniwa Auction</B>$aucs6
<br>��<font color="royalblue"><B>$ac1</B></font>／<font color="SALMON"><B>$topvalue1兆円以上</B></font>$acjo1
<br>��<font color="royalblue"><B>$ac2</B></font>／<font color="SALMON"><B>$topvalue2兆円以上</B></font>$acjo2
$aucs3
<br>パスワード<INPUT TYPE=password NAME=PASSWORD VALUE="$HdefaultPassword" SIZE=10>


品番<SELECT NAME=AUCNUMBER>
END
    my($i);
    for($i = 1; $i < 3; $i++) {
	out("<OPTION VALUE=$i>$i\n");
    }

    if ($rank > 20) {
	    out("<OPTION VALUE=3>3\n");
    }

    out(<<END);
</SELECT>

金額＋<SELECT NAME=AMOUNT>
END

    # 数量
    for($i = 1; $i < 100; $i++) {
	out("<OPTION VALUE=$i>$i\n");
    }

    out(<<END);
</SELECT>兆円
$nyuusatu
</FORM>
</CENTER>
</TD>
<TD $HbgCommandCell>
END
    for($i = 0; $i < $HcommandMax; $i++) {
	tempCommand($i, $Hislands[$HcurrentNumber]->{'command'}->[$i]);
    }
    my $comment = $Hislands[$HcurrentNumber]->{'comment'};
    out(<<END);

</TD>
</TR>
</TABLE>
</CENTER>
<HR>
<CENTER>
${HtagBig_}コメント更新${H_tagBig}<BR>
<FORM action="$HthisFile" method="POST">
コメント<INPUT TYPE=text NAME=MESSAGE SIZE=80 VALUE="$comment"><BR>
パスワード<INPUT TYPE=password NAME=PASSWORD VALUE="$HdefaultPassword">
<INPUT TYPE=submit VALUE="コメント更新" NAME=MessageButton$Hislands[$HcurrentNumber]->{'id'}>
$kakushuyoso
$shutohen

<BR>
目標の島<SELECT NAME=TARGETID>$HtargetList<BR></SELECT>
有効ターン数<SELECT NAME=AMOUNT>
END

    # 数量
    for($i = 0; $i < 25; $i++) {
	out("<OPTION VALUE=$i>$i\n");
    }


    for($ii = 0; $ii < $HislandNumber; $ii++) {
	$j = $ii + 1;
	$island = $Hislands[$ii];

	$etc7 = $island->{'etc7'};
	$etc7 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
	($msjotai, $nokotan, $msid) = ($1, $2, $3);

	if (($msid == $HcurrentID) && ($msjotai == 1)) {
	    $kyokasinseitiu .= "$island->{'name'}島、";
	}

    }

	my($oStr3) = '';
	if($kyokasinseitiu eq ''){
	  $oStr3 = "";
	} else {
	  $oStr3 = "<BR><BR>★<font color=hotpink><B>$kyokasinseitiuから、あなたの島への援助射撃の申請が届いてます。</B></font>★";
	}

    out(<<END);
</SELECT>
<INPUT TYPE="submit" VALUE="大量破壊兵器の使用許可申請" NAME="MsButton$Hislands[$HcurrentNumber]->{'id'}">
<INPUT TYPE="submit" VALUE="申請許可" NAME="Ms2Button$Hislands[$HcurrentNumber]->{'id'}">
$oStr3
<BR><BR>（注）申請許可をされた島からは有効ターンの間、ミサイルを撃たれることが可能になります。
<BR>　　大使館派遣の際にも、事前に申請許可をもらってから派遣を行なってください。
</FORM>
</CENTER>
END

}

# 入力済みコマンド表示
sub tempCommand {
    my($number, $command) = @_;
    my($kind, $target, $x, $y, $arg) =
	(
	 $command->{'kind'},
	 $command->{'target'},
	 $command->{'x'},
	 $command->{'y'},
	 $command->{'arg'}
	 );
    my($name) = "$HtagComName_${HcomName[$kind]}$H_tagComName";
    my($point) = "$HtagName_($x,$y)$H_tagName";
    my($island) = $Hislands[$HcurrentNumber];
    $target = $HidToName{$target};
    if($target eq '') {
	$target = "無人";
    }
    $target = "$HtagName_${target}島$H_tagName";
    my($value) = $arg * $HcomCost[$kind];
    if($value == 0) {
	$value = $HcomCost[$kind];
    }
    if($value < 0) {
	$value = -$value;
	$value = "$value$HunitFood";
    } else {
	$value = "$value$HunitMoney";
    }
    $value = "$HtagName_$value$H_tagName";

    my($j) = sprintf("%02d：", $number + 1);

    out("<A CLASS=\"type3\" HREF=\"JavaScript:void(0);\" onClick=\"ns($number)\"><NOBR>$HtagNumber_$j$H_tagNumber<FONT COLOR=\"$HnormalColor\" size=\"-1\">");

    if(($kind == $HcomDoNothing) ||
       ($kind == $HcomGiveup)) {
	out("$name");
    } elsif(($kind == $HcomMissileNM) ||
	    ($kind == $HcomMissilePP) ||
	    ($kind == $HcomMissileWP) ||
	    ($kind == $HcomMissileSPP) ||
	    ($kind == $HcomMissileST) ||
	    ($kind == $HcomMissileSS) ||
	    ($kind == $HcomMissileLR) ||
	    ($kind == $HcomMissileLD)) {
	# ミサイル系
	my($n) = ($arg == 0 ? '無制限' : "${arg}発");
	out("$target$pointへ$name($HtagName_$n$H_tagName)");
    } elsif($kind == $HcomTaishi) {
	out("$target$pointへ$name");
    } elsif($kind == $HcomEiseiAtt) {
	if($arg == 99) {
	    $arg = 99;
	} elsif(($arg >= 7) ||
	   ($arg == 0)) {
	    $arg = 1;
	}
	    if($arg == 1) {
		$t = "気象衛星";
	    }
	    if($arg == 2) {
		$t = "観測衛星";
	    }
	    if($arg == 3) {
		$t = "迎撃衛星";
	    }
	    if($arg == 4) {
		$t = "軍事衛星";
	    }
	    if($arg == 5) {
		$t = "防衛衛星";
	    }
	    if($arg == 6) {
		$t = "イレギュラー";
	    }
	    if($arg == 99) {
		$t = "宇宙ステーション";
	    }
	out("$targetの<B>$t</B>へ$name");
    } elsif($kind == $HcomMagic) {
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
	out("$target$pointへ${HtagComName_}${t}${H_tagComName}");
    } elsif($kind == $HcomEiseiLzr) {
	out("$target$pointへ$name");
    } elsif($kind == $HcomSendMonster) {
	# 怪獣派遣
        if ($arg > 30) {
            $arg = 30;
        }
	out("$targetへ$name($HmonsterName[$arg])");
    } elsif($kind == $HcomSell) {
	# 食料輸出
	out("$name$value");
    } elsif($kind == $HcomPropaganda) {
	# 誘致活動
	if($arg == 0) {
	    out("$name");
	} else {
	    out("$name($arg回)");
	}
    } elsif($kind == $HcomEisei) {
	if($arg == 99) {
	    $arg = 99;
	} elsif(($arg >= 7) ||
	   ($arg == 0)) {
	    $arg = 1;
	}

	    if($arg == 1) {
		$t = "気象衛星";
	    }
	    if($arg == 2) {
		$t = "観測衛星";
	    }
	    if($arg == 3) {
		$t = "迎撃衛星";
	    }
	    if($arg == 4) {
		$t = "軍事衛星";
	    }
	    if($arg == 5) {
		$t = "防衛衛星";
	    }
	    if($arg == 6) {
		$t = "イレギュラー";
	    }
	    if($arg == 99) {
		$t = "宇宙ステーション";
	    }
	out("${HtagComName_}${t}打ち上げ${H_tagComName}");
    } elsif($kind == $HcomEiseimente) {
	if($arg == 99) {
	    $arg = 99;
	} elsif(($arg >= 7) ||
	   ($arg == 0)) {
	    $arg = 1;
	}
	    if($arg == 1) {
		$t = "気象衛星";
	    }
	    if($arg == 2) {
		$t = "観測衛星";
	    }
	    if($arg == 3) {
		$t = "迎撃衛星";
	    }
	    if($arg == 4) {
		$t = "軍事衛星";
	    }
	    if($arg == 5) {
		$t = "防衛衛星";
	    }
	    if($arg == 6) {
		$t = "イレギュラー";
	    }
	    if($arg == 99) {
		$t = "宇宙ステーション";
	    }
	out("${HtagComName_}${t}修復${H_tagComName}");
    } elsif(($kind == $HcomMoney) ||
	    ($kind == $HcomFood)) {
	# 援助
	out("$targetへ$name$value");
    } elsif($kind == $HcomEneGive) {
	# 援助
	out("$targetへ$name(${arg}00kW)");
    } elsif($kind == $HcomDestroy) {
	# 掘削
	if($arg != 0) {
	    out("$pointで$name(予算${value})");
	} else {
	    out("$pointで$name");
	}
    } elsif($kind == $HcomMine) {
        # 地雷
        if ($arg == 0) {
            $arg = 1;
        } elsif ($arg > 9) {
            $arg = 9;
        }
        out("$pointで$name(ダメージ$arg)");
    } elsif($kind == $HcomZoo) {
        if ($arg > 30) {
            $arg = 30;
        }
        out("$pointで$name(もしくは$HmonsterName[$arg]脱出)");
    } elsif($kind == $HcomTrain) {	
        if ($arg > 9) {
            $arg = 0;
        }
        out("$pointで$name(指定$arg)");
    } elsif($kind == $HcomKura) {
        if ($arg == 0) {
            $arg = 1;
        }
        out("$pointで$name($arg兆円)");
    } elsif($kind == $HcomKuraf) {
        if ($arg == 0) {
            $arg = 1;
        } elsif ($arg > 9) {
            $arg = 9;
        }
        out("$pointで$name(${arg}00万トン)");
    } elsif($kind == $HcomKura2) {
        if ($arg == 0) {
            $arg = 1;
        }
        out("$pointで$name($arg兆円or${arg}00万トン)");
    } elsif($kind == $HcomFune) {
        if ($arg == 0) {
            $arg = 1;
        }
        out("$pointで$name($HfuneName[$arg])");
    } elsif($kind == $HcomMonument) {
        out("$pointで$name($HmonumentName[$arg])");
    } elsif($kind == $HcomFarmcpc) {
	if(($arg >= 4) ||
	   ($arg == 0)) {
	    $arg = 1;
	}
	    if($arg == 1) {
		$t = "養鶏場";
	    }
	    if($arg == 2) {
		$t = "養豚場";
	    }
	    if($arg == 3) {
		$t = "牧場";
	    }
	out("$pointで$name($t)");
    } elsif($kind == $HcomCollege) {
		$etc5 = $island->{'etc5'};
		$etc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
		($s00,$s01,$s02,$s03,$s04,$s05,$s06,$s07,$s08,$s09,$s10,$s11,$s12,$s13,$s14,$s15,$s16,$s17,$s18,$s19,$s20,$s21,$s22,$s23,$s24,$s25,$s26,$s27,$s28,$s29,$s30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
		$s10b = int($s10/5)+1;
		if(($s00 > 0) && ($arg < 10) && ($arg != 0) && ($arg-1 < $s10b)) {
			if($arg == 0) {
			    $arg = 1;
			}
		    if($arg == 1) {
			$t = "農業大学";
		    }
		    if($arg == 2) {
			$t = "工業大学";
		    }
		    if($arg == 3) {
			$t = "総合大学";
		    }
		    if($arg == 4) {
			$t = "軍事大学";
		    }
		    if($arg == 5) {
			$t = "生物大学";
		    }
		    if($arg == 6) {
			$t = "気象大学";
		    }
		    if($arg == 7) {
			$t = "経済大学";
		    }
		    if($arg == 8) {
			$t = "魔法学校";
		    }
		    if($arg == 9) {
			$t = "電工大学";
		    }
			out("$pointで$name($t)");
		} else {
			out("$pointで$name");
		}

    } elsif(($kind == $HcomFarm) ||
	     ($kind == $HcomFoodim) ||
	     ($kind == $HcomFactory) ||
             ($kind == $HcomNursery) ||
             ($kind == $HcomEneAt) ||
             ($kind == $HcomEneFw) ||
             ($kind == $HcomEneWt) ||
             ($kind == $HcomEneBo) ||
             ($kind == $HcomEneWd) ||
             ($kind == $HcomEneSo) ||
             ($kind == $HcomEneCs) ||
             ($kind == $HcomBoku) ||
             ($kind == $HcomPark) ||
             ($kind == $HcomUmiamu) ||
             ($kind == $HcomKai) ||
             ($kind == $HcomHTget) ||
             ($kind == $HcomGivefood) ||
	     ($kind == $HcomMountain)) {	
	# 回数付き
	if($arg == 0) {
	    out("$pointで$name");
	} else {
	    out("$pointで$name($arg回)");
	}
    } else {
	# 座標付き
	out("$pointで$name");
    }

    out("</FONT></NOBR></A><BR>");
}

# ローカル掲示板
sub tempLbbsHead {
    out(<<END);
<HR>
<CENTER>
${HtagBig_}${HtagName_}${HcurrentName}島${H_tagName}観光者通信${H_tagBig}<BR>
</CENTER>
END
}

# ローカル掲示板入力フォーム
sub tempLbbsInput {
    out(<<END);
<CENTER>
<FORM action="$HthisFile" method="POST">
END
    if ($HlbbsMoneyPublic + $HlbbsMoneySecret > 0) {
        # 発言は有料
        out("<CENTER><B>※</B>");
        out("公開通信は<B>$HlbbsMoneyPublic$HunitMoney</B>です。") if ($HlbbsMoneyPublic > 0);
        out("極秘通信は<B>$HlbbsMoneySecret$HunitMoney</B>です。") if ($HlbbsMoneySecret > 0);
        out("</CENTER>");
    }
    out(<<END);
<TABLE BORDER>
<TR>
<TH>パスワード</TH>
<TH>島名</TH>
<TH>通信方法</TH>
</TR>
<TR>
<TD><INPUT TYPE=password SIZE=32 MAXLENGTH=32 NAME=PASSWORD VALUE="$HdefaultPassword"></TD>
<TD>
<SELECT NAME="ISLANDID2">$HislandList</SELECT>
END
    out(<<END) if ($HlbbsAnon);
<INPUT TYPE="radio" NAME="LBBSTYPE" VALUE="ANON">観光客
END
    out(<<END);
</TD>
<TD>
<INPUT TYPE="radio" NAME="LBBSTYPE" VALUE="PUBLIC" CHECKED>公開
<INPUT TYPE="radio" NAME="LBBSTYPE" VALUE="SECRET"><FONT COLOR="red">極秘</FONT>
</TD>
</TR>
<TR>
<TH>名前</TH>
<TH>内容</TH>
<TH>動作</TH>
</TR>
<TR>
<TD><INPUT TYPE="text" SIZE=32 MAXLENGTH=32 NAME="LBBSNAME" VALUE="$HdefaultName"></TD>
<TD><INPUT TYPE="text" SIZE=80 NAME="LBBSMESSAGE"></TD>
<TD><CENTER><INPUT TYPE="submit" VALUE="記帳する" NAME="LbbsButtonSS$HcurrentID"></CENTER></TD>
</TR>
</TABLE>
</FORM>
</CENTER>
END
}

# ローカル掲示板入力フォーム owner mode用
sub tempLbbsInputOW {
    out(<<END);
<CENTER>
<FORM action="$HthisFile" method="POST">
<TABLE BORDER>
<TR>
<TH>名前</TH>
<TH COLSPAN=2>内容</TH>
</TR>
<TR>
<TD><INPUT TYPE="text" SIZE=32 MAXLENGTH=32 NAME="LBBSNAME" VALUE="$HdefaultName"></TD>
<TD COLSPAN=2><INPUT TYPE="text" SIZE=80 NAME="LBBSMESSAGE"></TD>
</TR>
<TR>
<TH>パスワード</TH>
<TH COLSPAN=2>動作</TH>
</TR>
<TR>
<TD><INPUT TYPE=password SIZE=32 MAXLENGTH=32 NAME=PASSWORD VALUE="$HdefaultPassword"></TD>
<TD align=right>
<INPUT TYPE="submit" VALUE="記帳する" NAME="LbbsButtonOW$HcurrentID">
</TD>
<TD align=right>
番号
<SELECT NAME=NUMBER>
END
    # 発言番号
    my($j, $i);
    for($i = 0; $i < $HlbbsMax; $i++) {
	$j = $i + 1;
	out("<OPTION VALUE=$i>$j\n");
    }
    out(<<END);
</SELECT>
<INPUT TYPE="submit" VALUE="削除する" NAME="LbbsButtonDL$HcurrentID">
</TD>
</TR>
</TABLE>
</FORM>
</CENTER>
END
}

# ローカル掲示板内容
sub tempLbbsContents {
    my($lbbs, $line);
    $lbbs = $Hislands[$HcurrentNumber]->{'lbbs'};
    out(<<END);
<CENTER>
<TABLE BORDER>
<TR>
<TH>番号</TH>
<TH>記帳内容</TH>
</TR>
END


    my($i);
    for($i = 0; $i < $HlbbsMax; $i++) {
        $line = $lbbs->[$i];
        if($line =~ /([0-9]*)\<(.*)\<([0-9]*)\>(.*)\>(.*)$/) {
            my($j) = $i + 1;
            out("<TR><TD align=center>$HtagNumber_$j$H_tagNumber</TD>");
            my($speaker);
            $speaker = "<FONT COLOR=gray><B><SMALL>($2)</SMALL></B></FONT>" if ($HlbbsSpeaker && ($2 ne ''));
            if($3 == 0) {
                # 観光者
                if ($1 == 0) {
                    # 公開
                    out("<TD>$HtagLbbsSS_$4 > $5$H_tagLbbsSS $speaker</TD></TR>");
                } else {
                    # 極秘
                    if ($HmainMode ne 'owner') {
                        # 観光客
                        out("<TD><CENTER><FONT COLOR=gray>- 極秘 -</FONT></CENTER></TD></TR>");
                    } else {
                        # オーナー
                        out("<TD>$HtagLbbsSS_$4 >(秘) $5$H_tagLbbsSS $speaker</TD></TR>");
                    }
                }
            } else {
                # 島主
                out("<TD>$HtagLbbsOW_$4 > $5$H_tagLbbsOW $speaker</TD></TR>");
            }
        }
    }

    out(<<END);

</TD></TR></TABLE></CENTER>
END
}

# すでに同じＩＰの島がある場合
sub tempIP2IslandAlready {
    out(<<END);
${HtagBig_}登録されたＩＰと異なる場合、侵入できません。${H_tagBig}$HtempBack
END
}

# ローカル掲示板で名前かメッセージがない場合
sub tempLbbsNoMessage {
    out(<<END);
${HtagBig_}名前または内容の欄が空欄です。${H_tagBig}$HtempBack
END
}

# 書きこみ削除
sub tempLbbsDelete {
    out(<<END);
${HtagBig_}記帳内容を削除しました${H_tagBig}<HR>
END
}

# コマンド登録
sub tempLbbsAdd {
    out(<<END);
${HtagBig_}記帳を行いました${H_tagBig}<HR>
END
}

# 通信資金足りず
sub tempLbbsNoMoney {
    out(<<END);
${HtagBig_}資金不足のため記帳できません${H_tagBig}$HtempBack
END
}

# 資金足りず
sub tempNoMoney {
    out(<<END);
${HtagBig_}資金が足りません${H_tagBig}$HtempBack
END
}

# 資金足りず
sub tempNoMoney2 {
    out(<<END);
${HtagBig_}現在トップですよ${H_tagBig}$HtempBack
END
}

# 資金足りず
sub tempNoMoney3 {
    out(<<END);
${HtagBig_}入札は１品までです${H_tagBig}$HtempBack
END
}

# 資金足りず
sub tempNoMoney4 {
    out(<<END);
${HtagBig_}こちらの商品は落札されました${H_tagBig}$HtempBack
END
}

# コマンド削除
sub tempCommandDelete {
    out(<<END);
${HtagBig_}コマンドを削除しました${H_tagBig}<HR>
END
}

# コマンド登録
sub tempCommandAdd {
    out(<<END);
${HtagBig_}コマンドを登録しました${H_tagBig}<HR>
END
}

# コメント変更成功
sub tempComment {
    out(<<END);
${HtagBig_}コメントを更新しました${H_tagBig}<HR>
END
}

# toto変更成功
sub tempToto {
    out(<<END);
${HtagBig_}予想しました${H_tagBig}<HR>
END
}

# toto変更成功
sub tempToto2 {
    out(<<END);
${HtagBig_}変更しました${H_tagBig}<HR>
END
}

# toto変更成功
sub tempToto3 {
    out(<<END);
${HtagBig_}入札しました${H_tagBig}<HR>
END
}

# ms変更成功
sub tempMs {
    out(<<END);
${HtagBig_}許可申請しました${H_tagBig}<HR>
END
}

# toto変更不能
sub tempTotoend {
    out(<<END);
${HtagBig_}現在、変更できません${H_tagBig}<HR>$HtempBack
END
}

# 近況
sub tempRecent {
    my($mode) = @_;
    out(<<END);
<HR>
${HtagBig_}${HtagName_}${HcurrentName}島${H_tagName}の近況${H_tagBig}<BR>
END
    logPrintLocal($mode);
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

sub tempChange2 {
    out(<<END);
${HtagBig_}清き１票ありがとうございました。${H_tagBig}$HtempBack
END
}

# パスワード間違い
sub tempWrongPassword3 {
    out(<<END);
${HtagBig_}自分の島には無理ですよ。${H_tagBig}$HtempBack
END
}

# パスワード間違い
sub tempWrongPassword4 {
    out(<<END);
${HtagBig_}１島１票まででお願いします。${H_tagBig}$HtempBack
END
}

# パスワード間違い
sub tempWrongPassword5 {
    out(<<END);
${HtagBig_}３票までしか投票できません。結果をお待ちください。${H_tagBig}$HtempBack
END
}

# パスワード間違い
sub tempWrongPassword6 {
    out(<<END);
${HtagBig_}どれか選んでね。${H_tagBig}$HtempBack
END
}

1;

#----------------------------------------------------------------------
# 箱庭諸島 ver2.30
# トップモジュール(ver1.00)
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


#----------------------------------------------------------------------
# トップページモード
#----------------------------------------------------------------------
# メイン
sub topPageMain {
    # 開放
    unlock();

    # テンプレート出力
    tempTopPage();
}

# メイン
sub topPageMain {
	#アクセスログ取得
	if($HtopAxes) {
		axeslog();
	}
	# 開放
	unlock();
	# テンプレート出力
	tempTopPage(0);
}

sub topPageMainL {
	#アクセスログ取得
	if($HtopAxes) {
		axeslog();
	}
	# 開放
	unlock();
	# テンプレート出力
	tempTopPage(1);
}

sub topPageMainS {
	#アクセスログ取得
	if($HtopAxes) {
		axeslog();
	}
	# 開放
	unlock();
	# テンプレート出力
	tempTopPage(2);
}

#=============================================
#■アクセスログ取得
#=============================================
sub axeslog {
	my @lines;


	my $cookie;
	$cookie = jcode::euc($ENV{'HTTP_COOKIE'});
	if($cookie =~ /OWNISLANDID=\(([^\)]*)\)/) {
		$cookie = $1;
	}
	
	my $agent   = $ENV{'HTTP_USER_AGENT'};
	my $addr	= $ENV{'REMOTE_ADDR'};
	my $host	= $ENV{'REMOTE_HOST'};
	my $referer = $ENV{'HTTP_REFERER'};
	if (($host eq $addr) || ($host eq '')) {
		$host = gethostbyaddr(pack('C4',split(/\./,$addr)),2) || $addr;
	}
	$ENV{'TZ'} = 'JST-9';
	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
	my $day = ('日','月','火','水','木','金','土')[$wday];
	$year = $year + 1900;
	$mon = $mon + 1;
	my $date = sprintf("%04d/%02d/%02d(%s) %02d:%02d:%02d",$year,$mon,$mday,$day,$hour,$min,$sec);

	open(IN, "$HaxesLogfile");
	my @lines = <IN>;
	close(IN);
	
	while ($HaxesMax <= @lines) { pop @lines; }
	unshift(@lines, "[$date] - $referer - $host - $addr - $agent - $cookie\n");
	
	if(open(OUT, ">$HaxesLogfile")){
		foreach $line (@lines) {
			print OUT jcode::sjis($line);
		}
		close(OUT);
	} else {
		tempProblem();
		return;
	}
}

1;

# トップページ
sub tempTopPage {
    # タイトル
    out(<<END);
${HtagTitle_}$Htitle${H_tagTitle}
END

    # デバッグモードなら「ターンを進める」ボタン
    if($Hdebug == 1) {
        out(<<END);
<FORM action="$HthisFile" method="POST">
<INPUT TYPE="submit" VALUE="ターンを進める" NAME="TurnButton">
</FORM>
END
    }

    my($mStr1) = '';
    if($HhideMoneyMode != 0) {
	$mStr1 = "<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}資金${H_tagTH}</NOBR></TH>";
    }

    # フォーム
    my($remain) = $HunitTime + $HislandLastTime - time;
    out(<<END);
<H1>${HtagHeader_}ターン$HislandTurn${H_tagHeader}</H1>
<FORM name="RemainForm"><INPUT name="RemainTime" size="30" type="text" readonly></FORM><SCRIPT language="JavaScript">
<!--
nextTurn = ${remain}; loadDate = new Date();
timerID = setTimeout('dispRemainTime()', 100);
function dispRemainTime() { clearTimeout(timerID);
document.RemainForm.RemainTime.value = getRemainTime();
timerID = setTimeout('dispRemainTime()', 1000);}
function getRemainTime() {
now = new Date();msec = now.getTime() - loadDate.getTime();
msec -= msec % 1000; msec /= 1000;msec = nextTurn - msec;
if (msec < 0) {msec = 0;}
sec = msec % 60; msec = (msec - sec) / 60;
min = msec % 60; hour = (msec - min) / 60;
if (hour < 10) {hour = "0" + hour;}
if (min < 10) {min = "0" + min;}
if (sec < 10) {sec = "0" + sec;}
return "次のターンまで残り" + hour + ":" + min + ":" + sec;}
//-->
</SCRIPT>
<HR>
<H1>${HtagHeader_}自分の島へ${H_tagHeader}</H1>
<FORM action="$HthisFile" method="POST">
あなたの島の名前は？<BR>
<SELECT NAME="ISLANDID">
$HislandList
</SELECT><BR>

パスワードをどうぞ！！<BR>
<INPUT TYPE="password" NAME="PASSWORD" VALUE="$HdefaultPassword" SIZE=32 MAXLENGTH=32><BR>
<INPUT TYPE="submit" VALUE="開発しに行く" NAME="OwnerButton"><BR>
</FORM>

END

	if ($AnkeitoOnOff == 1) {

	$anjo = "<INPUT TYPE=\"submit\" VALUE=\"投票する\" NAME=\"AnkeButton\">";

	$ant = $an1+$an2+$an3+$an4+$an5;
	$ant2 = $an1+$an2+$an3+$an4+$an5;

	if ($ant == 0) {
	    $ant = 1;
	}

	if ($HislandNumber == 0) {
	    $HislandNumber = 1;
	}

	$ant3 = int($ant2/$HislandNumber*100);

	$an1p = int($an1/$ant*100);
	$an2p = int($an2/$ant*100);
	$an3p = int($an3/$ant*100);
	$an4p = int($an4/$ant*100);
	$an5p = int($an5/$ant*100);

    out(<<END);
<br>
<H1>${HtagHeader_}<font color="MEDIUMSEAGREEN">アンケート</font>${H_tagHeader}</H1>
$AnkeitoSetumei
<TABLE border="1" cellpadding="1" cellspacing="1">
<TR>
<TD $HbgTitleCell align=center nowrap=nowrap><NOBR>　</NOBR></TD>
<TD $HbgTitleCell COLSPAN=2 align=center nowrap=nowrap><NOBR><B><font color="royalblue">$AnkeitoShitumon0</font></B></NOBR></TD>
</TR>
<TR>
<TD $HbgTitleCell ROWSPAN=2 align=center nowrap=nowrap><INPUT type="radio" name="ann" value="1"></TD>
<TD $HbgNameCell align=left nowrap=nowrap><NOBR>　Ａ．$AnkeitoShitumon1</NOBR></TD>
<TD $HbgPoinCell align=center nowrap=nowrap><NOBR>$an1票</NOBR></TD>
</TR>
<TR>
<TD $HbgNameCell COLSPAN=2 align=center nowrap=nowrap><NOBR>
<TABLE border="0" cellpadding="0" cellspacing="0" width=100%>
<TR>
<TD align=left nowrap=nowrap><NOBR></NOBR></TD>
<TD rowspan="4" align=center nowrap=nowrap><NOBR>($an1p%)</NOBR></TD>
</TR>
<TR>
<TD $HbgInfoCell align=left nowrap=nowrap width=$an1p%><NOBR></NOBR></TD>
</TR>
<TR>
<TD $HbgInfoCell align=left nowrap=nowrap width=$an1p%><NOBR></NOBR></TD>
</TR>
<TR>
<TD align=left nowrap=nowrap><NOBR></NOBR></TD>
</TR>
</TABLE>
</NOBR></TD>
</TR>
<TR>
<TD $HbgTitleCell ROWSPAN=2 align=center nowrap=nowrap><INPUT type="radio" name="ann" value="2"></TD>
<TD $HbgNameCell align=left nowrap=nowrap><NOBR>　Ｂ．$AnkeitoShitumon2</NOBR></TD>
<TD $HbgPoinCell align=center nowrap=nowrap><NOBR>$an2票</NOBR></TD>
</TR>
<TR>
<TD $HbgNameCell COLSPAN=2 align=center nowrap=nowrap><NOBR>
<TABLE border="0" cellpadding="0" cellspacing="0" width=100%>
<TR>
<TD align=left nowrap=nowrap><NOBR></NOBR></TD>
<TD rowspan="4" align=center nowrap=nowrap><NOBR>($an2p%)</NOBR></TD>
</TR>
<TR>
<TD $HbgInfoCell align=left nowrap=nowrap width=$an2p%><NOBR></NOBR></TD>
</TR>
<TR>
<TD $HbgInfoCell align=left nowrap=nowrap width=$an2p%><NOBR></NOBR></TD>
</TR>
<TR>
<TD align=left nowrap=nowrap><NOBR></NOBR></TD>
</TR>
</TABLE>
</NOBR></TD>
</TR>
<TR>
<TD $HbgTitleCell ROWSPAN=2 align=center nowrap=nowrap><INPUT type="radio" name="ann" value="3"></TD>
<TD $HbgNameCell align=left nowrap=nowrap><NOBR>　Ｃ．$AnkeitoShitumon3</NOBR></TD>
<TD $HbgPoinCell align=center nowrap=nowrap><NOBR>$an3票</NOBR></TD>
</TR>
<TR>
<TD $HbgNameCell COLSPAN=2 align=center nowrap=nowrap><NOBR>
<TABLE border="0" cellpadding="0" cellspacing="0" width=100%>
<TR>
<TD align=left nowrap=nowrap><NOBR></NOBR></TD>
<TD rowspan="4" align=center nowrap=nowrap><NOBR>($an3p%)</NOBR></TD>
</TR>
<TR>
<TD $HbgInfoCell align=left nowrap=nowrap width=$an3p%><NOBR></NOBR></TD>
</TR>
<TR>
<TD $HbgInfoCell align=left nowrap=nowrap width=$an3p%><NOBR></NOBR></TD>
</TR>
<TR>
<TD align=left nowrap=nowrap><NOBR></NOBR></TD>
</TR>
</TABLE>
</NOBR></TD>
</TR>
<TR>
<TD $HbgTitleCell ROWSPAN=2 align=center nowrap=nowrap><INPUT type="radio" name="ann" value="4"></TD>
<TD $HbgNameCell align=left nowrap=nowrap><NOBR>　Ｄ．$AnkeitoShitumon4</NOBR></TD>
<TD $HbgPoinCell align=center nowrap=nowrap><NOBR>$an4票</NOBR></TD>
</TR>
<TR>
<TD $HbgNameCell COLSPAN=2 align=center nowrap=nowrap><NOBR>
<TABLE border="0" cellpadding="0" cellspacing="0" width=100%>
<TR>
<TD align=left nowrap=nowrap><NOBR></NOBR></TD>
<TD rowspan="4" align=center nowrap=nowrap><NOBR>($an4p%)</NOBR></TD>
</TR>
<TR>
<TD $HbgInfoCell align=left nowrap=nowrap width=$an4p%><NOBR></NOBR></TD>
</TR>
<TR>
<TD $HbgInfoCell align=left nowrap=nowrap width=$an4p%><NOBR></NOBR></TD>
</TR>
<TR>
<TD align=left nowrap=nowrap><NOBR></NOBR></TD>
</TR>
</TABLE>
</NOBR></TD>
</TR>
<TR>
<TD $HbgTitleCell ROWSPAN=2 align=center nowrap=nowrap><INPUT type="radio" name="ann" value="5"></TD>
<TD $HbgNameCell align=left nowrap=nowrap><NOBR>　Ｅ．$AnkeitoShitumon5</NOBR></TD>
<TD $HbgPoinCell align=center nowrap=nowrap><NOBR>$an5票</NOBR></TD>
</TR>
<TR>
<TD $HbgNameCell COLSPAN=2 align=center nowrap=nowrap><NOBR>
<TABLE border="0" cellpadding="0" cellspacing="0" width=100%>
<TR>
<TD align=left nowrap=nowrap><NOBR></NOBR></TD>
<TD rowspan="4" align=center nowrap=nowrap><NOBR>($an5p%)</NOBR></TD>
</TR>
<TR>
<TD $HbgInfoCell align=left nowrap=nowrap width=$an5p%><NOBR></NOBR></TD>
</TR>
<TR>
<TD $HbgInfoCell align=left nowrap=nowrap width=$an5p%><NOBR></NOBR></TD>
</TR>
<TR>
<TD align=left nowrap=nowrap><NOBR></NOBR></TD>
</TR>
</TABLE>
</NOBR></TD>
</TR>
<TR>
<TD $HbgTotoCell COLSPAN=3 align=center nowrap=nowrap><NOBR>$anjo　　($ant2/$HislandNumber票…$ant3%)</NOBR></TD>
</TR>
</TABLE>



END

    }
    out(<<END);

<br>
<HR>
END

    my($island, $j, $farm, $factory, $mountain, $name, $id, $ii);
    for($ii = 0; $ii < $HislandNumber; $ii++) {
	$j = $ii + 1;
	$island = $Hislands[$ii];

	$id = $island->{'id'};
	$farm = $island->{'farm'};

	$factory = $island->{'factory'};
	$factory =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($factory1, $factory2, $co0, $co1, $htf, $shtf, $co95, $co95, $co95, $co95) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10);
	$factoryt = $factory1 + $factory2;

	$island->{'factoryt'} = $factoryt;

	$mountain = $island->{'mountain'};



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
	    my($islandauc, $j, $ii);
	    for($ii = 0; $ii < $HislandNumber; $ii++) {
		$j = $ii + 1;
		$islandauc = $Hislands[$ii];
			if($avalue1 == $islandauc->{'id'}) {
			    $dashiname = $islandauc->{'auc7'};
			}
		}
	    $ac1 = "$dashiname";
	} else {
	    $ac1 = '？';
	}

	if($ajoutai1 == 15) {
	    $acjo1 = "<font color=\"hotpink\">(落札済み)</font>";
	} else {
	    $acjot1 = 15-$ajoutai1;
	    $acjo1 = "<font color=\"royalblue\">(残り$acjot1ターン)</font>";
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
	    my($islandauc, $j, $ii);
	    for($ii = 0; $ii < $HislandNumber; $ii++) {
		$j = $ii + 1;
		$islandauc = $Hislands[$ii];
			if($avalue2 == $islandauc->{'id'}) {
			    $dashiname = $islandauc->{'auc7'};
			}
		}
	    $ac2 = "$dashiname";
	} else {
	    $ac2 = '？';
	}

	if($ajoutai2 == 15) {
	    $acjo2 = "<font color=\"hotpink\">(落札済み)</font>";
	} else {
	    $acjot2 = 15-$ajoutai2;
	    $acjo2 = "<font color=\"royalblue\">(残り$acjot2ターン)</font>";
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
	    my($islandauc, $j, $ii);
	    for($ii = 0; $ii < $HislandNumber; $ii++) {
		$j = $ii + 1;
		$islandauc = $Hislands[$ii];
			if($avalue3 == $islandauc->{'id'}) {
			    $dashiname = $islandauc->{'auc7'};
			}
		}
	    $ac3 = "$dashiname";
	} else {
	    $ac3 = '？';
	}

	if($ajoutai3 == 15) {
	    $acjo3 = "<font color=\"hotpink\">(落札済み)</font>";
	} else {
	    $acjot3 = 15-$ajoutai3;
	    $acjo3 = "<font color=\"royalblue\">(残り$acjot3ターン)</font>";
	}


	$eisei3 = $island->{'eisei3'};
	$eisei3 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($ene, $shouhi, $sabun, $chikuden, $ene) = ($1, $2, $3, $4, $5);
	$island->{'ene'} = $ene;


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

	$island->{'kachiten'} = $kachiten;
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

	$etc6 = $island->{'etc6'};
	$etc6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($z0,$z1,$z2,$z3,$z4,$z5,$z6,$z7,$z8,$z9,$z10,$z11,$z12,$z13,$z14,$z15,$z16,$z17,$z18,$z19,$z20,$z21,$z22,$z23,$z24,$z25,$z26,$z27,$z28,$z29,$z30) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
	($z->{'0'},$z->{'1'},$z->{'2'},$z->{'3'},$z->{'4'},$z->{'5'},$z->{'6'},$z->{'7'},$z->{'8'},$z->{'9'},$z->{'10'},$z->{'11'},$z->{'12'},$z->{'13'},$z->{'14'},$z->{'15'},$z->{'16'},$z->{'17'},$z->{'18'},$z->{'19'},$z->{'20'},$z->{'21'},$z->{'22'},$z->{'23'},$z->{'24'},$z->{'25'},$z->{'26'},$z->{'27'},$z->{'28'},$z->{'29'},$z->{'30'}) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,$12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22,$23, $24, $25, $26, $27, $28, $29, $30, $31);
	$zookazu = $z0+$z1+$z2+$z3+$z4+$z5+$z6+$z7+$z8+$z9+$z10+$z11+$z12+$z13+$z14+$z15+$z16+$z17+$z18+$z19+$z20+$z21+$z22+$z23+$z24+$z25+$z26+$z27+$z28+$z29+$z30;

	$monsterlive = $island->{'monsterlive'};
	$monsterlive2 = $monsterlive + $zookazu;
	$island->{'monsterlive2'} = $monsterlive2;

	$auc0 = $island->{'auc0'};
	$auc0 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($auc0a, $auc0b, $auc0c, $auc0d, $auc0e) = ($1, $2, $3, $4, $5);
	$island->{'auc0c'} = $auc0c;

	$auc5 = $island->{'auc5'};
	$auc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($auc5a, $auc5b, $auc5c, $auc5d, $auc5e) = ($1, $2, $3, $4, $5);
	$island->{'auc5c'} = $auc5c;

	}
	islandSortPop();
            my($islandp) = $Hislands[0];
	islandSortFarm();
            my($islandfm) = $Hislands[0];
	islandSortFactory();
            my($islandfc) = $Hislands[0];
	islandSortMountain();
            my($islandm) = $Hislands[0];
	islandSortArea();
            my($islanda) = $Hislands[0];
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
	islandSortPika();
            my($islandpika) = $Hislands[0];
	islandSortHamu();
            my($islandhamu) = $Hislands[0];
	islandSortMonta();
            my($islandmonta) = $Hislands[0];
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

	$rena = $islandr->{'rena'};
	$renae = int($rena / 10 ) + 1;
	$idp = $islandp->{'id'};
	    $islandp->{'bumon'} ++;
	    $islandp->{'bumonp'} ++;
	$idfm = $islandfm->{'id'};
	    $islandfm->{'bumon'} ++;
	    $islandfm->{'bumonfm'} ++;
	$idfc = $islandfc->{'id'};
	    $islandfc->{'bumon'} ++;
	    $islandfc->{'bumonfc'} ++;
	$idm = $islandm->{'id'};
	    $islandm->{'bumon'} ++;
	    $islandm->{'bumonm'} ++;
	$ida = $islanda->{'id'};
	$idf = $islandf->{'id'};
	    $islandf->{'bumon'} ++;
	    $islandf->{'bumonf'} ++;
	$idl = $islandl->{'id'};
	    $islandl->{'bumon'} ++;
	    $islandl->{'bumonl'} ++;
	$idr = $islandr->{'id'};
	    $islandr->{'bumon'} ++;
	    $islandr->{'bumonr'} ++;
	$idk = $islandk->{'id'};
	    $islandk->{'bumon'} ++;
	    $islandk->{'bumonk'} ++;
	$idw = $islandw->{'id'};
	    $islandw->{'bumon'} ++;
	    $islandw->{'bumonw'} ++;
	$idpika = $islandpika->{'id'};
	$idhamu = $islandhamu->{'id'};
	$idmonta = $islandmonta->{'id'};
	$idtare = $islandtare->{'id'};
	    $islandtare->{'bumon'} ++;
	    $islandtare->{'bumontare'} ++;
	$idzipro = $islandzipro->{'id'};
	    $islandzipro->{'bumon'} ++;
	    $islandzipro->{'bumonzipro'} ++;
	$idleje = $islandleje->{'id'};
	    $islandleje->{'bumon'} ++;
	    $islandleje->{'bumonleje'} ++;
	$idforce = $islandforce->{'id'};
	    $islandforce->{'bumon'} ++;
	    $islandforce->{'bumonforce'} ++;
	$ideisei2 = $islandeisei2->{'id'};
	    $islandeisei2->{'bumon'} ++;
	    $islandeisei2->{'bumoneisei2'} ++;
	$iduni = $islanduni->{'id'};
	    $islanduni->{'bumon'} ++;
	    $islanduni->{'bumonuni'} ++;
	$tuni = $islanduni->{'tuni'};

	$idhck = $islandhck->{'id'};
	    $islandhck->{'bumon'} ++;
	    $islandhck->{'bumonhck'} ++;
	$idhckt = $islandhckt->{'id'};
	    $islandhckt->{'bumon'} ++;
	    $islandhckt->{'bumonhckt'} ++;
	$idhcr = $islandhcr->{'id'};
	    $islandhcr->{'bumon'} ++;
	    $islandhcr->{'bumonhcr'} ++;
	$idhcy = $islandhcy->{'id'};
	    $islandhcy->{'bumon'} ++;
	    $islandhcy->{'bumonhcy'} ++;
	$idhct = $islandhct->{'id'};
	    $islandhct->{'bumon'} ++;
	    $islandhct->{'bumonhct'} ++;


	$eisei4 = $islandhck->{'eisei4'};
	$eisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($ksto, $kstd, $kstk, $kstwin, $kstdrow, $kstlose, $kstwint, $kstdrowt, $kstloset, $kstyusho, $kstshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);

	$eisei4 = $islandhckt->{'eisei4'};
	$eisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($ktsto, $ktstd, $ktstk, $ktstwin, $ktstdrow, $ktstlose, $ktstwint, $ktstdrowt, $ktstloset, $ktstyusho, $ktstshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);

	$eisei4 = $islandhcr->{'eisei4'};
	$eisei4 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($rsto, $rstd, $rstk, $rstwin, $rstdrow, $rstlose, $rstwint, $rstdrowt, $rstloset, $rstyusho, $rstshoka) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);


	islandSort();

	my($loopInit) = $viewFirst;
	my($loopEnd) = $viewFirst + $viewNumber;
	if($viewFirst < 0) { $viewFirst = $loopInit = 0;}
	if($loopEnd > $HislandNumber) { $loopEnd = $HislandNumber;}
	if($viewFlag eq 'ALL') { $loopEnd = $HislandNumber;}
	my($first) = $loopInit + 1;

        out(<<END);

<H1>${HtagHeader_}各部門別ＮＯ.１${H_tagHeader}</H1>
<P>
目指せ<B>ＡＬＬ ＮＯ.１!!</B>各部門でNO.1になると諸島の状況に部門賞が表示されます。
</P>
<TABLE ALIGN="center" width="100%"><tr><td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>人口NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idp}" \"alt="ID=${idp}">${HtagName_}$islandp->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islandp->{'pop'}$HunitPop</TD></TR>
</TABLE><td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>農場NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idfm}" \"alt="ID=${idfm}">${HtagName_}$islandfm->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islandfm->{'farm'}0$HunitPop規模</TD></TR>
</TABLE><td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>職場NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idfc}" \"alt="ID=${idfc}">${HtagName_}$islandfc->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islandfc->{'factoryt'}0$HunitPop規模</TD></TR>
</TABLE><td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>採掘場NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idm}" \"alt="ID=${idm}">${HtagName_}$islandm->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islandm->{'mountain'}0$HunitPop規模</TD></TR>
</TABLE><td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>森林NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idw}" \"alt="ID=${idw}">${HtagName_}$islandw->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islandw->{'fore'}$HunitTree</TD></TR>
</TABLE>
</TABLE>
<br>
<TABLE ALIGN="center" width="100%">
<td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>にわとり数NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idtare}" \"alt="ID=${idtare}">${HtagName_}$islandtare->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islandtare->{'tare'}万羽</TD></TR>
</TABLE>
<td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>ぶた数NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idzipro}" \"alt="ID=${idzipro}">${HtagName_}$islandzipro->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islandzipro->{'zipro'}万頭</TD></TR>
</TABLE>
<td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>うし数NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idleje}" \"alt="ID=${idleje}">${HtagName_}$islandleje->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islandleje->{'leje'}万頭</TD></TR>
</TABLE>
<td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>怪獣出現＆捕獲数NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idl}" \"alt="ID=${idl}">${HtagName_}$islandl->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islandl->{'monsterlive2'}$HunitMonster</TD></TR>
</TABLE>
<td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>怪獣退治数NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idk}" \"alt="ID=${idk}">${HtagName_}$islandk->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islandk->{'taiji'}$HunitMonster</TD></TR>
</TABLE>
</TABLE>
<br>
<TABLE ALIGN="center" width="100%">
<td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>生物大学能力NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idforce}" \"alt="ID=${idforce}">${HtagName_}$islandforce->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">合計$islandforce->{'force'}pts.</TD></TR>
</TABLE>
<td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>通算観光客NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${ideisei2}" \"alt="ID=${ideisei2}">${HtagName_}$islandeisei2->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islandeisei2->{'eisei2'}$HunitPop</TD></TR>
</TABLE>
<td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>ユニーク地形数NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${iduni}" \"alt="ID=${iduni}">${HtagName_}$islanduni->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islanduni->{'uni'}種類/$tuniヶ所</TD></TR>
</TABLE>
<td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>記念碑数NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idf}" \"alt="ID=${idf}">${HtagName_}$islandf->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islandf->{'kei'}ヶ所</TD></TR>
</TABLE>
<td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>軍事技術NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idr}" \"alt="ID=${idr}">${HtagName_}$islandr->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">Ｌｖ$renae</TD></TR>
</TABLE>
</TABLE>
<br>
<TABLE ALIGN="center" width="100%">
<td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>ＨＣ通算勝率NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idhcr}" \"alt="ID=${idhcr}">${HtagName_}$islandhcr->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islandhcr->{'shoritu'}％($rstwint勝$rstloset敗$rstdrowt分)</TD></TR>
</TABLE>
<td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>ＨＣ優勝回数NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idhcy}" \"alt="ID=${idhcy}">${HtagName_}$islandhcy->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islandhcy->{'styusho'}回</TD></TR>
</TABLE>
<td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>サッカーチーム力NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idhct}" \"alt="ID=${idhct}">${HtagName_}$islandhct->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">合計$islandhct->{'teamforce'}pts.</TD></TR>
</TABLE>
<td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>鉄道NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idhckt}" \"alt="ID=${idhckt}">${HtagName_}$islandhckt->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islandhckt->{'etc0'}ｋｍ＋移動</TD></TR>
</TABLE>
<td width="9%"><TABLE BORDER=1 width="100%">
<TR><TD BGCOLOR="lightsteelblue" ALIGN="center" COLSPAN="2">
<FONT COLOR="#ffffff"><B>電力NO.1</B></FONT></TD></TR>
<TR><TD ALIGN="center"><A CLASS=\"type3\" HREF="${HthisFile}?Sight=${idhck}" \"alt="ID=${idhck}">${HtagName_}$islandhck->{'name'}島${H_tagName}</TD></TR>
<TR><TD ALIGN="center">$islandhck->{'ene'}万ｋＷ</TD></TR>
</TABLE>
</TABLE>
</table>

<SCRIPT Language="JavaScript">
<!--

function MM_displayStatusMsg(msgStr) {
    window.status=msgStr;
}

function Navi(jj, img, title, title2, text, exp) {
	StyElm = document.getElementById("NaviView");
	StyElm.style.visibility = "visible";

		    StyElm.style.marginLeft = 0;
		    StyElm.style.marginTop = -115+jj*102;

	    StyElm.innerHTML = "<table WIDTH=100%><tr><td class='M'><img class='NaviImg' src=" + img + "><\/td><td class='M'><div class='NaviText'><div class='NaviTitle'>" + title + " <\/div><hr>" + title2 + " <\/div><\/td><\/tr><\/table>";

}
function NaviClose() {
	StyElm = document.getElementById("NaviView");
	StyElm.style.visibility = "hidden";
}


//-->
</SCRIPT>

<hr>
<H1>${HtagHeader_}諸島の状況($first位〜$loopEnd位)${H_tagHeader}</H1>

<P>
島の名前をクリックすると、<B>観光</B>することができます。
</P>
END

	my($prev, $next, $nextCnt);
	if($viewFirst - $viewNumber < 0) {
	$prev = 0;
	} else {
	$prev = $viewFirst - $viewNumber;
	}
	if($viewFirst + $viewNumber >= $HislandNumber) {
	$next = -1;
	} else {
	$next = $viewFirst + $viewNumber;
	$nextCnt = $viewNumber;
	if($next + $nextCnt > $HislandNumber) {
	$nextCnt = $HislandNumber - $next;
	}
	}
	if($viewFlag ne 'ALL') { # "全島表示"されているときは使わない
	out("<FORM action=\"$HthisFile\" method=\"GET\">");
	if($next != $viewNumber) {out("<INPUT TYPE=\"submit\" VALUE=\"前の$viewNumber島\" NAME=\"view$prev\">");}
	if($next != -1) {out("<INPUT TYPE=\"submit\" VALUE=\"次の$nextCnt島\" NAME=\"view$next\">");}
	out("<INPUT TYPE=\"submit\" VALUE=\"全表示\" NAME=\"viewALL\">"); out("</form>"); }
	out(<<END);


<TABLE BORDER>
<TR>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}順位${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}島${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}人口${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}面積${H_tagTH}</NOBR></TH>
$mStr1
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}食料${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}農場${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}職場${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}採掘場${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}発電力${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}軍事技術${H_tagTH}</NOBR></TH>
</TR>
END

    my($island, $j, $farm, $factory, $mountain, $name, $id, $prize, $ii);
    my($pts);
    my($unemployed);
    my($rena);
    my($eis1, $eis2, $eis3);
    for($ii = $loopInit; $ii < $loopEnd; $ii++) {
	$j = $ii + 1;
	$island = $Hislands[$ii];

	$id = $island->{'id'};
	$farm = $island->{'farm'};

	$pop = $island->{'pop'};
	$factory = $island->{'factory'};
	$factory =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($factory1, $factory2, $co0, $co1, $htf, $shtf, $co95, $co95, $co95, $co95) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10);
	$factoryt = $factory1 + $factory2;
	$mountain = $island->{'mountain'};
	$rena = $island->{'rena'};
	$renae = int($rena / 10 ) + 1;
	$pts = $island->{'pts'};
	$eisei1 = $island->{'eisei1'};
	$eisei2 = $island->{'eisei2'};
	$eisei2nd = int($eisei2 / 100 );
	$monsterlive = $island->{'monsterlive'};
        $unemployed = ($island->{'pop'} - ($farm + $factoryt + $mountain) * 10) / $island->{'pop'} * 100;
        $unemployed = '<font color="' . ($unemployed < 0 ? 'royalblue' : 'red') . '">' . sprintf("%.2f%%", $unemployed) . '</font>';

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

	$farm = ($farm == 0) ? "保有せず" : "<p onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', 'black.gif', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">${farm}0$HunitPop</p>";
	$factoryt = ($factoryt == 0) ? "保有せず" : "<p onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', 'black.gif', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">${factoryt}0$HunitPop</p>";
	$mountain = ($mountain == 0) ? "保有せず" : "<p onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', 'black.gif', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">${mountain}0$HunitPop</p>";
        $HunitPts = 'pts.';
	$pts = ($pts == 0) ? "0" : "${pts}";
	$monsi = ($monsterlive == 0) ? "" : "${monsterlive}$HunitMonster";
	$monsm = ($monsterlive == 0) ? "" : "出現中！";
	$rieki = ($island->{'pika'} < 0) ? "$island->{'pika'}$HunitMoney" : "＋$island->{'pika'}$HunitMoney";
	$zouka = ($island->{'hamu'} < 0) ? "$island->{'hamu'}$HunitPop" : "＋$island->{'hamu'}$HunitPop";
	$seicho = ($island->{'monta'} < 0) ? "$island->{'monta'}pts." : "＋$island->{'monta'}pts.";
	$eisei2 = ($eisei2nd == 0) ? "通算観光者数１万人未満<br>" : "通算観光者数${eisei2nd}万人<br>";

	$hcturn = int($HislandTurn/100)*100;
	$acturn = (int($HislandTurn/100)+1)*100;

	if($island->{'absent'}  == 0) {
		$name = "${HtagName_}$island->{'name'}島${H_tagName}";
	} else {
	    $name = "${HtagName2_}$island->{'name'}島($island->{'absent'})${H_tagName2}";
	}

	$eisei6 = $island->{'eisei6'};
	$eisei6 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($unimika, $unishuto, $unimeka, $unioumu, $unianseki, $unitiseki, $unihyouseki, $unifuseki, $unienseki, $unikouseki, $uniiseki, $uniden) = ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12);
	$unimika2 = ($unimika == 0) ? "" : "[天使ミカエルor幸福の女神像]";
	$unishuto2 = ($unishuto == 0) ? "" : "[首都]";
	$unimeka2 = ($unimeka == 0) ? "" : "[壊れた侵略者]";
	$unioumu2 = ($unioumu == 0) ? "" : "[王蟲の脱け殻]";
	$unianseki2 = ($unianseki == 0) ? "" : "[闇石]";
	$unitiseki2 = ($unitiseki == 0) ? "" : "[地石]";
	$unihyouseki2 = ($unihyouseki == 0) ? "" : "[氷石]";
	$unifuseki2 = ($unifuseki == 0) ? "" : "[風石]";
	$unienseki2 = ($unienseki == 0) ? "" : "[炎石]";
	$unikouseki2 = ($unikouseki == 0) ? "" : "[光石]";
	$uniiseki2 = ($uniiseki == 0) ? "" : "[古代遺跡]";
	$uniden2 = ($uniden == 0) ? "" : "[天空城or魔塔]";
	$uniquesu = $unimika+$unishuto+$unimeka+$unioumu+$unianseki+$unitiseki+$unihyouseki+$unifuseki+$unienseki+$unikouseki+$uniiseki+$uniden;

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

	$alt = "ユニーク地形";
	$alt2 = "全12種類中$uni種類<br>$unishuto2$unimika2$uniiseki2$unimeka2$unioumu2$unienseki2$unihyouseki2$unitiseki2$unifuseki2$unikouseki2$unianseki2$uniden2";
	$alt3 = "<font color = red>Complete!!</font><br>$unishuto2$unimika2$uniiseki2$unimeka2$unioumu2$unienseki2$unihyouseki2$unitiseki2$unifuseki2$unikouseki2$unianseki2$uniden2";
	$image2 = 'prize11.gif';


	if ($unimika != 0 || $unishuto != 0 || $unimeka != 0 || $unioumu != 0 || $unianseki != 0 || $unitiseki != 0 || $unihyouseki != 0 || $unifuseki != 0 || $unienseki != 0 || $unikouseki != 0 || $uniiseki != 0 || $uniden != 0)
	    {$unique = "<IMG SRC=\"prize10.gif\" ALT=\"入手の難しいユニーク地形：$unishuto2$unimika2$uniiseki2$unimeka2$unioumu2$unienseki2$unihyouseki2$unitiseki2$unifuseki2$unikouseki2$unianseki2$uniden2／全12種類\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\"> $uniquesuヶ所 "};
	if ($unimika != 0 && $unishuto != 0 && $unimeka != 0 && $unioumu != 0 && $unianseki != 0 && $unitiseki != 0 && $unihyouseki != 0 && $unifuseki != 0 && $unienseki != 0 && $unikouseki != 0 && $uniiseki != 0 && $uniden != 0)
	    {$unique = "<IMG SRC=\"prize10.gif\" ALT=\"入手の難しいユニーク地形：$unishuto2$unimika2$uniiseki2$unimeka2$unioumu2$unienseki2$unihyouseki2$unitiseki2$unifuseki2$unikouseki2$unianseki2$uniden2／Complete!!\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt3'); Navi('$j', '$image2', '$alt', '$alt3', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\"> $uniquesuヶ所 "};
	if ($unimika == 0 && $unishuto == 0 && $unimeka == 0 && $unioumu == 0 && $unianseki == 0 && $unitiseki == 0 && $unihyouseki == 0 && $unifuseki == 0 && $unienseki == 0 && $unikouseki == 0 && $uniiseki == 0 && $uniden == 0)
	    {$unique = ""};


	$bumon = $island->{'bumon'};
	$bumonp = $island->{'bumonp'};
	$bumonfm = $island->{'bumonfm'};
	$bumonfc = $island->{'bumonfc'};
	$bumonm = $island->{'bumonm'};
	$bumonf = $island->{'bumonf'};
	$bumonl = $island->{'bumonl'};
	$bumonr = $island->{'bumonr'};
	$bumonk = $island->{'bumonk'};
	$bumonw = $island->{'bumonw'};
	$bumontare = $island->{'bumontare'};
	$bumonzipro = $island->{'bumonzipro'};
	$bumonleje = $island->{'bumonleje'};
	$bumonforce = $island->{'bumonforce'};
	$bumoneisei2 = $island->{'bumoneisei2'};
	$bumonuni = $island->{'bumonuni'};
	$bumonhck = $island->{'bumonhck'};
	$bumonhckt = $island->{'bumonhckt'};
	$bumonhcr = $island->{'bumonhcr'};
	$bumonhcy = $island->{'bumonhcy'};
	$bumonhct = $island->{'bumonhct'};
	$bumonp5 = ($bumonp == 0) ? "" : "[人口]";
	$bumonfm5 = ($bumonfm == 0) ? "" : "[農場]";
	$bumonfc5 = ($bumonfc == 0) ? "" : "[職場]";
	$bumonm5 = ($bumonm == 0) ? "" : "[採掘場]";
	$bumonw5 = ($bumonw == 0) ? "" : "[森林]";
	$bumontare5 = ($bumontare == 0) ? "" : "[にわとり数]";
	$bumonzipro5 = ($bumonzipro == 0) ? "" : "[ぶた数]";
	$bumonleje5 = ($bumonleje == 0) ? "" : "[うし数]";
	$bumonl5 = ($bumonl == 0) ? "" : "[怪獣出現＆捕獲数]";
	$bumonk5 = ($bumonk == 0) ? "" : "[怪獣退治数]";
	$bumonforce5 = ($bumonforce == 0) ? "" : "[生物大学能力]";
	$bumoneisei25 = ($bumoneisei2 == 0) ? "" : "[通算観光客]";
	$bumonuni5 = ($bumonuni == 0) ? "" : "[ユニーク地形数]";
	$bumonf5 = ($bumonf == 0) ? "" : "[記念碑数]";
	$bumonr5 = ($bumonr == 0) ? "" : "[軍事技術]";
	$bumonhck5 = ($bumonhck == 0) ? "" : "[電力]";
	$bumonhckt5 = ($bumonhckt == 0) ? "" : "[鉄道]";
	$bumonhcr5 = ($bumonhcr == 0) ? "" : "[ＨＣ通算勝率]";
	$bumonhcy5 = ($bumonhcy == 0) ? "" : "[ＨＣ優勝回数]";
	$bumonhct5 = ($bumonhct == 0) ? "" : "[サッカーチーム力]";

	$alt = "部門賞";
	$alt2 = "$bumonp5$bumonfm5$bumonfc5$bumonm5$bumonw5$bumontare5$bumonzipro5$bumonleje5$bumonl5$bumonk5$bumonforce5$bumoneisei25$bumonuni5$bumonf5$bumonr5$bumonhcr5$bumonhcy5$bumonhct5$bumonhckt5$bumonhck5";
	$image2 = 'prize11.gif';

	if ($bumon > 0)
	    {$bumons = "<IMG SRC=\"$image2\" ALT=\"$alt2\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\"> $bumon冠 "};
	if ($bumon == 0)
	    {$bumons = ""};


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
	my($mshurui) = 0;
	for($i = 0; $i < $HmonsterNumber; $i++) {
	    if($monsters & $f) {
		$mNameList .= "[$HmonsterName[$i]] ";
		$mshurui++;
		$max = $i;
	    }
	    $f *= 2;
	}

	$alt = "$mshurui種類$island->{'taiji'}$HunitMonster退治";
	$alt2 = "$mNameList";
	$image2 = "${HmonsterImage[$max]}";

	if($max != -1) {
	    $prize .= "<IMG SRC=\"${HmonsterImage[$max]}\" ALT=\"$mNameList\" WIDTH=16 HEIGHT=16 onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\"> $mshurui種類$island->{'taiji'}$HunitMonster";
	}


        # 出現中の怪獣リスト
        $f = 1;
        $max = -1;
        $mNameList = '';
	my($mshurui) = 0;
        my($monslivetype) = $island->{'monsterlivetype'};
        my($monsliveimg);
        for($i = 0; $i < $HmonsterNumber; $i++) {
            if($monslivetype & $f) {
                $mNameList .= "[$HmonsterName[$i]] ";
		$mshurui++;
                $max = $i;
            }
            $f *= 2;
        }

	$alt = "$mshurui種類${monsterlive}$HunitMonster$monsm";
	$alt2 = "$mNameList";
	$image2 = "${HmonsterImage[$max]}";

        if($max != -1) {
            $monsliveimg = "<IMG SRC=\"${HmonsterImage[$max]}\" ALT=\"$mNameList\" WIDTH=16 HEIGHT=16 onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\"> ";
        }

	$auc9 = $island->{'auc9'};
	$auc9 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($auc9a, $auc9b, $auc9c, $auc9d, $auc9e) = ($1, $2, $3, $4, $5);

	$auc9c2 = int($auc9c/10000);

	$alt = "へそくり";
	$alt2 = "貯金…$auc9b兆円<br>Auction補助金…$auc9c2兆円<hr>合計…$auc9a兆円";
	$image2 = 'auc.gif';

	if ($auc9a >= 1)
	    {$auchojo = "＋<IMG SRC=\"auc.gif\" ALT=\"へそくり\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">"};
	if ($auc9a == 0)
	    {$auchojo = ""};

	my($mStr1) = '';
	if($HhideMoneyMode == 1) {
	    $mStr1 = "<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>$island->{'money'}$HunitMoney</NOBR></TD>";
	} elsif($HhideMoneyMode == 2) {
	    my($mTmp) = aboutMoney($island->{'money'});
	    $mStr1 = "<TD $HbgPoinCell align=right nowrap=nowrap><NOBR>$mTmp$auchojo</NOBR></TD>";
	}

	$etc7 = $island->{'etc7'};
	$etc7 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
	($msjotai, $nokotan, $msid) = ($1, $2, $3);
	$HcurrentNumber = $HidToNumber{$msid};
	my($island) = $Hislands[$HcurrentNumber];
	$HcurrentName = $island->{'name'};

	$island = $Hislands[$ii];

#ここから追加
  my($oStr) = '';
  if($island->{'onm'} eq ''){
    $oStr = "<TD $HbgTotoCell COLSPAN=9 align=left nowrap=nowrap><NOBR>${HtagTH_}コメント : ${H_tagTH}$island->{'comment'}</NOBR></TD>";
  } elsif($msjotai == 1) {
    $oStr = "<TD $HbgTotoCell COLSPAN=9 align=left nowrap=nowrap><NOBR><font color=#0000ff>$island->{'onm'} : </font><font color=red><B>$HcurrentName島への援助射撃許可を申請中(残り$nokotanターン)</B></font></NOBR></TD>";
  } elsif($msjotai == 2) {
    $oStr = "<TD $HbgTotoCell COLSPAN=9 align=left nowrap=nowrap><NOBR><font color=#0000ff>$island->{'onm'} : </font><font color=seagreen><B>$HcurrentName島への援助射撃が可能(残り$nokotanターン)</B></font></NOBR></TD>";
  } else {
    $oStr = "<TD $HbgTotoCell COLSPAN=9 align=left nowrap=nowrap><NOBR><font color=#0000ff>$island->{'onm'} : </font>$island->{'comment'}</NOBR></TD>";
  }
#ここまで

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

	$eleinfo = "<IMG SRC=\"ele.gif\" ALT=\"使用状況(消費$shouhi万ｋＷ／過不足$sabun万ｋＷ)\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">$sabun2";
	$island->{'ene'} = $ene;


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
	    {$me_sat .= "<IMG SRC=\"cst.gif\" ALT=\"宇宙ステーション／$cstpop$HunitPop滞在\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">$csten%"};
	if ($eis1 == 0 && $eis2 == 0 && $eis3 == 0 && $eis4 == 0 && $eis5 == 0 && $eis6 == 0 && $eis7 == 0)
	    {$me_sat = ""};

	# 牧場系
	my($Farmcpc) = "";
	$tare = $island->{'tare'};
	$zipro = $island->{'zipro'};
	$leje = $island->{'leje'};

	$alt = "にわとり";
	$seisan = $tare*100;
	$urine = $tare*10;
	$alt2 = "$tare万羽<br>生産力$seisanトン<br>売値$urine$HunitMoney";
	$image2 = "niwatori.gif";
	if ($tare >= 1)
	    {$Farmcpc .= "<IMG SRC=\"niwatori.gif\" ALT=\"にわとり\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">$tare万羽"};

	$alt = "ぶた";
	$seisan = $zipro*200;
	$urine = $zipro*20;
	$alt2 = "$zipro万頭<br>生産力$seisanトン<br>売値$urine$HunitMoney";
	$image2 = "buta.gif";
	if ($zipro >= 1)
	    {$Farmcpc .= "<IMG SRC=\"buta.gif\" ALT=\"ぶた\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">$zipro万頭"};

	$alt = "うし";
	$seisan = $leje*300;
	$urine = $leje*50;
	$alt2 = "$leje万頭<br>生産力$seisanトン<br>売値$urine$HunitMoney";
	$image2 = "ushi.gif";
	if ($leje >= 1)
	    {$Farmcpc .= "<IMG SRC=\"ushi.gif\" ALT=\"うし\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">$leje万頭"};
	if ($tare == 0 && $zipro == 0 && $leje == 0)
	    {$Farmcpc = ""};

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
	    {$house .= "<IMG SRC=\"house${hlv}.gif\" ALT=\"$onm$n\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\"> "};
	if ($eisei1 == 0)
	    {$house = ""};

	$totoyoso2 = $island->{'totoyoso2'};
	if ($totoyoso2 == 0)
	    {$shutoname = "首都：$totoyoso2<br>"};
	if ($totoyoso2 == 555)
	    {$shutoname = ""};


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

	$alt = "$nn";
	$alt2 = "攻撃力($sto)<br>守備力($std)<br>キーパー能力($stk)<br>チーム成績(勝点$kachiten/$stwin勝$stlose敗$stdrow分/通算$stwint勝$stloset敗$stdrowt分/優勝$styusho回)";
	$image2 = 'sc.gif';

	if ($stshoka >= 1)
	    {$ssss = "<IMG SRC=\"sc.gif\" ALT=\"$nn(攻($sto)守($std)KP($stk)チーム成績(勝点$kachiten/$stwin勝$stlose敗$stdrow分/通算$stwint勝$stloset敗$stdrowt分/優勝$styusho回)\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\"> "};
	if ($stshoka == 0)
	    {$ssss = ""};


	$eisei5 = $island->{'eisei5'};
	$eisei5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($mshp, $msap, $msdp, $mssp, $mswin, $msexe, $tet) = ($1, $2, $3, $4, $5, $6, $7);
	$force = $mshp+$msap+$msdp+$mssp;

	$alt = "マスコットいのら";
	$alt2 = "HP $mshp　AP $msap<br>DP $msdp　SP $mssp<br>$mswin匹撃破<br>経験値$msexe";
	$image2 = 'ms.gif';
	$alt3 = "超神獣テトラ";
	$alt4 = "HP $mshp　AP $msap<br>DP $msdp　SP $mssp<br>$mswin匹撃破<br>経験値$msexe";
	$image3 = 'tet.gif';


	if ($mshp >= 1)
	    {$mspet = "<IMG SRC=\"ms.gif\" ALT=\"マスコットいのら(HP$mshp.AP$msap.DP$msdp.SP$mssp/$mswin匹撃破/経験値$msexe)\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">Sum($force)"};
	if ($tet >= 1)
	    {$mspet = "<IMG SRC=\"tet.gif\" ALT=\"超神獣テトラ(HP$mshp.AP$msap.DP$msdp.SP$mssp/$mswin匹撃破/経験値$msexe)\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt3/$alt4'); Navi('$j', '$image3', '$alt3', '$alt4', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">Sum($force)"};
	if ($mshp == 0 && $tet == 0)
	    {$mspet = ""};


	$etc8 = $island->{'etc8'};
	$etc8 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($toto1, $toto2, $toto3, $toto4, $toto5, $toto6, $toto7) = ($1, $2, $3, $4, $5, $6, $7);

	$alt = "お守り";
	$alt2 = "toto的中回数…$toto1回<br>お守り残数…$toto2個";
	$image2 = 'omamori.gif';

	if ($toto1 >= 1)
	    {$omamori = "<IMG SRC=\"omamori.gif\" ALT=\"toto的中回数($toto1)/お守り残数($toto2)\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">残り($toto2)"};
	if ($toto1 == 0)
	    {$omamori = ""};
	if ($toto2 >= 1)
	    {$omamori = "<IMG SRC=\"omamori.gif\" ALT=\"toto的中回数($toto1)/お守り残数($toto2)\" WIDTH=16 HEIGHT=\"16\" onMouseOver=\"MM_displayStatusMsg('$alt/$alt2'); Navi('$j', '$image2', '$alt', '$alt2', '$NaviText', ''); return true\" onMouseOut=\"MM_displayStatusMsg(''); NaviClose(); return false\">残り($toto2)"};

	out(<<END);

<TR>
<TD $HbgNumberCell ROWSPAN=4 align=center nowrap=nowrap HEIGHT=100><NOBR>${HtagNumber_}$j${H_tagNumber}</NOBR></TD>
<TD $HbgNameCell ROWSPAN=4 valign="middle" align="left" nowrap=nowrap>
<div id=\"NaviView\"></div>
<center>
<NOBR>
<A CLASS=\"type3\" HREF="${HthisFile}?Sight=${id}" \"alt="ID=${id}">
$name
</A>
<br>
<font color="MEDIUMSEAGREEN" font size="-1">$shutoname</font>
<NOBR>ID:(<font color="SALMON"><B>$id</B></font>) <font color="royalblue">$pts</font>$HunitPts</NOBR><br>
<NOBR><font size="-1">失業率</font>:($unemployed)</NOBR><br>
<NOBR><font color="lightseagreen" font size="-1">$eisei2</font></NOBR>
<NOBR><font color="hotpink" font size="-2">(前ターン$seicho$zouka$rieki)</font></NOBR>
</center>
</TD>
<TD $HbgPoinCell align=right nowrap=nowrap><NOBR>$island->{'pop'}$HunitPop</NOBR></TD>
<TD $HbgPoinCell align=right nowrap=nowrap><NOBR>$island->{'area'}$HunitArea</NOBR></TD>
$mStr1
<TD $HbgPoinCell align=right nowrap=nowrap><NOBR>$island->{'food'}$HunitFood</NOBR></TD>
<TD $HbgPoinCell align=right nowrap=nowrap><NOBR>$farm</NOBR></TD>
<TD $HbgPoinCell align=right nowrap=nowrap><NOBR>$factoryt</NOBR></TD>
<TD $HbgPoinCell align=right nowrap=nowrap><NOBR>$mountain</NOBR></TD>
<TD $HbgPoinCell align=right nowrap=nowrap><NOBR>$ene万ｋＷ</NOBR></TD>
<TD $HbgPoinCell align=right nowrap=nowrap><NOBR>Ｌｖ$renae</NOBR></TD>
</TR>
<TR>
<TD $HbgCommentCell COLSPAN=9 align=left nowrap=nowrap><NOBR>${HtagtTH_}　info：<font size="-1">$ssss<font color="MEDIUMSEAGREEN">$unique</font><font color="SALMON">$house</font>$monsliveimg<font color="hotpink">$monsm</font>$mspet$Farmcpc$me_sat</font>$eleinfo</NOBR></TD>
</TR>

<TR>
<TD $HbgCommentCell COLSPAN=5 align=left nowrap=nowrap><NOBR>${HtagtTH_}Prize：<font size="-1">$bumons$prize$omamori</font></NOBR></TD>
<TD $HbgTotoCell COLSPAN=4 align=left nowrap=nowrap><NOBR><font size="-1">${HtagtTH_}予想１：${H_tagtTH}$island->{'eis8'}</font></NOBR></TD>
</TR>
<TR>
$oStr
</TR>

END
    }

    out(<<END);

</TABLE>

<HR>
<H1>${HtagHeader_}新しい島を探す${H_tagHeader}</H1>
END

    if($HislandNumber < $HmaxIsland) {
	out(<<END);
<FORM action="$HthisFile" method="POST">
どんな名前をつける予定？<BR>
<INPUT TYPE="text" NAME="ISLANDNAME" SIZE=32 MAXLENGTH=32>島<BR>
オーナー名は？<BR>
<INPUT TYPE="text" NAME="OWNERNAME" SIZE=32 MAXLENGTH=32><BR>
パスワードは？<BR>
<INPUT TYPE="password" NAME="PASSWORD" SIZE=32 MAXLENGTH=32><BR>
念のためパスワードをもう一回<BR>
<INPUT TYPE="password" NAME="PASSWORD2" SIZE=32 MAXLENGTH=32><BR>
参加にあたっての意気込み<BR>
<INPUT TYPE=text NAME=MESSAGE SIZE=80><BR>
<INPUT TYPE="submit" VALUE="探しに行く" NAME="NewIslandButton">
</FORM>
END
    } else {
	out(<<END);
        Biglobeじゃ限界だー（＞、＜）・・・現在登録できません。
END
    }

    out(<<END);
<HR>
<H1>${HtagHeader_}島の名前とパスワードの変更${H_tagHeader}</H1>
<P>
(注意)名前の変更には$HcostChangeName${HunitMoney}かかります。
</P>
<FORM action="$HthisFile" method="POST">
どの島ですか？<BR>
<SELECT NAME="ISLANDID">
$HislandList
</SELECT>
<BR>
どんな名前に変えますか？(変更する場合のみ)<BR>
<INPUT TYPE="text" NAME="ISLANDNAME" SIZE=32 MAXLENGTH=32>島<BR>
オーナー名は？(変更する場合のみ)<BR>
<INPUT TYPE="text" NAME="OWNERNAME" SIZE=32 MAXLENGTH=32><BR>
パスワードは？(必須)<BR>
<INPUT TYPE="password" NAME="OLDPASS" SIZE=32 MAXLENGTH=32><BR>
新しいパスワードは？(変更する時のみ)<BR>
<INPUT TYPE="password" NAME="PASSWORD" SIZE=32 MAXLENGTH=32><BR>
念のためパスワードをもう一回(変更する時のみ)<BR>
<INPUT TYPE="password" NAME="PASSWORD2" SIZE=32 MAXLENGTH=32><BR>

<INPUT TYPE="submit" VALUE="変更する" NAME="ChangeInfoButton">
<INPUT TYPE="submit" VALUE="(・∀・)" NAME="IPInfoButton">
</FORM>


END
my($Himfflag);
if($HimgLine eq '' || $HimgLine eq $imageDir){
    $Himfflag = '<FONT COLOR=RED>未設定</FONT>';
} else {
    $Himfflag = $HimgLine;
}

   out(<<END);
</TD>

<TD VALIGN=TOP WIDTH=350>
<H1>${HtagHeader_}画像のローカル設定${H_tagHeader}</H1>
現在の設定<B>[</b> ${Himfflag} <B>]</B>
　　<A CLASS=\"type3\" HREF=${imageExp} target=_BLANK><FONT SIZE=+1> 説 明 </FONT></A>
<form action=$HthisFile method=POST>
<INPUT TYPE=file NAME="IMGLINE">
<INPUT TYPE="submit" VALUE="設定" name=IMGSET>
</form>

<form action=$HthisFile method=POST>
Macユーザー用<BR>
<INPUT TYPE=text NAME="IMGLINEMAC">
<INPUT TYPE="submit" VALUE="設定" name=IMGSET><BR>
<FONT SIZE=-1>Macの方は、こちらを使用して下さい。</FONT>
</form>
</TD></TR>

<TR HEIGHT=100><TD ALIGN=CENTER>
<form action=$HthisFile method=POST>
<INPUT TYPE=hidden NAME="IMGLINE" value="deletemodenow">
<INPUT TYPE="submit" VALUE="設定を解除する" name=IMGSET>
</form>
</TD></TR>
</TABLE>
<HR>


<H1>${HtagHeader_}Hakoniwa Auction$acturn${H_tagHeader}</H1>

<TABLE BORDER>

<TR>
<TD><NOBR>



<TABLE border="0" cellpadding="0" cellspacing="0" width=100%>
<TR>
<TD>

<TABLE border="1" cellpadding="1" cellspacing="1" width=100%>
<TR>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}順位${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell COLSPAN=2 align=center nowrap=nowrap><NOBR><B>１．<font color="MEDIUMSEAGREEN">$ac1</font></B>$acjo1</NOBR></TH>
</TR>
END

    islandSortac1();

    my($island, $ii, $j);
    for($ii = 0; $ii < 5; $ii++) {
	$j = $ii + 1;
	$island = $Hislands[$ii];

	$id = $island->{'id'};
	$name = "？？？";
	$auc1 = $island->{'auc1'};

	$auc1 = ($auc1 == 0) ? "−" : "$auc1兆円";
	$name = ($auc1 == 0) ? "−" : "$name島";

    out(<<END);

<TR>
<TD $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagNumber_}$j${H_tagNumber}</NOBR></TD>
<TD $HbgNameCell align=center nowrap=nowrap><NOBR>${HtagName_}$name${H_tagName}</NOBR></TD>
<TD $HbgPoinCell align=center nowrap=nowrap><NOBR>${HtagTH_}<font color="black">$auc1</font>${H_tagTH}</NOBR></TD>
</TR>
END

    }
    out(<<END);

</TABLE>
</TD>

<TD>
<TABLE border="1" cellpadding="1" cellspacing="1" width=100%>
<TR>
<TH $HbgTitleCell COLSPAN=2 align=center nowrap=nowrap><NOBR><B>２．<font color="MEDIUMSEAGREEN">$ac2</font></B>$acjo2</NOBR></TH>
</TR>
END

    islandSortac2();

    my($island, $ii, $j);
    for($ii = 0; $ii < 5; $ii++) {
	$j = $ii + 1;
	$island = $Hislands[$ii];

	$id = $island->{'id'};
	$name = "？？？";
	$auc2 = $island->{'auc2'};

	$auc2 = ($auc2 == 0) ? "−" : "$auc2兆円";
	$name = ($auc2 == 0) ? "−" : "$name島";

    out(<<END);

<TR>
<TD $HbgNameCell align=center nowrap=nowrap><NOBR>${HtagName_}$name${H_tagName}</NOBR></TD>
<TD $HbgPoinCell align=center nowrap=nowrap><NOBR>${HtagTH_}<font color="black">$auc2</font>${H_tagTH}</NOBR></TD>
</TR>
END

    }
    out(<<END);

</TABLE>
</TD>

<TD>
<TABLE border="1" cellpadding="1" cellspacing="1" width=100%>
<TR>
<TH $HbgTitleCell COLSPAN=2 align=center nowrap=nowrap><NOBR><B>３．<font color="MEDIUMSEAGREEN">$ac3</font></B>$acjo3</NOBR></TH>
</TR>
END

    islandSortac3();

    my($island, $ii, $j);
    for($ii = 0; $ii < 5; $ii++) {
	$j = $ii + 1;
	$island = $Hislands[$ii];

	$id = $island->{'id'};
	$name = "？？？";
	$auc3 = $island->{'auc3'};

	$auc3 = ($auc3 == 0) ? "−" : "$auc3兆円";
	$name = ($auc3 == 0) ? "−" : "$name島";

    out(<<END);

<TR>
<TD $HbgNameCell align=center nowrap=nowrap><NOBR>${HtagName_}$name${H_tagName}</NOBR></TD>
<TD $HbgPoinCell align=center nowrap=nowrap><NOBR>${HtagTH_}<font color="black">$auc3</font>${H_tagTH}</NOBR></TD>
</TR>
END

    }
    out(<<END);

</TABLE>
</TD>

</TR>
</TABLE>



</NOBR></TD>
</TR>



<TR>
<TD>
<TABLE border="0" cellpadding="0" cellspacing="0">
<TR>
<TD>
<TABLE border="1" cellpadding="1" cellspacing="1">
<TR>
<TH $HbgPoinCell COLSPAN=6 align=center nowrap=nowrap><NOBR><B><font color="royalblue">高額落札ランキング</font></B></NOBR></TH>
</TR>
<TR>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}順位${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}落札価格${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}落札島名${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}落札品名${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}セクション${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}ボーナス${H_tagTH}</NOBR></TH>
</TR>
END

    islandSortac4();

    my($island, $ii, $j);
	$aa = $HislandNumber;
	    if($aa > 10) {
		$aa = 10;
	    }
    for($ii = 0; $ii < $aa; $ii++) {
	$j = $ii + 1;
	$island = $Hislands[$ii];

	$islandat = $Hislands[0];
	$nameat = $islandat->{'name'};
	$auc4 = $islandat->{'auc4'};
	$auc4 =~ /^([0-9]*),([0-9]*),([0-9]*)$/;
	($auc4a, $auc4b, $auc4c) = ($1, $2, $3);

	$id = $island->{'id'};
	$name = $island->{'name'};
	$auc0 = $island->{'auc0'};
	$auc0 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($auc0a, $auc0b, $auc0c, $auc0d, $auc0e) = ($1, $2, $3, $4, $5);

	if(($auc0c != 0) || ($j == 1)) {

	$auc0c = ($auc0c == 0) ? "−" : "$auc0c兆円";
	$auc0d = ($auc0c == 0) ? "−" : "$auc0d";
	$name = ($auc0c == 0) ? "−" : "$name島";

	if($auc0a == 0) {
	    $ac4 = '−';
	} elsif($auc0a == 1) {
	    $ac4 = '地石';
	} elsif($auc0a == 2) {
	    $ac4 = '氷石';
	} elsif($auc0a == 3) {
	    $ac4 = '風石';
	} elsif($auc0a == 4) {
	    $ac4 = '炎石';
	} elsif($auc0a == 5) {
	    $ac4 = '光石';
	} elsif($auc0a == 6) {
	    $ac4 = '天使ミカエル';
	} elsif($auc0a == 7) {
	    $ac4 = 'アイススコーピオン';
	} elsif($auc0a == 8) {
	    $ac4 = 'スライムレジェンド';
	} elsif($auc0a == 9) {
	    $ac4 = "お守り$auc0b個";
	} elsif($auc0a == 10) {
	    $auc0b = $auc0b * 1000;
	    $ac4 = "海あみゅ$auc0b人規模";
	} elsif($auc0a == 11) {
	    $auc0b = $auc0b * 1000;
	    $ac4 = "食研$auc0b人規模";
	} elsif($auc0a == 12) {
	    $ac4 = "コスモ$auc0b万ｋＷ";
	} elsif($auc0a == 13) {
	    $ac4 = '闇石';
	} elsif($auc0a == 14) {
	    $ac4 = '衛星６種';
	} elsif($auc0a == 15) {
	    $ac4 = '宇宙ステーション';
	} elsif($auc0a == 16) {
	    $ac4 = '黄金のコンデンサ';
	} elsif($auc0a == 17) {
	    $auc0b = $auc0b * 1000;
	    $ac4 = "金山$auc0b人規模";
	} elsif($auc0a == 18) {
	    $auc0b = $auc0b * 1000;
	    $ac4 = "養殖場$auc0b人規模";
	} elsif($auc0a == 19) {
	    $ac4 = '人造怪獣f02';
	} elsif($auc0a == 20) {
	    $ac4 = '魔王サタン';
	} elsif($auc0a == 21) {
	    $ac4 = 'unknown';
	} elsif($auc0a == 22) {
	    $ac4 = "サッカーチーム力1.$auc0b倍";
	} elsif($auc0a == 23) {
	    $ac4 = "生物大学能力1.$auc0b倍";
	} elsif($auc0a == 24) {
	    $ac4 = "生物大学経験値$auc0b";
	} elsif($auc0a == 25) {
	    $ac4 = '卵';
	} elsif($auc0a == 26) {
	    $ac4 = '生物大学';
	} elsif($auc0a == 27) {
	    $ac4 = "風力$auc0b万ｋＷ";
	} elsif($auc0a == 28) {
	    $ac4 = "バイオマス$auc0b万ｋＷ";
	} elsif($auc0a == 29) {
	    $ac4 = '今回はお休み';
	} elsif($auc0a == 30) {
	    $ac4 = "$island->{'auc8'}";
	} else {
	    $ac4 = '？';
	}

	$auc0e = (11-$auc0e)*500;

	$auc0e = ($auc0c == 0) ? "−" : "+<font color=\"red\">$auc0e</font>pts.";

    out(<<END);

<TR>
<TD $HbgNumberCell align=center nowrap=nowrap><NOBR>${HtagNumber_}$j${H_tagNumber}</NOBR></TD>
<TD $HbgPoinCell align=center nowrap=nowrap><NOBR>${HtagTH_}<font color="black">$auc0c</font>${H_tagTH}</NOBR></TD>
<TD $HbgNameCell align=center nowrap=nowrap><NOBR>${HtagName_}$name${H_tagName}</NOBR></TD>
<TD $HbgTotoCell align=center nowrap=nowrap><NOBR>${HtagName_}<font color="MEDIUMSEAGREEN">$ac4</font>${H_tagName}</NOBR></TD>
<TD $HbgTotoCell align=center nowrap=nowrap><NOBR>${HtagName_}<font color="black">$auc0d</font>${H_tagName}</NOBR></TD>
<TD $HbgTotoCell align=center nowrap=nowrap><NOBR>${HtagName_}$auc0e${H_tagName}</NOBR></TD>
</TR>
END

    }
    }
    out(<<END);

</TABLE>
</TD>
<TD width=100% align=center>

<TABLE border="0" cellpadding="5" cellspacing="0" width=100%>
<TR>
<TD width=100% align=center>
<font color="royalblue"><b>高額落札ランキング１位</b></font>
<br>${HtagName_}$nameat島${H_tagName}
<br>１位（$auc4a回）賞品まで（$auc4b/$aucshouhin）
</TD>
</TR>
<TR>
<TD width=100% align=center>
<font color="hotpink">$aucshouhin連続ランキング１位の賞品を<br>
$aucdendou回もらうと殿堂入りとなります。</font>
</TD>
</TR>
</TABLE>

</TD>
</TR>
</TABLE>
</TD>
</TR>




<TR>
<TD>
<TABLE border="0" cellpadding="0" cellspacing="0" width=100%>
<TR>
<TD>
<TABLE border="1" cellpadding="1" cellspacing="1" width=100%>
<TR>
<TH $HbgPoinCell COLSPAN=6 align=center nowrap=nowrap><NOBR><B><font color="royalblue">殿堂入り</font></B></NOBR></TH>
</TR>
<TR>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}順位${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}落札価格${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}落札島名${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}落札品名${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}セクション${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}１位保守回数${H_tagTH}</NOBR></TH>
</TR>
END

    islandSortac5();

    my($island, $ii, $j);
	$aa = $HislandNumber;
	    if($aa > 5) {
		$aa = 5;
	    }
    for($ii = 0; $ii < $aa; $ii++) {
	$j = $ii + 1;
	$island = $Hislands[$ii];

	$id = $island->{'id'};
	$name = $island->{'name'};
	$auc5 = $island->{'auc5'};
	$auc5 =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	($auc5a, $auc5b, $auc5c, $auc5d, $auc5e) = ($1, $2, $3, $4, $5);

	if(($auc5c != 0) || ($j == 1)) {

	$auc5c = ($auc5c == 0) ? "−" : "$auc5c兆円";
	$auc5d = ($auc5c == 0) ? "−" : "$auc5d";
	$auc5e = ($auc5c == 0) ? "−" : "$auc5e回";
	$name = ($auc5c == 0) ? "−" : "$name島";

	if($auc5a == 0) {
	    $ac4 = '−';
	} elsif($auc5a == 1) {
	    $ac4 = '地石';
	} elsif($auc5a == 2) {
	    $ac4 = '氷石';
	} elsif($auc5a == 3) {
	    $ac4 = '風石';
	} elsif($auc5a == 4) {
	    $ac4 = '炎石';
	} elsif($auc5a == 5) {
	    $ac4 = '光石';
	} elsif($auc5a == 6) {
	    $ac4 = '天使ミカエル';
	} elsif($auc5a == 7) {
	    $ac4 = 'アイススコーピオン';
	} elsif($auc5a == 8) {
	    $ac4 = 'スライムレジェンド';
	} elsif($auc5a == 9) {
	    $ac4 = "お守り$auc5b個";
	} elsif($auc5a == 10) {
	    $auc5b = $auc5b * 1000;
	    $ac4 = "海あみゅ$auc5b人規模";
	} elsif($auc5a == 11) {
	    $auc5b = $auc5b * 1000;
	    $ac4 = "食研$auc5b人規模";
	} elsif($auc5a == 12) {
	    $ac4 = "コスモ$auc5b万ｋＷ";
	} elsif($auc5a == 13) {
	    $ac4 = '闇石';
	} elsif($auc5a == 14) {
	    $ac4 = '衛星６種';
	} elsif($auc5a == 15) {
	    $ac4 = '宇宙ステーション';
	} elsif($auc5a == 16) {
	    $ac4 = '黄金のコンデンサ';
	} elsif($auc5a == 17) {
	    $auc5b = $auc5b * 1000;
	    $ac4 = "金山$auc5b人規模";
	} elsif($auc5a == 18) {
	    $auc5b = $auc5b * 1000;
	    $ac4 = "養殖場$auc5b人規模";
	} elsif($auc5a == 19) {
	    $ac4 = '人造怪獣f02';
	} elsif($auc5a == 20) {
	    $ac4 = '魔王サタン';
	} elsif($auc5a == 21) {
	    $ac4 = 'unknown';
	} elsif($auc5a == 22) {
	    $ac4 = "サッカーチーム力1.$auc5b倍";
	} elsif($auc5a == 23) {
	    $ac4 = "生物大学能力1.$auc5b倍";
	} elsif($auc5a == 24) {
	    $ac4 = "生物大学経験値$auc5b";
	} elsif($auc5a == 25) {
	    $ac4 = '卵';
	} elsif($auc5a == 26) {
	    $ac4 = '生物大学';
	} elsif($auc5a == 27) {
	    $ac4 = "風力$auc5b万ｋＷ";
	} elsif($auc5a == 28) {
	    $ac4 = "バイオマス$auc5b万ｋＷ";
	} elsif($auc5a == 29) {
	    $ac4 = '今回はお休み';
	} elsif($auc5a == 30) {
	    $ac4 = "$island->{'auc8'}";
	} else {
	    $ac4 = '？';
	}

    out(<<END);

<TR>
<TD $HbgNumberCell align=center nowrap=nowrap><NOBR>${HtagNumber_}$j${H_tagNumber}</NOBR></TD>
<TD $HbgPoinCell align=center nowrap=nowrap><NOBR>${HtagTH_}<font color="black">$auc5c</font>${H_tagTH}</NOBR></TD>
<TD $HbgNameCell align=center nowrap=nowrap><NOBR>${HtagName_}$name${H_tagName}</NOBR></TD>
<TD $HbgTotoCell align=center nowrap=nowrap><NOBR>${HtagName_}<font color="MEDIUMSEAGREEN">$ac4</font>${H_tagName}</NOBR></TD>
<TD $HbgTotoCell align=center nowrap=nowrap><NOBR>${HtagName_}<font color="black">$auc5d</font>${H_tagName}</NOBR></TD>
<TD $HbgTotoCell align=center nowrap=nowrap><NOBR>${HtagName_}$auc5e${H_tagName}</NOBR></TD>
</TR>
END

    }
    }
    out(<<END);

</TABLE>
</TD>
</TR>
</TABLE>
</TD>
</TR>





<TR>
<TD width=100%><font color="red" size="+1">(注)品番３は21位以下の島のみ入札可能です。</font><br><NOBR>
END
    aucPrint();
    out(<<END);
</NOBR></TD>
</TR>

</TABLE>

<H1>${HtagHeader_}Hakoniwa Cup$hcturn${H_tagHeader}</H1>
END
    hcPrint();
    out(<<END);
<H1>${HtagHeader_}最近の出来事${H_tagHeader}</H1>
END
    logPrintTop();
    out(<<END);
<H1>${HtagHeader_}発見の記録${H_tagHeader}</H1>
END
    historyPrint();
}

# トップページ用ログ表示
sub logPrintTop {
    my($i);
    for($i = 0; $i < $HtopLogTurn; $i++) {
	logFilePrint($i, 0, 0);
    }
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
sub islandSortArea {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'area'} <=> $Hislands[$a]->{'area'} || $a <=> $b } @idx;
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
sub islandSortPika {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'pika'} <=> $Hislands[$a]->{'pika'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}
sub islandSortHamu {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'hamu'} <=> $Hislands[$a]->{'hamu'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}
sub islandSortMonta {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'monta'} <=> $Hislands[$a]->{'monta'} || $a <=> $b } @idx;
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

sub islandSortac1 {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'auc1'} <=> $Hislands[$a]->{'auc1'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}

sub islandSortac2 {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'auc2'} <=> $Hislands[$a]->{'auc2'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}

sub islandSortac3 {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'auc3'} <=> $Hislands[$a]->{'auc3'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}

sub islandSortac4 {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'auc0c'} <=> $Hislands[$a]->{'auc0c'} || $a <=> $b } @idx;
@Hislands = @Hislands[@idx];
}

sub islandSortac5 {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'auc5c'} <=> $Hislands[$a]->{'auc5c'} || $a <=> $b } @idx;
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

# 記録ファイル表示
sub historyPrint {
    open(HIN, "${HdirName}/hakojima.his");
    my(@line, $l);
    while($l = <HIN>) {
	chomp($l);
	push(@line, $l);
    }
    @line = reverse(@line);

    foreach $l (@line) {
	$l =~ /^([0-9]*),(.*)$/;
	out("<NOBR>${HtagNumber_}ターン${1}${H_tagNumber}：${2}</NOBR><BR>\n");
    }
    close(HIN);
}

# Hakoniwa Cupログ表示
sub hcPrint {
    open(CIN, "${HdirName}/hakojima.lhc");
    my(@line, $l);
    while($l = <CIN>) {
	chomp($l);
	push(@line, $l);
    }
    @line = reverse(@line);

    foreach $l (@line) {
	$l =~ /^([0-9]*),(.*)$/;
	out("<NOBR>${HtagNumber_}ターン${1}${H_tagNumber}：${2}</NOBR><BR>\n");
    }
    close(CIN);
}

# Hakoniwa Auctionログ表示
sub aucPrint {
    open(AIN, "${HdirName}/hakojima.auc");
    my(@line, $l);
    while($l = <AIN>) {
	chomp($l);
	push(@line, $l);
    }
    @line = reverse(@line);

    foreach $l (@line) {
	$l =~ /^([0-9]*),(.*)$/;
	out("<NOBR>${2}</NOBR><BR>\n");
    }
    close(AIN);
}

1;

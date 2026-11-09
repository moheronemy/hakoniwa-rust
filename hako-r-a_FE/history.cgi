#!/usr/bin/perl

#---------------------------------------------------------------------
#	
#	究想の箱庭　最近の出来事と最近の天気の履歴を表示
#
#	作成日 : 20001/11/25 (ver0.10)
#	作成者 : ラスティア <nayupon@mail.goo.ne.jp>
#
#---------------------------------------------------------------------

#---------------------------------------------------------------------
#	初期設定
#---------------------------------------------------------------------
# jcode.plをrequire
require './jcode.pl';

# ログデータディレクトリの名前
$HlogdirName = 'data';

# 表示するログのターン数(hako-main.cgiのログファイル保持ターン数より多く出来ません。)
$HtopLogTurn = 6;

#----------------------------
#	HTMLに関する設定
#----------------------------
# ブラウザのタイトルバーの名称
$title = '最近の出来事';

# 画面の色や背景の設定(HTML)
$body = '<body bgcolor=lemonchiffon>';

# 画面の「戻る」リンク先(URL)
$bye = 'http:/www.xxxxxx/cgi-bin/hako-main.cgi';

# H1タグ用
$HtagHeader_ = '<FONT COLOR="#4444ff">';
$H_tagHeader = '</FONT>';

# 順位の番号など
$HtagNumber_ = '<FONT COLOR="#800000"><B>';
$H_tagNumber = '</B></FONT>';

#メインルーチン-------------------------------------------------------

&cgiInput;
&tempHeader;

if($HMode == 100) {
	# 天気
	&logTenki;
} elsif($HMode =~ /([0-9]*)/) {
	if($HMode == 99) {
		&logFilePrintAll;
	} else {
		&logFilePrint($HMode, $HcurrentID);
	}
} else {
	# 天気
	&logTenki;
}

&tempFooter;
#終了
exit(0);

#サブルーチン---------------------------------------------------------
#--------------------------------------------------------------------
#	POST or GETで入力されたデータ取得
#--------------------------------------------------------------------
sub cgiInput {
  my($line, $getLine);

  # 入力を受け取って日本語コードをEUCに
  $line = <>;
  $line =~ tr/+/ /;
  $line =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  $line = jcode::euc($line);
  $line =~ s/[\,\r]//g;

  # GETのやつも受け取る
  $getLine = $ENV{'QUERY_STRING'};

  if($getLine =~ /tenki/){
	$HMode = 100;
  } elsif($getLine =~ /saikin=([0-9]*)/){
	$HMode = $1;

	if($getLine =~ /id=([0-9]*)/){
	$HcurrentID = $1;
	}

  } else {
	$HMode = 100;
  }
}
#---------------------------------------------------------------------
#	HTMLのヘッダとフッタ部分を出力
#---------------------------------------------------------------------
# ヘッダ
sub tempHeader {
	print qq{Content-type: text/html; charset=Shift_JIS\n\n};
	print qq{<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">\n\n};
	out(<<END);
<HTML>
<HEAD>
<TITLE>
$title
</TITLE>
</HEAD>
$body
[最近の出来事]
END
	my $i;
	for($i = 0;$i < $HtopLogTurn;$i++) {
		out("<A HREF='history.cgi?saikin=${i}'>[${i}]</A>\n");
	}
	out(<<END);


[各島の近況]
END


	my $id;
	$id = $HcurrentID;
		if($id != 0) {
		my $i;
		for($i = 0;$i < $HtopLogTurn;$i++) {
			out("<A HREF='history.cgi?saikin=${i}&id=${id}'>[${i}]</A>\n");
		}
		}

	out(<<END);
<br>
<br>
END
}
# フッタ
sub tempFooter {
	out(<<END);
</BODY>
</HTML>
END
}
#---------------------------------------------------------------------
#	ログファイルタイトル
#---------------------------------------------------------------------
sub logDekigoto {
	out(<<END);
<H1>${HtagHeader_}最近の出来事${H_tagHeader}</H1>
END
}
#---------------------------------------------------------------------
#	ログファイル全て表示
#---------------------------------------------------------------------
#---------------------------------------------------------------------
#	ファイル番号指定でログ表示
#---------------------------------------------------------------------
sub logFilePrint {
	my($fileNumber, $id) = @_;
	
	open(LIN, "${HlogdirName}/hakojima.log$_[0]");
	my($line, $m, $turn, $id1, $id2, $message);
	while($line = <LIN>) {
		$line =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),(.*)$/;
		($m, $turn, $id1, $id2, $message) = ($1, $2, $3, $4, $5);

		# 機密関係
		if($m == 1) {
			next;
		} else {
			$m = '';
		}

		if($id != 0) {
		    if(($id != $id1) &&
		       ($id != $id2)) {
			next;
		    }
		}

		# 表示
		out("<NOBR>${HtagNumber_}ターン$turn$m${H_tagNumber}：$message</NOBR><BR>\n");
	}
	close(LIN);
}
#---------------------------------------------------------------------
#	文字コードをshift jisで標準出力にアウトプット
#---------------------------------------------------------------------
sub out {
  print STDOUT jcode::sjis($_[0]);
}


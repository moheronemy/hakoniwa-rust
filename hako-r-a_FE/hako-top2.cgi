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
# ＩＰチェック用の改造版。情報変更の項目にマスターパスワードを入力し
# 顔文字をクリックすると裏ランキングが見れます。
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

# トップページ
sub tempTopPage {
    # タイトル
    out(<<END);
${HtagTitle_}$Htitle${H_tagTitle}（裏ランキング）
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
    out(<<END);
<H1>${HtagHeader_}ターン$HislandTurn${H_tagHeader}</H1>

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
    my($island, $j, $farm, $factory, $mountain, $name, $id, $prize, $ii);
    for($ii = 0; $ii < $HislandNumber; $ii++) {
	$j = $ii + 1;
	$island = $Hislands[$ii];

	$id = $island->{'id'};

	if($island->{'absent'}  == 0) {
		$name = "${HtagName_}$island->{'name'}島${H_tagName}";
	} else {
	    $name = "${HtagName2_}$island->{'name'}島($island->{'absent'})${H_tagName2}";
	}

	$ip0 = $island->{'ip0'};
	$ip1 = $island->{'ip1'};
	$ip2 = $island->{'ip2'};
	$ip3 = $island->{'ip3'};
	$ip4 = $island->{'ip4'};
	$ip5 = $island->{'ip5'};
	$ip6 = $island->{'ip6'};
	$ip7 = $island->{'ip7'};
	$ip8 = $island->{'ip8'};
	$ip9 = $island->{'ip9'};

	$island->{'ippts'} = 0;


	    my($ip0) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip0'} eq $island->{'ip0'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip1) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip1'} eq $island->{'ip0'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip2) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip2'} eq $island->{'ip0'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip3) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip3'} eq $island->{'ip0'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip4) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip4'} eq $island->{'ip0'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip5) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip5'} eq $island->{'ip0'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }


	    my($ip0) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip0'} eq $island->{'ip1'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip1) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip1'} eq $island->{'ip1'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip2) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip2'} eq $island->{'ip1'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip3) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip3'} eq $island->{'ip1'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip4) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip4'} eq $island->{'ip1'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip5) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip5'} eq $island->{'ip1'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }


	    my($ip0) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip0'} eq $island->{'ip2'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip1) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip1'} eq $island->{'ip2'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip2) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip2'} eq $island->{'ip2'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip3) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip3'} eq $island->{'ip2'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip4) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip4'} eq $island->{'ip2'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip5) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip5'} eq $island->{'ip2'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }


	    my($ip0) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip0'} eq $island->{'ip3'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip1) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip1'} eq $island->{'ip3'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip2) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip2'} eq $island->{'ip3'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip3) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip3'} eq $island->{'ip3'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip4) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip4'} eq $island->{'ip3'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip5) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip5'} eq $island->{'ip3'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }


	    my($ip0) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip0'} eq $island->{'ip4'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip1) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip1'} eq $island->{'ip4'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip2) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip2'} eq $island->{'ip4'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip3) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip3'} eq $island->{'ip4'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip4) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip4'} eq $island->{'ip4'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip5) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip5'} eq $island->{'ip4'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }


	    my($ip0) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip0'} eq $island->{'ip5'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip1) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip1'} eq $island->{'ip5'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip2) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip2'} eq $island->{'ip5'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip3) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip3'} eq $island->{'ip5'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip4) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip4'} eq $island->{'ip5'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }
	    my($ip5) = @_;
	    # 全島から探す
	    my($i);
	    for($i = 0; $i < $HislandNumber; $i++) {
		if($Hislands[$i]->{'ip5'} eq $island->{'ip5'}) {
		if($Hislands[$i]->{'id'} != $island->{'id'}) {
		    $island->{'ippts'}++;
		    $island->{'ipkaburi'} .= "$Hislands[$i]->{'name'}島(ID:$Hislands[$i]->{'id'})／";
		}
		}
	    }

	$ippts = $island->{'ippts'};

	$island->{'iprank'} = $island->{'ippts'};


	islandSortip();
	    }

        out(<<END);

<HR>

<H1>${HtagHeader_}表の説明${H_tagHeader}</H1>
<P>
・IP発見数はそれぞれの島の６つのIPについて、自分以外の全ての島のものから比較して算出してます。<br>
　つまり複数発見された場合、他の島に同IPがあるということになります(当たり前か^^;)<br><br>
・IP変化数はプロバイダによりけりなので、多い島はプロバイダについて調べてみるのがいいかもです。<br>
　複数の回線を使ってる場合は怪しいかもです。ちなみにBIGLOBEは接続の度にIP変動しました(T∇T)<br><br>
・裏ランキングは同IP発見数で決まっています。高順位のものほど怪しい！？かな！？<br>
　こうゆうものを数えてみれば怪しさの参考になるのでは？という意見は<br>
　ぜひご一報を。。。（例）ミサイル発射数、コメント発言数←黙ってる人は怪しいの原理？！<br><br>
・登録時IPは島発見時のもので、既存の島などは初コマンド入力の際にゲットされます。<br>
　この情報は基本的に消えないはずです。（バックアップ使用時は未対応かも^^;;;（大汗<br><br>
・最新 ― ― ― 古 のIPは過去５回までのIPの変動値です。コマンド入力時のIPが最新のものと<br>
　異なっていた場合に更新されます。その場合古いIPは消えます。（過去５回分では少ないでしょうか？！）
</P>
<TABLE BORDER>
<TR>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}順位${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}島${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}同IP発見数${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}最新${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}―${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}―${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}―${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}古${H_tagTH}</NOBR></TH>
<TH $HbgTitleCell align=center nowrap=nowrap><NOBR>${HtagTH_}登録時${H_tagTH}</NOBR></TH>
</TR>
END

    my($island, $j, $farm, $factory, $mountain, $name, $id, $prize, $ii);
    for($ii = 0; $ii < $HislandNumber; $ii++) {
	$j = $ii + 1;
	$island = $Hislands[$ii];

	$id = $island->{'id'};

	if($island->{'absent'}  == 0) {
		$name = "${HtagName_}$island->{'name'}島${H_tagName}";
	} else {
	    $name = "${HtagName2_}$island->{'name'}島($island->{'absent'})${H_tagName2}";
	}

	$ip0 = $island->{'ip0'};
	$ip1 = $island->{'ip1'};
	$ip2 = $island->{'ip2'};
	$ip3 = $island->{'ip3'};
	$ip4 = $island->{'ip4'};
	$ip5 = $island->{'ip5'};
	$ip6 = $island->{'ip6'};
	$ip7 = $island->{'ip7'};
	$ip8 = $island->{'ip8'};
	$ip9 = $island->{'ip9'};

	$ippts = $island->{'ippts'};

	$island->{'iprank'} = $island->{'ippts'};

	out(<<END);
<TR>
<TD $HbgNumberCell ROWSPAN=3 align=center nowrap=nowrap><NOBR>${HtagNumber_}$j${H_tagNumber}</NOBR></TD>
<TD $HbgNameCell ROWSPAN=3 align=left nowrap=nowrap>
<NOBR>
<A STYlE=\"text-decoration:none\" HREF="${HthisFile}?Sight=${id}">
$name
</A><br>(ID:$island->{'id'})
</NOBR>
</TD>
<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>$island->{'ippts'}</NOBR></TD>
<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>$island->{'ip5'}</NOBR></TD>
<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>$island->{'ip4'}</NOBR></TD>
<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>$island->{'ip3'}</NOBR></TD>
<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>$island->{'ip2'}</NOBR></TD>
<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>$island->{'ip1'}</NOBR></TD>
<TD $HbgInfoCell align=right nowrap=nowrap><NOBR>$island->{'ip0'}</NOBR></TD>
</TR>
<TR>
<TD $HbgCommentCell COLSPAN=7 align=left nowrap=nowrap><NOBR>${HtagTH_}同IPを発見した島：${H_tagTH}$island->{'ipkaburi'}</NOBR></TD>
</TR>
<TR>
<TD $HbgCommentCell COLSPAN=7 align=left nowrap=nowrap><NOBR>${HtagTH_}その他情報：${H_tagTH}00〜99ターンでのIP変動数($island->{'ip8'}回)・通算IP変動数($island->{'ip9'}回)</NOBR></TD>
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
パスワードは？<BR>
<INPUT TYPE="password" NAME="PASSWORD" SIZE=32 MAXLENGTH=32><BR>
念のためパスワードをもう一回<BR>
<INPUT TYPE="password" NAME="PASSWORD2" SIZE=32 MAXLENGTH=32><BR>

<INPUT TYPE="submit" VALUE="探しに行く" NAME="NewIslandButton">
</FORM>
END
    } else {
	out(<<END);
        島の数が最大数です・・・現在登録できません。
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
パスワードは？(必須)<BR>
<INPUT TYPE="password" NAME="OLDPASS" SIZE=32 MAXLENGTH=32><BR>
新しいパスワードは？(変更する時のみ)<BR>
<INPUT TYPE="password" NAME="PASSWORD" SIZE=32 MAXLENGTH=32><BR>
念のためパスワードをもう一回(変更する時のみ)<BR>
<INPUT TYPE="password" NAME="PASSWORD2" SIZE=32 MAXLENGTH=32><BR>

<INPUT TYPE="submit" VALUE="変更する" NAME="ChangeInfoButton">
<INPUT TYPE="submit" VALUE="(・∀・)" NAME="IPInfoButton">
</FORM>

<HR>

END

}

# トップページ用ログ表示
sub logPrintTop {
    my($i);
    for($i = 0; $i < $HtopLogTurn; $i++) {
	logFilePrint($i, 0, 0);
    }
}

sub islandSortip {
my($flag, $i, $tmp);

my @idx = (0..$#Hislands);
@idx = sort { $Hislands[$b]->{'iprank'} <=> $Hislands[$a]->{'iprank'} || $a <=> $b } @idx;
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

1;

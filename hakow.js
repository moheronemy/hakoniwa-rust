// 設定値
function initialize() {
    adminName = '徳岡宏樹';
    email = 'tokuoka@taurus.bekkoame.ne.jp';
    homepage = 'http://t.pos.to/ex.html';

    // 表示する地図の大きさ
    normalSize = 11;
    largeSize = 23;
    printMode = 0; // 0がnormal

    normalHalf = Math.floor(normalSize / 2);
    largeHalf = Math.floor(largeSize / 2);

    // 一度に表示する順位
    printOrder = 5;

    // 資金の単位
    unitMoney = '億円';

    // 食料の単位
    unitFood = '00トン';

    // 人口の単位
    unitPop = '00人';

    // 面積の単位
    unitArea = '00万坪';

    // 木の単位
    unitTree = '00本';

    // 入力中コマンドの背景色
    changeCommandBG = '#DDDDFF';

    // コマンド
    comlist = 
	[
	 [1,'整地',5],
	 [62,'食料輸出',-100],
	 [2,'地均し',100],
	 [3,'埋めたて',150],
	 [4,'掘削',200],
	 [5,'伐採',0],
	 [6,'領土拡張',100],
	 [21,'植林',50],
	 [22,'農場整備',20],
	 [23,'工場建設',100],
	 [24,'採掘場整備',300],
	 [25,'ミサイル基地建設',300],
	 [26,'防衛施設建設',800],
	 [27,'海底基地建設',8000],
	 [28,'記念碑建造',9999],
	 [29,'ハリボテ設置',1],
	 [41,'ミサイル発射',20],
	 [42,'PPミサイル発射',50],
	 [43,'陸地破壊弾発射',100],
	 [44,'弾道ミサイル発射',150],
	 [45,'怪獣派遣',3000],
	 [61,'資金繰り',0],
	 [63,'資金援助',100],
	 [64,'食料援助',-100],
	 [65,'誘致活動',1000],
	 [67,'拠点変更',1000],
	 [66,'島の放棄',0]
	 ];

    // 怪獣の名前
    monsterName =
	[
	 'メカいのら',     // 0(人造)
	 'いのら',         // 1
	 'サンジラ',       // 2
	 'レッドいのら',   // 3
	 'ダークいのら',   // 4
	 'いのらゴースト', // 5
	 'クジラ',         // 6
	 'キングいのら'    // 7
	 ];

    // 怪獣の画像
    monsterImage =
	[
	 'monster7.gif',
	 'monster0.gif',
	 'monster5.gif',
	 'monster1.gif',
	 'monster2.gif',
	 'monster8.gif',
	 'monster6.gif',
	 'monster3.gif'
	 ];

    // 経験値
    baseExp = [20, 60, 120, 200];
    sBaseExp = [50, 200];

    // 怪獣の画像(硬化中)
    monsterImage2 = ['','','monster4.gif','','','','monster4.gif',''];

    // 怪獣の硬化特性
    // 0:硬化しない 1:奇数ターン 2:偶数ターン
    monsterHard = [0,0,1,0,0,0,2,0];

    // 賞の名前
    prizeName = 
	[
	 '100ターン杯',
	 '300ターン杯',
	 '1000ターン杯',
	 '繁栄賞',
	 '超繁栄賞',
	 '究極繁栄賞',
	 '災難賞',
	 '超災難賞',
	 '究極災難賞',
	 '平和賞',
	 '超平和賞',
	 '究極平和賞'
	 ];

    // 賞の画像
    prizeImage = 
	[
	 'prize0.gif',
	 'prize10.gif',
	 'prize11.gif',
	 'prize1.gif',
	 'prize2.gif',
	 'prize3.gif',
	 'prize7.gif',
	 'prize8.gif',
	 'prize9.gif',
	 'prize4.gif',
	 'prize5.gif',
	 'prize6.gif'
	 ];

    // 記念碑の名前
    monumentName =
	[
	 'モノリス',
	 '平和の塔',
	 '戦争の碑'
	 ];

    // ヘッダ
    header =
	'<A HREF="http://www.bekkoame.ne.jp/~tokuoka/hakoniwa.html">箱庭諸島スクリプト配布元</A><HR>'
        + '<FONT SIZE=7 COLOR="#8888ff">' + titleName + '</FONT><HR>';

    // フッタ
    footer = 
	'<HR><P align=center>管理者:' + adminName + '(<A HREF="mailto:' +
	    email + '">' + email + '</A>)<BR>掲示板(<A HREF="' + bbs + '">' +
		bbs + '</A>)<BR>ホームページ(<A HREF="' + homepage + '">' + homepage +
		    '</A>)<BR>箱庭諸島のページ(<A HREF="http://www.bekkoame.ne.jp/' +
    '~tokuoka/hakoniwa.html">http://www.bekkoame.ne.jp/~tokuoka/hakoniwa.html' +
    '</A>)<BR>';

    // 「戻る」リンク
    backLink = big('<A HREF="' + cgiURL + '?cname=' + cname + '">トップへ戻る</A>');

    // フォームヘッダ
    formHeader = '<FORM action="' + cgiURL + '" method="POST"><input type=hidden name="cname" value="' + cname + '">';
}

// フォントの設定
function tagHeader(s) {
    return '<FONT COLOR="#4444ff">' + s + '</FONT>';
}

// エラーメッセージ
function errorMes(s) {
    return '<FONT SIZE=5>' + s + '</FONT>';
}

// でかい文字
function big(s) {
    return '<FONT SIZE=5>' + s + '</FONT>';
}

// ボタン
function tagButton(s) {
    return '<FONT COLOR="#008800"><B><U>' + s + '</U></B></FONT>';
}

// 番号
function tagNumber(s) {
    return '<FONT COLOR="#800000"><B>' + s + '</B></FONT>';
}

// コマンドの名前
function tagComName(s) {
    return '<FONT COLOR="#d08000"><B>' + s + '</B></FONT>';
}

// 島の名前
function tagName(s) {
    return '<FONT COLOR="#a06040" ><B>' + s + '</B></FONT>';
}

// 島の名前(グレー)
function tagName2(s) {
    return '<FONT COLOR="#808080"><B>' + s + '</B></FONT>';
}

// 災害
function tagDis(s) {
    return '<FONT COLOR="#FF0000"><B>' + s + '</B></FONT>';
}

// セルの属性
// 順位表見出し
function cellTitle(s) {
    return '<TH BGCOLOR="#ccffcc"><NOBR>' + s + '</NOBR></TH>';
}

// 順位表順位
function cellNumber(s) {
    return '<TD BGCOLOR="#ccffcc" ROWSPAN=2 ALIGN=center><NOBR>' + tagNumber(s) + '</NOBR></TD>';
}

// 順位表島名
function cellName(s) {
    return '<TD BGCOLOR="#ccffff" ROWSPAN=2 ALIGN=center><NOBR>' + s + '</NOBR></TD>';
}

// 順位表島情報
function cellInfo(s) {
    return '<TD BGCOLOR="#ccffff" ALIGN=right><NOBR>' + s + '</NOBR></TD>';
}

// 順位表コメント欄
function cellComment(s) {
    return '<TD BGCOLOR="#ccffcc" COLSPAN=8><NOBR>' + s + '</NOBR></TD>';
}

// メインルーチン
function main() {
    // 初期化
    initialize();
    var str = header;

    // モードで分岐
    if(mainMode == 'owner') {
	// 島主モード
	str += ownerMain();
    } else if(mainMode == 'map') {
	// 観光者モード
	str += tagHeader('<H1>箱庭諸島へようこそ・・・</H1>') + backLink;
	str += sightMain();
    } else if(mainMode == 'mente') {
	// メンテナンスモード
	str += menteMain();
    } else if(mainMode == 'top') {
	// トップメニューモード
	str += topMain();
    } else {
	// エラーメッセージ(エラーじゃないのもある)
	if(mainMode == 'errorNewIsland') {
	    str += errorMes('島を発見しました！！');

	} else if(mainMode == 'errorIslandFull') {
	    str += errorMes('島の数が最大数です。登録できません。');

	} else if(mainMode == 'errorNoName') {
	    str += errorMes('島の名前が必要です。');


	} else if(mainMode == 'errorBadName') {
	    str += errorMes(',"?()<>\$とか入ってたり、「忘れ去られた島」とかいった変な名前はやめましょうよ～'); // "

	    } else if(mainMode == 'errorDupName') {
		str += errorMes('その島なら既に発見されていますよ。');

	    } else if(mainMode == 'errorNoPassword') {
		str += errorMes('パスワードが必要です。');

	    } else if(mainMode == 'errorWrongPassword') {
		str += errorMes('パスワードが違います。');

	    } else if(mainMode == 'errorNotEnoughArea') {
		str += errorMes('その辺には島はないようです・・・');

	    } else if(mainMode == 'errorNotEnoughMoney') {
		str += errorMes('資金が不足しています・・・');

	    } else if(mainMode == 'errorNotChange') {
		str += errorMes('変更はされませんでした。');

	    } else if(mainMode == 'errorMaxMoney') {
		str += errorMes('資金、食料を最大値にしました。');

	    } else if(mainMode == 'errorChange') {
		str += errorMes('変更しました。');

	    }

	// 'トップへ戻る'リンク
	str += backLink;

    }	

    // フッタを出して終了
    document.all.mainBody.innerHTML = str + footer;
}

// トップページ
function topMain() {
    var str = '';
    if(debugMode == 1) {
	str = formHeader + '<INPUT TYPE="submit" NAME="TurnMode" VALUE="ターンを進める"></FORM>';
    }
    str +=
	tagHeader('<H1>ターン' + cturn + '/' + eturn + '</H1>') + '<HR>' +
        formHeader + tagHeader('<H1>自分の島へ</H1>') + islandList() +
	'<BR>パスワード<INPUT TYPE="password" NAME="Password" VALUE="' +
	dpass +	'"SIZE=32 MAXLENGTH=32>' +
	'<BR><INPUT TYPE="submit" VALUE="開発しに行く" NAME="OwnerMode"></FORM>' +
	tagHeader('<HR><H1>観光、島探し</H1>') + 
					    formHeader + 
						'<INPUT TYPE="submit" VALUE="観光／島探しに行く" NAME="MapMode"></FORM>' +
						    tagHeader('<HR><H1>島名、パスワードの変更</H1>') + 
							"<P>(島名の変更は500億円、パスワード変更は無料)</P>" +
							    formHeader + 
								'<TABLE><TR><TD>元の島名</TD><TD>' + islandList() + '</TD></TR>' +
								    '<TR><TD>新しい島名(変更する場合のみ)</TD><TD><INPUT TYPE="text" NAME="IslandName" SIZE=32 MAXLENGTH=32>島</TD></TR>' + 
									'<TR><TD>旧パスワード(必須)</TD><TD><INPUT TYPE="password" NAME="Password" VALUE="' +
									    dpass +	'"SIZE=32 MAXLENGTH=32></TD></TR>' +
										'<TR><TD>新パスワード(変更する場合のみ)</TD><TD><INPUT TYPE="password" NAME="Password3" SIZE=32 MAXLENGTH=32></TD></TR>' +
										    '<TR><TD>確認用パスワード</TD><TD><INPUT TYPE="password" NAME="Password2" SIZE=32 MAXLENGTH=32></TD></TR><TR><TD></TD><TD><INPUT TYPE="submit" VALUE="変更する" NAME="RenameMode"></TD></TR></TABLE></FORM><HR>' +
											formHeader + 
											    'パスワード<INPUT TYPE="password" NAME="Password" SIZE=32 MAXLENGTH=32>' +
												'<BR><INPUT TYPE="submit" VALUE="管理者モードへ" NAME="MenteMode">' +

												    '</FORM>';
    return str;
}

// 島主モード
function ownerMain() {
    var island = getIslandByID(currentID);
    var name = island[0];
    currentX = island[2];
    currentY = island[3];

    // 予約コマンドセット
    currentPlanD();

    var str = tagHeader('<H1>' + name + '島開発計画</H1>') + backLink;

    str += orderPrint(getNumberByID(currentID) + 1, 1);

    str += '<TABLE BORDER><TR><TD ID ="map">' + 
	mapPrint(currentX,currentY) + '</TD>' +
	    '<TD align=center><B>計画番号</B>' + planNumList() +
            '<HR><B>開発計画</B><BR>' + commandList() +
	    '<HR><B>座標</B>' + pointList(currentX, currentY) +
	    '<HR><B>対象の島</B><BR>' + islandList() +
            '<HR><B>数量</B>' + amountList() +
	    '<HR><A HREF="JavaScript:void(0);" onClick="comIn(0)">' +
             tagButton('挿入') + '</A>　' +
            '<A HREF="JavaScript:void(0);" onClick="comIn(1)">' +
            tagButton('上書') + '</A>　' +
            '<A HREF="JavaScript:void(0);" onClick="comIn(2)">' +
            tagButton('削除') + '</A>' +
	    formHeader +
            '<INPUT NAME="CommandList" TYPE="hidden" ID="commandtext" VALUE="' +
						    currentPlanD() +
							'"><B>パスワード</B><BR><INPUT TYPE=password VALUE="' +
							    dpass +
								'"NAME="Password">' +
								    '<HR><INPUT NAME="CommandMode" VALUE="計画送信" TYPE="submit"></FORM>' +
									'</TD><TD ID="planarea">';

    str += currentPlan() + '</TD></TR></TABLE>';

    // 順位部分
    currentOrder = 1;
    str += '<P ID="order">' + orderPrint(1, 0) + '</P>';

    // コメント入力ボックス
    str += tagHeader('<H1>コメント更新</H1>') + formHeader +
	'<TABLE BORDER><TR><TH COLSPAN=2><INPUT TYPE=text NAME=Message SIZE=80></TH></TR><TR><TH>パスワード<INPUT TYPE=password NAME=Password VALUE="' + dpass + '"></TH><TH><INPUT TYPE=submit VALUE="コメント更新" NAME=MesMode' + currentID + '></TH></TR></TABLE></FORM>';


    // ログ部分
    str += tagHeader('<H1>最近の出来事</H1>') + 
	'<P ID="log">' + logPrint(currentID) + '</P>' + hisPrint();

    return str;
}

// 観光者モード
function sightMain() {
    // 地図部分
    currentX = Math.floor(worldSize / 2);
    currentY = Math.floor(worldSize / 2);
    if(infoData.length > 0) {
	currentX = infoData[0][2];
	currentY = infoData[0][3];
    }
    var str =
	'<TABLE BORDER><TR><TD ID ="map">' +
	    mapPrint(currentX,currentY) +
		'</TD><TD>';

    // 島が最大数でない場合
    str += tagHeader('<H2>島を探す</H2>');
    str += formHeader + 'どんな名前をつける予定？<BR><INPUT TYPE="text" NAME="IslandName" SIZE=32 MAXLENGTH=32>島<BR>パスワードは？<BR><INPUT TYPE="password" VALUE="' + dpass +
	'"NAME="Password" SIZE=32 MAXLENGTH=32><BR>念のためパスワードをもう一回<BR><INPUT TYPE="password" NAME="Password2" SIZE=32 MAXLENGTH=32><BR>' +
	    pointList(currentX, currentY);
    if(infoData.length < maxNumber) {
	str += '付近へ<INPUT TYPE="submit" VALUE="探しに行く" NAME="NewIslandMode"></FORM>';
    } else {
	str += '<BR><B>島の数が最大数です。<BR>現在登録できません。</B></FORM>';
    }

    str += '</TD></TR></TABLE>';

    // 順位部分
    currentOrder = 1;
    str += '<P ID="order">' + orderPrint(1, 0) + '</P>';

    // ログ部分
    str += tagHeader('<H1>最近の出来事</H1>') + 
	'<P ID="log">' + logPrint(0) + '</P>' + hisPrint();
    return str;
}

// メンテモード
function menteMain() {
    var str = '<H1>管理者モード</H1>' + backLink + '<HR>' + formHeader +
	'パスワード：<INPUT TYPE="password" NAME="Password" SIZE=32 MAXLENGTH=32>';
    if(currentData[0] == 0) {
	str +=
	    '<HR>現役データはありません<BR><INPUT TYPE="submit" VALUE="新規データを作る" NAME="MakeData">';
    } else {
	str += '<HR><H3>現役データ</H3>';
	str += menteData(currentData);
	str += '<BR><INPUT TYPE="submit" VALUE="バックアップ" NAME="BackUp">';
	str += '<INPUT TYPE="submit" VALUE="このデータを削除" NAME="Delete">';
	str += '<BR>最終更新秒数を<INPUT TYPE="text" NAME="Second" VALUE="' + currentData[1] + '" SIZE=32 MAXLENGTH=32><INPUT TYPE="submit" VALUE="に変更する" NAME="ChangeTime">';
    }

    var i;
    for(i = 0; i < backUpMax; i++) {
	if(backData[i][0] != 0) {
	    str += '<HR><H3>バックアップ' + i + '</H3>';
	    str += menteData(backData[i]);
	    str += '<BR><INPUT TYPE="submit" VALUE="このデータを現役に" NAME="Activate' + i + '">';
	    str += '<INPUT TYPE="submit" VALUE="このデータを削除" NAME="Delete' + i + '">';
	}
    }

    return str + '</FORM>';
}

// 各データ表示
function menteData(d) {
    var str = '[' + d[0] + 'ターン]最終更新' + d[1] + '秒(';
    var dDate = new Date(d[1] * 1000);
    str += dDate.toLocaleString() + ')';
    return str;
}

// 地図表示
function mapPrint(sx, sy) {
    var x, y, tx, ty, str;

    var printSize;
    var halfSize;
    var il, is;
    if(printMode == 0) {
	printSize = normalSize;
	halfSize = normalHalf;
	il = 32;
	is = 16;
    } else {
	printSize = largeSize;
	halfSize = largeHalf;
	il = 16;
	is = 8;
    }

    tx = sx - halfSize;
    ty = sy - halfSize;
    if(tx < 0) { tx = 0; }
    if(ty < 0) { ty = 0; }
    if(tx >= (worldSize - printSize)) { tx = (worldSize - printSize); }
    if(ty >= (worldSize - printSize)) { ty = (worldSize - printSize); }

    str = '<B>(' + currentX + ',' + currentY + ')地点付近</B> 表示領域(' +
	tx + ',' + ty + ')～(' + (tx + printSize - 1) + ',' +
	    (ty + printSize - 1) + ')';
    str += '<TABLE BORDER><TR><TD>';
    for(y = ty; y < (ty + printSize); y++) {
	if((y % 2) == 0) {
	    str += '<IMG WIDTH=' + is + ' HEIGHT=' + il + ' SRC="black.gif">';
	}
	for(x = tx; x < (tx + printSize); x++) {
	    var land = mapPoint(x, y);
	    var kind = land[0];  // 地形の種類
	    var param = land[1]; // パラメータ
	    var owner = land[2]; // 持ち主
	    var name = '中立地域';
	    if(owner != 0) {
		name = getIsland(owner)[0] + '島';
	    }
	    var altString = name + '(' + x + ',' + y + ')\n';
	    var imageFile = '';
	    switch(kind) {
	    case 0:
		if(param == 0) {
		    altString += '海';
		    imageFile = 'land0.gif';
		} else if(param == 1){
		    altString += '海(浅瀬)';
		    imageFile = 'land14.gif';
		} else {
		    altString += '海底油田';
		    imageFile = 'land16.gif';
		}
		break;

	    case 1:
		altString += '荒地';
		if(param == 0) {
		    imageFile = 'land1.gif';
		} else {
		    imageFile = 'land13.gif';
		}
		break;

	    case 2:
		if(param == 0) {
		    altString += '平地';
		    imageFile = 'land2.gif';
		} else {
		    if(param < 30) {
			altString += '村';
			imageFile = 'land3.gif';
		    } else if(param < 100) {
			altString += '町';
			imageFile = 'land4.gif';
		    } else {
			altString += '都市';
			imageFile = 'land5.gif';
		    }
		    altString += '(' + param + unitPop + ')'
		    }
		break;

	    case 3:
		altString += '森';
		imageFile = 'land6.gif';
		if(param != 0) {
		    altString += '(' + param + unitTree + ')';
		}
		break;

	    case 4:
		altString += '農場(' + param + '0' + unitPop + '規模)';
		imageFile = 'land7.gif';
		break;

	    case 5:
		altString += '工場(' + param + '0' + unitPop + '規模)';
		imageFile = 'land8.gif';
		break;

	    case 6:
		altString += 'ミサイル基地(レベル' +
		    expToLevel(baseExp, param) + '/経験値' + param + ')';
		imageFile = 'land9.gif';
		break;

	    case 7:
		if(param == 0) {
		    altString += '防衛施設';
		} else {
		    altString += 'ハリボテ';
		}
		imageFile = 'land10.gif';
		break;

	    case 8:
		if(param == 0) {
		    altString += '山';
		    imageFile = 'land11.gif';
		} else {
		    altString += '山(採掘場' + param + '0' + unitPop + '規模)';
		    imageFile = 'land15.gif';
		}

		break;

	    case 9:
		{
		    var k = Math.floor(param / 20);
		    var h = Math.floor(param % 20);
		    if(((monsterHard[k] == 1) && ((cturn % 2) == 1)) ||
		       ((monsterHard[k] == 2) && ((cturn % 2) == 0))) {
			altString += '怪獣' + monsterName[k] + '(体力' + h + ':硬化中)';
			imageFile = monsterImage2[k];
		    } else {
			altString += '怪獣' + monsterName[k] + '(体力' + h + ')';
			imageFile = monsterImage[k];
		    }
		}
		break;

	    case 10:
		altString += '海底基地(レベル' +
		    expToLevel(sBaseExp, param) + '/経験値' + param + ')';
		imageFile = 'land12.gif';
		break;

	    case 11:
		altString += monumentName[param];
		imageFile = 'monument0.gif';
		break;
	    }

	    if(mainMode == 'owner') {
		var i;
		for(i = 0; i < commandMax; i++) {
		    var c = comData[i];
		    if(c[0] < 40) {
			if((x == c[2]) && (y == c[3])) {
			    var cn = commandObj(c[0]);
			    altString += '\n[' + (i + 1) + ']' + cn[1];
			}
		    }
		}
	    }
	    var alt2;
	    alt2 = altString.replace(/[\n]/g,"");
	    str += '<IMG WIDTH=' + il + ' HEIGHT=' + il + ' SRC="' + imageFile +
		'" ALT ="' + altString +
		    '" ondblclick="mapMove(' + x + ',' + y + ')" onclick="pointMove(' + x + ',' + y + '); return true" onmouseover="window.status=\'' + alt2 + '\';return true"  BORDER=0>';
	    //		'" ondblclick="mapMove(' + x + ',' + y + ')" onclick="pointMove(' + x + ',' + y + '); return true" onmouseover="window.status=\'' + '\';return true">';
	}
	if((y % 2) == 1) {
	    str += '<IMG WIDTH=' + is + ' HEIGHT=' + il + ' SRC="black.gif">';
	}
	str += '<BR>';

    }
    str += '</TD></TR></TABLE>';
    str += 'ダブルクリックした場所が中心になります<BR>';
    str += '<A HREF="JavaScript:void(0);" onclick="changePMode(); return true" align=center>表示モード切り替え(使用マシンに自信のある人のみ)</A>';
    return str;
}

// 表示モード切り替え
function changePMode() {
    printMode = 1 - printMode;
    mapMove(currentX, currentY);
}


// 順位表示
function orderPrint(number, mode) {
    var i;
    var l = infoData.length;
    var str = '';
    var po;
    if(mode == 0) {
	po = printOrder;
    } else {
	po = 1;
    }
    if((number > 1) && (mode == 0)){
	str += '<A HREF="JavaScript:void(0);" onclick="orderMove(-' + printOrder + ')">▲上位▲</A>';
    } else {
	str += '<BR>';
    }
    str +=
	'<TABLE BORDER><TR>' +
        cellTitle('順位') +
	cellTitle('島の名前</A>') +
	cellTitle('人口') + cellTitle('位置') +
	cellTitle('面積') +
	cellTitle('資金') + cellTitle('食料') + cellTitle('農場') +
	cellTitle('工場') + cellTitle('採掘場') + '</TR>';
    for(i = number; (i < (number + po)) && (i <= l); i++){
	var island = getIsland(i);
	var money = island[8];
	if((island[1] != currentID) || (mainMode != 'owner')){
	    if(money < 500) {
		money = '推定500' + unitMoney + '未満';
	    } else {
		money = '推定' + money + unitMoney;
	    }
	} else {
	    money = money + unitMoney;
	}
	var farm;
	if(island[12] == 0) {
	    farm = '保有せず';
	} else {
	    farm = island[12] + '000人規模';
	}

	var factory;
	if(island[13] == 0) {
	    factory = '保有せず';
	} else {
	    factory = island[13] + '000人規模';
	}

	var mountain;
	if(island[14] == 0) {
	    mountain = '保有せず';
	} else {
	    mountain = island[14] + '000人規模';
	}

	var name = island[0] + '島';
	if(island[6] > 0) {
	    name = tagName2(name + '(' + island[6] + ')');
	} else  {
	    name = tagName(name);
	}

	var prize = island[4];
	var prizeStr = '';
	var j;
	var k = 1;
	for(j = 0; j < prizeName.length; j++) {
	    if(k & prize) {
		prizeStr += ' <IMG SRC="' + prizeImage[j] + '" ALT="' + prizeName[j] + '" WIDTH=16 HEIGHT=16>';
	    }
	    k = k * 2;
	}

	var monster = island[5];
	var last = -1;
	var monAlt = '';
	k = 1;
	for(j = 0; j < monsterName.length; j++) {
	    if(k & monster) {
		last = j;
		monAlt += monsterName[j];
	    }
	    if(j != monsterName.length - 1) {
		monAlt += "\n";
	    }
	    k = k * 2;
	}
	if(last != -1) {
		prizeStr += ' <IMG SRC="' + monsterImage[last] + '" ALT="' + monAlt + '" WIDTH=16 HEIGHT=16>';
	}

	str += '<TR>' + cellNumber(i) +
	    cellName(
		     '<A STYLE="text-decoration:none" HREF="JavaScript:void(0);" onclick="mapMove(' +
		     island[2] + ',' + island[3] +
		     ');logRewrite(' + island[1] + ');">' +
		     name + '</A><BR><NOBR>' + prizeStr + '</NOBR>' ) +
		     cellInfo(island[10] + unitPop) + 
		     cellInfo('(' + island[2] + ',' + island[3] + ')') +
		     cellInfo(island[11] + unitArea) + cellInfo(money) + 
		     cellInfo(island[9] + unitFood) + cellInfo(farm) +
		     cellInfo(factory) +
		     cellInfo(mountain) + '</TR><TR>' + cellComment('<B>コメント：</B>' + island[7]) + '<TR>';
    }
    str += '</TABLE>';
    if(((number + po) <= l) && (mode == 0)) {
	str += '<A HREF="JavaScript:void(0);" onclick="orderMove(' + printOrder + ')">▼下位▼</A>';
    } else {
	str += '<BR>';
    }
    return str;
}

// 順位表の上下
function orderMove(d) {
    currentOrder += d;
    var l = infoData.length;
    if(currentOrder < 1) {
	currentOrder = 1;
    } else if(currentOrder > l) {
	currentOrder = l;
    }
    currentOrder -= (currentOrder % printOrder - 1);
    document.all.order.innerHTML = orderPrint(currentOrder, 0);
}

// 移動
function mapMove(x, y) {
    if(x < 0) { x = 0; }
    if(y < 0) { y = 0; }
    if(x >= worldSize) { x = worldSize - 1; }
    if(y >= worldSize) { y = worldSize - 1; }
    currentX = x;
    currentY = y;
    var str = mapPrint(x,y);
    document.all.map.innerHTML = str;
    pointMove(currentX, currentY);
}

// 座標だけ移動
function pointMove(x, y) {
    if(x < 0) { x = 0; }
    if(y < 0) { y = 0; }
    if(x >= worldSize) { x = worldSize - 1; }
    if(y >= worldSize) { y = worldSize - 1; }
    document.all.pointX.options[x].selected = true;
    document.all.pointY.options[y].selected = true;
}

// コマンド入力
function comIn(mode) {
    // 情報取り出し
    var planNum = document.all.planNum.value;
    var command = document.all.command.value;
    var x = document.all.pointX.value;
    var y = document.all.pointY.value;
    var island = document.all.island.value;
    var amount = document.all.amount.value;
    var i;

    if(mode == 0) {
	// 挿入モード
	// 番号以降を後ろへずらす
	for(i = commandMax - 1; i > planNum; i--) {
	    comData[i] = comData[i - 1];
	}
    }

    if(mode != 2) {
	// 削除以外
	comData[planNum] = [command, island, x, y, amount];
	if(planNum < (commandMax - 1)) {
	    numberSet(1 + Math.floor(planNum));	
	}
    } else {
	// 削除
	for(i = Math.floor(planNum); i < (commandMax - 1); i++) {
	    comData[i] = comData[i + 1];
	}
	comData[commandMax - 1] = [61,0,0,0,0];
    }

    // データに反映
    document.all.commandtext.value = currentPlanD();
    document.all.planarea.innerHTML = currentPlan();
    document.all.planarea.bgColor = changeCommandBG;
}

// 地形1マス分取り出し
function mapPoint(x, y) {
    var s = mapData[y].substr(x * 5, 5);
    var s1 = hex(s.substr(0,1));
    var s2 = hex(s.substr(1,2));
    var s3 = hex(s.substr(3,2));
    return [s1, s2, s3];
}

// 文字列の16進数化
function hex(s) {
    var l = s.length;
    var i;
    var v = 0;
    for(i = 0; i < l; i++) {
	v = v * 16;
	var c = s.charCodeAt(i);
	if(c <= 57/* '9' */) {
	    c -= 48/* '0' */;
	} else {
	    c += 10 - 97/* 'a' */;
	}
	v += c;
    }
    return v;
}

// 入力済みの計画(hiddenのvalue用)
function currentPlanD() {
    var str = currentID + ' ';
    var i;
    for(i = 0; i < commandMax; i++) {
	var c = comData[i];
	str += c[0] + ' ' + c[1] + ' ' + c[2] + ' ' + c[3] + ' ' + c[4] + ' ';
    }    
    return str;
}

// 入力済みの計画(表示用)
function currentPlan() {
    var str = '';
    var i;
    for(i = 0; i < commandMax; i++) {
	var c = comData[i];
	var kind = c[0];
	var cc = commandObj(kind);
	var name = tagComName(cc[1]);
	var tname;
	var target = getIslandByID(c[1]);
	tname = target[0];
	tname = tagName(tname + '島');
	var x = c[2];
	var y = c[3];
	var amount = c[4];
	var point = tagName("(" + x + "," + y + ")");

	// 種類で分岐
	var tstr;
	if((kind == 61) ||
	   (kind == 65) ||
	   (kind == 66)) {
	    // 名前だけ系
	    tstr = name;
	} else if((kind == 41) ||
		  (kind == 42) ||
		  (kind == 43) ||
		  (kind == 44)) {
	    // ミサイル
	    tstr = point + 'へ' + name;
	    if(amount == 0) {
		tstr += '(無制限)';
	    } else {
		tstr += '(' + amount + '発)';
	    }
	} else if(kind == 45) {
	    // ターゲット付記
	    tstr = tname + 'へ' + name;
	} else if(kind == 63) {
	    // 資金付記
	    if(amount == 0) { amount = 1; } 
	    tstr = tname + 'へ' + name + amount + '00' + unitMoney;
	} else if(kind == 64) {
	    if(amount == 0) { amount = 1; } 
	    // 食料、相手島付記
	    tstr = tname + 'へ' + name + amount + '00' + unitFood;
	} else if(kind == 62) {
	    if(amount == 0) { amount = 1; } 
	    // 食料付記
	    tstr = name + amount + '00' + unitFood;
	} else if(kind == 4) {
	    // 掘削
	    tstr = point + 'で' + name;
	    if(amount != 0) {
		tstr += '(予算' + (amount * 200) + unitMoney + ')';
	    }
	} else if(kind == 67) {
	    // 座標付記(特殊)
	    tstr = point + 'へ' + name;
	} else  if((kind == 22) || (kind == 23) || (kind == 24)) {
	    // 座標、回数付記
	    if(amount != 0) {
		tstr = point + 'で' + name + '(' + amount + '回)';
	    } else {
		tstr = point + 'で' + name;
	    }
	} else {
	    // 座標付記
	    tstr = point + 'で' + name;
	}
	var dum0 = '';
	if(i < 9) {
	    dum0 = '0';
	}
	str +=
	    '<A STYLE="text-decoration:none;color:000" HREF="JavaScript:void(0);" onClick="numberSet(' + i + ')"><NOBR>' +
		tagNumber(dum0 + (i + 1)) + ':' +
		    tstr + '</NOBR></A><BR>';
    }
    return str;
}

// 計画番号ダイアログをセット
function numberSet(x) {
    document.all.planNum.options[x].selected = true;
}

// 計画の種類->計画オブジェクト
function commandObj(k) {
    var i;
    for(i = 0; i < comlist.length; i++) {
	var c = comlist[i];
	if(k == c[0]) {
	    return c;
	}
    }
    return commandObj(61)/* 資金繰り */;
}

// 計画番号ボックス
function planNumList() {
    var str = '<SELECT NAME="PlanNum" ID= "planNum">'
	var i;
    for(i = 0; i < commandMax; i++) {
	str += '<OPTION VALUE=' + i + '>' + (i + 1);
    }
    str += '</SELECT>'
	return str;
}

// 数量用リストボックスの中身
function amountList() {
    var str = '<SELECT NAME="Amount" ID="amount">';
    var i;
    for(i = 0; i < 100; i++) {
	str += '<OPTION VALUE=' + i + '>' + i;
    }
    str += '</SELECT>'
	return str;
}

// コマンド用リストボックスの中身
function commandList(x, y) {
    var str = '<SELECT NAME="Command" ID="command">';
    var i;
    for(i = 0; i < comlist.length; i++) {
	var c = comlist[i];
	var v = c[2];
	str += '<OPTION VALUE=' + c[0] + '>' + c[1];
	if(v == 0) {
	    str += '(無料)';
	} else if(v < 0) {
	    str += '(' + (-v) + unitFood +')';
	} else {
	    str += '(' + v + unitMoney +')';
	}
    }
    str += '</SELECT>';
    return str;
}

// 座標選択用リストボックスの中身
function pointList(x, y) {
    var str = '(<SELECT NAME="PointX" ID="pointX">';
    str += pointListSub(x);
    str += '</SELECT>,<SELECT NAME="PointY" ID="pointY">';
    str += pointListSub(y);
    str += '</SELECT>)';
    return str;
}

function pointListSub(num) {
    var str = '';
    var i;
    for(i = 0; i < worldSize; i++) {
	if(i == num) {
	    str += '<OPTION VALUE=' + i + ' SELECTED>' + i;
	} else {
	    str += '<OPTION VALUE=' + i + '>' + i;
	}
    }
    return str;
}

// 座標選択用リストボックスの中身
function islandList(x, y) {
    var l = infoData.length;
    var str = '<SELECT NAME="Island" ID="island">';
    for(i = 0; i < l; i++) {
	var island = infoData[i];
	var name = island[0];
	var id = island[1];
	if(did == id) {
	    str += '<OPTION VALUE=' + id + ' SELECTED>' + name + '島';
	} else {
	    str += '<OPTION VALUE=' + id + '>' + name + '島';
	}
    }
    str += '</SELECT>';
    return str;
}

// 番号から島配列を取得
function getIsland(num) {
    return infoData[num - 1];
}

// IDから島配列を取得
function getIslandByID(id) {
    var l = infoData.length;
    var i;
    for(i = 0; i < l; i++) {
	if(infoData[i][1] == id) {
	    return infoData[i];
	}
    }
    return ['忘れ去られた',id,0,0,0,0,0,'',0,0,0,0,0,0,0];
}


// IDから島番号を取得
function getNumberByID(id) {
    var l = infoData.length;
    var i;
    for(i = 0; i < l; i++) {
	if(infoData[i][1] == id) {
	    return i;
	}
    }
    return 0;
}

// ログ書きなおし
function logRewrite(id) {
    document.all.log.innerHTML = logPrint(id);
}


// ログ表示
function logPrint(id) {
    var str = '<A STYLE="text-decoration:none" HREF="JavaScript:void(0);" onclick="logRewrite(0)"><B>[全島分を見るにはここをクリック]</B></A><BR><BR>';
    var i, j;
    var len1 = logData.length;
    if((id == 0) && (len1 > 2)){
	len1 = 2;
    }
    for(i = 0; i < len1; i++) {
	var l = logData[i];
	var len2 = l.length;
	for(j = len2 - 1; j >= 0; j--) {
	    var ll = l[j];
	    if(ll.length != 8) {
		continue;
	    }
	    var kind = ll[0];
	    var mIsland = ll[1];
	    var sIsland = ll[2];
	    var cKind = ll[3];
	    var x = ll[4];
	    var y = ll[5];
	    var land = ll[6];
	    var amount = ll[7];
	    if((id == 0) ||
	       (mIsland == -1) ||
	       (id == mIsland) ||
	       (id == sIsland)) {
		str += logMessage(kind, mIsland, sIsland, cKind,
				  x, y, land, amount, cturn - i);
	    }
	}
    }
    return str;
}

// 各ログの表示
function logMessage(kind, mIsland, sIsland, cKind, x, y, land, amount, turn) {
    var name1 = tagName('中立地域');
    var name2 = tagName('中立地域');
    if(mIsland) {
	var i1 = getIslandByID(mIsland);
	name1 = tagName(i1[0] + '島');
    }
    if(sIsland) {
	var i2 = getIslandByID(sIsland);
	name2 = tagName(i2[0] + '島');
    }
    var c = commandObj(cKind);
    var cName = tagComName(c[1]);

    var lName = '<B>' + landName(land) + '</B>';
    var point;
    if(x != -999) {
	point = '<A STYLE="text-decoration:none" HREF="JavaScript:void(0);" onclick="mapMove(' + x + ',' + y + '); return true">' + tagName('(' + x + ',' + y + ')') + '</A>';
    } else {
	point = tagName('(?,?)');
    }

    var str = '<NOBR>' + tagNumber(turn + 'ターン:');
    switch(kind) {
    case 100: // 資金不足
	str += name1 + 'で予定されていた' + cName +
	    'は、<B>資金不足</B>のため中止されました。';
	break;

    case 101: // 食料不足
	str += name1 + 'で予定されていた' + cName +
	    'は、<B>食料不足</B>のため中止されました。';
	break;

    case 102: // 自分の土地じゃない
	str += name1 + 'で予定されていた' + cName + 'は、予定地の' + point +
	    'が<B>領有地でない</B>ため中止されました。';
	break;

    case 103: // 陸地の種類がだめ
	str += name1 + 'で予定されていた' + cName + 'は、予定地の' + point +
	    'が' + lName + 'だったため中止されました。';
	break;

    case 104: // 周囲に領有地がない
	str += name1 + 'で予定されていた' + cName + 'は、予定地の' + point +
	    '周辺に<B>領有地が無い</B>ため中止されました。';
	break;

    case 105: // すでに自分の土地
	str += name1 + 'で予定されていた' + cName + 'は、予定地の' + point +
	    'が<B>既に領有地である</B>ため中止されました。';
	break;

    case 106: // 他人の土地
	str += name1 + 'で予定されていた' + cName + 'は、予定地の' + point +
	    'が<B>他島の領有地である</B>ため中止されました。';
	break;

    case 107: // 相手の島がない
	str += name1 + 'で予定されていた' + cName +
	    'は、<B>相手の島が既に存在しない</B>ため中止されました。';
	break;

    case 108: // 陸地の種類がだめ
	str += name1 + 'で予定されていた' + cName + 'は、予定地の' + point +
	    'の<B>海運が不便なため</B>に中止されました。';
	break;

    case 200: // 行った + 座標
	str += name1 + 'が' + point + 'で' + cName + 'を行いました。';
	break;

    case 201: // 油田発見
	str += name1 + 'が' + point + 'で予算' + amount + unitMoney + 'の' +
	    cName + 'を行い、<B>油田を掘り当てました。</B>';
	break;

    case 202: // 油田発見ならず
	str += name1 + 'が' + point + 'で予算' + amount + unitMoney + 'の' +
	    cName + 'を行いましたが、<B>油田は見つかりませんでした。</B>';
	break;

    case 203: // 起爆装置起動
	str += name1 + point + 'の' + lName + 'で<B>起爆装置が起動</B>されました。';
	break;

    case 204: // こころなしか・・・
	str += 'こころなしか、' + name1 + 'の<B>森</B>が増えたようです。';
	break;

    case 205: // ミサイル発射指令
	str += name1 + 'が' + point + '地点への' + cName + 'を発令しました。';
	break;

    case 206: // 怪獣派遣
	str += name1 + 'が<B>人造怪獣を建造</B>、' + name2 + 'へ派遣しました。';
	break;

    case 207: // 資金援助
	str += name1 + 'が、' + name2 + 'へ' + amount + unitMoney + 'の' +
	    cName + 'を行いました。';
	break;

    case 208: // 食料援助
	str += name1 + 'が、' + name2 + 'へ' + amount + unitFood + 'の' +
	    cName + 'を行いました。';
	break;

    case 209: // 食料輸出
	str += name1 + 'が' + amount + unitFood + 'の' +
	    cName + 'を行いました。';
	break;

    case 210: // 行っただけ
	str += name1 + 'が' + cName + 'を行いました。';
	break;

    case 211: // 埋蔵金
	str += name1 + 'で' + amount + unitMoney + 'もの<B>埋蔵金</B>が発掘されました。';
	break;

    case 212: // 油田収入
	str += name1 + point + 'の' + lName + 'で' + amount + unitMoney + 'の収入がありました。';
	break;

    case 213: // 油田枯渇
	str += name1 + point + 'の' + lName + 'が<B>枯渇</B>した模様。';
	break;

    case 214: // 領土の変化
	str += name1 + point + 'の' + lName + 'は、' + name2 + 'の領地となりました。';
	break;

    case 400: // 食料不足
	str += name1 + 'の<B>食料が不足しています。</B>';
	break;

    case 401: // 火災
	str += name1 + point + 'の' + lName + 'で' + tagDis('火災') + 'が発生</B>。一帯が荒地と化しました。';
	break;

    case 402: // 広域被害で水没
	str += name1 + point + 'の' + lName + 'は水没しました。';
	break;

    case 403: // 広域被害で荒地
	str += name1 + point + 'の' + lName + 'は消し飛びました。';
	break;

    case 404: // 防衛施設自爆
	str += name1 + point + 'にある' + lName + 'の<B>自爆装置が作動！！</B>';
	break;

    case 405: // 海底が深くなる
	str += name1 + point + 'の海底がえぐられました。';
	break;

    case 406: // 怪獣動く
	str += name1 + point + 'に居た' + lName + 'が動き出した模様！！';
	break;

    case 407: // 怪獣被害
	str += name1 + point + 'の' + lName + 'が踏み荒らされました。';
	break;

    case 408: // 記念碑発射
	str += name1 + point + 'の' + lName + 'が、轟音とともに飛び立ちました。</B>';
	break;

    case 409: // 記念碑着弾
	str += point + 'に<B>何かとてつもないもの</B>が落下した模様です。</B>';
	break;

    case 410: // 地震で荒地
	str += name1 + point + 'の' + lName + 'は崩壊しました。';
	break;

    case 411: // 地震発生
	str += tagDis('地震発生！！') + '震源地は' + point + '地点！！';
	break;

    case 412: // 津波発生
	str += point + '付近で' + tagDis('津波') + 'の被害が出ています。';
	break;

    case 413: // 台風発生
	str += point + '付近を' + tagDis('台風') + 'が襲いました';
	break;

    case 414: // 飛ばされる
	str += name1 + point + 'の' + lName + 'は飛んでいきました。';
	break;

    case 415: // 流星群
	str += point + '付近を' + tagDis('流星群') + 'が襲来しました。';
	break;

    case 416: // 隕石落ちただけ
	str += name1 + point + 'の' + lName + 'に' + tagDis('隕石') + 'が落下しました。';
	break;

    case 417: // 海底抉られる
	str += name1 + point + 'の' + lName + 'に' + tagDis('隕石') + 'が落下、海底が抉られました。';
	break;

    case 418: // 海の藻屑
	str += name1 + point + 'に' + tagDis('隕石') + 'が落下、' + lName + 'は海の藻屑と消えました。';
	break;

    case 419: // 水没
	str += name1 + point + 'に' + tagDis('隕石') + 'が落下、' + lName + 'は水没しました。';
	break;

    case 420: // 巨大隕石
	str += point + 'に' + tagDis('巨大隕石') + 'が落下！！';
	break;

    case 421: // 噴火
	str += point + 'で' + tagDis('火山噴火') + '、<B>山</B>ができました。';
	break;

    case 422: // 海底が隆起
	str += name1 + point + 'の海底が隆起、' + lName + 'になりました。';
	break;

    case 423: // 火山灰
	str += name1 + point + 'の' + lName + 'に向かって溶岩流が流れ、一帯が<B>荒地</B>と化しました。';
	break;

    case 424: // 怪獣
	str += name1 + point + 'の' + lName + 'に' + tagDis('怪獣') + 'が出現。一帯が踏み荒らされました。';
	break;

    case 425: // 難民
	str += name1 + 'にどこからともなく' + amount + unitPop + 'の<B>難民</B>が漂着しました。' + name1 + 'は快く受け入れたようです。';
	break;

    case 426: // 暴動
	str += name1 + point + 'の' + lName + 'は、食料を求める住民の' + tagDis('暴動') + 'により破壊されました。';
	break;

    case 500: // ミサイル落ちたが領域外
	str += name1 + 'が' + cName + 'を行いましたが、<B>領域外の海</B>に落ちた模様です。';
	break;

    case 501: // 通常ミサイル、硬化中の怪獣にヒット
	str += name1 + 'が' + cName + 'を行い、' + name2 + point + 'の' +
	    lName + 'に命中。しかし硬化状態だっため効果がありませんでした。';
	break;

    case 502: // 通常ミサイル、怪獣にヒット
	str += name1 + 'が' + cName + 'を行い、' + name2 + point + 'の' +
	    lName + 'に命中。' + lName + 'は苦しそうに咆哮しました。';
	break;

    case 503: // 通常ミサイル、怪獣にヒット、倒れる。
	str += name1 + 'が' + cName + 'を行い、' + name2 + point + 'の' +
	    lName + 'に命中。' + lName + 'は力尽き、倒れました。';
	break;

    case 504: // 怪獣の残骸が売れる
	str += lName + 'の残骸には、' + amount + unitMoney +
	    'の値が付きました。';
	break;

    case 505: // ミサイル、海等に落ちて効果なし
	str += name1 + 'が' + cName + 'を行いましたが、' + name2 + point + 'の' +
	    lName + 'に落ちました。';
	break;

    case 506: // ミサイル着弾。海になる。
	str += name1 + 'が' + cName + 'を行い、' + name2 + point + 'の' +
	    lName + 'に着弾、' + lName + 'は海の藻屑と消えました。';
	break;

    case 507: // ミサイル着弾。荒地になる。
	str += name1 + 'が' + cName + 'を行い、' + name2 + point + 'の' +
	    lName + 'に着弾、一帯が荒地と化しました。';
	break;

    case 508: // ミサイル着弾。深くなる。
	str += name1 + 'が' + cName + 'を行い、' + name2 + point + 'の' +
	    lName + 'に着弾、海底がえぐられました。';
	break;

    case 509: // ミサイル着弾。浅瀬になる。
	str += name1 + 'が' + cName + 'を行い、' + name2 + point + 'の' +
	    lName + 'に着弾、一帯が水没しました。';
	break;

    case 510: // 防衛施設で防御
	str += name1 + 'が' + cName + 'を行いましたが、' + name2 + point +
	    'の上空で空中爆破されました。';
	break;

    case 600: // 受賞
	str += name1 + 'が<B>' + prizeName[amount] + '</B>を受賞しました。';
	break;

    default:
        str += 'ログ番号' + kind + 'は定義されていません。';
	break;
    }
    return str + '</NOBR><BR>';
}

// 発見ログ
function hisPrint() {
    // 発見ログ部分
    var str = tagHeader('<H1>発見の記録</H1>');
    var i;
    for(i = hisData.length - 1; i >= 0; i--) {
	var l = hisData[i];
	if(l.length != 4) {
	    continue;
	}
	var turn = l[0];
	str += '<NOBR>' + tagNumber(turn + 'ターン:');
	var kind = l[1];
	var name = tagName(l[2] + '島');
	var name2 = tagName(l[3] + '島');
	switch(kind) {
	case 0: // 発見
	    str += name + 'が発見される。';
	    break;

	case 1: // 放棄
	    str += name + 'が放棄され、忘れ去られる。';
	    break;

	case 2: // 無人化
	    str += name + 'から人がいなくなり、忘れ去られる。';
	    break;

	case 3: // 名前変更
	    str += name + '、島の名前を' + name2 + 'に変更する。';
	    break;
	}
	str += '</NOBR><BR>';
    }

    return str;
}

// 経験値からレベル算出
function expToLevel(elist, point) {
    var i;
    var level = 1;
    for(i = 0; i < elist.length; i++) {
	if(point >= elist[i]) {
	    level++;
	}
    }
    return level;
}

// 陸地の名前
function landName(land) {
    switch(land) {
    case 0: return '海';
	case 1: return '浅瀬';
	case 2: return '海底油田';
	case 10: return '荒地';
	case 20: return '平地';
	case 21: return '村';
	case 22: return '町';
	case 23: return '都市';
	case 30: return '森';
	case 40: return '農場';
	case 50: return '工場';
	case 60: return 'ミサイル基地';
	case 70: return '防衛施設';
	case 71: return 'ハリボテ';
	case 80: return '山';
	case 100: return '海底基地';
	default:
	    if(land < 300) {
		// 怪獣
		return '怪獣' + monsterName[land - 200];
	    } else {
		// 記念碑
		return monumentName[land - 300];
	    }
	}
}

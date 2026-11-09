#!/usr/local/bin/perl
# ↑はサーバーに合わせて変更して下さい。
# perl5用です。

#----------------------------------------------------------------------
# 箱庭諸島 ver2.30
# メインスクリプト(ver1.02)
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
# 各種設定値
# (これ以降の部分の各設定値を、適切な値に変更してください)
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# 以下、必ず設定する部分
#----------------------------------------------------------------------

# このファイルを置くディレクトリ
# my($baseDir) = 'http://場所/hako-mente.cgi';
#
# 例)
# http://cgi2.bekkoame.ne.jp/cgi-bin/user/u5534/hakoniwa/hako-main.cgi
# として置く場合、
# my($baseDir) = 'http://cgi2.bekkoame.ne.jp/cgi-bin/user/u5534/hakoniwa';
# とする。最後にスラッシュ(/)は付けない。

my($baseDir) = 'http://www.xxxxxxxx/cgi-bin/hako';

# 画像ファイルを置くディレクトリ
# my($imageDir) = 'http://場所/hako-mente.cgi';
my($imageDir) = 'http://www.xxxxxxxx/cgi-bin/hako/hakoimg';

# jcode.plの位置

# my($jcode) = '/usr/libperl/jcode.pl';  # ベッコアメの場合
# my($jcode) = './jcode.pl';             # 同じディレクトリに置く場合
my($jcode) = './jcode.pl';

# マスターパスワード
# このパスワードは、すべての島のパスワードを代用できます。
# 例えば、「他の島のパスワード変更」等もできます。
my($masterPassword) = 'uhusnuvnurkanjhfh';

# 特殊パスワード
# このパスワードで「名前変更」を行うと、その島の資金、食料が最大値になります。
# (実際に名前を変える必要はありません。)
$HspecialPassword = 'uhusnuvnurkanjhfhmax';

# 首都パスワード
# このパスワードで「名前変更」を行うと、その島の首都名が変わります。
# (実際に名前を変える必要はありません。)
$HshutoPassword = 'uhusnuvnurkanjhfhshuto';

# IPパスワード
# このパスワードで「名前変更」を行うと、その島のIPが変わります。(IPがおかしくなった時に)
# (実際に名前を変える必要はありません。)
$HipPassword = 'uhusnuvnurkanjhfhip';

# おみやげパスワード
# このパスワードで「名前変更」を行うと、その島のおまもりが増えます。
# (実際に名前を変える必要はありません。)
$HomamoriPassword = 'uhusnuvnurkanjhfhomiya';

# ステータスいじりパスワード
# このパスワードで「名前変更」を行うと、オーナー名に入力した任意のステータスをどんな名前に変えますか？に変更できます。
# (実際に名前を変える必要はありません。)
$HijiriPassword = 'uhusnuvnurkanjhfhiji';


# アンケート関係
# 使う(1)、使わない(0)
$AnkeitoOnOff = 0;
# アンケートの説明
$AnkeitoSetumei = "<FONT COLOR=hotpink>◎今回、補助金を使用し、４京円(41111兆円)でお守りが落札されました。
<br>　 補助金は、比較的デメリットもなくに無制限に貯めることができ、
<br>　 ハコオクに優位に使用できることは、ゲームバランス的にどうなのか？
<br>　 という意見が寄せられてきました。
<br>　 皆様のご意見をお聞かせくださいませ。</font><br>";
# 質問
$AnkeitoShitumon0 = "ハコオクと補助金の対策についてどう思いますか？";
$AnkeitoShitumon1 = "補助金に上限をつけてみる(個人的には、上限をつけたくなかったりする。。)";
$AnkeitoShitumon2 = "高額落札ランキングの賞品制度をいじってみる";
$AnkeitoShitumon3 = "HT職場を確保しにくくする(HT企業・改の修正)";
$AnkeitoShitumon4 = "補助金の、維持に手数料かかるよ制度";
$AnkeitoShitumon5 = "その他、別の選択肢で再アンケート希望でござるよ";


# 管理者名
my($adminName) = '管理人';

# 管理者のメールアドレス
my($email) = 'めあど';

# 掲示板アドレス
my($bbs) = '掲示板';

# ホームページのアドレス
my($toppage) = 'http://';

# ディレクトリのパーミッション
# 通常は0755でよいが、0777、0705、0704等でないとできないサーバーもあるらしい
$HdirMode = 0755;

# データディレクトリの名前
# ここで設定した名前のディレクトリ以下にデータが格納されます。
# デフォルトでは'data'となっていますが、セキュリティのため
# なるべく違う名前に変更してください。
$HdirName = 'data';

# データの書き込み方

# ロックの方式
# 1 ディレクトリ
# 2 システムコール(可能ならば最も望ましい)
# 3 シンボリックリンク
# 4 通常ファイル(あまりお勧めでない)
my($lockMode) = 2;

# (注)
# 4を選択する場合には、'key-free'という、パーミション666の空のファイルを、
# このファイルと同位置に置いて下さい。

#----------------------------------------------------------------------
# 必ず設定する部分は以上
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# 以下、好みによって設定する部分
#----------------------------------------------------------------------
#----------------------------------------
# ゲームの進行やファイルなど
#----------------------------------------
# 1ターンが何秒か
$HunitTime = 21600; # 6時間

# 異常終了基準時間
# (ロック後何秒で、強制解除するか)
my($unlockTime) = 12;

# 島の最大数
$HmaxIsland = 30;

# トップページに表示するログのターン数
$HtopLogTurn = 1;

# ログファイル保持ターン数
$HlogMax = 8; 

# バックアップを何ターンおきに取るか
$HbackupTurn = 12;

# バックアップを何回分残すか
$HbackupTimes = 1;

# 発見ログ保持行数
$HhistoryMax = 20;

# Hakoniwa Cupログ保持行数
$HhcMax = 20;

# 放棄コマンド自動入力ターン数
$HgiveupTurn = 24;

# コマンド入力限界数
# (ゲームが始まってから変更すると、データファイルの互換性が無くなります。)
$HcommandMax = 40;

# 攻撃系、援助系、怪獣出現から島が守られる基準人口
# （この人口を超えるまで開発しかできない）
$HguardPop = 500; # ５万人

# ローカル掲示板行数を使用するかどうか(0:使用しない、1:使用する)
$HuseLbbs = 1;

# ローカル掲示板行数
$HlbbsMax = 15;

# ローカル掲示板への匿名発言を許可するか(0:禁止、1:許可)
$HlbbsAnon = 0;

# ローカル掲示板の発言に発言者の名前を表示するか(0:表示しない、1:表示する)
$HlbbsSpeaker = 1;

# ローカル掲示板のログを移行するか(0:移行しない、1:移行する)
# (稼働中の掲示板ログを極秘発言対応に移行することができます)
$HlbbsOldToNew = 1;

# 他島のローカル掲示板に発言するための費用(0:無料)
$HlbbsMoneyPublic =   0; # 公開
$HlbbsMoneySecret = 10000; # 極秘

# 島の大きさ　
# (変更できないかも)12もしくは20で
$HislandSize = 12;

# 他人から資金を見えなくするか
# 0 見えない
# 1 見える
# 2 100の位で四捨五入
$HhideMoneyMode = 2;

# パスワードの暗号化(0だと暗号化しない、1だと暗号化する)
my($cryptOn) = 1;

# デバッグモード(1だと、「ターンを進める」ボタンが使用できる)
$Hdebug = 0;

# 画像のローカル設定の説明ページ
$imageExp = 'e.html';

# 怪獣出現データをどこに保存するか (新規ゲームなら 1 がお勧め)
#  0: monslive.dat に保存 (稼働中のゲームはこちらで！)
#  1: hakojima.dat に保存 (稼働中のゲームでは禁止！ データが壊れます)
$HnewGame = 1;

$viewFirst = 0; # 最初に表示される島
$viewNumber = 20; # 表示する数# CGIの読みこみ

# トップページでアクセスログをとるか？(0:とらない、1:とる)
$HtopAxes = 1;
# 1にした場合、以下を設定
# ログファイル名
$HaxesLogfile = './axes-hako.log';
# 最大記録件数
$HaxesMax = 500;

# 負荷計測するか？(0:しない、1:する)
$Hperformance = 1;

# 平和系モード？(0:OFF、1:ON)
$lovePeace = 1;

# アナザーモード？(0:OFF、1:ON)
$anothermood = 0;

# ハコオク何連続１位で賞品を出すか？
$aucshouhin = 5;

# ハコオクで何回、連続１位賞品をもらえば殿堂入りとするか？
$aucdendou = 3;

# ＩＰ重複登録自動カット？(0:OFF、1:ON)…登録時に既存の島とかぶるＩＰは登録できなくなります。
$IPcut = 1;

#----------------------------------------
# 資金、食料などの設定値と単位
#----------------------------------------
# 初期資金
$HinitialMoney = 2000;

# 初期食料
$HinitialFood = 200;

# お金の単位
$HunitMoney = '億円';

# 食料の単位
$HunitFood = '00トン';

# 人口の単位
$HunitPop = '00人';

# 広さの単位
$HunitArea = '00万坪';

# 木の数の単位
$HunitTree = '00本';

# 木の単位当たりの売値
$HtreeValue = 5;

# 名前変更のコスト
$HcostChangeName = 500;

# 人口1単位あたりの食料消費料
$HeatenFood = 0.2;

# 怪獣の数の単位
$HunitMonster = '匹';

#----------------------------------------
# 基地の経験値
#----------------------------------------
# 経験値の最大値
$HmaxExpPoint = 200; # ただし、最大でも255まで

# レベルの最大値
my($maxBaseLevel) = 5;  # ミサイル基地
my($maxSBaseLevel) = 4; # 海底基地

# 経験値がいくつでレベルアップか
my(@baseLevelUp, @sBaseLevelUp);
@baseLevelUp = (20, 60, 120, 200); # ミサイル基地
@sBaseLevelUp = (50, 100, 200);         # 海底基地


# 島主の家のランク
$HouseLevel1  = 15000; # 簡易住宅
$HouseLevel2  = 20000; # 住宅
$HouseLevel3  = 25000; # 高級住宅
$HouseLevel4  = 30000; # 豪邸
$HouseLevel5  = 35000; # 大豪邸
$HouseLevel6  = 40000; # 高級豪邸
$HouseLevel7  = 45000; # 城
$HouseLevel8  = 50000; # 巨城
$HouseLevel9  = 55000; # 黄金城


#----------------------------------------
# 防衛施設の自爆
#----------------------------------------
# 怪獣に踏まれた時自爆するなら1、しないなら0
$HdBaseAuto = 1;

#----------------------------------------
# 災害
#----------------------------------------
# 通常災害発生率(確率は0.1%単位)
$HdisEarthquake = 5;  # 地震
$HdisTsunami    = 5; # 津波
$HdisTyphoon    = 5; # 台風
$HdisMeteo      = 5; # 隕石
$HdisHugeMeteo  = 2;  # 巨大隕石
$HdisEruption   = 5; # 噴火
$HdisFire       = 5; # 火災
$HdisMaizo      = 10; # 埋蔵金

# 地盤沈下
$HdisFallBorder = 350; # 安全限界の広さ(Hex数)
$HdisFalldown   = 15; # その広さを超えた場合の確率

# 怪獣
$HdisMonsBorder1 = 5000; # 人口基準1(怪獣レベル1)
$HdisMonsBorder2 = 7500; # 人口基準2(怪獣レベル2)
$HdisMonsBorder3 = 9000; # 人口基準3(怪獣レベル3)
$HdisMonsBorder4 = 10000; # 人口基準4(怪獣レベル4)
$HdisMonster     = 1;    # 単位面積あたりの出現率(0.01%単位)

# 種類
$HmonsterNumber  = 31; 

# 各基準において出てくる怪獣の番号の最大値
$HmonsterLevel1  = 4; # サンジラまで    
$HmonsterLevel2  = 8; # いのらゴーストまで
$HmonsterLevel3  = 12; # キングいのらまで(全部)
$HmonsterLevel4  = 23; # キングいのらまで(全部)

$HmonsterDefence = 500; #怪獣がミサイルを叩き落す確率

# 名前
@HmonsterName = 
    (
     '人造メカいのら',     # 0(人造)
     '怪獣いのら',         # 1
     '怪獣サンジラ',       # 2
     '怪獣レッドいのら',   # 3
     '怪獣ダークいのら',   # 4
     '霊獣いのらゴースト', # 5
     '怪獣クジラ',         # 6
     '怪獣キングいのら',   # 7
     '古獣王蟲',           # 8
     '硬獣めたはむ',       # 9
     '怪獣バリモア',       # 10
     '奇獣スライム',       # 11
     '珍獣はねはむ',       # 12
     '天使ミカエル',       # 13
     'スライムレジェンド', # 14
     '魔獣レイジラ',       # 15
     '魔獣クイーンいのら', # 16
     '人造怪獣f02',        # 17
     '天使ウリエル',       # 18
     '魔術師アールヴ',     # 19
     '堕天使イセリア',     # 20
     '魔王サタン',         # 21
     'アイススコーピオン', # 22
     'unknown',            # 23
     '怪獣キングいのら',   # 24
     '怪獣キングいのら',   # 25
     '怪獣キングいのら',   # 26
     '怪獣キングいのら',   # 27
     'マスコットいのら',   # 28
     '神獣テトラ',         # 29
     '超神獣テトラ'        # 30
);

# 最低体力、体力の幅、特殊能力、経験値、死体の値段
@HmonsterBHP     = ( 2, 1, 1, 3, 2, 1, 4, 7, 6, 5, 7, 3, 5,10, 7, 9, 9, 8, 9, 2, 7,10, 9,10, 1, 1, 1, 1, 0, 5, 0);
@HmonsterDHP     = ( 0, 2, 2, 2, 2, 0, 2, 2, 0, 2, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1, 1, 1, 1, 0, 0, 0);
@HmonsterSpecial = ( 0, 0, 3, 5, 1, 2, 4, 0, 1, 8, 5, 0, 2, 0, 8, 8, 5, 2, 0, 1, 7, 0, 2, 7, 1, 1, 1, 1, 0, 6, 0);
@HmonsterExp     = ( 5, 5, 7,12,15,10,20,30,45,40,35, 5,40,99,70,55,60,85,90,95, 0,80,40,99, 1, 1, 1, 1, 0, 7,99);
@HmonsterValue   = ( 0, 400, 500, 1000, 800, 300, 1500, 5555, 2500, 3500, 3000, 100, 3500, 99999, 27000, 10000, 12000, 48000, 80000, 95000, 85000, 0, 4000, 99999, 1, 1, 1, 1, 1, 2000, 200000);

# 特殊能力の内容は、
# 0 特になし
# 1 足が速い(最大2歩あるく)
# 2 足がとても速い(最大何歩あるくか不明)
# 3 奇数ターンは硬化
# 4 偶数ターンは硬化
# 5 ミサイル迎撃
# 6 怪獣を攻撃
# 7 衝撃波１
# 8 ランダムなターンに硬化
# 9 アイスストーム

# 画像ファイル
@HmonsterImage =
    (
     'monster7.gif',
     'monster0.gif',
     'monster5.gif',
     'monster1.gif',
     'monster2.gif',
     'monster8.gif',
     'monster6.gif',
     'monster3.gif',
     'monster18.gif',
     'monster25.gif',
     'monster13.gif',
     'monster14.gif',
     'monster16.gif',
     'monster17.gif',
     'monster19.gif',
     'monster22.gif',
     'monster21.gif',
     'f02.gif',
     'monster23.gif',
     'monster24.gif',
     'monster26.gif',
     'monster27.gif',
     'monster29.gif',
     'monster31.gif',
     'monster3.gif',
     'monster3.gif',
     'monster3.gif',
     'monster3.gif',
     'monster30.gif',
     'monster10.gif',
     'monster28.gif'
     );

# 画像ファイルその2(硬化中)
@HmonsterImage2 =
    ('', '', 'monster4.gif', '', '', '', 'monster4.gif', '', '', 'monster25.gif', '', '', '', '', 'monster20.gif', 'monster4.gif', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '');


#----------------------------------------
# 油田
#----------------------------------------
# 油田の収入
$HoilMoney = 2500;

# 油田の枯渇確率
$HoilRatio = 80;

#----------------------------------------
# 記念碑
#----------------------------------------
# 何種類あるか
$HmonumentNumber = 70;

# 名前
@HmonumentName = 
    (
     'モノリス',      # 0
     '聖樹', 
     '戦いの碑',
     'ラスカル', 
     '棺桶', 
     'ヨーゼフ', 
     'くま', 
     'くま', 
     'くま', 
     '雪だるま', 
     'モアイ',        # 10
     '地球儀', 
     'バッグ', 
     'ごみ箱', 
     'ダークいのら像', 
     'テトラ像', 
     'はねはむ像', 
     'ロケット', 
     'ピラミッド', 
     'アサガオ', 
     'バラ',          # 20
     'バラ', 
     'パンジー', 
     '仙人掌', 
     '仙人掌', 
     '魔方陣', 
     '神殿', 
     '神社', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱',         # 30
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱',          # 40
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱',          # 50
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱',          # 60
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱', 
     'ごみ箱',          # 70
     'ごみ箱', 
     'ごみ箱', 
     'ツクシ', 
     '闇石', 
     '地石', 
     '氷石', 
     '風石', 
     '炎石', 
     '光石', 
     '卵',              # 80
     '卵', 
     '卵', 
     '卵', 
     '古代遺跡', 
     'Millenniumクリスマスツリー', 
     '壊れた侵略者', 
     '王蟲の脱け殻',
     '桜',
     '向日葵', 
     '銀杏',          # 90
     'クリスマスツリー2002',
     '雪うさぎ',
     '幸福の女神像',
     '豚の香取くん',
     'サンタクロース',
     '人工炎石',
     '人工氷石',
     '人工地石',
     '人工風石',
     '人工光石',
     '人工闇石',
     'モノリス'

    );

# 画像ファイル
@HmonumentImage = 
    (
     'monument0.gif',     # 0
     'monument5.gif',
     'monument3.gif',
     'monument12.gif',
     'monument11.gif',
     'monument13.gif',
     'monument16.gif',
     'monument15.gif',
     'monument14.gif',
     'monument17.gif',
     'monument18.gif',     # 10
     'monument19.gif',
     'monument20.gif',
     'monument21.gif',
     'monument4.gif',
     'monument22.gif',
     'monument23.gif',
     'monument27.gif',
     'monument29.gif',
     'monument30.gif',
     'monument31.gif',     # 20
     'monument32.gif',
     'monument33.gif',
     'monument34.gif',
     'monument35.gif',
     'monument40.gif',
     'monument46.gif',
     'monument47.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',     # 30
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',     # 40
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',     # 50
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',     # 60
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',
     'monument21.gif',     # 70
     'monument21.gif',
     'monument21.gif',
     'monument63.gif',
     'monument53.gif',
     'monument52.gif',
     'monument48.gif',
     'monument49.gif',
     'monument50.gif',
     'monument51.gif',
     'monument41.gif',     # 80
     'monument42.gif',
     'monument43.gif',
     'monument44.gif',
     'monument45.gif',
     'monument9.gif',
     'monument24.gif',
     'monument25.gif',
     'monument26.gif',
     'monument28.gif',
     'monument36.gif',     # 90
     'monument37.gif',
     'monument38.gif',
     'monument54.gif',
     'monument55.gif',
     'monument56.gif',
     'monument57.gif',
     'monument58.gif',
     'monument59.gif',
     'monument60.gif',
     'monument61.gif',
     'monument62.gif',
     'monument0.gif'
     );

#----------------------------------------
# 船
#----------------------------------------
# 何種類あるか
$HfuneNumber = 12;

# 名前
@HfuneName = 
    (
     '漁船・改', 
     '小型漁船', 
     '中型漁船', 
     '海底探査船', 
     '帆船', 
     '大型漁船', 
     '高速漁船', 
     '海底探査船・改', 
     '豪華客船TITANIC', 
     '戦艦RENAS', 
     '戦艦ERADICATE', 
     '漁船MASTER', 
     'モノリス', 
     'モノリス', 
     'モノリス', 
     'モノリス', 
     'モノリス', 
     'モノリス', 
     'モノリス', 
     '戦艦ERADICATE・改'
    );

@HfuneSpecial = ( 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 5, 0);
# 特殊能力の内容は、
# 0 特になし
# 1 足が速い(最大2歩あるく)
# 2 足がとても速い(最大何歩あるくか不明)

# 画像ファイル
@HfuneImage = 
    (
     'fune1.gif',
     'fune1.gif',
     'fune2.gif',
     'fune5.gif',
     'fune4.gif',
     'fune3.gif',
     'fune6.gif',
     'fune5.gif',
     'fune7.gif',
     'fune8.gif',
     'fune9.gif',
     'fune10.gif',
     'monument0.gif',
     'monument0.gif',
     'monument0.gif',
     'monument0.gif',
     'monument0.gif',
     'monument0.gif',
     'monument0.gif',
     'fune11.gif'
     );

#----------------------------------------
# 賞関係
#----------------------------------------
# ターン杯を何ターン毎に出すか
$HturnPrizeUnit = 100;

# 賞の名前
$Hprize[0] = 'ターン杯';
$Hprize[1] = '繁栄賞';
$Hprize[2] = '超繁栄賞';
$Hprize[3] = '究極繁栄賞';
$Hprize[4] = '平和賞';
$Hprize[5] = '超平和賞';
$Hprize[6] = '究極平和賞';
$Hprize[7] = '災難賞';
$Hprize[8] = '超災難賞';
$Hprize[9] = '究極災難賞';

#----------------------------------------
# 外見関係
#----------------------------------------
# <BODY>タグのオプション
my($htmlBody) = 'BGCOLOR="lemonchiffon"';

# ゲームのタイトル文字
$Htitle = '☆Hakoniwa R.A.☆';

# タグ
# タイトル文字
$HtagTitle_ = '<FONT SIZE=7 COLOR="#8888ff">';
$H_tagTitle = '</FONT>';

# H1タグ用
$HtagHeader_ = '<FONT COLOR="#4444ff">';
$H_tagHeader = '</FONT>';

# 大きい文字
$HtagBig_ = '<FONT SIZE=5>';
$H_tagBig = '</FONT>';

# 島の名前など
$HtagName_ = '<FONT COLOR="#a06040"><B>';
$H_tagName = '</B></FONT>';

# 薄くなった島の名前
$HtagName2_ = '<FONT COLOR="#808080"><B>';
$H_tagName2 = '</B></FONT>';

# 順位の番号など
$HtagNumber_ = '<FONT COLOR="#800000"><B>';
$H_tagNumber = '</B></FONT>';

# 順位表における見だし
$HtagTH_ = '<FONT COLOR="#C00000"><B>';
$H_tagTH = '</B></FONT>';

# toto表における見だし
$HtagtTH_ = '<FONT COLOR="royalblue"><B>';
$H_tagtTH = '</B></FONT>';

# 開発計画の名前
$HtagComName_ = '<FONT COLOR="#d08000"><B>';
$H_tagComName = '</B></FONT>';

# 災害
$HtagDisaster_ = '<FONT COLOR="#ff0000"><B>';
$H_tagDisaster = '</B></FONT>';

# ローカル掲示板、観光者の書いた文字
$HtagLbbsSS_ = '<FONT COLOR="#0000ff"><B>';
$H_tagLbbsSS = '</B></FONT>';

# ローカル掲示板、島主の書いた文字
$HtagLbbsOW_ = '<FONT COLOR="#ff0000"><B>';
$H_tagLbbsOW = '</B></FONT>';

# 通常の文字色(これだけでなく、BODYタグのオプションもちゃんと変更すべし
$HnormalColor = '#000000';

# 順位表、セルの属性
$HbgTitleCell   = 'BGCOLOR="LAVENDER"';       # 順位表見出し
$HbgNumberCell  = 'BGCOLOR="LAVENDER"';       # 順位表順位
$HbgNameCell    = 'BGCOLOR="LAVENDERBLUSH"';  # 順位表島の名前
$HbgInfoCell    = 'BGCOLOR="LIGHTPINK"';      # 順位表島の情報
$HbgCommentCell = 'BGCOLOR="LAVENDER"';       # 順位表コメント欄
$HbgInputCell   = 'BGCOLOR="LAVENDER"';       # 開発計画フォーム
$HbgMapCell     = 'BGCOLOR="LAVENDER"';       # 開発計画地図
$HbgCommandCell = 'BGCOLOR="LAVENDER"';       # 開発計画入力済み計画
$HbgPoinCell    = 'BGCOLOR="MOCCASIN"';       # Point欄
$HbgTotoCell    = 'BGCOLOR="WHITE"';          # toto欄

#----------------------------------------------------------------------
# 好みによって設定する部分は以上
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# これ以降のスクリプトは、変更されることを想定していませんが、
# いじってもかまいません。
# コマンドの名前、値段などは解りやすいと思います。
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# 各種定数
#----------------------------------------------------------------------
# このファイル
$HthisFile = "$baseDir/hako-main.cgi";

# 地形番号
$HlandSea      = 0;  # 海
$HlandWaste    = 1;  # 荒地
$HlandPlains   = 2;  # 平地
$HlandTown     = 3;  # 町系
$HlandForest   = 4;  # 森
$HlandFarm     = 5;  # 農場
$HlandFactory  = 6;  # 工場
$HlandBase     = 7;  # ミサイル基地
$HlandDefence  = 8;  # 防衛施設
$HlandMountain = 9;  # 山
$HlandMonster  = 10; # 怪獣
$HlandSbase    = 11; # 海底基地
$HlandOil      = 12; # 海底油田
$HlandMonument = 13; # 記念碑
$HlandHaribote = 14; # ハリボテ
$HlandSeacity  = 15; # 海底都市
$HlandPark     = 16; # 遊園地
$HlandMinato   = 17; # 港
$HlandFune     = 18; # 船舶
$HlandMine     = 19; # 地雷
$HlandNursery  = 20; # 養殖場
$HlandKyujo    = 21; # 野球場
$HlandUmiamu   = 22; # 海あみゅ
$HlandFoodim   = 23; # 食物研究所
$HlandProcity  = 24; # 防災都市
$HlandGold     = 25; # 金山
$HlandSeki     = 26; # 関所
$HlandRottenSea= 27; # 腐海
$HlandNewtown  = 28; # ニュータウン
$HlandBigtown  = 29; # 現代都市
$HlandSeatown  = 30; # 海底ニュー
$HlandFarmchi  = 31;
$HlandFarmpic  = 32;
$HlandFarmcow  = 33;
$HlandCollege  = 34;
$HlandFrocity  = 35; # 海上都市
$HlandSunahama = 36; # 砂浜
$HlandOnsen    = 37; # 温泉
$HlandHouse    = 38; # 島主の家
$HlandShuto    = 39; # 首都
$HlandUmishuto = 40; # 海首都
$HlandIce      = 41; # 氷河
$HlandRizort   = 42; # リゾート地
$HlandBettown  = 43; # 輝ける都市
$HlandKyujokai = 44; # 多目的スタジアム
$HlandBigRizort= 45; # リゾート宿泊施設
$HlandHTFactory= 46; # ハイテク企業
$HlandTaishi   = 47; # 大使館
$HlandPlains2  = 48; # 開発予定地
$HlandYakusho  = 49; # 島役所
$HlandKura     = 50; # 倉庫
$HlandKuraf    = 51; # 倉庫Food
$HlandTrain    = 52; # 電車系
$HlandEneAt    = 53; # 電車系
$HlandEneFw    = 54; # 電車系
$HlandEneWt    = 55; # 電車系
$HlandConden   = 56; # コンデンサ系
$HlandConden2  = 57; # コンデンサ系
$HlandEneWd    = 58; # 電力系
$HlandEneBo    = 59; # 電力系
$HlandEneSo    = 60; # 電力系
$HlandEneCs    = 61; # 電力系
$HlandFoodka   = 62; # 食品加工場
$HlandKajino   = 63; # カジノ
$HlandConden3  = 64; # コンデンサ系
$HlandConden4  = 65; # コンデンサ系
$HlandSkycity  = 66; # 空中都市系
$HlandUmicity  = 67; # 海都市系
$HlandZoo      = 68; # 動物園系
$HlandSHTF     = 69; # ハイテク企業・改
$HlandOWNF     = 70; # 島営企業

# コマンド
$HcommandTotal = 90; # コマンドの種類

# 計画番号の設定
# 整地系
$HcomPrepare  = 01; # 整地
$HcomPrepare2 = 02; # 地ならし
$HcomReclaim  = 03; # 埋め立て
$HcomDestroy  = 04; # 掘削
$HcomSellTree = 05; # 伐採
$HcomMinato   = 06; # 港開発
$HcomFune     = 07; # 造船
$HcomSeki     = 10; # 関所建設

# 作る系
$HcomPlant    = 11; # 植林
$HcomFarm     = 12; # 農場整備
$HcomFactory  = 13; # 工場建設
$HcomMountain = 14; # 採掘場整備
$HcomBase     = 15; # ミサイル基地建設
$HcomDbase    = 16; # 防衛施設建設
$HcomSbase    = 17; # 海底基地建設
$HcomMonument = 18; # 記念碑建造
$HcomHaribote = 19; # ハリボテ設置
$HcomSeacity  = 20; # 海底都市建設
$HcomMonbuy   = 21; # 怪獣購入
$HcomMonbuyt  = 22; # tetora購入
$HcomPark     = 23; # 遊園地建設
$HcomMine     = 24; # 地雷設置
$HcomNursery  = 25; # 養殖場設置
$HcomKyujo    = 26; # 野球場
$HcomUmiamu   = 27; # 海あみゅ建設
$HcomFoodim   = 28; # 食物研究所建設
$HcomProcity  = 29; # 防災化
$HcomBoku     = 30; # 僕の引越し
$HcomNewtown  = 70; # ニュータウン建設
$HcomBigtown  = 71; # 現代都市建設
$HcomSeatown  = 72; # 海底ニュー建設
$HcomFarmcpc  = 73; # 牧場建設
$HcomCollege  = 74; # 大学建設
$HcomOnsen    = 75; # 温泉掘削
$HcomReclaim2 = 76; # 埋め立て
$HcomHouse    = 77; # 島主の家
$HcomRizort   = 78; # リゾート地
$HcomBettown  = 79; # 輝ける都市
$HcomGivefood = 100; # エサをあげる
$HcomKai      = 101; # 改装
$HcomHTget    = 102; # ハイテクゲット
$HcomReclaim3 = 103; # 埋め立て２
$HcomDestroy3 = 104; # 掘削２
$HcomYoyaku   = 105; # 開発予定
$HcomYakusho  = 106; # 役所
$HcomKura     = 107; # 倉庫
$HcomKura2    = 108; # 倉庫２
$HcomKuraf    = 109; # 倉庫Food
$HcomTrain    = 110; # 電車系
$HcomEneAt    = 111; # 電車系
$HcomEneFw    = 112; # 電車系
$HcomEneWt    = 113; # 電車系
$HcomConden   = 114; # コンデンサ系
$HcomEneWd    = 115; # 電力系
$HcomEneBo    = 116; # 電力系
$HcomEneSo    = 117; # 電力系
$HcomEneCs    = 118; # 電力系
$HcomBoku2    = 119; # 僕の引越し２
$HcomEneNF    = 120; # 電力系
$HcomZoo      = 121; # 動物園系
$HcomAuction  = 122; # オークション

# 発射系
$HcomMissileNM   = 31; # ミサイル発射
$HcomMissilePP   = 32; # PPミサイル発射
$HcomMissileST   = 33; # STミサイル発射
$HcomMissileLD   = 34; # 陸地破壊弾発射
$HcomSendMonster = 35; # 怪獣派遣
$HcomMissileSPP  = 36; # SPPミサイル発射
$HcomMissileSS   = 37; # 核ミサイル発射
$HcomMissileLR   = 38; # 地形隆起弾発射
$HcomEisei       = 39; # 人工衛星発射
$HcomEiseimente  = 40; # 人工衛星メンテ
$HcomEiseiLzr    = 80; # 人工衛星レーザー
$HcomEiseiAtt    = 81; # 人工衛星破壊
$HcomTaishi      = 82; # 大使館発射
$HcomMagic       = 83; # 魔術師発射

# 運営系
$HcomDoNothing  = 41; # 資金繰り
$HcomSell       = 42; # 食料輸出
$HcomMoney      = 43; # 資金援助
$HcomFood       = 44; # 食料援助
$HcomPropaganda = 45; # 誘致活動
$HcomGiveup     = 46; # 島の放棄
$HcomEneGive    = 47; # 電力援助

# 自動入力系
$HcomAutoPrepare  = 61; # フル整地
$HcomAutoPrepare2 = 62; # フル地ならし
$HcomAutoDelete   = 63; # 全コマンド消去
$HcomAutoReclaim  = 64; # 浅瀬埋め立て
$HcomAutoDestroy  = 65; # 浅瀬掘削
$HcomAutoSellTree = 66; # 伐採
$HcomAutoForestry = 67; # 伐採と植林
$HcomAutoYoyaku   = 68; # 開発予定
$HcomAutoUchuste  = 69; # 宇宙ステ

$HcomIjiri        = 60; # いじりコマンド

# 順番
@HcomList =
    ($HcomHouse, $HcomBettown, $HcomKai, $HcomBoku2, $HcomPrepare, $HcomSell, $HcomPrepare2, $HcomYoyaku, $HcomReclaim, $HcomReclaim2, $HcomReclaim3, $HcomDestroy, $HcomDestroy3, $HcomOnsen,
     $HcomSellTree, $HcomPlant, $HcomEneWd, $HcomEneWt, $HcomEneFw, $HcomEneAt, $HcomEneBo, $HcomEneSo, $HcomEneCs, $HcomEneNF, $HcomConden, $HcomFarm, $HcomFoodim, $HcomFarmcpc, $HcomFactory, $HcomHTget, $HcomMountain, $HcomNursery, $HcomCollege,
     $HcomPark, $HcomKyujo, $HcomUmiamu, $HcomZoo, $HcomRizort, $HcomBase, $HcomDbase, $HcomSbase, $HcomSeacity,
     $HcomMonument, $HcomMonbuy, $HcomMonbuyt, $HcomHaribote, $HcomMine,
     $HcomMinato, $HcomFune, $HcomProcity, $HcomNewtown, $HcomBigtown, $HcomSeatown, $HcomBoku, $HcomSeki, $HcomYakusho, $HcomKura, $HcomKuraf, $HcomKura2, $HcomTrain,
     $HcomEisei, $HcomEiseimente, $HcomTaishi, $HcomMagic,
     $HcomMissileNM, $HcomMissilePP, $HcomMissileSPP,
     $HcomMissileST, $HcomMissileLD, $HcomMissileLR, $HcomMissileSS, $HcomEiseiLzr, $HcomEiseiAtt, $HcomSendMonster, $HcomDoNothing,
     $HcomMoney, $HcomFood, $HcomEneGive, $HcomPropaganda, $HcomGiveup, $HcomGivefood,
     $HcomAutoReclaim, $HcomAutoDestroy, $HcomAutoSellTree, $HcomAutoForestry,
     $HcomAutoPrepare, $HcomAutoPrepare2, $HcomAutoYoyaku, $HcomAutoUchuste, $HcomAutoDelete, $HcomAuction, $HcomIjiri);

# 計画の名前と値段
$HcomName[$HcomHouse]        = '自宅建設/税率変更';
$HcomCost[$HcomHouse]        = 18; # ←ここは変えちゃあかんです＞＜
$HcomName[$HcomBettown]      = '輝ける都市計画';
$HcomCost[$HcomBettown]      = 28; # ←ここは変えちゃあかんです＞＜
$HcomName[$HcomKai]          = '改装・強化';
$HcomCost[$HcomKai]          = 28; # ←ここは変えちゃあかんです＞＜
$HcomName[$HcomBoku2]        = '僕の引越し２';
$HcomCost[$HcomBoku2]        = 48; # ←ここは変えちゃあかんです＞＜
$HcomName[$HcomPrepare]      = '整地';
$HcomCost[$HcomPrepare]      = 5;
$HcomName[$HcomPrepare2]     = '地ならし';
$HcomCost[$HcomPrepare2]     = 1000;
$HcomName[$HcomReclaim]      = '埋め立て';
$HcomCost[$HcomReclaim]      = 150;
$HcomName[$HcomEneWt]        = '水力発電所建設';
$HcomCost[$HcomEneWt]        = 300;
$HcomName[$HcomEneFw]        = '火力発電所建設';
$HcomCost[$HcomEneFw]        = 7500;
$HcomName[$HcomEneAt]        = '原子力発電所建設';
$HcomCost[$HcomEneAt]        = 40000;
$HcomName[$HcomEneWd]        = '風力発電所建設';
$HcomCost[$HcomEneWd]        = 150;
$HcomName[$HcomEneBo]        = 'バイオマス発電所建設';
$HcomCost[$HcomEneBo]        = 40000;
$HcomName[$HcomEneSo]        = 'ソーラー発電所建設';
$HcomCost[$HcomEneSo]        = 60000;
$HcomName[$HcomEneCs]        = 'コスモ発電所建設';
$HcomCost[$HcomEneCs]        = 298000;
$HcomName[$HcomEneNF]        = '核融合発電所建設';
$HcomCost[$HcomEneNF]        = 1500000;
$HcomName[$HcomConden]       = 'コンデンサ建設';
$HcomCost[$HcomConden]       = 98000;
$HcomName[$HcomReclaim2]     = '遠距離埋め立て';
$HcomCost[$HcomReclaim2]     = 5000;
$HcomName[$HcomReclaim3]     = '２段階埋め立て';
$HcomCost[$HcomReclaim3]     = 5000;
$HcomName[$HcomDestroy3]     = '２段階掘削';
$HcomCost[$HcomDestroy3]     = 3000;
$HcomName[$HcomYoyaku]       = '開発予定計画';
$HcomCost[$HcomYoyaku]       = 1000;
$HcomName[$HcomYakusho]      = '島役所建設';
$HcomCost[$HcomYakusho]      = 30000;
$HcomName[$HcomKura]         = '倉庫建設・貯金';
$HcomCost[$HcomKura]         = 10500;
$HcomName[$HcomKuraf]        = '倉庫建設・貯食';
$HcomCost[$HcomKuraf]        = -10000;
$HcomName[$HcomKura2]        = '倉庫引き出し';
$HcomCost[$HcomKura2]        = 500;
$HcomName[$HcomTrain]        = '駅・線路・電車建設';
$HcomCost[$HcomTrain]        = 10000;
$HcomName[$HcomDestroy]      = '掘削';
$HcomCost[$HcomDestroy]      = 200;
$HcomName[$HcomOnsen]        = '温泉掘削';
$HcomCost[$HcomOnsen]        = 50;
$HcomName[$HcomMinato]       = '港町開発';
$HcomCost[$HcomMinato]       = 550;
$HcomName[$HcomFune]         = '造船・出航';
$HcomCost[$HcomFune]         = 500;
$HcomName[$HcomSeki]         = '関所建設';
$HcomCost[$HcomSeki]         = 1000;
$HcomName[$HcomSellTree]     = '伐採';
$HcomCost[$HcomSellTree]     = 0;
$HcomName[$HcomPlant]        = '植林';
$HcomCost[$HcomPlant]        = 50;
$HcomName[$HcomFarm]         = '農場整備';
$HcomCost[$HcomFarm]         = 20;
$HcomName[$HcomFoodim]       = '食物研究所建設';
$HcomCost[$HcomFoodim]       = 5000;
$HcomName[$HcomFarmcpc]      = '牧場建設・家畜販売';
$HcomCost[$HcomFarmcpc]      = 3000;
$HcomName[$HcomCollege]      = '大学建設';
$HcomCost[$HcomCollege]      = 2000;
$HcomName[$HcomFactory]      = '工場建設';
$HcomCost[$HcomFactory]      = 100;
$HcomName[$HcomHTget]        = 'ハイテク技術誘致';
$HcomCost[$HcomHTget]        = 10000;
$HcomName[$HcomMountain]     = '採掘場整備';
$HcomCost[$HcomMountain]     = 300;
$HcomName[$HcomBase]         = 'ミサイル基地建設';
$HcomCost[$HcomBase]         = 300;
$HcomName[$HcomDbase]        = '防衛施設建設';
$HcomCost[$HcomDbase]        = 800;
$HcomName[$HcomSbase]        = '海底基地建設';
$HcomCost[$HcomSbase]        = 10000;
$HcomName[$HcomSeacity]      = '海底都市建設';
$HcomCost[$HcomSeacity]      = 77777;
$HcomName[$HcomMonument]     = '記念碑建造';
$HcomCost[$HcomMonument]     = 9999;
$HcomName[$HcomMonbuy]       = '怪獣の購入・配置';
$HcomCost[$HcomMonbuy]       = 3980;
$HcomName[$HcomMonbuyt]      = 'テトラの購入・配置';
$HcomCost[$HcomMonbuyt]      = 10000;
$HcomName[$HcomHaribote]     = 'ハリボテ設置';
$HcomCost[$HcomHaribote]     = 1;
$HcomName[$HcomMine]         = '地雷設置';
$HcomCost[$HcomMine]         = 100;
$HcomName[$HcomPark]         = '遊園地建設';
$HcomCost[$HcomPark]         = 3000;
$HcomName[$HcomZoo]          = '動物園建設';
$HcomCost[$HcomZoo]          = 100000;
$HcomName[$HcomNursery]      = '養殖場設置';
$HcomCost[$HcomNursery]      = 50;
$HcomName[$HcomKyujo]        = '野球場建設';
$HcomCost[$HcomKyujo]        = 5000;
$HcomName[$HcomUmiamu]       = '海あみゅ建設';
$HcomCost[$HcomUmiamu]       = 15000;
$HcomName[$HcomRizort]       = 'リゾート地開発';
$HcomCost[$HcomRizort]       = 50000;
$HcomName[$HcomProcity]      = '防災都市化';
$HcomCost[$HcomProcity]      = 25000;
$HcomName[$HcomNewtown]      = 'ニュータウン建設';
$HcomCost[$HcomNewtown]      = 950;
$HcomName[$HcomBigtown]      = '現代都市建設';
$HcomCost[$HcomBigtown]      = 45000;
$HcomName[$HcomSeatown]      = '海底新都市建設';
$HcomCost[$HcomSeatown]      = 69800;
$HcomName[$HcomBoku]         = '僕の引越し';
$HcomCost[$HcomBoku]         = 1000;
$HcomName[$HcomTaishi]       = '大使派遣';
$HcomCost[$HcomTaishi]       = 50000;
$HcomName[$HcomMagic]        = '魔術師派遣';
$HcomCost[$HcomMagic]        = 5000;
$HcomName[$HcomEisei]        = '人工衛星打ち上げ';
$HcomCost[$HcomEisei]        = 9999;
$HcomName[$HcomEiseimente]   = '人工衛星修復';
$HcomCost[$HcomEiseimente]   = 5000;
$HcomName[$HcomEiseiLzr]     = '衛星レーザー発射';
$HcomCost[$HcomEiseiLzr]     = 39999;
$HcomName[$HcomEiseiAtt]     = '衛星破壊砲発射';
$HcomCost[$HcomEiseiAtt]     = 49999;
$HcomName[$HcomMissileNM]    = 'ミサイル発射';
$HcomCost[$HcomMissileNM]    = 20;
$HcomName[$HcomMissilePP]    = 'PPミサイル発射';
$HcomCost[$HcomMissilePP]    = 500;
$HcomName[$HcomMissileSPP]   = 'SPPミサイル発射';
$HcomCost[$HcomMissileSPP]   = 2000;
$HcomName[$HcomMissileST]    = 'STミサイル発射';
$HcomCost[$HcomMissileST]    = 50;
$HcomName[$HcomMissileLD]    = '陸地破壊弾発射';
$HcomCost[$HcomMissileLD]    = 3000;
$HcomName[$HcomMissileLR]    = '地形隆起弾発射';
$HcomCost[$HcomMissileLR]    = 5000;
$HcomName[$HcomMissileSS]    = '核ミサイル発射';
$HcomCost[$HcomMissileSS]    = 12000;
$HcomName[$HcomSendMonster]  = '動物派遣';
$HcomCost[$HcomSendMonster]  = 10000;
$HcomName[$HcomDoNothing]    = '資金繰り';
$HcomCost[$HcomDoNothing]    = 0;
$HcomName[$HcomSell]         = '食料輸出';
$HcomCost[$HcomSell]         = -100;
$HcomName[$HcomMoney]        = '資金援助';
$HcomCost[$HcomMoney]        = 100;
$HcomName[$HcomFood]         = '食料援助';
$HcomCost[$HcomFood]         = -100;
$HcomName[$HcomEneGive]      = '電力援助';
$HcomCost[$HcomEneGive]      = 100;
$HcomName[$HcomPropaganda]   = '誘致活動';
$HcomCost[$HcomPropaganda]   = 2000;
$HcomName[$HcomGiveup]       = '島の放棄';
$HcomCost[$HcomGiveup]       = 0;
$HcomName[$HcomGivefood]     = 'エサをあげる';
$HcomCost[$HcomGivefood]     = -50000;
$HcomName[$HcomAutoPrepare]  = '整地自動入力';
$HcomCost[$HcomAutoPrepare]  = 0;
$HcomName[$HcomAutoPrepare2] = '地ならし自動入力';
$HcomCost[$HcomAutoPrepare2] = 0;
$HcomName[$HcomAutoDelete]   = '全計画を白紙撤回';
$HcomCost[$HcomAutoDelete]   = 0;
$HcomName[$HcomAutoReclaim]  = '浅瀬埋め立て自動入力';
$HcomCost[$HcomAutoReclaim]  = 0;
$HcomName[$HcomAutoDestroy]  = '浅瀬掘削自動入力';
$HcomCost[$HcomAutoDestroy]  = 0;
$HcomName[$HcomAutoSellTree] = '伐採自動入力';
$HcomCost[$HcomAutoSellTree] = 0;
$HcomName[$HcomAutoForestry] = '伐採＆植林自動入力';
$HcomCost[$HcomAutoForestry] = 0;
$HcomName[$HcomAutoYoyaku]   = '開発予定計画自動入力';
$HcomCost[$HcomAutoYoyaku]   = 0;
$HcomName[$HcomAutoUchuste]  = '宇宙ステ修復自動入力';
$HcomCost[$HcomAutoUchuste]  = 0;
$HcomName[$HcomAuction]      = 'オークション出品';
$HcomCost[$HcomAuction]      = 0;
$HcomName[$HcomIjiri]        = '丸秘(>_<)ー~)';
$HcomCost[$HcomIjiri]        = 0;

#----------------------------------------------------------------------
# 変数
#----------------------------------------------------------------------

# COOKIE
my($defaultID);       # 島の名前
my($defaultTarget);   # ターゲットの名前


# 島の座標数
$HpointNumber = $HislandSize * $HislandSize;

#----------------------------------------------------------------------
# メイン
#----------------------------------------------------------------------

# jcode.plをrequire
require($jcode);

# 「戻る」リンク
$HtempBack = "<A CLASS=\"type3\" HREF=\"$HthisFile\">${HtagBig_}トップへ戻る${H_tagBig}</A>";

# ロックをかける
if(!hakolock()) {
    # ロック失敗
    # ヘッダ出力
    tempHeader();

    # ロック失敗メッセージ
    tempLockFail();

    # フッタ出力
    tempFooter();

    # 終了
    exit(0);
}

# 乱数の初期化
srand(time^$$);

# COOKIE読みこみ
cookieInput();

# CGI読みこみ
cgiInput();

# 島データの読みこみ
if(readIslandsFile($HcurrentID) == 0) {
    unlock();
    tempHeader();
    tempNoDataFile();
    tempFooter();
    exit(0);
}

# テンプレートを初期化
tempInitialize();

# COOKIE出力
cookieOutput();

# ヘッダ出力
tempHeader();

if($HmainMode eq 'turn') {
    # ターン進行
    require('hako-turn.cgi');
    require('hako-top.cgi');
    turnMain();

} elsif($HmainMode eq 'new') {
    # 島の新規作成
    require('hako-turn.cgi');
    require('hako-map.cgi');
    newIslandMain();

} elsif($HmainMode eq 'print') {
    # 観光モード
    require('hako-map.cgi');
    printIslandMain();

} elsif($HmainMode eq 'owner') {

    # 開発モード
    require('hako-map.cgi');
    ownerMain();

} elsif($HmainMode eq 'command') {
    # コマンド入力モード
    require('hako-map.cgi');
    commandMain();

} elsif($HmainMode eq 'comment') {
    # コメント入力モード
    require('hako-map.cgi');
    commentMain();

} elsif($HmainMode eq 'lbbs') {

    # ローカル掲示板モード
    require('hako-map.cgi');
    localBbsMain();

} elsif($HmainMode eq 'change') {
    # 情報変更モード
    require('hako-turn.cgi');
    require('hako-top.cgi');
    changeMain();

} elsif($HmainMode eq 'ipinfo') {
    # IP情報モード
    if($HoldPassword eq $masterPassword) {
	# マスターパスワード
	require('hako-top2.cgi');
	topPageMain();
    } else {
	require('hako-top.cgi');
	topPageMain();
    }

} elsif($HmainMode eq 'chowner') {
  # オーナー名変更モード
  require('hako-turn.cgi');
  require('hako-top.cgi');
  changeOwner();

} elsif($HmainMode eq 'ankeito') {
  require('hako-map.cgi');
  changeAnkeito();

} elsif($HmainMode eq 'totoyoso') {
    # コメント入力モード
    require('hako-map.cgi');
    totoMain();

} elsif($HmainMode eq 'totoyoso2') {
    # コメント入力モード
    require('hako-map.cgi');
    totosMain();

} elsif($HmainMode eq 'shouene') {
    # コメント入力モード
    require('hako-map.cgi');
    shoueneMain();

} elsif($HmainMode eq 'bousai') {
    # コメント入力モード
    require('hako-map.cgi');
    bousaiMain();

} elsif($HmainMode eq 'kankou') {
    # コメント入力モード
    require('hako-map.cgi');
    kankouMain();

} elsif($HmainMode eq 'sizen') {
    # コメント入力モード
    require('hako-map.cgi');
    sizenMain();

} elsif($HmainMode eq 'kyouiku') {
    # コメント入力モード
    require('hako-map.cgi');
    kyouikuMain();

} elsif($HmainMode eq 'chochiku') {
    # コメント入力モード
    require('hako-map.cgi');
    chochikuMain();

} elsif($HmainMode eq 'auction') {
    # コメント入力モード
    require('hako-map.cgi');
    auctionMain();

} elsif($HmainMode eq 'mskyoka') {
    require('hako-map.cgi');
    msMain();

} elsif($HmainMode eq 'ms2kyoka') {
    require('hako-map.cgi');
    ms2Main();

} else {
    # その他の場合はトップページモード
    require('hako-top.cgi');
    topPageMain();
}

# フッタ出力
tempFooter();

# 終了
exit(0);

# コマンドを前にずらす
sub slideFront {
    my($command, $number) = @_;
    my($i);

    # それぞれずらす
    splice(@$command, $number, 1);

    # 最後に資金繰り
    $command->[$HcommandMax - 1] = {
	'kind' => $HcomDoNothing,
	'target' => 0,
	'x' => 0,
	'y' => 0,
	'arg' => 0
	};
}

# コマンドを後にずらす
sub slideBack {
    my($command, $number) = @_;
    my($i);

    # それぞれずらす
    return if $number == $#$command;
    pop(@$command);
    splice(@$command, $number, 0, $command->[$number]);
}

#----------------------------------------------------------------------
# 島データ入出力
#----------------------------------------------------------------------

# 全島データ読みこみ
sub readIslandsFile {
    my($num) = @_; # 0だと地形読みこまず
                   # -1だと全地形を読む
                   # 番号だとその島の地形だけは読みこむ

    # データファイルを開く
    if(!open(IN, "${HdirName}/hakojima.dat")) {
	rename("${HdirName}/hakojima.tmp", "${HdirName}/hakojima.dat");
	if(!open(IN, "${HdirName}/hakojima.dat")) {
	    return 0;
	}
    }

    open(OIN, "${HdirName}/howner.dat");
    open(PIN, "${HdirName}/ips.dat");
    open(AIN, "${HdirName}/auction.dat");
    open(KIN, "${HdirName}/an.dat");

    # 各パラメータの読みこみ
    $HislandTurn     = int(<IN>); # ターン数
    if($HislandTurn == 0) {
	return 0;
    }
    $HislandLastTime = int(<IN>); # 最終更新時間
    if($HislandLastTime == 0) {
	return 0;
    }
    $HislandNumber   = int(<IN>); # 島の総数
    $HislandNextID   = int(<IN>); # 次に割り当てるID

    $auction1   = <AIN>;
    chomp($auction1);
    if($auction1 == '') {
	$shuppin = random(27)+1;
	$auction1 = "$shuppin,0,0,0,0";
    }
    $auction2   = <AIN>;
    chomp($auction2);
    if($auction2 == '') {
	$shuppin = random(27)+1;
	$auction2 = "$shuppin,0,0,0,0";
    }
    $auction3   = <AIN>;
    chomp($auction3);
    if($auction3 == '') {
	$shuppin = random(27)+1;
	$auction3 = "$shuppin,0,0,0,0";
    }

    $an1 = int(<KIN>);
    if($an1 == '') {
	$an1 = "0";
    }
    $an2 = int(<KIN>);
    if($an2 == '') {
	$an2 = "0";
    }
    $an3 = int(<KIN>);
    if($an3 == '') {
	$an3 = "0";
    }
    $an4 = int(<KIN>);
    if($an4 == '') {
	$an4 = "0";
    }
    $an5 = int(<KIN>);
    if($an5 == '') {
	$an5 = "0";
    }

    # ターン処理判定
    my($now) = time;
    if((($Hdebug == 1) && 
	($HmainMode eq 'Hdebugturn')) ||
       (($now - $HislandLastTime) >= $HunitTime)) {
	$HmainMode = 'turn';
	$num = -1; # 全島読みこむ
    }

    # 島の読みこみ
    my($i);
    for($i = 0; $i < $HislandNumber; $i++) {
	 $Hislands[$i] = readIsland($num);
	 $HidToNumber{$Hislands[$i]->{'id'}} = $i;
    }

    # 怪獣出現数の読み込み
    if (!$HnewGame) {
        if (open(MIN, "<${HdirName}/monslive.dat")) {
            for ($i = 0; $i < $HislandNumber; $i++) {
                $Hislands[$i]->{'monsterlive'} = int(<MIN>);
                $Hislands[$i]->{'monsterlivetype'} = int(<MIN>);
                $Hislands[$i]->{'eisei1'} = int(<MIN>);
                $Hislands[$i]->{'eisei2'} = int(<MIN>);
                $Hislands[$i]->{'eisei3'} = int(<MIN>);
                $Hislands[$i]->{'eisei4'} = int(<MIN>);
                $Hislands[$i]->{'eisei5'} = int(<MIN>);
                $Hislands[$i]->{'eisei6'} = int(<MIN>);
            }
            close(MIN);
        } else {
            for ($i = 0; $i < $HislandNumber; $i++) {
                $Hislands[$i]->{'monsterlive'} = 0;
                $Hislands[$i]->{'monsterlivetype'} = 0;
                $Hislands[$i]->{'eisei1'} = 0;
                $Hislands[$i]->{'eisei2'} = 0;
                $Hislands[$i]->{'eisei3'} = 0;
                $Hislands[$i]->{'eisei4'} = 0;
                $Hislands[$i]->{'eisei5'} = 0;
                $Hislands[$i]->{'eisei6'} = 0;
            }
        }
    }

    # ファイルを閉じる
    close(IN);
    close(OIN);
    close(PIN);
    close(AIN);
    close(KIN);
    return 1;
}

# 島ひとつ読みこみ
sub readIsland {
    my($num) = @_;
    my($name, $id, $prize, $absent, $comment, $password, $money, $food,
       $pop, $area, $farm, $factory, $mountain, $pts, $eis1, $eis2, $eis3, $eis4, $eis5, $eis6, $eis7, $eis8, $taiji, $onm, $monslive, $monslivetype, $eisei1, $eisei2, $eisei3, $eisei4, $eisei5, $eisei6, $score);
    $name = <IN>; # 島の名前
    chomp($name);
    if($name =~ s/,(.*)$//g) {
	$score = int($1);
    } else {
	$score = 0;
    }
    $id = int(<IN>); # ID番号
    $id1= int(<OIN>);
    $ownername = <OIN>;
    chomp($ownername);
    $totoyoso = <OIN>;
    chomp($totoyoso);
    $totoyoso2 = <OIN>;
    chomp($totoyoso2);
    $kei = int(<OIN>);
    $rena = int(<OIN>);
    $momotan = int(<OIN>);
    $fore = int(<OIN>);
    $pika = int(<OIN>);
    $hamu = int(<OIN>);
    $monta = int(<OIN>);
    $tare = int(<OIN>);
    $zipro = int(<OIN>);
    $leje = int(<OIN>);
    $ipname = <PIN>;
    chomp($ipname);
    $ip0 = <PIN>;
    chomp($ip0);
    $ip1 = <PIN>;
    chomp($ip1);
    $ip2 = <PIN>;
    chomp($ip2);
    $ip3 = <PIN>;
    chomp($ip3);
    $ip4 = <PIN>;
    chomp($ip4);
    $ip5 = <PIN>;
    chomp($ip5);
    $ip6 = <PIN>;
    chomp($ip6);
    $ip7 = <PIN>;
    chomp($ip7);
    $ip8 = int(<PIN>);
    $ip9 = int(<PIN>);
    $etc0 = int(<PIN>);
    $etc1 = int(<PIN>);
    $etc2 = int(<PIN>);
    $etc3 = int(<PIN>);
    $etc4 = int(<PIN>);
    $etc5 = <PIN>;
    chomp($etc5);
    $etc6 = <PIN>;
    chomp($etc6);
    $etc7 = <PIN>;
    chomp($etc7);
    $etc8 = <PIN>;
    chomp($etc8);
    $etc9 = <PIN>;
    chomp($etc9);
    $auc0 = <AIN>;
    chomp($auc0);
    if($auc0 == '') {
	$auc0 = '0,0,0,0,0';
    }
    $auc1 = int(<AIN>);
    if($auc1 == '') {
	$auc1 = 0;
    }
    $auc2 = int(<AIN>);
    if($auc2 == '') {
	$auc2 = 0;
    }
    $auc3 = int(<AIN>);
    if($auc3 == '') {
	$auc3 = 0;
    }
    $auc4 = <AIN>;
    chomp($auc4);
    if($auc4 == '') {
	$auc4 = '0,0,0';
    }
    $auc5 = <AIN>;
    chomp($auc5);
    if($auc5 == '') {
	$auc5 = '0,0,0,0,0';
    }
    $auc6 = <AIN>;
    chomp($auc6);
    if($auc6 == '') {
	$auc6 = '0,0,0';
    }
    $auc7 = <AIN>;
    chomp($auc7);
    $auc8 = <AIN>;
    chomp($auc8);
    $auc9 = <AIN>;
    chomp($auc9);
    if($auc9 == '') {
	$auc9 = '0,0,0,0,0';
    }

    $anflag = int(<KIN>);
    if($anflag == '') {
	$anflag = '1';
    }

    $prize = <IN>; # 受賞
    chomp($prize);
    $absent = int(<IN>); # 連続資金繰り数
    $comment = <IN>; # コメント
    chomp($comment);
    $password = <IN>; # 暗号化パスワード
    chomp($password);
    $money = int(<IN>);    # 資金
    $food = int(<IN>);     # 食料
    $pop = int(<IN>);      # 人口
    $area = int(<IN>);     # 広さ
    $farm = int(<IN>);     # 農場
    $factory = <IN>;
    chomp($factory);
    $mountain = int(<IN>); # 採掘場
    $pts = int(<IN>);      # ポイント
    $eis1 = int(<IN>);
    $eis2 = int(<IN>);
    $eis3 = int(<IN>);
    $eis4 = int(<IN>);
    $eis5 = int(<IN>);
    $eis6 = int(<IN>);
    $eis7 = int(<IN>);
    $eis8 = <IN>;
    chomp($eis8);
    $taiji = int(<IN>);
    $onm = <IN>;
    chomp($onm);
    $monslive = int(<IN>) if ($HnewGame); # 怪獣出現数
    $monslivetype = int(<IN>) if ($HnewGame); # 怪獣出現種類
    $eisei1 = int(<IN>) if ($HnewGame);
    $eisei2 = int(<IN>) if ($HnewGame);
    $eisei3 = (<IN>) if ($HnewGame);
    chomp($eisei3);
    $eisei4 = (<IN>) if ($HnewGame);
    chomp($eisei4);
    $eisei5 = (<IN>) if ($HnewGame);
    chomp($eisei5);
    $eisei6 = (<IN>) if ($HnewGame);
    chomp($eisei6);

    # HidToNameテーブルへ保存
    $HidToName{$id} = $name;	# 

    # 地形
    my(@land, @landValue, $line, @command, @lbbs);

    if(($num == -1) || ($num == $id)) {
	if(!open(IIN, "${HdirName}/island.$id")) {
	    rename("${HdirName}/islandtmp.$id", "${HdirName}/island.$id");
	    if(!open(IIN, "${HdirName}/island.$id")) {
		exit(0);
	    }
	}
	my($x, $y);
	for($y = 0; $y < $HislandSize; $y++) {
	    $line = <IIN>;
	    for($x = 0; $x < $HislandSize; $x++) {
		$line =~ s/^(..)(...)//;
		$land[$x][$y] = hex($1);
		$landValue[$x][$y] = hex($2);
	    }
	}

	# コマンド
	my($i);
	for($i = 0; $i < $HcommandMax; $i++) {
	    $line = <IIN>;
	    $line =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)$/;
	    $command[$i] = {
		'kind' => int($1),
		'target' => int($2),
		'x' => int($3),
		'y' => int($4),
		'arg' => int($5)
		}
	}

	# ローカル掲示板
	for($i = 0; $i < $HlbbsMax; $i++) {
	    $line = <IIN>;
	    chomp($line);
            if ($HlbbsOldToNew) {
                # 掲示板ログの形式を変換する
                if ($line =~ /^([0-9]*)\>(.*)\>(.*)$/) {
                    # 標準形式ログである
                    $line = "0<<$1>$2>$3";
                }
            }
	    $lbbs[$i] = $line;
	}

	close(IIN);
    }

    # 島型にして返す
    return {
	 'name' => $name,
         'ownername' => $ownername,
	 'id' => $id,
	 'id1' => $id1,
	 'score' => $score,
	 'prize' => $prize,
	 'absent' => $absent,
	 'comment' => $comment,
	 'password' => $password,
	 'money' => $money,
	 'food' => $food,
	 'pop' => $pop,
	 'area' => $area,
	 'farm' => $farm,
	 'factory' => $factory,
	 'mountain' => $mountain,
	 'pts' => $pts,
	 'eis1' => $eis1,
	 'eis2' => $eis2,
	 'eis3' => $eis3,
	 'eis4' => $eis4,
	 'eis5' => $eis5,
	 'eis6' => $eis6,
	 'eis7' => $eis7,
	 'eis8' => $eis8,
	 'taiji' => $taiji,
	 'onm' => $onm,
	 'ipname' => $ipname,
	 'ip0' => $ip0,
	 'ip1' => $ip1,
	 'ip2' => $ip2,
	 'ip3' => $ip3,
	 'ip4' => $ip4,
	 'ip5' => $ip5,
	 'ip6' => $ip6,
	 'ip7' => $ip7,
	 'ip8' => $ip8,
	 'ip9' => $ip9,
	 'etc0' => $etc0,
	 'etc1' => $etc1,
	 'etc2' => $etc2,
	 'etc3' => $etc3,
	 'etc4' => $etc4,
	 'etc5' => $etc5,
	 'etc6' => $etc6,
	 'etc7' => $etc7,
	 'etc8' => $etc8,
	 'etc9' => $etc9,
	 'auc0' => $auc0,
	 'auc1' => $auc1,
	 'auc2' => $auc2,
	 'auc3' => $auc3,
	 'auc4' => $auc4,
	 'auc5' => $auc5,
	 'auc6' => $auc6,
	 'auc7' => $auc7,
	 'auc8' => $auc8,
	 'auc9' => $auc9,
	 'anflag' => $anflag,
         'monsterlive' => $monslive,
         'monsterlivetype' => $monslivetype,
         'eisei1' => $eisei1,
         'eisei2' => $eisei2,
         'eisei3' => $eisei3,
         'eisei4' => $eisei4,
         'eisei5' => $eisei5,
         'eisei6' => $eisei6,
         'totoyoso' => $totoyoso,
         'totoyoso2' => $totoyoso2,
         'kei' => $kei,
         'rena' => $rena,
         'momotan' => $momotan,
         'fore' => $fore,
         'pika' => $pika,
         'hamu' => $hamu,
         'monta' => $monta,
         'tare' => $tare,
         'zipro' => $zipro,
         'leje' => $leje,
	 'land' => \@land,
	 'landValue' => \@landValue,
	 'command' => \@command,
	 'lbbs' => \@lbbs,
    };
}

# オーナー名を記述
sub writeIslandsOwner {
  my($num) = @_;
  # File Open
  open(OUT, ">${HdirName}/howner.tmp");
  my($i);
  for($i = 0; $i < $HislandNumber; $i++){
    print OUT "$Hislands[$i]->{'id1'}\n";
    print OUT "$Hislands[$i]->{'ownername'}\n";
    print OUT "$Hislands[$i]->{'totoyoso'}\n";
    print OUT "$Hislands[$i]->{'totoyoso2'}\n";
    print OUT "$Hislands[$i]->{'kei'}\n";
    print OUT "$Hislands[$i]->{'rena'}\n";
    print OUT "$Hislands[$i]->{'momotan'}\n";
    print OUT "$Hislands[$i]->{'fore'}\n";
    print OUT "$Hislands[$i]->{'pika'}\n";
    print OUT "$Hislands[$i]->{'hamu'}\n";
    print OUT "$Hislands[$i]->{'monta'}\n";
    print OUT "$Hislands[$i]->{'tare'}\n";
    print OUT "$Hislands[$i]->{'zipro'}\n";
    print OUT "$Hislands[$i]->{'leje'}\n";
  }

  close(OUT);

  # 本来の名前にする
  unlink("${HdirName}/howner.dat");
  rename("${HdirName}/howner.tmp", "${HdirName}/howner.dat");
}

# 全島データ書き込み
sub writeIslandsFile {
    my($num) = @_;

    # ファイルを開く
    open(OUT, ">${HdirName}/hakojima.tmp");
    open(HOUT, ">${HdirName}/howner.tmp");
    open(POUT, ">${HdirName}/ips.tmp");
    open(AOUT, ">${HdirName}/auction.tmp");
    open(KOUT, ">${HdirName}/an.tmp");

    # 各パラメータ書き込み
    print OUT "$HislandTurn\n";
    print OUT "$HislandLastTime\n";
    print OUT "$HislandNumber\n";
    print OUT "$HislandNextID\n";

    print AOUT "$auction1\n";
    print AOUT "$auction2\n";
    print AOUT "$auction3\n";

    print KOUT "$an1\n";
    print KOUT "$an2\n";
    print KOUT "$an3\n";
    print KOUT "$an4\n";
    print KOUT "$an5\n";

    # 島の書きこみ
    my($i);
    for($i = 0; $i < $HislandNumber; $i++) {
	 writeIsland($Hislands[$i], $num);
    }

    # 怪獣出現数の書き込み
    if (!$HnewGame) {
        if (open(MIN, ">${HdirName}/monslive.dat")) {
            for ($i = 0; $i < $HislandNumber; $i++) {
                print MIN $Hislands[$i]->{'monsterlive'} . "\n";
                print MIN $Hislands[$i]->{'monsterlivetype'} . "\n";
                print MIN $Hislands[$i]->{'eisei1'} . "\n";
                print MIN $Hislands[$i]->{'eisei2'} . "\n";
                print MIN $Hislands[$i]->{'eisei3'} . "\n";
                print MIN $Hislands[$i]->{'eisei4'} . "\n";
                print MIN $Hislands[$i]->{'eisei5'} . "\n";
                print MIN $Hislands[$i]->{'eisei6'} . "\n";
            }
            close(MIN);
        }
    }

    # ファイルを閉じる
    close(OUT);
    close(HOUT);
    close(POUT);
    close(AOUT);
    close(KOUT);

    # 本来の名前にする
    unlink("${HdirName}/hakojima.dat");
    rename("${HdirName}/hakojima.tmp", "${HdirName}/hakojima.dat");

    unlink("${HdirName}/howner.dat");
    rename("${HdirName}/howner.tmp", "${HdirName}/howner.dat");

    unlink("${HdirName}/ips.dat");
    rename("${HdirName}/ips.tmp", "${HdirName}/ips.dat");

    unlink("${HdirName}/auction.dat");
    rename("${HdirName}/auction.tmp", "${HdirName}/auction.dat");

    unlink("${HdirName}/an.dat");
    rename("${HdirName}/an.tmp", "${HdirName}/an.dat");

}

# 島ひとつ書き込み
sub writeIsland {
    my($island, $num) = @_;
    my($score);
    $score = int($island->{'score'});
    print OUT $island->{'name'} . ",$score\n";
    print OUT $island->{'id'} . "\n";
    print OUT $island->{'prize'} . "\n";
    print OUT $island->{'absent'} . "\n";
    print OUT $island->{'comment'} . "\n";
    print OUT $island->{'password'} . "\n";
    print OUT $island->{'money'} . "\n";
    print OUT $island->{'food'} . "\n";
    print OUT $island->{'pop'} . "\n";
    print OUT $island->{'area'} . "\n";
    print OUT $island->{'farm'} . "\n";
    print OUT $island->{'factory'} . "\n";
    print OUT $island->{'mountain'} . "\n";
    print OUT $island->{'pts'} . "\n";
    print OUT $island->{'eis1'} . "\n";
    print OUT $island->{'eis2'} . "\n";
    print OUT $island->{'eis3'} . "\n";
    print OUT $island->{'eis4'} . "\n";
    print OUT $island->{'eis5'} . "\n";
    print OUT $island->{'eis6'} . "\n";
    print OUT $island->{'eis7'} . "\n";
    print OUT $island->{'eis8'} . "\n";
    print OUT $island->{'taiji'} . "\n";
    print OUT $island->{'onm'} . "\n";
    print OUT $island->{'monsterlive'} . "\n" if ($HnewGame);
    print OUT $island->{'monsterlivetype'} . "\n" if ($HnewGame);
    print OUT $island->{'eisei1'} . "\n" if ($HnewGame);
    print OUT $island->{'eisei2'} . "\n" if ($HnewGame);
    print OUT $island->{'eisei3'} . "\n" if ($HnewGame);
    print OUT $island->{'eisei4'} . "\n" if ($HnewGame);
    print OUT $island->{'eisei5'} . "\n" if ($HnewGame);
    print OUT $island->{'eisei6'} . "\n" if ($HnewGame);
    print HOUT $island->{'id1'} . "\n";
    print HOUT $island->{'ownername'} . "\n";
    print HOUT $island->{'totoyoso'} . "\n";
    print HOUT $island->{'totoyoso2'} . "\n";
    print HOUT $island->{'kei'} . "\n";
    print HOUT $island->{'rena'} . "\n";
    print HOUT $island->{'momotan'} . "\n";
    print HOUT $island->{'fore'} . "\n";
    print HOUT $island->{'pika'} . "\n";
    print HOUT $island->{'hamu'} . "\n";
    print HOUT $island->{'monta'} . "\n";
    print HOUT $island->{'tare'} . "\n";
    print HOUT $island->{'zipro'} . "\n";
    print HOUT $island->{'leje'} . "\n";
    print POUT $island->{'name'} . "\n";
    print POUT $island->{'ip0'} . "\n";
    print POUT $island->{'ip1'} . "\n";
    print POUT $island->{'ip2'} . "\n";
    print POUT $island->{'ip3'} . "\n";
    print POUT $island->{'ip4'} . "\n";
    print POUT $island->{'ip5'} . "\n";
    print POUT $island->{'ip6'} . "\n";
    print POUT $island->{'ip7'} . "\n";
    print POUT $island->{'ip8'} . "\n";
    print POUT $island->{'ip9'} . "\n";
    print POUT $island->{'etc0'} . "\n";
    print POUT $island->{'etc1'} . "\n";
    print POUT $island->{'etc2'} . "\n";
    print POUT $island->{'etc3'} . "\n";
    print POUT $island->{'etc4'} . "\n";
    print POUT $island->{'etc5'} . "\n";
    print POUT $island->{'etc6'} . "\n";
    print POUT $island->{'etc7'} . "\n";
    print POUT $island->{'etc8'} . "\n";
    print POUT $island->{'etc9'} . "\n";
    print AOUT $island->{'auc0'} . "\n";
    print AOUT $island->{'auc1'} . "\n";
    print AOUT $island->{'auc2'} . "\n";
    print AOUT $island->{'auc3'} . "\n";
    print AOUT $island->{'auc4'} . "\n";
    print AOUT $island->{'auc5'} . "\n";
    print AOUT $island->{'auc6'} . "\n";
    print AOUT $island->{'auc7'} . "\n";
    print AOUT $island->{'auc8'} . "\n";
    print AOUT $island->{'auc9'} . "\n";
    print KOUT $island->{'anflag'} . "\n";

    # 地形
    if(($num <= -1) || ($num == $island->{'id'})) {
	open(IOUT, ">${HdirName}/islandtmp.$island->{'id'}");

	my($land, $landValue);
	$land = $island->{'land'};
	$landValue = $island->{'landValue'};
	my($x, $y);
	for($y = 0; $y < $HislandSize; $y++) {
	    for($x = 0; $x < $HislandSize; $x++) {
		printf IOUT ("%02x%03x", $land->[$x][$y], $landValue->[$x][$y]);
	    }
	    print IOUT "\n";
	}

	# コマンド
	my($command, $cur, $i);
	$command = $island->{'command'};
	for($i = 0; $i < $HcommandMax; $i++) {
	    printf IOUT ("%d,%d,%d,%d,%d\n", 
			 $command->[$i]->{'kind'},
			 $command->[$i]->{'target'},
			 $command->[$i]->{'x'},
			 $command->[$i]->{'y'},
			 $command->[$i]->{'arg'}
			 );
	}

	# ローカル掲示板
	my($lbbs);
	$lbbs = $island->{'lbbs'};
	for($i = 0; $i < $HlbbsMax; $i++) {
	    print IOUT $lbbs->[$i] . "\n";
	}

	close(IOUT);
	unlink("${HdirName}/island.$island->{'id'}");
	rename("${HdirName}/islandtmp.$island->{'id'}", "${HdirName}/island.$island->{'id'}");
    }
}

#----------------------------------------------------------------------
# 入出力
#----------------------------------------------------------------------

# 標準出力への出力
sub out {
    print STDOUT jcode::sjis($_[0]);
}

# デバッグログ
sub HdebugOut {
   open(DOUT, ">>debug.log");
   print DOUT ($_[0]);
   close(DOUT);
}

# CGIの読みこみ
sub cgiInput {
    my($line, $getLine);

    # 入力を受け取って日本語コードをEUCに
    $line = <>;
    $line =~ tr/+/ /;
    $line =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
    $line = jcode::euc($line);
    $line =~ s/[\x00-\x1f\,]//g;

    # GETのやつも受け取る
    $getLine = $ENV{'QUERY_STRING'};
    if($getLine =~ /view([0-9]+|ALL)/) {
    my($num) = $1; 
        if($num eq "ALL") {
	$viewFlag = 'ALL';
	$viewFirst = 0;
	} else { 
	$viewFlag = ''; $viewFirst = $num;
	}
    }

    # 対象の島
    if($line =~ /CommandButton([0-9]+)=/) {
	# コマンド送信ボタンの場合
	$HcurrentID = $1;
	$defaultID = $1;
    }

    if($line =~ /ISLANDNAME=([^\&]*)\&/){
	# 名前指定の場合
	$HcurrentName = cutColumn($1, 20);
    }

if($line =~ /OWNERNAME=([^\&]*)\&/){
  # オーナー名の場合
  $HcurrentOwnerName = cutColumn($1, 20);
}

    if($line =~ /ISLANDID=([0-9]+)\&/){
	# その他の場合
	$HcurrentID = $1;
	$defaultID = $1;

    }

    if($line =~ /ISLANDID2=([0-9]+)\&/){
        # 掲示板の発言島
        $HspeakerID = $1;
    }
    if($line =~ /LBBSTYPE=([^\&]*)\&/){
        # 掲示板の通信形式
        $HlbbsType = $1;
    }

    if($line =~ /ann=([^\&]*)\&/){
        # 掲示板の通信形式
        $AnnType = $1;
    }

    # パスワード
    if($line =~ /OLDPASS=([^\&]*)\&/) {
	$HoldPassword = $1;
	$HdefaultPassword = $1;
    }
    if($line =~ /PASSWORD=([^\&]*)\&/) {
	$HinputPassword = $1;
	$HdefaultPassword = $1;
    }
    if($line =~ /PASSWORD2=([^\&]*)\&/) {
	$HinputPassword2 = $1;
    }

    # メッセージ
    if($line =~ /MESSAGE=([^\&]*)\&/) {
	$Hmessage = cutColumn($1, 80);
    }

    # YOSO
    if($line =~ /MESSAGE=([^\&]*)\&/) {
	$HyosoMessage = cutColumn($1, 44);
    }

    # shuto
    if($line =~ /MESSAGE=([^\&]*)\&/) {
	$HshutoMessage = cutColumn($1, 32);
    }

    # ローカル掲示板
    if($line =~ /LBBSNAME=([^\&]*)\&/) {
	$HlbbsName = $1;
	$HdefaultName = $1;
    }
    if($line =~ /LBBSMESSAGE=([^\&]*)\&/) {
	$HlbbsMessage = cutColumn($1, 80);
    }

    # main modeの取得
    if($line =~ /TurnButton/) {
	if($Hdebug == 1) {
	    $HmainMode = 'Hdebugturn';
	}
    } elsif($line =~ /ChangeOwnerButton/) {
        $HmainMode = 'chowner';
    } elsif($line =~ /OwnerButton/) {
	$HmainMode = 'owner';
    } elsif($line =~ /AnkeButton/) {
	$HmainMode = 'ankeito';
    } elsif($getLine =~ /Sight=([0-9]*)/) {
	$HmainMode = 'print';
	$HcurrentID = $1;
    } elsif($line =~ /SightButton/) {
        $HmainMode = 'print';
        $line =~ /TARGETID=([^\&]*)\&/;
        $HcurrentID = $1;
    } elsif($line =~ /NewIslandButton/) {
	$HmainMode = 'new';
    } elsif($line =~ /LbbsButton(..)([0-9]*)/) {
	$HmainMode = 'lbbs';
	if($1 eq 'SS') {
	    # 観光者
	    $HlbbsMode = 0;
	} elsif($1 eq 'OW') {
	    # 島主
	    $HlbbsMode = 1;
	} else {
	    # 削除
	    $HlbbsMode = 2;
	}
	$HcurrentID = $2;

	# 削除かもしれないので、番号を取得
	$line =~ /NUMBER=([^\&]*)\&/;
	$HcommandPlanNumber = $1;

    } elsif($line =~ /ChangeInfoButton/) {
	$HmainMode = 'change';
    } elsif($line =~ /IPInfoButton/) {
	$HmainMode = 'ipinfo';
    } elsif($line =~ /MessageButton([0-9]*)/) {
	$HmainMode = 'comment';
	$HcurrentID = $1;
    } elsif($line =~ /TotoButton([0-9]*)/) {
	$HmainMode = 'totoyoso';
	$HcurrentID = $1;
    } elsif($line =~ /TotosButton([0-9]*)/) {
	$HmainMode = 'totoyoso2';
        $HcurrentID = $1;
    } elsif($line =~ /ShoueneButton([0-9]*)/) {
	$HmainMode = 'shouene';
        $HcurrentID = $1;
	$line =~ /AMOUNT=([^\&]*)\&/;
	$HcommandArg = $1;
    } elsif($line =~ /BousaiButton([0-9]*)/) {
	$HmainMode = 'bousai';
        $HcurrentID = $1;
	$line =~ /AMOUNT=([^\&]*)\&/;
	$HcommandArg = $1;
    } elsif($line =~ /KankouButton([0-9]*)/) {
	$HmainMode = 'kankou';
        $HcurrentID = $1;
	$line =~ /AMOUNT=([^\&]*)\&/;
	$HcommandArg = $1;
    } elsif($line =~ /SizenButton([0-9]*)/) {
	$HmainMode = 'sizen';
        $HcurrentID = $1;
	$line =~ /AMOUNT=([^\&]*)\&/;
	$HcommandArg = $1;
    } elsif($line =~ /KyouikuButton([0-9]*)/) {
	$HmainMode = 'kyouiku';
        $HcurrentID = $1;
	$line =~ /AMOUNT=([^\&]*)\&/;
	$HcommandArg = $1;
    } elsif($line =~ /ChochikuButton([0-9]*)/) {
	$HmainMode = 'chochiku';
        $HcurrentID = $1;
	$line =~ /AMOUNT=([^\&]*)\&/;
	$HcommandArg = $1;
    } elsif($line =~ /AuctionButton([0-9]*)/) {
	$HmainMode = 'auction';
        $HcurrentID = $1;
	$line =~ /AUCNUMBER=([^\&]*)\&/;
	$HAucNumber = $1;
	$line =~ /AMOUNT=([^\&]*)\&/;
	$HcommandArg = $1;
    } elsif($line =~ /MsButton([0-9]*)/) {
        $HmainMode = 'mskyoka';
	$HcurrentID = $1;
	$line =~ /TARGETID=([^\&]*)\&/;
	$HcommandTarget = $1;
	$defaultTarget = $1;
	$line =~ /AMOUNT=([^\&]*)\&/;
	$HcommandArg = $1;
    } elsif($line =~ /Ms2Button([0-9]*)/) {
        $HmainMode = 'ms2kyoka';
	$HcurrentID = $1;
	$line =~ /TARGETID=([^\&]*)\&/;
	$HcommandTarget = $1;
	$defaultTarget = $1;
	$line =~ /AMOUNT=([^\&]*)\&/;
	$HcommandArg = $1;
    } elsif($line =~ /CommandButton/) {
	$HmainMode = 'command';

	# コマンドモードの場合、コマンドの取得
	$line =~ /NUMBER=([^\&]*)\&/;
	$HcommandPlanNumber = $1;
	$line =~ /COMMAND=([^\&]*)\&/;
	$HcommandKind = $1;
	$HdefaultKind = $1;
	$line =~ /AMOUNT=([^\&]*)\&/;
	$HcommandArg = $1;
	$line =~ /TARGETID=([^\&]*)\&/;
	$HcommandTarget = $1;
	$defaultTarget = $1;
	$line =~ /POINTX=([^\&]*)\&/;
	$HcommandX = $1;
	$HdefaultX = $1;
        $line =~ /POINTY=([^\&]*)\&/;
	$HcommandY = $1;
	$HdefaultY = $1;
	$line =~ /COMMANDMODE=(write|insert|delete)/;
	$HcommandMode = $1;

	$line =~ /LAMOUNT1=([^\&]*)\&/;
	$lamount1 = $1;
	$HdefaultLamount1 = $1;
	    if($line =~ /LAMOUNT2=([^\&]*)\&/) {
		$lamount2 = cutColumn($1, 40);
	    }

    } else {
	$HmainMode = 'top';
    }


    if($line =~ /IMGLINEMAC=([^&]*)\&/){
        my($flag) = 'file:///' . $1;
        $HimgLine = $flag;
    }

    if($line =~ /IMGLINE=([^&]*)\&/){
        my($flag) = substr($1, 0 , -10);
        $flag =~ tr/\\/\//;
    if($flag eq 'del'){ $flag = $imageDir; } else { $flag = 'file:///' . $flag; }
        $HimgLine = $flag;
    }


}

#cookie入力
sub cookieInput {
    my($cookie);

    $cookie = jcode::euc($ENV{'HTTP_COOKIE'});

    if($cookie =~ /${HthisFile}OWNISLANDID=\(([^\)]*)\)/) {
	$defaultID = $1;
    }
    if($cookie =~ /${HthisFile}OWNISLANDPASSWORD=\(([^\)]*)\)/) {
	$HdefaultPassword = $1;
    }
    if($cookie =~ /${HthisFile}TARGETISLANDID=\(([^\)]*)\)/) {
	$defaultTarget = $1;
    }
    if($cookie =~ /${HthisFile}LBBSNAME=\(([^\)]*)\)/) {
	$HdefaultName = $1;
    }
    if($cookie =~ /${HthisFile}POINTX=\(([^\)]*)\)/) {
	$HdefaultX = $1;
    }
    if($cookie =~ /${HthisFile}POINTY=\(([^\)]*)\)/) {
	$HdefaultY = $1;
    }
    if($cookie =~ /${HthisFile}KIND=\(([^\)]*)\)/) {
	$HdefaultKind = $1;
    }
    if($cookie =~ /${HthisFile}LAMOUNT1=\(([^\)]*)\)/) {
	$HdefaultLamount1 = $1;
    }

    if($cookie =~ /${HthisFile}IMGLINE=\(([^\)]*)\)/) {
        $HimgLine = $1;
    }

}

#cookie出力
sub cookieOutput {
    my($cookie, $info);

    # 消える期限の設定
    my($sec, $min, $hour, $date, $mon, $year, $day, $yday, $dummy) =
	gmtime(time + 30 * 86400); # 現在 + 30日

    # 2ケタ化
    $year += 1900;
    if ($date < 10) { $date = "0$date"; }
    if ($hour < 10) { $hour = "0$hour"; }
    if ($min < 10) { $min  = "0$min"; }
    if ($sec < 10) { $sec  = "0$sec"; }

    # 曜日を文字に
    $day = ("Sunday", "Monday", "Tuesday", "Wednesday",
	    "Thursday", "Friday", "Saturday")[$day];

    # 月を文字に
    $mon = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
	    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")[$mon];

    # パスと期限のセット
    $info = "; expires=$day, $date\-$mon\-$year $hour:$min:$sec GMT\n";
    $cookie = '';
    
    if(($HcurrentID) && ($HmainMode eq 'owner')){
	$cookie .= "Set-Cookie: ${HthisFile}OWNISLANDID=($HcurrentID) $info";
    }
    if($HinputPassword) {
	$cookie .= "Set-Cookie: ${HthisFile}OWNISLANDPASSWORD=($HinputPassword) $info";
    }
    if($HcommandTarget) {
	$cookie .= "Set-Cookie: ${HthisFile}TARGETISLANDID=($HcommandTarget) $info";
    }
    if($HlbbsName) {
	$cookie .= "Set-Cookie: ${HthisFile}LBBSNAME=($HlbbsName) $info";
    }
    if($HcommandX) {
	$cookie .= "Set-Cookie: ${HthisFile}POINTX=($HcommandX) $info";
    }
    if($HcommandY) {
	$cookie .= "Set-Cookie: ${HthisFile}POINTY=($HcommandY) $info";
    }
    if($HcommandKind) {
	# 自動系以外
	$cookie .= "Set-Cookie: ${HthisFile}KIND=($HcommandKind) $info";
    }
    if($lamount1) {
	$cookie .= "Set-Cookie: ${HthisFile}LAMOUNT1=($lamount1) $info";
    }

    if($HimgLine) {
        $cookie .= "Set-Cookie: ${HthisFile}IMGLINE=($HimgLine) $info";
    }

    out($cookie);
}

#----------------------------------------------------------------------
# ユーティリティ
#----------------------------------------------------------------------
sub hakolock {
    if($lockMode == 1) {
	# directory式ロック
	return hakolock1();

    } elsif($lockMode == 2) {
	# flock式ロック
	return hakolock2();
    } elsif($lockMode == 3) {
	# symlink式ロック
	return hakolock3();
    } else {
	# 通常ファイル式ロック
	return hakolock4();
    }
}

sub hakolock1 {
    # ロックを試す
    if(mkdir('hakojimalock', $HdirMode)) {
	# 成功
	return 1;
    } else {
	# 失敗
	my($b) = (stat('hakojimalock'))[9];
	if(($b > 0) && ((time() -  $b)> $unlockTime)) {
	    # 強制解除
	    unlock();

	    # ヘッダ出力
	    tempHeader();

	    # 強制解除メッセージ
	    tempUnlock();

	    # フッタ出力
	    tempFooter();

	    # 終了
	    exit(0);
	}
	return 0;
    }
}

sub hakolock2 {
    open(LOCKID, '>>hakojimalockflock');
    if(flock(LOCKID, 2)) {
	# 成功
	return 1;
    } else {
	# 失敗
	return 0;
    }
}

sub hakolock3 {
    # ロックを試す
    if(symlink('hakojimalockdummy', 'hakojimalock')) {
	# 成功
	return 1;
    } else {
	# 失敗
	my($b) = (lstat('hakojimalock'))[9];
	if(($b > 0) && ((time() -  $b)> $unlockTime)) {
	    # 強制解除
	    unlock();

	    # ヘッダ出力
	    tempHeader();

	    # 強制解除メッセージ
	    tempUnlock();

	    # フッタ出力
	    tempFooter();

	    # 終了
	    exit(0);
	}
	return 0;
    }
}

sub hakolock4 {
    # ロックを試す
    if(unlink('key-free')) {
	# 成功
	open(OUT, '>key-locked');
	print OUT time;
	close(OUT);
	return 1;
    } else {
	# ロック時間チェック
	if(!open(IN, 'key-locked')) {
	    return 0;
	}

	my($t);
	$t = <IN>;
	close(IN);
	if(($t != 0) && (($t + $unlockTime) < time)) {
	    # 120秒以上経過してたら、強制的にロックを外す
	    unlock();

	    # ヘッダ出力
	    tempHeader();

	    # 強制解除メッセージ
	    tempUnlock();

	    # フッタ出力
	    tempFooter();

	    # 終了
	    exit(0);
	}
	return 0;
    }
}

# ロックを外す
sub unlock {
    if($lockMode == 1) {
	# directory式ロック
	rmdir('hakojimalock');

    } elsif($lockMode == 2) {
	# flock式ロック
	close(LOCKID);

    } elsif($lockMode == 3) {
	# symlink式ロック
	unlink('hakojimalock');
    } else {
	# 通常ファイル式ロック
	my($i);
	$i = rename('key-locked', 'key-free');
    }
}

# 小さい方を返す
sub min {
    return ($_[0] < $_[1]) ? $_[0] : $_[1];
}

# パスワードエンコード
sub encode {
    if($cryptOn == 1) {
	return crypt($_[0], 'h2');
    } else {
	return $_[0];
    }
}

# パスワードチェック
sub checkPassword {
    my($p1, $p2) = @_;

    # nullチェック
    if($p2 eq '') {
	return 0;
    }

    # マスターパスワードチェック
    if($masterPassword eq $p2) {
	return 1;
    }

    # 本来のチェック
    if($p1 eq encode($p2)) {
	return 1;
    }

    return 0;
}

# 1000億単位丸めルーチン
sub aboutMoney {
    my($m) = @_;
    if($m < 500) {
	return "推定500${HunitMoney}未満";
    } else {
	$m = int(($m + 500) / 1000);
	return "推定${m}000${HunitMoney}";
    }
}

# エスケープ文字の処理
sub htmlEscape {
    my($s) = @_;
    $s =~ s/&/&amp;/g;
    $s =~ s/</&lt;/g;
    $s =~ s/>/&gt;/g;
    $s =~ s/\"/&quot;/g; #"
    return $s;
}

# 80ケタに切り揃え
sub cutColumn {
    my($s, $c) = @_;
    if(length($s) <= $c) {
	return $s;
    } else {
	# 合計80ケタになるまで切り取り
	my($ss) = '';
	my($count) = 0;
	while($count < $c) {
	    $s =~ s/(^[\x80-\xFF][\x80-\xFF])|(^[\x00-\x7F])//;
	    if($1) {
		$ss .= $1;
		$count ++;
	    } else {
		$ss .= $2;
	    }
	    $count ++;
	}
	return $ss;
    }
}

# 島の名前から番号を得る(IDじゃなくて番号)
sub nameToNumber {
    my($name) = @_;

    # 全島から探す
    my($i);
    for($i = 0; $i < $HislandNumber; $i++) {
	if($Hislands[$i]->{'name'} eq $name) {
	    return $i;
	}
    }

    # 見つからなかった場合
    return -1;
}

sub ipToNumber {
    my($ip0) = @_;

    # 全島から探す
    my($i);
    for($i = 0; $i < $HislandNumber; $i++) {
	if($Hislands[$i]->{'ip0'} eq $ip0) {
	    return $i;
	}
    }

    my($ip1) = @_;

    # 全島から探す
    my($i);
    for($i = 0; $i < $HislandNumber; $i++) {
	if($Hislands[$i]->{'ip1'} eq $ip1) {
	    return $i;
	}
    }

    my($ip2) = @_;

    # 全島から探す
    my($i);
    for($i = 0; $i < $HislandNumber; $i++) {
	if($Hislands[$i]->{'ip2'} eq $ip2) {
	    return $i;
	}
    }

    my($ip3) = @_;

    # 全島から探す
    my($i);
    for($i = 0; $i < $HislandNumber; $i++) {
	if($Hislands[$i]->{'ip3'} eq $ip3) {
	    return $i;
	}
    }

    my($ip4) = @_;

    # 全島から探す
    my($i);
    for($i = 0; $i < $HislandNumber; $i++) {
	if($Hislands[$i]->{'ip4'} eq $ip4) {
	    return $i;
	}
    }

    my($ip5) = @_;

    # 全島から探す
    my($i);
    for($i = 0; $i < $HislandNumber; $i++) {
	if($Hislands[$i]->{'ip5'} eq $ip5) {
	    return $i;
	}
    }

    # 見つからなかった場合
    return -1;
}

# 怪獣の情報
sub monsterSpec {
    my($lv) = @_;

    # 種類
    my($kind) = ($lv >> 4) & 31;

    # 名前
    my($name);
    $name = $HmonsterName[$kind];

    # 体力
    my($hp) = ($lv & 15);
    
    return ($kind, $name, $hp);
}

# 経験地からレベルを算出
sub expToLevel {
    my($kind, $exp) = @_;
    my($i);
    if($kind == $HlandBase) {
	# ミサイル基地
	for($i = $maxBaseLevel; $i > 1; $i--) {
	    if($exp >= $baseLevelUp[$i - 2]) {
		return $i;
	    }
	}
	return 1;
    } else {
	# 海底基地
	for($i = $maxSBaseLevel; $i > 1; $i--) {
	    if($exp >= $sBaseLevelUp[$i - 2]) {
		return $i;
	    }
	}
	return 1;
    }

}

# (0,0)から(size - 1, size - 1)までの数字が一回づつ出てくるように
# (@Hrpx, @Hrpy)を設定
sub makeRandomPointArray {
    # 初期値
    my($y);
    @Hrpx = (0..$HislandSize-1) x $HislandSize;
    for($y = 0; $y < $HislandSize; $y++) {
	push(@Hrpy, ($y) x $HislandSize);
    }

    # シャッフル
    my ($i);
    for ($i = $HpointNumber; --$i; ) {
	my($j) = int(rand($i+1)); 
	if($i == $j) { next; }
	@Hrpx[$i,$j] = @Hrpx[$j,$i];
	@Hrpy[$i,$j] = @Hrpy[$j,$i];
    }
}

# 0から(n - 1)の乱数
sub random {
    return int(rand(1) * $_[0]);
}

# 与えた数値に対応する疑似乱数(0から9の整数のみ)
sub seqnum {
    my($v) = sin($_[0] + 1234); # 1234 は任意の整数、乱数の系列を変える
    return (substr($v, -2, 1));
}

#----------------------------------------------------------------------
# ログ表示
#----------------------------------------------------------------------
# ファイル番号指定でログ表示
sub logFilePrint {
    my($fileNumber, $id, $mode) = @_;
    open(LIN, "${HdirName}/hakojima.log$_[0]");
    my($line, $m, $turn, $id1, $id2, $message);
    while($line = <LIN>) {
	$line =~ /^([0-9]*),([0-9]*),([0-9]*),([0-9]*),(.*)$/;
	($m, $turn, $id1, $id2, $message) = ($1, $2, $3, $4, $5);

	# 機密関係
	if($m == 1) {
	    if(($mode == 0) || ($id1 != $id)) {
		# 機密表示権利なし
		next;
	    }
	    $m = '<B>(機密)</B>';
	} else {
	    $m = '';
	}

	# 表示的確か
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

#----------------------------------------------------------------------
# テンプレート
#----------------------------------------------------------------------
# 初期化
sub tempInitialize {
    # 島セレクト(デフォルト自分)
    $HislandList = getIslandList($defaultID);
    $HtargetList = getIslandList($defaultID);
}

# 島データのプルダウンメニュー用
sub getIslandList {
    my($select) = @_;
    my($list, $name, $id, $s, $i);

    #島リストのメニュー
    $list = '';
    for($i = 0; $i < $HislandNumber; $i++) {
	$name = $Hislands[$i]->{'name'};
	$id = $Hislands[$i]->{'id'};
	if($id eq $select) {
	    $s = 'SELECTED';
	} else {
	    $s = '';
	}
	$list .=
	    "<OPTION VALUE=\"$id\" $s>${name}島\n";
    }
    return $list;
}


# ヘッダ
sub tempHeader {

$HislandNextTurn = $HislandTurn + 1;

if($HimgLine ne '' ){
    $baseIMG = $HimgLine;
} else {
    $baseIMG = $imageDir;
}

    out(<<END);
Content-type: text/html

<HTML>
<HEAD>
<TITLE>
$Htitle
</TITLE>
<BASE HREF="$baseIMG/">

<STYLE type="text/css">
<!--

	A:link.type1 { color:#0000FF; text-decoration: none; }

	A:visited.type1 { color:#800080; text-decoration: none; }

	A:hover.type1, A:focus.type1 { color:#0000FF; text-decoration: underline; }

	A:action.type1 { color:#FF0000; text-decoration: underline; }



	A:link.type2 { color:#0000FF; text-decoration: underline; }

	A:visited.type2 { color:#800080; text-decoration: underline; }

	A:hover.type2, A:focus.type2 { color:#FF00FF; text-decoration: underline; }

	A:action.type2 { color:#FF0000; text-decoration: underline; }



	A:link.type3 { color:#0000FF; text-decoration: none; }

	A:visited.type3 { color:#800080; text-decoration: none; }

	A:hover.type3, A:focus.type3 { background-color: pink; color: #FFFFFF; text-decoration: none; }

	A:action.type3 { color:#FF0000; text-decoration: none; }


	/* 観光画面ナビゲータ・ウィンドウ */
	#NaviView{
	  visibility: hidden;
	  z-index:1;
	  position:absolute;
	  background-color: #000000;
	  border: solid #4169E1;
	  border-width: 10px 1px 1px 1px;
	  margin-top : -224px;
	}
	.NaviTitle {
	  color: #ffffff;
	  font-size: 11pt;
	}
	.NaviImg {
	  margin : 1px;
	}
	.NaviText {
	  color: #ffffff;
	  font-size: 9pt;
	}
	TD.M {
	  cursor:default;
	  border-style:outset;
	  border-width:0px;
	  border-color:#CCCCFF;
	}

	body{ scrollbar-3dlight-color:royalblue;
	scrollbar-arrow-color:royalblue;
	scrollbar-darkshadow-color:lemonchiffon;
	scrollbar-face-color:lemonchiffon;
	scrollbar-highlight-color:lemonchiffon;
	scrollbar-shadow-color:royalblue;
	scrollbar-track-color:lemonchiffon;

-->

</STYLE>

</HEAD>
<BODY $htmlBody>
[<A CLASS="type3" HREF="http://t.pos.to/hako/" target="_blank">箱庭諸島スクリプト配布元</A>] [<A CLASS="type3" HREF="http://www5b.biglobe.ne.jp/~k-e-i/" target="_blank">Hakoniwa R.A.スクリプト配布元</A>] [<A CLASS="type3" HREF="$toppage">トップページ</A>]<HR>

<hr WIDTH="100%">
END

}

# フッタ
sub tempFooter {
    my($uti, $sti, $cuti, $csti) = times();
    $uti += $cuti;
    $sti += $csti;
    my($cpu) = $uti + $sti;
    out(<<END);
<HR>
<P align=center>
管理者:$adminName(<A CLASS="type3" HREF="mailto:$email">$email</A>)<BR>
掲示板(<A CLASS="type3" HREF="$bbs">$bbs</A>)<BR>
トップページ(<A CLASS="type3" HREF="$toppage">$toppage</A>)<BR>
箱庭諸島のページ(<A CLASS="type3" HREF="http://www.bekkoame.ne.jp/~tokuoka/hakoniwa.html">http://www.bekkoame.ne.jp/~tokuoka/hakoniwa.html</A>)<BR>
Hakoniwa R.A.のページ(<A CLASS="type3" HREF="http://www5b.biglobe.ne.jp/~k-e-i/">http://www5b.biglobe.ne.jp/~k-e-i/</A>)
<br>

</P>
<DIV align="right">
<SMALL>CPU($cpu) : user($uti) system($sti)</SMALL>
</DIV>
</BODY>
</HTML>
END
}

# ロック失敗
sub tempLockFail {
    # タイトル
    out(<<END);
${HtagBig_}同時アクセスエラーです。<BR>
ブラウザの「戻る」ボタンを押し、<BR>
しばらく待ってから再度お試し下さい。${H_tagBig}$HtempBack
END
}

# 強制解除
sub tempUnlock {
    # タイトル
    out(<<END);
${HtagBig_}前回のアクセスが異常終了だったようです。<BR>
ロックを強制解除しました。${H_tagBig}$HtempBack
END
}

# hakojima.datがない
sub tempNoDataFile {
    out(<<END);
${HtagBig_}データファイルが開けません。${H_tagBig}$HtempBack
END
}

# パスワード間違い
sub tempWrongPassword {
    out(<<END);
${HtagBig_}パスワードが違います。${H_tagBig}$HtempBack
END
}

# 何か問題発生
sub tempProblem {
    out(<<END);
${HtagBig_}問題発生、とりあえず戻ってください。${H_tagBig}$HtempBack
END
}

sub get_host {
	$host = "";
	$addr = "";
	if($Hlipdisp) {
		$host = $ENV{'REMOTE_HOST'};
		$addr = $ENV{'REMOTE_ADDR'};

		if ($get_remotehost) {
			if ($host eq "" || $host eq "$addr") {
				$host = gethostbyaddr(pack("C4", split(/\./, $addr)), 2);
			}
		}
		if ($host eq "") { $host = $addr; }
		
		$addr = "(${addr})";
	}
}


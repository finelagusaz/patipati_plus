#!/usr/bin/perl

use utf8;
use Encode qw/decode encode/;

#=======================================================================================
#				 PatiPati System                                                   Script by HAL
#                                                                 Last Update 2007.3.12(Towa)
#=======================================================================================
require './preset.cgi';
require './sub.pl';
$cgi_file = 'view.cgi';
$cookie_name = 'patipatiview';

if ($ENV{'REQUEST_METHOD'} eq "POST") {
	read(STDIN, $formdata, $ENV{'CONTENT_LENGTH'});
} else { $formdata = $ENV{'QUERY_STRING'}; }
@pairs = split(/&/,$formdata);
foreach my $pair (@pairs) {
	my ($name, $value) = split(/=/, $pair);
	$value =~ tr/+/ /;
	$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
	$value =~ s/</&lt;/g;
	$value =~ s/>/&gt;/g;
	$value =~ s/\n//g;
	$value =~ s/\,//g;
	$QUERY{$name} = $value;
}

# クッキー読み込みのチェック
&get_adcookie;
$passw = $COOKIE{'pass'};

if($QUERY{'passwd'} ne ""){ $passw = $QUERY{'passwd'}; }

if($passw ne $admin_pass){
	binmode(STDOUT, ":utf8");
	print "Content-Type: text/html; charset=UTF-8\n\n";
	print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n";
	print <<"EOM";
<html>
<head><title></title>
<center>
	<form action="$cgi_file" method="post">
	Password <input type="password" name="passwd" size="10">
	<input type="submit" value="login">
	</form>
	</center>
</body></html>
EOM
	exit;
}

$cook="pass<>$passw";
&set_adcookie("60",$cook);

$time_w = time();
$gw = &get_date($time_w);

if($QUERY{'mode'} eq "menu"){ &menu; }
elsif($QUERY{'mode'} eq "view"){ &view; }
elsif($QUERY{'mode'} eq "bin"){ &bin; }
elsif($QUERY{'mode'} eq "bout"){ &bout; }
elsif($QUERY{'mode'} eq "blist"){ &blist; }
elsif($QUERY{'mode'} eq 'logout') { &logout; }
else{ &html; }

#===============================表示HTMLドキュメント作成===========================
sub html {
	# 古いデータ削除
		&del_logs;


	binmode(STDOUT, ":utf8");
	print "Content-Type: text/html; charset=UTF-8\n\n";
	print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n";
	print <<"EOM";
		<html>
		<head><title>PATIPATI LOG</title></head>

		<frameset cols="130,*" frameborder="NO" border="0" framespacing="0">
		  <frame src="$cgi_file?mode=menu" name="patimenu" scrolling="YES" noresize>
		  <frame src="$cgi_file?mode=view" name="patiview">
		</frameset>
		<noframes><body>
		</body></noframes>
		</html>
EOM
		exit;
}

#===============================表示HTMLドキュメント作成===========================
sub menu {
	&log_shushu;
	# ビューリンク作成
		$vlink = ""; $mlink = ""; $last_m = "";
		foreach (@wfilesw){
			my ($yymmw, $dmy) = split(/\./,$_);
			$ymw = substr($yymmw,0,4) .substr($yymmw,4,2);
			$ymw2 = substr($yymmw,0,4) .'/' .substr($yymmw,4,2);
			if($last_m != $ymw){
				#$mlink .= "&nbsp;<a href=\"$cgi_file?mode=view&yymm=$ymw\">$ymw2</a><br>\n";
				$mlink .= "&nbsp;<a href=\"$cgi_file?mode=view&yymm=$ymw\" target=\"patiview\">$ymw2</a><br>\n";
			}
			$ymw = substr($yymmw,0,4) .'/' .substr($yymmw,4,2) .'/' .substr($yymmw,6,2);
			#$vlink .= "<a href=\"$cgi_file?mode=view&yymmdd=$yymmw\">$ymw</a><br>\n";
			$vlink .= "<a href=\"$cgi_file?mode=view&yymmdd=$yymmw\" target=\"patiview\">$ymw</a><br>\n";
			$last_m = substr($yymmw,0,4) .substr($yymmw,4,2);
		}

	binmode(STDOUT, ":utf8");
	print "Content-Type: text/html; charset=UTF-8\n\n";
	print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n";
	print <<"EOM";
		<html>
		<head><title>PATIPATI LOG</title>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<style type="text/css">
		<!--
		body, tr, td { font-size: 10pt; }
		small        { font-size: 8pt; }
		big          { font-size: 12pt; }
		A:link,A:visited,A:active {text-decoration:none;}
		A:link,A:active { color: #6699cc }
		A:visited { color: #336699 }
		A:hover { color: #999999 }
		input,textarea,select {            /* フォーム部品  */
			font-size       :12px;             /* 文字サイズ  */
			color           :#666666;          /*   文字色    */
			background-color:#eeeeee;          /*   背景色    */
			border          :1 solid #999999; /* 枠線スタイル*/
		}
		-->
		</style>
		<base target="patiview">
		</head>
		<body bgcolor="#ffffff" text="#666666">
		<a href="$cgi_file?mode=logout" target=\"_top\">&gt;&gt;ログアウト</a><br><br>
		<a href="$cgi_file?mode=blist">&gt;&gt;ブラックリスト</a><br><br>
		<b><font color="#990000">&lt;月ビュー&gt;</font></b><br>$mlink<br>
		<b><font color="#990000">&lt;日別表示&gt;</font></b><br>
		$vlink
		</body></html>
EOM
	exit;
}
#===============================表示HTMLドキュメント作成===========================
sub view {
	if($hiritsu <= 0){ $hiritsu = 1; }
	if($view_pre == 1 && $QUERY{'yymmdd'} eq "" && $QUERY{'yymm'} eq ""){ $QUERY{'yymm'} = $nen .$tsuki; }
	elsif($QUERY{'yymmdd'} eq ""){ $QUERY{'yymmdd'} = $nen .$tsuki .$hi; }
	$now_date = substr($QUERY{'yymmdd'},0,4) .'/' .substr($QUERY{'yymmdd'},4,2) .'/' .substr($QUERY{'yymmdd'},6,2);
	$log_file = $log_dir .$QUERY{'yymmdd'} .'.cgi'; # ログファイル
	# ブラックリストファイル読み込み
		# エンコーディング自動検出で読み込み
		@blists = &read_file_auto_encoding($ip_ck_file);
	# データ表示
		if($QUERY{'yymm'} ne ""){ # 月データ表示
			&log_shushu;
			$view_data = '
				<table cellspacing=1 cellpadding=4 border=0 bgcolor="#666666">
				<tr><td bgcolor="#eeeeee" align="middle" nowrap>日付</td><td bgcolor="#eeeeee" align="middle" nowrap>回数</td><td bgcolor="#eeeeee" align="middle">コメント</td></tr>
			';
			$gokei = 0; @wks = ();
			foreach (@wfilesw){
				my ($yymmw, $dmy) = split(/\./,$_);
				$ymw = substr($yymmw,0,4) .substr($yymmw,4,2);
				if($QUERY{'yymm'} == $ymw){
					$now_date = substr($yymmw,0,4) .'/' .substr($yymmw,4,2);
					$dw = substr($yymmw,6,2);
					$ymd = $ymw .$dw;
					$log_filew = $log_dir .$ymd .'.cgi'; # ログファイル
					if(-e $log_filew){
						$comm = ""; $shokei = 0;
						# エンコーディング自動検出で読み込み
						@logs = &read_file_auto_encoding($log_filew);
						foreach (@logs) {
							my ($jikanw, $user_ipw, $kaisuw, $comw) = split("<>",$_);
							if($comw ne ""){
								@coms = split(/<#>/,$comw);
								$user_ipc = &encrypt_ip($user_ipw);
								foreach my $cw (@coms){
									if($cw ne ""){
										if($ip_ck == 1){
											$bw = "<a href=\"$cgi_file?mode=bin&day=$ymd&ip=$user_ipc\">ブラックリストへ</a>";
											foreach my $bk(@blists){
												my ($n_ip, $c_ip) = split(/<>/,$bk);
												if($c_ip eq $user_ipc){ $cw = "<font color=\"#ffffff\">$cw</font>"; $bw = "<b><font color=\"#cc3300\">BLACK!</font></b><a href=\"$cgi_file?mode=bout&ip=$user_ipc\">解除</a>"; last; }
											}
											$cw .= " ⇒$bw";
										}
										$comm .= "$cw<hr noshade size=1>";
									}
								}
							}
							$shokei += $kaisuw;
							$gokei += $kaisuw;
							push(@wks,$kaisuw);
						}
					}
					if($comm ne ""){ $comm = substr($comm,0,-19); }
					$width = int($shokei / $hiritsu);
					$view_data .= "<tr bgcolor=\"#ffffff\" valign=\"top\"><td align=\"right\" nowrap><a href=\"" . $cgi_file . "?mode=view&yymmdd=" . $QUERY{'yymm'} . $dw . "\">" . $dw . "日</a></td><td nowrap><img src=\"" . $graph . "\" height=\"12\" width=\"" . $width . "\">&nbsp;" . $shokei . "回</td><td>" . $comm . "&nbsp;</td></tr>\n";
				}
			}
			$view_data .= '</table>';
			if($gokei <= 0){ $view_data = '記録はありませんでした。'; }
			else{
				@wks = sort { $b <=> $a } @wks;
				$view_data .= '<br>連続回数集計<br>';
				$view_data .= '
					<table cellspacing=1 cellpadding=4 border=0 bgcolor="#666666">
					<tr><td bgcolor="#eeeeee" align="middle" nowrap>回数</td><td bgcolor="#eeeeee" align="middle">日数</td></tr>
				';
				$shokei = 0; $last_data = "";
				foreach my $kw (@wks) {
					if($last_data ne "" && $kw ne $last_data){
						$width = int($shokei / $hiritsu);
						$view_data .= "<tr bgcolor=\"#ffffff\"><td align=\"right\" nowrap>" . $last_data . "回&nbsp;</td><td><img src=\"" . $graph . "\" height=\"12\" width=\"" . $width . "\">&nbsp;" . $shokei . "日</td></tr>\n";
						$shokei = 0;
					}
					$shokei++;
					$last_data = $kw;
				}
			$width = int($shokei / $hiritsu);
			$view_data .= "<tr bgcolor=\"#ffffff\"><td align=\"right\" nowrap>" . $last_data . "回</td><td><img src=\"" . $graph . "\" height=\"12\" width=\"" . $width . "\">&nbsp;" . $shokei . "日</td></tr>\n";
			$view_data .= '</table>';
			}
		}
		else{ # 日データ表示
			if(-e $log_file){
				# エンコーディング自動検出で読み込み
				@logs = &read_file_auto_encoding($log_file);
			}
			$view_data = '
				<table cellspacing=1 cellpadding=4 border=0 bgcolor="#666666">
				<tr><td bgcolor="#eeeeee" align="middle" nowrap>時間</td><td bgcolor="#eeeeee" align="middle" nowrap>回数</td><td bgcolor="#eeeeee" align="middle">コメント</td></tr>
			';
			$gokei = 0; $comm = ""; $last_time = ""; $shokei = 0; @wks = ();
			foreach (@logs) {
				my ($jikanw, $user_ipw, $kaisuw, $comw) = split("<>",$_);
				if($last_time ne "" && $jikanw ne $last_time){
					if($comm ne ""){ $comm = substr($comm,0,-19); }
					$width = int($shokei / $hiritsu);
					$view_data .= "<tr bgcolor=\"#ffffff\" valign=\"top\"><td align=\"right\" nowrap>" . $last_time . "時</td><td nowrap><img src=\"" . $graph . "\" height=\"12\" width=\"" . $width . "\">&nbsp;" . $shokei . "回</td><td>" . $comm . "&nbsp;</td></tr>\n";
					$comm = ""; $last_time = ""; $shokei = 0;
				}
				if($comw ne ""){
					@coms = split(/<#>/,$comw);
					foreach my $cw (@coms){
						if($cw ne ""){
							if($ip_ck == 1){
								$user_ipc = &encrypt_ip($user_ipw);
								$bw = "<a href=\"$cgi_file?mode=bin&day=$QUERY{'yymmdd'}&ip=$user_ipc\">ブラックリストへ</a>";
								foreach my $bk(@blists){
									my ($n_ip, $c_ip) = split(/<>/,$bk);
									if($c_ip eq $user_ipc){ $cw = "<font color=\"#ffffff\">$cw</font>"; $bw = "<b><font color=\"#cc3300\">BLACK!</font></b><a href=\"$cgi_file?mode=bout&ip=$user_ipc\">解除</a>"; last; }
								}
								$cw .= " ⇒$bw";
							}
							$comm .= "$cw<hr noshade size=1>";
						}
					}
				}
				$shokei += $kaisuw;
				$gokei += $kaisuw;
				$last_time = $jikanw;
				push(@wks,$kaisuw);
			}
			if($comm ne ""){ $comm = substr($comm,0,-19); }
			$width = int($shokei / $hiritsu);
			$view_data .= "<tr bgcolor=\"#ffffff\" valign=\"top\"><td align=\"right\" nowrap>" . $last_time . "時</td><td nowrap><img src=\"" . $graph . "\" height=\"12\" width=\"" . $width . "\">&nbsp;" . $shokei . "回</td><td>" . $comm . "&nbsp;</td></tr>\n";
			$view_data .= '</table>';
			if($gokei <= 0){ $view_data = '記録はありませんでした。'; }
			else{
				@wks = sort { $b <=> $a } @wks;
				$view_data .= '<br>連続回数集計<br>';
				$view_data .= '
					<table cellspacing=1 cellpadding=4 border=0 bgcolor="#666666">
					<tr><td bgcolor="#eeeeee" align="middle" nowrap>回数</td><td bgcolor="#eeeeee" align="middle">日数</td></tr>
				';
				$shokei = 0; $last_data = "";
				foreach my $kw (@wks) {
					if($last_data ne "" && $kw ne $last_data){
						$width = int($shokei / $hiritsu);
						$view_data .= "<tr bgcolor=\"#ffffff\"><td align=\"right\" nowrap>" . $last_data . "回</td><td><img src=\"" . $graph . "\" height=\"12\" width=\"" . $width . "\">&nbsp;" . $shokei . "日</td></tr>\n";
						$shokei = 0;
					}
					$shokei++;
					$last_data = $kw;
				}
			$width = int($shokei / $hiritsu);
			$view_data .= "<tr bgcolor=\"#ffffff\"><td align=\"right\" nowrap>" . $last_data . "回</td><td><img src=\"" . $graph . "\" height=\"12\" width=\"" . $width . "\">&nbsp;" . $shokei . "日</td></tr>\n";
			$view_data .= '</table>';
			}
		}

	binmode(STDOUT, ":utf8");
	print "Content-Type: text/html; charset=UTF-8\n\n";
	print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n";
	print <<"EOM";
		<html>
		<head><title>PATIPATI LOG</title>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<style type="text/css">
		<!--
		body, tr, td { font-size: 10pt; }
		small        { font-size: 8pt; }
		big          { font-size: 12pt; }
		A:link,A:visited,A:active {text-decoration:none;}
		A:link,A:active { color: #6699cc }
		A:visited { color: #336699 }
		A:hover { color: #999999 }
		input,textarea,select {            /* フォーム部品  */
			font-size       :12px;             /* 文字サイズ  */
			color           :#666666;          /*   文字色    */
			background-color:#eeeeee;          /*   背景色    */
			border          :1 solid #999999; /* 枠線スタイル*/
		}
		-->
		</style>
		<base target="patiview">
		</head>
		<body bgcolor="#ffffff" text="#666666">
		$now_date 総アクセス<big><b>$gokei</b>回</big>
		<hr noshade size=1>
		$view_data
		<hr noshade size=1>- $systeminfo -
		</body></html>
EOM
	exit;
}

#===============================ログファイル収集===========================
sub log_shushu{
	if($shell_use == 1){
		$time_w2 = $time_w - 60*60*24*30*$log_max;
		$dayw = $time_w;
		@wfiles = ();
		while($dayw >= $time_w2){
			$wk = &get_date($dayw);
			$wk = substr($wk,0,8) .'.' .cgi;
			$fck = $log_dir .$wk;
			if(-e $fck){ push(@wfiles,$wk); }
			$dayw -= 60*60*24;
		}
	}else{
		@files = glob("$log_dir*");
		my $i = @files;
		@wfiles = ();
		foreach (@files){
			@dmy = split(/\//,$_);
			$dmy_su = @dmy - 1;
			$fn = $dmy[$dmy_su];
			@dmy = split(/\//,$ip_ck_file);
			$dmy_su = @dmy - 1;
			$ipw = $dmy[$dmy_su];
			$fck = $log_dir .$fn;
			if($fn ne $ipw && (-e $fck)){ push(@wfiles,$fn); }
		}
	}
	@wfilesw = sort { $b <=> $a } @wfiles;
}

#===============================ブラックリスト記録===========================
sub bin{
	$log_file = $log_dir .$QUERY{'day'} .'.cgi'; # ログファイル
	if(-e $log_file){
		# エンコーディング自動検出で読み込み
		@logs = &read_file_auto_encoding($log_file);
		$ipw = "";
		foreach (@logs) {
			my ($jikanw, $user_ipw, $kaisuw, $comw) = split("<>",$_);
			$user_ipc = &encrypt_ip($user_ipw);
			if($user_ipc eq $QUERY{'ip'}){ $ipw = $user_ipw; }
		}
	}
	# エンコーディング自動検出で読み込み
	@blists = &read_file_auto_encoding($ip_ck_file);
	if($ip_ck_su != 0){ while(@blists >= $ip_ck_su){ pop @blists; } }
	unshift(@blists,"$ipw<>$QUERY{'ip'}<>\n");
	open(OUT,">:utf8", "$ip_ck_file") || &error('FILE OPEN ERROR - Black List');
	print OUT @blists;
	close(OUT);
	# 画面表示
    print "Location: $cgi_file?mode=view\n\n";
}

#===============================ブラックリスト解除===========================
sub bout{
	# エンコーディング自動検出で読み込み
	@blists = &read_file_auto_encoding($ip_ck_file);
	@news = ();
	foreach (@blists){
		my ($n_ip, $c_ip) = split(/<>/,$_);
		if($c_ip ne $QUERY{'ip'}){ push(@news,$_); }
	}
	open(OUT,">:utf8", "$ip_ck_file") || &error('FILE OPEN ERROR - Black List');
	print OUT @news;
	close(OUT);
	# 画面表示
    print "Location: $cgi_file?mode=view\n\n";
}

#===============================ブラックリスト表示===========================
sub blist{
	# エンコーディング自動検出で読み込み
	@blists = &read_file_auto_encoding($ip_ck_file);
	$bdata = "";
	foreach my $bk(@blists){
		my ($n_ip, $c_ip) = split(/<>/,$bk);
		$bdata .= "<tr><td bgcolor=\"#ffffff\">$c_ip</td><td bgcolor=\"#ffffff\"><a href=\"$cgi_file?mode=bout&ip=$c_ip\">解除</a></td></tr>";
	}
	binmode(STDOUT, ":utf8");
	print "Content-Type: text/html; charset=UTF-8\n\n";
	print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n";
	print <<"EOM";
		<html>
		<head><title>PATIPATI ブラックリスト表示</title>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<style type="text/css">
		<!--
		body, tr, td { font-size: 10pt; }
		small        { font-size: 8pt; }
		big          { font-size: 12pt; }
		A:link,A:visited,A:active {text-decoration:none;}
		A:link { color: #ff9900 }
		A:active { color: #ffcc00 }
		A:visited { color: #660000 }
		A:hover { color: #ffcc00 }
		-->
		</style>
		<base target="patiview">
		</head>
		<body bgcolor="#ffffff" text="#666666">
		<table cellspacing=1 cellpadding=4 border=0 bgcolor="#666666">
		<tr><td bgcolor="#cccccc">拒否登録されたIP</td><td bgcolor="#cccccc">解除</td></tr>
		$bdata
		</table>
		<hr noshade size=1>- $systeminfo -
		</body></html>
EOM
	exit;
}

#===============================ログアウト判定===========================
sub logout{
	&set_adcookie("0","");
	# 画面表示
    print "Location: $cgi_file?\n\n";
}

#===============================クッキーの取得===========================
sub get_adcookie{
	@pairs = split(/\;/, $ENV{'HTTP_COOKIE'});
	foreach my $pair (@pairs) {
		my ($name, $value) = split(/\=/, $pair);
		$name =~ s/ //g;
		$DUMMY{$name} = $value;
	}
	@pairs = split(/\,/, $DUMMY{$cookie_name});
	foreach my $pair (@pairs) {
		my ($name, $value) = split(/<>/, $pair);
		$COOKIE{$name} = $value;
	}
}

#===============================クッキー発行($days日有効)===========================
sub set_adcookie{
	my $days = $_[0];
	my $cook = $_[1];
	($secg,$ming,$hourg,$mdayg,$mong,$yearg,$wdayg,$dmy,$dmy) = gmtime(time + 60*24*60*$days);
	$yearg += 1900;
	if ($secg  < 10) { $secg  = "0$secg";  }
	if ($ming  < 10) { $ming  = "0$ming";  }
	if ($hourg < 10) { $hourg = "0$hourg"; }
	if ($mdayg < 10) { $mdayg = "0$mdayg"; }
	$month = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')[$mong];
	$youbi = ('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday')[$wdayg];
	$date_gmt = "$youbi, $mdayg\-$month\-$yearg $hourg:$ming:$secg GMT";
	print "Set-Cookie: $cookie_name=$cook; expires=\"$date_gmt\"\n";
}


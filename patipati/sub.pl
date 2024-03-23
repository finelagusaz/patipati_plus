#=======================================================================================
# 共通サブルーチン
#=======================================================================================
$systeminfo = '<a href="http://www.gnbnet.com/" target="_blank">PatiPati (Ver 4.3)</a> + <a href="http://www3.to/gift/" target="_blank">Towa </a>';
$systeminfo2 = '<a href="http://www.gnbnet.com/" target="_blank">PatiPati (Ver 4.3)</a> + <a href="http://www3.to/gift/" target="_blank">Towa </a>';
$salt = 'pt';

#======================================時間取得ルーチン=================================
sub get_date{
	$timew = $_[0];
	$ENV{'TZ'} = "JST-9";
	@date = localtime($timew);
	$nen = $date[5] + 1900;
	$tsuki = sprintf("%02d",$date[4] + 1);
	$hi = sprintf("%02d",$date[3]);
	$jikan = sprintf("%02d",$date[2]);
	$youbi = ('日','月','火','水','木','金','土') [$date[6]];
	$gw = $nen .$tsuki .$hi;
	return $gw;
}

#======================================ロック処理ルーチン=================================
sub lock1 { # flock関数
 	eval { flock( LOCKCHK, 8 ) ; } ;
	if ( ! $@ ){
		open(LOCK,">$lock_file") or die "Can't open lockfile: $!";
	  flock(LOCK, 2) or die "Can't flock        : $!";
	}else{
		&error('このサーバーではflock関数は使えないようです。');
	}
}

sub lock2 { # mkdir関数
	$retry = 5; # リトライ回数セット
	$lockdir = $lock_file;
	$lockdir =~ s/\./_/g;
	$lockdir2 =  'c_' .$lockdir;
	while (!mkdir($lockdir, 0755)) {
		if (--$retry <= 0) {
			if (mkdir($lockdir2, 0755)) {          # ロックを消すための排他
				if ((-M $lockdir) * 86400 > 600) { # 作成時間が10分以上前なら
					rename($lockdir2, $lockdir) or die 'LOCK ERROR'; # ロック入れ替え
					last;                          # 一連の処理へ
				}else { rmdir($lockdir2); }         # 部分ロック削除
			}
			&error("BUSY");
		}
		sleep(1);
	}
}

sub unlock { # ロック解除
	if ($lockkey == 1) { close(LOCK); }
	elsif ($lockkey == 2) {
		$lockdir = $lock_file;
		$lockdir =~ s/\./_/g;
		rmdir($lockdir);
	}
}

#================================過去データ消去処理=================================
sub del_logs{
	$g_mon = $log_dir .'*.' .$kakucho;
	$i = 0;
	while($i <= $log_max){
		$yw = $nen - 1;
		$mw = $tsuki + 12 - $i;
		if($mw > 12){ $yw++; $mw = $mw - 12; }
		$mww = sprintf("%02d",$mw);
		$datew = "$yw$mww" .'31';
		$i++;
	}
	if($shell_use == 1){
		@months = ();
		$dayw = time();
		$dayw = $dayw - 60*60*24*30*$log_max;
		$dayw2 = $dayw - 60*60*24*30*$log_max;
		while($dayw >= $dayw2){
			$wk = &get_date($dayw);
			$wk = $log_dir .substr($wk,0,8) .'.' .$kakucho;
			push(@months,$wk);
			$dayw -= 60*60*24;
		}
	}else{
		@months = glob($g_mon);
	}
	foreach $ml (@months) {
		@ms = split(/\//,$ml);
		$msw = pop(@ms);
		($mw,$ft) = split(/\./,$msw);
		if($mw <= $datew){
			unlink $ml;
		}
	}
}

#================================エラー処理=================================
sub error {
	$error = $_[0];
	if ($error eq "") { $error = '原因不明のエラーで処理を継続できません。'; }
	&jcode'convert(*error,'sjis');
	&unlock; # ロック解除
	open(HTML,"$error_file") || die "FILE OPEN ERROR - error";
	@html = <HTML>;
	close(HTML);
	print "Content-Type: text/html\n\n";
	print "<!DOCTYPE HTML PUBLIC -//IETF//DTD HTML//EN>\n";
	foreach $line (@html) {
		$line =~ s/<!--error-->/$error/g;
		$line =~ s/<!--system-->/$systeminfo/g;
		print $line;
	}
	exit;
}


return 1;

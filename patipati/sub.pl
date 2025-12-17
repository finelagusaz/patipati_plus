#!/usr/bin/perl
use utf8;
use Encode qw/decode encode/;
use Encode::Guess qw/shift_jis euc-jp utf8/;
#=======================================================================================
# 共通サブルーチン
#=======================================================================================
$systeminfo = '<a href="http://www.gnbnet.com/" target="_blank">PatiPati (Ver 4.3)</a> + <a href="http://www3.to/gift/" target="_blank">Towa </a>';
$systeminfo2 = '<a href="http://www.gnbnet.com/" target="_blank">PatiPati (Ver 4.3)</a> + <a href="http://www3.to/gift/" target="_blank">Towa </a>';
$salt = 'pt';

#======================================エンコーディング自動検出でファイルを読み込む=================================
sub read_file_auto_encoding {
	my ($filename) = @_;
	my @lines;

	# ファイルをバイナリモードで読み込み
	open(my $fh, '<', $filename) or return ();
	binmode($fh);
	my $content = do { local $/; <$fh> };
	close($fh);

	# 空ファイルの場合
	return () if length($content) == 0;

	# エンコーディングを推測
	my $enc = guess_encoding($content, qw/utf8 shiftjis euc-jp/);

	if (ref($enc)) {
		# 推測成功：デコードして返す
		my $decoded = $enc->decode($content);
		@lines = split(/\n/, $decoded);
		# 行末の改行を復元
		@lines = map { $_ . "\n" } @lines;
	} else {
		# 推測失敗：UTF-8として読み込む
		@lines = split(/\n/, decode('utf8', $content));
		@lines = map { $_ . "\n" } @lines;
	}

	return @lines;
}

#======================================日時取得ルーチン=================================
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

#======================================ロック用ルーチン=================================
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
			if (mkdir($lockdir2, 0755)) {          # ロック掛かっている人以外
				if ((-M $lockdir) * 86400 > 600) { # 最終時間が10分以上経過なら
					rename($lockdir2, $lockdir) or die 'LOCK ERROR'; # ロック無理矢理
					last;                          # 繰り返し処理終了
				}else { rmdir($lockdir2); }         # 十分経ってない
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

#================================ログ削除処理=================================
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
	if ($error eq "") { $error = '予期しないエラーで処理が継続できません。'; }
	# UTF-8で出力（Encodeモジュールは不要、binmode設定）
	&unlock; # ロック解除
	open(HTML,"$error_file") || die "FILE OPEN ERROR - error";
	@html = <HTML>;
	close(HTML);
	print "Content-Type: text/html; charset=UTF-8\n\n";
	print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n";
	foreach $line (@html) {
		$line =~ s/<!--error-->/$error/g;
		$line =~ s/<!--system-->/$systeminfo/g;
		print $line;
	}
	exit;
}


return 1;

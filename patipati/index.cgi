#!/usr/bin/perl
use utf8;
use Encode qw/decode encode/;
use Encode::Guess qw/shift_jis euc-jp utf8/;

#=======================================================================================
#				 PatiPati System                                                   Script by HAL
#                                                                 Last Update 2007.3.10(Towa)
#=======================================================================================
require './preset.cgi';
require './sub.pl';
$cookie_name = 'patipati';

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
	# エンコーディング自動検出でデコード（Shift_JIS/EUC-JP/UTF-8に対応）
	if (length($value) > 0) {
		eval {
			my $enc = guess_encoding($value, qw/utf8 shiftjis euc-jp/);
			if (ref($enc)) {
				$value = $enc->decode($value);
			} else {
				# 推測失敗時はUTF-8として扱う
				$value = decode('utf8', $value);
			}
		};
		# デコードエラー時はそのまま使用
		if ($@) {
			$value = decode('utf8', $value, Encode::FB_QUIET);
		}
	}
	$QUERY{$name} = $value;
}

#================================メイン処理=================================
	&get_cookie;
	&Setdirectory;
	if(!(-e $ip_ck_file)){ # ブラックリスティングファイルがない場合は作成
				open(OUT,">$ip_ck_file");
				print OUT "";
				close(OUT);
				chmod (0666,$ip_ck_file);

			}

	if(!(-e $Gindex)){ # index.htmlがない場合は作成
				open(OUT,">$Gindex") || &error('FILE OPEN ERROR - log');
				print OUT "<Content-type: text/html>";
				close(OUT);

			}
	if($COOKIE{'f'} == 1){
		open(HTML,"<:utf8", "$last_file") || &error("ファイルオープンに失敗しました - $last_file");
		@htmls = <HTML>;
		close(HTML);
	}else{
		$time_w = time();
		$QUERY{'pkai'}++;
		$hidden = "<input type=\"hidden\" name=\"pkai\" value=\"$QUERY{'pkai'}\">";
		$gn = &get_date($time_w);
		# 旧データ削除
			&del_logs;
		$gn = &get_date($time_w);
		$user_ipg = $ENV{'REMOTE_ADDR'};
		$crypt_ip = &encrypt_ip($user_ipg);
		# ブラックリスト判断
			$bk_ck = 0;
			if($ip_ck == 1){
				# エンコーディング自動検出で読み込み
				@blists = &read_file_auto_encoding($ip_ck_file);
			}

			# スパム対策チェック
			&check_spam($QUERY{'com'}, $kickurl, $delspam);

			foreach my $bk(@blists){
				my ($n_ip, $c_ip) = split(/<>/,$bk);
				if($c_ip eq $crypt_ip){ $bk_ck = 1; last; }
			}

		if($ip_ck == 1 && $bk_ck == 1 && $ip_ck_msg ne ""){ &error("$ip_ck_msg"); }
		if($bk_ck == 0){
			my $i = 1;
			while($i <= $sub_su){
				my $wk = 'sub' .$i;
				if($QUERY{$wk} ne ""){
					$QUERY{$wk} =~ s/\r\n//g;
					$QUERY{$wk} =~ s/\r//g;
					$QUERY{$wk} =~ s/\n//g;
					$QUERY{'com'} .= "【$QUERY{$wk}】";
				}
				$i++;
			}
			$QUERY{'com'} =~ s/\r\n/\n/g;
			$QUERY{'com'} =~ s/\r/\n/g;
			$msg = $QUERY{'com'};
			$msgw = $msg;
			$msgw =~ tr/A-Z/a-z/;
			if($com_jisu != 0 && $com_jisu < length($msg)){ &error("すみません。メッセージは半角$com_jisu文字（全角の場合その半分）までです。"); }
			if($delspam ne "1") {
			if(($msg ne "") && ($msg !~ m/[\x80-\xff]/)) {&error('変数：半角のみ引っ掛けはスパム禁止のため送信できません。'); }
			}

			$ng_ck = 0;
			if($msg ne ""){
				foreach my $ngw (@ngs){
					$ngw =~ tr/A-Z/a-z/;
					if($ngw ne "" && index($msgw,$ngw) >= 0){ $ng_ck = 1; }
				}
			}
			if($ng_ck == 1 && $ng_ck_msg ne ""){ &error($ng_ck_msg); }
			elsif($ng_ck == 0){
				$QUERY{'com'} =~ s/\n/<br>/g;
				$log_file = $log_dir .$gw .'.cgi'; # ログファイル
				# ロック開始
					if ($lockkey == 1) { &lock1; }
					elsif ($lockkey == 2) { &lock2; }
				if(!(-e $log_file)){ # ログファイルがない場合は作成
					open(OUT,">:utf8", "$log_file") || &error('FILE OPEN ERROR - log');
					print OUT "";
					close(OUT);
					chmod (0666,$log_file);
				}
				# エンコーディング自動検出で読み込み（既存ログとの互換性のため）
				@logs = &read_file_auto_encoding($log_file);
				@news = ();
				$kaisu = 1;
				foreach (@logs) {
					my ($jikanw, $user_ipw, $kaisuw, $comw) = split("<>",$_);
					$user_ipc = &encrypt_ip($user_ipw);
					if($user_ipg eq $user_ipw && $jikanw eq $jikan){
						$kaisu = $kaisuw + 1;
						if($QUERY{'com'} ne ""){ $QUERY{'com'} = $comw ."<#>$QUERY{'com'}"; }
						else{ $QUERY{'com'} = $comw; }
					}else{ push(@news,$_); }
				}
				if($clap_su == 0 || $kaisu <= $clap_su){
					push(@news,"$jikan<>$user_ipg<>$kaisu<>$QUERY{'com'}<>\n");
					@sorted = sort { $a <=> $b } @news;
					open(OUT,">:utf8", "$log_file") || &error('FILE OPEN ERROR - log');
					print OUT @sorted;
					close(OUT);
				}

				&unlock; # ロック解除
				if($msg ne "" && $mail_ck == 1){ &mail; }
			}
	  }
		my $ifile = @location_files;
		if($locate_rand == 1){
			srand;
			my $r = int(rand($ifile));
			$location_file = @location_files[$r];
		}elsif($locate_rand == 2){
			my $i = $kaisu;
			$location_file = @location_files[$i-1];
			if($i >= $ifile){ $location_file = @location_files[$ifile-1]; }
		}else{
			my $i = $kaisu;
			while($i > $ifile){ $i -= $ifile; }
			$location_file = @location_files[$i-1];
		}
		if($clap_su != 0 && $kaisu >= $clap_su){
			&set_cookie();
			open(HTML,"<:utf8", "$last_file") || &error("ファイルオープンに失敗しました - $last_file");
			@htmls = <HTML>;
			close(HTML);
		}else{
			open(HTML,"<:utf8", "$location_file") || &error("ファイルオープンに失敗しました - $location_file");
			@htmls = <HTML>;
			close(HTML);
		}
	}

			# スパム対策チェック（$msgに対して、半角チェック無効で実行）
			&check_spam($msg, $kickurl, "1");

	if ($msg ne "") {
		$msg_in = $msg;
		$comment_over = "以下のメッセージを送信しました。";
	}
	if ($clap_su eq "0") {
		$clap_su_v = "制限無効";
		$clap_su_v2 = "回";
	}else{
		$clap_su_v = $clap_su;
		$clap_su_v2 = "回まで";
	}

	if ($com_jisu eq "0") {
		$moji_hmax_v = "無制限";
		$moji_hmax_v2 = "字";
		$moji_zmax = "無制限";
		$moji_zmax_v2 = "字";
	}else{
		$moji_hmax_v = $com_jisu;
		$moji_hmax_v2 = "文字";
		$moji_zmax = int($com_jisu / 2);
		$moji_zmax_v2 = "文字";
	}

	$html = "";
	foreach (@htmls) { $html .= $_; }
	$html =~ s/<!--cgi-->/$cgi_file/g;
	$html =~ s/<!--hidden-->/$hidden/g;
	$html =~ s/<!--clap_su-->/$clap_su_v/g;
	$html =~ s/<!--clap_su_v2-->/$clap_su_v2/g;
	$html =~ s/<!--comment_t-->/$comment_over/g;
	$html =~ s/<!--comment_v-->/$msg_in/g;
	$html =~ s/<!--clap_kankaku-->/$clap_kankaku/g;
	$html =~ s/<!--moji_hmax-->/$moji_hmax_v/g;
	$html =~ s/<!--moji_hmax_v2-->/$moji_hmax_v2/g;
	$html =~ s/<!--moji_zmax-->/$moji_zmax/g;
	$html =~ s/<!--moji_zmax_v2-->/$moji_zmax_v2/g;
	$html =~ s/<!--system-->/$systeminfo/g;

	# UTF-8で出力
	binmode(STDOUT, ":utf8");
	print "Content-Type: text/html; charset=UTF-8\n\n";
	print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n";
	print $html;
	exit;


#================================メール転送処理=================================
sub mail{
	# メール送信時はISO-2022-JPにエンコード
	my $subject_jis = encode('iso-2022-jp', $subject);
	my $msg_jis = encode('iso-2022-jp', $msg);

	foreach my $mlw (@mailtos){
		my $mailtow = $mlw;
		if (!open(MAIL,"| $sendmail $mailtow")) { &error('何らかの原因で送信できませんでした。'); }
			print MAIL "X-Mailer: GNBSys\n";
			print MAIL "To: $mailtow\n";
			print MAIL "From: $mailtow\n";
			print MAIL "Subject: $subject_jis\n";
			print MAIL "Content-Transfer-Encoding: 7bit\n";
			print MAIL "Content-Type: text/plain\; charset=\"ISO-2022-JP\"\n\n";
			print MAIL "$msg_jis";
			close(MAIL);
	}
}

#===============================クッキーの取得===========================
sub get_cookie{
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

#===============================クッキーの発行(60分有効)===========================
sub set_cookie{
	($secg,$ming,$hourg,$mdayg,$mong,$yearg,$wdayg,$dmy,$dmy)
					 	= gmtime(time + 60*60*$clap_kankaku);
	$yearg += 1900;
	if ($secg  < 10) { $secg  = "0$secg";  }
	if ($ming  < 10) { $ming  = "0$ming";  }
	if ($hourg < 10) { $hourg = "0$hourg"; }
	if ($mdayg < 10) { $mdayg = "0$mdayg"; }

	$month = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')[$mong];
	$youbi = ('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday')[$wdayg];
	$date_gmt = "$youbi, $mdayg\-$month\-$yearg $hourg:$ming:$secg GMT";
	$cook="f<>1";
	print "Set-Cookie: $cookie_name=$cook; expires=\"$date_gmt\"\n";
}

#---------------------------------ディレクトリ生成--------------------------
sub Setdirectory{
	$LockDirc = "lock";
	( mkdir $log_dir );
	( mkdir $LockDirc );
	chmod (0777,$log_dir);
	chmod (0777,$LockDirc);
	$firstset = 1;
}

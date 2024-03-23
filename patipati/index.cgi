#!/usr/bin/perl

#=======================================================================================
#				 PatiPati System                                                   Script by HAL
#                                                                 Last Update 2007.3.10(Towa)
#=======================================================================================
require 'preset.cgi';
require 'sub.pl';
require $jcode;
$cookie_name = 'patipati';

if ($ENV{'REQUEST_METHOD'} eq "POST") {
	read(STDIN, $formdata, $ENV{'CONTENT_LENGTH'});
} else { $formdata = $ENV{'QUERY_STRING'}; }
@pairs = split(/&/,$formdata);
foreach $pair (@pairs) {
	($name, $value) = split(/=/, $pair);
	$value =~ tr/+/ /;
	$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
	$value =~ s/</&lt;/g;
	$value =~ s/>/&gt;/g;
	$value =~ s/\n//g;
	$value =~ s/\,//g;
	&jcode'convert(*value,'euc');
	$QUERY{$name} = $value;
}

#================================�ᥤ�����=================================
	&get_cookie;
	&Setdirectory;
	if(!(-e $ip_ck_file)){ # �֥�å��ꥹ�ƥ��󥰥ե����뤬�ʤ���������
				open(OUT,">$ip_ck_file");
				print OUT "";
				close(OUT);
				chmod (0666,$ip_ck_file);

			}

	if(!(-e $Gindex)){ # index.html���ʤ���������
				open(OUT,">$Gindex") || &error('FILE OPEN ERROR - log');
				print OUT "<Content-type: text/html>";
				close(OUT);

			}
	if($COOKIE{'f'} == 1){
		open(HTML,"$last_file") || die "�ե����륪���ץ�˼��Ԥ��ޤ��� - design";
		@htmls = <HTML>;
		close(HTML);
	}else{
		$time_w = time();
		$QUERY{'pkai'}++;
		$hidden = "<input type=\"hidden\" name=\"pkai\" value=\"$QUERY{'pkai'}\">";
		$gn = &get_date($time_w);
		# ���ǡ����õ�
			&del_logs;
		$gn = &get_date($time_w);
		$user_ipg = $ENV{'REMOTE_ADDR'};
		# crypt
			$ic = length($user_ipg) / 8;
			if(length($user_ipg) % 8 != 0){ $ic++; }
			$i = 0; $crypt_ip = "";
			while($i <= $ic){
				$keta = $i*8;
				$crypt_ip .= crypt(substr($user_ipg,$keta,8),$salt);
				$i++;
			}
		# �֥�å��ꥹ�Ƚ���
			$bk_ck = 0;
			if($ip_ck == 1){
				open(BLT,"$ip_ck_file") || &error('FILE OPEN ERROR - Black List');
				@blists = <BLT>;
				close(BLT);
			}

			#URL���ѥ��к���
			if($kickurl eq 1) {
			if($QUERY{'com'} =~ "http") {&error('URL�����ä�ʸ�Ϥϥ��ѥ��к��Τ��᤽�ΤޤޤǤ������Ǥ��ޤ���<br>Ƭ�Σ��ȴ���ʤɤ����������Ƥ���������'); }
			}
			#�ѿ�Ⱦ���к�
			if($delspam ne "0") {
			if(($QUERY{'com'} ne "") && ($QUERY{'com'} !~ m/[\x80-\xff]/)) {&error('�ѿ�Ⱦ�ѤΤߤ���Ƥϥ��ѥ��ɻߤΤ��������Ǥ��ޤ���'); }
			}

			foreach $bk(@blists){
				($n_ip,$c_ip) = split(/<>/,$bk);
				if($c_ip eq $crypt_ip){ $bk_ck = 1; last; }
			}
			
		if($ip_ck == 1 && $bk_ck == 1 && $ip_ck_msg ne ""){ &error("$ip_ck_msg"); }
		if($bk_ck == 0){
			$i = 1;
			while($i <= $sub_su){
				$wk = 'sub' .$i;
				if($QUERY{$wk} ne ""){
					$QUERY{$wk} =~ s/\r\n//g;
					$QUERY{$wk} =~ s/\r//g;
					$QUERY{$wk} =~ s/\n//g;
					$QUERY{'com'} .= "��$QUERY{$wk}��";
				}
				$i++;
			}
			$QUERY{'com'} =~ s/\r\n/\n/g;
			$QUERY{'com'} =~ s/\r/\n/g;
			$msg = $QUERY{'com'};
			$msgw = $msg;
			$msgw =~ tr/A-Z/a-z/;
			if($com_jisu != 0 && $com_jisu < length($msg)){ &error("�����Ǥ����å�������Ⱦ��$com_jisuʸ�������Ѥξ�礽��Ⱦʬ�ˤޤǤǤ���"); }
			if($delspam ne "1") {
			if(($msg ne "") && ($msg !~ m/[\x80-\xff]/)) {&error('�ѿ�Ⱦ�ѤΤߤ���Ƥϥ��ѥ��ɻߤΤ��������Ǥ��ޤ���'); }
			}

			$ng_ck = 0;
			if($msg ne ""){
				foreach $ngw (@ngs){
					&jcode'convert(*ngw,'euc');
					$ngw =~ tr/A-Z/a-z/;
					if($ngw ne "" && index($msgw,$ngw) >= 0){ $ng_ck = 1; }
				}
			}
			if($ng_ck == 1 && $ng_ck_msg ne ""){ &error($ng_ck_msg); }
			elsif($ng_ck == 0){
				$QUERY{'com'} =~ s/\n/<br>/g;
				$log_file = $log_dir .$gw .'.cgi'; # ���ե�����
				# ��å�����
					if ($lockkey == 1) { &lock1; }
					elsif ($lockkey == 2) { &lock2; }
				if(!(-e $log_file)){ # ���ե����뤬�ʤ���������
					open(OUT,">$log_file") || &error('FILE OPEN ERROR - log');
					print OUT "";
					close(OUT);
					chmod (0666,$log_file);
				}
				open(LOG,"$log_file") || &error('FILE OPEN ERROR - log');
				@logs = <LOG>;
				close(LOG);
				@news = ();
				$kaisu = 1;
				foreach (@logs) {
					($jikanw,$user_ipw,$kaisuw,$comw) = split("<>",$_);
					# crypt
						$ic = length($user_ipw) / 8;
						if(length($user_ipw) % 8 != 0){ $ic++; }
						$i = 0; $user_ipc = "";
						while($i <= $ic){
							$keta = $i*8;
							$user_ipc .= crypt(substr($user_ipw,$keta,8),$salt);
							$i++;
					}
					if($user_ipg eq $user_ipw && $jikanw eq $jikan){
						$kaisu = $kaisuw + 1;
						if($QUERY{'com'} ne ""){ $QUERY{'com'} = $comw ."<#>$QUERY{'com'}"; }
						else{ $QUERY{'com'} = $comw; }
					}else{ push(@news,$_); }
				}
				if($clap_su == 0 || $kaisu <= $clap_su){
					push(@news,"$jikan<>$user_ipg<>$kaisu<>$QUERY{'com'}<>\n");
					@sorted = sort { $a <=> $b } @news;
					open(OUT,">$log_file") || &error('FILE OPEN ERROR - log');
					print OUT @sorted;
					close(OUT);
				}

			#URL���ѥ��к���
			if($kickurl eq 1) {
			if($QUERY{'com'} =~ "http") {&error('URL�����ä�ʸ�Ϥϥ��ѥ��к��Τ��᤽�ΤޤޤǤ������Ǥ��ޤ���<br>Ƭ�Σ��ȴ���ʤɤ����������Ƥ���������'); }
			}
			#�ѿ�Ⱦ���к�
			if($delspam ne "0") {
			if(($QUERY{'com'} ne "") && ($QUERY{'com'} !~ m/[\x80-\xff]/)) {&error('�ѿ�Ⱦ�ѤΤߤ���Ƥϥ��ѥ��ɻߤΤ��������Ǥ��ޤ���'); }
			}

				&unlock; # ��å����
				if($msg ne "" && $mail_ck == 1){ &mail; }
			}
	  }
		$ifile = @location_files;
		if($locate_rand == 1){
			srand;
			$r = int(rand($ifile));
			$location_file = @location_files[$r];
		}elsif($locate_rand == 2){
			$i = $kaisu;
			$location_file = @location_files[$i-1];
			if($i >= $ifile){ $location_file = @location_files[$ifile-1]; }
		}else{
			$i = $kaisu;
			while($i > $ifile){ $i -= $ifile; }
			$location_file = @location_files[$i-1];
		}
		if($clap_su != 0 && $kaisu >= $clap_su){
			&set_cookie();
			open(HTML,"$last_file") || die "�ե����륪���ץ�˼��Ԥ��ޤ��� - design";
			@htmls = <HTML>;
			close(HTML);
		}else{
			open(HTML,"$location_file") || die "�ե����륪���ץ�˼��Ԥ��ޤ��� - design";
			@htmls = <HTML>;
			close(HTML);
		}
	}

			#�ѿ�Ⱦ���к�
			if($delspam ne "0") {
			if(($msg ne "") && ($QUERY{'com'} !~ m/[\x80-\xff]/)) {&error('�ѿ�Ⱦ�ѤΤߤ���Ƥϥ��ѥ��ɻߤΤ��������Ǥ��ޤ���'); }
			}


			#URL���ѥ��к���
			if($kickurl eq 1) {
			if($msg =~ "http") {&error('URL�����ä�ʸ�Ϥϥ��ѥ��к��Τ��᤽�ΤޤޤǤ������Ǥ��ޤ���<br>Ƭ�Σ��ȴ���ʤɤ����������Ƥ���������'); }
			};

	if ($msg ne "") {
		($msg_in = $msg);
		&jcode'convert(*msg_in,'sjis');
		($comment_over = "�ʲ��Υ�å���������������ޤ�����");
		&jcode'convert(*comment_over,'sjis');
	}
	if ($clap_su eq "0") {
		($clap_su_v = "����̵��");
		($clap_su_v2 = "��");
		&jcode'convert(*clap_su_v,'sjis');
		&jcode'convert(*clap_su_v2,'sjis');
	}else{
		($clap_su_v = $clap_su);
		($clap_su_v2 = "��ޤ�");
		&jcode'convert(*clap_su_v2,'sjis');
	}

	if ($com_jisu eq "0") {
		($moji_hmax_v = "̵����");
		($moji_hmax_v2 = "��");
		($moji_zmax = "̵����");
		($moji_zmax_v2 = "��");
		&jcode'convert(*moji_hmax_v,'sjis');
		&jcode'convert(*moji_hmax_v2,'sjis');
		&jcode'convert(*moji_zmax,'sjis');
		&jcode'convert(*moji_zmax_v2,'sjis');
	}else{
		($moji_hmax_v = $com_jisu);
		($moji_hmax_v2 = "ʸ��");
		&jcode'convert(*moji_hmax_v2,'sjis');
		($moji_zmax = int($com_jisu / 2));
		($moji_zmax_v2 = "ʸ��");
		&jcode'convert(*moji_zmax_v2,'sjis');
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
		#$moji_zmax = int($com_jisu / 2) ; ���ꥸ�ʥ�ν���
	$html =~ s/<!--moji_zmax-->/$moji_zmax/g;
	$html =~ s/<!--moji_zmax_v2-->/$moji_zmax_v2/g;
	$html =~ s/<!--system-->/$systeminfo/g;
	print "Content-Type: text/html; charset=Shift_JIS\n\n";
		#print "Content-Type: text/html;charset=EUC-JP\n\n"; ���ꥸ�ʥ�ν���
	print "<!DOCTYPE HTML PUBLIC -//IETF//DTD HTML//EN>\n";
	print $html;
	exit;


#================================�᡼��ž������=================================
sub mail{
	&jcode'convert(*subject,'jis');
	&jcode'convert(*msg,'jis');

	foreach $mlw (@mailtos){
		$mailtow = $mlw;
		if (!open(MAIL,"| $sendmail $mailtow")) { &error('���餫�θ����������Ǥ��ޤ���Ǥ�����'); }
			print MAIL "X-Mailer: GNBSys\n";
			print MAIL "To: $mailtow\n";
			print MAIL "From: $mailtow\n";
			print MAIL "Subject: $subject\n";
			print MAIL "Content-Transfer-Encoding: 7bit\n";
			print MAIL "Content-Type: text/plain\; charset=\"ISO-2022-JP\"\n\n";
			print MAIL "$msg";
			close(MAIL);
	}
}

#===============================���å����μ���===========================
sub get_cookie{
	@pairs = split(/\;/, $ENV{'HTTP_COOKIE'});
	foreach $pair (@pairs) {
		local($name, $value) = split(/\=/, $pair);
		$name =~ s/ //g;
		$DUMMY{$name} = $value;
	}
	@pairs = split(/\,/, $DUMMY{$cookie_name});
	foreach $pair (@pairs) {
		local($name, $value) = split(/<>/, $pair);
		$COOKIE{$name} = $value;
	}
}

#===============================���å�����ȯ��(60����ͭ��)===========================
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

#---------------------------------�ǥ��쥯�ȥ��������--------------------------
sub Setdirectory{
	$LockDirc = "lock";
	( mkdir $log_dir );
	( mkdir $LockDirc );
	chmod (0777,$log_dir);
	chmod (0777,$LockDirc);
	$firstset = 1;
}

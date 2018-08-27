#!/usr/local/bin/perl

use DBI;
use MIME::Lite;
use lib_cmts;
use lib_equipment;

my ($sec, $min, $hour, $mday, $mon, $year) = localtime();
#print "mday: $mday\n";
#print "mon: $mon\n";
#print "year: $year\n";
@month = ('1', '2', '3','4','5','6','7','8','9','10','11','12');
#           0      1      2      3      4       5    6       7     8      9       10     11
@month = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC');
#		   31	  28	 31      30     31     30	 31      31    30      31     30     31
$year = $year+1900;
$mday = $mday-1;

if($mday == 1){
	if($mon == 2){
		$mday = 28;
		$mon--;
	}elsif($mon == 3 || $mon == 5 || $mon == 8 || $mon == 10){
		$mday = 31;
		$mon--;
	}elsif($mon == 4 || $mon == 6 || $mon == 9 || $mon == 11){
		$mday = 30;
		$mon--;
	}
	if(length($mday) eq 1){
		$mday = 0 . $mday;
	}
	$start_time = $mday . "-" . $month[$mon] . "-" . $year . "-12";
	$end_time = $mday . "-" . $month[$mon] . "-" . $year . "-14";
}else{
	if(length($mday) eq 1){
		$mday = 0 . $mday;
	}
	$start_time = $mday . "-" . $month[$mon] . "-" . $year . "-12";
	$end_time = $mday . "-" . $month[$mon] . "-" . $year . "-14";
}

#print "$start_time\n";
#print "$end_time\n";

$ENV{'ORACLE_HOME'} = "/home/oracle/product/10.2.0/blackcap";
my $PRIMAL_DN = "dbi:Oracle:host=REDACTED;sid=REDACTED;port=1521";
my $PRIMAL_CU = "REDACTED";
my $PRIMAL_CP = "REDACTED";
my $modem = "REDACTED";
my $st = "SELECT substr(SUM(DELTA_OCTETS_PASSED)/1024/1024,0,6) as MB_USED,SUBSCRIBER_ID from RA_SAMIS_RAW where SUBSCRIBER_ID = \'$modem\' and IPDR_CREATION_TIME between to_date(\'";
$st = $st . "$start_time\','dd-mon-yyyy-HH24') and  to_date(\'$end_time\','dd-mon-yyyy-HH24') group by SUBSCRIBER_ID";


my $ch = DBI->connect( $PRIMAL_DN, $PRIMAL_CU, $PRIMAL_CP );
my $qh = $ch->prepare($st);
my $re = $qh->execute;
my($usage,$mac) = $qh->fetchrow_array();

if (!defined($usage)){
	$html = "<html>Primal Verification Script. The following Modem has usage outside of the scope during the time period of 12:00 and 14:00 hours. ";
	$html = $html . "The usage expected is supposed to be between 4.2 GB and 4.5 GB. ";
	$html = $html . "The modem is on top of the rack in the NOC and is labeled Primal Verify Modem. The machine connected to it has a scheduled task to download the CentOS ISO everyday. ";
	$html = $html . "Validate the modem is online, the machine is online and the scheduled task is running successfully.";
	$modem = &equipment_format_docsis_dot($modem);
	$state = &cm_state_by_mac($modem);
	$html = $html . "<br><table border=\"1\">\n<th>Modem</th><th>Modem State</th><th>Usage</th></tr>\n";
	$html = $html . "<tr><td>$modem</td><td>$state</td><td></td></tr></table>\n";
	&email_alert($html);
}elsif ($usage lt 4200){;
	$html = "<html>Primal Verification Script. The following Modem has usage outside of the scope during the time period of 12:00 and 14:00 hours. ";
	$html = $html . "The usage expected is supposed to be between 4.2 GB and 4.5 GB. ";
	$html = $html . "The modem is on top of the rack in the NOC and is labeled Primal Verify Modem. The machine connected to it has a scheduled task to download the CentOS ISO everyday. ";
	$html = $html . "Validate the modem is online, the machine is online and the scheduled task is running successfully.";
	$modem = &equipment_format_docsis_dot($modem);
	$state = &cm_state_by_mac($modem);
	$html = $html . "<br><table border=\"1\">\n<th>Modem</th><th>Modem State</th><th>Usage</th></tr>\n";
	$html = $html . "<tr><td>$modem</td><td>$state</td><td>$usage</td></tr></table>\n";
	&email_alert($html);
}elsif($usage gt 4500){
	$html = "<html>Primal Verification Script. The following Modem has usage outside of the scope during the time period of 12:00 and 14:00 hours. ";
	$html = $html . "The usage expected is supposed to be between 4.2 GB and 4.5 GB. ";
	$html = $html . "The modem is on top of the rack in the NOC and is labeled Primal Verify Modem. The machine connected to it has a scheduled task to download the CentOS ISO everyday. ";
	$html = $html . "Validate the modem is online, the machine is online and the scheduled task is running successfully.";
	$modem = &equipment_format_docsis_dot($modem);
	$state = &cm_state_by_mac($modem);
	$html = $html . "<br><table border=\"1\">\n<th>Modem</th><th>Modem State</th><th>Usage</th></tr>\n";
	$html = $html . "<tr><td>$modem</td><td>$state</td><td>$usage</td></tr></table>\n";
	&email_alert($html);
}else{
	$html = "<html>Primal Verification Script. The following Modem has usage inside of the scope during the time period of 12:00 and 14:00 hours. ";
	$html = $html . "The usage expected is supposed to be between 4.2 GB and 4.5 GB and it is inside that scope. ";
	$html = $html . "The modem is on top of the rack in the NOC and is labeled Primal Verify Modem. The machine connected to it has a scheduled task to download the CentOS ISO everyday. ";
	$html = $html . "Validate the modem is online, the machine is online and the scheduled task is running successfully.";
	$modem = &equipment_format_docsis_dot($modem);
	$state = &cm_state_by_mac($modem);
	$html = $html . "<br><table border=\"1\">\n<th>Modem</th><th>Modem State</th><th>Usage</th></tr>\n";
	$html = $html . "<tr><td>$modem</td><td>$state</td><td>$usage</td></tr></table>\n";
	&email_alert($html);
}

sub email_alert($){
	$html = $_[0];
	my $to_email = 'REDACTED';
	my $msg = MIME::Lite->new(
		Subject => "Primal Verification Script",
		From    => 'REDACTED',
		To      => $to_email,
		Type    => 'text/html',
		Data    => $html
	);
	$msg->send('smtp','REDACTED', Debug=>0 );

}

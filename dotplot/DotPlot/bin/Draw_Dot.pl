#!/usr/bin/perl -w
use strict;
BEGIN{push @INC,'../SVG';}
use SVGLAB;
use Getopt::Long;

my ($width,$high,$edge);
my ($Qinfo,$Tinfo);
my ($Qcol,$Tcol,$Scol);
my $ShowLN;
my ($XtR,$YtR);
my ($ShowCoor,$Win);
my ($Qgff,$Tgff);
my ($GeneW,$GeneStr);
GetOptions(
	"w:i"	=>	\$width,
	"h:i"	=>	\$high,
	"e:i"	=>	\$edge,

	"Qinfo:s"=>	\$Qinfo,
	"Tinfo:s"=>	\$Tinfo,

	"Qcol:s"	=>	\$Qcol,
	"Tcol:s"	=>	\$Tcol,
	"Scol:s"	=>	\$Scol,

	"ShowLN"	=>	\$ShowLN,

	"ShowC"		=>	\$ShowCoor,
	"Win:i"		=>	\$Win,


	"XtR"		=>	\$XtR,
	"YtR"		=>	\$YtR,

	"Qgff:s"	=>	\$Qgff,
	"Tgff:s"	=>	\$Tgff,

	"GeneW:f"	=>	\$GeneW,
	"GeneStr"	=>	\$GeneStr,
);
$width ||= 800;
$high ||= 600;
$edge ||= 200;

#m6
$Qcol ||= "0,2,3";
my @Qc = split /\,/,$Qcol;
$Tcol ||= "5,7,8";
my @Tc = split /\,/,$Tcol;
$Scol ||= 4;

#
#
#mummer	
#-Qcol "9,0,1" -Tcol "10,2,3" -Scol 8 \
#
#blast, m6
#-Qcol "0,8,9" -Tcol "1,11,12" -Scol 16 \
#
#minimap2
#


@ARGV || die "Usage:perl $0 <svg>\n";

my $svg = shift;
my $map = shift;

figure($svg,$width+$edge,$high+$edge);
my ($x,$y,$w,$h) = ($edge,$edge,0.9*$width,0.9*$high);
my $lw = 0.01*$edge;
my $lw2 = 0.5*$lw;
my $lw3 = 0.1*$lw;

my (%QX,%QY);
my ($x1,$y1) = ($x,$y);
chomp(my $Qsize = `cat $Qinfo | grep -v \^\$ | grep -v \^# | awk '{s+=\$2}END{print s}'`);
my $hr = $h/$Qsize;

if($ShowCoor && $Win){
	my $n = int($Qsize / $Win);
	my $Lh = $Win*$hr;
	my ($lx,$ly) = ($x1,$y1);
	foreach my $i(0..$n){
		my $v = $i*$Win;
		ShQ("xk:$lw");line($lx,$ly,$lx-3*$lw,$ly);
		ShQ("zt:Arial;zh:12;md:end");text($v,$lx-10*$lw,$ly-2*$lw);
		$ly += $Lh;
	}
}


open IN,$Qinfo;
while(<IN>){
        chomp;
        my @l = split;
        my ($chr,$len) = @l[0,1];
	$QX{$chr} = $x1;
	$QY{$chr} = $y1;
	ShQ("xk:$lw2");line($x1,$y1,$x1+$w,$y1);
	my ($midx,$midy) = ($x1-10*$lw,$y1+0.5*$len*$hr);
	if($YtR){
		rotate(90,$midx,$midy); gp;
		ShQ("zt:Arial;zh:12;md:middle");text($chr,$midx,$midy);
		gpend;
	}else{
		ShQ("zt:Arial;zh:12;md:end");text($chr,$midx,$midy);
	}
	$y1 += $hr*$len;
}
close IN;
ShQ("xk:$lw");line($x1,$y1,$x1+$w,$y1);



my (%TX,%TY);
($x1,$y1) = ($x,$y);
chomp(my $Tsize = `cat $Tinfo | grep -v \^\$ | grep -v \^# | awk '{s+=\$2}END{print s}'`);
my $wr = $w/$Tsize;

if($ShowCoor && $Win){
        my $n = int($Tsize / $Win);
        my $Lw = $Win*$wr;
        my ($lx,$ly) = ($x1,$y1);
        foreach my $i(0..$n){
                my $v = $i*$Win;
                ShQ("xk:$lw");line($lx,$ly,$lx,$ly-3*$lw);
                ShQ("zt:Arial;zh:12;md:middle");text($v,$lx,$ly-15*$lw);
                $lx += $Lw;
        }
}


open IN,$Tinfo;
while(<IN>){
        chomp;
        my @l = split;
        my ($chr,$len) = @l[0,1];
        $TX{$chr} = $x1;
        $TY{$chr} = $y1;
	ShQ("xk:$lw2");line($x1,$y1,$x1,$y1+$h);
	my ($midx,$midy) = ($x1+0.5*$wr*$len,$y1-10*$lw);
	if($XtR){
		rotate(90,$midx,$midy);	gp;
		ShQ("zt:Arial;zh:12;md:end");text($chr,$midx,$midy);
		gpend;
	}else{
		ShQ("zt:Arial;zh:12;md:middle");text($chr,$midx,$midy);	
	}
        $x1 += $wr*$len;
}
close IN;
ShQ("xk:$lw");line($x1,$y1,$x1,$y1+$h);

##minimap2
my $line_n = 1;
open IN,$map;
while(<IN>){
	chomp;
	my @l = split /\t/;
	my ($Qchr,$Qs,$Qe) = ($l[$Qc[0]],$l[$Qc[1]],$l[$Qc[2]]);
	my ($Tchr,$Ts,$Te) = ($l[$Tc[0]],$l[$Tc[1]],$l[$Tc[2]]);

	my $strand = $l[$Scol];
	my $color = ($strand =~ /\+/ || $strand =~ /plus/ || $strand=~/^1$/) ? "red" : "blue";

	($Ts,$Te) = $Ts<$Te ? ($Ts,$Te) : ($Te,$Ts);
	
	#print "$Tchr\t$Ts\t$Te\t$strand\n";


	$TX{$Tchr} || next;
	$QY{$Qchr} || next;

	my $Lx1 = $TX{$Tchr} + $Ts*$wr;
	my $Ly1 = $QY{$Qchr} + $Qs*$hr;
	my $Lx2 = $TX{$Tchr} + $Te*$wr;
	my $Ly2 = $QY{$Qchr} + $Qe*$hr;
	ShQ("xk:$lw;xs:$color");line($Lx1,$Ly1,$Lx2,$Ly2);
	if($ShowLN){
		ShQ("zt:Arial;zh:12;md:middle");text($line_n,$Lx2,$Ly2);
	}
	$line_n++;
}
close IN;

if($Tgff){
	($x1,$y1) = ($x,$y+$h+10*$lw);
	my $gh = 5*$lw;
	my $xk = $GeneW * $lw;
	open IN,$Tgff;
	while(<IN>){
		my @l = split /\t/;
		my ($Tchr,$Ts,$Te,$strand) = @l[0,3,4,6];
		my $color = ($strand =~ /\+/ || $strand =~ /plus/ || $strand=~/^1$/) ? "red" : "blue";
		
		my $Lx1 = $TX{$Tchr} + $Ts*$wr;
		my $Ly1 = $y1;
		my $Lx2 = $TX{$Tchr} + $Te*$wr;
		my $Ly2 = $y1;

                if($GeneStr){
			my ($xn,$yn,$xn1,$yn1) = (12,15,6,4);
			ShQ("xk:$lw;xs:black;");line($Lx1-$xn*$lw,$Ly1+$yn*$lw,$Lx2+$xn*$lw,$Ly2+$yn*$lw);
                        if($color =~ /red/){
				my ($gx,$gy) = ([$Lx2+$xn*$lw-$xn1*$lw,$Lx2+$xn*$lw,$Lx2+$xn*$lw-$xn1*$lw],
						[$Ly2+$yn*$lw+$yn1*$lw,$Ly2+$yn*$lw,$Ly2+$yn*$lw-$yn1*$lw]);
				ShQ("xk:$lw;xs:black");polyline($gx,$gy);
                        }else{
				my ($gx,$gy) = ([$Lx1-$xn*$lw+$xn1*$lw,$Lx1-$xn*$lw,$Lx1-$xn*$lw+$xn1*$lw],
						[$Ly1+$yn*$lw+$yn1*$lw,$Ly1+$yn*$lw,$Ly1+$yn*$lw-$yn1*$lw]);
				ShQ("xk:$lw;xs:black");polyline($gx,$gy);
				
			}
                        $color = "black";
                }


		if($l[2] =~ /mRNA/){
			ShQ("xk:$lw;xs:$color;");line($Lx1,$Ly1,$Lx2,$Ly2);
		}elsif($l[2] =~ /CDS/){
			my ($gx,$gy) = ([$Lx1,$Lx1,$Lx2,$Lx2],[$Ly1+$gh,$Ly1-$gh,$Ly1-$gh,$Ly1+$gh]);
			ShQ("xk:$xk;tc:$color;xs:$color");polygon($gx,$gy);
		}

	}
	close IN;	
}





figend;


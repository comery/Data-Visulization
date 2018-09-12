#!/usr/bin/perl -w
use strict;
use Cwd qw(abs_path);
use FindBin qw($Bin);
use Bio::SeqIO;
use Bio::SeqFeatureI;
use Getopt::Long;
use Statistics::Descriptive;

=head1 Description
	This script is an utility for chloroplast/mitochondria 
	annotation pipoline to draw circos pictures 

=head1 Author :
	YangChentao yangchentao@genomics.cn 2017/05

=head1 options
	*--gb 	<str>	*.mitogenome.gb
	*--conf	<str>	*.conf
	--help		display this help information

=head1 Usage
	perl draw_circos_for_mitogenome.pl  -gb <*.mitogenome.gb> -conf <*.conf> 

=head1 attention
	~ If you want to draw depth part, well you need prepare a depth file format
	like is :
	#	ID	start	end	depth
		mt1	1	1	3
		mt1	2	2	4
		mt1	3	3	4
	meanwhile you should set "depth_file" value.

=cut

my (%conf,$help,$gbfile,$configure,$warn,$outdir);

GetOptions(
			'help' => \$help,
			'gb=s' => \$gbfile,
			'conf=s' => \$configure
	);

die `pod2text $0` if ($help || !$gbfile );

$warn = <<_WARN_;
#------------------------------------------------------------------------------------------------------
WARNNING:
         No configure file!
         So using $Bin/mitogenome.auto_depth.conf
#------------------------------------------------------------------------------------------------------
_WARN_

if (! $configure) {
	print STDERR "$warn";
	$configure = "$Bin/mitogenome.auto_depth.conf";
}

# reading configures from $configure
open CC, "$configure";	# circos_path,win,cds,rRNA,tRNA,locus_color,label_color,gc_fill,depth_fill
while (<CC>){
	next if (/^#/);
	next if (/^\s*$/);
	s/\s//g;
	chomp;
	my @cc = split /=/,$_;
	$conf{$cc[0]} = $cc[1];

}

close CC;
$outdir = $conf{'outdir'};
$outdir = abs_path($outdir);

## check configure
die "circos path is bad !" unless ( -e $conf{'circos_path'} ) ;
$conf{'win'} = 50 if (! $conf{'win'});
$conf{'gc'} = 'yes' if (! $conf{'gc'});
$conf{'depth'} = 'yes' if (! $conf{'depth'});
$conf{'base'} = 'no' if (! $conf{'base'});
my $depth_file = abs_path($conf{'depth_file'});

die "Depth file is necessary in configures when you set \"depth = yes\"" if ($conf{'depth'} eq 'yes' && !$depth_file) ;

if (! -d $outdir) {
	`mkdir $outdir`;
	print STDERR "mkdir : $outdir\n";
}
print STDERR "Configures are OK !\n";

### read genebank file 
# whether link chromsome as a whole according to topology[linear|circular] of mitogenome.
my (%breaks,%topology);
my $locus_line = `grep "LOCUS" $gbfile `;
chomp $locus_line;
my @lines = split /\n/,$locus_line;
foreach my $l(@lines) {
	my $break;
	my $a = (split/\s+/,$l)[1];
	my $topo = (split/\s+/,$l)[5];
	$topology{$a} = $topo;
	if ($topo eq 'circular') {
		$break = 0;
		print STDERR "Sequence is circular, it will link as a complete circle.\n";
	}else {
		$break = "0.5r";
		print STDERR "Sequence is linear, it will not link as a complete circle,\n";
	}
	$breaks{$a} = $break;
}

# get cds rRNA tRNA's location and strand information
my $in = Bio::SeqIO-> new(-file => "$gbfile", "-format" => 'genbank');
while (my $seq_obj=$in->next_seq()) {
	
	my $source = $seq_obj->seq;
	my $sou_len = $seq_obj->length;
	my $locus = $seq_obj -> display_name;
	print STDERR "locus name is $locus\n";
	
	open KAR,">$outdir/$locus.karyotype.txt";
	print KAR "chr1 - mt1\t$locus-$topology{$locus}\t0\t$sou_len\tgrey";
	close KAR;

	if ($conf{'base'} eq 'yes') {
		open BASE,">$outdir/$locus.base.txt";
		my @base = split//,$source;
		# output base 
		foreach my $i(0..$#base) {
			my $j = $i +1;
			print BASE "mt1\t$j\t$j\t$base[$i]\n";
		}

	}
	close BASE;
	
	#calculate GC content
	if ($conf{'gc'} eq 'yes') {
		open GC,">$outdir/$locus.fa.gc.txt";
		my $win = $conf{'win'};
		for (my $i = 0; $i < $sou_len - $win -1; $i+=$win) {
			my $tmp = substr($source,$i,$win);
			my $gc_num = $tmp =~ tr/GCgc/GCgc/;
			my $GC = $gc_num/$win;
			my $start = $i +1 ;
			my $end = $i + $win ;
			print GC "mt1\t$start\t$end\t$GC\n";
		}	

	}
	close GC;

	
	open ORI,">$outdir/$locus.strand.text.txt"; # strand label
	print ORI "mt1\t0\t10\t+\tr0=1r-250p,r1=1r-150p\n";
	#print ORI "mt1\t0\t300\t-\tr0=1r+100p,r1=1r+200p";
	close ORI;

	open FEA,">$outdir/$locus.features.txt"; # location information
	
	open TEXT,">$outdir/$locus.gene.text.txt"; # gene name text

	for my $feature ($seq_obj->top_SeqFeatures){
		my ($db_xref,$val,$location);

		if ($feature->primary_tag eq 'CDS' )  {
			my $seq = $feature->spliced_seq->seq;
			my $start = $feature -> start;
			my $end = $feature -> end;
			my $strand = $feature -> strand;
			my $direction;
			if ($strand == 1) {
				$direction = '+';
				print FEA "mt1\t$start\t$start\tfill_color=black,r0=0.955r,r1=1r\n";
				print FEA "mt1\t$end\t$end\tfill_color=black,r0=0.955r,r1=1r\n";
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'cds'},r0=0.955r,r1=1r\n";
			}elsif ($strand == -1){
				$direction = '-';
				print FEA "mt1\t$start\t$start\tfill_color=black,r0=1r,r1=1.045r\n";
				print FEA "mt1\t$end\t$end\tfill_color=black,r0=1r,r1=1.045r\n";
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'cds'},r0=1r,r1=1.045r\n";
			}else {
				$direction = '?';
				print FEA "mt1\t$start\t$start\tfill_color=black,r0=0.98r,r1=1.020r\n";
				print FEA "mt1\t$end\t$end\tfill_color=black,r0=0.98r,r1=1.020r\n";
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'cds'},r0=0.98r,r1=1.020r\n";
			}
			#print CDS "mt1\t$start\t$end\n";

			if ($feature->has_tag('gene')) {
				for $val ($feature->get_tag_values('gene')){
				
					print TEXT "mt1\t$start\t$end\t$val\n";
				}
			}else{
			
				print TEXT "mt1\t$start\t$end\tCDS_NA\n";
			}
		}elsif ($feature->primary_tag eq 'rRNA' )  {
		
			my $start = $feature -> start;
			my $end = $feature -> end;
		#	print RRNA "mt1\t$start\t$end\n";

			my $strand = $feature -> strand;
			my $direction;
			if ($strand == 1) {
				$direction = '+';
				print FEA "mt1\t$start\t$start\tfill_color=black,r0=0.955r,r1=1r\n";
				print FEA "mt1\t$end\t$end\tfill_color=black,r0=0.955r,r1=1r\n";
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'rRNA'},r0=0.955r,r1=1r\n";
			}elsif ($strand == -1){
				$direction = '-';
				print FEA "mt1\t$start\t$start\tfill_color=black,r0=1r,r1=1.045r\n";
				print FEA "mt1\t$end\t$end\tfill_color=black,r0=1r,r1=1.045r\n";
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'rRNA'},r0=1r,r1=1.045r\n";
			}else {
				$direction = '?';
				print FEA "mt1\t$start\t$start\tfill_color=black,r0=0.98r,r1=1.020r\n";
				print FEA "mt1\t$end\t$end\tfill_color=black,r0=0.98r,r1=1.020r\n";
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'rRNA'},r0=0.98r,r1=1.020r\n";
			}
			if ($feature->has_tag('gene')) {
				for $val ($feature->get_tag_values('gene')){
					print TEXT "mt1\t$start\t$end\t$val\n";
				}
			}else{
			
				print TEXT "mt1\t$start\t$end\trRNA_NA\n";
			}

		}elsif ($feature->primary_tag eq 'tRNA' )  {
		 
		 	my $start = $feature -> start;
			my $end = $feature -> end;
		#	print TRNA "mt1\t$start\t$end\n";

			my $strand = $feature -> strand;
			my $direction;
			if ($strand == 1) {
				$direction = '+';
				print FEA "mt1\t$start\t$start\tfill_color=black,r0=0.955r,r1=1r\n";
				print FEA "mt1\t$end\t$end\tfill_color=black,r0=0.955r,r1=1r\n";
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'tRNA'},r0=0.955r,r1=1r\n";
			}elsif ($strand == -1){
				$direction = '-';
				print FEA "mt1\t$start\t$start\tfill_color=black,r0=1r,r1=1.045r\n";
				print FEA "mt1\t$end\t$end\tfill_color=black,r0=1r,r1=1.045r\n";
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'tRNA'},r0=1r,r1=1.045r\n";
			}else {
				$direction = '?';
				print FEA "mt1\t$start\t$start\tfill_color=black,r0=0.98r,r1=1.020r\n";
				print FEA "mt1\t$end\t$end\tfill_color=black,r0=0.98r,r1=1.020r\n";
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'tRNA'},r0=0.98r,r1=1.020r\n";
			}
			if ($feature->has_tag('product')) {
				for $val ($feature->get_tag_values('product')){
				
					print TEXT "mt1\t$start\t$end\t$val\n";
				}
			}else{
				
					print TEXT "mt1\t$start\t$end\ttRNA_NA\n";
			}
		}
	}
	

close FEA;
close TEXT;

print STDERR "$locus Reading genebank file done. \n";
print STDERR "$locus Creating circos.conf.\n...\n";
# creat a circos.conf file
open CON,">$outdir/$locus.circos.conf";
print  CON <<_CONFIG_;

<<include etc/colors_fonts_patterns.conf>>

#-----------------image------------------
<image>
###<<include etc/image.conf>>
dir   = $conf{'outdir'}
file  = $locus.png
png   = $conf{'png'}
svg   = $conf{'svg'}

# radius of inscribed circle in image
radius         = 1500p

# by default angle=0 is at 3 o'clock position
angle_offset      = -90

#angle_orientation = counterclockwise
auto_alpha_colors = yes
auto_alpha_steps  = 5
background = $conf{'background'}
</image>

#-----------------ideogram------------------
<ideogram>

<spacing>
default = 0.01r
break   = $breaks{$locus}
</spacing>

###<<include ideogram.position.conf>>
radius           = 0.80r
thickness        = 20p
fill             = yes
fill_color       = grey
stroke_thickness = 3
stroke_color     = black

###<<include ideogram.label.conf>>
show_label       = yes
label_font       = bolditalic
label_radius     = dims(image,radius) - 1r
label_center   = yes
label_color    = grey
#label_radius     = 0.00001r
label_size       = 48
label_parallel   = yes
label_case       = upper
#label_format     = eval(sprintf("chr%s",var(label)))
#label_format     = eval(var(labe))


###<<include bands.conf>>
show_bands            = yes
fill_bands            = yes
band_stroke_thickness = 2
band_stroke_color     = white
band_transparency     = 0

</ideogram>
#-----------------ticks------------------
show_ticks          = yes
show_tick_labels    = yes

<ticks>

radius           = dims(ideogram,radius_outer)
#radius           = 1r+0.06r
orientation      = out
label_multiplier = 1e-3
color            = black
thickness        = 2p
font             = blod

<tick>
spacing        = 1u
show_label     = yes
label_size     = 25p
size           = 25p
format         = %d
label_offset   = 2p
#suffix         = " kb"
</tick>

<tick>
spacing        = 5u
show_label     = yes
label_size     = 30p
size           = 30p
format         = %d
suffix         = " kb"
label_offset   = 2p
</tick>

<tick>
spacing        = 10u
show_label     = yes
label_size     = 30p
size           = 30p
format         = %d
label_offset   = 2p
suffix         = " kb"
</tick>

</ticks>
#-----------------karyotype------------------

karyotype   = $locus.karyotype.txt

chromosomes_units = 1000
chromosomes       = mt1
chromosomes_display_default = no

#-----------------plots------------------

<plots>
############ gene name text
<plot>

type       = text
color      = $conf{'label_color'}
label_font = default
label_size = 28p
file = $locus.gene.text.txt
r1   = 1r+250p
r0   = 1r+10p
show_links     = yes
link_dims      = 0p,20p,70p,3p,10p
link_thickness = 2p
link_color     = black

label_snuggle         = yes
max_snuggle_distance  = 1r
snuggle_tolerance     = 0.25r
snuggle_sampling      = 2

</plot>

<plot>

type       = text
color      = $conf{'label_color'}
label_font = bold
label_size = 40p
file = $locus.strand.text.txt
show_links     = no

</plot>


_CONFIG_

if ($conf{'gc'} eq 'yes') {
	print CON <<_CONFIG_;
###############GC content
<plot>
type      = histogram
file      = $outdir/$locus.fa.gc.txt

r1        = 0.615r
r0        = 0.45r
max       = 1
min       = 0

stroke_type = line
thickness   = 2
color       = $conf{'gc_fill'}
extend_bin  = no
fill_color = $conf{'gc_fill'}
<backgrounds>
#<background>
#y1    = -0.1
#color = lred
#</background>
#<background>
#y0    = 0
#color = lgreen
#</background>
</backgrounds>

<axes>

<axis>
spacing   = 0.2r
color     = lgrey
thickness = 1
</axis>

<axis>
position = 0.5r
color = dred
thickness = 2
</axis> 
 
</axes>

<rules>
use = yes
<rule>
condition  = var(value) >0.50
fill_color = lgreen
</rule>

#<rule>
#condition  = var(value) < 0.25
#fill_color = lgreen
#</rule>
</rules>

</plot>

_CONFIG_

}

if ($conf{'base'} eq 'yes') {
	print CON <<_CONFIG_;

########## sequence base
<plot>
type       = text
label_font = mono
file       = $outdir/$locus.base.txt
r1         = 0.91r
r0         = 0.88r
label_size = 20
padding    = -0.25r
#label_rotate = no

<rules>
<rule>
condition = var(value) eq "A"
color     = red
</rule>
<rule>
condition = var(value) eq "T"
color     = blue
</rule>
<rule>
condition = var(value) eq "C"
color     = green
</rule>
</rules>
</plot>

_CONFIG_
}

if ($conf{'depth'} eq 'yes' && $depth_file) {

	# caculate upper quartile value
	my $str = `grep -v "^#" $depth_file|awk '{print \$4}'`;
	chomp $str;
	my @tmp = split /\n/,$str;
	my $stat = Statistics::Descriptive::Full->new();
	$stat->add_data(@tmp);	
	my $low_quartile = $stat->quantile(2);
	my $upper_quartile = $stat->quantile(3);
	my $max_depth = $stat->quantile(4);

	print CON <<_CONFIG_;

########### depth information
<plot>
type      = line
thickness = 2
max_gap = 1u
file    = $depth_file
color   = dgreen
min     = 0
max     = $max_depth
r0      = 0.618r
r1      = 0.768r
fill_color = $conf{'depth_fill'}


<axes>
<axis>
color     = lgrey_a2
thickness = 1
spacing   = 0.06r
</axis>
</axes>

<rules>

<rule>
condition    = var(value) > $upper_quartile
color        = dgreen
fill_color   = dgreen_a1
</rule>

<rule>
condition    = var(value) < 20 
##$low_quartile
color        = dred
fill_color   = dred_a1
</rule>

</rules>

</plot>

_CONFIG_
}

print CON "</plots>\n";

print CON <<_CONFIG_;

#-----------------highlights------------------
<highlights>

# CDS & rRNA & tRNA
<highlight>
file         = $outdir/$locus.features.txt
</highlight>

</highlights>

<<include etc/housekeeping.conf>>

_CONFIG_

close CON;

print STDERR "$locus Drawing circos.\n...\n";
`$conf{'circos_path'} -conf $outdir/$locus.circos.conf`;

}
print STDERR "All done !";

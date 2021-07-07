#!/usr/bin/perl -w
use strict;
use Cwd qw(abs_path);
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
	Configures example: /hwfssz1/ST_DIVERSITY/USER/yangchentao/perlscript/deal_genebank/draw_circos/draw_multi-circos_in_oneimage_byclass.conf

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
         So using /hwfssz1/ST_DIVERSITY/USER/yangchentao/perlscript/deal_genebank/draw_circos/draw_multi-circos_in_oneimage_byclass.conf
#------------------------------------------------------------------------------------------------------
_WARN_

if (! $configure) {
	print STDERR "$warn";
	$configure = "/hwfssz1/ST_DIVERSITY/USER/yangchentao/software/perlscript/deal_genebank/draw_circos/draw_multi-circos_in_oneimage_byclass.conf";
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


`[ -d $outdir ] || mkdir $outdir`;
print "Configures are OK !\n";
print "outdir : $outdir...\n";
### read genebank file 
# whether link chromsome as a whole according to topology[linear|circular] of mitogenome.
my (%groups,%breaks,%topology,%lens);
my $locus_line = `grep 'LOCUS' $gbfile `;
chomp $locus_line;
my @lines = split /\n/,$locus_line;
foreach my $l(@lines) {
	my $break;
#	print "$l";
	my $a = (split/\s+/,$l)[1];
	my $topo = (split/\s+/,$l)[5];
	$topology{$a} = $topo;
	if ($topo eq 'circular') {
		$break = 0;
		print "Sequence is circular, it will link as a complete circle.\n";
	}else {
		$break = "0.5r";
		print "Sequence is linear, it will not link as a complete circle,\n";
	}
	$breaks{$a} = $break;
}
# get cds rRNA tRNA's location and strand information
my $in = Bio::SeqIO-> new(-file => "$gbfile", "-format" => 'genbank');
while (my $seq_obj=$in->next_seq()) {
	
	my $source = $seq_obj->seq;
	my $sou_len = $seq_obj->length;
	my $locus = $seq_obj -> display_id;

	# class name is prefix of $locus, making hash of groups
	my $class = (split /_/,$locus)[0];
	`mkdir -p $outdir/$class` unless ( -d "$outdir/$class");

#	record the class groups information
	$groups{$class}{$locus} = $sou_len;

	$lens{$locus} = $sou_len;
	
	open KAR,">$outdir/$class/$locus.karyotype.txt";
#	print KAR "chr1 - mt1\t$locus-$topology{$locus}\t0\t$sou_len\tgrey";
	print KAR "chr1 - mt1\t$class\_GC\t0\t$sou_len\tgrey";
	close KAR;

	open IDO,">$outdir/$class/$locus.ideo.txt";
	print IDO "mt1\t0\t$sou_len\t1";
	close IDO;

	if ($conf{'base'} eq 'yes') {
		open BASE,">$outdir/$class/$locus.base.txt";
		my @base = split//,$source;
		# output base 
		foreach my $i(0..$#base) {
			my $j = $i +1;
			print BASE "mt1\t$j\t$j\t$base[$i]\n";
		}

	}
	close BASE;
	
	#calculate GC content
#	if ($conf{'gc'} eq 'yes') {
		open GC,">$outdir/$class/$locus.fa.gc.txt";
		my $win = $conf{'win'};
		for (my $i = 0; $i < $sou_len - $win -1; $i+=$win) {
			my $tmp = substr($source,$i,$win);
			my $gc_num = $tmp =~ tr/GCgc/GCgc/;
			my $GC = $gc_num/$win;
			my $start = $i +1 ;
			my $end = $i + $win ;
			print GC "mt1\t$start\t$end\t$GC\n";
		}	

#	}
	close GC;

	
	open FEA,">$outdir/$class/$locus.features.txt"; # location information
	
	open TEXT,">$outdir/$class/$locus.gene.text.txt"; # gene name text

	for my $feature ($seq_obj->top_SeqFeatures){
		my ($db_xref,$val,$location);

		if ($feature->primary_tag eq 'CDS' )  {
		#	my $seq = $feature->spliced_seq->seq;
			my $start = $feature -> start;
			my $end = $feature -> end;
			my $strand = $feature -> strand;
			my $direction;
			if ($strand == 1) {
				$direction = '+';
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'cds'}\n";
			}elsif ($strand == -1){
				$direction = '-';
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'cds'}\n";
			}else {
				$direction = '?';
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'cds'}\n";
			}
			#print CDS "mt1\t$start\t$end\n";

			if ($feature->has_tag('gene')) {
				for $val ($feature->get_tag_values('gene')){
				
					print TEXT "mt1\t$start\t$end\t$val\n";
				}
			}elsif ($feature->has_tag('product')){
				for $val ($feature->get_tag_values('product')){
				
					print TEXT "mt1\t$start\t$end\t$val\n";
				}
			}else {
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
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'rRNA'}\n";
			}elsif ($strand == -1){
				$direction = '-';
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'rRNA'}\n";
			}else {
				$direction = '?';
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'rRNA'}\n"
			}
			if ($feature->has_tag('gene')) {
				for $val ($feature->get_tag_values('gene')){
					print TEXT "mt1\t$start\t$end\t$val\n";
				}
			}elsif($feature->has_tag('product')){
				for $val ($feature->get_tag_values('product')){
					$val =~ s/\s/_/g;
					print TEXT "mt1\t$start\t$end\t$val\n";
				}
				
			}else {
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
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'tRNA'}\n";
			}elsif ($strand == -1){
				$direction = '-';
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'tRNA'}\n";
			}else {
				$direction = '?';
				print FEA "mt1\t$start\t$end\tfill_color=$conf{'tRNA'}\n"
			}
			if ($feature->has_tag('product')) {
				for $val ($feature->get_tag_values('product')){
				
					print TEXT "mt1\t$start\t$end\t$val\n";
				}
			#}elsif($feature->has_tag('product')){
			#	for $val ($feature->get_tag_values('product')){
			#		print TEXT "mt1\t$start\t$end\t$val\n";
			#	}
			}else{
				
					print TEXT "mt1\t$start\t$end\ttRNA_NA\n";
			}
		}
	}
	

close FEA;
close TEXT;

}


print "Reading genebank file done. \n";
print "--------------------\n";


#----------define the circls range---------------------------------------------------------------
#my $min_radious = 0.25;
my $min_radious ; # calculate by f(x): sub min_rad;
my $max_radious = 0.975;

#---------Traverse each element of an array， key1 is 'class', key2 is locus, 
#---------and value is length of mitogenome which name is locus

foreach my $class(keys %groups) {
	my $hash = $groups{$class};
	my @sort_lens = sort {$$hash{$a} <=> $$hash{$b}} keys %$hash;
	my $numer_spes = @sort_lens;

#	print "$numer_spes\n";
#	print "@sort_lens\n";
	print "Creating circos.conf for [$class].\n...\n";

	open HIS, ">$outdir/$class/ideogram.histogram.conf";
	print HIS "<plots>\n";
	print HIS "#-----------------plots------------------\n";

	open HILI,">$outdir/$class/features.highlight.conf";
	print HILI "<highlights>\n";
		
	my $i = 1;
	foreach my $spes(@sort_lens) {
	#	print "$spes=>$$hash{$spes}\n";

		$min_radious = &min_rad($numer_spes) ;
	#	print "$min_radious\n";
		my ($aa,$bb,$unit,$r1,$r0,$gc_r1);
		if ($numer_spes == 1) {
			$aa = 0;
			$bb = 0;
			$unit = 0;
			$r0 = 0.85;
			$r1 = 0.95;
			$gc_r1 = 0.95;
		}else{
			$aa =  ($max_radious - $min_radious)/(($numer_spes -1) * 2.2);
			$bb = $aa * 1.2;
			$unit = $aa + $bb;
			$r1 = $min_radious + ($i -1) * $unit;
			$r0 = $r1 - $bb;
			$i ++;
			$gc_r1 = $r1 + $bb*0.5;
			
		}
		$r1 = $r1.'r';
		$r0 = $r0.'r';
		$gc_r1 = $gc_r1.'r' ;
	
	# use histogram showing muiti_mitogenome circles

		print HIS <<_HIS_;
#-------------GC--------------------
<plot>
type      = histogram
file      = $outdir/$class/$spes.fa.gc.txt
r1        = $gc_r1
r0        = $r0
max       = 1
min       = 0

stroke_type = line
thickness   = 1
color       = $conf{'gc_fill'}
extend_bin  = yes
fill_color = $conf{'gc_fill'}

<rules>
use = yes
<rule>
condition  = var(value) >$conf{'gc_upper'}
fill_color = red_a1
</rule>
<rule>
condition  = var(value) <$conf{'gc_lower'}
fill_color = yellow
</rule>
</rules>

</plot>

_HIS_

# whether to show highlight genes features:cds rRNA tRNA
		if ($conf{'features'} eq 'yes') {
			print HILI <<_HILI_;

#------gene features-----------------------------
<highlight>
file         = $outdir/$class/$spes.features.txt
r1        = $r1
r0        = $r0
</highlight>
_HILI_
		}
		print HILI <<_HILI_;
#-----------different mitogenomes showed by highlight model-------
<highlight>
file         = $outdir/$class/$spes.ideo.txt
r1        = $r0 
r0        = $r1
fill_color = grey_a5
</highlight>


_HILI_


	}
	

	print HIS <<_HIS_;

############ gene name text
<plot>
type       = text
color      = $conf{'label_color'}
label_font = default
label_size = 30p
file = $sort_lens[-1].gene.text.txt

r1   = 0.95r+300p
r0   = 0.95r+10p

show_links     = yes
link_dims      = 5p,0p,30p,5p,10p
link_thickness = 2p
link_color     = red

</plot>
_HIS_


	print HIS "</plots>";
	print HILI "</highlights>\n";
	close HIS;
	close HILI;

	# creat a circos.conf file
	open CON,">$outdir/$class/circos.conf";
	print  CON <<_CONFIG_;

<<include etc/colors_fonts_patterns.conf>>

#-----------------image------------------
<image>
###<<include etc/image.conf>>
#dir   = $conf{'outdir'}
dir   = ./
file  = $class.png
png   = $conf{'png'}
svg   = $conf{'svg'}

# radius of inscribed circle in image
radius         = 2000p

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
break   = $breaks{$sort_lens[-1]}
</spacing>

###<<include ideogram.position.conf>>
radius           = 0.975r
thickness        = 20p
fill             = yes
fill_color       = grey
stroke_thickness = 3
stroke_color     = black

###<<include ideogram.label.conf>>
show_label       = yes
label_font       = bolditalic
#label_radius     = dims(image,radius)
label_radius     = 0.15r
label_size       = 45
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

karyotype   = $outdir/$class/$sort_lens[-1].karyotype.txt

chromosomes_units = 1000
chromosomes       = mt1
chromosomes_display_default = no


_CONFIG_


	print CON <<_CONFIG_;

#-----------------highlights------------------
<<include $outdir/$class/features.highlight.conf>>
<<include $outdir/$class/ideogram.histogram.conf>>
<<include etc/housekeeping.conf>>

_CONFIG_

	close CON;
	print "Drawing circos for [$class].\n...\n";
	`$conf{'circos_path'} -conf $outdir/$class/circos.conf`;
	print "Drawing [$class] done!\n";
	print "--------------------\n";
}


print "All done !";


sub min_rad {
	my $num = shift;
	my $min;
	if ($num <= 5){
		$min = 0.5;
	}elsif($num <= 10){
		$min = 0.4125;
	}elsif($num <=15){
		$min = 0.325;
	}else{
		$min = 0.25;
	}
	return $min;
}

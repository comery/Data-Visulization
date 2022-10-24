### asm2ref
This is a tiny pipeline to draw circos plot for genome alignment visualization.

#### Prerequisites

- python 3.6+
- python module: palettable
- unimap



#### Usage

```shell
# generate overview dotplot
Usage : run_asm2ref_unimap_links.sh ref.fasta query.fasta outprex

# generate circos plot
bin='/path/where_you_download'
python3 $bin/asm2ref/unimap/split_alignment_by_Chrs.py asm2ref.unimap.paf paf

[ -d circos   ] || mkdir circos
cd splitbyChrs
ls |grep '^chr'|while read a
do
	cd $a
	sort -k6,6 -k8,8n $a.paf > $a.sort.paf
	sed 's/chr[0-9XY]*/hs1/' cent.bed.txt > cent.bed.highlight.txt
	if [ -s $a.sort.paf  ] ; then
		echo "$a looks good!"
		python3 $bin/asm2ref/unimap/preCircosLinkFromPaf.sort.py -paf $a.sort.paf -filter -minL 500000 -minB 2000 -rate 0.2
		circos -silent -conf $bin/asm2ref/unimap/confs/run_asm2ref_unimap_links_cent.conf
		mv circos_aln_link.png $a.circos.png
		mv circos_aln_link.svg $a.circos.svg
	else
		echo '$a.sort.paf is empty!'
	fi
	cd ..
done

```


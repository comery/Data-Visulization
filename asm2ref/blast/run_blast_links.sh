if [[ $# != 3 ]] ; then
	echo "Usage : $0 ref.fasta query.fasta outprex"
	exit 1
fi

ref=$1
qry=$2
outpre=$3
src=$(cd $(dirname $0);pwd)
# blast
makeblastdb -in $ref -dbtype nucl -parse_seqids -out $outpre
blastn -query $qry -out blast.out -db $outpre -outfmt 6 -evalue 1e-5 -num_threads 4 -max_target_seqs 10

# generate link.txt and karyotype.txt
python3 $src/preCircosLinkFromPaf.sort.py -paf $outpre.unimap.paf -filter 
# get conf 
cp $src/confs/run_asm2ref_unimap_links.conf .
# plot cirocs
circos -conf run_asm2ref_unimap_links.conf

if [[ $# != 4 ]]; then
	echo "Usage : $0 ref.fasta query.fasta outprex kmer_size"
	exit 1
fi

ref=$1
qry=$2
outpre=$3
kmer=$4

src=$(cd $(dirname $0);pwd)

# For either mapping long reads or computing whole-genome alignments, 
# Winnowmap requires pre-computing high frequency k-mers (e.g., top 0.02% most frequent) in a reference. 
# Winnowmap uses meryl k-mer counting tool for this purpose.
$src/meryl count k=$kmer output merylDB $ref
$src/meryl print greater-than distinct=0.9998 merylDB > repetitive_k$kmer.txt

# -a for sam output
# asm5, 5% divergency
$src/winnowmap -W repetitive_k$kmer.txt -x asm5 $ref $qry > $outpre.paf

# generate link.txt and karyotype.txt
python3 $src/preCircosLinkFromPaf.sort.py -paf $outpre.winnowmap.paf -filter

# get conf
cp $src/confs/run_asm2ref_unimap_links.conf .

# plot cirocs
circos -conf run_asm2ref_unimap_links.conf
